task: "agate 协议脚本环境适配（Windows 原生兼容 + Linux 基线回归）：修复审计发现的 SEVERE/MODERATE 环境问题——pre-commit-gate 空格路径静默绕过、13 个 py 缺 encoding、P6 证据引用 ASCII 正则、全角冒号 locale 残留、CRLF 污染、路径正则元字符。核心约束：Linux 现状是基线不得回退，Windows 兼容是增量"

known_risks:
  - "改动面横跨 46 个脚本（25 sh + 21 py），每处都可能在 Windows 修复时破坏 Linux 行为——必须用现有 bats 全量回归 + 新增 Linux 基线测试兜底"
  - "pre-commit-gate.sh 空格拼接列表（S1）是 fail-open 静默绕过，最危险但改动也最易引入回归——改数组后需验证 Linux 下全部 commit 场景"
  - "13 个 py 加 encoding 是机械改动但量大，漏一处就还有隐患——需用 grep 断言审计（所有 open() 必须带 encoding）"
  - "Windows 无法在本环境（Linux）实测——只能静态修复 + Linux 回归 + CI 双平台验证（protocol-tests.yml 加 windows-latest）兜底，不能宣称'已实测 Windows'"
  - "check-p6-evidence.sh 中文证据文件名（S2）若改正则过宽，可能放过真正的缺证据误报——需新增中文文件名回归测试"
  - "M6（md CRLF）改动 .gitattributes 会影响所有仓库的 md 换行——需评估存量历史 review 文件影响，或改用 frontmatter 提取处统一容错"
  - "【2026-08-13 用户明确】兼容 Windows ≠ 只支持 Windows——Linux 现状是基线，Windows 是新增，两个平台都要跑通，不能为了 Windows 牺牲 Linux"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "limited"
  git: true

env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale），Windows 需通过 CI windows-latest 验证"
  test_cmd: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/；python3 agate/scripts/check-protocol-consistency.py --strict"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0004-env-adaptation/"
  # 关键：所有修复必须保持 Linux 全绿（现有 676 测试为回归基线），Windows 兼容通过静态分析 + CI matrix 验证
