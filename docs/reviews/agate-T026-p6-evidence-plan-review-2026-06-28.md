---
type: review
source: docs/plans/agate-T026-p6-evidence-2026-06-28.md
trace_id: agate-T026-p6-evidence-plan-review-2026-06-28
created: 2026-06-28
status: done
---

# T026 P6 证据存在性计划专家评审

> 评审焦点：证据存在性检查是否真正堵住伪造路径？是否引入新的误判/假阴性？

---

## 问题 1：证据数量 ≥ BDD 总数的假设过于严格

计划要求 `P6-evidence/ 文件数 ≥ P1 BDD 总数`，即每条 BDD 至少一个证据文件。

但 T026 的 16 条 BDD 中，查询类 BDD（如 BE-1 "列出所有 entries"）的验收证据是断言值（数据库查询结果），不是截图。verifier.md 当前写的是"查询类 BDD 可不截图（断言值是唯一证据）"。如果查询类 BDD 的断言值写在 P6-acceptance.md 内联（如 `实际值: [...]`），那证据文件数就可能 < BDD 总数，导致假阴性。

**修正**：证据数量条件改为 `P6-evidence/ 文件数 ≥ ui_affected BDD 数`（UI 类 BDD 必须有截图，非 UI 类 BDD 的断言值写在 P6-acceptance.md 内联即可）。但这引入了"区分 UI/非 UI BDD"的判定，脚本化困难。

**更安全的修正**：`P6-evidence/ 非空`（只检查目录存在且有内容），不强制文件数。理由：伪造的关键特征是"无任何证据"，不是"证据数少于 BDD 数"。一个编造 11 条 PASS 的主 Agent，连一张截图都不会有——`非空`已经能堵住这个场景。`文件数 ≥ BDD 总数` 是过度约束，会误伤合理的验收（如纯后端任务的 P6 可能只有 test-output.log 一个文件）。

**建议**：动作 1/2/3/8 中的文件数条件全部降级为"目录存在且非空"，去掉 `文件数 ≥ BDD 总数`。

## 问题 2：P6-evidence/ 路径是 agate 协议硬编码，但证据目录名应可由项目自定义

计划硬编码 `P6-evidence/` 作为证据目录名。但不同项目的证据存放方式不同——PeekView 用 `evidences/`，其他项目可能用 `screenshots/` 或 `artifacts/`。

然而，agate 的设计风格是约定默认路径 + P2 gate_commands 可覆盖。P5 的 gate_commands 已经是动态注入的，P6 的证据路径也可以类似处理。

**修正**：协议级约定默认路径为 `{task}/P6-evidence/`，但允许 P2-design.md 的 `gate_commands.P6.evidence_dir` 覆盖。check-gate.sh 从 P2 读取（但 check-gate.sh P6 当前返回 exit 2 需主 Agent 自判，所以脚本侧暂不读 P2，只用默认路径）。

**建议**：协议文件用约定路径 `{task}/P6-evidence/`，不加覆盖机制（过度工程化）。如果未来有项目需要不同路径，再扩展。

## 问题 3：动作 7 "不接受主 Agent 自写脚本替代 verifier 交付的脚本"不可强制执行

这是文本约束，不是可判定约束。主 Agent 完全可以忽略这个要求，自写脚本，跑完把输出落盘到 `P6-evidence/test-output.log`——gate 只检查文件存在，不检查文件内容是否来自 verifier 交付的脚本。

T026 的故障不是"主 Agent 自写脚本"，而是"主 Agent 不跑任何脚本直接写 PASS"。自写脚本 + 真正执行 + 证据落盘 = 虽然不是最优路径，但结果是真实的。自写脚本 + 不执行 + 编造 PASS = 才是故障。

**修正**：动作 7 的措辞改为建议性而非禁止性：

```
## P6 verifier 脚本执行
P6 verifier 交付的验证脚本（Playwright / shell / pytest）应由主 Agent 执行。
执行输出落盘到 P6-evidence/test-output.log。
若主 Agent 需要自写脚本（如 verifier 脚本不兼容当前环境），自写脚本的执行输出也落盘到 P6-evidence/test-output.log。
关键约束：P6-evidence/ 必须有执行产出，不接受空目录。
```

这把约束从"不得自写"（不可强制）改为"必须有执行产出"（可强制——目录非空）。

## 问题 4：P7 标 `self-authored` 但无缓解措施

gate 分类标记中 P7 被标为 `self-authored`，但缓解措施只写了"P5 回归测试兜底"。P7 的一致性标注确实可以伪造，但 P7 的标注是用来标记"实现和设计是否一致"，不一致 = DEVIATION/BLOCKER，一致 = OK。伪造"一致"的动机是"让 gate 通过"，但 P5 回归测试兜底意味着即使 P7 标注被伪造，bug 不会漏过。

这个缓解措施是充分的。但 `⚠️ self-authored` 标记在门槛表中可能引起误解——读者可能以为 P7 gate 不可信。建议在分类标记中明确 P7 的兜底机制。

**建议**：动作 4 的分类表中 P7 行改为：`P7 | 一致性标注 + P5 兜底 | 是，但 P5 回归测试兜底`。

---

## 评审结论

| 类别 | 数量 | 详情 |
|------|------|------|
| Critical | 0 | — |
| Important | 2 | 文件数条件降级为"非空"；动作 7 改为建议性 |
| Minor | 2 | P7 分类标记措辞；路径约定不加覆盖机制（已采纳） |

**判定：可实施，但需修正 Important 项。**

核心修正：
1. `文件数 ≥ BDD 总数` → `目录存在且非空`（避免假阴性，伪造特征是"无证据"不是"证据少"）
2. 动作 7 从"不接受自写脚本"改为"必须有执行产出"（不可强制的禁止是噪音）
