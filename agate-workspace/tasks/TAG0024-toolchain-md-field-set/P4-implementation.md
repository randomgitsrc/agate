---
phase: P4
task_id: TAG0024
type: implementation
parent: P2-design.md
trace_id: TAG0024-P4-20260825
status: draft
created: 2026-08-25
agent: implementer
---

> 本文件是 3 个并行批次（P2-design.md dispatch_plan：`md-field-set-tool` / `check-gate-debt-fixes` /
> `phases-yaml-consistency`）实现说明的合并汇总，由主 Agent 做轻量拼装（拼接各批次产出，无跨
> 批次交叉修改）。各批次完整实现细节/自跑证据保留在各自的 `P4-implementation-{batch-id}.md` 中，
> 本文件只做顶层索引 + 统一字段声明 + 主 Agent 独立复核记录。

## implementation_dir

```yaml
implementation_dir: agate/scripts/
```

三批次改动分布（零文件交叉，与 P2-review.md 核验的 dispatch_plan 一致）：
- `agate/scripts/agate-md-field-set.py`（新建，批次 `md-field-set-tool`）
- `agate/scripts/agate-md-field-set-gate-commands.py`（新建，批次 `md-field-set-tool`）
- `agate/assets/templates/dispatch-prompt.md`（修改，批次 `md-field-set-tool`，BDD-19）
- `agate/assets/templates/dispatch-context.md`（修改，批次 `md-field-set-tool`，BDD-19）
- `agate/scripts/check-gate.py`（修改，批次 `check-gate-debt-fixes`，DEBT0019/20）
- `agate/rules/phases.yaml`（修改，批次 `phases-yaml-consistency`，RM-AG0049/50）

以及三批次各自的测试代码（P3 阶段产出，P4 让其转绿）：
- `agate/tests/unit/test_agate_md_field_set.py`（新建于 P3，P4 转绿 + 修复 BDD-16 fixture 缺陷 + ruff lint 清理）
- `agate/tests/unit/test_check_gate.py`（P3 追加，P4 转绿）
- `agate/tests/unit/test_check_structure_consistency.py`（P3 追加，P4 转绿）

**第四批次（SELF-GATE 触发，BDD-30 `[SCOPE+ from P4]`，见 P1-requirements.md）**：
- `agate/assets/templates/dispatch-context.md`（修复，SELF-GATE 语义对齐审查 A1/A2 MISALIGNED：FILE 调用语法从位置参数误写改为 env var 语法）
- `agate/scripts/check-pruning.py`（修复，SELF-GATE 语义对齐审查 A4：`_staged_source_count()` 两处 `run_git` 调用加 `cwd=task_dir`，测试隔离缺陷根治）
- `agate/tests/unit/test_check_pruning.py`（追加回归测试 `test_p2_6f_*` + 3 个既有用例补 `GIT_CEILING_DIRECTORIES` env，兼容本仓库强制的 `--basetemp=.pytest-tmp` 场景）
- `agate/adr.md`（新增 ADR-011，用户拍板：引导型 CLI 工具的权限是早纠错，不是安全边界）

## 新增文件核对表

本仓库未采用骨架（无 `P2-skeleton.md`）或 CODE-MAP（`agate-workspace/agents/CODE-MAP.md` 不存在）机制，本节按 P4 卡片规则可省略。

## 主 Agent 独立复核记录（非采信各批次自述）

主 Agent 已对三批次产出逐一独立核验，并额外发现 2 处批次自查未覆盖的问题并已派发修复：

1. **批次 md-field-set-tool**：`git diff --stat` 确认 `agate-frontmatter-check.py`/`agate-md-field-get.py`/`check-judge-verdict.py` 零改动；`grep spec_from_file_location` 确认真实用 importlib 动态加载，非复制粘贴。首轮自跑 34/35（BDD-16 因测试 fixture 缺陷失败）——**主 Agent 诊断确认该 BDD-16 失败是 P3 测试设计遗留的 fixture 数据缺陷（非实现问题）**，已派 test-designer 角色定向修复（只改 `test_bdd_16_*` 函数 5 行，其余 34 个测试函数逐字节未变），复核后 35/35 转绿。**主 Agent 额外发现批次自查未跑 ruff**：全仓 `~/.venvs/agate-dev/bin/ruff check agate/` 命中 9 处 lint 问题，全部集中在本批次 3 个文件（其余批次文件干净）——已派修复轮（纯格式清理，不改逻辑），复核后 `ruff check agate/` 全仓 0 errors。
2. **批次 check-gate-debt-fixes**：`git diff` 逐行确认改动只在 `_check_roadmap_done()`（新增 `_ROADMAP_EXPECTED_COLS = 9` 常量 + 精确匹配）与 `gate_p8()` 的 `roadmap_path` 构造（改用 `_git(["rev-parse", "--show-toplevel"])` 仓库根锚定 + 非 git 环境区分性提示），未见其他函数改动。独立重跑 `test_check_gate.py`：182 passed，0 failed。
3. **批次 phases-yaml-consistency**：`git diff` 确认改动只是追加（`id: P4` outputs 追加一行 + `id: P6.5` 前追加纯注释块），未改变任何既有字段结构（`id`/`gates`/`retry_cap`/`task_fields` 逐一核对未变）。独立重跑 `test_check_structure_consistency.py`：17 passed，0 failed。

**SELF-GATE 触发 protocol-alignment-review**（`docs/reviews/agate-alignment-review-2026-08-25-TAG0024.md`）独立实跑发现两处真实问题（主 Agent + implementer 均已复核确认）：
- A1/A2 MISALIGNED：`dispatch-context.md` 新增的 set 工具调用指引语法错误（FILE 误作位置参数）——已修复，实测验证。
- A4 NEEDS_HUMAN_REVIEW：全量 pytest 在当前暂存区状态下实测 3 failed（`test_check_pruning.py`），根因为 `check-pruning.py._staged_source_count()` 读取真实外层仓库暂存区而非隔离仓库——经用户明确人工确认（`[HUMAN_CONFIRMED]`），增补 BDD-30（`[SCOPE+ from P4]`）在本任务内修复：第 1 轮 `cwd=task_dir`（根因修复）+ 第 2 轮 `GIT_CEILING_DIRECTORIES`（兼容本仓库强制的 `--basetemp=.pytest-tmp`），两轮均独立复核，全仓 1285 passed/0 failed。
- A7（建议项，非阻塞）：用户拍板"现在就补"，已新增 `agate/adr.md` ADR-011。

**全仓整合验证（最终，含 SELF-GATE 修复后）**：
- `python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q` → **1285 passed, 2 skipped, 0 failed**
- `~/.venvs/agate-dev/bin/ruff check agate/` → **All checks passed**
- `shellcheck -S warning agate/scripts/*.sh` → 0 warning/error
- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → exit 0（仅历史归档任务的既有 WARNING，非本次改动引入）
- `bash agate/tests/scripts/count-tests.sh` → 1287 个测试用例（远超 749 基线），与 pytest collect 口径一致
- `python3 agate/scripts/check-scope-resolved.py` → exit 0（BDD-30 的 `[SCOPE+]`/`[SCOPE_RESOLVED]` 配对通过）

## 各批次完整实现说明

详见：
- `P4-implementation-md-field-set-tool.md`
- `P4-implementation-check-gate-debt-fixes.md`
- `P4-implementation-phases-yaml-consistency.md`
