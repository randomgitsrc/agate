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

# TAG0003 — 工作区架构：P4 定向修复轮实现记录（implementer-fix）

> 角色：implementer（fix 轮，`~/.agate/assets/execution-roles/implementer.md`）。
> 范围：只改 3 个脚本（`check-protocol-consistency.py` / `install-hook.sh` / `agate-render-dispatch-prompt.sh`），解决 SCOPE_GAP（2 个）+ RP.13 红灯（1 个）。未改动这三个文件集之外的任何文件。

## 1. 改动清单

### 1.1 `agate/scripts/check-protocol-consistency.py`（[SCOPE_GAP] 补做，BDD-20 白名单重校准）

`PATH_IGNORE_SUBSTRINGS`（L65-78）：
- `"docs/tasks/"`（L72，运行时任务目录）→ 替换为 `"agate-workspace/"`（v2.0 工作区运行时目录，覆盖 tasks/agents/archived/reviews/...）。
- `"docs/agents/"`（L69，项目侧 orchestrator 安装位置示例）→ 保留，注释重校准为「旧布局项目侧 project.md 位置（v2.0 起迁移到工作区 agents/）」——P2 §3.7 明确保留作为旧布局兼容，协议文档（orchestrator-template / UPGRADING）仍有旧布局检测说明引用该路径。
- `"{"` 注释同步补 `{AGATE_WORKSPACE}` 占位符说明。

验证：`python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR 全 PASS（CHECK 1/2/3/4/6/7/8/9）。

### 1.2 `agate/scripts/install-hook.sh`（[SCOPE_GAP] 补做，BDD-6）

L87 `.gitignore` 检测提示文字：`git add docs/tasks/` → `git add agate-workspace/tasks/`（v2.0 工作区默认 tasks 路径，与解析器默认分支一致）。

验证：`install-hook.bats` 5/5 绿（现有断言 `.state.yaml`+`忽略` 关键词不受影响）。

### 1.3 `agate/scripts/agate-render-dispatch-prompt.sh`（RP.13 红灯修复）

- 根因：implementer-docs 已把 `assets/templates/dispatch-prompt.md` 换用 `{AGATE_WORKSPACE}` 占位符（5 处：L20/25/43/46/135），但渲染脚本 sed 仅替换 `{agate_root}`/`{Txxx}` 等，`{AGATE_WORKSPACE}` 残留 → RP.13「no residual placeholders」红灯。
- 修复：新增 `AGATE_WORKSPACE_RENDER="$(dirname "$(dirname "$TASK_DIR")")"`（L110）——TASK_DIR 恒为 `{AGATE_WORKSPACE}/tasks/{Txxx}` 布局，反推工作区根即 dirname 两层；相对/绝对、workspace/legacy 布局均自洽。sed 新增 `-e "s|{AGATE_WORKSPACE}|${AGATE_WORKSPACE_RENDER}|g"`（L114）。
- 语义验证：用 `/tmp/opencode/demo-repo/agate-workspace/tasks/TAG0001-demo` 作 TASK_DIR 渲染，`{AGATE_WORKSPACE}/tasks/{Txxx}/...` 正确解析为 `/tmp/opencode/demo-repo/agate-workspace/tasks/TAG0001-demo/...`，无残留占位符。

## 2. 自查结果（自查≠gate，不声称 P5 已过）

- `python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR。
- `bats agate/tests/unit/agate-render-dispatch-prompt.bats` → 16/16 绿（RP.13 转绿）。
- `bats agate/tests/unit/install-hook.bats` → 5/5 绿（回归确认）。
- `shellcheck -S warning agate/scripts/agate-render-dispatch-prompt.sh agate/scripts/install-hook.sh` → 0 告警。
- `bash agate/tests/scripts/count-tests.sh` → 总计 624 用例，无漂移。

## 3. 偏差与缺口声明

无 [DESIGN_GAP]：dispatch-context 对三个改动的语义目标（SCOPE_GAP 补做 / RP.13 补替换）均已明确，未发现歧义。

无 [SCOPE+]：未发现 P1/P2 未覆盖的新隐含需求。

## 4. 实现对照（P2 方案 A）

| P2 要求 | 实现落点 |
|---|---|
| §1.1 check-protocol-consistency.py 白名单重校准（L72） | 1.1 ✓ |
| §1.1 install-hook.sh 提示文字路径（L87） | 1.2 ✓ |
| RP.13 render-dispatch-prompt 补 `{AGATE_WORKSPACE}` 替换 | 1.3 ✓ |

## 5. 未触碰范围

- 并行组的 6 脚本 / 16 文档 / 8 测试 fixture（core/docs/tests 组产出，工作树中未动）；
- `~/.agate`（稳定版 v0.40.2，未动）；
- 除 3 个目标脚本与任务文档（本实现记录 + progress 留痕）外的任何文件。

## 6. 环境状态标记

[PROD_NOT_TOUCHED] 本次实现仅改动 worktree `agate/scripts/` 下 3 个脚本与任务文档，未接触任何生产环境/生产数据/生产 API；`~/.agate` 稳定版未动。
