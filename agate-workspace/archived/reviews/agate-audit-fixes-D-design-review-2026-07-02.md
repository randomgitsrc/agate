---
task_id: agate-audit-fixes-D-design-review
agent: main
date: 2026-07-02
status: 评审完成
评审对象: docs/plans/agate-audit-fixes-D-design-2026-07-02.md
来源: docs/plans/agate-audit-fixes-2026-07-01.md §D + docs/reviews/agate-audit-fixes-plan-review-2026-07-01.md §D
---

# D 组设计文档评审：门槛表对齐修复

## 评审方法

逐项对照设计文档的决策、代码片段、测试计划与隐藏依赖，结合以下源文件验证：

- `agate/scripts/check-gate.sh`（#13 修改对象，当前 133 行）
- `agate/dispatch-protocol.md` L570-590（门槛表）
- `agate/tests/unit/check-gate.bats`（现有 33 用例）
- `agate/scripts/check-protocol-consistency.py`（CHECK 8/9 锚点表）
- `agate/tests/helpers/fixtures.bash`（`create_task_dir` 构造逻辑）
- `agate/assets/templates/task-files.md`（P2 模板四字段声明）
- `agate/assets/execution-roles/architect.md`（四字段定义）

---

## #12 P1 门槛不实现

### 决策

**PASS** — 合理。P1 gate 设计为 exit 2，grep 检查改动大且影响主 Agent 判断流程。文档 grep 命令仍列在门槛表供主 Agent 手动执行。

### 代码

不涉及。

### 测试

不涉及。

### 隐藏依赖

无。

---

## #13 P2 门槛对齐

### 决策

**PASS** — 同步文档和脚本的决策方向正确。评审 D.2 指出的两个问题（status:approved 查错文件、遗漏四字段计数）在本设计文档中均已修复。

### 代码：status:approved 检查

**PASS** — 查 P2-review.md 正确。

代码片段：
```bash
P2_REVIEW="$TASK_DIR/P2-review.md"
if [ -f "$P2_REVIEW" ]; then
    if ! grep -qE 'status:\s*approved' "$P2_REVIEW" 2>/dev/null; then
        echo "GATE P2: P2-review.md 缺 status: approved" >&2
        exit 1
    fi
fi
```

逐项验证：

1. **文件路径正确**：`$TASK_DIR/P2-review.md`，与文档门槛表 `grep 'status: approved' P2-review.md` 一致 ✓
2. **正则 `status:\s*approved`**：比文档的 `status: approved` 更宽松（允许 YAML 中冒号后多空格），合理 ✓
3. **`2>/dev/null`**：冗余但不影响正确性。`[ -f "$P2_REVIEW" ]` 已守卫文件存在，grep 不会报错。保留无害 ✓
4. **P2-review.md 不存在时放行**：设计明确说"P2-review.md 不存在时跳过 status 检查"，代码 `[ -f "$P2_REVIEW" ]` 实现了此逻辑 ✓。但需注意：这意味着 P2 阶段刚完成（还没评审）时，只要 count + 四字段 + form 都通过就 exit 2 放行——**这是正确的**，因为评审文件可能还没创建，exit 2 本身就是"需主 Agent 自判"。

**ISSUE（一般）** — status:approved 检查放在 `CANDIDATE_COUNT >= 2` 条件块**内部**，但设计文档代码片段把 `if [ -f "$P2_REVIEW" ]` 放在 `CANDIDATE_COUNT >= 2` 通过后、form check 之前。当前 check-gate.sh L25 的 `if [ -f "$P2_FILE" ]` 守卫了整个 P2 分支，所以 P2_FILE 不存在时整个分支跳过（exit 2）。新加的 status:approved 检查应放在**哪里**？

设计文档说"放置顺序：count check → status:approved → 四字段 → form check → exit 2"。但注意 count check 和 form check 都在 `if [ -f "$P2_FILE" ]` 内部。status:approved 查的是 P2-review.md（不是 P2_FILE），所以它**可以脱离** `if [ -f "$P2_FILE" ]` 独立存在。但如果 P2_FILE 不存在（design_trivial 裁剪场景），P2 case 直接 exit 2（L37），不会走到 status:approved 检查——这也是正确的。

**实际嵌入位置建议**：在 L35（form check 通过后）和 L37（exit 2）之间插入 status:approved + 四字段检查。这符合设计文档的放置顺序，且逻辑上 count → form → status → 四字段 → exit 2 也合理（先查 P2 文件自身内容，再查外部评审文件）。

**但设计文档说顺序是 count → status → 四字段 → form → exit 2**，把 status 放在 form 之前。功能上无差异（都是 exit 1），但错误消息清晰度有影响：先查 status:approved（更基础——评审结论）再查 form（nudge）比反过来更合理。**建议按设计文档顺序**：count → status → 四字段 → form → exit 2。

### 代码：四字段计数

**PASS** — 正确。

代码片段：
```bash
FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' "$P2_FILE" 2>/dev/null || echo 0)
FIELD_COUNT=$(echo "$FIELD_COUNT" | tail -1)
if [ "$FIELD_COUNT" -lt 4 ]; then
    echo "GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 ${FIELD_COUNT}）" >&2
    exit 1
fi
```

逐项验证：

1. **字段名与文档一致**：`packages|domains|ui_affected|gate_commands`，与 dispatch-protocol.md:577 门槛表 `^(packages|domains|ui_affected|gate_commands):` 完全一致 ✓
2. **字段名与模板一致**：task-files.md L153-154, 196-201 有 `packages:`, `domains:`, `ui_affected:`, `gate_commands:` ✓
3. **字段名与 architect.md 一致**：L36-39 明确定义了这四个字段 ✓
4. **`|| echo 0` + `| tail -1`**：符合 AGENTS.md 约定（grep -c 无匹配时 exit 1，|| echo 0 产生双行）✓
5. **`< 4` 而非 `!= 4`**：设计文档说"允许额外字段（如 env_constraints、files_to_read）"，用 `< 4` 拦截不足 4 个的情况，正确 ✓
6. **查的是 `$P2_FILE`（P2-design.md）**：与文档门槛表 `grep -cE ... P2-design.md` 一致 ✓（四字段属于设计方案，不是评审结论）
7. **`2>/dev/null`**：P2_FILE 在 L25 已有 `[ -f "$P2_FILE" ]` 守卫，此处冗余但无害 ✓

### 代码：门槛表文档改动

**ISSUE（一般）** — 门槛表改动中追加了 `含'权衡'或'选择理由'描述`，但这部分是 C 组 #10 form check 的内容，不是 D 组 #13 的范围。混入 D 组门槛表改动虽然功能正确（门槛表应反映脚本全部行为），但增加了跨组耦合。

设计文档门槛表改动：
```markdown
| P2→P3 | 方案已批准 | `scripts/check-gate.sh P2` → 候选方案 ≥2 + `grep 'status: approved' P2-review.md` → 命中 + `grep -cE '^(packages|domains|ui_affected|gate_commands):' P2-design.md → =4` + 含'权衡'或'选择理由'描述 |
```

**问题**：
1. 门槛表行首加了 `scripts/check-gate.sh P2 →` 前缀——这改变了门槛表的格式风格（其他行都是"主 Agent 亲自执行"的命令，不以脚本名开头）。建议保持原有风格，把脚本检查列为补充说明。
2. `=4` 与脚本的 `< 4` 逻辑不一致。门槛表写 `=4` 是"最小要求"，脚本用 `< 4` 是"至少 4 个"。建议门槛表改为 `≥4` 以与脚本行为一致（允许额外字段）。
3. `含'权衡'或'选择理由'描述` 缺少具体判定命令。其他门槛都有可执行命令，这里只有描述。建议补 `grep -qE '权衡|选择理由' P2-design.md → 命中`。

### 测试计划

**ISSUE（一般）** — 测试覆盖不够充分。

| ID | 描述 | 期望 | 评价 |
|----|------|------|------|
| G2.10 | P2 有候选方案 + 权衡，但 P2-review.md 无 status:approved | exit 1，含"status: approved" | **PASS** ✓ sad path |
| G2.11 | P2 有候选方案 + 权衡 + P2-review.md 有 status:approved | exit 2（happy path） | **ISSUE** — 缺四字段。此测试的 P2-design.md 必须包含四字段，否则会因为四字段检查 exit 1 而非 exit 2。设计文档未说明 happy path 测试需同时满足四字段 |
| G2.12 | P2-design.md 缺字段（<4） | exit 1，含"缺字段" | **PASS** ✓ sad path |

**缺失测试**：

1. **P2-review.md 不存在**：有候选方案 + 权衡 + 四字段，但无 P2-review.md → 应 exit 2（跳过 status 检查）。这是设计文档隐藏依赖 #2 明确提到的行为，必须有测试覆盖。
2. **P2-review.md 存在但无 status 字段**（区别于 G2.10 的"有 status 但非 approved"）：P2-review.md 有内容但不含 status 行 → grep -qE 不命中 → exit 1。G2.10 已隐含覆盖此场景（"无 status:approved"包括"无 status 字段"和"status 非 approved"），但建议测试描述更明确。
3. **四字段恰好 4 个** vs **4+ 个**：门槛表写 `=4`，脚本用 `< 4`。应有测试验证 5 个字段也通过（如 P2-design.md 含 packages + domains + ui_affected + gate_commands + files_to_read → FIELD_COUNT=5 → `< 4` 不成立 → 放行）。

### 隐藏依赖

**PASS** — 三个依赖均已识别：

1. **G2.3/G2.6/G2.7/G2.9 会变红**：正确。这四个测试的 P2-design.md 不含四字段（packages/domains/ui_affected/gate_commands），加四字段检查后会 exit 1。需要同步更新测试 fixture 补四字段。✓
2. **P2-review.md 不存在时放行**：正确。✓ 但如上所述缺测试覆盖。
3. **四字段计数用 `≥` 不用 `=`**：正确。✓ 但门槛表文档仍写 `=4`，应改为 `≥4`。

---

## #6 P4 路径偏离：改文档

### 决策

**PASS** — 改文档对齐脚本正确。脚本查暂存区（`git diff --cached`）比查"P4-implementation/ 下文件非空"更适合 pre-commit 场景。

### 代码

门槛表改动：
```markdown
# 当前：P4-implementation/ 下文件非空 + `git log --oneline -1` → 含 "P4" 或 "wf(Txxx-P4)"
# 改为：暂存区含非 md/yaml 文件（`git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'`）
```

**PASS** — 与 check-gate.sh:44 一致：
```bash
git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state' && exit 0 || exit 1
```

文档的 grep 命令 `grep -qvE '\.(md|yaml)$|^\.state'` 与脚本完全一致 ✓

### 测试

不涉及（纯文档改动）。

### 隐藏依赖

**NOTE** — CHECK 8 锚点（L461）要求 check-gate.sh 含 `--cached` 关键词，当前已有。改文档不影响此锚点。✓

---

## #16 P4 git log → --cached

### 决策

**PASS** — 正确。与 #6 合并修改。

### 代码

已在 #6 中一并修改（去掉 git log，改为 --cached）✓

### 测试

不涉及。

### 隐藏依赖

无额外依赖。

---

## G2.3/G2.6/G2.7/G2.9 变红

### 受影响测试逐一验证

**G2.3**（L42-54）：P2-design.md 内容为：
```
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
```
无四字段 → 四字段检查 FIELD_COUNT=0 → exit 1。**确认变红** ✓

需补四字段。最小补法：
```
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
```

**G2.6**（L431-443）：P2-design.md 内容为：
```
# P2 design
### 方案A
### 方案B
## 权衡
A 简单，B 稳健。
```
无四字段 → **确认变红** ✓。同上补法。

**G2.7**（L445-457）：P2-design.md 内容为：
```
# P2 design
## 候选方案 A
## 候选方案 B
## 权衡
A 简单，B 稳健。
```
无四字段 → **确认变红** ✓。同上补法。

**G2.9**（L89-101）：P2-design.md 内容为：
```
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
方案 A 更简单但性能差，方案 B 复杂但性能好。
```
无四字段 → **确认变红** ✓。同上补法。

**ISSUE（一般）** — 设计文档说"G2.3/G2.6/G2.7/G2.9 需补四字段"但未提及 G2.10/G2.11/G2.12 新增测试的 P2-design.md 也需含四字段。特别是 G2.11（happy path）如果 P2-design.md 不含四字段，会因为四字段检查 exit 1 而非 exit 2。**所有新增和修改的 P2 测试 fixture 都必须包含四字段。**

另外注意：**G2.1/G2.2/G2.4/G2.5/G2.8 不受影响**：
- G2.1/G2.2/G2.4：候选方案 < 2，在 count check 阶段已 exit 1，不会走到四字段检查 ✓
- G2.5：P2 文件不存在，跳过整个 P2 分支 exit 2 ✓
- G2.8：候选方案 ≥2 但无权衡，在 form check 阶段 exit 1。但此时四字段检查**尚未执行**（按设计文档顺序 count → status → 四字段 → form → exit 2，如果 form 在四字段之后的话）。**等等**——设计文档说放置顺序是 count → status → 四字段 → form → exit 2。那 G2.8（无权衡）会先过 count，再过 status（假设无 P2-review.md），再过四字段——**G2.8 的 P2-design.md 也缺四字段，会在四字段检查处 exit 1 而非 form check 处 exit 1**。

**ISSUE（严重）** — G2.8 也会变红！设计文档只列了 G2.3/G2.6/G2.7/G2.9，遗漏了 G2.8。

G2.8 的 P2-design.md：
```
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
```
无四字段，会在四字段检查 exit 1，但期望是在 form check exit 1（输出含"权衡"）。如果补了四字段，则 G2.8 能正确走到 form check 并 exit 1。所以 G2.8 **也必须补四字段**。

---

## CHECK 9 锚点影响

### CHECK 8（v0.6 关键词）

当前锚点：
```python
("DESIGN_GAP", "agate/scripts/check-gate.sh", "P7 gate 脚本"),
("--cached", "agate/scripts/check-gate.sh", "P4/P8 gate 脚本"),
```

#13 改动在 P2 case 中新增 `status:approved` 和四字段检查。不涉及 DESIGN_GAP 或 --cached 的修改。**CHECK 8 不受影响** ✓

### CHECK 9（协议-脚本结构对齐）

当前涉及 check-gate.sh 的锚点只有：
```python
{"desc": "DESIGN_GAP 配对", "script": "agate/scripts/check-gate.sh", "keywords": ["DESIGN_GAP"]}
```

#13 新增的检查不涉及 DESIGN_GAP。**CHECK 9 不受影响** ✓

**NOTE** — 如果未来要加 P2 gate 的 CHECK 9 锚点（如 `status:approved`、`packages` 等），需同步更新 check-protocol-consistency.py。但本次改动不要求。

---

## 汇总

### PASS 项

| 项 | 评价 |
|----|------|
| #12 不实现 | 决策合理 |
| #13 status:approved 查 P2-review.md | 正确 |
| #13 P2-review.md 不存在时放行 | 正确 |
| #13 四字段计数（字段名、正则、`< 4` 逻辑、`|| echo 0` + `tail -1`） | 正确 |
| #6 改文档对齐脚本 | 正确 |
| #16 合并 #6 | 正确 |
| #6/#16 门槛表 grep 命令与脚本一致 | 正确 |
| CHECK 8/9 锚点不受影响 | 正确 |

### ISSUE 项

| 项 | 严重度 | 问题 | 修复建议 |
|----|--------|------|----------|
| #13 门槛表格式 | 一般 | 门槛表行首加了 `scripts/check-gate.sh P2 →` 前缀，与其他行风格不一致 | 保持原有风格，把脚本检查列为补充命令 |
| #13 门槛表 `=4` vs 脚本 `< 4` | 一般 | 门槛表写 `=4`，脚本允许 >4；`含'权衡'或'选择理由'描述` 缺具体判定命令 | 门槛表改为 `≥4`；补 `grep -qE '权衡\|选择理由' P2-design.md → 命中` |
| G2.8 遗漏变红 | **严重** | G2.8（候选方案 ≥2 但无权衡）的 P2-design.md 也缺四字段，会在四字段检查 exit 1 而非 form check exit 1 | G2.8 必须同步补四字段 |
| G2.10/G2.11/G2.12 fixture | 一般 | 新增测试的 P2-design.md 未明确要求含四字段；G2.11 happy path 如果缺四字段会 exit 1 | 所有 P2 测试 fixture 补四字段 |
| 缺 P2-review.md 不存在测试 | 一般 | 隐藏依赖 #2 提到"P2-review.md 不存在时放行"但无测试覆盖 | 补测试：有候选方案 + 权衡 + 四字段 + 无 P2-review.md → exit 2 |

### NOTE 项

| 项 | 备注 |
|----|------|
| 放置顺序 | 设计文档明确 count → status → 四字段 → form → exit 2，合理。实施时注意代码嵌入位置 |
| G2.1/G2.2/G2.4/G2.5 不受影响 | 这些测试在四字段检查之前就已 exit 1 或 exit 2 |
| 四字段额外字段 | P2-design.md 模板（task-files.md:27）要求 `files_to_read:` 和 `env_constraints:`，所以实际 P2-design.md 会有 6 个字段。四字段计数 FIELD_COUNT 会是 4-6，`< 4` 不会误拦 |

### 结论：**需先修以下项再实施**

1. **（严重）G2.8 加入变红列表**：G2.8 也缺四字段，必须同步补四字段才能在四字段检查后继续走到 form check
2. **（一般）门槛表 `=4` → `≥4`**：与脚本 `< 4` 逻辑对齐
3. **（一般）门槛表补 form check 判定命令**：`grep -qE '权衡|选择理由' P2-design.md → 命中`
4. **（一般）所有 P2 测试 fixture 补四字段**：包括 G2.10/G2.11/G2.12 新增测试
5. **（一般）补 P2-review.md 不存在测试**：覆盖隐藏依赖 #2 的放行行为
