# tests/unit/test_agate_retreat_to.py — agate-retreat-to.py 自动化多步回退校验
# （agate-retreat-to.bats 5 用例迁移，TAG0011 批次 4）
# 被测：agate/scripts/agate-retreat-to.py（TASK_DIR TARGET_PHASE REASON，多步单向回退）
# 依赖 git_repo fixture（_init_task_repo 等价 bats setup 的目录+git commit）
# run_cli(..., cwd=repo) 等价 bats `cd '$repo'`；git 断言经 git_repo.git(...)（git -C repo 等价）
# 流语义：错误/超限消息写 stderr，成功输出写 stdout——断言一律基于合并流 .output（P2 BLOCKER-1）

import pytest


def _init_task_repo(git_repo, phase, retries_yaml="retries: {}"):
    """bats _init_task_repo 等价：建 docs/tasks/T001 + .state.yaml + 产出 + commit init。"""
    repo = git_repo.path
    task = repo / "docs" / "tasks" / "T001"
    (task / "P6-evidence" / "screenshots").mkdir(parents=True)
    (task / ".state.yaml").write_text(
        f"task_id: T001\nphase: {phase}\nstatus: active\n{retries_yaml}\n",
        encoding="utf-8",
    )
    (task / "P6-acceptance.md").write_text("old p6\n", encoding="utf-8")
    (task / "P6-evidence" / "screenshots" / "x.png").touch()
    git_repo.commit("init")
    return repo


def _run_retreat(agate_scripts, python_exe, run_cli, repo, *args):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-retreat-to.py"),
        *args,
        cwd=str(repo),
    )


@pytest.mark.windows_smoke
def test_retreat_1_p6_to_p4_two_commits(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = _init_task_repo(git_repo, "P6")

    result = _run_retreat(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001", "P4", "诊断原因测试")
    assert result.returncode == 0
    assert "共 2 步" in result.output

    log = git_repo.git("log", "--oneline").stdout
    assert "retreat: P6 -> P5" in log
    assert "retreat: P5 -> P4" in log

    state = (repo / "docs" / "tasks" / "T001" / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P4" in state
    assert "P5:" in state
    assert "P4:" in state


def test_retreat_2_target_not_below_current_rejected(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = _init_task_repo(git_repo, "P4")

    result = _run_retreat(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001", "P6", "诊断")
    assert result.returncode == 1
    assert "不是回退" in result.output


def test_retreat_3_retry_budget_exceeded_precheck_noop(
    git_repo, agate_scripts, python_exe, run_cli
):
    retries_yaml = "retries:\n  P5:\n  - attempt: 1\n  - attempt: 2"
    repo = _init_task_repo(git_repo, "P6", retries_yaml)

    result = _run_retreat(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001", "P4", "诊断")
    assert result.returncode == 1
    assert "超限" in result.output

    log = git_repo.git("log", "--oneline").stdout
    assert len([line for line in log.splitlines() if line.strip()]) == 1
    state = (repo / "docs" / "tasks" / "T001" / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P6" in state


def test_retreat_4_staged_files_outside_task_dir_rejected(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = _init_task_repo(git_repo, "P6")
    (repo / "other-project").mkdir()
    (repo / "other-project" / "wip.txt").write_text("unrelated\n", encoding="utf-8")
    git_repo.git("add", "other-project/wip.txt")

    result = _run_retreat(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001", "P4", "诊断")
    assert result.returncode == 1
    assert "TASK_DIR 之外的文件" in result.output
    assert "wip.txt" in result.output

    cached = git_repo.git("diff", "--cached", "--name-only").stdout
    assert "wip.txt" in cached


def test_retreat_5_invalid_target_phase_rejected(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = _init_task_repo(git_repo, "P6")

    result = _run_retreat(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001", "PAUSED", "诊断")
    assert result.returncode == 1
