# BDD-9: 旧格式文件（正文内嵌、无 frontmatter）仍被正确读取

## P5 测试证据
- `ok 78 MDF.2 BDD-9: 旧格式（frontmatter 无 risk_level，只在正文）仍通过正则回退正确读取`
- `ok 238 G_BDD9.1 BDD-9: check-gate.sh P2-design.md 旧格式（四字段仅在正文、frontmatter 无这些字段）仍被正确读取`
- `ok 365 P2.5 BDD-9: check-pruning.sh 旧格式（--legacy-fields，risk_level 在正文非 frontmatter）risk=high 裁剪 P3 期望 exit 1（回退路径行为与 v0.35 一致）`

## 本次验收独立复现
构造 frontmatter 只含 phase/task_id（无 risk_level），risk_level 只在正文声明：
```yaml
---
phase: P1
task_id: T001
---
# Requirements
risk_level: medium
phases: [P1, P2]
```
执行 `FILE=... python3 agate/scripts/agate-md-field-get.py risk_level` → 输出 `medium`。
frontmatter 完全不含 risk_level 字段（key 不存在），双读工具走正则回退路径读到正文声明值，
读取结果与 v0.35 行为一致（旧格式在途任务无需迁移即可继续被正确读取）。

## 判定
PASS
