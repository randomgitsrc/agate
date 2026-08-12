# BDD-7: 校验错误信息可定位修复

## P5 测试证据
- `ok 156 CF.7 BDD-7: P2 frontmatter candidate_count 类型错误（字符串而非 int）→ 报错含字段名 candidate_count`

## 本次验收独立复现
frontmatter `candidate_count: "two"`（字符串而非 int）：
```
$ bash agate/scripts/check-frontmatter.sh .../P2-design.md
GATE FRONTMATTER: .../P2-design.md frontmatter 格式错误：
  - P2-design.md:candidate_count: 类型错误（应为 int，实际 str）
exit=1
```
错误信息含字段名 `candidate_count`、期望类型 `int`、实际类型 `str`——subagent 可据此直接定位并修复
（不需要额外排查是哪个字段、哪种类型不对）。

## 补充：异常处理健壮性（P4-review CRITICAL 修复的关联证据）
P4-implementation.md 记录了一处 Review 阶段发现的 CRITICAL：深嵌套 risk_level 触发 RecursionError 时
校验器会崩溃且 check-frontmatter.sh 原实现会把崩溃误判为"无错误"从而放行坏格式。已修复为
try/except 包裹 + fail-closed（校验器异常退出时 shell 层 exit 1 而非静默通过）。这不是 BDD-7 字面
覆盖的场景，但属于"错误信息可定位"这条防线的健壮性延伸——校验器本身崩溃时也不会误判为通过，
而是给出明确的异常信息并拦截。P4-implementation.md 记录该修复的手动验证：修复前 exit 0（放行），
修复后 exit 1，错误输出 `P1-requirements.md: frontmatter 处理异常（maximum recursion depth
exceeded while calling a Python object）`。

## 判定
PASS
