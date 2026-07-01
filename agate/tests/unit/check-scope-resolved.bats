#!/usr/bin/env bats
# tests/unit/check-scope-resolved.bats — 6 用例覆盖 check-scope-resolved.sh
# 计划：5.5 / 实际 6 行 / 与附录 A 一致

load ../helpers/load.bash

@test "SC.1 check-scope-resolved.sh 不存在的 task 目录 期望 exit 2" {
    local dir="/tmp/nonexistent-task-$$-$(date +%s%N)"
    # 不创建该目录
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 2 ]
}

@test "SC.2 check-scope-resolved.sh 无 SCOPE+ 触发 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
正常文档，无 SCOPE+ 标记
EOF
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "SC.3 check-scope-resolved.sh 有 SCOPE+ 但无 P1 文件 期望 exit 1" {
    local dir
    dir=$(mktemp -d /tmp/task-XXXXXX)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
[SCOPE+] 新增功能
EOF
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"无 P1-requirements.md"* ]]
    rm -rf "$dir"
}

@test "SC.4 check-scope-resolved.sh 有 SCOPE+ 但 P1 无 SCOPE_RESOLVED 期望 exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
[SCOPE+] 新增功能
EOF
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"SCOPE_RESOLVED"* ]]
}

@test "SC.5 check-scope-resolved.sh 有 SCOPE+ + P1 有 [SCOPE_RESOLVED] 期望 exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
[SCOPE+] 新增功能
EOF
    echo "" >> "$dir/P1-requirements.md"
    echo "[SCOPE_RESOLVED] 已纳入 v0.7" >> "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "SC.5b check-scope-resolved.sh [SCOPE_RESOLVED: 带说明] 格式也接受" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
[SCOPE+] 新增功能
EOF
    echo "" >> "$dir/P1-requirements.md"
    echo "[SCOPE_RESOLVED: 已纳入 v0.7]" >> "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 0 ]
}
