---
phase: P3
task_id: TAG0017-toolchain-fixes
type: test-cases
parent: P2-design.md
trace_id: TAG0017-P3-20260820
status: draft
created: 2026-08-20
agent: test-designer
test_code_dir: agate/tests
---

> 本文件由主 Agent 合并 5 个并行批次（P2 dispatch_plan `static-batch`，`parallel_limit: 5`）各自产出的 `P3-test-cases-{batch}.md`，批次间文件边界互不重叠（已在 P2 plan-eng-review 与本阶段主 Agent 独立核验中确认），BDD 编号全局唯一（BDD-1~12，无跳号无重复）。合并为轻量拼装（无跨批交叉修改），原始批次文件保留在任务目录供溯源。

## 批次总览

| 批次 | 覆盖 BDD | 测试文件 |
|------|---------|---------|
| fg1-parser-scripts | BDD-1/2/3/4 | `test_agate_common.py`（新建）、`test_gate_key_suffix_audit.py`（新建）、`test_check_tdd_red.py`（追加）、`test_agate_gate_missing_cmds.py`（追加）、`test_agate_gate_p5_count.py`（追加）、`test_agate_read_p5_commands.py`（追加） |
| fg1-doc-boundary | BDD-5/6/9（文档半） | `test_p2p4_boundary_docs.py`（新建） |
| fg2-self-gate-naming | BDD-7/8 | `test_self_gate_naming_docs.py`（新建） |
| fg3-strict-mode-code | BDD-9（代码半） | `test_check_protocol_consistency.py`（追加） |
| fg4-windows-python-probe | BDD-10/11/12 | `test_pre_commit_hook.py`（追加）、`test_windows_python_probe_docs.py`（新建） |

---

## 批次 fg1-parser-scripts（BDD-1/2/3/4）

test_code_dir: `agate/tests/unit`

### BDD-1: P2 阶段声明 `{key}_timeout_seconds` 不再被误判为待核实命令
- 测试用例：test_bdd_1_is_gate_meta_key_timeout_seconds_suffix_true（agate/tests/unit/test_agate_common.py，参数化 3 例，起始 L38）
- 测试用例：test_pyx_7_bdd_1_timeout_seconds_excluded_from_commands（agate/tests/unit/test_check_tdd_red.py:683）
- 测试用例：test_gmc_3_bdd_1_timeout_seconds_key_not_treated_as_missing_command（agate/tests/unit/test_agate_gate_missing_cmds.py:47）
- 测试用例：test_p5c_5_bdd_1_3_timeout_seconds_not_treated_as_command（agate/tests/unit/test_agate_read_p5_commands.py:18，同时覆盖 BDD-3）
- 预期行为：`gate_commands` 块中以 `_timeout_seconds` 结尾的 key（纯整数字符串值，无路径无 `=`）不被 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` 误判为待核实/待执行命令；`is_gate_meta_key(key)` 对该类 key 返回 True。
- 当前状态：红灯（AssertionError——4 个脚本均只排除 `_formatter` 后缀，`_timeout_seconds` 后缀 key 被当作真实命令处理，输出中出现 `"cmd": "120"` / `P5_timeout_seconds:120` 等假命令；`test_agate_common.py` 因 `is_gate_meta_key` 尚不存在，`from agate_common import is_gate_meta_key` 触发 ImportError，属项目内 import 失败的真实红灯）

### BDD-2: P3 阶段声明 timeout_seconds 时真红灯仍正确判定为 A 类失败
- 测试用例：test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class（agate/tests/unit/test_check_tdd_red.py:718）
- 测试用例：test_bdd_2_is_gate_meta_key_ordinary_key_false（agate/tests/unit/test_agate_common.py，参数化 5 例，起始 L48——含 `P3_timeout`「前缀相似但非完整 `_timeout_seconds` 后缀」的护栏用例，防止判据被放宽为通配匹配）
- 预期行为：P2-design.md 同时声明 `P3_timeout_seconds` 与真实会失败（SyntaxError，非超时）的 P3 测试命令时，`check-tdd-red.py` 判定结果仍为 A 类真实失败（exit 1），且 `_timeout_seconds` key 不应被当作独立命令实际执行（用 `TDD_CHECK:` 输出行数精确验证只有 1 条真实命令被判定，而非仅退出码——本场景下退出码在修复前后巧合地都是 1，无法单独作为红灯信号）。
- 当前状态：红灯（AssertionError：`result.output.count("TDD_CHECK:") == 1` 实测为 2——修复前 `check-tdd-red.py` 的 `main()` 会把 `P3_timeout_seconds: 120` 当作一条 `cmd="120"` 的命令真的 subprocess 执行一遍（`bash: 120: command not found`，exit 127），多打印一行 `TDD_CHECK: A-class error (test runner failed with exit code 127)`，证实这不只是展示问题，而是会执行一条虚假命令的功能性 bug）

### BDD-3: P5 阶段命令计数不含 timeout_seconds 声明键
- 测试用例：test_gpc_4_bdd_3_timeout_seconds_excluded_from_aux_count（agate/tests/unit/test_agate_gate_p5_count.py:54）
- 测试用例：test_p5c_5_bdd_1_3_timeout_seconds_not_treated_as_command（agate/tests/unit/test_agate_read_p5_commands.py:18，与 BDD-1 共用）
- 预期行为：`gate_commands` 块含一条 `P5:` 主命令 + 一条 `P5_timeout_seconds: 120` 时，`agate-gate-p5-count.py` 输出 "1 0"（1 主命令 + 0 辅助命令），`P5_timeout_seconds` 不计入辅助命令。
- 当前状态：红灯（AssertionError：实测输出 "1 1"——当前脚本 `aux = [... if not k.endswith("_formatter")]` 未排除 `_timeout_seconds`，误将其计入辅助命令）

### BDD-4: 同类遗漏拦截——防止未来新增第 5 处未排除 `_timeout_seconds` 的解析点
- 测试用例：test_bdd_4_formatter_excluding_scripts_also_exclude_timeout_seconds（agate/tests/unit/test_gate_key_suffix_audit.py，新建文件）
- 测试用例：test_bdd_4_is_gate_meta_key_formatter_suffix_true（agate/tests/unit/test_agate_common.py，参数化 4 例，起始 L28）
- 预期行为：结构性审计扫描 `agate/scripts/agate-*.py`，任何脚本对 gate_commands key 做了字面量 `"_formatter"` 后缀排除逻辑，必须同时含字面量 `"_timeout_seconds"` 或引用共享判据函数 `is_gate_meta_key`，否则判定为与 DEBT0010 同类的新遗漏点，令 pytest 整体失败。判据用带引号字面量（而非裸子串）精确定位"做 key 后缀排除逻辑"的脚本，已验证不会误伤仅调用 `resolve_formatter`/`run_test_with_formatter` 等公共函数名的间接消费方（如 `agate-capture-env-baseline.py`，P1 3.1 节判定为本次不处理范围）。
- 当前状态：红灯（AssertionError：offenders = ['agate-gate-missing-cmds.py', 'agate-gate-p5-count.py', 'agate-read-gate-commands.py', 'agate-read-p5-commands.py']——4 个目标脚本均命中 `_formatter` 排除逻辑但未命中 `_timeout_seconds`/`is_gate_meta_key`）

**未修改文件确认**：未修改 `agate/scripts/agate_common.py` 及 4 个 `agate-*.py` 解析脚本本身（P4 implementer 工作范围）。

---

## 批次 fg1-doc-boundary（BDD-5/6/9文档半）

test_code_dir: `agate/tests`
测试代码文件: `agate/tests/unit/test_p2p4_boundary_docs.py`（5 个测试用例，文档内容断言型，当前全部红灯）

说明：BDD-5/6/9(文档半) 判据是"文档能否找到结论"，不是"新增 gate 脚本执行绑定"（P2-design.md §1.3 R1）。三条 BDD 共享同一批次是因为 `phase-cards/P2-design.md`「gate_commands 声明」节是 BDD-5 与 BDD-9 文档半的共同落点文件（避免被拆到两批、同一文件改两次）。

### BDD-5: env_constraints 声明性字段与 gate_commands 执行机制的语义边界已文档化
- 测试用例：test_bdd_5_p2_design_gate_commands_section_states_env_constraints_is_declarative（从 `agate/phase-cards/P2-design.md`「## gate_commands 声明」节正文断言含 `env_constraints`/"声明性"/"执行机制"类结论表述）
- 测试用例：test_bdd_5_architect_role_states_env_constraints_is_declarative（从 `agate/assets/execution-roles/architect.md` 的 `env_constraints:` 字段段落断言同类结论）
- 当前状态：红灯（AssertionError，两处文档均未提及"声明性"边界说明）

### BDD-6: UI 类任务的部署类执行性约束在 P4 后有显式检查提醒
- 测试用例：test_bdd_6_p4_implementation_self_check_section_has_dist_build_reminder（`agate/phase-cards/P4-implementation.md`「## 自查≠gate」节断言含 UI/构建/dist 相关提醒）
- 当前状态：红灯（AssertionError，该节当前未提及 UI/构建/dist 字眼）

### BDD-9（文档半）: `--strict` 不放 `&&` 链路中间的协议指引 + 反例
> 代码半（`check-protocol-consistency.py --strict-errors-only`）由 fg3-strict-mode-code 批次负责
- 测试用例：test_bdd_9_p2_design_gate_commands_section_has_strict_anti_pattern_guidance（断言含 `--strict`/`&&`/"反模式"类指引措辞）
- 测试用例：test_bdd_9_p2_design_gate_commands_section_has_concrete_anti_pattern_example（断言含具体反例命令串）
- 当前状态：红灯（AssertionError，节内容当前完全未出现 `--strict`/`&&` 字样）

**自跑结果**：`python3 -m pytest agate/tests/unit/test_p2p4_boundary_docs.py -v` → 5 failed（全部 AssertionError，无假红灯来源）。

---

## 批次 fg2-self-gate-naming（BDD-7/8）

test_code_dir: `agate/tests/unit/test_self_gate_naming_docs.py`

被测文档：`SELF-GATE.md`（仓库根目录，无 `agate/` 前缀）L48-60/133/143/183/193；`agate/assets/review-roles/protocol-alignment-review.md` L100-119。

### BDD-7: 同日不同任务的 SELF-GATE 审查文件不再同名覆盖

| 测试函数 | 断言点 | 当前结果 |
|---|---|---|
| `test_bdd_7_self_gate_path_has_no_agate_prefix` | 前置校验：`SELF-GATE.md` 确实在仓库根目录 | PASS（路径前置校验，非本批次待改动内容） |
| `test_bdd_7_file_type_table_progress_filename_has_task_id` | 文件约定表留痕文件命名模板含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_file_type_table_result_filename_has_task_id` | 文件约定表成果文件命名模板含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_change_triggered_template_naming_has_task_id` | 变更触发模式派发模板命名含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_full_review_template_naming_has_task_id` | 全量审查模式派发模板命名含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_naming_template_produces_distinct_filenames_for_different_task_ids` | 纯字符串格式化逻辑自证：补上 `{task_id}` 后两个不同 task_id 生成的文件名确实不同 | PASS（逻辑自证，非文档状态断言） |

### BDD-8: subagent 写入前检查目标路径存在性，避免误覆盖历史记录

| 测试函数 | 断言点 | 当前结果 |
|---|---|---|
| `test_bdd_8_protocol_alignment_review_has_write_precheck_logic` | `protocol-alignment-review.md` 含 "Write 前"/"目标路径" 关键词说明 | **FAIL（红灯）** |
| `test_bdd_8_write_precheck_distinguishes_same_task_vs_other_task` | 区分"同一任务可覆盖"vs"不可覆盖"两分支说明 | **FAIL（红灯）** |

**红灯确认**：8 个测试，6 FAILED（真实 AssertionError）、2 PASSED（路径前置校验 + 纯逻辑自证，按设计本就应为绿，不受文档当前状态影响）。

**自检确认**：未修改 `SELF-GATE.md` 或 `protocol-alignment-review.md` 本身；`SELF-GATE.md` 路径引用统一为仓库根目录（无 `agate/` 前缀）。

---

## 批次 fg3-strict-mode-code（BDD-9代码半）

test_code_dir: `agate/tests/unit`

对应 `agate/scripts/check-protocol-consistency.py` main()（约 L1076-1134）新增 `--strict-errors-only` 互斥模式。

| 用例 | 场景 | Then | 测试函数 |
|---|---|---|---|
| BDD-9-code-1 | 0 ERROR + 0 WARNING | exit 0，输出含"🎉 全部检查通过" | `test_strict_errors_only_zero_error_zero_warning_exit_0` |
| BDD-9-code-2 | 0 ERROR + N WARNING | exit 0 + 提示信息，不压制既有提示 | `test_strict_errors_only_zero_error_n_warning_exit_0_with_hint` |
| BDD-9-code-3 | N ERROR | exit 1 + 含 ERROR 消息 | `test_strict_errors_only_n_error_exit_1` |

**红灯确认**：当前 argparse 未定义 `--strict-errors-only`，三条用例均在 `cpc.main()` 触发 `unrecognized arguments: --strict-errors-only`（SystemExit: 2），真红灯（B 类：CLI 接口缺失）。

**既有 `--strict` 矩阵回归确认**：`python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -k "not strict_errors_only"` → 24 passed，未受影响。

**范围确认**：本批次唯一改动文件 `agate/tests/unit/test_check_protocol_consistency.py`（追加 3 个测试函数）；未修改脚本本身；未碰 `phase-cards/P2-design.md`/`architect.md`/`P4-implementation.md`（fg1-doc-boundary 范围）。

---

## 批次 fg4-windows-python-probe（BDD-10/11/12）

test_code_dir: `agate/tests`

> **诚实边界（P0-brief 约束 3，强制）**：本环境是 Linux，无法真实触发 Windows Store `python3.exe` 占位符。以下集成测试全部用**模拟 stub**（exit 非零的假可执行文件）复现症状，不代表已在真实 Windows 环境验证；真实场景由 GitHub Actions Windows CI matrix（`pytest -m windows_smoke`）冒烟兜底。

### BDD-10：探测循环命中不可执行的候选时能继续探测下一候选
- 测试函数：`test_bdd_10_probe_skips_unexecutable_candidate`（参数化跑 3 个 hook：pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）
- 场景：PATH 上放置 broken `python3` stub（exit 49）+ 可用 `python` stub，验证探测循环跳过不可执行候选、继续探测并成功解析
- 当前状态：红灯（3 个参数化实例均 `returncode == 49`，marker 未出现，AssertionError 真实抛出——当前 3 薄壳无可执行性小测试，直接把命中的 broken stub 当可用候选）

### BDD-11：显式指定的 Python 路径可跳过探测循环
- 测试函数：`test_bdd_11_agate_python_explicit_override_skips_probe_loop`（同样参数化 3 个 hook）
- 场景：PATH 上只放 broken `python3` stub，额外设置 `AGATE_PYTHON` 指向真实解释器，验证薄壳直接采用该显式路径、不执行探测循环
- 当前状态：红灯（3 薄壳均未读取 `AGATE_PYTHON`，仍走探测循环命中 broken stub，AssertionError 真实抛出）

### BDD-12：Windows 已知问题已在协议文档中说明（文档断言型）
- 测试文件：新建 `agate/tests/unit/test_windows_python_probe_docs.py`
- 正面断言（当前红灯）：`test_bdd_12_platform_notes_documents_store_placeholder` / `test_bdd_12_platform_notes_documents_agate_python` / `test_bdd_12_agents_md_documents_agate_python_probe_enhancement`——platform-notes.md/AGENTS.md 当前均未提及 Store 占位符或 `AGATE_PYTHON`，AssertionError 真实抛出
- 负面断言（诚实性护栏，当前天然为绿，P4 实现后须继续保持绿）：`test_bdd_12_platform_notes_no_overclaim` / `test_bdd_12_agents_md_no_overclaim`——断言两处文本均不含"已在 Windows 实测通过"类夸大表述

**红灯确认**：9 failed（BDD-10 x3 + BDD-11 x3 + BDD-12 正面 x3），2 passed（BDD-12 负面诚实性护栏，按设计天然为绿）。全量 `agate/tests/` `--collect-only` 确认 1013 个测试正常收集，无导入/语法错误，本批次未破坏其他并行批次产出。

**未覆盖/边界说明**：未真实触发 Windows Store 占位符（环境限制）；实现侧判据按 P2-design.md 选定为通用 exit code 判据（非精确 49），测试断言只检查最终 `returncode == 0` + marker 出现，不绑定 exit 49 具体数值。未修改 3 薄壳/`platform-notes.md`/`AGENTS.md` 本身。

---

## P3 修复轮记录（retries[P3] round 1）

主 Agent 亲自跑 `gate_commands.P3`（`python3 -m pytest agate/tests/`，与 P2-design.md §5 一致的命令，无 `-q`）后，发现 5 个并行批次产生的 3 处测试代码卫生问题（非设计缺陷，均为并行批次间未预见的副作用）：

1. **fg1-parser-scripts**：`test_check_tdd_red.py` 第 726 行字符串字面量 `"Traceback...SyntaxError..."` 在该测试自身处于红灯时被 pytest 默认详细模式回显到外层 gate 判定的 raw_output 中，触发 `check-tdd-red.py` 无 formatter 时的原始输出正则误判为 A 类错误（假红灯）。**已修复**：改写为字符串拼接形式（运行时值不变，源码不含连续可匹配子串）。
2. **fg2-self-gate-naming**：`test_self_gate_naming_docs.py` 第 24 行 `import pytest` 未使用，触发 `ruff check agate/` 报 F401。**已修复**：删除未使用的 import。
3. **fg4-windows-python-probe**：`test_pre_commit_hook.py` 第 1462 行断言消息含裸词 `python3`，触发 `check-platform-assumptions.py` R2 规则误判（消息是自然语言描述，非命令引用）。**已修复**：改写消息措辞避免裸词匹配。

修复后主 Agent 独立复核：`python3 -m pytest agate/tests/` → 41 failed, 970 passed, 2 skipped（41 = 5 批次红灯总数，970 = 968 基线相关 + 2 处集体回归修复）；`ruff check agate/` → 全绿；`check-platform-assumptions.py agate/tests` → 0 命中；`check-tdd-red.py $TASK_DIR` → **exit 0（真红灯确认）**。

## 全量红灯确认（主 Agent 最终验证）

```
$ python3 agate/scripts/check-tdd-red.py agate-workspace/tasks/TAG0017-toolchain-fixes
TDD_CHECK: red-light (unexpected test failure)
EXIT=0
```

41 个新增测试用例失败（对应 BDD-1~12，除 4 个"按设计天然为绿"的护栏/前置/负面断言用例外），均为真实 AssertionError/ImportError（B 类失败），无 SyntaxError/第三方 ImportError 等假红灯来源。
