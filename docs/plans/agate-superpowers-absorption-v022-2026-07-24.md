# v0.22.0 — Superpowers 吸收 + 上下文编排 + 并行执行

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 四条线：(1) 从 superpowers 吸收行为纪律嵌入 subagent 角色文件；(2) 强化上下文编排让 subagent 不从半空白开始；(3) 把已有的专家组并行评审设计落地到阶段卡片；(4) 执行阶段（P3/P4/P5）按包拆分并行。所有改动不增加主 Agent 负担、不暴露 gate 细节、能自动化的自动化。

**Architecture:** 文档层改动为主（角色文件 + dispatch-context 模板 + 阶段卡片），1 个脚本改动（dispatch-context 上游关联自动提取）。纪律嵌入 subagent 侧，主 Agent 按现有流程派发。并行以 P2 packages 拆分为前提，主 Agent 是 orchestrator 不需新角色。

**Tech Stack:** markdown 文档编辑 + 1 个 bash 脚本改动 + bats 测试

---

## 设计原则

1. **不增加主 Agent 负担** — 主 Agent 不多读、不多判断。纪律嵌入 subagent 角色文件或 dispatch-context 模板
2. **能自动化的自动化** — gate 细节不让主 Agent 读太多。上下文编排能脚本提取的不要主 Agent 手写
3. **面向复杂场景** — 原型、复杂交互、系统架构设计、设计模式需要具体方法论
4. **纪律嵌入角色文件** — superpowers 的铁律翻译成"遇到 X 必须做 Y"，subagent 在隔离上下文中读到并遵守
5. **已有设计要落地** — 专家组并行评审在 role-system.md 已设计但阶段卡片没给操作指引，需要落地
6. **并行以拆分为前提** — 执行阶段并行的前提是 P2-design.md 已把改动域拆清（packages 声明多包且互不依赖）。没拆清就不并行，安全第一

---

## 变更清单

### P2.37: architect.md 方案探索方法论

**问题**：architect.md 的"多方案探索"只有结构要求（>=2 候选 + 权衡 + 选择理由），没有方法论。系统架构/复杂交互/原型场景容易锚定第一个方案。

**吸收来源**：superpowers brainstorming——"先探索问题空间再提交方案"、"YAGNI"、"探索替代方案"

**改动**：在 `architect.md` 方法论节新增"方案探索方法论"子节：

```markdown
**方案探索方法论（按场景类型）**

写候选方案前，先判断场景类型，按对应方法论探索：

| 场景类型 | 识别信号 | 探索方法 |
|----------|----------|----------|
| 系统架构 | 多组件交互、数据流跨 N 个边界、状态机复杂 | 画数据流图 → 找瓶颈/单点 → 针对瓶颈设计替代拓扑 |
| 复杂交互 | ui_affected: true + 多步操作 + 状态依赖 | 列用户操作序列 → 找分支/回退/并发冲突 → 针对冲突点设计替代交互模型 |
| 原型/验证 | minimal_validation 字段触发、外部系统依赖 | 先写最小验证（10 行脚本/curl）→ 验证结果决定方案可行性 → 不可行的方案直接排除，不写进候选 |
| 设计模式 | follows_existing_pattern 但模式需适配 | 列 2-3 个候选模式 → 每个模式写 3 行伪代码适配 → 选适配成本最低的 |
| 常规功能 | 无上述信号 | 现有流程（>=2 候选 + 权衡）足够 |

**关键原则**：
- 先探索再写方案——不要想到一个就写一个，先花 2 分钟列 3-5 个可能方向，再选 2 个深入
- 稻草人检测——如果第二个方案的"缺点"只是"不如方案一"，它不是真正的替代方案。真正的替代方案应该在**某些维度上**比方案一更好
- YAGNI——每个候选方案只解决 P1 列出的问题，不预设计未来可能的需求
```

**文件**：`agate/assets/execution-roles/architect.md`

---

### P2.38: investigate.md 结构化诊断流程强化

**问题**：四阶段框架太抽象--"列出所有可能原因按概率排序"变成"列 2 个原因就动手"。P5 失败回退时 implementer 不找根因就修。

**吸收来源**：superpowers systematic-debugging--"没有根因调查就不提出修复方案"、"3+ 次修复失败质疑架构"

**现有内容**（investigate.md 阶段 2/3）：
```
### 阶段 2：分析 - 穷举可能性
- 列出所有可能的原因，按概率排序
- root-cause-tracing 回溯
- 排除法：逐个排查可能原因，排除一个就记一个

### 阶段 3：假设 - 选最可能的原因，先验证再修
- 选出最可能的原因，说明理由
- 验证假设：在修之前先设计一个最小验证步骤
- ⚠️ 临近重试上限时质疑架构
```

**改为**：
```markdown
### 阶段 2：分析 - 穷举可能性

- 列出**至少 3 个**可能原因（防止锚定在第一个想到的原因上）
- 每个原因写一行证据：为什么它可能是根因（不是"感觉像"）
- 按以下优先级排序：
  1. 最近变更引入的（git diff 可验证）
  2. 环境变化导致的（配置/依赖/时序）
  3. 既有代码的边界条件（长期存在但未被触发）
- **排除法必须留痕**：排除一个原因时写"已排除：X，证据：Y"--不留痕的排除不算排除

### 阶段 3：假设 - 选最可能的原因，先验证再修

- 选出最可能的原因，**必须写明**：为什么是它而不是其他候选（一行理由）
- **验证假设**：修之前先设计一个最小验证步骤（debug log / curl / 单独跑一个 test case），确认假设成立再动手
- **禁止"先改一下试试"**：没有验证过的假设不能直接修代码。如果无法设计最小验证步骤，标 `[NEED_CONFIRM]` 交主 Agent
- **3+ 次修复失败**：不再继续在同一层面试修。回溯 P2-design.md 的方案假设，检查是否有隐含前提不成立。若确认架构假设有误，标 `[SCOPE+]` 触发回 P2
```

**文件**：`agate/assets/review-roles/investigate.md`

---

### P2.39: dispatch-prompt.md P4 回退诊断模板自动注入

**问题**：P5->P4 回退时主 Agent 只写"测试失败请修复"，implementer 不诊断直接改。

**改动**：在 `dispatch-prompt.md` 的"阶段特定提示"节新增"P4 回退派发追加"子节：

```markdown
### P4 回退派发追加（P5/P6 失败回退时使用）

\```
## 回退诊断（强制）
本次是从 P5/P6 回退。上次失败信息：{主 Agent 填：哪条测试/BDD 失败 + 失败现象}

修复前必须先诊断根因，按以下流程：
1. 读 P5-test-results/ 或 P6-acceptance.md 的失败详情
2. 列出至少 3 个可能原因 + 每个原因的证据
3. 选最可能的原因，写最小验证步骤确认
4. 确认根因后再修代码

修复产出必须包含：
- P4-diagnosis.md：根因 + 排除项清单（已排除 X，证据 Y）+ 验证步骤
- 代码改动（只修根因，不带入其他改动）

跳过诊断直接修代码 = 门槛不通过。
\```
```

**关键设计**：
- 主 Agent 只需填"哪条测试/BDD 失败 + 失败现象"--一行信息
- 诊断流程由模板自动注入，implementer 在隔离上下文中读到并遵守
- P4-diagnosis.md 是新增产出，gate 不检查（不增加 gate 复杂度），但主 Agent 可在下一轮回退的 dispatch-context 中引用
- "跳过诊断直接修代码 = 门槛不通过"是角色文件层面的纪律声明（nudge），不是 gate 脚本强制--与现有"自查≠gate"同一级别

**文件**：`agate/assets/templates/dispatch-prompt.md`

---

### P2.40: verifier.md 验证纪律

**问题**：T026 事故--verifier 先写 PASS 再找证据。provenance 审计能抓"证据不存在"，但抓不了"证据存在但与结论不对应"。

**改动**：在 `verifier.md` P6 模式的"Hardening 关键约束"节之后新增"验证纪律"子节：

```markdown
### 验证纪律（P6 模式）

**铁律：先验证，后结论。**

每条 BDD 的验收流程：
1. 跑验证命令 / 检查证据 -> 看到客观结果
2. 根据客观结果写 PASS 或 FAIL
3. 引用证据路径

**禁止**：
- 先写 PASS 再找证据（T026 事故模式）
- "应该能过"-> 写 PASS（"应该"不是证据，命令输出才是）
- 复用上一轮验收的结论（每轮验收必须重新验证）

**无法验证的 BDD**：标 `[NEED_CONFIRM]`，不标 PASS。诚实比完整更重要。
```

**文件**：`agate/assets/execution-roles/verifier.md`

---

### P2.41: implementer.md 实现纪律

**问题**：implementer 容易一次写太多代码（超出 P2 范围），或遇到测试不通过时改测试而非改实现。

**现有内容**（implementer.md 认知模式节）：
```
## 认知模式
- 只实现 P2 方案里的东西，不擅自扩大范围
- 让 P3 的红灯测试变绿灯，不改测试去迁就实现
- 每个改动可追溯到设计和测试
- 遵循项目现有代码风格和项目约定文件（CLAUDE.md / AGENTS.md）中的规范
```

**改为**（追加 2 条）：
```markdown
## 认知模式
- 只实现 P2 方案里的东西，不擅自扩大范围
- 让 P3 的红灯测试变绿灯，不改测试去迁就实现
- 每个改动可追溯到设计和测试
- 遵循项目现有代码风格和项目约定文件（CLAUDE.md / AGENTS.md）中的规范
- **最小实现原则**：写最简单的代码让测试通过，不加额外功能、不重构无关代码、不"顺便改进"
- **测试不通过时的决策树**：
  1. 实现有误 -> 修实现
  2. 测试断言与 P1 BDD 矛盾 -> 标 `[DESIGN_GAP]`，不改测试
  3. 测试环境问题（缺依赖/端口占用）-> 标 `[CAPABILITY_GAP]`，不降级验证
  4. 不确定是 1 还是 2 -> 按 investigate.md 诊断，不猜
```

**文件**：`agate/assets/execution-roles/implementer.md`

---

### P2.42: dispatch-context 上游关联自动提取脚本

**问题**：subagent 从半空白上下文开始的根因--主 Agent 只拿到 subagent 的"路径+一句话摘要"（铁律 3），上游关联节经常只有一句话。下一个 subagent 读不到足够的上游信息。

**核心矛盾**：铁律 3（只返回摘要）是上下文隔离的保证，不能放松。但摘要信息量不够，下一个 subagent 需要更多上游关联。

**解决方案**：不是让主 Agent 多写，也不是让 subagent 多返回--而是**脚本自动从上游产出文件提取结构化字段**，直接写入 dispatch-context 的上游关联节。

**吸收来源**：superpowers subagent-driven-development 的"给子 agent 提供完整任务文本+上下文"--但 agate 不能传全文（铁律 2），所以用**结构化提取**替代全文传递。

**改动**：新增 `agate/scripts/agate-extract-context.sh`，主 Agent 在写 dispatch-context 时调用：

```bash
# 用法 1：直接写入 dispatch-context 的上游关联节（推荐）
bash $AGATE_ROOT/scripts/agate-extract-context.sh P4 $TASK_DIR --write
# 直接将提取结果追加到 dispatch-context 上游关联节

# 用法 2：输出到 stdout（调试用）
bash $AGATE_ROOT/scripts/agate-extract-context.sh P4 $TASK_DIR
# 输出 markdown 片段，供主 Agent 审阅
```

**`--write` 模式设计**：脚本直接追加到 `P{N}-dispatch-context-{role}.md` 的 `### 上游关联` 节末尾。主 Agent 不需要读取输出再粘贴--**零阅读量增加**，只增加一个 bash 调用。如果主 Agent 需要审阅提取结果，用 stdout 模式。

**提取规则**（按阶段，只提取 grep/sed 可靠提取的结构化字段）：

| 目标阶段 | 提取来源 | 提取内容 | 提取方式 |
|----------|----------|----------|----------|
| P1 | P0-brief.md | task + known_risks + env_constraints | YAML 字段提取 |
| P2 | P1-requirements.md | domains + risk_level + BDD 编号列表（`#### BDD-NN` 标题） | grep `^domains:` / `^risk_level:` / `^#### BDD-` |
| P3 | P2-design.md | ui_affected + gate_commands + packages | grep 结构化字段 |
| P4 | P2-design.md + P3-test-cases.md | files_to_read + packages + BDD 编号列表 | grep 结构化字段 + `^#### BDD-` |
| P5 | P2-design.md + P4-implementation.md | gate_commands + implementation_dir | grep 结构化字段 |
| P6 | P1-requirements.md + P5-test-results/ | BDD 编号列表 + failed count（从 unit.md grep `failed` 行） | grep `^#### BDD-` + grep failed。**注**：failed count 仅供 P6 verifier 上下文参考，gate 以主 Agent 实跑为准（C7 规则：subagent 自报不可信） |
| P7 | P2-design.md + P6-acceptance.md | packages + PASS/FAIL 计数（`grep -c`） + DESIGN_GAP 列表 | grep 结构化字段 + 计数 |
| P8 | P2-design.md + P7-consistency.md | packages + BLOCKER 计数 + DEVIATION 列表 | grep 结构化字段 + 计数 |

**关键设计**：
- **只提取结构化字段**（YAML 字段、grep 可匹配的标记行、计数）--不提取自由文本摘要。"选中方案摘要"不是结构化字段，已从提取规则中移除
- `--write` 模式直接写入 dispatch-context 文件，主 Agent 零阅读量增加
- 提取脚本不替代主 Agent 的判断--主 Agent 仍可补充/修改
- 回退场景：提取脚本自动检测 gate-diagnosis.md 是否存在，存在则追加引用路径

**为什么不是"专门 subagent 制造上下文"**：引入新角色（context-curator）会增加流程复杂度。当前用脚本提取结构化字段足够--能自动化的自动化。如果后续发现结构化提取不够（需要语义提炼），再考虑派 context-curator subagent。

**实施约束**：先写 bats 测试（含 fixture 产出文件），再写提取逻辑，确保每条提取规则可验证。

**文件**：新增 `agate/scripts/agate-extract-context.sh` + `agate/tests/unit/agate-extract-context.bats`

---

### P2.43: 阶段卡片落地并行执行操作指引（评审 + 执行阶段）

**问题**：
- 评审并行：role-system.md:166-190 已设计专家组并行评审 + 组长汇总，但阶段卡片只写了一行，主 Agent 不知道怎么并行派发
- 执行阶段并行：dispatch-protocol.md:601 已写"任务间有依赖时串行，无依赖时并行"，但没有操作指引。P3/P4/P5 按包拆分并行天然安全（各写不同文件/目录），但主 Agent 默认串行

**并行安全分析**：

| 阶段 | 并行场景 | 文件冲突 | 基础设施冲突 | 安全性 |
|------|---------|---------|-------------|--------|
| P2/P4 评审 | 多角色各写 P{N}-review-{role}.md | 无 | 无（评审不启动服务） | ✅ 安全 |
| P3 TDD | 多包各写各的测试文件 | 无 | 低（测试不启动服务） | ✅ 安全 |
| P4 实现 | 多包各写各的代码目录 | **有**——共享类型/接口 | **有**——debug server 端口/测试数据库 | ⚠️ 需约束 |
| P5 验证 | 多包各跑各的测试 | 无 | **有**——测试端口/数据库/临时文件 | ⚠️ 需隔离 |
| P6 验收 | 多包各验各的 BDD | 无 | **有**——验收端口/截图目录 | ⚠️ 需隔离 |

**基础设施隔离维度**：

| 维度 | 冲突场景 | 隔离方案 |
|------|---------|---------|
| 端口 | 两个 implementer 同时启动 debug server 抢 3000 端口 | 每个 subagent 分配不同端口（dispatch-context 约束节写明） |
| 数据库 | 两个 verifier 写同一个 test.db | 每个 subagent 用独立数据库路径/名称 |
| 临时文件 | 两个 verifier 写 /tmp/test-output.log | 每个包用 `P5-test-results/{pkg}/` 独立目录 |
| 浏览器 | 两个 E2E 测试同时操作同一浏览器实例 | Playwright 默认隔离（独立 browser context），但端口仍需区分 |
| 环境变量 | 两个 subagent 的 .env 覆盖 | 每个 subagent 的 dispatch-context 写明独立的环境变量值 |

**改动**：

**1. dispatch-protocol.md 拆分原则新增包级并行维度**

现有拆分原则（dispatch-protocol.md:598-603）只覆盖"按产出文件拆分"（每个任务产出 1-3 个文件）。包级并行是不同的拆分维度（同一阶段的多个 subagent 同时工作，各写不同目录）。在拆分原则节末尾新增：

```markdown
**按包拆分并行（与按产出拆分正交）**：
- 当 P2 声明 `packages: [pkg-a, pkg-b, ...]` 且包间无数据依赖时，同一阶段可派多个 subagent 并行（每个包一个）
- 包级并行的操作指引在阶段卡片（P3/P4/P5/P6）的"按包拆分并行"节，phase card 是包级并行的权威来源
- 包级并行不改变拆分原则的其他条目（产出文件数/输入文件数限制仍适用于每个并行 subagent）
```

**2. P2/P4 阶段卡片扩展评审并行操作指引**

P2-design.md 评审派发节改为：
```markdown
## 评审派发（C8 机械映射 + 专家组并行）

按 P1 声明的 domains + risk_level 机械映射评审（见 review-mapping.md）。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review -> P2-review-eng.md
   - plan-design-review -> P2-review-design.md
   - plan-ceo-review -> P2-review-ceo.md
   - cso -> P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER -> status: rejected
   - 多位专家分歧 -> 标「专家组分歧」交人工
   - 全票无 BLOCKER -> status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。
```

P4-implementation.md 评审派发节同理扩展。

**3. P3/P4/P5/P6 阶段卡片新增"按包拆分并行"节**

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

**P3-tdd.md 新增**：
```markdown
## 按包拆分并行（可选）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

当 P2 声明多个 packages 且包间无数据依赖时，P3 可拆分并行：

1. 每个 package 派一个 test-designer subagent
2. 各自写各自的测试文件（不同目录）
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit

拆分判据：
- P2 packages > 1 且包间无数据依赖 -> 可并行
- 单包或包间有依赖 -> 串行（不拆分）
- P2 未声明 packages -> 串行

每个 subagent 的 dispatch-context 必须明确其负责的 package 范围（约束节写"只写 {pkg} 目录下的测试"）。
```

**P4-implementation.md 新增**：
```markdown
## 按包拆分并行（可选，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**--跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 -> 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 -> 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前应确认每个 subagent 的 dispatch-context 已包含上述隔离参数。**注意**：这是 nudge 不是强制规则（无 gate 脚本检查），与 design_trivial 的形式义务同级。未分配隔离参数的后果是运行时冲突（端口占用/数据库锁），由 subagent 报错暴露。
```

**P5-verification.md 新增**：
```markdown
## 按包拆分并行（可选）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

当 P2 声明多个 packages 时，P5 可按包拆分并行--各 verifier subagent 跑各包的 gate_commands，各写 P5-test-results/{pkg}/。

拆分判据同 P3。P5 是只读验证，无代码写冲突风险。

**基础设施隔离（并行时强制）**：
- 测试端口：各 verifier 使用独立端口（与 P4 并行时分配的端口一致，或新分配）
- 测试数据库：各 verifier 用独立数据库（与 P4 隔离方案一致），不共享同一 test.db
- 临时输出：各 verifier 写入 `P5-test-results/{pkg}/` 独立目录，不共享同一 unit.md
- E2E 浏览器：Playwright 默认隔离 browser context，但若 E2E 测试启动了本地 server，各 verifier 需用不同端口

主 Agent 在并行派发前应确认每个 verifier 的 dispatch-context 已包含独立的基础设施参数（nudge，同 P4）。
```

**P6-acceptance.md 同理新增按包拆分并行指引**，基础设施隔离要求与 P5 一致（验收端口、截图目录 `P6-evidence/{pkg}/` 独立）。

**为什么 P4 并行要额外约束**：P4 是唯一有写冲突风险的阶段。多个 implementer 同时改同一个共享文件（如 `types.ts`、`config.py`）会导致 git 冲突。解决方案是**dispatch-context 约束节显式限定每个 implementer 的改动范围**——这和现有的 files_to_read 机制一致，只是从"读什么"扩展到"改什么"。

**为什么不需要 subagent-orchestrator 新角色**：agate 的主 Agent 本身就是 orchestrator。并行 subagent 各自返回路径+摘要，主 Agent 汇总后统一 commit——这和专家组评审的模式完全一致。增加新角色只会让流程更重。

**文件**：`agate/phase-cards/P2-design.md`、`agate/phase-cards/P3-tdd.md`、`agate/phase-cards/P4-implementation.md`、`agate/phase-cards/P5-verification.md`、`agate/phase-cards/P6-acceptance.md`

---

### P2.44: loop-orchestration.md 并行执行状态更新

**改动**：更新 loop-orchestration.md 的"已知改进项"节：

```markdown
**1. 并行执行**

- ✅ **评审并行已落地**（v0.22.0）：P2/P4 多评审角色可同时派发，各写不同产出文件，组长汇总。见 P2/P4 阶段卡片。
- ✅ **执行阶段按包拆分并行已落地**（v0.22.0）：P3/P4/P5 当 P2 packages > 1 且包间无依赖时可拆分并行。P4 需额外约束（各 implementer 只改自己 package 目录）。见 P3/P4/P5 阶段卡片。
- ❌ **跨任务并行未落地**：多个独立任务（Txxx-a, Txxx-b）同时执行。需要每个任务独立的 .state.yaml + git 工作区隔离（worktree 或独立分支）。当前多任务 hook 已支持（扫描所有暂存的 .state.yaml），但主 Agent 串行推进任务。待 v0.23.0+ 设计讨论。
```

**文件**：`agate/loop-orchestration.md`

---

## 不做的事

| 候选项 | 不做理由 |
|--------|----------|
| 主 Agent 红旗信号表 | 增加主 Agent 负担 |
| brainstorming skill 整体引入 | 太重，依赖交互式对话 |
| writing-plans skill 引入 | P2-design.md 已是结构化执行计划 |
| context-curator subagent | 当前用脚本提取结构化字段足够；语义提炼需求出现时再考虑 |
| P4-diagnosis.md gate 检查 | 不增加 gate 复杂度 |
| 新增 gate 脚本强制诊断 | gate 细节不让主 Agent 读太多 |
| subagent-orchestrator 新角色 | 主 Agent 本身就是 orchestrator，新角色增加流程复杂度 |
| 跨任务并行（Txxx-a/Txxx-b 同时跑） | 需 git 工作区隔离（worktree/独立分支），当前多任务 hook 已支持但主 Agent 串行推进，留待 v0.23.0+ |

---

## 文件变更汇总

| 文件 | 变更类型 | 内容 |
|------|----------|------|
| `agate/assets/execution-roles/architect.md` | 修改 | 方法论节新增"方案探索方法论"子节 |
| `agate/assets/review-roles/investigate.md` | 修改 | 阶段 2/3 强化（≥3 原因、排除留痕、禁止先改试试、3+ 失败质疑架构） |
| `agate/assets/templates/dispatch-prompt.md` | 修改 | 新增 P4 回退派发追加模板 |
| `agate/assets/execution-roles/verifier.md` | 修改 | P6 模式新增验证纪律子节 |
| `agate/assets/execution-roles/implementer.md` | 修改 | 认知模式节强化（最小实现 + 测试不通过决策树） |
| `agate/scripts/agate-extract-context.sh` | **新增** | dispatch-context 上游关联自动提取（支持 --write 直接写入） |
| `agate/tests/unit/agate-extract-context.bats` | **新增** | 提取脚本测试 |
| `agate/dispatch-protocol.md` | 修改 | 拆分原则新增"按包拆分并行"维度 |
| `agate/phase-cards/P2-design.md` | 修改 | 评审并行操作指引 |
| `agate/phase-cards/P3-tdd.md` | 修改 | 按包拆分并行操作指引 |
| `agate/phase-cards/P4-implementation.md` | 修改 | 评审并行 + 按包拆分并行操作指引（含共享文件约束） |
| `agate/phase-cards/P5-verification.md` | 修改 | 按包拆分并行 + 基础设施隔离操作指引 |
| `agate/phase-cards/P6-acceptance.md` | 修改 | 按包拆分并行 + 基础设施隔离操作指引 |
| `agate/loop-orchestration.md` | 修改 | 并行执行状态更新（评审+执行阶段已落地，跨任务未落地） |
| `docs/hardening-roadmap.md` | 修改 | v0.22.0 版本计划新增 P2.37-P2.44 |

---

## 测试计划

- P2.37-P2.41/P2.43-P2.44：文档改动，无新增 bats。验证：`bats agate/tests/` 全通过 + consistency 0 ERROR
- P2.42：新增 `agate-extract-context.sh` + `agate-extract-context.bats`，测试各阶段提取规则

验证：
1. `bats agate/tests/` 全通过
2. `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR
3. `shellcheck -S warning agate/scripts/*.sh` clean
4. 人工审阅角色文件/阶段卡片内容

---

## 自审

1. **Spec 覆盖**：8 项变更全覆盖（5 项行为纪律 + 1 项上下文编排 + 1 项并行执行落地 + 1 项状态更新）
2. **占位符扫描**：无 TBD/TODO；P2.38-P2.41 已内联完整改动内容，无"见前版"引用
3. **一致性**：agate-extract-context.sh 命名与 agate-next-card.sh/agate-inject-card.sh 一致；P2-review-eng.md 等产出命名与现有 P2-review.md 模式一致；按包拆分在 dispatch-protocol.md 拆分原则新增维度，phase card 为操作权威来源
4. **主 Agent 负担**：P2.42 --write 模式直接写入 dispatch-context，零阅读量增加；P2.43 并行操作减少判断（按卡片执行）；**诚实标注**：包间依赖分析、共享文件识别、基础设施参数分配是判断性工作（非机械检查），隔离参数检查是 nudge 不是强制规则（无 gate 检查，运行时冲突由 subagent 报错暴露）
5. **gate 暴露**：零新增 gate 逻辑；P4-diagnosis.md 不进 gate；并行产出文件（P2-review-eng.md 等）不被 gate 检查
6. **并行风险**：评审并行安全（各写不同文件）；P3 TDD 并行安全（各写不同文件）；P4 实现并行有约束（dispatch-context 限定改动范围 + 主 Agent 统一处理共享文件 + 基础设施隔离参数）；P5/P6 验证并行有基础设施隔离约束
7. **提取规则可验证性**：P2.42 只提取结构化字段（YAML 字段/grep 标记行/计数），不提取自由文本摘要；实施时先写 bats 测试再写提取逻辑

## R1 评审修复记录

| 评审项 | 级别 | 修复 |
|--------|------|------|
| B1-P2.38-41 内容缺失 | BLOCKING | 内联 P2.38/39/40/41 完整改动内容（含现有内容对比） |
| B2-选中方案摘要不可提取 | BLOCKING | 移除提取规则中的选中方案摘要，只保留 grep 可提取的结构化字段 |
| B6-dispatch-protocol.md 拆分原则 | NEEDS_FIX | P2.43 新增 dispatch-protocol.md 拆分原则更新（包级并行维度） |
| B3-P2.42 不增加阅读量 | NEEDS_FIX | 脚本新增 --write 模式直接写入 dispatch-context，零阅读量 |
| B7-最后一个返回 implementer 竞态 | NEEDS_FIX | 改为主 Agent 在所有并行 implementer 返回后统一处理共享文件 |
| B2-BDD 映射不可靠 | NEEDS_FIX | 降级为提取 BDD 编号列表（grep BDD- 标题） |
| B3-负担评估不准确 | NEEDS_FIX | 自审第 4 点诚实标注包间依赖/共享文件/参数分配是判断性工作 |
| B7-隔离参数检查是 nudge | NEEDS_FIX | P4/P5 卡片标注这是 nudge 不是强制规则与 design_trivial 同级 |
| S1-dispatch-context 注入膨胀 | SUGGESTION | 并行节加仅当 P2 packages > 1 时适用前缀单包任务快速跳过 |
| S2-P2.42 --write 模式 | SUGGESTION | 已采纳脚本支持 --write 直接写入 |
| S3-提取规则实现细节 | SUGGESTION | 已采纳实施时先写 bats 测试再写提取逻辑 |
