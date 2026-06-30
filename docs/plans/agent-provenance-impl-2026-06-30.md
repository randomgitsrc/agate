# P2.1/P2.10 客观行为审计 v2 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 P6 验收客观行为审计（证据-结论对应 + dispatch-context 审计 + BDD 总数对照 + agent 字段协作规范），解决 P2.1/P2.10 的 Blocked 状态

**Architecture:** 新增 check-p6-provenance.sh 脚本做三道客观审计 + agent 字段格式校验/软提醒；集成到 pre-commit-gate.sh；CI backstop 加 git blame WARNING；协议文件加 agent 字段 + 保留 ⚠️ self-authored

**Tech Stack:** Bash (hook 脚本), Python (CI backstop), YAML (Header 字段)

**设计文档:** docs/plans/agent-provenance-design-2026-06-30.md

**关键要求:**
- 「空证据拦截」「挑验拦截」必须真能拦
- 「空 png 充数」在文档局限里明确写到 CI WARNING 兜底
- 实现扎实，不走过场

---

## 文件结构

| 操作 | 文件 | 职责 |
|------|------|------|
| 新建 | `scripts/check-p6-provenance.sh` | P6 客观行为审计（证据-结论对应 + dispatch-context + BDD 总数 + agent 字段） |
| 修改 | `scripts/pre-commit-gate.sh` | 集成 check-p6-provenance.sh |
| 修改 | `scripts/ci-gate-backstop.py` | 新增 P6 git blame WARNING |
| 修改 | `assets/templates/task-files.md` | Header 加 agent 字段 + P6 证据引用格式 |
| 修改 | `assets/templates/dispatch-prompt.md` | Header 模板加 agent + 证据引用要求 |
| 修改 | `dispatch-protocol.md` | P6 门槛加 provenance 审计，保留 ⚠️ self-authored |
| 修改 | `state-machine.md` | P6 转移加 provenance，保留 ⚠️ self-authored |
| 修改 | `WORKFLOW.md` | P6/P2 行更新 |
| 修改 | `docs/hardening-roadmap.md` | P2.1/P2.10/P2.6 状态更新 |
| 修改 | `LIMITATIONS.md` | 局限 3 加降级缓解说明 + 空 png 充数局限 |

---

### Task 1: check-p6-provenance.sh — 审计 1 证据-结论对应

**Files:**
- Create: `scripts/check-p6-provenance.sh`

- [ ] **Step 1: 创建脚本骨架 + 审计 1（证据-结论对应）**

```bash
#!/usr/bin/env bash
# check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
# 三道客观审计 + agent 字段协作规范
# exit 0 = 通过; exit 1 = 审计不通过; exit 2 = WARNING（不阻塞）

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
# 1a. PASS 行的证据引用路径必须存在
# 1b. PASS 条目数 ≤ 证据文件数（空证据拦截）
# 1c. 证据文件必须被至少一条 PASS 行引用（空 png 充数拦截）

if [ -f "$P6_FILE" ]; then
    PASS_COUNT=$(grep -cE '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || echo 0)
    PASS_COUNT=$(echo "$PASS_COUNT" | tail -1)

    # 1a: PASS 行里的证据引用路径必须存在
    MISSING_REFS=0
    while IFS= read -r line; do
        REF=$(echo "$line" | grep -oE '\([^)]+\)' | sed 's/[()]//g' | head -1)
        if [ -n "$REF" ]; then
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

    # 1b: PASS 数 ≤ 证据文件数（空证据拦截）
    if [ -d "$EVIDENCE_DIR" ]; then
        EVIDENCE_COUNT=$(find "$EVIDENCE_DIR" -type f 2>/dev/null | wc -l)
    else
        EVIDENCE_COUNT=0
    fi

    if [ "$PASS_COUNT" -gt 0 ] && [ "$EVIDENCE_COUNT" -eq 0 ]; then
        echo "GATE PROVENANCE: 有 ${PASS_COUNT} 条 PASS 但 P6-evidence/ 为空或不存在" >&2
        exit 1
    fi

    if [ "$PASS_COUNT" -gt "$EVIDENCE_COUNT" ]; then
        echo "GATE PROVENANCE: PASS 条目数(${PASS_COUNT}) > 证据文件数(${EVIDENCE_COUNT})" >&2
        exit 1
    fi

    # 1c: 证据文件必须被至少一条 PASS 行引用（空 png 充数拦截）
    if [ "$EVIDENCE_COUNT" -gt 0 ] && [ -d "$EVIDENCE_DIR" ]; then
        UNREFERENCED=0
        while IFS= read -r ev_file; do
            ev_basename=$(basename "$ev_file")
            if ! grep -qF "$ev_basename" "$P6_FILE" 2>/dev/null; then
                UNREFERENCED=$((UNREFERENCED + 1))
            fi
        done < <(find "$EVIDENCE_DIR" -type f 2>/dev/null)
        if [ "$UNREFERENCED" -gt 0 ]; then
            echo "GATE PROVENANCE: ${UNREFERENCED} 个证据文件未被 P6-acceptance.md 引用（可能为充数文件）" >&2
            exit 1
        fi
    fi
fi

exit 0
```

- [ ] **Step 2: chmod +x**

```bash
chmod +x scripts/check-p6-provenance.sh
```

- [ ] **Step 3: 手动测试审计 1**

创建临时测试目录模拟三种场景：

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/P6-evidence"

# 场景 A：PASS 引用不存在的证据 → 应 exit 1
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test (p6-b01.png)
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 A exit=$?"

# 场景 B：PASS 引用存在的证据 → 应 exit 0
touch "$TMPDIR/P6-evidence/p6-b01.png"
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 B exit=$?"

# 场景 C：PASS 数 > 证据文件数 → 应 exit 1
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test (p6-b01.png)
- PASS B02: test2
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 C exit=$?"

# 场景 D：未引用的证据文件（充数）→ 应 exit 1
touch "$TMPDIR/P6-evidence/fake.png"
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 D exit=$?"

rm -rf "$TMPDIR"
```

预期：A=1, B=0, C=1, D=1

- [ ] **Step 4: Commit**

```bash
git add scripts/check-p6-provenance.sh
git commit -m "feat(hardening): check-p6-provenance.sh 审计 1 — 证据-结论对应"
```

---

### Task 2: check-p6-provenance.sh — 审计 2 + 3 + agent 字段

**Files:**
- Modify: `scripts/check-p6-provenance.sh`

- [ ] **Step 1: 追加审计 2（dispatch-context 审计）+ 审计 3（BDD 总数对照）+ agent 字段协作规范**

在现有脚本的 `exit 0` 前追加：

```bash
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
            echo "GATE PROVENANCE: P6 结果数(${P6_TOTAL}) < P1 BDD 条目数(${P1_BDD})，挑验不通过" >&2
            exit 1
        fi
    else
        echo "GATE PROVENANCE: P1 BDD 格式非标准（无 Given 行），BDD 总数对照需主 Agent 手动核实" >&2
        exit 2
    fi
fi

# --- 协作规范：agent 字段 ---
# 不做硬拦截（自报数据不可信），只做格式校验和软提醒

if [ -f "$P6_FILE" ]; then
    AGENT=$(get_agent "$P6_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 缺 agent 字段（协作规范）" >&2
        exit 1
    fi
fi

# P2 评审：risk=high 且 agent=main → 警告
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
```

- [ ] **Step 2: 测试审计 2 — dispatch-context 预判拦截**

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/P6-evidence"
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test (p6-b01.png)
EOF
touch "$TMPDIR/P6-evidence/p6-b01.png"

# 场景 E：dispatch-context 含预判 → exit 1
cat > "$TMPDIR/P6-dispatch-context.md" <<'EOF'
- PASS B01 should pass
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 E exit=$?"

# 场景 F：dispatch-context 无预判 → exit 0
cat > "$TMPDIR/P6-dispatch-context.md" <<'EOF'
debug URL: http://localhost:8888
selector: #root
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 F exit=$?"

rm -rf "$TMPDIR"
```

预期：E=1, F=0

- [ ] **Step 3: 测试审计 3 — BDD 总数对照（挑验拦截）**

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/P6-evidence"
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test (p6-b01.png)
EOF
touch "$TMPDIR/P6-evidence/p6-b01.png"

# 场景 G：P1 有 3 条 BDD，P6 只有 1 条 → 挑验，exit 1
cat > "$TMPDIR/P1-requirements.md" <<'EOF'
- Given user creates entry
- When entry is saved
- Then default expiry is 15 days
- Given user publishes
- When publish is called
- Then link is created
- Given entry expires
- When expired link is accessed
- Then 410 returned
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 G exit=$?"

# 场景 H：P6 条数 >= P1 BDD → exit 0
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test1 (p6-b01.png)
- PASS B02: test2 (p6-b02.png)
- PASS B03: test3 (p6-b03.png)
EOF
touch "$TMPDIR/P6-evidence/p6-b02.png" "$TMPDIR/P6-evidence/p6-b03.png"
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 H exit=$?"

# 场景 I：P1 无 Given 行 → exit 2 (WARNING)
cat > "$TMPDIR/P1-requirements.md" <<'EOF'
BDD 条件：
1. 用户可以创建 entry
2. 默认过期 15 天
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 I exit=$?"

rm -rf "$TMPDIR"
```

预期：G=1, H=0, I=2

- [ ] **Step 4: 测试 agent 字段协作规范**

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/P6-evidence"

# 场景 J：P6 缺 agent 字段 → exit 1
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
---
- PASS B01: test (p6-b01.png)
EOF
touch "$TMPDIR/P6-evidence/p6-b01.png"
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 J exit=$?"

# 场景 K：risk=high + P2 agent=main → exit 2 (WARNING)
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
agent: verifier
---
- PASS B01: test (p6-b01.png)
EOF
cat > "$TMPDIR/P1-requirements.md" <<'EOF'
risk_level: high
- Given test
EOF
cat > "$TMPDIR/P2-review.md" <<'EOF'
---
phase: P2
agent: main
---
status: approved
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "场景 K exit=$?"

rm -rf "$TMPDIR"
```

预期：J=1, K=2

- [ ] **Step 5: Commit**

```bash
git add scripts/check-p6-provenance.sh
git commit -m "feat(hardening): check-p6-provenance.sh 审计 2+3 + agent 字段协作规范"
```

---

### Task 3: pre-commit-gate.sh 集成

**Files:**
- Modify: `scripts/pre-commit-gate.sh:75`

- [ ] **Step 1: 在步骤 5.5（裁剪条件检查）之前插入 provenance 审计**

在 `# 5.5 裁剪条件检查` 行之前插入：

```bash
# 5.4 P6 客观行为审计（P2.1/P2.10 降级方案 v2）
if [ "$GATE_EXIT" != "1" ] && [ -n "$TASK_ID" ] && [ -d "$TASK_DIR" ]; then
    PROV_EXIT=0
    bash "$REPO_ROOT/scripts/check-p6-provenance.sh" "$TASK_DIR" || PROV_EXIT=$?
    if [ "$PROV_EXIT" -eq 1 ]; then
        exit 1
    fi
fi
```

注意：exit 2 (WARNING) 不阻塞 commit，只输出警告。exit 1 硬拦截。

- [ ] **Step 2: 验证 pre-commit-gate.sh 语法**

```bash
bash -n scripts/pre-commit-gate.sh && echo "语法 OK"
```

- [ ] **Step 3: Commit**

```bash
git add scripts/pre-commit-gate.sh
git commit -m "feat(hardening): pre-commit-gate.sh 集成 check-p6-provenance.sh"
```

---

### Task 4: CI backstop — git blame WARNING

**Files:**
- Modify: `scripts/ci-gate-backstop.py:94`

- [ ] **Step 1: 在 `print(f"PASS: ...")` 行之前追加 P6 provenance 审计**

```python
    # P6 provenance audit (CI layer)
    # 单 author WARNING：空 png 充数等场景的兜底审计
    if task_dir:
        p6_file = Path(task_dir) / "P6-acceptance.md"
        if p6_file.exists():
            try:
                blame = subprocess.run(
                    ["git", "blame", "--line-porcelain", str(p6_file)],
                    capture_output=True, text=True
                )
                authors = set()
                for line in blame.stdout.splitlines():
                    if line.startswith("author "):
                        authors.add(line.split(" ", 1)[1])
                if len(authors) == 1:
                    print(f"WARN: P6-acceptance.md 只有一个 author: {authors.pop()}（可能为主 Agent 自写，建议审查证据真实性）")
            except Exception as e:
                print(f"WARN: P6 git blame 审计无法完成（{e}）")
```

- [ ] **Step 2: 验证 Python 语法**

```bash
python3 -m py_compile scripts/ci-gate-backstop.py && echo "语法 OK"
```

- [ ] **Step 3: Commit**

```bash
git add scripts/ci-gate-backstop.py
git commit -m "feat(hardening): CI backstop P6 git blame WARNING — 空 png 充数兜底"
```

---

### Task 5: 协议文件 — Header agent 字段 + 证据引用格式

**Files:**
- Modify: `assets/templates/task-files.md`
- Modify: `assets/templates/dispatch-prompt.md`

- [ ] **Step 1: task-files.md 通用 Header 加 agent 字段**

在通用 Header 的 `created:` 行后加一行：

```yaml
agent: {main|analyst|architect|reviewer|test-designer|implementer|verifier}
```

在 P6-acceptance.md 结构部分，证据引用格式强化说明：

在 `- PASS B01: 用户可以创建分享链接（evidences/p6-ac1.png）` 行后加注释：

```markdown
（括号内为证据文件引用，路径相对于 P6-evidence/ 目录。hook 检查引用路径必须真实存在。无引用的 PASS 不算有证据。）
```

- [ ] **Step 2: dispatch-prompt.md Header 模板加 agent 行**

在 Header 模板的 `created:` 行后加：

```
agent: {角色名}
```

在关键提醒部分追加一条：

```
- **agent 字段由主 Agent 填好**：主 Agent 派发时已知角色名，直接填入，subagent 复制即可
```

在 P5/P6 派发追加部分，`## P6 证据要求` 节末尾追加：

```
## P6 证据引用格式
每条 PASS 结果必须在括号内引用对应证据文件路径（相对于 P6-evidence/ 目录）。
示例：- PASS B01: 用户可以创建分享链接（p6-b01.png）
hook 会检查引用路径是否真实存在。无引用的 PASS 行不算有证据。
```

- [ ] **Step 3: Commit**

```bash
git add assets/templates/task-files.md assets/templates/dispatch-prompt.md
git commit -m "feat(hardening): Header agent 字段 + P6 证据引用格式强化"
```

---

### Task 6: 协议文件 — 门槛/转移/WORKFLOW 更新

**Files:**
- Modify: `dispatch-protocol.md`
- Modify: `state-machine.md`
- Modify: `WORKFLOW.md`

- [ ] **Step 1: dispatch-protocol.md — P6 门槛更新**

找到 P6→P7 行（约 L575），将 `⚠️ self-authored` 改为 `⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3）`。

在门槛描述中，P6 部分追加 provenance 审计：

找到 P6 门槛描述行，在 `scripts/check-gate.sh P6` 后追加 `AND scripts/check-p6-provenance.sh exit 0 或 exit 2 AND 主 Agent 手动核实 BDD 总数（provenance exit 2 时必做）`。

在 P5/P6 派发时追加部分，确认证据引用格式要求已加入（Task 5 已处理）。

- [ ] **Step 2: state-machine.md — P6 转移规则更新**

找到 P6 转移行（约 L114），在 `scripts/check-gate.sh P6 exit 2` 后追加 `AND scripts/check-p6-provenance.sh exit 0`。

在行末追加 `⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3 平台支持独立 git author）`。

- [ ] **Step 3: WORKFLOW.md — P6/P2 行更新**

P1-P8 阶段总览表 P6 行：门槛列追加 `check-p6-provenance.sh exit 0`，保留 `⚠️ self-authored`。

P2 行评审角色列：risk_level=high 时注明"建议派发独立 subagent（agent=reviewer），hook 对 agent=main 输出 WARNING"。

- [ ] **Step 4: Commit**

```bash
git add dispatch-protocol.md state-machine.md WORKFLOW.md
git commit -m "feat(hardening): P6 门槛加 provenance 审计，保留 self-authored 标记"
```

---

### Task 7: hardening-roadmap.md + LIMITATIONS.md 状态更新

**Files:**
- Modify: `docs/hardening-roadmap.md`
- Modify: `LIMITATIONS.md`

- [ ] **Step 1: hardening-roadmap.md 状态更新**

P2.1 行：状态从 `待实现（有平台依赖，见下）` 改为 `降级方案 v2 已实现（客观行为审计：证据-结论对应 + dispatch-context 审计 + BDD 总数对照）`。

P2.10 行：状态从 `**移除**（评审 C1：...）` 改为 `降级方案 v2 已实现（agent 字段软提醒 + dispatch-context 审计，硬拦截待 Phase 3 平台支持独立 git author）`。

P2.6 行：确认已标注为 `**移除**`（评审：hook 无法验证 full run vs partial run，属流程层规则），解除 Blocked。

- [ ] **Step 2: LIMITATIONS.md — 局限 3 加降级缓解 + 空 png 充数局限**

找到局限 3 部分，追加降级缓解说明：

```markdown
**降级缓解（v2 客观行为审计）**：
- P6 验收：证据-结论对应（hook 检查每条 PASS 有证据文件且被引用）+ BDD 总数对照 + dispatch-context 审计
- P2 评审：agent 字段软提醒（risk=high 自审 → WARNING）
- 已知局限：主 Agent 可伪造证据文件（如空 png 充数），但成本远高于填一行自报字段。CI git blame WARNING 作为兜底审计。
- 根治：Phase 3 平台支持独立 git author 后，agent 字段升级为 git author 硬检查。
```

- [ ] **Step 3: Commit**

```bash
git add docs/hardening-roadmap.md LIMITATIONS.md
git commit -m "docs(hardening): P2.1/P2.10 降级方案 v2 状态更新 + LIMITATIONS 局限 3 缓解说明"
```

---

### Task 8: 一致性检查 + 端到端验证

**Files:**
- (无新文件)

- [ ] **Step 1: 跑协议一致性检查**

```bash
python3 scripts/check-protocol-consistency.py
```

预期：0 ERROR（WARNING 可接受）。

- [ ] **Step 2: 端到端验证 — 模拟完整 P6 provenance 检查流程**

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/P6-evidence/screenshots"

# 合规场景：P1 有 2 条 BDD，P6 有 2 条 PASS + 2 个证据 + 证据被引用 + agent=verifier
cat > "$TMPDIR/P1-requirements.md" <<'EOF'
risk_level: medium
- Given user creates entry
- When saved
- Then default expiry is 15 days
- Given user publishes
- When publish called
- Then link created
EOF
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T999
agent: verifier
---
- PASS B01: 创建 entry 默认 15 天过期 (screenshots/b01.png)
- PASS B02: publish 创建链接 (screenshots/b02.png)
EOF
touch "$TMPDIR/P6-evidence/screenshots/b01.png" "$TMPDIR/P6-evidence/screenshots/b02.png"

bash scripts/check-p6-provenance.sh "$TMPDIR"
echo "合规场景 exit=$?"

# 违规场景 1：空证据（P6-evidence/ 为空）
rm -rf "$TMPDIR/P6-evidence"
mkdir -p "$TMPDIR/P6-evidence"
bash scripts/check-p6-provenance.sh "$TMPDIR" 2>/dev/null
echo "空证据 exit=$?"

# 恢复
rm -rf "$TMPDIR/P6-evidence"
mkdir -p "$TMPDIR/P6-evidence/screenshots"
touch "$TMPDIR/P6-evidence/screenshots/b01.png" "$TMPDIR/P6-evidence/screenshots/b02.png"

# 违规场景 2：挑验（P6 只有 1 条，P1 有 2 条 Given）
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T999
agent: verifier
---
- PASS B01: 创建 entry 默认 15 天过期 (screenshots/b01.png)
EOF
bash scripts/check-p6-provenance.sh "$TMPDIR" 2>/dev/null
echo "挑验 exit=$?"

# 违规场景 3：空 png 充数（多一个未引用的证据文件）
cat > "$TMPDIR/P6-acceptance.md" <<'EOF'
---
phase: P6
task_id: T999
agent: verifier
---
- PASS B01: 创建 entry (screenshots/b01.png)
- PASS B02: 发布链接 (screenshots/b02.png)
EOF
touch "$TMPDIR/P6-evidence/screenshots/fake.png"
bash scripts/check-p6-provenance.sh "$TMPDIR" 2>/dev/null
echo "空 png 充数 exit=$?"

rm -rf "$TMPDIR"
```

预期：合规=0, 空证据=1, 挑验=1, 空 png 充数=1

- [ ] **Step 3: 最终 commit + push**

```bash
git push
```

---

### Task 9: 评审

- [ ] **Step 1: 自评审 — 逐项检查完成标准**

对照设计文档第 7 节完成标准逐项确认：

- [ ] check-p6-provenance.sh 落地，覆盖证据-结论对应 + dispatch-context 审计 + BDD 总数对照 + agent 字段格式校验/软提醒
- [ ] pre-commit-gate.sh 集成 check-p6-provenance.sh
- [ ] CI backstop 新增 git blame WARNING
- [ ] task-files.md 通用 Header 加 agent 字段 + P6 证据引用格式强化
- [ ] dispatch-prompt.md Header 模板加 agent 行 + 证据引用格式要求
- [ ] dispatch-protocol.md P6 门槛保留 ⚠️ self-authored + 加 provenance 审计
- [ ] state-machine.md P6 转移规则保留 ⚠️ self-authored + 加 provenance 审计
- [ ] WORKFLOW.md P6/P2 行更新
- [ ] hardening-roadmap.md P2.1/P2.10/P2.6 状态更新
- [ ] 一致性检查通过（0 ERROR）

- [ ] **Step 2: 写评审记录**

```bash
# 评审记录写入 docs/reviews/ 目录，记录实测结果和发现的问题
```
