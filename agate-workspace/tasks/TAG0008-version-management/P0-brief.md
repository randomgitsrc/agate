task: "agate 版本管理机制（v1）：多版本共存 + 项目级版本锁定 + 程序化安装/升级，解决'~/.agate 唯一、pull 被动升级打断实施'。v1 闭环 4 组件——agate-install / agate-resolve / hook 解析入口 / summary 版本显示 + **环境探测与 agent 向 setup 指引**。设计稿 archived/docs-2026-08/plans/agate-version-management-20260813.md 已定稿（2026-08-15 文档体系更新后归档，内容仍有效，P1/P2 引用时读归档路径）"

issues:
  - "被动升级问题：~/.agate 是单一软链→指向某 checkout/agate。git pull 后所有用 ~/.agate 的项目全部被动升级，进行中的项目被打断。hook 通过软链自动跟随，无法按项目隔离"
  - "形态2（用户确认）：安装即建版本目录 ~/.agate/vX.Y.Z/（git worktree 检出 tag），latest 是纯指针→最新发布版。非'latest 真实 checkout 归档'"
  - "项目锁定（asdf 模式）：项目根 .agate-version 声明 agate: v0.43.0，从 cwd 向上查找；无声明回退 ~/.agate/current（默认→latest）。v1 只支持精确版本，>= 折中留 v2"
  - "hook/setup 版本对应：install-hook 装固定入口 resolve-entry，运行时读项目 .agate-version→映射版本→得 AGATE_ROOT→exec 该版本 gate 逻辑。项目 A 锁旧版、项目 B 用新版互不干扰，切版本不用重装 hook"
  - "语言路线：**Python**（TAG0010/0011 已全面 Python 化，产品逻辑在 .py，3 个 hook 薄壳为 .sh）。与 TAG0010 产物对齐——版本管理的 install/resolve/summary 逻辑用 .py，hook 入口沿用薄壳模式（python 探测 + exec py）。TAG0008 原 P0-brief 的 .sh 路线已过时（TAG0010 完成，2026-08-15 修正）"
  - "安装来源与版本指定（2026-08-16 用户确认补充）：来源是 GitHub（repo 首次 clone + worktree add tag）；`agate-install` 无参数 = 装最新（latest 指针），`agate-install v0.48.0` = 装指定版本；**离线切换**（已装过的版本目录是本地 worktree，切版本完全离线）——设计稿 §4.1 已隐含支持，P0-brief 显式声明；**离线首次安装**（无网络装从未装过的版本）超出 v1 范围，记 v2"
  - "**内网离线部署包（2026-08-16 用户确认，升级模式 A）**：内网无互联网 + 有 agent，要在外网打包一个"可用的 agate 环境"拿进内网直接安装。**外网打包器** `agate-pack-offline.py v0.48.0 [--platform linux-x86_64|windows-x86_64] [--include-python] [--include-pillow]` → 产出平台标签 bundle（agate tag 代码 + wheels（pyyaml 必装/Pillow 可选，`pip download --platform <目标>` 按目标平台拉）+ 嵌入式 Python 可选 + manifest.json 清单）。**manifest.json 含各组件 checksum（sha256）**——外网打包时计算，内网安装器校验，不匹配拒绝安装（防传输损坏/篡改，内网经介质传递是基本保障）。**内网一键安装器** `install-offline.py [--skip-python] [--skip-pillow]` → 读 manifest.json 核对平台（不匹配警告防错装）+ 校验 checksum → 装 wheels（`pip install --no-index --find-links wheels/`）→ 建 ~/.agate/vX.Y.Z/ → hook/orchestrator 指向（Windows 复制模式/Linux 软链）→ 验证（agate-summary）。**勾选语义：打包时决定包含项，内网安装时可用 --skip 覆盖**。**git 不打包**（项目侧状态落盘依赖）。**平台维度：Python 运行时/wheels/hook 都是平台相关的，打包器必须按目标平台拉取**。与在线模式共用 agate-resolve/hook 逻辑，只有安装动作分叉"
  - "向后兼容：~/.agate 软链保留，无 .agate-version 的项目 resolve 回退 current；AGATE_ROOT env 显式覆盖优先级最高"
  - "summary 集成：显示当前项目解析到的版本 + 原因（.agate-version 或全局 current）；v2 扩展版本列表"
  - "环境探测 + agent 向 setup 指引（2026-08-16 用户确认补充）：`agate-install --check` 自动探测运行时（python3/pyyaml/git/bash），缺失项列清单 + 分平台修复指引；SETUP.md 增'环境准备（agent 执行）'节——**写给 agent 而非人类**（现在 setup 活多由 agent 干）：探测命令（agent 跑，exit code 可判）→ 分平台修复（Linux `python -m pip install pyyaml`；Windows Python/PATH/PYTHONUTF8/Git for Windows）→ 验证闭环（agate-summary + agate_common）。**不自动装系统级依赖**（Windows 自动配置不可行，各机器差异大）"

known_risks:
  - "hook 改造影响所有下游项目——resolve 失败必须回退稳（回退 current），不能因解析失败静默禁用 gate"
  - "~/.agate 从'单软链'到'目录'的迁移影响存量用户——需迁移脚本/文档，install.sh 保留兼容"
  - "Windows 软链退化：latest/current 指针在无符号链接权限时用复制/配置文件模式（platform-notes 已有先例，复用 TAG0004 成果）"
  - "【范围边界】内网离线部署包（打包器 + 一键安装器 + 勾选 + checksum 校验）**在 v1 范围内**（2026-08-16 用户确认）；**版本卸载/清理 `agate-install --uninstall v0.43.0` 也在 v1 范围内**（删版本目录 + 清理指针，防多版本磁盘膨胀，2026-08-16 用户确认加入）；离线包自动更新/镜像分发记 v2"
  - "【依赖已解除】原依赖 TAG0004（bash 适配）已完成（v0.44.0）；本任务现依赖 TAG0010/TAG0011 的 Python 化产物（install/resolve/summary 须按 .py 写、测试按 pytest）——两个前置均已完成，2026-08-15 更新依赖状态"
  - "【强制要求】同类扫描 + 影响面梳理：版本管理是机制级改动，涉及 install.sh/install-hook.py/pre-commit-gate.py/agate-summary.py/SETUP/README/UPGRADING 多个文件联动。P1/P2 必须梳理'~/.agate 消费点'（哪些脚本/文档引用 ~/.agate 路径），确保改一处同步所有联动点。用户明确：不愿意一轮一轮来回改"
  - "【2026-08-13 用户确认】走完整 task（机制级，比 TAG0005/6/7 大），P0-P8；不 plan 硬做"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）或 MSYS2 环境验证"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0008-version-management/"
  # 设计稿：archived/docs-2026-08/plans/agate-version-management-20260813.md（2026-08-15 归档，§8 决策定稿 + v1/v2 范围）
