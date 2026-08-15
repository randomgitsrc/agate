# tests/unit/test_agate_read_p5_commands.py — P5 gate_commands 解析器
# （agate-read-p5-commands.bats 4 用例迁移，TAG0011 批次 2）
# 被测：agate/scripts/agate-read-p5-commands.py（P2_DESIGN env 指向 md 文件，stdout 输出 JSON）
# 流语义：P5C.2 / P5C.3 空输出断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest


def _run_p5c(agate_scripts, python_exe, run_cli, p2_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-read-p5-commands.py"),
        env={"P2_DESIGN": str(p2_file)},
    )


@pytest.mark.windows_smoke
def test_p5c_1_p2_with_p5_and_formatters_output_commands(
    agate_scripts, python_exe, run_cli, tmp_path
):
    p2_file = tmp_path / "P2-design.md"
    p2_file.write_text(
        "---\nagent: test\n---\ngate_commands:\n"
        "  P5: pytest\n"
        "  P5_formatter: pytest.sh\n"
        "  P5_js: vitest run\n"
        "  P5_js_formatter: vitest.sh\n",
        encoding="utf-8",
    )
    result = _run_p5c(agate_scripts, python_exe, run_cli, p2_file)
    assert result.returncode == 0
    assert '"cmd": "pytest"' in result.output
    assert '"formatter": "pytest.sh"' in result.output
    assert '"cmd": "vitest run"' in result.output
    assert '"commands"' in result.output


def test_p5c_2_p2_empty_gate_commands_output_empty(agate_scripts, python_exe, run_cli, tmp_path):
    p2_file = tmp_path / "P2-design.md"
    p2_file.write_text("---\nagent: test\n---\ngate_commands: {}\n", encoding="utf-8")
    result = _run_p5c(agate_scripts, python_exe, run_cli, p2_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_p5c_3_p2_no_gate_commands_block_output_empty(agate_scripts, python_exe, run_cli, tmp_path):
    p2_file = tmp_path / "P2-design.md"
    p2_file.write_text("---\nagent: test\n---\n无 gate_commands\n", encoding="utf-8")
    result = _run_p5c(agate_scripts, python_exe, run_cli, p2_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_p5c_4_p5_quoted_values_stripped_with_formatter_link(
    agate_scripts, python_exe, run_cli, tmp_path
):
    p2_file = tmp_path / "P2-design.md"
    p2_file.write_text(
        "---\nagent: test\n---\ngate_commands:\n"
        '  P5: "pytest -q"\n'
        "  P5_html_formatter: vitest.sh\n"
        '  P5_html: "npx vitest"\n',
        encoding="utf-8",
    )
    result = _run_p5c(agate_scripts, python_exe, run_cli, p2_file)
    assert result.returncode == 0
    assert '"cmd": "pytest -q"' in result.output
    assert '"cmd": "npx vitest"' in result.output
    assert '"formatter": "vitest.sh"' in result.output
