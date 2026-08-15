# tests/unit/test_check_p6_evidence.py — P6 证据链检查（check-p6-evidence.py）
# （check-p6-evidence.bats 30 用例迁移，TAG0011 批次 9a）
# 被测：agate/scripts/check-p6-evidence.py TASK_DIR（exit 0/1/2；P6-acceptance.md 缺失 exit 2）。
# 流语义（P2 BLOCKER-1）：GATE P6-EVIDENCE 消息经 sys.stderr.write → 断言一律用合并流
#   result.output（等价 bats $output），未映射 .stdout。
# Pillow 可选：本批 30 用例全部 Pillow 无关——check-p6-evidence.py 调 agate-image-check.py
#   variance/ahash，缺 Pillow 时 SKIP_NO_PILLOW 走 WARNING 分支（不阻断），exit code 判定
#   不随 Pillow 安装状态变化（与 bats 原文一致，bats 也无 Pillow skip）。
# 随机字节文件用 os.urandom + write_bytes（平台无关，不写字面命中行，BDD-5）。

import base64
import os

import pytest


def _run_evidence(agate_scripts, python_exe, run_cli, td):
    return run_cli(python_exe, str(agate_scripts / "check-p6-evidence.py"), str(td))


def _write_p6(td, text):
    (td / "P6-acceptance.md").write_text(text, encoding="utf-8")


def _write_ui_p2(td, value):
    (td / "P2-design.md").write_text(
        f"---\nagent: test\n---\nui_affected: {value}\n", encoding="utf-8"
    )


@pytest.mark.windows_smoke
def test_e_1_no_p6_file_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    td = tmp_path / "task"
    td.mkdir()
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 2


def test_e_2_no_bdd_entries_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "无 BDD\n")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "无 BDD 条目" in result.output


def test_e_3_pass_missing_file_ref_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1\n")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "缺文件证据引用" in result.output


def test_e_4_pass_with_ref_and_file_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (result.json)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text("log\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_5_evidence_dir_missing_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (result.json)\n")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "P6-evidence" in result.output


def test_e_6_evidence_dir_empty_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (result.json)\n")
    (td / "P6-evidence").mkdir()
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_e_7_normal_pass_no_ui_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (result1.json)\n- PASS BDD-2 (result2.json)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result1.json").write_text("log\n", encoding="utf-8")
    (ev / "result2.json").write_text("log\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_8_ui_true_screenshots_dir_missing_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/login.png)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text("log\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "screenshots" in result.output


def test_e_9_ui_screenshot_lt_1kb_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/login.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "login.png").write_bytes(os.urandom(100))
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "1KB" in result.output


def test_e_10_ui_screenshot_ge_1kb_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/login.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "login.png").write_bytes(os.urandom(5000))
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_11_multiple_extensions_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1 (result.log)\n"
        "- PASS BDD-2 (data.json)\n"
        "- PASS BDD-3 (page.html)\n"
        "- PASS BDD-4 (notes.txt)\n"
        "- PASS BDD-5 (config.yaml)\n",
    )
    ev = td / "P6-evidence"
    ev.mkdir()
    for ext in ("log", "json", "html", "txt", "yaml"):
        (ev / ("file." + ext)).write_text("content\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_12_ui_duplicate_screenshots_md5_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/login.png)\n- PASS BDD-2 (screenshots/dashboard.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    content = base64.b64encode(os.urandom(5000)).decode("ascii")
    (shots / "login.png").write_text(content, encoding="utf-8")
    (shots / "dashboard.png").write_text(content, encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "md5" in result.output or "重复" in result.output


def test_e_14_pass_ref_with_extra_content_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (result.png, vision: OK)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.png").write_text("log\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_1_pdf_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1 (report.pdf)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "report.pdf").write_text("pdf content\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_2_jpeg_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1 (photo.jpeg)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "photo.jpeg").write_text("jpeg content\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_3_comma_separated_refs_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1: works (screenshots/a.png, screenshots/b.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "a.png").write_text("a\n", encoding="utf-8")
    (shots / "b.png").write_text("b\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_4_nested_parens_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1: works (screenshots/b07.png — element: .katex nth(1))\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "b07.png").write_text("img\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_5_version_parens_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1: upgraded (v2.0)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text("some evidence\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evid_ext_6_no_path_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "---\nagent: test\n---\n- PASS BDD-1: works (no reference here)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text("some evidence\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "缺文件证据引用" in result.output


def test_evid_ext_7_existing_extensions_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "---\nagent: test\n---\n"
        "- PASS BDD-1 (result.png)\n"
        "- PASS BDD-2 (photo.jpg)\n"
        "- PASS BDD-3 (output.log)\n"
        "- PASS BDD-4 (data.json)\n"
        "- PASS BDD-5 (page.html)\n"
        "- PASS BDD-6 (notes.txt)\n"
        "- PASS BDD-7 (config.yaml)\n"
        "- PASS BDD-8 (config2.yml)\n",
    )
    ev = td / "P6-evidence"
    ev.mkdir()
    for f in (
        "result.png", "photo.jpg", "output.log", "data.json",
        "page.html", "notes.txt", "config.yaml", "config2.yml",
    ):
        (ev / f).write_text("content\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_13_ui_different_screenshots_exit_0(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/login.png)\n- PASS BDD-2 (screenshots/dashboard.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "login.png").write_bytes(os.urandom(5000))
    (shots / "dashboard.png").write_bytes(os.urandom(5000))
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_evidence_no_ref_detail_1_has_specific_pass_lines(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1\n- PASS BDD-2 (result.json)\n- PASS BDD-3\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text("log\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "  - - PASS BDD-1" in result.output
    assert "  - - PASS BDD-3" in result.output


def test_evidence_empty_detail_1_has_basename(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/tiny.txt)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "tiny.txt").write_bytes(os.urandom(100))
    (td / "P6-evidence" / "real.json").write_text('{"ok":true}\n', encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "  - tiny.txt" in result.output


def test_evidence_md5_detail_1_has_basenames(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (screenshots/a.png)\n- PASS BDD-2 (screenshots/b.png)\n")
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    content = base64.b64encode(os.urandom(5000)).decode("ascii")
    (shots / "a.png").write_text(content, encoding="utf-8")
    (shots / "b.png").write_text(content, encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "  - a.png" in result.output
    assert "  - b.png" in result.output


def test_evidence_md5_detail_2_spaces_in_name(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(
        td,
        "- PASS BDD-1 (screenshots/login page.png)\n"
        "- PASS BDD-2 (screenshots/dashboard view.png)\n",
    )
    shots = td / "P6-evidence" / "screenshots"
    shots.mkdir(parents=True)
    content = base64.b64encode(os.urandom(5000)).decode("ascii")
    (shots / "login page.png").write_text(content, encoding="utf-8")
    (shots / "dashboard view.png").write_text(content, encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "  - login page.png" in result.output
    assert "  - dashboard view.png" in result.output


def test_e_15_ui_true_all_text_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (analysis.md)\n- PASS BDD-2 (notes.txt)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "analysis.md").write_text("source code analysis\n", encoding="utf-8")
    (ev / "notes.txt").write_text("manual notes\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "全是纯文本" in result.output


def test_e_16_ui_true_has_json_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_ui_p2(td, "true")
    _write_p6(td, "- PASS BDD-1 (result.json)\n- PASS BDD-2 (notes.txt)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "result.json").write_text('{"status":"pass"}\n', encoding="utf-8")
    (ev / "notes.txt").write_text("supplementary notes\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_e_17_ui_false_all_text_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_ui_p2(td, "false")
    _write_p6(td, "- PASS BDD-1 (analysis.md)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "analysis.md").write_text("text analysis\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_9_chinese_filename_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (截图 验证通过.png)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "截图 验证通过.png").write_text("img\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_10_no_extension_still_blocked_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "- PASS BDD-1 (见截图)\n")
    ev = td / "P6-evidence"
    ev.mkdir()
    (ev / "截图.png").write_text("img\n", encoding="utf-8")
    result = _run_evidence(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
    assert "缺文件证据引用" in result.output
