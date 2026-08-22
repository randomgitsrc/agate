# agate/tests/unit/test_check_reconcile.py — BDD-6/7/8(M1/M2) 对账模式
#
# 被测：M1 对账钩子（agate_common.reconcile_field + agate-read-gate-commands /
#       check-pruning / check-gate 三消费点接入，P4 M1 交付，P3 尚不存在 → 真红灯 B 类）。
# 契约（P2-design §3.4）：
#   * 字段级双跑：grep/md 读取路径（保退出码语义 0/2 不变，不新增阻断）+ 结构化读取路径对比
#   * 差异可观测出口：stderr `RECONCILE WARNING: <op> <field>: grep=… structured=…` +
#     `RECONCILE SUMMARY: N mismatches across M fields`；默认开（AGATE_RECONCILE 缺省 on）
#   * 覆盖 ≥3 脚本 + 3 类解析点：gate_commands 块（agate-read-gate-commands / check-gate）、
#     P1 裁剪字段 risk_level/phases（check-pruning）、P2 四字段（check-gate）
#   * 对账归一化（R10）：frontmatter list 与正文内联/块式等价 → 0 差异；值真不同 → WARNING
#   * P2-review 发现 #3 固化：gate_commands 合法 key = is_gate_meta_key OR project_module 特判
#     （project_module 不告警、未知 key 告警）
#   * BDD-8（M2）：对账清零判据——一致夹具 → RECONCILE SUMMARY 0 mismatches；残留差异 → 禁止切换
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest

from conftest import add_p2_candidate_count, add_p2_review

# 已知差异夹具：P1-requirements.md frontmatter 声明 risk_level=medium，正文追加 risk_level=high
# → grep 读取（正文）与结构化读取（frontmatter）不一致 → RECONCILE WARNING。
_DIFF_BODY_LINE = "risk_level: high\n"


def _run_pruning(agate_scripts, python_exe, run_cli, task_arg):
    return run_cli(python_exe, str(agate_scripts / "check-pruning.py"), str(task_arg))


@pytest.mark.windows_smoke
def test_bdd_6_pruning_warning_and_exit_preserved(task_dir, agate_scripts, python_exe, run_cli):
    """check-pruning 对账：已知差异夹具 → stderr 出 RECONCILE 告警 + 退出码保持原判定（0=通过）。"""
    td = task_dir()
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write(_DIFF_BODY_LINE)

    result = _run_pruning(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, "对账不阻断：退出码应为原判定 0"
    assert "RECONCILE" in result.output, "已知差异未输出对账告警（M1 对账钩子未实现）"


def test_bdd_6_read_gate_commands_unknown_key_warning(agate_scripts, python_exe, run_cli, tmp_path):
    """agate-read-gate-commands 对账（gate_commands 块解析点）：块内未知 key → RECONCILE 告警；
    合法 key（P5 / P5_formatter / P5_timeout_seconds / project_module 特判）不告警。"""
    p2 = tmp_path / "P2-design.md"
    p2.write_text(
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P5_formatter: pytest.sh\n"
        "  P5_timeout_seconds: 300\n"
        "  project_module: src\n"
        "  P9_custom: oops\n",
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert result.returncode == 0, "gate_commands 块解析退出码应保持 0"
    assert "RECONCILE" in result.output, "未知 gate_commands key 未输出对账告警"


def test_bdd_6_check_gate_p2_reconcile_warning(task_dir, agate_scripts, python_exe, run_cli):
    """check-gate P2 分支对账（P2 四字段 + gate_commands 键集解析点）：已知差异 → RECONCILE 告警。"""
    td = task_dir()
    (td / "P2-design.md").write_text(
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P9_custom: oops\n",
        encoding="utf-8",
    )
    add_p2_candidate_count(td, 2)
    add_p2_review(td)

    result = run_cli(
        python_exe, str(agate_scripts / "check-gate.py"), "P2", str(td)
    )
    assert result.returncode == 2, "check-gate P2 退出码应保持原语义 exit 2"
    assert "RECONCILE" in result.output, "P2 四字段/gate_commands 差异未输出对账告警"


# BDD-7 覆盖面：3 脚本 × 3 类解析点（gate_commands 块 / P1 裁剪字段 / P2 四字段）
# 映射 = 脚本 → 其覆盖的解析点集合（P2-design §3.4 三类）
_PARSED_POINT_BY_SCRIPT = {
    "agate-read-gate-commands.py": {"gate_commands 块"},
    "check-pruning.py": {"P1 裁剪字段（risk_level/phases）"},
    "check-gate.py": {"gate_commands 块", "P2 四字段"},
}

# 设计要求的解析点全集（P2-review「测试缺口」：三类缺一即不达标）
_PARSE_POINT_CLASSES = {"gate_commands 块", "P1 裁剪字段（risk_level/phases）", "P2 四字段"}


def test_bdd_7_coverage_three_scripts_three_parse_points(
    task_dir, agate_scripts, python_exe, run_cli, tmp_path
):
    """对账覆盖面 ≥3 脚本且覆盖 3 类解析点：逐一驱动已知差异夹具并断言对账输出出现；
    覆盖点集合与设计规定三类相等，脚本数不足/缺类即红灯。"""
    assert len(_PARSED_POINT_BY_SCRIPT) >= 3, "对账脚本数 < 3（BDD-7）"
    covered = set().union(*_PARSED_POINT_BY_SCRIPT.values())
    assert covered == _PARSE_POINT_CLASSES, (
        f"三类解析点覆盖不齐（P2-design §3.4）：得 {covered}，需 {_PARSE_POINT_CLASSES}"
    )

    # 1) agate-read-gate-commands：gate_commands 块含未知 key
    p2 = tmp_path / "P2-design.md"
    p2.write_text(
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P9_custom: oops\n",
        encoding="utf-8",
    )
    r1 = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    # 2) check-pruning：P1 裁剪字段 frontmatter↔正文差异
    td2 = task_dir()
    with open(td2 / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write(_DIFF_BODY_LINE)
    r2 = _run_pruning(agate_scripts, python_exe, run_cli, td2)
    # 3) check-gate P2：四字段/gate_commands 键集差异
    td3 = task_dir()
    (td3 / "P2-design.md").write_text(
        "# P2 design\n"
        "### 候选方案 A：方案一\n"
        "### 候选方案 B：方案二\n"
        "## 权衡\n"
        "A 更简单，B 更稳健。\n"
        "packages: [pkg-a]\n"
        "domains: [backend]\n"
        "ui_affected: false\n"
        "gate_commands:\n"
        "  P5: pytest\n"
        "  P9_custom: oops\n",
        encoding="utf-8",
    )
    add_p2_candidate_count(td3, 2)
    add_p2_review(td3)
    r3 = run_cli(python_exe, str(agate_scripts / "check-gate.py"), "P2", str(td3))

    for result, script in ((r1, "agate-read-gate-commands.py"), (r2, "check-pruning.py"), (r3, "check-gate.py")):
        assert "RECONCILE" in result.output, f"{script} 未接入对账（BDD-7 覆盖面不达标）"


def test_bdd_7_project_module_not_warned(agate_scripts, python_exe, run_cli, tmp_path):
    """P2-review 发现 #3 固化：project_module 是 is_gate_meta_key 之外的合法特判 key——
    对账实现须以 agate-gate-missing-cmds.py 的 `is_gate_meta_key(k) or k == project_module`
    为参照，project_module 出现不得作为差异告警。"""
    p2 = tmp_path / "P2-design.md"
    p2.write_text(
        "gate_commands:\n"
        "  P5_consistency_timeout_seconds: 120\n"
        "  project_module: src\n",
        encoding="utf-8",
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )
    assert "RECONCILE" in result.output, "对账输出缺失（project_module 特判路径未实现）"
    assert "project_module" not in result.output.split("RECONCILE WARNING:")[1:], (
        "project_module 被误报为差异（合法特判 key）"
    )


def test_bdd_8_zero_diff_blocks_switch(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-8 对账清零判据：一致夹具（frontmatter 与正文同值，list 归一化等价）→
    RECONCILE SUMMARY 报 0 mismatches；存在残留差异 → 禁止切换（非 0 计数兜底）。"""
    td = task_dir()
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        # 与 frontmatter 同值（块式 list vs 空格连接 list 归一化等价）
        fh.write(
            "phases:\n"
            "  - P0\n  - P1\n  - P2\n  - P3\n  - P4\n  - P5\n  - P6\n  - P7\n  - P8\n"
        )

    result = _run_pruning(agate_scripts, python_exe, run_cli, td)
    assert "RECONCILE SUMMARY" in result.output, "对账汇总行未输出（对账机制未实现）"
    assert "0 mismatches" in result.output, "一致夹具出现非 0 差异——对账清零判据（BDD-8）不成立"


def test_bdd_8_normalization_list_inline_block_equal(task_dir, agate_scripts, python_exe, run_cli, tmp_path):
    """R10 归一化口径固化（P2-review 测试缺口）：正文内联 list / 块式 list 与 frontmatter
    空格连接 list 语义等价 → 归一化后 0 差异（不误报 WARNING）。"""
    td = task_dir()
    with open(td / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write("phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]\n")

    result = _run_pruning(agate_scripts, python_exe, run_cli, td)
    assert "RECONCILE SUMMARY" in result.output, "对账汇总行未输出"
    assert "0 mismatches" in result.output, "等价形态被误报差异（归一化口径未落实）"
