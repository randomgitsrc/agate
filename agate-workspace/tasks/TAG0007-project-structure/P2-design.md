---
phase: P2
task_id: TAG0007
type: design
parent: P1-requirements.md
trace_id: TAG0007-P2-20260820
status: draft
created: 2026-08-20
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 8
packages: [phase-cards, execution-roles, templates, scripts]
domains: [backend]
ui_affected: false
# ── v2.0 派发编排字段 ──
dispatch_plan: {mode: static-batch, parallel_limit: 4, batches: [{id: skeleton-docs, complexity: medium}, {id: code-map-docs, complexity: medium}, {id: gate-script-both, complexity: medium}, {id: dogfood-bootstrap, complexity: low}]}
---

## 0. 总览

本方案覆盖 P1-requirements.md 的 11 条 BDD（RM-AG0008 骨架 BDD-1~5 + RM-AG0009 CODE-MAP BDD-6~11）。
两个机制生命周期不同（骨架一次性 / CODE-MAP 持续演进），按 dispatch-context 约束 1 分开探索候选
方案（§2.2 骨架、§2.3 CODE-MAP），但共享一次影响面梳理（§1）与两个跨机制联合决策（§2.1 落盘
位置、§2.4 角色复用）。核心设计决策：

- 骨架产出物 = P2 architect 为「0→1 任务」产出的**任务目录内 companion 文件**（`P2-skeleton.md`），
  由新增 P1 可选字段 `project_phase: bootstrap` 驱动触发，向后兼容（字段缺省 = 不触发，1011 条
  既有回归测试行为不变）。
- CODE-MAP.md = **复用既有工作区 `agents/` 子目录**（`{AGATE_WORKSPACE}/agents/CODE-MAP.md`），
  不新增 WORKFLOW.md 第 10 个固定子目录；文件是否存在即"该项目是否已采用 CODE-MAP 机制"的判据。
- BDD-4（骨架归属）与 BDD-7（CODE-MAP 更新义务）合并进 P4-implementation.md 同一张"新增文件核对
  表"，implementer 一次动作满足两条累加验收标准（dispatch-context 约束 4）。
- CODE-MAP 一致性核对复用 P7 现有 `DESIGN_GAP`/`DESIGN_GAP_REVIEWED` 的 frontmatter 计数 + 正文
  regex 双轨判定模式（`check-gate.py gate_p7`，L807-903 已读源码确认），新增
  `code_map_new_files_count`/`code_map_reviewed_count` 字段与 `[CODE_MAP_SYNC:]`/
  `[CODE_MAP_DRIFT:]` 标记，与 DESIGN_GAP 平行运作，不新造一套判定机制。
- 依赖方向偏离检测（BDD-9）不做跨语言静态分析（违反 ADR-003），改为 consistency-reviewer 人工
  判断 + gate 强制"必须留痕"（pairing 硬校验，缺失 → exit 1），发现的偏离本身标 WARNING 级
  `[CODE_MAP_DRIFT:]`（不阻断，满足 BDD-9"至少一个可见信号"的字面要求，同时不因新机制误伤
  commit 通过率）。
- 并发更新边界（dispatch-context 约束 5）：声明为已知限制，比照仓库已有的 `CHANGELOG.md
  [Unreleased]` 同类"多任务共享持续追加文件"的既有 git merge 冲突解决路径，不新增锁机制（见
  §1.3 风险 R5）。

## 1. 影响面梳理（强制节，写在候选方案之前）

### 1.1 改什么（Modify）

| 文件 | 改动点 | 关联 BDD |
|------|--------|----------|
| `agate/phase-cards/P1-requirements.md`（L77-80 附近，`change_type: refactor` 注释样例后） | 新增可选字段注释样例：`project_phase: bootstrap`（bootstrap / established，缺省=established，向后兼容） | BDD-1/3 |
| `agate/phase-cards/P2-design.md`「产出规格」节（L136-166 附近） | 新增条件产出规格：`project_phase: bootstrap` 时，P2 除 P2-design.md 外还需产出 task 目录下 `P2-skeleton.md`（含 `## 骨架声明` 标题） | BDD-1/2 |
| `agate/assets/execution-roles/architect.md`「输出」节（P2 部分，L34-63 附近） | 新增骨架设计职责段落：0→1 任务时产出 `P2-skeleton.md`，须用「候选目录集合 + 项目侧声明」参数化形式，不写死语言/框架目录名 | BDD-1/2 |
| `agate/assets/templates/skeleton-template.md`（新增） | 骨架模板：五类候选目录（源码/测试/文档/构建/部署）以**抽象类别标签**表达 + 项目侧技术栈声明填空区，不出现 `src/components`/`src/include` 等具体技术栈目录名 | BDD-2 |
| `agate/tests/unit/test_skeleton_template_stack_neutral.py`（新增） | 回归测试：读 `skeleton-template.md`，断言不含硬编码技术栈目录名黑名单 + 含参数化标记关键词 | BDD-2 |
| `agate/scripts/check-gate.py`（`gate_p2` 函数，L552-641） | 新增判定：读 `P1-requirements.md` 的 `project_phase` frontmatter 字段（复用既有 `_frontmatter_field`），值为 `bootstrap` 时要求 `P2-skeleton.md` 存在且含 `## 骨架声明` 标题，否则 exit 1；字段缺失/非 bootstrap → 不检查（向后兼容） | BDD-1/3/5 |
| `agate/tests/unit/test_check_gate.py`（grep `def test_gate_p2` 定位既有用例风格） | 新增用例：`project_phase: bootstrap` + 缺 P2-skeleton.md → gate 失败；含正确标题 → 通过；字段缺失 → 行为与改动前逐字节一致（回归） | BDD-1/3/5 |
| `agate/phase-cards/P4-implementation.md`「产出规格」节后（L60-65 附近） | 新增「新增文件核对表」小节：implementer 为每个新增文件填一行——骨架归属列（`within <dir>` / `[SKELETON_DEVIATION: 理由]`）+ CODE-MAP 处理列（`[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT: 理由]`）；末尾追加一句 `change_type: refactor` 同样适用本表（不因换用回归口径而豁免） | BDD-4/7/10 |
| `agate/phase-cards/P7-consistency.md`「产出规格」节 frontmatter 样例（L48-73 附近） | 新增两个可选 frontmatter 字段：`code_map_new_files_count`（P4 核对表中 CODE-MAP 处理列标记的转抄计数，语义对应 `design_gap_count`）/`code_map_reviewed_count`（consistency-reviewer 实际核对完成数，语义对应 `design_gap_reviewed_count`）；「检查清单」新增第 5 条：CODE-MAP 核对（对照 `agents/CODE-MAP.md` 与 P4 新增文件核对表，发现依赖方向偏离标 `[CODE_MAP_DRIFT:]`，核对通过标 `[CODE_MAP_SYNC:]`） | BDD-6/8/9 |
| `agate/assets/execution-roles/consistency-reviewer.md`「检查清单」节（L42-56 附近） | 新增职责段落：CODE-MAP 核对（对照 `agents/CODE-MAP.md` 记录与实际新增文件，逐条判定同步/偏离） | BDD-8/9 |
| `agate/scripts/check-gate.py`（`gate_p4` 函数，L650-680） | 新增 WARNING 级检查（不阻断）：暂存区含代码文件 AND（task 目录存在 `P2-skeleton.md` OR `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在）AND `P4-implementation.md` 缺 `## 新增文件核对表` 标题 → stderr WARNING | BDD-4/7 |
| `agate/scripts/check-gate.py`（`gate_p7` 函数，L807-903） | 新增**两层**硬校验（与 DESIGN_GAP pairing 逻辑结构对齐，非单层）：(a) 内部一致性——`code_map_reviewed_count < code_map_new_files_count` → exit 1（对应现有 `dg_reviewed < dg_count` 分支，L840-848）；(b) 转抄核对——`P4-implementation.md` 核对表中 `[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT` 标记的实际计数 > P7 的 `code_map_new_files_count`（**不是** `code_map_reviewed_count`）→ exit 1（对应现有 `p4_design_gap_count > dg_count` 分支，L873-893，专门捕获 consistency-reviewer 忘记转抄场景）；机制未采用（P4 无该表）→ 两层均不检查 | BDD-8/9 |
| `agate/tests/unit/test_check_gate.py`（同上定位） | 新增用例覆盖 gate_p4 WARNING 分支 + gate_p7 pairing 硬校验分支（未配对/已配对/机制未采用三态） | BDD-4/7/8/9 |
| `agate/assets/templates/code-map-template.md`（新增） | CODE-MAP 模板：五类必填字段占位（模块/层/依赖方向/关键文件/约定），初始内容可为占位声明 | BDD-6 |
| `agate/tests/unit/test_code_map_template.py`（新增） | 回归测试：模板含五个必填标题 | BDD-6 |
| `agate/WORKFLOW.md`「目录结构」`agents/` 行（L62-63 附近，assets 树状图之外的目录规范节 L88 `agents/` 行） | 追加一句：`agents/` 也承载 `CODE-MAP.md`（项目架构全貌维护物，非任务产出） | BDD-6 |
| `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（本任务自身，agate 仓库 dogfooding 实例） | 为 agate 自身初始化 CODE-MAP.md（BDD-6 存在性验收对象，五字段填 agate 实际架构：phase-cards/execution-roles/review-roles/scripts/templates 五层 + 依赖方向声明） | BDD-6 |

### 1.2 不改什么（Not Modify）

| 范围 | 理由 |
|------|------|
| `agate/scripts/check-protocol-consistency.py`（CHECK 1-12 框架本体） | 该脚本检查**协议文档间的静态一致性**（gate_commands 键集合、脚本名引用漂移等），骨架/CODE-MAP 校验的对象是"任务实例产出物 vs 任务实例设计"，性质对应 `check-gate.py`（任务级 gate）既有分工，不属于协议自身一致性问题，不新增 CHECK 编号 |
| `agate/WORKFLOW.md`「工作区目录规范」9 固定子目录列表结构本身 | 复用既有 `agents/` 子目录承载 CODE-MAP.md（见 §2.1 候选 A），不新增第 10 个目录，避免打开 WORKFLOW.md 目录规范这一高频引用协议表面 |
| `agate/assets/review-roles/*`（含 `plan-eng-review.md`） | C8 机械映射（backend + high）已自动触发 plan-eng-review，无需新增评审维度声明；本任务不新增评审角色 |
| `agate/assets/execution-roles/`（新增角色文件，如 `skeleton-designer.md`） | 见 §2.4 候选 B 排除理由：违反 role-system.md「角色清单最小化」既定原则，复用 architect + consistency-reviewer 即可覆盖两机制职责 |
| `agate/phase-cards/P3-tdd.md`、`P5-verification.md`、`P6-acceptance.md`、`P8-release.md` | 骨架/CODE-MAP 机制不改变这四阶段的产出规格或 gate 逻辑；BDD 覆盖范围止于 P1/P2/P4/P7，P6 acceptance 只需照常按 BDD 逐条验收（无需新增验收口径） |
| `agate/scripts/agate_common.py` | `_frontmatter_field`/`_md_field_get` 等既有公共函数签名已足够复用（读代码确认见 §5 minimal_validation），无需新增共享函数 |
| 任何跨语言静态依赖分析实现（import/require 语法解析器） | 见 §2.3 候选 B 排除理由，违反 ADR-003 不绑定技术栈 |
| CODE-MAP.md 多 worktree 自动合并/锁机制 | dispatch-context 约束 5 允许"声明已知限制"；本轮不解决，比照 `CHANGELOG.md [Unreleased]` 处理方式但需承认其结构化字段更新比纯追加冲突更难自动合并（见 §1.3 R5） |
| 本任务自身已 approved 的 `P1-requirements.md` 正文（BDD-1~11、frontmatter） | 只在 P1 卡片新增**未来任务可选**字段 `project_phase` 的文档说明，不回改本任务自己已批准的 P1 产出 |

### 1.3 风险在哪（Risk）

| 风险 | 缓解措施 |
|------|----------|
| **R1（check-gate.py 单文件多函数跨批冲突）**：`gate_p2`/`gate_p4`/`gate_p7` 三处改动若分属不同并行批次，存在同文件不同行区间被两个 subagent 各自 Write 互相覆盖的风险（TAG0017 §1.3 R1 同类教训） | 三处改动合并进单一批次 `gate-script-both`（见 §6），不与文档类批次并行触碰同一文件 |
| **R2（project_phase 字段向后兼容性）**：新分支若判定逻辑写错，可能误将现有 1011 个无 `project_phase` 声明的任务判为需要骨架，破坏回归基线（BDD-5） | 判定逻辑显式仿照既有 `design_trivial`/`follows_existing_pattern` 可选字段读取模式（`_frontmatter_field` 返回空串时天然走"不检查"分支，见 §5 minimal_validation 已读源码确认）；新增专项回归测试验证"字段缺失时 gate_p2 行为与改动前逐字节一致" |
| **R3（CODE-MAP pairing 判据与 DESIGN_GAP 计数字段混淆）**：P7-consistency.md 未来需同时维护 `design_gap_count`/`design_gap_reviewed_count` 与 `code_map_new_files_count`/`code_map_reviewed_count` 两组平行计数，consistency-reviewer 容易漏填其一 | P7-consistency.md frontmatter 样例（本任务新增）在同一代码块内并列展示两组字段，`consistency-reviewer.md` 角色文件「实质锚点要求」表格新增一行 CODE-MAP 对应项，与 DESIGN_GAP 行并列呈现 |
| **R4（gate_p4 WARNING 误伤存量任务）**：新检查若触发条件过宽，会对未采用骨架/CODE-MAP 机制的老项目产生噪音 | 触发条件严格限定为"task 目录存在 `P2-skeleton.md` **或** 项目 `agents/CODE-MAP.md` 存在"——两者均由项目/任务主动产出，未采用机制的项目/任务两个条件皆不成立，不受影响；且为 WARNING 非阻断，即便误触发也不拦截 commit |
| **R5（CODE-MAP.md 并发更新/合并冲突）**：多 worktree 并行 P4 阶段可能各自更新同一份 `agents/CODE-MAP.md`（P1 隐含需求第 8 条已点名） | 本轮不解决自动合并，比照 `CHANGELOG.md [Unreleased]` 处理方式（多任务共享持续追加文件，冲突时人工在 PR merge 阶段解决），但需承认 CODE-MAP.md 按设计含模块/层/依赖方向等**结构化字段**，多方并发改写同一条目更接近"同一行被两方各自改写"而非纯追加，git 无法自动合并，实际解决成本高于 CHANGELOG 追加冲突；不新增锁机制，若未来暴露实质冲突频率问题，留待独立任务登记 debt 处理（不在本任务范围内新增机制） |
| **R6（依赖方向偏离判断主观性）**：consistency-reviewer 人工判断"是否偏离已声明依赖方向"缺少自动化交叉验证，可能漏判 | gate 层面只强制"必须留痕"（pairing 硬校验），不强制"判断必须正确"——与现有 DESIGN_GAP 审查模式一致（P7 卡片本就承认 self-authored 局限，见 WORKFLOW.md P7 行 `⚠️ self-authored`）；判断质量依赖 consistency-reviewer 角色定义的检查清单指引，非本任务能根治的结构性局限 |
| **R7（骨架模板参数化检查是启发式黑名单，非语义验证）**：`test_skeleton_template_stack_neutral.py` 用黑名单字符串匹配（如 `src/components`），无法覆盖所有可能的技术栈硬编码写法 | 黑名单覆盖 BDD-2 原文举例的两个具体反例（`src/components`、`src/include`）+ 常见框架目录名（`src/hooks`、`src/pages`），并要求正面存在"候选目录集合"类参数化关键词；该检查是**回归防线**（防止未来编辑把模板改回硬编码），不是穷尽式语义证明，job 记录在测试 docstring 里以免误解为完备性保证 |

## 2. 候选方案

> §1 影响面梳理已完成，以下候选方案的取舍均建立在该梳理之上。按 dispatch-context 约束 1，
> 骨架（§2.2）与 CODE-MAP（§2.3）机制分开探索；两处跨机制共享决策（落盘位置 §2.1、角色复用
> §2.4）各自独立探索，避免两组机制候选各自重复讨论同一批共享决策点。

### 2.1 决策组 1：骨架 + CODE-MAP 落盘位置（两机制共享，合并决策一次）

**候选 A（推荐）：骨架落 task 目录 companion 文件；CODE-MAP 复用现有 `agents/` 子目录**
- 骨架：`{AGATE_WORKSPACE}/tasks/{Txxx}/P2-skeleton.md`（与 P2-design.md 同目录），由 P2 architect
  在判定 0→1 任务时产出。
- CODE-MAP：`{AGATE_WORKSPACE}/agents/CODE-MAP.md`——`agents/` 现有定位是"agent 输入知识（project.md
  / memory）"（WORKFLOW.md L62），CODE-MAP.md（项目架构知识）语义上完全落在这条定位内，零新增目录。
- 优点：① 骨架产出是"这个 0→1 任务的一次性设计产物"，天然是任务编排流程生成/消费的东西，按
  WORKFLOW.md 既有「内容边界判据」（是否由 agate 编排流程生成/消费）应归工作区，落 task 目录不
  产生判据冲突；也字面满足 BDD-1"工作区中存在"的措辞。② CODE-MAP.md 是跨任务持久物，语义贴近
  `agents/` 现有"agent 输入知识"定位，未来所有任务的 P2/P4/P7 都会读取它，天然该在与任务无关、
  跨任务共享的位置；不需要改 WORKFLOW.md 目录列表本身（只加一句描述），改动面最小。
- 风险：`agents/` 目录当前只有 `project.md`/memory 两类既有内容，混入 CODE-MAP.md 后该目录职责
  略微泛化——已在 §1.3 未识别为独立风险项，因为"agent 输入知识"本就是宽泛类别，非狭义单一用途
  目录。
- 工作量：低（无需新增目录、无需改 WORKFLOW.md 目录列表结构）。

**候选 B（不采纳）：两者均落项目 `docs/` 新增子目录**
- 骨架 → `docs/PROJECT-STRUCTURE.md`；CODE-MAP → `docs/CODE-MAP.md`。理由：两者都"描述产品/项目
  本身"（WORKFLOW.md 判据第二问），按判据字面应归项目 docs/。
- 优点：与 README 类"项目自身文档"同侧存放，人类读者浏览项目文档时更容易发现。
- 缺点（判定不采纳的理由）：① 骨架产出物是 P2 architect 在**任务编排流程内**判定触发、产出、
  被 P4 消费的东西——按判据「对偶自洽性」提示"优先问这是谁生成、谁消费的"，骨架的生成者/消费者
  都是 agate 编排流程本身（P2 生成、P4 消费、P2 gate 校验存在性），只是内容恰好描述了项目结构，
  这与"任务验收记录"性质更接近而非"项目 README"；② 落 `docs/` 意味着 P2/P4/P7 三个阶段的 commit
  流程都要额外处理工作区之外的路径（`git add {AGATE_WORKSPACE}/tasks/{Txxx}/` 现有约定不覆盖
  `docs/`），需要修改多张阶段卡片的 commit 步骤描述，改动面明显大于候选 A；③ 新增 `docs/` 子
  目录不是既有约定，`agents/` 已有且语义贴合，候选 B 舍近求远。
- 工作量：中（需新增目录约定 + 改多张卡片的 git add 步骤说明）。

**选择理由**：候选 A。CODE-MAP 复用 `agents/` 是零协议表面变化的最小改动；骨架落 task 目录
companion 文件契合"谁生成谁消费"判据且字面满足 BDD-1，避免候选 B 引入的多卡片 commit 流程改动。

### 2.2 决策组 2：骨架机制设计（触发判据 + 产出阶段 + 参数化落地）

**候选 A（推荐）：P1 新增 `project_phase` 字段驱动 + P2 architect 产出 companion 文件**
- P1-requirements.md 新增可选 frontmatter 字段 `project_phase: bootstrap | established`（缺省
  established，向后兼容），仿照现有 `change_type: refactor` 可选字段模式（L79-80）。
- `project_phase: bootstrap` 时，P2 architect 除 P2-design.md 外，同批产出 `P2-skeleton.md`（含
  `## 骨架声明` 标题 + 参数化目录集合，模板见 `assets/templates/skeleton-template.md`）。
- `check-gate.py gate_p2` 读取该字段，`bootstrap` 时校验文件存在 + 标题存在，否则不检查（BDD-3
  的"不重复触发"通过"字段缺省/非 bootstrap 时不校验"自然满足，无需额外判据）。
- 优点：判据可机器判定（BDD-1 要求"触发判据存在且可判定"）；复用现有 P1 frontmatter 可选字段
  扩展的既定模式（风险最低，读代码已确认该模式的解析逻辑健壮，见 §5）；骨架设计天然是"这次
  任务的技术方案"，落在 architect P2 职责范围内，不需要新角色（呼应 §2.4）。
- 风险：`project_phase` 由谁判定（analyst P1 阶段判断项目是否 0→1）依赖人工/subagent 的经验
  判断，无自动化检测——与现有 `risk_level`/`domains` 等字段的判定方式一致（均是 P1 analyst 声明，
  非脚本推导），不是本机制独有的新风险类别。
- 工作量：低（1 个字段 + 1 个条件产出文件 + 1 处 gate 分支 + 若干测试）。

**候选 B（不采纳）：P0 阶段由主 Agent 亲自产出骨架**
- 在 P0-brief.md 阶段就要求主 Agent 声明骨架目录树，作为 P0 四字段之外的第五个必填字段。
- 优点：更早确定骨架，理论上能让 P1/P2 从一开始就"知道"项目结构。
- 缺点（判定不采纳的理由）：① P0-orchestrator.md 明确"P0 不派 subagent，主 Agent 亲自执行"，
  且 P0 四字段是"PM 视角的任务简报"（`task`/`known_risks`/`executor_env`/`env_constraints`），
  不含任何技术方案设计内容——骨架目录树属于技术方案（需要判断技术栈、目录组织范式），这类
  判断力不应该压给不具备 subagent 独立上下文优势的主 Agent；② P0 阶段项目还未经 P1 需求质疑，
  技术栈、模块划分等信息尚不完整，过早锁定目录结构违反"先质疑再设计"的 agate 核心原则；
  ③ architect 角色定义（role-system.md）本就是"P2 方案设计师"，骨架设计与既有 P2 职责高度
  重合，候选 B 制造了不必要的机制分裂。
- 工作量：中（需扩展 P0-brief.md 五字段模板 + P0 卡片流程改动，且与既有"P0 不产出技术方案"
  原则冲突，返工风险高）。

**选择理由**：候选 A。判据可机器判定、复用既有字段扩展模式、职责落在 P2 architect 天然合适，
候选 B 违反 P0 阶段职责边界的既定设计原则。

### 2.3 决策组 3：CODE-MAP 维护与一致性核对机制设计

**候选 A（推荐）：consistency-reviewer 在 P7 人工审计 + presence-based marker pairing gate（复用
DESIGN_GAP 模式）**
- P4 implementer 在「新增文件核对表」（§1.1 已列）为每个新文件填 CODE-MAP 处理列
  （`[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT: 理由]`）。
- P7 consistency-reviewer 对照 `agents/CODE-MAP.md` 实际内容与该表逐条核对，标 `[CODE_MAP_SYNC:]`
  （同步）或 `[CODE_MAP_DRIFT:]`（依赖方向偏离，WARNING 级，不阻断）。
- `check-gate.py gate_p7` 新增**两层** pairing 硬校验，与 `DESIGN_GAP`/`DESIGN_GAP_REVIEWED` 现有
  判定逻辑结构真正对齐（见 §1.1、已读源码 L807-903）：① 内部一致性——`code_map_reviewed_count <
  code_map_new_files_count` → exit 1；② 转抄核对——P4 核对表中标记的实际计数 > P7 的
  `code_map_new_files_count`（不是 `code_map_reviewed_count`）→ exit 1。
- 优点：不需要理解任何具体语言的模块系统语法（ADR-003 合规）；实现成本低（复用现成的双轨
  frontmatter 计数 + 正文 regex 回退模式，只需新增两个字段名和两个标记名，无需新写判定算法）；
  与现有 DESIGN_GAP 机制并行运作，consistency-reviewer 角色的认知模式（"逐条对照，不做看起来对
  的跳过"）天然适配。
- 风险：人工判断可能漏判真实的依赖方向偏离（已在 §1.3 R6 说明并接受——gate 只强制"留痕"不强制
  "判断正确"，与 DESIGN_GAP 现状一致，非本任务能根治的结构性局限）。
- 工作量：低（无新脚本、无新语言解析逻辑，只有字段/标记新增 + gate 函数内新增判定分支）。

**候选 B（不采纳）：新增自动化静态依赖分析脚本（解析 import/require 语句判断依赖方向）**
- 新增 `agate/scripts/check-code-map-drift.py`，对项目源码做静态解析，自动比对 import 语句的
  依赖方向与 `CODE-MAP.md` 声明的依赖方向是否一致。
- 优点：判断客观、不依赖人工经验，理论上能捕获人工漏判的偏离。
- 缺点（判定不采纳的理由）：① 直接违反 ADR-003"不绑定技术栈"——每种语言的模块系统语法不同
  （Python `import`/JS `require`/`import`/Go `import`/Rust `use`/C++ `#include`……），要做到
  "通用"必然要么内置多语言 AST 解析器（维护成本极高，agate 协议本体不应携带语言特定解析器
  依赖），要么做纯文本正则匹配（脆弱，误报/漏报率高，反而制造虚假的"客观"信号）；② AGENTS.md
  「改脚本的工作流」要求先写失败测试再改绿——一个跨语言依赖分析器的测试覆盖成本（需要为每种
  语言构造真实代码样本）远超本任务其余部分工作量总和，与 P1 已确认的任务粒度不成比例；③ ADR-003
  的"后果"节已明确"agate 不能自动发现项目的测试/构建命令，依赖人工声明"——依赖方向分析属于
  同一类"项目特定的语义信息"，理应遵循同样的"人工声明 + 协议提供检查框架"分工，而非协议自身
  实现语义分析。
- 工作量：高（多语言解析器 + 大量测试样本 + 长期维护成本）。

**选择理由**：候选 A。BDD-9 只要求"至少产生一个可见信号，不允许静默通过"，不要求判断必然
正确；候选 A 用 presence-based pairing 已能满足这条字面要求，候选 B 为了追求"客观正确性"付出
的成本与 ADR-003 硬约束冲突，且远超本任务合理工作量边界。

### 2.4 决策组 4：角色复用 vs 新增专属角色

**候选 A（推荐）：复用 architect（P2 骨架设计）+ consistency-reviewer（P7 CODE-MAP 核对）**
- 骨架设计职责并入 `architect.md`「输出」节 P2 部分；CODE-MAP 核对职责并入
  `consistency-reviewer.md`「检查清单」节，均不新增角色文件。
- 优点：role-system.md 明确既定原则"角色清单最小化"，且已有先例（UI 设计节由 architect 兼任，
  不新增 designer 角色）；两机制职责与 architect（"工程化+实现+回归策略"）、consistency-reviewer
  （"一致性交叉检查"）的既有认知模式高度重合，不存在职责错位；派发路径不变，主 Agent 不需要
  学习新角色的派发规则。
- 风险：architect.md 承担的职责逐渐变多（P2 设计 + UI 设计节 + 骨架设计），单个角色文件行数
  增长——已读 architect.md 全文（267 行），新增骨架设计段落预计增加 15-20 行，不会导致角色文件
  过度膨胀。
- 工作量：低（在现有角色文件内新增段落，无新文件、无新派发逻辑）。

**候选 B（不采纳）：新增 `skeleton-designer` + `architecture-reviewer` 专属角色**
- 为骨架设计新增独立执行角色，为 CODE-MAP 核对新增独立评审/执行角色。
- 优点：职责边界更"纯粹"，单一角色文件不因新机制持续膨胀。
- 缺点（判定不采纳的理由）：① 直接违反 P1 隐含需求第 4 条已点名的既定原则（role-system.md
  "角色清单最小化"），且 dispatch-context 约束 3 已明确"新增专属角色需要有明确理由才能选择（不
  是默认选项）"——本任务未发现这样的明确理由，两机制职责均能被现有角色的认知模式覆盖；② 新增
  角色意味着主 Agent 需要新增派发逻辑（新角色的 dispatch-context 模板、C8 映射表是否需要扩展等），
  改动面显著大于候选 A，且与"两个都是'建'（新增机制），不愿意一轮一轮来回改"的用户诉求（P0-brief
  known_risks）相悖——角色越多，未来维护/派发路径越复杂；③ 现有 7 个执行角色已覆盖 P1-P8 全部
  阶段，新增角色会打破"每阶段对应固定执行角色"的现有一一映射心智模型。
- 工作量：中（2 个新角色文件 + role-system.md 表格更新 + 派发路径文档更新）。

**选择理由**：候选 A。既定原则 + dispatch-context 约束 3 已明确要求"新增角色需要理由"，本任务
未找到这样的理由，两机制职责均落在 architect/consistency-reviewer 既有认知模式内。

## 3. 实现完成的标志

- `P1-requirements.md` 卡片含 `project_phase: bootstrap` 字段样例说明；未声明该字段的任务
  `gate_p2` 行为与改动前逐字节一致（新增回归测试验证）。
- `project_phase: bootstrap` 声明的任务：`P2-skeleton.md` 未产出或缺 `## 骨架声明` 标题时
  `check-gate.py P2` exit 1；产出且格式正确时通过。
- `assets/templates/skeleton-template.md` 存在，`test_skeleton_template_stack_neutral.py` 全绿
  （黑名单硬编码目录名缺席 + 参数化关键词存在）。
- `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在（agate 自身实例），含模块/层/依赖方向/关键文件/
  约定五类字段；`assets/templates/code-map-template.md` 含同五个占位标题。
- `P4-implementation.md` 卡片含「新增文件核对表」小节规格 + refactor 口径不豁免声明；
  `check-gate.py gate_p4` 在骨架/CODE-MAP 机制已采用且表缺失时输出 WARNING（不阻断）。
- `check-gate.py gate_p7` 在 CODE-MAP 处理标记数 > P7 核对标记数时 exit 1（pairing 硬校验，
  与 DESIGN_GAP 现有判定平行运作）；`P7-consistency.md` 卡片 frontmatter 样例含
  `code_map_new_files_count`/`code_map_reviewed_count` 字段。
- `consistency-reviewer.md`「检查清单」含 CODE-MAP 核对第 5 条职责说明。
- `python3 -m pytest agate/tests/` 全绿（含新增用例，1011 条既有用例 0 新增失败）；
  `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR（314 条存量 WARNING 非回归基线）；
  `bash agate/tests/scripts/count-tests.sh` 计数与实际用例数一致；`shellcheck -S warning
  agate/scripts/*.sh` 0 error（本任务不改 `.sh` 文件，此项预期无变化，仅确认不引入新问题）。

## 4. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本地 Linux（继承 P0-brief）：python3 -m pytest agate/tests/ + python3 agate/scripts/check-protocol-consistency.py（非 --strict，0 ERROR 即可，314 条 WARNING 为存量基线不回归）+ bash agate/tests/scripts/count-tests.sh + shellcheck -S warning agate/scripts/*.sh，均在 worktree 自己的脚本上跑（dogfooding 纪律，AGENTS.md 已声明：check-protocol-consistency.py 必须用 worktree 自己的，不能用 ~/.agate 稳定版）"
  isolation_check: "本任务改动对象是 agate 协议脚本/文档本体，不涉及生产环境/生产数据库/生产 API；[PROD_NOT_TOUCHED]（预期声明，P6 acceptance 复核实际执行情况后二值判定）"
  code_map_bootstrap_note: "P4 implementer 需在 {AGATE_WORKSPACE}/agents/ 目录下创建 CODE-MAP.md（本任务 dogfooding 示例，BDD-6 存在性验收对象）；implementer 需确认 {AGATE_WORKSPACE} 指向本 worktree 的 agate-workspace/ 而非 ~/.agate（worktree 双工作区约定，AGENTS.md 已声明）"
```

## 5. minimal_validation

```yaml
minimal_validation:
  - assumption: "P7 CODE-MAP pairing 判定可复用 check-gate.py 现有 DESIGN_GAP/DESIGN_GAP_REVIEWED 的两层判定结构（内部一致性 + 转抄交叉核对），套用同款字段/标记名不需要新写判定算法，只需按正确的对应关系补齐两层"
    method: "读 check-gate.py gate_p7 函数源码（L807-903）逐行核实：DESIGN_GAP 实际是**两层**校验，非单层——(a) 内部一致性（L840-848）：`dg_reviewed < dg_count` 判失败（frontmatter `design_gap_reviewed_count` < `design_gap_count`）；(b) 转抄交叉核对（L873-893）：P4 正文 regex 实际计数 `p4_design_gap_count` 与 P7 的 `design_gap_count`（不是 reviewed_count）比较，`p4_design_gap_count > dg_count` 判失败。CODE-MAP 提案按此结构对齐：`code_map_new_files_count` 对应 `design_gap_count`（P4 实际标记数的转抄计数），`code_map_reviewed_count` 对应 `design_gap_reviewed_count`（consistency-reviewer 实际核对数）；两层判定逻辑均可直接复制 gate_p7 现有分支模板改字段名/标记名，不需要新写判定算法"
    result: confirmed
    note: "初版方案曾将两层结构误简化为单层描述（P4 实际计数直接比 reviewed_count，且新增的 code_map_new_files_count 字段未被任何判定分支引用），已在本轮修复轮核实源码并修正为完整两层结构、字段对应关系归位。_md_field_get/_frontmatter_field 函数签名通用（非 DESIGN_GAP 专用），复用两层判定分支模板改字段名的实现成本评估结论不变（仍是低成本，只是多一层判定分支，非新算法）"
  - assumption: "project_phase 字段缺失时 gate_p2 不会误触发骨架校验，向后兼容 1011 条既有测试"
    method: "读 gate_p2 现有可选字段判定逻辑（L570-575，design_trivial/follows_existing_pattern 分支）：`if any(re.search(...) for line in p1_lines)` 对空/不匹配输入返回 False，天然走默认分支。project_phase 判定拟用同款写法：`_frontmatter_field(p1_file, \"project_phase\") == \"bootstrap\"`——_frontmatter_field 对不存在字段返回空字符串（已读该函数签名于既有调用处 `_frontmatter_field(p2_review, \"status\")` 确认返回类型为 str），空字符串 != \"bootstrap\" 为 False，天然不触发新校验"
    result: confirmed
    note: "新分支与现有代码同款写法，不存在“意外匹配空值”的边界条件；新增回归测试仍需覆盖此路径作为双重保险（TDD 红→绿标准流程），非因不信任本次验证结果，而是遵循 AGENTS.md 改脚本工作流强制要求"
  - assumption: "其余改动（模板文件新增、phase-cards 文字新增、architect.md/consistency-reviewer.md 文字新增）是纯文档新增，无外部系统依赖"
    method: "纯代码逻辑，无外部系统依赖。依赖的内部函数/数据转换：无（新增内容为 Markdown 文本段落 + YAML 注释样例，不涉及运行时代码路径），验证方式是 §3「实现完成的标志」列出的静态存在性/关键词断言（pytest 读文件 + 正则匹配），非行为验证"
    result: not_needed
    note: "声明性验证，非「待验证假设→实测确认」类型；P3 测试设计阶段用简单文件读取 + 字符串/正则断言即可覆盖，无需最小验证脚本"
```

## 6. gate_commands（P2 固化，P3/P5/P6 按此执行，不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
```

说明：
- `P3`/`P5` 固定为 `python3 -m pytest agate/tests/`（`P5` 加 `-q --tb=no` 走 architect.md 要求的
  紧凑输出模式，`P3` 保留详细输出供 `check-tdd-red.py` 自动读取）。
- `P5_consistency`/`P5_count_tests`/`P5_shellcheck` 均为**独立 key**，不与 `P5` 用 `&&` 拼接
  （dispatch-context 约束 7 要求；`--strict-errors-only`/`--strict` 均不使用——按 P0-brief
  时效性更新说明，日常默认模式即 `check-protocol-consistency.py`（非 `--strict`），0 ERROR 即
  通过，314 条存量 WARNING 不构成回归）。
- 不声明 `{key}_timeout_seconds`：本任务验证命令均为常规单元测试规模（现有 1011 条用例历史
  实测数分钟量级，新增用例增量很小），走既有 `AGATE_TDD_TIMEOUT` 默认机制即可。
- `project_module` 未声明：本任务改动对象是 agate 自身（dogfooding），参照 TAG0017 同类
  dogfooding 任务的 P2-design.md 先例，未声明该字段。

## 7. dispatch_plan 说明（批次设计，TAG0014 强制节）

**工作量五维评估**：
- 产出规模：跨 phase-cards（P1/P2/P4/P7，4 张）+ execution-roles（architect.md/
  consistency-reviewer.md，2 个）+ templates（2 新增）+ scripts（check-gate.py 单文件 3 处函数）+
  WORKFLOW.md（1 处）+ 至少 4 个新增测试文件 + 1 份 agate 自身 CODE-MAP.md 实例，共 >6 个文件 →
  **high**。
- 输入规模：files_to_read（见 §8）跨批统计后单批 ≤5 个，但整体输入文件（本 P2-design.md 已读
  的 11 个协议文件）远超单发上限 → 需拆批。
- 改动性质：跨模块协议改动（phase-cards/execution-roles/scripts 三层联动）→ **high**。
- 耦合度：check-gate.py 的 gate_p2/gate_p4/gate_p7 三处改动与文档层新增字段/标记名强耦合（字段
  名/标记名必须与文档描述逐字一致）→ 中高。
- 认知负荷：需理解现有 DESIGN_GAP pairing 机制才能正确复用 → 中。

任一维度 high → 综合定级 **high**，按硬规则必须拆批（不允许单发）。

**批次边界设计**（对齐 §1 影响面梳理的文件分组，4 批，静态拆批，全部并行，无跨批文件重叠）：

| 批次 id | 覆盖范围 | 涉及文件 | complexity |
|---------|---------|---------|------------|
| `skeleton-docs` | 骨架机制文档层：P1/P2 卡片字段与产出规格 + architect.md 职责 + 骨架模板 + 模板回归测试 | `phase-cards/P1-requirements.md`、`phase-cards/P2-design.md`、`assets/execution-roles/architect.md`、`assets/templates/skeleton-template.md`、`tests/unit/test_skeleton_template_stack_neutral.py` | medium |
| `code-map-docs` | CODE-MAP 机制文档层：P4/P7 卡片新增小节 + consistency-reviewer.md 职责 + CODE-MAP 模板 + 模板回归测试 + WORKFLOW.md agents/ 行说明 | `phase-cards/P4-implementation.md`、`phase-cards/P7-consistency.md`、`assets/execution-roles/consistency-reviewer.md`、`assets/templates/code-map-template.md`、`tests/unit/test_code_map_template.py`、`WORKFLOW.md` | medium |
| `gate-script-both` | 两机制共享的唯一脚本文件：check-gate.py 的 gate_p2/gate_p4/gate_p7 三处判定改动一次性完成，避免跨批同文件冲突（见 §1.3 R1） | `agate/scripts/check-gate.py`、`agate/tests/unit/test_check_gate.py` | medium |
| `dogfood-bootstrap` | agate 自身 CODE-MAP.md 初始化（BDD-6 存在性验收实例） | `{AGATE_WORKSPACE}/agents/CODE-MAP.md` | low |

- `mode: static-batch`，`parallel_limit: 4`（4 批文件集合两两不相交，可一轮全部并行；无资源
  密集型全量测试/E2E/构建类批次，全量 `python3 -m pytest agate/tests/` 作为 P5 gate 在所有批次
  合并后统一跑一次，不在单批内跑全量）。
- 跨批共享文件核查：4 批覆盖的文件集合两两不相交（check-gate.py 的三处改动已合并进单一批次
  `gate-script-both`，不与 `skeleton-docs`/`code-map-docs` 重叠），满足"同一文件不跨批次被改
  两轮"。
- `dogfood-bootstrap` 批次内容（agate 自身 CODE-MAP.md 五字段：模块/层/依赖方向/关键文件/约定）
  依赖 `code-map-docs` 批次确定的模板结构（`assets/templates/code-map-template.md` 的字段标题），
  但本 P2-design.md 已声明五字段**名称**（见 §1.1、§3），具体标题的 markdown markup 形式
  （`##` 二级标题 / `###` 三级标题 / 加粗文本等）由各批次自行决定，不强制两批次产出的 markup
  完全一致；`dogfood-bootstrap` 批次可直接依据本设计文档已声明的字段名称独立产出，不需要等待
  `code-map-docs` 批次的实际产出物返回，因此仍可与其余三批同轮并行派发（两批次标题 markup 是否
  一致目前无回归测试覆盖，属已知测试缺口）。
- 批次间无顺序依赖（各批改动的文档/代码/测试文件相互独立），可全部并行派发；仅需在所有批次
  返回后，主 Agent 统一跑一次全量 `python3 -m pytest agate/tests/` + `check-protocol-consistency.py`
  确认无跨批次意外交互。

## 8. files_to_read（P4 implementer 上下文导航）

按批次归类，P4 implementer 按所属批次读取对应子集，不必全读：

**skeleton-docs**：
- `agate/phase-cards/P1-requirements.md:60-89`（frontmatter 字段样例节，`change_type: refactor`
  注释样例是 `project_phase` 新字段的插入模板参照点）
- `agate/phase-cards/P2-design.md:136-166`（产出规格节，P2-skeleton.md 条件产出规格插入点）
- `agate/assets/execution-roles/architect.md:34-63`（「输出」节 P2 部分，骨架设计职责段落插入点）
- 本 P2-design.md §1.1/§2.2/§3（骨架机制的字段名、文件名、标题名、判定逻辑已完整声明，无需另
  查其他文件）

**code-map-docs**：
- `agate/phase-cards/P4-implementation.md:60-65`（产出规格节，「新增文件核对表」小节插入点）
- `agate/phase-cards/P7-consistency.md:48-73`（产出规格节 frontmatter 样例，新增字段插入点）
- `agate/assets/execution-roles/consistency-reviewer.md:42-56`（「检查清单」节，CODE-MAP 核对
  职责插入点）
- `agate/WORKFLOW.md:79-95`（工作区目录规范节，`agents/` 行补充说明插入点）
- 本 P2-design.md §1.1/§2.3/§3（CODE-MAP 机制的字段名、标记名、五字段模板结构已完整声明）

**gate-script-both**：
- `agate/scripts/check-gate.py:552-641`（`gate_p2` 全函数，`project_phase` 判定插入点）
- `agate/scripts/check-gate.py:650-680`（`gate_p4` 全函数，CODE-MAP WARNING 判定插入点）
- `agate/scripts/check-gate.py:807-903`（`gate_p7` 全函数，CODE-MAP pairing 硬校验插入点，
  DESIGN_GAP 判定逻辑是直接参照模板）
- `agate/tests/unit/test_check_gate.py`（grep `def test_gate_p2\|def test_gate_p4\|def test_gate_p7`
  定位既有用例风格，比照编写新用例；文件较大 2395 行，不通读，按 grep 结果定位相关测试类/函数
  附近读取）

**dogfood-bootstrap**：
- 本 P2-design.md §1.1/§3（CODE-MAP 五字段结构与内容要求已完整声明）
- `agate/WORKFLOW.md:35-75`（目录结构树状图，用于填写 agate 自身 CODE-MAP.md 的"模块/层"字段
  内容参照）
