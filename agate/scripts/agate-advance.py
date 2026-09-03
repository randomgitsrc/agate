#!/usr/bin/env python3
"""agate-advance.py — 手动/多阶回退引导 CLI（TAG0027 §3.4 D4-A，BDD-10）

用法：
  agate-advance.py [TASK_DIR] [--to {phase}] [--reason {text}]

语义：
  * 不传 --to → 打印当前 phase 的 next/retreat 转移表建议（读 phases.yaml），不动作
  * --to 目标与当前 diff ≥ 2（人工直接跳转，如 P6→P4）→ 提示「diff≥2 须先 PAUSED
    （check-state-transition 会拦截直退）」，引导跑归档 + 置 PAUSED，不自行回退
    （state-machine.md 647-654：人工直跳路径强制 PAUSED）
  * diff = 1（如 P6→P5）→ 等价委托 agate-retreat-to.py 单步（逐阶 diff=1 独立 commit，
    retry 记录同步；retreat-to 自动化与人工直跳不同轨，不触发 PAUSED 拦截）
  * advance 不内联回退实现——只做目标解析 + 合法性提示 + 委托（I-7 复用而非重造）

与 agate-retreat-to.py 边界：advance 是"目标解析 + 合法性提示 + 委托"薄壳；
retreat-to 是既有单步回退自动化（逐阶归档 + retry + 独立 commit）。

平台无关：显式 utf-8；无 /tmp 字面量；解释器一律 sys.executable 子进程。
Python 3.8+（禁 match / str.removeprefix）。
"""

import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    sys.path.insert(0, SCRIPT_DIR)
    from agate_common import read_rules_yaml, resolve_rules_root
except Exception:  # pragma: no cover - 独立副本降级
    read_rules_yaml = None
    resolve_rules_root = None

RETREAT_TO = os.path.join(SCRIPT_DIR, "agate-retreat-to.py")


def _log(msg):
    sys.stderr.write("AGATE ADVANCE: " + msg + "\n")


def _resolve_rules():
    """解析 AGATE_ROOT/rules 目录（同 agate-next：env → 版本链 → 脚本路径上溯）。"""
    if resolve_rules_root is not None:
        try:
            return resolve_rules_root(__file__)
        except Exception:
            pass
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return os.path.join(env_root, "rules")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules")


def _load_phase_table(rules_root):
    """读 phases.yaml → {phase_id: phase_dict}；缺失/解析失败 → {}。"""
    if read_rules_yaml is None:
        return {}
    data = read_rules_yaml(rules_root, "phases")
    if not isinstance(data, dict):
        return {}
    out = {}
    for ph in data.get("phases", []) or []:
        if isinstance(ph, dict) and ph.get("id"):
            out[str(ph["id"])] = ph
    return out


def _read_state_phase(task_dir):
    """读 task_dir/.state.yaml 的 phase；缺失/解析失败 → "". """
    state_file = os.path.join(task_dir, ".state.yaml")
    if not os.path.isfile(state_file) or yaml is None:
        return ""
    try:
        with open(state_file, encoding="utf-8", errors="replace") as fh:
            data = yaml.safe_load(fh)
    except Exception:
        return ""
    if not isinstance(data, dict):
        return ""
    return str(data.get("phase", ""))


def _phase_num(phase):
    """phase 数值（P6.5 → 6；PAUSED/READY/DONE 无数字 → None）。"""
    m = re.search(r"^P([0-9]+(?:\.[0-9]+)?)$", str(phase))
    return float(m.group(1)) if m else None


def _repo_root(task_dir):
    """定位 task_dir 所在 git 仓库根（无仓库 → None）。"""
    try:
        proc = subprocess.run(
            ["git", "-C", task_dir, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    out = (proc.stdout or "").strip()
    return out or None


def _print_table(phase, phases):
    """打印当前 phase 的 next/retreat 转移表建议。"""
    entry = phases.get(phase, {})
    _log(f"当前 phase={phase}；转移表建议：")
    _log(f"  next    = {entry.get('next')!r}（gate exit 0 推进目标 / null = 无自动后继）")
    retreat = entry.get("retreat")
    if retreat is None:
        _log("  retreat = null（gate exit 1 → 重试本阶段，无跨阶回退表值）")
    else:
        _log(f"  retreat = {retreat!r}（gate exit 1 → 委托 agate-retreat-to.py 逐阶回退）")
    if phase == "P6.5":
        sub = entry.get("gate_subphase") if isinstance(entry, dict) else None
        if isinstance(sub, dict):
            _log(f"  gate_subphase: hosted_on={sub.get('hosted_on')} "
                 f"forward_to={sub.get('forward_to')} needs_revision_to={sub.get('needs_revision_to')}")


def main():
    args = sys.argv[1:]
    task_dir = None
    to_phase = None
    reason = ""
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--to":
            if i + 1 >= len(args):
                sys.stderr.write("AGATE ADVANCE: --to 缺目标 phase\n")
                sys.exit(1)
            to_phase = args[i + 1]
            i += 2
        elif a == "--reason":
            if i + 1 >= len(args):
                sys.stderr.write("AGATE ADVANCE: --reason 缺文本\n")
                sys.exit(1)
            reason = args[i + 1]
            i += 2
        else:
            task_dir = a
            i += 1
    if task_dir is None:
        task_dir = os.getcwd()

    current = _read_state_phase(task_dir)
    if not current:
        sys.stderr.write(f"AGATE ADVANCE: {os.path.join(task_dir, '.state.yaml')} 缺失/无 phase\n")
        sys.exit(1)

    rules_root = _resolve_rules()
    phases = _load_phase_table(rules_root)

    if to_phase is None:
        _print_table(current, phases)
        sys.exit(0)

    cur_num = _phase_num(current)
    tgt_num = _phase_num(to_phase)
    if cur_num is None or tgt_num is None:
        _log(f"当前 phase={current} 或目标 phase={to_phase} 不是 P0-P8/P6.5 形态")
        sys.exit(0)
    if tgt_num >= cur_num:
        _log(f"目标 {to_phase} 不低于当前 {current}——这不是回退（advance 只引导回退）")
        sys.exit(0)

    diff = cur_num - tgt_num
    if diff >= 2:
        # 人工直接跳转 diff≥2 → 强制 PAUSED 引导（state-machine.md 647-654），不自行回退
        _log(
            f"diff={int(diff)} ≥ 2（{current} → {to_phase}）人工直接跳转须先 PAUSED："
            "check-state-transition 会拦截直退。请先落盘 gate-diagnosis + 置 PAUSED，"
            "人工批准后再恢复目标阶段（逐阶回退请用 --to 相邻阶段多次，或走 agate-retreat-to.py 自动化逐阶）。"
        )
        _log("不自行改 phase（拦截为 PAUSED 引导，非表内直退）")
        sys.exit(0)

    # diff == 1 → 等价委托 agate-retreat-to.py 单步（retry 记录同步 + 独立 commit）
    reason = reason or "agate advance 按转移表单步回退"
    repo_root = _repo_root(task_dir)
    _log(f"diff=1（{current} → {to_phase}）→ 委托 agate-retreat-to.py 单步回退")
    try:
        proc = subprocess.run(
            [sys.executable, RETREAT_TO, task_dir, to_phase, reason],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_root or None,
        )
        rc = proc.returncode
        out = (proc.stdout or "") + (proc.stderr or "")
    except OSError as exc:
        rc = 127
        out = f"subprocess 启动失败: {exc}"
    if out:
        for line in out.splitlines()[:10]:
            _log("  " + line.strip())
    if rc != 0:
        _log(f"agate-retreat-to.py 返回 {rc}——单步回退未完成，见上方输出")
        sys.exit(rc)
    sys.exit(0)


if __name__ == "__main__":
    main()
