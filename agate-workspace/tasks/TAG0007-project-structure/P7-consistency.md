---
phase: P7
task_id: TAG0007
type: consistency
parent: P2-design.md
trace_id: TAG0007-P7-20260820
status: approved
created: 2026-08-20
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 2
design_gap_reviewed_count: 2
---

# P7 一致性交叉检查 — TAG0007-project-structure

对照 P1-requirements.md（approved，11 BDD）→ P2-design.md（approved，4 决策组）→
P4-implementation.md（approved，2 DESIGN_GAP）→ P4-review.md（approved）→ P6-acceptance.md
（11/11 PASS）做跨文件一致性审查。重点核实 dispatch-context 约束2（gate_p4「## 新增文件核对表」
子串判定假阴性问题）并给出独立判断。

## 1. DESIGN_GAP 逐条转抄 + REVIEWED

[DESIGN_GAP: dispatch-context 建议 gate_p7 用 `_md_field_get` 读取
`code_map_new_files_count`/`code_map_reviewed_count`（与既有 `design_gap_count` 读取方式一致），
但 `agate-md-field-get.py` 的 `KNOWN_OPS` 允许列表尚未注册这两个新字段名，且该文件不在本批次
允许改动范围内（只能改 `check-gate.py`）——若照字面调用 `_md_field_get`，子进程会因 unknown op
`sys.exit(2)`，`_md_field_get` 恒回退为空字符串，导致两层校验永远被判定为"机制未采用"而跳过，
会使 3 个 gate_p7 新增测试失败。改为使用本文件已有的纯本地函数 `_frontmatter_field(path, field)`
（同文件内定义，无子进程/无 allowlist 限制）直接从 P7-consistency.md frontmatter 块取值，行为
等价……]（P4-implementation.md:166，转抄自原始声明）

[DESIGN_GAP_REVIEWED: 引用 P4-review.md「DESIGN_GAP 逐条判定」第1条（P4-review.md:144-153）——
判定为**接受该实现选择**，但补充一处未被 implementer 声明的边界差异（`_md_field_get` 依赖整个
frontmatter 块可被 `yaml.safe_load` 完整解析，`_frontmatter_field` 是逐行前缀匹配不要求整块
可解析；块内他处存在 YAML 语法错误时两者不等价，分歧方向对当前实现有利——更稳健，不会因无关
字段错误而漏检 CODE_MAP pairing）。非阻塞，已在 P4-review.md 留痕供后续参考，本轮不要求修复。
本 P7 复核该判定合理：`_frontmatter_field` 与 `_md_field_get` 均为 agate_common/check-gate.py
既有公共函数，替换不引入未声明的第三方依赖，且 P3 新增的 12 个 gate_p7 测试用例已覆盖该分支的
两层判定行为（内部一致性层 + 转抄核对层），functional correctness 有测试兜底。]

[DESIGN_GAP: `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 的路径解析方式 P2-design.md 未给出函数级
精确规格（dispatch-context 已明确指出这是本批次需自主决策的空间，P3 测试只覆盖 `P2-skeleton.md`
分支）。本实现采用 dispatch-context 建议的推导方式：`task_dir` 通常形如
`{AGATE_WORKSPACE}/tasks/{Txxx}`，从 `task_dir` 向上两级到 workspace 根，再拼接
`agents/CODE-MAP.md`……此推导依赖"task_dir 是两级嵌套"这一约定，若与
`agate_common._resolve_workspace` / `.agate.env` 的实际工作区解析机制不一致，需后续对齐……]
（P4-implementation.md:168，转抄自原始声明）

[DESIGN_GAP_REVIEWED: 引用 P4-review.md「DESIGN_GAP 逐条判定」第2条（P4-review.md:155-183）——
判定为**非阻塞，登记为技术债 DEBT0016，approve 通过**。理由：① 已读 `agate_common.py:464-493`
`resolve_workspace` 源码 + `pre-commit-gate.py:251-252` `task_dir` 实际构造逻辑，确认当前所有
实际调用路径下 `task_dir` 恒等于 `{workspace}/tasks/{task_id}` 两级嵌套，本地推导与权威函数
输出代数等价；② 唯一真实分歧点是符号链接解析（`Path.resolve()` vs `os.path.abspath`），本
worktree 场景未直接命中该风险路径；③ 影响范围严格限于 `gate_p4` 一处 **WARNING** 分支，不阻断
任何 commit，最坏后果是"少一次提醒"而非"误拦截"；④ 属技术债性质而非需人工抉择的架构问题，已
登记 `DEBT0016`（`category: technical`, `priority: low`）。本 P7 复核：DEBT0016 登记记录存在
（P4-review.md:185-189 已给出 evidence 引用与 `check-debt.py` exit 0 校验），判定合理，不重复
处理，本轮不再追加新 debt。]

**跨文件引用锚点**：本节判定依据 `P4-implementation.md` 正文（DESIGN_GAP 原始声明行）+
`P4-review.md`「DESIGN_GAP 逐条判定」小节的 approved 结论，二者逐条对应，无缺口。

## 2. CODE-MAP 核对（本任务新增检查项，dispatch-context 约束2 重点核实）

### 2.1 独立复核：gate_p4「## 新增文件核对表」字面匹配问题是否属实

读 `check-gate.py:661-718`（`gate_p4` 全函数）确认判定逻辑：

```
if os.path.isfile(skeleton_file) or os.path.isfile(code_map_file):   # L711
    if "## 新增文件核对表" not in _read_text(p4_impl_check):          # L713
        WARNING
```

`code_map_file` 解析为 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（本 worktree 即
`agate-workspace/agents/CODE-MAP.md`）。已用 `ls`/`test -f` 独立确认该文件存在（由本任务自身
`dogfood-bootstrap` 批次创建）——OR 条件对 TAG0007 自己的 P4 commit 成立。

独立执行 `grep -n "## 新增文件核对表" agate-workspace/tasks/TAG0007-project-structure/P4-implementation.md`：
仅 1 处命中，位于第 71 行，出现在「批次二：code-map-docs」的「改动文件清单」表格单元格内——
该单元格描述的是"给 `agate/phase-cards/P4-implementation.md`（协议卡片模板本体）新增了一个
标题逐字为『## 新增文件核对表』的小节"这一**事实陈述**，不是 TAG0007 自己这份任务级
`P4-implementation.md` 正文里真实存在的、逐个新文件填行的核对表。

进一步用标记级正则独立核实：`grep -n "^\s*-\?\s*\[CODE_MAP_UPDATED\]\|^\s*-\?\s*\[CODE_MAP_EXEMPT"
agate-workspace/tasks/TAG0007-project-structure/P4-implementation.md` → **0 命中**。全文出现
`CODE_MAP_UPDATED`/`CODE_MAP_EXEMPT` 字样的 3 处（第 71、155、156、157 行）均是描述"这两个标记
该如何使用"的说明性/引用性文字（分别在改动文件清单表格与 gate_p7 转抄核对层实现说明中），没有
一处是 TAG0007 自己为自己新增的文件（`skeleton-template.md`、`code-map-template.md`、
`agate-workspace/agents/CODE-MAP.md`、3 个新增测试文件等）真实打上 `[CODE_MAP_UPDATED]` 或
`[CODE_MAP_EXEMPT: 理由]` 标记的记录。

**结论：问题属实。** 这是一处真实的假阴性——`"## 新增文件核对表" not in text` 的子串判定被
TAG0007 自己描述"这个机制怎么实现"的说明性文字中恰好逐字出现的标题字符串误判为"已满足"，实际上
TAG0007 自己的 P4-implementation.md 并没有一份真正填写的、逐文件打标记的核对表。该 WARNING
本该触发却未触发。

### 2.2 是否需要 implementer 回填一份真正的核对表：独立判断

**判定：`[CODE_MAP_DRIFT:]`——存在真实偏离，但不构成 P7 级 [BLOCKER]。**

判断依据：

1. **BDD-7 的 Given 前提字面成立**：BDD-7（P1-requirements.md:87-91）要求"P4 实现阶段新增了一个
   不在既有 CODE-MAP.md 记录范围内的文件"时，"P4 产出中包含对 CODE-MAP.md 的相应更新，或显式声明
   该新增文件不改变项目架构全貌因而豁免更新的理由；两者必居其一，不允许沉默跳过"。TAG0007 自己
   的场景恰好命中这条 Given——`agents/CODE-MAP.md` 在本次 P4 之前完全不存在（本次 P4 才首次创建），
   是"从 0 到 1 建立该维护物"的自指/bootstrapping 场景，所有本次新增文件（含骨架模板、CODE-MAP
   模板、3 个测试文件、`check-gate.py` 改动）在"既有 CODE-MAP.md"意义上都不在任何记录范围内。
2. TAG0007 自己的 P4-implementation.md 对这批新文件的 CODE-MAP 处置**只以叙事方式**交代（4 个
   批次改动文件清单表格 + 文末「BDD 覆盖核对表」+「批次四：dogfood-bootstrap」产出摘要段落），
   完整覆盖了每个新文件的归属信息，但**未使用 P2 设计的标准标记**（`[CODE_MAP_UPDATED]` /
   `[CODE_MAP_EXEMPT: 理由]`）逐条落标——这与该任务要求未来所有任务遵守的标准格式不一致，构成
   "机制的自我应用缺口"。
3. 但该缺口的实际风险有限：① gate_p4 的 WARNING 按 P2-design.md §1.3 R4 设计本就是**非阻断**
   （"即便误触发也不拦截 commit"），即使当初正确触发也只是提醒，不会改变本次 P4/P7 的通过结果；
   ② P6-acceptance.md 对 BDD-6/7/8/9 的 PASS 判定依据是"机制本身（`[CODE_MAP_UPDATED]`/
   `[CODE_MAP_EXEMPT]` 标记 + gate_p7 两层 pairing 校验）在单元测试构造的场景下是否正确工作"，
   不依赖"TAG0007 是否对自己的新增文件使用了标准标记"，因此该发现不推翻已有的 11/11 PASS 判定；
   ③ TAG0007 自身不声明 `project_phase: bootstrap`（P1-requirements.md frontmatter 无此字段），
   骨架半侧机制（BDD-1/3/4）对自身合法不适用（agate 是 established 项目非 0→1），只有 CODE-MAP
   半侧（BDD-6/7/8/9）存在"是否自我应用"的开放问题。
4. **建议动作**：不要求打回 P4 重做（P4-review.md 已 approved 且已 commit，重开 P4 的流程成本
   与该问题的实际风险不成比例），但建议 implementer/主 Agent 后续用**低成本方式**之一处理：
   (a) 为 `P4-implementation.md` 补一份真正的「新增文件核对表」附录，逐个列出本任务实际新增的
   文件（`skeleton-template.md`、`code-map-template.md`、`agate-workspace/agents/CODE-MAP.md`、
   `test_skeleton_template_stack_neutral.py`、`test_code_map_template.py`、
   `test_check_gate.py` 新增用例部分）+ 骨架归属列（均为 `N/A（established 项目，骨架机制不
   适用）`）+ CODE-MAP 处理列（对模板/脚本类文件标 `[CODE_MAP_UPDATED]`，理由是这些文件的
   模块归属已被本次创建的 `agate-workspace/agents/CODE-MAP.md`「模块」字段覆盖；对纯测试文件
   可标 `[CODE_MAP_EXEMPT: 测试文件不改变项目架构全貌]`）；或 (b) 比照 DEBT0016 的处理方式登记
   一条技术债，说明"gate_p4 的子串判定在自指场景下存在假阴性风险，且 TAG0007 自身的 P4 产出未
   对自己的新增文件使用标准 CODE-MAP 标记"，留待独立任务处理 gate_p4 判定逻辑的健壮性（例如改为
   要求标题必须整行匹配 `^## 新增文件核对表\s*$` 而非子串包含，可同时修复本类假阴性对未来其他
   自指/dogfooding 场景的影响）。两种路径均不要求本轮 P7 打回。

**本轮 P7 结论对该发现的处理**：记为已识别、已显式论证的非阻塞发现，不计入 `blocker_count`
（TAG0007 对自身的处理属于"叙事覆盖但格式不合规"，而非"完全未处理/沉默跳过"，且不影响任何
BDD 的 PASS 判定或任何 gate exit code），但作为 P7 产出的正式记录留痕，供主 Agent 决定是否在
P8 前追加处理。

## 3. SCOPE+ 闭环核查

全任务目录 `grep -rn "\[SCOPE+\]" agate-workspace/tasks/TAG0007-project-structure/*.md` 独立复核：
命中的全部行都出现在各批次 `P4-dispatch-context-implementer-*.md`/`P4-dispatch-context-review.md`/
`P7-dispatch-context-consistency-reviewer.md` 这类**派发指引模板文件**里，是"如果发现范围外
改动该怎么标记"的通用规则说明文字，不是任何一份 P1-P6 实际产出文件（P1-requirements.md、
P2-design.md、P4-implementation.md、P4-review.md、P6-acceptance.md）正文中真实出现的 `[SCOPE+]`
声明。**结论：SCOPE+ 闭环天然满足（无 SCOPE+ 需要闭环，全任务 0 处实际触发），无需
`[SCOPE_RESOLVED]` 标记。** 该结论已显式写出，不留空白。

## 4. 跨文件一致性核查

### 4.1 P1 BDD 数量 vs P6 验收结果数量

`P1-requirements.md`「3. BDD 验收条件」节声明 BDD-1 ~ BDD-11（共 11 条，RM-AG0008 骨架
BDD-1~5 + RM-AG0009 CODE-MAP BDD-6~11）。`P6-acceptance.md`「BDD 逐条对照」节逐条列出
`PASS BDD-1` 至 `PASS BDD-11`（共 11 行），末尾 `**Summary**: 11/11 PASS, 0 FAIL`，frontmatter
`pass: 11 / fail: 0` 与正文一致。逐条编号核对：BDD-1（骨架存在性）/BDD-2（模板参数化）/
BDD-3（不重复触发）/BDD-4（骨架归属）/BDD-5（骨架回归）/BDD-6（CODE-MAP存在）/BDD-7（CODE-MAP
更新义务）/BDD-8（P7核对）/BDD-9（依赖偏离可见信号）/BDD-10（refactor不豁免）/BDD-11（CODE-MAP
回归）—— P6 每条 PASS 行的内容摘要与 P1 对应 BDD 原文语义逐条匹配，无错位、无遗漏、无多余。
**锚点**：`P1-requirements.md` §3（L51-113）× `P6-acceptance.md`「BDD 逐条对照」节（L32-44）。

### 4.2 P2 packages vs P8 release bump 范围

`P2-design.md` frontmatter 声明 `packages: [phase-cards, execution-roles, templates, scripts]`
（L12）。**P8-release.md 尚未产出**（当前任务处于 P7 阶段），本项暂不适用，留待 P8 阶段核对，
本轮不编造 P8 数据，不做判定。

### 4.3 P4 实现路径 vs P2 方案设计

核对 `P4-implementation.md` 4 批次改动文件清单与 `P2-design.md` §1.1「改什么」表（L49-67）逐条
对应：
- `skeleton-docs` 批次 4 个文件（`P1-requirements.md`/`P2-design.md`/`architect.md`/
  `skeleton-template.md`）与 P2 §1.1 对应表格行的文件路径、插入位置描述、关联 BDD 编号
  （BDD-1/2/3）逐条一致。
- `code-map-docs` 批次 5 个文件（`P4-implementation.md`/`P7-consistency.md`/
  `consistency-reviewer.md`/`code-map-template.md`/`WORKFLOW.md`）与 P2 §1.1 对应行一致
  （BDD-4/6/7/8/9/10）。
- `gate-script-both` 批次（`check-gate.py` 的 `gate_p2`/`gate_p4`/`gate_p7` 三处）与 P2
  §1.1 对应行、§2.2/§2.3 候选方案的判定逻辑描述逐条一致（字段名 `project_phase`、标题
  `## 骨架声明`/`## 新增文件核对表`、frontmatter 字段 `code_map_new_files_count`/
  `code_map_reviewed_count`、标记 `[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT]` 全部逐字匹配，
  已由 P4-review.md「约束4核查」表格独立核验过一次，本 P7 复核该表格未发现反例）。
- `dogfood-bootstrap` 批次（`agate-workspace/agents/CODE-MAP.md`）与 P2 §1.1 表格最后一行、
  §4「实现完成的标志」第4条一致（五字段：模块/层/依赖方向/关键文件/约定，均已实地核对存在）。

**锚点**：`P4-implementation.md`「改动文件清单」各批次小节（L23-30、L67-75）× `P2-design.md`
§1.1（L49-67）× P4-review.md「约束4核查」表格（L88-101）。未发现"实现路径与设计吻合但内容
偏离"的情形。

## 5. 未决项清零核查（独立复核，不只信主 Agent 转述）

独立执行以下 grep，范围覆盖 `agate-workspace/tasks/TAG0007-project-structure/` 下全部
`.md` 产出文件：

- `grep -rn "^\s*>\?\s*-\?\s*\[BLOCKER" *.md` → 0 处出现在 P1/P2/P4/P4-review/P6 正文（唯一
  命中在 `P7-dispatch-context-consistency-reviewer.md` 的 gate 规则说明文字里，非产出正文）。
- `grep -rn "\[DEVIATION-CRITICAL" *.md` → 同上，仅命中 dispatch-context/角色规则说明文字。
- `grep -rn "\[NEED_CONFIRM" *.md`（排除 `NO_NEED_CONFIRM`）→ P1-requirements.md 与
  P6-acceptance.md 正文均只有 `[NO_NEED_CONFIRM]`，无残留 `[NEED_CONFIRM]`；其余命中全部在
  dispatch-context 模板的规则说明文字里。
- P6-acceptance.md 客观验收口径为 PASS/FAIL 二值（frontmatter `pass: 11 / fail: 0`），无
  `NEED_CONFIRM` 语义残留，符合「P6 不再有 NEED_CONFIRM」要求。

**结论**：P1-requirements.md 无残留行首 `[NEED_CONFIRM]`；P4-implementation.md/P4-review.md/
P6-acceptance.md 均无 `[BLOCKER]`/`[DEVIATION-CRITICAL]` 残留。未决项清零核查通过。

## 6. 结论

- `blocker_count: 0`，`deviation_critical_count: 0`，`deviation_count: 0`
- DESIGN_GAP 2 条全部转抄 + REVIEWED 配对（第1节）
- SCOPE+ 闭环天然满足（第3节）
- CODE-MAP 核对：gate_p4 假阴性问题**属实确认**，独立判定为 `[CODE_MAP_DRIFT:]`（非阻塞发现，
  建议后续低成本补救，不打回本轮 P7，见第2节完整论证）
- 跨文件一致性核查（BDD数量匹配、实现路径吻合）均已给出具体锚点，P2 packages vs P8 bump 范围
  待 P8 阶段核对、本轮不适用
- 未决项清零：独立复核确认

`status: approved`（无 [BLOCKER]/[DEVIATION-CRITICAL]，映射规则：无 BLOCKER → approved）。
第2节 CODE_MAP_DRIFT 发现建议主 Agent 在推进 P8 前自行决定是否追加处理（补核对表附录或登记
技术债），本 P7 不因该发现单独打回。
