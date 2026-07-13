# 评审角色机械映射（C8）

> ⚠️ C8 是 mapping **机制**，不是 mapping **结果**。
> 协议不穷举每个项目的评审角色——项目方应基于本表扩展，
> 文档化自己的 mapping（示例：项目侧 `docs/decisions/review-mapping.md`）。
> 主 Agent 看到本表应理解：表内触发是最低要求，
> 表外应根据安全/认证/数据迁移等场景主动派评审。

> 权威源：`agate/role-system.md`。提取 C8 机械映射表，供 P2/P4 卡片按需引用。

## 映射规则

P1 在 requirements.md 声明 `domains:` 和 `risk_level:`，主 Agent **机械映射**评审角色：

| domain | risk_level | 触发评审角色 | 插入阶段 |
|--------|------------|-------------|---------|
| backend | 任意 | review | P4 后 |
| frontend | 任意 | plan-design-review | P2 |
| frontend | 任意 | design-review | P4 后 |
| mcp | 任意 | review + 关注 MCP 接口契约 | P4 后 |
| security | 任意 | cso | P4 后 |
| 任意 | **high** | plan-eng-review（硬规则，必须派独立 subagent） | P2 |
| 业务方向不明 | 任意 | office-hours / plan-ceo-review | P1 后 / P2 |

## 评审产出规范

所有作为阶段门槛的评审产出的 Header 统一 status 字段：

| 评审结论 | status 值 |
|---------|----------|
| 确认 / 通过 / PASS / approved | `approved` |
| 转向 / 打回 / HOLD / 有 BLOCKER / rejected | `rejected` |
| 需补充 / needs revision | `needs-revision`（计入重试） |

主 Agent 只读 `status` 字段判定，不需要理解各角色的具体结论语义。

## 专家组并行 + 组长汇总

P2 / P4 评审可同时派发多个角色（并行），所有评审返回后派发组长汇总：

- 输入：所有评审文件路径
- 输出：统一 P2-review.md（或 P4-review.md），status: approved / rejected

## 非门槛评审

纯参考的 office-hours 方向建议不强制 status，也不参与门槛判定。
