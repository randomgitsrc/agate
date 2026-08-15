# agate 通用化复盘改进 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 T086 复盘中 4 条已确认可通用化的改进落地到 agate 协议本体，且不绑定任何具体项目或技术栈。

**Architecture:** 4 个独立小改进，互不耦合，可独立评审/提交，但都改 agate 协议本体，需走 self-gate-review。其中 A2（candidate_count 强制）是唯一破坏性变更，需 minor 版本 bump（v0.31.0）；其余为文档补强（角色卡模板 / 检查项），非破坏性。

**Tech Stack:** bash（check-gate.sh）+ Markdown（角色卡）+ bats（测试）。

**来源：** `docs/reviews` 中 T086 复盘（agate 通用化取舍后保留 4 条）：
- A1：角色卡补 gate 解析字段的 YAML 模板（消除"语义对但格式错"）
- A2：P2 候选方案判定从正则改显式 `candidate_count:` 字段（纯强制，消除脆弱正则）
- B1：architect.md minimal_validation 补"删除/移动路由接口类必须验证落点"检查项
- C1：verifier.md 截图流程补 CSS 过渡 settle-wait

---

## File Structure

- **Modify** `agate/scripts/check-gate.sh` — A2：P2 分支候选方案计数从"正则数标题"改为"读 `candidate_count:` 字段"，删除正则。
- **Modify** `agate/assets/execution-roles/analyst.md` — A1：补 gate 解析字段的 YAML 模板块。
- **Modify** `agate/assets/execution-roles/architect.md` — A1/A2/B1：补 `candidate_count:` 字段到输出规格 + `minimal_validation` 删除/移动路由接口检查项。
- **Modify** `agate/assets/templates/task-files.md` — A2：给 P2-design 产出模板补 `candidate_count:` 字段（architect 实际复制的模板）。
- **Modify** `agate/assets/execution-roles/verifier.md` — C1：截图流程补 settle-wait。
- **Modify** `agate/tests/unit/check-gate.bats` — A2：给受影响的 P2 测试补 `candidate_count:`；新增纯强制语义测试。
- **Modify** `agate/tests/helpers/fixtures.bash` — A2：新增 `add_p2_candidate_count` helper 减少 churn。
- **Modify** `agate/tests/README.md` — 用例数更新。
- **Modify** `README.md`, `CHANGELOG.md` — v0.31.0 版本 bump。

---

### Task 1: A2 — check-gate.sh 改读 `candidate_count:` 字段（纯强制）

**Files:**
- Modify: `agate/scripts/check-gate.sh:97-114`
- Modify (test helper): `agate/tests/helpers/fixtures.bash`
- Test: `agate/tests/unit/check-gate.bats`

**背景**：当前 P2 分支用 `grep -cE '^#{2,4}\s*(候选方案|方案\s*[A-Za-z0-9一二三四五]|Alternative|Option)'` 数候选方案标题。`### 方案：描述`（全角冒号）匹配不上 → 假阳性误拦。改为强制 `candidate_count:` 字段，删除正则。

- [ ] **Step 1: 新增 helper `add_p2_candidate_count`**

在 `agate/tests/helpers/fixtures.bash` 末尾（`add_p6_need_confirm` 之后）追加：

```bash
# 用法：add_p2_candidate_count <task_dir> <count>
# 在 P2-design.md 加 candidate_count 字段（替换或追加）
add_p2_candidate_count() {
    local dir="$1"
    local count="$2"
    local p2="$dir/P2-design.md"
    if grep -q "^candidate_count:" "$p2" 2>/dev/null; then
        sed -i "s|^candidate_count:.*|candidate_count: ${count}|" "$p2"
    else
        echo "candidate_count: ${count}" >> "$p2"
    fi
}
```

- [ ] **Step 2: 写失败测试（先红）**

在 `agate/tests/unit/check-gate.bats` 的 P2 区块末尾追加以下测试：

```bash
@test "G2.26 check-gate.sh P2 全角冒号标题 + candidate_count 字段 期望 exit 2（纯强制）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 方案：方案一
### 方案：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    add_p2_candidate_count "$dir" 2
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}

@test "G2.27 check-gate.sh P2 缺 candidate_count 字段 期望 exit 1（纯强制）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 简单，B 稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    add_p2_review "$dir"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"candidate_count"* ]]
}
```

> **红绿说明**：G2.26 是唯一"真红"（当前正则数全角冒号标题=0 → exit 1，但期望 2）。G2.27 用 2 个 `### 候选方案 A/B` 标题构造——当前正则数出 2 → flow 越过计数检查 → 期望 exit 1 但当前 exit 2，同样是红。**不要**用 1 个标题构造 G2.27（那样当前就 exit 1，测试会"假绿"逃过红阶段）。

运行：`bats agate/tests/unit/check-gate.bats --filter 'G2.26\|G2.27'`
预期：两个都 FAIL（红）。

- [ ] **Step 3: 改 check-gate.sh P2 分支**

把 `agate/scripts/check-gate.sh` 第 100-114 行的候选方案计数逻辑替换为读字段：

```bash
      P2_FILE="$TASK_DIR/P2-design.md"
      if [ -f "$P2_FILE" ]; then
          # v0.31.0：候选方案数改为显式 candidate_count 字段（纯强制），不再用正则数标题
          # 消除脆弱标题匹配（如全角冒号 # 方案：），gate 只检查字段存在性（自声明 nudge）
          CANDIDATE_COUNT=$(grep -oE '^candidate_count:[[:space:]]*[0-9]+' "$P2_FILE" 2>/dev/null | grep -oE '[0-9]+$' | head -1 || echo 0)
          CANDIDATE_COUNT=$(echo "$CANDIDATE_COUNT" | tail -1)
          if [ -z "$CANDIDATE_COUNT" ]; then
              CANDIDATE_COUNT=0
          fi
          P1_FILE="$TASK_DIR/P1-requirements.md"
          MIN_CANDIDATES=2
          if [ -f "$P1_FILE" ]; then
              if grep -qE '^(design_trivial|follows_existing_pattern):\s*\S' "$P1_FILE" 2>/dev/null; then
                  MIN_CANDIDATES=1
              fi
          fi
          if [ "$CANDIDATE_COUNT" -lt "$MIN_CANDIDATES" ]; then
              echo "GATE P2: P2-design.md candidate_count=${CANDIDATE_COUNT}，需至少 ${MIN_CANDIDATES} 个候选方案（design_trivial/follows_existing_pattern 时可只写 1）。请显式声明 candidate_count 字段" >&2
              exit 1
          fi
```

> 注意：`grep -oE '^candidate_count:[[:space:]]*[0-9]+'` 若无匹配，`grep -oE '[0-9]+$'` 也空 → `|| echo 0` 兜底赋 0。但 `head -1` 后若为空，`CANDIDATE_COUNT=""`，需 `[ -z ]` 归 0。上面已处理。
>
> **保留原错误消息子串 `需至少 ${MIN_CANDIDATES} 个候选方案`**：既有测试 G2.1（check-gate.bats:39）断言 `[[ "$output" == *"需至少 2 个候选方案"* ]]`，是唯一引用该消息的测试。新消息必须保留该子串，否则 G2.1 仍 exit 1 但断言失败。

- [ ] **Step 4: 更新受影响的既有测试**

`check-gate.bats` 中 **P2 阶段**（运行 `check-gate.sh P2`）且创建 P2-design.md 的测试需补 `candidate_count:`。分两类：

**A. 期望 exit 2 的（~20 个）**：在 P2-design.md heredoc 之后、`add_p2_review`/`cat > P2-review.md` 之前，插入 `add_p2_candidate_count "$dir" N`（N=该测试实际候选方案标题数）。

**B. 期望 exit 1 但因其它原因失败的（G2.8, G2.10, G2.10a, G2.12, G2.13, PG.P2REVIEW, G2.19 等 ~8 个）**：需补 `candidate_count` 使 flow 越过计数检查、到达原失败点，否则 candidate_count 检查会提前拦截并改变失败原因。

**需特别注意**：
- **G2.1/G2.2/G2.4/G2.5**（0/1/h5 候选、G2.5 无 P2-design 且断言串含 "P2-design.md" 是 awk 误报）：**不要补 candidate_count**。G2.1 靠新消息保留的 `需至少 2 个候选方案` 子串仍通过；G2.2/G2.4 只断言 exit 1，不受影响；G2.5 是 awk 粗定位的误报，补了反而会创建 P2-design.md 改变其 exit。
- **P5 阶段测试（G5.1, G5_CMD.1-5）**：也创建 P2-design.md 但运行 `check-gate.sh P5`，**不需要** candidate_count。不要误改。
- 插入位置：是 **P2-design.md heredoc 之后**，不是"add_p2_review 之前"——因为 G2.10/G2.10a/G2.11/G2.18/G2.19/G2.20 是 `cat > P2-review.md` 直接写，无 `add_p2_review` 调用。

用以下命令**粗定位**（列出所有创建 P2-design.md 的测试，含 P5 阶段测试，需按下方说明人工排除 G2.1/G2.2/G2.4 及 P5 测试）：

```bash
# 列出 P2 阶段测试名（第一个 awk 段收集 @test 名，第二个检查其体内是否创建 P2-design.md）
awk '
  /^@test/{name=$0; has=0}
  /P2-design.md/{has=1}
  /^}/{ if (has) print name }
' agate/tests/unit/check-gate.bats
```

**Step 4b: 处理过时的正则边界测试（N1）**
删除正则后，G2.25（"h4 支持"）**会因缺 candidate_count 从 exit 2 变 exit 1 而 FAIL**，需补 `add_p2_candidate_count` 或改为普通"candidate_count 满足 MIN → exit 2"用例。G2.4（"h5 不识别"）**仍绿**（本就 exit 1，缺字段仍是 exit 1）——但它的正则边界语义已不存在，建议改为显式"lower candidate_count → exit 1"测试（或并入 G2.27），去掉对标题层级的依赖。

- [ ] **Step 5: 跑测试验证全绿**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```
预期：全绿，0 not ok。

- [ ] **Step 6: shellcheck + consistency + 计数**

```bash
shellcheck -S warning agate/scripts/check-gate.sh
python3 agate/scripts/check-protocol-consistency.py
bash agate/tests/scripts/count-tests.sh
```
预期：shellcheck clean；consistency 0 ERROR；用例数更新到 `agate/tests/README.md`。

- [ ] **Step 7: Commit**

```bash
git add agate/scripts/check-gate.sh agate/tests/helpers/fixtures.bash agate/tests/unit/check-gate.bats
git commit -m "refactor: P2 候选方案判定改显式 candidate_count 字段 (v0.31.0 BREAKING)

T086 复盘 A2：check-gate.sh 用正则数候选方案标题，`### 方案：`（全角冒号）
匹配不上导致假阳性误拦。改为强制 candidate_count: 字段，删除脆弱正则。

gate 只检查字段存在性（自声明 nudge），不做语义真实性校验——与跳过风险/
implicit_coupling 同构。design_trivial/follows_existing_pattern 时 MIN=1 保留。

self-gate-review: agate/scripts/check-gate.sh"
```

---

### Task 2: A1 — analyst.md 补 gate 解析字段 YAML 模板

**Files:**
- Modify: `agate/assets/execution-roles/analyst.md`

**背景**：check-pruning.sh / check-gate.sh 用 YAML 正则解析 `risk_level`/`phases`/`design_trivial`/`follows_existing_pattern` 等字段，但 analyst.md 只用一句散文描述，未给可复制模板 → analyst 写"语义对但格式错"（T086 A1 命中 2 次）。

- [ ] **Step 1: 在 analyst.md 输出节补模板块**

在 `analyst.md` 第 36 行（裁剪说明）附近的"裁剪说明"条目下，追加可复制 YAML 模板。把第 36 行：

```bash
5. **裁剪说明**：判定任务复杂度，声明走哪些阶段（如 `phases: [P1,P4,P5,P6,P8]`），**每个跳过的阶段写明理由**
```

改为：

```bash
5. **裁剪说明**：判定任务复杂度，声明走哪些阶段，**每个跳过的阶段写明理由**。**必须用下方机器可解析的 YAML 格式**（gate 脚本按此正则解析，散文表述不会被识别）：

```yaml
risk_level: low            # low / medium / high
phases: [P1, P4, P5, P6, P8]   # P1 必填，P2/P4/P5/P6 不可裁，仅 low 可裁 P3，P7/P8 有条件可裁
跳过风险: 说明裁剪每个阶段的风险评估（裁剪声明必备）
```

仅在适用时声明以下**可选**字段（gate 按需解析）：
```yaml
design_trivial: true              # 若 P2 只需 1 个候选方案（简单/无争议）
follows_existing_pattern: [src/foo.py]  # 若 P2 遵循既有模式
implicit_coupling: true           # 若改动涉及隐式耦合（P7 裁剪时会拦截）
coupling_checklist: [api-schema: checked, data-model: checked]  # 裁剪 P7 时必备
internal_only: true               # 若裁剪 P8
internal_only_reason: 说明        # 裁剪 P8 时必填
override: 说明                    # 若裁剪声明与执行不一致时
```
```

- [ ] **Step 2: 验证无语法/一致性破坏**

```bash
python3 agate/scripts/check-protocol-consistency.py
```
预期：0 ERROR（这些字段 analyst.md 之前散落，无既有锚点要求这一格式）。

- [ ] **Step 3: Commit**

```bash
git add agate/assets/execution-roles/analyst.md
git commit -m "docs: analyst.md 补 gate 解析字段 YAML 模板 (v0.31.0)

T086 复盘 A1：P1/P2 阶段 gate 脚本按正则解析 risk_level/phases/
design_trivial/follows_existing_pattern 等字段，但角色卡只用散文描述，
导致 analyst 产出'语义对但格式错'（命中 2 次）。补机器可解析模板，源头消除。

self-gate-review: agate/assets/execution-roles/analyst.md"
```

---

### Task 3: A1+A2+B1 — architect.md 补 candidate_count 字段 + minimal_validation 删除/移动验证

**Files:**
- Modify: `agate/assets/execution-roles/architect.md`
- Modify: `agate/assets/templates/task-files.md`

**背景**：A2 引入 `candidate_count:` 必填字段，architect.md 输出规格必须同步；B1 是 minimal_validation 章节补一条删除/移动路由接口的强制验证项。

- [ ] **Step 1: 输出规格补 candidate_count 字段**

在 `architect.md` 第 36 行 `packages:` 之前，插入：

```bash
  - `candidate_count: N` — **必填**。本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可为 1）。gate 脚本按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
```

- [ ] **Step 1b: task-files.md P2-design 模板补 candidate_count 字段**

在 `agate/assets/templates/task-files.md` 第 193 行代码块内，第 194 行（`## 1. 候选方案`）之前插入该字段（architect 实际复制此模板，需同步）：

````markdown
## 0. 候选方案数（必填，v0.31.0）
candidate_count: 2   # 本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1）。gate 按此字段校验，不再解析标题。

## 1. 候选方案（v0.6：至少 2 个 + 权衡 + 选择理由）
````

- [ ] **Step 2: minimal_validation 章节补删除/移动验证项**

在 `architect.md` 第 84-85 行（"什么需要最小验证" + "纯代码逻辑"两行）之后追加：

```bash
    **涉及删除/移动路由、接口、注册表项时（T086 B1 教训）**：即使判定为"纯代码逻辑"，也必须验证"删除后，原本依赖这条路由/接口的请求会流向哪个兜底分支"。这种"代码逻辑正确性假设"不因"纯代码逻辑"标签豁免——在 minimal_validation 里体现为 `method: "读代码验证路由匹配顺序"` 这类最小验证动作，或明确说明已验证落点。
```

- [ ] **Step 3: 验证**

```bash
python3 agate/scripts/check-protocol-consistency.py
```
预期：0 ERROR。

- [ ] **Step 4: Commit**

```bash
git add agate/assets/execution-roles/architect.md agate/assets/templates/task-files.md
git commit -m "docs: architect.md + task-files.md 补 candidate_count 字段 + 删除/移动路由验证项 (v0.31.0)

A2: 输出规格补必填 candidate_count 字段（与 Task 1 check-gate.sh 同步），
且同步到 P2-design 产出模板 task-files.md（architect 实际复制处）。
B1 (T086): minimal_validation 补'删除/移动路由接口必须验证删除后落点'，
不因'纯代码逻辑'豁免——原文案 B1 是唯一造成生产代码 bug 的根因。

self-gate-review: agate/assets/execution-roles/architect.md agate/assets/templates/task-files.md"
```

---

### Task 4: C1 — verifier.md 截图流程补 settle-wait

**Files:**
- Modify: `agate/assets/execution-roles/verifier.md`

**背景**：T086 C1。Playwright 截图 `waitForSelector(state:'visible')` 后立即截图，CSS 过渡（`opacity 0.15s ease`）期间可能截到淡入中间帧。需补过渡完成确认。

- [ ] **Step 1: 在 UI 处理流程节补截图步骤**

在 `verifier.md` 第 143 行（"1. Playwright 跑完，截图存入..."）之前，插入：

```bash
0. **截图前确认过渡完成**：对含 CSS 过渡/动画的页面（路由淡入淡出、hover 效果等），`waitForSelector(state:'visible')` 只保证元素非零尺寸且非 display:none，**不保证 opacity===1**。截图前用 `page.evaluate` 确认目标元素 `getComputedStyle().opacity === '1'`，或 `waitForTimeout(200)` 等待过渡结束，避免截到淡入中间帧。低对比度/有淡入动画的设计系统里此风险反复出现。
```

- [ ] **Step 2: 验证 + Commit**

```bash
python3 agate/scripts/check-protocol-consistency.py   # 预期 0 ERROR
git add agate/assets/execution-roles/verifier.md
git commit -m "docs: verifier.md 截图前补 CSS 过渡 settle-wait (v0.31.0)

T086 复盘 C1：waitForSelector visible 不保证 opacity===1，CSS 过渡期间
可能截到淡入中间帧。补过渡完成确认步骤（getComputedStyle opacity 检查或
waitForTimeout），避免低对比度+淡入动画设计系统反复踩坑。

self-gate-review: agate/assets/execution-roles/verifier.md"
```

---

### Task 5: 版本 bump v0.31.0 + 收尾验证

**Files:**
- Modify: `README.md`（version badge）
- Modify: `CHANGELOG.md`（[v0.31.0] 区）
- Modify: `agate/tests/README.md`（用例数，若 Task 1 后未更新）

- [ ] **Step 1: 全量验证**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
shellcheck -S warning agate/scripts/*.sh
python3 agate/scripts/check-protocol-consistency.py
bash agate/tests/scripts/count-tests.sh
```
预期：全绿 / clean / 0 ERROR / 用例数 = README。

- [ ] **Step 2: 更新 README badge + CHANGELOG**

README.md version badge `v0.30.3` → `v0.31.0`。CHANGELOG.md 顶部加 `[v0.31.0]` 区，记录 4 项改进（A1/A2/B1/C1），标注 A2 为 BREAKING。

- [ ] **Step 3: Commit**

```bash
git add README.md CHANGELOG.md agate/tests/README.md
git commit -m "chore: v0.31.0

BREAKING: P2-design.md 必填 candidate_count 字段（替代正则数标题）。
通用化复盘改进：A1 角色卡 YAML 模板 / A2 candidate_count 强制 / B1 路由删除验证 / C1 截图 settle-wait。

self-gate-review: agate/scripts/check-gate.sh agate/assets/execution-roles/architect.md agate/assets/execution-roles/analyst.md agate/assets/execution-roles/verifier.md"
```

- [ ] **Step 4: 独立实施评审**

派发独立 subagent 做实现评审（superpowers:requesting-code-review），确认 4 项都实现、无回归、self-gate-review 路径齐全。评审通过后走 PR 合并。

---

## Self-Review

**1. Spec coverage（4 条通用化项全覆盖）：**
- A1 → Task 2（analyst.md）+ Task 3 Step 1（architect.md candidate_count）
- A2 → Task 1（check-gate.sh + 测试）+ Task 3 Step 1（architect.md 输出规格）
- B1 → Task 3 Step 2（architect.md minimal_validation）
- C1 → Task 4（verifier.md）
- 版本 bump → Task 5

**2. Placeholder scan：** 无 TBD/TODO；所有代码步骤含完整代码。架构师/角色卡补丁均为精确插入位置说明。

**3. Type consistency：** `add_p2_candidate_count` helper 在 Task 1 Step 3 定义、Step 4 被测试使用，命名一致；check-gate.sh 里 `CANDIDATE_COUNT` 变量名与现有 MIN_CANDIDATES 逻辑一致。`candidate_count:` 字段在 check-gate.sh（Task 1）、architect.md（Task 3 Step 1）、task-files.md（Task 3 Step 1b）、测试（Task 1）四处命名一致。

**已识别风险：** ~28 个既有 P2 测试需补 `candidate_count:`（Task 1 Step 4）——churn 真实但机械。两类需人工核对：① G2.1/G2.2/G2.4 本就因候选少失败，**不补**；② P5 阶段测试不补。新错误消息保留 `需至少 ${MIN_CANDIDATES} 个候选方案` 子串以维持 G2.1 断言。若个别测试原本依赖"缺字段→走别的分支"，需人工核对 flow 顺序，避免 candidate_count 检查提前拦截掩盖原测试意图。

**评审修复记录（独立评审 2 轮）：**
- 第 1 轮：✗ 37 → **~28** 个需补字段，且排除 6 个 P5 阶段测试（G5.1/G5_CMD.*）；✗ 新错误消息破坏 G2.1 断言 → 保留 `需至少 ${MIN_CANDIDATES} 个候选方案` 子串；✗ task-files.md 产出模板未更新 → 补 Task 3 Step 1b；✗ 插入位置写"add_p2_review 前"但部分测试 `cat >` 直写 → 改为"P2-design.md heredoc 之后"
- 第 2 轮：✗ 精确数 ~28 → **27**（G2.5 无 P2-design；B 类 ~8 → 7）；✗ G2.27 红阶段构造会"假绿" → 改用 2 个标题使真红；✗ 过时正则测试 G2.4/G2.25 语义不再存在 → 补 Step 4b；✗ 定位 awk 命令无效 → 改用状态机 awk
- 第 3 轮（GO）：✗ G2.5 是 awk 粗定位误报 → 加入 Step 4 手动排除清单；✗ G2.4 措辞（仍绿不 FAIL）→ 修正 Step 4b。无阻断项，计划可实施