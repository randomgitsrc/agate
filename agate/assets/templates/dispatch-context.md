> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: {P1-P8}
generated_by: agate-inject-card.py + 主 Agent
task_id: {Txxx}
role: {角色名，如 analyst / requirements-review / implementer}
---

> **本文件既是手工注入的骨架（`agate-inject-card.py`），也是渲染时注入的模板
> （`agate-dispatch.py`）**。渲染路径（`agate-dispatch.py {phase} {role} [TASK_DIR]`）读本模板
> 渲染写 `{phase}-dispatch-context-{role}.md`：frontmatter `generated_by` 改写为
> `agate-dispatch.py + 主 Agent`（机器来源字段），并在卡片块前（START 标记行之上）注入
> 单行「CARD-SOURCE 来源注释」（HTML 注释，块外，不进入 START..END 抽取区间）。手工路径保持现状。

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
{一句话：本角色在本阶段要产出什么（渲染时注入：agate-dispatch.py [--guide FILE] 时替换为 guide 首行）}

### 约束
{从 P0-brief env_constraints/known_risks + 上游产出 + 协议知识提取。写的是"必须满足什么/不能做什么"，不是"应该怎么做"——后者是 subagent 的自主决策空间}

> **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（被 provenance 预判检测匹配）。改用"通过/失败"或加引号。

> **子派发能力声明位（RM-AG0055 / TAG0028）**：执行角色（analyst/architect/implementer/
> verifier）可被授予子派发权限（边界见 role-system.md「子派发权限边界」节）；**judge 类
> 角色不适用子派发**——judge 派发时本行注入「不启用子派发能力」，其余角色留空或按需声明。
> 声明位：`子派发能力：{启用（执行角色，按需）| 不启用子派发能力（judge 类角色）}`

### 上游关联
{上一阶段 subagent 摘要中的关键信息}

### 输入文件
- {AGATE_WORKSPACE}/tasks/{Txxx}/P0-brief.md（主 Agent 的任务简报和风险声明）
- {AGATE_WORKSPACE}/tasks/{Txxx}/{上一阶段产出文件}
- {project_conventions_file}（项目约定）
{按角色定义补充其他需要读的文件}

### 产出文件字段
用 `FILE={产出文件路径} agate-md-field-set --list` 查看本阶段应填字段；`FILE={产出文件路径} agate-md-field-set <key> <value>`
逐个写入；写入失败照错误提示修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。
</dispatch_guide>

<!-- 卡片块前（本行与 START 之间）为渲染路径来源标记注入区：agate-dispatch.py 渲染时
     在此行注入单行来源注释（HTML 注释，内容以 CARD-SOURCE 开头），置于 START 行之上——
     不进 START..END 抽取区间（pre-commit 2p hash 不受影响）；手工路径无此行 -->
<!-- AGATE_CARD_START -->
{卡片占位：手工路径由 agate-inject-card.py 注入 next-card stdout；渲染路径由
 agate-dispatch.py 在渲染时直接嵌入 next-card stdout——START..END 区间内与
 agate-next-card.py {P1-P8} 输出逐字一致（pre-commit 2p hash 校验锚点）}
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：{服务运行状态、版本号}
- 关键标识：{URL、API 端点、文件 ID、DOM 选择器}
- 查证结果：{grep/命令输出摘要}
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
