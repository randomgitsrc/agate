# tests/unit/test_check_retrospective.py — 复盘异常触发（gate 重试超限 / SCOPE+ / override）
# （check-retrospective.bats 10 用例迁移，TAG0011 批次 7）
# 被测：agate/scripts/check-retrospective.py（TASK_DIR [STATE_FILE]；总是 exit 0，只提醒）。
# GATE RETRO 提醒消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，本文件断言一律用
#   合并流 result.output（等价 bats $output，BLOCKER-1）。RT.1/RT.6/RT.7 三处
#   `[ -z "$output" ]` → 合并流空断言 result.output == ""。
# RT_BDD21.1 走 check-gate.py P1（need_confirm_resolved 结构化匹配，exit 2）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest


def _run_retro(agate_scripts, python_exe, run_cli, td):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-retrospective.py"),
        str(td),
        str(td / ".state.yaml"),
    )


def _run_gate_p1(agate_scripts, python_exe, run_cli, td):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-gate.py"),
        "P1",
        str(td),
    )


def _insert_override_after_phases(p1_file):
    """等价 bats `sed -i '/^phases:/a override: P2 retained'`。"""
    lines = p1_file.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        out.append(line)
        if line.startswith("phases:"):
            out.append("override: P2 retained")
    p1_file.write_text("\n".join(out) + "\n", encoding="utf-8")


@pytest.mark.windows_smoke
def test_rt_1_no_anomaly_exit_0_empty_output(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert result.output == ""


def test_rt_2_retries_over_exit_0_warns(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / ".state.yaml").write_text(
        "task_id: T001\n"
        "phase: PAUSED\n"
        "status: active\n"
        "retries:\n"
        "  P2:\n"
        "    - attempt: 1\n"
        "    - attempt: 2\n"
        "    - attempt: 3\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "重试超限" in result.output


def test_rt_bdd21_1_need_confirm_resolved_not_blocking(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: draft\n"
        "agent: analyst\n"
        'need_confirm_resolved: ["z 的边界条件需确认"]\n'
        "---\n"
        "# Requirements\n"
        "- Given x When y Then z\n"
        "- [NEED_CONFIRM] z 的边界条件需确认\n",
        encoding="utf-8",
    )
    (td / "P1-review.md").write_text(
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS\n",
        encoding="utf-8",
    )

    result = _run_gate_p1(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 2


def test_rt_dp1_dispatch_prompt_excluded_from_scope_scan(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P4-dispatch-prompt-implementer.md").write_text(
        "> render product\n- [SCOPE+] this should be ignored\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "SCOPE+" not in result.output


def test_rt_4_override_triggers(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _insert_override_after_phases(td / "P1-requirements.md")

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "override" in result.output


def test_rt_5_p3_two_retries_triggers_over(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / ".state.yaml").write_text(
        "task_id: T001\n"
        "phase: PAUSED\n"
        "status: active\n"
        "retries:\n"
        "  P3:\n"
        "    - attempt: 1\n"
        "    - attempt: 2\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "重试超限" in result.output


def test_rt_6_p3_one_retry_no_trigger_empty_output(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / ".state.yaml").write_text(
        "task_id: T001\n"
        "phase: P4\n"
        "status: active\n"
        "retries:\n"
        "  P3:\n"
        "    - attempt: 1\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert result.output == ""


def test_rt_7_inline_scope_plus_not_line_start_empty_output(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P2-design.md").write_text(
        "检查了 [SCOPE+] 的引用情况\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert result.output == ""


def test_retro_scope_dc_1_dispatch_context_excluded_from_scope_scan(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P6-dispatch-context-verifier.md").write_text(
        "- [SCOPE+] 发现：新增功能需重新验收\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "SCOPE+" not in result.output


def test_retro_scope_card_1_agate_card_block_excluded_from_scope_scan(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P2-design.md").write_text(
        "设计内容\n"
        "<!-- AGATE_CARD_START -->\n"
        "- [SCOPE+] 示例：范围扩展\n"
        "<!-- AGATE_CARD_END -->\n"
        "正常设计\n",
        encoding="utf-8",
    )

    result = _run_retro(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert "SCOPE+" not in result.output
