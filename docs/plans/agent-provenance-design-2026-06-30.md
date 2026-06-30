# P2.1/P2.6/P2.10 降级方案设计：产出者可判定性

> 日期：2026-06-30
> 状态：设计文档
> 关联：docs/hardening-roadmap.md P2.1/P2.6/P2.10（原 Blocked，待 Phase 3 平台支持）
> 核心原则：改动最小，给 Agent 压力小，通过客观事实做到判定

---

## 1. 问题

三项 Blocked 都指向同一个缺口：**无法区分"主 Agent 写的文件"和"subagent 写的文件"**。

| 编号 | 名称 | 原依赖 | 威胁 |
|------|------|--------|------|
| P2.1 | P6 验收独立化 | subagent 独立 git author | T026：主 Agent 编造 11/16 BDD 结果 |
| P2.10 | P2 评审派发强制 | subagent 独立 git author | 3 个保留 P2 任务全 self-approve |
| P2.6 | gate 判定独立化 | subagent 独立 git author | 主 Agent 可伪造 .gate-result.json |

**三种攻击场景**：

1. **跳过 subagent**（T026 模式）：主 Agent 不派 verifier subagent，自己直接写 P6-acceptance.md
2. **事后篡改**：主 Agent 派了 subagent，但产出后修改 P6-acceptance.md 的 PASS/FAIL 结果
3. **误导 subagent**：主 Agent 在 dispatch-context.md 里预写验收结论，verifier subagent 被引导到同样结论

**原方案**：等平台支持 subagent 独立 git author。但 Claude Code/OpenCode 不支持，且无时间表。

**核心判断**：不应该等平台。用降级方案现在实现，把"等平台"变成"先用降级方案，平台支持后升级"。

---

## 2. 方案：Header agent 字段 + 多重交叉验证

### 2.1 核心机制

产出文件通用 Header 加 `agent` 字段，声明谁写的这个文件。hook 通过 `agent` 字段值 + 多重客观事实交叉验证，判定产出者身份。

**为什么不用密码学签名**：
- subagent 是 LLM，不会自动算 sha256 写进文件
- 要让它签名就得改 dispatch prompt 让它执行额外脚本，增加复杂度
- agate 是文档协议不是加密协议，防篡改靠可观测性叠加，不靠单点密码学强度

**为什么不用伴生 .provenance.json**：
- 双文件管理复杂，subagent 可能忘记产出伴生文件
- 主 Agent 要同时改两个文件确实更难，但复杂度成本不值得——三层交叉验证已经把伪造成本提到"同时改三处"

**为什么不用纯派发日志 + mtime**：
- 派发日志是主 Agent 自己写的（self-reported），和 .state.yaml 一样可伪造
- mtime 可被 `touch -t` 伪造
- 单一信号源不可靠，必须多重交叉

### 2.2 Header agent 字段

**改动**：通用 Header 从 7 个字段变为 8 个。

```yaml
---
phase: P6
task_id: T027
type: acceptance
parent: P5-test-results.md
trace_id: T027-P6-20260630
status: approved
created: 2026-06-30
agent: verifier        # ← 新增
---
```

**agent 字段取值**（与 execution-roles 一一对应）：

| 值 | 含义 | 产出文件 |
|---|------|---------|
| `main` | 主 Agent 亲自产出 | P0-brief.md |
| `analyst` | P1 analyst subagent | P1-requirements.md |
| `architect` | P2 architect subagent | P2-design.md |
| `reviewer` | P2 reviewer subagent | P2-review.md |
| `test-designer` | P3 test-designer subagent | P3-test-cases.md |
| `implementer` | P4 implementer subagent | P4-implementation.md |
| `verifier` | P5/P6 verifier subagent | P5-test-results/, P6-acceptance.md |

**对 subagent 的压力**：dispatch prompt 模板 Header 部分加一行 `agent: {角色名}`。主 Agent 派发时已填好，subagent 复制即可。零额外认知负担。

**对主 Agent 的压力**：P0-brief.md 主 Agent 自己写，agent: main。其他阶段主 Agent 不写产出文件（铁律 1），不需要额外操作。

**客观判定**：hook `grep '^agent:'` 字段，值是确定字符串，完全可判定。

### 2.3 多重交叉验证

单一信号可伪造，多重信号同时伪造的成本远高于"派一个 subagent"。

**验证层 1：agent 字段检查**（防场景 1：跳过 subagent）

| 条件 | 检查 | 结果 |
|------|------|------|
| P6-acceptance.md 存在 | Header `agent:` == `verifier` | 不匹配 → exit 1 |
| P2-review.md 存在 且 risk_level=high | Header `agent:` == `reviewer` | 不匹配 → exit 1 |
| P2-review.md 存在 且 risk_level=medium | Header `agent:` == `reviewer` 或 `main` | `main` → exit 2（警告，不阻塞） |
| 任何阶段产出文件 | Header `agent:` 字段存在 | 缺失 → exit 1 |

**验证层 2：phase 序列对照**（防场景 1 的辅助验证）

.state.yaml 的 phase 历史必须经过对应阶段。例如 P6-acceptance.md 存在时，.state.yaml 的 phase 序列必须经过 P6（不能从 P5 直接跳到 P7——除非 P1 声明裁剪 P6 且 no_behavior_change: true，这已被 check-pruning.sh 覆盖）。

这一层已有 check-state-transition.sh 保证，不需要新增逻辑。只需在 check-agent-provenance.sh 里确认 .state.yaml 当前 phase >= P6（即 P6 已经或正在执行）。

**验证层 3：dispatch-context 审计**（防场景 3：误导 subagent）

P6 阶段的 dispatch-context.md 不含验收结论预判。具体检查：
- `P6-dispatch-context.md` 存在时，`grep -cE '^\s*- (PASS|FAIL)'` == 0
- 即：dispatch-context 里不能出现 BDD 验收结论格式

主 Agent 在 dispatch-context 里写环境状态、URL、选择器是合法的（客观事实），写"B01 应该 PASS"是违规的（预判结论）。

**验证层 4：git diff 完整性**（防场景 2：事后篡改，CI 层）

CI backstop 重跑 gate 时，额外检查：
- P6-acceptance.md 的 git blame：如果整个文件只有一个 author（且等于主 Agent identity），标记 WARNING
- 这不是硬拦截（主 Agent 可能合法地修改格式/排版），但留下审计痕迹

**四层叠加的伪造成本分析**：

| 要伪造什么 | 需要同时改 | 成本 |
|-----------|----------|------|
| 跳过 verifier 自己写 P6 | P6-acceptance.md 的 agent 字段 + .state.yaml 的 phase 序列 | 2 处，且 .state.yaml 格式受 check-state-yaml.sh 校验 |
| 事后篡改 P6 结果 | P6-acceptance.md 内容（留 git diff 痕迹）+ 可能触发 CI WARNING | git 历史可审计 |
| 误导 verifier | dispatch-context.md（受 hook 检查 PASS/FAIL 模式）| 1 处，hook 直接拦截 |

对比"派一个 verifier subagent"的成本：一次 task 调用 + 等返回。伪造成本 > 合规成本。

---

## 3. 具体改动清单

### 3.1 协议文件改动

#### 3.1.1 assets/templates/task-files.md

通用 Header 部分加 `agent` 字段：

```yaml
---
phase: {P1-P8}
task_id: {Txxx}
type: {problems|design|review|test-cases|...}
parent: {上一阶段文件名，P1 时是外部需求来源}
trace_id: {Txxx}-{Pn}-{YYYYMMDD}
status: {draft|approved|rejected|done}
created: {YYYY-MM-DD}
agent: {main|analyst|architect|reviewer|test-designer|implementer|verifier}
---
```

P0-brief.md 结构说明：agent 固定为 `main`（主 Agent 亲自写）。

#### 3.1.2 assets/templates/dispatch-prompt.md

Header 模板加 `agent` 行：

```
文件必须以这段 Header 开头（直接复制，主 Agent 已填好所有值）：
---
phase: {Pn}
task_id: {完整 task_id，如 T002-fix-db-migration}
type: {problems|design|review|test-cases|implementation|test-results|acceptance|consistency|release}
parent: {上一阶段文件名}
trace_id: {Txxx}-{Pn}-{YYYYMMDD}
status: draft
created: {YYYY-MM-DD}
agent: {角色名}
---
```

关键提醒加一条：
- **agent 字段由主 Agent 填好**：主 Agent 派发时已知角色名，直接填入，subagent 复制即可

#### 3.1.3 dispatch-protocol.md

**可判定门槛规范** P6→P7 行更新：

原：
```
P6→P7 | BDD 验收通过 ⚠️ self-authored
```

改为：
```
P6→P7 | BDD 验收通过 | scripts/check-gate.sh P6 exit 2 + scripts/check-agent-provenance.sh exit 0 + 主 Agent 手动核实 BDD 总数
```

去掉 `⚠️ self-authored` 标记——agent provenance 检查将 self-authored 风险从"无法检测"降为"可检测且成本高于合规"。

**P5/P6 派发时追加**部分加一条：

```
## 产出者声明
P6-acceptance.md 的 Header agent 字段必须为 verifier（由主 Agent 在派发 prompt 里填好）。
你自己不需要填——Header 已由主 Agent 填好，直接复制即可。
```

#### 3.1.4 state-machine.md

P6 转移规则更新：

原：
```
P6 --[scripts/check-gate.sh P6 exit 2（FAIL=0/NC=0/证据非空）AND 主 Agent 手动核实 BDD 总数 = P1 BDD 总数]--> P7
```

改为：
```
P6 --[scripts/check-gate.sh P6 exit 2 AND scripts/check-agent-provenance.sh exit 0 AND 主 Agent 手动核实 BDD 总数 = P1 BDD 总数]--> P7
```

#### 3.1.5 WORKFLOW.md

P1-P8 阶段总览表 P6 行更新门槛列，去掉 `⚠️ self-authored`。

P2 行评审角色列更新：
- risk_level=high 时：`plan-eng-review（必须派发独立 subagent，hook 检查 agent: reviewer）`

### 3.2 新增脚本

#### 3.2.1 scripts/check-agent-provenance.sh

```bash
#!/usr/bin/env bash
# check-agent-provenance.sh — 产出者可判定性检查（P2.1/P2.6/P2.10 降级方案）
# 检查阶段产出文件的 Header agent 字段 + 交叉验证
# exit 0 = 通过; exit 1 = 产出者不符; exit 2 = 警告（不阻塞）

set -euo pipefail

TASK_DIR="${1:?用法: check-agent-provenance.sh TASK_DIR}"
STATE_FILE="${2:-}"  # 可选，用于 phase 序列交叉验证

P1_FILE="$TASK_DIR/P1-requirements.md"
P6_FILE="$TASK_DIR/P6-acceptance.md"
P2_REVIEW_FILE="$TASK_DIR/P2-review.md"

# --- 辅助函数 ---

# 从文件 Header 提取 agent 字段值
get_agent() {
    local file="$1"
    [ ! -f "$file" ] && echo "" && return
    # 只读 Header 区域（--- 到 --- 之间）
    sed -n '/^---$/,/^---$/p' "$file" | grep -E '^agent:' | sed 's/^agent:\s*//' | head -1
}

# 从 P1 读取 risk_level
get_risk_level() {
    [ ! -f "$P1_FILE" ] && echo "" && return
    P1_F="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_F']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo ""
}

# --- 检查 1：P6 验收产出者 ---
# P6-acceptance.md 必须由 verifier subagent 产出

if [ -f "$P6_FILE" ]; then
    AGENT=$(get_agent "$P6_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 缺 agent 字段" >&2
        exit 1
    fi
    if [ "$AGENT" != "verifier" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md agent=$AGENT，期望 verifier" >&2
        exit 1
    fi
fi

# --- 检查 2：P2 评审产出者 ---
# risk_level=high 时 P2-review.md 必须由 reviewer subagent 产出
# risk_level=medium 时允许 main（自审）但警告

if [ -f "$P2_REVIEW_FILE" ]; then
    RISK=$(get_risk_level)
    AGENT=$(get_agent "$P2_REVIEW_FILE")

    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P2-review.md 缺 agent 字段" >&2
        exit 1
    fi

    if [ "$RISK" = "high" ] && [ "$AGENT" != "reviewer" ]; then
        echo "GATE PROVENANCE: risk_level=high 但 P2-review.md agent=$AGENT，期望 reviewer" >&2
        exit 1
    fi

    if [ "$RISK" = "medium" ] && [ "$AGENT" = "main" ]; then
        echo "GATE PROVENANCE: risk_level=medium 且 P2-review.md agent=main（自审），建议派发独立 reviewer" >&2
        exit 2
    fi
fi

# --- 检查 3：dispatch-context 审计 ---
# P6 阶段的 dispatch-context 不能含验收结论预判

DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"
if [ -f "$DISPATCH_CTX" ]; then
    PREJUDICE=$(grep -cE '^\s*- (PASS|FAIL)' "$DISPATCH_CTX" 2>/dev/null || echo 0)
    PREJUDICE=$(echo "$PREJUDICE" | tail -1)
    if [ "$PREJUDICE" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-dispatch-context.md 含 ${PREJUDICE} 处验收结论预判（- PASS/- FAIL 格式），可能误导 verifier" >&2
        exit 1
    fi
fi

# --- 检查 4：agent 字段存在性（所有产出文件）---
# 阶段产出文件（P{n}-*.md）必须有 agent 字段

for f in "$TASK_DIR"/P[0-8]-*.md; do
    [ -f "$f" ] || continue
    # P0-brief.md 由主 Agent 写，agent=main，跳过检查（已保证）
    basename "$f" | grep -q '^P0-' && continue
    AGENT=$(get_agent "$f")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: $(basename "$f") 缺 agent 字段" >&2
        exit 1
    fi
done

exit 0
```

### 3.3 现有脚本改动

#### 3.3.1 scripts/pre-commit-gate.sh

在步骤 5.5（裁剪条件检查）之前插入 agent provenance 检查：

```bash
# 5.4 产出者可判定性检查（P2.1/P2.6/P2.10）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-agent-provenance.sh" "$TASK_DIR" "$STATE_FILE" || exit 1
fi
```

位置在 gate 运行之后、裁剪检查之前——因为 provenance 检查不依赖裁剪结果，但依赖 gate 未失败（gate 错误优先）。

#### 3.3.2 scripts/ci-gate-backstop.py

CI backstop 新增一项检查：P6-acceptance.md 的 git blame 只有一个 author 时输出 WARNING。

```python
# P6 provenance audit (CI layer)
p6_file = task_dir / "P6-acceptance.md"
if p6_file.exists():
    blame = subprocess.run(
        ["git", "blame", "--line-porcelain", str(p6_file)],
        capture_output=True, text=True
    )
    authors = set()
    for line in blame.stdout.splitlines():
        if line.startswith("author "):
            authors.add(line.split(" ", 1)[1])
    if len(authors) == 1:
        print(f"WARN: P6-acceptance.md 只有一个 author: {authors.pop()}")
```

### 3.4 .gitignore

无新增。agent 字段在产出文件 Header 内，不产生新文件。

---

## 4. 对三项 Blocked 的解决

| 编号 | 原状态 | 降级方案 | 效果 |
|------|--------|---------|------|
| P2.1 | Blocked（等独立 git author） | Header agent: verifier + phase 序列对照 + dispatch-context 审计 | 主 Agent 不派 verifier → agent=main → gate 不通过。事后篡改留 git diff 痕迹。误导 verifier → dispatch-context 审计拦截 |
| P2.10 | Blocked（等独立 git author） | Header agent: reviewer（risk_level=high 时） | 主 Agent 自审高风险任务 → agent=main → gate 不通过。medium 风险自审 → 警告 |
| P2.6 | Blocked（等独立 git author） | 已由 pre-commit hook + CI backstop 覆盖（hook 覆写 .gate-result.json） | 不依赖 git author。hook 自动跑 gate 写结果，主 Agent 无法伪造而不留痕迹 |

**P2.6 不需要新逻辑**——pre-commit-gate.sh 已经在 commit 前自动跑 gate 并覆写 .gate-result.json，CI backstop 重跑对照。主 Agent 伪造 .gate-result.json 会被 hook 覆盖，`--no-verify` 绕过 hook 会被 CI 暴露。P2.6 的 Blocked 标记可以解除。

---

## 5. 与 Phase 3 的关系

降级方案不是替代 Phase 3，是"先用着，平台支持后升级"：

| 当前（降级方案） | Phase 3（平台支持后） |
|-----------------|---------------------|
| hook 检查 Header agent 字段 | hook 检查 git author |
| 交叉验证：agent + phase 序列 + dispatch-context | 交叉验证：git author + phase 序列 + dispatch-context |
| 伪造成本 > 合规成本（但非不可伪造） | 伪造不可行（git author 由平台控制） |

升级路径：平台支持独立 git author 后，check-agent-provenance.sh 的 `get_agent()` 函数改为从 `git log --format='%an'` 读取，Header agent 字段变为冗余（保留但不作为主要判据）。协议文件不需要改——门槛表述从"agent 字段"变为"产出者身份"，两种实现都满足。

---

## 6. 风险与局限

### 6.1 主 Agent 可以伪造 agent 字段

**风险**：主 Agent 自己写 P6-acceptance.md 时填 `agent: verifier`。

**缓解**：
- 需要同时确保 .state.yaml 的 phase 序列经过 P6（已有 check-state-transition.sh 保证）
- 需要确保 dispatch-context.md 无预判结论（hook 检查）
- 两处同时伪造的成本 > 派一个 verifier subagent
- git diff 留痕迹，CI 可审计

**结论**：不是不可伪造，是伪造成本高于合规成本。这和 pre-commit hook 的 `--no-verify` 绕过同理——绕过需要刻意操作，不是"不知不觉"就绕过了。

### 6.2 subagent 可能忘记写 agent 字段

**风险**：subagent 产出文件时漏掉 agent 字段。

**缓解**：
- dispatch prompt 模板里 Header 是主 Agent 填好的成品，subagent 复制即可
- 主 Agent 派发时已填好 phase/task_id/parent/trace_id/status/created/agent 七个字段
- subagent 只需复制 Header 块，不需要自己填写任何字段
- hook 检查 agent 字段缺失 → exit 1，立即发现

**结论**：风险极低。Header 已是主 Agent 填好的成品，subagent 复制是零认知负担操作。

### 6.3 dispatch-context 审计的误报

**风险**：dispatch-context.md 里合法地出现 `- PASS` 格式的文本（如记录某个历史事件的通过状态）。

**缓解**：
- 检查用 `^\s*- (PASS|FAIL)` 正则，匹配行首的列表格式
- 合法文本通常不是行首列表格式（如"上次发布 PASS 了健康检查"不会匹配）
- 如果确实误报，可以在 dispatch-context.md 里用非列表格式（如"状态：通过"而非"- PASS"）

**结论**：误报概率低，且可通过格式调整避免。

### 6.4 CI git blame 检查的局限

**风险**：P6-acceptance.md 只有一个 author 不一定是问题——可能是主 Agent 做了格式修复。

**缓解**：
- CI 只输出 WARNING，不硬拦截
- WARNING 触发人工审查，审查后可以接受
- 真正的 verifier 产出 + 主 Agent 格式修复 = 两个 author，不会触发 WARNING

**结论**：WARNING 级别合适，不误杀。

---

## 7. 完成标准

- [ ] check-agent-provenance.sh 落地，覆盖 P6 验收 + P2 评审 + dispatch-context 审计 + agent 字段存在性四项检查
- [ ] pre-commit-gate.sh 集成 check-agent-provenance.sh
- [ ] CI backstop 新增 git blame WARNING
- [ ] task-files.md 通用 Header 加 agent 字段
- [ ] dispatch-prompt.md Header 模板加 agent 行
- [ ] dispatch-protocol.md P6 门槛去掉 ⚠️ self-authored，加 provenance 检查
- [ ] state-machine.md P6 转移规则加 provenance 检查
- [ ] WORKFLOW.md P6/P2 行更新
- [ ] hardening-roadmap.md P2.1/P2.6/P2.10 状态从 Blocked 改为降级方案已实现
- [ ] 一致性检查通过（0 ERROR）
