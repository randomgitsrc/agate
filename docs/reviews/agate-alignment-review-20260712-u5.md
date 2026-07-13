---
review_date: 2026-07-12
reviewer: protocol-alignment-review
change_summary: U5 结构卫生——P6 CI证据原则(L0)、D2假完成校验表、P2候选方案正则语义化放宽、verification_env条件化、dispatch-context任务上下文节锚点
files_changed: [agate/dispatch-protocol.md, agate/assets/execution-roles/verifier.md, agate/assets/templates/dispatch-prompt.md, agate/orchestrator-template.md, agate/scripts/check-gate.sh, agate/scripts/check-protocol-consistency.py, agate/tests/unit/check-gate.bats, agate/tests/unit/check-p6-provenance.bats]
---

# 协议-脚本对齐审查 — U5

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | NEEDS_HUMAN_REVIEW |

## 逐项审查

### A1: 文档→脚本对齐

**④ P6 证据由 CI 执行生成原则（L0）**

文档声明（dispatch-protocol.md:693-699）：
> P6 证据由 CI 执行生成原则（长期目标，当前 L0 指导）：短期——若项目有 CI 流水线，优先要求 verifier 引用 CI 产出……⚠️ 安全收益为零

verifier.md:135 声明：
> CI 证据优先：若项目有 CI 流水线，优先引用 CI 产出路径……agent 自带证据是条件退让，非默认。

脚本侧：无脚本变更（L0 指导性声明，非 gate 强制）。provenance 1a 只验引用存在性不验来源，与文档"⚠️ 安全收益为零"自评一致。

**结论：ALIGNED** — 两处文档语义一致，L0 不需脚本强制。

---

**⑤ D2 假完成校验表**

文档声明（dispatch-protocol.md:79-90）D2 表 4 项：

| 校验项 | 文档方式 | 脚本实现 |
|--------|----------|----------|
| 代码文件真改了 | `git diff --stat HEAD` 或 `--cached --stat` | check-gate.sh P4:83 `git diff --cached --name-only \| grep -qvE` — 语义等价 |
| 测试真跑了 | grep test runner 输出签名于 P5-test-results/ | P5 gate exit 2（主 Agent 自判），文档也标注为主 Agent 行为 |
| review 真审查了 | N3 锚点检查（BDD 编号引用 / DESIGN_GAP 配对引用） | check-gate.sh P7:120-138 检查 DESIGN_GAP 配对 + P4/P7 交叉核对 |
| 验收真跑了 | provenance 审计（证据-结论对应 + BDD 总数对照） | check-p6-provenance.sh 审计 1 + 审计 3 完全覆盖 |

dispatch-prompt.md:66-70 "返回前自检"节 4 项与 D2 表对应，是 subagent 侧自检，与 D2 主 Agent 侧校验互补。

**结论：ALIGNED**

---

**⑥ P2 候选方案正则语义化放宽**

脚本实现（check-gate.sh:29）：
```bash
grep -cE '^###?\s*(候选方案|方案\s*[A-Za-z一二三四五]|Alternative|Option)'
```

变更：`方案\s*[ABC123abc]` → `方案\s*[A-Za-z一二三四五]|Alternative|Option`

**⚠️ 回归**：原 regex 含 `[123]`，匹配 `方案 1`/`方案 2`/`方案 3`。新 regex `[A-Za-z]` 不含数字，`方案 1` 不再匹配。实测确认：

```
$ echo '### 方案 1' | grep -cE '^###?\s*(候选方案|方案\s*[ABC123abc一二三四五])'  → 1
$ echo '### 方案 1' | grep -cE '^###?\s*(候选方案|方案\s*[A-Za-z一二三四五]|Alternative|Option)'  → 0
```

docs/plans/t048-improvements-20260708.md:58 明确列出了 `方案1` 为支持的格式。

**结论：ALIGNED**（文档→脚本方向：文档未显式要求阿拉伯数字方案名，但见 A5 破坏性变更评估）

---

**⑦ verification_env 条件化**

三处文档声明：
- dispatch-protocol.md:701-706：三条件触发（ui_affected / Playwright-e2e / known_risks 环境依赖）
- verifier.md:136：简化版（ui_affected=true 必填，其余无需声明）
- orchestrator-template.md:59：三条件完整列出

verifier.md 简化是角色文件面向执行者的合理简化，不是语义冲突。脚本侧无变更（L0 指导）。

**结论：ALIGNED**

### A2: 脚本→文档对齐

**P2 regex 扩展（Alternative/Option）→ 文档**

check-gate.sh:29 新增 `Alternative`、`Option` 匹配，但 dispatch-protocol.md 和 P2 phase card（P2-design.md）未提及这些英文方案名格式。P2-design.md phase card:40 只说"候选方案 ≥2"，:79 只说"候选方案数 ≥2"。

使用者写 `### Alternative A` / `### Option B` 能过 gate，但协议文档从未声明这是合法格式。

**结论：MISALIGNED** — 脚本接受了文档未声明的方案名格式（Alternative/Option）。修复方向：在 P2-design.md phase card 的 gate 规则节补充说明，或在 dispatch-protocol.md P2 描述中注明。

### A3: 一致性连锁 + 反向传播

**A3a 连锁（diff 中已知衍生改动）**

| 改动 | 衍生文件 | 状态 |
|------|----------|------|
| D2 假完成表 | dispatch-prompt.md "返回前自检" | ✅ 已在 diff |
| CI 证据原则 | verifier.md "CI 证据优先" | ✅ 已在 diff |
| verification_env 条件化 | verifier.md + orchestrator-template.md | ✅ 已在 diff |
| P2 regex 扩展 | check-gate.bats G2.21-G2.23 | ✅ 已在 diff |
| dispatch-context 任务上下文节 | check-protocol-consistency.py 锚点 + check-p6-provenance.bats PV.17 | ✅ 已在 diff |

**A3b 反向传播（应被影响但未在 diff 中的文件）**

| 推断文件 | 是否应受影响 | 实际状态 |
|----------|-------------|----------|
| P2-design.md phase card | regex 放宽后应补充 Alternative/Option 格式说明 | 未改（见 A2 MISALIGNED）|
| WORKFLOW.md | 无 gate 逻辑细节 | 无需改 |
| architect.md | 未提及方案名格式 | 无需改 |
| LIMITATIONS.md | 无相关 | 无需改 |
| CHANGELOG.md | 协议语义变更 | 未改，feature branch 合并前统一处理 |

**结论：ALIGNED**（P2 phase card 的 Alternative/Option 文档补充已在 A2 标记）

### A4: 测试覆盖

**bats 全量实跑输出**：

```
check-gate.bats: 61/61 passed
check-p6-provenance.bats: 19/19 passed
```

**新增测试覆盖**：
- G2.21: "方案 Alpha" + "方案 Beta" → exit 2 ✅
- G2.22: "Alternative A" + "Option B" → exit 2 ✅
- G2.23: "方案 Recommended" + "方案 Conservative" → exit 2 ✅
- PV.17: dispatch-context 含任务上下文节 → 审计 2 放行 ✅
- D-drift-4: dispatch-context.md 含"任务上下文"节 ✅

**缺失覆盖**：
- `方案 1`/`方案 2`（阿拉伯数字方案名）——旧 regex 支持但无测试，新 regex 也不支持。如需恢复此格式需加测试。
- verification_env 条件化：L0 指导，无脚本变更，无需 bats ✅
- CI 证据原则：L0 指导，无需 bats ✅

**一致性检查**：0 ERROR，8 WARNING（均为叙事文件引用，非协议文件）✅

**结论：ALIGNED**（现有新增测试覆盖了新逻辑边界）

### A5: 下游影响 + 文档传播

**P2 regex 变更的破坏性**：

原 regex `方案\s*[ABC123abc一二三四五]` 支持 `方案 1`/`方案 2`/`方案 3`（阿拉伯数字后缀）。
新 regex `方案\s*[A-Za-z一二三四五]` 不支持阿拉伯数字后缀。

实测验证：
```
echo '### 方案 1' | grep -cE '旧regex' → 1 (匹配)
echo '### 方案 1' | grep -cE '新regex' → 0 (不匹配)
```

影响：已有项目若 P2-design.md 使用 `方案 1`/`方案 2` 命名，升级后 P2 gate 将从 exit 2 变为 exit 1（候选方案数不足），**阻断现有工作流**。

docs/plans/t048-improvements-20260708.md:58 明确将 `方案1` 列为支持的格式，说明这是有意设计的功能。

**结论：MISALIGNED** — regex 变更引入破坏性回归，`方案 1`/`方案 2`/`方案 3` 不再被识别。修复方向：regex 中恢复 `[0-9]` 或 `[123]` 数字匹配，如 `方案\s*[A-Za-z0-9一二三四五]`。

**文档传播**：
- CHANGELOG.md 未更新——feature branch 合并前统一处理，此处不阻断。
- P2-design.md phase card 未补充 Alternative/Option 格式说明——见 A2。

### A6: 锚点表覆盖

check-protocol-consistency.py 新增锚点（:540-543）：

```python
{
    "desc": "dispatch-context 任务上下文节",
    "script": "agate/scripts/check-p6-provenance.sh",
    "keywords": ["dispatch-context"],
}
```

验证：check-p6-provenance.sh:100 含 `DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"`，关键词 `dispatch-context` 存在 ✅

**未覆盖的新行为**：

| 新行为 | 是否需要 CHECK 9 锚点 | 理由 |
|--------|----------------------|------|
| P2 regex Alternative/Option | NEEDS_HUMAN_REVIEW | 脚本新增了 Alternative/Option 匹配逻辑，但 CHECK 9 只做关键词存在性检查，而 regex 模式不是简单的关键词。现有 P2 锚点（`P2 不可裁剪`、`P2 agent=main 硬拦截`）不覆盖方案名格式检查。是否需要新增锚点取决于是否认为方案名 regex 是"文档声明的规则"——目前文档未声明 Alternative/Option 格式（见 A2），所以无法建立锚点 |
| D2 假完成校验 | 不需要 | D2 是主 Agent 行为指引，无脚本自动化检查 |
| CI 证据原则 | 不需要 | L0 指导，无脚本变更 |
| verification_env 条件化 | 不需要 | L0 指导，无脚本变更 |

**结论：NEEDS_HUMAN_REVIEW** — Alternative/Option regex 是否需要 CHECK 9 锚点取决于 A2 的修复决策。若 A2 修复后在文档中声明了这些格式，则应加锚点；若不加文档声明则无锚点可建。

---

## 闭环

| 结论 | 主 Agent 动作 |
|------|--------------|
| A1 ALIGNED | 通过 |
| A2 MISALIGNED | **必须修复**——在 P2-design.md phase card 或 dispatch-protocol.md 补充 Alternative/Option 为合法方案名格式 |
| A3 ALIGNED | 通过 |
| A4 ALIGNED | 通过 |
| A5 MISALIGNED | **必须修复**——check-gate.sh:29 regex 需恢复数字后缀匹配（`[A-Za-z]` → `[A-Za-z0-9]`），并补充 G2.24 测试覆盖 `方案 1` + `方案 2` |
| A6 NEEDS_HUMAN_REVIEW | 修复 A2 后决定是否加 CHECK 9 锚点 |

**总裁定：MISALIGNED — 2 项必须修复后方可 commit**
