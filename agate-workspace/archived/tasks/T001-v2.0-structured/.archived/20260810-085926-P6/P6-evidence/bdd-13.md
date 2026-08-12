# BDD-13: 一致性检查 0 ERROR（含 CHECK 9 锚点表 37→38）

## P5 测试证据
- `P5_consistency` 命令结果：CHECK 1/2/3/4/6/7/8/9 全部 PASS，0 ERROR
- `ok 535 CON.8 BDD-13: CHECK 9 协议-脚本结构对齐（含新增 check-frontmatter.sh 锚点，37→38）`

## 本次验收独立复现（自己动手重跑，非引用旧结果）
```
$ python3 agate/scripts/check-protocol-consistency.py
================================================================
  agate 协议结构一致性检查 (P3-1)
================================================================
  ✅ PASS  CHECK 1  YAML 代码块可解析
  ✅ PASS  CHECK 2  仓库内文件引用存在
  ✅ PASS  CHECK 3  协议文件无硬编码行号
  ✅ PASS  CHECK 4  gate_commands 键集合一致
  ✅ PASS  CHECK 6  LICENSE 与 gstack 归属
  ✅ PASS  CHECK 7  version badge 与 git tag
  ✅ PASS  CHECK 8  v0.6 关键词存在性
  ✅ PASS  CHECK 9  协议-脚本结构对齐
----------------------------------------------------------------
  🎉 全部检查通过，协议结构一致性无问题。
```
2026-08-10 本次验收独立重跑，0 ERROR，与 P5 结果一致。

## 锚点表 37→38 的 SCOPE+ 说明
P2-design.md §12 / P1-requirements.md §5 SCOPE+ 登记：新校验器 `check-frontmatter.sh` 触发 CHECK 9
反向覆盖检查，锚点表须从 37 增至 38（新增一条 `check-frontmatter.sh` 锚点，desc:
frontmatter schema 校验，keywords: frontmatter，caller: pre-commit-gate.sh）。已标注为
[SCOPE_RESOLVED]，P4-implementation.md 第 68-74 行确认落地：`SCRIPT_ALIGNMENT_ANCHORS` 追加第
38 条，`check_anchor_coverage` 不再对 check-frontmatter.sh 输出 WARNING。BDD-13 的验收表述
（P3-test-cases.md）已注明"37 条既有 + 新增 1 条 = 38 条全过，0 ERROR"，本次实测 0 ERROR 且
CHECK 9 PASS，与该表述一致。

## 判定
PASS
