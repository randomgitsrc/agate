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
- 版本解析（TAG0008）：resolve_version_root（四层，agate-resolve/summary 用）/
  resolve_hook_root（hook 入口用，返回 warnings）/ _find_project_declaration（.agate-version 向上查找）

约定：所有文本读写显式 encoding="utf-8"；pyyaml 缺失时 fail-closed（同
agate-state-get.py）。Python 3.8+（禁 match / str.removeprefix）。
"""

import hashlib
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


def is_gate_meta_key(key):
    """gate_commands key 是否为元信息 key（非待执行命令）（DEBT0010/TAG0017）。

    仅精确匹配两个已知固定后缀 `_formatter` / `_timeout_seconds`，不做通配/正则
    宽松匹配（P1 R3 风险条目：防止把真正需要核实/计入的 key 一并放宽排除）。
    供 agate-read-gate-commands.py / agate-gate-missing-cmds.py /
    agate-gate-p5-count.py / agate-read-p5-commands.py 共用（P2-design.md §1.1）。
    """
    return key.endswith(("_formatter", "_timeout_seconds"))


# ---------- 版本解析（TAG0008，resolve-chain 批次） ----------
# 四层解析语义（P2-design.md §4.1）：
#   env 最高 → 项目声明（.agate-version，asdf 模式 cwd 向上）→ current/latest 指针链
#   → legacy 软链兜底（或脚本路径上溯，视调用方）。current/latest 为文本指针
#   （内容 = 目标名），Windows 复制模式指针形态；版本目录存在即视为已安装。

_AGATE_VERSION_RE = re.compile(r"^\s*agate\s*:\s*(v[0-9]+\.[0-9]+\.[0-9]+)\s*$")


def _find_project_declaration(start_dir=None):
    """cwd 向上找 .agate-version（asdf 模式，BDD-10）。

    返回 (status, version)：status ∈ {"none"（无文件）、"invalid"（文件格式非法）、
    "ok"（合法声明）}；version 仅 ok 时非空。非法格式（含空文件/未知前缀）→ invalid
    （BDD-14）。
    """
    d = os.path.abspath(start_dir) if start_dir else os.path.abspath(os.getcwd())
    while True:
        vf = os.path.join(d, ".agate-version")
        if os.path.isfile(vf):
            try:
                with open(vf, encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                content = ""
            m = _AGATE_VERSION_RE.match(content)
            if m:
                return "ok", m.group(1)
            return "invalid", None
        parent = os.path.dirname(d)
        if parent == d:
            return "none", None
        d = parent


def _resolve_pointer_chain(base, name, seen=None):
    """current/latest 指针链解析：目录即根；软链 readlink 目标名继续追；文本指针内容=目标名继续追；防环。

    兼容目录即版本根（无指针时的直接版本目录）、POSIX 软链指针（`os.symlink`）与
    文本指针（Windows-safe）三种形态。先判 `os.path.islink` 再判 `os.path.isdir`——
    软链指向版本目录时 `isdir` 恒为 True，若先判 isdir 会把软链路径自身当终态
    （返回 "current"/"latest" 而非实际版本目录名），导致版本号解析/指针修复失效。
    """
    if seen is None:
        seen = set()
    if not name or name in seen:
        return None
    seen.add(name)
    p = os.path.join(base, name)
    if os.path.islink(p):
        try:
            target = os.readlink(p)
        except OSError:
            return None
        if not target or target in seen:
            return None
        if os.path.isabs(target):
            t = os.path.normpath(target)
            if os.path.isdir(t):
                return t
            return _resolve_pointer_chain(base, t, seen)
        return _resolve_pointer_chain(base, target, seen)
    if os.path.isdir(p):
        return p
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            content = f.read().replace("\r", "").strip()
    except OSError:
        return None
    if not content or content == name:
        return None
    return _resolve_pointer_chain(base, content, seen)


def _resolve_version_info(start_dir=None, use_legacy=True):
    """版本解析核心：env → 项目声明 → current 链 → legacy 软链兜底。

    返回 dict {root, version, reason, warnings}。root 为 None = 终态失败（调用方须
    fail-closed）。env 覆盖返回 env 原值（不 resolve，与既有契约一致，兼容字面盘符路径）。
    声明未安装 / 格式非法 → warnings 加警告 + 回退 current（绝不静默禁用，BDD-13/14）。
    """
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return {"root": env_root, "version": "", "reason": "AGATE_ROOT 环境变量覆盖", "warnings": []}

    base = os.path.expanduser("~/.agate")
    warnings = []
    status, declared = _find_project_declaration(start_dir)
    if status == "ok":
        vdir = os.path.join(base, declared)
        if os.path.isdir(vdir):
            return {"root": vdir, "version": declared, "reason": "引用 .agate-version", "warnings": warnings}
        warnings.append(f"警告: .agate-version 声明的版本 {declared} 未安装，回退全局 current")
    elif status == "invalid":
        warnings.append("警告: .agate-version 格式非法（应为 agate: vX.Y.Z），回退全局 current")

    cur = _resolve_pointer_chain(base, "current")
    if cur:
        return {"root": cur, "version": os.path.basename(cur), "reason": "全局 current", "warnings": warnings}

    if use_legacy and os.path.islink(base):
        return {"root": os.path.realpath(base), "version": "", "reason": "legacy 软链布局（无版本指针）", "warnings": warnings}

    return {"root": None, "version": None, "reason": "无可用 AGATE_ROOT", "warnings": warnings}


def resolve_version_root(start_dir=None):
    """版本解析四层（env → 项目声明 → current 链 → legacy 软链兜底）。

    供 agate-resolve.py / agate-summary.py 复用（P2 §4.1/§4.6）。root 为 None =
    终态失败（调用方 fail-closed，exit 非 0）。
    """
    return _resolve_version_info(start_dir=start_dir, use_legacy=True)


def resolve_hook_root(script_path):
    """hook 解析入口（resolve-entry.py）用：env → 项目声明 → current 链 → 脚本路径上溯兜底。

    返回 (root, warnings)。root 恒非空（脚本路径上溯 + 复制模式 .agate-root 标记恢复兜底，
    兼容既有 hook 自定位契约），调用方再校验 gate 脚本存在（fail-closed）。
    """
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return env_root, []
    info = _resolve_version_info(use_legacy=False)
    if info["root"]:
        return info["root"], info["warnings"]
    real = str(Path(script_path).resolve())
    agate_root = os.path.dirname(os.path.dirname(real))
    if not os.path.isdir(os.path.join(agate_root, "scripts")):
        marker = os.path.join(os.path.dirname(real), ".agate-root")
        if os.path.isfile(marker):
            with open(marker, encoding="utf-8") as f:
                content = f.read().replace("\r", "").strip()
            if content:
                return content, info["warnings"]
    return agate_root, info["warnings"]


def resolve_agate_root(script_path):
    """解析 AGATE_ROOT：env 优先 → 项目版本解析（.agate-version / current 链）→
    软链 readlink 上溯 → 复制模式 .agate-root 标记恢复。

    AGATE_ROOT 环境变量优先（返回原值）。项目声明命中已安装版本或全局 current 指针链
    命中时返回版本根；否则回退既有脚本路径上溯语义（做加法不改既有契约）。
    """
    root, _warnings = resolve_hook_root(script_path)
    return root


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


# ---------- 事件账本（TAG0020：P6.5 独立 Judge 机制） ----------
# append-only 哈希链账本 gate-events.jsonl（P2-design §3.2）：每行 JSON 事件，
# prev_hash = sha256(上一行原始文本 UTF-8).hexdigest()，首行 = GENESIS_HASH。
# append_event 是唯一写路径（hook/gate 统一走它）；check-events.py 审计链完整性。
GENESIS_HASH = hashlib.sha256(b"").hexdigest()


def append_event(task_dir, event):
    """向 {task_dir}/gate-events.jsonl 追加一条事件（append-only 哈希链账本）。

    - 自动补 ts（UTC ISO8601 微秒）与 prev_hash：首行 = GENESIS_HASH，
      后续行 = sha256(上一行原始文本 UTF-8).hexdigest()（行间哈希链，防改写）
    - ts 单调兜底：尾行 ts 晚于当前时刻时沿用尾行 ts（同格式字符串比较，
      保证单调不减；check-events 判定用 <= 放宽微秒精度，P2 R7）
    - 文件不存在/为空 → 直接写首事件（prev_hash = GENESIS_HASH）
    - 失败（IOError 等）→ stderr WARNING 不抛：gate 主判定不依赖写账本成功，
      账本审计是辅助防线（P2-design §3.2；judge_verdict 事件写入失败也仅告警）
    """
    try:
        path = os.path.join(task_dir, "gate-events.jsonl")
        prev_hash = GENESIS_HASH
        tail_ts = None
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    raw_lines = f.read().splitlines()
            except OSError:
                raw_lines = []
            if raw_lines:
                # 链始终接续到文件尾行原始文本（即使尾行 JSON 损坏，防改写链不破）
                prev_hash = hashlib.sha256(raw_lines[-1].encode("utf-8")).hexdigest()
                try:
                    tail_ts = json.loads(raw_lines[-1]).get("ts")
                except Exception:
                    tail_ts = None
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        ts = now_ts
        if tail_ts and tail_ts > now_ts:
            ts = tail_ts
        row = dict(event)
        row.pop("prev_hash", None)
        row["ts"] = ts
        row["prev_hash"] = prev_hash
        line = json.dumps(row, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as exc:
        sys.stderr.write(
            f"agate_common: append_event WARNING: 账本事件写入失败（不阻断主判定）: {exc}\n"
        )


def read_judge_verdict(task_dir):
    """解析 {task_dir}/P6.5-judge-verdict.md 的 frontmatter（--- 块）。

    返回 dict {status, criteria_total, criteria_passed, verdict_evidence, partial}；
    文件缺失 / 无 frontmatter / 解析失败 → None（调用方按缺失处理，fail-closed）。
    partial 为可选降级标记字段：缺省 False（BDD-5 必需字段仅
    status/criteria_total/criteria_passed/verdict_evidence 四项）。
    """
    path = os.path.join(task_dir, "P6.5-judge-verdict.md")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return {
        "status": data.get("status"),
        "criteria_total": data.get("criteria_total"),
        "criteria_passed": data.get("criteria_passed"),
        "verdict_evidence": data.get("verdict_evidence"),
        "partial": bool(data.get("partial", False)),
    }


def read_vision_tri_state(p1_file):
    """读取 P1-requirements.md 声明的能力三态（available/supplementable/GAP）中的视觉条目状态。

    TAG0006（DEBT0005）统一解析：capability_requirements yaml 代码围栏块内
    need/name 含 visual|vision 的条目，其 status 即该任务的视觉能力声明。
    返回该 status 字符串；文件不存在 / 无视觉条目 / 解析失败 → 返回 None
    （调用方按"无声明默认 available 语义"处理——TAG0006 P2 §2.8 兼容回归锚点）。
    平台无关：纯文件文本解析，无路径/进程假设，gate/P6 多脚本复用同一口径。
    """
    if not os.path.isfile(p1_file):
        return None
    try:
        with open(p1_file, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None
    for m in re.finditer(r"```(?:yaml|yml)\s*\n(.*?)```", text, re.DOTALL):
        try:
            data = yaml.safe_load(m.group(1))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        reqs = data.get("capability_requirements")
        if not isinstance(reqs, list):
            continue
        for item in reqs:
            if not isinstance(item, dict):
                continue
            need = item.get("need") or item.get("name")
            if need and re.search(r"visual|vision", str(need), re.IGNORECASE):
                return item.get("status")
    return None


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


# ---------- M1 对账（TAG0021，BDD-6/7；P2-design §3.4） ----------
# 双跑对账：现行 grep/md 读取路径（保退出码语义 0/2 不变，不新增阻断）+ 结构化读取路径
# （frontmatter YAML / rules/*.yaml 声明）对比。差异可观测出口（BDD-6）：
#   stderr `RECONCILE WARNING: <op> <field>: grep=<grep_val> structured=<structured_val>` +
#   `RECONCILE SUMMARY: N mismatches across M fields`（可重定向进日志、可计数审计）。
# 开关：AGATE_RECONCILE 缺省 on（CI/批处理可设 off/0/false 降噪，P2-design §3.4）。
# 归一化口径（R10）：与 agate-md-field-get 的 BOOL/LIST 归一化一致（list 空格连接、
# bool 小写）；正文内联/块式 list 与 frontmatter list 语义等价 → 0 差异（P3 BDD-8）。
# 对账是叠加层：任何异常/失败均不阻断调用方原判定（fail-open），对账计数不改变退出码。

_RECONCILE_MISMATCHES = 0
_RECONCILE_FIELDS = 0

_RECONCILE_OFF_VALUES = frozenset({"", "0", "off", "false", "no", "disable"})


def reconcile_enabled():
    """对账开关：AGATE_RECONCILE 缺省 on；显式关闭值（off/0/false/no/空）才关闭。"""
    return os.environ.get("AGATE_RECONCILE", "1").strip().lower() not in _RECONCILE_OFF_VALUES


def _reconcile_norm(value):
    """对账归一化：str 化 + 剥首尾空白 + 折叠内部空白（list 空格连接后统一）。"""
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def reconcile_field(op, field, grep_val, structured_val):
    """字段级对账（BDD-6）：grep/md 读取值 vs 结构化读取值不一致 → stderr WARNING + 计数。

    返回 True=一致 / False=不一致。对账不改变调用方退出码语义（原判定 0/2 不变）；
    对账关闭时不做任何输出并恒返回 True。
    """
    global _RECONCILE_MISMATCHES, _RECONCILE_FIELDS
    if not reconcile_enabled():
        return True
    _RECONCILE_FIELDS += 1
    if _reconcile_norm(grep_val) != _reconcile_norm(structured_val):
        _RECONCILE_MISMATCHES += 1
        sys.stderr.write(
            "RECONCILE WARNING: %s %s: grep=%s structured=%s\n"
            % (op, field, str(grep_val), str(structured_val))
        )
        return False
    return True


def reconcile_summary():
    """对账汇总行（BDD-6）：`RECONCILE SUMMARY: N mismatches across M fields`。"""
    if not reconcile_enabled():
        return
    sys.stderr.write(
        "RECONCILE SUMMARY: %d mismatches across %d fields\n"
        % (_RECONCILE_MISMATCHES, _RECONCILE_FIELDS)
    )


def read_rules_yaml(rules_root, name):
    """读 {rules_root}/{name}.yaml（pyyaml）；缺失/解析失败 → None（调用方按数据缺失处理）。"""
    path = os.path.join(rules_root, name + ".yaml")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except Exception:  # noqa: BLE001  YAML 解析失败按缺失降级（对账不阻断）
        return None


def resolve_rules_root(script_path):
    """解析 AGATE_ROOT 协议根下 rules/ 目录（env → 版本链 → 脚本路径上溯兜底）。

    与 check-structure-consistency._resolve_root 同口径：env AGATE_ROOT 优先（返回原值），
    否则 agate_common 版本解析（resolve_agate_root），失败回退脚本路径上溯。
    """
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        root = env_root
    else:
        try:
            root = resolve_agate_root(script_path)
        except Exception:  # noqa: BLE001  agate_common 不可用时兜底脚本路径上溯
            root = os.path.dirname(os.path.dirname(os.path.abspath(script_path)))
    return os.path.join(root, "rules")


_DEFAULT_PHASE_IDS = frozenset({"P0", "P1", "P2", "P3", "P4", "P5", "P6", "P6.5", "P7", "P8"})


def known_phase_ids(rules_root):
    """已知阶段 id 集：phases.yaml phases[].id ∪ 内置 {P0..P8, P6.5}（YAML 缺失回退内置）。"""
    phases = read_rules_yaml(rules_root, "phases")
    if isinstance(phases, dict) and isinstance(phases.get("phases"), list):
        ids = {str(p.get("id")) for p in phases["phases"] if isinstance(p, dict) and p.get("id")}
        if ids:
            return ids
    return _DEFAULT_PHASE_IDS


def is_legal_gate_key(key, phase_ids=None):
    """gate_commands key 合法性（P2-review 发现 #3 + 阶段集约束）。

    合法 = project_module 特判 / is_gate_meta_key（`_formatter`/`_timeout_seconds` 后缀）/
    裸或带自定义后缀的 `P{阶段}` 键（阶段 ∈ phases.yaml id ∪ 内置 P0-P8）。未声明 key
    （如 P9_custom——P9 非合法阶段）→ False → 对账 WARNING（BDD-6/7）。
    """
    if key == "project_module":
        return True
    if is_gate_meta_key(key):
        return True
    if phase_ids is None:
        phase_ids = _DEFAULT_PHASE_IDS
    m = re.match(r"^P([0-9]+(?:\.[0-9]+)?)(?:_[A-Za-z0-9_]*)?$", key)
    return bool(m) and ("P" + m.group(1)) in phase_ids


def split_frontmatter(text):
    """拆 frontmatter 块与正文：返回 (fm_dict_or_None, body_text)。

    只认文件头 `---` 块（与 agate-md-field-get._read_frontmatter 同规则）；
    无块 / 解析失败 → (None, 原文本)（正文含全部文本，供 grep 侧读取）。
    """
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end < 0:
        return None, text
    fm_text = text[4:end]
    body = text[end + 4:]
    try:
        fm = yaml.safe_load(fm_text)
    except Exception:  # noqa: BLE001  解析失败按无 frontmatter 降级
        fm = None
    return fm, body


def _body_scalar_value(body, pattern):
    """正文标量字段 grep 值（pattern 须含一个捕获组）；无匹配 → ""。"""
    m = re.search(pattern, body)
    return m.group(1).strip() if m else ""


def _body_list_value(body, field):
    """正文 list 字段 grep 值（与 agate-md-field-get._regex_list 同归一化：空格连接）。

    兼容内联 `[a, b, c]` 与块式 `- item` 两种形态；无匹配 → ""。
    """
    m = re.search(re.escape(field) + r":\s*\[([^\]]+)\]", body)
    if m:
        items = [p.strip() for p in m.group(1).split(",") if p.strip()]
        return " ".join(items)
    m = re.search(re.escape(field) + r":\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)", body)
    if m:
        items = re.findall(r"-\s+(\S+)", m.group(1))
        return " ".join(items)
    return ""


def body_field_value(body, field):
    """正文 grep 字段值（与 agate-md-field-get._regex_fallback 同归一化口径）。

    list 字段（phases/packages/domains）空格连接、bool（ui_affected）小写、标量原值。
    """
    if field in ("phases", "packages", "domains"):
        return _body_list_value(body, field)
    if field == "ui_affected":
        return _body_scalar_value(body, r"ui_affected:\s*(true|false)")
    if field == "candidate_count":
        return _body_scalar_value(body, r"candidate_count:\s*(\d+)")
    if field == "risk_level":
        return _body_scalar_value(body, r"risk_level:\s*(low|medium|high)")
    return ""


def fm_field_value(fm, field):
    """frontmatter 结构化字段值（与 agate-md-field-get._format_value 同归一化口径）。

    list 空格连接 / bool（ui_affected）小写 / 其余 str 化；字段缺失或 null → ""。
    """
    if not isinstance(fm, dict) or field not in fm or fm[field] is None:
        return ""
    val = fm[field]
    if field in ("phases", "packages", "domains"):
        return " ".join(str(v) for v in val) if isinstance(val, list) else str(val)
    if field == "ui_affected":
        return str(val).lower()
    return str(val)


# ---------- M2 共享解析（TAG0021，BDD-9；P2-design §3.4/§3.5 M2-1） ----------
# 已迁移解析点（P1 §4.1 A 组四字段行正则 + B 组 gate_commands 块正则）从三消费脚本
# （agate-read-gate-commands / check-pruning / check-gate）抽到公共库单点：BDD-9 要求
# 这些已迁移模式在消费脚本源码中字面命中数 = 0，共享解析落在 agate_common（不在
# _MIGRATED_SCRIPTS 扫描清单内）。行为与原内联实现逐字节等价：
#   * gate_commands 块只认列 0 的 `gate_commands:` 标题行 + 二空格缩进的 `key: value` 行
#     （空行吞入块边界，与既有 5 处同源实现的块正则一致）
#   * 四字段计数 = 全文（frontmatter + 正文）列 0 声明行数（`^(packages|domains|
#     ui_affected|gate_commands):`），与 check-gate.py P2 分支既有计数语义一致

_GATE_COMMANDS_BLOCK_RE = re.compile(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", re.MULTILINE)
_GATE_KEY_LINE_RE = re.compile(r"^  (\w+):\s*(.+)$", re.MULTILINE)
_P2_FIELD_LINE_RE = re.compile(r"^(packages|domains|ui_affected|gate_commands):")


def parse_gate_commands_block(text):
    """解析 gate_commands 多行块 → (has_block, [(key, value), ...])。

    M2 起 agate-read-gate-commands.py / check-gate.py 共用（BDD-9：块正则不在消费脚本
    字面出现，落在公共库单点，防"同一规则多处实现"漂移）。无块/空块 → (False, [])。
    """
    if not text.endswith("\n"):
        text += "\n"
    m = _GATE_COMMANDS_BLOCK_RE.search(text)
    if not m:
        return False, []
    return True, _GATE_KEY_LINE_RE.findall(m.group(1))


def count_p2_declared_fields(text):
    """统计 P2 四字段（packages/domains/ui_affected/gate_commands）声明行数（列 0 匹配）。

    M2 起 check-gate.py P2 分支用（BDD-9：四字段行正则不在消费脚本字面出现）。
    语义与原内联 `sum(1 for line in text.splitlines() if re.match(...))` 等价——
    frontmatter 与正文都算（真实 P2-design.md 四字段散落两处）。
    """
    return sum(1 for line in text.splitlines() if _P2_FIELD_LINE_RE.match(line))


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    workspace, tasks_dir = resolve_workspace(project_root)
    print(f"AGATE_WORKSPACE={workspace}")
    print(f"AGATE_TASKS_DIR={tasks_dir}")
