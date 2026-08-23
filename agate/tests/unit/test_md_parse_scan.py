# agate/tests/unit/test_md_parse_scan.py — BDD-3：check-gate.py 协议规则类 md 解析清零（TAG0022 RM-AG0038）
#
# 被测：agate/scripts/check-gate.py（静态扫描，不运行）。
# 背景（P1 §4.2 / P2 §4.2.1）：RM-AG0038 把 check-gate.py 的协议规则 md/grep 解析点
# （A/B/C/D 组）迁移到 rules/*.yaml + agate_common 共享读取器 + agate-md-field-get op。
# BDD-3 验收锚 = 迁移后 check-gate.py 内「协议规则类 md 解析点命中数 = 0」。
# 本文件把 P2 §4.2.1 逐点映射清单固化为**静态扫描模式清单**（判定模式清单，P2 要求 P3 固化）。
#
# 判定口径（P1 D2）：E 组（.state.yaml 读取，YAML 结构化）与 F 组（git/CHANGELOG 输出解析）
# 不计入「md 解析」面——模式清单不含这两组。
# 过滤规则：仅扫**非注释代码行**（行首 # 的行剔除）——历史注释里对旧解析点的引用不是解析点。
#
# TDD 红灯：P3 现状 check-gate.py 未迁移 → 清单命中数 > 0 → 断言失败（B 类，被测模块行为未变更）。
# P4 迁移后清单命中数 = 0 → 转绿。
#
# 平台无关（BDD-16/10）：无裸解释器字面量 / 无 PATH 硬编码 / 无 POSIX symlink 假设 /
# 无临时目录字面量；只做纯文本扫描（read_text + str.count），跨平台一致。

import pytest

# ── BDD-3 判定模式清单（P2 §4.2.1 A/B/C/D 组 → 本文件为权威源，P4 迁移须让全部命中归零）──
# 每个模式取「当前 check-gate.py 内解析点字面片段」；迁移后该字面不得再出现在 check-gate.py 代码行。
_MD_PARSE_PATTERNS = [
    # A 组：frontmatter 字面读取（→ agate-md-field-get 新 op status/agent/project_phase/code_map_*）
    #   定义 L164 + 调用 L500/506/716/722/768/799/805/1108/1109（NB-6 补全 L799/805）
    "_frontmatter_field",
    # B 组：行首标记正则（→ agate_common.count_markers，L101-110 定义 + L523-584 计数）
    "_NC_RE",
    "_SUGGEST_RE",
    "_NO_NEED_RE",
    "_NC_DESC_RE",
    "_SUGGEST_DESC_RE",
    "_SUGGEST_TAIL_BT_RE",
    "_SUGGEST_TAIL_BRACKET_RE",
    # C 组：任务产出格式判定正则（→ agate_common 共享读取器）
    r"#{2,5}\s+BDD-[0-9]+",  # extract_bdd_titles（L390）
    r"#{2,3}\s+UI 设计",  # parse_ui_design_section 节标题（L417）
    r"^candidate_count:",  # scan_fm_line candidate_count（L693）
    r"^(design_trivial|follows_existing_pattern):",  # scan_fm_line design_trivial（L703）
    "trade-?off",  # has_keyword 权衡关键词（L736）
    "```fail-list",  # parse_fail_list_block（L878）
    r"^\|\s*[0-9]+\s*\|",  # count_kf_entries known-failures 表格计数（L909）
    r"(PASS|FAIL)\b.*BDD-[0-9]",  # count_p6_pass_fail（L950/954）
    r"^\s*-?\s*\[BLOCKER\]",  # count_p7_markers（L1015）
    r"^\s*-?\s*\[DEVIATION-CRITICAL\]",  # count_p7_markers（L1016）
    r"^\s*>?\s*-?\s*\[DESIGN_GAP:",  # count_design_gap（L1048/1079）
    r"^\s*>?\s*-?\s*\[DESIGN_GAP_REVIEWED",  # count_design_gap（L1049）
    r"设计偏差|design gap|未列入|gap:",  # has_keyword P4 关键词（L1060）
    r"^\s*-?\s*\[CODE_MAP_UPDATED\]",  # count_code_map_lines（L1127）
    r"^\s*-?\s*\[CODE_MAP_EXEMPT",  # count_code_map_lines（L1128）
    # D 组：md 内嵌 yaml 块解析（→ agate_common.extract_embedded_yaml_blocks，L336）
    r"```(?:yaml|yml)",
]


def _code_lines(path):
    """非注释代码行（行首 # 剔除）；空行剔除。注释里的历史引用不算解析点。"""
    return [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


@pytest.mark.windows_smoke
def test_bdd_3_check_gate_no_protocol_md_parse_points(agate_scripts):
    """BDD-3：check-gate.py 协议规则类 md 解析点命中数 = 0。

    Given RM-AG0038 迁移完成（规则权威源切到 rules/*.yaml，S-1~S-6 收紧）
    When  对 check-gate.py 静态扫描 A/B/C/D 组模式
    Then  命中数 = 0（P1 D2：E/F 组不计入；注释行不计）
    TDD：P3 现状未迁移 → 命中 > 0 → 红灯（B 类）。
    """
    gate_src = agate_scripts / "check-gate.py"
    code = "\n".join(_code_lines(gate_src))
    hits = {p: code.count(p) for p in _MD_PARSE_PATTERNS}
    total = sum(hits.values())
    assert total == 0, (
        "BDD-3 红灯（RM-AG0038 未迁移）：check-gate.py 存在协议规则类 md 解析点残留。"
        f"命中 {total} 处：{[(p, n) for p, n in hits.items() if n > 0]}"
    )
