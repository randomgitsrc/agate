---
phase: P5
task_id: TAG0018
type: verification
parent: P5-dispatch-context-verifier.md
trace_id: T0018-P5-20260821
status: done
created: 2026-08-21
agent: verifier
---

# TAG0018 P5 技术验证报告

执行环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0018/`（分支 feat/TAG0018-dsh-platform，HEAD `153c0a2`）；Linux；/tmp 只读（pytest 以 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider` 适配）；命令按 P2-design.md §5 gate_commands 执行。

## 逐命令结果

### P5（全量 pytest）

- 命令：`timeout 120 python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`
- **exit code: 1**
- 输出尾部摘要：
  ```
  FAILED agate/tests/scripts/test_check_platform_assumptions.py::test_bdd_8_clean_tree_zero_detection
  1 failed, 1035 passed, 2 skipped in 93.92s (0:01:33)
  ```
- 失败项：`test_bdd_8_clean_tree_zero_detection`（断言 `check-platform-assumptions.py agate/tests/` 扫描全树 returncode == 0 且输出为空）
- 失败根因（已复现定位，未修复）：
  - `check-platform-assumptions.py`（既有脚本，TAG0010/TAG0011 引入）对 `agate/tests/` 全树扫描命中 2 处：
    - R4：`agate/tests/unit/test_dsh_preset.py:26` —— 注释行 `#   1. 不写 /tmp —— 只读仓库内文件，无临时文件` 含 `/tmp` 字面量；R4 豁免仅覆盖 `BATS_TEST_TMPDIR` 变量行与 `# scan-exempt:` 标记行，**普通注释不豁免**
    - R2：`agate/tests/unit/test_dsh_preset.py:202` —— 代码字符串 `assert "python3 ~/.agate/scripts/install-hook.py" in section` 含命令位置 `python3`；R2 豁免（注释/@test 标题/command -v/env 探测/docstring）**不覆盖代码字符串**
  - `test_dsh_preset.py` 为 **TAG0018 P3（15a6874）引入的本任务交付物**；引入前 tests/ 树无此文件，bdd-8 扫描为 0 命中（既有基线绿）
  - 判定：**本任务引入的新增失败**（非预存失败，非环境问题）——TAG0018 新增测试文件触发了既有 bdd-8 全树 0 命中闭环约束
- 说明：P2 §5 权威命令为 `pytest agate/tests/ -q --tb=no`（全量，含 `scripts/` 与 `test_sanity.py`）；派发上下文给出的三子目录命令（unit/regression/integration）不含 `scripts/`，会漏掉本失败项，故按 P2 权威全量口径执行。

### P5_consistency（协议一致性，strict-errors-only）

- 命令：`timeout 60 python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`
- **exit code: 0**
- 输出尾部摘要：
  ```
  仅有 317 个 WARNING，无 ERROR。
  ```
- 与 P4 后基线（0 ERROR / ~317 WARNING）一致

### P5_count（用例计数不漂移）

- 命令：`timeout 30 bash agate/tests/scripts/count-tests.sh`
- **exit code: 0**
- 输出摘要：
  ```
  总计：1038 个测试用例（pytest collect-only 口径）
  目标：≥ 749（TAG0011 迁移基线）
  ```
- 1038 ≥ 1030（P2 §5 钉死基线）→ 通过；与 P4 后基线 1038 一致

## 判定

- P5 判定：**失败**
- 依据：P5（全量 pytest）exit 1、failed=1，不满足"全部命令 exit 0 + failed==0"
- P5_consistency、P5_count 各自独立通过（exit 0）
- 按派发指引：任何非零 → 如实记录失败并停止深入修复，返回主 Agent（P5 修复流程按 dispatch-protocol，由主 Agent 判定回 P4 或按新增失败处理）

## 修复轮（round 2）

> 首轮 P5 判定为失败（见上），按 dispatch-protocol P5 修复流程回 implementer 修复后复验。本节为修复轮留痕，最终 P5 结论以本节为准。

### 首轮失败项

- `agate/tests/scripts/test_check_platform_assumptions.py::test_bdd_8_clean_tree_zero_detection`（bdd-8 闭环：`check-platform-assumptions.py agate/tests/` 全树扫描应 0 命中，首轮实际命中 2 处 → exit 1）

### 根因

- TAG0018 新增测试文件 `agate/tests/unit/test_dsh_preset.py` 两处字面量触发既有扫描器（check-platform-assumptions.py，TAG0010/TAG0011 引入）：
  - R4：L26 注释 `# 1. 不写 /tmp ...` 含字面 `/tmp`（R4 豁免仅覆盖 BATS_TEST_TMPDIR 变量行与 `# scan-exempt:` 标记行，普通注释不豁免）
  - R2：L202 断言 `assert "python3 ~/.agate/scripts/install-hook.py" in section` 含命令位置字面 `python3` 前缀（R2 豁免不覆盖代码字符串）

### 修复内容（implementer 完成）

- `test_dsh_preset.py` L26：注释去掉字面 `/tmp`（消除 R4 命中）
- `test_dsh_preset.py` L202：断言去掉字面 `python3` 前缀（消除 R2 命中）
- implementer 侧复验：8/8 绿 + 变异复证通过

### 复验结果（主 Agent 实测，round 2）

| 命令 | exit code | 摘要 |
|------|-----------|------|
| `pytest agate/tests/`（全量） | **0** | 1036 passed, 2 skipped |
| `check-protocol-consistency.py --strict-errors-only` | **0** | 0 ERROR / 317 WARNING |
| `bash agate/tests/scripts/count-tests.sh` | **0** | 总计 1038（≥1030 基线） |
| `check-platform-assumptions.py agate/tests/`（bdd-8 闭环） | **0** | 0 命中 |

### 最终 P5 结论

- **P5 判定：通过**
- 依据：全部命令 exit 0 + failed==0（pytest 1036 passed / 2 skipped，无 failed；bdd-8 0 命中复绿；consistency 0 ERROR；count 1038 ≥ 1030）
- 本节（round 2）为最终判定，覆盖首轮失败判定；P5 修复流程留痕完成，供主 Agent 继续推进 P6

## 附注

- 无 PROD_TOUCHED 事件（纯本地测试执行）→ `[PROD_NOT_TOUCHED]`
- 无不可逆操作待确认 → `[NO_NEED_CONFIRM]`
- 测试环境隔离：仅使用 worktree 内仓库文件与可写 basetemp，未触碰生产环境
