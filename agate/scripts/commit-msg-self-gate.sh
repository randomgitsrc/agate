#!/usr/bin/env bash
# commit-msg-self-gate.sh — commit-msg hook
# 检测 self-gate 触发文件的改动，要求 commit message 含 self-gate-review: 路径
# WARNING 不拦截——遵循 hook 鲁棒性优先原则

set -euo pipefail

COMMIT_MSG_FILE="${1:?用法: commit-msg-self-gate.sh COMMIT_MSG_FILE}"

# 检查暂存区是否含 self-gate 触发文件
SELF_GATE_TRIGGERED=false
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
if echo "$STAGED_FILES" | grep -qE '^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$'; then
    SELF_GATE_TRIGGERED=true
fi

if [ "$SELF_GATE_TRIGGERED" = "false" ]; then
    exit 0
fi

# 检查 commit message 是否含 self-gate-skip: 理由 或 self-gate-review: 路径
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE" 2>/dev/null || true)
if echo "$COMMIT_MSG" | grep -qE '^self-gate-skip:\s*\S+'; then
    exit 0
fi
if echo "$COMMIT_MSG" | grep -qE '^self-gate-review:\s*\S+'; then
    exit 0
fi

echo "GATE SELF-GATE: 暂存区含 self-gate 触发文件（agate/scripts/*.sh / agate/*.md / SELF-GATE.md），" >&2
echo "  但 commit message 未含 self-gate-review: 路径。" >&2
echo "  请先派发 protocol-alignment-review subagent，审查报告路径写入 commit message：" >&2
echo "    self-gate-review: docs/reviews/agate-alignment-review-{date}.md" >&2
echo "  或如果本次改动确实不需要 self-gate（如纯 typo），在 commit message 加：" >&2
echo "    self-gate-skip: 理由" >&2

exit 0
