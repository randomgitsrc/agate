#!/usr/bin/env python3
"""统计 gate_commands.P5 命令数（py 抽离批次 6）。

读 GATE_FILE env。无 gate_commands 块输出 0。
"""

import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print(0)
    sys.exit(0)
block = m.group(1)
count = len(re.findall(r"^  (P5\w*):", block, re.MULTILINE))
print(count)