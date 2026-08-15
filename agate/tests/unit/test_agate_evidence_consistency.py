# tests/unit/test_agate_evidence_consistency.py — evidence JSON 与 P6 一致性
# （agate-evidence-consistency.bats 2 用例迁移，TAG0011 批次 1）
# 被测：agate/scripts/agate-evidence-consistency.py（EVIDENCE_DIR / P6_FILE env 输入）
# 流语义：EC.2 空断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import json

import pytest


def _run_ec(agate_scripts, python_exe, run_cli, evidence_dir, p6_file):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-evidence-consistency.py"),
        env={"EVIDENCE_DIR": str(evidence_dir), "P6_FILE": str(p6_file)},
    )


def _write_evidence(tmp_path, bdd_status):
    evidence_dir = tmp_path / "P6-evidence"
    evidence_dir.mkdir()
    p6_file = tmp_path / "P6-acceptance.md"
    p6_file.write_text("- PASS BDD-1 (result.json)\n", encoding="utf-8")
    (evidence_dir / "result.json").write_text(
        json.dumps({"bdd_results": [{"id": "BDD-1", "status": bdd_status}]}),
        encoding="utf-8",
    )
    return evidence_dir, p6_file


@pytest.mark.windows_smoke
def test_ec_1_pass_but_evidence_fail_reports_inconsistent(
    agate_scripts, python_exe, run_cli, tmp_path
):
    evidence_dir, p6_file = _write_evidence(tmp_path, "fail")
    result = _run_ec(agate_scripts, python_exe, run_cli, evidence_dir, p6_file)
    assert result.returncode == 0
    assert "BDD-1" in result.output


def test_ec_2_no_inconsistency_is_empty(agate_scripts, python_exe, run_cli, tmp_path):
    evidence_dir, p6_file = _write_evidence(tmp_path, "pass")
    result = _run_ec(agate_scripts, python_exe, run_cli, evidence_dir, p6_file)
    assert result.returncode == 0
    assert result.output == ""
