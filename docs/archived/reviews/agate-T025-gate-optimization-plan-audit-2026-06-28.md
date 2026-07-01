---
type: review
source: docs/plans/agate-T025-gate-optimization-2026-06-28.md
trace_id: agate-T025-gate-optimization-plan-audit-2026-06-28
created: 2026-06-28
status: done
---

# T025 Gate 优化计划复核：Shell 命令逐条审计

> 复核对象：`docs/plans/agate-T025-gate-optimization-2026-06-28.md` 动作 1/2/3 中的 shell 命令
> 复核方法：逐条对照 state-machine.md 转移规则 + dispatch-protocol.md 门槛表的实际规则，验证命令语义等价性
> 对照基准：P0-brief.md 实际字段、P1 产出实际格式、T025 实战数据

---

## 动作 1：步骤 5 gate 命令审计

### P1：3 条命令，2 条有问题

| # | 计划命令 | 预期语义 | 实际问题 |
|---|---------|---------|---------|
| P1-a | `grep -cE 'AC\d+.*Given.*When.*Then' {task}/P1-requirements.md → ≥1` | P1 含 ≥1 条 BDD 条件 | **正则不匹配实际格式**。T025 的 BDD 用 BE-1/FE-1 编号，不是 AC 前缀。不同项目的 BDD 编号格式不同（AC/BE/FE/TC），这个正则会假阴性 |
| P1-b | `grep -c NEED_CONFIRM {task}/P1-requirements.md → =0` | 无未决 NEED_CONFIRM | 语义正确，但注意：`NEED_CONFIRM` 可能出现在 `capability_requirements` 的描述文本中被提及但已解决，导致假阳性 |
| P1-c | `grep -c CAPABILITY_GAP {task}/P1-requirements.md → =0` | 无 CAPABILITY_GAP | **误判 supplementable 为 GAP**。P1 的 capability_requirements 中 `status: supplementable` 的条目也会包含字符串 `CAPABILITY_GAP`（在上下文描述中），但 supplementable 不阻塞。协议原文是"无 `[CAPABILITY_GAP]`"——特指 `status: GAP` 的条目，不是字符串出现 |

**P1 根因**：BDD 条件的格式是项目/任务特定的，不能用单一正则匹配。CAPABILITY_GAP 的判定需要区分标记语义（`status: GAP` vs `status: supplementable`），不能靠字符串计数。

**修正方向**：
- P1-a：不改。P1 gate 的"BDD 条件 ≥1"本身不可单一正则判定——BDD 格式由 analyst 角色定义约束，但编号格式是自由的。保留自然语言描述，不硬写正则
- P1-c：改为 `grep -cE 'status:.*GAP' {task}/P1-requirements.md → =0`，只匹配 `status:` 行中的 GAP

### P2：1 条命令，逻辑有漏洞

| # | 计划命令 | 预期语义 | 实际问题 |
|---|---------|---------|---------|
| P2-a | `grep -qE '^(packages\|domains\|ui_affected\|gate_commands):' {task}/P2-design.md → 四字段均命中` | P2-design.md 含四字段 | **`grep -qE` 只验证至少一个命中，不验证四个全命中**。3/4 字段存在时仍 exit 0。这不是"四字段均命中" |

**修正方向**：拆成 4 个 `grep -q`，或用 `grep -cE '^(packages|domains|ui_affected|gate_commands):' {task}/P2-design.md → =4`。后者更紧凑。

### P3：无问题

`scripts/check-tdd-red.sh → exit 0` 与协议一致。UI 任务附加条件是自然语言（合理，因为 Playwright 用例的"存在"本身不是纯 grep 能判定的——需要看 P3-test-cases.md 的内容是否含 E2E 描述）。

### P4：无问题

`git log --oneline -1 → 含 "P4"` 与协议一致。

### P5：2 条命令，1 条有问题，1 条不是 shell 命令

| # | 计划命令 | 预期语义 | 实际问题 |
|---|---------|---------|---------|
| P5-a | `从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0` | 执行 P2 声明的 P5 gate 命令 | **不是 shell 命令，是自然语言指令**。计划的定位是"把自然语言改为可直接执行的 shell 命令"，但 P5 命令是动态的——无法提前写死。这与计划的定位矛盾 |
| P5-b | `grep -rc PROD_TOUCHED {task}/ → =0` | 无 PROD_TOUCHED 标记 | **假阳性风险高**。`-r` 递归搜索 {task}/ 下所有文件，P6-acceptance.md 可能包含"验证无 PROD_TOUCHED"的文本，P5-verification.md 可能引用 PROD_TOUCHED 检查过程。`-c` 统计出现次数，不是标记计数 |

**P5-a 修正方向**：承认 P5/P6 的 gate 命令是动态注入的，不能写成固定 shell 命令。步骤 5 的 P5/P6 行保留"从 P2 gate_commands 读取"的自然语言，但把"读取后执行"的通用模式写成示例（如 `grep 'P5:' {task}/P2-design.md → 提取命令 → 执行 → exit 0`）

**P5-b 修正方向**：改为 `grep -rl PROD_TOUCHED {task}/ → 无命中`（`-l` 只列文件名，不计数），或更精确地 `grep -cE '^\s*-?\s*\[PROD_TOUCHED\]' {task}/ → =0`（匹配标记格式，不匹配提及文本）

### P6：3 条命令，1 条有问题

| # | 计划命令 | 预期语义 | 实际问题 |
|---|---------|---------|---------|
| P6-a | `grep -cE '^\s*- (PASS\|FAIL)' {task}/P6-acceptance.md → =P1 BDD 总数` | P6 验收条数 == P1 BDD 总数 | P1 BDD 总数本身的计算方式有问题（见 P1-a），但 P6 这条自身的逻辑是对的——只要 P1 那边能正确算出总数 |
| P6-b | `grep -c 'FAIL' {task}/P6-acceptance.md → =0` | 无 FAIL 条件 | **假阳性**。`grep -c 'FAIL'` 会匹配任何含 "FAIL" 的行，包括 "previous FAIL was fixed" 或 "failure_mode" 等说明性文本。应锚定：`grep -cE '^\s*- FAIL\b' {task}/P6-acceptance.md → =0` |
| P6-c | `grep -c NEED_CONFIRM {task}/P6-acceptance.md → =0` | 无未决 NEED_CONFIRM | 同 P1-b 的问题，但 P6 产出中 NEED_CONFIRM 出现在描述文本里的概率更低。可接受 |

### P7：无问题

两条 grep 与协议一致（BLOCKER + DEVIATION-CRITICAL）。

### P8：2 条命令，2 条有问题

| # | 计划命令 | 预期语义 | 实际问题 |
|---|---------|---------|---------|
| P8-a | `git diff --stat → 含 version 文件变更` | git diff 确认各包 version bump | **P8 完成时会 commit，git diff 为空**。这和 P4 gate 的坑一样（state-machine.md L95 明确写了"P4 完成时会 commit，git diff 永远是空"）。应改为 `git log --oneline -1` 确认 P8 commit，或 `git diff HEAD~1 --stat` 看最近一次 commit 的变更 |
| P8-b | `grep -q CHANGELOG {task}/P8-release.md → 命中` | CHANGELOG 已更新 | **检查了错误的文件**。CHANGELOG 是项目根目录文件，不是 P8-release.md 的内容。协议原文是"CHANGELOG 已更新"，主 Agent 应检查项目根 CHANGELOG 文件有变更（`git diff HEAD~1 -- CHANGELOG.md`），不是 grep P8-release.md |

---

## 动作 2：check-tdd-red.sh 修复审计

### 问题 1：修复引用了不存在的 P0-brief 字段

计划写：`从 P0-brief.md 的 executor_env 读取 test runner 路径`，然后脚本里 `grep 'test_runner'`。

但 P0-brief.md 的 executor_env 字段（dispatch-protocol.md L169-177）只定义了：
```yaml
executor_env:
  platform: ...
  has_task_tool: ...
  has_local_runtime: ...
  network: ...
```

**没有 `test_runner` 字段**。脚本 `grep 'test_runner' P0-brief.md` 永远找不到。

### 问题 2：修复目标文件不存在

计划写修复 `assets/templates/check-tdd-red.sh`，但 `assets/templates/` 下只有 4 个文件：
- active-tasks-template.md
- custom-role.md
- dispatch-prompt.md
- task-files.md

**没有 check-tdd-red.sh**。实际脚本在 `scripts/check-tdd-red.sh`（agate 协议自身的脚本，不是项目模板）。

### 问题 3：从 P0-brief 动态解析是脆弱方案

脚本在运行时用 `grep -A5 | grep | sed` 解析 YAML 文件提取字段，这种方式对格式变化极其脆弱（缩进变化、字段顺序变化、注释行都会导致解析失败）。

**修正方向**：
1. 脚本接受环境变量 `TEST_RUNNER`，主 Agent 在调用前从 P0-brief 读取并 export
2. 脚本内部回退链：`$TEST_RUNNER` → `which pytest` → 报错退出
3. 不在脚本里解析 YAML

---

## 动作 3：dispatch-protocol.md 门槛表同步

动作 1 的命令有问题，门槛表如果照抄会继承所有问题。必须先修动作 1 的命令，再同步到门槛表。

---

## 复核结论

动作 1 的 8 个 gate 中，5 个有命令问题（P1/P2/P5/P6/P8），3 个无问题（P3/P4/P7）。动作 2 的修复方案有 3 个问题（字段不存在、文件不存在、解析脆弱）。

**核心问题**：计划的"shell 命令格式"假设所有 gate 判定都能写成静态 shell 命令，但 agate 的 gate 规则是分层的——有些是静态可写（P3/P4/P7），有些是动态注入（P5/P6 从 P2 gate_commands 读取），有些需要语义判断（P1 的 BDD 格式、P2 的四字段全命中）。

**建议**：不追求全部 shell 命令化。按 gate 的可自动化程度分两档：
- **可 shell 化的 gate**（P3/P4/P7）：写 shell 命令
- **需要动态/语义判断的 gate**（P1/P2/P5/P6/P8）：保留自然语言 + 补充关键判定命令示例

这不是偷懒——是尊重 agate 的 gate 规则设计现实：动态注入和语义判断本来就不是一行 grep 能解决的。
