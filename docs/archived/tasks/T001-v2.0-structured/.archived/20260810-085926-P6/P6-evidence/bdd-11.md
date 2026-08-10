# BDD-11: 测试用例数不漂移

## P5 测试证据
- `P5_count` 命令结果：594 个测试用例（sanity.bats 6 另计）

## 本次验收独立复现（自己动手跑，非引用旧结果）
```
$ bash agate/tests/scripts/count-tests.sh
=== 测试用例覆盖度自检 ===
  ...(52 个 .bats 文件逐项列出)...
总计：594 个测试用例
EXIT_CODE=0
```
2026-08-10 本次验收独立重跑，结果仍为 594，与改造前基线（P2-design.md 客观数字段声明）一致。

## 594 配平机制交叉核对
P3-test-cases.md §1 给出的配平表：新增 `unit/check-frontmatter.bats`（10 个 @test）由
check-gate.bats/check-p6-format.bats/check-p6-provenance.bats/check-scope-resolved.bats/
check-retrospective.bats 五个文件各移减 1-4 条重复覆盖的既有断言（合计移减 10 条）配平，
354→344，+240（其余不动）+10（新文件）= 594。本次实测总数与该配平表推导结果一致。

## 判定
PASS
