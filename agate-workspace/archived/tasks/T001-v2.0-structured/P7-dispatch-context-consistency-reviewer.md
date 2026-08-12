> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P7
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: consistency-reviewer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对 T001（agate v0.40.0 结构化数据改造）做 P1-P6 全链路一致性交叉检查，产出 `docs/tasks/T001-v2.0-structured/P7-consistency.md`。核心工作是逐条裁决 `P4-implementation.md` 里的 7 条 `[DESIGN_GAP:]`——**这些是设计与实现之间的已知偏离，需要你独立判断"这个偏离是否可接受"，不是机械转抄**。

### 约束

1. **DESIGN_GAP 逐条裁决（本阶段最核心的工作）**：`P4-implementation.md` 里有 **7 条**（不是常见默认的更少数量，自己 `grep -c "^\[DESIGN_GAP:" docs/tasks/T001-v2.0-structured/P4-implementation.md` 核实）：
   - 2 条来自流 A（`check-gate.sh`/`check-pruning.sh` 未迁移到双读工具）
   - 2 条来自流 B（P6 回退正则比设计原文宽松；P6/P7 新旧格式判定用 AND 语义）
   - 1 条来自流 C（`check-scope-resolved.sh` 对"字段存在但空列表"与"字段不存在"未区分）
   - 2 条来自流 D（`check-changelog.sh` 移除设计要求保留的 fallback；硬切正则触发的 33 个既有测试回归——**这一条已经在 commit `68e4173` 修复并独立验证过**，不是仍然开放的偏离，你转抄时要如实反映"已解决"这个状态，不要当成还悬而未决）
   
   **对每一条，你需要**：
   - 独立读取涉及的代码文件（不是只信 P4-implementation.md 的自述），核实描述与实际代码是否一致
   - 判断这个偏离本身是否可接受（复现/验证过其合理性 — 比如流B第一条的理由是"严格正则会让既有测试回归"，你可以自己验证一下这个理由是否站得住）
   - 在 `P7-consistency.md` 里逐条转抄 + 加 `[DESIGN_GAP_REVIEWED: 你的裁决 + 理由]`（行首格式，不要句中引用）
   - 如果你认为某条 DESIGN_GAP 事实上不可接受（比如判断依据站不住、或者有更简单的正确做法没被采用），**不要自己去改代码**——按 BLOCKER 处理，在报告里说明，交主 Agent 决定是否需要再退回 P4
2. **SCOPE+ 闭环检查**：`P1-requirements.md` 应该有 1 个 `[SCOPE_RESOLVED]` 标记（对应 `P2-design.md` 的 1 处 `[SCOPE+]`），确认这个闭环成立——找到具体的 SCOPE+ 内容和对应的 SCOPE_RESOLVED 内容，核实语义匹配（不是只看标记存在）。
3. **跨文件一致性核对**（引用具体章节，不要写"一致"这种裸结论）：
   - `P1-requirements.md` 的 28 条 BDD 与 `P6-acceptance.md` 的验收结果数量匹配（28 PASS / 0 FAIL，含 BDD-11 因 `[BASELINE_CHANGE: 594→597]` 从 FAIL 改判 PASS 的特殊情况——`P6-evidence/bdd11-test-count.md` 有完整判定变更记录，你需要确认这个变更过程本身是否合规，不是简单看最终数字对不对）
   - `P2-design.md` 声明的 `packages: [agate]` 与后续 P8 发布的 bump 范围是否一致（P8 还没做，这里主要确认 P2 声明和 P4 实际改动的文件范围是否都落在 `agate/` 目录内，没有意外触碰其他范围）
   - `P4-implementation.md` 的实现路径（流A/B/C/D + Review修复 + P6回退修复 六个小节涉及的文件清单）与 `P2-design.md` §6 files_to_read 声明的文件范围是否吻合
4. **未决项清零**：确认 `P1-requirements.md` 无残留行首 `[NEED_CONFIRM]`（P1-review.md 应已是 approved，NEED_CONFIRM 应已清零；本次新加的 `[BASELINE_CHANGE:]` 标注不是 NEED_CONFIRM，不冲突）、无 `[BLOCKER]`、无 `[DEVIATION-CRITICAL]`。
5. **frontmatter 汇总字段要求（本任务自身也要遵守 BDD-19/20 的格式，dogfooding 但要避开已知的 P6-acceptance.md 那个坑）**：`P7-consistency.md` 的 frontmatter 需要 `blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count` 五个字段（int）——**这几个字段和 P6-acceptance.md 那次的 pass:/fail: 不是同一个坑**：`check-p6-format.sh --fix` 只对"P6-acceptance.md"这个精确文件名生效（脚本开头有文件名判断 `if [[ "$basename_check" != P6-acceptance.md ]]; then exit 0; fi`），P7-consistency.md 不受影响，可以放心按设计样例（阶段卡片给的 frontmatter 样例）正常写这几个字段，不需要规避。
6. **不要修改任何代码/测试/其他阶段产出文件**——你是纯审查角色，发现 BLOCKER 只报告，不自己修。
7. **产出 `docs/tasks/T001-v2.0-structured/P7-consistency.md`**，Header 含 `status` 字段（approved/rejected/needs-revision，映射规则见角色定义）。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（7 条 DESIGN_GAP 的完整声明+理由，本次核心审查对象）
- `docs/tasks/T001-v2.0-structured/P6-acceptance.md` + `P6-evidence/`（28 BDD 验收结果，含 BDD-11 判定变更记录）
- `docs/tasks/T001-v2.0-structured/P1-requirements.md`（含新加的 `[BASELINE_CHANGE:]` 标注）
- `docs/tasks/T001-v2.0-structured/P2-design.md`（设计依据，files_to_read/packages 声明）

### 输入文件（自己读）

- `agate/assets/execution-roles/consistency-reviewer.md`（你的角色定义，先读这个）
- `docs/tasks/T001-v2.0-structured/P0-brief.md`
- `docs/tasks/T001-v2.0-structured/P1-requirements.md`
- `docs/tasks/T001-v2.0-structured/P2-design.md`
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（全文，7 条 DESIGN_GAP）
- `docs/tasks/T001-v2.0-structured/P6-acceptance.md` + `docs/tasks/T001-v2.0-structured/P6-evidence/`
- 涉及 DESIGN_GAP 的实际代码文件（`agate/scripts/check-gate.sh`、`agate/scripts/check-pruning.sh`、`agate/scripts/check-scope-resolved.sh`、`agate/scripts/check-changelog.sh`）——按需读取，核实 DESIGN_GAP 描述与实际代码一致
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
6. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
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
- 环境状态：worktree `feat/v2.0`，HEAD `8c38c2f`（P6 验收通过后）。`.state.yaml` phase=P6 status=active（P7 产出后，主 Agent 会在同一个 commit 里把 phase 推进到 P7）。
- P4-implementation.md 的 7 条 `[DESIGN_GAP:]` 分布：流A×2（行 78/86）、流B×2（行 196/198）、流C×1（行 342）、流D×2（行 446/448，其中行 448 那条已在 commit 68e4173 修复解决）。
- P6 验收：28 PASS / 0 FAIL，BDD-11 有 `[BASELINE_CHANGE: 594→597]` 特殊处理记录。
- P1-requirements.md 有 1 处 `[SCOPE_RESOLVED]`（对应 P2-design.md 1 处 `[SCOPE+]`）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
