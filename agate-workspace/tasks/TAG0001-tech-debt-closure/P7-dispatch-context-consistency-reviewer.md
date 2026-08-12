---
phase: P7
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0001
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0001-tech-debt-closure/P7-consistency.md——对 TAG0001 P1-P6 产出做跨文件一致性审查：DESIGN_GAP 配对、SCOPE+ 闭环、跨文件一致性、未决项清零。你是独立视角（agent 必须是 consistency-reviewer）。

### 约束
- **只审不写**：不修改任何产出文件，只产出 P7-consistency.md。
- 本任务是 **agate 协议自身改造**（dogfooding）：审查对象是 worktree `agate/`（已含 TAG0003 工作区架构 + TAG0002 refactor 机制 + TAG0001 技术债闭环）；`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。
- **检查清单**（P7 卡片）：
  1. **DESIGN_GAP 配对**：P4-implementation-core.md / -fix.md 中的 [DESIGN_GAP] 声明 → 必须在 P7-consistency.md 中逐条转抄 + 配 [DESIGN_GAP_REVIEWED] 标记。未配对 → gate 不通过。（注意：core 标了 1 条 BDD-2 测试 fixture bug，主 Agent 已修复并标 REVIEWED；P5 修复 serialize_evidence 若标了 DESIGN_GAP 也要转抄）
  2. **SCOPE+ 闭环**：P1-requirements.md frontmatter 有 scope_resolved（2 项：G8 fixture 同步 + consistency 锚点）——确认已纳入 P2/P4 实现。
  3. **跨文件一致性**：
     - P2 packages=[agate] 与 P8 release 的 bump 范围一致？
     - P1 的 20 条 BDD 与 P6 的 20 条验收结果数量匹配 + 内容对应？
     - P4 实现（agate-debt-check.py / check-debt.sh / tech-debt-template.md / check-gate.sh P8 debt_check / agate-retreat-to.sh + 12 文档）与 P2 方案（§0.1 改动面表）吻合？
     - debt/ 归类修正同步面（WORKFLOW.md 目录图 / agents/ 注释 / 三处 mkdir 9 子目录 / UPGRADING v0.43.0 / TAG0003 修订注）是否完整？
     - P4-implementation-core.md / -docs.md / -fix.md 声明与 git 实际改动一致？
  4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]；全任务目录无未处理的 [BLOCKER] / [DEVIATION-CRITICAL]。
- **实质锚点要求**（gate 会校验）：
  - BLOCKER=0：DESIGN_GAP 配对项 + REVIEWED 标记
  - CRITICAL=0：跨文件检查项 + 源文件节名（P2§packages / P4§impl-path 等）
  - SCOPE+ 闭环：条目 + SCOPE_RESOLVED
- **frontmatter 机器计数**：blocker_count / deviation_count / deviation_critical_count / design_gap_count / design_gap_reviewed_count 五个字段必填。
- 结论引用具体锚点，不写裸 "一致" / "BLOCKER=0"。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P4-implementation-core.md 有 1 条 [DESIGN_GAP]（BDD-2 测试 fixture bug）+ [DESIGN_GAP_REVIEWED: 已确认]（主 Agent 已标：修复 mkdir 显式参数 + SETUP 断言 + R5 fixture）。
- P5 修复 serialize_evidence（P4-implementation-fix.md）——若含 DESIGN_GAP 声明需转抄。
- P1 frontmatter scope_resolved 2 项（G8 fixture 同步 + consistency 锚点）。
- P6 验收 20/20 PASS（P6-acceptance.md，provenance 审计 0）。
- P5 全量验证绿（bats 676/0 + consistency 0 ERROR + shellcheck 0）。

### 输入文件
- docs/tasks/TAG0001-tech-debt-closure/P1-requirements.md（需求基线 + BDD + scope_resolved——必读）
- docs/tasks/TAG0001-tech-debt-closure/P2-design.md（方案设计 + packages/domains——必读）
- docs/tasks/TAG0001-tech-debt-closure/P4-implementation-core.md / -docs.md / -fix.md（实现记录——必读，含 DESIGN_GAP）
- docs/tasks/TAG0001-tech-debt-closure/P4-review.md（实现评审——必读）
- docs/tasks/TAG0001-tech-debt-closure/P5-test-results/unit.md（验证结果——必读）
- docs/tasks/TAG0001-tech-debt-closure/P6-acceptance.md（验收结果——必读）
- docs/tasks/TAG0001-tech-debt-closure/P0-brief.md（任务简报——必读）
- AGENTS.md（项目约定——必读）
- git log（实际改动核对——按需）
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
4. 预跑 check-gate.sh P7
5. 更新 .state.yaml phase=P7 → P8
6. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
7. git commit -m "wf({Txxx}-P7): {摘要}"

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
check-gate.sh P7 $TASK_DIR
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0001-P6 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 任务进度：P1 20 BDD → P2 D1-D4 定案 → P3 22 测试红灯 → P4 实现（review approved + P5 修复 serialize_evidence）→ P5 验证绿 → P6 验收 20/20 PASS。
- 已核实查证：P4-implementation-core.md 含 1 条 DESIGN_GAP + REVIEWED；P4-implementation-fix.md（serialize_evidence 修复）可能含声明；P1 scope_resolved 2 项；debt/ 归类修正同步面已落地。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
