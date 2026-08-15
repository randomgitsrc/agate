# tests/unit/test_agate_state_get.py — 状态 YAML 读取共享工具
# （agate-state-get.bats 6 用例迁移，TAG0011 批次 2）
# 被测：agate/scripts/agate-state-get.py（STATE_FILE env 输入；phase / phase_stdin / task_id / retries_over）
# 流语义：STGET.2 / STGET.6 空输出断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest

LIMITS = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"


def _run_stget(agate_scripts, python_exe, run_cli, *args, input=None, state_file=None):
    env = None
    if state_file is not None:
        env = {"STATE_FILE": str(state_file)}
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-state-get.py"),
        *args,
        input=input,
        env=env,
    )


@pytest.mark.windows_smoke
def test_stget_1_phase_reads_state_yaml(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text("task_id: T001\nphase: P3\nstatus: active\n", encoding="utf-8")
    result = _run_stget(agate_scripts, python_exe, run_cli, "phase", state_file=state_file)
    assert result.returncode == 0
    assert result.output.strip() == "P3"


def test_stget_2_phase_empty_state_file_empty_string(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text("", encoding="utf-8")
    result = _run_stget(agate_scripts, python_exe, run_cli, "phase", state_file=state_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_stget_3_phase_stdin_reads_phase(agate_scripts, python_exe, run_cli):
    result = _run_stget(
        agate_scripts,
        python_exe,
        run_cli,
        "phase_stdin",
        input="task_id: T1\nphase: P5\n",
    )
    assert result.returncode == 0
    assert result.output.strip() == "P5"


def test_stget_4_task_id_reads_state_yaml(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text("task_id: T042\nphase: P1\n", encoding="utf-8")
    result = _run_stget(agate_scripts, python_exe, run_cli, "task_id", state_file=state_file)
    assert result.returncode == 0
    assert result.output.strip() == "T042"


def test_stget_5_retries_over_first_exceeding_phase(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T1\nphase: P3\nretries:\n  P1:\n    - {attempt: 1}\n    - {attempt: 2}\n    - {attempt: 3}\n",
        encoding="utf-8",
    )
    result = _run_stget(
        agate_scripts,
        python_exe,
        run_cli,
        "retries_over",
        LIMITS,
        state_file=state_file,
    )
    assert result.returncode == 0
    assert "P1=3 (MAX=3)" in result.output


def test_stget_6_retries_over_no_exceed_empty(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T1\nphase: P3\nretries:\n  P1:\n    - {attempt: 1}\n",
        encoding="utf-8",
    )
    result = _run_stget(
        agate_scripts,
        python_exe,
        run_cli,
        "retries_over",
        LIMITS,
        state_file=state_file,
    )
    assert result.returncode == 0
    assert result.output.strip() == ""
