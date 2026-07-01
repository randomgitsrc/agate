#!/usr/bin/env bash
# check-changelog.sh — CHANGELOG [Unreleased] 含 task_id 检查（P1.6）
# exit 0 = 通过; exit 1 = 未记录; 无 CHANGELOG 文件时 exit 0

set -euo pipefail

TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"
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

if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID"; then
    exit 0
else
    echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID}" >&2
    exit 1
fi
