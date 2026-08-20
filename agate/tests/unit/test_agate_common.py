# tests/unit/test_agate_common.py — agate_common.is_gate_meta_key 单测
# （TAG0017/DEBT0010 新增：BDD-1/2/3/4 共同依赖的共享判据函数 is_gate_meta_key(key) 直接单测）
# 被测：agate/scripts/agate_common.py 的 is_gate_meta_key（P2 候选方案 A，拟插入点
# probe_python() 附近，见 P2-design.md §1.1）。语义：
#   key.endswith(("_formatter", "_timeout_seconds")) —— 仅排除这两个已知固定后缀，
#   不做通配/正则宽松匹配（P1 R3 风险条目：防止把 DEBT0010 修复做成"所有非常规 key 都忽略"，
#   连真正需要核实/计入的 key 也一并放宽）。
#
# 当前 agate_common.py 尚不存在该函数 → `from agate_common import is_gate_meta_key`
# 直接触发 ImportError（真实的项目内 import 失败 = B 类红灯语义），非测试代码自身语法错误。
#
# 复用项目既有 subprocess -c 调用惯例（test_helpers_python.py `_probe_code` 同款），
# 不在 pytest 自身进程内直接 `import agate_common`（避免与其他用例共享/污染 sys.path）。

import pytest


def _check_code(key):
    return (
        "from agate_common import is_gate_meta_key; "
        f"print(is_gate_meta_key({key!r}))"
    )


@pytest.mark.parametrize(
    "key",
    ["P3_formatter", "P5_formatter", "P3_html_formatter", "P5_js_formatter"],
)
def test_bdd_4_is_gate_meta_key_formatter_suffix_true(python_exe, run_cli, agate_scripts, key):
    """`_formatter` 后缀键（既有排除逻辑，未受 DEBT0010 影响）应仍判定为元信息 key。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "True"


@pytest.mark.parametrize(
    "key",
    ["P3_timeout_seconds", "P5_timeout_seconds", "P3_html_timeout_seconds"],
)
def test_bdd_1_is_gate_meta_key_timeout_seconds_suffix_true(python_exe, run_cli, agate_scripts, key):
    """`_timeout_seconds` 后缀键（DEBT0010 核心目标）必须判定为元信息 key，不被当作待核实命令。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "True"


@pytest.mark.parametrize(
    "key",
    ["P3", "P5", "P3_html", "project_module", "P3_timeout"],
)
def test_bdd_2_is_gate_meta_key_ordinary_key_false(python_exe, run_cli, agate_scripts, key):
    """普通命令 key（含前缀相似但非完整 `_timeout_seconds` 后缀的 `P3_timeout`）不得被误排除——
    R3 护栏：防止修复把判据放宽为通配匹配，导致真实命令 key 被静默吞掉。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "False"
