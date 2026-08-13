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
bash --version && python3 --version && bats --version && \
python3 -c "import yaml; print('pyyaml OK')" && command -v shellcheck
```

缺什么补什么（bash/python/pyyaml/bats/shellcheck）。

### Step 3：基线验证（Step 4 of skill——确保干净起点）

```bash
cd .worktrees/agate-{Txxx}
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py --strict
```

全绿 + 0 ERROR 才算干净基线。失败则停下来（可能主 checkout 有未合并改动）。

### Step 4：确认 hook 就位（共享 git 目录）

worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 在共享目录：

```bash
ls -la /home/kity/oclab/agate/.git/hooks/ | grep -E 'pre-commit|commit-msg|pre-push' | grep -v sample
```

预期：三个 hook 软链指向 `~/.agate/scripts/`。这是有意的——commit hook 用稳定版判定，避免"用未验证的新 gate 判自己"。

### Step 5：注册 orchestrator（SETUP）

```bash
mkdir -p .opencode/agents
ln -sf ~/.agate/orchestrator-template.md .opencode/agents/orchestrator.md
```

`.opencode/` 已被 gitignore（本地环境配置不入库）。

### Step 6：验证工作区解析

```bash
bash agate/scripts/agate-workspace-resolve.sh
# 预期输出 worktree 自己的 agate-workspace/（不是主 checkout 的）
```

### Step 7：确认任务数据就位

```bash
ls agate-workspace/tasks/{Txxx}-{slug}/
grep -E 'task_id|phase' agate-workspace/tasks/{Txxx}-{slug}/.state.yaml
```

预期：P0-brief.md + .state.yaml phase=P0。

### Step 8：写交接单

复制 `agate/assets/templates/handoff-template.md` → worktree 根 `HANDOFF-{Txxx}.md`，填：
- 任务编号/标题/一句话（从 P0-brief 取）
- worktree 路径（实际路径）
- 缺陷/需求清单（从 P0-brief known_risks + 审计/复盘取）
- 核心约束（Linux 基线 / Windows 增量 / 范围锁定）
- 验证命令（模板已有，改测试文件名）
- 风险（从 P0-brief known_risks 取）

### Step 9：交接单 commit

```bash
git add HANDOFF-{Txxx}.md && git commit -m "docs: {Txxx} 交接单"
```

### Step 10：最终确认 + 切换

```bash
git worktree list   # 确认 worktree 就位
git log --oneline -3   # 确认交接单已提交
```

然后切到 worktree 目录，新开 session，让 agent 读 `HANDOFF-{Txxx}.md` 启动 P1。

## 关键纪律（违反必出事故）

| 纪律 | 说明 |
|------|------|
| 主 checkout 禁止改动 | 它是稳定版来源 + hook 的 AGATE_ROOT |
| `~/.agate` 禁止改动 | 稳定版（当前发布 tag），跑 gate / 读卡片用它 |
| gate 工具 ≠ 检查对象 | commit hook 用 `~/.agate` 判定；但 `check-protocol-consistency.py` 必须用 worktree 自己的（检查 worktree 里的文件） |
| `~/.agate` 脚本显示主 checkout 上下文 | `agate-summary.sh` 在 worktree 跑显示稳定版 main/HEAD，不代表 worktree 状态 |
| 工具稳定优先 | hook 指向稳定版，不指向 worktree（避免"用未验证的新 gate 判自己"）——用户已确认此哲学 |
| commit 时 phase = 本 commit 产出阶段 | 防 pre-commit 用下一阶段 gate 拦截 |

## 完成后清理

```bash
# 任务合并 main 后
git worktree remove .worktrees/agate-{Txxx}
git branch -D feat/{Txxx}-{slug}
```

## 与 AGENTS.md 的关系

AGENTS.md「v2.0 改造期间执行约定」已有双工作区纪律的零散条目（117-129 行）。本指南是把"构建"流程固化。纪律部分两者一致；若冲突以 AGENTS.md 为准。
