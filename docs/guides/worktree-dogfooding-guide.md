# 构建 worktree session + setup + 交接单（dogfooding 标准流程）

> 适用：agate 自身改造任务（dogfooding）需要隔离 worktree 时。
> 每次新任务（TAG0005+）按此流程快速构建，避免临时发挥。
> 配套：交接单模板 `agate/assets/templates/handoff-template.md`。

---

## 为什么需要这套流程

agate 自身改造 = 用 agate 改造 agate（dogfooding）。涉及双工作区（稳定版 `~/.agate` vs 改造对象 worktree）、共享 hook、基线验证、交接单。步骤多且易错（T001/TAG0004 两次都踩过），固化后可 10 分钟内完成。

## 前置条件

- 主 checkout（`/home/kity/oclab/agate`）在 main 且干净
- `~/.agate` 软链指向主 checkout/agate（稳定版）
- 任务已 P0 立项（P0-brief + .state.yaml 在 agate-workspace/tasks/）

## 流程（10 步）

### Step 0：检测现有隔离（using-git-worktrees skill）

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
[ "$GIT_DIR" = "$GIT_COMMON" ] && echo "普通 checkout" || echo "已在 worktree"
```

主 checkout 是普通 checkout（GIT_DIR=GIT_COMMON），`.worktrees/` 已 gitignore（T001 时期验证过）。

### Step 1：创建 worktree

```bash
git worktree add .worktrees/agate-{Txxx} -b feat/{Txxx}-{slug}
```

- 分支名：`feat/TAG0004-env-adaptation` 风格
- 位置：`.worktrees/agate-{Txxx}`（仓库根下，已 gitignore）

### Step 2：依赖检查（worktree 内）

```bash
bash --version && python3 --version && python3 -m pytest --version && \
python3 -c "import yaml; print('pyyaml OK')" && command -v shellcheck && command -v ruff
```

缺什么补什么（bash/python/pyyaml/pytest/shellcheck/ruff）。

**⚠️ 解释器注意**：请用**系统 python（`/usr/bin/python3`）**跑 pytest/pyyaml——pytest 以模块形式装在系统 python，**裸 `pytest` 命令在 PATH 里通常找不到**（会误报"缺 pytest"）。`~/.venvs/agate-dev` 是开发 agate 本体的 venv，只装了 python + ruff、**没装 pytest**，不要 source 它跑测试。CI 用 `python3 -m pytest`（`protocol-tests.yml`），本机也应统一 `python3 -m pytest`。ruff 用 `~/.venvs/agate-dev/bin/ruff`（开发 agate 才需要，仅跑测试用不到，但本任务要改脚本所以需检查）。

### Step 3：基线验证（Step 4 of skill——确保干净起点）

```bash
cd .worktrees/agate-{Txxx}
python3 -m pytest agate/tests/
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
```

全绿 + 0 ERROR 才算干净基线。失败则停下来（可能主 checkout 有未合并改动）。

> ⚠️ **用 `--strict-errors-only` 而非 `--strict`（DEBT0012 教训）**：仓库存量有 300+ 条历史叙事文件死链 WARNING，`--strict` 会让"仅有 WARNING、无 ERROR"也 exit 2，把干净基线误判为"主 checkout 有未合并改动"。`--strict-errors-only` 仅在 ERROR 时非 0（TAG0017 起官方默认语义，见 `agate/scripts/README.md`）。pytest 全量大可分 unit/regression/integration 三片跑（`tests/README.md`），每片外层加 `timeout 90`，gate/consistency 单跑并加 timeout。

### Step 4：确认 hook 就位（共享 git 目录）

worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 在共享目录：

```bash
ls -la /home/kity/oclab/agate/.git/hooks/ | grep -E 'pre-commit|commit-msg|pre-push' | grep -v sample
```

预期：三个 hook 软链指向 `~/.agate/scripts/`。这是有意的——commit hook 用稳定版判定，避免"用未验证的新 gate 判自己"。

### Step 5：注册 orchestrator（SETUP）

```bash
# OpenCode + Claude Code 双平台都注册（TAG0016/17 实际都双平台）
mkdir -p .opencode/agents
ln -sf ~/.agate/orchestrator-template.md .opencode/agents/orchestrator.md
mkdir -p .claude/agents
ln -sf ~/.agate/orchestrator-template.md .claude/agents/orchestrator.md
```

`.opencode/` 与 `.claude/` 均已 gitignore（本地环境配置不入库），对应 setup 步骤见 `SETUP.md`（OpenCode 与 Claude Code 各一节）。

### Step 6：验证工作区解析

```bash
python3 agate/scripts/agate_common.py
# 预期输出 AGATE_WORKSPACE=/AGATE_TASKS_DIR= 指向 worktree 自己的 agate-workspace/（不是主 checkout 的）
```

### Step 7：确认任务数据就位

```bash
ls agate-workspace/tasks/{Txxx}-{slug}/
grep -E 'task_id|phase' agate-workspace/tasks/{Txxx}-{slug}/.state.yaml
```

预期：P0-brief.md + .state.yaml phase=P0。

### Step 8：写交接单

复制 `agate/assets/templates/handoff-template.md` → worktree 根 `HANDOFF-{Txxx}.md`，**按模板全部 9 个小节填写**（不要只填部分字段）：
- §1 你要做什么（任务编号/标题/一句话，从 P0-brief 取）
- §2 工作区布局（worktree/主 checkout/`~/.agate` 双工作区表 + 核心原则）
- §3 任务范围（缺陷/需求清单从 P0-brief known_risks + 审计/复盘取 + 核心约束）
- §4 关键验证命令（模板已有，改测试文件名 + 解释器）
- §5 阶段推进纪律（commit phase、TDD、SELF-GATE 触发、`wf({Txxx}-P{N})` 前缀——T001 血泪教训级硬约束，**必填**）
- §6 任务编号与状态
- §7 已知风险与止损
- §8 完成后（PR 普通 merge 非 squash、CI 检查、roadmap 回写）
- §9 交接确认

> ⚠️ §5 的 commit-phase 纪律与 §8 的 PR merge 规则都是硬约束，只填到 §3 会让后续 agent 漏掉关键纪律。

### Step 9：交接单 commit

```bash
git add HANDOFF-{Txxx}.md && git commit -m "docs: {Txxx} 交接单"
```

### Step 10：最终确认 + 切换

```bash
git worktree list   # 确认 worktree 就位
git log --oneline -3   # 确认交接单已提交
```

然后切到 worktree 目录，新开 session。

**⚠️ 启动入口（HANDOFF 读取盲点）**：orchestrator 的默认启动流程读的是 `{AGATE_WORKSPACE}/tasks/active-tasks.md` + `.state.yaml`（orchestrator-template.md），**并不会自动读 HANDOFF**。所以必须在新 session 的首条指令里显式写"**读 worktree 根 `HANDOFF-{Txxx}.md`**"（认准当前任务号——仓库根会积累历史 `HANDOFF-TAG0xxx.md`，别读错；且本任务分支未合并前，其 HANDOFF 只存在于本 worktree、不在 main）。若 agent 没读 HANDOFF，它仍能按默认流程从 active-tasks.md + P0-brief 启动（handoff 是"快捷入口"而非"必需"），但缺陷清单/核心约束/阶段纪律会缺失。

## 关键纪律（违反必出事故）

| 纪律 | 说明 |
|------|------|
| 主 checkout 禁止改动 | 它是稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate` 禁止改动 | 稳定版（当前发布 tag），跑 gate / 读卡片用它 |
| gate 工具 ≠ 检查对象 | commit hook 用 `~/.agate` 判定；但 `check-protocol-consistency.py` 必须用 worktree 自己的（检查 worktree 里的文件） |
| `~/.agate` 脚本显示主 checkout 上下文 | `agate-summary.py` 在 worktree 跑显示稳定版 main/HEAD，不代表 worktree 状态 |
| 工具稳定优先 | hook 指向稳定版，不指向 worktree（避免"用未验证的新 gate 判自己"）——用户已确认此哲学 |
| commit 时 phase = 本 commit 产出阶段 | 防 pre-commit 用下一阶段 gate 拦截 |

## 完成后清理

```bash
# 任务合并 main 后
# worktree 有未追踪残留（P5 日志等）时 remove 会拒删——确认已合并 main 后加 --force
git worktree remove .worktrees/agate-{Txxx} --force
git branch -D feat/{Txxx}-{slug}
# 若 PR 未自动删远端分支：
# git push origin --delete feat/{Txxx}-{slug}
```

## 与 AGENTS.md 的关系

AGENTS.md「v2.0 改造期间执行约定」已有双工作区纪律的零散条目（117-129 行）。本指南是把"构建"流程固化。纪律部分两者一致；若冲突以 AGENTS.md 为准。
