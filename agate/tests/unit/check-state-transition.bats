#!/usr/bin/env bats
# tests/unit/check-state-transition.bats — 20 用例覆盖 check-state-transition.sh

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
    # 先 commit 旧 .state.yaml + P1 产出（commit gate 要求旧产出已 commit）
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/P1-requirements.md" <<'EOF'
risk_level: medium
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
- Given test
EOF
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/
    git -C "$repo" commit -qm "init"
    # 改 phase 到 P3 并暂存
    sed -i 's/phase: P1/phase: P3/' "$repo/docs/tasks/T001/.state.yaml"
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
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
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P2 design" > "$repo/docs/tasks/T001/P2-design.md"
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add .state.yaml docs/tasks/T001/
    git -C "$repo" commit -qm "init"
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

# ========== 检查 3: commit gate（逐阶段 commit 强制）==========

@test "ST.16 commit gate: P1→P2 推进，P1 产出已 commit → exit 0" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/P1-requirements.md" <<'EOF'
risk_level: medium
phases: [P0, P1, P2, P3]
- Given test
EOF
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/
    git -C "$repo" commit -qm "T001 P1"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -eq 0 ]
}

@test "ST.17 commit gate: P1→P2 推进，P1 产出在暂存区未 commit → exit 1" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "T001 phase P1"
    # P1 产出 + phase 改 P2 在同一个暂存区
    echo "# P1 output" > "$repo/docs/tasks/T001/P1-requirements.md"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -ne 0 ]
    [[ "$output" == *"产出必须已 commit"* ]]
}

@test "ST.18 commit gate: P1→P2 推进，P1 产出从未 commit → exit 1" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "T001 phase P1"
    # 改 phase 到 P2，但 P1 产出从未创建
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -ne 0 ]
    [[ "$output" == *"尚未 commit"* ]]
}

@test "ST.19 commit gate: PAUSED→P3 恢复 → 跳过 commit gate" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P2 design" > "$repo/docs/tasks/T001/P2-design.md"
    git -C "$repo" add docs/tasks/T001/P2-design.md
    # 状态 machine PAUSED（old_phase 无数字）
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "Paused"
    # 恢复到 P3
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -eq 0 ]
}

@test "ST.20 commit gate: P3→P1 回退 → 跳过 commit gate" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    echo "# P1" > "$repo/docs/tasks/T001/P1-requirements.md"
    git -C "$repo" add docs/tasks/T001/P1-requirements.md
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "T001 P3"
    # 回退到 P1
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    # 回退自身被检查 1 拦截（exit 1），但我们只验证 commit gate 不触发
    # 所以这里不 assert exit code，只 assert 输出不含 commit gate 消息
    [[ "$output" != *"产出必须已 commit"* ]]
    [[ "$output" != *"尚未 commit"* ]]
}
