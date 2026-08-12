# agate 升级指引

> 面向**已有 agate 项目**（已用旧版 agate 跑过任务）升级到新版本。
> 新接入项目不用看这里，直接读 `SETUP.md`。
> 升级前先读：`CHANGELOG.md`（本版本的变更）+ 本文件（旧数据怎么处理）。

---

## 核心原则：不动则无感

agate 的校验器（`agate-state-yaml-check.py` 等）**只在 .state.yaml 被 git add 暂存时才触发**（pre-commit 机制），不是扫描所有任务目录。所以：

- **旧任务数据（已完成/归档）如果不动它，升级后零检测触发、零问题**
- 只有"**要继续推进的进行中任务**"和"**新任务**"需要符合新版本规范

**升级最小动作**：`git pull` 拉新版 agate + 重跑 `install-hook.sh`（见下文），其余按需。

---

## 1. 通用升级步骤

```bash
# 1. 升级 agate 本体（~/.agate 软链指向的仓库）
cd <你克隆 agate 的目录> && git pull

# 2. 重装 hook（推荐，pre-commit/commit-msg 软链自动跟随；pre-push 也是软链 v0.32+ 自动跟随）
bash ~/.agate/scripts/install-hook.sh

# 3. 验证版本
bash ~/.agate/scripts/agate-summary.sh   # 应显示新版本号
```

**符号链接 vs 复制模式**：
- **符号链接**（Linux/macOS 标准）：协议本体升级后自动生效，无需额外操作
- **复制模式**（Windows 无符号链接权限）：协议本体的**修改不会自动同步**到项目副本，需重跑 `cp` 命令（见 SETUP.md 步骤 2 的 Windows 段）
- **orchestrator 注册**：软链方式自动跟随；复制方式需重跑 SETUP.md 步骤 2 的 `cp`

---

## 2. 旧数据兼容策略

### 2.1 active-tasks.md（看板）

| 旧任务状态 | 处理 |
|-----------|------|
| 已完成/归档 | **不动**，保留旧编号（历史记录） |
| 进行中 | **改编号**为新格式（见 2.2），列结构本身不变 |

**列结构（进行中/待开始/已完成 + 各列头）在 v0.40.x 未变**——只有任务编号格式变了。

### 2.2 任务编号（⚠️ v0.40.0 破坏性变更）

- **旧格式**：`T001` / `T002`（`^T\d+$`）
- **新格式**：`TAG0001`（`^T[A-Z]{2}\d+$`，项目代号 2 个大写字母 + 数字）
- **硬切不兼容**：`T001` 在新校验器下会被拦（`agate-state-yaml-check.py`）

**迁移动作（仅进行中任务）**：
```bash
# 修改进行中任务的 .state.yaml 的 task_id
# T001 → TAG0001（选你项目的 2 字母代号 + 数字）
# 路径按你项目的实际任务目录（v2.0 起在工作区 {AGATE_WORKSPACE}/tasks/ 下）
# Linux：sed -i 's/^task_id: T001$/task_id: TAG0001/' {AGATE_WORKSPACE}/tasks/T001-*/.state.yaml
# macOS（BSD sed 的 -i 需空后缀）：sed -i '' 's/^task_id: T001$/task_id: TAG0001/' {AGATE_WORKSPACE}/tasks/T001-*/.state.yaml
```

**已完成的旧任务**：编号保留 `T001`，不进新格式（历史记录，不被扫描）。

### 2.2.1 项目代号（`AG`/`PV`）语义

- **来源**：项目接入 agate 时**自行约定** 2 个大写字母代号（对齐 Jira `[A-Z][A-Z]+` 风格），agate **不自动生成**。例如 `AG`=agate 改造、`PV`=peekview。
- **一致性**：**同一项目应用同一代号**（`active-tasks-template.md` 第 4 条规则："项目局部命名空间内按项目代号 + 动态编号递增"）。不同项目可用不同代号（`TAG0001`/`TPV0001` 各不同，正常）；**同一项目混用代号会破坏编号的"项目标识"意义**，看板/追溯会混乱。
- **校验边界**：`agate-state-yaml-check.py` **只校验格式**（`^T[A-Z]{2}\d+$`），**不校验代号一致性**——`TAG0001`/`TPV0001`/`TXX0001` 格式都合法。代号一致性靠**项目约定 + 看板规则**维持，无强制拦截。若你的项目需要强制，可自行加检查（当前 agate 未内置）。
- **升级时**：为进行中的旧任务选代号时，**用你项目的既有代号**（若有约定），或新定一个并在 active-tasks-template 里记录，保持全项目一致。

### 2.3 旧任务目录

- v2.0 起任务目录位于工作区 `{AGATE_WORKSPACE}/tasks/` 下
- 旧目录 `docs/tasks/T001-xxx/` 保留不动 = 无检测触发（迁移工具会将其迁入工作区 `tasks/`，见 v0.41.0 变更节）
- 新任务用新目录 `{AGATE_WORKSPACE}/tasks/TAG0001-xxx/`

### 2.4 项目侧文件（project.md 等）

- `{AGATE_WORKSPACE}/agents/project.md`（项目特定信息，v2.0 起位于工作区）**不在 agate 协议内，不会自动升级**——若其内容引用了旧编号格式（`T001`）或旧看板结构，需手动同步
- 其他项目自有文件同理：升级后检查一次即可，agate 不负责这些

---

## 3. 已知破坏性变更（按版本）

> 升级到新版本前，检查你的项目是否触及以下变更点。

### v0.43.0 — 技术债登记闭环 + 工作区子目录 8→9（影响：进行中任务 + 已部署项目）

**① 工作区子目录集 8→9（新增 `debt/`，可选启用）**：
- 工作区目录集从 8 个扩为 9 个（roadmap/tasks/agents/archived/reviews/decisions/plans/logs/**debt**），`debt/` 为技术债登记目录。
- 存量项目**无需迁移动作**：技术债登记是新增可选机制，不建 `debt/` 时行为不变（校验器/回退比对/P8 留痕在无 tech-debt.md 时 no-op）。要启用技术债登记，运行 `mkdir -p {AGATE_WORKSPACE}/debt`。
- 归类修正：tech-debt 不再归入 `agents/`（该目录只放 agent 输入知识 project.md/memory）；`{AGATE_WORKSPACE}/agents/` 若已有 tech-debt.md，可手动移到 `{AGATE_WORKSPACE}/debt/tech-debt.md`。

**② tech-debt.md 路径**：技术债登记文件位于 `{AGATE_WORKSPACE}/debt/tech-debt.md`（模板 `assets/templates/tech-debt-template.md`），不再指向 agents/。

**③ P8-release.md 新增 `debt_check` 必填字段**：发布准备阶段确认债务清单并留痕（`none` = 本次无关注项 / `reviewed` = 已核对）。check-gate.sh P8 分支对缺失该字段的 P8-release.md 硬拦截（exit 1）；字段存在则内容任意放行（不阻断发布）。

**④ 回退落地后必须建 DEBT 条目**：任何正式回退（`retreat:` 提交）完成后必须建立 `source: retreat` 的 DEBT 条目（`evidence` 引用 retreat 提交哈希）。`check-debt.sh --retreat-coverage` 会把未登记的 retreat 提交比对出来并报 WARNING（只读提醒，不挂 gate）。

### v0.41.0 — 工作区架构（docs/tasks → agate-workspace/）（影响：所有已部署项目 + 进行中任务）

**背景**：agate 的全部编排状态（任务/看板/归档/评审/决策/计划/日志/roadmap/agent 知识）从项目 `docs/tasks/`、`docs/agents/`、`docs/archived/` 迁移到**工作区**（默认项目根 `agate-workspace/`，可用 `.agate.env` 配置位置）。orchestrator 从工作区读取 project.md 与 active-tasks，不再读 `docs/` 下旧路径。

**① 迁移工具（推荐）**：在项目根运行

```bash
bash {agate_root}/scripts/agate-migrate-workspace.sh
```

**迁移前先处理暂存区**：迁移工具会自动 commit 目录 rename（保留 git 历史），commit 用 pathspec 限定只提交迁移目录，不会带上迁移前已暂存的无关改动——但为避免状态混乱，建议先 `git commit` 或 `git unstage`（`git reset`）掉无关的已暂存改动，让暂存区只含迁移内容。

工具自动完成：
- `docs/tasks/`（含 active-tasks.md + 全部任务目录 + 被 gitignore 的 `.state.yaml`）→ 工作区 `tasks/`（git mv 目录级，保留 git 历史）
- `docs/archived/` → 工作区 `archived/`
- 空源 no-op（项目从无 docs/tasks 时正常退出）
- 幂等：重复运行无新增动作

迁移后验证：`ls {AGATE_WORKSPACE}/tasks/` 应包含 active-tasks.md 与任务目录；`bash {agate_root}/scripts/agate-summary.sh` 正常。

**② 手工迁移（不用工具时）**：`git mv docs/tasks {AGATE_WORKSPACE}/tasks`、`git mv docs/archived {AGATE_WORKSPACE}/archived`；`.state.yaml` 若被 gitignore 需 `git add -f` 后随目录移动。

**③ 项目侧文件位置变化**：
- `docs/agents/project.md` → `{AGATE_WORKSPACE}/agents/project.md`（模板 `assets/templates/project.md`）
- `docs/tasks/active-tasks.md` → `{AGATE_WORKSPACE}/tasks/active-tasks.md`（非本仓：使用者项目旧路径）
- 项目 README 等产品文档**留在**项目 `docs/` 不动（内容边界判据：编排状态进工作区，产品文档留项目 docs/，见 WORKFLOW.md「内容边界判据」）

**④ 未迁移时的行为**：orchestrator 启动检测到旧布局（`docs/tasks/active-tasks.md` 存在而工作区 tasks 无 active-tasks，非本仓：使用者项目旧路径）→ 输出迁移指引并停止自动推进，不静默使用旧路径。

**⑤ 外部工作区**：`.agate.env` 指向项目外路径时，git mv 无法跨仓库（fallback 普通 `mv` + WARNING「git 历史无法在新路径追溯」）。

### v0.40.0 — 任务编号硬切 + orchestrator 符号链接接入（影响：进行中任务 + 已部署项目）

**① 任务编号硬切**：
- `task_id` 从 `T\d+` 硬切为 `T[A-Z]{2}\d+`（如 `TAG0001`），**不兼容旧格式**
- 影响：进行中任务的 `.state.yaml` 必须改编号；已完成任务不受影响
- 迁移见上文 2.2

**② orchestrator 从拷贝改为符号链接接入**（对已部署项目影响最大）：
- 旧方式：把 `orchestrator-template.md` 拷贝到项目并手改字段
- 新方式：**删除旧拷贝文件 `docs/agents/orchestrator.md`（若存在）**，按 `SETUP.md` 重新建立符号链接（`.claude/agents/orchestrator.md` / `.opencode/agents/orchestrator.md` 直接指向 `~/.agate/orchestrator-template.md`）
- 原来内联在 orchestrator.md 里的项目特定约束，迁移到新建的 `docs/agents/project.md`（模板见 `assets/templates/project.md`）
- 影响：不迁移则 orchestrator 仍是旧拷贝，不跟随新版本

### v0.31.0 — P2 必填 candidate_count 字段（影响：P2 设计阶段）
- `P2-design.md` 必须显式声明 `candidate_count: N`（替代正则数标题）
- 影响：新任务的 P2 产出需含该字段；旧任务若重新走到 P2 需补

### v0.17.0 — 标记格式收紧（影响：产出文件标记写法）
- `[PROD_TOUCHED]`/`[NEED_CONFIRM]` 必须行首声明，句中引用会被拦截
- `无 [PROD_TOUCHED]` 等否定写法不再接受，须用 `[PROD_NOT_TOUCHED]`
- 影响：写 dispatch-context/产出文件时标记要行首

### v0.29.x 及更早
- 如需了解，查 `CHANGELOG.md` 对应版本

---

## 4. 升级后验证

```bash
# 1. 版本
bash ~/.agate/scripts/agate-summary.sh

# 2. 协议一致性（0 ERROR）
python3 ~/.agate/scripts/check-protocol-consistency.py

# 3. 进行中任务的 .state.yaml 能通过校验
cd <项目目录>
git add {AGATE_WORKSPACE}/tasks/{进行中任务}/.state.yaml
# 触发 pre-commit → 应无"task_id 格式错误"
git reset   # 取消暂存
```

---

## 5. 常见问题

**Q: 旧任务目录会导致升级后报错吗？**
A: 不会——只要不暂存它的 `.state.yaml`。consistency 不查 .state.yaml 格式，pre-commit 只在暂存时校验。v2.0 起旧任务目录会由迁移工具迁入工作区，未迁移时 orchestrator 会输出迁移指引。

**Q: 必须把旧任务编号都改成 TAG0001 吗？**
A: 只有"继续进行中的"必须改。已完成/归档的保留旧编号即可。

**Q: 复制模式（Windows）升级后 orchestrator 提示词是旧的？**
A: 是——复制模式不自动同步，需重跑 SETUP.md 步骤 2 的 `cp`。软链模式无此问题。
