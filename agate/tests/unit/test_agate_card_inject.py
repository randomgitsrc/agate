# tests/unit/test_agate_card_inject.py — agate-card-inject.py 工具单元测试
# （agate-card-inject.bats 2 用例迁移，TAG0011 批次 1）
# 被测：agate/scripts/agate-card-inject.py（DC_FILE / CARD_FILE env 输入，写回 DC_FILE）
# 流语义：无占位符 → stderr 写失败信息 + exit 1（stderr 归属 + 合并流见流语义回归锁）

import pytest


def _run_ic(agate_scripts, python_exe, run_cli, dc_file, card_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-card-inject.py"),
        env={"DC_FILE": str(dc_file), "CARD_FILE": str(card_file)},
    )


@pytest.mark.windows_smoke
def test_ic_1_inject_card_between_placeholders(agate_scripts, python_exe, run_cli, tmp_path):
    dc = tmp_path / "dc.md"
    card = tmp_path / "card.md"
    dc.write_text(
        "pre\n<!-- AGATE_CARD_START -->\nold\n<!-- AGATE_CARD_END -->\npost\n",
        encoding="utf-8",
    )
    card.write_text("newcard\n", encoding="utf-8")
    result = _run_ic(agate_scripts, python_exe, run_cli, dc, card)
    assert result.returncode == 0
    injected = dc.read_text(encoding="utf-8")
    assert "newcard" in injected
    assert "old" not in injected


def test_ic_2_no_placeholder_exits_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    dc = tmp_path / "dc.md"
    card = tmp_path / "card.md"
    dc.write_text("no placeholder\n", encoding="utf-8")
    card.write_text("card\n", encoding="utf-8")
    result = _run_ic(agate_scripts, python_exe, run_cli, dc, card)
    assert result.returncode != 0
