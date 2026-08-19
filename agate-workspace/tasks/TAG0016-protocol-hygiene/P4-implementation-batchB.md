---
phase: P4
task_id: TAG0016
type: implementation
parent: P2-design.md
trace_id: TAG0016-P4b-20260819
status: draft
created: 2026-08-19
agent: implementer
---

implementation_dir: agate/scripts/

## 摘要

实现 P2-design.md §2 选定的候选 2（结构化权威锚点扫描），在 `agate/scripts/check-protocol-consistency.py`
中新增 **CHECK 12（权威数值/规则跨文件一致性，BDD-9/10）**，覆盖当前唯一注册的锚点 `retry-max`（阶段重试上限）。

## 改动内容

文件：`agate/scripts/check-protocol-consistency.py`

1. 文件头 docstring 编号表追加一行：
   `CHECK 12  权威数值/规则跨文件一致性（防复发，锚点表：重试上限表 vs 指针文件/内联值）  (对应 BDD-9, BDD-10)`
2. 新增三个函数 + 一张锚点表（插入在 CHECK 11 之后、`# ── 主流程 ──` 之前）：
   - `extract_md_table_int_column(path)`：从「## 重试上限」小节提取 `{阶段: 数值}`。**关键设计点**：
     只扫描该小节文本（截至下一个 `## ` 标题或文件末尾），不对整文件做无范围正则扫描——
     `agate/state-machine.md` L30 有一行同形态的任务追踪表行 `| P4 | 0 | YYYY-MM-DD |`，若不限定
     section 范围会被误吞进权威值提取，虽然最终会被 L394 真实 `| P4 | 3 |` 行覆盖（字典按顺序覆写，
     碰巧不影响最终结果），但这是脆弱的隐患，限定 section 后从根本上消除。
   - `redeclares_table(text, authoritative)`：统计文本中命中权威表 `(phase, value)` 组合的行数，
     ≥3 组同时命中判定"重新声明了完整表格"（阈值 3，遵循 P2-design.md §2.3 附注的理由）。
   - `AUTHORITATIVE_VALUE_ANCHORS`：含 1 条 `retry-max` 锚点，`authoritative_file` =
     `agate/state-machine.md`，`pointer_files` = `[{"file": "agate/rules/state-transitions.md", ...}]`，
     `must_contain_any` = `["权威源", "详见", "见 agate/state-machine.md"]`（读取批次1迁移后真实文本
     `详见 \`state-machine.md\`《重试上限》——权威唯一来源`，含"详见"子串，匹配成功），
     `inline_value_files` = `[{"glob": "agate/phase-cards/P*-*.md", "extract": r"MAX=(\d+)", ...}]`。
   - `check_authoritative_values(root, rep)`：遍历锚点表，逐条比对 pointer_files（重声明判定 + 指针短语
     存在性）和 inline_value_files（内联数值与权威表逐阶段比对），0 error 时 `rep.ok("CHECK12-authval")`。
3. `CHECKS` 列表追加：`("CHECK 12 权威数值/规则跨文件一致性", check_authoritative_values)`。

未改动任何 `agate/*.md` 协议文档，未改动 `agate/tests/unit/*.py` 测试代码。

## 与批次1真实文档的对照（锚点表设计依据）

- `agate/state-machine.md` L385-398：权威表实际表头列名为 `MAX_RETRY`（非设计伪代码里的 `MAX`），
  故 `extract_md_table_int_column` 按列**位置**（第1列阶段、第2列数值）解析，不依赖列名文本，
  天然兼容真实列名。
- `agate/rules/state-transitions.md` L56-58：迁移后确认为纯指针句
  `详见 \`state-machine.md\`《重试上限》——权威唯一来源，本文件不重复维护。`，不含数值表格行，
  `redeclares_table` 对其判定为 False，`must_contain_any` 命中"详见"，0 ERROR。
- 8 张 `agate/phase-cards/P{1-8}-*.md` 的 `MAX=` 内联行核实与权威表逐阶段一致
  （P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2）。`P0-orchestrator.md` 同样匹配 glob
  `P*-*.md` 但不含 `MAX=` 文本，`re.search` 返回 None 被安全跳过，不误报。

## 测试结果（自查，非 P5 gate）

```
timeout 60s python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -v
```
23 passed（含全部 7 条 CHECK 12 相关用例）：
`test_bdd_9_checks_list_registers_check12` / `test_bdd_9_authoritative_value_anchors_retry_max_registered` /
`test_bdd_9_check12_mismatched_inline_max_reports_error` / `test_bdd_9_check12_consistent_values_zero_error` /
`test_bdd_10_check12_no_false_positive_on_existing_precommit_pointers` /
`test_bdd_5_check12_pointer_file_missing_phrase_reports_error` /
`test_bdd_5_check12_pointer_redeclares_table_reports_error` 全部变绿；文件内其余既有 CHECK 9/1-5 用例
（16 条）未被破坏，测试代码本身未改动。

```
timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict
```
CHECK 12 一栏显示 `✅ PASS`，全仓 **0 ERROR**（`ERROR (` 汇总行未出现，`rep.errors` 为空）。exit code 为 2
是因为 `--strict` 把既有的 308 条 WARNING（叙事文件死链引用类，与本批次改动无关，批次1之前已存在）
计入失败，不含任何 ERROR 或 FAIL 项；不加 `--strict` 时 exit code 为 0。

```
timeout 180s python3 -m pytest agate/tests/ -q --tb=no
```
8 failed, 951 passed, 2 skipped（objective_info 预期"失败数从 15 降到 8"已达成，且 8 条失败全部落在
`test_check_p6_provenance.py`（4 条，批次3 audit7 范围）+ `test_protocol_dedup_audit.py`（3 条，批次3范围）+
`test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff`（1 条，ruff lint，与本批次
无关），无一属于 CHECK 12/本批次改动范围）。

以上均为自查，不代表 P5 gate 已通过。

## SCOPE+ / DESIGN_GAP / CLARIFY

无。P2-design.md §2 伪代码提供的实现导航已足够清晰落地为可运行代码，未发现设计歧义需要自主决策，
未发现范围外隐含需求。DEBT0010（`agate-read-gate-commands.py` L31）不在本批次改动文件范围内，
按 dispatch-context 约束 8 判断不顺手处理（改动文件不同，非必要，留给后续任务）。
