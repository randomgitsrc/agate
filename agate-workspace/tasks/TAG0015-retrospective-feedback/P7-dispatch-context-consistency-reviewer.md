> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: consistency-reviewer
retry: 0
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对 P0-P6 全部产出做跨文件一致性审查，产出 P7-consistency.md。这是 P8 发布前最后一道质量门。

### 约束

1. **DESIGN_GAP 配对（强制，本任务恰好有 1 条）**：`P4-implementation.md`「DESIGN_GAP 偏差
   声明」节记录了 1 条 `[DESIGN_GAP: ...]`——P2-design.md §1.1 类 4.1 要求 roadmap.md 三处
   literal 路径字符串"只追加脚注式更正，不删除原叙述"，但物理 git mv 后
   `check-protocol-consistency.py` CHECK 2（`NARRATIVE_DIRS` 白名单不含
   `agate-workspace/roadmap/` 与 `agate/assets/`）会把连续字符串误判为死链 ERROR，implementer
   将其拆成两段非连续字符串规避（内容未删减）。**本条必须在 P7-consistency.md 中逐条转抄
   + 配 `[DESIGN_GAP_REVIEWED]` 标记 + 说明为何接受这个偏差**（提示：SELF-GATE 语义对齐审查
   `docs/reviews/agate-alignment-review-2026-08-19.md`「已知偏离核实」节已独立核实过这条
   DESIGN_GAP 的技术依据成立——CHECK 2 结果确实是 WARN 非 ERROR，可引用复用该核实结论，不需要
   重新查一遍源码，但仍需在本文件里正式配对留痕）。
2. **SCOPE+ 闭环检查**：`grep -n "\[SCOPE+\]" P1-requirements.md agate-workspace/tasks/
   TAG0015-retrospective-feedback/P4-implementation.md` 核实本任务全程未产生 `[SCOPE+]`
   增补（P1-requirements.md 只有 `[NO_NEED_CONFIRM]`，两处 `[SUGGEST:]` 已在正文内被主 Agent
   采纳但那不是 SCOPE+）——若确认无 SCOPE+，在 P7-consistency.md 里显式写"本任务无 SCOPE+
   增补，闭环检查不适用"，不要留空。
3. **跨文件一致性核对（逐项给出源文件节名锚点，不能裸写"一致"）**：
   a. P1 BDD 总数（20）与 P6 PASS 总数（20）+ FAIL 总数（0）核对——引用 `P1-requirements.md
   §4` 与 `P6-acceptance.md` frontmatter `pass:`/`fail:` 字段
   b. P1 §9 `packages:` 声明（6 项：assets/templates/scripts/state-machine/phase-cards/
   docs-reviews-migration/core-protocol-docs）与 P4 实际改动文件（`git show --stat` 该
   commit 或 `P4-implementation.md`「改动文件清单」节）逐项核对是否落在这 6 个包范围内，
   有无遗漏/超出
   c. P2-design.md §1.1 承诺的改动落点（7 类，按 BDD 编号分组）与 P4-implementation.md
   实际交付是否一一对应（引用 `P2-design.md §1.1` 与 `P4-implementation.md`「改动文件清单」）
   d. P4 的 4 项 SELF-GATE 修复（ADR-007 合规/测试断言订正/三处文档同步）是否在 P6 验收里
   有对应体现（如 BDD-17 证据是否用的是订正后的 `agate-feedback.py` 实现）
4. **未决项清零**：`grep -n "\[NEED_CONFIRM\]\|\[BLOCKER\]\|\[DEVIATION-CRITICAL\]"` 逐一核对
   P1-requirements.md、P2-design.md、P4-implementation.md、P6-acceptance.md 均无残留（P1 已
   是 `[NO_NEED_CONFIRM]`，其余文件预期也无这三种标记，需实际 grep 确认而非假设）。
5. **本任务 SELF-GATE 已走过完整流程**（P4 阶段的语义对齐审查，非本 P7 一致性检查的范畴，
   不要重复做——P7 关注的是"P0-P6 产出物之间"的一致性，SELF-GATE 关注的是"协议文档/脚本本身
   与彼此的语义对齐"，两者检查对象不同，P7 不需要重跑 protocol-alignment-review）。

### 输入文件

P7 是输入数量限制的豁免特例（角色文件已列清单），核心需要通读：
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P0-brief.md
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P4-implementation.md（含
  DESIGN_GAP 声明 + SELF-GATE 修复说明）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P6-acceptance.md
- docs/reviews/agate-alignment-review-2026-08-19.md（SELF-GATE 审查报告，供 DESIGN_GAP
  核实交叉引用）

### 门槛（什么算完成）

P7-consistency.md frontmatter：`blocker_count: 0`、`deviation_count`/`deviation_critical_count`
按实际（预期均为 0）、`design_gap_count: 1`、`design_gap_reviewed_count: 1`。正文含
DESIGN_GAP 配对（引用 P4 原文 + REVIEWED 标记 + 理由）、SCOPE+ 闭环声明、4 项跨文件核对
（各带源文件节名锚点）、未决项清零核对。
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
- P4-implementation.md 的 DESIGN_GAP 原文位置：约第 59-69 行「DESIGN_GAP 偏差声明」节。
- P6-acceptance.md frontmatter：`pass: 20`, `fail: 0`, `ui_affected: false`。
- P1-requirements.md frontmatter：`packages: [assets/templates, scripts, state-machine,
  phase-cards, docs-reviews-migration, core-protocol-docs]`。
- 本次是首次进入 P7（retry: 0）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
