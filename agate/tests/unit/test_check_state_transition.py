# tests/unit/test_check_state_transition.py — 状态转移合法性检查
# （check-state-transition.bats 30 用例迁移，TAG0011 批次 6a）
# 被测：agate/scripts/check-state-transition.py（[STATE_FILE]，默认 .state.yaml；
#   exit 0 = 合法 / exit 1 = 非法）。注意脚本需真实 git 仓库（git show HEAD:file）。
# 依赖 git_repo fixture（git init/commit/stage 等价 git-helper.bash）+ run_cli(..., cwd=repo)
#   （等价 bats `cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/check-state-transition.py' ...`）。
# 流语义：GATE STATE 失败消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import shutil

import pytest


def _write_state(state_path, phase, retries_block=None):
    """写 .state.yaml（bats `cat > ... <<EOF` 等价）。retries_block 为多行 retries 段或 None。"""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    retries = retries_block if retries_block is not None else "retries: {}"
    state_path.write_text(
        f"task_id: T001\nphase: {phase}\nstatus: active\n{retries}\n",
        encoding="utf-8",
    )


def _run_state(agate_scripts, python_exe, run_cli, repo, state_arg):
    """bats `cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/check-state-transition.py' <state>` 等价。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "check-state-transition.py"),
        state_arg,
        cwd=str(repo),
    )


@pytest.mark.windows_smoke
def test_st_1_no_state_yaml_staged_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_2_new_phase_p1_first_exit_0(
    git_repo, agate_scripts, python_exe, run_cli, load_fixture
):
    repo = git_repo.path
    shutil.copyfile(load_fixture("full-task/.state.yaml"), repo / ".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_3_forward_jump_p1_to_p3_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P1-requirements.md").write_text(
        "risk_level: medium\n"
        "phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]\n"
        "- Given test\n",
        encoding="utf-8",
    )
    _write_state(task / ".state.yaml", "P1")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P3")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_4_backward_jump_p3_to_p1_exit_1_paused(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P1")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_5_backward_jump_p4_to_p2_exit_1_paused(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P4")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P2")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1


def test_st_6_retries_p2_ge3_non_paused_exit_1_paused(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P2")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P3",
        "retries:\n  P2:\n    - attempt: 1\n    - attempt: 2\n    - attempt: 3",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_7_retries_p2_ge3_paused_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P2")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "PAUSED",
        "retries:\n  P2:\n    - attempt: 1\n    - attempt: 2\n    - attempt: 3",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_8_terminal_phase_paused_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P1")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "PAUSED")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_9_retries_p3_ge2_exit_1_paused_p3(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P4",
        "retries:\n  P3:\n    - attempt: 1\n    - attempt: 2",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output
    assert "P3" in result.output


def test_st_10_retries_p5_ge2_exit_1_p5(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P5")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P6",
        "retries:\n  P5:\n    - attempt: 1\n    - attempt: 2",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "P5" in result.output


def test_st_11_multi_phase_retries_below_threshold_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P2-design.md").write_text("# P2 design\n", encoding="utf-8")
    _write_state(repo / ".state.yaml", "P2")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P3",
        "retries:\n  P2:\n    - attempt: 1\n    - attempt: 2\n  P3:\n    - attempt: 1",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_12_retries_p2_3_and_p3_2_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P2")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P4",
        "retries:\n  P2:\n    - attempt: 1\n    - attempt: 2\n    - attempt: 3\n"
        "  P3:\n    - attempt: 1\n    - attempt: 2",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1


def test_st_13_backward_jump_p3_to_p1_exit_1_paused_recovery(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P1")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_14_backward_jump_p4_to_p2_exit_1_paused_recovery(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P4")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P2")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1


def test_st_15_paused_to_p4_recovery_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "PAUSED")
    git_repo.commit("paused")

    _write_state(repo / ".state.yaml", "P4")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_st_16_commit_gate_p1_output_committed_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P1-requirements.md").write_text(
        "risk_level: medium\nphases: [P0, P1, P2, P3]\n- Given test\n",
        encoding="utf-8",
    )
    _write_state(task / ".state.yaml", "P1")
    git_repo.commit("T001 P1")

    _write_state(task / ".state.yaml", "P2")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_17_commit_gate_output_same_commit_mode_b_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P1")
    git_repo.commit("T001 phase P1")

    (task / "P1-requirements.md").write_text("# P1 output\n", encoding="utf-8")
    _write_state(task / ".state.yaml", "P2")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_18_commit_gate_output_missing_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P1")
    git_repo.commit("T001 phase P1")

    _write_state(task / ".state.yaml", "P2")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_19_commit_gate_paused_recovery_skipped_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P2-design.md").write_text("# P2 design\n", encoding="utf-8")
    _write_state(task / ".state.yaml", "PAUSED")
    git_repo.commit("Paused")

    _write_state(task / ".state.yaml", "P3")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_20_commit_gate_backward_skipped_no_commit_message(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P1-requirements.md").write_text("# P1\n", encoding="utf-8")
    _write_state(task / ".state.yaml", "P3")
    git_repo.commit("T001 P3")

    _write_state(task / ".state.yaml", "P1")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert "产出必须已 commit" not in result.output
    assert "尚未 commit" not in result.output


def test_st_archive_1_p6_to_p5_unarchived_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P6")
    (task / "P6-acceptance.md").write_text("old p6\n", encoding="utf-8")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P5")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 1
    assert "P6 的自撰产出" in result.output
    assert "agate-archive-stale-outputs.py" in result.output


def test_st_archive_2_p6_to_p5_archived_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P6")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P5")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_archive_3_p5_to_p4_not_self_authored_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P5")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P4")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_archive_4_forward_p4_to_p5_no_archive_check_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P4")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P5")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_archive_5_p1_to_p0_start_phase_exit_0(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P1")
    (task / "P1-requirements.md").write_text("req\n", encoding="utf-8")
    (task / "P1-review.md").write_text("review\n", encoding="utf-8")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P0")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 0


def test_st_archive_6_p2_to_p1_review_still_in_place_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P2")
    (task / "P2-review.md").write_text("review\n", encoding="utf-8")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P1")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 1
    assert "P2-review.md" in result.output


def test_st_ws_1_new_layout_agate_workspace_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P1")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_ws_2_custom_task_path_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "custom-tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P1")
    git_repo.stage("custom-tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "custom-tasks/T001/.state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_ws_3_root_level_state_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P1")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output


def test_st_ws_4_old_layout_docs_tasks_exit_1(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    task = repo / "docs" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_state(task / ".state.yaml", "P3")
    git_repo.commit("init")

    _write_state(task / ".state.yaml", "P1")
    git_repo.stage("docs/tasks/T001/.state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, "docs/tasks/T001/.state.yaml")
    assert result.returncode == 1
    assert "PAUSED" in result.output
