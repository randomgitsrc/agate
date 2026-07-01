#!/usr/bin/env bats
# tests/integration/consistency.bats — 7 用例覆盖 check-protocol-consistency.py
# 计划：7.2 / 实际 7 行 / 与附录 A 一致

load ../helpers/load.bash

@test "CON.1 CHECK 1: 所有 .md 文件的 YAML 代码块可解析" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    # 输出不应有 ERROR
    if [[ "$output" == *"ERROR"* ]]; then
        echo "$output" >&2
    fi
    [[ "$output" != *"ERROR ("* ]]
}

@test "CON.2 CHECK 2: 仓库内文件引用存在" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    # WARN 可接受，FAIL 不可
    [[ "$output" != *"FAIL  CHECK 2"* ]]
}

@test "CON.3 CHECK 3: 协议文件无硬编码行号" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [[ "$output" == *"PASS  CHECK 3"* ]]
}

@test "CON.4 CHECK 4: gate_commands 键集合一致" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [[ "$output" == *"PASS  CHECK 4"* ]]
}

@test "CON.5 CHECK 5: 协议文件计数声明正确" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [[ "$output" == *"PASS  CHECK 5"* ]]
}

@test "CON.6 CHECK 6: LICENSE 与 gstack 归属" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [[ "$output" == *"PASS  CHECK 6"* ]]
}

@test "CON.7 CHECK 7: version badge 与 git tag 同步" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [[ "$output" == *"PASS  CHECK 7"* ]]
}
