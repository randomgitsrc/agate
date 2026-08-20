---
review_date: 2026-08-20
reviewer: protocol-alignment-review
change_summary: TAG0017 协议工具链修复批（DEBT0010/11/12/14/15）——4 处 gate_commands 解析脚本改用共享判据函数 is_gate_meta_key（含修复 _timeout_seconds 遗漏）；check-protocol-consistency.py 新增 --strict-errors-only 互斥模式并配套文档指引，消除 `&&` 链路短路反模式；SELF-GATE.md 留痕/成果文件命名补 {task_id} 防同日多任务互相覆盖，并给 protocol-alignment-review.md 增补 Write 前防误覆盖检查；3 个 hook 薄壳探测循环支持 AGATE_PYTHON 显式覆盖 + 候选可执行性小测试，规避 Windows Store python3.exe 占位符现象。
files_changed: [AGENTS.md, SELF-GATE.md, agate/assets/execution-roles/architect.md, agate/assets/review-roles/protocol-alignment-review.md, agate/phase-cards/P2-design.md, agate/phase-cards/P4-implementation.md, agate/platform-notes.md, agate/scripts/agate-gate-missing-cmds.py, agate/scripts/agate-gate-p5-count.py, agate/scripts/agate-read-gate-commands.py, agate/scripts/agate-read-p5-commands.py, agate/scripts/agate_common.py, agate/scripts/check-protocol-consistency.py, agate/scripts/commit-msg-self-gate.sh, agate/scripts/pre-commit-gate.sh, agate/scripts/pre-push-gate.sh]
---

# 协议-脚本对齐审查

## 意图分析

本次变更的意图：消除 gate 工具链里三类"改一处忘改一处"的结构性弱点——(1) 4 处独立实现的 `gate_commands` 元信息 key 判据（`_formatter`/`_timeout_seconds`）散落各脚本、口径不一致（`agate-gate-p5-count.py` 此前遗漏 `_timeout_seconds` 排除，是一个潜藏 bug）；(2) `--strict` 校验被写进 `&&` 链路中间会被前序命令短路、问题被静默掩盖；(3) self-gate 审查的留痕/成果文件命名不含 `{task_id}`，同日多任务派发会互相覆盖审查记录；(4) Windows Store 的 `python3.exe` 占位符可执行文件让 hook 薄壳的 `command -v` 探测误判为"找到可用 python"。四条修复分别是：抽共享判据函数、加互斥严格模式、命名模板补 `task_id` + Write 前存在性检查、探测循环加可执行性小测试 + `AGATE_PYTHON` 显式逃生舱。都是"让声明的规则不会被静默架空"这一条主线的不同侧面。

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED（1 处：`agate/scripts/README.md` 未同步 `--strict-errors-only`） |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED（A3b：同上，反向传播遗漏 `agate/scripts/README.md`） |
| A4 | 测试覆盖 | ALIGNED（附实跑：1011 passed, 2 skipped, 0 failed, 89.29s） |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（`agate/phase-cards/P2-design.md:148-152`，新增节）：
> `env_constraints` 是**声明性字段**——它只做信息确认/注入……本身不会被自动执行，也没有任何 gate 脚本会去校验……真正被执行的机制是 `gate_commands`。

**脚本实现**：无对应校验脚本改动（本条是纯文档边界澄清，DEBT0015 明确判定"不新增自动化校验"是刻意选择，见任务 P2-design.md §2.3 候选比较）。文档表述与代码现状（`env_constraints` 确实无任何 gate 脚本读取/校验）一致。

**结论**：ALIGNED

---

**文档声明**（`agate/phase-cards/P2-design.md:154-172`，`--strict` 反模式节）：
> `gate_commands` 的每个 key 声明的是一条完整命令，若用 `&&` 拼接会有短路问题……`--strict-errors-only`（仅 ERROR 判失败）适合日常任务默认使用；`--strict`（WARNING-only 也判失败）保留给专门做 WARNING 债务清理的任务主动选用。

**脚本实现**（`agate/scripts/check-protocol-consistency.py:1078-1141`）：
```python
strict_group = ap.add_mutually_exclusive_group()
strict_group.add_argument("--strict", action="store_true", ...)
strict_group.add_argument("--strict-errors-only", action="store_true", ...)
...
if rep.errors:
    return 1
if args.strict_errors_only:
    return 0
if rep.warnings and args.strict:
    return 2
return 0
```
`--strict-errors-only` 在有 ERROR 时仍返回 1（不改变 ERROR 语义），仅在 ERROR=0 时提前 `return 0`（跳过 `--strict` 的 WARNING 判定分支）。与文档描述的"仅 ERROR 判失败"语义完全一致；互斥组保证两个 flag 不会被同时传入。

**结论**：ALIGNED

---

**文档声明**（`agate/scripts/agate_common.py:78-85`，`is_gate_meta_key` docstring）：
> 仅精确匹配两个已知固定后缀 `_formatter` / `_timeout_seconds`，不做通配/正则宽松匹配……供 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-gate-p5-count.py` / `agate-read-p5-commands.py` 共用。

**脚本实现**：`return key.endswith(("_formatter", "_timeout_seconds"))`（`agate_common.py:86`），4 个调用方分别在 `agate-read-gate-commands.py:33`、`agate-gate-missing-cmds.py:22`、`agate-gate-p5-count.py:25`、`agate-read-p5-commands.py:31` 精确替换旧的 `key.endswith("_formatter")` 判据为 `is_gate_meta_key(key)`。逐一核对 4 处调用点均已切换，且 `agate-gate-missing-cmds.py` 保留了独立的 `project_module` 精确匹配分支（未强行并入共享函数），与任务 P2-design.md §1.3 R7 的设计决策一致。

**结论**：ALIGNED

---

**文档声明**（`agate/platform-notes.md` 新增行 + `AGENTS.md:41`）：
> `AGATE_PYTHON` 环境变量显式覆盖（非空时直接使用该路径，跳过探测循环），未设置时逐候选做可执行性小测试后再采用。

**脚本实现**（`pre-commit-gate.sh`/`commit-msg-self-gate.sh`/`pre-push-gate.sh`，3 文件逻辑逐字一致）：
```bash
if [ -n "${AGATE_PYTHON:-}" ]; then
    PY="$AGATE_PYTHON"
else
    for c in python3 python; do
        command -v "$c" >/dev/null 2>&1 || continue
        "$c" -c "" >/dev/null 2>&1 || continue
        PY="$c"; break
    done
fi
```
与文档描述完全一致：`AGATE_PYTHON` 非空即直接使用、跳过探测循环；否则遍历候选并对每个候选做 `-c ""` 可执行性小测试，非零退出则跳过继续下一候选。`platform-notes.md` 新增的"DEBT0014 验证边界说明"段落明确声明"未在真实 Windows 环境下触发过 Store 占位符场景本身……不代表已在 Windows 环境中复现并验证通过"，未夸大验证程度，符合 P1 `verification_env` 诚实性约束。

**结论**：ALIGNED

### A2: 脚本→文档对齐

**脚本实现**（`agate/scripts/check-protocol-consistency.py`，本次新增 `--strict-errors-only`）：argparse 新增了这个用户可见的 CLI flag，且改变了脚本的对外行为契约（3 种模式：默认 / `--strict` / `--strict-errors-only`）。

**文档声明**（`agate/scripts/README.md:163-178`，「用法」+ 退出码节，**本次未改动**）：
```
python3 agate/scripts/check-protocol-consistency.py
# WARNING 也判失败（更严格）
python3 agate/scripts/check-protocol-consistency.py --strict
...
退出码：`0` = 无 ERROR；`1` = 有 ERROR；`2` = 仅 WARNING 且加了 `--strict`。
```
该文件是这个脚本对外的用法说明（CLI 用户/未来 maintainer 查阅入口），目前只字未提新增的 `--strict-errors-only`，也没有更新退出码表格（新 flag 下 WARNING-only 场景退出码是 `0` 而非 `2`，这一分支在文档里完全缺失）。`git diff HEAD --stat` 确认 `agate/scripts/README.md` 完全未出现在本次改动清单中。

**结论**：MISALIGNED
**差异**：`check-protocol-consistency.py` 的 CLI 契约新增了一个模式，`agate/scripts/README.md` 的「用法」示例块和退出码说明未同步，读者查该 README 会误以为该脚本只有 `--strict`/默认两种模式。
**建议**：在 `agate/scripts/README.md:163-178` 补一行 `--strict-errors-only` 用法示例（可直接引用 `phase-cards/P2-design.md` 里"日常默认用 `--strict-errors-only`，`--strict` 留给 WARNING 债务清理任务"的措辞），并把退出码表格扩展为区分三种模式（如"`0` = 无 ERROR（含 `--strict-errors-only` 下 WARNING-only 场景）；`1` = 有 ERROR；`2` = 仅 WARNING 且加了 `--strict`"）。属于纯文档补丁，不涉及代码/测试改动，修复成本低。

### A3: 一致性连锁 + 反向传播

**A3a（连锁）**：本次改动的协议文档层已做到位——`phase-cards/P2-design.md`（gate_commands 声明节）与 `assets/execution-roles/architect.md`（env_constraints 段落）两处保持字面一致的边界表述；`SELF-GATE.md` 内 3 处命名模板（文件约定表 + 两种审查模式的落盘小节）与 `protocol-alignment-review.md` 的人工验收清单最后一条同步更新为 `{task_id}` 格式，未发现遗漏的姊妹文件。

**A3b（反向传播，主动推断）**：依据本角色文件自带的"反向传播常见路径"表（`protocol-alignment-review.md:35`）：
> `agate/scripts/check-*.py`（脚本行为）| `agate/scripts/README.md`、`agate/tests/README.md`、对应角色文件

逐一核实：
- `agate/scripts/README.md` — **应传播但未传播**（即 A2 发现的同一个差异，此处从"反向传播检查"的角度复核确认）。
- `agate/tests/README.md` — 该文件的「脚本 → 测试文件」映射表本身在改动前就未收录 `check-protocol-consistency.py` 对应的 `test_check_protocol_consistency.py`（核实：该表现有条目里确实没有这一行），本次新增的 `test_agate_common.py`、`test_windows_python_probe_docs.py`、`test_self_gate_naming_docs.py`、`test_p2p4_boundary_docs.py` 等测试文件同样未被加入映射表。判定为**预先存在的表格未强制同步惯例**（该表本就不含所有测试文件的一一映射，"总计"栏注明"以 `count-tests.sh` 输出为准"），不是本次改动新引入的回归，不计入 MISALIGNED，但建议顺手补充（非阻断项）。
- 对应角色文件（`implementer.md`/`architect.md`）— `architect.md` 已在本次改动清单中同步（`env_constraints` 边界提醒），`implementer.md` 未涉及本次改动的字段/脚本行为，核实其现有内容未引用 `_formatter`/`is_gate_meta_key` 等实现细节，无需同步。
- `agate/state-machine.md` / `agate/dispatch-protocol.md` / `agate/WORKFLOW.md` — grep 全文确认无 `AGATE_PYTHON`/`strict-errors-only`/`is_gate_meta_key`/`_timeout_seconds` 相关引用，且这三份文档是概念层（阶段总览/gate 表/转移规则），不下沉到脚本参数级实现细节，**本就不该被本次改动触及**，核实结果正确未改动。

**结论**：MISALIGNED（等同 A2 发现的同一处差异——`agate/scripts/README.md` 遗漏），其余反向传播路径均已核实到位。
**差异 + 建议**：同 A2。

### A4: 测试覆盖

新增/复用测试：
- `agate/tests/unit/test_agate_common.py`（新文件，`is_gate_meta_key` 单测，3 组参数化用例覆盖 `_formatter` 后缀 true / `_timeout_seconds` 后缀 true / 普通 key 及"看似相似但非完整后缀"的 `P3_timeout` false——精确覆盖 P1 R3 风险条目"防止判据被放宽为通配匹配"的边界）。
- `agate/tests/unit/test_check_protocol_consistency.py:512-620`（新增 3 用例：0 ERROR+0 WARNING / 0 ERROR+N WARNING / N ERROR，分别验证 `--strict-errors-only` 的 exit 0/0/1，覆盖三种边界场景）。
- `agate/tests/integration/test_pre_commit_hook.py:1443-1487`（`test_bdd_10_probe_skips_unexecutable_candidate` + `test_bdd_11_agate_python_explicit_override_skips_probe_loop`，分别覆盖"候选不可执行时跳过"和"AGATE_PYTHON 显式覆盖跳过探测循环"两条新逻辑分支）。
- `test_windows_python_probe_docs.py` / `test_self_gate_naming_docs.py` / `test_p2p4_boundary_docs.py`（P4-implementation.md 提及的文档条文断言测试，未逐字重读全文但已确认这些文件存在且在 P3 红灯阶段先行落地）。

**实跑证据**（本次审查独立执行，非引用 implementer 自报）：
```
$ python3 -m pytest agate/tests/ -q --tb=short
1011 passed, 2 skipped in 89.29s (0:01:29)
```
（首次全量跑出现过 1 次 `test_check_pruning.py` 3 个用例失败：`test_p2_6e_prune_p7_coupling_checklist_exit_0`、`test_p2_52_yaml_list_phases_exit_0`、`test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0`。已排查：① `check-pruning.py` 及其测试文件均**不在本次 diff 改动范围内**（`git status`/`git diff HEAD` 确认零改动）；② 单独跑该测试文件 4 次（含 `-k` 过滤跑相关用例、跑全文件、`-x` 跑全文件）全部 29/29 通过；③ 再次执行两次全量 `pytest agate/tests/` 均为 `1011 passed, 2 skipped`、零失败，与 implementer 自报数字完全一致。判定为一次性环境抖动（`_staged_source_count` 依赖真实进程 cwd 下的 `git diff --cached`，在全量套件跑动过程中可能受本机并发操作影响出现窗口期误判，属于测试设计对真实仓库 git 状态的隐性依赖，与本任务无关的既有脆弱性），不影响本次改动的测试覆盖结论。)

`python3 agate/scripts/check-protocol-consistency.py` 独立验证：0 ERROR，314 WARNING（与 baseline 一致）；`--strict-errors-only` 同为 exit 0。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

- `is_gate_meta_key` 把 `agate-gate-p5-count.py` 的排除口径从"仅 `_formatter`"修正为"`_formatter` 或 `_timeout_seconds`"——这是修复了一个此前存在的潜藏 bug（声明了 `P5_timeout_seconds` 字段的任务，此前会被 `agate-gate-p5-count.py` 误计入 aux 命令数）。已确认 `agate/state-machine.md`/`agate/dispatch-protocol.md` 均无依赖该旧计数口径的硬编码表述，修正不破坏协议层文档的既有断言。
- `AGATE_PYTHON` 为纯 opt-in 新增分支，未设置时走的探测循环对正常安装的 `python3`/`python`（`-c ""` 秒退出 0）无行为变化，向后兼容确认。
- `--strict-errors-only` 是新增互斥模式，不修改 `--strict` 既有语义，向后兼容确认（任务 P2-design.md §1.3 已有同样论证，本次独立复核认可）。
- CHANGELOG.md 本次未标注改动——核对任务背景说明"P8 阶段会处理"，且 `agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md` 影响面梳理节「不改什么」明确把 `CHANGELOG.md`/`README.md` version badge 列为 P8 既有流程范围、P2/P4 有意不预先处理，未发现遗漏。

**结论**：ALIGNED

### A6: 锚点表覆盖

本次改动均为对**既有** gate 脚本（`agate_common.py`/4 个解析脚本/`check-protocol-consistency.py`/3 个 hook 薄壳）的内部逻辑修改，未新增任何 gate 脚本文件，因此 `check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS`（`check-protocol-consistency.py:480`）及其 `check_anchor_coverage()`（新脚本未纳入锚点表检测，`check-protocol-consistency.py:730-762`）均无需新增条目。独立执行 `check-protocol-consistency.py` 确认 0 ERROR、314 WARNING，与任务自报的"存量基线未新增"完全一致，未出现新的 `CHECK9-coverage` WARNING，佐证锚点表覆盖无遗漏。

**结论**：ALIGNED

### A7: 设计原则一致性

- **ADR-002（可判定性——gate 门槛机器可判定）**：`--strict-errors-only` 仍是纯 exit code 判定（0/1），未引入任何需要人工解读的模糊状态，符合"机器可判定"原则。
- **ADR-003（最小约定——不绑定技术栈）**：`gate_commands` 仍由项目在 P2 自行声明命令，本次改动只是给 `check-protocol-consistency.py` 自身增加一个可选 flag，未改变"agate 不硬编码技术栈命令"的边界。
- **ADR-004（安全网分层——hook 兜底，主动验主流程）**：`AGATE_PYTHON` + 可执行性探测强化的是三层防线里的第 2 层（pre-commit hook 兜底）本身的健壮性——让"hook 因环境异常而静默失效/走错解释器"这条隐患变小，没有改变三层防线各自的职责边界，与 ADR-004 精神一致（强化兜底层可靠性，不是替代主流程）。

**结论**：ALIGNED

## 已知偏离核对

已查 `agate-workspace/tasks/TAG0017-toolchain-fixes/P4-implementation.md`：本任务无 `[DESIGN_GAP]`/`[SCOPE+]`/`[CLARIFY]` 记录（P4 正文明确写"5 个批次的进度记录均未出现……本次实现无 DESIGN_GAP/SCOP+/CLARIFY"）。本次审查发现的 A2/A3b MISALIGNED（`agate/scripts/README.md` 遗漏）**未见于**该任务的任何 P4/P4-review 记录，不属于已被 P7/P4-review 核实接受的已知偏离，按新发现的 MISALIGNED 正常处理，需修复。

## 闭环状态

- MISALIGNED 1 处（A2/A3b 同源，`agate/scripts/README.md` 遗漏 `--strict-errors-only`）**已于复评（retry round 1）确认修复，转为 ALIGNED**——详见文末「## 复评（retry round 1）」节。
- A1/A2/A3/A4/A5/A6/A7 现全部 ALIGNED。
- 无 NEEDS_HUMAN_REVIEW 项。
- 闭环完成，可 commit。

## 复评（retry round 1）

**复核对象**：上一轮 A2/A3b 判定的唯一 MISALIGNED——`agate/scripts/README.md` 未同步 `check-protocol-consistency.py` 新增的 `--strict-errors-only` 模式。

**implementer 修复内容**（`agate/scripts/README.md:163-186`）：
- 「用法」代码块新增一行示例：`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`，注释「仅 ERROR 判失败，WARNING 不视为失败（与 --strict 互斥）」（README.md:172-173）。
- 新增一行选用指引：「日常任务默认用 `--strict-errors-only`；`--strict` 留给专门做 WARNING 债务清理的任务主动选用。两者互斥，不可同时传入。」（README.md:181）。
- 退出码说明由二态改写为区分三种模式的三条列表（README.md:183-186）：
  - `0` = 无 ERROR（默认模式、`--strict-errors-only` 下 WARNING-only 场景，以及 `--strict` 下 0 ERROR + 0 WARNING）
  - `1` = 有 ERROR（三种模式下均如此，`--strict-errors-only` 不改变 ERROR 语义）
  - `2` = 仅 WARNING 且加了 `--strict`（默认模式和 `--strict-errors-only` 下不会返回此码）

**代码核对**（`agate/scripts/check-protocol-consistency.py:1079-1141`）：
- `--strict` 与 `--strict-errors-only` 确认通过 `ap.add_mutually_exclusive_group()`（:1079）互斥登记，argparse 层面不可同时传入，与 README 「两者互斥，不可同时传入」字面一致。
- `main()` 尾部实际分支逻辑（:1135-1141）：
  ```python
  if rep.errors:
      return 1
  if args.strict_errors_only:
      return 0
  if rep.warnings and args.strict:
      return 2
  return 0
  ```
  逐条对照 README 新增的三条退出码说明：
  - 有 ERROR → 恒定 `return 1`，三种模式（默认/`--strict`/`--strict-errors-only`）都会先命中这一行，与 README「三种模式下均如此」完全一致。
  - 无 ERROR + `--strict-errors-only` → 命中 `if args.strict_errors_only: return 0`，即便有 WARNING 也是 `0`，与 README「`--strict-errors-only` 下 WARNING-only 场景」→ `0` 一致。
  - 无 ERROR + 默认模式（两个 flag 都未传）→ `args.strict_errors_only` 为 False、`args.strict` 为 False，跳过中间两个分支，落到末尾 `return 0`（不论有无 WARNING），与 README「默认模式」→ `0` 一致，且默认模式确实不会返回 `2`（因为 `args.strict` 恒 False），与 README「默认模式…不会返回此码」一致。
  - 无 ERROR + `--strict` + 有 WARNING → 命中 `if rep.warnings and args.strict: return 2`，与 README「`2` = 仅 WARNING 且加了 `--strict`」一致。
  - 无 ERROR + `--strict` + 无 WARNING → 落到末尾 `return 0`，与 README「`--strict` 下 0 ERROR + 0 WARNING」→ `0` 一致。

  六种组合全部逐一核对，README 新增文字与代码实际分支语义完全对应，未发现字面或语义偏差。

**残留观察（非阻断，不计入本轮 MISALIGNED）**：脚本自身模块 docstring（`check-protocol-consistency.py:23-28`，`退出码：0 = 全过；1 = 有 ERROR；2 = 仅有 WARNING…` 及用法示例）仍是旧版二态措辞、未提及 `--strict-errors-only`。这份 docstring 不是本轮复核范围（原 A2/A3b 判定的差异对象是 `agate/scripts/README.md`，不是脚本内部 docstring），且属于代码内部注释而非独立协议文档，按角色审查原则严格来说可再开一条新的 A2 观察，但鉴于：① 上一轮报告的 MISALIGNED 明确限定为 `agate/scripts/README.md`；② README.md 才是本脚本对外的用法说明入口（docstring 是给直接读源码的人看的辅助信息，二者不是同一权威来源的两份拷贝，不属于本角色文件「反向传播路径表」列出的必须同步对（表中只列了 `agate/scripts/README.md`/`agate/tests/README.md`/角色文件）；不作为本轮 MISALIGNED 计入，仅记录供后续任务参考。

**A2 复核结论**：ALIGNED（原差异已消除，README 与脚本实际 CLI 契约/退出码语义完全对应）。
**A3b 复核结论**：ALIGNED（`agate/scripts/README.md` 反向传播缺口已补齐，「脚本行为 → README」路径核实到位）。

**复评闭环状态**：本任务 A1-A7 全部 ALIGNED，无遗留 MISALIGNED，无待确认的 NEEDS_HUMAN_REVIEW，可 commit。
