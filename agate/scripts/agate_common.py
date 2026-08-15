#!/usr/bin/env python3
"""agate_common.py — agate 脚本公共函数库（P4 批次 0）

替代 gate-result.sh + agate-workspace-resolve.sh 的函数库，并承载 3 个 hook 薄壳
共用的定位/探测工具（P2-design.md §3.1）。

- 数据流函数（迁移自 gate-result.sh）：write_gate_result / read_state_phase /
  read_state_task_id / has_staged_phase_change / has_staged_phase_output /
  resolve_formatter / run_test_with_formatter
- 工作区解析函数（迁移自 agate-workspace-resolve.sh）：resolve_workspace
  （执行模式 main 输出 AGATE_WORKSPACE=/AGATE_TASKS_DIR= 两行，bats 直调契约）
- hook 公共工具：resolve_agate_root / probe_python / run_git

约定：所有文本读写显式 encoding="utf-8"；pyyaml 缺失时 fail-closed（同
agate-state-get.py）。Python 3.8+（禁 match / str.removeprefix）。
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("agate_common: 需要 pyyaml。pip install pyyaml\n")
    sys.exit(1)

_AGATE_ROOT = Path(__file__).resolve().parent.parent


# ---------- MAX_RETRY_MAP（单一数据源） ----------
# 按阶段差异化 MAX_RETRY（P3/P5/P6/P7/P8=2，其他=3）。
# 供 check-state-transition.py / agate-retreat-to.py 共享（原 check-state-transition.sh
# 的字面值 + check-retrospective.py 的模块级常量，TAG0010 批次 2b 统一于此）；
# 两脚本仍支持环境变量覆盖（MAX_RETRY_MAP=... 优先，同 sh 版 ${MAX_RETRY_MAP:-...} 语义）。
MAX_RETRY_MAP = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"


# ---------- run_git / 通用工具 ----------


def run_git(args, cwd=None):
    """git subprocess 封装。

    encoding="utf-8" + errors="replace"（Windows 代码页差异不崩溃），返回
    (returncode, stdout)。git 不可用时按失败处理（同 sh 侧 2>/dev/null 语义）。
    """
    try:
        proc = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=cwd,
        )
        return proc.returncode, proc.stdout
    except OSError:
        return 1, ""


def probe_python():
    """探测可用 python 解释器：python3 → python（shutil.which 顺序，替代 detect_python）。

    返回解析到的可执行路径；均不可用时返回 None（调用方须 fail-closed 阻断）。
    """
    for name in ("python3", "python"):
        path = shutil.which(name)
        if path:
            return path
    return None


def resolve_agate_root(script_path):
    """解析 AGATE_ROOT：软链 readlink 解析 → 复制模式 .agate-root 标记恢复。

    AGATE_ROOT 环境变量优先（hook 显式传入）。本体 scripts/ 缺失且标记文件存在时
    读标记文件（utf-8 + CRLF 剥离）恢复。
    """
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return env_root
    real = str(Path(script_path).resolve())
    agate_root = os.path.dirname(os.path.dirname(real))
    if not os.path.isdir(os.path.join(agate_root, "scripts")):
        marker = os.path.join(os.path.dirname(real), ".agate-root")
        if os.path.isfile(marker):
            with open(marker, encoding="utf-8") as f:
                content = f.read().replace("\r", "").strip()
            if content:
                return content
    return agate_root


# ---------- 数据流函数（gate-result.sh 迁移） ----------


def write_gate_result(phase, task_id, exit_code, output):
    """写 .gate-result.json（结构不变）+ 追加 .gate-history.jsonl。

    output 用 json.dumps 转义（替代 agate-json-get.py escape）；prev_commit_sha 用
    git rev-parse HEAD（失败回退 "pre-commit"——pre-commit hook 在 commit 创建前
    运行，HEAD 是上一个 commit）。
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rc, head = run_git(["rev-parse", "HEAD"])
    prev_commit_sha = head.strip() if rc == 0 and head.strip() else "pre-commit"

    result = {
        "phase": phase,
        "task_id": task_id,
        "exit_code": int(exit_code),
        "timestamp": ts,
        "output": output,
        "runner": "pre-commit-hook",
        "prev_commit_sha": prev_commit_sha,
    }
    with open(".gate-result.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")

    history = {
        "phase": phase,
        "task_id": task_id,
        "exit_code": int(exit_code),
        "timestamp": ts,
        "prev_commit_sha": prev_commit_sha,
    }
    with open(".gate-history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(history, separators=(",", ":"), ensure_ascii=True) + "\n")


def _read_state(state_file):
    """读 .state.yaml 为 dict；文件不存在/解析失败返回 None（调用方按空处理）。"""
    if not os.path.isfile(state_file):
        return None
    try:
        with open(state_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def read_state_phase(state_file):
    """读 .state.yaml 的 phase；文件不存在/解析失败返回 ""。"""
    data = _read_state(state_file)
    return data.get("phase", "") if data else ""


def read_state_task_id(state_file):
    """读 .state.yaml 的 task_id；文件不存在/解析失败返回 ""。"""
    data = _read_state(state_file)
    return data.get("task_id", "") if data else ""


def has_staged_phase_change(state_file):
    """暂存区中 state 文件含 phase 字段变更。

    git diff --cached --name-only + CRLF 剥离（line.rstrip("\\r")）判断文件已暂存，
    再对该文件 diff 检查 ^\\+.*phase:（替代 tr -d '\\r' + grep，TAG0009）。
    """
    basename = os.path.basename(state_file)
    rc, name_only = run_git(["diff", "--cached", "--name-only"])
    if rc != 0:
        return False
    staged = [line.rstrip("\r") for line in name_only.splitlines()]
    if basename not in staged:
        return False
    rc, diff = run_git(["diff", "--cached", "--", basename])
    if rc != 0:
        return False
    return any(re.match(r"^\+.*phase:", line.rstrip("\r")) for line in diff.splitlines())


def has_staged_phase_output():
    """暂存区文件名匹配阶段产出（P{n}-*.md|yaml）。"""
    rc, name_only = run_git(["diff", "--cached", "--name-only"])
    if rc != 0:
        return False
    return any(re.search(r"P[0-9]+-.*\.(md|yaml)$", line.rstrip("\r")) for line in name_only.splitlines())


def resolve_formatter(fmt, task_dir=None, agate_root=None):
    """formatter 路径解析，优先级：绝对路径 → $task_dir/.agate/formatters/ → $agate_root/assets/formatters/。

    返回存在路径；找不到返回 None（调用方按空处理，同 sh 侧 exit 1 语义）。
    """
    if agate_root is None:
        agate_root = _AGATE_ROOT
    if fmt.startswith("/"):
        if os.path.isfile(fmt):
            return fmt
        return None
    if task_dir:
        p = os.path.join(task_dir, ".agate", "formatters", fmt)
        if os.path.isfile(p):
            return p
    p = os.path.join(str(agate_root), "assets", "formatters", fmt)
    if os.path.isfile(p):
        return p
    return None


def _timeout_json():
    return json.dumps({
        "exit_code": 124,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "failed_tests": [],
        "import_errors": [],
        "syntax_errors": [],
    })


def _fallback_json(exit_code, output):
    return json.dumps({
        "exit_code": exit_code,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "failed_tests": [],
        "import_errors": [],
        "syntax_errors": [],
        "name_errors": [],
        "raw_output": output,
    })


def run_test_with_formatter(cmd, fmt_path, timeout_secs=None):
    """跑测试命令并输出 JSON 结果（TDD 语义，P2 §3.1）。

    用 subprocess timeout（替代 GNU timeout 二进制），保留 exit 124 超时语义；
    stdout/stderr 合并（2>&1）。fmt_path 为空或 formatter 失败时回退 raw_output JSON。
    """
    if timeout_secs is None:
        timeout_secs = int(os.environ.get("AGATE_TDD_TIMEOUT", "120"))
    output = ""
    exit_code = 0
    try:
        proc = subprocess.run(
            cmd, shell=True, executable="bash",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            timeout=timeout_secs,
        )
        output = proc.stdout or ""
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        exit_code = 124

    if exit_code == 124:
        sys.stderr.write(f"TDD_CHECK: 测试命令超时（{timeout_secs}s），请手动运行确认：{cmd}\n")
        return _timeout_json()

    if not fmt_path:
        return _fallback_json(exit_code, output)

    try:
        fmt_proc = subprocess.run(
            ["bash", fmt_path, str(exit_code)],
            input=output, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return _fallback_json(exit_code, output)
    if fmt_proc.returncode != 0:
        return _fallback_json(exit_code, output)
    return fmt_proc.stdout or _fallback_json(exit_code, output)


# ---------- 工作区解析函数（agate-workspace-resolve.sh 迁移） ----------


def _resolve_abs(base, p):
    """相对路径相对 base 归一 / 绝对路径原样，Path.resolve() 替代 realpath -m。"""
    if os.path.isabs(p):
        return str(Path(p).resolve())
    return str(Path(base, p).resolve())


def resolve_workspace(project_root):
    """解析工作区 → (AGATE_WORKSPACE, AGATE_TASKS_DIR)。

    优先级：.agate.env(AGATE_WORKSPACE=) → env AGATE_TASKS_DIR → 默认
    {project_root}/agate-workspace。.agate.env 读取 utf-8 + CRLF 剥离（bdd-18 契约），
    取最后一条匹配行。解析器不创建任何目录。
    """
    project_root = str(Path(project_root).resolve())

    ws_value = ""
    env_file = os.path.join(project_root, ".agate.env")
    if os.path.isfile(env_file):
        with open(env_file, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.replace("\r", "")
                if line.startswith("AGATE_WORKSPACE="):
                    ws_value = line[len("AGATE_WORKSPACE="):].rstrip("\n")

    if ws_value:
        workspace = _resolve_abs(project_root, ws_value)
        tasks_dir = os.path.join(workspace, "tasks")
    else:
        env_tasks = os.environ.get("AGATE_TASKS_DIR", "")
        if env_tasks:
            tasks_dir = _resolve_abs(project_root, env_tasks)
            workspace = os.path.dirname(tasks_dir)
        else:
            workspace = os.path.join(project_root, "agate-workspace")
            tasks_dir = os.path.join(workspace, "tasks")
    return workspace, tasks_dir


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    workspace, tasks_dir = resolve_workspace(project_root)
    print(f"AGATE_WORKSPACE={workspace}")
    print(f"AGATE_TASKS_DIR={tasks_dir}")
