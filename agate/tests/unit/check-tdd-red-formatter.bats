#!/usr/bin/env bats
# tests/unit/check-tdd-red-formatter.bats — 12 用例覆盖 formatter 脚本

load ../helpers/load.bash

FORMATTER_DIR="$AGATE_ROOT/assets/formatters"

assert_json_field() {
    local json="$1"
    local expr="$2"
    local expected="$3"
    local actual
    actual=$(printf '%s' "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print($expr)" 2>/dev/null)
    [ "$actual" = "$expected" ]
}

assert_json_contains() {
    local json="$1"
    local expr="$2"
    local expected="$3"
    printf '%s' "$json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
val=$expr
if isinstance(val, list):
    assert any('$expected' in str(x) for x in val), f'$expected not found in {val}'
else:
    assert '$expected' in str(val), f'$expected not found in {val}'
" 2>/dev/null
}

@test "FMT.1: generic-exit-only.sh exit 1 → exit_code=1, empty arrays" {
    local result
    result=$(echo "some output" | bash "$FORMATTER_DIR/generic-exit-only.sh" 1)
    assert_json_field "$result" "d['exit_code']" "1"
    assert_json_field "$result" "len(d['failed_tests'])" "0"
    assert_json_field "$result" "len(d['import_errors'])" "0"
    assert_json_field "$result" "len(d['syntax_errors'])" "0"
}

@test "FMT.2: generic-exit-only.sh exit 0 → exit_code=0" {
    local result
    result=$(echo "all good" | bash "$FORMATTER_DIR/generic-exit-only.sh" 0)
    assert_json_field "$result" "d['exit_code']" "0"
    assert_json_field "$result" "d['passed']" "0"
    assert_json_field "$result" "d['failed']" "0"
}

@test "FMT.3: pytest.sh (2 failed, 5 passed) → failed=2, passed=5, errors=0, failed_tests has 2" {
    local output="tests/test_a.py::test_one FAILED [ 50%]
tests/test_b.py::test_two FAILED [100%]
2 failed, 5 passed"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/pytest.sh" 1)
    assert_json_field "$result" "d['failed']" "2"
    assert_json_field "$result" "d['passed']" "5"
    assert_json_field "$result" "d['errors']" "0"
    assert_json_field "$result" "len(d['failed_tests'])" "2"
}

@test "FMT.4: pytest.sh B-class (ImportError from myapp.foo) → import_errors[0].module=='myapp.foo'" {
    local output="ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'
1 error"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/pytest.sh" 2)
    assert_json_field "$result" "d['import_errors'][0]['module']" "myapp.foo"
}

@test "FMT.5: pytest.sh A-class (SyntaxError) → syntax_errors non-empty" {
    local output="ERROR tests/test_x.py - SyntaxError: invalid syntax
1 error"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/pytest.sh" 2)
    assert_json_field "$result" "len(d['syntax_errors'])" "1"
}

@test "FMT.6: pytest.sh all passed → passed=5, failed=0" {
    local output="5 passed"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/pytest.sh" 0)
    assert_json_field "$result" "d['passed']" "5"
    assert_json_field "$result" "d['failed']" "0"
}

@test "FMT.7: vitest.sh (11 failed, 6 passed) → failed=11, errors=0, import_errors=[]" {
    local output="Tests  11 failed | 6 passed
Test Files  3 failed"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/vitest.sh" 1)
    assert_json_field "$result" "d['failed']" "11"
    assert_json_field "$result" "d['errors']" "0"
    assert_json_field "$result" "len(d['import_errors'])" "0"
}

@test "FMT.8: vitest.sh B-class (Cannot find module '../src/bar') → import_errors[0].module=='../src/bar'" {
    local output="Failed Suites 1
Error: Cannot find module '../src/bar' imported from /tmp/test/foo.test.ts"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/vitest.sh" 1)
    assert_json_field "$result" "d['import_errors'][0]['module']" "../src/bar"
}

@test "FMT.9: vitest.sh A-class (Cannot find module 'react') → import_errors[0].module=='react'" {
    local output="Failed Suites 1
Error: Cannot find module 'react' imported from /tmp/test/foo.test.ts"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/vitest.sh" 1)
    assert_json_field "$result" "d['import_errors'][0]['module']" "react"
}

@test "FMT.10: go-test.sh cargo format (2 passed, 1 failed) → failed=1, failed_tests contains 'foo::test_bar'" {
    local output="test foo::test_bar ... FAILED
test foo::test_baz ... ok
test foo::test_qux ... ok
1 failed, 2 passed"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/go-test.sh" 1)
    assert_json_field "$result" "d['failed']" "1"
    assert_json_contains "$result" "d['failed_tests']" "foo::test_bar"
}

@test "FMT.11: generic-tap.sh (2 ok, 1 not ok) → passed=2, failed=1, failed_tests contains 'test gamma'" {
    local output="TAP version 13
ok 1 - test alpha
ok 2 - test beta
not ok 3 - test gamma"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/generic-tap.sh" 1)
    assert_json_field "$result" "d['passed']" "2"
    assert_json_field "$result" "d['failed']" "1"
    assert_json_contains "$result" "d['failed_tests']" "test gamma"
}

@test "FMT.12: generic-junit-xml.sh (tests=3, failures=1, errors=1) → total=3, failed=1, errors=1, passed=1" {
    local output='<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="suite" tests="3" failures="1" errors="1" skipped="0">
<testcase name="test_one" classname="MyClass"/>
<testcase name="test_two" classname="MyClass"><failure message="fail">expected true</failure></testcase>
<testcase name="test_three" classname="MyClass"><error message="err">exception</error></testcase>
</testsuite>'
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/generic-junit-xml.sh" 1)
    assert_json_field "$result" "d['total']" "3"
    assert_json_field "$result" "d['failed']" "1"
    assert_json_field "$result" "d['errors']" "1"
    assert_json_field "$result" "d['passed']" "1"
}

# ========== TAG0004 TPV0090-M4 formatter name_errors 字段（BDD-35，TDD 红灯） ==========

@test "bdd-35f FMT.13: pytest.sh 输出含 NameError 时 JSON 含 name_errors 字段（项目内未定义符号）" {
    local output="ERROR tests/test_x.py - NameError: name 'compute' is not defined
1 error"
    local result
    result=$(echo "$output" | bash "$FORMATTER_DIR/pytest.sh" 2)
    # 修复前：pytest.sh 无 name_errors 字段（KeyError）；修复后：解析出 1 条 NameError
    assert_json_field "$result" "len(d['name_errors'])" "1"
}
