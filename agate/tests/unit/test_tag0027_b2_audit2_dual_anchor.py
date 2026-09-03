# agate/tests/unit/test_tag0027_b2_audit2_dual_anchor.py — TAG0027 B2 批：审计 2 双锚点剥离
# （BDD-20/21）
#
# 被测契约（P2-design §3.6 定案 D6-A）：
#   BDD-20 渲染产物（P6 dispatch-context，含 `<!-- CARD-SOURCE: agate-dispatch.py P6 -->` 于
#          AGATE_CARD_START **之前** + START..END 内卡片正文含 PASS/FAIL 模板字样）→
#          check-p6-provenance.py 审计 2 exit 0（剥离锚点 = CARD-SOURCE 行起物理块优先，
#          卡片模板含 PASS/FAIL 字样不误报"验收结论预判"）
#   BDD-21 手工注入文件（物理 AGATE_CARD_START/END 占位符块，无 CARD-SOURCE）→ 审计 2 exit 0
#          （既有物理块剥离兜底路径，A2 定案：双锚点并存，START..END 兜底）
#   剥离后逻辑不变：剥卡片块 → 剥 frontmatter → 数行首 `- PASS|FAIL` 预判。
#
# TDD 红灯语义：BDD-20 两用例 = 扩展点行为（P3 现状 check-p6-provenance.py 审计 2 只认
#   AGATE_CARD_START 物理块，CARD-SOURCE 行在块外不被剥离 → 渲染产物含 CARD-SOURCE 行残余？
#   不——CARD-SOURCE 行在 START 之前，物理块剥离只剥 START..END，CARD-SOURCE 行 + dispatch
#   正文保留；若正文行首无 PASS/FAIL → 现状 exit 0（绿）？需让场景对现状红：
#   断言改为"剥离区间含 CARD-SOURCE 行起物理块"不可直接观测；改用行为断言：渲染产物卡片
#   正文含 PASS/FAIL 模板行 + CARD-SOURCE 在 START 前 → 审计 2 必须 exit 0。现状：审计 2 只剥
#   START..END → START 前 CARD-SOURCE 行保留（非 PASS/FAIL 行首 → 不误报）→ 卡片正文 PASS/FAIL
#   在 START..END 内被剥 → exit 0 现状也绿？——场景退化为回归守卫。为使该扩展点对现状红，
#   断言"剥离后文件体不含 CARD-SOURCE 行"（§3.6 剥离起点语义）→ 现状保留 CARD-SOURCE → 红。
#   故 BDD-20 用例 2 用「剥离后无 CARD-SOURCE/START/END 残余」断言现状红；用例 1（exit 0 不误报）
#   为回归守卫现状绿（P4 双锚点后仍绿）。BDD-21 手工物理块回归守卫现状绿。
# 平台无关：tmp_path/task_dir fixture + run_cli(python_exe,...)；显式 utf-8。


_START = "<!-- AGATE_CARD_START -->"
_END = "<!-- AGATE_CARD_END -->"
_SOURCE = "<!-- CARD-SOURCE: agate-dispatch.py P6 -->"


def _run_prov(agate_scripts, python_exe, run_cli, td):
    return run_cli(python_exe, str(agate_scripts / "check-p6-provenance.py"), str(td))


def _write_p6_and_p1(td):
    """P6-acceptance + P1 BDD（provenance 审计 1/3 前置：PASS 引用证据 + BDD 计数）。"""
    (td / "P1-requirements.md").write_text(
        "---\nagent: test\n---\n#### BDD-1: test\n- Given g\n- When w\n- Then t\n",
        encoding="utf-8",
    )
    (td / "P6-acceptance.md").write_text(
        "---\nphase: P6\ntask_id: T001\nagent: verifier\npass: 1\nfail: 0\n---\n"
        "- PASS BDD-1: verified (e1.json)\n",
        encoding="utf-8",
    )
    ev = td / "P6-evidence"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "e1.json").write_text("evidence\n", encoding="utf-8")


_CARD_WITH_PASS_FAIL = (
    "## 当前阶段卡片：P6\n"
    "- PASS BDD-1 pre-judged (card template text)\n"
    "- FAIL BDD-2 pre-judged (card template text)\n"
)


def _render_dc_with_card_source(td):
    """渲染产物形态（§3.5）：CARD-SOURCE 在 START 之前（块外）+ START..END 内卡片含 PASS/FAIL 模板。"""
    (td / "P6-dispatch-context-verifier.md").write_text(
        "---\nphase: P6\ntask_id: T001\nrole: verifier\n"
        "generated_by: agate-dispatch.py + 主 Agent\n---\n\n"
        "<dispatch_guide>\n### 目标\n验收\n</dispatch_guide>\n\n"
        f"{_SOURCE}\n"
        f"{_START}\n{_CARD_WITH_PASS_FAIL}{_END}\n",
        encoding="utf-8",
    )


def test_bdd_20_audit2_render_product_with_card_source_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-20 回归守卫：渲染产物（CARD-SOURCE 块外 + 卡片含 PASS/FAIL 模板）→ 审计 2 exit 0
    （卡片块被剥离，不因模板 PASS/FAIL 误报预判）。现状（物理块剥离）与 P4（双锚点）均应绿。"""
    td = task_dir()
    _write_p6_and_p1(td)
    _render_dc_with_card_source(td)
    result = _run_prov(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"渲染产物卡片块应被剥离不误报；{result.output[:800]}"


def test_bdd_20_audit2_pass_before_start_requires_dual_anchor(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-20 双锚点剥离起点的真红灯锚点：CARD-SOURCE 行与 START 之间放置行首 `- PASS` 预判行
    （双锚点剥离 = CARD-SOURCE 行起整段剥 → 该行也被剥 → exit 0）；单锚点（只剥 START..END）
    会保留该行 → 预判误报 exit 1。P3 现状 = 单锚点 → 本用例红（B 类：双锚点剥离未实现）。"""
    td = task_dir()
    _write_p6_and_p1(td)
    (td / "P6-dispatch-context-verifier.md").write_text(
        "---\nphase: P6\ntask_id: T001\nrole: verifier\n"
        "generated_by: agate-dispatch.py + 主 Agent\n---\n\n"
        "<dispatch_guide>\n### 目标\n验收\n</dispatch_guide>\n\n"
        f"{_SOURCE}\n"
        "- PASS BDD-9 pre-judged (between source and card, must be stripped with dual anchor)\n"
        f"{_START}\n{_CARD_WITH_PASS_FAIL}{_END}\n",
        encoding="utf-8",
    )
    result = _run_prov(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, (
        f"双锚点剥离应把 CARD-SOURCE 起整段（含 START 前 PASS 行）剥掉 → exit 0；"
        f"现状单锚点保留该行 → 误报 exit {result.returncode}（B 类红，扩展点未实现）"
    )


def test_bdd_21_audit2_manual_physical_block_fallback_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-21 回归守卫：手工注入文件（物理 AGATE_CARD_START/END 占位符块，无 CARD-SOURCE）
    含 PASS/FAIL 卡片行 → 审计 2 exit 0（既有物理块剥离兜底路径在新机制下继续工作）。"""
    td = task_dir()
    _write_p6_and_p1(td)
    (td / "P6-dispatch-context-verifier.md").write_text(
        "---\nphase: P6\ntask_id: T001\nrole: verifier\n"
        "generated_by: agate-inject-card.py + 主 Agent\n---\n\n"
        "<dispatch_guide>\n### 目标\n验收\n</dispatch_guide>\n\n"
        f"{_START}\n{_CARD_WITH_PASS_FAIL}{_END}\n",
        encoding="utf-8",
    )
    result = _run_prov(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"手工物理块剥离兜底应 exit 0；{result.output[:800]}"
