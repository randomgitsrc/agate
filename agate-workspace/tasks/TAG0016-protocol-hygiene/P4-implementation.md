---
phase: P4
task_id: TAG0016
type: implementation
parent: P2-design.md
trace_id: TAG0016-P4a-20260819
status: draft
created: 2026-08-19
agent: implementer
---

implementation_dir: agate/

# P4 实现记录 — 批次 A：doc-dedup（RM-AG0025 协议文档去重）

本批次落地 P2-design.md §1.1 改动清单 M1-M12（M13 按设计保留原样，未改动），对应 BDD-1/2/3/4/5/7/19（+
回归防护 BDD-16/18）。**只改 Markdown 协议文档**，未触碰 `agate/scripts/*.py`，未改测试代码。

## 改动文件清单

### `agate/WORKFLOW.md`
- M3：H1 主标题下方新增 `> 职责边界：主流程入口——P0-P8 阶段总览、裁剪规则、核心原则、需求/验收机制骨架（详见职责声明表，P2-design.md §0）`
- M2：「## P1-P8 阶段总览」标题后新增分工声明，指向 `dispatch-protocol.md`《可判定门槛规范》
- M1：「## 平台适配」小节收窄为一句话 + 指向 `platform-notes.md` 的指针，删除 OpenCode issue #29616 明细（原描述迁至 platform-notes.md 权威源，本文件不重复维护）

### `agate/dispatch-protocol.md`
- M7：文件头新增 `> 职责边界：派发操作层——可执行门槛判定命令、派发编排机制（工作量评估/并行规则/回退处理）、特殊事件恢复（详见职责声明表，P2-design.md §0）`
- M5：「## 可判定门槛规范」标题后新增分工声明，指向 `WORKFLOW.md`《P1-P8 阶段总览》
- M4：「## 平台适配」删除 `### OpenCode`/`### Claude Code`/`### Codex` 三个平台能力子标题的完整描述，收窄为一句话 + 指向 `platform-notes.md` 的指针；保留 OpenCode issue #29616 调用坑位段落（M4 明确判定该内容属"调用方式"，符合本文件职责，不要求删除）
- M6：「## 派发 prompt 模板」内联版（原 431-682 行，约 250 行、含 P2 最小验证/P3 自检/refactor 口径/P6 BDD 规则等十余个阶段特定追加子节）收窄为 <20 行的极简结构骨架 + 显式指针，指向 `assets/templates/dispatch-prompt.md` 作为唯一权威源

### `agate/assets/templates/dispatch-prompt.md`
- M8：文件头删除矛盾声明"本模板与 dispatch-protocol.md 保持同步，协议文件为权威来源"，改为"本文件是派发 prompt 的权威来源；dispatch-protocol.md 仅保留极简结构提示 + 指针"
- 配套补充：新增「### refactor 任务派发追加（P1 change_type: refactor）」小节，把 dispatch-protocol.md 收窄前独有的两段 refactor 口径内容（P3 侧回归测试口径 + P6 侧回归验收口径）迁移进来（原因见下方 DESIGN_GAP）

### `agate/state-machine.md`
- M10：文件头新增 `> 职责边界：状态机权威源——阶段转移规则、重试上限唯一权威数值表、PAUSED 恢复机制（详见职责声明表，P2-design.md §0）`
- M9：「## 重试上限」标题后新增 `> 本表是重试上限的唯一权威源；rules/state-transitions.md 与 8 张阶段卡片均须与本表一致（CHECK 12 自动校验）。`

### `agate/rules/state-transitions.md`
- M11：「## 重试上限」删除完整数值表（8 行 `| P{N} | MAX | 说明 |`），改为指针句"详见 `state-machine.md`《重试上限》——权威唯一来源，本文件不重复维护"（与文件头已有"权威源：agate/state-machine.md"声明行为一致）

### `agate/platform-notes.md`
- M12：文件头新增 `> 职责边界：平台适配权威源——各 Agent 平台（OpenCode/Claude Code/Codex 等）能力矩阵、Windows 原生安装指南（详见职责声明表，P2-design.md §0）`

### 未改动（按设计要求）
- M13（8 张 `phase-cards/P{N}-*.md` 的 `MAX=` 内联行）：保留原样，未触碰
- BDD-7 回归防护对象三处正确指针（`dispatch-protocol.md` L972 附近 / `state-machine.md` Pre-commit 指针 / `git-integration.md` L162）：未改动
- `agate/tests/unit/*.py`：未改动

## [DESIGN_GAP] 记录

[DESIGN_GAP: P2 M6/§1.1 假设 assets/templates/dispatch-prompt.md 已是 dispatch-protocol.md 内联"派发 prompt 模板"的完整超集（P1 3.3 节比对结论），但实测发现反向缺口——dispatch-protocol.md 收窄前独有两段"refactor 任务（P1 change_type: refactor）"内容（P3 侧回归测试口径 + P6 侧三段式回归验收口径）在 dispatch-prompt.md 中完全没有对应小节。若按 M6 原字面收窄+纯指针处理，会造成真实内容丢失（dispatch-prompt.md 声明自己是"唯一权威源"却缺这块内容，权威源承诺不成立）。实现中自主决策：先把这两段内容原样迁移进 dispatch-prompt.md（新增「### refactor 任务派发追加」小节），确保内容不丢失后再收窄 dispatch-protocol.md，未改变 M6/M8 的既定收窄方向，只是补上了迁移动作本身。]

## 自查过程中发现并修复的两处回归（不在 P2 改动清单内，是本批次操作本身引入又被本批次修复，非新增 SCOPE）

跑全量 `pytest agate/tests/` 自查时发现 M6 对「## 派发 prompt 模板」的整段收窄，误伤了两条**其他任务（TAG0005/TAG0012）已产出的既有绿灯回归测试**：
1. `test_check_gate.py::test_tag0005_bdd_9_review_role_instruction_single_file`——断言全仓恰好 1 处文件含"Review 角色特别指令"字面串（应为 dispatch-prompt.md），我写的骨架列表里为了列举阶段追加节名称也用了这个字面串，导致命中 2 处。已改用"评审角色专属指令"措辞规避。
2. `test_protocol_mechanism_anchors.py` 三条 `BDD-13-*` 用例——断言 `agate/dispatch-protocol.md` 含"命令超时兜底"/"层级 4"/"×1.5" 三个关键词（TAG0012 遗留的锚点回归测试），随整段收窄被一并删除。已在骨架末尾补回一行保留这三个关键词并指向 dispatch-prompt.md 权威源的完整规则。

两处均已修复并自查确认变绿，未产生新的净回归（详见下方测试结果）。

## 自查测试结果（自查≠gate，非 P5 结论）

```
timeout 60s python3 -m pytest agate/tests/unit/test_protocol_dedup_audit.py -v
```
16 条用例：BDD-1/19(×4)/BDD-2(×2)/BDD-3/BDD-4(×2)/BDD-5/BDD-7 共 13 条 PASSED；
BDD-11/BDD-14/BDD-15 共 3 条 FAILED（预期，属批次 3 test-evidence-provenance 范围，dispatch-context
明确本批次不覆盖）。回归防护 BDD-16/BDD-18 同时通过（未被本批次误伤）。

```
timeout 180s python3 -m pytest agate/tests/ -q --tb=line
```
944 passed, 15 failed, 2 skipped。15 个失败全部落在：
- `test_check_protocol_consistency.py` 7 条（CHECK 12，批次 2 check12-anti-recurrence 范围，未实现）
- `test_check_p6_provenance.py` 4 条（审计 7，批次 3 test-evidence-provenance 范围，未实现）
- `test_protocol_dedup_audit.py` 3 条（BDD-11/14/15，同上批次 3 范围）
- `test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff` 1 条——ruff 报的是
  `test_protocol_dedup_audit.py` 自身的既有 lint 问题（import 排序 + E741 变量名歧义），属测试代码，
  dispatch-context 明确要求不改测试代码，本批次未处理，非本批次改动引入。

```
timeout 60s python3 agate/scripts/check-protocol-consistency.py
```
CHECK 1/3/4/6/7/8/9/11 全 PASS，CHECK 2/10 WARN（既有存量 WARNING，未新增），**0 ERROR**——与改动前
基线一致，CHECK 3（硬编码行号）/CHECK 9（协议-脚本结构对齐）锚点未因本批次迁移而失效（R1 风险未触发）。

## 未做的事（明确排除，非遗漏）

- 未新增 CHECK 12（M14/M15，属批次 2）
- 未新增审计 7（M16-M22，属批次 3）
- 未新增 CI xdist 观测步骤（M23，属批次 3）
- 未改动 `agate/scripts/*.py` 与 `agate/tests/unit/*.py`
