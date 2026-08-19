# BDD-15 证据：复盘位置措辞同步（AGENTS.md）

文件：`agate/AGENTS.md`

## Then 子句逐项核对

Then 要求：`AGENTS.md:11` 更新为区分"历史存量复盘仍在 docs/reviews/（迁移前旧布局）"与
"新复盘归 tasks/{Txxx}/retrospective.md"，不再让"复盘在 docs/，使用者无需阅读"作为对新复盘
同样成立的过期声明留存。

## 本轮独立核实

```
$ sed -n '11p' agate/AGENTS.md
仓库根的 `docs/` 目录存放 agate **项目的开发资料**——设计文档、评审记录、路线图，以及迁移前旧布局下的历史复盘（docs/reviews/，2026-08-19 前）。这些都是仓库维护者（author）写的，**使用者无需阅读**。新复盘归 `tasks/{Txxx}/retrospective.md`（模板见 `agate/assets/templates/retrospective-template.md`），同样是维护者产物，使用者无需阅读，但路径不在 `docs/` 下。
```

（第 11 行为单行长文本，上方证据展示为原始 sed 输出，未做换行改写）

## 逐项核对

| Then 要求 | 实际文本 | 满足？ |
|-----------|---------|--------|
| 区分"历史存量复盘仍在 docs/reviews/（迁移前旧布局）" | "以及迁移前旧布局下的历史复盘（docs/reviews/，2026-08-19 前）" | 是 |
| 区分"新复盘归 tasks/{Txxx}/retrospective.md" | "新复盘归 `tasks/{Txxx}/retrospective.md`（模板见 `agate/assets/templates/retrospective-template.md`）" | 是 |
| 不再让旧声明对新复盘同样成立 | 明确把"使用者无需阅读"这句原样保留给**两支**（历史/新复盘都无需阅读），但**位置**已区分——不是把"docs/ 下的复盘"这一路径断言错误地延伸到新复盘（新复盘"路径不在 docs/ 下"一句显式排除了这个可能误解） | 是 |

**关键点**：Then 子句真正担心的是"复盘在 docs/"这句**路径断言**对新复盘不再成立而被误读为
仍成立（BDD-15 的隐含需求 4 原文："复盘产出路径改为 tasks/{Txxx}/ 后这句话与目标方案矛盾"）。
实际文本用"路径不在 docs/ 下"收尾，明确切断了"新复盘也在 docs/"这个可能的过期推论，逻辑闭环。

## 判定

**满足**——AGENTS.md:11 已改写为区分历史/新复盘两支表述，不再让旧的路径断言对新复盘成立，
避免被 P7/CI 一致性检查判定为文档漂移。
