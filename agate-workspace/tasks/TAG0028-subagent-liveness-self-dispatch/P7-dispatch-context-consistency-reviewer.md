---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0028
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P7-consistency.md`：对照 P1-P6 产出做跨文件一致性交叉检查，确保实现未偏离设计。
核心任务：**DESIGN_GAP 逐条配对**（P4 声明 → P7 转抄 + REVIEWED）+ SCOPE+ 闭环 + 跨文件一致性 +
未决项清零 + CODE-MAP 核对。

### 约束

1. **DESIGN_GAP 配对（红线）**：P4-implementation.md 中声明的 DESIGN_GAP 必须在 P7-consistency.md
   逐条转抄（行首 `[DESIGN_GAP: ...]`）+ 配 REVIEWED 标记（行首 `[DESIGN_GAP_REVIEWED: ...]`）。
   P4 现有 4 条 DESIGN_GAP：
   - GAP-1（P3 测试缺陷 test_bdd_3）：P4-implementation.md 已含 `[DESIGN_GAP_REVIEWED: 已确认...]`
     标记——P7 转抄原始标记行 + REVIEWED 行（gate 扫描 P7 文件）
   - GAP-2（ts_end int|None 放宽，CRITICAL-3 修复需要）
   - GAP-3（DSH 截断双信号启发式，Q6 未给字段名）
   - GAP-4（expected 接入用 CLI --expected N 参数）
   后 3 条在 P4-implementation.md「### fix1」节 268-282 行，无 REVIEWED——P7 须逐条审查并给
   `[DESIGN_GAP_REVIEWED: 已确认/已打回 P2]`。
2. **SCOPE+ 闭环**：P1-requirements.md 若有 [SCOPE+] 增补，须有 [SCOPE_RESOLVED]（本任务 P1-P4
   未标 SCOPE+，核对后如无则写"无 SCOPE+ 增补"）。
3. **跨文件一致性（引用具体锚点，非裸"一致"）**：
   - P2 packages（[agate]）与 P8 release bump 范围一致
   - P1 BDD 数量（33）与 P6 验收结果数量（33 PASS / 0 FAIL）匹配
   - P4 实现路径（agate/scripts/agate-cmdstream-*.py 三脚本 + 协议改写）与 P2 方案 A 吻合
   - P6.5 judge verdict（33/33 passed）与 P6 对照
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM] / [BLOCKER] / [DEVIATION-CRITICAL]
   （P1 已写 [NO_NEED_CONFIRM]）。
5. **CODE-MAP 核对**：对照 `agate-workspace/agents/CODE-MAP.md` 与 P4「新增文件核对表」
   （3 个新脚本登记）逐条判定 [CODE_MAP_SYNC:] / [CODE_MAP_DRIFT:]。
6. **产出 Header**：P7-consistency.md frontmatter 含 phase=P7 / task_id=TAG0028 / type=consistency /
   parent=P2-design.md / trace_id=TAG0028-P7-20260903 / status=draft→approved / created=2026-09-03 /
   agent=consistency-reviewer / blocker_count=0 / deviation_count / deviation_critical_count=0 /
   design_gap_count=4 / design_gap_reviewed_count=4 / code_map_new_files_count=3 /
   code_map_reviewed_count（可选，语义对应 design_gap_reviewed_count）。
7. **无行首 PASS/FAIL 预判**：P7 产出禁止行首 `- PASS` / `- FAIL` 格式。

### 上游关联

- P1-requirements.md（33 BDD + [NO_NEED_CONFIRM] + 同类扫描）
- P2-design.md（方案 A + packages=[agate] + gate_commands）
- P4-implementation.md（DESIGN_GAP 4 条 + 新增文件核对表）
- P6-acceptance.md（33 PASS / 0 FAIL）
- P6.5-judge-verdict.md（33/33 passed）
- CODE-MAP.md（新增文件登记核对）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P1-requirements.md`
2. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md`
3. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P4-implementation.md`（重点 DESIGN_GAP 4 条 + 新增文件核对表）
4. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P6-acceptance.md`
5. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P6.5-judge-verdict.md`
6. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P0-brief.md`
7. `agate-workspace/agents/CODE-MAP.md`
8. `agate/assets/execution-roles/consistency-reviewer.md`（角色定义）
9. `AGENTS.md`（项目约定）

### 产出文件字段

产出 `P7-consistency.md` 到任务目录，frontmatter 用 `agate-md-field-set` 填写（先 `--list`；
set 报错照提示改；不要手写）：
phase=P7 / task_id=TAG0028 / type=consistency / parent=P2-design.md /
trace_id=TAG0028-P7-20260903 / status=draft→approved / created=2026-09-03 /
agent=consistency-reviewer / blocker_count=0 / deviation_count=N / deviation_critical_count=0 /
design_gap_count=4 / design_gap_reviewed_count=4 / code_map_new_files_count=3 /
code_map_reviewed_count=N。
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
### A. P4 DESIGN_GAP 清单（4 条，P7 须逐条转抄 + REVIEWED）
- GAP-1：test_bdd_3 断言结构性矛盾（P3 测试缺陷，P4-implementation.md 已含 REVIEWED——转抄原始行 + REVIEWED 行）
- GAP-2：CommandRecord.ts_end 类型放宽 int|None（CRITICAL-3 修复需要未结束 call 携带 ts_end=None）
- GAP-3：DSH 截断双信号启发式检测（Q6 未给字段名，tool-result 布尔字段 + 文本字面量）
- GAP-4：expected 接入用 CLI --expected N 参数（per-command 语义，maintainability.yaml 无对应键）

### B. 跨文件数量锚
- P1 BDD = 33（#### BDD-NN: 标题数）；P6 验收 = 33 PASS / 0 FAIL；P6.5 judge = 33/33 passed
- P2 packages = [agate]；P4 implementation_dir = agate/scripts/；新增文件 = 3 脚本
- CODE-MAP.md 已登记 3 新脚本（P4 新增文件核对表核对）

### C. 环境
- worktree 根 = /home/kity/oclab/agateon/.worktrees/agate-TAG0028
- 任务目录 = agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
