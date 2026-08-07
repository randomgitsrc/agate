#!/usr/bin/env bats
# tests/unit/agate-retreat-state.bats — 回退状态读写专用工具单元测试
load ../helpers/load.bash

@test "RSTATE.1 check_retreat 路径上阶段超限 → 输出 phase:count:limit" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
retries:
  P3:
    - {attempt: 1}
    - {attempt: 2}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' CUR=4 TGT=2 python3 '$AGATE_SCRIPTS/agate-retreat-state.py' check_retreat 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [[ "$output" == "P3:3:2" ]]
}

@test "RSTATE.2 check_retreat 无超限 → 空输出" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
retries:
  P3:
    - {attempt: 1}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' CUR=4 TGT=2 python3 '$AGATE_SCRIPTS/agate-retreat-state.py' check_retreat 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "RSTATE.3 write_retreat 追加 retry + 改 phase + 回写" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/rs-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T1
phase: P4
status: active
retries:
  P3:
    - {attempt: 1, reason: x}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' NEW_PHASE=P3 RETREAT_REASON='test reason' python3 '$AGATE_SCRIPTS/agate-retreat-state.py' write_retreat"
    [ "$status" -eq 0 ]
    run cat "$dir/.state.yaml"
    [[ "$output" == *"phase: P3"* ]]
    [[ "$output" == *"attempt: 2"* ]]
    [[ "$output" == *"test reason"* ]]
}