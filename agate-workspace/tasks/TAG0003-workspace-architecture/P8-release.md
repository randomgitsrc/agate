---
phase: P8
task_id: TAG0003-workspace-architecture
type: release
parent: P7-consistency.md
trace_id: TAG0003-P8-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0003 — agate 工作区架构：P8 发布准备

> 角色：releaser subagent（implementer P8 模式）。
> 本文件是**发布准备记录**——只给出建议（bump_type / 版本号 / CHANGELOG 内容 / 临时资源清单），**不执行 git commit / git tag / bump-version**（主 Agent 在 gate 验证后亲自执行）。
> 发布对象：worktree `agate/`（新版协议，含 TAG0003 全部改动）；`~/.agate` 是稳定版 v0.40.2 开发工具（本任务全程未动）。
> 环境标记：`[PROD_NOT_TOUCHED]` 本次 P8 只读 P0-P7 产出 + git 只读查询 + /tmp/opencode 临时目录核查，未修改任何 agate/ 文件，未接触生产环境；`~/.agate` 稳定版未动。

## 1. bump_type 与版本号变更确认

```
bump_type: minor
旧版本号：v0.40.2
建议新版本号：v0.41.0
```

**理由（主 Agent 决策，2026-08-12）**：

| 判据 | 依据 | 结论 |
|------|------|------|
| 变更性质 | 破坏性变更：docs/tasks 强制迁移到 agate-workspace/（P0-brief known_risks A 策略已确认）、orchestrator 路径改动影响所有接入项目（P2-design §1.3） | major 候选 |
| 项目版本策略 | WORKFLOW.md L7 明文：「规则新增/调整升 minor（v1.1.0），破坏性变更升 major（v2.0.0）」 | major 候选 |
| **主 Agent 决策** | **用户明确指示「不用 2.0，bump 小版本号就行」**——采纳 minor，版本号 v0.41.0。用户是版本策略的最终决策者，supersede 版本策略建议；CHANGELOG 中破坏性变更仍显著标注（工作区迁移 + UPGRADING.md 迁移指引），语义上属于「v2.0 系列改造的中间里程碑」，待后续流全部合入后再升 major | **minor → v0.41.0** |

**版本文件**：`README.md` L6 version badge（`v0.40.2` → `v0.41.0`）。按 AGENTS.md 版本发布流程：主 Agent 更新 badge → `git tag v0.41.0 && git push origin v0.41.0` → CHECK 7（badge vs tag）自动通过。无独立 VERSION 文件。

**发布前置验证（主 Agent 亲自执行，不可跳过）**：
- P5 gate 重跑：`bats ... 2>&1 | tail -30`（631/0）+ `check-protocol-consistency.py`（0 ERROR）+ `shellcheck -S warning agate/scripts/*.sh`（0）+ `count-tests.sh`（625）——P5/P6/P7 已绿（2bf9221/6bf3110/2c833f3），bump 后需重跑 P5 gate 确认仍全绿
- `git log v0.40.2..HEAD --oneline`（27 commit）对照下方 CHANGELOG 建议无遗漏
- **release PR 必须普通 merge（--no-ff），禁止 squash**（AGENTS.md 版本发布流程——git tag 需成为 main 祖先，v0.31.0 事故教训）

## 2. CHANGELOG 更新建议

`CHANGELOG.md` 当前顶部为 `## [0.40.2] - 2026-08-11`（无 [Unreleased] 节）。建议在 L11 之前插入以下新版本号节（Keep a Changelog 格式）：

````markdown
## [0.41.0] - 2026-08-12

### 破坏性变更（TAG0003 工作区架构）
- **编排状态迁移到工作区（agate-workspace/）**：agate 的全部编排状态（任务/看板/归档/评审/决策/计划/日志/roadmap/agent 知识）从项目 `docs/tasks/`、`docs/agents/`、`docs/archived/` 迁移到**工作区**（默认项目根 `agate-workspace/`，可用 `.agate.env` 的 `AGATE_WORKSPACE=` 配置位置）。orchestrator 从工作区读取 `agents/project.md` 与 `tasks/active-tasks.md`，不再读 `docs/` 下旧路径——**影响所有已部署项目**。⚠️ 存量项目升级前必读 `agate/UPGRADING.md` §3「v0.41.0」迁移节（迁移工具步骤见下）
- **新增迁移工具 `agate-migrate-workspace.sh`**：目录级 `git mv` 强制迁移 `docs/tasks/` → `{workspace}/tasks/`、`docs/archived/` → `{workspace}/archived/`，保留 git 历史；空源 no-op、重复运行幂等、外部工作区 fallback 普通 mv（WARNING 标注历史不可在新路径追溯）。在项目根运行 `bash {agate_root}/scripts/agate-migrate-workspace.sh`
- **未迁移时的行为**：orchestrator 启动检测到旧布局（`docs/tasks/active-tasks.md` 存在而工作区 tasks 无 active-tasks）→ 输出迁移指引并停止自动推进，不静默使用旧路径

### 新增（TAG0003 工作区架构）
- **`agate-workspace-resolve.sh`**：工作区路径单点解析器——解析优先级 `.agate.env`（`AGATE_WORKSPACE=`）> 环境变量 `AGATE_TASKS_DIR`（向后兼容既有 CI 设置）> 默认 `agate-workspace/`；输出 `AGATE_WORKSPACE` + `AGATE_TASKS_DIR`，bash（source 复用）与 python（ci-gate-backstop subprocess）共用，结构性保证本地 hook 与 CI 解析同路径。支持相对/绝对/含空格/项目外路径
- **roadmap 项目级任务管理循环**：新增 `assets/templates/roadmap-template.md` 单文件模板（对齐 active-tasks-template 模式），条目结构 `| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |`，状态标识 backlog/scheduled/in_progress/done/cancelled；循环规范（新需求→backlog、拆任务→scheduled、任务完成→回写 done）写入 WORKFLOW.md 正式规则
- **内容边界判据正式规则**（WORKFLOW.md）：文件是否由 agate 编排流程生成/消费 → 归工作区；描述产品/项目本身 → 留项目 docs/。二值判定、对偶自洽（验收记录→工作区 / 项目 README→项目 docs/）
- **`agate/UPGRADING.md`**：存量项目迁移指引（迁移工具步骤 + 旧布局说明 + 外部工作区限制）

### 变更（TAG0003 工作区架构）
- **orchestrator-template.md**：project.md 路径 `{project_root}/docs/agents/project.md` → `{AGATE_WORKSPACE}/agents/project.md`；active-tasks 路径 → `{AGATE_WORKSPACE}/tasks/active-tasks.md`；接入 mkdir 建 8 子目录（roadmap/tasks/agents/archived/reviews/decisions/plans/logs）；启动时旧布局检测 + 迁移指引
- **6 个既有脚本路径换血 + 2 处隐藏硬编码去硬编码**：
  - `pre-commit-gate.sh`：tasks_base 改调工作区解析器（AGATE_TASKS_DIR 默认值 + 根级 .state.yaml 的 TASK_DIR 推导跟随解析结果）
  - `ci-gate-backstop.py`：tasks_base 改调解析器，本地 hook 与 CI 同路径
  - `check-state-transition.sh`：任务级 .state.yaml 检测从 `grep 'docs/tasks/[^/]+/'` 改为 `dirname != REPO_ROOT` 语义（[SCOPE+] 隐藏硬编码，改法已验证：迁移后任务级文件若仍走 basename 分支会让状态转移检查静默失效）
  - `check-pruning.sh`：P7 源码文件数过滤排除模式跟随工作区路径（[SCOPE+] 隐藏硬编码，防任务文件误计入源码数）
  - `check-protocol-consistency.py`：`PATH_IGNORE_SUBSTRINGS` 白名单 `docs/tasks/` → 工作区运行时目录
  - `install-hook.sh`：gitignore 提示文字路径跟随工作区
  - 另 `agate-render-dispatch-prompt.sh`（P4-fix 修复）路径同步
- **16 文档 + 8 测试文件全量路径换血**：dispatch-protocol.md（28 处）/ state-machine.md / git-integration.md / role-system.md / WORKFLOW.md / SETUP.md / phase-cards / assets/templates / assets/execution-roles / loop-orchestration.md / rules/state-transitions.md 等；测试 fixture 中 `docs/tasks` 硬编码路径改为工作区路径（既有用例 603 条换血不改数）
- **新增测试**：`unit/agate-workspace-resolve.bats`（解析优先级/空格/外部路径）+ `unit/agate-migrate-workspace.bats`（迁移/幂等/空源/归档）；用例基线 625（P5 count 实测）

### 修复（本版本范围 [v0.40.2..HEAD] 内既有修复，随本版本一并发布）
- **check-p6-format.sh --fix POSIX locale 下全角冒号总结行静默失效**（8cc7cd3）
- **orchestrator permission 全 allow + consistency 排除平台目录**（40c5713）
- **.gitignore 移除 .state.yaml 忽略规则**（f773e30/8aa94fb）——迁移工具目录级 git mv 依赖文件物理移动而非跟踪状态
- **README 升级段链 UPGRADING.md + 新增 UPGRADING.md 升级指引**（892f266/cf2ddce）

### 文档（非协议变更，随版本发布）
- 项目侧：知识索引试点 / 主动架构演进机制设计 / 生命周期演进框架讨论稿 / agate 商业分析 / 质量评估 / roadmap P2.67-P2.71 讨论记录 / 独立评审（本项目开发资料，与协议本体变更分离）

---

**CHANGELOG 完整性对照（主 Agent 验证用）**：`git log v0.40.2..HEAD --oneline` 共 **27 commit**——TAG0003 P0-P7（8 commit，协议本体全部改动）+ .gitignore 修复（3）+ UPGRADING/README 链（2）+ orchestrator permission 修复（1）+ p6-format locale 修复（1）+ 项目文档/评审（12）。上述 CHANGELOG 建议按此分组，逐条有 commit 锚点。
````

> 注：上面是**内容建议**（供主 Agent 直接使用），插入位置为 CHANGELOG.md 当前 L10 `---` 之后、L11 `## [0.40.2]` 之前。日期 2026-08-12 与 release 实际执行日对齐（若跨日发布请主 Agent 改日期）。

## 3. 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务执行期间启动/创建的临时资源（供主 Agent P8 gate 通过后 READY 收尾检查清理）：

**临时服务/进程**：无（本任务为文档 + 脚本改动，未启动任何服务/daemon；`/tmp/opencode/debug-start-tpv0088.log` / `debug-start-tpv0090.log` 属其他项目（peekview）历史遗留，非本任务资源，READMEY 时可顺带确认状态，不属本清单清理范围）。

**临时数据 / fixture 仓库（`/tmp/opencode/`，2026-08-12 本任务时段，全部可删）**：
- P2 minimal_validation fixture：`p2-mv-validate/`、`p2-mv-validate2/`、`p2-mv-validate3/`、`p2-mv-validate4/`、`p2-env-validate/`、`p2-mv-spaces/`、`tap-test.bats`、`t.bats`
- P3/P4/P5/P6 迁移工具验证 fixture：`migtest/`、`migtest2/`、`migtest3/`、`demo-repo/`、`revcheck2/`（P4-review F1 成对 pathspec 实证）、`mwtest*/`、`mw9*/`、`mwdbg*/`、`mwempty-VEFV/`、`mwfinal-OA2L/`、`p6fix/`、`agate-migrate-fixed.bak`
- P4/P5/P6 输出留痕：`P4-dispatch-prompt-implementer.md`、`p5-bats-full.txt`（P5 全量 bats 原始输出）、`p6-bdd*.log`（P6 验收过程日志）

**开发安装**：无（未 pip install / editable install / 全局包安装）。

**任务目录内可清理项**：`docs/tasks/TAG0003-workspace-architecture/P8-progress.md`（本 subagent 落盘留痕，主 Agent 可在 P8 完成后删除）；`HANDOFF-TAG-TASKS.md`（worktree 根，任务交接文件，P8 后按主 Agent 判断归档或删除）。

**必须保留（非临时）**：`docs/tasks/TAG0003-workspace-architecture/P8-release.md`（本产出，正式交接物）、`P6-evidence/`（验收证据，已 commit）。

## 4. Lessons Learned（2-3 条，主 Agent 汇入 docs/notes/lessons.md）

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 架构 | **路径重构类任务的暗雷是"检测逻辑里的硬编码"，不是提示文字**：check-state-transition.sh 的 `grep 'docs/tasks/[^/]+/'` 是任务级 .state.yaml 检测的唯一入口，迁移后此 grep 永假 → 状态转移检查**静默失效**（T086 B1 教训同构）。同类还有 check-pruning.sh 的 P7 源码数过滤。P2 阶段用 minimal_validation 验证"移动路径后的兜底分支流向"（已验证 git mv 目录级 + dirname!=REPO_ROOT 改法），比靠人肉 grep 换血清单更可靠 | TAG0003 | 2026-08-12 |
| 流程 | **破坏性变更的版本号决策要有项目规范锚点，不套通用 semver**：WORKFLOW.md 明文「破坏性变更升 major（v2.0.0）」+ UPGRADING.md 先行写入 v2.0.0 迁移节 → 版本号是 v2.0.0 而非 v0.41.0。dispatch 给了备选（v0.41.0），靠既有文档惯例消除歧义，不是拍脑袋 | TAG0003 | 2026-08-12 |
| 测试 | **目录级 git mv 的边界行为（空源 exit 128 / 目标非空 exit 1 / 仓库外 exit 128）必须先验证再写工具**：P2 minimal_validation 实测后，迁移工具在 P4 一步到位（空源守卫 no-op、冲突检测、外部 fallback + WARNING 诚实标注「git 历史不可追溯」），避免了在用户侧踩坑 | TAG0003 | 2026-08-12 |

## 5. READY 收尾检查提示（供主 Agent P8 gate 通过后执行）

- **状态与版本**：.state.yaml phase → READY；active-tasks.md 任务行更新；git 工作区干净；`git tag v0.41.0` 已创建（tag 打在 feature 分支头，release PR 普通 merge --no-ff）
- **测试环境已清理**：无调试服务/进程需停止；按 §3 清理 `/tmp/opencode/` 本任务 fixture；无测试端口占用
- **开发环境已还原**：无开发安装需卸载；`~/.agate` 稳定版 v0.40.2 未被触碰（本任务全程隔离）
- **生产环境无残留**：`[PROD_NOT_TOUCHED]`（本任务全程未触发；若主 Agent 后续操作触发按规范补标记）
- **已知遗留**：`agate-retreat-to.bats` 仍含 `docs/tasks/T001` fixture 路径（P7 §五 残留观察，非阻塞，留痕）

## 6. 主 Agent 需亲自执行的发布动作（本 subagent 未做、也不允许做）

1. P5 gate 重跑确认全绿（bats 631/0 + consistency 0 ERROR + shellcheck 0 + count 625）
2. `git log v0.40.2..HEAD` 对照 CHANGELOG 建议无遗漏
3. 更新 `README.md` L6 badge：`v0.40.2` → `v0.41.0`
4. 按 §2 内容插入 CHANGELOG 新版本号节（bump-version + CHANGELOG 更新 → **同一 commit**，P8 card + v0.30.1 约定）
5. `git tag v0.41.0 && git push origin v0.41.0`
6. release PR 普通 merge（--no-ff），禁止 squash
7. 按 §3 临时资源清单执行 READY 清理，然后 .state.yaml phase=READY → DONE
