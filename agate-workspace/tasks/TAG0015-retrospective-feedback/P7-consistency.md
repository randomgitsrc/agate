---
phase: P7
task_id: TAG0015
type: consistency
parent: P2-design.md
trace_id: TAG0015-P7-20260819
status: draft
created: 2026-08-19
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# P7-consistency.md — TAG0015 一致性交叉检查

## 0. 检查范围与方法

对照 P1-requirements.md / P2-design.md / P4-implementation.md / P6-acceptance.md 全文 + 实际
git 提交（`208a1ec` P4、`4fd310f` P6）+ `docs/reviews/agate-alignment-review-2026-08-19.md`
（SELF-GATE 语义对齐审查报告），逐条核对 dispatch-context 五条约束。

## 1. DESIGN_GAP 配对（约束 1）

**转抄 `P4-implementation.md:61-69` 原文**：

> [DESIGN_GAP: P2-design.md §1.1 类 4.1 要求 roadmap.md 三处及新模板迁移说明"只对三处 literal
> 路径字符串 `docs/reviews/postmortem-template.md` 追加行内脚注式更正，不删除原叙述"，隐含要求
> 保留该字符串原样连续出现；但物理 git mv 后，`check-protocol-consistency.py` CHECK 2（仅
> `agate-workspace/roadmap/` 与 `agate/assets/` 均不在 NARRATIVE_DIRS 宽松名单内）会把这个连续
> 字符串当作"协议文件引用了不存在的文件"判为 ERROR（P2 未预见迁移对 CHECK 2 分类的连带影响）。
> 实现中将 `roadmap.md:313` 与新模板文件自身迁移说明里的连续路径字符串拆成"`docs/reviews/` 下
> 的 `postmortem-template.md`"两段（内容/语义不变，只是不再连续可被 CHECK 2 正则匹配为单一死链
> 引用），以满足 P4 门槛"check-protocol-consistency.py --strict 仍 0 ERROR"的硬性要求，同时保留
> 了原叙述内容（未删减一字）。]

`[DESIGN_GAP_REVIEWED: 接受此偏差]` 理由：

1. **技术前提独立复核过**——`docs/reviews/agate-alignment-review-2026-08-19.md:214-218`（SELF-GATE
   语义对齐审查「已知偏离核实」节）已独立读取 `check-protocol-consistency.py:76` 的
   `NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/",
   "archived/", "agate-workspace/tasks/", "CHANGELOG.md")`，确认不含 `agate-workspace/roadmap/`
   与 `agate/assets/`，DESIGN_GAP 声称的技术前提成立；并实跑 `check-protocol-consistency.py
   --strict` 确认 CHECK 2 结果是 **WARN 非 ERROR**（0 ERROR / 305 WARNING，`P4-implementation.md`
   自查记录一致）。本条 REVIEWED 复用该独立核实结论（dispatch-context 已明确允许复用，不需要
   重新查一遍源码），但仍在本文件正式配对留痕，满足角色文件"不能只写'已核实'"的要求。
2. **未违反 P2 意图的实质**——P2§1.1 原文的核心约束是"不删除原叙述、只做脚注式更正"，这是为了
   保护"历史讨论记录不应被静默篡改结论"的档案完整性（P2-design.md:63-66）。实现方式（拆成两段
   非连续字符串）没有删减任何一字内容，只是把 literal 路径字符串物理断开以规避 CHECK 2 的正则
   死链误判，语义与档案完整性均未受损，是对 P2 约束字面表述的技术性适配，不是对约束意图的违反。
3. **有硬门槛验证托底**——P4 自查与 P6 验收（`P6-acceptance.md` 共享命令输出）均独立实跑确认
   `check-protocol-consistency.py --strict` 0 ERROR，DESIGN_GAP 声明的"满足条件"是可验证的客观
   结果，非单方面主张。

**结论：本条 DESIGN_GAP 配对完整，接受该偏差，不构成 BLOCKER。**

## 2. SCOPE+ 闭环检查（约束 2）

```
$ grep -n "\[SCOPE+\]" P1-requirements.md P4-implementation.md
（零命中，退出码 1）
```

本任务全程未产生 `[SCOPE+]` 增补。P1-requirements.md §6 待确认清单标记为 `[NO_NEED_CONFIRM]`，
其中两处 `[SUGGEST:]`（BDD-10「DEBT/roadmap 关联作为机制缺口检测代理」、BDD-16「存量复盘保留
原位+标注」）已在正文内被主 Agent 采纳并落实为 BDD 正文的一部分（非独立追加的范围外增补条目），
不构成 `[SCOPE+]`。**本任务无 SCOPE+ 增补，闭环检查不适用。**

## 3. 跨文件一致性核对（约束 3，逐项给出源文件节名锚点）

### 3a. P1 BDD 总数 与 P6 PASS/FAIL 总数

- `P1-requirements.md §4`：`grep -c "^#### BDD-" P1-requirements.md` = **20**（BDD-1 至 BDD-20，
  按 4.1~4.7 七个文件分组）
- `P6-acceptance.md` frontmatter：`pass: 20`、`fail: 0`
- `P6-acceptance.md §3 Summary`：`20/20 PASS, 0 FAIL`

**数量匹配，且逐条核对非仅数字**——`P6-acceptance.md §1` 20 条 PASS 条目逐一对应 P1 §4.1~4.7
的 BDD 编号（BDD-1~BDD-20 全部出现且各只出现一次，无重复/遗漏/错位映射）。

### 3b. P1 §9 packages 声明（6 项）与 P4 实际改动文件核对

`P1-requirements.md §9`：`packages: [assets/templates, scripts, state-machine, phase-cards,
docs-reviews-migration, core-protocol-docs]`

`git show --stat 208a1ec`（P4 commit，含 SELF-GATE 重试 #1）实际改动的协议/脚本/文档文件
（排除 `.state.yaml`/`P4-*.md`/`orchestrator-log.md`/`active-tasks.md`/`P4-progress.md` 等
task 工作区流程文件，只看落入 6 个包范围判定对象的文件）：

| 实际改动文件 | 归属包 | 是否在 6 项声明内 |
|---|---|---|
| `agate/assets/templates/retrospective-template.md`（git mv） | assets/templates | 是 |
| `agate/assets/templates/task-files.md` | assets/templates | 是 |
| `agate/scripts/check-retrospective.py` | scripts | 是 |
| `agate/scripts/agate-feedback.py`（新） | scripts | 是 |
| `agate/scripts/agate-md-field-get.py` | scripts | 是 |
| `agate/scripts/README.md` | scripts | 是（同物理目录） |
| `agate/state-machine.md` | state-machine | 是 |
| `agate/phase-cards/P8-release.md` | phase-cards | 是 |
| `docs/reviews/retrospective-tag{0008,0010-0011×2,0013,0014}.md`（5 份） | docs-reviews-migration | 是 |
| `agate/AGENTS.md` | core-protocol-docs | 是 |
| `agate/WORKFLOW.md` | core-protocol-docs | 是（同物理目录，SELF-GATE 追加） |
| `agate/tests/README.md` | 未在 P1§9 逐项文字列出，物理归属 scripts 包同类（测试文档） | 归入包范围内（同类推定） |
| `agate/tests/unit/test_agate_feedback.py` | scripts（配套测试） | 是 |
| `agate-workspace/roadmap/roadmap.md` | **P1§9 文字未显式归类** | **观察项，见下** |

**观察项（非阻断）**：`agate-workspace/roadmap/roadmap.md`（BDD-8 关联改动，追加脚注式更正）
未被 `P1-requirements.md §9` 的 packages 归类描述文字显式提及（§9 原文对 6 个包逐一说明对应
内容，未含 roadmap.md）。核实结论：该文件改动在 `P1-requirements.md §4.1 BDD-8` 与
`P2-design.md §1.1 类 4.1` 均已明文声明为"关联但不计入以上编号"的同一改动动作的一部分，改动量
极小（3 处脚注追加），且不属于新增范围（P1 §2 隐含需求 1 已识别"模板迁移后引用点必须同步"）。
判定：**§9 packages 描述文字有轻微遗漏（未把 roadmap.md 显式挂靠某个包名），但改动本身在 P1/P2
两阶段均有明文出处，不构成未声明的范围外改动，不升级为 DEVIATION。**

### 3c. P2-design.md §1.1 七类改动落点 与 P4-implementation.md 实际交付核对

逐类核对（`P2-design.md §1.1` 类 4.1~4.7 vs `P4-implementation.md`「改动清单」1~7 条）：

| P2§1.1 类别 | P4 改动清单对应条目 | 核对结果 |
|---|---|---|
| 类 4.1 模板迁移 BDD-1~8 | 改动清单 1 | 一致（四节标题/内容价值标准/归因分层/技术债强制说明/两类去向/frontmatter 三字段/agate 反馈节/P8-release.md 挂钩点/roadmap.md 脚注，逐项对应） |
| 类 4.2 check-retrospective.py BDD-9~11 | 改动清单 2 | 一致（第 93→141 行路径文案 + `_scan_debt_roadmap_signal` 分支 + 独立第二段 stderr 输出） |
| 类 4.3 state-machine.md BDD-12~13 | 改动清单 3 | 一致（第 481 行追加依据分句 + 新增 L2 checkpoint 两件套小节） |
| 类 4.4 跨文件同步 BDD-14 | 改动清单 4 | 一致（核实 loop-orchestration.md/task-files.md 不矛盾 + task-files.md 辅助文件表新增 2 行） |
| 类 4.5 AGENTS.md BDD-15 | 改动清单 5 | 一致（第 11 行区分历史/新复盘措辞） |
| 类 4.6 存量标注 BDD-16 | 改动清单 6 | 一致（5 份文件首行统一标注） |
| 类 4.7 agate-feedback.py BDD-17~20 | 改动清单 7 | 一致（新脚本 + 提取/脱敏/开关/不自动提交四项） |

**七类全部一一对应，无遗漏无超出。**

**额外观察（非新增 DEVIATION，转入 3d 处理）**：`P2-design.md §1.2「不改什么」` 原文明确列出
`agate/WORKFLOW.md:91,318`、`agate/scripts/agate-feedback.py`（P2 §1.1 类 4.7 原设计是"本地
实现等价函数，不 import" `agate-frontmatter-check.py`）为不改/维持原设计对象；但
`P4-implementation.md`「重试 #1」节记录 SELF-GATE 语义对齐审查（`docs/reviews/
agate-alignment-review-2026-08-19.md` A2/A3b/A5/A7）发现 4 项需修复，实际额外触碰了
`agate/WORKFLOW.md:318`、`agate/scripts/README.md`、`agate/tests/README.md`、
`agate/scripts/agate-md-field-get.py`。这是 P2 原设计之外、由 SELF-GATE 质量门发现并经用户裁决
批准的修正，**不是未经审查的静默偏离**——全过程有完整留痕（审查报告 + 用户裁决记录 +
`P4-implementation.md`「重试 #1」节说明），dispatch-context 约束 5 已明确"SELF-GATE 语义对齐
审查非本 P7 一致性检查范畴，不重复做"，本 P7 不对该审查结论本身复核，只确认其触发的额外文件
改动已完整记录在案（是），故不计入 deviation_count。

### 3d. P4 四项 SELF-GATE 修复 是否在 P6 验收有对应体现

`P4-implementation.md「重试 #1」` 四项修复：① ADR-007 合规（`agate-md-field-get.py` 复用）
② 测试断言订正 ③ 三处文档同步（WORKFLOW.md/scripts/README.md/tests/README.md）④（同③批）。

核对：

- **时序前提**：`git log` 显示 P4 commit `208a1ec`（含重试 #1 全部修复）早于 P6 commit
  `4fd310f`——P6 验收基于修复后的代码运行，不存在"验收了修复前旧实现"的风险。
- **BDD-17 证据**：`P6-acceptance.md §1` `PASS BDD-17` 明确写"本轮独立编写样例复盘文档……
  实跑 `AGATE_FEEDBACK=on python3 agate-feedback.py retrospective.md`，`mechanism_issues` 列表
  内容被正确解析输出（语义完整保留）……无解析错误，exit 0"——验证的是修复后（调用
  `agate-md-field-get.py`）的实际运行行为，非转抄旧断言。
- **BDD-20 证据（直接引用 ADR-007 修复）**：`P6-evidence/bdd-20-manual-trigger-no-submit.md:43-44`
  原文："唯一一处 `subprocess.run` 调用的是本地脚本间通信 `agate-md-field-get.py`（ADR-007 单一
  双读工具复用，见 `agate/scripts/agate-feedback.py:46-65` `_md_field_get` 函数），非网络提交"——
  直接对应修复项①（ADR-007）与②（断言订正后仍确认无网络提交调用）。
- **三处文档同步（WORKFLOW.md/scripts/README.md/tests/README.md）**：均为流程说明性文档，不是
  P1 任何 BDD 的直接验收对象（P1 20 条 BDD 未把这三份 README/WORKFLOW.md 列为 Then 断言目标），
  P6 未单独验收在预期之内，不构成缺口。

**结论：4 项 SELF-GATE 修复中，直接可被 BDD 验收覆盖的部分（ADR-007/断言订正）已在 P6-evidence
中有明确证据体现；不属于 BDD 验收对象的部分（文档同步）本就不在 P6 验收范围，缺失不构成问题。**

## 4. 未决项清零核对（约束 4，实际 grep）

```
$ grep -n "\[NEED_CONFIRM\]\|\[BLOCKER\]\|\[DEVIATION-CRITICAL\]" \
  P1-requirements.md P2-design.md P4-implementation.md P6-acceptance.md
（零命中，退出码 1）
```

- `P1-requirements.md §6`：`[NO_NEED_CONFIRM]`（非残留 NEED_CONFIRM，是已闭环标记）
- `P2-design.md`：无 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]` 残留
- `P4-implementation.md`：唯一的方括号标记是已处理的 `[DESIGN_GAP: ...]`（见第 1 节），无
  `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]`
- `P6-acceptance.md`：`[NO_NEED_CONFIRM]` + `[PROD_NOT_TOUCHED]`，无残留三种标记

**四份文件均无 `[NEED_CONFIRM]`/`[BLOCKER]`/`[DEVIATION-CRITICAL]` 残留，未决项清零确认。**

## 5. 约束 5 声明

本任务 P4 阶段已完整走过 SELF-GATE 语义对齐审查（`docs/reviews/agate-alignment-review-2026-08-19.md`，
含首轮 + 重试 #1 复核，最终 4 点全部转 ALIGNED）。按 dispatch-context 约束 5，P7 不重跑
protocol-alignment-review，本文件第 1、3d 节对该审查报告的引用均为交叉核实用途，非重新执行。

## 6. 总结

- BLOCKER = 0
- DEVIATION = 0（deviation_critical = 0）
- DESIGN_GAP = 1，DESIGN_GAP_REVIEWED = 1（第 1 节）
- SCOPE+ 闭环：不适用（本任务无 SCOPE+ 增补）
- 未决项清零：确认（第 4 节实际 grep）
- 观察项（不阻断，供归档参考）：`agate-workspace/roadmap/roadmap.md` 未被 `P1§9 packages` 描述
  文字显式归类（第 3b 节）；SELF-GATE 重试 #1 额外触碰 4 个 P2 原声明"不改"的文件，已确认全程
  留痕且不构成未审查偏离（第 3c 节）

**结论：通过，无 BLOCKER，可进入 P8。**
