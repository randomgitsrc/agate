---
type: plan
source: docs/reviews/agate-T025-cheatsheet-plan-review-2026-06-28.md
trace_id: agate-T025-gate-optimization-2026-06-28
created: 2026-06-28
status: 待执行
---

# 修复方案：T025 gate 判定效率优化（修订版）

> 来源：`docs/reviews/agate-T025-feedback-review-2026-06-28.md`（采纳 A 修正版）
> 前版：`docs/plans/agate-T025-cheatsheet-2026-06-28.md`（新增 gate-cheatsheet.md）
> 修订原因：专家评审发现 cheatsheet 引入四处重复、静态命令与动态 gate 规则冲突、绕过专用脚本导致判定降级
> 修订方向：不做新增文件，内联优化现有协议中 gate 命令的可执行性

---

## 前版问题回顾

| # | 问题 | 严重度 |
|---|------|--------|
| 1 | gate 命令四处重复（dispatch-protocol + state-machine 转移规则 + state-machine 步骤 5 + cheatsheet），一致性维护负担 | 高 |
| 2 | cheatsheet 静态一行命令 vs agate 动态 gate 规则（P5/P6 命令来自 P2 gate_commands），信息丢失 | 高 |
| 3 | P3 绕过 check-tdd-red.sh 直接跑 test runner，丢失"只允许 assertion failure"的判定逻辑 | 高 |
| 4 | "异常时必须读产出全文"的警告不可强制执行，Agent 会走捷径 | 中 |
| 5 | 主 Agent 步骤 0 已读 state-machine.md，步骤 5 的按阶段列举已是紧凑参考，cheatsheet 增量收益存疑 | 中 |

---

## 修订方案：内联优化 state-machine.md 步骤 5

**核心思路**：不新增文件，把 `state-machine.md` 单步函数步骤 5 的 gate 命令列举从自然语言改为可直接执行的 shell 命令。主 Agent 步骤 0 已读此文件，不需要额外导航。

### 动作 1：优化 state-machine.md 步骤 5 的 gate 命令格式

**文件**：`state-machine.md` L286-295

**当前格式**（自然语言描述）：
```
5. 主 Agent 亲自跑 gate 命令验证门槛（A1 原则：跑命令不信文件）：
   - P1: P1-requirements.md 有 BDD 条件 && 无未决 NEED_CONFIRM && 无 CAPABILITY_GAP
   - P2: P2-review.md status==approved && P2-design.md 含 packages/domains/ui_affected/gate_commands 四字段
   - P3: scripts/check-tdd-red.sh exit 0（UI 任务额外查 Playwright 用例存在）
   - P4: git log --oneline -1 确认 P4 commit
   - P5: pytest -q exit 0 && failed==0 && 无 [PROD_TOUCHED]（UI 任务额外实跑 Playwright/E2E）
         确认整个过程在 debug_env 中进行，无 [PROD_TOUCHED] 标记
   - P6: P1 每条 BDD 标记为 PASS 或 FAIL（二值）&& UI 条件 vision-analyst YAML summary.blocker_count==0 && 无未决 NEED_CONFIRM
   - P7: ! grep -qE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md
   - P8: 每个 package 的发布检查命令 exit 0
```

**改为**（shell 命令 + 通过条件，保留动态规则说明）：
```
5. 主 Agent 亲自跑 gate 命令验证门槛（A1 原则：跑命令不信文件）：
   - P1: grep -cE 'AC\d+.*Given.*When.*Then' {task}/P1-requirements.md → ≥1;
         grep -c NEED_CONFIRM {task}/P1-requirements.md → =0;
         grep -c CAPABILITY_GAP {task}/P1-requirements.md → =0
   - P2: grep 'status: approved' {task}/P2-review.md → 命中;
         grep -qE '^(packages|domains|ui_affected|gate_commands):' {task}/P2-design.md → 四字段均命中
   - P3: scripts/check-tdd-red.sh → exit 0;
         （UI 任务：ls {task}/P3-test-cases.md 内含 Playwright 用例描述）
   - P4: git log --oneline -1 → 含 "P4" 或 "wf(Txxx-P4)"
   - P5: 从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0;
         grep -rc PROD_TOUCHED {task}/ → =0;
         （UI 任务：从 gate_commands.P5 读取 E2E 命令执行 → exit 0）
   - P6: grep -cE '^\s*- (PASS|FAIL)' {task}/P6-acceptance.md → =P1 BDD 总数;
         grep -c 'FAIL' {task}/P6-acceptance.md → =0;
         grep -c NEED_CONFIRM {task}/P6-acceptance.md → =0;
         （UI 条件：vision-analyst YAML summary.blocker_count → =0）
   - P7: grep -cE '^\s*-?\s*\[BLOCKER\]' {task}/P7-consistency.md → =0;
         grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' {task}/P7-consistency.md → =0
   - P8: 从 P2-design.md gate_commands 逐包读取发布检查命令执行 → 全部 exit 0;
         git diff --stat → 含 version 文件变更;
         grep -q CHANGELOG {task}/P8-release.md → 命中
```

**关键设计决策**：

1. **不绕过 check-tdd-red.sh**：P3 仍用专用脚本，保留"只允许 assertion failure"的判定逻辑。脚本的裸 pytest bug 另行修复（见动作 2）
2. **P5/P6 命令从 P2 gate_commands 读取**：不硬编码 pytest，尊重 B7 规则（gate 命令由 P2 动态声明）
3. **P7 含 DEVIATION-CRITICAL**：与 T022 动作 4 一致
4. **P6 含 BDD count**：与 T022 动作 1 一致
5. **P8 含 bump 后重跑 P5**：与 T022 动作 2 一致（在 P8 命令中体现"从 gate_commands 逐包读取"）
6. **{task} 是路径占位符**：主 Agent 替换为 `docs/tasks/{Txxx}`，不硬编码

### 动作 2：修复 check-tdd-red.sh 的裸 pytest bug

**文件**：项目级 `scripts/check-tdd-red.sh`（非 agate 协议文件，是项目模板）

**问题**：T025 暴露脚本用裸 `pytest`，在 venv 项目中裸 pytest 不存在 → `|| true` 吞掉错误 → 假绿灯。

**改法**：在 `assets/templates/check-tdd-red.sh` 中，把 `pytest` 改为从 P0-brief.md 的 executor_env 读取 test runner 路径：

```bash
# 旧：RESULT=$(pytest -q 2>&1)
# 新：从 P0-brief 读取 test runner，回退到 pytest
TEST_RUNNER=$(grep -A5 'executor_env' docs/tasks/${TASK_ID}/P0-brief.md 2>/dev/null | grep 'test_runner' | head -1 | sed 's/.*: *//' || echo "pytest")
RESULT=$($TEST_RUNNER -q 2>&1)
```

**注意**：这是模板文件的修复，不是协议变更。已有项目需手动更新脚本。agate 的 `assets/templates/` 是参考模板，不自动覆盖项目文件。

### 动作 3：dispatch-protocol.md 门槛表同步 shell 命令格式

**文件**：`dispatch-protocol.md` L505-514「可判定门槛规范」表

**改法**：在"怎么判定"列中，把自然语言描述改为与 state-machine.md 步骤 5 一致的 shell 命令格式。两处保持完全一致，避免主 Agent 在两份文档间找差异。

**同步原则**：state-machine.md 步骤 5 是主 Agent 的执行参考（步骤 0 已读），dispatch-protocol.md 门槛表是完整定义。两处的 shell 命令必须一致，差异只在 dispatch-protocol.md 保留额外的设计说明（A1 原则、C7 规则、B7 规则等）。

---

## 不落地项

| # | 原始建议 | 不落地理由 |
|---|---------|-----------|
| gate-cheatsheet.md 新增文件 | 四处重复 + 静态命令与动态规则冲突 + 绕过专用脚本 + 不可强制的警告 |
| dispatch-base.md | 不省 subagent 上下文，引入版本一致性风险 |
| skip_reviews | Agent 自信判断不可信，评审不可跳过 |
| 分层 P5 gate | 质量环节不可裁减 |
| verification_env | subagent 无 timeout kill，写跑分离隔离 hang 风险 |
| 信任等级 | 不需要单独分类 |

## 与 T022 计划的交叉

T022 计划的 7 项动作修改 state-machine.md 和 dispatch-protocol.md 的 gate 定义。本计划的动作 1 和动作 3 也修改同一位置。

**执行顺序**：T022 先落地（修改 gate 定义），本计划后落地（优化命令格式）。本计划不改变 gate 逻辑，只改变呈现格式——从自然语言改为 shell 命令。T022 落地后的新规则（P6 BDD count、P7 DEVIATION-CRITICAL、P8 bump 后重跑 P5）直接以 shell 命令格式写入，不需要二次转换。

## 落地清单

| # | 动作 | 文件 | 工作量 |
|---|------|------|--------|
| 1 | 步骤 5 gate 命令格式优化 | state-machine.md | 10 分钟 |
| 2 | check-tdd-red.sh 裸 pytest 修复 | assets/templates/check-tdd-red.sh | 5 分钟 |
| 3 | 门槛表同步 shell 命令格式 | dispatch-protocol.md | 10 分钟 |

**总计**：3 项动作，约 25 分钟。

## 收益评估

| 维度 | 前版（cheatsheet） | 本版（内联优化） |
|------|-------------------|----------------|
| gate 命令可执行性 | ✅ shell 命令 | ✅ shell 命令 |
| 新增文件 | 1 个（cheatsheet） | 0 个 |
| gate 命令重复处数 | 4→4（不减少） | 3→2（步骤 5 和门槛表统一格式，转移规则保留形式化表述） |
| 动态 gate 规则保留 | ❌ 压成静态一行 | ✅ P5/P6 从 P2 gate_commands 读取 |
| check-tdd-red.sh 判定逻辑 | ❌ 绕过 | ✅ 保留 + 修 bug |
| 一致性检查扩展 | 需要 | 不需要（无新文件） |
