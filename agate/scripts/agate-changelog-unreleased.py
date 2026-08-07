#!/usr/bin/env python3
"""从 CHANGELOG_FILE 提取 [Unreleased] 区域内容（py 抽离批次 5）。"""

import os
import re
import sys

with open(os.environ["CHANGELOG_FILE"]) as f:
    text = f.read()
m = re.search(r"##\s*\[Unreleased\](.*?)(?=##\s*\[|\Z)", text, re.S)
if m:
    print(m.group(1))