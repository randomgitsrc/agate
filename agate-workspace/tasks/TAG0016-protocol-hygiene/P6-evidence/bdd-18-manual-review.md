=== BDD-18: Windows 章节完整性核查 ===
3:> 职责边界：平台适配权威源——各 Agent 平台（OpenCode/Claude Code/Codex 等）能力矩阵、Windows 原生安装指南（详见职责声明表，P2-design.md §0）
85:## Windows 原生（Git for Windows，不用 WSL）
87:> agate 的 gate 脚本已全部 Python 化（`.py`），不再依赖 bash + GNU coreutils——TAG0010 起**无 bash 环境（纯 cmd/PowerShell）成为可行选项**：脚本可直接 `python3` 运行。仅 3 个 git hook 入口保留 `.sh` 薄壳（定位 AGATE_ROOT + python 探测 + exec 对应 `.py` 主程序），需要 **Git for Windows** 自带的 sh 执行。以下仍按 Git for Windows 全功能方式说明。
93:| **Git for Windows** | https://git-scm.com/download/win （独立安装包，不依赖 GitHub 账号） | 提供 git + `sh`（hook 薄壳执行需要）。gate 脚本本体已不依赖其 bash/coreutils |
102:1. **装 Git for Windows**：下载安装包，全程默认即可。它会在 `C:\Program Files\Git\` 安装 git + sh。
133:   > Windows 无符号链接权限时，hook 会以**复制模式**安装（输出含「复制模式」提示）。**升级 agate 后需重跑此命令**更新 hook（复制不自动跟随源文件）。
141:### 已知限制（Windows 原生）
145:| `ln -sf` 退化为复制 | hook 不随 agate 升级自动更新 | 升级 agate 后重跑 `python3 ~/.agate/scripts/install-hook.py`；或开 Windows「开发者模式」启用真符号链接 |
147:| pytest 需安装 | 开发者无法跑 `python3 -m pytest` 测试 | `pip install pytest`（Windows 原生 python 直接可用）；或用 WSL 跑测试（使用不受影响） |
148:| CI 仅 ubuntu | Windows 本地行为无 CI 兜底 | 靠本地验证；protocol-tests.yml 的 pytest job 已加 `windows-latest` matrix（`-m windows_smoke` 冒烟，见 AGENTS.md 测试约定） |
153:`~/.agate` 版本管理根目录里的 `latest` / `current` 是**纯指针**：Linux/macOS 用 POSIX 软链（`latest → v0.48.0`），Windows 无符号链接权限（或 `AGATE_HOOK_COPY_MODE=1`）时**退化为文本指针文件**——文件内容为指向的版本目录名（如 `v0.48.0`），解析时按内容恢复目标路径（`agate_common.py` 的指针链解析兼容软链与文本两形）。`.agate-root` 标记先例沿用：复制模式下安装的 hook / orchestrator 副本写 `.agate-root` 记录安装根，解析入口（`resolve-entry.py`）据此恢复 AGATE_ROOT。行为与单软链时代一致：解析失败回退 current，绝不静默禁用 gate。
158:- **Cygwin（非 MSYS2）**：理论上可行但未测，不保证。推荐 Git for Windows。

=== 人工核对：本任务全部 P6-acceptance.md 正文未出现'已在 Windows 实测验证'类措辞 ===
（核对对象：本文件自身 P6-acceptance.md 撰写时将逐句自查，不使用该类措辞；本次核对未发现历史 P6 文档，因本任务首次到达 P6）
