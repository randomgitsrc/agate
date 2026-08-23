# P7-dispatch-context-consistency-reviewer — TAG0022 一致性检查

> 派发对象：consistency-reviewer（P7 交叉检查）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

跨文件一致性审查 TAG0022 的 P1-P6 产出，产出 `P7-consistency.md`（含 DESIGN_GAP 配对 REVIEWED + 跨文件引用锚点 + 机器计数 frontmatter）。

## 检查清单（P7 卡 + consistency-reviewer 角色定义）

1. **DESIGN_GAP 配对（硬门槛）**：P4-implementation.md 中 2 条 [DESIGN_GAP]（L289：P5 gate_commands.P5 token 对齐；L291：S-3a/S-3b token 匹配粒度定案）→ P7-consistency.md 必须**逐条转抄原始标记行 + REVIEWED 标记行**（`[DESIGN_GAP_REVIEWED: 已确认]` 或 `[DESIGN_GAP_REVIEWED: 已打回 P2]`）。判定依据：主 Agent 已采纳 + protocol-alignment-review 独立核实成立（docs/reviews/agate-alignment-review-2026-08-23-TAG0022.md）+ P3 用例全绿 + P6 BDD-3/5 PASS
2. **SCOPE+ 闭环**：P1-requirements.md 有 [SCOPE_RESOLVED]（M15 iter_md_files 排除钩子）——确认 M15 已实现（check-protocol-consistency.py）+ P6 BDD-9 PASS
3. **跨文件一致性**（每条引用源文件节名锚点）：
   - `P1§packages`=[agate] vs `P2§packages` vs P8 bump 范围（单版本单元）
   - `P1§BDD`=10 vs `P6§pass/fail`=10/0（数量匹配 + 编号集合一致）
   - `P4§impl` 四批实现 vs `P2§design` 方案（C 批迁移映射 / B 批 judge 判据 / D 批 M15 / A 批 workflow）逐条吻合
   - `P1§ceremony`=standard vs `P2§ceremony`（非 thin；RM-AG0040 实证计划在 P2 §4.4）
   - judge 机制链：`.state.yaml` judge.enabled=true ↔ P6.5 verdict passed 10/10 ↔ 账本 judge_verdict 事件
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]/[BLOCKER]/[DEVIATION-CRITICAL]；P1 `[NO_NEED_CONFIRM]` 声明核对
5. **CODE-MAP 核对**：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` vs P4「新增文件核对表」（test_md_parse_scan.py 新增 + 各批无新增代码文件）→ `[CODE_MAP_SYNC:]` 或 `[CODE_MAP_DRIFT:]`
6. **批界偏差标注核对**：P4-implementation.md batch B 节「批界偏差标注」（test_env_adapt_docs.py:172 注释跨批修复）——确认标注存在且可追溯（P4-review INFORMATIONAL #1 闭环）

## 输入文件（P7 输入数量豁免，全部源文件）

1. `P1-requirements.md` / `P1-review.md`
2. `P2-design.md` / `P2-review.md`
3. `P3-test-cases.md`
4. `P4-implementation.md`（含 2 条 DESIGN_GAP + 批界偏差标注）/ `P4-review.md`
5. `P5-test-results/unit.md`
6. `P6-acceptance.md` / `P6.5-judge-verdict.md`
7. `{AGATE_WORKSPACE}/agents/CODE-MAP.md`
8. 客观查证：`{agate_root}/phase-cards/P7-consistency.md` + `{agate_root}/assets/execution-roles/consistency-reviewer.md`

## 产出规格

`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P7-consistency.md`，Header：

---
phase: P7
task_id: TAG0022-confirmed-problems
type: consistency
parent: P2-design.md
trace_id: TAG0022-P7-20260822
status: draft
created: 2026-08-22
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 2
design_gap_reviewed_count: 2
code_map_new_files_count: 1
code_map_reviewed_count: 1
---

正文含：DESIGN_GAP 配对节（原始标记 + REVIEWED 逐条）、跨文件一致性节（源文件节名锚点）、SCOPE+ 闭环节、未决项清零节、CODE-MAP 核对节、结论（BLOCKER=0 / CRITICAL=0 / DESIGN_GAP 全配对）。

## 环境约束

Linux；/tmp 只读；bash 一律 timeout；双工作区纪律（只读消费，写操作仅限 P7-consistency.md 与 P7-progress.md）。状态标记：`[PROD_TOUCHED]`/`[PROD_NOT_TOUCHED]`。

## 分阶段落盘

每完成一个检查项，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P7-progress.md`。

## 返回给我

只返回两行：① P7-consistency.md 路径；② 一句话摘要（BLOCKER 数 / DESIGN_GAP 配对数 / 结论）。绝不返回文件全文。
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
