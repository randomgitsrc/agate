---
phase: P4
task_id: TAG0024
type: implementation
parent: P2-design.md
trace_id: TAG0024-P4-md-field-set-tool-20260825
status: draft
created: 2026-08-25
agent: implementer
---

```yaml
implementation_dir: agate/scripts/
```

## 一句话说明

新增 `agate-md-field-set.py`（frontmatter 字段写入 CLI，`<key> <value>` / `--list`）与
`agate-md-field-set-gate-commands.py`（正文 `gate_commands` YAML 块专用写入），二者均用
`importlib.util.spec_from_file_location`（仿 `check-routing.py:41-52` `_load_script` 模式）
动态加载 `agate-frontmatter-check.py` 的 `SCHEMAS`/`_check()`、`agate-md-field-get.py` 的字段
分类常量、`check-judge-verdict.py` 的 `_VALID_STATUS`，逐字节复用、零改动三个既有校验器；
`agate_common.py` 六个函数走普通 import。同时按 BDD-19 把 `dispatch-prompt.md`/
`dispatch-context.md` 中可被字面复制的 frontmatter Header 围栏替换为 `agate-md-field-set`
一行式指引。

## 自跑测试结果

命令：`python3 -m pytest agate/tests/unit/test_agate_md_field_set.py --basetemp=.pytest-tmp -p no:cacheprovider -v`

最终结果：**34/35 通过，1 项因下方"发现的测试缺陷"未转绿**（非本实现问题，见下节）。

```
agate/tests/unit/test_agate_md_field_set.py::test_bdd_1_valid_key_value_roundtrip_and_gate_pass PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_2_invalid_key_rejected_lists_valid_keys PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_3_invalid_value_rejected_with_enum_role_and_suggestion PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_4_role_unauthorized_write_rejected PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_5_list_matches_phase_task_fields PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_6_reports_remaining_missing_after_write PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_7_gate_commands_block_write_and_parse PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_8_gate_commands_invalid_block_rejected[undeclared-phase-key] PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_8_gate_commands_invalid_block_rejected[non-integer-timeout] PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_9_evidence_fields_rejected[...] PASSED（10 例全过）
agate/tests/unit/test_agate_md_field_set.py::test_bdd_10_atomic_write_interrupted_leaves_file_unchanged PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_11_missing_file_rejected PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_12_inserts_frontmatter_preserves_body PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_13_residual_body_field_warns_but_not_deleted PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_14_generated_frontmatter_passes_check_frontmatter PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_15_value_validation_same_source_as_check[invalid-below-min] PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_15_value_validation_same_source_as_check[valid-above-min] PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_16_zero_protocol_knowledge_walkthrough_converges FAILED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_17_writable_keys_is_mechanical_union PASSED
agate/tests/unit/test_agate_md_field_set.py::test_bdd_18_append_only_fields_rejected[...] PASSED（6 例全过）
agate/tests/unit/test_agate_md_field_set.py::test_bdd_19_dispatch_templates_reference_set_tool_no_copyable_fence PASSED

1 failed, 34 passed in 2.51s
```

## [DESIGN_GAP] BDD-16 测试用例数据缺陷（非实现问题，已诊断，未改测试）

`test_bdd_16_zero_protocol_knowledge_walkthrough_converges` 失败于最后一步
`check-gate.py P2 $TASK_DIR` 返回 1（非 `!= 1`），stderr：

```
GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述
```

**根因（已用独立脚本复现确认）**：`task_dir(phases=["P1","P2"])` fixture 自动生成的
`P2-design.md` 初始正文为空（`"---\nagent: test\n---\n\n"`），不含 `check-gate.py:815-820`
`has_keyword(p2_text, "tradeoff"/"choice_and_reason")` 要求的"权衡/选择理由"关键词——这是
`gate_p2()` 一条与 task_fields 完全无关的正文散文内容 nudge。`agate-md-field-set.py` 按
P2-design.md §3 设计（同源铁律 + 最小实现原则）只写 frontmatter 字段与 `gate_commands` 正文块，
不生成/篡改任意正文散文，因此无法、也不应该替测试注入这段文案。

对照组：`test_bdd_1_valid_key_value_roundtrip_and_gate_pass` 手写 `P2-design.md` 时特意包含了
"方案设计正文，选择理由如下：候选 A 更简单，权衡后选 A" 这句话满足该 nudge；`test_bdd_16`
改用自动 fixture（空正文）且全程只通过 `set`/`set-gate-commands` 调用字段写入，从未获得等价的
正文内容注入路径——这是 P3-test-cases 对 BDD-16 fixture 数据的遗漏，不是
`agate-md-field-set.py`/`agate-md-field-set-gate-commands.py` 的实现缺陷。

按 implementer.md 决策树处理：判定为"测试断言与真实系统行为矛盾"（该 nudge 独立于本工具
覆盖的 task_fields 契约），**未修改测试文件**（角色红线：不改测试去迁就实现），也未在
set 工具里添加"自动注入权衡文案"这类超出 P2 设计范围的功能（会违反最小实现原则与同源
铁律的边界声明）。已在 progress 文件逐条记录复现过程，供主 Agent 决定是否回退 P3 补
fixture 或另行判定。

## 产出文件

- `agate/scripts/agate-md-field-set.py`（新建）
- `agate/scripts/agate-md-field-set-gate-commands.py`（新建）
- `agate/assets/templates/dispatch-prompt.md`（修改，BDD-19）
- `agate/assets/templates/dispatch-context.md`（修改，BDD-19）

本仓库当前未采用骨架（`P2-skeleton.md`）或 CODE-MAP（`agents/CODE-MAP.md`）机制
（均未在本任务工作区发现），按角色定义规则本节"新增文件核对表"可省略。

## 校验证据

- `grep -n "spec_from_file_location" agate/scripts/agate-md-field-set.py` → 命中第 49 行，确认
  同源复用走 importlib 动态加载而非复制粘贴。
- `git diff --stat -- agate/scripts/agate-frontmatter-check.py agate/scripts/agate-md-field-get.py
  agate/scripts/check-judge-verdict.py` → 空输出，确认三个受保护文件零改动。
