---
task_id: agate-audit-fixes-C-impl-review
agent: main
date: 2026-07-02
status: 实施评审
来源: docs/plans/agate-audit-fixes-C-design-2026-07-01.md
---

# C 组实施评审：裁剪条件偏差修复

## 评审结果汇总

| # | 项 | 代码一致性 | 逻辑正确性 | 测试覆盖 | 文档同步 | 反向传播 | 总评 |
|---|------|-----------|-----------|---------|---------|---------|------|
| #5 | P3 裁剪文档改写 | ALIGNED | ALIGNED | N/A（纯文档） | ALIGNED | NEEDS_HUMAN_REVIEW | NEEDS_HUMAN_REVIEW |
| #7 | 检查 7 加 P6 | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED |
| #8 | P8 internal_only_reason | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED |
| #10 | P2 form check | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED | ALIGNED |

## 逐项评审

### #5 P3 裁剪条件：改文档对齐脚本

**代码一致性**：ALIGNED
- 设计要求 state-machine.md:165 从"需 risk_level=low（high 风险不可裁）"改为"裁剪 P3：high 风险不可裁"
- 实际 state-machine.md:165 为 `裁剪 P3：high 风险不可裁` — 完全匹配

**逻辑正确性**：ALIGNED
- 脚本 check-pruning.sh:70-74 仅在 `risk_level=high` 时拦截 P3 裁剪，medium 放行 — 与文档一致

**文档同步**：ALIGNED
- state-machine.md 已更新

**反向传播**：NEEDS_HUMAN_REVIEW
- `orchestrator-template.md:78` 仍写"声明裁剪的阶段必须满足条件（risk_level=low 等）"，其中 `risk_level=low` 已过时（#5 修正后只有 high 不可裁，medium/low 均可裁 P3）
- 建议修改为"声明裁剪的阶段必须满足条件（如 high 风险不可裁 P3 等）"或类似措辞
- 此为低优先级——orchestrator-template.md 是概要描述，不影响运行时行为

---

### #7 检查 7 跳过风险条件加 P6

**代码一致性**：ALIGNED
- 设计要求 check-pruning.sh:106 条件加 `! echo "$PHASES_DECLARED" | grep -qw 'P6'`
- 实际 check-pruning.sh:106 为：`if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ! echo "$PHASES_DECLARED" | grep -qw 'P3' || ! echo "$PHASES_DECLARED" | grep -qw 'P6' || ! echo "$PHASES_DECLARED" | grep -qw 'P7' || ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then` — P6 已加入

**逻辑正确性**：ALIGNED
- 场景推演：
  - P6 被裁剪 + 无"跳过风险:" → 条件 `! grep P6` 为真 → 整体或链为真 → 进入检查 → 报错 ✓
  - P6 被裁剪 + 有"跳过风险:" → 条件为真但 grep "跳过风险:" 命中 → 不报错 ✓
  - P6 未被裁剪 → `! grep P6` 为假，但其他阶段若被裁剪仍会触发 → 正确 ✓

**测试覆盖**：ALIGNED
- P2.12: P6 裁剪无跳过风险 → exit 1，含"跳过风险" ✓
- P2.12a: P6 裁剪 + no_behavior_change + 跳过风险 → exit 0 ✓
- 与设计文档测试计划一致

**文档同步**：ALIGNED
- state-machine.md:170 裁剪理由格式描述覆盖所有裁剪阶段

**反向传播**：ALIGNED — 无其他文件受影响

---

### #8 P8 裁剪加 internal_only_reason 理由字段检查

**代码一致性**：ALIGNED
- 设计要求 check-pruning.sh:96-101 改为嵌套 if 结构：
  - 无 `internal_only: true` → 报"裁剪 P8 需声明 internal_only: true"
  - 有 `internal_only: true` 但无 `internal_only_reason:` → 报"裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）"
  - 两者都有 → 不报错
- 实际 check-pruning.sh:97-103：
  ```bash
  if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
      if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
          ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true\n"
      elif ! grep -qE '^internal_only_reason:' "$P1_FILE" 2>/dev/null; then
          ERRORS="${ERRORS}裁剪 P8 需 internal_only: true + 理由（internal_only_reason: 字段缺失）\n"
      fi
  fi
  ```
  — 嵌套 if 结构正确，错误消息与设计文档匹配

**逻辑正确性**：ALIGNED
- 场景推演：
  - P8 被裁剪 + 无 `internal_only: true` → 第一个 if 为真 → 报错 ✓
  - P8 被裁剪 + 有 `internal_only: true` + 无 `internal_only_reason:` → 第一个 if 为假，elif 为真 → 报错 ✓
  - P8 被裁剪 + 两者都有 → 两个条件都为假 → 不报错 ✓
  - P8 未被裁剪 → 外层 if 为假 → 跳过 ✓

**测试覆盖**：ALIGNED
- P2.7: P8 裁剪无 internal_only → exit 1 ✓
- P2.7a: P8 裁剪 + internal_only: true + internal_only_reason → exit 0 ✓（评审修订已纳入：加了 reason 字段）
- P2.13: P8 裁剪有 internal_only 无 reason → exit 1，含"internal_only_reason" ✓
- P2.14: P8 裁剪有两者 → exit 0 ✓
- R4.1/R4.2/R4.3 回归测试全部覆盖 ✓
- P2.7a 变红修复已确认（加了 `add_p1_field "$dir" "internal_only_reason" "内部工具，无外部用户"`）

**文档同步**：ALIGNED
- state-machine.md:168: `裁剪 P8：需声明 internal_only: true + internal_only_reason: <理由>` ✓
- task-files.md:145-146: 两个字段示例已添加 ✓

**反向传播**：ALIGNED
- WORKFLOW.md:200 P8 gate 描述已含 `internal_only: true` 声明（较概括，未提到 reason 字段，但属于"脚本化部分"的内部细节，不需要逐字段列出）
- dispatch-protocol.md 无 internal_only 引用 — 不受影响
- CHECK 9 锚点关键词 `internal_only` 在代码中仍存在，锚点不受影响（设计文档隐藏依赖 §4 已确认）

---

### #10 P2 候选方案 form check

**代码一致性**：ALIGNED
- 设计要求在 check-gate.sh P2 case 的 `[ -f "$P2_FILE" ]` 块内，CANDIDATE_COUNT < 2 检查之后加 form check
- 实际 check-gate.sh:25-37：
  ```bash
  P2_FILE="$TASK_DIR/P2-design.md"
  if [ -f "$P2_FILE" ]; then
      CANDIDATE_COUNT=...
      if [ "$CANDIDATE_COUNT" -lt 2 ]; then
          echo "..." >&2; exit 1
      fi
      if ! grep -qE '权衡|选择理由' "$P2_FILE" 2>/dev/null; then
          echo "GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述" >&2
          exit 1
      fi
  fi
  echo "GATE P2: 需从 P2-design.md gate_commands 动态读取..." >&2
  exit 2
  ```
  — form check 在 `[ -f "$P2_FILE" ]` 块内部 ✓
  — 在 CANDIDATE_COUNT 检查之后 ✓
  — 错误消息与设计文档匹配 ✓

**逻辑正确性**：ALIGNED
- 场景推演：
  - 无 P2 文件 → 跳过整个 if 块 → exit 2（主 Agent 自判）✓
  - 有 P2 文件 + < 2 候选方案 → exit 1（count check 先拦截）✓
  - 有 P2 文件 + ≥ 2 候选方案 + 无"权衡/选择理由" → exit 1（form check 拦截）✓
  - 有 P2 文件 + ≥ 2 候选方案 + 有"权衡" → 跳过 form check → exit 2 ✓
  - 有 P2 文件 + ≥ 2 候选方案 + 有"选择理由" → 同上 ✓
- `$CANDIDATE_COUNT` 作用域：在 `[ -f "$P2_FILE" ]` 块内定义和使用，不存在 unbound variable 风险（评审修订关注点）

**测试覆盖**：ALIGNED
- G2.8: P2 候选方案 ≥2 但无"权衡" → exit 1，含"权衡" ✓
- G2.9: P2 候选方案 ≥2 + 含"权衡" → exit 2 ✓
- G2.3: 2 个候选方案 + 权衡 → exit 2（原有测试，确认未回归）✓
- G2.6/G2.7: 不同命名格式 → exit 2（含权衡）✓

**文档同步**：ALIGNED — 此项不涉及文档修改（设计文档未要求）

**反向传播**：ALIGNED
- G2.3/G2.6/G2.7 旧测试已验证通过（G2.3 含"权衡"关键词，G2.6/G2.7 也含）— 无回归
- CHECK 9 锚点不受影响

---

## 测试执行结果

全部 63 个测试通过（24 check-pruning + 33 check-gate + 3 regression + 3 重复的 regression 跑在完整套件中）：

```
1..63 — all ok
```

一致性检查：0 ERROR, 5 WARNING（均为既有 WARNING，非本次引入）

shellcheck：未在本次评审中重跑，建议验证。

---

## 汇总结论

**3/4 项 ALIGNED，1 项 NEEDS_HUMAN_REVIEW**

- #5/#7/#8/#10 的脚本逻辑、嵌套 if 结构、form check 位置、测试覆盖、文档同步均与修订后的设计文档一致
- 唯一待处理项：`orchestrator-template.md:78` 的 `risk_level=low` 概要描述与 #5 修改后的文档不同步（低优先级，不影响运行时）
- P2.7a 变红修复已确认（评审修订要求已纳入）
- CHECK 9 锚点不受影响
