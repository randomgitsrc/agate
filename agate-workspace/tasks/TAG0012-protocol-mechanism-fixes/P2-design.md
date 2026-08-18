---
phase: P2
task_id: TAG0012-protocol-mechanism-fixes
type: design
parent: P1-requirements.md
trace_id: TAG0012-P2-20260818
status: draft
created: 2026-08-18
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3
packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]
domains: [process]
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 8, batches: [{id: p0-p1-state-scan, complexity: low}, {id: analyst-role, complexity: low}, {id: dispatch-protocol-core, complexity: high}, {id: dispatch-prompt-sync, complexity: low}, {id: p5-refs, complexity: low}, {id: p6-verifier-refs, complexity: low}, {id: p2-architect-timeout, complexity: medium}, {id: task-files-schema, complexity: low}]}
---

[PROD_NOT_TOUCHED]

# P2 方案设计 — agate 协议机制增强批（TAG0012，RM-AG0013/RM-AG0014/RM-AG0019/RM-AG0016）

> 本文件把 P1-requirements.md 的 23 条 BDD（BDD-1~22 + BDD-15b）转化为可实现的技术方案。P1 已把
> "改哪个文件、哪个小节"锁定到 11 个文件分组（A-K），本设计的核心工作是给出**三类新增机制**的
> 具体规则文本（不是重复 P1 的问题清单），其余 BDD 按 `follows_existing_pattern`（权威定义 + 卡片
> /角色文件引用惯例）落地，逐条覆盖见第 4 节 BDD 覆盖映射表。

## 0. 影响面梳理（本设计自身对 RM-AG0013 的示范）

在写候选方案前先做了一次影响面核实（RM-AG0013 要求"设计候选方案前做影响面梳理"，本文档以身作则）：

- grep 全仓 `verification_env`（`dispatch-protocol.md`/`verifier.md`/P5/P6 卡片），确认消费点只有这 4 处，无遗漏文件
- grep 全仓 `timeout_seconds`：零命中，确认是纯新增字段非补全（P1 第 0 节已确认，本次复核一致）
- 读 `check-protocol-consistency.py` 的 `PROTOCOL_FILES`/`PROTOCOL_DIRS`/`check_line_refs`（CHECK3）：确认 `dispatch-protocol.md`/`phase-cards/`/`assets/`（execution-roles+templates）/`state-machine.md` 全部在协议文件扫描面内——**这意味着 P4 落地时任何跨文件引用文本禁止写 `xxx.md L123` 硬编码行号**（会被 CHECK3-lineref 判 ERROR），必须用"见 dispatch-protocol.md「派发编排机制」并行规则"这类节标题引用。此约束已写入第 3 节各处方案文本与 files_to_read 备注，避免 P4 implementer 沿用 P1-requirements.md 里为了定位而写的 `L691-695` 式表述直接誊抄进协议正文
- 读 `agate/rules/state-transitions.md` 重试上限表（P1/P2 MAX=3，P3/P5/P6/P7/P8 MAX=2），作为设计"止损轮次"数值时的参照基准（不生搬硬套，见 §1 候选方案 A）

## 1. 候选方案与权衡（三个设计维度）

按 dispatch-context 约束 1，候选方案聚焦三类"新增机制设计"，每个维度 ≥2 候选，正交独立。其余
BDD（"新增小节 + 可 grep 命中"类）按既有"权威定义 + 卡片/角色文件引用"惯例落地，设计空间小，
不逐条写候选，覆盖见第 4 节。

### 候选方案 A：verification_env 失败处理协议（BDD-10 的 4 个问题）

**方案 A1（采纳）：止损轮次=2、独立计数不入 `.state.yaml`、批处理强制、三条 READY 后归属判据**

具体规则（供 P4 逐字落地到 dispatch-protocol.md verification_env 节）：

1. **可重试 / 不可重试清单**：
   - 可重试（环境本身可通过标准操作恢复，允许在轮次预算内重试）：端口占用/临时资源未就绪、依赖包缺失但可用标准安装命令补齐、网络连接瞬时抖动/服务未完全启动、配置路径或环境变量误设（本任务范围内可修正）
   - 不可重试（立即升级人工，不消耗验证轮次预算）：权限/凭据缺失且当前环境无法自行获取、平台原生能力不支持（如声明只在 Linux 可行的能力在 Windows CI matrix 侧本质不可行）、需要外部人工提供的账号/证书/生产访问、**机制误用型问题**（如 TAG0009：应声明 verification_env 却标了 supplementable——这是协议使用错误，应立即改正声明方式，不是"环境故障重试"）
2. **批处理要求**：单轮验证若同时存在 ≥2 个待验证假设，必须一次性列出并在同一轮内批量验证完，不允许"改一个假设→单独起一轮验证→再改下一个假设→再起一轮"（TAG0009 11.7 小时教训的直接对策）
3. **止损轮次 = 2 轮**，与阶段 retry（`retries[Pn]`）**独立计数**，不新增 `.state.yaml` 字段（本任务范围锁定在协议文档，不做状态机 schema 变更）——由主 Agent 在验证 subagent 的 dispatch-context 中手工记录"当前第几轮验证 + 历次已排除假设清单"作为轮次追踪。超过 2 轮未解决 → 状态转 **PAUSED**，落盘 `PAUSED-resolution.md` 引用本轮诊断（沿用既有 PAUSED 流程，不新建流程）
4. **READY 后问题归属判定（三条判据）**：①若问题是本任务改动引入的环境依赖变化（如新增依赖但 P0-brief 未声明）→ 判定**本任务遗留**，回 P4/P5 修复；②若问题是环境本身的外部变化（与本任务改动无关，如 CI 平台版本升级导致行为差异）→ 判定**环境本身问题**，登记 known_risks/roadmap，不重开本任务；③证据不足无法判定 → 默认按①处理（保守原则，避免真实缺陷逃逸）

- 优点：轮次数值可判定（2，非"看情况"）；与阶段 retry 独立计数直接回应 P1 隐含需求 4（避免"环境重试用光阶段 retry 预算"的隐性耦合）；不触碰 `.state.yaml` schema，改动面收窄在文档层
- 缺点：轮次追踪靠主 Agent 人工记录（无脚本强制），存在漏记风险；但本任务定性是"协议文档改动"，引入新 state.yaml 字段属于范围外扩（P0-brief 约束 4 禁止），该缺点是范围约束下的合理取舍
- 工作量：dispatch-protocol.md verification_env 节新增约 25-30 行规则文本

**方案 A2：止损轮次并入既有 `retries[Pn]`（复用现有计数器，不新增语义）**

- 实现：环境验证失败与阶段质量失败共用 `retries[Pn]`，达到阶段 MAX（如 P5=2）后按现有阶段回退/PAUSED 规则处理，不单独定义"验证轮次"
- 优点：零新概念，复用现成状态机字段，理解成本最低
- 缺点：直接违反 P1 隐含需求 4 明确指出的反模式——"环境重试用光了阶段 retry 预算"（如 P5 因环境问题耗光 2 次 retry，代码本身质量问题反而没有 retry 预算可用）；且与 P1 BDD-10 Then 子句"止损轮次由谁判定"的独立设计要求冲突（P1 已经预判这是需要区分的两套计数）
- 选择理由：A2 的"零新概念"是以重演 P1 已明确警示的反模式为代价。**采纳 A1**

### 候选方案 B：timeout_seconds 与 AGATE_TDD_TIMEOUT 关系 + 阈值基准（BDD-16/21）

**方案 B1（采纳）：排除 P3，per-key 声明，三档默认基准表（声明性字段，不做运行时自动推断）**

具体规则：

1. **关系判定：排除 P3**——`gate_commands.P3` 继续用既有 `AGATE_TDD_TIMEOUT` env var 机制（`agate_common.py:408`，`run_test_with_formatter()`，默认 120s，`check-tdd-red.py` 消费）；`timeout_seconds` 只服务 `P5`/`P6`/其他非 P3 key。理由：P3 层已有成熟的 TDD 语义（exit 124 → `_timeout_json()`，区分 A/B 类错误），是运行时代码消费的字段；`timeout_seconds` 若要"互斥覆盖"P3，需改 `agate_common.py` 消费链路（读 `gate_commands.P3_timeout_seconds` 覆盖 env var），这是运行时逻辑新增，超出 P0-brief 定性的"少量脚本 schema 字段"范围，风险/工作量不对称
2. **声明粒度：每条 key 独立声明**（`{key}_timeout_seconds`，如 `P5_timeout_seconds: 300`），不设整体共享默认——不同命令类型耗时差异大（单元测试 vs E2E 差 2.5 倍以上），共享一个默认值起不到"分类阈值"作用；命名与既有 `{key}_formatter`/`{key}_e2e` per-key 命名惯例一致（P1 BDD-21 要求三处命名一致）
3. **默认阈值基准表**（文档提供"建议档位"供各任务 P2 architect 手动按命令类型声明，非自动推断——保持字段纯声明性，无代码消费方去"猜"命令类型）：

   | 命令类型 | 建议默认档位 | 依据 |
   |---------|------------|------|
   | 单元测试类（pytest/vitest 等） | 120s | 与 `AGATE_TDD_TIMEOUT` 默认值对齐，同类命令的既有锚点 |
   | E2E 类（Playwright/CDP） | 300s | 覆盖页面加载+多步操作；比 L790-879 既有"脚本内部硬超时"HARD=90s/180s 更大，因为 `timeout_seconds` 是外层命令级预期时长，脚本内部硬超时是内层子机制，外层须留够内层完整走完的余量 |
   | 构建类（编译/安装依赖/打包） | 600s | 覆盖 `npm install`/编译等可能耗时较长的操作（TPV0093 `make test-quick` 挂 188min 的教训：宁可基准档位定高，避免长命令被误判失败） |

4. **向后兼容**：缺字段 → 行为等同现状（沿用 `dispatch_plan` "缺字段/坏 YAML → gate 跳过校验"既有先例），不新增强制阻断

- 优点：不改动 `agate_common.py` 运行时逻辑，改动面锁定在文档 + schema 样例；per-key 声明贴合"不同命令耗时差异大"的真实场景；三档基准表直接回应 TPV0093"阈值过低误杀长命令"的教训
- 缺点：P3 与 P5/P6 用两套不同机制表达"超时"（env var vs 声明字段），文档需要显式区分说明这个不对称，减损"一个字段管所有阶段"的直觉预期——已在 `task-files.md` 样例块注释中显式引用本节说明（BDD-21 联动要求）缓解
- 工作量：`P2-design.md` 卡 + `architect.md` 批次设计节 + `task-files.md` 样例块，共 3 处文档新增

**方案 B2：互斥覆盖（`timeout_seconds` 存在时优先覆盖 `AGATE_TDD_TIMEOUT`，含 P3）**

- 实现：`agate_common.py::run_test_with_formatter()` 新增参数读取 `gate_commands.P3_timeout_seconds`（若声明），覆盖 env var 优先级；`check-tdd-red.py` 需要新增从 P2-design.md 读取该字段并转成 env var 传给子进程的桥接逻辑
- 优点：字段语义统一，P2 声明即对所有阶段生效，无需理解"P3 例外"这层不对称
- 缺点：需要新增运行时消费链路（`agate_common.py` + `check-tdd-red.py` 两处代码改动 + 配套测试），工作量与风险显著高于 B1；且与既有 `AGATE_TDD_TIMEOUT` 的"env var 全局默认"设计初衷（跨任务统一默认值）产生优先级歧义，需要额外文档说明"何时用哪个"，认知负担不降反升
- 选择理由：B2 的"语义统一"收益，被"新增运行时消费链路 + 优先级歧义文档负担"的成本抵消，且超出 P0-brief"少量脚本 schema 字段"定性。**采纳 B1**（P1 objective_info 第 0 节已明确要求"必须保留/强化这层区分，不能合并成一层"，与 B1 结论一致）

**关联决定（BDD-13/14 命令级超时兜底倍数，layer 4）**：与 `timeout_seconds`（P2 静态声明字段，B 维度）是相邻但独立的机制（P1 隐含需求 1 明确要求拆开）。运行时纪律规则：subagent 执行**任意** bash 命令前必须设 shell 层 timeout，取值 = 该命令预期耗时 × **1.5**（沿用 P0-brief 已给出的具体倍数，未见需要偏离的理由——TPV0093 教训要"宁可等一等也不要无限挂起"，1.5 倍在"给足抖动余量"与"及时发现异常"间取得的平衡已经过一次真实事故验证）。当该命令对应 `gate_commands.{key}_timeout_seconds` 已声明时，"预期耗时"直接取该值；未声明时（含绝大多数非 gate 命令的日常 bash 调用）由 subagent 按经验估算。超时后停止执行、写 progress 记录卡在哪条命令，返回主 Agent，不允许自行更换命令或深入诊断（P1 BDD-13 Then 子句 2）。

### 候选方案 C：P0-brief 漂移判定标准（RM-AG0019，轻微 vs 严重两档）

**方案 C1（采纳）：前提性质判据（checklist 命中即严重，否则轻微）**

具体规则：

**严重漂移**（需回 P0 重新立项/可行性分析）——命中以下任一条：
1. task 字段描述的目标方案本身不再成立（如所需修改的技术路线/架构已变化，TAG0008 案例：立项写 `.sh` 路线，启动时已全量 Python 化）
2. `executor_env` 声明的平台/运行时前提不再成立（如声明的 CI 环境/工具链已下线或大版本不兼容）
3. `known_risks` 中被判定为"已解决前提"的条目实际仍未解决，或反之已被其他任务解决导致本任务范围重叠/失效

**轻微漂移**（更新 P0-brief 对应字段 + 标注 `[P0_STALE: 漂移点]` 后继续）——不命中以上任一条，仅：
4. 局部细节变化（文件路径、依赖版本号、单个工具调用方式）不影响任务方案选择
5. `env_constraints` 的具体值需刷新（如 `debug_env` 端口变化）但环境类型未变

判定流程：主 Agent/analyst 对照 1-3 逐条排查，命中任一条 → 严重（回 P0）；全部不命中 → 轻微（更新 P0-brief + `[P0_STALE]` 标注 + 继续 P1）。

- 优点：checklist 二值化可判定（不是"看情况"）；直接贴合 TAG0008 真实案例（技术路线切换）；判据与"重新立项"这一动作的触发条件语义对齐——只有"方案本身不成立"才值得推倒重来
- 缺点：checklist 仍需 analyst 对"是否属于路线级变化"做一定经验判断，边界案例（如依赖大版本升级但接口兼容）判断仍有主观空间——但这是"可判定标准"能做到的上限，不可能消灭全部主观性，只能把主观判断收窄到 3 条清单内
- 工作量：P0 卡 + P1 卡 + state-machine.md L77 上下文，共新增判断树文本

**方案 C2：时间阈值判据（距 P0-brief 创建天数 >N 天强制复核为严重）**

- 实现：如 >30 天默认判定严重（强制回 P0），≤30 天默认轻微
- 优点：极简单，机械可判定，零主观判断
- 缺点：时间与漂移程度不相关——TAG0008 案例本身就是反例：8-13 立项、8-15 启动仅隔 2 天，但技术路线已经切换（若套用 C2 的"≤30 天默认轻微"规则会直接漏判，恰恰漏掉本任务用来论证 RM-AG0019 必要性的那个真实案例）；反之一个搁置 60 天但项目完全没变的任务会被误判严重，触发不必要的重新立项流程，造成噪音
- 选择理由：C2 的"简单"是以判据失真为代价，且被 TAG0008 案例直接证伪。**采纳 C1**

> `candidate_count: 3`（A/B/C 三维度各选 1，每维度均 ≥2 候选 + 权衡 + 理由）。

## 2. 影响域分析（改 / 不改 / 风险）

### 2.1 改什么（Modify，按 P1 §3 十一个文件分组逐条核对）

| 文件 | 改动内容 | 关联 BDD | 关键词锚点（供 grep 断言审计测试断言） |
|------|---------|---------|------------------------------------|
| `agate/phase-cards/P0-orchestrator.md` | 新增"同类/影响面预判"节（写在 `known_risks` 填写指引旁）；「推进条件」新增 P0-brief 时效性自检项（引用 §1 候选 C 的 checklist） | BDD-1, BDD-2 | `同类/影响面预判`、`[P0_STALE]` |
| `agate/state-machine.md` | L77 转移条件文本紧邻处新增说明段：四字段自查含时效性校验，覆盖任务重启场景，引用 P0 卡规则（不重写全文） | BDD-3 | `时效性校验` |
| `agate/phase-cards/P1-requirements.md`（卡片） | 新增"同类扫描"强制节；新增 verification_env vs supplementable 边界判断树（含"环境验证轮次预算占位"声明位）；新增 `[P0_STALE: 具体漂移点]` 标记规则 + 阻塞/记录二选一说明 | BDD-4, BDD-5, BDD-6 | `同类扫描`、`verification_env`、`supplementable`、`[P0_STALE:` |
| `agate/assets/execution-roles/analyst.md` | 「隐含需求清单」新增"同类/影响面"维度；「三态判断规则」旁新增"缺的是能力还是环境？"判断树；「输入」节新增 P0-brief 时效性质疑步骤 | BDD-7, BDD-8, BDD-9 | `同类/影响面`、`缺的是能力还是环境`、`[P0_STALE]` |
| `agate/dispatch-protocol.md`（verification_env 节，L940-960 现状） | 扩为"条件化 + 失败处理协议"：新增 §1 候选 A 的完整规则文本（可/不可重试清单 + 批处理要求 + 止损轮次=2 独立计数 + READY 后归属三判据）；新增"环境准备职责边界"子节（启动/维护/关停默认归主 Agent，多 subagent 共享环境由主 Agent 统一注入，与 `.state.yaml` `env_state` 建立引用关系不重复定义字段语法） | BDD-10, BDD-11 | `止损轮次`、`可重试`、`不可重试`、`批处理`、`环境准备职责边界` |
| `agate/dispatch-protocol.md`（「派发编排机制」§4 并行规则，L691-695 现状） | 新增第 4 条规则："资源密集型默认串行"（全量 pytest xdist / CDP-Playwright E2E 等即使无数据依赖也默认串行），与「全阶段适用表」P5 行建立引用关系 | BDD-12 | `资源密集型默认串行` |
| `agate/dispatch-protocol.md`（「派发 prompt 模板」正文，L429-497 现状） | 新增"命令超时兜底 + 命令前 progress"标准段（§1 候选 B 关联决定：×1.5 倍规则 + 超时/非预期失败均停止返回 + 分阶段落盘粒度扩展到"每条 bash 命令执行前"），与 L790-879 既有「Playwright/长时操作」层级 2 硬超时机制建立显式引用区分（标注"层级 4：bash 命令级超时兜底"） | BDD-13 | `命令超时兜底`、`层级 4`、`×1.5` |
| `agate/dispatch-protocol.md`（L521「非阶段产出的路径规范」示例块） | 判定该场景（self-gate/alignment-review）不适用命令超时兜底展开（本身多为 grep/读取类短命令），加一句"为何不适用"说明，不重复展开完整规则 | BDD-13（条件性子句） | — |
| `agate/assets/templates/dispatch-prompt.md` | 同步 BDD-13 的"命令超时兜底 + 命令前 progress"段落到「分阶段落盘」/「执行顺序」节，文本与 dispatch-protocol.md 对应段落不矛盾 | BDD-14 | `命令超时兜底` |
| `agate/phase-cards/P2-design.md`（卡片） | 新增"影响面梳理"强制节；「gate_commands 声明」节新增 `{key}_timeout_seconds` 字段规则（§1 候选 B 全部 4 点：per-key 声明/三档基准表/向后兼容/排除 P3 关系说明） | BDD-15, BDD-16 | `影响面梳理`、`timeout_seconds` |
| `agate/assets/execution-roles/architect.md`（「批次设计」节） | 新增检查项：引用 P2 卡「影响面梳理」要求（不重复展开）；同步 `timeout_seconds` 字段规则位（引用 §1 候选 B，不重复展开三档基准表细节） | BDD-15b, BDD-16 | `影响面梳理`、`timeout_seconds` |
| `agate/phase-cards/P5-verification.md`（「按包拆分并行」节，L113-128 现状） | 新增一句引用："资源密集型默认串行"（引用 dispatch-protocol.md BDD-12 规则，不重复展开判据细节）；新增一句明确"环境准备职责边界"落地（verifier 默认不自行启动环境，引用 dispatch-protocol.md verification_env 节） | BDD-17, BDD-18 | `资源密集型默认串行`、`环境准备职责边界` |
| `agate/assets/execution-roles/verifier.md`（L245-262「verification_env 条件化」节现状） | 改为引用 dispatch-protocol.md 权威定义（BDD-10/BDD-11），不重复展开失败处理协议/职责边界完整内容 | BDD-19 | `环境准备职责边界`（引用式） |
| `agate/phase-cards/P6-acceptance.md` | 新增一句："P6 环境访问沿用 P5 已由主 Agent 准备的环境（若环境状态未变），需要新环境时同样遵循 dispatch-protocol.md verification_env 节统一准备规则，不由 verifier subagent 自行启动" | BDD-20 | `环境准备职责边界`（引用式） |
| `agate/assets/templates/task-files.md`（L266 起 `gate_commands:` 样例块） | 新增 `timeout_seconds` 字段格式示例（含用途/缺省行为注释）；若样例中 `P3` key 下也标注，须附引用指向 §1 候选 B「排除 P3」说明，不重复展开关系细节 | BDD-21 | `timeout_seconds` |
| `agate/tests/unit/test_protocol_mechanism_anchors.py`（新建） | grep 断言审计测试：逐条断言上表全部关键词锚点确实落盘（见 §3.6） | BDD-22（分支：文档约定，见 §3.7） | — |

### 2.2 不改什么（Not Modify）

| 文件/范围 | 理由 |
|-----------|------|
| `agate/scripts/check-gate.py` | **明确不改**（BDD-22 分支决定，见 §3.7）：`timeout_seconds` 目前无运行时代码消费方（P5/P6 由 subagent 自跑 `gate_commands` 命令，`check-gate.py` 只是阶段产出物门槛检查器，不代跑命令、不施加超时），强行加"数值合法性"级浅校验收益有限，选择文档约定分支 |
| `agate/scripts/agate_common.py` | **明确不改**（§1 候选 B1 采纳理由）：`AGATE_TDD_TIMEOUT` 消费逻辑保持不变，P3 继续走既有 env var 机制 |
| `agate/scripts/agate-frontmatter-check.py` | 不入 schema：`timeout_seconds` 是 `gate_commands` 块内的自由 YAML 子字段（沿用 `dispatch_plan` 同类先例），不改动现有 P2 frontmatter schema 校验 |
| `agate/.state.yaml` schema / `state-machine.md` `env_state` 字段语法 | 不新增字段（§1 候选 A 采纳理由：止损轮次独立计数不落盘 `.state.yaml`）；`env_state` 现有字段语法不变，只在 verification_env 职责边界子节建立引用关系 |
| `agate/WORKFLOW.md` / `adr.md` | P1 第 0 节第 5 点已核实为结构性引用，不消费 P0-brief 四字段具体内容，不需要因 RM-AG0019 改动 |
| `agate/loop-orchestration.md`、既有测试文件（`test_check_gate.py`/`test_dispatch_orchestration.py` 等） | 不改，只跑回归确认；`check-protocol-consistency.py` 扫描面（`PROTOCOL_FILES`/`PROTOCOL_DIRS`）已覆盖全部改动文件，不需要扩展 consistency-reviewer 校验规则本身（P1 §7 范围外观察已排除） |
| `agate/scripts/*.sh`（3 个 hook 薄壳） | RM-AG0016 判断不改，仅 shellcheck 回归确认（P0-brief 已定性） |

### 2.3 风险在哪（Risk）

| 风险 | 缓解 |
|------|------|
| 同一文件被不同 BDD 分组重复改动，本任务自己犯"改一处漏同类"的反模式 | §2.1 表逐条对齐 P1 11 个文件分组，未拆散重组；`dispatch_plan` 按文件边界分批（§5），不跨批次二次改同一文件 |
| 协议正文引用误写成硬编码行号（`xxx.md L123`），触发 CHECK3-lineref ERROR | §0 已核实 CHECK3 扫描面覆盖全部改动文件；§2.1 所有"引用式"改动点均已用节标题措辞（"引用 dispatch-protocol.md「派发编排机制」并行规则"）而非行号，写入 files_to_read 备注提醒 P4 |
| `dispatch-protocol.md` 权威源与 `dispatch-prompt.md` 副本双源漂移（P1 隐含需求 3） | BDD-14 独立验收条件（两文件同含新段落且不矛盾）；`check-protocol-consistency.py` 既有一致性检查口径覆盖这两处文本 |
| verification_env 止损轮次无脚本强制，主 Agent 可能漏记轮次 | 已在 §1 候选 A 缺点中显式承认，属范围约束（不新增 `.state.yaml` 字段）下的合理取舍；后续任务若发现漏记频发，可作为新 RM 提出（不在本任务范围内解决） |
| `timeout_seconds` 三档基准表被误当作自动推断规则（P4/未来任务照抄样例时忽略是"建议档位需手动声明"） | `task-files.md` 样例块注释显式标注"建议档位，需按命令类型手动声明，非自动推断"；BDD-21 联动要求样例块 P3 key 处附引用指向 §1 候选 B 说明 |
| P0-brief 漂移 checklist（§1 候选 C）3 条判据仍需一定经验判断，边界案例可能被误判轻微/严重 | 已在候选 C1 缺点中承认边界主观性上限；checklist 已把判断收窄到 3 条清单内，比"看情况"更可判定，属可接受改进幅度 |
| SELF-GATE 触发（本任务改动面广，`agate/*.md`+`scripts/*.py`+`phase-cards/*`） | commit message 按 AGENTS.md 约定含 `self-gate-review:`/`self-gate-skip:`；每次协议文档 commit 前跑 `check-protocol-consistency.py --strict` 确认 0 ERROR（P0-brief 约束 1 的回归底线） |

## 3. 方案设计细化

### 3.1 verification_env 失败处理协议

见 §1 候选方案 A 采纳文本（1-4 条规则），落点 `dispatch-protocol.md` verification_env 节。

### 3.2 timeout_seconds 字段规范 + 命令级超时兜底（层级 4）

见 §1 候选方案 B 采纳文本（关系判定/声明粒度/三档基准表/向后兼容）+「关联决定」段（×1.5 倍规则）。

### 3.3 环境准备职责边界（BDD-11/18/19/20）

具体条款（供 P4 落地到 dispatch-protocol.md verification_env 节的子节）：

1. 环境的启动/维护/关停默认归主 Agent（或 P0-brief 显式声明的单一责任方），subagent 默认只消费不自行启动
2. 多个并行 subagent 需要访问同一环境时，由主 Agent 统一启动后通过 dispatch-context 注入访问方式，不允许各 subagent 各自启动导致冲突/资源竞争
3. 该子节与 `.state.yaml` 的 `env_state` 字段（state-machine.md 已有定义：`debug_backend`/`test_entry_slug`/`env_verified_at`）建立引用关系，不重复定义 `env_state` 字段语法

P5/P6/verifier.md 三处落地方式一致：**引用**本条款，不重复展开（BDD-18/19/20 的"落地引用"模式，避免"权威定义 + 卡片引用"惯例被破坏）。

### 3.4 P0-brief 漂移判据

见 §1 候选方案 C 采纳文本（严重 3 条 / 轻微 2 条 + 判定流程），落点 `P0-orchestrator.md` + `P1-requirements.md`（卡片）+ `state-machine.md` L77 上下文。

### 3.5 RM-AG0013 同类扫描/影响面梳理落地（follows_existing_pattern，轻设计）

`follows_existing_pattern: [agate/dispatch-protocol.md「派发编排机制」小节结构]`——沿用既有"新增小节，可被固定关键词 grep 命中"惯例（analyst.md「隐含需求清单」维度并列格式、dispatch-protocol.md 各权威节的标题+段落结构）。5 处落点（P0 卡/P1 卡/analyst.md/P2 卡/architect.md）各自的确切关键词见 §2.1 表最后一列，P4 实现时须逐字使用该列关键词（不得意译替换），因为 §3.6 的 grep 断言审计测试按这些关键词硬编码断言。

### 3.6 grep 断言审计测试设计（BDD-22 强制项，无论分支都需要）

新建 `agate/tests/unit/test_protocol_mechanism_anchors.py`，组织方式参照 `agate/tests/unit/test_check_protocol_consistency.py`（该文件读取脚本内 `SCRIPT_ALIGNMENT_ANCHORS` 表逐条断言，本测试改为对协议文档文件本身做关键词存在性断言，不涉及被测脚本逻辑）：

- 结构：一个 `ANCHOR_TABLE`（文件路径 → 关键词列表），每条 `(file, keyword)` 组合生成一个 `pytest.mark.parametrize` 用例，断言 `keyword in file_text`
- 覆盖范围：§2.1 表最后一列列出的全部关键词锚点（覆盖 BDD-1~21，共 21 条有独立关键词的 BDD；BDD-15b/19/20 为"引用式"落地，断言其"引用词"而非重复展开的完整规则文本；BDD-22 自身以"本测试文件存在且全部用例通过"为验收标准，不需要额外关键词断言）
- 平台无关：纯文本 `in` 判断，不依赖 shell/grep 二进制，Windows/Linux 行为一致（覆盖 `windows_smoke` 标记）
- TDD 红→绿：P3 阶段先写好该测试（此时关键词均未落盘 → 全红），P4 阶段逐条实现协议文档改动使其转绿——这正是 P0-brief"批量机械改动的 TDD 策略"要求的"先写一个 grep 断言审计测试作为回归拦截"

### 3.7 BDD-22 分支决定：不做脚本硬校验，仅文档约定 + grep 断言审计测试

**决定**：`check-gate.py` 不新增 `timeout_seconds` 校验函数。

**理由**：
1. `timeout_seconds` 对 P5/P6 目前无运行时消费方——P5/P6 由 subagent 自己跑 `gate_commands.{key}` 命令并观察结果，`check-gate.py` 不是命令执行器，不像 P3 有 `run_test_with_formatter()` 那样"读字段→施加真实 subprocess timeout"的消费链路
2. 若强行加脚本校验，只能做到"数值合法性"级浅校验（类似 `_gate_p2_dispatch_plan` 对 `parallel_limit` 的 `int ≥1` 校验模式），但一个格式合法却没有代码读取它去真正生效的字段，校验收益有限，且会增加 `check-gate.py` 复杂度/测试面，与 P0-brief"少量脚本 schema 字段"定性不完全匹配（"少量"更贴合"文档约定优先"）
3. BDD-22 明确"两种结果都是合法收敛"，选择文档约定分支，把回归拦截压力转移到 §3.6 的 grep 断言审计测试（P1 已强制要求，无论 BDD-22 走哪个分支都需要）

## 4. BDD 覆盖映射（23 条全量）

| BDD | 设计方案落点 |
|-----|------------|
| BDD-1 | §2.1 P0-orchestrator.md：新增"同类/影响面预判"节 |
| BDD-2 | §2.1 P0-orchestrator.md：推进条件新增时效性自检项（引用 §3.4） |
| BDD-3 | §2.1 state-machine.md L77：新增时效性校验说明段（引用 P0 卡规则） |
| BDD-4 | §2.1 P1-requirements.md 卡：新增"同类扫描"强制节 |
| BDD-5 | §2.1 P1-requirements.md 卡：verification_env vs supplementable 边界判断树 + 轮次预算占位声明位 |
| BDD-6 | §2.1 P1-requirements.md 卡：`[P0_STALE:]` 标记规则 + 阻塞/记录二选一说明 |
| BDD-7 | §2.1 analyst.md：隐含需求清单新增"同类/影响面"维度 |
| BDD-8 | §2.1 analyst.md：supplementable vs verification_env 判断树（"缺的是能力还是环境？"） |
| BDD-9 | §2.1 analyst.md：P0-brief 时效性质疑步骤 |
| BDD-10 | §1 候选 A + §3.1：verification_env 失败处理协议 4 条规则 |
| BDD-11 | §1 候选 A 关联 + §3.3：环境准备职责边界子节 |
| BDD-12 | §1 候选 B 关联 + §2.1：并行规则新增"资源密集型默认串行" |
| BDD-13 | §1 候选 B 关联决定 + §2.1：命令超时兜底 + progress 标准段（层级 4，×1.5 倍）+ L521 条件性子句判定不适用 |
| BDD-14 | §2.1 dispatch-prompt.md：同步 BDD-13 段落 |
| BDD-15 | §2.1 P2-design.md 卡：新增"影响面梳理"强制节 |
| BDD-15b | §2.1 architect.md：批次设计节新增检查项，引用 BDD-15 不重复展开 |
| BDD-16 | §1 候选 B + §3.2：P2 卡 + architect.md 新增 `timeout_seconds` 规则位（4 点全部回答） |
| BDD-17 | §2.1 P5-verification.md 卡：引用"资源密集型默认串行"（BDD-12） |
| BDD-18 | §2.1 P5-verification.md 卡：落地"环境准备职责边界"（§3.3） |
| BDD-19 | §2.1 + §3.3 verifier.md：改为引用 dispatch-protocol.md 权威定义，不重复展开 |
| BDD-20 | §2.1 + §3.3 P6-acceptance.md：落地"环境准备职责边界"引用 |
| BDD-21 | §2.1 task-files.md：`timeout_seconds` 样例块（三处命名一致 + P3 key 关系引用） |
| BDD-22 | §3.6 + §3.7：grep 断言审计测试（强制）+ 不做脚本硬校验的决定与理由 |

## 5. 批次设计（`dispatch_plan`，工作量五维评估）

### 5.1 五维评估结论

| 维度 | 评级 | 依据 |
|------|------|------|
| 产出规模 | **high** | 直接改动文件 = 13 个（phase-cards×5 + dispatch-protocol.md + state-machine.md + execution-roles×3 + templates×2 + scripts 测试新增 1），>6 个文件 |
| 输入规模 | **high** | P2 自身输入已 7 个文件（P1-requirements.md/P0-brief.md/dispatch-protocol.md/state-machine.md/architect.md/TAG0014 参考/AGENTS.md），P4 阶段每个批次仍需读取本设计 + 对应协议节现状，>5 个 |
| 改动性质 | **high** | 跨模块改动：phase-cards / dispatch-protocol / state-machine / execution-roles / templates / scripts 六类文件同时改，新增字段（schema 变更） |
| 耦合度 | **high** | 与 ≥3 个模块耦合（跨 6 类文件的交叉引用密度高，P1 §5 已定级 `risk_level: high` 的同一理由） |
| 认知负荷 | **high** | 需读全貌才能动手：三类新增机制设计 + TAG0009/TAG0008/TPV0093 三段历史教训 + 避免"权威源/副本双源漂移" |

**综合定级：high**（任一维 high → 整体 high）。按 architect.md「批次设计（强制节）」硬规则"high 复杂度必须拆分，不允许单发"——**必须声明 `dispatch_plan`**。

### 5.2 编排模式选择

选 `mode: static-batch`（非 `recon-then-split`）：P1 已完成"侦察"工作——11 个文件分组 A-K 边界清晰、互不重叠（P1 §组织原则已明确"避免同一文件被后续阶段分批改多轮"），不需要再派侦察 subagent 重新理解结构。本设计在 P1 的 11 组基础上合并为 8 个批次（详见 §5.3），主要用于 **P4 实现阶段**的拆分依据；P3（仅 1 个新测试文件）、P5/P6（单个 verifier 跑全量回归 + consistency，非并行受益场景）按「全阶段适用表」默认走**模式 1（单发）**，不复用本批次表。

### 5.3 批次表与执行顺序（8 批，`parallel_limit: 8`）

批次边界严格对齐 §2.1 改动落点表的文件分组，不拆散/不跨批次二次改同一文件：

| 批次 id | 覆盖文件（输出） | BDD | 复杂度 |
|---------|----------------|-----|--------|
| `p0-p1-state-scan` | P0-orchestrator.md + P1-requirements.md卡 + state-machine.md | BDD-1,2,3,4,5,6 | low |
| `analyst-role` | analyst.md | BDD-7,8,9 | low |
| `dispatch-protocol-core` | dispatch-protocol.md（verification_env 节 + 并行规则 + 派发prompt模板正文，三处新机制原文） | BDD-10,11,12,13 | **high**（内容量最大，三类新机制原文均在此文件） |
| `dispatch-prompt-sync` | dispatch-prompt.md | BDD-14 | low |
| `p5-refs` | P5-verification.md卡 | BDD-17,18 | low |
| `p6-verifier-refs` | P6-acceptance.md卡 + verifier.md | BDD-19,20 | low |
| `p2-architect-timeout` | P2-design.md卡 + architect.md | BDD-15,15b,16 | medium |
| `task-files-schema` | task-files.md | BDD-21 | low |

> `test_protocol_mechanism_anchors.py`（BDD-22）不计入批次表——它是 P3 阶段先行产出（TDD 红），P4 各批次落地后由主 Agent 统一跑该测试确认转绿，不属于"并行实现批次"。

**执行顺序（依赖关系，`dispatch_plan` schema 无 `depends_on` 字段，此处以 prose 声明，供 P4 派发时的主 Agent 参考，非 gate 强制）**：

- **Wave 1（无相互依赖，可并行）**：`p0-p1-state-scan` / `analyst-role` / `dispatch-protocol-core` / `p2-architect-timeout` —— 四者互不引用彼此新增内容
- **Wave 2（依赖 `dispatch-protocol-core` 先落地，因为要引用其新增的节标题）**：`dispatch-prompt-sync` / `p5-refs` / `p6-verifier-refs`
- **Wave 3（依赖 `p2-architect-timeout` 先落地 `timeout_seconds` 字段规则）**：`task-files-schema`

`parallel_limit: 8` 与批次总数一致（满足 `check-gate.py` 的 `批数 ≤ parallel_limit` 校验），不代表 8 批全部同时并发派发——实际派发遵守上方 wave 顺序 + dispatch-protocol.md「并行规则」默认并行上限 3 的惯例（同一 wave 内如超过 3 批，仍需分轮次派发）。

## 6. 四字段声明

### gate_commands

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
```

> P0-brief `test_cmd` 三件套（pytest / consistency --strict / count-tests.sh）全部纳入 P5，`shellcheck` 作为本任务定性"RM-AG0016 判断不改 .sh，仅回归确认"的验证项一并纳入。P5_e2e 不需要（`ui_affected: false`）。P3 用 verbose 输出（`-v`，非 `-q`），与既有惯例（"P3 verbose 区分 A/B 类错误，P5 紧凑判过没过"）一致——本测试文件失败信息本身就是"哪个关键词没落盘"，verbose 输出直接可用。

### env_constraints

```yaml
env_constraints:
  debug_env: "Linux；本环境无法实测 Windows，靠 CI matrix（pytest -m windows_smoke）兜底，不宣称已实测 Windows"
  isolation_check: "grep 断言审计测试为纯文本匹配，无外部系统/网络/浏览器依赖，天然平台无关；worktree 与主 checkout/~/.agate 双工作区隔离（改代码在 worktree，跑 gate 用 ~/.agate 稳定版，check-protocol-consistency.py 必须用 worktree 自己的脚本——见 HANDOFF-TAG0012.md 第 2 节）"
  consistency_strict: "每次协议文档 commit 前跑 python3 agate/scripts/check-protocol-consistency.py --strict（worktree 自己的脚本），0 ERROR 才可提交；当前基线已验证 0 ERROR"
```

### files_to_read

```yaml
files_to_read:
  - path: agate/dispatch-protocol.md:643-762
    why: 「派发编排机制」权威节（五维评级/五模式/并行规则/全阶段适用表），BDD-12 新增第4条规则的插入点；本文件本身也是 §5 批次表的设计参照
  - path: agate/dispatch-protocol.md:429-500
    why: 「派发 prompt 模板」规范正文，BDD-13"命令超时兜底+progress"标准段插入点
  - path: agate/dispatch-protocol.md:940-960
    why: verification_env 条件化节现状，BDD-10/11 扩展点（失败处理协议+职责边界子节）
  - path: agate/dispatch-protocol.md:780-879
    why: 「Playwright/长时操作 subagent 派发策略」层级2既有硬超时机制（HARD=90s/180s），BDD-13 需要显式区分"层级4"不与之混淆
  - path: agate/dispatch-protocol.md:503-524
    why: 「非阶段产出的路径规范」L521 示例块，BDD-13 条件性子句判定该场景不适用命令超时兜底的落点
  - path: agate/state-machine.md:70-80
    why: P0->P1 转移条件文本（L77），BDD-3 新增时效性校验说明段的插入点
  - path: agate/state-machine.md:300-320
    why: env_state 一致性验证既有步骤，BDD-11 环境准备职责边界子节需与之建立引用关系（不重复定义字段语法）
  - path: agate/assets/execution-roles/analyst.md
    why: BDD-7/8/9 三处插入点定位（「隐含需求清单」/「三态判断规则」/「输入」节）
  - path: agate/assets/execution-roles/verifier.md:245-262
    why: verification_env 条件化节现状，BDD-19 改为引用式写法的落点
  - path: agate/phase-cards/P5-verification.md:108-128
    why: 「按包拆分并行」节现状，BDD-17/18 插入点
  - path: agate/assets/templates/task-files.md:255-290
    why: gate_commands 权威 schema 样例块，BDD-21 timeout_seconds 示例插入点
  - path: agate/scripts/agate_common.py:395-425
    why: run_test_with_formatter() + AGATE_TDD_TIMEOUT 既有消费逻辑，§1 候选B「排除P3」决定的代码证据
  - path: agate/scripts/check-protocol-consistency.py:272-292
    why: CHECK3 硬编码行号引用检查（check_line_refs），确认所有新增跨文件引用文本必须用节标题不能用 "xxx.md L123"（§0 已验证，P4 落地时须遵守）
  - path: agate/rules/state-transitions.md:55-70
    why: 既有重试上限表（P1/P2 MAX=3，P3/P5/P6/P7/P8 MAX=2），§1 候选A"止损轮次=2"设计时的参照基准
  - path: agate/tests/unit/test_check_protocol_consistency.py:1-40
    why: grep 断言审计测试的组织范式参照（§3.6 新建 test_protocol_mechanism_anchors.py 沿用同类结构）
  - path: agate-workspace/tasks/TAG0014-dispatch-orchestration/P2-design.md
    why: 同类协议机制批量任务的已完成 P2 设计范式（按设计维度分候选方案 + 逐文件改动落点表 + dispatch_plan 声明方式），本设计组织结构直接借鉴
```

### minimal_validation

```yaml
minimal_validation:
  assumption: "纯代码逻辑，无外部系统依赖——本任务是协议文档改动 + 新建1个纯文本grep断言测试文件，不涉及浏览器/网络/外部系统行为"
  method: |
    依赖的内部函数/数据结构（已通过读代码验证，非凭空假设）：
    1. agate_common.py:395-425 run_test_with_formatter() 的 AGATE_TDD_TIMEOUT 消费逻辑
       —— 确认 P3 层超时机制的实际消费路径，支撑 §1 候选B「排除P3」决定
    2. check-protocol-consistency.py:272-292 check_line_refs()（CHECK3）+ :54-67 PROTOCOL_FILES/PROTOCOL_DIRS
       —— 确认本任务全部改动文件（dispatch-protocol.md/phase-cards/execution-roles/templates/state-machine.md）
          均在协议文件扫描面内，新增跨文件引用文本若含硬编码行号会被判ERROR，已据此约束§2.1所有"引用式"
          改动点的措辞（节标题引用，非行号引用）
    3. check-gate.py:516-556 _gate_p2_dispatch_plan()
       —— 读取 dispatch_plan 校验实现（mode枚举/parallel_limit≥1/batches字段/批数≤parallel_limit），
          确认本设计frontmatter声明的 dispatch_plan 值（mode: static-batch, parallel_limit: 8, 8个batch）
          能通过该函数校验（8≤8满足"批数≤parallel_limit"；mode∈合法枚举；每batch含id+complexity∈{low,medium,high}）
    4. test_check_protocol_consistency.py:1-40 的测试组织模式（importlib加载模块+parametrize断言）
       —— 确认新建 test_protocol_mechanism_anchors.py 可采用更简单的"直接读文件文本+in判断"模式（比
          test_check_protocol_consistency.py的"加载脚本模块读常量表"更轻量，因为本测试断言对象是文档文本
          本身而非脚本内部数据结构）
  result: "confirmed"
  note: |
    ① AGATE_TDD_TIMEOUT 机制确认只服务 run_test_with_formatter()，P3/check-tdd-red.py 专属，无
       跨阶段复用逻辑——支撑"排除P3"不会遗漏其他消费点。
    ② CHECK3-lineref 的正则 `([A-Za-z0-9_\-]+\.md)\s+L\d+(?:-\d+)?` 会命中任何 "xxx.md L123" 模式，
       本设计§2.1表中所有"引用"措辞已手工核对不含此模式（用"「节标题」"代替）。
    ③ _gate_p2_dispatch_plan 对 batches 的校验是 `len(batches) > limit` 才报错，8个batch+parallel_limit:8
       为 8>8 不成立，校验通过（若未来该字段实际值调整，需同步保持 batches数≤parallel_limit）。
    ④ 本任务不改 check-gate.py（§3.7决定），dispatch_plan 字段本身的读取/校验逻辑复用 TAG0014 已实现的
       既有 _gate_p2_dispatch_plan，无需新增代码。
    结论：核心假设全部 confirmed，方案无需外部系统依赖验证，可直接进入 P3 TDD（先写
    test_protocol_mechanism_anchors.py 确认红灯）。
```

## 7. 实现完成标志

供 P3 测试设计 / P5 验证 / P6 验收判定"做到什么程度算完成"：

1. **verification_env 失败处理协议完成**：dispatch-protocol.md verification_env 节含可/不可重试清单、批处理要求、止损轮次=2独立计数、READY后三条归属判据（BDD-10）+ 环境准备职责边界子节（BDD-11）
2. **timeout_seconds 字段完成**：P2-design.md 卡 + architect.md + task-files.md 三处一致新增 `{key}_timeout_seconds` 字段规则（per-key声明/三档基准表/向后兼容/排除P3关系说明），三处命名一致（BDD-16, BDD-21）
3. **P0-brief 漂移判据完成**：P0卡 + P1卡 + state-machine.md 三处含严重3条/轻微2条判据 + `[P0_STALE]` 标记规则（BDD-2, BDD-3, BDD-6, BDD-9）
4. **RM-AG0013 同类扫描机制完成**：P0/P1/P2 三张卡 + analyst.md/architect.md 五处各自含对应关键词锚点（BDD-1, BDD-4, BDD-7, BDD-15, BDD-15b）
5. **RM-AG0016 运行时管控完成**：dispatch-protocol.md + dispatch-prompt.md 双源同步含"命令超时兜底+progress"段（×1.5倍规则），并行规则新增"资源密集型默认串行"，P5卡引用落地（BDD-12, BDD-13, BDD-14, BDD-17）
6. **环境准备职责边界落地完成**：verifier.md 改为引用式，P5/P6卡各含落地引用句（BDD-18, BDD-19, BDD-20）
7. **测试完成**：`test_protocol_mechanism_anchors.py` 全部 parametrize 用例转绿；全量 pytest 全绿；`count-tests.sh` 计数含新测试文件（BDD-22）
8. **一致性完成**：`check-protocol-consistency.py --strict` 0 ERROR（含 CHECK3 无硬编码行号引用）
9. **BDD-22 决定落盘**：本文件 §3.7 显式声明"不做脚本硬校验"的决定与理由，作为该 BDD 的通过标准

## 8. [SCOPE+] 声明

无新增隐含需求。§0 影响面梳理 + §1 三个候选维度的 grep/读代码核实均未发现 P1 未列出的必须做的事；`check-gate.py` 明确决定不改（§3.7）属于"范围收窄"而非"范围扩大"，不触发 `[SCOPE+]`。
