#!/usr/bin/env bash
# agate-render-dispatch-prompt.sh — 渲染 dispatch-prompt 模板为具体派发实例
# 用法：
#   agate-render-dispatch-prompt.sh PHASE ROLE TASK_DIR [--rollback]
#
# PHASE: P1-P8
# ROLE: subagent 角色名（如 analyst, architect, implementer 等）
# TASK_DIR: 任务目录路径（含 P0-brief.md 等）
# --rollback: 可选，P4 回退派发时使用（选"P4 回退派发追加"而非"P4 派发追加"）
#
# 输出：
#   1. 渲染后的完整文本写入 TASK_DIR/P{N}-dispatch-prompt-{role}.md（持久化存档）
#   2. 同时打印到 stdout（主 Agent 复制作为 Task 工具调用的 prompt）
#
# 注意：本脚本生成的 P{N}-dispatch-prompt-{role}.md 是渲染产物，不是协议模板。
# 修改渲染产物不会影响 agate/assets/templates/dispatch-prompt.md 模板。

set -euo pipefail

SCRIPT_REAL="$(readlink -f "${BASH_SOURCE[0]:-$0}" 2>/dev/null || echo "${BASH_SOURCE[0]:-$0}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_REAL")" 2>/dev/null && pwd || true)"
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$SCRIPT_DIR")}"

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
    echo "用法: agate-render-dispatch-prompt.sh PHASE ROLE TASK_DIR [--rollback]" >&2
    exit 1
fi

PHASE="$1"
ROLE="$2"
TASK_DIR="$3"
ROLLBACK="${4:-}"

case "$PHASE" in
    P1|P2|P3|P4|P5|P6|P7|P8) ;;
    *)
        echo "agate-render-dispatch-prompt.sh: phase '$PHASE' 不在 P1-P8 范围内" >&2
        exit 2
        ;;
esac

if [ ! -d "$TASK_DIR" ]; then
    echo "agate-render-dispatch-prompt.sh: 任务目录不存在: $TASK_DIR" >&2
    exit 2
fi

TEMPLATE="$AGATE_ROOT/assets/templates/dispatch-prompt.md"
if [ ! -f "$TEMPLATE" ]; then
    echo "agate-render-dispatch-prompt.sh: 模板文件不存在: $TEMPLATE" >&2
    exit 2
fi

TASK_ID="$(basename "$TASK_DIR")"
PHASE_NUM="${PHASE#P}"
TODAY="$(date +%Y-%m-%d)"
TRACE_ID="${TASK_ID}-${PHASE}-${TODAY//-/}"

safe_role="$(printf '%s' "$ROLE" | sed 's/[^a-zA-Z0-9_-]/_/g')"
OUTPUT_FILE="$TASK_DIR/P${PHASE_NUM}-dispatch-prompt-${safe_role}.md"

extract_first_code_block() {
    awk '/^```$/{if(!started){started=1;next}else{exit}} started{print}'
}

main_block="$(sed -n '1,/^## 阶段特定提示/p' "$TEMPLATE" | sed '/^## 阶段特定提示/d' | extract_first_code_block)"

appendix=""
case "$PHASE" in
    P2)
        appendix="$(sed -n '/^### P2 派发追加$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        ;;
    P4)
        if [ "$ROLLBACK" = "--rollback" ]; then
            appendix="$(sed -n '/^### P4 回退派发追加/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        else
            appendix="$(sed -n '/^### P4 派发追加$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        fi
        ;;
    P5|P6)
        appendix="$(sed -n '/^### P5\/P6 派发追加$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        ;;
    P8)
        appendix="$(sed -n '/^### P8 派发追加$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
        ;;
esac

rendered="$main_block"
if [ -n "$appendix" ]; then
    rendered="${rendered}"$'\n\n'"${appendix}"
fi

rendered="$(printf '%s' "$rendered" | sed \
    -e "s/{阶段 Pn}/${PHASE}/g" \
    -e "s/{Pn}/${PHASE}/g" \
    -e "s/P{N}/P${PHASE_NUM}/g" \
    -e "s/{角色名}/${ROLE}/g" \
    -e "s/{role}/${ROLE}/g" \
    -e "s|{Txxx}|${TASK_ID}|g" \
    -e "s/{YYYY-MM-DD}/${TODAY}/g" \
    -e "s/{YYYYMMDD}/${TODAY//-/}/g" \
    -e "s/{完整 task_id，如 T002-fix-db-migration}/${TASK_ID}/g" \
    -e "s/{Txxx}-${PHASE}-{YYYYMMDD}/${TRACE_ID}/g" \
)"

header="> 本文件是 agate-render-dispatch-prompt.sh 的渲染产物，不是协议模板。修改本文件不会影响模板。"
final="${header}"$'\n\n'"${rendered}"

printf '%s\n' "$final" > "$OUTPUT_FILE"
printf '%s\n' "$final"
echo "已写入 $OUTPUT_FILE" >&2
