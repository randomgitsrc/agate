# tests/unit/test_agate_extract_context.py — agate-extract-context.py 上下文摘要校验
# （agate-extract-context.bats 16 用例迁移，TAG0011 批次 4）
# 被测：agate/scripts/agate-extract-context.py（PHASE TASK_DIR [--write] 上下文摘要提取）
# 流语义：exit 1/2 用法/错误走 stderr，成功内容走 stdout——断言一律基于合并流 .output
#        （bats $output = stdout + stderr，P2 BLOCKER-1）
# 平台：EC.16 用 fakebin 前置 PATH 模拟"无 bc"环境（Windows 无此工具，P3 §5.2 表 W 打标）

import os

import pytest


def _run(agate_scripts, python_exe, run_cli, *args, env=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-extract-context.py"),
        *args,
        env=env,
    )


@pytest.mark.windows_smoke
def test_ec_1_rejects_missing_arguments(agate_scripts, python_exe, run_cli):
    result = _run(agate_scripts, python_exe, run_cli)
    assert result.returncode == 1


def test_ec_2_rejects_invalid_phase(agate_scripts, python_exe, run_cli, tmp_path):
    result = _run(agate_scripts, python_exe, run_cli, "P9", str(tmp_path))
    assert result.returncode == 2


def test_ec_3_rejects_nonexistent_task_dir(agate_scripts, python_exe, run_cli):
    result = _run(agate_scripts, python_exe, run_cli, "P1", "/nonexistent")
    assert result.returncode == 2


def test_ec_4_p1_extracts_p0_brief_fields(agate_scripts, python_exe, run_cli, tmp_path):
    (tmp_path / "P0-brief.md").write_text(
        "---\ntask: fix login timeout\nknown_risks: [session_expiry]\n---\n",
        encoding="utf-8",
    )
    result = _run(agate_scripts, python_exe, run_cli, "P1", str(tmp_path))
    assert result.returncode == 0
    assert "task: fix login timeout" in result.output


def test_ec_5_p2_extracts_p1_domains_and_bdd_count(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P1-requirements.md").write_text(
        "---\ndomains: [backend]\nrisk_level: high\n---\n"
        "#### BDD-1: user can log in\n"
        "#### BDD-2: session expires after timeout\n",
        encoding="utf-8",
    )
    result = _run(agate_scripts, python_exe, run_cli, "P2", str(tmp_path))
    assert result.returncode == 0
    assert "domains: [backend]" in result.output
    assert "risk_level: high" in result.output
    assert "BDD 条件数: 2" in result.output


def test_ec_6_p3_extracts_p2_structured_fields(agate_scripts, python_exe, run_cli, tmp_path):
    (tmp_path / "P2-design.md").write_text(
        "packages: [pkg-a, pkg-b]\n"
        "domains: [backend, frontend]\n"
        "ui_affected: true\n"
        "gate_commands:\n"
        '  P5: "pytest -q"\n',
        encoding="utf-8",
    )
    result = _run(agate_scripts, python_exe, run_cli, "P3", str(tmp_path))
    assert result.returncode == 0
    assert "packages: [pkg-a, pkg-b]" in result.output
    assert "ui_affected: true" in result.output


def test_ec_7_p6_extracts_bdd_id_list_and_failed_reference(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P1-requirements.md").write_text(
        "#### BDD-1: feature works\n#### BDD-2: edge case handled\n",
        encoding="utf-8",
    )
    (tmp_path / "P5-test-results").mkdir()
    (tmp_path / "P5-test-results" / "unit.md").write_text("  failed: 1\n", encoding="utf-8")
    result = _run(agate_scripts, python_exe, run_cli, "P6", str(tmp_path))
    assert result.returncode == 0
    assert "- BDD-1" in result.output
    assert "- BDD-2" in result.output
    assert "P5 failed 参考: 1" in result.output


def test_ec_8_p7_extracts_pass_fail_counts(agate_scripts, python_exe, run_cli, tmp_path):
    (tmp_path / "P2-design.md").write_text("packages: [pkg-a]\n", encoding="utf-8")
    (tmp_path / "P6-acceptance.md").write_text(
        "- PASS BDD-1: works (evidence.log)\n- FAIL BDD-2: broken (evidence2.log)\n",
        encoding="utf-8",
    )
    result = _run(agate_scripts, python_exe, run_cli, "P7", str(tmp_path))
    assert result.returncode == 0
    assert "1 PASS" in result.output
    assert "1 FAIL" in result.output


def test_ec_9_write_mode_appends_to_dispatch_context_file(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P0-brief.md").write_text("---\ntask: test task\n---\n", encoding="utf-8")
    (tmp_path / "P1-dispatch-context-analyst.md").write_text(
        "### 上游关联\n(none)\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P1", str(tmp_path), "--write")
    assert result.returncode == 0
    assert "已追加到" in result.output
    text = (tmp_path / "P1-dispatch-context-analyst.md").read_text(encoding="utf-8")
    assert "task: test task" in text


def test_ec_10_p4_extracts_p2_fields_and_p3_bdd_count(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P2-design.md").write_text(
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands:\n"
        '  P5: "pytest -q"\n'
        "files_to_read: [src/main.py]\n",
        encoding="utf-8",
    )
    (tmp_path / "P3-test-cases.md").write_text(
        "#### BDD-1: works\n#### BDD-2: edge case\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P4", str(tmp_path))
    assert result.returncode == 0
    assert "packages: [pkg-a]" in result.output
    assert "files_to_read: [src/main.py]" in result.output
    assert "P3 BDD 测试覆盖数: 2" in result.output


def test_ec_11_p5_extracts_gate_commands_and_implementation_dir(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P2-design.md").write_text(
        "gate_commands:\n" '  P5: "pytest -q"\n', encoding="utf-8"
    )
    (tmp_path / "P4-implementation.md").write_text(
        "implementation_dir: src/\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P5", str(tmp_path))
    assert result.returncode == 0
    assert "gate_commands" in result.output
    assert "implementation_dir: src/" in result.output


def test_ec_12_p8_extracts_packages_and_blocker_deviation(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P2-design.md").write_text("packages: [pkg-a, pkg-b]\n", encoding="utf-8")
    (tmp_path / "P7-consistency.md").write_text(
        "[BLOCKER] API mismatch\n[DEVIATION] minor naming difference\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P8", str(tmp_path))
    assert result.returncode == 0
    assert "packages: [pkg-a, pkg-b]" in result.output
    assert "BLOCKER 数: 1" in result.output
    assert "DEVIATION" in result.output


def test_ec_13_gate_diagnosis_reference_auto_appended(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P0-brief.md").write_text("task: test\n", encoding="utf-8")
    (tmp_path / "P1-gate-diagnosis.md").write_text(
        "gate failed because...\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P1", str(tmp_path))
    assert result.returncode == 0
    assert "gate-diagnosis 引用" in result.output
    assert "P1-gate-diagnosis.md" in result.output


def test_ec_14_p5_extracts_implementation_dir_from_package_subdirs(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P2-design.md").write_text(
        "gate_commands:\n" '  P5: "pytest -q"\n', encoding="utf-8"
    )
    (tmp_path / "P4-implementation" / "pkg-a").mkdir(parents=True)
    (tmp_path / "P4-implementation" / "pkg-b").mkdir(parents=True)
    (tmp_path / "P4-implementation" / "pkg-a" / "notes.md").write_text(
        "implementation_dir: pkg-a/src\n", encoding="utf-8"
    )
    (tmp_path / "P4-implementation" / "pkg-b" / "notes.md").write_text(
        "implementation_dir: pkg-b/lib\n", encoding="utf-8"
    )
    result = _run(agate_scripts, python_exe, run_cli, "P5", str(tmp_path))
    assert result.returncode == 0
    assert "implementation_dir: pkg-a/src" in result.output
    assert "implementation_dir: pkg-b/lib" in result.output


def test_ec_15_p6_extracts_failed_count_from_package_subdirs(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P1-requirements.md").write_text("#### BDD-1: feature works\n", encoding="utf-8")
    (tmp_path / "P5-test-results" / "pkg-a").mkdir(parents=True)
    (tmp_path / "P5-test-results" / "pkg-b").mkdir(parents=True)
    (tmp_path / "P5-test-results" / "pkg-a" / "unit.md").write_text("  failed: 2\n", encoding="utf-8")
    (tmp_path / "P5-test-results" / "pkg-b" / "unit.md").write_text("  failed: 1\n", encoding="utf-8")
    result = _run(agate_scripts, python_exe, run_cli, "P6", str(tmp_path))
    assert result.returncode == 0
    assert "P5 failed 参考: 3" in result.output


@pytest.mark.windows_smoke
def test_ec_16_p6_failed_sum_without_bc_simulation(
    agate_scripts, python_exe, run_cli, tmp_path
):
    (tmp_path / "P1-requirements.md").write_text("#### BDD-1: feature works\n", encoding="utf-8")
    (tmp_path / "P5-test-results" / "pkg-a").mkdir(parents=True)
    (tmp_path / "P5-test-results" / "pkg-b").mkdir(parents=True)
    (tmp_path / "P5-test-results" / "pkg-a" / "unit.md").write_text("  failed: 2\n", encoding="utf-8")
    (tmp_path / "P5-test-results" / "pkg-b" / "unit.md").write_text("  failed: 1\n", encoding="utf-8")
    fakebin = tmp_path / "fakebin-nobc"
    fakebin.mkdir()
    bc_stub = fakebin / "bc"
    bc_stub.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
    os.chmod(str(bc_stub), 0o755)
    env = {"PATH": str(fakebin) + os.pathsep + os.environ.get("PATH", "")}
    result = _run(agate_scripts, python_exe, run_cli, "P6", str(tmp_path), env=env)
    assert result.returncode == 0
    assert "P5 failed 参考: 3" in result.output
