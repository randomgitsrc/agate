#!/usr/bin/env bash
# pre-push-gate.sh — pre-push hook：协议文件（agate/*.md）大改动自动提示 alignment-review
# 由 install-hook.sh 以软链方式安装到 .git/hooks/pre-push
# git 以仓库根为 cwd 执行（与 pre-commit-gate.sh 相同），stdin 收 local_ref/local_sha/remote_ref/remote_sha
# exit 0 = 不阻断 push；仅提示。

set -euo pipefail

THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20}"
ZERO_SHA="0000000000000000000000000000000000000000"

# shellcheck disable=SC2034  # remote_ref 为 pre-push stdin 格式占位，未使用
while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        echo "ℹ️  新分支首次推送，跳过 agate/*.md 改动量检测（无远端基线可比较）"
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || true)
    CHANGED_LINES="${CHANGED_LINES:-0}"
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "⚠️  本次 push（${local_ref}）对 agate/*.md 的改动达 ${CHANGED_LINES} 行（阈值 ${THRESHOLD}）"
        echo "    建议先派发一次 protocol-alignment-review，确认改动未破坏协议文件间的语义一致性。"
        echo "    忽略本提示继续 push：git push --no-verify"
    fi
done

exit 0