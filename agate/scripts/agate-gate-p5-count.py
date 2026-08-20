#!/usr/bin/env python3
"""统计 gate_commands.P5 命令数（py 抽离批次 6）。

读 GATE_FILE env。输出单行双值 `"{main} {aux}"`：
  - main = 主命令数（精确 `P5:` 键，不匹配 P5_* 辅助键）
  - aux  = 辅助命令数（`P5_<name>:` 键，排除 `_formatter` / `_timeout_seconds` 元信息键——与 read-p5-commands 的执行枚举语义对齐）
无 gate_commands 块输出 `0 0`。
"""

import os
import re
import sys

from agate_common import is_gate_meta_key

content = open(os.environ["GATE_FILE"], encoding="utf-8").read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print("0 0")
    sys.exit(0)
block = m.group(1)
main = len(re.findall(r"^  P5:", block, re.MULTILINE))
aux = [k for k in re.findall(r"^  (P5_\w+):", block, re.MULTILINE) if not is_gate_meta_key(k)]
print(f"{main} {len(aux)}")
