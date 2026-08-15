# tests/unit/test_check_scope_resolved.py — SCOPE+ 处理追踪
# （check-scope-resolved.bats 10 用例迁移，TAG0011 批次 6c）
# 被测：agate/scripts/check-scope-resolved.py（TASK_DIR；exit 0 = 通过 / exit 1 = SCOPE+ 未处理 /
#   exit 2 = 无 task 目录）。
# task_dir 等价 create_task_dir；add_p1_field 等价 fixtures.bash helper（frontmatter 块写入）。
# 流语义：GATE SCOPE 消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest

from conftest import add_p1_field


def _run_scope(agate_scripts, python_exe, run_cli, task_arg):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-scope-resolved.py"),
        task_arg,
    )


@pytest.mark.windows_smoke
def test_sc_1_nonexistent_task_dir_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    d = tmp_path / "nonexistent-task"

    result = _run_scope(agate_scripts, python_exe, run_cli, str(d))
    assert result.returncode == 2


def test_sc_2_no_scope_plus_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text("# P2 design\n正常文档，无 SCOPE+ 标记\n", encoding="utf-8")

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_3_scope_plus_no_p1_file_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    d = tmp_path / "task"
    d.mkdir()
    (d / "P2-design.md").write_text("# P2 design\n[SCOPE+] 新增功能\n", encoding="utf-8")

    result = _run_scope(agate_scripts, python_exe, run_cli, str(d))
    assert result.returncode == 1
    assert "无 P1-requirements.md" in result.output


def test_p2_53_progress_file_excluded_from_scope_scan(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P4", "P5", "P6", "P7", "P8"])
    (td / "P2-progress.md").write_text(
        "## P2 progress\n- [SCOPE+] 检查: 无新增隐含需求\n",
        encoding="utf-8",
    )
    p1 = td / "P1-requirements.md"
    p1.write_text(
        p1.read_text(encoding="utf-8") + "- [SCOPE_RESOLVED] test\n",
        encoding="utf-8",
    )

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_dp1_dispatch_prompt_excluded_from_scope_scan(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P4-dispatch-prompt-implementer.md").write_text(
        "> render product\n- [SCOPE+] this should be ignored\n",
        encoding="utf-8",
    )

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_4_scope_plus_no_resolved_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text("# P2 design\n[SCOPE+] 新增功能\n", encoding="utf-8")

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "SCOPE_RESOLVED" in result.output


def test_sc_5_scope_plus_with_resolved_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text("# P2 design\n[SCOPE+] 新增功能\n", encoding="utf-8")
    p1 = td / "P1-requirements.md"
    p1.write_text(
        p1.read_text(encoding="utf-8") + "\n[SCOPE_RESOLVED] 已纳入 v0.7\n",
        encoding="utf-8",
    )

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_bdd22_1_scope_plus_frontmatter_scope_resolved_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P2-design.md").write_text("# P2 design\n[SCOPE+] 新增功能\n", encoding="utf-8")
    add_p1_field(td, "scope_resolved", "[新增功能已纳入 v0.7]")

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_6_dispatch_context_excluded_from_scope_scan(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P4-dispatch-context-implementer.md").write_text(
        "---\n"
        "phase: P4\n"
        "task_id: T001\n"
        "role: implementer\n"
        "---\n"
        "\n"
        "<dispatch_guide>\n"
        "### 约束\n"
        "如果发现需求与设计矛盾，标 [SCOPE+] 而非直接做\n"
        "</dispatch_guide>\n",
        encoding="utf-8",
    )

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_sc_7_inline_scope_plus_not_line_start_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text("# P2 design\n检查了 [SCOPE+] 的引用情况\n", encoding="utf-8")

    result = _run_scope(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0
