---
task_id: agate-audit-fixes
agent: main
date: 2026-07-01
status: 修复实施计划（待评审）
来源: docs/reviews/agate-full-audit-2026-07-01.md + agate-full-audit-part2-2026-07-01.md
---

# 审计发现修复实施计划

## 问题总览

全量审查发现 21 个问题，按性质分组：

| 组 | 问题数 | 性质 |
|----|--------|------|
| A | 3 | MAX_RETRY 相关（#1, #15, A10）|
| B | 3 | 回退跳变相关（#2, #11, A12）|
| C | 4 | 裁剪条件偏差（#5, #7, #8, #10）|
| D | 4 | 门槛表对齐（#12, #13, #6, #16）|
| E | 4 | 文档滞后（#3, #4, #9, #14）|
| F | 3 | NEEDS_HUMAN_REVIEW（#17, #18, #19）|

---

## A. MAX_RETRY 相关（3 项）

### 问题

| # | 描述 | 文档 | 脚本 |
|---|------|------|------|
| #1 | MAX_RETRY 硬编码 | state-machine.md:428-437 按阶段：P1=3,P2=3,P3=2,P4=3,P5=2,P6=2,P7=2,P8=2 | check-state-transition.sh:12 `MAX_RETRY=3` 统一 |
| #15 | 复盘提醒阈值 | 同上 | check-retrospective.sh:23 `>= 3` 统一 |
| A10 | 重试超限 PAUSED 强制 | 承接 #1 | 阈值因 #1 错误 |

### 设计决策

**修脚本，不修文档。** 文档的按阶段差异化是有意设计——P3/P5/P6/P7/P8 是"少轮次"阶段（TDD 红灯、技术验证、验收），重试 2 次就该 PAUSED。脚本统一为 3 放宽了这些阶段的上限。

### 修复方案

**check-state-transition.sh**：

不能用 `get_max_retry "$new_phase"`——`.state.yaml` 的 retries 是按阶段存储的 dict，可以同时包含多个阶段的记录。如果用 `new_phase`（如 P3, MAX=2）作为阈值查 P2 的 2 次重试（P2 MAX=3），会误判 P2 超限。

正确做法：在 Python 循环内按 retries dict 的 key（阶段名）逐阶段查阈值：

```bash
# 替换 MAX_RETRY=3 硬编码，改为传映射表给 Python
# shell 层保留 MAX_RETRY 变量名（CHECK 9 锚点要求）
MAX_RETRY=3  # 默认值（向后兼容旧调用方式）
MAX_RETRY_MAP="P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"
export MAX_RETRY_MAP
```

Python 检查逻辑改为 per-phase 查找：

```python
max_map_str = os.environ.get("MAX_RETRY_MAP", "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2")
max_map = dict(p.split(":") for p in max_map_str.split(","))
retries = data.get('retries', {})
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        phase_max = int(max_map.get(phase, 3))
        if isinstance(attempts, list) and len(attempts) >= phase_max:
            print(f'{phase}={len(attempts)}')
            break
```

**check-retrospective.sh**：

同样按阶段查 MAX_RETRY。内联映射，注释标明"与 check-state-transition.sh 的 MAX_RETRY_MAP 保持同步"：

```bash
# 按阶段查 MAX_RETRY（与 check-state-transition.sh 保持同步）
get_max_retry() {
    case "$1" in
        P1|P2|P4) echo 3 ;;
        P3|P5|P6|P7|P8) echo 2 ;;
        *) echo 3 ;;
    esac
}
```

### 测试

- 扩展 `check-state-transition.bats`：
  - P3 retries=2 → 拦截（之前放行）
  - **多阶段 retries + 不同阈值**：new_phase=P3, retries={P2:[2 条], P3:[1 条]} → exit 0（P2 的 MAX=3, 2<3 不超限；P3 的 MAX=2, 1<2 不超限）。这是防止 `get_max_retry "$new_phase"` 误拦的关键测试
- 扩展 `check-retrospective.bats`：P5 retries=2 → 提醒（之前不提醒）

---

## B. 回退跳变相关（3 项）

### 问题

| # | 描述 | 文档 | 脚本 |
|---|------|------|------|
| #2 | 回退跳变降级 | state-machine.md:407-411 "强制 PAUSED" | check-state-transition.sh:63-67 WARNING 不拦截 |
| #11 | 方向 | state-machine.md:408 绝对值（双向）| 脚本只查 old > new（回退）|
| A12 | 同 #11 | 同上 | 同上 |

### 设计决策

**#2：恢复 exit 1（强制 PAUSED）。**

脚本注释说降级原因是"等 .gate-history.jsonl 积累数据"——但 `.gate-history.jsonl` 的 PAUSED 验证功能已被 HEAD/staged diff 机制隐式覆盖（PAUSED 单独 commit 时 HEAD=PAUSED → L51-53 早退 exit 0）。简单 diff 检查足以强制 PAUSED 检查点，不需要等待 .gate-history.jsonl 的精确验证。

T019 教训正是"跨阶段回退未 PAUSED"——降级为 WARNING 等于放弃这条防护。

**#11：保持只查回退方向，不改双向。**

双向检查会破坏合法裁剪流程——P3/P4 被裁剪后，主 Agent 直接将 phase 从 P2 改为 P5（state-machine.md:160-161："跳过时直接转移到裁剪声明中的下一个阶段"），diff = |5-2| = 3，双向检查会 exit 1 误拦。

`check-state-transition.sh` 只读 `.state.yaml`，不读 P1-requirements.md 的 phases 声明，无法区分"合法裁剪前向跳"和"非法跳过阶段"。如果确实要查前向跳，必须先让脚本读 P1 phases 声明做白名单——这是较大改动，不宜混入本次修复。

文档 state-machine.md:408 用绝对值是表述不严谨，改为明确回退方向消除歧义。

### 修复方案

**check-state-transition.sh**：

```bash
# 当前（L58-68）：
diff=$((old_num - new_num))
if [ "$diff" -ge 2 ]; then
    echo "WARNING..."
    # 降级，不 exit 1
fi

# 改为（保留 old_num > 0 守卫，防止 PAUSED→Pn 恢复被误拦）：
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]; then
    diff=$((old_num - new_num))
    if [ "$diff" -ge 2 ]; then
        echo "GATE STATE: 回退跳变 P${old_num}→P${new_num}（差 ${diff}），强制 PAUSED" >&2
        exit 1
    fi
fi
```

**state-machine.md:408**：

```markdown
# 当前：若 |next_phase_num - current_phase_num| >= 2
# 改为：若 current_phase_num - next_phase_num >= 2（回退方向）
```

### 测试

- 扩展 `check-state-transition.bats`：
  - P6→P1（回退 5 阶段）→ 拦截（之前只 WARNING）
  - P5→P4（回退 1 阶段）→ 放行（正常回归）
  - **PAUSED→P3（恢复）→ exit 0**：验证 `old_num=0` 守卫不被移除

---

## C. 裁剪条件偏差（4 项）

### 问题

| # | 描述 | 文档 | 脚本 |
|---|------|------|------|
| #5 | P3 裁剪条件 | "需 risk_level=low" | 只禁 high（medium 放行）|
| #7 | 跳过风险遗漏 P6 | "每条裁剪须含跳过风险" | 条件只含 P2/P3/P7/P8 |
| #8 | P8 缺理由检查 | "internal_only: true + 理由" | 只查 internal_only |
| #10 | P2 候选方案 | "≥2 候选方案 + 权衡 + 选择理由" | 只查数量 ≥2 |

### 设计决策

**#5：改文档对齐脚本。** 脚本 + 测试一致允许 medium 裁剪 P3。medium 是中间态，允许裁剪 P3 合理（P3 是 TDD，medium 风险可以不强制 TDD）。文档"需 low"措辞过于严格。

改 state-machine.md:165："需 risk_level=low（high 风险不可裁）" → "high 风险不可裁"

**#7：修脚本加 P6。** 文档说"每条裁剪"含 P6。脚本条件漏了 P6。

**#8：修脚本加理由检查。** 文档说"+ 理由"，脚本应该检查。

**#10：修脚本加 form check。** 和"跳过风险"同理——检查 P2-design.md 含"权衡"或"选择理由"字样。是 nudge 不是 barrier（可绕过，但制造思考摩擦）。

### 修复方案

**check-pruning.sh**：

```bash
# #7：检查 7 条件加 P6
# 当前（L104）：
if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ... 'P3' || ... 'P7' || ... 'P8'; then
# 改为：
if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ... 'P3' || ... 'P6' || ... 'P7' || ... 'P8'; then

# #8：P8 理由检查
# 当前（L98）：
if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
# 改为（if/elif 结构）：
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    : # P8 未裁剪，跳过
elif ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
    ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true\n"
elif ! grep -qE '^internal_only_reason:' "$P1_FILE" 2>/dev/null; then
    ERRORS="${ERRORS}裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）\n"
fi
```

**同步更新文档和模板**（`internal_only_reason` 字段名需先建立）：

- `state-machine.md:168`：`internal_only: true + 理由` → `internal_only: true + internal_only_reason: <理由>`
- `assets/templates/task-files.md` P1 模板裁剪说明区补 `internal_only:` 和 `internal_only_reason:` 示例
- 回归测试 `v060-p8-internal-only.bats` R4.2 更新：当前只加 `internal_only: true`，改后还需加 `internal_only_reason:` 才能通过

**check-gate.sh**：

```bash
# #10：P2 候选方案 form check
# 复用已有的 $P2_FILE 变量（L24 定义，L25 有守卫）
# 放在 CANDIDATE_COUNT >= 2 通过后、exit 2 之前
if [ "$CANDIDATE_COUNT" -ge 2 ]; then
    if ! grep -qE '权衡|选择理由' "$P2_FILE" 2>/dev/null; then
        echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
        exit 1
    fi
fi
```

**state-machine.md**：

```markdown
# #5：P3 裁剪条件
# 当前：需 risk_level=low（high 风险不可裁）
# 改为：high 风险不可裁
```

### 测试

- `check-pruning.bats`：P6 裁剪无"跳过风险" → 拦截
- `check-pruning.bats`：P8 裁剪有 internal_only 无理由 → 拦截
- `check-pruning.bats`：P8 裁剪有 internal_only + internal_only_reason → 通过（happy path）
- `check-gate.bats`：P2 候选方案 ≥2 但无"权衡" → 拦截
- `check-gate.bats`：P2 候选方案 ≥2 + 含"权衡" → exit 2 放行（happy path）
- `v060-p8-internal-only.bats` R4.2 更新（加 internal_only_reason）

---

## D. 门槛表对齐（4 项）

### 问题

| # | 描述 | 文档 | 脚本 |
|---|------|------|------|
| #12 | P1 门槛过度保守 | 有可脚本化 grep | 完全 exit 2 不检查 |
| #13 | P2 门槛错位 | 门槛表列 status:approved + 四字段 | 脚本查候选方案≥2（门槛表没列）|
| #6 | P4 路径偏离 | "P4-implementation/ 下文件非空" | 查任意暂存非 md/yaml 文件 |
| #16 | P4 文档滞后 | 门槛表写 git log | 脚本用 --cached |

### 设计决策

**#12：部分实现。** P1 gate 当前完全 exit 2。文档列了可脚本化的 grep（risk_level 命中、NEED_CONFIRM=0、status:GAP=0）。实现这些 grep 不影响 exit 2 的"需主 Agent 判断"语义——只是给主 Agent 更多信息。但改动较大且 P1 gate 本身设计为 exit 2，暂不动。标为已知局限。

**#13：同步文档和脚本。** 脚本检查"候选方案≥2"是 v0.6 加的（多方案探索），文档门槛表没更新。反过来文档列的 status:approved 脚本没查。两边都要改。

**#6：改文档对齐脚本。** 脚本查"暂存区有非 md/yaml 文件"比查"P4-implementation/ 下文件非空"更合理（pre-commit 场景下查暂存区是正确的）。改文档。

**#16：改文档。** git log → --cached。

### 修复方案

**dispatch-protocol.md 门槛表**：

```markdown
# #13：P2 门槛补"候选方案≥2"
# #16：P4 门槛 git log → git diff --cached
# #6：P4 门槛"P4-implementation/ 下文件非空" → "暂存区含非 md/yaml 文件"
```

**check-gate.sh**：

```bash
# #13：P2 补 status:approved 检查
# 文档要求查 P2-review.md（评审结论），不是 P2-design.md（设计方案）
P2_REVIEW="$TASK_DIR/P2-review.md"
if [ "$CANDIDATE_COUNT" -ge 2 ]; then
    if [ -f "$P2_REVIEW" ]; then
        if ! grep -qE 'status:\s*approved' "$P2_REVIEW" 2>/dev/null; then
            echo "GATE P2: P2-review.md 缺 status: approved" >&2
            exit 1
        fi
    fi
    # 四字段计数（packages/domains/ui_affected/gate_commands）
    FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' "$P2_FILE" 2>/dev/null || echo 0)
    FIELD_COUNT=$(echo "$FIELD_COUNT" | tail -1)
    if [ "$FIELD_COUNT" -lt 4 ]; then
        echo "GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 ${FIELD_COUNT}）" >&2
        exit 1
    fi
fi
```

### 测试

- `check-gate.bats`：P2 有候选方案但 P2-review.md 无 status:approved → 拦截
- `check-gate.bats`：P2-review.md 有 status:approved → 放行（happy path）
- `check-gate.bats`：P2-design.md 缺字段（<4）→ 拦截

---

## E. 文档滞后（4 项）

### 问题

| # | 描述 | 位置 |
|---|------|------|
| #3 | md5 去重声称"hook 强制"但未实现 | dispatch-protocol.md:575, task-files.md:244, verifier.md:130 |
| #4 | P3 gate 说"否则 gate 不通过"但 P3 gate 不检查 UI 用例 | state-machine.md:91 |
| #9 | BDD 总数文档说"="但脚本用"≥" | dispatch-protocol.md:575,363 |
| #14 | "三道客观审计"但实际四道 | dispatch-protocol.md:597 |

### 设计决策

**#3：删除"hook 强制"声明。** md5 去重边际收益有限（R1a 截图 >1KB + R1b vision YAML 已覆盖核心风险）。改为"建议"而非"hook 强制"。

**#4：改为"主 Agent 确认"。** P3 gate 不检查 UI 用例存在性（识别方式不固定），属主 Agent 判断职责。

**#9：改文档"="→"≥"。** 脚本用 ≥ 是正确的（允许 SCOPE+ 增补）。

**#14：改"三道"→"四道"。** R1b vision YAML 审计已落地。

### 修复方案

纯文档改动，不改脚本：

- dispatch-protocol.md：md5 "hook 强制" → "建议"；BDD "=" → "≥"；"三道" → "四道"
- state-machine.md:91：P3 UI 用例 "gate 不通过" → "主 Agent 确认"
- task-files.md:244：md5 "hook 强制" → "建议"
- verifier.md:130：md5 "hook 强制" → "建议"

### 测试

- 无新增测试（纯文档改动）
- 跑 consistency check 确认无 ERROR

---

## F. NEEDS_HUMAN_REVIEW + 遗漏项（6 项）

| # | 描述 | 处理 |
|---|------|------|
| #17 | FAIL 行证据未检查 | 不修——FAIL 回 P4 重做，影响小；FAIL 证据格式不统一 |
| #18 | pre-commit-gate.sh 顺序与文档表格不同步 | 改文档表格对齐脚本，**补 P1.2 PROD_TOUCHED 行**（当前表格完全没列）|
| #19 | check-changelog.sh exit 1 vs 文档"警告不拦截" | 不修——hook 层已降级，分层设计正确 |
| 遗漏 1 | P5 PROD_TOUCHED 可脚本化检查 | 不修——pre-commit-gate.sh:60 已有全局 PROD_TOUCHED 检测（扫暂存 diff），覆盖了 task 目录场景。文档门槛表的 grep 命令供主 Agent 手动执行 |
| 遗漏 2 | P1.7 跳过逻辑不一致（gate 失败时仍执行）| 不修——gate 失败时多给诊断信息可接受，P1.7 只在 P6/P7 执行 |
| 遗漏 3 | task-files.md 模板缺 internal_only | 修——C 组 #8 已包含（补 internal_only + internal_only_reason 到 P1 模板）|

---

## 实施顺序

按依赖关系排序：

1. **A+B 组：check-state-transition.sh** — MAX_RETRY per-phase 查找 + 回退跳变恢复 exit 1（只查回退 + 保留守卫）+ state-machine.md L408 去绝对值 + 测试
2. **C 组：check-pruning.sh + check-gate.sh** — 裁剪条件修复（P6 加跳过风险 + P8 加理由 + P2 加 form check）+ state-machine.md P3 裁剪条件 + task-files.md 模板 + **同步更新 v060-p8-internal-only.bats R4.2** + 测试
3. **D 组：check-gate.sh + dispatch-protocol.md** — P2 status:approved 检查（查 P2-review.md）+ 四字段计数 + 门槛表文档对齐 + 测试
4. **E 组：文档滞后修复** — 纯文档改动（md5→建议 / BDD =→≥ / 三道→四道 / P3 UI→主Agent确认）
5. **F 组：文档表格同步** — dispatch-protocol.md pre-commit 表格补 P1.2 + 调顺序
6. **全量测试 + consistency + shellcheck**
7. **self-gate 审查本次变更**

**关键依赖**：
- C 组 #8 改 P8 理由检查后，回归测试 `v060-p8-internal-only.bats` R4.2 会变红（只加 `internal_only: true` 不再加 reason）——必须在同一次修改中更新该测试
- A+B 和 C+D 合并修改时注意放置顺序：C#10 form check 和 D#13 status:approved 都在 `CANDIDATE_COUNT >= 2` 之后，先查 status:approved（更基础）再查 form check（nudge）

---

## 不做的事

| 不做 | 理由 |
|------|------|
| #12 P1 门槛实现 grep | P1 gate 设计为 exit 2，改动大且影响主 Agent 判断流程 |
| #3 md5 去重实现 | 边际收益有限，R1a+R1b 已覆盖核心风险 |
| #4 P3 UI 用例检查实现 | 识别方式不固定（playwright/e2e/cypress），不可泛化 |
| #17 FAIL 行证据检查 | 影响小，格式不统一 |
| #19 check-changelog.sh 改 exit code | hook 层已降级，分层设计正确 |
