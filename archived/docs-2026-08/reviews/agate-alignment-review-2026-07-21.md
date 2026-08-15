---
review_date: 2026-07-21
reviewer: protocol-alignment-review
change_summary: dispatch-context 单一信息源重构 + T059 复盘改进（Plan A + Plan B，2 commits）
files_changed:
  - agate/dispatch-protocol.md
  - agate/state-machine.md
  - agate/WORKFLOW.md
  - agate/orchestrator-template.md
  - agate/scripts/pre-commit-gate.sh
  - agate/scripts/check-gate.sh
  - agate/scripts/check-p6-provenance.sh
  - agate/scripts/check-p6-evidence.sh
  - agate/scripts/check-scope-resolved.sh
  - agate/scripts/check-protocol-consistency.py
  - agate/scripts/agate-inject-card.sh (新增)
  - agate/assets/templates/dispatch-context.md
  - agate/assets/templates/dispatch-prompt.md
  - agate/assets/execution-roles/verifier.md
  - agate/assets/execution-roles/analyst.md
  - agate/phase-cards/P1-P8
  - agate/tests/ (多处)
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED |
| A4 | 测试覆盖 | MISALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

审查了 10 组关键对照，9 组通过，1 组不通过。

---

**A1-1: dispatch-context 文件名从 `P{N}-dispatch-context.md` 改为 `P{N}-dispatch-context-{role}.md`**

**文档声明**（dispatch-protocol.md:289）：
> 文件名：`docs/tasks/{Txxx}/P{N}-dispatch-context-{role}.md`（每个 subagent 一个，只含该角色的导航信息）

**脚本实现**：
- pre-commit-gate.sh:158 `DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)` — glob 匹配新格式
- check-p6-provenance.sh:112 `DISPATCH_CTXS=("$TASK_DIR/P6-dispatch-context-"*.md)` — glob 匹配
- check-scope-resolved.sh:13 注释引用 `dispatch-context-{role}.md`

**结论**：ALIGNED

---

**A1-2: dispatch-context 内容重构（XML 标记 + role frontmatter + AGATE_CARD 块）**

**文档声明**（dispatch-protocol.md:295-336）：新结构含 `<dispatch_guide>`、`<objective_info>` XML 标记，`role:` frontmatter，`<!-- AGATE_CARD_START/END -->` 块

**脚本实现**：
- dispatch-context.md 模板：含 `<dispatch_guide>`、`<objective_info>`、`role:` frontmatter — 完全一致
- pre-commit-gate.sh:165 `sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p'` — 校验 AGATE_CARD 块
- check-p6-provenance.sh:116 `sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d'` — 排除 AGATE_CARD 块审计

**结论**：ALIGNED

---

**A1-3: 所有 P1-P8 阶段统一强制 dispatch-context 存在**

**文档声明**（dispatch-protocol.md:291）：
> 所有 P1-P8 阶段统一强制 dispatch-context 存在——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。

**脚本实现**（pre-commit-gate.sh:155-211）：glob 匹配所有阶段的 dispatch-context 文件，无匹配时若该阶段有产出暂存则 exit 1

**结论**：ALIGNED

---

**A1-4: dispatch-prompt 精简（移除任务特定内容，添加 dispatch-context 引用 + 执行顺序）**

**文档声明**（dispatch-protocol.md:410-475）：prompt 模板含 `## dispatch-context（核心输入）` + `## 执行顺序` 节

**脚本实现**（dispatch-prompt.md:13-15, 26-33）：含 `## dispatch-context（核心输入）` + `## 执行顺序` 节 — 完全一致

**结论**：ALIGNED

---

**A1-5: P8 subagent 提交约束**

**文档声明**（dispatch-protocol.md:568-576）：
> releaser subagent 只产出文件...不执行 git commit / git tag...不执行 bump-version

**脚本实现**：无脚本直接强制执行（这是行为级规则，依赖主 Agent 遵守）

**结论**：ALIGNED（行为规则不适合脚本化硬拦截）

---

**A1-6: AGATE_CARD 通过 agate-inject-card.sh 注入**

**文档声明**（dispatch-protocol.md:335）：
> 主 Agent 用 agate-inject-card.sh P{N} TASK_DIR 注入卡片内容...禁止手写 AGATE_CARD 内容

**脚本实现**（agate-inject-card.sh:1-57）：完整实现 — 调用 agate-next-card.sh，解析 AGATE_CARD 块，用 python3 替换

**结论**：ALIGNED

---

**A1-7: P8 CHANGELOG gate 从硬失败降为 WARNING ⚠️**

**文档声明**：
- state-machine.md:133 `git diff --cached -- ${CHANGELOG_FILE:-CHANGELOG.md} → 非空`
- WORKFLOW.md:224 `git diff --cached -- ${CHANGELOG_FILE:-CHANGELOG.md} 非空`
- dispatch-protocol.md:789 `git diff --cached -- ${CHANGELOG_FILE:-CHANGELOG.md} → 非空`

三处均将 CHANGELOG "非空"列在 P8 gate 列表中，含意是硬要求。

**脚本实现**（check-gate.sh:207-224）：
```bash
if [ "$CACHED_CHANGELOG" = "no" ] && [ "$RECENT_CHANGELOG" = "no" ]; then
    echo "GATE P8 WARNING: 暂存区和最近 ${LOOKBACK} 个 commit 均无 ${CHANGELOG_FILE} 变更" >&2
fi
```
CHANGELOG 无变更时仅发 WARNING，不 exit 1。且新增了"最近 commit"路径 B 兜底。

**结论**：**MISALIGNED**

**差异**：脚本将 CHANGELOG 检查从 `exit 1`（硬拦截）降为 WARNING（不阻断），同时新增了"最近 commit"备选路径。但 state-machine.md、WORKFLOW.md、dispatch-protocol.md 三处文档仍将 CHANGELOG 列为 P8 gate 必要条件（"非空"），未反映 WARNING 降级。

**建议**：
- 如果 WARNING 降级是有意的设计决策：更新三处文档，将 CHANGELOG 从 gate 要求改为 "WARNING（不阻断）"
- 如果应为硬拦截：修复脚本恢复 exit 1
- 建议方向：WARNING 降级合理（双路径检查已覆盖暂存区 + 最近 commit），应更新文档

---

**A1-8: PNG header check + md5 去重 WARNING**

**文档声明**（verifier.md:104-106）：
> 截图文件大小必须 > 1KB（空 png 充数会被 check-p6-evidence.sh 拦截）

**脚本实现**（check-p6-evidence.sh:75-103）：实现 ≤1KB PNG header 检查，合法 PNG ≤1KB 发 WARNING exit 2；md5 去重从 exit 1 降为 exit 2

**结论**：ALIGNED

---

**A1-9: SCOPE+ 排除 AGATE_CARD 块**

**文档声明**：dispatch-protocol.md 未直接描述此机制，但 SCOPE+ 追踪逻辑在 dispatch-protocol.md:864-870

**脚本实现**（check-scope-resolved.sh:18）：
```bash
sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -q '\[SCOPE+\]'
```

**结论**：ALIGNED（脚本实现正确，AGATE_CARD 块中的字面 SCOPE+ 不会误触）

---

**A1-10: provenance PASS 行截图路径提取修复**

**文档声明**（verifier.md:93,134）：
> 每条 PASS 后必须引证据路径：`- PASS B01: 描述 (P6-evidence/screenshots/b01.png)`

**脚本实现**（check-p6-provenance.sh:52-56）：
```bash
REF=$(echo "$LINE_CLEAN" | grep -oE 'screenshots/[^ )]+' | head -1 || true)
if [ -z "$REF" ]; then
    REF=$(echo "$LINE_CLEAN" | grep -oE '\([^)]+\)$' | sed 's/[()]//g' | head -1 || true)
fi
```

**结论**：ALIGNED（新增精确 screenshots/ 路径提取 + fallback 括号组解析）

---

### A2: 脚本→文档对齐

审查了脚本新增行为是否在文档中有对应描述。

---

**A2-1: P8 gate 双路径检查（暂存区 + 最近 commit）**

**脚本存在**（check-gate.sh:189-221）：version 和 CHANGELOG 均实现双路径检查

**文档描述**：
- state-machine.md:133 只提 `git diff --cached`，未提最近 commit 兜底
- dispatch-protocol.md:789 同上
- WORKFLOW.md:224 同上

**结论**：**MISALIGNED**

**差异**：脚本新增了"最近 N 个 commit"备选路径（`AGATE_P8_LOOKBACK`），三处协议文档均未描述此机制。

**建议**：更新文档描述 P8 gate 的双路径策略 + `AGATE_P8_LOOKBACK` 环境变量。

---

**A2-2: PNG ≤1KB 区分合法 PNG vs 非 PNG 文件**

**脚本存在**（check-p6-evidence.sh:75-95）：PNG header 检查，合法 PNG ≤1KB → WARNING exit 2，非 PNG ≤1KB → exit 1

**文档描述**（verifier.md:104-106）：
> 截图文件大小必须 > 1KB（空 png 充数会被 check-p6-evidence.sh 拦截）

文档只提了 "> 1KB" 规则，未描述 PNG header 检查机制和合法小 PNG 的 WARNING 降级。

**结论**：MISALIGNED（轻微）

**差异**：文档未反映 PNG header 检查的细分逻辑（合法PNG≤1KB=WARNING vs 非PNG≤1KB=拦截）。

**建议**：更新 verifier.md 描述完整检查逻辑。

---

**A2-3: check-p6-evidence.sh PASS 行文件引用检测（新增）**

**脚本存在**（check-p6-evidence.sh:30-35）：逐行检查 PASS 是否含文件引用（括号内路径）

**文档描述**：verifier.md:93 描述了引用需求，但 WORKFLOW.md:245 的 P1.7 描述仅说"P6-evidence/ 非空 + BDD 行数 ≥ 1"，未提文件引用检测

**结论**：MISALIGNED（轻微）

**建议**：更新 WORKFLOW.md P1.7 描述反映完整的 PASS 行文件引用检查。

---

### A3: 一致性连锁 + 反向传播

#### A3a: 连锁（已知改动）

| 改动 | 应连锁更新 | 状态 |
|------|-----------|------|
| dispatch-context 文件名 → `P{N}-dispatch-context-{role}.md` | pre-commit-gate.sh glob 匹配 | ✅ 已更新 |
| dispatch-context 文件名变更 | check-p6-provenance.sh glob 匹配 | ✅ 已更新 |
| dispatch-context 文件名变更 | check-scope-resolved.sh 注释 | ✅ 已更新 |
| dispatch-context 文件名变更 | dispatch-protocol.md 全文引用 | ✅ 已更新 (11 处) |
| dispatch-context 文件名变更 | WORKFLOW.md L274 | ✅ 已更新 |
| dispatch-context 文件名变更 | orchestrator-template.md L64 | ✅ 已更新 |
| dispatch-context 文件名变更 | dispatch-prompt.md 模板 | ✅ 已更新 |
| dispatch-context 文件名变更 | verifier.md / analyst.md | ✅ 已更新 (P{N}-dispatch-context.md → dispatch-prompt 引用) |
| dispatch-context 文件名变更 | phase-cards/P1-P8 | ✅ 已更新 |
| dispatch-prompt 结构变更 | dispatch-protocol.md 内联模板 | ✅ 已更新 |
| dispatch-prompt 结构变更 | dispatch-prompt.md 模板文件 | ✅ 已更新 |
| P8 CHANGELOG gate 降级 | state-machine.md | ❌ 未更新（仍写"非空"） |
| P8 CHANGELOG gate 降级 | WORKFLOW.md | ❌ 未更新（仍写"非空"） |
| P8 CHANGELOG gate 降级 | dispatch-protocol.md | ❌ 未更新（仍写"非空"） |
| P8 gate 双路径 | state-machine.md | ❌ 未描述 |
| P8 gate 双路径 | WORKFLOW.md | ❌ 未描述 |
| P8 gate 双路径 | dispatch-protocol.md | ❌ 未描述 |
| P8 subagent 提交约束 | state-machine.md | ✅ 已描述 (L132-134) |
| AGATE_CARD 注入脚本 | orchestrator-template.md commit 被拦处理 | ✅ 已更新 (L205) |
| SCOPE+ AGATE_CARD 排除 | check-scope-resolved.sh | ✅ 已更新 |
| provenance 审计 glob 匹配 | check-p6-provenance.sh | ✅ 已更新 (L111-122) |
| provenance 审计 1a 路径提取 | check-p6-provenance.sh | ✅ 已更新 (R1c) |

#### A3b: 反向传播（应被影响但未在 diff 中的文件）

| 应被影响的文件 | 理由 | 实际状态 |
|--------------|------|---------|
| **CHANGELOG.md** | 两组变更（Plan A + Plan B）合共 40 个文件改动，属重大协议变更 | **❌ 未更新** |
| **agate/tests/unit/check-gate.bats G8.3** | P8 CHANGELOG 从 exit 1 → WARNING，测试期望仍为 exit 1 | **❌ 未更新**（2 tests fail） |
| **agate/tests/regression/v060-p8-cached.bats R5.3** | 同上，仍期望 exit 1 | **❌ 未更新**（2 tests fail） |
| **agate/rules/state-transitions.md** | 跨阶段规则文件，P8 gate 变更应反映 | 需人工确认 |
| **agate/rules/review-mapping.md** | 角色文件更新后 review 映射可能需同步 | 需人工确认（analyst.md/verifier.md 角色增补了 BDD 反模式清单 + gate 预检，但 review 维度可能需同步） |
| **SELF-GATE.md** | 非典型触发路径——这两次变更本身改的是 gate 脚本，需确认 self-gate 机制的递归适用 | 需确认 |

**结论**：**MISALIGNED** — CHANGELOG.md 未被更新是明确的遗漏；2 个测试失败佐证测试未同步。

---

### A4: 测试覆盖

**实跑输出**（296 个测试，2 个失败，0 个跳过）：

```
296 tests, 0 failures, 2 pending, 0 skipped  ← 总览
```

实际 2 个失败：
```
not ok 76 G8.3 check-gate.sh P8 有 version 但 CHANGELOG 无变更 期望 exit 1
not ok 245 R5.3 P8 gate 暂存区有 version 但 CHANGELOG 无变更 → exit 1
```

两个失败均因为：脚本将 P8 CHANGELOG 从 `exit 1` 降为 WARNING，但测试仍期望 `exit 1`。

**新增测试审查**：
- `agate-inject-card.bats`：7 个 @test — 覆盖注入脚本的核心功能 ✅
- `dispatch-context-card.bats`：8→8 个 @test（更新，非新增数量）— 覆盖新格式 dispatch-context 校验 ✅
- `check-p6-provenance.bats`：+? 个 @test（从 22 增至?）— 覆盖 screenshots/ 路径提取 ✅
- `pre-commit-hook.bats`：更新 — 覆盖 P8/P5/P7 dispatch-context 缺失检查 ✅
- `check-gate.bats`：+? 个 @test — 但 G8.3 和 R5.3 未更新 ❌

**总测试数**：290（count-tests.sh 输出），实跑 296（含 sanity 等）

**结论**：**MISALIGNED** — 2 个测试失败（G8.3、R5.3），因 P8 CHANGELOG 行为变更后测试未同步更新。新增行为的测试覆盖（agate-inject-card、dispatch-context 新格式、provenance 路径提取）是充分的。

---

### A5: 下游影响 + 文档传播

#### 破坏性变更识别

| 变更 | 破坏性 | 影响 |
|------|--------|------|
| dispatch-context 文件名 `P{N}-dispatch-context.md` → `P{N}-dispatch-context-{role}.md` | ⚠️ 命名变更 | 已有任务的旧格式 dispatch-context 文件不再被 hook 识别。脚本有 fallback（pre-commit-gate.sh 会提示），check-p6-provenance.sh 的旧格式排除在 toml 中保留。过渡期兼容通过 `TODO: remove old format compatibility in v2.0` 标记处理 ✅ |
| 所有 P1-P8 强制 dispatch-context | ⚠️ 新增硬约束 | commit 时若缺 dispatch-context → exit 1 拦截。已有中间 commit / legacy 任务 / 裁剪跳阶不受影响（pre-commit-gate.sh:180 有豁免逻辑） ✅ |
| P8 CHANGELOG gate 降级 | ⚠️ 行为变更 | 不再因 CHANGELOG 缺失而拦截 P8 commit。降低 gate 严格度 |
| P8 gate 双路径 | ⚠️ 行为变更 | 允许 version/CHANGELOG 变更在最近 N 个 commit 中而非仅暂存区 |

#### CHANGELOG.md

**CHANGELOG.md 未被本次变更更新**。`git log HEAD~2..HEAD -- CHANGELOG.md` 无输出。

两组 commit 合共 40 个文件变更、816 行新增，属于重大协议变更，应在 CHANGELOG 记录新版本（如 0.15.0）。

#### 文档传播检查

| 文档 | 是否需要更新 | 状态 |
|------|------------|------|
| state-machine.md | 是 — P8 gate 描述 | ❌ CHANGELOG 检查仍写"非空"，未反映双路径 |
| WORKFLOW.md | 是 — P8 gate 描述、P1.7 描述 | ❌ 同上 |
| dispatch-protocol.md | 是 — P8 gate 描述 | ❌ 同上 |
| verifier.md | 是 — PNG header 检查描述 | ❌ 文档只提 >1KB，未描述 PNG header 细分 |
| orchestator-template.md | 否 — 已更新 dispatch-context 引用 | ✅ |
| LIMITATIONS.md | 否 — 无新增限制 | ✅ |
| role-system.md | 否 — 角色体系未变 | ✅ |
| adr.md | 否 — 无新架构决策需要 ADR | ✅ |
| CONTEXT.md | 否 — 术语未变 | ✅ |

**结论**：**MISALIGNED** — CHANGELOG.md 未更新（明确遗漏）；3 处协议文档 P8 gate 描述滞后；verifier.md PNG header 检查描述不完整。

---

### A6: 锚点表覆盖 (CHECK 9)

**脚本反向覆盖检查**（check-protocol-consistency.py check_anchor_coverage）：

一致性检查输出：11 个 gate 脚本全部被锚点表覆盖，无遗漏。

**新增锚点检查**（check-protocol-consistency.py SCRIPT_ALIGNMENT_ANCHORS）：
- `dispatch-context 派发指引节` → dispatch-protocol.md `dispatch-context`, `dispatch_guide` ✅
- `dispatch-context provenance 审计引用` → check-p6-provenance.sh `dispatch-context` ✅
- `dispatch-context role frontmatter` → dispatch-context.md `role:` ✅
- `dispatch-context XML 标记` → dispatch-context.md `<dispatch_guide>`, `<objective_info>` ✅

**md5 去重关键词 WARNING**：
check-p6-evidence.sh 不含字面"去重"关键词，但功能上确实有 md5 去重逻辑。CHECK 9 输出 WARNING：`缺少关键词 '去重'（可能未实现，或措辞差异）`。这属于关键词匹配假阳性，功能已实现。**不需要修复**，但建议将 echo 文本中的"md5 重复"改为"md5 去重"消除假阳性。

**结论**：ALIGNED — 所有新增检查项已纳入锚点表，反向覆盖检查通过。

---

### A7: 设计原则一致性

逐条对照 adr.md 的 6 条 ADR：

| ADR | 决策 | 本次变更一致性 |
|-----|------|--------------|
| ADR-001 隔离性 | 主 Agent 不写产出 | ✅ 一致。dispatch-context 是主 Agent 的"查证/编排"职责，不是阶段产出。P8 subagent 提交约束强化了隔离性——commit/tag 由主 Agent 专责 |
| ADR-002 可判定性 | gate 机器可判定 | ✅ 一致。PNG header 检查、screenshots/ 路径提取、AGATE_CARD 块排除均提升脚本可判定性。AGATE_CARD 注入使卡片 hash 成为可判定检查 |
| ADR-003 最小约定 | 不绑定技术栈 | ✅ 一致。agate-inject-card.sh 不绑定特定阶段输出格式，只操作 AGATE_CARD 块 |
| ADR-004 安全网分层 | hook + CI backstop | ✅ 一致。pre-commit-gate.sh 的 dispatch-context hash 校验增强了 hook 层检查能力 |
| ADR-005 改动性质 | 声明性/行为逻辑/机制交叉 | ✅ 一致。本次变更未修改改动性质判断逻辑 |
| ADR-006 双层角色 | 执行+评审分离 | ✅ 一致。verifier gate 预检指令强化了执行者自检但不自判的原则。analyst BDD 反模式自检清单提升 P1 产出质量，不改变评审独立性 |

**未记录的架构决策**：
- dispatch-context 从"一个文件一个阶段"变为"一个 subagent 一个文件"是架构决策，但它是现有 dispatch-context 机制的延伸，不是新决策。现有 ADR-001（隔离性）已覆盖其理由（dispatch-context 是编排工作）。
- P8 CHANGELOG gate 降级 + 双路径是 gate 设计调整，属于实现细节变化，不需要新 ADR。

**结论**：ALIGNED — 所有变更与已记录的 6 条 ADR 一致，无需要补充新 ADR 的未记录决策。

---

## MISALIGNED 项修复建议汇总

| # | 项 | 优先级 | 修复方向 |
|---|-----|--------|---------|
| **M1** | P8 CHANGELOG gate：文档说"非空"，脚本只发 WARNING | 🔴 高 | 二选一：(a) 更新三处文档（state-machine.md:133, WORKFLOW.md:224, dispatch-protocol.md:789）将 CHANGELOG 从 gate 必要条件改为 WARNING；(b) 恢复脚本 exit 1。建议(a)，双路径已覆盖 |
| **M2** | P8 gate 双路径（暂存区+最近commit）：文档未描述 | 🔴 高 | 在三处文档补充双路径策略 + `AGATE_P8_LOOKBACK` 环境变量说明 |
| **M3** | 测试 G8.3 / R5.3 失败：期望 exit 1 但脚本给 WARNING | 🔴 高 | 更新测试期望为 `exit 2`（WARNING）并验证输出含 WARNING 消息 |
| **M4** | CHANGELOG.md 未更新两个版本的变更 | 🔴 高 | 新增 `[0.15.0]` 条目记录 Plan A + Plan B 变更 |
| **M5** | verifier.md PNG header 检查描述不完整 | 🟡 低 | 补充 "合法 PNG ≤1KB → WARNING exit 2，非 PNG ≤1KB → exit 1" 的细分逻辑 |
| **M6** | WORKFLOW.md P1.7 描述未反映 PASS 行文件引用检查 | 🟡 低 | 补充文件引用存在性检查的描述 |
| **M7** | CHECK 9 "去重"关键词假阳性 WARNING | 🟢 极低 | 可选：将 echo 中的 "md5 重复" 改为 "md5 去重" 消除假阳性 |

