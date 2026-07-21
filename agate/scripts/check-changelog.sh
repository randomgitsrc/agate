#!/usr/bin/env bash
# check-changelog.sh — CHANGELOG [Unreleased] 含 task_id 检查（P1.6）
# exit 0 = 通过; exit 1 = 未记录; 无 CHANGELOG 文件时 exit 0

set -euo pipefail

TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"

# 提取 task_id 短前缀（T\d+）作为 CHANGELOG 搜索关键词
# .state.yaml 的 task_id 可能是完整目录名（T060-archived-visibility-auth-refresh），
# 但 CHANGELOG 条目通常只写短前缀（T060）
TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)
[ -z "$TASK_ID_SHORT" ] && TASK_ID_SHORT="$TASK_ID"
CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"

[ ! -f "$CHANGELOG_FILE" ] && exit 0

UNRELEASED_CONTENT=$(CHANGELOG_FILE="$CHANGELOG_FILE" python3 -c "
import re, os
with open(os.environ['CHANGELOG_FILE']) as f:
    text = f.read()
m = re.search(r'##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)', text, re.S)
if m:
    print(m.group(1))
" 2>/dev/null || echo "")

if [ -z "$UNRELEASED_CONTENT" ]; then
    echo "GATE CHANGELOG: ${CHANGELOG_FILE} 无 [Unreleased] 区域" >&2
    exit 1
fi

if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)" 2>/dev/null; then
    exit 0
fi
# fallback: 尝试完整 task_id 固定字符串匹配（如 CHANGELOG 写了完整目录名）
if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID" 2>/dev/null; then
    exit 0
fi
echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID_SHORT}（或 ${TASK_ID}）" >&2
exit 1
