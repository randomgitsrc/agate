# tests/unit/test_check_frontmatter.py — frontmatter schema 校验器
# （check-frontmatter.bats 14 用例迁移，TAG0011 批次 7）
# 被测：agate/scripts/agate-frontmatter-check.py（env FILE 传参）——校验错误经 stdout
#   print 输出（P2 §3.2 先判流归属：确定 stdout → result.stdout 亦可，但本文件一律用
#   合并流 result.output，与 bats $output 等价，BLOCKER-1，双跑对照不漂移）；
#   check-frontmatter.py（薄壳，FILE 位置参数）经 subprocess 转发并原样退出码。
# 流语义：CF.11/CF.14 两处 `[ -z "$output" ]` → 合并流空断言 result.output == ""。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest

_P1_HEAD = (
    "---\n"
    "phase: P1\n"
    "task_id: T001\n"
    "agent: analyst\n"
)
_P2_HEAD = (
    "---\n"
    "phase: P2\n"
    "task_id: T001\n"
    "agent: architect\n"
)
_P1_TAIL = (
    "---\n"
    "#### BDD-1: test\n"
    "- Given x\n"
    "- When y\n"
    "- Then z\n"
)
_P2_TAIL = "---\n# P2 design\n"


def _run_frontmatter(agate_scripts, python_exe, run_cli, file_path):
    """bats `run bash -c "FILE='...' $PYTHON '.../agate-frontmatter-check.py'"` 等价。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-frontmatter-check.py"),
        env={"FILE": str(file_path)},
    )


def _run_frontmatter_wrapper(agate_scripts, python_exe, run_cli, file_path):
    """bats `run "$PYTHON" "$AGATE_SCRIPTS/check-frontmatter.py" "$dir/P2-design.md"` 等价。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "check-frontmatter.py"),
        str(file_path),
    )


@pytest.mark.windows_smoke
def test_cf_1_bdd_2_fullwidth_colon_risk_level_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-1"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level：high\n"
        + "phases: [P1, P2]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "risk_level" in result.output


def test_cf_2_bdd_4_indent_error_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-2"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: high\n"
        + "phases: [P1]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "coupling_checklist:\n"
        + "- api-schema: checked\n"
        + "   - data-model: checked\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert (
        "coupling_checklist" in result.output
        or "line" in result.output
        or "行" in result.output
    )


def test_cf_3_bdd_5_invalid_risk_level_hints_valid_values(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-3"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: HIGH\n"
        + "phases: [P1]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "low" in result.output
    assert "medium" in result.output
    assert "high" in result.output


def test_cf_4_bdd_6_p1_missing_risk_level_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-4"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "phases: [P1]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "risk_level" in result.output


def test_cf_5_bdd_6_p2_missing_candidate_count_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-5"
    d.mkdir()
    (d / "P2-design.md").write_text(
        _P2_HEAD
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "ui_affected: false\n"
        + _P2_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P2-design.md")
    assert result.output != ""
    assert "candidate_count" in result.output


def test_cf_6_bdd_6_find_1_p7_missing_design_gap_count_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-6"
    d.mkdir()
    (d / "P7-consistency.md").write_text(
        "---\n"
        "phase: P7\n"
        "task_id: T001\n"
        "agent: consistency-reviewer\n"
        "blocker_count: 0\n"
        "deviation_count: 0\n"
        "deviation_critical_count: 0\n"
        "---\n"
        "一致性检查完成。\n",
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P7-consistency.md")
    assert result.output != ""
    assert "design_gap_count" in result.output


def test_cf_7_bdd_7_candidate_count_type_error_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-7"
    d.mkdir()
    (d / "P2-design.md").write_text(
        _P2_HEAD
        + "candidate_count: two\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "ui_affected: false\n"
        + _P2_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P2-design.md")
    assert result.output != ""
    assert "candidate_count" in result.output


def test_cf_8_bdd_12_nesting_deeper_than_3_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-8"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: high\n"
        + "phases: [P1]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "coupling_checklist:\n"
        + "  level1:\n"
        + "    level2:\n"
        + "      level3:\n"
        + "        level4: too-deep\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "coupling_checklist" in result.output


def test_cf_9_find_5_single_line_fullwidth_block_not_dict_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-9"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        "---\n风险等级：高\n---\n#### BDD-1: test\n- Given x\n- When y\n- Then z\n",
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "No such file" not in result.output
    assert (
        "映射" in result.output
        or "必须为" in result.output
        or "dict" in result.output
    )


def test_cf_10_bdd_8_wrapper_bad_then_good(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-10"
    d.mkdir()
    bad = d / "P2-design.md"
    bad.write_text(
        _P2_HEAD
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "ui_affected: false\n"
        + _P2_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter_wrapper(agate_scripts, python_exe, run_cli, bad)
    assert result.returncode == 1

    good = d / "P2-design.md"
    good.write_text(
        _P2_HEAD
        + "candidate_count: 2\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "ui_affected: false\n"
        + _P2_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter_wrapper(agate_scripts, python_exe, run_cli, good)
    assert result.returncode == 0


def test_cf_11_bdd_1_change_type_refactor_valid_empty_output(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-11"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: medium\n"
        + "phases: [P1, P2, P3, P4, P5, P6, P7, P8]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "change_type: refactor\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.returncode == 0
    assert result.output == ""


def test_cf_12_bdd_1_change_type_invalid_hints_refactor(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-12"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: medium\n"
        + "phases: [P1, P2]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "change_type: feature\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "change_type" in result.output
    assert "refactor" in result.output


def test_cf_13_bdd_4_regression_pass_type_invalid(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-13"
    d.mkdir()
    (d / "P6-acceptance.md").write_text(
        "---\n"
        "phase: P6\n"
        "task_id: T001\n"
        "agent: verifier\n"
        "pass: 1\n"
        "fail: 0\n"
        "ui_affected: false\n"
        'regression_pass: "yes"\n'
        "---\n"
        "- PASS BDD-1: 全量回归全绿 (P6-evidence/regression.log)\n",
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P6-acceptance.md")
    assert result.output != ""
    assert "regression_pass" in result.output


def test_cf_14_bdd_4_regression_pass_type_valid_empty_output(
    tmp_path, agate_scripts, python_exe, run_cli
):
    d = tmp_path / "cf-14"
    d.mkdir()
    (d / "P6-acceptance.md").write_text(
        "---\n"
        "phase: P6\n"
        "task_id: T001\n"
        "agent: verifier\n"
        "pass: 1\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "regression_pass: true\n"
        "---\n"
        "- PASS BDD-1: 全量回归全绿 (P6-evidence/regression.log)\n",
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P6-acceptance.md")
    assert result.returncode == 0
    assert result.output == ""
