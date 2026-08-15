# tests/unit/test_agate_archive_stale_outputs.py — agate-archive-stale-outputs.py 归档校验
# （agate-archive-stale-outputs.bats 7 用例迁移，TAG0011 批次 4）
# 被测：agate/scripts/agate-archive-stale-outputs.py（PHASE TASK_DIR，归档 .archived/ 下
#       {YYYYmmdd-HHMMSS}-{PHASE} 目录 + .retreat-history.md breadcrumb）
# 流语义：ARCH.2 输出断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）
# ARCH.4 flaky（时间戳）：归档目录名含秒级时间戳，两次归档用 time.sleep(1) 区分——
#       隔离单跑必过语义保留（P2 §7.2 R2.4 / 派发指引 ARCH.4）

import time

import pytest


def _run_archive(agate_scripts, python_exe, run_cli, *args):
    return run_cli(python_exe, str(agate_scripts / "agate-archive-stale-outputs.py"), *args)


def _archived_dirs(task_dir, phase):
    """find .archived -maxdepth 1 -type d -name "*-P6" 等价：归档目录列表。"""
    archived = task_dir / ".archived"
    if not archived.is_dir():
        return []
    return sorted(d for d in archived.iterdir() if d.is_dir() and d.name.endswith("-" + phase))


@pytest.mark.windows_smoke
def test_arch_1_p6_acceptance_and_evidence_archived(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task1"
    (task_dir / "P6-evidence" / "screenshots").mkdir(parents=True)
    (task_dir / "P6-acceptance.md").write_text("old p6 content\n", encoding="utf-8")
    (task_dir / "P6-evidence" / "screenshots" / "a.png").touch()

    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0
    assert not (task_dir / "P6-acceptance.md").exists()
    assert not (task_dir / "P6-evidence").exists()

    dirs = _archived_dirs(task_dir, "P6")
    assert len(dirs) == 1
    archived_dir = dirs[0]
    assert (archived_dir / "P6-acceptance.md").is_file()
    assert (archived_dir / "P6-evidence" / "screenshots" / "a.png").is_file()


def test_arch_2_p4_no_archive_needed(agate_scripts, python_exe, run_cli, tmp_path):
    task_dir = tmp_path / "task2"
    task_dir.mkdir()

    result = _run_archive(agate_scripts, python_exe, run_cli, "P4", str(task_dir))
    assert result.returncode == 0
    assert "无需归档" in result.output
    assert not (task_dir / ".archived").exists()


def test_arch_3_p6_evidence_missing_only_acceptance(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task3"
    task_dir.mkdir()
    (task_dir / "P6-acceptance.md").write_text("content\n", encoding="utf-8")

    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0
    assert not (task_dir / "P6-acceptance.md").exists()

    dirs = _archived_dirs(task_dir, "P6")
    assert len(dirs) == 1
    archived_dir = dirs[0]
    assert (archived_dir / "P6-acceptance.md").is_file()
    assert not (archived_dir / "P6-evidence").exists()


def test_arch_4_double_archive_keeps_both_histories(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task4"
    task_dir.mkdir()
    (task_dir / "P6-acceptance.md").write_text("first attempt\n", encoding="utf-8")

    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0
    time.sleep(1)

    (task_dir / "P6-acceptance.md").write_text("second attempt\n", encoding="utf-8")
    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0

    assert len(_archived_dirs(task_dir, "P6")) == 2


def test_arch_5_fail_breadcrumb_summary_and_not_archived(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task5"
    task_dir.mkdir()
    (task_dir / "P6-acceptance.md").write_text(
        "- PASS BDD-1: ok (screenshots/a.png)\n"
        "- FAIL BDD-7: 购物车金额错误 (screenshots/b.png)\n",
        encoding="utf-8",
    )

    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0
    breadcrumb = task_dir / ".retreat-history.md"
    assert breadcrumb.is_file()
    assert "FAIL BDD-7" in breadcrumb.read_text(encoding="utf-8")

    dirs = _archived_dirs(task_dir, "P6")
    assert len(dirs) == 1
    archived_dir = dirs[0]
    assert not (archived_dir / ".retreat-history.md").exists()


def test_arch_6_double_archive_breadcrumb_appends(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task6"
    task_dir.mkdir()
    (task_dir / "P6-acceptance.md").write_text(
        "- FAIL BDD-7: 第一次失败 (a.png)\n", encoding="utf-8"
    )
    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0
    time.sleep(1)
    (task_dir / "P6-acceptance.md").write_text(
        "- FAIL BDD-7: 第二次仍失败 (b.png)\n", encoding="utf-8"
    )
    result = _run_archive(agate_scripts, python_exe, run_cli, "P6", str(task_dir))
    assert result.returncode == 0

    text = (task_dir / ".retreat-history.md").read_text(encoding="utf-8")
    assert "第一次失败" in text
    assert "第二次仍失败" in text


def test_arch_7_p1_archives_requirements_and_review(
    agate_scripts, python_exe, run_cli, tmp_path
):
    task_dir = tmp_path / "task7"
    task_dir.mkdir()
    (task_dir / "P1-requirements.md").write_text("req\n", encoding="utf-8")
    (task_dir / "P1-review.md").write_text("review\n", encoding="utf-8")

    result = _run_archive(agate_scripts, python_exe, run_cli, "P1", str(task_dir))
    assert result.returncode == 0
    assert not (task_dir / "P1-requirements.md").exists()
    assert not (task_dir / "P1-review.md").exists()

    dirs = _archived_dirs(task_dir, "P1")
    assert len(dirs) == 1
    archived_dir = dirs[0]
    assert (archived_dir / "P1-requirements.md").is_file()
    assert (archived_dir / "P1-review.md").is_file()
