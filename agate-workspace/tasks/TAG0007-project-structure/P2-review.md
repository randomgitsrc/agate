---
phase: P2
task_id: TAG0007
type: review
parent: P2-design.md
trace_id: TAG0007-P2-review-20260820
status: approved
created: 2026-08-20
agent: plan-eng-review
---

## 复评：3 处修复核实

1. **阻塞项（gate_p7 两层校验 + 字段对应关系）：已修复，核实到位**。
   独立重读 `agate/scripts/check-gate.py` `gate_p7` 源码（`timeout 60s sed -n '780,910p'` +
   `timeout 60s grep -n`），精确定位：内部一致性判定在 **L844**
   `if dg_count is not None and dg_reviewed is not None and dg_reviewed < dg_count`，其中
   `dg_count` 取自 **L838** `_md_field_get("design_gap_count", p7_file)`、`dg_reviewed` 取自
   **L839** `_md_field_get("design_gap_reviewed_count", p7_file)`；转抄交叉核对判定在 **L889**
   `if p4_design_gap_count > dg_count`——比较对象同样是 `dg_count`（即 `design_gap_count`），**不是**
   `dg_reviewed`（`design_gap_reviewed_count`）。这是上轮问题的核心：字段对应关系一旦颠倒，
   `code_map_new_files_count` 就会失去被引用的判定位置。

   当前 P2-design.md 三处对应位置逐字核对：
   - §1.1（L62，gate_p7 行）：「① 内部一致性——`code_map_reviewed_count < code_map_new_files_count`
     → exit 1（对应现有 `dg_reviewed < dg_count` 分支，L840-848）；② 转抄核对——…实际计数 >
     P7 的 `code_map_new_files_count`（**不是** `code_map_reviewed_count`）→ exit 1（对应现有
     `p4_design_gap_count > dg_count` 分支，L873-893）」——字段对应关系正确：
     `code_map_new_files_count` 对齐 `design_gap_count`（两层判定中均作为"总数/上限"一侧），
     `code_map_reviewed_count` 对齐 `design_gap_reviewed_count`（均作为"已核实数"一侧），两层
     判定都比较的是 `_new_files_count`（对应 `dg_count`），不是 `_reviewed_count`。行号引用
     `L840-848`/`L873-893` 与本轮独立核实的精确行号 `L844`/`L889` 落在其声明区间内，无偏差。
   - §2.3（L175-178）：候选 A 描述与 §1.1 一致，同样是两层、同样字段对应关系正确。
   - §5 minimal_validation 第 1 条（L269-272）：`method` 字段逐行核实了 DESIGN_GAP 真实两层
     结构（明确写出 L840-848 内部一致性 / L873-893 转抄核对，转抄核对比较对象点名"不是
     reviewed_count"），并给出 `code_map_new_files_count` 对应 `design_gap_count`、
     `code_map_reviewed_count` 对应 `design_gap_reviewed_count` 的明确映射；`result: confirmed`
     的 `note` 如实交代修复过程——"初版方案曾将两层结构误简化为单层描述（P4 实际计数直接比
     reviewed_count，且新增的 code_map_new_files_count 字段未被任何判定分支引用），已在本轮
     修复轮核实源码并修正为完整两层结构、字段对应关系归位"——这不是换个说法掩盖问题，而是
     准确复述了上轮 review 指出的具体缺陷并说明已解决，如实反映修复情况。
   - `code_map_new_files_count` 字段不再是"声明但未使用"：在两层判定（内部一致性的比较对象、
     转抄核对的比较对象）中均被实际引用，语义位置与源码 `design_gap_count` 完全对应。
   判定：**字段对应关系无颠倒，两层结构完整，阻塞项已实质修复，非表面修复**。

2. **非阻塞项 1（CHANGELOG 类比措辞）：已修复**。
   §1.2「不改什么」（L80）与 §1.3 R5（L91）均已改写为"比照 `CHANGELOG.md [Unreleased]` 处理方式，
   但需承认 CODE-MAP.md 按设计含模块/层/依赖方向等**结构化字段**，多方并发改写同一条目更接近
   '同一行被两方各自改写'而非纯追加，git 无法自动合并，实际解决成本高于 CHANGELOG 追加冲突"——
   与上轮建议的改写方向一致，不再暗示两者冲突形态类似，诚实标注了差异。

3. **非阻塞项 2（§7 markup 表述）：已修复**。
   §7（L337-343）已从"已完整声明五字段标题名与格式要求"改写为"本 P2-design.md 已声明五字段
   **名称**（见 §1.1、§3），具体标题的 markdown markup 形式（`##` 二级标题 / `###` 三级标题 /
   加粗文本等）由各批次自行决定，不强制两批次产出的 markup 完全一致"，并显式补充"两批次标题
   markup 是否一致目前无回归测试覆盖，属已知测试缺口"——表述与实际已声明信息量相符，且诚实
   标注了测试缺口，不再夸大。

## 其余部分维持上轮判定

决策组1/2/4、BDD-4/7 累加设计、BDD-10 落地、多方案探索诚实度、gate_commands、dispatch_plan
拆批不相交性：维持上轮方向确认/合规判定，本轮 dispatch-context 明确圈定只需复核上述 3 处，
且核对 P2-design.md 全文未见这些部分有变更，无需重新展开。

## 结论

**approved**。上一轮指出的 1 个阻塞项（gate_p7 pairing 两层结构 + 字段对应关系颠倒）已通过
独立重读源码（精确定位 L838/L839/L844/L889）核实为真实修复，`code_map_new_files_count`/
`code_map_reviewed_count` 与 `design_gap_count`/`design_gap_reviewed_count` 的对应关系正确、
两层判定逻辑完整，非"换个说法但字段对应关系仍颠倒"式的表面修复。2 个非阻塞措辞建议（CHANGELOG
类比精确度、§7 markup 表述精确度）均已按建议方向改写到位。其余 7 项已判定方向确认/合规的核查点
本轮未见改动，维持上轮判定。可进入 P3。
