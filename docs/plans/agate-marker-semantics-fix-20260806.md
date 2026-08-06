# 全标记语义一致性修正

> 2026-08-06 | v0.30.3 | 来源：SUGGEST 重命名后的全标记语义审视

## 背景

v0.30.2 重命名 `[NEED_CONFIRM倾向:]` → `[SUGGEST:]` 后，全面审视所有标记在每个环节的语义。发现 5 个问题：P6 NEED_CONFIRM 语义不合理、P5 verifier 误用 NEED_CONFIRM、P2 architect NEED_CONFIRM 语义不一致、BLOCKER 在 P4/P7 语义混淆、SUGGEST 适用范围未明确。

## Task 1: P6 删除 NEED_CONFIRM 检测

**问题**：P6 是客观验收——每条 BDD 实跑出 PASS 或 FAIL。"无法验证"应该 FAIL（回 P4），不是"等人确认方向"。验收是事实，不是方向。

### Step 1: check-gate.sh P6 删除 NEED_CONFIRM 相关逻辑

删除 L268-282 的 NC 检测（NC 计数 + NC>0 exit 1 + 格式不符检测 + 缺失声明 WARNING）。P6 gate 只保留：FAIL=0 + TOTAL>0 + 证据 + provenance。

### Step 2: P6 卡片删除 NEED_CONFIRM 相关说明

- L88：`FAIL=0 / NEED_CONFIRM=0 / 总数>0` → `FAIL=0 / 总数>0`
- L94：`NEED_CONFIRM > 0 → gate exit 1 → PAUSED` 整行删除
- L115：`无行首 [NEED_CONFIRM]（[NO_NEED_CONFIRM] 为合规负向声明）` 整行删除

### Step 3: verifier.md 把"无法验证标 NEED_CONFIRM"改为"标 FAIL"

- L84：`blocker_count > 0 → 标 [NEED_CONFIRM]` → `blocker_count > 0 → 标 FAIL`
- L98：`无法验证的 BDD 标 [NEED_CONFIRM]，不标 PASS` → `无法验证的 BDD 标 FAIL，不标 PASS`
- L122：同上
- L155：`拿不准"这个结果算不算符合预期" → 标 [NEED_CONFIRM]` → `拿不准"这个结果算不算符合预期" → 标 FAIL`
- L169-171：`### 何时标 [NEED_CONFIRM]` 的两条 P6 场景描述删除
- L173：`无待确认项时写 [NO_NEED_CONFIRM]` 保留——P5 verifier 仍需声明（不可逆操作的 NEED_CONFIRM 场景）。移到 verifier.md L49（P5 质量门槛节"PROD_TOUCHED"说明之后），作为 P5 的声明规则
- L179：`Z 个 NEED_CONFIRM` → 删除 NEED_CONFIRM 计数

**verifier.md L80-85 vision 仲裁流程**：L84 改为 `标 FAIL` 后，整个流程语义变为"blocker > 0 → 标 FAIL → 回 P4 重做"（非"交人判断"）。L80-85 的流程描述需同步调整：把"交人判断"改为"标 FAIL 回 P4"。

### Step 3b: state-machine.md 删除 P6 NEED_CONFIRM 状态转移

- L118：`FAIL=0/NC=0/证据非空` → `FAIL=0/证据非空`
- L124：`P6 --[存在未决 NEED_CONFIRM]--> PAUSED` 整行删除

### Step 3c: loop-orchestration.md 修正 P6 NEED_CONFIRM 引用

- L51：`未决的 [NEED_CONFIRM]（P1 需求方向 / P6 验收判断拿不准，必须人确认）` → `未决的 [NEED_CONFIRM]（P1 需求方向，必须人确认）`（删除 P6 验收引用）

### Step 4: task-files.md 删除 P6 的 NEED_CONFIRM 门槛

- L35：`无未决 [NEED_CONFIRM]（门槛）` → 删除
- L66：`无未决 [NEED_CONFIRM]` → 删除
- L274：`NEED_CONFIRM M 个` → 删除

### Step 5: 测试适配

- G6.2（P6 含 NEED_CONFIRM 期望 exit 1）→ **删除**（P6 不再检测 NEED_CONFIRM）
- G6.6（P6 FAIL=0 但 NEED_CONFIRM>0 期望 exit 1）→ **删除**
- G_NC_BINARY.4（P6 含 [NO_NEED_CONFIRM] + 最小 fixture 期望 exit 2）→ **删除**（P6 不再要求 NO_NEED_CONFIRM）
- 新增测试：P6 含 [NEED_CONFIRM] 不再被 gate 拦截（验证 NEED_CONFIRM 在 P6 被忽略，不报错不阻塞）

### Step 6: P7 consistency-reviewer 调整

consistency-reviewer.md L50：`未决项清零：全阶段产出无残留行首 [NEED_CONFIRM]` → 改为 `未决项清零：P1-requirements.md 无残留行首 [NEED_CONFIRM]（P6 不再有 NEED_CONFIRM）`

P7 卡片 L33 同步调整。

## Task 2: P2 architect NEED_CONFIRM 语义修正

**问题**：architect.md L104 的 NEED_CONFIRM "不硬阻塞"——与 P1 的阻塞语义不一致。

### Step 1: architect.md L104 改为 SUGGEST

`DEVIATION 涉及 P2 核心设计目标但已部分落地 → 标 [DEVIATION] + [NEED_CONFIRM]（不硬阻塞，但需人工确认是否可接受）`

改为：

`DEVIATION 涉及 P2 核心设计目标但已部分落地 → 标 [DEVIATION] + [SUGGEST: 理由]（不阻塞，主 Agent 可采纳）`

理由：P2 的"偏差需人确认但不阻塞"恰好是 SUGGEST 语义。如果偏差严重到需要人定夺，应该走 NEED_CONFIRM 阻塞回 P2 重设计。

## Task 3: BLOCKER 在 P4/P7 语义区分

**问题**：architect.md L93/L110 的 BLOCKER 是 P4 review 意见，P7 的 BLOCKER 是一致性检查结论。同名不同义。

### Step 1: architect.md P4 review 不用 BLOCKER 标记

- L93：`偏差用 [BLOCKER] 或 [OK] 标记` → `偏差用 [DEVIATION] 或 [OK] 标记`
- L110：`标 [DESIGN_GAP_REVIEWED: 已打回 P2] + [BLOCKER]` → `标 [DESIGN_GAP_REVIEWED: 已打回 P2]`（回 P2 本身就是阻断，不需要额外标 BLOCKER）

理由：P4 review 不需要复用 P7 的 BLOCKER 标记。architect.md 同文件 L103-105 已有 DEVIATION 三级分类（DEVIATION-CRITICAL / DEVIATION / EXTENSION），L93 的"偏差用 BLOCKER"直接改为"偏差用 DEVIATION"与同文件体系一致，不引入新标记。

## Task 4: 标记声明规范表加适用范围

**问题**：SUGGEST 的适用范围未明确。

### Step 1: dispatch-protocol.md 标记声明规范表加适用范围列

```markdown
| 标记 | 正向（触发了）| 倾向（求确认）| 负向（未触发）| 适用环节 |
|------|-------------|-------------|-------------|---------|
| PROD_TOUCHED | `[PROD_TOUCHED] {描述}` | — | `[PROD_NOT_TOUCHED]` | P5/P8（全阶段检测） |
| NEED_CONFIRM | `[NEED_CONFIRM] {描述}` | `[SUGGEST: 推荐 X，理由 Y]` | `[NO_NEED_CONFIRM]` | P1（gate 检测）；P2（信息标记，无 gate）；任意阶段不可逆操作（硬中断，含 P5） |
| BLOCKER | `[BLOCKER] {描述}` | — | `[BLOCKER]: 0 条` | P7（一致性检查） |
| DESIGN_GAP | `[DESIGN_GAP: 描述]` | — | `[DESIGN_GAP_REVIEWED: 描述]` | P4（标记）→ P7（配对检查） |
| SCOPE+ | `[SCOPE+] {描述}` | — | `[SCOPE_RESOLVED]` | P2/P4（声明）→ P1（增补）→ P7（检查） |
```

注：
- SUGGEST 仅在 P1 有 gate 检测（WARNING 不阻塞）。P2 architect 可用 SUGGEST 作为信息标记（无 gate）
- NEED_CONFIRM 在 P6 不再使用（客观验收，PASS/FAIL 二值）
- BLOCKER 专属于 P7，P4 review 用 DEVIATION-CRITICAL / DEVIATION / EXTENSION（见 architect.md DEVIATION 分类）

## Task 5: 测试 + 验证 + roadmap

### Step 1: 测试

- 删除 G6.2/G6.6/G_NC_BINARY.4（P6 NEED_CONFIRM 相关）
- 新增 G6.10：P6 含 [NEED_CONFIRM] → 不拦截（exit 2，NEED_CONFIRM 被忽略）
- 新增 G6.11：P6 无 [NO_NEED_CONFIRM] → 不再 WARNING

### Step 2: roadmap + CHANGELOG + README

### Step 3: 全量验证

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
```

## Self-Review

### 语义一致性

| 标记 | P1 | P2 | P4 | P5 | P6 | P7 | P8 |
|------|----|----|----|----|----|----|----|
| NEED_CONFIRM | 阻塞(gate) | 信息标记(无gate) | — | 不可逆操作硬中断 | ❌ 不用 | 检查P1残留 | — |
| SUGGEST | 不阻塞(gate) | 信息标记(无gate) | — | — | ❌ 不用 | — | — |
| NO_NEED_CONFIRM | 负向(P1) | — | — | 负向(P5不可逆操作) | ❌ 不用 | — | — |
| PROD_TOUCHED | — | — | — | 检测(gate) | — | — | 检测 |
| BLOCKER | — | — | ❌ 不用(P4用DEVIATION) | — | — | 检测(gate) | — |
| DESIGN_GAP | — | — | 标记 | — | — | 配对检查 | — |
| SCOPE+ | 增补 | 声明 | 声明 | — | — | 检查闭环 | — |

### 不增加 agent 负担

- P6 删除 NEED_CONFIRM → verifier 不需要写 NO_NEED_CONFIRM，减少一个必填项
- P2 architect 用 SUGGEST 替代 NEED_CONFIRM → 语义更准确
- P4 review 不用 BLOCKER → 消除歧义

### 向后兼容

- P6 删除 NEED_CONFIRM 检测是**宽松化**——之前含 NEED_CONFIRM 会 exit 1，现在不拦截。不会破坏现有通过的任务
- P2 architect 的 NEED_CONFIRM → SUGGEST 是文档改动，无 gate 检测
- P4 BLOCKER → CRITICAL 是文档改动，P4 gate 不检测 BLOCKER

### 风险

- 删除 G6.2/G6.6/G_NC_BINARY.4 测试 → 需确认这些测试的 fixture 不被其他测试复用
- P7 "未决项清零"从"全阶段"缩窄到"P1" → 如果 P2 architect 仍用 NEED_CONFIRM（信息标记），P7 不检查 P2 残留。但 P2 的 NEED_CONFIRM 是信息标记非门槛，P7 不需要检查
