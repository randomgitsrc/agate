# T091 摩擦点 A+B 修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 T091 复盘发现的两处 agate 协议摩擦点：A（phase-commit 语义未澄清导致 P5→P6 边界误伤 fail-list.txt）、B（subagent 外部中断无恢复清单）。

**Architecture:** 纯文档改动，无脚本逻辑变更。A 修 `git-integration.md` 规则 2（通用 phase 语义）+ P5 phase card（边界特例提醒）；B 在 `dispatch-protocol.md` 补"外部中断恢复"一节。C（并行环境隔离）记入 roadmap，本次不做。

**Tech Stack:** Markdown + bats（验证现有测试不破）。

**来源：** T091 复盘（peeklink tbtv6l）+ 已核实 v0.40.0 现状：
- 摩擦点 2（DESIGN_GAP 双零巧合）已由 v0.40.0 结构化解决，无需动作
- 摩擦点 1（P5→P6 fail-list.txt 误伤）根因 = phase-commit 语义未澄清 + P5 card 教了"先推 phase 再 commit"
- 摩擦点 3（subagent 中断恢复）部分存在（有"返回校验"和"失败≠降级"，无"外部中断恢复清单"）

---

## File Structure

- **Modify** `agate/git-integration.md` — A：规则 2 补 phase-commit 语义澄清
- **Modify** `agate/phase-cards/P5-verification.md` — A：P5→P6 边界特例提醒
- **Modify** `agate/dispatch-protocol.md` — B：subagent 外部中断恢复一节
- **Modify** `docs/hardening-roadmap.md` — C：并行环境隔离规范记入 roadmap
- **Modify** `README.md`, `CHANGELOG.md` — v0.40.1 bump

---

### Task 1: A — git-integration.md 规则 2 补 phase-commit 语义澄清

**Files:**
- Modify: `agate/git-integration.md:27-42`

**背景**：规则 2 说"产出和 .state.yaml phase 更新在同一个 commit 里"，但**没说清 phase 字段 = "本 commit 提交的产出阶段"**。P5 phase card 的"更新 phase=P5→P6 再 commit"指令让 orchestrator 用"提前写下一阶段"惯例，导致 P5 的 fail-list.txt（P5 合法产出）在 phase=P6 的 commit 里被 P6 硬拦截误伤（`pre-commit-gate.sh:299` 白名单只认 `P[n]-evidence/` 和 `evidences/`）。

- [ ] **Step 1: 规则 2 补 phase 语义澄清**

在 `agate/git-integration.md` 规则 2 的"产出和 .state.yaml phase 更新在同一个 commit 里"之后，追加：

```markdown
**phase 字段语义（消除"提前写"歧义）**：`.state.yaml` 的 `phase` 字段 = **本 commit 提交的产出阶段**，不是"当前进展到哪"。commit 时 phase 写该阶段（如提交 P5 产出 → phase=P5），**不得提前写下一阶段**。否则 P5 的合法产出（如 `P5-test-results/fail-list.txt`）会在 phase=P6 的 commit 里被 P6 的 self-authored gate 硬拦截（P6 拦截"非证据文件"以防验收阶段改代码）。

**特例**：唯一例外是**同一 commit 里同时提交上一阶段产出 + 下一阶段已就绪的产出**（如 P1 产出 + P2 产出都完成时一次 commit，phase 写 P2）——此时 phase 反映"commit 里最晚的产出阶段"，且必须所有产出都过了各自 gate。**该特例不适用于 P5→P6 边界**（P6 self-authored gate 硬拦截非证据文件，P5 产出必须留在 phase=P5 的 commit）。
```

- [ ] **Step 2: 验证**

```bash
python3 agate/scripts/check-protocol-consistency.py
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```
预期：0 ERROR；全绿（纯文档改动，无行为变化）。

- [ ] **Step 3: Commit**

```bash
git add agate/git-integration.md
git commit -m "docs: git-integration 规则2 澄清 phase 字段=本 commit 产出阶段 (v0.40.1)

T091 摩擦点1 根因：phase 语义未澄清，P5 card 教'先推 phase 再 commit'，
导致 P5 的 fail-list.txt 在 phase=P6 提交时被 P6 硬拦截误伤。
补 phase=本 commit 产出阶段语义 + 唯一特例（同 commit 多阶段产出）。

self-gate-review: agate/git-integration.md"
```

---

### Task 2: A — P5 phase card 补边界特例提醒

**Files:**
- Modify: `agate/phase-cards/P5-verification.md:4-6`

**背景**：P5 card 开头 L4-6 是"更新 .state.yaml phase=P5 → P6 → git add → git commit"——这直接教了"先推 phase 再 commit"，是摩擦点 1 的操作源头。

- [ ] **Step 1: 修正 P5 card 的推进指令顺序**

把 P5 card 开头"如果是首次进入本阶段"的操作（实际位于 `agate/phase-cards/P5-verification.md:13-15`）：

```
4. 更新 .state.yaml phase=P5 → P6
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
6. git commit -m "wf({Txxx}-P5): {摘要}"
```

改为：

```
4. git add docs/tasks/{Txxx}/（含 .state.yaml + P5 产出，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P5，不要提前写 P6——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P5): {摘要}"（phase=P5，P5 产出含 P5-test-results/fail-list.txt）
6. P5 commit 完成后进入 P6：**phase 推进 P6 随 P6 产出 commit 一起**（P6-acceptance.md + P6-evidence/ 就绪后），不是单独 phase commit
   ⚠️ P5→P6 是唯一硬拦边界：P6 的 self-authored gate 拦截"非证据文件"，
      P5 的 .txt/.json 等合法产出必须在 phase=P5 的 commit 里提交，不能带进 phase=P6
   ⚠️ 不要"先 commit 产出再单独 commit 改 phase"（state-machine.md:431 明确禁止）——
      phase 与产出同 commit，P6 产出就绪时 phase 一并写 P6
```

> 关键：P5 的产出（P5-test-results/、fail-list.txt、pre-task-baseline.md）在 phase=P5 提交；phase 推进 P6 与 P6 产出（P6-acceptance.md、P6-evidence/）同 commit。

- [ ] **Step 2: 验证**

```bash
python3 agate/scripts/check-protocol-consistency.py
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```
预期：0 ERROR；全绿。

- [ ] **Step 3: Commit**

```bash
git add agate/phase-cards/P5-verification.md
git commit -m "docs: P5 card 修正推进指令，phase=P5 提交产出，P6 推进随 P6 产出同 commit (v0.40.1)

T091 摩擦点1 操作源头：P5 card 教'先推 phase=P6 再 commit'，导致
P5 合法产出（fail-list.txt）在 P6 硬拦边界被误伤。改为 phase=P5
提交产出，phase 推进 P6 随 P6 产出同 commit（不单独 phase commit，
state-machine.md:431）。P5→P6 唯一硬拦边界提醒。

self-gate-review: agate/phase-cards/P5-verification.md"
```

---

### Task 3: B — dispatch-protocol.md 补 subagent 外部中断恢复一节

**Files:**
- Modify: `agate/dispatch-protocol.md`（在"subagent 返回校验"节之后插入）

**背景**：现有 L44"subagent 返回校验"处理的是 subagent **正常返回后的校验**；L164"失败≠降级"处理的是"明确失败"。但**外部中断（API 额度/超时/崩溃）**是第三种场景——subagent 可能已落盘部分高质量产出就被打断，现有协议把它当"失败"重派，浪费已落盘内容。

- [ ] **Step 1: 在返回校验节后插入"外部中断恢复"节**

在 `agate/dispatch-protocol.md` 的 **`## 执行模式` 节之前**插入（注意：`subagent 返回校验` `##` 节实际延伸至 L138，含"Subagent 假完成校验/主 Agent 跑 gate/空返回恢复"三个子节——**不要**插在"任一校验失败 → 计入 retries[Pn]"之后，那会把它后面的子节全吞进新节。锚定到 `## 执行模式` 这一行之前）：

```markdown
## subagent 外部中断恢复（额度/超时/崩溃）

subagent 可能因**外部原因**（API 额度上限、平台超时、进程崩溃）中途终止——与"正常返回后校验失败"不同，此时 subagent 可能已落盘部分产出。**不能一律当作失败重派**，应先评估已落盘内容再决定复用/补做/重来。

```
subagent 收到 failed/中断信号后，主 Agent 按序检查：
  1. 检查 docs/tasks/{Txxx}/ 下已落盘产出（Edit 工具即时写入，不因中断丢失）
  2. 评估产出完整度：
     - 文件存在 + Header 完整 + 内容非空非半截 + 能过该阶段 gate → 直接复用
     - 文件存在但内容明显半截（写一半断）→ 补充少量工作后复用，不重派
     - 无产出或产出无实质内容 → 视为失败，计入 retries[Pn] 重派
  3. 复用已落盘内容时，仍须亲自跑 gate 验证（不能因"是上次中断的产出"就采信）
  4. 复用 vs 重派的边界：已落盘内容 ≥80% 完整 → 补充复用；<80% → 重派
  5. 中断不计入 retries[Pn] 的"subagent 失败"语义（那是 subagent 做不好的惩罚）；
     但若中断 2 次以上且均无实质产出，按环境/平台问题记录，不盲目重试
```

> 与"返回校验"的关系：返回校验针对 subagent **正常返回**（含其 step 4 "半截内容 → 视为失败，重试"）；本节针对**外部中断**（额度/超时/崩溃，subagent 无法正常返回）。**本节优先于返回校验 step 4**——外部中断且已落盘内容 ≥80% 完整时，补充复用而非重试；若中断前已正常返回则仍走返回校验。两者都要求主 Agent 亲自跑 gate 验证，不采信 subagent 自述。
```

- [ ] **Step 2: 验证**

```bash
python3 agate/scripts/check-protocol-consistency.py
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```
预期：0 ERROR；全绿。

- [ ] **Step 3: Commit**

```bash
git add agate/dispatch-protocol.md
git commit -m "docs: dispatch-protocol 补 subagent 外部中断恢复清单 (v0.40.1)

T091 摩擦点3：外部中断（额度/超时/崩溃）时 subagent 可能已落盘部分
产出，现有协议一律按失败重派浪费。补恢复清单：先查落盘完整度，
≥80% 补充复用 / <80% 重派，复用仍须亲自跑 gate。

self-gate-review: agate/dispatch-protocol.md"
```

---

### Task 4: C — 并行环境隔离规范记入 roadmap

**Files:**
- Modify: `docs/hardening-roadmap.md`

**背景**：C 扩大为"任意环节并行执行机制"。协议已有"按包拆分并行"（dispatch-protocol.md L623-626）和"专家组并行评审"（P2 card），但**缺并行时的环境隔离规范**（并行 subagent 各自启动 debug server 会端口冲突）。

- [ ] **Step 1: roadmap 加 C 条目**

在 `docs/hardening-roadmap.md` 的"v0.23.0+ — 设计讨论（P4，按需启动）"表后追加：

```markdown
### v0.40.0+ — 并行执行环境隔离（P4，按需启动）

| ID | 内容 | 依赖 |
|----|------|------|
| P2.66 | 并行执行环境隔离规范：多 subagent 并行时 debug server 生命周期归属（共享 or 端口分配）、`debug_env`/`isolation_check` 字段落地语义。协议已有"按包拆分并行"（dispatch-protocol.md L623）和"专家组并行评审"（P2 card），缺的是并行时的环境隔离规范。来源 T091 摩擦点4 + C 讨论扩大。 | 独立设计讨论 |
```

- [ ] **Step 2: 验证 + Commit**

```bash
python3 agate/scripts/check-protocol-consistency.py   # 0 ERROR
git add docs/hardening-roadmap.md
git commit -m "docs: roadmap 记入并行执行环境隔离规范 (v0.40.1)

T091 摩擦点4 扩大：任意环节并行的环境隔离规范。协议已有按包拆分并行
+ 专家组并行评审，缺并行时 debug server 生命周期归属规范。roadmap P4 项。

self-gate-review: docs/hardening-roadmap.md"
```

---

### Task 5: 版本 bump v0.40.1 + 收尾验证

**Files:**
- Modify: `README.md`, `CHANGELOG.md`

- [ ] **Step 1: 全量验证**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
shellcheck -S warning agate/scripts/*.sh
python3 agate/scripts/check-protocol-consistency.py
bash agate/tests/scripts/count-tests.sh
```
预期：全绿 / clean / 0 ERROR / 用例数不漂移。

- [ ] **Step 2: 版本 bump**

README badge `v0.40.0` → `v0.40.1`。CHANGELOG 加 `[v0.40.1]`（A：phase-commit 语义澄清 / B：中断恢复清单 / C：roadmap 记录）。非 BREAKING。

- [ ] **Step 3: Commit + tag + PR**

```bash
git add README.md CHANGELOG.md
git commit -m "chore: v0.40.1

T091 摩擦点 A/B 修复 + C roadmap 记录。非 BREAKING。"
git tag v0.40.1 && git push origin v0.40.1
```
**release PR 必须普通 merge（--no-ff）**（AGENTS.md 规则）。

---

## Self-Review

**1. Spec coverage（A+B+C 全覆盖）：**
- A（phase-commit 语义澄清）→ Task 1（git-integration 通用层）+ Task 2（P5 card 边界特例）
- B（subagent 中断恢复）→ Task 3
- C（并行环境隔离 roadmap）→ Task 4
- 版本 → Task 5

**2. Placeholder scan：** 无 TBD；每步含完整文本/代码。

**3. Type consistency：** phase 语义在 git-integration（Task 1）与 P5 card（Task 2）一致（"phase = 本 commit 的产出阶段"）；中断恢复判断标准在 dispatch-protocol（Task 3）自洽（≥80% 复用）。

**已识别风险：**
- **Task 2 是行为变更（评审确认方向正确）**：P5 card 从"先推 phase 再 commit"改为"phase=P5 提交产出，phase 推进随 P6 产出同 commit"。实测 T001 历史：P5 证据 commit phase=P5（`1483f36`）、P6 产出 commit phase=P6（`8c38c2f`），plan 的改动与真实实践一致。评审确认 CHECK 9 无锚点指向 P5 card，无失配风险。
- **P6 card 的同类推进指令（L15"phase=P6→P7"）语义仍不一致**：P6 card 说推进 P7 时提交 P6 产出（phase 提前写 P7）。P7 gate 宽松不拦，但语义上与 plan 的新规则冲突。**建议实现时同步修正 P6 card**（或明确本 plan 只修 P5→P6 边界，P6→P7 留待后续统一）。—— 已加为实现时的注意事项。
- **B 的"≥80% 完整"是主观判断**：已在文本里写明是边界引导（不是精确测量），符合 agate"自声明 nudge"风格。

**评审记录（独立评审 2 轮）：**
- 第 1 轮（NO-GO → 修复）：✗ Task 2 Step 6"单独 phase commit"被 gate 拦（check-gate.sh:290-299）+ 违反 state-machine.md:431 → 改为"phase 推进随 P6 产出同 commit"；✗ Task 4 P2.63 ID 冲突 → 改 P2.66；✗ Task 3 与返回校验 step 4 矛盾 → 加 supersede 注
- 第 2 轮（GO + 3 文本修正）：✓ 三处修复验证正确；✗ N1 commit message 残留矛盾 → 改；✗ N2 插入锚点歧义 → 锚定 `## 执行模式` 前；✗ N3 Task 1 特例未排除 P5→P6 → 补一句