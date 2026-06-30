# T045 评审 v5 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落实 T045 评审 v5（`docs/reviews/review-20260701-t045-lessons.md`）的 R1-R5 建议，把"形式合规"升级为"实质合规"——用客观证据 barrier 堵住 T045 暴露的 P6 验收逃逸点 + 补实现裁剪层 bug fix + 加自报 nudge。

**Architecture:** 分 3 层改动：(1) 协议模板格式定义（先定格式再写 hook）；(2) hook 脚本实现（客观证据检查 + bug fix + nudge check）；(3) 协议文档同步。每层独立可测试、可 commit。

**Tech Stack:** Bash（hook 脚本）、Python（YAML 解析）、Markdown（协议文档）

**来源评审：** `docs/reviews/review-20260701-t045-lessons.md` v5

**优先级排序（评审 v5 建议）：**
1. R4(a) 补实现文件数检查——纯 bug fix，修复一年未生效的规则
2. R1(a) 截图 > 1KB——最低成本堵住 T045 核心逃逸点
3. R1(b) vision YAML hook 化——需先确认格式
4. R2/R3/R5——需先定模板格式

---

## 文件结构

| 文件 | 改动类型 | 负责的 R# |
|------|---------|----------|
| `agate/assets/templates/task-files.md` | 修改：补 P5 e2e.md 格式 + P6 screenshots/ 约定 + P6 vision YAML 引用格式 | R1/R2 前置 |
| `agate/scripts/check-pruning.sh` | 修改：补 P7 文件数检查 + P7 shared_styles + P8 internal_only + 裁剪风险评估 | R3/R4/R5 |
| `agate/scripts/check-p6-evidence.sh` | 修改：UI 截图 > 1KB 检查 | R1(a) |
| `agate/scripts/check-p6-provenance.sh` | 修改：审计 4 vision YAML 引用检查 | R1(b) |
| `agate/state-machine.md` | 修改：裁剪条件表更新 P7 条件 + P8 条件 + 裁剪理由格式 | R3/R4/R5 |
| `agate/WORKFLOW.md` | 修改：P6 行加 vision YAML hook + P7 语义澄清 | R1/R3 |
| `agate/dispatch-protocol.md` | 修改：门槛表 P6→P7 同步 vision YAML hook | R1 |
| `agate/assets/execution-roles/verifier.md` | 修改："脚本已写≠验证完成"约束 | R1 附 |

---

## Task 1: 协议模板格式定义（R1/R2 前置）

**Files:**
- Modify: `agate/assets/templates/task-files.md:34-35,243`

评审 v5 补充 3：先定协议格式、再写检查脚本。

- [ ] **Step 1: 补 P5 e2e.md 格式约定**

Read `agate/assets/templates/task-files.md`，找到 line 34 的 e2e.md 行，在末尾加 `。须含 status: passed 字段（hook 检查）`。

- [ ] **Step 2: 补 P6 screenshots/ 目录约定 + vision YAML 引用格式**

找到 line 243（证据引用格式段），在其后追加 UI 任务证据追加约定段：

```
**UI 任务证据追加约定**（`ui_affected: true` 时）：
- `P6-evidence/screenshots/` 目录必须非空，每个截图文件大小 > 1KB（防空 png 充数，hook 检查）
- 每条 UI 类 PASS 必须含 vision-analyst YAML 引用：`- PASS B01: ... (screenshots/b01.png) (vision: vision-reports/b01.yaml)`
- vision YAML 文件必须存在且 `summary.blocker_count == 0`（hook 检查）
- vision YAML 格式见 `assets/execution-roles/vision-analyst.md` 的完整 YAML 结构
```

- [ ] **Step 3: 验证一致性检查通过**

Run: `python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -5`
Expected: `仅有 19 个 WARNING，无 ERROR。`

- [ ] **Step 4: Commit**

```bash
git add agate/assets/templates/task-files.md
git commit -m "docs: task-files.md 补 P5 e2e.md status 字段 + P6 screenshots/vision YAML 引用格式约定

T045 评审 v5 R1/R2 前置：先定协议格式再写 hook"
```

---

## Task 2: check-p6-evidence.sh 增加 UI 截图实质检查（R1a）

**Files:**
- Modify: `agate/scripts/check-p6-evidence.sh`

R1(a)：`ui_affected: true` 时，P6-evidence/screenshots/ 必须非空 + 每个截图文件大小 > 1KB。客观证据 barrier——文件大小是文件系统级属性，subagent 无法靠"再写一行文本"绕过。

- [ ] **Step 1: 在脚本末尾 exit 0 之前加 UI 检查逻辑**

在 `echo "GATE P6-EVIDENCE: ${BDD_COUNT} 条 BDD，证据目录非空" >&2` 之前插入：

```bash
# UI 截图实质检查（R1a：T045 评审 v5）
P2_FILE="$TASK_DIR/P2-design.md"
UI_AFFECTED=""
if [ -f "$P2_FILE" ]; then
    UI_AFFECTED=$(P2_FILE="$P2_FILE" python3 -c "
import re, os
with open(os.environ['P2_FILE']) as f:
    text = f.read()
m = re.search(r'ui_affected:\s*(true|false)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
fi

if [ "$UI_AFFECTED" = "true" ]; then
    SCREENSHOTS_DIR="$EVIDENCE_DIR/screenshots"
    if [ ! -d "$SCREENSHOTS_DIR" ] || [ -z "$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' 2>/dev/null)" ]; then
        echo "GATE P6-EVIDENCE: ui_affected=true 但 P6-evidence/screenshots/ 目录不存在或为空" >&2
        exit 1
    fi
    EMPTY_COUNT=0
    while IFS= read -r -d '' img; do
        SIZE=$(stat -c%s "$img" 2>/dev/null || stat -f%z "$img" 2>/dev/null || echo 0)
        if [ "$SIZE" -le 1024 ]; then
            EMPTY_COUNT=$((EMPTY_COUNT + 1))
        fi
    done < <(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -print0 2>/dev/null)
    if [ "$EMPTY_COUNT" -gt 0 ]; then
        echo "GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 ${EMPTY_COUNT} 个文件 ≤ 1KB（疑似空 png 充数）" >&2
        exit 1
    fi
fi
```

- [ ] **Step 2: 语法检查**

Run: `bash -n agate/scripts/check-p6-evidence.sh`
Expected: 无输出

- [ ] **Step 3: 测试——非 UI 任务不受影响**

创建临时任务目录，无 P2-design.md（非 UI 任务），跑脚本应 exit=0。

- [ ] **Step 4: 测试——UI 任务空 screenshots 被拦截**

创建 P2-design.md 含 `ui_affected: true`，不建 screenshots/ 目录，应 exit=1。

- [ ] **Step 5: 测试——UI 任务空 png 被拦截**

创建 screenshots/ + 100 字节假 png，应 exit=1。

- [ ] **Step 6: 测试——UI 任务合规通过**

创建 screenshots/ + 2KB 假 png，应 exit=0。

- [ ] **Step 7: Commit**

```bash
git add agate/scripts/check-p6-evidence.sh
git commit -m "feat(hardening): check-p6-evidence.sh 增加 UI 截图实质检查（R1a）

ui_affected=true 时 screenshots/ 非空 + 每个截图 > 1KB
客观证据 barrier——文件大小是文件系统级属性，subagent 无法靠文本绕过
T045 评审 v5 R1(a)"
```

---

## Task 3: check-p6-provenance.sh 审计 4 vision YAML 引用（R1b）

**Files:**
- Modify: `agate/scripts/check-p6-provenance.sh`

R1(b)：将 `dispatch-protocol.md:575` 已有的 UI vision 规则 hook 化。`ui_affected: true` 时，每条 UI 类 PASS 必须含 `(vision: vision-reports/*.yaml)` 引用 + YAML 文件存在 + `summary.blocker_count == 0`。

- [ ] **Step 1: 在审计 3 之后、agent 字段之前加审计 4**

找到 `# --- 协作规范：agent 字段 ---` 行，在其前面插入审计 4 代码块。代码逻辑：
1. 读取 P2-design.md 的 `ui_affected` 字段
2. `ui_affected: true` 时，检查每条 PASS 行含 `(vision: ...)` 引用
3. 检查每个 vision YAML 文件存在 + `summary.blocker_count == 0`（用 python3 + pyyaml 解析）
4. 任何一项不通过 → exit 1

- [ ] **Step 2: 语法检查**

Run: `bash -n agate/scripts/check-p6-provenance.sh`

- [ ] **Step 3: 测试——非 UI 任务不受影响**

无 P2-design.md 或 `ui_affected: false`，应 exit=0。

- [ ] **Step 4: 测试——UI 任务缺 vision 引用被拦截**

`ui_affected: true` + PASS 行无 `(vision: ...)`，应 exit=1。

- [ ] **Step 5: 测试——UI 任务 blocker_count != 0 被拦截**

PASS 行有 vision 引用 + YAML 存在但 `blocker_count: 1`，应 exit=1。

- [ ] **Step 6: 测试——UI 任务全合规通过**

PASS 行有 vision 引用 + YAML 存在 + `blocker_count: 0`，应 exit=0。

- [ ] **Step 7: Commit**

```bash
git add agate/scripts/check-p6-provenance.sh
git commit -m "feat(hardening): check-p6-provenance.sh 审计 4 — UI vision YAML 引用检查（R1b）

将 dispatch-protocol.md:575 已有规则 hook 化
ui_affected=true 时每条 UI PASS 须 vision YAML 引用 + blocker_count==0
客观证据 barrier——blocker_count 是 vision-analyst 产出的客观值
T045 评审 v5 R1(b)"
```

---

## Task 4: check-pruning.sh 补 P7/P8 裁剪条件 + 裁剪风险评估（R3/R4/R5）

**Files:**
- Modify: `agate/scripts/check-pruning.sh`
- Modify: `agate/state-machine.md:163-167`

这是最大的 Task。R4(a) 是纯 bug fix（state-machine 文档了"文件数 ≤ 5"但 hook 从未实现），R4(b)/R5(a) 是自报 nudge，R3(a) 是自报 nudge。

- [ ] **Step 1: 在 check-pruning.sh 检查 4 之后、P2.9 之前插入 P7/P8/风险评估检查**

插入 3 个新检查块：
- 检查 5（R4）：P7 裁剪条件——源码文件数 > 5 → 不可跳 + shared_styles 声明 → 不可跳
- 检查 6（R5）：P8 裁剪条件——需 `internal_only: true` 声明
- 检查 7（R3）：裁剪理由含"跳过风险:"评估

源码文件数 = `git diff --name-only HEAD~1` 排除 `docs/tasks/`、`.state.yaml`、`P{n}-*.md`、隐藏文件。

- [ ] **Step 2: 语法检查**

Run: `bash -n agate/scripts/check-pruning.sh`

- [ ] **Step 3: 测试——P7 文件数 > 5 被拦截**

创建 7 个源码文件 + P1 声明裁剪 P7，应 exit=1。

- [ ] **Step 4: 测试——P8 缺 internal_only 被拦截**

P1 声明裁剪 P8 但缺 `internal_only: true`，应 exit=1。

- [ ] **Step 5: 测试——裁剪缺"跳过风险"被拦截**

P1 有裁剪声明但无"跳过风险:"字样，应 exit=1。

- [ ] **Step 6: 测试——全合规通过**

P1 含裁剪理由 + 跳过风险 + `internal_only: true` + 文件数 ≤ 5，应 exit=0。

- [ ] **Step 7: 更新 state-machine.md 裁剪条件表**

将"裁剪 P7：需改动文件数 ≤ 5"改为"裁剪 P7：需源码文件数 ≤ 5 AND 无 shared_styles 声明"；加"裁剪 P8：需声明 internal_only: true"；加裁剪理由格式段 + P7 语义澄清段。

- [ ] **Step 8: 一致性检查**

Run: `python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -5`
Expected: 0 ERROR

- [ ] **Step 9: Commit**

```bash
git add agate/scripts/check-pruning.sh agate/state-machine.md
git commit -m "feat(hardening): check-pruning.sh 补 P7/P8 裁剪条件 + 裁剪风险评估（R3/R4/R5）

R4(a) bug fix：补实现 state-machine.md 文档化的 P7 文件数 ≤ 5 条件（一年未生效）
R4(b)：加 shared_styles 隐式耦合维度（self-declaration nudge，标注局限）
R5(a)：P8 裁剪需 internal_only: true 声明
R3(a)：裁剪理由含'跳过风险:'评估（self-declaration nudge）
R3(b)：P7 语义澄清——'实现 vs 设计'不是'是否跨端'
T045 评审 v5 R3/R4/R5"
```

---

## Task 5: 协议文档同步（R1/R2/R3 文档层）

**Files:**
- Modify: `agate/WORKFLOW.md` P6 行 + P8 行
- Modify: `agate/dispatch-protocol.md` 门槛表 P6→P7 + P8→READY
- Modify: `agate/assets/execution-roles/verifier.md` 加"脚本已写≠验证完成"约束

- [ ] **Step 1: WORKFLOW.md P6 行加 R1a/R1b hook 标注**

P6 门槛列加 `check-p6-evidence.sh UI 截图 > 1KB（R1a 客观证据 barrier）` + `provenance 审计 4 UI vision YAML [R1b hook 化]`。

- [ ] **Step 2: WORKFLOW.md P8 行加 internal_only 标注**

P8 门槛列加 `check-pruning.sh 验证 internal_only 声明`。

- [ ] **Step 3: dispatch-protocol.md 门槛表同步**

P6→P7 门槛加 R1a/R1b 标注；P8→READY 门槛加 internal_only 标注。

- [ ] **Step 4: verifier.md 加"脚本已写≠验证完成"约束**

在 P6 验收模式的输出段后加约束："脚本已写不等于验证完成——主 Agent 必须确认脚本被实跑"。

- [ ] **Step 5: 一致性检查**

Run: `python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -5`
Expected: 0 ERROR

- [ ] **Step 6: Commit**

```bash
git add agate/WORKFLOW.md agate/dispatch-protocol.md agate/assets/execution-roles/verifier.md
git commit -m "docs: 协议文档同步 T045 评审 v5 — P6/P8 门槛表 + verifier 约束

WORKFLOW.md P6 行加 R1a/R1b hook 标注
WORKFLOW.md P8 行加 internal_only 标注
dispatch-protocol.md 门槛表同步
verifier.md 加'脚本已写≠验证完成'约束
T045 评审 v5 文档同步"
```

---

## Task 6: 端到端验证

- [ ] **Step 1: 所有 bash 脚本语法检查**

```bash
for f in agate/scripts/*.sh; do bash -n "$f" && echo "OK: $f"; done
```

- [ ] **Step 2: 所有 Python 脚本语法检查**

```bash
for f in agate/scripts/*.py; do python3 -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f"; done
```

- [ ] **Step 3: 一致性检查**

Run: `python3 agate/scripts/check-protocol-consistency.py 2>&1 | tail -5`
Expected: 0 ERROR

- [ ] **Step 4: 软链接访问验证**

```bash
bash /home/kity/.agate/scripts/agate-summary.sh | head -5
```

- [ ] **Step 5: Pre-commit 检查总览表更新（WORKFLOW.md）**

确认 WORKFLOW.md 的 Pre-commit 检查总览表已含 R1a/R1b 新增检查项。

- [ ] **Step 6: Final commit（如有遗漏修复）+ push**

```bash
git push
```

---

## Self-Review

### Spec coverage

| 评审建议 | 对应 Task |
|---------|----------|
| R1(a) 截图 > 1KB | Task 2 |
| R1(b) vision YAML hook 化 | Task 3 |
| R2(a) P2 gate 强制 E2E 声明 | Task 5（文档层标注，hook 实现需 P2-design.md gate_commands 解析，复杂度高，标记为 Phase 2） |
| R2(b) P5 冒烟降级 WARNING | Task 5（文档层标注，hook 实现标记为 Phase 2） |
| R3(a) 裁剪理由含"跳过风险" | Task 4 |
| R3(b) P7 语义澄清 | Task 4 Step 7 + Task 5 |
| R4(a) 补实现文件数检查 | Task 4 |
| R4(b) shared_styles 维度 | Task 4 |
| R4(c) 条件合并 | Task 4 Step 7 |
| R5(a) internal_only 声明 | Task 4 |
| R5(b) P8 风险评估 | Task 4（统一于 R3a） |
| R6 minimal_validation | 不实施（项目侧执行改进，非协议本体） |

### Phase 2 标记

R2(a) P2 gate 强制 E2E 声明 和 R2(b) P5 冒烟 WARNING 需要：
- P2-design.md 的 `gate_commands.P5` 字段解析（复杂 YAML 解析）
- P5-test-results/e2e.md 的 `status: passed` 检查

这两个在 Task 1 定义了格式约定，但 hook 实现标记为 Phase 2——因为 `gate_commands` 解析涉及 `check-gate.sh` 改动（需要从 P2 读取命令并验证含 E2E 字样），范围较大。v0.5.1 先落地 R1/R3/R4/R5，R2 在 v0.5.2 跟进。

### Placeholder scan

无 TBD/TODO。所有代码块完整。测试步骤有预期 exit code。

### Type consistency

- `ui_affected` 字段读取：Task 2 和 Task 3 都用相同的 Python regex `r'ui_affected:\s*(true|false)'` ✓
- `shared_styles` 字段：Task 4 检查和 state-machine.md 文档一致 ✓
- `internal_only` 字段：Task 4 检查和 state-machine.md 文档一致 ✓
- `blocker_count` 路径：Task 3 用 `vision_analysis.summary.blocker_count`，与 vision-analyst.md YAML 结构一致 ✓
