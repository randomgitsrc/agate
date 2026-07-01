#!/usr/bin/env bats
# tests/unit/check-retrospective.bats — 4 用例覆盖 check-retrospective.sh
# 计划：5.9 / 实际 4 行 / 与附录 A 一致
# 注意：此脚本总是 exit 0，测试只能断言 output 含特定模式

load ../helpers/load.bash

@test "RT.1 check-retrospective.sh 无异常 期望 exit 0 + 无输出" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    # 无异常时输出为空
    [ -z "$output" ]
}

@test "RT.2 check-retrospective.sh retries 超限 期望 exit 0 + 含'重试超限'" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries:
  P2:
    - attempt: 1
    - attempt: 2
    - attempt: 3
EOF
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"重试超限"* ]]
}

@test "RT.3 check-retrospective.sh SCOPE+ 触发 期望 exit 0 + 含'SCOPE+'" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
[SCOPE+] 新增功能
EOF
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"SCOPE+"* ]]
}

@test "RT.4 check-retrospective.sh override 触发 期望 exit 0 + 含'override'" {
    local dir
    dir=$(create_task_dir)
    sed -i '/^phases:/a override: P2 retained' "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"override"* ]]
}

@test "RT.5 check-retrospective.sh retries[P3]=2 触发超限（P3 MAX=2）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: PAUSED
status: active
retries:
  P3:
    - attempt: 1
    - attempt: 2
EOF
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" == *"重试超限"* ]]
}

@test "RT.6 check-retrospective.sh retries[P3]=1 不触发（P3 MAX=2 未达）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P4
status: active
retries:
  P3:
    - attempt: 1
EOF
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" "$dir/.state.yaml"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
