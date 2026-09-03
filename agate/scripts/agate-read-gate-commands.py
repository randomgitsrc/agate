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


def _clean_value(raw, key):
    """M1 值清洗（P2-design §3.1，BDD-1/BDD-2）：剥离行内注释 + 引号闭合校验。

    外层首尾一对匹配引号视为块语法包裹先剥一层，再在剩余内容中截断首个
    引号外未转义 ` #`（`\\#` 转义保留，引号内 ` #` 保留）；截断后仍有未闭合
    引号（计数为奇）则 fail-closed：stderr 报解析错误（含 key 名）+ exit 2。
    """

    def _peel(s):
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("\"", "'"):
            return s[1:-1]
        return s

    s = _peel(raw.strip())
    out = []
    quote = None
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            out.append(ch)
            out.append(s[i + 1])
            i += 2
            continue
        if ch in ("\"", "'"):
            if quote is None:
                quote = ch
            elif quote == ch:
                quote = None
            out.append(ch)
            i += 1
            continue
        if ch == "#" and quote is None and out and out[-1] in (" ", "\t"):
            break
        out.append(ch)
        i += 1
    s = _peel("".join(out).strip())
    if s.count("\"") % 2 == 1 or s.count("'") % 2 == 1:
        sys.stderr.write(
            f"agate-read-gate-commands: 解析错误: {key} 命令值引号未闭合: {s[:60]}\n"
        )
        sys.exit(2)
    return s


content = open(os.environ["GATE_FILE"], encoding="utf-8").read()
has_block, entries = parse_gate_commands_block(content)
if not has_block:
    print(json.dumps({"commands": [], "project_module": ""}))
    sys.exit(0)
commands = []
project_module = ""
for key, raw in entries:
    val = _clean_value(raw, key)
    if key == "project_module":
        project_module = val
    elif key == "P3":
        suffix = ""
        fmt_key = "P3_formatter"
        fmt_val = ""
        for key2, raw2 in entries:
            if key2 == fmt_key:
                fmt_val = _clean_value(raw2, key2)
        commands.append({"cmd": val, "formatter": fmt_val, "suffix": suffix})
result = {"commands": commands, "project_module": project_module}
_reconcile_block_keys(entries)
print(json.dumps(result))
