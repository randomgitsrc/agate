---
phase: P2
task_id: TAG0028
type: design
parent: P1-requirements.md
trace_id: TAG0028-P2-20260903
status: draft
created: '2026-09-03'
agent: architect
candidate_count: 3
packages:
- agate
domains:
- backend
- cli
ui_affected: false
---

# P2 设计 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P2（方案设计）· 角色：architect · 日期：2026-09-03
> 验收锚：P1-requirements.md 33 条 BDD（approved）· 设计输入：设计文档 v5（§3.4.2/§3.4.3/§3.4.4/§3.5/§3.6/§4/§6）·
> 验证记录 verification-cmdstream-datasource-20260903.md（三平台格式差异事实）· verify_cmdstream_detection.py（9 场景锚）
> 本文件是 P3/P4/P5/P6/P7 的实现与验证导航，不是对设计文档 v5 的复述——候选方案权衡与影响面梳理是本文件的核心增量。

## 1. 影响面梳理（候选方案之前）

> 依据 P1 §3 同类扫描（S-1~S-8）+ P0 影响面预判 + 本阶段实读代码的 grep/消费方证据，做**候选方案级**影响域分析。
> 客观证据清单：实读 check-maintainability.py:88-148（`_load_config` 全兜底）、check-p6-provenance.py:85-93（`_find_files` 隐藏文件跳过）、
> agate-archive-stale-outputs.py 全文（_OUTPUTS/.archived/breadcrumb 模式）、dispatch-protocol.md:944-951（Subagent 安全节 + 存活检查 951 行）、
> dispatch-protocol.md:502-560（派发编排机制 + 并行规则第 4 条）、role-system.md 全文（无子派发权限边界描述，S-7 空白确认）、
> dispatch-context.md 模板全文（56 行，dispatch_guide 骨架）、check-protocol-consistency.py:947-949（scripts 目录 iterdir 文件集枚举）、
> CI protocol-tests.yml:179-215（shellcheck 命令形态）、maintainability.yaml 现状（9 行）、phases.yaml P2 task_fields（5 字段）。

### 1.1 改什么（Modify）

| # | 文件 / 模块 | 改动落点 | 关联 BDD |
|---|------------|---------|---------|
| M1 | `agate/scripts/agate-cmdstream-ir.py`（新增） | CommandRecord 统一中间表示：dataclass 十字段（platform/session_id/tool/command/ts_start/ts_end/exit/exit_signal/output_hash/truncated）+ 字段契约校验（ts_start/ts_end epoch 毫秒 int、exit int\|null、truncated bool）+ JSON 序列化 | BDD-1 |
| M2 | `agate/scripts/agate-cmdstream-adapters.py`（新增） | `CommandStreamAdapter` 基类（probe/list_sessions/read_commands 契约）+ 三平台适配器（ClaudeCodeAdapter 解析 JSONL + "Exit code N" 文本前缀、OpenCodeAdapter 解析 SQLite + metadata.exit 整数、DSHAdapter 解析 JSONL.zstd + isError/"Error:" 前缀 + node zstd 解压隔离）+ 显式注册表 `ADAPTERS = {"claude-code": ..., "opencode": ..., "dsh": ...}`；子 agent 会话定位（Claude sidecar `subagents/agent-*.jsonl` / DSH delegationDepth>0 独立 session 文件） | BDD-2/3/4/5/6/7 |
| M3 | `agate/scripts/agate-cmdstream-detect.py`（新增） | 检测引擎：消费 CommandRecord 列表 → 判定 FROZEN（调用冻结 expected×2 + 兜底 300/900）/ FROZEN（活动冻结 60/300）/ SPIN（窗口 10 内同签名 ≥5）/ NORMAL（含 REPEAT_UNIQUE_MIN=3 信息级、截断排除、轮询误报标注）；输出 = 平台无关"证据 + 触发核查"形态；阈值从 maintainability.yaml 读取（复用 `_load_config` 全兜底模式）；CLI 子命令（list-sessions / read-commands / detect） | BDD-8/9/10/11/12/13/14/15/16/17/18/19/20/21/23/24 |
| M4 | `agate-workspace/maintainability.yaml`（修改） | 同文件新增 `cmdstream_detection:` 节（调用冻结 alert/suspect、活动冻结 alert/suspect、无效重复窗口/阈值、REPEAT_UNIQUE_MIN、expected 倍率/下限），缺失/损坏兜底协议默认值（300/900/60/300/10/5 + 3 + ×2/30s）不报错；不新增独立配置文件 | BDD-19/20/21（S-8：同文件加节或同模式新键，P2 定 → 取同文件加节） |
| M5 | `agate/dispatch-protocol.md`（修改） | ① 951 行「Subagent 安全 → 硬超时保护 → 存活检查」节改写：命令流日志承担"存活/卡死"判定职责（取代 progress 心跳扩展此职责），progress.md 保留"语义进展"职责不变，两套信号分工明确（BDD-28）；② 新增「心跳文件生命周期」子节：`.heartbeat` / `.heartbeat.child-{n}` 命名规范、审计豁免声明、清理时机（任务结束由产生方清理；异常遗留由派发前置检查清空，复用 agate-archive-stale-outputs 任务目录收尾模式，不新建清理机制）（BDD-25/26/27）；③ 新增「subagent 自主再派发」节：与五模式编排关系（互补不替代，模式 4 仍权威）、§4.1 两条边界、子任务产出收敛语义（不产生新编排层级、中间产出不计 gate 判定、files_modified 走 D2）（BDD-29/30/32） | BDD-25/26/27/28/29/30/32 |
| M6 | `agate/role-system.md`（修改） | 新增「子派发权限边界」节：执行角色（analyst/architect/implementer/verifier）可被授予子派发权限，两条硬边界（子任务不写 .state.yaml/active-tasks.md；写权限是父权限严格子集）；judge 类角色例外（不开放 Agent/subagent_fork，信息隔离冲突论证） | BDD-29/30/31 |
| M7 | `agate/assets/templates/dispatch-context.md`（修改） | `<dispatch_guide>` 节补「不启用子派发能力」显式声明位（judge 类角色派发时注入） | BDD-31（S-6：模板 56 行补节，其余骨架不变） |
| M8 | `agate/scripts/check-p6-provenance.py`（修改，注释/登记级） | `_find_files`（85-93 行）隐藏文件过滤已天然跳过 `.heartbeat*`（实读确认 `if name.startswith("."): continue`）；在路径过滤逻辑处**登记显式确认结果**（注释 + 常量说明），不改枚举逻辑、不改 7 道审计结构 | BDD-26（S-5：登记豁免确认，不能仅靠"默认不扫"假设） |
| M9 | `agate/tests/unit/test_agate_cmdstream_*.py`（新增） | pytest 覆盖：适配器解析（三平台 fixture → CommandRecord 断言）/ 检测引擎判定（复刻 verify 9 场景 + 阈值覆盖/缺失/损坏兜底）/ 心跳文件生命周期（命名/豁免/清理）/ 自主再派发边界（.state.yaml 不写、写权限子集、judge 例外声明） | BDD-1~33 承载 |
| M10 | `agate/tests/fixtures/`（新增） | 三平台脱敏 fixture 样例（字段结构取自验证记录；命令/输出内容脱敏，不含真实用户路径/密钥/会话标识；OpenCode SQLite fixture 运行时构造或最小转储） | BDD-7（I-14） |

**验证锚保持**：`docs/design-notes/.../verify-heartbeat-cmdstream/verify_cmdstream_detection.py` **不改**——它是 Phase 2 验收锚（BDD-22），P5 gate 命令直接运行它判定 9 场景全 PASS；检测引擎以其判据为参考实现（M3）。

### 1.2 不改什么（Not Modify）

| # | 看起来该改但决定不改 | 理由 |
|---|---------------------|------|
| N1 | `agate/scripts/check-gate.py` / `check-state-transition.py` | BDD-33 + 约束 1 + P0 out-of-scope：心跳判定与 gate 判定是两套独立信号，exit 三态约定（0/1/2）不动 |
| N2 | `agate/rules/*.yaml` | 约束 1：增字段须过 JSON Schema + S-1~S-6 双向一致性 gate；阈值配置走 `agate-workspace/maintainability.yaml`（M4），不碰 rules yaml |
| N3 | `agate/scripts/agate-archive-stale-outputs.py` | S-4：复用其"任务目录收尾清理模式"（派发前置检查清空心跳遗留），脚本本身与调用点语义不变，不扩展 _OUTPUTS |
| N4 | `agate/assets/templates/dispatch-prompt.md` 分阶段落盘节 | S-2：progress.md 保留"语义进展"职责（正在做什么），命令流日志取代的是"存活判定"职责，protocol 层改写即可，role 文件/模板的分阶段落盘指令语义不变 |
| N5 | 各执行角色文件（analyst/architect/implementer/verifier/test-designer/consistency-reviewer）的分阶段落盘节 | S-2：同 N4，role 文件的"写 progress"指令仍是语义进展落盘，不冲突 |
| N6 | `agate/assets/templates/task-files.md` progress.md 定义（44 行） | S-2：progress.md 定义不变 |
| N7 | `docs/design-notes/.../verify_cmdstream_detection.py` | BDD-22 锚：9 场景断言保持，P4 实现不得破坏（P1 §10 下游提示） |
| N8 | `agate/platform-notes.md` | S-7：DSH 工具矩阵（subagent/subagent_fork/workflow）保持现状，只补权限边界声明不重写工具矩阵；platform-notes.md:68 Codex 单层限制陈述保持 |
| N9 | `agate/LIMITATIONS.md:62` | S-1：既有已知限制陈述（"Task 工具暴露 subagent 活动信号…心跳"），改写 dispatch-protocol.md 后如措辞冲突再同步，不单独立项 |
| N10 | DSH 心跳钩子机制本身 / OpenCode `opencode run` CLI 子进程路线封装 | P0 out-of-scope：命令流路径已验证，钩子方案仅实机验证注记不实现；CLI 路线仅文档指导不封装脚本 |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解 |
|---|------|------|
| R1 | **外部数据源脆弱性**：Claude Code 与 DSH 无数字 exit code，靠文本前缀（"Exit code N"/"Error:"）解析——平台改失败输出格式则解析规则需更新（验证记录差异点 2） | 适配器把差异点沉淀在验证记录文档（已有）；解析规则集中在适配器内（M2）；脱敏 fixture 回归测试锁定解析行为（M10）；IR 的 exit_signal 留档原始形态，解析失败可审计 |
| R2 | **DSH zstd 解压依赖**：`~/.dsh/sessions/*.jsonl.zstd` 为拼接帧容器，需逐帧解压；本机无 python zstandard/zstd 二进制 | 解压隔离在 dsh 适配器内部（spawn node 单行脚本 `node:zlib.zstdDecompress`），检测引擎零平台细节（BDD-4）；验证记录已实机验证 node v24.15.0 zlib.zstdDecompress 可用（minimal_validation 引用该结论）；适配器探测 node 可用性并报清晰错误 |
| R3 | **检测引擎与 verify 脚本语义漂移**：9 场景锚（BDD-22）若被 P4 实现破坏则 Phase 2 验收失效 | verify 脚本不改（N7）；P5 gate 固化运行 verify 脚本（exit 0 判定）；检测引擎单测复刻 9 场景断言（M9）；阈值默认值常量与 verify 脚本对齐（同源数值 300/900/60/300/10/5/×2/30） |
| R4 | **双源同步**：maintainability.yaml 权威值 vs 脚本默认值副本（BDD-19/20/21） | 复用 check-maintainability.py:88-148 `_load_config` 全兜底模式（文件缺失/yaml 损坏/键缺失/类型坏均回默认值不报错、不静默跳过）；默认值单点定义在检测引擎常量，配置仅覆盖 |
| R5 | **心跳文件与审计脚本交互**：`.heartbeat*` 落盘 `tasks/` 进入协议命名空间，可能被审计/一致性扫描命中 | check-p6-provenance.py `_find_files` 已跳过隐藏文件（实读确认 line 85-93）→ `.heartbeat*` 天然豁免；登记显式确认（M8）；check-protocol-consistency 扫 md 不扫运行时文件 |
| R6 | **dispatch-protocol.md 改写与 RM-AG0023 职责漂移**：两套信号（命令流 vs progress 心跳）定义若漂移则存活判定回归不可验证（P0 known_risks 第 6 条） | 改写节明确边界表述（命令流=存活/卡死判定，progress.md=语义进展）；P5 gate 含 `check-protocol-consistency.py --strict-errors-only` 0 ERROR（约束 11）；SELF-GATE commit message 含 self-gate-review: |
| R7 | **子派发权限越界**：子任务写权限意外超出父 subagent 权限（BDD-30） | §4.1 两条边界写死在 role-system.md（M6）；父 subagent 派子任务 prompt 显式重申约束（设计 §4.1 边界 2）；子任务 files_modified 走既有 D2 假完成校验路径（BDD-32） |
| R8 | **judge 例外误开放**：judge 若获得子派发权限则信息隔离防线被破坏（P0 known_risks 第 4 条） | role-system.md 显式声明 judge 不适用子派发 + dispatch-context 模板补"不启用子派发能力"声明位（M7）；phase-card 层面 judge 角色工具声明默认不含 Agent/subagent_fork |
| R9 | **SELF-GATE 触发面**：本任务改 `agate/scripts/*.py` + `agate/*.md`（dispatch-protocol.md/role-system.md + 模板） | 全部 commit 含 `self-gate-review:`；协议文档改动跑 check-protocol-consistency --strict-errors-only；P8 走 protocol-alignment-review |
| R10 | **OpenCode 数据源描述不一致**：dispatch-context C 节写 `storage/session/<id>/info.json + messages.json`，验证记录（实机 2026-09-03）写单一 SQLite 库 `opencode.db`（part.data.state 结构） | **以验证记录为准（SQLite）**——P1 BDD-3 已锚定"opencode 会话 SQLite 库（fixture 含 part.data.state 结构）"；设计注明差异来源防 P4 踩坑；OpenCodeAdapter 只依赖验证记录确认的字段（state.time/start+end、state.input.command、state.metadata.exit、state.metadata.truncated） |

## 2. 候选方案

> 三个候选方案覆盖**最大的架构分叉**：脚本组织形态（平铺脚本族 vs 单脚本聚合 vs 子目录包）+ 适配器注册机制（显式注册表 vs 目录扫描）。检测引擎判定逻辑、阈值配置模式、心跳清理方式、Phase 3/4 文档改写四个维度三案一致（分别由 BDD-8~24 / BDD-19~21 / BDD-25~28 / BDD-29~33 锚定），候选差异聚焦"脚本面怎么摆 + 注册机制怎么选"。

### 2.1 候选方案 A：平铺脚本族 + 显式注册表（推荐）

- **脚本面**：`agate-cmdstream-ir.py`（IR + 校验）+ `agate-cmdstream-adapters.py`（基类 + 三平台适配器 + 显式注册表）+ `agate-cmdstream-detect.py`（检测引擎 + CLI 子命令 list-sessions/read-commands/detect），三个新脚本平铺在 `agate/scripts/`，命名符合既有 `agate-*.py` 惯例。
- **注册机制**：显式注册表（配置声明形态）——`ADAPTERS = {"claude-code": ClaudeCodeAdapter(), "opencode": OpenCodeAdapter(), "dsh": DSHAdapter()}`；新增平台 = 新适配器文件/类 + 注册表加一行。
- **优点**：
  - 平铺布局与 agate/scripts 现状完全一致（实查目录全部为单层 .py 文件），无子目录/魔法目录；
  - CHECK 10（check-protocol-consistency.py:947-949 `scripts_dir.iterdir() if p.is_file()`）枚举 scripts 顶层文件做脚本名引用漂移对照——平铺文件天然在检测面内，新脚本被协议文档引用时漂移可被捕获；
  - god-file 可控：三脚本职责单一（IR / 适配器 / 检测），单文件行数 <500，过 check-maintainability god_file_threshold=1000；
  - 显式注册表可测试（单测直接断言注册表内容）、无加载顺序/命名冲突问题（对比目录扫描）；
  - BDD-6 验收锚（注册后新平台 list_sessions/read_commands 可用 + 检测引擎零改动）由"适配器实现契约 + 注册表加一行"直接满足，检测引擎只 import ADAPTERS 不感知平台。
- **缺点**：
  - 新增平台需改注册表（加一行），不是"放文件即注册"的零代码体验；
  - 三个脚本的 import 关系需 P4 处理（同目录互 import，参考 agate_common 被 import 的既有模式）。

### 2.2 候选方案 B：单脚本聚合 + 子命令

- **脚本面**：一个 `agate/scripts/agate-cmdstream.py` 聚合 IR + 三平台适配器 + 检测引擎 + 心跳清理，argparse 子命令（list-sessions/read-commands/detect/cleanup）。
- **注册机制**：同文件内注册表（或同文件类内注册）。
- **优点**：文件数最少、部署最简单、单测 import 一个模块。
- **缺点**：
  - **god-file 高风险**：三平台适配器（Claude JSONL + OpenCode SQLite + DSH zstd）约 400-500 行 + IR + 检测引擎 + CLI，单文件预估 800-1200 行，**触发 check-maintainability god_file_threshold=1000**（P4 gate 红灯）；
  - 新增平台需修改同一大文件（文件级耦合高，BDD-6"检测引擎零改动"字面满足但改动面集中）；
  - 与 scripts/ 平铺惯例不冲突但与"每脚本单一职责"的既有组织逻辑相悖（现网脚本均为单职责）。

### 2.3 候选方案 C：子目录包 `cmdstream/` + 目录扫描注册

- **脚本面**：`agate/scripts/cmdstream/` 子目录包（`__init__.py` + `ir.py` + `adapters/` 子目录每平台一个文件 + `detect.py` + `cli.py`），注册 = 目录扫描 `adapters/*.py`（importlib 动态加载，模块级 `ADAPTER` 变量约定）。
- **优点**：扩展性最强（新增平台 = 放文件即注册，零注册表改动）；文件粒度最细、god-file 零风险。
- **缺点**：
  - **与既有惯例冲突**：agate/scripts 全为平铺单文件（实查无子目录先例），子目录包引入新布局形态；
  - **CHECK 10 检测盲区**：check-protocol-consistency.py 用 `iterdir()` 枚举 **scripts 顶层文件**——子目录内脚本不在脚本名引用漂移对照面，协议文档引用 `cmdstream/xxx.py` 时漂移无法被捕获（新机制需额外豁免/改造一致性 gate，扩范围）；
  - 目录扫描是隐式注册（魔法目录）：加载顺序、命名冲突、坏模块静默失败均需额外约定与容错，可测试性差；
  - pytest 收集子包 import 路径需额外处理（对比平铺文件的 sys.path 惯例）。

### 2.4 权衡与选择理由

| 维度 | A 平铺脚本族+显式注册表 | B 单脚本聚合 | C 子目录包+目录扫描 |
|------|------------------------|-------------|-------------------|
| 与 scripts/ 现状一致 | ✅ 平铺单文件惯例 | ✅ 平铺 | ❌ 子目录新布局 |
| CHECK 10 脚本名漂移检测面 | ✅ 顶层文件在检测面内 | ✅ | ❌ 子目录文件盲区 |
| god-file（threshold=1000） | ✅ 每文件 <500 行 | ❌ 预估 800-1200 行 | ✅ 每文件小 |
| BDD-6 扩展路径 | 适配器文件 + 注册表一行 | 改同一大文件 | 放文件即注册（零代码） |
| 可测试性 / 显式性 | ✅ 注册表可断言 | 中 | ❌ 隐式注册，加载/冲突需额外容错 |
| 实现/评审工作量 | 中（3 脚本） | 低（1 脚本但 P4 压力大） | 中高（包结构 + 一致性 gate 盲区处理） |

**选择理由（选 A）**：
1. **不扩范围**：C 方案为规避 CHECK 10 盲区需改造 check-protocol-consistency.py 的脚本名扫描逻辑（子目录递归），超出 P0-brief/设计文档锁定范围（约束 12）；A 方案零一致性 gate 改动。
2. **gate 兼容**：B 方案 god-file 风险会直接触发既有 P4 gate（check-maintainability），需 known-violations 登记或拆文件——拆文件后即退化为 A。
3. **BDD-6 语义满足**：A 的显式注册表满足"配置声明"形态（设计 §6 事项 7 二选一，P2 决策取配置声明）；"新增平台只写适配器"由"新适配器文件/类 + 注册表一行"实现，检测引擎 import 注册表不感知平台，零改动成立。
4. **检测引擎平台无关（I-1/I-3）**：平台细节全部收敛在 adapters 模块内（含 DSH zstd 解压 spawn node），detect 只消费 CommandRecord IR——A 的模块边界正好承载该隔离。

## 3. 选定方案设计（候选方案 A）

### 3.1 Phase 1 — 命令流数据源解析层（M1/M2/M10）

- **CommandRecord IR**（M1）：dataclass 十字段，类型契约按 BDD-1（ts_start/ts_end epoch 毫秒 int、exit int|null、truncated bool、output_hash truncated 时 null）；提供 `to_json()/from_json()` 供 CLI 中间传递与测试断言。
- **适配器契约**（M2）：`probe(path) -> bool` / `list_sessions(cwd) -> list[str]` / `read_commands(session_path) -> list[CommandRecord]`，基类 + 三平台实现：
  - ClaudeCodeAdapter：`~/.claude/projects/<dir>/<session>.jsonl`，tool_use/tool_result 配对（sourceToolAssistantUUID ↔ uuid），`input.command`、`timestamp`、`is_error` + `"Exit code N"` 前缀 → exit + exit_signal；子 agent = sidecar `subagents/agent-*.jsonl`（BDD-5）。
  - OpenCodeAdapter：SQLite（`opencode.db`，验证记录为准，R10），`part.data.state` 结构，`state.time.start/end`、`state.input.command`、`state.metadata.exit`（整数）、`state.metadata.truncated`（显式标记）（BDD-3）。
  - DSHAdapter：`~/.dsh/sessions/<sanitized-cwd>/<session-id>/session.jsonl.zstd`，**解压隔离在适配器内部**（spawn node 单行脚本 `node:zlib.zstdDecompress` 逐帧解压拼接帧容器），`tool/call`+`tool/result` 按 callId 配对产出 ts_start/ts_end，`arguments.command`、`isError` + `"Error:"` 前缀 → exit + exit_signal；子 agent = delegationDepth>0 独立 session 文件（BDD-4/5）。
- **适配器注册**：显式注册表 `ADAPTERS`（配置声明形态，BDD-6）。
- **fixture**（M10）：三平台脱敏样例，字段结构取自验证记录，命令/输出内容脱敏（不含真实用户路径/密钥/会话标识，I-14）。

### 3.2 Phase 2 — 检测引擎（M3/M4）

- **判定**（detect(records, now) → verdict + reasons，verdict ∈ {FROZEN, SPIN, NORMAL}）：
  - 调用冻结：未结束 call（call 无配对 result）→ 有 expected 用 `max(expected×2, 30s)` 主信号（BDD-8），无 expected 兜底 alert 300s（BDD-9）/ suspect 900s（BDD-10）；
  - 活动冻结：无未结束 call 时最后活动事件（思考/输出/工具任一）距今 >60s alert（BDD-11）/ >300s suspect（BDD-12）；三类活动均计入 → 长时间思考不误杀（BDD-13）；
  - 无效重复：窗口 10 内同 (命令, exit, 输出哈希) ≥5 → SPIN（BDD-14）；结果签名变化不误报（BDD-15）；唯一命令数 <3 信息级提示不判空转（BDD-16）；truncated 不参与哈希比对仍参与冻结检测（BDD-17）；
  - 轮询误报标注：信号定位"核查提示"而非自动判定（BDD-18/23）；输出平台无关（判定类别 + 原因 + 阈值依据 + 建议动作方向，不含平台工具名，BDD-24）。
- **阈值配置**（M4）：maintainability.yaml 新增 `cmdstream_detection:` 节；读取复用 check-maintainability.py:88-148 `_load_config` 全兜底模式（缺失/损坏/类型坏 → 协议默认值 300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3 + ×2/30s，不报错不静默跳过）（BDD-19/20/21）；默认值宁可偏保守（用户明确要求，P0 约束 2）。
- **与 verify 脚本关系**：verify_cmdstream_detection.py 不改（N7），作为 P5 gate 锚；检测引擎单测复刻 9 场景断言（M9），阈值常量与 verify 脚本对齐（R3）。

### 3.3 Phase 3 — 心跳文件生命周期 + 协议文档（M5/M8）

- **命名规范**（BDD-25）：任务级 `${TASK_DIR}/.heartbeat`；父 subagent 为子任务维护 `${TASK_DIR}/.heartbeat.child-{n}`（n 为父任务内序号，同父任务内不重复不覆盖）。
- **审计豁免登记**（BDD-26/M8）：`_find_files` 隐藏文件过滤已覆盖（实读确认），登记显式确认结果于 check-p6-provenance.py 路径过滤逻辑处 + 本文件 §1.1 M8。
- **清理时机**（BDD-27）：任务结束（成功/失败/超限）由产生心跳的一方清理自己产生的心跳文件；异常遗留由下次同任务重新派发前的**派发前置检查清空**（比照 agate-archive-stale-outputs 任务目录收尾模式，不新建清理机制，N3）。
- **协议改写**（BDD-28/M5）：dispatch-protocol.md 951 行存活检查节改写——命令流日志承担"存活/卡死"判定职责（取代 progress 心跳扩展此职责），progress.md 保留"语义进展"职责（正在做什么、下一步计划）不变；两套信号分工清晰、无职责重叠表述；不修改 check-gate.py/check-state-transition.py 返回约定。

### 3.4 Phase 4 — 受控自主再派发（M5/M6/M7）

- **权限边界**（BDD-29/30）：role-system.md 新增「子派发权限边界」节——执行角色（analyst/architect/implementer/verifier）可被授予子派发权限；两条硬边界：① 子任务不写 `.state.yaml`/`active-tasks.md`，不产生独立 phase 状态，外部观感永远"一个 subagent 在跑"，父汇总后仅以"路径+摘要"回报；② 子任务写权限是父权限严格子集，父在派子任务 prompt 中显式重申约束（不自动继承）。
- **judge 例外**（BDD-31）：role-system.md 声明 judge 类角色不适用子派发（fresh context 信息隔离与"自主决定查什么"决策路径开放性的性质冲突，设计 §4.4 论证）；dispatch-context 模板补"不启用子派发能力"显式声明位（M7）；judge 角色工具声明默认不含 Agent/subagent_fork。
- **产出收敛**（BDD-32）：子任务中间产出不计入 gate 判定对象；仅父 subagent 最终声明的 files_modified 走既有 D2 假完成校验；不产生新编排层级（状态机单层不变）。
- **与五模式关系**（设计 §4.2）：subagent 自主再派发是 subagent 内部一层，与主 Agent 层面模式 4"先理解后拆"并存互补，不合并不互相替代——本设计在 dispatch-protocol.md 明确此关系。

## 4. gate_commands（P2 固化，后续阶段不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ -q --tb=short"        # P3 TDD 红灯读取测试运行器（fix1：裸 pytest → python3 -m pytest）
  P5: "python3 -m pytest agate/tests/ -q --tb=no -n auto"   # P5 全量三片（unit/regression/integration）合跑 + -n auto 并行（fix1）
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_cmdstream_verify: "python3 docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py"
  P5_shellcheck: "shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 600
  P5_consistency_timeout_seconds: 120
  P5_cmdstream_verify_timeout_seconds: 120
  P5_shellcheck_timeout_seconds: 120
  P5_count_tests_timeout_seconds: 120
```

- **逐 key 独立**（不拼接 `&&`）：consistency / verify / shellcheck / count-tests 各自独立判定，避免短路掩盖（约束 14）。
- **timeout_seconds 三档基准**：P5 全量 pytest（三片合跑 + `-n auto` 并行）取 600s（对照 TAG0027 同量级套件 600s 档位，宁高勿低，TPV0093 教训；fix1 由 300s 上调）；其余单命令 120s（单测类档位）。
- **P5_cmdstream_verify**：BDD-22 验收锚（9 场景全 PASS、exit 0），P4 实现不得破坏。
- **P5_consistency**：协议文档改写（dispatch-protocol.md/role-system.md/模板）后 0 ERROR（约束 11，SELF-GATE）；必须用 worktree 自己的脚本（双工作区纪律）。
- **P5_count_tests**：用例数不漂移（测试基线 E 节）。
- **P5_shellcheck**：与 CI（protocol-tests.yml:179-215）同口径 `-S warning` 3 个 hook 薄壳；本任务不改 .sh，作为基线保持。

## 5. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/check-maintainability.py:88-148
    why: _load_config 全兜底模式参照（阈值配置读取复用）
  - path: agate/scripts/check-p6-provenance.py:85-93
    why: _find_files 隐藏文件过滤确认 + 心跳豁免登记位置
  - path: agate/scripts/agate-archive-stale-outputs.py
    why: 任务目录收尾清理模式参照（心跳遗留清空语义）
  - path: agate/dispatch-protocol.md:944-951
    why: Subagent 安全节改写对象（951 行存活检查）
  - path: agate/dispatch-protocol.md:502-560
    why: 派发编排机制 + 并行规则第 4 条（自主再派发节引用）
  - path: agate/role-system.md
    why: Phase 4 子派发权限边界新增位置
  - path: agate/assets/templates/dispatch-context.md
    why: Phase 4 模板补"不启用子派发能力"声明位对象
  - path: docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verification-cmdstream-datasource-20260903.md
    why: 三平台格式差异事实 + fixture 脱敏样例来源（解析器设计依据）
  - path: docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py
    why: 9 场景判据参考实现 + 阈值常量对齐源
  - path: agate/tests/conftest.py
    why: pytest fixture 体系（create_task_dir/_run_cli_impl）供新增测试复用
  - path: agate-workspace/maintainability.yaml
    why: cmdstream_detection 节新增落点
```

## 6. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "系统 python3（/usr/bin/python3）跑 pytest/pyyaml；ruff 用 ~/.venvs/agate-dev/bin/ruff"
  dsh_zstd: "DSH 会话文件 JSONL.zstd 拼接帧容器：node v24.15.0 zlib.zstdDecompress 可用（验证记录 2026-09-03 实机验证），解压隔离在 dsh 适配器内部（spawn node 单行脚本），不硬依赖 python zstandard/zstd 二进制"
  workspace_discipline: "双工作区：改代码/写产出在 worktree；编排/派发类工具用 ~/.agate 稳定版；check-protocol-consistency.py 必须用 worktree 自己的"
  fixture_only: "三平台真实会话片段仅作脱敏 fixture（BDD-7），不得读取其他用户会话（I-14）"
  self_gate: "本任务改 agate/scripts/*.py + agate/*.md（dispatch-protocol.md/role-system.md/模板）→ commit message 须含 self-gate-review:；协议文档改动需 check-protocol-consistency --strict-errors-only 0 ERROR"
  baseline: "基线验证 --strict-errors-only（DEBT0012）；全量 pytest 全绿 + count-tests 不漂移 + shellcheck 0 error"
  threshold_policy: "阈值默认值宁可多提示、绝不误杀（用户明确要求，P0 约束 2）"
```

> 边界提醒：本字段为声明性（信息注入），强制力靠 gate_commands（P5_consistency/P5_cmdstream_verify 等有命令可跑、有 exit code 可判定）承载；不落 gate 的约束（如 fixture_only）由 P4/P8 卡片 checklist 人工自查。

## 7. minimal_validation

```yaml
minimal_validation:
  assumption: "DSH JSONL.zstd 拼接帧容器可被 node:zlib.zstdDecompress 逐帧解压（本任务唯一关键外部行为）"
  method: "引用验证记录已实机验证结论（2026-09-03：node v24.15.0，zlib.zstdDecompress 类型为 function，可用）；P4 实现时如需复验，跑 node -e \"const z=require('node:zlib'); console.log(typeof z.zstdDecompress)\" 断言输出 function"
  result: "confirmed（验证记录闭环，无需重验）"
  note: "其余均为纯代码逻辑，无外部系统依赖：适配器解析依赖内部函数（JSONL/SQLite/zstd 解析 + CommandRecord 数据转换，IR 字段契约见 BDD-1）；检测引擎判定依赖 verify_cmdstream_detection.py 判据语义与阈值常量（同源数值）；心跳生命周期依赖文件系统操作 + check-p6-provenance.py 既有 _find_files 隐藏过滤；再派发边界为文档/模板改动。这些由 M9 pytest 承载，无需外部最小验证"
```

## 8. 实现完成标志

- Phase 1：三个新脚本（ir/adapters/detect）落地，三平台 fixture 解析单测全绿（BDD-1~7）。
- Phase 2：检测引擎 9 场景（复刻 verify 锚）+ 阈值覆盖/缺失/损坏兜底单测全绿（BDD-8~21/23/24）；verify_cmdstream_detection.py 仍 9 场景全 PASS。
- Phase 3：dispatch-protocol.md 存活检查节改写 + 心跳生命周期规范落盘；check-p6-provenance.py 豁免登记；BDD-25~28 单测/文档断言通过。
- Phase 4：role-system.md 权限边界节 + dispatch-context 模板声明位；BDD-29~33 单测/文档断言通过。
- 整体：`gate_commands` 全部通过（P5 全量 pytest + consistency 0 ERROR + verify 9 场景 + shellcheck 0 error + count-tests 不漂移）；P1 33 条 BDD 逐条可追溯至本设计（M1~M10 映射表）。

## 9. 环境隔离声明

[PROD_NOT_TOUCHED] 本阶段仅读取任务目录、协议本体、设计文档与验证记录，未触碰任何生产环境；未读取其他用户 DSH 会话（三平台真实会话仅作设计依据引用，fixture 脱敏由 P4 落地）。

## 10. 修复轮记录（fix1）

> 修复轮（增量模式，TAG0028-P2 fix1）：P2 gate 预跑发现 T075 WARNING——gate_commands 命令不可解析（环境无裸 `pytest` 可执行文件，`command -v pytest` exit 1；实际可用 `python3 -m pytest`，pytest 9.0.3）。方案本体（候选方案 A 选型、影响面梳理、files_to_read、env_constraints、minimal_validation）已评审通过（P2-review.md status=approved），本轮**仅**修正 gate_commands 声明与 timeout 档位，其余已评审内容不动。

### 10.1 gate_commands 修正（裸 pytest → python3 -m pytest）

| key | 修正前 | 修正后 | 原因 |
|-----|--------|--------|------|
| P3 | `pytest` | `python3 -m pytest agate/tests/ -q --tb=short` | T075 WARNING：裸 `pytest` 不可解析（PATH 无 pytest 可执行文件）；`python3 -m pytest` 可用。保留 `-q --tb=short` 紧凑形态供 check-tdd-red.py 读取测试运行器（本任务未声明 P3_formatter，退化为 exit-code-only） |
| P5 | `pytest -q --tb=no` | `python3 -m pytest agate/tests/ -q --tb=no -n auto` | 同上（裸 pytest 不可解析，保留会导致 P5 全量验证 exit 127 红灯）；补 `-n auto` 与交接单 §4 三片命令并行口径一致——unit/regression/integration 三片合跑为一条 P5 命令，逐 key 独立不拼接 `&&` |

- 其余 key（P5_consistency / P5_cmdstream_verify / P5_shellcheck / P5_count_tests）原已是 `python3 ...` / `bash ...` 可解析形态，未含裸 pytest，无需修改。
- 命令均在 worktree 根跑（`python3 -m pytest agate/tests/` 路径口径），与 TAG0027 惯例一致。

### 10.2 timeout_seconds 档位复核

| key | 修正前 | 修正后 | 依据 |
|-----|--------|--------|------|
| P5_timeout_seconds | 300 | 600 | P5 全量 = unit/regression/integration 三片合跑 + `-n auto` 并行；TAG0027 同量级套件（`--reruns 1 -n auto`）声明 600s。本任务无 `--reruns`，但按实际测试量宁高勿低（TPV0093 教训），300s 偏紧、600s 覆盖 |
| P5_consistency / P5_cmdstream_verify / P5_shellcheck / P5_count_tests 的 `{key}_timeout_seconds` | 120（不变） | 120 | 均为单命令短任务（一致性脚本检查 / 9 场景验证 / 3 文件 shellcheck / count-tests），120s 单测类档位足够 |

### 10.3 对下游角色的影响

- **P3 test-designer（check-tdd-red.py）**：测试运行器命令从 `gate_commands.P3` 读取。修正后 P3 = `python3 -m pytest agate/tests/ -q --tb=short`，在本环境可解析（exit 0 可判定，A/B 类错误区分不再受 exit 127 干扰）；test-designer 无需其他调整。
- **P5 verifier**：全量验证跑修正后 P5（`python3 -m pytest agate/tests/ -q --tb=no -n auto`），不再 exit 127。
- 修正不改变命令语义（同一 pytest 套件、同一路径口径），仅修复可执行文件解析路径。

### 10.4 环境隔离

[PROD_NOT_TOUCHED] 本轮仅修改任务目录内 P2-design.md（gate_commands 声明 + 修复轮记录），未触碰生产环境。
