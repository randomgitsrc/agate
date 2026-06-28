---
type: plan
source: docs/reviews/agate-状态评估与后续建议-20260628.md
trace_id: agate-t022-debt-paydown-2026-06-28
created: 2026-06-28
status: 待执行
---

# T022 债务清还 + check-gate.sh 落地

> 来源：`docs/reviews/agate-状态评估与后续建议-20260628.md` §二/§四
> T022 plan（`docs/plans/agate-t022-mechanism-fixes-2026-06-26.md`）7 项动作中，2 项已由 T025 gate-opt 顺带落地（动作 1 的 state-machine/dispatch-protocol 部分、动作 4 的 state-machine 部分），5 项完全未动，2 项半落地各缺一个文件。
> 本计划补全剩余债务，并新增 check-gate.sh（状态评估 P-2 建议）。

---

## 债务清单与当前状态

| # | T022 动作 | 当前状态 | 本计划动作 |
|---|----------|---------|-----------|
| 1 | P6 BDD 总数对照 | state-machine ✅ dispatch-protocol ✅ **dispatch-prompt ❌** | 动作 1：补 dispatch-prompt |
| 2 | P8 bump 后重跑 P5 + bump_type 字段 | **完全未落地** | 动作 2：落地 |
| 3 | P8 bump 判定指引 | **完全未落地** | 动作 3：落地 |
| 4 | P7 DEVIATION-CRITICAL 分类标准 | state-machine ✅ **architect.md ❌** | 动作 4：补 architect.md |
| 5 | 写跑分离澄清 | **完全未落地** | 动作 5：落地 |
| 6 | verifier.md 证据优先级 | **完全未落地** | 动作 6：落地 |
| 7 | compact 恢复环境验证 | **完全未落地** | 动作 7：落地 |
| — | check-gate.sh | 不存在 | 动作 8：新增 |

---

## 落地动作

### 动作 1：补 dispatch-prompt.md P6 BDD 覆盖完整性

**文件**：`assets/templates/dispatch-prompt.md`

**改法**：在 P5/P6 派发追加节（L84-92）的 `## P6 BDD 二值规则` 之后追加：

```
## P6 BDD 覆盖完整性
P6 验收必须全量对照 P1 的 BDD 条数（含 SCOPE+ 增补），不能挑验。
P1 有 N 条 BDD → P6 必须有 N 条验收结果（PASS 或 FAIL）。挑验 = gate 不通过。
```

同时在 `dispatch-protocol.md` 阶段特定提示 P5/P6 派发时追加节（L358 附近）同步追加同内容。

### 动作 2：P8 bump 后重跑 P5 + bump_type 字段

**文件**：`state-machine.md` P8 转移规则 + `dispatch-protocol.md` 门槛表

**改法**：

state-machine.md P8 转移规则（当前 L125）追加 bump 后重跑 P5 + bump_type 字段：
```
P8 --[每个声明的 package 的发布检查命令 exit 0 + bump-version 后重跑 P5 gate（gate_commands.P5 exit 0 AND failed==0）+ P8-release.md 含 bump_type: 字段 + git diff HEAD~1 --stat 确认各包 version bump + git diff HEAD~1 -- CHANGELOG.md 非空]--> READY
```

dispatch-protocol.md 门槛表 P8→READY 行追加：
```
bump 后重跑 P5 gate（版本号变化可能影响版本敏感的测试）AND P8-release.md 含 bump_type: 字段
```

state-machine.md 步骤 5 P8 行追加：
```
从 P2-design.md gate_commands.P5 重跑 P5 命令 → exit 0 AND failed==0;
grep -q 'bump_type:' {task}/P8-release.md → 命中
```

### 动作 3：P8 bump 判定指引

**文件**：`assets/templates/dispatch-prompt.md` + `dispatch-protocol.md`

**改法**：

dispatch-prompt.md P8 派发追加节追加：
```
## 版本 bump 判定
- 公共 API 行为变化 / 破坏性变更 → major
- 加功能 / 内部重构改 API（向后兼容）→ minor
- 修 bug / 不改 API 行为 → patch
- 测试缺陷不应影响版本号决策：测试 hard-code 版本号 → 修测试，不降级版本
- 在 P8-release.md 中显式声明：bump 类型（major/minor/patch）+ 理由
```

dispatch-protocol.md P8 派发时追加节追加同内容。

### 动作 4：补 architect.md DEVIATION 分类定义

**文件**：`assets/execution-roles/architect.md`

**改法**：在 P7 输出规范（L80 附近，`方向 1/方向 2` 之后）追加：

```markdown
### DEVIATION 分类

DEVIATION 标注必须注明"涉及 P2 哪个设计目标"：
- DEVIATION 涉及 P2 核心设计目标且实现完全未落地 → 标 `[DEVIATION-CRITICAL]`（升级为 BLOCKER，gate 不通过）
- DEVIATION 涉及 P2 核心设计目标但已部分落地 → 标 `[DEVIATION]` + `[NEED_CONFIRM]`（不硬阻塞，但需人工确认是否可接受）
- DEVIATION 涉及命名风格/行数预算等非核心 → 标 `[DEVIATION]`（保持，不阻塞）

判定"核心设计目标"的依据：P2-design.md 的改动方案节（§1）中明确列出的设计目标，被 P1 BDD 引用为验收条件的，为核心设计目标。
```

### 动作 5：写跑分离澄清

**文件**：`dispatch-protocol.md`「写脚本与跑脚本分离」节

**改法**：在 L477（T020 教训段）之后追加：

```markdown
### 主 Agent 的"inspect DOM"属于查证职责

主 Agent 可以跑最小 inspect 脚本（如 `page.evaluate(() => document.querySelector('#root').innerHTML.length)`）来查证 DOM 结构——这是查证客观信息（写 dispatch-context.md 的选择器清单），不属于"写脚本"或"降级"。查证产出落盘到 dispatch-context.md，派发时传路径。

区分：
- 主 Agent 跑 inspect 脚本（只查 DOM 结构、不做断言）= 查证职责 ✅
- 主 Agent 写验收脚本（含断言逻辑）= 降级 ❌
```

### 动作 6：verifier.md 证据优先级

**文件**：`assets/execution-roles/verifier.md`

**改法**：在 P6 模式的认知模式节（L61-65 之后）追加：

```markdown
### 行为验证证据优先级（高→低）

1. **DOM 结构验证**（最可靠）：innerHTML 长度、元素存在性、class 状态
2. **交互响应验证**（可靠）：点击后 class 变化、modal 出现/消失、URL 跳转
3. **vision-analyst 视觉分析**（辅助证据）：可被 1/2 覆盖

当 vision-analyst 报 blocker 但 DOM 验证 PASS 时：
1. 派第二轮截图（换主题/换时机/换 viewport）
2. vision-analyst 重新分析
3. 第二轮 blocker_count == 0 → gate 通过
4. 第二轮仍 blocker_count > 0 → 标 [NEED_CONFIRM] 交人判断
5. 在 P6-acceptance.md 中记录仲裁过程

**注意**：P6 gate 仍保持 `blocker_count == 0` 二值判定。证据优先级是 verifier 的工作方法指引，不改变 gate 定义。
```

### 动作 7：compact 恢复环境验证

**文件**：`state-machine.md`

**改法**：

1. 在单步函数步骤 1（读 .state.yaml / active-tasks.md）之后、步骤 2 之前，加步骤 1.5：

```markdown
1.5 环境一致性验证（若 .state.yaml 含 env_state 字段）

   若 .state.yaml 含 `env_state:` 块（运行时环境状态，如 debug backend URL、test entry ID、端口等）：
   - 验证这些状态在当前环境中仍有效（具体检查方式由项目自定，如 curl health check、查询 entry 是否存在）
   - 若任一失效：重新创建对应资源，更新 .state.yaml 的 env_state，commit 修订
   - 若环境全部失效 → PAUSED 报告人工

   注意：此步骤只适用于 .state.yaml 显式记录了 env_state 的任务。
   无 env_state 的任务跳过此步骤。
```

2. 在「每任务独立状态文件」节的 YAML 模板（L340 附近）追加可选 env_state 块：

```yaml
# 可选：运行时环境状态（P6 等需要运行环境的阶段记录）
env_state:
  debug_backend: "http://127.0.0.1:8888"
  test_entry_slug: "zg71s7"
  env_verified_at: "2026-06-26T03:25:00"
```

### 动作 8：新增 check-gate.sh

**文件**：`scripts/check-gate.sh`

**定位**：把 P3/P4/P6/P7 的 gate 判定脚本化，主 Agent 只看 `check-gate.sh P6 Txxx` 的 exit 0/1。P1/P2/P5/P8 含动态 gate_commands 或语义判断，脚本返回 exit 2 让主 Agent 自判。

**内容**：

```bash
#!/usr/bin/env bash
# check-gate.sh PHASE TASK_DIR
# exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）
#
# 可脚本化的 gate（exit 0/1）：P3 / P4 / P6 / P7
# 需动态读取 P2 gate_commands 的 gate（exit 2）：P2 / P5 / P8
# 含语义判断的 gate（exit 2）：P1（BDD 格式不固定）
#
# 本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
# 步骤 5 变更时必须同步更新本脚本。一致性检查脚本覆盖本文件。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHASE="${1:?用法: check-gate.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: check-gate.sh PHASE TASK_DIR}"

case "$PHASE" in
  P1)
      echo "GATE P1: BDD 编号格式不固定，需主 Agent 自行判定" >&2
      exit 2 ;;
  P2)
      echo "GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P3)
      exec "$SCRIPT_DIR/check-tdd-red.sh" ;;
  P4)
      # 查最近 5 条 commit（P4 commit 后可能有 .state.yaml 更新 commit）
      git log --oneline -5 | grep -qE 'P4|wf\(T[0-9]+-P4\)' && exit 0 || exit 1 ;;
  P5)
      echo "GATE P5: 需从 P2-design.md gate_commands.P5 动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  P6)
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      TOTAL=$(grep -cE '^\s*- (PASS|FAIL)' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      FAIL=$(grep -cE '^\s*- FAIL\b' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      NC=$(grep -cE '\[NEED_CONFIRM\]' "$TASK_DIR/P6-acceptance.md" 2>/dev/null || echo 0)
      if [ "$FAIL" -eq 0 ] && [ "$NC" -eq 0 ] && [ "$TOTAL" -gt 0 ]; then
          echo "GATE P6: PASS. 注意：BDD 总数对照需主 Agent 在步骤 5 手动验证" >&2
          exit 0
      else
          echo "GATE P6: FAIL=$FAIL, NEED_CONFIRM=$NC, TOTAL=$TOTAL" >&2
          exit 1
      fi ;;
  P7)
      # grep -c 无匹配时返回 exit 1，|| echo 0 处理此情况
      BLOCKERS=$(grep -cE '^\s*-?\s*\[BLOCKER\]' "$TASK_DIR/P7-consistency.md" 2>/dev/null || echo 0)
      DEVCRIT=$(grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' "$TASK_DIR/P7-consistency.md" 2>/dev/null || echo 0)
      if [ "$BLOCKERS" -eq 0 ] && [ "$DEVCRIT" -eq 0 ]; then
          exit 0
      else
          echo "GATE P7: BLOCKER=$BLOCKERS, DEVIATION-CRITICAL=$DEVCRIT" >&2
          exit 1
      fi ;;
  P8)
      echo "GATE P8: 需从 P2-design.md gate_commands 逐包动态读取，主 Agent 自行判定" >&2
      exit 2 ;;
  *)
      echo "未知阶段: $PHASE" >&2
      exit 2 ;;
esac
```

**P6 的 BDD 总数对照**：check-gate.sh P6 只检查 FAIL=0 AND NEED_CONFIRM=0 AND TOTAL>0。BDD 总数对照（P6 验收条数 == P1 BDD 总数）需要读 P1-requirements.md，而 P1 的 BDD 编号格式不固定（T025 v2 复核结论），脚本无法可靠统计 P1 BDD 总数。此项由主 Agent 在步骤 5 手动对照。

---

## 落地清单

| # | 动作 | 文件 | 工作量 |
|---|------|------|--------|
| 1 | dispatch-prompt 补 P6 BDD 覆盖完整性 | assets/templates/dispatch-prompt.md + dispatch-protocol.md | 3 分钟 |
| 2 | P8 bump 后重跑 P5 + bump_type | state-machine.md + dispatch-protocol.md | 5 分钟 |
| 3 | P8 bump 判定指引 | assets/templates/dispatch-prompt.md + dispatch-protocol.md | 5 分钟 |
| 4 | architect.md DEVIATION 分类 | assets/execution-roles/architect.md | 5 分钟 |
| 5 | 写跑分离澄清 | dispatch-protocol.md | 3 分钟 |
| 6 | verifier.md 证据优先级 | assets/execution-roles/verifier.md | 5 分钟 |
| 7 | compact 恢复环境验证 | state-machine.md | 6 分钟 |
| 8 | check-gate.sh 新增 | scripts/check-gate.sh | 8 分钟 |

**总计**：8 项动作，约 40 分钟。

## 完成后

1. 把 T022 plan（`docs/plans/agate-t022-mechanism-fixes-2026-06-26.md`）的 `status` 改为 `已落地`，顶部加备注：「动作 1 的 state-machine/dispatch-protocol 部分由 T025 gate-opt 顺带落地，动作 4 的 state-machine 部分由 T025 gate-opt 顺带落地，其余 5 项 + check-gate.sh 由本批次落地」
2. 运行 `scripts/check-protocol-consistency.py` 确认 0 ERROR
