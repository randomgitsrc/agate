#!/usr/bin/env bats
# tests/unit/check-p6-evidence.bats — 11 用例覆盖 check-p6-evidence.sh
# 计划：5.3 / 实际 11 行 / 与附录 A 一致

load ../helpers/load.bash

@test "E.1 check-p6-evidence.sh P6 文件不存在 期望 exit 2" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 2 ]
}

@test "E.2 check-p6-evidence.sh P6 无 BDD 条目 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
无 BDD
EOF
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"无 BDD 条目"* ]]
}

@test "E.3 check-p6-evidence.sh PASS 缺文件引用 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
EOF
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺文件证据引用"* ]]
}

@test "E.4 check-p6-evidence.sh PASS 有引用且文件存在（基本格式）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    # check-p6-evidence.sh 只验证括号存在 + 文件存在 + 目录非空
    # 文件存在性由 check-p6-provenance.sh 验证
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "E.5 check-p6-evidence.sh 证据目录不存在 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    # 不创建 P6-evidence/
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P6-evidence"* ]]
}

@test "E.6 check-p6-evidence.sh 证据目录完全空（无文件）期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    mkdir -p "$dir/P6-evidence"
    # 不放任何文件（包括 .gitkeep）
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
}

@test "E.7 check-p6-evidence.sh 正常通过（无 UI）期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result1.json)
- PASS BDD-2 (result2.json)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result1.json"
    echo "log" > "$dir/P6-evidence/result2.json"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "E.8 check-p6-evidence.sh UI 任务 + 截图目录空 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"  # 让 P6-evidence 目录"非空"
    # 不创建 screenshots/ 子目录
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"screenshots"* ]]
}

@test "E.9 check-p6-evidence.sh UI 任务 + 截图 ≤ 1KB 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    # 创建 100 字节的"假 png"
    head -c 100 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"1KB"* ]]
}

@test "E.10 check-p6-evidence.sh UI 任务 + 截图 ≥ 1KB 通过 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "E.11 check-p6-evidence.sh 多种文件后缀（.log .json .html .txt .yaml）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.log)
- PASS BDD-2 (data.json)
- PASS BDD-3 (page.html)
- PASS BDD-4 (notes.txt)
- PASS BDD-5 (config.yaml)
EOF
    mkdir -p "$dir/P6-evidence"
    for ext in log json html txt yaml; do
        echo "content" > "$dir/P6-evidence/file.$ext"
    done
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "E.12 check-p6-evidence.sh UI 任务 + 重复截图（md5 相同）期望 exit 1 (阻断)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
- PASS BDD-2 (screenshots/dashboard.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    local content
    content=$(head -c 5000 /dev/urandom | base64)
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/login.png"
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/dashboard.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"md5"* || "$output" == *"重复"* ]]
}

@test "E.14 check-p6-evidence.sh PASS 引用带附加内容 (path.png, vision: OK) 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.png, vision: OK)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.1 check-p6-evidence.sh PASS 引用 .pdf 文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (report.pdf)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "pdf content" > "$dir/P6-evidence/report.pdf"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.2 check-p6-evidence.sh PASS 引用 .jpeg 文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (photo.jpeg)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "jpeg content" > "$dir/P6-evidence/photo.jpeg"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.3 check-p6-evidence.sh PASS 引用逗号分隔的 2 个证据文件 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (screenshots/a.png, screenshots/b.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    echo "a" > "$dir/P6-evidence/screenshots/a.png"
    echo "b" > "$dir/P6-evidence/screenshots/b.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.4 check-p6-evidence.sh PASS 含 nth(1) 嵌套括号 + 单一证据路径 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (screenshots/b07.png — element: .katex nth(1))
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    echo "img" > "$dir/P6-evidence/screenshots/b07.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.5 check-p6-evidence.sh PASS 括号内容是纯版本号 (v2.0) 期望 exit 0（evidence 层放行）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: upgraded (v2.0)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "some evidence" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "EVID_EXT.6 check-p6-evidence.sh PASS 括号内容是纯描述文字无路径结构 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1: works (no reference here)
EOF
    mkdir -p "$dir/P6-evidence"
    echo "some evidence" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺文件证据引用"* ]]
}

@test "EVID_EXT.7 check-p6-evidence.sh 现有 png/jpg/log/json/html/txt/yaml/yml 用例保持 exit 0（回归）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
- PASS BDD-1 (result.png)
- PASS BDD-2 (photo.jpg)
- PASS BDD-3 (output.log)
- PASS BDD-4 (data.json)
- PASS BDD-5 (page.html)
- PASS BDD-6 (notes.txt)
- PASS BDD-7 (config.yaml)
- PASS BDD-8 (config2.yml)
EOF
    mkdir -p "$dir/P6-evidence"
    for f in result.png photo.jpg output.log data.json page.html notes.txt config.yaml config2.yml; do
        echo "content" > "$dir/P6-evidence/$f"
    done
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "E.13 check-p6-evidence.sh UI 任务 + 不同截图（md5 不同）期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login.png)
- PASS BDD-2 (screenshots/dashboard.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/login.png"
    head -c 5000 /dev/urandom > "$dir/P6-evidence/screenshots/dashboard.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 0 ]
}

# ========== 错误消息详情（P2.32）==========

@test "EVIDENCE_NO_REF_DETAIL.1 PASS 缺引用时错误消息含具体 PASS 行" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1
- PASS BDD-2 (result.json)
- PASS BDD-3
EOF
    mkdir -p "$dir/P6-evidence"
    echo "log" > "$dir/P6-evidence/result.json"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"  -"*"PASS BDD-1"* ]]
    [[ "$output" == *"  -"*"PASS BDD-3"* ]]
}

@test "EVIDENCE_EMPTY_DETAIL.1 小文件错误消息含具体 basename" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/tiny.txt)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    head -c 100 /dev/urandom > "$dir/P6-evidence/screenshots/tiny.txt"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"  -"*"tiny.txt"* ]]
}

@test "EVIDENCE_MD5_DETAIL.1 md5 重复错误消息含具体 basename" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/a.png)
- PASS BDD-2 (screenshots/b.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    local content
    content=$(head -c 5000 /dev/urandom | base64)
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/a.png"
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/b.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"  -"*"a.png"* ]]
    [[ "$output" == *"  -"*"b.png"* ]]
}

@test "EVIDENCE_MD5_DETAIL.2 md5 重复文件名含空格时错误消息含完整 basename" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
ui_affected: true
EOF
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (screenshots/login page.png)
- PASS BDD-2 (screenshots/dashboard view.png)
EOF
    mkdir -p "$dir/P6-evidence/screenshots"
    local content
    content=$(head -c 5000 /dev/urandom | base64)
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/login page.png"
    printf '%s' "$content" > "$dir/P6-evidence/screenshots/dashboard view.png"
    run bash "$AGATE_SCRIPTS/check-p6-evidence.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"  -"*"login page.png"* ]]
    [[ "$output" == *"  -"*"dashboard view.png"* ]]
}
