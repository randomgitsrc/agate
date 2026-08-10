# BDD-5: 枚举字段非法值被类型校验拦截

## P5 测试证据
- `ok 152 CF.3 BDD-5: P1 frontmatter risk_level 枚举外的值（HIGH）→ 校验失败且提示 low/medium/high`

## 本次验收独立复现
frontmatter `risk_level: HIGH`（大写，不在枚举 low/medium/high 内）：
```
$ bash agate/scripts/check-frontmatter.sh .../P1-requirements.md
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - P1-requirements.md:risk_level: 非法值 'HIGH'（合法值: low, medium, high）
exit=1
```
exit=1，错误信息明确列出合法值集合 low/medium/high。符合 BDD-5 Then："校验失败并提示合法值"。

## 判定
PASS
