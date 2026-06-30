# 子 Agent 派发协议

> agate 核心文件，解决"主 Agent 不派发、自己一路走到底"的问题

---

## 问题诊断

agate 的派发协议把每次阶段推进翻译成**明确的工具调用 + 精确的输入输出规范**，解决「主 Agent 写入上下文」这类不可执行的模糊描述。

---

## 派发的三条铁律

### 铁律 1：用 task 工具派发，动词是"派发"不是"执行"

主 Agent 到了某个阶段，**不自己产出文件**，而是调用 task 工具启动一个 subagent。

```
❌ 错误理解："P2 阶段我要产出 P2-design.md" → 主 Agent 自己写
✅ 正确理解："P2 阶段我要派发一个 architect subagent 去产出 P2-design.md"
```

### 铁律 2：prompt 只传文件路径，不传文件内容

```
❌ 错：把 P1-requirements.md 的全文复制进 subagent 的 prompt
✅ 对：prompt 写"读取 docs/tasks/T001/P1-requirements.md"
```

subagent 在自己独立的上下文里读文件。主 Agent 的上下文永远不碰这些文件的全文。**这是上下文隔离的核心。**

### 铁律 3：subagent 只返回"路径 + 一句话摘要"

```
❌ 错：subagent 把 P2-design.md 全文返回给主 Agent
✅ 对：subagent 返回 "已产出 docs/tasks/T001/P2-design.md，方案采用 schema version 表 + 迁移脚本目录，3 个迁移步骤"
```

主 Agent 只拿摘要做门槛判断，需要细节时让下一个 subagent 自己去读文件。

---

## subagent 返回校验（处理 subagent 自身失败）

subagent 可能崩溃、超时、不产出文件、或不遵守"只返回摘要"。主 Agent 收到返回后必须校验，不能假设 subagent 一定成功。

```
subagent 返回后，主 Agent 校验：
  1. 约定的产出文件是否真的存在？
      不存在 → 派发失败，计入重试，带"未产出文件"原因重派
  2. 返回是否是"路径+摘要"格式？
      返回了文件全文 → 直接判失败重试，要求 subagent 重新只返回摘要
  3. 产出文件是否含合法 Header（phase/task_id/parent/trace_id）？
      没有或不完整 → 门槛不通过，计入重试
  4. 产出文件内容是否非空且有实质内容？
      空文件或半截内容（写一半崩了）→ 视为失败，重试
  5. 独立验证 subagent 的声明：
      主 Agent 必须亲自执行 gate 命令验证门槛，不能仅凭 subagent
      返回的摘要或产出文件中的声明判定通过。
      例：P5 subagent 说 "failed=0" → 主 Agent 跑 pytest -q
          确认 exit 0 且 failed 行确实为 0，才算通过。

任一校验失败 → 计入 `retries[Pn]`，超限则 PAUSED。
```

**关键：主 Agent 永远不信任 subagent 的口头返回，以自己执行的命令结果为准。**

### 主 Agent 跑 gate 时保护自己的上下文

主 Agent 必须亲自跑 gate（上面铁律），但 gate 失败时的完整诊断（traceback/堆栈全文）会涌入主 Agent 自己的上下文，长流程下累积污染。

区分两件事：主 Agent 跑 gate 只为**判断「过没过」**，不为**诊断「为什么失败」**。前者只需紧凑信息（exit code + 通过/失败汇总 + 失败项清单），后者（完整 traceback）是修复 subagent 的事，在它的独立上下文里获取。

因此：
- gate 命令从 P2 的 `gate_commands` 读取，这些命令已被 architect 设为**紧凑输出模式**（`--tb=no` / `--quiet` / `--reporter=dot` / `| tail -N` 等，见 architect 角色定义）
- 主 Agent 直接跑这些紧凑命令，判断信息（汇总行、失败清单）都在,完整 traceback 不进上下文
- 若 gate 失败且需要把完整诊断传给修复阶段：派 gate-runner subagent 在独立上下文跑**完整模式**命令、把完整输出落盘到文件，主 Agent 读紧凑结论判断，修复 subagent 读落盘文件——完整 traceback 始终不碰主 Agent 上下文

**不要**先跑完整命令再想办法截取——命令一执行，完整输出已进上下文，事后无法挽回。截断必须在命令层（紧凑模式参数或 shell 管道），让爆炸的输出从一开始就不产生。

### 空返回的恢复策略

subagent 空返回（约定产出文件不存在）是特殊失败模式，不能简单重试相同 prompt。

**分阶段落盘已默认启用**（见派发 prompt 模板），每次派发都带落盘指令。空返回仍可能发生（任务结构问题超出落盘缓解范围），此时：

1. 第 1 次空返回：
   - 计入 `retries[Pn]`（现成规则），记录 `failure_mode: empty_return, prompt_changed: false, adjustment: null`
   - 分析失败原因：prompt 是否过复杂？输入文件是否过多？任务粒度是否过大？
   - 调整策略后重派：
      a. 拆分任务（见「任务粒度指引」）
      b. 补输入导航（见「输入导航原则」）
      c. 换 subagent 类型（frontend ↔ general）
   - 更新本次 retry 记录：`prompt_changed: true, adjustment: <具体调整>`

2. 第 2 次空返回（调整策略后仍失败）：
   - 计入 `retries[Pn]`
   - `len(retries[Pn]) > MAX_RETRY` → PAUSED 报告人工

**禁止**：不调整策略、相同 prompt 直接重试（`retries` 记录里 `prompt_changed=false` 且非首次）。
空返回说明 subagent 扛不住当前任务形态，原样重试大概率还是空返回。

**空返回诊断的间接缓解**（当前平台不支持 subagent 活动检测，无法直接判断"subagent 是否在干活"，见 LIMITATIONS.md 局限 4）：
1. 主 Agent 记录派发耗时作为参考（弱信号，不作主要判据——耗时不能区分"卡死"和"在干活但慢"）
2. 空返回后检查中间产物文件（P{N}-progress.md 是否有内容 → 判断 subagent 是否动过；有 progress 内容说明落盘生效但最终产出未完成，问题在产出阶段；无 progress 内容说明 subagent 早期就放弃了）
3. 从任务本身分析（输入是否过多、产出文件数是否超过 3——见「任务粒度指引」）

**空返回的最可能根因**（验证实测）：不是上下文窗口被输入占满，而是**任务结构导致认知过载**——subagent 读完所有输入后面对"从零开始写一篇大报告"的推理复杂度过高，模型在单次推理中放弃。`steps` 上限无法缓解（已验证 steps:15/30 均无效）。有效的是**分阶段落盘**（见派发 prompt 模板的落盘指令）——把"一次性大产出"拆成"逐步小产出"，每步认知闭合，降低单次推理复杂度。因此分阶段落盘已作为默认指令写入每次派发 prompt，不再作为空返回后的补救措施。

—— T016 教训：P3 subagent 连续 3 次空返回，主 Agent 既没记 retry 也没调整策略，直接降级亲自写。如果有 `prompt_changed` 字段，事后一眼就能看出"3 次重试 prompt_changed 全是 false"——违规一目了然。
—— T020 教训：空返回后不需要精确诊断"为什么"也能正确应对——走 retry→PAUSED，不降级。诊断是优化，不降级是底线。

---

## 执行模式：有 task 工具 vs 单 Agent

agate 的标准模式假设主 Agent 有 `task` 工具。若 `executor_env.has_task_tool: false`（如 Claude Project 会话），整个派发机制降级为**单 Agent 顺序执行模式**：

| 标准模式（has_task_tool: true）| 单 Agent 模式（has_task_tool: false）|
|-------------------------------|--------------------------------------|
| 主 Agent 派发 subagent，自己不写产出 | 主 Agent 直接执行每个阶段，自己写产出 |
| 每阶段独立上下文，角色专注 | 所有阶段同一上下文，无上下文隔离 |
| TDD：P3/P4 由不同 subagent 执行 | TDD：P3/P4 同一 Agent 执行，独立视角消失 |
| gate：主 Agent 亲自跑命令 | gate：同上，但本地环境也可能缺失 |

**单 Agent 模式的附加要求：**
- P1 裁剪说明里声明 `single_agent_mode: true`
- P3 写测试时必须在 P4 实现之前完成，模拟 TDD 的「契约先行」
- P6 不能以「代码审查」替代实际运行 BDD——若无法跑，走 HANDOVER 交接
- 强烈建议：P0-P2 在单 Agent 完成后，将结果 push 到 main，再切换有 task 工具的平台执行 P3-P8

---

## 降级规则（硬边界）

降级（主 Agent 亲自执行阶段产出）只在以下情况发生：
- `has_task_tool: false`（环境不支持 subagent）
- `has_local_runtime: false` 且阶段需要本地运行（gate 无法执行）

**subagent 执行失败 ≠ 降级信号。** subagent 失败时：
1. 计入 `retries[Pn]`（现成规则）
2. 调整策略重派（拆分任务 / 补导航 / 换 subagent 类型）
3. retry 超限 → PAUSED（state-machine 现成规则）

**主 Agent 不得以"subagent 做不好"为由跳过 retry/PAUSED 直接降级。**

—— T016 教训：P3 subagent 3 次空返回后，主 Agent 自行决定降级亲自写代码。协议没有明确说"subagent 失败时不能降级"，主 Agent 把"协议没说不行"当成了"可以"。本节把降级的合法条件写死，降级不再是一个可选项。

---

## 标准派发流程（每个阶段）

```
主 Agent 执行：

0. 任务启动（仅首次，任务刚收到时）

   主 Agent 首先必须写 P0-brief.md，然后再派发任何 subagent。
   这是主 Agent 作为 PM 的判断输出，P1 analyst 以此为输入做需求质疑和 BDD。

   P0-brief.md 结构（主 Agent 亲自填写）：
   ```yaml
   task: {一句话描述这个任务是什么}
      # 若一句话无法概括，考虑拆分为多个任务——见「任务粒度指引」
   known_risks:
     - {已知风险1，如：涉及 schema 变更}
     - {已知风险2，如：跨越 N 个改动端}
   executor_env:
     platform: {opencode | claude-code | codex | claude-project}
     has_task_tool: true       # false = 单 Agent 模式
     has_local_runtime: true   # false = gate 命令无法执行，需交接有本地环境的平台
     network: {full | restricted}
   env_constraints:
     debug_env: {项目的测试/调试环境路径/命令，从项目约定读取}
     # 不写 prod_env：生产环境不在 agate 开发流程范围内
   pruning_tendency: {保守/激进 + 一句话理由}
   phase_hint: [P1, P2, ..., P8]  # 主 Agent 预判，P1 analyst 可调整，但须经主 Agent 确认
   ```

   P0-brief 完成后，主 Agent 自查五个必填字段是否有实质内容：
   - task：是否是工程视角的一句话描述。若写不出一句话 → 任务太大，拆分
   - known_risks：至少列出一条，没有风险也要写「无已知风险」而不是留空
   - executor_env：platform/has_task_tool/has_local_runtime/network 四项都要填实际值，不是占位符
   - env_constraints.debug_env：是否从项目约定（CLAUDE.md）读取了具体路径/命令
   - pruning_tendency：是否有明确的「保守/激进 + 理由」，不是占位符
   任一字段为空占位符状态 → 补完再继续。

   P0-brief 完成后，第一步输出只允许两种内容之一：
   a) 派发 P1 analyst（传入 P0-brief.md 路径作为主要输入）
   b) 判断为微/小任务并声明「直接执行」的理由

   任何其他输出（分析方案、直接改代码）视为违规。

   —— T005/T006 教训：主 Agent 把「提炼问题定义」也委托给了 subagent，
      P1 analyst 拿到的是用户原始需求文档，缺少主 Agent 对环境约束、风险、裁剪倾向的判断注入。
      P0-brief 是主 Agent 作为 PM 的思考文件，不可省略。

   ### P0 / P1 职责边界

   P0 是"决策记忆"（PM 视角），P1 是"需求基线"（analyst 视角）。
   P1 读 P0 作为输入，遵循三层处理：
   - **引用**：P0 已有的决策内容（user_decisions / 协调依赖等），P1 直接引用，不重写
   - **形式化**：P0 的验收基线，P1 转化为 BDD Given/When/Then 格式（仅改格式，不改内容）
   - **补全**：P0 没覆盖的隐含需求、待确认清单、能力需求，由 P1 独立产出

1. 读状态
   读 docs/tasks/active-tasks.md → 确认当前任务和阶段
   读 docs/tasks/Txxx/ → 确认上一阶段产出文件存在

2. 选角色
   按阶段从 assets/execution-roles/ 选执行角色
   （P1→analyst, P2→architect, P3→test-designer, P4→implementer, P5→verifier）

3. 派发 subagent（task 工具）
   传入：
     - 角色定义文件路径（assets/execution-roles/xxx.md）
     - 输入文件路径（上一阶段产出，不传内容）
     - 输出要求（产出哪个文件 + Header 规范 + 门槛）
     - 返回要求（只返回路径 + 摘要）

4. 接收返回
   只读 subagent 的摘要，不读产出文件全文

5. 门槛检查
   读产出文件的 Header / 关键字段，判断门槛是否通过
   （可判定条件，见下）

6. 更新状态
   更新 active-tasks.md 的阶段和状态
   门槛通过 → 进入下一阶段（回到步骤 1）
    门槛失败 → 重试（retries 记录 +1，超限则停下报告）
```

---

## 输入导航原则

铁律 2"只传路径不传内容"防止的是上下文污染，不是禁止主 Agent 给方向。主 Agent 派发 subagent 前，给 subagent 提供"读哪个节、关注什么"的导航。

**导航 ≠ 提炼 ≠ 读全文：**
- 导航：prompt 里注明"读 P1-requirements.md 的 BDD 验收条件节"
- 提炼（禁止）：主 Agent 读完文件把内容总结进 prompt
- 读全文（禁止）：把文件内容复制进 prompt

**导航的信息来源是协议知识，不是文件内容：**
- 每个阶段产出文件的节结构由对应角色定义文件硬约束（analyst.md 定义 P1 的节、architect.md 定义 P2 的字段）。角色定义文件不在主 Agent 的 8 文件启动读取列表里——主 Agent 不需要读它们，导航用的节名称在下方已内联
- P1 的节名称（来自 analyst.md）：需求复述 / 隐含需求识别 / BDD 验收条件 / 待确认清单 / 裁剪说明 / 范围声明 / 能力需求声明
- P2 的字段（来自 architect.md）：packages / domains / ui_affected / gate_commands / env_constraints / files_to_read / minimal_validation（后两个控制 P4 implementer 上下文 + 方案可行性验证）
- 主 Agent 用这些协议定义的节名称给导航，不需要读产出文件的实际内容
- 节名称是协议固定的，章节号是 subagent 自己编的——导航用节名称，不用章节号

**主 Agent 的核心职责是任务分解 + 输入导航 + 验证**，不是传话筒（把文件路径原样转发），也不是消化器（读完所有文件做提炼）。

—— T016 教训：P3 派发时主 Agent 把 7 个文件路径（~1917 行）甩给 subagent，没给任何导航。subagent 要自己理解 BDD + 接口 + 串行队列 + mock + vitest，认知负荷过载导致 3 次空返回。

**残余风险**：如果 subagent 产出时偏离了角色定义的节结构（用了自定义标题），导航会静默失效——subagent 找不到对应节，大概率又是空返回循环。缓解方式：P1/P2 gate 检查时，主 Agent 顺带验证产出文件是否含角色定义要求的节名称，缺失则门槛不通过。

### 客观信息落盘

主 Agent 在派发前通过查证获得的客观信息（环境状态、URL、选择器、接口契约、命令输出等），当信息量较大（超过约 10 行）或需在同阶段多次派发中复用时，应落盘成文件，不写进 prompt。

**为什么这是铁律 2 的补全**：铁律 2"只传路径不传内容"当前只覆盖了阶段产出文件（P1-requirements.md 等），没覆盖主 Agent 自己查证的客观信息。这个缺口从 T016 就存在，T020 第一次被显式提出——主 Agent 把环境状态、URL、选择器全写进 prompt（约 50 行），违反铁律 2 精神且不可复用。

**文件名**：`docs/tasks/{Txxx}/P{N}-dispatch-context.md`

**内容**：主 Agent 已查证确认的客观事实：
- 环境状态（服务是否运行、版本、数据是否就绪）
- 关键路径/标识（正确的 URL、API 端点、文件 ID 等）
- 接口/结构清单（DOM 选择器、API 字段、配置项等，从源码提取）
- 参照文件路径（现有同类测试、可套用的模式）
- 运行方式（如何执行脚本、必要的环境变量）

派发时 prompt 只给这个文件路径，不写具体内容。这个文件由主 Agent 在派发前查证后写（主 Agent 的合法职责，类似 P0-brief）。

**判断标准**：信息量 > 10 行 → 落盘；同阶段多次派发复用 → 落盘；信息量小且单次使用 → 可写进 prompt。

---

## 派发 prompt 模板

主 Agent 调用 task 工具时，prompt 用这个结构（完整模板见 `assets/templates/dispatch-prompt.md`，以下为内联版）：

```
你是 {阶段} 阶段的 {角色名} 子 Agent。

## 你的角色定义
读取并遵循：{agate_root}/assets/execution-roles/{role}.md

## 项目约定（必读）
- {project_conventions_file}（项目约定、命名规范、目录结构）
- docs/tasks/{Txxx}/P0-brief.md（本任务的环境约束和风险声明）

## 环境隔离（强制，所有阶段适用）
本任务的环境约束见 P0-brief.md 的 env_constraints 字段。
- 调试/验证必须使用 P0-brief 的 debug_env 声明的测试环境，严禁直接操作生产环境
- 开发全程不应接触生产环境；若意外接触，立即停止并标注 [PROD_TOUCHED] 报告主 Agent

## 输入（自己读取，不要等我提供内容）
- docs/tasks/{Txxx}/P0-brief.md（主 Agent 的任务简报和风险声明）
- docs/tasks/{Txxx}/{上一阶段产出文件}
- {agate_root}/WORKFLOW.md（流程规范）
- docs/tasks/{Txxx}/P{N}-dispatch-context.md（若存在：主 Agent 已查证的客观信息，如环境状态、URL、选择器等）

## 任务
{这个阶段要做什么，一两句话}

## 分阶段落盘（重要，默认启用）
每读完一个输入文件或完成一个关键步骤，立即把发现追加写入 docs/tasks/{Txxx}/P{N}-progress.md（bash 追加模式）。这样即使你最终无法产出完整报告，progress 文件也能让主 Agent 知道你做了什么。不要等所有文件读完再一次性写——逐条写。

## 输出
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}
必须包含 Header（完整字段见 task-files.md「通用 Header」）：
  phase: {Pn}
  task_id: {完整 task_id，如 T002-fix-db-migration}
  type: {problems|design|review|test-cases|implementation|test-results|acceptance|consistency|release}
  parent: {上一阶段文件名}
  trace_id: {Txxx}-{Pn}-{日期}
  status: draft
  created: {日期}

## 门槛（什么算完成）
{可判定的完成条件}

## 返回给我
只返回两行：
  1. 产出文件路径
  2. 一句话摘要（不超过 30 字）
不要返回文件全文。
```

### 阶段特定提示（按需追加到 prompt 末尾）

**P2 派发时追加**：
```
## P2 最小验证（若方案依赖浏览器行为/安全模型/外部系统行为）
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。纯代码逻辑不需要最小验证。
```

**P4 派发时追加**：
```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。
## 写跑分离
若需写验证脚本（Playwright/测试脚本等），只写脚本不跑——主 Agent 会跑脚本验证。
```

**P5/P6 派发时追加**：
```
## 截图质量标准
操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图但须有断言记录文件（response.json / assert.log 等，hook 强制）。
## P6 BDD 二值规则
每条 BDD 结果只允许 PASS 或 FAIL，不允许"调整/跳过/覆盖"等中间态。任何 BDD 标 FAIL → gate 不通过。
## P6 BDD 结果格式
每条 BDD 验收结果必须用行首 `- PASS` 或 `- FAIL` 格式，便于 gate 命令 `grep -cE '^\s*- (PASS|FAIL)'` 可靠匹配。
不要用表格格式（`| B01 | ... | PASS |`），不要用 ✅/❌ emoji，不要用其他格式。
示例：
- PASS B01: 用户可以创建分享链接
- FAIL B02: 过期链接返回 410
## P6 BDD 覆盖完整性
P6 验收必须全量对照 P1 的 BDD 条数（含 SCOPE+ 增补），不能挑验。
P1 有 N 条 BDD → P6 必须有 N 条验收结果（PASS 或 FAIL）。挑验 = gate 不通过。
## P6 证据要求
每条 BDD 验收结果必须有对应证据文件，存入 docs/tasks/{Txxx}/P6-evidence/。
证据类型：
- test-output.log — 验证脚本执行日志（所有任务通用）
- screenshots/ — Playwright 截图（仅 UI 任务）
- traces/ — Playwright trace（仅 UI 任务，可选）
无证据的 PASS 标记 = gate 不通过。
## P6 verifier 脚本执行
P6 verifier 交付的验证脚本（Playwright / shell / pytest）应由主 Agent 执行。
执行输出落盘到 P6-evidence/test-output.log。
若主 Agent 需要自写脚本（如 verifier 脚本不兼容当前环境），自写脚本的执行输出也落盘到 P6-evidence/test-output.log。
关键约束：P6-evidence/ 必须有执行产出，不接受空目录。
## 写跑分离
若需写验证脚本，只写脚本不跑——主 Agent 会跑脚本验证。
```

**P8 派发时追加**：
```
## READY 收尾检查
P8 gate 通过后，主 Agent 会执行收尾检查（停止调试服务、清理临时数据、还原开发环境、确认生产无残留）。
你在 P8 产出中应列出：启动了哪些临时服务/进程、创建了哪些临时数据、做了哪些开发安装，供主 Agent 清理。

## 版本 bump 判定
- 公共 API 行为变化 / 破坏性变更 → major
- 加功能 / 内部重构改 API（向后兼容）→ minor
- 修 bug / 不改 API 行为 → patch
- 测试缺陷不应影响版本号决策：测试 hard-code 版本号 → 修测试，不降级版本
- 在 P8-release.md 中显式声明：bump 类型（major/minor/patch）+ 理由
```

**[PROD_TOUCHED] 标记说明**：任何 subagent 若在执行过程中意外接触了生产环境（写入、读取真实数据、触发外部调用），立即在产出文件标注：
```
[PROD_TOUCHED] 接触了生产环境：{描述具体行为}
影响范围：{估计}
是否可逆：{是/否}
```
主 Agent 看到 [PROD_TOUCHED] → 立即暂停流程 → PAUSED → 报告人工处置。

---

## 任务粒度指引

当阶段产出涉及以下特征时，主 Agent 应拆分为多个 subagent 任务：
- 输入文件超过 5 个（主 Agent 应先检查是否都必要，精简输入比拆分任务成本低；确实都必要时再拆分）
- 单次产出超过 3 个文件（超出 subagent 可靠交付范围）

**拆分判据用输出数量，不用行数**——LLM 处理 2000 行同质内容没问题，但单次产出文件过多时遗漏率上升。行数是弱相关变量，产出文件数是强相关变量。

**异构性不再是拆分判据**——T026 实验证实：在 agate dispatch prompt 模板（含分阶段落盘指令）下，subagent 能可靠处理异构产出（文档 + 代码 + 测试在一个 task 里）。T016 失败的根因是当时缺乏分阶段落盘指令导致空返回，不是异构切换本身。

**拆分原则：**
- 每个任务产出 1-3 个文件
- 每个任务的输入文件 ≤ 3 个
- 任务间有依赖时串行，无依赖时并行
- 拆分通过多次 task 调用实现，commit message 记录拆分（如 `wf(Txxx-P3a): 测试用例文档`）
- 状态机不变——仍只看 P3 阶段，gate 仍是该阶段的门槛命令

—— T016 教训（历史）：P3 要求一个 subagent 产出 3 个异构文件时出现空返回。后经 T026 实验证实根因是缺乏分阶段落盘指令，非异构切换本身。当前模板已默认启用分阶段落盘，异构产出不再需要强制拆分。

---

## P5 修复流程

P5 gate 不通过时（测试失败），主 Agent 派修复 subagent 回 P4 修复代码。修复后**必须重跑 P5 gate（全量测试）**，不是只检查修复项。

**T027 教训**：P5 修复 subagent 只修了 datetime 问题，但引入了 4 个回归（原有测试从绿变红）。如果主 Agent 只检查修复项不跑全量，回归会被放行到 P6。

### 修复流程

1. P5 gate 失败 → 主 Agent 记录失败项（哪些测试失败、失败原因）
2. 派修复 subagent（角色：implementer，输入含失败项清单 + 修复历史）
3. 修复 subagent 返回 → 主 Agent **重跑 P5 gate（全量测试）**
4. 全量通过 → P5 gate 通过，推进 P6
5. 全量仍有失败 → 回到步骤 1（修复历史追加本轮失败项，避免重复踩坑）

### 修复策略记忆

每轮修复重派时，prompt 里必须附上**修复历史**：
- 之前修了什么、怎么修的
- 之前试过但失败的策略
- 当前仍失败的项

避免修复 subagent 重复踩同一个坑（T027 第 2 轮修复引入了第 1 轮已解决的 datetime 回归）。

---

## Playwright/长时操作 subagent 派发策略

Task 工具本身无超时参数。subagent 内部脚本挂起会无限阻塞主 Agent。通过**拆分 + 预期耗时**规避，不依赖超时机制。

### 拆分原则

P6 Playwright 验证不派一个大 subagent 跑完整流程，按职责拆成小步骤：

| 子任务 | 预期耗时 | 返回值 |
|--------|---------|--------|
| 加载页面 + 检查 readyState | 30-60s | `{ loaded: true, loadTime: 35 }` |
| 检查 CSP 违规 | 5-10s | `{ violations: 0 }` |
| 检查 WebGL context | 5-10s | `{ webgl: true, renderer: "D3D11" }` |
| 检查 React/框架渲染 | 10-20s | `{ rootChildren: 3 }` |
| 截图 + vision 分析 | 10-20s | `{ screenshot: "/path.png" }` |

每个子任务：
- 职责单一，耗时可预测
- 返回结构化结果（不是文件全文）
- 有独立 Node 脚本硬超时兜底（见下）

### subagent 超时判定

主 Agent 不主动计时，但 subagent 的 Node 脚本内部必须设硬超时：

```typescript
const HARD = 90_000;  // 或 180_000 for >1MB HTML
let lastStep = 'init';
setTimeout(() => {
  console.error(`HARD TIMEOUT at: ${lastStep}`);
  process.exit(2);
}, HARD);
```

- exit 0 = 成功，exit 2 = 硬超时，exit 1 = 其他错误
- 主 Agent 看到 exit 2 + `lastStep` 信息，知道卡在哪步，可以加长 timeout 重跑该子任务
- 主 Agent 看到 exit 1，看 error message 决定修复策略

### 误杀处理

硬超时触发后，主 Agent 判断：
1. `lastStep` 是 `goto` → 页面加载慢，加大 `page.goto` timeout 重跑
2. `lastStep` 是 `waitForSelector` → 元素没出现，检查页面逻辑（非超时问题）
3. `lastStep` 是 `evaluate` → JS 执行慢或死循环，检查 evaluate 内容

**续跑**：已完成的子任务结果可复用，不从头重跑。如"加载页面"已完成，"检查 CSP"超时，只需重跑 CSP 检查。

### 大文件处理

涉及 >1MB HTML 的 Playwright 操作：
- 主 Agent **不直接 Read** 大文件内容，用 `wc -c` 查大小
- subagent 脚本 `page.goto` timeout 设 60-90s
- 脚本 HARD timeout 设 180s
- 加载后先 `page.evaluate(() => document.readyState)` 确认加载完成，再 `waitForSelector`

—— T019 教训：3.3MB Three.js HTML 的 P6 验证，subagent 内 `waitForSelector('#root > *')` 无 timeout 等待永不出现的元素（因 WebGL 被禁用导致 Three.js 初始化失败），subagent 挂起 → Task 工具无限等待 → 主 Agent 卡死数小时。根因是缺分层超时 + subagent 粒度过大。

### 写脚本与跑脚本分离

反馈循环长的脚本验证任务（浏览器自动化、测试脚本、构建脚本等），不要让一个 subagent 既写又跑又调试——几轮试错后上下文窗口满了导致空返回。

**拆法**：
- 阶段 A：subagent 写脚本（产出脚本文件，不跑）
  - 输入：dispatch-context.md（若存在）+ BDD/验收条件 + 参照文件
  - 产出：脚本文件
  - 用专项 subagent（前端/backend/mcp 对应类型）
- 阶段 B：主 Agent 跑脚本（gate 验证，A1 原则）
  - 跑 subagent A 写的脚本，看 exit code + stdout
  - 最小修复属于"跑命令"的一部分
  - 重大逻辑错误回 subagent A 修
- 阶段 C：subagent 读脚本输出写报告（可选，需格式化时）
  - 输入：脚本输出的结构化结果 + 验收条件原文
  - 只做格式化，不做验证

**最小修复 vs 重写的界限**：
- 改常量值（timeout、selector、URL、超时阈值）= 最小修复，主 Agent 可做
- 改控制流（if/else 结构、循环逻辑、数据处理）= 重写，回 subagent

主 Agent 跑 subagent 写的脚本 = "跑命令"不是"写产出"。
主 Agent 重写脚本逻辑 = 降级，违规。

—— T020 教训：主 Agent 空返回后以"跑脚本是 gate 验证"为由降级亲自写脚本。写脚本不是 gate 验证，是有创造性的工程工作。写跑分离让 subagent 写、主 Agent 跑，各司其职。

### 主 Agent 的"inspect DOM"属于查证职责

主 Agent 可以跑最小 inspect 脚本（如 `page.evaluate(() => document.querySelector('#root').innerHTML.length)`）来查证 DOM 结构——这是查证客观信息（写 dispatch-context.md 的选择器清单），不属于"写脚本"或"降级"。查证产出落盘到 dispatch-context.md，派发时传路径。

区分：
- 主 Agent 跑 inspect 脚本（只查 DOM 结构、不做断言）= 查证职责 ✅
- 主 Agent 写验收脚本（含断言逻辑）= 降级 ❌

### P2 最小验证（方案可行性先验证再全流程推进）

**规则**：P2 方案设计时，如果方案依赖某个**浏览器行为/安全模型/外部系统行为**（非纯代码逻辑），必须在 P2 阶段做最小验证，验证通过后再写 P2 design。

**什么需要最小验证**：
- 浏览器安全模型（CSP 继承规则、sandbox 行为、iframe origin 语义）
- 外部库的核心能力（Three.js 能否初始化、BS4 能否解析目标 HTML）
- 跨系统交互（WSL→Windows 路径、CDP 连接、网络转发）

**怎么做最小验证**：
- 一个 10 行的 HTML 测试页
- 一个 curl 请求验证 API 行为
- 一个 20 行的脚本验证库的核心 API

**不需要最小验证的**：
- 纯代码逻辑（函数输入输出、数据转换）——TDD 单元测试覆盖
- 项目内已有模式（API 路由、Vue 组件）——已有先例

—— T019 教训：srcdoc 方案在 P2 设计、P3 写 57 个测试、P4 完整实现后，到 P6 实跑才发现 srcdoc iframe 继承父 CSP，方案根本不可行。如果 P2 阶段用一个 10 行 HTML 测试页验证 srcdoc 的 CSP 行为，5 分钟就能发现方案不可行，避免 P2-P4 全部返工。

---

## 可判定门槛规范

门槛必须是**主 Agent 亲自跑命令可验证的明确值**，不能是模糊判断或仅依赖 subagent 产出文件字段。

| 阶段 | 门槛 | 怎么判定（主 Agent 亲自执行）|
|------|------|--------------------------|
| P1→P2 | 需求基线建立 | P1-requirements.md 存在 + 有 Header + 含 ≥1 条 BDD 条件（BDD 编号格式不固定，按实际格式 grep）+ `grep -cE '\[NEED_CONFIRM\]' P1-requirements.md → =0` + `grep -cE 'status:.*GAP\b' P1-requirements.md → =0`（仅匹配 status: GAP，不匹配 supplementable）+ `grep -qE 'risk_level:\s*(low|medium|high)' P1-requirements.md → 命中`|
| P2→P3 | 方案已批准 | `grep 'status: approved' P2-review.md` → 命中 + `grep -cE '^(packages\|domains\|ui_affected\|gate_commands):' P2-design.md → =4` |
| P3→P4 | TDD 真红灯 | `scripts/check-tdd-red.sh` exit 0（UI 任务额外确认 Playwright 用例存在）|
| P4→P5 | 实现完成 | P4-implementation/ 下文件非空 + `git log --oneline -1` → 含 "P4" 或 "wf(Txxx-P4)" |
| P5→P6 | 技术验证通过 | 从 P2-design.md `gate_commands.P5` 读取命令执行 → exit 0 AND failed==0 + `grep -rl '\[PROD_TOUCHED\]' {task}/` → 无命中（匹配标记格式）+ 若 ui_affected：从 gate_commands.P5 读取 E2E 命令执行 → exit 0 |
| P6→P7 | BDD 验收通过 ⚠️ self-authored（降级缓解：provenance 审计 + R1a 截图实质检查，根治待 Phase 3） | `scripts/check-gate.sh P6` → exit 2（FAIL=0/NC=0/证据非空已验）+ `scripts/check-p6-evidence.sh` UI 截图 > 1KB（R1a 客观证据 barrier）+ `scripts/check-p6-provenance.sh` → exit 0 或 exit 2（证据-结论对应 + dispatch-context 审计 + BDD 总数对照 + UI vision YAML 审计 [R1b hook 化]）+ 主 Agent 手动核实 `grep -cE '^\s*- (PASS\|FAIL)' P6-acceptance.md` = P1 BDD 总数（provenance exit 2 时必做）（UI 条件须截图 + vision-analyst YAML 引用 + `summary.blocker_count → =0`）。**截图质量标准**：操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图但须有断言记录文件（response.json / assert.log 等，hook 强制）。任何 BDD 标 FAIL → gate 不通过 → 回 P4 |
| P7→P8 | 一致性通过 ⚠️ self-authored | `grep -cE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md → =0` + `grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' P7-consistency.md → =0`（已知限制：定性分析，P5 回归测试兜底）|
| P8→READY | 发布准备完成 | `scripts/check-gate.sh P8` → 脚本化部分通过（exit 2）+ 从 P2-design.md `gate_commands` 逐包读取发布检查命令执行 → 全部 exit 0 + bump-version 后重跑 P5 gate（`gate_commands.P5` exit 0 AND failed==0）+ `git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 条目 → 无遗漏 + 从 P2 `packages` 验证 version 文件路径变更 + `grep -q 'bump_type:' P8-release.md` → 命中 + `git diff HEAD~1 --stat` → 含 version 文件变更 + `git diff HEAD~1 -- ${CHANGELOG_FILE:-CHANGELOG.md}` → 非空（默认 CHANGELOG.md，`CHANGELOG_FILE` 环境变量可覆盖）|

**反例（禁止用作门槛）：**
- ❌ "unit.md 里 failed: 0"（信 subagent 写的数字）
- ❌ "P8-release.md 存在"（文件存在不等于已发布）
- ❌ "P6 里 subagent 写了 ✅"（信 subagent 自我报告，见下方 C7 规则）
- ❌ "UI 代码看起来对"（UI 必须实跑 Playwright，不接受目测）
- ❌ "方案足够好" / "测试差不多了"

**A1 原则**：gate 判定是主 Agent 运行命令得到的客观事实，不是 subagent 文件里的声明。

**Pre-commit 检查全景（hook + CI 兜底）**：

每次 `git commit` 触发 `.git/hooks/pre-commit`（由 `~/.agate/scripts/install-hook.sh` 安装），按顺序执行：

| 阶段/机制 | 检查脚本 | 用途 |
|------|------|------|
| 文件级 P2.15 | `scripts/check-state-yaml.sh` | `.state.yaml` 格式合法（必填字段、phase 取值、retries 结构）|
| 阶段级 P1.1 | `scripts/check-gate.sh` | 各阶段门控规则 |
| 阶段级 P1.7 | `scripts/check-p6-evidence.sh` | P6/P7 阶段：证据目录非空 + BDD 行数 ≥ 1 |
| 阶段级 P2.1/P2.10 | `scripts/check-p6-provenance.sh` | P6 客观行为审计（证据-结论对应 + dispatch-context + BDD 总数）|
| 阶段级 P2.3-P2.5 | `scripts/check-state-transition.sh` | 状态转移合法性 + 重试上限 |
| 阶段级 P2.7-P2.9 | `scripts/check-pruning.sh` | 裁剪条件 + override 校验 |
| 阶段级 P2.11 | `scripts/check-scope-resolved.sh` | `[SCOPE+]` 标记追踪 |
| 提醒级 P2.12 | `scripts/check-retrospective.sh` | 异常模式提醒（不拦截）|
| 提醒级 P1.6 | `scripts/check-changelog.sh` | `[Unreleased]` 含 task_id |

**CI backstop（P1.3）**：`push` 后 GitHub Actions `.github/workflows/protocol-consistency.yml` 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit；并对 `P6-acceptance.md` 单 author 情况发 WARNING 作为兜底审计。

**Gate 分类**：

| 类型 | 阶段 | 判定对象 | 可伪造？ |
|------|------|----------|----------|
| 外部产出 gate | P3, P4, P5 | 外部工具输出（test runner exit code, type checker, git log） | 否 |
| 自写文件 gate ⚠️ | P1, P2, P6, P7 | 主 Agent 写的文件内容 | 是（主 Agent 直接写文件） |

自写文件 gate 的缓解措施：
- P1/P2：gate 条件简单（标记存在性、字段计数），伪造动机低
- P6：证据存在性检查（`P6-evidence/` 非空）+ provenance 客观行为审计 + BDD 总数对照。三层防护：跳过 verifier 拦、伪造 N 个证据的成本极高、单 author WARNING 兜底
- P7：P5 回归测试兜底（一致性标注错误不会导致 bug 漏过）
- C7 规则见下方：所有阶段遵守「subagent 自我报告不可信」

**C7 规则（subagent 自我报告不可信）**：subagent 产出里的"检查结果""✅/通过"等自评，**仅供参考，绝不作为 gate 判定依据**。gate 一律以主 Agent 亲自跑命令的结果为准。T005 教训：P8 subagent 把 `1 failed` 标成 ✅，主 Agent 若信了就放行了缺陷。

**packages 动态注入（B4/B6）**：派发 P8 subagent 时，主 Agent 必须先读 P2-design.md 的 `packages:` 声明，把"需要 bump 哪些包"明确写进 prompt，并据此从 `gate_commands:` 字段生成各包的 gate 命令集。不能用固定的单包命令——不同项目的发布命令不同，必须从 P2 声明读取。

**P5/P6 gate 命令固化（B7）**：P5/P6 的 gate 命令必须从 P2-design.md 的 `gate_commands:` 字段读取，不得在派发 prompt 里自行修改或降级。
- subagent 要求跳过命令 / 换更简单的命令 → `[SCOPE_GAP]`，不通过
- 命令本身跑不通（能力缺口）→ `[CAPABILITY_GAP]` 交人决策，不得自行降级为目测
- T004 教训 B7：P6 子代理连续失败后，主 Agent 要求「不用 Playwright，纯命令行验证」—— 这是主 Agent 降级了 P2 已固化的验收标准，属于违规。

**SCOPE+ / SCOPE_GAP 扫描**：每次 subagent 返回后，主 Agent 扫描产出是否含 `[SCOPE+]`（新隐含需求 → 增补 P1 基线 + 定向回补）或 `[SCOPE_GAP]`（prompt 漏了 P2 已声明的改动 → 修正 prompt 重派）。

**SCOPE+ 处理追踪（P2.11）**：产出含 [SCOPE+] 时，主 Agent 必须在 P1-requirements.md 增补对应条目并标记 [SCOPE_RESOLVED: 来源文件]。未标记 [SCOPE_RESOLVED] 的 [SCOPE+] → gate 不通过（scripts/check-scope-resolved.sh）。

格式：
[SCOPE_RESOLVED: from P4-implementation.md] 新需求已增补为 AC-N，影响范围已评估

---

## 重试与上限

```
门槛失败时：
  retries[Pn].append({
    round: len(retries[Pn]) + 1,
    failure_mode: quality | empty_return | timeout,
    prompt_changed: <bool>,
    adjustment: split_task | add_navigation | switch_type | null
  })
  if len(retries[Pn]) < MAX_RETRY (见 state-machine.md 重试上限表):
      带着失败原因重新派发同阶段 subagent
      （prompt 里加上"上次失败原因：xxx，请修正"）
  else:
      触发 L2 上溯（见 state-machine.md 评审迭代机制）
      上溯后重新开始该阶段
```

重试记录落盘到 `.state.yaml` 的 `retries` 字段（格式见 state-machine.md「每任务独立状态文件」），避免主 Agent 忘记重试了几次、也无法区分"原样重试"和"调整策略后重试"。

---

## Subagent 安全

### 硬超时保护

1. **硬超时**：Task 工具本身无平台层超时参数（T019 实战验证：subagent 内部脚本挂起导致主 Agent 卡死数小时）。防卡死依赖 subagent 内部脚本硬超时（见上方「subagent 超时判定」节）+ 主 Agent 拆分策略，不依赖平台超时
2. **进展标记**：派发 prompt 中要求 subagent 每隔若干关键操作输出进度标记
   `[progress] N/M files processed` 到 stdout，让平台日志可追溯
3. **存活检查**：真正的存活监控（心跳、文件增长检测）需平台原生支持并发后补，当前为已知限制

### 升级机制（[UPGRADE] 标记）

subagent 可在产出文件中标注 `[UPGRADE]` 并附建议：

```
> [UPGRADE] 建议拆分为 Txxx-a / Txxx-b，原因：需求范围过大，单任务不可行
```

主 Agent 看到 `[UPGRADE]` → 停止自动流程 → PAUSED 交人工决策。

### P1 范围把关

P1 完成后可选评审（触发条件见 WORKFLOW.md 阶段总览表 P1 评审角色列）：

派发 `office-hours`（YC 合伙人）评审 P1 产出：
- 问题定义是否准确
- 范围是否合理
- AC 是否可验证

### 不可逆操作保护协议（通用）

**基本原则：开发全程在测试环境进行，生产环境不在 agate 范围内。**

任何阶段，只要涉及以下操作，必须触发 `[NEED_CONFIRM]` 硬中断，等人确认后才可执行：

- **批量数据删除**：即使在测试环境，批量 DELETE / DROP TABLE / 清空也需人工确认范围
- **数据 schema 迁移**：测试环境的迁移逻辑需人工确认后再执行
- **不可逆的外部调用**：发送邮件/通知、扣费、第三方 API 写操作（应在测试环境用 mock）

`[NEED_CONFIRM]` 输出格式（T005/T006 教训）：
```
[NEED_CONFIRM] 不可逆操作待确认

操作类型：{删除/迁移/写入/...}
影响范围：{列出将被影响的数据/文件/资源，尽量具体}
是否已备份：{是（备份路径）/ 否（原因）}
建议操作：{具体要执行的命令或步骤}

请确认执行，或说明调整方案。
```

**严禁在未收到人工确认的情况下执行上述操作。**
备份先于删除——若无法备份，必须在 [NEED_CONFIRM] 中说明原因，等人决策。

### gate 无法执行时的处理路径

gate 命令因**环境限制**无法执行（如无 npm、无 Playwright、网络受限），不能：
- 跳过 gate 直接推进下一阶段
- 以「代码审查」替代实际运行
- 假装 gate 通过

**正确处理方式（三选一，按优先级）：**

1. **补充能力**：安装缺失依赖、切换有本地环境的 Agent 执行
2. **写 HANDOVER.md 交接**：在 `docs/tasks/{Txxx}/HANDOVER.md` 里写明：
   - 当前完成的阶段
   - 待执行的 gate 命令（逐条列出）
   - 接手 Agent 需要的环境（从 P0-brief `executor_env` 读取）
   - 交接后推进的步骤
   标记任务状态为 `[HANDOVER]`，等能执行 gate 的 Agent 接手
3. **标记 `[CAPABILITY_GAP: gate-env]`**：暂停任务，告知人工干预

**严禁**：在 `executor_env.has_local_runtime: false` 的环境里，对需要本地运行的 gate 声称已通过。

---

### [CAPABILITY_GAP] 处理协议

P1 产出的 `capability_requirements` 中，`status: GAP` 的条目触发此协议：

**主 Agent 处理步骤**：
1. 暂停进入 P2，输出 `[CAPABILITY_GAP]` 报告给人：
   ```
   [CAPABILITY_GAP] 任务 {Txxx} 在 P1 检测到能力缺口：
   - need: {能力名称}
   - why: {为什么需要}
   - 当前环境：无可用补充路径
   - 建议选项：
     A) 注入 {skill名称} / 连接 {@agent名称}
     B) 降级验收标准（说明降级后的影响）
     C) 换具备该能力的模型
   ```
2. 等人选择后继续

**三态判断（不要只看主力模型能力）**：
- `available`：Agent 自身 OR 已注入 skill OR 可调用外部 agent → 不触发，流程自走
- `supplementable`：当前没有但有已知补充路径 → 在后续 prompt 中指引获取，不触发
- `GAP`：主力模型 + 环境均无补充路径 → 触发 `[CAPABILITY_GAP]`

**supplementable 能力的传递规则（A3 修复）**：
P1 产出 `capability_requirements` 后，主 Agent 在派发后续阶段时必须：
1. 读 P1-requirements.md 的 `capability_requirements`，提取 `status: supplementable` 的条目
2. 在该阶段的派发 prompt 里注入能力获取指引，例如：
   ```
   ## 能力补充说明
   本任务 P6 验收需要 browser-vision 能力。
   可用方式：派发 vision-analyst（{agate_root}/assets/execution-roles/vision-analyst.md）
   ```
3. 若能力在 P3/P4 阶段就需要（如 Playwright viewport 配置），提前在对应阶段 prompt 里注入
如未注入，subagent 不知道补充方式，supplementable 等效退化为 GAP。

**注意**：`supplementable` 不是 `GAP`。
T004 教训 B8：P6 需要 vision，主力模型没有，但环境里有 playwright-vision skill 可注入。
如果 P1 就识别出这是 `supplementable` 并提示「需要注入 playwright-vision skill」，
就不会跑到 P6 才撞墙，也不会触发 B7（主动要求跳过 Playwright）。

**什么时候 supplementable 升级为 GAP**：
人无法或不愿提供补充路径 → 人主动标记为 GAP → 此时才降级验收标准。
主 Agent 不得自行决定降级。

---

## 平台适配

### OpenCode

用 `task` 工具派发，`subagent_type` 指定角色。

**自定义角色用 markdown 文件方式定义**（放在 OpenCode 的 agent 目录，文件名即角色名）。

⚠️ **已知坑（issue #29616）**：用 `opencode.jsonc` 里 `mode: "subagent"` 定义的自定义 agent 可能无法被 task 工具调起来（subagent_type 枚举硬编码只有 explore/general）。**优先用 markdown 文件方式定义自定义角色**，并在实际环境先做最小验证：定义一个测试角色，让主 Agent 派发它，确认能调起来。

如果自定义角色确实调不起来，退路：用内置的 general subagent，把角色定义文件路径写进派发 prompt 让它读取遵循（角色行为靠 prompt 注入而非平台机制）。

### Claude Code

用 Agent Teams（2026-02 起）或 Task 工具派发。lead agent spawn teammate agent，各自独立上下文，通过消息传递协调。角色定义可以放 `.claude/agents/` 下的 markdown。

### Codex

用 spawn_agent / send_input / wait / close_agent 工具套件。`agents.max_depth` 默认 1（允许直接子 agent，禁止深层嵌套）。自定义 agent 在 `[agents]` 配置。Codex 只在被明确要求时才 spawn subagent，所以派发指令要明确。

---

## 完整派发示例（T001 P2 阶段）

```
主 Agent：

1. 读 active-tasks.md → T001 在 P2 阶段
2. 确认 docs/tasks/T001/P1-requirements.md 存在 ✓
3. 选角色：architect（P2 执行角色）
4. 调用 task 工具：
   subagent_type: architect（或 general + 注入角色文件）
   prompt:
     你是 P2 阶段的 architect 子 Agent。
     角色定义：读取 {agate_root}/assets/execution-roles/architect.md
     项目约定（必读）：CLAUDE.md
     P0-brief（必读）：docs/tasks/T001/P0-brief.md（环境约束和风险声明）
     输入：读取 docs/tasks/T001/P1-requirements.md
     任务：为数据库迁移问题设计方案
     输出：docs/tasks/T001/P2-design.md（含 Header）
     门槛：方案覆盖 P1 列出的所有问题
     返回：只返回文件路径 + 一句话摘要
5. subagent 返回："docs/tasks/T001/P2-design.md，采用 schema_version 表 + 顺序迁移脚本"
6. 派发评审 subagent（plan-eng-review 角色）→ 产出 P2-review.md
7. 读 P2-review.md 的 Header status
   - approved → 更新 active-tasks.md，T001 进入 P3
   - rejected → 重试 architect（retries[P2] 记录第 1 轮），通过文件路径回流评审意见（见下）
```

### 评审打回后的意见回流（重要）

rejected 重试时，architect 必须知道"上次为什么被打回"，否则会产出同样的东西再次被打回，空转到 retry 耗尽。

**评审意见通过文件路径回流（不是主 Agent 读全文塞 prompt）：**

```
rejected 时，主 Agent 的重试派发 prompt 里加一行：
  "上一轮方案被评审打回。评审意见见 docs/tasks/Txxx/P2-review.md，
   请先读取该文件了解被打回的具体原因，再修正方案。"
```

- architect 自己读 P2-review.md（评审意见在文件里，符合"只传路径"原则）
- 主 Agent 不碰评审全文，上下文不被污染
- architect 角色定义的"输入"在重试时额外包含上一轮的 review 文件

这样评审→执行的反馈闭环真正打通，重试不再是空转。

---

## 任务完成小结

**触发时机：P8 gate 通过、状态进入 READY 时。强制输出，不可跳过。**
（T001 教训：主 Agent 完成任务后未向 PM 汇报，PM 需自己翻 git log 才能知道发生了什么）

主 Agent 从各阶段 gate check 的命令输出拼出小结，不读文件全文：

```
[{task_id}] READY — {task_name} {version}

改动：{files_summary from git diff --stat}
验证：{test_results from gate checks}
说明：{one-line design summary}
```

示例：
```
[T001] DONE — 数据库迁移机制修复 v0.1.53

改动：exceptions.py +18 / database.py +51 / cli.py +7 / main.py +2
验证：14/14 migration tests + 486 regression tests
说明：Server 独���迁移，CLI schema 兼容检查
```

---

## PAUSED 报告模板

```markdown
[PAUSED] {task_id} 需用户介入

任务背景：{task_name}
当前阶段：{phase}
失败原因：连续 {len(retries[phase])} 轮 {phase} 评审发现 {issue_summary}

已尝试的解决方案：
  {attempted_solutions}

需要用户决策：
  - [ ] {option_1}
  - [ ] {option_2}
  - [ ] {option_3}

请回复选项或直接说明。
```

---

*派发协议是 agate 解决上下文爆炸的核心，配合 state-machine.md 和 loop-orchestration.md 使用*
