---
review_date: 2026-07-02
reviewer: protocol-alignment-review
change_summary: pre-commit-gate.sh 重写为多任务 .state.yaml 扫描 + 新增 phase-产出一致性 WARNING（不拦截）
files_changed:
  - agate/scripts/pre-commit-gate.sh
  - agate/tests/integration/pre-commit-hook.bats
  - agate/state-machine.md
  - CHANGELOG.md
  - docs/plans/agate-issue-001-design-2026-07-02.md（设计文档，非协议本体）
留痕文件: docs/reviews/agate-alignment-2026-07-02-02.progress.md
---

# 协议-脚本对齐审查 — Issue #001（多任务 hook 适配 + phase-产出一致性检查）

## 意图分析

本次变更意图：**修复多任务架构下 pre-commit hook 静默放行的 bug**（hook 写死根 `.state.yaml`，多任务项目根目录无此文件 → 读不到 phase → exit 0 放行），并**补一个轻量 WARNING**覆盖"产出了 P{n} 文件但忘改 phase"的中间态。意图正确且必要——这是影响 PeekView 等下游项目实际可用性的 bug。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | **MISALIGNED**（多任务扫描本身 ALIGNED；但 CI backstop 依赖的 `.gate-result.json` 被删除，违反 state-machine.md:225 等声明） |
| A2 | 脚本→文档对齐 | **MISALIGNED**（脚本删了 `write_gate_result` 调用，但注释/load-check/死代码未同步） |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（dispatch-protocol.md pre-commit 表格未同步；ci-gate-backstop.py 消费方未同步；CHANGELOG 未标破坏性变更） |
| A4 | 测试覆盖 | **NEEDS_HUMAN_REVIEW**（IT.1-IT.10 全过，向后兼容 OK；但 IT.8/IT.9 未断言"无 WARNING"，且无 `.gate-result.json` 回归测试） |
| A5 | 下游影响 + 文档传播 | **MISALIGNED**（CHANGELOG 标了新增行为，但漏标 `.gate-result.json` 不再写 / CI backstop 降级这一破坏性影响） |
| A6 | 锚点表覆盖 | **ALIGNED**（PROD_TOUCHED 锚点仍命中；新 WARNING 规则未加锚点属可选增强，非强制） |

**总判定：MISALIGNED — 不允许直接 commit。** 主项是 A1/A2/A3 联动的 `.gate-result.json` 回归：重写时把 `write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"` 这行丢了，而 CI backstop（P1.3）依赖该文件做 `--no-verify` 绕过检测。需修复或显式退役该机制并同步全部文档/消费方。

---

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 多任务 .state.yaml 扫描** — ALIGNED

- 文档声明（state-machine.md:449）：`位置：docs/tasks/{Txxx}/.state.yaml`
- 文档声明（state-machine.md:223，本次新增）：`pre-commit-gate.sh 扫描暂存区中所有变更的 .state.yaml（根目录 + docs/tasks/{Txxx}/），对每个文件独立跑格式校验 + 状态转移 + gate`
- 脚本实现（pre-commit-gate.sh:40-49）：收集 `STAGED_STATE_FILES`（grep `.state.yaml`，含根 + 任务级）；52-152 行循环对每个文件跑格式校验 / 状态转移 / gate
- 结论：**ALIGNED**。扫描根 + 任务级，向后兼容根目录，与文档一致。

**A1.2 phase-产出一致性 WARNING** — ALIGNED

- 文档声明（state-machine.md:223）：`phase-产出不一致（暂存了 P{n}-*.md 但 phase 不匹配）只发 WARNING 不拦截`
- 脚本实现（pre-commit-gate.sh:87-101，2f 段）：对暂存的 `^${TASK_REL}/P[0-8]-.*\.md$` 提取 `out_phase`，与 `PHASE` 不等则 `echo GATE WARNING`，不 exit；154-184 行第 3 段对"无 .state.yaml 变更的任务"补做同一检查
- 结论：**ALIGNED**。WARNING 不拦截，覆盖"产出但忘改 phase"场景，与设计原则一致。

**A1.3 CI backstop 依赖 `.gate-result.json`** — MISALIGNED（关键）

- 文档声明（state-machine.md:225）：`CI 兜底（P1.3）：push 后 GitHub Actions 重跑 check-gate.sh + ci-gate-backstop.py，捕获 --no-verify 绕过 hook 的 commit`
- 文档声明（dispatch-protocol.md:641）：`捕获 --no-verify 绕过 hook 的 commit；并对 P6-acceptance.md 单 author 情况发 WARNING`
- 消费方实现（ci-gate-backstop.py:30）：`gate_result = repo_root / ".gate-result.json"`；53-90 行：文件不存在→WARN（无法区分"hook 跑了"与"--no-verify 绕过"）；存在则对照 phase/exit/timestamp
- 脚本实现（pre-commit-gate.sh 全文）：**不再调用 `write_gate_result`**。git diff 证实旧版有 `write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"`，重写后删除。
- 影响：hook 不再写 `.gate-result.json` → ci-gate-backstop.py:53-58 永远走"无 .gate-result.json"分支 → 只能靠 CI 重跑 gate 的 exit code 判断（gate 失败仍能 FAIL，但 gate 通过时无法检测 `--no-verify` 绕过，phase/exit 对照逻辑 66-72 行彻底失效）。单任务项目的 CI backstop 降级。
- 结论：**MISALIGNED**。脚本行为与文档声明的 P1.3 机制冲突。
- 建议修复方向（二选一）：
  1. **恢复写入**（推荐，最小改动）：在 2o 段 case 之前补回 `write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"`。多任务下注意路径——`write_gate_result` 当前写根目录 `.gate-result.json`，多任务会互相覆盖；可改为按 `TASK_DIR` 写，并同步 ci-gate-backstop.py 扫描任务级。但这扩大改动面。
  2. **显式退役**：若认定 `.gate-result.json` 机制已被 CI 重跑覆盖（gate 失败 CI 仍 FAIL），则删除 ci-gate-backstop.py 的 `.gate-result.json` 对照逻辑 + 删 gate-result.sh 的 `write_gate_result` + 更新 state-machine.md:225 / dispatch-protocol.md:641 / orchestrator-template.md:83 + CHANGELOG 标注破坏性变更。改动面更大但语义更干净。
- 设计文档自身的分歧：设计文档第 58f 行写"gate 结果按任务路径写 .gate-result.json（不是根目录）"，但实现直接删除了写入。设计与实现已背离。

---

### A2: 脚本→文档对齐

**A2.1 陈旧注释** — MISALIGNED（次要）

- 脚本（pre-commit-gate.sh:5）：`# Phase 1: P1.1 跑 gate 写 .gate-result.json` —— 但脚本已不写该文件。
- 脚本（pre-commit-gate.sh:27-30）：仍 source gate-result.sh 并 `type write_gate_result` 校验加载，但函数从未被调用 → load-check 沦为摆设。
- 结论：**MISALIGNED**（次要）。建议同步注释，或恢复调用。

**A2.2 死代码** — MISALIGNED（次要）

- gate-result.sh:58-65 `has_staged_phase_change`、67-70 `has_staged_phase_output`：旧版 pre-commit-gate.sh 调用，重写后无人调用（全仓 grep 确认仅定义处）。
- 设计文档（设计文档:102-106）"改动 3：has_staged_phase_output 适配多任务，改为返回文件列表"——实现未遵循设计，而是内联了 git diff 逻辑并抛弃这两个函数。
- 结论：**MISALIGNED**（次要）。建议删除死函数，或在 gate-result.sh 注明"保留供未来/外部调用"。

---

### A3: 一致性连锁 + 反向传播

**A3a 一致性连锁（已知衍生改动）**

- dispatch-protocol.md:624-641「Pre-commit 检查全景」表格：**未更新**。表格仍按单任务描述，未加"多任务扫描"说明，未加 phase-产出 WARNING 行。state-machine.md:223 已加说明，但 dispatch-protocol.md 这张对等表没同步 → **MISALIGNED**。建议在表后补一行或在表注加多任务说明。
- gate-result.sh：见 A2.2，未清理死代码 → MISALIGNED（次要）。

**A3b 反向传播（应被影响但 diff 未列出的文件）**

| 应被影响文件 | 理由 | 是否影响到了 |
|---|---|---|
| agate/scripts/ci-gate-backstop.py | 消费 `.gate-result.json`，hook 不再写 → 降级 | ❌ 未同步 |
| agate/dispatch-protocol.md（pre-commit 表） | 与 state-machine.md:223 对等表，应同步多任务/WARNING | ❌ 未同步 |
| agate/orchestrator-template.md:72-83 | "9 项检查"描述；多任务行为未提 | ⚠️ 次要（"9 项"仍准，可不改） |
| CHANGELOG.md | 需标 `.gate-result.json` 不再写 / CI backstop 降级 | ❌ 未标（见 A5） |
| agate/scripts/gate-result.sh | write_gate_result/has_staged_* 死代码清理 | ❌ 未清理 |

结论：**MISALIGNED**。至少 dispatch-protocol.md 表格 + ci-gate-backstop.py 消费方 + CHANGELOG 必须同步。

---

### A4: 测试覆盖

**A4.1 向后兼容 + 新场景** — 基本达标

- IT.1-IT.5（根 .state.yaml，向后兼容）全过 ✓
- IT.6-IT.10（多任务 + WARNING + 裁剪跳阶 + 向后兼容）全过 ✓
- 全量 bats：190 用例，仅 CON.9 失败。已验证 CON.9 在 clean HEAD（git stash）同样失败 → 预存回归（md5 去重已实现，使"期望 WARN 缺 md5 关键词"的断言落空），**非本次引入**。

**A4.2 覆盖缺口** — NEEDS_HUMAN_REVIEW

1. **IT.8 / IT.9 未断言"无 WARNING"**：设计文档:133-134 明确 IT.8/IT.9 期望"不拦截不 WARNING / 无 WARNING"，但测试只 `[ "$status" -eq 0 ]`，未验证 stderr 不含 WARNING。一旦 2f/第 3 段误报，测试抓不到。建议补 `[[ "$output" != *"WARNING"* ]]`。
2. **无 `.gate-result.json` 回归测试**：A1.3 的回归没有任何测试守护。建议补一个用例断言 hook 运行后 `.gate-result.json` 存在（或显式断言不再存在，取决于修复方向）。
3. **测试文件头注释陈旧**：pre-commit-hook.bats:2-3 `# 5 用例覆盖` / `# 实际 5 行`，实际已 10 用例。建议更新。

结论：**NEEDS_HUMAN_REVIEW**。核心场景覆盖到位，但"无 WARNING"断言缺失 + `.gate-result.json` 无守护，建议补齐后再 commit。

---

### A5: 下游影响 + 文档传播

**A5.1 CHANGELOG** — 部分达标

- CHANGELOG.md:14 已标注：`pre-commit-gate.sh 多任务适配 ... 新增 phase-产出一致性 WARNING` ✓
- **未标注**：`write_gate_result` 调用被删除 → `.gate-result.json` 不再生成 → CI backstop（P1.3）降级。这是**破坏性变更**，依赖 `.gate-result.json` 的项目/工具会受影响。必须补 CHANGELOG。

**A5.2 下游影响**

- 多任务项目（如 PeekView）：原本 hook 完全静默放行（bug），现在能正常工作 → **正面影响**。
- 单任务项目：hook 原本写 `.gate-result.json` 供 CI 对照，现在不写 → CI backstop 对 `--no-verify` 绕过的检测能力下降（gate 失败仍能抓，gate 通过时无法区分是否绕过）→ **负面影响/破坏性**。
- ci-gate-backstop.py 本身对多任务本就 SKIP（它读根 `.state.yaml`，多任务无此文件 → L32-34 SKIP）→ 多任务侧 CI backstop 本就未覆盖，本次不恶化；但单任务侧恶化。

结论：**MISALIGNED**。CHANGELOG 漏标破坏性变更，下游单任务项目的 CI backstop 降级未披露。

---

### A6: 锚点表覆盖

- CHECK 9 锚点（check-protocol-consistency.py:522-526）：`pre-commit-gate.sh` 锚点 keywords=`["PROD_TOUCHED"]`。脚本 pre-commit-gate.sh:34 仍含 `\[PROD_TOUCHED\]` → 锚点命中 ✓。consistency 检查 CHECK 9 PASS ✓。
- 新增规则 phase-产出 WARNING（state-machine.md:223 声明）未加入锚点表。锚点是结构兜底，非强制；但按 A6 精神可加一条（如 keywords=`["WARNING", "phase"]` 指向 pre-commit-gate.sh）。属**可选增强**。
- 结论：**ALIGNED**。现有锚点不破；新规则锚点可选补。

---

## 特别关注项复核

**向后兼容（单任务根 .state.yaml）**：IT.10 + IT.1-IT.5 验证通过。脚本 81-85 行对根 .state.yaml 反推 `TASK_DIR=$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID`，逻辑正确。✓

**误拦场景**：
- 2f 用 `^${TASK_REL}/P[0-8]-.*\.md$` 限定同任务目录，不跨任务误报 ✓
- PAUSED/READY/DONE 在 2g 段 `continue` 跳过 gate，但仍先做了 2f WARNING——PAUSED 状态下若暂存了 P{n} 产出会误 WARN。属可接受噪音（设计已声明 WARNING 容忍噪音）。
- 裁剪跳阶（IT.9 P2→P5 + P5 产出）：out_phase=P5=PHASE → 不 WARN ✓

**WARNING 触发场景**：
- 情况 B（P4 产出+phase=P3）：IT.7 验证触发 WARNING + exit 0 ✓
- 情况 C（P4 产出+phase=P5）：逻辑等价 B，会触发 ✓（无独立测试，但同代码路径）
- 情况 D（无产出）：2f STAGED_OUTPUTS 空 + 第 3 段无 P 文件 → 不检查 ✓

**安全性（phase-产出检查漏洞）**：
- 第 3 段（174 行）读**工作树** `.state.yaml`（非暂存版）。若 agent 已在工作树改 phase=P4 但只暂存了 P4 产出（未暂存 .state.yaml），则读到 P4 → 不 WARN。这是 best-effort，符合设计"WARNING 不拦截"定位，非安全漏洞。
- phase-产出检查不拦截 → 不影响 gate 决策，无绕过 gate 的路径。gate 仍在 .state.yaml 暂存变更时强制跑。✓

---

## 闭环建议

| 项 | 结论 | 主 Agent 动作 |
|---|---|---|
| A1.3 `.gate-result.json` 回归 | MISALIGNED | **必须修复**：恢复 `write_gate_result` 调用（推荐），或显式退役该机制并同步 ci-gate-backstop.py + 3 处文档 + CHANGELOG |
| A2 注释/死代码 | MISALIGNED（次要） | 同步注释 line 5；清理或保留 has_staged_* 并注明 |
| A3 dispatch-protocol.md 表格 | MISALIGNED | 补多任务扫描/WARNING 说明 |
| A4 "无 WARNING"断言 | NEEDS_HUMAN_REVIEW | 补 IT.8/IT.9 的 `!= *WARNING*` 断言；补 `.gate-result.json` 守护测试；更新文件头注释 |
| A5 CHANGELOG 破坏性变更 | MISALIGNED | 补 `.gate-result.json` 不再写 / CI backstop 降级条目 |
| A6 锚点 | ALIGNED | 可选：为新 WARNING 规则加 CHECK 9 锚点 |

**修复优先级**：A1.3（阻断性）> A5 CHANGELOG > A3 dispatch-protocol.md 表格 > A4 断言补强 > A2 注释/死代码 > A6 锚点（可选）。

修完 A1.3 + A5 + A3 + A4 后建议重审，确认 `.gate-result.json` 链路（hook 写入 ↔ ci-gate-backstop.py 对照 ↔ 文档声明）三方一致再 commit。
