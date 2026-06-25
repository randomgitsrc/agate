---
type: review
source: agate v1.2.0 P0-brief 设计
trace_id: agate-p0-brief-design-review-2026-06-25
created: 2026-06-25
status: draft
reviewer: 主 Agent (实战来源：peekview T020-T027 5 个 P0 brief 立项)
---

# 评审：agate v1.2.0 P0-brief 设计

> 评审对象：agate v1.2.0 的 P0-brief 规范（dispatch-protocol.md:155-189, task-files.md:66-99）
> 实战参考：peekview 项目的 5 个近期 P0 brief（T020 svg-codeblock-viewer / T021 zen-mode / T022 diagram-renderer-refactor / T023 page-basics / T024-T027 路由批任务）
> 评审者立场：agate 是通用框架，peekview 是其中一个实战项目。本 review 的所有改进建议**针对通用设计**，不为 peekview 优化。

## 总体评价

agate v1.2.0 的 P0-brief 设计**骨架合理、扩展自由，但边界模糊**。

**骨架合理（70 分）**：
- 5 字段最小不变量（task / known_risks / executor_env / env_constraints / pruning_tendency）能保证 subagent 启动的最低信息量
- "主 Agent 不可省略 P0-brief" 的硬约束（dispatch-protocol:159）从 T005/T006 教训中沉淀，是关键设计
- 强调"主 Agent 是 PM 视角"（task-files:69-70）准确把握了 P0 性质

**扩展自由（10 分）**：
- 5 字段模板**没禁止扩展**（dispatch-protocol:162-173 的 YAML 块没写"必须只含此字段"）
- 实战项目**普遍扩展**（peekview T020-T027 都有 user_decisions / coordination / 范围声明 等扩展章节）
- agate 不禁止扩展是正确选择

**边界模糊（-30 分）**：
- P0 与 P1 的职责边界**没说清楚**——"用户决策"是 P0 的"决策记忆"还是 P1 的"需求复述"？无指引
- "task = 一句话" 硬约束在复杂任务上不实用（实战 T027 一句话 80 字仍不够）
- 扩展章节缺少**官方模板**（实战都扩展但格式各自发挥）
- "扩展是允许的还是容忍的"在文档中**无明确表态**

## 逐项评估

### ✅ 做得对（建议保留）

#### 1. 5 字段最小不变量设计

**证据**：dispatch-protocol.md:175-181 的 5 项自查清单
**实战验证**：peekview 5 个 brief 全部包含 5 字段，subagent 派发时拿到 P0 即可开工
**判断**：✅ 5 字段是"必要条件"，不是"充分条件"。设计正确。

#### 2. 主 Agent 不可省略 P0-brief（硬约束）

**证据**：dispatch-protocol.md:159 "主 Agent 首先必须写 P0-brief.md，然后再派发任何 subagent"
**教训来源**：T005/T006（dispatch-protocol:189-191 引用）
**判断**：✅ 硬约束正确。T005/T006 教训是真实痛点。

#### 3. "主 Agent 是 PM 视角" 的定位

**证据**：task-files.md:69 "P0-brief 是主 Agent 作为 PM 在派发任何 subagent 之前写的判断文件"
**实战验证**：peekview P0 brief 的"用户决策"段是 PM 视角（决策记忆），不是 analyst 视角（需求分析）
**判断**：✅ 定位准确。P0 是"决策记忆的标准化输出"，P1 是"需求基线"。

#### 4. debug_env 从项目约定（CLAUDE.md）读取

**证据**：dispatch-protocol.md:179, task-files.md:90
**实战验证**：peekview 5 个 brief 的 debug_env 都引用了项目约定（`make debug`、vitest、vue-tsc 等）
**判断**：✅ 强制从项目约定读取，避免 subagent 乱选测试方式。

### ⚠️ 待优化（建议改进）

#### 5. P0 与 P1 的职责边界没说清楚

**问题**：
- P0 brief 包含"用户决策"段（实战 peekview 5 个 brief 都有）
- P1 analyst 写 P1-requirements.md 时，是否重写这些决策？
- 现有规范**没有指引**——可能重复劳动（重写）或丢失（不重写）

**证据**：
- dispatch-protocol.md:160 "P1 analyst 以此为输入做需求质疑和 BDD"
- task-files.md:105-146 P1-requirements.md 模板包含"需求复述"、"隐含需求识别"
- 但**没说明 P0 已有的"用户决策"是否需要在 P1 重写**

**实战观察**：
- peekview T020/T021 的 P0 brief 都有"用户决策"段
- T020/T021 后续 P1 阶段我没看到，所以**实战是否重写未知**
- 但**从 P1-requirements.md 模板看**（"需求复述"段），倾向重写

**改进建议**：

在 dispatch-protocol.md:160 后或 task-files.md P1 模板前加一段**"P0/P1 职责边界"**：

```markdown
## P0 / P1 职责边界

P0 brief 是"主 Agent 决策记忆"（不可重写的现状）：
- task / known_risks / executor_env / env_constraints / pruning_tendency
- 5 字段是 subagent 启动的**必要条件**

P0 brief 可扩展（建议）：
- user_decisions（PM 视角的用户已确认决策）
- coordination（与其他任务的依赖关系）
- 验收条件（PM 视角的验收基线）

P1 analyst 写 P1-requirements.md 时：
- **需求复述**：引用 P0 的 user_decisions（不重写）
- **隐含需求识别**：基于 P0 的 known_risks 扩展（不重复）
- **BDD 验收条件**：基于 P0 的验收条件**形式化**为 Given/When/Then（不重写内容，只改格式）
- **待确认清单**：P0 没解决的开放问题
- **裁剪说明**：基于 P0 的 pruning_tendency 细化
- **范围声明 / 能力需求**：P1 analyst 自己的产出
```

**优先级**：🟠 中（影响每个任务的 P1 阶段产出质量）

#### 6. "task = 一句话" 硬约束在复杂任务上不实用

**问题**：
- dispatch-protocol.md:164 "task: {一句话描述这个任务是什么}"
- dispatch-protocol.md:176 "task：是否是工程视角的一句话描述"
- task-files.md:76 "task: 一句话描述任务（工程视角，不是产品语言）"
- **三处规定"一句话"**

**实战观察**：

| Task | 一句话尝试 | 字数 | 信息完整度 |
|------|----------|------|----------|
| T023 page-basics | "删 17 行僵尸 HomeView.vue + 加 4 行 catch-all 404 路由" | 28 字 | ✅ 够 |
| T024 landing-page | "把 `/` 从 EntryListView 改为新 LandingView，EntryListView 路由迁到 `/explore`，已登录用户访问 `/` 自动跳 `/explore`" | 60 字 | ⚠️ 勉强 |
| T025 user-page | "加 `/users/:username` 路由复用 EntryListView + 后端 `list_entries` 接 `owner=username`（User join）+ EntryListView 接受 `owner` prop + tab URL 同步 + 卡片 `@username` 包 router-link" | 90 字 | ❌ 长 |
| T027 share-link | "为 private entry 实现"临时分享链接"功能（路径 C，非密码）—— 后端 `entry_shares` 表 + 3 端点（生成/列表/批量撤销）+ private→public 自动撤销；前端 EntryDetailView owner 视角加分享管理面板（生成对话框 + 列表 + 勾选批量撤销）；访问 `?share={token}` 凭 16 字符密码学 token 即可（无需登录）" | 130 字 | ❌ 不可能一句话 |

**判断**：**"一句话"约束在 T023 这种小活上合理，在 T027 这种复杂任务上强制执行会损失信息**。

**改进建议**：

修改 task-files.md:76 和 dispatch-protocol.md:164/176 的措辞：

```diff
- task: "一句话描述任务（工程视角，不是产品语言）"
+ task: "任务核心描述（工程视角）。小任务可一句话；复杂任务用 1 段话列关键改动端 + 涉及技术栈。"

- task: {一句话描述这个任务是什么}
+ task: {任务核心描述}

- task：是否是工程视角的一句话描述
+ task：是否是工程视角的核心描述（小任务一句话即可，复杂任务允许 1 段话列关键改动）
```

**优先级**：🟡 低（实战中主 Agent 会自己处理，但措辞硬化会让 P0 评估变纠结）

#### 7. P0 模板与自查清单不一致（事实错误）

**问题**：

dispatch-protocol.md:162-173 的 P0 模板（YAML 块）**没有 `executor_env` 段**：

```yaml
task: {一句话描述这个任务是什么}
known_risks:
  - {已知风险1}
env_constraints:
  debug_env: {路径/命令}
pruning_tendency: {保守/激进 + 理由}
phase_hint: [P1, P2, ..., P8]
```

但 dispatch-protocol.md:178 自查清单**要求 executor_env 4 子项**：
> executor_env：platform/has_task_tool/has_local_runtime/network 四项都要填实际值，不是占位符

而 task-files.md:83-87 的 P0 模板**有 executor_env 段**：

```yaml
executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
```

**两个模板不一致**：
- dispatch-protocol.md 模板：4 字段
- task-files.md 模板：5 字段（含 executor_env）
- dispatch-protocol.md 自查清单：要求 5 字段

**实战观察**：peekview 5 个 brief 都按 task-files.md 模板（5 字段），自查清单通过。

**改进建议**：

dispatch-protocol.md:162-173 的 YAML 块补 executor_env 段：

```yaml
executor_env:
  platform: {opencode | claude-code | codex | claude-project}
  has_task_tool: true
  has_local_runtime: true
  network: {full | restricted}
```

**优先级**：🔴 高（这是事实错误，不修会让 P0 模板不可信）

#### 8. 扩展章节缺少官方模板

**问题**：
- 实战 peekview 5 个 brief 都扩展了 4-6 个章节（user_decisions / coordination / 范围声明 / 验收条件 / 预期成果 / 行为保真策略）
- 但 **task-files.md 的 P0 模板只列了 5 字段**，没给扩展模板
- 各项目扩展格式**各自发挥**（T020 是 7 段、T021 是 9 段、T023-T027 是 8-10 段）

**实战影响**：
- 扩展内容有价值（避免 P1 重做 1-2 小时讨论）
- 但**格式不统一**让 reader 解析成本高

**改进建议**：

在 task-files.md P0 模板后加**"扩展章节（可选）"**子节，给出官方推荐：

```markdown
## P0 brief 扩展章节（可选，但推荐）

P0 brief 是 subagent 启动的"决策记忆"载体。5 字段是必要条件，扩展章节是充分条件。
以下扩展章节是实战验证有价值的，**不是必须但强烈推荐**：

### user_decisions
PM 视角记录已与用户确认的关键决策，避免 P1 重做讨论。
格式：编号列表 + 一句话说明 + 决策理由（可选）

### coordination
与其他任务（已进行中或计划中）的依赖和时序约束。
格式：依赖任务列表 + 协调说明

### 范围声明
本任务做 / 不做的明确边界。
格式：do 列表 + don't 列表

### 验收条件
PM 视角的验收基线（形式化 BDD 在 P1）。
格式：可量化条件列表（"X 时 Y 应 Z"）

### 预期成果
任务的 metric 指标（行数、覆盖率、test 数量等）。
格式：表格（当前 vs 目标）
```

**优先级**：🟡 低（实战中主 Agent 会自己扩展，但官方模板能减少格式不一致）

#### 9. P0 扩展内容与 P1 重复的风险

**问题**：
- P0 brief 包含"验收条件"（实战）
- P1 analyst 写 P1-requirements.md 的 BDD 段（Given/When/Then）也写验收条件
- **是否重复？** 现有规范没说

**实战风险**：
- 如果 P1 重写：浪费 30 分钟
- 如果 P1 不重写：违反 P1 模板"独立产出"原则
- 如果 P1 引用 P0：需要在 P1 模板里明确"可引用 P0 段"

**改进建议**：

task-files.md P1 模板"需求复述"段加引用指引：

```markdown
## 1. 需求复述
（用结构化语言重写原始需求）

**注**：P0 brief 的 `## user_decisions` 段是 PM 视角的决策记忆。需求复述**引用** P0 决策（不重写内容），如需扩展则在 P1 增补。
```

**优先级**：🟠 中（影响每个任务的 P1 阶段产出质量与效率）

#### 10. "占位符"判定不明确

**问题**：
- dispatch-protocol.md:181 "任一字段为空占位符状态 → 补完再继续"
- 但**没定义"占位符"是什么**

**例子**：
- platform: "opencode" → 实际值，不是占位符 ✅
- platform: "TBD" → 占位符 ❌
- platform: "" → 占位符 ❌
- platform: "opencode（待确认）" → 是占位符还是实际值？模糊

**实战观察**：peekview 5 个 brief 的字段都填了实际值，无占位符问题。

**改进建议**：

在 dispatch-protocol.md:181 后加判定规则：

```markdown
"占位符"判定（任一即视为占位符）：
- 空字符串或只有空白
- 包含 "TBD" / "TODO" / "待定" / "待确认" 等
- 字段值与字段名重复（如 platform: "platform"）
- 包含括号注释但无实际值（如 platform: "（待定）"）
```

**优先级**：🟢 低（实际很少出现，但明确化可减少争议）

### ❌ 不建议改

#### 11. 5 字段"必须由主 Agent 亲自写"（硬约束）

**证据**：dispatch-protocol.md:159, task-files.md:69
**判断**：❌ 不改。这是 P0 设计的核心约束（避免 T005/T006 教训重演）。

#### 12. 不写 prod_env（避免触碰生产）

**证据**：task-files.md:91-92 "不写 prod_env... 若 subagent 接触了生产环境（[PROD_TOUCHED]），说明它走错路了"
**判断**：❌ 不改。安全约束。

---

## 跨项目模式识别

### 模式 1：扩展章节是"决策记忆"载体

peekview 5 个 brief 的扩展章节都承担"主 Agent 决策记忆"功能：
- user_decisions：避免 P1 重做 30 分钟讨论
- coordination：避免多 agent 冲突
- 验收条件：避免 P1 形式化 BDD 时重写内容

**建议**：agate 官方承认"扩展是设计意图"，不只是"容忍"

### 模式 2：复杂任务的"一句话"约束失真

- 小任务（T023）："一句话"约束自然
- 中任务（T024/T025/T026）："一句话"勉强可用
- 大任务（T027）："一句话"硬塞会损失信息

**建议**：去掉"一句话"硬性措辞，改为"工程视角的核心描述"。

### 模式 3：P0 vs P1 职责边界

P0 已是"决策记忆"，P1 应是"需求基线"。但**没说清楚**。
**建议**：加"职责边界"指引。

---

## 改进优先级排序

| # | 改进项 | 优先级 | 工作量 |
|---|--------|--------|--------|
| 7 | P0 模板与自查清单不一致（事实错误）| 🔴 高 | 5 分钟 |
| 5 | P0 vs P1 职责边界没说清楚 | 🟠 中 | 30 分钟 |
| 9 | P0 扩展与 P1 重复风险 | 🟠 中 | 15 分钟 |
| 6 | "一句话"硬约束在复杂任务上不实用 | 🟡 低 | 10 分钟 |
| 8 | 扩展章节缺少官方模板 | 🟡 低 | 30 分钟 |
| 10 | "占位符"判定不明确 | 🟢 低 | 10 分钟 |

## 落地建议

按优先级落地：

1. **立即修**（5 分钟）：修正 dispatch-protocol.md:162-173 的 P0 YAML 模板，补 executor_env 段
2. **本次落地**（45 分钟）：加 P0/P1 职责边界段 + P1 模板引用指引 + 改"一句话"措辞
3. **下次落地**（30 分钟）：加扩展章节官方模板
4. **暂不落地**（10 分钟）：占位符判定（低频问题）

---

## 评审元判断

agate v1.2.0 的 P0-brief 设计**70 分**。骨架正确，扩展自由但边界模糊。最大的改进机会是**P0/P1 职责边界**和**P0 模板事实错误**。

实战项目（peekview）的 P0 brief 已**实际扩展**且**运转良好**（subagent 拿到 P0 即可开工，无需重做 1-2 小时讨论）。这反向验证了"扩展是设计意图"，建议 agate 正式承认并提供扩展模板。

**不要为任何特定项目优化**——这些改进对所有 agate 项目都有价值。
