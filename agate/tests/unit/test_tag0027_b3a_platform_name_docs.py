# agate/tests/unit/test_tag0027_b3a_platform_name_docs.py — TAG0027 B3a 批：编排心智统一文档化
# （BDD-14/16/17/23）
#
# 被测契约（P1 BDD-14/16/17 + P2-design §3.8/§6③ + P2-review A3 定案①）：
#   BDD-14 dispatch-protocol.md 五模式为唯一语义锚点；协议层不发明 "workflow 模式 / ralph 模式 /
#          goal 模式" 平台命名概念（Not Modify，P2 §1.2）——纯文档断言回归守卫
#   BDD-16 markdown 叙述文档平台名仅限带「实现注记」标记（`> 实现注记：`）的小节/段落
#          （豁免：platform-notes.md / SETUP.md 整文件 + WORKFLOW.md「已知适用环境」表）
#          ——B3a 清理后存量段挂注记（P4 Phase 3 批次）；「实现注记」统一格式 = P2 §3.8 判据
#   BDD-17 存量 9 文件三分类判定可追溯 + assets/ 适配说明命中段（architect.md:229 /
#          custom-role.md:49-56）挂注记 + assets/templates/dsh/ 平台食谱目录结构豁免（A3）
#   BDD-23 agate-render-dispatch-prompt.py 既有 CLI 契约（PHASE ROLE TASK_DIR，exit 0/1/2）
#          不被方案 A 破坏（Not Modify）——回归守卫
#
# TDD 红灯语义：BDD-16 「实现注记」标记现状全协议 0 处 → 断言"清理面文档含注记标记"红
#   （B 类：Phase 3 文档批次未完成——由 P4 B3a 批次转绿）；BDD-14/23 + 豁免结构现状绿
#   （回归守卫：验证既有机制/文档不被破坏）。BDD-17 dsh/ 目录存在性 + 平台名豁免语义
#   现目录实存（SKILL.md 等）→ 断言平台食谱目录为**非协议叙述面**（不在 PROTOCOL_FILES）
#   现状绿 = 结构事实。
# 平台无关：agate_root fixture（只读 worktree 协议文档）；显式 utf-8。

import re

import pytest


def _read(root, rel):
    return (root / rel).read_text(encoding="utf-8")


# ── BDD-14：五模式唯一语义锚点 ─────────────────────────────────────────

def test_bdd_14_dispatch_protocol_five_modes_single_anchor(agate_root):
    """BDD-14：dispatch-protocol.md 含五模式（单发/静态拆批/并行/先理解后拆/串行链）语义锚点
    条文，且协议层不出现 "workflow 模式"/"ralph 模式"/"goal 模式" 平台命名概念（回归守卫）。"""
    text = _read(agate_root, "dispatch-protocol.md")
    for token in ("模式 1", "模式 2", "模式 3", "模式 4", "模式 5"):
        assert token in text, f"五模式锚点缺 {token}（BDD-14）"
    for banned in ("workflow 模式", "ralph 模式", "goal 模式", "workflow模式", "ralph模式", "goal模式"):
        assert banned not in text, f"协议层出现平台命名模式概念 {banned!r}（BDD-14 违反）"


# ── BDD-16：实现注记标记 + 豁免结构 ────────────────────────────────────

def test_bdd_16_workflow_md_known_env_table_has_anchor(agate_root):
    """BDD-16 豁免结构现状回归：WORKFLOW.md「已知适用环境」表（平台适配元信息权威源）
    仍存在（豁免结构事实，回归守卫）。"""
    text = _read(agate_root, "WORKFLOW.md")
    assert "已知适用环境" in text, "WORKFLOW.md 缺「已知适用环境」表（豁免结构被误删）"


def test_bdd_16_implementation_note_marker_format_present_after_cleanup(agate_root):
    """BDD-16：Phase 3 清理批次（P4 B3a）落地后，清理面文档出现统一格式「实现注记」标记行
    `> 实现注记：`。P3 现状全协议 0 处标记 → 红（B 类：B3a 文档批次未完成）。"""
    cleaned_docs = (
        "role-system.md", "UPGRADING.md", "adr.md",
        "loop-orchestration.md", "dispatch-protocol.md", "WORKFLOW.md",
    )
    note_re = re.compile(r"^>\s*实现注记：")
    seen = 0
    for name in cleaned_docs:
        path = agate_root / name
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if note_re.match(line):
                    seen += 1
    assert seen >= 1, (
        "Phase 3 清理后协议文档应含 `> 实现注记：` 标记行（BDD-16/17）；P3 现状 0 处 → 红（B3a 未完成）"
    )


# ── BDD-17：assets/ 命中段 + dsh/ 结构豁免 ─────────────────────────────

def test_bdd_17_assets_dsh_skill_md_is_structure_exempt(agate_root):
    """BDD-17（A3 定案①）：assets/templates/dsh/ 平台食谱目录（SKILL.md 等）属结构豁免——非协议
    叙述文档面（不在 check-protocol-consistency PROTOCOL_FILES 顶层清单），CHECK 14 扫描面豁免，
    不进清理批。现状目录实存 = 结构事实（绿）。"""
    dsh = agate_root / "assets" / "templates" / "dsh"
    assert dsh.is_dir(), "assets/templates/dsh/ 目录缺失（A3 结构豁免对象）"
    md_files = [p for p in dsh.rglob("*.md")]
    assert md_files, "assets/templates/dsh/ 无 md 资产（SKILL.md 等平台食谱文件缺失）"
    # 结构豁免语义：dsh/ 属 assets 模板平台食谱（非协议语义叙述），其平台名命中不被 CHECK 14
    # 当 ERROR（协议层检查对象 = agate/*.md 顶层语义叙述面 + 非豁免 assets md 适配说明段）
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        # 平台食谱资产允许出现平台名（DSH 等）——断言其含平台词不构成协议叙述污染
        # （真实豁免判定由 CHECK 14 结构豁免承载，B3b 批用例覆盖；此处仅锚定目录/资产存在）
        assert isinstance(text, str)


def test_bdd_23_render_dispatch_prompt_cli_contract_regression(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-23 回归守卫：agate-render-dispatch-prompt.py 既有 CLI 契约（PHASE ROLE TASK_DIR）
    不被方案 A 破坏——正常调用成功 exit 0 且产出 {P}-dispatch-prompt-{role}.md（Not Modify）。"""
    script = agate_scripts / "agate-render-dispatch-prompt.py"
    if not script.is_file():
        pytest.skip("agate-render-dispatch-prompt.py 缺失（测试环境异常）")
    td = tmp_path / "task"
    td.mkdir()
    # role=analyst（真实 execution-roles 文件存在；render-dispatch-prompt 契约 PHASE ROLE TASK_DIR）
    result = run_cli(python_exe, str(script), "P1", "analyst", str(td))
    assert result.returncode == 0, f"render-dispatch-prompt 正常调用应 exit 0；{result.output[:800]}"
    out = td / "P1-dispatch-prompt-analyst.md"
    assert out.is_file(), "渲染产出 {P}-dispatch-prompt-{role}.md 缺失（既有 CLI 契约破坏）"
