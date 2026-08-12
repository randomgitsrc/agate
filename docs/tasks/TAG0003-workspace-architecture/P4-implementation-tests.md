---
phase: P4
task_id: TAG0003-workspace-architecture
type: implementation
parent: P2-design.md
trace_id: TAG0003-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# P4 实现记录 — 测试 fixture 换血（implementer-tests）

## 改动概览

按 P2-design.md §1.1 方案 A，将 8 个既有 .bats 测试文件中的 `docs/tasks` 硬编码路径换血为工作区路径（默认 `agate-workspace/tasks/` 语义，与 `agate-workspace-resolve.sh` 解析器默认一致）。仅换路径，不改用例数、不改测试语义、不动 P3 新增文件。

## files_modified

| 文件 | docs/tasks 换血处数 | 说明 |
|------|---------------------|------|
| `agate/tests/integration/pre-commit-hook.bats` | 247 | 全部 `$REPO/docs/tasks/T001` → `$REPO/agate-workspace/tasks/T001`，含 heredoc 模板内容（dispatch-context 输入文件清单） |
| `agate/tests/integration/dispatch-context-card.bats` | 3 | heredoc 模板内输入文件清单路径 |
| `agate/tests/unit/check-state-transition.bats` | 89（换 80 处，保留 9 处） | 仅换既有用例（ST.1-ST.20 + ST_ARCHIVE.1-6，行 1-588）；**ST_WS.1-4 用例（行 589-662）未动**，其中 ST_WS.4 是 P3 新增的旧布局 docs/tasks 回归守卫，保留 |
| `agate/tests/unit/ci-gate-backstop.bats` | 2 | fixture 任务目录换到 agate-workspace/tasks/T001，与 ci-gate-backstop.py 换血后 tasks_base 一致 |
| `agate/tests/unit/check-pruning.bats` | 0 | **无 docs/tasks 硬编码**（fixture 用 create_task_dir mktemp + `$repo/task`），无需改动 |
| `agate/tests/unit/agate-capture-env-baseline.bats` | 42 | 仅换 `docs/tasks/T00X` 任务路径；`docs/.agate-env-baseline-cache` 缓存目录**未动**（agate-capture-env-baseline.sh 不在本次脚本改动清单，缓存路径仍为 docs/） |
| `agate/tests/unit/dispatch-context-warning.bats` | 4 | fixture 任务目录 |
| `agate/tests/regression/v040-dotarchived-exclusion.bats` | 5 + docs/archived 2 | `docs/tasks` → `agate-workspace/tasks`；`docs/archived` → `agate-workspace/archived`（BDD-18 归档迁入工作区） |

`agate/tests/helpers/fixtures.bash`：**未改**。`create_task_dir` 用 mktemp（P2 §1.1 明确不改）；评估后**未新增** `AGATE_TASKS_DIR` 测试变量——7 个文件统一用字面量 `agate-workspace/tasks/`，与解析器默认一致，无需变量间接层。

## 换血语义

- 字面替换 `docs/tasks/` → `agate-workspace/tasks/`（测试无 `.agate.env`、无 `AGATE_TASKS_DIR` 环境变量时解析器走默认分支，任务根 = `{repo_root}/agate-workspace/tasks`）。
- 涉及模式：`mkdir -p $repo/docs/tasks/...`、`git add docs/tasks/...`、`run bash ... docs/tasks/T001/...`、heredoc 内 dispatch-context 输入文件清单、`agate-retreat-to.sh docs/tasks/T001` 参数（TASK_DIR 由调用方直接传入，换血后指向新路径）。
- 保留用例数：8 文件 @test 数与改动前一致，count-tests.sh 基线 624（603 既有 + 21 P3 新增）无漂移。

## 自查结果（自查≠gate，P5 由 verifier 执行）

- count-tests.sh：624（改动前 624，无漂移）
- sanity + regression + unit + integration：除 1 处红灯外全绿（见下）
- 红灯 1：`unit/agate-render-dispatch-prompt.bats` RP.13「no residual placeholders」——**非本角色文件集**。根因：并行 implementer-docs 已将 `assets/execution-roles/*.md` 与 templates 换用 `{AGATE_WORKSPACE}` 占位符，但 `agate-render-dispatch-prompt.sh`（implementer-core 文件）L109 仅替换 `{agate_root}`/`{Txxx}`，未替换 `{AGATE_WORKSPACE}` → 渲染输出残留。不阻塞本角色换血，记录待 core 在渲染脚本补齐替换。

## DESIGN_GAP / SCOPE+ 声明

- 无 [DESIGN_GAP]：P2 方案对测试换血范围（§1.1）、用例数口径（§3.7）、fixture 变量决策（§1.1「可新增…非强制」）均已明确，未发现歧义。
- 无 [SCOPE+]：未发现 P1/P2 未覆盖的新隐含需求。
- [PROD_NOT_TOUCHED]：仅改动 worktree `agate/tests/` 下测试 fixture，未触碰 `~/.agate`（v0.40.2 稳定版开发工具）、脚本、协议文档。

## 协调事项（不阻塞）

1. RP.13 红灯来自并行组交接：docs 已改模板占位符 `{AGATE_WORKSPACE}`，core 需在 `agate-render-dispatch-prompt.sh` 补替换（若渲染脚本消费方确认该占位符应被替换）。
2. `agate-retreat-to.bats`（不在本角色 8 文件集内）仍含 `docs/tasks` fixture 路径——若后续一致性检查（BDD-20 白名单）覆盖它，需单独换血或由 core/docs 组处理。
