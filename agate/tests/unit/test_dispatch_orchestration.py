# tests/unit/test_dispatch_orchestration.py — dispatch_plan: 字段契约测试（TAG0014，plan Task 1）
# 被测：
#   agate/scripts/agate-md-field-get.py 的 dispatch_plan op（BDD-1/7）
#   agate/scripts/check-gate.py 的 P2 gate dispatch_plan 校验（BDD-2~7）
# 契约（plan Task 1 / P2-design §3.1）：
#   * P2-design.md frontmatter 单行 flow YAML（与 candidate_count 同级），如
#     dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}]}
#   * mode ∈ {single, static-batch, parallel, recon-then-split, serial}
#   * 缺字段 / YAML 解析失败 → 行为等同现状（向后兼容，不误拦不崩溃）
#   * P2 gate 对非法 mode / parallel_limit<1 / batch 缺 complexity / 批数超限 报 GATE P2 ERROR + exit 1
# 测试设计：正向 5 + 负向 5，对应 P1 BDD-19（覆盖 BDD-1~7）+ 修复轮负向补强（mode 非 str / complexity 非法值）。
# 平台无关：conftest fixtures（python_exe 探测不裸 python3）、tmp_path 不用 /tmp。

import json

import pytest

from conftest import add_p2_review

_DISPATCH_MODES = frozenset({"single", "static-batch", "parallel", "recon-then-split", "serial"})
_VALID_COMPLEXITY = frozenset({"low", "medium", "high"})

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


def _write_p2_design(td, dispatch_line=None):
    """写合规 P2-design.md：frontmatter（agent/candidate_count + 可选 dispatch_plan 单行 flow YAML）+ 正文。"""
    fm = "---\nagent: test\ncandidate_count: 2\n"
    if dispatch_line is not None:
        fm += f"dispatch_plan: {dispatch_line}\n"
    fm += "---\n"
    (td / "P2-design.md").write_text(fm + _P2_TWO_CAND_BODY, encoding="utf-8")


def _run_gate(agate_scripts, python_exe, run_cli, td):
    return run_cli(python_exe, str(agate_scripts / "check-gate.py"), "P2", str(td))


def _run_op(agate_scripts, python_exe, run_cli, p2_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-md-field-get.py"),
        "dispatch_plan",
        env={"FILE": str(p2_file)},
    )


# ========== 正向 5 条 ==========


@pytest.mark.windows_smoke
def test_dispatch_plan_required_fields(agate_scripts, python_exe, run_cli, task_dir):
    """BDD-19 正向①/BDD-1：op 输出合法 JSON 含 mode（∈ 枚举），parallel_limit 存在时 ≥ 1。"""
    td = task_dir()
    _write_p2_design(
        td,
        "{mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}]}",
    )
    result = _run_op(agate_scripts, python_exe, run_cli, td / "P2-design.md")
    assert result.returncode == 0
    plan = json.loads(result.output.strip())
    assert "mode" in plan
    assert plan["mode"] in _DISPATCH_MODES
    if "parallel_limit" in plan:
        assert plan["parallel_limit"] >= 1


def test_dispatch_plan_mode_valid(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-19 正向②/BDD-3：mode 非法值（xyz）→ P2 gate 报 GATE P2 ERROR + exit 1。"""
    td = task_dir()
    _write_p2_design(td, "{mode: xyz}")
    add_p2_review(td)
    result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "GATE P2" in result.output


def test_dispatch_plan_batch_granularity(agate_scripts, python_exe, run_cli, task_dir):
    """BDD-19 正向③/BDD-5：batches 各含 id + complexity ∈ {low, medium, high}；模式 1/5 可无 batches。"""
    td = task_dir()
    _write_p2_design(
        td,
        "{mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}, {id: B2, complexity: low}]}",
    )
    result = _run_op(agate_scripts, python_exe, run_cli, td / "P2-design.md")
    assert result.returncode == 0
    plan = json.loads(result.output.strip())
    assert "batches" in plan
    for batch in plan["batches"]:
        assert "id" in batch
        assert batch["complexity"] in _VALID_COMPLEXITY

    td_single = task_dir()
    _write_p2_design(td_single, "{mode: single}")
    add_p2_review(td_single)
    gate_result = _run_gate(agate_scripts, python_exe, run_cli, td_single)
    assert gate_result.returncode == 2


def test_dispatch_plan_parallel_limit(agate_scripts, python_exe, run_cli, task_dir):
    """BDD-19 正向④/BDD-6：static-batch/parallel 模式 batch 数 ≤ parallel_limit（默认 3）。"""
    td = task_dir()
    _write_p2_design(
        td,
        "{mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: low}, {id: B2, complexity: low}]}",
    )
    result = _run_op(agate_scripts, python_exe, run_cli, td / "P2-design.md")
    assert result.returncode == 0
    plan = json.loads(result.output.strip())
    limit = plan.get("parallel_limit", 3)
    assert len(plan.get("batches", [])) <= limit

    add_p2_review(td)
    gate_result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert gate_result.returncode == 2


def test_dispatch_plan_optional(agate_scripts, python_exe, run_cli, task_dir):
    """BDD-19 正向⑤/BDD-2：无 dispatch_plan 时 P2 gate 行为等同现状（exit 2、输出逐行一致）。"""
    td_with = task_dir()
    _write_p2_design(td_with, "{mode: parallel, parallel_limit: 2}")
    add_p2_review(td_with)

    op_result = _run_op(agate_scripts, python_exe, run_cli, td_with / "P2-design.md")
    assert op_result.returncode == 0
    json.loads(op_result.output.strip())

    td_without = task_dir()
    _write_p2_design(td_without)
    add_p2_review(td_without)

    gate_with = _run_gate(agate_scripts, python_exe, run_cli, td_with)
    gate_without = _run_gate(agate_scripts, python_exe, run_cli, td_without)
    assert gate_with.returncode == gate_without.returncode == 2
    assert gate_with.output == gate_without.output


# ========== 负向 3 条 ==========


def test_dispatch_plan_malformed_yaml(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-19 负向①/BDD-7：dispatch_plan 为不可解析 YAML → 不误拦、不崩溃（按缺字段处理）。"""
    td = task_dir()
    _write_p2_design(td, "{mode: [unclosed")
    add_p2_review(td)

    op_result = _run_op(agate_scripts, python_exe, run_cli, td / "P2-design.md")
    assert op_result.returncode == 0
    assert op_result.output.strip() == ""

    gate_result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert gate_result.returncode == 2
    assert "ERROR" not in gate_result.output


def test_dispatch_plan_parallel_limit_zero(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-19 负向②/BDD-4：parallel_limit=0 → P2 gate 报 GATE P2 ERROR + exit 1。"""
    td = task_dir()
    _write_p2_design(td, "{mode: parallel, parallel_limit: 0}")
    add_p2_review(td)
    result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "GATE P2" in result.output


def test_dispatch_plan_batch_missing_complexity(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-19 负向③/BDD-5 子场景①：batch 缺 complexity → P2 gate 报 GATE P2 ERROR + exit 1。"""
    td = task_dir()
    _write_p2_design(td, "{mode: static-batch, parallel_limit: 3, batches: [{id: B1}]}")
    add_p2_review(td)
    result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "GATE P2" in result.output


def test_dispatch_plan_mode_non_string(task_dir, agate_scripts, python_exe, run_cli):
    """修复轮负向④/CRITICAL：mode 为非字符串（list）→ P2 gate 干净报 GATE P2 ERROR + exit 1，不崩溃。"""
    td = task_dir()
    _write_p2_design(td, "{mode: [single]}")
    add_p2_review(td)
    result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "GATE P2 ERROR" in result.output


def test_dispatch_plan_complexity_invalid(task_dir, agate_scripts, python_exe, run_cli):
    """修复轮负向⑤/BDD-5 子场景②：complexity 为非法值 → P2 gate 报 GATE P2 ERROR + exit 1。"""
    td = task_dir()
    _write_p2_design(
        td,
        "{mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: invalid}]}",
    )
    add_p2_review(td)
    result = _run_gate(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "GATE P2 ERROR" in result.output
