---
review_date: 2026-08-20
reviewer: protocol-alignment-review
change_summary: TAG0007 P4 实现——为 agate 协议新增两个机制：RM-AG0008（0→1 项目骨架脚手架，project_phase: bootstrap → P2-skeleton.md）+ RM-AG0009（CODE-MAP 架构演进纪律，agents/CODE-MAP.md 存在性 + P4 新增文件核对表 + P7 pairing 校验），check-gate.py 在 gate_p2/gate_p4/gate_p7 三处新增判定分支。本文件为**复评版**：核实针对首轮 5 处 MISALIGNED 发现的追加式修复（implementer 纯追加 6 行，`git diff --stat` 确认：`agate/assets/templates/task-files.md` +2、`agate/phase-cards/P4-implementation.md` +1、`agate/phase-cards/P7-consistency.md` +1、`agate/scripts/README.md` +1、`agate/state-machine.md` +1）。
files_changed: [agate/assets/templates/task-files.md, agate/phase-cards/P4-implementation.md, agate/phase-cards/P7-consistency.md, agate/scripts/README.md, agate/state-machine.md]
---

# 协议-脚本对齐审查（复评）

审查对象：commit `1e9d74e` 之后 implementer 针对首轮审查（`docs/reviews/agate-alignment-review-2026-08-20-TAG0007.md` 首轮版本，A2/A3/A5 判 MISALIGNED）的 5 处追加式修复。本轮复评范围限定为 A2、A3（重点 A3b）、A5 三项及其共享的 5 条修复项；A1/A4/A6/A7 首轮已 ALIGNED 且本次改动未触及其判定逻辑，未重新展开全套复查，仅在过程中留意有无新引入问题（未发现）。

## 审查结论汇总（复评后最终结论）

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（首轮结论，未变） |
| A2 | 脚本→文档对齐 | **ALIGNED**（复评改判，原 MISALIGNED 已修复） |
| A3 | 一致性连锁 + 反向传播 | **ALIGNED**（复评改判，A3a 首轮已 ALIGNED，A3b 原 MISALIGNED 已修复） |
| A4 | 测试覆盖 | ALIGNED（首轮结论，未变；本轮独立重跑复核） |
| A5 | 下游影响 + 文档传播 | **ALIGNED**（复评改判，原 MISALIGNED 已修复） |
| A6 | 锚点表覆盖 | ALIGNED（首轮结论，未变） |
| A7 | 设计原则一致性 | ALIGNED（首轮结论，未变） |

**A1-A7 全部 ALIGNED，本轮 self-gate 通过。**

## 逐条修复核实

### 修复 1（对应首轮 A2 问题 1，高优先级）：P7-consistency.md「## gate 规则」小节补 CODE-MAP exit 1 说明

**改动**（`agate/phase-cards/P7-consistency.md` L89，新增一行，紧邻既有 L88 DESIGN_GAP 行之后）：
```
- CODE-MAP 未配对（code_map_reviewed_count < code_map_new_files_count，或 P4 实际标记数 > code_map_new_files_count）→ exit 1（两字段均缺失时机制未采用，跳过）
```

**脚本核对**（`agate/scripts/check-gate.py` L937-979，`gate_p7`）：
```python
cm_count_fm = _frontmatter_field(p7_file, "code_map_new_files_count")
cm_reviewed_fm = _frontmatter_field(p7_file, "code_map_reviewed_count")
if cm_count_fm != "" and cm_reviewed_fm != "":
    ...
    if cm_count is not None and cm_reviewed is not None and cm_reviewed < cm_count:
        ...
        return 1                              # 内部一致性层
    ...
    if p4_code_map_actual_count > cm_count:
        ...
        return 1                              # 转抄核对层
```
两个判定分支（内部一致性层 `cm_reviewed < cm_count`、转抄核对层 `P4 实际标记数 > cm_count`）与新增文档行逐字对应，均 `return 1`（exit 1）。

**次要观察（不构成 MISALIGNED）**：新增行括注「两字段均缺失时机制未采用，跳过」，字面指"两字段都缺失"才跳过；而代码实际跳过条件是 `cm_count_fm != "" and cm_reviewed_fm != ""` 为假，即**任一**字段缺失就整体跳过（不仅"两者都缺失"）。这是一个精确度层面的简化表述，非语义错误：① 该措辞与首轮审查报告"建议"栏原文完全一致（属于原建议自身的简化，而非实施方偏离建议）；② 现有模板（`task-files.md`/`P7-consistency.md` 的 frontmatter 样例）两字段总是成对出现、成对填 0，正常流程不会出现"只填一个"的中间态；③ 对照同一小节中既有 DESIGN_GAP 一行（L88）也未在快速参考表里展开"新旧格式回退"的实现细节，风格一致。判定为可接受的简化陈述，不影响"是否会 exit 1"这一读者最关心的判断，不追加为新 MISALIGNED 项。

**核实结论：修复到位，措辞准确对应判定逻辑。**

### 修复 2（对应首轮 A3b 问题 3，高优先级）：task-files.md P7 frontmatter 样例补两个新字段

**改动**（`agate/assets/templates/task-files.md` L436-437）：
```yaml
code_map_new_files_count: 0        # int ≥0（可选，仅骨架/CODE-MAP 机制已采用时填）
code_map_reviewed_count: 0         # int ≥0（可选，语义对应 design_gap_reviewed_count）
```

**核对**：与 `agate/phase-cards/P7-consistency.md` L75-76 逐字节比对（含字段名、默认值、行内注释文案、对齐空格），**完全一致**，两处"可直接复制"样例块恢复同步。

**核实结论：修复到位，逐字同步，问题 3 闭环。**

### 修复 3（对应首轮 A3b 问题 4，中优先级）：scripts/README.md check-gate.py 工具清单补续行

**改动**（`agate/scripts/README.md` L34，紧接既有 L33「check-gate.py（续）」行之后）：
```
| `check-gate.py`（再续） | gate_p2 新增 project_phase:bootstrap → P2-skeleton.md 存在性校验；gate_p4 新增 骨架/CODE-MAP 机制已采用时缺「新增文件核对表」WARNING；gate_p7 新增 CODE-MAP 两层 pairing 硬校验 | |
```

**核对**：三处描述分别对应 `check-gate.py` 中的
- `gate_p2` L637-645（`project_phase == "bootstrap"` → `P2-skeleton.md` 存在性 + 标题校验）
- `gate_p4` L698-716（骨架/CODE-MAP 任一存在 → 缺「## 新增文件核对表」标题时 WARNING，`return 0` 不阻断）
- `gate_p7` L937-979（CODE-MAP 两层 pairing，见修复 1）

三处描述与代码行为逐一对应，且沿用了 TAG0006 先例的「（续）」行格式（本次为「（再续）」，与既有表格风格一致，未破坏表格结构）。

**核实结论：修复到位，问题 4 闭环。**

### 修复 4（对应首轮 A3b 问题 5，中优先级）：state-machine.md P2 转移条件块补括注

**改动**（`agate/state-machine.md` L100，插入在既有 L99「ui_affected」括注行和 L101「vision 三态约束」括注行之间）：
```
（project_phase: bootstrap 时 P2-design.md 之外还须产出 P2-skeleton.md 含「## 骨架声明」标题，P2 gate 拦截缺失，见 phase-cards/P2-design.md「骨架产出」节）
```

**核对**：
- 与 `agate/phase-cards/P2-design.md` L84-90「骨架产出」小节比对：字段名 `project_phase: bootstrap`、产出文件名 `P2-skeleton.md`、必含标题 `## 骨架声明`、"P2 gate 校验"性质，均逐字对应。
- 与 `check-gate.py` L637-645（`gate_p2` 新增分支）比对：`project_phase == "bootstrap"` 分支下 `os.path.isfile(skeleton_file) and "## 骨架声明" in text` 的判定逻辑，与"拦截缺失"的表述一致。
- 引用路径「见 phase-cards/P2-design.md「骨架产出」节」指向正确（该小节标题以粗体 `**骨架产出（...）：**` 形式存在，非严格 markdown heading，但与 state-machine.md 中既有的「UI 设计节」引用风格一致，可定位）。

**核实结论：修复到位，问题 5 闭环。**

### 修复 5（对应首轮 A2 问题 2，低优先级）：P4-implementation.md「## gate 规则」小节补 WARNING 说明

**改动**（`agate/phase-cards/P4-implementation.md` L147，紧接既有 L145-146 exit 0/exit 1 两行之后）：
```
- WARNING（不改变 exit code）：骨架/CODE-MAP 机制已采用（P2-skeleton.md 或 agents/CODE-MAP.md 存在）但缺「新增文件核对表」标题
```

**脚本核对**（`check-gate.py` L698-716，`gate_p4`）：
```python
skeleton_file = os.path.join(task_dir, "P2-skeleton.md")
code_map_file = os.path.join(..., "agents", "CODE-MAP.md")
if os.path.isfile(skeleton_file) or os.path.isfile(code_map_file):
    if "## 新增文件核对表" not in _read_text(p4_impl_check):
        sys.stderr.write("GATE P4 WARNING: 骨架/CODE-MAP 机制已采用，但 P4-implementation.md 缺少「## 新增文件核对表」标题（不阻断，请补充）\n")
        # 不 return，继续往下，最终仍 return 0
```
OR 条件、"不改变 exit code"（WARNING 不 return 1）、触发条件（缺「新增文件核对表」标题）三点均与新增文档行逐字对应。

**核实结论：修复到位，问题 2 闭环。**

## A2/A3b/A5 复评结论

- **A2（脚本→文档对齐）**：首轮两处问题（P7「gate 规则」漏 CODE-MAP exit 1、P4「gate 规则」漏 WARNING）均已修复（修复 1、修复 5），措辞与脚本判定逻辑一致。**改判 ALIGNED**。
- **A3（一致性连锁 + 反向传播）**：A3a 首轮已 ALIGNED，未受影响。A3b 三处问题（task-files.md 样例漏字段、scripts/README.md 漏续行、state-machine.md 漏括注）均已修复（修复 2/3/4）。**改判 ALIGNED**。
- **A5（下游影响 + 文档传播）**：下游影响本身首轮已确认 ALIGNED（无破坏性变更，字段缺失即完全跳过的回归对照测试已覆盖）；文档传播部分与 A3b 共享同一组问题，现已闭环。**改判 ALIGNED**。

本轮复评过程中未发现 implementer 修复引入的新增偏离；5 处改动均为纯追加（无删除/改写既有内容），`git diff --stat` 复核为 6 处 insertion（`task-files.md` 2 行 + 其余 4 个文件各 1 行），与交接单描述一致。

## A4 独立复核（本轮重新实跑，非仅引用）

```
timeout 180 python3 -m pytest agate/tests/ -q --tb=line
...
1028 passed, 2 skipped in 101.23s (0:01:41)
```
与主 Agent commit 声称及首轮审查记录的数字一致，独立复核通过。

## check-protocol-consistency.py 独立复核

```
timeout 60 python3 agate/scripts/check-protocol-consistency.py
...
仅有 316 个 WARNING，无 ERROR。
```
0 ERROR，316 条 WARNING 均为既存的叙事文件旧引用（如 `docs/reviews/postmortem-template.md`、已归档脚本名等），与本次 5 处修复无关，非新增。

## 结论

首轮发现的 5 处 MISALIGNED 均已修复到位，内容准确对应脚本判定逻辑，无删除/改写既有内容的副作用，无新引入的偏离。**A1-A7 全部 ALIGNED，本轮 self-gate 通过，可 commit。**
