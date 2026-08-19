# BDD-7 证据：「## agate 反馈」结构化节（AG0021 依赖）

文件：`agate/assets/templates/retrospective-template.md`

## Then 子句逐项核对

Then 要求：文档含标题为「## agate 反馈」的独立小节，模板对该节的内容边界做出显式声明
（只列出归因到 agate 机制/执行层面的条目，不涉及项目敏感信息）。

| 要求 | 实际（行号） |
|------|-------------|
| 标题「## agate 反馈」 | L147 `## agate 反馈` |
| 内容边界声明——只列出归因到 agate 机制/执行层面的条目 | L149 `> 当 `feedback_ready: true` 时填写本节：只列出归因到 agate 机制/执行层面的条目，` |
| 内容边界声明——不涉及项目敏感信息 | L149-151 `> 不涉及项目敏感信息（项目名/绝对路径等由 `agate-feedback.py` 做进一步脱敏，\n> 但撰写时本身也应避免带入项目特定信息）。` |
| 触发条件（`feedback_ready: true`） | L149 显式与 BDD-6 的 `feedback_ready` 字段挂钩 |

## 原文摘录

```
## agate 反馈

> 当 `feedback_ready: true` 时填写本节：只列出归因到 agate 机制/执行层面的条目，
> 不涉及项目敏感信息（项目名/绝对路径等由 `agate-feedback.py` 做进一步脱敏，
> 但撰写时本身也应避免带入项目特定信息）。

（填写：归因到 agate 机制/执行层面、值得反馈给 agate 项目组的条目）
```

## 与 BDD-17/18 的联动核实

该节文本被 `agate-feedback.py` 的 `_extract_agate_feedback_section` 用标题正则
`^## agate 反馈\s*$` 定位提取（见 `P6-evidence/bdd-17-extraction.md`/`bdd-18-anonymize.md`
的独立实跑证据），标题字符串与本模板逐字一致，非悬空定义。

## 判定

**满足**——标题、内容边界声明（含"只列出归因到 agate 机制/执行层面的条目"与"不涉及项目
敏感信息"两句）均在模板文件本身存在，本轮独立跑 agate-feedback.py 已验证该节确实能被脚本
正确定位提取（见 BDD-17/18 证据），标题字符串跨文件一致。
