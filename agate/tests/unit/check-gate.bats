#!/usr/bin/env bats
# tests/unit/check-gate.bats — 33 用例覆盖 check-gate.sh
# 计划：5.2 / 实际 33 行 / 与附录 A 一致

load ../helpers/load.bash

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

@test "G2.5 check-gate.sh P2 无 P2 文件（design_trivial 裁剪）期望 exit 2" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)  # P2 不在
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

@test "G_OTHER check-gate.sh 未知阶段 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P9 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"未知阶段"* ]]
}

# ========== 额外边界（凑到 33 个用例） ==========

@test "G2.6 check-gate.sh P2 方案 A/B/C 多种命名（regex [ABC123]）" {
    local dir
    dir=$(create_task_dir)
    # regex 是 ^###?\s*方案[ABC123]（无空格），所以"方案A""方案B"可识别
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案A
### 方案B
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
EOF
    # ^###? 匹配 ## 和 ###
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
