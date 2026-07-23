#!/usr/bin/env bats
# tests/unit/agate-retreat-to.bats — agate-retreat-to.sh 自动化多步回退校验

load ../helpers/load.bash

setup() {
    RETREAT_CMD="$AGATE_SCRIPTS/agate-retreat-to.sh"
}

_init_task_repo() {
    local repo="$1"
    local phase="$2"
    local retries_yaml="${3:-retries: {}}"
    mkdir -p "$repo/docs/tasks/T001/P6-evidence/screenshots"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<EOF
task_id: T001
phase: ${phase}
status: active
${retries_yaml}
EOF
    echo "old p6" > "$repo/docs/tasks/T001/P6-acceptance.md"
    touch "$repo/docs/tasks/T001/P6-evidence/screenshots/x.png"
    git_commit "$repo" "init"
}

@test "RETREAT.1 phase=P6 目标 P4，retry 预算充足，产生 2 个独立 commit" {
    local repo
    repo=$(git_init)
    _init_task_repo "$repo" "P6"

    run bash -c "cd '$repo' && bash '$RETREAT_CMD' docs/tasks/T001 P4 '诊断原因测试'"
    [ "$status" -eq 0 ]
    [[ "$output" == *"共 2 步"* ]]

    run bash -c "cd '$repo' && git log --oneline"
    [[ "$output" == *"retreat: P6 -> P5"* ]]
    [[ "$output" == *"retreat: P5 -> P4"* ]]

    run cat "$repo/docs/tasks/T001/.state.yaml"
    [[ "$output" == *"phase: P4"* ]]
    [[ "$output" == *"P5:"* ]]
    [[ "$output" == *"P4:"* ]]
}

@test "RETREAT.2 目标 phase 不低于当前 phase，拒绝执行" {
    local repo
    repo=$(git_init)
    _init_task_repo "$repo" "P4"

    run bash -c "cd '$repo' && bash '$RETREAT_CMD' docs/tasks/T001 P6 '诊断'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"不是回退"* ]]
}

@test "RETREAT.3 路径上 retry 预算不足，预检查阶段拒绝且不做任何操作" {
    local repo
    repo=$(git_init)
    _init_task_repo "$repo" "P6" "retries:
  P5:
  - attempt: 1
  - attempt: 2"

    run bash -c "cd '$repo' && bash '$RETREAT_CMD' docs/tasks/T001 P4 '诊断'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"超限"* ]]

    # 确认没有产生任何 commit，.state.yaml 未变
    run bash -c "cd '$repo' && git log --oneline | wc -l"
    [ "$output" -eq 1 ]
    run cat "$repo/docs/tasks/T001/.state.yaml"
    [[ "$output" == *"phase: P6"* ]]
}

@test "RETREAT.4 暂存区含 TASK_DIR 之外的文件，拒绝执行且不误提交" {
    local repo
    repo=$(git_init)
    _init_task_repo "$repo" "P6"
    mkdir -p "$repo/other-project"
    echo "unrelated" > "$repo/other-project/wip.txt"
    git -C "$repo" add other-project/wip.txt

    run bash -c "cd '$repo' && bash '$RETREAT_CMD' docs/tasks/T001 P4 '诊断'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"TASK_DIR 之外的文件"* ]]
    [[ "$output" == *"wip.txt"* ]]

    # 无关文件依然留在暂存区，没被误提交或清掉
    run bash -c "cd '$repo' && git diff --cached --name-only"
    [[ "$output" == *"wip.txt"* ]]
}

@test "RETREAT.5 目标 phase 不是 P0-P8 合法值" {
    local repo
    repo=$(git_init)
    _init_task_repo "$repo" "P6"

    run bash -c "cd '$repo' && bash '$RETREAT_CMD' docs/tasks/T001 PAUSED '诊断'"
    [ "$status" -eq 1 ]
}
