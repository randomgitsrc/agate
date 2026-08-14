#!/usr/bin/env python3
"""agate-retreat-to.py — 自动化多步单向回退（每一步仍是独立、真实、受 gate 校验的 commit）

从 agate-retreat-to.sh 迁移（TAG0010 批次 2b）。CLI 契约与 sh 版等价：
  agate-retreat-to.py TASK_DIR TARGET_PHASE "诊断原因"
exit 0 = 回退完成; exit 1 = 任一步失败

迁移说明：MAX_RETRY_MAP 从 agate_common 导入（单一数据源，环境变量覆盖仍有效）；
grep -vE '^${TASK_DIR#./}/' → startswith 前缀判定（路径为字面前缀，等价安全）；
agate-archive-stale-outputs.py / agate-retreat-state.py / agate-state-get.py 子进程 →
sys.executable subprocess（归档依赖已在批次 1b py 化）。
"""

import contextlib
import os
import re
import subprocess
import sys

try:
    from agate_common import MAX_RETRY_MAP as _DEFAULT_MAX_RETRY_MAP
except ImportError:
    _DEFAULT_MAX_RETRY_MAP = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGATE_STATE_GET = os.path.join(SCRIPT_DIR, "agate-state-get.py")
AGATE_RETREAT_STATE = os.path.join(SCRIPT_DIR, "agate-retreat-state.py")
AGATE_ARCHIVE = os.path.join(SCRIPT_DIR, "agate-archive-stale-outputs.py")

MAX_RETRY_MAP = os.environ.get("MAX_RETRY_MAP", _DEFAULT_MAX_RETRY_MAP)


def phase_num(text):
    """提取首个数字序列；无匹配回退空串（同 sh grep -oE '[0-9]+' || echo ""）。"""
    m = re.search(r"[0-9]+", text)
    return m.group(0) if m else ""


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        sys.stderr.write("用法: agate-retreat-to.py TASK_DIR TARGET_PHASE REASON\n")
        sys.exit(1)
    task_dir = args[0]
    target_phase = args[1]
    reason = args[2]
    state_file = os.path.join(task_dir, ".state.yaml")

    if not os.path.isfile(state_file):
        sys.stderr.write(f"GATE RETREAT: {state_file} 不存在\n")
        sys.exit(1)

    env = dict(os.environ)
    env["STATE_FILE"] = state_file
    try:
        proc = subprocess.run(
            [sys.executable, AGATE_STATE_GET, "phase"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        sys.exit(1)
    if proc.returncode != 0:
        sys.exit(proc.returncode)
    current_phase = (proc.stdout or "").rstrip("\n")

    cur_num = phase_num(current_phase)
    tgt_num = phase_num(target_phase)

    if not cur_num or not tgt_num:
        sys.stderr.write(
            f"GATE RETREAT: 当前 phase（{current_phase}）或目标 phase（{target_phase}）不是合法的 P0-P8\n"
        )
        sys.exit(1)
    if int(tgt_num) >= int(cur_num):
        sys.stderr.write(
            f"GATE RETREAT: 目标 phase（{target_phase}）不低于当前 phase（{current_phase}），这不是回退\n"
        )
        sys.exit(1)

    # 预检查 A：暂存区不能有 TASK_DIR 之外的内容——下面的 commit 会用 pathspec 限定到
    # TASK_DIR，但如果暂存区本来就有无关文件，容易让人误以为它们也被这次 retreat 处理了
    # （其实只是继续留在暂存区，状态含糊）。提前报错比事后困惑更清楚。
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        proc = None
    outside_staged = []
    if proc is not None and proc.returncode == 0:
        prefix = (task_dir[2:] if task_dir.startswith("./") else task_dir) + "/"
        for raw_line in (proc.stdout or "").splitlines():
            line = raw_line.rstrip("\r")
            if line and not line.startswith(prefix):
                outside_staged.append(line)
    if outside_staged:
        sys.stderr.write(
            "GATE RETREAT: 暂存区含 TASK_DIR 之外的文件，请先处理（commit 或 unstage）再重试：\n"
        )
        for line in outside_staged:
            sys.stderr.write(f"  {line}\n")
        sys.exit(1)

    # 预检查 B：一次性查完路径上每一阶退回后的 retry 是否超限，避免半退到一半卡在中间
    check_env = dict(env)
    check_env["CUR"] = cur_num
    check_env["TGT"] = tgt_num
    try:
        proc = subprocess.run(
            [sys.executable, AGATE_RETREAT_STATE, "check_retreat", MAX_RETRY_MAP],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=check_env,
        )
    except OSError:
        sys.exit(1)
    if proc.returncode != 0:
        sys.exit(proc.returncode)
    check_result = (proc.stdout or "").rstrip("\n")
    if check_result:
        parts = check_result.split(":")
        bad_phase = parts[0] if len(parts) > 0 else ""
        would_be = parts[1] if len(parts) > 1 else ""
        limit = parts[2] if len(parts) > 2 else ""
        sys.stderr.write(
            f"GATE RETREAT: 路径上 {bad_phase} 退回后 retry 将达到 {would_be}（MAX={limit}），超限——不执行任何一步，"
            "直接转 PAUSED 问人类\n"
        )
        sys.exit(1)

    # 逐步执行：每一步都是独立的归档 + phase 更新 + retry+1 + 真实 git commit
    n = int(cur_num)
    target_n = int(tgt_num)
    steps = 0
    while n > target_n:
        nxt = n - 1
        old_p = f"P{n}"
        new_p = f"P{nxt}"

        try:
            rc = subprocess.run(
                [sys.executable, AGATE_ARCHIVE, old_p, task_dir]
            ).returncode
        except OSError:
            sys.exit(1)
        if rc != 0:
            sys.exit(rc)

        write_env = dict(env)
        write_env["NEW_PHASE"] = new_p
        write_env["RETREAT_REASON"] = reason
        try:
            rc = subprocess.run(
                [sys.executable, AGATE_RETREAT_STATE, "write_retreat"],
                env=write_env,
            ).returncode
        except OSError:
            sys.exit(1)
        if rc != 0:
            sys.exit(rc)

        with contextlib.suppress(OSError):
            subprocess.run(["git", "add", task_dir], capture_output=True)

        commit_msg = f"retreat: {old_p} -> {new_p}（诊断：{reason}）"
        try:
            rc = subprocess.run(
                ["git", "commit", "-qm", commit_msg, "--", task_dir]
            ).returncode
        except OSError:
            sys.exit(1)
        if rc != 0:
            sys.stderr.write(
                f"GATE RETREAT: {old_p} -> {new_p} 的 commit 未通过 pre-commit hook 校验，已停在 {old_p}\n"
            )
            sys.exit(1)

        sys.stdout.write(f"GATE RETREAT: {old_p} -> {new_p} 已提交（诊断：{reason}）\n")
        n = nxt
        steps += 1

    sys.stdout.write(
        f"GATE RETREAT: 已退到 {target_phase}，共 {steps} 步，均已独立 commit + 归档\n"
    )
    # 回退落地后必须建 DEBT 条目（TAG0001 Phase 2 唯一硬强制，BDD-12）
    # 事后兜底由 check-debt.py --retreat-coverage 只读比对（不阻断）
    sys.stdout.write(
        "GATE RETREAT: 回退已完成——请为本次回退建立 source: retreat 的 DEBT 条目"
        "（{AGATE_WORKSPACE}/debt/tech-debt.md，模板见 assets/templates/tech-debt-template.md）\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
