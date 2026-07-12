#!/usr/bin/env bats
# tests/unit/check-gate.bats — 41 用例覆盖 check-gate.sh

load ../helpers/load.bash

# ========== P0 (立项阶段，无需脚本 gate) ==========

@test "G0 check-gate.sh P0 立项阶段 期望 exit 2（输出不含『未知』）" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P0 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"未知"* ]]
}

# ========== P1 (固定 exit 2) ==========

@test "G1 check-gate.sh P1 期望 exit 2（主 Agent 判定）" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P2 多方案探索（5 用例） ==========

@test "G2.1 check-gate.sh P2 0 个候选方案 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
## 设计
无候选方案。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"需至少 2 个候选方案"* ]]
}

@test "G2.2 check-gate.sh P2 1 个候选方案 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
}

@test "G2.3 check-gate.sh P2 2 个候选方案 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.4 check-gate.sh P2 h4 候选方案不识别（regex 边界）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
#### 候选方案 A：方案一
#### 候选方案 B：方案二
EOF
    # h4 不被 ^###? 匹配
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
}

@test "G2.5 check-gate.sh P2 无 P2 文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)  # P2 不在
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2-design.md"* ]]
}

@test "G2.8 check-gate.sh P2 候选方案 ≥2 但无权衡 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"权衡"* ]]
}

@test "G2.9 check-gate.sh P2 候选方案 ≥2 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
方案 A 更简单但性能差，方案 B 复杂但性能好。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.9a check-gate.sh P2 design_trivial + 1 候选方案 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" "design_trivial" "true"
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
## 权衡
简单修改，无需多方案。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.9b check-gate.sh P2 follows_existing_pattern + 1 候选方案 + 含权衡 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    add_p1_field "$dir" "follows_existing_pattern" "[src/foo.py]"
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：照搬已有模式
## 权衡
照搬 src/foo.py 模式。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.10 check-gate.sh P2 有候选方案+权衡+四字段，P2-review.md 无 status:approved 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
---
status: rejected
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"status: approved"* ]]
}

@test "G2.11 check-gate.sh P2 有候选方案+权衡+四字段+status:approved 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
---
status: approved
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.12 check-gate.sh P2-design.md 缺字段（<4）期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺字段"* ]]
}

@test "G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P3 check-tdd-red.sh 委托（7 个子用例） ==========
# G3.1-G3.7 见 check-tdd-red.bats（独立文件覆盖）
# 这里只验证 check-gate.sh P3 委托给了 check-tdd-red.sh

@test "G3 check-gate.sh P3 委托 check-tdd-red.sh（不直接执行测试）" {
    # 通过设置 TEST_RUNNER 验证委托关系
    local dir
    dir=$(create_task_dir)
    local fake_pytest="$BATS_TEST_TMPDIR/fake-pytest"
    cat > "$fake_pytest" <<'EOF'
#!/bin/bash
echo "5 passed"
exit 0
EOF
    chmod +x "$fake_pytest"
    TEST_RUNNER="$fake_pytest" run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    # check-tdd-red.sh 输出 "tests pass, no red-light" → exit 2
    [ "$status" -eq 2 ]
}

# ========== P4 (4 用例) ==========

@test "G4.1 check-gate.sh P4 暂存区仅 .md 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "doc" > "$repo/task/P4-implementation.md"
    git -C "$repo" add "task/P4-implementation.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
}

@test "G4.2 check-gate.sh P4 暂存区有 .py 代码 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "def hello(): pass" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

@test "G4.3 check-gate.sh P4 暂存区 .md + .yaml + .py 混合 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "doc" > "$repo/task/P4-implementation.md"
    echo "code" > "$repo/src.py"
    echo "yaml: 1" > "$repo/config.yaml"
    git -C "$repo" add .
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

@test "G4.4 check-gate.sh P4 暂存区 .py 排除 .md 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    # .py 不在排除列表
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 0 ]
}

# ========== P5 (固定 exit 2) ==========

@test "G5 check-gate.sh P5 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P6 (5 用例) ==========

@test "G6.1 check-gate.sh P6 含 FAIL 行 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1
- FAIL AC2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAIL="* ]]
}

@test "G6.2 check-gate.sh P6 含 NEED_CONFIRM 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1
- [NEED_CONFIRM] AC2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
}

@test "G6.3 check-gate.sh P6 全 PASS 但无 BDD 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
无 BDD 条目
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"TOTAL=0"* ]]
}

@test "G6.4 check-gate.sh P6 全 PASS 但无证据目录 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1
- PASS AC2
EOF
    # 没有 P6-evidence/ 目录
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-evidence"* ]]
}

@test "G6.5 check-gate.sh P6 全 PASS + 证据目录非空 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1
- PASS AC2
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.log"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 2 ]
}

# ========== P7 (5 用例) ==========

@test "G7.1 check-gate.sh P7 含 [BLOCKER] 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER] arch flaw
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BLOCKER="* ]]
}

@test "G7.2 check-gate.sh P7 含 [DEVIATION-CRITICAL] 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DEVIATION-CRITICAL] ui break
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"DEVIATION-CRITICAL="* ]]
}

@test "G7.3 check-gate.sh P7 DESIGN_GAP 未配对 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"DESIGN_GAP"*"未配对"* ]]
}

@test "G7.4 check-gate.sh P7 DESIGN_GAP 已配对 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.5 check-gate.sh P7 2 GAP + 1 REVIEWED 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: A]
- [DESIGN_GAP: B]
- [DESIGN_GAP_REVIEWED: A 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
}

@test "G7.6 check-gate.sh P7 空文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    : > "$dir/P7-consistency.md"  # 空
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.7 check-gate.sh P7 P4 有 DESIGN_GAP 但 P7 未转抄 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-implementation.md" <<'EOF'
---
agent: test
---
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    cat > "$dir/P7-consistency.md" <<'EOF'
---
agent: test
---
一致性检查完成。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4"*"DESIGN_GAP"*"P7"* ]]
}

# ========== P8 (5 用例) ==========

@test "G8.1 check-gate.sh P8 缺 bump_type 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
无 bump_type
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"bump_type"* ]]
}

@test "G8.2 check-gate.sh P8 无 version 文件变更（暂存区）期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    # 不改 version 文件
    echo "doc" > "$repo/some.md"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add some.md CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"version"* ]]
}

@test "G8.3 check-gate.sh P8 有 version 但 CHANGELOG 无变更 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    # CHANGELOG 没改
    git -C "$repo" add package.json
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"CHANGELOG"* ]]
}

@test "G8.4 check-gate.sh P8 全合规 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
}

@test "G8.5 check-gate.sh P8 无 P8 文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P3 P4 P5 P6 P7)  # P8 不在
    # P8-release.md 不存在 → bump_type 缺失 → exit 1
    run bash "$AGATE_SCRIPTS/check-gate.sh" P8 "$dir"
    [ "$status" -eq 1 ]
}

# ========== 默认 case ==========

@test "D-drift-1: dispatch-prompt.md 含'返回前自检'" {
    grep -q '返回前自检' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "D-drift-2: dispatch-prompt.md 含'files_modified'" {
    grep -q 'files_modified' "$AGATE_ROOT/assets/templates/dispatch-prompt.md"
}

@test "G-drift-1: dispatch-protocol.md 含'自查≠gate'关键词" {
    grep -q '自查≠gate' "$AGATE_ROOT/dispatch-protocol.md"
}

@test "G-drift-2: implementer.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/implementer.md"
}

@test "G-drift-3: verifier.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/verifier.md"
}

@test "G_OTHER check-gate.sh 未知阶段 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P9 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"未知阶段"* ]]
}

@test "G2.14 check-gate.sh P2 方案 A（有空格）+ 方案 B 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 A
### 方案 B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.15 check-gate.sh P2 方案一 + 方案二 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案一
### 方案二
## 权衡
方案一简单，方案二稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.16 check-gate.sh P2 候选方案 ≥2 + 含'取舍' 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 取舍
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.17 check-gate.sh P2 候选方案 ≥2 + '选择'标题+正文'理由' 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
### 选择：方案 A
**理由**：A 更简单。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.18 check-gate.sh P2-review agent=subagent + status:approved → exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: subagent
---
status: approved
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.19 check-gate.sh P2-review agent=main + status:approved → exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: main
---
status: approved
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"agent=main"* ]]
}

@test "G2.20 check-gate.sh P2-review 缺 agent 字段 + status:approved → exit 2 (WARNING)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
status: approved
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"agent"* ]]
}

@test "G7.8 check-gate.sh P7 [BLOCKER]: 0 条（声明）期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER]: 0 条
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "G7.9 check-gate.sh P7 [BLOCKER]: 0 条 + 实际 BLOCKER 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [BLOCKER]: 0 条
- [BLOCKER] arch flaw
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BLOCKER="* ]]
}

# ========== 额外边界（凑到 33 个用例） ==========

@test "G2.6 check-gate.sh P2 方案 A/B/C 多种命名（regex [ABC123]）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案A
### 方案B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.7 check-gate.sh P2 h2 (##) 候选方案也被识别" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
## 候选方案 A
## 候选方案 B
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G6.6 check-gate.sh P6 FAIL=0 但 NEED_CONFIRM>0 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1
- [NEED_CONFIRM] AC2
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"NEED_CONFIRM="* ]]
}

@test "G8.6 check-gate.sh P8 CHANGELOG_FILE 环境变量覆盖" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    # 用非默认 changelog 文件
    echo "## [Unreleased]" > "$repo/HISTORY.md"
    git -C "$repo" add package.json HISTORY.md
     CHANGELOG_FILE="HISTORY.md" run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
}

@test "G2.21 check-gate.sh P2 方案 Alpha（多词方案名）期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 Alpha
### 方案 Beta
## 权衡
Alpha 简单，Beta 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.22 check-gate.sh P2 Alternative A + Option B 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### Alternative A
### Option B
## 权衡
Alternative A is simpler, Option B is more robust.
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.23 check-gate.sh P2 方案 Recommended（多词方案名）期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案 Recommended
### 方案 Conservative
## 权衡
Recommended 更激进，Conservative 更保守。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}
