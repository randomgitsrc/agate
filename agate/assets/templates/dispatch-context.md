> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: {P1-P8}
generated_by: agate-next-card.sh + 主 Agent
task_id: {Txxx}
role: {角色名，如 analyst / requirements-review / implementer}
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
{一句话：本角色在本阶段要产出什么}

### 约束
{从 P0-brief env_constraints/known_risks + 上游产出 + 协议知识提取。写的是"必须满足什么/不能做什么"，不是"应该怎么做"——后者是 subagent 的自主决策空间}

### 上游关联
{上一阶段 subagent 摘要中的关键信息}

### 输入文件
- docs/tasks/{Txxx}/P0-brief.md（主 Agent 的任务简报和风险声明）
- docs/tasks/{Txxx}/{上一阶段产出文件}
- {project_conventions_file}（项目约定）
{按角色定义补充其他需要读的文件}
</dispatch_guide>

<!-- AGATE_CARD_START -->
{CLI 输出原文}
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：{服务运行状态、版本号}
- 关键标识：{URL、API 端点、文件 ID、DOM 选择器}
- 查证结果：{grep/命令输出摘要}
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
