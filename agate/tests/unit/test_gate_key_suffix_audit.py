# tests/unit/test_gate_key_suffix_audit.py — 结构性审计：防止未来新增第 5 处遗漏排除 _timeout_seconds 的解析脚本
# （TAG0017/DEBT0010 BDD-4：同类遗漏拦截）
#
# P1 同类扫描（3.1 节）确认当前仅 4 处解析缺陷点（agate-read-gate-commands.py /
# agate-gate-missing-cmds.py / agate-gate-p5-count.py / agate-read-p5-commands.py），
# 均只判 key.endswith("_formatter")，从未排除 _timeout_seconds。本测试不针对某一个具体脚本
# 断言，而是扫描 agate/scripts/agate-*.py 全体：任何脚本一旦含有对字面量 "_formatter" 的
# key 后缀排除逻辑，就必须同时含 "_timeout_seconds" 字面量，或引用共享判据函数
# is_gate_meta_key——否则视为与 DEBT0010 同类的新遗漏点，本测试（进而 pytest 整体）失败。
#
# 判据字面量选择说明：用带引号的字面量 "_formatter" / '_formatter'（而非裸子串 "_formatter"）
# 精确定位"做 key 后缀排除逻辑"的脚本，排除掉仅仅调用 resolve_formatter /
# run_test_with_formatter 等公共函数名的间接消费方（如 agate-capture-env-baseline.py，
# 按 P1 3.1 节判定为"间接消费方，本次不处理"，不应被本审计误伤）。
#
# 当前状态：4 个目标脚本均命中 "_formatter" 排除逻辑但未命中 "_timeout_seconds" /
# is_gate_meta_key → offenders 非空 → 本测试当前必须失败（真红灯）。P4 实现（改用
# is_gate_meta_key 或直接补 "_timeout_seconds" 判据）后 offenders 应变空，测试转绿。

import re
from pathlib import Path

_FORMATTER_LITERAL_RE = re.compile(r"""["']_formatter["']""")
_TIMEOUT_LITERAL_RE = re.compile(r"""["']_timeout_seconds["']""")


def test_bdd_4_formatter_excluding_scripts_also_exclude_timeout_seconds(agate_root):
    scripts_dir = Path(agate_root) / "scripts"
    offenders = []
    for path in sorted(scripts_dir.glob("agate-*.py")):
        text = path.read_text(encoding="utf-8")
        if not _FORMATTER_LITERAL_RE.search(text):
            continue
        if _TIMEOUT_LITERAL_RE.search(text) or "is_gate_meta_key" in text:
            continue
        offenders.append(path.name)

    assert offenders == [], (
        "以下脚本对 gate_commands key 做了 \"_formatter\" 后缀排除，但未同时排除 "
        "\"_timeout_seconds\"（也未引用共享判据函数 is_gate_meta_key），存在与 "
        f"DEBT0010 同类的遗漏风险，需改用 agate_common.is_gate_meta_key 或补齐判据: {offenders}"
    )
