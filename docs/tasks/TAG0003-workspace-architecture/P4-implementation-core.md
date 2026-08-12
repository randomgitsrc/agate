---
phase: P4
task_id: TAG0003-workspace-architecture
type: implementation
parent: P2-design.md
trace_id: TAG0003-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0003 — 工作区架构：P4 核心脚本实现记录

> 角色：implementer（core 组，`~/.agate/assets/execution-roles/implementer.md`）。
> 范围：只改本角色文件集（6 个脚本：2 新增 + 4 改造），未改动任何协议文档或既有测试 fixture（那是并行 docs/tests 组的活）。

## 1. 改动清单

### 1.1 新增 `agate/scripts/agate-workspace-resolve.sh`（工作区路径单点解析器）

- 接口：`bash agate-workspace-resolve.sh [PROJECT_ROOT]`（PROJECT_ROOT 默认 `$PWD`）；输出两行 `AGATE_WORKSPACE=<绝对路径>` / `AGATE_TASKS_DIR=<绝对路径>`；被 source 时只 export 同名变量、不输出（`${BASH_SOURCE[0]} = "$0"` 分支区分执行/复用模式）。
- 解析优先级（P2 §3.1）：① 项目根 `.agate.env` 的 `AGATE_WORKSPACE=`（相对路径相对项目根解析 / 绝对路径原样 / 含空格，取最后一行）② 环境变量 `AGATE_TASKS_DIR`（二级向后兼容，tasks 基目录 = 该值，工作区根 = dirname）③ 默认 `{project_root}/agate-workspace`，tasks = 工作区根/tasks。
- 全程 `resolve_abs`（`realpath -m` 归一）+ 引号包裹（BDD-5 含空格路径）；解析器不创建任何目录（BDD-3/4，实测 WR.3 断言 `agate-workspace` 不生成）。
- 消费方：pre-commit-gate.sh（source）、ci-gate-backstop.py（subprocess）、agate-migrate-workspace.sh（source）。

### 1.2 新增 `agate/scripts/agate-migrate-workspace.sh`（强制迁移工具）

- 接口：`cd <project_root> && bash agate-migrate-workspace.sh [--to <workspace>]`；`--to` 覆盖工作区目标（相对/绝对）。
- 流程（P2 §3.2）：解析工作区目标（source 解析器）→ 源检测（docs/tasks 不存在/为空 → rmdir 清理，no-op exit 0，BDD-19）→ 目标冲突检测（工作区 tasks/archived 已存在且非空 → exit 1 防覆盖）→ `migrate_dir`（`mkdir -p` 父目录 + 目录级 `git mv`，实测 git mv 物理移动 gitignore 的 .state.yaml 与未追踪文件；git mv 失败 → fallback 普通 `mv` + 含 `WARNING` 的 git 历史限制标注，BDD-3/8）→ docs/archived 同语义迁移（相对结构保留，BDD-18）→ 无动作时 no-op（BDD-9 幂等）→ 迁移摘要输出（含「迁移」字样，BDD-10 不静默）。
- 仓库外 `--to` 目标实测：git mv 报 exit 128（`在仓库之外`），fallback mv 生效。

### 1.3 改造 `agate/scripts/pre-commit-gate.sh`（§3.1 消费方）

- L27 `AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"` → source 解析器取绝对路径（`source "$AGATE_ROOT/scripts/agate-workspace-resolve.sh" "$REPO_ROOT"`）；解析器缺失时（旧 AGATE_ROOT 兼容）`-f` 守卫退回原默认值。
- L83 根级 .state.yaml 的 `TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"` → `TASK_DIR="$AGATE_TASKS_DIR/$TASK_ID"`（解析器已输出绝对路径，不再拼 REPO_ROOT 前缀，P2-review 非阻塞项 2）；任务级分支不变（保持语义）。

### 1.4 改造 `agate/scripts/ci-gate-backstop.py`（§3.1 消费方）

- L86 `tasks_base = os.environ.get(...)` → 新增 `resolve_tasks_dir(project_root)`：subprocess 调 `agate-workspace-resolve.sh` 解析 `AGATE_TASKS_DIR=` 行，与 bash 侧共用同一解析逻辑（BDD-13 本地/CI 同路径）；解析器不存在/解析失败时回退 env/default（向后兼容）。`task_dir = str(Path(tasks_dir) / task_id)`。

### 1.5 改造 `agate/scripts/check-state-transition.sh`（§3.6 去硬编码，SCOPE+ #1）

- `get_old_phase()` 的 `grep -qE 'docs/tasks/[^/]+/'` → `dirname($STATE_FILE) != REPO_ROOT` 语义：`state_dir=$(realpath -m dirname STATE_FILE)`，`repo_root=$(git rev-parse --show-toplevel)`，不等 → 任务级 → `git_path=$(realpath --relative-to repo_root STATE_FILE)`（恒为仓库相对路径，覆盖 docs/tasks / agate-workspace/tasks / 自定义路径三种布局，ST_WS.1-4 验证）。根级 → 仍走 basename 分支（行为不变）。

### 1.6 改造 `agate/scripts/check-pruning.sh`（SCOPE+ #2）

- L66 排除模式 `^docs/tasks/` → 动态并入工作区 tasks 相对路径：`TASKS_BASE_REL=$(realpath --relative-to="$REPO_ROOT" "$(dirname "$TASK_DIR")")`（从运行时 TASK_DIR 反推 tasks 基目录，不硬编码路径），排除正则改为 `^docs/tasks/|^${TASKS_BASE_REL}/|...`（保留 `^docs/tasks/` 兼容旧布局，新布局匹配 `agate-workspace/tasks/`）。

## 2. 自查结果（自查≠gate，不声称 P5 已过）

- P3 目标测试命令 `bats --formatter tap agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/agate-migrate-workspace.bats agate/tests/unit/check-state-transition.bats`：**47/47 ok / 0 not ok**（WR.1-9 + MW.1-8 + ST.1-20 + ST_ARCHIVE.1-6 + ST_WS.1-4 全绿，红灯 19 已转绿）。
- `shellcheck -S warning` 5 个 .sh：0 error；`python3 -c "ast.parse(...)"` ci-gate-backstop.py：OK。
- 全量 unit 529 用例仅 1 红 = RP.13（`agate-render-dispatch-prompt` 残留占位符检查）——该断言渲染的是 `assets/templates/dispatch-prompt.md`，属并行 docs 组在改的文件集，非本角色文件集引入；regression 17/17 绿；integration 78/78 绿。
- 与 tests 并行组的协作点已实测打通：ci-gate-backstop.bats 换血后（fixture 用 agate-workspace/tasks），backstop 的 WARN/FAIL 判定符合预期（无 FAIL）。

## 3. 偏差与缺口声明

[DESIGN_GAP: P2 §3.2 未指定迁移后是否 commit。P3 MW.3 断言 git log --follow 在新路径可追溯旧 commit，但实测 git mv 只暂存 rename（index），未 commit 时 git log --follow 在新路径查不到任何 commit（历史为空）——故实现采用迁移完成后若有暂存变更则自动 `git commit -qm "chore(workspace): migrate legacy docs/tasks layout to workspace"`。此 commit 是全量 index commit，若用户迁移前有其他已暂存改动会被一并提交（风险已在工具输出注释标注，文档侧 UPGRADING.md 应提示迁移前保持暂存区干净）]
[DESIGN_GAP_REVIEWED: 已确认——P3 MW.3 断言 git log --follow 在新路径可追溯旧 commit，git mv 只暂存 rename 未 commit 时历史为空，自动 commit 是满足 BDD-8 的必要行为。风险（全量 index commit 会带入迁移前已暂存改动）已由工具输出注释 + UPGRADING.md 提示缓解，接受该实现决策。主 Agent 2026-08-12]

[SCOPE_GAP: P2-design.md §1.1 声明 `check-protocol-consistency.py`（PATH_IGNORE_SUBSTRINGS 重校准，L72）与 `install-hook.sh`（L87 提示文字路径）两个脚本改动，但本任务三个并行 implementer 的 dispatch-context 文件集（core=6 脚本 / docs=16 文档 / tests=8 测试文件）均未覆盖这两个脚本——需主 Agent 确认归属（建议归 docs 组或 P7 前回补），否则 P5_consistency gate（check-protocol-consistency.py 0 ERROR）在 BDD-20 验收时会因白名单未重校准而误报]

## 4. 实现对照（P2 方案 A）

| P2 要求 | 实现落点 |
|---|---|
| §3.1 解析器三分支 + 绝对路径输出 + source/python 双复用 | 1.1 ✓ |
| §3.2 迁移工具 8 步流程 | 1.2 ✓ |
| pre-commit L27/L83 改解析器 | 1.3 ✓ |
| ci L86 改 subprocess 共用解析 | 1.4 ✓ |
| §3.6 check-state-transition 去硬编码 | 1.5 ✓ |
| check-pruning L66 跟随工作区路径 | 1.6 ✓ |

## 5. 未触碰范围

- 协议文档 / orchestrator-template / roadmap 机制 / 内容边界判据（docs 组）；
- 8 个既有 .bats fixture 换血 + fixtures.bash（tests 组）；
- `check-protocol-consistency.py` / `install-hook.sh` / `gate-result.sh`（见 [SCOPE_GAP]）；
- `~/.agate`（稳定版 v0.40.2，未动）。

## 6. 环境状态标记

[PROD_NOT_TOUCHED] 本次实现仅改动 worktree `agate/` 下 6 个脚本与任务文档，未接触任何生产环境/生产数据/生产 API；`~/.agate` 稳定版未动。
