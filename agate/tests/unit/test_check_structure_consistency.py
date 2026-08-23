# agate/tests/unit/test_check_structure_consistency.py — BDD-2/3/5(M0) S-1~S-6 双向一致性
#
# 被测：agate/scripts/check-structure-consistency.py（P4 M0 交付，P3 尚不存在 → 真红灯 B 类）。
# 契约（P2-design §3.3）：
#   S-1 YAML→md   phases.yaml 每个 phase（id/name/exec_role）在 WORKFLOW 阶段总览表有对应行且一致
#   S-2 md→YAML   WORKFLOW 表每行 phase id 在 phases.yaml 有定义（只匹配 P 数字前缀行，
#                 READY/表外行显式排除——P2-review 发现 #1 固化）
#   S-3 YAML→cards 抽检 phase-cards/P2-design.md 门槛/产出/派发节 vs phases.yaml P2 声明
#   S-4 YAML→scripts 脚本字段读取登记表（dispatch.yaml field_readers）与 phases.yaml 字段集一致；
#                 gate_commands 语法声明（meta_suffixes/special_keys）与 is_gate_meta_key 判据一致
#   S-5 schema    串联 check-yaml-schema.py（独立进程），rules/*.yaml 违反 schema → 报 S-5
#   S-6 引用完整性 YAML 中 file:/template:/script: 引用路径在协议根下真实存在
# 任一 ERROR → exit 1；全部 OK → exit 0。夹具入口 = AGATE_ROOT 指向最小假协议树。
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest
from _rules_test_utils import (
    DEFAULT_DISPATCH_YAML,
    DEFAULT_P2_CARD,
    DEFAULT_PHASES_YAML,
    make_fake_root,
)


def _run_structure(agate_scripts, python_exe, run_cli, proto_root):
    script = agate_scripts / "check-structure-consistency.py"
    assert script.is_file(), "check-structure-consistency.py 未实现（P4 M0 交付）——TDD 红灯锚点"
    return run_cli(python_exe, str(script), env={"AGATE_ROOT": str(proto_root)})


@pytest.mark.windows_smoke
def test_bdd_2_s1_s2_consistent_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """两侧一致（YAML 含 READY 行之外全部阶段；表含 READY 行被 S-2 排除）→ 退出码 0。
    同时固定 P2-review 发现 #1：S-2 必须忽略 READY 行。"""
    root = make_fake_root(tmp_path)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output


def test_bdd_2_s1_yaml_extra_phase_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-1 漂移：phases.yaml 增一个表外阶段（P9）→ 退出码非 0。"""
    yaml_with_p9 = DEFAULT_PHASES_YAML + (
        "  - id: P9\n"
        "    name: 幽灵阶段\n"
        "    exec_role: verifier\n"
        "    retry_cap: 2\n"
    )
    root = make_fake_root(tmp_path, phases_text=yaml_with_p9)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_2_s2_md_extra_phase_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-2 漂移：WORKFLOW 表新增 P4 行（YAML 未定义；READY 行仍应排除）→ 退出码非 0。"""
    table_with_p4 = (
        "| 阶段 | 名称 | 执行角色 | 评审角色 | 门槛 |\n"
        "|------|------|----------|----------|------|\n"
        "| P1 | 需求基线 | analyst | requirements-review | P1-requirements.md 存在 |\n"
        "| P2 | 方案设计层 | architect | plan-eng-review | P2-review.md approved |\n"
        "| P3 | 测试设计 | test-designer | --- | check-tdd-red exit 0 |\n"
        "| P4 | 代码实现 | implementer | review | 暂存区含非 md 文件 |\n"
        "| READY | 待发布 | --- | --- | 人手动发布 |\n"
    )
    root = make_fake_root(tmp_path, workflow_text=table_with_p4)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_2_s1_name_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-1 漂移：phases.yaml 的 P2 name 与总览表不一致 → 退出码非 0。"""
    yaml_renamed = DEFAULT_PHASES_YAML.replace("  - id: P2\n    name: 方案设计层", "  - id: P2\n    name: 方案设计改名")
    root = make_fake_root(tmp_path, phases_text=yaml_renamed)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_3_s6_missing_reference_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-6 引用完整性：roles.yaml 引用不存在的角色文件 → 退出码非 0。"""
    bad_roles = (
        "schema_version: 1\n"
        "execution_roles:\n"
        "  - {id: ghost-role, file: assets/execution-roles/ghost-role.md}\n"
    )
    root = make_fake_root(tmp_path, roles_text=bad_roles)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_3_s5_schema_enum_violation_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-5：structure 串联 schema 校验——phases.yaml 违反 exec_role 枚举 → 退出码非 0。"""
    bad_enum_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P2\n"
        "    name: 方案设计层\n"
        "    exec_role: not-a-role\n"
        "    retry_cap: 3\n"
    )
    root = make_fake_root(tmp_path, phases_text=bad_enum_phases)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3_card_output_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-3 抽检：phase-cards/P2-design.md 产出规格节缺失 phases.yaml 声明的 P2-review.md →
    退出码非 0（BDD-5「任一处不一致 → 非 0」）。"""
    tampered_card = (
        "# P2 方案设计层\n\n"
        "## 前置条件\n"
        "- P1-requirements.md 完成\n\n"
        "## 产出规格\n"
        "- P2-design.md\n"  # P2-review.md 缺失
    )
    root = make_fake_root(tmp_path, card_text=tampered_card)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s4_field_readers_unknown_field_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-4：dispatch.yaml field_readers 登记了 phases.yaml 未声明的字段 → 退出码非 0。"""
    bad_dispatch = DEFAULT_DISPATCH_YAML.replace(
        "fields: [candidate_count, packages, domains, ui_affected, gate_commands]",
        "fields: [nonexistent_field]",
    )
    root = make_fake_root(tmp_path, dispatch_text=bad_dispatch)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s4_gate_commands_syntax_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-4 + P2-review 发现 #3 固化：gate_commands 合法 key = is_gate_meta_key
    （_formatter/_timeout_seconds 后缀）OR project_module 特判；语法声明缺少 project_module
    特判 → 与 agate_common.is_gate_meta_key 判据不一致 → 退出码非 0。"""
    bad_dispatch = DEFAULT_DISPATCH_YAML.replace(
        "  special_keys: [project_module]",
        "  special_keys: []",
    )
    root = make_fake_root(tmp_path, dispatch_text=bad_dispatch)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_initial_consistency_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """BDD-5 正面路径：S-3/S-4 初始一致（默认假协议树 P2 三方一致）→ 退出码 0 且报 S-3/S-4 OK。"""
    root = make_fake_root(tmp_path)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output
    assert "S3" in result.output, "未输出 S-3 检查项（卡片↔YAML 一致判定缺失）"
    assert "S4" in result.output, "未输出 S-4 检查项（脚本字段登记一致判定缺失）"


# ─────────────────────────────────────────────
# TAG0022 增补：S-3 双向 gate 命令一致性（RM-AG0038 / BDD-5，P2 §4.2.2 S-3a/S-3b；TG-1）
#   S-3a（YAML→md）：phases.yaml gates[].check 中的命令串须在对应卡片 ## gate 规则
#                    （或推进条件）节出现；缺失 → ERROR（单侧漂移：YAML 侧加了，md 侧没加）。
#   S-3b（md→YAML）：卡片 ## gate 规则 节中机器可判定命令行（check-gate.py P\d+ /
#                    gate_commands.P\d+ / check-[\w-]+\.py）须在 gates[].check 有声明；
#                    未声明 → ERROR（单侧漂移：md 侧加了，YAML 侧没加）。
#   P3 现状 S-3a/S-3b 未实现 → 单侧漂移不报 → exit 0 → 断言非 0 失败 = 真红灯（B 类，行为未实现）；
#   双侧一致 → 现 exit 0（回归守卫，P4 实现后仍 exit 0）。
#   NB-1：S-3a/S-3b 是叠加在既有 S-3 outputs/orphan/exec_role 下的新增子检查——本组用例
#   不触碰产出规格/派发节，既有 S-3 用例保持绿。
#   S-3a 口径：卡片 ## gate 规则 节内须同时出现 P2 的全部 gates[].check 串（含散文描述），
#   故双侧一致用例把两条 gate 串都放进节内，对「命令串专属」或「全部串」两种实现语义均稳健。


def _phases_with_p2_gate_cmd():
    """DEFAULT_PHASES_YAML + P2 gates 增补机器可判定 gate 命令串（S-3a/S-3b 对账对象）。"""
    return DEFAULT_PHASES_YAML.replace(
        "      - {check: P2-review.md status == approved}\n",
        "      - {check: P2-review.md status == approved}\n"
        "      - {check: check-gate.py P2 $TASK_DIR}\n",
    )


def _card_with_gate_rules(extra_lines):
    """DEFAULT_P2_CARD + `## gate 规则` 节（节内行可含机器可判定命令行）。"""
    return DEFAULT_P2_CARD + "## gate 规则\n" + extra_lines


def test_bdd_5_s3a_yaml_gate_cmd_not_in_card_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 S-3a：YAML gates 增补命令串但卡片 ## gate 规则 未出现 → 非 0（YAML 侧漂移）。
    TDD：P3 现状 S-3a 未实现 → exit 0 → 红灯（B 类）。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_p2_gate_cmd(),
        card_text=_card_with_gate_rules("- P3-test-cases.md 声明 test_code_dir\n"),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3b_card_gate_cmd_not_in_yaml_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 S-3b：卡片 ## gate 规则 含机器可判定命令行但 YAML gates 未声明 → 非 0（md 侧漂移）。
    TDD：P3 现状 S-3b 未实现 → exit 0 → 红灯（B 类）。"""
    root = make_fake_root(
        tmp_path,
        card_text=_card_with_gate_rules("- check-gate.py P2 $TASK_DIR\n"),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3a_s3b_both_sides_consistent_exit_0(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 双侧一致：YAML gates 声明命令串 + 卡片 ## gate 规则 含对应命令行 → exit 0
    （S-3a/S-3b 同时通过）。回归守卫：P3 现状即 exit 0（无 S-3a/b）；P4 实现后双侧一致仍 exit 0。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_p2_gate_cmd(),
        card_text=_card_with_gate_rules(
            "- check-gate.py P2 $TASK_DIR\n- P2-review.md status == approved\n"
        ),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output
