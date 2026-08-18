> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对照 P0-P6 全部产出做跨文件一致性审查，产出 P7-consistency.md。本任务预期是"低摩擦"一致性检查
（P4/P6 均未出现 DESIGN_GAP/SCOPE+/NEED_CONFIRM），但**仍需逐项实质核查，不能因为预期干净就走
过场**——你的价值恰恰是在"看起来都对"的地方找出真正的不一致。

### 约束

1. **DESIGN_GAP 配对**：P4-implementation.md 自报 0 条 DESIGN_GAP——**独立核实**这个自报是否属实
   （grep 全部改动文件确认无遗漏的 `[DESIGN_GAP:` 标记），不要直接采信"0 条"的自述。
2. **SCOPE+ 闭环**：P1-requirements.md 第 2 节有 1 条 `[SUGGEST: 同类扫描不追溯历史产出]`（已被
   主 Agent 采纳，非 SCOPE+），P4 报告 0 条 SCOPE+。同样独立核实（grep `[SCOPE+]`）。
3. **跨文件数量一致性**：
   - P1 BDD 总数（23 条：BDD-1~22 + BDD-15b）与 P6 pass+fail 总数（23）是否一致——**不只对数字**，
     抽查至少 3-5 条 BDD 编号确认 P6 里对应的确实是同一条 BDD 的验收结果（不是编号错位）
   - P2 declares `packages: [phase-cards, dispatch-protocol, state-machine, execution-roles,
     templates, scripts]` 与 P4-implementation.md 实际改动的文件所属类别是否吻合（本任务 P8
     尚未执行，无法核对"P8 bump 范围"，这一项在本次 P7 标注"待 P8 核对"而非强行判定）
   - P4 实现路径（12 个文件）与 P2-design.md §2.1 改动落点表（13 行，含 1 行是 P3 测试文件不算
     P4 改动）是否吻合，逐行核对无遗漏无多余
4. **未决项清零**：grep 全部任务文件确认无残留行首 `[NEED_CONFIRM]`、`[BLOCKER]`、
   `[DEVIATION-CRITICAL]`。
5. **本任务的特殊背景**：本任务本身是"agate 协议机制增强批"，其中一条 RM-AG0013 正是"补齐同类
   扫描/影响面梳理机制"——P7 一致性检查是这套新机制在真实任务里最后一次被验证的机会（P0 同类
   预判 → P1 同类扫描 → P2 影响面梳理 → 这里 P7 是最后的交叉核对）。核查时可以顺带确认：本任务
   自己在 P1-P4 各阶段是否真的做到了"同类扫描"（P1-requirements.md 第 0 节 + P2-design.md 第 0
   节已有相关记录），这不是新增检查项，只是提醒你查阅时留意这条线索的自洽性。
6. **SELF-GATE 语义对齐审查**：`docs/reviews/agate-alignment-review-TAG0012.md`（P4 阶段产出）
   已对 A1-A7 做过独立审查，A4/A7 的 NEEDS_HUMAN_REVIEW 已由主 Agent 附 `[HUMAN_CONFIRMED: ...]`
   裁决——P7 不需要重复这项审查，但可以核实这两条 HUMAN_CONFIRMED 裁决本身是否与 P1-P2 的设计
   文档口径一致（不引入新的不一致）。

### 上游关联

- P1-requirements.md（approved，23 条 BDD，`[NO_NEED_CONFIRM]`）
- P2-design.md（approved，`candidate_count: 3`，13 行改动落点表）
- P4-implementation.md（0 DESIGN_GAP，0 SCOPE+，12 个改动文件）
- P6-acceptance.md（23 pass / 0 fail，逐条语义证据在 P6-evidence/）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P0-brief.md
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P4-implementation.md
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P6-acceptance.md（+ P6-evidence/ 按需抽查）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P7

路径：phase-cards/P7-consistency.md
---
# P7 — 一致性检查

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P7 + 源文件数 ≤5 + 无 implicit_coupling + 有 coupling_checklist（须列出至少 2 个已检查的耦合点，空清单不合规）→ 跳过，读 P8 卡片
> ⑨ P7 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 consistency-reviewer subagent 执行交叉检查
   1.1 写 P7-dispatch-context-consistency-reviewer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 对照 P1-P6 产出做跨文件一致性审查
3. 产出 P7-consistency.md
4. 预跑 check-gate.py P7
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P7，不要提前写 P8——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P7): {摘要}"（phase=P7，P7 产出含 P7-consistency.md）
7. P7 commit 完成后进入 P8：**phase 推进 P8 随 P8 产出 commit 一起**（P8-release.md 就绪后），不是单独 phase commit

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P7 MAX=2）

## 前置条件

- [ ] P1-P6 全部产出文件就绪

## 执行方式

consistency-reviewer subagent 执行。检查清单：

1. **DESIGN_GAP 配对**：P4-implementation.md 中的 DESIGN_GAP 声明 → 必须在 P7-consistency.md 中逐条转抄 + 配 REVIEWED 标记。未配对 → gate 不通过
2. **SCOPE+ 闭环**：P1-requirements.md 有 [SCOPE_RESOLVED] 标记，确认所有 SCOPE+ 增补已纳入基线
3. **跨文件一致性**：P2 声明的 packages 与 P8 release 的 bump 范围一致？P1 的 BDD 和 P6 的验收结果数量匹配？P4 的实现路径和 P2 的方案设计吻合？
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]（P6 不再有 NEED_CONFIRM）、[BLOCKER]、[DEVIATION-CRITICAL]

## 实质锚点要求（N3⑨）

| gate 断言 | 实质锚点（P7 产出须包含） |
|-----------|--------------------------|
| BLOCKER=0 | DESIGN_GAP 配对项 + REVIEWED 标记 |
| CRITICAL=0 | 跨文件检查项 + 源文件节名 |
| SCOPE+ 闭环 | 条目 + SCOPE_RESOLVED |

gate 脚本校验说明：
- DESIGN_GAP_REVIEWED：P4 声明的每条 DESIGN_GAP 在 P7 产出中须有对应行含 `DESIGN_GAP_REVIEWED`
- 跨文件引用关键词：P7 产出中须含源文件节名（如 `P2§packages`、`P4§impl-path`），否则 WARNING

## 产出规格

- P7-consistency.md：一致性审查结论
- 逐条检查结果，无 [BLOCKER] 标记

`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/
`design_gap_reviewed_count` 写在文件头 **frontmatter**（`---` 分隔块），不写正文；正文
`[BLOCKER]`/`[DEVIATION-CRITICAL]`/`[DESIGN_GAP]`/`[DESIGN_GAP_REVIEWED]` 散文标记保留为
人类痕迹（不迁移），gate 判定改读 frontmatter 结构化计数。**可直接复制的完整样例**：
```yaml
---
phase: P7
task_id: TAG0001           # 替换为实际任务编号
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260101 # {task_id}-P7-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0                  # int ≥0
deviation_count: 0                # int ≥0
deviation_critical_count: 0       # int ≥0
design_gap_count: 0                # int ≥0
design_gap_reviewed_count: 0       # int ≥0
---
```

## gate 规则

```bash
check-gate.py P7 $TASK_DIR
```

- [BLOCKER] 存在 → exit 1
- [DEVIATION-CRITICAL] 存在 → exit 1
- DESIGN_GAP 未配对（P4 有但 P7 无 REVIEWED）→ exit 1
- 含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING（不改变 exit code）
- 全部通过 → exit 0

BLOCKER → consistency-reviewer 修改 → 再验 gate → … → 通过（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 推进条件（全部满足才写 phase: P8）

- [ ] P7-consistency.md 存在
- [ ] 无 [BLOCKER] / [DEVIATION-CRITICAL]
- [ ] DESIGN_GAP 全部 REVIEWED 配对
- [ ] SCOPE+ 闭环（P1 有 [SCOPE_RESOLVED]）

## P7 输入文件数量

P7 是输入文件数量限制的例外（模式 1 单发 + 输入数量豁免特例，见 dispatch-protocol「派发编排机制」全阶段适用表），不拆分。原因：
1. 跨文件一致性比较需要全部源文件同时可见
2. 角色文件（consistency-reviewer）已列出所需输入清单
3. dispatch-context 为 subagent 提供摘要，无需逐文件全文注入

## 常见错误

1. **漏转抄 P4 的 DESIGN_GAP**：P4 implementer 声明了实现偏差但 P7 没转抄 → gate 拦截
2. **一致性检查只看标题不对内容**：P1 BDD 数 = 15，P6 PASS 数 = 15 → 数量对，但 BDD-8 的内容在 P6 里被映射到错误的验收结果
3. **裸 'BLOCKER=0' 不引用锚点**：未做实质交叉检查，只写 '一致' → gate WARNING 提醒

gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P8 发布前最后一道质量门——P7 通过后进入机械发布步骤

> 完成 → 读 phase-cards/P8-release.md
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree HEAD 已含 P6 commit（103107d），P0-P6 全部产出文件均已落盘。
- P4/P6 自报：DESIGN_GAP=0，SCOPE+=0，P6 pass=23/fail=0。P7 需独立核实这些自报，不直接采信。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
