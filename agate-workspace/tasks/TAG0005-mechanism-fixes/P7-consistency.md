---
phase: P7
task_id: TAG0005-mechanism-fixes
type: consistency
parent: P2-design.md
trace_id: TAG0005-mechanism-fixes-P7-20260813
status: approved
created: 2026-08-13
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 1
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---

# P7 一致性审查 — agate 机制修复批（TAG0005）

> 审查范围：P1-P6 产出跨文件一致性 + SELF-GATE（协议本体改动）一致性。
> 结论：**无 [BLOCKER] / [DEVIATION-CRITICAL]**；DESIGN_GAP 配对项为空（P4 无声明）；发现 1 项非关键 [DEVIATION]（P3 测试映射表/GPC 测试名 BDD 编号标注错位），不阻塞验收。

## 1. DESIGN_GAP 配对

- `[DESIGN_GAP_REVIEWED: P4 无 DESIGN_GAP 声明，配对项为空]`——P4-implementation.md §DESIGN_GAP 节（L81-86）明确「无 [DESIGN_GAP]（P2 设计对 6 处修复均无歧义，实现按设计逐条落地）」。经与 P2-design.md §1 设计总览逐项对照，6 处修复（RM-AG0010/AG0011/AG0012①/AG0012②/AG0003/同类扫描守卫）全部按 P2 方案落地，未发现 P2 未覆盖的实现偏差，确认 P4 声明真实，不编造配对项。

## 2. SCOPE+ 闭环

- P1-requirements.md 无 SCOPE+ 增补，无需闭环。P1 全文无 [SCOPE+] 标记；P2-design.md §8 范围确认（L326-328）声明「本设计未发现需超出 P1 锁定范围的新增改动（无 [SCOPE+] 条目）」；P4-implementation.md §DESIGN_GAP 节同步「无 [SCOPE+]」「无 [SCOPE_GAP]」。三级声明一致，无 SCOPE+ 残留。

## 3. 跨文件一致性（引用具体锚点）

### 3.1 P1 BDD ↔ P6 验收结果（数量 + 编号逐条对齐）

- P1-requirements.md §3（L62-156）共 16 条 BDD（BDD-1..16），P6-acceptance.md §BDD 逐条验收结果（L29-44）共 16 条 PASS，数量 16=16 匹配。
- BDD 编号逐条核对（grep 提取编号排序比对一致）：BDD-1→C8 表补 backend P2 评审、BDD-2→gate 不改、BDD-3→P5 主/辅计数、BDD-4→WARNING 文案、BDD-5→仅 P5 不 WARNING、BDD-6→read-p5 执行枚举、BDD-7→execution 不含 Review 指令、BDD-8→review 含完整语义、BDD-9→单文件守卫、BDD-10→exit 2、BDD-11→回归测试、BDD-12/13/14→自动重试/<1min 告警/上限语义、BDD-15/16→同类扫描守卫/check-debt exit 2。P6 每条 PASS 均引用 P6-evidence/ 证据文件，无编号跳位或错配。
- P6-acceptance.md L56「Summary: 16/16 PASS, 0 FAIL」与 P1 16 条 BDD 一一对应。

### 3.2 P2 packages ↔ P4 实际改动文件归属

- P2-design.md frontmatter `packages: [agate-scripts-sh, agate-scripts-py, agate-docs, agate-tests]`（L12）。
- P4 实现 commit（9aacf81）实际改动 **12 个 agate 文件**，全部归属上述 4 个 packages，无越界：
  - **agate-scripts-sh**：`agate/scripts/check-gate.sh`（P5 WARNING 主/辅文案）、`agate/scripts/agate-render-dispatch-prompt.sh`（Review 指令条件注入）、`agate/scripts/check-debt.sh`（依赖失败 exit 2）
  - **agate-scripts-py**：`agate/scripts/agate-gate-p5-count.py`（主/辅双值输出）
  - **agate-docs**：`agate/role-system.md`、`agate/rules/review-mapping.md`、`agate/phase-cards/P2-design.md`（三处 C8 表）、`agate/dispatch-protocol.md`（空返回策略增量）、`agate/assets/templates/dispatch-prompt.md`（Review 指令拆独立块）、`agate/scripts/README.md`（check-debt 描述同步）
  - **agate-tests**：`agate/tests/README.md`（计数表同步）、`agate/tests/unit/agate-debt-check.bats`（头注释同步）+ P3 阶段改动的 `agate-gate-p5-count.bats`、`agate-render-dispatch-prompt.bats`、`check-gate.bats`
- 说明：dispatch-context objective_info 记「P4: 11 文件改动」，实测 P4 commit 为 12 个 agate 文件——差额 1 为 `agate/tests/unit/agate-debt-check.bats` 的头注释同步（仅 2 行注释更新，属 P4 §同步更新范畴，非实现文件）。归属判断不受影响，全部在 4 个 packages 内。
- P1 §6 范围声明（L187-190）对 4 个 packages 的改动描述与 P4 实际一致；P2 §1「明确不改」清单（check-gate.sh P2 分支 / agate-read-p5-commands.py / check-debt.sh FILE 模式与有意跳过分支 / count-tests.sh L22 / agate-capture-env-baseline.sh）经 git diff 核验全部未改。

### 3.3 P4 实现路径 ↔ P2 §2.1-2.6 方案吻合（6 处修复逐项对照）

| P2 方案节 | P4 实现（文件 + 改动） | 核对 |
|-----------|------------------------|------|
| §2.1 RM-AG0010 C8 表补 backend P2 评审 | 三处 C8 表 backend 行补 plan-eng-review（P2）+ 保留 review（P4 后）+ 去重说明；check-gate.sh P2 分支未动 | 一致 |
| §2.2 RM-AG0011 主/辅计数 | count.py 输出单行双值 `{main} {aux}`，main 精确 `^  P5:`、aux 排除 `_formatter`；check-gate.sh P5 分支读双值、`P5_TOTAL>1` 触发主/辅文案 WARNING | 一致 |
| §2.3 RM-AG0012① 条件注入 | dispatch-prompt.md 主代码块移除 Review 节 → 「## 阶段特定提示」下新增 `### Review 角色特别指令` 独立块；render 按 ROLE_DIR=review-roles 追加 review_appendix（main_block → review_appendix → appendix）；dispatch-protocol.md 内联模板加语义备注（无 Review 指令字面量） | 一致 |
| §2.4 RM-AG0012② 回归测试 | 无脚本改动（v0.23.0 已修）；RP.17 新增锁定 exit 2 + stderr | 一致 |
| §2.5 RM-AG0003 自动重试 | dispatch-protocol.md 第 1 次空返回改写 a-e 步骤；自动重试不占 retries 槽位；<1min →「会话时长异常短」告警；禁止段后补唯一豁免说明；MAX_RETRY/PAUSED 未动 | 一致 |
| §2.6 check-debt.sh 依赖失败 | L26/L28 exit 0→2 + 消息改「回退覆盖比对无法执行」；头注释同步；有意跳过分支保留 | 一致 |

### 3.4 P2 gate_commands ↔ P5 执行结果（1 主 2 辅全绿）

- P2-design.md §3 gate_commands（L246-252）声明 P5（主）+ P5_consistency + P5_shellcheck（2 辅），恰 1 主 2 辅。
- P5-test-results/unit.md §结论（L14-22）三条命令全部 exit 0：bats 全量 726 ok / consistency 0 ERROR / shellcheck 0 error，与 P2 §3 命令字面一致（`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`、`python3 agate/scripts/check-protocol-consistency.py --strict`、`shellcheck -S warning agate/scripts/*.sh`）。
- P5-test-results/unit.md §附加客观查证 L71-73：worktree check-gate.sh P5 实际输出「1 个主命令 + 2 个辅助命令（共 3 条）」，与 P2 §3 注释声明的 1 主 2 辅一致，in-situ 验证 BDD-3/4 落地。

## 4. 未决项清零

- P1-requirements.md L17/L160 `[NO_NEED_CONFIRM]` 标记；§4 待确认清单（L158-166）「无未决待确认项」，方向决策均拍板。无残留行首 [NEED_CONFIRM]。
- P6-acceptance.md 无 [BLOCKER] / [DEVIATION-CRITICAL] 标记（16/16 PASS, 0 FAIL）；P5-test-results 无预存失败（fail-list.txt 为空）。

## 5. SELF-GATE 一致性（协议本体改动）

本任务是 agate 协议本体修复，额外核验协议文档改动与 P2 设计的一致性：

- **三处 C8 表同步**：role-system.md、rules/review-mapping.md、phase-cards/P2-design.md 的 backend 行均补 plan-eng-review（P2 方案评审）且保留 review（P4 后），三表均附去重说明（P6-evidence/bdd-1-c8-rows.log 复核，三表 backend 行文本逐条核对一致）。与 P2 §2.1 候选方案 A 的 L50-52 行文本完全吻合。
- **dispatch-prompt.md 模板**：Review 指令从主代码块移至「## 阶段特定提示」下独立子块，指令文本原样保留（含 approved/rejected/needs-revision 完整语义）；全仓 `grep -rl 'Review 角色特别指令' agate/` 仅命中该模板单文件（BDD-9 守卫，实跑确认）。与 P2 §2.3 方案 A 一致。
- **dispatch-protocol.md**：内联模板加评审角色 status 语义备注（无 Review 指令字面量，避免 BDD-9 守卫被破坏）；空返回恢复策略 a-e 增量 + 唯一豁免说明。与 P2 §2.5 一致。
- **check-gate.sh 文案**：P5 WARNING 改为「X 个主命令 + Y 个辅助命令（共 Z 条）」，与 P2 §2.2 消费逻辑一致；P2 分支（L157-164）无条件 P2-review.md 要求原样保留（git diff 0 命中），BDD-2 硬约束满足。

## 6. 发现的偏差

- `[DEVIATION]`（已修复）：P3-test-cases.md §测试映射总表（L21-23）将 GPC.1/2/3 标注为 BDD-1/2/3，且 agate-gate-p5-count.bats 中 GPC.1/2/3 测试名分别标注「BDD-1」「BDD-2」「BDD-3」——但按 P1-requirements.md 全局编号，BDD-1/2 属于 RM-AG0010（C8 表补评审/gate 不改），GPC.* 对应的是 RM-AG0011 的 P5 计数（应为 BDD-3/4/5 区间）。同一测试在 P1/P6 用全局编号（P6 BDD-3 = P5 计数），在 P3 映射表与 GPC 测试名中编号偏移 2。
  - **处理**：已在本阶段修复——GPC 测试名对齐全局编号（GPC.1/3 → BDD-3，GPC.2 → BDD-5 边界），P3-test-cases.md 映射表同步修正。原判断「纯标注错位不影响功能正确性」成立（测试断言本身正确，P6 BDD-3/4/5 验收 PASS），修正后编号统一无残留。

## 7. 结论

- BLOCKER=0，DEVIATION-CRITICAL=0，DESIGN_GAP 未配对=0（P4 无声明），SCOPE+ 无残留。
- 跨文件一致性全部通过（引用锚点见 §3-5）；1 项标注类偏差（§6）已在本阶段修复（GPC 测试名 + P3 映射表 BDD 编号对齐全局编号）。
- `[PROD_NOT_TOUCHED]`——全程仅在 worktree 内读产出文件与 git diff 核验，未接触生产环境。
