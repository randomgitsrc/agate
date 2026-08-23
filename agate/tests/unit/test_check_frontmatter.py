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


def test_cf_15_bdd_6_ceremony_invalid_enum_rejected(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-6 写侧（TAG0019 C3）：ceremony: light（非 thin/standard/full）→ 非法值拦截 exit 1。"""
    d = tmp_path / "cf-15"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: medium\n"
        + "phases: [P1, P2]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "ceremony: light\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter_wrapper(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.returncode == 1
    assert "ceremony" in result.output


# ========== TAG0023 RM-AG0045（BDD-12~13）：错误消息修复提示增强 + 历史用例写时回归 ==========
# BDD-12 被测：agate-frontmatter-check.py `_check()` 每类 errors.append 消息（P2-design.md
#   §1.1 改动表）需追加修复提示关键词，当前实现只报"缺必填字段 X" / "非法值 X（合法值: ...）"，
#   无"补"/"改用"等具体指引动词——这正是本批红灯的来源。
# BDD-13 被测：TAG0019 实际触发过 commit 时格式折返的两类声明用例（coupling_checklist
#   非列表声明 / FIND-5 全角冒号非 dict）在 agate-frontmatter-check.py 现状代码下已能
#   写时（Write 后即跑，不依赖 git 状态）拦截——这两类检测能力已存在（P2-design.md §2.4
#   候选 A 选择理由），本用例作为回归防呆锚点，当前可能已是绿灯（详见 P3-test-cases.md
#   BDD-13 说明），第三类"源码数 6>5"锚点见 test_check_routing.py。


def test_bdd_12_missing_required_field_error_includes_fix_hint(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-12：缺必填字段错误消息须含修复提示关键词"补"（当前只报"缺必填字段 X"，无动词）。"""
    d = tmp_path / "bdd12-1"
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
    assert "risk_level" in result.output
    assert "补" in result.output


def test_bdd_12_invalid_enum_error_includes_fix_hint(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-12：非法枚举值错误消息须含修复提示关键词"改用"（当前只报"非法值 X（合法值:...)"）。"""
    d = tmp_path / "bdd12-2"
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
    assert "risk_level" in result.output
    assert "改用" in result.output


def test_bdd_13_historical_coupling_checklist_non_list_write_time_caught(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-13 回归用例①（TAG0019 实证）：coupling_checklist 写成逗号分隔字符串而非
    flow-list，写时即被 agate-frontmatter-check.py 类型校验拦截（非新增能力，回归防呆）。"""
    d = tmp_path / "bdd13-1"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        _P1_HEAD
        + "risk_level: high\n"
        + "phases: [P1]\n"
        + "packages: [agate]\n"
        + "domains: [backend]\n"
        + "coupling_checklist: api-schema checked, data-model checked\n"
        + _P1_TAIL,
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "coupling_checklist" in result.output


def test_bdd_13_historical_fullwidth_colon_write_time_caught(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-13 回归用例②（TAG0019 实证，FIND-5）：半角冒号误写为全角冒号导致 frontmatter
    整块被解析为非 dict 标量，写时即被拦截（非新增能力，回归防呆）。"""
    d = tmp_path / "bdd13-2"
    d.mkdir()
    (d / "P1-requirements.md").write_text(
        "---\nrisk_level：high\n---\n#### BDD-1: test\n- Given x\n- When y\n- Then z\n",
        encoding="utf-8",
    )

    result = _run_frontmatter(agate_scripts, python_exe, run_cli, d / "P1-requirements.md")
    assert result.output != ""
    assert "映射" in result.output or "必须为" in result.output or "dict" in result.output
