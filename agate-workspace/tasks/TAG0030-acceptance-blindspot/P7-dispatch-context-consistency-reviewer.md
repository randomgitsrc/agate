---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0030
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

P7 一致性检查（consistency-reviewer subagent）：对照 P1-P6 全部产出做跨文件一致性审查，
产出 `P7-consistency.md`。检查项：DESIGN_GAP 配对 / SCOPE+ 闭环 / 跨文件一致性（packages、
BDD↔验收数量、实现↔方案）/ 未决项清零 / CODE-MAP 核对。

### 检查清单（P7 卡权威，逐项执行）

1. **DESIGN_GAP 配对**：P4-implementation.md 中 DESIGN_GAP 声明 → 逐条转抄 + 配 REVIEWED 标记
   （未配对 → gate exit 1）。本任务 P4 未声明 DESIGN_GAP（三批实现均按 P2 方案落笔），
   须在 P7 中显式写"P4 无 DESIGN_GAP 声明"并配 count=0（空白不算做过）。
2. **SCOPE+ 闭环**：P1-requirements.md 有 [SCOPE_RESOLVED] 标记？确认所有 SCOPE+ 增补已纳入
   基线。本任务 P1 无 [SCOPE+]（范围锁定无越界），须显式确认。
3. **跨文件一致性**：
   - P2 packages（agate-phase-cards / agate-assets-roles / agate-assets-templates）↔ P4 实际
     改动文件面 ↔ P8 bump 范围一致（P8 未到，按 P4 面核对）
   - P1 BDD 21 条 ↔ P6 PASS 21 条数量匹配，且逐条内容对应（不是只对数量）
   - P4 实现路径 ↔ P2 方案（§2 四 phase 落点表）逐文件核对吻合
4. **未决项清零**：P1 无残留行首 [NEED_CONFIRM] / [BLOCKER] / [DEVIATION-CRITICAL]（P6 后）。
5. **CODE-MAP 核对**：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 与 P4「新增文件核对表」逐条核对。
   本任务 P4 三批均声明"无新增文件"（只改既有文件）→ 核对 CODE-MAP 是否需要更新（改既有
   文件不新增条目），结论标 `[CODE_MAP_SYNC:]` 或 `[CODE_MAP_DRIFT:]`。

### 约束

1. **实质锚点**：结论引用具体源文件节名（如 `P2§packages`、`P4§impl-path`、`P6§acceptance`），
   不写裸 "BLOCKER=0"（gate WARNING 提醒）。
2. **frontmatter 机器计数**：blocker_count / deviation_count / deviation_critical_count /
   design_gap_count / design_gap_reviewed_count / code_map_new_files_count /
   code_map_reviewed_count 写文件头 frontmatter（用 agate-md-field-set 写，无命令则用
   `python3 /home/kity/oclab/agateon/agate/scripts/agate-md-field-set.py`；agent 键拒绝 set 按
   惯例手工写）。
3. **无行首预判**：本文件与 P7-progress.md 禁止行首 `- PASS`/`- FAIL`；P7-consistency.md 正文
   `[BLOCKER]`/`[DEVIATION-CRITICAL]`/`[DESIGN_GAP]`/`[DESIGN_GAP_REVIEWED]` 标记按产出规格写。
4. **只审不写**：不改任何协议文件/阶段产出，只写 P7-consistency.md + progress，标记
   `[PROD_NOT_TOUCHED]`。
5. **命令超时兜底**：所有 bash 命令外层 timeout（grep 核对 `timeout 60s`）。
6. **跨文件引用关键词**：P7 产出须含源文件节名（`P2§packages` / `P4§impl-path` / `P1§BDD` /
   `P6§acceptance` 等），否则 gate WARNING。

### 上游关联

- P1-requirements.md（21 BDD + frontmatter packages/domains/phases）
- P2-design.md（§0.1 Modify 表 + §2 四 phase 落点 + frontmatter packages/candidate_count/dispatch_plan）
- P3-test-cases.md + test_tag0030_assertions.py（21 用例 1:1）
- P4-implementation.md（三批章节 + 新增文件核对表）+ P4-review.md（approved）
- P5-test-results/（技术验证）+ known-failures.md（1 预存 flaky）
- P6-acceptance.md（21 PASS）+ P6-evidence/ + P6.5-judge-verdict.md（passed）
- CODE-MAP.md（agents/ 目录）

### 输入文件（按顺序读，P7 输入豁免不拆分）

1. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P1-requirements.md`
2. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P2-design.md`
3. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P3-test-cases.md`
4. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P4-implementation.md`
5. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P4-review.md`
6. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P5-test-results/unit.md`
7. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P6-acceptance.md`
8. `agate-workspace/tasks/TAG0030-acceptance-blindspot/P6.5-judge-verdict.md`
9. `agate-workspace/tasks/TAG0030-acceptance-blindspot/known-failures.md`
10. `agate-workspace/agents/CODE-MAP.md`
11. `agate/assets/execution-roles/consistency-reviewer.md`（角色定义）
12. `AGENTS.md`（worktree 根，项目约定）

### 产出文件字段

产出 `P7-consistency.md` 到任务目录，frontmatter 用 agate-md-field-set 写：
phase=P7, task_id=TAG0030, type=consistency, parent=P2-design.md,
trace_id=TAG0030-P7-20260904, status=draft, created=2026-09-04, agent=consistency-reviewer,
blocker_count / deviation_count / deviation_critical_count / design_gap_count /
design_gap_reviewed_count / code_map_new_files_count / code_map_reviewed_count
（按实际核对填，预期全 0——本任务无 DESIGN_GAP/DEVIATION/新增文件）。
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
5. **CODE-MAP 核对**：对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 与 P4「新增文件核对表」逐条核对，发现依赖方向偏离标 `[CODE_MAP_DRIFT:]`（WARNING 级，不阻断）；核对通过标 `[CODE_MAP_SYNC:]`

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
`design_gap_reviewed_count`/`code_map_new_files_count`/`code_map_reviewed_count` 写在文件头
**frontmatter**（`---` 分隔块），不写正文；正文
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
code_map_new_files_count: 0        # int ≥0（可选，仅骨架/CODE-MAP 机制已采用时填）
code_map_reviewed_count: 0         # int ≥0（可选，语义对应 design_gap_reviewed_count）
---
```

## gate 规则

```bash
check-gate.py P7 $TASK_DIR
```

- [BLOCKER] 存在 → exit 1
- [DEVIATION-CRITICAL] 存在 → exit 1
- DESIGN_GAP 未配对（P4 有但 P7 无 REVIEWED）→ exit 1
- CODE-MAP 未配对（code_map_reviewed_count < code_map_new_files_count，或 P4 实际标记数 > code_map_new_files_count）→ exit 1（两字段均缺失时机制未采用，跳过）
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
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0030`
- 任务目录 = `agate-workspace/tasks/TAG0030-acceptance-blindspot/`
- CODE-MAP = `agate-workspace/agents/CODE-MAP.md`
- commit 链：P1 25c81f6 → P2 ba40610 → P3 167a044 → P4 e39c897 + SELF-GATE 3c2d647 →
  P5 196aca8 → P6 b650508 → P6.5 feb0858

### B. 已知事实（核对用，非结论）
- P1 BDD 21 条（Phase1 BDD-1~6 / Phase2 BDD-7~9 / Phase3 BDD-10~15 / Phase4 BDD-16~21）
- P2 packages 三包（agate-phase-cards / agate-assets-roles / agate-assets-templates）+
  dispatch_plan static-batch 三批（与 packages 对齐）
- P4 改动面 14 协议文件（= P2 §0.1 Modify 表 #1~13 + role-system；#14 审计单测在 P3 commit）
- P4 新增文件核对表：三批均"无新增文件"（只改既有）
- P6 验收 21/21 PASS；judge 21/21 重验通过
- 预存 flaky 1 条已登记 known-failures.md（TAG0011 竞态，非本任务引入）
- P1 无 [SCOPE+] / [NEED_CONFIRM] / [CAPABILITY_GAP]
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。