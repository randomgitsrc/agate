---
review_date: 2026-07-20
reviewer: protocol-alignment-review
change_summary: v0.13.1 适用边界强化（改动性质分层判断+风险矩阵入口+P2.14改动性质声明）+P8 gate tag WARNING+P3前置状态覆盖提示+orchestrator-log最低纪律+A7设计原则一致性审查项；v0.14.0 ADR架构决策记录+CONTEXT.md术语表+A7锚定到ADR+AGENTS.md文件清单更新+hardening-roadmap Phase 2C同步
files_changed: [agate/WORKFLOW.md, agate/orchestrator-template.md, agate/state-machine.md, agate/assets/review-roles/protocol-alignment-review.md, SELF-GATE.md, agate/phase-cards/P3-tdd.md, agate/scripts/check-gate.sh, agate/tests/unit/check-gate.bats, agate/AGENTS.md, agate/adr.md, agate/CONTEXT.md, agate/scripts/check-p6-provenance.sh, agate/scripts/pre-commit-gate.sh, agate/tests/integration/pre-commit-hook.bats, docs/hardening-roadmap.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（2 项 NEEDS_HUMAN_REVIEW 见详情） |
| A4 | 测试覆盖 | ALIGNED（1 项 NEEDS_HUMAN_REVIEW 见详情） |
| A5 | 下游影响 + 文档传播 | MISALIGNED（CHANGELOG 未更新） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 改动性质分层判断**

**文档声明**（WORKFLOW.md:124-143）：
> 判断"直接做"还是走 agate，先看改动性质，再看影响范围和风险等级。
> 声明性改动（不改变程序运行时控制流）→ 可直接做
> 行为逻辑改动（条件分支、状态转换、数据处理）→ 至少走裁剪 agate
> 机制交叉（≥2 个子系统交互、时序依赖、跨层影响）→ 必须走完整 agate

**脚本实现**：无脚本实现（纯文档规则，主 Agent 决策入口，在走 agate 之前判断）。

**结论**：ALIGNED。改动性质判断是文档层面的决策指引，不需要脚本实现。判断结果体现在 P0-brief 和 P1 裁剪说明中，由后续 gate 脚本间接验证（裁剪条件检查）。

**A1.2 P2.14 改动性质声明**

**文档声明**（WORKFLOW.md:195）：
> "直接做"的最低要求（P2.14）：commit message 必须声明改了什么 + 改动性质（声明性/行为逻辑/机制交叉）+ 为什么安全。

**脚本实现**：无 commit-msg hook 检查改动性质字段。

**结论**：ALIGNED。P2.14 是对"直接做"场景的行为约束，此时不走 agate 流程（无 pre-commit hook 触发），属于文档规则。建议未来考虑 commit-msg hook 提醒，但当前不构成 MISALIGNED。

**A1.3 P8→READY tag 条件**

**文档声明**（state-machine.md:132）：
> P8 --[...+ git tag -l "${VERSION_TAG_PREFIX}{version}" 存在（推荐，不阻断）]--> READY

**脚本实现**（check-gate.sh:206-213）：
```bash
VERSION_TAG_PREFIX="${VERSION_TAG_PREFIX:-v}"
CHANGELOG_DIFF=$(git diff --cached -- "$CHANGELOG_FILE" 2>/dev/null || true)
TAG_VERSION=$(echo "$CHANGELOG_DIFF" | grep -oE '\[[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9.-]*\]' | head -1 | tr -d '[]' || true)
if [ -n "$TAG_VERSION" ]; then
    if ! git tag -l "${VERSION_TAG_PREFIX}${TAG_VERSION}" 2>/dev/null | grep -q .; then
        echo "GATE P8 WARNING: tag ${VERSION_TAG_PREFIX}${TAG_VERSION} 不存在..."
    fi
fi
```

**结论**：ALIGNED。文档说"推荐不阻断"，脚本实现为 WARNING（不设 RC=1），语义一致。`VERSION_TAG_PREFIX` 环境变量覆盖符合 ADR-003 不绑定技术栈原则。

**A1.4 orchestrator-log 最低纪律**

**文档声明**（state-machine.md:416）：
> 若 gate 不通过：追加至少一行到 orchestrator-log.md（记录 gate 失败阶段+原因）

**文档声明**（orchestrator-template.md:170-171）：
> 以下事件应追加至少一行：gate 失败、subagent 失败/空返回、流程决策（PAUSED/回退/跳阶）、用户叫停
> 其他事件自由追加，仅追加不编辑不整理

**脚本实现**：无脚本检查（主 Agent 行为约束）。

**结论**：ALIGNED。orchestrator-log 是主 Agent 的行为纪律，不依赖脚本强制。

**A1.5 P3 前置状态覆盖**

**文档声明**（WORKFLOW.md:163-165）：
> Given 不仅是"数据准备"，也是"系统处于某种状态"——这个状态本身需要被验证。

**阶段卡片同步**（P3-tdd.md:60）：
> 5. 只覆盖交互路径，忽略前置状态：测试设计应覆盖 BDD Given 隐含的前置状态，不只覆盖 When/Then 路径（详见 WORKFLOW.md §P3 测试设计指导）

**结论**：ALIGNED。WORKFLOW.md 新增指导节，P3 卡片常见错误同步引用。

**A1.6 机制交叉引用到 orchestrator-template.md**

**文档声明**（orchestrator-template.md:105）：
> 机制交叉改动（≥2 个子系统交互、时序依赖、跨层影响）必须走完整 agate——判断"直接做"前先评估改动性质（详见 WORKFLOW.md §改动性质判断）

**WORKFLOW.md 源**（WORKFLOW.md:124-143）：改动性质判断完整节。

**结论**：ALIGNED。关键不变量节引用了改动性质判断，指向 WORKFLOW.md 对应节。

**A1.7 ADR-005 引用**

**文档声明**（WORKFLOW.md:142）：
> 架构决策记录：ADR-005

**ADR-005 内容**（adr.md:128-162）：改动性质决定流程——声明性/行为逻辑/机制交叉。

**结论**：ALIGNED。WORKFLOW.md 改动性质判断节底部引用 ADR-005，ADR-005 内容与 WORKFLOW.md 规则一致。

### A2: 脚本→文档对齐

**A2.1 check-gate.sh P8 tag WARNING**

**脚本实现**（check-gate.sh:206-213）：P8 新增 tag 存在性检查，WARNING 不阻断，支持 `VERSION_TAG_PREFIX` 环境变量。

**文档声明**（state-machine.md:132）：
> git tag -l "${VERSION_TAG_PREFIX}{version}" 存在（推荐，不阻断）

**结论**：ALIGNED。脚本 WARNING 行为与文档"推荐不阻断"一致。

**A2.2 A7 审查项**

**角色文件**（protocol-alignment-review.md:26）：
> A7 | 设计原则一致性 | 变更是否符合已记录的 ADR（agate/adr.md）？

**SELF-GATE.md**（SELF-GATE.md:119）：
> A7 设计原则一致性

**结论**：ALIGNED。两处同步新增 A7 项，内容一致。

**A2.3 A7 特殊规则**

**角色文件**（protocol-alignment-review.md:105）：
> A7 只有 ALIGNED 和 NEEDS_HUMAN_REVIEW 两种结论，不存在 MISALIGNED

**结论**：ALIGNED。特殊规则明确，与 A7 审查性质（设计原则是指导性的）一致。

### A3: 一致性连锁 + 反向传播

#### A3a: 已知的衍生改动（连锁）

| 改动源 | 衍生目标 | 是否同步 | 结论 |
|--------|----------|----------|------|
| WORKFLOW.md 改动性质判断 | orchestrator-template.md 关键不变量 | ✅ 已同步（:105） | ALIGNED |
| state-machine.md P8 tag 条件 | check-gate.sh P8 tag 检查 | ✅ 已同步（:206-213） | ALIGNED |
| WORKFLOW.md P3 测试设计指导 | P3-tdd.md 常见错误 5 | ✅ 已同步（:60） | ALIGNED |
| A7 审查项 | protocol-alignment-review.md | ✅ 已同步（:26,105） | ALIGNED |
| A7 审查项 | SELF-GATE.md | ✅ 已同步（:119） | ALIGNED |
| AGENTS.md 文件清单 | adr.md + CONTEXT.md 条目 | ✅ 已同步（:26-27） | ALIGNED |

#### A3b: 反向传播——应被影响但 diff 未列出的文件

**1. dispatch-protocol.md**

改动性质判断在 WORKFLOW.md 适用边界节，是主 Agent 决定"走不走 agate"的入口。dispatch-protocol.md 描述的是"走 agate 后"的派发协议。改动性质判断发生在 P0-brief 之前（主 Agent 收到任务后先判断要不要走 agate），不属于派发协议范畴。

**结论**：ALIGNED。dispatch-protocol.md 不需要同步改动性质判断。

**2. role-system.md**

ADR-006（双层角色）已在 adr.md 记录。role-system.md 描述双层角色的具体实现（执行角色+评审角色列表、C8 映射），与 ADR-006 内容一致但角色不同——role-system.md 是"怎么做"，ADR-006 是"为什么这样做"。

**结论**：ALIGNED。role-system.md 不需要引用 ADR-006（两者内容一致，引用是增强非必须）。

**3. LIMITATIONS.md**

ADR-001/003/005 的后果中提到局限（如 ADR-001 后果"微任务成本可能超过收益"、ADR-005 后果"判断边界仍有灰区"），但 LIMITATIONS.md 的局限描述自包含（局限 1-8 各自独立描述问题和现状），不需要交叉引用 ADR。

**结论**：NEEDS_HUMAN_REVIEW。LIMITATIONS.md 加 ADR 交叉引用是增强（帮助读者理解局限的决策背景），但当前描述自包含，不加也不构成 MISALIGNED。建议维护者按需添加。

**4. P0-brief 模板**

WORKFLOW.md 新增改动性质判断后，P0-brief 模板（dispatch-protocol.md:186-202）的 `phase_hint` 字段隐含了"已决定走 agate"的前提。改动性质判断发生在 P0-brief 之前，不影响 P0-brief 字段结构。

**结论**：NEEDS_HUMAN_REVIEW。P0-brief 是否应新增 `change_nature: {声明性|行为逻辑|机制交叉}` 字段？当前 P0-brief 五字段不含改动性质，但改动性质判断在 P0 之前完成（决定走 agate 后才写 P0-brief），所以 P0-brief 不需要此字段。建议确认此理解。

### A4: 测试覆盖

**bats 全量实跑输出**：

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
283 tests passed, 0 failed
```

**P8 tag 测试覆盖**：

| 用例 | 覆盖场景 | 结论 |
|------|----------|------|
| G8.7 | tag 不存在 → WARNING（exit 2） | ✅ |
| G8.8 | tag 存在 → 无 WARNING | ✅ |

**未覆盖**：

| 场景 | 风险评估 | 结论 |
|------|----------|------|
| `VERSION_TAG_PREFIX` 环境变量覆盖 | 低风险（默认 v 前缀覆盖了绝大多数场景） | NEEDS_HUMAN_REVIEW |

**改动性质判断 / P3 前置状态 / A7 审查项**：纯文档规则，无脚本实现，不需要 bats 测试。

**结论**：ALIGNED。核心变更（P8 tag）有测试覆盖，`VERSION_TAG_PREFIX` 环境变量覆盖未测但风险低。

### A5: 下游影响 + 文档传播

**破坏性变更**：无。P8 tag 检查是 WARNING 不阻断，不影响已有项目的 gate 行为。

**CHANGELOG 标注**：

CHANGELOG.md 最新条目为 `[0.13.0] - 2026-07-13`，**未包含 v0.13.1 和 v0.14.0 的变更记录**。

**结论**：MISALIGNED。v0.13.1 和 v0.14.0 的变更（改动性质判断、P8 tag WARNING、P3 指导、A7 审查项、ADR、术语表）均为协议语义变更，应在 CHANGELOG 中标注。

**建议修复方向**：在 CHANGELOG.md 的 `[Unreleased]` 或新版本号下添加 v0.13.1/v0.14.0 变更条目。

**文档传播检查**：

| 文档 | 是否需要同步 | 是否已同步 | 结论 |
|------|------------|-----------|------|
| orchestrator-template.md | 机制交叉引用 + log 纪律 | ✅ 已同步 | ALIGNED |
| state-machine.md | P8 tag 条件 + log 追加 | ✅ 已同步 | ALIGNED |
| P3-tdd.md | 常见错误 5 | ✅ 已同步 | ALIGNED |
| dispatch-protocol.md | 不需要（改动性质判断不在派发协议范围） | N/A | ALIGNED |
| role-system.md | 不需要（ADR-006 内容一致） | N/A | ALIGNED |
| LIMITATIONS.md | 加 ADR 引用是增强非必须 | 未加 | NEEDS_HUMAN_REVIEW（见 A3b） |
| hardening-roadmap.md | Phase 2C 条目 | ✅ 已同步 | ALIGNED |

### A6: 锚点表覆盖

`check-protocol-consistency.py` CHECK 9 通过（0 ERROR），协议-脚本结构对齐无问题。

新增规则分析：

| 新增规则 | 是否需要锚点表条目 | 理由 |
|----------|-------------------|------|
| 改动性质判断 | 否 | 纯文档规则，无脚本实现 |
| P8 tag WARNING | 否 | CHECK 9 已覆盖 check-gate.sh |
| P3 前置状态指导 | 否 | 纯文档指导，无脚本实现 |
| A7 审查项 | 否 | 审查流程规则，无 gate 脚本锚点需求 |
| ADR-005 | 否 | 决策记录，无脚本实现 |
| CONTEXT.md 术语 | 否 | 术语表，无脚本实现 |

**结论**：ALIGNED。锚点表不需要更新。

### A7: 设计原则一致性

逐条检查相关 ADR：

**ADR-001（隔离性——主 Agent 不写产出）**

改动性质判断允许"声明性改动→直接做"，即主 Agent 可以不走 agate 直接改代码。这不违反 ADR-001——"直接做"是跳过 agate 流程，不涉及"主 Agent 写阶段产出"。走 agate 时仍遵守隔离性（主 Agent 不写 P1-P8 产出）。

**结论**：ALIGNED。

**ADR-002（可判定性——gate 门槛机器可判定）**

P8 tag 检查是 WARNING（exit 2），属于"需人工判断"级别，符合 ADR-002 的三级判定（0=通过，1=不通过，2=需人工判断）。

**结论**：ALIGNED。

**ADR-003（最小约定——不绑定技术栈）**

`VERSION_TAG_PREFIX` 环境变量覆盖，不硬编码 tag 前缀为 `v`。符合不绑定技术栈原则。

**结论**：ALIGNED。

**ADR-004（安全网分层——hook 兜底，主动验主流程）**

P8 tag WARNING 在 check-gate.sh 中实现，三层防线（主 Agent 主动验 + hook + CI backstop）均覆盖。

**结论**：ALIGNED。

**ADR-005（改动性质决定流程）**

本次变更的核心——WORKFLOW.md 改动性质判断节就是 ADR-005 的落地实现。WORKFLOW.md:142 引用 ADR-005。

**结论**：ALIGNED。

**ADR-006（双层角色——执行角色 + 评审角色）**

A7 审查项新增，审查角色（protocol-alignment-review）独立于被审查的协议/脚本，符合执行+评审分离原则。

**结论**：ALIGNED。

**未记录的架构决策检查**：

- orchestrator-log 最低纪律（应追加事件 vs 想写就写）：这是流程规则的细化，不是架构决策。
- P3 前置状态指导：这是测试设计指导，不是架构决策。
- CONTEXT.md 术语表：这是文档组织方式，不是架构决策。

**结论**：ALIGNED。无遗漏 ADR。
