#!/usr/bin/env bats
# tests/unit/agate-state-get.bats — 状态 YAML 读取共享工具单元测试
load ../helpers/load.bash

@test "STGET.1 phase 读 .state.yaml 的 phase" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' phase"
    [ "$status" -eq 0 ]
    [[ "$output" == "P3" ]]
}

@test "STGET.2 phase 空状态文件 → 空串" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    echo "" > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' phase"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "STGET.3 phase_stdin 从 stdin 读 phase" {
    run bash -c "echo 'task_id: T1
phase: P5' | $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' phase_stdin"
    [ "$status" -eq 0 ]
    [[ "$output" == "P5" ]]
}

@test "STGET.4 task_id 读 .state.yaml 的 task_id" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T042
phase: P1
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' task_id"
    [ "$status" -eq 0 ]
    [[ "$output" == "T042" ]]
}

@test "STGET.5 retries_over 首个超限阶段" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P3
retries:
  P1:
    - {attempt: 1}
    - {attempt: 2}
    - {attempt: 3}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' retries_over 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [[ "$output" == "P1=3 (MAX=3)"* ]]
}

@test "STGET.6 retries_over 无超限 → 空输出" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P3
retries:
  P1:
    - {attempt: 1}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' retries_over 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}