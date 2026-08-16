# agate 项目 roadmap 看板

> 规划层（想做什么/做了没），执行层见 `tasks/active-tasks.md`。roadmap 条目拆出的任务行记录 `roadmap: <条目id>` 关联。

---

## 条目列表

| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |
|----|------|------|------|----------|------|------|
| RM-AG0001 | check-gate P1 标记反引号包裹识别盲区 | done | TPV0091 复盘 §11.1 B1（2026-08-13）| TAG0004 | 2026-08-13 | 2026-08-15 |
| RM-AG0002 | check-tdd-red 无 formatter 时 A/B 类盲区（编译失败误判红灯）| done | TQC0001 复盘 Q3 残留（2026-08-13）| TAG0004 | 2026-08-13 | 2026-08-15 |
| RM-AG0003 | subagent 短命会话制度化重试（空返回自动重试一次 + <1min 告警）| done | TQC0001 复盘 Q4（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-15 |
| RM-AG0004 | P6 视觉验收能力边界：无多模态模型时强制双证据 + 雷同截图降级待复核 | scheduled | TQC0001 复盘 Q7（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0005 | 冒烟验证脚本内置 finally-kill + 进程清理主 Agent 复核 | cancelled | TQC0001 复盘 Q8（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0006 | GUI 自动化框架评估（WinAppDriver/AutoIt）补真实 GUI 交互路径 | scheduled | TQC0001 复盘 Q9（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0007 | UI/UX 质量机制缺失：P1/P2 缺 UX 需求与设计评审、P6 缺视觉质量验收 | scheduled | qtcalc 对比分析 §6（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0008 | 0→1 项目目录结构脚手架：agate 立项时应按最佳实践设计合理目录结构，避免东放一点西放一点 | scheduled | 用户需求（2026-08-13）| TAG0007 | 2026-08-13 | 2026-08-13 |
| RM-AG0009 | code-map + 架构演进纪律：新增文件/代码要从架构设计与设计模式层面考虑，避免胶水式层层堆叠 | scheduled | 用户需求（2026-08-13）| TAG0007 | 2026-08-13 | 2026-08-13 |
| RM-AG0010 | P2 gate 与 C8 映射表契约矛盾：backend 域 P2 无评审角色但 check-gate 硬拦 P2-review.md | done | TPV0090 复盘 M1（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-15 |
| RM-AG0011 | check-gate P5 gate_commands 计数语义模糊（P5* 前缀全算，WARNING 误解主/辅命令）| done | TPV0090 复盘 M2（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-15 |
| RM-AG0012 | 自定义角色机制两瑕疵：dispatch-prompt 无条件注入评审指令到执行角色 + render 脚本角色不存在时 exit 0 | done | 角色体系验证（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-15 |
| RM-AG0013 | 阶段卡缺"同类扫描/影响面梳理"机制层要求：P0-P8 卡无举一反三提示，仅 task P0-brief 局部 | scheduled | 阶段提示词核查（2026-08-13）| TAG0012 | 2026-08-13 | 2026-08-15 |
| RM-AG0014 | 跨平台/外部环境验证的机制边界：supplementable vs verification_env 误用 + verification_env 缺失败处理流程 | scheduled | TAG0005/0009 复盘核实（2026-08-14）| TAG0012 | 2026-08-13 | 2026-08-15 |
| RM-AG0015 | 文档脚本名引用漂移无 gate 兜底：CHECK 2 只捕获 `scripts/` 前缀引用，裸脚本名（phase-cards/rules 全是）完全漏检 + phase-cards/rules 不在 PROTOCOL_FILES（引用检查降级 WARNING）| scheduled | TAG0010/0011 复盘（2026-08-15）+ 实测验证 | TAG0013 | 2026-08-15 | 2026-08-15 |
| RM-AG0016 | subagent 派发编排机制（全阶段）：工作量评估 + 五模式编排（单发/静态拆批/并行/先理解后拆/串行链）+ 并行规则统一；P1/P2 补空白、P3-P6 统一现有分散"按包并行" | scheduled | TAG0010/0011 复盘（2026-08-15）+ 用户需求扩展（全阶段）| TAG0014 | 2026-08-15 | 2026-08-15 |
| RM-AG0017 | self-gate 触发面缺仓库根级文档：README.md/AGENTS.md 不在触发面（改协议语义绕过 self-gate 评审）| scheduled | TAG0010/0011 复盘（2026-08-15）| TAG0013 | 2026-08-15 | 2026-08-15 |
| RM-AG0018 | 复盘/评审发现未接 tech-debt 登记触发点：tech-debt.md 零登记（DEBT0001 前），复盘发现缺口只写进复盘/roadmap 不走 DEBT 路径 | scheduled | 独立观察 + DEBT0001 破冰（2026-08-15）| TAG0013 | 2026-08-15 | 2026-08-15 |
| RM-AG0019 | P0-brief 时效性验证缺失：立项后搁置再启动时，P0-brief 前提（技术路线/依赖/风险）可能已与最新状态漂移（TAG0008 .sh→py 实证），无检测/更新环节 | scheduled | 用户提问（2026-08-15）| TAG0012 | 2026-08-15 | 2026-08-15 |
| RM-AG0020 | 复盘机制统一：模板缺正文结构（只有核对清单）、内容无价值标准、标的矛盾（异常触发 vs 所有任务）、路径矛盾（docs/releases vs docs/reviews）；分层归因 + 执行错误/机制缺口二分 + 措施可落地缺失 | backlog | TAG0013/0014 复盘讨论（2026-08-16）| — | 2026-08-16 | 2026-08-16 |

## 状态标识

| 状态 | 说明 | 何时进入 |
|------|------|----------|
| `backlog` | 待规划 | 新需求/讨论进入 roadmap 时（含来源与日期）|
| `scheduled` | 已拆任务 | 拆任务 → 工作区 tasks/ 建任务目录 + active-tasks.md「待开始」写入任务行（任务行 `roadmap: <条目id>` 关联）|
| `in_progress` | 实施中 | 对应任务进入 P1 起（可选标记，不做强制）|
| `done` | 已完成 | 任务 P8 gate + READY 完成 → 回写 |
| `cancelled` | 取消 | 需求变更/不再需要 → 回写 |

## 条目 id 规则

- 格式：`RM-{项目代号}{编号}`（本仓代号 `AG`，与任务编号 `TAGxxxx` 对齐）。
- 项目局部命名空间内递增，不复用已取消条目的编号。

## 循环规范

1. **需求/讨论 → backlog**：追加 `backlog` 条目，来源列记录需求出处（讨论/评审/复盘），创建列记日期。
2. **条目 → 任务**：拆任务时建任务目录 + active-tasks.md「待开始」区写入任务行（`roadmap: <条目id>`），条目状态改 `scheduled`。
3. **任务完成 → 回写**：P8 gate + READY → 条目改 `done`（或 `cancelled`），更新列记日期。

## 维护规则

1. 只有主 Agent 维护本文件，subagent 不直接写。
2. 条目状态变更与任务看板推进同步（拆任务 → scheduled，完成 → done）。
3. 状态只允许五选一（backlog/scheduled/in_progress/done/cancelled），不写中间态。

---

## RM-AG0001 详情

**check-gate P1 标记反引号包裹识别盲区**

- **问题**：check-gate.py P1 NEED_CONFIRM 检查用行首正则 `^\s*-?\s*\[SUGGEST:` / `^\s*-?\s*\[NO_NEED_CONFIRM\]` 计数。当标记被反引号包住（`` `[SUGGEST: ...]` `` / `` `[NO_NEED_CONFIRM]` ``）时，行首不匹配 → 计数 0；typo 兜底（`grep '\[SUGGEST'` && ! `grep '\[SUGGEST:'`）也不触发（冒号子串仍存在）→ 落入「未检测到 NEED_CONFIRM 声明」WARNING，**不阻断**。
- **影响**：主 Agent 若用反引号包裹标记（markdown 代码样式），P1 gate 静默降级为 WARNING，NEED_CONFIRM 声明形同虚设。中低风险（只影响该标记的强制力，非数据/安全）。
- **建议修复方向**：typo 兜底扩展为「子串存在 + 行首正则不匹配」也报错（类似现有 L121-124 逻辑，改为"有子串但计数为 0"），使反引号包裹被明确拦截而非静默 WARNING。契约格式已在 analyst.md:138-152 / P1-card:78 / task-files.md:186 讲清，无需改文档。
- **验证口径**：新增回归测试——反引号包住 `[SUGGEST: ...]` / `[NO_NEED_CONFIRM]` 时 gate exit 1（而非 WARNING）；合规写法仍通过。
- **攒批说明**：单独立项不值得（一个 gate 正则盲区）。等 gate/协议层问题攒到 2-4 个再拆任务走裁剪 agate（P1-P6，跳过 P7，P2 不可裁剪）。

---

## RM-AG0005 取消说明

**状态**：cancelled（2026-08-13）

**取消理由**：核实后确认**非缺陷**——机制已存在且实测有效：
- `state-machine.md:148` 收尾清单明确要求"调试服务/进程已停止"
- `dispatch-protocol.md:606-607` 要求 P8 产出列出临时服务/进程供主 Agent 清理
- TQC0001 READY 收尾**逐项实查发现并强杀了残留进程**（复盘自述"流程有效"）

冒烟验证的 finally-kill 是**项目侧实现细节**（每个项目冒烟方式不同，agate 不该规定具体实现），不属于 agate 协议 backlog。复盘结论本身是正面案例（收尾兜底生效），非缺陷。若后续要补强，可在 `state-machine.md:148` 加注"冒烟验证启动的进程须由验证者自行 finally-kill，不依赖收尾兜底"——属文档补强，不立项。

---

## RM-AG0007 详情

**UI/UX 质量机制缺失：agate 保证工程质量但不保证 UX 质量**

- **背景**：qtcalc 对比分析（review-qtcalc-basic-vs-qtcalc-comparison.md）——走 agate 的 qtcalc（B）在架构/测试/治理全面领先，但**表达式次显示、键盘输入、UI 样式三项 UX 反而不如没走 agate 的 qtcalc-basic（A）**。B 的 P2 明确"为可测试性让渡视觉打磨"。
- **根因（协议机制）**：
  - `ui_affected` 只触发 **E2E 交互功能测试**（state-machine.md:89-94），不要求视觉/交互质量
  - P2 的 plan-design-review 审的是**架构**（分层/可测性），不是**视觉稿/交互设计**
  - P3 TDD 鼓励 offscreen + objectName 契约 → 抑制视觉打磨
  - P6 视觉验收看"渲染成功"（截图/blocker），无多模态时退化为像素/OCR（RM-AG0004），无"美观/易用"维度
  - **全部 gate 是 exit code，无"用户主观体验"验收标准**
- **影响**：走 agate 的 UI 项目"功能正确但 UX 平庸"；agate 不阻止做 UX，也不要求、不度量、不评审 UX。
- **建议修复方向**：
  1. P1/P2 增加 UX 需求基线（把键盘输入/表达式显示/样式等写成 BDD 可测项 + 视觉验收项）
  2. P2 的 domains 含 frontend 时，plan-design-review 增加视觉/交互维度评审（不只架构）
  3. P6 对 UI 任务强制双证据（截图 + 行为日志）+ 视觉质量 checklist（对齐/间距/反馈/可用性）
  4. 与 RM-AG0004（无多模态视觉能力）关联，落地时一并考虑
- **归属**：独立任务（跨 P1/P2/P6 的协议增强），不并入 TAG0004（TAG0004 是脚本环境适配，本条目是质量机制）

---

## RM-AG0008 详情

**0→1 项目目录结构脚手架：agate 立项时应按最佳实践设计合理目录结构**

- **背景**（用户需求 2026-08-13）：项目从 0→1 开始时，项目文件夹可能还没建立。agate 应该能够按**最佳实践**设计出**合理的目录结构**，不要"东放一点西放一点"。合理的目录文件该建立的就可以建立。
- **现状**：agate 的 P0-brief 只写任务描述/风险/环境，**没有"项目骨架设计"环节**；P1 analyst 分析需求，P2 architect 设计**本次任务**的方案，但都不要求"设计整个项目的目录布局"。
- **问题**：0→1 项目若缺骨架设计，会出现——CMakeLists/源码/测试/文档/构建产物散落、阶段文件与工程文件不同步（qtcalc-basic 复盘问题 C：CMake 引用了尚未存在的文件）、后续每阶段往项目里"加东西"却无整体布局。
- **建议修复方向**：
  1. P1（或 P0）增加"项目骨架"产出：analyst/architect 按技术栈最佳实践输出目录树（如 C++/CMake：src/include/tests/docs/build/deploy；Web：src/components/hooks/pages/api 等）
  2. P2 的 files_to_read + P4 的上下文注入包含项目骨架，实现时遵循既定布局
  3. 骨架作为"第一个可验收产物"（P1 或独立前置阶段），后续阶段产出必须落在骨架布局内
  4. 提供模板（agate/assets/templates/ 下按技术栈的 skeleton-template）
- **归属**：独立任务（协议增加"项目骨架"阶段或产出），与架构演进（RM-AG0009）关联

---

## RM-AG0009 详情

**code-map + 架构演进纪律：新增代码要从架构设计与设计模式层面考虑**

- **背景**（用户需求 2026-08-13）：项目已正常开展时，要有 **code-map** 思路——能找到有效文件位置；当新增文件和代码时，要从**架构设计、设计模式**层面考虑，**不要用胶水一层一层砌砖块**，砌得老高、摇摇欲坠。
- **现状**：agate 每阶段（P2/P4）只对**本次任务**做设计/实现，**无全局架构视角**；P7 一致性只查本次任务范围。新增代码若不在架构约束内，会逐步偏离最初设计（架构漂移）。
- **问题**：
  - 缺"当前架构全貌"的维护物（code-map：模块/层/依赖方向/关键文件索引）——subagent 每次独立上下文启动，不知道项目里有什么
  - 缺"新增代码必须符合架构"的约束（新增文件放哪层、依赖方向、是否引入新抽象 vs 胶水堆叠）
  - 架构随版本演进的变更记录（重构成一等任务 TAG0002 已支持"重构类"任务，但缺"日常增量也要守架构"的防漂移机制）
- **建议修复方向**：
  1. **code-map 维护物**：项目工作区维护 `CODE-MAP.md`（或并入 `agents/project.md`）——模块/层/依赖方向/关键文件/约定；每次 P4 新增文件时更新；P7 一致性核对 code-map 与实际结构是否漂移
  2. **P2 架构演进检查**：新增/修改文件时，P2 必须回答"新文件属于哪层、依赖方向是否合规、是否复用既有抽象 vs 新砌胶水层"
  3. **gate 或 WARNING**：检测"新增文件数量/新增依赖方向"与 code-map 声明的偏离（如新的 include/import 方向违反分层）
  4. **设计模式约束**：P2 候选方案评审增加"设计模式合理性"维度（是否引入合适抽象，避免 if-else 胶水堆叠）
- **归属**：独立任务（协议增加 code-map 维护 + 架构演进纪律），与 RM-AG0008（骨架）、TAG0002（重构一等任务）关联

---

## RM-AG0010 详情

**P2 gate 与 C8 映射表契约矛盾（TPV0090 复盘 M1）**

- **问题**：三层契约不一致——
  - `check-gate.py` P2 L323：**无条件**硬性要求 `P2-review.md` 存在且 status=approved（"P2 评审不可裁剪，必须派发独立 subagent 产出"）
  - `role-system.md` C8 表（L52-56）：backend 域 = "review（P4 后）"，**P2 无触发评审角色**（只有 frontend→plan-design-review、high→plan-eng-review、NEED_CONFIRM→plan-ceo-review 触发）
  - `phase-cards/P2-design.md` L91-96 C8 表：同样 backend 域无 P2 评审
- **后果**：backend 域（low/medium 风险）任务 P2 时，按 C8 表不派评审 → 无 P2-review.md → check-gate exit 1 拦截 → 主 Agent 被迫"自造评审派发"补文件（TPV0090 实测踩坑）
- **影响**：每个 backend 域 P2 都会踩（TPV0091 是 backend+frontend，frontend 触发评审没暴露）
- **建议修复方向（二选一，需设计）**：
  1. C8 表补一句"backend 域 P2 也派 review"（消除契约差，但增加评审开销）
  2. check-gate 对无 C8 触发角色的任务豁免 P2-review 硬性要求（但要保证 P2 评审不裁的原则不破——需定义"无角色时评审退化为 self-review 还是必须派通用 review"）
- **归属**：独立任务（机制契约一致性，涉及 check-gate.py + role-system.md + P2 卡片三层同步）。与 Q2（卡片 phase 契约，TAG0004 内）同类但独立

---

## RM-AG0011 详情

**check-gate P5 gate_commands 计数语义模糊（TPV0090 复盘 M2）**

- **问题**：`check-gate.py` L424，`P5*` 前缀命令都计入 P5 命令数，WARNING "P2 声明了 N 个 gate_commands.P5 命令，请确认已全部执行"。当 P2 声明 `P5/P5_cli_remote/P5_serial` 时计数 3，但实际是"1 主 + 2 辅助"——WARNING 语义模糊，易误解。
- **影响**：轻微（WARNING 不阻断，全执行就通过），但理解成本高，可能误导主 Agent。
- **建议修复方向**：脚本区分"主命令"与"辅助命令"（如 `P5_*` 后缀为辅助），WARNING 文案区分"N 个 P5 命令"与"M 个辅助命令"。
- **归属**：可随 RM-AG0010 或攒批小任务。

---

## RM-AG0012 详情

**自定义角色机制两瑕疵（角色体系验证实测，2026-08-13）**

- **背景**：评估"自定义角色机制是否好用"时实测发现——机制本身可用（模板完整、render 脚本支持 execution-roles/ 与 review-roles/、方法 B 稳妥），但有两个瑕疵：
- **瑕疵 1（模板）**：`agate/assets/templates/dispatch-prompt.md` L10-13 无条件注入"Review 角色特别指令"（产出文件 Header `status:` draft → approved/rejected/needs-revision）。该指令对**评审角色**是必需的，但对**执行角色**（implementer/analyst/test-designer 等）也被注入——执行角色不产评审文件，status 字段语义混乱。实测：render db-specialist（执行角色）后产物含"Review 角色特别指令"。修复方向：按角色类型条件注入（type: review 才注入 status 指令）。
- **瑕疵 2（脚本）**：`agate-render-dispatch-prompt.py` L126-128 角色文件不存在时报错到 stderr，但 **exit 0**（实测 `nonexist-role` → 报错但 exit 0）。主 Agent 可能忽略 stderr 继续走 → 派发失败无声。修复方向：角色文件不存在时 exit 非零（如 exit 2），与"渲染成功"区分。
- **归属**：攒批小任务（模板条件注入 + 脚本 exit code，单点低风险）。

---

## RM-AG0013 详情

**阶段卡缺"同类扫描/影响面梳理"机制层要求（阶段提示词核查，2026-08-13）**

- **背景**：核查 P0-P8 阶段提示词（phase-cards/*.md）时发现——所有阶段卡均无"同类扫描/全仓 grep/影响面梳理/联动"要求。agate 历史多次栽在"修一处漏同类"（M4/M5 的 `[:：]` 只修 check-p6-format.py:84 一处、Q2 只修 P5 卡、TPV0090 backend 域反复踩 P2 契约）。
- **现状**："同类扫描强制要求"只存在于 TAG0005/0006/0007 三个 task 的 P0-brief 里（局部、一次性），**机制层（阶段卡）缺失**——未来其他任务不会有此要求。
- **建议修复方向**：
  1. **P0 卡片**：加"同类/影响面预判"——写 P0-brief 时识别"这个改动会牵动哪些同类/联动处"
  2. **P1 卡片**：加"同类扫描"到产出规格或常见错误——analyst 建立 BDD 时 grep 全仓同类，纳入需求
  3. **P2 卡片**：加"影响面梳理"——architect 画改动影响面（如 ui_affected 64 处消费点），确保联动点同步
- **范围界定（2026-08-13 用户确认）**：**不属于 TAG0005/0006/0007**——那三个 task 只做各自 roadmap 条目的修复（带 P0-brief 已有的局部同类扫描质量保障）；本条目是**协议本体阶段卡增强**，独立 backlog，另行立项（改 phase-cards/*.md 触发 SELF-GATE）。
- **归属**：独立任务（阶段卡协议增强），或并入未来"协议机制增强"类任务。

---

## RM-AG0014 详情

**跨平台/外部环境验证的机制边界（TAG0005/0009 复盘核实，2026-08-14）**

- **背景**：TAG0009 在 Windows CI 排障拉了 11.7 小时（78→29→全绿），复盘归因于"supplementable 是声明非协议"。核实后修正——**主因是机制误用，不是机制缺失**：
- **核实 1：机制误用**——协议已有 `verification_env`（dispatch-protocol.md L884-886）专用于"环境依赖"场景（debug server、测试数据库、临时端口），触发条件含"P0-brief known_risks 含环境依赖"。TAG0009 的 P0-brief **声明了"无法实测 Windows 靠 CI matrix 兜底"**（满足 verification_env 触发条件），但 P1 实际把"真 Windows CI"标成了 `supplementable`（capability_requirements 三态，用于**能力缺失**如缺 vision/skill）——**用错了机制**。跨平台验证是"环境依赖"，不是"能力缺失"。
- **核实 2：真协议空白**——`verification_env` 只定义"如何声明环境"，**没有定义"环境验证失败后怎么办"**：无 CI 轮次预算、无止损轮次、无"一次 CI 验证多个假设"的批处理要求、无 READY 后外部问题归属（原任务补丁 vs 新任务）。11.7 小时拉锯的根源在此。
- **建议修复方向**：
  1. **明确 supplementable vs verification_env 边界**：P1 卡片 + analyst 角色加注——"能力缺失"用 supplementable，"环境依赖/需外部环境验证"用 verification_env；跨平台验证属后者
  2. **补 verification_env 的失败处理协议**：本地无法验证的项，P1 声明时同时列"可验证清单 vs 不可验证清单"；设定每轮 CI 验证多假设的批处理要求；设止损轮次（如 3 轮未收敛必须升级汇报）；定义 READY 后暴露外部问题的归属（补丁 vs 新任务）
  3. **CI 轮次预算进 P1**：risk_level 或专门字段记录"预计外部验证轮次"，让主 Agent 和用户对总时长有预期
- **归属**：独立任务（协议机制增强：dispatch-protocol + P1 卡片 + analyst 角色），与 RM-AG0013（阶段卡同类扫描）同属"协议机制增强"簇。

---

## RM-AG0015 详情

**文档脚本名引用漂移无 gate 兜底（TAG0010/0011 复盘 + 实测验证，2026-08-15）**

- **问题**：`check-protocol-consistency.py` 的 CHECK 2 引用存在性检查用 `REF_RE = (?<![\w/])((?:docs|assets|scripts)/[A-Za-z0-9_./\-]+\.(?:md|sh|ya?ml|py))`（L238）——**只匹配带 `docs/` `assets/` `scripts/` 前缀的相对路径引用**。协议文档（phase-cards/rules/assets）里大量使用**裸脚本名**（`check-gate.py`、`check-tdd-red.py`，无前缀），实测 `'check-tdd-red.py 确认'` → 正则匹配 `[]` → **完全不被捕获**。脚本被删/改名后文档漂移，consistency 0 ERROR 照过。v0.46.0 的 phase-cards 26 处过时 .sh 引用就是实锤（已修但无 gate 防复发）。
- **问题 2（同批）**：`PROTOCOL_FILES`（L52-64）只含 11 个文件 + `agate/assets/` 目录，**不含 `agate/phase-cards/`、`agate/rules/`** → 这些必读卡引用不存在文件时按"非协议文件"宽松降级 WARNING 而非 ERROR。
- **问题 3（同批，2026-08-15 补充，经数据核查修正）**：`NARRATIVE_DIRS`（L74）按**目录**粗分，未按**文件性质**分——导致两类误配：① 历史目录（`archived/` 62.7% 引用漂移、已完成 task 42.7% 漂移）若严格 = 误报海啸；② 活文档（`roadmap.md`/`active-tasks.md`/`debt/`/进行中 task）若宽松 = 漂移漏网（实测：审查报告引用已归档 `archived/docs-2026-08/plans/agate-test-plan-2026-07-01.md` 的原路径触发 ERROR，改归档路径才通过；进行中 task 引用已删脚本不会被抓）。**按文件性质分类**：严格（活文档，引用必须真实）= roadmap.md / active-tasks.md / debt/ / 进行中 task（phase 非 READY/DONE）；宽松（历史/参考，漂移是常态）= archived/ / reviews/ / plans/ / 已完成 task（phase = READY/DONE）。
- **建议修复方向**：
  1. **新增 CHECK 10**：扫描协议文件中的脚本名引用（裸名 + 相对路径），对照 `agate/scripts/` 实际文件，漂移报 ERROR。豁免：UPGRADING 迁移对照表（旧→新命令对照写旧名是有意保留）、assets/formatters/（仍为 sh）、3 个 hook 薄壳（pre-commit-gate.sh 等）、count-tests.sh
  2. **phase-cards/rules 入 PROTOCOL_DIRS**：把 `agate/phase-cards/`、`agate/rules/` 加入协议目录，享受严格引用检查
  3. **NARRATIVE_DIRS 按文件性质重组**：`agate-workspace/debt/` 移出宽松（evidence 应指向真实路径，债的证据不能是死的）；`archived/ reviews/ plans/` 保持宽松（历史/参考，漂移是常态，实测 62.7% 漂移严格=误报海啸）；`roadmap.md`/`active-tasks.md` 保持严格（活看板，引用应真实）。基线已确认（2026-08-15 0 ERROR）
  4. **进行中 task 动态分类**（并入 CHECK 10 实现，2026-08-15 用户确认）：CHECK 2 扫描 `tasks/` 时读 `{task}/.state.yaml` 的 phase——phase ∈ {READY, DONE} 宽松，否则严格。进行中 task 引用已删脚本/归档路径 = 前提漂移 → ERROR 暴露（复用 agate-state-get.py 读取，TAG0013 的 .sh 引用实测会被抓）
- **验证口径**：新增一致性测试——协议文件引用已删脚本名 → ERROR；引用现存脚本 → 通过；UPGRADING/formatters/薄壳豁免路径不误报
- **归属**：独立任务（协议机制增强），与 RM-AG0013/0014 同簇。

---

## RM-AG0016 详情

**subagent 派发编排机制（全阶段，TAG0010/0011 复盘 + 用户扩展，2026-08-15）**

- **背景**：TAG0010 批次 0 卡死（agate_common 整库 + ci-gate-backstop + 3 bats 一次派发，用户中止）；TAG0011 拆 19 批后零卡死。复盘 §3.1 称"P2 批次设计有效"，但**协议本身没有任何批次粒度机制**——"表 E 批次设计"是任务内部临时产物，非协议要求。工作量高的形态不限于 P4——P1/P2 单发 architect/analyst 扛整任务、P3-P6 分散的"按包并行"（P3/P4/P5/P6 卡片各写各的）、多包 P8 releaser 单发，都可能过载。
- **根因**：「任务粒度指引」只存在于 `dispatch-protocol.md` L639-663（产出 ≤3 文件 / 输入 ≤3 个），**无任何其他文件引用它**（P2-design.md / architect.md / 派发模板均无）。且只覆盖"数量上限"，**无工作量评估方法、无编排模式定义、无并行规则**（上限/失败处理/共享文件）。P2 architect 设计批次时看不到粒度约束，主 Agent 派发时靠记忆——渐进披露下不一定读到 dispatch-protocol。
- **现状核查**（全阶段）：
  - P3/P4/P5/P6 有"按包拆分并行"（各卡片独立定义，非统一机制）
  - P7 明确不拆分（一致性需跨文件对照）
  - **P1/P2 无任何拆分/编排机制**——P2 恰是最需要"先理解后拆"的阶段（architect 要先读 P1 全貌才能规划后续批次）
  - 并行规则分散且缺：无并行上限（平台并发 + 主 Agent 上下文）、无并行失败处理（失败批单独 retry vs 全批重跑）、无共享文件统一约束（仅 P4 有）
- **建议修复方向**（统一机制，全阶段适用）：
  1. **工作量评估**：复杂度 = 产出规模/输入规模/改动性质/耦合度/认知负荷 五维评级 → low/medium/high
  2. **五模式编排**：
     - 模式 1 单发（low）：一个 subagent 直接做
     - 模式 2 静态拆批（medium）：批次表（P2 预设计 或 本阶段派发前设计），按批执行
     - 模式 3 并行（无依赖且 ≤medium）：多 subagent 并行 + 共享文件后处理
     - 模式 4 先理解后拆（high/结构不明）：侦察 subagent 读全貌产出拆分方案 → 按方案派执行（并行/串行）→ 合并（轻量拼装由主 Agent/单 subagent；重量整合派整合 subagent）
     - 模式 5 串行链（有依赖）：分批串行
  3. **并行规则统一**：并行上限默认 3（可配置）；失败批单独计 `retries[Pn]` 不重跑成功批；各批只改自己范围、共享文件由主 Agent 统一后处理（P4 约束推广到全阶段）
  4. **落地位置**（单一权威源）：dispatch-protocol.md 新增「派发编排机制」节（升级扩充现有任务粒度指引）；P2-design.md 新增 `dispatch_plan:` 机器字段；各阶段卡片加"编排模式"引用（指向权威节，不重复定义）；dispatch-prompt.md 内联"产出>3 或输入>5 必须分批或说明"兜底
- **验证口径**：`dispatch_plan:` 字段可被 gate 校验（复杂度/模式/并行上限一致性）；派发模板约束主 Agent 每轮可见；模式 4 流程有测试覆盖（侦察→执行→合并 三阶段）
- **参考实施计划（2026-08-15）**：`agate-workspace/plans/agate-dispatch-orchestration-20260815.md`（已通过 plan-eng-review 三轮评审，approved，2026-08-15）——含字段契约（frontmatter 单行 flow YAML + op `dispatch_plan` 子进程读取 + JSON 输出 + 不入 frontmatter-check schema）、6 个 Task（TDD 驱动）、验收标准。实施本条目时作为**参考输入**，不是替代。
- **⚠️ 阶段完整性声明**：**有实施计划 ≠ 裁剪 agate 阶段**。本条目作为任务执行时，仍须走完整 agate 流程（P0 立项 → P1 需求基线 + BDD → P2 设计 → … → P8 发布），P1/P2 须对照本 roadmap 详情 + 参考计划重新产出当前任务自己的需求基线与设计（可引用计划内容，不可跳过阶段）。计划文档只提供"做什么、怎么落地"的既有分析，不豁免本任务的质量 gate。同理适用于其他含参考计划/设计文档的条目。
- **归属**：独立任务（协议机制增强：dispatch-protocol + P2-design.md + 各阶段卡片 + 派发模板 + 角色文件），与 RM-AG0013/0014/0015 同簇，工作量最大，建议单独立项。

---

## RM-AG0017 详情

**self-gate 触发面缺仓库根级文档（TAG0010/0011 复盘，2026-08-15）**

- **问题**：`commit-msg-self-gate.py` 的 `_SELF_GATE_RE`（L38-40）覆盖 `agate/scripts/*.sh|*.py`、`agate/*.md`、`agate/*/*.md`、`SELF-GATE.md`——**不含仓库根级文档**：README.md / AGENTS.md / CHANGELOG.md。
- **影响**：改仓库根级协议文档（README 门面、AGENTS 开发指引）不触发 self-gate WARNING，绕过语义审查。本次文档体系更新（README/AGENTS 重写）即未走独立评审。
- **注意**：复盘原文称"SELF-GATE.md 不在触发面"是**错误**（实测正则包含它）——本条目只补 README/AGENTS，CHANGELOG 变动频繁且非协议语义，豁免。
- **建议修复方向**：`_SELF_GATE_RE` 扩展匹配 `README.md`、`AGENTS.md`（CHANGELOG.md 豁免，理由：频繁变动 + 非协议语义）。SELF-GATE.md 已覆盖，不加。
- **验证口径**：新增测试——staged 含 README.md/AGENTS.md → self-gate WARNING 触发；CHANGELOG.md → 不触发
- **归属**：独立任务（脚本 + 测试），低优先级，可与 RM-AG0015/0016 攒批。

---

## RM-AG0018 详情

**复盘/评审发现未接 tech-debt 登记触发点（独立观察 + DEBT0001 破冰，2026-08-15）**

- **背景**：TAG0001 技术债闭环（v0.43.0）建成后，`agate-workspace/debt/tech-debt.md` **零登记**（目录都不存在）。复盘/评审发现的缺陷只写进复盘文档或 roadmap backlog，从不走 DEBT 路径。独立观察者指出：复盘自己发现"文档脚本名引用漂移无 gate 兜底"（CHECK 10 缺口）并建议修复，但没登记进刚建好的技术债系统——机制建好了，发现渠道没接上。
- **根因**：tech-debt 只有 **retreat 回退**一个自动触发渠道（`check-debt.py --retreat-coverage` 强制登记 source: retreat）。**review / retrospective 来源无登记钩子**——发现者直接把缺口写进复盘/roadmap 就完事，tech-debt 无感知。这不是"习惯问题"，是**机制缺触发点**（review/retrospective 无法机器检测，设计上就没强制，但可在模板层加要求）。
- **本次处置（已落地，2026-08-15）**：
  1. **DEBT0001 登记**：`agate-workspace/debt/tech-debt.md` 首条真账（CHECK 10 缺口，source: retrospective，task_id: RM-AG0015 关联），`check-debt.py` 校验通过——tech-debt 从零破冰，验证系统真实可用
  2. **postmortem-template.md 加"技术债登记"核对行 + 机制说明**：复盘/评审发现缺陷或缺口（影响验收真实性或让未来变更更贵）→ 必须登记 DEBT 或 roadmap backlog，二选一注明去向；未登记 = 机制缺口（引用 DEBT0001 教训）
- **建议修复方向**：
  1. **模板层触发**（已做）：postmortem-template 核对清单加"技术债登记"行——复盘时强制核对"本次发现是否登记了"
  2. **可选增强**：`check-retrospective.py`（P2.12）输出加一行提醒"复盘发现的新缺口请登记 DEBT/roadmap"（纯提醒不拦截，与 P2.12 精神一致）——是否做可评估
  3. **克制原则**：不做"发现必须登记 DEBT"的硬 gate——tech-debt-template 三分法明确"不影响验收也不影响未来成本的不登记"是合法出口，硬登记会让登记簿变垃圾场
- **归属**：本条目主体（模板层 + 提醒）已随本次处置落地，**剩余可选增强**（check-retrospective 提醒）低优先级，可与 RM-AG0017 攒批。

---

## RM-AG0019 详情

**P0-brief 时效性验证缺失（用户提问，2026-08-15）**

- **问题**：P0-brief 是**立项时点的快照**（task/known_risks/executor_env/env_constraints 反映当时状态），状态机把它当恒真前提——P0 完成即锁死，之后任何阶段不再回头校验。任务立项后搁置再启动时（如 TAG0008：8-13 立项写 .sh 路线，8-15 启动时 TAG0010 已全量 Python 化），P0-brief 前提可能已与最新项目状态漂移。若直接按错误 P0 推进实施，产出是**放大版且错误的 task**。
- **现状核查**（无此机制）：
  - P0 卡片「环境自检」（P0-orchestrator.md L29-34）：只查 debug 环境/测试框架/浏览器**运行时可用**，不查 P0-brief 内容是否过时
  - P0 推进条件（L42-44）：四字段齐全 + 环境自检 + 看板行——全是"是否做了"，无"前提是否仍成立"
  - P1 输入校验（P1-requirements.md L30/35）：P0-brief 完成 + 作为输入——**P1 在过时基础上工作**
  - state-machine L77：`P0 --[P0-brief 完成，四字段自查通过]--> P1`——无时效维度
  - 现有 `env_state` 环境一致性验证（state-machine L300-306）只覆盖**运行时资源**（URL/端口），不覆盖**立项前提**（技术路线/依赖/风险）
- **问题分层**：
  1. **检测缺失**：无环节检测"P0-brief 前提 vs 当前状态"是否漂移
  2. **更新缺失**：检测到漂移后，无流程定义"如何更新 P0-brief 并重新进入决策"（轻更新 vs 重新立项/可行性分析）
- **建议修复方向**：
  1. **P0 → P1 前提校验**：启动（含搁置后启动）时，主 Agent 对照当前项目状态核对 P0-brief 四字段前提（技术路线/依赖/风险/环境）是否仍成立；有漂移 → 更新 P0-brief（标注更新日期 + 变更点）
  2. **重启动判断**：漂移严重（技术路线全变/前置任务完成改变依赖）→ 需重新立项分析/可行性分析，而非直接 P1
  3. **P1 analyst 职责扩展**：需求质疑前先校验 P0-brief 前提，发现过时标记 `[P0_STALE]` 交主 Agent
  4. **落点**：P0 卡片加"前提时效性自检" + state-machine P0→P1 转移条件加"前提验证" + P1 卡片加"P0-brief 前提校验"
- **验证口径**：搁置后启动的任务，P0-brief 前提漂移被检测 → 更新或重立项；P1 在验证过的 P0-brief 基础上工作
- **归属**：**并入 TAG0012**（2026-08-15 决策）——改动域与 TAG0012 高度重叠（P0/P1 卡片 + analyst + dispatch-protocol/state-machine），且与 RM-AG0014 同类（声明有时效处理无）；分开做会两轮改同文件。实施时 P1 须按"哪些卡/哪些节"组织 BDD，与 RM-AG0013/0014 一并规划。

---

## RM-AG0020 详情

**复盘机制统一（TAG0013/0014 复盘讨论，2026-08-16）**

- **问题**：复盘机制在协议层面残缺且不自洽：
  1. **模板缺正文结构**：`docs/reviews/postmortem-template.md` 只有"机制触发核对清单"（retry/SCOPE+/gate 等是否触发），**无复盘正文结构**（做得好的/发现的问题/改进措施）——正文靠执行者临场拼（TAG0013 复盘 84 行是拼出来的，非模板定义）
  2. **内容无价值标准**：不定义"什么值得写"——易沦为流水账（复述 P1-P8 过程）/自我表扬（只写做得好的）；有价值的内容是"机制缺口 + 可复用模式 + 归因到可行动层面的问题"
  3. **标的矛盾**：`check-retrospective.py`（P2.12）只在**异常模式**（retry 超限/SCOPE+/override）时提醒复盘；但正常任务（TAG0013 无 retry）也写了复盘（因发现机制缺口）——无统一标的定义
  4. **路径矛盾**：check-retrospective 提示 `docs/releases/v{version}-retrospective.md`，实际先例在 `docs/reviews/retrospective-tag00xx-*.md`——两处不一致
  5. **归因纪律缺失**：不区分"执行错误（agent 没遵守规则 → 修纪律）" vs "机制缺口（协议没定义 → 修协议）"——归因错层，措施落空（如把协议缺陷误判为执行粗心）
  6. **产出流向缺失**：复盘发现机制缺口 → 应流向 roadmap（RM 条目）或 DEBT 登记，但无强制/约定（check-retrospective 提醒行已加，TAG0018）
- **建议修复方向**：
  1. **复盘正文结构模板**：事实基线（客观数据）/ 做得好的 + 可复用模式（问"该固化进协议吗"）/ 发现的问题（分层归因：管理/技术/agate 机制/agent 执行，标注"执行错误 vs 机制缺口"）/ 改进措施（落到文件/字段/gate）/ 核对清单（沿用 postmortem-template）
  2. **标的定义**：①异常模式（retry 超限/SCOPE+/override）→ 强制 ②发现机制缺口（任何任务）→ 强制 ③高价值任务（大型/跨模块/首次新做法/用户要求）→ 建议。正常完成且无机制发现 → 可不复盘
  3. **路径统一**：`docs/reviews/retrospective-{task}-{date}.md`（对齐实际先例），check-retrospective 输出同步
  4. **归因纪律 + 产出流向**：每条问题标"执行错误/机制缺口"；机制缺口 → 立 RM/DEBT；执行偏差 → 更新角色文件/派发模板/阶段卡
  5. **事实依据三层（2026-08-16 补充，核心）**：复盘的机理分析（为什么这么做）不能只靠 git log（结果级）——因果链在主 Agent/subagent 的 session 里，session 会 compact 导致事实源丢失。按可靠性分层：
     - **L1 仓库落盘（永久）**：git log / 产出文件 / orchestrator-log / progress.md
     - **L2 会话 checkpoint（任务期间持续落盘，新增）**：防 compact 的核心保障——orchestrator-log 从"只记决策"扩展为"决策 + 依据"（每次派发记"给了哪些输入/为什么"、每次 gate 判定记"基于什么"）；每个阶段 gate 通过时落盘 `P{n}-checkpoint.md`（本阶段异常/关键判断/subagent 表现）；P8 完成时先落盘 `task-session-summary.md`（任务级过程摘要）
     - **L3 平台 session 导出（补充，可能已 compact）**：OpenCode / Claude Code 会话历史可导出，作补充事实源，不作为依赖
  6. **复盘时机前置（2026-08-16 定稿）**：**过程摘要（L2）在任务完成时立即落盘（趁 session 完整）**，正式复盘在 PR merge main 后基于摘要写——防止 session compact 后事实源丢失。时机链条：`P8 完成 → 落盘 task-session-summary.md → PR merge main → 基于摘要写正式复盘 → 登记 RM/DEBT`
  7. **平台导出工具书（2026-08-16 补充，可做）**：产出 `docs/reviews/session-export-guide.md`——各平台 session 存储位置/导出方法/如何定位某次 subagent 派发过程。找对方法即可用，不作协议硬依赖
- **验证口径**：复盘文档含"做得好的/发现的问题/改进措施"三节 + 每条问题标归因层面 + 措施写落点；check-retrospective 提示路径与实际一致；复盘文档"事实依据"节列出 L1/L2/L3 来源；长任务复盘能在 session compact 后仍写出完整因果链（L2 落盘生效）
- **归属**：独立任务（协议机制增强：postmortem-template + check-retrospective.py + orchestrator-log 扩展 + checkpoint 落盘 + 复盘文档规范 + session-export-guide），与 RM-AG0018（tech-debt 登记触发点）同簇。
