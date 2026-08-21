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
| backend | 任意 | plan-eng-review | P2 |
| backend | 任意 | review | P4 后 |
| frontend | 任意 | plan-design-review | P2 |
| frontend | 任意 | design-review | P4 后 |
| mcp | 任意 | review + 关注 MCP 接口契约 | P4 后 |
| security | 任意 | cso | P4 后 |
| 任意 | **high** | plan-eng-review（P2 方案评审，硬规则） + P4 实现评审（按 domains 派 review/design-review/cso） | P2 + P4 |
| 任意 | **full**（tier=full 或声明 `ceremony: full`）| plan-eng-review（P2）+ cso（security 域）+ P7 不可裁 | P2 + P4 |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review | P1 后 / P2 |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。**full 档（tier=full 或声明 `ceremony: full`）与 risk_level=high 命中同一角色时同样只派 1 次**。

> **risk=high 的 P4 实现评审不可省**：P2 plan-eng-review 审的是方案设计（P2-design.md），
> P4 review 审的是实现代码（SQL 注入/竞态/TOCTOU/资源泄漏）。高风险任务（安全/权限/数据
> 迁移/生产环境）恰恰最需要 P4 实现评审——P2 审方案 ≠ 实现安全。T001 实证：risk=high 任务
> 仍应产 P4-review.md。

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

纯参考的方向建议不强制 status，也不参与门槛判定。
