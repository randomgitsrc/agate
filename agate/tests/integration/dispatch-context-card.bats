#!/usr/bin/env bats
# tests/integration/dispatch-context-card.bats — hash 校验 + 防漂移端到端
# 验证 pre-commit-gate.sh 2p 节（dispatch-context.md 卡片 hash 校验）

load ../helpers/load.bash
load ../helpers/git-helper.bash

setup() {
    REPO=$(git_init)
    HOOK_PATH="$REPO/.git/hooks/pre-commit"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$HOOK_PATH"
    chmod +x "$HOOK_PATH"
    cd "$REPO"
}

_create_dispatch_context() {
    local phase="$1" out_file="$2"
    cat > "$out_file" << 'DCTPL'
---
phase: PHASE_PLACEHOLDER
generated_by: agate-next-card.sh
task_id: T999
---

## 任务上下文
- task_id: T999
- P0-brief 路径: docs/tasks/T999/P0-brief.md

## 当前阶段卡片（强制注入）

<!-- AGATE_CARD_START -->
DCTPL
    bash "$AGATE_SCRIPTS/agate-next-card.sh" "$phase" 2>/dev/null >> "$out_file"
    cat >> "$out_file" << 'DCTPL'
<!-- AGATE_CARD_END -->

## 其他派发上下文
DCTPL
    sed -i "s/PHASE_PLACEHOLDER/${phase}/" "$out_file"
}

_setup_task_with_state() {
    local dir="$1" phase="$2"
    mkdir -p "$dir"
    echo "test" > "$dir/test.py"
    cat > "$dir/.state.yaml" << 'SYS'
task_id: T999
phase: PHASE_PLACEHOLDER
status: in_progress
retries: {}
SYS
    sed -i "s/PHASE_PLACEHOLDER/${phase}/" "$dir/.state.yaml"
}

@test "DC.1 dispatch-context.md 含正确卡片 hash → commit 不因 hash mismatch 被拦" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    _create_dispatch_context "P3" "$dir/P3-dispatch-context.md"
    git add "$dir"
    run git commit -m "test: valid card hash"
    # 可能被 check-tdd-red 拦截（无 pytest），但只要不是 card hash mismatch 就行
    [[ "$output" != *"hash mismatch"* ]]
}

@test "DC.2 dispatch-context.md 卡片被篡改 → hash mismatch" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    _create_dispatch_context "P3" "$dir/P3-dispatch-context.md"
    # 篡改：在卡片块末尾加一行额外内容
    sed -i '/<!-- AGATE_CARD_END -->/i _TAMPERED_' "$dir/P3-dispatch-context.md"
    git add "$dir"
    run git commit -m "test: tampered card"
    [ "$status" -ne 0 ]
    [[ "$output" == *"hash mismatch"* ]]
}

@test "DC.3 dispatch-context.md 空卡片块 → hash mismatch（CLI输出非空但嵌入为空）" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    cat > "$dir/P3-dispatch-context.md" << 'DCTPL'
---
phase: P3
generated_by: agate-next-card.sh
---

<!-- AGATE_CARD_START -->
<!-- AGATE_CARD_END -->
DCTPL
    git add "$dir"
    run git commit -m "test: empty card block"
    [ "$status" -ne 0 ]
    [[ "$output" == *"hash mismatch"* ]]
}