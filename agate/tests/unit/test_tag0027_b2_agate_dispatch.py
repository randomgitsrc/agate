# agate/tests/unit/test_tag0027_b2_agate_dispatch.py — TAG0027 B2 批：agate dispatch 渲染时注入
# + 两路并存（BDD-18/19/25）
#
# 被测契约（P2-design §3.5 定案 D5-A + §3.6 A2 机制）：
#   BDD-18 新增 agate/scripts/agate-dispatch.py {phase} {role} [TASK_DIR] [--guide FILE]（P4 新建）：
#          模板骨架 + Lazy Injection（子进程 agate-next-card.py 取卡）；产物 = {phase}-dispatch-
#          context-{role}.md，含完整卡片块（AGATE_CARD_START/END 内与 next-card stdout 逐字一致），
#          frontmatter phase/generated_by: agate-dispatch.py + 主 Agent/task_id/role；
#          CARD-SOURCE 注释置于 START 之前（块外）；exit 0/1
#   BDD-19 手工路径保留：占位符文件 + agate-inject-card.py 注入 exit 0 且卡片写入占位符块，
#          文件过 pre-commit 2p hash（抽取 START..END == next-card stdout 归一化）
#   BDD-25 两路（自动/手工）dispatch-context 均满足 2p：START..END 内嵌抽取 hash == next-card
#          stdout hash（CARD-SOURCE 在块外不入抽取区间 = A2 机制）
#
# TDD 红灯语义：被测 = 新增 agate-dispatch.py（P3 缺失 → rc 2 can't open file → 断言失败 =
#   B 类真红灯）；agate-inject-card.py / agate-next-card.py / pre-commit-gate.py 均为既有脚本
#   （现状存在，直接调用断言 = 回归/行为）。不 mock 被测对象。
# 平台无关：tmp_path fixture；无 /tmp 字面量；显式 utf-8。卡片 hash 比较用 CRLF 归一化
# （test_agate_next_card 同款约定）。

import hashlib
import re

import pytest

_START = "<!-- AGATE_CARD_START -->"
_END = "<!-- AGATE_CARD_END -->"
_SOURCE = "<!-- CARD-SOURCE: agate-dispatch.py"


def _extract_card_text(text):
    """pre-commit-gate.py _extract_card 同款：START..END 之间（不含标记行），CR 剥离。"""
    out = []
    in_block = False
    for line in text.splitlines():
        if not in_block:
            if _START in line:
                in_block = True
            continue
        if _END in line:
            break
        out.append(line.replace("\r", ""))
    return "\n".join(out)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalized_next_card_expected(cli_out):
    """2p 期望 hash 口径：agate-next-card stdout 去 CR 去尾换行（pre-commit-gate.py 425-437）。"""
    return _sha256(cli_out.replace("\r", "").rstrip("\n"))


def _run_next_card(agate_scripts, python_exe, run_cli, phase):
    return run_cli(python_exe, str(agate_scripts / "agate-next-card.py"), phase)


def _write_placeholder_dc(td, phase, role):
    """手工占位符 dispatch-context（模板结构，含 AGATE_CARD_START/END 占位）。"""
    (td / f"{phase}-dispatch-context-{role}.md").write_text(
        "---\n"
        f"phase: {phase}\n"
        "generated_by: agate-inject-card.py + 主 Agent\n"
        f"task_id: T001\n"
        f"role: {role}\n"
        "---\n"
        "\n"
        "<dispatch_guide>\n"
        "### 目标\n"
        "测试\n"
        "</dispatch_guide>\n"
        "\n"
        f"{_START}\n"
        "旧占位\n"
        f"{_END}\n",
        encoding="utf-8",
    )


def _make_dispatch_render_dc(td, phase, role):
    """手工构造 agate-dispatch 渲染产物形态：CARD-SOURCE 块外 + START..END 内卡片（测试夹具用）。"""
    (td / f"{phase}-dispatch-context-{role}.md").write_text(
        "---\n"
        f"phase: {phase}\n"
        "generated_by: agate-dispatch.py + 主 Agent\n"
        f"task_id: T001\n"
        f"role: {role}\n"
        "---\n"
        "\n"
        "<dispatch_guide>\n"
        "### 目标\n"
        "测试\n"
        "</dispatch_guide>\n"
        "\n"
        f"<!-- CARD-SOURCE: agate-dispatch.py {phase} -->\n"
        f"{_START}\n"
        "# 卡片正文（P4 渲染时注入 next-card stdout）\n"
        f"{_END}\n",
        encoding="utf-8",
    )


# ── BDD-18：agate dispatch 单命令渲染时注入 ────────────────────────────

def test_bdd_18_dispatch_render_injects_full_card(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-18：跑 agate-dispatch P3 test-designer → 产物含完整卡片块（START..END 内抽取 ==
    agate-next-card P3 body 归一化 hash）+ frontmatter generated_by 含 agate-dispatch.py。
    P3 agate-dispatch.py 缺失 → 红灯（B 类）。"""
    td = tmp_path / "task"
    td.mkdir()
    script = agate_scripts / "agate-dispatch.py"
    result = run_cli(python_exe, str(script), "P3", "test-designer", str(td))
    assert result.returncode == 0, f"agate-dispatch exit 0 预期；当前 rc={result.returncode}"
    dc = td / "P3-dispatch-context-test-designer.md"
    assert dc.is_file(), "dispatch-context 产物缺失（BDD-18）"
    text = dc.read_text(encoding="utf-8")
    assert "generated_by: agate-dispatch.py" in text, "frontmatter generated_by 应为 agate-dispatch.py"
    embedded = _extract_card_text(text)
    assert embedded.strip(), "卡片块为空（Lazy Injection 未注入完整卡片）"
    expected = _run_next_card(agate_scripts, python_exe, run_cli, "P3")
    assert expected.returncode == 0
    assert _sha256(embedded) == _normalized_next_card_expected(expected.output), (
        "嵌入卡片与 agate-next-card stdout 不一致（2p hash 前提，BDD-18/25）"
    )


def test_bdd_18_dispatch_card_source_marker_outside_block(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-18：CARD-SOURCE 标记在 AGATE_CARD_START 之前（块外）——不进 _extract_card 抽取区间
    （A2 机制：2p hash 不受影响）。P3 红灯。"""
    td = tmp_path / "task"
    td.mkdir()
    script = agate_scripts / "agate-dispatch.py"
    result = run_cli(python_exe, str(script), "P6", "verifier", str(td))
    assert result.returncode == 0, f"agate-dispatch exit 0 预期；rc={result.returncode}"
    dc = td / "P6-dispatch-context-verifier.md"
    assert dc.is_file()
    text = dc.read_text(encoding="utf-8")
    src_pos = text.find("<!-- CARD-SOURCE:")
    start_pos = text.find(_START)
    assert src_pos != -1, "渲染产物缺 CARD-SOURCE 来源标记（§3.5 结构）"
    assert start_pos != -1 and src_pos < start_pos, "CARD-SOURCE 必须在 AGATE_CARD_START 之前（块外）"


# ── BDD-19：手工路径保留 ───────────────────────────────────────────────

def test_bdd_19_manual_inject_card_kept_exit_0(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-19：手工占位符 + agate-inject-card.py P3 注入 → exit 0 且卡片块写入占位符块
    （方案 A 落地后手工路径不被破坏 = 两路并存兜底）。"""
    td = tmp_path / "task"
    td.mkdir()
    _write_placeholder_dc(td, "P3", "test-designer")
    result = run_cli(
        python_exe, str(agate_scripts / "agate-inject-card.py"), "P3", str(td)
    )
    assert result.returncode == 0, f"inject-card 手工注入应 exit 0；{result.output}"
    text = (td / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8")
    assert _START in text and _END in text
    embedded = _extract_card_text(text)
    assert embedded.strip() and "旧占位" not in embedded, "卡片未写入占位符块（BDD-19）"


def test_bdd_19_manual_path_2p_hash_pass_anchor(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-19 2p 锚点：手工注入产物 START..END 内嵌 hash == agate-next-card P3 期望 hash
    （手工路径过 pre-commit 2p = 现状语义，A2 机制下不破坏）。"""
    td = tmp_path / "task"
    td.mkdir()
    _write_placeholder_dc(td, "P3", "test-designer")
    result = run_cli(
        python_exe, str(agate_scripts / "agate-inject-card.py"), "P3", str(td)
    )
    assert result.returncode == 0, result.output
    embedded = _extract_card_text(
        (td / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8")
    )
    expected = _run_next_card(agate_scripts, python_exe, run_cli, "P3")
    assert expected.returncode == 0
    assert _sha256(embedded) == _normalized_next_card_expected(expected.output), (
        "手工注入产物 2p hash mismatch（BDD-19/25）"
    )


# ── BDD-25：两路 dispatch-context 均满足 2p 与 provenance 冻结 ──────────

def test_bdd_25_two_paths_dispatch_context_hash_equal(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-25：两路生成物（自动 dispatch 渲染 / 手工 inject-card）的 START..END 内嵌抽取 hash
    相等且 == next-card 期望 hash（CARD-SOURCE 不入抽取区间 → 两路 gate 行为无差异）。"""
    # 手工路
    td_manual = tmp_path / "task-manual"
    td_manual.mkdir()
    _write_placeholder_dc(td_manual, "P3", "test-designer")
    r_manual = run_cli(
        python_exe, str(agate_scripts / "agate-inject-card.py"), "P3", str(td_manual)
    )
    assert r_manual.returncode == 0, r_manual.output
    manual_hash = _sha256(
        _extract_card_text(
            (td_manual / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8")
        )
    )
    # 自动路（agate-dispatch 产物）
    td_auto = tmp_path / "task-auto"
    td_auto.mkdir()
    r_auto = run_cli(
        python_exe, str(agate_scripts / "agate-dispatch.py"), "P3", "test-designer", str(td_auto)
    )
    assert r_auto.returncode == 0, f"自动路径应成功；rc={r_auto.returncode}"
    auto_hash = _sha256(
        _extract_card_text(
            (td_auto / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8")
        )
    )
    expected = _run_next_card(agate_scripts, python_exe, run_cli, "P3")
    assert expected.returncode == 0
    assert manual_hash == auto_hash == _normalized_next_card_expected(expected.output), (
        "两路 dispatch-context 卡片 hash 应一致且等于 next-card 期望（BDD-25）"
    )


def test_bdd_25_auto_dispatch_card_hash_matches_next_card(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-25（A2 机制锚点）：含 CARD-SOURCE（块外）+ START..END 内嵌 next-card stdout 的
    dispatch-context 产物，其 _extract_card 抽取 hash == next-card 期望 hash——CARD-SOURCE 在
    START 前不入抽取区间 → 2p 天然兼容（§3.5/§3.6）。本用例夹具卡片区直接取真实 agate-next-card
    stdout（agate-dispatch P4 实现后产出的形态与此一致），是纯抽取口径不变量：现状即绿，P4
    后仍绿（防 A2 机制回归）；"agate-dispatch 真能产出该形态"由 test_bdd_18（红灯）覆盖。"""
    td = tmp_path / "task"
    td.mkdir()
    expected = _run_next_card(agate_scripts, python_exe, run_cli, "P3")
    assert expected.returncode == 0
    stdout_body = expected.output.replace("\r", "").rstrip("\n")
    # §3.5 渲染产物结构：dispatch_guide → CARD-SOURCE（块外）→ START → next-card stdout 全文 → END
    (td / "P3-dispatch-context-test-designer.md").write_text(
        "---\nphase: P3\ngenerated_by: agate-dispatch.py + 主 Agent\ntask_id: T001\n"
        "role: test-designer\n---\n\n<dispatch_guide>\n### 目标\n测试\n</dispatch_guide>\n\n"
        "<!-- CARD-SOURCE: agate-dispatch.py P3 -->\n"
        f"{_START}\n{stdout_body}\n{_END}\n",
        encoding="utf-8",
    )
    text = (td / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8")
    src_pos = text.find("<!-- CARD-SOURCE:")
    start_pos = text.find(_START)
    assert src_pos != -1 and src_pos < start_pos, "CARD-SOURCE 应在 START 之前（A2 结构前提）"
    embedded = _extract_card_text(text)
    assert _sha256(embedded) == _sha256(stdout_body), "START..END 抽取应还原卡片正文"
    assert _sha256(embedded) == _normalized_next_card_expected(expected.output), (
        "渲染产物 2p hash mismatch（A2：CARD-SOURCE 不入抽取区间 → hash == next-card 期望）"
    )
