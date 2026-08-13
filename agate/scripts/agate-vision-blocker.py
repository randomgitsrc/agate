#!/usr/bin/env python3
"""读 vision_analysis.summary.blocker_count（py 抽离批次 5）。

从 YAML_PATH env 读文件。无 blocker_count 或解析失败输出 -1。
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-vision-blocker: 需要 pyyaml\n")
    sys.exit(1)

try:
    with open(os.environ["YAML_PATH"], encoding="utf-8") as f:
        data = yaml.safe_load(f)
    va = data.get("vision_analysis", {}) if data else {}
    summary = va.get("summary", {})
    print(summary.get("blocker_count", -1))
except Exception:
    print(-1)