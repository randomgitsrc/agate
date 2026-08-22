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
import sys

from agate_common import (
    is_gate_meta_key,
    is_legal_gate_key,
    known_phase_ids,
    parse_gate_commands_block,
    reconcile_enabled,
    reconcile_field,
    reconcile_summary,
    resolve_rules_root,
)


def _reconcile_block_keys(entries):
    """M1 对账（P2-design §3.4，BDD-6/7）：gate_commands 块键集 vs 声明语法。

    块内出现未声明 key（project_module 特判 / is_gate_meta_key 后缀 / P{阶段} 键之外）
    → stderr `RECONCILE WARNING` + 计数（可进日志）；对账不改变本脚本退出码语义（0 不变）。
    对账关闭（AGATE_RECONCILE=off）或无键时不输出。任何异常 fail-open（不阻断原判定）。
    """
    if not reconcile_enabled():
        return
    try:
        keys = [k for k, _v in entries]
        if not keys:
            return
        phase_ids = known_phase_ids(resolve_rules_root(__file__))
        for key in keys:
            if not is_legal_gate_key(key, phase_ids):
                reconcile_field("read-gate-commands", "gate_commands." + key, key, "(未声明)")
        reconcile_summary()
    except Exception:
        pass


content = open(os.environ["GATE_FILE"], encoding="utf-8").read()
has_block, entries = parse_gate_commands_block(content)
if not has_block:
    print(json.dumps({"commands": [], "project_module": ""}))
    sys.exit(0)
commands = []
project_module = ""
for key, raw in entries:
    val = raw.strip().strip(chr(34)).strip(chr(39))
    if key == "project_module":
        project_module = val
    elif key.startswith("P3") and not is_gate_meta_key(key):
        suffix = key[2:] if len(key) > 2 else ""
        fmt_key = "P3" + suffix + "_formatter"
        fmt_val = ""
        for key2, raw2 in entries:
            if key2 == fmt_key:
                fmt_val = raw2.strip().strip(chr(34)).strip(chr(39))
        commands.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
result = {"commands": commands, "project_module": project_module}
_reconcile_block_keys(entries)
print(json.dumps(result))
