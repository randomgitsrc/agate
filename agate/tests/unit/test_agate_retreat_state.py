# tests/unit/test_agate_retreat_state.py — 回退状态读写专用工具
# （agate-retreat-state.bats 4 用例迁移，TAG0011 批次 2）
# 被测：agate/scripts/agate-retreat-state.py（STATE_FILE env 输入；check_retreat / write_retreat）
# 流语义：RSTATE.2 空输出断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest

LIMITS = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"


def _run_rstate(agate_scripts, python_exe, run_cli, *args, env=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-retreat-state.py"),
        *args,
        env=env,
    )


def _state_env(state_file, **extra):
    env = {"STATE_FILE": str(state_file)}
    env.update(extra)
    return env


@pytest.mark.windows_smoke
def test_rstate_1_check_retreat_over_limit_output_phase_count_limit(
    agate_scripts, python_exe, run_cli, tmp_path
):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T1\nphase: P4\nretries:\n  P3:\n    - {attempt: 1}\n    - {attempt: 2}\n",
        encoding="utf-8",
    )
    result = _run_rstate(
        agate_scripts,
        python_exe,
        run_cli,
        "check_retreat",
        LIMITS,
        env=_state_env(state_file, CUR="4", TGT="2"),
    )
    assert result.returncode == 0
    assert result.output.strip() == "P3:3:2"


def test_rstate_2_check_retreat_no_over_limit_empty(
    agate_scripts, python_exe, run_cli, tmp_path
):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T1\nphase: P4\nretries:\n  P3:\n    - {attempt: 1}\n",
        encoding="utf-8",
    )
    result = _run_rstate(
        agate_scripts,
        python_exe,
        run_cli,
        "check_retreat",
        LIMITS,
        env=_state_env(state_file, CUR="4", TGT="2"),
    )
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_rstate_3_write_retreat_appends_retry_and_rewrites(
    agate_scripts, python_exe, run_cli, tmp_path
):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T1\nphase: P4\nstatus: active\nretries:\n  P3:\n    - {attempt: 1, reason: x}\n",
        encoding="utf-8",
    )
    result = _run_rstate(
        agate_scripts,
        python_exe,
        run_cli,
        "write_retreat",
        env=_state_env(state_file, NEW_PHASE="P3", RETREAT_REASON="test reason"),
    )
    assert result.returncode == 0
    text = state_file.read_text(encoding="utf-8")
    assert "phase: P3" in text
    assert "attempt: 2" in text
    assert "test reason" in text


def test_bdd_7_write_retreat_chinese_reason(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text(
        "task_id: T001\nphase: P1\nstatus: active\nretries: {}\n",
        encoding="utf-8",
    )
    result = _run_rstate(
        agate_scripts,
        python_exe,
        run_cli,
        "write_retreat",
        env=_state_env(state_file, NEW_PHASE="P2", RETREAT_REASON="回退原因含中文"),
    )
    assert result.returncode == 0
    text = state_file.read_text(encoding="utf-8")
    assert "回退原因含中文" in text
    assert "phase: P2" in text
