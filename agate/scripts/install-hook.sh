#!/usr/bin/env bash
# install-hook.sh — 安装 pre-commit hook
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
