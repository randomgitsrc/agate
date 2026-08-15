---
phase: P7
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: protocol-alignment-review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

self-gate 协议-脚本对齐审查（P2-design §3.6 / SELF-GATE 流程）：TAG0014 改动面大（agate/dispatch-protocol.md + agate/scripts/agate-md-field-get.py + agate/scripts/check-gate.py + 8 个阶段卡 + architect.md + dispatch-prompt.md + task-files.md + README/CHANGELOG/UPGRADING），独立上下文审查协议文档与脚本的语义一致性。产出 docs/reviews/agate-alignment-review-TAG0014.md（P4 commit message 已引用此路径）。

### 约束

- **审查范围**：P4 commit（772bbc2）改动的全部文件——按 A1-A7 审查清单逐项检查，每项输出结论（ALIGNED / MISALIGNED / NEEDS_HUMAN_REVIEW）。
- **重点审查项**：
  - A1 文档→脚本：dispatch-protocol 权威节（工作量评估五维/五模式/模式 4/并行规则/全阶段表）→ check-gate.py dispatch_plan 校验逻辑是否语义一致（mode 枚举 5 值 / parallel_limit≥1 / batch id+complexity / 批数≤limit）
  - A2 脚本→文档：agate-md-field-get.py 新 op dispatch_plan（KNOWN_OPS 注册 / JSON_FIELDS / json.dumps / frontmatter-only）→ P2-design 卡片字段契约说明是否同步
  - A3 一致性连锁 + 反向传播：P1-P8 卡片引用权威节是否完整；阶段特定约束（N7：P4 隔离/共享文件、P5 端口/数据库、P6 证据并行+汇总 verifier）是否在卡片保留；**反向传播**——列出"应该被这次改动影响但未列在 diff 中的文件"逐一验证
  - A4 测试覆盖：**必须附最近一次 pytest 全量实跑输出**（pytest 780 passed / consistency 0 ERROR / count 782 已在 P5/P6 实测）；8+2 条 dispatch_plan 用例是否覆盖新逻辑边界
  - A5 下游影响 + 文档传播：dispatch_plan 可选字段向后兼容声明；CHANGELOG/UPGRADING [0.49.0] 是否标注；影响既有项目 gate 行为？（不应——缺字段跳过）
  - A6 锚点表覆盖：CHECK 9 锚点表是否需要更新（新增 op dispatch_plan 是否影响 check-gate.py 锚点）
  - A7 设计原则一致性：对照 agate/adr.md
- **DESIGN_GAP 优先核查（原则 6）**：审查对象关联 TAG0014 任务，先检查 P4-implementation.md / P7-consistency.md 是否已有对应 [DESIGN_GAP:] / [DESIGN_GAP_REVIEWED:] 记录；已被 P7 独立核实且 REVIEWED-ACCEPTED 的不判 MISALIGNED，标注 KNOWN_DEVIATION。
- **只写报告不改代码**：审查角色只写报告，修复由主 Agent 派 implementer 落地。
- **输出路径硬约束**：产出 docs/reviews/agate-alignment-review-TAG0014.md（{project_root}/docs/reviews/ 下，文件名含任务编号以区分既有 agate-alignment-review-2026-08-15.md）。

### 上游关联

- P4 commit：772bbc2（实现 + self-gate-review 标记已引用本报告路径）
- P7-consistency.md：consistency-reviewer 已产出（BLOCKER=0，2/2 DESIGN_GAP REVIEWED）
- P6-acceptance.md：22/22 BDD PASS
- P2-design §3.6：self-gate 流程设计

### 输入文件

- {project_root}/agate/scripts/agate-md-field-get.py（审查对象）
- {project_root}/agate/scripts/check-gate.py（审查对象）
- {project_root}/agate/dispatch-protocol.md（审查对象）
- {project_root}/agate/phase-cards/P{1..8}-*.md（审查对象）
- {project_root}/agate/assets/execution-roles/architect.md（审查对象）
- {project_root}/agate/assets/templates/dispatch-prompt.md + task-files.md（审查对象）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P7-consistency.md（DESIGN_GAP 优先核查）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P4-implementation.md（DESIGN_GAP 记录）
- {project_root}/agate/assets/review-roles/protocol-alignment-review.md（角色定义）
- {project_root}/SELF-GATE.md（self-gate 流程）
- {project_root}/agate/adr.md（A7 设计原则）
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
- 审查对象版本：worktree 当前（P4 commit 772bbc2 后）
- 实测证据（P5/P6）：pytest 780 passed / consistency 0 ERROR（279 WARNING 既有基线）/ count 782；22/22 BDD PASS
- 既有审查报告：docs/reviews/agate-alignment-review-2026-08-15.md（上次任务，可参照格式）
- P7-consistency.md 已确认 2/2 DESIGN_GAP REVIEWED（P4 修复轮的 README badge 还原 + P2-design YAML 修复——若审查涉及，按原则 6 处理）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
