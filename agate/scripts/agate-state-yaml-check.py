#!/usr/bin/env python3
"""校验 .state.yaml 格式（py 抽离批次 5）。

从 STATE_FILE env 读文件。输出错误行（每行一个），无错误输出空。
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-state-yaml-check: 需要 pyyaml\n")
    sys.exit(1)

valid_phases = "P0 P1 P2 P3 P4 P5 P6 P7 P8 PAUSED READY DONE".split()

state_file = os.environ["STATE_FILE"]
try:
    with open(state_file) as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print("YAML 解析错误: {}".format(e))
    sys.exit(0)

errors = []

if data is None:
    errors.append("文件为空")
    print("\n".join(errors))
    sys.exit(0)

for field in ("task_id", "phase", "status"):
    if field not in data:
        errors.append("缺必填字段: {}".format(field))

task_id = data.get("task_id", "")
if task_id and not re.match(r"^T[A-Z]{2}\d+$", str(task_id)):
    errors.append("task_id 格式错误: {}（应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001）".format(task_id))

phase = str(data.get("phase", ""))
if phase and phase not in valid_phases:
    errors.append("phase 非法值: {}（合法值: {}）".format(phase, " ".join(valid_phases)))

retries = data.get("retries", {})
if retries:
    if not isinstance(retries, dict):
        errors.append("retries 应为 dict，实际为 {}".format(type(retries).__name__))
    else:
        for key, val in retries.items():
            if not re.match(r"^P\d+$", str(key)):
                errors.append("retries key 格式错误: {}（应为大写 P + 数字，如 P2）".format(key))
            if not isinstance(val, list):
                errors.append("retries[{}] 应为列表，实际为 {}".format(key, type(val).__name__))

if errors:
    print("\n".join(errors))