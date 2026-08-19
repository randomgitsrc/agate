# BDD-8 证据：模板挂入协议本体（解决"游离"问题）

## Then 子句逐项核对

Then 要求：至少一个核心协议文件（如 `dispatch-protocol.md` 或对应的 `phase-cards/P8-release.md`）
显式引用新模板路径，使模板成为协议本体的一部分而非游离资料（可通过 grep 新路径字符串在该
协议文件中命中校验）。

## 实际核实（本轮独立 grep，非转抄）

```
$ grep -n "retrospective-template" agate/phase-cards/P8-release.md
96:  `tasks/{Txxx}/retrospective.md` 基于 `agate/assets/templates/retrospective-template.md`
```

命中 `agate/phase-cards/P8-release.md:96`，该行位于"READY 收尾检查"节（P2-design.md §1.1
BDD-8 指定挂钩点），显式引用完整新路径字符串 `agate/assets/templates/retrospective-template.md`。

## 附带核实：`roadmap.md` 旧路径引用同步（When 子句关联动作）

```
$ grep -n "postmortem-template" agate-workspace/roadmap/roadmap.md
313: ...postmortem-template.md`（→ 已于 TAG0015 迁移至 agate/assets/templates/retrospective-template.md）...
316: ...postmortem-template.md 在 docs/reviews/ 合理...（→ 已于 TAG0015 迁移至 agate/assets/templates/retrospective-template.md）
322: ...postmortem-template.md 保留在 docs/reviews/...（→ 已于 TAG0015 迁移至 agate/assets/templates/retrospective-template.md）。
```

三处旧路径引用均带同步更正脚注，指向新路径，符合 P1 §4.1 BDD-8 When 子句"`roadmap.md` 中对
旧路径的引用同步更新为新路径"。

## 判定

**满足**——`agate/phase-cards/P8-release.md` 显式引用新模板完整路径字符串，模板不再游离于
协议本体外；`roadmap.md` 三处旧路径引用均已同步更正，非遗留死链。
