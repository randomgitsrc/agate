# tests/unit/test_agate_capture_env_baseline.py — 环境基线捕获（EB.1-EB.15）
# （agate-capture-env-baseline.bats 15 用例迁移，TAG0011 批次 5）
# 被测：agate/scripts/agate-capture-env-baseline.py（TASK_DIR arg；P5 命令经
#   agate-read-p5-commands.py 解析 + run_test_with_formatter 执行 + formatter 提取 fail-list）
# 流语义：ENV_BASELINE 消息一律 sys.stderr.write → 断言用 .stderr（P2 §3.2 先判流归属）；
#   EB.1 no-op 零输出（合并流 .output == ""）
# 机制：fake runner = tmp_path 下可执行 bash 脚本（cat heredoc 输出 + exit code），
#   P2-design.md 的 P5 命令指向该脚本（等价 bats make_fake_runner / make_recording_runner）

import os
import shutil

import pytest


def _write_fake_runner(tmp_path, output, exit_code, name="fake-runner"):
    """bats make_fake_runner 等价：cat 输出 + 退出码的 bash 脚本。"""
    runner = tmp_path / name
    runner.write_text(
        f"#!/bin/bash\ncat <<'OUT'\n{output}\nOUT\nexit {exit_code}\n",
        encoding="utf-8",
    )
    os.chmod(runner, 0o755)
    return str(runner)


def _write_recording_runner(tmp_path, output, exit_code, sentinel, name="rec-runner"):
    """bats make_recording_runner 等价：touch sentinel + cat 输出 + 退出码。"""
    runner = tmp_path / name
    runner.write_text(
        f"#!/bin/bash\ntouch '{sentinel}'\ncat <<'OUT'\n{output}\nOUT\nexit {exit_code}\n",
        encoding="utf-8",
    )
    os.chmod(runner, 0o755)
    return str(runner)


def _setup_repo_with_p2(git_repo, p2_content):
    """bats setup_git_repo_with_p2 等价：git 仓库 + agate-workspace/tasks/T001/P2-design.md。"""
    repo = git_repo.path
    task = repo / "agate-workspace" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P2-design.md").write_text(p2_content, encoding="utf-8")
    git_repo.commit("init")
    return repo


def _run_baseline(agate_scripts, python_exe, run_cli, repo, task_rel="agate-workspace/tasks/T001"):
    """bats `cd $repo && python agate-capture-env-baseline.py <task>` 等价。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-capture-env-baseline.py"),
        task_rel,
        cwd=str(repo),
    )


@pytest.mark.windows_smoke
def test_eb_1_existing_baseline_noop(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "pre-task-baseline.md").write_text("existing baseline\n", encoding="utf-8")

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-capture-env-baseline.py"),
        str(td),
    )
    assert result.returncode == 0
    assert "ENV_BASELINE" not in result.output
    assert (td / "pre-task-baseline.md").read_text(encoding="utf-8").strip() == "existing baseline"


def test_eb_2_p2_design_missing_warning(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir(phases=["P0", "P1", "P3", "P4", "P5", "P6", "P7", "P8"])

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-capture-env-baseline.py"),
        str(td),
    )
    assert result.returncode == 0
    assert "P2-design.md 不存在" in result.stderr
    assert not (td / "pre-task-baseline.md").exists()


def test_eb_3_no_gate_commands_p5_warning(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text(
        "# P2 design\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands: {}\n",
        encoding="utf-8",
    )

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-capture-env-baseline.py"),
        str(td),
    )
    assert result.returncode == 0
    assert "未在 P2-design.md 找到 gate_commands.P5" in result.stderr
    assert not (td / "pre-task-baseline.md").exists()


def test_eb_4_first_capture_runs_and_writes(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "3 failed, 5 passed\n"
        "FAILED tests/test_a.py::test_x\n"
        "FAILED tests/test_b.py::test_y\n"
        "FAILED tests/test_c.py::test_z",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr

    baseline = repo / "agate-workspace/tasks/T001/pre-task-baseline.md"
    assert baseline.is_file()
    cache_dir = repo / "docs" / ".agate-env-baseline-cache"
    assert cache_dir.is_dir()
    assert len(list(cache_dir.glob("*.md"))) == 1
    text = baseline.read_text(encoding="utf-8")
    assert "captured_at_commit:" in text
    assert "tests/test_a.py::test_x" in text


def test_eb_5_cache_hit_same_commit_skips_rerun(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    sentinel = str(tmp_path / "eb5-ran")
    fake = _write_recording_runner(
        tmp_path,
        "2 failed, 5 passed\n"
        "FAILED tests/test_a.py::test_x\n"
        "FAILED tests/test_b.py::test_y",
        1,
        sentinel,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert os.path.exists(sentinel)

    os.remove(sentinel)
    t002 = repo / "agate-workspace" / "tasks" / "T002"
    t002.mkdir(parents=True)
    shutil.copyfile(repo / "agate-workspace/tasks/T001/P2-design.md", t002 / "P2-design.md")

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T002")
    assert result.returncode == 0
    assert "复用缓存" in result.stderr
    assert not os.path.exists(sentinel)
    assert (t002 / "pre-task-baseline.md").is_file()


def test_eb_6_cache_miss_commit_changed(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "1 failed, 5 passed\nFAILED tests/test_a.py::test_x",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr

    (repo / "newfile.txt").write_text("new commit\n", encoding="utf-8")
    git_repo.commit("second commit")
    t002 = repo / "agate-workspace" / "tasks" / "T002"
    t002.mkdir(parents=True)
    shutil.copyfile(repo / "agate-workspace/tasks/T001/P2-design.md", t002 / "P2-design.md")

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T002")
    assert result.returncode == 0
    assert "已捕获" in result.stderr
    assert (t002 / "pre-task-baseline.md").is_file()


def test_eb_7_same_commit_diff_commands_miss(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake1 = _write_fake_runner(
        tmp_path,
        "1 failed, 5 passed\nFAILED tests/test_a.py::test_x",
        1,
        name="fake-runner-1",
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake1}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr

    fake2 = _write_fake_runner(
        tmp_path,
        "2 failed, 3 passed\n"
        "FAILED tests/test_d.py::test_w\n"
        "FAILED tests/test_e.py::test_v",
        1,
        name="fake-runner-2",
    )
    t002 = repo / "agate-workspace" / "tasks" / "T002"
    t002.mkdir(parents=True)
    (t002 / "P2-design.md").write_text(
        f"gate_commands:\n  P5: {fake2}\n  P5_formatter: pytest.sh",
        encoding="utf-8",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo, "agate-workspace/tasks/T002")
    assert result.returncode == 0
    assert "已捕获" in result.stderr
    text = (t002 / "pre-task-baseline.md").read_text(encoding="utf-8")
    assert "test_d.py::test_w" in text


def test_eb_8_runner_crash_no_files_written(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(tmp_path, "some error output", 127)
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "本身崩溃" in result.stderr
    assert not (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").exists()


def test_eb_9_count_mismatch_no_files_written(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "3 failed, 5 passed\nFAILED tests/test_a.py::test_x",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "不一致" in result.stderr
    assert not (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").exists()


def test_eb_10_two_commands_merged_dedup(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake1 = _write_fake_runner(
        tmp_path,
        "2 failed, 5 passed\n"
        "FAILED tests/test_a.py::test_x\n"
        "FAILED tests/test_b.py::test_y",
        1,
        name="fake-runner-1",
    )
    fake2 = _write_fake_runner(
        tmp_path,
        "2 failed, 3 passed\n"
        "FAILED tests/test_b.py::test_y\n"
        "FAILED tests/test_c.py::test_z",
        1,
        name="fake-runner-2",
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake1}\n  P5_formatter: pytest.sh\n"
        f"  P5_e2e: {fake2}\n  P5_e2e_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr

    text = (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").read_text(encoding="utf-8")
    assert "test_a.py::test_x" in text
    assert "test_b.py::test_y" in text
    assert "test_c.py::test_z" in text
    fail_lines = [line for line in text.splitlines() if line.startswith("tests/")]
    assert len(fail_lines) == 3


def test_eb_11_non_git_repo_warning(task_dir, tmp_path, agate_scripts, python_exe, run_cli):
    td = task_dir()
    (td / "P2-design.md").write_text(
        'gate_commands:\n  P5: "pytest -q"\n  P5_formatter: "pytest.sh"\n',
        encoding="utf-8",
    )

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-capture-env-baseline.py"),
        str(td),
        env={"GIT_DIR": str(tmp_path / "nonexistent" / ".git")},
    )
    assert result.returncode == 0
    assert "非 git 仓库" in result.stderr
    assert not (td / "pre-task-baseline.md").exists()


def test_eb_12_corrupted_cache_reused(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "1 failed, 5 passed\nFAILED tests/test_a.py::test_x",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr

    cache_dir = repo / "docs" / ".agate-env-baseline-cache"
    cache_file = next(cache_dir.glob("*.md"))
    cache_file.write_text("corrupted content without frontmatter\n", encoding="utf-8")
    (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").unlink()

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "复用缓存" in result.stderr
    text = (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").read_text(encoding="utf-8")
    assert "corrupted content" in text


def test_eb_13_pytest_formatter_extracts_fail_list(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "2 failed, 3 passed\n"
        "FAILED tests/test_alpha.py::test_one\n"
        "FAILED tests/test_beta.py::test_two",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: pytest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr
    assert "失败数=2" in result.stderr

    text = (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").read_text(encoding="utf-8")
    assert "tests/test_alpha.py::test_one" in text
    assert "tests/test_beta.py::test_two" in text


def test_eb_14_no_formatter_no_files(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "2 failed, 5 passed\n"
        "FAILED tests/test_a.py::test_x\n"
        "FAILED tests/test_b.py::test_y",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "无 formatter" in result.stderr
    assert not (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").exists()


def test_eb_15_vitest_formatter_extracts_fail_list(git_repo, tmp_path, agate_scripts, python_exe, run_cli):
    fake = _write_fake_runner(
        tmp_path,
        "Tests  2 failed | 4 passed\nFAIL tests/b.test.ts\nFAIL tests/c.test.ts",
        1,
    )
    repo = _setup_repo_with_p2(
        git_repo,
        f"gate_commands:\n  P5: {fake}\n  P5_formatter: vitest.sh",
    )

    result = _run_baseline(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert "已捕获" in result.stderr
    assert "失败数=2" in result.stderr

    text = (repo / "agate-workspace/tasks/T001/pre-task-baseline.md").read_text(encoding="utf-8")
    assert "tests/b.test.ts" in text
    assert "tests/c.test.ts" in text
