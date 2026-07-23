#!/usr/bin/env bash
# agate-archive-stale-outputs.sh — 回退时归档被跨过阶段的自撰产出
# 用法：agate-archive-stale-outputs.sh PHASE_BEING_LEFT TASK_DIR
# 只处理 self-authored gate 阶段（P1/P2/P6/P7），P4/P5 无跨重试持久化产出，不适用

set -euo pipefail
PHASE="${1:?用法: agate-archive-stale-outputs.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: agate-archive-stale-outputs.sh PHASE TASK_DIR}"

_outputs_for() {
    case "$1" in
        P1) echo "P1-requirements.md P1-review.md" ;;
        P2) echo "P2-design.md P2-review.md" ;;
        P6) echo "P6-acceptance.md" ;;
        P7) echo "P7-consistency.md" ;;
        *) echo "" ;;
    esac
}

OUTPUTS=$(_outputs_for "$PHASE")
[ -z "$OUTPUTS" ] && { echo "GATE ARCHIVE: $PHASE 无需归档（非 self-authored 产出阶段）"; exit 0; }

TS=$(date +%Y%m%d-%H%M%S)
ARCHIVE_DIR="$TASK_DIR/.archived/${TS}-${PHASE}"
mkdir -p "$ARCHIVE_DIR"

# 归档前先把关键失败信息摘要写入一份不会被归档的 breadcrumb 文件
# （P6-acceptance.md 一旦挪进 .archived/，"当初具体是哪条 BDD 失败"这个信息
#  如果没有留痕在当前目录，重新派发 implementer 时容易被忽略——代码保留下来了，
#  但"为什么要退回来"这个最关键的上下文却跟着一起被"藏"进了归档目录）
BREADCRUMB="$TASK_DIR/.retreat-history.md"
{
    echo ""
    echo "## ${TS} 归档 ${PHASE}"
    echo ""
    echo "归档位置：\`${ARCHIVE_DIR}\`"
    if [ "$PHASE" = "P6" ] && [ -f "$TASK_DIR/P6-acceptance.md" ]; then
        FAIL_LINES=$(grep -iE '^\s*- FAIL' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || true)
        if [ -n "$FAIL_LINES" ]; then
            echo ""
            echo "失败详情（供重新派发时引用，避免翻 .archived/）："
            echo '```'
            echo "$FAIL_LINES"
            echo '```'
        fi
    fi
} >> "$BREADCRUMB"

MOVED=0
for f in $OUTPUTS; do
    if [ -f "$TASK_DIR/$f" ]; then
        mv "$TASK_DIR/$f" "$ARCHIVE_DIR/"
        MOVED=$((MOVED + 1))
    fi
done
# P6 专属：连带归档证据目录
if [ "$PHASE" = "P6" ] && [ -d "$TASK_DIR/P6-evidence" ]; then
    mv "$TASK_DIR/P6-evidence" "$ARCHIVE_DIR/"
    MOVED=$((MOVED + 1))
fi

echo "GATE ARCHIVE: $PHASE 产出已归档至 ${ARCHIVE_DIR}（${MOVED} 项），失败摘要已写入 ${BREADCRUMB}"
