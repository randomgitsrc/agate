#!/usr/bin/env python3
"""agate-retreat-to.sh 的状态读写专用工具（py 抽离批次 4）。

从 STATE_FILE 环境变量读写 .state.yaml。

用法：
  check_retreat MAP  回退路径超限检查。遍历 CUR-1..TGT（CUR/TGT 环境变量），
                    若某阶段 len(attempts)+1 > limit，输出 "PHASE:COUNT+1:LIMIT" 并 break。
  write_retreat      追加一条 retry 到 NEW_PHASE、把 phase 改为 NEW_PHASE、
                    回写 .state.yaml（allow_unicode/sort_keys=False）。
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-retreat-state: 需要 pyyaml。pip install pyyaml\n")
    sys.exit(1)


def main():
    op = sys.argv[1]
    state_file = os.environ["STATE_FILE"]
    if op == "check_retreat":
        max_map_str = sys.argv[2]
        with open(state_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        retries = data.get("retries", {}) or {}
        max_map = dict(p.split(":") for p in max_map_str.split(","))
        cur, tgt = int(os.environ["CUR"]), int(os.environ["TGT"])
        for n in range(cur - 1, tgt - 1, -1):
            phase = f"P{n}"
            attempts = retries.get(phase, [])
            count = len(attempts) if isinstance(attempts, list) else 0
            limit = int(max_map.get(phase, 3))
            if count + 1 > limit:
                print(f"{phase}:{count + 1}:{limit}")
                break
    elif op == "write_retreat":
        with open(state_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        retries = data.setdefault("retries", {})
        new_phase = os.environ["NEW_PHASE"]
        attempts = retries.setdefault(new_phase, [])
        attempts.append({"attempt": len(attempts) + 1, "reason": os.environ["RETREAT_REASON"]})
        data["phase"] = new_phase
        with open(state_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    else:
        sys.stderr.write("agate-retreat-state: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()