# 项目 roadmap 看板（roadmap-template.md）

> 复制此文件到 `{AGATE_WORKSPACE}/roadmap/roadmap.md`，作为项目级任务规划看板。
> 与 active-tasks.md 的关系：roadmap 是**规划层**（"想做什么、做了没"），active-tasks.md 是**执行层**（"正在/待实施的任务看板"）。由 roadmap 条目拆出的任务，其任务行记录 `roadmap: <条目id>` 关联。

---

## 条目列表

| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |
|----|------|------|------|----------|------|------|
| RM-AG0001 | 示例条目：某某功能 | backlog | 需求讨论 2026-08-01 | — | 2026-08-01 | 2026-08-01 |

## 状态标识

| 状态 | 说明 | 何时进入 |
|------|------|----------|
| `backlog` | 待规划 | 新需求/讨论进入 roadmap 时（含来源与日期）|
| `scheduled` | 已拆任务 | 拆任务 → 工作区 tasks/ 建任务目录 + active-tasks.md「待开始」写入任务行（任务行 `roadmap: <条目id>` 关联）|
| `in_progress` | 实施中 | 对应任务进入 P1 起（可选标记，不做强制）|
| `done` | 已完成 | 任务 P8 gate + READY 完成 → 回写 |
| `cancelled` | 取消 | 需求变更/不再需要 → 回写 |

## 条目 id 规则

- 格式：`RM-{项目代号}{编号}`（如 `RM-AG0001`），项目代号对齐任务编号规则（2 个大写字母，见 active-tasks-template.md 第 4 条）。
- 项目局部命名空间内递增，不复用已取消条目的编号。

## 循环规范（正式规则见 WORKFLOW.md「roadmap 循环」）

1. **需求/讨论 → backlog**：新需求或讨论 → 追加一条 `backlog` 条目，来源列记录需求出处（讨论/评审/复盘），创建列记日期。
2. **条目 → 任务**：拆任务时在 `{AGATE_WORKSPACE}/tasks/` 建任务目录 + active-tasks.md「待开始」区写入任务行，任务行记录 `roadmap: <条目id>`；同时把条目状态改为 `scheduled`。
3. **任务完成 → 回写**：任务完成（P8 gate + READY）→ 条目状态改为 `done`（或 `cancelled`），更新列记日期。闭环：任务→条目（任务行 roadmap 字段）、条目→任务（条目关联任务列）双向可见。

## 维护规则

1. 只有主 Agent 维护本文件，subagent 不直接写。
2. 条目状态变更与任务看板推进同步（拆任务 → scheduled，完成 → done）。
3. 状态只允许五选一（backlog/scheduled/in_progress/done/cancelled），不写中间态。
4. **done 条目折叠归档**：done 条目移出主表 → 折叠到文件底部「已归档 RM 条目」的 `<details>` 块（信息保留，主表只留 backlog/scheduled 活跃项）。**折叠只用于已完成/归档区，活跃条目（backlog/scheduled）永不折叠**（要常看）。
5. **折叠 summary 禁硬编码数字**：`<summary>` 文案**不写具体数量**（如"已完成的 RM"而非"已完成的 7 条 RM"）——数量会漂移，省略避免漂移。需要数量时从表格行自动统计。

---

> 模板字段：条目 id、标题、状态标识（backlog/scheduled/in_progress/done/cancelled）、来源（新需求/讨论）、关联 task_id、创建、更新。
