# P7-dispatch-context-protocol-alignment-review — TAG0023 协议-脚本对齐审查

> 派发对象：protocol-alignment-review（self-gate 语义审查）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> 触发依据：本任务 P4 阶段改动了 9 个 self-gate 触发文件（`agate/scripts/*.py` 4 个 + `agate/*.md`/`agate/**/*.md` 5 个），P4 commit 已声明"完整 protocol-alignment-review 于 P7/P8 统一派发"，本轮兑现该承诺。

## 目标

对本任务 P4 阶段改动的 9 个协议文件做完整的 A1-A7 语义一致性审查，产出审查报告，落盘到 `{project_root}/docs/reviews/agate-alignment-review-2026-08-25-TAG0023.md`。

## 本次改动范围（审查对象）

**脚本（4 个）**：
- `agate/scripts/check-state-transition.py`（新增门槛失败事件↔retries对应性校验，检查3）
- `agate/scripts/check-gate.py`（`gate_p8()` 新增 `_check_roadmap_done()` 分支）
- `agate/scripts/check-debt.py`（`_retreat_coverage()` 改用动态 `_short_hash()`）
- `agate/scripts/agate-frontmatter-check.py`（错误消息增强，"补"/"改用"修复提示）

**协议文档（5 个）**：
- `agate/rules/state-transitions.md`（新增"单步回退必须同步写 retries"表述）
- `agate/state-machine.md`（新增两处"该步骤现由 check-state-transition.py 机械校验"表述）
- `agate/dispatch-protocol.md`（新增"评审 rejected 后必须写 retries"+「评审打回后的意见回流」节命名强制措辞）
- `agate/WORKFLOW.md`（Pre-commit 检查总览表 2.3 行更新 + 新增"评审被拒必须写 retries"提示）
- `agate/assets/templates/dispatch-prompt.md`（新增"P1/P2 声明写时自检"小节）

## 审查重点（逐项，按角色文件 A1-A7 清单）

1. **A1 文档→脚本对齐**：`state-transitions.md`/`state-machine.md`/`dispatch-protocol.md`/`WORKFLOW.md` 新增的"机械校验"表述，是否与 `check-state-transition.py` 检查3 的实际实现（BDD-1/3 WARNING 不阻断、BDD-2 阻断）语义一致（阻断 vs WARNING 的强度措辞是否精确）
2. **A2 脚本→文档对齐**：`check-gate.py` 新增的 `_check_roadmap_done()` 是否已在对应文档（`WORKFLOW.md`/`state-machine.md`/P8 卡片）有同步说明？（**已知信息**：本任务 P2-design.md 已充分设计此分支，但 P8 阶段卡片本身`{agate_root}/phase-cards/P8-release.md`目前是否提及 roadmap done 校验，需要你实际去读，本次改动未涉及该卡片文件本身，需判断是否属于遗漏的反向传播）
3. **A3 反向传播**：`agate/scripts/check-debt.py` 的行为变化（固定切片→动态计算）是否需要同步到消费方文档？`agate/assets/templates/dispatch-prompt.md` 新增的"写时自检"小节是否需要同步到 `agate/dispatch-protocol.md`/`agate/WORKFLOW.md`（角色文件提示词一致性）？
4. **A4 测试覆盖**：本任务 P5 全量 pytest 结果（1238 passed/2 skipped）+ P4/P4-retry 各批测试结果，**必须附最近一次全量 pytest 实跑输出**（可引用 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P5-test-results/unit.md`，或你自己重跑一次）
5. **A5 下游影响 + 文档传播**：本次改动是否有破坏性变更（如 `check-state-transition.py` 新增检查3 是否可能影响其他现存任务的 pre-commit 行为）？CHANGELOG.md 是否需要标注（本任务尚未到 P8，CHANGELOG 更新是 P8 的工作，本轮只需确认"待 P8 更新"这一点，不要求本轮完成）
6. **A6 锚点表覆盖**：`agate/scripts/check-protocol-consistency.py` 的 CHECK 9 锚点表是否需要新增本次改动涉及的新校验点
7. **A7 设计原则一致性**：对照 `agate/adr.md` 相关 ADR，检查本次改动（尤其"检查3 对应性校验"这类新增机械校验机制）是否符合已记录的设计原则，有无需要补充新 ADR 的架构决策

## 已知背景（供审查参考，不预设结论）

- 本任务的完整方案设计见 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`
- 本任务的完整实现总结见 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`
- P4 review 迭代中发现并修复的 4 条 CRITICAL 见 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-review.md`（第2轮 approved）
- 全量测试结果见 `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P5-test-results/unit.md`

## 输入文件

1. `git diff 4e8a852..HEAD -- agate/scripts/check-state-transition.py agate/scripts/check-gate.py agate/scripts/check-debt.py agate/scripts/agate-frontmatter-check.py agate/rules/state-transitions.md agate/state-machine.md agate/dispatch-protocol.md agate/WORKFLOW.md agate/assets/templates/dispatch-prompt.md`（本任务全部协议改动，`4e8a852` 是 TAG0023 P0 完成时的 commit，即本任务改动前的基线）
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`
3. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-implementation.md`
4. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P5-test-results/unit.md`
5. `{agate_root}/scripts/check-protocol-consistency.py`（CHECK 9 锚点表定义处）
6. `{agate_root}/adr.md`
7. `{agate_root}/phase-cards/P8-release.md`（A2 反向传播核对用）
8. `{agate_root}/assets/review-roles/protocol-alignment-review.md`（角色定义）

## 分阶段落盘

留痕文件：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P7-alignment-review-trace.md`（开始前 `rm -f` 清空，逐条 `echo >>` 追加原始痕迹，不整理格式）

## 产出

`{project_root}/docs/reviews/agate-alignment-review-2026-08-25-TAG0023.md`（按角色文件「输出格式」，含 review_date/reviewer/change_summary/files_changed frontmatter + A1-A7 逐项审查表 + 详细审查内容）

## 门槛

- A1-A7 每项都有明确三态结论（ALIGNED/MISALIGNED/NEEDS_HUMAN_REVIEW）
- 每项引用文档原文（行号）+ 脚本代码（行号）
- A4 附真实 pytest 实跑输出引用（不能是"应该没问题"）
- 若发现 MISALIGNED，具体说明差异 + 修复方向（不由你直接改代码）

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（A1-A7 结论汇总，≤50字）。绝不返回文件全文。

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
