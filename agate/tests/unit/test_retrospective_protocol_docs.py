# tests/unit/test_retrospective_protocol_docs.py — 复盘协议文档条文守护（TAG0015 新增）
# 覆盖 P1-requirements.md 的 13 条纯文档类 BDD：BDD-1/2/3/4/5/6/7/8（模板正文结构，
# agate/assets/templates/retrospective-template.md）/BDD-12/13（state-machine.md orchestrator-log
# 语义扩展 + L2 会话 checkpoint）/BDD-14（跨文件同步一致）/BDD-15（AGENTS.md 措辞同步）/
# BDD-16（docs/reviews/ 存量文件标注）。
# 风格参照 test_review_role_docs.py：agate_root fixture（tests/conftest.py:306）+ 逐 BDD 一个
# test_bdd_N_xxx 函数 + 纯文本读取 + 子串断言，不 import 被测协议文档为 Python 模块。
# 验收对象层次说明（dispatch-context 约束 1c）：本文件只断言"协议文档是否定义了规则/结构"，
# 不断言某次任务运行时产物（如 P{n}-checkpoint.md 是否真的存在）——后者是 P6 verifier 的职责。
# 红灯预期：agate/assets/templates/retrospective-template.md 尚不存在（P4 才迁移+改写），
# 其余文档改动点均未落地，本文件全部测试函数当前预期失败（P2-design.md §6「实现完成的标志」
# 逐条对应本文件断言）。


def _read(agate_root, *parts):
    return agate_root.joinpath(*parts).read_text(encoding="utf-8")


def _read_repo(agate_root, *parts):
    """读取仓库根（agate_root 的父目录）下的文件，用于 docs/reviews/ 等协议本体之外的路径。"""
    return agate_root.parent.joinpath(*parts).read_text(encoding="utf-8")


TEMPLATE_PARTS = ("assets", "templates", "retrospective-template.md")

LEGACY_RETRO_FILES = [
    "retrospective-tag0008-docs-20260817.md",
    "retrospective-tag0010-0011-docs-20260815.md",
    "retrospective-tag0010-0011-docs-20260815-review.md",
    "retrospective-tag0013-docs-20260816.md",
    "retrospective-tag0014-docs-20260816.md",
]


# ── 类 4.1：retrospective-template.md 正文结构（BDD-1~8） ────────────────────


def test_bdd_1_template_defines_four_body_sections(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "事实基线" in content
    assert "做得好的" in content
    assert "发现的问题" in content
    assert "改进措施" in content
    # 迁移完成：旧路径不再以旧内容存在（git mv，非留 stub）
    old_path = agate_root.parent / "docs" / "reviews" / "postmortem-template.md"
    assert not old_path.exists()


def test_bdd_2_template_declares_content_value_criteria(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "内容价值标准" in content
    assert "机制缺口" in content
    assert "可复用模式" in content
    assert "可行动层面" in content


def test_bdd_3_template_attribution_layer_field(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "归因层面" in content
    assert "机制缺口" in content
    assert "执行错误" in content
    assert "两者都是" in content  # 二值语义的显式禁止说明（不允许"两者都是"）


def test_bdd_4_template_debt_registration_mandatory_note(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "DEBT" in content
    assert "roadmap" in content
    assert "待定" in content  # "不允许留空或写'待定'" 强制说明


def test_bdd_5_template_asset_precipitation_prompt(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？" in content
    assert "回馈 agate" in content
    assert "项目资产沉淀" in content


def test_bdd_6_template_frontmatter_machine_fields(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "mechanism_issues" in content
    assert "execution_issues" in content
    assert "feedback_ready" in content


def test_bdd_7_template_agate_feedback_section(agate_root):
    content = _read(agate_root, *TEMPLATE_PARTS)
    assert "## agate 反馈" in content
    assert "不涉及项目敏感信息" in content


def test_bdd_8_template_hooked_into_protocol_body(agate_root):
    content = _read(agate_root, "phase-cards", "P8-release.md")
    assert "agate/assets/templates/retrospective-template.md" in content


# ── 类 4.3：state-machine.md（orchestrator-log 语义扩展 + L2 checkpoint） ────


def test_bdd_12_orchestrator_log_decision_and_rationale(agate_root):
    content = _read(agate_root, "state-machine.md")
    # 三项既有排除原样保留
    assert "不写思考过程、不写文件内容摘要、不写 subagent 返回原文" in content
    # 新增"依据"分句
    assert "简要依据" in content
    # 旧的限制性表述（"只写决策和下一步"，无顿号）已被"只写决策、下一步和…依据"取代
    assert "只写决策和下一步" not in content


def test_bdd_13_l2_checkpoint_docs(agate_root):
    content = _read(agate_root, "state-machine.md")
    heading_idx = content.find("L2 会话 checkpoint")
    assert heading_idx != -1
    assert "P{n}-checkpoint.md" in content
    assert "task-session-summary.md" in content
    assert content.find("P{n}-checkpoint.md", heading_idx) > heading_idx
    assert content.find("task-session-summary.md", heading_idx) > heading_idx


# ── 类 4.4：跨文件同步一致（BDD-14，Given 前置于 BDD-12 已完成） ─────────────


def test_bdd_14_cross_file_orchestrator_log_consistency(agate_root):
    sm = _read(agate_root, "state-machine.md")
    # Given 前置条件：state-machine.md 已完成 BDD-12 扩展
    assert "简要依据" in sm
    loop = _read(agate_root, "loop-orchestration.md")
    task_files = _read(agate_root, "assets", "templates", "task-files.md")
    # 两处引用点均未逐字复述已被 BDD-12 扩展的旧限制性表述，不与新语义矛盾
    assert "只写决策和下一步" not in loop
    assert "只写决策和下一步" not in task_files


# ── 类 4.5：AGENTS.md 复盘位置措辞同步（BDD-15） ─────────────────────────────


def test_bdd_15_agents_md_retrospective_location_split(agate_root):
    content = _read(agate_root, "AGENTS.md")
    assert "tasks/{Txxx}/retrospective.md" in content
    assert "历史复盘" in content


# ── 类 4.6：docs/reviews/ 存量复盘文档标注（BDD-16） ─────────────────────────


def test_bdd_16_legacy_retrospectives_annotated(agate_root):
    for name in LEGACY_RETRO_FILES:
        content = _read_repo(agate_root, "docs", "reviews", name)
        assert "历史复盘" in content, f"{name} 缺少历史复盘标注行"
        assert "tasks/{Txxx}/retrospective.md" in content, f"{name} 未指向新复盘路径"
