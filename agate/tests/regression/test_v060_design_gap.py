# tests/regression/test_v060_design_gap.py — 回归测试：DESIGN_GAP 配对（check-gate.py P7）
# （v060-design-gap.bats 4 用例迁移，TAG0011 批次 11）
# 触发：cf6cd80 "feat(v0.6): DESIGN_GAP" 提交新机制；R2.3 已修复：P4/P7 DESIGN_GAP 数量交叉核对。
# T001 v2.0 流 B（BDD-20）改写：配对判定改读 P7 frontmatter 的 design_gap_count /
#   design_gap_reviewed_count（结构化计数），不再用正文数量相减的 0-vs-0 歧义判定（F14 消除）。
#   [DESIGN_GAP]/[DESIGN_GAP_REVIEWED] 散文标记保留为人类痕迹。
# 流语义：GATE P7 消息一律 sys.stderr.write → 断言用合并流 result.output（P2 §3.2，BLOCKER-1）。

import pytest


def _run_gate(agate_scripts, python_exe, run_cli, phase, task_arg):
    return run_cli(python_exe, str(agate_scripts / "check-gate.py"), phase, task_arg)


def _write_p7(td, body):
    (td / "P7-consistency.md").write_text(body, encoding="utf-8")


_P7_FM_HEAD = (
    "---\n"
    "phase: P7\n"
    "task_id: T001\n"
    "agent: consistency-reviewer\n"
    "blocker_count: 0\n"
    "deviation_count: 0\n"
    "deviation_critical_count: 0\n"
)


@pytest.mark.windows_smoke
def test_r2_1_gap_paired_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(
        td,
        _P7_FM_HEAD
        + "design_gap_count: 1\n"
        + "design_gap_reviewed_count: 1\n"
        + "---\n"
        + "- [DESIGN_GAP: P2 未指定错误处理]\n"
        + "- [DESIGN_GAP_REVIEWED: 已确认]\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0


def test_r2_2_gap_unpaired_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(
        td,
        _P7_FM_HEAD
        + "design_gap_count: 1\n"
        + "design_gap_reviewed_count: 0\n"
        + "---\n"
        + "- [DESIGN_GAP: P2 未指定错误处理]\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1


def test_r2_3_p4_gap_not_copied_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P4-implementation.md").write_text(
        "---\nagent: test\n---\n- [DESIGN_GAP: P2 未指定错误处理]\n", encoding="utf-8"
    )
    _write_p7(
        td,
        _P7_FM_HEAD
        + "design_gap_count: 0\n"
        + "design_gap_reviewed_count: 0\n"
        + "---\n"
        + "一致性检查完成。\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "P4" in result.output
    assert "DESIGN_GAP" in result.output
    assert "P7" in result.output


def test_r2_3b_p4_gap_copied_and_reviewed_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P4-implementation.md").write_text(
        "---\nagent: test\n---\n- [DESIGN_GAP: P2 未指定错误处理]\n", encoding="utf-8"
    )
    _write_p7(
        td,
        _P7_FM_HEAD
        + "design_gap_count: 1\n"
        + "design_gap_reviewed_count: 1\n"
        + "---\n"
        + "- [DESIGN_GAP: P2 未指定错误处理]\n"
        + "- [DESIGN_GAP_REVIEWED: 已确认]\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0
