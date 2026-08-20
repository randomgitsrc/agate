---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0017-toolchain-fixes
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。P7 不拆分（输入数量豁免例外），单发。

### 目标
对 P1-P6 全部产出做跨文件一致性交叉检查，产出 P7-consistency.md。

### 约束
1. **双工作区纪律**：只读写 worktree，不碰主 checkout 或 `~/.agate`。
2. **DESIGN_GAP 配对**：核实 P4-implementation.md 中确实无 `[DESIGN_GAP]` 声明（本任务 5 个批次 + review-fix 均明确报告"无 DESIGN_GAP"），若核实属实，`design_gap_count: 0` / `design_gap_reviewed_count: 0`，无需配对转抄。
3. **SCOPE+ 闭环**：核实 P1-requirements.md、P2-design.md、P4-implementation.md 全程无 `[SCOPE+]` 声明（本任务范围在 P0-brief 锁定、P1/P2 均未发现范围外必须做的事）。
4. **跨文件一致性重点核查项**：
   - P1 的 12 条 BDD 编号（BDD-1~12）与 P6 的验收结果数量是否精确匹配（P6 frontmatter `pass: 12, fail: 0`）
   - P2 的 4 个功能分组候选方案（A 均获选）与 P4 的 5 个批次实现是否吻合（注意 P2 是 4 组、P4 dispatch_plan 是 5 批，因为 fg1 被拆成 fg1-parser-scripts + fg1-doc-boundary 两批，这是有意设计，非不一致——需在 P7 报告中明确说明这一点，避免被误判为数量不符）
   - P2 声明的 `packages`/`domains` 与 P4 实际改动文件范围是否一致
   - P4-review.md 发现的 1 个 CRITICAL（`--strict` → `--strict-errors-only` 同步）修复后，是否已在最终代码状态中生效（可核实 `agate/phase-cards/P2-design.md` 与本任务自身 P2-design.md 是否均已是 `--strict-errors-only`）
   - self-gate（protocol-alignment-review）发现的 1 个 MISALIGNED（`agate/scripts/README.md`）修复后，是否已在最终状态中生效
5. **未决项清零**：核实 P1-requirements.md 无残留行首 `[NEED_CONFIRM]`（P1 已是 `[NO_NEED_CONFIRM]`）、无 `[BLOCKER]`、无 `[DEVIATION-CRITICAL]`。
6. **实质锚点要求**：结论必须引用具体源文件节名（如 `P1§BDD-1`、`P2§候选方案`、`P4§fg1-parser-scripts`），不能写裸"一致"。

### 上游关联
- P1：12 条 BDD，4 功能分组，`[NO_NEED_CONFIRM]`
- P2：8 候选方案（4 组各 2 个），5 批 dispatch_plan，approved（1 轮 CRITICAL 修复后）
- P3：41 个红灯测试用例，5 批并行 + 1 轮卫生修复
- P4：5 批实现 + 1 轮 review-fix（CRITICAL：`--strict-errors-only` 同步）+ self-gate 1 轮修复（`README.md`），approved，A1-A7 全 ALIGNED
- P5：4/4 gate_commands 命令 exit 0，1011 passed/0 failed
- P6：12/12 BDD PASS，0 FAIL

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P1-requirements.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-review.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P3-test-cases.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P4-implementation.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P4-review.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P5-test-results/unit.md
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P6-acceptance.md
- /home/kity/oclab/agate/.worktrees/agate-TAG0017/docs/reviews/agate-alignment-review-2026-08-20-TAG0017.md（self-gate 审查报告）
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
- 环境：worktree，全部 P1-P6 产出已 commit 完成
- 本任务无 DESIGN_GAP、无 SCOPE+ 声明（各阶段均已确认）
</objective_info>
