# tests/unit/test_check_p6_format.py — P6-acceptance.md 格式校验（--check / --fix）
# （check-p6-format.bats 16 用例迁移，TAG0011 批次 7）
# 被测：agate/scripts/check-p6-format.py（[--check|--fix] FILE；exit 0/1；
#   --fix 归一化小写 PASS/FAIL + 全角冒号总结行 → **Summary**: PASS: N）。
# 失败消息（--check 有偏差）经 sys.stderr.write → 按 P2 §3.2 先判流归属，断言一律用
#   合并流 result.output（等价 bats $output，BLOCKER-1）。文件回写断言直接 read_text。
# F_P6FMFIX.1/2 的 yaml 校验（bats 内联 `$PYTHON -c`）→ 测试内 import yaml 等价断言。
# create_python_shim_bin 退役（P2 §3.1）：pytest 直跑解释器，无需 harness shim。

import pytest
import yaml


def _run_p6(agate_scripts, python_exe, run_cli, mode, p6_file, env=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-p6-format.py"),
        mode,
        str(p6_file),
        env=env,
    )


def _write_p6(td, text):
    (td / "P6-acceptance.md").write_text(text, encoding="utf-8")


@pytest.mark.windows_smoke
def test_f1_check_clean_file_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- PASS BDD-2: confirmed (evidence/result.json)\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--check", td / "P6-acceptance.md")
    assert result.returncode == 0


def test_f2_check_lowercase_pass_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- pass BDD-1: verified (evidence/log.json)\n")

    result = _run_p6(agate_scripts, python_exe, run_cli, "--check", td / "P6-acceptance.md")
    assert result.returncode == 1


def test_f3_fix_lowercase_pass_auto_fix(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- pass BDD-1: verified (evidence/log.json)\n")

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0
    assert "- PASS BDD-1" in (td / "P6-acceptance.md").read_text(encoding="utf-8")


def test_f5_check_no_p6_file_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()

    result = _run_p6(agate_scripts, python_exe, run_cli, "--check", td / "P6-acceptance.md")
    assert result.returncode == 0


def test_f_bdd17_1_line_start_pass_fail_bdd_format_valid(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/a.json)\n"
        "- FAIL BDD-2: broken (evidence/b.json)\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--check", td / "P6-acceptance.md")
    assert result.returncode == 0
    content = (td / "P6-acceptance.md").read_text(encoding="utf-8")
    assert "- PASS BDD-1:" in content
    assert "- FAIL BDD-2:" in content


def test_f8_check_lowercase_fail_colon_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    td = task_dir()
    _write_p6(td, "- fail: BDD-2 broken\n")

    result = _run_p6(agate_scripts, python_exe, run_cli, "--check", td / "P6-acceptance.md")
    assert result.returncode == 1


def test_f9_fix_lowercase_fail_with_space_auto_fix(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "- fail BDD-3: timeout\n")

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0
    assert "- FAIL BDD-3" in (td / "P6-acceptance.md").read_text(encoding="utf-8")


def test_f10_fix_failure_not_matched_word_boundary(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(td, "- failure mode detected in production\n")

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0
    assert "failure mode" in (td / "P6-acceptance.md").read_text(encoding="utf-8")


def test_f_bdd18_1_summary_line_not_counted_as_item(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1\n"
        "- PASS: 16\n"
        "- FAIL: 0\n",
    )

    result = run_cli(
        python_exe,
        str(agate_scripts / "check-gate.py"),
        "P6",
        str(td),
    )
    assert result.returncode == 1
    assert "P6-evidence" in result.output


def test_f12_fix_summary_fullwidth_colon_normalized(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- PASS：34\n"
        "- FAIL：0\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0
    content = (td / "P6-acceptance.md").read_text(encoding="utf-8")
    assert "**Summary**: PASS: 34" in content
    assert "**Summary**: FAIL: 0" in content
    assert "- PASS：34" not in content


def test_f13_fix_summary_posix_locale_normalized(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- PASS：34\n"
        "- FAIL：0\n",
    )

    result = _run_p6(
        agate_scripts,
        python_exe,
        run_cli,
        "--fix",
        td / "P6-acceptance.md",
        env={"LC_ALL": "POSIX", "LANG": ""},
    )
    assert result.returncode == 0
    content = (td / "P6-acceptance.md").read_text(encoding="utf-8")
    assert "**Summary**: PASS: 34" in content
    assert "**Summary**: FAIL: 0" in content
    assert "- PASS：34" not in content


def test_f_p6fmfix_1_frontmatter_pass_fail_not_touched(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "---\n"
        "phase: P6\n"
        "task_id: T001\n"
        "pass: 28\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "---\n"
        "\n"
        "- PASS BDD-1: xxx (x.log)\n"
        "- pass BDD-2: yyy (y.log)\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0

    content = (td / "P6-acceptance.md").read_text(encoding="utf-8")
    assert "pass: 28" in content
    assert "fail: 0" in content
    assert "**Summary**: PASS: 28" not in content
    assert "**Summary**: FAIL: 0" not in content

    assert content.startswith("---\n")
    end = content.find("\n---", 4)
    assert end > 0
    data = yaml.safe_load(content[4:end])
    assert data["pass"] == 28
    assert data["fail"] == 0

    assert "- PASS BDD-2" in content


def test_f_p6fmfix_2_frontmatter_summary_still_normalized(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "---\n"
        "phase: P6\n"
        "task_id: T001\n"
        "pass: 2\n"
        "fail: 0\n"
        "ui_affected: false\n"
        "---\n"
        "\n"
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- PASS：2\n"
        "- FAIL：0\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0

    content = (td / "P6-acceptance.md").read_text(encoding="utf-8")
    end = content.find("\n---", 4)
    data = yaml.safe_load(content[4:end])
    assert data["pass"] == 2 and data["fail"] == 0

    assert "**Summary**: PASS: 2" in content
    assert "**Summary**: FAIL: 0" in content


def test_f_p6fmfix_3_no_frontmatter_close_treated_as_body(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "---\n"
        "phase: P6\n"
        "- pass BDD-1: verified (evidence/log.json)\n",
    )

    result = _run_p6(agate_scripts, python_exe, run_cli, "--fix", td / "P6-acceptance.md")
    assert result.returncode == 0
    assert "- PASS BDD-1" in (td / "P6-acceptance.md").read_text(encoding="utf-8")


def test_bdd_12_fix_lowercase_fail_fullwidth_posix_locale(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- fail：3\n",
    )

    result = _run_p6(
        agate_scripts,
        python_exe,
        run_cli,
        "--fix",
        td / "P6-acceptance.md",
        env={"LC_ALL": "POSIX", "LANG": ""},
    )
    assert result.returncode == 0
    assert "**Summary**: FAIL: 3" in (td / "P6-acceptance.md").read_text(encoding="utf-8")


def test_bdd_13_fix_and_check_halfwidth_posix_locale(
    task_dir, agate_scripts, python_exe, run_cli
):
    td = task_dir()
    _write_p6(
        td,
        "- PASS BDD-1: verified (evidence/log.json)\n"
        "- FAIL: 3\n",
    )

    result = _run_p6(
        agate_scripts,
        python_exe,
        run_cli,
        "--fix",
        td / "P6-acceptance.md",
        env={"LC_ALL": "POSIX", "LANG": ""},
    )
    assert result.returncode == 0
    assert "**Summary**: FAIL: 3" in (td / "P6-acceptance.md").read_text(encoding="utf-8")

    result = _run_p6(
        agate_scripts,
        python_exe,
        run_cli,
        "--check",
        td / "P6-acceptance.md",
        env={"LC_ALL": "POSIX", "LANG": ""},
    )
    assert result.returncode == 0
