#!/usr/bin/env bats
# tests/integration/consistency.bats — 7 用例覆盖 check-protocol-consistency.py
load ../helpers/load.bash

setup() {
    CONSISTENCY_OUTPUT=$(python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py" 2>&1) || true
}

@test "CON.1 CHECK 1: YAML 代码块可解析" {
    [[ "$CONSISTENCY_OUTPUT" != *"ERROR ("* ]]
}

@test "CON.2 CHECK 2: 文件引用存在" {
    [[ "$CONSISTENCY_OUTPUT" != *"FAIL  CHECK 2"* ]]
}

@test "CON.3 CHECK 3: 无硬编码行号" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 3"* ]]
}

@test "CON.4 CHECK 4: gate_commands 键集合一致" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 4"* ]]
}

@test "CON.5 CHECK 5: 协议文件计数声明正确" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 5"* ]]
}

@test "CON.6 CHECK 6: LICENSE 归属" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 6"* ]]
}

@test "CON.7 CHECK 7: version badge 同步" {
    [[ "$CONSISTENCY_OUTPUT" == *"PASS  CHECK 7"* ]]
}
