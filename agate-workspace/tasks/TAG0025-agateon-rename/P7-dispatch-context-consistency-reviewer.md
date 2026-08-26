---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0025
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
对照 P1-P6.5 全部产出做跨文件一致性交叉审查，产出 `P7-consistency.md`。本任务经历了一次真实
的 BASELINE_CHANGE 循环（P6.5 judge 第 1 轮发现 BDD-10 豁免授权缺口 → P1-requirements.md 修订
→ P6 第 2 轮重新验收 → P6.5 judge 第 2 轮通过），这个过程本身就是一次跨文件一致性事件，需要
你重点核实收敛得是否干净（P1/P6/P6.5 三处现在是否互相对得上）。

### 约束

1. **DESIGN_GAP 配对**：本任务 P4-implementation.md 全文（批次 1/批次 2/重试 1 三节）均声明
   "SCOPE/DESIGN_GAP/CLARIFY 声明：无"，请自己核实这个声明是否属实（读 P4-implementation.md
   确认三节都无 `[DESIGN_GAP]` 行），如属实则本项检查结论为"无 DESIGN_GAP 需配对"，不需要
   伪造配对项。
2. **SCOPE+ 闭环核实**：P2-design.md 正文含一处 `### [SCOPE+] 发现：BDD-10 豁免清单遗漏第 5
   类边界文档` 小节，但这不是常规意义上"P1 需要新增功能范围"的 SCOPE+（不是新功能需求增补），
   而是"验收清单授权缺口"的发现，走的是 `[BASELINE_CHANGE]` 机制而非
   `[SCOPE+]`/`[SCOPE_RESOLVED]` 机制——请核实 P1-requirements.md 全文确实没有
   `[SCOPE+]`/`[SCOPE_RESOLVED]` 标记（意味着按字面判据"SCOPE+ 闭环"检查项不适用，不是遗漏），
   同时要点出 P1-requirements.md 含 2 处 `[BASELINE_CHANGE]` 标注（BDD-10 正文 + 3.2 节各一处，
   对应 6 类豁免中的第 5/6 类），核实这 2 处标注是否都写明了理由、是否都在正确的位置（详见约束 3）。
3. **BASELINE_CHANGE 全链路收敛核实（本任务特有的重点检查）**：核实以下三处现在互相一致，都指向
   同一个"6 类豁免"最终状态：
   - P1-requirements.md BDD-10 正文（第 4 节）与 §3.2 边界案例表，是否都列出 6 类豁免且措辞
     对应（不要求逐字相同，但类别数量、每类指向的文件/目录必须一致）
   - P6-evidence/bdd-10-residual-scan.txt（第 2 轮，当前生效版本，注意不是 `.archived/` 下的
     第 1 轮版本）是否按这 6 类豁免给出"剩余命中数为 0"的结果
   - P6.5-judge-verdict.md（第 2 轮，当前生效版本）BDD-10 结论是否为 PASS 且引用了 6 类豁免
     已正式授权这一事实
   - `agate/tests/regression/test_repo_url_no_stale_rename.py` 的 `_is_exempt()` 函数逻辑
     是否与 P1 正式授权的 6 类豁免范围一致（不多不少）
4. **跨文件一致性核对（常规检查项）**：
   - P1 BDD 数量（16）与 P6-acceptance.md（第 2 轮，当前生效版本）PASS 数量（16）是否匹配
   - P2-design.md 声明的 `packages: [agate-brand-docs, agate-installer-scripts,
     agate-repo-admin]` 是否与 P4 实际改动文件的范围吻合（README/CHANGELOG → brand-docs；
     install.sh/agate-install.py/agate-changes.py → installer-scripts；GitHub 改名 + remote
     迁移 → repo-admin，无源码 diff 的运维类改动）
   - P4 实现路径（README.md/README.zh-CN.md/CHANGELOG.md/install.sh/agate-install.py/
     agate-changes.py 6 个文件的编辑 + GitHub 改名 + remote 迁移）与 P2-design.md §0.1 影响面
     表 + 候选方案 B 的编排设计是否吻合
   - P2 packages 与 P8 release 的 bump 范围一致性检查：**P8 尚未执行**，本项检查在 P7 阶段
     无法完整核对（P8 产出还不存在），请如实标注"P8 尚未产出，本项留待 P8 阶段自行核对
     packages 覆盖是否完整"，不要凭空判定一致/不一致
5. **CODE-MAP 核对**：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 描述的是 agate 协议本体的 5 大
   模块（phase-cards/execution-roles/review-roles/scripts/templates/rules），**不追踪
   `agate/tests/` 目录**。本任务 P3 阶段新增了 1 个文件
   `agate/tests/regression/test_repo_url_no_stale_rename.py`（P4「新增文件核对表」批次 1 节
   写"本批次未新增任何文件"，指的是 P4 批次 1 本身没新增文件——这个新文件是 P3 阶段新增的，
   P3 没有"新增文件核对表"机制，需要你在 P7 补做这个核对）。请判定该文件是否需要更新
   CODE-MAP.md（参考：不属于 CODE-MAP 描述的 5 大模块范畴，是测试脚手架，可判定
   `[CODE_MAP_EXEMPT: 理由]`），并相应填写 frontmatter 的 `code_map_new_files_count` /
   `code_map_reviewed_count` 字段（自己判断，不要照抄本段结论，按你实际核实的结果填写）。
6. **无 [NEED_CONFIRM]/[BLOCKER]/[DEVIATION-CRITICAL] 核实**：核实 P1-requirements.md 全文
   确实没有这三种残留标记（P0 阶段已确认无漂移，P1 已 [NO_NEED_CONFIRM]，P6/P6.5 均已 PASS，
   预期本项检查结论干净）。

### 上游关联

- P1-requirements.md（含 2 处 `[BASELINE_CHANGE]` 标注）
- P2-design.md（含 `[SCOPE+] 发现` 小节，性质见约束 2）
- P4-implementation.md（三节：批次 1/批次 2/重试 1）
- P6-acceptance.md（**第 2 轮，当前生效版本**，commit `b804cd8`）
- P6.5-judge-verdict.md（**第 2 轮，当前生效版本**，commit `7bac49c`，status: passed）
- 第 1 轮的 P6-acceptance.md/P6-evidence/、P6.5-judge-verdict.md 已归档至 `.archived/`，仅供
  你了解历史脉络，不作为本次一致性检查的判定依据（判定依据是当前生效版本）

### 输入文件（按顺序读，P7 输入数量豁免不拆分）

1. `agate-workspace/tasks/TAG0025-agateon-rename/P0-brief.md`
2. `agate-workspace/tasks/TAG0025-agateon-rename/P1-requirements.md`
3. `agate-workspace/tasks/TAG0025-agateon-rename/P2-design.md`
4. `agate-workspace/tasks/TAG0025-agateon-rename/P4-implementation.md`
5. `agate-workspace/tasks/TAG0025-agateon-rename/P6-acceptance.md`
6. `agate-workspace/tasks/TAG0025-agateon-rename/P6.5-judge-verdict.md`
7. `agate-workspace/agents/CODE-MAP.md`
8. `agate/tests/regression/test_repo_url_no_stale_rename.py`（仅需读 `_is_exempt()` 函数与
   文件顶部注释，核对约束 3/5）

### 产出文件字段
`P7-consistency.md` frontmatter 含 `blocker_count`/`deviation_count`/
`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count`/
`code_map_new_files_count`/`code_map_reviewed_count`。用
`FILE={AGATE_WORKSPACE}/tasks/TAG0025-agateon-rename/P7-consistency.md agate-md-field-set
--list` 查看应填字段。
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
- P6 第 2 轮 commit：`b804cd8`；P6.5 第 2 轮 commit：`7bac49c`（当前 HEAD）
- P1-requirements.md 含 2 处 `[BASELINE_CHANGE]`：BDD-10 正文一处（第 5/6 类豁免）+ §3.2 边界
  案例表一处（同源，表格形式的镜像标注）
- P4-implementation.md 三节均声明"SCOPE/DESIGN_GAP/CLARIFY 声明：无"
- CODE-MAP.md 描述范围明确限定在 5 大模块（phase-cards/execution-roles/review-roles/scripts/
  templates/rules），不含 `agate/tests/`
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
