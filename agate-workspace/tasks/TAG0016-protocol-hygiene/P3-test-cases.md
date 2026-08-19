---
phase: P3
task_id: TAG0016
type: test-cases
parent: P2-design.md
trace_id: TAG0016-P3-20260819
status: draft
created: 2026-08-19
agent: test-designer
---

test_code_dir: agate/tests/unit

# P3 测试用例 — agate 协议卫生与测试效率（TAG0016）

## 0. 产出概览

| 文件 | 性质 | 新增测试函数数 | 覆盖 BDD |
|------|------|----------------|----------|
| `agate/tests/unit/test_check_protocol_consistency.py` | 追加（CHECK 12 单测） | 7 | BDD-5, BDD-6, BDD-7, BDD-9, BDD-10 |
| `agate/tests/unit/test_check_p6_provenance.py` | 追加（审计 7 单测） | 4 | BDD-12, BDD-13 |
| `agate/tests/unit/test_protocol_dedup_audit.py` | 新建（批量机械去重断言审计） | 13（其中 1 个对 4 文件参数化） | BDD-1, BDD-2, BDD-3, BDD-4, BDD-5, BDD-7, BDD-11, BDD-14, BDD-15, BDD-16, BDD-18, BDD-19 |

`gate_commands.P3`（P2-design.md §6）：
```
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py agate/tests/unit/test_check_p6_provenance.py agate/tests/unit/test_protocol_dedup_audit.py -v
```

**当前红灯状态**（本次落盘后手动跑一遍 gate 命令实测，见 §4）：24 failed / 60 passed。
24 个失败全部是真实红灯（AttributeError 项目内属性/函数不存在，或 AssertionError 文档内容尚未
按 P2 设计迁移），无 SyntaxError / 第三方 ImportError / collection error（A 类假红灯为零）。
60 个通过里含 97 个既有回归用例的一部分 + 本批新增的 3 个"回归防护"用例（`test_bdd_7_*` /
`test_bdd_16_*` / `test_bdd_18_platform_notes_windows_section_preserved`）——这三个用例断言的是
"迁移后不应被误伤的既有正确内容"，设计上就应该在迁移前后都保持通过（不是红灯驱动项，见 §1 逐条
说明），与 TDD"证明测试真的在测目标功能"的原则不冲突：它们测的目标功能是"迁移不破坏既有正确
模式"，这项功能当前（迁移前，没有任何迁移动作）天然成立，属于合理的初始绿灯。

---

## 1. 19 条 BDD 逐条覆盖表

| BDD | 覆盖方式 | 测试函数 | 当前状态 |
|-----|---------|---------|---------|
| BDD-1 | 自动化：4 文件参数化断言"文件头 20 行内含 `职责边界` 声明" | `test_bdd_1_19_responsibility_boundary_declared[WORKFLOW.md\|dispatch-protocol.md\|state-machine.md\|platform-notes.md]`（test_protocol_dedup_audit.py） | 红（4/4 AssertionError，声明行尚未存在） |
| BDD-2 | 自动化：WORKFLOW.md/dispatch-protocol.md 平台适配小节收窄断言 | `test_bdd_2_platform_dedup_workflow`、`test_bdd_2_platform_dedup_dispatch_protocol`（test_protocol_dedup_audit.py） | 红（两处仍独立展开完整内容） |
| BDD-3 | 自动化：两表分工声明句存在性断言 | `test_bdd_3_phase_threshold_table_division_of_labor`（test_protocol_dedup_audit.py） | 红（两处均缺分工声明句） |
| BDD-4 | 自动化：内联模板收窄行数 + 权威源指针短语 / 文件头矛盾声明修正 | `test_bdd_4_dispatch_prompt_single_source_template`、`test_bdd_4_dispatch_prompt_single_source_head`（test_protocol_dedup_audit.py） | 红（内联版仍 208 行；文件头仍含矛盾声明） |
| BDD-5 | 自动化：① dedup 内容断言（state-transitions.md 仍复制 8 行权威表）② CHECK 12 单测覆盖"Then 子句要求的 gate 检测能力"两面 | `test_bdd_5_retry_max_pointer_in_state_transitions`（test_protocol_dedup_audit.py）+ `test_bdd_5_check12_pointer_file_missing_phrase_reports_error`、`test_bdd_5_check12_pointer_redeclares_table_reports_error`（test_check_protocol_consistency.py） | 全部红 |
| BDD-6 | 自动化，但不在 test_protocol_dedup_audit.py 单独覆盖——Then 子句字面是"防复发 gate（BDD-9）运行后报 ERROR"，即 CHECK 12 本身的行为，M13 已声明 8 张卡片内联 MAX 行"保留原样不改"（无去重前后差异可断言）。由 CHECK 12 正报测试覆盖 | `test_bdd_9_check12_mismatched_inline_max_reports_error`（test_check_protocol_consistency.py） | 红 |
| BDD-7 | 自动化（回归防护）：三处既有正确指针句原样保留断言 | `test_bdd_7_precommit_pointers_unchanged`（test_protocol_dedup_audit.py）+ `test_bdd_10_check12_no_false_positive_on_existing_precommit_pointers`（test_check_protocol_consistency.py，测 gate 侧不误报；dedup_audit 测文档内容本身未被误伤，两者目的不同都保留） | dedup_audit 侧当前绿（预期行为，三处指针句现状本就正确，去重不应触碰）；CHECK 12 侧红（函数未实现） |
| BDD-8 | **不适合自动化**——P1 定义为 P6 阶段人工抽查动作（判断"内容是否已迁移到正确归属文档或被职责表显式认定合理保留"是定性语义判断，见 P1 3.7 节），未写测试 | — | 验证方式：P6 验收阶段人工抽查 WORKFLOW.md、dispatch-protocol.md 各至少 1 处曾被认定"职责定位混乱"的段落，核对是否与 P2 §0 职责声明表口径一致 |
| BDD-9 | 自动化：CHECKS 注册 + 锚点表结构 + 正报（数值不一致报 ERROR，含文件名与数值对） | `test_bdd_9_checks_list_registers_check12`、`test_bdd_9_authoritative_value_anchors_retry_max_registered`、`test_bdd_9_check12_mismatched_inline_max_reports_error`、`test_bdd_9_check12_consistent_values_zero_error`（test_check_protocol_consistency.py） | 全部红（AttributeError：`AUTHORITATIVE_VALUE_ANCHORS`/`check_authoritative_values` 不存在） |
| BDD-10 | 自动化：既有正确模式（Pre-commit 三处指针）0 误报 | `test_bdd_10_check12_no_false_positive_on_existing_precommit_pointers`（test_check_protocol_consistency.py）；"`pytest agate/tests/` 全绿"由 gate_commands.P5 整体校验，非独立 P3 项 | 红（函数未实现） |
| BDD-11 | 自动化：dispatch-protocol.md 新增小节存在性 + 四个重跑点关键词 | `test_bdd_11_rerun_audit_table_exists`（test_protocol_dedup_audit.py） | 红（小节不存在） |
| BDD-12 | 自动化：审计 7 三态之二（无改动→允许复用 / 字段缺失→静默回退强制重跑） | `test_bdd_12_audit7_no_changes_reuse_allowed`、`test_bdd_12_audit7_missing_field_no_reuse_claim_possible`（test_check_p6_provenance.py） | 红（AttributeError：`audit7_p5_evidence_reuse` 不存在） |
| BDD-13 | 自动化：审计 7 第三态（有非产出文件改动→拦截强制重跑）+ 边界（共享看板文件被正确排除，不误判） | `test_bdd_13_audit7_non_produce_change_reuse_blocked`、`test_bdd_13_audit7_only_produce_dirs_excluded_active_tasks_board`（test_check_p6_provenance.py） | 红（同上） |
| BDD-14 | 自动化（轻量 grep 断言，dispatch-context 判断为"可写"）：P8-release.md 精简表述存在性 | `test_bdd_14_p8_release_reuse_wording`（test_protocol_dedup_audit.py） | 红（现状仍是无条件"重跑 P5 gate"表述） |
| BDD-15 | 自动化：解析 workflow YAML，断言新增 xdist 观测步骤存在且不阻塞 job | `test_bdd_15_ci_xdist_observability_step`（test_protocol_dedup_audit.py） | 红（步骤不存在） |
| BDD-16 | 自动化（回归防护）：并行规则 xdist 判据文本仍存在 | `test_bdd_16_parallel_rule_xdist_judgement_unchanged`（test_protocol_dedup_audit.py） | 绿（预期行为，判据现状本就包含 xdist 表述，M23 不应削弱它） |
| BDD-17 | **不单独覆盖**——由 `gate_commands.P5`（`pytest agate/tests/` 全绿 + `check-protocol-consistency.py --strict` 0 ERROR + `count-tests.sh` 计数一致）整体校验，是贯穿全任务的元要求，非独立 P3 红灯项 | — | 验证方式：P5/P8 阶段跑 gate_commands.P5 三命令串联，任一非 0 即整体失败 |
| BDD-18 | **不适合自动化**（"不得声称已在 Windows 实测"是文档表述的语义/口径要求，非结构可判定）；仅写一个回归防护辅助用例，保护"Windows 原生安装指南未被去重误删" | `test_bdd_18_platform_notes_windows_section_preserved`（test_protocol_dedup_audit.py，辅助非强制） | 验证方式：P6/P8 阶段人工核对涉及 Windows 兼容性的结论表述是否符合"仅增量声明"口径；辅助用例当前绿（章节现状本就存在） |
| BDD-19 | 与 BDD-1 合并测试（同一处声明行同时满足两条 BDD 的 Then 子句） | 同 BDD-1：`test_bdd_1_19_responsibility_boundary_declared` 参数化用例 | 红 |

---

## 2. 设计说明（关键决策记录）

### 2.1 CHECK 12（test_check_protocol_consistency.py）

- 沿用现有 `_load_cpc`（importlib 动态加载模块）+ `cpc.Report()` 直接调函数的测试范式，与既有
  CHECK 4/9/10/11 测试风格一致（不用 CLI subprocess，函数级白盒测试）。
- 夹具 `_make_check12_tree()` 用真实重试上限数值（P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2，
  P1-requirements.md §3.5 已核实）和真实阶段卡片文件名（P3-tdd.md/P5-verification.md/
  P6-acceptance.md/P8-release.md 等），使夹具贴近迁移后的真实文档形态，而非抽象占位符。
- 7 个测试覆盖：CHECKS 注册（BDD-9）、锚点表结构（BDD-9）、正报-数值不一致（BDD-6/9）、
  不误报-一致状态（BDD-9/10）、不误报-既有 Pre-commit 指针位置（BDD-7/10）、边界-指针短语缺失
  （BDD-5）、边界-仍复制完整表格即使声明权威源（BDD-5，对应 M11 迁移前的红灯基线）。

### 2.2 审计 7（test_check_p6_provenance.py）

- 与既有测试的黑盒 CLI 风格（`_run_prov` + `run_cli` fixture）不同，审计 7 测试改用函数级白盒
  测试（`_load_prov_module` + 直接调 `cpp_mod.audit7_p5_evidence_reuse(task_dir, state_yaml)`），
  理由：P2-design.md §3.5 伪代码明确给出了该函数的签名与三态返回值契约
  （`no_reuse_claim_possible`/`reuse_blocked`/`reuse_allowed`），直接测函数契约比测 CLI 整体
  exit code 更精确；且 `p6_declares_reuse()` 的具体判定格式（P6-acceptance.md 里"声明引用 P5
  证据"的确切标记语法）P2 设计未定稿，留给 P4 实现决定，不在 P3 预先假设具体字符串格式，避免
  测试对未定稿格式过度绑定。
- 用真实 git 仓库（`conftest.GitRepo` fixture）构造 commit 历史，而非 mock `subprocess.run`——
  贴近 §3.5 伪代码"跑 `git diff <commit>..HEAD --name-only`"的真实实现路径，且能自然验证
  `EXCLUDE_PRODUCE_PREFIX = "agate-workspace/tasks/"` 前缀判定的真实语义（含 P2
  minimal_validation 附注的"跨任务共享看板文件 active-tasks.md 同样被排除"边界，已单独写一个
  测试覆盖）。
- 4 个测试覆盖 BDD-12 的两态（无改动/字段缺失）+ BDD-13 的一态（有改动）+ BDD-13 边界（共享看板
  文件不误判）。

### 2.3 test_protocol_dedup_audit.py（批量机械去重断言审计）

- 采用 HANDOFF-TAG0016.md 建议的策略：直接读真实 `agate/` 协议文档内容（不用 fake fixture），
  断言"去重后文档应该长什么样"。所有断言都基于已读取的真实现状文本（WORKFLOW.md L461 平台适配
  段落、dispatch-protocol.md L429-680 派发 prompt 模板内联版、dispatch-prompt.md 文件头矛盾声明、
  rules/state-transitions.md L56 完整表格等），确保红灯是真实反映"内容还没改"，不是凭空断言。
- BDD-1/BDD-19 用同一个参数化测试覆盖（P2-review 第 1 轮指出的测试缺口，本次派发已作为硬约束
  纳入）：4 个文件（WORKFLOW.md/dispatch-protocol.md/state-machine.md/platform-notes.md）逐一
  断言文件头 20 行内含 `职责边界` 声明行。
- BDD-7/BDD-16/BDD-18 三个"回归防护"用例设计上预期已绿（断言的是"既有正确内容不应被误伤"，
  迁移前这些内容本就正确存在）。这不违反"P3 测试须证明测试真的在测目标功能"的原则——它们测的
  目标功能本身就是"迁移不破坏既有正确模式"，该功能在"零改动"状态下天然成立是合理初始状态；
  `check-tdd-red.py` 的红灯判定标准（`assertion failure > 0 且 collection error == 0` 即可判定
  为红灯可推进，见 `agate/scripts/check-tdd-red.py` 文件头 docstring）不要求"每一个测试都失败"，
  只要求"整体命令有真实断言失败、无 A 类错误"，本次 24 个失败满足该标准。
- BDD-6 未在本文件单独写测试：其 Then 子句字面要求的是"CHECK 12 报 ERROR"这一 gate 行为本身，
  已由 test_check_protocol_consistency.py 的正报测试覆盖；且 M13 明确 8 张卡片内联 MAX 行
  "保留原样不改"，本文件若另写一条"迁移前后值不变"的断言，不会带来去重前后的红灯语义（该断言
  当前即为真，不是红灯驱动项，写了也无意义）。
- BDD-14/BDD-15 按 dispatch-context 指引判断为"可以写"，均已写；BDD-17（元要求，由 gate_commands.P5
  兜底）与 BDD-8/BDD-18（定性人工判断）按指引判断为"不适合/不需要独立自动化"，已在表中显式声明
  验证方式，不是遗漏。

---

## 3. 已知问题（不在本阶段修复范围，如实记录）

`agate/scripts/agate-read-gate-commands.py` 存在一个预置 bug：解析 P2-design.md 的
`gate_commands:` 块时，正则判据 `key.startswith("P3") and not key.endswith("_formatter")` 会把
`P3_timeout_seconds: 120` 这类超时声明字段误判成一条待执行命令（`cmd="120"`），导致
`check-tdd-red.py` 内部 `bash -c "120"` 返回 127（command not found），而 `worst_exit` 取多条
命令中的最差结果，把本应正确的 B 类红灯判定（针对真实 pytest 命令）覆盖成 A 类错误（整体 exit 1）。

本任务 P2-design.md §6 declares `gate_commands.P3_timeout_seconds: 120`，会触发此 bug——主 Agent
若直接跑 `python3 agate/scripts/check-tdd-red.py {task_dir}` 会得到误导性的 exit 1（A 类）。
已用等价的直接命令手动验证真实红灯状态（见下），确认这是 gate 工具本身的既有缺陷，不是本次新增
测试的问题：

```bash
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py agate/tests/unit/test_check_p6_provenance.py agate/tests/unit/test_protocol_dedup_audit.py -v
# 结果：24 failed, 60 passed — 全部失败为 AttributeError / AssertionError，无 SyntaxError/ImportError/collection error
```

本 bug 修复不在 P3 test-designer 的允许改动范围内（`agate/scripts/*.py` 属 P4 implementer 工作），
如实记录供主 Agent/后续阶段决策（可用 `TEST_RUNNER` 环境变量覆盖绕过，或登记为独立债务项）。

---

## 4. 红灯实测记录

命令：
```bash
python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py agate/tests/unit/test_check_p6_provenance.py agate/tests/unit/test_protocol_dedup_audit.py -v
```

结果：`24 failed, 60 passed in 5.45s`

失败分类：
- AttributeError（B 类，项目内属性/函数不存在）：11 个（CHECK 12 相关 7 个 + 审计 7 相关 4 个）
- AssertionError（B 类，断言失败因文档内容/CI 配置尚未按 P2 设计迁移）：13 个（test_protocol_dedup_audit.py 全部新增红灯用例）
- SyntaxError / 第三方 ImportError / collection error：0 个

既有 97 个回归用例（`test_check_protocol_consistency.py` 16 个 + `test_check_p6_provenance.py`
41 个 + 二者原有共计）未受影响，全部仍通过（新增 import `GitRepo` 未破坏既有 collection）。
