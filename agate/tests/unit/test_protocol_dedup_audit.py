# tests/unit/test_protocol_dedup_audit.py — TAG0016（RM-AG0025/RM-AG0026）批量机械去重断言审计
#
# 设计依据：P2-design.md §6 说明段 + HANDOFF-TAG0016.md「批量机械改动的 TDD 策略」——批量机械
# 改动（文档去重迁移、职责声明行新增、指针句改写）用一个断言审计测试覆盖多条 BDD，不为每处改动
# 单独写测试。断言对象是"去重后协议文档内容应该长什么样"，直接读取真实 agate/ 协议文档（不用
# fake fixture），对应 P2-design.md §1.1 M1-M23 改动清单尚未落地前，本文件测试当前应全部红灯
# （assertion 失败——B 类：非语法错误/非第三方 import 失败）。
#
# 覆盖范围（BDD 编号 → 测试函数）：
#   BDD-1 / BDD-19  test_bdd_1_19_responsibility_boundary_declared（参数化 4 文件）
#   BDD-2           test_bdd_2_platform_dedup_workflow / test_bdd_2_platform_dedup_dispatch_protocol
#   BDD-3           test_bdd_3_phase_threshold_table_division_of_labor
#   BDD-4           test_bdd_4_dispatch_prompt_single_source_template / _head
#   BDD-5           test_bdd_5_retry_max_pointer_in_state_transitions
#   BDD-6           不在本文件单独覆盖——Then 子句本身是"CHECK 12 报 ERROR"，由
#                   test_check_protocol_consistency.py 的 test_bdd_9_check12_mismatched_inline_max_*
#                   系列覆盖（M13 已声明 8 卡片内联行"保留原样不改"，无去重前后差异可断言）
#   BDD-7           test_bdd_7_precommit_pointers_unchanged（回归防护，预期已绿，不因去重被误伤）
#   BDD-8           不适合自动化（P6 人工抽查"职责定位混乱"段落是否已迁移/被职责表认定合理保留，
#                   属定性语义判断，见 P1 3.7 节）——验证方式：P6 阶段人工核对 WORKFLOW.md/
#                   dispatch-protocol.md 各 ≥1 处曾被认定"职责定位混乱"的段落
#   BDD-9 / BDD-10  见 test_check_protocol_consistency.py（CHECK 12 单测）
#   BDD-11          test_bdd_11_rerun_audit_table_exists
#   BDD-12 / BDD-13 见 test_check_p6_provenance.py（审计 7 单测）
#   BDD-14          test_bdd_14_p8_release_reuse_wording（轻量 grep 断言，非强制但已判断可写）
#   BDD-15          test_bdd_15_ci_xdist_observability_step
#   BDD-16          test_bdd_16_parallel_rule_xdist_judgement_unchanged（回归防护，预期已绿）
#   BDD-17          不在本文件单独覆盖——由 gate_commands.P5 整体校验（pytest 全绿 +
#                   check-protocol-consistency.py --strict 0 ERROR + count-tests.sh 计数一致），
#                   非独立 P3 红灯项，贯穿全任务的元要求
#   BDD-18          不适合自动化（禁止声称"已在 Windows 实测"是文档表述要求，语义判断）——
#                   验证方式：P6/P8 阶段人工核对涉及 Windows 兼容性的结论表述；本文件用
#                   test_bdd_18_platform_notes_windows_section_preserved 做"Windows 原生安装指南
#                   未被去重误删"的回归防护（预期已绿，非 BDD-18 本身的自动化证明）

import re
from pathlib import Path

import pytest

# ── 工具函数 ──────────────────────────────────────────────────────────────


def _read(agate_root, relpath):
    """relpath 相对 agate_root（即仓库 agate/ 子目录本身，fixture 已确认含 scripts/+assets/）。"""
    return (Path(agate_root) / relpath).read_text(encoding="utf-8")


def _repo_root(agate_root):
    """agate_root 的父目录 = 仓库根（.github/ 等仓库级文件的落点）。"""
    return Path(agate_root).parent


def _section(text, heading_pattern, end_pattern=r"^---\s*$"):
    """提取从 heading_pattern（正则，需以 ^ 锚定）匹配行开始，到 end_pattern 匹配行（不含）
    之间的正文（不含标题行本身）。找不到 heading 时返回 None。"""
    m = re.search(heading_pattern + r"\n(.*?)\n" + end_pattern, text, re.M | re.S)
    if m:
        return m.group(1)
    # 退化：没有 end_pattern 分隔时，退到下一个同级 "^## " 标题
    m2 = re.search(heading_pattern, text, re.M)
    if not m2:
        return None
    rest = text[m2.end():]
    m3 = re.search(r"\n^## ", rest, re.M)
    return rest[: m3.start()] if m3 else rest


# ── BDD-1 / BDD-19：职责声明表落地（4 份文件，M3/M7/M10/M12）──────────────

_RESPONSIBILITY_FILES = [
    "WORKFLOW.md",
    "dispatch-protocol.md",
    "state-machine.md",
    "platform-notes.md",
]


@pytest.mark.parametrize("relpath", _RESPONSIBILITY_FILES)
def test_bdd_1_19_responsibility_boundary_declared(agate_root, relpath):
    """BDD-1/BDD-19：4 份文档文件头/主标题附近须含 `> 职责边界：` 声明行
    （P2-design.md §0 职责声明表落地格式；P2-review 第 1 轮指出的测试缺口，本次派发已补）。"""
    text = _read(agate_root, relpath)
    head = "\n".join(text.splitlines()[:20])
    assert "职责边界" in head, (
        f"{relpath} 文件头 20 行内未找到 '职责边界' 声明行（BDD-1/BDD-19 要求 P2 §0 职责声明表"
        f"落地为 `> 职责边界：...` 格式）"
    )


# ── BDD-2：平台适配收敛为单一权威源（M1/M4，platform-notes.md 权威源）──────


def test_bdd_2_platform_dedup_workflow(agate_root):
    """WORKFLOW.md「## 平台适配」应收窄为一句话摘要 + 指向 platform-notes.md 的指针，
    不再独立展开平台坑位描述（如 OpenCode issue #29616 明细）。"""
    text = _read(agate_root, "WORKFLOW.md")
    section = _section(text, r"^## 平台适配")
    assert section is not None, "WORKFLOW.md 未找到 '## 平台适配' 小节"
    assert "issue #29616" not in section, (
        "WORKFLOW.md「平台适配」仍独立展开 OpenCode 坑位明细（应收窄为摘要+指针，权威源见 "
        "platform-notes.md）"
    )
    assert "platform-notes.md" in section, "WORKFLOW.md「平台适配」缺少指向 platform-notes.md 的指针"
    assert ("权威" in section) or ("详见" in section), (
        "WORKFLOW.md「平台适配」缺少指针短语（'权威'/'详见'）"
    )


def test_bdd_2_platform_dedup_dispatch_protocol(agate_root):
    """dispatch-protocol.md「## 平台适配」不应再逐平台独立展开完整描述
    （如 ### Codex 整段小标题），应收窄为摘要 + 指针，OpenCode 调用侧坑位细节可保留
    （M4：属"调用方式"，符合本文件职责，不要求删除）。"""
    text = _read(agate_root, "dispatch-protocol.md")
    section = _section(text, r"^## 平台适配")
    assert section is not None, "dispatch-protocol.md 未找到 '## 平台适配' 小节"
    assert "### Codex" not in section, (
        "dispatch-protocol.md「平台适配」仍逐平台独立展开完整子标题描述（应收窄为摘要+指针）"
    )
    assert "platform-notes.md" in section, (
        "dispatch-protocol.md「平台适配」缺少指向 platform-notes.md 的指针"
    )


# ── BDD-3：阶段门槛表分工声明（M2/M5）────────────────────────────────────


def test_bdd_3_phase_threshold_table_division_of_labor(agate_root):
    """WORKFLOW.md「P1-P8 阶段总览」附近应新增分工声明句，指向 dispatch-protocol.md
    《可判定门槛规范》；反之 dispatch-protocol.md《可判定门槛规范》附近应指回 WORKFLOW.md
    《阶段总览》——两表现有的角色映射颗粒度与可执行命令颗粒度分工须显式声明（BDD-3）。"""
    wf_text = _read(agate_root, "WORKFLOW.md")
    m = re.search(r"^## P1-P8 阶段总览\n(.{0,400})", wf_text, re.M | re.S)
    assert m is not None, "WORKFLOW.md 未找到 '## P1-P8 阶段总览' 标题"
    wf_nearby = m.group(1)
    assert "可判定门槛规范" in wf_nearby and "dispatch-protocol.md" in wf_nearby, (
        "WORKFLOW.md「P1-P8 阶段总览」附近缺少指向 dispatch-protocol.md《可判定门槛规范》的分工声明"
    )

    dp_text = _read(agate_root, "dispatch-protocol.md")
    m2 = re.search(r"^## 可判定门槛规范\n(.{0,400})", dp_text, re.M | re.S)
    assert m2 is not None, "dispatch-protocol.md 未找到 '## 可判定门槛规范' 标题"
    dp_nearby = m2.group(1)
    assert "阶段总览" in dp_nearby and "WORKFLOW.md" in dp_nearby, (
        "dispatch-protocol.md「可判定门槛规范」附近缺少指向 WORKFLOW.md《P1-P8 阶段总览》的分工声明"
    )


# ── BDD-4：派发 prompt 模板单一权威源（M6/M8）────────────────────────────


def test_bdd_4_dispatch_prompt_single_source_template(agate_root):
    """dispatch-protocol.md「## 派发 prompt 模板」内联版应收窄为极简结构提示（骨架），
    不再维护完整模板正文（当前约 250 行完整正文，含全部阶段特定追加节，应收窄为 <30 行）。"""
    text = _read(agate_root, "dispatch-protocol.md")
    section = _section(text, r"^## 派发 prompt 模板")
    assert section is not None, "dispatch-protocol.md 未找到 '## 派发 prompt 模板' 小节"
    line_count = len([line for line in section.splitlines() if line.strip()])
    assert line_count < 30, (
        f"dispatch-protocol.md「派发 prompt 模板」内联版仍有 {line_count} 行非空内容"
        "（应收窄为极简结构骨架 + 指针，权威源见 assets/templates/dispatch-prompt.md）"
    )
    assert "assets/templates/dispatch-prompt.md" in section
    assert ("唯一权威" in section) or ("权威来源" in section) or ("权威源" in section), (
        "dispatch-protocol.md「派发 prompt 模板」缺少明确指向 dispatch-prompt.md 的权威源指针短语"
    )


def test_bdd_4_dispatch_prompt_single_source_head(agate_root):
    """assets/templates/dispatch-prompt.md 文件头应改为声明"本文件是权威来源"，
    删除与 dispatch-protocol.md 互相矛盾的"协议文件为权威来源"旧声明。"""
    text = _read(agate_root, "assets/templates/dispatch-prompt.md")
    head = "\n".join(text.splitlines()[:8])
    assert "协议文件为权威来源" not in head, (
        "dispatch-prompt.md 文件头仍保留旧矛盾声明'协议文件为权威来源'（应改为声明自身是权威来源）"
    )
    assert re.search(r"本文件是.{0,20}权威来源", head), (
        "dispatch-prompt.md 文件头未找到'本文件是...权威来源'声明（BDD-4 要求修正矛盾声明）"
    )


# ── BDD-5：重试上限表单一数值来源（M11）──────────────────────────────────


def test_bdd_5_retry_max_pointer_in_state_transitions(agate_root):
    """rules/state-transitions.md「## 重试上限」不再复制完整数值表，改为指针引用
    state-machine.md（须与文件头已有的"权威源：state-machine.md"声明行为一致）。"""
    text = _read(agate_root, "rules/state-transitions.md")
    section = _section(text, r"^## 重试上限")
    assert section is not None, "rules/state-transitions.md 未找到 '## 重试上限' 小节"
    # 完整表格判定：≥3 组 "| P\d | \d |" 行同时出现即视为仍在复制权威表格
    table_rows = re.findall(r"^\|\s*P\d+\s*\|\s*\d+\s*\|", section, re.M)
    assert len(table_rows) < 3, (
        f"rules/state-transitions.md「重试上限」仍复制了 {len(table_rows)} 行权威数值表"
        "（应改为纯指针句，不再复制数值）"
    )
    assert "state-machine.md" in section
    assert ("权威" in section) or ("详见" in section), (
        "rules/state-transitions.md「重试上限」缺少指向 state-machine.md 的指针短语"
    )


# ── BDD-7：既有正确指针模式不被误伤（回归防护）───────────────────────────


def test_bdd_7_precommit_pointers_unchanged(agate_root):
    """P1 3.4 节已验证的三处 Pre-commit 清单指针（dispatch-protocol.md / state-machine.md /
    git-integration.md）应保持不变，去重方案与防复发 gate 均不误改这三处正确模式。"""
    dp = _read(agate_root, "dispatch-protocol.md")
    assert "WORKFLOW.md" in dp and "Pre-commit" in dp and "权威唯一来源" in dp, (
        "dispatch-protocol.md 的 Pre-commit 指针句被移除或改动（应保持指向 WORKFLOW.md 不变）"
    )
    sm = _read(agate_root, "state-machine.md")
    assert "WORKFLOW.md" in sm and "Pre-commit" in sm and "权威唯一来源" in sm, (
        "state-machine.md 的 Pre-commit 指针句被移除或改动（应保持指向 WORKFLOW.md 不变）"
    )
    gi = _read(agate_root, "git-integration.md")
    assert "WORKFLOW.md" in gi and "Pre-commit" in gi, (
        "git-integration.md 的 Pre-commit 指针句被移除或改动（应保持指向 WORKFLOW.md 不变）"
    )


# ── BDD-11：全量重跑点审计表产出（M16）───────────────────────────────────


def test_bdd_11_rerun_audit_table_exists(agate_root):
    """dispatch-protocol.md 应新增「## 全量重跑点审计」小节，逐点列出 P5 首跑 / P5 失败重跑 /
    P6 refactor 独立 regression.log / P8 bump-version 后重跑四个重跑点。"""
    text = _read(agate_root, "dispatch-protocol.md")
    assert re.search(r"^## 全量重跑点审计", text, re.M), (
        "dispatch-protocol.md 未找到 '## 全量重跑点审计' 小节（M16 落点，BDD-11）"
    )
    section = _section(text, r"^## 全量重跑点审计")
    assert section is not None
    for marker in ("P5 首跑", "P5", "regression.log", "P8"):
        assert marker in section, f"「全量重跑点审计」缺少关键词 '{marker}'"


# ── BDD-14：P8 重跑范围精简的表述变化（轻量 grep 断言）──────────────────


def test_bdd_14_p8_release_reuse_wording(agate_root):
    """P8-release.md「主 Agent 必须亲自执行」重跑 P5 一条应精简为条件化表述：
    无改动时复用同一份 P5-test-results/，而非无条件"重跑 P5 gate"。"""
    text = _read(agate_root, "phase-cards/P8-release.md")
    assert "P5-test-results" in text and ("复用" in text), (
        "P8-release.md 未找到'复用同一份 P5-test-results/'类精简表述（BDD-14 要求 M22 精简重跑范围/"
        "方式，仍保留至少一次客观验证动作，不可整体取消）"
    )


# ── BDD-15：xdist CI 观测步骤（M23）──────────────────────────────────────


def test_bdd_15_ci_xdist_observability_step(agate_root):
    """.github/workflows/protocol-tests.yml 的 pytest job 应新增一个观测性 xdist 步骤
    （记录耗时，不影响 job 整体 pass/fail）。"""
    import yaml

    wf_path = _repo_root(agate_root) / ".github" / "workflows" / "protocol-tests.yml"
    doc = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    steps = doc["jobs"]["pytest"]["steps"]
    xdist_steps = [
        s for s in steps if "-n auto" in (s.get("run") or "")
    ]
    assert len(xdist_steps) >= 1, (
        "protocol-tests.yml 的 pytest job 未找到含 'pytest -n auto' 的观测性步骤（BDD-15/M23）"
    )
    step = xdist_steps[0]
    non_blocking = bool(step.get("continue-on-error")) or "|| true" in (step.get("run") or "")
    assert non_blocking, (
        "新增的 xdist 观测步骤未标记为不影响 job 整体 exit code"
        "（期望 continue-on-error: true 或命令自身吞掉非 0 退出码）"
    )


# ── BDD-16：并行规则 xdist 判据保持不变（回归防护）───────────────────────


def test_bdd_16_parallel_rule_xdist_judgement_unchanged(agate_root):
    """dispatch-protocol.md「并行规则」第 4 条资源密集型判据描述仍须包含 xdist 相关表述，
    不因 M23 新增 CI 观测步骤而放松/删除这条隔离规则。"""
    text = _read(agate_root, "dispatch-protocol.md")
    assert "xdist" in text and "pytest -n auto" in text, (
        "dispatch-protocol.md「并行规则」判据描述中的 xdist/pytest -n auto 表述缺失"
        "（BDD-16 要求该判据保持不变）"
    )


# ── BDD-18：Windows 安装指南未被去重误删（回归防护，非 BDD-18 本身的自动化证明）──


def test_bdd_18_platform_notes_windows_section_preserved(agate_root):
    """platform-notes.md「Windows 原生」章节应在去重后依然保留，指令未被误删/误改
    （BDD-18 要求：若改动触及该章节，须保持现有安装指南步骤的准确性）。"""
    text = _read(agate_root, "platform-notes.md")
    assert re.search(r"^## Windows 原生", text, re.M), (
        "platform-notes.md 未找到 '## Windows 原生' 章节（去重迁移不应触碰/删除本章节）"
    )
