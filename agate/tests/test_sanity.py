# tests/test_sanity.py — 框架 sanity check（sanity.bats 6 用例迁移，TAG0011 批次 0）
# conftest 体系自检：agate_root / task_dir / git_repo 可正常 load 并执行。

import pytest

from conftest import add_pruning_excuse


@pytest.mark.windows_smoke
def test_sanity_1_load_bash_agate_root_resolution(agate_root):
    assert (agate_root / "scripts").is_dir()
    assert (agate_root / "assets").is_dir()
    assert (agate_root / "tests").is_dir()


def test_sanity_2_fixtures_bash_create_task_dir_default_phases(task_dir):
    d = task_dir()
    assert (d / ".state.yaml").is_file()
    assert (d / "P0-brief.md").is_file()
    assert (d / "P1-requirements.md").is_file()
    assert (d / "P2-design.md").is_file()
    assert (d / "P8-release.md").is_file()


def test_sanity_3_fixtures_bash_create_task_dir_custom_phases(task_dir):
    d = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    assert (d / "P0-brief.md").is_file()
    assert not (d / "P2-design.md").exists()


def test_sanity_4_fixtures_bash_add_pruning_excuse_writes(task_dir):
    d = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    add_pruning_excuse(d, "P2", "无设计必要", "低风险")
    text = (d / "P1-requirements.md").read_text(encoding="utf-8")
    assert "裁剪 P2" in text
    assert "跳过风险" in text


def test_sanity_5_git_helper_git_init_creates_valid_repo(git_repo):
    assert (git_repo.path / ".git").is_dir()


def test_sanity_6_git_helper_git_commit_and_stage_work(git_repo):
    (git_repo.path / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init commit")
    log = git_repo.git("log", "--oneline").stdout
    assert len([line for line in log.splitlines() if line.strip()]) == 1
