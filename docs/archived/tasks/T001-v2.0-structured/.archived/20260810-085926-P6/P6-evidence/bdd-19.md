# BDD-19: P7 BLOCKER/DEVIATION 状态入 frontmatter（计数结构化）

## P5 测试证据
- `ok 322 PV_BDD19.1 BDD-19: check-gate.sh P7 frontmatter blocker_count/deviation_count 均 0 时判定通过（不再用非计数行排除正则）`

## 本次验收独立复现
构造 P7-consistency.md：frontmatter 声明全部计数字段为 0，**正文故意包含一条容易与"非计数行排除
正则"产生歧义的散文**（"[BLOCKER]: 0 条（历史遗留写法...）"——这正是 F13 摩擦原文描述的
歧义场景）：
```yaml
---
phase: P7
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---
正文含一条容易与"计数行"混淆的散文： [BLOCKER]: 0 条（历史遗留写法，不应影响判定，因为判定改读 frontmatter）
```
执行：
```
$ bash agate/scripts/check-gate.sh P7 <TASK_DIR>; echo "REAL EXIT=$?"
REAL EXIT=0
```
exit=0（通过）。判定完全基于 frontmatter 的 `blocker_count`/`deviation_critical_count`
（均为 0），不依赖 `grep -cvE '\[BLOCKER\][:：]?[0-9]+条?$'` 这类"排除计数行"的正则去解析正文
散文——即使正文含有歧义写法也不影响判定结果，F13 消除。

## 判定
PASS
