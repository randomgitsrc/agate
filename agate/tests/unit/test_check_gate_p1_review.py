# tests/unit/test_check_gate_p1_review.py — check-gate.py P1-review 独立评审分支
# （check-gate-p1-review.bats 9 用例迁移，TAG0011 批次 8i）。
# 覆盖（bats @test「P1: ...」前缀）：P1-review.md 缺失 / agent=main /
#   无 BDD 编号引用 / status:approved+agent≠main+含锚点 / status:rejected /
#   缺 status 字段 / 对抗绕过（frontmatter rejected + 正文 approved 字面串）/
#   BDD-21 NEED_CONFIRM 未结构化解决仍阻塞 / 无 NEED_CONFIRM。
# 被测：agate/scripts/check-gate.py P1 TASK_DIR（gate_p1，P2-review 同机制挂载
#   相邻但不同校验对象，BDD-21 流 C）。
# 流语义：GATE P1 消息一律 sys.stderr.write → 断言合并流 result.output
#   （P2 §3.2 流语义规则，BLOCKER-1；bats $output 等价）。
# 等价映射：bats `create_task_dir --no-state-yaml` + `cat >` heredoc 覆写
#   P1-requirements.md / P1-review.md → task_dir(no_state_yaml=True) + write_text。
# 函数命名 test_pg_p1review_N_<slug>（PG 前缀，P2 §5 N1 PG.P2REVIEW 同族约定）。

import pytest


def _run_gate(agate_scripts, python_exe, run_cli, phase, task_arg):
    """bats `'$PYTHON' '$AGATE_SCRIPTS/check-gate.py' P1 TASK_DIR` 等价。"""
    cmd = [python_exe, str(agate_scripts / "check-gate.py"), phase, task_arg]
    return run_cli(*cmd)


_P1_REQ_BODY = (
    "---\n"
    "phase: P1\n"
    "task_id: T001-test\n"
    "status: draft\n"
    "agent: analyst\n"
    "---\n"
    "# Requirements\n"
    "- Given x When y Then z\n"
)


def _write_p1_review(td, body):
    (td / "P1-review.md").write_text(body, encoding="utf-8")


@pytest.mark.windows_smoke
def test_pg_p1review_1_missing_review_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "P1-review.md" in result.output


def test_pg_p1review_2_agent_main_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: main\n"
        "---\n"
        "approved\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "agent=main" in result.output


def test_pg_p1review_3_no_bdd_reference_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "All good, approved.\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "BDD" in result.output or "锚点" in result.output


def test_pg_p1review_4_approved_with_anchor_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS + 覆盖维度：数据✓ 前端✓ 多端✗ 边界✓ 兼容✓\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2


def test_pg_p1review_5_rejected_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: rejected\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: FAIL - 不可二值判定\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1


def test_pg_p1review_6_missing_status_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS + 覆盖维度：数据✓\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1


def test_pg_p1review_7_rejected_with_approved_literal_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: rejected\n"
        "agent: requirements-review\n"
        "---\n"
        "## 裁决说明\n"
        "\n"
        "gate 规则要求 status: approved 才放行，本次评审未通过。\n"
        "\n"
        "## BDD 评审\n"
        "- BDD-1: FAIL - 不可二值判定\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "非 approved" in result.output


def test_pg_p1review_8_need_confirm_blocking_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(
        _P1_REQ_BODY + "- [NEED_CONFIRM] z 的边界条件需确认\n", encoding="utf-8"
    )
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 1
    assert "NEED_CONFIRM" in result.output


def test_pg_p1review_9_no_need_confirm_exit_2(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(no_state_yaml=True)
    (td / "P1-requirements.md").write_text(_P1_REQ_BODY, encoding="utf-8")
    _write_p1_review(
        td,
        "---\n"
        "phase: P1\n"
        "task_id: T001-test\n"
        "status: approved\n"
        "agent: requirements-review\n"
        "---\n"
        "## BDD 评审\n"
        "- BDD-1: PASS\n",
    )

    result = _run_gate(agate_scripts, python_exe, run_cli, "P1", str(td))
    assert result.returncode == 2
