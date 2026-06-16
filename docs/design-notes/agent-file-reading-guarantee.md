# Agent 文件读取保证

> 日期：2026-06-16
> 状态：已决策，已落地（非过时，无需失效标记）
> 落地位置：`orchestrator-template.md`「工作流规则」一节 / `state-machine.md`「为什么这样能抗中断」一节

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

主 Agent 启动后、执行任何任务前，依次读完全部顶层协议文件：

```markdown
## 工作流规则

遵循 agate 工作流。启动后依次读完以下文件，再开始执行任务：

1. {agate_root}/WORKFLOW.md          ← 阶段总览 + 角色映射 + 裁剪规则
2. {agate_root}/dispatch-protocol.md  ← 派发模板 + gate 表 + 特殊事件处理
3. {agate_root}/state-machine.md      ← 转移规则 + 重试上限 + 单步函数
4. {agate_root}/role-system.md        ← 双层角色体系 + domains→评审角色映射
5. {agate_root}/loop-orchestration.md ← /loop 自动编排 + 护栏规则
6. {agate_root}/git-integration.md    ← commit 规范（wf() 前缀）+ push 策略
7. {agate_root}/platform-notes.md     ← 各平台能力差异 + 已知坑
```

**为什么不列 assets/ 下的文件**：执行角色文件和模版是 subagent 在独立上下文里读的，编排者不需要读。编排者只需要知道"P1 派 analyst"，这 WORKFLOW.md 里已经有了。

**为什么全列而不是挑 4 个**：loop-orchestration.md 里的全局步数上限、git-integration.md 里的 `wf()` 前缀约定、platform-notes.md 里的 issue #29616——这些文件存在的意义就是"防止踩坑"。如果 agent 不读，它们的存在价值就丢失了。没有哪一个是可以安全跳过的。

**代价**：7 个文件约 1900 行，一次性读入上下文。相比按需读取的"几乎不读"，是有明确回报的固定开销。

## 延伸决策：中断恢复时同样要重读

方案 D 解决的是"启动时"的读取保证，但 agate 的核心前提是会话可能被压缩/中断/重启（见 state-machine.md「为什么这样能抗中断」）。中断恢复时，state-machine.md 原有的恢复步骤只重建**任务进度**（读 active-tasks.md、判断阶段产出文件是否存在），没有覆盖**协议规则本身**是否还在上下文里。

这是两类不同的状态：任务状态会变（在哪个阶段、重试几次），协议规则不会变（gate 怎么判、prompt 怎么写）。前者必须靠文件重建（agate 设计的核心），后者容易被忽略——因为主 Agent 即使忘了协议细节，依然能"看起来正常"地继续派发，只是派发的内容可能不准确（比如漏掉某次协议升级新加的字段）。

**修正**：中断恢复 = 一次新的启动。在 state-machine.md「为什么这样能抗中断」的恢复步骤里，第一步必须是重读 7 个协议文件（与方案 D 的启动读取清单一致），再进入任务进度的重建。不能假设"压缩前读过的协议内容还在"。
