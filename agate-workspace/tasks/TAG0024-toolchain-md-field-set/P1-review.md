---
phase: P1
task_id: TAG0024
type: review
parent: P1-requirements.md
trace_id: TAG0024-P1-review-rev2-20260825
status: approved
created: 2026-08-25
agent: requirements-review
---

# P1-review：P1-requirements.md 独立评审（TAG0024，复评第 2 轮）

本文件是**复评（第 2 轮）**，直接覆盖第 1 轮 P1-review.md。第 1 轮判定 `needs-revision`，唯一阻塞点：DEBT0020 缺一条与 BDD-21（DEBT0019 侧）对称的"既有合法场景（仓库根 CWD 正常调用路径）判定结果不变"回归锚点 BDD；另有一条不阻塞的记录项：BDD-28（旧编号）排除措辞可精确化（区分 `_check_roadmap_done()` 本体与调用点 `gate_p8()` 的 `roadmap_path` 定位行）。analyst 本轮修复：新增 BDD-24（对称锚点），原 BDD-24~28 顺延为 BDD-25~29，BDD-29（原 BDD-28）排除措辞已精确化。本轮复评方法：不采信 analyst 自述"已修复"，独立重新执行 grep/读正文逐字核对两处修复点，并抽查未改动 BDD 是否原样未动，过程见 P1-review-progress.md 复评部分。

## 编号完整性复算（独立核验，不采信声称）

`grep -oP "^#### BDD-\K[0-9]+"` 提取全部编号后用 Python 排序比对 `list(range(1,30))`：结果为 True，count=29，dupes=[]——**编号 1~29 连续、无跳号、无重复，独立核验通过**（未采信第 1 轮"28 条"或 analyst 自述"顺延至 29"的说法，本轮重新全量提取核对）。`check-frontmatter.py` 对最新 P1-requirements.md 执行 exit 0。

## 重点复核 1：BDD-24（DEBT0020 对称锚点，第 1 轮唯一阻塞点）

原文（P1-requirements.md 226-229 行）：

> #### BDD-24: 既有合法场景（仓库根 CWD）判定结果不变
> - Given 当前工作目录是仓库根（既有正常调用路径，含 TAG0023 P8 roadmap 回写校验覆盖的既有用例）
> - When 修复后的 `gate_p8()` 调用 `_check_roadmap_done()` 定位并解析 roadmap.md
> - Then 判定结果（阻断行为/rm_id/status）与修复前完全一致

逐项比对第 1 轮打回要求的结构要素——Given 仓库根既有正常调用路径（含 TAG0023 用例）/ When `gate_p8()`+`_check_roadmap_done()` 解析 roadmap.md / Then 判定结果（阻断行为/rm_id/status）与修复前完全一致：**三要素全部满足**，且与 BDD-21（DEBT0019 侧对称锚点：Given 列数精确匹配的既有合法表格含 TAG0023 用例 / When 修复后 `_check_roadmap_done()` 解析 / Then 判定结果与修复前完全一致）在结构、措辞模式（"与修复前完全一致"）、TAG0023 用例引用上完全对称，不再是"只覆盖新增边界场景、遗漏既有合法路径"的状态。插入位置在 BDD-23（仓库根不可得提示）之后、DEBT0020 小节末尾，属于该小节第三条 BDD，位置合理，未影响 DEBT0020 小节内既有两条 BDD（BDD-22/23）的独立性。

**核验结论：第 1 轮阻塞点已对症修复，通过。**

## 重点复核 2：BDD-29（原 BDD-28）排除措辞精确化

原文（P1-requirements.md 257-260 行）Then 子句：

> Then 除 `_check_roadmap_done()` 及其调用点 `gate_p8()` 中 `roadmap_path` 定位相关行外，两文件不含其他判定逻辑变更

对照第 1 轮记录项要求（措辞需区分 `_check_roadmap_done()` 函数体本身与其调用点 `gate_p8()` 内 `roadmap_path` 构造行这两个具体改动位置，避免 P7 一致性核对时对"是否算相关行"产生解释分歧）：新措辞已同时点名两个具体位置——函数本体 `_check_roadmap_done()`，以及调用点 `gate_p8()` 中的 `roadmap_path` 定位行——不再是第 1 轮"`_check_roadmap_done()` 相关行"这一可被宽泛解释、边界模糊的表述。

**核验结论：措辞精确化到位，记录项已随同修复。**

## 编号顺延交叉核对（BDD-25~29 内容是否随顺延被误改）

独立读取顺延后的 BDD-25（P4 outputs 声明补全）、BDD-26（S-1/S-2 双向一致性检查通过）、BDD-27（phases.yaml 与 state-machine.md 表述口径一致）、BDD-28（既有判定行为不变，覆盖 `check-gate.py`/`check-judge-verdict.py` 现有判定行为）：与第 1 轮 P1-review.md 中对原 BDD-24/25/26/27 的转述逐字对照，Given/When/Then 内容完全一致，仅编号从 24/25/26/27 顺延为 25/26/27/28，未见内容被误改或截断。小节归属（"### RM-AG0049：phases.yaml P4 outputs 声明对齐"、"### RM-AG0050：P6.5 定位口径统一"、"### 跨issue 约束验收"）与顺延前一致，无错位。

## 抽查：未改动 BDD 是否原样未动（≥5 条，dispatch-context 要求本轮不重新展开全部维度，只抽查）

逐条读取并与第 1 轮评审转述比对，以下均确认内容逐字一致、未被误改：

- BDD-1（合法 key/value 写入并可读回）：Given/When/Then 与第 1 轮记录一致
- BDD-5（`--list` 输出与阶段 schema 一致）：一致
- BDD-9（证据字段——`pass`/`fail`/`blocker_count` 等 10 个字段——一期拒绝写入）：字段枚举与第 1 轮一致
- BDD-15（set 校验与 `check-gate.py` 同源，RM-AG0048 同源铁律核心锚点）：一致，未被削弱
- BDD-17（白名单=`task_fields`∪通用 Header 完整并集）：一致
- BDD-20（DEBT0019 核心：描述列含字面 `|` 时不误判）：一致
- BDD-21（DEBT0019 对称锚点，本轮未改动）：一致，且与新增的 BDD-24 结构对称验证互相印证
- BDD-22 / BDD-23（DEBT0020 前两条：非仓库根 CWD 定位 / 仓库根不可得提示）：一致，未受新增 BDD-24 插入影响

抽查共 9 条（超过要求的 5 条），均确认原样未动。全文章节结构（`## 1. 需求复述` ~ `## 7. 待确认清单`，含 `## 3. 同类扫描` 三条线索、`## 4. BDD 验收条件` 下 5 个 issue 小节 + 跨 issue 约束小节）与 frontmatter（`risk_level: medium` / `ceremony: standard` / `phases` 全阶段不裁 / `packages` 四包 / `domains: [backend]`）经 `grep "^## \|^### "` 核对，与第 1 轮评审时的结构完全一致，无章节缺失、错位或字段被误改。

## 其余核验维度（第 1 轮已逐条核实通过，本轮未见改动，不重新展开）

隐含需求覆盖（数据/前端/多端/边界维度覆盖，兼容维度此前唯一缺口即 DEBT0020，已在本轮修复）、BDD 跨条一致性、裁剪合理性（P3/P6.5/P7/P8 不裁理由）、审声明核对（risk_level/ceremony/phases 声明与 P0-brief 改动面一致，暂存区为空属阶段性限制非缺陷）、P0-brief 时效性（已核对无漂移）、同类扫描三线索（get 白名单对齐/roadmap 消费点/P6.5 消费点，均已独立复算通过）、范围核验（BDD 与 5 项 issue 精确映射，无遗漏无蔓延）：以上维度第 1 轮均已逐条独立核实通过，analyst 本轮未改动其对应正文内容（章节结构核对已确认），故不重新展开核验，仅确认"原样未动"。

## 结论

`status: approved`——第 1 轮唯一阻塞点（DEBT0020 缺 BDD-21 对称锚点）已通过新增 BDD-24 对症修复，结构与 BDD-21 完全对称；记录项（BDD-28 旧编号排除措辞精度）已通过 BDD-29 措辞精确化一并处理；编号 1~29 独立复算连续无跳号无重复；编号顺延后 BDD-25~29 内容未被误改；抽查 9 条未改动 BDD（BDD-1/5/9/15/17/20/21/22/23）内容原样未动；全文章节结构与 frontmatter 未受影响。需求基线本轮复评通过，可推进 P2。
