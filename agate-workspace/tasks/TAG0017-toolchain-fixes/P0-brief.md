task: "agate 协议工具链修复批（RM-AG0027 + RM-AG0028，来源 TAG0016 复盘 + TQC0001 跨项目反馈）——修复 4 个真实、未修复、影响后续任务的系统缺陷：DEBT0010（gate_commands 键解析脚本未排除 _timeout_seconds 后缀，4 脚本同类）+ DEBT0011（SELF-GATE 审查文件纯日期命名，跨任务同日覆盖历史记录）+ DEBT0012（check-protocol-consistency --strict 与 && 链路短路，P5 链路永远 exit 2）+ RM-AG0028/DEBT0015（env_constraints 声明性字段无执行/gate 绑定，deploy 类动作只注入不强制）。DEBT0013（P8 时序文档注）已在 PR #166 修复、DEBT0009（决策备忘非债）已单独关闭，不在本任务范围"

issues:
  - "DEBT0010 gate_commands 键解析脚本未排除 _timeout_seconds 后缀（4 处同类，medium）：agate-read-gate-commands.py L31 / agate-gate-missing-cmds.py L20 / agate-gate-p5-count.py L23 / agate-read-p5-commands.py L29 均只排除 _formatter、未排除 _timeout_seconds。TAG0016 三阶段实测复现：P2 报假'命令不存在' WARNING（check-gate.py 把整数值当待核实命令 token）；P3 check-tdd-red.py 对真红灯误报 exit 1（A 类，bash -c '120' → 127）；P5 报假'1 主命令 + 1 辅助命令'。影响：任何任务按 P2 卡片「{key}_timeout_seconds 字段规则」正常声明后，P2/P3/P5 阶段 gate 判定被同一类解析缺陷误导。修复=4 脚本判据统一补 key.endswith('_timeout_seconds')（与 _formatter 并列，可抽 agate_common.py 共享判据函数防第五处）+ 回归用例覆盖 P2/P3/P5 三场景"
  - "DEBT0011 SELF-GATE 审查文件纯日期命名跨任务覆盖（medium）：SELF-GATE.md 派发模板规定 agate-alignment-review-{date}.md / agate-alignment-{date}-{NN}.progress.md（只含日期，无任务标识）。TAG0016 实测：2026-08-19 当天 TAG0015 与 TAG0016 各自触发审查，生成同名文件，TAG0016 覆盖 TAG0015 已提交历史（git diff 实证），git 无法区分'合法覆盖草稿'与'意外破坏历史记录'。修复=命名模板补任务标识（agate-alignment-review-{date}-{task_id}.md）+ protocol-alignment-review 角色文件提示 subagent 用 Write 前先检查目标路径是否已存在、确认是否同一任务复核轮（可覆盖）还是别的任务遗留（不可覆盖，改用带任务标识新文件名）"
  - "DEBT0012 check-protocol-consistency.py --strict 与 && 链路永久短路（medium）：main() 末尾 if rep.errors: return 1 / if rep.warnings and args.strict: return 2 / return 0——--strict 模式'WARNING-only 也 exit 2' 与 gate_commands.P5 的 && 串联组合（pytest && consistency --strict && count-tests.sh），在存量 WARNING 未清零（当前 314 条，全为历史叙事文件死链）时，链路第 2 步恒非 0 短路第 3 步（TAG0016 P5 实跑 count-tests.sh 未执行到）；历史验证方法盲区（command | tail 掩盖真实 exit code）使该缺陷长期存在未被发现（本任务 P4 也踩过同一陷阱）。修复=二选一或都做：(a) P2 卡片 gate_commands 声明示例 + 协议文档不再推荐 --strict 放 && 链路中间，改三条独立命令分别判定；(b) check-protocol-consistency.py 新增 --strict-errors-only 模式（仅 ERROR 时非 0，WARNING 通过打印提示），保留现有 --strict（WARNING-only 也非 0）供人工主动选用不作为 && 链路默认组成"
  - "DEBT0014（计划，2026-08-19 用户跨项目反馈汇入）Windows Store python3 占位符命中 hook 探测循环导致 Windows 用户 commit 阻断（medium，AGENTS.md/CLAUDE.md 已知但 protocol 层未处理）：agate/scripts/pre-commit-gate.sh 第 11-13 行（及 commit-msg-self-gate.sh / pre-push-gate.sh 同结构薄壳）探测循环 `for c in python3 python` 中 `command -v python3` 能命中 WindowsApps 目录下的 Store 占位符 python3.exe（它是真实 exe stub），但 exec 时 Store 占位符非交互模式直接 exit 49 → hook 走 fail-closed 分支阻断 commit。Windows 用户每次都踩的坑——目前 workaround 是手动复制 python.exe 为 python3.exe 或项目脚本用 python 命令，脆弱且不可重现。修复=①3 薄壳探测循环增强：探测后做可执行性小测试（exit 49 / 含 Microsoft Store 字符串 → skip 该候选）或加 `AGATE_PYTHON` 环境变量优先直接接受显式指定 ②agate/platform-notes.md「已知限制」表新增一条 + 「Windows 原生」章节加 Store 占位符说明 + AGATE_PYTHON 机制文档 ③agate/AGENTS.md「升级 agate」段同步一句。P1 派发时需实测薄壳代码并定 Store 占位符识别阈值（exit 49 / stderr 内容 / Python313 路径是否在 WindowsApps 之前）"
  - "RM-AG0028/DEBT0015 env_constraints 声明性字段无执行/gate 绑定（medium，TQC0001 跨项目反馈）：env_constraints 是 P0-brief/P2-design 的声明性字段——协议所有引用都是'确认/细化 + 注入 subagent 上下文'（agate-extract-context.py L107-109 只做注入；P0/P1/P2/P4 卡片当输入/约束读；dispatch-prompt 注入约束节），没有任何 gate/脚本消费 env_constraints.deploy 之类字段做执行性校验。实证：TQC0001（Qt 计算器）P2 声明 env_constraints.deploy（windeployqt 构建 dist），全流程从未主动执行，用户双击 exe 报缺 DLL 才补做。修复=①明确 env_constraints 字段语义边界：声明性（信息注入）vs 执行性（gate 强制）——P2 卡片/architect 角色说明'执行性约束必须落到 gate_commands 或 P4/P8 明确 checklist' ②UI 任务 P4 后应构建 dist：P4 卡片「自查≠gate」节补'UI 任务 P4 后构建 dist（windeployqt 等）'或 P8 gate 加 dist 产物存在性检查 ③可选：check-gate.py 或新脚本校验 gate_commands 声明了 deploy/构建命令时 P4/P8 产出物存在"

known_risks:
  - "改动域 = gate 脚本（agate/scripts/*.py）+ SELF-GATE.md + P2 卡片 → 触发 SELF-GATE + commit-msg WARNING（需 self-gate-review 标注）"
  - "DEBT0010 修复会触碰 check-tdd-red.py 判定语义核心——回归测试必须覆盖'P3 声明 timeout_seconds 时真红灯仍正确判定'，不能把修复做成放宽判定"
  - "DEBT0010 抽共享判据函数是建议非强制——若 4 处判据上下文差异大（如 p5-count 用 regex 而非 endswith），可保持各自内联修复 + grep 断言审计测试防第五处"
  - "DEBT0012 的 (b) 方案加新 CLI 模式影响 check-protocol-consistency.py 的 AI4 接口——需要与既有 --strict/默认模式测试覆盖区分（0 ERROR=0、WARNING-only=2(默认)/0(--strict-errors-only)/2(--strict)）"
  - "DEBT0011 需一并检查存量已生成的 docs/reviews/ 文件是否有历史同名覆盖（TAG0016 已手工恢复一次，确认无其他遗留）"
  - "【强制要求】同类扫描 + 影响面梳理：P1 必须 grep 全仓 _timeout_seconds（找第五处遗漏/消费点）、grep agate-alignment-review-{date}（找同类命名引用）、grep --strict 在 gate_commands/协议文档的所有使用点。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/"