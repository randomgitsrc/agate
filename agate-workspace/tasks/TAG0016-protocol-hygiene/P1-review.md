---
phase: P1
task_id: TAG0016
type: review
parent: P1-requirements.md
trace_id: TAG0016-P1-20260819
status: approved
created: 2026-08-19
agent: requirements-review
---

# P1-requirements.md 独立评审（TAG0016）—— 第 2 轮复审

这是第 2 轮复审，范围收窄为核查 BDD-12 修订（按
`P1-dispatch-context-requirements-review-retry1.md` 指引，不重新审全部 19 条）。第 1 轮
（`status: needs-revision`）指出的唯一实质问题是 BDD-12 Then 子句括号部分把"P5 通过 commit
hash 的记录来源"描述得像已存在的可读字段，而实地核查 `.state.yaml` 与 `P5-test-results/` 两处
候选位置均无此字段。本轮核查 analyst 的修订是否解决了这个问题。

---

## BDD-12 核查结论——修订到位

当前 P1-requirements.md（第 226-231 行）BDD-12 原文：

> Then check-p6-provenance.py 新增一道审计：读取 P5 gate 通过时的 commit hash 并与 P6 验收发起
> 时点的当前 commit/暂存区状态比对，执行 `git diff <P5通过commit>..HEAD --name-only` 排除仅含
> 协议产出文件……的改动后：非产出文件的 diff 为空 → 判定"无代码改动"成立……**"P5 gate 通过时的
> commit hash"当前无处可直接读取**——经核实 `.state.yaml` 现有 schema（字段为 task_id / phase /
> status / retries / retry_count / updated）不含 commit hash 字段，`P5-test-results/` 里的
> commit 提及是格式不统一的自由文本、不是可稳定 parse 的结构化字段；这是一次需要 P2 新增的
> schema 变更（选定落在 `.state.yaml` 新字段还是 `P5-test-results/` 新增结构化 provenance 头，
> 及对应的解析规则），不是读取既有字段。

对照第 1 轮指出的问题逐点核查：

1. **"既成事实语气"已去除**：原文第 1 轮版本"记录来源为 `.state.yaml` 或 `P5-test-results/`
   的 provenance 信息"这一断言性表述已被删除，替换为加粗强调的"当前无处可直接读取"，明确否定
   了"字段已存在"的读法。
2. **已显式声明这是需要 P2 新增的 schema 变更**：原文明确写出"这是一次需要 P2 新增的 schema
   变更（选定落在 `.state.yaml` 新字段还是 `P5-test-results/` 新增结构化 provenance 头，及对应
   的解析规则），不是读取既有字段"——这正是第 1 轮「处理建议」选项 (a) 的表述，把决策权重显式
   交给 P2，不再是可被误读为"写个 parser 读一下就行"的既成事实。
3. **两处候选位置的核实依据保留且准确**：`.state.yaml` 现有字段清单（task_id / phase / status /
   retries / retry_count / updated）与第 1 轮 review 实地核查结果一致；`P5-test-results/` 的
   "格式不统一的自由文本"表述也与第 1 轮核查结论一致，未引入新的失实断言。

**结论：BDD-12 修订已解决"既成事实语气"问题。**

## 存量兼容说明核查——已补充，表述清楚

紧随 BDD-12 之后新增一段独立的补充说明（第 231 行）：

> 补充说明（数据维度，若字段落在 `.state.yaml`）：新增的 commit hash 字段须声明为**可选**，
> 缺失时回退到强制重跑（不要求 TAG0001~TAG0015 等存量归档任务的 `.state.yaml` 补填该字段）。
> 避免 check-state-yaml.py 未来把该字段设为必填后，历史任务的 `.state.yaml` 被动触发校验时
> 报错。

这段完整覆盖了第 1 轮「隐含需求覆盖·数据维度」指出的"部分遗漏"：①字段可选性已声明；②缺失时的
回退行为（强制重跑）已声明；③明确不要求存量任务回填；④点出了具体风险场景（check-state-yaml.py
未来加严校验导致历史任务被动报错）。表述具体、无歧义，未留下"字段是否可选"的新模糊点。

**结论：存量兼容说明已补充到位，表述清楚。**

## BDD-13 未被意外破坏

当前第 233-236 行 BDD-13 原文与第 1 轮评审时逐字一致（"不可复用边界由 git diff 结果自动判定，
不依赖人工声明或记忆"的判定逻辑未改动）。analyst 的 dispatch-context（P1-dispatch-context-
analyst-retry1.md）明确要求"除非 BDD-12 修法影响了 BDD-13 表述，否则不动"，本轮核查确认
BDD-13 确实未被触碰，其逻辑链条（P4 阶段产生非产出文件改动 → diff 非空 → 强制拦截）依然清楚、
可判定，且不因 BDD-12 括号部分改写而产生新的表述矛盾——BDD-13 引用的仍是同一套 `git diff` 机制，
只是不再假设 commit hash 字段已存在，这一点由 BDD-12 单独声明，BDD-13 无需重复。

**结论：BDD-13 未被意外破坏，沿用第 1 轮"可用（依赖 BDD-12）"判定。**

## BDD 总数与编号连续性核查

`grep -c "^#### BDD-" P1-requirements.md` = 19，编号 BDD-1 至 BDD-19 连续无跳号无重复（`grep -n
"^#### BDD-"` 逐行核对，标题与第 1 轮评审时记录的标题文本一致）。

Frontmatter 关键字段（`risk_level: high`、`phases: [P0...P8]`、`packages: [...]`、
`domains: [protocol-docs, gate-scripts, test-infra]`）与第 1 轮评审时一致，未被本轮修订意外
改动——符合 analyst dispatch-context「不要因为修 BDD-12 就顺带调整 domains/packages/risk_level/
phases 等 frontmatter 字段」的约束。

## BDD-2 / 3.1 节可选补充——已做，表述合理（非阻塞，不构成 approve/reject 判据）

3.1 节「同类扫描」判定段末尾新增一句（第 95 行）：

> 本条不留给 P2 二次判断权威源归属——上述独家内容量对比（能力矩阵 + Windows 安装指南 vs
> 另两处的一句话摘要/调用侧说明）已经充分，无需 P2 重新调查判断。

这是第 1 轮「补充意见」建议的可选项，analyst 选择了处理。表述清楚地说明了"为何本条不留给 P2
二次判断"的理由（独家内容量对比已充分），与 BDD-2 判定 platform-notes.md 为权威源的结论一致，
未引入新的矛盾或模糊。按 dispatch-context 指引，此项加不加都不影响本轮结论，此处仅确认表述
合理。

## 沿用第 1 轮的其余结论（不重复展开）

按 dispatch-context 约束 5，以下结论第 1 轮已完成且结论稳定，本轮直接沿用，本轮核查未发现
analyst 的改动意外波及这些部分：

- **同类扫描可信度复核**（3.4/3.5/3.6 节抽查 3 条）：与 P1 正文判定一致，grep 复现结果吻合。
- **BDD 判据行号绑定抽查**（BDD-2/BDD-5/BDD-9）：三条 Then 子句均未把行号数字写死为判据。
- **BDD-14"文字游戏"检查**：Given/Then 区分现状与目标清楚，非文字游戏。
- **其余 17 条 BDD 逐条判定**（BDD-1、BDD-3~11、BDD-14~19）：18 条"可用"、1 条（BDD-19 第二段）
  "部分可用但不需退回"，判定结论、覆盖维度标注均沿用第 1 轮「BDD 评审」节全文，未重新展开。
- **隐含需求覆盖**（数据/前端/多端/边界/兼容五维度）：数据维度的"部分遗漏"已在本轮通过 BDD-12
  附近的补充说明解决（见上文），其余四个维度（前端不适用、多端覆盖、边界覆盖、兼容覆盖）判定
  沿用第 1 轮结论不变。
- **裁剪评审**：无裁剪、全部走 P1-P8，理由核对 WORKFLOW.md 风险矩阵后确认站得住，沿用第 1 轮
  结论。

---

## 总体结论

BDD-12 修订已解决第 1 轮指出的"既成事实语气"问题，显式声明为需要 P2 设计的 schema 变更；存量
兼容说明（字段可选 + 缺失回退强制重跑 + 不要求存量任务回填）已补充到位；BDD-13 未被意外改动，
逻辑链条依然清楚；BDD 总数仍为 19、编号连续、其余内容与第 1 轮评审时一致；BDD-2/3.1 节的可选
补充已做且表述合理。

**status: approved**——本轮复审确认 P1-requirements.md 19 条 BDD 全部可用（18 条第 1 轮已判定
可用 + BDD-12 本轮修订后可用），无遗留阻塞项，可推进 P2。

---

## 门槛自检

- BDD-12 修订是否解决"既成事实语气"问题：完成核查，**已解决**（引用修订后原文见上）
- BDD-13 是否被意外破坏：完成核查，**未破坏**（逐字比对与第 1 轮一致）
- BDD 总数是否仍为 19、编号连续：完成核查，**19 条，BDD-1~BDD-19 连续无跳号**
- Header status 字段与结论一致：`approved`，与本文件"总体结论"一致
