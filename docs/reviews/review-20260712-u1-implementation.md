---
review_date: 2026-07-12
reviewer: plan-eng-review
review_target:
  - U1 implementation (feat/u1-p1-requirements-review branch)
  - 8 commits, 15 files, +364/-21 lines
verdict: pass-with-minor（0 blocking，2 minor，3 observation；实现忠实匹配方案 v7 ⑧⑩N3）
status: pass-with-minor
---

# U1 实施评审

## 验证结果

| 检查 | 结果 |
|------|------|
| bats | 254/254 PASS（含新增 6 个 P1 gate 用例） |
| consistency | 0 ERROR（6 WARNING 均为叙事文件引用，pre-existing） |
| shellcheck | 0 warning |
| 变更文件 | 15 files, +364/-21 |

## 交叉引用核验

| # | 检查项 | 结果 |
|---|--------|------|
| 1 | check-gate.sh P1 gate vs state-machine.md P1 转移规则 | ✅ MATCH：均要求 P1-review.md + status:approved + agent≠main + BDD 锚点 |
| 2 | dispatch-protocol.md P1 门槛 vs check-gate.sh P1 gate | ✅ MATCH |
| 3 | WORKFLOW.md P1 评审角色 vs requirements-review.md role_id | ✅ MATCH |
| 4 | dispatch-protocol.md 迭代循环表 vs 5 个 phase-card 注释 | ✅ MATCH：P1/P2/P4/P6/P7 均有 ⑩ 注释 |
| 5 | N3 P7 WARNING 触发条件 | ✅ CORRECT：仅 DESIGN_GAP_REVIEWED>0 且缺跨文件引用时触发 |
| 6 | CHECK 9 新锚点 | ✅ CORRECT：P1 + agent=main 关键词均存在于 check-gate.sh |
| 7 | P1 agent=main 检查 vs P2 agent=main 检查 | ✅ 同模式，P1 对缺 agent 更严（exit 1 vs exit 2），合理 |
| 8 | BDD 锚点正则 `BDD-\|B[0-9]` | ✅ 匹配 B01/BDD-01，不匹配裸 approved/BDD 编号引用文本 |

## Findings

### F1 🟡 P1 缺 agent 字段 exit 1 vs P2 缺 agent 字段 exit 2

check-gate.sh P1 分支对缺 agent 字段 exit 1（硬拦），P2 分支对同样情况 exit 2（WARNING 向后兼容）。这是有意设计差异（P1 review 是新增强制机制，P2 review 是既有可选机制），但未在代码注释中说明理由。

- Evidence: `check-gate.sh:32-35` vs `check-gate.sh:71-74`
- Fix: 无需改代码。可在 P1 分支加一句注释说明"intentionally stricter than P2 (P1 review is mandatory and new)"

### F2 🟡 B[0-9] 正则较松

`BDD-|B[0-9]` 会匹配任何 B+数字开头的词（如 "B2B integration"）。在 P1-review.md 语境下误匹配极低，且方案已诚实标注"结构兜底非语义审查"。

- Evidence: `check-gate.sh:40`
- Fix: 无需改。若收紧可用 `\bB[0-9]{2,}`，但方案未要求

### F3 🟢 P7 N3 WARNING 无活跃 bats 测试

P7 N3 WARNING 代码已加入 check-gate.sh，但 bats 测试用了 `skip`。WARNING 不改变 exit code，bats 难以验证 stderr 内容。与 plan Task 3 一致。

### F4 🟢 requirements-review.md 用 agent 字段而非 mode

方案草稿写 `mode: 需求基线评审`，实现用 `agent: requirements-review`（与 design-review.md 的 `agent: design-review` 对称）。实现更符合既有约定。

### F5 🟢 integration tests 主动适配

pre-commit-hook.bats 的 4 个测试 fixture 主动增加了 P1-review.md，避免因 check-gate P1 新要求导致集成测试失败。plan 未显式要求但必要。

## 裁定

| 项 | 裁定 |
|----|------|
| ⑧ P1 需求评审 | ✅ 完整实现 |
| ⑩ do→review 迭代循环 | ✅ 完整实现 |
| N3 review 实质锚点 | ✅ 完整实现 |
| 协议文档同步 | ✅ 完整实现 |
| bats | ✅ 254/254 |
| consistency | ✅ 0 ERROR |
| shellcheck | ✅ 0 warning |

**判定：pass-with-minor**。无 blocking。实现忠实匹配方案 v7 ⑧⑩N3，所有交叉引用一致。F1/F2 是有意设计差异，F3-F5 是合理偏离。

*评审依据：feat/u1-p1-requirements-review 分支全量代码实核 + 方案 v7 ⑧⑩N3 逐条比对。*
