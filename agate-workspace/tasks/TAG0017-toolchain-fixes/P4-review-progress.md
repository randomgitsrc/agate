# P4 Review Progress Log (TAG0017)

## 文件清单核对
git diff --stat 实测 16 个改动文件（脚本7 + phase-cards2 + assets2 + SELF-GATE.md + platform-notes.md + AGENTS.md + check-protocol-consistency.py 单算），与 P2-design.md §6 dispatch_plan 声明的 5 批文件边界逐一核对：
- fg1-parser-scripts: agate_common.py + 4 个 agate-*.py 解析脚本 —— 匹配
- fg1-doc-boundary: P2-design.md / architect.md / P4-implementation.md —— 匹配
- fg2-self-gate-naming: SELF-GATE.md / protocol-alignment-review.md —— 匹配
- fg3-strict-mode-code: check-protocol-consistency.py —— 匹配
- fg4-windows-python-probe: 3 hook sh + platform-notes.md + AGENTS.md —— 匹配
结论：5 批文件集合两两不相交，与声明一致，无遗漏无越界。
[INFO] dispatch-context 描述"14 个改动文件"，实测 diff --stat 为 16 个（非 test 目录范围内）。计数口径出入（可能未含全部或统计方式不同），非阻塞，仅记录。

## is_gate_meta_key 核查（DEBT0010 / BDD-2 红灯语义）
agate_common.py 新增：
  def is_gate_meta_key(key): return key.endswith(("_formatter", "_timeout_seconds"))
仅精确匹配两个固定后缀，无通配/正则宽松匹配。4 个消费方（agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py / agate-read-p5-commands.py）grep 确认原 `.endswith("_formatter")` 判断已全部替换为 `is_gate_meta_key(key)`，无遗漏未切换点。
结论：PASS，未放宽 TDD 红灯判定语义。
[INFO minor] agate-gate-p5-count.py 顶部 docstring 注释（L6）仍只写"排除 `_formatter` 键"，未同步提及新排除的 `_timeout_seconds`，文档性遗漏（不影响行为）。

## check-protocol-consistency.py --strict-errors-only 核查
新增 --strict-errors-only 与 --strict 用 mutually_exclusive_group 互斥。exit 逻辑：
  if rep.errors: return 1          # ERROR 始终优先返回 1，两种 strict 模式下均不吞错
  if args.strict_errors_only: return 0
  if rep.warnings and args.strict: return 2
  return 0
结论：PASS。ERROR 场景在两个分支之前统一拦截，--strict-errors-only 未吞掉 ERROR；WARNING-only 场景下 --strict-errors-only 返回 0（不短路后续 && 链路），符合 BDD-9。

## 3 个 hook 薄壳探测循环核查（DEBT0014）
pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh 三份 diff 逐字比对完全一致（含注释）。
新增逻辑：
  if [ -n "${AGATE_PYTHON:-}" ]; then PY="$AGATE_PYTHON"
  else for c in python3 python; do command -v "$c" ... || continue; "$c" -c "" ... || continue; PY="$c"; break; done
  fi
- AGATE_PYTHON 显式覆盖跳过探测循环 —— 符合 BDD-11，且未对显式路径做可执行性校验（与 BDD-11 Given/When/Then 原文一致：显式路径应直接使用不做探测）。
- 可执行性小测试用 "$c" -c "" 真实起一次解释器进程判定 exit code，非 command -v 命中即用，可正确跳过 Windows Store 占位符（exit 49）继续探测下一候选 —— 符合 BDD-10。
- TOCTOU 关注点：小测试到 exec 之间存在理论竞态窗口（另一进程替换该路径下的可执行文件），但该窗口在原有实现（command -v 后直接 exec）中同样存在，本次改动未扩大风险面，属已有可接受的 shell 脚本固有模式，非本次引入的新增回归。
- set -u 存在，`${AGATE_PYTHON:-}` 使用安全展开，无 unbound variable 风险。
结论：PASS。

## SELF-GATE.md / protocol-alignment-review.md 核查（DEBT0011，BDD-7/8）
命名模板从 `{date}-{NN}` / `{date}` 改为 `{date}-{task_id}-{NN}` / `{date}-{task_id}`，4 处出现点（首次+重试两套流程 × 留痕/成果各一）全部同步更新，一致。
protocol-alignment-review.md 新增"Write 前检查"章节 + 人工验收清单勾选项，符合 BDD-8 的"同一任务复核轮可覆盖 / 别任务遗留不可覆盖"判断分支要求。
[MINOR] SELF-GATE.md L62 示例文案遗漏更新：`全量审查如果分批派发，每批用自己的留痕文件（如 agate-alignment-2026-07-01-01.progress.md、-02.progress.md）`——该示例文件名仍是旧格式（缺 `{task_id}` 片段），与同一文件 L53 刚定义的新命名模板 `{date}-{task_id}-{NN}` 不一致，是本次改动里唯一未同步的旧格式残留示例。

## platform-notes.md / AGENTS.md 诚实性边界核查（P0-brief 约束 3）
- AGENTS.md 新增句："...未在真实 Windows 环境实测" —— 明确排除"已实测通过"断言。
- platform-notes.md 新增表格行 + 独立 blockquote："DEBT0014 验证边界说明"，原文明确写"不代表已在 Windows 环境中复现并验证通过"。
结论：PASS，两处新增文字均无"已在 Windows 实测通过"类断言，诚实边界符合 P0-brief 约束 3。

## git diff HEAD 范围内看似"无测试文件改动"的排查
`git diff HEAD --stat`（不限定路径）与限定路径结果一致，只有 16 个非测试文件被 P4 改动。核实：P3 阶段（commit 02785e6，"TDD 红灯测试 41 用例覆盖 BDD-1~12"）已把全部回归/审计测试（含 `agate/tests/unit/test_gate_key_suffix_audit.py`，已确认存在）提前写入并 commit 到 HEAD，P4 只需让红灯转绿，不需要再新增/修改测试文件，故 `git diff HEAD` 范围内不出现测试文件改动，属正常 TDD 流程，非遗漏。

## [CRITICAL 候选] --strict vs --strict-errors-only：新 flag 未被自身实践/指引采用，示例仍会在已知 314-WARNING 基线下返回非零
- 实测：`python3 agate/scripts/check-protocol-consistency.py --strict` 在当前仓库真实基线（0 ERROR + 314 WARNING）下 EXIT=2（已验证）。
- `agate/phase-cards/P2-design.md` 新增的"`--strict` 反模式：不要放进 `&&` 链路中间"一节给出的"正确做法"示例：
  ```yaml
  gate_commands:
    P5: "pytest -q --tb=no"
    P5_consistency: "check-protocol-consistency.py --strict"
    P5_shellcheck: "shellcheck scripts/*.sh"
  ```
  该示例只解决了"短路"问题（拆成独立 key，避免 && 链路互相拖累），但示例本身选用的仍是 `--strict`（非本任务新增的 `--strict-errors-only`），在当前已知长期存在、短期不会清零的 314 条 WARNING 基线下，`P5_consistency` 这个独立 key 自身的执行结果仍然是非零退出——这正是 BDD-9 的 Given 前提场景。BDD-9 的 Then 只窄义要求"后续步骤不被短路跳过"，示例技术上满足了这个窄义要求，但若被未来任务照抄（P1 同类扫描已证实历史上 8 个任务确实会照抄这类示例），会让每个新任务的 `P5_consistency` 检查项永久红——这不是这次任务引入的新 bug，但错失了 `--strict-errors-only`（本任务专门为此新增的 flag）本该在这里被推荐使用的机会，示例本身对未来采用者是一个新的隐性陷阱。
- 更能坐实这一判断的证据：TAG0017 自己的 `agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md` §5 gate_commands 声明里，`P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict"` 也是原样用 `--strict`（未用新 flag），本任务"以身作则"的自我声明本身在当前仓库基线下也会令 `P5_consistency` 这一独立 key 返回 EXIT=2——这本应是 P4/P5 阶段主 Agent 已经会撞到的现象；dispatch-context 里的 `<objective_info>` 独立核验清单列出了 pytest/ruff/shellcheck/hook 逐字比对/check-platform-assumptions 核实，唯独没有列出 `check-protocol-consistency.py --strict`（或 `--strict-errors-only`）本身的核验结果，与该命令实测非零退出的情况吻合。
- 建议修复方向（列选项，不代为决策）：
  - 选项 A：`phase-cards/P2-design.md`"正确做法"示例把 `P5_consistency` 改用 `--strict-errors-only`（仅拦 ERROR），并在文档里补一句说明"`--strict` 保留给刻意要求 WARNING 清零的场景，日常推荐 `--strict-errors-only`"。
  - 选项 B：保留示例用 `--strict`，但在示例正下方明确加一句"当前 314 条历史 WARNING 基线下 `--strict` 会返回非零，若不打算清零存量 WARNING，请改用 `--strict-errors-only`"，避免读者误以为这个示例在当前仓库状态下能直接跑绿。
  - 选项 C：TAG0017 自己的 `agate-workspace/.../P2-design.md` §5 的 `P5_consistency` 声明同步改为 `--strict-errors-only`，让本任务自身的 P5 gate_commands 声明与"不应被已知 WARNING 基线阻塞"的实际诉求一致（当前用 `--strict` 与自身 314-WARNING 基线冲突）。
选项 A/B 属于 fg1-doc-boundary 批次落点文件（`phase-cards/P2-design.md`），选项 C 属于任务自身工作区文件（非评审范围内代码文件，但会影响本任务 P5 gate 是否能通过，需要主 Agent 关注）。

## 最终结论
status: rejected（1 个 CRITICAL：--strict vs --strict-errors-only 文档示例与 TAG0017 自身 gate_commands 声明未真正解决 WARNING 基线阻塞问题；2 个 INFO：docstring 未同步 + SELF-GATE.md 旧格式示例残留）。
产出文件：/home/kity/oclab/agate/.worktrees/agate-TAG0017/agate-workspace/tasks/TAG0017-toolchain-fixes/P4-review.md

## 复评轮 retry1 独立核验记录

1. `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only --root .`（独立一行捕获 exit code，未走管道）
   → EXIT=0，「仅有 314 个 WARNING，无 ERROR」。CRITICAL 已解决。
2. `python3 agate/scripts/check-protocol-consistency.py --root .`（默认模式）
   → EXIT=0，同为 314 WARNING + 0 ERROR，与修复前基线一致，未新增/减少 WARNING（YAML `#` 注释规避 CHECK 1 的处理方式验证有效）。
3. 文档核验：
   - agate/phase-cards/P2-design.md L169：`P5_consistency: "check-protocol-consistency.py --strict-errors-only"`，L172 新增推荐用法说明——已改用新 flag。
   - agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md L168-169：新增 YAML `#` 注释「P4 review 修正：...」+ `P5_consistency` 已改用 `--strict-errors-only`——已解决，且自身 gate_commands 与"不被历史 WARNING 阻塞"诉求一致。
   - 该文件其余处（L151/L157/L159）仍保留裸 `--strict` 措辞，核实为验收标准描述性文字/env_constraints 声明性说明，非 gate_commands 声明本体，不在本轮修复范围内，未构成新问题。
4. `agate/scripts/agate-gate-p5-count.py:6` docstring 已同步为「排除 `_formatter` / `_timeout_seconds` 元信息键」，与 `is_gate_meta_key` 实现一致。INFO 已解决。
5. `SELF-GATE.md:62` 示例文案已改为 `agate-alignment-2026-07-01-TAG0017-01.progress.md`、`-02.progress.md` 新格式，与 L53 命名模板 `{date}-{task_id}-{NN}` 一致。INFO 已解决。
