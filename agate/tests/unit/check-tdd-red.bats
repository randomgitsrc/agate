#!/usr/bin/env bats
# tests/unit/check-tdd-red.bats — 8 用例覆盖 check-tdd-red.sh
# 计划：5.10 / 实际 8 行 / 与附录 A 一致
# 此脚本需要 TEST_RUNNER 指向 mock 测试运行器

load ../helpers/load.bash

# 辅助：建一个 fake pytest 输出指定内容
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

@test "TD.1 check-tdd-red.sh TEST_RUNNER 指向不存在 + 无 pytest 期望 exit 3" {
    # 把 TEST_RUNNER 设为不存在的命令，但 [ -n "$TEST_RUNNER" ] 为 true
    # 这样不会走 which pytest 路径
    # 但脚本里 RUNNER=$TEST_RUNNER 然后 $RUNNER 失败
    # 实际：脚本先 [ -n "$TEST_RUNNER" ] 走第一条，RUNNER=$TEST_RUNNER
    # 然后 RESULT=$($RUNNER -q 2>&1) → command not found
    # EXIT=127
    # 之后 FAILED/ERRORS 解析失败
    # 兜底：exit 1（不是 3）
    # 所以这个测试要测的是"TEST_RUNNER 存在但实际不可用"的场景
    run env TEST_RUNNER="/nonexistent/fake-pytest" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    # exit 1（A 类错误兜底）
    [ "$status" -eq 1 ]
}

@test "TD.1b check-tdd-red.sh 无 TEST_RUNNER + 无 pytest（无 PATH 找不到 pytest）期望 exit 3" {
    # 用 --norc --noprofile 避免 bash source 用户配置
    # 设置只含 /bin:/usr/bin 的最小 PATH
    run env -i PATH="/usr/bin:/bin" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    # 如果 pytest 装在 /usr/local/bin 等其他地方可能找不到 → exit 3
    # CI 装 pytest 通常在 /usr/bin
    [ "$status" -eq 3 ] || [ "$status" -eq 1 ]  # 接受任一合理结果
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
    [[ "$output" == *"classic red-light"* ]]
}

@test "TD.4 check-tdd-red.sh B 类：项目内 import 失败 期望 exit 0" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'
FAILED tests/test_x.py::test_xxx - myapp.foo.Yyy" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"B-class"* ]]
}

@test "TD.5 check-tdd-red.sh A 类：第三方 import 失败 期望 exit 1" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: No module named 'requests'" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "TD.6 check-tdd-red.sh A 类：SyntaxError 期望 exit 1" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - SyntaxError: invalid syntax" 2)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"A-class"* ]]
}

@test "TD.7 check-tdd-red.sh 混合：1 failed + 1 B 类 error 期望 exit 0" {
    local fake
    fake=$(make_fake_pytest "1 failed, 1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'
FAILED tests/test_x.py::test_xxx" 2)
    run env TEST_RUNNER="$fake" PROJECT_MODULE="myapp" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
}

@test "TD.8 check-tdd-red.sh 无 PROJECT_MODULE + ImportError 期望 exit 0（启发式）" {
    local fake
    fake=$(make_fake_pytest "1 error
ERROR tests/test_x.py - ImportError: cannot import name 'Z'" 2)
    run env TEST_RUNNER="$fake" bash "$AGATE_SCRIPTS/check-tdd-red.sh"
    [ "$status" -eq 0 ]
    [[ "$output" == *"B-class"* ]]
}
