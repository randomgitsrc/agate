---
phase: P1
task_id: TAG0012-protocol-mechanism-fixes
type: gate-diagnosis
created: 2026-08-18
---

# P1 gate 诊断

## 失败现象

`python3 ~/.agate/scripts/check-gate.py P1 agate-workspace/tasks/TAG0012-protocol-mechanism-fixes`
exit 1：

```
GATE P1: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM]、[SUGGEST: ...] 或 [NO_NEED_CONFIRM] 声明）
```

## 根因分析

`check-gate.py` L491-492 的检测逻辑：字符串 `"[NEED_CONFIRM]"` 出现在全文中（子串匹配，非行首），
但行首正则 `_NC_RE`（`^\s*`*-?\s*`*\[NEED_CONFIRM\]`）匹配数 `nc_blocking == 0` → 判定为"格式不合规"。

命中位置：`P1-requirements.md` 第 243 行（第 4 节「待确认清单」正文）：

> 无阻塞性 `` `[NEED_CONFIRM]` ``。第 2 节列出的 1 条 `` `[SUGGEST:]` ``（同类扫描机制不追溯历史产出）方向明确……

这里 `[NEED_CONFIRM]` 是**行中散文引用**（说明"没有这类项"），不是行首标记声明。第 241 行的
`` `[NO_NEED_CONFIRM]` `` 才是真正的行首声明，格式正确（gate 的行首正则允许反引号前缀，能正确
识别）。问题只在第 243 行的散文提及触发了子串误判。

## 目标阶段

不退回上游，本阶段（P1）内小修——只需 analyst 微调第 243 行措辞，不产出 `[NEED_CONFIRM]` 这一
字面子串（用"待确认清单为空"或类似表述替代），不改变 BDD/frontmatter/裁剪结论等任何实质内容。

## 诊断依据

- `check-gate.py` L48-58（正则定义）+ L491-492（子串误判触发点），已用 grep/Read 核实源码逻辑。
- `P1-requirements.md` L241/L243 已用 grep 定位到两处具体行号。
- P1-review.md（status: approved）未涉及第 4 节措辞，approved 结论不受本次微调影响（不改变 BDD
  判定语义，无需重新走 requirements-review 全流程；仅需主 Agent 复跑 check-gate.py 确认转绿）。
