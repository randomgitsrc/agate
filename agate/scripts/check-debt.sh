#!/usr/bin/env bash
# check-debt.sh — tech-debt.md 条目 schema 校验 + 回退覆盖比对（TAG0001 D3）
# 用法：
#   check-debt.sh FILE                    # FILE 模式：schema 校验（fail-closed）
#   check-debt.sh --retreat-coverage      # 回退覆盖比对（只读 WARNING，恒 exit 0）
# exit 0 = 通过（FILE 模式：schema 合法 / 文件不存在 / 无 yaml 块；覆盖模式：恒 0）
# exit 1 = FILE 模式：schema 非法或校验器异常（fail-closed）
#
# 双命令（P2-design.md §2.3）：
#   - 默认 FILE 模式：复刻 check-frontmatter.sh 的 fail-closed 薄壳（mktemp stderr +
#     python exit≠0 → exit 1 + ERRORS 非空 → exit 1）；文件不存在 → exit 0。
#   - --retreat-coverage 模式：git log 提取 retreat 提交，与 tech-debt.md 中
#     source: retreat 条目的 evidence 引用比对，缺失打 WARNING；恒 exit 0（不阻断）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODE="${1:?用法: check-debt.sh FILE 或 check-debt.sh --retreat-coverage}"

if [ "$MODE" = "--retreat-coverage" ]; then
    REPO_ROOT="${2:-$PWD}"
    # 工作区解析（source 模式只 export 不输出），同 pre-commit-gate.sh L30-32
    if [ -f "$SCRIPT_DIR/agate-workspace-resolve.sh" ]; then
        source "$SCRIPT_DIR/agate-workspace-resolve.sh" "$REPO_ROOT" \
            || { echo "GATE DEBT: 无法加载 agate-workspace-resolve.sh" >&2; exit 0; }
    else
        echo "GATE DEBT WARNING: 缺少 agate-workspace-resolve.sh，无法解析工作区，跳过回退覆盖比对" >&2
        exit 0
    fi
    DEBT_FILE="$AGATE_WORKSPACE/debt/tech-debt.md"

    # 提取 retreat 提交（只读比对，零新增埋点；--grep='^retreat:' 同 agate-retreat-to.sh 提交格式）
    RETREATS=$(git log --all --format='%H%x09%s' --grep='^retreat:' 2>/dev/null || true)
    if [ -z "$RETREATS" ]; then
        exit 0
    fi

    # 已覆盖哈希集合：tech-debt.md 中 source: retreat 条目 evidence 里的 hex token（7-40 位）
    COVERED=$(python3 "$SCRIPT_DIR/agate-debt-check.py" --covered-hashes "$DEBT_FILE" 2>/dev/null || true)

    while IFS=$'\t' read -r full subject; do
        [ -n "$full" ] || continue
        short="${full:0:7}"
        if ! printf '%s\n' "$COVERED" | grep -qxF "$short" && ! printf '%s\n' "$COVERED" | grep -qxF "$full"; then
            echo "GATE DEBT WARNING: retreat 提交 ${short}（${subject}）未登记为 source: retreat DEBT 条目（evidence 须引用该提交，文件 ${DEBT_FILE}）" >&2
        fi
    done <<< "$RETREATS"
    exit 0
fi

FILE="$MODE"

[ ! -f "$FILE" ] && exit 0

# fail-closed 薄壳（同 check-frontmatter.sh）：python 非零退出（自身崩溃）→ exit 1；
# python 正常退出但 stdout 有错误行 → exit 1；两条件均不满足 → 真无错误，exit 0。
PY_STDERR_FILE=$(mktemp)
set +e
ERRORS=$(FILE="$FILE" python3 "$SCRIPT_DIR/agate-debt-check.py" 2>"$PY_STDERR_FILE")
PY_EXIT=$?
set -e

if [ "$PY_EXIT" -ne 0 ]; then
    echo "GATE DEBT: $FILE tech-debt 校验器异常退出（exit $PY_EXIT），fail-closed 拦截：" >&2
    cat "$PY_STDERR_FILE" >&2
    rm -f "$PY_STDERR_FILE"
    exit 1
fi
rm -f "$PY_STDERR_FILE"

if [ -n "$ERRORS" ]; then
    echo "GATE DEBT: $FILE tech-debt 条目格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
