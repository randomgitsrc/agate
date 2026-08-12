# roadmap 模拟闭环记录（BDD-14/15/16 共享证据）

> 按 WORKFLOW.md「roadmap 循环」+ assets/templates/roadmap-template.md 规范，在 fixture
> /tmp/opencode/p6fix/roadmap-sim/agate-workspace/ 模拟执行完整闭环：
> 新需求进入 roadmap（backlog）→ 拆任务进待开始看板（scheduled）→ 任务完成回写（done）。

## 1) BDD-14 模拟：新需求进入 roadmap（追加 backlog 条目，含来源与日期）
roadmap.md 追加条目：
| RM-AG0003 | 审计日志导出 | backlog | 需求讨论 2026-08-12 | — | 2026-08-12 | 2026-08-12 |

## 2) BDD-15 模拟：条目拆分为任务
- 工作区 tasks/TAG0004-audit-export/ 建任务目录（含 .state.yaml）
- tasks/active-tasks.md「待开始」区写入任务行并记录 roadmap 关联：`- [ ] TAG0004-audit-export (roadmap: RM-AG0003)`
- roadmap 条目状态 backlog → scheduled：| RM-AG0003 | 审计日志导出 | scheduled | 需求讨论 2026-08-12 | TAG0004-audit-export | 2026-08-12 | 2026-08-12 |

## 3) BDD-16 模拟：任务完成回写（闭环）
任务实施完成（模拟 P8 gate + READY）→ 回写条目状态 done：
| RM-AG0003 | 审计日志导出 | done | 需求讨论 2026-08-12 | TAG0004-audit-export | 2026-08-12 | 2026-08-12 |

## 闭环双向可见
- 任务→条目：active-tasks.md 任务行 `roadmap: RM-AG0003`
- 条目→任务：roadmap.md 条目关联任务列 `TAG0004-audit-export`

## 状态合法性
全程仅使用五状态之一（backlog / scheduled / done），无中间态。

## 模拟产物（fixture 实文件）
- roadmap/roadmap.md（含 RM-AG0001/2 示例 + RM-AG0003 闭环）
- tasks/active-tasks.md（含待开始任务行 + roadmap 关联）
- tasks/TAG0004-audit-export/.state.yaml
