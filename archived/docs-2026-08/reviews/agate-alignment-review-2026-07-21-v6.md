---
review_date: 2026-07-21
reviewer: protocol-alignment-review (round 6 — final re-review)
change_summary: 验证 v5 审查的 2 个 MISALIGNED 项是否已在更新后的计划中修复
source_plan: docs/plans/agate-multi-platform-ci-support-20260721.md
prior_review: docs/reviews/agate-alignment-review-2026-07-21-v5.md
---

# 协议-脚本对齐重审查（v6）

## 审查范围

本重审查仅验证 v5 发现的 2 个 MISALIGNED 项是否已在计划文档中正确修复。不重读协议文件，不新增审查范围。

---

## MISALIGNED-1: 内联 Python 脚本计数错误

**v5 发现**：计划声称 AGENTS.md 和 LIMITATIONS.md 中内联 Python 脚本计数从 8 增至 9，但 `check-p6-evidence.sh` 和 `check-p6-provenance.sh` 已在该列表中，新增 Python 代码不增加脚本数。

**修复验证**：

- `plan:889-896`（AGENTS.md 依赖节计数更新）：明确标注「v5 评审纠正：... 总数保持 8 不变」，diff 保留计数 8，仅在 `pip install` 和描述文字中增加 Pillow 依赖说明。
- `plan:898`（LIMITATIONS.md）：明确「LIMITATIONS.md 局限 6 的 8→9 计数同步撤消」。
- `plan:621-623`（B2 局限 6 diff）：`python3 + pyyaml` 行的「8 个 gate 脚本内联 python3 调用」文字未变，计数保持 8；新增独立 Pillow 条目正确表达新增依赖。

**判定：已修复。** 计划现在正确保持计数为 8，通过独立的 Pillow 依赖条目表达变更。

---

## MISALIGNED-2: scripts/README.md 三处描述遗漏

**v5 发现**：scripts/README.md 中 check-p6-evidence.sh、check-p6-provenance.sh、ci-gate-backstop.py 三个条目的描述未在文档传播节中更新。

**修复验证**：

`plan:957-971`（「补充：scripts/README.md 三处条目更新（v5 评审 MISALIGNED-2）」）：

| 条目 | 旧描述 | 新描述 | 评估 |
|------|--------|--------|------|
| `check-p6-evidence.sh` | P6 证据目录非空检查 / 0=通过, 1=缺证据/空文件, 2=WARNING | P6 证据目录非空 + md5 逐字节去重（阻断）+ 像素方差/average hash 检测（WARNING）/ 0=通过, 1=阻断, 2=WARNING | exit code 语义变更（M3.2 md5 阻断）+ 新检测均已体现 |
| `check-p6-provenance.sh` | P6 客观行为审计（三道）| P6 客观行为审计（五道 + EXIT_CODE 一致性 + 协作规范）| 审计数量（M1.3b 审计 5）+ EXIT_CODE 一致性均已体现 |
| `ci-gate-backstop.py` | push 后重跑 gate + P6 git blame 单 author WARNING | push 后重跑 gate + provenance 审计重跑 + git blame 单 author WARNING；多平台自动检测（GitHub/GitLab/Gitea）| 多平台探测（M4.1）+ provenance 重跑（M4.2）均已体现 |

**判定：已修复。** 三处条目描述完整覆盖了本次所有相关改动。

---

## 新增问题检查

对计划文档全文扫描，未发现新的不一致：

- AGENTS.md 计数（plan:889-896）与 LIMITATIONS.md B2 diff（plan:621-623）均保持 8，一致
- scripts/README.md 三处更新（plan:957-971）与各处 B1-B3、N4 描述一致（如「五道 + EXIT_CODE 一致性」与 N4 的「五道客观审计 + agent 字段协作规范」语义匹配）
- 无新增 MISALIGNED 项

---

## 最终 A1-A7 表

| # | 审查项 | v5 结论 | v6 结论 |
|---|--------|---------|---------|
| A1 | 文档→脚本对齐 | ALIGNED | ALIGNED（未复审） |
| A2 | 脚本→文档对齐 | ALIGNED | ALIGNED（未复审） |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED | **ALIGNED** — 2 项均已修复 |
| A4 | 测试覆盖 | ALIGNED | ALIGNED（未复审） |
| A5 | 下游影响 + 文档传播 | ALIGNED | ALIGNED（未复审） |
| A6 | 锚点表覆盖 | ALIGNED | ALIGNED（未复审） |
| A7 | 设计原则一致性 | ALIGNED | ALIGNED（未复审） |

**MISALIGNED: 0 | NEEDS_HUMAN_REVIEW: 0**

---

## 总体评估

v5 的 2 个 MISALIGNED 项均已正确修复：

1. **MISALIGNED-1**：AGENTS.md 和 LIMITATIONS.md 中的内联 Python 脚本计数保持 8 不变，Pillow 依赖通过独立条目表达。
2. **MISALIGNED-2**：scripts/README.md 的三处条目（check-p6-evidence.sh、check-p6-provenance.sh、ci-gate-backstop.py）均已补充完整描述。

无新问题发现。计划文档现在一致，**可进入实施。**
