# BDD-2: 全角冒号不再导致字段静默缺失

## P5 测试证据
- `ok 150 CF.1 BDD-2: P1 frontmatter risk_level 用全角冒号（risk_level：high）→ 校验失败且报错含 risk_level`

## 本次验收独立复现
构造 frontmatter 中 `risk_level` 用全角冒号（`risk_level：high`）的 P1-requirements.md，跑
`check-frontmatter.sh`（P4-implementation.md 记录的实际交付脚本）：
```
$ bash agate/scripts/check-frontmatter.sh .../P1-requirements.md
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - while scanning a simple key
  -   in "<unicode string>", line 9, column 1:
  -     risk_level：high
  -     ^
  - could not find expected ':'
  -   in "<unicode string>", line 10, column 1:
  -     phases: [P1, P2]
  -     ^
exit=1
```
exit code = 1（拦截），错误信息明确指出第 9 行 `risk_level：high`——不是静默当作字段缺失处理，
而是显式报错并定位到具体行。符合 BDD-2 的 Given（误用全角冒号）/ When（跑 schema 校验）/
Then（校验失败 + 报错可定位）。

## 判定
PASS
