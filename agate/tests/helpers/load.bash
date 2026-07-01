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
#   2. 否则 → 用 BATS_TEST_DIRNAME 反推
#      - 顶层测试（如 sanity.bats）→ $BATS_TEST_DIRNAME = tests/ → 父目录 = agate/
#      - 单元测试（unit/*.bats）→ $BATS_TEST_DIRNAME = tests/unit/ → 上溯两级 = agate/
#
# 用 git rev-parse 反推更可靠：tests/ 在 git 仓库的 agate/ 子目录下，
# 找最近的 agate/scripts 即可
_resolve_agate_root() {
    local dir="$BATS_TEST_DIRNAME"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/scripts" ] && [ -d "$dir/assets" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

export AGATE_ROOT="${AGATE_ROOT:-$(_resolve_agate_root)}"

# 验证 AGATE_ROOT 下有 scripts/ 和 assets/，防止路径错位
if [ ! -d "$AGATE_ROOT/scripts" ] || [ ! -d "$AGATE_ROOT/assets" ]; then
    echo "FATAL: AGATE_ROOT=$AGATE_ROOT 下找不到 scripts/ 或 assets/" >&2
    echo "  BATS_TEST_DIRNAME=$BATS_TEST_DIRNAME" >&2
    echo "  请检查测试目录结构：tests/ 应在 agate/ 之下" >&2
    return 1
fi

# 加载 fixtures 库（用绝对路径，避免 load() 的 $BATS_TEST_DIRNAME 解析问题）
_HELPERS_DIR="$(cd "$BATS_TEST_DIRNAME/.." 2>/dev/null && pwd)/helpers"
[ -d "$_HELPERS_DIR" ] || _HELPERS_DIR="$BATS_TEST_DIRNAME/helpers"
source "$_HELPERS_DIR/fixtures.bash"
source "$_HELPERS_DIR/git-helper.bash"

# 通用常量
export AGATE_SCRIPTS="$AGATE_ROOT/scripts"
export AGATE_ASSETS="$AGATE_ROOT/assets"
