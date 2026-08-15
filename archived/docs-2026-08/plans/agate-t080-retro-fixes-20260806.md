# T080 复盘改进计划

> 2026-08-06 | 来源：T080-admin-user-management 复盘（14 个 agate 机制缺口）
> 7 个高可行性项 + 1 个中可行性项（NEED_CONFIRM 分级，含 gate 脚本改动）
> 3 个低可行性项（架构级，记 roadmap 待论证）

## 背景

T080 复盘核心结论："慢的主因不是 agate 流程臃肿，而是质量问题的延迟发现"。但"为什么质量门没前移"——不是 agent 不够努力，是 agate 的机制设计缺了这些维度。本 plan 落实前移质量门的具体机制。

## Task 1: gate 格式契约透明化（#1+#2+#3）

**问题**：gate 脚本正则是"硬法律"，但角色文件只给描述性说明。verifier/consistency-reviewer 写的格式"看起来对"但不符合正则。T080 中 4 处格式问题被 gate 拦截（vision YAML 结构、引用括号、dispatch-context 预判、DESIGN_GAP_REVIEWED 行首）。

### Step 1: verifier 角色文件追加 gate 正则模板

在 `agate/assets/execution-roles/verifier.md` 追加：

```markdown
## P6 gate 格式契约（精确正则）

gate 脚本用以下正则匹配，产出必须严格符合：

- PASS/FAIL 行：`^\s*- (PASS|FAIL)\b`（行首，`-` 后空格，PASS/FAIL 大写）
- 总结行禁止用行首 `- PASS`/`- FAIL`（用 `**Summary**: PASS: 34` 格式，check-p6-format.sh 会自动修正）
- vision 引用：独立括号 `(vision: path/to/yaml)`，不与截图引用合并在同一括号
- vision YAML 结构：`vision_analysis.summary.blocker_count`（嵌套，非顶层）
- 截图引用：`(screenshots/filename.png)`

示例：
```
- PASS BDD-1: 描述 (screenshots/login.png) (vision: vision-reports/bdd-1.yaml)
- FAIL BDD-2: 描述 (result.json)
```
```

### Step 2: consistency-reviewer 角色文件追加 DESIGN_GAP 格式

在 `agate/assets/execution-roles/consistency-reviewer.md` 追加：

```markdown
## P7 gate 格式契约

- DESIGN_GAP 必须在行首：`[DESIGN_GAP: 描述]`（非句中引用）
- DESIGN_GAP_REVIEWED 必须在行首：`[DESIGN_GAP_REVIEWED: 描述]`
- gate 正则：`^\[DESIGN_GAP` / `^\[DESIGN_GAP_REVIEWED`
```

### Step 3: dispatch-context 模板追加格式提醒

在 `agate/assets/templates/dispatch-context.md` 的"### 约束"节追加：

```markdown
> **dispatch-context 格式约束**：约束节避免行首 `- PASS`/`- FAIL`（被 provenance 预判检测匹配）。改用"通过/失败"或加引号。
```

### 测试

纯文档，无脚本测试。consistency checker 确认无断引用。

## Task 2: known-failures.md 语义边界明确化（#5）

**问题**：verifier 把当前任务失败写进 known-failures.md（语义是"预存失败"）。T080 中 E2E 选择器失败被写入，污染语义。

### Step 1: known-failures 模板追加语义说明

在 `agate/assets/templates/known-failures-template.md` 追加：

```markdown
> **语义边界**：本文件只登记**预存失败**（P5 之前就存在的、与当前任务无关的失败）。
> 当前任务引入的失败用 P5-test-results/ 记录，不写本文件。
```

### Step 2: P5 卡片追加说明

在 `agate/phase-cards/P5-verification.md` L67 附近追加：

```markdown
> **known-failures.md 只登预存失败**（P5 之前就存在的、与当前任务无关的）。当前任务引入的失败用 P5-test-results/ 记录。
```

### 测试

纯文档，无脚本测试。

## Task 3: P1 基线变更保护（#6）

**问题**：P4 修改 P1 文档无 [BASELINE_CHANGE] 机制。下游改上游文档应触发主 Agent 显式批准。

### Step 1: P1 卡片追加基线保护说明

在 `agate/phase-cards/P1-requirements.md` 末尾追加：

```markdown
**P1 基线保护**：P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
```

### Step 2: P4 卡片追加提醒

在 `agate/phase-cards/P4-implementation.md` 常见错误节追加：

```markdown
N. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
```

### 测试

纯文档，无脚本测试。

## Task 4: P8 bump + CHANGELOG 绑定同一 commit（#7）

**问题**：P8 双 bump commit（先 commit 再 amend 补 CHANGELOG）。

### Step 1: P8 卡片明确 bump + CHANGELOG 同一 commit

在 `agate/phase-cards/P8-release.md` L12 改为：

```markdown
3. 主 Agent 执行 gate 验证 → 通过后执行 bump-version + CHANGELOG 更新 → 同一 commit + tag
```

### 测试

纯文档，无脚本测试。

## Task 5: P2 选择器契约提示（#8）

**问题**：P3/P4 class 命名无协同。T080 中 test-designer 用 `.admin-user-list`，implementer 用 `.user-list`。

### Step 1: P2 卡片追加选择器建议

在 `agate/phase-cards/P2-design.md` 的"产出规格"节末尾追加：

```markdown
**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。
```

### 测试

纯文档，无脚本测试。

## Task 6: P1 review 跨条 BDD 一致性维度（#9）

**问题**：P1 requirements-review 检查维度没"同场景不同 BDD 的 Then 是否矛盾"。T080 最大耗时杀手（P4 retry 3 次主要解决 P1 BDD 矛盾）。

### Step 1: requirements-review 角色文件追加检查维度

在 `agate/assets/review-roles/requirements-review.md` 的检查清单追加：

```markdown
**BDD 跨条一致性：**
- 同一 Given/When 场景的多条 BDD，Then 是否矛盾（如 BDD-A 返回 400 但 BDD-B 同场景返回 409）
- 保护优先级：同场景多个保护机制重叠时，优先级是否显式声明
- 测试数据设计是否考虑环境约束（并发/数据量/资源限制等）
```

### 测试

纯文档，无脚本测试。

## Task 7: P2 review UI 组件完整性维度（#10）

**问题**：P2 plan-design-review 聚焦方案/权衡，不查 spec 是否遗漏组件。T080 中 architect 漏了 PasswordResetDialog 的 input spec。

### Step 1: plan-design-review 角色文件追加检查维度

在 `agate/assets/review-roles/plan-design-review.md` 的评分维度追加：

```markdown
- **组件完整性**：spec 涉及的每个 UI 组件是否有完整的 input/output 描述（触发条件 + 用户输入 + 预期输出）。遗漏组件 spec 会导致 P4 implementer 凭空实现
```

### 测试

纯文档，无脚本测试。

## Task 8: NEED_CONFIRM 分级（#11）

**问题**：只有阻塞/不阻塞两档。"有倾向但求确认"和"真无方向"被同等对待。T080 中 6 个 NEED_CONFIRM 全部阻塞，其中 5 个用户选了 analyst 推荐项。

### Step 1: P1 卡片追加 NEED_CONFIRM 分级格式

在 `agate/phase-cards/P1-requirements.md` 的 NEED_CONFIRM 说明处追加：

```markdown
**NEED_CONFIRM 分级**：
- `[NEED_CONFIRM倾向: 推荐 X，理由 Y]` — 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` — 真无方向需人定夺。阻塞推进，主 Agent 问用户
```

### Step 2: gate 脚本适配

check-gate.sh P1 的 NEED_CONFIRM 检测（L67）当前匹配所有行首 `[NEED_CONFIRM]`。改为：
- `[NEED_CONFIRM倾向: ...]` → WARNING 不阻塞
- `[NEED_CONFIRM]`（精确匹配，不含"倾向"）→ exit 1 阻塞

**P6 不同步**：P6 的 NEED_CONFIRM 语义与 P1 不同——P6 是验收阶段的"需确认"（如 UI 问题需人判断），不适合自动采纳倾向。只改 P1。

关键：用精确正则区分两种格式。`[NEED_CONFIRM倾向: X]` 不被 `^\s*-?\s*\[NEED_CONFIRM\]` 匹配（`\]` 要求 `]` 紧跟 `NEED_CONFIRM`，倾向性标记中 `NEED_CONFIRM` 后跟 `倾向`）。

用 `NC_ALL - NC_TENDENCY` 计算阻塞性数量（不用 `grep -v`，避免管道给数字做匹配的 bug）：
```bash
NC_ALL=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM' "$P1_FILE" 2>/dev/null || echo 0)
NC_TENDENCY=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM倾向:' "$P1_FILE" 2>/dev/null || echo 0)
NC_BLOCKING=$((NC_ALL - NC_TENDENCY))
```

### 测试

```bash
@test "G_NC_TENDENCY.1 P1 含 [NEED_CONFIRM倾向: X] → exit 2（不阻塞）" {
    # 只有倾向性 NEED_CONFIRM，无阻塞性 → exit 2
}

@test "G_NC_TENDENCY.2 P1 含 [NEED_CONFIRM倾向: X] + [NEED_CONFIRM] → exit 1（阻塞性仍在）" {
    # 混合 → exit 1
}
```

## Task 9: roadmap + 全量验证

### Step 1: roadmap 更新

8 项从"待处理"改为"已实施"。低可行性 3 项（#12 P6 格式修正例外、#13 P6 断点续做、#14 retry 预算分类）保留"待论证"。

### Step 2: 验证

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
```

## Self-Review

### 不增加 agent 负担

- Task 1-7: 纯文档（角色文件/卡片/模板追加格式契约和检查维度），agent 读到就知道怎么写对，减少 retry
- Task 8: NEED_CONFIRM 分级减少用户阻塞（倾向性确认主 Agent 自行采纳）
- 所有改动都是"把隐式规则显式化"，不增加新门槛

### 向后兼容

- Task 1-7: 纯文档追加，不改 gate 行为
- Task 8: `[NEED_CONFIRM倾向: ...]` 是新格式，旧 `[NEED_CONFIRM]` 行为不变（仍阻塞）。gate 脚本向后兼容

### 前移质量门的核心逻辑

| 改进 | 前移到 | T080 节省 |
|------|--------|-----------|
| P1 review 跨条一致性（Task 6） | P1 review | ~58min（P4 retry 3→0） |
| P2 review UI 组件完整性（Task 7） | P2 review | ~9min（P2 retry 1→0） |
| gate 格式契约透明化（Task 1） | verifier 一次写对 | ~8min（P6 格式拉锯→0） |
| NEED_CONFIRM 分级（Task 8） | P1 不阻塞用户 | 用户等待→0 |

### 风险

- Task 8 gate 脚本改动：用 `NC_ALL - NC_TENDENCY` 计算阻塞性数量，避免 `grep -v` 误过滤。需确保 `[NEED_CONFIRM倾向:` 不被 `^\s*-?\s*\[NEED_CONFIRM\]` 匹配（正则 `\]` 结尾不匹配 `倾向:` 开头）——实际上 `[NEED_CONFIRM倾向: X]` 的 `]` 在末尾，`\[NEED_CONFIRM\]` 要求 `]` 紧跟 `NEED_CONFIRM`，不匹配 `倾向`。安全。
