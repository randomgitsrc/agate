---
phase: P4
task_id: TAG0014-dispatch-orchestration
type: review
parent: P4-implementation.md
trace_id: TAG0014-P4-20260816
status: approved
created: 2026-08-16
agent: review
---

[PROD_NOT_TOUCHED]

# P4 实现评审（复评轮）— agate 派发编排机制（TAG0014-dispatch-orchestration）

评审角色：review（偏执 Staff Engineer）。本轮为复评轮：上轮判定 rejected（1 CRITICAL + 3 建议），implementer 已修复，本文件复核修复是否解决全部发现项。只审不写，[PROD_NOT_TOUCHED]。

**结论：0 个 CRITICAL → status: approved。** 上轮 CRITICAL 已修复并闭环，2 条负向用例补齐全绿，stale 声明已对齐；全量 780 passed + 2 skipped + 0 failed，consistency 0 ERROR，count-tests 782。无回归。

---

## 复评轮逐项复核

### 1. [CRITICAL] check-gate.py mode 非 str 崩溃 → ✅ 已修复

- **修复落点**：agate/scripts/check-gate.py:314
  ```python
  if not isinstance(mode, str) or mode not in valid_modes:
  ```
  `isinstance(mode, str)` 前置已置于 frozenset 成员测试之前，`{mode: [single]}`（list）/ `{mode: {a: b}}`（dict）不再触发 `TypeError: unhashable type`，干净输出 `GATE P2 ERROR` + exit 1。
- **闭环验证**：新增负向用例 `test_dispatch_plan_mode_non_string`（test_dispatch_orchestration.py:186-193）——Given `{mode: [single]}`，断言 returncode == 1 且 output 含 "GATE P2 ERROR"，无 traceback。**该用例执行通过**（10 passed）。
- **手动复现**（progress 记录）：implementer 已按上轮复现命令验证 `{mode: [single]}` → GATE P2 ERROR + exit 1。

### 2. 负向用例补全（上轮 Pass 2 #1 建议）→ ✅ 已补齐

| 建议用例 | 落点 | 断言 | 执行 |
|---------|------|------|------|
| `{mode: [single]}` → exit 1 + GATE P2（BDD-6/CRITICAL 闭环） | test_dispatch_orchestration.py:186 | returncode==1 + "GATE P2 ERROR" | ✅ |
| `complexity: invalid` → ERROR（BDD-5 子场景②） | test_dispatch_orchestration.py:196-206 | returncode==1 + "GATE P2 ERROR" | ✅ |

- 两分支原为自动化覆盖缺口（check-gate.py:314 / :332），现均已纳入。**单文件实测 10 passed**（8 既有 + 2 新增），与 BDD-19 规定的 8 条逐字一致 + 修复轮 2 条负向补强，无 contract 违背。

### 3. P4-implementation.md stale 声明对齐 → ✅ 已对齐

- §1.3：README badge 修复轮已还原 v0.48.0（`git diff README.md` 为空），版本 bump 归 P8——声明与现状一致。
- §2.2：已改为修复轮后最终状态「778 passed + 2 skipped + 0 failed」，并对 test_con_1/test_bdd_25/test_con_6 三条逐条说明（YAML 加引号 + badge 还原），不再声称"预期失败"。
- §3：两条 DESIGN_GAP（P2 YAML `why:` 加引号、badge 还原）均标「已解决」。
- §1.1：check-gate.py 改动已记录「修复轮：mode 校验加 isinstance(str) 前置（修复 review CRITICAL）」。
- §2.3 / §4：#6 全量 780 passed + 2 skipped，count-tests 782，#7 consistency 0 ERROR。
- **注意**：§1.3 中「tests/README.md 计数 8→10 待 P5 一致性核对同步」——该文件目前仍写 `8`，属已知延迟项（上轮建议 3），P5 verifier 应核对同步，非本 P4 阻塞。

### 4. parallel_limit bool 采纳与否（上轮建议 3，可选）→ 未采纳，不阻塞

- check-gate.py:318 仍为 `not isinstance(parallel_limit, int) or parallel_limit < 1`。bool 是 int 子类，`parallel_limit: true` 会被当作 1 放行。
- 上轮已标注「可选 / 无实际风险（YAML 正常写法是数字）」，dispatch-context 明确「确认是否采纳（可选）」。未采纳不构成缺陷，维持 INFORMATIONAL，接受现状。

---

## 修复回归复核（Pass 1/Pass 2 快速重扫）

- **上轮 Pass 1 其余 INFORMATIONAL**（空 dict `{}` → ERROR、标量坏值静默跳过、op 层 json.dumps 遇 YAML 特殊类型）——均为设计取向/已知边界，非 CRITICAL，本复评维持原判，无需修复。
- **TOCTOU / 路径 / 竞态**：`_md_field_get` 只读子进程、dispatch_plan 校验纯读 P2-design.md，无 read-check-write。无发现。
- **测试覆盖抽查**：dispatch_plan 10 条全绿；check-gate 既有用例无改动（test_check_gate.py 未修改，见实现记录 §5）；mdf 16/17 计数一致。
- **向后兼容**：test_dispatch_plan_optional 逐行断言 `gate_with.output == gate_without.output`，无 dispatch_plan 字段任务行为等同现状——锁定未破坏。

## 实测数据（本复评轮自行执行）

| 项 | 结果 |
|----|------|
| test_dispatch_orchestration.py | 10 passed in 1.00s |
| test_check_gate.py + test_agate_md_field_get.py | 140 passed in 8.63s |
| 全量 pytest | **780 passed, 2 skipped in 65.82s**（0 failed） |
| check-protocol-consistency.py | **0 ERROR**（279 WARNING 既有叙事基线） |
| count-tests.sh | **782**（≥ 749 达标） |

## 结论

**0 个 CRITICAL。** 上轮唯一 CRITICAL（check-gate.py:314 mode 非 str 崩溃）已按建议修复（isinstance str 前置），并由 `test_dispatch_plan_mode_non_string` 闭环；建议 1（complexity invalid 负向用例）已采纳；建议 2（stale 声明对齐）已落地；建议 3（parallel_limit bool，可选）未采纳但非阻塞。全量回归无回归，consistency 0 ERROR，count-tests 782。

**status: approved。** 仅剩的已知非阻塞项：tests/README.md 用例计数 `dispatch_plan | 8` 需在 P5 一致性核对时同步为 10。
