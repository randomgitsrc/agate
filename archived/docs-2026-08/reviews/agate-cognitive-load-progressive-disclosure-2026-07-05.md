---
review_date: 2026-07-05
reviewer: main
scope: agate 协议全貌审视 — 认知过载根因与渐进披露重构方向
evidence:
  - docs/issues/003-main-agent-cognitive-overload.md
  - docs/reviews/t046-postmortem-20260705.md（非本仓，peekview 项目）
  - docs/reviews/t046-retrospective-20260705.md（非本仓，peekview 项目）
  - docs/plans/agate-cognitive-overload-gate-hardening-2026-07-05.md
---

# agate 协议全貌审视：认知过载与渐进披露重构

## 一、问题：规则密度超过 Agent 认知容量

### 1.1 现状

agate 协议本体 10 个文件，总计约 2900 行。主 Agent 被要求"先读完整协议再做任务"——每次任务开始时读 8 个协议文件 + 相关角色文件，然后才进入 P0。

**不是一次性的**——主 Agent 被压缩/中断后，恢复时必须重读。loop-orchestration.md 的步骤 0 明确要求"重新读一遍协议文件"。

### 1.2 症状（T046 实证 + 日常观察）

| 症状 | 频率 | 是否可以通过加 gate 规则缓解 |
|------|------|---------------------------|
| 忘了派评审 | T046 P2 实测 + 日常 | 可以（gate 检查 P2-review 存在） |
| 忘了做端到端验证 | T046 P4/P5/P6 | 可以（gate 检查 P5_e2e 字段） |
| 用"指标正确"替代"功能正确" | T046 P6 实测 | 部分可以（vision-helper 绑定） |
| 长时间无响应卡死 | T046 6 次记录 | 不完全是（orchestrator-log 缓解） |
| 规则写了但执行时不知道 | 高频 | **不可以**——gate 脚本只能覆盖部分规则 |
| 明知要回查但不回查 | 高频 | **不可以**——过载时回查是最先被砍的行为 |

### 1.3 恶性循环

```
问题 → 加规则 → 协议文件更长 → Agent 认知负担更大
  → 更过载 → 更容易跳步 → 出更严重的问题 → 加更多规则
```

v0.6 → v0.7 → v0.8 规则在增加（多方案探索、裁剪检查、evidence 审计、SCOPE+ 追踪、self-gate），但主 Agent 的认知容量没有增加。T046 是 v0.8 最完整规则下执行的，也是效果最差的一次。

**在"全量加载"模式下，加规则是负收益。** 当前 gate 硬约束扩展的计划（`agate-cognitive-overload-gate-hardening`）能做，但做完之后继续加规则就是在重复 swiss cheese model——每层都加一层但从不消灭根因。

**但需要分清两类问题**：
- **信息过载**：规则存在但 Agent 不知道/看不到 → 卡片解决
- **行为偏差**：规则知道但 Agent 选另一条路（gate 格式 > 功能验证、指标替代结果、反驳否定证据）→ 卡片不解决，需要配合 gate 硬化等机制

认知过载不是唯一原因，但它是让行为偏差变得致命的**条件**。Agent 不做过载时硬约束和软约束都能照顾；过载时 swiss cheese model 对穿——因为注意力只能放一个，就放那个会阻塞自己的。

## 二、根因：字典模式 vs 地图模式

### 2.1 两个模式

**字典模式（当前）**：所有信息在一个地方，用的时候查。适合人——人可以翻目录跳着读。不适合 Agent——Agent 的"读"是把整个文件内容装进上下文窗口，没有"跳着读"的能力。

**地图模式（应然）**：按阶段切割，每张卡片自包含。Agent 当前在 P3，就只需要 P3 的执行卡片——其他阶段的规则不在视野里，也不占用认知资源。

### 2.2 为什么字典模式对 Agent 不成立

人用字典：打开 → 看目录 → 跳到自己要的那页 → 只看那页。其他页不经过大脑。

Agent 用字典：`Read` 8 个文件 → 8 个完整文件内容全部进上下文窗口 → 2900 行同时在大脑里。Agent 不能"跳着读"——它能 `grep`，但 grep 结果只是定位，最终还是要读文件获取完整上下文，文件一读就是整段。

**Agent 的认知模型和人的认知模型不同。** agate 的设计隐含假设"Agent 会像人一样按需查阅文件"，但 Agent 的阅读行为是把文件完整加载到上下文窗口。这不是 implementation detail——这是根本性的架构不匹配。

### 2.3 当前各文件的信息分布

| 文件 | 行数 | 内容类型 | 什么阶段需要 |
|------|------|---------|------------|
| WORKFLOW.md | 360 | 阶段总览、流程图 | 全程 |
| dispatch-protocol.md | 953 | 派发模板、裁剪规则、P2.9 覆盖、任务粒度 | P0/P2/P4/P6（派发时） |
| state-machine.md | 652 | 状态转移、重试、中断恢复、P1-P8 条件 | 每阶段推进 |
| role-system.md | 206 | C8 映射表、双层角色、评审机制 | P2/P4（派评审时） |
| orchestrator-template.md | 178 | 全局配置、P0-brief、commit 策略 | 任务开始 |
| loop-orchestration.md | 253 | 自动编排、无状态原则 | loop 模式 |
| git-integration.md | 187 | 状态文件何时入 git、tag | commit 时 |
| LIMITATIONS.md | 84 | 已知局限 | 全程 |
| AGENTS.md | 83 | 目录索引 | 首次 |
| platform-notes.md | 79 | 平台适配 | 首次 |

**核心浪费**：Agent 在 P4 实现阶段需要读的角色文件是 implementer.md（111 行），但它同时持有 dispatch-protocol.md 的 953 行——其中 800+ 行跟 P4 无关（那是 P1/P2/P6 的派发模板、P2.9 覆盖逻辑、任务粒度指引等）。

### 2.4 "回查"为什么不可靠

agate 的规则执行模式是：

```
Agent 在上下文中持有全套协议 → 遇到决策点 → 主动回查相关规则 → 执行
```

问题是：过载时"回查"本身被跳过。不是 Agent 不想查——是上下文窗口已经被 2900 行占据，"我还有哪些规则需要回查"这个元认知本身就被规则密度压没了。

**"不忘记"和"知道要查什么"的前提是认知资源充足。** 当认知资源被规则加载耗尽时，两者一起消失。

## 三、方向：渐近披露的 Phase Card 模式

### 3.1 核心思路

把 agate 从"一个字典"变成"一组阶段卡片"。Agent 当前在哪个阶段就加载哪张卡片。每张卡片自包含——不需要查其他文件就能完成该阶段。

```
agate/
├── phase-cards/                    # 新增：阶段执行卡片
│   ├── P0-orchestrator.md          # 主 Agent 启动卡片
│   ├── P1-requirements.md          # 需求阶段卡片
│   ├── P2-design.md                # 设计阶段卡片
│   ├── P3-tdd.md                   # 测试设计阶段卡片
│   ├── P4-implementation.md        # 实现阶段卡片
│   ├── P5-verification.md          # 技术验证阶段卡片
│   ├── P6-acceptance.md            # 验收阶段卡片
│   ├── P7-consistency.md           # 一致性阶段卡片
│   ├── P8-release.md               # 发布阶段卡片
│   └── README.md                   # 各卡片索引，单一入口
├── rules/                          # 跨阶段规则（按需查阅，不上膛）
│   ├── state-transitions.md        # 状态转移规则
│   ├── review-mapping.md           # C8 评审映射表
│   └── commit-strategy.md          # commit/git 策略
├── roles/                          # 角色定义（subagent 读，主 Agent 只需派发时引用路径）
│   ├── execution/
│   └── review/
└── scripts/                        # gate 脚本（不变）
```

### 3.2 入口机制：怎么让 Agent 在正确的阶段读正确的卡片

Agent 不需要自己判断"该读哪张卡片"——mapping 表 + 卡片末尾指针组成一条链：

```
orchestrator-template.md ← Agent 永远从这里开始（项目侧拷贝）
  │
  │  mapping 表（内嵌在 orchestrator-template 中）：
  │    当前阶段 → 读哪张卡片
  │    P0 → agate/phase-cards/P0-orchestrator.md
  │    P1 → agate/phase-cards/P1-requirements.md
  │    ...
  │    P8 → agate/phase-cards/P8-release.md
  │
  ▼
  P0 卡片 ─→ 末尾: "完成 → 读 P1 卡片"
  P1 卡片 ─→ 末尾: "完成 → 读 P2 卡片"
  ...
  P8 卡片 ─→ 末尾: "完成 → 任务 DONE"
```

**启动路径**：Agent 读 orchestrator-template（含 mapping 表 + 项目配置）→ 无进行中任务 → 从 P0 开始 → 读 P0 卡片。

**中断恢复路径**：Agent 读 orchestrator-template → 读 .state.yaml → phase=P3 → 查 mapping 表 → "去读 P3 卡片"。

**单次加载量**：mapping 表（~20 行）+ 当前阶段卡片（~60 行）= ~80 行。相比当前的 ~2900 行。

### 3.3 卡片结构

每张卡片内容自包含，统一遵循 8 节模板：

```markdown
# P{N} — {阶段名}

> 当前状态：[首次 / 重试 #N / 裁剪跳阶] ← Agent 从 .state.yaml + phases 列表判定后填写

## 如果是首次进入本阶段
走完整流程

## 如果是重试（.state.yaml retries[P{N}] > 0）
确认上一轮失败原因 → 只修复失败项 → 读 rules/state-transitions.md 确认重试上限

## 如果是裁剪跳阶（phases 列表不含本阶段）
确认 P1 裁剪理由合规（check-pruning.sh 已检查）→ 跳过，读下一张卡片

## 前置条件（gate 会检查）
- [ ] 进入本阶段前必须满足的条件

## 派发（角色、输入、输出）

## 产出规格（产出文件的要求）

## gate 规则（gate 脚本会检查什么）

## 推进条件（满足什么才能写 phase: P{N+1}）

## 常见错误

## 下游影响（本阶段产出如何被后续阶段使用）
P{N+1} 需要... / P6 验收需要... / 如果本阶段输出 X 不对，Y 阶段会 fail
```

**导航**：卡片末尾一行 `完成本阶段 → 读 phase-cards/P{N+1}.md`。

Agent 读这一张卡片就知道 P3 该做什么、不该做什么、gate 会查什么、什么条件下能推进。**不需要同时持有 role-system.md、dispatch-protocol.md、state-machine.md、WORKFLOW.md 才能做对。**

### 3.3 关键设计原则

**1. 卡片是执行指南，不是字典条目**

不是把 2900 行切成 9 块就完了。每张卡片重新组织信息——从"这个阶段要做什么"的角度出发，而不是从"这些规则属于哪个文件"的角度出发。

**2. 前置条件在卡片上显式列出，不在其他文件里**

当前 P2→P3 的前置条件（P2-review approved、SCOPE+ resolved、retries 未超限）散在 state-machine.md、role-system.md、dispatch-protocol.md 三个文件。卡片把它们集中在一个前置条件清单里。

**3. gate 规则内联**

每张卡片把该阶段的 gate 判定规则写清楚。Agent 不需要读 check-gate.sh 的源代码来理解"gate 不过怎么办"。

**4. 跨阶段规则单独存放，按需引用**

state-machine.md 的状态转移规则是所有阶段共享的——它不应该在任何一张阶段卡片里重复。作为独立文件，只在"推进到下一阶段"时查阅。

**5. Agent 只读卡片 + 角色文件**

当前主 Agent 每轮读 8+ 文件。卡片模式下：
- 任务开始：P0 卡片（~60 行）
- 每个阶段：该阶段卡片（~60 行）+ 角色文件路径引用（subagent 自己读）
- 推进时：跨阶段规则文件中的状态转移规则（~80 行）

单次加载从 ~2900 行降到 ~140 行。

### 3.4 与现有文件的关系

| 现有文件 | 去向 |
|---------|------|
| AGENTS.md | 简化为一页索引（指向 phase-cards/README.md） |
| orchestrator-template.md | 合并入 P0 卡片。项目配置（agate_root/project_root）保留为配置片段 |
| WORKFLOW.md | 拆入各阶段卡片的前置/推进条件 |
| dispatch-protocol.md | 拆入各阶段卡片的派发小节。任务粒度/裁剪/P2.9 入 rules/ |
| state-machine.md | 入 rules/state-transitions.md。状态标记绑定规则内联到对应卡片 |
| role-system.md | 入 rules/review-mapping.md。C8 映射表按阶段内联到 P2/P4 卡片 |
| loop-orchestration.md | 入 P0 卡片（loop 模式是启动参数，不是阶段产物） |
| git-integration.md | 入 rules/commit-strategy.md |
| LIMITATIONS.md | 保留为独立文件（全程相关信息，但短——84 行） |
| platform-notes.md | 保留（首次接入时读一次即可） |

### 3.5 对 subagent 行为的影响

subagent 本身不变——它还是读角色文件按角色干活。变的是主 Agent 对 subagent 的调用方式：派发 prompt 不再需要主 Agent 自己从 dispatch-protocol.md 拼装——卡片上有完整的派发模板。

## 四、计划外的评审缺口（P1 需求评审）

当前 C8 评审映射表覆盖 P2（3 个评审角色）和 P4（4 个评审角色），P1 **没有任何评审角色定义**。

P1 产出的质量直接决定后续所有阶段的方向：
- BDD 拆分不合理 → P3 测试覆盖不全
- packages/domains 声明错 → P2 方案设计跑偏 → P4 审不到该审的
- capability_requirements 漏声明 → P6 验收遇到 GAP 才发现

需要一个 P1 需求评审角色（如 `requirements-review`），产出 `P1-review.md`，status: approved 作为 P1→P2 推进的前置条件。

## 五、只做 P3 卡片？不合理，必须全做

### 5.1 为什么只做一张不合理

卡片模式的目的是"Agent 全程只持有一张卡片"。如果只有 P3 是卡片、P0/P1/P2 仍走老路，Agent 在到达 P3 之前就已经过载了——它还是读了 8 个文件才走到 P2。到 P3 时上下文窗口已经满了，P3 卡片再轻量也没用。

**过载发生在启动阶段，不在执行中期。** 只做中期卡片是治标不治本。

### 5.2 全过程可以一次做完

9 张卡片 × ~60 行 = ~540 行，比 dispatch-protocol.md 一根文件（953 行）还短。内容已经存在——只是重新组织，不是创造新规则。

可行的实施路径：

1. 写 9 张卡片（1 天内可完成——每张卡片的内容在现有文件中已有答案）
2. 改 orchestrator-template.md：mapping 表 + 删除"8 个要读的文件"列表
3. 改 AGENTS.md：指向卡片索引
4. 跑全部测试（卡片是文档，不影响 gate 脚本，测试应全绿）
5. 在 peekview 任务试跑验证

**实现可行性**：
- 卡片不引入新规则 → 不产生新 bug
- 卡片是协议文档的新入口 → 旧文件保留作 reference → 向后兼容
- 内容从现有文件提取 → 不是从零创作
- gate 脚本不变 → 全量测试不受影响
- 实施复杂度：低。打字量：~540 行。风险：万一卡片漏了关键信息，Agent 会因为信息不全而做出错误判断

### 5.3 实施即验证

卡片对不对，不用控制变量的 AB 对比——写完直接用在 peekview 下一个任务里。如果正确率明显高于 T046（不用再犯"忘了派评审""忘了端到端"等错误），就是有效。如果还是翻车，说明减少信息量不是解药，方向需要重新评估。

## 六、补充考虑

### 6.1 卡片间的信息分布

卡片自包含意味着某些信息会跨卡片重复——比如 C8 评审映射在 P2 卡片和 P4 卡片都会出现。这不是问题，是设计意图。**Agent 的认知窗口是一张卡片，不是所有卡片。** 维护成本（改 C8 要改两张卡片）是值得的——换来执行时不需要跨文件查。

对外部规则文件的引用（如 state-machine.md 的转移规则），卡片不需要复制内容——只告诉 Agent "推进到下一阶段前，读 rules/state-transitions.md 确认转移条件"。

### 6.2 裁剪怎么办

任务裁剪某阶段 → 该卡片仍然被读，但 Agent 看到"前置条件"的第一条会是：

> **如果本阶段被裁剪**：确认 P1-requirements.md 的 phases 列表不含 P{N}，且有合规的裁剪理由（check-pruning.sh 会检查）。确认后跳过本卡片，直接读下一张卡片。

Agent 不需要自己判断是否裁剪——裁剪声明在 P1 里，check-pruning.sh 在 gate 时强制检查。卡片只告诉 Agent"如果裁剪了该怎么做"。

### 6.3 重试怎么办

重试逻辑是跨阶段的：P2 做错了要回到 P2，不是重新读 P2 卡片从头来。卡片需要区分"首次"和"重试"两种模式：

```
## 如果是首次进入本阶段
→ 走完整流程（派发 subagent → 产产出 → gate）

## 如果是重试（.state.yaml retries[P{N}] > 0）
→ 确认上一轮的失败原因（来自 gate 输出 / P{N}-review.md 的 rejected 理由）
→ 仅修复失败项，不重做已通过的部分
→ 读 rules/state-transitions.md 确认重试上限
```

### 6.4 SCOPE+ 怎么办

SCOPE+ 不是在某个特定阶段触发的——它可能在 P2 设计时、P4 实现时、甚至 P6 验收时才暴露。每张卡片的前置条件包括：

> **如果本任务发生过 SCOPE+**：确认 P1-requirements.md 是否有对应增补记录和 `[SCOPE_RESOLVED]` 标记。否则先处理 SCOPE+ 再说。

这不是全局规则重复——每张卡片都需要知道"SCOPE+ 没 resolve 不能推进"。因为它影响每个阶段的判断："当前产出的范围是什么、有没有超出原始声明"。

### 6.5 P0-brief 怎么处理

P0-brief 是跨阶段常量——Agent 在 P0 写了它，P1-P8 每个阶段派发 subagent 时都要引用（env_constraints、known_risks 等）。它不适合塞进 P0 卡片（P0 卡片是协议规则，P0-brief 是项目数据）。

处理方式：每张卡片的"派发"小节写：

> **派发时务必在 prompt 中包含 P0-brief.md 的路径**，subagent 需要其中的 env_constraints / known_risks / executor_env。

Agent 不需要每次都重读 P0-brief 全文——它已经在上一个阶段持有过。只需要知道"别忘了引用"。

### 6.6 卡片结构一致性

9 张卡片需要统一的节结构，否则 Agent 跨阶段时要重新适应格式：

```
# P{N} — {阶段名}

## 前置条件（进入本阶段前必须满足）
## 派发（角色、输入、输出）
## 产出规格（产出文件的要求）
## gate 规则（gate 脚本会检查什么）
## 推进条件（满足什么才能写 phase: P{N+1}）
## 常见错误
```

所有卡片遵循同一模板，Agent 只需适应一次格式，之后每个阶段都能快速定位信息。

### 6.7 旧文件怎么处理

卡片是入口，旧文件是 reference。关系：

- **AGENTS.md**：改为"先读 orchestrator-template.md → 按 mapping 表走。完整协议细节见以下文件（reference）"
- **orchestrator-template.md**：简化为 mapping 表 + 项目配置。不再列 8 个要读的文件
- **其余 9 个协议文件**：保留，标记为 reference/权威细节源。Agent 按需查阅——不是每轮必读。卡片上写"详细规则见 {file}#{section}"作为 fallback

维护规则：**卡片是执行层的 single source of truth。** 规则变了 → 先改对应协议文件 → 再同步卡片。

**内联 vs 引用的策略**：卡片和协议文件双重维护是真实的风险。策略应根据 agate 迭代频率调整：
- **稳定期**（当前 v0.8，规则不再频繁增发）→ 卡片内联规则，降低 Agent 外部读取次数
- **迭代期**（如果以后进入密集规则增发）→ 卡片引用协议文件的精确行范围（`见 state-machine.md:520-535`），Agent 只读那个片段而非整个文件

不是二选一，是按阶段切换。当前应走内联。

**卡片-协议一致性检查**：不能像 CHECK 9 那样逐锚点机械化验证——卡片重新组织信息结构，不是简单映射。能做到的是：卡片引用的文件段存在（CHECK 2 扩展）、卡片声明的规则类别在对应文件里至少有一处对应内容（分类一致性）。全量逐条对齐不可机械化，需要人工审查。

### 6.8 self-gate 与卡片机制

**触发漏**：当前 commit-msg-self-gate.sh 的触发正则不覆盖 `agate/phase-cards/*.md`（正则白名单是 `agate/scripts/... agate/[^/]+\.md agate/.+/.*\.md`——phase-cards 匹配 `agate/.+/.*\.md` 但需要确认）。改了卡片必须触发 self-gate，否则执行层的规则可以在无审查的情况下修改。

**双重维护的一致漏**：卡片和协议文件是两份表达同一协议的信息源。改协议文件忘同步卡片 → 卡片过期，Agent 按旧卡片执行 → 和没改一样或更糟（卡片说无需评审但新协议要求评审）。

**完备漏**：卡片从协议文件提取内容时有遗漏——某条规则在 dispatch-protocol.md 第 500 行写了但没出现在对应卡片里。当前 CHECK 9 只检查锚点-脚本对齐，不检查卡片-协议文件内容覆盖度。

**需要的机制**：

1. `commit-msg-self-gate.sh` 触发正则追加 `agate/phase-cards/.*\.md`
2. CHECK 新增：卡片-协议文件一致性检查。思路类似 CHECK 9 的锚点覆盖——但不能逐锚点比，卡片是重新组织的信息结构。可以：检查每张卡片的每条规则能否在至少一个协议文件里找到来源（反向：卡片不能有"凭空出现"的规则），同时检查协议文件里的每条规则是否至少在对应卡片里出现（正向：没有"被卡片遗忘"的规则）。后者更难——比如 state-machine.md 的 retry 规则，在卡片上是 "读 rules/state-transitions.md"，不算"出现"而是"引用"。需要区分"内联规则"和"引用规则"。
3. SELF-GATE.md 更新：新增卡片文件的触发条件和审查清单条目。

## 七、初步结论

agate 当前的核心矛盾不是"规则不够"，是"规则太多导致 Agent 执行时不知道有哪些规则"。

**方向**：从字典模式转为地图模式——按阶段切割，每张卡片自包含。Agent 只加载当前阶段需要的信息（~80 行），不把全套协议装脑子里（~2900 行）。

**卡片结构**：8 节统一模板——首次/重试/裁剪跳阶三模式入口、前置条件、派发、产出规格、gate 规则、推进条件、常见错误、下游影响。mapping 表 + 末尾指针组成导航链。

**卡片不解决所有问题**：行为偏差（"指标正确 = 功能正确"、反驳否定证据、优先满足硬约束）需要配合 gate 硬化等机制。卡片解决的是信息获取成本过高导致规则不执行的问题——这是必要但不充分的一步。

**维护策略**：当前稳定期走内联，未来迭代期可退化为引用+行范围。卡片-协议一致性检查做分类级（非逐条级）+ CHECK 2 扩展覆盖卡片。

**可行性**：9 张卡片 × ~60 行 ≈ 540 行，比 dispatch-protocol.md 单独一个文件还短。内容已存在，是重新组织不是创造新规则。gate 脚本不变，全量测试不受影响。

**关键设计约束**：
- 卡片间允许适当重复（如 C8 评审映射在多张卡片出现）——执行效率优先于维护 DRY
- 跨阶段规则（state-machine 转移、retry 逻辑）保留在 rules/ 文件里，卡片用一行引用即可
- 旧协议文件保留为 reference，卡片是执行层的 single source of truth
- 裁剪/重试/SCOPE+ 在每张卡片上有专门的"非首次/非标准情况"小节

**前提和风险**：核心假设——Agent 确实能"只读一张卡片"就做对。如果 Agent 在低信息量下仍选择用错误指标替代功能验证（T046 模式），那减少信息量不解决行为层的问题，需要配合 G3（vision-helper 绑定）等其他机制。但不试不知道，实施即验证。

**下一步**：一次写完 9 张卡片 + 改 orchestrator-template mapping 表 + 改 AGENTS.md 索引。在 peekview 下一个任务试跑。
