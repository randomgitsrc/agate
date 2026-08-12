---
phase: P4
task_id: TAG0003-workspace-architecture
type: implementation
parent: P2-design.md
trace_id: TAG0003-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0003 — 工作区架构：P4 实现记录（协议文档组 implementer-docs）

> 角色：implementer-docs（3 个并行 implementer 之一，只改协议文档文件集）。
> 范围：16 个既有协议文档的 `docs/tasks` 引用换血 + 新增 `roadmap-template.md` + WORKFLOW.md 内容边界判据与 roadmap 循环规范 + orchestrator-template 路径切换。
> 未改动：脚本（implementer-core 负责）、测试 fixture（implementer-tests 负责）。

## 1. 改动清单（16 + 1 + 扩展）

### 1.1 16 个既有文档

| 文件 | 改动 |
|------|------|
| `orchestrator-template.md` | project.md 路径 3 处（L21/25/113 语义位）→ `{AGATE_WORKSPACE}/agents/project.md`；active-tasks 路径 3 处（L69/94/115 语义位）→ `{AGATE_WORKSPACE}/tasks/active-tasks.md`；接入 mkdir 建 8 子目录；会话开始解析 `AGATE_WORKSPACE`（`agate-workspace-resolve.sh`）；旧布局检测 + 迁移指引（BDD-10，不静默使用旧路径/不静默失败） |
| `state-machine.md` | 首接入节 mkdir docs/tasks → 建工作区 8 子目录；产出路径 → `{AGATE_WORKSPACE}/tasks/{Txxx}/`；其余任务路径引用（PAUSED-resolution / 状态绑定 / P0-brief 确认 / 状态文件位置 / orchestrator-log）全部换血 |
| `dispatch-protocol.md` | 28 处 `docs/tasks/{Txxx}/` → `{AGATE_WORKSPACE}/tasks/{Txxx}/`（含铁律示例、dispatch-context 文件名、输入文件清单、派发 prompt 模板、P6-evidence、HANDOVER、完整示例 TAG0001、评审意见回流） |
| `git-integration.md` | commit 规范 `git add docs/tasks/{task_id}/ docs/tasks/active-tasks.md` → 工作区路径（策略 1 任务目录隔离 + 规则 2 单步 commit） |
| `role-system.md` | 评审对象/产出路径 → `{AGATE_WORKSPACE}/tasks/{Txxx}/P2-design.md` + `P2-review.md` |
| `WORKFLOW.md` | 目录结构图 + 新增「工作区目录规范」节（8 子目录）+ **内容边界判据正式规则**（BDD-17，含二值判定 + 对偶自洽性）+ **roadmap 循环规范**（BDD-14/15/16 三步循环 + 状态机）+ 任务目录命名改为工作区路径 + 多任务适配/状态落盘路径 |
| `SETUP.md` | project.md 位置 → 工作区 agents/；初始化 mkdir 建 8 子目录；新增 `.agate.env` 配置节（优先级/相对绝对/空格路径/缺失不报错）；.gitignore 建议同步 |
| `UPGRADING.md` | 新增 v2.0.0 工作区架构迁移节（迁移工具步骤 + 手工迁移 + 项目侧文件位置变化 + 未迁移行为 + 外部工作区限制，BDD-6/8/10/18）；2.3/2.4 旧布局说明 + 升级验证路径同步 |
| `phase-cards/P{0,1,2,3,4,5,6,7,8}*.md` | 各卡片 `git add docs/tasks/{Txxx}/` → 工作区路径；P4 的 `.retreat-history.md` 引用、P5 的 known-failures、P0/P8 的 active-tasks 引用同步换血 |
| `assets/templates/active-tasks-template.md` | 复制目标 → `{AGATE_WORKSPACE}/tasks/active-tasks.md`；目录结构图 → 工作区；待开始表加 `roadmap` 关联列（BDD-15） |
| `assets/templates/project.md` | 复制目标 → `{AGATE_WORKSPACE}/agents/project.md` |
| `assets/templates/dispatch-context.md` | 输入文件路径 → `{AGATE_WORKSPACE}/tasks/{Txxx}/` |
| `assets/templates/task-files.md` | 目录说明 → `{AGATE_WORKSPACE}/tasks/{Txxx}/` |
| `assets/templates/dispatch-prompt.md` | dispatch-context/P0-brief/progress 留痕/产出路径/P6-evidence → 工作区路径 |
| `assets/execution-roles/*.md`（7 个） | 输入/产出/落盘路径中的 `docs/tasks/{Txxx}/` → `{AGATE_WORKSPACE}/tasks/{Txxx}/`（analyst/architect/consistency-reviewer/implementer/test-designer/verifier/vision-analyst） |
| `loop-orchestration.md` + `rules/state-transitions.md` | active-tasks/任务目录引用 → `{AGATE_WORKSPACE}/tasks/active-tasks.md` / `{AGATE_WORKSPACE}/tasks/{Txxx}/` |

### 1.2 新增（1 个）

- `assets/templates/roadmap-template.md`：roadmap 条目模板——条目 id（`RM-{项目代号}{编号}`）、标题、状态标识（backlog/scheduled/in_progress/done/cancelled 五选一）、来源、关联任务、创建/更新列；状态机 + 三步循环规范 + 维护规则。

### 1.3 SCOPE+ 扩展（不在 P2 §1.1 16 文档清单内，但同为协议文档且含旧路径，一并换血）

[SCOPE+] 发现：`assets/templates/custom-role.md`、`assets/review-roles/protocol-alignment-review.md`、`phase-cards/P0-orchestrator.md`、`phase-cards/P8-release.md` 也含 `docs/tasks` 或裸 `active-tasks.md` 引用，不在 P2 §1.1 的 16 文档清单内。漏改会让这 4 个协议文档继续指向旧布局（新角色模板会教用户写旧路径、一致性审查会引用旧任务目录）。
        必须做的理由：与 BDD-6「docs/tasks 迁入工作区」+ BDD-10「旧布局获得迁移指引」一致——协议文档不应残留旧路径教学；custom-role.md 是自定义角色模板的权威来源，其路径示例会被复制进新角色文件。
        影响：4 个文件已一并换血；若 P7 一致性核对发现更多遗漏，按同法补齐。

## 2. 路径语义约定（本次实现遵循）

- 文档统一用 `{AGATE_WORKSPACE}/...`（工作区根，解析自 `agate-workspace-resolve.sh` 输出）表述。
- 任务路径统一 `{AGATE_WORKSPACE}/tasks/{Txxx}/`；看板 `{AGATE_WORKSPACE}/tasks/active-tasks.md`；project.md `{AGATE_WORKSPACE}/agents/project.md`；roadmap `{AGATE_WORKSPACE}/roadmap/roadmap.md`。
- bash 侧变量 `AGATE_TASKS_DIR`（tasks 基目录）保留给脚本实现（implementer-core 负责），文档不重复声明其推导。
- 8 子目录：roadmap/tasks/agents/archived/reviews/decisions/plans/logs（orchestrator 接入 mkdir + state-machine 首接入 + SETUP 初始化三处一致）。

## 3. 关键行为点核对（对 P2 方案 §3.3/3.4/3.5）

- **orchestrator 路径切换（§3.3）**：project.md / active-tasks / mkdir 8 子目录 / 旧布局检测（BDD-10）四处全部落地。旧布局检测逻辑：`docs/tasks/active-tasks.md` 存在而工作区 tasks 无 → 输出迁移指引 `bash {agate_root}/scripts/agate-migrate-workspace.sh` 并停止自动推进。
- **roadmap 循环（§3.4）**：WORKFLOW.md 正式规范节 + roadmap-template.md 模板就位，三步循环（backlog → scheduled → done/cancelled）有状态机定义。
- **内容边界判据（§3.5）**：WORKFLOW.md 正式规则节含判据原文（BDD-17 锚点）+ 二值判定 + 对偶自洽性双场景。
- 与 implementer-core 解析器输出的衔接：文档引用 `{AGATE_WORKSPACE}` 与 `agate-workspace-resolve.sh`，脚本名/输出格式以 core 组实现为准，本组不改脚本。

## 4. 自查结果（自查≠P5 gate）

- `python3 agate/scripts/check-protocol-consistency.py` → 全部检查 PASS，0 ERROR（含新增 roadmap-template 的引用检查 CHECK 2）。
- `rg 'docs/tasks'` 残留仅存在于 UPGRADING.md / orchestrator-template.md 的**迁移语境**（旧布局说明、旧→新对照），属有意保留；协议读取路径无残留旧路径。

## 5. DESIGN_GAP / SCOPE+ 声明

[SCOPE+] 见 §1.3（custom-role / protocol-alignment-review / P0-card / P8-card 四个清单外文档一并换血）。

[DESIGN_GAP: P2 §3.3 只列了 orchestrator-template 的 4 处路径切换点，未覆盖 phase-cards/P0-orchestrator.md 与 P8-release.md 的裸 `active-tasks.md` 引用；实现中将其一并改为工作区路径以保持一致。]

## 6. 交付物

- 16 个既有文档换血 + `assets/templates/roadmap-template.md` 新增（见 §1）
- 本文件：P4-implementation-docs.md（实现记录）
