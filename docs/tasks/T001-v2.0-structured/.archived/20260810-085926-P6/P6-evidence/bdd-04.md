# BDD-4: 缩进错误被校验器拦截

## P5 测试证据
- `ok 151 CF.2 BDD-4: P1 frontmatter coupling_checklist 列表项缩进错误 → 校验失败且报错可定位`

## 本次验收独立复现
构造 `coupling_checklist` 列表项缩进不一致（第二项比第一项多缩进一格）的 frontmatter：
```yaml
coupling_checklist:
  - api-schema: checked
   - db-migration: checked
```
执行：
```
$ bash agate/scripts/check-frontmatter.sh .../P1-requirements.md
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - while parsing a block collection
  -   in "<unicode string>", line 14, column 3:
  -       - api-schema: checked
  -       ^
  - expected <block end>, but found '<block sequence start>'
  -   in "<unicode string>", line 15, column 4:
  -        - db-migration: checked
  -        ^
exit=1
```
exit=1，错误信息含具体行号（14/15）和列号，可直接定位到缩进错误的位置。v0.6 yaml-indent 类回归
（此前无机器校验，产出文件从不校验 YAML 合法性）在这里被明确拦截。

## 判定
PASS
