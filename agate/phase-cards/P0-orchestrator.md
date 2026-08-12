# P0 — 任务启动

> P0 不派 subagent（主 Agent 亲自执行）。结构与其他卡片不同。
>
> 当前阶段：P0

## 做什么

P0 是立项阶段。主 Agent 自己写完 P0-brief.md，不派 subagent。

## P0-brief.md 四字段

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
```

任一字段为空占位符 → 补完再推进 P1。四字段是 agate 要求的最小集，项目可按需扩展。

## 环境自检

启动任务前必须确认环境可用（不确认不得推进 P1）：
- debug 环境可访问（curl health check / 启动服务）
- 测试框架可用（项目使用的测试框架，如 pytest/vitest/go test/cargo test --version）
- 浏览器自动化可用（playwright --version，UI 任务时）

## 任务粒度

若写不出一句话任务描述 → 任务太大，必须拆分为多个任务。不允许用模糊描述强行通过。

## 推进条件（全部满足才推进）

- [ ] P0-brief.md 四字段齐全（无空占位符）
- [ ] 环境自检已执行（debug 环境 / 测试框架 / UI 任务的浏览器自动化）
- [ ] {AGATE_WORKSPACE}/tasks/active-tasks.md 已写入新任务行

推进后 → 读 P1 卡片

## loop 模式

若使用 `/loop` 自动编排：P0 完成后主 Agent 按顺序自动推进 P1→P8，遇 PAUSED 或异常时停下。

## 任务类型提示

**hardening / refactor 类任务**：P0-brief 建议包含代码审计结果（现有代码的问题清单），作为 P1 需求的输入。P0 卡片不强制要求审计（非门槛），但跳过审计可能导致 P1 需求不完整、P2 设计基于错误假设。

## P0-brief 质量自检（源自 office-hours 六问）

写完 P0-brief 后对照自检（非门槛，但跳过可能导致 P1 需求不完整）：
1. 需求真实性：有没有人真的需要这个（不是假设性需求）
2. 现状：用户现在怎么解决这个问题
3. 绝望的具体性：最痛的那个人是谁
4. 最窄切入点：最小可交付版本是什么
5. 亲眼观察：有没有看过实际使用场景
6. 未来契合：这个方向长期是否成立

## 下游影响

P0-brief 的 env_constraints / known_risks / executor_env 会在 P1-P8 每个阶段派发 subagent 时注入。写清楚能让每个 subagent 知道项目约束。
