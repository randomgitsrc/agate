# TAG0025 会话间环境交接单 — 仓库改名的会话/环境连续性

> 用途：跨 DSH 会话/跨任务阶段的环境事实交接。任何会话在执行或恢复 TAG0025（含 P4 改名动作
> 前后）时先读本文件，避免误判"改名会影响什么"。
> 权威源：`docs/design-notes/design-rename-execution.md` §1（三层解耦）+ 本交接单。

---

## 一、核心事实（一句话）

**GitHub 仓库改名（`randomgitsrc/agate` → `randomgitsrc/agateon`）与本地目录完全解耦：
本地目录 `/home/kity/oclab/agate` 不改名，`~/.agate` 软链不动，DSH 会话配置零更新。**

改名只发生在 GitHub 侧（仓库名/品牌层）；本地文件系统的 `agate` 路径属于内部命名空间，
按设计永久保留（或 v1.0 窗口重评估，非本任务）。

## 二、改名前后环境对照表

| 环境要素 | 改名前 | 改名后 | 需要动作？ |
|----------|--------|--------|-----------|
| 本地目录 `/home/kity/oclab/agate` | 主 checkout | **不变** | 否 |
| worktree `.worktrees/agate-TAG0025` | 分支 `feat/TAG0025-agateon-rename` | **不变**（目录/分支名与 GitHub 仓名无关）| 否 |
| `~/.agate` 软链 | → 主 checkout/agate | **不变** | 否 |
| DSH 会话工作区 | `/home/kity/oclab/agate` | **不变**（会话配置引用本地路径，与 GitHub 仓名无关）| 否 |
| git remote `origin` URL | `https://github.com/randomgitsrc/agate.git` | 需改 `.../agateon.git` | **是（任务内执行）**：`git remote set-url origin <新URL>` 在**主 checkout 设一次即可**——已实测验证（2026-08-26）worktree 与主仓共享同一 `.git/config`（worktree 的 `git config --show-origin` 指向主仓文件），全部 worktree 自动跟随；设完后各 worktree 跑一次 `git fetch` 实测 |
| `/home/kity/bin/git-to-pr` / `git-to-main` | 绝对路径引用 `/home/kity/oclab/agate` | **不变**（引用本地路径非远程名）| 否 |
| hooks（主 checkout `.git/hooks/`）| 软链 → `~/.agate/scripts/` | **不变** | 否 |
| GitHub 旧 URL | 直达 | 301 → 新仓（git 协议/网页均兜底）| 否（但任务内主动迁移，不依赖 301）|
| PR / issue / tag / CI | 旧仓名下 | 全部保留至新仓名 | 否 |
| README badge / install.sh 等硬编码 | 旧仓名 | 新仓名 | **是（与改名同批提交，任务交付物）** |

## 三、DSH 会话连续性（为什么零更新）

1. DSH 会话锚定的是**本地路径** `/home/kity/oclab/agate`（会话工作区），不是 GitHub 仓名
2. 本会话内的后台任务/目标/工具配置均引用本地路径
3. `gh` CLI 按 remote URL 解析仓库——remote 迁移后 `gh pr list` 等命令自动指向新仓，无需配置
4. 会话内已加载的 AGENTS.md 指令来自本地文件，不受影响

**会话恢复指引**：改名后任何新会话/恢复会话，只需按常规读
`{AGATE_WORKSPACE}/tasks/active-tasks.md` + `HANDOFF-TAG0025.md` + 本文件，无额外环境配置。

## 四、P4 改名执行窗口（唯一需要小心的时段）

改名动作本身（`gh api -X PATCH repos/randomgitsrc/agate -f name=agateon`）前后 1 分钟内：
- **不要**有并行会话在 push/开 PR（301 生效有秒级窗口，并发操作可能撞旧名解析）
- 执行后立即验证（4 条验收锚，见 HANDOFF-TAG0025 §4）：
  1. `curl -sI https://github.com/randomgitsrc/agate` → 301
  2. `git ls-remote https://github.com/randomgitsrc/agateon.git HEAD` → 正常
  3. 全仓 grep 无 `randomgitsrc/agate\b` 残留（排除 archived/ 豁免层）
  4. GitHub 搜索 `in:name agateon` 首屏命中
- 验证通过后本文件 §二 表格打勾归档（更新"改名后"列的实测时间戳）

## 五、未来场景：若决定连本地目录也改名（**不是本任务，另立任务**）

> 触发条件：v1.0 窗口重评估用户面命名时（设计 §8.2）用户决定本地目录跟改。
> 届时是**高风险环境手术**，必须逐项执行以下清单（漏一项即断链）：

1. `git worktree repair`——所有 worktree 的 `.git` 文件与主仓 `worktrees/` 元数据双向引用
   绝对路径，目录改名后**必须先修**（`git worktree list` 验证）
2. 重建 `~/.agate` 软链 → 新路径/agate（`ln -sfn`）；hook 软链指向 `~/.agate` 无需动
3. 重装/验证三个 hook：`python3 ~/.agate/scripts/install-hook.py`（主仓 `.git/hooks/`）
4. DSH 会话：工作区路径配置更新为新目录（**需新开/迁移会话**，旧会话工作区失效）
5. `/home/kity/bin/git-to-pr` / `git-to-main`：脚本内绝对路径更新
6. `~/.venvs/agate-dev`：venv 内 shebang/pyvenv.cfg 绝对路径——重建比迁移干净
7. 全量回归：`python3 -m pytest agate/tests/` + consistency + `agate-summary.py` 解析验证
8. shell rc / 编辑器工作区配置 / 任何引用旧绝对路径的自动化（grep `/oclab/agate` 全 home 扫描）

**止损**：上述任一步失败 → 目录名改回（`mv` 可逆），逐项排查；软链断链的表象是
`~/.agate/scripts/` 命令全部 No such file，第一反应查软链。

## 六、版本记录

| 日期 | 事件 | 会话 |
|------|------|------|
| 2026-08-26 | 交接单建立（P0，改名未执行）| TAG0025 主会话 |
| （待填）| P4 改名执行完成 + §四 验收锚 4 条实测通过 | |
