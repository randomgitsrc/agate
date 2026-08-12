# BDD-18: P6 总结行不再导致逐条计数膨胀

## P5 测试证据
- `ok 315 F_BDD18.1 BDD-18: check-gate.sh P6 审计口径不把总结行（- PASS: 16，无 BDD 编号）计入逐条 PASS/FAIL 总数`

## 本次验收独立复现
构造 P6-acceptance.md：正文含 1 条真实逐条结果（`- PASS BDD-1: ...`）+ 1 条容易被旧版 grep
误判的总结行（`- PASS: 16`，无 BDD 编号），**frontmatter 无 pass/fail 汇总**（走旧格式回退路径，
确保测的是正文计数逻辑本身，而非 frontmatter 优先路径）：
```yaml
---
phase: P6
---
- PASS BDD-1: works (evidence.log)
- PASS: 16
```
执行：
```
$ bash agate/scripts/check-gate.sh P6 <TASK_DIR>
GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL=1。BDD 总数对照由 check-p6-provenance.sh 审计 3 自动执行。
REAL EXIT=2
```
`P6_TOTAL=1`——如果总结行 `- PASS: 16` 被误计入，结果应为 2（甚至因为该行的数字"16"被误解析而
更离谱）。实测结果只统计了那条带 BDD 编号的真实逐条行，总结行未被计入。F11 摩擦（"- PASS: 16"
类总结行被 `grep -ciE '^\s*- (PASS|FAIL)'` 误计为逐条 PASS/FAIL）已消除。

## DESIGN_GAP 交叉核对（P4-implementation.md 第 196 行）
[DESIGN_GAP]：check-gate.sh P6 分支旧格式回退路径用的是较宽松正则
`^\s*- (PASS|FAIL)\b.*BDD-[0-9]`（只要求行内含 BDD 编号，不要求紧邻），而非
P2-design.md §3.2.1 给出的严格锚定形式 `^\s*- (PASS|FAIL) BDD-[0-9]`。原因是既有测试用例
G6.7（`- fail: BDD-2 broken`，FAIL 与 BDD 编号之间隔着冒号）要求兼容。check-p6-provenance.sh
审计 3 的 `P6_BODY_STRICT` 计数则严格照抄设计原文正则，两处口径故意不同。
本次验收观察：这个宽松度差异不影响本条 BDD-18 已验证的核心结论（总结行 `- PASS: 16` 本身既无
BDD 编号也不满足两种正则中的任何一种，两个口径下都不会被计入）——DESIGN_GAP 影响的是"哪些历史
写法的正文行能被算作有效逐条结果"的边界宽严，不影响"总结行不计入"这一 BDD-18 断言。

## 判定
PASS
