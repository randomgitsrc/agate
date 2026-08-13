# agate 项目 roadmap 看板

> 规划层（想做什么/做了没），执行层见 `tasks/active-tasks.md`。roadmap 条目拆出的任务行记录 `roadmap: <条目id>` 关联。

---

## 条目列表

| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |
|----|------|------|------|----------|------|------|
| RM-AG0001 | check-gate P1 标记反引号包裹识别盲区 | scheduled | TPV0091 复盘 §11.1 B1（2026-08-13）| TAG0004 | 2026-08-13 | 2026-08-13 |
| RM-AG0002 | check-tdd-red 无 formatter 时 A/B 类盲区（编译失败误判红灯）| scheduled | TQC0001 复盘 Q3 残留（2026-08-13）| TAG0004 | 2026-08-13 | 2026-08-13 |
| RM-AG0003 | subagent 短命会话制度化重试（空返回自动重试一次 + <1min 告警）| scheduled | TQC0001 复盘 Q4（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-13 |
| RM-AG0004 | P6 视觉验收能力边界：无多模态模型时强制双证据 + 雷同截图降级待复核 | scheduled | TQC0001 复盘 Q7（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0005 | 冒烟验证脚本内置 finally-kill + 进程清理主 Agent 复核 | cancelled | TQC0001 复盘 Q8（2026-08-13）| — | 2026-08-13 | 2026-08-13 |
| RM-AG0006 | GUI 自动化框架评估（WinAppDriver/AutoIt）补真实 GUI 交互路径 | scheduled | TQC0001 复盘 Q9（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0007 | UI/UX 质量机制缺失：P1/P2 缺 UX 需求与设计评审、P6 缺视觉质量验收 | scheduled | qtcalc 对比分析 §6（2026-08-13）| TAG0006 | 2026-08-13 | 2026-08-13 |
| RM-AG0008 | 0→1 项目目录结构脚手架：agate 立项时应按最佳实践设计合理目录结构，避免东放一点西放一点 | scheduled | 用户需求（2026-08-13）| TAG0007 | 2026-08-13 | 2026-08-13 |
| RM-AG0009 | code-map + 架构演进纪律：新增文件/代码要从架构设计与设计模式层面考虑，避免胶水式层层堆叠 | scheduled | 用户需求（2026-08-13）| TAG0007 | 2026-08-13 | 2026-08-13 |
| RM-AG0010 | P2 gate 与 C8 映射表契约矛盾：backend 域 P2 无评审角色但 check-gate 硬拦 P2-review.md | scheduled | TPV0090 复盘 M1（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-13 |
| RM-AG0011 | check-gate P5 gate_commands 计数语义模糊（P5* 前缀全算，WARNING 误解主/辅命令）| scheduled | TPV0090 复盘 M2（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-13 |
| RM-AG0012 | 自定义角色机制两瑕疵：dispatch-prompt 无条件注入评审指令到执行角色 + render 脚本角色不存在时 exit 0 | scheduled | 角色体系验证（2026-08-13）| TAG0005 | 2026-08-13 | 2026-08-13 |
| RM-AG0013 | 阶段卡缺"同类扫描/影响面梳理"机制层要求：P0-P8 卡无举一反三提示，仅 task P0-brief 局部 | backlog | 阶段提示词核查（2026-08-13）| — | 2026-08-13 | 2026-08-13 |

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

- **问题**：check-gate.sh P1 NEED_CONFIRM 检查用行首正则 `^\s*-?\s*\[SUGGEST:` / `^\s*-?\s*\[NO_NEED_CONFIRM\]` 计数。当标记被反引号包住（`` `[SUGGEST: ...]` `` / `` `[NO_NEED_CONFIRM]` ``）时，行首不匹配 → 计数 0；typo 兜底（`grep '\[SUGGEST'` && ! `grep '\[SUGGEST:'`）也不触发（冒号子串仍存在）→ 落入「未检测到 NEED_CONFIRM 声明」WARNING，**不阻断**。
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
  - `check-gate.sh` P2 L155-159：**无条件**硬性要求 `P2-review.md` 存在且 status=approved（"P2 评审不可裁剪，必须派发独立 subagent 产出"）
  - `role-system.md` C8 表（L52-56）：backend 域 = "review（P4 后）"，**P2 无触发评审角色**（只有 frontend→plan-design-review、high→plan-eng-review、NEED_CONFIRM→plan-ceo-review 触发）
  - `phase-cards/P2-design.md` L91-96 C8 表：同样 backend 域无 P2 评审
- **后果**：backend 域（low/medium 风险）任务 P2 时，按 C8 表不派评审 → 无 P2-review.md → check-gate exit 1 拦截 → 主 Agent 被迫"自造评审派发"补文件（TPV0090 实测踩坑）
- **影响**：每个 backend 域 P2 都会踩（TPV0091 是 backend+frontend，frontend 触发评审没暴露）
- **建议修复方向（二选一，需设计）**：
  1. C8 表补一句"backend 域 P2 也派 review"（消除契约差，但增加评审开销）
  2. check-gate 对无 C8 触发角色的任务豁免 P2-review 硬性要求（但要保证 P2 评审不裁的原则不破——需定义"无角色时评审退化为 self-review 还是必须派通用 review"）
- **归属**：独立任务（机制契约一致性，涉及 check-gate.sh + role-system.md + P2 卡片三层同步）。与 Q2（卡片 phase 契约，TAG0004 内）同类但独立

---

## RM-AG0011 详情

**check-gate P5 gate_commands 计数语义模糊（TPV0090 复盘 M2）**

- **问题**：`check-gate.sh` L247-253，`P5*` 前缀命令都计入 P5 命令数，WARNING "P2 声明了 N 个 gate_commands.P5 命令，请确认已全部执行"。当 P2 声明 `P5/P5_cli_remote/P5_serial` 时计数 3，但实际是"1 主 + 2 辅助"——WARNING 语义模糊，易误解。
- **影响**：轻微（WARNING 不阻断，全执行就通过），但理解成本高，可能误导主 Agent。
- **建议修复方向**：脚本区分"主命令"与"辅助命令"（如 `P5_*` 后缀为辅助），WARNING 文案区分"N 个 P5 命令"与"M 个辅助命令"。
- **归属**：可随 RM-AG0010 或攒批小任务。

---

## RM-AG0012 详情

**自定义角色机制两瑕疵（角色体系验证实测，2026-08-13）**

- **背景**：评估"自定义角色机制是否好用"时实测发现——机制本身可用（模板完整、render 脚本支持 execution-roles/ 与 review-roles/、方法 B 稳妥），但有两个瑕疵：
- **瑕疵 1（模板）**：`agate/assets/templates/dispatch-prompt.md` L10-13 无条件注入"Review 角色特别指令"（产出文件 Header `status:` draft → approved/rejected/needs-revision）。该指令对**评审角色**是必需的，但对**执行角色**（implementer/analyst/test-designer 等）也被注入——执行角色不产评审文件，status 字段语义混乱。实测：render db-specialist（执行角色）后产物含"Review 角色特别指令"。修复方向：按角色类型条件注入（type: review 才注入 status 指令）。
- **瑕疵 2（脚本）**：`agate-render-dispatch-prompt.sh` L63-67 角色文件不存在时报错到 stderr，但 **exit 0**（实测 `nonexist-role` → 报错但 exit 0）。主 Agent 可能忽略 stderr 继续走 → 派发失败无声。修复方向：角色文件不存在时 exit 非零（如 exit 2），与"渲染成功"区分。
- **归属**：攒批小任务（模板条件注入 + 脚本 exit code，单点低风险）。

---

## RM-AG0013 详情

**阶段卡缺"同类扫描/影响面梳理"机制层要求（阶段提示词核查，2026-08-13）**

- **背景**：核查 P0-P8 阶段提示词（phase-cards/*.md）时发现——所有阶段卡均无"同类扫描/全仓 grep/影响面梳理/联动"要求。agate 历史多次栽在"修一处漏同类"（M4/M5 的 `[:：]` 只修 check-p6-format.sh:84 一处、Q2 只修 P5 卡、TPV0090 backend 域反复踩 P2 契约）。
- **现状**："同类扫描强制要求"只存在于 TAG0005/0006/0007 三个 task 的 P0-brief 里（局部、一次性），**机制层（阶段卡）缺失**——未来其他任务不会有此要求。
- **建议修复方向**：
  1. **P0 卡片**：加"同类/影响面预判"——写 P0-brief 时识别"这个改动会牵动哪些同类/联动处"
  2. **P1 卡片**：加"同类扫描"到产出规格或常见错误——analyst 建立 BDD 时 grep 全仓同类，纳入需求
  3. **P2 卡片**：加"影响面梳理"——architect 画改动影响面（如 ui_affected 64 处消费点），确保联动点同步
- **范围界定（2026-08-13 用户确认）**：**不属于 TAG0005/0006/0007**——那三个 task 只做各自 roadmap 条目的修复（带 P0-brief 已有的局部同类扫描质量保障）；本条目是**协议本体阶段卡增强**，独立 backlog，另行立项（改 phase-cards/*.md 触发 SELF-GATE）。
- **归属**：独立任务（阶段卡协议增强），或并入未来"协议机制增强"类任务。
