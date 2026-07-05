# P0 — 任务启动

> P0 不派 subagent（主 Agent 亲自执行）。结构与其他卡片不同。
>
> 当前阶段：P0

## 做什么

P0 是立项阶段。主 Agent 自己写完 P0-brief.md，不派 subagent。

## P0-brief.md 五字段

```yaml
task: "一句话描述任务（工程视角）"
known_risks:
  - "涉及数据 schema 变更"
  - "跨越多个改动端"
executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
env_constraints:
  debug_env: "项目的测试/调试环境命令或路径"
pruning_tendency: "保守 / 激进"
```

任一字段为空占位符 → 补完再推进 P1。五字段是 agate 要求的最小集，项目可按需扩展。

## 环境自检

在启动任务前确认环境可用：
- debug 环境可访问（curl health check / 启动服务）
- 测试框架可用（pytest/vitest --version）
- 浏览器自动化可用（playwright --version，UI 任务时）

## 任务粒度

若写不出一句话任务描述 → 任务太大，考虑拆分。单任务应在 1-2 个会话内完成。

## 推进条件

P0-brief.md 五字段齐全 → 写 active-tasks.md（新任务行）→ 读 P1 卡片

## loop 模式

若使用 `/loop` 自动编排：P0 完成后主 Agent 按顺序自动推进 P1→P8，遇 PAUSED 或异常时停下。

## 下游影响

P0-brief 的 env_constraints / known_risks / executor_env 会在 P1-P8 每个阶段派发 subagent 时注入。写清楚能让每个 subagent 知道项目约束。
