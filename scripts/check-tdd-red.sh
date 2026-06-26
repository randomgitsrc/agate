#!/bin/bash
# 检查 TDD 红灯：只允许 assertion failure，拒绝 collection/import error
# 退出 0 = 正确的红灯（assertion failure > 0, collection error == 0）
# 退出 1 = 错误（有 collection/import error）
# 退出 2 = 测试全绿（说明实现先于测试写完，违反 TDD）
#
# 本脚本由 agate 协议定义（见 state-machine.md「P3 红灯的特别说明」），
# 供主 Agent 在 P3 gate 验证 TDD 红灯时调用。
# 项目可直接使用 {agate_root}/scripts/check-tdd-red.sh，或复制到项目 scripts/ 目录。

RESULT=$(pytest -q 2>&1)
EXIT=$?

FAILED=$(echo "$RESULT" | grep -oP '\d+ failed' | grep -oP '\d+')
ERRORS=$(echo "$RESULT" | grep -oP '\d+ error' | grep -oP '\d+')

echo "assertion_failures=${FAILED:-0}, collection_errors=${ERRORS:-0}"

if [ "$EXIT" -eq 0 ]; then
    echo "TDD_CHECK: tests pass, no red-light — implementation may be ahead of tests"
    exit 2
fi

if [ "${ERRORS:-0}" -gt 0 ]; then
    echo "TDD_CHECK: collection/import errors detected — test code has bugs, fix before proceeding"
    exit 1
fi

# exit code > 0 (pytest has failures) but not due to errors = assertion failures
exit 0
