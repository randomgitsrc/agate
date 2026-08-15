# tests/regression/test_v060_p8_internal_only.py — 回归测试：裁剪 P8 需 internal_only
# （v060-p8-internal-only.bats 3 用例迁移，TAG0011 批次 11）
# 触发：fabca40 hardening R5。
# T001 v2.0 流 A（BDD-1/9）改写：internal_only/internal_only_reason 现由 add_p1_field
#   写入 P1-requirements.md 的 frontmatter 块（而非 v0.35 的正文追加）——check-pruning.py
#   仍能正确读取这两个 presence 语义字段。@test 数保持 3 不变。
# 流语义：GATE PRUNING 失败消息一律 sys.stderr.write → 断言用合并流 result.output
#   （P2 §3.2，BLOCKER-1）。

import pytest

from conftest import add_p1_field, add_pruning_excuse


def _run_pruning(agate_scripts, python_exe, run_cli, task_arg):
    return run_cli(python_exe, str(agate_scripts / "check-pruning.py"), task_arg)


_PHASES_NO_P8 = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]


@pytest.mark.windows_smoke
def test_r4_1_p8_pruned_no_internal_only_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(phases=_PHASES_NO_P8)

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "internal_only" in result.output


def test_r4_2_p8_internal_only_with_reason_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(phases=_PHASES_NO_P8)
    add_p1_field(td, "internal_only", "true")
    add_p1_field(td, "internal_only_reason", "内部工具，无外部用户")
    add_pruning_excuse(td, "P8", "内部任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 0
    lines = (td / "P1-requirements.md").read_text(encoding="utf-8").splitlines()
    assert any(line == "---" for line in lines)
    assert any(line == "internal_only: true" for line in lines)


def test_r4_3_p8_internal_only_no_reason_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir(phases=_PHASES_NO_P8)
    add_p1_field(td, "internal_only", "true")
    add_pruning_excuse(td, "P8", "内部任务", "低")

    result = _run_pruning(agate_scripts, python_exe, run_cli, str(td))
    assert result.returncode == 1
    assert "internal_only_reason" in result.output
