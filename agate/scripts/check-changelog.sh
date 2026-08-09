#!/usr/bin/env bash
# check-changelog.sh — CHANGELOG [Unreleased] 含 task_id 检查（P1.6）
# exit 0 = 通过; exit 1 = 未记录; 无 CHANGELOG 文件时 exit 0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"

# v2.0 流 D（BDD-27，P2-design.md §3.4.2）：不再截取短前缀，直接用完整 task_id
# 作为 CHANGELOG 搜索关键词。新格式 task_id（如 TAG0001）本身就是完整短标识，
# 旧版 grep -oE 'T[0-9]+' 对 T 后紧跟字母的新格式会提取为空（F17）。
TASK_ID_SHORT="$TASK_ID"
CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"

[ ! -f "$CHANGELOG_FILE" ] && exit 0

# 问题6 (T090)：post-bump 模式（bump-version 调用时）——检查新版本段落非空，而非 [Unreleased]
if [ "${CHECK_CHANGELOG_MODE:-normal}" = "post-bump" ]; then
    LATEST_SECTION=$(grep -E '^## \[' "$CHANGELOG_FILE" | head -1 || true)
    [ -z "$LATEST_SECTION" ] && { echo "GATE CHANGELOG: 无版本段落" >&2; exit 1; }
    exit 0
fi

UNRELEASED_CONTENT=$(CHANGELOG_FILE="$CHANGELOG_FILE" python3 "$SCRIPT_DIR/agate-changelog-unreleased.py" 2>/dev/null || echo "")

if [ -z "$UNRELEASED_CONTENT" ]; then
    echo "GATE CHANGELOG: ${CHANGELOG_FILE} 无 [Unreleased] 区域" >&2
    exit 1
fi

if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)" 2>/dev/null; then
    exit 0
fi
# 无固定字符串 fallback：TASK_ID_SHORT 现已等于完整 TASK_ID，若再对 TASK_ID 做
# grep -qF 固定字符串匹配会失去上面的单词边界保护，导致 TAG0001 被 TAG00012
# 这类"更长编号任务"的条目误判为匹配（BDD-27 / CL.7 明确要求不误匹配）。
echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID_SHORT}（或 ${TASK_ID}）" >&2
exit 1
