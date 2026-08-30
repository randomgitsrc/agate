---
review_date: 2026-08-30
reviewer: independent-design-review
change_summary: RM-AG0046 落地计划 v2（维护性反模式 gate，G0 优先，diff 驱动）设计文档独立评审——docs/design-notes/rm-ag0046-maintainability-gate-plan.md
files_changed: [docs/design-notes/rm-ag0046-maintainability-gate-plan.md]
---

# RM-AG0046 落地计划 v2 设计评审

审查对象：`docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（142 行）。
权威规则源：`agate/scripts/check-gate.py`、`agate/scripts/agate-risk-score.py`、`agate/scripts/check-p6-provenance.py`、`agate/assets/templates/known-failures-template.md`、`docs/design-notes/design-maintainability-gate.md`、`agate/adr.md`、`agate/WORKFLOW.md`、`agate/phase-cards/P2-design.md`。

## 结论汇总

| # | 问题 | 级别 |
|---|------|------|
| B1 | 挂载阶段（P6）与 diff 数据源（`git diff --cached`）错位——检测器扫不到代码 | **BLOCKER** |
| B2 | "登记内容进 provenance 审计范围"为虚构声称——七道审计均不含 known-violations | **BLOCKER** |
| B3 | known-violations 与 known-failures 语义相反，"完整复刻"掩盖根本差异 | **WARNING** |
| N1 | design-notes/README.md 未登记本计划文件 | NIT |
| N2 | known-violations.md 模板/格式未定义，count_kf_entries 兼容性存疑 | NIT |

## 事实核验（文档声称 vs 仓库现状）

| 声称 | 核验结果 |
|------|---------|
| `agate-risk-score.py` 的 `score_task()` 返回 dict + `_norm_rel` | ✅ 属实（score_task 在 202 行，_norm_rel 在 86 行）|
| P5 known-failures"读客观快照→比对登记数量"判定 | ✅ 属实（check-gate.py 972-981 行）|
| `_load_script` importlib 模式 | ✅ 属实（check-routing.py:41-52，agate-md-field-set.py 复用）|
| BDD-9 红线"exit code 才是门槛" | ✅ 属实（WORKFLOW.md:310、LIMITATIONS.md:35）|
| ADR-009 界定 `~/.agate` 版本管理根目录 | ✅ 属实（agate/adr.md:259）|
| G0-G3 占比 20/20/25/35 + 决策2"跨越≠超过" | ✅ 属实（design-maintainability-gate.md:75-103）|
| gate_commands 可插拔机制 | ✅ 属实（P2-design.md:125）|
| 阈值 N=1000 无实证、诚实标注 | ✅ 处理得当 |

## B1（BLOCKER）：挂载阶段与 diff 数据源错位——检测器扫不到代码

文档 2.2 将检测挂载到 **P6**（check-gate.py 的 P6 判定函数），但 2.1 定义数据源为 `git diff --cached -U0`（fuzzy-boundary）与 `git show HEAD:path`（god-file）。

矛盾：`git diff --cached` 反映"暂存区 vs HEAD"。代码在 **P4 阶段已 commit**（`gate_p4` 检查暂存区含代码文件，check-gate.py:895），到 P6 commit 时暂存区仅剩 `P6-acceptance.md` 等验收文档——**代码改动早已不在 staged**。

推演：

```text
P4 提交代码 → P5 提交验证 → P6 提交验收文档
P6 时 git diff --cached = 验收文档 diff（不含代码）
→ fuzzy-boundary 永远零命中；god-file before/after 相等
```

即：按文档当前写法，gate 在 P6 是死检测器（永远无 violation），与 BDD 验收标准 1-4 无法成立。

可选修正：

1. 挂载到 **P4**（代码 staged 时），P6 不再挂载；
2. 或数据源改为"任务全量 commit diff"（如 `P4..HEAD` 或 `base_branch...HEAD`），并明确与 pre-commit 单阶段 diff 的口径差异；
3. 或在 BDD 增加"P6 阶段代码已 commit 时仍能检出 violation"的验证用例（当前 BDD 未覆盖该时序）。

## B2（BLOCKER）："登记内容进 provenance 审计范围"是虚构声称

文档 2.2 与 BDD-9 均称"登记内容进 provenance 审计范围，供事后复核"。

核验 `agate/scripts/check-p6-provenance.py` 头部注释的七道审计：

| 审计 | 内容 |
|------|------|
| 1 | 证据-结论对应（1a/1b/1c）|
| 2 | dispatch-context 内容约束 |
| 3 | BDD 总数自动化对照 |
| 4 | UI vision YAML 引用 |
| 5 | 日志 EXIT_CODE 与 PASS/FAIL 一致性 |
| 6 | evidence JSON 与 P6 声明一致性 |
| 7 | P6 引用 P5 证据的无改动校验 |

**无任何一道涉及 known-violations（或 known-failures）登记内容**。登记内容目前不存在任何机械审计。若需审计，须**新增第 8 道审计**——文档既未声明要新增，也未改 provenance 脚本范围，仅声称"已进审计"，会造成"有兜底"的错觉，恰与 self-authored gate 防伪方向相反。

修正：删除该声称，或将"新增 provenance 审计 8"写入范围（与双归零提案的复现证据/举一反三同方向）。

## B3（WARNING）：known-violations 与 known-failures 语义相反

`agate/assets/templates/known-failures-template.md` 明确：

> 本文件只登记**预存失败**（P5 之前就存在的、与当前任务无关的失败）。当前任务引入的失败用 P5-test-results/ 记录，不写本文件。

而 known-violations 登记的是**本次 diff 引入的**反模式（god-file 跨越、fuzzy-boundary 新增行）——属"当前任务引入"类别，与 known-failures 语义**相反**。

文档反复强调"完整复刻 P5 known-failures 既有解法"，但：

- P5 容忍预存失败合理（非本任务引入，登记透明即可）
- known-violations 容忍**本任务自引入**反模式（登记即可放行）= gate 变成"登记了就能带反模式过关"

判据算法可复用，但语义基调不同。文档未论证"为何自引入反模式登记即可放行"这一更激进主张；BDD-9 的"理由字段自由文本供人工复核"无机械兜底，等于回到 v1 批评的"登记即放行"，仅把数量对齐了。

修正建议：正面回答该主张——或默认"登记 ≠ 放行，须 P4 评审 approve"，或引入与双归零一致的复现证据要求。

## N1（NIT）：design-notes/README.md 未登记本计划文件

`docs/design-notes/README.md` 仅登记 `design-maintainability-gate.md`（待立项 RM-AG0046），未含本落地计划文件——与 return-to-zero-proposal 此前漏登记为同类问题。建议补登记。

## N2（NIT）：known-violations.md 模板/格式未定义

`count_kf_entries`（agate_common.py:1015-1017）数的是 `| N |` 行首表格格式；known-violations 若不沿用同格式，计数函数须重写。文档未定义登记模板（字段集、表格头），P1/P2 前应补。

## 建议

1. 修复 B1：决定挂载阶段与 diff 口径（建议 P4 挂载 + 全任务 diff 验证）。
2. 修复 B2：删声称或新增 provenance 审计 8。
3. 修复 B3：明确"自引入反模式登记即放行"的论证与机械兜底。
4. 补 N1/N2：索引登记 + 登记模板定义。
