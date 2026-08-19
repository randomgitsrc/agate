---
phase: P5
task_id: TAG0016
type: test-results
parent: P4-implementation.md
trace_id: TAG0016-P5-20260819
status: draft
created: 2026-08-19
agent: verifier
---

[NO_NEED_CONFIRM]
[PROD_NOT_TOUCHED]

# P5 技术验证结果 — TAG0016

worktree HEAD 实跑：`0738075`（与 dispatch-context `<objective_info>` 声明一致，工作区干净）。
工作目录：`/home/kity/oclab/agate/.worktrees/agate-TAG0016`（worktree 自己的 `agate/`，未碰
`~/.agate`）。

## gate_commands.P5（P2-design.md §6 权威声明，原样执行）

```
python3 -m pytest agate/tests/ -q --tb=no && python3 agate/scripts/check-protocol-consistency.py --strict && bash agate/tests/scripts/count-tests.sh
```

按 dispatch-context 约束 1，用 `timeout 200s bash -c '...'` 整条串联实跑一次（原始输出见
`gate-chain-output.txt`）：

- **链路整体 exit code：2**
- **链路在第 2 步后中断**：`check-protocol-consistency.py --strict` 返回 2 触发 `&&` 短路，
  第 3 步 `count-tests.sh` **未在链路内执行到**。这是脚本自身既定语义（非命令执行失败）：
  `agate/scripts/check-protocol-consistency.py` L1129-1133：
  ```python
  if rep.errors:
      return 1
  if rep.warnings and args.strict:
      return 2
  return 0
  ```
  即 `--strict` 模式下"仅有 WARNING、无 ERROR"也返回 2，与"有 ERROR"（返回 1）在语义上不同。
  为了拿到第 3 步的真实结果（而不是因链路中断而缺失数据），逐步单独复核如下。

## 逐步单独复核（同一 HEAD 下独立执行，确认真实结果）

### 步骤 1/3：`python3 -m pytest agate/tests/ -q --tb=no`

- exit code：**0**
- 结果：**966 passed, 2 skipped in 96.37s (0:01:36)**，**0 failed**
- 与 dispatch-context 预期基线（966+ passed / 0 failed / 2 skipped）完全一致

### 测试运行器输出签名证据（N5 残余风险缓解）

补跑同一测试选择集、追加 `-rA` 标志（不改变测试范围/结果，只让 pytest 额外打印逐条
PASSED/FAILED 短摘要），结果集与步骤 1 完全一致：

```
966 passed, 2 skipped in 100.89s (0:01:40)
PYTEST_EXIT=0
```

完整片段见 `pytest-rA-summary.txt`（985 行）。签名统计（真实命令输出，非人工编造）：

- `grep -cE '^PASSED' pytest-rA-summary.txt` = **966**
- `grep -cE '^FAILED' pytest-rA-summary.txt` = **0**

短摘要节选（`short test summary info`，节选自 `pytest-rA-summary.txt`）：

```
PASSED agate/tests/unit/test_review_role_docs.py::test_bdd_17_p6_card_evidence_form_by_shape
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:21: Pillow 已安装，跳过无 Pillow 分支
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:51: Pillow 已安装，跳过无 Pillow 分支
966 passed, 2 skipped in 100.89s (0:01:40)
```

### 步骤 2/3：`python3 agate/scripts/check-protocol-consistency.py --strict`

- exit code：**2**（脚本既定语义，见上方 L1129-1133 引用，非"命令执行失败"）
- 结果：**0 ERROR，308 个 WARNING**
- CHECK 1/3/4/6/7/8/9/11/12 全部 `✅ PASS`；CHECK 2（仓库内文件引用存在）、CHECK 10（协议文档
  脚本名引用漂移）为 `⚠️ WARN`
- 与 dispatch-context 预期基线（0 ERROR，308 条与本任务无关的既有 WARNING）**完全一致**——
  308 条 WARNING 逐条为"叙事文件引用旧路径/已归档文档/已重命名脚本名"类提示（如
  `docs/plans/agate-test-plan-2026-07-01.md`、`docs/reviews/postmortem-template.md`、
  `scripts/check-gate.sh` 等历史任务文档引用），非本任务改动引入的新问题
- 完整输出见 `gate-chain-output.txt`（该文件即链路整体实跑的完整输出，含此步骤的完整 WARNING 清单）

### 步骤 3/3：`bash agate/tests/scripts/count-tests.sh`（独立执行，因链路在步骤 2 中断未跑到）

- exit code：**0**
- 结果：
  ```
  === pytest 用例覆盖度自检 ===
  总计：968 个测试用例（pytest collect-only 口径）

  目标：≥ 749（TAG0011 迁移基线，BDD-1）
  ```
- 968 ≥ dispatch-context 预期基线（≥ 961），符合"本轮修复轮又新增了 3 条测试"的预期方向
  （P4 阶段最后一次统计 961 → 本轮 968，净增 7，未低于基线，无用例计数漂移/丢失）

## 汇总

| 步骤 | exit code | 关键计数 |
|------|-----------|---------|
| 链路整体（`&&` 串联，原样执行）| 2 | 在步骤2后中断，步骤3未在链路内执行到 |
| 1 pytest 全量 | 0 | 966 passed, 2 skipped, 0 failed |
| 2 consistency --strict | 2（脚本既定语义，非失败）| 0 ERROR, 308 WARNING |
| 3 count-tests.sh（独立执行）| 0 | 968 个测试用例 |

- **新增失败**：无。pytest 全量 0 failed，逐条 PASSED 签名核对（966/966）确认无遗漏。
- **预存失败**：无 pytest 失败可标注。若把"consistency --strict 链路整体 exit=2"计入广义
  "预存现象"：308 条 WARNING 与本任务改动无关（dispatch-context 已声明为既有基线），且该
  exit-2-on-warning-only 是 `check-protocol-consistency.py` 脚本自身一直如此的既定行为
  （非本任务引入），不阻塞本任务判定，但如实记录供主 Agent 判断"gate_commands.P5 用 `&&` 串联
  三条命令、其中一条按设计在 WARNING-only 时也返回非 0"这一命令设计本身是否需要在后续任务中调整
  （不属于 verifier 职责范围内的自行判定，仅如实记录客观事实）。
- **PROD_TOUCHED**：`[PROD_NOT_TOUCHED]`，全部命令均为本地测试/脚本检查，无生产环境接触。
- **不可逆操作**：`[NO_NEED_CONFIRM]`，本阶段全部为只读验证，无数据删除/迁移类操作。
- 全部命令均由 verifier subagent 在本次会话独立实跑（链路整体跑一遍 + 逐步单独复核一遍，
  pytest 额外跑一遍 `-rA` 拿签名），非抄录他人已跑结果。
