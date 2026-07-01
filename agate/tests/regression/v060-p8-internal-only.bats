#!/usr/bin/env bats
# tests/regression/v060-p8-internal-only.bats — 回归测试：裁剪 P8 需 internal_only
# 触发：fabca40 hardening R5

load ../helpers/load.bash

@test "R4.1 裁剪 P8 无 internal_only → exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)  # P8 不在
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"internal_only"* ]]
}

@test "R4.2 裁剪 P8 + internal_only: true → exit 0" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)
    add_p1_field "$dir" "internal_only" "true"
    add_pruning_excuse "$dir" P8 "内部任务" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}
