---
phase: P4
task_id: TAG0012-protocol-mechanism-fixes
type: implementation
parent: P2-design.md
trace_id: TAG0012-P4-20260818
status: draft
created: 2026-08-18
agent: implementer
---

[PROD_NOT_TOUCHED]

# P4 实现记录 — agate 协议机制增强批（TAG0012，RM-AG0013/RM-AG0014/RM-AG0019/RM-AG0016）

implementation_dir: agate/

> 本任务的"代码"就是协议文档本身（P0-brief 已定性为"协议文档 + 少量 schema 字段"批次），
> 按 P2-design.md §2.1 改动落点表逐文件落地，共改动 **12 个文件**（§2.1 表的第 13 行
> `test_protocol_mechanism_anchors.py` 是 P3 已产出的测试文件，本阶段不改）。
> 单次 implementer 完成全部改动（同 TAG0014 模式），未拆并行派发。

## 1. 改动清单（按 P2-design.md §2.1 / dispatch-context 逐文件清单）

### 1.1 dispatch-protocol.md（三类新机制原文的落点，改动量最大）

| 落点 | 改动 | BDD |
|------|------|-----|
| 「可判定门槛规范」大节 · `verification_env 条件化` 段之后 | 新增 **`verification_env 失败处理协议`** 加粗子节（P2 §1 候选 A 全文转写）：①可重试/不可重试**二列判据表**（可重试＝端口占用/依赖缺失可标准安装/网络瞬时抖动/配置误设；不可重试＝权限凭据缺失、平台原生不支持、需外部人工提供、**机制误用型**（应声明 verification_env 却标 supplementable），不可重试类**不消耗**轮次预算）②**批处理**要求（单轮 ≥2 个待验假设须一次性批量验完，禁"一个假设一轮"）③**止损轮次 = 2**、与 `retries[Pn]` 独立计数、不新增 `.state.yaml` 字段、超限转 PAUSED ④READY 后归属三判据（本任务遗留 / 环境本身问题 / 证据不足默认按第 1 条） | BDD-10 |
| 同上，紧接其后 | 新增 **`环境准备职责边界`** 加粗子节（P2 §3.3 三条条款）：启动/维护/关停默认归主 Agent；并行 subagent 共享环境由主 Agent 统一启动 + dispatch-context 注入访问方式；与 `.state.yaml` 的 `env_state` 建立**引用关系**（指向 state-machine.md「主 Agent 的单步执行（一轮）」的环境一致性验证步骤），不重复定义字段语法。子节头显式声明"本节是权威定义，P5/P6 卡片与 verifier.md 引用本节，不重复展开" | BDD-11 |
| 「派发编排机制」§4 并行规则 | 新增**第 4 条规则「资源密集型默认串行」**：四条判据（全量测试 xdist / CDP-Playwright E2E / 构建打包安装依赖 / 独占外部资源），要并行须先按 P4 卡「基础设施隔离」分配隔离参数，无法隔离即串行（安全默认值）；并与「全阶段适用表」P5 行建立引用关系 | BDD-12 |
| 「派发编排机制」§5 全阶段适用表 · P5 行 | 模式列补 "资源密集型命令 → 模式 5（串行）"，说明列引用并行规则第 4 条 | BDD-12 |
| 「派发 prompt 模板」内联模板正文 | ①「执行顺序」第 4 步补"跑任何 bash 命令前先设超时"②「分阶段落盘」补落盘粒度扩展到**每条 bash 命令执行前** ③新增 **`## 命令超时兜底（层级 4，所有 bash 命令强制）`** 段：取值 = 预期耗时 **×1.5**（有 `_timeout_seconds` 声明则直接取该值）+ 超时/非预期失败后固定三动作（停止执行、写 progress 记卡在哪条命令、返回主 Agent，不自行换命令/深入诊断） | BDD-13 |
| 「派发 prompt 模板」代码块之后（新增 `###` 子节） | 新增 **`命令超时兜底与既有超时机制的分层关系`**：四层对照表（层级 1 = `{key}_timeout_seconds` 静态声明 / 层级 2 = 脚本内部硬超时 HARD 90s·180s / 层级 3 = `AGATE_TDD_TIMEOUT` / **层级 4** = bash 命令级兜底）+ 三条区分要点（外层须留够内层余量、静态声明 vs 运行时纪律、层级 3 只服务 P3）+ TPV0093 教训 | BDD-13 |
| 「非阶段产出的路径规范」self-gate 示例块之后 | 新增"**为何本示例不展开「命令超时兜底」**"说明：self-gate/alignment-review 多为 grep/读文件/`git log` 秒级短命令，逐条声明只稀释 prompt；纪律本身仍适用（层级 4 是全局纪律），确要跑长命令时须把模板该节一并追加 | BDD-13 条件性子句 |

### 1.2 P0/P1/state-machine（RM-AG0019 漂移判据 + RM-AG0013 同类扫描）

| 文件 | 改动 | BDD |
|------|------|-----|
| `agate/phase-cards/P0-orchestrator.md` | ①`known_risks` 填写指引旁新增 **`## 同类/影响面预判`** 节：预判三问（同类实例 grep 命中数+清单 / 上下游消费方 / 同类未来实例是否需回归拦截）+ `known_risks` 写法 yaml 示例 + 与 P1「同类扫描」/P2「影响面梳理」的逐级细化关系 ②新增 **`## P0-brief 时效性自检（漂移判据）`** 节：严重 3 条（task 目标方案不成立 / `executor_env` 平台前提不成立 / `known_risks` 已解决前提实际未解决或已被他任务解决）+ 轻微 2 条（局部细节变化 / `env_constraints` 值刷新）+ 判定流程 + "不要用天数当判据"反例 ③「推进条件」新增 2 项 checklist（同类/影响面预判结论、时效性自检已执行含 `[P0_STALE]` 处理） | BDD-1, BDD-2 |
| `agate/state-machine.md` | `P0 --[...四字段自查通过...]--> P1` 转移条件**紧邻下方**新增注解段（沿用该代码块既有的括号注解体例）：四字段自查含**时效性校验**，覆盖搁置重启 / 跨会话恢复 / 从 PAUSED 恢复三种任务重启场景；严重漂移回 P0、轻微漂移更新字段 + 标 `[P0_STALE]`；判据全文引用 P0 卡「P0-brief 时效性自检（漂移判据）」不重写 | BDD-3 |
| `agate/phase-cards/P1-requirements.md`（卡片） | ①新增 **`## 同类扫描（强制节）`**：扫描动作（grep 关键符号记命中数+文件清单）/ 逐条判定（处理 or 不处理 + 理由）/ 回归拦截手段转 BDD / 结论落盘（"只此一处"也要显式写出），缺失 → requirements-review 打回 ②新增 **`## verification_env vs supplementable 边界判断树`**：ASCII 判断树（能力 → 三态；环境 → `verification_env`）+ 判别口诀 + "把环境问题标 supplementable 属机制误用"+ **环境验证轮次预算占位声明位**（`verification_env_budget` yaml 示例，数值权威定义引 dispatch-protocol.md）③新增 **`## P0-brief 时效性质疑`**：`[P0_STALE: 具体漂移点]` 标记格式（禁裸标记）+ **阻塞/记录二选一**三行表（严重→阻塞回 P0 / 轻微→记录继续 / 无漂移→写"已核对"）④「推进条件」新增 2 项 checklist | BDD-4, BDD-5, BDD-6 |

> BDD-5 的 AND 语义已满足：`verification_env` 由本次新增判断树引入，`supplementable` 为该文件既有 2 处出现（`capability_requirements` 三态说明 + 推进条件），未新增冗余。

### 1.3 analyst.md（RM-AG0013/0014/0019 的角色侧落地）

| 落点 | 改动 | BDD |
|------|------|-----|
| 「方法论」·**隐含需求清单** | 维度列表**首位**新增 `同类/影响面` 维度（grep 扫关键符号记命中数+清单、逐条判处理与否、结论写进 P1 正文、"只此一处"也要写出），落地要求引 P1 卡「同类扫描」 | BDD-7 |
| 「三态判断规则」之后 | 新增 **判断树：`缺的是能力还是环境？`**（ASCII 树：能力侧 → available/supplementable/GAP；环境侧 → 不走三态，走 `verification_env`）+ 口诀（换更强模型能做＝能力；换谁都得先起服务＝环境）+ TAG0009 机制误用教训 | BDD-8 |
| 「输入（自己读取）」节末 | 新增 **"读完 P0-brief 的第一个动作：质疑它的时效性"** 四步流程（对照 P0 卡严重 3 条排查 → 严重则写 `[P0_STALE: 具体漂移点]` 并停下报告主 Agent → 轻微则标记后继续 → 无漂移写"已核对"）+ "不要拿天数当判据" + `[P0_STALE]` 必须带出具体漂移点 | BDD-9 |

### 1.4 timeout_seconds 字段规则三处（RM-AG0016，命名一致）

| 文件 | 改动 | BDD |
|------|------|-----|
| `agate/phase-cards/P2-design.md`（卡片） | ①新增 **`## 影响面梳理（强制节）`**（写在「gate_commands 声明」之前）：改什么 / 不改什么 / 风险在哪 三部分 + "梳理动作要有客观证据" + 与 P0 预判、P1 同类扫描的同源逐级细化关系 ②「gate_commands 声明」样例块新增 `P5_timeout_seconds` / `P5_e2e_timeout_seconds` 两行 ③新增 **`### {key}_timeout_seconds 字段规则`**（P2 §1 候选 B 四点全覆盖）：排除 P3（P3 继续走 `AGATE_TDD_TIMEOUT`，两层不合并）/ per-key 声明（与 `{key}_formatter`·`{key}_e2e` 命名惯例一致，不设共享默认）/ **三档默认基准表**（单元 120s / E2E 300s / 构建 600s，显式标注"手动声明非自动推断"）/ 向后兼容（缺字段等同现状，沿用 `dispatch_plan` 先例）+ 与层级 4 运行时纪律的关系 ④「推进条件」新增「影响面梳理」checklist | BDD-15, BDD-16 |
| `agate/assets/execution-roles/architect.md` | 「批次设计（强制节）」末新增 **「批次设计前置检查项」4 条 checklist**：影响面梳理已完成（**引用** P2 卡「影响面梳理（强制节）」，不重复展开）/ 批次边界对齐影响面梳理的文件分组 / 资源密集型批次已判定串行（引用 dispatch-protocol.md 并行规则第 4 条）/ **长命令已声明 `{key}_timeout_seconds`**（字段规则四点**引用** P2 卡，不重复展开三档基准表细节） | BDD-15b, BDD-16 |
| `agate/assets/templates/task-files.md` | 「3. gate 命令」样例块新增 `P5_timeout_seconds: 120` / `P5_e2e_timeout_seconds: 300` / `P6_timeout_seconds: 120` 三行 + 成块注释：用途（供跑命令方设 shell 超时，×1.5 见 dispatch-protocol.md 分层关系节）/ 命名（per-key 惯例）/ 建议档位三档（标注"手动声明非自动推断"）/ **缺省行为**（不声明即等同现状、无 gate 拦截、老任务无需回填）/ **⚠️ 排除 P3**（P3 走 `AGATE_TDD_TIMEOUT`，完整关系说明**引用** P2 卡字段规则）；并在既有 P3 键注释末补一行"P3 的超时不写 `P3_timeout_seconds`" | BDD-21 |

### 1.5 双源同步 + 引用式落地（BDD-14/17/18/19/20）

| 文件 | 改动 | BDD |
|------|------|-----|
| `agate/assets/templates/dispatch-prompt.md` | 同步 dispatch-protocol.md 的 BDD-13 段落（该文件头已声明"与 dispatch-protocol.md 保持同步，协议文件为权威来源"，故先落协议再同步此处）：「执行顺序」第 4 步补超时提示、「分阶段落盘」补"每条 bash 命令执行前"粒度、新增 `## 命令超时兜底（层级 4，所有 bash 命令强制）` 段（×1.5 + 固定三动作 + 与脚本内部硬超时的分层关系**引用**协议节标题）。措辞精简但语义/关键词与协议侧一致，无矛盾 | BDD-14 |
| `agate/phase-cards/P5-verification.md` | 「按包拆分并行」节内新增两段：①"'无写冲突'不等于可以随便并行"——`gate_commands.P5` 常为全量套件/E2E，属**资源密集型默认串行**，**引用** dispatch-protocol.md 并行规则第 4 条，不重复展开判据 ②**环境准备职责边界（本阶段落地）**——verifier 默认不自行启动环境，由主 Agent 统一准备 + dispatch-context 注入；失败处理**引用**协议两节，不重复展开 | BDD-17, BDD-18 |
| `agate/assets/execution-roles/verifier.md` | 「质量门槛」的 `verification_env 条件化` 条目改为**引用式**：权威定义指向 dispatch-protocol.md「verification_env 条件化」「verification_env 失败处理协议」「**环境准备职责边界**」三节，本文件不重复展开；只保留落到 verifier 身上的两条操作约束（默认不自启环境、失败先分类再动作且可重试类须一次性批量验完） | BDD-19 |
| `agate/phase-cards/P6-acceptance.md` | 「按包拆分并行（条件触发，受限模式）」节末新增 **环境准备职责边界（本阶段落地）** 一段：P6 沿用 P5 已由主 Agent 准备的环境（状态未变时不重复起）；需要新环境时同样遵循 dispatch-protocol.md「verification_env 条件化」/「环境准备职责边界」统一准备规则，不由 verifier subagent 自行启动 | BDD-20 |

## 2. 测试自查结果（自查 ≠ P5 gate）

### 2.1 P3 红灯测试转绿（gate_commands.P3）

```
python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v
→ 28 passed in 0.04s
```

28 条 parametrize 用例（BDD-1~21，含 BDD-10 四条子用例 / BDD-13 三条子用例 / BDD-15b / BDD-16 两条）全部由红转绿。全部关键词按 P2-design.md §2.1 表最后一列**逐字**落地，未意译、未加空格断开：`同类/影响面预判`、`[P0_STALE]`、`时效性校验`、`同类扫描`、`verification_env`+`supplementable`（AND）、`[P0_STALE:`、`同类/影响面`、`缺的是能力还是环境`、`可重试`、`不可重试`、`批处理`、`止损轮次`、`环境准备职责边界`、`资源密集型默认串行`、`命令超时兜底`、`层级 4`、`×1.5`、`影响面梳理`、`timeout_seconds`。

### 2.2 全量回归

```
python3 -m pytest agate/tests/ -q --tb=no
→ 909 passed, 2 skipped in 90.44s
bash agate/tests/scripts/count-tests.sh
→ 总计 911 个用例（目标 ≥749，达标）
```

**过程中出现并已修复的一处回归**（记录备查）：首轮全量回归时 `test_agate_render_dispatch_prompt.py::test_rp_13_no_residual_placeholders_except_whitelisted` 红灯——原因是我在 `assets/templates/dispatch-prompt.md`（渲染模板本体）写的示例含 `{N}` / `{key}` 两个花括号占位符，被"渲染后不得有残留占位符"的既有断言判为残留。**未修改测试**，改为在模板里用 `timeout 180s <你的命令>` 与具体 key 名（`P5_e2e_timeout_seconds: 300`）表达，语义不变，重跑转绿。协议文件 `dispatch-protocol.md` 侧不受此约束（非渲染模板），`{key}_timeout_seconds` 的规范写法保留在协议/卡片/角色文件中。

### 2.3 协议一致性自查

```
python3 agate/scripts/check-protocol-consistency.py --strict
→ 0 ERROR（仅 WARNING）
```

与改动前基线**逐行 diff 比对**：WARNING 集合完全一致（281 行，全部是既有的叙事文件历史死链），本次改动**未新增任何 WARNING、未新增任何 ERROR**。

CHECK3（硬编码行号引用）重点自查：本次新增的全部跨文件引用一律用「节标题」措辞（如"见 dispatch-protocol.md「verification_env 失败处理协议」"、"引用 P2 卡片「影响面梳理（强制节）」"），无一处 `xxx.md L123` 形式。P2-design.md §2.1 / `files_to_read` 里的 `L691-695` 等行号仅用作施工定位坐标，未抄进协议正文。

CHECK4（`gate_commands` 键集合跨文件一致）自查：权威来源是 `architect.md` 的 `gate_commands:` 块。本次**只在 `task-files.md` 与 P2 卡片的样例块新增 `*_timeout_seconds` 键，未动 `architect.md` 的 YAML 块**（architect.md 侧走 prose 引用），因此不会触发"权威里有、副本没有"的 ERROR 分支（额外键不报）。

## 3. 决策标注

- `[DESIGN_GAP]`：**0 条**（`grep -c '^\[DESIGN_GAP:' P4-implementation.md` = 0）。P2-design.md §1 候选 A/B/C 与 §3.3 已把三类新增机制的规则文本、数值（止损轮次 2、×1.5、120/300/600 三档）、判据条数（严重 3 / 轻微 2 / 归属 3）全部写定，落地只做"转写成协议正文 + 补小节标题与过渡句"，未遇到需要我自主拍板的设计缺口。
- `[SCOPE+]`：**0 条**。改动严格限定在 dispatch-context 逐文件清单的 13 行内（实改 12 个文件），未顺手改 P2-design.md §2.2「明确不改」清单里的任何文件（`check-gate.py` / `agate_common.py` / `agate-frontmatter-check.py` / `.state.yaml` schema / `WORKFLOW.md` / `adr.md` / `loop-orchestration.md` / 既有测试 / `scripts/*.sh` 全部零改动）。
- `[SCOPE_GAP]`：**0 条**。dispatch-context 的 13 行清单与 P2-design.md §2.1 表逐行核对一致，无遗漏项。
- `[CLARIFY]`：**0 条**。
- P0-brief 约束 2（本环境 Linux）：新增文本中涉及 Windows 的表述只有 dispatch-protocol.md 不可重试判据里的"平台原生能力不支持（如声明只在 Linux 可行的能力在 Windows CI matrix 侧本质不可行）"——沿用既有文档惯例的引用式表述，**未新增任何"已实测 Windows"类宣称**。
- `[PROD_NOT_TOUCHED]`：全部改动为仓库内协议文档，未接触任何生产环境/数据。

## 4. 实现完成标志对照（P2-design.md §7）

| # | 完成标志 | 落地位置 |
|---|---------|---------|
| 1 | verification_env 失败处理协议 + 职责边界子节 | `dispatch-protocol.md`「verification_env 失败处理协议」「环境准备职责边界」两节（四条规则 + 三条条款齐全） |
| 2 | `timeout_seconds` 三处一致 | P2 卡「`{key}_timeout_seconds` 字段规则」（四点全）+ `architect.md` 批次设计前置检查项（引用式）+ `task-files.md` 样例块（示例 + 注释），三处命名统一为 `{key}_timeout_seconds` |
| 3 | P0-brief 漂移判据三处 | `P0-orchestrator.md`（严重 3/轻微 2 全文）+ `P1-requirements.md` 卡（标记规则 + 阻塞/记录二选一）+ `state-machine.md`（转移条件注解，引用不重写） |
| 4 | 同类扫描机制五处 | `P0-orchestrator.md`「同类/影响面预判」+ `P1-requirements.md` 卡「同类扫描」+ `P2-design.md` 卡「影响面梳理」+ `analyst.md` 隐含需求清单维度 + `architect.md` 批次设计前置检查项 |
| 5 | 运行时管控（双源同步 + 并行规则 + P5 引用） | `dispatch-protocol.md`（模板段 + 四层分层节 + 并行规则第 4 条）↔ `dispatch-prompt.md`（同步段），`P5-verification.md`（引用落地） |
| 6 | 环境准备职责边界落地引用三处 | `verifier.md`（改引用式）+ `P5-verification.md` + `P6-acceptance.md` |
| 7 | 测试完成 | 28 条锚点用例全绿；全量 909 passed / 2 skipped；`count-tests.sh` 911（含新测试文件） |
| 8 | 一致性完成 | `check-protocol-consistency.py --strict` 0 ERROR，含 CHECK3 无硬编码行号引用 |
| 9 | BDD-22 决定落盘 | P2-design.md §3.7 已声明"不做脚本硬校验"，本阶段据此**未改** `check-gate.py`（无独立关键词断言，符合测试文件头说明） |

## 5. 范围核对

- 实际改动文件（`git status --short`，12 个，全部在 `agate/` 下）：
  `agate/dispatch-protocol.md`、`agate/state-machine.md`、
  `agate/phase-cards/P0-orchestrator.md`、`agate/phase-cards/P1-requirements.md`、
  `agate/phase-cards/P2-design.md`、`agate/phase-cards/P5-verification.md`、
  `agate/phase-cards/P6-acceptance.md`、
  `agate/assets/execution-roles/analyst.md`、`agate/assets/execution-roles/architect.md`、
  `agate/assets/execution-roles/verifier.md`、
  `agate/assets/templates/dispatch-prompt.md`、`agate/assets/templates/task-files.md`
- 未改动：`agate/tests/unit/test_protocol_mechanism_anchors.py`（测试文件本体，纪律要求）、P2-design.md §2.2「明确不改」全部条目、版本文件（`README.md` 徽章 / `CHANGELOG.md` / `UPGRADING.md` 的 bump 归 P8，本阶段不动）
- 未执行 `git add` / `git commit`（由主 Agent 处理）
