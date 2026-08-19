# BDD-4 证据：产出流向强制约定（技术债登记核对清单行）

文件：`agate/assets/templates/retrospective-template.md`

## Then 子句逐项核对

Then 要求：技术债登记核对清单行标记为"是"时，"未触发后果/原因"列必须填写具体 DEBT 编号或
roadmap RM 编号（不允许留空或写"待定"），模板对该字段的必填性做显式强制说明；
check-retrospective.py 侧不做内容语义解析（沿用只提醒不阻断既有边界）。

| 要求 | 实际（行号） |
|------|-------------|
| 核对清单表格存在"技术债登记"行 | L117：`\| **技术债登记** \| 是/否/— \| ✅/❌/— \| 标记为"是"时，本列必须填写具体 DEBT 编号或 roadmap RM 编号，**不允许留空或写"待定"** \| \|` |
| 强制说明写在"未触发后果"列 | 同 L117，位于表格第 4 列（未触发后果列） |
| check-retrospective.py 不做内容语义解析 | 见下方脚本核实 |

## 脚本侧核实（不做内容语义解析）

`grep -n "待定" agate/scripts/check-retrospective.py` → **零命中**（脚本内不含"待定"这个
校验目标词，说明脚本没有针对模板"未触发后果"列具体文案做内容解析）。脚本确实引用了
`DEBT`/`roadmap` 关键词（`tech-debt.md`/`roadmap.md` 文件路径、`_scan_debt_roadmap_signal`
函数名），但这是 BDD-10 新增的**客观副产物检测**（`os.path.isfile` + 对 task_id 的正则匹配，
`_scan_debt_roadmap_signal`，L66-90），检测对象是"该 task_id 是否在 tech-debt.md/roadmap.md
里被登记"这一独立文件的存在性/命中性，不是解析复盘文档本身"未触发后果"列的文本内容（复盘
文档正文从未被 check-retrospective.py 读取或解析），两者是不同的信号源。脚本不新增任何阻断
逻辑（`main()` 末尾恒 `sys.exit(0)`，L152）。这与 BDD-4 Then 子句"check-retrospective.py 侧
不做内容语义解析"要求一致——脚本没有、也不需要检查复盘文档"未触发后果"列是否真的填了具体
编号，这件事完全交给人工撰写与审阅。

## 原文摘录

```
| **技术债登记** | 是/否/— | ✅/❌/— | 标记为"是"时，本列必须填写具体 DEBT 编号或 roadmap RM 编号，**不允许留空或写"待定"** | |
```

## 判定

**满足**——模板对"未触发后果"列做出显式强制说明（含"不允许留空或写'待定'"字样），且本轮
独立 grep 核实 check-retrospective.py 未对该列内容做任何语义解析，符合"只提醒不阻断"既有
边界，无新增阻断逻辑。
