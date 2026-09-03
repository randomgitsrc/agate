# tests/unit/test_tag0030_assertions.py — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）
# grep 断言审计测试（TAG0027 批量改动 TDD 策略）
#
# 背景：TAG0030 是纯协议文档面改造批次（phase-cards + assets/roles + assets/templates +
# tests/README + 仓库根 AGENTS.md）。P1-requirements.md 的 BDD-1~21 性质特殊——不是常规业务
# 功能断言，而是"协议卡/评审角色/派发模板/测试约定是否含特定新增条文/关键词"的存在性断言。
#
# 组织方式参照 agate/tests/unit/test_review_role_docs.py（_read + 逐条 assert），并吸收
# test_protocol_mechanism_anchors.py（TAG0012）的锚词纪律：关键词从 P2-design.md §2 改动详述 /
# §0.1 落点表「改动一句话」列**逐字复用**（不意译/不改写）——P4 implementer 落地时也用同一批词。
#
# 假绿规避说明（TAG0012 BDD-5 教训）：写每条用例前已核实目标关键词当前命中数——
#   * plan-design-review.md 既有条文已含「布局型」（行 19 常规布局型任务启用）、
#     「渲染正确性/动效时序/形态」（行 21 渲染正确性与时序维度行）、「0-10」（行 13）、
#     「status」（行 32-35）——这些词单关键词断言当前即为真（假绿），相关 BDD（11/12/14/15）
#     改为 AND 语义，至少一个当前 0 命中的新锚词兜底（三组/渲染组件型+architect/原文保留/回落），
#     保证整体断言现在为假。
#   * architect.md 已含「对齐」（行 111 时间戳对齐、行 221 批次边界对齐），与视觉契约五类
#     （宽度/高度/对齐/重叠/溢出）语义不同——BDD-16/17 不用「对齐」作唯一锚词，改用
#     「视觉契约/可表达子集/不收主观视觉」等当前 0 命中的词。
#   * BDD-20 载体 AGENTS.md 在仓库根（agate_root.parent），不在 agate/ 内（P2-review G2）。
#
# 此时（P3 阶段）协议文件尚未被本任务改动，全部用例当前失败（红灯）——这是本任务的 TDD 证据。
# P4 逐条落地后转绿；任一条文被后续改动删除即转红（BDD-6 回归防线）。
# BDD-6 特别说明：BDD-6 断言的是"断言审计单测本身"（本测试文件存在 + 锁定 Phase 1 载体）——
# 用例 test_bdd_6_phase1_audit_lock 汇总断言 P3/P4/P6 卡 + dispatch-context 模板的 Phase 1
# 锚词（清理钩子/残留检查/环境还原），与 BDD-1~5 同源同词，当前同样全 0 命中（红）。
#
# 平台无关：仅 read_text + `in`，无 shell grep、无 /tmp、无裸 python3（DSH 测试约定硬约束）。

import pytest


def _read_repo(agate_root, rel_path):
    """读仓库根（agate_root.parent）下相对路径文件；AGENTS.md 即 rel_path="AGENTS.md"。"""
    return agate_root.parent.joinpath(rel_path).read_text(encoding="utf-8")


# ── Phase 1（BDD-1~6）：测试副作用/环境还原 gate（RM-AG0057-①）──


@pytest.mark.windows_smoke
def test_bdd_1_p3_card_cleanup_hook(agate_root):
    """BDD-1：P3 卡声明创建型测试清理钩子要求（P2 §2 Phase 1 锚词：清理钩子/创建即注册）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P3-tdd.md")
    assert "清理钩子" in content
    assert "创建即注册" in content


@pytest.mark.windows_smoke
def test_bdd_2_p4_card_cleanup_hook(agate_root):
    """BDD-2：P4 卡同步声明创建型测试清理要求（与 P3 卡同源同锚词）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P4-implementation.md")
    assert "清理钩子" in content
    assert "创建即注册" in content


@pytest.mark.windows_smoke
def test_bdd_3_cleanup_delete_semantics(agate_root):
    """BDD-3：清理钩子规则含「无条件删除 + 接受 200/204/404」（afterEach 清理队列模式）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P3-tdd.md")
    assert "无条件删除" in content
    assert "200/204/404" in content


@pytest.mark.windows_smoke
def test_bdd_4_p6_residue_check(agate_root):
    """BDD-4：P6 卡补 post-test 环境残留检查步骤（快照比对或清理钩子验证）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P6-acceptance.md")
    assert "残留检查" in content
    assert "post-test" in content


@pytest.mark.windows_smoke
def test_bdd_5_dispatch_context_cleanup_slot(agate_root):
    """BDD-5：dispatch-context 模板声明环境清理/还原/残留检查约束条目位。"""
    content = _read_repo(agate_root, "agate/assets/templates/dispatch-context.md")
    assert "环境还原" in content
    assert "残留检查" in content


def test_bdd_6_phase1_audit_lock(agate_root):
    """BDD-6：断言审计单测锁定 Phase 1 新增条文（回归防线）——本测试文件对 P3/P4/P6 卡
    路径 + 锚词及 dispatch-context 模板路径 + 锚词的 grep 断言（汇总 BDD-1/2/4/5 载体，
    当前全 0 命中 → 红；P4 落地后转绿，条文被删即转红）。
    """
    p3 = _read_repo(agate_root, "agate/phase-cards/P3-tdd.md")
    p4 = _read_repo(agate_root, "agate/phase-cards/P4-implementation.md")
    p6 = _read_repo(agate_root, "agate/phase-cards/P6-acceptance.md")
    tmpl = _read_repo(agate_root, "agate/assets/templates/dispatch-context.md")
    assert "清理钩子" in p3
    assert "清理钩子" in p4
    assert "残留检查" in p6
    assert "环境还原" in tmpl


# ── Phase 2（BDD-7~9）：P1 人工体验路径验收节（RM-AG0057-②）──


@pytest.mark.windows_smoke
def test_bdd_7_p1_card_manual_experience(agate_root):
    """BDD-7：P1 卡声明「人工体验路径验收」节（seed 影响页面内容 → 强制补 seed BDD）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P1-requirements.md")
    assert "人工体验" in content
    assert "seed" in content


@pytest.mark.windows_smoke
def test_bdd_8_analyst_manual_experience(agate_root):
    """BDD-8：analyst 角色文件声明同一条人工体验验收要求（与 P1 卡同源）。"""
    content = _read_repo(agate_root, "agate/assets/execution-roles/analyst.md")
    assert "人工体验" in content
    assert "seed" in content


@pytest.mark.windows_smoke
def test_bdd_9_seed_content_bdd_required(agate_root):
    """BDD-9：「Given seed 数据 → 页面有内容」成为 BDD 强制句式（P1 卡条文锁定）。"""
    content = _read_repo(agate_root, "agate/phase-cards/P1-requirements.md")
    assert "seed 数据" in content
    assert "页面有内容" in content


# ── Phase 3（BDD-10~15）：plan-design-review 形态驱动化（RM-AG0057-③）──


@pytest.mark.windows_smoke
def test_bdd_10_shape_dispatch_header(agate_root):
    """BDD-10：plan-design-review 先读受评任务 ui_render_shape 再加载维度组评分细则
    （「ui_render_shape」当前 0 命中；「形态」行 21 已命中故不作唯一锚词）。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "ui_render_shape" in content
    assert "维度组" in content


@pytest.mark.windows_smoke
def test_bdd_11_layout_dimension_group(agate_root):
    """BDD-11：布局型形态加载布局/交互/视觉三组（「布局型」行 19 已命中 → AND「三组」，
    三组当前 0 命中保证整体为假）。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "布局型" in content
    assert "三组" in content


@pytest.mark.windows_smoke
def test_bdd_12_render_component_group(agate_root):
    """BDD-12：渲染组件型加载渲染正确性/动效时序组并交叉引用 architect 渲染 checklist
    （「渲染正确性/动效时序」行 21 已命中 → AND「渲染组件型」+「architect」，均当前 0 命中）。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "渲染组件型" in content
    assert "architect" in content


@pytest.mark.windows_smoke
def test_bdd_13_two_candidates_tradeoff(agate_root):
    """BDD-13：每个启用维度要求布局方案 ≥2 候选 + 权衡说明（candidate_count 下沉 UI 布局层）。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "候选" in content
    assert "权衡" in content


@pytest.mark.windows_smoke
def test_bdd_14_score_status_preserved(agate_root):
    """BDD-14：0-10 评分输出 + status 字段保持（门槛读 status 契约不破坏）——
    「0-10/status」当前已命中（行 13/32-35，既有门槛契约，保持性断言）→ AND「原文保留」
    （P2 §2 Phase 3 逐字锚词，当前 0 命中）保证整体现在为假。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "0-10" in content
    assert "status" in content
    assert "原文保留" in content


@pytest.mark.windows_smoke
def test_bdd_15_default_layout_fallback(agate_root):
    """BDD-15：无形态声明时回落布局型默认（既有行为兼容）——「回落」当前 0 命中
    （「布局型」行 19 已命中 → AND「回落」保证整体为假）。"""
    content = _read_repo(agate_root, "agate/assets/review-roles/plan-design-review.md")
    assert "回落" in content
    assert "布局型" in content


# ── Phase 4（BDD-16~21）：视觉契约断言收录 + DEBT0024/25/26 ──


@pytest.mark.windows_smoke
def test_bdd_16_visual_contract_expressible(agate_root):
    """BDD-16：视觉契约「可表达子集」定义收录（只收五类 DOM 度量，不收主观视觉）
    ——落点 architect.md 视觉 checklist 头部（P2 §3 pin 定）；「对齐」行 111/221 已命中
    （语义不同）故不作锚词。"""
    content = _read_repo(agate_root, "agate/assets/execution-roles/architect.md")
    assert "视觉契约" in content
    assert "可表达子集" in content


@pytest.mark.windows_smoke
def test_bdd_17_architect_checklist_dom_metric(agate_root):
    """BDD-17：architect 视觉 checklist 提及可量化 DOM 度量断言（同文件一次落笔）。"""
    content = _read_repo(agate_root, "agate/assets/execution-roles/architect.md")
    assert "DOM 度量" in content
    assert "不收主观视觉" in content


@pytest.mark.windows_smoke
def test_bdd_18_verifier_dom_evidence(agate_root):
    """BDD-18：P6/verifier 指南提及 E2E DOM 度量断言为截图之外的非截图量化证据。"""
    content = _read_repo(agate_root, "agate/assets/execution-roles/verifier.md")
    assert "DOM 度量" in content
    assert "getBoundingClientRect" in content


@pytest.mark.windows_smoke
def test_bdd_19_real_gate_semantics(agate_root):
    """BDD-19：tests/README「何时更新」节写明 gate 消费方测试夹具走真实 gate 语义
    （DEBT0024 closure，不 stub/mock 假 exit）。"""
    content = _read_repo(agate_root, "agate/tests/README.md")
    assert "真实 gate 语义" in content


@pytest.mark.windows_smoke
def test_bdd_20_full_scan_before_check(agate_root):
    """BDD-20：AGENTS.md「改脚本的工作流」节写明新增 CHECK 上线前先全量扫描存量
    （DEBT0025 closure；AGENTS.md 在仓库根 agate_root.parent）。"""
    content = _read_repo(agate_root, "AGENTS.md")
    assert "全量扫描" in content
    assert "新增 CHECK" in content


@pytest.mark.windows_smoke
def test_bdd_21_split_by_volume(agate_root):
    """BDD-21：dispatch-context 模板含大任务拆小默认指导（DEBT0026 closure，
    >5 文件/大文档按体量评估拆小，与 TAG0028 内部自主拆互补）。"""
    content = _read_repo(agate_root, "agate/assets/templates/dispatch-context.md")
    assert "拆小" in content
    assert "体量" in content
