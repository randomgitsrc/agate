---
phase: P5
task_id: TAG0012-protocol-mechanism-fixes
type: test-results
parent: P4-implementation.md
trace_id: TAG0012-P5-20260818
status: draft
created: 2026-08-18
agent: verifier
---

[NO_NEED_CONFIRM]
[PROD_NOT_TOUCHED]

# P5 技术验证结果 — TAG0012

四条 `gate_commands.P5*` 命令（P2-design.md §6 权威声明）在当前 worktree HEAD（含 P4 commit
27509a2）下由 verifier subagent 独立串行实跑，工作目录固定
`/home/kity/oclab/agate/.worktrees/agate-TAG0012`。RM-AG0016 判定本任务全量 pytest 属资源密集型
命令，按"资源密集型默认串行"规则，四条命令依次执行，不拆分并行。

## 命令 1/4：`python3 -m pytest agate/tests/ -q --tb=no`（gate_commands.P5）

- exit code：**0**
- 结果：**909 passed, 2 skipped in 89.76s (0:01:29)**，**0 failed**
- 与 P4 阶段已知基线（909 passed + 2 skipped）完全一致，无新增失败，无预存失败
- 本任务新增 `test_protocol_mechanism_anchors.py` 的 28 条锚点用例包含在全量结果中，独立复核见下方
  命令签名证据

### 测试运行器输出签名证据（N5 残余风险缓解，真实命令输出片段）

为满足"签名要求"（可被 `grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)'` 命中），补跑同一测试
选择集、追加 `-rA` 标志（不改变测试范围/结果，只是让 pytest 额外打印逐条 PASSED/FAILED 短摘要）：

命令：`python3 -m pytest agate/tests/ -q --tb=no -rA`（结果集与命令 1 完全一致，独立确认一遍）

```
909 passed, 2 skipped in 94.94s (0:01:34)
```

短摘要片段（`short test summary info`，逐条真实测试结果，节选，完整片段见
`P5-test-results/pytest-rA-summary.txt`）：

```
PASSED agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_1_readme_triggers_warning
PASSED agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_2_trigger_no_review_warning
PASSED agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_3_trigger_with_review_no_warning
PASSED agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_4_trigger_with_skip_no_warning
PASSED agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_5_scripts_sh_triggers
...
PASSED agate/tests/unit/test_protocol_mechanism_anchors.py::test_anchor_present[BDD-19]
PASSED agate/tests/unit/test_protocol_mechanism_anchors.py::test_anchor_present[BDD-20]
PASSED agate/tests/unit/test_protocol_mechanism_anchors.py::test_anchor_present[BDD-21]
PASSED agate/tests/unit/test_review_role_docs.py::test_bdd_1_analyst_classification_framework
...
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:21: Pillow 已安装，跳过无 Pillow 分支
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:51: Pillow 已安装，跳过无 Pillow 分支
909 passed, 2 skipped in 94.94s (0:01:34)
```

- `grep -cE '^PASSED' pytest-rA-summary.txt` = **909**（=全部 passed 用例数，逐条真实签名）
- `grep -cE '^FAILED' pytest-rA-summary.txt` = **0**
- `test_protocol_mechanism_anchors.py` 的 28 个 `test_anchor_present[BDD-*]` parametrize 用例
  独立核对：`grep -c 'test_protocol_mechanism_anchors.py::test_anchor_present' pytest-rA-summary.txt`
  = **28**（28/28 全绿，与 P4-implementation.md 自查结论一致）

## 命令 2/4：`python3 agate/scripts/check-protocol-consistency.py --strict`（gate_commands.P5_consistency）

- exit code：**2**（脚本既定语义，非"命令失败"：`check-protocol-consistency.py` L992-993
  `if rep.warnings and args.strict: return 2` —— `--strict` 模式下存在 WARNING 即返回 2，区别于
  ERROR 触发的 exit 1）
- 结果：**0 ERROR，279 个 WARNING**
- CHECK 1/3/4/6/7/8/9/11 全部 `✅ PASS`
- 279 条 WARNING 全部为"叙事文件引用旧路径/脚本名"类提示（如历史任务文档引用已归档/重命名的
  `docs/tasks/...`、`scripts/*.sh` 旧文件名），与 P4 阶段已知基线（0 ERROR，279 WARNING）**完全一致**
  ——不是本次改动引入的新问题，逐条比对详见下方原始输出片段

原始输出片段（尾部汇总，节选自实际命令执行输出）：

```
  ✅ PASS  CHECK 1  YAML 代码块可解析
  ✅ PASS  CHECK 3  协议文件无硬编码行号
  ✅ PASS  CHECK 4  gate_commands 键集合一致
  ✅ PASS  CHECK 6  LICENSE 与 gstack 归属
  ✅ PASS  CHECK 7  version badge 与 git tag
  ✅ PASS  CHECK 8  v0.6 关键词存在性
  ✅ PASS  CHECK 9  协议-脚本结构对齐
  ✅ PASS  CHECK 11 UI/UX 机制条文跨文档一致
  仅有 279 个 WARNING，无 ERROR。
```

完整输出见 `P5-test-results/consistency-strict-output.txt`。

## 命令 3/4：`bash agate/tests/scripts/count-tests.sh`（gate_commands.P5_count）

- exit code：**0**
- 结果：

```
=== pytest 用例覆盖度自检 ===
总计：911 个测试用例（pytest collect-only 口径）

目标：≥ 749（TAG0011 迁移基线，BDD-1）；迁移期数值单调逼近 749。
```

- 911 = 909 passed + 2 skipped（命令 1 结果），口径完全对齐；≥ 749 基线满足

## 命令 4/4：`shellcheck -S warning agate/scripts/*.sh`（gate_commands.P5_shellcheck）

- exit code：**0**
- 结果：**0 个 warning/error**（无任何输出）
- 扫描文件（3 个，RM-AG0016 判定本任务不改 `.sh`，仅回归确认，符合 P2-design.md §2.2「不改什么」）：
  - `agate/scripts/commit-msg-self-gate.sh`
  - `agate/scripts/pre-commit-gate.sh`
  - `agate/scripts/pre-push-gate.sh`

## 汇总

| 命令 | exit code | 关键计数 |
|------|-----------|---------|
| 1 pytest 全量 | 0 | 909 passed, 2 skipped, 0 failed |
| 2 consistency --strict | 2（既定语义，非失败） | 0 ERROR, 279 WARNING |
| 3 count-tests.sh | 0 | 911 个测试用例 |
| 4 shellcheck | 0 | 0 问题 |

- **预存失败**：无。未发现改动前就存在、与本任务无关的失败，未登记 `known-failures.md`。
- **新增失败**：无。
- **PROD_TOUCHED**：`[PROD_NOT_TOUCHED]`，本次全部命令均为本地测试/脚本检查，无生产环境接触。
- **不可逆操作**：`[NO_NEED_CONFIRM]`，本阶段全部为只读验证，无数据删除/迁移类操作。
- 四条命令均由 verifier subagent 在本次会话中独立实跑（非抄主 Agent 已跑结果），与 P4 阶段快照
  （P4-implementation.md / P4-review.md / docs/reviews/agate-alignment-review-TAG0012.md）报告的结论
  一致，确认 commit 落盘过程中无意外遗漏。
