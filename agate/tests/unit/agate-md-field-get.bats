#!/usr/bin/env bats
# tests/unit/agate-md-field-get.bats — MD 字段提取共享工具单元测试
load ../helpers/load.bash

@test "MDF.1 risk_level 提取 low/medium/high" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "risk_level: high" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [[ "$output" == "high" ]]
}

@test "MDF.2 risk_level 无匹配 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "no risk" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' risk_level"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "MDF.3 ui_affected 提取 true/false" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "ui_affected: true" > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' ui_affected"
    [ "$status" -eq 0 ]; [[ "$output" == "true" ]]
}

@test "MDF.4 ui_affected 无匹配 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "no ui" > "$dir/P2.md"
    run bash -c "FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' ui_affected"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "MDF.5 phases 行内列表 [a, b, c] → 空格连接" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    echo "phases: [P0, P1, P2]" > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' phases"
    [ "$status" -eq 0 ]; [[ "$output" == "P0 P1 P2" ]]
}

@test "MDF.6 phases 块式列表 → 空格连接" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/md-XXXXXX")
    printf 'phases:\n  - P0\n  - P1\n' > "$dir/P1.md"
    run bash -c "FILE='$dir/P1.md' python3 '$AGATE_SCRIPTS/agate-md-field-get.py' phases"
    [ "$status" -eq 0 ]; [[ "$output" == "P0 P1" ]]
}