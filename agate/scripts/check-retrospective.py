#!/usr/bin/env python3
"""check-retrospective.py — 复盘异常触发（P2.12）

从 check-retrospective.sh 迁移（TAG0010 批次 2a）。CLI 契约与 sh 版等价：
检测异常模式（gate 重试超限 / SCOPE+ / 裁剪 override），输出复盘提醒到 stderr
（不中止 commit）。exit 0 = 总是通过（只提醒不拦截）。

迁移说明：sh 的 STATE_FILE=... agate-state-get.py retries_over 子进程 →
sys.executable subprocess（$(...) 剥尾换行 → .rstrip("\n")）；sed 剥离 AGATE_CARD
块 + grep 行首 SCOPE+ → 正则等价；grep '^override:' → re.MULTILINE 等价。
"""

import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGATE_STATE_GET = os.path.join(SCRIPT_DIR, "agate-state-get.py")
MAX_RETRY_MAP = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"
SCOPE_PLUS_RE = re.compile(r"^\s*-?\s*\[SCOPE\+\]", re.MULTILINE)
SKIP_NAME_RE = re.compile(r"dispatch-context|dispatch-prompt|progress")
AGATE_CARD_RE = re.compile(r"<!-- AGATE_CARD_START -->.*?<!-- AGATE_CARD_END -->", re.DOTALL)
OVERRIDE_RE = re.compile(r"^override:", re.MULTILINE)


def _retries_over(state_file):
    """调 agate-state-get.py retries_over（等价 sh 的 STATE_FILE=... agate-state-get.py
    retries_over 'P1:3,...' 2>/dev/null || echo ""；$(...) 剥尾换行 → .rstrip("\n")）。"""
    env = dict(os.environ)
    env["STATE_FILE"] = state_file
    try:
        proc = subprocess.run(
            [sys.executable, AGATE_STATE_GET, "retries_over", MAX_RETRY_MAP],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").rstrip("\n")


def _scan_scope_plus(task_dir):
    """扫描顶层 *.md 找行首 [SCOPE+]（排除 dispatch-context/dispatch-prompt/progress 文件
    + 剥离 AGATE_CARD 块，同 sh sed 删除 + grep -qE）。返回首个命中文件 basename 或空串。"""
    for name in sorted(os.listdir(task_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(task_dir, name)
        if not os.path.isfile(path):
            continue
        if SKIP_NAME_RE.search(name):
            continue
        with open(path, encoding="utf-8") as f:
            text = AGATE_CARD_RE.sub("", f.read())
        if SCOPE_PLUS_RE.search(text):
            return name
    return ""


def main():
    args = sys.argv[1:]
    if not args:
        sys.stderr.write("用法: check-retrospective.py TASK_DIR\n")
        sys.exit(1)
    task_dir = args[0]
    state_file = args[1] if len(args) > 1 else ".state.yaml"

    warnings = []

    if os.path.isfile(state_file):
        over = _retries_over(state_file)
        if over:
            warnings.append(f"gate 重试超限（{over}）")

    if os.path.isdir(task_dir):
        hit = _scan_scope_plus(task_dir)
        if hit:
            warnings.append(f"SCOPE+ 触发（{hit}）")

    p1_file = os.path.join(task_dir, "P1-requirements.md")
    if os.path.isdir(task_dir) and os.path.isfile(p1_file):
        with open(p1_file, encoding="utf-8") as f:
            if OVERRIDE_RE.search(f.read()):
                warnings.append("裁剪声明与执行不一致（override 触发）")

    if warnings:
        sys.stderr.write("GATE RETRO: 建议复盘 — 检测到异常模式：\n")
        for w in warnings:
            sys.stderr.write(f"  - {w}\n")
        sys.stderr.write("  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
