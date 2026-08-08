#!/usr/bin/env python3
"""gate_commands 缺失命令检测（py 抽离批次 6）。

读 GATE_FILE env。解析 gate_commands 每个命令的第一个 token，
跳过含 / 或 = 的 token，输出 "key:token"。无 gate_commands 块输出空。
"""

import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
block = m.group(1)
for k, v in re.findall(r"^  (P[0-9]\w*):\s*(.+)$", block, re.MULTILINE):
    if k.endswith("_formatter") or k == "project_module":
        continue
    val = v.strip().strip(chr(34)).strip(chr(39))
    if not val:
        continue
    token = val.split()[0]
    token = token.lstrip("$(").rstrip(")")
    if "/" in token or "=" in token:
        continue
    print("{}:{}".format(k, token))