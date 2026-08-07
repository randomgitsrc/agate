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

if [ -L "$HOOK_FILE" ]; then
    echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
else
    echo "pre-commit hook 已安装（复制模式，Windows 无符号链接权限）: $HOOK_FILE"
    echo "  ⚠️  升级 agate 后需重跑 install-hook.sh（复制不自动跟随源文件）"
fi

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
    if [ -L "$COMMIT_MSG_HOOK" ]; then
        echo "commit-msg hook 已安装: $COMMIT_MSG_HOOK -> $COMMIT_MSG_SOURCE"
    else
        echo "commit-msg hook 已安装（复制模式）: $COMMIT_MSG_HOOK"
    fi
else
    echo "提示: $COMMIT_MSG_SOURCE 不存在，跳过 commit-msg hook 安装"
fi

# 安装 pre-push hook（协议文件大改动自动提示 alignment-review）
# v0.32.0：与 pre-commit/commit-msg 统一为软链，bug 修复自动分发，无需重装
PRE_PUSH_HOOK="$HOOK_DIR/pre-push"
PRE_PUSH_SOURCE="$AGATE_ROOT/scripts/pre-push-gate.sh"

# 备份已有 pre-push hook（与 pre-commit/commit-msg 一致：仅备份非软链的既有 hook）
if [ -f "$PRE_PUSH_HOOK" ] && [ ! -L "$PRE_PUSH_HOOK" ]; then
    cp "$PRE_PUSH_HOOK" "$PRE_PUSH_HOOK.bak.$(date +%s)"
    echo "已备份现有 pre-push hook"
fi

[ ! -f "$PRE_PUSH_SOURCE" ] && { echo "错误: $PRE_PUSH_SOURCE 不存在（AGATE_ROOT=$AGATE_ROOT）" >&2; exit 1; }
ln -sf "$PRE_PUSH_SOURCE" "$PRE_PUSH_HOOK"
chmod +x "$PRE_PUSH_SOURCE"
if [ -L "$PRE_PUSH_HOOK" ]; then
    echo "pre-push hook 已安装: $PRE_PUSH_HOOK -> $PRE_PUSH_SOURCE (协议文件大改动自动提示)"
else
    echo "pre-push hook 已安装（复制模式）: $PRE_PUSH_HOOK"
fi

# .gitignore 检测：.state.yaml 被忽略时提醒用 git add -f
GITIGNORE="$REPO_ROOT/.gitignore"
if [ -f "$GITIGNORE" ]; then
    if grep -qE '^\s*[*]*\.state\.yaml' "$GITIGNORE"; then
        echo ""
        echo "⚠️  .gitignore 中忽略了 .state.yaml"
        echo "    agate 需要 git add -f 强制暂存 .state.yaml（否则 git add docs/tasks/ 不会暂存它）"
        echo "    建议：从 .gitignore 移除 .state.yaml，或在每次 git add 时记得加 -f"
    fi
fi
