# tests/unit/test_check_gate.py — check-gate.py 阶段 gate 总闸
# （check-gate.bats 124 用例迁移，TAG0011 批次 8a：G0 / G1 / G3 / G4 / G_OTHER，11 用例）
# 被测：agate/scripts/check-gate.py（PHASE TASK_DIR [OLD_PHASE]；exit 0 = 通过 / exit 1 = 未通过 /
#   exit 2 = 主 Agent 自判）。
# G0/G1/G3/G_OTHER 用 task_dir factory（create_task_dir 等价）；G4 系列需要 git_repo
#   （gate_p4 检查 git diff --cached 暂存区）+ shutil.copytree 把 task 目录复制进 repo，
#   run_cli(..., cwd=repo) 等价 bats `cd '$repo' && ...`。
# 流语义：GATE 前缀消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import shutil

import pytest


def _run_gate(agate_scripts, python_exe, run_cli, phase, task_arg, cwd=None):
    """bats `'$PYTHON' '$AGATE_SCRIPTS/check-gate.py' PHASE TASK_DIR` 等价。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "check-gate.py"),
        phase,
        task_arg,
        cwd=cwd,
    )


def _init_repo_with_task(git_repo, td):
    """bats `git_init + echo init > README.md + git_commit + cp -r task` 等价。"""
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    shutil.copytree(td, repo / "task")


def _write_p4_review(repo, status, agent):
    """写 repo/task/P4-review.md（bats heredoc 等价）。"""
    (repo / "task" / "P4-review.md").write_text(
        f"---\nstatus: {status}\nagent: {agent}\n---\nreviewed.\n",
        encoding="utf-8",
    )


@pytest.mark.windows_smoke
def test_g0_p0_no_unknown_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P0", str(td))
    assert result.returncode == 2
    assert "未知" not in result.output


def test_g1_p1_missing_review_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "P1-review.md" in result.output


def test_g3_p3_checks_test_cases_md(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P3", str(td))
    assert result.returncode == 1
    assert "P3-test-cases.md 不存在" in result.output

    (td / "P3-test-cases.md").write_text("## P3 test cases\n", encoding="utf-8")
    result = _run_gate(agate_scripts, python_exe, run_cli, "P3", str(td))
    assert result.returncode == 2
    assert "check-tdd-red.sh" in result.output


def test_g4_1_staged_only_md_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    (repo / "task" / "P4-implementation.md").write_text("doc\n", encoding="utf-8")
    git_repo.stage("task/P4-implementation.md")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 1


def test_g4_2_staged_py_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    _write_p4_review(repo, "approved", "reviewer-subagent")
    (repo / "src.py").write_text("def hello(): pass\n", encoding="utf-8")
    git_repo.stage("src.py")
    git_repo.stage("task/P4-review.md")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 0


def test_g4_3_staged_mixed_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    _write_p4_review(repo, "approved", "reviewer-subagent")
    (repo / "task" / "P4-implementation.md").write_text("doc\n", encoding="utf-8")
    (repo / "src.py").write_text("code\n", encoding="utf-8")
    (repo / "config.yaml").write_text("yaml: 1\n", encoding="utf-8")
    git_repo.stage(".")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 0


def test_g4_4_py_not_excluded_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    _write_p4_review(repo, "approved", "reviewer-subagent")
    (repo / "src.py").write_text("code\n", encoding="utf-8")
    git_repo.stage("src.py")
    git_repo.stage("task/P4-review.md")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 0


def test_g4_5_missing_review_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    (repo / "src.py").write_text("code\n", encoding="utf-8")
    git_repo.stage("src.py")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 1
    assert "P4-review.md" in result.output


def test_g4_6_review_not_approved_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    _write_p4_review(repo, "rejected", "reviewer-subagent")
    (repo / "src.py").write_text("code\n", encoding="utf-8")
    git_repo.stage("src.py")
    git_repo.stage("task/P4-review.md")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 1
    assert "非 approved" in result.output


def test_g4_7_review_agent_main_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _init_repo_with_task(git_repo, td)
    repo = git_repo.path
    _write_p4_review(repo, "approved", "main")
    (repo / "src.py").write_text("code\n", encoding="utf-8")
    git_repo.stage("src.py")
    git_repo.stage("task/P4-review.md")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P4", "task", cwd=str(repo))
    assert result.returncode == 1
    assert "agent=main" in result.output


def test_other_unknown_phase_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P9", str(td))
    assert result.returncode == 2
    assert "未知阶段" in result.output
