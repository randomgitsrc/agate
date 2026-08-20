---
phase: P3
task_id: TAG0007
type: test-cases
parent: P2-design.md
trace_id: TAG0007-P3-20260820
status: draft
created: 2026-08-20
agent: test-designer
---

# P3 测试用例（TAG0007：项目结构管理——骨架 + CODE-MAP）

`test_code_dir: agate/tests/unit`

本任务不是 refactor 任务（`P1-requirements.md` frontmatter 未声明 `change_type: refactor`），
走标准 TDD 口径：先写测试，测试当前须红灯，实现在 P4 完成后转绿。

## 产出文件

| 文件 | 性质 | 覆盖 BDD |
|------|------|----------|
| `agate/tests/unit/test_check_gate.py`（追加，新增 12 个测试函数，不改既有用例） | gate_p2/gate_p4/gate_p7 分支 | BDD-1/3/4/7/8/9/10 |
| `agate/tests/unit/test_skeleton_template_stack_neutral.py`（新建，3 个测试函数） | 骨架模板参数化回归 | BDD-2 |
| `agate/tests/unit/test_code_map_template.py`（新建，2 个测试函数） | CODE-MAP 模板字段齐全性 | BDD-6 |

BDD-5/BDD-11 不新增测试用例（见文末专节说明），验证方式为全量回归套件：
`python3 -m pytest agate/tests/` + `python3 agate/scripts/check-protocol-consistency.py`。

## 用例清单（1:1 映射 P1 BDD）

### BDD-1: 0→1 项目产出骨架的存在性

对应函数：`test_bdd_1_bootstrap_missing_skeleton_exit_1`、
`test_bdd_1_bootstrap_with_skeleton_title_exit_2`（`test_check_gate.py`，gate_p2 分支）。

- **用例 1（红灯）**：`P1-requirements.md` 声明 `project_phase: bootstrap`，`P2-design.md`
  满足既有 2 候选方案等前置条件（`add_p2_candidate_count(2)` + `add_p2_review`），但
  task 目录内**不存在** `P2-skeleton.md`。
  - 预期（BDD-1 要求）：`check-gate.py P2` exit 1，stderr 含 `P2-skeleton.md`。
  - 当前实际：gate_p2 尚无 `project_phase` 判定分支，exit 2（放行）——`assert
    result.returncode == 1` 断言失败，AssertionError，真红灯。
- **用例 2（当前已绿，合规）**：同上前提，但补齐 `P2-skeleton.md`（含 `## 骨架声明`
  标题）。
  - 预期：`check-gate.py P2` exit 2（主 Agent 自判，与现有 gate_p2 结束态一致）。
  - 当前实际：因 gate_p2 尚无该分支，结果同样是 exit 2——本用例目前已绿，属于
    "字段存在但未被消费，两种实现状态（有/无判定逻辑）碰巧同一结果"的必然情形，
    与 BDD-3 的"字段缺失回归对照"同理，不构成假红灯问题，P4 实现后仍须保持通过。

### BDD-2: 骨架模板技术栈参数化，不硬编码进协议本体

对应文件：`test_skeleton_template_stack_neutral.py`（3 个函数，均红灯）。

- `test_bdd_2_skeleton_template_exists`：断言 `assets/templates/skeleton-template.md`
  存在。当前该文件不存在 → `AssertionError`（真红灯）。
- `test_bdd_2_skeleton_template_no_hardcoded_stack_dirs`：断言文件内容不含黑名单
  （`src/components`、`src/include`、`src/hooks`、`src/pages`，P2-design.md §1.3 R7
  已列出）。当前因文件不存在，先在 `is_file()` 断言处失败（同上，真红灯）。
- `test_bdd_2_skeleton_template_has_parameterization_markers`：断言文件内容含参数化
  关键词（`候选目录`、`技术栈`）。同上，先在存在性断言处失败。
- 声明：该检查是**回归防线**（防止未来编辑把模板改回硬编码），黑名单/关键词列表非
  穷尽式语义证明。

### BDD-3: 骨架机制不对已有结构的项目重复触发

对应函数：`test_bdd_3_field_missing_no_regression_exit_2`、
`test_bdd_3_established_explicit_no_regression_exit_2`（`test_check_gate.py`）。

- **用例 1（当前已绿，回归对照，dispatch-context 已明确允许）**：`project_phase`
  字段完全不声明（缺省 = established），无 `P2-skeleton.md`，其余同既有
  `test_g2_3_two_candidates_exit_2` 前提。
  - 预期：`check-gate.py P2` exit 2，stderr 不含 `P2-skeleton.md`。
  - 当前实际：exit 2 ——与改动前逐字节一致，用现有测试断言对照，验证行为未变，
    合规地保持绿灯（不是遗漏，是 BDD-3"不重复触发"的正面验证）。
- **用例 2（当前已绿，同上）**：显式声明 `project_phase: established`，无
  `P2-skeleton.md`。
  - 预期：同用例 1，exit 2。
  - 目的：显式声明非 bootstrap 值时同样不触发骨架校验（补齐用例 1 只测"缺省"未测
    "显式声明"的缺口）。

### BDD-4: 后续阶段产出物落在骨架声明目录内，偏离需可追溯说明

（与 BDD-7 共用同一对 gate_p4 测试函数，见下方 BDD-7 节的用例说明，不重复列出。）

### BDD-5: 骨架机制的实现改动不破坏现有回归基线

**不新增测试用例**——验证方式为全量回归套件：
`python3 -m pytest agate/tests/` 与 `python3 agate/scripts/check-protocol-consistency.py`
（gate_commands.P3/P5/P5_consistency，P2-design.md §6）。P5 阶段执行时须确认改动前
1011 条既有用例 0 新增失败、一致性检查仍为 0 ERROR。这不是遗漏，是 P2-design.md §3
"实现完成的标志"已明确的验证口径。

### BDD-6: CODE-MAP 维护物的存在与初始化

对应文件：`test_code_map_template.py`（2 个函数，均红灯）。

- `test_bdd_6_code_map_template_exists`：断言 `assets/templates/code-map-template.md`
  存在。当前不存在 → `AssertionError`（真红灯）。
- `test_bdd_6_code_map_template_has_five_required_headings`：断言文件内容含五个必填
  标题（模块/层/依赖方向/关键文件/约定）。同上，先在存在性断言处失败。
- 声明：`{AGATE_WORKSPACE}/agents/CODE-MAP.md`（agate 自身 dogfooding 实例）不在本
  自动化测试覆盖范围内——它是本任务 P4 在**本 worktree 工作区**内产出的实例文件，
  不是协议本体的通用模板，其存在性由 P6 acceptance 人工核对（BDD-6 验收对象），
  与 `assets/templates/code-map-template.md`（协议本体模板，本测试覆盖对象）是两个
  不同的产出物。

### BDD-7: P4 新增文件触发 CODE-MAP 更新义务

（与 BDD-4 共用同一对 gate_p4 测试函数：`test_bdd_4_7_gate_p4_warning_when_table_missing`、
`test_bdd_4_7_gate_p4_no_warning_when_table_present`，`test_check_gate.py`。BDD-4/BDD-7
在 P1 原文已声明是"同一触发场景，累加关系"，P2-design.md §1.1 的实现映射也是同一个
gate_p4 分支，故测试用例合并设计，不拆分。）

- **用例 1（红灯）**：`git_repo` + 暂存一个代码文件（`src.py`）+ `P4-review.md`
  approved；task 目录存在 `P2-skeleton.md`（骨架机制已采用，触发 OR 条件之一）；
  `P4-implementation.md` **缺** `## 新增文件核对表` 标题（`create_task_dir` 默认生成
  的空文件补 frontmatter 后天然缺该标题）。
  - 预期（P2-design.md §1.1 gate_p4 行）：exit 0（WARNING 不阻断），stderr 含
    `WARNING` 与 `新增文件核对表`。
  - 当前实际：gate_p4 尚无骨架/CODE-MAP 机制感知分支，无 WARNING 输出 ——
    `assert "WARNING" in result.output` 失败，AssertionError，真红灯。
- **用例 2（当前已绿，正面对照）**：同上前提，但 `P4-implementation.md` 补齐
  `## 新增文件核对表` 标题 + 一行核对表内容。
  - 预期：exit 0，stderr 不含 `WARNING`。
  - 当前实际：因 gate_p4 本就不产出该 WARNING，天然满足"不含 WARNING"——与 BDD-3
    同理，合规地保持绿灯，不是遗漏。
- 声明：dispatch-context 给出的 WARNING 触发条件是"task 目录存在 `P2-skeleton.md`
  **或** `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在"（OR 关系）。本测试只覆盖
  `P2-skeleton.md` 分支（task-dir 相对路径，判据明确无歧义）；`{AGATE_WORKSPACE}` 的
  具体解析机制（`.agate.env` / 环境变量优先级，见 `agate_common.py`
  `_resolve_workspace`）P2-design.md 未给出精确到函数级的解析细节，属 P4 实现细节，
  本测试不预先假设该细节，避免测试断言绑死一种未定的实现路径；`P2-skeleton.md`
  分支已足以覆盖"机制已采用触发 WARNING"这条判定路径的红灯验证。

### BDD-8: P7 一致性检查核对 CODE-MAP 与实际文件的同步偏离

对应函数：`test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1`、
`test_bdd_8_9_gate_p7_transcription_mismatch_exit_1`、
`test_bdd_8_9_gate_p7_paired_matches_exit_0`、
`test_bdd_8_9_gate_p7_mechanism_not_adopted_no_check`（`test_check_gate.py`，gate_p7
分支。BDD-8 与 BDD-9 共用同一组测试——BDD-8 要求"存在核对动作且结果可见"，BDD-9
要求"可见信号，不允许静默通过"，两者的可判定标准都落在同一处 gate_p7 pairing
硬校验，P2-design.md §1.1 也是同一行映射，故合并设计，不拆分。）

**两层 pairing 校验的字段对应关系（P2-design.md §2.3/§5 已修正，本任务测试用例
严格按此编写，不重新推导）**：
- 内部一致性层：`code_map_reviewed_count < code_map_new_files_count` → exit 1。
- 转抄核对层：P4 正文 `[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT` 标记的**实际计数**
  与 P7 的 `code_map_new_files_count`（**不是** `code_map_reviewed_count`）比较，
  实际计数 > `code_map_new_files_count` → exit 1。

用例：

- **用例 1（红灯，内部一致性层）**：`P7-consistency.md` frontmatter
  `code_map_new_files_count: 2` / `code_map_reviewed_count: 1`（1 < 2）。
  - 预期：exit 1，stderr 含 `CODE_MAP`。
  - 当前实际：gate_p7 尚无该判定分支，exit 0 —— AssertionError，真红灯。
- **用例 2（红灯，转抄核对层，隔离设计）**：`P4-implementation.md` 含 3 条
  `[CODE_MAP_UPDATED]`/`[CODE_MAP_EXEMPT` 标记（实际计数 3）；`P7-consistency.md`
  声明 `code_map_new_files_count: 2` / `code_map_reviewed_count: 2`（**故意让
  `reviewed_count` 与 `new_files_count` 相等**，使内部一致性层本身通过，只让转抄
  核对层单独触发——这是 dispatch-context 明确要求的隔离设计，防止用例把两层
  校验的失败原因混在一起，掩盖字段写反的风险）。
  - 预期：exit 1（3 > 2），stderr 含 `CODE_MAP`。
  - 当前实际：exit 0 —— AssertionError，真红灯。
- **用例 3（当前已绿，正面对照）**：P4 标记实际计数 2，P7 声明
  `code_map_new_files_count: 2` / `code_map_reviewed_count: 2`，两层均匹配。
  - 预期：exit 0。
  - 当前实际：exit 0（gate_p7 本就不检查该字段）——两种实现状态碰巧同一结果，
    与 BDD-3/BDD-7 正面用例同理，合规地保持绿灯。
- **用例 4（当前已绿，回归对照）**：`P7-consistency.md` 完全不声明
  `code_map_new_files_count`/`code_map_reviewed_count`（机制未采用）。
  - 预期：exit 0，stderr 不含 `CODE_MAP`，两层 pairing 校验均不触发。
  - 当前实际：exit 0，行为与改动前一致，回归对照，合规地保持绿灯。

### BDD-9: 依赖方向偏离检测产生可见信号，不允许静默通过

同 BDD-8（见上节，共用同一组测试函数，不重复列出）。

### BDD-10: change_type: refactor 任务不豁免 CODE-MAP 更新义务

对应函数：`test_bdd_10_gate_p4_refactor_not_exempt_warning`、
`test_bdd_10_gate_p7_refactor_not_exempt_pairing_check`（`test_check_gate.py`）。

- **用例 1（红灯，gate_p4）**：与 BDD-4/7 用例 1 相同前提，额外声明 `P1-requirements.md`
  `change_type: refactor`。
  - 预期：判定逻辑不因 `change_type: refactor` 而跳过，WARNING 仍应触发（与非
    refactor 场景行为一致）。
  - 当前实际：exit 0，无 WARNING —— AssertionError，真红灯（与 BDD-4/7 用例 1 同一
    根因：gate_p4 尚无该分支，与 `change_type` 无关，恰好验证了"判定逻辑不读取/
    不分支 `change_type` 字段"这条要求——P4 实现后，refactor 与非 refactor 两个
    版本的用例应产出相同判定结果）。
- **用例 2（红灯，gate_p7）**：与 BDD-8 用例 1（内部一致性层不匹配）相同前提，额外
  声明 `change_type: refactor`。
  - 预期：pairing 硬校验仍应生效，exit 1。
  - 当前实际：exit 0 —— AssertionError，真红灯，同上道理。

### BDD-11: CODE-MAP 机制的实现改动不破坏现有回归基线

**不新增测试用例**，验证方式同 BDD-5：全量回归套件
（`python3 -m pytest agate/tests/` + `check-protocol-consistency.py`）。

## 红灯自检记录

执行 `python3 -m pytest agate/tests/unit/test_check_gate.py
agate/tests/unit/test_skeleton_template_stack_neutral.py
agate/tests/unit/test_code_map_template.py -v`：

- 11 个新增测试函数当前失败，失败类型均为 `AssertionError`（`test_bdd_1_bootstrap_missing_skeleton_exit_1`
  / `test_bdd_4_7_gate_p4_warning_when_table_missing` /
  `test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1` /
  `test_bdd_8_9_gate_p7_transcription_mismatch_exit_1` /
  `test_bdd_10_gate_p4_refactor_not_exempt_warning` /
  `test_bdd_10_gate_p7_refactor_not_exempt_pairing_check` / 3 个骨架模板测试 / 2 个
  CODE-MAP 模板测试），非 `SyntaxError`/`ImportError`，真红灯确认。
- 其余 6 个新增测试函数（BDD-1/3/4/7/8/9 各自的"正面对照/回归对照"用例）当前通过——
  均属"字段/机制未被判定逻辑消费，实现前后碰巧同一结果"的合规情形（本文档逐条已
  标注理由，非遗漏，与 dispatch-context 对 BDD-1/3 的明确说明一致）。
- 全量回归（`python3 -m pytest agate/tests/`）额外确认：新增用例不影响既有 1011 条
  用例（无新增失败）；`test_con_1_check_1_yaml_parseable` 与
  `test_bdd_25_consistency_zero_error` 两处失败经核实**不是**改动前已存在的基线
  失败，真实根因是 `P2-design.md` 第 276 行 `note:` 字段值内部含未转义的 ASCII
  双引号，属本任务自身 P2 产出物的 YAML 转义 bug，已在本任务内修复（改为中文全角
  引号）。修复后 `check-protocol-consistency.py` 恢复 0 ERROR，上述两个测试单独执行
  均 PASSED；全量回归结果更新为 `11 failed, 1017 passed, 2 skipped`，0 条遗留意外
  失败。
