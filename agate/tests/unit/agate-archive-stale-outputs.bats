#!/usr/bin/env bats
# tests/unit/agate-archive-stale-outputs.bats — agate-archive-stale-outputs.sh 归档校验

load ../helpers/load.bash

setup() {
    ARCHIVE_CMD="$AGATE_SCRIPTS/agate-archive-stale-outputs.sh"
}

@test "ARCH.1 P6 阶段有 P6-acceptance.md + P6-evidence/，归档 P6" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task1"
    mkdir -p "$task_dir/P6-evidence/screenshots"
    echo "old p6 content" > "$task_dir/P6-acceptance.md"
    touch "$task_dir/P6-evidence/screenshots/a.png"

    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]
    [ ! -f "$task_dir/P6-acceptance.md" ]
    [ ! -d "$task_dir/P6-evidence" ]

    local archived_dir
    archived_dir=$(find "$task_dir/.archived" -maxdepth 1 -type d -name "*-P6")
    [ -n "$archived_dir" ]
    [ -f "$archived_dir/P6-acceptance.md" ]
    [ -f "$archived_dir/P6-evidence/screenshots/a.png" ]
}

@test "ARCH.2 P4 阶段调用归档脚本，无需归档" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task2"
    mkdir -p "$task_dir"

    run bash "$ARCHIVE_CMD" P4 "$task_dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"无需归档"* ]]
    [ ! -d "$task_dir/.archived" ]
}

@test "ARCH.3 P6-evidence/ 不存在，只有 P6-acceptance.md" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task3"
    mkdir -p "$task_dir"
    echo "content" > "$task_dir/P6-acceptance.md"

    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]
    [ ! -f "$task_dir/P6-acceptance.md" ]

    local archived_dir
    archived_dir=$(find "$task_dir/.archived" -maxdepth 1 -type d -name "*-P6")
    [ -f "$archived_dir/P6-acceptance.md" ]
    [ ! -d "$archived_dir/P6-evidence" ]
}

@test "ARCH.4 同一任务对 P6 归档两次，两份历史证据都保留" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task4"
    mkdir -p "$task_dir"
    echo "first attempt" > "$task_dir/P6-acceptance.md"

    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]
    sleep 1

    echo "second attempt" > "$task_dir/P6-acceptance.md"
    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]

    local count
    count=$(find "$task_dir/.archived" -maxdepth 1 -type d -name "*-P6" | wc -l)
    [ "$count" -eq 2 ]
}

@test "ARCH.5 P6-acceptance.md 含 FAIL，breadcrumb 正确摘要且不被归档" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task5"
    mkdir -p "$task_dir"
    cat > "$task_dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1: ok (screenshots/a.png)
- FAIL BDD-7: 购物车金额错误 (screenshots/b.png)
EOF

    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]
    [ -f "$task_dir/.retreat-history.md" ]
    grep -q "FAIL BDD-7" "$task_dir/.retreat-history.md"

    # breadcrumb 本身必须留在当前目录，不能被归档走
    local archived_dir
    archived_dir=$(find "$task_dir/.archived" -maxdepth 1 -type d -name "*-P6")
    [ ! -f "$archived_dir/.retreat-history.md" ]
}

@test "ARCH.6 连续两次归档 P6，breadcrumb 追加而非覆盖" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task6"
    mkdir -p "$task_dir"
    echo "- FAIL BDD-7: 第一次失败 (a.png)" > "$task_dir/P6-acceptance.md"
    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]
    sleep 1
    echo "- FAIL BDD-7: 第二次仍失败 (b.png)" > "$task_dir/P6-acceptance.md"
    run bash "$ARCHIVE_CMD" P6 "$task_dir"
    [ "$status" -eq 0 ]

    grep -q "第一次失败" "$task_dir/.retreat-history.md"
    grep -q "第二次仍失败" "$task_dir/.retreat-history.md"
}

@test "ARCH.7 P1 阶段归档 P1-requirements.md + P1-review.md" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task7"
    mkdir -p "$task_dir"
    echo "req" > "$task_dir/P1-requirements.md"
    echo "review" > "$task_dir/P1-review.md"

    run bash "$ARCHIVE_CMD" P1 "$task_dir"
    [ "$status" -eq 0 ]
    [ ! -f "$task_dir/P1-requirements.md" ]
    [ ! -f "$task_dir/P1-review.md" ]

    local archived_dir
    archived_dir=$(find "$task_dir/.archived" -maxdepth 1 -type d -name "*-P1")
    [ -f "$archived_dir/P1-requirements.md" ]
    [ -f "$archived_dir/P1-review.md" ]
}
