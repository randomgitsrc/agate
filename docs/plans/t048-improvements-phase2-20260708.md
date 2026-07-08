---
task_id: t048-improvements-phase2
agent: main
date: 2026-07-08
status: 设计方案 v2（评审后迭代）
来源: docs/plans/t048-improvements-20260708.md Phase 2 + 流程图分析 + 写跑分离讨论
---

# T048 改进 Phase 2：协议+脚本联动

## 前置条件

Phase 1（A+C）已实施并通过 self-gate：
- A1-A4: gate 脚本正则改为语义匹配 ✅
- C: provenance 证据数规则改为引用计数 ✅

## Phase 2 改进项

| # | 问题 | 来源 | 优先级 |
|---|------|------|--------|
| G | 写跑分离粒度修正 | 流程图分析 + 用户讨论 | 🔴 |
| B | dispatch-context 时序约束 | T048 复盘 §10.1 | 🔴 |
| D | subagent 假完成防护 | T048 复盘 §5.4 | 🟡 |
| E2 | 评审 agent=main 硬拦截 | T048 复盘 + 流程图评审缺口 | 🔴 |
| E3 | 非合法阶段代码暂存 WARNING | T048 复盘 | 🟡 |

---

## G. 写跑分离粒度修正

### 问题

当前写跑分离规则（P4/P6 prompt 模板）一刀切："只写脚本不跑"。

**实际执行中的矛盾**：
- P4 implementer 写完代码后不自跑 = 交付未验证代码
- T048 实际执行中 implementer 自跑 pytest 确认通过才返回——写跑分离未被遵守
- P6 verifier 写验证脚本后不自跑 = 不知道脚本语法是否正确

**正确区分**：

| 行为 | 当前规则 | 应改为 |
|------|---------|--------|
| implementer 写代码后自跑确认基本功能 | ❌ 禁止 | ✅ 允许（自查） |
| implementer 自跑后声称"P5 gate 已过" | 未明确禁止 | ❌ 禁止（P5 是主 Agent 职责） |
| verifier 写验证脚本后自跑确认语法正确 | ❌ 禁止 | ✅ 允许（自查） |
| verifier 自跑后声称"P6 验收通过" | 未明确禁止 | ❌ 禁止（P6 gate 是主 Agent 跑的） |
| 主 Agent 跑 implementer/verifier 交付的脚本 | ✅ 允许 | ✅ 保持不变 |

### 方案

#### G1. 重命名："写跑分离" → "自查≠gate"

"写跑分离"这个名字暗示"写和跑是两个人"，但实际上写的人可以自查，只是自查结论不等于 gate 结论。

新名称更准确：subagent 可以自跑自查，但自查结果 **不等于 gate 结论**。gate 由主 Agent 亲自执行。

**P5 不受影响**：P5 由主 Agent 亲自跑 gate_commands，不派 subagent，不存在"写跑分离"问题。

**注意两个层面的区分**：
- G 的"自查"= 确认功能正确（subagent 自跑测试/验证脚本）
- D 的"自检"= 确认文件写入（subagent grep 确认改动落盘）
两者不冲突：G 管功能验证，D 管写入确认。

#### G2. 修改 prompt 模板

**P4 追加**（`dispatch-protocol.md:382-383` + `phase-cards/P4-implementation.md:42-43` + `assets/templates/dispatch-prompt.md:87` + `assets/execution-roles/implementer.md:45`）：

```
## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 亲自执行 P2-design.md 的 gate_commands，结果以主 Agent 为准。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。
```

**P6 追加**（`dispatch-protocol.md:413-414` + `assets/templates/dispatch-prompt.md:122` + `assets/execution-roles/verifier.md:46` + `assets/execution-roles/verifier.md:134`）：

```
## 自查≠gate
写完验证脚本后应自跑确认脚本可执行（自查），但自查通过 ≠ P6 gate 通过。
P6 gate 由主 Agent 亲自执行验收检查，结果以主 Agent 为准。
不要在返回中声称"验收已通过"或"全部 BDD PASS"——只返回路径 + 摘要。
```

#### G3. 更新 dispatch-protocol.md 解释段落

`dispatch-protocol.md:568` 当前解释：

> 写跑分离让 subagent 写、主 Agent 跑，各司其职。

改为：

> 自查≠gate：subagent 可以自跑自查确认基本功能，但自查结论不等于 gate 结论。gate 由主 Agent 亲自执行，结果以主 Agent 为准。这防止 subagent 的"假完成"被当作 gate 通过。

### 覆盖边界

- ✅ implementer 自跑 pytest 确认代码可用 → 允许
- ✅ verifier 自跑验证脚本确认语法正确 → 允许
- ❌ implementer 返回"P5 gate 通过" → 违规
- ❌ verifier 返回"P6 验收通过" → 违规
- ❌ 主 Agent 用 subagent 的自查结论替代 gate → 违规

### 测试

1 个 bats 测试：dispatch-prompt.md 含"自查≠gate"关键词（防 drift，与 D1 同测）。

---

## B. dispatch-context 时序约束

### 问题

dispatch-context.md 事后补写，hash 校验形同虚设。多次派发时一篇 dispatch-context 无法覆盖。

### 方案

#### B1. 协议层：明确"先写再派"时序

在 `dispatch-protocol.md` 的"客观信息落盘"节增加时序约束（硬规则）：

```
时序约束：
- dispatch-context.md 必须在派发 subagent 之前写入
- 派发 prompt 引用此文件路径 → subagent 读取 → 上下文注入生效
- 事后补写 = 违规（hook 无法完全检测时序，但见 B3 弱检测）
```

#### B2. 多次派发：dispatch-context 定位为"阶段级共享上下文"

dispatch-context.md 记录本阶段所有派发共享的客观信息。每次派发的差异部分（如"评审修订后重派"）写在 prompt 里。

理由：
- dispatch-context 的设计意图是"主 Agent 已查证的客观信息"（环境/URL/选择器），同阶段多次派发间通常不变
- 每次派发的差异是任务描述，属于 prompt 内容
- 文件数不膨胀，hook 逻辑不变

#### B3. hook 层：弱检测（WARNING）

在 `pre-commit-gate.sh` 中，如果产出文件被暂存但 dispatch-context.md 不存在（不在暂存区也不在 HEAD），发出 WARNING：

```bash
STAGED_OUTPUT_IN_TASK=$(git diff --cached --name-only 2>/dev/null \
    | grep -E "^${TASK_REL}/P[0-8]-.*\.md$" || true)
if [ -n "$STAGED_OUTPUT_IN_TASK" ]; then
    DC_FILE="$TASK_DIR/${PHASE}-dispatch-context.md"
    if [ ! -f "$DC_FILE" ] && ! git show "HEAD:${TASK_REL}/${PHASE}-dispatch-context.md" >/dev/null 2>&1; then
        echo "GATE WARNING: ${PHASE} 产出已暂存但 ${PHASE}-dispatch-context.md 不存在——是否忘记先写 dispatch-context？" >&2
    fi
fi
```

覆盖：
- ✅ 首次 commit 产出时 dispatch-context 不存在 → WARNING
- ✅ dispatch-context 在之前 commit 已提交 → 不警告
- ✅ dispatch-context 和产出同次 commit → 不警告
- ❌ dispatch-context 事后补写且同次 commit → 无法检测

### 测试

1 个 bats 测试：P2 产出暂存但无 dispatch-context → WARNING 输出。

---

## D. subagent 假完成防护

### 问题

subagent 返回"已修复"但文件未实际变更。根因是"只返回摘要"指令可能被理解为"不需实际执行"。

### 方案

#### D1. 派发 prompt 增加返回前自检

在 `assets/templates/dispatch-prompt.md` 的"返回给我"节追加：

```
## 返回前自检（强制）
如果任务涉及修改/创建文件，返回前必须：
  1. 用 bash 执行 grep/rg 确认改动已落盘（如：grep "新增函数名" 目标文件）
  2. 如果 grep 未匹配 → 文件未写入成功 → 重新写入后再返回
  3. 不要在未确认落盘的情况下返回"已完成"
```

#### D2. 主 Agent 校验第 6 条

在 `dispatch-protocol.md` 的"subagent 返回校验"节增加：

```
6. 修改类任务的文件内容校验：
   subagent 返回"已修复/已实现"后，主 Agent 对声称修改的文件做最小验证：
   - 用 bash 执行 grep 确认新增/修改的代码行存在
   - 如果声称修改但文件内容未变 → 视为假完成，重派
   - 这不是"主 Agent 改代码"——主 Agent 只读验证，不写文件
```

### 测试

1 个 bats 测试：dispatch-prompt.md 含"返回前自检"关键词（防 drift）。

---

## E2. 评审 agent=main 硬拦截

### 问题

当前 `check-p6-provenance.sh` 对 `risk=high + agent=main` 只输出 WARNING（exit 2）。主 Agent 可以自行批准评审（T048 P2 违规）。

### 方案

将评审文件 `status=approved + agent=main` 从 WARNING 升级为硬拦截（exit 1），并扩展到所有评审文件（不只是 P2）。

**有意变更**：移除 `risk=high` 前置条件。任何阶段的评审 self-approved（agent=main + status:approved）都应拦截，不限于 high risk。理由：低风险任务的 self-review 同样不可信——T048 的 P2 违规任务 risk=medium。

在 `check-p6-provenance.sh` 协作规范节，替换现有的 P2-review WARNING 逻辑为全评审硬拦截：

```bash
for review_file in "$TASK_DIR"/P[0-8]-review.md; do
    [ -f "$review_file" ] || continue
    AGENT=$(get_agent "$review_file")
    if grep -qE 'status:\s*approved' "$review_file" 2>/dev/null; then
        if [ -z "$AGENT" ]; then
            echo "GATE PROVENANCE: $(basename "$review_file") status=approved 但缺 agent 字段（向后兼容 WARNING）" >&2
        elif [ "$AGENT" = "main" ]; then
            echo "GATE PROVENANCE: $(basename "$review_file") status=approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
            exit 1
        fi
    fi
done
```

覆盖：
- ✅ subagent 评审 approved → agent ≠ main → 通过
- ✅ 主 Agent 擅改 approved → agent = main → 拦截（exit 1）
- ✅ 旧文件缺 agent 字段 + approved → WARNING（exit 2，向后兼容）
- ❌ 主 Agent 同时改 agent 字段 → 绕过（蓄意伪造，超出脚本防线）

现有 PV.15 测试需从 exit 2 改为 exit 1，并新增两个测试：
- PV.16：agent=subagent + status=approved → exit 0
- PV.17：缺 agent 字段 + status=approved → exit 2（WARNING）

### 测试

- PV.15 改为期望 exit 1
- 新增 PV.16：agent=subagent + status=approved → exit 0
- 新增 PV.17：缺 agent 字段 + status=approved → exit 2（WARNING）

---

## E3. 非合法阶段代码暂存 WARNING

### 问题

主 Agent 可能在非 P4/P5/P6 阶段直接改代码，当前无检测。

### 方案

在 `pre-commit-gate.sh` 的 2n 节（P6 证据检查）之后、2o 节（gate 结果处理）之前增加 WARNING（与 B3 同一插入点）：

```bash
CODE_FILES=$(git diff --cached --name-only 2>/dev/null | grep -vE '\.(md|yaml)$|^\.state')
if [ -n "$CODE_FILES" ]; then
    case "$PHASE" in
        P4|P5|P6) ;;
        *)
            echo "GATE WARNING: phase=$PHASE 但暂存了代码文件——主 Agent 是否在非实现阶段直接改代码？" >&2
            ;;
    esac
fi
```

覆盖：
- ✅ P4 阶段暂存代码 → 不警告
- ✅ P2 阶段暂存代码 → 警告
- ✅ P6 验收脚本 → P6 在放行列表
- ❌ P4 阶段主 Agent 自己改代码 → 无法区分

### 测试

1 个 bats 测试：P2 阶段暂存 .py → WARNING 输出。

---

## 实施顺序

```
G. 写跑分离粒度修正（纯文档，无脚本依赖）
   → 改 6 个文件的 prompt 文本

B. dispatch-context 时序约束（B1 协议 + B3 WARNING）
   → 改 dispatch-protocol.md + pre-commit-gate.sh

D. subagent 假完成防护（D1 prompt + D2 协议）
   → 改 dispatch-prompt.md + dispatch-protocol.md

E2. 评审 agent=main 硬拦截
   → 改 check-p6-provenance.sh + 测试

E3. 非合法阶段代码暂存 WARNING
   → 改 pre-commit-gate.sh + 测试
```

G/B/D 是文档为主，E2/E3 是脚本为主。各 item 无依赖，可并行。

---

## 风险

| 风险 | 缓解 |
|------|------|
| G 重命名后旧 prompt 文本残留 | grep 扫描确认所有"写跑分离"已替换 |
| E2 旧评审文件缺 agent 字段被误拦截 | 缺字段时 exit 2 WARNING（向后兼容，不阻塞） |
| E2 主 Agent 伪造 agent 字段绕过 | provenance 审计可标记；蓄意伪造超出脚本防线 |
| E3 P6 验收脚本被误判为代码文件 | P6 在放行列表 |
| B3 dispatch-context WARNING 误报（产出和 context 同次 commit） | 同次 commit 不警告 |

---

## 不在本次范围内

- **P1 评审缺口**：需定义 C8 评审角色 + hook 化，是独立 feature
- **P4 评审 hook 化**：check-gate.sh P4 检查 P4-review.md，需设计"评审触发条件"语义
- **P6/P7 self-authored 根治**：需平台支持独立 git author
- **Phase 3（F 上下文缓解）**：依赖 E2/E3 就位

---

## v1→v2 评审变更记录

| # | v1 问题 | v2 修正 |
|---|--------|--------|
| 1 | G 未说明 P5 不受影响 | G1 补充：P5 无 subagent，不存在写跑分离问题 |
| 2 | G 未区分"自查"（功能验证）和"自检"（写入确认） | G1 补充：G 管功能验证，D 管写入确认，不冲突 |
| 3 | E2 保留 risk=high 前置条件，但 intention 是拦截所有 self-review | E2 明确：移除 risk=high 前置条件，任何阶段 self-approved 都拦截 |
| 4 | E2 缺 agent 字段时静默放行（`[ "" = "main" ]` = false） | E2 补充：缺字段时 exit 2 WARNING，不静默放行 |
| 5 | E2 只加 PV.16 一个新测试 | E2 加 PV.16（agent=subagent）+ PV.17（缺字段）两个新测试 |
| 6 | B3/E3 未说明 pre-commit-gate.sh 插入位置 | B3/E3 补充：2n 节之后、2o 节之前 |
