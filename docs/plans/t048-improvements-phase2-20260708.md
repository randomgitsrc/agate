---
task_id: t048-improvements-phase2
agent: main
date: 2026-07-08
status: 设计方案 v3（评审迭代：修复 E2 BLOCKER + B scope 错配 + D 结构化返回）
来源: docs/plans/t048-improvements-phase2-20260708.md v2 + docs/reviews/review-20260708-0903.md
---

# T048 改进 Phase 2：协议+脚本联动

## 前置条件

Phase 1（A+C）已实施并通过 self-gate ✅

## 诚实标注

Phase 2 是**增量加固，不是结构性修复**。5 项里真正触及主 Agent 侧防御空白（LIMITATIONS.md 局限 3）的只有 D2（主 Agent grep 校验，锚到外部可观测事实）和 E2（评审 agent=main 检查，但自报字段可绕过——抬高随手自批成本，挡不住蓄意伪造）。其余 3 项（G/B/D1）落在 subagent 侧 / honor-system。

强制力分级（防 L1 漂移测试被误读为行为强制）：

| 级别 | 含义 | 本方案中的项 |
|------|------|-------------|
| L0 指导 | 只写文档，靠自觉，机器不验证 | G1/B1/B2 |
| L1 漂移测试 | 只验证"规则文本还在"，不验证"规则被执行" | G 漂移测试 |
| L2 WARNING | exit 2，提醒不阻塞 | B3/E3/缺 agent 字段 |
| L3 硬拦截 | exit 1，唯一真正强制 | E2（⚠️ 自报字段可绕过） |
| L4 主 Agent 侧外部可观测 | 主 Agent 亲自跑命令，结果锚到磁盘 | D2 |

---

## Phase 2 改进项

| # | 问题 | 来源 | 优先级 | 强制力 |
|---|------|------|--------|--------|
| G | 写跑分离粒度修正 | 流程图分析 + 用户讨论 | 🔴 | L0+L1 |
| B | dispatch-context 缺失检测 | T048 复盘 §10.1（⚠️ scope 修正见下） | 🔴 | L0+L2 |
| D | subagent 假完成防护 | T048 复盘 §5.4 | 🟡 | L0+L4 |
| E2 | 评审 self-approved 检查 | T048 复盘 + 评审缺口 | 🔴 | L3 ⚠️ |
| E3 | 非合法阶段代码暂存 WARNING | T048 复盘 | 🟡 | L2 |

---

## G. 写跑分离粒度修正

### 问题

当前写跑分离规则一刀切"只写脚本不跑"，实际执行中 implementer 自跑 pytest 才返回（T048），规则名实不副。

### 方案

#### G1. 重命名"写跑分离" → "自查≠gate"

subagent 可以自跑自查确认基本功能，但自查结论 **不等于 gate 结论**。gate 由主 Agent 亲自执行。

P5 不受影响：P5 由主 Agent 亲自跑 gate_commands，不派 subagent。

G 的"自查"= 确认功能正确（subagent 自跑测试/验证脚本），D 的"自检"= 确认文件写入（subagent grep 确认改动落盘）。两者不冲突。

#### G2. 修改 prompt 文本（8 处）

替换所有"写跑分离"文本为"自查≠gate"，每个阶段版本不同：

| 文件 | 旧文本 | 新文本 |
|------|--------|--------|
| `phase-cards/P4-implementation.md:42-43` | 写跑分离：只写脚本不跑 | 自查≠gate：写完代码后应自跑测试确认基本功能，但自查≠P5 gate。不要声称"P5 已过" |
| `phase-cards/P6-acceptance.md` | 无（需新增） | 自查≠gate：写完验证脚本后应自跑确认语法正确，但自查≠P6 gate。不要声称"验收已通过" |
| `dispatch-protocol.md:382-383` | P4 写跑分离 | P4 自查≠gate（同上） |
| `dispatch-protocol.md:413-414` | P6 写跑分离 | P6 自查≠gate（同上） |
| `assets/templates/dispatch-prompt.md:87` | P4 写跑分离 | P4 自查≠gate |
| `assets/templates/dispatch-prompt.md:122` | P6 写跑分离 | P6 自查≠gate |
| `assets/execution-roles/implementer.md:45` | 写跑分离 | 自查≠gate |
| `assets/execution-roles/verifier.md:46,134` | 写跑分离 | 自查≠gate |

#### G3. 更新 dispatch-protocol.md 解释段落

`dispatch-protocol.md:568` 改为：

> 自查≠gate：subagent 可以自跑自查确认基本功能，但自查结论不等于 gate 结论。gate 由主 Agent 亲自执行，结果以主 Agent 为准。这防止 subagent 的"假完成"被当作 gate 通过。

#### G4. 漂移测试覆盖所有编辑点

评审指出当前只测 1 处（dispatch-prompt.md），遗漏 5 处。改为单一 source 测试：

```bash
@test "G-drift: dispatch-protocol.md 含'自查≠gate'关键词" {
    grep -q '自查≠gate' "$AGATE_ROOT/dispatch-protocol.md"
}

@test "G-drift: implementer.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/implementer.md"
}

@test "G-drift: verifier.md 不含'写跑分离'" {
    ! grep -q '写跑分离' "$AGATE_ROOT/assets/execution-roles/verifier.md"
}
```

3 个测试覆盖全部 8 个编辑点（dispatch-protocol.md 是聚合文件，implementer.md 和 verifier.md 是角色定义）。`phase-cards` 和 `dispatch-prompt.md` 继承这两个角色文件，如果角色文件改了卡片和模板也会同步改（一致性检查覆盖）。

---

## B. dispatch-context 缺失检测

### 问题（scope 修正）

**T048 复盘 §10.1** 描述两个问题：
1. dispatch-context.md **压根没写**（缺失）
2. dispatch-context.md **事后补写**（绕过 hash 校验）

本项解决的是**问题 1（缺失）**。问题 2（事后补写）属于自报数据同源无解类——agent 字段由主 Agent 自己写，hash 校验的输入也由主 Agent 自己提供。这与 LIMITATIONS.md 局限 3（主 Agent 侧防御空白）同根，当前无法根治，需 defer 到 git author 等平台机制。

### 方案

#### B1. 协议层：先写再派（L0 指导）

在 `dispatch-protocol.md` 的"客观信息落盘"节增加时序约束：

```
时序约束：
- dispatch-context.md 必须在派发 subagent 之前写入
- 派发 prompt 引用此文件路径 → subagent 读取 → 上下文注入生效
- 事后补写 = 违规（当前无法自动检测——与局限 3 同根，defer 到 git author 等平台机制）
```

#### B2. 多次派发：阶段级共享上下文

dispatch-context.md 记录本阶段所有派发共享的客观信息。每次派发的差异部分写在 prompt 里。

#### B3. hook 层：缺失 WARNING（L2）

在 `pre-commit-gate.sh` 的 2n 节之后、2o 节之前：

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
- ❌ dispatch-context 事后补写且同次 commit → 无法检测（defer）

### defer 清单

**事后补写绕过 hash 校验**：与局限 3 同根（自报数据同源），需 git author 或平台结构化身份机制，当前 defer。

### 测试

1 个 bats 测试：产出暂存但无 dispatch-context → WARNING 输出。

---

## D. subagent 假完成防护

### 问题

subagent 返回"已修复"但文件未实际变更。

### 方案

#### D1. 派发 prompt 增加返回前自检（L0 指导）

在 `assets/templates/dispatch-prompt.md` 的"返回给我"节追加：

```
## 返回前自检（强制）
如果任务涉及修改/创建文件，返回前必须：
  1. 用 bash 执行 grep/rg 确认改动已落盘
  2. 如果 grep 未匹配 → 文件未写入成功 → 重新写入后再返回
  3. 不要在未确认落盘的情况下返回"已完成"
```

#### D2. 主 Agent 独立校验（L4 外部可观测）

在 `dispatch-protocol.md` 的"subagent 返回校验"节增加：

```
6. 修改类任务的文件内容校验（外部可观测）：
   subagent 返回"已修复/已实现"后，主 Agent 对声称修改的文件做最小验证：
   - 用 bash 执行 grep 确认新增/修改的代码行存在
   - 如果声称修改但文件内容未变 → 视为假完成，重派
   - 这不是"主 Agent 改代码"——主 Agent 只读验证，不写文件
```

#### D3. 结构化返回 `files_modified`（L0 指导，补充 D2）

复盘 §5.4 原建议是 `files_modified: [path1, path2]` 结构化返回，让主 Agent **自动**校验路径存在性 + 文件非空。比"grep 猜函数名"可靠一个量级。

在 `assets/templates/dispatch-prompt.md` 的"返回给我"节追加：

```
## 返回格式（修改类任务）
第 3 行（可选）：files_modified: [path1, path2, ...]
列出你修改/创建的文件路径。主 Agent 将校验这些路径存在且非空。
```

在 `dispatch-protocol.md` 的"subagent 返回校验"节增加第 7 条：

```
7. files_modified 路径校验：
   subagent 返回 files_modified: [path1, path2] 时，主 Agent 校验每个路径：
   - 路径对应的文件存在 + 非空 → 通过
   - 路径不存在或文件为空 → 假完成，重派
   - 无 files_modified 字段 → 退回 D2 的 grep 校验（兼容旧格式）
```

**成本**：仅在 prompt 里要求多写一行路径列表，无脚本改动。

**为什么是 L0 不是 L3**：files_modified 是 subagent 自报的，主 Agent 仍可忽略。真正强制靠 D2（主 Agent 亲自 grep 磁盘）。D3 是 D2 的补充——如果 subagent 诚实返回了路径列表，主 Agent 的校验更精确；如果 subagent 不诚实，D2 的 grep 兜底。

### 测试

2 个 bats 测试：
1. dispatch-prompt.md 含"返回前自检"关键词
2. dispatch-prompt.md 含"files_modified"关键词

---

## E2. 评审 self-approved 检查

### 问题

主 Agent 可以自行批准评审（T048 P2 违规）。当前 provenance 脚本对 `risk=high + agent=main` 只 WARNING。

### 评审 BLOCKER 修复

**评审指出**：当前 `check-p6-provenance.sh` 全体被 `if [ -f "$P6_FILE" ]` 门控，P2 阶段 self-approved 的评审要到 P6 才被拦——此时 P3/P4/P5 已基于自批设计跑完，为时已晚。

**解决方案**：把评审 agent=main 检查从 provenance 脚本（P6 门控）拆出来，放进 `check-gate.sh` 的 P2 分支，在 **P2 gate 时直接触发**。

移除 `risk=high` 前置条件：任何 risk 等级的 self-review 都不可信（T048 是 risk=medium）。

### 方案

#### E2a. check-gate.sh P2 分支增加 agent 检查（L3 硬拦截）

在 `check-gate.sh` 的 P2 分支，P2-review.md status:approved 检查之后，增加：

```bash
if [ -f "$P2_REVIEW" ] && grep -qE 'status:\s*approved' "$P2_REVIEW" 2>/dev/null; then
    P2_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | grep '^agent:' | sed 's/^agent:\s*//' | head -1)
    if [ -z "$P2_REVIEW_AGENT" ]; then
        echo "GATE P2: P2-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
        exit 2
    fi
    if [ "$P2_REVIEW_AGENT" = "main" ]; then
        echo "GATE P2: P2-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
        exit 1
    fi
fi
```

触发时机：P2 gate → P2→P3 状态转移时 pre-commit hook 调 check-gate.sh → 立即拦截。不依赖 P6 门控。

#### E2b. 修改 provenance 脚本（移除旧的 P2-review WARNING）

在 `check-p6-provenance.sh` 的协作规范节，删除现有的 P2-review `risk=high + agent=main` WARNING 逻辑（L206-217），因为同等检查已由 E2a 在 P2 gate 做（且更强——exit 1 而非 exit 2，无 risk=high 前置）。

provenance 的 P2-review 部分保留缺 agent 字段 WARNING（向后兼容，exit 2）。

#### E2c. CI backstop 扩展（堵 --no-verify）

评审指出：CI 只重跑 `check-gate.sh`，不跑 `check-p6-provenance.sh`。E2a 把检查放进 `check-gate.sh` 后，CI backstop 自然覆盖——`ci-gate-backstop.py:51` 已调用 `run_gate(phase, task_dir)` 而这正是 `check-gate.sh`。

无需额外改动 CI。E2a 的检查随 P2 gate 进入 CI 覆盖范围。

#### E2d. 定位诚实标注

E2 是**抬高随手自批成本**，不是**根治自批**。agent 字段是主 Agent 自己写的——诚实标注 agent=main 的会被抓，蓄意写 agent=subagent 的可零成本绕过。根治需 git author 等主 Agent 写不了的身份来源（defer）。

### 覆盖边界

- ✅ P2 gate 时 P2-review.md agent=main + approved → exit 1（L3 硬拦截）
- ✅ P2-review.md 缺 agent 字段 + approved → exit 2（L2 WARNING）
- ✅ subagent 评审 agent≠main + approved → 通过
- ✅ CI 覆盖（随 P2 gate 进入 backstop）
- ❌ 主 Agent 同时改 agent 字段 → 绕过（蓄意伪造，defer 到 git author）
- ❌ `git commit --no-verify` → E2a 在 P2 gate 不触发，但 **CI backstop 会重跑 P2 gate** → 最终被拦

### 测试

- 修改现有 G2.10/G2.11 测试：P2-review.md agent=main + approved → exit 1（原 exit 1，但原因从"缺 status:approved"变为"agent=main"）
- 新增 G2.18：P2-review.md agent=test + approved → exit 2（通过）
- 新增 G2.19：P2-review.md 缺 agent 字段 + approved → exit 2（WARNING）
- PV.15 改为 exit 1（与 E2a 一致，但 provenance 脚本的 P2-review 段已删除此逻辑，改为缺字段 WARNING）

---

## E3. 非合法阶段代码暂存 WARNING

### 方案

在 `pre-commit-gate.sh` 的 2n 节之后、2o 节之前（与 B3 同一插入点）：

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

覆盖：P4/P5/P6 放行，其他阶段 WARNING。盲区在 P4（主 Agent 自己改代码无法区分），价值有限但成本低，作为绊线保留。

### 测试

1 个 bats 测试：P2 阶段暂存 .py → WARNING 输出。

---

## 实施顺序

```
G. 写跑分离粒度修正（8 个文件文本替换 + 3 个漂移测试）
B. dispatch-context 缺失检测（B1 协议 + B3 WARNING）
D. subagent 假完成防护（D1 prompt + D2 协议 + D3 结构化返回）
E2. 评审 self-approved 检查（E2a gate.sh + E2b provenance 清理 + 测试）
E3. 非阶段代码 WARNING（pre-commit-gate.sh + 测试）
```

G/B/D 是文档为主，E2 是脚本为主（需 TDD），E3 是脚本为主。各 item 无依赖，可并行。

---

## defer 清单

| 项 | 原因 | 需要什么 |
|---|------|---------|
| dispatch-context 事后补写 | 自报数据同源（与局限 3 同根） | git author 或平台结构化身份 |
| 评审 agent 字段蓄意伪造 | 自报字段可绕过 | git author（主 Agent 写不了） |
| P1 评审缺口 | 需定义 C8 评审角色 + hook 化 | 独立 feature |
| P4 评审 hook 化 | check-gate.sh P4 不检查 P4-review.md | 需设计"评审触发条件"语义 |
| P6/P7 self-authored 根治 | verifier/主 Agent 既是执行者又是判定者 | 平台支持独立 git author |

---

## 风险

| 风险 | 缓解 |
|------|------|
| G 重命名后旧"写跑分离"文本残留 | grep 扫描确认 0 处残留 |
| E2a 主 Agent 伪造 agent 字段 |抬高随手自批成本；蓄意伪造 defer 到 git author |
| E2a 缺 agent 字段向后兼容 | exit 2 WARNING 不阻塞 |
| B3 dispatch-context WARNING 误报（同次 commit） | 同次 commit 不警告 |
| D2 主 Agent 不知道 grep 什么 | D3 的 files_modified 补充路径列表；无 D3 时退回 D2 grep |
| E3 P4 盲区（主 Agent 自己改代码） | 价值有限成本低，绊线保留 |

---

## v1→v2→v3 评审变更记录

| # | 版本 | 问题 | 修正 |
|---|------|------|------|
| 1 | v1→v2 | G 未说明 P5 不受影响 | v2 补充 P5 无 subagent |
| 2 | v1→v2 | G 未区分自查 vs 自检 | v2 补充：G 管功能验证，D 管写入确认 |
| 3 | v1→v2 | E2 保留 risk=high 前置 | v2 移除，任何 risk 的 self-review 都拦截 |
| 4 | v1→v2 | E2 缺 agent 字段静默放行 | v2 补充缺字段时 exit 2 WARNING |
| 5 | v1→v2 | B3/E3 未说明插入位置 | v2 补充 2n 之后 2o 之前 |
| 6 | v2→v3 | **E2 触发时机 BLOCKER**（P6 门控下 P2 检查到 P6 才生效） | v3 把检查从 provenance 拆到 check-gate.sh P2 分支，P2 gate 时直接触发 |
| 7 | v2→v3 | **B scope 错配**（B 解决缺失不解决事后补写） | v3 改写问题陈述；事后补写 defer |
| 8 | v2→v3 | **D 丢了 files_modified 结构化返回** | v3 加回 D3，补充 D2 |
| 9 | v2→v3 | **G 漂移测试只覆盖 1/6** | v3 扩到 3 个测试覆盖全部编辑点 |
| 10 | v2→v3 | **强制力分级缺失** | v3 增加 L0-L4 分级表 |
| 11 | v2→v3 | **E2 CI 不覆盖** | v3 说明 E2a 随 P2 gate 自然进入 CI backstop |
| 12 | v2→v3 | **E2 定位过度承诺** | v3 诚实标注：抬高随手自批成本，非根治 |
