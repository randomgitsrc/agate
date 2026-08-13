# agate 版本管理机制设计（agate-version-management）

> **状态**：设计稿（待独立 task 立项实施）
> **日期**：2026-08-13
> **来源**：用户需求讨论（多版本共存 + 项目锁定 + 跨平台），参考 asdf/mise/nvm/pyenv 业界实践 + git worktree
> **语言路线**：.sh（bash，Git for Windows/MSYS2，与 TAG0004 对齐）——用户已确认

---

## 1. 问题背景

**现状**：`~/.agate` 是单一软链 → 指向某个 checkout 的 `agate/` 子目录。升级 = 对该 checkout `git pull` → **所有用 `~/.agate` 的项目全部被动升级**。hook 通过软链自动跟随 → 一个项目开发中，agate 本体升级会**打断进行中的项目实施**。

**目标**：
1. 多版本共存（`v0.20.1` / `v0.43.0` / `latest`）
2. **项目级版本锁定**（每个项目指定用哪个 agate 版本，asdf 模式）
3. 安装/升级通过**程序**（非手动 clone+ln）
4. 升级不打断进行中项目（锁旧版的项目不受影响）
5. 跨平台（Linux + Windows via Git for Windows/MSYS2）

## 2. 业界实践参考

| 实践 | 机制 | 借鉴点 |
|------|------|--------|
| asdf | shims + `.tool-versions` 项目声明 + **从 cwd 向上查找** | 版本解析按项目目录，非全局 |
| mise | `min_version`（锁最低版本非锁死）| 平滑演进，不锁死 |
| nvm/pyenv | 多版本并存目录 + 软链/激活切换 | 版本共存是常态 |
| git worktree | 同仓库多 checkout 共享 .git 对象 | **agate 版本本质是 git tag**，worktree 免费多版本 + 省磁盘 |

## 3. 核心设计决策

### 3.1 形态：安装即建版本目录，latest 是纯指针（用户确认）

```
~/.agate/
├── repo/              # 唯一主仓库（首次 clone，之后只 pull + worktree）
├── dev/               # worktree → main（开发版，跟随 pull）
├── v0.43.0/           # worktree → tag v0.43.0（稳定版，冻结）
├── v0.44.0/           # worktree → tag v0.44.0
├── latest -> v0.44.0  # 纯指针：最新发布版
└── current            # 全局默认指针（默认 → latest）
```

**与用户原方案的映射**：
| 用户方案 | 最终设计 |
|---------|---------|
| `{agate_root}/agate-latest` | `~/.agate/latest`（纯指针，非 checkout）|
| `{agate_root}/agate-v0.20.1` | `~/.agate/v0.20.1`（worktree 实现）|
| `{agate_root}/.agate-env` 全局 | 改为**项目级** `.agate-version`（asdf 模式）|
| 全局 `agate_current_version` | 保留为 `~/.agate/current`（项目声明优先）|

**为什么不用"latest 是真实 checkout"**：latest 内容会随 pull 变（隐藏行为）；纯指针 `-> v0.44.0` 无隐藏行为，谁指向谁一目了然。

### 3.2 为什么多版本必然需要多份代码

只有 `latest` 时，它演进到 v0.44.0 后，锁 v0.43.0 的项目**拿不到旧代码**（只在 git tag 里）。只要"项目锁旧版 + 新项目用新版"并存，就必须多份代码共存。worktree 是实现手段（省磁盘、秒级），对用户透明。

### 3.3 语言路线：.sh（bash，MSYS2）

- agate 的"Windows 支持"定义 = **Git for Windows 提供 bash**（platform-notes L152，TAG0004 方向），非纯 cmd/PowerShell
- 版本工具是 gate 生态一部分，应**同环境同语言**（.sh），复用 TAG0004 的 bash 适配（encoding/引号/locale/路径）
- 若做 .py 版本工具，Windows 原生能跑但管理的是"给 bash 脚本用的 agate"——悖论，脱离生态单独跨平台没意义

## 4. 组件设计

### 4.1 `agate-install.sh`（新，或改造 install.sh）

```bash
agate-install                    # 首次：clone repo → worktree add dev → latest=dev 或最新 tag
agate-install v0.43.0            # 装特定版本：repo 已存在则 worktree add v0.43.0
agate-upgrade                    # repo pull → 新 tag 版本自动归档 → latest 重指向
```

**为什么不需要每次 clone**：`repo` 只 clone 一次，所有版本 `worktree add` 出来（秒级、共享对象）。agate 是纯文档+脚本仓库，版本 = git tag 代码快照，无编译安装。

### 4.2 `agate-resolve.sh`（新，版本解析器，asdf 模式）

```
从项目 cwd 向上找 .agate-version → 命中用其声明的版本
无声明 → ~/.agate/current（全局默认）
输出 AGATE_ROOT=<对应版本路径> + 版本号
```

**`.agate-version` 语法**：
```
agate: v0.43.0        # 精确锁定
agate: >=v0.40.0      # 最低版本（mise min_version 折中，平滑演进）
```

### 4.3 hook/setup 改造（版本对应，用户强调）

- `install-hook.sh`：hook 指向**固定入口** `~/.agate/scripts/resolve-entry.sh`，不指向具体版本
- `resolve-entry.sh` 运行时：
  1. 从项目 cwd 向上找 `.agate-version` → 项目锁定版本
  2. 映射 `~/.agate/v0.43.0/` → AGATE_ROOT
  3. source 该版本的 `gate-result.sh` 等
- **效果**：项目 A 锁 v0.43.0 用旧 gate，项目 B 用 latest 用新 gate，同机互不干扰；改 `.agate-version` 切版本**不用重装 hook**
- orchestrator 注册（`.opencode/agents/orchestrator.md`）同理：软链指向解析入口

### 4.4 Windows 适配（复用 TAG0004）

- 软链退化：latest/current 指针在 Windows 无符号链接权限时用**复制/配置文件模式**（platform-notes 已有先例）
- 路径：`~/.agate` 在 Windows 是 `C:\Users\xxx\.agate`，resolve 处理盘符
- 依赖 TAG0004 成果：encoding / 引号 / locale / 路径归一化

## 5. 安装/发布/升级流程

### 首次安装
```bash
agate-install
# clone repo → worktree add dev → current=dev（或最新 tag）
```

### 发布 v0.44.0
```bash
git -C ~/.agate/dev tag v0.44.0 && git -C ~/.agate/dev push origin v0.44.0
git -C ~/.agate/dev worktree add ~/.agate/v0.44.0 v0.44.0
ln -sfn ~/.agate/v0.44.0 ~/.agate/latest
```

### 日常升级（不打断项目）
```bash
git -C ~/.agate/dev pull
```

### 项目锁版本
```bash
echo "agate: v0.43.0" > 项目根/.agate-version
```

## 6. 与现有机制的兼容

- **`~/.agate` 软链保留**（向后兼容）：现有项目无 `.agate-version` → resolve 回退 `~/.agate/current` → 兼容现状
- **install.sh 保留**：现有 install.sh 作为 `agate-install` 的底层实现或替换
- **AGATE_ROOT env 覆盖**保留：手动设 AGATE_ROOT 优先级最高（显式 > 项目声明 > 全局）

## 7. 实施范围（独立 task）

| 组件 | 类型 |
|------|------|
| `agate-install.sh` / `agate-upgrade.sh`（新）| 系统工具 |
| `agate-resolve.sh`（新）| 版本解析器 |
| `install-hook.sh` 改造 | hook 装"解析入口"|
| `pre-commit-gate.sh` 改造 | AGATE_ROOT 运行时解析 |
| SETUP.md / README / UPGRADING | 文档 |
| `.agate-version` 语法规范 | 协议 |
| bats 测试 | 回归 |

**风险**：hook 改造影响所有下游项目（解析失败回退逻辑必须稳）；Windows 软链退化；`~/.agate` 从"单软链"到"目录"的迁移（存量用户）。
**建议**：独立 task 立项（机制级，比 TAG0005/6/7 大），走完整 P0-P8；与 TAG0004（环境适配）有依赖（复用其 bash 适配）。

## 8. 决策定稿（2026-08-13 用户确认判断）

### 8.1 dev 存在但不默认（定稿）

- `dev/` 目录**存在**（agate 自身 dogfooding 必须，主 checkout 即 dev）
- 普通项目**默认不指向 dev**——只有显式 `agate: dev` 或 AGATE_ROOT 指向才用
- 理由：dev 是未验证代码，普通使用者应拿发布 tag

### 8.2 current 默认指向 latest（定稿）

- `~/.agate/current` 默认 → `latest`（最新发布 tag）
- 需要 dev 的人显式声明，不默认
- **兼容性收益**：pull 主 checkout 不再影响 `~/.agate`（解决"被动升级"）——这正是版本管理的核心目标
- 对 agate 自身：主 checkout 即 dev，需显式 `.agate-version: dev` 或 AGATE_ROOT

### 8.3 清理策略：引用即保护，v1 只检查不自动删（定稿）

- **引用即保护**：任何项目 `.agate-version` 声明了 v0.43.0 → 该版本永不清理
- **保留窗口**：最近 2 个 minor + latest
- **v1 范围**：`agate-prune --check` 只做引用检查 + 报告（列出"被引用的版本/可清理的版本"），**不自动删除**——等实际版本多了、确认不会误伤再开自动删
- 理由：清理是"引用检查 + 保留窗口"双条件，防"某项目锁的版本被删"灾难

### 8.4 agate-summary 显示当前项目版本 + 原因（定稿）

- `agate-summary.sh` 显示：
  - 当前项目解析到的 AGATE_ROOT（哪个版本 + 为什么：`.agate-version` 声明 or 全局 current）
  - 全局 current 指向
- v2 扩展：已安装版本列表
- 理由：把"项目用哪个版本 + 为什么"显性化，排障不再靠猜

### 8.5 v1 / v2 范围划分（定稿）

| 项 | v1（可用闭环）| v2 |
|----|---------------|-----|
| 安装/升级 | `agate-install` / `agate-upgrade` | — |
| 版本解析 | `agate-resolve`（精确 `v0.43.0`）| `>=` 最低版本语义 |
| hook | 装解析入口，运行时解析 | — |
| summary | 显示当前版本 + 原因 | 版本列表 |
| prune | 引用保护检查（不自动删）| 自动清理 |

**v1 = 4 组件可用闭环**（install/resolve/hook 解析/summary 显示），不拖泥带水。

## 9. 整体自省：是否过度设计

- **必要**：被动升级打断实施是真实痛点；多版本共存 + 项目锁定是刚需
- **控制**：v1 收敛到 4 组件；prune 只检查；`>=` 折中留 v2；语法 v1 只支持精确版本
- **最小可用闭环**优先，避免一次铺开
