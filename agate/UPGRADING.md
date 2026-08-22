# agate 升级指引

> 面向**已有 agate 项目**（已用旧版 agate 跑过任务）升级到新版本。
> 新接入项目不用看这里，直接读 `SETUP.md`。
> 升级前先读：`CHANGELOG.md`（本版本的变更）+ 本文件（旧数据怎么处理）。

---

## 核心原则：不动则无感

agate 的校验器（`agate-state-yaml-check.py` 等）**只在 .state.yaml 被 git add 暂存时才触发**（pre-commit 机制），不是扫描所有任务目录。所以：

- **旧任务数据（已完成/归档）如果不动它，升级后零检测触发、零问题**
- 只有"**要继续推进的进行中任务**"和"**新任务**"需要符合新版本规范

**升级最小动作**：`git pull` 拉新版 agate + 重跑 `install-hook.py`（见下文），其余按需。

---

## 1. 通用升级步骤

```bash
# 1. 升级 agate 本体（~/.agate 软链指向的仓库）
cd <你克隆 agate 的目录> && git pull

# 2. 重装 hook（推荐，pre-commit/commit-msg 软链自动跟随；pre-push 也是软链 v0.32+ 自动跟随）
python3 ~/.agate/scripts/install-hook.py

# 3. 验证版本
python3 ~/.agate/scripts/agate-summary.py   # 应显示新版本号
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

### v0.59.0 — 独立 Judge 机制（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 P6.5 独立 Judge 复核（P6 验收后、P7 之前，所有任务强制）：新角色 `assets/review-roles/judge.md`
  以 fresh context 逐条重验所有 BDD（含已 PASS 项），只信 `P6-evidence/` 证据与 git log。
- 新增检查脚本 `check-judge-verdict.py` + `check-events.py`；`check-gate.py` 增加 `P6.5` 分支——
  **只对启用了 judge 机制的任务生效**（`.state.yaml` 含 `judge.enabled: true`）；历史任务/存量任务
  无该字段 → P6.5 全链自动跳过（含 gate、pre-commit 注入、CI backstop 三处守卫一致）。
- 新增 append-only 事件账本 `{AGATE_WORKSPACE}/tasks/{Txxx}/gate-events.jsonl`（`append_event`
  单点写入，随任务目录落库）——仅新增文件，不改变既有 `.state.yaml` / 产出文件语义。

### v0.58.0 — TAG0019 风险分路由（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 `ceremony:` 声明字段（P1 frontmatter 可选，thin / standard / full）：缺省 standard（fail-closed——不声明或声明要素不满足一律按 standard 处理，不做薄化）；声明 thin 须四要素 checklist（coupling_checklist 流式 + 跳过风险 + P5/P6 保留）；`ceremony: full` 任务 phases 必须含 P7（P7 不可裁）。
- 新增 `check-routing.py` gate 挂载（pre-commit 2.7.1）：ceremony 路由校验——声明与算分 tier 一致性（单向 fail-closed）+ thin 四要素 checklist，不声明回退 standard。
- 新增 `agate-risk-score.py` 新工具：客观信号算分（文件类型 / 敏感路径 / 改动规模 / 影响面），输出 risk_score / tier（thin/standard/full）+ 逐信号证据行；提供可 import 的 `score_task(task_dir)` 与 CLI 薄壳。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号链接模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。

### v0.57.0 — DSH 平台支持（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- agate 新增对 DSH（deepseek-harness）平台的原生支持（RM-AG0030）：`assets/templates/dsh/`
  三文件（agent.cordis.yml / preset.yml / SKILL.md）+ `SETUP.md`「步骤 2-DSH」+ `platform-notes.md`
  DSH 条目 + `tests/unit/test_dsh_preset.py` 回归测试——全部为新增文件/新增章节，未改动任何既有
  协议机制运行时行为。
- **DSH 平台接入（新接入用户）见 `SETUP.md`「步骤 2-DSH」**：符号链接注册 orchestrator
  agent-preset 与 agate-protocol skill 后，在 DSH 会话选择器选「agate 编排者」即可按 P0-P8
  全流程使用。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号
  链接模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。

### v0.52.0 — 协议机制增强批（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 `{key}_timeout_seconds` **可选**声明性字段（`gate_commands` 块内，如 `P5_timeout_seconds`）——缺字段时行为等同现状（`check-gate.py` 未新增校验，无运行时消费方），既有任务不受影响。
- `dispatch-protocol.md` verification_env 节新增「失败处理协议」+「环境准备职责边界」子节（权威定义，P5/P6 卡片与 verifier.md 引用不重复展开）；「派发编排机制」并行规则新增第 4 条"资源密集型默认串行"；「派发 prompt 模板」新增"命令超时兜底"运行时纪律段落（与 `dispatch-prompt.md` 同步）——均为新增文档规则/运行时纪律，不改变任何既有 gate 脚本 exit code 语义。
- P0/P1/P2 三张阶段卡新增"同类扫描/影响面梳理"强制节 + P0-brief 时效性自检项（`[P0_STALE:]` 标记）——新增的是人工评审流程要求（requirements-review 打回判据），不对应脚本硬拦截，老任务不受影响。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号链接模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。

### v0.51.0 — agate UI/UX 验收质量机制（影响：frontend/UI 任务 + P6 截图证据路径）

> 版本号已由 P8 确认（v0.51.0）。TAG0006 为 agate 补充 UI/UX 验收质量机制：P1 vision 能力三态硬声明、P2 UI 设计节检查、P6 双证据三态分档 + 射线形态适配、avg-hash 雷同判定升级。**本版本破坏性变更 / 行为变化逐条列出**（供升级前三问"我的项目是否触及"）。

**① `avg-hash` 雷同截图判定从 WARNING 升级为「降级待复核」（影响：所有任务的 P6 截图证据路径）**：

| 升级前 | 升级后 |
|--------|--------|
| P6 验收中两条不同操作类 BDD 截图视觉高度相似（avg-hash 相同）→ 仅非阻断 WARNING（exit 2） | avg-hash 重复 → 判定为「降级待复核」——P6-acceptance.md 含人工复核记录（`雷同截图复核` / `manual-review: <file>` 引用且文件存在）→ 放行；无记录 → exit 1 阻断 |

- **md5 逐字节重复硬阻断语义不变**（原本就是 exit 1）。
- **行为差异类 BDD 视觉相同的场景**（如两个查询命中同一空状态）：优先改用非截图证据（断言日志/response.json），或用带时间戳/高亮差异的截图，确保逐字节不同；若必须用截图且视觉相近 → 走人工复核记录放行。
- **帧序列 `frames/` 与时序截图 `-tN` 系列**：同 BDD 组（bdd-id 前缀）内的相邻帧/相邻时刻**豁免**雷同判定（动画/时序正常特性），跨 BDD 组雷同仍按上表处理。
- 升级动作：既有任务如有 P6 截图证据即将面对该判定——按需补复核记录或改用非截图证据。

**② 新检查为"零动作则无感"门槛（不触发既有任务）**：P1 vision 三态、P1 渲染形态/维度声明、P2 UI 设计节检查——只在任务**新声明 `domains: frontend` / `ui_affected: true` / 形态字段**时才触发；既有任务（无这些声明）走默认（布局型 + available 语义），不新增硬校验、不红基线。**若未来某 frontend 任务 P1 漏声明 vision 条目 → 下次过 P1 gate 会 exit 1（这正是机制目标：强制声明）**。

**③ 渲染形态适配为可选（向后兼容）**：`ui_render_shape` / `ui_ux_dimensions` 为 P1 frontmatter **可选字段**（presence 语义），缺失 = 布局型默认。开启了渲染组件/时序特效形态的任务，P6 证据形式须按形态匹配（帧序列/渲染输出对比/时序截图），纯文本证据拦截。

---

### v0.47.0 — 测试框架 bats → pytest 迁移（影响：跑 agate 测试的开发者 / CI 维护者）

> 版本号已由 P8 确认（v0.47.0）。agate 测试套件从 Bats 全面迁移到 pytest（TAG0011）：`agate/tests/` 下 60 个 `.bats` 文件 / 749 @test 迁移为 `test_*.py` pytest 用例，`agate/tests/helpers/` 三文件（load.bash / fixtures.bash / git-helper.bash）退役，由 `agate/tests/conftest.py` fixture 体系承接。

**① 测试命令变化（跑 agate 测试的开发者必须改命令）**：

| 迁移前（bats） | 迁移后（pytest） |
|----------------|------------------|
| `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | `python3 -m pytest agate/tests/` |
| `bats agate/tests/unit/check-pruning.bats` | `python3 -m pytest agate/tests/unit/test_check_pruning.py` |
| `bats -c` 收集计数 | `python3 -m pytest --collect-only -q`（`count-tests.sh` 已改写为 pytest 收集计数） |

- 依赖从「Bats + shellcheck + python3-yaml」改为「**pytest + pyyaml**」；shellcheck 仍用于 3 个 hook 薄壳静态检查（CI `shellcheck` job 保留）
- **Windows 冒烟机制变化**：`check-windows-smoke.sh` 退役，Windows CI 冒烟由 `@pytest.mark.windows_smoke` marker 承接（`python3 -m pytest agate/tests/ -m windows_smoke`）——平台敏感用例的打标清单即代表集，语义与退役脚本的「每文件第 1 个用例 + 平台关键词用例」一致
- **目录变化**：`agate/tests/helpers/` 三文件退役；`agate/tests/` 下 60 个 `.bats` 已全部删除（0 残留），不再有 `.bats`，测试用例均为 `test_*.py` pytest 用例（`conftest.py` fixture、`agate/tests/scripts/count-tests.sh` 等支持文件保留）

**② CI matrix（项目维护者）**：`.github/workflows/protocol-tests.yml` 的 `bats` job 改为 `pytest` job（ubuntu/windows 双 matrix 保留：Linux 全量 + Windows `-m windows_smoke` 冒烟）。若你 fork/自建 CI 参考了 agate 的 workflow，注意此点——分支保护 required checks 需更新为实际 job 名（`pytest` / `pytest (ubuntu-latest)` / `pytest (windows-latest)` 等，含平台后缀）。

**③ ruff 覆盖范围（项目维护者）**：`ruff check agate/scripts/` 扩展为 `ruff check agate/`（含 tests，BDD-3）——测试代码也纳入 ruff 静态检查。

### v0.46.0 — 产品逻辑 Python 化（影响：所有已部署项目 + 直接调用脚本的用户）

> 版本号已由 P8 确认（v0.46.0）。这是 agate 自建以来最大的一次脚本层破坏性变更：`agate/scripts/` 下全部 30 个 `.sh` 脚本的 bash 逻辑迁移为 Python（`.py`），仅 3 个 git hook 入口保留 `.sh` 薄壳。

**① 脚本改名/删档清单（直接调用脚本的用户必须改命令）**：

| 迁移前（.sh） | 迁移后（.py） | 说明 |
|---------------|--------------|------|
| `check-changelog.sh` | `check-changelog.py` | 同名换后缀 |
| `check-frontmatter.sh` | `check-frontmatter.py` | 同名换后缀 |
| `check-state-yaml.sh` | `check-state-yaml.py` | 同名换后缀 |
| `check-p6-format.sh` | `check-p6-format.py` | 同名换后缀 |
| `check-scope-resolved.sh` | `check-scope-resolved.py` | 同名换后缀 |
| `agate-archive-stale-outputs.sh` | `agate-archive-stale-outputs.py` | 同名换后缀 |
| `agate-extract-context.sh` | `agate-extract-context.py` | 同名换后缀 |
| `agate-next-card.sh` | `agate-next-card.py` | 同名换后缀 |
| `agate-render-dispatch-prompt.sh` | `agate-render-dispatch-prompt.py` | 同名换后缀 |
| `agate-summary.sh` | `agate-summary.py` | 同名换后缀 |
| `agate-changes.sh` | `agate-changes.py` | 同名换后缀 |
| `agate-migrate-workspace.sh` | `agate-migrate-workspace.py` | 同名换后缀 |
| `check-platform-assumptions.sh` | `check-platform-assumptions.py` | 同名换后缀 |
| `check-state-transition.sh` | `check-state-transition.py` | 同名换后缀 |
| `check-retrospective.sh` | `check-retrospective.py` | 同名换后缀 |
| `check-pruning.sh` | `check-pruning.py` | 同名换后缀 |
| `check-debt.sh` | `check-debt.py` | 同名换后缀 |
| `check-tdd-red.sh` | `check-tdd-red.py` | 同名换后缀 |
| `check-gate.sh` | `check-gate.py` | 同名换后缀 |
| `check-p6-evidence.sh` | `check-p6-evidence.py` | 同名换后缀 |
| `check-p6-provenance.sh` | `check-p6-provenance.py` | 同名换后缀 |
| `agate-capture-env-baseline.sh` | `agate-capture-env-baseline.py` | 同名换后缀 |
| `agate-retreat-to.sh` | `agate-retreat-to.py` | 同名换后缀 |
| `agate-inject-card.sh` | `agate-inject-card.py` | 同名换后缀 |
| `install-hook.sh` | `install-hook.py` | 同名换后缀 |
| `pre-commit-gate.sh` | **保留 `.sh` 薄壳** + 新增 `pre-commit-gate.py` | hook 入口薄壳化：只做定位 AGATE_ROOT + python 探测 + exec py 主程序 |
| `commit-msg-self-gate.sh` | **保留 `.sh` 薄壳** + 新增 `commit-msg-self-gate.py` | 同上 |
| `pre-push-gate.sh` | **保留 `.sh` 薄壳** + 新增 `pre-push-gate.py` | 同上 |
| `gate-result.sh` | **删档** → 并入 `agate_common.py` | 函数库合并为公共模块 |
| `agate-workspace-resolve.sh` | **删档** → 并入 `agate_common.py` | 工作区解析合并为公共模块 |

- **调用命令变化**：`bash ~/.agate/scripts/xxx.sh` → `python3 ~/.agate/scripts/xxx.py`（hook 薄壳仍由 git 经 sh 执行，无需手动调）
- **新增 `agate_common.py`**：承载原 gate-result.sh + agate-workspace-resolve.sh 的函数库（`write_gate_result` / `read_state_phase` / `resolve_workspace` / `probe_python` / `run_git` / `MAX_RETRY_MAP` 等），执行模式输出 `AGATE_WORKSPACE=` / `AGATE_TASKS_DIR=` 两行（workspace-resolve 契约不变）
- 3 个 hook 薄壳是**仅存的 `.sh`**；`agate/tests/scripts/count-tests.sh` 已改写为 pytest 收集计数、`check-windows-smoke.sh` 已退役（TAG0011，Windows 冒烟由 pytest marker 承接）

**② install-hook 迁移命令**：

```bash
# 旧：bash ~/.agate/scripts/install-hook.sh
python3 ~/.agate/scripts/install-hook.py
```

- **符号链接模式（Linux/macOS 标准）**：hook 为 `ln -sf` 软链 → 升级 agate 后**自动跟随新代码，无需重装**。不放心可重跑一次上面的命令确认。
- **复制模式（Windows 无符号链接权限）**：hook 是复制品，不自动跟随 → **必须重跑** `python3 ~/.agate/scripts/install-hook.py`（会以复制模式重装 + 写 `.agate-root` 标记）。
- 手动复制的 hook（早期版本 `cp` 方式）：同样重跑上面的命令。

**③ shellcheck → ruff（开发者）**：

- `shellcheck` 扫描面收敛到 3 个 hook 薄壳（`shellcheck -S warning agate/scripts/*.sh` 只覆盖它们）
- Python 脚本改用 **ruff** 静态检查：`ruff check agate/scripts/`（规则集在仓库根 `pyproject.toml`，TAG0010 交付）——CI `ruff` job 独立运行
- `bash agate/tests/scripts/count-tests.sh` 仍可用——已改写为 pytest 收集计数（TAG0011）

**④ python3 + pyyaml 强制依赖（影响：所有已部署项目）**：

- 全部 gate 逻辑现为 Python，**pyyaml 从「可选」变为「强制」**（agate_common.py 及所有状态读取工具 import yaml，缺失时 fail-closed exit 1）
- 安装：`pip install pyyaml`（Python 3.8+）
- **hook 薄壳 fail-closed 语义**：薄壳探测不到 python3/python 或对应 `.py` 缺失时，输出 `GATE ERROR` 并 **exit 1 阻断 commit**（不静默放行、无 sh 兜底逻辑）——Windows 无 python 环境的机器 commit 会被阻断，需先装 python3 + pyyaml
- Pillow 仍为可选（仅 check-p6-evidence.py 的像素方差/ahash）

**⑤ 无 bash 环境（纯 cmd/PowerShell）成为可行选项**：gate 脚本已全部 Python 化，`python3` 可直接运行（P0-P8 全程可执行）；唯一受限是 git hook 入口薄壳仍需 sh（Git for Windows）。详见 `platform-notes.md`「Windows 原生」。

### v0.50.0 — agate 版本管理机制（~/.agate 目录化 + .agate-version + hook 解析入口迁移，影响：所有已部署项目）

> 版本号已由 P8 确认（v0.50.0）。TAG0008 交付 agate 版本管理机制 v1：`~/.agate` 从**单一软链**升级为**版本管理根目录**（`repo/` + `vX.Y.Z/` 版本目录 + `latest`/`current` 纯指针），新增 `agate-install` / `agate-resolve` / `agate-pack-offline` / `install-offline` 4 个工具，hook 从"指向具体版本脚本"改为"经固定解析入口 resolve-entry 按项目 `.agate-version` 解析版本"。

**① `~/.agate` 布局变化（安装层，影响：管理 agate 本体的人）**：

| 迁移前（≤ v0.49.0） | 迁移后（v0.50.0+） |
|---------------------|---------------------|
| `~/.agate` = 软链 → 仓库的 `agate/` 子目录 | `~/.agate/` = 版本管理根目录：`repo/`（唯一主仓库）+ `vX.Y.Z/`（worktree 检出 tag）+ `latest`/`current` 纯指针 + `scripts/`（版本管理工具） |
| 升级 = `git pull` + hook 自动跟随 | 升级 = `python3 ~/.agate/scripts/agate-install.py`（装最新版，指针切到新版本目录） |
| 卸载 = `rm ~/.agate` + 删仓库 | 卸载 = `python3 ~/.agate/scripts/agate-install.py --uninstall vX.Y.Z`（含引用保护：仍有项目锁定该版本时拒绝卸载） |

- **存量单软链用户不跑新工具时行为不变（红线，BDD-30）**：`~/.agate` 仍是软链 → 旧 checkout 的 `agate/` 子目录，无版本目录/无指针时，resolve 直接把软链目标解析为 AGATE_ROOT，hook 照常按既有语义运行——**无迁移动作即可继续用**，gate 不静默禁用。
- **`install.sh` 兼容保留**：单软链场景仍可用，不破坏存量升级路径。

**② `.agate-version` 项目级版本锁定（新机制，可选）**：

- 项目根放 `.agate-version`，内容 `agate: v0.43.0`（v1 只支持精确版本，asdf 模式 cwd 向上找）。
- 声明版本后该项目 commit 用**该版本**的 gate 逻辑判定；改声明即生效，**不用重装 hook**。
- 声明版本未安装 / 格式非法（含空文件）→ stderr 警告 + 回退 current（**绝不静默禁用 gate**）。
- 不声明 = 用全局 `current`（默认 → latest = 最新发布版），与旧行为等价。

**③ hook 解析入口迁移（机制内部，用户无需重装 hook）**：

- `install-hook.py` 现在安装**固定解析入口** `resolve-entry.py`（不随版本变）到 `.git/hooks/`，运行时读项目 `.agate-version` → exec 对应版本 gate py。
- **符号链接模式（Linux/macOS 标准）**：升级后 hook 自动跟随新解析入口，无需重装。
- **复制模式（Windows 无符号链接权限）**：hook 是复制品，不自动跟随 → **必须重跑** `python3 ~/.agate/scripts/install-hook.py`（复制模式 + `.agate-root` 标记保留）。
- AGATE_ROOT env 显式覆盖仍是最高优先级（既有契约未破坏）。

**④ 新工具（可选使用）**：

- `agate-install.py`：安装/卸载/环境探测（`--check` 输出 python3/pyyaml/git/bash 探测结果，exit code 可判 + 分平台修复指引）。
- `agate-resolve.py`：解析项目实际使用的版本（输出 AGATE_ROOT/AGATE_VERSION/AGATE_REASON）。
- `agate-pack-offline.py` + `install-offline.py`：外网打包 → 内网离线安装闭环（平台核对 + checksum 校验 + 版本目录 + hook 指向）。

**⑤ agate-summary 语义变化（显示层，提示文案变更）**：`agate-summary.py` 不再显示仓库自身 tag，改为显示**当前项目解析到的版本 + 原因**（`.agate-version` 或全局 current）——排障时直接可见"项目用哪个版本、为什么"。

**迁移动作小结**：
- 存量单软链用户：无强制迁移（legacy 兜底，BDD-30）。
- 想用版本隔离：跑 `python3 ~/.agate/scripts/agate-install.py` 装最新版 → 项目加 `.agate-version` → 重跑 `install-hook.py`（Windows 复制模式必须重跑）。
- 已验证：31 条 BDD 全 PASS（含 BDD-30 存量软链不受破坏红线）。

### v0.49.0 — 派发编排机制（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 `dispatch_plan:` **可选**机器字段（P2-design.md frontmatter 单行 flow YAML，mode/batches/parallel_limit）——缺字段 / 坏 YAML 时 P2 gate 跳过校验，既有任务行为与改造前完全一致（向后兼容）。
- `dispatch-protocol.md`「任务粒度指引」节升级为「派发编排机制」权威节（五维工作量评估 + 五模式编排 + 模式 4 流程 + 并行规则 + 全阶段适用表）；既有引用点（L118/L132/L211 + task-files.md）措辞同步更新，锚点位置不变，一致性 CHECK 3 零漂移。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号链接模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。

### v0.48.0 — 脚本一致性 gate（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 CHECK 10「协议文档脚本名引用漂移」一致性检查（增量，当前 0 漂移），self-gate 触发面补 README/AGENTS（内部行为），check-retrospective 追加登记提醒行（纯提醒）——用户可见协议语义不变。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号链接模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。

### v0.45.0 — backend 域 P2 评审触发 + 平台假设扫描器（影响：所有已部署项目）

**① backend 域任务 P2 现强制派发方案评审（plan-eng-review）**（RM-AG0010）：
- C8 映射表 backend 行新增 `plan-eng-review（P2 方案评审）`（保留 `review（P4 后）`）。**所有 backend 域任务（含 low/medium）P2 阶段现在必须派发一个 plan-eng-review 评审 subagent 产 P2-review.md**，否则 check-gate.py P2 会 exit 1 拦截。
- 这是「P2 gate 无条件要求 P2-review.md」契约矛盾的对齐——之前 backend low/medium 任务按 C8 不派评审被 gate 拦截、主 Agent 被迫自造评审（TPV0090），现在契约一致了。
- 同任务命中多个触发行且同一评审角色时去重只派一次（backend+high 均命中 plan-eng-review → 只派 1 个）。

**② 新增平台假设静态扫描器（测试基建，影响：测试套件维护者）**：
- 新增 `agate/scripts/check-platform-assumptions.py` 扫描 `agate/tests/` 全树 Unix 假设（硬编码 PATH / 裸 python3 / `[[ -L ]]` / /tmp / bc 等），CI `platform-scan` job 阻断。
- **测试平台无关原则是硬要求**：写新测试不得硬编码单平台假设（AGENTS.md「测试约定」）；被扫描器检出的假设会导致 CI 失败。

**③ bats job 增 windows-latest matrix（CI 维护者，TAG0011 后为 pytest job）**：bats job 改 matrix 后 job 名带平台后缀（如 `bats (windows-latest)`，TAG0011 起 pytest job 同名规则 `pytest (windows-latest)`），分支保护 required checks 需更新。

**④ P5 gate_commands 计数语义**：check-gate.py P5 WARNING 文案改「X 个主命令 + Y 个辅助命令」——不影响判定逻辑，仅文案区分主/辅。

### v0.44.0 — 脚本健壮性 + Windows 环境适配（影响：所有已部署项目）

**① Windows 用户**：agate 现在支持 Git for Windows/MSYS2 下运行 gate 脚本（Windows 原生兼容）。
- 依赖：Git for Windows（自带 bash/coreutils），python3 + pyyaml，Git Bash 作为执行 shell。
- 见 `SETUP.md`「Windows 原生」章节（AGATE_ROOT 用 Unix 风格路径 `/c/...`、`PYTHONUTF8=1`、`core.autocrlf` 与 CRLF）。
- 若你的 hook 是复制模式安装（无符号链接权限），升级后**重跑 install-hook.py** 更新 hook。

**② 非 Windows 用户**：本版本为修复型，Linux 行为不变（676→714 bats 全绿回归，bats 时代基线）。无需迁移动作。

**③ CI matrix（项目维护者）**：`.github/workflows/protocol-tests.yml` 新增 `windows-latest` 平台矩阵（bats/shellcheck/consistency/gate-backstop；TAG0011 起 bats job 改 pytest job）。分支保护 required checks 需更新为实际 job 名（含平台后缀，如 `shellcheck (ubuntu-latest)`）——若你 fork/自建 CI 参考了 agate 的 workflow，注意此点。

**④ 路径含空格/特殊字符的项目**：`pre-commit-gate.sh` 内部数组化（S1 修复）——路径含空格/`[`/`]`/`*` 时 gate 不再静默绕过。行为更严格但更正确。

**⑤ 中文证据文件名（P6 任务）**：check-p6-evidence.py 证据引用正则加宽，中文文件名正确匹配。之前因中文证据名被误拦的项目现在可正常通过。

**⑥ 阶段卡片 phase 语义（文档，无强制）**：P1/P2/P3/P4/P6/P7/P8 卡片补注"commit 时 phase = 本 commit 产出阶段"。仅文档说明，gate 判定逻辑零改动，遵循既有习惯即可。

### v0.43.0 — 技术债登记闭环 + 工作区子目录 8→9（影响：进行中任务 + 已部署项目）

**① 工作区子目录集 8→9（新增 `debt/`，可选启用）**：
- 工作区目录集从 8 个扩为 9 个（roadmap/tasks/agents/archived/reviews/decisions/plans/logs/**debt**），`debt/` 为技术债登记目录。
- 存量项目**无需迁移动作**：技术债登记是新增可选机制，不建 `debt/` 时行为不变（校验器/回退比对/P8 留痕在无 tech-debt.md 时 no-op）。要启用技术债登记，运行 `mkdir -p {AGATE_WORKSPACE}/debt`。
- 归类修正：tech-debt 不再归入 `agents/`（该目录只放 agent 输入知识 project.md/memory）；`{AGATE_WORKSPACE}/agents/` 若已有 tech-debt.md，可手动移到 `{AGATE_WORKSPACE}/debt/tech-debt.md`。

**② tech-debt.md 路径**：技术债登记文件位于 `{AGATE_WORKSPACE}/debt/tech-debt.md`（模板 `assets/templates/tech-debt-template.md`），不再指向 agents/。

**③ P8-release.md 新增 `debt_check` 必填字段**：发布准备阶段确认债务清单并留痕（`none` = 本次无关注项 / `reviewed` = 已核对）。check-gate.py P8 分支对缺失该字段的 P8-release.md 硬拦截（exit 1）；字段存在则内容任意放行（不阻断发布）。

**④ 回退落地后必须建 DEBT 条目**：任何正式回退（`retreat:` 提交）完成后必须建立 `source: retreat` 的 DEBT 条目（`evidence` 引用 retreat 提交哈希）。`check-debt.py --retreat-coverage` 会把未登记的 retreat 提交比对出来并报 WARNING（只读提醒，不挂 gate）。

### v0.41.0 — 工作区架构（docs/tasks → agate-workspace/）（影响：所有已部署项目 + 进行中任务）

**背景**：agate 的全部编排状态（任务/看板/归档/评审/决策/计划/日志/roadmap/agent 知识）从项目 `docs/tasks/`、`docs/agents/`、`docs/archived/` 迁移到**工作区**（默认项目根 `agate-workspace/`，可用 `.agate.env` 配置位置）。orchestrator 从工作区读取 project.md 与 active-tasks，不再读 `docs/` 下旧路径。

**① 迁移工具（推荐）**：在项目根运行

```bash
python3 {agate_root}/scripts/agate-migrate-workspace.py
```

**迁移前先处理暂存区**：迁移工具会自动 commit 目录 rename（保留 git 历史），commit 用 pathspec 限定只提交迁移目录，不会带上迁移前已暂存的无关改动——但为避免状态混乱，建议先 `git commit` 或 `git unstage`（`git reset`）掉无关的已暂存改动，让暂存区只含迁移内容。

工具自动完成：
- `docs/tasks/`（含 active-tasks.md + 全部任务目录 + 被 gitignore 的 `.state.yaml`）→ 工作区 `tasks/`（git mv 目录级，保留 git 历史）
- `docs/archived/` → 工作区 `archived/`
- 空源 no-op（项目从无 docs/tasks 时正常退出）
- 幂等：重复运行无新增动作

迁移后验证：`ls {AGATE_WORKSPACE}/tasks/` 应包含 active-tasks.md 与任务目录；`python3 {agate_root}/scripts/agate-summary.py` 正常。

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
python3 ~/.agate/scripts/agate-summary.py

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
