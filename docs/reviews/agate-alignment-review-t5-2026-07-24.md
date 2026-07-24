---
review_date: 2026-07-24
reviewer: protocol-alignment-review
change_summary: T5 修复：agate-next-card.sh 路径解析解耦（AGATE_ROOT 替代 AGATE_REPO + ci-gate-backstop.py __file__ 相对路径）
files_changed: [agate/scripts/agate-next-card.sh, agate/scripts/ci-gate-backstop.py, agate/tests/unit/agate-next-card.bats, docs/hardening-roadmap.md, docs/plans/agate-t5-path-resolution-fix-20260724.md]
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

agate-next-card.sh 是 CLI 工具（输出卡片全文），无 gate 规则对应文档。ci-gate-backstop.py 路径解析改为 `__file__` 相对，行为不变（定位同一个 check-gate.sh/check-p6-provenance.sh）。

**结论**：ALIGNED

### A2: 脚本→文档对齐

REL_CARD 路径行从 `agate/phase-cards/...` 变为 `phase-cards/...`——这是 CLI 输出格式变化，不影响 gate 行为或协议语义。无协议文档需更新。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

agate-inject-card.sh 已用 AGATE_ROOT（:10），无传播需求。pre-commit-gate.sh 不直接调用 agate-next-card.sh。无遗漏。

**结论**：ALIGNED

### A4: 测试覆盖

+2 测试：NC_ROOT.1（AGATE_ROOT 环境变量覆盖）、NC_ROOT.2（无 .git 目录场景）。407 bats / 0 fail。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

- REL_CARD 变化：hook sha256 校验用 body（不含 header 路径行），无影响
- ci-gate-backstop.py：`__file__` 在 CI 环境解析为 `agate/scripts/ci-gate-backstop.py`，`.parent.parent` = 协议目录，与原路径等效
- 无破坏性变更，无文档传播需求

**结论**：ALIGNED

### A6: 锚点表覆盖

agate-next-card.sh 不在 CHECK 9 锚点表（只覆盖 check-*.sh + pre-commit-gate.sh + ci-gate-backstop.py）。ci-gate-backstop.py 锚点关键词不变。

**结论**：ALIGNED

### A7: 设计原则一致性

ADR-003（最小约定）：路径解耦使脚本不依赖特定目录名，更符合"不绑定"原则。✅

**结论**：ALIGNED
