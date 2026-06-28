#!/bin/bash
# 检查 TDD 红灯：区分 A 类（测试代码有 bug）和 B 类（实现未写的 import 失败）
# 退出 0 = 正确红灯（assertion failure > 0, collection error == 0）或 B 类红灯（import 未实现）
# 退出 1 = A 类错误（测试代码自身有语法/import 错误）
# 退出 2 = 测试全绿（说明实现先于测试写完，违反 TDD）
# 退出 3 = 找不到测试运行器
#
# 本脚本由 agate 协议定义（见 state-machine.md「P3 红灯的特别说明」），
# 供主 Agent 在 P3 gate 验证 TDD 灯时调用。
# 项目可直接使用 {agate_root}/scripts/check-tdd-red.sh，或复制到项目 scripts/ 目录。
#
# 环境变量 TEST_RUNNER：主 Agent 在调用前从 P0-brief.md env_constraints.debug_env
# 提取测试启动命令并 export。回退链：$TEST_RUNNER → which pytest → 报错 exit 3。
#
# T027 教训：P3 test-designer 不写 stub（那是 P4 implementer 的活），
# 所以 TDD 红灯几乎都是 ImportError（from myapp.xxx import Yyy），
# 不可能是 assertion failure。旧版脚本把所有 collection error 判为 A 类（exit 1），
# 导致 P3 gate 实践中永远无法通过。新版区分 A/B 类：
# - B 类：ImportError 目标是项目内模块（测试代码正确，只是依赖未实现）→ exit 0
# - A 类：测试代码自身语法错误或 import 非项目模块 → exit 1

if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var or install pytest." >&2
    exit 3
fi

RESULT=$($RUNNER -q 2>&1)
EXIT=$?

FAILED=$(echo "$RESULT" | grep -oP '\d+ failed' | grep -oP '\d+')
ERRORS=$(echo "$RESULT" | grep -oP '\d+ error' | grep -oP '\d+')

echo "assertion_failures=${FAILED:-0}, collection_errors=${ERRORS:-0}"

if [ "$EXIT" -eq 0 ]; then
    echo "TDD_CHECK: tests pass, no red-light — implementation may be ahead of tests"
    exit 2
fi

# 有 assertion failure 但无 collection error → 经典红灯
if [ "${ERRORS:-0}" -eq 0 ] && [ "${FAILED:-0}" -gt 0 ]; then
    echo "TDD_CHECK: classic red-light (assertion failures only)"
    exit 0
fi

# 有 collection error → 区分 A 类 / B 类
if [ "${ERRORS:-0}" -gt 0 ]; then
    # 提取 ImportError 行，检查目标是否是项目内模块
    # pytest 输出中 ImportError 格式示例：
    #   E   ImportError: cannot import name 'EntryShare' from 'peekview.shares' (/path/to/shares.py)
    #   E   ModuleNotFoundError: No module named 'myapp.shares'
    IMPORT_ERRORS=$(echo "$RESULT" | grep -E '(ImportError|ModuleNotFoundError):')
    if [ -n "$IMPORT_ERRORS" ]; then
        # 检查 ImportError 是否指向项目内模块
        # 策略：如果有任何 import error 且无测试代码自身语法错误，判定为 B 类
        # 语法错误特征：SyntaxError, IndentationError, NameError in test file
        SYNTAX_ERRORS=$(echo "$RESULT" | grep -E '(SyntaxError|IndententationError)' || true)
        if [ -z "$SYNTAX_ERRORS" ]; then
            echo "TDD_CHECK: B-class red-light (import errors from missing implementation)"
            echo "  ImportError lines:"
            echo "$IMPORT_ERRORS" | head -5 | sed 's/^/    /'
            exit 0
        fi
    fi
    # A 类：测试代码自身有 bug
    echo "TDD_CHECK: A-class error (test code has bugs, fix before proceeding)"
    echo "  Collection errors: ${ERRORS:-0}"
    exit 1
fi

# 兜底：有失败但既不是 assertion 也不是 error（不应到达此处）
echo "TDD_CHECK: unexpected test result — exit=$EXIT, failed=${FAILED:-0}, errors=${ERRORS:-0}"
exit 1
