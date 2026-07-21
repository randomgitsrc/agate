#!/usr/bin/env bats
# tests/unit/agate-inject-card.bats — agate-inject-card.sh 注入校验

load ../helpers/load.bash

setup() {
    INJECT_CMD="$AGATE_SCRIPTS/agate-inject-card.sh"
}

# ========== 基本功能 ==========

@test "注入后 dispatch-context 内 AGATE_CARD 块 sha256 与卡片原文一致" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task"
    mkdir -p "$task_dir"

    # 造一个带 AGATE_CARD 占位块的 dispatch-context 文件
    cat > "$task_dir/P1-dispatch-context-analyst.md" <<'EOF'
---
phase: P1
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: analyst
---

<dispatch_guide>
### 目标
分析需求
</dispatch_guide>

<!-- AGATE_CARD_START -->
{占位}
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：test
</objective_info>
EOF

    run bash "$INJECT_CMD" P1 "$task_dir"
    [ "$status" -eq 0 ]

    # 提取注入后的内容（去掉 AGATE_CARD 包装标记）
    local injected_body
    injected_body=$(sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p' \
        "$task_dir/P1-dispatch-context-analyst.md" \
        | sed '1d;$d')

    # 与 agate-next-card.sh P1 全文对比（含 header，因为 inject 注入全文）
    local expected_body
    expected_body=$(bash "$AGATE_SCRIPTS/agate-next-card.sh" P1)

    local expected_hash injected_hash
    expected_hash=$(printf '%s' "$expected_body" | sha256sum | awk '{print $1}')
    injected_hash=$(printf '%s' "$injected_body" | sha256sum | awk '{print $1}')
    [ "$expected_hash" = "$injected_hash" ]
}

@test "注入后其他内容保持不变（只替换 AGATE_CARD 块）" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task"
    mkdir -p "$task_dir"

    cat > "$task_dir/P3-dispatch-context-test-designer.md" <<'EOF'
---
phase: P3
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: test-designer
---

<dispatch_guide>
### 目标
写测试用例

### 约束
基于 P2 的接口契约
</dispatch_guide>

<!-- AGATE_CARD_START -->
{占位}
<!-- AGATE_CARD_END -->

<objective_info>
- 关键标识：test
</objective_info>
EOF

    local before_guide before_info
    before_guide=$(sed -n '1,/<!-- AGATE_CARD_START -->/p' \
        "$task_dir/P3-dispatch-context-test-designer.md" | head -n -1)
    before_info=$(sed -n '/<!-- AGATE_CARD_END -->/,$p' \
        "$task_dir/P3-dispatch-context-test-designer.md" | tail -n +2)

    run bash "$INJECT_CMD" P3 "$task_dir"
    [ "$status" -eq 0 ]

    local after_guide after_info
    after_guide=$(sed -n '1,/<!-- AGATE_CARD_START -->/p' \
        "$task_dir/P3-dispatch-context-test-designer.md" | head -n -1)
    after_info=$(sed -n '/<!-- AGATE_CARD_END -->/,$p' \
        "$task_dir/P3-dispatch-context-test-designer.md" | tail -n +2)

    [ "$before_guide" = "$after_guide" ]
    [ "$before_info" = "$after_info" ]
}

# ========== 多角色文件 ==========

@test "P1 下多个 dispatch-context-{role}.md 全部注入" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task"
    mkdir -p "$task_dir"

    cat > "$task_dir/P1-dispatch-context-analyst.md" <<'EOF'
<!-- AGATE_CARD_START -->
旧
<!-- AGATE_CARD_END -->
EOF
    cat > "$task_dir/P1-dispatch-context-review.md" <<'EOF'
<!-- AGATE_CARD_START -->
旧
<!-- AGATE_CARD_END -->
EOF

    run bash "$INJECT_CMD" P1 "$task_dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P1-dispatch-context-analyst.md"* ]]
    [[ "$output" == *"P1-dispatch-context-review.md"* ]]

    # 两者都不含"旧"
    run grep -c '旧' "$task_dir/P1-dispatch-context-analyst.md" || true
    [ "$output" = "0" ]
    run grep -c '旧' "$task_dir/P1-dispatch-context-review.md" || true
    [ "$output" = "0" ]
}

# ========== 失败路径 ==========

@test "TASK_DIR 不存在 dispatch-context 时 exit 1" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task_empty"
    mkdir -p "$task_dir"

    run bash "$INJECT_CMD" P1 "$task_dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"不存在"* ]]
}

@test "无参数时 exit 1" {
    run bash "$INJECT_CMD"
    [ "$status" -eq 1 ]
}

@test "缺 TASK_DIR 时 exit 1" {
    run bash "$INJECT_CMD" P1
    [ "$status" -eq 1 ]
}

# ========== transitory 兼容：旧格式 dispatch-context（无 -{role}） ==========

@test "过渡期兼容：旧格式 P{N}-dispatch-context.md 也可注入" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task"
    mkdir -p "$task_dir"

    cat > "$task_dir/P1-dispatch-context.md" <<'EOF'
<!-- AGATE_CARD_START -->
旧
<!-- AGATE_CARD_END -->
EOF

    run bash "$INJECT_CMD" P1 "$task_dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"AGATE_CARD 已注入"* ]]

    run grep -c '旧' "$task_dir/P1-dispatch-context.md" || true
    [ "$output" = "0" ]
}
