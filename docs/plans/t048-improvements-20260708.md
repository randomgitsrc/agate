---
task_id: t048-improvements
agent: main
date: 2026-07-08
status: 设计方案 v2（专家评审后迭代）
来源: docs/reviews/t048-retrospective-20260707.md + 用户补充（§10.1-10.3）
---

# T048 复盘改进计划

## 原则

1. **降低主 Agent 负担**——能用脚本解决的优先用脚本，主 Agent 只做不可脚本化的判断
2. **脚本覆盖边界要明确**——不太小（漏检），也不无边界蔓延（误杀）
3. **上下文窗口是稀缺资源**——协议规则应尽量压缩到脚本/hook 层，不依赖 Agent 记忆

## 问题分类与优先级

| # | 问题 | 根因 | 优先级 | 改进方向 |
|---|------|------|--------|---------|
| A | gate 脚本正则过严（4处） | 脚本：字符串匹配 vs 语义匹配 | 🔴 | 改脚本 |
| B | dispatch-context 时序漏洞 | 协议：无"先写再派"约束 | 🔴 | 改协议+脚本 |
| C | provenance 证据数规则 | 脚本：文件计数 vs 引用计数 | 🟡 | 改脚本 |
| D | subagent 假完成 | 协议：无产出验证机制 | 🟡 | 改协议 |
| E | 主 Agent 违规兜底 | 协议：铁律依赖 Agent 记忆 | 🔴 | 脚本兜底 |
| F | 上下文窗口与纪律 | 环境：200k vs 1M | 🟡 | 协议缓解 |

---

## A. gate 脚本正则改为语义匹配

### 问题

4 处正则过严，本质相同：脚本检查"精确关键词存在"而非"语义意图达成"。

| # | 位置 | 当前正则 | 误杀案例 |
|---|------|---------|---------|
| A1 | check-gate.sh:29 | `方案[ABC123]` | `### 方案 A`（有空格） |
| A2 | check-gate.sh:48 | `权衡\|选择理由` | `### 选择：方案 A` + `**理由**` |
| A3 | check-gate.sh:89-90 | `\[BLOCKER\]` | `- [BLOCKER]: 0 条`（声明当实际） |
| A4 | check-p6-evidence.sh:32 | `.(png\|jpg\|...)` | `(path.png, vision: OK)` |

### 方案

**原则**：同义词列表扩展 + 声明/实际区分 + 格式兼容。不引入语义解析（bash 不适合 NLP），只做"关键词空间扩大"。

#### A1. P2 候选方案标题

```bash
# 当前
grep -cE '^###?\s*候选方案|^###?\s*方案[ABC123]'

# 改为
grep -cE '^###?\s*(候选方案|方案\s*[ABC123abc一二三四五])'
```

覆盖：
- ✅ `方案 A` `方案A` `方案1` `方案一` `候选方案A` `候选方案 1`
- ❌ `方案概述` `方案说明`（非编号，正确拒绝）

#### A2. P2 权衡/选择理由

```bash
# 当前
grep -qE '权衡|选择理由'

# 改为
grep -qE '权衡|选择理由|取舍|考量|trade-?off|选择.*理由|理由.*权衡'
```

覆盖：
- ✅ `权衡` `选择理由` `取舍` `考量` `tradeoff` `理由与权衡`
- ✅ `选择：方案 A` 后文 `**理由**` → `选择.*理由` 跨行匹配（grep 不做跨行，但 P2-design.md 是同一文件内的全文搜索，`选择` 和 `理由` 可能在不同行 → 改为两步检查）

**两步检查**（更稳健）：
```bash
# 步骤1：同义词直接匹配
if grep -qE '权衡|选择理由|取舍|考量|trade-?off|理由与权衡' "$P2_FILE"; then
    : # 通过
# 步骤2：有"选择"标题 + 正文含"理由/原因/因为"
elif grep -qE '选择' "$P2_FILE" && grep -qE '理由|原因|因为' "$P2_FILE"; then
    : # 通过
else
    echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
    exit 1
fi
```

#### A3. P7 BLOCKER 声明 vs 实际

```bash
# 当前
BLOCKERS=$(grep -cE '^\s*-?\s*\[BLOCKER\]' "$P7_FILE" 2>/dev/null || echo 0)

# 改为：排除纯数量声明行
BLOCKERS=$(grep -E '^\s*-?\s*\[BLOCKER\]' "$P7_FILE" 2>/dev/null \
    | grep -cvE '\[BLOCKER\][:：]?\s*\d+\s*条?\s*$' \
    || echo 0)
```

覆盖：
- ✅ `- [BLOCKER] 数据库迁移不可逆` → 计数
- ✅ `- [BLOCKER]: 0 条` → 排除
- ✅ `- [BLOCKER]：0条` → 排除（中文冒号+无空格）
- ✅ `- [BLOCKER]: 2 条` → 计数（"2 条"后有描述文字则不匹配 `$`）

#### A4. P6 证据引用格式

```bash
# 当前
echo "$line" | grep -qE '\([a-zA-Z0-9_/.-]+\.(png|jpg|log|json|html|txt|yaml|yml)\)'

# 改为：括号内含文件扩展名即可，允许后续附加内容
echo "$line" | grep -qE '\([a-zA-Z0-9_/.-]+\.(png|jpg|log|json|html|txt|yaml|yml)[^)]*\)'
```

覆盖：
- ✅ `(path.png)` `(path.png, vision: OK)` `(screenshots/b01.png; see also b02.log)`
- ❌ `(see description)` 无扩展名 → 正确拒绝

**注意**：`check-p6-provenance.sh` 已有 R1b 兼容（剥离 `(vision: ...)` 后取行末括号组），两个脚本的提取逻辑不一致。A4 修复后 `check-p6-evidence.sh` 只判断"有引用"，`check-p6-provenance.sh` 负责"引用指向真实文件"——职责不同，逻辑差异可接受。

### 测试

每个 A item 加 2 个 bats 测试：1 个误杀案例（v1 拦截、v2 放行）+ 1 个正常拦截案例（v1/v2 都拦截）。

---

## B. dispatch-context 时序约束

### 问题

1. dispatch-context.md 事后补写，hash 校验形同虚设
2. 多次派发时一篇 dispatch-context 无法覆盖

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

**方案**：dispatch-context.md 记录本阶段所有派发共享的客观信息。每次派发的差异部分（如"评审修订后重派"）写在 prompt 里。

理由：
- dispatch-context 的设计意图是"主 Agent 已查证的客观信息"（环境/URL/选择器），同阶段多次派发间通常不变
- 每次派发的差异是任务描述，属于 prompt 内容
- 文件数不膨胀，hook 逻辑不变

#### B3. hook 层：弱检测（WARNING）

在 `pre-commit-gate.sh` 中，如果产出文件被暂存但 dispatch-context.md 不存在（不在暂存区也不在 HEAD），发出 WARNING：

```bash
# 产出文件被暂存 + dispatch-context 不存在 → WARNING
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

**结论**：hook 做弱检测，真正保障靠协议层规则（B1）。

### 测试

1 个 bats 测试：P2 产出暂存但无 dispatch-context → WARNING 输出。

---

## C. provenance 证据数规则改为引用计数

### 问题

`check-p6-provenance.sh` 审计 1b：`PASS 条目数 ≤ 证据文件数`。多条 BDD 共享同一 pytest 结果文件时被迫创建充数文件。

### 方案

删除审计 1b（`PASS_COUNT > EVIDENCE_COUNT` 检查）。保留审计 1a（引用路径存在）和 1c（文件被引用）。审计 1a + 1c 组合已足够：

- 1a 保证：每条 PASS 引用的文件都存在
- 1c 保证：每个证据文件都被至少一条 PASS 引用（防充数）
- 删除 1b 后：N 个 PASS 可共享 M 个证据文件（M < N 允许）

覆盖：
- ✅ 14 PASS 引用 8 个证据文件 → 通过（当前被拦截）
- ✅ 14 PASS 引用 14 个证据文件 → 通过
- ❌ 14 PASS 引用 0 个证据文件 → 审计 1a 拦截（引用路径不存在）
- ❌ 8 个证据文件但只有 5 个被引用 → 审计 1c 拦截（3 个充数）

### 改动

`check-p6-provenance.sh`：删除第 65-81 行（审计 1b 整段）。

### 测试

1 个 bats 测试：14 PASS 引用 8 个共享证据文件 → exit 0。

---

## D. subagent 假完成防护

### 问题

subagent 返回"已修复"但文件未实际变更。根因是"只返回摘要"指令被理解为"不需实际执行"。

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

## E. 主 Agent 违规的脚本兜底

### 问题

T048 主 Agent 3 次违规（P1 未 commit、擅改评审、直接改代码），根因是 Agent 遗忘铁律。

### 现有覆盖

| 违规 | 现有防护 | 缺口 |
|------|---------|------|
| P1 未 commit | ✅ `check-state-transition.sh` 检查 3（P1→P2 时 P1-requirements.md 必须已 commit） | 无缺口，已覆盖 |
| 擅改评审 | ⚠️ `check-p6-provenance.sh` 仅 WARNING（risk=high + agent=main） | 无硬拦截 |
| 直接改代码 | ❌ 无检测 | 完全缺口 |

### 方案

#### E1. P1 未 commit → 已覆盖，无需改动

`check-state-transition.sh:106-156` 的检查 3 已覆盖：P{n}→P{n+1} 时 P{n} 产出必须已 commit。覆盖 P1→P2, P2→P3, P3→P4, P6→P7。

**T048 仍发生的原因**：主 Agent 跳过了 .state.yaml 更新（P1 未 commit 也没改 phase），直接进入 P2——hook 根本没触发。这不是脚本缺口，是 Agent 完全跳过了流程。

**缓解**：阶段卡片已显式列出"gate 后 commit → 更新 phase → 推进"，无需额外脚本改动。

#### E2. 评审 agent=main 硬拦截

在 `check-p6-provenance.sh` 的协作规范节，将现有 WARNING 升级：

```bash
# 当前（WARNING，exit 2）
if [ "$RISK" = "high" ] && [ "$AGENT" = "main" ]; then
    echo "GATE PROVENANCE: risk_level=high 且 P2-review.md agent=main（自审），建议派发独立 reviewer" >&2
    exit 2
fi

# 改为（硬拦截，exit 1）+ 扩展到所有评审文件
for review_file in "$TASK_DIR"/P[0-8]-review.md; do
    [ -f "$review_file" ] || continue
    AGENT=$(get_agent "$review_file")
    if grep -qE 'status:\s*approved' "$review_file" 2>/dev/null; then
        if [ "$AGENT" = "main" ]; then
            echo "GATE PROVENANCE: $(basename "$review_file") status=approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
            exit 1
        fi
    fi
done
```

覆盖：
- ✅ subagent 评审 approved → agent ≠ main → 通过
- ✅ 主 Agent 擅改 approved → agent = main → 拦截
- ❌ 主 Agent 同时改 agent 字段 → 绕过（蓄意伪造，provenance 审计可标记）
- ❌ 旧文件无 agent 字段 → 向后兼容（缺字段时 WARNING 不阻塞，与现有逻辑一致）

#### E3. 非 P4/P5/P6 阶段暂存代码 → WARNING

```bash
# 在 pre-commit-gate.sh 中增加
CODE_FILES=$(git diff --cached --name-only 2>/dev/null | grep -vE '\.(md|yaml)$|^\.state')
if [ -n "$CODE_FILES" ]; then
    case "$PHASE" in
        P4|P5|P6) ;;  # 合法代码修改阶段
        *)
            echo "GATE WARNING: phase=$PHASE 但暂存了代码文件——主 Agent 是否在非实现阶段直接改代码？" >&2
            ;;
    esac
fi
```

覆盖：
- ✅ P4 阶段暂存代码 → 不警告
- ✅ P2 阶段暂存代码 → 警告
- ✅ P6 验收脚本（.py/.ts）→ P6 在放行列表，不警告
- ❌ P4 阶段主 Agent 自己改代码 → 无法区分（需 agent 字段，代码文件无 frontmatter）

**结论**：E3 只做弱检测。主 Agent 在 P4 直接改代码靠 E2（评审 agent 检查）+ 协议铁律 + 上下文管理（F）综合缓解。

### 测试

- E2：2 个 bats 测试（agent=main + approved → exit 1；agent=subagent + approved → exit 0）
- E3：1 个 bats 测试（P2 阶段暂存 .py → WARNING 输出）

---

## F. 上下文窗口与 Agent 纪律

### 问题

200k 上下文下规则被挤出，Agent 行为退化。1M 上下文下正常。

### 方案

#### F1. hook 兜底声明

在 `orchestrator-template.md` 增加"hook 兜底"说明：

```
## 铁律由脚本强制

以下铁律已由 gate 脚本/hook 强制执行，Agent 不需要记忆——忘了也会被拦截：
- 每阶段产出必须 commit 后才能推进 phase（check-state-transition.sh 检查 3）
- 评审 approved 必须由 subagent 判定（check-p6-provenance.sh agent 检查）
- 非 P4/P5/P6 阶段暂存代码 → WARNING（pre-commit-gate.sh）

Agent 仍需遵守这些规则（减少拦截次数 = 减少无效时间），但违反时不会静默通过。
```

#### F2. 上下文预算建议

在 `LIMITATIONS.md` 增加：

```
## 上下文预算

agate 协议文件 + 阶段卡片约占 15-20k token。建议：
- 主 Agent 上下文 ≥ 100k token 时，可完整运行 P0-P8
- 主 Agent 上下文 < 100k token 时，建议分批执行（P0-P2 → commit → 新会话 P3-P8）
- 200k 上下文在长任务（>2h）后期可能出现规则遗忘，hook 兜底是关键防线
```

#### F3. 会话中断恢复

在 `dispatch-protocol.md` 增加：

```
## 会话中断恢复

如果模型切换/会话超时/content filter 触发导致上下文丢失：
1. 读 .state.yaml 确认当前 phase
2. 读当前阶段卡片
3. 读 P{N}-progress.md（subagent 留痕文件）确认已完成步骤
4. 读 dispatch-context.md 确认客观信息
5. 从中断点继续，不重做已完成步骤
```

### 测试

无脚本改动，不需 bats 测试。一致性检查确认文档更新即可。

---

## v1→v2 评审变更记录

| # | v1 问题 | v2 修正 |
|---|--------|--------|
| 1 | E1 提议在 check-state-transition.sh 增加 commit 检查 | **已存在**（检查 3，L106-156）。E1 改为"已覆盖，无需改动" |
| 2 | A2 `选择.*理由` 声称跨行匹配 | grep 不做跨行匹配。改为两步检查（同义词 + "选择"∩"理由"组合） |
| 3 | A3 先用 lookahead（bash 不支持），再给两个替代方案 | v2 只保留一个方案（grep -vE 排除纯数量声明），删除废弃思路 |
| 4 | A4 未注意 check-p6-evidence.sh 和 check-p6-provenance.sh 的提取逻辑不一致 | v2 明确说明两个脚本职责不同（证据引用格式检查 vs 引用路径存在性检查），逻辑差异可接受 |
| 5 | E2 只检查 P2-review.md | v2 扩展到所有 P{N}-review.md 文件 |
| 6 | B2 列出方案 A 和方案 B，方案 B 未被分析 | v2 只保留方案 A（阶段级共享上下文），删除未选方案 |
| 7 | D1/D2 未考虑"主 Agent 不知道改了哪行"时的 fallback | v2 保留此限制在覆盖边界中，标注"依赖 subagent 摘要定位" |
| 8 | F1 声称"主 Agent 只需读 2 个文件" | 不现实（dispatch-protocol.md 的铁律仍需读）。v2 改为"hook 兜底声明"——铁律由脚本强制，不是不需要读 |
| 9 | 缺 frontmatter | v2 增加 task_id/agent/date/status 来源 |
| 10 | 风险表未覆盖 E3 误判 | v2 风险表补充 E3 场景 |

---

## 实施顺序

```
Phase 1（脚本层，独立可测，无协议依赖）:
  A. gate 脚本正则改为语义匹配
  C. provenance 证据数规则改为引用计数

Phase 2（协议+脚本联动）:
  B. dispatch-context 时序约束（B1 协议 + B3 WARNING）
  D. subagent 假完成防护（D1 prompt + D2 协议）
  E2. 评审 agent=main 硬拦截
  E3. 非合法阶段代码暂存 WARNING

Phase 3（协议层，文档为主，依赖 Phase 2 hook 就位）:
  F. 上下文窗口与纪律缓解
```

Phase 1 和 Phase 2 各 item 无依赖，可并行。Phase 3 依赖 E2/E3 就位。

---

## 风险

| 风险 | 缓解 |
|------|------|
| A 正则放宽导致漏检 | 覆盖边界分析 + 每个 item 2 个 bats 测试 |
| A4 两个脚本提取逻辑不一致 | 职责不同（格式检查 vs 路径存在性），可接受 |
| E2 评审 agent=main 拦截旧文件（无 agent 字段） | 缺字段时 WARNING 不阻塞（向后兼容） |
| E2 主 Agent 伪造 agent 字段绕过 | provenance 审计可标记；蓄意伪造超出脚本防线范围 |
| E3 P6 验收脚本被误判为"代码文件" | P6 在放行列表 |
| E3 P4 主 Agent 自己改代码无法区分 | 代码文件无 frontmatter，脚本无法区分 author |

---

## 不在本次范围内

- **ORM 枚举序列化差异**：项目层面问题，非 agate 协议问题
- **构建产物版本检查**：项目层面问题，需项目自定义 gate_commands
- **content filter 触发原因分析**：需 GLM 5.1 的 filter 日志，agate 无法获取
- **subagent 返回结构化字段**：需 Task 工具平台支持
- **E1 P1 未 commit**：`check-state-transition.sh` 检查 3 已覆盖
