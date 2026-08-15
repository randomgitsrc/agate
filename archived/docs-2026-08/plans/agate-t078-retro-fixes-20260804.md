# T078 复盘改进计划

> 2026-08-04 | 来源：T078 read-tracking-hardening 复盘（3 个被误归因的 agate 改进项）

## 背景

T078 复盘第二版"修正归因"将 7 次中断全部归为 opencode 平台 + 主 Agent 执行 + 任务调度，结论"agate 协议 0 损耗"。但实际有 3 个 agate 可改进项被过度修正推给了执行方/环境：

1. **P6 总结行格式**：隐式约定（行首 `- PASS`/`- FAIL` 只用于 BDD 条目）未显式化 → verifier subagent 写了 `- PASS：34` 被 gate 误判
2. **check-tdd-red.sh 缺 timeout**：formatter 卡住时脚本无限等待 → CI backstop 也会卡
3. **P0 卡片缺 hardening 审计提示**：P0 只要求四字段，hardening 类任务缺代码审计引导 → P0-brief 写两次浪费 30 min

## Task 1: P6 总结行格式显式化

**Files:**
- Modify: `agate/phase-cards/P6-acceptance.md`（格式规范节追加总结行禁令）
- Modify: `agate/scripts/check-p6-format.sh`（--fix 加总结行自动修正）
- Modify: `agate/tests/unit/check-p6-format.bats`（新增测试）
- Modify: `agate/tests/unit/check-gate.bats`（G6 系列确认总结行不被误判）

### 问题机制

gate 用 `grep -cE '^\s*- (PASS|FAIL)\b'` 统计 BDD 条目数。任何行首 `- PASS`/`- FAIL` 都会被匹配——包括总结行 `- PASS：34` / `- FAIL：0`。provenance 也用同样的正则扫描 dispatch-context。

T078 中 verifier subagent 写了：
```
- PASS：34
- FAIL：0
```
被 gate 误判为 2 条 BDD 条目（其中 `- FAIL：0` 使 FAIL > 0 → gate exit 1）。

### Step 1: P6 卡片追加格式规范

在 `### P6-acceptance.md` 节的 PASS 行格式规范后追加：

```markdown
**总结行格式**：行首 `- PASS`/`- FAIL` 只用于 BDD 条目，不得用于总结行。总结行用其他格式：
```
**Summary**: 34/34 PASS, 0 FAIL
```
```

### Step 2: check-p6-format.sh 加总结行检测 + 自动修正

**check 模式和 fix 模式都加总结行检测**。check 模式检测到总结行 → exit 1（强制跑 --fix）。fix 模式自动修正。

插入位置：在现有 L39（行首空白修正后 `CONTENT="$FIXED"` 之后、`if [ "$MODE" = "fix" ]` 之前）追加：

```bash
# 总结行修正：行首 - PASS/- FAIL 后面不含 BDD-NN（纯数字结尾）→ 改为 Summary 格式
FIXED=$(printf '%s' "$FIXED" | sed -E 's/^-\s+(PASS|FAIL)\s*[:：]\s*([0-9]+)\s*$/\*\*Summary\*\*: \1: \2/')
if [ "$FIXED" != "$CONTENT" ]; then
    CHANGES=1
fi
CONTENT="$FIXED"
```

这样 check 模式也会检测到总结行（CHANGES=1 → exit 1），fix 模式自动修正。

### Step 3: 测试

```bash
@test "F11 check-p6-format.sh --fix: summary line - PASS：34 → **Summary**: PASS: 34" {
    # 创建含总结行的 P6-acceptance.md
    # --fix 后总结行被修正
    # gate 不再误判为 BDD 条目
}
```

## Task 2: check-tdd-red.sh 内部 timeout

**Files:**
- Modify: `agate/scripts/gate-result.sh`（run_test_with_formatter 加 timeout）
- Modify: `agate/tests/unit/check-tdd-red.bats`（新增 timeout 测试）

### 问题机制

`run_test_with_formatter()`（gate-result.sh L90）用 `eval "$cmd"` 跑测试命令，无 timeout。如果测试命令或 formatter 卡住，脚本无限等待。

T078 中 check-tdd-red.sh 120s 未完成（手动 pytest 5.66s），根因可能是 formatter 环境检测卡住。

### Step 1: 加 timeout

`gate-result.sh` `run_test_with_formatter()` L90：

```bash
# 当前
output=$(eval "$cmd" 2>&1) && exit_code=0 || exit_code=$?

# 改为
local timeout_secs="${AGATE_TDD_TIMEOUT:-120}"
if command -v timeout &>/dev/null; then
    output=$(timeout "$timeout_secs" bash -c "$cmd" 2>&1) && exit_code=0 || exit_code=$?
else
    # macOS 无 timeout 命令，跳过 timeout 保护
    output=$(eval "$cmd" 2>&1) && exit_code=0 || exit_code=$?
fi
if [ "$exit_code" -eq 124 ]; then
    echo "TDD_CHECK: 测试命令超时（${timeout_secs}s），请手动运行确认：$cmd" >&2
    echo "{\"exit_code\":124,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[]}"
    return 0
fi
```

exit 124（timeout 默认 exit code）→ JSON `exit_code: 124` → judge_result 需要专门处理（见 Step 2）。

**macOS 兼容**：`command -v timeout` 检测，无 timeout 时跳过保护（退化为原有行为）。CI 是 Linux，有 timeout。本地 macOS 开发者如需 timeout 可 `brew install coreutils`（提供 `gtimeout`，但不做自动别名——保持简单）。

### Step 2: judge_result 加 124 分支

**关键**：124 分支必须加在 L96 `exit_code == 0` 判断之前，否则会被 L140 `exit_code >= 120` 拦截为 A 类错误（return 1），与"红灯可推进"矛盾。

check-tdd-red.sh `judge_result()` L96 之前插入：

```bash
    if [ "$exit_code" -eq 124 ]; then
        echo "TDD_CHECK: 测试命令超时，视为红灯可推进（请手动确认测试确实失败）"
        return 0
    fi
```

这样 timeout → exit 0（红灯可推进），主 Agent 可手动确认。

**agate-capture-env-baseline.sh 兼容性**：capture-env-baseline.sh L85 `if [ "$JSON_EXIT_CODE" -ge 120 ]` 会处理 exit 124 → 放弃捕获（`PARSE_OK=0`）→ 输出"命令本身崩溃"。这是合理行为（超时确实无法捕获 baseline），不需要改。

### Step 3: 测试

```bash
@test "TDD.TIMEOUT: 测试命令超时 → exit 0 + 超时提示" {
    # TEST_RUNNER 指向 sleep 70（超过 AGATE_TDD_TIMEOUT=2）
    # 期望 exit 0 + 输出含"超时"
}
```

## Task 3: P0 卡片 hardening 审计提示

**Files:**
- Modify: `agate/phase-cards/P0-orchestrator.md`（推进条件后追加提示）

### 改动

在 P0 卡片"下游影响"节前追加：

```markdown
## 任务类型提示

**hardening / refactor 类任务**：P0-brief 建议包含代码审计结果（现有代码的问题清单），作为 P1 需求的输入。P0 卡片不强制要求审计（非门槛），但跳过审计可能导致 P1 需求不完整、P2 设计基于错误假设。
```

### 测试

无需测试（纯文档措辞）。

## Task 4: roadmap + 全量验证

### Step 1: 更新 roadmap

三项从"待处理"改为"已实施"。

### Step 2: 全量验证

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
bash agate/tests/scripts/count-tests.sh
```

## Self-Review

### 1. 影响范围

- Task 1: check-p6-format.sh 改动影响 check 和 fix 模式（总结行检测两模式都触发）。现有 P6 测试不受影响（无总结行）
- Task 2: gate-result.sh 是公共函数库，但 timeout 只影响 `run_test_with_formatter`（check-tdd-red.sh 和 agate-capture-env-baseline.sh 调用）。默认 60s，可通过 `AGATE_TDD_TIMEOUT` 环境变量覆盖
- Task 3: 纯文档，无脚本/测试影响

### 2. 向后兼容

- check-p6-format.sh 新增的总结行修正只匹配 `- PASS：数字` / `- FAIL：数字`，不影响正常 BDD 行（`- PASS BDD-NN: ...`）
- timeout 默认 60s，现有测试命令都在 60s 内完成
- P0 卡片提示是"建议"非"门槛"

### 3. 风险

- check-p6-format.sh 总结行正则可能误匹配：`- PASS: 3 条说明` 会被匹配吗？正则要求行尾是纯数字 `\s*$`，`3 条说明` 不匹配 → 安全
- timeout 120s 可能不够：大型项目测试可能 > 120s。但 check-tdd-red.sh 主要在 P3 确认红灯时跑（测试少），P5 用 gate_commands.P5 不走此脚本。可通过 AGATE_TDD_TIMEOUT 覆盖
- 行首 PASS/FAIL 误匹配范围：grep 确认 4 处正则全部在 P6 相关脚本（check-gate.sh L253、check-p6-provenance.sh L119+L134、check-p6-evidence.sh L16）。其他阶段无此格式。dispatch-context 中的预判检查（provenance L119）也用同一正则——T078 中 dispatch-context 的 `- PASS 有证据文件引用` 也被误判。check-p6-format.sh 只修 P6-acceptance.md（不修 dispatch-context），但 P6 卡片明确写约定后主 Agent 和 verifier 都能看到，从源头避免
- macOS 无 `timeout` 命令：已加 `command -v timeout` 检测，无则跳过（退化为原有行为）

### 4. 评审修复记录

| # | 级别 | 问题 | 修复 |
|---|------|------|------|
| 1 | BLOCKER | check-p6-format.sh 只改 fix 不改 check，gate 仍误判 | check 模式也加总结行检测 → exit 1 |
| 2 | BLOCKER | exit 124 被 judge_result L140 `exit_code >= 120` 拦截为 A 类 | 124 分支加在 L96 之前 return 0 |
| 3 | BLOCKER | macOS 无 timeout 命令 | 加 `command -v timeout` 检测，无则跳过 |
