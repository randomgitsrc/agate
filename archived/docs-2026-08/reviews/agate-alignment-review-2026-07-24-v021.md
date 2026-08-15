---
review_date: 2026-07-24
reviewer: protocol-alignment-review
change_summary: v0.21.0 维护补丁：LIMITATIONS.md ADR 交叉引用、protocol-alignment-review.md BDD 传播路径行、check-retrospective.sh dispatch-context/AGATE_CARD 排除、check-p6-evidence.sh 错误消息详情
files_changed: [agate/LIMITATIONS.md, agate/assets/review-roles/protocol-alignment-review.md, agate/scripts/check-retrospective.sh, agate/scripts/check-p6-evidence.sh, agate/tests/unit/check-retrospective.bats, agate/tests/unit/check-p6-evidence.bats, docs/hardening-roadmap.md, docs/plans/agate-protocol-maintenance-patch-20260724.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | NEEDS_HUMAN_REVIEW |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**A1.1 LIMITATIONS.md ADR 交叉引用**

5 处新增 ADR 引用，逐一验证：

| 局限 | 引用 | ADR 存在 | 关系准确 |
|------|------|----------|----------|
| 局限 1 (LIMITATIONS.md:11) | → ADR-002 | adr.md:41 ✅ | ADR-002 后果"gate 脚本只能检查客观条件"，与"测试本身正确"局限语义一致 |
| 局限 2 (LIMITATIONS.md:19) | → ADR-006 | adr.md:165 ✅ | ADR-006 双层角色，局限 2 同源模型盲区共享 |
| 局限 3 (LIMITATIONS.md:47) | → ADR-001, ADR-005 | adr.md:8, adr.md:128 ✅ | ADR-001 隔离性不约束裁量权，ADR-005 改动性质判断依赖主 Agent |
| 局限 5 (LIMITATIONS.md:82) | → ADR-002 | adr.md:41 ✅ | ADR-002 可判定性不覆盖协议文档自身 |
| 局限 6 (LIMITATIONS.md:94) | → ADR-003 | adr.md:69 ✅ | ADR-003 不绑定项目技术栈，但 agate 自身有运行时依赖 |

**结论**：ALIGNED

**A1.2 protocol-alignment-review.md BDD 传播路径行**

新增行（:37）列出 13+ 文件。验证关键脚本：
- check-p6-provenance.sh:131 `grep -cE '^#### BDD-[0-9]'` ✅
- check-gate.sh:61 `grep -qE 'BDD-[0-9]'` ✅
- check-protocol-consistency.py:623-625 CHECK 9 含 `BDD-[0-9]` ✅

路径完整性：行中文件名简写与表格惯例一致。

**结论**：ALIGNED

**A1.3 check-retrospective.sh dispatch-context 排除 + AGATE_CARD 块剥离**

check-retrospective.sh:37-38 与 check-scope-resolved.sh:18-20 逐字符一致。

**结论**：ALIGNED

### A2: 脚本→文档对齐

check-retrospective.sh 排除逻辑是实现一致性修复（与 check-scope-resolved.sh 对齐），不需要单独协议文档。
check-p6-evidence.sh DETAILS 输出是 UX 增强，不改变 exit code，不需要文档更新。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

A3a 连锁：adr.md 不需反向引用 LIMITATIONS.md（方向性是局限→决策）。✅
A3b 反向传播：

1. check-retrospective.sh:37 dispatch-context 排除缺行内注释（check-scope-resolved.sh:18-19 有注释）。**NEEDS_HUMAN_REVIEW**

[HUMAN_CONFIRMED: 2026-07-24 确认：check-retrospective.sh 已有注释"C3 修复：与 check-scope-resolved.sh 一致"（:33），读者可跳转查看。补充注释是 nice-to-have 非必须，不修。]

2. protocol-alignment-review.md:37 BDD 传播路径行中角色文件未标注目录前缀。**NEEDS_HUMAN_REVIEW**

[HUMAN_CONFIRMED: 2026-07-24 确认：与表格其他行简写惯例一致（如 check-*.sh 行也只写脚本名），标注目录会增加行长度降低可读性，不修。]

**结论**：NEEDS_HUMAN_REVIEW → 2 项已人工确认，可 commit

### A4: 测试覆盖

- check-retrospective.sh: +2 测试（RETRO_SCOPE_DC.1, RETRO_SCOPE_CARD.1）覆盖两个排除逻辑 ✅
- check-p6-evidence.sh: +4 测试（EVIDENCE_NO_REF_DETAIL.1, EVIDENCE_EMPTY_DETAIL.1, EVIDENCE_MD5_DETAIL.1/2）覆盖 3 处 DETAILS + 空格文件名边界 ✅
- 全量 bats：405 passed / 0 failed ✅

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

- check-retrospective.sh：新增排除只减少 WARNING（减少误报），无破坏性 ✅
- check-p6-evidence.sh：DETAILS 不改变 exit code，md5 逻辑修复是 bugfix ✅
- LIMITATIONS.md / protocol-alignment-review.md：纯文档 ✅
- 无协议语义变更，不需 CHANGELOG 条目 ✅

**结论**：ALIGNED

### A6: 锚点表覆盖

CHECK 9 无需新增锚点——排除逻辑和 DETAILS 输出不是新协议规则。
consistency CHECK 9 PASS ✅

**结论**：ALIGNED

### A7: 设计原则一致性

所有变更符合 ADR-001 至 ADR-006，无未记录的架构决策。✅

**结论**：ALIGNED
