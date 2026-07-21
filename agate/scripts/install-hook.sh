#!/usr/bin/env bash
# install-hook.sh — 安装 pre-commit hook + commit-msg hook + pre-push hook
# 把 agate 的 pre-commit-gate.sh 链接到当前 git 仓库的 .git/hooks/pre-commit
#
# 用法：
#   bash ~/.agate/scripts/install-hook.sh                     # 默认 ~/.agate
#   bash ~/.agate/scripts/install-hook.sh /path/to/agate_root
#
# 此脚本应在**项目仓库**内运行（不在 agate 仓库内）。
# AGATE_ROOT 默认指向 ~/.agate（软链接 → agate/ 协议本体）。

set -euo pipefail

AGATE_ROOT="${1:-${AGATE_ROOT:-$HOME/.agate}}"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || { echo "不在 git 仓库中" >&2; exit 1; })
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"
SOURCE="$AGATE_ROOT/scripts/pre-commit-gate.sh"

[ ! -f "$SOURCE" ] && { echo "错误: $SOURCE 不存在（AGATE_ROOT=$AGATE_ROOT）" >&2; exit 1; }

mkdir -p "$HOOK_DIR"

# 备份已有 hook
if [ -f "$HOOK_FILE" ] && [ ! -L "$HOOK_FILE" ]; then
    cp "$HOOK_FILE" "$HOOK_FILE.bak.$(date +%s)"
    echo "已备份现有 pre-commit hook"
fi

ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"

# 安装 commit-msg hook（self-gate 强制触发）
COMMIT_MSG_HOOK="$HOOK_DIR/commit-msg"
COMMIT_MSG_SOURCE="$AGATE_ROOT/scripts/commit-msg-self-gate.sh"

if [ -f "$COMMIT_MSG_SOURCE" ]; then
    if [ -f "$COMMIT_MSG_HOOK" ] && [ ! -L "$COMMIT_MSG_HOOK" ]; then
        cp "$COMMIT_MSG_HOOK" "$COMMIT_MSG_HOOK.bak.$(date +%s)"
        echo "已备份现有 commit-msg hook"
    fi
    ln -sf "$COMMIT_MSG_SOURCE" "$COMMIT_MSG_HOOK"
    chmod +x "$COMMIT_MSG_SOURCE"
    echo "commit-msg hook 已安装: $COMMIT_MSG_HOOK -> $COMMIT_MSG_SOURCE"
else
    echo "提示: $COMMIT_MSG_SOURCE 不存在，跳过 commit-msg hook 安装"
fi

# 安装 pre-push hook（协议文件大改动自动提示 alignment-review）
PRE_PUSH_HOOK="$HOOK_DIR/pre-push"
cat > "$PRE_PUSH_HOOK" << 'HOOK_EOF'
#!/usr/bin/env bash
THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20}"
ZERO_SHA="0000000000000000000000000000000000000000"

while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        echo "ℹ️  新分支首次推送，跳过 agate/*.md 改动量检测（无远端基线可比较）"
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || echo 0)
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "⚠️  本次 push（${local_ref}）对 agate/*.md 的改动达 ${CHANGED_LINES} 行（阈值 ${THRESHOLD}）"
        echo "    建议先派发一次 protocol-alignment-review，确认改动未破坏协议文件间的语义一致性。"
        echo "    忽略本提示继续 push：git push --no-verify"
    fi
done
exit 0
HOOK_EOF
chmod +x "$PRE_PUSH_HOOK"
echo "pre-push hook 已安装: $PRE_PUSH_HOOK (协议文件大改动自动提示)"
