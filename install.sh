#!/usr/bin/env bash
# install.sh — agate 协议安装脚本（单软链布局，兼容保留）
# 默认把仓库克隆到 $HOME/oclab/agate，创建 ~/.agate 软链接
# 可通过环境变量 AGATE_REPO_DIR 自定义安装目录
#
# ⚠️ 兼容保留说明（TAG0008）：本脚本保持"单软链"形态，存量用户升级路径不破坏。
# 需要按项目锁定版本时，改用版本管理工具（TAG0008 起）：
#   python3 ~/.agate/scripts/agate-install.py            # 装最新版（vX.Y.Z/ 版本目录 + latest/current 指针）
#   python3 ~/.agate/scripts/agate-install.py v0.48.0    # 装指定版本
# 版本管理布局下 ~/.agate 变为目录，legacy 软链直接解析为 AGATE_ROOT（向后兼容，见 UPGRADING v0.50.0）。

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
    git clone https://github.com/randomgitsrc/agateon.git "$INSTALL_DIR"
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
echo "  在项目里按 $LINK_NAME/SETUP.md 的步骤把 orchestrator 注册成"
echo "  OpenCode/Claude Code 能调用的 agent（含装 hook 那一步）"
