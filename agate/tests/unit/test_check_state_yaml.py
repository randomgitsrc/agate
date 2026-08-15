# tests/unit/test_check_state_yaml.py — .state.yaml 格式校验
# （check-state-yaml.bats 9 用例迁移，TAG0011 批次 7）
# 被测：agate/scripts/check-state-yaml.py（[STATE_FILE]；exit 0 = 正确 / exit 1 = 错误 /
#   exit 2 = 无 .state.yaml）。GATE STATE-YAML 错误消息一律 sys.stderr.write →
#   按 P2 §3.2 先判流归属，本文件断言一律用合并流 result.output（等价 bats $output，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest


def _write_state(state_path, text):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(text, encoding="utf-8")


def _run_state(agate_scripts, python_exe, run_cli, state_path):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-state-yaml.py"),
        str(state_path),
    )


@pytest.mark.windows_smoke
def test_sy_1_no_state_file_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    assert not f.exists()

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 2


def test_sy_2_empty_file_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1


def test_sy_3_missing_task_id_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "phase: P1\nstatus: active\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "缺必填字段: task_id" in result.output


def test_sy_4_bad_task_id_format_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "task_id: T001a\nphase: P1\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "task_id 格式错误" in result.output


def test_sy_5_invalid_phase_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "task_id: T001\nphase: P9\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "phase 非法值" in result.output


def test_sy_6_retries_not_dict_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "task_id: T001\nphase: P1\nretries: 3\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "retries 应为 dict" in result.output


def test_sy_7_retries_p1_not_list_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "task_id: T001\nphase: P1\nretries:\n  P1: 3\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "retries[P1] 应为列表" in result.output


def test_sy_8_valid_exit_0(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(
        f,
        "task_id: TXX0001\n"
        "phase: P1\n"
        "status: active\n"
        "retries:\n"
        "  P2:\n"
        '    - attempt: 1\n'
        '      reason: "fail"\n',
    )

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 0


def test_sy_9_yaml_syntax_error_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    f = tmp_path / "state.yaml"
    _write_state(f, "task_id: T001\n  phase: P1: extra\n")

    result = _run_state(agate_scripts, python_exe, run_cli, f)
    assert result.returncode == 1
    assert "YAML 解析错误" in result.output
