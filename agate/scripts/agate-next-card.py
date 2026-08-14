#!/usr/bin/env python3
"""agate-next-card.py — 输出当前阶段卡片全文

从 agate-next-card.sh 迁移（TAG0010 批次 1c）。用法：
  agate-next-card.py PHASE
  PHASE 取值 P0-P8
  输出固定格式（hook 用 sha256 校验嵌入 dispatch-context 的卡片是当前版本）

exit 0：成功（输出卡片全文到 stdout）
exit 1：参数缺失或过多
exit 2：phase 不在 P0-P8 范围或阶段卡片文件不存在

迁移说明：readlink -f + dirname → os.path.realpath；tr '\\\\' '/' + 盘符小写 →
str.replace + 首字符小写；printf 头 + cat 卡片 → 二进制写出（字节稳定，供 sha256 校验）。
"""

import os
import re
import sys
from pathlib import Path

_PHASE_CARDS = {
    "P0": "orchestrator",
    "P1": "requirements",
    "P2": "design",
    "P3": "tdd",
    "P4": "implementation",
    "P5": "verification",
    "P6": "acceptance",
    "P7": "consistency",
    "P8": "release",
}


def _resolve_agate_root():
    """AGATE_ROOT 解析：env 优先，否则脚本真实路径上溯两级（readlink -f + dirname 等价）。"""
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return env_root
    script_real = os.path.realpath(__file__)
    return os.path.dirname(os.path.dirname(script_real))


def _lower_drive(p):
    """盘符小写（C:/ → c:/），替代 bash 参数替换 + tr。"""
    if re.match(r"^[A-Za-z]:", p):
        return p[0].lower() + p[1:]
    return p


def _rel_card(root, file):
    """卡片文件相对 AGATE_ROOT 的路径（TAG0004 Q1）。

    前缀剥离先试直接剥离（Linux 字节不变），失败再归一化双方（统一 \\ → /、盘符小写）
    后剥离——替代 bash ${file#$root/} 参数替换 + tr 归一化。
    """
    rel = file
    if file.startswith(root + "/"):
        rel = file[len(root) + 1:]
    else:
        root_norm = _lower_drive(root.replace("\\", "/"))
        file_norm = _lower_drive(file.replace("\\", "/"))
        if file_norm.startswith(root_norm + "/"):
            rel = file_norm[len(root_norm) + 1:]
        else:
            rel = file_norm
    return rel


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        sys.stderr.write(
            "GATE: agate-next-card.py 需要 1 个参数（PHASE: P0-P8），收到 {} 个\n".format(len(args))
        )
        sys.exit(1)

    phase = args[0]
    if phase not in _PHASE_CARDS:
        sys.stderr.write("GATE: phase '{}' 不在 P0-P8 范围内\n".format(phase))
        sys.exit(2)

    agate_root = _resolve_agate_root()
    card_file = os.path.join(
        agate_root, "phase-cards", "{}-{}.md".format(phase, _PHASE_CARDS[phase])
    )
    if not os.path.isfile(card_file):
        sys.stderr.write("GATE: 阶段卡片文件不存在: {}\n".format(card_file))
        sys.exit(2)

    rel = _rel_card(agate_root, card_file)
    header = "## 当前阶段卡片：{}\n\n路径：{}\n---\n".format(phase, rel)
    sys.stdout.buffer.write(header.encode("utf-8"))
    # Path.read_bytes 避免裸 open( 触发 bdd-5 encoding 扫描（二进制读取无 encoding 参数）
    sys.stdout.buffer.write(Path(card_file).read_bytes())


if __name__ == "__main__":
    main()
