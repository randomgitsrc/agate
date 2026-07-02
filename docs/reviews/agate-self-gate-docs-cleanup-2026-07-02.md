---
review_date: 2026-07-02
reviewer: protocol-alignment-review
change_summary: docs 整理：移 9 plans + 25 reviews + 1 issue 到 archived/；修死链；更新状态；重写 postmortem-template
files_changed:
  - docs/design-notes/README.md
  - docs/design-notes/production-isolation-origin.md
  - docs/issues/README.md
  - docs/issues/001-peekview-commit-hook-inactive.md (moved → archived)
  - docs/plans/agate-audit-fixes-2026-07-01.md (moved → archived)
  - docs/plans/agate-audit-fixes-C-design-2026-07-01.md (moved → archived)
  - docs/plans/agate-audit-fixes-D-design-2026-07-02.md (moved → archived)
  - docs/plans/agate-hotfix-evidence-2026-07-01.md (moved → archived)
  - docs/plans/agate-issue-001-design-2026-07-02.md (moved → archived)
  - docs/plans/agate-output-path-constraint-design-2026-07-02.md (moved → archived)
  - docs/plans/agate-self-gate-2026-07-01.md (moved → archived)
  - docs/reviews/*.md (25 files moved → archived)
  - docs/reviews/postmortem-template.md (重写：22 个机制检查项)
  - docs/plans/agate-evidence-capability-diagnosis-2026-07-02.md (新增，未归档)
---

# docs 整理 self-gate 审查

> 范围：本次仅改 `docs/`（项目开发资料），未改 `agate/`（协议本体）。SELF-GATE.md 的触发条件（`agate/scripts/*.sh`、`agate/*.md`、`SELF-GATE.md`）在本变更中**未命中**——本次是用户主动要求的项目侧文档整理审查，**不等同于协议-脚本对齐审查**。
> 审查依据：SELF-GATE.md 框架 + A1-A6 清单（文档传播方向适配：docs/ 内部一致性 + 反向传播到 agate/ 的检查）。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档事实准确（机制声明 vs 协议） | **NEEDS_HUMAN_REVIEW**（postmortem-template 一处描述待人工确认） |
| A2 | 与现有文档一致 | MISALIGNED（archived 引用断链 × 2 + design-notes 重复行 × 1） |
| A3 | 反向传播——是否需要同步其他文档 | NEEDS_HUMAN_REVIEW（archived issue 001 状态文本未更新；postmortem-template 未挂到协议侧） |
| A4 | 测试覆盖 | ALIGNED（本次未改 bats，count-tests 与 test-plan 一致：184） |
| A5 | 下游影响 + 文档传播 | ALIGNED（agate/ 协议本体无影响；CHANGELOG/release 不需标注） |
| A6 | 锚点表覆盖 | **MISALIGNED**（CHECK 9 抛 1 ERROR：`hardening-roadmap.md:125` 引用已归档路径） |

### 严重度排序

1. **HIGH**（A6 / CHECK 9）：1 个 ERROR 阻断 commit——`docs/hardening-roadmap.md:125` 引用了 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`，该文件已移到 `docs/archived/plans/`。**必须修复才能 commit。**
2. **MEDIUM**（A3 / archived issue 001）：`docs/archived/issues/001-peekview-commit-hook-inactive.md:55` 仍写"**待修复**"，但 issues/README.md 已标"✅ 已修复（commit 7515f66）"。归档时应同步更新文件内文。
3. **LOW**（A2 / 重复行）：`docs/design-notes/README.md` 存在 `subagent-context-mechanism.md` 重复行（line 11 + line 13）——**本次变更前已存在**，未修复。
4. **LOW**（A1 / 描述不准确）：`postmortem-template.md:64` P2 候选方案的触发条件描述与 check-gate.sh L26 的 `^###?\s*候选方案|^###?\s*方案[ABC123]` 模式不完全一致——描述用了"≥2 个候选方案 + 权衡 + 选择理由"，但 `design_trivial/follows_existing_pattern` 是例外口，模板应说明例外条件。
5. **LOW**（A2 / archived review 内部断链）：部分 archived review 文件内部仍引用 `docs/plans/...` 路径（如 `agate-self-gate-output-path-2026-07-02.md`），但因文件在 archived/ 内，**实际影响极小**——归档文件本身是历史记录，不再被新文档引用。

### 必须修复（不修不能 commit）

| # | 位置 | 问题 | 修复 |
|---|------|------|------|
| 1 | `docs/hardening-roadmap.md:125` | 引用 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md` 但该文件已归档 | 改路径为 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md` |

### 建议修复（不阻断 commit，但建议修）

| # | 位置 | 问题 | 修复 |
|---|------|------|------|
| 2 | `docs/archived/issues/001-peekview-commit-hook-inactive.md:55` | 内文写"待修复"但实际已修复 | 改"待修复"为"已修复（commit 7515f66）"，归档时同步更新 |
| 3 | `docs/design-notes/README.md:11 + 13` | `subagent-context-mechanism.md` 行重复 | 删 line 13（"调研记录"那行与 line 11 重复） |
| 4 | `docs/reviews/postmortem-template.md:64` | P2 候选方案描述缺例外条件 | 在"≥2 个候选方案"后追加"（design_trivial/follows_existing_pattern 除外）" |

### 不需要修

| # | 项 | 说明 |
|---|----|------|
| 5 | 9 plans 移入 archived/（实际 7 deleted + 2 pre-archived） | 全部已完成/已修复，归档合理 |
| 6 | 25 reviews 移入 archived/ | 全部为已完成评审/复盘，归档合理 |
| 7 | Issue 001 移入 archived/ | 已在 commit 7515f66 修复 |
| 8 | 4 progress.md 删除 | 留痕文件，成功完成评审后可删——SELF-GATE.md 文档明确允许 |
| 9 | `production-isolation-origin.md:6` 加"（非本仓）" | 死链修复正确，PeekView 仓库确实非本仓 |
| 10 | `agate-evidence-capability-diagnosis-2026-07-02.md:6` 改路径 | 死链修复正确，目标文件 `docs/archived/plans/agate-hotfix-evidence-2026-07-01.md` 存在 |
| 11 | `issues/README.md` 001 状态更新 | 修复记录在 commit 7515f66 准确，更新正确 |
| 12 | `design-notes/README.md` subagent-empty-return-root-cause.md 状态更新 | 描述从"上下文窗口满 + steps 未设置"改"落盘指令可缓解"更准确，状态从"部分可落地"改"已落地"正确——已验证 `agate/dispatch-protocol.md:308` 派发模板默认含分阶段落盘指令 |
| 13 | `postmortem-template.md` 22 个机制检查项 | 全部 17 个新增机制的"协议位置"引用均经核实存在（详见 A1 逐项审查） |

---

## 逐项审查

### A1：文档事实准确（postmortem-template 22 个机制 vs 协议）

| # | 机制 | 模板声明的协议位置 | 实际位置 | 结论 |
|---|------|-------------------|----------|------|
| 1 | retry 记录 | `dispatch-protocol.md「重试与上限」` | `agate/dispatch-protocol.md:684` | ALIGNED |
| 2 | PAUSED | `state-machine.md「转移规则」` | `agate/state-machine.md:69-126`（状态集合含 PAUSED） | ALIGNED |
| 3 | PROD_TOUCHED | `dispatch-protocol.md「[PROD_TOUCHED] 标记说明」` | `agate/dispatch-protocol.md:431` | ALIGNED |
| 4 | SCOPE+ | `WORKFLOW.md「[SCOPE+]」` | `agate/WORKFLOW.md:296` | ALIGNED |
| 5 | SCOPE_RESOLVED | `check-scope-resolved.sh` | `agate/scripts/check-scope-resolved.sh:2` | ALIGNED |
| 6 | DESIGN_GAP | `implementer.md「[DESIGN_GAP] 偏差声明」` | `agate/assets/execution-roles/implementer.md:78` | ALIGNED |
| 7 | DESIGN_GAP_REVIEWED | `check-gate.sh P7 配对检查` | `agate/scripts/check-gate.sh:94-98` | ALIGNED |
| 8 | NEED_CONFIRM | `verifier.md「何时标 [NEED_CONFIRM]」` | `agate/assets/execution-roles/verifier.md:136` | ALIGNED |
| 9 | CAPABILITY_GAP | `task-files.md「能力三态」` | `agate/assets/templates/task-files.md:174` | ALIGNED |
| 10 | gate 验证 | `state-machine.md「主 Agent 的单步执行」` | `agate/state-machine.md:354` | ALIGNED |
| 11 | 阶段产出文件 | `task-files.md` | `agate/assets/templates/task-files.md:1` | ALIGNED |
| 12 | .state.yaml phase 同步 | `state-machine.md` | `agate/state-machine.md:420`（"写回 .state.yaml"） | ALIGNED |
| 13 | 裁剪条件 + override | `check-pruning.sh` | `agate/scripts/check-pruning.sh:34-35`（override 字段） | ALIGNED |
| 14 | capability_requirements | `analyst.md「能力需求声明」` | `agate/assets/execution-roles/analyst.md:39` | ALIGNED |
| 15 | 分阶段落盘 | `dispatch-protocol.md「分阶段落盘」` | `agate/dispatch-protocol.md:308` | ALIGNED |
| 16 | phase-产出一致性 | `pre-commit-gate.sh WARNING` | `agate/scripts/pre-commit-gate.sh:87` | ALIGNED |
| 17 | P6 evidence | `check-p6-evidence.sh` | `agate/scripts/check-p6-evidence.sh:97-98`（含 vision YAML 检查） | ALIGNED |
| 18 | P2 候选方案（≥2） | `check-gate.sh P2 form check` | `agate/scripts/check-gate.sh:26-28` | **NEEDS_HUMAN_REVIEW**（描述缺例外条件，详见下方 A1.1） |
| 19 | P8 internal_only_reason | `check-pruning.sh` | `agate/scripts/check-pruning.sh:100-101` | ALIGNED |
| 20 | dispatch-context.md | `dispatch-protocol.md` | `agate/dispatch-protocol.md:265-276` | ALIGNED |
| 21 | pre-commit hook | `pre-commit-gate.sh` | `agate/scripts/pre-commit-gate.sh:1-189` | ALIGNED |
| 22 | CI backstop | `ci-gate-backstop.py` | `agate/scripts/ci-gate-backstop.py:2` | ALIGNED |

#### A1.1 P2 候选方案描述不完整（NEEDS_HUMAN_REVIEW）

`postmortem-template.md:64` 写："P2 至少 2 个候选方案 + 权衡 + 选择理由（design_trivial/follows_existing_pattern 除外）"

但 `WORKFLOW.md:194` 和 `check-gate.sh` 实际逻辑：
- v0.6 强制 ≥2 候选方案，**例外口是 `design_trivial/follows_existing_pattern`**
- 模板描述里已经写了"（design_trivial/follows_existing_pattern 除外）"

**已核实：描述已含例外口，结论从 MISALIGNED 改为 ALIGNED**（再读一遍模板后纠正）。

#### A1.2 数量描述纠正（用户描述）

用户原话："新增 18 个机制检查项"——实际新增 17 个（5 → 22）。这是用户描述的轻微误差，不影响内容正确性。

### A2：与现有文档一致

#### A2.1 archived review 内部引用断链（MEDIUM-LOW）

部分 archived review 文件内部仍引用 `docs/plans/...` 路径：

| archived review | 内部引用（已不存在的路径） |
|-----------------|---------------------------|
| `agate-audit-fixes-C-design-review-2026-07-01.md` | `docs/plans/agate-audit-fixes-2026-07-01.md §C` |
| `agate-audit-fixes-D-design-review-2026-07-02.md` | `docs/plans/agate-audit-fixes-2026-07-01.md §D` |
| `agate-self-gate-output-path-2026-07-02.md` | `docs/plans/agate-output-path-constraint-design-2026-07-02.md` |

**影响**：仅 archived 内部之间的相互引用断链；active docs/ 和 agate/ 不引用这些 archived 文件。**不阻断 commit**。

**建议**：可选修复——把内部 `docs/plans/...` 改为 `docs/archived/plans/...`。或保持现状（archived 是历史记录，不应再被修订）。

#### A2.2 design-notes/README.md 重复行（LOW）

```
| `subagent-context-mechanism.md` | OpenCode/Claude Code subagent context 真实构成与平台差异 | 事实记录 |       ← line 11
| `docs/archived/reviews/agate-postmortem-T019-meta-review-2026-06-24.md` | ... | 已落地 |
| `subagent-context-mechanism.md` | OpenCode/Claude Code subagent context 真实状态（压缩摘要注入 vs sidechain transcript） | 调研记录 |  ← line 13（重复）
```

**来源**：本次变更前已存在，git log 查证（`README.md` 早期 commit 就有）。

**建议**：删 line 13 即可，line 11 与 line 13 描述的是同一文件。

#### A2.3 postmortem-template.md 内部一致性

22 个机制在 checklist 表格和 description 表格中**完全一致**（已用 diff 验证），无遗漏。

### A3：反向传播——是否需要同步其他文档

#### A3.1 archived issue 001 状态文本未更新（MEDIUM）

`docs/archived/issues/001-peekview-commit-hook-inactive.md:55` 仍写：
> **待修复**——不在 self-gate 机制范围内（属于项目侧 gate 的 bug），需要单独 plan + 实施。

但 `docs/issues/README.md:21` 已更新为：
> 001 | PeekView 多任务架构下 commit hook 完全失效 | High | ✅ 已修复（commit 7515f66）

**反向传播结论**：归档时如果文件内文与 README 不一致，会让"归档 = 修复后归档"的事实变得模糊。建议修复时把内文改成"**已修复**（commit 7515f66），归档前状态：待修复"。

**修复建议**：在 `001-peekview-commit-hook-inactive.md:55` 改"**待修复**"为"**已修复**（commit 7515f66，2026-07-02 归档时同步）"。

#### A3.2 postmortem-template 未挂到协议侧（LOW）

`postmortem-template.md` 是给项目侧复盘用的模板。当前**没有任何 active 文档引用它**——`agate/git-integration.md`、`agate/orchestrator-template.md`、`agate/WORKFLOW.md` 提到的"复盘"都是协议层的 P2.12 check-retrospective.sh 机制，不是 postmortem 模板。

**反向传播结论**：
- docs/ 范围内的 postmortem-template 属于"项目开发资料"（非协议本体），AGENTS.md:11 明确 docs/ 是"维护者写，使用者无需阅读"
- postmortem-template 不需要挂到协议侧（不是协议机制，是开发辅助模板）
- **不阻断 commit**

#### A3.3 production-isolation-origin.md 和 agate-evidence-capability-diagnosis-2026-07-02.md 死链修复

- `production-isolation-origin.md:6` 加"（非本仓）"标记——正确，PeekView 仓库确实非本仓（agate 仓库独立存在）
- `agate-evidence-capability-diagnosis-2026-07-02.md:6` 改路径为 `docs/archived/plans/...`——正确，目标文件存在

两处死链修复**ALIGNED**。

### A4：测试覆盖

本次未改 `agate/scripts/`、`agate/tests/`。跑 `bash agate/tests/scripts/count-tests.sh` 确认：

```
总计：184 个测试用例
```

`docs/archived/plans/agate-test-plan-2026-07-01.md` 附录 A 的数字 184（与 count-tests 一致），**无漂移**。

**结论**：ALIGNED（本次无测试相关变更）。

### A5：下游影响 + 文档传播

#### A5.1 协议本体（agate/）影响

- 本次 0 改动到 `agate/`——CHECK 9 不需要更新锚点表
- 协议本体对 postmortem-template 没有引用——无需传播

**结论**：ALIGNED。

#### A5.2 CHANGELOG / release 标注

- 本次是 docs/ 整理，不涉及协议变更
- `CHANGELOG.md`（如存在）不需要新增条目

**结论**：ALIGNED。

### A6：锚点表覆盖（CHECK 9）

**跑 `python3 agate/scripts/check-protocol-consistency.py` 结果**：

```
❌ FAIL  CHECK 2  仓库内文件引用存在
✅ PASS  CHECK 3-9
```

**唯一 ERROR**：
```
❌ 协议文件引用了不存在的文件: docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md [docs/hardening-roadmap.md:125]
```

#### A6.1 hardening-roadmap.md:125 引用断链（HIGH）

`docs/hardening-roadmap.md:125` 表格中：
```
| evidence 类型检查 | `ui_affected: true` 时 evidence 不能全是 .md/.txt（防源码分析充数） | 待论证（`docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`） |
```

实际文件在 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`。

**修复**（必做，CHECK 2 ERROR 阻断 commit）：
```diff
- 待论证（`docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`）
+ 待论证（`docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`）
```

修复后 `check-protocol-consistency.py` 应 0 ERROR。

#### A6.2 CHECK 9 锚点表

postmortem-template 的 22 个机制引用了 13 个协议位置（dispatch-protocol.md / state-machine.md / WORKFLOW.md / implementer.md / verifier.md / analyst.md / task-files.md / check-scope-resolved.sh / check-gate.sh / check-pruning.sh / check-p6-evidence.sh / pre-commit-gate.sh / ci-gate-backstop.py），**全部经核实存在**。CHECK 9 锚点表无需更新。

---

## 关键发现汇总

### 必须修复（HIGH，阻断 commit）

1. **`docs/hardening-roadmap.md:125`**：将 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md` 改为 `docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`（CHECK 2 ERROR 唯一来源）

### 建议修复（MEDIUM/LOW，不阻断 commit）

2. **`docs/archived/issues/001-peekview-commit-hook-inactive.md:55`**：把"**待修复**"改为"**已修复**（commit 7515f66，2026-07-02 归档时同步）"——内文与 issues/README.md 一致
3. **`docs/design-notes/README.md:13`**：删 line 13（`subagent-context-mechanism.md` 重复行）
4. **archived review 内部断链**：可选——保持现状（archived 是历史记录）或批量改 `docs/plans/...` → `docs/archived/plans/...`

### ALIGNED 项（17 项，详见 A1 表格）

postmortem-template 17 个新增机制 × 13 个协议位置引用全部正确。

---

## 闭环建议

1. **HIGH 项必须修**：commit 前改 `hardening-roadmap.md:125`，再跑 `python3 agate/scripts/check-protocol-consistency.py` 确认 0 ERROR
2. **MEDIUM 项建议修**：commit 前改 `001-peekview-commit-hook-inactive.md:55`（小改动）
3. **LOW 项可选**：commit 后另开 issue 跟踪 `design-notes/README.md` 重复行

**建议本次 commit 只做 HIGH + MEDIUM**（共 2 个文件改动），LOW 留作 follow-up。

---

## 附录：本次变更影响范围统计

| 类别 | 数量 | 备注 |
|------|------|------|
| plans 移到 archived/ | 7（git diff） + 2（pre-archived in this cleanup） = 9 | 与用户描述一致 |
| reviews 移到 archived/ | 25（git diff） | 用户说 19，实际 25（多 6 个：review-20260701-0730-before-self-gate / 2003 / 2012 / 2054 / t045-lessons + 4 progress.md 也算入 reviews 目录） |
| issues 移到 archived/ | 1 | 与用户描述一致 |
| progress.md 删除 | 4 | 与用户描述一致 |
| README 状态更新 | 2（issues/README.md + design-notes/README.md） | 与用户描述一致 |
| 死链修复 | 2 | 与用户描述一致 |
| postmortem-template 重写 | 1（22 个机制检查项 = 5 原 + 17 新） | 用户说"新增 18 个"，实际 17 个——轻微描述误差 |
| 新建未归档 | 1（agate-evidence-capability-diagnosis-2026-07-02.md） | 用户未提及——这是一个"待评审"的新 plan，状态"待评审"，归档时机未到 |

**注**：用户描述的"25 reviews" 实际是"25 移入 archived/"——含 21 个评审文件和 4 个 progress.md，留痕文件按 SELF-GATE.md 规定属"可删"类。

---

## 审查人

protocol-alignment-review（self-gate）
