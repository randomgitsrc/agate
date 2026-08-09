#!/usr/bin/env bash
# check-frontmatter.sh FILE — frontmatter schema 校验（P1/P2/P6/P7，v2.0 T001 流 A）
# 检查 FILE 的 frontmatter 块是否符合 P2-design.md §3.1.3 定义的 schema
# exit 0 = 格式正确（含非目标文件 / 旧格式无 frontmatter）; exit 1 = 格式错误

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FILE="${1:?用法: check-frontmatter.sh FILE}"

[ ! -f "$FILE" ] && exit 0

# 用环境变量传参，避免 shell 变量注入 Python 代码（同 check-state-yaml.sh 惯例）
# 解析错误信息由 agate-frontmatter-check.py 输出到 stdout（ERRORS 捕获）。
# P4-review.md CRITICAL fix B（纵深防御）：不再用 2>/dev/null || true 把 stderr 和非零
# exit code 一起吞掉——那样会把"校验器自己崩了"误判成"没有错误"（exit 0 放行）。
# 区分两种情况：python 正常退出（exit 0）但 stdout 为空 → 真的没错误，exit 0；
# python 非零退出（脚本自己崩了）→ fail-closed，exit 1，并把 stderr 打印出来方便排查。
PY_STDERR_FILE=$(mktemp)
set +e
ERRORS=$(FILE="$FILE" python3 "$SCRIPT_DIR/agate-frontmatter-check.py" 2>"$PY_STDERR_FILE")
PY_EXIT=$?
set -e

if [ "$PY_EXIT" -ne 0 ]; then
    echo "GATE FRONTMATTER: $FILE frontmatter 校验器异常退出（exit $PY_EXIT），fail-closed 拦截：" >&2
    cat "$PY_STDERR_FILE" >&2
    rm -f "$PY_STDERR_FILE"
    exit 1
fi
rm -f "$PY_STDERR_FILE"

if [ -n "$ERRORS" ]; then
    echo "GATE FRONTMATTER: $FILE frontmatter 格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
