# tests/unit/test_agate_gate_missing_cmds.py — gate_commands 缺失命令检测
# （agate-gate-missing-cmds.bats 2 用例迁移，TAG0011 批次 1）
# 被测：agate/scripts/agate-gate-missing-cmds.py（GATE_FILE env 输入，stdout 输出 key:token）
# 流语义：GMC.2 空断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest


def _run_gmc(agate_scripts, python_exe, run_cli, gate_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-gate-missing-cmds.py"),
        env={"GATE_FILE": str(gate_file)},
    )


@pytest.mark.windows_smoke
def test_gmc_1_extract_command_tokens_as_key_token(agate_scripts, python_exe, run_cli, tmp_path):
    gate_file = tmp_path / "P2.md"
    gate_file.write_text(
        "gate_commands:\n"
        "  P3: pytest -q\n"
        "  P3_formatter: pytest.sh\n"
        "  P5: npx vitest\n",
        encoding="utf-8",
    )
    result = _run_gmc(agate_scripts, python_exe, run_cli, gate_file)
    assert result.returncode == 0
    assert "P3:pytest" in result.output
    assert "P5:npx" in result.output
    assert "formatter" not in result.output


def test_gmc_2_tokens_with_slash_or_equals_skipped(agate_scripts, python_exe, run_cli, tmp_path):
    gate_file = tmp_path / "P2.md"
    gate_file.write_text(
        "gate_commands:\n"
        "  P3: .venv/bin/python -m pytest\n"
        "  P5: A=1 pytest\n",
        encoding="utf-8",
    )
    result = _run_gmc(agate_scripts, python_exe, run_cli, gate_file)
    assert result.returncode == 0
    assert result.output == ""
