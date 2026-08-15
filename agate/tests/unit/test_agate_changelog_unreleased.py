# tests/unit/test_agate_changelog_unreleased.py — Changelog Unreleased 提取
# （agate-changelog-unreleased.bats 2 用例迁移，TAG0011 批次 1）
# 被测：agate/scripts/agate-changelog-unreleased.py（CHANGELOG_FILE env 输入）
# 流语义：CL.2 空断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest


def _run_cl(agate_scripts, python_exe, run_cli, changelog_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-changelog-unreleased.py"),
        env={"CHANGELOG_FILE": str(changelog_file)},
    )


@pytest.mark.windows_smoke
def test_cl_1_extract_unreleased_section_content(agate_scripts, python_exe, run_cli, tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "## [Unreleased]\n"
        "### Added\n"
        "- T001 fix\n"
        "\n"
        "## [v0.33.0]\n"
        "- old\n",
        encoding="utf-8",
    )
    result = _run_cl(agate_scripts, python_exe, run_cli, changelog)
    assert result.returncode == 0
    assert "T001 fix" in result.output


def test_cl_2_no_unreleased_is_empty(agate_scripts, python_exe, run_cli, tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [v0.33.0]\n", encoding="utf-8")
    result = _run_cl(agate_scripts, python_exe, run_cli, changelog)
    assert result.returncode == 0
    assert result.output == ""
