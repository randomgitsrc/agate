---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P7-consistency.md：对照 P1-P6 产出做跨文件一致性交叉检查（实现 vs 设计），确保未偏离设计。这是 P7 阶段门槛产出。

### 约束

- **检查清单（consistency-reviewer 角色定义）**：
  1. DESIGN_GAP 配对：P4-implementation.md 中的 DESIGN_GAP 声明 → 逐条转抄 + `[DESIGN_GAP_REVIEWED: 已确认/已打回 P2]` 配对标记（行首格式）
  2. SCOPE+ 闭环：P1-requirements.md 有 [SCOPE_RESOLVED] 标记 → 确认所有 SCOPE+ 增补已纳入基线
  3. 跨文件一致性（必须引用具体锚点，非裸"一致"）：
     - P2 packages 与 P8 release bump 范围一致（本任务 packages: [agate-protocol, agate-scripts, agate-tests]）
     - P1 BDD 数量（22）与 P6 验收结果数量（22）匹配
     - P4 实现路径与 P2 方案设计吻合（op/gate/权威节/卡片/模板）
  4. 未决项清零：P1-requirements.md 无残留行首 [NEED_CONFIRM] / [BLOCKER] / [DEVIATION-CRITICAL]
- **跨文件引用关键词**：P7 产出须含源文件节名（如 `P2§packages`、`P4§impl-path`、`P1§BDD-22`）——gate WARNING 检查
- **DESIGN_GAP 格式**：行首 `[DESIGN_GAP: 描述]` + 行首 `[DESIGN_GAP_REVIEWED: 描述]`（gate 正则匹配行首）
- **frontmatter 机器计数**：blocker_count / deviation_count / deviation_critical_count / design_gap_count / design_gap_reviewed_count
- **只读检查**：P7 不修改任何代码/文档/协议文件（只产出 P7-consistency.md）。
- **输出路径硬约束**：P7-consistency.md → {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P7-consistency.md

### 上游关联

- P1-requirements.md：22 条 BDD，[NO_NEED_CONFIRM]
- P2-design.md：方案设计 + §4 BDD 映射表 + §7 SCOPE+ 声明（无新增）
- P4-implementation.md：实现记录（检查是否有 DESIGN_GAP / SCOPE+ 声明）
- P6-acceptance.md：22/22 BDD PASS
- P5-test-results/unit.md：技术验证通过

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P0-brief.md（环境约束）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P1-requirements.md（BDD 条件、SCOPE+ 声明）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md（packages、domains、方案设计）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P4-implementation.md（DESIGN_GAP 声明）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P6-acceptance.md（BDD 验收结果）
- {project_root}/agate/assets/execution-roles/consistency-reviewer.md（角色定义）
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

P7 是输入文件数量限制的例外，不拆分。原因：
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
- P6 验收：22/22 BDD PASS；P5 验证：pytest 780 passed / consistency 0 ERROR / count 782
- P2-design §7：无新增 SCOPE+（I1-I10 已在 P1 §2 声明）；SUGGEST S1（loop-orchestration.md L215）待主 Agent 决定
- P4-implementation.md：implementer 修复轮后状态（README badge 已还原 / 3 条失败已修复）
- 本任务触发 self-gate：P7 阶段另派 protocol-alignment-review（见 SELF-GATE 流程，独立于本检查）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
