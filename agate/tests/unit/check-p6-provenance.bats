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
- PASS AC1 (ghost.png)
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
- PASS AC1 (screenshots/login.png) (vision: vision.yaml)
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
- PASS AC1 (a.png) (b.png)
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
- PASS AC1 (a.png) (b.png)
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
- PASS AC1 (shared.json)
- PASS AC2 (shared.json)
- PASS AC3 (shared.json)
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
- PASS AC1 (e1.json)
- PASS AC2 (e2.json)
- PASS AC3 (e3.json)
- PASS AC4 (e4.json)
- PASS AC5 (e5.json)
- PASS AC6 (e6.json)
- PASS AC7 (e7.json)
- PASS AC8 (e8.json)
- PASS AC9 (e1.json)
- PASS AC10 (e2.json)
- PASS AC11 (e3.json)
- PASS AC12 (e4.json)
- PASS AC13 (e5.json)
- PASS AC14 (e6.json)
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
- PASS AC1 (r1.json)
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
- PASS AC1 (result.json)
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
    cat > "$dir/P6-dispatch-context.md" <<'EOF'
- PASS AC1 pre-judged
EOF
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-dispatch-context"* ]]
}

@test "PV.9 check-p6-provenance.sh P1 BDD Given 数 > P6 总数 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    # 3 个 Given 但 P6 只 1 条 PASS
    cat >> "$dir/P1-requirements.md" <<'EOF'

- Given a
- Given b
- Given c
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"挑验"* ]]
}

@test "PV.10 check-p6-provenance.sh P1 无 Given 格式 期望 exit 2" {
    local dir
    dir=$(create_task_dir)
    # 去掉默认的 Given 行
    sed -i '/^- Given /d' "$dir/P1-requirements.md"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"BDD 格式非标准"* ]]
}

@test "PV.11 check-p6-provenance.sh UI + 截图 PASS 缺 vision 引用 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS AC1 (screenshots/login.png)
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
- PASS AC1 (screenshots/login.png) (vision: vision/missing.yaml)
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
- PASS AC1 (screenshots/login.png) (vision: vision.yaml)
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
- PASS AC1 (result.json)
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
- PASS AC1 (result.json)
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
- PASS AC1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}
