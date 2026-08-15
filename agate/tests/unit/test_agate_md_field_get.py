# tests/unit/test_agate_md_field_get.py — MD 字段提取共享工具
# （agate-md-field-get.bats 14 用例迁移，TAG0011 批次 2）
# 被测：agate/scripts/agate-md-field-get.py（FILE env 指向 md 文件，op 取字段名）
# 语义：frontmatter 优先 + 无 key 正则回退（T001 v2.0 流 A）；change_type / regression_pass
#       为 frontmatter-only（TAG0002）。空/精确等值断言统一 .strip()（bats $output 剥尾部换行）。

import json

import pytest


def _run_mdf(agate_scripts, python_exe, run_cli, op, md_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-md-field-get.py"),
        op,
        env={"FILE": str(md_file)},
    )


@pytest.mark.windows_smoke
def test_mdf_1_risk_level_from_frontmatter(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text("---\nagent: test\nrisk_level: high\n---\nbody\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "risk_level", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "high"


def test_mdf_2_old_format_body_regex_fallback(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text("---\nagent: test\n---\nrisk_level: medium\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "risk_level", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "medium"


def test_mdf_3_frontmatter_quoted_string_wins_over_body(
    agate_scripts, python_exe, run_cli, tmp_path
):
    md_file = tmp_path / "P1.md"
    md_file.write_text('---\nagent: test\nrisk_level: "high"\n---\nrisk_level: low\n', encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "risk_level", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "high"


def test_mdf_4_phases_block_list_space_joined(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text("---\nagent: test\nphases:\n  - P1\n  - P2\n---\nbody\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "phases", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "P1 P2"


def test_mdf_5_candidate_count_int_to_str(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P2.md"
    md_file.write_text("---\nagent: test\ncandidate_count: 2\n---\nbody\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "candidate_count", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "2"


def test_mdf_6_packages_list_space_joined(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P2.md"
    md_file.write_text("---\nagent: test\npackages: [agate, other-pkg]\n---\nbody\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "packages", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "agate other-pkg"


def test_mdf_7_change_type_frontmatter(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text(
        "---\nagent: test\nrisk_level: high\nchange_type: refactor\n---\nbody\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "change_type", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "refactor"


def test_mdf_8_change_type_frontmatter_only_no_fallback(
    agate_scripts, python_exe, run_cli, tmp_path
):
    md_file = tmp_path / "P1.md"
    md_file.write_text("---\nagent: test\n---\nchange_type: refactor\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "change_type", md_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_mdf_9_regression_pass_frontmatter_true(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P6.md"
    md_file.write_text(
        "---\nagent: test\npass: 1\nfail: 0\nui_affected: false\nregression_pass: true\n---\nbody\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "regression_pass", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "true"


def test_mdf_10_regression_pass_no_fallback_empty(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P6.md"
    md_file.write_text(
        "---\nagent: test\npass: 1\nfail: 0\nui_affected: false\n---\nregression_pass: false\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "regression_pass", md_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_mdf_11_change_type_prose_mention_empty(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text(
        "---\nagent: test\n---\nchange_type: refactor 是可选字段，缺省为功能任务\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "change_type", md_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_mdf_12_change_type_negated_mention_empty(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text(
        "---\nagent: test\n---\n本任务不涉及 change_type: refactor 机制\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "change_type", md_file)
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_bdd_6_chinese_content_reads_field(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text(
        "---\nagent: test\nrisk_level: high\ntask: 中文任务名验证\n---\n正文含中文\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "risk_level", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "high"


def test_bdd_15_lf_ascii_behavior_unchanged(agate_scripts, python_exe, run_cli, tmp_path):
    md_file = tmp_path / "P1.md"
    md_file.write_text("---\nagent: test\nrisk_level: medium\n---\nbody\n", encoding="utf-8")
    result = _run_mdf(agate_scripts, python_exe, run_cli, "risk_level", md_file)
    assert result.returncode == 0
    assert result.output.strip() == "medium"


# ===== TAG0014 dispatch_plan op 契约（S2，P1 BDD-1/7；plan N9） =====
# 现状红灯基础：dispatch_plan 未注册 KNOWN_OPS → exit 2 "unknown op"；dict 值走 str() repr 非 JSON。

def test_mdf_16_dispatch_plan_frontmatter_json(agate_scripts, python_exe, run_cli, tmp_path):
    """BDD-1 op 层：dispatch_plan 对含 flow YAML 的 P2 文件输出合法 JSON（含 mode）。"""
    md_file = tmp_path / "P2.md"
    md_file.write_text(
        "---\nagent: test\n"
        "dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}]}\n"
        "---\nbody\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "dispatch_plan", md_file)
    assert result.returncode == 0
    plan = json.loads(result.output.strip())
    assert plan["mode"] == "static-batch"
    assert plan["parallel_limit"] == 3


def test_mdf_17_dispatch_plan_dict_json_output(agate_scripts, python_exe, run_cli, tmp_path):
    """BDD-1/7 op 层（I4）：dict → json.dumps 输出合法 JSON（非 Python repr 单引号）。"""
    md_file = tmp_path / "P2.md"
    md_file.write_text(
        "---\nagent: test\n"
        "dispatch_plan: {mode: single}\n"
        "---\nbody\n",
        encoding="utf-8",
    )
    result = _run_mdf(agate_scripts, python_exe, run_cli, "dispatch_plan", md_file)
    assert result.returncode == 0
    output = result.output.strip()
    plan = json.loads(output)
    assert isinstance(plan, dict)
    assert plan["mode"] == "single"
    assert "'" not in output
