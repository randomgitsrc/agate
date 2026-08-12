---
phase: P2
task_id: TAG0003-workspace-architecture
type: design
parent: P1-requirements.md
trace_id: TAG0003-P2-20260812
status: draft
created: 2026-08-12
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3
packages: [agate]
domains: [backend, cli]
ui_affected: false
---

# TAG0003 — agate 工作区架构：P2 方案设计

> 输入：P2-dispatch-context-architect.md（派发指引）+ P1-requirements.md（20 条 BDD 基线）+ P1-review.md（观察项 2 条）+ P0-brief.md（风险/约束）+ AGENTS.md（项目约定）+ review-design-20260812-1428.md（roadmap 思路来源）。
> 角色：architect（`~/.agate/assets/execution-roles/architect.md`）。
> 方法：先读现有代码再设计（已读 6 个引用脚本 + orchestrator-template + 模板 + fixtures + count-tests + 一致性检查器）；先最小验证再定方案（git mv 行为 / .agate.env 解析 / bats TAP，验证结果见 §8）。
> 范围：本方案设计的是 **worktree 的 `agate/`（协议本体）将改成的样子**，不是 `~/.agate`（稳定版 v0.40.2 开发工具，禁止改动）。

## 1. 影响域分析

### 1.1 改什么（6 脚本 + 16 文档 + 8 测试文件 + 新增 3 交付物）

**脚本（`agate/scripts/`，6 个既有 + 2 个新增 + 1 个改函数库）**

| 文件 | 改动 | 依据 |
|------|------|------|
| `pre-commit-gate.sh` | `AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"`（L27）改为调工作区解析器获取 tasks_base；根级 .state.yaml 的 `TASK_DIR=$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID`（L83）跟随解析结果 | BDD-2/3/4/13 |
| `ci-gate-backstop.py` | `tasks_base = os.environ.get("AGATE_TASKS_DIR", "docs/tasks")`（L86）改为调解析器（subprocess 调 bash 解析脚本）或复用同一解析逻辑，保证本地 hook 与 CI 同路径 | BDD-13（隐含需求 #4） |
| `check-state-transition.sh` | L28 `grep -qE 'docs/tasks/[^/]+/'` 是**任务级 .state.yaml 检测的唯一入口**，硬编码路径必须移除。改为与 pre-commit-gate.sh L82 一致的语义：`dirname($STATE_FILE) != REPO_ROOT` 即任务级（见 §3.6 与 §8 minimal_validation#4） | BDD-6/13；[SCOPE+]（见 §10） |
| `check-pruning.sh` | L66 `grep -cvE '^docs/tasks/|\.state\.yaml$|...'` 的排除模式改为工作区 tasks 相对路径（P7 裁剪的源码文件数过滤），否则裁剪 P7 时任务文件被误计入源码文件数 | BDD-6/13；[SCOPE+] |
| `check-protocol-consistency.py` | `PATH_IGNORE_SUBSTRINGS` 中 `"docs/tasks/"`（L72）替换/补充为工作区运行时目录（如 `"agate-workspace/"`），`"docs/agents/"`（L69）按 project.md 新位置重校准 | BDD-20（隐含需求 #9） |
| `install-hook.sh` | L87 提示文字 `git add docs/tasks/` 改为工作区 tasks 路径 | BDD-6 |
| `gate-result.sh`（函数库） | 新增 `resolve_workspace` 解析函数（.agate.env > AGATE_TASKS_DIR > 默认 agate-workspace/），供各 .sh source 使用；或由新增解析脚本承载（见 §3.1 候选 A 细化的实现选择） | BDD-2/3/4/5/13 |
| **`agate-workspace-resolve.sh`（新增）** | 工作区路径单点解析器：读 `.agate.env`（`AGATE_WORKSPACE=`）→ 环境变量 `AGATE_TASKS_DIR` → 默认 `agate-workspace/`（相对项目根，tasks_base = 工作区根/tasks）；输出 `AGATE_WORKSPACE` 与 `AGATE_TASKS_DIR` 供脚本消费；bash 与 python（ci-gate-backstop）共用 | BDD-2/3/4/5/13 |
| **`agate-migrate-workspace.sh`（新增）** | 强制迁移工具：`docs/tasks/` → 工作区 `tasks/`、`docs/archived/` → 工作区 `archived/`；git mv 目录级语义 + 空源守卫 + 仓库外 fallback mv + 幂等 + 旧布局检测 | BDD-6/7/8/9/18/19/10 |

**文档（`agate/*.md` + `agate/assets/` + `agate/phase-cards/`，16 个）**

| 文件 | 改动 | 依据 |
|------|------|------|
| `orchestrator-template.md` | project.md 路径 `{project_root}/docs/agents/project.md`（L21/25/113）→ 工作区内 `{AGATE_WORKSPACE}/agents/project.md`；active-tasks 路径（L69/94/115）→ `{AGATE_WORKSPACE}/tasks/active-tasks.md`；接入 `mkdir -p`（L93）建 8 子目录；启动时旧布局检测 + 迁移指引（BDD-10） | BDD-1/2/10/11/12 |
| `state-machine.md` | 首接入节（L33-44）`mkdir docs/tasks/` → 建工作区 8 子目录；产出路径 `docs/tasks/Txxx/Pn-*.md`（L48）→ 工作区内路径 | BDD-1/2/6 |
| `dispatch-protocol.md` | 全部 `docs/tasks/{Txxx}/` 引用（28 处，L28-1181）→ 工作区路径占位 | BDD-6 |
| `git-integration.md` | commit 规范里的 `docs/tasks/{task_id}/`（L89/115）→ 工作区路径 | BDD-6 |
| `role-system.md` | 评审对象/产出路径（L93-94）→ 工作区路径 | BDD-6 |
| `WORKFLOW.md` | 目录结构图（L66-82）、多任务适配（L258）、状态落盘（L297）→ 工作区路径；**内容边界判据正式规则（BDD-17 文档锚点，写入本节）**；roadmap 循环规范 | BDD-6/17/14/15/16 |
| `SETUP.md` | 新项目接入步骤：project.md 位置 → 工作区 agents/；初始化建工作区目录；.agate.env 配置说明 | BDD-1/2/3 |
| `UPGRADING.md` | 存量项目迁移指引（迁移工具使用步骤 + 旧布局说明） | BDD-6/8/10/18 |
| `phase-cards/P{1,2,3,4,5,6,7}*.md` | `git add docs/tasks/{Txxx}/`（各卡片）→ 工作区路径 | BDD-6 |
| `assets/templates/active-tasks-template.md` | 复制目标路径 + 目录结构图（L61-72）→ 工作区 | BDD-1/6 |
| `assets/templates/project.md` | 复制目标 `{project_root}/docs/agents/project.md`（L3）→ 工作区 agents/ | BDD-11 |
| `assets/templates/dispatch-context.md` | `docs/tasks/{Txxx}/`（L25-26）→ 工作区路径 | BDD-6 |
| `assets/templates/task-files.md` | 目录说明（L3）→ 工作区路径 | BDD-6 |
| `assets/templates/dispatch-prompt.md` | `docs/tasks/{Txxx}/`（L20）→ 工作区路径 | BDD-6 |
| `assets/execution-roles/*.md`（7 个） | 输入/产出路径中的 `docs/tasks/{Txxx}/` → 工作区路径 | BDD-6 |
| `loop-orchestration.md` / `rules/state-transitions.md` | active-tasks/任务目录引用 → 工作区路径 | BDD-6 |
| **`assets/templates/roadmap-template.md`（新增）** | roadmap 条目模板：条目 id、标题、状态标识（backlog/scheduled/in-progress/done/cancelled）、来源（新需求/讨论）、关联 task_id | BDD-14/15/16 |

**测试（`agate/tests/`，8 个 .bats 文件 / 377 处 `docs/tasks` 引用，fixture 内路径）**

- `integration/pre-commit-hook.bats`、`integration/dispatch-context-card.bats`、`unit/check-state-transition.bats`、`unit/ci-gate-backstop.bats`、`unit/check-pruning.bats`、`unit/agate-capture-env-baseline.bats`、`unit/dispatch-context-warning.bats`、`regression/v040-dotarchived-exclusion.bats`：fixture 里 `mkdir -p $repo/docs/tasks/...`、`git add docs/tasks/...`、`run bash ... docs/tasks/T001` 等硬编码路径换血为工作区路径（或引入 helpers 变量）。
- `tests/helpers/fixtures.bash`：`create_task_dir` 用 `mktemp`（不依赖 docs/tasks，**不改**）；可新增一个 `AGATE_TASKS_DIR` 测试变量辅助路径构造。
- 新增测试文件（P3 定）：`unit/agate-workspace-resolve.bats`（解析优先级/空格路径/外部路径）、`unit/agate-migrate-workspace.bats`（迁移/幂等/空源/归档）。
- 用例数：**既有 603 条换血不改数**，新增迁移工具/解析器用例允许增长（P1-review 观察项 1 口径，BDD-20）。

### 1.2 不改什么（明确边界）

- `check-gate.sh`（461 行）：无 `docs/tasks` 硬编码，路径只来自 TASK_DIR 参数——**不改**。
- `check-p6-provenance.sh` / `check-p6-evidence.sh` / `check-scope-resolved.sh` / `check-retrospective.sh` / `check-changelog.sh` / `check-tdd-red.sh`：路径均为 TASK_DIR 相对——**不改**（已 grep 确认无 docs/tasks 硬编码）。
- `agate-*.py` 系列工具（agate-state-get / agate-md-field-get / agate-gate-p5-count 等）：无 docs/tasks 硬编码——**不改**。
- 协议编排模型：P0-P8 阶段、双层角色体系、gate 判定逻辑、状态机转移规则、裁剪规则——**语义不变**（BDD-13「行为不变」）。
- `AGATE_TASKS_DIR` 环境变量缝隙：**保留**（作为 .agate.env 之下的二级解析源，向后兼容既有 CI 设置）。
- 任务编号空间（`T[A-Z]{2}\d+`）、.state.yaml 格式校验（agate-state-yaml-check.py）——**不改**。
- worktree 自身 live `docs/tasks/TAG0003-.../`（当前任务正在运行的目录）：**此任务内不物理迁移**——迁移工具用 fixture 仓库验证，物理迁移属于 P8 发布后用户侧的升级动作（见 §1.3 风险 + §10 SCOPE+）。

### 1.3 风险在哪

| 风险 | 缓解 |
|------|------|
| 43 文件 / 516 处引用（含 377 测试）跨脚本/文档/测试换血，漏改 → 一致性检查红或运行错路径 | P7 双向一致性核对 + BDD-20 一致性检查白名单重校准为 gate；grep 定量核对（§4 BDD-20 验收路径） |
| **check-state-transition.sh 的 `docs/tasks/[^/]+/` grep 漏改** → 任务级 .state.yaml 被当根级处理（get_old_phase 用 basename），状态转移检查静默失效 | §3.6 显式改造 + §8 minimal_validation#4 已验证改法（改用 dirname!=REPO_ROOT 语义，与 pre-commit-gate.sh 统一，不绑死任何路径） |
| orchestrator 路径改动影响**所有接入项目**（符号链接接入） | P1 已确认 A 策略（破坏性变更）；UPGRADING.md + SETUP.md 双路径指引（新项目初始化 / 旧项目迁移） |
| 迁移工具在外部工作区（.agate.env 指向项目外）场景 git mv 失败（exit 128，已验证） | fallback 普通 `mv` + WARNING 标注「git 历史不可在新路径追溯」——外部工作区下 BDD-8 只能部分满足，方案诚实标注此限制 |
| 迁移工具在 fixture 外误跑，把 worktree 自身 live docs/tasks 迁走 → 当前任务中断 | 工具只在用户显式调用时运行；测试全部走 fixture（BATS_TEST_TMPDIR）；文档指引强调在项目根运行 |
| count-tests 用例数漂移（新增用例使总数 >603，与 BDD-20「不漂移」字面冲突） | 采用 P1-review 观察项 1 口径：既有 603 条换血不改数 = 不漂移；新增迁移工具用例允许增长，在 BDD-20 验收路径显式声明 |
| .gitignore 忽略 .state.yaml 导致迁移漏文件 | minimal_validation#1 已验证 git mv 目录级**物理移动**所有文件（含 gitignore 的 .state.yaml + 未追踪文件），与 git 跟踪状态解耦 |

## 2. 候选方案与权衡

### 候选方案 A（推荐）：单点解析器 + git mv 目录级迁移 + 全量文档/测试同步

**设计**：
- 新增 `agate-workspace-resolve.sh` 单点解析工作区路径：解析优先级 **`.agate.env` 显式配置（`AGATE_WORKSPACE=`）> 环境变量 `AGATE_TASKS_DIR` > 默认 `agate-workspace/`**（相对项目根），并派生出 tasks_base（= 工作区根/tasks）。bash 脚本 source 复用；python（ci-gate-backstop.py）subprocess 调同脚本，保证本地 hook 与 CI 解析到同一路径。
- 新增 `agate-migrate-workspace.sh`：`git mv` 目录级迁移 `docs/tasks/` → `{workspace}/tasks/`、`docs/archived/` → `{workspace}/archived/`；空源 no-op（BDD-19）、已迁移幂等（BDD-9）、仓库外 fallback `mv`、旧布局检测输出迁移指引。
- 6 脚本 + 16 文档 + 8 测试文件全量同步换血；roadmap 单文件（`roadmap/roadmap.md`）模板；内容边界判据文档化（WORKFLOW.md）；一致性白名单重校准。

**权衡**：
- 优点：单点解析从结构上保证本地/CI 一致（BDD-13）；git mv 目录级一次覆盖 .state.yaml/未追踪文件（BDD-7 天然满足，已验证）；语义最干净，一劳永逸。
- 代价：改动面最大（43 文件/516 引用）；新增 2 个脚本需维护；roadmap 是新增机制需定义状态机与回写规则。
- 风险：换血遗漏（靠 P7 + BDD-20 gate 兜底）。

### 候选方案 B（对照）：环境变量直连，不引入 .agate.env

**设计**：只把 `AGATE_TASKS_DIR` 默认从 `docs/tasks` 改为 `agate-workspace/tasks`，环境变量是唯一配置缝隙；无解析器、无 .agate.env、迁移工具最小化（纯 mv 脚本）。

**权衡**：
- 优点：改动面最小，脚本基本不动。
- 代价：**违背 P1 已确认决策 4（.agate.env 配置工作区位置）**——只能作为对照而非候选；无法满足 BDD-3（项目外路径无文件承载，CI/本地手工设 env 易漂移）、BDD-4（无文件时行为依赖环境，默认值不落盘）、BDD-5（空格路径靠 env 传递脆弱）；BDD-13 一致性靠人工保证，无结构性约束。**否决。**

### 候选方案 C（对照）：.agate.env + 文件级 git mv 迁移

**设计**：解析机制同 A，但迁移工具逐文件 `git mv`（显式指定每个被迁移文件，含 .state.yaml 用 `git add -f` 后迁移）。

**权衡**：
- 优点：对每个文件的迁移粒度可控，可选择性跳过/记录。
- 代价：逐文件循环慢、代码复杂、易漏（377 引用换血已是重活）；目录级 git mv 已验证物理移动 gitignore 文件 + 保留历史（minimal_validation#1），文件级没有额外收益；归档目录（docs/archived）需额外遍历。**否决，选 A 的目录级。**

### 选择理由

选 **方案 A**。决定性因素：(1) BDD-13 要求本地 hook 与 CI 解析同一工作区路径，单点解析器是结构性保证而非人工约定；(2) git mv 目录级迁移经验证物理覆盖 .state.yaml 等 gitignore 文件（BDD-7 隐含需求 #2），文件级方案无增益；(3) B 违背 P1 决策 4，C 复杂度高于收益。roadmap 采用**单文件**（对齐 active-tasks.md 既有模式，`follows_existing_pattern: [agate/assets/templates/active-tasks-template.md]`），内容边界判据采用**文档锚点**（写入 WORKFLOW.md，对齐 P1 SUGGEST #3）。

## 3. 选定方案详细设计

### 3.1 工作区路径解析（`agate-workspace-resolve.sh`）

**解析优先级**（P1 SUGGEST #2 落地）：
1. `.agate.env` 存在于项目根，且含 `AGATE_WORKSPACE=` → 工作区根 = 该值（相对路径 → 相对项目根解析；绝对路径原样；可含空格）。
2. 否则环境变量 `AGATE_TASKS_DIR`（既有缝隙）→ tasks_base = 该值（向后兼容：允许直接指定 tasks 目录）。
3. 否则默认 → 工作区根 = `{project_root}/agate-workspace`，tasks_base = `{project_root}/agate-workspace/tasks`。

**输出**：`AGATE_WORKSPACE`（工作区根绝对路径）+ `AGATE_TASKS_DIR`（tasks 基目录绝对路径），两值均打印。脚本内部统一处理：相对/绝对、含空格、指向项目外。

**消费方**：pre-commit-gate.sh（source 解析，替换 L27/L83）、ci-gate-backstop.py（subprocess 调解析脚本，替换 L86）、orchestrator-template.md（启动时解析工作区根用于读 project.md/active-tasks）、迁移工具（解析目标位置）。

**边界语义**（对应 BDD）：
- BDD-2：无 `.agate.env` → 默认 `agate-workspace/`（项目根下）。
- BDD-3：`.agate.env` 声明项目外绝对路径 → 工作区用外部路径；项目根下不新建默认目录（解析器不创建目录，目录创建只在初始化/迁移时显式进行）。
- BDD-4：无 `.agate.env` → 不报错、走默认。
- BDD-5：路径含空格 → 全程引号包裹 + `realpath -m`（已验证，见 §8）。

### 3.2 迁移工具（`agate-migrate-workspace.sh`）

**输入**：在项目根运行，可选 `--to <workspace>` 覆盖。

**流程**（顺序执行，任一步 git 失败 exit 1 并输出指引）：
1. 解析工作区目标（复用解析器）。
2. **源检测**：`docs/tasks/` 存在且非空？
   - 不存在 / 为空目录 → **no-op exit 0**（BDD-19：空源合法）。空目录直接用 `rmdir` 清理。
   - 存在且非空 → 继续。
3. **目标冲突检测**：工作区 `tasks/` 已存在且非空 → 输出冲突指引并 exit 1（不自动合并，防覆盖）。
4. **迁移**（目录级）：
   - `git mv docs/tasks {workspace}/tasks`——目标在仓库内时保留 git 历史（BDD-8）。已验证：目录级 git mv 物理移动含 gitignore 的 .state.yaml + 未追踪文件，`git log --follow` 历史可追溯。
   - git mv 失败（目标在仓库外，exit 128）→ fallback `mv` + WARNING「文件已移动，但 git 历史无法在新路径追溯（外部工作区固有限制）」。
5. **归档迁移**（BDD-18）：`docs/archived/` 存在且非空 → 同语义迁入 `{workspace}/archived/`（目录级 git mv，含相对结构保留）。
6. **幂等**（BDD-9）：迁移后 `docs/tasks/` 不再存在 → 重复运行在第 2 步即 no-op；不产生重复目录/重复动作。
7. **迁移后校验**：`docs/tasks/` 与工作区 `tasks/` 文件数/清单对照，输出迁移摘要。
8. 可选写 `.agate.env`（`AGATE_WORKSPACE=...`）用于外部工作区场景持久化配置。

### 3.3 orchestrator 路径切换（orchestrator-template.md）

- **project.md**：`{project_root}/docs/agents/project.md` → `{AGATE_WORKSPACE}/agents/project.md`（BDD-11）。
- **active-tasks**：`docs/tasks/active-tasks.md` → `{AGATE_WORKSPACE}/tasks/active-tasks.md`（BDD-12）。
- **初始化**：`mkdir -p {AGATE_WORKSPACE}/{roadmap,tasks,agents,archived,reviews,decisions,plans,logs}`；active-tasks 模板从 `{agate_root}/assets/templates/` 复制（BDD-1）。
- **旧布局检测**（BDD-10）：启动时若检测到 `{project_root}/docs/tasks/active-tasks.md` 存在而工作区 tasks 无 active-tasks → 输出迁移指引「运行 `bash {agate_root}/scripts/agate-migrate-workspace.sh`」并**不静默使用旧路径**、也不静默失败（输出指引后按指引路径继续，不假装已迁移）。

### 3.4 roadmap 循环（新增机制，BDD-14/15/16）

- **产物形态**：`{AGATE_WORKSPACE}/roadmap/roadmap.md` 单文件（模板 `assets/templates/roadmap-template.md`），与 active-tasks.md 同模式。
- **条目结构**：`| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |`；状态标识 = `backlog`（待规划）/ `scheduled`（已拆任务）/ `in_progress`（实施中）/ `done`（已完成）/ `cancelled`（取消）。
- **循环**（写入 WORKFLOW.md 正式规范）：
  - BDD-14：新需求/讨论 → roadmap 追加条目（状态 `backlog`，含来源与日期）。
  - BDD-15：拆任务 → 工作区 tasks/ 建任务目录 + active-tasks.md「待开始」区写入任务行，任务行记录 `roadmap: <id>` 关联；条目状态 → `scheduled`。
  - BDD-16：任务完成（P8 gate + READY）→ 回写条目状态 `done`（或 cancelled），闭环可追溯（任务→条目、条目→任务双向可见）。
- 状态机定义在 roadmap-template.md + WORKFLOW.md，无脚本 gate（新增机制的产物存在性/状态合法性检查是否纳入一致性检查器，见 §3.5）。

### 3.5 内容边界判据（BDD-17 文档锚点）

写入 `WORKFLOW.md`（正式规则节）：

> **判据**：某文件是否**由 agate 编排流程生成或消费**（任务产出、评审、决策、计划、日志、状态、看板、roadmap、agent 知识、归档）？→ 是：归入工作区。该文件是否**描述产品/项目本身而非任务编排**（README、产品文档）？→ 是：留在项目 docs/。
> 二值判定：一个文件必须且只能归入一侧；两侧同时不适用 = 属项目文档。

对偶自洽性（BDD-17 双场景）：任务验收记录（编排流程生成）→ 工作区；项目 README（描述产品本身）→ 项目 docs/。同一判据对两类文件结论相反。

### 3.6 任务级 .state.yaml 检测去硬编码（check-state-transition.sh，[SCOPE+]）

`get_old_phase()` 用 `grep -qE 'docs/tasks/[^/]+/'` 判断「任务级 .state.yaml 保留完整路径」。迁移后此 grep 若不同步，任务级文件被当根级（`git_path=$STATE_BASENAME`），`git show HEAD:basename` 取不到旧值 → 状态转移检查静默失效（T086 B1 教训同构）。改法：**检测语义从「路径含 docs/tasks」改为「STATE_FILE 的 dirname != REPO_ROOT」**——与 pre-commit-gate.sh L82 `[ "$STATE_DIR" = "$REPO_ROOT" ]` 完全同构，天然不依赖任何硬编码路径，覆盖 docs/tasks、agate-workspace/tasks、外部工作区三种布局。§8 minimal_validation#4 已做移动后兜底分支验证。

### 3.7 一致性白名单与用例数基线（BDD-20）

- `check-protocol-consistency.py` `PATH_IGNORE_SUBSTRINGS`：`"docs/tasks/"` → `"agate-workspace/"`（+ 保留 `"docs/agents/"` 作为项目侧示例/旧布局兼容，按实际引用调整）。一致性检查需 0 ERROR。
- `count-tests.sh` 基线：迁移后既有 603 条（换血路径）不漂移；新增迁移工具/解析器用例允许增长。BDD-20 验收路径显式采用此口径（P1-review 观察项 1）。
- P1-review 观察项 2（BDD-19 与 BDD-1 判定分离）：BDD-1 验收「新项目初始化」走初始化路径（空项目直接建 8 子目录）；BDD-19 验收「迁移工具空源」走迁移工具路径（无 docs/tasks 时 no-op + 不建错目录）。两路径在验收时分别执行，避免一条 PASS 误判另一条。

## 4. BDD 覆盖对照

| BDD | 验收路径（设计落点） |
|-----|---------------------|
| BDD-1 新项目初始化完整目录 | orchestrator 接入节 mkdir 8 子目录（§3.3）+ SETUP.md 步骤 |
| BDD-2 默认 agate-workspace/ | 解析器默认分支（§3.1） |
| BDD-3 项目外路径 | `.agate.env` 绝对路径分支 + 迁移工具 fallback（§3.1/3.2） |
| BDD-4 无 .agate.env 不报错 | 解析器默认分支 + 初始化不依赖 .agate.env |
| BDD-5 路径含空格 | 解析器/迁移工具全引号 + realpath（§8 已验证） |
| BDD-6 docs/tasks 迁入工作区 | 迁移工具核心（§3.2）+ 编排读取路径切换（§3.3/BDD-11/12/13 落点） |
| BDD-7 不丢失状态与阶段产出 | git mv 目录级物理移动（§8 已验证），fixture 迁移前后清单对比 |
| BDD-8 保留 git 历史 | git mv 目录级 + `git log --follow` 验证（§8）；外部工作区 fallback 标注限制 |
| BDD-9 迁移幂等 | 迁移工具第 2/6 步（源不存在→no-op，重复运行无新增动作） |
| BDD-10 旧布局获得迁移指引 | orchestrator 启动检测 + 指引（§3.3），不静默继续/不静默失败 |
| BDD-11 orchestrator 从工作区读 project.md | orchestrator-template 路径切换（§3.3） |
| BDD-12 从工作区读任务看板 | orchestrator-template active-tasks 路径（§3.3） |
| BDD-13 状态机与 gate 以工作区为任务根、行为不变 | 解析器统一消费（§3.1）+ pre-commit/ci 改造 + §3.6 去硬编码 + fixture 回归（行为不变断言） |
| BDD-14 需求/讨论进入 roadmap | roadmap.md 条目 + 状态标识（§3.4） |
| BDD-15 条目拆分进待开始看板 | roadmap→任务→active-tasks「待开始」+ 关联（§3.4） |
| BDD-16 任务完成回写 roadmap | P8/READY → 条目 done/cancelled 闭环（§3.4） |
| BDD-17 内容边界二值判据 | WORKFLOW.md 判据 + 双场景对偶（§3.5） |
| BDD-18 归档迁入工作区 archived/ 且幂等 | 迁移工具第 5/6 步（§3.2） |
| BDD-19 无 docs/tasks 时迁移工具正常 | 迁移工具第 2 步空源 no-op（§3.2），与 BDD-1 判定分离（§3.7） |
| BDD-20 一致性白名单与用例数基线全绿 | 白名单重校准 + count-tests 口径（§3.7） |

## 5. gate_commands

```yaml
gate_commands:
  P3: "bats --formatter tap agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/agate-migrate-workspace.bats agate/tests/unit/check-state-transition.bats"
  P3_formatter: "generic-tap.sh"
  P5: "bats --formatter tap agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -30"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
```

- P3 红灯由 check-tdd-red.sh 读本字段执行（bats TAP 输出，已验证兼容 generic-tap.sh，见 §8）。
- P5 为全量 bats 紧凑模式（`tail -30` 保汇总）；P5_consistency / P5_shellcheck / P5_count 为补充 gate 命令（check-gate.sh P5 会对多个 P5* 命令发 WARNING 提示全部执行，属预期行为）。
- ui_affected: false，无 P5_e2e。

## 6. files_to_read

```yaml
files_to_read:
  - path: agate/scripts/pre-commit-gate.sh
    why: AGATE_TASKS_DIR 默认值（L27）与根级 .state.yaml 的 TASK_DIR 推导（L82-86）；TASK_REL 相对路径用法（L91/123）——改解析点需保持任务级/根级分支语义
  - path: agate/scripts/ci-gate-backstop.py:86
    why: tasks_base 解析点，改为与 bash 侧共用解析
  - path: agate/scripts/check-state-transition.sh:23-31
    why: 任务级 .state.yaml 检测 grep（需去硬编码，改 dirname!=REPO_ROOT 语义）
  - path: agate/scripts/check-pruning.sh:64-67
    why: P7 源码文件数过滤模式（^docs/tasks/）需跟随工作区路径
  - path: agate/scripts/check-protocol-consistency.py:64-78
    why: PATH_IGNORE_SUBSTRINGS 白名单重校准
  - path: agate/scripts/install-hook.sh:81-89
    why: .state.yaml gitignore 提示文字路径
  - path: agate/orchestrator-template.md
    why: project.md / active-tasks / 接入 mkdir / 旧布局检测四处路径切换点（L21/25/69/93/94/113/115）
  - path: agate/state-machine.md:21-48
    why: 首接入初始化流程与阶段产出路径
  - path: agate/assets/templates/active-tasks-template.md
    why: roadmap-template 的 follows_existing_pattern 参照 + 复制目标路径更新
  - path: agate/tests/helpers/fixtures.bash
    why: create_task_dir（mktemp 不改）作为 fixture 结构参照；评估新增 AGATE_TASKS_DIR 测试变量
  - path: agate/tests/integration/pre-commit-hook.bats
    why: 最大改动面 fixture（42 用例），路径换血的代表性样本
  - path: agate/scripts/gate-result.sh
    why: 被 source 的函数库，resolve_workspace 函数（或解析脚本调用）落点
```

## 7. env_constraints

```yaml
env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0003-workspace-architecture/.state.yaml"
  test_cmd: "bats agate/tests/unit/"
  isolation_check: "改造对象 = worktree 的 agate/；~/.agate 指向主 checkout 稳定版 v0.40.2（禁止改动）。迁移工具/解析器行为在 BATS_TEST_TMPDIR fixture 仓库验证，不触 worktree 自身 live docs/tasks。CI 里 ~/.agate 软链不存在，load.bash 用 BATS_TEST_DIRNAME 反推 AGATE_ROOT"
```

## 8. minimal_validation

```yaml
minimal_validation:
  - assumption: "git mv 目录级迁移保留历史 + 物理移动含 gitignore/未追踪文件（BDD-7/8 核心假设）"
    method: "tmp git 仓库构造 docs/tasks/T001-fake（含 .state.yaml 被 *.state.yaml gitignore 场景），git mv docs/tasks agate-workspace/tasks"
    result: "confirmed —— 目录级 git mv 物理移动全部文件（含 gitignore 的 .state.yaml 与未追踪 .log），跟踪文件记 R rename，git log --follow 在新路径可追溯两 commit；gitignore 的 .state.yaml 未被遗漏"
    note: "git mv 目录级 = 一次性移动，与 .gitignore/跟踪状态解耦（P1 隐含需求 #2 直接满足）"
  - assumption: "git mv 边界行为：空源 / 目标非空 / 目标在仓库外"
    method: "分别实测 git mv 空目录（exit 128）、git mv 到已有内容的目标（exit 1）、git mv 到仓库外路径（exit 128）"
    result: "confirmed —— 空源 exit 128（迁移工具须第 2 步守卫 no-op，BDD-19）；非空目标 exit 1（须冲突检测防覆盖）；仓库外 exit 128（须 fallback 普通 mv，BDD-3 外部工作区场景）"
    note: "BDD-8 在外部工作区场景只能部分满足，fallback 时输出 WARNING 诚实标注"
  - assumption: ".agate.env 解析含空格路径 + AGATE_TASKS_DIR 优先级链（BDD-5/SUGGEST #2）"
    method: "tmp 项目构造 .agate.env（AGATE_WORKSPACE=ws 相对路径 + 'My Project' 含空格目录），grep+cut+realpath -m 解析并读写验证"
    result: "confirmed —— 含空格路径解析/读写正常；优先级链设计：.agate.env > AGATE_TASKS_DIR env > 默认 agate-workspace/（纯代码逻辑，不依赖外部系统）"
    note: "依赖内部逻辑：解析器读取顺序 + realpath 路径归一；引号包裹是空格路径正确性关键"
  - assumption: "移动路径后兜底分支（T086 B1 教训）：check-state-transition.sh 任务级检测 grep 改法"
    method: "读代码验证检测语义 —— 现 grep 'docs/tasks/[^/]+/' 决定 get_old_phase 用完整路径还是 basename；若不同步改，任务级文件走 basename 分支，git show HEAD:basename 取空 → 状态转移检查静默失效"
    result: "confirmed —— 必须去硬编码。改法 = dirname($STATE_FILE) != REPO_ROOT 即任务级（与 pre-commit-gate.sh L82 同构），不依赖任何具体路径，三种布局（docs/tasks/agate-workspace/外部）均正确路由"
    note: "移动 docs/tasks → 工作区后，原本依赖旧 grep 的任务级状态文件会流向 basename 兜底分支（错误）；改造后流向 dirname!=REPO_ROOT 判定（正确）"
  - assumption: "bats --formatter tap 输出可被 generic-tap.sh formatter 解析（P3/P5 gate 命令可用性）"
    method: "bats --formatter tap 实测输出 '1..N' + 'ok 1 t1'；对照 generic-tap.sh 正则（^ok\\b / ^not ok\\b）"
    result: "confirmed —— TAP 格式与 generic-tap.sh 匹配，P3/P5 gate 命令可用"
    note: "纯代码逻辑 + 本地工具实测，无外部系统依赖"
```

## 9. 实现完成标志

1. `agate-workspace-resolve.sh` 存在，三种解析分支（.agate.env 显式 / AGATE_TASKS_DIR env / 默认 agate-workspace/）均正确输出 `AGATE_WORKSPACE` 与 `AGATE_TASKS_DIR`；含空格路径解析正确。
2. `agate-migrate-workspace.sh` 存在，覆盖：docs/tasks → workspace/tasks（git mv 目录级）、docs/archived → workspace/archived、空源 no-op、幂等、外部工作区 fallback、迁移后清单对照。
3. `pre-commit-gate.sh` / `ci-gate-backstop.py` 通过解析器取 tasks_base，本地 hook 与 CI 解析同路径（fixture 双侧断言一致）。
4. `check-state-transition.sh` 任务级检测去硬编码（dirname!=REPO_ROOT 语义），既有 check-state-transition.bats 换血后全绿。
5. `check-pruning.sh` / `check-protocol-consistency.py` / `install-hook.sh` 路径同步，一致性检查 0 ERROR。
6. orchestrator-template.md 的 project.md / active-tasks / 初始化 mkdir / 旧布局检测四处切换完成；SETUP.md / UPGRADING.md 双路径指引齐全。
7. roadmap-template.md + WORKFLOW.md 循环规范就位，BDD-14/15/16 可验收（条目创建→拆任务→回写闭环有模板与规范支撑）。
8. WORKFLOW.md 内容边界判据节就位（BDD-17 文档锚点）。
9. 全部既有 bats 换血后 **603 条不漂移** + 新增解析器/迁移工具用例通过；`bats` 全量绿 + shellcheck clean + consistency 0 ERROR。
10. P7 双向一致性核对：43 文件/516 处引用与方案无偏差（DEVIATION 逐条记录）。

## 10. SCOPE+ 声明

[SCOPE+] 发现：check-state-transition.sh 的任务级 .state.yaml 检测（L28 grep `docs/tasks/[^/]+/`）是隐藏硬编码——P1 基线只列了 6 个引用脚本，但此 grep 是「检测逻辑」而非「路径提示」，漏改会让状态转移检查静默失效。
        必须做的理由：迁移后任务级文件路径不再含 docs/tasks，此 grep 永假 → get_old_phase 走 basename 分支 → 状态转移/重试上限检查全部失效（T086 B1 教训同构）。
        影响：check-state-transition.sh 需一并改造（改 dirname!=REPO_ROOT 语义，见 §3.6）；已纳入 P2 方案 §1.1 与 §8 minimal_validation#4，不需新增 BDD（BDD-13「行为不变」覆盖此点）。

[SCOPE+] 发现：check-pruning.sh 的 P7 源码文件数过滤（L66 `grep -cvE '^docs/tasks/...'`）是第二个隐藏硬编码——其作用是从暂存区排除任务文件后再计数，路径不同步会让裁剪 P7 的计数把任务文件误计入源码数。
        必须做的理由：过滤模式只排除 docs/tasks/，迁移后任务文件在新路径 → 源码文件数虚高 → P7 裁剪条件误判。
        影响：check-pruning.sh 过滤模式跟随工作区路径；纳入 P2 方案 §1.1（不新增 BDD，BDD-6/13 覆盖）。

[SCOPE+] 发现：worktree 自身 live docs/tasks（当前 TAG0003 任务目录）不应被此任务物理迁移。
        必须做的理由：迁移工具在 worktree 运行会移动正在执行的当前任务目录，破坏运行中的编排状态。
        影响：迁移工具验证全部走 fixture 仓库（BATS_TEST_TMPDIR）；worktree 自身迁移留待 P8 发布后用户侧升级动作；不新增 BDD（BDD-6 验收用 fixture 判定）。

## 参考

- 派发指引：P2-dispatch-context-architect.md（目标/约束/上游关联/输入文件）
- 需求基线：P1-requirements.md（20 条 BDD + 6 项已确认决策 + 4 SUGGEST）
- 评审意见：P1-review.md（approved；观察项 1：BDD-20 用例数口径；观察项 2：BDD-19/BDD-1 判定分离）
- 任务简报：P0-brief.md（A 策略、known_risks、env_constraints）
- 背景设计：docs/reviews/review-design-20260812-1428.md（方案丙 change_budget → roadmap 关联参考）
- 现状代码：agate/scripts/ 6 脚本 + orchestrator-template.md + assets/templates/ + tests/helpers/fixtures.bash + count-tests.sh + check-protocol-consistency.py
- 最小验证：§8（git mv 行为 / .agate.env 解析 / bats TAP / 移动路径兜底）
