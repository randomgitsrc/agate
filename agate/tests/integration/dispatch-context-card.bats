#!/usr/bin/env bats
# tests/integration/dispatch-context-card.bats — hash 校验 + 防漂移端到端
# 验证 pre-commit-gate.sh 2p 节（dispatch-context 卡片 hash 校验，glob 匹配新格式）

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
    local phase="$1" role="$2" out_file="$3"
    cat > "$out_file" << 'DCTPL'
---
phase: PHASE_PLACEHOLDER
generated_by: agate-next-card.sh + 主 Agent
task_id: T999
role: ROLE_PLACEHOLDER
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
测试目标描述

### 约束
测试约束

### 上游关联
上游摘要信息

### 输入文件
- docs/tasks/T999/P0-brief.md
- docs/tasks/T999/前阶段产出.md
</dispatch_guide>

<!-- AGATE_CARD_START -->
DCTPL
    bash "$AGATE_SCRIPTS/agate-next-card.sh" "$phase" 2>/dev/null >> "$out_file"
    cat >> "$out_file" << 'DCTPL'
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：正常
- 关键标识：无
</objective_info>
DCTPL
    sed -i "s/PHASE_PLACEHOLDER/${phase}/" "$out_file"
    sed -i "s/ROLE_PLACEHOLDER/${role}/" "$out_file"
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

@test "DC.1 dispatch-context-{role}.md 含正确卡片 hash → commit 不因 hash mismatch 被拦" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    _create_dispatch_context "P3" "test-designer" "$dir/P3-dispatch-context-test-designer.md"
    git add "$dir"
    run git commit -m "test: valid card hash"
    [[ "$output" != *"hash mismatch"* ]]
}

@test "DC.2 dispatch-context-{role}.md 卡片被篡改 → hash mismatch" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    _create_dispatch_context "P3" "test-designer" "$dir/P3-dispatch-context-test-designer.md"
    sed -i '/<!-- AGATE_CARD_END -->/i _TAMPERED_' "$dir/P3-dispatch-context-test-designer.md"
    git add "$dir"
    run git commit -m "test: tampered card"
    [ "$status" -ne 0 ]
    [[ "$output" == *"hash mismatch"* ]]
}

@test "DC.3 dispatch-context-{role}.md 空卡片块 → hash mismatch" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P3"
    cat > "$dir/P3-dispatch-context-test-designer.md" << 'DCTPL'
---
phase: P3
generated_by: agate-next-card.sh + 主 Agent
task_id: T999
role: test-designer
---

<dispatch_guide>
### 目标
测试

### 约束
无

### 上游关联
无

### 输入文件
- docs/tasks/T999/P0-brief.md
</dispatch_guide>

<!-- AGATE_CARD_START -->
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：正常
</objective_info>
DCTPL
    git add "$dir"
    run git commit -m "test: empty card block"
    [ "$status" -ne 0 ]
    [[ "$output" == *"hash mismatch"* ]]
}

@test "DC.4 派发阶段 (P2) 产出 commit 缺 dispatch-context → exit 1" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P2"
    echo "# P2 design" > "$dir/P2-design.md"
    git add "$dir"
    run git commit -m "test: missing dispatch-context in P2"
    [ "$status" -ne 0 ]
    [[ "$output" == *"dispatch-context"* ]]
}

@test "DC.5 P5 产出 commit 缺 dispatch-context → 拦截" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P5"
    mkdir -p "$dir/P5-test-results"
    echo "results" > "$dir/P5-test-results/unit.md"
    git add "$dir"
    run git commit -m "test: no dispatch-context in P5"
    [ "$status" -ne 0 ]
    [[ "$output" == *"dispatch-context"* ]]
}

@test "DC.6 P7 产出 commit 缺 dispatch-context → 拦截" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P7"
    echo "# P7 consistency" > "$dir/P7-consistency.md"
    git add "$dir"
    run git commit -m "test: no dispatch-context in P7"
    [ "$status" -ne 0 ]
    [[ "$output" == *"dispatch-context"* ]]
}

@test "DC.7 P8 产出 commit 缺 dispatch-context → 拦截" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P8"
    echo "# P8 release" > "$dir/P8-release.md"
    git add "$dir"
    run git commit -m "test: no dispatch-context in P8"
    [ "$status" -ne 0 ]
    [[ "$output" == *"dispatch-context"* ]]
}

@test "DC.multi 同一阶段多个 dispatch-context 文件 → 逐个校验 hash" {
    local dir="$REPO/task"
    _setup_task_with_state "$dir" "P1"
    _create_dispatch_context "P1" "analyst" "$dir/P1-dispatch-context-analyst.md"
    _create_dispatch_context "P1" "requirements-review" "$dir/P1-dispatch-context-requirements-review.md"
    git add "$dir"
    run git commit -m "test: multiple dispatch-context files"
    [[ "$output" != *"hash mismatch"* ]]
}
