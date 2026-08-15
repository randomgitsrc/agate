# tests/unit/test_check_gate.py — check-gate.py 阶段 gate 总闸
# （check-gate.bats 124 用例迁移，TAG0011 批次 8a：G0 / G1 / G3 / G4 / G_OTHER，11 用例；
#   批次 8b：G2 系列 + G_BDD1.1/9.1/10.1 + G_CMD_EXEC.1/2，29 用例；
#   批次 8c：G5 / G5.1 / G5_CMD.1-5，7 用例）
# 被测：agate/scripts/check-gate.py（PHASE TASK_DIR [OLD_PHASE]；exit 0 = 通过 / exit 1 = 未通过 /
#   exit 2 = 主 Agent 自判）。
# G0/G1/G3/G_OTHER 用 task_dir factory（create_task_dir 等价）；G4 系列需要 git_repo
#   （gate_p4 检查 git diff --cached 暂存区）+ shutil.copytree 把 task 目录复制进 repo，
#   run_cli(..., cwd=repo) 等价 bats `cd '$repo' && ...`。
# 8b（gate_p2 分支）：task_dir + add_p2_candidate_count / add_p2_review / add_p1_field
#   （conftest 纯函数，frontmatter 块写入，T001 v2.0 流 A）；P2-design.md 用 heredoc 原文覆写。
# 流语义：GATE 前缀消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import shutil

import pytest

from conftest import add_p1_field, add_p2_candidate_count, add_p2_review


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


# ========== 8b: gate_p2 分支（G2 系列 + G_BDD1.1/9.1/10.1 + G_CMD_EXEC） ==========

_P2_TWO_CAND_BODY = (
    "# P2 design\n"
    "### 候选方案 A：方案一\n"
    "### 候选方案 B：方案二\n"
    "## 权衡\n"
    "A 更简单，B 更稳健。\n"
    "packages: [pkg-a]\n"
    "domains: [backend]\n"
    "ui_affected: false\n"
    "gate_commands: {}\n"
)


def _write_p2_design(td, body):
    (td / "P2-design.md").write_text(body, encoding="utf-8")


def test_g2_1_zero_candidates_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, "# P2 design\n## 设计\n无候选方案。\n")
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "需至少 2 个候选方案" in result.output


def test_g2_2_one_candidate_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, "# P2 design\n### 候选方案 A：方案一\n")
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1


def test_g2_3_two_candidates_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_4_h5_candidates_not_recognized_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td, "# P2 design\n##### 候选方案 A：方案一\n##### 候选方案 B：方案二\n"
    )
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1


def test_g2_25_h4_candidates_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "#### 候选方案 A：方案一\n"
        "#### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_26_fullwidth_colon_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 方案：方案一\n"
        "### 方案：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_27_missing_candidate_count_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "candidate_count" in result.output


def test_g2_5_missing_p2_file_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(
        phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"]
    )  # P2 不在
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "P2-design.md" in result.output


def test_g2_8_two_candidates_no_tradeoff_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "权衡" in result.output


def test_g2_9_two_candidates_with_tradeoff_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "方案 A 更简单但性能差，方案 B 复杂但性能好。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_9a_design_trivial_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    add_p1_field(td, "design_trivial", "true")
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "## 权衡\n"
        "简单修改，无需多方案。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 1)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_9b_follows_existing_pattern_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "follows_existing_pattern", "[src/foo.py]")
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：照搬已有模式\n"
        "## 权衡\n"
        "照搬 src/foo.py 模式。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 1)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_10_review_rejected_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: test\nstatus: rejected\n---\n## 裁决\n未通过。\n",
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "非 approved" in result.output


def test_g2_10a_rejected_with_approved_literal_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: test\nstatus: rejected\n---\n## 裁决说明\n\n"
        "gate 规则要求 status: approved 才放行，本次评审未通过。\n",
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "非 approved" in result.output


def test_g2_11_review_approved_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: test\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_bdd1_1_four_fields_via_frontmatter_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "---\n"
        "phase: P2\n"
        "task_id: T001\n"
        "agent: architect\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "---\n"
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_13_missing_review_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "P2-review.md" in result.output


def test_cmd_exec_1_missing_cmd_warning_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands:\n"
        '  P3: "definitely-nonexistent-cmd --flag"\n'
        '  P5: "echo hi"\n',
    )
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: test\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2
    assert "definitely-nonexistent-cmd" in result.output


def test_cmd_exec_2_all_cmds_executable_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands:\n"
        '  P3: "true"\n'
        '  P5: "echo hi"\n',
    )
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: test\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2
    assert "不存在" not in result.output


def test_g2_14_candidate_with_space_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 方案 A\n"
        "### 方案 B\n"
        "## 权衡\n"
        "A 简单，B 稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_bdd10_1_frontmatter_count_wins_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n"
        "candidate_count: 1\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_17_selection_title_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "### 选择：方案 A\n"
        "**理由**：A 更简单。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_18_review_agent_subagent_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: subagent\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_19_review_agent_main_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nagent: main\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "agent=main" in result.output


def test_g2_20_review_missing_agent_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    (td / "P2-review.md").write_text(
        "---\nstatus: approved\n---\n通过。\n", encoding="utf-8"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2
    assert "agent" in result.output


def test_g2_7_h2_candidates_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "## 候选方案 A\n"
        "## 候选方案 B\n"
        "## 权衡\n"
        "A 简单，B 稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_21_multiple_word_candidates_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 方案 Alpha\n"
        "### 方案 Beta\n"
        "## 权衡\n"
        "Alpha 简单，Beta 稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_bdd9_1_legacy_body_fields_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


def test_g2_24_numeric_candidates_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "# P2 design\n"
        "### 方案 1\n"
        "### 方案 2\n"
        "## 权衡\n"
        "方案 1 简单，方案 2 稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 2


# ========== 8c: gate_p5 分支（G5 / G5.1 / G5_CMD.1-5） ==========

def test_g5_p5_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_g5_1_multi_cmd_warning(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "---\n"
        "phase: P2\n"
        "task_id: T001\n"
        "agent: architect\n"
        "---\n"
        "\n"
        "gate_commands:\n"
        '  P5: "pytest -q --tb=no"\n'
        '  P5_e2e: "playwright test --reporter=line tests/e2e/"\n',
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert (
        "gate_commands.P5" in result.output
        or "子集" in result.output
        or "全量" in result.output
    )


def test_g5_cmd_1_p5_plus_e2e_counted(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    bullets = "".join(f"- 要点 {i}\n" for i in range(1, 21))
    _write_p2_design(
        td,
        "---\n"
        "phase: P2\n"
        "---\n"
        "\n"
        "候选方案：\n"
        f"{bullets}"
        "\n"
        "gate_commands:\n"
        '  P5: "pytest -q"\n'
        '  P5_e2e: "playwright test"\n',
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "1 个主命令 + 1 个辅助命令" in result.output
    assert "共 2 条" in result.output
    assert "22 个" not in result.output


def test_g5_cmd_2_single_p5_no_warning(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    bullets = "".join(f"- 要点 {i}\n" for i in range(1, 11))
    _write_p2_design(
        td,
        "---\n"
        "phase: P2\n"
        "---\n"
        "\n"
        f"{bullets}"
        "\n"
        "gate_commands:\n"
        '  P5: "pytest -q"\n',
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "gate_commands.P5 命令" not in result.output


def test_g5_cmd_3_no_gate_commands_no_warning(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p2_design(
        td,
        "---\n" "phase: P2\n" "---\n" "候选方案：无 gate_commands 声明\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "gate_commands.P5 命令" not in result.output


def test_g5_cmd_4_p6_not_counted_as_p5(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(
        td,
        "---\n"
        "phase: P2\n"
        "---\n"
        "gate_commands:\n"
        '  P5: "pytest -q"\n'
        '  P6: "pytest tests/acceptance"\n',
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "gate_commands.P5 命令" not in result.output


def test_g5_cmd_5_no_trailing_newline(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text(
        'gate_commands:\n  P5: "pytest"\n  P5_e2e: "playwright"',
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "1 个主命令 + 1 个辅助命令" in result.output
    assert "共 2 条" in result.output
