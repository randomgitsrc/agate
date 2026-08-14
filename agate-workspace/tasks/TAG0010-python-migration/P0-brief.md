task: "agate 产品逻辑 Python 化（阶段一）：把 30 个 sh 的 bash 逻辑迁移到 Python（hook 入口保留 sh 薄壳），消解 bash 在 Windows MSYS2 模拟层的结构性平台问题。分析报告 docs/reviews/agate-python-migration-analysis-20260814.md 已定稿。阶段二（测试框架 bats→pytest）另立。TAG0008 版本管理依赖本任务（避免用将废弃的 bash 路线实现新工具）"

issues:
  - "根因（TAG0005/0009 复盘）：78 个 Windows 失败 + 11.7 小时 CI 排障拉锯 = bash 在 Windows MSYS2 模拟层不成立（MSYS 路径风格混用/CRLF/WSL 干扰/路径解析差异）。Python 跨平台可消解产品脚本侧的结构性平台问题"
  - "现状：agate 早已是 'sh 薄壳 + py 逻辑' 混合架构——19/30 个 sh 的退出路径落在 python；无 bash-only 不可移植特性（0 个关联数组）"
  - "硬约束：git hook 入口必须保留 sh 薄壳——理由已核实充足：①git 在 Windows 通过 Git Bash 的 sh.exe 执行 hook，shebang 由 git 内部解析；②#!/usr/bin/env bash 总能解析（git 自带 bash），而 #!/usr/bin/env python3 依赖 env/python3 在 git 的 PATH 可解析（Windows 命令名是 python 非 python3，PATH 有限，不可靠）；③复制模式 .agate-root 恢复必须留在薄壳。约 15 行/个，逻辑全移到 py"
  - "阶段一范围：30 个 sh → py（优先 check-gate.sh 488 行 + pre-commit-gate.sh 404 行两个最重）；gate-result.sh + agate-workspace-resolve.sh → agate_common.py；CI 保持 Linux 全量 + Windows 冒烟"
  - "明确不做：测试框架迁移（TAG0011 另立）；协议文档全量重写与 CI 同步归 TAG0011（用户确认 2026-08-14）——阶段一只做必要的脚本内部逻辑迁移，不铺开文档"

known_risks:
  - "协议文档与脚本引用大面积失效——每个脚本迁移后跑 consistency + 全量 bats；文档与代码同步改"
  - "consistency.py 锚点关键字约束：CHECK 8/9 锚点表硬编码 .sh 路径与关键字——py 版脚本必须保留这些关键字或同步更新锚点表，否则 consistency 报 ERROR"
  - "hook 入口 exec 失败（Python 路径/依赖）——hook 薄壳加 'python 探测 + 失败回退'；保留 sh 逻辑作为 fallback"
  - "pyyaml 从可选变强制依赖——所有 gate 逻辑依赖，SETUP.md 明确 pip install pyyaml，纳入 CI"
  - "编码规范：Windows Python 文本默认 ANSI 代码页——新代码必须显式 encoding='utf-8'，列为 gate 规则（否则 88d0deb 根因复发）"
  - "Python 版本下限 3.8+——避免 3.9+/3.10+ 语法（match、str.removeprefix 等）"
  - "测试回归——阶段一逐脚本迁移 + 每步全量 bats 验证；不批量重写"
  - "【强制要求】同类扫描 + 影响面梳理：P1/P2 必须梳理 '30 个 sh 的调用关系 + 文档引用 + 锚点关键字' 完整影响面，先画映射表再动手。用户明确：不愿意一轮一轮来回改"
  - "【2026-08-14 用户确认】走完整 task（P0-P8）；TAG0008 版本管理推迟到本任务之后（避免用将废弃的 bash 路线实现新工具）"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 用 CI matrix 冒烟 + 静态分析验证（分析报告 §4 逐项映射 Python 消解效果）"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict；shellcheck -S warning agate/scripts/*.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0010-python-migration/"
  # 分析报告：docs/reviews/agate-python-migration-analysis-20260814.md（§9 立项建议 + 5 条验收标准）
