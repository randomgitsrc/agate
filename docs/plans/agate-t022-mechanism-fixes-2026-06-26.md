---
type: plan
source: docs/reviews/agate-mechanism-improvements-T022-2026-06-26.md
trace_id: agate-t022-mechanism-fixes-2026-06-26
created: 2026-06-26
status: 已落地
remark: 动作 1 的 state-machine/dispatch-protocol 部分由 T025 gate-opt 顺带落地，动作 4 的 state-machine 部分由 T025 gate-opt 顺带落地，其余 5 项 + check-gate.sh 由 T022 债务清还批次落地（2026-06-28）
---

# 修复方案：T022 机制改进落地

> 来源：`docs/reviews/agate-mechanism-improvements-T022-2026-06-26.md`（8 项改进建议）
> 裁决原则：gate 必须机器可判定；不可判定的改进降级为 prompt 指引或角色定义，不进 gate 条件。

## 裁决总览

| # | 评审建议 | 裁决 | 理由 |
|---|---------|------|------|
| 2 | P6 BDD 总数对照 | ✅ 修 | 最有价值的改进。BDD 条数 grep + 比对，完全机器可判定 |
| 4 | bump 后重跑 P5 gate | ✅ 修 | 简单可判定（跑 gate 命令 exit 0），直接加进 P8 转移规则 |
| 3 | 版本 bump 类型判定 | ✅ 修（降级为 prompt 指引）| bump 规则表是好的指引，但"选择是否正确"不可 gate。落地为 P8 派发追加节 + 要求显式声明 |
| 7 | DEVIATION 升级 BLOCKER | ✅ 修 | `[DEVIATION-CRITICAL]` 标签 + grep gate 可判定。分类标准写进 architect.md |
| 5 | 写跑分离三阶段 | ✅ 修（简化）| 加一句"主 Agent 跑最小 inspect 脚本属于查证职责"，不做完整三阶段 |
| 6 | 证据优先级 DOM > vision | ✅ 修（拆分）| 证据优先级概念写进 verifier.md 角色指引。P6 gate 仍保持 blocker_count==0 二值，不改 gate 定义 |
| 8 | compact 恢复环境验证 | ✅ 修（抽象化）| 落地为通用原则"恢复后验证 .state.yaml 环境状态字段"，不硬编码 curl 命令 |
| 1 | P4 子目标覆盖度 | ❌ 拒绝 | 不可机器判定（语义提取子目标）。#2 已覆盖同一失败链路（P6 BDD count 拦截） |

## 落地动作

### 动作 1：P6 gate 增加 BDD 总数对照（#2）

**文件**：`state-machine.md` P6 转移规则 + `dispatch-protocol.md` 可判定门槛表 + P6 派发追加节

**改法**：

state-machine.md P6 转移规则：
```yaml
P6 --[
  P6-acceptance.md 有效 AND
  P1 的每条 BDD 条件标记为 PASS 或 FAIL（二值）AND
  P1 的 BDD 总数 == P6-acceptance.md 的验收条数 AND  # 新增
  无 FAIL 条件 AND
  无未决 NEED_CONFIRM
]--> P7
```

dispatch-protocol.md 门槛表 P6→P7 行追加：
```
P1 BDD 总数 == P6 验收条数（grep 统计，含 SCOPE+ 增补的 BDD）
```

dispatch-prompt.md P5/P6 派发追加节追加：
```
## P6 BDD 覆盖完整性
P6 验收必须全量对照 P1 的 BDD 条数（含 SCOPE+ 增补），不能挑验。
P1 有 N 条 BDD → P6 必须有 N 条验收结果（PASS 或 FAIL）。挑验 = gate 不通过。
```

**SCOPE+ 增补处理**：BDD 总数 = P1-requirements.md 当前所有 BDD 条件（含 `[SCOPE+ from Pn]` 标记的增补条目）。主 Agent grep `^\*\*Given\|^- AC\|Given.*When.*Then` 统计。

**验证**：`grep -cE '^\s*- (PASS|FAIL)' P6-acceptance.md` == `grep -cE '^\s*-?\s*AC\d+.*Given.*When.*Then' P1-requirements.md`（锚定行首 `- PASS` / `- FAIL`，避免匹配说明性文本）

### 动作 2：P8 gate 增加 bump 后重跑 P5（#4）

**文件**：`state-machine.md` P8 转移规则 + `dispatch-protocol.md` 门槛表

**改法**：

state-machine.md P8 转移规则：
```yaml
P8 --[
  bump-version 后重跑 P5 gate（gate_commands.P5 exit 0 AND failed==0）AND  # 新增
  每个声明的 package 的发布检查命令 exit 0 AND
  git diff 确认各包 version bump AND
  P8-release.md 含 bump_type: 字段（grep -q 'bump_type:' P8-release.md）AND  # 新增
  CHANGELOG 已更新
]--> READY
```

dispatch-protocol.md 门槛表 P8→READY 行追加：
```
bump 后重跑 P5 gate（版本号变化可能影响版本敏感的测试）AND P8-release.md 含 bump_type: 字段
```

**理由**：版本号是全局变量，bump 前的 P5 通过不保证 bump 后仍通过。

### 动作 3：P8 bump 判定指引（#3，降级为 prompt 指引）

**文件**：`dispatch-protocol.md` P8 派发追加节 + `dispatch-prompt.md` P8 派发追加

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

**gate 可判定部分**：P8-release.md 必须含 `bump_type:` 字段（`grep -q 'bump_type:' P8-release.md`）。接入 P8 gate（见动作 2 的转移规则）。"选择是否正确"是语义判断，不进 gate。

### 动作 4：P7 增加 DEVIATION-CRITICAL（#7）

**文件**：`state-machine.md` P7 转移规则 + `architect.md` P7 输出规范

**改法**：

state-machine.md P7 转移规则：
```yaml
P7 --[
  ! grep -qE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md AND
  ! grep -qE '^\s*-?\s*\[DEVIATION-CRITICAL\]' P7-consistency.md  # 新增
]--> P8
```

architect.md P7 输出规范追加：
```markdown
## DEVIATION 分类

DEVIATION 标注必须注明"涉及 P2 哪个设计目标"：
- DEVIATION 涉及 P2 核心设计目标且实现完全未落地 → 标 `[DEVIATION-CRITICAL]`（升级为 BLOCKER，gate 不通过）
- DEVIATION 涉及 P2 核心设计目标但已部分落地 → 标 `[DEVIATION]` + `[NEED_CONFIRM]`（不硬阻塞，但需人工确认是否可接受）
- DEVIATION 涉及命名风格/行数预算等非核心 → 标 `[DEVIATION]`（保持，不阻塞）

判定"核心设计目标"的依据：P2-design.md 的改动方案节（§1）中明确列出的设计目标，被 P1 BDD 引用为验收条件的，为核心设计目标。
```

### 动作 5：写跑分离澄清（#5，简化）

**文件**：`dispatch-protocol.md`「写脚本与跑脚本分离」节

**改法**：在现有节末尾追加一段：

```markdown
### 主 Agent 的"inspect DOM"属于查证职责

主 Agent 可以跑最小 inspect 脚本（如 `page.evaluate(() => document.querySelector('#root').innerHTML.length)`）来查证 DOM 结构——这是查证客观信息（写 dispatch-context.md 的选择器清单），不属于"写脚本"或"降级"。查证产出落盘到 dispatch-context.md，派发时传路径。

区分：
- 主 Agent 跑 inspect 脚本（只查 DOM 结构、不做断言）= 查证职责 ✅
- 主 Agent 写验收脚本（含断言逻辑）= 降级 ❌
```

### 动作 6：证据优先级写进 verifier.md（#6，拆分）

**文件**：`assets/execution-roles/verifier.md` P6 模式

**改法**：在 P6 模式的认知模式节追加：

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

### 动作 7：compact 恢复环境验证（#8，抽象化）

**文件**：`state-machine.md`「主 Agent 的单步执行（一轮）」节（单步函数步骤 1 之后）

**改法**：在单步函数步骤 1（读 .state.yaml / active-tasks.md）之后、步骤 2 之前，加步骤 1.5：

```markdown
1.5 环境一致性验证（若 .state.yaml 含 env_state 字段）

   若 .state.yaml 含 `env_state:` 块（运行时环境状态，如 debug backend URL、test entry ID、端口等）：
   - 验证这些状态在当前环境中仍有效（具体检查方式由项目自定，如 curl health check、查询 entry 是否存在）
   - 若任一失效：重新创建对应资源，更新 .state.yaml 的 env_state，commit 修订
   - 若环境全部失效 → PAUSED 报告人工

   注意：此步骤只适用于 .state.yaml 显式记录了 env_state 的任务。
   无 env_state 的任务跳过此步骤。
```

**.state.yaml 模板补充**（state-machine.md「每任务独立状态文件」节的 YAML 模板）：
```yaml
# 可选：运行时环境状态（P6 等需要运行环境的阶段记录）
env_state:
  debug_backend: "http://127.0.0.1:8888"
  test_entry_slug: "zg71s7"
  env_verified_at: "2026-06-26T03:25:00"
```

**不硬编码**：具体检查命令（curl、health endpoint 等）由项目自定。agate 只给出原则"恢复后验证环境状态仍有效"。

## 不落地项

| # | 评审建议 | 不落地理由 |
|---|---------|-----------|
| 1 | P4 子目标覆盖度检查 | "提取子目标清单"是语义判断，不可机器判定。#2（P6 BDD count）已覆盖同一失败链路——P6 拒绝通过时回退到 P4，代价可控。加一道 fuzzy gate 增加主 Agent 负担，违反 gate 可判定原则 |

## 同步点（落地时勿遗漏）

state-machine.md「主 Agent 的单步执行（一轮）」节步骤 5 的 per-phase gate 清单需同步更新：
- P6 行追加：`P1 BDD 总数 == P6 验收条数`
- P7 行追加：`! grep -qE '^\s*-?\s*\[DEVIATION-CRITICAL\]' P7-consistency.md`
- P8 行追加：`bump 后重跑 P5 gate` + `P8-release.md 含 bump_type: 字段`

## 落地清单

| # | 动作 | 文件 | 优先级 | 工作量 |
|---|------|------|--------|--------|
| 1 | P6 BDD 总数对照 | state-machine.md + dispatch-protocol.md + dispatch-prompt.md | 🔴 高 | 10 分钟 |
| 2 | P8 bump 后重跑 P5 | state-machine.md + dispatch-protocol.md | 🔴 高 | 5 分钟 |
| 3 | P8 bump 判定指引 | dispatch-prompt.md + dispatch-protocol.md | 🟠 中 | 5 分钟 |
| 4 | P7 DEVIATION-CRITICAL | state-machine.md + architect.md | 🟠 中 | 8 分钟 |
| 5 | 写跑分离澄清 | dispatch-protocol.md | 🟡 低 | 3 分钟 |
| 6 | 证据优先级 | verifier.md | 🟡 低 | 5 分钟 |
| 7 | compact 恢复环境验证 | state-machine.md | 🟡 低 | 5 分钟 |

**总计**：7 项动作，约 41 分钟。
