---
task_id: agate-self-gate
agent: main
date: 2026-07-01
status: 设计文档（待评审）
---

# agate 自身变更的 gate — 协议-脚本语义对齐审查

## 1. 问题

### 1.1 agate 适用于其他项目的自动化推进，但 agate 改自己时没有对等机制

agate 给项目提供的防护层：

| 项目侧层 | 机制 | 作用 |
|---------|------|------|
| 脚本 gate | check-gate.sh 等 10 个脚本 | 确定性检查产出文件 |
| 语义 gate | P2 评审 subagent | 独立上下文审查设计方案 |
| 验收 gate | P6 BDD + P7 一致性 | 行为验证 + 实现vs设计对照 |
| CI 兜底 | GitHub Actions | 重跑 gate + 一致性检查 |

agate 改自己时的现状：

| agate 自身层 | 现有机制 | 缺口 |
|-------------|---------|------|
| 脚本正确性 | 154 bats 测试 | 只测"脚本逻辑对不对"，不测"文档和脚本是否语义一致" |
| 结构一致性 | check-protocol-consistency.py（8 项 CHECK）| 只检查 YAML 解析/死链/行号/计数，**不检查语义对齐** |
| 语义一致性 | **无** | 文档写了规则但脚本没实现/语义不一致 → 无 gate 拦截 |
| CI | 3 jobs | 不跑语义审查 |

### 1.2 实证：23 项漏检

深度审计（见附录 A）发现协议文档 vs 脚本实现的 23 项偏差：

- **2 个 ERROR**：规则未实现或语义相反
  - #1: MAX_RETRY 硬编码 3，文档说 P3/P5/P6/P7/P8 = 2
  - #2: 回退跳变文档说"强制 PAUSED"，脚本降级 WARNING 不拦截
- **8 个 WARN**：措辞差异/弱化检查
  - md5 去重声称 hook 强制但未实现、P3 裁剪条件文档说"需 low"脚本只禁 high、P4 gate 路径偏离、裁剪检查遗漏 P6 等
- **13 个 INFO**：exit 2 委派 / 主 Agent 手动职责，非脚本缺陷

这 23 项**全部不在现有 check-protocol-consistency.py 的检查范围内**。

### 1.3 为什么纯脚本不够

check-protocol-consistency.py 能做的：关键词存在性、文件引用存在性、YAML 可解析、计数对照。

做不到的：
- 文档说"≤ 5"，脚本实现的是"< 5"还是"≤ 5"？
- 文档说"retries 超限须 PAUSED"，脚本检查的是 `>= 3` 还是 `> 3`？用哪个 MAX_RETRY？
- 新加的协议规则，脚本实现是否覆盖了所有子条件？
- 脚本实现了检查，文档描述是否准确反映了脚本的实际行为？

这些是**语义判断**，需要 LLM 理解上下文后判定。

### 1.4 设计原则

> **LLM 做语义审查 + 脚本做结构兜底，两层叠加。**

- LLM 层：改协议/脚本时人工触发，独立上下文的 review subagent 逐项审查语义对齐
- 脚本层：CI 每次 push 自动跑，确定性兜底，只抓"关键词缺失"级问题

两层都不可少——脚本层防止"完全忘了改"，LLM 层防止"改了但语义不一致"。

---

## 2. Layer 0：脚本结构兜底（CHECK 9）

### 2.1 定位

check-protocol-consistency.py 新增 CHECK 9，**不替代 LLM 语义审查**，只做确定性结构检查。

### 2.2 检查项

CHECK 9 扫描协议文档中所有"gate 检查项声明"，核对对应脚本是否含相关关键词。

**锚点表**（白名单式，和 CHECK 5 同模式）：

| 锚点 | 文档位置 | 脚本 | 关键词 |
|------|---------|------|--------|
| 裁剪 P2 条件 | state-machine.md 裁剪表 | check-pruning.sh | `design_trivial` / `follows_existing_pattern` / `legacy_p2_pruned` |
| 裁剪 P3 条件 | 同上 | check-pruning.sh | `risk_level` |
| 裁剪 P6 条件 | 同上 | check-pruning.sh | `no_behavior_change` |
| 裁剪 P7 条件 | 同上 | check-pruning.sh | 源码文件数检查 |
| 裁剪 P8 条件 | 同上 | check-pruning.sh | `internal_only` |
| 重试上限 | state-machine.md 重试表 | check-state-transition.sh | `MAX_RETRY` |
| 回退跳变 | state-machine.md 转移规则 | check-state-transition.sh | `diff` / `phase_num` |
| PROD_TOUCHED | dispatch-protocol.md gate 表 | pre-commit-gate.sh | `PROD_TOUCHED` |
| SCOPE+ 追踪 | state-machine.md | check-scope-resolved.sh | `SCOPE_RESOLVED` |
| DESIGN_GAP 配对 | state-machine.md | check-gate.sh | `DESIGN_GAP` |
| P6 evidence | dispatch-protocol.md 门槛表 | check-p6-evidence.sh | `ui_affected` |
| P6 截图去重 | dispatch-protocol.md 门槛表 | check-p6-evidence.sh | `md5` / `去重` |
| P6 provenance | 同上 | check-p6-provenance.sh | `PASS` / `Evidence` |
| P6 裁剪跳过风险 | state-machine.md 裁剪表 | check-pruning.sh | `P6` + `跳过风险` |
| 复盘提醒 | state-machine.md | check-retrospective.sh | `retries` |
| P2 候选方案质量 | dispatch-protocol.md gate 表 | check-gate.sh | `权衡` / `选择理由` |
| P8 CHANGELOG | dispatch-protocol.md 门槛表 | check-changelog.sh | `CHANGELOG` / `task_id` |
| state.yaml 结构 | state-machine.md 状态文件节 | check-state-yaml.sh | `task_id` / `phase` / `retries` |
| TDD 红灯 | dispatch-protocol.md 门槛表 | check-tdd-red.sh | `pytest` / `ImportError` |

### 2.3 输出

- **PASS**：所有锚点的关键词在对应脚本中找到
- **WARN**：锚点关键词未找到（可能是措辞差异，需 LLM 确认）
- **ERROR**：锚点脚本文件不存在

### 2.4 局限性（明确记录）

CHECK 9 只能确认"关键词存在"，不能确认"语义一致"。例如：
- 文档说"MAX_RETRY = 2"，脚本有 `MAX_RETRY=3` → CHECK 9 PASS（关键词存在），但语义不一致
- 文档说"强制 PAUSED"，脚本有 `echo 警告` → CHECK 9 PASS，但语义不一致

**语义一致性由 Layer 1（LLM 审查）保证。**

### 2.5 审计 WARN 的锚点覆盖分类

对附录 A 中 WARN #3-#10 逐条判定"能否设计关键词级结构锚点"：

| WARN # | 描述 | 能否加锚点 | 理由 |
|--------|------|-----------|------|
| #3 | md5 去重声称 hook 强制但未实现 | ✅ 已加 | `md5` / `去重` 关键词在 check-p6-evidence.sh 中缺失即 WARN |
| #4 | P3 gate 不检查 UI 用例存在性 | ❌ 只靠 LLM | "UI 用例"的识别方式不固定（playwright/e2e/cypress），关键词列举不全 |
| #5 | P3 裁剪文档说"需 low"，脚本只禁 high | ❌ 只靠 LLM | 关键词层面无法区分"需 low"和"禁 high"的语义差异 |
| #6 | P4 gate 路径偏离（文档说 P4-implementation/，脚本查任意暂存文件）| ❌ 只靠 LLM | 脚本里有 `git diff` 和路径过滤，但"是否查 P4-implementation/"需要语义理解 |
| #7 | 裁剪"跳过风险"检查遗漏 P6 | ✅ 已加 | check-pruning.sh 中 `P6` + `跳过风险` 关键词组合缺失即 WARN |
| #8 | P8 裁剪文档说"+ 理由"，脚本只检查 internal_only | ❌ 只靠 LLM | "理由"是自由文本，关键词存在不等于理由存在 |
| #9 | BDD 总数文档内部矛盾（= vs ≥）| ❌ 只靠 LLM | 文档内部矛盾需要跨文件语义理解 |
| #10 | P2 候选方案文档说"权衡+选择理由"，脚本只查数量 ≥2 | ✅ 已加 | check-gate.sh 中 `权衡` / `选择理由` 关键词缺失即 WARN |

**结论**：8 条 WARN 中 3 条可加锚点（#3/#7/#10），5 条只能靠 LLM 层。标注盲区本身有价值——维护者知道 CHECK 9 全绿不等于语义对齐，5 类偏差只能靠 LLM 审查覆盖。

### 2.5 集成

- 加入 check-protocol-consistency.py 作为 CHECK 9
- CI 的 consistency job 自动覆盖
- bats 测试 `consistency.bats` 加 CHECK 9 用例

---

## 3. Layer 1：LLM 语义审查 gate

### 3.1 触发时机

**不是 CI 自动跑**——LLM 审查需要人触发，因为：
- LLM 判断不可复现，不能作为 CI gate
- 审查需要理解变更意图，不是每次 push 都值得

**触发条件**：以下任一变更 commit 时：
- `agate/scripts/*.sh` 有改动
- `agate/scripts/check-protocol-consistency.py` 有改动
- `agate/**/*.md` 有改动（含协议文档、角色文件、模板文件）

**为什么用 `agate/**/*.md` 而非逐一列举**：v0.6 实施经验表明，角色文件（execution-roles/*.md、review-roles/*.md）和模板文件（templates/*.md）改动引发语义偏差的概率不低于协议文档本身。例如 DESIGN_GAP 功能同时改了 implementer.md、architect.md 和 check-gate.sh——如果只改了脚本没改角色文件，gate 会拦住所有任务。用通配符覆盖所有 .md 文件，避免逐一列举遗漏。

**触发方式**：主 Agent 在 commit 前主动派发 review subagent。不是 hook 自动触发——hook 无法调用 LLM。

### 3.2 流程

```
1. 主 Agent 完成 agate 协议/脚本变更
2. 主 Agent 派发 protocol-alignment-review subagent（task 工具）
   → 输入：变更 diff + 受影响文件全文 + 审查清单（见 3.4）
   → subagent 在独立上下文逐项审查
   → 产出：docs/reviews/agate-alignment-review-{date}.md
3. 主 Agent 读审查报告
   → ALIGNED：通过
   → MISALIGNED：必须修复，修完重审
   → NEEDS_HUMAN_REVIEW：标记，人工确认
4. 全部 ALIGNED 或 NEEDS_HUMAN_REVIEW 后，才允许 commit
```

### 3.3 输入导航（派发 prompt 模板）

主 Agent 不能只甩文件路径——派发时给 subagent 明确的审查方向（遵循 dispatch-protocol.md「输入导航原则」）：

```
你是 agate 协议-脚本对齐审查员。

## 变更内容
{diff 摘要：哪些文件改了什么}

## 审查范围
读以下文件全文：
- {变更的协议文件}
- {变更的脚本}
- agate/state-machine.md（裁剪表、重试表、转移规则——权威规则源）
- agate/dispatch-protocol.md（gate 表、门槛表——检查项声明源）

## 配套文件提示
根据变更内容，可能还需要读以下文件确认一致性：
- 如果变更涉及 gate 检查逻辑（check-gate.sh），同时读对应的角色文件
  （implementer.md / architect.md / verifier.md）确认角色侧描述是否一致
- 如果变更涉及文件格式/字段（check-pruning.sh / check-state-yaml.sh），
  同时读 assets/templates/task-files.md 确认模板是否一致
- 如果变更涉及 P6 证据格式，同时读 verifier.md 和 vision-analyst.md

## 审查清单
逐项检查（见 3.4 节），每项输出：
- 审查项编号
- 文档说了什么（引用原文 + 行号）
- 脚本实现了什么（引用代码 + 行号）
- 结论：ALIGNED / MISALIGNED / NEEDS_HUMAN_REVIEW
- 若 MISALIGNED：具体差异描述 + 建议修复方向

## 产出
写到 docs/reviews/agate-alignment-review-{date}.md
```

### 3.4 审查清单

| # | 审查项 | 说明 | 数据源 |
|---|--------|------|--------|
| A1 | 文档→脚本对齐 | 变更涉及的协议规则，对应脚本是否同步实现？语义是否一致？ | state-machine.md 裁剪表/重试表/转移规则 → 对应 check-*.sh |
| A2 | 脚本→文档对齐 | 变更涉及的脚本逻辑，对应协议文档是否同步更新？ | check-*.sh 改动 → state-machine.md / dispatch-protocol.md |
| A3 | 一致性连锁 | 变更是否需要同步改其他协议文件？ | 如 WORKFLOW.md 改了裁剪条件，state-machine.md 和 dispatch-protocol.md 是否一致？ |
| A4 | 测试覆盖 | 变更是否有对应 bats 测试？测试是否覆盖了新逻辑的边界？ | tests/ 下对应 .bats 文件 |
| A5 | 下游影响 | 变更是否影响已有项目的 gate 行为？是否有破坏性变更？ | 变更的 gate 逻辑是否改变现有 PASS/FAIL 判定 |
| A6 | 锚点表覆盖 | CHECK 9 的锚点表是否需要更新？ | 新增的协议规则是否需要加入 CHECK 9 锚点表？ |

### 3.5 产出格式

```markdown
---
review_date: 2026-07-01
reviewer: protocol-alignment-review
change_summary: {一句话变更摘要}
files_changed: [{文件列表}]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED / MISALIGNED / NEEDS_HUMAN_REVIEW |
| A2 | 脚本→文档对齐 | ... |
| A3 | 一致性连锁 | ... |
| A4 | 测试覆盖 | ... |
| A5 | 下游影响 | ... |
| A6 | 锚点表覆盖 | ... |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（state-machine.md:428-437）：
> P3 MAX_RETRY = 2

**脚本实现**（check-state-transition.sh:12）：
> MAX_RETRY=3

**结论**：MISALIGNED
**差异**：文档规定 P3/P5/P6/P7/P8 重试上限为 2，脚本硬编码统一为 3。
**建议**：脚本实现按阶段差异化 MAX_RETRY，或文档统一为 3。

---

### A2: 脚本→文档对齐
...
```

### 3.6 闭环规则

| 结论 | 主 Agent 动作 |
|------|--------------|
| ALIGNED | 通过，可 commit |
| MISALIGNED | **必须修复**——修脚本或修文档（看哪个是对的），修完重审 |
| NEEDS_HUMAN_REVIEW | 标记到审查报告，人工确认后可 commit（附确认理由）|

**NEEDS_HUMAN_REVIEW 的确认标记**：

和 `[DESIGN_GAP]` → `[DESIGN_GAP_REVIEWED]`、`[SCOPE+]` → `[SCOPE_RESOLVED]` 同模式，每条 NEEDS_HUMAN_REVIEW 必须有一条 `[HUMAN_CONFIRMED: ...]` 配对：

```markdown
### A3: 一致性连锁

**结论**：NEEDS_HUMAN_REVIEW
**差异**：P3 裁剪条件文档说"需 low"，脚本只禁 high，测试与脚本一致但与文档矛盾。
[HUMAN_CONFIRMED: 2026-07-01 确认：这是有意的设计取舍，P3 裁剪条件文档将在 v0.9 统一措辞]
```

主 Agent commit 前检查：审查报告里每条 NEEDS_HUMAN_REVIEW 下面都有 `[HUMAN_CONFIRMED: ...]`。未确认的 NEEDS_HUMAN_REVIEW 等同于 MISALIGNED——不允许 commit。这不是脚本自动化检查（LLM 审查本身不是脚本化的），但给人工确认提供可追溯的落盘格式。

**禁止**：跳过审查直接 commit。等同于项目侧"跳过 gate 直接推进"——正是 agate 要防的行为。

### 3.7 与项目侧 agate 流程的对应

| 项目侧 | agate 自身 |
|--------|-----------|
| check-gate.sh（脚本 gate）| check-protocol-consistency.py CHECK 1-9（脚本 gate）|
| P2 评审 subagent（语义 gate）| protocol-alignment-review subagent（语义 gate）|
| P6 BDD 验收 | bats 测试 |
| P7 一致性检查 | A3 一致性连锁审查 |
| pre-commit hook 兜底 | 主 Agent 主动派发（hook 无法调 LLM）|

---

## 4. 角色文件

### 4.1 新增 assets/review-roles/protocol-alignment-review.md

```markdown
---
role_id: protocol-alignment-review
type: review
phases: [pre-commit]
agent: review
---

# 协议-脚本对齐审查员

**定位**：agate 改自己时的语义 gate。独立上下文审查协议文档和脚本的语义一致性。

## 审查范围
（见 plan 文档 3.4 节审查清单 A1-A6）

## 审查原则
1. **逐项引用原文**：每项审查必须引用文档原文（行号）和脚本代码（行号），不说"大概一致"
2. **语义判断而非关键词匹配**：不只要看关键词存在，要看语义是否一致（≤ vs <、强制 vs 建议、拦截 vs 警告）
3. **不改代码**：审查角色只写报告，修复由主 Agent 派 implementer 落地
4. **NEEDS_HUMAN_REVIEW 用于真模糊**：如果无法确定是对是错（如设计决策的取舍），标 NEEDS_HUMAN_REVIEW，不要猜

## 输出格式
（见 plan 文档 3.5 节产出格式）

## 人工验收清单（每次使用后核对）

- [ ] 审查报告含 A1-A6 六项，每项有结论
- [ ] MISALIGNED 项有差异描述 + 建议方向
- [ ] 每条 NEEDS_HUMAN_REVIEW 下面有 [HUMAN_CONFIRMED: ...] 标记
- [ ] 审查报告落盘到 docs/reviews/agate-alignment-review-{date}.md
```

---

## 5. 文档改动

### 5.1 AGENTS.md（repo-root）

加"改 agate 协议本体的检查清单"节：

```markdown
## 改 agate 协议本体的检查清单

改协议文档或脚本时，除了常规测试，还需：

1. **跑 check-protocol-consistency.py** — 确认 CHECK 1-9 无 ERROR
2. **派发 protocol-alignment-review subagent** — 语义对齐审查
3. **读审查报告** — MISALIGNED 必须修复，NEEDS_HUMAN_REVIEW 人工确认
4. **跑全量 bats** — 确认无退化
5. **如果改了 gate 逻辑** — 确认下游项目（如 PeekView）的 gate 仍能跑通

触发条件：agate/scripts/*.sh 或 agate/*.md 有改动时。
```

### 5.2 LIMITATIONS.md

更新局限 5，补充：

```markdown
**缓解（v0.8）**：协议-脚本语义对齐审查（protocol-alignment-review）。
改协议/脚本时派发独立 review subagent 做语义审查，CHECK 9 做结构兜底。
语义一致性仍非 100% 自动化——需要人触发审查 + 人确认 NEEDS_HUMAN_REVIEW 项。
```

### 5.3 orchestrator-template.md

Hardening 节补一句：

```markdown
- **agate 自身变更**：改协议/脚本时派发 protocol-alignment-review subagent 做语义对齐审查（见 AGENTS.md 检查清单）
```

---

## 6. 脚本改动

### 6.1 check-protocol-consistency.py 扩展

新增 CHECK 9（`check_script_alignment`函数）：

- 锚点表（见 2.2 节）
- 逻辑：读锚点文档位置 → 提取关键词 → grep 对应脚本
- 输出：PASS / WARN / ERROR

### 6.2 不改的脚本

| 不改 | 理由 |
|------|------|
| pre-commit-gate.sh | LLM 审查不是 hook，是主 Agent 主动派发 |
| install-hook.sh | 不需要新 hook |
| check-gate.sh 等 | 本方案不改项目侧 gate |

---

## 7. 测试计划

### 7.1 CHECK 9 单元测试

`tests/unit/check-consistency-alignment.bats`（或扩展现有 consistency.bats）：

| # | 用例 | 预期 |
|---|------|------|
| 1 | 锚点脚本存在 + 关键词存在 | PASS |
| 2 | 锚点脚本不存在 | ERROR |
| 3 | 锚点关键词未找到 | WARN |
| 4 | 新增锚点项 | PASS |
| 5 | 删除锚点项（锚点表过期） | WARN |

### 7.2 可自动化部分（bats 测试）

LLM 审查不可 CI 化，但审查流程的脚手架可以测试：

`tests/integration/protocol-alignment-review.bats`：

| # | 用例 | 预期 |
|---|------|------|
| 1 | 角色文件 `protocol-alignment-review.md` 存在且含必需 frontmatter | role_id/type/phases/agent 字段存在 |
| 2 | 触发条件检测：给定变更文件列表含 `agate/scripts/*.sh` | 触发标记 = true |
| 3 | 触发条件检测：给定变更文件列表含 `agate/assets/**/*.md` | 触发标记 = true |
| 4 | 触发条件检测：给定变更文件列表只含 `README.md` | 触发标记 = false |

### 7.3 不可自动化部分（人工验收清单）

放在 `assets/review-roles/protocol-alignment-review.md` 角色文件末尾：

```markdown
## 人工验收清单（每次使用后核对）

- [ ] 审查报告含 A1-A6 六项，每项有结论
- [ ] MISALIGNED 项有差异描述 + 建议方向
- [ ] 每条 NEEDS_HUMAN_REVIEW 下面有 [HUMAN_CONFIRMED: ...] 标记
- [ ] 审查报告落盘到 docs/reviews/agate-alignment-review-{date}.md
```

### 7.4 回归测试

`tests/regression/v0.5.1-alignment.bats`：

模拟审计发现的 2 个 ERROR 场景：
- MAX_RETRY 文档说 2 脚本写 3 → 审查报告标 MISALIGNED
- 回退跳变文档说强制 PAUSED 脚本降级 WARNING → 审查报告标 MISALIGNED

### 7.5 测试用例计数

新增约 9 个用例（5 + 4）。
154 → 约 163。

---

## 8. 实现顺序

1. **修审计发现的 2 个 ERROR**（#1 MAX_RETRY + #2 回退跳变）——先让现有协议和脚本对齐
2. **CHECK 9 实现** — check-protocol-consistency.py 扩展 + 单元测试
3. **角色文件** — assets/review-roles/protocol-alignment-review.md
4. **派发模板** — dispatch-protocol.md 补 protocol-alignment-review 派发模板
5. **文档改动** — AGENTS.md / LIMITATIONS.md / orchestrator-template.md
6. **集成测试 + 回归测试**
7. **全量测试 + consistency + shellcheck**
8. **版本号 v0.8.0**

---

## 9. 不做的事

| 不做 | 理由 |
|------|------|
| LLM 审查 CI 化 | LLM 判断不可复现，不能作为 CI gate |
| hook 自动触发 LLM 审查 | hook 无法调用 LLM；主 Agent 主动派发是正确流程 |
| 审查所有协议文件 | 只审查受变更影响的文件，不做全量扫描（成本太高）|
| 替代 bats 测试 | LLM 审查是语义层，bats 是行为层，互补不替代 |
| 项目侧 gate 改动 | 本方案只针对 agate 自身变更，不影响项目侧流程 |

---

## 10. 风险与缓解

### 10.1 LLM 审查质量不稳定

**风险**：不同次审查结论不一致，同样的变更有时 ALIGNED 有时 MISALIGNED。

**缓解**：
- 审查清单明确（A1-A6），每项要求引用原文+代码，减少主观判断空间
- NEEDS_HUMAN_REVIEW 用于真模糊地带，不强制 LLM 给确定结论
- 审查报告落盘，可回溯——如果后续发现问题，可以看审查时漏了什么

### 10.2 主 Agent 跳过审查

**风险**：主 Agent 觉得"小改动不用审查"直接 commit。

**缓解**：
- AGENTS.md 检查清单写明触发条件（scripts/*.sh 或 agate/*.md 改动）
- CHECK 9 在 CI 跑，如果锚点表没更新会 WARN——提醒主 Agent "改了脚本但没跑审查"
- 和项目侧"gate 主动验 vs hook 兜底"同理：主 Agent 主动派发是主流程，CHECK 9 是兜底

### 10.3 锚点表过期

**风险**：新增协议规则但忘了加入 CHECK 9 锚点表。

**缓解**：
- A6 审查项专门检查"锚点表是否需要更新"
- 新增协议规则时，派发审查的 prompt 模板里有"审查清单 A6"提醒

---

## 附录 A：审计发现明细（2026-07-01 深度审计）

### ERROR 级（2 项）

| # | 类型 | 文档位置 | 脚本位置 | 描述 |
|---|------|---------|---------|------|
| 1 | SEMANTIC_MISMATCH | state-machine.md:428-437（P3/P5/P6/P7/P8 MAX_RETRY=2）| check-state-transition.sh:12 `MAX_RETRY=3` | 脚本对所有阶段用统一 MAX_RETRY=3，未实现按阶段差异化上限 |
| 2 | SEMANTIC_MISMATCH | state-machine.md:407-411「强制 PAUSED」| check-state-transition.sh:63-67 降级 WARNING | 回退跳变 ≥2 阶段：文档说强制 PAUSED，脚本仅 WARNING 不拦截 |

### WARN 级（8 项）

| # | 类型 | 描述 |
|---|------|------|
| 3 | DOC_WITHOUT_SCRIPT | md5 去重声称 hook 强制但未实现 |
| 4 | DOC_WITHOUT_SCRIPT | P3 gate 不检查 UI 用例存在性（文档说 gate 不通过）|
| 5 | SEMANTIC_MISMATCH | P3 裁剪文档说"需 low"，脚本只禁 high（允许 medium）|
| 6 | SEMANTIC_MISMATCH | P4 gate 文档说查 P4-implementation/，脚本查任意暂存代码文件 |
| 7 | SEMANTIC_MISMATCH | 裁剪"跳过风险"检查遗漏 P6 |
| 8 | SEMANTIC_MISMATCH | P8 裁剪文档说"+ 理由"，脚本只检查 internal_only: true |
| 9 | SEMANTIC_MISMATCH | BDD 总数文档内部矛盾（dispatch 说 =，LIMITATIONS 说 ≥）|
| 10 | SEMANTIC_MISMATCH | P2 候选方案文档说"权衡+选择理由"，脚本只查数量 ≥2 |

### INFO 级（13 项）

#11-#23：exit 2 委派 / 主 Agent 手动职责 / 脚本细化文档模糊描述，非脚本缺陷。详见审计报告原始数据。

---

## 附录 B：与 hotfix-evidence plan 的关系

`agate-hotfix-evidence-2026-07-01.md` 是项目侧改进（hotfix 协议 + evidence L3 + 诊断优先）。
本方案是 agate 自身变更机制的改进。

两者独立，可并行实现。实现顺序建议：
1. 先修审计发现的 2 个 ERROR（本方案 step 1）
2. 再做 hotfix-evidence（项目侧改进）
3. 最后做本方案的 CHECK 9 + LLM 审查（自身变更机制）

理由：先修已知 bug，再加新功能，最后加变更机制。
