#!/usr/bin/env python3
"""check-tdd-red.py — 检查 TDD 红灯：区分 A 类（测试代码有 bug）和 B 类（实现未写的 import 失败）

从 check-tdd-red.sh 迁移（TAG0010 批次 2e）。CLI 契约与 sh 版等价：
  exit 0 = 正确红灯（assertion failure > 0, collection error == 0）或 B 类红灯（import 未实现）
  exit 1 = A 类错误（测试代码自身有语法/import 错误）
  exit 2 = 测试全绿（说明实现先于测试写完，违反 TDD）
  exit 3 = 找不到测试运行器

供主 Agent 在 P3 gate 验证 TDD 灯时调用（见 state-machine.md「P3 红灯的特别说明」）。
项目可直接使用 {agate_root}/scripts/check-tdd-red.py，或复制到项目 scripts/ 目录。

技术栈无关：通过 formatter 机制支持任意技术栈的测试运行器。formatter 是 bash 脚本，
接收测试原始输出（stdin）和 exit code（$1），输出一行标准 JSON：
  {"exit_code":1,"total":5,"passed":0,"failed":3,"errors":1,
   "failed_tests":["test_foo"],"import_errors":[{"module":"myapp.foo","message":"..."}],
   "syntax_errors":[{"file":"test.py","message":"..."}],
   "name_errors":[{"symbol":"compute","module":"myapp","message":"..."}]}
无 formatter 时（TEST_RUNNER / gate_commands.P3 未配 P3_formatter），JSON 增
"raw_output" 字段，供 exit 1 + 编译/import 错误关键词判定 A/B 类。内置 formatter
位于 {agate_root}/assets/formatters/（pytest.sh / vitest.sh / go-test.sh /
generic-tap.sh / generic-junit-xml.sh / generic-exit-only.sh）。

环境变量（契约同 sh 版）：
  TEST_RUNNER    — 测试运行器命令（最高优先级，向后兼容；无 formatter 时按 exit code + 输出关键词判定 A/B）
  TASK_DIR       — 任务目录路径（读取 P2-design.md 的 gate_commands）；也可经位置参数 $1 传入
  PROJECT_MODULE — 项目模块前缀（B 类检测，如 "myapp"；未设置时退化为启发式——所有 ImportError 视为 B 类）
                   覆盖 gate_commands 的 project_module
  已废弃（不再有效，退化为 exit-code-only）：
  TEST_RUNNER_FLAGS / TEST_FAIL_PATTERN / TEST_ERROR_PATTERN / TEST_IMPORT_PATTERN

测试运行器探测链：$TEST_RUNNER → gate_commands.P3（P2-design.md）→ which pytest → exit 3

迁移映射（与 check-pruning.py / agate-capture-env-baseline.py 同风格）：
- run_test_with_formatter / resolve_formatter 来自 agate_common.py（P2 批次 0 公共库，
  原 sh source gate-result.sh），直接 import 复用不重新实现
- gate_commands 读取调 agate-read-gate-commands.py（env GATE_FILE 传参，sys.executable
  subprocess；$(...) 剥尾换行 → json.loads）
- JSON 字段提取不再逐字段子进程调 agate-json-get.py，改为 json.loads 内联等价
  （get / len / count_prefix 语义逐一对应，见 judge_result；batch 2c
  agate-capture-env-baseline.py 同款先例）
- formatter 仍是 bash 脚本 → 保持 ["bash", fmt_path, str(exit_code)] subprocess（在
  agate_common.run_test_with_formatter 内）
- command -v pytest → shutil.which
"""

import json
import os
import re
import shutil
import subprocess
import sys

try:
    from agate_common import resolve_formatter, run_test_with_formatter
except ImportError:
    sys.stderr.write("check-tdd-red: 需要 agate_common.py（与脚本同目录）。\n")
    sys.exit(3)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
READ_GATE_COMMANDS = os.path.join(SCRIPT_DIR, "agate-read-gate-commands.py")


def _read_gate_commands(p2_file):
    """调 agate-read-gate-commands.py（env GATE_FILE 传参），失败回退空命令 JSON（同 sh || echo）。"""
    env = dict(os.environ)
    env["GATE_FILE"] = p2_file
    try:
        proc = subprocess.run(
            [sys.executable, READ_GATE_COMMANDS],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return {"commands": [], "project_module": ""}
    if proc.returncode != 0:
        return {"commands": [], "project_module": ""}
    try:
        data = json.loads(proc.stdout or "{}")
    except ValueError:
        return {"commands": [], "project_module": ""}
    if not isinstance(data, dict):
        return {"commands": [], "project_module": ""}
    return data


def judge_result(json_str, project_module):
    """判定单个测试命令结果 → exit 0/1/2（等价 sh judge_result + agate-json-get.py 提取）。"""
    try:
        data = json.loads(json_str)
    except ValueError:
        data = {}

    exit_code = int(data.get("exit_code", 1))
    failed = int(data.get("failed", 0))
    errors = int(data.get("errors", 0))
    syntax_count = len(data.get("syntax_errors", []))
    import_count = len(data.get("import_errors", []))
    name_errors_count = len(data.get("name_errors", []))
    raw_output = data.get("raw_output", "") or ""

    if exit_code == 124:
        print("TDD_CHECK: 测试命令超时，视为红灯可推进（请手动确认测试确实失败）")
        return 0

    if exit_code == 0:
        print("TDD_CHECK: tests pass, no red-light — implementation may be ahead of tests")
        return 2

    if (
        exit_code == 2
        and failed == 0
        and errors == 0
        and syntax_count == 0
        and import_count == 0
        and name_errors_count == 0
        and raw_output
        and re.search(r"syntax error|unexpected|matching|寻找匹配|未预期", raw_output, re.IGNORECASE)
    ):
        print("TDD_CHECK: A-class error (command string itself has syntax error, runner never started)")
        return 1

    if exit_code == 1 and raw_output and re.search(r"Traceback|SyntaxError|ImportError|ModuleNotFoundError", raw_output):
        print("TDD_CHECK: A-class error (compile or import error in raw output, no formatter to classify)")
        return 1

    if syntax_count > 0:
        print("TDD_CHECK: A-class error (syntax errors in test code)")
        return 1

    if import_count > 0:
        if project_module:
            matched = sum(1 for e in data.get("import_errors", [])
                          if e.get("module", "").startswith(project_module))
            if matched > 0:
                print(f"TDD_CHECK: B-class red-light (import errors from missing project module '{project_module}')")
                return 0
            print(f"TDD_CHECK: A-class error (import errors are NOT from project module '{project_module}')")
            return 1
        print("TDD_CHECK: B-class red-light (heuristic: import errors without syntax errors)")
        return 0

    if name_errors_count > 0:
        if project_module:
            matched = sum(1 for e in data.get("name_errors", [])
                          if e.get("module", "").startswith(project_module))
            if matched > 0:
                print(f"TDD_CHECK: B-class red-light (NameError from missing project symbol '{project_module}')")
                return 0
        print("TDD_CHECK: B-class red-light (NameError: test references unimplemented symbol)")
        return 0

    if errors > 0:
        print("TDD_CHECK: A-class error (test code has errors, fix before proceeding)")
        return 1

    if failed > 0:
        print("TDD_CHECK: classic red-light (assertion failures only)")
        sys.stderr.write(
            "TDD_CHECK 提示: 测试能运行但断言失败。若失败原因是断言与测试数据矛盾（如行数/列数/页数不符），"
            "这是测试代码 bug，应退回 P3 修正断言——不是 P4 实现问题。"
            "T075 教训：7 条魔数断言与数据矛盾到 P5 才暴露。\n")
        return 0

    if exit_code >= 120:
        print(f"TDD_CHECK: A-class error (test runner failed with exit code {exit_code})")
        return 1

    print("TDD_CHECK: red-light (unexpected test failure)")
    return 0


def collect_commands(task_dir):
    """构建命令列表 JSON；找不到运行器时返回 None（调用方 exit 3）。"""
    project_module = os.environ.get("PROJECT_MODULE", "")

    test_runner = os.environ.get("TEST_RUNNER", "")
    if test_runner:
        return json.dumps({
            "commands": [{"cmd": test_runner, "formatter": "", "suffix": ""}],
            "project_module": project_module,
        })

    if task_dir and os.path.isfile(os.path.join(task_dir, "P2-design.md")):
        commands_data = _read_gate_commands(os.path.join(task_dir, "P2-design.md"))
        if commands_data.get("commands"):
            if project_module:
                commands_data["project_module"] = project_module
            return json.dumps(commands_data)

    if shutil.which("pytest"):
        return json.dumps({
            "commands": [{"cmd": "pytest", "formatter": "pytest.sh", "suffix": ""}],
            "project_module": project_module,
        })

    sys.stderr.write("TDD_CHECK: no test runner found. Set TEST_RUNNER env var, declare gate_commands.P3, or install pytest.\n")
    sys.stderr.write("  (本脚本支持任意技术栈，非 pytest 项目请在 P2 gate_commands.P3 声明测试命令)\n")
    return None


def main():
    task_dir = os.environ.get("TASK_DIR", "")
    if not task_dir and len(sys.argv) > 1:
        task_dir = sys.argv[1]

    commands_json = collect_commands(task_dir)
    if commands_json is None:
        sys.exit(3)
    try:
        commands_data = json.loads(commands_json)
    except ValueError:
        sys.exit(3)
    project_module = commands_data.get("project_module", "")
    commands = commands_data.get("commands", [])

    worst_exit = 0
    for entry in commands:
        cmd = entry.get("cmd", "")
        fmt_val = entry.get("formatter", "")
        fmt_path = None
        if fmt_val:
            fmt_path = resolve_formatter(fmt_val, task_dir)
        json_result = run_test_with_formatter(cmd, fmt_path)
        judge_exit = judge_result(json_result, project_module)
        if judge_exit > worst_exit:
            worst_exit = judge_exit
    sys.exit(worst_exit)


if __name__ == "__main__":
    main()
