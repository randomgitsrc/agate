---
review_date: 2026-09-02
reviewer: independent-design-review-v3
review_target: docs/design-notes/design-orchestration-semantics.md（设计讨论 v3a，208 行，待立项候选 RM-AG0049）
change_summary: 对 design-orchestration-semantics.md v3a 的独立复审——逐条验证两轮评审（2026-09-01 v1 评审 + 2026-09-02 Claude v2 独立评审）全部发现是否在 v3 中闭合，逐条对照仓库权威源核验证据，检查采纳的 4 条补充想法是否方式正确，并排查 v3 是否引入新问题
files_reviewed: [docs/design-notes/design-orchestration-semantics.md (v3a，审查时点 12:5x), docs/reviews/review-design-orchestration-semantics-2026-09-01.md, docs/reviews/review-orchestration-semantics-v2-independent-20260902.md, agate/dispatch-protocol.md, agate/state-machine.md, agate/loop-orchestration.md, agate/rules/phases.yaml, agate/rules/state-transitions.md, agate/scripts/check-gate.py, agate/scripts/check-state-transition.py, agate/scripts/check-structure-consistency.py, agate/scripts/agate-next-card.py, agate/scripts/agate-retreat-to.py, agate/WORKFLOW.md, docs/design-notes/README.md]
---

# 编排语义统一设计 v3（design-orchestration-semantics）独立复审

审查对象：`docs/design-notes/design-orchestration-semantics.md` **v3a**（208 行，N-New1~4 修复前版本）。

> ⚠️ **审查版本与时间线（可追溯性标注，2026-09-02 补充）**：本复审读取的是 **v3a**（此时文档"裁剪跳变"示例确为"P2→P4 / P5→P8 / P7→DONE"、exit 三态表动作列确无 P6 例外——见下文 N-New1/N-New4 引用的原文）。本文件于 **12:55:11 落盘**；N-New1~4 的修复由作者在复审落盘**之后**应用（设计文档 12:59:30 修改，v3a → v3b），修复位置见第 6 节"修复闭环确认"。因此：本文件引用的行号与文本均为 v3a 快照；最终发布的设计文档为 v3b（行号与内容已变）。本标注为回应第三轮 Claude 元评审（`review-orchestration-semantics-v3-claude-meta-20260902.md`）指出的"评审链时间线在快照内不可见"缺陷而补——详见该存档文件第二节时间线核验。

本轮复审与前两轮的关键区别：**结论落盘**——本文件即 v3 的独立复审证据，同时构成第二轮 B1'（"PASS 标签无复审证据"）所要求的"真正针对新版内容的独立复核"。

核验方法：v3 中每一处对权威源的引用（行号），均回到仓库对应文件实际读取核对；README 登记状态用 grep 实际核验；脚本契约（check-gate.py exit 三态、check-state-transition.py 拦截项、check-structure-consistency.py S-1/S-2）以脚本 docstring 与代码为准。

---

## 结论汇总

| 编号 | 问题（原评审）| 修复状态 |
|------|-------------|---------|
| B1 | 4.1/5 节"dispatch-protocol 五模式"内容误述 | ✅ 已修复 |
| B2 | 第 5 节资产清单不完整 + Phase 1 重复造轮子 | ✅ 已修复 |
| W1 | "流程层 100% 可程序化"过度简化 | ✅ 已修复 |
| W2 | "gate 失败 → 回当前 phase"与既有回退语义不符 | ✅ 已修复 |
| W3 | 4.3 三条护栏可执行性不足且自相矛盾 | ✅ 已修复 |
| W4 | gate exit code 建模忽略 exit 2 语义 | ✅ 已修复 |
| N1 | P6.5 非独立 phase 值未提 | ✅ 已修复 |
| N2 | design-notes/README.md 未登记 | ✅ 已修复 |
| N3 | 外部链接 issue #20849 推断略超前 | ✅ 已修复 |
| N4 | agate-next-card.py 用途描述不精确 | ✅ 已修复 |
| B1' | 条目"PASS"标签无复审证据 | ✅ 已修复（本次复审即修复动作）|
| W1' | 护栏范围遗漏 WORKFLOW.md「已知适用环境」表 | ✅ 已修复 |
| W2' | 护栏机械化仍是未来时 | ✅ 已修复 |
| N1' | 平台语义表与语义叙述排版未分离 | ✅ 已修复 |
| N2' | README 登记状态待核验 | ✅ 已修复（grep 实核）|

两轮评审共 15 项发现（v1：2 BLOCKER + 4 WARNING + 4 NIT；v2：1 BLOCKER + 2 WARNING + 2 NIT）**全部闭合**，无遗留 BLOCKER/WARNING。4 条补充设计想法全部采纳，采纳方式正确（含 2 处落地细节 NIT，见下）。v3 新引入/新观察到 4 个 NIT 级问题，无新 BLOCKER/WARNING。

---

## 1. 第一轮（v1，2026-09-01）逐条修复核验

| # | 修复状态 | 一句话证据（v3 位置 ↔ 权威源）|
|---|---------|------------------------------|
| B1 | ✅ 已修复 | v3 4.1 五模式表（82-87 行）= 单发/静态拆批/并行/先理解后拆/串行链，与 `dispatch-protocol.md:513-519` 逐项一致；89 行明示"统一锚点必须是**协议侧**的 dispatch-protocol 五模式"，DSH 工具降为 4.2 的实现——v1 所指"张冠李戴"不复存在 |
| B2 | ✅ 已修复 | 37 行现状盘点补列 `state-machine.md` / `loop-orchestration.md` / `check-state-transition.py` / `agate-retreat-*.py` / `rules/` 结构化层；5 节资产表（159-168 行）列全九项且逐项核验属实；172-173 行缺口收敛为两点（`phases.yaml` 无 next/retreat 字段 ✅ 实读确认；无 `agate next`/`agate advance` ✅ `scripts/` 实列确认）；181 行 Phase 1 改为"扩展 phases.yaml 增 next/retreat"，不再新建 schema |
| W1 | ✅ 已修复 | 61 行"100% 可程序化"改为"**主线推进 + 单步回退**可程序化"；63-69 行五类非确定性成分显式建模为暂停点，行号引用逐一复核：PAUSED 汇合 ↔ `state-machine.md:95-99（PAUSED 边）/254-263（恢复协议）`、跨阶段回退 ↔ `132-133（P5→P4）/148（P6→P4）` + diff≥2 由 `check-state-transition.py` P2.5 机械拦截、裁剪跳变 ↔ `218-224`、SCOPE+ 定向回补 ↔ `233-241`（"判断影响范围依赖主 Agent 临场判断，无明确决策规则"原文一致）、P6.5 judge ↔ `WORKFLOW.md:310`（grep 定位精确命中）|
| W2 | ✅ 已修复 | 202 行回退目标照抄 `state-machine.md`：P1/P2 review rejected → 回自身（↔ 94/102 行）、P5/P6 gate 失败 → 回 P4（↔ 132-133/148 行）、P6.5 needs-revision → 回 P6 重验且 judge 轮次 ≤2（↔ 156-157 行）、回退 diff≥2 → 强制 PAUSED + 人工批准（↔ `check-state-transition.py` P2.5，转移表与脚本不搞双套判定）；"回当前 phase"的错误表述已删除 |
| W3 | ✅ 已修复 | 4.3 护栏 2（136 行）明确 `platform-notes.md`/`SETUP.md`/`WORKFLOW.md`「已知适用环境」表**整文件/整表**归入"如何实现"豁免；护栏 1 与 4.2 表矛盾通过「实现注记」标记 + 语义/实现排版分离消除（见 N1'）；护栏无判据问题以结构性判据（135 行）+ 机械化排期（139 行）回应 |
| W4 | ✅ 已修复 | 111-119 行 exit code 建模为三态（0 直推 / 1 回退 / 2 暂停转主 Agent），语义引 `check-gate.py:6-7` 与实际 docstring（"exit 0 = 通过; exit 1 = 未通过; exit 2 = 需主 Agent 自判"）逐字一致；示例 P5/P8 exit 2 与脚本 return 2 分支相符（P8 分支 stderr 原文："仍需主 Agent：① 从 P2 gate_commands 逐包读取发布检查命令……"，1376 行附近）|
| N1 | ✅ 已修复 | 203 行"P6.5 是挂载于 P6→P7 转移上的强门槛子阶段，非独立 phase 值（state-machine.md:74-78）——schema 用'子阶段门槛'表达，.state.yaml 的 phase 保持 P6 直至 P7"，与 `state-machine.md:74-78/152` 及 `check-gate.py gate_p65` docstring 一致 |
| N2 | ✅ 已修复 | `docs/design-notes/README.md:26` 已登记本笔记（grep 实际命中），条目含"设计讨论 v3（候选 RM-AG0049；评审链：v1 FAIL→v2 修复→2026-09-02 独立评审 FAIL→v3 修复待复审）" |
| N3 | ✅ 已修复 | 153 行"注意：单一 issue 不代表官方路线图，表述到此为止"——措辞降级为"平台层有向该方向演进的社区提案"，v1 所指"推断略超前"已收敛 |
| N4 | ✅ 已修复 | 166 行"按 PHASE 参数输出阶段卡片全文（sha256 校验契约 + M3 从 phases.yaml 渲染可判定节）\| 不承担'选下一张'逻辑"，与 `agate-next-card.py` docstring（"M3 渲染化：裸模板卡片从 YAML 渲染" + sha256 校验契约）一致 |

## 2. 第二轮（v2，2026-09-02 Claude 独立评审）逐条修复核验

| # | 修复状态 | 一句话证据（v3 位置 ↔ 权威源）|
|---|---------|------------------------------|
| B1' | ✅ 已修复 | v3 头部 3-4 行评审链**如实叙述**（"2026-09-02 经 Claude 独立评审指出'PASS 标签无复审证据'（B1'）→ 本版 v3 修复上述全部发现"），全文无任何自贴"独立评审 PASS"标签；README.md:26 状态为"v3 修复待复审"；B1' 要求的"真正针对新版内容的独立复审"即本文件——评审链从"自评"闭环为"证据驱动" |
| W1' | ✅ 已修复 | 136 行护栏 2 明确 `WORKFLOW.md:143-148`「已知适用环境」表与 `platform-notes.md` **同类豁免**（"整文件/整表视为'如何实现'……是元信息而非编排语义"）；143-148 行号引用实测命中（143 行表头、145-148 行四平台行）；v2 所指"未分类的边界情况"不再存在 |
| W2' | ✅ 已修复 | 139 行机械化排期明确："三护栏目前是文档写作纪律……机械化是**随 RM-AG0049 一起排期的方向**（不做则遗留'协议一致性靠评审员把关'的残留点，与本笔记 4.2 对 exit 2 分支的诚实态度一致，不假装消除）"；207 行风险表重申"随 RM-AG0049 排期"——由"未来时"变为"已排期的未来时 + 显式残留点"，v2 建议二选一的表达已落实为"排期 + 诚实承认" |
| N1' | ✅ 已修复 | 平台语义映射表移入 4.2（125-131 行），前置「实现注记」标记行（123 行）；4.1 为纯语义（五模式表 + 编排心智），不再与实现表同节；131 行明示"该表带「实现注记」标记……与协议语义叙述（4.1 五模式表）排版分离" |
| N2' | ✅ 已修复 | README.md:26 条目存在（本轮实际 grep 核验，非文档自述）——登记状态由"待核验"销项 |

## 3. 补充想法采纳核验（v2 评审「超出评分范围的补充设计想法」）

| 想法 | 采纳状态 | 证据（v3 位置 ↔ 想法原文）|
|------|---------|--------------------------|
| 1. exit 2 的"下一动作"建模为可机械复核的子状态 + 落盘留痕 | ✅ 采纳且方式正确 | 121 行"exit 2 的'下一动作'建模为可机械复核的子状态，而非自由文本占位。要求 exit 2 分支的解决必须落盘一个机器可读产物（如 `exit2-resolution.md` 或 `.state.yaml` 字段……），纳入 P6.5 judge 或 provenance 审计的复核范围"——与想法 1 原文（子状态 + exit2-resolution/state 字段 + 审计留痕）逐点对应；187 行 Phase 2 与 204 行风险表回环衔接 |
| 2. 状态机 CLI 是 /loop 档位 C 的可观测层（非机械替身），补 BDD 验收 | ✅ 采纳且方式正确 | 174 行"CLI 是档位 C 的**可观测层**……消除档位 C 里唯一一处完全依赖模型自律的环节"，并补 BDD 方向："档位 C 全程使用 `agate next` 推进，主 Agent 从未自行判断是否进入下一 phase"——与想法 2 原文一致；162/208 行衔接论证；前提事实（档位 C 由主 Agent 驱动循环）与 `loop-orchestration.md` 执行逻辑（主 Agent 逐轮读状态→执行单步）相符 |
| 3. 转移表字段纳入既有 S-1/S-2 双向一致性 gate，不新开检查 | ✅ 采纳且方式基本正确 | 183-185 行"新增字段直接纳入既有 S-1/S-2 双向一致性 gate 的检查范围（check-structure-consistency.py），防止'结构化数据面（phases.yaml）'与'人类可读权威源'日后漂移——**不新开独立一致性检查**"——机制与想法 3 原文一致；S-1/S-2 实存（`check-structure-consistency.py:7-11`：S-1 YAML→md、S-2 md→YAML，锚点为 phases.yaml ↔ WORKFLOW.md 阶段总览表）；落地细节 NIT 见 N-New3 |
| 4. 护栏 1 从"文件名单"改为"数据面 vs 叙述面"结构性判据 + 「实现注记」格式约定 | ✅ 采纳且方式正确 | 135 行结构性判据完整落地："凡 `rules/*.yaml` 等机器可读数据面，禁止出现平台名；凡 markdown 叙述文档，允许出现平台名，但**仅限带「实现注记」标记的小节/表格**（统一格式约定：`> 实现注记：` 标记行）……扫描'markdown 里不含实现注记标记、但含平台名的段落'——新增任何权威文档都自动被覆盖"；139 行落 scan 形态（check-protocol-consistency.py）；文档自身在 4.2 示范该标记；文档自身示范不完整见 N-New2 |

## 4. 新引入 / 新观察到的问题

以下为 v3 中本次复审新观察到的轻微问题，均为 NIT 级，不影响核心论证，**不构成 WARNING/BLOCKER**。

| # | 级别 | 问题 | 证据 |
|---|------|------|------|
| N-New1 | NIT | 63-67 行非确定性成分表"裁剪跳变"示例"P2→P4 / **P5→P8** / P7→DONE"中，`P5→P8` 不是 `state-machine.md:218-224` 的既有跳边（grep 全仓无 `P5->P8` 表述；实际边：跳过 P6 → P5→P7（222 行）、跳过 P7 → P6→P8（223 行））；P2→P4（220 行，跳过 P3）与 P7→DONE（224 行，跳过 P8）两例准确，机制结论（跳边由 P1 裁剪声明驱动 + 主 Agent 确认）与引用范围均正确，仅示例不精确 | v3 67 行 ↔ `state-machine.md:218-224` |
| N-New2 | NIT | 4.2「实现注记」标记行（123 行）声明"平台差异**只在本标记之后的表格出现**"，但后文 4.4 节（146-153 行）含 DSH/OpenCode/Claude 平台名（渲染层示例 + issue #20849）且未挂「实现注记」标记——按 v3 自己 4.3 结构性判据的字面扫描会命中该段；设计笔记若不在 CI 扫描范围（扫描对象为权威文档）则无实际后果，但格式约定的自我示范不完整，建议 4.4 补标记或明示设计笔记不适用该判据 | v3 123 行 ↔ v3 146-153 行 |
| N-New3 | NIT | 想法 3 采纳（183 行）的防漂移对象写"防止'结构化数据面（phases.yaml）'与'人类可读权威源（state-machine.md）'日后漂移"，但既有 S-1/S-2 的 md 侧锚点是 **WORKFLOW.md 阶段总览表**（`check-structure-consistency.py:7-11` 只比对 id/name/exec_role 与表行），state-machine.md 的转移语义不在其对照面——落地时新增 next/retreat 字段的 md 侧对照面（state-machine.md 转移规则 / rules/state-transitions.md）需要明确扩展方式，v3 未指明（机制复用本身正确，"不新开独立检查"符合想法 3 原意） | v3 183-185 行 ↔ `check-structure-consistency.py:7-11` |
| N-New4 | NIT | 113-117 行 exit 三态表"exit 2 → **暂停转主 Agent**"的泛化措辞未覆盖 P6 特例——P6 exit 2（FAIL=0/证据非空 AND check-p6-provenance exit 0）实际**前进**到 P6.5 judge 复核（`state-machine.md:139`），非停等主 Agent；表中 P5/P8 两示例准确，三态建模正确（check-gate.py:6-7 语义核验一致），仅"动作"列的泛化表述不完整，建议补"P6 exit 2 → P6.5 judge 复核"之例 | v3 113-119 行 ↔ `state-machine.md:139`、`check-gate.py:6-7` |

另注（并入 W1' 证据，不单列）：136 行把 `WORKFLOW.md:143-148` 表定性为"这份文档在哪些平台**验证过**"——实际表内容为"agate 在哪些平台具备完整执行前提"（task 工具/本地环境/agate 完整度，143-148 行）；归为"元信息而非编排语义"从而豁免的**结论正确**，仅描述措辞略松。

## 4.5 修复闭环确认（作者于复审落盘后应用，2026-09-02 12:56-12:59）

> 本节为可追溯性补充（回应第三轮 Claude 元评审指出的"快照内无法区分复审时状态与修复后状态"缺陷）：以下为 v3a → v3b 的修复闭环，读者无需仓库访问即可在快照内核对"发现 → 修复"一一对应。

| 复审发现（v3a 文本引用）| 修复后位置（v3b）| 修复内容 |
|------------------------|-----------------|---------|
| N-New1：v3a 63-67 行"裁剪跳变"示例"P2→P4 / **P5→P8** / P7→DONE" | v3b 67 行 | 改为"P2→P4 / **P5→P7 / P6→P8** / P7→DONE"（对齐 state-machine.md:218-224 实际跳边，附"跳过无 TDD/无验收/无一致性/无发布阶段"注）|
| N-New2：v3a 4.2「实现注记」声明"平台差异只在本标记之后的表格出现"与 4.4 平台名段落未挂标记 | v3b 125 行 + 143 行 | 声明改准为"平台名只出现在挂此标记的小节/段落"；4.4 节标题补"v3 修正 N-New2：补实现注记"，正文前置 `> 实现注记：` 标记行 |
| N-New3：v3a 183 行防漂移对象写"与 state-machine.md"，未指明 S-1/S-2 md 侧锚点 | v3b 188 行 | 明确"S-1 YAML→md 以 WORKFLOW.md 阶段总览表为 md 侧锚点（check-structure-consistency.py:7-11）" |
| N-New4：v3a 113-117 行 exit 三态表"exit 2 → 暂停转主 Agent"未覆盖 P6 特例 | v3b 117-119 行 | 动作列补"**P6 例外**：P6 exit 2 → 前进 P6.5（judge 复核，state-machine.md:139）"；119 行加注说明 P6 是唯一例外 |

**闭环状态**：4 项 NIT 全部在 v3b 中修复，与复审建议逐条对应；修复发生于复审落盘（12:55:11）之后，非复审时已存在（mtime 证据：设计文档 12:59:30 修改）。

## 5. 是否通过

**PASS（通过）**。

判定依据（对照结论标准：PASS = 两轮评审全部发现闭合且无新引入 BLOCKER/WARNING）：

1. **两轮评审全部 15 项发现闭合**：v1 的 2 BLOCKER（B1 五模式误述、B2 资产盘点/重复造轮子）+ 4 WARNING + 4 NIT 全部修复，且修复均有 v3 行号 ↔ 权威源的一一对应证据（见第 1 节）；v2 的 1 BLOCKER（B1' PASS 标签缺证据）+ 2 WARNING（W1' WORKFLOW.md 归属、W2' 机械化排期）+ 2 NIT 全部修复（见第 2 节），其中 B1' 的修复动作即为本复审文件的产生本身——评审链至此证据闭环；
2. **4 条补充想法全部采纳且方式正确**（见第 3 节），采纳不是照抄措辞而是落到落地路径（Phase 1-4）、风险表与缺口分析中；
3. **新观察 4 个 NIT + 1 条并入注记**，全部为示例/措辞/落地细节级（N-New1~N-New4），无新 BLOCKER/WARNING，不影响 v3 的核心论证（协议侧五模式锚点、资产盘点、exit 三态建模、结构性护栏判据、机械化排期）。

建议（不阻塞，可随立项讨论消化）：① 修正裁剪跳变示例 P5→P8 为实际边 P5→P7/P6→P8（N-New1）；② 4.4 补「实现注记」标记或声明设计笔记不适用该判据（N-New2）；③ Phase 1 落地时明确 next/retreat 字段的 S-1/S-2 md 侧对照面（N-New3）；④ exit 三态表补 P6 → P6.5 之例（N-New4）。v3 内容质量足以支撑 RM-AG0049 立项讨论，且本次独立复审以落盘文件形式给出，B1' 所指"标签先于证据"问题终态解决。