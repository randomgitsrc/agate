---
phase: P6
task_id: TAG0007
type: acceptance
parent: P5-verification.md
trace_id: TAG0007-P6-20260820
status: draft
created: 2026-08-20
agent: verifier
# ── v2.0 机器汇总 ──
pass: 11
fail: 0
ui_affected: false
---

[NO_NEED_CONFIRM] [PROD_NOT_TOUCHED]

# P6 验收报告 — TAG0007-project-structure

按 P3-test-cases.md 给出的 BDD→测试函数精确映射，重新实跑全部对应测试函数与内容核对命令，
结果作为本次验收证据。本任务非 refactor（无 `change_type: refactor` 声明），走标准功能验收
口径；`ui_affected: false`，不涉及截图/vision。

## 实跑摘要

`python3 -m pytest` 一次调用跑齐 12 个 `test_check_gate.py` 新增函数（BDD-1/3/4/7/8/9/10）+
3 个 `test_skeleton_template_stack_neutral.py` 函数（BDD-2）+ 2 个 `test_code_map_template.py`
函数（BDD-6），共 17 个测试函数，`-v --tb=short` 输出：**17 passed in 1.56s**，EXIT_CODE: 0
（`P6-evidence/test-output.log`）。另外对骨架模板、CODE-MAP 模板、CODE-MAP dogfooding 实例、
P4 核对表产出规格分别执行内容核对命令，产出独立证据文件。

## BDD 逐条对照

- PASS BDD-1: 0→1 项目产出骨架的存在性——test_bdd_1_bootstrap_missing_skeleton_exit_1（缺 P2-skeleton.md 时 exit 1）+ test_bdd_1_bootstrap_with_skeleton_title_exit_2（补齐后 exit 2）均 PASSED (test-output.log)
- PASS BDD-2: 骨架模板技术栈参数化，不硬编码具体语言/框架目录名——3 个骨架模板测试函数均 PASSED，模板原文以"候选目录集合（五类抽象类别标签）"表格表达，未见 src/components 等硬编码写法 (test-output.log, skeleton-template-content.log)
- PASS BDD-3: 骨架机制不对已有结构的项目重复触发——test_bdd_3_field_missing_no_regression_exit_2（project_phase 缺省）+ test_bdd_3_established_explicit_no_regression_exit_2（显式 established）均 PASSED，均 exit 2 不产生骨架强制要求 (test-output.log)
- PASS BDD-4: 后续阶段产出物落在骨架声明目录内，偏离需可追溯说明——test_bdd_4_7_gate_p4_warning_when_table_missing（缺「新增文件核对表」时 WARNING）+ test_bdd_4_7_gate_p4_no_warning_when_table_present（补齐后无 WARNING）均 PASSED；P4-implementation.md 第 66-69/147 行确认该产出规格文字真实存在 (test-output.log, p4-checklist-spec.log)
- PASS BDD-5: 骨架机制的实现改动不破坏现有回归基线——P5 独立实跑 pytest 1028 passed/2 skipped/0 failed（含改动前 1011 条基线全部不失败），check-protocol-consistency.py 0 ERROR (../P5-test-results/unit.md)
- PASS BDD-6: CODE-MAP 维护物的存在与初始化——test_bdd_6_code_map_template_exists + test_bdd_6_code_map_template_has_five_required_headings（模块/层/依赖方向/关键文件/约定五字段齐全）均 PASSED；agate-workspace/agents/CODE-MAP.md dogfooding 实例 test -f 确认存在 + grep -c 确认五字段均命中且已填入实际内容 (test-output.log, code-map-content.log)
- PASS BDD-7: P4 新增文件触发 CODE-MAP 更新义务——与 BDD-4 共用同一对测试函数（WARNING 提示"更新或显式豁免二者必居其一"）均 PASSED (test-output.log, p4-checklist-spec.log)
- PASS BDD-8: P7 一致性检查核对 CODE-MAP 与实际文件的同步偏离——4 个 gate_p7 pairing 测试函数（内部一致性层不匹配 exit 1 / 转抄核对层不匹配 exit 1 / 两层匹配 exit 0 / 机制未采用不触发）均 PASSED，核对动作存在且结果可见 (test-output.log)
- PASS BDD-9: 依赖方向偏离检测产生可见信号，不允许静默通过——与 BDD-8 共用同一组 4 个测试函数均 PASSED，偏离场景均产生 exit 1 + stderr 含 CODE_MAP 的可见信号，无静默通过路径 (test-output.log)
- PASS BDD-10: change_type: refactor 任务不豁免 CODE-MAP 更新义务——test_bdd_10_gate_p4_refactor_not_exempt_warning + test_bdd_10_gate_p7_refactor_not_exempt_pairing_check 均 PASSED，声明 refactor 时判定逻辑未被豁免 (test-output.log)
- PASS BDD-11: CODE-MAP 机制的实现改动不破坏现有回归基线——同 BDD-5，P5 独立实跑 pytest 1028 passed/2 skipped/0 failed，check-protocol-consistency.py 0 ERROR (../P5-test-results/unit.md)

**Summary**: 11/11 PASS, 0 FAIL

## 补充说明（逐条延伸细节）

- BDD-1：两个测试函数分别验证"骨架机制已采用触发场景判据"（判据存在且可判定，P1 只要求判据存在，具体触发条件由 P2 设计）。
- BDD-2：黑名单覆盖 `src/components`/`src/include`/`src/hooks`/`src/pages`；参数化关键词覆盖"候选目录"/"技术栈"，模板正文的「项目侧技术栈声明（填空区）」小节要求项目侧自行声明技术栈并在候选目录集合中填空，不由协议本体写死具体目录名。
- BDD-4/BDD-7：`p4-checklist-spec.log` 摘录了 `agate/phase-cards/P4-implementation.md` 第 66-69 行「新增文件核对表」小节标题与适用条件说明，以及第 147 行 WARNING 触发条件（骨架/CODE-MAP 机制已采用但缺该标题时 WARNING，不阻断 exit code），与测试函数实跑行为一致。
- BDD-6：dogfooding 实例 `agate-workspace/agents/CODE-MAP.md` 的模块/层/依赖方向/关键文件/约定五个标题已被 P4 填入 agate 协议本体自身的实际模块划分（五大模块）与分层说明，非仅占位符残留。
- BDD-8/BDD-9：两层 pairing 校验（内部一致性层 `code_map_reviewed_count < code_map_new_files_count`；转抄核对层 P4 正文标记实际计数 > `code_map_new_files_count`）均已被独立测试用例覆盖，且两个用例刻意隔离设计（用例 2 让 reviewed_count 与 new_files_count 相等，只让转抄核对层单独触发），避免两层失败原因混淆。
- BDD-10：两个用例分别复现 BDD-4/7 与 BDD-8 的判定前提，仅额外声明 `change_type: refactor`，验证判定逻辑不因该字段分支豁免——与非 refactor 版本行为一致。

## 视觉/UI 说明

本任务 `ui_affected: false`，P1 `capability_requirements: []`，无视觉能力声明条目，不涉及
Playwright/vision-analyst，不产出截图/vision YAML/人工复核记录。

## 证据目录清单

- `P6-evidence/test-output.log`：17 个测试函数（覆盖 BDD-1/2/3/4/6/7/8/9/10）`-v --tb=short`
  实跑输出 + `EXIT_CODE: 0`
- `P6-evidence/skeleton-template-content.log`：`assets/templates/skeleton-template.md` 原文
- `P6-evidence/code-map-content.log`：`assets/templates/code-map-template.md` 原文 +
  `agate-workspace/agents/CODE-MAP.md` 存在性/五字段核对 + 原文
- `P6-evidence/p4-checklist-spec.log`：`agate/phase-cards/P4-implementation.md`「新增文件核对表」
  节原文摘录
- BDD-5/BDD-11 引用 `../P5-test-results/unit.md`（P5 独立实跑证据，工作区任务目录相对路径）
