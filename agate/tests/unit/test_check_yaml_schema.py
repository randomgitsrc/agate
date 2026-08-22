# agate/tests/unit/test_check_yaml_schema.py — BDD-1(M0) rules/ 结构化目录过 schema 校验
#
# 被测：agate/scripts/check-yaml-schema.py（P4 M0 交付，P3 尚不存在 → 真红灯 B 类）。
# 契约（P2-design §3.2）：校验 AGATE_ROOT/rules/*.yaml 对 rules/schema/*.json（draft-07
# 子集：type/required/enum/properties/items/additionalProperties/minItems）：
#   * 全部 YAML 合法 → exit 0
#   * 任一非法字段（additionalProperties 拒绝）/ 错误枚举 / 错误类型 / 缺 required → exit 非 0
# 夹具入口：AGATE_ROOT 指向 tmp_path 下的最小假协议树（_rules_test_utils.make_fake_root）。
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest
from _rules_test_utils import DEFAULT_DISPATCH_YAML, default_dispatch_schema, make_fake_root


def _run_schema_check(agate_scripts, python_exe, run_cli, proto_root):
    script = agate_scripts / "check-yaml-schema.py"
    assert script.is_file(), "check-yaml-schema.py 未实现（P4 M0 交付）——TDD 红灯锚点"
    return run_cli(python_exe, str(script), env={"AGATE_ROOT": str(proto_root)})


@pytest.mark.windows_smoke
def test_bdd_1_valid_rules_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """合法 YAML（schema 与数据互证）→ 退出码 0。"""
    root = make_fake_root(tmp_path)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output


def test_bdd_1_invalid_enum_exit_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    """错误枚举：exec_role 不在 schema 枚举 → 退出码非 0。"""
    bad_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P2\n"
        "    name: 方案设计层\n"
        "    exec_role: not-a-role\n"  # 非执行角色枚举
        "    retry_cap: 3\n"
    )
    root = make_fake_root(tmp_path, phases_text=bad_phases)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_invalid_type_exit_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    """错误类型：retry_cap 声明为字符串而非整数 → 退出码非 0。"""
    bad_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P3\n"
        "    name: 测试设计\n"
        "    exec_role: test-designer\n"
        "    retry_cap: three\n"
    )
    root = make_fake_root(tmp_path, phases_text=bad_phases)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_invalid_field_exit_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    """非法字段：phases 项含 schema 未声明 key（additionalProperties false）→ 退出码非 0。"""
    bad_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P1\n"
        "    name: 需求基线\n"
        "    exec_role: analyst\n"
        "    totally_unknown_key: 1\n"
    )
    root = make_fake_root(tmp_path, phases_text=bad_phases)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_missing_required_exit_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    """缺 required：phase 缺 name → 退出码非 0。"""
    bad_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P1\n"
        "    exec_role: analyst\n"  # 缺 name
    )
    root = make_fake_root(tmp_path, phases_text=bad_phases)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_dispatch_mode_enum_aligned(agate_scripts, python_exe, run_cli, tmp_path):
    """P2-review 发现 #2 固化：dispatch.yaml modes 词表 = 对齐后五模式；
    混入旧词表词（hybrid）→ 枚举违规 → 退出码非 0。"""
    bad_dispatch = (
        "schema_version: 1\n"
        "modes: [single, hybrid]\n"  # hybrid 为设计文档首版遗留词，非对齐后词表
    )
    root = make_fake_root(tmp_path, dispatch_text=bad_dispatch)
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_schema_self_check_exit_nonzero(agate_scripts, python_exe, run_cli, tmp_path):
    """P2-design §3.2 R5：check-yaml-schema 对 schema 文件自身做健全性检查——
    损坏的 schema（非法 JSON）→ 退出码非 0，防 schema 形同虚设。"""
    root = make_fake_root(tmp_path, phases_schema="{ not valid json")
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_1_dispatch_schema_roundtrip(agate_scripts, python_exe, run_cli, tmp_path):
    """dispatch.yaml 合法（对齐词表）且 schema 互证 → 退出码 0。"""
    root = make_fake_root(
        tmp_path,
        dispatch_text=DEFAULT_DISPATCH_YAML,
        dispatch_schema=default_dispatch_schema(),
    )
    result = _run_schema_check(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output
