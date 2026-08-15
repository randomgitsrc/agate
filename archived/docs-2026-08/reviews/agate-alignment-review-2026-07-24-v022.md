---
review_date: 2026-07-24
reviewer: protocol-alignment-review
change_summary: v0.22.0 superpowers 吸收 + 上下文编排 + 并行执行（P2.37-P2.44）
files_changed: [agate/assets/execution-roles/architect.md, agate/assets/execution-roles/implementer.md, agate/assets/execution-roles/verifier.md, agate/assets/review-roles/investigate.md, agate/assets/templates/dispatch-prompt.md, agate/scripts/agate-extract-context.sh, agate/tests/unit/agate-extract-context.bats, agate/dispatch-protocol.md, agate/phase-cards/P2-design.md, agate/phase-cards/P3-tdd.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P5-verification.md, agate/phase-cards/P6-acceptance.md, agate/loop-orchestration.md, docs/hardening-roadmap.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

P2.37-P2.41 是角色文件纯文档改动，无 gate 行为变化。P2.42 新脚本 agate-extract-context.sh 不被任何 gate 脚本调用（是主 Agent 辅助工具），不影响 gate 行为。P2.43 阶段卡片改动是操作指引，不改变 gate �4判定逻辑。P2.44 是状态更新纯文档。

**结论**：ALIGNED

### A2: 脚本→文档对齐

agate-extract-context.sh 的行为（从上游产出提取结构化字段）与 plan P2.42 描述一致。提取规则只提取 grep/sed 可靠提取的结构化字段（YAML 字段/BDD 标题行/计数），不提取自由文本摘要。

**F4 dispatch-prompt.md 新增 P4 回退模板节与 dispatch-protocol.md 的派发协议一致（模板是 prompt 层，不是阶段产出）。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

7 个角色文件改动 + 5 个阶段卡片改动 + 1 个 dispatch-protocol.md 拆分原则更新。所有改动在 plan 中有明确的传播路径记录。dispatch-protocol.md 拆分原则新增"按包拆分并行"维度，与阶段卡片操作指引一致。

**结论**：ALIGNED

### A4: 测试覆盖

P2.42 新增 9 个 bats 测试（EC.1-EC.9），覆盖参数校验/P1-P7 各阶段提取/--write 模式。P2.37-P2.41/P2.43-P2.44 是文档改动，无新增 bats（合理——现有 gate 不检查文档内容）。416 bats / 0 fail。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

- architect.md 方法论新增不影响 P2 gate（gate 检查的是四字段 + 候选方案数 + review status，不检查方法论内容）
- investigate.md 强化不影响任何 gate（investigate 是 review 角色，不作为阶段门槛产出被 gate 检查）
- dispatch-prompt.md 新增模板节不影响 gate（prompt 模板不是阶段产出文件）
- verifier.md 验证纪律不影响 P6 gate（纪律是认知层指引，gate 检查的是 PASS/FAIL 格式 + provenance）
- implementer.md 强化不影响 P4 gate（gate 检查的是暂存区代码文件存在性）
- P2/P4 评审并行产出文件（P2-review-eng.md 等）不被 gate 检查（gate 只检查 P2-review.md/P4-review.md）
- P6 并行产出（P6-evidence/{pkg}/results.md）不被 gate 检查（gate 只检查 P6-acceptance.md）

**结论**：ALIGNED

### A6: 锚点表覆盖

agate-extract-context.sh 命名不匹配 `check-*.sh` 模式，不被 check-protocol-consistency.py 的 CHECK 9 扫描（该函数只扫 `check-*.sh` + `pre-commit-gate.sh` + `ci-gate-backstop.py`）。这是正确的——它不是 gate 脚本，是辅助工具。

**结论**：ALIGNED

### A7: 设计原则一致性

- ADR-003（最小约定）：P2.43 并行操作指引是"可选"节，单包任务跳过，不增加默认复杂度 ✅
- ADR-001（隔离性）：P2.43 并行 subagent 各写不同文件/目录，主 Agent 汇总后统一 commit，不违反铁律 1 ✅
- P6 受限并行（方案 A）选择"不扩展脚本"而非"限制并行范围"，符合"P6 是加固最多的阶段"的判断 ✅

**结论**：ALIGNED
