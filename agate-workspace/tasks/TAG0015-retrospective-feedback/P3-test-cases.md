---
phase: P3
task_id: TAG0015
type: test-cases
parent: P2-design.md
trace_id: TAG0015-P3-20260819
status: draft
created: 2026-08-19
agent: test-designer
---

# P3-test-cases.md — TAG0015 agate 复盘与反馈机制统一（TDD 测试设计）

`test_code_dir: agate/tests/unit/`

## 1. 三个测试文件（严格对应 P2-design.md §5 gate_commands.P3 固化的命令）

```bash
python3 -m pytest agate/tests/unit/test_check_retrospective.py \
  agate/tests/unit/test_agate_feedback.py \
  agate/tests/unit/test_retrospective_protocol_docs.py -v
```

| 文件 | 类型 | 覆盖 BDD | 新增/新建函数数 |
|------|------|---------|-----------------|
| `agate/tests/unit/test_check_retrospective.py` | 扩展既有文件（12 既有用例保留不动） | BDD-9/BDD-10（BDD-11 由新增用例本身实现，不单列） | 3 |
| `agate/tests/unit/test_agate_feedback.py` | 新建（`agate-feedback.py` 尚不存在） | BDD-17/BDD-18/BDD-19/BDD-20 | 7 |
| `agate/tests/unit/test_retrospective_protocol_docs.py` | 新建（风格参照 `test_review_role_docs.py`） | BDD-1/2/3/4/5/6/7/8/12/13/14/15/16 | 13 |

新增/新建测试函数合计 **23** 个，覆盖 P1-requirements.md 全部 20 条 BDD（满射，见 §2 映射表）。

## 2. BDD → 测试函数映射表

### 2.1 `test_check_retrospective.py`（脚本类，check-retrospective.py）

| BDD | 测试函数 | 覆盖点 |
|-----|---------|--------|
| BDD-9 | `test_tag0015_bdd9_stderr_hint_points_to_task_dir` | 触发异常提醒时 stderr 含字面量 `tasks/{Txxx}/retrospective.md`，且不再含 `docs/releases` |
| BDD-10 | `test_tag0015_bdd10_debt_signal_triggers_mechanism_gap_reminder` | 无 retry/SCOPE+/override 异常，仅 `{workspace}/debt/tech-debt.md` 命中本 task_id → 输出"发现机制缺口"提醒块（与"检测到异常模式"标题可区分），exit 0；两层嵌套 fixture 隔离（`tmp_path/agate-workspace/tasks/T001/` + 兄弟 `debt/`），不依赖仓库真实 debt 数据 |
| BDD-10 | `test_tag0015_bdd10_roadmap_signal_triggers_mechanism_gap_reminder` | 同上，触发面换成 `{workspace}/roadmap/roadmap.md` 关联任务表格命中 task_id |
| BDD-11 | （由上述 3 个新增用例本身构成——BDD-11 Then 子句要求"新增 ≥2 个单测断言覆盖 BDD-9/10"，本身不产生独立测试对象，P2-design.md §5 已定案） | — |

### 2.2 `test_agate_feedback.py`（脚本类，新增 agate-feedback.py）

| BDD | 测试函数 | 覆盖点 |
|-----|---------|--------|
| BDD-17 | `test_bdd17_extracts_mechanism_issues_from_frontmatter_and_section` | 输入符合 BDD-6/BDD-7 格式的内联 fixture 复盘文档，`AGATE_FEEDBACK=on` + `--format json` → stdout 含 `mechanism_issues` 键与其列表内容，exit 0，不报解析错误 |
| BDD-18 | `test_bdd18_anonymize_project_name_replaced_with_placeholder` | `## agate 反馈` 节含项目名 `MySecretProject`（经 `--project-name` 显式传入）→ 输出不含原始项目名，含 `<PROJECT>` 占位符 |
| BDD-18 | `test_bdd18_anonymize_absolute_path_removed_or_relativized` | 节内容含项目外绝对路径 `/home/otheruser/.secret-tool/config.json` → 输出不含原始路径，含 `<PATH>` 占位符 |
| BDD-19 | `test_bdd19_env_unset_produces_no_output_and_disabled_message` | 未设置 `AGATE_FEEDBACK` → exit 2，output 含"未启用"，stdout 为空（断言消息文案而非仅 exit code，避免与"脚本文件不存在"的巧合 exit 2 混淆产生假绿） |
| BDD-19 | `test_bdd19_env_explicit_off_produces_no_output_and_disabled_message` | 显式 `AGATE_FEEDBACK=off` → 同上行为 |
| BDD-20 | `test_bdd20_source_contains_no_network_submit_calls` | 静态源码断言：不含 `subprocess`/`git push`/`gh ` |
| BDD-20 | `test_bdd20_stdout_contains_markdown_issue_body_snippet` | `--format markdown` → stdout 含 Markdown 标题标记 + 复盘内容片段（产出待人工提交内容，非自动提交） |

### 2.3 `test_retrospective_protocol_docs.py`（纯文档类，不 import 为模块）

| BDD | 测试函数 | 覆盖点 |
|-----|---------|--------|
| BDD-1 | `test_bdd_1_template_defines_four_body_sections` | `retrospective-template.md` 含"事实基线/做得好的/发现的问题/改进措施"四小节标题；旧路径 `docs/reviews/postmortem-template.md` 已不存在（git mv 完成） |
| BDD-2 | `test_bdd_2_template_declares_content_value_criteria` | 含"内容价值标准"小节 + 三条标准（机制缺口/可复用模式/可行动层面） |
| BDD-3 | `test_bdd_3_template_attribution_layer_field` | 含"归因层面"字段 + "机制缺口/执行错误" + "两者都是"禁止说明 |
| BDD-4 | `test_bdd_4_template_debt_registration_mandatory_note` | 含 DEBT/roadmap 编号强制说明 + "待定"禁止写法提示 |
| BDD-5 | `test_bdd_5_template_asset_precipitation_prompt` | 含追问句原文"本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？" + "回馈 agate"/"项目资产沉淀"两类去向 |
| BDD-6 | `test_bdd_6_template_frontmatter_machine_fields` | frontmatter 样例含 `mechanism_issues`/`execution_issues`/`feedback_ready` |
| BDD-7 | `test_bdd_7_template_agate_feedback_section` | 含 `## agate 反馈` 标题 + "不涉及项目敏感信息"边界声明 |
| BDD-8 | `test_bdd_8_template_hooked_into_protocol_body` | `phase-cards/P8-release.md` 含新模板路径字符串（挂钩点） |
| BDD-12 | `test_bdd_12_orchestrator_log_decision_and_rationale` | `state-machine.md` 三项既有排除原样保留 + 新增"简要依据"分句；旧限制性表述"只写决策和下一步"（无顿号）已被替换 |
| BDD-13 | `test_bdd_13_l2_checkpoint_docs` | `state-machine.md` 含"L2 会话 checkpoint"小节标题，且其后同时出现 `P{n}-checkpoint.md` 与 `task-session-summary.md` 两个文件名字符串（P2-design.md §5 指定的静态锚点，函数名逐字沿用） |
| BDD-14 | `test_bdd_14_cross_file_orchestrator_log_consistency` | Given 前置 BDD-12 已完成（`state-machine.md` 含"简要依据"）；`loop-orchestration.md`/`task-files.md` 均不逐字复述旧限制性表述，不矛盾 |
| BDD-15 | `test_bdd_15_agents_md_retrospective_location_split` | `AGENTS.md` 含 `tasks/{Txxx}/retrospective.md` 与"历史复盘"两类措辞区分 |
| BDD-16 | `test_bdd_16_legacy_retrospectives_annotated` | 5 份存量复盘文件（tag0008/tag0010-11 含同名 review/tag0013/tag0014）均含"历史复盘"标注行 + 新路径引用 |

## 3. 红灯真实性自检（dispatch-context 约束 3）

`timeout 60s python3 -m pytest agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v` 实跑结果：

- **23 failed, 12 passed**
- 12 passed = `test_check_retrospective.py` 既有 12 个用例原样通过（未被本次扩展破坏）
- 23 failed = 本次新增/新建的全部 23 个测试函数（3 + 7 + 13），失败原因均为 `AssertionError`（断言失败）或 `FileNotFoundError`（读取尚不存在的 `agate/assets/templates/retrospective-template.md` / `agate/scripts/agate-feedback.py`），均属 B 类错误（真红灯），无 `SyntaxError`/第三方库缺失类 A 类错误
- 特别核实：`test_agate_feedback.py` 的 BDD-19 两个用例存在"脚本文件不存在导致 python3 本身返回 exit 2"与"BDD-19 预期的功能未启用 exit 2"数值巧合的假绿风险——已通过额外断言 `"未启用" in result.output` 排除（脚本不存在时错误消息是 `can't open file...`，不含"未启用"，故仍正确红灯）

## 4. fixture 隔离说明（BDD-10，对应 P2-design.md env_constraints）

`test_tag0015_bdd10_*` 两个用例不复用共享 `task_dir` fixture（其默认单层 `tmp_path/task-XXXXXX/` 布局下两级向上推导会指向 `tmp_path` 本身，不是虚构的 debt/roadmap 目录）。改为手搭两层嵌套结构：

```
tmp_path/agate-workspace/tasks/T001/        ← task_dir（含 .state.yaml，task_id: T001）
tmp_path/agate-workspace/debt/tech-debt.md  ← 兄弟目录
tmp_path/agate-workspace/roadmap/roadmap.md ← 兄弟目录
```

不读取真实仓库的 `agate-workspace/debt/tech-debt.md` / `roadmap.md`，测试结果不依赖仓库实际数据。

## 5. 不提前实现被测对象（dispatch-context 约束 4）

本阶段未创建/修改以下 P4 职责产物：`agate/assets/templates/retrospective-template.md`（尚不存在）、`agate/scripts/agate-feedback.py`（尚不存在）、`agate/scripts/check-retrospective.py`（第 93 行仍是旧文案，未改动）、`agate/state-machine.md`/`agate/AGENTS.md`/`agate/phase-cards/P8-release.md`/`docs/reviews/*.md`（均未改动）。红灯是本阶段的正常且预期结果。
