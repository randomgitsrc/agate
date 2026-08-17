# tests/unit/test_review_role_docs.py — TAG0006 UI/UX 机制协议文档条文守护
# 覆盖 BDD-1/2/5/6/11/12/13/16/17 的"协议文档含要求条文"验收方式（P1 §3 验收方式①）。
# 被测：agate 协议文档（analyst.md / architect.md / verifier.md / plan-design-review.md /
#   role-system.md / phase-cards/P1-requirements.md / phase-cards/P6-acceptance.md /
#   dispatch-protocol.md / assets/templates/dispatch-prompt.md）是否含 P4 将新增的
#   UI/UX 机制条文（分类框架 / 渲染正确性维度 / 形态声明要求 / 证据按形态选择等锚点词）。
# 文档漂移保护：P4 实现后全绿；P3（实现前）锚点词全部缺席 → 红灯（B 类断言失败）。
# 平台无关：仅读文件文本（encoding="utf-8"），无路径/进程假设。
# 无单测 BDD 说明：BDD-7（Windows GUI 评估）/BDD-8（影响面清单）验收对象是本任务自身
#   P2-design.md（agate-workspace 任务工件，CI 无该路径）→ P6 verifier 读取核对；
#   BDD-15（回归）由 gate_commands 实跑覆盖（P2 §2.14）。


def _read(agate_root, *parts):
    return agate_root.joinpath(*parts).read_text(encoding="utf-8")


def test_bdd_1_analyst_classification_framework(agate_root):
    content = _read(agate_root, "assets", "execution-roles", "analyst.md")
    assert "分类框架" in content
    assert "渲染形态" in content


def test_bdd_1_p1_card_classification_framework(agate_root):
    content = _read(agate_root, "phase-cards", "P1-requirements.md")
    assert "分类框架" in content


def test_bdd_2_analyst_quantitative_criteria(agate_root):
    content = _read(agate_root, "assets", "execution-roles", "analyst.md")
    assert "渲染正确性" in content
    assert "动效时序" in content
    assert "可量化判据" in content


def test_bdd_5_architect_ui_design_section(agate_root):
    content = _read(agate_root, "assets", "execution-roles", "architect.md")
    assert "UI 设计" in content
    assert "兼任" in content


def test_bdd_5_role_system_architect_dual_hats(agate_root):
    content = _read(agate_root, "role-system.md")
    assert "UI 设计节由 architect 兼任产出" in content


def test_bdd_6_plan_design_review_dimensions(agate_root):
    content = _read(agate_root, "assets", "review-roles", "plan-design-review.md")
    assert "视觉设计" in content
    assert "交互设计" in content
    assert "渲染正确性与时序" in content


def test_bdd_11_dispatch_prompt_injection_guidance(agate_root):
    content = _read(agate_root, "assets", "templates", "dispatch-prompt.md")
    assert "视觉能力" in content
    assert "获取指引" in content


def test_bdd_11_dispatch_protocol_a3_vision(agate_root):
    content = _read(agate_root, "dispatch-protocol.md")
    assert "视觉能力" in content


def test_bdd_12_dispatch_prompt_self_check(agate_root):
    content = _read(agate_root, "assets", "templates", "dispatch-prompt.md")
    assert "能力自查" in content
    assert "先自查能否调用视觉能力" in content


def test_bdd_13_verifier_input_state_review(agate_root):
    content = _read(agate_root, "assets", "execution-roles", "verifier.md")
    assert "人工复核" in content
    assert "输入态" in content


def test_bdd_13_p6_card_input_state_review(agate_root):
    content = _read(agate_root, "phase-cards", "P6-acceptance.md")
    assert "人工复核" in content
    assert "输入态" in content


def test_bdd_16_render_component_dim_requirements(agate_root):
    p1_card = _read(agate_root, "phase-cards", "P1-requirements.md")
    analyst = _read(agate_root, "assets", "execution-roles", "analyst.md")
    assert "渲染形态" in p1_card
    assert "渲染正确性" in p1_card
    assert "动效时序" in p1_card
    assert "手势交互" in analyst
    assert "特效" in analyst


def test_bdd_17_verifier_evidence_form_by_shape(agate_root):
    content = _read(agate_root, "assets", "execution-roles", "verifier.md")
    assert "帧序列" in content
    assert "时序截图" in content
    assert "渲染输出对比" in content


def test_bdd_17_p6_card_evidence_form_by_shape(agate_root):
    content = _read(agate_root, "phase-cards", "P6-acceptance.md")
    assert "帧序列" in content
    assert "时序截图" in content
    assert "渲染输出对比" in content