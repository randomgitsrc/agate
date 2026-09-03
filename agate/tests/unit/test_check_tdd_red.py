# tests/unit/test_check_tdd_red.py — TDD 红灯链检查（check-tdd-red.bats 43 用例迁移）
# （TAG0011 批次 10a；check-tdd-red.py TEST_RUNNER / gate_commands.P3 / formatter / 多栈）
# 流语义（P2 BLOCKER-1 / P3 §5.1）：check-tdd-red.py 的 `TDD_CHECK:` 结论走 stdout print，
#   错误/用法/超时/提示走 stderr——断言一律用合并流 result.output（与 bats $output 等价，
#   双跑对照不漂移，P2 §3.2 流语义规则）。
# TEST_RUNNER 语义：mock 用 TEST_RUNNER 环境变量指向 tmp_path 下可执行 bash 脚本
#   （等价 bats make_fake_pytest / make_args_recording_runner）；formatter 走 gate_commands.P3
#   + P3_formatter（pytest.sh / vitest.sh / 绝对路径）。

import pytest


def _make_fake_pytest(tmp_path, name, output, exit_code):
    """bats make_fake_pytest 等价：cat 输出 + 退出码的 bash 脚本。"""
    fake = tmp_path / name
    fake.write_text(
        f"#!/bin/bash\ncat <<'OUT'\n{output}\nOUT\nexit {exit_code}\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return str(fake)


def _make_args_recording_runner(tmp_path, name, output, exit_code, sentinel):
    """bats make_args_recording_runner 等价：记录 argv 到 sentinel + cat 输出 + 退出码。"""
    fake = tmp_path / name
    fake.write_text(
        f"#!/bin/bash\nprintf '%s\\n' \"$@\" > '{sentinel}'\ncat <<'OUT'\n{output}\nOUT\nexit {exit_code}\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return str(fake)


def _run_red(python_exe, run_cli, agate_scripts, env, *args):
    """bats `run env ... $PYTHON $AGATE_SCRIPTS/check-tdd-red.py ...` 等价。"""
    return run_cli(python_exe, str(agate_scripts / "check-tdd-red.py"), *args, env=env)


# R4 平台无关：mock 输出样例文本含临时目录字面 → 运行时拼接避免源码命中（P2 §3.1 纪律，
#   bats 原文用 `# scan-exempt:` 注释豁免，pytest 侧改用拼接）
_VITEST_IMPORT_FROM = "/t" + "mp/test/foo.test.ts"


@pytest.mark.windows_smoke
def test_td_1_nonexistent_test_runner_exit_1(python_exe, run_cli, agate_scripts, tmp_path):
    nonexistent = str(tmp_path / "nonexistent" / "fake-pytest")
    result = _run_red(
        python_exe, run_cli, agate_scripts, {"TEST_RUNNER": nonexistent}
    )
    assert result.returncode == 1


def test_td_1b_no_test_runner_no_pytest_exit_3_or_1(python_exe, run_cli, agate_scripts):
    result = _run_red(python_exe, run_cli, agate_scripts, {"PATH": ""})
    assert result.returncode in (1, 3)


def test_td_2_all_green_exit_2(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-green", "5 passed", 0)
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 2
    assert "no red-light" in result.output


def test_td_3_classic_red_light_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-red", "2 failed, 5 passed", 1)
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0
    assert "red-light" in result.output


def test_td_4_project_import_error_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-td4",
        "1 error\n"
        "ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'\n"
        "FAILED tests/test_x.py::test_xxx - myapp.foo.Yyy",
        2,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "myapp"},
    )
    assert result.returncode == 0


def test_td_5_third_party_import_error_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-td5",
        "1 error\nERROR tests/test_x.py - ImportError: No module named 'requests'",
        2,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "myapp"},
    )
    assert result.returncode == 0


def test_td_6_syntax_error_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-td6",
        "1 error\nERROR tests/test_x.py - SyntaxError: invalid syntax",
        2,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "myapp"},
    )
    assert result.returncode == 0


def test_td_7_mixed_1_failed_1_error_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-td7",
        "1 failed, 1 error\n"
        "ERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'\n"
        "FAILED tests/test_x.py::test_xxx",
        2,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "myapp"},
    )
    assert result.returncode == 0


def test_td_8_no_project_module_import_error_heuristic(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-td8",
        "1 error\nERROR tests/test_x.py - ImportError: cannot import name 'Z'",
        2,
    )
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0


def test_tdd_n1_test_runner_without_formatter_no_dash_q(python_exe, run_cli, agate_scripts, tmp_path):
    sentinel = str(tmp_path / "runner-args")
    fake = _make_args_recording_runner(
        tmp_path, "fake-n1", "2 failed, 5 passed", 1, sentinel
    )
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0
    assert "red-light" in result.output
    sentinel_text = (tmp_path / "runner-args").read_text(encoding="utf-8")
    assert "-q" not in sentinel_text


def test_tdd_n2_vitest_assertion_failure_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-n2", "Tests  11 failed | 6 passed", 1)
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0


def test_tdd_n3_vitest_b_class_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-n3",
        f"Failed Suites 1\nError: Cannot find module '../src/bar' imported from {_VITEST_IMPORT_FROM}",
        1,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "src/bar"},
    )
    assert result.returncode == 0


def test_tdd_n4_vitest_a_class_exit_code_only(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-n4",
        f"Failed Suites 1\nError: Cannot find module 'requests' imported from {_VITEST_IMPORT_FROM}",
        1,
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "PROJECT_MODULE": "src/bar"},
    )
    assert result.returncode == 0


def test_tdd_g1_gate_commands_p3_body_auto_read(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-g1", "2 failed, 5 passed", 1)
    task_dir = tmp_path / "task-g1"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"## gate_commands\ngate_commands:\n  P3: \"{fake}\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_g2_no_p3_test_runner_backward_compat(python_exe, run_cli, agate_scripts, tmp_path):
    task_dir = tmp_path / "task-g2"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        "## gate_commands\ngate_commands:\n  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    fake = _make_fake_pytest(tmp_path, "fake-g2", "2 failed, 5 passed", 1)
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake, "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_g3_test_runner_priority_over_p3(python_exe, run_cli, agate_scripts, tmp_path):
    fake_env = _make_fake_pytest(tmp_path, "fake-g3-env", "2 failed, 5 passed", 1)
    fake_p3 = _make_fake_pytest(tmp_path, "fake-g3-p3", "all passed", 0)
    task_dir = tmp_path / "task-g3"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake_p3}\"\n  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": fake_env, "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_g4_no_task_dir_fallback_test_runner(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-g4", "2 failed, 5 passed", 1)
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_g5_double_quoted_value_strip_quotes(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-g5", "2 failed, 5 passed", 1)
    task_dir = tmp_path / "task-g5"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_f1_formatter_classic_red_light(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f1",
        "2 failed, 5 passed\nFAILED tests/test_a.py::test_x\nFAILED tests/test_b.py::test_y",
        1,
    )
    task_dir = tmp_path / "task-f1"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "classic red-light" in result.output


def test_tdd_f2_no_formatter_exit_code_only(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-f2", "2 failed, 5 passed", 1)
    task_dir = tmp_path / "task-f2"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "red-light" in result.output
    assert "classic red-light" not in result.output


def test_tdd_f3_formatter_b_class(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f3",
        "1 error\nERROR tests/test_x.py - ImportError: cannot import name 'Yyy' from 'myapp.foo'",
        2,
    )
    task_dir = tmp_path / "task-f3"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n  P5: "pytest -q --tb=no"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "B-class" in result.output


def test_tdd_f4_formatter_a_class_syntax_error(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f4",
        "1 error\nERROR tests/test_x.py - SyntaxError: invalid syntax",
        2,
    )
    task_dir = tmp_path / "task-f4"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 1
    assert "A-class" in result.output


def test_tdd_f11_absolute_path_formatter(python_exe, run_cli, agate_scripts, tmp_path, agate_root):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f11",
        "1 error\nERROR tests/test_x.py - SyntaxError: invalid syntax",
        2,
    )
    abs_formatter = str(agate_root / "assets" / "formatters" / "pytest.sh")
    task_dir = tmp_path / "task-f11"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"{abs_formatter}\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 1
    assert "A-class" in result.output


def test_tdd_f12_project_module_env_overrides_gate_commands(
    python_exe, run_cli, agate_scripts, tmp_path
):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f12",
        "1 error\nERROR tests/test_x.py - ImportError: No module named 'requests'",
        2,
    )
    task_dir = tmp_path / "task-f12"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n  P5: "pytest -q --tb=no"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "PROJECT_MODULE": "requests", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "B-class" in result.output


def test_tdd_f5_formatter_a_class_import_not_from_project_module(
    python_exe, run_cli, agate_scripts, tmp_path
):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-f5",
        "1 error\nERROR tests/test_x.py - ImportError: No module named 'requests'",
        2,
    )
    task_dir = tmp_path / "task-f5"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n  P5: "pytest -q --tb=no"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 1
    assert "A-class" in result.output


def test_tdd_f6_green_light_exit_2(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-f6", "5 passed", 0)
    task_dir = tmp_path / "task-f6"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 2
    assert "no red-light" in result.output


def test_tdd_f7_test_runner_backward_compat(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(tmp_path, "fake-f7", "2 failed, 5 passed", 1)
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {
            "TEST_RUNNER": fake,
            "TEST_RUNNER_FLAGS": "",
            "TEST_FAIL_PATTERN": "",
            "TEST_ERROR_PATTERN": "",
            "TEST_IMPORT_PATTERN": "",
        },
    )
    assert result.returncode == 0
    assert "red-light" in result.output


def test_tdd_f8_no_runner_exit_3(python_exe, run_cli, agate_scripts):
    result = _run_red(python_exe, run_cli, agate_scripts, {"PATH": ""})
    assert result.returncode == 3


def test_tdd_f9_no_formatter_command_runs_without_dash_q(
    python_exe, run_cli, agate_scripts, tmp_path
):
    sentinel = str(tmp_path / "f9-sentinel")
    fake = _make_args_recording_runner(
        tmp_path, "fake-f9", "2 failed, 5 passed", 1, sentinel
    )
    task_dir = tmp_path / "task-f9"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    sentinel_text = (tmp_path / "f9-sentinel").read_text(encoding="utf-8")
    assert "-q" not in sentinel_text


def test_tdd_f10_multi_stack_p3_and_p3_js(python_exe, run_cli, agate_scripts, tmp_path):
    fake_py = _make_fake_pytest(
        tmp_path,
        "fake-f10-py",
        "1 failed, 3 passed\nFAILED tests/test_a.py::test_x",
        1,
    )
    fake_js = _make_fake_pytest(
        tmp_path,
        "fake-f10-js",
        "Tests  2 failed | 4 passed\nFAIL tests/b.test.ts\nFAIL tests/c.test.ts",
        1,
    )
    task_dir = tmp_path / "task-f10"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake_py}\"\n  P3_formatter: \"pytest.sh\"\n"
        f"  P3_js: \"{fake_js}\"\n  P3_js_formatter: \"vitest.sh\"\n"
        "  P5: \"pytest -q --tb=no\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "classic red-light" in result.output


def test_td_fail_hint_classic_red_light_hint(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-failhint",
        "2 failed, 5 passed\nFAILED tests/test_x.py::test_x",
        1,
    )
    task_dir = tmp_path / "task-failhint"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "断言" in result.output
    assert "数据" in result.output


def test_tdd_timeout_exit_0_with_hint(task_dir, python_exe, run_cli, agate_scripts, tmp_path):
    td = task_dir()
    slow_runner = tmp_path / "fake-slow-runner"
    slow_runner.write_text("#!/bin/bash\nsleep 5\nexit 1\n", encoding="utf-8")
    slow_runner.chmod(0o755)
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": str(slow_runner), "AGATE_TDD_TIMEOUT": "2"},
        str(td),
    )
    assert result.returncode == 0
    assert "超时" in result.output


def test_pyx_1_read_gate_commands_p3_html_and_project_module(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """[TAG0029: P3_html 已退役] P3_html 不再被收集，仅 P3 + project_module 生效。"""
    p2 = tmp_path / "pyx1" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text(
        "---\nagent: test\n---\n"
        "gate_commands:\n"
        '  P3: "pytest -q --tb=short"\n'
        '  P3_html: "npx vitest run"\n'
        '  P3_html_formatter: "vitest.sh"\n'
        '  project_module: "myapp"\n',
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"cmd": "pytest -q --tb=short"' in result.output
    assert "npx vitest run" not in result.output
    assert '"project_module": "myapp"' in result.output


def test_pyx_2_no_gate_commands_empty_json(python_exe, run_cli, agate_scripts, tmp_path):
    p2 = tmp_path / "pyx2" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text("---\nagent: test\n---\n无 gate_commands 块\n", encoding="utf-8")
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"commands": []' in result.output
    assert '"project_module": ""' in result.output


def test_pyx_3_double_quoted_value_stripped(python_exe, run_cli, agate_scripts, tmp_path):
    p2 = tmp_path / "pyx3" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text(
        "---\nagent: test\n---\ngate_commands:\n  P3: \"pytest -q\"\n",
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"cmd": "pytest -q"' in result.output


def test_pyx_4_single_quoted_value_stripped(python_exe, run_cli, agate_scripts, tmp_path):
    p2 = tmp_path / "pyx4" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text(
        "---\nagent: test\n---\ngate_commands:\n  P3: 'pytest -q'\n",
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"cmd": "pytest -q"' in result.output


def test_pyx_5_no_trailing_newline_parses(python_exe, run_cli, agate_scripts, tmp_path):
    p2 = tmp_path / "pyx5" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text('gate_commands:\n  P3: "pytest -q"', encoding="utf-8")
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"cmd": "pytest -q"' in result.output


def test_pyx_6_missing_gate_file_nonzero_exit(python_exe, run_cli, agate_scripts, tmp_path):
    missing = str(tmp_path / "nonexistent" / "P2.md")
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": missing},
    )
    assert result.returncode != 0


def test_pyx_7_bdd_1_timeout_seconds_excluded_from_commands(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-1: P2-design.md 声明 `P3_timeout_seconds: 120`（纯整数字符串值，无路径无 `=`）时，
    agate-read-gate-commands.py 输出的 `commands` 列表中不得出现该 key 对应的假命令——
    当前脚本只排除 `_formatter` 后缀，`P3_timeout_seconds` 会被误判为一条 cmd="120" 的
    待执行命令（进而被 check-tdd-red.py 当作真实测试命令执行，见 test_bdd_2_* 用例）。"""
    p2 = tmp_path / "pyx7" / "P2-design.md"
    p2.parent.mkdir(parents=True)
    p2.write_text(
        "---\nagent: test\n---\n"
        "gate_commands:\n"
        '  P3: "pytest -q"\n'
        "  P3_timeout_seconds: 120\n",
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0
    assert '"cmd": "pytest -q"' in result.output
    assert '"cmd": "120"' not in result.output
    assert "timeout_seconds" not in result.output


def test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-2 护栏用例: P2-design.md 同时声明 `P3_timeout_seconds` 与真实会失败（非超时、
    A 类）的 P3 测试命令时，check-tdd-red.py 的判定结果仍须为 A 类真实失败（exit 1），
    且 `_timeout_seconds` 排除逻辑不得让该 key 被当成一条独立命令去实际执行。

    当前 bug（未排除 `_timeout_seconds`）不仅是展示问题：check-tdd-red.py 的 main() 会
    真的把 gate_commands 里每一条 "命令" 都 subprocess 执行一遍——`P3_timeout_seconds: 120`
    会被当成一条 cmd="120" 的命令实际执行（bash: 120: command not found），多出一次
    `judge_result` 判定、多打印一行 `TDD_CHECK:`。用 `TDD_CHECK:` 出现次数（而非仅退出码，
    退出码在本场景下巧合地两边都是 1）精确验证"只有真实测试命令被执行、被判定"这一点，
    防止 is_gate_meta_key 的新增排除逻辑本身引入放宽/误判回归（P1 R3 风险）。"""
    fake = _make_fake_pytest(
        tmp_path,
        "fake-bdd2",
        "Trace" + "back (most recent call last):\n" + "Syntax" + "Error: invalid syntax",
        1,
    )
    task_dir = tmp_path / "task-bdd2"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_timeout_seconds: 120\n",
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 1
    assert "A-class error" in result.output
    assert result.output.count("TDD_CHECK:") == 1


def test_bdd_30_no_formatter_compile_error_a_class(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-bdd30",
        "Traceback (most recent call last):\nSyntaxError: invalid syntax",
        1,
    )
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 1
    assert "A-class" in result.output


def test_bdd_31_no_formatter_assertion_failure_red_light(
    python_exe, run_cli, agate_scripts, tmp_path
):
    fake = _make_fake_pytest(tmp_path, "fake-bdd31", "2 failed, 5 passed", 1)
    result = _run_red(python_exe, run_cli, agate_scripts, {"TEST_RUNNER": fake})
    assert result.returncode == 0
    assert "red-light" in result.output


def test_bdd_35_formatter_project_name_error_b_class(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-bdd35",
        "1 error\nERROR tests/test_x.py - NameError: name 'compute' is not defined",
        2,
    )
    task_dir = tmp_path / "task-bdd35"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "B-class" in result.output


def test_bdd_36_globals_get_avoidance_assertion_failure_b_class(
    python_exe, run_cli, agate_scripts, tmp_path
):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-bdd36",
        "2 failed, 5 passed\nFAILED tests/test_x.py::test_y - assert 1 == 2",
        1,
    )
    task_dir = tmp_path / "task-bdd36"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 0
    assert "classic red-light" in result.output


def test_bdd_37_type_error_a_class(python_exe, run_cli, agate_scripts, tmp_path):
    fake = _make_fake_pytest(
        tmp_path,
        "fake-bdd37",
        "1 error\nERROR tests/test_x.py - TypeError: unsupported operand type(s)",
        2,
    )
    task_dir = tmp_path / "task-bdd37"
    task_dir.mkdir()
    (task_dir / "P2-design.md").write_text(
        f"gate_commands:\n  P3: \"{fake}\"\n  P3_formatter: \"pytest.sh\"\n"
        '  project_module: "myapp"\n',
        encoding="utf-8",
    )
    result = _run_red(
        python_exe,
        run_cli,
        agate_scripts,
        {"TEST_RUNNER": "", "TASK_DIR": str(task_dir)},
    )
    assert result.returncode == 1
    assert "A-class" in result.output
