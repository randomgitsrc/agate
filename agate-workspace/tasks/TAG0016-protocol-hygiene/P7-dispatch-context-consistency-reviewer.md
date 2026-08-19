---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

以批判的第三方视角（假设 P2 设计可能有错，不因为"这是我们当初设计的方案"就宽容）对 P1-P6 全部
产出做跨文件一致性检查，产出 P7-consistency.md。

### 约束

1. **DESIGN_GAP 配对（必做）**：`P4-implementation.md` 记录了 1 条 `[DESIGN_GAP:]`（M6 假设
   `dispatch-prompt.md` 是 `dispatch-protocol.md` 内联版完整超集，实测发现反向缺口——refactor
   任务两段内容缺失，implementer 自主决策先迁移再收窄）。**必须**在 P7-consistency.md 中
   逐条转抄该 DESIGN_GAP 原始标记行 + 你的判定结论（`[DESIGN_GAP_REVIEWED: 已确认]` 或
   `[DESIGN_GAP_REVIEWED: 已打回 P2]`）。判定依据：核实 implementer 的自主决策是否合理——
   实际检查 `agate/assets/templates/dispatch-prompt.md` 是否确实新增了「### refactor 任务派发
   追加」小节且内容与原 `dispatch-protocol.md` 收窄前的两段一致，判断这个决策是否需要退回
   P2 补充设计（大概率不需要，这是纯粹的内容迁移动作，不改变既定收窄方向，但你需要自己核实
   而不是直接采信）。
2. **SCOPE+ 闭环**：全仓检索确认本任务**未触发任何 `[SCOPE+]`**（P1-requirements.md §8 显式
   声明"无"，P2/P4 实现记录也未发现新增）。不需要闭环动作，但仍需在 P7-consistency.md 中显式
   写一句"已核对，无 SCOPE+ 需闭环"（空白不算做过）。
3. **跨文件一致性核查重点**：
   - P1 的 19 条 BDD 与 P6 的验收结果数量匹配（P1 `#### BDD-NN` 标题数 vs P6
     `grep -cE '^\s*- (PASS|FAIL)'` 结果数，应均为 19）——不能只看总数一致，抽查几条编号
     确认内容对应正确（如 BDD-12 在 P1 定义的判定标准 vs P6 BDD-12 引用的证据是否真的对应
     同一件事）
   - P2 声明的 `packages`（8 个：workflow/dispatch-protocol/state-machine/platform-notes/
     state-transitions/phase-cards/dispatch-prompt-template/gate-scripts）与 P4 三个批次
     实际改动的文件范围是否吻合（不要求每个 package 都对应实际改了文件——`packages` 是"受影响
     范围声明"，重点是"P4 是否有超出 packages 声明范围之外的改动"）
   - P4 的实现路径与 P2 §1.1 的 M1-M23 改动清单逐条对照，是否有 M 项在 P4 实现记录里找不到
     对应落地（三份 P4-implementation*.md + 1 份 selfgate-fix + 1 份 reviewfix 共 5 份，
     需要你自己汇总核对全部 23 个 M 项是否都有落地记录）
   - P2 CHECK 12/审计 7 的设计（§2/§3）与 P4 实际实现是否一致（尤其 P4-review 修复轮之后的
     最终状态：CRITICAL-1 fail-closed + CRITICAL-2 小节裁剪，这两处修复是否与 P2 原始设计
     有偏离——若有偏离，判断是否需要标 DEVIATION 或已经是"P2 设计遇到实现细节问题后的合理
     演进"）
4. **未决项清零**：核实 P1-requirements.md 无残留行首 `[NEED_CONFIRM]`（已确认 `[NO_NEED_CONFIRM]`）、
   全部 5 份 P4 系列实现记录无 `[BLOCKER]`/`[DEVIATION-CRITICAL]`。
5. **实质锚点要求**：结论不能是裸"一致"，必须引用具体源文件节名（如 `P2§1.1 M17`、
   `P4-implementation-batchC.md`、`P6-acceptance.md BDD-12`）。

### 上游关联

P1-P6 全部完成：P1（19 BDD，2 轮 review approved）、P2（2 轮方案设计，plan-eng-review approved，
含 serial 3 批次 dispatch_plan）、P3（24 测试红灯）、P4（3 批次实现 + SELF-GATE 修复轮 + P4-review
2 轮修复 approved）、P5（966 passed/0 failed，consistency 0 ERROR）、P6（19/19 BDD PASS）。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P4-implementation.md、
  P4-implementation-batchB.md、P4-implementation-batchC.md、
  P4-implementation-selfgate-fix.md、P4-implementation-reviewfix.md（5 份，全部要读）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P5-test-results/unit.md
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P6-acceptance.md
- agate/assets/templates/dispatch-prompt.md（DESIGN_GAP 核实对象）

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
- worktree HEAD：59ed117（P6 已 commit），工作区干净。
- 全仓检索确认：`[SCOPE+]` 字面标记全任务 0 次触发（P1 §8 声明"无"）；`[DESIGN_GAP:]` 全任务
  仅 1 处（P4-implementation.md 第 53 行）。
</objective_info>
