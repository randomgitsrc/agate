---
phase: P7
generated_by: 主 Agent
task_id: TAG0029
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
对照 P1–P6 产出做跨文件一致性审查，产出 `P7-consistency.md`（frontmatter 机器计数 + 正文逐条检查 + 实质锚点）。

### 约束
- **DESIGN_GAP 配对**：主 Agent 已查 `P4-implementation.md` 行首 `^\[DESIGN_GAP:` 计数为 0——P7 写 `design_gap_count: 0 / design_gap_reviewed_count: 0`，正文声明"无 DESIGN_GAP 声明，无需配对"（空白不算，需显式写出）。
- **SCOPE+ 闭环**：P1-requirements.md 无 `[SCOPE+]` 行首标记、无 `SCOPE_RESOLVED`——正文声明"无 SCOPE+ 增补"（P1 基线自 P1 以来未变更；P2 §2.5 退役声明落在设计与协议卡，非 P1 基线变更）。
- **跨文件一致性（逐项引用节名，非裸"一致"）**：
  1. P1 BDD 数（9）vs P6 PASS+FAIL（9/0）vs judge criteria（9/9）：三处计数一致，逐条编号对照（BDD-1~9 无错位映射）。
  2. P2 packages（gate-parser/tdd-judge/platform-scanner/protocol-docs）vs P4 files_modified（3 脚本 + P2 卡 + S1 测试 + formatters README + CHANGELOG/docstring 自审同步）：包域覆盖一致；SELF-GATE 新增两文档文件（formatters README/CHANGELOG）在包外但属 A3 反向传播已裁决范围，需显式说明。
  3. P4 实现 vs P2 §3.1–3.4：M1–M5 落点一致（P4-review C1–C6 已独立核对，引用其结论 + 行号）。
  4. P2 gate_commands（7 key）vs P5 执行（7 条全跑，unit.md 逐条记录）：无子集遗漏（T060）。
  5. P1 risk_level=high vs phases 全量 vs P7 不可裁：一致。
- **未决项清零**：P1 无行首 NEED_CONFIRM（仅 [NO_NEED_CONFIRM]）；无 BLOCKER/DEVIATION-CRITICAL；GAP 无。
- **CODE-MAP 核对**：骨架未采用（无 P2-skeleton.md）；CODE-MAP 机制存在（`agate-workspace/agents/CODE-MAP.md`）——本次新增文件为既有脚本修改（非新增文件）+ 测试文件 2 个（A/B 批）+ 任务目录文档。对照 CODE-MAP 记录逐条判定 `[CODE_MAP_SYNC:]`/`[CODE_MAP_EXEMPT: 理由]`/`[CODE_MAP_DRIFT:]`。测试文件若按惯例豁免须写明理由。
- **frontmatter 机器计数**：phase=P7, task_id=TAG0029, type=consistency, parent=P2-design.md, trace_id=TAG0029-P7-20260904（执行日为准）, agent=consistency-reviewer, status=draft→终态 approved/rejected；blocker_count/deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count 必填（预期全 0）；code_map_new_files_count/code_map_reviewed_count 按实际核对填写。
- 返回前跑 check-frontmatter 自检（worktree 根）。
</dispatch_guide>

### 上游关联
- P1-requirements.md（9 BDD）/ P1-review.md（approved）/ P2-design.md（方案 A + §2.5 退役）/ P2-review.md（approved，B1 关闭）/ P3-test-cases.md（10 用例）/ P4-implementation.md（M1–M5 + S1/I1）/ P4-review.md（approved，S1 更新 + S2/S3 保留）/ P5-test-results/unit.md（1444 绿）/ P6-acceptance.md（9/0）+ P6-evidence/（9 日志）/ P6.5-judge-verdict.md（passed 9/9）。
- `.state.yaml` phase=P6（P7 推进随 P7 产出 commit 一起）。

### 输入文件
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-design.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P2-review.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P3-test-cases.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P4-implementation.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P4-review.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P5-test-results/unit.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P6-acceptance.md`
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P6.5-judge-verdict.md`
- `agate-workspace/agents/CODE-MAP.md`（CODE-MAP 核对）
- `agate-workspace/tasks/TAG0029-gate-parser-fix/.state.yaml`

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
- worktree 根：`/home/kity/oclab/agateon/.worktrees/agate-TAG0029`。
- 门槛事实（主 Agent 已查）：DESIGN_GAP 0 条；SCOPE+ 0 条；骨架未采用；CODE-MAP 存在；P4 新增文件 0 个（全为既有文件修改）+ 测试文件 2 个 + 任务文档。
- P7 输入豁免特例：单发不拆分（跨文件比较需全可见）。
- 注：该文件禁止包含 verdict 预判。
</objective_info>
