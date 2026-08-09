#!/usr/bin/env bats
# tests/regression/v060-p8-internal-only.bats — 回归测试：裁剪 P8 需 internal_only
# 触发：fabca40 hardening R5
# T001 v2.0 流 A（BDD-1/9）改写：internal_only/internal_only_reason 现由
# add_p1_field 写入 P1-requirements.md 的 frontmatter 块（而非 v0.35 的正文追加，
# 详见 tests/helpers/fixtures.bash add_p1_field）——check-pruning.sh 仍能正确读取
# 这两个 presence 语义字段（BDD-1"门禁基于 frontmatter 声明值完成判定"）。@test 数保持 3 不变。

load ../helpers/load.bash

@test "R4.1 裁剪 P8 无 internal_only → exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)  # P8 不在
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"internal_only"* ]]
}

@test "R4.2 BDD-1: 裁剪 P8 + frontmatter internal_only: true + internal_only_reason → exit 0" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)
    add_p1_field "$dir" "internal_only" "true"
    add_p1_field "$dir" "internal_only_reason" "内部工具，无外部用户"
    add_pruning_excuse "$dir" P8 "内部任务" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
    grep -qE '^---$' "$dir/P1-requirements.md"
    grep -q '^internal_only: true$' "$dir/P1-requirements.md"
}

@test "R4.3 BDD-1: 裁剪 P8 + frontmatter internal_only: true 但无 internal_only_reason → exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)
    add_p1_field "$dir" "internal_only" "true"
    add_pruning_excuse "$dir" P8 "内部任务" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"internal_only_reason"* ]]
}
