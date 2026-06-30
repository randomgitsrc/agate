#!/usr/bin/env bash
# install.sh — agate 协议安装脚本
# 默认把仓库克隆到 $HOME/oclab/agate，创建 ~/.agate 软链接
# 可通过环境变量 AGATE_REPO_DIR 自定义安装目录

set -euo pipefail

INSTALL_DIR="${AGATE_REPO_DIR:-$HOME/oclab/agate}"
LINK_TARGET="$INSTALL_DIR/agate"
LINK_NAME="${AGATE_SYMLINK:-$HOME/.agate}"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "仓库已存在: $INSTALL_DIR"
    cd "$INSTALL_DIR" && git pull
else
    echo "克隆仓库到: $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone https://github.com/randomgitsrc/agate.git "$INSTALL_DIR"
fi

if [ -L "$LINK_NAME" ]; then
    CURRENT=$(readlink "$LINK_NAME")
    if [ "$CURRENT" = "$LINK_TARGET" ]; then
        echo "软链接已正确: $LINK_NAME -> $LINK_TARGET"
    else
        echo "更新软链接: $LINK_NAME (原指向 $CURRENT)"
        ln -sfn "$LINK_TARGET" "$LINK_NAME"
    fi
elif [ -d "$LINK_NAME" ]; then
    echo "错误: $LINK_NAME 是现有目录（非软链接），请手动处理" >&2
    echo "建议: mv $LINK_NAME ${LINK_NAME}.bak && ln -s $LINK_TARGET $LINK_NAME" >&2
    exit 1
else
    ln -s "$LINK_TARGET" "$LINK_NAME"
    echo "创建软链接: $LINK_NAME -> $LINK_TARGET"
fi

echo ""
echo "安装完成。"
echo "  仓库: $INSTALL_DIR"
echo "  软链接: $LINK_NAME -> $LINK_TARGET"
echo ""
echo "自定义位置:"
echo "  AGATE_REPO_DIR=/path/to/clone bash install.sh   # 指定仓库路径"
echo "  AGATE_SYMLINK=/path/to/symlink bash install.sh # 指定软链接路径"
echo ""
echo "下一步:"
echo "  1. 在项目里: cp $LINK_NAME/orchestrator-template.md \\"
echo "                 your-project/docs/agents/orchestrator.md"
echo "  2. 在项目里: bash $LINK_NAME/scripts/install-hook.sh"
