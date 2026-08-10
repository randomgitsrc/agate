# BDD-12: frontmatter 无超过 3 层的嵌套结构

## P5 测试证据
- `ok 157 CF.8 BDD-12: P1 frontmatter 字段嵌套深度 > 3 层 → 校验失败`

## 本次验收独立复现
构造 4 层嵌套（超出 schema 允许的 ≤3 层）：
```yaml
coupling_checklist:
  - level1:
      level2:
        level3:
          level4: too_deep
```
执行：
```
$ bash agate/scripts/check-frontmatter.sh .../P1-requirements.md
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - P1-requirements.md:coupling_checklist: 嵌套深度超过 3 层
exit=1
```
校验器能拦截超深嵌套（BDD-12 验收对象是"校验器能拦截"这一机制本身，而非"schema 定义本身不含
嵌套"——P3-test-cases.md §9 已注明 CF.8 是唯一刻意构造的"非法反例"）。

## 补充：schema 定义本身无超 3 层嵌套（P2-design.md §3.1.1 原始设计）
P2-design.md 目标 frontmatter 样例中，迁移字段全部为单层 `key: value` 或一层列表（如
`coupling_checklist: [api-schema: checked]`），未见任何 >3 层嵌套字段定义，符合"schema 定义本身
不引入深嵌套"的设计意图。

## 判定
PASS
