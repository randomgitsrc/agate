---
phase: P4
task_id: TAG0017-toolchain-fixes
type: implementation
parent: P2-design.md
trace_id: TAG0017-P4-20260820
status: draft
created: 2026-08-20
agent: implementer
---

implementation_dir: agate/

# P4 实现记录 — 协议工具链修复批（DEBT0010/11/12/14/15，5 批并行 + 1 轮 review-fix）

本任务覆盖 P1-requirements.md 的 12 条 BDD、4 个功能分组，按 P2-design.md §6 `dispatch_plan` 拆为 5 个互不重叠的并行批次（`fg1-parser-scripts`/`fg1-doc-boundary`/`fg2-self-gate-naming`/`fg3-strict-mode-code`/`fg4-windows-python-probe`），全部完成后经专家组 P4-review（`trace_id: TAG0017-P4review-20260820`）发现 1 CRITICAL + 2 INFO，修复后复评（`trace_id: TAG0017-P4review-20260820-retry1`）**approved**。

测试文件（`test_gate_key_suffix_audit.py`、各解析脚本回归用例、`test_check_protocol_consistency.py` 新增矩阵、`test_pre_commit_hook.py` BDD-10/11 段、`test_windows_python_probe_docs.py`、`test_self_gate_naming_docs.py`、`test_p2p4_boundary_docs.py` 等 41 条红灯用例）已在 P3（commit `02785e6`）先行落地，本阶段（P4）不改动测试文件，只做红转绿的实现改动。`git diff HEAD --stat` 核对：本次改动共 19 个文件，其中 17 个是 P2-design.md §1.1「改什么」表列明的代码/文档文件（全部覆盖，无遗漏），另外 2 个（`agate-workspace/tasks/TAG0017-toolchain-fixes/.state.yaml`、`agate-workspace/tasks/active-tasks.md`）是主 Agent 阶段推进的编排 bookkeeping 文件，不属于 implementer 产出范围，不在下文改动清单中列出。

## 批次 1：fg1-parser-scripts（DEBT0010 核心，BDD-1/2/3/4）

共享判据函数 + 4 处解析脚本改用该函数，消除"改一处忘改一处"的重复失误来源。

- `agate/scripts/agate_common.py`：新增 `is_gate_meta_key(key)`（`key.endswith(("_formatter", "_timeout_seconds"))`），供 4 个解析脚本复用。关联 BDD-1/2/3/4。
- `agate/scripts/agate-read-gate-commands.py`（L31 附近）：`elif key.startswith("P3") and not key.endswith("_formatter"):` 改为调用 `is_gate_meta_key(key)`。关联 BDD-2/4。
- `agate/scripts/agate-gate-missing-cmds.py`（L20 附近）：`if k.endswith("_formatter") or k == "project_module": continue` 改为 `if is_gate_meta_key(k) or k == "project_module": continue`（保留 `project_module` 精确匹配独立分支，不强行合并进 `is_gate_meta_key`，见 P2-design.md §1.3 R7）。关联 BDD-1/4。
- `agate/scripts/agate-gate-p5-count.py`（L23 附近）：`aux = [k for k in ... if not k.endswith("_formatter")]` 改为 `if not is_gate_meta_key(k)`。关联 BDD-3/4。
- `agate/scripts/agate-read-p5-commands.py`（L29 附近）：`if key.endswith("_formatter"): continue` 改为 `if is_gate_meta_key(key): continue`。关联 BDD-1/3/4。

自查：批次目标测试 71 passed；关联脚本回归测试（`capture_env_baseline`/`dispatch_context_warning`）16 passed，无回归。未修改测试文件。

## 批次 2：fg1-doc-boundary（DEBT0015 边界文档化 + DEBT0012 文档半，BDD-5/6/9）

与 `fg3-strict-mode-code` 同属 DEBT0012，但落点文件不同（本批次只改协议文档，代码改动在批次 4）；本批次因 P2-design.md §1.3 R1 与 DEBT0015 合并为一批，避免同一文件被两批各改一次。

- `agate/phase-cards/P2-design.md`「gate_commands 声明」节：新增两个三级小节——① `env_constraints` 声明性 vs `gate_commands` 执行性边界说明（BDD-5）；② `--strict` 不放 `&&` 链路中间的指引 + 反例（BDD-9）。
- `agate/assets/execution-roles/architect.md`：`env_constraints` 字段说明段落同步 BDD-5 边界提醒。
- `agate/phase-cards/P4-implementation.md`「自查≠gate」节：新增 UI/需构建任务需确认 dist 产物存在的提醒条目（BDD-6）。

自查：`python3 -m pytest agate/tests/unit/test_p2p4_boundary_docs.py -q` → 5 passed。未修改测试文件，未碰 `check-protocol-consistency.py`。`[PROD_NOT_TOUCHED]`。

## 批次 3：fg2-self-gate-naming（DEBT0011，BDD-7/8）

命名模板补 `{task_id}` 消除同日多任务互相覆盖风险 + Write 前存在性检查区分"同任务复核轮可覆盖"与"他任务遗留不可覆盖"。

- `SELF-GATE.md`：3 处命名模板改造——文件约定表（L53-54）：留痕文件 → `docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md`；成果文件 → `docs/reviews/agate-alignment-review-{date}-{task_id}.md`；变更触发模式模板、全量审查模式模板同步补 `{task_id}`。关联 BDD-7。
- `agate/assets/review-roles/protocol-alignment-review.md`：新增「Write 前检查：写入前防误覆盖（BDD-8）」段落（人工验收清单前），含"Write 前"/"目标路径"关键词，区分"同一任务复核轮可覆盖" vs "别的任务遗留不可覆盖"两分支；顺手同步人工验收清单最后一条的成果文件路径示例为含 `{task_id}` 的新模板。关联 BDD-7/8。

自查：`python3 -m pytest agate/tests/unit/test_self_gate_naming_docs.py -q` → 8 passed。未修改测试文件（已核实 `git status`）。`[PROD_NOT_TOUCHED]`。

## 批次 4：fg3-strict-mode-code（DEBT0012 代码半，BDD-9）

`check-protocol-consistency.py` 新增 `--strict-errors-only` 互斥模式，与文档指引（批次 2）形成双重防线，覆盖"独立 key 被下游重新拼接成 `&&` 链路"的残余风险。

- `agate/scripts/check-protocol-consistency.py`：新增 `add_mutually_exclusive_group()`（`--strict` / `--strict-errors-only` 互斥）；`main()` 尾部新增 `if args.strict_errors_only: return 0`（在 `rep.errors` 检查之后、`--strict` 检查之前）——仅 ERROR 非零（exit 1），WARNING-only 场景打印提示后 exit 0；既有 `--strict` 语义不变。原有"仅有 N 个 WARNING，无 ERROR。"提示分支与 `args.strict` 无关，天然复用，未改动。关联 BDD-9。

自查：`pytest -k strict_errors_only` → 3 passed；`pytest -k "not strict_errors_only"` → 24 passed（既有矩阵不受影响）。未碰 `phase-cards/P2-design.md`。

## 批次 5：fg4-windows-python-probe（DEBT0014，BDD-10/11/12）

3 个 hook 薄壳探测循环支持 `AGATE_PYTHON` 显式覆盖 + 候选可执行性小测试（通用 exit code 判据），默认路径即可跳过 Windows Store 占位符类不可执行候选，不要求用户先知道有环境变量才能绕过问题。

- `agate/scripts/pre-commit-gate.sh` / `agate/scripts/commit-msg-self-gate.sh` / `agate/scripts/pre-push-gate.sh`：探测循环片段改为——`AGATE_PYTHON` 非空时直接使用（跳过探测循环，BDD-11）；否则遍历候选，每个候选先做 `"$CAND" -c "" >/dev/null 2>&1` 可执行性小测试，非零则跳过继续下一候选（BDD-10）。3 文件改动内容逐字一致（md5 校验确认）。关联 BDD-10/11。
- `agate/platform-notes.md`「已知限制（Windows 原生）」表：新增 Store 占位符条目 + `AGATE_PYTHON` 验证边界说明段落（不含"已实测通过"断言，遵守 P1 verification_env 约束）。关联 BDD-12。
- `AGENTS.md`「Gate 脚本分层」节：追加一句 `AGATE_PYTHON` 说明（同样不含夸大断言）。关联 BDD-12。

自查：`test_pre_commit_hook.py`（bdd_10/bdd_11，6 用例）+ `test_windows_python_probe_docs.py`（5 用例，含 2 条诚实性负面断言）全绿，合计 59 passed，无回归。未修改测试文件（`git status` 未标记 `test_pre_commit_hook.py`/`test_windows_python_probe_docs.py` 为已改动）。

## review-fix 轮（P4-review CRITICAL/INFO 修复，retry round 1）

上轮 P4-review（`trace_id: TAG0017-P4review-20260820`）发现 1 个 CRITICAL + 2 个 INFO，修复内容：

**CRITICAL**：`gate_commands.P5_consistency` 声明使用裸 `--strict`（WARNING-only 也判失败），在当前 314 条既有 WARNING 存量基线下会阻塞 P5——不论是协议文档给出的"正确做法"范例，还是本任务自身的 `gate_commands` 声明，都需要改为 `--strict-errors-only`：
- `agate/phase-cards/P2-design.md`「gate_commands 声明」节"正确做法"示例（L165-172）：`P5_consistency` 由 `check-protocol-consistency.py --strict` 改为 `--strict-errors-only`，并新增一句推荐用法说明区分两个 flag 的适用场景（`--strict-errors-only` 日常默认；`--strict` 留给专门做 WARNING 债务清理的任务主动选用）。
- `agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md` §5 `gate_commands`（L164-171）：`P5_consistency` 同步改为 `--strict-errors-only`，紧邻上方新增一行 YAML `#` 注释说明修正原因（首次尝试用 HTML `<!-- -->` 注释会被 CHECK 1「YAML 代码块可解析」误判为无法解析，WARNING 数从 314 增至 315；改用 `#` 注释后验证仍为 314，问题已规避）。

**INFO ×2**：
- `agate/scripts/agate-gate-p5-count.py` docstring 第 6 行：`排除 _formatter 键` → `排除 _formatter / _timeout_seconds 元信息键`（核实 `agate_common.py:is_gate_meta_key` 已实现精确匹配两个后缀，本次仅同步文档描述，无行为变更）。
- `SELF-GATE.md` 第 62 行示例文案：`agate-alignment-2026-07-01-01.progress.md`/`-02.progress.md`（旧格式，缺 `{task_id}`）→ 补 `TAG0017`（新格式），与批次 3 命名模板改造保持一致，消除残留旧格式示例。

验证：`check-protocol-consistency.py --strict-errors-only --root .` → EXIT=0，「仅有 314 个 WARNING，无 ERROR」；默认模式同为 0 ERROR + 314 WARNING，与修复前历史基线完全一致，未新增/减少 WARNING；`python3 -m pytest agate/tests/ -q --tb=no` → `1011 passed, 2 skipped in 88.67s`，与基线一致，无回归。复评（`trace_id: TAG0017-P4review-20260820-retry1`）独立复核以上 4 处修复，全部确认已解决，**status: approved**。

## 无 DESIGN_GAP / SCOPE+ / CLARIFY

5 个批次的进度记录均未出现 `[DESIGN_GAP]`/`[SCOPE+]`/`[CLARIFY]` 标记（`fg4-windows-python-probe` 进度文件明确写"全部完成，无 DESIGN_GAP / SCOPE+ / CLARIFY 标记"；其余 4 个批次进度记录及 review-fix 轮进度记录中同样无此类标记）。本次实现无 DESIGN_GAP/SCOPE+/CLARIFY。

## 自查测试结果汇总（自查≠gate，非 P5 结论）

- 各批次目标测试子集分别全绿（见上文各批次自查小节）。
- review-fix 后全量：`python3 -m pytest agate/tests/ -q --tb=no` → **1011 passed, 2 skipped, 0 failed**。
- `python3 agate/scripts/check-protocol-consistency.py`（默认模式）→ 0 ERROR，314 WARNING（存量基线，未新增）。
- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → EXIT=0。
- ruff/shellcheck 全绿（`objective_info` 记录）。
