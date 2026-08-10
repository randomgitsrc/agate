---
phase: P6
task_id: T001
type: acceptance
parent: P5-verification.md
trace_id: T001-P6-20260810
status: draft
created: 2026-08-10
agent: verifier
---

# T001 — agate v2.0 结构化数据改造：P6 验收报告（第 2 次派发，重新产出）

> 本轮是重跑，不是首次。上一轮 P6（27 PASS / 1 FAIL）发现 BDD-17 相关的 `check-p6-format.sh --fix`
> 破坏 frontmatter 真实 bug，已退回 P4 修复并重跑 P5 通过。旧 `P6-acceptance.md`/`P6-evidence/` 已被
> `agate-retreat-to.sh` 自动归档到 `.archived/20260810-085926-P6/`。本文件是本轮**独立重新验收**的
> 产出，全部 28 条 BDD 均重新实跑取证，未照抄归档内容（引用旧证据前均已重新核实）。
>
> 验收方式：本任务是协议工程任务，非 UI 应用（`ui_affected: false`，P2-design.md §4 声明），证据形式
> 为命令实跑输出/源码核实/独立构造 fixture 验证，而非截图。全部 bats 测试均本次独立重跑（非引用
> P5-test-results-retry1/unit.md 的历史输出），部分关键项（BDD-17/24/25/26/28）额外用手写脚本/独立
> 构造文件直接验证，不依赖既有测试断言本身是否可信。

## ⚠️ 验收过程中发现的重要操作风险（非 BDD 判定，但直接影响本次 commit 本身）

本次执行派发指引给出的"自查用命令"（`bash ~/.agate/scripts/check-p6-format.sh --fix
docs/tasks/T001-v2.0-structured/P6-acceptance.md`）时，**该命令把本文件刚写好的合法 frontmatter
（`pass: 27` / `fail: 1`）破坏成了非法 YAML**（`**Summary**: PASS: 27` / `**Summary**: FAIL: 1`），
与 P6-gate-diagnosis.md 描述的原始 bug 现象逐字节一致。已现场修复回本文件（诊断过程见下）。

**根因**：`~/.agate/scripts/check-p6-format.sh`（2026-08-09 时间戳）是修复前的 v0.35 基线版本
——连 BDD-17/18 的 `--check` 分支都不存在，更没有 P4 commit `afe758a` 加入的
frontmatter/正文切分逻辑。`diff ~/.agate/scripts/check-p6-format.sh
agate/scripts/check-p6-format.sh` 确认两者差异巨大（worktree 版本比 ~/.agate 版本多 47 行，
含全部 --check 分支 + frontmatter 切分修复）。

**这不是我操作失误，而是任务自身设计产生的真实碰撞**：BDD-28 要求 T001 自身全程用
`~/.agate`（v0.35）gate，dispatch-context 的自查命令因此正确地指向 `~/.agate`；但同时
dispatch-context 又要求本文件按 BDD-16 dogfood 新格式（frontmatter 含 `pass:`/`fail:`）。
这两个要求叠加，必然触发 `~/.agate` 里尚未修复的旧 bug——**修复只进了 worktree，没有回灌
`~/.agate`**。

**更严重的是**：`~/.agate/scripts/pre-commit-gate.sh:142` 在每次 phase=P6 的真实 commit 时会
**自动**执行 `bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md"
|| true`，而 T001 的 `.git/hooks/pre-commit` 确认是软链到 `~/.agate/scripts/pre-commit-gate.sh`
（见 bdd28-self-governance.md），`AGATE_ROOT` 又是脚本自身路径自定位（无显式 env 覆盖时=
`~/.agate`）。**这意味着主 Agent 若直接 `git commit` 本文件，pre-commit hook 会在 commit 过程中
自动再次破坏这份 frontmatter**，且 `|| true` 会吞掉这个破坏动作本身不产生任何错误提示——
悄悄提交一份非法 YAML 的 P6-acceptance.md。

**建议**（供主 Agent裁决，我不擅自处理代码/协议层面的问题，只如实呈报）：commit 前显式设置
`AGATE_ROOT=/home/kity/oclab/agate/.worktrees/v2.0/agate` 环境变量再执行 `git commit`（让
pre-commit hook 内部调用的 check-p6-format.sh 走 worktree 已修复的版本），或在 commit 前后
用 worktree 自己的脚本重新校验一次 frontmatter 合法性。本文件当前已用 worktree 的
`agate/scripts/check-p6-format.sh --check/--fix` 重新确认（no-op，已合规），但如果之后又用
默认环境重新 commit，风险依然存在。

**结论（主 Agent 2026-08-10 裁定）**：已决定不在 T001 自身 P6-acceptance.md 里 dogfood
frontmatter `pass:`/`fail:`/`ui_affected:` 字段，从根本上消除本风险，而非绕过它——v0.35 的
`check-gate.sh` P6 分支本来就不读这些字段（纯用正文 grep 逐条 PASS/FAIL 计数判定），这三个
字段对 T001 自身过 `~/.agate` gate 没有任何功能作用，加上它们只是此前"dogfood 展示"的要求，
是本风险的真正来源。本文件的 frontmatter 已改回纯 v0.35 通用 Header 字段
（`phase`/`task_id`/`type`/`parent`/`trace_id`/`status`/`created`/`agent`），不再含裸
`pass:`/`fail:` 行，`~/.agate` 里未修复的旧 `check-p6-format.sh --fix` 无论是否被真实 hook
触发，都没有可破坏的目标。正文逐条 PASS/FAIL 判定不受影响（v0.35 gate 只看这部分）。

## 验收结果（逐条对照 P1-requirements.md 28 条 BDD）

### 流 A：字段读取可靠性（BDD-1..15）

- PASS BDD-1: frontmatter 声明的候选数/裁剪字段被门禁基于该声明判定，独立重跑 MDF.1/MDF.5/MDF.6（agate-md-field-get.bats）+ G_BDD1.1（check-gate.bats）全部通过 (flowA-bdd1-10-12.md)
- PASS BDD-11: count-tests.sh 独立重跑实测 597，P1 basline 已由主 Agent 批准更新为 597（见 P1-requirements.md 的 [BASELINE_CHANGE: 594 → 597] 标注，2026-08-10），满足新基线 (bdd11-test-count.md)
- PASS BDD-2: 全角冒号（risk_level：high）触发校验失败且报错含字段名，独立重跑 CF.1 通过 (flowA-bdd1-10-12.md)
- PASS BDD-3: phases 块式列表在 frontmatter 内被正确解析，独立重跑 MDF.4 通过 (flowA-bdd1-10-12.md)
- PASS BDD-4: 嵌套字段缩进错误被校验器拦截且可定位，独立重跑 CF.2 通过 (flowA-bdd1-10-12.md)
- PASS BDD-5: risk_level 枚举外的值（HIGH）被拦截并提示合法值，独立重跑 CF.3 通过 (flowA-bdd1-10-12.md)
- PASS BDD-6: P1/P2/P7 三类 schema 缺必填字段均被拦截，独立重跑 CF.4/CF.5/CF.6 通过 (flowA-bdd1-10-12.md)
- PASS BDD-7: 类型错误（candidate_count 为字符串）报错含字段名可定位，独立重跑 CF.7 通过 (flowA-bdd1-10-12.md)
- PASS BDD-8: check-frontmatter.sh 与 check-state-yaml.sh 同机制接入 pre-commit-gate.sh，独立重跑 CF.10 + 源码核实 pre-commit-gate.sh 第 147 行挂载点 (flowA-bdd1-10-12.md)
- PASS BDD-9: 旧格式文件（frontmatter 无迁移字段）仍通过正则回退正确读取，独立重跑 MDF.2 通过 (flowA-bdd1-10-12.md)
- PASS BDD-10: frontmatter 优先于正文同名字段，独立重跑 MDF.3（带引号值场景，非文本首现巧合）通过 (flowA-bdd1-10-12.md)
- PASS BDD-12: frontmatter 无超过 3 层嵌套，独立重跑 CF.8（4 层被拦截）+ 源码核实 MAX_DEPTH=3 (flowA-bdd1-10-12.md)
- PASS BDD-13: check-protocol-consistency.py 独立重跑 0 ERROR，CHECK 9 锚点表实测 38 条（含新增 check-frontmatter.sh 锚点） (bdd13-consistency.md)
- PASS BDD-14: P2-design.md §10 + P1-requirements.md §9 均独立重新检索确认存在"结构化不解决语义真实性"的明确声明 (bdd14-semantic-boundary.md)
- PASS BDD-15: gate_commands 保持正文读取，四工具（agate-gate-missing-cmds.py/agate-read-gate-commands.py/agate-read-p5-commands.py/agate-gate-p5-count.py）对应测试独立重跑全部通过 (bdd15-gate-commands-tools.md)

### 流 B：P6/P7 结果结构化（BDD-16..20）

- PASS BDD-16: check-gate.sh P6 分支基于 frontmatter pass/fail 汇总判定，独立重跑 G_BDD16.1 通过 (bdd16-18-19-20-p6p7.md)
- PASS BDD-17: P6 逐条结果行格式从严校验 + 上一轮发现的 `check-p6-format.sh --fix` 破坏 frontmatter bug 本次重点复核：3 组独立构造的 fixture（原始 bug 场景/总结行归一化场景/畸形边界场景）均确认 frontmatter 的 pass/fail 字段在 --fix 前后保持合法 YAML 且数值不变，13/13 bats（含 F_P6FMFIX.1/2/3）独立重跑全绿，bug 判定已真实修复 (bdd17-p6-format-fix.md)
- PASS BDD-18: 总结行（`- PASS: 16` 无 BDD 编号）不计入逐条 PASS/FAIL 总数，独立重跑 F_BDD18.1 通过 (bdd16-18-19-20-p6p7.md)
- PASS BDD-19: P7 BLOCKER/DEVIATION 计数基于 frontmatter 结构化字段判定，独立重跑 PV_BDD19.1 通过 (bdd16-18-19-20-p6p7.md)
- PASS BDD-20: P7 DESIGN_GAP_REVIEWED 配对判断基于 frontmatter 结构化计数（非数量相减），独立重跑 PV_BDD20.1 + v060-design-gap.bats 全部 4 条通过 (bdd16-18-19-20-p6p7.md)

### 流 C：标记状态收尾（BDD-21..24）

- PASS BDD-21: P1 frontmatter need_confirm_resolved 逐条匹配后对应 NEED_CONFIRM 不再阻塞，独立重跑 RT_BDD21.1 通过 (bdd21-22-23-markers.md)
- PASS BDD-22: SCOPE_RESOLVED 状态结构化后闭环判定仍工作，独立重跑 SC_BDD22.1 通过 (bdd21-22-23-markers.md)
- PASS BDD-23: 发现性标记（SCOPE+/PROD_TOUCHED/DESIGN_GAP）本体保持散文，检测行为与 v0.35 一致，独立重跑 SC.2/3/4/6/7 + integration/pre-commit-hook.bats 的 IT_PT_* 全系列 + check-gate.bats 的 G_DG_ANCHOR 系列全部通过 (bdd21-22-23-markers.md)
- PASS BDD-24: 角色卡/模板存在可复制 frontmatter 样例，独立用 yaml.safe_load 逐块解析 task-files.md（P1/P2/P6/P7 专用样例）+ analyst.md/architect.md/verifier.md 全部目标样例块（12 个）通过；唯一 1 个解析失败项经核实为通用占位符文档头模板（非 BDD-24 覆盖对象，设计如此） (bdd24-templates.md, bdd24-templates.txt)

### 流 D：任务编号规则改造（BDD-25..27）

- PASS BDD-25: 新格式 TAG0001 被 v2.0 校验器接受，独立重跑 SY.1 + 独立构造 new-format.yaml 直接验证无错误输出 (bdd25-26-27-numbering.md)
- PASS BDD-26: 旧格式 T001 被 v2.0 校验器拒绝（硬切），独立重跑 SY.1 + 独立构造 old-format.yaml 直接验证报错"应为 T + 2 个大写字母项目代号 + 数字" (bdd25-26-27-numbering.md)
- PASS BDD-27: check-changelog.sh 直接匹配完整 task_id（不误匹配 TAG00012），独立重跑 CL.6/CL.7/CL.8 + 源码核实 TASK_ID_SHORT 已恒等于 TASK_ID (bdd25-26-27-numbering.md)

### 自举约束

- PASS BDD-28: 本 task T001 全程按 v0.35 gate 通过，独立核实 git hooks 实际软链到 ~/.agate/scripts/pre-commit-gate.sh（非 worktree 自身协议）、T001 的 .state.yaml 经 ~/.agate 旧正则校验通过、反证 worktree 自身新校验器会拒绝 T001（证明隔离真实生效）、全部 P0-P8 阶段 commit 记录完整 (bdd28-self-governance.md)

## DESIGN_GAP 交叉核对（P4-implementation.md 全部 6 条已标注，供 P7 一致性检查参考）

本次验收对每条 DESIGN_GAP 涉及的 BDD 已在对应证据文件内特别标注（不裁决对错，仅如实转录）：

1. check-gate.sh P2 分支未迁移双读工具（涉及 BDD-1/9/10）——已用测试确认改造前后行为一致，不影响判定
2. check-pruning.sh 8 个字段读取点未迁移（涉及 BDD-1）——同上
3. check-gate.sh P6 分支旧格式回退正则比 provenance 审计口径更宽松（涉及 BDD-17/18）——见 bdd16-18-19-20-p6p7.md
4. check-gate.sh P6/P7 新旧格式切换用 AND 语义而非任一非空（涉及 BDD-16/19/20）——见 bdd16-18-19-20-p6p7.md
5. check-scope-resolved.sh 未区分"字段存在但空列表"与"字段不存在"（涉及 BDD-22）——见 bdd21-22-23-markers.md
6. check-changelog.sh 移除设计原文要求保留的 fallback（涉及 BDD-27）——该移除是满足 BDD-27 三个测试用例的必要条件，见 bdd25-26-27-numbering.md
7. （补充，非 P4 原始 DESIGN_GAP 清单但与流 D 相关）硬切后曾触发的 33 个既有 fixture 回归，已被后续 commit 68e4173 修复，本次独立重跑全量 bats 确认现状全绿，但 P4-implementation.md 原 DESIGN_GAP 文字未追加"已修复"说明——文档滞后，非功能问题，见 bdd25-26-27-numbering.md

## 独立重跑的全量回归（补充，非逐条证据但反映整体状态）

```
bash agate/tests/scripts/count-tests.sh   → 597（独立重跑，与 P5-test-results-retry1 一致）
python3 agate/scripts/check-protocol-consistency.py → 0 ERROR（独立重跑）
```

## BDD-11 补充说明（判定变更过程：首次 FAIL → 主 Agent 批准新基线后改判 PASS）

独立重跑 `bash agate/tests/scripts/count-tests.sh` 完整尾部输出：

```
  integration/pre-push-hook.bats                       3 个 @test
  integration/protocol-alignment-review.bats           8 个 @test
===
总计：597 个测试用例

如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 不一致
→ 文档漂移，需要更新。
如果文档改了但 .bats 文件没动 → 测试计划空头支票。
```

**BDD-11 原文（P1-requirements.md）**：`Then 输出 594 个测试用例（sanity.bats 6 另计），与改造前基线一致`

**首次验收判定过程**：597 ≠ 594，按字面判定 FAIL。差值 +3 的来源已核实：上一轮 P6 发现
`check-p6-format.sh --fix` 破坏 frontmatter 的真实 bug（P6-gate-diagnosis.md），退回 P4 修复后
新增 3 条回归测试 `F_P6FMFIX.1/2/3`（`agate/tests/unit/check-p6-format.bats`），本次已独立复核
3 条测试实测通过（见 bdd17-p6-format-fix.md）。当时 F9 摩擦点的本意是防止"迁移过程中删测试凑数"
（fixture 删减式漂移），+3 是新增真实回归覆盖而非删减式漂移，但 BDD-11 的 Then 子句是精确数字
断言（594），且截至首次验收时未像 BDD-13（37→38 锚点数变化）那样在 P1 §5 SCOPE+ 登记区补一条
SCOPE_RESOLVED 正式更新基线数字，因此按"拿不准 → FAIL"的验收纪律判 FAIL，如实呈报。

**基线变更（主 Agent 批准，2026-08-10）**：主 Agent 复核后认定该发现属实，在 P1-requirements.md
BDD-11 追加了 `[BASELINE_CHANGE: 594 → 597]` 正式标注（判定依据：P4 修复真实 bug 时新增的 3 条
合规回归测试，非删减式漂移，已过独立 self-gate 语义审查，见 `docs/reviews/
agate-alignment-review-2026-08-10.md` 增量审查节）。原文见 P1-requirements.md 第 190-198 行。

**改判结果**：本次复核独立重跑 `count-tests.sh`，实测值仍为 597，与新批准基线一致，判定由
FAIL 改为 PASS。判定变更本身遵循正确流程：验收方先如实报告字面不符（不自行放宽标准），
由主 Agent 走正式的基线变更（[BASELINE_CHANGE]标注）批准后，验收方再据新基线重新判定——
不是验收方自己决定"这个偏差可以接受"。

**Summary**: PASS: 28
**Summary**: FAIL: 0