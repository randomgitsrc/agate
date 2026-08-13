task: "agate 协议脚本健壮性 + 环境适配（Windows 原生兼容 + Linux 基线回归）：修复审计发现的 SEVERE/MODERATE 环境问题 + TQC0001 复盘归入项 + roadmap 并入项（RM-AG0001/AG0002）——pre-commit-gate 空格路径静默绕过、13 个 py 缺 encoding、P6 证据引用 ASCII 正则、全角冒号 locale 残留、CRLF 污染、路径正则元字符；并入 Q1（AGATE_ROOT 路径归一化）、Q5（PATH/编码/CRLF/.gitignore 模板）、Q2（阶段卡片 phase 推进顺序对齐 git-integration.md 规则 2）、M4/M5（全角冒号 locale 残留同类）、RM-AG0001（check-gate P1 反引号包裹盲区）、RM-AG0002（check-tdd-red 无 formatter A/B 类盲区）。核心约束：Linux 现状是基线不得回退，Windows 兼容是增量"

known_risks:
  - "改动面横跨 46 个脚本（25 sh + 21 py），每处都可能在 Windows 修复时破坏 Linux 行为——必须用现有 bats 全量回归 + 新增 Linux 基线测试兜底"
  - "pre-commit-gate.sh 空格拼接列表（S1）是 fail-open 静默绕过，最危险但改动也最易引入回归——改数组后需验证 Linux 下全部 commit 场景"
  - "13 个 py 加 encoding 是机械改动但量大，漏一处就还有隐患——需用 grep 断言审计（所有 open() 必须带 encoding）"
  - "Windows 无法在本环境（Linux）实测——只能静态修复 + Linux 回归 + CI 双平台验证（protocol-tests.yml 加 windows-latest）兜底，不能宣称'已实测 Windows'"
  - "check-p6-evidence.sh 中文证据文件名（S2）若改正则过宽，可能放过真正的缺证据误报——需新增中文文件名回归测试"
  - "M6（md CRLF）改动 .gitattributes 会影响所有仓库的 md 换行——需评估存量历史 review 文件影响，或改用 frontmatter 提取处统一容错"
  - "【2026-08-13 用户明确】兼容 Windows ≠ 只支持 Windows——Linux 现状是基线，Windows 是新增，两个平台都要跑通，不能为了 Windows 牺牲 Linux"
  - "【2026-08-13 并入 TQC0001 复盘】Q1：agate-next-card.sh 卡片 hash 校验的 `${CARD_FILE#$AGATE_ROOT/}` 前缀匹配在 Windows 盘符/斜杠下失效（TQC0001 实测 4 次 gate 重试）——路径归一化属本任务范围，修法需同时保证 Linux 前缀匹配不变"
  - "【2026-08-13 并入 TQC0001 复盘】Q5：Windows 下 PATH 注入、控制台 GBK 乱码、core.autocrlf CRLF、.gitignore 模板缺 version.txt/dist 白名单——SETUP.md 增 Windows 章节 + 模板预设"
  - "【2026-08-13 并入 TQC0001 复盘】Q2：7 张阶段卡片仍残留 v0.29.0 模式 B 旧写法（先更新 phase=N→N+1 再 commit），与 v0.40.1 git-integration.md 规则 2（phase=本 commit 产出阶段，不得提前写下一阶段）矛盾。P5 卡已同步，P1/P2/P3/P4/P6/P7/P8 未跟上。修复=卡片与规则 2 对齐（补注'commit 时 phase = 本 commit 产出阶段，下一阶段推进随下一阶段产出同 commit'），不改 commit 顺序（P2.64 原子性设计保留）。TQC0001 实测 2 次真实失败 + 1 次侥幸。注意：修改 phase-cards/*.md 触发 SELF-GATE"
  - "【2026-08-13 并入】M4/M5 全角冒号 [:：] locale 残留（check-gate.sh:356、check-p6-format.sh:69）——v0.40.3 只修了 check-p6-format.sh:84 一处，同类实例未清干净，与审计问题同类，归入本任务一并处理"
  - "【2026-08-13 并入 RM-AG0001】check-gate.sh P1 标记反引号包裹识别盲区——行首正则 `^\\s*-?\\s*\\[SUGGEST:` 对 `` `[SUGGEST: ...]` `` 不匹配（反引号在标记前），typo 兜底也不触发（冒号子串仍存在）→ 只 WARNING 不阻断。与 M4/M5 同在 check-gate.sh，同批修正则，避免二次动同一文件"
  - "【2026-08-13 并入 RM-AG0002】check-tdd-red.sh 无 formatter 时退化为 exit-code-only（L43）——编译失败（A 类）被误判为红灯（exit 0 推进）。有 formatter 时已区分 A/B 类（L80+），仅无 formatter 降级路径残留。修复方向：无 formatter 时对 exit code 做更保守判定（如 exit 1 且输出含 compile/error 关键词 → 判 A 类）"

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
