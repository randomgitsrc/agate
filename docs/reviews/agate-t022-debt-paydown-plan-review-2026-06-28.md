---
type: review
source: docs/plans/agate-t022-debt-paydown-2026-06-28.md
trace_id: agate-t022-debt-paydown-plan-review-2026-06-28
created: 2026-06-28
status: done
---

# T022 债务清还计划专家评审

> 评审对象：`docs/plans/agate-t022-debt-paydown-2026-06-28.md`（8 项动作）
> 评审焦点：动作 1-7 与 T025 gate-opt 已落地内容的一致性、动作 8 check-gate.sh 的设计合理性

---

## 动作 1-7 评审：T022 原始 plan 的落地，无重大问题

动作 1-7 是 T022 plan 的直接执行，plan 本身经过 T022 评审已裁决。逐条快速复核：

| 动作 | 判定 | 备注 |
|------|------|------|
| 1 dispatch-prompt 补 BDD 覆盖完整性 | ✅ | 补的是 T025 gate-opt 遗漏的文件 |
| 2 P8 bump 后重跑 P5 + bump_type | ✅ | 需注意：当前 P8 转移规则已含 `git diff HEAD~1`，追加内容需合并进同一条规则，不是另起一条 |
| 3 P8 bump 判定指引 | ✅ | 纯 prompt 指引，不进 gate |
| 4 architect.md DEVIATION 分类 | ✅ | 补的是 T025 gate-opt 遗漏的文件 |
| 5 写跑分离澄清 | ✅ | 一段追加文字，无风险 |
| 6 verifier.md 证据优先级 | ✅ | 角色指引，不改变 gate 定义 |
| 7 compact 恢复环境验证 | ✅ | 可选步骤，无 env_state 时跳过 |

**唯一注意点**：动作 2 的 P8 转移规则改写。当前 L125 已是：
```
P8 --[每个声明的 package 的发布检查命令 exit 0 + git diff HEAD~1 --stat 确认各包 version bump + git diff HEAD~1 -- CHANGELOG.md 非空]--> READY
```
追加后应为：
```
P8 --[每个声明的 package 的发布检查命令 exit 0 + bump-version 后重跑 P5 gate（gate_commands.P5 exit 0 AND failed==0）+ P8-release.md 含 bump_type: 字段 + git diff HEAD~1 --stat 确认各包 version bump + git diff HEAD~1 -- CHANGELOG.md 非空]--> READY
```
不是两条独立规则，是同一条规则的扩展。

---

## 动作 8 评审：check-gate.sh

### 问题 1：P3 路径不正确

计划写 `exec scripts/check-tdd-red.sh`。check-gate.sh 和 check-tdd-red.sh 都在 `scripts/` 目录下，但 `exec scripts/check-tdd-red.sh` 假设工作目录是 agate 根目录。如果主 Agent 在项目目录下运行 check-gate.sh，路径会解析失败。

**修正**：用 `dirname "$0"` 定位同目录脚本：
```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
P3)  exec "$SCRIPT_DIR/check-tdd-red.sh" ;;
```

### 问题 2：P4 只查最近一条 commit

`git log --oneline -1 | grep -qE 'P4|...'` 只看 HEAD~1。但 agate 的 P4 gate 通常在 P4 commit 之后还有 .state.yaml 更新 commit（步骤 7 写状态），所以最近的 commit 可能是 `.state.yaml` 更新而不是 P4。

**修正**：扩大搜索范围：
```bash
P4)  git log --oneline -5 | grep -qE 'P4|wf\(T[0-9]+-P4\)' && exit 0 || exit 1 ;;
```
查最近 5 条 commit 足够覆盖 P4 commit + .state.yaml 更新 + 可能的 retry commit。

### 问题 3：P6 缺 BDD 总数对照但计划标注了，这是正确的取舍

计划明确写了"BDD 总数对照不进脚本，由主 Agent 手动对照"，理由是 P1 BDD 编号格式不固定。这与 T025 v2 复核结论一致。

但有一个隐患：**如果主 Agent 只跑 `check-gate.sh P6` 看到 exit 0 就推进，跳过了步骤 5 的 BDD 总数对照，P6 的 BDD count 规则就形同虚设。** 这与之前评审发现的"Agent 会走阻力最小路径"是同一问题。

**修正**：check-gate.sh P6 的 stderr 输出加一行提醒：
```bash
echo "GATE P6: PASS（FAIL=0, NEED_CONFIRM=0）. 注意：BDD 总数对照需主 Agent 在步骤 5 手动验证" >&2
```
不是强制，但是一个"你还没做完"的提醒。

### 问题 4：`set -euo pipefail` 与 `|| echo 0` 冲突

计划中 P6/P7 用 `grep -cE ... 2>/dev/null || echo 0`。但 `set -e` 下，如果 grep 没匹配到任何行，`grep -c` 返回 exit 1，`set -e` 会终止脚本——`|| echo 0` 永远执行不到。

实际上 `grep -c` 在匹配数为 0 时返回 exit 1。在 `set -e` 下，`$(grep -cE ... || echo 0)` 里的 `|| echo 0` 会正确处理 exit 1——`||` 在子 shell 中覆盖 `set -e`。所以 `RESULT=$(grep -cE ... 2>/dev/null || echo 0)` 在 `set -e` 下是安全的：grep 返回 1 时 `|| echo 0` 生效，TOTAL/FAIL/NC 被赋值为 0。

但有一个更微妙的问题：如果文件不存在（P6-acceptance.md 还没产出），`grep -cE` 会报错且 `2>/dev/null` 抑制了错误信息。此时 `|| echo 0` 给出 TOTAL=0，而 `[ "$TOTAL" -gt 0 ]` 为 false → exit 1。行为正确——文件不存在 = gate 不通过。

**结论**：无 bug，但脚本的可读性差。建议加注释说明 `|| echo 0` 处理 grep exit 1 的情况。

### 问题 5：check-gate.sh 与 state-machine.md 步骤 5 的关系未声明

check-gate.sh 实现了步骤 5 中 P3/P4/P6/P7 的 grep 命令，但脚本和协议文件之间的权威关系未明确。如果步骤 5 的 grep 命令被修改（如 T022 动作 2 追加了 P8 的 bump 后重跑 P5），check-gate.sh 需要同步更新——但目前没有机制保证这一点。

**修正**：在 check-gate.sh 头部加声明：
```bash
# 本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
# 步骤 5 变更时必须同步更新本脚本。一致性检查脚本（check-protocol-consistency.py）覆盖本文件。
```

---

## 评审结论

| 类别 | 数量 | 详情 |
|------|------|------|
| Critical | 0 | — |
| Important | 2 | P3 路径修正、P4 commit 搜索范围扩大 |
| Minor | 3 | P6 提醒信息、脚本可读性注释、权威关系声明 |

**判定：可实施，但需在实施时修正 Important 项。**

动作 1-7 无重大问题，直接执行。动作 8 的 check-gate.sh 需在实施时修正：
1. P3 路径改用 `dirname "$0"` 定位
2. P4 改为 `git log --oneline -5`
3. P6 exit 0 时 stderr 加 BDD 总数对照提醒
4. 脚本头部加权威关系声明
