# tests/unit/test_check_gate.py — check-gate.py 阶段 gate 总闸
# （check-gate.bats 124 用例迁移，TAG0011 批次 8a：G0 / G1 / G3 / G4 / G_OTHER，11 用例；
#   批次 8b：G2 系列 + G_BDD1.1/9.1/10.1 + G_CMD_EXEC.1/2，29 用例；
#   批次 8c：G5 / G5.1 / G5_CMD.1-5，7 用例；
#   批次 8d：G6 系列 + G_BDD16.1 + test_bdd_1..8（TAG0002 refactor 口径），20 用例；
#   批次 8e：G7.1-9 + G_DG_ANCHOR.1/2 + bdd-11（TAG0004 M4 全角冒号），12 用例；
#   批次 8f：G8.1-10（gate_p8 分支），10 用例；
#   批次 8g：G_RETREAT.1-6 + G_NC_BINARY.1/2/3/5/6 + G_SUGGEST.1-4，15 用例；
#   批次 8h：D-drift-1/2/4/4b/5/6 + G-drift-1/2/3 + TAG0005 BDD-1/2/9/12/13/14/15，16 用例；
#   批次 8 补遗：PG.P2REVIEW / bdd-14 / bdd-28 / bdd-29，4 用例）
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

import re
import shutil

import pytest

from conftest import add_p1_field, add_p2_candidate_count, add_p2_review


def _run_gate(agate_scripts, python_exe, run_cli, phase, task_arg, cwd=None, env=None, old_phase=None):
    """bats `'$PYTHON' '$AGATE_SCRIPTS/check-gate.py' PHASE TASK_DIR [OLD_PHASE]` 等价。

    old_phase 对应 bats 可选第 3 参数（G_RETREAT 系列，回退抵达检测）。
    """
    cmd = [
        python_exe,
        str(agate_scripts / "check-gate.py"),
        phase,
        task_arg,
    ]
    if old_phase is not None:
        cmd.append(old_phase)
    return run_cli(*cmd, cwd=cwd, env=env)


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


# ========== 8d: gate_p6 分支（G6 系列 + G_BDD16.1）+ TAG0002 refactor 口径（test_bdd_1..8） ==========
# P6-acceptance.md 用 write_text 覆写（等价 bats heredoc）；P6-evidence/ 目录存在性
# 由 gate_p6 判定（G6.4 断言其缺失）。refactor 系列用 add_p1_field 写 P1 frontmatter
# change_type（NO_FALLBACK_STRING_FIELDS，仅 frontmatter 生效）。


def _write_p6_acceptance(td, body):
    (td / "P6-acceptance.md").write_text(body, encoding="utf-8")


def _add_p6_evidence(td, filename, content="log\n"):
    (td / "P6-evidence").mkdir(parents=True, exist_ok=True)
    (td / "P6-evidence" / filename).write_text(content, encoding="utf-8")


_P6_REGRESSION_BODY = (
    "---\n"
    "phase: P6\n"
    "task_id: TAG0002\n"
    "agent: verifier\n"
    "pass: 1\n"
    "fail: 0\n"
    "ui_affected: false\n"
    "regression_pass: true\n"
    "---\n"
    "- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)\n"
)


def test_g6_1_fail_line_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- FAIL BDD-2\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "FAIL=" in result.output


def test_g6_3_all_pass_no_bdd_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6_acceptance(td, "无 BDD 条目\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "TOTAL=0" in result.output


def test_g6_4_no_evidence_dir_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- PASS BDD-2\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "P6-evidence" in result.output


def test_g6_5_evidence_nonempty_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- PASS BDD-2\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_g6_10_need_confirm_not_blocking_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- [NEED_CONFIRM] some text\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_g6_11_no_need_confirm_no_warning_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1 (result.log)\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2
    assert "NEED_CONFIRM" not in result.output


def test_g6_7_lowercase_fail_counted_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- fail: BDD-2 broken\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "FAIL=1" in result.output


def test_bdd16_1_frontmatter_summary_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6_acceptance(
        td,
        "---\n"
        "phase: P6\n"
        "task_id: T001\n"
        "agent: verifier\n"
        "pass: 1\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "---\n"
        "逐条结果见 P6-evidence/ 详细记录（本文件正文不复述逐条 PASS/FAIL 行）。\n",
    )
    _add_p6_evidence(td, "result.json")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_g6_9_failure_not_counted_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- failure mode detected\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2
    assert "FAIL=0" in result.output


def test_bdd_1_p1_gate_accepts_refactor_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    (td / "P1-review.md").write_text(
        "---\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS\n",
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2
    assert "change_type" not in result.output


def test_bdd_2_p6_default_no_change_type_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6_acceptance(td, "- PASS BDD-1\n- PASS BDD-2\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_bdd_2b_p6_body_mentions_change_type_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write(
            "\nchange_type: refactor 是可选字段，缺省为功能任务（本文档仅作说明，本任务不采用 refactor 口径）\n"
        )
    _write_p6_acceptance(td, "- PASS BDD-1\n- PASS BDD-2\n")
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_bdd_3_p6_refactor_with_regression_evidence_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    _write_p6_acceptance(td, _P6_REGRESSION_BODY)
    _add_p6_evidence(td, "regression.log", "bats ... 0 failures\nEXIT_CODE: 0\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_bdd_4_p6_refactor_missing_regression_log_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    _write_p6_acceptance(td, _P6_REGRESSION_BODY)
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "regression.log" in result.output


def test_bdd_4b_p6_refactor_missing_regression_pass_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    _write_p6_acceptance(
        td,
        "---\n"
        "phase: P6\n"
        "task_id: TAG0002\n"
        "agent: verifier\n"
        "pass: 1\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "---\n"
        "- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)\n",
    )
    _add_p6_evidence(td, "regression.log", "bats ... 0 failures\nEXIT_CODE: 0\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1
    assert "regression_pass" in result.output


def test_bdd_6_p6_no_behavior_change_not_waived_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write("\nno_behavior_change: 预期无行为变更\n")
    _write_p6_acceptance(td, _P6_REGRESSION_BODY)
    _add_p6_evidence(td, "result.log")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 1


def test_bdd_6b_p6_no_behavior_change_with_evidence_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write("\nno_behavior_change: 预期无行为变更\n")
    _write_p6_acceptance(td, _P6_REGRESSION_BODY)
    _add_p6_evidence(td, "regression.log", "bats ... 0 failures\nEXIT_CODE: 0\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_bdd_7_refactor_backfill_walk_p1_p3_p6(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    add_p1_field(td, "change_type", "refactor")
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write(
            "\n#### BDD-2: 关键路径行为不变\n"
            "- Given 重构后的协议状态\n"
            "- When 执行关键路径\n"
            "- Then 行为与重构前一致\n"
        )
    (td / "P1-review.md").write_text(
        "---\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS\n"
        "- BDD-2: PASS\n",
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2

    (td / "P3-test-cases.md").write_text(
        "## P3 test cases（回归测试口径，不新增功能行为断言）\n", encoding="utf-8"
    )
    result = _run_gate(agate_scripts, python_exe, run_cli, "P3", str(td))
    assert result.returncode == 2

    _write_p6_acceptance(
        td,
        "---\n"
        "phase: P6\n"
        "task_id: TAG0002\n"
        "agent: verifier\n"
        "pass: 2\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "regression_pass: true\n"
        "---\n"
        "- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败）(P6-evidence/regression.log)\n"
        "- PASS BDD-2: 关键路径行为不变（重构前后关键路径结果一致）(P6-evidence/regression.log)\n",
    )
    _add_p6_evidence(td, "regression.log", "bats ... 0 failures\nEXIT_CODE: 0\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P6", str(td))
    assert result.returncode == 2


def test_bdd_5_p6_card_docs_forbid_fake_bdd(agate_root):
    content = (agate_root / "phase-cards" / "P6-acceptance.md").read_text(encoding="utf-8")
    assert re.search(r"禁止.*伪造", content)


def test_bdd_8_p3_card_docs_regression_test_port(agate_root):
    content = (agate_root / "phase-cards" / "P3-tdd.md").read_text(encoding="utf-8")
    assert "回归测试口径" in content


# ========== 8e: gate_p7 分支（G7.1-9 + G_DG_ANCHOR.1/2 + bdd-11，12 用例） ==========
# P7-consistency.md 用 write_text 覆写（等价 bats heredoc）。gate_p7 输出
# （GATE P7: ... / GATE P7 WARNING / WARNING P7）一律 sys.stderr.write → 断言合并流
# result.output（P2 §3.2 流语义规则，BLOCKER-1）。
# bdd-11 需 env LC_ALL=C LANG=（M4 全角冒号总结行），经 _run_gate env= 透传 run_cli。


def _write_p7(td, body):
    (td / "P7-consistency.md").write_text(body, encoding="utf-8")


def test_g7_1_blocker_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [BLOCKER] arch flaw\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "BLOCKER=" in result.output


def test_g7_2_deviation_critical_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [DEVIATION-CRITICAL] ui break\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "DEVIATION-CRITICAL=" in result.output


def test_g7_3_design_gap_unpaired_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [DESIGN_GAP: P2 未指定错误处理]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "DESIGN_GAP" in result.output
    assert "未配对" in result.output


def test_g7_4_design_gap_paired_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [DESIGN_GAP: P2 未指定错误处理]\n- [DESIGN_GAP_REVIEWED: 已确认]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0


def test_g7_5_two_gaps_one_reviewed_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [DESIGN_GAP: A]\n- [DESIGN_GAP: B]\n- [DESIGN_GAP_REVIEWED: A 已确认]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1


def test_g7_6_empty_file_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0


def test_g7_7_p4_gap_not_copied_to_p7_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "P4-implementation.md").write_text(
        "---\nagent: test\n---\n- [DESIGN_GAP: P2 未指定错误处理]\n",
        encoding="utf-8",
    )
    _write_p7(td, "---\nagent: test\n---\n一致性检查完成。\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "P4" in result.output
    assert "DESIGN_GAP" in result.output
    assert "P7" in result.output


def test_g7_8_blocker_zero_declared_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p7(td, "- [BLOCKER]: 0 条\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0


def test_g7_9_blocker_zero_plus_real_blocker_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p7(td, "- [BLOCKER]: 0 条\n- [BLOCKER] arch flaw\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "BLOCKER=" in result.output


def test_dg_anchor_1_inline_gap_not_counted_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p7(td, "# P7 一致性检查\n检查了 [DESIGN_GAP: xxx] 的引用\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 0


def test_dg_anchor_2_bol_gap_counted_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p7(td, "# P7 一致性检查\n- [DESIGN_GAP: xxx] 未配对\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P7", str(td))
    assert result.returncode == 1
    assert "DESIGN_GAP" in result.output


def test_bdd_11_fullwidth_colon_blocker_summary_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p7(td, "- [BLOCKER]：3 条\n")

    result = _run_gate(
        agate_scripts,
        python_exe,
        run_cli,
        "P7",
        str(td),
        env={"LC_ALL": "C", "LANG": ""},
    )
    assert result.returncode == 0


# ========== 8f: gate_p8 分支（G8.1-10，10 用例） ==========
# P8 检查在 git repo 内进行：_init_repo_with_task 复制 task 目录后，写
# version/CHANGELOG 文件并 stage（bats `git -C "$repo" add ...` 等价），
# run_cli(..., cwd=repo) 等价 bats `cd '$repo' && ...`。P8 输出（GATE P8: /
# GATE P8 WARNING:）一律 sys.stderr.write → 断言合并流 result.output
# （P2 §3.2 流语义规则，BLOCKER-1）。G8.5 无 P8 文件分支不需要 git repo
# （bump_type 缺失提前 return 1，gate_p8 不触达 git 检查）。
# G8.6 用 env CHANGELOG_FILE=HISTORY.md 覆盖默认 CHANGELOG.md（bats
# `CHANGELOG_FILE="HISTORY.md" run bash -c ...` 等价）。


def _write_p8_release(td, body):
    (td / "P8-release.md").write_text(body, encoding="utf-8")


def _init_p8_repo(git_repo, td, files=None, tag=None):
    """bats G8 系列 git 前置等价：init + README commit + cp task + 写/暂存文件 + 可选 tag。"""
    repo = git_repo.path
    _init_repo_with_task(git_repo, td)
    for name, content in (files or {}).items():
        (repo / name).write_text(content, encoding="utf-8")
        git_repo.stage(name)
    if tag:
        git_repo.git("tag", tag)
    return repo


_P8_COMPLIANT = "bump_type: minor\ndebt_check: none\n"
_P8_UNRELEASED = "## [Unreleased]\n"
_P8_CHANGELOG_TAGGED = "## [Unreleased]\n\n## [0.2.0] - 2026-07-20\n"


def test_g8_1_missing_bump_type_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, "无 bump_type\n")
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "CHANGELOG.md": _P8_UNRELEASED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 1
    assert "bump_type" in result.output


def test_g8_2_no_version_change_warning_exit_2(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"some.md": "doc\n", "CHANGELOG.md": _P8_UNRELEASED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2
    assert "WARNING" in result.output
    assert "version" in result.output


def test_g8_3_version_changed_no_changelog_exit_2(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo, td, files={"package.json": "v0.1.0\n"}
    )  # CHANGELOG 没改 → WARNING

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2
    assert "CHANGELOG" in result.output


def test_g8_4_full_compliance_exit_2(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "CHANGELOG.md": _P8_UNRELEASED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2


def test_g8_5_missing_p8_file_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])  # P8 不在

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", str(td))
    assert result.returncode == 1


def test_g8_6_changelog_file_env_override(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "HISTORY.md": _P8_UNRELEASED},
    )

    result = _run_gate(
        agate_scripts,
        python_exe,
        run_cli,
        "P8",
        "task",
        cwd=str(repo),
        env={"CHANGELOG_FILE": "HISTORY.md"},
    )
    assert result.returncode == 2


def test_g8_7_tag_missing_warning_exit_2(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "CHANGELOG.md": _P8_CHANGELOG_TAGGED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2
    assert "tag v0.2.0 不存在" in result.output


def test_g8_8_tag_exists_no_warning(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.2.0\n", "CHANGELOG.md": _P8_CHANGELOG_TAGGED},
        tag="v0.2.0",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2
    assert "tag v0.2.0 不存在" not in result.output


def test_g8_9_missing_debt_check_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, "bump_type: minor\n")
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "CHANGELOG.md": _P8_UNRELEASED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 1
    assert "debt_check" in result.output


def test_g8_10_debt_check_any_content_exit_2(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p8_release(td, _P8_COMPLIANT)
    repo = _init_p8_repo(
        git_repo,
        td,
        files={"package.json": "v0.1.0\n", "CHANGELOG.md": _P8_UNRELEASED},
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P8", "task", cwd=str(repo))
    assert result.returncode == 2
    assert "debt_check" not in result.output


# ========== 8g: G_RETREAT / G_NC_BINARY / G_SUGGEST（15 用例） ==========
# 子批 8g 覆盖 check-gate.bats 的 G_RETREAT.1-6（回退抵达检测，main() 可选第 3 参数
# OLD_PHASE）、G_NC_BINARY.1/2/3/5/6（P1 NEED_CONFIRM 三值分级）与 G_SUGGEST.1-4
# （SUGGEST 不阻塞 / typo 兜底）。
# G_RETREAT 系列：bats 用 `mkdir -p "$BATS_TEST_TMPDIR/g_retreatN"` 建空目录（非
# create_task_dir）→ pytest 用 tmp_path 建空目录；G_RETREAT.5 额外 git init + cwd
# （gate_p4 检查暂存区代码文件，空暂存区 exit 1）。
# G_NC_BINARY / G_SUGGEST 系列：bats 用 create_task_dir --no-state-yaml + heredoc
# 覆写 P1-requirements.md / P1-review.md → pytest 用 task_dir(no_state_yaml=True) +
# write_text 覆写。GATE P1 输出一律 sys.stderr.write → 断言合并流 result.output
# （P2 §3.2 流语义规则，BLOCKER-1）。


def test_g_retreat_1_no_old_phase_exit_1(tmp_path, agate_scripts, python_exe, run_cli):
    td = tmp_path / "g_retreat1"
    td.mkdir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1


def test_g_retreat_2_old_phase_p2_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    td = tmp_path / "g_retreat2"
    td.mkdir()

    result = _run_gate(
        agate_scripts, python_exe, run_cli, "P1", str(td), old_phase="P2"
    )
    assert result.returncode == 2
    assert "回退抵达" in result.output


def test_g_retreat_3_old_phase_p6_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    td = tmp_path / "g_retreat3"
    td.mkdir()

    result = _run_gate(
        agate_scripts, python_exe, run_cli, "P4", str(td), old_phase="P6"
    )
    assert result.returncode == 2
    assert "回退抵达" in result.output


def test_g_retreat_4_old_phase_p7_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    td = tmp_path / "g_retreat4"
    td.mkdir()

    result = _run_gate(
        agate_scripts, python_exe, run_cli, "P6", str(td), old_phase="P7"
    )
    assert result.returncode == 2


def test_g_retreat_5_old_phase_p3_forward_exit_1(
    git_repo, agate_scripts, python_exe, run_cli
):
    # 正常推进方向（P4 ← P3，非回退）：暂存区无代码文件 → 仍 exit 1
    repo = git_repo.path

    result = _run_gate(
        agate_scripts,
        python_exe,
        run_cli,
        "P4",
        str(repo),
        cwd=str(repo),
        old_phase="P3",
    )
    assert result.returncode == 1


def test_g_retreat_6_same_phase_not_retreat_exit_1(
    tmp_path, agate_scripts, python_exe, run_cli
):
    td = tmp_path / "g_retreat6"
    td.mkdir()

    result = _run_gate(
        agate_scripts, python_exe, run_cli, "P1", str(td), old_phase="P1"
    )
    assert result.returncode == 1
    assert "回退抵达" not in result.output


_P1_MARKER_HEAD = (
    "---\n"
    "phase: P1\n"
    "task_id: T001-test\n"
    "status: draft\n"
    "agent: analyst\n"
    "---\n"
    "# Requirements\n"
    "- Given x When y Then z\n"
)

_P1_MARKER_REVIEW = (
    "---\n"
    "phase: P1\n"
    "task_id: T001-test\n"
    "status: approved\n"
    "agent: requirements-review\n"
    "---\n"
    "## BDD 评审\n"
    "- BDD-1: PASS\n"
)


def _write_p1_marker_task(td, req_body):
    (td / "P1-requirements.md").write_text(req_body, encoding="utf-8")
    (td / "P1-review.md").write_text(_P1_MARKER_REVIEW, encoding="utf-8")


def test_g_nc_binary_1_no_need_confirm_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(td, _P1_MARKER_HEAD + "- [NO_NEED_CONFIRM]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2


def test_g_nc_binary_2_need_confirm_bol_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td, _P1_MARKER_HEAD + "- [NEED_CONFIRM] z 的边界条件需确认\n"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "NEED_CONFIRM" in result.output


def test_g_nc_binary_3_inline_ref_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(td, _P1_MARKER_HEAD + "无 [NEED_CONFIRM] 需要确认\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "不合规" in result.output


def test_g_nc_binary_5_no_declaration_warning_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(td, _P1_MARKER_HEAD)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2
    assert "WARNING" in result.output


def test_g_nc_binary_6_no_need_confirm_with_desc_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td, _P1_MARKER_HEAD + "- [NO_NEED_CONFIRM] 确认无不可逆操作\n"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2


def test_g_suggest_1_suggest_no_blocker_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td, _P1_MARKER_HEAD + "- [SUGGEST: 推荐方案 A，理由是更安全]\n"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2
    assert "SUGGEST" in result.output
    assert "未解决的 NEED_CONFIRM 项（阻塞）" not in result.output


def test_g_suggest_2_suggest_plus_need_confirm_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td,
        _P1_MARKER_HEAD
        + "- [SUGGEST: 推荐方案 A，理由是更安全]\n"
        + "- [NEED_CONFIRM] 需用户决策的方向\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "阻塞" in result.output


def test_g_suggest_3_old_marker_rename_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(td, _P1_MARKER_HEAD + "- [NEED_CONFIRM倾向: 推荐方案 A]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "重命名为" in result.output


def test_g_suggest_4_missing_colon_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(td, _P1_MARKER_HEAD + "- [SUGGEST xxx]\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "SUGGEST 格式不符" in result.output


# ========== 8h: D-drift / G-drift / TAG0005 BDD（16 用例） ==========
# 子批 8h 覆盖 check-gate.bats 的文档/协议漂移守护用例（bats `grep -q ...` 等价，
# 非 run_cli）：D-drift-1/2/4/4b/5/6（dispatch 模板关键词）+ G-drift-1/2/3
# （dispatch-protocol 关键词 + implementer/verifier 反例）+ TAG0005 BDD-1/2/9/12/13/14/15
# （role-system / check-gate.py / dispatch-protocol 文档锚点 + scripts 扫描）。
# 等价映射：grep -q 'X' FILE → 读文件 text + `assert "X" in text`；`! grep -q` →
# `assert "X" not in text`；`grep -rl ... --include='*.md'` → rglob 收集 + 单文件断言；
# `grep -rnE '>&2;\s*exit 0' scripts/*.sh` → 逐行正则 + 每命中行必须含「跳过」。
# 全走 agate_root fixture（等价 $AGATE_ROOT），所有 read_text 显式 encoding="utf-8"
# （BDD-7）。此批无 create_task_dir / git_repo 依赖，纯文件内容断言。


def _read_text(path):
    return path.read_text(encoding="utf-8")


def test_drift_1_dispatch_prompt_contains_return_self_check(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-prompt.md")
    assert "返回前自检" in content


def test_drift_2_dispatch_prompt_contains_files_modified(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-prompt.md")
    assert "files_modified" in content


def test_drift_4_dispatch_context_xml_guide_sections(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-context.md")
    assert "<dispatch_guide>" in content
    assert "### 目标" in content
    assert "### 约束" in content


def test_drift_4b_dispatch_context_xml_markers(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-context.md")
    assert "<dispatch_guide>" in content
    assert "<objective_info>" in content


def test_drift_5_dispatch_prompt_contains_p3_self_check(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-prompt.md")
    assert "P3 自检" in content


def test_drift_6_dispatch_prompt_contains_fix_round_dispatch(agate_root):
    content = _read_text(agate_root / "assets/templates/dispatch-prompt.md")
    assert "修复轮派发追加" in content


def test_drift_g1_dispatch_protocol_self_check_neq_gate(agate_root):
    content = _read_text(agate_root / "dispatch-protocol.md")
    assert "自查≠gate" in content


def test_drift_g2_implementer_no_write_run_separation(agate_root):
    content = _read_text(agate_root / "assets/execution-roles/implementer.md")
    assert "写跑分离" not in content


def test_drift_g3_verifier_no_write_run_separation(agate_root):
    content = _read_text(agate_root / "assets/execution-roles/verifier.md")
    assert "写跑分离" not in content


def test_tag0005_bdd_1_backend_rows_plan_eng_review(agate_root):
    for rel in ("role-system.md", "rules/review-mapping.md", "phase-cards/P2-design.md"):
        content = _read_text(agate_root / rel)
        assert re.search(r"^\| backend \|.*plan-eng-review", content, re.M)


def test_tag0005_bdd_2_p2_review_unconditional_gate(agate_root):
    content = _read_text(agate_root / "scripts/check-gate.py")
    assert "P2-review.md 不存在（P2 评审不可裁剪" in content
    assert "P2-review.md frontmatter status 非 approved" in content


def test_tag0005_bdd_9_review_role_instruction_single_file(agate_root):
    hits = [
        p
        for p in agate_root.rglob("*.md")
        if "Review 角色特别指令" in _read_text(p)
    ]
    assert len(hits) == 1
    assert "assets/templates/dispatch-prompt.md" in str(hits[0])


def test_tag0005_bdd_12_empty_return_auto_retry_once(agate_root):
    content = _read_text(agate_root / "dispatch-protocol.md")
    assert "自动重试一次" in content


def test_tag0005_bdd_13_short_session_warning(agate_root):
    content = _read_text(agate_root / "dispatch-protocol.md")
    assert "会话时长异常短" in content
    assert "<1min" in content


def test_tag0005_bdd_14_retry_paused_unchanged(agate_root):
    content = _read_text(agate_root / "dispatch-protocol.md")
    assert "MAX_RETRY" in content
    assert "PAUSED 报告人工" in content


def test_tag0005_bdd_15_scripts_stderr_exit0_only_skip_semantics(agate_root):
    pattern = re.compile(r">&2;\s*exit 0")
    for sh in (agate_root / "scripts").glob("*.sh"):
        for line in _read_text(sh).splitlines():
            if pattern.search(line):
                assert "跳过" in line


# ========== 批次 8 补遗：PG.P2REVIEW / bdd-14 / bdd-28 / bdd-29（4 用例） ==========
# 8a-8h 按 P2 §5 子批表非穷举分区（`-k`）迁移后整文件核对，check-gate.bats 剩余 4 个
# @test（PG.P2REVIEW / bdd-14 / bdd-28 / bdd-29）此前未入 pytest（8h 偏离点已记录）。
# 本补遗补齐：PG.P2REVIEW = P2-review.md 不存在（exit 1，与 G2.13 差异在断言子串
# "P2-review.md 不存在"）；bdd-14 = P1 CRLF 行尾 frontmatter 提取（M6，exit 2，bats
# printf 写 CRLF 文本）；bdd-28/bdd-29 = 反引号包裹 [SUGGEST:]/[NEED_CONFIRM] 标记
# 仍被识别（RM-AG0001）。复用 8b `_P2_TWO_CAND_BODY` / `add_p2_candidate_count` 与
# 8g `_P1_MARKER_HEAD` / `_P1_MARKER_REVIEW` / `_write_p1_marker_task`。
# bdd-14 名称含平台关键词 CRLF → 按 P2 §5.2 加 @pytest.mark.windows_smoke（Windows
# checkout 的 CRLF review 文件是该用例验证的机制本身）。


def test_pg_p2review_not_found_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p2_design(td, _P2_TWO_CAND_BODY)
    add_p2_candidate_count(td, 2)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P2", str(td))
    assert result.returncode == 1
    assert "P2-review.md 不存在" in result.output


@pytest.mark.windows_smoke
def test_bdd14_crlf_review_frontmatter_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-review.md").write_text(
        "---\r\nphase: P1\r\ntask_id: T001-test\r\nstatus: approved\r\n"
        "agent: requirements-review\r\n---\r\n## BDD 评审\r\n- BDD-1: PASS\r\n",
        encoding="utf-8",
    )
    (td / "P1-requirements.md").write_text(
        "---\r\nagent: test\r\nrisk_level: medium\r\n"
        "phases: [P1,P2,P3,P4,P5,P6,P7,P8]\r\n---\r\n- [NO_NEED_CONFIRM]\r\n",
        encoding="utf-8",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2


def test_bdd28_backtick_suggest_warning_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td,
        _P1_MARKER_HEAD
        + "- [NO_NEED_CONFIRM]\n"
        + "- `[SUGGEST: 推荐 X，理由 Y]`\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2
    assert "SUGGEST" in result.output


def test_bdd29_backtick_need_confirm_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    _write_p1_marker_task(
        td, _P1_MARKER_HEAD + "- `[NEED_CONFIRM]` z 的边界条件需确认\n"
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "未解决的 NEED_CONFIRM" in result.output
