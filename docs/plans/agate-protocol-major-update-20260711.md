---
task_id: agate-protocol-major-update-20260711
agent: main
date: 2026-07-11
status: 方案 v7（砍掉 N4 trivial 分支：P1 评审不可裁，所有任务都走独立 requirements-review，gate 逻辑回归简单）
来源: 本轮讨论（基于 p6-gate-institutional-design v3 + 四轮问答）
---

# agate 协议大更新方案

> 本方案整合了 p6-gate-institutional-design v3 的 7 个部件 + 本轮讨论产生的 5 个新部件，共 12 个部件。新部件编号从 ⑧ 开始，与原方案 ①-⑦ 连续编号。③ 按本轮讨论修正，完全替代原方案 ③。①②④⑤⑥⑦ 完整内联于本方案，不再引用外部文件。

## 总原则

**先疏后堵**（R8）：造假不是因为"没有出口"，而是正规出口（重试/回退/PAUSED）被误用或贴了负标签，造假在性价比上插了队。解法是修出口的语义和排序（让正路更快、失败免责、红灯指向溯源），最后才拿走作弊工具。

## 诚实标注

本方案是**结构性修复**，不是增量加固。它修正了此前所有"加检查/降门禁"方案的同一盲区：producer=judge=editor 同体时，纯检测是输家的军备竞赛——agent 能满足的任何 bar 都不可信，加更多检查只告诉造假者该造什么。

但本方案也有边界：
- ①②③（激励层）依赖主 Agent 遵循协议文本——是 L0 指导，非 L3 硬拦截。效果取决于"语义翻转"对 LLM 行为的实际影响，这需要实证验证
- ④（结构层）对测试类证据是强解，对 UI 类证据受限于项目是否有 CI e2e 流水线——agate 栈无关，不能假设
- ⑧⑨⑪（结构性缺口）是 L0 指导 + L3 gate 脚本混合——P1 review 的 gate 检查是 L3，但 review 质量本身是 L0
- ⑨ P5 subagent 化后，P5 gate 对 subagent 伪造测试结果的防御依赖 CI backstop——commit 前无法 100% 验证

## 保留机制（本方案不改，但必须保留）

以下机制是 agate 已有的防空/防丢失设计，本方案不改动但**不得遗漏**：

| 机制 | 文件 | 作用 |
|------|------|------|
| **subagent 分阶段落盘** | dispatch-protocol.md + 各角色文件 + dispatch-prompt.md | subagent 每读完一个输入或完成一个关键步骤，立即追加写入 `P{N}-progress.md`（bash 追加）。防空返回——即使 subagent 最终无法产出完整报告，progress 文件也能让主 Agent 知道它做了什么 |
| **主 Agent 防无响应落盘** | orchestrator-template.md | 主 Agent 在长操作前写 `NEXT: ...` 到 `orchestrator-log.md`，降低单次推理复杂度。写下去的那一刻就完成了使命，不需要再读回来。恢复任务用 `.state.yaml` + 产出文件 |
| **dispatch-context 派发前写** | dispatch-protocol.md + ⑪ | 主 Agent 在派发前写 `P{N}-dispatch-context.md`（客观信息 + 任务上下文），派发后冻结 |
| **C7 规则** | dispatch-protocol.md | subagent 自我报告不可信，gate 一律以主 Agent 亲自跑命令的结果为准 |
| **铁律 1-3** | dispatch-protocol.md | ① 用 task 工具派发不亲自执行；② prompt 只传路径不传内容；③ subagent 只返回路径+摘要 |
| **CI backstop** | protocol-tests.yml | push 后重跑 gate + git blame 单 author WARNING，捕获 `--no-verify` 绕过 |

本方案新增的 `P{N}-gate-diagnosis.md`（⑫）与 `P{N}-progress.md` 是不同文件：
- `progress.md`：subagent 写，防空返回，逐条追加，是过程记录
- `gate-diagnosis.md`：主 Agent 写，防诊断丢失，一次性写出，是诊断结论

---

## 本轮讨论产生的新结论

| # | 问题 | 结论 |
|---|------|------|
| Q1 | P1 没有独立需求评审 | P2 review 评审的是 P2 设计，不是 P1 需求基线。P1 应有 requirements-review |
| Q2 | check-p6-format.sh 原来各环节都有？ | 不是。v1 流程图画错了。provenance 审计只在 P6 触发，auto-fix 也只在 P6 |
| Q3 | 回退机制混乱 | 诊断→跳转→PAUSED→人工批准→修→重跑。逐步是诊断过程，不是执行过程 |
| Q4 | P5/P7/P8 主 Agent 亲自跑不合理 | 有 gate 后全部可 subagent 化。主 Agent 只做 P0-brief + READY 收尾 |
| Q5 | 主 Agent 如何写好 prompt | dispatch-context 扩展 + 任务节模板化 + gate 诊断自动落入 |

---

## 方案总览

| 部件 | 改什么 | 层次 | 来源 | 优先级 |
|------|--------|------|------|--------|
| ① | P6 自动格式化断掉"自己写更快"的算计 | 激励 | 原方案 | 🔴 |
| ② | PAUSED 语义翻转：责任绑流程不绑绿灯 | 激励 | 原方案 | 🔴 |
| ③ | 红 gate 诊断→跳转→PAUSED→修→重跑 | 激励 | 原方案+Q3修正 | 🔴 |
| ④ | P6 证据由 CI 执行生成、agent 只引用 | 结构 | 原方案 | 🟡 |
| ⑤ | Subagent 假完成：主 Agent 文件校验 | 结构 | 原方案 | 🟡 |
| ⑥ | Gate 正则语义化放宽 | 卫生 | 原方案 | 🟡 |
| ⑦ | verification_env 条件化（仅 ui_affected） | 卫生 | 原方案 | 🟢 |
| **⑧** | **P1 需求评审** | 结构 | Q1 | 🔴 |
| **⑨** | **P5/P7/P8 subagent 化** | 结构 | Q4 | 🔴 |
| **⑩** | **do→review 迭代循环** | 结构 | Q3 | 🟠 |
| **⑪** | **dispatch-context 扩展 + 任务节模板化** | 结构 | Q5 | 🔴 |
| **⑫** | **gate 诊断落盘** | 结构 | Q5 | 🟠 |

---

## ⑧ P1 需求评审

### 问题

当前协议 P1 没有 subagent 评审。P2 的 design-review 评审的是 P2 设计方案，不是 P1 需求基线。需求基线是整个流程的地基——如果需求本身有歧义或遗漏，下游全白做。

### 方案

P1 阶段增加 `requirements-review` subagent，与 P2 的 `design-review` 对称：

| 阶段 | 评审角色 | 评审对象 | 评审重点 | 产出文件 |
|------|---------|---------|---------|---------|
| P1 | requirements-review | P1-requirements.md | BDD 完整性、隐含需求覆盖、裁剪合理性、风险遗漏 | P1-review.md |
| P2 | design-review | P2-design.md | 方案可行性、权衡合理性、四字段完整 | P2-review.md |

### 修改清单

**1. 新增 `assets/review-roles/requirements-review.md`**

```yaml
---
role_id: requirements-review
type: review
phases: [P1]
mode: 需求基线评审
---
```

评审清单：
- BDD 条件是否可二值判定（PASS/FAIL）
- 隐含需求是否按维度覆盖（数据/前端/多端/边界/兼容）
- 裁剪跳过的阶段理由是否充分
- risk_level 是否与实际风险匹配
- capability_requirements 三态判断是否正确
- 有无掺入解决方案设计（P1 只定义问题）

### review 实质锚点校验（N3）

review 类 subagent 不能靠 ⑤ D2 兜底——D2 是 grep 代码文件改动，对 review 产出无效（review 文件确实写了，D2 grep 不到"是否真审查了"）。review 产物的可信性需要**实质锚点**：review 结论必须引用具体产物锚点，而非裸 "approved" 或 "BLOCKER=0"。

**requirements-review 的实质锚点要求**：

| review 结论 | 必须引用的锚点 | 校验方式 |
|------------|--------------|---------|
| approved | 每条 BDD 编号 + 覆盖维度清单（数据/前端/多端/边界/兼容逐项标注） | check-gate.sh P1 分支检查 P1-review.md 含 BDD 编号引用（`BDD-[0-9]`）+ 覆盖维度标注 |
| 隐含需求覆盖 OK | 列出覆盖的隐含需求条目编号 | 主 Agent 目视或 gate 脚本检查 `隐含需求` 关键词 + 条目引用 |
| 裁剪合理 | 逐个跳过阶段 + 理由 | 已有 gate 检查（check-pruning.sh），不变 |

**gate 脚本更新**：`check-gate.sh` P1 分支增加——P1-review.md 含 `BDD-` 或 `B[0-9]` 编号引用（轻量正则查锚点存在性），不含则 exit 1。这不是语义审查（LLM 审查层做），是结构兜底——裸 "approved" 连编号都不引用，极可能是假完成。但**锚点正则只拦最懒的假完成**（不引用编号）；引用了编号但没真审查的 reviewer 仍可通过。真正的反造假靠 LLM 语义审查层（self-gate Layer 1）+ 引错 BDD 编号会在下游 P6/P7 暴露。

### P1 评审不可裁（砍掉 N4 trivial 分支）

N4 原建议给 P1 评审加 `requirement_trivial` 泄压阀（analyst 自检替代独立 review）。**砍掉**，理由：

1. **自己审自己审不出盲点**——P1 review 的核心价值是独立视角发现需求遗漏，analyst 自检等于没审
2. **trivial 任务的 P1 本来就短**——review 耗时低，没有需要泄压的真实瓶颈
3. **P2 的 design_trivial 有道理**（1 候选方案 vs 2 候选方案是客观结构差异），P1 review 没有类似的"结构差异"可以收窄
4. **留口子 = 主 Agent 会走口子**——省的不是 reviewer 的时间，是主 Agent 派发 subagent 的编排步骤，但这个编排步骤恰恰是 agate 的核心价值

**结论**：所有任务都走独立 requirements-review，无例外。P1 评审不可裁，与 P2/P6 不可裁同级。

**2. `dispatch-protocol.md`** — P1 派发流程增加 requirements-review 步骤

**3. `phase-cards/P1-requirements.md`** — 增加评审步骤

**4. `check-gate.sh` P1 分支** — 增加 P1-review.md 检查（无条件，所有任务统一）：

```
要求 P1-review.md 存在 + status:approved + agent≠main + 含 BDD-/B[0-9] 锚点，缺则 exit 1
```

bats 用例（`unit/check-gate.bats` 补充）：
- 缺 P1-review.md → exit 1
- P1-review.md agent=main → exit 1
- P1-review.md 无 BDD 编号引用 → exit 1
- P1-review.md status:approved + agent≠main + 含锚点 → exit 2（需主 Agent 自判 BDD 编号格式）

**5. `WORKFLOW.md`** — P1 评审角色列更新

**6. `check-protocol-consistency.py`** — CHECK 9 锚点表新增：P1 review agent≠main → check-gate.sh

### bats 测试

- `unit/check-gate.bats` 补充：P1 gate 检查 P1-review.md approved + agent≠main

---

## ⑨ P5/P7/P8 subagent 化

### 问题

当前协议让主 Agent 亲自跑 P5/P7/P8，与 orchestrator-template.md 的"只做四件事"矛盾。有 gate 机制后，主 Agent 只需"派发→验 gate→推进"，不需要亲自执行。

### 方案

| 阶段 | 当前 | 改为 | 角色 |
|------|------|------|------|
| P5 | 主 Agent 亲自跑 gate_commands.P5 | 派发 verifier subagent | verifier（P5 模式） |
| P7 | 主 Agent 亲自做交叉检查 | 派发 consistency-reviewer subagent | 新角色 |
| P8 | 主 Agent 亲自做发布步骤 | 派发 releaser subagent | implementer（P8 模式） |

**主 Agent 只亲自做两件事**：
1. P0-brief（编排者本职，PM 视角）
2. P8 READY 收尾检查（编排者最终责任：环境清理+生产确认）

### 修改清单

**1. `phase-cards/P5-verification.md`** — 改为 subagent 派发模式

**2. `phase-cards/P7-consistency.md`** — 改为 subagent 派发模式

**3. `phase-cards/P8-release.md`** — 改为 subagent 派发模式，READY 收尾仍为主 Agent。releaser subagent 产出 P8-release.md（含临时资源清单：本任务启动的临时服务/进程/数据/开发安装），主 Agent 据此执行 READY 收尾检查（清理临时资源 + 环境确认）。临时资源清单是 releaser→主 Agent 的交接文件，不是主 Agent 自己写的

**4. 新增 `assets/execution-roles/consistency-reviewer.md`**

```yaml
---
role_id: consistency-reviewer
type: execution
phases: [P7]
mode: 一致性交叉检查
---
```

职责：
- DESIGN_GAP 配对（P4 声明 → P7 转抄 + REVIEWED）
- SCOPE+ 闭环
- 跨文件一致性（P2 packages vs P8 bump、P1 BDD vs P6 验收、P4 实现 vs P2 设计）
- 未决项清零

### consistency-reviewer 实质锚点校验（N3）

consistency-reviewer 是 review 类 subagent，不能靠 ⑤ D2 兜底（D2 grep 代码改动，对 review 产出无效）。P7-consistency.md 中的 `BLOCKER=0` 必须附带实质锚点，证明真做了交叉检查：

| 结论 | 必须引用的锚点 | 校验方式 |
|------|--------------|---------|
| BLOCKER=0 | 逐条 DESIGN_GAP 配对项 + `[DESIGN_GAP_REVIEWED:]` 标记 | check-gate.sh P7 已检查 DESIGN_GAP 配对（现有逻辑） |
| CRITICAL=0 | 列出跨文件检查项 + 引用源文件行号或节名 | check-gate.sh P7 增加：P7-consistency.md 含 `DESIGN_GAP_REVIEWED` + 跨文件引用标记 |
| SCOPE+ 闭环 | 列出 SCOPE+ 条目 + 对应 `[SCOPE_RESOLVED]` | check-scope-resolved.sh 已覆盖 |

**gate 脚本更新**：`check-gate.sh` P7 分支增加——P7-consistency.md 含至少一个 `DESIGN_GAP_REVIEWED` 标记或跨文件引用关键词（`P1.*BDD\|P2.*packages\|P4.*implementation`），不含则 WARNING（不 ERROR——P7 可能无 DESIGN_GAP）。

### P5 commit→push 窗口残余风险（N5）

P5 改为 verifier subagent 跑测试后，伪造的 P5-test-results 在 **commit→push→CI** 之间会流向下游——P6 verifier 会复用 P5-test-results（verifier.md 输入已写），本地任务链可能跑在伪造结果上。

**残余风险**：分支保护保证伪造进不了 main（CI backstop 兜底），但**本地 P6/P7/P8 在 push 前被污染、白跑**。

**缓解**：主 Agent 按 ⑤ D2 对 P5-test-results 做最小校验——grep test runner 的真实输出签名（如 pytest 的 `passed`/`failed` 汇总行、bats 的 `ok/not ok`），不信裸 `failed: 0`。具体：
- `grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md` → 计数 >0 才信（证明真跑了 test runner）
- 计数 =0 → 疑似伪造，重派 verifier 或 PAUSED

这是**轻量校验**，不重新跑测试，只验证产出文件含 test runner 的真实输出签名。

**5. `verifier.md`** — P5 模式增加"从 P2-design.md 读取 gate_commands.P5 并执行"的明确指令

**6. `implementer.md`** — P8 模式已有，确认覆盖 bump-version + CHANGELOG + P5 重跑 + git tag

**7. `orchestrator-template.md`** — "你的角色"节更新：主 Agent 只做 P0-brief + READY 收尾，其余全部派发

**8. `dispatch-protocol.md`** — P5/P7/P8 派发流程更新

**9. `dispatch-protocol.md` 可判定门槛规范** — P5/P7/P8 门槛表更新

**10. `check-protocol-consistency.py`** — CHECK 9 锚点表新增：P7 consistency-reviewer → check-gate.sh

### P5 gate 验证方式

P5 subagent 跑测试后，主 Agent 验 gate 的方式：

| 验证项 | 方式 | 理由 |
|--------|------|------|
| P5-test-results/ 存在且非空 | check-gate 脚本检查 | 产出存在性 |
| failed 计数 | gate 脚本读 unit.md 的 failed 字段 | 外部产出 gate（test runner exit code），非自写文件 gate |
| PROD_TOUCHED | gate 脚本扫描暂存 diff | 客观检查 |
| 测试是否真的跑了 | **CI backstop 兜底** | commit 前无法 100% 验证 subagent 确实跑了测试而非伪造结果；push 后 CI 重跑是最终兜底 |

**与 C7 规则的关系**：C7 说"subagent 自我报告不可信"。P5 的 failed 计数写在 unit.md 里——这是 subagent 写的文件，按 C7 不可信。但 P5 是外部产出 gate（test runner 的 exit code 是客观事实），不是自写文件 gate（如 P1/P2/P6/P7）。区分：

- **自写文件 gate**（P1/P2/P6/P7）：gate 检查的是 agent 自己写的文件内容 → 造假风险高 → 需要额外审计（provenance、review subagent）
- **外部产出 gate**（P3/P4/P5）：gate 检查的是外部工具输出（test runner exit code、暂存区文件）→ 造假需要伪造外部工具输出 → 成本高 → CI backstop 兜底足够

P5 的 unit.md 虽然是 subagent 写的，但它的内容来自 test runner 的输出（subagent 执行 `pytest -q --tb=no` 并记录结果）。伪造 unit.md 需要同时伪造 test runner 的 exit code（subagent 可以做到），但 CI backstop 会在 push 后重跑测试暴露伪造。这与 P6 的 provenance 审计不同——P6 没有 CI 重跑验收的兜底。

**结论**：P5 gate 保持当前设计——subagent 跑测试、产出 P5-test-results/，主 Agent 验 gate（检查产出文件存在性 + failed 计数 + PROD_TOUCHED），CI backstop 兜底。

### P7 输入文件数量

P7 consistency-reviewer 需要读 P1-P6 全部产出（5+ 个文件），超过 dispatch-protocol.md 的"输入文件超过 5 个应拆分"指引。

**处理**：P7 是例外，不拆分。理由：
1. 一致性检查天然需要跨文件对照，拆分会丧失交叉检查能力
2. consistency-reviewer 的角色文件明确列出需要读的文件和关注点，提供输入导航
3. dispatch-context.md 的任务上下文节提供关键决策摘要，减少 subagent 需要从产出文件中自行提取的信息量

在 dispatch-protocol.md 的任务粒度指引中增加例外说明："P7 一致性检查天然需要跨文件对照，不受输入文件数限制。"

### bats 测试

- `unit/check-gate.bats` 补充：P5/P7/P8 gate 在 subagent 产出下的行为
- `integration/` 补充：P5 subagent 产出 → gate 通过/失败的端到端场景

---

## ⑩ do→review 迭代循环

### 问题

当前流程图和协议把"do→review"画成单次判定。实际上 review 不通过 → 修改 → 再 review 是循环，直到 review 通过才推进到下一阶段。

### 方案

在协议中明确：每个"do→review"阶段都是迭代循环，不是单次通过/失败。

**迭代循环的阶段**：

| 阶段 | do | review | 循环语义 |
|------|-----|--------|---------|
| P1 | analyst 写需求 | requirements-review | review 否 → analyst 修改 → 再 review → … → approved |
| P2 | architect 写方案 | design-review | review 否 → architect 修改 → 再 review → … → approved |
| P4 | implementer 写代码 | design-review(可选) | review 否 → implementer 修改 → 再 review → … → approved |
| P6 | verifier 写验收 | provenance 审计 | 格式问题 → verifier 调格式 → 再审计 → … → 通过 |
| P7 | consistency-reviewer | gate 脚本 | BLOCKER → reviewer 修改 → 再验 gate → … → 通过 |

**不适用迭代循环的阶段**：

| 阶段 | 理由 |
|------|------|
| P0 | 主 Agent 亲自写，无 subagent 评审 |
| P3 | gate 是 check-tdd-red.sh（脚本判定红灯/绿灯），不是 review subagent |
| P5 | gate 是 test runner exit code（外部产出），不是 review subagent |
| P8 | gate 是脚本检查（bump_type + version + CHANGELOG），不是 review subagent |

### 修改清单

**1. `dispatch-protocol.md`** — 增加"do→review 迭代循环"节

**2. `state-machine.md`** — 在评审相关转移规则旁增加迭代注释

**3. `phase-cards/` P1/P2/P4/P6/P7** — 在评审步骤中明确"review 不通过 → 修改 → 再 review"的循环

### retry 预算分配

review 迭代和 gate 重试**共享同一阶段 retry 预算**（`retries[Pn]`）。理由：
1. 两者的失败根因相同——产出质量不够
2. 分开计数增加主 Agent 认知负担，且无额外收益
3. 共享预算自然收敛：review 迭代消耗预算 → 剩余预算给 gate 重试 → 超限 PAUSED

**但**：review 迭代的第一轮不算 retry（首次 review 是正常流程，不是重试）。从 review 第二轮开始算 retry。

| 事件 | retry 计数 |
|------|-----------|
| 首次 do → 首次 review | 不算 retry |
| review 不通过 → 修改 → 再 review | retries[Pn] += 1 |
| gate 不通过 → 修改 → 再验 gate | retries[Pn] += 1 |
| review + gate 交替失败 | 共享累加 |

### bats 测试

无需新增脚本态。这是 L0 指导层改动。

---

## ⑪ dispatch-context 扩展 + 任务节模板化

### 问题

主 Agent 不读产出文件全文、不亲自实现，那它凭什么写出精准的 prompt？当前 dispatch-context.md 只覆盖"主 Agent 查证的客观信息"（URL、选择器、环境状态），不覆盖"任务特定的上下文导航"。当前 prompt 模板的"## 任务"节只要求"一两句话"——这是最关键的缺口。

### 分析：主 Agent 的理解来源

主 Agent 不需要读全文来写好 prompt。它的理解来源是：

| 信息来源 | 主 Agent 怎么获得 | 用在哪 |
|---------|------------------|--------|
| 任务目标和风险 | **P0-brief 亲自写** | 每次派发的项目约定节 |
| 上游产出的结构和关注点 | 协议知识（角色文件的节定义） | 输入导航 |
| 上游产出的结构化字段 | **grep 提取**（packages/domains/ui_affected/gate_commands/files_to_read） | dispatch-context 任务上下文 |
| 上游产出的具体内容/问题 | **gate 失败时的诊断** + **subagent 返回的一句话摘要** | 修复重派 / 回退时的诊断信息 |
| 上一阶段的关键决策 | subagent 摘要 + 残余风险字段 | dispatch-context.md 的任务上下文节 |

**关键补充**：P2-design.md 的结构化字段（packages/domains/ui_affected/gate_commands/files_to_read）是主 Agent 可以 grep 提取的——不是读全文，是读特定字段。这些字段对下游派发至关重要（P4 需要 files_to_read、P5 需要 gate_commands.P5、P8 需要 packages），主 Agent 应在 dispatch-context.md 的任务上下文节中引用这些字段值。

### 方案

**1. dispatch-context.md 扩展**：从"只放客观信息"扩展为"客观信息 + 任务上下文"

当前结构：
```markdown
## 客观信息（主 Agent 已查证）
- 环境状态：...
- 关键路径/标识：...
- 接口/结构清单：...
```

扩展后结构：
```markdown
## 客观信息（主 Agent 已查证）
- 环境状态：...
- 关键路径/标识：...
- 接口/结构清单：...

## 任务上下文（主 Agent 从 P0-brief + gate + 摘要积累）
- 目标：本阶段要解决什么问题
- 关注点：从上游产出/gate 诊断中提取的关键约束
- 已知风险：P0-brief 的 known_risks 中与本阶段相关的
- 上游关键决策：上一阶段 subagent 摘要中提到的关键选择
- 上游结构化字段（从 P2-design.md grep 提取，非读全文）：
  - packages: {值}
  - domains: {值}
  - ui_affected: {值}
  - gate_commands.P5: {值}（P5/P6/P8 派发时）
  - files_to_read: {值}（P4 派发时）
- 回退诊断（仅回退时）：失败 BDD 清单 / verifier 诊断 / 修复方向
```

**2. "## 任务"节模板化**：从自由文本改为结构化

当前：
```
## 任务
{这个阶段要做什么，一两句话}
```

改为：
```
## 任务
目标：{一句话：本阶段要产出什么}
关注点：{从 dispatch-context.md 任务上下文节提取，2-5 条}
已知约束：{从 P0-brief + 上游产出提取}
与上阶段关联：{上一阶段 subagent 摘要中的关键信息}
```

**3. 主 Agent 写 dispatch-context.md 的信息来源**：

| 来源 | 何时写入 | 写什么 |
|------|---------|--------|
| P0-brief | 首次派发 P1 时 | 目标 + 已知风险 |
| subagent 返回摘要 | 每次收到 subagent 返回时 | 上游关键决策 |
| gate 诊断 | gate 失败时 | 关注点 + 回退诊断 |
| 主 Agent 查证 | 派发前查证客观信息时 | 客观信息节 |
| P2-design.md 结构化字段 | P4/P5/P6/P8 派发时 | packages/domains/gate_commands/files_to_read |

**4. dispatch-context.md 的生命周期**：

- 每个阶段一个文件：`P{N}-dispatch-context.md`
- 主 Agent 在派发前写，派发后**冻结**（provenance 审计需要初始版本不变）
- 重试/回退时的诊断信息**不追加到 dispatch-context.md**，写入单独的 `P{N}-gate-diagnosis.md`（见 ⑫）
- 回退时：新写目标阶段的 dispatch-context.md，包含回退诊断信息

### 修改清单

**1. `dispatch-protocol.md`** — 
- "客观信息落盘"节扩展为"dispatch-context.md 规范"
- 增加任务上下文节的结构定义
- 增加主 Agent 写 dispatch-context.md 的信息来源表
- "派发 prompt 模板"的"## 任务"节改为结构化模板

**2. `assets/templates/dispatch-prompt.md`** — "## 任务"节改为结构化模板

**3. `check-p6-provenance.sh`** — 审计 2（dispatch-context 审计）需适配扩展后的结构

**4. `orchestrator-template.md`** — "主 Agent 的合法职责"节更新：dispatch-context.md 包含任务上下文

**5. `check-protocol-consistency.py`** — CHECK 9 锚点表新增：dispatch-context 任务上下文 → check-p6-provenance.sh；DOC_ALIGNMENT_ANCHORS 表新增：dispatch-protocol.md 含"任务上下文"关键词

### 关键约束

- dispatch-context.md **禁止包含 PASS/FAIL 预判**（已有约束，不变）
- dispatch-context.md **派发后冻结**——provenance 审计检查的是派发时的初始版本，追加内容会破坏审计基准
- 任务上下文节写的是"关注点"和"已知约束"，不是"应该怎么做"——后者是 subagent 的自主决策空间
- 主 Agent 不读产出文件全文——任务上下文的信息来源是 P0-brief + gate 诊断 + subagent 摘要 + P2 结构化字段 grep，不是主 Agent 读完 P1-requirements.md 后的提炼
- P2 结构化字段的 grep 提取是**读特定字段**，不是读全文——`grep -E '^(packages|domains|ui_affected|gate_commands|files_to_read):' P2-design.md`

### bats 测试

- `unit/check-p6-provenance.bats` 补充：dispatch-context.md 含任务上下文节时的审计行为
- `unit/dispatch-context-warning.bats` 补充：dispatch-prompt.md 含结构化任务节关键词

---

## ⑫ gate 诊断落盘

### 问题

gate 失败时，主 Agent 需要诊断原因并决定路由（重试/退回/PAUSED）。当前诊断信息只在主 Agent 的上下文中，不落盘。回退时需要携带诊断信息给上游 subagent，但当前没有机制保证诊断信息被传递。

### 方案

gate 失败后，主 Agent 的诊断结果**写入单独的 `P{N}-gate-diagnosis.md`**，不追加到 dispatch-context.md（后者派发后冻结，见 ⑪）。

**诊断信息结构**：

```markdown
---
phase: P6
date: 2026-07-11
trigger: gate_fail
---
# P6 Gate 诊断

- gate 结果：FAIL=3, NC=0
- 失败项：B03 过期链接返回 404 非 410, B07 批量操作无确认, B12 并发竞态
- 诊断：P4 实现问题（B03/B07）+ P2 设计问题（B12 未考虑并发）
- 路由：B03/B07 → 退回 P4；B12 → 标 [SCOPE+] 增补 P1
- 修复方向（P4）：link-service.ts 的 TTL 检查逻辑 + batch 的确认流程
```

### 诊断格式禁令（N2）

`gate-diagnosis.md` 和 `dispatch-context.md` 回退诊断节**禁止使用 `^\s*- (PASS|FAIL)` 行首格式**列失败项。理由：`check-p6-provenance.sh` 审计 2 grep `^\s*- (PASS|FAIL)\b` 于 dispatch-context.md，命中即判为"验收结论预判" exit 1。诊断中的失败项是**事后诊断**不是预判，但审计 2 分不出两者。

**允许的格式**（不触审计 2）：
- `失败项：B03, B07`（内联，非列表行首）
- `- 失败BDD: B03 过期链接返回 404`（前缀 `失败BDD` 不匹配 `(PASS|FAIL)\b`）
- `gate 结果：FAIL=3, NC=0`（等号后，非行首列表）

**禁止的格式**（触审计 2）：
- `- FAIL B03: 过期链接返回 404`（行首 `- FAIL` 命中审计 2）
- `- PASS B01: 已验证`（同理）

**dispatch-context.md 回退诊断节**只放 `gate-diagnosis.md` 的**路径引用**，不 inline 诊断内容（方案 ⑪ 已有此约束，此处重申并绑定 N2 禁令）。

### bats 测试（N2 固化）

- `unit/check-p6-provenance.bats` 补充：
  - dispatch-context 含"回退诊断节引用 gate-diagnosis.md 路径" → 审计 2 放行
  - dispatch-context 含 `- FAIL B03` 行首 → 审计 2 exit 1（误触预判）
  - gate-diagnosis.md 含 `失败项：B03, B07` → 不触发审计 2（gate-diagnosis.md 不在审计 2 扫描范围内，但 dispatch-context 引用路径不 inline 内容 → 审计 2 放行）

**落盘时机**：

| 场景 | 落盘位置 | 何时写 |
|------|---------|--------|
| 重试（本步抖动） | `P{N}-gate-diagnosis.md` | 诊断后立即写 |
| 退回上游 | `P{N}-gate-diagnosis.md` + 目标阶段新 dispatch-context.md 引用诊断 | 退回前写 |
| PAUSED | `PAUSED-resolution.md` 引用 `P{N}-gate-diagnosis.md` | PAUSED 时写 |

**与 ⑪ 的关系**：
- ⑪ 定义 dispatch-context.md 派发后冻结
- ⑫ 定义诊断信息写入单独文件，不破坏 dispatch-context.md 的冻结状态
- 回退时：新写目标阶段的 dispatch-context.md，在"回退诊断"子节引用 `P{N}-gate-diagnosis.md` 路径（subagent 自己读诊断文件）

**与 ③ 的关系**：
- ③ 定义回退时"携带诊断信息"
- ⑫ 定义诊断信息的落盘格式和传递方式
- ⑫ 是 ③ 的操作化

### 修改清单

**1. `dispatch-protocol.md`** — 增加"gate 诊断落盘"节

**2. `state-machine.md`** — 在回退转移规则旁增加诊断落盘要求

**3. `phase-cards/` 各阶段** — 在"gate 不通过"段增加诊断落盘步骤

### bats 测试

无需新增脚本态。这是 L0 指导层改动。

---

## ③ 修正：回退机制

原方案 ③ 选了"方案 A（顺代码，一次退一阶）"。本轮讨论修正为"诊断→跳转→PAUSED→人工批准→修→重跑"。**本节完全替代原方案 ③**。

### 修正后的逻辑

**逐步是诊断过程，不是执行过程**：

1. **诊断**：主 Agent 分析 gate 失败原因，确定问题源头在哪一阶段，落盘 `P{N}-gate-diagnosis.md`（见 ⑫）
2. **跳转**：直接改 .state.yaml phase 到目标阶段
3. **PAUSED**（diff≥2 时）：check-state-transition.sh 拦截 → 主 Agent 在 PAUSED resolution 中写明诊断和目标 → 人工批准
4. **恢复到目标**：修完后从目标往下逐阶段重跑
5. **不在中间阶段停留**：诊断已确认问题在源头，中间阶段不需要重做

### diff=1 的回退（无需 PAUSED）

| 回退 | diff | 流程 |
|------|------|------|
| P5→P4 | 1 | 直接退，带诊断信息（写入 P4-dispatch-context.md 的回退诊断节） |
| P6→P5 | 1 | 直接退（但 P5 通常不是问题源头，更常见是 P6→P4） |

### diff≥2 的回退（PAUSED + 诊断）

| 回退 | diff | 流程 |
|------|------|------|
| P4→P2 | 2 | PAUSED → 人工批准诊断 → 恢复 P2 → 修完 → P3→P4 重跑 |
| P6→P4 | 2 | PAUSED → 人工批准诊断 → 恢复 P4 → 修完 → P5→P6 重跑 |
| P6→P2 | 4 | PAUSED → 人工批准诊断 → 恢复 P2 → 修完 → P3→P4→P5→P6 重跑 |
| P7→P4 | 3 | PAUSED → 人工批准诊断 → 恢复 P4 → 修完 → P5→P6→P7 重跑 |

### 对 check-state-transition.sh 的影响

**不改脚本**。diff≥2 仍强制 PAUSED。但 PAUSED 的语义从"认输"变为"诊断通道"——主 Agent 在 PAUSED resolution 中写明诊断和目标，人工批准后恢复到目标阶段。这与 ② PAUSED 语义翻转协同。

---

## ① 疏通 honest path：P6 自动格式化

### 问题

P6 格式摩擦的根因不是"格式没规定"（verifier.md 已有详尽规范），而是"规定了但生成时不被机器强制、gate 事后才拦"——verifier 产出后、gate 拦截前，中间的往返就是 65 分钟摩擦的来源。

### 方案

新增 `scripts/check-p6-format.sh --fix`（pre-gate 规范化器）：

**自动归一化的范围（只碰无歧义形状，绝不触语义）**：

| 归一化项 | 示例 | 性质 | 歧义性 |
|---------|------|------|--------|
| PASS/FAIL 行首大小写 | `pass B01` → `- PASS B01` | 形状 | 无歧义 |
| 行首空白标准化 | `  - PASS` → `- PASS` | 形状 | 无歧义 |

**不做 auto-fix 的范围（有歧义或触语义，留给 gate）**：

| 不碰项 | 理由 |
|--------|------|
| 裸路径补括号（`b01.png` → `(b01.png)`） | 需判断"这个 token 是证据路径"——描述文本里也可能出现文件名，"哪个 token 是路径"是语义判断 |
| 裸 vision 引用补括号 | 同上 |
| 凭空补出缺失的证据引用 | 需判断"该引用哪个文件"，是语义判断 |
| 补上缺失的 PASS/FAIL 行 | 需判断"该跑哪个 BDD"，是语义判断 |
| 修改 PASS/FAIL 判定 | 需判断"结果对不对"，是语义判断 |
| 补上缺失的 vision YAML 引用 | 需判断"该引用哪个 YAML"，是语义判断 |

裸路径缺括号的情况由 gate 的 provenance 审计 1a 检查（引用格式不对 → exit 1 或 WARNING），不由 auto-fix 猜着包。

### 执行位置

verifier subagent 返回后、主 Agent 运行 gate 前，主 Agent 调：

```bash
bash $AGATE_ROOT/scripts/check-p6-format.sh --fix "$TASK_DIR/P6-acceptance.md"
```

### 效果

- 排版摩擦大幅下降（行首大小写/空白等无歧义形状偏差在 verifier 产出后自动修复，无往返）
- 伪造防御：零增量（provenance 审计能力不变，1a 仍只验存在性不验内容——这是已知局限，非本方案引入）
- 四道 provenance 审计**全部保留 exit 1**（门牙不动）
- 只有真问题（证据文件真不存在、真漏跑场景、真有 blocker、引用真缺失）才 exit 1——这些本就该阻塞
- ① 的价值在排版维度：排版摩擦降 + 防御零削弱。在安全维度：防御零增量。两个维度独立，不可混称

### 边界

`--fix` 覆盖不到的边角格式摩擦仍可能存在。对**那一小部分**单独评估降级——但先自动化、后降级，而非一刀切降级。

### bats 测试

- `unit/check-p6-format.bats`：
  - `--fix` 模式：行首大小写和空白偏差自动修正，exit 0
  - `--check` 模式（默认）：上述偏差 exit 1 + 输出差异描述
  - 裸路径缺括号：**不修复**（语义判断），由 gate provenance 审计 1a 处理
  - 语义内容（PASS/FAIL 判定、证据引用指向）不被 `--fix` 改动
  - 无 P6-acceptance.md 时 exit 0（不阻塞非 P6 阶段）

---

## ② 给 PAUSED 出口贴对标签

### 问题

PAUSED 出口本就存在（state-machine.md），但被当成"认输"而非"正确"。agent 倾向于凿墙（造假过关）而不愿走一扇挂着"失败者走这里"牌子的门。

### 方案

**纯协议文本改动**，零脚本成本。在以下文件中翻转 PAUSED 的语义定义：

### 修改清单

**1. `WORKFLOW.md`** — 在 PAUSED 定义处增加语义声明段落：

> **PAUSED 不是失败，是正确路由。**
>
> agent 的责任是"走对流程"，不是"让 gate 变绿"。派了真 subagent、跑了真验证、gate 仍不过——这不是你的失败，红灯是工作/设计的问题，不是你没本事顶过去。伪造证据让它变绿，才是唯一的失败。
>
> 走正规途径仍不过 → PAUSED/问人类 = 正确行为、零追责
> 伪造证据过关 = 唯一失败
>
> ⚠️ 这是 L0 指导（协议文本语义翻转），非 L3 硬拦截。效果取决于语义翻转对 LLM 行为的实际影响，需实证验证。但它零脚本成本，且与 ①③ 协同——当 honest path 被疏通（①）且红灯正确路由（③）时，PAUSED 的语义翻转才有物质基础。

**2. `state-machine.md`** — 在每个 `→ PAUSED` 转移规则旁加注释：

现有格式如：
```
P6 --[retry>=MAX]--> PAUSED
```

改为：
```
P6 --[retry>=MAX]--> PAUSED（正确路由：上游问题需人工介入，非 agent 失败）
```

对全部 PAUSED 转移统一加注（P1/P2/P3/P4/P5/P6/P7 的 retry 超限 + NEED_CONFIRM + PROD_TOUCHED）。

**3. `dispatch-protocol.md`** — 在主 Agent 行为规范中增加：

> **红灯处理优先级**：
> 1. 诊断：本步抖动还是上游输入问题？
> 2. 本步抖动 → 重试一次（仅一次，避免在被污染的输入上打转）
> 3. 上游问题 → 退回源头那一步（见 ③ 逐步溯源）
> 4. 退到 P0 仍无解 / 外部阻塞 → PAUSED 问人类（正确路由，非认输）

**4. `phase-cards/` 各阶段卡片** — 在"gate 不通过"处理段增加：

> gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

### bats 测试

无新增脚本态，无需新增 bats。但 `check-protocol-consistency.py` 的 CHECK 9 锚点表需更新：新增关键词 `PAUSED 不是失败` / `正确路由` / `责任绑流程不绑绿灯` 在 WORKFLOW.md / dispatch-protocol.md 中存在。

---

## ④ P6 证据由 CI 执行生成、agent 只引用

### 问题

当前 P6 证据由 agent 自己提交（写 P6-evidence/ 文件）。producer=judge=editor 同体时，agent 可以伪造证据。provenance 审计只查"在不在/被没被引用"，不查真伪。

### 方案

**长期目标**：P6 证据由 CI 从真实代码跑出，agent 只能引用 CI 产出物，不能自带。它没法"改证据"，因为证据不是它写的。

### 可行性分层

| 证据类型 | CI 生成可行性 | 方案 |
|---------|-------------|------|
| 测试类（pytest/bats 结果） | ✅ 天然可行 | CI 跑测试 → 产出结果文件 → agent 在 P6-acceptance.md 引用 CI 产出路径 |
| UI 类（截图 + vision YAML） | ⚠️ 依赖项目有 e2e/截图流水线 | 有流水线 → 同上；无流水线 → 退化为"尽量锚 + 明标残余风险" |

**agate 栈无关，不能假设 CI 有 e2e 流水线**。所以 ④ 对测试类证据是强解，对 UI 类证据是条件解。

### 落地路径

1. **短期（本方案）**：在 `verifier.md` 和 `dispatch-protocol.md` 中增加可操作指令——P6 派发 verifier 时，若项目有 CI 流水线，优先要求 verifier 引用 CI 产出（如 pytest 结果路径）而非自带证据文件。⚠️ **安全收益为零**（不改变任何可执行检查——provenance 1a 只验引用存在性不验来源，verifier 可引用 CI 路径同时自带伪造文件）。短期价值是语义铺垫（为中期落地建立文档基础），非安全增益
2. **中期**：CI 独立**重新生成证据**（跑测试→产出结果文件），而非重跑 provenance 审计。provenance 重跑同一把不辨真伪的尺子，对伪造无效（见"不做的事"）；真正堵伪造的是"证据由执行生成"——CI 生成新证据，agent 产出若与 CI 不一致则暴露伪造
3. **长期**：P6 证据产出完全由 CI 驱动，agent 只写引用

### bats 测试

短期（L0 指导）无需新增 bats。中期 CI 复核需 `integration/ci-p6-evidence.bats`。

---

## ⑤ Subagent 假完成：主 Agent 文件校验

### 问题

subagent 报告"已修复/已实现"但文件未实际变更（T048 实证）。verifier.md 已有"分阶段落盘"机制但执行率低。

### 方案

两层防护（来自 t048-improvements-phase2 方案 D2，评为"本轮质量最高"但尚未落地）：

**1. subagent 侧**：派发 prompt 末尾加固定校验指令：

```
返回前执行：grep -c '关键改动标记' 文件路径
输出非 0 才返回成功，否则报告"改动未落盘"并重试
```

主 Agent 在 prompt 中指定期望的 grep 模式和文件路径。

**2. 主 Agent 侧（外部可观测，D2）**：在 `dispatch-protocol.md` 主 Agent 行为规范中增加：

> 收到 subagent "已修复/已实现"报告后，必须对声称修改的文件做内容校验（grep 关键行或 diff），未改则重派。不信 subagent 摘要，信磁盘内容。

### 修改清单

- `dispatch-protocol.md`：主 Agent 行为规范增加校验步骤
- `assets/templates/dispatch-prompt.md`：prompt 模板末尾加校验指令段

### bats 测试

- `unit/dispatch-context-warning.bats` 补充：dispatch-prompt.md 含校验指令关键词

---

## ⑥ Gate 正则语义化放宽

### 问题

P2 候选方案正则 `^###?\s*(候选方案|方案\s*[ABC123abc一二三四五])` 对 `方案 <多词名>` 写法不友好（如 `### 方案 Alpha`）。但用 `候选方案` 前缀的写法（如 `### 候选方案 Alpha`）已可匹配——问题仅限 `方案` 前缀+多词名的场景。gate 检查"格式对不对"而非"有没有"。

### 方案

统一原则：**gate 检查"有没有"，不检查"格式对不对"**。格式由 CI lint 管。

### 修改清单

- `check-gate.sh` P2 分支：候选方案正则改为 `^###?\s*(候选方案|方案\s*[A-Za-z一二三四五]|Alternative|Option)`——保留 `^###?\s*` 行首锚点，防止匹配行内任意位置
- 审查其他 gate 正则，凡是"关键词精确匹配"的，改为"语义关键词集合匹配"——均保留行首锚点

### bats 测试

- `unit/check-gate.bats` 补充：`方案 Alpha` / `方案 Recommended` / `Alternative A` 等多词方案名匹配

---

## ⑦ verification_env 条件化（仅 ui_affected）

### 问题

原评审建议 P0-brief 新增 `verification_env` 字段 + P8 发布后 checklist。但给每个任务（含大量非 UI 任务）增加填写负担——UI 任务受益，非 UI 任务纯负担。

### 方案

**`verification_env` 仅当 `ui_affected: true` 时必填**，非 UI 任务可省。

### 修改清单

- `verifier.md`：P6 验收环境规范段增加——"若 P0-brief 声明 ui_affected=true，verification_env 字段必填（列出验收环境与生产环境的已知差异）"
- `assets/templates/p0-brief-template.md`：`verification_env` 字段标注 `(ui_affected=true 时必填)`
- P8-release.md 模板：READY checklist 增加发布后验证项（版本 bump 后重跑 P5 gate + UI 任务截图验证），标注 `(ui_affected=true 时适用)`

### bats 测试

无需新增。这是 L0 指导层改动。

---

## 实施顺序

按**可独立 landable 的单元**拆分，每个单元独立评审 + bats + self-gate + 走 PR（分支保护已启用）。任何一个单元有隐藏缺陷可独立回滚，不牵连其余。

```
U1（结构对称）：
  ⑧ P1 需求评审                    ← 新角色 + gate 更新 + bats（不可裁，无 trivial 分支）
  ⑩ do→review 迭代循环              ← 纯文本改动（⑧ 的必要补充）
  N3 ⑧ review 实质锚点              ← requirements-review 引用 BDD 编号

U2（编排哲学）— 单独 PR，风险最高：
  ⑨ P5/P7/P8 subagent 化           ← 阶段卡片 + 新角色 + gate 更新
  N3 ⑨ review 实质锚点              ← consistency-reviewer 引用 DESIGN_GAP 配对
  N5 P5 commit→push 窗口残余风险标注

U3（上下文机制）：
  ⑪ dispatch-context 扩展           ← 协议文本 + 模板更新
  ⑫ gate 诊断落盘                   ← 纯文本改动（③ 的操作化）
  N2 诊断格式禁令                    ← 禁 - PASS/FAIL 行首 + 审计2 适配规格

U4（激励层，先疏）：
  ① check-p6-format.sh --fix       ← 新脚本 + bats
  ② PAUSED 语义翻转                 ← 纯文本改动 + consistency 锚点更新
  ③ 回退机制修正                    ← 纯文本改动

U5（结构+卫生）：
  ④ 证据由 CI 生成原则声明          ← 纯文本改动（L0）
  ⑤ subagent 假完成校验             ← dispatch-protocol.md + dispatch-prompt.md
  ⑥ gate 正则语义化                 ← check-gate.sh + bats
  ⑦ verification_env 条件化         ← 纯文本改动
```

**每个 U 落地后**：跑全套 bats + `check-protocol-consistency.py` + `shellcheck` + self-gate 检查清单 + 走 PR。

**U 内部依赖**：
- U1：⑩ 依赖 ⑧（迭代循环是评审的必要补充），N3 依赖 ⑧（锚点校验挂 P1 review）
- U2：⑨ 内部 P5/P7/P8 无先后依赖，可同 PR；N3/N5 依赖 ⑨
- U3：⑫ 依赖 ⑪（诊断落盘依赖 dispatch-context 冻结约束），N2 依赖 ⑪⑫
- U4：①②③ 无先后依赖，但 ②③ 的物质基础依赖 ①（先疏后堵）
- U5：④⑤⑥⑦ 无先后依赖

**U 间依赖**：
- U2 依赖 U1 的 ⑩（subagent 化后需要迭代循环定义 review 不通过时的行为）——但 U2 可先落地 P5/P8（无 review），P7 的 consistency-reviewer 迭代等 U1 的 ⑩
- U3 的 ⑫ 依赖 U4 的 ③（诊断落盘是回退机制的操作化）——但 ⑫ 可先落地格式和文件结构，③ 的回退逻辑补在后
- 实际落地顺序：U1 → U2 → U3 → U4 → U5（U2 等 U1 是最紧的依赖）

---

## 不做的事

| 不做 | 理由 |
|------|------|
| provenance 审计降级 WARNING | 削弱局限 3 防御换摩擦缓解，交易方向错（R1）。用自动格式化替代 |
| P6-acceptance.md 加 agent=main 硬拦截 | 投入产出比不如制度设计（R3） |
| CI 重跑同一套 provenance | 重跑同一把不辨真伪的尺子，对伪造无效（R8.3） |
| provenance 1a 从存在性升级为内容校验 | 需 CI 基础设施支持（CI 生成带 hash 的证据清单 + 1a 比对 hash），超出 agate 栈无关协议范围——留为长期目标，与 ④ 长期合并 |
| verification_env 无条件进全局 | 给非 UI 任务加填写负担（R7） |
| 主 Agent 亲自跑 P5/P7/P8 | 有 gate 后全部可 subagent 化，主 Agent 只做 P0+READY |
| dispatch-context.md 包含 PASS/FAIL 预判 | provenance 审计 2 会拦截 |
| dispatch-context.md 派发后追加内容 | 破坏 provenance 审计基准，诊断信息写入单独文件 |
| 主 Agent 读产出文件全文写 prompt | 违反铁律 2，上下文爆炸 |
| P7 拆分多次派发 | 一致性检查天然需要跨文件对照，拆分丧失交叉检查能力 |

---

## 与已有方案的关系

| 已有方案 | 本方案关系 |
|---------|-----------|
| p6-gate-institutional-design v3（①-⑦） | ①②④⑤⑥⑦ 完整内联；③ 按本轮讨论修正（诊断→跳转→PAUSED→修→重跑） |
| t048-improvements-phase2（G/B/D/E2/E3） | D（假完成防护）→ 本方案 ⑤；E2（agent=main）→ 不做（R3）；G/B → 已实施 |
| agate-protocol-review-t048-t052（F1-F10） | F1 降级 → 不做，改 ① 自动格式化；F2 agent 字段 → 不做，改 ①②③ 制度设计；F3-F8 → 本方案 ⑤⑥⑦ |
| review-20260711-1921（R1-R8） | ①-⑦ 是 R8 落地清单的实现 |
| 本轮讨论 Q1-Q5 | ⑧⑨⑩⑪⑫ 是 Q1-Q5 的方案化 |

---

## self-gate 同步更新计划

本方案改动 agate 协议本体，必须同步更新 self-gate 机制。以下是每个 Phase 对应的 self-gate 更新项，**不直接实施，待对应 Phase 落地时同步执行**。

### CHECK 9 锚点表更新

`check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 需新增：

| Phase | 新增锚点 | 对应部件 |
|-------|---------|---------|
| Phase 0 | `P1 review agent≠main 检查` → `check-gate.sh` → `["P1", "agent=main"]` | ⑧ |
| Phase 0 | `P7 consistency-reviewer 存在` → `check-gate.sh` → `["consistency-reviewer"]` 或 `["P7"]` | ⑨ |
| Phase 0 | `dispatch-context 任务上下文节` → `check-p6-provenance.sh` → `["任务上下文"]` | ⑪ |
| Phase 1 | `P6 格式自动修复` → `check-p6-format.sh`（新脚本）→ `["--fix"]` | ① |
| Phase 1 | `PAUSED 正确路由` → `state-machine.md`（文档锚点，非脚本）→ 需 CHECK 9 扩展或新 CHECK | ② |
| Phase 1 | `gate-diagnosis 落盘` → `dispatch-protocol.md`（文档锚点）| ⑫ |

**难点**：CHECK 9 当前只检查"脚本关键词存在性"，不检查"文档关键词存在性"。② 的 `PAUSED 不是失败` / `正确路由` 和 ⑫ 的 `gate-diagnosis` 是文档层面的声明，没有对应脚本关键词。两种处理方式：
- A：扩展 CHECK 9 支持文档锚点（检查协议文档是否含特定关键词）——增加检查维度
- B：仅依赖 Layer 1 LLM 语义审查——不扩展 CHECK 9，但 ②③⑫ 的文档声明无结构兜底

**建议选 A**：在 CHECK 9 增加 `DOC_ALIGNMENT_ANCHORS` 表，检查协议文档是否含关键词。这与现有 `SCRIPT_ALIGNMENT_ANCHORS` 对称——脚本锚点检查"脚本实现了文档声明的规则"，文档锚点检查"文档包含了协议要求的声明"。

**DOC_ALIGNMENT_ANCHORS 设计**：

```python
DOC_ALIGNMENT_ANCHORS = [
    {
        "desc": "PAUSED 正确路由语义",
        "doc": "agate/state-machine.md",
        "keywords": ["正确路由"],
    },
    {
        "desc": "PAUSED 不是失败声明",
        "doc": "agate/WORKFLOW.md",
        "keywords": ["PAUSED 不是失败"],
    },
    {
        "desc": "红灯处理优先级",
        "doc": "agate/dispatch-protocol.md",
        "keywords": ["红灯处理优先级"],
    },
    {
        "desc": "dispatch-context 任务上下文节",
        "doc": "agate/dispatch-protocol.md",
        "keywords": ["任务上下文"],
    },
    {
        "desc": "gate 诊断落盘",
        "doc": "agate/dispatch-protocol.md",
        "keywords": ["gate-diagnosis"],
    },
    {
        "desc": "do→review 迭代循环",
        "doc": "agate/dispatch-protocol.md",
        "keywords": ["迭代循环"],
    },
]
```

检查逻辑与 `SCRIPT_ALIGNMENT_ANCHORS` 对称：遍历锚点表 → 读文档 → 检查关键词是否存在 → 缺失则 WARNING（不 ERROR——文档措辞可能变化，关键词存在性是弱信号）。

### SELF-GATE.md 触发文件更新

当前触发文件正则：
```
^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$
```

本方案新增的触发文件：

| 新增文件 | 是否被现有正则覆盖 |
|---------|------------------|
| `agate/assets/review-roles/requirements-review.md` | ✅ `agate/.+/.*\.md` |
| `agate/assets/execution-roles/consistency-reviewer.md` | ✅ `agate/.+/.*\.md` |
| `agate/scripts/check-p6-format.sh` | ✅ `agate/scripts/.*\.sh` |

**结论**：现有正则已覆盖所有新增文件，无需修改触发条件。

### commit-msg hook 更新

`commit-msg-self-gate.sh` 的正则与 SELF-GATE.md 触发文件相同，已覆盖新增文件。无需修改。

### protocol-alignment-review.md 反向传播表更新

`assets/review-roles/protocol-alignment-review.md` 的 A5 节有"反向传播的常见路径"表。本方案新增的文件和改动需要在此表中增加条目：

| 变更文件 | 应反向传播到 |
|---------|-----------|
| `dispatch-protocol.md`（dispatch-context 扩展） | `check-p6-provenance.sh`（审计 2 适配）、`dispatch-prompt.md`（任务节模板化）、`orchestrator-template.md`（合法职责更新）、`verifier.md`（P5/P6 派发模式） |
| `state-machine.md`（PAUSED 语义、回退机制） | `WORKFLOW.md`（PAUSED 定义）、`phase-cards/` 各阶段（gate 不通过处理）、`check-state-transition.sh`（回退 diff 注释） |
| `check-gate.sh`（P1 review、P7 consistency-reviewer） | `WORKFLOW.md`（阶段总览表）、`dispatch-protocol.md`（门槛表） |
| `phase-cards/P5-verification.md`（subagent 化） | `verifier.md`（P5 模式指令）、`dispatch-protocol.md`（P5 派发流程） |
| `phase-cards/P7-consistency.md`（subagent 化） | `consistency-reviewer.md`（新角色）、`dispatch-protocol.md`（P7 派发流程 + 粒度例外） |
| `phase-cards/P8-release.md`（subagent 化） | `implementer.md`（P8 模式确认）、`dispatch-protocol.md`（P8 派发流程） |

### self-gate 更新时机

| Phase | self-gate 更新项 |
|-------|-----------------|
| Phase 0 | CHECK 9 锚点表：P1 review + P7 consistency-reviewer + dispatch-context 任务上下文；DOC_ALIGNMENT_ANCHORS 表（新增）；protocol-alignment-review.md 反向传播表 |
| Phase 1 | CHECK 9 锚点表：check-p6-format.sh + --fix；DOC_ALIGNMENT_ANCHORS：PAUSED 正确路由 + gate-diagnosis |
| Phase 2 | 无新增 |
| Phase 3 | 无新增 |

**每个 Phase 实施后**：跑 self-gate 检查清单（SELF-GATE.md），确认 CHECK 1-9 无 ERROR + 派发 protocol-alignment-review + 跑全量 bats。

---

## 验证

每个 Phase 完成后跑：

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
bash agate/tests/scripts/count-tests.sh
```

Phase 0 新增：
- `unit/check-gate.bats` 补充 P1 review + P5/P7/P8 subagent 场景
- `assets/review-roles/requirements-review.md` 新文件
- `assets/execution-roles/consistency-reviewer.md` 新文件

Phase 1 新增：
- `unit/check-p6-format.bats`

用例数以 `count-tests.sh` 输出为准。
