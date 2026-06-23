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

—— T016 教训：P3 subagent 连续 3 次空返回，主 Agent 既没记 retry 也没调整策略，直接降级亲自写。如果有 `prompt_changed` 字段，事后一眼就能看出"3 次重试 prompt_changed 全是 false"——违规一目了然。

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
   known_risks:
     - {已知风险1，如：涉及 schema 变更}
     - {已知风险2，如：跨越 N 个改动端}
   env_constraints:
     debug_env: {项目的测试/调试环境路径/命令，从项目约定读取}
     # 不写 prod_env：生产环境不在 agate 开发流程范围内
   pruning_tendency: {保守/激进 + 一句话理由}
   phase_hint: [P1, P2, ..., P8]  # 主 Agent 预判，P1 analyst 可调整，但须经主 Agent 确认
   ```

   P0-brief 完成后，主 Agent 自查五个必填字段是否有实质内容：
   - task：是否是工程视角的一句话描述（不是产品语言的模糊表述）
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
- 每个阶段产出文件的节结构由对应角色定义文件硬约束（analyst.md 定义 P1 的节、architect.md 定义 P2 的字段）。角色定义文件不在主 Agent 的 7 文件启动读取列表里——主 Agent 不需要读它们，导航用的节名称在下方已内联
- P1 的节名称（来自 analyst.md）：需求复述 / 隐含需求识别 / BDD 验收条件 / 待确认清单 / 裁剪说明 / 范围声明 / 能力需求声明
- P2 的字段（来自 architect.md）：packages / domains / ui_affected / gate_commands
- 主 Agent 用这些协议定义的节名称给导航，不需要读产出文件的实际内容
- 节名称是协议固定的，章节号是 subagent 自己编的——导航用节名称，不用章节号

**主 Agent 的核心职责是任务分解 + 输入导航 + 验证**，不是传话筒（把文件路径原样转发），也不是消化器（读完所有文件做提炼）。

—— T016 教训：P3 派发时主 Agent 把 7 个文件路径（~1917 行）甩给 subagent，没给任何导航。subagent 要自己理解 BDD + 接口 + 串行队列 + mock + vitest，认知负荷过载导致 3 次空返回。

**残余风险**：如果 subagent 产出时偏离了角色定义的节结构（用了自定义标题），导航会静默失效——subagent 找不到对应节，大概率又是空返回循环。缓解方式：P1/P2 gate 检查时，主 Agent 顺带验证产出文件是否含角色定义要求的节名称，缺失则门槛不通过。

---

## 派发 prompt 模板

主 Agent 调用 task 工具时，prompt 用这个结构（详见 `assets/templates/dispatch-prompt.md`）：

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

## 任务
{这个阶段要做什么，一两句话}

## 输出
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}
必须包含 Header：
  phase: {Pn}
  task_id: {Txxx}
  parent: {上一阶段文件名}
  trace_id: {Txxx}-{Pn}-{日期}

## 门槛（什么算完成）
{可判定的完成条件}

## 返回给我
只返回两行：
  1. 产出文件路径
  2. 一句话摘要（不超过 30 字）
不要返回文件全文。
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
- 产出 **2 种及以上不同类型文件**（如 文档 + 代码、stub + 测试、设计 + 实现）
- 输入文件超过 5 个（主 Agent 应先检查是否都必要，精简输入比拆分任务成本低；确实都必要时再拆分）

**拆分判据用输出异构性，不用行数**——T016 失败的根因是异构切换（文档 + stub + 测试三种身份在一个 task 里），不是输入行数。LLM 处理 2000 行同质内容没问题，处理 500 行 4 种技术域照样会崩。行数是弱相关变量，异构性才是强相关变量。

**拆分原则：**
- 每个任务产出 1-2 个文件，只涉及一种技术类型
- 每个任务的输入文件 ≤ 3 个
- 任务间有依赖时串行，无依赖时并行
- 拆分通过多次 task 调用实现，commit message 记录拆分（如 `wf(Txxx-P3a): 测试用例文档`）
- 状态机不变——仍只看 P3 阶段，gate 仍是该阶段的门槛命令

—— T016 教训：P3 要求一个 subagent 产出 3 个异构文件（P3-test-cases.md 文档 + usePlantUML.ts stub 代码 + usePlantUML.spec.ts 测试代码），主 Agent 要在技术文档作者、TypeScript 开发者、测试工程师三种身份间切换，粒度过大。

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
| P1→P2 | 需求基线建立 | P1-requirements.md 存在 + 有 Header + 含 ≥1 条 BDD 条件 + 无未决 `[NEED_CONFIRM]` + 无 `[CAPABILITY_GAP]` |
| P2→P3 | 方案已批准 | P2-review.md `status: approved` + P2-design.md 含 packages/domains/ui_affected/gate_commands 四字段 |
| P3→P4 | TDD 真红灯 | `scripts/check-tdd-red.sh` exit 0（UI 任务额外确认 Playwright 用例存在）|
| P4→P5 | 实现完成 | P4-implementation/ 下文件非空 + `git log --oneline -1` 确认 P4 commit |
| P5→P6 | 技术验证通过 | `pytest -q` exit 0 AND failed==0（亲手跑）+ 无 `[PROD_TOUCHED]` + 若 ui_affected：Playwright/E2E 实跑通过 |
| P6→P7 | BDD 验收通过 | P6-acceptance.md 中 P1 每条 BDD 都有实跑结果 + 无未决 `[NEED_CONFIRM]`（UI 条件须截图）|
| P7→P8 | 一致性通过 | `! grep -qF '[BLOCKER]' P7-consistency.md`（已知限制：定性分析，P5 回归测试兜底）|
| P8→READY | 发布准备完成 | **每个** P2 声明的 package 的发布检查命令 exit 0 + `git diff` 确认各包 version bump + CHANGELOG |

**反例（禁止用作门槛）：**
- ❌ "unit.md 里 failed: 0"（信 subagent 写的数字）
- ❌ "P8-release.md 存在"（文件存在不等于已发布）
- ❌ "P6 里 subagent 写了 ✅"（信 subagent 自我报告，见下方 C7 规则）
- ❌ "UI 代码看起来对"（UI 必须实跑 Playwright，不接受目测）
- ❌ "方案足够好" / "测试差不多了"

**A1 原则**：gate 判定是主 Agent 运行命令得到的客观事实，不是 subagent 文件里的声明。

**C7 规则（subagent 自我报告不可信）**：subagent 产出里的"检查结果""✅/通过"等自评，**仅供参考，绝不作为 gate 判定依据**。gate 一律以主 Agent 亲自跑命令的结果为准。T005 教训：P8 subagent 把 `1 failed` 标成 ✅，主 Agent 若信了就放行了缺陷。

**packages 动态注入（B4/B6）**：派发 P8 subagent 时，主 Agent 必须先读 P2-design.md 的 `packages:` 声明，把"需要 bump 哪些包"明确写进 prompt，并据此从 `gate_commands:` 字段生成各包的 gate 命令集。不能用固定的单包命令——不同项目的发布命令不同，必须从 P2 声明读取。

**P5/P6 gate 命令固化（B7）**：P5/P6 的 gate 命令必须从 P2-design.md 的 `gate_commands:` 字段读取，不得在派发 prompt 里自行修改或降级。
- subagent 要求跳过命令 / 换更简单的命令 → `[SCOPE_GAP]`，不通过
- 命令本身跑不通（能力缺口）→ `[CAPABILITY_GAP]` 交人决策，不得自行降级为目测
- T004 教训 B7：P6 子代理连续失败后，主 Agent 要求「不用 Playwright，纯命令行验证」—— 这是主 Agent 降级了 P2 已固化的验收标准，属于违规。

**SCOPE+ / SCOPE_GAP 扫描**：每次 subagent 返回后，主 Agent 扫描产出是否含 `[SCOPE+]`（新隐含需求 → 增补 P1 基线 + 定向回补）或 `[SCOPE_GAP]`（prompt 漏了 P2 已声明的改动 → 修正 prompt 重派）。

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

1. **硬超时**：`task` 工具设 generous timeout（默认 10 分钟），防止无限等待
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
