# P2.1/P2.10 降级方案设计 v2：客观行为审计

> 日期：2026-06-30（v1 评审后重写）
> 状态：设计文档
> 关联：docs/hardening-roadmap.md P2.1/P2.10（原 Blocked，待 Phase 3 平台支持）
> 评审：docs/reviews/review-20260630-1949.md
> 核心原则：防护建立在客观、非自报数据上，不把 self-reported 字段当安全边界

---

## 0. v1 评审结论与修正

v1 方案的核心漏洞：**agent 字段是主 Agent 自填的字符串，属于 self-reported 数据。T026 模式下主 Agent 谎填 `agent: verifier` 即可通过全部四层检查。** 评审指出"四层交叉验证"中三层是软的或空的，唯一硬拦截层建立在自报数据上。

v2 的根本修正：

| | v1 | v2 |
|---|---|---|
| 核心机制 | Header agent 字段（自报身份） | 客观行为审计（外部产物 + 内容约束） |
| 防护重心 | "谁写的"（身份验证） | "写了什么 + 外部证据是否支撑"（行为审计） |
| agent 字段定位 | 安全边界 | 协作规范 + Phase 3 铺垫 |
| self-authored 标记 | 去掉 | 保留，注明降级缓解 |
| 对 T026 的实际效力 | 四层全放行 | 至少两层硬拦截 |

---

## 1. 问题（不变）

三项 Blocked 都指向同一个缺口：**无法区分"主 Agent 写的文件"和"subagent 写的文件"**。

| 编号 | 名称 | 威胁 |
|------|------|------|
| P2.1 | P6 验收独立化 | T026：主 Agent 编造 11/16 BDD 结果 |
| P2.10 | P2 评审派发强制 | 3 个保留 P2 任务全 self-approve |
| P2.6 | gate 判定独立化 | 已由 pre-commit hook + CI backstop 覆盖，可解除 Blocked |

**三种攻击场景**：

1. **跳过 subagent**（T026 模式）：主 Agent 不派 verifier subagent，自己直接写 P6-acceptance.md
2. **事后篡改**：主 Agent 派了 subagent，但产出后修改 P6-acceptance.md 的 PASS/FAIL 结果
3. **误导 subagent**：主 Agent 在 dispatch-context.md 里预写验收结论，verifier subagent 被引导到同样结论

---

## 2. 方案：客观行为审计

### 2.1 设计原则

**只信任主 Agent 难以伪造的外部产物，不信任主 Agent 自报的任何字段。**

什么是"难以伪造的外部产物"：
- P6-evidence/ 里的截图文件（Playwright 产出，主 Agent 可伪造但成本高——需要真实浏览器环境生成截图）
- P6-evidence/ 里的 test-output.log（测试运行输出，主 Agent 可伪造但需匹配实际测试框架输出格式）
- P1-requirements.md 的 BDD 条目数（客观计数，不受 P6 作者影响）
- dispatch-context.md 的内容（客观文件内容，hook 可 grep）
- 文件系统状态（产出文件存在/不存在，mtime 关系）

什么是"主 Agent 可轻松伪造的"：
- Header 里的任何字段（一行字）
- .state.yaml 的 phase 值（主 Agent 自己写的）
- dispatch 日志（主 Agent 自己写的）

### 2.2 三道客观审计

#### 审计 1：证据-结论对应（防场景 1 + 场景 2）

**核心逻辑**：P6-acceptance.md 的每条 PASS 必须有对应的证据文件支撑。这不是新概念——check-p6-evidence.sh 已经检查"P6-evidence/ 非空"，但太粗。现在加强为**逐条对应**。

**当前协议已定义的格式**（dispatch-protocol.md P6 派发追加）：

```markdown
- PASS B01: 用户可以创建分享链接（evidences/p6-b01.png）
- PASS B02: MCP publish_files 不传 expires → 实测同样生效
- FAIL B03: 过期链接返回 410
```

括号里的 `evidences/p6-b01.png` 是证据引用。**hook 检查**：

1. P6-acceptance.md 里每个 PASS 行，如果包含证据引用（括号内路径），该路径对应的文件必须存在于 P6-evidence/ 下
2. P6-acceptance.md 的 PASS 条目数 ≤ P6-evidence/ 下的文件数（每条 PASS 至少对应一个证据文件）
3. P6-evidence/ 下的每个文件必须被至少一条 PASS 行引用（防止主 Agent 塞垃圾文件充数）

**为什么这能防 T026**：T026 主 Agent 编造 11/16 BDD 结果时，P6-evidence/ 要么为空（被现有检查拦住），要么是伪造的证据文件。伪造截图需要 Playwright 环境 + 正确的 UI 状态，伪造 test-output.log 需要匹配测试框架输出格式——这些成本远高于填一行 `agent: verifier`。

**局限**：主 Agent 可以伪造证据文件（但成本高），也可以在 PASS 行不写证据引用（但违反 P6 派发追加的格式要求）。hook 检查第 2 条（PASS 数 ≤ 证据文件数）兜底：即使不写引用，证据文件数量也必须足够。

#### 审计 2：dispatch-context 内容约束（防场景 3）

**核心逻辑**：P6 阶段的 dispatch-context.md 不能含验收结论预判。这是 v1 方案里唯一真正有效的检查，原封不动保留。

**hook 检查**：
- P6-dispatch-context.md 存在时，`grep -cE '^\s*- (PASS|FAIL)'` == 0
- 即：dispatch-context 里不能出现 BDD 验收结论格式

**为什么有效**：dispatch-context.md 的内容是客观文件内容，不是主 Agent 对自己身份的声明。主 Agent 可以不创建这个文件（检查跳过），但如果创建了，就不能含预判结论。

**加强**：不只是 P6，所有阶段的 dispatch-context.md 都不能含后续阶段的验收结论格式。但 P6 是最关键的（T026 证据），其他阶段风险低，先只检查 P6。

#### 审计 3：BDD 总数自动化对照（防场景 1）

**核心逻辑**：P6-acceptance.md 的 BDD 结果数必须 = P1-requirements.md 的 BDD 条目数。

**当前状态**：这个对照需要主 Agent 手动核实（check-gate.sh P6 exit 2 的原因之一）。现在尝试自动化。

**难点**：BDD 编号格式不固定（dispatch-protocol.md L570 明确说了）。P1 里的 BDD 可能是 `AC1:` / `B01:` / `BDD-01:` 等各种格式，P6 里是 `- PASS B01: ...`。

**可行方案**：不依赖编号格式，用**行计数**。

1. P1 的 BDD 条目数 = `grep -cE '^\s*-\s+(Given|When|Then)\b' P1-requirements.md`（Given/When/Then 是 BDD 的固定关键词）
2. P6 的 BDD 结果数 = `grep -cE '^\s*- (PASS|FAIL)' P6-acceptance.md`（已有格式）
3. 两者必须相等（或 P6 数 ≥ P1 数，因为 SCOPE+ 可能增补）

**局限**：Given/When/Then 不一定每条 BDD 都有完整三段，可能只有 Given+Then。但 BDD 验收条件的核心是 `Given` 开头——`grep -cE '^\s*-?\s*Given\b'` 作为计数器足够。如果 P1 analyst 没用 Given/When/Then 格式（用了纯列表），这个计数会失败。

**降级处理**：如果 P1 的 Given 计数为 0（非标准格式），hook 输出 WARNING（"P1 BDD 格式非标准，无法自动计数，需主 Agent 手动核实"），不阻塞。这是 v1 评审建议的"诚实标注"——自动化能做多少做多少，做不了的诚实说明。

### 2.3 Header agent 字段（协作规范，非安全边界）

**仍然加上**，但定位改变：

- **定位**：协作规范 + Phase 3 铺垫。提醒主 Agent"这个文件该由谁写"，为 git author 可用时的升级做协议准备。
- **不作为安全边界**：hook 检查 agent 字段缺失（格式校验），但**不依赖 agent 字段值做硬拦截**。
- **软提醒**：risk_level=high 且 P2-review.md 的 agent=main 时输出 WARNING（exit 2，不阻塞）。

### 2.4 T026 攻击在 v2 方案下的实际走向

```
主 Agent 正常走到 P6
  → 不派 verifier subagent，自己写 P6-acceptance.md
  → 谎填 agent: verifier（v1 方案全部放行，v2 不依赖此字段硬拦截）
  → 需要填 N 条 - PASS 行（N = P1 BDD 总数）
  → 需要至少 N 个证据文件在 P6-evidence/ 下

审计 1（证据-结论对应）：
  PASS 数 ≤ 证据文件数 → 需要在 P6-evidence/ 下伪造 N 个文件
  每条含证据引用的 PASS → 引用路径必须真实存在
  → 伪造 N 个截图/test-output → 需要 Playwright 环境 + 正确 UI 状态

审计 2（dispatch-context）：
  不创建 P6-dispatch-context.md → 检查跳过（不拦截）
  但创建时不能含预判结论 → 这层只防误导场景

审计 3（BDD 总数）：
  P6 PASS 数 = P1 Given 数 → 必须逐条填完，不能挑验

agent 字段（协作规范）：
  agent=verifier → WARNING 级别不拦截
  但 CI 层：单 author WARNING → 审计痕迹
```

**v1 vs v2 对比**：

| 攻击 | v1 结果 | v2 结果 |
|------|---------|---------|
| 跳过 verifier 自写 P6，无证据 | P6-evidence/ 为空 → 现有检查拦住 | 同上 |
| 跳过 verifier 自写 P6，伪造空证据 | agent=verifier 放行 | **证据-结论对应拦截**：PASS 引用的文件不存在，或文件数不足 |
| 跳过 verifier 自写 P6，精心伪造全部证据 | agent=verifier 放行 | **成本极高**：N 个截图 + test-output + 引用路径全对 + BDD 总数匹配 + 单 author CI WARNING。比派一个 verifier subagent 贵得多 |
| 误导 verifier | dispatch-context 审计拦截 | 同上 |

**v2 的关键改善**：审计 1（证据-结论对应）是真正基于客观外部产物的硬拦截。主 Agent 要绕过，必须伪造 N 个与真实测试/截图一致的证据文件——这不是填一行字能搞定的。

---

## 3. 具体改动清单

### 3.1 新增脚本

#### 3.1.1 scripts/check-p6-provenance.sh

替代 v1 的 check-agent-provenance.sh。重心从身份验证转向客观审计。

```bash
#!/usr/bin/env bash
# check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
# 基于客观、非自报数据检查 P6 验收的可信度
# exit 0 = 通过; exit 1 = 审计不通过; exit 2 = 警告（不阻塞）

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-provenance.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"
P6_FILE="$TASK_DIR/P6-acceptance.md"
EVIDENCE_DIR="$TASK_DIR/P6-evidence"

# --- 辅助函数 ---

get_agent() {
    local file="$1"
    [ ! -f "$file" ] && echo "" && return
    sed -n '/^---$/,/^---$/p' "$file" | grep -E '^agent:' | sed 's/^agent:\s*//' | head -1
}

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

# --- 审计 1：证据-结论对应 ---
# P6 里每个 PASS 行的证据引用路径必须存在
# PASS 条目数 ≤ 证据文件数
# 证据文件必须被至少一条 PASS 行引用

if [ -f "$P6_FILE" ]; then
    PASS_COUNT=$(grep -cE '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || echo 0)
    PASS_COUNT=$(echo "$PASS_COUNT" | tail -1)

    # 检查 PASS 行里的证据引用是否存在
    MISSING_REFS=0
    while IFS= read -r line; do
        REF=$(echo "$line" | grep -oE '\([^)]+\)' | sed 's/[()]//g' | head -1)
        if [ -n "$REF" ]; then
            # strip P6-evidence/ 前缀（subagent 可能写全路径或相对路径）
            REF_CLEAN=$(echo "$REF" | sed 's|^P6-evidence/||' | sed 's|^p6-evidence/||')
            REF_PATH="$EVIDENCE_DIR/$REF_CLEAN"
            if [ ! -f "$REF_PATH" ]; then
                MISSING_REFS=$((MISSING_REFS + 1))
            fi
        fi
    done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

    if [ "$MISSING_REFS" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 有 ${MISSING_REFS} 条 PASS 引用的证据文件不存在" >&2
        exit 1
    fi

    # PASS 数 ≤ 证据文件数
    if [ -d "$EVIDENCE_DIR" ]; then
        EVIDENCE_COUNT=$(find "$EVIDENCE_DIR" -type f 2>/dev/null | wc -l)
    else
        EVIDENCE_COUNT=0
    fi

    if [ "$PASS_COUNT" -gt "$EVIDENCE_COUNT" ]; then
        echo "GATE PROVENANCE: PASS 条目数(${PASS_COUNT}) > 证据文件数(${EVIDENCE_COUNT})" >&2
        exit 1
    fi

    # 证据文件必须被至少一条 PASS 行引用（防塞垃圾文件充数）
    if [ "$EVIDENCE_COUNT" -gt 0 ] && [ -d "$EVIDENCE_DIR" ]; then
        UNREFERENCED=0
        while IFS= read -r ev_file; do
            ev_basename=$(basename "$ev_file")
            if ! grep -qF "$ev_basename" "$P6_FILE" 2>/dev/null; then
                UNREFERENCED=$((UNREFERENCED + 1))
            fi
        done < <(find "$EVIDENCE_DIR" -type f 2>/dev/null)
        if [ "$UNREFERENCED" -gt 0 ]; then
            echo "GATE PROVENANCE: ${UNREFERENCED} 个证据文件未被 P6-acceptance.md 引用" >&2
            exit 1
        fi
    fi
fi

# --- 审计 2：dispatch-context 内容约束 ---
# P6 阶段的 dispatch-context 不能含验收结论预判

DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"
if [ -f "$DISPATCH_CTX" ]; then
    PREJUDICE=$(grep -cE '^\s*- (PASS|FAIL)' "$DISPATCH_CTX" 2>/dev/null || echo 0)
    PREJUDICE=$(echo "$PREJUDICE" | tail -1)
    if [ "$PREJUDICE" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-dispatch-context.md 含 ${PREJUDICE} 处验收结论预判" >&2
        exit 1
    fi
fi

# --- 审计 3：BDD 总数自动化对照 ---
# P6 的 PASS+FAIL 数 ≥ P1 的 Given 行数（BDD 条目数）

if [ -f "$P6_FILE" ] && [ -f "$P1_FILE" ]; then
    P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)
    P1_BDD=$(echo "$P1_BDD" | tail -1)

    P6_TOTAL=$(grep -cE '^\s*- (PASS|FAIL)' "$P6_FILE" 2>/dev/null || echo 0)
    P6_TOTAL=$(echo "$P6_TOTAL" | tail -1)

    if [ "$P1_BDD" -gt 0 ]; then
        if [ "$P6_TOTAL" -lt "$P1_BDD" ]; then
            echo "GATE PROVENANCE: P6 结果数(${P6_TOTAL}) < P1 BDD 条目数(${P1_BDD})" >&2
            exit 1
        fi
    else
        # P1 BDD 格式非标准，无法自动计数
        echo "GATE PROVENANCE: P1 BDD 格式非标准（无 Given 行），BDD 总数对照需主 Agent 手动核实" >&2
        exit 2
    fi
fi

# --- 协作规范：agent 字段 ---
# 不做硬拦截，只做格式校验和软提醒

if [ -f "$P6_FILE" ]; then
    AGENT=$(get_agent "$P6_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 缺 agent 字段（协作规范）" >&2
        exit 1
    fi
fi

# P2 评审：risk=high 时 agent=main → 警告（软提醒）
P2_REVIEW_FILE="$TASK_DIR/P2-review.md"
if [ -f "$P2_REVIEW_FILE" ]; then
    RISK=$(get_risk_level)
    AGENT=$(get_agent "$P2_REVIEW_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P2-review.md 缺 agent 字段（协作规范）" >&2
        exit 1
    fi
    if [ "$RISK" = "high" ] && [ "$AGENT" = "main" ]; then
        echo "GATE PROVENANCE: risk_level=high 且 P2-review.md agent=main（自审），建议派发独立 reviewer" >&2
        exit 2
    fi
fi

# 所有产出文件必须有 agent 字段（格式校验）
for f in "$TASK_DIR"/P[0-8]-*.md; do
    [ -f "$f" ] || continue
    basename "$f" | grep -q '^P0-' && continue
    AGENT=$(get_agent "$f")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: $(basename "$f") 缺 agent 字段（协作规范）" >&2
        exit 1
    fi
done

exit 0
```

### 3.2 现有脚本改动

#### 3.2.1 scripts/pre-commit-gate.sh

在步骤 5.5（裁剪条件检查）之前插入：

```bash
# 5.4 P6 客观行为审计（P2.1/P2.10 降级方案 v2）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    bash "$REPO_ROOT/scripts/check-p6-provenance.sh" "$TASK_DIR" || {
        EXIT_CODE=$?
        [ "$EXIT_CODE" = "2" ] && echo "GATE PROVENANCE: WARNING（不阻塞）" >&2 || exit 1
    }
fi
```

#### 3.2.2 scripts/check-p6-evidence.sh

现有检查（P6-evidence/ 非空 + BDD 条目计数）与 check-p6-provenance.sh 有重叠。处理方式：
- check-p6-evidence.sh 保留，仍负责 P1.7 的基本检查（证据目录非空）
- check-p6-provenance.sh 做更细粒度的逐条对应检查
- pre-commit-gate.sh 里两者都跑：evidence 先跑（基本门槛），provenance 后跑（深度审计）

#### 3.2.3 scripts/ci-gate-backstop.py

CI backstop 新增 P6 审计：

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

### 3.3 协议文件改动

#### 3.3.1 assets/templates/task-files.md

通用 Header 加 `agent` 字段（协作规范）：

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

P6-acceptance.md 结构更新——证据引用格式强化：

```markdown
- PASS B01: 用户可以创建分享链接（P6-evidence/p6-b01.png）
```

说明：括号内路径相对于 `P6-evidence/` 目录。每条 PASS 的证据引用是 hook 检查的对象。

#### 3.3.2 assets/templates/dispatch-prompt.md

Header 模板加 `agent` 行。关键提醒加一条：
- **agent 字段由主 Agent 填好**：主 Agent 派发时已知角色名，直接填入，subagent 复制即可

P5/P6 派发追加部分更新——证据引用格式要求强化：

```
## P6 证据引用格式
每条 PASS 结果必须在括号内引用对应证据文件路径（相对于 P6-evidence/ 目录）。
示例：- PASS B01: 用户可以创建分享链接（p6-b01.png）
hook 会检查引用路径是否真实存在。无引用的 PASS 行不算有证据。
```

#### 3.3.3 dispatch-protocol.md

**P6→P7 门槛更新**（保留 ⚠️ self-authored）：

原：
```
P6→P7 | BDD 验收通过 ⚠️ self-authored
```

改为：
```
P6→P7 | BDD 验收通过 ⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3）
```

门槛描述加：
```
scripts/check-gate.sh P6 exit 2
+ scripts/check-p6-provenance.sh exit 0 或 exit 2（exit 2 = WARNING，如 BDD 格式非标准需手动核实）
+ 主 Agent 手动核实 BDD 总数（provenance exit 2 时必做，exit 0 时可选）
```

**P5/P6 派发时追加**部分更新——证据引用格式要求。

#### 3.3.4 state-machine.md

P6 转移规则更新（保留 ⚠️ self-authored）：

```
P6 --[scripts/check-gate.sh P6 exit 2 AND scripts/check-p6-provenance.sh exit 0 AND 主 Agent 手动核实 BDD 总数 = P1 BDD 总数]--> P7
     ⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3 平台支持独立 git author）
```

#### 3.3.5 WORKFLOW.md

P1-P8 阶段总览表 P6 行：保留 `⚠️ self-authored`，门槛列加 `check-p6-provenance.sh exit 0`。

P2 行：risk_level=high 时，评审角色列注明"建议派发独立 subagent（agent=reviewer），hook 对 agent=main 输出 WARNING"。

#### 3.3.6 docs/hardening-roadmap.md

P2.1 状态从 "待实现（有平台依赖）" 改为 "降级方案 v2 已设计（客观行为审计），待实现"。

P2.10 状态从 "移除（评审 C1）" 改为 "降级方案 v2 已设计（agent 字段软提醒 + dispatch-context 审计），待实现"。

P2.6 状态：解除 Blocked。已由 pre-commit hook + CI backstop 覆盖。

---

## 4. 对三项 Blocked 的解决

| 编号 | 原状态 | v2 降级方案 | 实际效力 |
|------|--------|-----------|---------|
| P2.1 | Blocked | 证据-结论对应（硬拦截）+ dispatch-context 审计（硬拦截）+ BDD 总数对照（硬/软）+ agent 字段（格式校验） | 跳过 verifier 且无证据 → 拦截。跳过 verifier 且伪造证据 → 成本极高（N 个截图 + test-output + 引用路径）。比 v1 强：v1 四层全放行，v2 至少两层硬拦截 |
| P2.10 | 移除 | agent 字段 WARNING（软）+ dispatch-context 审计（硬） | 高风险自审 → 警告（不阻塞）。误导 reviewer → dispatch-context 拦截。诚实标注：软约束，防君子不防小人 |
| P2.6 | Blocked | 已有 hook + CI 覆盖 | 解除 Blocked |

**诚实标注**：v2 对 T026 的防护不是硬保证——精心伪造全部证据仍可绕过。但 v2 比 v1 强在：
1. 证据-结论对应是客观外部产物的硬拦截，不是自报字段的软拦截
2. 伪造 N 个证据文件的成本远高于填一行 agent: verifier
3. BDD 总数对照自动化减少了"手动核实"这个易被跳过的环节

---

## 5. 与 Phase 3 的关系

| | v2 降级方案 | Phase 3（平台支持后） |
|---|---|---|
| 证据-结论对应 | hook 检查（客观，保留） | 保留（始终有价值） |
| dispatch-context 审计 | hook 检查（客观，保留） | 保留（始终有价值） |
| BDD 总数对照 | 自动化（客观，保留） | 保留（始终有价值） |
| agent 字段 | 协作规范 + 软提醒 | 升级为 git author 硬检查 |
| CI git blame | WARNING | 升级为硬检查（author != 主 Agent） |
| self-authored 标记 | 保留 | 平台支持后去掉 |

v2 的三层客观审计（证据-结论对应 / dispatch-context / BDD 总数）**无论平台是否支持独立 git author 都有价值**——它们检查的是验收质量，不是产出者身份。Phase 3 只需在 v2 基础上加 git author 硬检查，不需要替换 v2 的任何机制。

---

## 6. 风险与局限

### 6.1 主 Agent 可以伪造证据文件

**风险**：主 Agent 自己创建截图和 test-output.log 填充 P6-evidence/。

**缓解**：
- 伪造截图需要 Playwright 环境 + 正确 UI 状态 + 截图间互不重复（P6 派发追加已有 md5 去重要求）
- 伪造 test-output.log 需要匹配测试框架输出格式
- 每条 PASS 引用的证据路径必须真实存在，且每个证据文件必须被引用
- 全部伪造的成本 >> 派一个 verifier subagent

**诚实标注**：这不是硬保证。精心伪造可绕过。但 v2 的拦截效力远高于 v1（v1 四层全放行，v2 至少两层硬拦截基于客观产物）。

### 6.2 P1 BDD 格式非标准时 BDD 总数对照退化为 WARNING

**风险**：P1 analyst 没用 Given/When/Then 格式，grep Given 行数为 0。

**缓解**：
- 退化为 WARNING，需主 Agent 手动核实——和当前一样
- 但给了 incentive：用标准 BDD 格式的 P1 可以自动对照，不用标准的需要手动
- 不阻塞流程，不误杀

### 6.3 证据引用格式不统一

**风险**：subagent 产出 P6 时，证据引用可能不按 `(p6-b01.png)` 格式写。

**缓解**：
- dispatch prompt 模板已明确要求格式
- hook 检查引用路径不存在 → exit 1，立即发现格式问题
- 即使引用格式有偏差（如写全路径 `P6-evidence/p6-b01.png`），hook 也能正确检查

### 6.4 agent 字段 WARNING 对高风险 P2 自审的约束不够

**风险**：risk_level=high 且 P2-review.md agent=main 时只输出 WARNING，不阻塞。

**缓解**：
- 诚实标注：这是软约束
- 当前平台不支持独立 git author，硬拦截 = 100% 卡死所有高风险任务（主 Agent 也无法伪造 reviewer author）
- 软提醒是当前平台限制下的最优选择
- Phase 3 后升级为硬拦截

---

## 7. 完成标准

- [ ] check-p6-provenance.sh 落地，覆盖证据-结论对应 + dispatch-context 审计 + BDD 总数对照 + agent 字段格式校验/软提醒
- [ ] pre-commit-gate.sh 集成 check-p6-provenance.sh
- [ ] CI backstop 新增 git blame WARNING
- [ ] task-files.md 通用 Header 加 agent 字段 + P6 证据引用格式强化
- [ ] dispatch-prompt.md Header 模板加 agent 行 + P6 证据引用格式要求
- [ ] dispatch-protocol.md P6 门槛保留 ⚠️ self-authored + 加 provenance 审计
- [ ] state-machine.md P6 转移规则保留 ⚠️ self-authored + 加 provenance 审计
- [ ] WORKFLOW.md P6/P2 行更新
- [ ] hardening-roadmap.md P2.1/P2.10 状态更新，P2.6 解除 Blocked
- [ ] 一致性检查通过（0 ERROR）
