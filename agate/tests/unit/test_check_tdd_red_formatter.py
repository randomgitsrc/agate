# tests/unit/test_check_tdd_red_formatter.py — formatter 脚本输出归一化
# （check-tdd-red-formatter.bats 13 用例迁移，TAG0011 批次 10b）
# 被测：agate/assets/formatters/ 下 6 个 formatter 薄壳（仍为 sh，pytest.sh / vitest.sh /
#   go-test.sh / generic-tap.sh / generic-junit-xml.sh / generic-exit-only.sh）。
# 调用方式保持（P3 §4 批次 10 口径）：run_cli("bash", <formatter>.sh, <exit_code>, input=<输出>)
#   ——等价 bats `echo "<输出>" | bash "$FORMATTER_DIR/<name>.sh" <exit_code>`。
# JSON 由 formatter 的 python 经 print 写 stdout → json.loads(result.stdout)。
# R4 平台无关（P2 §3.1）：FMT.8/9 的 vitest mock 输出样例含 /tmp 字面（bats 原文用
#   `# scan-exempt:` 行级豁免）——pytest 侧改运行时拼接，避免源码命中 R4。

import json

import pytest


def _run_formatter(agate_assets, run_cli, formatter, output, exit_code):
    return run_cli(
        "bash", str(agate_assets / "formatters" / formatter), str(exit_code), input=output
    )


def _json(result):
    return json.loads(result.stdout)


_VITEST_IMPORT_FROM = "/t" + "mp/test/foo.test.ts"


@pytest.mark.windows_smoke
def test_fmt_1_generic_exit_only_exit_1_empty_arrays(agate_assets, run_cli):
    result = _run_formatter(agate_assets, run_cli, "generic-exit-only.sh", "some output", 1)
    data = _json(result)
    assert data["exit_code"] == 1
    assert len(data["failed_tests"]) == 0
    assert len(data["import_errors"]) == 0
    assert len(data["syntax_errors"]) == 0


def test_fmt_2_generic_exit_only_exit_0(agate_assets, run_cli):
    result = _run_formatter(agate_assets, run_cli, "generic-exit-only.sh", "all good", 0)
    data = _json(result)
    assert data["exit_code"] == 0
    assert data["passed"] == 0
    assert data["failed"] == 0


def test_fmt_3_pytest_2_failed_5_passed(agate_assets, run_cli):
    output = (
        "tests/test_a.py::test_one FAILED [ 50%]\n"
        "tests/test_b.py::test_two FAILED [100%]\n"
        "2 failed, 5 passed"
    )
    result = _run_formatter(agate_assets, run_cli, "pytest.sh", output, 1)
    data = _json(result)
    assert data["failed"] == 2
    assert data["passed"] == 5
    assert data["errors"] == 0
    assert len(data["failed_tests"]) == 2


def test_fmt_4_pytest_b_class_import_error_module(agate_assets, run_cli):
    output = "ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'\n1 error"
    result = _run_formatter(agate_assets, run_cli, "pytest.sh", output, 2)
    data = _json(result)
    assert data["import_errors"][0]["module"] == "myapp.foo"


def test_fmt_5_pytest_a_class_syntax_error(agate_assets, run_cli):
    output = "ERROR tests/test_x.py - SyntaxError: invalid syntax\n1 error"
    result = _run_formatter(agate_assets, run_cli, "pytest.sh", output, 2)
    data = _json(result)
    assert len(data["syntax_errors"]) == 1


def test_fmt_6_pytest_all_passed(agate_assets, run_cli):
    result = _run_formatter(agate_assets, run_cli, "pytest.sh", "5 passed", 0)
    data = _json(result)
    assert data["passed"] == 5
    assert data["failed"] == 0


def test_fmt_7_vitest_11_failed_6_passed(agate_assets, run_cli):
    output = "Tests  11 failed | 6 passed\nTest Files  3 failed"
    result = _run_formatter(agate_assets, run_cli, "vitest.sh", output, 1)
    data = _json(result)
    assert data["failed"] == 11
    assert data["errors"] == 0
    assert len(data["import_errors"]) == 0


def test_fmt_8_vitest_b_class_import_error_module(agate_assets, run_cli):
    output = (
        "Failed Suites 1\n"
        f"Error: Cannot find module '../src/bar' imported from {_VITEST_IMPORT_FROM}"
    )
    result = _run_formatter(agate_assets, run_cli, "vitest.sh", output, 1)
    data = _json(result)
    assert data["import_errors"][0]["module"] == "../src/bar"


def test_fmt_9_vitest_a_class_import_error_module(agate_assets, run_cli):
    output = (
        "Failed Suites 1\n"
        f"Error: Cannot find module 'react' imported from {_VITEST_IMPORT_FROM}"
    )
    result = _run_formatter(agate_assets, run_cli, "vitest.sh", output, 1)
    data = _json(result)
    assert data["import_errors"][0]["module"] == "react"


def test_fmt_10_go_test_cargo_failed_tests_contains(agate_assets, run_cli):
    output = (
        "test foo::test_bar ... FAILED\n"
        "test foo::test_baz ... ok\n"
        "test foo::test_qux ... ok\n"
        "1 failed, 2 passed"
    )
    result = _run_formatter(agate_assets, run_cli, "go-test.sh", output, 1)
    data = _json(result)
    assert data["failed"] == 1
    assert any("foo::test_bar" in str(x) for x in data["failed_tests"])


def test_fmt_11_generic_tap_passed_failed_contains(agate_assets, run_cli):
    output = "TAP version 13\nok 1 - test alpha\nok 2 - test beta\nnot ok 3 - test gamma"
    result = _run_formatter(agate_assets, run_cli, "generic-tap.sh", output, 1)
    data = _json(result)
    assert data["passed"] == 2
    assert data["failed"] == 1
    assert any("test gamma" in str(x) for x in data["failed_tests"])


def test_fmt_12_generic_junit_xml_total_failed_errors_passed(agate_assets, run_cli):
    output = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<testsuite name="suite" tests="3" failures="1" errors="1" skipped="0">\n'
        '<testcase name="test_one" classname="MyClass"/>\n'
        '<testcase name="test_two" classname="MyClass"><failure message="fail">expected true</failure></testcase>\n'
        '<testcase name="test_three" classname="MyClass"><error message="err">exception</error></testcase>\n'
        "</testsuite>"
    )
    result = _run_formatter(agate_assets, run_cli, "generic-junit-xml.sh", output, 1)
    data = _json(result)
    assert data["total"] == 3
    assert data["failed"] == 1
    assert data["errors"] == 1
    assert data["passed"] == 1


def test_bdd_35f_pytest_name_errors_field(agate_assets, run_cli):
    output = "ERROR tests/test_x.py - NameError: name 'compute' is not defined\n1 error"
    result = _run_formatter(agate_assets, run_cli, "pytest.sh", output, 2)
    data = _json(result)
    assert len(data["name_errors"]) == 1
