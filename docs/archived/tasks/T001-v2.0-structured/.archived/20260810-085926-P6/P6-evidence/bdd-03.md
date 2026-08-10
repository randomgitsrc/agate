# BDD-3: phases 内联与块式两种格式统一解析

## P5 测试证据
- `ok 80 MDF.4 BDD-3: phases 在 frontmatter 内以块式列表（每行 - Pn）声明 → 解析为空格连接列表`

## 本次验收独立复现
frontmatter 声明块式列表：
```yaml
phases:
  - P1
  - P2
  - P3
```
执行 `FILE=... python3 agate/scripts/agate-md-field-get.py phases` → 输出 `P1 P2 P3`。
块式列表被正确解析为 v0.35 兼容的空格连接字符串，无需内联方括号格式 `[P1,P2,P3]`。
符合 BDD-3 Then："解析结果与声明一致（不要求内联方括号格式）"。

## 判定
PASS
