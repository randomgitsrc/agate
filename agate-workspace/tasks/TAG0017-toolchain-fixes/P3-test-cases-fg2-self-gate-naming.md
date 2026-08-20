## 批次 fg2-self-gate-naming（BDD-7/8）

test_code_dir: `agate/tests/unit/test_self_gate_naming_docs.py`

被测文档（不属于测试代码本身，供实现阶段定位）：
- `SELF-GATE.md`（仓库根目录，无 `agate/` 前缀）L48-60（文件类型表）、L133/143（变更触发模式派发模板）、L183/193（全量审查模式派发模板）
- `agate/assets/review-roles/protocol-alignment-review.md` L100-119（闭环规则 + 人工验收清单）

### BDD-7: 同日不同任务的 SELF-GATE 审查文件不再同名覆盖

- Given 两个不同任务（如 TAG0015 与 TAG0016）在同一日期各自触发 protocol-alignment-review
- When 两次审查各自按 `SELF-GATE.md` 模板生成留痕文件与成果文件
- Then 两次生成的文件名不同（命名模板含任务标识），两次产出互不覆盖

对应测试用例：

| 测试函数 | 断言点 | 当前结果 |
|---|---|---|
| `test_bdd_7_self_gate_path_has_no_agate_prefix` | 前置校验：`SELF-GATE.md` 确实在仓库根目录（非 `agate/SELF-GATE.md`），确保后续断言的路径解析前提正确 | PASS（路径本已正确，非本批次待改动内容） |
| `test_bdd_7_file_type_table_progress_filename_has_task_id` | 文件约定表（L48-60）留痕文件命名模板含 `{task_id}`，且等于 `docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md` | **FAIL（红灯）** |
| `test_bdd_7_file_type_table_result_filename_has_task_id` | 文件约定表成果文件命名模板等于 `docs/reviews/agate-alignment-review-{date}-{task_id}.md` | **FAIL（红灯）** |
| `test_bdd_7_change_triggered_template_naming_has_task_id` | 变更触发模式派发模板段（原 L133/143）留痕/成果文件命名模板均含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_full_review_template_naming_has_task_id` | 全量审查模式派发模板段（原 L183/193）留痕/成果文件命名模板均含 `{task_id}` | **FAIL（红灯）** |
| `test_bdd_7_naming_template_produces_distinct_filenames_for_different_task_ids` | 纯字符串格式化模拟：命名模板一旦补上 `{task_id}` 占位符，同日两个不同 task_id 生成的留痕/成果文件名确实互不相同（验证 BDD-7 判定逻辑本身可判定，不依赖协议文档当前状态） | PASS（逻辑自证，非文档状态断言） |

### BDD-8: subagent 写入前检查目标路径存在性，避免误覆盖历史记录

- Given protocol-alignment-review subagent 即将用 Write 工具写入审查产出路径
- When 目标路径已存在同名文件
- Then subagent 先判断该文件是否属于同一任务的复核轮（可覆盖）还是别的任务遗留（不可覆盖，需改用带任务标识的新文件名），不无条件覆盖

对应测试用例：

| 测试函数 | 断言点 | 当前结果 |
|---|---|---|
| `test_bdd_8_protocol_alignment_review_has_write_precheck_logic` | `protocol-alignment-review.md` 含 "Write 前" 与 "目标路径" 关键词说明 | **FAIL（红灯）** |
| `test_bdd_8_write_precheck_distinguishes_same_task_vs_other_task` | 同一文档区分"同一任务/同一批次可覆盖" vs "不可覆盖" 两种判断分支的说明 | **FAIL（红灯）** |

### 红灯确认

`cd agate && python3 -m pytest tests/unit/test_self_gate_naming_docs.py -v`

结果：8 个测试，6 FAILED（真实 AssertionError，B 类：项目内文档内容断言失败，非语法/第三方 import 错误）、2 PASSED（路径前置校验 + 纯逻辑自证测试，按设计本就应为绿）。

红灯原因逐一核实：
- `SELF-GATE.md` 当前留痕/成果文件命名模板（文件类型表 + 两处派发模板共 6 处出现）均为 `docs/reviews/agate-alignment-{date}-{NN}.progress.md` / `docs/reviews/agate-alignment-review-{date}.md`，不含 `{task_id}` 占位符。
- `agate/assets/review-roles/protocol-alignment-review.md` 全文 grep "test -f|写入前|Write 前|目标路径" 无命中，当前无 Write 前存在性检查逻辑说明。

### 自检确认

- 未修改 `SELF-GATE.md` 或 `agate/assets/review-roles/protocol-alignment-review.md` 本身（只读取，未 Edit/Write）。
- `SELF-GATE.md` 路径引用统一为 `agate_root.parent / "SELF-GATE.md"`（即仓库根目录，无 `agate/` 前缀），并新增了显式的路径前置断言测试防止本批次再次写错路径。
