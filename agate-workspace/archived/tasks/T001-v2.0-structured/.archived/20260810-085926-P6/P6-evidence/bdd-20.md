# BDD-20: P7 DESIGN_GAP_REVIEWED 配对状态入 frontmatter

## P5 测试证据
- `ok 346 PV_BDD20.1 BDD-20: check-gate.sh P7 frontmatter design_gap_reviewed_count < design_gap_count 时拦截（不再用数量相减的 0-vs-0 歧义判定）`
- `ok 508 R2.1 BDD-20: frontmatter design_gap_count == design_gap_reviewed_count（已全部配对）→ exit 0`
- `ok 509 R2.2 BDD-20: frontmatter design_gap_reviewed_count(0) < design_gap_count(1) → exit 1（未配对）`
- `ok 510 R2.3 P4 有 DESIGN_GAP 但 P7 frontmatter design_gap_count 为 0（未转抄）→ exit 1（交叉核对，回归 R2.3）`
- `ok 511 R2.3b BDD-20: P4 DESIGN_GAP 数量 ≤ P7 frontmatter design_gap_count 且已 REVIEWED → exit 0`

## 本次验收独立复现
构造 P7-consistency.md：`design_gap_count: 2, design_gap_reviewed_count: 1`（reviewed < count，
未配对）：
```
$ bash agate/scripts/check-gate.sh P7 <TASK_DIR>
GATE P7: 有 1 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]（frontmatter: design_gap_count=2, design_gap_reviewed_count=1）——主 Agent 需审查 implementer 的自主决策
REAL EXIT=1
```
exit=1（拦截），错误信息明确引用 frontmatter 的两个计数字段（design_gap_count=2,
design_gap_reviewed_count=1），判定逻辑是 `reviewed < count` 直接比较而非"数量相减看是否为
0"——F14 的"0-vs-0 配对歧义"（数量对但配对语义不一定对）已消除，因为判定依据是结构化配对状态
而非数量运算。

## 判定
PASS
