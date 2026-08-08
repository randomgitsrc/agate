#!/usr/bin/env bats
# tests/unit/agate-card-inject.bats — agate-card-inject.py 工具单元测试
# 注意：文件名用 agate-card-inject（非 agate-inject-card），避免与
# agate-inject-card.sh 的测试文件 agate-inject-card.bats 冲突。
load ../helpers/load.bash

@test "IC.1 注入卡片到占位符之间" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ic-XXXXXX")
    printf 'pre\n<!-- AGATE_CARD_START -->\nold\n<!-- AGATE_CARD_END -->\npost\n' > "$dir/dc.md"
    echo "newcard" > "$dir/card.md"
    run bash -c "DC_FILE='$dir/dc.md' CARD_FILE='$dir/card.md' python3 '$AGATE_SCRIPTS/agate-card-inject.py'"
    [ "$status" -eq 0 ]
    run cat "$dir/dc.md"
    [[ "$output" == *"newcard"* ]]
    [[ "$output" != *"old"* ]]
}

@test "IC.2 无占位符 → 非零退出" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ic-XXXXXX")
    echo "no placeholder" > "$dir/dc.md"
    echo "card" > "$dir/card.md"
    run bash -c "DC_FILE='$dir/dc.md' CARD_FILE='$dir/card.md' python3 '$AGATE_SCRIPTS/agate-card-inject.py'"
    [ "$status" -ne 0 ]
}