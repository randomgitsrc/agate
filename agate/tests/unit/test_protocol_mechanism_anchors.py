# tests/unit/test_protocol_mechanism_anchors.py — 协议机制增强批（TAG0012）grep 断言审计测试
#
# 背景：TAG0012（RM-AG0013/RM-AG0014/RM-AG0019/RM-AG0016）是纯协议文档 + 少量脚本 schema
# 改动批次。P1-requirements.md 的 23 条 BDD（BDD-1~22 + BDD-15b）性质特殊——不是常规业务功能
# 断言，而是"协议文档/角色文件是否含特定新增小节/关键词"的存在性断言。
#
# 组织方式参照 agate/tests/unit/test_check_protocol_consistency.py 的范式（P2-design.md §3.6
# 已指定），但本测试更简单：不需要 importlib 加载脚本模块，只需要直接读文件文本 + 关键词
# `in` 判断。平台无关（纯文本判断，不依赖 shell/grep 二进制），覆盖 windows_smoke 标记。
#
# 关键词锚点来源：P2-design.md §2.1 改动落点表最后一列，逐字复用（不意译/改写），因为
# P4 implementer 落地协议文档改动时也必须逐字使用同一批词（P2-design.md §3.5）。
#
# 此时（P3 阶段）协议文件尚未被本任务改动，全部用例当前必须失败（红灯）——这是本任务的
# TDD 证据。P4 逐条落地后，本测试对应用例转绿。
#
# BDD-5 特别说明：P2-design.md §2.1 表给 BDD-5（P1-requirements.md 卡片新增 verification_env
# vs supplementable 边界判断树）列出两个关键词锚点 `verification_env`、`supplementable`。
# 核实发现 `supplementable` 当前已在 agate/phase-cards/P1-requirements.md 中出现 2 次（既有
# capability_requirements 三态说明，与 BDD-5 要新增的边界判断树无关）——若按"每个关键词独立
# 断言"处理，`supplementable` 那一条会当前即为真（假绿）。因此 BDD-5 改为单条用例、AND 语义
# 同时要求两个关键词都出现（`verification_env` 当前 0 命中，故整体断言现在为假，真红灯成立），
# 两个关键词仍逐字保留、未意译（详见 P3-test-cases.md）。
#
# BDD-22（check-gate.py 是否扩展 timeout_seconds 校验）：P2-design.md §3.7 已决定"不做脚本
# 硬校验，仅文档约定 + 本 grep 断言审计测试"分支。BDD-22 自身以"本测试文件存在 + 全部用例
# 可运行（此刻全红）"为验收标准（dispatch-context 约束 4），不设独立关键词断言。

from pathlib import Path

import pytest

# ANCHOR_CASES: (test_id, file_path, keywords)
#   test_id   — 追溯到 P1-requirements.md 的 BDD 编号；一个 BDD 若在 P2-design.md §2.1 表中
#               对应多个独立关键词锚点，拆成同一 BDD 编号下的多条子用例（id 加锚点后缀区分），
#               仍可逐条追溯回同一个 BDD。
#   file_path — 相对仓库根（worktree 根，agate/ 的父目录）的路径，与 P2-design.md §2.1 表的
#               路径写法一致，不做任何改写。
#   keywords  — 该用例要求同时出现（AND 语义）的关键词元组；绝大多数用例只有 1 个关键词，
#               BDD-5 用例例外（见文件头说明）。
ANCHOR_CASES = [
    # 文件分组 A：agate/phase-cards/P0-orchestrator.md（RM-AG0013 + RM-AG0019）
    ("BDD-1", "agate/phase-cards/P0-orchestrator.md", ("同类/影响面预判",)),
    ("BDD-2", "agate/phase-cards/P0-orchestrator.md", ("[P0_STALE]",)),
    # 文件分组 B：agate/state-machine.md（RM-AG0019）
    ("BDD-3", "agate/state-machine.md", ("时效性校验",)),
    # 文件分组 C：agate/phase-cards/P1-requirements.md 卡片（RM-AG0013 + RM-AG0014 + RM-AG0019）
    ("BDD-4", "agate/phase-cards/P1-requirements.md", ("同类扫描",)),
    ("BDD-5", "agate/phase-cards/P1-requirements.md", ("verification_env", "supplementable")),
    ("BDD-6", "agate/phase-cards/P1-requirements.md", ("[P0_STALE:",)),
    # 文件分组 D：agate/assets/execution-roles/analyst.md（RM-AG0013 + RM-AG0014 + RM-AG0019）
    ("BDD-7", "agate/assets/execution-roles/analyst.md", ("同类/影响面",)),
    ("BDD-8", "agate/assets/execution-roles/analyst.md", ("缺的是能力还是环境",)),
    ("BDD-9", "agate/assets/execution-roles/analyst.md", ("[P0_STALE]",)),
    # 文件分组 E：agate/dispatch-protocol.md（RM-AG0014 + RM-AG0016）
    ("BDD-10-可重试", "agate/dispatch-protocol.md", ("可重试",)),
    ("BDD-10-不可重试", "agate/dispatch-protocol.md", ("不可重试",)),
    ("BDD-10-批处理", "agate/dispatch-protocol.md", ("批处理",)),
    ("BDD-10-止损轮次", "agate/dispatch-protocol.md", ("止损轮次",)),
    ("BDD-11", "agate/dispatch-protocol.md", ("环境准备职责边界",)),
    ("BDD-12", "agate/dispatch-protocol.md", ("资源密集型默认串行",)),
    ("BDD-13-命令超时兜底", "agate/dispatch-protocol.md", ("命令超时兜底",)),
    ("BDD-13-层级4", "agate/dispatch-protocol.md", ("层级 4",)),
    ("BDD-13-倍数", "agate/dispatch-protocol.md", ("×1.5",)),
    # 文件分组 F：agate/assets/templates/dispatch-prompt.md（RM-AG0016，同步 BDD-13）
    ("BDD-14", "agate/assets/templates/dispatch-prompt.md", ("命令超时兜底",)),
    # 文件分组 G：agate/phase-cards/P2-design.md 卡片 + agate/assets/execution-roles/architect.md
    ("BDD-15", "agate/phase-cards/P2-design.md", ("影响面梳理",)),
    ("BDD-15b", "agate/assets/execution-roles/architect.md", ("影响面梳理",)),
    ("BDD-16-P2卡", "agate/phase-cards/P2-design.md", ("timeout_seconds",)),
    ("BDD-16-architect", "agate/assets/execution-roles/architect.md", ("timeout_seconds",)),
    # 文件分组 H：agate/phase-cards/P5-verification.md（RM-AG0016 引用 + RM-AG0014 补充）
    ("BDD-17", "agate/phase-cards/P5-verification.md", ("资源密集型默认串行",)),
    ("BDD-18", "agate/phase-cards/P5-verification.md", ("环境准备职责边界",)),
    # 文件分组 I：agate/phase-cards/P6-acceptance.md + agate/assets/execution-roles/verifier.md
    ("BDD-19", "agate/assets/execution-roles/verifier.md", ("环境准备职责边界",)),
    ("BDD-20", "agate/phase-cards/P6-acceptance.md", ("环境准备职责边界",)),
    # 文件分组 J：agate/assets/templates/task-files.md（RM-AG0016）
    ("BDD-21", "agate/assets/templates/task-files.md", ("timeout_seconds",)),
    # BDD-22（文件分组 K：agate/scripts/check-gate.py）无独立关键词断言，见文件头说明。
]

_IDS = [case[0] for case in ANCHOR_CASES]


@pytest.mark.windows_smoke
@pytest.mark.parametrize("bdd_id,file_path,keywords", ANCHOR_CASES, ids=_IDS)
def test_anchor_present(agate_root, bdd_id, file_path, keywords):
    """每条用例对应 P1-requirements.md 的一个 BDD 编号：目标协议/角色文件须含
    P2-design.md §2.1 表给出的关键词锚点（此刻协议文件尚未被本任务改动，预期全红）。
    """
    repo_root = Path(agate_root).parent
    target = repo_root / file_path
    assert target.is_file(), f"{bdd_id}: 目标文件不存在 {file_path}"

    text = target.read_text(encoding="utf-8")
    missing = [kw for kw in keywords if kw not in text]
    assert not missing, (
        f"{bdd_id}: {file_path} 缺少关键词锚点 {missing}"
        f"（P2-design.md §2.1 改动落点表对应行，须由 P4 逐字落地）"
    )
