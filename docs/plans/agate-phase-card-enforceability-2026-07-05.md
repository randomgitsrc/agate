---
task_id: agate-phase-card-enforceability
agent: main
date: 2026-07-05
status: 设计方案（含问题分析）
来源:
  - docs/reviews/agate-cognitive-load-progressive-disclosure-2026-07-05.md（原始 Phase Card 方案）
  - docs/reviews/phase-cards-self-gate-review-2026-07-05.md
  - docs/reviews/agate-phase-cards-p0-fix-implementation-review-2026-07-05.md（独立对抗评审）
  - 用户提问："agent 能再合适的实际真的去读 map 确定各阶段上下文么"
---

# Phase Card 防漂移 + 信息层完整性 — 设计方案

> 本方案在诚实评估后定位为**防漂移 + 信息层完整性**。原始用户问题「用 map 又不知道 agent 真读了没」对应的强制阅读，需要 forcing function（未采纳）或 issue #003 后续机制。本方案不声称解决强制阅读——只是保证嵌入 dispatch-context 的卡片是当前版本，不是过期或篡改版。

## 问题诊断

Phase Card 方案（commit `30cf55b`）的目标是让主 Agent 的**单次加载从 2900 行降到 ~100 行**。但用户在 review 部署后指出一个核心矛盾：

> "如果还维持现在 agate 读全量文件，那上下文仍会撑爆；如果用 map，又不知道 agent 真的读了没"

这个矛盾在原始 review 中未显式识别——原方案默认"agent 看到 mapping 表会自觉遵循"。这是**认知假设**，不是**可执行性保证**。

### 三层问题

| 层 | 问题 | 现状 | 谁该解决 |
|----|------|------|---------|
| **信息层** | 主 Agent 读 2900 行 → 上下文爆炸 | Phase Card mapping 表理论解决 | ✓ Phase Card 已解决（如果 agent 真的读 map） |
| **行为层** | 主 Agent 不读 mapping，继续全量读 / 跳过 | 无检查机制 | ❌ 未解决 |
| **决策层** | 主 Agent 需要"我现在该读哪张卡片"的判断 | 写在 mapping 表里 = agent 自己读自己判断 | ❌ 未解决——把决策放在 agent 内部 |

**关键洞察**：

- **决策层** 必须从 agent 内部挪走——它是个机械判断（"phase=P3 → 读 P3 卡片"），不应该是 agent 的自由裁量
- **行为层** 必须有外部约束——agent 跳过 mapping 的代价是另一个被 hook 检查的流程失败
- **信息层** Phase Card 已解决

## 方案分析

### 方案 A：CLI 命令（机械化决策层）

新增 `agate-next-card.sh` 命令：

```bash
$ agate-next-card.sh PHASE
→ 输出对应阶段的卡片全文
exit 0
```

参数说明：
- 只接收 PHASE（如 `P3`），不接受 task_dir（CLI 不需要任务上下文）
- PHASE 取值 P0-P8——每个都有卡片
- 不接受 P0-P8 之外的阶段（exit 2）

**机制**：
- agent 不再需要"自己读 mapping 表自己查 phase"——调一个命令就拿到
- 命令的输出是**当前阶段卡片的全文**，不是路径——agent 不需要二次读文件
- 命令的输出**可被下游流程消费**（关键）

**解决**：决策层（机械化）+ 信息层（不读全量）
**不解决**：行为层（agent 可以不调 CLI，自己读全量）

### 方案 B：派发 prompt 强制注入（强制行为层）

把 subagent 派发流程改为：

```bash
# 当前 dispatch-prompt.md 模板
P3 派发时 prompt 包含：
- 角色定义
- 输入文件列表
- 输出文件列表
+ 当前阶段卡片全文（强制）
```

**机制**：
- pre-commit hook 检查 dispatch-context.md 必须含当前阶段卡片全文
- 没有卡片全文 → commit 拦截
- agent 想跳过 Phase Card → 派发 subagent 失败

**解决**：行为层（subagent 派发强制附带卡片）
**不解决**：决策层（agent 仍需自己判断 phase→卡片）

### 方案 C：方案 A + B 组合

CLI 命令输出卡片全文 → 自动嵌入 dispatch-context.md → hook 验证。

**机制**：
1. agent 调 `agate-next-card phase=P3` → 拿到 P3 卡片全文
2. agent 把卡片全文粘贴到 dispatch-context.md
3. hook 检查：dispatch-context.md 必须含卡片全文（CLI 输出作为唯一权威源）
4. agent 想跳过 → 没有卡片全文 → hook 拦

**解决**：决策层（CLI）+ 信息层（不读全量）+ 行为层（hook 强制嵌入）

**新增问题**：agent 必须调 CLI 才能派发 subagent。如果 agent 想跳过 subagent 派发（自己写代码）——那又是另一个问题，不在本 plan 范围。

### 方案 D：保留现状

只优化文档（mapping 表加粗、orchestrator 强调映射），靠 agent 自觉。

**评价**：不可行。已经在 T046 证明"规则写在那不执行"。

## 推荐：方案 C

| 维度 | A | B | C | D |
|------|---|---|---|---|
| 信息层解决 | ✓ | ✗ | ✓ | ✗ |
| 决策层解决 | ✗（agent 仍需自决 phase→cat） | ✗ | ✗（同上） | ✗ |
| 行为层解决 | ✗ | 部分（仅当 agent 走 subagent 派发路径） | 部分（条件式 nudge，非 barrier） | ✗ |
| 实施成本 | 低 | 中 | 中+ | 零（不动） |
| 真实效果 | 信息层 + 防漂移 | 信息嵌入 subagent prompt | 信息层 + 防漂移 + 行为嵌入（仅当自愿） | 无 |

方案 C 的真实价值在信息层和防漂移，不是 barrier。这是诚实降级后的版本。CLI 的核心价值是给 hook 提供**可在 commit 时复算的权威 hash 源**——防止卡片被过期版本或篡改版本嵌入。

## 实施步骤

### 步骤 1：新增 CLI 命令 `agate-next-card.sh`

文件：`agate/scripts/agate-next-card.sh`

调用方式：

```bash
agate-next-card.sh P3   # 唯一参数：phase 名（P0-P8）
```

输出（stdout）：

```
## 当前阶段卡片：P3

路径：{agate_root}/phase-cards/P3-tdd.md
---
<card content>
```

exit code：
- 0：成功
- 1：参数缺失或过多
- 2：phase 不在 P0-P8 范围

实现要点：
- 用 `readlink -f` 解析 agate_root（参考现有 `agate-changes.sh` 模式）
- 直接 cat 对应阶段的卡片文件
- 输出用 `---` 分隔，hash 校验用 sha256sum

CLI 对每个 P0-P8 都返回对应卡片（P0 也是卡片，含主 Agent 启动指引）——`P0` 不应作为无效 phase。

### 步骤 2：新增 dispatch-context.md 模板

文件：`agate/assets/templates/dispatch-context.md`（当前不存在）

模板内容（**marker 名必须与 step 3 hook 完全一致，去掉 fence**）：

```markdown
---
phase: {P1-P8}
generated_by: agate-next-card.sh
---

## 任务上下文
- task_id: {Txxx}
- P0-brief 路径: docs/tasks/{Txxx}/P0-brief.md

## 当前阶段卡片（强制注入）

以下内容由 `agate-next-card.sh P{N}` 输出原样粘贴（**去掉 ``` fence，CLI 原文直嵌 marker 之间**）。hook 会校验 sha256 一致。

<!-- AGATE_CARD_START -->
{CLI 输出原文}
<!-- AGATE_CARD_END -->

## 其他派发上下文
（自由补充：环境状态、URL、选择器等）
```

**关键约束**：template ↔ hook ↔ CLI 三方字节必须完全一致：
1. marker 统一为 `AGATE_CARD_START` / `AGATE_CARD_END`
2. 模板里去 ``` fence，CLI 原文紧贴 marker
3. CLI 输出末尾不要带额外换行（避免 sed 区间边界错位）

### 步骤 3：hook 检查

文件：`agate/scripts/pre-commit-gate.sh`（在 2h 之后、subagent 派发相关检查之前）

新加检查项（2p）：

```bash
# 2p. dispatch-context.md 必须含当前阶段卡片且 sha256 匹配
# 注：PHASE 已含 P 前缀（实测 check-p6-provenance.sh:105 用 P6-dispatch-context.md）
DC_FILE="$TASK_DIR/${PHASE}-dispatch-context.md"
if [ -f "$DC_FILE" ]; then
    # 两侧都 hash 同一字节串（CLI 原始输出），零 strip
    EXPECTED=$(bash "$AGATE_ROOT/scripts/agate-next-card.sh" "$PHASE" 2>/dev/null)
    EXPECTED_HASH=$(printf '%s' "$EXPECTED" | sha256sum | awk '{print $1}')

    # 提取 dispatch-context 里 marker 之间的 CLI 原文
    EMBEDDED=$(sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p' "$DC_FILE" \
               | sed '1d;$d')  # 去掉 marker 行
    EMBEDDED_HASH=$(printf '%s' "$EMBEDDED" | sha256sum | awk '{print $1}')

    if [ "$EMBEDDED_HASH" != "$EXPECTED_HASH" ]; then
        echo "GATE: dispatch-context.md 卡片内容与 CLI 输出不一致（hash mismatch）" >&2
        echo "      期望 sha256: $EXPECTED_HASH" >&2
        echo "      实际 sha256: $EMBEDDED_HASH" >&2
        echo "      提示：重新调 agate-next-card.sh ${PHASE} 复制到 dispatch-context.md" >&2
        exit 1
    fi
fi
```

触发条件：仅当 `${PHASE}-dispatch-context.md` 存在时才检查。如果 agent 没生成（且没派发 subagent），检查跳过——但这意味着 agent 跳过 subagent 派发就不受强制，这是已知边界（plan §不解决什么 已声明）。

**hash 校验的真实价值**：防漂移——保证嵌入的是当前卡片版本，不是过期或篡改版本。**不证明 agent 读了卡片**（agent 可以机械粘贴不读）。这是诚实降级。

**实施纪律**：step 5 测试必须真跑到"嵌入 → hook → hash 相等 → commit 成功"。仅"文件生成"不够，必须到 hash 相等这一步。这是项目反复强调的"实跑纪律"——伪代码层面看不出 marker/fence 错位。

### 步骤 4：orchestrator-template.md 更新

替换 mapping 表为 CLI 调用指引：

```markdown
## 按阶段加载卡片

### 推荐方式（CLI）

```bash
agate-next-card.sh P3  # 返回 P3 卡片全文
```

CLI 输出直接作为当前阶段执行依据。subagent 派发时把输出粘贴到 `dispatch-context.md`。

### Fallback 方式（手工读映射）

| 当前阶段 | 卡片 |
|---------|------|
| P1 | `{agate_root}/phase-cards/P1-requirements.md` |
...
```
```

### 步骤 5：测试

新增 `agate/tests/unit/agate-next-card.bats`：
- 验证 CLI 对每个 phase 输出对应卡片
- 验证 CLI exit code 语义
- 验证无效 phase 退出 2

新增 `agate/tests/integration/dispatch-context-card.bats`：
- 验证 hook 检查逻辑
- **必须实跑到 hash 相等**：用 step 2 模板真生成 dispatch-context.md → 嵌入 CLI 真实输出 → 跑 hook → 断言 hash 相等 + commit 成功
- 构造"卡片未注入"和"卡片内容不一致"测试

### 步骤 6：self-gate

本实施涉及 `agate/scripts/*.sh` 改动 + 新增脚本 + 模板改动，必须走 self-gate：
- 派 protocol-alignment-review
- commit message 含 `self-gate-review:` 路径

### 步骤 7：验证

- `bats` 全量套件（新增 ~6 个测试）
- `check-protocol-consistency.py` 0 ERROR
- `shellcheck agate/scripts/*.sh` 0 error
- 实跑：模拟主 Agent 调用 CLI → 把输出注入 dispatch-context → commit 成功

## 不解决什么

### 行为偏差（行为层更深）

即使卡片被强制注入，agent 仍可能：
- 读了卡片但跳过"常见错误"小节
- 收到了 vision-helper 报告但选择用程序化指标反驳（T046 模式）

这是**激励结构问题**——非 Phase Card 能解决。需要：
- gate 硬化（已有计划 `agate-cognitive-overload-gate-hardening`）
- vision-helper 结论绑定（同一计划的 G3）
- 否定证据处理规则

Phase Card 解决"该知道"，这些机制解决"该知道且该执行"。

### 主 Agent 自己写代码不派 subagent

CLI + hook 的强制只在 agent **派发 subagent** 时生效。如果主 Agent 决定绕过 subagent 自己写代码，整个 Phase Card + hook 链条失效。

这条边界需要其他机制守护（如 issue #003 提到的"主 Agent 单点故障"结构性局限），不在本 plan 范围。

## 风险

| 风险 | 缓解 |
|------|------|
| agent 不调 CLI 也不派 subagent | 不在本 plan 范围；需要 issue #003 后续 |
| CLI 输出格式被 agent 误改 | hash 校验（步骤 3 用了 EXPECTED_CARD 对比） |
| CLI 输出过长（如果某张卡片 >500 行） | 实测 `wc -l`：P0=51 P1=69 P2=104 P3=65 P4=99 P5=74 P6=87 P7=63 P8=90，最长 P2=104 行远低于窗口 |
| 多个任务并发 → CLI 调用混淆 | CLI 不带 task_id 参数化，多任务并发是 hook 设计问题 |
| 增加 hook 检查 → 性能开销 | dispatch-context 检查在暂存区文件存在时才跑，~10ms 级别 |

## 优先级

方案 C 涉及多个改动（CLI + 模板 + hook + 测试 + self-gate），一次性实施约 1-2 天工作量。建议：

1. 步骤 1（CLI 命令）独立提交——基础工具，可单独用
2. 步骤 2-3（hook 强制）独立提交——可独立验证
3. 步骤 4（orchestrator 更新）独立提交——文档引导

3 个 commit，每个都可独立回滚。