> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P7
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0004
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P7-consistency.md`——TAG0004 跨文件一致性审查。对照 P1-P6 产出，重点：DESIGN_GAP 配对（P4 的 [DESIGN_GAP] 转抄 + REVIEWED）、SCOPE+ 闭环（P4 的 [SCOPE+] 增补确认纳入基线）、跨文件一致性（P1 BDD 数 vs P6 验收数、P2 packages vs 实际改动、P4 实现 vs P2 方案）、未决项清零。

### 约束

- **本任务 P4 有 1 个 [DESIGN_GAP] + 1 个 [SCOPE+]（+1 个 [SCOPE_GAP] 已闭环）**，必须逐条处理：
  1. **组 2 的 [DESIGN_GAP]**（P4-implementation-group2.md）：P2 候选 11A 未明确"formatter 检测到 NameError 但无 project_module 前缀匹配"（裸符号/前缀不匹配）时的归类——实现选择"只要 formatter 检测到 NameError 即判 B 类"，非 NameError（TypeError 等）由 pytest.sh 精确解析 + errors>0 分支兜底仍 A 类。**审查**：该决策是否合理（TDD 红灯正常状态 = 引用未实现符号；BDD-35/36/37 全绿证明边界守住了）→ 标 `[DESIGN_GAP_REVIEWED: 已确认]`
  2. **组 1 的 [SCOPE+]**（P4-implementation-group1.md）：pre-commit-gate.sh L290（2n.1 分支）与 L104 同缺陷模式（`^${TASK_REL}` 拼入 grep -E），一并按同方案改造。**确认**：该增补是否已纳入 P1 基线（P1 是否需补 [SCOPE_RESOLVED]）
  3. **组 1 的 [SCOPE_GAP]**：bdd-14（M6 CRLF frontmatter）不在组 1 职责内——已由 m6-shell 补充实现，P6 BDD-14 PASS。该 SCOPE_GAP 已闭环（不阻塞，但 P7 应记录闭环事实）
- **跨文件一致性检查项**（逐条引用源文件节名）：
  - P1 BDD 37 条 vs P6 验收 37 条（PASS 37 / FAIL 0）数量匹配？
  - P2 packages（agate-scripts-sh/py、phase-cards、docs、gitconfig、ci、tests）vs P4 实际改动范围一致？
  - P2 方案（候选 1A-16A）vs P4 实现路径吻合（每组修复落在 P2 选定方案上）？
  - P2 gate_commands.P5 vs P5-test-results 执行命令一致？
  - P6 evidence 文件引用 vs P6-evidence/ 目录实际文件存在？
- **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]、[BLOCKER]、[DEVIATION-CRITICAL]。
- **frontmatter 机器计数**：blocker_count / deviation_count / deviation_critical_count / design_gap_count / design_gap_reviewed_count（见样例）。
- **结论必须引用实质锚点**：BLOCKER=0 须配 DESIGN_GAP 配对项 + REVIEWED 标记；CRITICAL=0 须配跨文件检查项 + 源文件节名（如 `P1§BDD-35`、`P2§1.11`、`P4§group2`）；SCOPE+ 闭环须列条目 + [SCOPE_RESOLVED]。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`。改用"通过/失败"或加引号。

### 上游关联

- P1-requirements.md approved：37 BDD、无 NEED_CONFIRM、无 GAP。
- P2-design.md approved：候选 1A-16A、packages 7 项、gate_commands.P5。
- P4 五份实现（group1/2/3a/3b/m6-shell）：1 DESIGN_GAP + 1 SCOPE+ + 1 SCOPE_GAP（闭环）。
- P6-acceptance.md：37/37 PASS、0 FAIL、证据 41 文件。

### 输入文件

- `agate-workspace/tasks/TAG0004-env-adaptation/P1-requirements.md`（BDD + SCOPE+ 状态）
- `agate-workspace/tasks/TAG0004-env-adaptation/P2-design.md`（packages/方案）
- `agate-workspace/tasks/TAG0004-env-adaptation/P4-implementation-group1.md` / `-group2.md` / `-group3a.md` / `-group3b.md` / `-m6-shell.md`（DESIGN_GAP/SCOPE+ 声明）
- `agate-workspace/tasks/TAG0004-env-adaptation/P6-acceptance.md`（BDD 验收结果）
- `agate-workspace/tasks/TAG0004-env-adaptation/P5-test-results/`（验证结果）
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
6. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`；协议 v0.43.0；P6 已 commit（c8653b8）
- 关键路径：产出 `agate-workspace/tasks/TAG0004-env-adaptation/P7-consistency.md`
- 查证结果：P4 有 1 DESIGN_GAP（组 2 NameError 归类）+ 1 SCOPE+（组 1 L290）+ 1 SCOPE_GAP（m6-shell 已闭环）；P6 37/37 PASS
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
