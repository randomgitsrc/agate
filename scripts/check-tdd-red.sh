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
# === 通用性说明 ===
# 本脚本是 pytest 的参考实现。agate 是通用协议，不绑定特定技术栈。
# 非 Python 项目应提供自己的 TDD 红灯检查脚本，遵循以下契约：
#
# TEST_RUNNER 输出契约：
#   1. 测试运行器必须输出摘要行，包含 "N failed" 和 "M error" 格式
#   2. Import/collection 错误的 stderr 必须包含可识别的 import 错误标记
#   3. 退出码：0=全绿, >0=有失败
#
# 若项目的测试运行器不满足此契约，主 Agent 应：
#   - 写一个适配脚本包装测试运行器，将输出标准化为上述格式
#   - 将适配脚本路径设为 TEST_RUNNER 环境变量
#
# 环境变量：
#   TEST_RUNNER — 测试运行器命令（主 Agent 从 P0-brief.md env_constraints.debug_env 提取）
#                 回退链：$TEST_RUNNER → which pytest → exit 3
#   PROJECT_MODULE — 项目模块前缀（用于 B 类检测，如 "peekview"、"myapp"）
#                    若未设置，B 类检测退化为启发式（所有 ImportError 视为 B 类）
#                    非 Python 项目应设置此变量以匹配项目内模块路径
#
# T027 教训：P3 test-designer 不写 stub（那是 P4 implementer 的活），
# 所以 TDD 红灯几乎都是 ImportError（from myapp.xxx import Yyy），
# 不可能是 assertion failure。旧版脚本把所有 collection error 判为 A 类（exit 1），
# 导致 P3 gate 实践中永远无法通过。新版区分 A/B 类：
# - B 类：ImportError 目标是项目内模块（测试代码正确，只是依赖未实现）→ exit 0
# - A 类：测试代码自身语法错误或 import 非项目模块失败 → exit 1

if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var or install pytest." >&2
    echo "  (本脚本是 pytest 参考实现，非 Python 项目请提供适配脚本)" >&2
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
    # 提取 import 错误行
    IMPORT_ERRORS=$(echo "$RESULT" | grep -E '(ImportError|ModuleNotFoundError|Cannot find module|ClassNotFoundException|NoClassDefFoundError|unresolved import):' || true)
    if [ -n "$IMPORT_ERRORS" ]; then
        # 检查是否有测试代码自身语法错误
        SYNTAX_ERRORS=$(echo "$RESULT" | grep -E '(SyntaxError|IndentationError|CompileError|ParseError)' || true)
        if [ -z "$SYNTAX_ERRORS" ]; then
            # 若设置了 PROJECT_MODULE，检查 import 目标是否是项目内模块
            if [ -n "$PROJECT_MODULE" ]; then
                INTERNAL_IMPORT=$(echo "$IMPORT_ERRORS" | grep -E "(from ${PROJECT_MODULE}|import ${PROJECT_MODULE}|${PROJECT_MODULE}\.)" || true)
                if [ -n "$INTERNAL_IMPORT" ]; then
                    echo "TDD_CHECK: B-class red-light (import errors from missing project module '${PROJECT_MODULE}')"
                    echo "  ImportError lines:"
                    echo "$INTERNAL_IMPORT" | head -5 | sed 's/^/    /'
                    exit 0
                else
                    echo "TDD_CHECK: A-class error (import errors are NOT from project module '${PROJECT_MODULE}')"
                    echo "  ImportError lines:"
                    echo "$IMPORT_ERRORS" | head -5 | sed 's/^/    /'
                    exit 1
                fi
            else
                # 未设置 PROJECT_MODULE → 启发式：所有无语法错误的 ImportError 视为 B 类
                echo "TDD_CHECK: B-class red-light (heuristic: import errors without syntax errors)"
                echo "  注意：未设置 PROJECT_MODULE，无法区分项目内/第三方 import 错误"
                echo "  建议：设置 PROJECT_MODULE 环境变量以提高判定精度"
                echo "  ImportError lines:"
                echo "$IMPORT_ERRORS" | head -5 | sed 's/^/    /'
                exit 0
            fi
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
