---
phase: P4
task_id: TAG0016
type: implementation
parent: P4-review.md
trace_id: TAG0016-P4-reviewfix-20260819
status: draft
created: 2026-08-19
agent: implementer
---

implementation_dir: agate/scripts/

# P4 实现评审修复（CRITICAL-1 / CRITICAL-2）

对应 `P4-review.md`（status: rejected，2 个 CRITICAL）。本轮只修复被 rejected 的两处，不改动
批次 1/2/3 及 SELF-GATE 修复轮已改对的其余内容，不改已有测试的既有断言逻辑。

## CRITICAL-1：`audit7_p5_evidence_reuse` 未检查 `git diff` 返回码

**问题**：`agate/scripts/check-p6-provenance.py:179`（修复前行号）`_run_git` 返回
`(stdout, returncode)`，调用方只用了 `out`，从未检查 `_rc`。当 `p5_pass_commit` 是
`git diff` 无法解析的哈希（历史被 rebase/squash 移除、`.state.yaml` 手工写错、CI 浅克隆
导致该 commit 不在本地历史）时，`git diff` 失败返回空 stdout + 非 0 返回码，原实现把空
stdout 误判为"无改动"→ `reuse_allowed`，本该强制重跑 P5 的场景被静默放行。

**修复方式**（review 推荐的选项 A，fail-closed）：
- 检查 `_run_git` 返回的 `rc`；`rc != 0` 时不再判空 diff，直接 `return "reuse_blocked"`。
- 向 stderr 写独立的诊断消息，明确点出"git 命令本身执行失败"及可能原因（commit 被
  rebase/squash 移除 / `.state.yaml` 手工写错哈希 / CI 浅克隆），与"确实检测到非产出文件
  改动"分支使用不同的 stderr 文案，两种失败不混在同一条消息里。
- 该分支在 `changed` 判定之前提前 return，`p6_declares_reuse` 分支的既有逻辑不受影响。

代码位置：`agate/scripts/check-p6-provenance.py` 的 `audit7_p5_evidence_reuse` 函数（约行
164-201，改动后）。

**新增测试**（2 条）：
- `agate/tests/unit/test_check_p6_provenance.py::test_p4_review_critical1_git_diff_command_fails_fail_closed_reuse_blocked`
  —— 单元级：构造只有一次 init commit 的仓库，`p5_pass_commit` 传入伪造的 40 位十六进制
  哈希（仓库历史里不存在），断言 `audit7_p5_evidence_reuse` 返回 `"reuse_blocked"`，并断言
  stderr 含"命令本身执行失败"，且不含"检测到非产出文件改动"（验证两种失败消息不混淆）。
- `agate/tests/unit/test_check_p6_provenance.py::test_audit7_only_p4_review_critical1_fake_commit_git_fails_exit1`
  —— CLI 级：`--audit7-only` 模式下同样构造伪造哈希写入 `.state.yaml`，断言
  `AUDIT7_RESULT: reuse_blocked` 且退出码为 1（覆盖 review 指出的"`--audit7-only` CLI 模式
  同一函数，同样会退化"这条路径）。

## CRITICAL-2：`redeclares_table` 无范围全文扫描的误报风险

**问题**：`agate/scripts/check-protocol-consistency.py:944-956`（修复前行号）
`redeclares_table` 对指针文件做全文无范围 `finditer` 扫描，而同一 CHECK 里的姊妹函数
`extract_md_table_int_column` 已经用"限定在 `## 重试上限` 小节内"的策略规避"误吞同形态但
语义无关表格行"的问题。`redeclares_table` 没有做同样的限定，指针文件（如
`agate/rules/state-transitions.md`）未来任何一处新增的、恰好形如
`| P{n} | {小整数} |` 的无关表格行，只要碰巧命中 ≥3 组 (phase, value) 组合，就会被误判为
"重新声明了权威表格"。

**修复方式**（按 dispatch-context 指定路径：复用 `extract_md_table_int_column` 同一套小节
裁剪逻辑，不搞两套实现）：
- 把 `extract_md_table_int_column` 内联的小节裁剪逻辑抽取为通用辅助函数
  `extract_section(text: str, heading: str) -> str | None`（定位 `heading` 标题下的正文，
  到下一个同级 `## ` 标题或文件末尾为止；未找到该标题返回 `None`）。
- `extract_md_table_int_column` 改为调用 `extract_section(text, RETRY_LIMIT_HEADING)`
  （`RETRY_LIMIT_HEADING = "## 重试上限"`），行为与修复前完全一致（回归验证：既有测试全绿）。
- `check_authoritative_values` 在调用 `redeclares_table` 前，先用同一个
  `extract_section(text, RETRY_LIMIT_HEADING)` 裁剪出指针文件里对应的「## 重试上限」小节
  文本，只把这段文本传给 `redeclares_table` 扫描；若指针文件根本没有该级别标题，回退为对
  全文扫描（保持与修复前行为一致，不引入新的漏报——当前唯一一条 `pointer_files` 记录
  `agate/rules/state-transitions.md` 确认有该小节标题，实测该回退分支不会被真实文件触发）。
- `must_contain_any` 指针短语检查仍用未裁剪的全文 `text`（指针短语可能不在「## 重试上限」
  小节内，不能收窄）。
- 顺手处理 INFO-1（死配置）：`must_not_redeclare_table` key 此前从未被读取，现改为
  `pf.get("must_not_redeclare_table", True)` 实际参与判断（默认 `True`，向后兼容既有唯一
  一条 `pointer_files` 记录，行为不变）。

代码位置：`agate/scripts/check-protocol-consistency.py`
- 新增 `extract_section`（约行 924-938）
- `extract_md_table_int_column` 改用 `extract_section`（约行 941-956）
- `redeclares_table` 函数体不变，只补充文档说明"调用方须先裁剪小节"的契约（约行 959-976）
- `check_authoritative_values` 调用处（约行 1012-1024）：先裁剪再扫描 + 读取
  `must_not_redeclare_table`

**新增测试**（1 条）：
- `agate/tests/unit/test_check_protocol_consistency.py::test_p4_review_critical2_unrelated_table_outside_section_no_false_positive`
  —— 扩展 `_make_check12_tree`（新增可选参数 `unrelated_table_outside_section`，默认
  `False`，不影响任何既有调用/断言），构造指针文件在「## 重试上限」小节外还有另一张与
  重试上限无关的表格（`| P1 | 3 |` / `| P2 | 3 |` / `| P3 | 2 |`，与权威表数值完全一致、
  命中数 = 3 达到阈值），断言 `check_authoritative_values` 不产生 `CHECK12-authval` 错误
  （0 误报，`"CHECK12-authval" in rep.passed`）。

## INFORMATIONAL 处理情况

- **INFO-1（`must_not_redeclare_table` 死配置）**：已顺手修复（见上，CRITICAL-2 修复的自然
  延伸，成本为零，不修复反而会让新增的裁剪逻辑看起来像"配了却没用"）。
- **INFO-2（`main()` 无顶层 try/except）**：未处理。属于全文件既有写法的加固建议，本轮只
  处理 dispatch-context 明确要求的 2 个 CRITICAL + 关联紧密的 INFO-1，避免范围蔓延。
- **INFO-3（`_load_state_yaml` 的 `except Exception` 吞掉 ImportError 与 YAML 错误）**：
  未处理。退化方向本身是安全的（宁可多跑不可少跑），只是诊断信号缺失，非本轮阻塞项。
- **INFO-4（`MAX=(\d+)` 正则无上下文锚定）**：未处理。已用 grep 核实当前 8 张阶段卡片均
  只有唯一一处 `MAX=`，当前无风险，留作后续技术债观察。

## 自检

- `grep -n "fail-closed\|returncode=" agate/scripts/check-p6-provenance.py` 确认 CRITICAL-1
  改动落盘。
- `grep -n "extract_section\|must_not_redeclare_table" agate/scripts/check-protocol-consistency.py`
  确认 CRITICAL-2 改动落盘。
- 新增测试单独跑（`-k critical1` / `-k critical2`）：全部通过。
- `agate/tests/unit/test_check_p6_provenance.py` + `test_check_protocol_consistency.py`
  单独跑：75 passed。
- 全量 `timeout 180s python3 -m pytest agate/tests/ -q --tb=no`：**966 passed, 2 skipped,
  0 failed**（基线 963 passed + 本轮新增 3 条测试 = 966，无回归）。
