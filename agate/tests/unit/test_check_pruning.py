# tests/unit/test_check_pruning.py — 裁剪条件检查
# （check-pruning.bats 29 用例迁移，TAG0011 批次 6b）
# 被测：agate/scripts/check-pruning.py（TASK_DIR；exit 0 = 通过 / exit 1 = 条件不满足 /
#   exit 2 = 无 P1 文件）。
# task_dir 等价 create_task_dir（P0-P8 文件 + frontmatter risk_level/phases）；add_p1_field /
#   add_pruning_excuse 等价 fixtures.bash helper（frontmatter 块写入，T001 v2.0 流 A）。
# P2.6a/6b 需要 git_repo（git diff --cached 源码文件数）+ 在 repo 内复制 task 目录，
#   run_cli(..., cwd=repo) 等价 bats `cd '$repo'`。
# 流语义：GATE PRUNING 失败消息一律 sys.stderr.write → 按 P2 §3.2 先判流归属，
#   本文件断言一律用合并流 result.output（与 bats $output 等价，BLOCKER-1）。

import shutil

import pytest

from conftest import add_p1_field, add_pruning_excuse

_YAML_LIST_P1 = (
    "---\n"
    "agent: test\n"
    "---\n"
    "risk_level: low\n"
    "phases:\n"
    "  - P1\n"
    "  - P2\n"
    "  - P4\n"
    "  - P5\n"
    "  - P6\n"
    "  - P8\n"
    "coupling_checklist: [api-schema: checked, data-model: checked]\n"
    "\n"
    "### 主流程\n"
    "\n"
    "#### BDD-1: test\n"
    "- Given test precondition\n"
    "- When test action\n"
    "- Then test result\n"
    "裁剪 P3: 纯配置改动无业务逻辑\n"
    "裁剪 P7: 小改动\n"
    "跳过风险: 无 TDD 需求\n"
)


def _run_pruning(agate_scripts, python_exe, run_cli, task_arg, cwd=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-pruning.py"),
        task_arg,
        cwd=cwd,
    )


@pytest.mark.windows_smoke
def test_p2_1_missing_risk_level_exit_1(task_dir, tmp_path, agate_scripts, python_exe, run_cli):
    d = tmp_path / "task"
    d.mkdir()
    (d / "P1-requirements.md").write_text("phases: [P0, P1, P2]\n", encoding="utf-8")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(d))
    assert result.returncode == 1
    assert "缺 risk_level" in result.output


def test_p2_2_prune_p2_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P2 不可裁剪" in result.output


def test_p2_3a_prune_p2_legacy_p2_pruned_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    add_p1_field(td, "legacy_p2_pruned", "true")
    add_pruning_excuse(td, "P2", "v0.5 任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P2 不可裁剪" in result.output


def test_p2_3b_prune_p2_design_trivial_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    add_p1_field(td, "design_trivial", "true")
    add_pruning_excuse(td, "P2", "文案修改", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P2 不可裁剪" in result.output


def test_p2_3c_prune_p2_follows_existing_pattern_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    add_p1_field(td, "follows_existing_pattern", "[src/foo.py]")
    add_pruning_excuse(td, "P2", "照搬", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P2 不可裁剪" in result.output


def test_p2_4_prune_p6_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8"])

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P6 不可裁剪" in result.output


def test_p2_4a_prune_p6_no_behavior_change_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8"])
    add_p1_field(td, "no_behavior_change", "true")
    add_pruning_excuse(td, "P6", "无行为变更", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P6 不可裁剪" in result.output


def test_p2_5c_prune_p4_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P5", "P6", "P7", "P8"], risk_level="low")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P4 不可裁剪" in result.output


def test_p2_5d_prune_p5_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P6", "P7", "P8"], risk_level="low")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P5 不可裁剪" in result.output


def test_p2_5_legacy_fields_high_prune_p3_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(
        phases=["P0", "P1", "P2", "P4", "P5", "P6", "P7", "P8"],
        risk_level="high",
        legacy_fields=True,
    )

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P3 不可裁剪" in result.output
    assert "仅 low" in result.output


def test_p2_5b_medium_prune_p3_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P4", "P5", "P6", "P7", "P8"], risk_level="medium")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P3 不可裁剪" in result.output
    assert "仅 low" in result.output


def test_p2_6a_prune_p7_source_count_gt5_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")

    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"])
    shutil.copytree(td, repo / "task")
    for i in range(1, 7):
        (repo / f"src_{i}.py").write_text(f"file {i}\n", encoding="utf-8")
    git_repo.stage("src_*.py")

    result = _run_pruning(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 1
    assert "源码文件数" in result.output


def test_p2_6b_prune_p7_source_count_le5_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    for i in range(1, 4):
        (repo / f"src_{i}.py").write_text(f"file {i}\n", encoding="utf-8")
    git_repo.commit("init")

    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"])
    add_p1_field(td, "coupling_checklist", "[api-schema: checked, data-model: checked]")
    add_pruning_excuse(td, "P7", "小改动", "低")
    shutil.copytree(td, repo / "task")
    git_repo.stage("src_*.py")

    result = _run_pruning(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0


def test_p2_6c_prune_p7_implicit_coupling_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"])
    add_p1_field(td, "implicit_coupling", "[api-schema, data-model]")
    add_pruning_excuse(td, "P7", "理由", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "implicit_coupling" in result.output


def test_p2_6d_prune_p7_no_coupling_checklist_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"])
    add_pruning_excuse(td, "P7", "小改动", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "coupling_checklist" in result.output


def test_p2_6e_prune_p7_coupling_checklist_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P8"])
    add_p1_field(td, "coupling_checklist", "[api-schema: checked, data-model: checked]")
    add_pruning_excuse(td, "P7", "小改动", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_p2_7_prune_p8_no_internal_only_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert ("P8 不可裁" in result.output) or ("internal_only" in result.output)


def test_p2_7a_prune_p8_internal_only_reason_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])
    add_p1_field(td, "internal_only", "true")
    add_p1_field(td, "internal_only_reason", "内部工具，无外部用户")
    add_pruning_excuse(td, "P8", "内部任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_p2_8_prune_reason_missing_skip_risk_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    p1 = td / "P1-requirements.md"
    p1.write_text(
        p1.read_text(encoding="utf-8") + "\n裁剪 P2: 某种理由\n",
        encoding="utf-8",
    )

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "跳过风险" in result.output


def test_p2_12_prune_p6_no_skip_risk_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8"])
    add_p1_field(td, "no_behavior_change", "true")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P6 不可裁剪" in result.output


def test_p2_12a_prune_p6_no_behavior_change_skip_risk_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8"])
    add_p1_field(td, "no_behavior_change", "true")
    add_pruning_excuse(td, "P6", "无行为变更", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P6 不可裁剪" in result.output


def test_p2_13_prune_p8_internal_only_no_reason_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])
    add_p1_field(td, "internal_only", "true")
    add_pruning_excuse(td, "P8", "内部任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "internal_only_reason" in result.output


def test_p2_14_prune_p8_internal_only_with_reason_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])
    add_p1_field(td, "internal_only", "true")
    add_p1_field(td, "internal_only_reason", "内部工具，无外部用户")
    add_pruning_excuse(td, "P8", "内部任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_p2_9_prune_declaration_mismatch_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    (td / "P2-design.md").write_text("actual design\n", encoding="utf-8")
    add_pruning_excuse(td, "P2", "理由", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "裁剪声明与执行不一致" in result.output


def test_p2_9a_prune_p2_override_with_output_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])
    (td / "P2-design.md").write_text("actual design\n", encoding="utf-8")
    add_p1_field(td, "override", "P2 retained manually")
    add_p1_field(td, "legacy_p2_pruned", "true")
    add_pruning_excuse(td, "P2", "理由", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "P2 不可裁剪" in result.output


def test_p2_10_no_p1_file_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    d = tmp_path / "task"
    d.mkdir()

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(d))
    assert result.returncode == 2


def test_p2_11_happy_path_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_p2_52_yaml_list_phases_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P4", "P5", "P6", "P8"], risk_level="low")
    (td / "P1-requirements.md").write_text(_YAML_LIST_P1, encoding="utf-8")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0


def test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P2", "P4", "P5", "P6", "P8"], risk_level="low")
    (td / "P1-requirements.md").write_text(_YAML_LIST_P1, encoding="utf-8")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0
