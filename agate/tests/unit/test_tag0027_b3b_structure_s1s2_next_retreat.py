# agate/tests/unit/test_tag0027_b3b_structure_s1s2_next_retreat.py — TAG0027 B3b 批：S-1/S-2
# next/retreat 双向一致性扩展（BDD-4）
#
# 被测契约（P2-design §3.2 定案 D2-A）：
#   WORKFLOW.md 阶段总览表在「执行角色」后加 next/retreat 两列（4/5 列，评审角色顺延 6/7 列）；
#   check-structure-consistency.py `_parse_workflow_rows` 扩展返回含 next/retreat 单元格；
#   `_check_s1` 增比对：YAML next/retreat ↔ 表 4/5 列（null ↔ 表 `—`/空归一）；P6.5 gate_subphase
#   形态语义检查（md 侧不出现指向独立后继 phase 的 plain P7 值）；S-2 不变。
#   不引入新一致性检查脚本（复用 S-1/S-2）。
#   BDD-4：phases.yaml 与 WORKFLOW 总览表之间制造不一致（改一处 retreat 值不同步）→
#   check-structure-consistency S-1 ERROR exit 1。
#
# TDD 红灯语义：P3 现状 `_parse_workflow_rows` 返回 3 元组、`_check_s1` 只比对 id/name/exec_role
#   → 对含 next/retreat 4/5 列的表 S-1 不比对 → "YAML retreat ≠ 表列"场景 exit 0（未检出）
#   → 断言 exit 1 失败 = B 类真红灯（扩展点未实现）；同表 YAML 一致场景现状 exit 0 = 回归守卫。
#   注意：S-5（schema）在假协议树上须保持通过——夹具 phases_schema 同步扩展声明 next/retreat
#   （P4 B1 须扩展真实 phases.schema.json 同理），保证不一致由 S-1 列比对检出而非 S-5 误伤。
# 平台无关：tmp_path fixture + run_cli(python_exe,...) + env AGATE_ROOT。

import json

from _rules_test_utils import make_fake_root


def _run_structure(agate_scripts, python_exe, run_cli, root):
    script = agate_scripts / "check-structure-consistency.py"
    assert script.is_file(), "check-structure-consistency.py 未实现——TDD 红灯锚点"
    return run_cli(python_exe, str(script), env={"AGATE_ROOT": str(root)})


# 带 next/retreat 4/5 列的总览表（D2-A 形态：执行角色后加 next/retreat，评审角色顺延 6/7 列）
_CONSISTENT_TABLE = (
    "| 阶段 | 名称 | 执行角色 | next | retreat | 评审角色 | 门槛 |\n"
    "|------|------|----------|------|---------|----------|------|\n"
    "| P1 | 需求基线 | analyst | P2 | P0 | requirements-review | P1-requirements.md 存在 |\n"
    "| P2 | 方案设计层 | architect | P3 | P1 | plan-eng-review | P2-review.md approved |\n"
    "| P3 | 测试设计 | test-designer | P4 | P1 | --- | check-tdd-red exit 0 |\n"
    "| READY | 待发布 | --- | --- | --- | --- | 人手动发布 |\n"
)


def _phases_with_next_retreat():
    """假 phases.yaml：P1/P2/P3 带 next/retreat（值与 _CONSISTENT_TABLE 对齐）。"""
    return (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P1\n"
        "    name: 需求基线\n"
        "    exec_role: analyst\n"
        "    retry_cap: 3\n"
        "    next: P2\n"
        "    retreat: P0\n"
        "  - id: P2\n"
        "    name: 方案设计层\n"
        "    exec_role: architect\n"
        "    retry_cap: 3\n"
        "    next: P3\n"
        "    retreat: P1\n"
        "  - id: P3\n"
        "    name: 测试设计\n"
        "    exec_role: test-designer\n"
        "    retry_cap: 2\n"
        "    next: P4\n"
        "    retreat: P1\n"
    )


def _extended_phases_schema():
    """default_phases_schema 等价但 items.properties 增 next/retreat（值域 P0-P8 联合 null，
    不含 P6.5——P6.5 非主线 next 目标；P2 §3.1 值域）。P4 须照此扩展真实 schema。"""
    phase_ids = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["schema_version", "phases"],
        "properties": {
            "schema_version": {"type": "integer", "enum": [1]},
            "phases": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["id", "name", "exec_role"],
                    "properties": {
                        "id": {"type": "string", "enum": [*phase_ids, "P6.5"]},
                        "name": {"type": "string"},
                        "exec_role": {"type": "string"},
                        "retry_cap": {"type": "integer", "enum": [2, 3]},
                        "next": {
                            "type": ["string", "null"],
                            "enum": [*phase_ids, None],
                        },
                        "retreat": {
                            "type": ["string", "null"],
                            "enum": [*phase_ids, None],
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def test_bdd_4_s1_yaml_retreat_vs_table_mismatch_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-4：制造 YAML↔表 retreat 不一致（YAML P2 retreat:P1 ↔ 表 P2 retreat 列写 P3）→
    check-structure-consistency S-1 exit 1（S-1 扩展比对 4/5 列 = BDD-4 核心）。
    P3 现状 S-1 不比对 next/retreat → exit 0（未检出）→ 红灯（B 类：扩展点未实现）。"""
    table_mismatch = _CONSISTENT_TABLE.replace(
        "| P2 | 方案设计层 | architect | P3 | P1 | plan-eng-review",
        "| P2 | 方案设计层 | architect | P3 | P3 | plan-eng-review",
    )
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_next_retreat(),
        workflow_text=table_mismatch,
        phases_schema=_extended_phases_schema(),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 1, (
        "YAML retreat ≠ 总览表 retreat 列 → S-1 应 ERROR exit 1（BDD-4）；"
        "现状 S-1 未扩展比对 4/5 列 → exit 0（B 类红，S-1/S-2 扩展未实现）"
    )


def test_bdd_4_s1_yaml_next_vs_table_mismatch_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-4：制造 YAML↔表 next 不一致（YAML P1 next:P2 ↔ 表 P1 next 列写 P4）→ S-1 exit 1。
    P3 现状 exit 0 → 红灯（B 类）。"""
    table_mismatch = _CONSISTENT_TABLE.replace(
        "| P1 | 需求基线 | analyst | P2 | P0 | requirements-review",
        "| P1 | 需求基线 | analyst | P4 | P0 | requirements-review",
    )
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_next_retreat(),
        workflow_text=table_mismatch,
        phases_schema=_extended_phases_schema(),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 1, (
        "YAML next ≠ 总览表 next 列 → S-1 应 ERROR exit 1（BDD-4）；现状未扩展 → exit 0（红）"
    )


def test_bdd_4_s1_consistent_next_retreat_exit_0(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-4 正向（回归守卫）：YAML 与表 next/retreat 一致 → S-1/S-2 exit 0（加列后既有
    id/name/exec_role 比对不受影响——_TABLE_ROW_RE 只消费前 3 列兼容实证，§3.2）。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_next_retreat(),
        workflow_text=_CONSISTENT_TABLE,
        phases_schema=_extended_phases_schema(),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, f"一致场景应 exit 0；{result.output[:800]}"
