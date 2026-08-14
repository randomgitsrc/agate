#!/usr/bin/env python3
"""check-state-transition.py — 状态转移合法性检查（Phase 2A: P2.3-P2.5）

从 check-state-transition.sh 迁移（TAG0010 批次 2b）。CLI 契约与 sh 版等价：
  check-state-transition.py [STATE_FILE]   # 默认 .state.yaml
exit 0 = 合法; exit 1 = 非法

P2.3 phase 跳变合法性
P2.4 重试超限 -> phase 必须是 PAUSED（按阶段差异化 MAX）
P2.5 回退跳变 >= 2 -> 强制 PAUSED（恢复 exit 1，T019 教训）

迁移说明：MAX_RETRY_MAP 从 agate_common 导入（单一数据源，环境变量覆盖仍有效）；
git show | agate-state-get.py phase_stdin 管道 → run_git + sys.executable subprocess
（stdin 传入，$(...) 剥尾换行 → .rstrip("\n")）；git diff --cached 的 tr -d '\r' 剥离 →
逐行 .rstrip("\r")；grep -oE 提取首个数字 → 正则等价。
"""

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from agate_common import MAX_RETRY_MAP as _DEFAULT_MAX_RETRY_MAP, run_git
except ImportError:
    _DEFAULT_MAX_RETRY_MAP = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"
    run_git = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGATE_STATE_GET = os.path.join(SCRIPT_DIR, "agate-state-get.py")

MAX_RETRY_MAP = os.environ.get("MAX_RETRY_MAP", _DEFAULT_MAX_RETRY_MAP)

_STALE_OUTPUTS = {
    "P1": ["P1-requirements.md", "P1-review.md"],
    "P2": ["P2-design.md", "P2-review.md"],
    "P6": ["P6-acceptance.md"],
    "P7": ["P7-consistency.md"],
}


def _run_state_get(args, env, input_text=None):
    """调 agate-state-get.py（等价 sh 的 python3 ... 2>/dev/null || echo ""；
    $(...) 剥尾换行 → .rstrip("\n")）。"""
    try:
        proc = subprocess.run(
            [sys.executable, AGATE_STATE_GET] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env, input=input_text,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").rstrip("\n")


def get_old_phase(state_file, state_basename):
    """HEAD 版本（commit 前旧版本）。任务级 .state.yaml 用 git ls-files 取仓库规范
    相对路径（TAG0003 v2.0 去硬编码，不用 realpath --relative-to——Git for Windows
    的 --show-toplevel 返回 C:/... 而 realpath -m 返回 /c/...，混用会算错路径致
    git show 失败）。git show 失败回退空。"""
    if run_git is None:
        return ""
    git_path = state_basename
    state_dir = str(Path(os.path.dirname(state_file)).resolve())
    rc, repo_root = run_git(["rev-parse", "--show-toplevel"], cwd=state_dir)
    repo_root = repo_root.rstrip("\n").strip() if rc == 0 else ""
    cwd = repo_root or None
    if repo_root:
        rc, tracked = run_git(["ls-files", "--full-name", "--", state_file], cwd=repo_root)
        first = tracked.splitlines()[0].rstrip("\r") if tracked.splitlines() else ""
        if first:
            git_path = first
    rc, shown = run_git(["show", "HEAD:" + git_path], cwd=cwd)
    if rc != 0:
        return ""
    env = dict(os.environ)
    return _run_state_get(["phase_stdin"], env, input_text=shown)


def get_new_phase(state_file):
    """当前暂存版本 phase；文件不存在回退空。"""
    if not os.path.isfile(state_file):
        return ""
    env = dict(os.environ)
    env["STATE_FILE"] = state_file
    return _run_state_get(["phase"], env)


def phase_num(text):
    """提取首个数字序列；无匹配回退 0（同 sh grep -oE '[0-9]+' || echo "0"）。"""
    m = re.search(r"[0-9]+", text)
    return int(m.group(0)) if m else 0


def _find_stale(old_phase, task_dir):
    """检查被跨过阶段的自撰产出是否仍在原位（列表须与
    agate-archive-stale-outputs.py 的 _OUTPUTS 保持一致）。"""
    for name in _STALE_OUTPUTS.get(old_phase, []):
        if os.path.isfile(os.path.join(task_dir, name)):
            return name
    return ""


def main():
    state_file = sys.argv[1] if len(sys.argv) > 1 else ".state.yaml"
    state_basename = os.path.basename(state_file)

    # 只在 .state.yaml 有暂存变更时检查
    # tr -d '\r'：Git for Windows 的 diff 输出文件名可能带 CRLF 行尾，grep -qF 精确匹配会失败
    if run_git is None:
        sys.exit(0)
    rc, name_only = run_git(["diff", "--cached", "--name-only"])
    if rc != 0:
        sys.exit(0)
    lines = [line.rstrip("\r") for line in name_only.splitlines()]
    if not any(state_basename in line for line in lines):
        sys.exit(0)

    old_phase = get_old_phase(state_file, state_basename)
    new_phase = get_new_phase(state_file)

    if new_phase in ("", "PAUSED", "READY", "DONE"):
        sys.exit(0)

    old_num = phase_num(old_phase)
    new_num = phase_num(new_phase)

    # 检查 1：回退跳变 >= 2（T019 教训）
    # 协议规定"不依赖 commit message 格式"（state-machine.md L371-373）
    # .gate-history.jsonl 的 PAUSED 验证功能已被 HEAD/staged diff 机制隐式覆盖
    # （PAUSED 单独 commit 时 HEAD=PAUSED → 早退 exit 0）
    # 保留 old_num > 0 守卫：PAUSED→Pn 恢复（old_num=0）不被误拦
    if old_num > 0 and new_num > 0:
        diff = old_num - new_num
        if diff >= 2:
            sys.stderr.write(
                "GATE STATE: 回退跳变 P{}→P{}（差 {}），强制 PAUSED\n".format(old_num, new_num, diff)
            )
            sys.exit(1)

    # 检查 2：重试超限（P2.4，按阶段差异化 MAX）
    # .state.yaml 的 retries[Pn] 是列表（每次重试一个对象），不是整数
    # 按 retries dict 的 key 逐阶段查 MAX_RETRY，不是按 new_phase
    if os.path.isfile(state_file):
        env = dict(os.environ)
        env["STATE_FILE"] = state_file
        retries_json = _run_state_get(["retries_over", MAX_RETRY_MAP], env)

        if retries_json and new_phase != "PAUSED":
            sys.stderr.write("GATE STATE: {}，phase 应为 PAUSED\n".format(retries_json))
            sys.exit(1)

    # 检查 4：回退时若被跨过阶段是 self-authored 产出阶段（P1/P2/P6/P7），
    # 且该阶段的产出文件仍在原位（未归档）-> 拦截，要求先跑 agate-archive-stale-outputs.py
    # （self-authored gate 产出不能跨重试静默复用，见 LIMITATIONS.md self-authored 分类）
    if old_num > 0 and new_num > 0:
        diff = old_num - new_num
        if diff == 1 and old_phase in _STALE_OUTPUTS:
            task_dir = os.path.dirname(state_file)
            stale_found = _find_stale(old_phase, task_dir)
            if stale_found:
                sys.stderr.write(
                    "GATE STATE: 回退 P{}->P{}，但 {} 的自撰产出（{}）仍在原位\n".format(
                        old_num, new_num, old_phase, stale_found
                    )
                )
                sys.stderr.write(
                    "  退回前须先跑：bash agate/scripts/agate-archive-stale-outputs.sh {} {}\n".format(
                        old_phase, task_dir
                    )
                )
                sys.stderr.write(
                    "  （self-authored gate 产出不能跨重试静默复用，见 LIMITATIONS.md self-authored 分类）\n"
                )
                sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
