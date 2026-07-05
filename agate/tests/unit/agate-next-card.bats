#!/usr/bin/env bats
# tests/unit/agate-next-card.bats — 12 用例覆盖 agate-next-card.sh

load ../helpers/load.bash

setup() {
    CARD_CMD="$AGATE_SCRIPTS/agate-next-card.sh"
}

# ========== 成功路径：每个 phase 返回对应卡片 ==========

@test "CLI P0 输出含 orchestrator 卡片标题" {
    run bash "$CARD_CMD" P0
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P0"* ]]
    [[ "$output" == *"任务启动"* ]]
}

@test "CLI P1 输出 requirements 卡片" {
    run bash "$CARD_CMD" P1
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P1"* ]]
    [[ "$output" == *"需求基线"* ]]
}

@test "CLI P2 输出 design 卡片（含候选方案 ≥2 规则）" {
    run bash "$CARD_CMD" P2
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P2"* ]]
    [[ "$output" == *"候选方案"* ]]
}

@test "CLI P3 输出 tdd 卡片" {
    run bash "$CARD_CMD" P3
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P3"* ]]
    [[ "$output" == *"TDD"* ]]
}

@test "CLI P4 输出 implementation 卡片（含 files_to_read 导航）" {
    run bash "$CARD_CMD" P4
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P4"* ]]
    [[ "$output" == *"files_to_read"* ]]
}

@test "CLI P5 输出 verification 卡片" {
    run bash "$CARD_CMD" P5
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P5"* ]]
    [[ "$output" == *"gate_commands"* ]]
}

@test "CLI P6 输出 acceptance 卡片（含 vision-helper 绑定）" {
    run bash "$CARD_CMD" P6
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P6"* ]]
    [[ "$output" == *"vision"* ]]
}

@test "CLI P7 输出 consistency 卡片" {
    run bash "$CARD_CMD" P7
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P7"* ]]
    [[ "$output" == *"DESIGN_GAP"* ]]
}

@test "CLI P8 输出 release 卡片" {
    run bash "$CARD_CMD" P8
    [ "$status" -eq 0 ]
    [[ "$output" == *"# P8"* ]]
    [[ "$output" == *"bump_type"* ]]
}

# ========== 输出格式 ==========

@test "CLI 输出含固定头部（hook 用 sha256 校验的格式契约）" {
    run bash "$CARD_CMD" P3
    [ "$status" -eq 0 ]
    [[ "$output" == *"## 当前阶段卡片：P3"* ]]
    [[ "$output" == *"路径："* ]]
    [[ "$output" == *"---"* ]]
}

# ========== 失败路径 ==========

@test "CLI 无参数 期望 exit 1" {
    run bash "$CARD_CMD"
    [ "$status" -eq 1 ]
    [[ "$output" == *"需要 1 个参数"* ]]
}

@test "CLI phase=P9（不在 P0-P8）期望 exit 2" {
    run bash "$CARD_CMD" P9
    [ "$status" -eq 2 ]
    [[ "$output" == *"不在 P0-P8 范围内"* ]]
}