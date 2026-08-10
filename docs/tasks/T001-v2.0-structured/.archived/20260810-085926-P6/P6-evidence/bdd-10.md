# BDD-10: frontmatter 优先于正文正则

## P5 测试证据
- `ok 79 MDF.3 BDD-10: frontmatter 带引号字符串值优先于正文同名字段（证明非文本首现巧合、而是 dict 优先）`
- `ok 228 G_BDD10.1 BDD-10: check-gate.sh P2 candidate_count 在 frontmatter 与正文声明不同值时以 frontmatter 为准`

## 本次验收独立复现
frontmatter 声明 `risk_level: "high"`，正文另声明 `risk_level: low`（两处值不同）：
```yaml
---
phase: P1
task_id: T001
risk_level: "high"
---
# Requirements
risk_level: low
```
执行 `FILE=... python3 agate/scripts/agate-md-field-get.py risk_level` → 输出 `high`。
返回的是 frontmatter 中的值而非正文值，证明"frontmatter 优先，不再走正则回退"（且用带引号的
字符串值排除了"文本首现巧合"的可能——MDF.3 用的正是这个手法：若只是巧合命中第一处出现的
`risk_level:`，带引号写法会让正则匹配行为与 dict 取值行为出现可观测差异，而结果证明确实走了
dict 取值）。

## 判定
PASS
