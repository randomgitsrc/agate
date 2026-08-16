#!/usr/bin/env python3
"""resolve-entry.py — hook 固定解析入口（TAG0008，批次 resolve-chain）

读项目 .agate-version（或 current/latest/脚本路径上溯兜底）→ 得 AGATE_ROOT →
exec 对应版本 gate py。AGATE_ROOT env 覆盖最高（BDD-12）。

用法:
  resolve-entry.py <gate-name> [args...]
gate-name → gate py 映射（P2-review 决策点 2，薄壳保留、exec 目标变 resolve-entry）:
  pre-commit  → pre-commit-gate.py
  commit-msg  → commit-msg-self-gate.py
  pre-push    → pre-push-gate.py

不重装 hook 切版本（BDD-18）：每次运行读 .agate-version，改声明即生效。
解析失败（声明未装/格式非法）→ stderr 警告 + 回退 current（绝不静默禁用，BDD-13/14/17）；
gate 脚本缺失 → exit 1（fail-closed，不静默放行 gate）。
"""

import os
import sys

try:
    from agate_common import resolve_hook_root
except (ImportError, SystemExit):
    sys.stderr.write("resolve-entry: agate_common 不可用（缺 pyyaml？），gate 阻断\n")
    sys.exit(1)

_GATE_MAP = {
    "pre-commit": "pre-commit-gate.py",
    "commit-msg": "commit-msg-self-gate.py",
    "pre-push": "pre-push-gate.py",
}


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("resolve-entry: 用法 resolve-entry.py <gate-name> [args...]\n")
        sys.exit(2)
    gate = sys.argv[1]
    gate_py = _GATE_MAP.get(gate)
    if gate_py is None:
        sys.stderr.write(f"resolve-entry: 未知 gate 名 '{gate}'（应为 pre-commit/commit-msg/pre-push）\n")
        sys.exit(2)

    root, warnings = resolve_hook_root(os.path.abspath(__file__))
    for w in warnings:
        sys.stderr.write(w + "\n")

    gate_path = os.path.join(root, "scripts", gate_py)
    if not os.path.isfile(gate_path):
        sys.stderr.write(f"resolve-entry: gate 脚本不存在 {gate_path}，gate 阻断\n")
        sys.exit(1)

    os.execv(sys.executable, [sys.executable, gate_path, *sys.argv[2:]])


if __name__ == "__main__":
    main()
