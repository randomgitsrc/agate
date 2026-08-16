---
phase: P3
task_id: TAG0014-dispatch-orchestration
type: test-cases
parent: P2-design.md
trace_id: TAG0014-P3-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

[PROD_NOT_TOUCHED]

# P3 测试用例 — dispatch_plan 字段契约（TAG0014-dispatch-orchestration）

> test_code_dir: agate/tests/unit/
> gate_commands.P3: `python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py agate/tests/unit/test_agate_md_field_get.py -q --tb=no`
> 现状红灯实测（2026-08-16，P3 自检）：10 条新增用例全部红灯，14 条既有 mdf 用例全绿。红灯原因均为"功能未实现"（op 未注册 exit 2 / check-gate P2 不校验 return 2），无测试自身 bug。

## 1. 测试范围

P1 BDD-19 的 8 条契约用例（5 正向 + 3 负向，覆盖 BDD-1~7）+ op 层 2 条（S2，BDD-1/7 的 op 层验证）。

| # | 测试文件 | 测试用例 | 对应 BDD | 用例数 |
|---|---------|---------|---------|-------|
| 1-8 | `agate/tests/unit/test_dispatch_orchestration.py`（新建） | 8 条（5 正向 + 3 负向） | BDD-19（覆盖 BDD-1~7） | 8 |
| 9-10 | `agate/tests/unit/test_agate_md_field_get.py`（追加） | test_mdf_16 / test_mdf_17 | BDD-1、BDD-7 | 2 |

## 2. 测试设计

### 2.1 新建 test_dispatch_orchestration.py（8 条）

fixture 复用：`task_dir`（create_task_dir factory）/ `agate_scripts` / `python_exe`（探测 `python3|python`）/ `run_cli` / `tmp_path`。参照 `test_check_gate.py` 的 `_write_p2_design` + `add_p2_review` 模式（P2 门文件模板：frontmatter `agent/candidate_count` + 正文 `packages/domains/ui_affected/gate_commands` 四字段 + 权衡描述，保证 gate 既有检查通过，dispatch_plan 是唯一变量）。

#### 正向 5 条（BDD-19 正向）

| 用例 | BDD | 前置（Given） | 动作（When） | 断言（Then） |
|------|-----|--------------|-------------|-------------|
| `test_dispatch_plan_required_fields` | BDD-1 | P2-design.md frontmatter 含 `dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [...]}` | 跑 `agate-md-field-get.py dispatch_plan`（env FILE） | 输出合法 JSON（`json.loads` 成功）；含 `mode` 且 ∈ {single, static-batch, parallel, recon-then-split, serial}；parallel_limit 存在时 ≥ 1 |
| `test_dispatch_plan_mode_valid` | BDD-3 | frontmatter 含 `dispatch_plan: {mode: xyz}` | 跑 `check-gate.py P2` | returncode == 1；output 含 `GATE P2` |
| `test_dispatch_plan_batch_granularity` | BDD-5 | frontmatter 含 `dispatch_plan: {mode: static-batch, ..., batches: [{id: B1, complexity: medium}, {id: B2, complexity: low}]}` | 跑 op | JSON 中 batches 各含 `id` 且 `complexity` ∈ {low, medium, high}；另有 `{mode: single}`（无 batches）→ gate returncode == 2 |
| `test_dispatch_plan_parallel_limit` | BDD-6 | frontmatter 含 `dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [2 批]}` | 跑 op + gate | JSON 中 batch 数 ≤ parallel_limit（缺省 3）；gate returncode == 2 |
| `test_dispatch_plan_optional` | BDD-2 | 一组含 dispatch_plan（`{mode: parallel, parallel_limit: 2}`）、一组不含 | 分别跑 op + gate | 含字段时 op 输出合法 JSON；两门 gate 输出逐行一致（`gate_with.output == gate_without.output`）且均 exit 2 |

#### 负向 3 条（BDD-19 负向）

| 用例 | BDD | 前置（Given） | 动作（When） | 断言（Then） |
|------|-----|--------------|-------------|-------------|
| `test_dispatch_plan_malformed_yaml` | BDD-7 | frontmatter 含 `dispatch_plan: {mode: [unclosed`（YAML 解析失败） | 跑 op + gate | op returncode == 0 且输出空（按缺字段处理，不崩溃）；gate returncode == 2 且 output 无 `ERROR` |
| `test_dispatch_plan_parallel_limit_zero` | BDD-4 | frontmatter 含 `dispatch_plan: {mode: parallel, parallel_limit: 0}` | 跑 gate | returncode == 1；output 含 `GATE P2` |
| `test_dispatch_plan_batch_missing_complexity` | BDD-5 子场景① | frontmatter 含 `dispatch_plan: {mode: static-batch, batches: [{id: B1}]}`（缺 complexity） | 跑 gate | returncode == 1；output 含 `GATE P2` |

### 2.2 追加 test_agate_md_field_get.py（2 条，S2 / op 层）

参照既有 `_run_mdf` 封装（env FILE + op），仅追加不破坏既有 14 例。

| 用例 | BDD | 前置（Given） | 动作（When） | 断言（Then） |
|------|-----|--------------|-------------|-------------|
| `test_mdf_16_dispatch_plan_frontmatter_json` | BDD-1 | P2.md frontmatter 含单行 flow `dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [...]}` | 跑 op `dispatch_plan` | returncode == 0；`json.loads` 成功；`plan["mode"] == "static-batch"`；`plan["parallel_limit"] == 3` |
| `test_mdf_17_dispatch_plan_dict_json_output` | BDD-1/7（I4） | P2.md frontmatter 含 `dispatch_plan: {mode: single}` | 跑 op `dispatch_plan` | returncode == 0；输出经 `json.loads` 为 dict（非 Python repr 单引号）；output 不含 `'` |

## 3. 红灯状态与原因（P3 自检记录）

gate_commands.P3 实跑：`10 failed, 14 passed`（14 = test_agate_md_field_get.py 既有用例，全绿无回归）。

| 红灯分组 | 失败点 | 失败原因（均为"功能未实现"） |
|---------|-------|------------------------------|
| op 层 7 条（required_fields / batch_granularity / parallel_limit / optional / malformed_yaml + mdf_16 / mdf_17） | `assert 2 == 0` | `agate-md-field-get.py` KNOWN_OPS 未注册 `dispatch_plan` → main() exit 2 "unknown op"（P2-design minimal_validation ① 已实测确认） |
| gate 负向 3 条（mode_valid / parallel_limit_zero / batch_missing_complexity） | `assert 2 == 1` | `check-gate.py` gate_p2 分支不读取/校验 dispatch_plan → return 2（主 Agent 自判）而非 1 |

无 A 类错误（无 SyntaxError/ImportError）——测试代码自身正确，红灯全部指向待实现功能。TDD 红灯成立。

## 4. 测试代码落盘

- 新建 `agate/tests/unit/test_dispatch_orchestration.py`（8 条，BDD-19）
- 追加 `agate/tests/unit/test_agate_md_field_get.py`（+2 条，test_mdf_16/17，对应 BDD-1/7）
- 平台无关：`python_exe` 探测（不裸 python3）、`tmp_path`（不用 /tmp）、无 PATH 硬编码、无 POSIX symlink 假设
- ruff check 通过（0 问题）

## 5. P4 实现参考（测试驱动提示）

- op 层：`agate-md-field-get.py` 新增 `import json` + `JSON_FIELDS = frozenset({"dispatch_plan"})`；`_format_value` 置顶 dict/list → `json.dumps(value, ensure_ascii=False)` 分支；`_get` 无正文回退集合并入 JSON_FIELDS；KNOWN_OPS 注册（P2-design §3.1）
- gate 层：`check-gate.py` gate_p2 复用 `_md_field_get("dispatch_plan", p2_file)`，非空 → `json.loads` 校验（mode 枚举 / parallel_limit≥1 / batch id+complexity / 批数≤limit），命中 ERROR 在 return 2 之前 return 1；解析失败或空 → 跳过（P2-design §3.1）
- 断言契约：gate 错误信息以 `GATE P2` 前缀 + returncode 1 为界（匹配 check-gate 既有消息约定，不锁定具体文案措辞，避免 P4 文案选择差异导致误红）
