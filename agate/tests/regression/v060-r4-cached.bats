#!/usr/bin/env bats
# tests/regression/v060-r4-cached.bats — 回归测试：裁剪 P7 用 --cached 不是 HEAD~1
# 触发：fabca40 "feat(hardening): check-pruning.sh 补 P7/P8 裁剪条件"
# 教训：pre-commit 时本次变更还没进 HEAD，用 HEAD~1 会看不到

load ../helpers/load.bash

@test "R3.1 裁剪 P7 + 暂存区 6 个源文件 → exit 1（源码文件数 > 5 拦截）" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P5 P6 P8)  # P7 不在
    add_pruning_excuse "$dir" P7 "源文件多" "中等"
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md"
    git_commit "$repo" "init"
    for i in 1 2 3 4 5 6; do
        echo "f$i" > "$repo/src_$i.py"
    done
    cp -r "$dir" "$repo/task"
    # 暂存新增的 6 个 src_*.py
    git -C "$repo" add src_*.py
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-pruning.sh' 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"裁剪 P7 需源码文件数"* ]]
}

@test "R3.2 裁剪 P7 + 暂存区 3 个源文件 + coupling_checklist → exit 0（≤ 5）" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P5 P6 P8)  # P7 不在
    add_p1_field "$dir" "coupling_checklist" "[api-schema: checked]"
    add_pruning_excuse "$dir" P7 "小改动" "低"
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md"
    git_commit "$repo" "init"
    for i in 1 2 3; do
        echo "f$i" > "$repo/src_$i.py"
    done
    cp -r "$dir" "$repo/task"
    git -C "$repo" add src_*.py
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-pruning.sh' 'task'"
    [ "$status" -eq 0 ]
}
