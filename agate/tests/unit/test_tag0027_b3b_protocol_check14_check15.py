# agate/tests/unit/test_tag0027_b3b_protocol_check14_check15.py — TAG0027 B3b 批：护栏 1 机械化
# CHECK 14/15（BDD-15/22/24）
#
# 被测契约（P2-design §3.8 定案 D8-A + P2-review A3）：
#   CHECK 14（markdown 叙述段落平台名扫描，进 check-protocol-consistency.py）：
#     结构性判据（不维护逐段文件名单）：协议 md 按标题/空行切段、代码围栏整体跳过；命中段
#     （OpenCode/Claude Code/DSH/workflow/ralph/goal/task 词边界）若段落内无 `> 实现注记：`
#     标记行 → ERROR。豁免结构 = platform-notes.md/SETUP.md 整文件 + assets/templates/dsh/
#     平台食谱目录 + WORKFLOW.md「已知适用环境」表行。新增协议 md 自动覆盖（BDD-24）。
#   CHECK 15（数据面平台名扫描）：rules/*.yaml + rules/schema/*.json 平台词表命中数 = 0；
#     词边界 + 豁免词典机械生成（schema property 名 ∪ phases.yaml task_fields ∪ dispatch.yaml
#     既有键名）——task_fields/task_id 等键不误报（BDD-15）。
#
# TDD 红灯语义：P3 现状 check-protocol-consistency.py 无 CHECK 14/15 函数 → 测试函数内调用
#   AttributeError → pytest FAILED → check-tdd-red B 类红（行为未实现）。函数名 = P4 B3b
#   须实现的契约（沿用既有 check_* 命名风格 + Report rep 形态；P4 照本文件调用面实现同名函数）。
#   现状绿用例（数据面既有键不误报的反面若无新函数不可跑 → 全部归红由实现转绿；实现后 task_fields
#   不误报 = 回归守卫语义）。
# 平台无关：tmp_path fixture；importlib 加载模块（同 test_check_protocol_consistency 先例）。

import importlib.util
import os

import pytest


def _load_cpc(agate_scripts):
    path = os.path.join(str(agate_scripts), "check-protocol-consistency.py")
    spec = importlib.util.spec_from_file_location("cpc", path)
    cpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cpc)
    return cpc


def _write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _err14(rep):
    return [e for e in rep.errors if e["check"].startswith("CHECK14")]


def _err15(rep):
    return [e for e in rep.errors if e["check"].startswith("CHECK15")]


# ── BDD-22/16/24：CHECK 14 段落级判据 ─────────────────────────────────

def test_bdd_22_check14_md_paragraph_platform_name_no_note_errors(agate_scripts, tmp_path):
    """BDD-22：协议 md 语义叙述段含平台名（DSH）且段内无 `> 实现注记：` → CHECK 14 ERROR。
    P3 无 CHECK 14 函数 → AttributeError → 红（B 类）。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(root, "agate/WORKFLOW.md", "## 某节\n\n本段出现 DSH 平台名，无注记标记。\n\n## 另一节\n")
    _write(root, "agate/state-machine.md", "状态机叙述，无平台名。\n")
    rep = cpc.Report()
    cpc.check_md_platform_paragraphs(root, rep)  # P4 B3b 须实现同名函数（CHECK 14 段落级扫描）
    assert _err14(rep), "含平台名且无注记的段应报 CHECK 14 ERROR（BDD-22）"


def test_bdd_22_check14_add_note_marker_pass(agate_scripts, tmp_path):
    """BDD-22：同段补 `> 实现注记：` 标记行 → CHECK 14 不报（注记豁免 = 段落级判据）。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(
        root,
        "agate/WORKFLOW.md",
        "## 某节\n\n> 实现注记：本段平台适配说明（豁免）。\n\n本段含 DSH 平台名但带注记。\n\n## 另一节\n",
    )
    _write(root, "agate/state-machine.md", "状态机叙述，无平台名。\n")
    rep = cpc.Report()
    cpc.check_md_platform_paragraphs(root, rep)  # P4 B3b 须实现（带注记段豁免）
    assert not _err14(rep), f"带注记段不应报 CHECK 14 ERROR；{rep.errors}"


def test_bdd_16_check14_whole_file_exempt_structure(agate_scripts, tmp_path):
    """BDD-16 豁免结构（BDD-22 结构性判据的豁免面）：platform-notes.md / SETUP.md 整文件豁免
    （平台适配权威源元信息）——含平台名段落不报 CHECK 14。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(root, "agate/platform-notes.md", "## 平台适配\nOpenCode 部署细节。\n")
    _write(root, "agate/SETUP.md", "## 安装\nClaude Code 相关设置。\n")
    _write(root, "agate/WORKFLOW.md", "## 某节\n正常叙述无平台名。\n")
    rep = cpc.Report()
    cpc.check_md_platform_paragraphs(root, rep)  # P4 B3b 须实现（整文件豁免结构）
    assert not _err14(rep), f"豁免文件不应报 CHECK 14 ERROR；{rep.errors}"


def test_bdd_24_new_protocol_md_auto_covered(agate_scripts, tmp_path):
    """BDD-24：未来新增协议 md（agate/ 顶层语义叙述面）含平台名无注记 → 自动被 CHECK 14 命中
    （结构性判据不依赖维护文件名单）。P3 无函数 → 红（B 类）。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(root, "agate/WORKFLOW.md", "## 某节\n正常叙述。\n")
    _write(root, "agate/new-future-protocol.md", "## 新节\n本段含 DSH 平台名（新文档无注记）。\n")
    rep = cpc.Report()
    cpc.check_md_platform_paragraphs(root, rep)  # P4 B3b 须实现（结构性判据无名单 → 自动覆盖）
    assert _err14(rep), "新增协议 md 含平台名应自动命中 CHECK 14（BDD-24）"


# ── BDD-15：CHECK 15 数据面平台名扫描 ─────────────────────────────────

def test_bdd_15_check15_data_rules_platform_token_zero(agate_scripts, tmp_path):
    """BDD-15：数据面（rules/*.yaml + schema）平台词表命中数 = 0（词边界 + 豁免词典机械生成；
    task_fields/task_id 等既有键不误报）→ CHECK 15 不报。P3 无函数 → 红（B 类）；P4 实现后
    task_fields 键不误报 = 回归守卫语义。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(root, "rules/phases.yaml",
           "schema_version: 1\nphases:\n  - id: P1\n    task_fields: [risk_level]\n    name: 需求基线\n")
    _write(root, "rules/dispatch.yaml",
           "schema_version: 1\nmodes: [single, static-batch]\nfield_readers:\n"
           "  - {script: check-gate.py, phase: P2, fields: [task_id]}\n")
    _write(root, "rules/schema/phases.schema.json", '{"type":"object","properties":{"task_fields":{"type":"array"}}}\n')
    rep = cpc.Report()
    cpc.check_rules_platform_tokens(root, rep)  # P4 B3b 须实现（CHECK 15 数据面扫描 + 豁免词典）
    assert not _err15(rep), f"既有键（task_fields/task_id）不应误报；{rep.errors}"


def test_bdd_15_check15_inserted_bare_task_errors(agate_scripts, tmp_path):
    """BDD-15 反例：数据面插入裸平台词（DSH 于注释）→ CHECK 15 ERROR（词边界命中，豁免词典不含
    该语境）。P3 无函数 → 红（B 类）。"""
    cpc = _load_cpc(agate_scripts)
    root = tmp_path / "repo"
    _write(root, "rules/phases.yaml",
           "# DSH 平台适配注记（数据面禁平台名）\nschema_version: 1\nphases:\n  - id: P1\n    name: 需求基线\n")
    _write(root, "rules/dispatch.yaml", "schema_version: 1\nmodes: [single]\n")
    rep = cpc.Report()
    cpc.check_rules_platform_tokens(root, rep)  # P4 B3b 须实现（裸平台词 → ERROR）
    assert _err15(rep), "数据面插入裸平台词应报 CHECK 15 ERROR（BDD-15）"
