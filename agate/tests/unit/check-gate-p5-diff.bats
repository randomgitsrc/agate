#!/usr/bin/env bats
# tests/unit/check-gate-p5-diff.bats — PG.1-PG.9 P5 机械 diff 回归判定

load ../helpers/load.bash

make_baseline() {
    local dir="$1"
    local commit="$2"
    shift 2
    local fails=("$@")
    {
        echo "---"
        echo "captured_at_commit: $commit"
        echo "generated_by: agate-capture-env-baseline.sh"
        echo "---"
        echo "# 任务前环境基线"
        echo ""
        echo "失败数：${#fails[@]}"
        echo ""
        echo '```fail-list'
        for f in "${fails[@]}"; do
            [ -n "$f" ] && echo "$f"
        done
        echo '```'
    } > "$dir/pre-task-baseline.md"
}

make_post_fails() {
    local dir="$1"
    shift
    local fails=("$@")
    mkdir -p "$dir/P5-test-results"
    {
        for f in "${fails[@]}"; do
            [ -n "$f" ] && echo "$f"
        done
    } > "$dir/P5-test-results/fail-list.txt"
}

@test "PG.1 两份文件均缺失 → 走原有分支，exit 2" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.2 无新增失败、无预存失败 → exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123"
    make_post_fails "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.3 有新增失败（post 独有）→ exit 1，输出列出具体新增失败 id" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    make_post_fails "$dir" "tests/test_a.py::test_x" "tests/test_b.py::test_y"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"新增失败"* ]]
    [[ "$output" == *"test_b.py::test_y"* ]]
}

@test "PG.4 有预存失败（pre/post 都有）、已有 known-failures.md → exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    make_post_fails "$dir" "tests/test_a.py::test_x"
    echo "---" > "$dir/known-failures.md"
    echo "agent: test" >> "$dir/known-failures.md"
    echo "---" >> "$dir/known-failures.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.5 有预存失败、known-failures.md 不存在 → exit 1" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    make_post_fails "$dir" "tests/test_a.py::test_x"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"known-failures.md 不存在"* ]]
}

@test "PG.6 预存失败已在本任务修复（pre 有、post 无）→ exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x" "tests/test_b.py::test_y"
    make_post_fails "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.7 pre-task-baseline.md 的 fail-list 为空（0 个预存失败），post 有失败 → 全部视为新增，exit 1" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123"
    make_post_fails "$dir" "tests/test_a.py::test_x" "tests/test_b.py::test_y"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"新增失败"* ]]
}

@test "PG.8 fail-list.txt 为空文件（0 个 post 失败），pre 有失败 → 全部视为预存已修复，exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    make_post_fails "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.9 known-failures.md 存在但为空（只有 frontmatter）→ exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    make_post_fails "$dir" "tests/test_a.py::test_x"
    cat > "$dir/known-failures.md" <<'EOF'
---
agent: test
---
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.10 pre-task-baseline.md 缺少 captured_at_commit: → 视为损坏，exit 2" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/pre-task-baseline.md" <<'EOF'
---
generated_by: something
---
# Corrupted baseline
```fail-list
tests/test_a.py::test_x
```
EOF
    make_post_fails "$dir" "tests/test_b.py::test_y"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"captured_at_commit"* ]]
    [[ "$output" == *"损坏"* ]]
}

@test "PG.11 只有 pre-task-baseline.md 没有 fail-list.txt → 走原有分支，exit 2" {
    local dir
    dir=$(create_task_dir)
    make_baseline "$dir" "abc123" "tests/test_a.py::test_x"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}

@test "PG.12 只有 fail-list.txt 没有 pre-task-baseline.md → 走原有分支，exit 2" {
    local dir
    dir=$(create_task_dir)
    make_post_fails "$dir" "tests/test_a.py::test_x"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"
    [ "$status" -eq 2 ]
}
