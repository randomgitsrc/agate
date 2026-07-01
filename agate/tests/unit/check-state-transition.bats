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

@test "ST.4 check-state-transition.sh 回退 P3→P1（差 2）期望 exit 1（强制 PAUSED）" {
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
    # 修复后回退 P3→P1 差 2 强制 PAUSED，exit 1
    [ "$status" -eq 1 ]
    [[ "$output" == *"PAUSED"* ]]
}

@test "ST.5 check-state-transition.sh 回退 P4→P2（差 2）期望 exit 1（强制 PAUSED）" {
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
    [ "$status" -eq 1 ]
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

# ── A 组：MAX_RETRY 按阶段差异化 ────────────────────────────────────────────

@test "ST.9 check-state-transition.sh retries[P3]>=2 + phase 非 PAUSED 期望 exit 1（P3 MAX=2）" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries:
  P3:
    - attempt: 1
    - attempt: 2
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 1 ]
    [[ "$output" == *"PAUSED"* ]]
    [[ "$output" == *"P3"* ]]
}

@test "ST.10 check-state-transition.sh retries[P5]>=2 + phase 非 PAUSED 期望 exit 1（P5 MAX=2）" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P5
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P6
status: active
retries:
  P5:
    - attempt: 1
    - attempt: 2
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P5"* ]]
}

@test "ST.11 check-state-transition.sh 多阶段 retries 不同阈值 期望 exit 0（P2:2 不超, P3:1 不超）" {
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
  P3:
    - attempt: 1
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # P2: 2 < 3 (MAX) → 不超限
    # P3: 1 < 2 (MAX) → 不超限
    [ "$status" -eq 0 ]
}

@test "ST.12 check-state-transition.sh retries[P2]=3 + retries[P3]=2 期望 exit 1（任一超限）" {
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
phase: P4
status: active
retries:
  P2:
    - attempt: 1
    - attempt: 2
    - attempt: 3
  P3:
    - attempt: 1
    - attempt: 2
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # P2: 3 >= 3 → 超限；P3: 2 >= 2 → 超限
    # Python 报告第一个匹配后 break，exit 1
    [ "$status" -eq 1 ]
}

# ── B 组：回退跳变恢复 exit 1 + 保留守卫 ────────────────────────────────────

@test "ST.13 check-state-transition.sh 回退 P3→P1（差 2）期望 exit 1（恢复强制 PAUSED）" {
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
    # 恢复 exit 1 后回退 P3→P1 差 2 应拦截
    [ "$status" -eq 1 ]
    [[ "$output" == *"PAUSED"* ]]
}

@test "ST.14 check-state-transition.sh 回退 P4→P2（差 2）期望 exit 1（恢复强制 PAUSED）" {
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
    [ "$status" -eq 1 ]
}

@test "ST.15 check-state-transition.sh PAUSED→P3 恢复 期望 exit 0（验证 old_num 守卫）" {
    local repo
    repo=$(git_init)
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    git_commit "$repo" "init"
    # 先 PAUSED
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries: {}
EOF
    git_commit "$repo" "paused"
    # 恢复到 P4
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries: {}
EOF
    git_stage "$repo" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' .state.yaml"
    # PAUSED→P4 是合法恢复，应 exit 0
    [ "$status" -eq 0 ]
}
