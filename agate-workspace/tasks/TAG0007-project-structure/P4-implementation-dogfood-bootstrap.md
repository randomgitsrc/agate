---
phase: P4
task_id: TAG0007
type: implementation
parent: P2-design.md
trace_id: TAG0007-P4-dogfood-bootstrap-20260820
status: draft
created: 2026-08-20
agent: implementer
---
implementation_dir: agate-workspace/agents/

## 产出摘要

新建 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（本 worktree 的
`agate-workspace/agents/CODE-MAP.md`，`agents/` 目录此前不存在，已创建），为 agate 协议本体
自身初始化 CODE-MAP dogfooding 实例——BDD-6「CODE-MAP 存在性」的验收对象。

内容按 P2-design.md §1.1 表格最后一行 + dispatch-context 约束 2 的字段清单，五类必填字段
（模块 / 层 / 依赖方向 / 关键文件 / 约定）均填真实内容，描述 agate 协议本体的实际架构：

- **模块**：phase-cards（9 张阶段卡片）/ execution-roles（7 个执行角色）/ review-roles（10 个
  评审角色）/ scripts（gate/一致性/状态三大脚本家族 + 编排辅助脚本）/ templates（模板文件，
  含协作批次新增的 `code-map-template.md`）。
- **层**：协议流程层（phase-cards）→ 角色层（execution-roles + review-roles）→ 工具层
  （scripts）→ 模板层（templates），逐层说明各层职责与消费关系。
- **依赖方向**：phase-cards 松耦合不依赖角色/脚本实现细节；scripts 消费 phase-cards/templates
  声明的字段名做判定（举例 `check-gate.py` 的 `gate_p7` 读 `code_map_new_files_count` 等字段）；
  execution-roles/review-roles 消费 phase-cards 声明的职责边界，不反向定义流程；明确禁止反向
  依赖。
- **关键文件**：WORKFLOW.md / dispatch-protocol.md / state-machine.md / role-system.md /
  check-gate.py，各自一句话职责说明。
- **约定**：新增机制需经 P0-P8 完整流程不可裁剪、改协议脚本走 TDD、改协议文档/脚本/卡片触发
  SELF-GATE 自审。

标题层级采用 `##`（模块/层/依赖方向/关键文件/约定），与 `code-map-template.md` 的标题结构一致
（dispatch-context 允许不强制完全一致，本次选择对齐以便对照阅读）。

内容中模块/角色/脚本/模板的数目（7 个执行角色、10 个评审角色、9 张阶段卡片）已实地
`ls` 核对，非猜测填写；`code-map-template.md` 已存在（另一并行批次 `code-map-docs` 的产出物），
本批次只读取参照其标题结构，未做任何修改。

## 关联 BDD

- BDD-6：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在，含模块/层/依赖方向/关键文件/约定五类
  字段——本文件即该验收对象，供 P6 acceptance 人工核对存在性。

## 自查记录

```
$ test -f agate-workspace/agents/CODE-MAP.md && echo EXISTS_OK
EXISTS_OK
$ grep -c "模块\|层\|依赖方向\|关键文件\|约定" agate-workspace/agents/CODE-MAP.md
15
```
五字段名（模块/层/依赖方向/关键文件/约定）均出现在文件中（含正文引用，不止标题行）。

## 范围确认

本批次只产出 `agate-workspace/agents/CODE-MAP.md` 一个文件，未触碰其他三个并行批次
（skeleton-docs / code-map-docs / gate-script-both）范围内的任何文件。
