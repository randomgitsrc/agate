---
task_id: agate-audit-fixes-review
agent: main
date: 2026-07-01
status: 评审完成
评审对象: docs/plans/agate-audit-fixes-2026-07-01.md
来源: docs/reviews/agate-full-audit-2026-07-01.md + agate-full-audit-part2-2026-07-01.md
---

# 审计修复实施计划评审

## 评审方法

逐条对照计划的设计决策、代码片段、测试方案与原始审查报告，并结合以下源文件验证：

- `agate/scripts/check-state-transition.sh`（A/B 组修改对象）
- `agate/scripts/check-pruning.sh`（C 组修改对象）
- `agate/scripts/check-gate.sh`（C/D 组修改对象）
- `agate/scripts/check-retrospective.sh`（A 组修改对象）
- `agate/scripts/pre-commit-gate.sh`（F 组 #18）
- `agate/state-machine.md`（裁剪条件表 L163-171、MAX_RETRY 表 L428-437、回退跳变 L407-411）
- `agate/dispatch-protocol.md`（门槛表 L574-583、pre-commit 表 L598-608）
- `agate/WORKFLOW.md`（风险矩阵 L161-169、阶段总览 L190-201）
- `agate/assets/templates/task-files.md`（P1/P2 模板）
- `agate/assets/execution-roles/architect.md`（多方案 nudge 说明 L24）
- `agate/scripts/check-protocol-consistency.py`（CHECK 9 锚点表 L486-561）
- `agate/scripts/gate-result.sh`（.gate-history.jsonl 追加逻辑）
- 全部 bats 测试文件 + helpers
- O1 修复历史（`docs/archived/reviews/review-20260630-1551.md`、`docs/archived/plans/hardening-phase1-2a-2026-06-30.md`）
- 实跑 `python3 agate/scripts/check-protocol-consistency.py`（当前 0 ERROR / 5 WARNING）

---

## A. MAX_RETRY 相关（3 项）

### A.1 设计决策：修脚本对齐文档（按阶段差异化）

**PASS** — 方向正确。

文档（state-machine.md:428-437）明确按阶段独立：P1=3,P2=3,P3=2,P4=3,P5=2,P6=2,P7=2,P8=2。脚本硬编码 `MAX_RETRY=3` 对 P3/P5/P6/P7/P8 放宽了 1 轮，违反"少轮次"设计意图。修脚本是对的。

### A.2 可落地性：`get_max_retry "$new_phase"` 用法错误

**ISSUE（严重）** — 核心设计缺陷，会导致误拦。

**问题**：`get_max_retry` 函数本身语法正确，但调用方式 `MAX_RETRY=$(get_max_retry "$new_phase")` 是错的。`.state.yaml` 的 `retries` 是按阶段存储的 dict（state-machine.md:454-461），可以同时包含多个阶段的记录：

```yaml
retries:
  P2:                    # P2 的 MAX=3
    - attempt: 1
    - attempt: 2         # 2 < 3，未超限
  P3:                    # P3 的 MAX=2
    - attempt: 1
```

Python 检查逻辑（L80-82）遍历 retries dict 的**所有**阶段，统一用 `max_retry` 比较。如果用 `new_phase`（假设=P3，MAX=2）作为阈值，会检查 `P2 的 2 次 >= 2` → 误判 P2 超限 → exit 1 拦截合法转移。

**正确做法**：按 dict 的 key（即 retries 记录的那个阶段）查 MAX_RETRY，不是按 `new_phase`。需要在 Python 循环内逐阶段查阈值：

```python
MAX_MAP = os.environ.get("MAX_RETRY_MAP", "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2")
max_map = dict(p.split(":") for p in MAX_MAP.split(","))
for phase, attempts in retries.items():
    phase_max = int(max_map.get(phase, 3))
    if isinstance(attempts, list) and len(attempts) >= phase_max:
        print(f'{phase}={len(attempts)}')
        break
```

或直接在 Python 内实现 `get_max_retry` 映射，避免 shell/Python 来回传参。

**修复建议**：改用 per-phase 查找。check-retrospective.sh 同理（L23 的 `>= 3` 也要按阶段查）。

### A.3 测试覆盖：缺少多阶段 retries 场景

**ISSUE** — 现有测试计划不够。

计划测试"P3 retries=2 → 拦截"和"P5 retries=2 → 提醒"只覆盖了单阶段 retries 的场景。必须补充：

- **多阶段 retries + 不同阈值**：new_phase=P3，retries={P2:[2 条], P3:[1 条]}。P2 的 MAX=3，2<3 不超限；P3 的 MAX=2，1<2 不超限 → 应 exit 0。**这是计划的 buggy 实现会误拦的场景（用 P3 的 MAX=2 查 P2 的 2 次）**。
- P1 retries=2 + new_phase=P2（P1 MAX=3，2<3 不超限）→ exit 0。

### A.4 一致性检查影响

**NOTE** — CHECK 9 锚点（L513-516）要求 `check-state-transition.sh` 含关键词 `MAX_RETRY`。计划的 `get_max_retry` 函数名是小写，shell 变量 `MAX_RETRY` 如果保留则满足。但如果按上述正确改法（映射传入 Python），shell 层可能不再有 `MAX_RETRY` 变量——需在注释或变量名中保留该字符串，否则 CHECK 9 会从 PASS 变 WARNING。

---

## B. 回退跳变相关（3 项）

### B.1 #2 恢复 exit 1：决策正确，但推理不完整

**PASS（附推理修正）**

**决策正确**：恢复 exit 1 强制 PAUSED 是对的。T019 教训正是"跨阶段回退未 PAUSED"。实测验证：协议规定每次状态转移单独 commit，所以 old_phase 从 HEAD 读取。如果用户走了 P5→PAUSED→P3（PAUSED 单独 commit），HEAD 的 phase=PAUSED → L51-53 早退 exit 0，不会误拦。exit 1 只在"P5 直接改 P3（无 PAUSED commit）"时触发——这本身就是流程违规。

**但推理需修正**：计划说"降级理由不成立——回退跳变检测不需要 .gate-history.jsonl"。这个论断不完整。查阅 O1 修复历史（`docs/archived/reviews/review-20260630-1551.md` L86-98）：

- O1 原始问题：旧检查依赖 commit message 判断是否经过 PAUSED → 违反"不依赖 commit message"原则
- 降级原因：`.gate-history.jsonl` 尚未实现，无法可靠验证 PAUSED 是否发生过 → 降级 WARNING
- 长期计划：查 `.gate-history.jsonl` 的 PAUSED 记录做精确判断

`.gate-history.jsonl` 确实与回退检测有关——原计划用它验证"PAUSED 是否在中间发生过"。但当前 `.state.yaml` 的 HEAD/staged diff 机制（old_phase 来自 HEAD commit）已经隐式验证了 PAUSED（如果 PAUSED 被 commit 过，HEAD 就是 PAUSED → 早退）。所以 `.gate-history.jsonl` 的精确验证不是必需的。

**正确表述**：".gate-history.jsonl 的 PAUSED 验证功能已被 HEAD/staged diff 机制隐式覆盖（PAUSED 单独 commit 时 HEAD=PAUSED → 早退 exit 0）。简单 diff 检查足以强制 PAUSED 检查点，不需要等待 .gate-history.jsonl 的精确验证。"

### B.2 #11 改为双向检查：会破坏合法裁剪流程

**REJECT** — 前向检查会导致误拦合法裁剪转移。

**问题**：裁剪场景下，P3/P4 被裁剪后，主 Agent 直接将 phase 从 P2 改为 P5（state-machine.md:160-161："跳过时直接转移到裁剪声明中的下一个阶段"）。diff = |5-2| = 3，双向检查会 exit 1 拦截。

`check-state-transition.sh` 只读 `.state.yaml`，**不读 P1-requirements.md 的 phases 声明**，无法区分"合法裁剪前向跳"和"非法跳过阶段"。计划说"阶段产出文件检查能兜底"——但那是 P5 gate 的事后检查，不是状态转移检查的职责，且会让用户在状态转移层被挡、不知道为什么。

**文档措辞分析**：state-machine.md:407 标题是"回退跳变检测"，T019 教训例子是 P5→P2（回退），但 L408 用了绝对值 `|next - current|`。审计也标为 NEEDS_HUMAN_REVIEW（"文档自身措辞有歧义"）。绝对值更像表述不严谨，而非有意要求双向。

**建议**：
1. 脚本保持**只查回退方向**（old > new），不改双向
2. 文档 L408 改为 `若 current_phase_num - next_phase_num >= 2`（明确回退方向），消除歧义
3. 如果确实要查前向跳，必须先让 check-state-transition.sh 读 P1 phases 声明做白名单——这是较大改动，不宜混入本次修复

### B.3 代码：`abs_diff=${diff#-}` 正确，但缺少 old_num 守卫

**ISSUE** — 计划代码片段省略了关键守卫。

`abs_diff=${diff#-}` 取绝对值语法正确 ✓。

但当前代码（L61）有守卫 `if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]`，计划的代码片段没有包含它。没有这个守卫：

- `PAUSED→P3`（从暂停恢复）：`phase_num("PAUSED")` = 0（无数字），`old_num=0`，`diff=0-3=-3`，`abs_diff=3` → **误拦恢复操作**
- `P0→P3`：虽然 P1 不可裁剪所以 P0→P3 不合法，但 PAUSED→Pn 是完全合法的恢复流程

**修复建议**：保留守卫。如果改回只查回退方向（B.2 建议），守卫仍然必要。

### B.4 测试覆盖：缺少 PAUSED 恢复场景

**ISSUE**

计划测试了 P6→P1、P2→P5、P5→P4，但缺少：

- **PAUSED→P3（恢复）→ 应 exit 0**：验证 old_num=0 守卫不被移除。如果按 B.2 改为只查回退，这个场景天然放行，但仍需测试覆盖。
- 如果保留双向检查：**裁剪场景 P2→P5（P3/P4 已声明裁剪）→ 应 exit 0**——但这需要测试构造 P1 phases 声明，而脚本不读 P1，所以这个测试会暴露 B.2 的问题（测试会红）。

---

## C. 裁剪条件偏差（4 项）

### C.1 #5 P3 裁剪：改文档对齐脚本

**PASS** — 有测试背书。

现有测试 `check-pruning.bats` P2.5b（L96-103）注释明确写"medium 风险 + P3 裁剪是允许的"，只因缺"跳过风险"才 exit 1。脚本行为（允许 medium）已被测试固化，是文档措辞滞后。

state-machine.md:165 改为"high 风险不可裁"正确。WORKFLOW.md 风险矩阵（L165-169）只有"低风险/高风险"两列无 medium 列，不构成"medium 不可裁"的反证。

### C.2 #7 裁剪理由加 P6

**PASS** — 逻辑正确。

当前条件（check-pruning.sh:104）`! P2 || ! P3 || ! P7 || ! P8` 漏了 P6。追加 `|| ! echo "$PHASES_DECLARED" | grep -qw 'P6'` 正确。P6 裁剪（no_behavior_change: true）也应写"跳过风险"评估。

### C.3 #8 P8 理由检查：字段名未建立

**ISSUE** — 引入了未在文档/模板中定义的字段名。

计划用 `internal_only_reason:` 作为理由字段名，但：

- `state-machine.md:168` 只写"需声明 internal_only: true + 理由"，未指定字段名
- `assets/templates/task-files.md` 的 P1 模板（L142-148）根本没有 `internal_only` 字段（连 `internal_only:` 都没列）
- 全仓库 grep `internal_only_reason` 零匹配

if/elif 逻辑结构正确 ✓。但必须补：

1. state-machine.md:168 明确字段名：`internal_only: true + internal_only_reason: <理由>`
2. task-files.md P1 模板的裁剪说明区补 `internal_only:` 和 `internal_only_reason:` 示例
3. 回归测试 `v060-p8-internal-only.bats` R4.2 需更新（当前只加 `internal_only: true`，改后还需加 `internal_only_reason:` 才能通过）

### C.4 #10 P2 候选方案 form check

**PASS** — 与 nudge 设计一致，非"假锚点"。

计划担忧"重蹈假锚点覆辙"，但审查 `architect.md:24` 明确写：

> "多方案是 nudge——稻草人方案能形式满足（架构师在隔离上下文里写'真方案 + 明显更差的陪衬'+ 选真方案），plan-eng-review 只能查'是否探索了 + 理由自洽'不能查'是否选最优'。价值是'强制 architect 走一遍还有别的做法吗的思考'"

所以 form check 是**有意的 nudge**，与"跳过风险:" self-declaration 同一设计模式。当前 echo 消息声称检查"权衡 + 选择理由"但实际不查——这才是假锚点。加 grep 检查反而让消息变诚实。

**代码细节 ISSUE**：计划片段用 `$TASK_DIR/P2-design.md`，但当前代码已定义 `P2_FILE="$TASK_DIR/P2-design.md"`（L24）且有 `[ -f "$P2_FILE" ]` 守卫（L25）。新检查应复用 `$P2_FILE` 变量，放在 `CANDIDATE_COUNT >= 2` 通过后、`exit 2` 之前。

**测试缺口**：缺少 happy path（P2 有 ≥2 候选方案 + 含"权衡"→ exit 2 放行）。

---

## D. 门槛表对齐（4 项）

### D.1 #12 P1 门槛不实现

**PASS** — 决策合理。

P1 gate 设计为 exit 2（"BDD 编号格式不固定"），实现 grep 检查改动大且影响主 Agent 判断流程。标为已知局限合理。文档的 grep 命令仍列在门槛表里供主 Agent 手动执行。

### D.2 #13 P2 status:approved 检查：检查了错误的文件

**ISSUE（严重）** — 代码检查 P2-design.md，文档要求查 P2-review.md。

文档（dispatch-protocol.md:577）：`grep 'status: approved' P2-review.md` → 命中。

计划代码：
```bash
if ! grep -qE 'status:\s*approved' "$TASK_DIR/P2-design.md" 2>/dev/null; then
```

检查的是 `P2-design.md`——**错误文件**。status: approved 是 P2-review.md（评审结论）的字段，不是 P2-design.md（设计方案）的字段。应改为 `$TASK_DIR/P2-review.md`。

**另外遗漏**：文档门槛表还要求 `grep -cE '^(packages|domains|ui_affected|gate_commands):' P2-design.md → =4`（四字段计数）。审计指出脚本遗漏了这项，计划只补了 status:approved，没补四字段计数。应一并补上（或明确说明为什么不补）。

**测试缺口**：缺少 happy path（P2-review.md 有 status: approved → 放行）。

### D.3 #6 P4 路径偏离：改文档

**PASS** — 正确。

脚本查"暂存区有非 md/yaml 文件"（`git diff --cached`）比文档的"P4-implementation/ 下文件非空"更适合 pre-commit 场景。AGENTS.md 明确要求"所有 git diff 用 --cached"。改文档对齐脚本是对的。

### D.4 #16 P4 git log → --cached

**PASS** — 正确。

### D.5 测试覆盖

D 组只列了一个测试（P2 有候选方案但无 status:approved → 拦截）。需补充：

- P2-review.md 有 status: approved → 放行（happy path）
- 如果补了四字段计数：P2-design.md 缺一个字段 → 拦截

---

## E. 文档滞后（4 项）

### E.1 全部 PASS，附细节

| # | 决策 | 结论 | 备注 |
|---|------|------|------|
| #3 | md5 "hook 强制"→"建议" | PASS | md5 去重确实未实现。实跑 consistency 确认 CHECK 9 对 check-p6-evidence.sh 缺 'md5'/'去重' 关键词发 WARNING（不阻断）。改文档后 WARNING 仍在，可接受 |
| #4 | P3 UI "gate 不通过"→"主 Agent 确认" | PASS | P3 gate 确实不检查 UI 用例（转发 check-tdd-red.sh）|
| #9 | BDD "="→"≥" | PASS | 脚本用 ≥ 正确（允许 SCOPE+ 增补）。注意实际行号：dispatch-protocol.md:370 和 :581 用 "="，计划写的 ":575,363" 行号有偏差 |
| #14 | "三道"→"四道" | PASS | R1b vision YAML 审计已落地 |

### E.2 一致性检查影响

改 E 组文档后需实跑 `python3 agate/scripts/check-protocol-consistency.py` 确认无新 ERROR。特别是 #14 改"三道"→"四道"可能触发 CHECK 5（计数声明校验）如果别处也有计数引用。

---

## F. NEEDS_HUMAN_REVIEW（3 项）

### F.1 #17 FAIL 行证据：不修

**PASS** — 合理。FAIL 回 P4 重做，影响小；FAIL 证据格式不统一（错误堆栈 vs 文件引用），难以泛化检查。

### F.2 #18 pre-commit 顺序：改文档

**PASS** — 但需补 P1.2。

脚本执行顺序（pre-commit-gate.sh 实际）：P2.15 → P1.2 PROD_TOUCHED → P2.3-P2.5 → P1.1 → P2.1/P2.10 → P2.7-P2.9 → P2.11 → P2.12 → P1.6 → P1.7

文档表格（dispatch-protocol.md:598-608）顺序：P2.15 → P1.1 → P1.7 → P2.1/P2.10 → P2.3-P2.5 → P2.7-P2.9 → P2.11 → P2.12 → P1.6

差异：① 文档表格**完全没有 P1.2 PROD_TOUCHED 行**（审计 part2 也指出："dispatch-protocol.md:588-604 pre-commit 检查全景表未列 P1.2 PROD_TOUCHED 检测"）；② P2.3-P2.5 在 P1.1 之前；③ P1.7 在最后。

计划说"改文档表格对齐脚本"——正确，但必须**补 P1.2 行**，不能只调顺序。

### F.3 #19 check-changelog.sh exit 1：不修

**PASS** — 分层设计正确。check-changelog.sh exit 1（严格），pre-commit-gate.sh 用 `|| echo` 降级为警告（L106-107）。最终行为与文档"警告不拦截"一致。脚本独立调用时严格，hook 调用时降级——这是合理的分层。

---

## 遗漏检查

### 遗漏 1：P5 PROD_TOUCHED 可脚本化检查未处理

**ISSUE** — 审计 part2 标为 NEEDS_HUMAN_REVIEW，计划完全未提及。

dispatch-protocol.md:580 P5 门槛：`grep -rl '\[PROD_TOUCHED\]' {task}/` → 无命中。脚本（check-gate.sh:41-43）直接 exit 2，未执行此 grep。虽然 pre-commit-gate.sh:60 有全局 PROD_TOUCHED 检测（扫暂存 diff），但那只查暂存区内容，不查 task 目录已有文件。文档门槛表明确列了这个 grep，脚本应至少执行。

计划应在 F 组明确处理（哪怕决定"不修，因 pre-commit-gate.sh 已覆盖"），而不是完全遗漏。

### 遗漏 2：pre-commit-gate.sh P1.7 跳过逻辑不一致

**ISSUE** — 审计 part2 标为 NEEDS_HUMAN_REVIEW，计划未提及。

pre-commit-gate.sh：provenance（L81）、pruning（L90）、scope（L95）在 `GATE_EXIT != 1` 时才执行，但 P1.7 evidence（L111）无此条件——gate 失败时仍执行。审计指出"这是不一致的"。计划应在 F 组说明处理方式（即使决定"不修，多给诊断信息可接受"）。

### 遗漏 3：D 组 #13 四字段计数检查

**ISSUE** — 见 D.2。审计指出脚本遗漏 `grep -cE '^(packages|domains|ui_affected|gate_commands):' → =4`，计划只补了 status:approved。

### 遗漏 4：#8 模板未更新

**ISSUE** — 见 C.3。task-files.md P1 模板缺 internal_only 字段。

---

## 实施顺序

### 合并判断

| 合并组 | 脚本 | 判断 |
|--------|------|------|
| A+B | check-state-transition.sh | **正确** — A 改检查 2（L70-90），B 改检查 1（L58-68），两段独立无冲突 |
| C+D | check-gate.sh | **正确** — C#10 和 D#13 都在 P2 case 内追加检查，需注意放置顺序：count check → status:approved → form check → exit 2 |
| C | check-pruning.sh | 独立修改，无合并问题 |

### 隐藏依赖

1. **C#10 和 D#13 的放置顺序**：两个检查都在 `CANDIDATE_COUNT >= 2` 之后。建议先查 status:approved（D#13，更基础）再查 form check（C#10，nudge 性质）。功能上无依赖，但错误消息清晰度有影响。

2. **A 组改 MAX_RETRY 后影响 check-retrospective.sh**：计划已提到。但两个脚本独立调用 `get_max_retry` 逻辑——如果实现为共享函数，需放在公共 source 文件中；如果各自内联，需保持同步。当前协议无公共函数库，建议各自内联并在注释中标明"与 check-state-transition.sh 的 get_max_retry 保持同步"。

3. **B#11 如果改为只查回退（按本评审建议）**：则 B 组改动变小（只恢复 exit 1 + 保留守卫），与 A 组合并无风险。

4. **C#3 改 P8 理由检查后**：回归测试 `v060-p8-internal-only.bats` R4.2 会变红（只加 internal_only: true 不再加 reason）。必须在同一次修改中更新该测试。计划未提及此依赖。

---

## 汇总

### 结论：不可直接进入实施，需先修以下项

#### 必须修（会导致功能错误）

| 项 | 问题 | 修复 |
|----|------|------|
| A.2 | `get_max_retry "$new_phase"` 误拦多阶段 retries | 改为 per-phase 查找（dict key） |
| B.2 | 双向检查破坏合法裁剪转移（P2→P5） | 改为只查回退方向；文档 L408 去绝对值改回退方向 |
| B.3 | 代码缺 `old_num -gt 0` 守卫，PAUSED→Pn 恢复被误拦 | 保留守卫 |
| D.2 | status:approved 检查了 P2-design.md，应为 P2-review.md | 改文件路径 |
| C.3 | `internal_only_reason` 字段名未在文档/模板建立 | 更新 state-machine.md + task-files.md + 回归测试 |

#### 应该修（测试/覆盖不足）

| 项 | 问题 | 修复 |
|----|------|------|
| A.3 | 缺多阶段 retries 测试 | 补 new_phase=P3 + retries={P2:[2],P3:[1]} → exit 0 |
| B.4 | 缺 PAUSED→Pn 恢复测试 | 补 PAUSED→P3 → exit 0 |
| C.4 | 缺 form check happy path | 补 P2 有"权衡"→ exit 2 |
| D.5 | 缺 status:approved happy path | 补 P2-review.md 有 status:approved → 放行 |
| C.3 | 缺 P8 理由 happy path | 补 internal_only + reason → exit 0 |

#### 建议修（遗漏/完整性）

| 项 | 问题 | 修复 |
|----|------|------|
| 遗漏 1 | P5 PROD_TOUCHED 未处理 | 在 F 组明确处理决定 |
| 遗漏 2 | P1.7 跳过逻辑不一致未处理 | 在 F 组明确处理决定 |
| 遗漏 3 | D#13 四字段计数检查遗漏 | 补充或说明不补理由 |
| 遗漏 4 | task-files.md 模板缺 internal_only | 补模板 |
| F.2 | #18 补 P1.2 PROD_TOUCHED 到文档表格 | 不能只调顺序 |
| C.3 | 回归测试 v060-p8-internal-only.bats R4.2 会变红 | 同步更新 |

#### 可直接实施（无需修改）

- A.1 方向（修脚本对齐文档）✓
- B.1 #2 恢复 exit 1 ✓（推理按本评审修正后）
- C.1 #5 改文档 ✓
- C.2 #7 加 P6 ✓
- C.4 #10 form check ✓（代码细节按本评审修正后）
- D.1 #12 不实现 ✓
- D.3 #6 改文档 ✓
- D.4 #16 改文档 ✓
- E 组全部 ✓
- F.1 #17 不修 ✓
- F.3 #19 不修 ✓

### 建议实施流程

1. 先修本评审指出的 5 个"必须修"项，更新计划文档
2. 补全测试用例（5 个"应该修"）
3. 处理遗漏项（6 个"建议修"）
4. 按 A+B（check-state-transition.sh）→ C（check-pruning.sh）→ C+D（check-gate.sh）→ E+F（文档）顺序实施
5. 每步 TDD：先加失败测试 → 改脚本 → 测试绿
6. 最后跑全量 bats + consistency + shellcheck + self-gate
