---
phase: P4
task_id: TAG0007
type: implementation
parent: P2-design.md
trace_id: TAG0007-P4-gate-script-both-20260820
status: draft
created: 2026-08-20
agent: implementer
---
implementation_dir: agate/

## 改动范围

只改动 `agate/scripts/check-gate.py`，在 `gate_p2`/`gate_p4`/`gate_p7` 三个函数内新增判定分支。未改动测试文件、未改动其他函数、未改动任何 `.md` 文档/`CODE-MAP.md`。

## 1. gate_p2（BDD-1/3）

插入位置：`_gate_p2_ui_design_section` 检查通过之后、最终 `sys.stderr.write(...) + return 2` 之前（`gate_p2` 函数末尾）。

逻辑：
- 用既有 `_frontmatter_field(p1_file, "project_phase")` 读取 P1-requirements.md 的 `project_phase` 字段。
- `project_phase == "bootstrap"`：检查 `task_dir/P2-skeleton.md` 是否存在且文本含 `"## 骨架声明"`。缺失或缺标题 → `sys.stderr.write(...)` 含 `"P2-skeleton.md"` 字样，`return 1`。存在且含标题 → 不拦截，继续走到原有 `return 2`。
- `project_phase` 缺失或非 `"bootstrap"`（含显式 `"established"`）：完全跳过该分支，不产生任何 `"P2-skeleton.md"` 相关输出（回归对照）。

关联 BDD：BDD-1（bootstrap 骨架声明校验）、BDD-3（字段缺失/established 回归无变化）。

## 2. gate_p4（BDD-4/7/10）

在现有"暂存区含代码文件 → return 0 / 否则 return 1"逻辑基础上重构为：先扫描暂存区判定 `has_code_file`（无代码文件仍 `return 1`，行为不变），有代码文件时不再立即 `return 0`，而是先做 WARNING 检查，再统一 `return 0`（exit code 行为不变，WARNING 不阻断）。

WARNING 触发条件（AND）：
1. 暂存区含代码文件（已判定）
2. `task_dir/P2-skeleton.md` 存在 **或** `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在（OR 条件，骨架/CODE-MAP 机制已采用）
3. `task_dir/P4-implementation.md` 正文不含 `"## 新增文件核对表"` 标题

满足则 `sys.stderr.write(...)` 含 `"WARNING"` 与 `"新增文件核对表"` 字样，`return 0`（不阻断）。判定逻辑完全不读取/不分支 `change_type` 字段（BDD-10：`change_type: refactor` 任务同样触发，不豁免）。

`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径解析见下方 DESIGN_GAP。

关联 BDD：BDD-4/7（WARNING 机制）、BDD-10（refactor 不豁免）。

## 3. gate_p7（BDD-8/9/10）

插入位置：现有 DESIGN_GAP pairing 检查段（含 N3 review 实质锚点 WARNING）之后、函数末尾 `return 0` 之前，作为并行独立检查段，不与 DESIGN_GAP 逻辑共享变量。

读取 P7-consistency.md frontmatter 的 `code_map_new_files_count` / `code_map_reviewed_count`（读取方式见下方 DESIGN_GAP，非字面照搬 `_md_field_get`）。

- 两字段均缺失 → 机制未采用，两层校验全部跳过，不触发任何 `"CODE_MAP"` 相关输出（回归对照）。
- 两字段均存在时，跑两层校验：
  - **内部一致性层**：`code_map_reviewed_count < code_map_new_files_count` → `sys.stderr.write(...)` 含 `"CODE_MAP"`，`return 1`（仿照 `dg_reviewed < dg_count` 分支）。
  - **转抄核对层**：正则数 `P4-implementation.md` 正文中 `[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT` 两种标记的实际出现次数（`r"^\s*-?\s*\[CODE_MAP_UPDATED\]"` / `r"^\s*-?\s*\[CODE_MAP_EXEMPT"`），若该计数 **>** `code_map_new_files_count`（不是 `code_map_reviewed_count`）→ `sys.stderr.write(...)` 含 `"CODE_MAP"`，`return 1`。
  - 两层均通过 → 不拦截，继续原有流程直到函数末尾 `return 0`。
- `change_type` 字段完全不读取、不分支（BDD-10：两层校验对 refactor 任务同样生效）。

关联 BDD：BDD-8/9（两层 pairing 硬校验）、BDD-10（refactor 不豁免）。

## DESIGN_GAP 声明

[DESIGN_GAP: dispatch-context 建议 gate_p7 用 `_md_field_get` 读取 `code_map_new_files_count`/`code_map_reviewed_count`（与既有 `design_gap_count` 读取方式一致），但 `agate-md-field-get.py` 的 `KNOWN_OPS` 允许列表尚未注册这两个新字段名，且该文件不在本批次允许改动范围内（只能改 `check-gate.py`）——若照字面调用 `_md_field_get`，子进程会因 unknown op `sys.exit(2)`，`_md_field_get` 恒回退为空字符串，导致两层校验永远被判定为"机制未采用"而跳过，会使 3 个 gate_p7 新增测试失败。改为使用本文件已有的纯本地函数 `_frontmatter_field(path, field)`（同文件内定义，无子进程/无 allowlist 限制）直接从 P7-consistency.md frontmatter 块取值，行为等价（frontmatter-only、无正文回退语义，因为 `_frontmatter_field` 本身只扫描 `---` 块内的行，不会误读正文散文）。若后续有其他改动把这两个字段注册进 `agate-md-field-get.py` 的 `NO_FALLBACK_INT_FIELDS`，可切回 `_md_field_get` 以保持代码风格统一，非阻塞项。]

[DESIGN_GAP: `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 的路径解析方式 P2-design.md 未给出函数级精确规格（dispatch-context 已明确指出这是本批次需自主决策的空间，P3 测试只覆盖 `P2-skeleton.md` 分支）。本实现采用 dispatch-context 建议的推导方式：`task_dir` 通常形如 `{AGATE_WORKSPACE}/tasks/{Txxx}`，从 `task_dir` 向上两级到 workspace 根，再拼接 `agents/CODE-MAP.md`——即 `os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(task_dir))), "agents", "CODE-MAP.md")`。此推导依赖"task_dir 是 `{AGATE_WORKSPACE}/tasks/{Txxx}` 的两级嵌套"这一约定，若与项目实际工作区解析机制（`agate_common.py` 的 `_resolve_workspace` 或 `.agate.env`）不一致（例如 workspace 根不由目录层级推导，而是显式配置/环境变量），需要后续对齐为读取同一权威解析源，而不是本地重新推导路径。测试套件未覆盖此分支（仅覆盖 `P2-skeleton.md` OR 条件的另一侧），因此该风险在当前测试下不可见，需人工/主 Agent 确认是否与实际部署布局相符。]

## 自查测试结果

- 12 个新增测试全部 PASSED：
  - `test_bdd_1_bootstrap_missing_skeleton_exit_1`
  - `test_bdd_1_bootstrap_with_skeleton_title_exit_2`
  - `test_bdd_3_field_missing_no_regression_exit_2`
  - `test_bdd_3_established_explicit_no_regression_exit_2`
  - `test_bdd_4_7_gate_p4_warning_when_table_missing`
  - `test_bdd_4_7_gate_p4_no_warning_when_table_present`
  - `test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1`
  - `test_bdd_8_9_gate_p7_transcription_mismatch_exit_1`
  - `test_bdd_8_9_gate_p7_paired_matches_exit_0`
  - `test_bdd_8_9_gate_p7_mechanism_not_adopted_no_check`
  - `test_bdd_10_gate_p4_refactor_not_exempt_warning`
  - `test_bdd_10_gate_p7_refactor_not_exempt_pairing_check`
- 既有测试无回归：`agate/tests/unit/test_check_gate.py` 全量 159 passed（0 failed）；`agate/tests/unit` 全量 gate 相关用例（`-k "check_gate or check-gate or gate"`）898 passed, 2 skipped（既有 skip，与本次改动无关）。
- `git status --porcelain agate/scripts/` 确认只改动 `check-gate.py` 一个文件。

（本文件为自查记录，不代表 P5 gate 已通过。）
