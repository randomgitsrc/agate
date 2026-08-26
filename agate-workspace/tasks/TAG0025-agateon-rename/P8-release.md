---
phase: P8
task_id: TAG0025-agateon-rename
type: release
parent: P2-design.md
trace_id: TAG0025-P8-20260826
status: draft
created: 2026-08-26
agent: implementer
packages:
- agate-brand-docs
- agate-installer-scripts
- agate-repo-admin
bump_type: minor
debt_check: none
---

# P8 发布准备 — TAG0025 Agateon 品牌改名执行 Phase 0-1：v0.63.0 → v0.64.0

> releaser（implementer P8 模式）产出。**不执行 git commit / tag / bump-version**——三项由主 Agent 在
> gate 验证通过后亲自执行。本文件为只读检查产出，未修改除本文件外的任何文件。
> [PROD_NOT_TOUCHED]：本次检查全部为文件 grep / git log / git show / git status 等只读命令，
> 未接触主 checkout（`/home/kity/oclab/agate`）、`~/.agate`，不涉及生产环境。

## 1. 版本信息

- **当前版本**：v0.63.0（README.md badge / CHANGELOG `[0.63.0]` 段 / git tag `v0.63.0`，TAG0024 发布）
- **目标版本**：**v0.64.0**
- `bump_type: minor`（用户已确认："与历史惯例一致"——本仓库每个任务完成都 bump minor）
- **单一版本方案说明**：P2-design.md frontmatter 声明 `packages: [agate-brand-docs,
  agate-installer-scripts, agate-repo-admin]` 是本任务内部改动范围的分类标签（品牌文档/安装脚本/
  仓库运维三类），不是三个独立可发布单元——本仓库只有一套版本号（README badge + CHANGELOG 版本头 +
  git tag），逐一确认过 P2 `gate_commands` 全部是全仓命令（`P5_unit`/`P5_other`/`P5_consistency`/
  `P5_count_tests`/`P5_bdd1~16`），没有任何 per-package 独立发布检查命令，符合派发指引判断。

## 2. 发布检查动作确认（检查内容①）

- `.state.yaml` 已确认：`judge.enabled: true`，`judge.rounds: 2`，
  **`judge.last_verdict: passed`**，`judge.partial: false`——P6.5 独立复核已通过。
- 无独立于全量测试套件之外的 per-package 发布检查命令（非 npm 项目）。
- **git 工作区状态核实（非完全"干净"，逐项说明如下）**：

  | 文件/目录 | git status | 判定 |
  |---|---|---|
  | `agate-workspace/roadmap/roadmap.md` | `M`（modified） | 预期——RM-AG0035 剩余工作②回写，dispatch-context 明示已由主 Agent 亲自完成 |
  | `agate-workspace/tasks/TAG0025-agateon-rename/gate-events.jsonl` | `M`（modified） | 预期——本任务自身 append-only 事件账本随各 phase 追加 |
  | `agate-workspace/tasks/TAG0025-agateon-rename/P8-dispatch-context-implementer.md` | `??`（untracked） | 预期——本 P8 阶段派发指引文件 |
  | `agate-workspace/tasks/TAG0025-agateon-rename/P8-progress.md` | `??`（untracked） | 预期——本 releaser 分阶段落盘产出 |
  | `.pytest-tmp/`（仓库根） | `??`（untracked，约 60+ 个子目录） | **非预期，需主 Agent 关注**（见下） |

  **`.pytest-tmp/` 说明**：本仓库因运行环境 `/tmp` 只读，pytest 需要可写临时目录，项目约定用
  `--basetemp` 指向仓库根下的可写目录（`agate/assets/templates/dsh/SKILL.md` L67 有明文说明；
  `agate/tests/ENV-SENSITIVE-TESTS.md` 记录了 basetemp 位置依赖类问题及其根治历史，
  `check-gate.py` 的相关测试用例也显式排除 basetemp 子树扫描）——**这是本仓库已知的环境适配模式，
  不是本任务引入的新问题**。但该目录内容（时间戳集中在 2026-08-26 00:51-00:52，落在本任务
  P4-P7 阶段执行窗口内）**未被 `.gitignore` 收录**（`.gitignore` 只声明了 `.pytest_cache/`，没有
  `.pytest-tmp/`），是本任务测试执行过程中产生、目前仍残留在工作区的临时数据，属于遗留清理项，
  已归入 §4 临时资源清单，建议主 Agent READY 收尾阶段清理（`rm -rf .pytest-tmp`）。
  除此之外未发现任何超出预期的暂存/未暂存改动。

## 3. CHANGELOG `[Unreleased]` 现状确认（检查内容②）

原样摘录当前 `## [Unreleased]` 段内容（`CHANGELOG.md` L11-21，位于 `## [0.63.0] - 2026-08-25` 段之上）：

```markdown
## [Unreleased]

### 变更（TAG0025：Agateon 品牌改名执行 Phase 0-1，RM-AG0035 剩余工作②）

- **品牌声明上线**：README.md / README.zh-CN.md 首屏新增 "Agateon (formerly agate)" 品牌声明，
  标志本项目正在从 `agate` 更名为 `Agateon`。
- **硬编码仓库 URL 同批更新**：`install.sh`、`agate/scripts/agate-install.py`、
  `agate/scripts/agate-changes.py`、README.md/README.zh-CN.md 的 badge 与安装入口，共 7 处
  硬编码仓库路径已同批更新为 `randomgitsrc/agateon`。
- 三层解耦原则：仅改外部品牌层（仓库名/品牌声明），内部命名空间（`agate/` 目录、
  `agate-workspace/`、`~/.agate`、`AGATE_*`、`agate-*.py` 文件名、`agate_common`）不变。
```

主 Agent 执行 `[Unreleased]` → `[0.64.0] - 2026-08-26` 改名时，以上 3 条要点应原样保留（见 §7
的重要发现——本次改名不应只搬运这 3 条）。

## 4. 版本文件现状确认（检查内容③）

| 文件 | 当前 badge 版本 | 说明 |
|---|---|---|
| `README.md` L5 | `version-v0.63.0` | 与 CHANGELOG/tag 一致 |
| `README.zh-CN.md` L5 | `version-v0.62.0` | **TAG0025 之前就存在的历史遗留不一致**（按 dispatch-context 指示不深究成因）——本次统一 bump 到 v0.64.0 后两者自然对齐 |

## 5. UPGRADING.md §3 章节格式参考（检查内容④）

最新一条 `### v0.63.0`（`agate/UPGRADING.md` L92-112）摘录作为模板：

```markdown
### v0.63.0 — 工具链批（TAG0024：agate-md-field-set / roadmap-done 健壮性）

> **本版本无破坏性变更，零迁移动作**。新增 CLI 工具随 `git pull` 自动可用，无需任何重装步骤
> （本版本未改 3 个 hook 薄壳与任何字段格式）。

**① 新增工具（无安装步骤）**：...
**② gate 行为收紧（合法数据无影响）**：...
**③ 其余（无升级动作）**：...

**通用升级动作**：`git pull` 即完成（软链布局）；通用步骤的 `install-hook.py` 重跑对本版本无必要
（无 hook 变更），跑了也无害。
```

**"无破坏性变更"判断核实**：读 `P4-implementation.md` 改动清单确认，本任务批次 1 为 6 个文件
（`install.sh`/`agate/scripts/agate-install.py`/`agate/scripts/agate-changes.py`/`README.md`/
`README.zh-CN.md`/`CHANGELOG.md`）纯文本 URL/品牌声明替换，未新增/删除文件；批次 2 为 remote
迁移（`git remote set-url` 主 checkout 单点执行，worktree 通过 `.git/config` 共享机制跟随），
未改任何 CLI 命令行为、字段格式或 hook 逻辑；另 P3 阶段新增 1 个回归测试文件
`agate/tests/regression/test_repo_url_no_stale_rename.py`（纯测试代码，不影响运行时行为）。
**判定：本任务性质是品牌层文本变更，"无破坏性变更"判断成立。**

> **但见 §7——本次 v0.64.0 版本区间还包含 13 个非 TAG0025 commit，其中至少 2 个（CHECK 13
> 新增一致性检查、CI fetch-tags 修复）涉及协议/CI 行为变化，UPGRADING §3 v0.64.0 章节撰写时
> 不能只依据 TAG0025 本身判断"无破坏性变更"，需要主 Agent 一并核实这批 commit 的性质。**

## 6. debt_check: none（检查内容⑤）

已读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（803 行，DEBT0001 起全文档）：
`grep -ni "agateon|品牌|改名|TAG0025|rename"` 全文匹配，仅 1 处命中（DEBT0001 的 impact
描述中提到"改名"，但该条目是 TAG0013 时代关于"脚本删/改名后协议文档漂移无 gate 兜底"的历史
条目，`status: closed`，与本任务无关）。**本任务范围内未发现需要关闭的既有条目，也未发现需要
新登记的技术债** → `debt_check: none`。

## 7. `git log v0.63.0..HEAD --oneline` 对照 CHANGELOG 核实（检查内容⑦，重要发现）

跑 `git log v0.63.0..HEAD --oneline --no-merges`，共 **27 个非 merge commit**：

- **13 个 `wf(TAG0025-*)` 前缀 commit**（P0~P7 各阶段产出记录）——内容与 CHANGELOG
  `[Unreleased]` 当前 3 条要点主题吻合，量级一致。
- **14 个非 TAG0025 commit**（逐一 `git show --stat` 核实，均**未 touch `CHANGELOG.md`**，
  当前 CHANGELOG 全文档也未见对应内容）：

  | commit | 摘要 | 是否触及 CHANGELOG.md |
  |---|---|---|
  | `d47b2db` | feat(consistency): CHECK 13 CHANGELOG↔UPGRADING 章节对应性检查（RM-AG0052） | 否 |
  | `f561a59` | docs(release): UPGRADING.md 补 v0.63.0 章节 | 否 |
  | `81ac819` | docs(TAG0024): 合并后复盘归档 + DEBT0022 登记 | 否 |
  | `bb82dd3` | docs: 关闭 Agateon 改名最后开放问题——GitHub org agateon 已占名 | 否 |
  | `9ae7942` | docs(TAG0024): active-tasks.md 回写 READY 状态 | 否 |
  | `97db170` | docs(design): design-rename-execution 状态行更新 | 否 |
  | `9dece79` | ci: docs-only PR 无法合并的根治修复 | 否 |
  | `3eaa2ae` | docs(design): Agateon 改名执行设计 + roadmap RM-AG0035 回写对齐 | 否 |
  | `ef20169` | docs(roadmap): RM-AG0051 标记 done（CHECK 7 hotfix） | 否 |
  | `6147241` | fix(ci): consistency job 全量 fetch tags，恢复 CHECK 7 版本漂移判定 | 否 |
  | `4d6b444` | fix(AGENTS): 恢复 Gate 脚本分层节标题 + 依赖节 | 否 |
  | `d29513b` | docs: 补 UPGRADING v0.62.0 章节 + roadmap 登记 RM-AG0051/0052 | 否 |
  | `f31f125` | docs: 重构 AGENTS.md | 否 |
  | `8f02efe` | chore(archive): 归档 HANDOFF-TAG0023 交接单 | 否 |

  这批 commit 的作者时间戳跨度为 2026-08-25 17:44 ~ 2026-08-26 00:43，部分早于 v0.63.0 tag
  commit（`a0a2d14`，2026-08-25 23:49:09）——是并行分支在 tag 切出后才合并进主线导致（git log
  按可达性而非作者时间排序），部分确实晚于 tag（如 `d47b2db` CHECK 13、`bb82dd3` org 占名关闭、
  `81ac819` TAG0024 复盘归档、`f561a59` UPGRADING 补写）。无论合并时序如何，这 14 个 commit 都
  在 `v0.63.0..HEAD` 区间内、都会被打入 v0.64.0 这次发布，但**没有任何一条在 CHANGELOG 中留痕**。

  **结论：CHANGELOG `[Unreleased]` 当前 3 条要点只覆盖了 13 个 TAG0025 commit，未覆盖同一
  发布区间内的另外 14 个非 TAG0025 commit——不是"逐字对应"层面的细节遗漏，是整批内容缺口**
  （其中 `d47b2db` 新增了一个新的一致性检查项 CHECK 13、`6147241` 修复了 CI 侧 CHECK 7 长期失效
  的问题，两者都是有实质工程内容、理应被发布说明记录的变更）。这个发现超出了"确认 TAG0025 自身
  3 条要点是否遗漏"的字面范围，但属于本检查项的应有覆盖面，如实报告供主 Agent 判断处理方式
  （例如在 `[0.64.0]` 段为这批 commit 补一组独立的变更条目，或确认它们是否已通过其他机制被
  记录）。

## 8. 临时资源清单（检查内容⑥，供主 Agent READY 收尾检查清理）

| # | 资源 | 状态 | 清理动作/确认项 |
|---|---|---|---|
| 1 | 临时服务/进程 | 本任务全程验证动作均为文件 grep / git log / git show / git status / curl 等只读命令，**未启动任何后台服务/daemon/debug server** | 无需清理；如需确认可跑 `ps aux \| grep -E 'agate\|pytest'` |
| 2 | `.pytest-tmp/`（仓库根，约 60+ 子目录） | **未清理，仍残留**（见 §2 说明，本任务 P4-P7 阶段全量 pytest 运行产生，因环境 `/tmp` 只读约定用 `--basetemp` 指向仓库内可写目录） | 建议 `rm -rf .pytest-tmp`；该目录未被 `.gitignore` 收录，属遗留清理项（非本任务代码逻辑问题） |
| 3 | 测试端口 | 未发现任何端口绑定痕迹 | 无端口占用 |
| 4 | 开发安装 | 未执行任何 pip 安装/editable install/全局包安装 | 无需卸载 |
| 5 | remote 迁移（批次 2） | 主 checkout `/home/kity/oclab/agate` 已执行 `git remote set-url` 指向 `randomgitsrc/agateon`（P4 批次 2 记录，用户当次会话已放行确认，属正式发布动作非临时资源） | 非清理项，仅记录留痕 |

## 9. releaser 边界声明

- 本文件未执行：bump-version（README/README.zh-CN badge 未改）、CHANGELOG 未写入新版本段、
  UPGRADING.md 未新增 `### v0.64.0` 章节、git commit/tag 未创建——全部由主 Agent 在 P8 gate
  验证通过后亲自执行。
- 除本文件外未修改任何文件；`.pytest-tmp/` 为发现并如实记录的既存残留，未做任何清理动作
  （P8 releaser 模式为只读检查）。
- 分阶段落盘记录见同目录 `P8-progress.md`。
