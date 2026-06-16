# Agent 文件读取保证

> 日期：2026-06-16
> 状态：已决策

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

### 方案 C：每步重读（否决）

在 orchestrator-template 里写固定流程，每步都重读 state-machine.md + dispatch-protocol.md。问题：
- state-machine.md 和 dispatch-protocol.md 的规则在运行中不会变，每步重读是多余的
- 执行角色文件是 subagent 读的，不是主 Agent（编排者）读的——混入流程反而是错误指令

### 方案 D（采用）：启动时一次性读完

主 Agent 启动后、执行任何任务前，依次读完 4 个核心文件：

```markdown
## 工作流规则

遵循 agate 工作流。启动后依次读完以下文件，再开始执行任务：

1. {agate_root}/WORKFLOW.md          ← 阶段总览 + 角色映射 + 裁剪规则
2. {agate_root}/dispatch-protocol.md  ← 派发模板 + gate 表 + 特殊事件处理
3. {agate_root}/state-machine.md      ← 转移规则 + 重试上限 + 单步函数
4. {agate_root}/role-system.md        ← 双层角色体系 + domains→评审角色映射

其余文件（loop-orchestration.md、git-integration.md、platform-notes.md）
在需要时参考。
```

**为什么是这 4 个**：编排者需要的全部规则都在里面——阶段总览、gate 命令、派发模板、转移规则、重试上限、角色选择。读完就能走完 P0-P8。

**为什么不列 execution-roles**：执行角色文件是 subagent 在独立上下文里读的，不是编排者读的。编排者只需要知道"P1 派 analyst"，这 WORKFLOW.md 里已经有了。

**代价**：4 个文件约 1400 行，启动时一次性读入上下文。相比方案 C 的每步重读（P0-P8 累计 ~7500 行重复扫描），是一次性固定开销 vs 持续重复开销的权衡。

## 修改范围

- `orchestrator-template.md`：将"其余文件按需读取"改为"启动后依次读完 4 个核心文件"
- 其余文件不动
