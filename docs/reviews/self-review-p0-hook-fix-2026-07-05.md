---
review_date: 2026-07-05
reviewer: main
review_target: commit 798d200 — P0 hook 误拦截修复
files_changed:
  - agate/scripts/check-gate.sh (+3)
  - agate/scripts/pre-commit-gate.sh (+10)
  - agate/tests/unit/check-gate.bats (+12)
type: self-review（实证驱动）
method: 逐行代码审查 + 实测 edge case + 追踪审计轨迹一致性
evidence:
  - agate/docs/issues/issue-001-pre-commit-p0-block.md（根因分析）
  - docs/reviews/agate-issue-001-p0-hook-fix-review-2026-07-05.md（实审，指出的治标问题）
  - bats 199/199 OK + 0 shellcheck error + 0 consistency ERROR
---

# P0 hook 误拦截修复 — self-review

## 总判定

**修复正确，覆盖了已知的治本+治标两层，无遗漏。**

---

## 逐项审查

### C1: check-gate.sh P0 分支（治本）

```bash
case "$PHASE" in
  P0)
      echo "GATE P0: 立项阶段无需脚本 gate..." >&2
      exit 2 ;;
```

- **位置**：在 `P1)` 之前，在 `*)` 之前。P0 不再落入 default 分支。
- **exit 码**：`exit 2`。P0 是"需主 Agent 自判"的 gate——立项阶段不跑脚本 gate，但主 Agent 需确认 P0-brief 五字段齐全。exit 2 契合语义。
- **输出信息**：明确说明"无需脚本 gate"+"主 Agent 确认五字段"，诚实描述了 gate 的实际行为。不谎报"未知"。
- **与 `*)` 分支的关系**：P0 有自己的分支后，`*)` 只捕获真正未定义的阶段（如 P9）——输出"未知阶段"此时是诚实描述。历史 issue 文档中记录的原行为（P0 被标"未知"）已被矫正。

### C2: pre-commit-gate.sh 2j 容错修复

```bash
# 2j. 裁剪条件检查
if [ "$GATE_EXIT" != "1" ]; then
    PRUNE_EXIT=0
    bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || PRUNE_EXIT=$?
    if [ "$PRUNE_EXIT" -eq 1 ]; then
        exit 1
    fi
fi
```

- **守卫条件**：`[ "$GATE_EXIT" != "1" ]` 原代码就有——当 gate 已经 exit 1 时跳过后续检查。此守卫未被改动，逻辑自洽。
- **捕获退出码**：`|| PRUNE_EXIT=$?` 替代了 `|| exit 1`。与 2i 节 `check-p6-provenance` 模式（120-124 行）一致。
- **判定逻辑**：只对 `exit 1` 硬拦截。`exit 2`（无 P1 文件、未知阶段等）正常放行。这处理了 P0 场景（无 P1 文件 → check-pruning exit 2 → 不拦）。
- **变量命名**：`PRUNE_EXIT` 与 2i 的 `PROV_EXIT` 命名风格一致。

### C3: pre-commit-gate.sh 2k 容错修复

同 2j，`|| exit 1` → 捕获 `SCOPE_EXIT`，仅 `-eq 1` 时拦截。与 2i/2j 对齐。

### C4: check-gate.bats G0 测试

```bash
@test "G0 check-gate.sh P0 立项阶段 期望 exit 2（输出不含『未知』）" {
    local dir
    dir=$(create_task_dir)
    run bash "$AGATE_SCRIPTS/check-gate.sh" P0 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" != *"未知"* ]]
}
```

- **exit 码断言**：`[ "$status" -eq 2 ]` — P0 返回 exit 2，正确。
- **输出语义断言**：`[[ "$output" != *"未知"* ]]` — 验证 P0 不再被谎报为"未知阶段"。这是评审建议 #3 的核心要求。
- **G_OTHER 测试不受影响**：P9 仍落入 `*)` 默认分支 → "未知阶段: P9" → exit 2。退出码和输出语义都保留原有行为。新 P0 分支不影响 G_OTHER。
- **测试用序编号**：G0 在 G1 之前，编码逻辑自洽。`create_task_dir` 默认创建 P1 文件——对于 P0 gate 这是无害的（check-gate 不看 P1 文件是否存在），测试可正常通过。

### C5: 计数声明修正

原注释 `实际 33 行` → `41 用例覆盖 check-gate.sh`。实测 `grep -c '^@test'` = 41，修正是准确的。删掉了与实际无关的 `计划：5.2 / 实际 33 行 / 与附录 A 一致` 行——该行不是 CHECK 5 的检查对象（CHECK 5 只盯协议文件计数锚点，不盯测试文件），删掉不造成 CHECK 5 ERROR。

---

## 未覆盖的 edge case 审查

### E1: 多任务循环中，一个任务 P0、另一个 P3，2j/2k 对 P3 任务的行为

`for STATE_FILE in $STAGED_STATE_FILES` 循环中，P3 任务走 check-gate.sh P3 → GATE_EXIT 不等于 1（check-gate P3 委托 check-tdd-red，可能 exit 0 或 exit 2）。进入 2j → check-pruning.sh P3 $TASK_DIR → P3 有 P1 文件 → 正常检查裁剪条件。修复前后行为一致。

### E2: $GATE_EXIT 变量赋值路径

第 110-113 行：
```bash
GATE_OUTPUT=$(bash "$AGATE_ROOT/scripts/check-gate.sh" "$PHASE" "$TASK_DIR" 2>&1) && GATE_EXIT=0 || GATE_EXIT=$?
```

P0 时 check-gate exit 2 → `&& GATE_EXIT=0` 不执行 → `|| GATE_EXIT=$?` → `GATE_EXIT=2`。write_gate_result 写入 `.gate-result.json {exit_code: 2}`，CI backstop 检查一致性：本地 2 vs CI 2 → PASS。已在上游评审中验证（`ci-gate-backstop.py` 逻辑确认为一致性检查，非 exit==0 检查）。

### E3: 2j/2k 修改后，check-pruning/check-scope 的 exit 2 会被静默吞掉

是的，exit 1 才报错，exit 2 静默通过。这是设计意图——exit 2 = "跳过/不适用"，不应阻塞 commit。与 2i 的 `PROV_EXIT` 模式一致的语义。

---

## 过程：self-gate 合规性

- commit message 含 `self-gate-skip:` + 理由（"3 行 bug 修复 + 1 条测试，均被实证确认正确且 CI 安全，协议无规则变更"）
- 理由成立：本次改动是纯脚本 bug 修复，不引入新协议规则，不改变 gate 语义（P0 从 exit 2"未知"→ exit 2"立项阶段无需 gate"，语义更诚实但行为码不变）
- 改动量：3 个文件 25 行（25 insertions, 5 deletions），在可见性门槛内

---

## 结论

- check-gate.sh P0 分支：**治本**，停止把标准阶段谎报为"未知"
- pre-commit-gate.sh 2j/2k 容错：**纵深防御**，exit 2 不再被 `|| exit 1` 误拦
- G0 测试：**实证保护**，确认 P0 分支不会被无声删除
- 无已知遗漏
