task: "agate 脚本一致性批：RM-AG0015（CHECK 10 文档脚本名引用漂移 gate）+ RM-AG0017（self-gate 触发面补 README/AGENTS）+ RM-AG0018 剩余（check-retrospective 登记提醒）。同属'脚本 + 一致性/self-gate'层，改动域重叠（脚本 + 测试 + consistency），合并一个 task"

issues:
  - "RM-AG0015 文档脚本名引用漂移无 gate 兜底：CHECK 2 的 REF_RE 只匹配 docs/assets/scripts 前缀引用，裸脚本名（phase-cards/rules 全是）完全漏检——实测 'check-tdd-red.py 确认' → 正则匹配 []。v0.46.0 的 phase-cards 26 处过时 .sh 引用就是实锤（已修无 gate 防复发）。另有 PROTOCOL_FILES 缺 phase-cards/rules（引用检查降级 WARNING）。已登记 DEBT0001（source: retrospective）。修复=①新增 CHECK 10（扫描协议文件脚本名引用对照 scripts/ 实际文件，豁免 UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh）②phase-cards/rules 入 PROTOCOL_DIRS"
  - "RM-AG0017 self-gate 触发面缺仓库根级文档：commit-msg-self-gate.py 的 _SELF_GATE_RE 覆盖 agate/scripts/*、agate/*.md、agate/*/*.md、SELF-GATE.md，不含 README.md/AGENTS.md——改仓库根级协议文档不触发 self-gate WARNING（本次文档体系更新即绕过）。注意复盘原文称'SELF-GATE.md 不在触发面'是错误（实测正则包含它）。修复=_SELF_GATE_RE 扩展匹配 README.md/AGENTS.md（CHANGELOG 豁免）"
  - "RM-AG0018 剩余（主体已落地）：tech-debt 登记触发点——DEBT0001 已登记、postmortem-template 已加'技术债登记'核对行（2026-08-15 完成）。剩余：check-retrospective.py（P2.12）输出加一行'复盘发现的新缺口请登记 DEBT/roadmap'提醒（纯提醒不拦截）"

known_risks:
  - "三条都改脚本 + 测试 → 触发 SELF-GATE"
  - "RM-AG0015 CHECK 10 是新增一致性检查——豁免清单（UPGRADING 对照表/formatters/薄壳/count-tests.sh）设计要防误报，P1 需先画'哪些文档引用哪些脚本名'影响面"
  - "RM-AG0017 扩展触发面可能误报（CHANGELOG 频繁变动）——需豁免设计 + 测试锁定"
  - "【强制要求】同类扫描 + 影响面梳理：P1 必须全仓 grep 脚本名引用（裸名 + 相对路径）建影响面表；grep self-gate 触发面相关测试。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/"
