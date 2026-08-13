#!/usr/bin/env python3
"""读 .state.yaml 的字段（py 抽离共享工具）。

从 STATE_FILE 环境变量读 .state.yaml，按子命令输出。STATE_FILE 不存在/不可读时
抛异常→非零退出（由 bash 调用方 2>/dev/null || echo 兜底）。

用法：
  phase         打印 STATE_FILE 的 data.get('phase', '')（data 为 None 时打印空）
  phase_stdin   从 stdin 读 yaml（git show 场景），打印 phase
  task_id       打印 STATE_FILE 的 data.get('task_id', '')
  retries_over MAP  打印首个 len(attempts) >= phase_max 的阶段 "PHASE=N (MAX=M)"
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-state-get: 需要 pyyaml。pip install pyyaml\n")
    sys.exit(1)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    op = sys.argv[1]
    if op == "phase":
        data = _load(os.environ["STATE_FILE"])
        print(data.get("phase", "") if data else "")
    elif op == "phase_stdin":
        data = yaml.safe_load(sys.stdin)
        print(data.get("phase", "") if data else "")
    elif op == "task_id":
        data = _load(os.environ["STATE_FILE"])
        print(data.get("task_id", "") if data else "")
    elif op == "retries_over":
        state_file = os.environ["STATE_FILE"]
        max_map_str = sys.argv[2]
        data = _load(state_file)
        retries = data.get("retries", {}) if data else {}
        max_map = dict(p.split(":") for p in max_map_str.split(","))
        if isinstance(retries, dict):
            for phase, attempts in retries.items():
                phase_max = int(max_map.get(phase, 3))
                if isinstance(attempts, list) and len(attempts) >= phase_max:
                    print(f"{phase}={len(attempts)} (MAX={phase_max})")
                    break
    else:
        sys.stderr.write("agate-state-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()