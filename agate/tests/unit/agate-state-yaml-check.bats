#!/usr/bin/env bats
# tests/unit/agate-state-yaml-check.bats — state-yaml 校验专用工具
load ../helpers/load.bash

@test "SY.1 合法 .state.yaml → 无输出" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "SY.2 缺必填字段 → 缺必填字段: xxx" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    echo "task_id: T1" > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"缺必填字段"* ]]
}

@test "SY.3 phase 非法值 → phase 非法值" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: ZZZ
status: active
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' python3 '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"phase 非法值"* ]]
}