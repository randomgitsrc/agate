---
type: plan
source: docs/reviews/agate-T025-gate-optimization-plan-audit-2026-06-28.md
trace_id: agate-T025-gate-optimization-v3-2026-06-28
created: 2026-06-28
status: 待执行
replaces: agate-T025-gate-optimization-2026-06-28
---

# 修复方案：T025 gate 判定效率优化（v3）

> 来源：`docs/reviews/agate-T025-feedback-review-2026-06-28.md`（采纳 A 修正版）
> v1：cheatsheet 新增文件 → 评审否决（四处重复、静态 vs 动态冲突）
> v2：内联 shell 命令化 → 复核发现 5/8 gate 的 shell 命令有语义错误
> v3：按可自动化程度分档，不追求全部 shell 命令化

---

## v2 复核发现回顾

| Gate | 问题 | 根因 |
|------|------|------|
| P1 | BDD 正则 `AC\d+.*Given.*When.*Then` 不匹配 BE-1/FE-1 等格式；CAPABILITY_GAP grep 无法区分 status:GAP vs status:supplementable | BDD 编号格式是项目/任务特定的；CAPABILITY_GAP 需要语义判定 |
| P2 | `grep -qE` 四字段只验证至少一个命中，不验证四个全命中 | 需要计数=4，不是存在性 |
| P5 | "从 P2 gate_commands 读取"不是 shell 命令；PROD_TOUCHED grep -rc 假阳性高 | P5 gate 命令是动态注入的；PROD_TOUCHED 可能出现在说明性文本中 |
| P6 | `grep -c 'FAIL'` 匹配说明性文本中的 "FAIL" | 需要锚定到标记格式 |
| P8 | `git diff --stat` 在 P8 commit 后为空；CHANGELOG grep 检查了错误的文件 | P8 完成时已 commit；CHANGELOG 是项目根文件不是 P8-release.md 内容 |
| 动作2 | P0-brief 无 test_runner 字段；assets/templates/ 无 check-tdd-red.sh；YAML 解析脆弱 | 引用了不存在的字段和文件 |

**核心教训**：agate 的 gate 规则是分层的——有些可静态 shell 化（P3/P4/P7），有些是动态注入（P5/P6 从 P2 gate_commands 读取），有些需要语义判断（P1 BDD 格式、P2 四字段全命中、P8 CHANGELOG 是项目根文件）。强行全部 shell 命令化会引入假阴性/假阳性。

---

## v3 方案：按可自动化程度分档优化

**原则**：不追求格式统一，追求每条 gate 判定命令的语义正确性。可 shell 化的写 shell 命令，不可的保留自然语言但补判定示例。

### 动作 1：优化 state-machine.md 步骤 5

**文件**：`state-machine.md` L286-295

**改为**：
```
5. 主 Agent 亲自跑 gate 命令验证门槛（A1 原则：跑命令不信文件）：
   - P1: P1-requirements.md 含 ≥1 条 BDD 条件（BDD 编号格式不固定，按实际格式 grep）;
         grep -cE '\[NEED_CONFIRM\]' {task}/P1-requirements.md → =0;
         grep -cE 'status:.*GAP\b' {task}/P1-requirements.md → =0（仅匹配 status: GAP，不匹配 supplementable）
   - P2: grep 'status: approved' {task}/P2-review.md → 命中;
         grep -cE '^(packages|domains|ui_affected|gate_commands):' {task}/P2-design.md → =4
   - P3: scripts/check-tdd-red.sh → exit 0;
         （UI 任务：确认 P3-test-cases.md 含 Playwright/E2E 用例描述）
   - P4: git log --oneline -1 → 含 "P4" 或 "wf(Txxx-P4)"
   - P5: 从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0;
         grep -rl '\[PROD_TOUCHED\]' {task}/ → 无命中（匹配标记格式，不匹配说明性文本）;
         （UI 任务：从 gate_commands.P5 读取 E2E 命令执行 → exit 0）
   - P6: grep -cE '^\s*- (PASS|FAIL)' {task}/P6-acceptance.md → =P1 BDD 总数;
         grep -cE '^\s*- FAIL\b' {task}/P6-acceptance.md → =0;
         grep -cE '\[NEED_CONFIRM\]' {task}/P6-acceptance.md → =0;
         （UI 条件：vision-analyst YAML summary.blocker_count → =0）
   - P7: grep -cE '^\s*-?\s*\[BLOCKER\]' {task}/P7-consistency.md → =0;
         grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' {task}/P7-consistency.md → =0
   - P8: 从 P2-design.md gate_commands 逐包读取发布检查命令执行 → 全部 exit 0;
         git diff HEAD~1 --stat → 含 version 文件变更;
         git diff HEAD~1 -- CHANGELOG.md → 非空（CHANGELOG 是项目根文件，不是 P8-release.md 内容）
```

**与 v2 的差异**：

| Gate | v2 | v3 | 修正原因 |
|------|----|----|---------|
| P1 BDD | `grep -cE 'AC\d+.*Given.*When.*Then'` | 保留自然语言 + "按实际格式 grep" | BDD 编号格式不固定，单一正则假阴性 |
| P1 CAPABILITY_GAP | `grep -c CAPABILITY_GAP` | `grep -cE 'status:.*GAP\b'` | 区分 GAP vs supplementable |
| P1 NEED_CONFIRM | `grep -c NEED_CONFIRM` | `grep -cE '\[NEED_CONFIRM\]'` | 锚定标记格式，减少假阳性 |
| P2 四字段 | `grep -qE`（至少一个） | `grep -cE` → =4 | 确保四个全命中 |
| P5 PROD_TOUCHED | `grep -rc PROD_TOUCHED` | `grep -rl '\[PROD_TOUCHED\]'` | 匹配标记格式，-l 只列文件名 |
| P6 FAIL | `grep -c 'FAIL'` | `grep -cE '^\s*- FAIL\b'` | 锚定行首标记格式 |
| P8 version | `git diff --stat` | `git diff HEAD~1 --stat` | P8 完成时已 commit，diff 为空 |
| P8 CHANGELOG | `grep -q CHANGELOG {task}/P8-release.md` | `git diff HEAD~1 -- CHANGELOG.md` | CHANGELOG 是项目根文件 |

**保留自然语言的部分**（不可 shell 化的 gate）：
- P1 BDD 条件 ≥1：BDD 编号格式由 analyst 角色定义约束但编号本身是自由的，主 Agent 需根据 P1 实际格式构造 grep
- P5/P6 gate 命令：从 P2 gate_commands 动态读取，无法提前写死
- P3 UI 附加条件：Playwright 用例"存在"需要看内容，不是纯 grep
- P6 UI 条件：vision-analyst blocker_count 需要解析 YAML，不是 grep

### 动作 2：修复 check-tdd-red.sh 的裸 pytest bug

**文件**：`scripts/check-tdd-red.sh`

**问题**：脚本 L11 用裸 `pytest`，在 venv 项目中裸 pytest 不存在 → `|| true` 吞掉错误 → 假绿灯。

**改法**：脚本接受环境变量 `TEST_RUNNER`，主 Agent 在调用前从 P0-brief.md 的 env_constraints.debug_env 读取测试启动命令并 export。脚本内部回退链：

```bash
# 旧：RESULT=$(pytest -q 2>&1)
# 新：
if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var or install pytest." >&2
    exit 3
fi
RESULT=$($RUNNER -q 2>&1)
```

**主 Agent 调用方式**（在步骤 5 P3 gate 处）：
```
从 P0-brief.md env_constraints.debug_env 提取测试启动命令
export TEST_RUNNER="{提取的命令，如 .venv/bin/python -m pytest}"
scripts/check-tdd-red.sh
```

**设计决策**：
1. 不在脚本内解析 P0-brief.md（YAML 解析脆弱）
2. 不在脚本内硬编码 venv 路径（项目结构不同）
3. 主 Agent 在调用前 export 环境变量——主 Agent 读 P0-brief 是合法职责
4. 回退链：`$TEST_RUNNER` → `which pytest` → 报错 exit 3（明确失败，不假绿灯）

### 动作 3：dispatch-protocol.md 门槛表同步

**文件**：`dispatch-protocol.md` L505-514「可判定门槛规范」表

**改法**：在"怎么判定"列中，把可 shell 化的部分改为 shell 命令（与步骤 5 一致），不可 shell 化的保留自然语言。两处的判定逻辑必须语义等价。

**同步原则**：state-machine.md 步骤 5 是主 Agent 的执行参考，dispatch-protocol.md 门槛表是完整定义。shell 命令部分完全一致，自然语言部分门槛表可更详细（含设计说明）。

---

## 不落地项

| # | 原始建议 | 不落地理由 |
|---|---------|-----------|
| gate-cheatsheet.md | 四处重复 + 静态 vs 动态冲突 + 绕过专用脚本 |
| 全部 shell 命令化 | P1/P2/P5/P6/P8 的 gate 规则需要动态注入或语义判断，强行 shell 化引入假阴性/假阳性 |
| dispatch-base.md | 不省 subagent 上下文 |
| skip_reviews | Agent 自信判断不可信 |
| 分层 P5 gate | 质量环节不可裁减 |
| verification_env | 写跑分离隔离 hang 风险 |

## 与 T022 计划的交叉

同 v2：T022 先落地（修改 gate 定义），本计划后落地（优化命令格式）。T022 的新规则（P6 BDD count、P7 DEVIATION-CRITICAL、P8 bump 后重跑 P5）直接以正确格式写入。

## 落地清单

| # | 动作 | 文件 | 工作量 |
|---|------|------|--------|
| 1 | 步骤 5 gate 命令分档优化 | state-machine.md | 15 分钟 |
| 2 | check-tdd-red.sh 环境变量修复 | scripts/check-tdd-red.sh | 8 分钟 |
| 3 | 门槛表同步 | dispatch-protocol.md | 15 分钟 |

**总计**：3 项动作，约 38 分钟。

## 收益评估

| 维度 | v1（cheatsheet） | v2（全 shell 化） | v3（分档） |
|------|-----------------|-----------------|-----------|
| gate 命令可执行性 | ✅ 但有语义错误 | ✅ 但有语义错误 | ✅ 语义正确 |
| 假阴性/假阳性风险 | 高（P1/P6/P8） | 高（P1/P2/P5/P6/P8） | 低（已逐条修正） |
| 新增文件 | 1 | 0 | 0 |
| 动态 gate 规则保留 | ❌ | ❌ P5/P6 硬写 | ✅ 保留"从 P2 gate_commands 读取" |
| check-tdd-red.sh 修复 | 绕过脚本 | 引用不存在的字段 | ✅ 环境变量 + 回退链 |
| 格式一致性 | 全 shell | 全 shell | 混合（可 shell 的 shell，不可的自然语言） |
