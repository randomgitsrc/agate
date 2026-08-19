---
phase: P1
task_id: TAG0016
type: problems
parent: P0-brief.md
trace_id: TAG0016-P1-20260819
status: draft
created: 2026-08-19
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
packages: [workflow, dispatch-protocol, state-machine, platform-notes, state-transitions, phase-cards, dispatch-prompt-template, gate-scripts]
domains: [protocol-docs, gate-scripts, test-infra]
capability_requirements:
  - need: python3-runtime
    why: 跑 gate 脚本（check-gate.py / check-protocol-consistency.py / check-p6-provenance.py）、pytest 全量测试、count-tests.sh
    available:
      - "系统 python3（3.12，worktree 基线已验证 916 全绿 + pyyaml + pytest 9.0.3）"
    status: available
  - need: grep-rg
    why: P1 同类扫描（全仓关键词交叉扫描是本任务强制方法论）+ P6 验收阶段对协议文档去重结果的二值锚点判定
    available:
      - "系统 grep / rg"
    status: available
  - need: git-log-diff
    why: AG0026 跨阶段证据引用机制的核心判据（P5 通过 commit 到 P6/P8 验收发起时点之间是否有代码改动）
    available:
      - "系统 git（本仓库已是 git 仓库，worktree 环境）"
    status: available
  - need: ruff
    why: 若 P4 新增/改动 check-protocol-consistency.py / check-p6-provenance.py 的 Python 代码，需静态检查（AGENTS.md 开发约定）
    available:
      - "~/.venvs/agate-dev/bin/ruff（若未装，pip install ruff 可补）"
    status: available
---

[PROD_NOT_TOUCHED]

# P1 需求基线 — agate 协议卫生与测试效率（RM-AG0025 + RM-AG0026 / TAG0016-protocol-hygiene）

> 本文件是 TAG0016 的需求基线（"活基线"）。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`。
> 范围锁定：P0-brief 两条 issue（RM-AG0025 协议文档职责边界与去重 / RM-AG0026 测试重跑审计与跨阶段证据引用）是全部范围，不扩。
> 改动对象是 `agate/` 目录下的协议文档（worktree 自己这份副本）与 `agate/scripts/` 下的 gate 脚本，不是产品代码。

已核对 P0-brief 时效性，无新增漂移（`executor_env.platform` 此前已由主 Agent 标记 `[P0_STALE]` 从 opencode 更新为 claude-code 并记录理由；本次复核逐条对照 P0 卡片「P0-brief 时效性自检（漂移判据）」严重三条——task 目标方案未变、executor_env 平台前提未变（orchestrator 双平台已注册）、known_risks 的"已解决前提"未被他任务解决——均不命中，无需回 P0）。

---

## 1. 需求复述

### 1.1 RM-AG0025：协议文档职责边界与去重

**现状**：agate 协议文档渐进叠加（每版本/任务往顺手文件追加），无职责边界审计，导致同一规则在多份文档中重复出现，其中部分是真实内容复制（维护时需手动同步、容易漂移），部分是已经正确的"单一权威源 + 指针引用"模式（不需要动）。P0-brief 给出 6 处已知重复，但已核实其中至少 2 处的具体文件对/行号已过期或判断有误（详见「同类扫描」）。

**期望行为**：
1. 为每份涉及去重的协议文档建立一句话唯一职责声明（去重前提，不能边改边定义职责）。
2. 对已核实为真实重复的内容做去重（保留一处权威源 + 其余改为指针引用），已经是正确"权威源+指针"模式的位置保持不变。
3. 新增/扩展 gate 机制，让"同一关键词/规则在多处协议文件独立展开成完整段落或表格"这类问题被自动检测（区分"内容真复制"与"合法引用/摘要"），防止本次修完又在下个任务复发。

### 1.2 RM-AG0026：测试重跑审计与跨阶段证据引用

**现状**：同一任务全量测试套件在流程中最多可能被完整执行数遍：P5 首跑（必然）+ P5 修复后重跑（条件，测试失败时）+ P6 refactor 任务独立 regression.log（条件，仅 `change_type: refactor` 任务）+ P8 阶段 bump-version 后重跑 `gate_commands.P5`（必然）。当前 pytest 套件单次约 106-115s（HANDOFF-TAG0016.md 声明的量级参考），重复执行会累积可观的等待时间。

**期望行为**：
1. 产出一份全量重跑点审计（逐点标注"必然发生"或"条件发生"及触发条件）。
2. 定义 P6 引用 P5 证据的核心机制：P5 全绿 且 P6 验收发起时点与 P5 通过 commit 之间无代码改动 → P6 regression 结果可引用 P5 产物，不必重跑；并定义清楚"何时不可复用"的边界（如 P6→P4 修复后重新到达 P6）。
3. 明确 P8 现状（已核实：主 Agent 在 bump-version 后重跑一次 `gate_commands.P5`，不是文档原始描述里让人误解的"再额外全量跑一次"）；本任务要"精简"的对象是这一次重跑的范围/触发方式，不是砍掉这唯一一次验证。
4. xdist 试点：仅在真实 CI（4 核）环境验证加速效果，不在本地单核环境下空测，且不与并行派发的资源密集型串行规则冲突。

---

## 2. 隐含需求识别（每次过全维度）

- **回归底线（数据/兼容）**：Linux 现有 916 pytest 全绿 + `check-protocol-consistency.py --strict` 0 ERROR 是回归底线（HANDOFF-TAG0016.md 已确认）。去重迁移内容、新增 CHECK、改造 provenance 审计，任何一步都不能让这条底线变红。→ BDD-17
- **既有正确模式不能被误伤**：`agate/dispatch-protocol.md`（L972）、`agate/state-machine.md`（L231-233）、`agate/git-integration.md`（L162）对 Pre-commit 清单已经采用"单一权威源（WORKFLOW.md）+ 指针引用"模式，不是重复源。本任务的去重动作和新增防复发 gate 都不能把这几处正确模式误判成"需要修的重复"而改动或报错。→ BDD-7、BDD-10
- **锚点失效风险**：`check-protocol-consistency.py` 的 CHECK 2（内部引用存在性）/ CHECK 3（硬编码行号）/ CHECK 9（协议-脚本结构对齐锚点表）依赖协议文档当前的标题/路径/关键词位置。去重迁移内容会移动这些位置，每批改动后必须重新跑 consistency 确认锚点未失效（P0-brief known_risks 已提及）。→ 隐含约束，贯穿 BDD-2~8
- **BDD 判据不能绑定具体行号**：dispatch-context 客观证据已指出 P0-brief 给的多个行号锚点（`dispatch-protocol L1207`→实际 L1291、`state-machine L215`→实际是裁剪条件非 pre-commit 清单）在本次派发前就已经漂移。BDD 判据必须绑定"标题/内容存在与否"而非行号，否则 BDD 本身在下次协议改动后又会过期。→ 全部 BDD 遵循此约束
- **self-gate 触发**：本任务改动 `agate/*.md`、`agate/**/*.md`、`agate/scripts/*.py` 触发 SELF-GATE.md（仓库根文件，非 `agate/SELF-GATE.md`）——commit message 需含 `self-gate-review:` 或 `self-gate-skip:`，且大概率需要真派发 protocol-alignment-review（Layer 1 语义审查），因为本任务恰好是 LIMITATIONS.md 局限 5 描述场景的实例（协议文档内部一致性问题）。→ 隐含需求，P4/P8 阶段需落实
- **测试先行（TDD 策略）**：新增 CHECK（防复发机制）和 check-p6-provenance.py 的证据引用审计都是脚本逻辑改动，须遵循 AGENTS.md「改脚本的工作流」（先加失败测试→改脚本→绿）。批量文档去重是机械改动，边际测试成本高，采用 HANDOFF-TAG0016.md 建议的"grep 断言审计测试"策略（写一个断言"去重后关键词只在权威源出现"的回归测试，覆盖全部去重项）。→ P3 阶段落实
- **roadmap 回写**：任务完成后需回写 RM-AG0025 / RM-AG0026 两条 roadmap 条目状态为 done（WORKFLOW.md「roadmap 循环」）。→ P8 阶段
- **复盘**：本任务规模大、涉及协议自身机制变更，符合 HANDOFF-TAG0016.md 第 8 节"复盘按 agate 自身变更流程归档"的要求。→ P8 阶段
- **平台无关**：改动全部是 Markdown 文本 + Python 脚本（无 bash 新增，2 个目标脚本均已是 `.py`），不引入 Unix-only 假设；xdist 试点命令本身平台无关，只是验证环境限定 CI。→ BDD-15、BDD-18

---

## 3. 同类扫描（全仓关键词交叉扫描 + 逐条判定，强制节）

> 方法：对 P0-brief 六条已知重复 + dispatch-context 客观证据提示的疑点，逐条用 grep/rg 扫全仓，记录命中数量与文件清单，逐条判定"本次处理/不处理 + 理由"。扫描命令均为可复现的字面 grep，供 P2/P6 复核。

### 3.1 平台适配（P0-brief 描述 ×3）

命中：`grep -rn "平台适配" agate/*.md agate/phase-cards/*.md agate/rules/*.md` → 8 处命中，分布在 `WORKFLOW.md`（×2：目录索引行 + L461 正文小节标题）、`dispatch-protocol.md`（×1：L1291 正文小节标题）、`platform-notes.md`（×2：文件标题 + L47 正文小节标题）、`AGENTS.md`（×1：索引表引用）、`loop-orchestration.md`（×1：引用 dispatch-protocol 平台适配的 issue 号）、`phase-cards/README.md`（×1：索引表引用）。

判定：**真实内容重复源 = 3 处**（WORKFLOW.md L461-468 / dispatch-protocol.md L1291-1309 / platform-notes.md 全文 156 行），P0-brief"×3"结论成立。其余 5 处（AGENTS.md、loop-orchestration.md、phase-cards/README.md 的引用行）是合法索引/交叉引用，不构成重复，本次不处理。三处真实内容重复源角度不同：WORKFLOW.md 是一句话摘要+索引；dispatch-protocol.md 侧重"派发机制怎么调用"（issue 坑、subagent_type 用法）；platform-notes.md 是能力矩阵 + Windows 安装指南（独家内容最多，应作权威源）。→ **本次处理**：platform-notes.md 定为权威源，WORKFLOW.md 与 dispatch-protocol.md 对应小节收窄为摘要+指针（BDD-2）。本条不留给 P2 二次判断权威源归属——上述独家内容量对比（能力矩阵 + Windows 安装指南 vs 另两处的一句话摘要/调用侧说明）已经充分，无需 P2 重新调查判断。

### 3.2 阶段门槛（P0-brief 描述 ×2）

命中：`grep -rln "阶段总览\|可判定门槛规范" agate/*.md` → `orchestrator-template.md`、`loop-orchestration.md`、`role-system.md`、`WORKFLOW.md`、`dispatch-protocol.md` 共 5 个文件。

判定：**真实内容重复源 = 2 处**（`WORKFLOW.md` L280「P1-P8 阶段总览」完整表格 / `dispatch-protocol.md` L948「可判定门槛规范」完整表格），P0-brief"×2"结论成立——两表都描述"进入下一阶段的门槛条件"这同一组语义，只是颗粒度不同（WORKFLOW 表含角色/评审映射的概览颗粒度；dispatch-protocol 表含逐条可执行 grep 命令的操作颗粒度）。其余 3 处（orchestrator-template.md/loop-orchestration.md/role-system.md）均为"见 WORKFLOW.md 阶段总览"式纯引用，不构成重复，本次不处理。→ **本次处理**：明确两表的分工边界（概览颗粒度 vs 操作颗粒度），任一表的门槛值变化时另一表只需要引用不需要跟着改字面值（BDD-3）。

### 3.3 派发 prompt 双源（P0-brief 描述"双源仍在"）

命中：`dispatch-protocol.md`「派发 prompt 模板」节（L429-628，主模板约 87 行 + 阶段特定提示约 115 行）与 `assets/templates/dispatch-prompt.md`（全文 259 行）。

判定：**真实重复，且分叉程度比 P0-brief 描述更严重**——`dispatch-prompt.md` 文件头自称"与 dispatch-protocol.md 保持同步，协议文件为权威来源"，但实测比对发现 `dispatch-prompt.md` 已经比 `dispatch-protocol.md` 内联版多出「能力补充说明」「能力自查（强制，BDD-12）」「Review 角色特别指令」「P4 回退派发追加」「证据日志格式约定（M1.3a）」「项目占位符映射」「返回前自检（强制）」「返回格式（修改类任务）」等独立小节，这些内容在 `dispatch-protocol.md` 里完全没有。这不是"完整版 vs 内联摘要版"的关系，是两份文件各自独立增补内容导致的**真实分叉**（N6 修过一次，之后又分叉），验证了 P0-brief"双源仍在"的判断准确，且问题比预期更重。→ **本次处理**：确定唯一权威源，另一份收窄为指针引用（BDD-4）。

### 3.4 Pre-commit 清单（P0-brief 描述 ×2，经核实不成立）

命中：`grep -rln "Pre-commit 检查" agate/*.md agate/rules/*.md` → `dispatch-protocol.md`、`git-integration.md`、`state-machine.md`、`WORKFLOW.md` 共 4 处。

判定：**P0-brief 的猜测不成立**——只有 `WORKFLOW.md` L303「Pre-commit 检查总览」是完整表格（含 check-state-yaml.py 等各校验脚本、触发条件、行为的 10 行表格）。其余 3 处（`dispatch-protocol.md` L972、`state-machine.md` L231-233、`git-integration.md` L162）都是"详见 WORKFLOW.md《Pre-commit 检查总览》——权威唯一来源，本文件不重复维护"式纯指针句，不复制任何表格内容。P0-brief 给的"state-machine.md L215"这个具体行号已过期/指错位置——该行号附近实际是裁剪条件相关内容，真正的 Pre-commit 指针在 L231。→ **本次不处理**（不是重复源，已经是本任务应该推广到其余重复项的正确目标模式）；唯一需要做的是防复发 gate 落地后不能把这 3 处正确的指针句误判为"需要修的重复"（BDD-7）。

### 3.5 重试上限（P0-brief 描述"state-machine vs dispatch-protocol"，经核实配对文件不准）

命中：`grep -rln "^## 重试上限" agate/*.md agate/rules/*.md` → 仅 `state-machine.md`（L383-394）与 `rules/state-transitions.md`（L56-67）两处含完整表格标题；`dispatch-protocol.md` 只在 L1081/L1087 引用"见 state-machine.md 重试上限表"（未复制数值），不构成第三份重复源。

判定：**真实重复源是 state-machine.md 与 rules/state-transitions.md**，P0-brief 猜测的配对文件（dispatch-protocol.md）不准确，dispatch-context 客观证据已指出此点，此处核实确认。两份表格数值完全一致（P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2）。更关键的是：`rules/state-transitions.md` 文件头自述"权威源：agate/state-machine.md"，但正文却把完整表格数值复制了一遍而非采用指针模式——这与它自己声明的"权威源"关系矛盾，也与 3.4 节已验证有效的"单一权威源+指针"模式不一致。→ **本次处理**：`rules/state-transitions.md` 改用指针模式（BDD-5）。

### 3.6 重试上限数字散落 8 张阶段卡片（P0-brief 未覆盖，dispatch-context 客观证据提示的新发现）

命中：`grep -n "MAX=" agate/phase-cards/*.md` → 8 个文件全部命中，各写死本阶段一个 MAX 数字（如 `P1-requirements.md:26` "P1 MAX=3"、`P6-acceptance.md:25` "P6 MAX=2"），且每处都紧邻一句"→ 读 agate/rules/state-transitions.md 确认 retry 上限"的引用。

判定：**这是 P0-brief 六处已知重复之外、经系统扫描新发现的第三类重复模式**——不是"整段/整表复制"，而是"单个数值散落写死在引用句旁边"。当前共 10 处存有 MAX 数字（state-machine.md 权威表 + rules/state-transitions.md 复制表 + 8 张卡片各 1 个内联数字），任何一次调整某阶段 MAX 值都需要同步这 10 处，人工同步极易漏改。→ **本次处理**：卡片内联数字可以保留（阅读体验需要就近可见），但必须被防复发 gate 纳入跨文件数值一致性检测范围，不一致时报错（BDD-6、BDD-9）。这正是 dispatch-context 约束 1 要求的"系统排查而非只修已知 6 处"的典型例证。

### 3.7 职责定位混乱（P0-brief 描述性问题，非关键词扫描可穷举）

判定：这是定性问题（WORKFLOW.md 塞了 gate 命令细节/Pre-commit 清单/平台适配摘要等本不属于"主流程入口"职责的内容；dispatch-protocol.md 塞了派发编排机制等内容），无法用单一 grep 关键词穷举扫描，依赖 3.1 建立的职责声明表逐条核对。→ **本次处理**：BDD-1 建立职责声明表后，BDD-8 做一次抽查式核对（不要求逐字重排全部内容，P2 设计阶段列出具体迁移清单）。

### 3.8 结论汇总

| 编号 | P0-brief 描述 | 核实结论 | 处理 |
|------|--------------|---------|------|
| ① 平台适配 | ×3 | 成立，3 处真实内容重复 | 处理（BDD-2） |
| ② 阶段门槛 | ×2 | 成立，2 处真实内容重复 | 处理（BDD-3） |
| ③ 派发 prompt 双源 | 双源仍在 | 成立且分叉比预期更严重 | 处理（BDD-4） |
| ④ Pre-commit 清单 | ×2 | **不成立**，已是正确指针模式 | 不处理，仅防误伤（BDD-7） |
| ⑤ 重试上限（文档级） | state-machine vs dispatch-protocol | 配对文件猜错，真实是 state-machine vs rules/state-transitions.md | 处理（BDD-5） |
| ⑥ 职责定位混乱 | 定性问题 | 成立，非结构化 | 处理（BDD-1、BDD-8） |
| 新增：重试上限（数值级，8 卡片） | 未在 P0-brief 六处之列 | 新发现的第三类重复模式 | 处理（BDD-6、BDD-9） |

即使是"已确认只此一处/不构成重复"的 ④，也已显式写出核实过程与理由，不留空白判定。

---

## 4. BDD 验收条件

### RM-AG0025 — 职责声明表（去重前提）

#### BDD-1: 职责声明表建立且覆盖全部去重对象文档
- Given P2 设计阶段准备产出去重方案
- When 读取 P1-requirements.md（本文件）
- Then 「同类扫描」结论已为 WORKFLOW.md / dispatch-protocol.md / state-machine.md / platform-notes.md / rules/state-transitions.md / phase-cards/*.md 六类文档给出去重方向（3.8 结论汇总表），P2 必须先补全每份文档的一句话唯一职责声明后才能产出具体去重方案，不允许边改边定义职责

### RM-AG0025 — 平台适配去重

#### BDD-2: 平台适配内容收敛为单一权威源
- Given 去重前 WORKFLOW.md「## 平台适配」、dispatch-protocol.md「## 平台适配」、platform-notes.md 三处均含平台相关实质内容
- When 去重方案落地后运行 `grep -rn "平台适配" agate/WORKFLOW.md agate/dispatch-protocol.md agate/platform-notes.md`
- Then platform-notes.md 保留完整平台能力矩阵与 Windows 安装指南（权威源），WORKFLOW.md 与 dispatch-protocol.md 对应小节均改为一句话摘要 + 指向 platform-notes.md 的指针引用，不再独立展开平台能力表格/坑位描述

### RM-AG0025 — 阶段门槛表去重

#### BDD-3: 阶段门槛表分工明确、数值单一来源
- Given WORKFLOW.md「P1-P8 阶段总览」与 dispatch-protocol.md「可判定门槛规范」两表并存
- When 去重方案落地后任一阶段的门槛条件发生变更
- Then 只需要修改一处（指定其中一份为该信息的权威来源），另一份通过指针引用该权威来源，不需要人工同步修改两处字面值；两表现有的角色映射颗粒度与可执行 grep 命令颗粒度分工在文档中显式声明

### RM-AG0025 — 派发 prompt 双源收敛

#### BDD-4: 派发 prompt 模板单一权威源
- Given dispatch-protocol.md「派发 prompt 模板」内联版与 assets/templates/dispatch-prompt.md 当前已产生实质分叉（后者含前者没有的多个独立小节）
- When 去重方案落地
- Then 两文件中仅一份保留完整模板正文（权威源），另一份仅保留指针引用（不展开完整段落），且两份文件各自的文件头都显式声明"本文件是否为权威来源"，避免再次出现"声明同步但实际分叉"的矛盾状态

### RM-AG0025 — 重试上限表去重

#### BDD-5: 重试上限表单一数值来源（文档级）
- Given state-machine.md「## 重试上限」与 rules/state-transitions.md「## 重试上限」两份表格数值当前完全一致
- When 去重方案落地
- Then rules/state-transitions.md 的重试上限表格改为指针引用 state-machine.md（不再复制数值表），且该文件头已有的"权威源：state-machine.md"声明与实际内容行为一致（不再出现声明权威源却复制表格的矛盾）

### RM-AG0025 — 重试上限数值散落收敛（8 张阶段卡片）

#### BDD-6: 阶段卡片内联 MAX 数字与权威表不同步时可被检测
- Given 8 张 agate/phase-cards/P{N}-*.md 各自内联展示本阶段 MAX 数字（如"P1 MAX=3"），权威数值来源为 state-machine.md「## 重试上限」表
- When 某次修改只改了 state-machine.md 的某阶段 MAX 值，未同步对应阶段卡片的内联数字
- Then 防复发 gate（BDD-9）运行后报 ERROR，明确指出"哪张卡片的内联数字与权威表不一致"，不再是无人发现的隐患

### RM-AG0025 — 已正确模式不被误伤（回归防护）

#### BDD-7: Pre-commit 清单去重模式保持不变
- Given WORKFLOW.md「Pre-commit 检查总览」是唯一完整表格，dispatch-protocol.md / state-machine.md / git-integration.md 三处已是"详见 WORKFLOW.md——权威唯一来源，本文件不重复维护"式指针（非重复内容）
- When 本任务的去重方案与防复发 gate 落地后
- Then 这三处指针引用保持原样不变（不被防复发 gate 误判为"需要去重的重复源"而报错、不被去重方案误改），`python3 agate/scripts/check-protocol-consistency.py --strict` 仍 0 ERROR

### RM-AG0025 — 职责定位收敛

#### BDD-8: 协议文档实际内容与职责声明表一致
- Given BDD-1 建立的职责声明表已确定每份文档的唯一职责
- When P6 验收阶段抽查 WORKFLOW.md、dispatch-protocol.md 各至少 1 处曾被认定"职责定位混乱"的内容段落（如 WORKFLOW.md 中的平台适配摘要、dispatch-protocol.md 中的派发编排机制归属）
- Then 抽查的内容段落与该文档在职责声明表中的职责描述相符（要么内容已迁移到正确归属文档，要么该段落被职责声明表显式认定为"合理保留在此，理由：xxx"）

### RM-AG0025 — 防复发机制（可判定 gate）

#### BDD-9: check-protocol-consistency.py 新增跨文件数值/规则一致性检测
- Given 当前 check-protocol-consistency.py 已有 CHECK 1-11，其中 CHECK 4（gate_commands 键集合跨文件一致）是跨文件比对数值集合一致性的既有实现模式
- When 本任务新增一项 CHECK（如 CHECK 12），扫描协议文档中被标记为"权威表格/权威数值"的内容块（至少覆盖重试上限表 state-machine.md vs rules/state-transitions.md、8 张阶段卡片内联 MAX 数字）
- Then 数值不一致时该 CHECK 报 ERROR（`python3 agate/scripts/check-protocol-consistency.py` 非 0 退出），消息含具体文件名与不一致的数值对；数值一致时该 CHECK 报 OK，整体 0 ERROR

#### BDD-10: 合法引用/摘要不被新 CHECK 误判为重复
- Given 协议文档中存在合法的多源引用场景：① 含"详见/见 XXX.md/权威源：XXX"等指针句式的内容块（如 3.4 节已验证的 Pre-commit 三处指针）；② 模板文件被阶段卡片间接引用但未展开完整正文
- When BDD-9 新增的 CHECK 运行
- Then 上述两类场景不产生 ERROR/WARNING；仅当同一数值/规则文本在两处以上**独立展开成完整段落或表格**（而非一句指针）时才报错——`python3 -m pytest agate/tests/` 全绿 且 该 CHECK 对当前仓库存量的正确"权威源+指针"模式（3.4/3.7 节列出的位置）实测 0 误报，作为该 CHECK 落地不误伤存量正确用法的验证依据

### RM-AG0026 — 全量重跑点审计

#### BDD-11: 全量重跑点审计表产出
- Given RM-AG0026 issue 描述"同一任务全量测试最多数遍"但未给出精确的必然/条件触发清单
- When P2/P4 阶段落地本条
- Then 产出一份审计记录（落在协议文档或 `{AGATE_WORKSPACE}/debt/` 均可），逐点列出 P5 首跑（必然）/ P5 失败重试（条件：测试失败）/ P6 refactor 独立 regression.log（条件：仅 `change_type: refactor` 任务）/ P8 阶段重跑 `gate_commands.P5`（必然）四个重跑点，并标注每点当前是"不可省的必要验证"还是"BDD-12/BDD-14 机制落地后可被引用证据替代"

### RM-AG0026 — 跨阶段证据引用核心机制

#### BDD-12: P6 引用 P5 证据的可判定"无改动"校验标准
- Given P6-acceptance.md 当前的 refactor 口径要求独立跑一次全量 regression.log（与 P5 gate_commands.P5 的测试范围高度重叠）
- When P6 验收阶段声明"引用 P5 证据，不重跑"
- Then check-p6-provenance.py 新增一道审计：读取 P5 gate 通过时的 commit hash 并与 P6 验收发起时点的当前 commit/暂存区状态比对，执行 `git diff <P5通过commit>..HEAD --name-only` 排除仅含协议产出文件（`{AGATE_WORKSPACE}/tasks/**` 下的 P{N}-*.md / .state.yaml 等，不含被检查任务自身写的源码）的改动后：非产出文件的 diff 为空 → 判定"无代码改动"成立，P6-acceptance.md 允许标注引用 P5-test-results/ 路径而不产出独立 regression.log；diff 非空 → 判定不成立，gate 仍要求独立 regression.log。**"P5 gate 通过时的 commit hash"当前无处可直接读取**——经核实 `.state.yaml` 现有 schema（字段为 task_id / phase / status / retries / retry_count / updated）不含 commit hash 字段，`P5-test-results/` 里的 commit 提及是格式不统一的自由文本、不是可稳定 parse 的结构化字段；这是一次需要 P2 新增的 schema 变更（选定落在 `.state.yaml` 新字段还是 `P5-test-results/` 新增结构化 provenance 头，及对应的解析规则），不是读取既有字段。

> 补充说明（数据维度，若字段落在 `.state.yaml`）：新增的 commit hash 字段须声明为**可选**，缺失时回退到强制重跑（不要求 TAG0001~TAG0015 等存量归档任务的 `.state.yaml` 补填该字段）。避免 check-state-yaml.py 未来把该字段设为必填后，历史任务的 `.state.yaml` 被动触发校验时报错。

#### BDD-13: 不可复用边界——P6 退回 P4 修复后重新到达 P6
- Given 任务从 P6 验收失败退回 P4 修复 bug，重新走到 P6
- When 该任务再次尝试声明"引用 P5 证据"
- Then BDD-12 的 git diff 校验检测到 P4 阶段产生的非产出文件代码改动（diff 非空），强制判定不可复用，check-p6-provenance.py 该审计项报错拦截"引用 P5 证据"的声明，必须重新执行 P5 全量测试（重新产出 P5-test-results/）后 P6 才能验收通过——即该边界由 git diff 结果自动判定，不依赖人工声明或记忆

### RM-AG0026 — P8 重跑范围精简

#### BDD-14: P8 阶段 P5 重跑现状确认与精简方向
- Given P8-release.md 现状（已核实）是"主 Agent 必须亲自执行……bump-version 后重跑一次 P5 gate（`gate_commands.P5` exit 0 + failed==0）"，不是文档原始描述里容易被误解的"再额外全量跑一次"
- When P2 设计阶段基于 BDD-12 的无改动校验机制定义具体精简方案
- Then 精简后的 P8 仍必须保留至少一次"bump-version 后重新确认测试全绿"的客观验证动作（不可被砍掉——发布准备阶段的最后一道回归防线不可移除）；精简的对象是这次验证的**范围/执行方式**（如：若 BDD-12 定义的无改动校验判定 P8 发起时点距 P5 通过点确实无代码改动，则 P8 可复用同一份 P5-test-results/ 而非重新执行完整命令；一旦声明期间存在任何代码改动则仍须完整重跑），而非取消这道验证本身

### RM-AG0026 — xdist 试点

#### BDD-15: xdist 试点仅锚定真实 CI 环境验证
- Given 本地开发环境为单核（P0-brief env_constraints.debug_env 已声明"本环境为 Linux；xdist 加速需真实 CI（ubuntu-latest 4 核）验证"）
- When P5 阶段引入 `pytest -n auto` 试点
- Then 验收依据是 CI（GitHub Actions ubuntu-latest runner）上该 xdist 命令相较于非 xdist 命令的实际耗时对比（读取 CI job 日志的执行时长数字），本地环境跑出的任何耗时数字不得作为"已验证加速效果"的证据写入验收结论；该 xdist 命令仅用于 P5 单发场景（一个 verifier subagent 内部跑 `pytest -n auto`）

#### BDD-16: xdist 试点不破坏并行派发的资源隔离规则
- Given dispatch-protocol.md「并行规则」第 4 条已将"全量测试套件跑 xdist / 多进程并发"列为资源密集型判据之一（命中时批次间默认改为串行，不并行）
- When 本任务为 P5 单发场景引入 xdist 试点后
- Then 「并行规则」第 4 条的判据描述保持不变（xdist 命令仍被列为资源密集型场景，多个并行 subagent 各自跑 xdist 的情形仍默认串行不并行），不因为本任务给单发场景引入了 xdist 就放松这条隔离规则

### 回归底线与平台兼容

#### BDD-17: Linux 回归基线不被破坏
- Given 当前基线是 916 pytest 全绿 + `check-protocol-consistency.py --strict` 0 ERROR（HANDOFF-TAG0016.md 已确认的 worktree 基线）
- When 本任务任一阶段（P2-P8）产出改动后
- Then `python3 -m pytest agate/tests/` 全绿（用例总数只增不减，若确需减少必须在对应阶段产出中显式声明理由）+ `python3 agate/scripts/check-protocol-consistency.py --strict` 0 ERROR + `bash agate/tests/scripts/count-tests.sh` 计数与文档声明一致

#### BDD-18: Windows 兼容性仅作增量声明
- Given 本任务的开发/验证环境是 Linux worktree，无法在 Windows 环境实测
- When P6 验收 / P8 发布准备阶段撰写涉及 Windows 兼容性的结论
- Then 表述仅能是"静态检查通过（未新增裸 `python3` / Unix-only 路径假设）+ CI Windows matrix 的 `-m windows_smoke` 冒烟通过"，不得出现"已在 Windows 实测验证"类表述；若本任务改动触及 platform-notes.md「Windows 原生」章节，必须保持该章节现有安装指南步骤的准确性（不因去重误删或误改指令）

### 防复发机制落地入口

#### BDD-19: 新增协议内容的归属指引可被后续 self-gate 审查依据
- Given known_risks 提到"生成性扫描（新内容塞错文件）"是防复发要求之一，LIMITATIONS.md 局限 5 已确认协议文档自身一致性依赖 SELF-GATE.md Layer 1（protocol-alignment-review）人工语义审查
- When BDD-1 的职责声明表建立后
- Then 每份去重涉及的协议文档文件头或紧邻主标题处新增一行"本文件职责边界"声明（引用职责声明表对应条目）；后续任何 agate 自身改造任务派发 protocol-alignment-review 时，审查角色能读到这行职责声明来判断"本次改动是否加入了不属于本文件职责的内容"——本任务不要求新增脚本强制拦截生成性错误（该判断仍是语义判断，见 LIMITATIONS.md 局限 5），但审查所需的职责声明本身必须先存在

---

## 5. 待确认清单

[NO_NEED_CONFIRM]

说明：本次分析新发现的第三类重复（8 张阶段卡片内联 MAX 数字散落）虽超出 P0-brief 列出的 6 处已知重复，但属于 dispatch-context 约束 1 明确要求的"系统排查而非只修已知 6 处"范畴内（dispatch-context objective_info 已将此案例作为系统扫描方法论的必要示例给出），未超出 P0-brief 锁定的 RM-AG0025 范围本身，不构成需要问用户的范围外扩，故不判定为需人工确认的阻塞项。P8 重跑范围具体如何精简（BDD-14）属于"怎么做"的设计决策，留给 P2 architect 处理，不在 P1 阶段预先拍板。

---

## 6. 裁剪说明

无裁剪，全部走 P1-P8。理由：按 WORKFLOW.md「风险矩阵」，本任务是跨模块改动（协议文档去重涉及 ≥5 个协议文件的结构调整 + gate 脚本机制变更），且机制交叉（去重结果影响 CHECK 2/3/9 锚点、防复发新 CHECK 影响 CI 门禁、跨阶段证据引用机制影响 P6/P8 gate 判定逻辑，≥2 个子系统交互），属于"中改动"矩阵格的完整 P1-P8（P6 不可裁剪，本任务改动涉及 gate 脚本本身，验收阶段尤其不能省）。P3 保留（改脚本走 TDD 是 AGENTS.md 强制约定，防复发 CHECK 与 provenance 审计扩展都是可测试的脚本逻辑）。P7 保留（多文件协议改动，需要一致性交叉检查覆盖去重后的锚点完整性）。

---

## 7. 能力需求声明

已在上方 frontmatter 声明（python3-runtime / grep-rg / git-log-diff / ruff，均 available，无 GAP，无 supplementable）。本任务不涉及 UI/浏览器/外部系统，无需 vision 相关能力声明。

---

## 8. SCOPE+ 预留

无。若后续阶段（如 P2 设计时）发现职责声明表覆盖的文档范围需要扩大（如波及 role-system.md / git-integration.md / loop-orchestration.md 等本次未纳入去重对象的协议文件），按 `[SCOPE+]` 流程增补，不在本文件预先声明。
