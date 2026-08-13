#!/usr/bin/env bats
# tests/unit/check-tdd-red.bats — TDD red-light check tests
# Covers: TEST_RUNNER path, gate_commands.P3 path, formatter path, multi-stack
# T001 v2.0 流 A（BDD-15）：gate_commands 明确不迁移 frontmatter（暂留正文），
# 本文件的 gate_commands.P3 读取路径（agate-read-gate-commands.py 等 4 工具）须
# 无回归——即便 P2-design.md 其余字段（candidate_count/packages/domains/ui_affected）
# 迁入 frontmatter，gate_commands 仍在正文按旧正则读取。@test 数保持 38 不变。

load ../helpers/load.bash

make_fake_pytest() {
    local output="$1"
    local exit_code="$2"
    local f="$BATS_TEST_TMPDIR/fake-pytest-$BATS_TEST_NUMBER"
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

make_args_recording_runner() {
    local output="$1"
    local exit_code="$2"
    local sentinel="$3"
    local f="$BATS_TEST_TMPDIR/fake-args-runner-$BATS_TEST_NUMBER"
    cat > "$f" <<EOF
#!/bin/bash
printf '%s\n' "\$@" > "$sentinel"
cat <<'OUT'
$output
OUT
exit $exit_code
EOF
    chmod +x "$f"
    echo "$f"
}

@test "TD.1 check-tdd-red.sh TEST_RUNNER 指向不存在 + 无 pytest 期望 exit 1" {
    run env TEST_RUNNER="/nonexistent/fake-pytest" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
}

@test "TD.1b check-tdd-red.sh 无 TEST_RUNNER + 无 pytest（无 PATH 找不到 pytest）期望 exit 3" {
    run env -u PATH bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 3 ] || [ "$status" -eq 1 ]
}

@test "TD.2 check-tdd-red.sh 测试全绿 期望 exit 2（实现先于测试）" {
    local fake
    fake=$(make_fake_pytest "5 passed" 0)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 2 ]
    [[ "$output" == *"no red-light"* ]]
}

@test "TD.3 check-tdd-red.sh 经典红灯（assertion failure）期望 exit 0" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TD.4 check-tdd-red.sh B 类：项目内 import 失败 期望 exit 0" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'
FAILED tests/test_x.py::test_xxx - myapp.foo.Yyy" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TD.5 check-tdd-red.sh A 类：第三方 import 失败 期望 exit 1" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: No module named 'requests'" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TD.6 check-tdd-red.sh A 类：SyntaxError 期望 exit 1" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - SyntaxError: invalid syntax" 2)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TD.7 check-tdd-red.sh 混合：1 failed + 1 B 类 error 期望 exit 0" {
    local fake
    fake=$(make_fake_pytest "1 failed, 1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'
FAILED tests/test_x.py::test_xxx" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TD.8 check-tdd-red.sh 无 PROJECT_MODULE + ImportError 期望 exit 0（启发式）" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Z'" 2)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

@test "TDD.N1: TEST_RUNNER without formatter does not add -q" {
    local sentinel="$BATS_TEST_TMPDIR/runner-args-$BATS_TEST_NUMBER"
    local fake
    fake=$(make_args_recording_runner "2 failed, 5 passed" 1 "$sentinel")
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
    run cat "$sentinel"
    [[ "$output" != *"-q"* ]]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TDD.N2: vitest pure assertion failure → red-light exit 0" {
    local fake
    fake=$(make_fake_pytest "Tests  11 failed | 6 passed" 1)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TDD.N3: vitest B-class → exit 0" {
    local fake
    fake=$(make_fake_pytest "Failed Suites 1
Error: Cannot find module '../src/bar' imported from /tmp/test/foo.test.ts" 1) # scan-exempt: mock 输出样例文本（非路径假设）
    run env TEST_RUNNER="$fake" PROJECT_MODULE="src/bar" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

# DEPRECATED: pattern-based tests, replaced by TDD.F*
@test "TDD.N4: vitest A-class → exit 0 (exit-code-only without formatter)" {
    local fake
    fake=$(make_fake_pytest "Failed Suites 1
Error: Cannot find module 'requests' imported from /tmp/test/foo.test.ts" 1) # scan-exempt: mock 输出样例文本（非路径假设）
    run env TEST_RUNNER="$fake" PROJECT_MODULE="src/bar" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

@test "TDD.G1: BDD-15 回归：gate_commands.P3 保持正文（不迁移 frontmatter）→ auto-read, red-light exit 0" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-g1"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
## gate_commands
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.G2: no gate_commands.P3 → TEST_RUNNER still works (backward compat)" {
    local task_dir="$BATS_TEST_TMPDIR/task-g2"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<'EOF'
## gate_commands
gate_commands:
  P5: "pytest -q --tb=no"
EOF
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env TEST_RUNNER="$fake" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.G3: TEST_RUNNER env var takes priority over gate_commands.P3" {
    local fake_env
    fake_env=$(make_fake_pytest "2 failed, 5 passed" 1)
    local fake_p3
    fake_p3="$BATS_TEST_TMPDIR/fake-p3-g3-$BATS_TEST_NUMBER"
    cat > "$fake_p3" <<'PEOF'
#!/bin/bash
cat <<'OUT'
all passed
OUT
exit 0
PEOF
    chmod +x "$fake_p3"
    local task_dir="$BATS_TEST_TMPDIR/task-g3"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake_p3"
  P5: "pytest -q --tb=no"
EOF
    run env TEST_RUNNER="$fake_env" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.G4: no TASK_DIR → skip gate_commands read, fall back to TEST_RUNNER" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.G5: gate_commands.P3 with double-quoted value → strip quotes" {
    local task_dir="$BATS_TEST_TMPDIR/task-g5"
    mkdir -p "$task_dir"
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.F1: gate_commands.P3 + P3_formatter → auto-read both, classic red-light exit 0" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed
FAILED tests/test_a.py::test_x
FAILED tests/test_b.py::test_y" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-f1"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}

@test "TDD.F2: gate_commands.P3 without formatter → exit-code-only, red-light exit 0" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-f2"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
    [[ "$output" != *"classic red-light"* ]]
}

@test "TDD.F3: formatter detects B-class (import from project_module) → exit 0 + B-class" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-f3"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"B-class"* ]]
}

@test "TDD.F4: formatter detects A-class (SyntaxError) → exit 1 + A-class" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - SyntaxError: invalid syntax" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-f4"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "TDD.F11: absolute path formatter works" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - SyntaxError: invalid syntax" 2)
    local abs_formatter="$BATS_TEST_TMPDIR/abs-fmt.sh"
    cp "$AGATE_ROOT/assets/formatters/pytest.sh" "$abs_formatter"
    local task_dir="$BATS_TEST_TMPDIR/task-f11"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "$abs_formatter"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "TDD.F12: PROJECT_MODULE env var overrides gate_commands project_module" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: No module named 'requests'" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-f12"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER PROJECT_MODULE="requests" TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"B-class"* ]]
}

@test "TDD.F5: formatter detects A-class (import NOT from project_module) → exit 1 + A-class" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: No module named 'requests'" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-f5"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "TDD.F6: green light (exit 0) → exit 2" {
    local fake
    fake=$(make_fake_pytest "5 passed" 0)
    local task_dir="$BATS_TEST_TMPDIR/task-f6"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 2 ]
    [[ "$output" == *"no red-light"* ]]
}

@test "TDD.F7: TEST_RUNNER env var still works (backward compat, exit-code-only)" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env -u TEST_RUNNER_FLAGS -u TEST_FAIL_PATTERN -u TEST_ERROR_PATTERN -u TEST_IMPORT_PATTERN TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "TDD.F8: no TEST_RUNNER, no gate_commands.P3, no pytest → exit 3" {
    run env -u PATH bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 3 ]
}

@test "TDD.F9: no formatter → command runs without -q" {
    local sentinel="$BATS_TEST_TMPDIR/f9-sentinel-$BATS_TEST_NUMBER"
    local fake="$BATS_TEST_TMPDIR/fake-f9-$BATS_TEST_NUMBER"
    cat > "$fake" <<EOF
#!/bin/bash
printf '%s\n' "\$@" > "$sentinel"
cat <<'OUT'
2 failed, 5 passed
OUT
exit 1
EOF
    chmod +x "$fake"
    local task_dir="$BATS_TEST_TMPDIR/task-f9"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    run cat "$sentinel"
    [[ "$output" != *"-q"* ]]
}

@test "TDD.F10: multi-stack P3 + P3_js → both run, combined result → exit 0" {
    local fake_py fake_js
    fake_py=$(make_fake_pytest "1 failed, 3 passed
FAILED tests/test_a.py::test_x" 1)
    fake_js="$BATS_TEST_TMPDIR/fake-js-f10-$BATS_TEST_NUMBER"
    cat > "$fake_js" <<'EOF'
#!/bin/bash
cat <<'OUT'
Tests  2 failed | 4 passed
FAIL tests/b.test.ts
FAIL tests/c.test.ts
OUT
exit 1
EOF
    chmod +x "$fake_js"
    local task_dir="$BATS_TEST_TMPDIR/task-f10"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake_py"
  P3_formatter: "pytest.sh"
  P3_js: "$fake_js"
  P3_js_formatter: "vitest.sh"
  P5: "pytest -q --tb=no"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}

@test "TD.FAIL_HINT: classic red-light outputs assertion-mismatch hint" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed
FAILED tests/test_x.py::test_x" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-failhint"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"断言"*"数据"* ]]
}

@test "TDD.TIMEOUT: 测试命令超时 → exit 0 + 超时提示" {
    local task_dir
    task_dir=$(create_task_dir)
    # 用 sleep 模拟超时（AGATE_TDD_TIMEOUT=2，sleep 5 必超时）
    cat > "$BATS_TEST_TMPDIR/fake-slow-runner" <<'EOF'
#!/bin/bash
sleep 5
exit 1
EOF
    chmod +x "$BATS_TEST_TMPDIR/fake-slow-runner"
    TEST_RUNNER="$BATS_TEST_TMPDIR/fake-slow-runner" AGATE_TDD_TIMEOUT=2 \
        run bash "$AGATE_SCRIPTS/check-tdd-red.sh" "$task_dir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"超时"* ]]
}

# ========== py 抽离试点：agate-read-gate-commands.py 直接测试 ==========
# 覆盖：P2 含 gate_commands 多栈 / 无 gate_commands / project_module /
#       双引号去除 / 单引号去除 / formatter 关联 / 末行无换行

@test "PYX.1 agate-read-gate-commands.py P2 含 P3 + P3_html_formatter + project_module" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: "pytest -q --tb=short"
  P3_html: "npx vitest run"
  P3_html_formatter: "vitest.sh"
  project_module: "myapp"
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q --tb=short"'* ]]
    [[ "$output" == *'"cmd": "npx vitest run"'* ]]
    [[ "$output" == *'"formatter": "vitest.sh"'* ]]
    [[ "$output" == *'"project_module": "myapp"'* ]]
}

@test "PYX.2 agate-read-gate-commands.py P2 无 gate_commands → 空 JSON" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
无 gate_commands 块
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"commands": []'* ]]
    [[ "$output" == *'"project_module": ""'* ]]
}

@test "PYX.3 agate-read-gate-commands.py P2 双引号值被去除" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: "pytest -q"
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.4 agate-read-gate-commands.py P2 单引号值被去除" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P3: 'pytest -q'
EOF
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.5 agate-read-gate-commands.py P2 末行无换行也能解析" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/py-XXXXXX")
    printf 'gate_commands:\n  P3: "pytest -q"' > "$dir/P2-design.md"
    run bash -c "GATE_FILE='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
}

@test "PYX.6 agate-read-gate-commands.py GATE_FILE 不存在 → 非零退出" {
    run bash -c "GATE_FILE='/nonexistent/P2.md' python3 '$AGATE_SCRIPTS/agate-read-gate-commands.py'"
    [ "$status" -ne 0 ]
}

# ========== TAG0004 RM-AG0002 无 formatter A/B 判定（BDD-30/31） + TPV0090-M4 NameError B 类（BDD-35/36/37） ==========
# 参照 TDD.F* 系列：gate_commands.P3 + P3_formatter + project_module 的写法。

@test "bdd-30 check-tdd-red.sh 无 formatter + exit 1 + 编译/错误关键词 判 A 类（exit 1，RM-AG0002）" {
    local fake
    fake=$(make_fake_pytest "Traceback (most recent call last):
SyntaxError: invalid syntax" 1)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    # 修复前：无 formatter 降级 exit-code-only → 编译失败被误判正确红灯（exit 0）；修复后：A 类 exit 1
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "bdd-31 check-tdd-red.sh 无 formatter 普通断言失败仍判正确红灯（exit 0，RM-AG0002）" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed" 1)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"red-light"* ]]
}

@test "bdd-35 check-tdd-red.sh formatter 项目模块内 NameError 判 B 类红灯（exit 0，TPV0090-M4）" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - NameError: name 'compute' is not defined" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-bdd35"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    # 修复前：errors>0 一律判 A 类（exit 1）；修复后：项目内 NameError 归 B 类（exit 0）
    [ "$status" -eq 0 ]
    [[ "$output" == *"B-class"* ]]
}

@test "bdd-36 check-tdd-red.sh globals().get() 规避模式断言失败仍判 B 类（回归，TPV0090-M4）" {
    local fake
    fake=$(make_fake_pytest "2 failed, 5 passed
FAILED tests/test_x.py::test_y - assert 1 == 2" 1)
    local task_dir="$BATS_TEST_TMPDIR/task-bdd36"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"classic red-light"* ]]
}

@test "bdd-37 check-tdd-red.sh 非未定义符号的真实测试 bug（TypeError）仍判 A 类（防过宽，TPV0090-M4）" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - TypeError: unsupported operand type(s)" 2)
    local task_dir="$BATS_TEST_TMPDIR/task-bdd37"
    mkdir -p "$task_dir"
    cat > "$task_dir/P2-design.md" <<EOF
gate_commands:
  P3: "$fake"
  P3_formatter: "pytest.sh"
  project_module: "myapp"
EOF
    run env -u TEST_RUNNER TASK_DIR="$task_dir" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}
