# 阶段卡片措辞加固 — 消除 agent 可钻空子 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过纯措辞修改消除阶段卡片中"可被合理化绕过"的模糊地带，让 agent 无脑遵循而非动脑筋钻空子。不改 gate 脚本逻辑。

**Architecture:** 三类修改：(1) 推进条件补全为显式 AND checklist，把 gate 不覆盖但必须做的项列进去；(2) 消灭"可选"/"若有触发"/"若方案依赖"等模糊措辞，改为条件触发的客观判定；(3) 统一"亲自执行"的定义，区分"派 subagent 产出"和"主 Agent 跑 gate 验证"。

**Tech Stack:** Markdown（协议文档），Bash（gate 脚本 P2 硬检查），Bats（测试）

---

## 背景

### 问题

T082 复盘发现 agent 在 P4 跳过了评审，理由是"gate exit 0 = 阶段通过"。审计发现每个阶段卡片都有类似空子：

1. **推进条件 ≠ gate 规则**：推进条件是阶段完成的完整定义，gate 脚本只检查机器可判定的子集。但卡片没明确区分二者关系，agent 把"gate 通过"等同于"可以推进"。
2. **模糊措辞给解读空间**："可选"/"若有触发"/"若方案依赖"等措辞让 agent 自行判断"不需要做"。
3. **"亲自执行"含义混淆**：P4 卡片说"P5 由主 Agent 亲自执行"，P5 卡片说"派发 verifier subagent 执行"——agent 选对自己有利的解读。

### 设计原则

- **不增加 agent 额外思考负担**：checklist 是无脑打勾的，不是让 agent 判断"该不该做"
- **不给 agent 动脑筋的空间**：凡是写"若"/"可选"/"可以考虑"的地方，要么改为客观触发条件，要么删除
- **不增加新 gate 脚本**：只改措辞，让现有规则无歧义（P2 review 文件存在性硬检查除外，这是 bug fix）
- **前后传播分析**：每个修改标注受影响的下游文件

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `agate/phase-cards/P0-orchestrator.md` | 修改 | 推进条件补全 + 模糊措辞消除 |
| `agate/phase-cards/P1-requirements.md` | 修改 | 推进条件补全 P1-review.md |
| `agate/phase-cards/P2-design.md` | 修改 | gate 规则消除"文件存在时检查" + design_trivial 须附理由 + 推进条件补全 |
| `agate/phase-cards/P3-tdd.md` | 修改 | "可选"→"条件触发" + 环境基线"必须执行" |
| `agate/phase-cards/P4-implementation.md` | 修改 | "若有触发"→"按 C8 映射" + "必要评审"→"C8 映射" + "P5 亲自执行"措辞修正 + "可选"→"条件触发" |
| `agate/phase-cards/P5-verification.md` | 修改 | "可选"→"条件触发" + 签名校验"必须" + 全量测试措辞 |
| `agate/phase-cards/P6-acceptance.md` | 修改 | "先验证功能再满足格式"消除先后暗示 + "亲自执行验收"明确为跑 gate 脚本 |
| `agate/phase-cards/P7-consistency.md` | 修改 | "可选"→"条件触发" |
| `agate/phase-cards/P8-release.md` | 修改 | "手动确认"→"必须亲自执行" + 收尾清单"必须实际执行命令" |
| `agate/scripts/check-gate.sh` | 修改 | P2 review 文件不存在时 exit 1（bug fix） |
| `agate/dispatch-protocol.md` | 修改 | P2 最小验证措辞同步 + P4 迭代表"可选"→"C8 映射触发" + P6 自查节同步 |
| `agate/assets/templates/dispatch-prompt.md` | 修改 | P2 最小验证措辞同步 |
| `agate/assets/templates/task-files.md` | 修改 | P2 最小验证措辞同步 |
| `agate/role-system.md` | 修改 | C8 映射表"业务方向不明"客观化 |
| `agate/rules/review-mapping.md` | 修改 | C8 映射表"业务方向不明"客观化 |
| `agate/assets/execution-roles/architect.md` | 修改 | minimal_validation 强制声明措辞同步 |
| `agate/assets/review-roles/plan-eng-review.md` | 修改 | minimal_validation 检查措辞同步 |
| `agate/tests/unit/check-gate.bats` | 修改 | 新增 P2 review 不存在时 exit 1 测试 + 修改 G2.13 |

---

## Task 1: check-gate.sh P2 review 文件存在性硬检查

**Files:**
- Modify: `agate/scripts/check-gate.sh:100-116`（P2 review 检查逻辑）
- Test: `agate/tests/unit/check-gate.bats`

### 背景

当前 `check-gate.sh` P2 分支 L101 用 `if [ -f "$P2_REVIEW" ]`，文件不存在时跳过评审检查。这意味着 agent 不创建 P2-review.md 就能过 gate——绕过了 P2 评审不可裁剪的协议意图。这是 bug fix，不是新功能。

### 步骤

- [ ] **Step 1: 写失败测试 — P2 review 不存在时期望 exit 1**

在 `agate/tests/unit/check-gate.bats` 中新增测试：

```bash
@test "PG.P2REVIEW: P2-review.md not found → exit 1" {
    local task_dir="$BATS_TEST_TMPDIR/task-p2review"
    mkdir -p "$task_dir"
    # 创建合格的 P2-design.md（四字段齐全 + 候选方案 ≥2 + 权衡）
    cat > "$task_dir/P2-design.md" <<'EOF'
## 方案 A
xxx
## 方案 B
yyy
### 选择理由
A 更简单且有先例

## 范围声明
packages: [pkg-a]
domains: [backend]
ui_affected: false

## gate 命令
gate_commands:
  P5: "pytest -q --tb=no"
EOF
    # 不创建 P2-review.md
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$task_dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P2-review.md"* ]]
}
```

- [ ] **Step 2: 跑测试确认失败**

Run: `bats agate/tests/unit/check-gate.bats --filter "PG.P2REVIEW"`
Expected: FAIL（当前文件不存在时跳过检查，gate exit 0 或 exit 2）

- [ ] **Step 3: 实现 — P2 review 不存在时 exit 1**

旧代码（check-gate.sh L100-116）：
```bash
          P2_REVIEW="$TASK_DIR/P2-review.md"
          if [ -f "$P2_REVIEW" ]; then
              P2_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
              if [ "$P2_REVIEW_STATUS" != "approved" ]; then
                  echo "GATE P2: P2-review.md frontmatter status 非 approved（当前: ${P2_REVIEW_STATUS:-缺失}）" >&2
                  exit 1
              fi
              P2_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
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

新代码：
```bash
          P2_REVIEW="$TASK_DIR/P2-review.md"
          if [ ! -f "$P2_REVIEW" ]; then
              echo "GATE P2: P2-review.md 不存在（P2 评审不可裁剪，必须派发独立 subagent 产出）" >&2
              exit 1
          fi
          P2_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
          if [ "$P2_REVIEW_STATUS" != "approved" ]; then
              echo "GATE P2: P2-review.md frontmatter status 非 approved（当前: ${P2_REVIEW_STATUS:-缺失}）" >&2
              exit 1
          fi
          P2_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P2_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
          if [ -z "$P2_REVIEW_AGENT" ]; then
              echo "GATE P2: P2-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
              exit 2
          fi
          if [ "$P2_REVIEW_AGENT" = "main" ]; then
              echo "GATE P2: P2-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
              exit 1
          fi
```

- [ ] **Step 4: 跑测试确认通过**

Run: `bats agate/tests/unit/check-gate.bats --filter "PG.P2REVIEW"`
Expected: PASS

- [ ] **Step 5: 修改现有测试 G2.13 — 期望 exit 2 改为 exit 1**

现有测试 `check-gate.bats:259`（G2.13）断言"无 P2-review.md 期望 exit 2"。Task 1 把脚本改为 exit 1 后，这个测试会 FAIL。修改它：

旧代码（check-gate.bats:259）：
```bash
@test "G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 2" {
```

新代码：
```bash
@test "G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 1" {
```

并在该测试体内把期望 exit code 从 2 改为 1：
```bash
    [ "$status" -eq 1 ]
```

- [ ] **Step 6: 跑全量 check-gate 测试确认无回归**

Run: `bats agate/tests/unit/check-gate.bats`
Expected: 全部 PASS（G2.13 已改为期望 exit 1，PG.P2REVIEW 新增期望 exit 1）

- [ ] **Step 7: Commit**

```bash
git add agate/scripts/check-gate.sh agate/tests/unit/check-gate.bats
git commit -m "fix(check-gate): P2-review.md not found → exit 1 (was: silently skipped)"
```

---

## Task 2: P0-orchestrator.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P0-orchestrator.md`

### 修改项

1. 推进条件补全为 AND checklist（含环境自检）
2. "考虑拆分"→"必须拆分"
3. 环境自检"确认环境可用"→明确为推进条件的一部分

### 步骤

- [ ] **Step 1: 修改推进条件 + 任务粒度 + 环境自检**

旧代码（L29-42）：
```markdown
## 环境自检

在启动任务前确认环境可用：
- debug 环境可访问（curl health check / 启动服务）
- 测试框架可用（pytest/vitest --version）
- 浏览器自动化可用（playwright --version，UI 任务时）

## 任务粒度

若写不出一句话任务描述 → 任务太大，考虑拆分。单任务应在 1-2 个会话内完成。

## 推进条件

P0-brief.md 四字段齐全 → 写 active-tasks.md（新任务行）→ 读 P1 卡片
```

新代码：
```markdown
## 环境自检

启动任务前必须确认环境可用（不确认不得推进 P1）：
- debug 环境可访问（curl health check / 启动服务）
- 测试框架可用（pytest/vitest --version）
- 浏览器自动化可用（playwright --version，UI 任务时）

## 任务粒度

若写不出一句话任务描述 → 任务太大，必须拆分为多个任务。不允许用模糊描述强行通过。

## 推进条件（全部满足才推进）

- [ ] P0-brief.md 四字段齐全（无空占位符）
- [ ] 环境自检已执行（debug 环境 / 测试框架 / UI 任务的浏览器自动化）
- [ ] active-tasks.md 已写入新任务行

推进后 → 读 P1 卡片
```

- [ ] **Step 2: 验证 consistency 检查**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 3: Commit**

```bash
git add agate/phase-cards/P0-orchestrator.md
git commit -m "docs(P0): harden wording — AND checklist, remove 'consider splitting'"
```

---

## Task 3: P1-requirements.md 推进条件补全

**Files:**
- Modify: `agate/phase-cards/P1-requirements.md:52-57`

### 修改项

推进条件缺 P1-review.md，但 gate 规则有。补全消除歧义。

### 步骤

- [ ] **Step 1: 修改推进条件**

旧代码（L52-57）：
```markdown
## 推进条件

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）
```

- [ ] **Step 2: Commit**

```bash
git add agate/phase-cards/P1-requirements.md
git commit -m "docs(P1): add P1-review.md to advancement checklist"
```

---

## Task 4: P2-design.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P2-design.md`

### 修改项

1. gate 规则消除"文件存在时检查"
2. design_trivial / follows_existing_pattern 须附理由
3. 最小验证"若方案依赖"→要求显式声明
4. "业务方向不明"改为客观触发条件
5. 推进条件标注"全部满足"

### 步骤

- [ ] **Step 1: 修改 gate 规则 — 消除"文件存在时检查"**

旧代码（L100-101）：
```markdown
- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md status: approved（文件存在时检查）
```

新代码：
```markdown
- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
```

- [ ] **Step 2: 修改 design_trivial / follows_existing_pattern — 须附理由**

旧代码（L47-49）：
```markdown
候选方案简化：
- `design_trivial: true` → 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]` → 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）
```

新代码：
```markdown
候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）
```

- [ ] **Step 3: 修改最小验证 — "若方案依赖"→要求显式声明**

旧代码（L32-36）：
```markdown
## P2 最小验证（若方案依赖浏览器行为/安全模型/外部系统行为）
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。纯代码逻辑不需要最小验证。
```

新代码：
```markdown
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

- [ ] **Step 4: 修改产出规格 — minimal_validation 强制声明**

旧代码（L45）：
```markdown
- **minimal_validation**（若方案依赖外部行为）
```

新代码：
```markdown
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）
```

- [ ] **Step 5: 修改 C8 映射表 — "业务方向不明"客观化**

旧代码（L69）：
```markdown
| 业务方向不明 | 任意 | plan-ceo-review / office-hours |
```

新代码：
```markdown
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review / office-hours |
```

> 注意：这是半客观化——"涉及业务方向"仍需 agent 判断，但至少要求有 [NEED_CONFIRM] 标记作为前置条件，比原来的"业务方向不明"（纯主观判断）更严格。完全客观化需要定义"业务方向"的判定信号，留待后续迭代。

- [ ] **Step 5b: 同步下游文件 — role-system.md 和 review-mapping.md 的 C8 映射表**

C8 映射表的权威源是 role-system.md（review-mapping.md:9 明确写"权威源：agate/role-system.md"）。改了 P2 卡片不改权威源会造成不一致。

role-system.md L62 旧代码：
```markdown
| 业务方向不明 | 任意 | office-hours / plan-ceo-review（P1 后 / P2）|
```

role-system.md L62 新代码：
```markdown
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | office-hours / plan-ceo-review（P1 后 / P2）|
```

review-mapping.md L23 做同样修改（措辞一致）。

- [ ] **Step 6: 修改推进条件 — 标注"全部满足"**

旧代码（L105-109）：
```markdown
## 推进条件

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 可只写 1 个）+ 四字段齐全
- [ ] P2-review.md status: approved（P2 未被裁剪时）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）
```

- [ ] **Step 7: 同步下游文件 — dispatch-protocol.md / dispatch-prompt.md / task-files.md 的最小验证文本**

P2 卡片修改了最小验证措辞，下游三个文件有相同的旧措辞需同步：

dispatch-protocol.md L502-504 旧代码：
```markdown
## P2 最小验证（若方案依赖浏览器行为/安全模型/外部系统行为）
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。纯代码逻辑不需要最小验证。
```

dispatch-protocol.md L502-504 新代码：
```markdown
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明"纯代码逻辑，无外部系统依赖"（须写明依赖了哪些内部函数/数据转换）
```

dispatch-prompt.md L87-89 和 task-files.md L231-237 做同样修改（措辞一致）。

dispatch-protocol.md L771-772 的"不需要最小验证的"节也同步修改：
```markdown
- 纯代码逻辑（函数输入输出、数据转换）→ 须在 minimal_validation 字段声明"纯代码逻辑"（写明依赖了哪些内部函数/数据转换）
```

architect.md L71, L80 同步修改（architect 角色文件是 subagent 实际读的指令，措辞不一致会导致 subagent 行为与卡片矛盾）：

architect.md L71 旧代码：
```markdown
  - `minimal_validation:` — **若方案依赖浏览器行为/安全模型/外部系统行为，P2 必须做最小验证**（T019 教训：...）：
```

architect.md L71 新代码：
```markdown
  - `minimal_validation:` — **必须声明**。方案依赖浏览器行为/安全模型/外部系统行为时必须做最小验证（T019 教训：...）；纯代码逻辑时须声明"纯代码逻辑，无外部系统依赖"（写明依赖了哪些内部函数/数据转换）。
```

architect.md L80 旧代码：
```markdown
    **不需要**：纯代码逻辑（TDD 覆盖）、项目内已有模式（已有先例）。
```

architect.md L80 新代码：
```markdown
    **纯代码逻辑**：须声明"纯代码逻辑，无外部系统依赖"（写明依赖了哪些内部函数/数据转换）。
```

plan-eng-review.md L22 同步修改：

旧代码：
```markdown
- **P2 最小验证**：若方案依赖浏览器行为/安全模型/外部系统行为，P2-design.md 是否包含 minimal_validation 字段且 result 为 confirmed
```

新代码：
```markdown
- **P2 最小验证**：P2-design.md 是否包含 minimal_validation 字段——方案依赖外部行为时须含验证结果；纯代码逻辑时须含声明"纯代码逻辑，无外部系统依赖"+ 理由
```

- [ ] **Step 8: Commit**

```bash
git add agate/phase-cards/P2-design.md agate/dispatch-protocol.md agate/assets/templates/dispatch-prompt.md agate/assets/templates/task-files.md agate/role-system.md agate/rules/review-mapping.md agate/assets/execution-roles/architect.md agate/assets/review-roles/plan-eng-review.md
git commit -m "docs(P2): harden wording — review must exist, trivial needs reason, minimal_validation required"
```

---

## Task 5: P3-tdd.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P3-tdd.md`

### 修改项

1. "按包拆分并行（可选）"→"（条件触发）"
2. 环境基线"均可忽略"→"必须执行，stderr 可忽略"
3. 推进条件标注"全部满足"

### 步骤

- [ ] **Step 1: 修改环境基线步骤**

旧代码（L8-10）：
```markdown
0. 跑 `agate-capture-env-baseline.sh $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
```

新代码：
```markdown
0. 跑 `agate-capture-env-baseline.sh $TASK_DIR`（自动捕获环境基线）。**必须执行**。
   该步骤不阻塞流程——脚本的 stderr 输出（含 WARNING）均可忽略，执行完直接继续步骤 1。
```

- [ ] **Step 1b: 修改前置条件 — "P2 未被裁剪时"→"P2 不可裁剪"**

P2 不可裁剪（state-machine.md 明确），"P2 未被裁剪时"措辞多余且暗示 P2 可能被裁剪。

旧代码（P3-tdd.md L25）：
```markdown
- [ ] P2-review.md status: approved（P2 未被裁剪时）
```

新代码：
```markdown
- [ ] P2-review.md status: approved（P2 不可裁剪）
```

- [ ] **Step 2: 修改"按包拆分并行"标题**

旧代码（L53）：
```markdown
## 按包拆分并行（可选）
```

新代码：
```markdown
## 按包拆分并行（条件触发，非强制）
```

- [ ] **Step 3: 修改推进条件标题**

旧代码（L71）：
```markdown
## 推进条件
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P4）
```

- [ ] **Step 4: Commit**

```bash
git add agate/phase-cards/P3-tdd.md
git commit -m "docs(P3): harden wording — 'optional' → 'conditional', baseline must run"
```

---

## Task 6: P4-implementation.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P4-implementation.md`

### 修改项

1. "必要评审派发"→"按 C8 映射表派发评审"
2. "P5 由主 Agent 亲自执行"→"P5 由主 Agent 派发 verifier subagent 执行"
3. "若有触发"→"按 C8 映射表触发的"
4. "按包拆分并行（可选，需额外约束）"→"（条件触发，需额外约束）"
5. "nudge 不是强制"→"必须分配，未分配导致冲突时计为重试"
6. 推进条件标注"全部满足"（已有，确认措辞一致）

### 步骤

- [ ] **Step 1: 修改步骤 3 — "必要评审"→"C8 映射"**

旧代码（L14）：
```markdown
3. 必要评审派发（见下方）
```

新代码：
```markdown
3. 按 C8 映射表派发评审（见下方）
```

- [ ] **Step 1b: 修改前置条件 — "P2 未被裁剪时"→"P2 不可裁剪"**

旧代码（P4-implementation.md L31）：
```markdown
- [ ] P2-review.md status: approved（P2 未被裁剪时）
```

新代码：
```markdown
- [ ] P2-review.md status: approved（P2 不可裁剪）
```

- [ ] **Step 2: 修改自查≠gate 节 — "P5 由主 Agent 亲自执行"**

旧代码（L48-51）：
```markdown
## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 亲自执行 P2-design.md 的 gate_commands，结果以主 Agent 为准。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。
```

新代码：
```markdown
## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。
```

- [ ] **Step 3: 修改评审派发标题 — 明确"C8 映射"**

旧代码（L63）：
```markdown
## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审：
```

新代码：
```markdown
## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：
```

- [ ] **Step 4: 修改推进条件 — "若有触发"→"按 C8 映射表"**

旧代码（L123-128）：
```markdown
## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 评审完成（若有触发）：P4-review.md status: approved
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（无触发评审角色时此项自动满足）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成
```

- [ ] **Step 5: 修改"按包拆分并行"标题**

旧代码（L89）：
```markdown
## 按包拆分并行（可选，需额外约束）
```

新代码：
```markdown
## 按包拆分并行（条件触发，需额外约束）
```

- [ ] **Step 6: 修改基础设施隔离 — "nudge 不是强制"→"必须分配"**

旧代码（L112）：
```markdown
主 Agent 在并行派发前应确认每个 subagent 的 dispatch-context 已包含上述隔离参数。**注意**：这是 nudge 不是强制规则（无 gate 脚本检查），与 design_trivial 的形式义务同级。未分配隔离参数的后果是运行时冲突（端口占用/数据库锁），由 subagent 报错暴露。
```

新代码：
```markdown
主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。
```

- [ ] **Step 7: Commit**

```bash
git add agate/phase-cards/P4-implementation.md
git commit -m "docs(P4): harden wording — C8 mapping mandatory, P5 is subagent, 'optional' → 'conditional'"
```

---

## Task 7: P5-verification.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P5-verification.md`

### 修改项

1. "按包拆分并行（可选）"→"（条件触发）"
2. 签名校验"轻量验证"→"必须"
3. 全量测试"建议"→"应"+未运行须声明
4. "nudge，同 P4"→"必须分配"
5. 推进条件标注"全部满足"

### 步骤

- [ ] **Step 1: 修改全量测试 WARNING**

旧代码（L50-53）：
```markdown
- **全量测试 WARNING**：P5 阶段建议运行全量测试套件（含非本任务测试），若发现预存失败：
  - 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
  - 主 Agent 判断：修复成本 < 推迟成本 → 立即修复；否则记录到 known-failures.md
  这是 WARNING 级建议，不阻断 P5 推进。
```

新代码：
```markdown
- **全量测试**：P5 阶段应运行全量测试套件（含非本任务测试）。发现预存失败时：
  - 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
  - 主 Agent 判断：修复成本 < 推迟成本 → 立即修复；否则记录到 known-failures.md
  全量测试不阻断 P5 推进，但未运行全量测试时须在 P5-test-results/unit.md 标注"未运行全量测试"。
```

- [ ] **Step 2: 修改签名校验 — "轻量验证"→"必须"**

旧代码（L96-102）：
```markdown
**缓解**：主 Agent 在推进前做轻量签名校验——grep test runner 输出签名：

```bash
grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md
```

计数 >0 才视为有效产出。这是轻量验证（确认文件包含真实 test runner 输出格式），不是重跑测试。CI backstop 在 push 后兜底全量验证。
```

新代码：
```markdown
**缓解**：主 Agent 在推进前**必须**执行签名校验——grep test runner 输出签名：

```bash
grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' P5-test-results/unit.md
```

计数 >0 才视为有效产出，计数=0 视为假完成，计为重试。这不是重跑测试（CI backstop 在 push 后兜底全量验证）。
```

- [ ] **Step 3: 修改推进条件标题**

旧代码（L79）：
```markdown
## 推进条件
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P6）
```

- [ ] **Step 4: 修改"按包拆分并行"标题**

旧代码（L106）：
```markdown
## 按包拆分并行（可选）
```

新代码：
```markdown
## 按包拆分并行（条件触发，非强制）
```

- [ ] **Step 5: 修改基础设施隔离 — "nudge"→"必须"**

旧代码（L120）：
```markdown
主 Agent 在并行派发前应确认每个 verifier 的 dispatch-context 已包含独立的基础设施参数（nudge，同 P4）。
```

新代码：
```markdown
主 Agent 在并行派发前**必须**为每个 verifier 的 dispatch-context 分配独立的基础设施参数（同 P4，未分配导致冲突时计为重试）。
```

- [ ] **Step 6: Commit**

```bash
git add agate/phase-cards/P5-verification.md
git commit -m "docs(P5): harden wording — signature check mandatory, 'optional' → 'conditional'"
```

---

## Task 8: P6-acceptance.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P6-acceptance.md`

### 修改项

1. "先验证功能再满足 gate 格式"消除先后优先级暗示
2. "P6 gate 由主 Agent 亲自执行验收检查"→明确为跑 gate 脚本
3. "按包拆分并行（可选，受限模式）"→"（条件触发，受限模式）"
4. 推进条件 — vision blocker>0 追查须写命令+输出+结论
5. 推进条件标注"全部满足"

### 步骤

- [ ] **Step 1: 修改核心原则 — 消除"再"字**

旧代码（L22-24）：
```markdown
## 核心原则 ⚠️

**先验证功能（用户视角），再满足 gate 格式。** gate 是必要条件（格式不对 → commit 不了），不是充分条件（格式对了 ≠ 功能正确）。T046 教训：花 2 小时凑 PASS 格式，没花 5 分钟检查 API 响应头。
```

新代码：
```markdown
## 核心原则 ⚠️

**功能验证和 gate 格式都必须满足。** T046 教训：花 2 小时凑 PASS 格式，没花 5 分钟检查 API 响应头。不接受只满足格式不验证功能，也不接受只验证功能不满足格式。gate 是必要条件（格式不对 → commit 不了），不是充分条件（格式对了 ≠ 功能正确）。
```

- [ ] **Step 2: 修改步骤 4 — 消除"再"字**

旧代码（L12）：
```markdown
4. **先验证功能（用户视角），再满足 gate 格式**（T046 教训：别反过来）
```

新代码：
```markdown
4. **功能验证和 gate 格式都必须满足**（T046 教训：先做功能验证，不要只凑格式）
```

- [ ] **Step 3: 修改自查≠gate 节 — 明确"亲自执行"=跑 gate 脚本**

旧代码（L129-132）：
```markdown
## 自查≠gate
写完验证脚本后应自跑确认脚本可执行（自查），但自查通过 ≠ P6 gate 通过。
P6 gate 由主 Agent 亲自执行验收检查，结果以主 Agent 为准。
不要在返回中声称"验收已通过"或"全部 BDD PASS"——只返回路径 + 摘要。
```

新代码：
```markdown
## 自查≠gate
写完验证脚本后应自跑确认脚本可执行（自查），但自查通过 ≠ P6 gate 通过。
P6 gate 由主 Agent 亲自跑 gate 脚本（check-gate.sh P6 + check-p6-evidence.sh + check-p6-provenance.sh），验证的是 verifier subagent 的产出。结果以主 Agent 跑的 gate 脚本为准。
不要在返回中声称"验收已通过"或"全部 BDD PASS"——只返回路径 + 摘要。
```

- [ ] **Step 4: 修改推进条件 — vision blocker 追查须写明**

旧代码（L106-112）：
```markdown
## 推进条件

- [ ] 所有 BDD PASS（FAIL=0）
- [ ] 无行首 `[NEED_CONFIRM]`（`[NO_NEED_CONFIRM]` 为合规负向声明）
- [ ] P6-evidence/ 目录非空 + 证据文件被引用
- [ ] UI 任务：vision-helper blocker_count=0 或 blocker>0 已追查
- [ ] provenance 审计通过
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P7）

- [ ] 所有 BDD PASS（FAIL=0）
- [ ] 无行首 `[NEED_CONFIRM]`（`[NO_NEED_CONFIRM]` 为合规负向声明）
- [ ] P6-evidence/ 目录非空 + 证据文件被引用
- [ ] UI 任务：vision-helper blocker_count=0；blocker>0 时须在 P6-acceptance.md 写明追查命令 + 输出 + 根因结论（仅写"已追查"不合规）
- [ ] provenance 审计通过
```

- [ ] **Step 5: 修改"按包拆分并行"标题**

旧代码（L94）：
```markdown
## 按包拆分并行（可选，受限模式）
```

新代码：
```markdown
## 按包拆分并行（条件触发，受限模式）
```

- [ ] **Step 6: 同步下游文件 — dispatch-protocol.md L549 的 P6 自查≠gate 节**

dispatch-protocol.md L549 旧代码：
```markdown
P6 gate 由主 Agent 亲自执行验收检查，结果以主 Agent 为准。
```

dispatch-protocol.md L549 新代码：
```markdown
P6 gate 由主 Agent 亲自跑 gate 脚本（check-gate.sh P6 + check-p6-evidence.sh + check-p6-provenance.sh），验证的是 verifier subagent 的产出。结果以主 Agent 跑的 gate 脚本为准。
```

- [ ] **Step 7: Commit**

```bash
git add agate/phase-cards/P6-acceptance.md agate/dispatch-protocol.md
git commit -m "docs(P6): harden wording — 'function first then format' → both required, gate = run scripts"
```

---

## Task 9: P7-consistency.md + P8-release.md 措辞加固

**Files:**
- Modify: `agate/phase-cards/P7-consistency.md`
- Modify: `agate/phase-cards/P8-release.md`

### 步骤

- [ ] **Step 1: P7 推进条件标注"全部满足"**

旧代码（P7 L64）：
```markdown
## 推进条件
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: P8）
```

- [ ] **Step 2: P7 裁剪跳阶 — coupling_checklist 须非空**

旧代码（P7 L4）：
```markdown
> 裁剪跳阶 → 确认 P1 phases 不含 P7 + 源文件数 ≤5 + 无 implicit_coupling + 有 coupling_checklist → 跳过，读 P8 卡片
```

新代码：
```markdown
> 裁剪跳阶 → 确认 P1 phases 不含 P7 + 源文件数 ≤5 + 无 implicit_coupling + 有 coupling_checklist（须列出至少 2 个已检查的耦合点，空清单不合规）→ 跳过，读 P8 卡片
```

- [ ] **Step 3: P8 gate 规则 — "手动确认"→"必须亲自执行"**

旧代码（P8 L61-65）：
```markdown
仍须主 Agent 手动确认：
- 从 P2 packages 逐包读取发布检查命令并执行
- 重跑 P5 gate（gate_commands.P5 exit 0 + failed==0）
- git log 对照 CHANGELOG 无遗漏
- 从 P2 packages 验证 version 文件路径
```

新代码：
```markdown
主 Agent **必须亲自执行**以下验证（不可跳过、不可委托 subagent）：
- 从 P2 packages 逐包读取发布检查命令并执行 → 全部 exit 0
- 重跑 P5 gate（gate_commands.P5 exit 0 + failed==0）
- `git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 无遗漏
- 从 P2 packages 验证 version 文件路径
```

- [ ] **Step 4: P8 READY 收尾 — "必须实际执行命令"**

旧代码（P8 L67）：
```markdown
## READY 收尾检查（P8 gate 通过后）— 主 Agent 亲自执行（不派发 subagent）

参考 P8-release.md 临时资源清单执行清理：
```

新代码：
```markdown
## READY 收尾检查（P8 gate 通过后）— 主 Agent 亲自执行（不派发 subagent）

参考 P8-release.md 临时资源清单执行清理。以上检查项无 gate 脚本自动验证（已知缺口），**必须逐项实际执行检查命令**（如 `ps aux | grep debug` 确认服务已停止、`git status` 确认工作区干净），不得仅凭记忆打勾。
```

- [ ] **Step 5: P8 推进条件标注"全部满足"**

旧代码（P8 L91）：
```markdown
## 推进条件
```

新代码：
```markdown
## 推进条件（全部满足才写 phase: READY）
```

- [ ] **Step 6: Commit**

```bash
git add agate/phase-cards/P7-consistency.md agate/phase-cards/P8-release.md
git commit -m "docs(P7,P8): harden wording — checklist AND, manual confirm mandatory, cleanup must execute"
```

---

## Task 10: dispatch-protocol.md P4 迭代表措辞修正

**Files:**
- Modify: `agate/dispatch-protocol.md:624`

### 步骤

- [ ] **Step 1: 修改 P4 迭代表 — "可选"→"按 C8 映射触发"**

旧代码：
```markdown
| P4 | implementer 写代码 | design-review(可选) | review 否 → implementer 修改 → 再 review → … → approved |
```

新代码：
```markdown
| P4 | implementer 写代码 | 按 C8 映射触发（非可选） | review 否 → implementer 修改 → 再 review → … → approved |
```

- [ ] **Step 2: Commit**

```bash
git add agate/dispatch-protocol.md
git commit -m "docs(dispatch-protocol): P4 review 'optional' → 'C8 triggered, not optional'"
```

---

## Task 11: 全量验证 + consistency + count-tests

**Files:**
- Verify: 全部协议文件

### 步骤

- [ ] **Step 1: 全量 bats**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: 全部 PASS（P2 review 硬检查新增 1 个测试，总计数 +1）

- [ ] **Step 2: consistency 检查**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 3: shellcheck**

Run: `shellcheck -S warning agate/scripts/*.sh`
Expected: 无 error

- [ ] **Step 4: 测试用例计数**

Run: `bash agate/tests/scripts/count-tests.sh`
Expected: 总计数比修改前 +0（G2.13 是修改不是新增，PG.P2REVIEW 是新增 → 净 +1）。count-tests 脚本不读取 expected 文件，只是输出统计数供人工对照。确认数字合理即可。

- [ ] **Step 5: 无需 commit（本 Task 是验证步骤，不修改文件）**

---

## Task 12: 更新 hardening-roadmap.md

**Files:**
- Modify: `docs/hardening-roadmap.md`

### 步骤

- [ ] **Step 1: 记录本次改进**

在 `docs/hardening-roadmap.md` 中添加 v0.25.0 版本节：

```markdown
### P2.50: 阶段卡片措辞加固 — 消除 agent 可钻空子

**状态**：已实施
**来源**：T082 复盘（agent 跳过 P4 评审，用 gate exit 0 作为合理化借口）
**改动**：
- 所有阶段卡片"推进条件"改为显式 AND checklist，标注"全部满足才推进"
- 消灭"可选"/"若有触发"/"若方案依赖"/"可以考虑"等模糊措辞
- "按包拆分并行（可选）"统一改为"（条件触发）"
- check-gate.sh P2 review 文件不存在时 exit 1（bug fix：原来文件不存在时跳过检查）
- design_trivial / follows_existing_pattern 须附理由
- minimal_validation 强制声明（"纯代码逻辑"也须写明理由）
- P4 自查节"P5 由主 Agent 亲自执行"→"派发 verifier subagent 执行"
- P6 "先验证功能再满足格式"→"两者都必须满足"
- P5 签名校验"轻量验证"→"必须"
- P8 "手动确认"→"必须亲自执行"
- 基础设施隔离"nudge"→"必须，未分配导致冲突时计为重试"
**不修理由**（P3 e2e 质量闸门）：
- "选择器写得好不好"不是机器可判定的，gate 不做语义判断
- P5 实跑 e2e 已经是正确的防线
- test-designer.md 已有指导，执行不到位是 subagent 质量问题
```

- [ ] **Step 2: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: record P2.50 phase card wording hardening in roadmap"
```

---

## Self-Review

### Spec coverage

- [x] P0 推进条件补全 + "考虑拆分"→"必须拆分" — Task 2
- [x] P1 推进条件补全 P1-review.md — Task 3
- [x] P2 gate 规则消除"文件存在时检查" + design_trivial 须附理由 + minimal_validation 强制声明 + "业务方向不明"客观化 — Task 4
- [x] P2 check-gate.sh bug fix（文件不存在 exit 1）— Task 1
- [x] P3 "可选"→"条件触发" + 环境基线"必须执行" — Task 5
- [x] P4 "必要评审"→"C8 映射" + "P5 亲自执行"修正 + "若有触发"→"按 C8 映射" + "可选"→"条件触发" + "nudge"→"必须" — Task 6
- [x] P5 签名校验"必须" + 全量测试措辞 + "可选"→"条件触发" + "nudge"→"必须" — Task 7
- [x] P6 "先验证再格式"→"两者都满足" + "亲自执行验收"→"跑 gate 脚本" + "可选"→"条件触发" + vision blocker 追查须写明 — Task 8
- [x] P7 推进条件标注 + coupling_checklist 须非空 — Task 9
- [x] P8 "手动确认"→"必须亲自执行" + 收尾清单"必须执行命令" + 推进条件标注 — Task 9
- [x] dispatch-protocol P4 迭代表"可选"→"C8 映射触发" — Task 10
- [x] roadmap 记录 — Task 12
- [x] 全量验证 — Task 11

### 前后传播分析

| 修改 | 影响的下游文件 | 是否需要同步修改 |
|------|--------------|----------------|
| P2 gate 规则"文件存在时检查"→"不存在 exit 1" | check-gate.sh 已在 Task 1 修改 | ✅ 已覆盖 |
| P2 gate 规则措辞变化 | state-machine.md L85（P2→P3 转移条件引用 P2-review.md 有效） | 不需要改——state-machine 说"P2-review.md 有效"暗示文件存在，Task 1 修复后两者一致性改善 |
| P2 最小验证措辞变化 | dispatch-protocol.md L502-504 + L771-772, dispatch-prompt.md L87-89, task-files.md L231-237, architect.md L71+L80, plan-eng-review.md L22 | ✅ Task 4 Step 7 覆盖 |
| P2 C8 映射表"业务方向不明"客观化 | role-system.md L62, review-mapping.md L23 | ✅ Task 4 Step 5b 覆盖 |
| P4 "P5 由主 Agent 亲自执行"→"派发 verifier" | P4-implementation.md 已在 Task 6 修改 | ✅ 已覆盖（dispatch-protocol.md L514 已是新措辞，不需再改） |
| P6 "亲自执行验收检查"→"跑 gate 脚本" | dispatch-protocol.md L549 | ✅ Task 8 Step 6 覆盖 |
| "按包拆分并行（可选）"→"（条件触发）" | P3/P4/P5/P6 四个卡片 | ✅ 全部覆盖（Task 5/6/7/8） |
| dispatch-protocol P4 迭代表 | 已在 Task 10 修改 | ✅ 已覆盖 |
| 推进条件"全部满足"标注 | P0-P8 所有卡片 | ✅ 全部覆盖（Task 2-9） |
| P2 design_trivial 须附理由 | architect.md（角色文件） | 不需要改——architect.md 已有指导，卡片加理由要求不改变角色文件行为 |
| "P2 未被裁剪时"→"P2 不可裁剪" | P3-tdd.md L25, P4-implementation.md L31 | ✅ Task 5 Step 1b + Task 6 Step 1b 覆盖 |
| P3/P5"非 pytest 技术栈"段落 | P3-tdd.md L51, P5-verification.md L39 | 已检查，无需修改（技术栈无关性说明，与措辞加固无直接关系） |
| orchestrator-template.md | 已检查，无模糊措辞 | 无需修改 |

### Placeholder scan

无 placeholder——所有步骤包含完整旧代码和新代码。

### Type consistency

- "推进条件（全部满足才写 phase: PN）"格式在所有卡片中一致
- "条件触发"一词在 P3/P4/P5/P6 中一致使用
- "必须亲自执行"在 P8 中一致使用
