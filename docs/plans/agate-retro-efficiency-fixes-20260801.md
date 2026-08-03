# T084+T075 复盘效率修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 T084+T075 复盘暴露的 6 个 agate 效率问题（3 脚本 BUG + 3 设计缺陷），预期节省 ~2.9h/任务。

**Architecture:** P2.52 check-pruning YAML 列表格式支持；P2.53 SCOPE+ 排除 progress 文件；P2.54 CHANGELOG 检查限制到 P7/P8；P2.55 并行派发操作级指导；P2.56 review status 字段更新指导；P2.57 P6 evidence-consistency 检查。

**Tech Stack:** Bash, Python 3 (内联), Bats (测试)

---

## 背景

### 问题

T084（1 行 CSS 改动）耗时 9h，T075（P0-P2）耗时 2.5h。30% 是损耗：
- 3 次 gate 拦截因 check-pruning.sh 不认 YAML 列表格式 `phases:`
- 1 次 gate 拦截因 SCOPE+ 误匹配 progress 文件
- 4 次 CHANGELOG WARNING（从 P1 到 P8 每次 commit 都提醒）
- 1 次 gate 拦截因 subagent 返回 approved 但 frontmatter status=draft
- P6 commit 声称 14/14 PASS 但 evidence JSON 实际 8/10
- 并行评审串行执行（3 个 review 串行 30min → 并行应 10min）

### 向后兼容

- 所有脚本修改不改变现有行为（YAML 内联格式仍受支持）
- 新增检查是增量（不删除现有检查）
- 文档修改不改变协议规则

---

## 文件结构

### 修改文件

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-pruning.sh:22-30` | phases 解析支持 YAML 列表格式 |
| `agate/scripts/check-scope-resolved.sh:19` | 排除 progress 文件 |
| `agate/scripts/check-retrospective.sh:37` | 排除 progress 文件 |
| `agate/scripts/pre-commit-gate.sh:247-249` | CHANGELOG 检查限制到 P7/P8 |
| `agate/scripts/check-p6-provenance.sh` | 审计 5 扩展：evidence JSON 与 PASS/FAIL 一致性 |
| `agate/phase-cards/P2-design.md:77-78` | 并行派发操作级指令 |
| `agate/phase-cards/P4-implementation.md:78-79` | 并行派发操作级指令 |
| `agate/assets/templates/dispatch-prompt.md` | review status 字段更新指令 |
| `agate/phase-cards/P6-acceptance.md` | evidence-consistency 声明 |

### 修改测试

| 文件 | 改动 |
|------|------|
| `agate/tests/unit/check-pruning.bats` | YAML 列表格式测试 |
| `agate/tests/unit/check-scope-resolved.bats` | progress 文件排除测试 |
| `agate/tests/unit/check-retrospective.bats` | progress 文件排除测试 |
| `agate/tests/unit/pre-commit-hook.bats` | CHANGELOG 限制到 P7/P8 测试 |
| `agate/tests/unit/check-p6-provenance.bats` | evidence-consistency 测试 |

---

## Task 1: check-pruning.sh 支持 YAML 列表格式 phases (P2.52)

**Files:**
- Modify: `agate/scripts/check-pruning.sh:22-30`
- Modify: `agate/tests/unit/check-pruning.bats`

- [ ] **Step 1: 先写失败测试**

在 `check-pruning.bats` 追加：

```bash
@test "P2.52: YAML list format phases: - P1\\n - P2 → parsed correctly" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P8 --risk-level low)
    # 覆盖 P1 为 YAML 列表格式
    cat > "$dir/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: low
phases:
  - P1
  - P2
  - P4
  - P5
  - P6
  - P8

### 主流程

#### BDD-1: test
- Given test precondition
- When test action
- Then test result
EOF
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/unit/check-pruning.bats --filter "P2.52"`
Expected: FAIL（脚本只认内联格式）

- [ ] **Step 3: 修改 check-pruning.sh**

将 L22-30 的 python3 代码替换为：

```python
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'phases:\s*\[([^\]]+)\]', text)
if m:
    phases = [p.strip() for p in m.group(1).split(',')]
    print(' '.join(phases))
else:
    m = re.search(r'phases:\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)', text)
    if m:
        phases = re.findall(r'-\s+(\S+)', m.group(1))
        print(' '.join(phases))
```

- [ ] **Step 4: 追加 YAML 列表格式 + 裁剪场景测试**

```bash
@test "P2.52b: YAML list format phases with P3 pruned (risk=low) → pass" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P8 --risk-level low)
    cat > "$dir/P1-requirements.md" <<'EOF'
---
agent: test
---
risk_level: low
phases:
  - P1
  - P2
  - P4
  - P5
  - P6
  - P8

### 主流程

#### BDD-1: test
- Given test precondition
- When test action
- Then test result
裁剪 P3: 纯配置改动无业务逻辑
跳过风险: 无 TDD 需求
EOF
    run bash "$AGATE_SCRIPTS/check-pruning.sh" "$dir"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 5: 运行测试验证通过**

Run: `bats agate/tests/unit/check-pruning.bats`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add agate/scripts/check-pruning.sh agate/tests/unit/check-pruning.bats
git commit -m "fix: check-pruning.sh supports YAML list format phases (P2.52)"
```

---

## Task 2: check-scope-resolved.sh + check-retrospective.sh 排除 progress 文件 (P2.53)

**Files:**
- Modify: `agate/scripts/check-scope-resolved.sh:19`
- Modify: `agate/scripts/check-retrospective.sh:37`
- Modify: `agate/tests/unit/check-scope-resolved.bats`
- Modify: `agate/tests/unit/check-retrospective.bats`

- [ ] **Step 1: 先写失败测试**

在 `check-scope-resolved.bats` 追加：

```bash
@test "P2.53: progress file with [SCOPE+] text does not trigger SCOPE check" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    # P2-progress.md 含 [SCOPE+] 字面文本（非声明）
    echo "## P2 progress
- [SCOPE+] 检查: 无新增隐含需求" > "$dir/P2-progress.md"
    # P1 有 SCOPE_RESOLVED（正常情况）
    echo "- [SCOPE_RESOLVED] test" >> "$dir/P1-requirements.md"
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$dir"
    [ "$status" -eq 0 ]
}
```

在 `check-retrospective.bats` 追加：

```bash
@test "RT.SCOPE_PROGRESS: progress file with [SCOPE+] does not trigger retro warning" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    echo "## P2 progress
- [SCOPE+] 检查: 无新增隐含需求" > "$dir/P2-progress.md"
    run bash "$AGATE_SCRIPTS/check-retrospective.sh" "$dir" ".state.yaml"
    [ "$status" -eq 0 ]
    [[ "$output" != *"SCOPE+ 触发"* ]]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/unit/check-scope-resolved.bats --filter "P2.53"`
Expected: FAIL（progress 文件被扫描）

- [ ] **Step 3: 修改 check-scope-resolved.sh**

L19 改为：

```bash
    basename "$f" | grep -qE 'dispatch-context|dispatch-prompt|progress' && continue
```

- [ ] **Step 4: 修改 check-retrospective.sh**

L37 改为：

```bash
        basename "$f" | grep -qE 'dispatch-context|dispatch-prompt|progress' && continue
```

- [ ] **Step 5: 运行测试验证通过**

Run: `bats agate/tests/unit/check-scope-resolved.bats agate/tests/unit/check-retrospective.bats`
Expected: ALL PASS

- [ ] **Step 6: Commit**

---

## Task 3: CHANGELOG 检查限制到 P7/P8 (P2.54)

**Files:**
- Modify: `agate/scripts/pre-commit-gate.sh:247-249`
- Modify: `agate/tests/integration/pre-commit-hook.bats`

- [ ] **Step 1: 先写失败测试**

在 `pre-commit-hook.bats` 追加：

```bash
@test "IT_CHANGELOG_P54: P4 commit without CHANGELOG → no CHANGELOG WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p54")
    mkdir -p "$repo/docs/tasks/T001"
    create_state_yaml "$repo" "T001" "P4"
    echo 'task: test' > "$repo/docs/tasks/T001/P0-brief.md"
    echo '## impl' > "$repo/docs/tasks/T001/P4-implementation.md"
    git_stage "$repo" "docs/tasks/T001/P0-brief.md" "docs/tasks/T001/P4-implementation.md" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'"
    [[ "$output" != *"CHANGELOG"* ]]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/integration/pre-commit-hook.bats --filter "IT_CHANGELOG_P54"`
Expected: FAIL（CHANGELOG WARNING 在 P4 也会出现）

- [ ] **Step 3: 修改 pre-commit-gate.sh**

L247-249 改为：

```bash
    # 2m. CHANGELOG 检查（P1.6）——仅 P8 phase 检查，其他阶段不触发
    # CHANGELOG 是 P8 发布准备产物，P1-P7 不需要
    case "$PHASE" in
        P8)
            bash "$AGATE_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
                echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2
            ;;
    esac
```

- [ ] **Step 4: 追加 P8 正向 CHANGELOG 测试**

在 `pre-commit-hook.bats` 追加：

```bash
@test "IT_CHANGELOG_P54b: P8 commit without CHANGELOG → CHANGELOG WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p54b")
    mkdir -p "$repo/docs/tasks/T001"
    create_state_yaml "$repo" "T001" "P8"
    echo 'task: test' > "$repo/docs/tasks/T001/P0-brief.md"
    echo '## release' > "$repo/docs/tasks/T001/P8-release.md"
    git_stage "$repo" "docs/tasks/T001/P8-release.md" ".state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_ROOT/scripts/pre-commit-gate.sh'"
    [[ "$output" == *"CHANGELOG"* ]]
}
```

- [ ] **Step 5: 运行测试验证通过**

Run: `bats agate/tests/integration/pre-commit-hook.bats`
Expected: ALL PASS

- [ ] **Step 6: Commit**

---

## Task 4: 并行派发操作级指导 (P2.55)

**Files:**
- Modify: `agate/phase-cards/P2-design.md:77-78`
- Modify: `agate/phase-cards/P4-implementation.md:78-79`

- [ ] **Step 1: 更新 P2-design.md 并行派发节**

在 L78（"1. 同时派发所有触发的评审 subagent"）后追加操作级说明：

```markdown
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
```

- [ ] **Step 2: 更新 P4-implementation.md 并行派发节**

在 L79（"1. 同时派发所有触发的评审 subagent"）后追加同样的操作级说明。

- [ ] **Step 3: Commit**

---

## Task 5: dispatch-prompt review status 字段更新指导 (P2.56)

**Files:**
- Modify: `agate/assets/templates/dispatch-prompt.md`

- [ ] **Step 1: 在 dispatch-prompt.md 追加 review status 指导**

在 Header 模板说明节（约 L20 附近，Header 模板之后）追加：

```markdown
## Review 角色特别指令

如果你的角色是评审/验收角色（review / design-review / plan-eng-review / plan-design-review / plan-ceo-review / cso / qa / requirements-review / consistency-reviewer）：
- 产出文件的 Header `status:` 字段初始为 `draft`
- 评审/验收完成后，**必须将 `status:` 改为 `approved` / `rejected` / `needs-revision`**
- gate 脚本读的是 Header 的 `status:` 字段，不是你的返回摘要——两者必须一致
```

- [ ] **Step 2: Commit**

---

## Task 6: P6 evidence-consistency 检查 (P2.57)

**Files:**
- Modify: `agate/scripts/check-p6-provenance.sh`
- Modify: `agate/tests/unit/check-p6-provenance.bats`
- Modify: `agate/phase-cards/P6-acceptance.md`

- [ ] **Step 1: 先写失败测试**

在 `check-p6-provenance.bats` 追加：

```bash
@test "PV.24: evidence JSON shows FAIL but P6 says PASS → exit 1" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    add_p1_bdd "$dir" "test 1"
    add_p1_bdd "$dir" "test 2"
    add_p6_pass "$dir" "BDD-1" "result.json"
    add_p6_pass "$dir" "BDD-2" "result2.json"
    add_evidence_file "$dir" "result.json" '{"bdd_results":[{"id":"BDD-1","status":"pass"},{"id":"BDD-2","status":"fail"}]}'
    add_evidence_file "$dir" "result2.json" '{"test":"data"}'
    echo "- [NO_NEED_CONFIRM]" >> "$dir/P6-acceptance.md"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"BDD-2"* ]]
    [[ "$output" == *"FAIL"* ]]
}

@test "PV.25: evidence JSON all pass + P6 all PASS → exit 0" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    add_p1_bdd "$dir" "test 1"
    add_p6_pass "$dir" "BDD-1" "result.json"
    add_evidence_file "$dir" "result.json" '{"bdd_results":[{"id":"BDD-1","status":"pass"}]}'
    echo "- [NO_NEED_CONFIRM]" >> "$dir/P6-acceptance.md"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: 运行测试验证失败**

Run: `bats agate/tests/unit/check-p6-provenance.bats --filter "PV.2[45]"`
Expected: FAIL（当前不检查 evidence JSON 内容）

- [ ] **Step 3: 修改 check-p6-provenance.sh**

在 L256 `exit 0` 之前（agent 字段检查之后）追加 evidence-consistency 检查：

> **JSON 格式约定**：检查兼容 `bdd_results` 和 `results` 数组字段名，每项含 `id`/`bdd` + `status` 字段。非标准格式的 JSON 静默跳过（不报错也不检查）。这是启发式检查——格式不匹配时退化为不检查，不会误报。

```bash
# 审计 6: evidence JSON 与 P6 PASS/FAIL 声明一致性（P2.57）
# 检查 P6-evidence/ 下的 JSON 文件中 bdd_results 的 status 字段
# 如果 JSON 显示某 BDD 为 fail 但 P6-acceptance.md 标 PASS → 不一致
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
if [ -d "$EVIDENCE_DIR" ]; then
    INCONSISTENCY=$(EVIDENCE_DIR="$EVIDENCE_DIR" P6_FILE="$TASK_DIR/P6-acceptance.md" python3 -c '
import json, os, glob, re, sys

evidence_dir = os.environ["EVIDENCE_DIR"]
p6_file = os.environ["P6_FILE"]

# 从 P6-acceptance.md 提取 PASS 声明的 BDD 编号
pass_bdds = set()
with open(p6_file) as f:
    for line in f:
        m = re.match(r"^\s*-\s*PASS\s+(BDD-\d+)", line, re.IGNORECASE)
        if m:
            pass_bdds.add(m.group(1))

# 从 evidence JSON 提取 fail 的 BDD 编号
fail_in_evidence = set()
for json_path in glob.glob(os.path.join(evidence_dir, "**/*.json"), recursive=True):
    try:
        with open(json_path) as f:
            data = json.load(f)
        results = data.get("bdd_results", data.get("results", []))
        if isinstance(results, list):
            for r in results:
                if isinstance(r, dict):
                    bdd_id = r.get("id", r.get("bdd", ""))
                    status = r.get("status", "").lower()
                    if status == "fail" and bdd_id:
                        fail_in_evidence.add(bdd_id)
    except (json.JSONDecodeError, KeyError):
        continue

# 找不一致：P6 标 PASS 但 evidence 标 FAIL
inconsistent = pass_bdds & fail_in_evidence
for bdd in sorted(inconsistent):
    print(f"{bdd}: P6 标 PASS 但 evidence JSON 显示 FAIL")
' 2>/dev/null || echo "")
    if [ -n "$INCONSISTENCY" ]; then
        echo "GATE PROVENANCE: evidence JSON 与 P6-acceptance.md 声明不一致：" >&2
        echo "$INCONSISTENCY" | sed 's/^/  - /' >&2
        exit 1
    fi
fi
```

- [ ] **Step 4: 追加边界场景测试**

在 `check-p6-provenance.bats` 追加：

```bash
@test "PV.26: non-standard evidence JSON (no bdd_results) → silent skip, exit 0" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    add_p1_bdd "$dir" "test 1"
    add_p6_pass "$dir" "BDD-1" "result.json"
    add_evidence_file "$dir" "result.json" '{"unrelated":"data","no_bdd_results":true}'
    echo "- [NO_NEED_CONFIRM]" >> "$dir/P6-acceptance.md"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}

@test "PV.27: P6 says FAIL + evidence JSON says fail → consistent, exit 0" {
    local dir
    dir=$(create_task_dir P0 P1 P2 P4 P5 P6 P7 P8)
    add_p1_bdd "$dir" "test 1"
    add_p6_fail "$dir" "BDD-1"
    add_evidence_file "$dir" "result.json" '{"bdd_results":[{"id":"BDD-1","status":"fail"}]}'
    echo "- [NO_NEED_CONFIRM]" >> "$dir/P6-acceptance.md"
    run bash "$AGATE_SCRIPTS/check-p6-provenance.sh" "$dir"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 5: 运行测试验证通过**

Run: `bats agate/tests/unit/check-p6-provenance.bats`
Expected: ALL PASS

- [ ] **Step 6: 更新 P6-acceptance.md**

在"核心原则"节追加：

```markdown
**验收报告记录的是验收时的事实，不是修复后的状态。** P6-acceptance.md 的 PASS/FAIL 声明必须基于 evidence 文件的实际输出。如果验收时 BDD 为 FAIL，写 FAIL——修复后重新验收时再改 PASS。不能在同一个 P6 acceptance 里写"修复后 PASS"。
```

- [ ] **Step 7: Commit**

---

## Task 7: 全量验证

- [ ] **Step 1: 全量 bats**

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: ALL PASS

- [ ] **Step 2: consistency**

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

- [ ] **Step 3: shellcheck**

Run: `shellcheck -S warning agate/scripts/*.sh`
Expected: 0 errors

- [ ] **Step 4: count-tests**

Run: `bash agate/tests/scripts/count-tests.sh`
Expected: 计数增加（新增测试）

- [ ] **Step 5: 更新 tests/README.md 覆盖度表**

如有新增测试文件或测试数量变化，更新覆盖度表。

- [ ] **Step 6: Commit**

---

## Self-Review

### 1. Spec coverage

| 需求 | Task |
|------|------|
| P2.52 check-pruning YAML 列表格式 | Task 1 |
| P2.53 SCOPE+ 排除 progress 文件 | Task 2 |
| P2.54 CHANGELOG 限制到 P7/P8 | Task 3 |
| P2.55 并行派发操作级指导 | Task 4 |
| P2.56 review status 字段指导 | Task 5 |
| P2.57 P6 evidence-consistency | Task 6 |
| 全量验证 | Task 7 |

### 2. Placeholder scan

无 TBD/TODO。所有 step 含具体代码或具体修改指令。

### 3. Type consistency

- `phases:` 解析在 check-pruning.sh 中两种格式都支持
- `progress` 排除在 check-scope-resolved.sh 和 check-retrospective.sh 中一致
- evidence JSON 检查的 `bdd_results` 字段名与 verifier 角色文件描述一致

---

## Execution Handoff

Plan complete. Two execution options:

**1. Subagent-Driven (recommended)** - Fresh subagent per task, review between tasks

**2. Inline Execution** - Execute in this session

Which approach?
