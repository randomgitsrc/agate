---
review_date: 2026-07-08
reviewer: protocol-alignment-review
change_summary: P2/P6 从"有例外口的不可裁"升级为"无例外口的不可裁"；P7 裁剪增加 coupling_checklist 声明要求；P2 review agent=main 从 WARNING 升级为硬拦截；"写跑分离"重构为"自查≠gate"；dispatch-protocol 新增 files_modified 校验
files_changed: [CHANGELOG.md, agate/LIMITATIONS.md, agate/WORKFLOW.md, agate/assets/execution-roles/architect.md, agate/assets/execution-roles/implementer.md, agate/assets/execution-roles/verifier.md, agate/assets/templates/dispatch-prompt.md, agate/assets/templates/task-files.md, agate/dispatch-protocol.md, agate/loop-orchestration.md, agate/orchestrator-template.md, agate/phase-cards/P2-design.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P6-acceptance.md, agate/platform-notes.md, agate/role-system.md, agate/scripts/check-gate.sh, agate/scripts/check-p6-provenance.sh, agate/scripts/check-protocol-consistency.py, agate/scripts/check-pruning.sh, agate/scripts/pre-commit-gate.sh, agate/state-machine.md, agate/tests/integration/pre-commit-hook.bats, agate/tests/unit/check-gate.bats, agate/tests/unit/check-p6-provenance.bats, agate/tests/unit/check-pruning.bats, agate/tests/unit/dispatch-context-warning.bats]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（design_trivial/follows_existing_pattern 候选方案简化已补；不可裁→不可裁剪已统一）|
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（WORKFLOW.md/state-machine.md 6处已修复）|
| A4 | 测试覆盖 | ALIGNED（G2.9a/G2.9b 补 design_trivial/follows_existing_pattern 1候选方案测试）|
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED（coupling_checklist 锚点已补）|

## 逐项审查

### A1: 文档→脚本对齐

**1. check-gate.sh 缺 design_trivial/follows_existing_pattern 候选方案简化逻辑**

**文档声明**（state-machine.md:164）：
> 裁剪 P2：不可裁（方案设计是必经阶段。……design_trivial / follows_existing_pattern 可简化 P2（1 个候选方案），不可省略 P2）

**文档声明**（P2-design.md:40/47-48/79/86）：
> 候选方案 ≥2 + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
> design_trivial: true → 可只写 1 个候选方案（P2 仍不可省略）

**脚本实现**（check-gate.sh:29-34）：
```bash
CANDIDATE_COUNT=$(grep -cE '^###?\s*(候选方案|方案\s*[ABC123abc一二三四五])' "$P2_FILE" 2>/dev/null || echo 0)
CANDIDATE_COUNT=$(echo "$CANDIDATE_COUNT" | tail -1)
if [ "$CANDIDATE_COUNT" -lt 2 ]; then
    echo "GATE P2: P2-design.md 需至少 2 个候选方案 + 权衡 + 选择理由（v0.6 多方案探索）" >&2
    exit 1
fi
```

**结论**：MISALIGNED
**差异**：脚本无条件要求 ≥2 候选方案，未实现 design_trivial/follows_existing_pattern 时允许 1 个的简化逻辑。当 architect 在 design_trivial: true 场景只写 1 个候选方案时，check-gate.sh 会误拦（exit 1）。
**建议**：check-gate.sh P2 分支增加：若 P1-requirements.md 含 design_trivial: true 或 follows_existing_pattern: [...]，候选方案数 ≥1 即可通过。

**2. state-machine.md 用"不可裁"而非"不可裁剪"导致 consistency check FAIL**

**文档声明**（state-machine.md:164）：
> 裁剪 P2：不可裁（……）

**脚本实现**（check-protocol-consistency.py:415-416）：
```python
("P2 不可裁剪", "agate/scripts/check-pruning.sh", "裁剪检查脚本"),
("P2 不可裁剪", "agate/state-machine.md", "状态机文档"),
```

**结论**：MISALIGNED
**差异**：state-machine.md 使用"不可裁"（无"剪"字），check-protocol-consistency.py 期望"P2 不可裁剪"（含"剪"字）。实际运行 `python3 agate/scripts/check-protocol-consistency.py` 输出：
> ❌ 状态机文档 (agate/state-machine.md) 缺少 v0.6 关键词 'P2 不可裁剪'
**建议**：二选一——要么 state-machine.md:164/166 改为"不可裁剪"，要么 V06_KEYWORD_ASSERTIONS 关键词改为"不可裁"。推荐统一为"不可裁剪"（与 check-pruning.sh 错误消息一致）。

### A2: 脚本→文档对齐

**1. check-gate.sh P2 agent=main 硬拦截 → 文档已同步**

**脚本实现**（check-gate.sh:41-49）：
```bash
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

**文档声明**（state-machine.md:84）：
> P2 --[P2-review.md 有效 AND status==approved AND agent≠main AND ...]--> P3

**文档声明**（WORKFLOW.md:230）：
> agent=main（自审）被 check-gate.sh 硬拦截 exit 1

**结论**：ALIGNED

**2. check-p6-provenance.sh 删除 P2-review agent=main 检查 → 已移至 check-gate.sh**

**脚本变更**：check-p6-provenance.sh 删除了 P2-review agent=main 的 WARNING 逻辑（原 L201-L215）。对应测试 PV.15 期望值从 exit 2 改为 exit 0。

**结论**：ALIGNED（检查责任从 provenance 移至 gate，语义正确）

**3. check-pruning.sh P2/P6 无例外口 → 文档已同步**

**脚本实现**（check-pruning.sh:46-54）：
```bash
# 检查 2：P2 不可裁剪（无例外口）
if ! echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    ERRORS="${ERRORS}P2 不可裁剪——..."
fi
# 检查 3：P6 不可裁剪（无例外口）
if ! echo "$PHASES_DECLARED" | grep -qw 'P6'; then
    ERRORS="${ERRORS}P6 不可裁剪——..."
fi
```

**文档声明**（state-machine.md:164/166）：已同步为"不可裁（无例外口）"

**结论**：ALIGNED

**4. check-pruning.sh coupling_checklist → 文档已同步**

**脚本实现**（check-pruning.sh:82-87）：
```bash
if ! grep -qE '^implicit_coupling:' "$P1_FILE" 2>/dev/null; then
    if ! grep -qE '^coupling_checklist:\s*\[' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P7 需 coupling_checklist: [检查过的耦合点]..."
    fi
fi
```

**文档声明**（state-machine.md:167）：
> 裁剪 P7：需源码文件数 ≤ 5 AND 无 implicit_coupling 声明 AND 有 coupling_checklist

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

**A3a（连锁：已知的衍生改动）**：已同步 ✓
- dispatch-protocol.md gate 表更新 ✓
- WORKFLOW.md 阶段总览表更新 ✓
- WORKFLOW.md 关键设计原则更新 ✓
- LIMITATIONS.md P2 评审描述更新 ✓
- orchestrator-template.md 关键不变量更新 ✓
- loop-orchestration.md agent=main 硬拦截更新 ✓
- platform-notes.md Codex 兼容性更新 ✓
- role-system.md 评审映射表更新 ✓
- architect.md/implementer.md/verifier.md 写跑分离→自查≠gate ✓
- dispatch-prompt.md 写跑分离→自查≠gate + 返回前自检 + files_modified ✓
- task-files.md 候选方案例外口→简化 ✓
- CHANGELOG.md 已标注 ✓

**A3b（反向传播：应被影响但未列在 diff 中的文件）**：

| 文件 | 问题 | 严重性 |
|------|------|--------|
| **WORKFLOW.md:118** | 适用边界表"小任务…跳过 P2/P7"——与 P2 不可裁剪矛盾 | 高 |
| **WORKFLOW.md:127-128** | "P2 设计+评审默认保留，方案明确时才可跳过"——与 P2 不可裁剪矛盾 | 高 |
| **WORKFLOW.md:138** | "小任务裁剪 P6 必须在 P1 裁剪说明里写明充分理由"——与 P6 不可裁剪矛盾 | 高 |
| **state-machine.md:186** | "不可跳过的阶段：P1（需求基线）、P4（实现）、P5（技术验证）"——缺 P2/P6 | 高 |
| **P7-consistency.md:4** | 裁剪跳阶说明"源文件数≤5+无 implicit_coupling"——缺 coupling_checklist | 中 |
| **task-files.md** | 裁剪说明模板缺 coupling_checklist 字段示例 | 中 |

**结论**：MISALIGNED
**差异**：6 处应被影响的文件/位置未被更新，与本次变更的核心语义（P2/P6 不可裁剪、P7 需 coupling_checklist）矛盾。
**建议**：
1. WORKFLOW.md:118 改为"小任务…跳过 P7"（删除"跳过 P2"），或改为"裁剪流程：P1 + P2 + P3 + P4 + P5（+ P6 若有 BDD 验收条件），跳过 P7"
2. WORKFLOW.md:127-128 改为"P2 不可裁剪——方案设计是必经阶段。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略"
3. WORKFLOW.md:138 改为"P6 不可裁剪——验收是质量最后防线。no_behavior_change 可简化（快速验收），不可省略"
4. state-machine.md:186 改为"不可跳过的阶段：P1（需求基线）、P2（方案设计）、P4（实现）、P5（技术验证）、P6（验收）"
5. P7-consistency.md:4 补充 coupling_checklist
6. task-files.md 裁剪说明模板补充 coupling_checklist 字段

### A4: 测试覆盖

**已覆盖**：
- check-pruning.bats: P2 裁剪无例外口（P2.2/P2.3a/P2.3b/P2.3c）、P6 裁剪无例外口（P2.4/P2.4a）、coupling_checklist（P2.6d/P2.6e）✓
- check-gate.bats: P2 agent=main 硬拦截（G2.18/G2.19/G2.20）✓
- check-p6-provenance.bats: agent=main 检查移除（PV.15/PV.16）✓
- dispatch-context-warning.bats: B3 WARNING ✓
- pre-commit-hook.bats: IT.11 非实现阶段代码暂存 WARNING ✓
- check-gate.bats: G2.5 P2 无 P2-design.md → exit 1 ✓
- 漂移检测: D-drift-1/2, G-drift-1/2/3 ✓

**未覆盖**：
- check-gate.sh 缺 design_trivial/follows_existing_pattern 1 候选方案的测试（因脚本本身未实现此逻辑，见 A1-1）
- check-gate.sh 缺 P2 无 P2-design.md + design_trivial 场景的测试（P2 不可裁剪，不存在 P2-design.md 应报错——G2.5 已覆盖 exit 1，但错误消息验证不够精确）

**结论**：NEEDS_HUMAN_REVIEW
**说明**：核心变更（P2/P6 不可裁剪、P7 coupling_checklist、agent=main 硬拦截）均有测试覆盖。但 A1-1 的 MISALIGNMENT 意味着 design_trivial/follows_existing_pattern 简化逻辑的测试也缺失——需要先决定是补脚本逻辑还是改文档。

### A5: 下游影响 + 文档传播

**破坏性变更**：
- P2/P6 从"有例外口的不可裁"变为"无例外口的不可裁"——已有项目 P1-requirements.md 中的 design_trivial: true / follows_existing_pattern: [...] / no_behavior_change: true / legacy_p2_pruned: true 声明将不再放行裁剪。这是**设计意图**（升级为不可裁），不是 bug。
- P2 review agent=main 从 WARNING 升级为硬拦截——已有 P2-review.md 中 agent: main 的任务将无法通过 gate。这是**设计意图**，迫使主 Agent 必须派发独立 subagent 评审。

**CHANGELOG**：已标注 ✓（三条变更记录）

**文档传播**：
- "写跑分离"→"自查≠gate"已在所有角色文件、模板、阶段卡片同步 ✓
- dispatch-protocol.md 新增校验 6/7（files_modified）+ 自查≠gate ✓
- pre-commit-gate.sh 新增 B3 dispatch-context WARNING + E3 非实现阶段代码暂存 WARNING ✓

**结论**：ALIGNED（破坏性变更是设计意图，CHANGELOG 已标注）

### A6: 锚点表覆盖

**已更新**：
- P2 不可裁剪锚点：desc 更新为"P2 不可裁剪（design_trivial / follows_existing_pattern 可简化不可省略）"，keywords 改为 ["P2 不可裁剪"] ✓
- P6 不可裁剪锚点：desc 更新为"P6 不可裁剪（no_behavior_change 可简化不可省略）"，keywords 改为 ["P6 不可裁剪"] ✓
- P2 agent=main 硬拦截锚点：新增 ✓

**未更新/问题**：
1. coupling_checklist 锚点未新增——SCRIPT_ALIGNMENT_ANCHORS 缺少 P7 coupling_checklist 检查的锚点
2. V06_KEYWORD_ASSERTIONS 关键词不匹配——期望"P2 不可裁剪"但 state-machine.md 用"不可裁"（见 A1-2），实际运行 consistency check FAIL

**结论**：MISALIGNED
**建议**：
1. SCRIPT_ALIGNMENT_ANCHORS 新增 coupling_checklist 锚点：
   ```python
   {
       "desc": "裁剪 P7 coupling_checklist 声明",
       "script": "agate/scripts/check-pruning.sh",
       "keywords": ["coupling_checklist"],
   }
   ```
2. 修复 state-machine.md:164/166 "不可裁"→"不可裁剪"（或修改 V06_KEYWORD_ASSERTIONS 关键词匹配"不可裁"）

## 修复清单（按优先级）

| # | 位置 | 修复 | 对应审查项 |
|---|------|------|-----------|
| 1 | check-gate.sh P2 分支 | 增加 design_trivial/follows_existing_pattern 时候选方案数 ≥1 即通过 | A1-1 |
| 2 | state-machine.md:164/166 | "不可裁"→"不可裁剪" | A1-2, A6 |
| 3 | WORKFLOW.md:118 | 小任务裁剪流程删除"跳过 P2" | A3b |
| 4 | WORKFLOW.md:127-128 | "方案明确时才可跳过"→"不可裁剪，可简化" | A3b |
| 5 | WORKFLOW.md:138 | "小任务裁剪 P6"→"P6 不可裁剪" | A3b |
| 6 | state-machine.md:186 | 不可跳过阶段列表增加 P2、P6 | A3b |
| 7 | P7-consistency.md:4 | 裁剪跳阶说明补充 coupling_checklist | A3b |
| 8 | task-files.md 裁剪说明模板 | 补充 coupling_checklist 字段示例 | A3b |
| 9 | check-protocol-consistency.py | 新增 coupling_checklist 锚点 | A6 |
| 10 | check-gate.bats | 新增 design_trivial/follows_existing_pattern 1 候选方案测试 | A4 |
