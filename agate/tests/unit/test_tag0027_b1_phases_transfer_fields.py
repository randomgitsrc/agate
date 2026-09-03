# agate/tests/unit/test_tag0027_b1_phases_transfer_fields.py — TAG0027 B1 批：转移表结构化（BDD-1/2/3/5）
#
# 被测契约（P2-design §3.1 定案 D1-A + P1-requirements BDD-1/2/3/5）：
#   BDD-1  phases.yaml 主线阶段（P0-P8，不含 P6.5 独立条目）新增 `next` 与 `retreat` 键；
#          P8 next/retreat 值域含 null；schema items.properties 同步声明两键
#          （additionalProperties:false 现状下不同步 = S-5 ERROR）
#   BDD-2  P6.5 条目按 state-machine.md:74-78 口径建模（gate_subphase: hosted_on/forward_to/
#          needs_revision_to），不写 next/retreat —— P6.5 不出现指向独立后继 phase 的主线转移边
#   BDD-3  表内 retreat 值域与 state-machine.md 一致：P5.retreat==P4（:132）、P6.retreat==P4
#          （:148 diff=2 亦写表内值，机械落地由 retreat-to 逐阶）；P6.5 needs_revision_to==P6
#          （:151-157）；"跨 ≥2 阶回退 = 强制 PAUSED"由 check-state-transition 拦截不入表
#   BDD-5  新增字段后 worktree 版 check-protocol-consistency 0 ERROR（回归守卫：既有消费方
#          next-card M3 / S-3/S-4 读取不被破坏）
#
# TDD 红灯语义：P3 现状 phases.yaml/schema 无 next/retreat/gate_subphase → 断言失败 = B 类
#   真红灯（数据面字段未实现）；BDD-5 回归守卫现状即绿（P4 不得破坏）。
# 平台无关：文本 I/O 显式 utf-8；无 /tmp（仅 pytest tmp_path/agate_root fixture）。

import json

import pytest
import yaml


def _load_phases(agate_root):
    """读 worktree agate/rules/phases.yaml → phases 列表（id → dict）。"""
    path = agate_root / "rules" / "phases.yaml"
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict) and isinstance(data.get("phases"), list), "phases.yaml 结构异常"
    by_id = {}
    for p in data["phases"]:
        if isinstance(p, dict) and p.get("id"):
            by_id[str(p["id"])] = p
    return by_id


def _load_schema(agate_root):
    """读 worktree agate/rules/schema/phases.schema.json → dict。"""
    path = agate_root / "rules" / "schema" / "phases.schema.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


_MAINLINE_IDS = ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8")


def test_bdd_1_phases_mainline_next_retreat_keys_present(agate_root):
    """BDD-1：9 个主线阶段（P0-P8，不含 P6.5）每条目均含 next 与 retreat 两键；P8 无后继例外用 null。"""
    phases = _load_phases(agate_root)
    assert "P6.5" in phases, "P6.5 条目缺失（数据面现状异常）"
    for pid in _MAINLINE_IDS:
        assert pid in phases, f"主线阶段 {pid} 缺失"
        entry = phases[pid]
        assert "next" in entry, f"phase {pid} 缺 next 键（P2 §3.1 D1-A 未实现）"
        assert "retreat" in entry, f"phase {pid} 缺 retreat 键（P2 §3.1 D1-A 未实现）"
    # P8 无自动后继例外：next/retreat 值域含 null（§3.1：next: null / retreat: null）
    assert phases["P8"].get("next") is None, "P8.next 应为 null（无自动后继）"
    assert phases["P8"].get("retreat") is None, "P8.retreat 应为 null（失败重试本阶段）"


def test_bdd_1_phases_schema_declares_next_retreat(agate_root):
    """BDD-1：phases.schema.json items.properties 声明 next/retreat（否则 additionalProperties:false 拦 S-5）。"""
    schema = _load_schema(agate_root)
    items = schema["properties"]["phases"]["items"]
    props = items.get("properties", {})
    assert "next" in props, "schema items.properties 未声明 next（P4 B1 须补，否则 S-5 ERROR）"
    assert "retreat" in props, "schema items.properties 未声明 retreat（P4 B1 须补，否则 S-5 ERROR）"


def test_bdd_2_p65_gate_subphase_not_independent_edge(agate_root):
    """BDD-2：P6.5 用 gate_subphase（hosted_on/forward_to/needs_revision_to）表达，不写 next/retreat。"""
    phases = _load_phases(agate_root)
    p65 = phases["P6.5"]
    sub = p65.get("gate_subphase")
    assert isinstance(sub, dict), "P6.5 缺 gate_subphase（非独立 phase 值口径，state-machine.md:74-78）"
    assert sub.get("hosted_on") == "P6", "gate_subphase.hosted_on 应为 P6（.state.yaml phase 保持 P6 至 P7）"
    assert sub.get("forward_to") == "P7", "gate_subphase.forward_to 应为 P7（judge 通过）"
    assert sub.get("needs_revision_to") == "P6", "gate_subphase.needs_revision_to 应为 P6（needs-revision 回退）"
    assert "next" not in p65, "P6.5 不得写 next（非独立转移边，BDD-2 直接 FAIL）"
    assert "retreat" not in p65, "P6.5 不得写 retreat（非独立转移边，BDD-2 直接 FAIL）"


def test_bdd_3_retreat_targets_match_state_machine(agate_root):
    """BDD-3：表内 retreat 值域与 state-machine.md 一致（P5→P4 / P6→P4 / P6.5 needs_revision→P6）。"""
    phases = _load_phases(agate_root)
    # state-machine.md:132 P5 gate 失败 → P4（diff=1）；:148 P6 失败 → P4（diff=2 表内值，
    # 机械落地由 agate-retreat-to 逐阶 P6→P5→P4，CLI 不预判 diff）
    assert phases["P5"].get("retreat") == "P4", "P5.retreat 应为 P4（state-machine.md:132）"
    assert phases["P6"].get("retreat") == "P4", "P6.retreat 应为 P4（state-machine.md:148）"
    # P6.5 needs-revision → P6（state-machine.md:151-157）
    assert phases["P6.5"]["gate_subphase"].get("needs_revision_to") == "P6"
    # P5.next 指向 P6（主线相邻推进）
    assert phases["P5"].get("next") == "P6", "P5.next 应为 P6（主线推进）"
    assert phases["P6"].get("next") == "P7", "P6.next 应为 P7（值域合法；推进为条件式由 CLI 消费）"


# ── BDD-26（exit2fix，CRITICAL-1 修正）：每条目声明 gate_pass_exit 且与 gate 真实出口码一致 ──
# P2 §3.1 实证（check-gate.py gate_p* return）：P0-P3/P5/P6/P8=2、P4/P7/P6.5=0。
_MAINLINE_PASS_EXIT = {
    "P0": 2, "P1": 2, "P2": 2, "P3": 2, "P4": 0, "P5": 2,
    "P6": 2, "P7": 0, "P8": 2,
}


def test_bdd_26_all_entries_declare_gate_pass_exit(agate_root):
    """BDD-26：全部阶段条目（P0-P8 主线 + P6.5）均含 gate_pass_exit 键，值 ∈ {0, 2}。"""
    phases = _load_phases(agate_root)
    for pid in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P6.5", "P7", "P8"):
        assert pid in phases, f"阶段 {pid} 缺失"
        entry = phases[pid]
        assert "gate_pass_exit" in entry, f"phase {pid} 缺 gate_pass_exit 键（BDD-26）"
        assert entry["gate_pass_exit"] in (0, 2), (
            f"phase {pid} gate_pass_exit 应为 0 或 2，实际 {entry['gate_pass_exit']!r}"
        )


def test_bdd_26_gate_pass_exit_matches_check_gate_return(
    agate_root, task_dir, python_exe, run_cli
):
    """BDD-26：每 phase 的 gate_pass_exit 与其 check-gate gate_p* 真实通过出口码一致
    （P2 §3.1 实证表：P0-P3/P5/P6/P8=2、P4/P7/P6.5=0）。数据面真值断言全表 + 真实 gate
    抽跑对照（P5 无 baseline 恒 exit 2、P6.5 judge 未启用早退 exit 0 两条真实通过路径）。"""
    phases = _load_phases(agate_root)
    # 数据面真值：与 P2 §3.1 实证表逐项一致
    for pid, expected in _MAINLINE_PASS_EXIT.items():
        assert phases[pid]["gate_pass_exit"] == expected, (
            f"phase {pid} gate_pass_exit={phases[pid]['gate_pass_exit']} != 实证 {expected}（BDD-26）"
        )
    assert phases["P6.5"]["gate_pass_exit"] == 0, "P6.5 gate_pass_exit 应为 0（judge 通过码）"
    # 真实 gate 抽跑对照：P5 通过路径（无 baseline → gate_p5 return 2）== pass_exit 2
    td = task_dir()
    (td / "P2-design.md").write_text("---\nagent: test\n---\n# P2 design\n", encoding="utf-8")
    r5 = run_cli(python_exe, str(agate_root / "scripts" / "check-gate.py"), "P5", str(td))
    assert r5.returncode == phases["P5"]["gate_pass_exit"] == 2, (
        f"check-gate P5 通过出口码 {r5.returncode} != gate_pass_exit 2（BDD-26）"
    )
    # P6.5 judge 未启用（task_dir 默认无 judge 块）→ gate_p65 早退 return 0 == pass_exit 0
    r65 = run_cli(python_exe, str(agate_root / "scripts" / "check-gate.py"), "P6.5", str(td))
    assert r65.returncode == phases["P6.5"]["gate_pass_exit"] == 0, (
        f"check-gate P6.5 通过出口码 {r65.returncode} != gate_pass_exit 0（BDD-26）"
    )
    # P7 通过路径（task_dir 干净 P7-consistency.md）→ gate_p7 return 0 == pass_exit 0
    r7 = run_cli(python_exe, str(agate_root / "scripts" / "check-gate.py"), "P7", str(td))
    assert r7.returncode == phases["P7"]["gate_pass_exit"] == 0, (
        f"check-gate P7 通过出口码 {r7.returncode} != gate_pass_exit 0（BDD-26）"
    )


def test_bdd_5_consistency_worktree_still_green_regression(agate_root, python_exe, run_cli):
    """BDD-5 回归守卫：worktree 版 check-protocol-consistency.py --strict-errors-only exit 0
    （P4 加字段后既有 WARNING 口径不变，S-3/S-4/next-card M3 不被破坏）。"""
    script = agate_root / "scripts" / "check-protocol-consistency.py"
    if not script.is_file():
        pytest.skip("worktree check-protocol-consistency.py 缺失（测试环境异常）")
    result = run_cli(
        python_exe, str(script), "--strict-errors-only", cwd=str(agate_root.parent)
    )
    assert result.returncode == 0, f"协议一致性回归被破坏：{result.output[:2000]}"
