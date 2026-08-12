# 首次接入指南：把 orchestrator 注册成可调用的 Agent

> 面向**第一次把 agate 接入某个项目**的人。`README.md`「快速上手」讲的是"装 agate 本体"，这份文档讲的是下一步——怎么让 OpenCode / Claude Code 真的能调起 orchestrator，这一步是平台相关的，容易卡住，所以单独写。
>
> 前置：已完成 `README.md`「快速上手」第 1 步（`~/.agate` 软链接存在，指向协议本体）。没做完先去做那一步。

---

## 核心结论先说

- **只需要注册 orchestrator 这一个 agent**。P1-P8 的执行角色/评审角色不需要在平台层预注册——派发时是"派一个通用 subagent，把角色文件路径写进 prompt 让它自己读"，见 `role-system.md`「方法 B」。
- `orchestrator-template.md` 对所有项目内容完全一致，**标准接入方式是符号链接直接指向它，不要拷贝**。这样 agate 升级模板，你项目里的 orchestrator 提示词自动跟着升级，不需要手动同步。
- 项目特定信息（工作区规则、gate 命令、测试基线……）**只写进** `{AGATE_WORKSPACE}/agents/project.md`（可选文件，模板见 `assets/templates/project.md`），不要碰 orchestrator.md 本身。工作区默认在项目根 `agate-workspace/`，可用 `.agate.env` 的 `AGATE_WORKSPACE=` 指向其他位置（含项目外绝对路径），解析见 `scripts/agate-workspace-resolve.sh`。

---

## 步骤 1：（可选）创建 project.md

如果你的项目有 orchestrator 专属的操作细节（不适合塞进通用的 AGENTS.md/CLAUDE.md），复制模板：

```bash
mkdir -p {AGATE_WORKSPACE}/agents
cp {agate_root}/assets/templates/project.md {AGATE_WORKSPACE}/agents/project.md
# 按模板里的说明填写，删掉不需要的小节
```

没有这类细节就跳过——orchestrator 默认只读 AGENTS.md/CLAUDE.md 也能正常工作。

## 步骤 2：把 orchestrator 注册到你的平台

**先确认你的 `agate_root`**（默认 `~/.agate`，自定义过装哪的话按实际路径替换下面命令里的 `~/.agate`）。

### Claude Code（`.claude/agents/`）

```bash
mkdir -p .claude/agents
ln -sf ~/.agate/orchestrator-template.md .claude/agents/orchestrator.md
```

**注意用文件级链接，不要把整个 `.claude/agents` 目录链到别处**——那样会让这个目录里以后任何非 agate 的自定义 agent 都被迫绑定到同一个源头，也可能把无关文件暴露给 agent 发现机制。只链这一个文件。

**Claude Code 的 frontmatter 必须含 `name: orchestrator` 字段**——缺了这个字段，Claude Code 会静默跳过整个文件，不报错不警告，agent 就是"不存在"，`orchestrator-template.md` 已经带了这个字段，不需要你额外加，这里提醒是因为如果你自己改过模板、不小心删掉了这个字段，是最容易踩、也最难发现的坑（没有任何报错信息）。

验证：`claude agents --json` **不能**用来验证——那条命令列的是当前活跃的后台/交互会话，和 `.claude/agents/` 目录下的自定义 agent 定义无关，跑通了不代表 orchestrator 注册成功。目前没有等价于 OpenCode `opencode debug agent <name>` 的空跑校验命令，最小成本的验证方式是真的选中一次：
```bash
claude --agent orchestrator -p "echo test"
```
能正常选中 orchestrator 并返回、不报 "Failed to parse agent" 或类似错误，就说明注册成功——不需要跑一次完整任务。

### OpenCode（`.opencode/agents/`）

```bash
mkdir -p .opencode/agents
ln -sf ~/.agate/orchestrator-template.md .opencode/agents/orchestrator.md
```

同样是文件级链接，理由同上。

> ⚠️ **副作用**：创建 `.opencode/` 目录后，OpenCode 会把它当作插件目录，自动初始化 `@opencode-ai/plugin` 依赖（生成 `package.json`/`package-lock.json`/`node_modules`）。这是 OpenCode 平台行为，无害，但 `.opencode/node_modules` 里的 `.md` 文件可能被 agate 的一致性检查（`check-protocol-consistency.py`）误扫——已从扫描范围排除 `.opencode`/`.claude`/`node_modules`，无需处理。

验证：
```bash
opencode debug agent orchestrator
```
应该能看到 `"mode": "primary"`、`"tools": {..., "task": true, ...}` 这些字段——重点看 `task` 是不是 `true`（这是 orchestrator 派发 subagent 要用的工具，早期 OpenCode 版本有过一个已知 bug 会让自定义 agent 拿不到这个工具，[issue #14308](https://github.com/anomalyco/opencode/issues/14308)，当前主流版本已修复，但升级/降级 OpenCode 后建议重新跑一次这条命令确认）。
`opencode agent list` 不会列出这个自定义 agent（那个命令只列内置 agent），看不到不代表没装上，以 `opencode debug agent orchestrator` 的结果为准。

### Windows（无 WSL，用 Git for Windows）

符号链接需要管理员权限或开发者模式（和 `install-hook.sh` 装 hook 遇到的限制是同一个系统限制）：

```bash
# Git Bash 里，和 Linux/macOS 写法一样：
ln -sf ~/.agate/orchestrator-template.md .claude/agents/orchestrator.md
ln -sf ~/.agate/orchestrator-template.md .opencode/agents/orchestrator.md
```

如果报错（没有开发者模式/非管理员），退化成复制：
```bash
cp ~/.agate/orchestrator-template.md .claude/agents/orchestrator.md
cp ~/.agate/orchestrator-template.md .opencode/agents/orchestrator.md
```
⚠️ **复制模式的代价**：agate 升级模板后不会自动同步，你需要在每次升级完 agate 后手动重跑上面这两条 `cp` 命令。目前没有自动漂移检测（`agate-summary.sh` 现有的漂移检测只覆盖 `scripts/` 目录下的脚本副本，不覆盖这个文件），这是已知的手动步骤，忘了也不会报错提醒——建议每次升级 agate 后养成习惯重跑一遍。

`cmd`/PowerShell 的 `mklink` 底层调用的是和 `ln -sf` 同一个系统 API，一样需要管理员权限，不是绕开限制的办法；`mklink /H`（硬链接）在同一 NTFS 分区内不需要管理员权限，可以作为免权限的进阶选项，但硬链接绑定的是当前这份文件的磁盘位置，**agate 自身升级模板文件时如果不是原地改写而是新建后替换（多数 git 实现是这样），硬链接会指向旧内容变成过期链接**——这一点没有在这套环境实测过，如果要用请自己验证一次"升级 agate 后硬链接是否还生效"，不确定就用复制模式更保险。

## 步骤 3（可选）：设成默认 agent

不设的话，每次开会话需要手动选/指定 orchestrator；设了之后新会话默认就是它。

**Claude Code**：
```bash
mkdir -p .claude
cat > .claude/settings.json <<'EOF'
{"agent": "orchestrator"}
EOF
```

**OpenCode**：目前没有找到确认过的、等价于 Claude Code `settings.json` 默认 agent的机制——可能需要 `opencode.json` 里配置，也可能只能每次用 `--agent orchestrator` 或平台内选择器手动指定。这条待核实，先按需要每次手动指定。

**要不要把这一步的配置文件提交进 git**：这是团队取舍，不是技术限制——提交意味着"团队所有人打开这个项目默认进 orchestrator"，不提交意味着"每个人自己决定"。两种都合理，自己定。

## 步骤 4：装 hook

```bash
bash ~/.agate/scripts/install-hook.sh
```

## 步骤 5：整体验证

```bash
bash ~/.agate/scripts/agate-summary.sh   # 确认协议版本、hook 已装
bash ~/.agate/scripts/agate-workspace-resolve.sh  # 确认工作区解析（输出 AGATE_WORKSPACE）
mkdir -p {AGATE_WORKSPACE}/{roadmap,tasks,agents,archived,reviews,decisions,plans,logs}
# 若 {AGATE_WORKSPACE}/tasks/active-tasks.md 不存在，orchestrator 首次运行会自动从模板建，不需要手动建
```

然后真开一个会话，指定/选择 orchestrator agent，让它执行「开始」那几步（读 `agate-summary.sh` 输出、读 `active-tasks.md`），确认它能正常找到 `{agate_root}`（`~/.agate` 或你设置的路径）、解析出 `{AGATE_WORKSPACE}` 并读到阶段卡片。

## .agate.env 配置（可选）

工作区位置默认 = 项目根下 `agate-workspace/`。需要指向别处时，在**项目根**创建 `.agate.env`：

```bash
# .agate.env（项目根）
AGATE_WORKSPACE=agate-workspace            # 相对路径 → 相对项目根解析
AGATE_WORKSPACE=/srv/agate-ws/My Project   # 绝对路径（可含空格）→ 指向项目外
```

优先级：`.agate.env` 显式配置 > 环境变量 `AGATE_TASKS_DIR` > 默认 `agate-workspace/`。缺失 `.agate.env` 不报错，走默认（BDD-4）。解析逻辑见 `scripts/agate-workspace-resolve.sh`。

## .gitignore 建议

```gitignore
# 平台 agent 目录本身是机器本地的注册入口（符号链接/复制品），不提交
.claude/agents/
.opencode/agents/
```

`{AGATE_WORKSPACE}/agents/project.md`（如果创建了）**要提交**——它是项目团队共享的真实内容，不是本地注册产物。`.claude/settings.json` 提不提交按上面步骤 3 的团队取舍决定。`.agate.env` 建议提交（团队共享工作区位置约定）；含本机路径的 `.agate.env` 可 gitignore，但提交一份默认样例更利于团队一致。

---

## 升级 agate 之后

**已有 agate 项目（跑过旧版任务）升级，先读 `UPGRADING.md`**——它讲清楚旧任务数据（active-tasks.md/.state.yaml/任务编号）如何处理，避免升级后踩到破坏性变更。

- 符号链接方式：什么都不用做，orchestrator 提示词自动跟着新版本。
- 复制模式（Windows 无权限场景）：重跑步骤 2 的 `cp` 命令。
- 两种方式都建议顺手跑一次 `bash ~/.agate/scripts/agate-summary.sh`，它会检测协议版本和本地脚本副本漂移（但目前不覆盖 orchestrator.md 复制模式的漂移，见上文已知限制）。
