#!/usr/bin/env bats
# tests/unit/check-pruning.bats — 19 用例覆盖 check-pruning.sh
# 计划：5.1 / 实际 19 行 / 与附录 A 一致
# 参考：docs/plans/agate-test-plan-2026-07-01.md 5.1

load ../helpers/load.bash

# ============== 检查 1：risk_level 必填 ==============

@test "P2.1 check-pruning.sh 缺 risk_level 期望 exit 1" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    # 只写 phases，不写 risk_level
    echo "phases: [P0, P1, P2]" > "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺 risk_level"* ]]
}

# ============== 检查 2：P2 不可裁剪（4 个例外口子用例） ==============

@test "P2.2 check-pruning.sh 裁剪 P2 无例外口 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2 不可裁剪"* ]]
}

@test "P2.3a check-pruning.sh 裁剪 P2 + legacy_p2_pruned: true 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    add_p1_field "$dir" "legacy_p2_pruned" "true"
    add_pruning_excuse "$dir" P2 "v0.5 任务" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "P2.3b check-pruning.sh 裁剪 P2 + design_trivial: true 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    add_p1_field "$dir" "design_trivial" "true"
    add_pruning_excuse "$dir" P2 "文案修改" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "P2.3c check-pruning.sh 裁剪 P2 + follows_existing_pattern: [src/foo.py] 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    add_p1_field "$dir" "follows_existing_pattern" "[src/foo.py]"
    add_pruning_excuse "$dir" P2 "照搬" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "P2.3d check-pruning.sh 裁剪 P2 + follows_existing_pattern: [] 空参照 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    add_p1_field "$dir" "follows_existing_pattern" "[]"
    add_pruning_excuse "$dir" P2 "空参照" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2 不可裁剪"* ]]
}

# ============== 检查 3：P6 不可裁剪 ==============

@test "P2.4 check-pruning.sh 裁剪 P6 无 no_behavior_change 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P7 P8)
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6 不可裁剪"* ]]
}

@test "P2.4a check-pruning.sh 裁剪 P6 + no_behavior_change: true 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P7 P8)
    add_p1_field "$dir" "no_behavior_change" "true"
    add_pruning_excuse "$dir" P6 "无行为变更" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

# ============== 检查 4：高风险不可裁 P3 ==============

@test "P2.5 check-pruning.sh risk=high 裁剪 P3 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8 --risk-level high)
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"高风险任务不可裁剪 P3"* ]]
}

@test "P2.5b check-pruning.sh risk=medium 裁剪 P3 缺跳过风险 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8 --risk-level medium)
    # medium 风险 + P3 裁剪是允许的，但需要写"跳过风险:"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"跳过风险"* ]]
}

# ============== 检查 5/6：裁剪 P7 需源码文件数 ≤ 5 + implicit_coupling ==============

@test "P2.6a check-pruning.sh 裁剪 P7，源文件数 > 5 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P5 P6 P8)  # P7 不在声明
    local repo
    repo=$(git_init)
    # 在 repo 创建 6 个源文件并 commit
    for i in 1 2 3 4 5 6; do
        echo "file $i" > "$repo/src_$i.py"
    done
    git_commit "$repo" "init"
    # 在 repo 复制 task dir
    cp -r "$dir" "$repo/task"
    # 暂存 6 个文件
    git -C "$repo" add src_*.py
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-pruning.sh' 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"源文件数"* || "$output" == *"implicit_coupling"* || "$output" == *"跳过风险"* ]]
}

@test "P2.6b check-pruning.sh 裁剪 P7，源文件数 ≤ 5 通过" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P5 P6 P8)  # P7 不在声明
    add_pruning_excuse "$dir" P7 "小改动" "低"
    local repo
    repo=$(git_init)
    for i in 1 2 3; do
        echo "file $i" > "$repo/src_$i.py"
    done
    git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    git -C "$repo" add src_*.py
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-pruning.sh' 'task'"
    [ "$status" -eq 0 ]
}

@test "P2.6c check-pruning.sh 裁剪 P7 + implicit_coupling 字段 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P5 P6 P8)  # P7 不在声明
    add_p1_field "$dir" "implicit_coupling" "[api-schema, data-model]"
    add_pruning_excuse "$dir" P7 "理由" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"implicit_coupling"* ]]
}

# ============== 检查 7：P8 需 internal_only ==============

@test "P2.7 check-pruning.sh 裁剪 P8 无 internal_only 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P8 不可裁"* || "$output" == *"internal_only"* ]]
}

@test "P2.7a check-pruning.sh 裁剪 P8 + internal_only: true 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)
    add_p1_field "$dir" "internal_only" "true"
    add_pruning_excuse "$dir" P8 "内部任务" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

# ============== 检查 8：裁剪理由必含"跳过风险" ==============

@test "P2.8 check-pruning.sh 裁剪理由缺'跳过风险' 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    # 写裁剪理由但不写跳过风险
    cat >> "$dir/P1-requirements.md" <<EOF

裁剪 P2: 某种理由
EOF
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"跳过风险"* ]]
}

# ============== 检查 9：裁剪声明与执行不一致 ==============

@test "P2.9 check-pruning.sh 裁剪声明 vs 实际有产出文件 + 无 override 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)  # P2 不在声明
    # 但创建 P2-design.md 文件
    echo "actual design" > "$dir/P2-design.md"
    add_pruning_excuse "$dir" P2 "理由" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"裁剪声明与执行不一致"* ]]
}

@test "P2.9a check-pruning.sh 裁剪声明 vs 实际有产出文件 + override 放行" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    echo "actual design" > "$dir/P2-design.md"
    # override 只解除检查 9 (P2.9 声明与执行不一致)，不解除检查 2 (P2 不可裁)
    # 所以需要同时给 P2 一个例外口（这里用 legacy_p2_pruned）
    add_p1_field "$dir" "override" "P2 retained manually"
    add_p1_field "$dir" "legacy_p2_pruned" "true"
    add_pruning_excuse "$dir" P2 "理由" "低"
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}

# ============== 边界 case ==============

@test "P2.10 check-pruning.sh 无 P1 文件 期望 exit 2" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 2 ]
}

@test "P2.11 check-pruning.sh 全合规 (happy path) 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}
