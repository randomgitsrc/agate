---
phase: P4
task_id: TAG0023-mechanism-checks
type: implementation
parent: P2-design.md
trace_id: TAG0023-P4-20260825
status: draft
created: 2026-08-25
agent: implementer
implementation_dir: agate/
---

> [PROD_NOT_TOUCHED] 全部改动落在 worktree `agate/` 目录（协议本体）与 `agate-workspace/roadmap/roadmap.md`（任务数据），未接触任何生产环境/生产数据库/生产 API；`.github/workflows/protocol-tests.yml` 改动为 CI 配置声明性修改，未触发任何实际 CI 运行。

# P4 实现总结 — TAG0023 机制校验补强批（RM-AG0042~0045）

四批并行实现，`dispatch_plan`（P2-design.md）确认的批次边界严格遵守，无跨批文件改动、无冲突。

## 批次与改动文件

| 批次 | RM 编号 | 改动文件 | 对应 BDD |
|------|---------|---------|---------|
| A | RM-AG0042 | `agate/scripts/check-state-transition.py`（新增检查3：对应性校验）+ `agate/rules/state-transitions.md` + `agate/state-machine.md` + `agate/dispatch-protocol.md` + `agate/WORKFLOW.md`（措辞同步） | BDD-1~4 |
| B | RM-AG0043 | `agate/scripts/check-gate.py`（`gate_p8()` 新增 `_check_roadmap_done()`）+ `agate-workspace/roadmap/roadmap.md`（补记 RM-AG0032 done 行，时序调整见下） | BDD-5~7 |
| C | RM-AG0044 | `agate/scripts/check-debt.py`（`_retreat_coverage()` 改用动态 `_short_hash()`）+ 新建 `agate/tests/ENV-SENSITIVE-TESTS.md` + `.github/workflows/protocol-tests.yml`（pytest-rerunfailures） | BDD-8~10 |
| D | RM-AG0045 | `agate/assets/templates/dispatch-prompt.md`（新增"P1/P2 声明写时自检"节）+ `agate/scripts/agate-frontmatter-check.py`（错误消息增强） | BDD-11~13 |

## 编排决策记录：RM-AG0032 时序调整

P2-design.md §2.2 原计划 RM-AG0032 历史补记在 P8 阶段执行，但 P3 已写的 `test_bdd_7_roadmap_rm_ag0032_backfilled_done` 断言属于标准 pytest 套件、且不符合 `known-failures.md`"仅登预存失败、与当前任务无关"的登记条件（本任务自己的 BDD-7）。主 Agent 判定：BDD-7 的验收语义（roadmap.md 存在 RM-AG0032 done 行）不因提前执行而改变，遂将该补记动作提前到本批次（batch B）完成，避免 P5-P7 全程红灯卡住 gate。已在 batch B dispatch-context 中明确记录此决策及理由。

## 验证结果（主 Agent 独立复核，非自述）

- 全量 `pytest agate/tests/`：**1234 passed, 2 skipped**（较 P3 基线 1224 passed 净增 10，即 10 条新测试全部转绿，无回归）
- `check-protocol-consistency.py --strict-errors-only`：exit 0，0 ERROR（321 WARNING 均为改动前已存在的叙事引用，与本次改动无关）
- `ruff check agate/`：All checks passed
- `bash agate/tests/scripts/count-tests.sh`：1236（collect-only 口径，含 2 skipped，单调不降）
- `.github/workflows/protocol-tests.yml` YAML 语法：合法

## 未覆盖的 BDD 说明

- **BDD-9**（连续 5 次 CI 稳定）：无 P3 单元测试，P6 阶段用真实 CI 触发验证（`--reruns 1` 机制已由本批次 C 加入 workflow，等待 P6 实测）
- 所有其余 12 条 BDD（BDD-1~8、10~13）均有对应单元测试且全部通过

## 新增文件核对表

（本仓库未采用骨架/CODE-MAP 机制，本节按 P4 卡片说明省略。）

## [SCOPE+] 声明

无。四批实现均严格按 P2-design.md 已批准范围执行，RM-AG0032 时序调整是编排层面的执行时机决策（不改变 BDD 语义/验收标准），不构成范围外改动。
