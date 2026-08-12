# BDD-13 — 一致性检查 0 ERROR（含 CHECK 9 锚点表 37→38）

独立重跑（非引用旧记录）：
```
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

## 锚点表数量核实（38 条，含新增 check-frontmatter.sh）
```
38
636:        "script": "agate/scripts/check-frontmatter.sh",
```

结论：CHECK 1-9 全部 PASS，0 ERROR；锚点表实测 38 条（P1 基线原文 37 条 + P2 §12 SCOPE+ 登记的新增 1 条 check-frontmatter.sh，SCOPE_RESOLVED 已在 P1-requirements.md §5 记录），与 P2-design.md §3.1.4/§12 说明一致。
