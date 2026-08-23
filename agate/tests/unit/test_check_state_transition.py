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


# ============================================================
# TAG0023 RM-AG0042（BDD-1~4）：门槛失败事件强制记录 retries 对应性校验
# 被测：check-state-transition.py 新增函数（P2-design.md §2.1 候选 A，尚未实现——
#   main() 目前无任何调用点，这正是本批红灯的来源）。
# 校验强度分层（P2-design.md §2.1 D1，P2 重试 #2 定案）：
#   BDD-1/BDD-3 = 高优 WARNING（不阻断）：exit 0 + stderr 含 "WARNING"；
#   BDD-2       = 阻断（结构化数值比较，误报率低）：exit 1；
#   BDD-4       = 回归防呆：三类事件均未命中 + retries 为空/缺失 → exit 0 且无 WARNING。
# ============================================================


def _write_task_state(task_dir, phase, retries_block=None):
    """task 级 .state.yaml（_write_state 的 task_dir 版本，供嵌套目录场景复用）。"""
    _write_state(task_dir / ".state.yaml", phase, retries_block)


def test_bdd_1_review_rejected_retry_file_empty_retries_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-1 分支①：评审角色重试 dispatch-context 文件存在（C8 角色 token 枚举命中，
    P2-design.md D6 最终正则）+ retries[P2] 为空/缺失 → 高优 WARNING，exit 0（不阻断）。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P2")
    git_repo.commit("init")

    (task / "P2-dispatch-context-plan-eng-review-retry1.md").write_text(
        "stub\n", encoding="utf-8"
    )
    _write_task_state(task, "P3", "retries: {}")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" in result.output


def test_bdd_1_review_rejected_retry_file_with_retries_no_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-1 分支②：同一评审重试文件存在，但 retries[P2] 已有记录 → 不再输出 WARNING。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P2")
    git_repo.commit("init")

    (task / "P2-dispatch-context-plan-eng-review-retry1.md").write_text(
        "stub\n", encoding="utf-8"
    )
    _write_task_state(task, "P3", "retries:\n  P2:\n    - attempt: 1")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_bdd_1_no_retry_dispatch_context_file_no_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-1 分支③：task_dir 下无评审重试 dispatch-context 文件 → 不触发 WARNING。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P2")
    git_repo.commit("init")

    _write_task_state(task, "P3", "retries: {}")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_bdd_1_negative_anchor_implementer_review_fix_not_matched(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-1 负面回归锚点①（P2-review.md 独立复核确认的真实历史假阳性样本，文件名模式取自
    agate-workspace/archived/tasks/T001-v2.0-structured/
    P4-dispatch-context-implementer-review-fix-retry1.md ——frontmatter role: implementer，
    正文是配额中断重启，与评审驳回无关；token "implementer-review-fix" 不精确等于枚举中任一
    评审角色 token，不得误命中 WARNING（P2-design.md D6 正则收紧后的回归防呆）。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P3")
    git_repo.commit("init")

    (task / "P4-dispatch-context-implementer-review-fix-retry1.md").write_text(
        "stub\n", encoding="utf-8"
    )
    _write_task_state(task, "P4", "retries: {}")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_bdd_1_negative_anchor_consistency_reviewer_not_matched(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-1 负面回归锚点②（P2-review.md 独立复核确认的真实历史假阳性样本，文件名模式取自
    agate-workspace/tasks/TAG0016-protocol-hygiene/
    P7-dispatch-context-consistency-reviewer-retry1.md ——frontmatter role: architect，是
    P7 阶段"architect 兼任一致性检查"的历史命名别名，非 C8 表内评审角色，不得误命中 WARNING。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P6")
    git_repo.commit("init")

    (task / "P7-dispatch-context-consistency-reviewer-retry1.md").write_text(
        "stub\n", encoding="utf-8"
    )
    _write_task_state(task, "P7", "retries: {}")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_bdd_2_retreat_p5_to_p4_no_retries_growth_exit_1(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-2：P5→P4 单步回退（diff==1，现有检查 1 只判 diff>=2，不覆盖单步）+ retries[P4]
    暂存版本长度未大于 HEAD 版本长度（本次 commit 未新增记录）→ 阻断 exit 1（P2 D1 阻断级）。"""
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P5", "retries:\n  P4:\n    - attempt: 1")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P4", "retries:\n  P4:\n    - attempt: 1")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 1


def test_bdd_2_retreat_p5_to_p4_retries_growth_exit_0(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-2 回归防呆：同一回退但本次 commit 确有新增 retries[P4] 条目（长度增长）→ 不拦截。"""
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P5", "retries:\n  P4:\n    - attempt: 1")
    git_repo.commit("init")

    _write_state(
        repo / ".state.yaml",
        "P4",
        "retries:\n  P4:\n    - attempt: 1\n    - attempt: 2",
    )
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0


def test_bdd_3_empty_return_redispatch_keyword_empty_retries_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-3：P{n}-progress.md 含"空返回"/"重派"关键词信号 + retries[Pn] 为空/缺失 →
    高优 WARNING（不阻断，自由文本关键词信号主观性高，P2 D1）。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P2")
    git_repo.commit("init")

    (task / "P2-progress.md").write_text("子代理空返回，已重派\n", encoding="utf-8")
    _write_task_state(task, "P3", "retries: {}")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" in result.output


def test_bdd_3_empty_return_redispatch_keyword_with_retries_no_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-3 回归防呆：同上关键词命中，但 retries[P2] 已有记录 → 不再输出 WARNING。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    _write_task_state(task, "P2")
    git_repo.commit("init")

    (task / "P2-progress.md").write_text("子代理空返回，已重派\n", encoding="utf-8")
    _write_task_state(task, "P3", "retries:\n  P2:\n    - attempt: 1")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _run_state(
        agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T001/.state.yaml"
    )
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_bdd_4_no_event_empty_retries_exit_0_no_warning(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-4 回归防呆：无评审 rejected / 无回退 / 无关键词命中，retries 为空或缺失 →
    exit 0 且无 WARNING（空 retries 本身不是错误，只有"事件存在而 retries 为空"才是缺口）。"""
    repo = git_repo.path
    _write_state(repo / ".state.yaml", "P1")
    git_repo.commit("init")

    _write_state(repo / ".state.yaml", "P2", "retries: {}")
    git_repo.stage(".state.yaml")

    result = _run_state(agate_scripts, python_exe, run_cli, repo, ".state.yaml")
    assert result.returncode == 0
    assert "WARNING" not in result.output
