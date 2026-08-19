# BDD-16 证据：存量 4 份复盘文档处理方式（保留原位 + 标注）

## Then 子句逐项核对

Then 要求：存量文件保留在原路径不做物理迁移，每份文件顶部追加一行标注（如"> 历史复盘（迁移前
旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`"），`roadmap.md` 等活文档对这 5 份文件的
路径引用保持不变。

## 本轮独立核实（5 份文件逐一读取首行）

```
$ for f in retrospective-tag0008-docs-20260817.md retrospective-tag0010-0011-docs-20260815.md \
    retrospective-tag0010-0011-docs-20260815-review.md retrospective-tag0013-docs-20260816.md \
    retrospective-tag0014-docs-20260816.md; do
  echo "=== $f ==="; head -1 docs/reviews/$f
done

=== retrospective-tag0008-docs-20260817.md ===
> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）
=== retrospective-tag0010-0011-docs-20260815.md ===
> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）
=== retrospective-tag0010-0011-docs-20260815-review.md ===
> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）
=== retrospective-tag0013-docs-20260816.md ===
> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）
=== retrospective-tag0014-docs-20260816.md ===
> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）
```

## 逐项核对

| Then 要求 | 实际 | 满足？ |
|-----------|------|--------|
| 5 份文件顶部各追加一行标注 | 全部 5 份文件首行均为该标注（本轮逐一 `head -1` 核实） | 是 |
| 标注文案实质与 P1 §4.6 BDD-16 给出的原文一致 | "历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`" 核心句一致（额外补充了模板路径，属增强非矛盾） | 是 |
| 不做物理迁移，文件保留原路径 `docs/reviews/` | `ls docs/reviews/` 命中全部 5 个文件名，`git status --short docs/reviews/` 为空（无未提交的删除/新增/重命名记录），说明文件确实原地保留、无物理搬迁 | 是 |
| `roadmap.md` 对这 5 份文件的路径引用保持不变 | `git diff HEAD~2 -- agate-workspace/roadmap/roadmap.md \| grep -c "retrospective-tag00"` → 0（roadmap.md 的本次 diff 未涉及任何 `retrospective-tag00*` 文件名字符串，说明未改动对这些文件的引用） | 是 |

## 判定

**满足**——5 份存量复盘文档（P1 计"4 份"因 tag0010-0011 含 2 个物理文件）均在原路径保留、
顶部标注文案齐全且逐字命中"历史复盘"与新路径字符串，`roadmap.md` 对这些文件的引用未被
本任务改动，符合 P1 已定案的"保留原位 + 顶部标注"决策。
