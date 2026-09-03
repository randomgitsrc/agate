---
phase: P1
task_id: TAG0028
type: problems
parent: P0-brief.md
trace_id: TAG0028-P1-20260903
status: draft
created: 2026-09-03
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
ceremony: standard
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate]
domains: [backend, cli]
---

# P1 需求基线 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P1（需求基线）· 角色：analyst · 日期：2026-09-03
> 上游输入：P0-brief.md · 设计文档 v5（4 轮独立评审闭环）· 三平台数据源实机验证记录 ·
> verify_cmdstream_detection.py（9 场景验证脚本）· dispatch-protocol.md · AGENTS.md
> 本文件是活基线——后续阶段发现的隐含需求（[SCOPE+]）由主 Agent 回写本文件，永远是需求的唯一真相源。

## 1. 需求复述

**一句话任务（P0-brief）**：在 agate 协议层落地 subagent 存活可观测性与受控自主再派发（RM-AG0055）——
命令流日志机制（从三平台会话记录外部获取活动信号，机械检测两类卡死与逻辑空转，检测定位"证据 + 触发核查、不自动判死"）
+ 心跳文件生命周期定义 + 受控自主再派发（执行角色子派发权限下放，judge 类角色例外）。

**范围锁定四 phase（P0-brief scope 原文）**：

| Phase | 内容 | 关键产出 |
|---|---|---|
| **Phase 1 命令流数据源解析层** | 三平台适配器（claude-code / opencode / dsh）+ 统一 CommandRecord IR（platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/output_hash/truncated）+ 适配器注册机制（配置声明或目录扫描 adapters/*.py）+ 解析单测（fixture 取自验证记录） | 适配器代码 + 单测 |
| **Phase 2 检测引擎** | 命令流检测器消费 IR——调用冻结（未结束 call vs expected×2 / 兜底 300s alert + 900s suspect）+ 活动冻结（60s alert + 300s suspect）+ 无效重复（窗口 10 重复 ≥5）+ 截断排除 + 轮询误报标注；阈值全部可配置（maintainability.yaml 模式）；`verify_cmdstream_detection.py` 9 场景全 PASS 保持 | 检测器代码 + 阈值配置 |
| **Phase 3 心跳文件生命周期 + 协议文档** | `.heartbeat` / `.heartbeat.child-{n}` 命名、check-p6-provenance.py 审计豁免确认、任务结束清理 + 异常遗留兜底（复用 agate-archive-stale-outputs 模式）；dispatch-protocol.md 改写 RM-AG0023 progress 心跳扩展节（命令流日志取代存活判定职责，progress.md 保留语义进展职责） | 心跳生命周期规范 + 协议文档改写 |
| **Phase 4 受控自主再派发** | 执行角色（analyst/architect/implementer/verifier）子派发权限下放（两条边界：不写 .state.yaml / 写权限严格子集）；judge 类角色例外声明；dispatch-context 模板补"不启用子派发能力"显式声明（judge） | 权限边界规范 + 模板补节 |

**out-of-scope（P0-brief 明示，本需求不覆盖）**：DSH 心跳钩子机制本身、OpenCode `opencode run` CLI 子进程路线封装、平台食谱产品化、修改 check-gate.py / check-state-transition.py 返回约定、RM-AG0023 全部机制重构、独立 judge 机制本身。

**需求本质**：这不是一个"新增功能"需求，而是**协议机制升级**——把 subagent 存活判定从"依赖 subagent 配合的 progress 心跳（不可验证、卡死时失效）"升级为"外部客观可测的命令流活动信号"，并在此之上开放受控的子派发能力，同时**不破坏既有协议语义**（gate 判定两套信号独立、五模式编排不变、状态机单层不变）。

## 2. 隐含需求识别

按维度逐项过（用户没说但技术上必须的依赖）：

| # | 隐含需求 | 为什么必须 | 归属 |
|---|---|---|---|
| I-1 | **三平台解析必须按适配器模式统一**（每平台一个适配器 → 统一 CommandRecord IR → 检测引擎平台无关） | 三平台存储格式/字段命名完全不同（JSONL / SQLite / JSONL.zstd），解析器不能共用（验证记录 Q2 差异）；检测引擎若依赖平台细节将无法扩展 | Phase 1 |
| I-2 | **Claude Code 与 DSH 无数字 exit code，需文本前缀解析**（`"Exit code N"` / `"Error:"`）并沉淀到 IR 的 exit_signal 留档 | 三平台 exit 信号三种形态（数字字段 / 文本前缀）；仅靠 is_error 布尔无法区分 exit code 数值，文本前缀解析脆弱但当前唯一可行，差异点须沉淀防重复踩坑 | Phase 1 |
| I-3 | **DSH JSONL.zstd 解压不可硬依赖 python zstandard**——本机无该库/二进制；解压须隔离在 dsh 适配器内部（具体解压手段见 capability_requirements 环境事实声明，实现路径留 P2 设计决策） | 交接单 §7 已核实环境事实；拼接帧容器需逐帧解压；若在检测引擎层解压会把平台细节泄漏进平台无关逻辑 | Phase 1 |
| I-4 | **子 agent 会话定位**（Claude Code sidecar `subagents/agent-*.jsonl` / DSH 独立 session 文件 delegationDepth 区分层级）——读主会话文件会漏掉子 agent 记录 | "检测某个具体 subagent 的命令流"需要正确的会话文件；验证记录明确标注此差异 | Phase 1 |
| I-5 | **truncated 输出不参与无效重复哈希比对**（只用于冻结检测） | 两个不同失败被截断成同前缀会误判"无效重复"（验证记录差异点 4）；检测引擎须消费 IR 的 truncated 字段执行排除 | Phase 2 |
| I-6 | **"最后一条命令开始距今"不能作冻结判据**，冻结检测须区分"卡住了 vs 在思考/在跑长命令" | 实测：思考间隙 max≈1239s（20 分钟）、长命令执行 max≈925s（15 分钟）——旧判据会误杀合法状态；须两级冻结（调用冻结看未结束 call vs expected×2；活动冻结看无 call 悬挂时的最后活动事件，三类活动信号思考/输出/工具都算活动） | Phase 2 |
| I-7 | **阈值必须可配置**（maintainability.yaml 模式，缺失/损坏兜底默认值不报错） | 实测命令耗时跨度极大（p50=57ms / max≈196s）；全局固定阈值必误杀；P4/P5 资源密集型阶段需按场景覆盖 | Phase 2 |
| I-8 | **检测结果定位"证据 + 触发核查，不自动判死"**——冻结/空转信号只是客观证据，中止/重派等动作仍由主 Agent 判断 | 设计 §3.4.2 防误杀判据 + P0-brief known_risks（TPV0095 误杀案例）；自动判死会重蹈"误杀仍在工作的 subagent"覆辙 | Phase 2 |
| I-9 | **心跳文件须纳入协议文件系统命名空间管理**（父子分层命名 / 审计豁免 / 清理时机），避免与既有审计脚本冲突 | 心跳文件落盘 `agate-workspace/tasks/` 即进入协议管辖命名空间；不定义生命周期会污染审计与一致性扫描 | Phase 3 |
| I-10 | **两套信号职责分工**：命令流日志承担"存活/卡死"判定（取代 progress 心跳扩展此职责），progress.md 保留"语义进展"职责（正在做什么）不变——dispatch-protocol.md 须同步改写避免两套信号定义漂移 | P0-brief known_risks 第 6 条 + 交接单 §7；TPV0093 实证 progress 心跳在卡死时失效；两套信号若定义漂移则存活判定回归不可验证 | Phase 3 |
| I-11 | **子派发权限下放必须带两条硬边界**（子任务不写 .state.yaml / active-tasks.md；子任务写权限是父 subagent 权限严格子集） | 设计 §4.1——不产生跨层状态外泄，外部观感永远是"一个 subagent 在跑"，状态机单层不变；写权限不收敛会扩大攻击面 | Phase 4 |
| I-12 | **judge 类角色例外必须显式声明**（不开放 Agent/subagent_fork 工具权限，dispatch-context 显式声明"不启用子派发能力"） | judge 的 fresh context 信息隔离与"自主决定查什么"的决策路径开放性存在性质冲突（设计 §4.4 论证）；不显式声明会误开放 | Phase 4 |
| I-13 | **不破坏既有协议语义**：check-gate.py / check-state-transition.py 返回约定不动（心跳判定与 gate 判定两套独立信号）；agate/rules/*.yaml 若增字段须过 JSON Schema + S-1~S-6 双向一致性 gate | P0-brief out-of-scope + dispatch-context 约束 6；破坏返回约定会把存活判定错误地并入 gate 判定路径 | 跨 Phase |
| I-14 | **三平台真实会话片段仅作脱敏 fixture 样例**，不得读取其他用户会话 | env_constraints 明确；DSH 会话文件含敏感命令内容，fixture 须脱敏 | Phase 1 |
| I-15 | **检测输出须平台无关指令**（检测/派发输出平台无关，平台适配由各平台食谱消费） | P0-brief out-of-scope 第 2 条；若检测输出绑定平台工具名，平台食谱无法消费 | Phase 2/4 |

**前端维度**：无 UI/交互变化 → domains 不含 frontend，不声明 ui_render_shape / ui_ux_dimensions，无 UX 类别 BDD。

## 3. 同类扫描结论

按 dispatch-context E 节线索逐条扫描并判定（扫描面：worktree 全仓，含 docs/ 与 agate-workspace/，排除 archived）：

| # | 扫描符号 | 命中清单 | 逐条判定 |
|---|---|---|---|
| S-1 | `存活` / `心跳` / `heartbeat` / `liveness` | **agate/dispatch-protocol.md:951**「Subagent 安全 → 硬超时保护 → 存活检查：真正的存活监控（心跳、文件增长检测）需平台原生支持并发后补，当前为已知限制」；**agate/LIMITATIONS.md:62**（Task 工具暴露 subagent 活动信号…心跳）；docs/design-notes/260903-…（本任务设计文档与评审 v1-v4，属设计源非实现）；TAG0010 系列文件（"存活"为 Python 迁移语境 `关键字必须存活在 py 中`，非存活监控机制） | **本次处理**：dispatch-protocol.md:951 是 Phase 3 改写对象（命令流日志取代"当前为已知限制"的存活判定职责）。**本次不处理**：LIMITATIONS.md:62 是对既有已知限制的陈述，不构成需修复的同类实现（改写 dispatch-protocol 后如措辞冲突再同步，不单独立项）；TAG0010 命中为无关语境。**结论：存活判定职责当前唯一落点在 dispatch-protocol.md「Subagent 安全」节，无第二处实现实例——"只此一处"已核实** |
| S-2 | `progress` 心跳扩展（RM-AG0023） | dispatch-protocol.md:951（同上）；**agate/assets/templates/dispatch-prompt.md:36-38**（分阶段落盘节：每个 bash 命令前写 progress 的指令来源）；**role 文件 6 处**（analyst.md:204 / architect.md:228 / implementer.md:121 / verifier.md:280 / test-designer.md:62 / consistency-reviewer.md:70 的分阶段落盘节）；agate/assets/templates/task-files.md:44（P{N}-progress.md 定义）；TAG0012 P0-brief（RM-AG0023 原始落地记录） | **本次处理**：dispatch-protocol.md「Subagent 安全 → 存活检查」节改写（命令流日志取代存活判定职责）；dispatch-prompt.md 分阶段落盘节**保留不动**（progress.md 语义进展职责不变，但需在改写节中明确边界）。**本次不处理**：role 文件的分阶段落盘节语义不变（progress 心跳的存活职责由协议层改写，role 文件的"写 progress"指令仍是语义进展落盘，不冲突）；task-files.md:44 的 progress.md 定义不变 |
| S-3 | `timeout_seconds` / `_timeout_seconds` | agate/phase-cards/P2-design.md:134-143（`{key}_timeout_seconds` 字段规则：per-key 声明、排除 P3、两层不合并）；agate/assets/templates/task-files.md:275-297；dispatch-prompt.md:43（命令超时兜底取值引用）；agate/assets/execution-roles/architect.md:223 | **本次处理（作为消费方，不改定义）**：检测引擎调用冻结的 expected 复用 RM-AG0023 的 `{key}_timeout_seconds` 声明（expected×2）；字段规则、per-key 语义、排除 P3 均保持，仅新增消费方。**本次不处理**：无其他需要修改的 timeout_seconds 实例 |
| S-4 | `agate-archive-stale-outputs` | agate/scripts/agate-archive-stale-outputs.py（PHASE TASK_DIR，产出 `.archived/{ts}-{phase}` + breadcrumb）；agate/scripts/README.md:106；check-state-transition.py:220/316/328（调用点）；rules/state-transitions.md:74 | **本次处理（复用模式，不改脚本）**：Phase 3 心跳文件异常遗留兜底比照该脚本的任务目录收尾清理模式（"派发前置检查清空"），不新造一套清理机制。**本次不处理**：脚本本身与调用点语义不变 |
| S-5 | `check-p6-provenance.py` 审计豁免 | agate/scripts/check-p6-provenance.py 全文（7 道审计；文件枚举用 os.walk + `if name.startswith("."): continue` 跳过隐藏文件——`.heartbeat*` 以 `.` 开头天然被跳过，line 88-90） | **本次处理（确认并登记豁免）**：落地时在 check-p6-provenance.py 路径过滤逻辑显式确认 `.heartbeat*` 不计入审计范围并登记确认结果（设计 §3.5 要求"不能假设默认不扫就足够，需要可核验记录"）。**本次不处理**：脚本现有隐藏文件过滤逻辑已覆盖，无需改枚举逻辑 |
| S-6 | `dispatch-context` 模板 | agate/assets/templates/dispatch-context.md（56 行模板，含 dispatch_guide 骨架） | **本次处理**：Phase 4 在模板中补"不启用子派发能力"显式声明位（judge 角色派发时使用）。**本次不处理**：模板其余骨架不变 |
| S-7 | `subagent_fork` / 子派发 / 再派发 | role-system.md（全文 grep：无既有子派发权限边界描述，仅评审映射与角色使用骨架）；dispatch-protocol.md（五模式编排 = 主 Agent 层面派发，无 subagent 内部子派发机制）；platform-notes.md:68（Codex 单层任务工具无法再派发——既有平台限制陈述）；platform-notes.md:186 + assets/templates/dsh/SKILL.md:21-23（DSH 派发工具矩阵） | **本次处理**：Phase 4 新增子派发权限边界描述（§4.1 两条边界 + judge 例外）到 role-system.md / dispatch-protocol.md / 执行角色 phase-card；**不产生新编排层级**（状态机单层不变）。**本次不处理**：platform-notes.md:68 的 Codex 限制陈述与 DSH 工具矩阵保持（DSH 工具矩阵已是 subagent/subagent_fork 现状，只补权限边界声明不重写工具矩阵） |
| S-8 | `maintainability.yaml` | agate-workspace/maintainability.yaml（存在：god_file_threshold + fuzzy_patterns）；agate/scripts/check-maintainability.py:89-107（读取 + 缺失兜底）；TAG0026 落地记录（P6 证据 bdd-5.log：配置缺失兜底验证） | **本次处理（复用模式）**：命令流检测阈值按 maintainability.yaml 模式扩展（同文件加节或同模式新键，P2 定），缺失/损坏时兜底默认值不报错——与 check-maintainability.py 既有兜底语义一致 |

**回归拦截声明**：上述 S-1 是"一次性修完的存量"（改写后无新的同类实例）；S-3 的消费方（检测引擎）与 S-5 的豁免登记均为新增，未来新增平台只写适配器（BDD-6 拦截），未来新增存活判定逻辑须走命令流检测引擎（BDD-23 定位原则拦截）——不新增文档约定类拦截（协议改写节本身即约定）。

## 4. BDD 验收条件

每条 BDD 可二值判定（PASS/FAIL），Given/When/Then 结构，编号连续。视角为系统行为（解析器输出 / 检测器判定 / 心跳文件生命周期 / 权限边界行为），不绑定实现函数名。

### 4.1 Phase 1 — 命令流数据源解析层

#### BDD-1: 统一 CommandRecord IR 字段完整性
- Given 任一平台适配器产出一条命令记录
- When 校验其字段集合
- Then 该记录必含 platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/output_hash/truncated 十个字段，且类型符合 IR 契约（ts_start/ts_end 为 epoch 毫秒整数、exit 为 int|null、truncated 为 bool）

#### BDD-2: claude-code 适配器从 JSONL 解析命令流
- Given 一份 claude-code 会话 JSONL（fixture 取自验证记录样例，含 tool_use/tool_result 配对）
- When 运行 claude-code 适配器解析
- Then 输出的每条 CommandRecord 的 command 等于 tool_use 行的 input.command、ts_start/ts_end 来自配对行 timestamp、exit 从 is_error 布尔 + "Exit code N" 文本前缀解析出数字并写入 exit_signal 留档原始形态

#### BDD-3: opencode 适配器从 SQLite 解析命令流
- Given 一份 opencode 会话 SQLite 库（fixture 含 part.data.state 结构）
- When 运行 opencode 适配器解析
- Then 输出的每条 CommandRecord 的 exit 直接取 state.metadata.exit 整数；truncated 取 state.metadata.truncated 显式标记

#### BDD-4: dsh 适配器从 JSONL.zstd 解析命令流（解压隔离在适配器内部）
- Given 一份 dsh 会话 session.jsonl.zstd（拼接帧容器）且本机无 python zstandard/zstd 二进制
- When 运行 dsh 适配器解析
- Then 解压全程隔离在 dsh 适配器内部完成（适配器之外不存在解压逻辑）、逐帧拼接后产出统一 CommandRecord IR，且解析不依赖 python zstandard/zstd 二进制；exit 从 isError 布尔 + "Error:" 文本前缀解析并写 exit_signal；tool/call 与 tool/result 按 callId 配对产出 ts_start/ts_end

#### BDD-5: 子 agent 会话定位（sidecar / delegationDepth）
- Given 会话目录中同时存在主会话文件与子 agent 会话文件（Claude Code sidecar `subagents/agent-*.jsonl`；DSH 独立 session 文件，delegationDepth 区分层级）
- When 适配器的 list_sessions/read_commands 定位"某个具体 subagent"的命令流
- Then 按平台规则定位到该子 agent 的会话文件并解析出其命令记录（Claude Code 读 sidecar 子转录文件、DSH 读 delegationDepth>0 的独立 session 文件）——仅读主会话文件会漏掉子 agent 记录，定位结果与主会话可区分

#### BDD-6: 新增平台只写适配器、检测引擎零改动
- Given 一个已有三平台适配器注册的解析层
- When 按适配器契约新增第四个平台适配器并注册（配置声明或目录扫描 adapters/*.py 约定）
- Then 检测引擎代码零改动即消费新平台 IR，且注册后 list_sessions/read_commands 对新平台会话可用

#### BDD-7: 解析单测 fixture 取自验证记录且脱敏
- Given 解析单测的 fixture 文件
- When 检查 fixture 来源与内容
- Then fixture 样例字段结构取自 verification-cmdstream-datasource-20260903.md 记录，且所有命令/输出内容已脱敏（不含真实用户路径、密钥、会话标识）

### 4.2 Phase 2 — 检测引擎

#### BDD-8: 调用冻结·主信号（未结束 call + expected 声明 → expected×2）
- Given 命令流中存在未结束的 tool/call（call 无配对 result）且该命令声明了 expected（复用 RM-AG0023 timeout_seconds）
- When 该 call 开始距今超过 expected×2（且不低于 30s 下限）
- Then 检测器判定 FROZEN（调用冻结），原因注明 expected×2 主信号来源

#### BDD-9: 调用冻结·兜底 alert（未结束 call 无 expected → 超过 300s）
- Given 命令流中存在未结束的 tool/call 且该命令未声明 expected
- When 该 call 开始距今超过 300s 但未超过 900s
- Then 检测器输出 alert 级提示核查（FROZEN，alert）

#### BDD-10: 调用冻结·兜底 suspect（未结束 call 无 expected → 超过 900s）
- Given 命令流中存在未结束的 tool/call 且该命令未声明 expected
- When 该 call 开始距今超过 900s
- Then 检测器输出 suspect 级考虑中止提示（FROZEN，suspect）

#### BDD-11: 活动冻结·alert（最后活动事件距今超过 60s）
- Given 命令流中无未结束调用
- When 任何一类活动事件（model 思考 / model 输出 / 执行 tool）的最后时间距今超过 60s 但未超过 300s
- Then 检测器输出 alert 级活动冻结提示（ACTIVITY_FROZEN，alert）

#### BDD-12: 活动冻结·suspect（最后活动事件距今超过 300s）
- Given 命令流中无未结束调用
- When 任何一类活动事件的最后时间距今超过 300s
- Then 检测器输出 suspect 级活动冻结提示（ACTIVITY_FROZEN，suspect）

#### BDD-13: 三类活动信号均计入活动、长时间思考不误杀
- Given subagent 已 20 分钟未调工具但 reasoning（model 思考）事件持续流动（对应实测思考间隙 max≈1239s）
- When 检测器按活动冻结判据评估
- Then 判定 NORMAL（不冻结）——活动冻结看"任何一类活动事件"而非"最后一条命令"，仅看最后一条命令的判据在此场景会误判 FROZEN

#### BDD-14: 无效重复检测（窗口 10 内同 (命令, exit, 输出哈希) 重复 ≥5 → SPIN）
- Given 窗口 10 条已完成命令中同一 (命令, exit, 输出哈希) 组合重复 ≥5 次（截断输出除外）
- When 检测器按无效重复判据评估
- Then 判定 SPIN（疑似逻辑空转），附重复组合与重复次数

#### BDD-15: 无效重复·结果签名变化不误报
- Given 窗口内命令名重复但 exit 或输出哈希在变化（合法"测试-修复-迭代"）
- When 检测器按无效重复判据评估
- Then 判定 NORMAL，不触发空转信号

#### BDD-16: 无效重复·唯一命令数 <3 信息级提示（REPEAT_UNIQUE_MIN=3）
- Given 窗口 10 条内唯一命令数 <3，且不存在同一 (命令, exit, 输出哈希) 组合重复 ≥5（结果签名在变化，属合法迭代特征）
- When 检测器按无效重复判据评估
- Then 不判空转——判定 NORMAL，附信息级提示（窗口内唯一命令数 <3、结果签名在变化属合法迭代特征，不判空转），不触发 SPIN

#### BDD-17: 截断输出不参与无效重复哈希比对
- Given 窗口内多条命令输出均为 truncated 标记且截断后哈希相同（对应两个不同失败被截断成同前缀的场景）
- When 检测器按无效重复判据评估
- Then truncated 命令不参与 (命令, exit, 输出哈希) 比对，判定 NORMAL（不误判空转）；truncated 记录仍参与冻结检测

#### BDD-18: 轮询循环误报标注（合法轮询不判死）
- Given 命令流中 `gh pr checks --watch` 或 `sleep N; check` 类合法轮询重复相同签名超过重复阈值
- When 检测器输出信号
- Then 信号定位为"核查提示"而非自动判定/自动终止，附注该模式为已知轮询误报类，由主 Agent 核查时识别循环体消解

#### BDD-19: 阈值显式覆盖生效（maintainability.yaml 模式）
- Given 检测引擎的阈值配置项（调用冻结 alert/suspect、活动冻结 alert/suspect、无效重复窗口/阈值）
- When 配置文件中显式覆盖某阈值（如活动冻结 alert 改为 120s）
- Then 检测引擎按覆盖值判定，不使用协议默认值

#### BDD-20: 阈值配置缺失兜底默认值
- Given 阈值配置文件缺失（maintainability.yaml 不存在或未含检测阈值节）
- When 运行检测引擎
- Then 兜底使用协议默认值（300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3），正常运行不报错

#### BDD-21: 阈值配置损坏兜底默认值
- Given 阈值配置文件存在但损坏（YAML 解析失败或字段类型非法）
- When 运行检测引擎
- Then 兜底使用协议默认值（300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3），正常运行不报错、不静默跳过检测

#### BDD-22: verify_cmdstream_detection.py 9 场景全 PASS 保持
- Given 仓库中既有验证脚本 verify_cmdstream_detection.py（A-I 九场景：调用阻塞/空转/合法迭代/健康长尾/合法长命令/expected 超期/截断排除/长时间思考/活动冻结）
- When 运行该脚本
- Then 9 场景全部 PASS（exit 0），输出结论"全部断言通过——命令流日志可机械区分九种状态"

#### BDD-23: 检测定位"证据 + 触发核查，不自动判死"
- Given 检测器对某 subagent 判定为 FROZEN 或 SPIN
- When 检查检测器的输出形态与后续动作
- Then 输出仅为客观证据（判定类别 + 原因 + 阈值依据），不包含任何自动终止/自动中止 subagent 的动作指令——中止/重派等动作仍由主 Agent 判断执行

#### BDD-24: 检测/派发输出平台无关、由平台食谱消费
- Given 检测引擎输出某 subagent 的判定信号（FROZEN/SPIN/NORMAL）或派发输出动作方向
- When 检查输出形态
- Then 输出为平台无关指令形态（判定类别 + 原因 + 阈值依据 + 建议动作方向），不含具体平台工具名/平台命令调用——同一输出可被 claude-code/opencode/dsh 三平台食谱原样消费并按平台适配执行

### 4.3 Phase 3 — 心跳文件生命周期 + 协议文档

#### BDD-25: 心跳文件父子分层命名
- Given 任务目录下需要心跳文件
- When 按命名规范落盘
- Then 任务级心跳文件名为 `${TASK_DIR}/.heartbeat`；父 subagent 为子任务维护的心跳文件名为 `${TASK_DIR}/.heartbeat.child-{n}`（n 为父任务内序号），同一父任务内不重复、不覆盖同名文件

#### BDD-26: 心跳文件审计豁免确认
- Given 任务目录内存在 `.heartbeat` 与 `.heartbeat.child-1` 文件
- When 运行 check-p6-provenance.py 与 check-protocol-consistency.py 对任务目录执行扫描
- Then 两类文件均不计入审计/一致性扫描对象（不产生未引用文件告警、不产生文档一致性命中），且落地记录中登记了显式确认结果（不能仅靠"默认不扫"假设）

#### BDD-27: 任务结束清理 + 异常遗留兜底
- Given 任务结束（成功/失败/超限任一结局）
- When 检查心跳文件清理行为
- Then 负责产生心跳的一方清理自己产生的心跳文件；若异常中止导致遗留，下次同任务重新派发前由派发前置检查清空（比照 agate-archive-stale-outputs 模式，不新建清理机制）

#### BDD-28: dispatch-protocol.md 两套信号职责分工改写
- Given 已改写的 dispatch-protocol.md「Subagent 安全 → 存活检查」节
- When 对照 RM-AG0023 progress 心跳扩展语义检查
- Then 节内明确：命令流日志承担"存活/卡死"判定职责（取代 progress 心跳扩展的此职责），progress.md 保留"语义进展"职责（正在做什么、下一步计划）不变；两套信号分工清晰、无职责重叠表述，且不修改 check-gate.py / check-state-transition.py 返回约定

### 4.4 Phase 4 — 受控自主再派发

#### BDD-29: 执行角色子派发权限下放（不写 .state.yaml）
- Given 一个被授予子派发权限的执行角色 subagent（analyst/architect/implementer/verifier）
- When 其内部派发子任务
- Then 子任务不写 `.state.yaml` / `active-tasks.md`，不产生独立 phase 状态——主 Agent 与状态机视角下仍是"一个 subagent 在跑"，父 subagent 汇总后仅以"路径+摘要"格式回报

#### BDD-30: 子任务写权限严格子集
- Given 父 subagent 被约束"只改 backend/ 目录"
- When 其派发子任务并检查子任务实际写权限
- Then 子任务只能触碰 backend/ 目录内文件——父 subagent 在派子任务的 prompt 中显式重申该约束，子任务不自动继承父权限

#### BDD-31: judge 类角色例外声明
- Given 派发 judge 类角色（要求 fresh context 信息隔离）
- When 检查其角色定义 / dispatch-context 的派发能力声明
- Then 显式声明"不启用子派发能力"——不开放 Agent/subagent_fork 工具权限，子派发决策路径与 fresh context 隔离冲突由此消解

#### BDD-32: 子派发产出收敛、不触发 gate 判定
- Given 父 subagent 内部完成子派发并汇总产出
- When 检查子派发中间产物与 gate 判定关系
- Then 子任务中间产出不计入 gate 判定对象；仅父 subagent 最终声明的 files_modified 走既有的假完成校验（D2），不产生新的编排层级

#### BDD-33: 不破坏 gate 返回约定（两套独立信号）
- Given 本任务全部落地后
- When 运行 check-gate.py 与 check-state-transition.py 对既有任务执行判定
- Then 两脚本 exit 三态约定（0/1/2）与落地前一致——心跳/命令流判定信号不并入 gate 判定路径，agate/rules/*.yaml 若新增字段通过 JSON Schema 与 S-1~S-6 双向一致性校验

## 5. 待确认清单

[NO_NEED_CONFIRM]

说明：设计文档 §6 剩余待确认事项（1/2/3/5/7）经核对均不阻塞立项，且不构成需求方向分叉需人定夺：
- 事项 1（阈值默认值）：dispatch-context 已给出确定值（300/900/60/300/10/5 + expected×2），且用户已明确"宁可多提示、绝不误杀"——方向已定，BDD-8/9/10/11/12/19/20/21 承载
- 事项 2（P4/P5 资源密集阶段放宽阈值）：由"阈值全部可配置"（BDD-19/20/21）覆盖，P2 设计期决定覆盖值即可
- 事项 3（OpenCode CLI 子进程实机验证）：P0-brief out-of-scope（不封装），需求不含此内容
- 事项 5（TPV0095 立论）：已核实为可能性 B（P2 评级正确执行、批内顺序依赖粒度未被静态评级捕捉），立论成立，无需更细粒度证据；P1 细化 BDD 未发现需要停下与用户确认的缺口
- 事项 7（适配器注册方式二选一）：P2 设计决策，非需求方向

## 6. 裁剪说明

本任务为**协议机制升级**（跨 4 phase 机制改动 + 协议文档改写 + SELF-GATE 触发），非小任务（不启用 P1_simplified）。阶段裁剪判定：

| 阶段 | 是否走 | 理由 |
|---|---|---|
| P1 需求基线 | ✅ 必走 | 核心阶段，本文件 |
| P2 设计 | ✅ 必走 | 适配器模式 / 检测引擎 / 权限边界需候选方案与评审；design 文档 v5 是设计输入而非替代 P2 产出 |
| P3 测试设计 | ✅ 走（medium 不可裁） | risk_level=medium（见 frontmatter），P3 不可裁剪；需设计适配器/检测引擎/心跳生命周期/再派发边界的 pytest 用例 |
| P4 实现 | ✅ 必走 | 新增脚本 + 协议文档改写 |
| P5 验证 | ✅ 必走 | 全量 pytest + consistency 0 ERROR + shellcheck 0 error + count-tests 不漂移（测试基线 F 节） |
| P6 验收 | ✅ 必走 | 逐条对照本文件 BDD（33 条），PASS/FAIL 二值 |
| P7 一致性 | ✅ 走 | 多文件协议改动（dispatch-protocol.md / role-system.md / 模板 / phase-card），需跨文件交叉核对（packages 声明）；无 internal_only 声明故不裁 |
| P8 发布 | ✅ 走 | 触发 SELF-GATE（改 agate/scripts/* + agate/*.md），commit 须含 self-gate-review:；协议文档改动需 protocol-alignment-review + 版本发布（非 internal_only） |

ceremony 声明：standard（缺省 fail-closed；任务跨多文件机制改动，不做薄化）。

## 7. 能力需求声明

```yaml
capability_requirements:
  - need: dsh-zstd-decompression
    why: DSH 会话文件为 JSONL+zstd 拼接帧容器，解析需逐帧解压；本机无 python zstandard/zstd 二进制（交接单 §7 已核实）
    available:
      - "Node 24 原生 zlib.zstdDecompress（2026-09-03 本会话实机验证：node v24.15.0，zlib.zstdDecompress 类型为 function，可用）"
    status: available

  - need: platform-session-parsing
    why: 三平台会话数据源格式完全不同（JSONL / SQLite / JSONL.zstd），解析单测需 fixture 样例（脱敏）
    available:
      - "python3（含 sqlite3 模块，实机验证可用）"
      - "pyyaml 6.0.1（maintainability.yaml 阈值配置读取，实机验证可用）"
      - "fixture 样例取自 verification-cmdstream-datasource-20260903.md（脱敏）"
    status: available

  - need: detection-logic-verification
    why: Phase 2 验收锚 verify_cmdstream_detection.py 9 场景须全 PASS 保持
    available:
      - "verify_cmdstream_detection.py（仓库内既有脚本，9 场景全 PASS 已入库）"
    status: available
```

无 GAP 条目；无 frontend 域 → 无视觉能力声明（P1 gate 的 `_gate_p1_vision_capability` 不适用）。

## 8. P0-brief 时效性质疑

已核对 P0-brief 时效性，无漂移。

核对依据（对照 P0 卡「漂移判据」严重 3 条逐一排查）：
1. **task 目标方案仍成立**：命令流日志机制的设计文档 v5（含三平台实机验证闭环）在 main 且可读；验证记录与 verify_cmdstream_detection.py 均存在；无替代方案出现
2. **executor_env 平台前提仍成立**：worktree 路径 `.worktrees/agate-TAG0028` 存在、任务目录存在、`~/.agate` 稳定版可用（本会话 agate-md-field-set 调用成功）；DSH 平台为本任务实际运行平台（本会话即 DSH subagent）
3. **known_risks 六条均无"已解决前提实际未解决"或"已被他任务解决"**：外部数据源脆弱性（验证记录已沉淀差异点）、阻塞派发平台妥协（设计诚实声明）、轮询误报类（阈值保守）、judge 隔离冲突（§4.4 论证）、TPV0095 立论（已核实可能性 B）、RM-AG0023 职责边界（§3.4.2 明确，Phase 3 落地）
4. 无轻微漂移项（阈值具体值由 dispatch-context 给出，未与 P0-brief 冲突；env_constraints 的 DSH 会话脱敏约束本任务遵守）

## 9. 环境隔离声明

[PROD_NOT_TOUCHED] 本任务为协议层开发（worktree 双工作区），全程未接触生产环境；仅读取本任务目录、协议文档与验证记录，未读取其他用户 DSH 会话。

## 10. 下游影响提示（供 P2/P6 参考，非需求正文）

- P2 设计依赖本文件的 domains（backend/cli）+ risk_level（medium）决定评审角色与强度
- P6 验收逐条对照 BDD-1~33（PASS/FAIL 总数必须 ≥ 33）
- P7 一致性检查依赖 packages（agate）声明做跨文件交叉核对
- 检测引擎脚本与验证脚本 `verify_cmdstream_detection.py` 的语义一致性（BDD-22）是 Phase 2 验收锚，P4 实现不得破坏 9 场景断言

## 11. 修复轮记录（fix1）

> 本轮依据 P1-review.md（status=needs-revision，独立评审 subagent de346328）执行增量修复。修复只动本文件，P1-review.md 由主 Agent 留存未改；机制数值（300/900/60/300/10/5 + expected×2 下限 30s + REPEAT_UNIQUE_MIN=3）全部保持与设计文档/验证脚本一致。修复动作逐条对应评审结论项 1-6：

1. **红线 1 — BDD-4 去除实现 API**（评审结论项 1）：BDD-4 标题与 Then 不再点名 "Node 24 原生 zlib.zstdDecompress"，改为行为化表述——"解压全程隔离在 dsh 适配器内部完成（适配器之外不存在解压逻辑）、产出统一 CommandRecord IR、不依赖 python zstandard/zstd 二进制"；具体解压 API（Node zlib / spawn node / 其他）留给 P2 设计决策。capability_requirements 中 "Node 24 原生 zlib.zstdDecompress 可用" 作为环境事实声明保留（能力声明，非 BDD 实现细节）。
2. **红线 2 — I-4 子 agent 会话定位补 BDD 锚点**（评审结论项 2）：新增 BDD-5（Phase 1 节，紧跟三平台解析之后），覆盖 "适配器 list_sessions/read_commands 按平台规则定位子 agent 会话（Claude Code sidecar `subagents/agent-*.jsonl` / DSH 独立 session 文件 delegationDepth 区分层级），而非只读主会话"；对应设计文档 §3.4.4 line 268 与验证记录 line 9/49/90。
3. **红线 3 — 多场景拆号**（评审结论项 3）：原 BDD-8 拆为 BDD-9（调用冻结·兜底 alert 300s）/BDD-10（调用冻结·兜底 suspect 900s）；原 BDD-9 拆为 BDD-11（活动冻结·alert 60s）/BDD-12（活动冻结·suspect 300s）；原 BDD-14 拆为 BDD-19（阈值显式覆盖生效）/BDD-20（配置缺失兜底默认值）/BDD-21（配置损坏兜底默认值）——拆分后每条仅一条 Given-When-Then。
4. **次要 4a — BDD-11 对照场景拆号**：原 BDD-11 Then 内嵌的对照场景（命令名重复但 exit/输出哈希变化 → NORMAL）拆为独立 BDD-15（无效重复·结果签名变化不误报）。
5. **次要 4b — REPEAT_UNIQUE_MIN=3 入 BDD**：新增 BDD-16（无效重复·唯一命令数 <3 信息级提示），覆盖验证脚本 line 44/148-151 语义——窗口内唯一命令数 <3 且结果签名在变化时判定 NORMAL、附信息级提示、不判空转（合法迭代特征）。
6. **次要 5 — I-15 平台无关输出补锚**：新增 BDD-24（检测/派发输出平台无关、由平台食谱消费），与 BDD-23（证据+核查不自动判死）互补，显式锚定输出形态的平台无关性（不含平台工具名/平台命令调用，三平台食谱原样消费）。

**编号重排与总数**：拆分/新增后全文件 BDD 重排为 **BDD-1~33 全局连续无跳号**；总数 25 → 33（净增 8 = 拆分净增 5 + 新增 3）。P6 验收按拆分后的 33 条对照（拆分产生的 BDD 为原 BDD 的单场景子集，语义不变）。正文旧编号引用（回归拦截声明、待确认清单、§10 下游提示）已同步更新为新编号。
