#!/usr/bin/env python3
"""从 P1/P2 markdown 提取字段（py 抽离共享工具）。

从 FILE 环境变量读文件路径，按子命令正则提取。FILE 不存在/不可读时
抛异常（FileNotFoundError）→非零退出（由 bash 调用方 2>/dev/null || echo 兜底）。

用法：
  risk_level   提取 risk_level 冒号后 low/medium/high，无匹配输出空
  ui_affected  提取 ui_affected 冒号后 true/false，无匹配输出空
  phases       提取 phases 行内列表（方括号）或块式列表（- Pn），空格连接
"""

import os
import re
import sys


def _read():
    with open(os.environ["FILE"]) as f:
        return f.read()


def main():
    op = sys.argv[1]
    text = _read()
    if op == "risk_level":
        m = re.search(r"risk_level:\s*(low|medium|high)", text)
        print(m.group(1) if m else "")
    elif op == "ui_affected":
        m = re.search(r"ui_affected:\s*(true|false)", text)
        print(m.group(1) if m else "")
    elif op == "phases":
        m = re.search(r"phases:\s*\[([^\]]+)\]", text)
        if m:
            phases = [p.strip() for p in m.group(1).split(",")]
            print(" ".join(phases))
        else:
            m = re.search(r"phases:\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)", text)
            if m:
                phases = re.findall(r"-\s+(\S+)", m.group(1))
                print(" ".join(phases))
    else:
        sys.stderr.write("agate-md-field-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()