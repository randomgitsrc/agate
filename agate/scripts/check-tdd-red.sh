#!/usr/bin/env bash
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
# === 技术栈无关 ===
# 本脚本通过 formatter 机制支持任意技术栈的测试运行器。
# formatter 是一个 bash 脚本，接收测试原始输出（stdin）和 exit code（$1），
# 输出一行标准 JSON：
#   {"exit_code":1,"total":5,"passed":0,"failed":3,"errors":1,
#    "failed_tests":["test_foo"],"import_errors":[{"module":"myapp.foo","message":"..."}],
#    "syntax_errors":[{"file":"test.py","message":"..."}]}
#
# 内置 formatter 位于 {agate_root}/assets/formatters/：
#   pytest.sh, vitest.sh, go-test.sh, generic-tap.sh, generic-junit-xml.sh, generic-exit-only.sh
#
# 环境变量：
#   TEST_RUNNER — 测试运行器命令（最高优先级，向后兼容，退化为 exit-code-only）
#   TASK_DIR — 任务目录路径（用于读取 P2-design.md 的 gate_commands）
#              也可通过位置参数 $1 传入（check-gate.sh 调用时传递）
#   PROJECT_MODULE — 项目模块前缀（用于 B 类检测，如 "myapp"、"webapp"）
#                    若未设置，B 类检测退化为启发式（所有 ImportError 视为 B 类）
#                    覆盖 gate_commands 的 project_module
#
# 已废弃环境变量（不再有效，退化为 exit-code-only）：
#   TEST_RUNNER_FLAGS, TEST_FAIL_PATTERN, TEST_ERROR_PATTERN, TEST_IMPORT_PATTERN
#
# 测试运行器探测链：$TEST_RUNNER → gate_commands.P3*（P2-design.md）→ which pytest → exit 3
#
# gate_commands 键（architect 在 P2-design.md 声明）：
#   P3: "pytest -q --tb=short"            — 主测试命令
#   P3_formatter: "pytest.sh"             — 对应的 formatter（可选，无则 exit-code-only）
#   P3_{suffix}: "npx vitest run"         — 多技术栈命令（suffix 自定义）
#   P3_{suffix}_formatter: "vitest.sh"    — 对应的 formatter
#   project_module: "myapp"               — 项目模块前缀（用于 B 类检测）
#
# 无 formatter 时退化为 exit-code-only：exit 0→绿灯(2)，exit>0→红灯(0)，无法区分 A/B 类。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/gate-result.sh"

if [ -z "${TASK_DIR:-}" ] && [ $# -gt 0 ]; then
    TASK_DIR="$1"
fi

read_gate_commands() {
    local p2_file="$1"
    GATE_FILE="$p2_file" python3 -c '
import re, os, sys, json
content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print(json.dumps({"commands": [], "project_module": ""}))
    sys.exit(0)
block = m.group(1)
commands = []
project_module = ""
for line in re.findall(r"^  (\w+):\s*(.+)$", block, re.MULTILINE):
    key = line[0]
    val = line[1].strip().strip("\"").strip(chr(39))
    if key == "project_module":
        project_module = val
    elif key.startswith("P3") and not key.endswith("_formatter"):
        suffix = key[2:] if len(key) > 2 else ""
        fmt_key = "P3" + suffix + "_formatter"
        fmt_val = ""
        for line2 in re.findall(r"^  (" + re.escape(fmt_key) + r"):\s*(.+)$", block, re.MULTILINE):
            fmt_val = line2[1].strip().strip("\"").strip(chr(39))
        commands.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
result = {"commands": commands, "project_module": project_module}
print(json.dumps(result))
' 2>/dev/null || echo '{"commands":[],"project_module":""}'
}

judge_result() {
    local json="$1"
    local project_module="$2"
    local exit_code failed errors syntax_count import_count

    exit_code=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("exit_code",1))')
    failed=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("failed",0))')
    errors=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("errors",0))')
    syntax_count=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("syntax_errors",[])))')
    import_count=$(echo "$json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("import_errors",[])))')

    if [ "$exit_code" -eq 0 ]; then
        echo "TDD_CHECK: tests pass, no red-light — implementation may be ahead of tests"
        return 2
    fi

    if [ "$syntax_count" -gt 0 ]; then
        echo "TDD_CHECK: A-class error (syntax errors in test code)"
        return 1
    fi

    if [ "$import_count" -gt 0 ]; then
        if [ -n "$project_module" ]; then
            local matched
            matched=$(echo "$json" | PROJECT_MODULE="$project_module" python3 -c '
import sys, json, os
d = json.load(sys.stdin)
pm = os.environ["PROJECT_MODULE"]
count = sum(1 for e in d.get("import_errors", []) if e.get("module","").startswith(pm))
print(count)
')
            if [ "$matched" -gt 0 ]; then
                echo "TDD_CHECK: B-class red-light (import errors from missing project module '${project_module}')"
                return 0
            else
                echo "TDD_CHECK: A-class error (import errors are NOT from project module '${project_module}')"
                return 1
            fi
        else
            echo "TDD_CHECK: B-class red-light (heuristic: import errors without syntax errors)"
            return 0
        fi
    fi

    if [ "$errors" -gt 0 ]; then
        echo "TDD_CHECK: A-class error (test code has errors, fix before proceeding)"
        return 1
    fi

    if [ "$failed" -gt 0 ]; then
        echo "TDD_CHECK: classic red-light (assertion failures only)"
        return 0
    fi

    if [ "$exit_code" -ge 120 ]; then
        echo "TDD_CHECK: A-class error (test runner failed with exit code $exit_code)"
        return 1
    fi

    echo "TDD_CHECK: red-light (unexpected test failure)"
    return 0
}

collect_commands() {
    local commands_json
    local project_module=""

    if [ -n "${TEST_RUNNER:-}" ]; then
        echo "{\"commands\":[{\"cmd\":\"$TEST_RUNNER\",\"formatter\":\"\",\"suffix\":\"\"}],\"project_module\":\"${PROJECT_MODULE:-}\"}"
        return 0
    fi

    if [ -n "${TASK_DIR:-}" ] && [ -f "$TASK_DIR/P2-design.md" ]; then
        commands_json=$(read_gate_commands "$TASK_DIR/P2-design.md")
        local cmd_count
        cmd_count=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d["commands"]))')
        if [ "$cmd_count" -gt 0 ]; then
            if [ -n "${PROJECT_MODULE:-}" ]; then
                commands_json=$(echo "$commands_json" | python3 -c 'import sys,json,os; d=json.load(sys.stdin); d["project_module"]=os.environ["PROJECT_MODULE"]; print(json.dumps(d))' 2>/dev/null || echo "$commands_json")
            fi
            echo "$commands_json"
            return 0
        fi
    fi

    if command -v pytest &>/dev/null; then
        echo "{\"commands\":[{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\",\"suffix\":\"\"}],\"project_module\":\"${PROJECT_MODULE:-}\"}"
        return 0
    fi

    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var, declare gate_commands.P3, or install pytest." >&2
    echo "  (本脚本支持任意技术栈，非 pytest 项目请在 P2 gate_commands.P3 声明测试命令)" >&2
    return 3
}

main() {
    local commands_json project_module commands_count
    commands_json=$(collect_commands) || exit 3
    project_module=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("project_module",""))')
    commands_count=$(echo "$commands_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d["commands"]))')

    local worst_exit=0
    local i=0
    while [ "$i" -lt "$commands_count" ]; do
        local cmd fmt_val fmt_path json_result
        cmd=$(echo "$commands_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['commands'][$i]['cmd'])")
        fmt_val=$(echo "$commands_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['commands'][$i]['formatter'])")

        fmt_path=""
        if [ -n "$fmt_val" ]; then
            fmt_path=$(resolve_formatter "$fmt_val" "${TASK_DIR:-}") || fmt_path=""
        fi

        json_result=$(run_test_with_formatter "$cmd" "$fmt_path")

        local judge_exit=0
        judge_result "$json_result" "$project_module" || judge_exit=$?

        if [ "$judge_exit" -gt "$worst_exit" ]; then
            worst_exit="$judge_exit"
        fi

        i=$((i + 1))
    done

    exit "$worst_exit"
}

main
