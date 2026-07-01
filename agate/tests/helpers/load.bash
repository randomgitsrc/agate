#!/usr/bin/env bash
# tests/helpers/load.bash — Bats 全局 setup
# 每个 .bats 文件第一行 load "tests/helpers/load.bash"
#
# 职责：
#   1. 解析 AGATE_ROOT（CI 直接 checkout 时 ~/.agate 软链接不存在）
#   2. 验证路径合法
#   3. 加载 fixtures.bash 和 git-helper.bash

# AGATE_ROOT 解析规则：
#   1. 显式设过 → 用
#   2. 否则 → 用 BATS_TEST_DIRNAME 反推（tests/ 的父目录 = agate/）
export AGATE_ROOT="${AGATE_ROOT:-$(cd "$BATS_TEST_DIRNAME/.." && pwd)}"

# 验证 AGATE_ROOT 下有 scripts/ 和 assets/，防止路径错位
if [ ! -d "$AGATE_ROOT/scripts" ] || [ ! -d "$AGATE_ROOT/assets" ]; then
    echo "FATAL: AGATE_ROOT=$AGATE_ROOT 下找不到 scripts/ 或 assets/" >&2
    echo "  BATS_TEST_DIRNAME=$BATS_TEST_DIRNAME" >&2
    echo "  请检查测试目录结构：tests/ 应在 agate/ 之下" >&2
    return 1
fi

# 加载 fixtures 库
load "$BATS_TEST_DIRNAME/helpers/fixtures.bash"
load "$BATS_TEST_DIRNAME/helpers/git-helper.bash"

# 通用常量
export AGATE_SCRIPTS="$AGATE_ROOT/scripts"
export AGATE_ASSETS="$AGATE_ROOT/assets"
