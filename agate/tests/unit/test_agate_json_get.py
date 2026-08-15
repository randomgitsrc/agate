# tests/unit/test_agate_json_get.py — 共享 JSON 提取工具
# （agate-json-get.bats 8 用例迁移，TAG0011 批次 2）
# 被测：agate/scripts/agate-json-get.py（JSON 从 stdin 读入；
#       get / len / index / set / count_prefix / list / escape）
# 流语义：JGET.7 空输出断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import pytest


def _run_jget(agate_scripts, python_exe, run_cli, *args, input=None, env=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-json-get.py"),
        *args,
        input=input,
        env=env,
    )


@pytest.mark.windows_smoke
def test_jget_1_get_scalar_key_with_default(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "get",
        "exit_code",
        "1",
        input='{"exit_code":2,"failed":3}',
    )
    assert result.returncode == 0
    assert result.output.strip() == "2"

    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "get",
        "missing",
        "0",
        input='{"exit_code":2,"failed":3}',
    )
    assert result.output.strip() == "0"


def test_jget_2_get_string_key_empty_default(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "get",
        "project_module",
        "",
        input='{"a":"b"}',
    )
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_jget_3_len_array_length_default_zero(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "len",
        "commands",
        input='{"commands":[{"cmd":"a"},{"cmd":"b"}]}',
    )
    assert result.returncode == 0
    assert result.output.strip() == "2"

    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "len",
        "commands",
        input='{"commands":[]}',
    )
    assert result.output.strip() == "0"

    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "len",
        "missing",
        input="{}",
    )
    assert result.output.strip() == "0"


def test_jget_4_index_nested_array_element_field(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "index",
        "commands",
        "0",
        "cmd",
        input='{"commands":[{"cmd":"pytest","formatter":"pytest.sh"},{"cmd":"pytest","formatter":"pytest.sh"}]}',
    )
    assert result.returncode == 0
    assert result.output.strip() == "pytest"

    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "index",
        "commands",
        "0",
        "formatter",
        input='{"commands":[{"cmd":"pytest","formatter":"pytest.sh"}]}',
    )
    assert result.output.strip() == "pytest.sh"


def test_jget_5_set_rewrite_key_and_reflow_json(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "set",
        "project_module",
        "PROJECT_MODULE",
        input='{"commands":[{"cmd":"pytest"}],"project_module":""}',
        env={"PROJECT_MODULE": "mymod"},
    )
    assert result.returncode == 0
    assert '"project_module": "mymod"' in result.output


def test_jget_6_count_prefix_module_prefix_matches(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "count_prefix",
        "import_errors",
        "module",
        "PROJECT_MODULE",
        input='{"import_errors":[{"module":"mymod.foo"},{"module":"other.bar"},{"module":"mymod.baz"}]}',
        env={"PROJECT_MODULE": "mymod"},
    )
    assert result.returncode == 0
    assert result.output.strip() == "2"


def test_jget_7_list_print_each_array_element(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "list",
        "failed_tests",
        input='{"failed_tests":["a","b","c"]}',
    )
    assert result.returncode == 0
    assert "a" in result.output
    assert "b" in result.output
    assert "c" in result.output

    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "list",
        "missing",
        input="{}",
    )
    assert result.returncode == 0
    assert result.output.strip() == ""


def test_jget_8_escape_json_dumps_stdin_raw_text(agate_scripts, python_exe, run_cli):
    result = _run_jget(
        agate_scripts,
        python_exe,
        run_cli,
        "escape",
        input='a"b\nc',
    )
    assert result.returncode == 0
    assert 'a\\"b' in result.output
