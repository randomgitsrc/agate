# P7-dispatch-context-consistency-reviewer — TAG0023 一致性检查

> 派发对象：consistency-reviewer（P7 一致性交叉检查）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> P7 是输入数量豁免特例，不拆分，单次派发覆盖全部 P0-P6 产出。

## 目标

对照 P0-P6 全部产出做跨文件一致性审查，产出 `P7-consistency.md`。

## 约束（硬约束，按角色文件「检查清单」逐项）

1. **DESIGN_GAP 配对检查（重点核实一个边界情况）**：`P4-implementation.md` 本身**不含**任何 `[DESIGN_GAP:` 标记（已核实），gate 脚本只扫描 `P4-implementation.md`，所以机械层面不需要配对。**但你需要知道**：implementer 在实现过程中（`P4-progress-batchA.md` 里）记录过一处真实的设计歧义发现——P2-design.md §2.1 对 BDD-2 条件的字面表述未显式要求 `old_retries_len>0`，implementer 最初加了这个守卫，后来 P4-review 独立评审发现这个守卫会漏判 RM-AG0042 的立项证据本身场景（CRITICAL 1），主 Agent 决策采用方案 A 去掉守卫、按 BDD-2 字面语义实现——这个歧义已经在 P4 review 迭代中被发现、讨论、解决，最终交付代码不存在遗留偏差。请你核实：这种"过程中发现但已被同阶段内的 review 循环解决"的情况，是否真的不需要在 P4-implementation.md 补记 `[DESIGN_GAP:]` 标记（判断依据：P4-implementation.md 描述的是最终交付状态，不是过程记录；`P4-progress-batchA.md` 已完整记录这段过程）——如果你认为需要补记，标注为 WARNING 级观察即可，不要求你去改 P4-implementation.md（P4 已 commit，不可回改，若你认为确有必要补记，在 P7-consistency.md 里明确指出并说明为什么不阻断）
2. **SCOPE+ 闭环**：`P1-requirements.md` 声明 `[NO_NEED_CONFIRM]`（无 SCOPE+ 项），`P4-implementation.md` 「[SCOPE+] 声明」节写"无"——确认全程无 SCOPE+ 增补，不需要 SCOPE_RESOLVED 配对
3. **跨文件一致性**（逐项引用具体节名，不写裸"一致"）：
   - P1-requirements.md 的 13 条 BDD 编号（BDD-1~BDD-13）与 P6-acceptance.md 的 13 条 PASS 是否逐一对应（不只对比数量，核对每条 BDD 编号在两份文件里的内容是否一致所指）
   - P2-design.md `packages: [agate]` 声明——P8 尚未产出，此项留待 P8 阶段核对，本轮只需确认 P2 声明存在且合理，不阻断
   - P4-implementation.md 的 4 批改动文件清单与 P2-design.md §1.1「改什么」表、dispatch_plan 5 批声明是否吻合（文件集合两两不相交的边界是否与 P2 设计一致）
4. **未决项清零**：确认 P1-requirements.md 无残留 `[NEED_CONFIRM]`、P6-acceptance.md 无 `[BLOCKER]`/`[DEVIATION-CRITICAL]`（已初步核实，你需要独立复核一遍）
5. **CODE-MAP 核对**：读 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`「模块」节——该文件明确只追踪 `phase-cards`/`execution-roles`/`review-roles`/`scripts`/`templates`/`rules` 六个模块目录。本任务新增的 `agate/tests/ENV-SENSITIVE-TESTS.md` 与 `agate/tests/unit/test_env_sensitive_tests_registry.py` 均在 `agate/tests/` 目录下，**不属于** CODE-MAP.md 追踪的任何模块——请你核实这个判断是否正确（读 CODE-MAP.md 全文确认 `tests/` 确实不在追踪范围），若确认无误，标 `[CODE_MAP_EXEMPT: agate/tests/ 目录不在 CODE-MAP.md 追踪的六大模块范围内]`；**注意**：`P4-implementation.md` 原文声称"本仓库未采用骨架/CODE-MAP机制"这个表述不准确（CODE-MAP.md 确实存在且在用），请在 P7-consistency.md 里指出这处表述不精确（WARNING 级，不阻断——因为实质结论"本任务新增文件不需要 CODE-MAP 条目"仍然成立，只是原因表述错了：不是"机制未采用"，而是"新增文件不在追踪范围"）

## 上游关联

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P0-brief.md`
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-progress-batchA.md`（DESIGN_GAP 过程记录核实用）
- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P6-acceptance.md`
- `{AGATE_WORKSPACE}/agents/CODE-MAP.md`

## 输入文件（P7 豁免拆分，全部读取）

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P0-brief.md`
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`
3. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`
4. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`
5. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-progress-batchA.md`
6. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P6-acceptance.md`
7. `{agate_root}/assets/execution-roles/consistency-reviewer.md`
8. `{agate_root}/phase-cards/P7-consistency.md`
9. `{AGATE_WORKSPACE}/agents/CODE-MAP.md`

## 产出

`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P7-consistency.md`（frontmatter `---` 分隔）：
```
---
phase: P7
task_id: TAG0023-mechanism-checks
type: consistency
parent: P2-design.md
trace_id: TAG0023-P7-20260825
status: draft
created: 2026-08-25
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---
```
（`design_gap_count`/`design_gap_reviewed_count` 均为 0，因为 P4-implementation.md 本身不含 DESIGN_GAP 标记；约束1 里那处过程记录作为 WARNING 级观察写在正文，不计入这两个字段）

## 门槛

- 无 [BLOCKER]/[DEVIATION-CRITICAL]
- 跨文件检查项引用具体锚点（P1 BDD 编号/P2 packages/P4 implementation 等），非裸"一致"
- CODE-MAP 核对结论明确（EXEMPT 或 SYNC）

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（结论，≤40字）。绝不返回文件全文。

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
