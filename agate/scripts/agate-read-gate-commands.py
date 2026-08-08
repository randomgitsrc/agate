#!/usr/bin/env python3
"""解析 P2-design.md 的 gate_commands 块，输出 JSON。

从 check-tdd-red.sh 的 read_gate_commands() 内联 python 抽离（py 抽离试点）。
值传递走环境变量 GATE_FILE（文件路径）。输出单条 JSON：
  {"commands":[{"cmd":...,"formatter":...,"suffix":...}], "project_module":...}
无 gate_commands 块时输出 {"commands": [], "project_module": ""} 并 exit 0。
GATE_FILE 不存在/不可读 → 抛异常 → 非零退出（由 bash 调用方 2>/dev/null 兜底）。
"""

import json
import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print(json.dumps({"commands": [], "project_module": ""}))
    sys.exit(0)
block = m.group(1)
commands = []
project_module = ""
for line in re.findall(r"^  (\w+):\s*(.+)$", block, re.MULTILINE):
    key = line[0]
    val = line[1].strip().strip(chr(34)).strip(chr(39))
    if key == "project_module":
        project_module = val
    elif key.startswith("P3") and not key.endswith("_formatter"):
        suffix = key[2:] if len(key) > 2 else ""
        fmt_key = "P3" + suffix + "_formatter"
        fmt_val = ""
        for line2 in re.findall(r"^  (" + re.escape(fmt_key) + r"):\s*(.+)$", block, re.MULTILINE):
            fmt_val = line2[1].strip().strip(chr(34)).strip(chr(39))
        commands.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
result = {"commands": commands, "project_module": project_module}
print(json.dumps(result))