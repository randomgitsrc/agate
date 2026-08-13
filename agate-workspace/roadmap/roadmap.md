# agate 项目 roadmap 看板

> 规划层（想做什么/做了没），执行层见 `tasks/active-tasks.md`。roadmap 条目拆出的任务行记录 `roadmap: <条目id>` 关联。

---

## 条目列表

| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |
|----|------|------|------|----------|------|------|
| RM-AG0001 | check-gate P1 标记反引号包裹识别盲区 | backlog | TPV0091 复盘 §11.1 B1（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0002 | check-tdd-red 无 formatter 时 A/B 类盲区（编译失败误判红灯）| backlog | TQC0001 复盘 Q3 残留（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0003 | subagent 短命会话制度化重试（空返回自动重试一次 + <1min 告警）| backlog | TQC0001 复盘 Q4（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0004 | P6 视觉验收能力边界：无多模态模型时强制双证据 + 雷同截图降级待复核 | backlog | TQC0001 复盘 Q7（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0005 | 冒烟验证脚本内置 finally-kill + 进程清理主 Agent 复核 | cancelled | TQC0001 复盘 Q8（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0006 | GUI 自动化框架评估（WinAppDriver/AutoIt）补真实 GUI 交互路径 | backlog | TQC0001 复盘 Q9（2026-08-13）| — | 2026-08-13 | 2026-08-13 |

## 状态标识

| 状态 | 说明 | 何时进入 |
|------|------|----------|
| `backlog` | 待规划 | 新需求/讨论进入 roadmap 时（含来源与日期）|
| `scheduled` | 已拆任务 | 拆任务 → 工作区 tasks/ 建任务目录 + active-tasks.md「待开始」写入任务行（任务行 `roadmap: <条目id>` 关联）|
| `in_progress` | 实施中 | 对应任务进入 P1 起（可选标记，不做强制）|
| `done` | 已完成 | 任务 P8 gate + READY 完成 → 回写 |
| `cancelled` | 取消 | 需求变更/不再需要 → 回写 |

## 条目 id 规则

- 格式：`RM-{项目代号}{编号}`（本仓代号 `AG`，与任务编号 `TAGxxxx` 对齐）。
- 项目局部命名空间内递增，不复用已取消条目的编号。

## 循环规范

1. **需求/讨论 → backlog**：追加 `backlog` 条目，来源列记录需求出处（讨论/评审/复盘），创建列记日期。
2. **条目 → 任务**：拆任务时建任务目录 + active-tasks.md「待开始」区写入任务行（`roadmap: <条目id>`），条目状态改 `scheduled`。
3. **任务完成 → 回写**：P8 gate + READY → 条目改 `done`（或 `cancelled`），更新列记日期。

## 维护规则

1. 只有主 Agent 维护本文件，subagent 不直接写。
2. 条目状态变更与任务看板推进同步（拆任务 → scheduled，完成 → done）。
3. 状态只允许五选一（backlog/scheduled/in_progress/done/cancelled），不写中间态。

---

## RM-AG0001 详情

**check-gate P1 标记反引号包裹识别盲区**

- **问题**：check-gate.sh P1 NEED_CONFIRM 检查用行首正则 `^\s*-?\s*\[SUGGEST:` / `^\s*-?\s*\[NO_NEED_CONFIRM\]` 计数。当标记被反引号包住（`` `[SUGGEST: ...]` `` / `` `[NO_NEED_CONFIRM]` ``）时，行首不匹配 → 计数 0；typo 兜底（`grep '\[SUGGEST'` && ! `grep '\[SUGGEST:'`）也不触发（冒号子串仍存在）→ 落入「未检测到 NEED_CONFIRM 声明」WARNING，**不阻断**。
- **影响**：主 Agent 若用反引号包裹标记（markdown 代码样式），P1 gate 静默降级为 WARNING，NEED_CONFIRM 声明形同虚设。中低风险（只影响该标记的强制力，非数据/安全）。
- **建议修复方向**：typo 兜底扩展为「子串存在 + 行首正则不匹配」也报错（类似现有 L121-124 逻辑，改为"有子串但计数为 0"），使反引号包裹被明确拦截而非静默 WARNING。契约格式已在 analyst.md:138-152 / P1-card:78 / task-files.md:186 讲清，无需改文档。
- **验证口径**：新增回归测试——反引号包住 `[SUGGEST: ...]` / `[NO_NEED_CONFIRM]` 时 gate exit 1（而非 WARNING）；合规写法仍通过。
- **攒批说明**：单独立项不值得（一个 gate 正则盲区）。等 gate/协议层问题攒到 2-4 个再拆任务走裁剪 agate（P1-P6，跳过 P7，P2 不可裁剪）。

---

## RM-AG0005 取消说明

**状态**：cancelled（2026-08-13）

**取消理由**：核实后确认**非缺陷**——机制已存在且实测有效：
- `state-machine.md:148` 收尾清单明确要求"调试服务/进程已停止"
- `dispatch-protocol.md:606-607` 要求 P8 产出列出临时服务/进程供主 Agent 清理
- TQC0001 READY 收尾**逐项实查发现并强杀了残留进程**（复盘自述"流程有效"）

冒烟验证的 finally-kill 是**项目侧实现细节**（每个项目冒烟方式不同，agate 不该规定具体实现），不属于 agate 协议 backlog。复盘结论本身是正面案例（收尾兜底生效），非缺陷。若后续要补强，可在 `state-machine.md:148` 加注"冒烟验证启动的进程须由验证者自行 finally-kill，不依赖收尾兜底"——属文档补强，不立项。
