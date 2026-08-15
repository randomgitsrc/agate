# tests/regression/test_v060_r4_cached.py — 回归测试：裁剪 P7 用 --cached 不是 HEAD~1
# （v060-r4-cached.bats 2 用例迁移，TAG0011 批次 11）
# 触发：fabca40 "feat(hardening): check-pruning.py 补 P7/P8 裁剪条件"
# 教训：pre-commit 时本次变更还没进 HEAD，用 HEAD~1 会看不到。
# T001 v2.0 流 A（BDD-1）改写：coupling_checklist 现由 add_p1_field 写入
#   P1-requirements.md 的 frontmatter 块——check-pruning.py 仍能正确读取。@test 数保持 2 不变。
# 迁移：与批次 6b test_check_pruning.py P2.6a/6b 同形态——git_repo（init commit 后建
#   task_dir，避免被 add -A 卷入）+ copytree 到 repo/task + stage("src_*.py")（git pathspec
#   glob），run_cli(..., cwd=repo)。流语义：GATE PRUNING 写 stderr → 合并流 result.output。

import shutil

import pytest

from conftest import add_p1_field, add_pruning_excuse


def _run_pruning(agate_scripts, python_exe, run_cli, task_arg, cwd=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-pruning.py"),
        task_arg,
        cwd=cwd,
    )


_PHASES_NO_P7 = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"]


@pytest.mark.windows_smoke
def test_r3_1_p7_pruned_six_sources_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")

    td = task_dir(phases=_PHASES_NO_P7)
    add_pruning_excuse(td, "P7", "源文件多", "中等")
    for i in range(1, 7):
        (repo / f"src_{i}.py").write_text(f"file {i}\n", encoding="utf-8")
    shutil.copytree(td, repo / "task")
    git_repo.stage("src_*.py")

    result = _run_pruning(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 1
    assert "裁剪 P7 需源码文件数" in result.output


def test_r3_2_p7_pruned_three_sources_coupling_checklist_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")

    td = task_dir(phases=_PHASES_NO_P7)
    add_p1_field(td, "coupling_checklist", "[api-schema: checked]")
    add_pruning_excuse(td, "P7", "小改动", "低")
    for i in range(1, 4):
        (repo / f"src_{i}.py").write_text(f"file {i}\n", encoding="utf-8")
    shutil.copytree(td, repo / "task")
    git_repo.stage("src_*.py")

    result = _run_pruning(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
