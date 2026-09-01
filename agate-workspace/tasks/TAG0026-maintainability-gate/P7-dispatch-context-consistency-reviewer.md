---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对 TAG0026 的 P1-P6 产出做跨文件一致性审查，产出 `P7-consistency.md`：
BLOCKER=0 / DEVIATION-CRITICAL=0 / DESIGN_GAP 全配对（P4 的 1 条 DESIGN_GAP → REVIEWED）/
SCOPE+ 闭环 / CODE-MAP 核对。

### 检查清单（P7 卡执行方式 + 本任务特有项）

1. **DESIGN_GAP 配对**：P4-implementation.md §3.1 有 1 条 `[DESIGN_GAP: ...]`
   （连字符文件名 import 兜底）——逐字转抄进 P7-consistency.md 并配
   `[DESIGN_GAP_REVIEWED]` 标记 + 审查结论（该偏差是否与 P2-design 契约兼容、实现侧
   importlib 兜底是否与 agate-risk-score `_load_script` 同源、P2-review 是否已核、
   文档层面是否需回写）。frontmatter `design_gap_count: 1` /
   `design_gap_reviewed_count: 1`（若全部核过）。
2. **SCOPE+ 闭环**：P4-implementation.md §5 声明"无 [SCOPE+]"——核对 P1-requirements.md
   无 [SCOPE+] 增补、无 [SCOPE_RESOLVED] 需求（无增补即无闭环动作，写明确结论）。
3. **跨文件一致性**（逐项给锚点）：
   - P1 BDD 数（13）= P6 PASS 数（13）= judge criteria_total（13），且逐条编号内容对应
     （抽查 BDD-7/9/12/13 对照 P1 判定锚与 P6-evidence 证据内容）
   - P2 packages（agate-scripts/agate-tests/agate-phase-cards/agate-templates）与 P4 实现
     落点、P8 bump 范围一致
   - P4 实现路径与 P2 §3 方案吻合（检测器契约/gate_p4 挂载点/模板格式/配置键）
   - P2 §4 gate_commands 与 P5 实跑命令一致（5 条键全执行）
   - 卡片改动（P4 卡 checklist/gate 规则 + P6 卡自查提醒）与实际 gate 行为对应
   - DEBT0023（P3* 键）与 P2 gate_commands 无 P3_xxx 键的契约一致
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]（应只有 [NO_NEED_CONFIRM]）、
   无 [BLOCKER]、[DEVIATION-CRITICAL]；P4-implementation.md 的阻塞上报（§3.2 测试探测缺陷）
   已解决（P4-progress + P4-review 记录），P7 写明"已解决"结论。
5. **CODE-MAP 核对**：对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（若存在）与
   P4-implementation.md「新增文件核对表」（3 个新增文件，均 [CODE_MAP_EXEMPT]）逐条核对，
   通过标 `[CODE_MAP_SYNC:]`；frontmatter `code_map_new_files_count: 3` /
   `code_map_reviewed_count: 3`。
6. **实质锚点**：结论引用源文件节名（P2§packages / P4§impl-path / P6§BDD 对照等），
   不写裸"一致"。
7. **不修任何文件**：只审，发现问题写 P7-consistency.md（BLOCKER → 主 Agent 处理）。
8. **PROD 隔离**：禁 worktree git 写；返回报 [PROD_NOT_TOUCHED]。所有 bash timeout。

### 产出（路径硬约束）

/home/kity/oclab/agateon/.worktrees/agate-TAG0026/agate-workspace/tasks/TAG0026-maintainability-gate/P7-consistency.md
frontmatter（agate-md-field-set，先 --list）：phase: P7 / task_id: TAG0026 / type: consistency /
parent: P2-design.md / trace_id: TAG0026-P7-20260830 / status: draft / created: 2026-08-30 /
agent: consistency-reviewer / blocker_count: 0 / deviation_count: 0 /
deviation_critical_count: 0 / design_gap_count: 1 / design_gap_reviewed_count: 1 /
code_map_new_files_count: 3 / code_map_reviewed_count: 3
（计数以实际审查结果为准，上述为预期值；若有 BLOCKER 照实写并报告）。

### 输入文件（P7 输入数量豁免，全部源文件同时可见）

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P1-requirements.md`
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（§1/§2/§4/§6）
3. `agate-workspace/tasks/TAG0026-maintainability-gate/P3-test-cases.md`
4. `agate-workspace/tasks/TAG0026-maintainability-gate/P4-implementation.md`（§1/§3/§4/§5）
5. `agate-workspace/tasks/TAG0026-maintainability-gate/P5-test-results/unit.md`
6. `agate-workspace/tasks/TAG0026-maintainability-gate/P6-acceptance.md`
7. `agate-workspace/tasks/TAG0026-maintainability-gate/P6.5-judge-verdict.md`
8. `agate-workspace/tasks/TAG0026-maintainability-gate/P6-evidence/`（抽查）
9. `agate-workspace/debt/tech-debt.md`（DEBT0023 条目）
10. `agate/scripts/check-maintainability.py` + `check-gate.py`（实现对照）
11. `agate/phase-cards/P4-implementation.md` + `P6-acceptance.md`（卡片改动处）
12. `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（若存在）
13. `AGENTS.md`
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
### A. 环境（主 Agent 已核）
- worktree 根 /home/kity/oclab/agateon/.worktrees/agate-TAG0026；HEAD=5d828c9（P6.5 commit）
- git 链：f7e7b9f（P4 实现）→ acf0cb2（P5 五命令全绿）→ 7af1e72（P6 13/13 PASS）→ 5d828c9（P6.5 judge passed 13/13）
- P4 的 DESIGN_GAP：1 条（P4-implementation.md §3.1，连字符文件名 import 兜底）
- P4 新增文件核对表：3 个新增文件（check-maintainability.py / known-violations-template.md / maintainability.yaml），均 [CODE_MAP_EXEMPT] 附理由
- CODE-MAP 机制采用中（agents/CODE-MAP.md 存在——P4 gate WARNING 曾因此提示）
- DEBT0023 已登记（tech-debt.md，check-debt exit 0）
- consistency 预检（P5 实测）：worktree check-protocol-consistency.py --strict-errors-only → 0 ERROR / 323 WARNING
- 本任务无 [SCOPE+]（P4 §5 声明）；P1 无残留 [NEED_CONFIRM]
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
