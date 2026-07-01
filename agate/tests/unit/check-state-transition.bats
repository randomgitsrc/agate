#!/usr/bin/env bats
# tests/unit/check-state-transition.bats — 8 用例覆盖 check-state-transition.sh
# 计划：5.7 / 实际 8 行 / 与附录 A 一致

load ../helpers/load.bash

# 注意：此脚本需要真实 git 仓库（用 git show HEAD:file）

@test "ST.1 check-state-transition.sh 无 .state.yaml 暂存 期望 exit 0" {
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md"
    git_commit "$repo" "init"
    # .state.yaml 未暂存
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 0 ]
}

@test "ST.2 check-state-transition.sh 新 phase: P1（首次）期望 exit 0" {
    local repo
    repo=$(git_init)
    # HEAD 没有 .state.yaml，新文件
    cp "$AGATE_ROOT/tests/fixtures/full-task/.state.yaml" "$repo/.state.yaml"
    # 不暂存
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # 没有 staged change → exit 0
    [ "$status" -eq 0 ]
}

@test "ST.3 check-state-transition.sh 顺序跳 P1→P3（差 2）期望 exit 0" {
    local repo
    repo=$(git_init)
    # 先 commit 旧 .state.yaml
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    # 改 phase 到 P3 并暂存
    sed -i 's/phase: P1/phase: P3/' "$repo/.state.yaml"
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # 顺序跳 P1→P3 = forward，跳 2，没限制
    [ "$status" -eq 0 ]
}

@test "ST.4 check-state-transition.sh 回退 P3→P1（差 2）降级 WARNING 期望 exit 0" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    sed -i 's/phase: P3/phase: P1/' "$repo/.state.yaml"
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # 回退 P3→P1 差 2 是 WARNING，不 exit 1
    [ "$status" -eq 0 ]
}

@test "ST.5 check-state-transition.sh 回退 P4→P2（差 2）降级 WARNING 期望 exit 0" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    sed -i 's/phase: P4/phase: P2/' "$repo/.state.yaml"
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 0 ]
}

@test "ST.6 check-state-transition.sh retries[P2]>=3 + phase 非 PAUSED 期望 exit 1" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries:
  P2:
    - attempt: 1
    - attempt: 2
    - attempt: 3
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 1 ]
    [[ "$output" == *"PAUSED"* ]]
}

@test "ST.7 check-state-transition.sh retries[P2]>=3 + phase: PAUSED 期望 exit 0" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries:
  P2:
    - attempt: 1
    - attempt: 2
    - attempt: 3
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 0 ]
}

@test "ST.8 check-state-transition.sh 终止态 PAUSED/READY/DONE 期望 exit 0" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    # 改为 PAUSED
    sed -i 's/phase: P1/phase: PAUSED/' "$repo/.state.yaml"
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 0 ]
}
