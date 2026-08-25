#!/usr/bin/env python3
"""agate-md-field-set-gate-commands.py — gate_commands 正文块写入（TAG0024 P4，P2-design.md §3.3）

CLI：agate-md-field-set-gate-commands.py FILE <yaml块或@文件路径>

gate_commands 是 P2-design.md **正文**（非 frontmatter）中的多行 YAML 映射块
（task-files.md「gate 命令」节约定）。本工具：
  1. yaml.safe_load 候选块 → 必须是 dict
  2. 逐 key 校验合法性：agate_common.is_legal_gate_key(key, known_phase_ids(...))
     （与 check-gate.py `_reconcile_p2_fields()` 同一函数，非重写）；
     `_timeout_seconds` 后缀 key 额外校验值为正整数（is_gate_meta_key 只判定 key 结构，
     不做值类型校验，本工具补上）
  3. 全部合法 → 生成标准块文本，整块替换正文既有 gate_commands: 块（无则追加正文末尾）
  4. 自校验：写入前用 agate_common.parse_gate_commands_block 反解析一次，确认条目与候选
     一致才允许落盘（BDD-7）
  5. 原子写（同 agate-md-field-set.py）
"""

import contextlib
import json
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import agate_common  # noqa: E402

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-md-field-set-gate-commands: 需要 pyyaml\n")
    sys.exit(1)


def _read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def _atomic_write(path, content):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".md-field-set-gc-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _format_gate_value(v):
    """gate_commands 块内 value 的字面文本（供写入正文行 `  key: <value>`）。"""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return json.dumps(str(v), ensure_ascii=False)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        sys.stderr.write(
            "用法: agate-md-field-set-gate-commands.py FILE <yaml块或@文件路径>\n"
        )
        return 2

    file_path, block_arg = args

    if not os.path.isfile(file_path):
        sys.stderr.write(
            f"ERROR: 文件不存在（{file_path}），请先 Write 产出文件，再 set 字段\n"
        )
        return 1

    if block_arg.startswith("@"):
        ref_path = block_arg[1:]
        try:
            with open(ref_path, encoding="utf-8") as fh:
                block_text_raw = fh.read()
        except OSError as e:
            sys.stderr.write(f"ERROR: 无法读取 {ref_path}（{e}）\n")
            return 1
    else:
        block_text_raw = block_arg

    try:
        candidate = yaml.safe_load(block_text_raw)
    except yaml.YAMLError as e:
        sys.stderr.write(f"ERROR: gate_commands 块解析失败（{e}）\n")
        return 1

    if not isinstance(candidate, dict):
        sys.stderr.write("ERROR: gate_commands 块须为 key: value 映射\n")
        return 1

    rules_root = agate_common.resolve_rules_root(__file__)
    phase_ids = agate_common.known_phase_ids(rules_root)

    illegal = []
    for key, value in candidate.items():
        if not agate_common.is_legal_gate_key(key, phase_ids):
            illegal.append(key)
            continue
        if key.endswith("_timeout_seconds") and (
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
        ):
            illegal.append(key)

    if illegal:
        sys.stderr.write(
            "ERROR: gate_commands 块含非法 key/值: " + ", ".join(illegal) + "\n"
        )
        return 1

    entries_formatted = [(k, _format_gate_value(v)) for k, v in candidate.items()]
    block_text = "gate_commands:\n" + "".join(f"  {k}: {v}\n" for k, v in entries_formatted)

    text = _read_text(file_path)
    fm, body = agate_common.split_frontmatter(text)

    has_block, _ = agate_common.parse_gate_commands_block(body)
    if has_block:
        padded = body if body.endswith("\n") else body + "\n"
        new_body = agate_common._GATE_COMMANDS_BLOCK_RE.sub(lambda m: block_text, padded, count=1)
    else:
        sep = "" if body == "" or body.endswith("\n") else "\n"
        new_body = body + sep + block_text

    if fm is not None:
        fm_dump = yaml.safe_dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        new_text = "---\n" + fm_dump + "---" + new_body
    else:
        # 无 frontmatter 的文件：一期边界，仅处理正文块，不新增 frontmatter（未被测试路径
        # 覆盖，防御性兜底，行为与"正文替换/追加"语义一致）。
        new_text = new_body

    # 写入前自校验（BDD-7）：反解析新文本，确认条目与候选写入值逐字节一致才允许落盘。
    check_has, check_entries = agate_common.parse_gate_commands_block(new_text)
    if not check_has or check_entries != entries_formatted:
        sys.stderr.write("ERROR: gate_commands 写入自校验失败（内部错误，未落盘）\n")
        return 1

    try:
        _atomic_write(file_path, new_text)
    except Exception as e:
        sys.stderr.write(f"ERROR: 写入失败（{e}），未落盘\n")
        return 1

    print(f"OK: gate_commands 已写入 {os.path.basename(file_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
