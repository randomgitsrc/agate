#!/usr/bin/env python3
"""agate-resolve.py — agate 版本解析 CLI（TAG0008，批次 resolve-chain）

cwd 向上找 .agate-version（asdf 模式）→ 映射版本目录 → 输出 AGATE_ROOT + version +
reason。优先级：AGATE_ROOT env 最高 → 项目声明 → current → legacy 软链兜底
（BDD-9~14/30 + P2-review 测试缺口 1 终态 fail-closed）。

用法:
  python3 agate-resolve.py [DIR]
  DIR 可选起始目录（默认 cwd）。输出：
    AGATE_ROOT=<绝对路径>
    AGATE_VERSION=<版本号，env/legacy 时为 ''>
    AGATE_REASON=<解析原因>

警告写 stderr（声明未安装/格式非法不静默，BDD-13/14）。exit 0 = 有可用根；
exit 1 = 终态失败（无 current/latest/legacy 可用根，绝不静默，fail-closed）。
"""

import sys
from pathlib import Path

try:
    from agate_common import resolve_version_root
except (ImportError, SystemExit):
    sys.stderr.write("agate-resolve: agate_common 不可用（缺 pyyaml？），exit 1\n")
    sys.exit(1)


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else None
    info = resolve_version_root(start_dir=start)
    for w in info["warnings"]:
        sys.stderr.write(w + "\n")

    root = info["root"]
    if not root:
        sys.stderr.write("agate-resolve: 无可用 AGATE_ROOT（无 current/latest/legacy 布局），exit 1\n")
        sys.exit(1)

    sys.stdout.write(f"AGATE_ROOT={Path(root).resolve()!s}\n")
    sys.stdout.write(f"AGATE_VERSION={info['version'] or ''}\n")
    sys.stdout.write(f"AGATE_REASON={info['reason'] or ''}\n")


if __name__ == "__main__":
    main()
