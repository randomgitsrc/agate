# tests/unit/test_agate_gate_p5_count.py — P5 命令计数工具
# （agate-gate-p5-count.bats 3 用例迁移，TAG0011 批次 1）
# 被测：agate/scripts/agate-gate-p5-count.py（GATE_FILE env 输入，stdout 输出 "N M"）
# 流语义回归锁（P2 §5 批次 1 / P3 §4）：脚本写 stderr 的内容必须被合并流 .output 命中，
# 防止后续批把 $output 等价断言漂移映射为 .stdout。

import pytest


def _run_gpc(agate_scripts, python_exe, run_cli, gate_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-gate-p5-count.py"),
        env={"GATE_FILE": str(gate_file)},
    )


@pytest.mark.windows_smoke
def test_gpc_1_count_main_and_aux_commands(agate_scripts, python_exe, run_cli, tmp_path):
    gate_file = tmp_path / "P2.md"
    gate_file.write_text(
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P5_unit: pytest unit\n"
        "  P5_e2e: npx vitest\n",
        encoding="utf-8",
    )
    result = _run_gpc(agate_scripts, python_exe, run_cli, gate_file)
    assert result.returncode == 0
    assert result.output.strip() == "1 2"


def test_gpc_2_no_gate_commands_block_counts_zero(agate_scripts, python_exe, run_cli, tmp_path):
    gate_file = tmp_path / "P2.md"
    gate_file.write_text("无 gate_commands\n", encoding="utf-8")
    result = _run_gpc(agate_scripts, python_exe, run_cli, gate_file)
    assert result.returncode == 0
    assert result.output.strip() == "0 0"


def test_gpc_3_formatter_excluded_from_aux(agate_scripts, python_exe, run_cli, tmp_path):
    gate_file = tmp_path / "P2.md"
    gate_file.write_text(
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P5_formatter: pytest.sh\n",
        encoding="utf-8",
    )
    result = _run_gpc(agate_scripts, python_exe, run_cli, gate_file)
    assert result.returncode == 0
    assert result.output.strip() == "1 0"


def test_stream_lock_stderr_hits_merged_output(agate_scripts, python_exe, run_cli, tmp_path):
    # 流语义回归锁：无占位符时 agate-card-inject.py 写失败信息到 stderr 并 exit 1。
    # bats $output = stdout + stderr 合并流（P2 BLOCKER-1）→ 断言必须用 result.output
    # 命中 stderr 内容；仅映射 .stdout 会静默漏掉，此锁防漂移。
    dc = tmp_path / "dc.md"
    card = tmp_path / "card.md"
    dc.write_text("no placeholder\n", encoding="utf-8")
    card.write_text("card\n", encoding="utf-8")
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-card-inject.py"),
        env={"DC_FILE": str(dc), "CARD_FILE": str(card)},
    )
    assert result.returncode != 0
    assert "注入失败" in result.stderr
    assert "注入失败" not in result.stdout
    assert "注入失败" in result.output
