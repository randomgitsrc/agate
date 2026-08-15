# tests/unit/test_check_gate_p5_diff.py — check-gate.py P5 机械 diff 回归判定
# （check-gate-p5-diff.bats 13 用例迁移，TAG0011 批次 8i）。
# 覆盖（bats @test「PG.N」前缀）：PG.1-PG.12 + PG.9a——pre-task-baseline.md vs
#   P5-test-results/fail-list.txt 的机械 diff：两文件均缺失走原有分支 / 无新增无预存 /
#   新增失败拦截 / 预存失败登记足够放行 / known-failures.md 缺失拦截 / 预存已修复 /
#   空 pre / 空 post / 登记不完整 / 登记足够 / 基线损坏（缺 captured_at_commit）/
#   仅基线 / 仅 fail-list。
# 被测：agate/scripts/check-gate.py P5 TASK_DIR（gate_p5 的机械 diff 分支）。
# 流语义：GATE P5 消息一律 sys.stderr.write → 断言合并流 result.output
#   （P2 §3.2 流语义规则，BLOCKER-1；bats $output 等价）。
# 等价映射：bats make_baseline/make_post_fails helper → 模块级纯函数
#   _make_baseline / _make_post_fails（同语义：captured_at_commit 头 + ```fail-list 块；
#   fail-list.txt 逐行写）；bats `create_task_dir` → task_dir()。
# 函数命名 test_pg_N_<slug>（PG 前缀，与 bats PG.N 一一对应）。

import pytest


def _run_gate(agate_scripts, python_exe, run_cli, phase, task_arg):
    """bats `'$PYTHON' '$AGATE_SCRIPTS/check-gate.py' P5 TASK_DIR` 等价。"""
    cmd = [python_exe, str(agate_scripts / "check-gate.py"), phase, task_arg]
    return run_cli(*cmd)


def _make_baseline(td, commit, *fails):
    """bats make_baseline 等价：写 pre-task-baseline.md（captured_at_commit 头 + fail-list 块）。"""
    body = (
        "---\n"
        f"captured_at_commit: {commit}\n"
        "generated_by: agate-capture-env-baseline.sh\n"
        "---\n"
        "# 任务前环境基线\n"
        "\n"
        f"失败数：{len(fails)}\n"
        "\n"
        "```fail-list\n"
    )
    body += "\n".join(fails) + "\n```\n"
    (td / "pre-task-baseline.md").write_text(body, encoding="utf-8")


def _make_post_fails(td, *fails):
    """bats make_post_fails 等价：写 P5-test-results/fail-list.txt（逐行失败 id）。"""
    (td / "P5-test-results").mkdir(parents=True, exist_ok=True)
    content = "\n".join(fails)
    if content:
        content += "\n"
    (td / "P5-test-results" / "fail-list.txt").write_text(content, encoding="utf-8")


_KNOWN_FAILURES_HEAD = (
    "---\n"
    "agent: test\n"
    "---\n"
    "\n"
    "## 预存失败\n"
    "\n"
    "| # | 测试文件 | 失败数 | 根因 | 与本任务相关 | 处理计划 |\n"
    "|---|---------|--------|------|-------------|---------|\n"
)


def _write_known_failures(td, rows):
    (td / "known-failures.md").write_text(
        _KNOWN_FAILURES_HEAD + rows, encoding="utf-8"
    )


@pytest.mark.windows_smoke
def test_pg_1_both_missing_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_2_no_new_no_stored_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123")
    _make_post_fails(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_3_new_fails_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x")
    _make_post_fails(td, "tests/test_a.py::test_x", "tests/test_b.py::test_y")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 1
    assert "新增失败" in result.output
    assert "test_b.py::test_y" in result.output


def test_pg_4_stored_failures_registered_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x")
    _make_post_fails(td, "tests/test_a.py::test_x")
    _write_known_failures(td, "| 1 | test_a | 1 | root cause | 否 | postpone |\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_5_known_failures_missing_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x")
    _make_post_fails(td, "tests/test_a.py::test_x")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 1
    assert "known-failures.md 不存在" in result.output


def test_pg_6_stored_fixed_exit_2(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x", "tests/test_b.py::test_y")
    _make_post_fails(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_7_empty_pre_all_new_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123")
    _make_post_fails(td, "tests/test_a.py::test_x", "tests/test_b.py::test_y")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 1
    assert "新增失败" in result.output


def test_pg_8_empty_post_all_fixed_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x")
    _make_post_fails(td)

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_9_registration_insufficient_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(
        td, "abc123", "tests/test_a.py::test_x", "tests/test_b.py::test_y"
    )
    _make_post_fails(td, "tests/test_a.py::test_x", "tests/test_b.py::test_y")
    _write_known_failures(td, "| 1 | test_a | 1 | root cause | 否 | postpone |\n")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 1
    assert "登记不完整" in result.output


def test_pg_9a_registration_sufficient_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(
        td, "abc123", "tests/test_a.py::test_x", "tests/test_b.py::test_y"
    )
    _make_post_fails(td, "tests/test_a.py::test_x", "tests/test_b.py::test_y")
    _write_known_failures(
        td,
        "| 1 | test_a | 1 | root cause | 否 | postpone |\n"
        "| 2 | test_b | 1 | root cause | 否 | postpone |\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_10_corrupted_baseline_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    (td / "pre-task-baseline.md").write_text(
        "---\n"
        "generated_by: something\n"
        "---\n"
        "# Corrupted baseline\n"
        "```fail-list\n"
        "tests/test_a.py::test_x\n"
        "```\n",
        encoding="utf-8",
    )
    _make_post_fails(td, "tests/test_b.py::test_y")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
    assert "captured_at_commit" in result.output
    assert "损坏" in result.output


def test_pg_11_only_baseline_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_baseline(td, "abc123", "tests/test_a.py::test_x")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2


def test_pg_12_only_fail_list_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _make_post_fails(td, "tests/test_a.py::test_x")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P5", str(td))
    assert result.returncode == 2
