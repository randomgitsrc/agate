## 11:10:37 代码改动完成
- 新增 add_mutually_exclusive_group()：--strict / --strict-errors-only 互斥
- main() 尾部新增 `if args.strict_errors_only: return 0`（在 rep.errors 检查之后、--strict 检查之前）
- print 提示分支（"仅有 N 个 WARNING，无 ERROR。"）本就与 args.strict 无关，未改动，天然复用

## 11:10:45 自查完成
- pytest -k strict_errors_only: 3 passed
- pytest -k "not strict_errors_only": 24 passed（既有矩阵不受影响）
- 未碰 phase-cards/P2-design.md

