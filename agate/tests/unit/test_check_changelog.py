# tests/unit/test_check_changelog.py — CHANGELOG [Unreleased] 含 task_id 检查
# （check-changelog.bats 8 用例迁移，TAG0011 批次 7）
# 被测：agate/scripts/check-changelog.py（TASK_ID；cwd 下 CHANGELOG.md；
#   exit 0 = 通过 / exit 1 = 未记录 / 无 CHANGELOG 文件时 exit 0）。
# git_repo fixture 承接 bats `git_init` + `cd "$repo"`；run_cli(..., cwd=repo) 等价
#   bats `cd "$repo" && "$PYTHON" "$AGATE_SCRIPTS/check-changelog.py" T001`。
# 流语义：GATE CHANGELOG 失败消息 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest


def _run_changelog(agate_scripts, python_exe, run_cli, repo, task_id):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-changelog.py"),
        task_id,
        cwd=str(repo),
    )


@pytest.mark.windows_smoke
def test_cl_1_no_changelog_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "T001")
    assert result.returncode == 0


def test_cl_2_changelog_no_unreleased_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [v0.5.0] - 2026-01-01\n- 已发布\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "T001")
    assert result.returncode == 1
    assert "无 [Unreleased]" in result.output


def test_cl_3_unreleased_no_task_id_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [Unreleased]\n- 其他内容\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "T001")
    assert result.returncode == 1
    assert "未找到 T001" in result.output


def test_cl_4_unreleased_with_task_id_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [Unreleased]\n- T001 任务完成\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "T001")
    assert result.returncode == 0


def test_cl_5_task_id_in_history_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [v0.5.0]\n- T001 旧版本\n\n## [Unreleased]\n- 新内容\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "T001")
    assert result.returncode == 1


def test_cl_6_bdd_27_full_new_task_id_matched_exit_0(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [Unreleased]\n\n### Fixed\n- TAG0001: 完成 v2.0 结构化改造\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "TAG0001")
    assert result.returncode == 0


def test_cl_7_bdd_27_longer_id_not_matched_exit_1(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [Unreleased]\n\n### Fixed\n- TAG00012: 其他任务条目\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "TAG0001")
    assert result.returncode == 1
    assert "未找到" in result.output


def test_cl_8_bdd_27_no_short_prefix_matching_exit_0(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "CHANGELOG.md").write_text(
        "## [Unreleased]\n\n### Fixed\n- TAG0001: 消除 check-changelog 短前缀提取摩擦\n",
        encoding="utf-8",
    )

    result = _run_changelog(agate_scripts, python_exe, run_cli, repo, "TAG0001")
    assert result.returncode == 0
