# Phase 2A 补充计划评审

> 评审对象：`docs/plans/hardening-phase2a-supplement-2026-06-30.md`
> 评审日期：2026-06-30
> 评审方法：逐行通读 + 逻辑推演

---

## 总体判断

**P2.15（.state.yaml 格式校验）设计正确，可以实施。P2.6（修复后全量重跑验证）有一个 🔴 设计缺陷——检查的时序和语义不匹配，会导致正常流程被误拦。**

---

## 🔴 阻断级

### R1：check-fix-rerun.sh 的 phase 匹配逻辑与时序冲突

**位置**：Task 2, `check-fix-rerun.sh` Step 1

```bash
# 检查 .gate-result.json 是否是 full run（phase 匹配 last_fix_phase）
RESULT_PHASE=$(python3 -c "...print(data.get('phase', ''))..." )

if [ "$RESULT_PHASE" != "$LAST_FIX" ]; then
    echo "GATE FIX-RERUN: phase=${RESULT_PHASE} != last_fix_phase=${LAST_FIX}"
    exit 1
fi
```

**问题**：`.gate-result.json` 由 `pre-commit-gate.sh` 的 `write_gate_result` 写入，记录的是**当前 phase**（从 .state.yaml 读取的 `phase` 字段）。而 `last_fix_phase` 记录的是"修复了哪个阶段"。

正常流程：Agent 在 P5 发现失败 → 回 P4 修复 → 重跑 P5 gate → P5 通过 → 推进到 P6。此时 `.state.yaml` 的 `phase: P6`，`last_fix_phase: P5`。`.gate-result.json` 的 `phase: P6`。检查 `P6 != P5` → **误拦**。

**根因**：`last_fix_phase` 表示"曾经修复过哪个阶段"，`.gate-result.json` 的 `phase` 表示"当前在哪个阶段"。这两个不是同一个东西。检查它们相等是语义错误。

**修法**：P2.6 的真正目的是"修复后必须重跑 full gate，不能只跑修复项"。但 pre-commit hook 无法区分"full run"和"partial run"——它只跑一次 check-gate.sh，没有"partial"的概念。这个检查应该在 **主 Agent 流程层**做（dispatch-protocol.md 的 P5 修复流程已规定"必须重跑全量"），不在 hook 层。

**建议**：**删除 check-fix-rerun.sh，P2.6 从 Phase 2A 移除**。理由：
1. hook 无法验证"full run vs partial run"——hook 只跑一次 gate，没有 partial 概念
2. `last_fix_phase` 字段的语义在当前架构里无法被机器验证
3. P5 修复后全量重跑的规则已在 dispatch-protocol.md 里（T027 教训），属于流程层规则
4. 强行加一个错误的检查比没有检查更糟（误拦正常流程）

如果一定要在 hook 层做什么，应该是：`last_fix_phase` 存在时输出 WARNING 提醒"确认已重跑全量 gate"，不中止 commit。但这和 P2.6 的"验证"目标不符——WARNING 不是验证。

---

## 🟡 中优先级

### M1：check-state-yaml.sh 的 YAML 解析失败处理

**位置**：Task 1, `check-state-yaml.sh` Step 1

```bash
ERRORS=$(python3 -c "..." 2>/dev/null || echo "YAML 解析失败")
```

**问题**：`2>/dev/null` 吞掉了 Python 的错误输出。如果 YAML 语法错误（如缩进错误），用户看不到具体错误信息，只看到 "YAML 解析失败"。

**修法**：保留 stderr 输出，或捕获到变量里输出：

```bash
ERRORS=$(python3 -c "..." 2>&1 || true)
```

这样 YAML 解析错误的具体信息会出现在 ERRORS 里。

### M2：check-state-yaml.sh 的 shell 变量注入 Python 代码

**位置**：Task 1, `check-state-yaml.sh` Step 1

```bash
ERRORS=$(python3 -c "
...
with open('$STATE_FILE') as f:
...
valid_phases = '$VALID_PHASES'.split()
...
")
```

**问题**：`$STATE_FILE` 和 `$VALID_PHASES` 直接 shell 展开到 Python 字符串里。如果路径含单引号（如 `it's a test.yaml`），Python 代码会语法错误。低风险但不规范。

**修法**：用环境变量传参：

```bash
STATE_FILE="$STATE_FILE" VALID_PHASES="$VALID_PHASES" python3 -c "
import os
state_file = os.environ['STATE_FILE']
valid_phases = os.environ['VALID_PHASES'].split()
with open(state_file) as f:
    ...
"
```

---

## 确认正确的部分

**P2.15 格式校验的检查项正确**：必填字段（task_id/phase/status）、task_id 格式（T+数字）、phase 合法值（P0-P8/PAUSED/READY/DONE）、retries 列表结构、retries key 大写 P+数字。这些与 state-machine.md:412-443 的协议模板完全对齐。

**集成位置正确**：格式校验放在 PROD_TOUCHED 检测之后、状态转移检查之前——先确保 .state.yaml 格式正确，再做状态转移检查（后者依赖前者读取的 phase 值）。

**测试用例覆盖合理**：合法格式/缺字段/非法 phase/retries 非列表，四个场景覆盖主要失败模式。

---

## 修复优先级汇总

| # | 问题 | 严重度 | 修复 |
|---|------|--------|------|
| R1 | check-fix-rerun.sh phase 匹配语义错误 | 🔴 | 删除 check-fix-rerun.sh，P2.6 移除 |
| M1 | YAML 解析错误信息被吞 | 🟡 | `2>/dev/null` 改 `2>&1` |
| M2 | shell 变量注入 Python | 🟡 | 用环境变量传参 |

**建议执行**：删除 Task 2（check-fix-rerun.sh），Task 3 集成只加 P2.15 格式校验，Task 4 roadmap 只更新 P2.15。
