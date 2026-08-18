---
phase: P1
task_id: TAG0012-protocol-mechanism-fixes
type: problems
parent: P0-brief.md
trace_id: TAG0012-P1-20260818
status: draft
created: 2026-08-18
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]
domains: [process]
capability_requirements:
  - need: python3-runtime
    why: 跑 gate 脚本（check-gate.py / agate-frontmatter-check.py）、pytest 全量回归、check-protocol-consistency.py --strict
    available:
      - "系统 python3（3.12.3）+ pyyaml + pytest 9.0.3（worktree 基线已验证 865 全绿）"
    status: available
  - need: grep-rg
    why: 本任务自身的同类扫描核实 + P6 验收阶段对协议文档新增节的二值锚点判定
    available:
      - "系统 grep / rg"
    status: available
  - need: shellcheck
    why: 若 RM-AG0016 改动触及 .sh 薄壳（当前判断不改，仅回归确认），AGENTS.md 约定的常规检查项
    available:
      - "系统 shellcheck（HANDOFF-TAG0012.md 确认已装）"
    status: available
---

[PROD_NOT_TOUCHED]

# P1 需求基线 — agate 协议机制增强批（RM-AG0013/RM-AG0014/RM-AG0019/RM-AG0016）

> 本文件是需求基线，后续阶段（P2-P8）不应直接修改。变更需主 Agent 显式批准 + `[BASELINE_CHANGE: 理由]` 标注。

## 0. 同类扫描核实结论（在 objective_info 起点基础上自行补充深挖）

dispatch-context 的 objective_info 提供了起点覆盖面（关键词零命中/命中文件清单）。以下是 analyst 自行补充核实、objective_info 未覆盖的同类发现，均已实际读取源码/协议文件验证，直接影响下方 BDD 的落点与边界声明：

1. **timeout 概念在协议里已有三层既有机制，RM-AG0016 是"补第四层"，不是从零设计**——必须在文档里显式区分层级，否则会与既有机制重复定义甚至冲突：
   - 层级 1（P3 测试命令超时）：`agate/scripts/agate_common.py::run_test_with_formatter()` 已有 `AGATE_TDD_TIMEOUT`（默认 120s，env var）机制，被 `check-tdd-red.py` 消费。
   - 层级 2（P6 Playwright 脚本内部超时）：`dispatch-protocol.md` L790-879「Playwright/长时操作 subagent 派发策略」已有"脚本内部硬超时（HARD=90s/180s）+ `lastStep` 上报 + exit code 语义（0/1/2）"机制——这是 **subagent 内部脚本自己的超时**，不是 TPV0093 遇到的"subagent 派发的 bash 命令本身（`cat`/`make test-quick`）挂起"。
   - 层级 3（Task 工具级 subagent 未返回）：`state-machine.md` `.state.yaml` `retries[Pn]` 已有 `failure_mode: timeout` 枚举——这是**整个 subagent 任务未返回**的分类，不是"subagent 存活但内部某条 bash 命令挂起"。
   - **层级 4（本任务要补的空白）**：subagent 存活、正在执行某条 bash 命令、命令本身无超时兜底导致挂起（TPV0093 的 `cat` 挂 3.1h / `make test-quick` 挂 188min 正是此层级）。RM-AG0016 的 `timeout_seconds` 字段 + dispatch-prompt "命令超时兜底" 节要解决的正是这一层。
2. **`gate_commands`/`dispatch_plan` 的权威 schema 定义实际落在 `agate/assets/templates/task-files.md`**（L266 起的 YAML 样例块），不只在 `agate/phase-cards/P2-design.md` 卡片正文——`timeout_seconds` 若新增为 `gate_commands` 的可选子字段，`task-files.md` 的样例块必须同步，否则新任务照抄旧样例会漏字段（见文件分组 J）。
3. **`dispatch-protocol.md` L643-762「派发编排机制」权威节已由 TAG0014（RM-AG0016 前身工作）建立**（五维评级/五模式编排/并行上限默认 3/全阶段适用表），当前"并行规则"子节已覆盖"数据依赖"维度的并/串行判断，但**没有"资源竞争"维度**（CPU/IO 密集型任务即使无数据依赖也可能不该并行，如 3 个 verifier 各跑全量 pytest xdist）。RM-AG0016 的"资源密集型默认串行"是在此既有权威节上的**补充点**，不是新建一节——写 BDD 时必须明确"扩展第 4 节，不新增第 6 节"，避免与 TAG0014 已完成内容重复。
4. **`.state.yaml` 已有 `env_state` 字段**（state-machine.md L424-429：`debug_backend`/`test_entry_slug`/`env_verified_at`）记录运行时环境状态，但**没有记录"谁启动/谁维护/谁负责关停"**——RM-AG0014 环境准备职责补充应该是在这个既有字段的语义说明旁边补"职责人"规则，不是另建新字段。
5. **`WORKFLOW.md` / `adr.md` 对 P0-brief 的引用是结构性引用**（"P0 阶段职责是写 P0-brief"、"P0-brief 完成是 gate 判据"），核实后确认它们**不消费 P0-brief 四字段的具体内容**做时效性判断，只是在描述"这个阶段产出这个文件"。因此 RM-AG0019 的落点不需要触达这两个文件——纳入本次范围会违反 P0-brief 约束 3/4（不得扩大范围），已排除，详见第 7 节「范围外观察」的反向说明。
6. **`check-gate.py` 当前无 `_gate_p0` 函数**——P0 阶段完全靠 `P0-orchestrator.md`「推进条件」的人工 checklist 把关，没有脚本化 gate。这直接决定 RM-AG0019 的 P0→P1 前提校验若沿用同一模式（人工自检清单增补一项），则不强制新增脚本、P3 不适用于这部分；若 P2 设计阶段决定改为脚本硬校验，则触达 `check-gate.py`，P3 适用。本 P1 在「裁剪说明」节写明判断依据，不代 P2 拍板具体实现方式。

## 1. 需求复述

把 P0-brief 已核实的 5 条协议机制缺口翻译为结构化需求，**按受影响文件分组**（P0-brief known_risks 已指出五条改动面高度重叠，避免同一文件被后续阶段分批改多轮）：

| RM 编号 | 一句话缺口 | 修复性质 |
|---------|-----------|---------|
| RM-AG0013 | P0/P1/P2 阶段卡均无"同类扫描/影响面梳理"要求 | 补机制层缺失节 |
| RM-AG0014（主体） | verification_env（环境依赖声明）与 supplementable（能力缺失三态）边界混用；verification_env 无"验证失败后怎么办"协议 | 补边界注 + 补新机制（失败处理协议） |
| RM-AG0014（补充） | verification_env 只定义"如何声明"，未定义"谁负责启动/维护/关停" | 补新机制（职责边界） |
| RM-AG0019 | P0-brief 是立项快照，任务搁置重启时前提可能漂移，缺时效性校验 | 补新机制（时效性校验 + 重启判定） |
| RM-AG0016（原 RM-AG0023） | subagent 运行时缺命令级超时兜底 / 资源密集型默认串行判断 / progress 心跳粒度不够 | 补新机制（运行时管控） + schema 字段新增 |

## 2. 隐含需求识别

用户/P0-brief 没有明说、但技术上必须处理的依赖：

1. **RM-AG0016 内部实为两个耦合但独立的机制，必须分开设计和分开落点**：
   - (a) "声明"层：`gate_commands.{key}_timeout_seconds`（P2 固化的期望时长阈值）—— 落点是 P2-design.md 卡片 + task-files.md schema + architect.md。
   - (b) "执行纪律"层：subagent 每次跑 bash 命令前必须设 shell 层 timeout（如 `timeout <n>s cmd` 或等效），命令前写 progress，超时/异常后停止并回报而非自行深挖 —— 落点是 dispatch-protocol.md「派发 prompt 模板」权威节 + templates/dispatch-prompt.md 同步副本。
   - P0-brief 把两者合写成一条 issue，但改动落点、验证方式完全不同（(a) 是 P2 architect 声明的静态字段，(b) 是所有阶段 subagent 的运行时行为纪律），必须拆成独立 BDD，否则 P2/P4 会漏做其中一半。
2. **向后兼容（隐含的"数据"维度）**：本任务不做破坏性 schema 迁移。所有新增字段/新增标记（`timeout_seconds`、`[P0_STALE]`、CI 轮次预算声明位）必须遵循 agate 现有的"presence 语义、缺省不校验、向后兼容"惯例（参照 `dispatch_plan` 字段"缺字段/坏 YAML → gate 跳过校验，行为等同现状"的既有先例）——旧任务的 `.state.yaml`/历史阶段产出文件不因本次改动被判定不合法。
3. **权威源 vs 引用副本必须保持同步（隐含的"多端"维度）**：`dispatch-protocol.md` 是协议权威源，`templates/dispatch-prompt.md` 是同步给 subagent 派发用的副本（文件头已注明"与 dispatch-protocol.md 保持同步，协议文件为权威来源"）。RM-AG0016 的"命令超时兜底"节必须两处同时改，任一方漏改会导致派发行为与协议文档描述不一致——这正是 `check-protocol-consistency.py` 要拦的问题类型，本任务自己不能留这个缺口。
4. **RM-AG0014 失败处理协议的"止损轮次"与既有 retry 预算机制（P5 MAX=2 等）是两套独立计数，需要显式声明关系**：verification_env 失败重试是"环境验证轮次"，不是阶段 retry（`retries[Pn]`）——P2 设计止损规则时必须说明这两套计数是否共享预算，否则会出现"环境重试用光了阶段 retry 预算"的隐性耦合。P1 在下方 BDD 中把这一点列为 P2 必须回答的问题，不代为拍板。
5. **RM-AG0019 的"漂移程度"判定需要边界情形声明**：P0-brief 只举了"全量技术路线切换"（TAG0008 的 .sh→Python 化）这种极端案例，但现实中更常见的是局部漂移（如某个文件路径改了、某个依赖版本升级了）——P2 设计判定标准时必须覆盖"轻微漂移（更新 P0-brief 即可）"与"严重漂移（需重新立项/可行性分析）"两档，不能只写极端案例的处理方式。
6. **同类扫描机制本身的适用范围需要声明**：RM-AG0013 新增的"同类扫描"要求是否溯及既往（要求给已经在跑的其他任务的历史 P0/P1/P2 产出补做同类扫描）？`[SUGGEST: 只对本次改动生效后新派发的任务/新进入的阶段生效，不追溯改造进行中任务已完成阶段的历史产出，理由：追溯会造成大量非本任务范围的返工，且协议变更通常向后生效是 agate 现有惯例（如 v2.0 机器字段对旧任务也是"缺省不阻断"而非强制回填）]`。

## 3. 按文件 → 改动归并的 BDD 验收条件

> 组织原则：先按"改哪个文件"分组，组内按 RM 编号列出该文件承接的具体改动点，避免同一文件在不同 BDD 分组里被分别描述。BDD 全局编号连续（BDD-1 … BDD-22，另有对称补充项 BDD-15b，共 23 条），凡涉及"新增机制设计"（RM-AG0014 失败处理协议 / RM-AG0019 重启判定标准 / RM-AG0016 阈值基准）的 BDD，Then 子句只界定"设计必须回答哪些问题 + 文档里能查到该规则"，不写死具体数值（止损轮次数/阈值秒数由 P2 architect 设计）。

### 文件分组 A：`agate/phase-cards/P0-orchestrator.md`

#### BDD-1: P0 卡新增"同类/影响面预判"节（RM-AG0013）
- Given 主 Agent 在 P0 阶段撰写 P0-brief.md 的 `known_risks` 字段
- When 打开 `agate/phase-cards/P0-orchestrator.md`
- Then 文件中存在一个新增小节，要求主 Agent 在填 `known_risks` 前先做一次"同类/影响面预判"（本次改动历史上是否有过同类问题、可能牵动哪些子系统/文件簇），且该节可被关键词 grep（如"同类"或"影响面预判"）命中

#### BDD-2: P0 卡"推进条件"新增 P0-brief 时效性自检项（RM-AG0019）
- Given 一个已存在 P0-brief.md 但任务被搁置后重新启动的场景
- When 主 Agent 对照 `agate/phase-cards/P0-orchestrator.md`「推进条件」checklist
- Then checklist 中存在一项要求：重启任务时需对照当前项目状态复核 P0-brief 四字段是否仍成立，发现漂移则先更新 P0-brief 或标注 `[P0_STALE]`，而不是直接推进 P1；该项对"首次立项即执行"的任务不构成额外阻塞（presence 语义：无重启场景时该项天然满足）

### 文件分组 B：`agate/state-machine.md`

#### BDD-3: P0→P1 转移条件文本补时效性校验（RM-AG0019）
- Given `agate/state-machine.md` L77 现有转移条件文本 `P0 --[P0-brief.md 完成，四字段自查通过...]--> P1`
- When 读取该行及其上下文
- Then 转移条件文本或紧邻的说明段落中包含"四字段自查"不仅指非空校验，还包含（或引用）时效性校验的要求，且该要求覆盖"任务重启"场景（与 BDD-2 的 P0 卡改动指向同一条规则，不重复定义，state-machine.md 侧只需引用 P0 卡的规则，不重写全文）

### 文件分组 C：`agate/phase-cards/P1-requirements.md`（阶段卡）

#### BDD-4: P1 卡新增"同类扫描"强制节（RM-AG0013）
- Given analyst subagent 在 P1 阶段撰写需求基线
- When 打开 `agate/phase-cards/P1-requirements.md`
- Then 文件中存在一个新增小节，明确要求 analyst 在识别隐含需求时执行一次全仓同类扫描（grep 关键概念/关键词，核实影响面是否超出 P0-brief 已列范围），且该节可被关键词 grep（如"同类扫描"）命中

#### BDD-5: P1 卡新增 verification_env vs supplementable 边界判断指引位（RM-AG0014 主体）
- Given analyst 在 P1 阶段需要判断某个能力/环境缺口该标 `supplementable` 还是声明 `verification_env`
- When 打开 `agate/phase-cards/P1-requirements.md`
- Then 文件中存在一段边界判断指引（可用判断树或对照表形式），明确"能力缺失但有替代获取路径"用 supplementable 三态，"任务依赖特定运行环境（debug server/测试数据库/临时端口等）"用 verification_env 声明，二者不互相替代；同一小节或紧邻位置声明"当任务涉及 verification_env 时，P1 需一并声明环境验证的轮次预算占位"（具体轮次数值由 P2 设计，P1 只要求"有声明位"）

#### BDD-6: P1 卡新增 P0_STALE 标记规则引用（RM-AG0019）
- Given analyst 在读取 P0-brief.md 时发现内容与当前项目状态不一致
- When 打开 `agate/phase-cards/P1-requirements.md`
- Then 文件中存在规则：analyst 发现 P0-brief 过时时，需在 P1-requirements.md 中标注 `[P0_STALE: 具体漂移点]`，该标记的处理路径（阻塞 / 记录后继续）在文档中有明确二选一说明，不是含糊表述

### 文件分组 D：`agate/assets/execution-roles/analyst.md`

#### BDD-7: analyst.md「隐含需求清单」新增"同类扫描"维度（RM-AG0013）
- Given analyst 角色文件现有「隐含需求清单（每次都过一遍这些维度）」列出数据/前端/多端/边界/兼容五个维度
- When 打开 `agate/assets/execution-roles/analyst.md`
- Then 该清单新增一个维度条目（同类/影响面：本次改动是否有历史同类问题？改动是否牵动其他未在 P0-brief 中列出的文件/模块？），与既有五维度并列，格式一致（可被 grep 命中）

#### BDD-8: analyst.md 新增 supplementable vs verification_env 判断树（RM-AG0014 主体）
- Given analyst.md 现有「三态判断规则」节只定义 supplementable 的 available/supplementable/GAP 三态
- When 打开 `agate/assets/execution-roles/analyst.md`
- Then 该节旁新增一段落，明确区分：`capability_requirements` 的 supplementable 三态用于"能力"缺失（技能/工具/skill），`verification_env` 用于"环境"依赖（跑起来需要的外部运行环境），并给出一个可操作的自问句（如"缺的是能力还是环境？"）帮助 analyst 判断，避免重演 TAG0009 的机制误用

#### BDD-9: analyst.md 新增 P0-brief 时效性质疑步骤（RM-AG0019）
- Given analyst.md 现有「输入（自己读取）」节要求读 P0-brief.md
- When 打开 `agate/assets/execution-roles/analyst.md`
- Then 该节或紧邻位置新增一步：读 P0-brief 后，先核对四字段内容是否仍反映当前项目状态（而非只确认非空），发现不一致时标 `[P0_STALE]` 并在需求复述中说明漂移点，再继续需求质疑

### 文件分组 E：`agate/dispatch-protocol.md`

#### BDD-10: verification_env 节扩为"条件化 + 失败处理协议"（RM-AG0014 主体）
- Given `agate/dispatch-protocol.md` L952-957 现有"verification_env 条件化"节只回答"何时需要声明该字段"
- When 打开该节
- Then 节内新增"验证失败后怎么办"的协议内容，且该协议至少显式回答以下问题（具体规则数值由 P2 architect 设计，本 BDD 只验证问题清单是否被完整回答，不验证具体数值）：
  1. 哪些验证失败属于"可通过重试解决"、哪些属于"不可重试需升级人工"（可验证/不可验证清单）
  2. 单轮验证失败时是否要求批量处理多个假设（而非逐个假设单独起一轮）
  3. 止损轮次由谁判定、超过轮次后状态转移到哪（如转 PAUSED）
  4. 若任务已进入 READY 后才暴露环境相关问题，问题归属如何判定（算本任务遗留 or 算环境本身问题）

#### BDD-11: verification_env 节新增"环境准备职责边界"子节（RM-AG0014 补充）
- Given verification_env 目前只定义"如何声明"，未定义"谁负责准备"
- When 打开 `agate/dispatch-protocol.md` verification_env 节
- Then 节内新增子节，明确职责边界至少覆盖：
  1. 环境的启动/维护/关停默认归主 Agent（或 P0-brief 显式声明的单一责任方），subagent 默认只消费不自行启动
  2. 多个并行 subagent 需要访问同一环境时，由主 Agent 统一启动后通过 dispatch-context 注入访问方式，不允许各 subagent 各自启动导致冲突/资源竞争
  该子节与 `.state.yaml` 的 `env_state` 字段（state-machine.md 已有定义）建立引用关系，不重复定义 env_state 的字段语法

#### BDD-12: 「派发编排机制」并行规则新增"资源密集型默认串行"判据（RM-AG0016）
- Given `agate/dispatch-protocol.md` L691-695「4. 并行规则」现有 3 条规则（并行上限默认 3 / 失败批 retry / 共享文件统一后处理），均基于"数据依赖"维度判断能否并行
- When 打开该节
- Then 该节新增第 4 条规则：即使批次间无数据依赖，若单批次任务本身是资源密集型（如全量测试套件在 xdist 模式下跑、CDP/Playwright E2E 浏览器实例），默认判定为串行，需评估 CPU/IO 竞争后才可改并行；该规则是对既有「4. 并行规则」节的追加条目，不新建独立小节，且明确与既有「全阶段适用表」的 P5 行建立引用关系

#### BDD-13: 「派发 prompt 模板」L462「分阶段落盘」规范正文新增"命令超时兜底 + 命令前 progress"标准段，L521 场景示例块按需引用（RM-AG0016）
- Given `agate/dispatch-protocol.md` L429 起「派发 prompt 模板」节 + L462「全阶段通用『分阶段落盘』模板」（规范性主文本）现状：分阶段落盘只要求"读完一个输入文件或完成一个关键步骤后追加 progress"，未要求"每个 bash 命令执行前写 progress"，也无命令级超时兜底要求；L503「非阶段产出的路径规范」节下 L521 起是 self-gate/alignment-review 等非阶段产出场景的**示例代码块**，与 L462 不是同级规范文本，不应被要求并列新增同一段内容
- When 打开 L429/L462 规范正文
- Then（规范正文，必改）新增一段标准指令，至少包含：
  1. subagent 执行的每条 bash 命令必须设置超时（超时时长 ≤ 该命令预期耗时的固定倍数，倍数由 P2 architect 定义具体值，本 BDD 只验证"倍数规则存在"）
  2. 命令超时后 subagent 必须停止执行、写 progress 记录卡在哪条命令，返回主 Agent，不允许自行更换命令或深入诊断
  3. 遇到非预期失败（非超时的报错）同样记录后返回主 Agent 判断，不允许 subagent 自行深入诊断（与既有「写脚本与跑脚本分离」节的"最小修复 vs 重写界限"不冲突，互相引用不重复定义）
  4. 分阶段落盘的粒度从"每个关键步骤"扩展到"每条 bash 命令执行前"
  5. 新增内容须与 L790-879「Playwright/长时操作 subagent 派发策略」既有硬超时机制（层级 2：subagent 内部脚本自己的硬超时，见第 0 节第 1 点）建立显式的文档内引用区分，明确标注本次新增的是"层级 4：bash 命令级超时兜底"，不是层级 2 的替代或重复，避免 P4 implementer/文档读者混淆两层超时机制
- Then（L521 示例块，条件性）：若 self-gate/alignment-review 等"非阶段产出"场景同样存在 bash 命令挂起风险，L521 示例块不重复展开完整规则，改为引用 L462 新增段落（与 BDD-17/BDD-19 的"权威定义 + 卡片/角色文件引用"模式保持一致）；若该场景判定不适用（如场景本身不含长耗时 bash 调用），需在落地时留一句"为何不适用"的说明，不允许留空不处理

### 文件分组 F：`agate/assets/templates/dispatch-prompt.md`

#### BDD-14: 同步 BDD-13 的命令超时兜底 + progress 心跳段落（RM-AG0016）
- Given `agate/assets/templates/dispatch-prompt.md` 文件头声明"与 dispatch-protocol.md「派发 prompt 模板」节保持同步，协议文件为权威来源"
- When BDD-13 在 dispatch-protocol.md 落地后，对照 `agate/assets/templates/dispatch-prompt.md`
- Then 该模板文件中的对应段落（「分阶段落盘」/「执行顺序」节）同步包含与 BDD-13 一致的命令超时兜底 + 命令前 progress 要求，两文件内容不出现矛盾表述（`check-protocol-consistency.py` 的既有一致性检查口径覆盖到这两处文本，不因本次新增内容产生新 ERROR）

### 文件分组 G：`agate/phase-cards/P2-design.md` + `agate/assets/execution-roles/architect.md`

#### BDD-15: P2 卡新增"影响面梳理"强制节（RM-AG0013）
- Given architect subagent 在 P2 阶段设计候选方案
- When 打开 `agate/phase-cards/P2-design.md`
- Then 文件中存在一个新增小节，要求 architect 在设计候选方案前做一次影响面梳理（本方案的改动是否波及 P1 未列出的文件/模块，是否与既有类似机制冲突或重复），且该节可被关键词 grep（如"影响面梳理"）命中

#### BDD-15b: architect.md「批次设计」节同步新增"影响面梳理"检查项，与 analyst.md（BDD-7）对称落地（RM-AG0013）
- Given BDD-15 要求 P2-design.md 卡片新增"影响面梳理"强制节，而 `agate/assets/execution-roles/architect.md`（P2 执行角色文件）现状对"影响面"/"同类"关键词零命中；RM-AG0013 在 analyst.md 侧同时获得"卡片（BDD-4）+ 角色文件（BDD-7）"两处落地，P2 侧此前只有卡片一处，覆盖不对称
- When 打开 `agate/assets/execution-roles/architect.md`「批次设计」节（或语义最接近的既有节）
- Then 该节新增一个检查项，要求 architect 在设计候选方案前引用/执行 P2-design.md（BDD-15）定义的"影响面梳理"要求，不在角色文件内重复展开梳理方法细节（与既有"权威定义 + 角色文件引用"惯例一致，可参照 BDD-19 verifier.md 对 dispatch-protocol.md 的引用模式），使 analyst.md/architect.md 两处角色文件对"同类/影响面"维度的覆盖方式保持对称

#### BDD-16: P2 卡 gate_commands 声明节 + architect.md 批次设计节新增 timeout_seconds 字段规则位（RM-AG0016）
- Given `agate/phase-cards/P2-design.md`「gate_commands 声明」节（现有 P3/P5/P5_e2e 等 key）与 `agate/assets/execution-roles/architect.md`「批次设计」节均不含超时相关字段
- When 打开这两处
- Then 均新增对 `timeout_seconds`（或等效命名的可选子字段）的声明规则，且该规则至少回答（具体阈值基准由 P2 architect 在实际任务中设计，本 BDD 只验证规则框架是否完整，不验证具体秒数）：
  1. 该字段是每条 gate 命令独立声明，还是整个 gate_commands 共享一个默认值 + 可选覆盖
  2. 默认阈值的基准来源是什么（如按命令类型分类：单元测试类 / E2E 类 / 构建类给不同默认档位）
  3. 缺字段时的向后兼容行为（沿用现有 `dispatch_plan` "缺字段/坏 YAML → gate 跳过校验，行为等同现状"惯例，不新增强制阻断）
  4. 新字段是否适用于 `gate_commands.P3` key；若适用，与既有 `AGATE_TDD_TIMEOUT` env var 机制（`agate/scripts/agate_common.py:408`，默认 120s，`check-tdd-red.py` 消费，即第 0 节第 1 点已确认的"层级 1"机制）是互斥（`timeout_seconds` 存在时优先覆盖）、叠加、还是字段本身排除 P3（P3 继续用 env var，`timeout_seconds` 只服务 P5/P6/其他新 key）——具体决定仍由 P2 architect 拍板，本 BDD 只验证"该层级关系问题被文档显式回答"，不预设/写死答案

### 文件分组 H：`agate/phase-cards/P5-verification.md`

#### BDD-17: 「按包拆分并行」节引用"资源密集型默认串行"判据（RM-AG0016）
- Given `agate/phase-cards/P5-verification.md` L113-128「按包拆分并行」节现有"仅当 P2 packages > 1 且包间无依赖时适用"的判据，未覆盖资源竞争维度
- When 打开该节
- Then 该节新增一句引用/补充：全量 pytest（尤其 xdist 并行模式）、frontend 全量 vitest、CDP/Playwright E2E 等资源密集型验证命令，默认判定为串行（即使包间无数据依赖），与 `dispatch-protocol.md` BDD-12 的规则保持引用一致，不在本文件重复展开判据细节

#### BDD-18: P5 卡落地"环境准备职责边界"（RM-AG0014 补充）
- Given P5 verifier subagent 可能需要访问 debug server / 测试数据库等运行环境
- When 打开 `agate/phase-cards/P5-verification.md`
- Then 文件中新增一句明确：P5 verifier 默认不自行启动/维护运行环境，环境由主 Agent 按 `verification_env` 声明统一准备并通过 dispatch-context 注入访问方式；多个并行 verifier 共享同一环境时，遵循 dispatch-protocol.md verification_env 节（BDD-11）定义的统一准备规则，本节只做落地引用

### 文件分组 I：`agate/phase-cards/P6-acceptance.md` + `agate/assets/execution-roles/verifier.md`

#### BDD-19: verifier.md verification_env 引用节补边界注 + 失败处理协议引用（RM-AG0014）
- Given `agate/assets/execution-roles/verifier.md` L252"verification_env 条件化"节现状只描述"何时需要声明该字段"（与 dispatch-protocol.md 近似重复）
- When 打开该节
- Then 该节改为引用 dispatch-protocol.md 的权威定义（BDD-10/BDD-11），不重复展开失败处理协议/职责边界的完整内容，避免"权威定义 + 卡片引用"惯例被破坏（同一内容散落两处、后续改一处漏一处）

#### BDD-20: P6/verifier 落地"环境准备职责边界"（RM-AG0014 补充）
- Given P6 verifier（模式二）可能需要复用 P5 已准备的运行环境，或需要新的环境访问
- When 打开 `agate/phase-cards/P6-acceptance.md`
- Then 文件中新增一句明确：P6 阶段的环境访问沿用 P5 已由主 Agent 准备的环境（若环境状态未变），需要新环境时同样遵循 dispatch-protocol.md verification_env 节的统一准备规则，不由 verifier subagent 自行启动

### 文件分组 J：`agate/assets/templates/task-files.md`

#### BDD-21: gate_commands 权威 schema 样例块新增 timeout_seconds 字段格式定义（RM-AG0016）
- Given `agate/assets/templates/task-files.md` L266 起的 `gate_commands:` YAML 样例块是新任务照抄的权威模板
- When 打开该样例块
- Then 样例块中新增 `timeout_seconds`（或等效命名）字段的格式示例（含注释说明用途与缺省行为），与 BDD-16 在 P2-design.md/architect.md 声明的规则一致，三处（task-files.md 样例 / P2-design.md 卡片 / architect.md 批次设计节）字段命名、语义保持一致，不出现同一概念三种命名
- Then（联动 BDD-16 第 4 点）：若样例块的 `P3` key 下也标注 `timeout_seconds` 示例，该处注释必须附带指向 BDD-16 第 4 点"与既有 `AGATE_TDD_TIMEOUT` 关系"说明的引用，不在本样例块重复展开关系细节，避免新任务照抄样例时忽略这层既有机制冲突风险

### 文件分组 K：`agate/scripts/check-gate.py`（+ 配套 pytest 回归）

#### BDD-22: check-gate.py 校验逻辑按 P2 设计结论决定是否扩展，扩展时须有 TDD 红→绿证据（RM-AG0016）
- Given `agate/scripts/check-gate.py` 当前对 `gate_commands` 只做"字段是否存在"级别的浅校验（P2.61 只检查命令 token 是否可执行，不校验子字段合法性），且全仓 grep `timeout_seconds` 零命中
- When P2 architect 在 BDD-16 的设计中决定 `timeout_seconds` 是否需要脚本硬校验（如格式合法性、数值范围）
- Then 若 P2 决定需要脚本校验：`check-gate.py`（或新增独立校验脚本）新增对应校验函数，且 `agate/tests/` 下有配套 pytest 用例先红后绿（TDD 证据）；若 P2 决定该字段仅作文档约定不做脚本硬校验，则本 BDD 以"P2-design.md 中显式声明该决定 + 理由"为通过标准，两种结果都是合法收敛，不预设哪种一定发生

## 4. 待确认清单

`[NO_NEED_CONFIRM]`

待确认清单为空，无阻塞性未决项。第 2 节列出的 1 条 `[SUGGEST:]`（同类扫描机制不追溯历史产出）方向明确、不涉及破坏性变更/业务判断，主 Agent 可直接采纳。

## 5. 裁剪说明

**不裁剪任何阶段**，`phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]` 全量声明，理由：

- **P2 不可裁**（核心阶段，卡片规则本身不允许裁剪）：RM-AG0014 失败处理协议、RM-AG0019 重启判定标准、RM-AG0016 阈值基准都是"新增机制设计"，必须过 P2 方案设计 + 评审。
- **P3 不裁剪，条件适用**：本任务主体是协议文档变更，但（a）RM-AG0016 的 `timeout_seconds` 明确是"少量脚本 schema 字段"改动（P0-brief 已定性），一旦 P2 决定需要脚本校验（见 BDD-22），必然产生红→绿测试；（b）即使 P2 判定不需要脚本硬校验，AGENTS.md「批量机械改动的 TDD 策略」惯例仍要求为本次大批量协议文档改动写至少一个"grep 断言审计"测试作为回归拦截（验证新增节的关键词锚点确实落盘、且不会被后续任务无意间删除）——本任务自己主张"同类扫描不能只改一处"，若 P3 因"看起来只是文档"被跳过，等于自己犯了要修的反模式。因此 P3 声明为不裁剪，具体测试量级由 P2/P4 按 BDD-22 的分支结论决定。
- **P4 不裁**：文档改动本身也是"实现"，且可能含 check-gate.py 的脚本改动。
- **P5/P6/P7 不可裁**（核心阶段/协议类任务惯例）：协议文档变更必须过 `check-protocol-consistency.py --strict` 0 ERROR（P5/P7 覆盖），且 P6 需要对 23 条 BDD（BDD-1~22 + BDD-15b）逐条给出 PASS/FAIL（grep 锚点验证）。
- **P8 不裁**：需要 bump agate 自身版本号 + CHANGELOG，任务完成后要走正常发布流程（HANDOFF-TAG0012.md 已声明"完成后提 PR 合并 main"）。

**risk_level: high**，理由（按协议类任务惯例定级，非业务破坏性但改动面广）：
1. 改动横跨 6 类文件（phase-cards / dispatch-protocol / state-machine / execution-roles / templates / scripts），单文件改动可能不大，但文件数量和交叉引用密度高。
2. 每次改动 `agate/*.md`、`agate/scripts/*`、`agate/phase-cards/*` 都触发 SELF-GATE（commit message 需 `self-gate-review:`/`self-gate-skip:`），且必须保持 `check-protocol-consistency.py --strict` 0 ERROR。
3. 这些文件是**所有后续任务**（不只是本任务）派发 subagent 时的行为依据——本任务改错或改漏，影响面不止 TAG0012 自己，而是之后所有走 P0-P8 流程的任务。
4. 与 TAG0014（同类协议机制批量任务，`risk_level: high`）的改动广度/性质相当，按同惯例定级。

## 6. 能力需求声明

见 frontmatter `capability_requirements`。本任务是纯文档/协议改动 + 少量脚本 schema 字段，运行环境为 Linux worktree，已验证的 python3/pytest/grep/shellcheck 满足全部验证需求，无需 browser-vision 等特殊能力，Linux 静态修复 + 现有 pytest 回归即可验证协议文档描述与脚本行为一致，不需要真实并发/超时/卡死场景复现（TPV0093 的复盘证据已作为 P0-brief 的既有依据，本任务不重新构造卡死场景）。

## 7. 范围外观察（不纳入本任务 BDD，仅记录供后续参考）

以下是同类扫描中发现的、与本任务相关但**未被 P0-brief 锁定、不擅自扩大范围**的观察：

1. **P7 一致性检查（`agate/assets/execution-roles/consistency-reviewer.md` + `check-protocol-consistency.py`）未扩展去校验本次新增内容的跨文件一致性**（如 P0/P1/P2 三张卡的"同类扫描"关键词是否真的三处都补了、`timeout_seconds` 在 task-files.md/P2-design.md/architect.md 三处命名是否一致）。这类校验属于自然的下一步强化，但 P0-brief 的 known_risks 只锁定 phase-cards/dispatch-protocol/state-machine/execution-roles 四类文件，未提及扩展 consistency-reviewer 的校验规则本身，暂不纳入。
2. **`WORKFLOW.md` / `adr.md` 对 P0-brief 的引用**核实为结构性引用（见第 0 节第 5 点），不需要因 RM-AG0019 改动——记录在此，避免 P2/P4 误判为遗漏同类文件而擅自扩改。
3. **`agate_common.py` 的 `AGATE_TDD_TIMEOUT` 机制**目前只服务 P3（`check-tdd-red.py`），若后续要把 P5/P6 等其他阶段的测试命令超时也统一到同一 env var 机制，是比本任务 `timeout_seconds`（bash 命令级、subagent 执行时动态设置）更大的重构，不在本任务范围，仅作为 P2 设计 `timeout_seconds` 时的参照对象记录。
4. **P0 阶段目前无脚本化 gate（`check-gate.py` 无 `_gate_p0`）**——若 RM-AG0019 之外，将来有需求要给 P0 阶段整体加脚本化 gate，是更大范围的机制变更，不在本任务讨论。
