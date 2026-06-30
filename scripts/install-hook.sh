#!/usr/bin/env bash
# install-hook.sh — 安装 pre-commit hook
# 把 pre-commit-gate.sh 链接到 .git/hooks/pre-commit

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || { echo "不在 git 仓库中" >&2; exit 1; })
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"
SOURCE="$REPO_ROOT/scripts/pre-commit-gate.sh"

[ ! -f "$SOURCE" ] && { echo "错误: $SOURCE 不存在" >&2; exit 1; }

mkdir -p "$HOOK_DIR"

# 备份已有 hook
if [ -f "$HOOK_FILE" ] && [ ! -L "$HOOK_FILE" ]; then
    cp "$HOOK_FILE" "$HOOK_FILE.bak.$(date +%s)"
    echo "已备份现有 pre-commit hook"
fi

ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
