#!/usr/bin/env python3
"""agate-capture-env-baseline.py — 捕获任务开始前的全量测试失败列表，供 P5 阶段做机械 diff。

从 agate-capture-env-baseline.sh 迁移（TAG0010 批次 2c）。CLI 契约与 sh 版等价：
  agate-capture-env-baseline.py TASK_DIR

幂等：任务级已捕获过则直接退出，不重跑。
缓存：仓库级按 (commit hash + gate_commands.P5 命令+formatter 集合) 缓存，HEAD 未变则复用。
不阻塞：本脚本任何情况下都不应导致调用方 P3/P4 流程失败——
  捕获失败或无法可靠解析（如项目尚未声明 gate_commands.P5、命令执行异常、
  无 formatter 无法提取 fail-list）一律只打印 WARNING 到 stderr、不写入任何文件、
  exit 0（缺失的后果由 P5 阶段的 graceful degradation 承担）。

重要：不对声明的命令追加任何 flag。命令必须原样来自 gate_commands.P5
（项目自己声明时就该带齐所需参数，本脚本只复用不改写）。

依赖：agate_common.resolve_formatter / run_test_with_formatter（批次 0 公共库，
替代 gate-result.sh source）；agate-read-p5-commands.py（env P2_DESIGN，sys.executable
subprocess）；agate-json-get.py 的取数语义用 json.loads 等价实现（不再 subprocess 逐字段取）；
$(...) 剥尾换行 → .rstrip("\n")；sha256sum | cut → hashlib.sha256().hexdigest()。
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys

try:
    from agate_common import resolve_formatter, run_git, run_test_with_formatter
except ImportError:
    resolve_formatter = None
    run_git = None
    run_test_with_formatter = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
READ_P5 = os.path.join(SCRIPT_DIR, "agate-read-p5-commands.py")


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("用法: agate-capture-env-baseline.py TASK_DIR\n")
        sys.exit(1)
    task_dir = sys.argv[1]
    baseline = os.path.join(task_dir, "pre-task-baseline.md")
    if os.path.isfile(baseline):
        sys.exit(0)

    p2_file = os.path.join(task_dir, "P2-design.md")
    if not os.path.isfile(p2_file):
        sys.stderr.write(
            "ENV_BASELINE: P2-design.md 不存在，跳过基线捕获（P2 未完成前不应到达此步）\n"
        )
        sys.exit(0)

    env = dict(os.environ)
    env["P2_DESIGN"] = p2_file
    try:
        proc = subprocess.run(
            [sys.executable, READ_P5],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
        p5_data = (proc.stdout or "").rstrip("\n")
    except OSError:
        p5_data = ""
    if not p5_data:
        sys.stderr.write("ENV_BASELINE: 未在 P2-design.md 找到 gate_commands.P5，跳过基线捕获\n")
        sys.exit(0)

    if run_git is None:
        sys.stderr.write("ENV_BASELINE: 非 git 仓库，跳过\n")
        sys.exit(0)
    rc, out = run_git(["rev-parse", "HEAD"])
    if rc != 0:
        sys.stderr.write("ENV_BASELINE: 非 git 仓库，跳过\n")
        sys.exit(0)
    commit = out.rstrip("\n").strip()

    cache_key = hashlib.sha256((commit + "\n" + p5_data).encode("utf-8")).hexdigest()
    rc, out = run_git(["rev-parse", "--show-toplevel"])
    if rc != 0:
        sys.stderr.write("ENV_BASELINE: 非 git 仓库，跳过\n")
        sys.exit(0)
    repo_root = out.rstrip("\n").strip()
    cache_dir = os.path.join(repo_root, "docs", ".agate-env-baseline-cache")
    cache_file = os.path.join(cache_dir, cache_key + ".md")
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except OSError:
        sys.stderr.write("ENV_BASELINE: 无法创建缓存目录，跳过基线捕获\n")
        sys.exit(0)

    if os.path.isfile(cache_file):
        shutil.copyfile(cache_file, baseline)
        sys.stderr.write("ENV_BASELINE: 复用缓存（commit {} 未变）\n".format(commit))
        sys.exit(0)

    try:
        commands = json.loads(p5_data).get("commands", [])
    except ValueError:
        sys.stderr.write("ENV_BASELINE: P5 数据解析失败，跳过基线捕获\n")
        sys.exit(0)

    fail_list = ""
    parse_ok = True
    for entry in commands:
        cmd = entry.get("cmd", "")
        fmt_val = entry.get("formatter", "")

        fmt_path = ""
        if fmt_val and resolve_formatter is not None:
            fmt_path = resolve_formatter(fmt_val, task_dir) or ""

        if not fmt_path:
            sys.stderr.write(
                "ENV_BASELINE: 命令 '{}' 无 formatter，无法提取 fail-list，放弃捕获，不写入任何文件\n".format(cmd)
            )
            parse_ok = False
            break

        if run_test_with_formatter is None:
            sys.stderr.write(
                "ENV_BASELINE: 命令 '{}' 无法执行（agate_common 不可用），放弃捕获，不写入任何文件\n".format(cmd)
            )
            parse_ok = False
            break
        json_result = run_test_with_formatter(cmd, fmt_path)
        try:
            result = json.loads(json_result)
        except ValueError:
            sys.stderr.write(
                "ENV_BASELINE: 命令 '{}' 结果解析失败，放弃捕获，不写入任何文件\n".format(cmd)
            )
            parse_ok = False
            break

        json_exit_code = int(result.get("exit_code", 0))
        if json_exit_code >= 120:
            sys.stderr.write(
                "ENV_BASELINE: 命令 '{}' 本身崩溃（exit code {}），放弃捕获，不写入任何文件\n".format(
                    cmd, json_exit_code
                )
            )
            parse_ok = False
            break

        failed_tests = result.get("failed_tests", [])
        cmd_fail_count = sum(1 for t in failed_tests if t != "")
        json_failed = int(result.get("failed", 0))
        json_errors = int(result.get("errors", 0))
        summary_count = json_failed + json_errors

        if summary_count == 0:
            sys.stderr.write("ENV_BASELINE: 命令 '{}' 无失败，跳过\n".format(cmd))
            continue

        if cmd_fail_count != summary_count:
            sys.stderr.write(
                "ENV_BASELINE: 命令 '{}' 汇总计数({})与明细提取数({})不一致，\n".format(
                    cmd, summary_count, cmd_fail_count
                )
            )
            sys.stderr.write(
                "  说明当前 runner 的明细行格式未被 formatter 识别，放弃捕获\n"
            )
            parse_ok = False
            break

        fail_list += "\n".join(failed_tests) + "\n"

    if not parse_ok:
        sys.exit(0)

    fail_lines = sorted(set(line for line in fail_list.split("\n") if line))
    fail_count = len(fail_lines)

    content = (
        "---\n"
        "captured_at_commit: {}\n".format(commit)
        + "generated_by: agate-capture-env-baseline.py\n"
        + "---\n"
        + "# 任务前环境基线\n"
        + "\n"
        + "失败数：{}\n".format(fail_count)
        + "\n"
        + "```fail-list\n"
        + "\n".join(fail_lines)
        + "\n"
        + "```\n"
    )
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError:
        sys.stderr.write("ENV_BASELINE: 写入缓存失败，跳过基线捕获\n")
        sys.exit(0)

    shutil.copyfile(cache_file, baseline)
    sys.stderr.write("ENV_BASELINE: 已捕获，失败数={}\n".format(fail_count))
    sys.exit(0)


if __name__ == "__main__":
    main()
