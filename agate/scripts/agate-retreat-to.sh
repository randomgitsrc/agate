#!/usr/bin/env bash
# agate-retreat-to.sh — 自动化多步单向回退（每一步仍是独立、真实、受 gate 校验的 commit）
# 用法：agate-retreat-to.sh TASK_DIR TARGET_PHASE "诊断原因"
set -euo pipefail

TASK_DIR="${1:?用法: agate-retreat-to.sh TASK_DIR TARGET_PHASE REASON}"
TARGET_PHASE="${2:?用法: agate-retreat-to.sh TASK_DIR TARGET_PHASE REASON}"
REASON="${3:?必须提供诊断原因（用于每一步回退的 commit message）}"
STATE_FILE="$TASK_DIR/.state.yaml"
# MAX_RETRY_MAP 从 check-state-transition.sh 提取（单一数据源，避免漂移）；
# 环境变量覆盖仍有效（check-state-transition.sh 也读 MAX_RETRY_MAP 环境变量）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "${MAX_RETRY_MAP:-}" ]; then
    MAX_RETRY_MAP=$(grep -oE 'MAX_RETRY_MAP="\$\{MAX_RETRY_MAP:-[^"]*\}"' "$SCRIPT_DIR/check-state-transition.sh" \
        | grep -oE 'P[0-9]:[0-9](,P[0-9]:[0-9])*' || true)
fi
MAX_RETRY_MAP="${MAX_RETRY_MAP:-P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2}"
ARCHIVE_SCRIPT="$SCRIPT_DIR/agate-archive-stale-outputs.sh"

[ -f "$STATE_FILE" ] || { echo "GATE RETREAT: $STATE_FILE 不存在" >&2; exit 1; }
phase_num() { echo "$1" | grep -oE '[0-9]+' || echo ""; }

CURRENT_PHASE=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-get.py" phase)
cur_num=$(phase_num "$CURRENT_PHASE")
tgt_num=$(phase_num "$TARGET_PHASE")

if [ -z "$cur_num" ] || [ -z "$tgt_num" ]; then
    echo "GATE RETREAT: 当前 phase（$CURRENT_PHASE）或目标 phase（$TARGET_PHASE）不是合法的 P0-P8" >&2
    exit 1
fi
if [ "$tgt_num" -ge "$cur_num" ]; then
    echo "GATE RETREAT: 目标 phase（$TARGET_PHASE）不低于当前 phase（$CURRENT_PHASE），这不是回退" >&2
    exit 1
fi

# 预检查 A：暂存区不能有 TASK_DIR 之外的内容——下面的 commit 会用 pathspec 限定到 TASK_DIR，
# 但如果暂存区本来就有无关文件，容易让人误以为它们也被这次 retreat 处理了（其实只是继续留在暂存区，
# 状态含糊）。提前报错比事后困惑更清楚。
OUTSIDE_STAGED=$(git diff --cached --name-only 2>/dev/null | grep -vE "^${TASK_DIR#./}/" || true)
if [ -n "$OUTSIDE_STAGED" ]; then
    echo "GATE RETREAT: 暂存区含 TASK_DIR 之外的文件，请先处理（commit 或 unstage）再重试：" >&2
    echo "$OUTSIDE_STAGED" | sed 's/^/  /' >&2
    exit 1
fi

# 预检查 B：一次性查完路径上每一阶退回后的 retry 是否超限，避免半退到一半卡在中间
CHECK_RESULT=$(STATE_FILE="$STATE_FILE" CUR="$cur_num" TGT="$tgt_num" python3 "$SCRIPT_DIR/agate-retreat-state.py" check_retreat "$MAX_RETRY_MAP")
if [ -n "$CHECK_RESULT" ]; then
    IFS=':' read -r bad_phase would_be limit <<< "$CHECK_RESULT"
    echo "GATE RETREAT: 路径上 ${bad_phase} 退回后 retry 将达到 ${would_be}（MAX=${limit}），超限——不执行任何一步，直接转 PAUSED 问人类" >&2
    exit 1
fi

# 逐步执行：每一步都是独立的归档 + phase 更新 + retry+1 + 真实 git commit
n="$cur_num"
STEPS=0
while [ "$n" -gt "$tgt_num" ]; do
    next=$((n - 1))
    old_p="P${n}"; new_p="P${next}"
    bash "$ARCHIVE_SCRIPT" "$old_p" "$TASK_DIR"
    STATE_FILE="$STATE_FILE" NEW_PHASE="$new_p" RETREAT_REASON="$REASON" python3 "$SCRIPT_DIR/agate-retreat-state.py" write_retreat
    git add "$TASK_DIR" 2>/dev/null || true
    git commit -qm "retreat: ${old_p} -> ${new_p}（诊断：${REASON}）" -- "$TASK_DIR" 2>&1 || {
        echo "GATE RETREAT: ${old_p} -> ${new_p} 的 commit 未通过 pre-commit hook 校验，已停在 ${old_p}" >&2
        exit 1
    }
    echo "GATE RETREAT: ${old_p} -> ${new_p} 已提交（诊断：${REASON}）"
    n="$next"; STEPS=$((STEPS + 1))
done
echo "GATE RETREAT: 已退到 ${TARGET_PHASE}，共 ${STEPS} 步，均已独立 commit + 归档"
# 回退落地后必须建 DEBT 条目（TAG0001 Phase 2 唯一硬强制，BDD-12）
# 事后兜底由 check-debt.sh --retreat-coverage 只读比对（不阻断）
echo "GATE RETREAT: 回退已完成——请为本次回退建立 source: retreat 的 DEBT 条目（{AGATE_WORKSPACE}/debt/tech-debt.md，模板见 assets/templates/tech-debt-template.md）"
