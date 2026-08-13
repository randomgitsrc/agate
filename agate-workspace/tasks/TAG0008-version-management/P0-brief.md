task: "agate 版本管理机制（v1）：多版本共存 + 项目级版本锁定 + 程序化安装/升级，解决'~/.agate 唯一、pull 被动升级打断实施'。v1 闭环 4 组件——agate-install / agate-resolve / hook 解析入口 / summary 版本显示。设计稿 docs/plans/agate-version-management-20260813.md 已定稿"

issues:
  - "被动升级问题：~/.agate 是单一软链→指向某 checkout/agate。git pull 后所有用 ~/.agate 的项目全部被动升级，进行中的项目被打断。hook 通过软链自动跟随，无法按项目隔离"
  - "形态2（用户确认）：安装即建版本目录 ~/.agate/vX.Y.Z/（git worktree 检出 tag），latest 是纯指针→最新发布版。非'latest 真实 checkout 归档'"
  - "项目锁定（asdf 模式）：项目根 .agate-version 声明 agate: v0.43.0，从 cwd 向上查找；无声明回退 ~/.agate/current（默认→latest）。v1 只支持精确版本，>= 折中留 v2"
  - "hook/setup 版本对应：install-hook 装固定入口 resolve-entry.sh，运行时读项目 .agate-version→映射版本→得 AGATE_ROOT→source 该版本 gate 逻辑。项目 A 锁旧版、项目 B 用新版互不干扰，切版本不用重装 hook"
  - "语言路线：.sh（bash，Git for Windows/MSYS2），与 TAG0004 对齐复用其 bash 适配（encoding/引号/locale/路径/软链退化）"
  - "向后兼容：~/.agate 软链保留，无 .agate-version 的项目 resolve 回退 current；AGATE_ROOT env 显式覆盖优先级最高"
  - "summary 集成：显示当前项目解析到的版本 + 原因（.agate-version 或全局 current）；v2 扩展版本列表"

known_risks:
  - "hook 改造影响所有下游项目——resolve 失败必须回退稳（回退 current），不能因解析失败静默禁用 gate"
  - "~/.agate 从'单软链'到'目录'的迁移影响存量用户——需迁移脚本/文档，install.sh 保留兼容"
  - "Windows 软链退化：latest/current 指针在无符号链接权限时用复制/配置文件模式（platform-notes 已有先例，复用 TAG0004 成果）"
  - "与 TAG0004 有依赖：本任务的 bash 适配（encoding/引号/locale/路径归一化）依赖 TAG0004 的环境修复成果——实施顺序应在 TAG0004 之后或并行隔离"
  - "【强制要求】同类扫描 + 影响面梳理：版本管理是机制级改动，涉及 install.sh/install-hook.sh/pre-commit-gate.sh/agate-summary.sh/SETUP/README/UPGRADING 多个文件联动。P1/P2 必须梳理'~/.agate 消费点'（哪些脚本/文档引用 ~/.agate 路径），确保改一处同步所有联动点。用户明确：不愿意一轮一轮来回改"
  - "【2026-08-13 用户确认】走完整 task（机制级，比 TAG0005/6/7 大），P0-P8；不 plan 硬做"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix 或 TAG0004 后的 MSYS2 环境验证"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0008-version-management/"
  # 设计稿：docs/plans/agate-version-management-20260813.md（§8 决策定稿 + v1/v2 范围）
