#!/usr/bin/env bats
# tests/unit/check-p6-provenance.bats — 15 用例覆盖 check-p6-provenance.sh
# 计划：5.4 / 实际 15 行 / 与附录 A 一致

load ../helpers/load.bash

@test "PV.1 check-p6-provenance.sh 无 P6 文件 期望 exit 0" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.2 check-p6-provenance.sh PASS 引用不存在的文件 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (ghost.png)
EOF
    mkdir -p "$dir/P6-evidence"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"证据文件不存在"* ]]
}

@test "PV.3 check-p6-provenance.sh (vision: ...) 引用被剥离不当文件路径" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    # vision YAML 在 task 根目录（不是 P6-evidence/ 里）
    cat > "$dir/vision.yaml" <<'EOF'
vision_analysis:
  summary:
    blocker_count: 0
EOF
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png) (vision: vision.yaml)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    # vision 引用被剥离 → 只看 screenshots/login.png（存在）
    # vision YAML 在 TASK_DIR/vision.yaml → blocker_count=0 → exit 0
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.4 check-p6-provenance.sh 行末多个括号取最后一个（a.png 不存在但 b.png 存在）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (a.png) (b.png)
EOF
    mkdir -p "$dir/P6-evidence"
    head -c 1000 /dev/urandom > "$dir/P6-evidence/b.png"
    # 最后一个括号 = b.png（存在）
    # a.png 不存在但取的是 b.png → audit 1a 通过
    # evidence 目录只有 b.png → audit 1c 通过
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.4b check-p6-provenance.sh 行末多括号 + 全部不存在 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (a.png) (b.png)
EOF
    mkdir -p "$dir/P6-evidence"
    # 都不存在
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
}

@test "PV.5 check-p6-provenance.sh 3 PASS 引用 1 共享证据文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (shared.json)
- PASS BDD-2 (shared.json)
- PASS BDD-3 (shared.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/shared.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.5b check-p6-provenance.sh 14 PASS 引用 8 共享证据文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (e1.json)
- PASS BDD-2 (e2.json)
- PASS BDD-3 (e3.json)
- PASS BDD-4 (e4.json)
- PASS BDD-5 (e5.json)
- PASS BDD-6 (e6.json)
- PASS BDD-7 (e7.json)
- PASS BDD-8 (e8.json)
- PASS BDD-9 (e1.json)
- PASS BDD-10 (e2.json)
- PASS BDD-11 (e3.json)
- PASS BDD-12 (e4.json)
- PASS BDD-13 (e5.json)
- PASS BDD-14 (e6.json)
EOF
    mkdir -p "$dir/P6-evidence"
    for i in 1 2 3 4 5 6 7 8; do
        echo "log" > "$dir/P6-evidence/e${i}.json"
    done
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.6 check-p6-provenance.sh 证据文件未被引用（充数文件）期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (r1.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/r1.json"
    echo "filler" > "$dir/P6-evidence/extra.json"  # 充数文件
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未被"* ]]
}

@test "PV.7 check-p6-provenance.sh .gitkeep 算隐藏文件不计入证据（exit 0）" {
    local dir
    dir=$(create_task_dir)
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    : > "$dir/P6-evidence/.gitkeep"
    echo "log" > "$dir/P6-evidence/result.json"
    # .gitkeep 隐藏文件被 find 排除 → EVIDENCE_COUNT=1（只 result.json）
    # PASS 数也是 1 → 不会触发"empty"检查
    # .gitkeep 是隐藏文件，find 跳过它，所以 audit 1c 不会报
    # 实际跑应该是 exit 0
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.8 check-p6-provenance.sh dispatch-context 含 PASS 预判 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-dispatch-context-subtask.md" <<'EOF'
- PASS BDD-1 pre-judged
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-dispatch-context"* ]]
}

@test "PV.9 check-p6-provenance.sh P1 BDD 标题数 > P6 总数 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    # create_task_dir 默认给 1 条 BDD-1，再加一条 BDD-2，但 P6 只 1 条 PASS
    add_p1_bdd "$dir" "second scenario"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"挑验"* ]]
}

@test "PV.10 check-p6-provenance.sh P1 无标准 BDD 标题 期望 exit 1（无过渡期兜底）" {
    local dir
    dir=$(create_task_dir)
    # 去掉默认的 #### BDD-N: 标题行
    sed -i '/^#### BDD-/d' "$dir/P1-requirements.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未使用标准"* ]]
}

@test "PV_BDD_COUNT.1 P1 含 3 条 #### BDD-NN，P6 有 3 条 PASS 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    add_p1_bdd "$dir" "second"
    add_p1_bdd "$dir" "third"
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (a.json)
- PASS BDD-2 (b.json)
- PASS BDD-3 (c.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo x > "$dir/P6-evidence/a.json"
    echo x > "$dir/P6-evidence/b.json"
    echo x > "$dir/P6-evidence/c.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV_BDD_COUNT.4 P1 含 1 条带 Examples 表的 BDD-NN，P6 有 1 条 PASS 期望 exit 0（数据驱动共享编号）" {
    local dir
    dir=$(create_task_dir)
    cat >> "$dir/P1-requirements.md" <<'EOF'

| existing | result |
|----------|--------|
| 0        | 201    |
| 5        | 400    |
EOF
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo x > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV_BDD_COUNT.5 P1 BDD 编号有间隔（BDD-1,BDD-3，无 BDD-2），P6 有 2 条 PASS 期望 exit 0（按标题计数非 max 编号）" {
    local dir
    dir=$(create_task_dir)
    cat >> "$dir/P1-requirements.md" <<'EOF'

#### BDD-3: third (skipped BDD-2 numbering on purpose)
- Given x
- When y
- Then z
EOF
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (a.json)
- PASS BDD-3 (b.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo x > "$dir/P6-evidence/a.json"
    echo x > "$dir/P6-evidence/b.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}


@test "PV.11 check-p6-provenance.sh UI + 截图 PASS 缺 vision 引用 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    # 缺 vision 引用
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺 vision"* ]]
}

@test "PV.12 check-p6-provenance.sh vision YAML 文件不存在 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png) (vision: vision/missing.yaml)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    # vision YAML 不存在（路径是 vision/missing.yaml，不创建）
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"vision YAML 引用的文件不存在"* ]]
}

@test "PV.13 check-p6-provenance.sh vision YAML blocker_count != 0 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
ui_affected: true
EOF
    # vision YAML 在 task 根目录
    cat > "$dir/vision.yaml" <<'EOF'
vision_analysis:
  summary:
    blocker_count: 1
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png) (vision: vision.yaml)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"blocker_count="* ]]
}

@test "PV.14 check-p6-provenance.sh P6 缺 agent 字段 期望 exit 2（WARNING）" {
    local dir
    dir=$(create_task_dir)
    # 去掉 P6 的 agent frontmatter
    sed -i '/^---$/d; /^agent: test$/d' "$dir/P6-acceptance.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    # exit 2 是 WARNING（不阻塞）
    [ "$status" -eq 2 ]
}

@test "PV.15 check-p6-provenance.sh risk=high + P2-review agent=main 期望 exit 0（agent=main 检查已移至 check-gate.sh）" {
    local dir
    dir=$(create_task_dir --risk-level high)
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: main
---
review done
EOF
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.16 check-p6-provenance.sh P2-review agent=subagent + status:approved → exit 0" {
    local dir
    dir=$(create_task_dir --risk-level high)
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: subagent
---
status: approved
EOF
    cat >> "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.17 dispatch-context 含任务上下文节 → 审计 2 放行" {
    local dir
    dir=$(create_task_dir --risk-level high)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: verified (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    cat > "$dir/P6-dispatch-context-subtask.md" <<'EOF'
## 客观信息（主 Agent 已查证）
- 环境状态：debug server 运行中

## 任务上下文（主 Agent 从 P0-brief + gate + 摘要积累）
- 目标：逐条 BDD 验收
- 关注点：P2 声明 ui_affected: true
- 上游关键决策：architect 选择了方案 B
- 上游结构化字段：
  - packages: [pkg-a]
  - ui_affected: true
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.18 check-p6-provenance.sh PASS 行含嵌套括号描述如 nth(1) → 提取 screenshots/ 路径（exit 0）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (screenshots/b07.png — element: .katex nth(1))
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/b07.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.19 check-p6-provenance.sh PASS 行含嵌套括号 + vision 引用 → 提取 screenshots/ 路径（exit 0）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/vision.yaml" <<'EOF'
vision_analysis:
  summary:
    blocker_count: 0
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (screenshots/b07.png — element: .katex nth(1)) (vision: vision.yaml)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/b07.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.20 check-p6-provenance.sh PASS 行含嵌套括号且路径不存在 → exit 1 + 含具体路径" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (screenshots/missing.png — element: .katex nth(1))
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    # 不创建 missing.png
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"证据文件不存在"* ]]
    [[ "$output" == *"screenshots/missing.png"* ]]
}

# ========== 审计 5: EXIT_CODE 一致性检测 (M1.3b) ==========

@test "PV.21 审计5: 日志 EXIT_CODE=1 但 P6 声明 PASS → exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (logs/test.log)
EOF
    mkdir -p "$dir/P6-evidence/logs"
    cat > "$dir/P6-evidence/logs/test.log" <<'EOF'
=== Test Results ===
total: 3, passed: 2, failed: 1
EXIT_CODE: 1
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"EXIT_CODE"* ]] || [[ "$output" == *"矛盾"* ]]
}

@test "PV.22 审计5: 日志 EXIT_CODE=0 配 PASS → exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (logs/test.log)
EOF
    mkdir -p "$dir/P6-evidence/logs"
    cat > "$dir/P6-evidence/logs/test.log" <<'EOF'
=== Test Results ===
total: 3, passed: 3, failed: 0
EXIT_CODE: 0
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.23 审计5: 日志缺少 EXIT_CODE 尾行 → WARNING 不阻断" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (logs/test.log)
EOF
    mkdir -p "$dir/P6-evidence/logs"
    cat > "$dir/P6-evidence/logs/test.log" <<'EOF'
=== Test Results ===
total: 3, passed: 3, failed: 0
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"EXIT_CODE"* || "$output" == *"跳过"* ]]
}

# ========== PROV_MULTI: 多文件引用解析 (v2 plan Part 1) ==========

@test "PROV_MULTI.1 PASS 行引用 2 个逗号分隔的证据文件，均存在 → exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (screenshots/file1.png, screenshots/file2.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/file1.png"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/file2.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PROV_MULTI.2 PASS 行引用 2 个逗号分隔的证据文件，其中 1 个不存在 → exit 1 + 报告缺失" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (screenshots/file1.png, screenshots/file2.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/file1.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"证据文件不存在"* ]]
    [[ "$output" == *"screenshots/file2.png"* ]]
}

@test "PROV_MULTI.3 PASS 行含 nth(1) 嵌套括号 + 行末单一证据路径 → exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (screenshots/b07.png — element: .katex nth(1))
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/b07.png"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PROV_MULTI.4 PASS 行引用单一证据文件（原有场景回归）→ exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}
