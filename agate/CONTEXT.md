# agate 术语表 + 上下文

> 统一定义 agate 协议中的关键术语。定义的权威来源是各协议文件，本表是补充入口。
> 新读者（或审查 subagent）可从此处快速理解术语，再按"首次定义位置"回溯详情。

## 术语表

| 术语 | 定义 | 首次定义位置 |
|------|------|------------|
| gate | 阶段门槛检查，由脚本 exit code 判定通过(0)/不通过(1)/需人工判断(2) | WORKFLOW.md |
| 裁剪 | 跳过某个阶段，须在 P1 裁剪说明里写明理由 | WORKFLOW.md §可裁剪的阶段 |
| 机制交叉 | ≥2 个子系统交互、时序依赖、跨层影响的改动 | WORKFLOW.md §改动性质判断 |
| 声明性改动 | 不改变程序运行时控制流的改动（改前改后控制流相同） | WORKFLOW.md §改动性质判断 |
| 行为逻辑改动 | 改变程序运行时控制流的改动（条件分支、状态转换、数据处理） | WORKFLOW.md §改动性质判断 |
| BDD | Behavior-Driven Development，Given/When/Then 格式的验收条件 | WORKFLOW.md §需求基线 |
| NEED_CONFIRM | 需人工确认的标记，subagent 拿不准方向时标注 | WORKFLOW.md §[NEED_CONFIRM] |
| SCOPE+ | 新发现的隐含需求标记，任何阶段 subagent 可标注，主 Agent 增补 P1 基线 | WORKFLOW.md §[SCOPE+] |
| SCOPE_GAP | 主 Agent 派发 prompt 漏了 P2 已声明的改动，subagent 标注 | dispatch-protocol.md |
| C8 域 | role-system.md 定义的协作域，命中时触发 P2/P4 评审 | role-system.md |
| agent 字段 | 阶段产出文件 Header 的角色标识（如 `agent: verifier`），`agent=main` 表示自审 | orchestrator-template.md |
| gate exit code | 0=通过，1=不通过，2=需人工判断 | check-gate.sh |
| PAUSED | 任务暂停状态，需人工介入后才能继续。不是失败，是正确路由 | state-machine.md |
| READY | 任务完成所有 gate、准备发布的状态。实际发布由人手动触发 | state-machine.md |
| dispatch-context | 派发前主 Agent 写的核心信息源，含派发指引（目标/约束/上游关联/输入文件）+ 阶段卡片 + 客观查证信息。文件名 P{N}-dispatch-context-{role}.md，每个 subagent 一个。禁止含 PASS/FAIL 预判 | dispatch-protocol.md |
| PROD_TOUCHED | subagent 意外接触生产环境时标注的标记，触发 PAUSED | dispatch-protocol.md |
| DESIGN_GAP | P4 实现中发现的设计偏差声明，须在 P7 被转抄 + 配对 DESIGN_GAP_REVIEWED | state-machine.md |
| 自审 | agent=main 的评审，被 check-gate.sh 硬拦截（exit 1） | orchestrator-template.md |
| 裁剪说明 | P1-requirements.md 中声明跳过阶段及理由的节 | WORKFLOW.md §可裁剪的阶段 |
| 风险等级 | P1 声明的 risk_level 字段（low/medium/high），影响裁剪和评审触发 | WORKFLOW.md §裁剪风险维度 |
