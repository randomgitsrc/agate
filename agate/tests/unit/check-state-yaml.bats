#!/usr/bin/env bats
# tests/unit/check-state-yaml.bats — 9 用例覆盖 check-state-yaml.sh
# 计划：5.6 / 实际 9 行 / 与附录 A 一致

load ../helpers/load.bash

@test "SY.1 check-state-yaml.sh 无 .state.yaml 期望 exit 2" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    rm -f "$f"
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 2 ]
}

@test "SY.2 check-state-yaml.sh 空文件 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    : > "$f"
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
}

@test "SY.3 check-state-yaml.sh 缺 task_id 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
phase: P1
status: active
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺必填字段: task_id"* ]]
}

@test "SY.4 check-state-yaml.sh task_id 格式错 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
task_id: T001a
phase: P1
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"task_id 格式错误"* ]]
}

@test "SY.5 check-state-yaml.sh phase 非法值 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
task_id: T001
phase: P9
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"phase 非法值"* ]]
}

@test "SY.6 check-state-yaml.sh retries 非 dict 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
task_id: T001
phase: P1
retries: 3
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"retries 应为 dict"* ]]
}

@test "SY.7 check-state-yaml.sh retries[P1] 非 list 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
task_id: T001
phase: P1
retries:
  P1: 3
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"retries[P1] 应为列表"* ]]
}

@test "SY.8 check-state-yaml.sh 全合规 期望 exit 0" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    cat > "$f" <<'EOF'
task_id: T001
phase: P1
status: active
retries:
  P2:
    - attempt: 1
      reason: "fail"
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 0 ]
}

@test "SY.9 check-state-yaml.sh YAML 语法错 期望 exit 1" {
    local f
    f=$(mktemp "$BATS_TEST_TMPDIR/state-XXXXXX.yaml")
    # 缩进错乱的非法 YAML
    cat > "$f" <<'EOF'
task_id: T001
  phase: P1: extra
EOF
    run bash "$AGATE_SCRIPTS/check-state-yaml.sh" "$f"
    [ "$status" -eq 1 ]
    [[ "$output" == *"YAML 解析错误"* ]]
}
