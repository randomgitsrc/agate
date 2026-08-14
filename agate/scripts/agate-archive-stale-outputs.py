#!/usr/bin/env python3
"""agate-archive-stale-outputs.py — 回退时归档被跨过阶段的自撰产出（P4 批次 1b）

从 agate-archive-stale-outputs.sh 迁移（TAG0010 批次 1b）。用法：
  agate-archive-stale-outputs.py PHASE_BEING_LEFT TASK_DIR
只处理 self-authored gate 阶段（P1/P2/P6/P7），P4/P5 无跨重试持久化产出，不适用。

CLI 契约与 sh 版等价：exit code、stdout 输出格式、归档目录命名
（.archived/{YYYYmmdd-HHMMSS}-{PHASE}）、.retreat-history.md breadcrumb 追加语义。
"""

import os
import re
import shutil
import sys
from datetime import datetime

_OUTPUTS = {
    "P1": ["P1-requirements.md", "P1-review.md"],
    "P2": ["P2-design.md", "P2-review.md"],
    "P6": ["P6-acceptance.md"],
    "P7": ["P7-consistency.md"],
}

_FAIL_RE = re.compile(r"^\s*- FAIL", re.IGNORECASE)


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("用法: agate-archive-stale-outputs.py PHASE TASK_DIR\n")
        sys.exit(1)
    phase = sys.argv[1]
    task_dir = sys.argv[2]

    outputs = _OUTPUTS.get(phase, [])
    if not outputs:
        print("GATE ARCHIVE: {} 无需归档（非 self-authored 产出阶段）".format(phase))
        sys.exit(0)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_dir = os.path.join(task_dir, ".archived", "{}-{}".format(ts, phase))
    os.makedirs(archive_dir, exist_ok=True)

    # 归档前先把关键失败信息摘要写入一份不会被归档的 breadcrumb 文件
    breadcrumb = os.path.join(task_dir, ".retreat-history.md")
    with open(breadcrumb, "a", encoding="utf-8") as f:
        f.write("\n## {} 归档 {}\n\n归档位置：`{}`\n".format(ts, phase, archive_dir))
        if phase == "P6":
            p6 = os.path.join(task_dir, "P6-acceptance.md")
            if os.path.isfile(p6):
                with open(p6, encoding="utf-8") as pf:
                    fail_lines = [
                        line for line in pf.read().splitlines()
                        if _FAIL_RE.search(line)
                    ]
                if fail_lines:
                    f.write("\n失败详情（供重新派发时引用，避免翻 .archived/）：\n```\n")
                    f.write("\n".join(fail_lines) + "\n")
                    f.write("```\n")

    moved = 0
    for name in outputs:
        src = os.path.join(task_dir, name)
        if os.path.isfile(src):
            shutil.move(src, os.path.join(archive_dir, name))
            moved += 1
    evidence = os.path.join(task_dir, "P6-evidence")
    if phase == "P6" and os.path.isdir(evidence):
        shutil.move(evidence, os.path.join(archive_dir, "P6-evidence"))
        moved += 1

    print("GATE ARCHIVE: {} 产出已归档至 {}（{} 项），失败摘要已写入 {}".format(
        phase, archive_dir, moved, breadcrumb))


if __name__ == "__main__":
    main()
