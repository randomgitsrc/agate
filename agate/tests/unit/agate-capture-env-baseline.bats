#!/usr/bin/env bats
# tests/unit/agate-capture-env-baseline.bats — EB.1-EB.15

load ../helpers/load.bash

make_fake_runner() {
    local output="$1"
    local exit_code="$2"
    local f="$BATS_TEST_TMPDIR/fake-runner-$BATS_TEST_NUMBER-$RANDOM"
    cat > "$f" <<EOF
#!/bin/bash
cat <<'OUT'
$output
OUT
exit $exit_code
EOF
    chmod +x "$f"
    echo "$f"
}

make_recording_runner() {
    local output="$1"
    local exit_code="$2"
    local sentinel="$3"
    local f="$BATS_TEST_TMPDIR/rec-runner-$BATS_TEST_NUMBER-$RANDOM"
    cat > "$f" <<EOF
#!/bin/bash
touch "$sentinel"
cat <<'OUT'
$output
OUT
exit $exit_code
EOF
    chmod +x "$f"
    echo "$f"
}

setup_git_repo_with_p2() {
    local repo="$1"
    local p2_content="$2"
    git_init "$repo"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    printf '%s' "$p2_content" > "$repo/agate-workspace/tasks/T001/P2-design.md"
    git_commit "$repo" "init" "agate-workspace/tasks/T001/P2-design.md"
}

@test "EB.1 任务级已有 pre-task-baseline.md → no-op，exit 0" {
    local dir
    dir=$(create_task_dir)
    echo "existing baseline" > "$dir/pre-task-baseline.md"
    run "$PYTHON" "$AGATE_SCRIPTS/agate-capture-env-baseline.py" "$dir"
    [ "$status" -eq 0 ]
    [[ "$output" != *"ENV_BASELINE"* ]]
    [[ "$(cat "$dir/pre-task-baseline.md")" == "existing baseline" ]]
}

@test "EB.2 P2-design.md 不存在 → exit 0 + WARNING" {
    local dir
    dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8)
    run "$PYTHON" "$AGATE_SCRIPTS/agate-capture-env-baseline.py" "$dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P2-design.md 不存在"* ]]
    [ ! -f "$dir/pre-task-baseline.md" ]
}

@test "EB.3 gate_commands.P5 未声明 → exit 0 + WARNING" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/agate-capture-env-baseline.py" "$dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"未在 P2-design.md 找到 gate_commands.P5"* ]]
    [ ! -f "$dir/pre-task-baseline.md" ]
}

@test "EB.4 首次捕获，仓库无缓存 → 真实跑测试命令，写入缓存+任务文件" {
    local repo="$BATS_TEST_TMPDIR/eb4-repo"
    local fake
    fake=$(make_fake_runner "3 failed, 5 passed
FAILED tests/test_a.py::test_x
FAILED tests/test_b.py::test_y
FAILED tests/test_c.py::test_z" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    [ -f "$repo/agate-workspace/tasks/T001/pre-task-baseline.md" ]
    local cache_dir="$repo/docs/.agate-env-baseline-cache"
    [ -d "$cache_dir" ]
    local cache_count
    cache_count=$(ls "$cache_dir"/*.md 2>/dev/null | wc -l | tr -d ' ')
    [ "$cache_count" -eq 1 ]
    grep -q 'captured_at_commit:' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
    grep -q 'tests/test_a.py::test_x' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
}

@test "EB.5 缓存命中（同 commit + 同命令集合）→ 不重跑测试命令，直接复制缓存" {
    local repo="$BATS_TEST_TMPDIR/eb5-repo"
    local sentinel="$BATS_TEST_TMPDIR/eb5-ran-$BATS_TEST_NUMBER"
    local fake
    fake=$(make_recording_runner "2 failed, 5 passed
FAILED tests/test_a.py::test_x
FAILED tests/test_b.py::test_y" 1 "$sentinel")
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [ -f "$sentinel" ]
    rm -f "$sentinel"
    mkdir -p "$repo/agate-workspace/tasks/T002"
    cp "$repo/agate-workspace/tasks/T001/P2-design.md" "$repo/agate-workspace/tasks/T002/P2-design.md"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T002"
    [ "$status" -eq 0 ]
    [[ "$output" == *"复用缓存"* ]]
    [ ! -f "$sentinel" ]
    [ -f "$repo/agate-workspace/tasks/T002/pre-task-baseline.md" ]
}

@test "EB.6 缓存未命中（commit 变了）→ 重新真实跑测试命令" {
    local repo="$BATS_TEST_TMPDIR/eb6-repo"
    local fake
    fake=$(make_fake_runner "1 failed, 5 passed
FAILED tests/test_a.py::test_x" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    echo "new commit" > "$repo/newfile.txt"
    git_commit "$repo" "second commit" "newfile.txt"
    mkdir -p "$repo/agate-workspace/tasks/T002"
    cp "$repo/agate-workspace/tasks/T001/P2-design.md" "$repo/agate-workspace/tasks/T002/P2-design.md"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T002"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    [ -f "$repo/agate-workspace/tasks/T002/pre-task-baseline.md" ]
}

@test "EB.7 同一 commit 但 gate_commands.P5 命令集合不同 → 视为未命中" {
    local repo="$BATS_TEST_TMPDIR/eb7-repo"
    local fake1 fake2
    fake1=$(make_fake_runner "1 failed, 5 passed
FAILED tests/test_a.py::test_x" 1)
    fake2=$(make_fake_runner "2 failed, 3 passed
FAILED tests/test_d.py::test_w
FAILED tests/test_e.py::test_v" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake1
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    mkdir -p "$repo/agate-workspace/tasks/T002"
    printf 'gate_commands:\n  P5: %s\n  P5_formatter: pytest.sh' "$fake2" > "$repo/agate-workspace/tasks/T002/P2-design.md"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T002"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    grep -q 'test_d.py::test_w' "$repo/agate-workspace/tasks/T002/pre-task-baseline.md"
}

@test "EB.8 声明命令本身崩溃 → 不写任何文件，stderr 有 WARNING，exit 0" {
    local repo="$BATS_TEST_TMPDIR/eb8-repo"
    local fake
    fake=$(make_fake_runner "some error output" 127)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"本身崩溃"* ]]
    [ ! -f "$repo/agate-workspace/tasks/T001/pre-task-baseline.md" ]
}

@test "EB.9 汇总计数与明细提取数不一致 → 不写任何文件，exit 0" {
    local repo="$BATS_TEST_TMPDIR/eb9-repo"
    local fake
    fake=$(make_fake_runner "3 failed, 5 passed
FAILED tests/test_a.py::test_x" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"不一致"* ]]
    [ ! -f "$repo/agate-workspace/tasks/T001/pre-task-baseline.md" ]
}

@test "EB.10 gate_commands.P5 声明 2 条命令，各自有失败 → 合并去重" {
    local repo="$BATS_TEST_TMPDIR/eb10-repo"
    local fake1 fake2
    fake1=$(make_fake_runner "2 failed, 5 passed
FAILED tests/test_a.py::test_x
FAILED tests/test_b.py::test_y" 1)
    fake2=$(make_fake_runner "2 failed, 3 passed
FAILED tests/test_b.py::test_y
FAILED tests/test_c.py::test_z" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake1
  P5_formatter: pytest.sh
  P5_e2e: $fake2
  P5_e2e_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    local baseline
    baseline=$(cat "$repo/agate-workspace/tasks/T001/pre-task-baseline.md")
    [[ "$baseline" == *"test_a.py::test_x"* ]]
    [[ "$baseline" == *"test_b.py::test_y"* ]]
    [[ "$baseline" == *"test_c.py::test_z"* ]]
    local fail_count
    fail_count=$(echo "$baseline" | grep -c '^tests/' || echo 0)
    [ "$fail_count" -eq 3 ]
}

@test "EB.11 非 git 仓库 → exit 0 + WARNING" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
gate_commands:
  P5: "pytest -q"
  P5_formatter: "pytest.sh"
EOF
    run env GIT_DIR=/nonexistent/.git "$PYTHON" "$AGATE_SCRIPTS/agate-capture-env-baseline.py" "$dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"非 git 仓库"* ]]
    [ ! -f "$dir/pre-task-baseline.md" ]
}

@test "EB.12 缓存文件存在但内容损坏（非合法 frontmatter）→ P5 diff 优雅降级" {
    local repo="$BATS_TEST_TMPDIR/eb12-repo"
    local fake
    fake=$(make_fake_runner "1 failed, 5 passed
FAILED tests/test_a.py::test_x" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    local cache_dir="$repo/docs/.agate-env-baseline-cache"
    local cache_file
    cache_file=$(ls "$cache_dir"/*.md | head -1)
    echo "corrupted content without frontmatter" > "$cache_file"
    rm -f "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"复用缓存"* ]]
    local baseline
    baseline=$(cat "$repo/agate-workspace/tasks/T001/pre-task-baseline.md")
    [[ "$baseline" == *"corrupted content"* ]]
}

@test "EB.13 P5 + P5_formatter: pytest.sh → fail-list 从 JSON 提取" {
    local repo="$BATS_TEST_TMPDIR/eb13-repo"
    local fake
    fake=$(make_fake_runner "2 failed, 3 passed
FAILED tests/test_alpha.py::test_one
FAILED tests/test_beta.py::test_two" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: pytest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    [[ "$output" == *"失败数=2"* ]]
    grep -q 'tests/test_alpha.py::test_one' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
    grep -q 'tests/test_beta.py::test_two' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
}

@test "EB.14 P5 无 formatter → WARNING，不写文件" {
    local repo="$BATS_TEST_TMPDIR/eb14-repo"
    local fake
    fake=$(make_fake_runner "2 failed, 5 passed
FAILED tests/test_a.py::test_x
FAILED tests/test_b.py::test_y" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"无 formatter"* ]]
    [ ! -f "$repo/agate-workspace/tasks/T001/pre-task-baseline.md" ]
}

@test "EB.15 vitest P5 + P5_formatter: vitest.sh → fail-list 提取" {
    local repo="$BATS_TEST_TMPDIR/eb15-repo"
    local fake
    fake=$(make_fake_runner "Tests  2 failed | 4 passed
FAIL tests/b.test.ts
FAIL tests/c.test.ts" 1)
    setup_git_repo_with_p2 "$repo" "gate_commands:
  P5: $fake
  P5_formatter: vitest.sh"
    run bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/agate-capture-env-baseline.py' agate-workspace/tasks/T001"
    [ "$status" -eq 0 ]
    [[ "$output" == *"已捕获"* ]]
    [[ "$output" == *"失败数=2"* ]]
    grep -q 'tests/b.test.ts' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
    grep -q 'tests/c.test.ts' "$repo/agate-workspace/tasks/T001/pre-task-baseline.md"
}
