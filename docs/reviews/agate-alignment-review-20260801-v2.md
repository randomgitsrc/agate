---
review_date: 2026-08-01
reviewer: protocol-alignment-review
change_summary: 修复 T084+T075 复盘暴露的 6 个效率问题：3 个脚本 BUG（check-pruning YAML 列表格式、SCOPE+ 误匹配 progress、CHANGELOG 检查时机）+ 3 个设计改进（并行派发操作指引、review status 字段指导、P6 evidence-consistency 审计）
files_changed: [README.md, agate/assets/templates/dispatch-prompt.md, agate/phase-cards/P2-design.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P6-acceptance.md, agate/scripts/check-p6-provenance.sh, agate/scripts/check-pruning.sh, agate/scripts/check-retrospective.sh, agate/scripts/check-scope-resolved.sh, agate/scripts/pre-commit-gate.sh, agate/tests/integration/pre-commit-hook.bats, agate/tests/unit/check-p6-provenance.bats, agate/tests/unit/check-pruning.bats, agate/tests/unit/check-retrospective.bats, agate/tests/unit/check-scope-resolved.bats]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED |
| A6 | 锚点表覆盖 | NEEDS_HUMAN_REVIEW |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**变更 1：check-pruning.sh YAML 列表格式解析**

文档声明（state-machine.md:165）：
> P1-requirements.md 的「裁剪说明」声明 phases: [列表]

文档示例（task-files.md:152）：
> `phases: [P1,P2,P4,P5,P6,P8]`（inline 列表格式）

脚本实现（check-pruning.sh:26-34）：
> 原有正则 `r'phases:\s*\[([^\]]+)\]'` 只匹配 inline 列表格式。
> 新增 else 分支：`r'phases:\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)'` 匹配 YAML 块列表格式。

**结论**：ALIGNED
**分析**：文档示例用 inline 格式，但 YAML 规范允许两种写法。脚本新增块列表支持是合理的兼容性扩展，不违反文档语义。task-files.md:152 的示例是示例而非约束（"示例非穷举"），不构成文档-脚本矛盾。

---

**变更 2：SCOPE+ 误匹配 progress 文件**

文档声明（state-machine.md:200）：
> 特殊转移（SCOPE+ 定向回补）：（行首声明格式：`^\s*-?\s*\[SCOPE+\]`）

脚本实现（check-retrospective.sh:37）：
> `basename "$f" | grep -qE 'dispatch-context|dispatch-prompt|progress' && continue`

脚本实现（check-scope-resolved.sh:19）：
> `basename "$f" | grep -qE 'dispatch-context|dispatch-prompt|progress' && continue`

**结论**：ALIGNED
**分析**：progress 文件是 subagent 的分阶段落盘中间产物（dispatch-prompt.md:43 定义），非阶段产出，不应触发 SCOPE+ 检查。排除逻辑与文档语义一致——SCOPE+ 检查的对象是"阶段产出文件"，progress 是过程产物。

---

**变更 3：CHANGELOG 检查限制到 P8**

文档声明（WORKFLOW.md:243）：
> | 1.6 | `check-changelog.sh` | **gate 通过后** | 文件级 | `[Unreleased]` 含本次 task_id（P1.6）|

文档声明（state-machine.md:221）：
> | **P1.6** CHANGELOG (scripts/check-changelog.sh) | **gate 通过后** | 缺 `[Unreleased]` → 警告不拦截 |

文档声明（dispatch-protocol.md:819）：
> | 提醒级 P1.6 | `scripts/check-changelog.sh` | **gate 通过后** | `[Unreleased]` 含 task_id |

脚本实现（pre-commit-gate.sh:247-254）：
> ```bash
> case "$PHASE" in
>     P8)
>         bash "$AGATE_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
>             echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2
>         ;;
>     esac
> ```

**结论**：**MISALIGNED**
**差异**：脚本将 CHANGELOG 检查限制到 P8 phase，但三个权威文档（WORKFLOW.md:243、state-machine.md:221、dispatch-protocol.md:819）的检查表仍将触发条件写为"gate 通过后"（不区分阶段）。文档读者会认为所有阶段的 commit 都会触发 CHANGELOG 检查，但实际只有 P8 触发。
**建议**：更新三个文档表格的"触发条件"列，从"gate 通过后"改为"P8 phase 且 gate 通过后"。

---

**变更 4：P6 evidence-consistency 审计（审计 6）**

文档声明（dispatch-protocol.md:792）：
> `scripts/check-p6-provenance.sh` → exit 0（证据-结论对应 + dispatch-context 审计 + BDD 总数对照由审计 3 自动执行...）

文档声明（WORKFLOW.md:245）：
> 五道客观审计（证据-结论对应 + dispatch-context 内容约束 + BDD 总数对照 + UI vision YAML 审计 [R1b] + EXIT_CODE 一致性 [审计5]）

脚本实现（check-p6-provenance.sh:256-302）：
> 新增"审计 6: evidence JSON 与 P6 PASS/FAIL 声明一致性（P2.57）"

**结论**：**MISALIGNED**
**差异**：脚本新增了第六道审计，但 WORKFLOW.md:245 和 dispatch-protocol.md:792 仍写"五道客观审计"。state-machine.md:117 也写"scripts/check-p6-provenance.sh exit 0（证据-结论对应 + dispatch-context 审计 + BDD 总数对照由审计 3 自动执行...）"未提及审计 6。
**建议**：更新 WORKFLOW.md:245 为"六道客观审计"并增加审计 6 描述；更新 dispatch-protocol.md:792 的审计枚举列表；更新 state-machine.md:117 的审计描述。

---

**变更 5：并行派发操作指引**

文档声明（P2-design.md:79-81）：
> > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
> > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
> > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。

文档声明（P4-implementation.md:80-82）：
> 同上，完全相同的操作指引。

**结论**：ALIGNED
**分析**：这是操作性指导的补充，不涉及 gate 逻辑或协议规则变更。与 dispatch-protocol.md 中"任务间有依赖时串行，无依赖时并行"（line 601）一致。

---

**变更 6：review status 字段指导**

文档声明（dispatch-prompt.md:9-13）：
> 如果你的角色是评审/验收角色（...）：
> - 产出文件的 Header `status:` 字段初始为 `draft`
> - 评审/验收完成后，**必须将 `status:` 改为 `approved` / `rejected` / `needs-revision`**
> - gate 脚本读的是 Header 的 `status:` 字段，不是你的返回摘要——两者必须一致

**结论**：ALIGNED
**分析**：与 state-machine.md:58（`status: approved` 门槛判定字段）和 check-gate.sh 的 gate 逻辑一致。补充的是 subagent 侧的操作指导，使行为与 gate 期望对齐。

---

**变更 7：P6 验收报告记录事实原则**

文档声明（P6-acceptance.md:26）：
> **验收报告记录的是验收时的事实，不是修复后的状态。** P6-acceptance.md 的 PASS/FAIL 声明必须基于 evidence 文件的实际输出。如果验收时 BDD 为 FAIL，写 FAIL——修复后重新验收时再改 PASS。不能在同一个 P6 acceptance 里写"修复后 PASS"。

**结论**：ALIGNED
**分析**：与 state-machine.md:119（验收 = 把 P1 的 BDD 条件逐条实际跑一遍）和 P6-acceptance.md:24（功能验证和 gate 格式都必须满足）一致。补充的是对 self-authored gate 的诚信约束。

### A2: 脚本→文档对齐

**变更 1：check-p6-provenance.sh 新增审计 6**

脚本实现（check-p6-provenance.sh:256-302）：
> 审计 6 检查 P6-acceptance.md 中标 PASS 的 BDD 是否在 evidence JSON 中显示 FAIL。
> 若不一致，exit 1 拦截。

文档声明：见上方 A1 变更 4 分析——三个文档仍写"五道审计"。

**结论**：**MISALIGNED**
**差异**：脚本新增了审计 6，但文档未同步更新审计数量和描述。
**建议**：同 A1 变更 4。

---

**变更 2：pre-commit-gate.sh CHANGELOG 限制到 P8**

脚本实现：见上方 A1 变更 3 分析——仅 P8 调用 check-changelog.sh。

文档声明：见上方 A1 变更 3 分析——三个文档仍写"gate 通过后"。

**结论**：**MISALIGNED**
**差异**：同 A1 变更 3。
**建议**：同 A1 变更 3。

---

**变更 3：check-retrospective.sh / check-scope-resolved.sh 排除 progress**

脚本实现：见上方 A1 变更 2 分析。

文档声明（dispatch-protocol.md:439, dispatch-prompt.md:43）：
> 留痕文件：docs/tasks/{Txxx}/P{N}-progress.md

**结论**：ALIGNED
**分析**：progress 文件在文档中明确定义为"分阶段落盘的中间产物"，非阶段产出。脚本排除 progress 与文档定义一致。

---

**变更 4：check-pruning.sh YAML 列表格式**

脚本实现：见上方 A1 变更 1 分析。

文档声明：task-files.md:152 示例用 inline 格式，但未明确禁止 YAML 块列表格式。

**结论**：ALIGNED
**分析**：脚本是扩展兼容性，不与文档矛盾。

### A3: 一致性连锁 + 反向传播

#### A3a：一致性连锁（已知的衍生改动）

| 变更 | 连锁文档 | 是否更新 |
|------|---------|---------|
| CHANGELOG 检查限制到 P8 | WORKFLOW.md:243, state-machine.md:221, dispatch-protocol.md:819 | ❌ 未更新 |
| 审计 6 新增 | WORKFLOW.md:245, dispatch-protocol.md:792, state-machine.md:117 | ❌ 未更新 |
| 审计 6 新增 | check-protocol-consistency.py CHECK 9 锚点表 | 未新增锚点（审计 6 的关键词如 `evidence JSON` 未入锚点表） |

#### A3b：反向传播（主动推断应被影响的文件）

| 应传播到 | 是否已影响 | 说明 |
|---------|----------|------|
| `agate/scripts/README.md` | ❌ 未更新 | check-changelog.sh 描述行未标注"P8 only" |
| `agate/tests/README.md` | ❌ 未更新 | check-changelog.sh 测试用例数描述未变（实际无新测试，不是问题），但 check-p6-provenance.sh 用例数应从旧的计数更新 |
| `agate/LIMITATIONS.md` | ✅ 无需更新 | 审计 6 不改变 self-authored gate 的局限描述 |
| `SELF-GATE.md` | ✅ 无需更新 | 变更未触及 self-gate 机制 |

**结论**：NEEDS_HUMAN_REVIEW
**分析**：CHANGELOG 检查时机变更和审计 6 新增需要同步更新三个文档表格，这些是明确的连锁改动（已在 A1/A2 中标记为 MISALIGNED）。CHECK 9 锚点表是否需要为审计 6 新增条目需人工判断——审计 6 的关键词（如 `P2.57` 或 `evidence JSON`）是否值得纳入锚点表取决于维护者对锚点表覆盖度的要求。scripts/README.md 的 check-changelog.sh 描述是否需要标注"P8 only"也需人工判断（当前描述是功能性的"[Unreleased] 含 task_id"，不限阶段本身不算错）。

### A4: 测试覆盖

**bats 全量实跑结果**（2026-08-01）：

```
513 ok, 0 not ok
```

（完整命令：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`）

**新增测试覆盖分析**：

| 变更 | 测试文件 | 测试用例 | 边界覆盖 |
|------|---------|---------|---------|
| check-pruning YAML 列表格式 | check-pruning.bats: P2.52, P2.52b | 2 个 | ✅ 覆盖 YAML 块列表格式 + P3 裁剪场景 |
| SCOPE+ 排除 progress | check-retrospective.bats: RT.SCOPE_PROGRESS | 1 个 | ✅ progress 文件含 [SCOPE+] 不触发 |
| SCOPE+ 排除 progress | check-scope-resolved.bats: P2.53 | 1 个 | ✅ progress 文件含 [SCOPE+] 不触发 |
| CHANGELOG P8 限制 | pre-commit-hook.bats: IT_CHANGELOG_P54, P54b | 2 个 | ✅ P4 不触发 + P8 触发 |
| 审计 6 evidence-consistency | check-p6-provenance.bats: PV.24-27 | 4 个 | ✅ FAIL/PASS 矛盾检测 + 一致通过 + 非标准 JSON 跳过 + FAIL+FAIL 一致 |

**shellcheck**：通过（`shellcheck -S warning agate/scripts/*.sh` 无输出）

**一致性检查**：0 ERROR, 12 WARNING（全为叙事文件旧引用，与本次变更无关）

**count-tests.sh**：507 用例

**结论**：ALIGNED
**分析**：所有变更均有对应测试，边界覆盖充分。审计 6 的 4 个测试覆盖了核心场景（矛盾检测 + 一致通过 + 非标准格式跳过 + FAIL+FAIL 一致）。CHANGELOG P8 限制的 2 个测试覆盖了正反两面。

### A5: 下游影响 + 文档传播

**破坏性变更分析**：

| 变更 | 破坏性 | 说明 |
|------|--------|------|
| CHANGELOG P8 限制 | ⚠️ 行为变更 | P1-P7 阶段不再触发 CHANGELOG 检查。已有项目如果在 P4 等 commit 时依赖 CHANGELOG WARNING 提醒，将不再收到提醒。但 CHANGELOG 本就是 P8 发布准备产物，P1-P7 不需要——这是修复不是破坏 |
| 审计 6 evidence-consistency | ⚠️ 新增拦截 | P6 阶段新增审计 6 检查。如果 evidence JSON 中有 BDD 标 FAIL 但 P6-acceptance.md 标 PASS，将 exit 1 拦截。这是新增的客观审计，提高了造假成本，符合 ADR-002（可判定性） |
| YAML 列表格式 | ✅ 向后兼容 | 新增解析能力，不影响 inline 格式 |
| progress 排除 | ✅ 向后兼容 | 减少误报，不新增拦截 |
| 并行派发/review status/验收事实 | ✅ 纯文档 | 不涉及脚本逻辑变更 |

**CHANGELOG.md 未更新**：

本次变更涉及协议语义变更（CHANGELOG 检查时机从"所有阶段"改为"P8 only"+ 新增审计 6），但 CHANGELOG.md 未在 diff 中更新。根据角色文件 A5 检查项：

> 协议语义变更 + 未标注 = A5 下游影响不完整

**结论**：**MISALIGNED**
**差异**：
1. CHANGELOG.md 未记录本次变更（T084+T075 效率修复）
2. 三个文档表格未同步更新 CHANGELOG 检查时机描述（已在 A1/A2 标记）
3. 文档中审计数量描述未从"五道"更新为"六道"（已在 A1/A2 标记）

**建议**：
1. 在 CHANGELOG.md [Unreleased] 中记录本次变更
2. 更新三个文档表格
3. 更新审计数量描述

### A6: 锚点表覆盖

**当前锚点表状态**（check-protocol-consistency.py:444-627）：

| 本次变更 | 是否需新增锚点 | 当前状态 |
|---------|--------------|---------|
| 审计 6 (evidence JSON 一致性) | 可考虑 | 未新增。审计 6 的关键词如 `P2.57` 或 `evidence JSON` 未在锚点表 |
| CHANGELOG P8 限制 | 不需要 | 锚点表已有 `check-changelog.sh` 的 CHANGELOG 关键词锚点，功能不变只是调用时机变了 |
| progress 排除 | 不需要 | 锚点表已有 SCOPE_RESOLVED 和 SCOPE+ 相关锚点，排除逻辑是细节 |
| YAML 列表格式 | 不需要 | 锚点表已有 phases/risk_level 关键词锚点 |

**结论**：NEEDS_HUMAN_REVIEW
**分析**：审计 6 是新增的 gate 检查逻辑，是否需要纳入 CHECK 9 锚点表取决于维护者对锚点表覆盖度的策略。当前锚点表对 check-p6-provenance.sh 已有 `EVIDENCE_DIR` 和 `EXIT_CODE` 两个锚点，审计 6 的核心关键词是 `evidence JSON` 和 `P2.57`，可考虑新增一条：
```python
{
    "desc": "P6 evidence JSON 与 PASS/FAIL 声明一致性（审计 6）",
    "script": "agate/scripts/check-p6-provenance.sh",
    "keywords": ["evidence JSON", "声明不一致"],
},
```
但不加也不会导致 ERROR（只会在反向覆盖检查时 WARNING），属于可选增强。

### A7: 设计原则一致性

**ADR-001：隔离性——主 Agent 不写产出**
- 审计 6 新增不违反隔离性。gate 脚本由主 Agent 亲自跑（A1 原则），验证的是 verifier subagent 的产出。✅

**ADR-002：可判定性——gate 门槛机器可判定**
- 审计 6 新增了一道客观行为审计（evidence JSON vs P6 声明），符合"gate 通过/不通过由脚本 exit code 决定"。提高了造假成本，强化了可判定性。✅

**ADR-003：最小约定——不绑定技术栈**
- 审计 6 检查 evidence JSON 的 `bdd_results`/`results` 字段。这是一个**隐含的技术约定**——要求 evidence JSON 有特定结构。但审计 6 设计为"非标准 JSON 静默跳过"（PV.26 测试验证），不强制要求特定格式，只是**如果**有标准格式就检查一致性。不违反 ADR-003。✅

**ADR-004：安全网分层——hook 兜底，主动验主流程**
- CHANGELOG P8 限制不影响分层结构，只是缩小了 CHANGELOG 检查的触发范围。CHANGELOG 检查是 WARNING 级（不拦截），从 P1-P7 移除不影响安全网。✅

**ADR-005：改动性质决定流程**
- 本次变更是 BUG 修复 + 效率改进，不涉及流程入口判断。✅

**ADR-006：双层角色——执行角色 + 评审角色**
- review status 字段指导强化了评审角色的操作规范，与 ADR-006 一致。✅

**结论**：ALIGNED
