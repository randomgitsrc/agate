# Agent 文件读取保证

> 日期：2026-06-16
> 状态：待决策

## 问题

`orchestrator-template.md` 的"工作流规则"一节列出按需读取文件清单：

```markdown
- 入口文件: WORKFLOW.md
- 其余文件按需读取：
  - dispatch-protocol.md
  - state-machine.md
  - assets/execution-roles/
  - assets/templates/
  - platform-notes.md
```

agent 大概率只读 WORKFLOW.md，"按需读取"的文件不会主动去读。

## 根因

"按需读取"是被动表述——agent 不知道"什么时候需要"，就不读。用触发条件（"派发前必读""状态转移时必读"）替代"按需"是同一个问题——agent 需要先识别自己处于某个场景才会触发，但识别本身不可靠。

**本质**：用规则触发规则，和用"按需"触发规则，是同一个问题。agent 缺的不是触发条件，是读取动作本身的确定性。

## 方案演进

### 方案 A：条件触发表（否决）

把"按需"改成具体的触发条件。问题：条件本身需要 agent 识别"我在派发""我在转移状态"，和"按需"是同一个问题。

### 方案 B：内联进 WORKFLOW.md（否决）

把 gate 表、转移规则、角色映射等操作性内容直接写进 WORKFLOW.md。问题：WORKFLOW.md 已 311 行，再塞 ~140 行会膨胀；与 dispatch-protocol.md / state-machine.md 严重重复；维护一处改多处。

### 方案 C（当前共识）：在 orchestrator-template 里写固定执行流程

把每步操作写成固定流程，读取动作嵌入流程步骤，不存在"要不要读"的判断：

```markdown
## 每一步执行流程

1. 读 {project_root}/docs/tasks/active-tasks.md → 确认当前阶段
2. 读 {agate_root}/state-machine.md → 确认本阶段转移规则和重试上限
3. 读 {agate_root}/dispatch-protocol.md → 确认本阶段 gate 命令和派发模板
4. 读 {agate_root}/assets/execution-roles/{本阶段角色}.md → 确认角色定义
5. 派发 subagent
6. 亲自跑 gate 命令
7. 更新状态
```

核心思路：从"你需要时去读"变成"每一步都先读这些再动手"。1-4 是固定动作，不存在"要不要读"的判断。

**为什么写在 orchestrator-template 而不是 WORKFLOW.md**：orchestrator-template 是 agent 的角色提示词，保证被读到；WORKFLOW.md 是被 template 引用的文件，agent 可能读了就觉得自己够了。

**代价**：template 变长；与 state-machine.md 的"单步执行函数"有重复。但重复的只是"读什么"的清单，不是完整规则内容——一个是编排指令（template），一个是机制定义（state-machine.md）。

## 待决策

1. 方案 C 是否可接受？重复代价 vs 读取保证的权衡
2. 固定流程的粒度——7 步够不够？是否需要细化到每个阶段的不同读取内容？
3. 是否需要同步修改 WORKFLOW.md 的"按需读取"措辞，避免两个文件的指令矛盾？

## 修改范围（若采用方案 C）

- `orchestrator-template.md`：新增"每一步执行流程"节，替代现有"工作流规则"的按需读取清单
- 其余文件不动
