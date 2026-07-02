# 复盘机制触发核对清单模板

> 每份 agate 任务复盘必须附此清单。
> 用途：强制核对 agate 的核心机制在本任务中是否被正确触发，防止遗漏。
> 使用方式：复制下方的表格到复盘文件末尾，逐条填写。

## 填写说明

- **应该触发？**：本任务中是否出现了该机制的触发条件（如：subagent 失败了→retry 应该触发；方案范围变化了→SCOPE+ 应该触发）
- **实际触发？**：主 Agent 是否按协议执行了该机制（✅ 执行了 / ❌ 没执行 / — 没有触发条件）
- **未触发后果**：如果应该触发但没触发，导致了什么后果
- **原因**：未触发的原执行错误还是机制缺口

"应该触发 = 是" 且 "实际触发 = ❌" = 执行错误（不是机制缺口）。

## 核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是/否/— | ✅/❌/— | | |
| PAUSED | 是/否/— | ✅/❌/— | | |
| PROD_TOUCHED | 是/否/— | ✅/❌/— | | |
| SCOPE+ | 是/否/— | ✅/❌/— | | |
| SCOPE_RESOLVED | 是/否/— | ✅/❌/— | | |
| DESIGN_GAP | 是/否/— | ✅/❌/— | | |
| DESIGN_GAP_REVIEWED | 是/否/— | ✅/❌/— | | |
| NEED_CONFIRM | 是/否/— | ✅/❌/— | | |
| CAPABILITY_GAP | 是/否/— | ✅/❌/— | | |
| gate 验证（每阶段） | 是/否/— | ✅/❌/— | | |
| 阶段产出文件（每阶段） | 是/否/— | ✅/❌/— | | |
| .state.yaml phase 同步 | 是/否/— | ✅/❌/— | | |
| 裁剪条件 + override | 是/否/— | ✅/❌/— | | |
| capability_requirements | 是/否/— | ✅/❌/— | | |
| 分阶段落盘（防 subagent 空返回） | 是/否/— | ✅/❌/— | | |
| phase-产出一致性 | 是/否/— | ✅/❌/— | | |
| P6 evidence（含截图 + 引用 + vision YAML） | 是/否/— | ✅/❌/— | | |
| P2 候选方案 + 权衡（≥2） | 是/否/— | ✅/❌/— | | |
| P8 internal_only_reason | 是/否/— | ✅/❌/— | | |
| dispatch-context.md | 是/否/— | ✅/❌/— | | |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是/否/— | ✅/❌/— | | |
| CI backstop | 是/否/— | ✅/❌/— | | |

## 机制说明

| 机制 | 触发条件 | 协议位置 |
|------|---------|----------|
| retry 记录 | 任何阶段门槛失败（含 subagent 空返回、gate 不通过） | dispatch-protocol.md「重试与上限」 |
| PAUSED | retry 超限、跨 ≥2 阶段回退、不可逆操作需确认 | state-machine.md「转移规则」 |
| PROD_TOUCHED | 开发/测试过程中意外接触生产环境 | dispatch-protocol.md「[PROD_TOUCHED] 标记说明」 |
| SCOPE+ | 任何阶段发现 P1 未覆盖的新隐含需求 | WORKFLOW.md「[SCOPE+]」 |
| SCOPE_RESOLVED | SCOPE+ 处理后追加的确认标记 | check-scope-resolved.sh |
| DESIGN_GAP | P4 implementer 发现 P2 设计有歧义/缺口而自主决策 | implementer.md「[DESIGN_GAP] 偏差声明」 |
| DESIGN_GAP_REVIEWED | 主 Agent 审查 DESIGN_GAP 后追加的确认标记 | check-gate.sh P7 配对检查 |
| NEED_CONFIRM | 实跑结果与 BDD 条件有偏差但不确定是 bug 还是需求理解问题 | verifier.md「何时标 [NEED_CONFIRM]」 |
| CAPABILITY_GAP | 任务需要的能力当前环境无法满足且无补充路径 | task-files.md「能力三态」 |
| gate 验证 | 每个阶段转移前，主 Agent 亲自跑 gate 命令 | state-machine.md「主 Agent 的单步执行」 |
| 阶段产出文件 | 每个阶段产出对应 P{n}-*.md（不裁剪时） | task-files.md |
| .state.yaml phase 同步 | 阶段转移时同步更新 .state.yaml phase 字段 | state-machine.md |
| 裁剪条件 + override | P1 声明裁剪时满足对应阶段的裁剪条件 | check-pruning.sh |
| capability_requirements | P1 识别任务需要的特殊能力并评估当前环境 | analyst.md「能力需求声明」 |
| 分阶段落盘 | subagent 派发时默认启用，防空返回 | dispatch-protocol.md「分阶段落盘」 |
| phase-产出一致性 | 暂存的 P{n}-*.md 产出与 .state.yaml phase 匹配 | pre-commit-gate.sh WARNING |
| P6 evidence | P6 验收的证据文件（截图/日志/JSON）含运行时数据 | check-p6-evidence.sh |
| P2 候选方案 | P2 至少 2 个候选方案 + 权衡 + 选择理由（design_trivial/follows_existing_pattern 除外） | check-gate.sh P2 form check |
| P8 internal_only_reason | 裁剪 P8 时声明 internal_only + 理由字段 | check-pruning.sh |
| dispatch-context.md | 主 Agent 派发前查证的客观信息落盘 | dispatch-protocol.md |
| pre-commit hook | git commit 时自动跑 gate / 状态转移 / 裁剪检查 | pre-commit-gate.sh |
| CI backstop | push 后 GitHub Actions 重跑 gate，捕获 --no-verify 绕过 | ci-gate-backstop.py |
