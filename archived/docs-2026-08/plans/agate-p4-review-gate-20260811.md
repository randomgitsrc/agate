# P4 gate 补 P4-review agent≠main 门禁（与 P2 对称）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 P4 gate 与 P2 gate 对称——要求 `P4-review.md` 存在 + `status: approved` + `agent≠main`，堵住"主 Agent 可跳过 P4 独立评审或自批实现"的漏洞。**同时修正 C8 表的 risk=high 逃生口**（P2 方案评审 ≠ P4 实现评审，高风险实现代码必须独立评审）。

**Architecture:** 复制 P2 gate 的 review 检查模式（存在性 → status → agent≠main）到 P4 gate 分支。P4 gate 检查顺序：先 review 门禁，再查暂存区代码文件。现有 G4.2/3/4 测试需补 P4-review.md。

**Tech Stack:** bash + bats。

**背景（已核实）**：
- `P4-implementation.md:86` 明确写"agent 字段必须非 main（与 P2 评审同规则，check-gate.sh 在 P2 分支硬拦截 agent=main 的 approved）"——**文档声称 gate 会拦，但脚本 P4 分支没实现**
- `check-gate.sh:220-224` 的 P4 分支只查"暂存区有代码文件"，不看 P4-review.md
- P2 gate（L155-171）有完整 review 检查：存在性（不存在 exit 1）→ status approved → agent≠main
- roadmap"不修清单"记录此 gap（"P4 gate 不验证 P4-review.md agent≠main，留待 v0.23.0+ 补充"）
- **决策**：完整对称 P2（用户确认）——要求 P4-review.md 存在 + approved + agent≠main。

**评审新增发现（risk=high 逃生口是设计缺陷）**：C8 表（review-mapping.md）risk=high 行写"—（plan-eng-review 在 P2 已派）"，但这混淆了两个层面——P2 plan-eng-review 审**方案设计**（P2-design.md），P4 review 审**实现代码**（SQL 注入/竞态/TOCTOU/资源泄漏）。高风险任务恰恰最需要 P4 实现评审（安全/权限/数据迁移最容易在生产炸）。P2 审方案 ≠ 实现安全。T001（risk=high）实际也产了 P4-review.md，印证真实执行需要它。**修正：删 C8 表 risk=high 逃生口，P4 对所有任务要求实现评审。**

---

## File Structure

- **Modify** `agate/scripts/check-gate.sh:220-224` — P4 分支加 review 门禁（存在+approved+agent≠main）
- **Modify** `agate/rules/review-mapping.md` — C8 表 risk=high 行删逃生口（P2 方案评审 ≠ P4 实现评审）
- **Modify** `agate/phase-cards/P4-implementation.md:130` — 删"无触发评审角色时此项自动满足"逃生口
- **Test** `agate/tests/unit/check-gate.bats` — G4.2/3/4 补 P4-review.md；新增 G4.5/4.6/4.7（缺文件/非 approved/agent=main）
- **Modify** `agate/tests/README.md` — 用例数
- **Modify** `README.md`, `CHANGELOG.md` — v0.40.2 bump

---

### Task 1: TDD — 写失败测试（先红）

**Files:**
- Test: `agate/tests/unit/check-gate.bats`

**背景**：现有 G4.2/3/4 期望 exit 0，但没放 P4-review.md。新增 review 门禁后它们应 fail（缺 review 文件被拦）。先验证红，再加新测试。

- [ ] **Step 1: 先跑现有 G4 测试确认基线绿**

```bash
bats agate/tests/unit/check-gate.bats --filter 'G4\.'
```
预期：4 个全绿（当前无 review 门禁）。

- [ ] **Step 2: 新增 G4.5/4.6/4.7 失败测试**

在 `agate/tests/unit/check-gate.bats` 的 G4 区块末尾追加：

```bash
@test "G4.5 check-gate.sh P4 无 P4-review.md → exit 1（评审不可跳过）" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4-review.md"* ]]
}

@test "G4.6 check-gate.sh P4 P4-review.md status 非 approved → exit 1" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: rejected
agent: reviewer-subagent
---
reviewed, found issues.
EOF
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"非 approved"* ]]
}

@test "G4.7 check-gate.sh P4 P4-review.md agent=main → exit 1（不可自批）" {
    local dir
    dir=$(create_task_dir)
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: main
---
self-approved.
EOF
    echo "code" > "$repo/src.py"
    git -C "$repo" add "src.py" "task/P4-review.md"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P4 'task'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"agent=main"* ]]
}
```

运行：
```bash
bats agate/tests/unit/check-gate.bats --filter 'G4\.5\|G4\.6\|G4\.7'
```
预期：3 个 FAIL（红）——当前 P4 gate 不看 P4-review.md，会 exit 0。

---

### Task 1.5: 修 C8 表 risk=high 逃生口 + P4 card

**Files:**
- Modify: `agate/rules/review-mapping.md`
- Modify: `agate/phase-cards/P4-implementation.md:130`

**背景（评审发现）**：C8 表 risk=high 行"—（plan-eng-review 在 P2 已派）"错误地把"P2 审了方案"当成"P4 无需审实现"。P2 plan-eng-review 审 P2-design.md（方案设计），P4 review 审实现代码（SQL 注入/竞态/TOCTOU）——高风险任务恰恰最需要 P4 实现评审。删逃生口，P4 对所有任务要求实现评审。

- [ ] **Step 1: review-mapping.md 修 risk=high 行**

把 `agate/rules/review-mapping.md` 的 C8 映射表 risk=high 行：

```
| 任意 | **high** | plan-eng-review（硬规则，必须派独立 subagent） | P2 |
```

改为：

```
| 任意 | **high** | plan-eng-review（P2 方案评审，硬规则） + P4 实现评审（按 domains 派 review/design-review/cso） | P2 + P4 |
```

并在表下方补一条说明：

```
> **risk=high 的 P4 实现评审不可省**：P2 plan-eng-review 审的是方案设计（P2-design.md），
> P4 review 审的是实现代码（SQL 注入/竞态/TOCTOU/资源泄漏）。高风险任务（安全/权限/数据
> 迁移/生产环境）恰恰最需要 P4 实现评审——P2 审方案 ≠ 实现安全。T001 实证：risk=high 任务
> 仍应产 P4-review.md。
```

- [ ] **Step 2: P4-implementation.md 删逃生口（含内联 C8 表）**

**Step 2a: 修推进条件**。把 `agate/phase-cards/P4-implementation.md:130`：

```
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（无触发评审角色时此项自动满足）
```

改为：

```
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
```

**Step 2b: 修卡片内联 C8 表（评审第 2 轮发现）**。`P4-implementation.md:74` 的**卡片内联 C8 表**仍含 risk=high 逃生行：

```
| risk=high | —（plan-eng-review 在 P2 已派）| — |
```

改为：

```
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |
```

> 关键：P4 card 有两处需同步——推进条件（L130）+ 内联 C8 表（L74）。漏改任一处都会造成卡片内部矛盾（L74 说 risk=high 无 P4 评审 vs L130 说所有任务都要求）。

- [ ] **Step 3: 验证 + Commit**

```bash
python3 agate/scripts/check-protocol-consistency.py   # 0 ERROR
git add agate/rules/review-mapping.md agate/phase-cards/P4-implementation.md
git commit -m "docs: 修 C8 表 risk=high 逃生口，P4 实现评审不可省 (v0.40.2)

P2 plan-eng-review 审方案设计，P4 review 审实现代码。risk=high 任务
恰恰最需要 P4 实现评审（安全/权限/数据迁移最易在生产炸），原 C8 表
'plan-eng-review 在 P2 已派'混淆了两个层面。删逃生口（review-mapping.md
C8 表 + P4 card 内联表 + 推进条件三处同步），P4 对所有任务要求实现评审。

self-gate-review: agate/rules/review-mapping.md agate/phase-cards/P4-implementation.md"
```

---

### Task 2: 改 check-gate.sh P4 分支

**Files:**
- Modify: `agate/scripts/check-gate.sh:220-224`

- [ ] **Step 1: 替换 P4 分支**

把当前 P4 分支：

```bash
  P4)
      # pre-commit 阶段：检查暂存区有代码文件（非纯文档/状态文件）
      # N1 修复：原来查 git log，但 pre-commit 时 commit 还没创建，第一条 P4 commit 永远无法通过
      git diff --cached --name-only | grep -qvE '(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$' && exit 0 || exit 1 ;;
```

替换为：

```bash
  P4)
      # P4 review 门禁（与 P2 对称，roadmap 补 gap）
      # P4-implementation.md:86 要求"agent 字段必须非 main（与 P2 评审同规则）"，但此前 gate 未强制
      P4_REVIEW="$TASK_DIR/P4-review.md"
      if [ ! -f "$P4_REVIEW" ]; then
          echo "GATE P4: P4-review.md 不存在（P4 评审不可裁剪，必须派发独立 subagent 产出，见 phase-cards/P4-implementation.md C8 机械映射）" >&2
          exit 1
      fi
      P4_REVIEW_STATUS=$(sed -n '/^---$/,/^---$/p' "$P4_REVIEW" | { grep '^status:' || true; } | sed 's/^status:\s*//' | head -1)
      if [ "$P4_REVIEW_STATUS" != "approved" ]; then
          echo "GATE P4: P4-review.md frontmatter status 非 approved（当前: ${P4_REVIEW_STATUS:-缺失}）" >&2
          exit 1
      fi
      P4_REVIEW_AGENT=$(sed -n '/^---$/,/^---$/p' "$P4_REVIEW" | { grep '^agent:' || true; } | sed 's/^agent:\s*//' | head -1)
      if [ -z "$P4_REVIEW_AGENT" ]; then
          echo "GATE P4: P4-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）" >&2
          exit 2
      fi
      if [ "$P4_REVIEW_AGENT" = "main" ]; then
          echo "GATE P4: P4-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）" >&2
          exit 1
      fi
      # pre-commit 阶段：检查暂存区有代码文件（非纯文档/状态文件）
      # N1 修复：原来查 git log，但 pre-commit 时 commit 还没创建，第一条 P4 commit 永远无法通过
      git diff --cached --name-only | grep -qvE '(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$' && exit 0 || exit 1 ;;
```

> 关键：与 P2 gate（L155-171）语义完全一致——存在性 exit 1 / status 非 approved exit 1 / 缺 agent WARNING exit 2 / agent=main exit 1。

- [ ] **Step 2: 更新现有 G4.2/3/4 测试补 P4-review.md**

`G4.2/3/4` 期望 exit 0，需在 `git add` 前补一个合规的 P4-review.md：

```bash
    cat > "$repo/task/P4-review.md" <<'EOF'
---
status: approved
agent: reviewer-subagent
---
reviewed, approved.
EOF
```

并在 `git add` 时加上 `"task/P4-review.md"`。

> 注意：`create_task_dir` 生成的任务目录已含 `.state.yaml`，G4.2 用 `cp -r "$dir" "$repo/task"` 复制。P4-review.md 需手动写（fixtures 不生成）。

- [ ] **Step 3: 验证**

```bash
bats agate/tests/unit/check-gate.bats --filter 'G4\.'
```
预期：G4.1-4.7 全绿（含新增 3 个）。

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
```
预期：全绿；0 ERROR。

- [ ] **Step 4: Commit**

```bash
git add agate/scripts/check-gate.sh agate/tests/unit/check-gate.bats
git commit -m "fix: P4 gate 补 P4-review 门禁（存在+approved+agent≠main）(v0.40.2)

与 P2 gate 对称。P4-implementation.md:86 声称'agent 必须非 main 与 P2 同规则'，
但 check-gate.sh P4 分支此前只查暂存区代码文件，未强制 P4-review。
补：P4-review.md 必须存在 + status approved + agent≠main，堵'跳过评审/自批实现'漏洞。

self-gate-review: agate/scripts/check-gate.sh"
```

---

### Task 3: 版本 bump v0.40.2 + 收尾验证

**Files:**
- Modify: `README.md`, `CHANGELOG.md`, `agate/tests/README.md`

- [ ] **Step 1: 更新 tests/README 计数**

```bash
bash agate/tests/scripts/count-tests.sh
```
确认 check-gate.bats 用例数 +3（97→100），同步到 `agate/tests/README.md`。

- [ ] **Step 2: 全量验证**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
shellcheck -S warning agate/scripts/*.sh
python3 agate/scripts/check-protocol-consistency.py
```
预期：全绿 / clean / 0 ERROR。

- [ ] **Step 3: 版本 bump + tag + PR**

README badge `v0.40.1` → `v0.40.2`。CHANGELOG 加 `[v0.40.2]`（P4 review 门禁，非 BREAKING）。tag v0.40.2。**release PR 普通 merge（--no-ff）**。

---

## Self-Review

**1. Spec coverage：** P4 review 门禁（存在+approved+agent≠main）→ Task 1（3 失败测试）+ Task 2（实现 + G4.2/3/4 补文件）；版本 → Task 3。与用户确认的"完整对称 P2"一致。

**2. Placeholder scan：** 无 TBD；每步含完整代码。

**3. Type consistency：** `P4_REVIEW`/`P4_REVIEW_STATUS`/`P4_REVIEW_AGENT` 与 P2 的 `P2_REVIEW`/`P2_REVIEW_STATUS`/`P2_REVIEW_AGENT` 命名模式一致。P4-review.md frontmatter 格式与 P2-review.md 一致（status/agent）。

**评审记录（独立评审 1 轮）：**
- ✓ P2 gate 模板、P4 分支语法、测试红绿、consistency 均验证正确
- ✗ **发现 C8 表 risk=high 逃生口是设计缺陷**（P2 方案评审 ≠ P4 实现评审，高风险实现必须独立评审）→ 新增 Task 1.5 修 review-mapping.md + P4 card
- ✗ **第 2 轮：Task 1.5 漏改 P4 card 内联 C8 表（L74）**→ 补 Step 2b 三处同步（review-mapping.md + P4 card 内联表 + 推进条件）
- ✗ **P3→P4 边界 commit 会被新 gate 拦**（T001 `293924f` 模式：staged phase=P4 + P3 产出，无 P4-review）——这是行为变更，符合 git-integration 规则 2"phase=本 commit 产出阶段"收紧，需文档化。已验证无活动任务在 phase=P4（active-tasks 空，T001 归档）

**已识别风险：**
- **G4.2/3/4 补 P4-review.md 是必需 churn**：新增 review 门禁后这些测试不补会红。已列入 Task 2 Step 2。
- **P4 gate 从 pre-commit 调用**：pre-commit 在 phase=P4 时跑 check-gate P4。若某任务 P4 产出分多次 commit（实现 + review 分开提交），第一次 commit（无 P4-review）会被拦——**符合协议意图**（P4 card L64 要求评审在实现完成后、gate 前派发），但需确认现有任务不因新增门禁而卡住。若 P4-review 通常在 P4 阶段同一 commit 提交，无影响。
- **缺 agent 字段时 exit 2（WARNING）**：与 P2 一致（向后兼容），不阻塞。