# agate/tests/unit/test_structure_migration.py — BDD-9/10(M2) 切换权威源与 gate 提升阻断
#
# 被测契约（P2-design §3.3/§3.5、M2-1..M2-5）：
#   BDD-9  静态扫描：已迁移解析点（三脚本 + agate-md-field-get 的
#          `^(packages|domains|ui_affected|gate_commands):` 与 `^gate_commands:` 块正则）
#          在 agate/scripts/*.py 中命中数 = 0（P3 当下这些模式仍存在 → 真红灯 B 类；
#          M2 切权威源删除 md 正则后转绿）
#   BDD-10 一致性 gate 提升阻断：check-structure-consistency.py 漂移即 exit 非 0；
#          pre-commit-gate.py 与 CI protocol-tests.yml 均追加该脚本步骤（三处阻断）
#   BDD-11 迁移后回归全绿 → 声明（无新测试，P5 全量回归 + gate_commands.P5_consistency 覆盖）
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest
from _rules_test_utils import DEFAULT_PHASES_YAML, make_fake_root

# 已迁移解析模式（P1 §4.1 B 组 + A 组字段正则；删除后 BDD-9 转绿）。
# 按「模式文本在源码中的字面出现」扫描（M2 前这些文本嵌在 check-gate / read-gate-commands
# 的正则字符串里；M2 删除 md 正则后字面不再出现）。
_MIGRATED_PATTERN_TEXTS = (
    r"^(packages|domains|ui_affected|gate_commands):",  # A 组四字段行正则文本
    r"^gate_commands:[ \t]*\n",  # B 组 gate_commands 块正则文本（5 处同源实现）
)

# 已迁移脚本清单（D3 首批三脚本 + md-field-get hub；SCOPE+2 消费方随 hub 生效）
_MIGRATED_SCRIPTS = (
    "agate-read-gate-commands.py",
    "check-pruning.py",
    "check-gate.py",
    "agate-md-field-get.py",
)


@pytest.mark.windows_smoke
def test_bdd_9_migrated_patterns_zero_hits(agate_scripts):
    """已迁移解析点在 agate/scripts 中命中数 = 0（M2 切权威源后成立；P3 当下必红）。"""
    hits = []
    for name in _MIGRATED_SCRIPTS:
        text = (agate_scripts / name).read_text(encoding="utf-8")
        for pattern_text in _MIGRATED_PATTERN_TEXTS:
            if pattern_text in text:
                hits.append(f"{name} 含 {pattern_text!r}")
    assert hits == [], f"已迁移解析点仍命中 {len(hits)} 处（M2 删除 md 正则后应归零）：{hits}"


def test_bdd_10_script_drift_blocked(agate_scripts, python_exe, run_cli, tmp_path):
    """check-structure-consistency.py 提升阻断：人为 S-1 漂移 → exit 1（--strict-errors-only 常开）。"""
    script = agate_scripts / "check-structure-consistency.py"
    assert script.is_file(), "check-structure-consistency.py 未实现（P4 M0 交付）——TDD 红灯锚点"
    yaml_with_p9 = DEFAULT_PHASES_YAML + (
        "  - id: P9\n"
        "    name: 幽灵阶段\n"
        "    exec_role: verifier\n"
        "    retry_cap: 2\n"
    )
    root = make_fake_root(tmp_path, phases_text=yaml_with_p9)
    result = run_cli(python_exe, str(script), env={"AGATE_ROOT": str(root)})
    assert result.returncode != 0, "S-1 漂移未被阻断（M2 提升阻断未生效）"


def test_bdd_10_precommit_includes_structure_step(agate_root):
    """pre-commit gate 追加 check-structure-consistency.py 独立 step（M2-4，与 check-gate 并列不短路）。"""
    text = (agate_root / "scripts" / "pre-commit-gate.py").read_text(encoding="utf-8")
    assert "check-structure-consistency" in text, (
        "pre-commit-gate.py 未调用 check-structure-consistency.py（M2-4 未实现）"
    )


def test_bdd_10_ci_includes_structure_step(agate_root):
    """CI consistency job 追加 check-structure-consistency.py 步骤（M2-5）。"""
    workflow = agate_root.parent / ".github" / "workflows" / "protocol-tests.yml"
    assert workflow.is_file(), "protocol-tests.yml 缺失"
    text = workflow.read_text(encoding="utf-8")
    assert "check-structure-consistency" in text, (
        "CI workflow 未追加 check-structure-consistency.py 步骤（M2-5 未实现）"
    )
