#!/usr/bin/env bats

load ../helpers/load.bash

setup() {
    TEST_TASK_DIR="$(mktemp -d "${BATS_TEST_TMPDIR}/task-XXXXXX")"
}

teardown() {
    rm -rf "$TEST_TASK_DIR" 2>/dev/null || true
}

@test "RP.1: rejects missing arguments" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh"
    [ "$status" -eq 1 ]
}

@test "RP.2: rejects invalid phase" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P9 architect "$TEST_TASK_DIR"
    [ "$status" -eq 2 ]
}

@test "RP.3: rejects nonexistent task dir" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 architect "/nonexistent"
    [ "$status" -eq 2 ]
}

@test "RP.4: placeholder replacement for phase/role/task_id" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 architect "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P2 阶段的 architect 子 Agent"* ]]
    [[ "$output" != *"阶段 阶段"* ]]
    [[ "$output" == *"$(basename "$TEST_TASK_DIR")"* ]]
    [[ "$output" == *"P2-dispatch-context-architect.md"* ]]
    [[ "$output" != *"P{N}"* ]]
    [[ "$output" != *"{role}"* ]]
}

@test "RP.5: P2 selects P2 appendix (minimal validation)" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 architect "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P2 最小验证"* ]]
    [[ "$output" != *"上下文控制"* ]]
    [[ "$output" != *"回退诊断"* ]]
}

@test "RP.6: P4 without --rollback selects P4 normal appendix" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P4 implementer "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"上下文控制"* ]]
    [[ "$output" != *"回退诊断"* ]]
}

@test "RP.7: P4 with --rollback selects P4 rollback appendix" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P4 implementer "$TEST_TASK_DIR" --rollback
    [ "$status" -eq 0 ]
    [[ "$output" == *"回退诊断"* ]]
    [[ "$output" != *"上下文控制"* ]]
}

@test "RP.8: P5/P6 share same appendix (screenshot quality)" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P5 verifier "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"截图质量标准"* ]]
    [[ "$output" != *"上下文控制"* ]]
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P6 verifier "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"截图质量标准"* ]]
}

@test "RP.9: P8 selects P8 appendix (READY check)" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P8 implementer "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"READY 收尾检查"* ]]
    [[ "$output" != *"上下文控制"* ]]
}

@test "RP.10: role with special characters produces safe filename" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 "design-review" "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [ -f "$TEST_TASK_DIR/P2-dispatch-prompt-design-review.md" ]
}

@test "RP.11: output file contains render-product header" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 architect "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    run cat "$TEST_TASK_DIR/P2-dispatch-prompt-architect.md"
    [[ "$output" == *"渲染产物"* ]]
    [[ "$output" == *"不是协议模板"* ]]
}

@test "RP.12: --rollback ignored for non-P4 phases" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 architect "$TEST_TASK_DIR" --rollback
    [ "$status" -eq 0 ]
    [[ "$output" == *"P2 最小验证"* ]]
    [[ "$output" != *"回退诊断"* ]]
}

@test "RP.13: no residual placeholders except whitelisted" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P4 implementer "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    local residual
    residual="$(printf '%s' "$output" | grep -oE '\{[a-zA-Z0-9_|： -]+\}' \
        | grep -v '{上一阶段文件名}' \
        | grep -v '{project_conventions_file}' \
        | grep -v '{problems|design|review|test-cases|implementation|test-results|acceptance|consistency|release}' \
        || true)"
    [ -z "$residual" ]
}

@test "RP.14: {agate_root} replaced with actual path" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P4 implementer "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" != *"{agate_root}"* ]]
    [[ "$output" == *"assets/execution-roles/implementer.md"* ]]
}

@test "RP.15: review-roles detected for review role" {
    run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 design-review "$TEST_TASK_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"assets/review-roles/design-review.md"* ]]
}

@test "RP.16: P3 renders P3 self-check appendix" {
    local output
    output=$(AGATE_ROOT="$AGATE_ROOT" bash "$AGATE_SCRIPTS/agate-render-dispatch-prompt.sh" P3 test-designer "$TEST_TASK_DIR")
    [[ "$output" == *"P3 自检"* ]]
}
