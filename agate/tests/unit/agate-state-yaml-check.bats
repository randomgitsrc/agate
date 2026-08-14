#!/usr/bin/env bats
# tests/unit/agate-state-yaml-check.bats — state-yaml 校验专用工具
# T001 v2.0 流 D（P2-design.md §3.4.1）：task_id 正则硬切 ^T\d+$ → ^T[A-Z]{2}\d+$。
# 3 个既有用例改写为 BDD-25/26 覆盖（@test 数保持 3 不变，P2-review FIND"需补
# TAG0001/T001 双向用例"已在 SY.1 内以两段 run 落实，SY.2/SY.3 覆盖其余必填/枚举校验回归）。
load ../helpers/load.bash

@test "SY.1 BDD-25/26: 新格式 TAG0001 校验通过；旧格式 T001 硬切拒绝（不兼容双格式）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")

    # BDD-25：新编号格式 TAG0001（项目代号 AG + 动态编号 0001）→ 通过，无输出
    cat > "$dir/.state.yaml" <<'EOF'
task_id: TAG0001
phase: P3
status: active
retries: {}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]

    # BDD-26：旧编号格式 T001 → 硬切拒绝，提示合法格式 ^T[A-Z]{2}\d+$
    cat > "$dir/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"task_id 格式错误"* ]]
}

@test "SY.2 缺必填字段 → 缺必填字段: xxx（回归，与流 D 编号规则无关）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    echo "task_id: TAG0001" > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"缺必填字段"* ]]
}

@test "SY.3 phase 非法值 → phase 非法值（新格式 task_id 下回归，不受流 D 硬切影响）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/sy-XXXXXX")
    cat > "$dir/.state.yaml" <<'EOF'
task_id: TAG0001
phase: ZZZ
status: active
EOF
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-yaml-check.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"phase 非法值"* ]]
}