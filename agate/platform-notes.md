# Platform Notes — 各平台适配说明

不同 Agent 平台对 agate 的支持程度不同，本文记录已知情况。

---

## OpenCode

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具派发 subagent | ✅ 可用 | 使用方法 B（general subagent + prompt 注入角色文件）|
| 自定义角色（--custom-role）| ❌ 不可用 | issue #29616，subagent 无法加载自定义角色 |
| 本地开发环境 | ✅ 完整 | P3-P8 全部阶段可执行 |

**推荐方式（方法 B）**：派发时在 prompt 里直接写入角色定义文件路径，让 subagent 自己读取。不使用 `--custom-role` 参数。

---

## Claude Code

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具派发 subagent | ✅ 可用 | Task tool 支持独立上下文 |
| 本地开发环境 | ✅ 完整 | P3-P8 全部阶段可执行 |

---

## Claude Project 会话（claude.ai）

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具 | ❌ 不可用 | 纯对话环境，无 task 工具 |
| 本地开发环境 | ❌ 受限 | 网络受限，npm/pip 安装受影响 |

**适用范围**：仅适合 P0-P2（设计规划阶段）。P3-P8 需交接给 OpenCode/Claude Code 执行。

**典型工作方式**：用 Claude Project 完成 P0-P2 并 push 到 main，再切换到 OpenCode 执行 P3-P8。

---

## Codex / Hermes / OpenClaw 等

待补充——如有使用经验，欢迎 PR。

---

## Hardening-roadmap 跨平台适配（自 v0.4 引入，持续生效）

hardening-roadmap 设计的核心 gate 机制（pre-commit hook + CI backstop）是 **git 协议级**的，自 v0.4 起所有平台统一可用。但配套能力有平台差异：

| 机制 | OpenCode | Claude Code | Codex | 说明 |
|------|---------|-------------|-------|------|
| pre-commit hook | ✅ 全功能 | ✅ 全功能 | ✅ 全功能 | git 机制本身，与平台无关 |
| `check-p6-provenance.py` 审计 | ✅ | ✅ | ✅ | 纯 Python + 文件系统 |
| `agent:` 字段协作规范 | ✅ | ✅ | ✅ | 文件级 metadata |
| `risk=high` 自审 WARNING | ✅ | ✅ | ✅ | hook 输出 exit 2 |
| CI backstop（gate 重跑 + provenance 重跑 + git blame WARNING）| ⚠️ 自实现 | ⚠️ 自实现 | ⚠️ 自实现 | GitHub Actions / GitLab CI / Gitea Actions 提供开箱实现（⚠️ Gitea 未实测） |
| 独立 git author 追踪（P2.10 根治）| ❌ | ❌ | ❌ | Phase 3 平台功能未实现 |
| `~/.agate` 软链接 | ✅ | ✅ | ✅ | 文件系统级，无平台差异 |

**CI backstop 说明**：`.github/workflows/protocol-tests.yml` 的 `gate-backstop` job 用 GitHub Actions 实现。ci-gate-backstop.py 原生支持 GitHub Actions / GitLab CI / Gitea Actions（通过 `detect_ci_platform()` 自动检测）。在自建 CI（Jenkins/本地）跑 agate 时：
- 需要等价实现：`git push` 后重跑 `scripts/check-gate.py` + `scripts/check-p6-provenance.py` + 调用 `ci-gate-backstop.py`
- 不实现 CI backstop 也能用——只是失去 `--no-verify` 绕过 hook 的兜底审计

**Codex 兼容性**：Codex subagent max_depth=1 与 P2.1 强制派发独立 subagent（risk=high）的兼容性：
- Codex 单层任务工具无法"再派发"——这种情况下 P2 review 必须由主 Agent 自己跑（agent=main）
- `check-gate.py` P2 对 `agent=main` 硬拦截（exit 1，不可自行批准评审）
- 升级到 Codex 多层派发（待官方发布）后兼容自动生效

---

## 验证记录

agate 的派发机制于 2026-06-12 在 OpenCode 上完成验证：
- Phase 1（方法 B 派发）✅
- Phase 2（方法 A 自定义角色）❌（issue #29616）
- Phase 3（上下文隔离）✅

完整验证报告存档：`archived/validation-report.md`

---

## Windows 原生（Git for Windows，不用 WSL）

> agate 的 gate 脚本已全部 Python 化（`.py`），不再依赖 bash + GNU coreutils——TAG0010 起**无 bash 环境（纯 cmd/PowerShell）成为可行选项**：脚本可直接 `python3` 运行。仅 3 个 git hook 入口保留 `.sh` 薄壳（定位 AGATE_ROOT + python 探测 + exec 对应 `.py` 主程序），需要 **Git for Windows** 自带的 sh 执行。以下仍按 Git for Windows 全功能方式说明。

### 前置条件

| 依赖 | 安装方式 | 说明 |
|------|---------|------|
| **Git for Windows** | https://git-scm.com/download/win （独立安装包，不依赖 GitHub 账号） | 提供 git + `sh`（hook 薄壳执行需要）。gate 脚本本体已不依赖其 bash/coreutils |
| **Python 3.8+** | https://www.python.org/downloads/ | 安装时勾选「Add to PATH」。全部 gate 脚本需要，**pyyaml 为强制依赖**（`pip install pyyaml`）|
| **pyyaml** | `pip install pyyaml` | **强制**。所有 py gate 脚本的 YAML 解析依赖（agate_common.py / 各状态读取工具），缺失时 fail-closed 阻断 |
| **Pillow（可选）** | `pip install Pillow` | 仅 check-p6-evidence.py 的像素方差/ahash 检测需要。未装时自动跳过（WARNING 不阻断）|
| **ruff（可选）** | `pip install ruff` | 仅开发者跑 `ruff check agate/` 时需要（替代 shellcheck，含 tests）。使用者不需要 |
| **pytest（仅开发者）** | `pip install pytest` | 使用者不需要跑测试；开发者跑 `python3 -m pytest agate/tests/`（Bats 已退役，TAG0011） |

### 安装步骤

1. **装 Git for Windows**：下载安装包，全程默认即可。它会在 `C:\Program Files\Git\` 安装 git + sh。

2. **验证 sh 可用（hook 薄壳执行需要）**：打开「Git Bash」（开始菜单），运行：
   ```bash
   bash --version
   ```
   应输出版本号。gate 脚本本体不需要 bash——验证纯 python 路径可用：

3. **装 Python + pyyaml**：
   ```bash
   python --version    # 应 3.8+
   pip install pyyaml
   ```

4. **clone agate 仓库**（任意 git 托管都行，不限于 GitHub）：
   ```bash
   git clone <你的 agate 仓库地址> ~/agate
   ```

5. **建立 `~/.agate` 软链接**（Git Bash 里 `~` 是 `C:\Users\<你>`）：
   ```bash
   ln -s ~/agate/agate ~/.agate
   ```
   > 若提示无法创建符号链接（无开发者模式/非管理员），改用环境变量：
   > 在系统环境变量里设 `AGATE_ROOT=C:\Users\<你>\agate\agate`（指向 agate 仓库的 `agate/` 子目录）。

6. **在项目仓库里装 hook**：
   ```bash
   cd /path/to/your/project
   python3 ~/.agate/scripts/install-hook.py
   ```
   > Windows 无符号链接权限时，hook 会以**复制模式**安装（输出含「复制模式」提示）。**升级 agate 后需重跑此命令**更新 hook（复制不自动跟随源文件）。

7. **验证 agate 可运行**：
   ```bash
   python3 ~/.agate/scripts/agate-summary.py
   ```
   应输出版本号 + 防护状态。

### 已知限制（Windows 原生）

| 限制 | 影响 | 规避 |
|------|------|------|
| `ln -sf` 退化为复制 | hook 不随 agate 升级自动更新 | 升级 agate 后重跑 `python3 ~/.agate/scripts/install-hook.py`；或开 Windows「开发者模式」启用真符号链接 |
| `core.autocrlf` CRLF 污染 | 3 个 hook 薄壳 `.sh` 报 `\r` 语法错；py 文件已显式 `encoding="utf-8"` 读写（免疫），仅卡片 sha256 校验受 hash 影响 | 仓库已含 `.gitattributes` 强制 LF；若 clone 旧版本无此文件，手动 `git config core.autocrlf false`。已 clone 且已物化 CRLF 的工作区需 `git add --renormalize .` 重规范化 |
| pytest 需安装 | 开发者无法跑 `python3 -m pytest` 测试 | `pip install pytest`（Windows 原生 python 直接可用）；或用 WSL 跑测试（使用不受影响） |
| CI 仅 ubuntu | Windows 本地行为无 CI 兜底 | 靠本地验证；protocol-tests.yml 的 pytest job 已加 `windows-latest` matrix（`-m windows_smoke` 冒烟，见 AGENTS.md 测试约定） |
| 路径分隔符 | MSYS2 自动转换 `/c/Users/` <-> `C:\Users\`，但极少数硬编码路径可能出问题 | 遇到时用 `cygpath -w` 转换 |

### 不支持的场景

- **纯 cmd/PowerShell 无 bash**：**TAG0010 起成为可行选项**——gate 脚本已全部 Python 化，`python3 ~/.agate/scripts/xxx.py` 可直接运行（P0-P8 全程可执行）。唯一受限：git hook 入口薄壳仍需 sh 执行，无 bash 时 hook 不触发（可用 CI backstop 兜底 `--no-verify` 场景）。
- **Cygwin（非 MSYS2）**：理论上可行但未测，不保证。推荐 Git for Windows。
