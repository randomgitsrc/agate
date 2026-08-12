---
phase: P4
task_id: TAG0003-workspace-architecture
type: implementation
parent: P4-review.md
trace_id: TAG0003-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0003 — 工作区架构：P4 评审修复轮实现记录（implementer-review-fix）

> 角色：implementer（评审修复轮，`~/.agate/assets/execution-roles/implementer.md`）。
> 范围：按 P4-review.md（needs-revision）F1/F2 定向修复 + 回归测试 MW.9 + 低危顺手项评估。只改 4 个目标文件（2 脚本 + 1 文档 + 1 测试），未触碰 `~/.agate` 与并行组文件集之外的任何文件。

## 1. 改动清单

### 1.1 `agate/scripts/agate-migrate-workspace.sh`（F1 + F2.1 + 空目标边角）

**F1 — 自动 commit 不再静默失败（选项 A 变体 + 选项 B 必做）**（原 L113-115 → 现 L123-153）：

- **选项 A（hook 跳过 + pathspec 限定）**：commit 改为 `git -c core.hooksPath=/dev/null commit -qm "chore(workspace): migrate legacy docs/tasks layout to workspace" -- <新旧路径成对>`。
- **实证修正 review 推荐的 pathspec 写法**：评审原文建议 pathspec 只给新路径（`-- "$AGATE_TASKS_DIR" "${AGATE_WORKSPACE}/archived"`）。实测（`/tmp/opencode/mwdbg*`）发现**只给新路径的 pathspec 会触发 git partial commit，rename 断裂**——旧路径（docs/tasks）残留在 HEAD，index 留下 staged 删除，需要第二次 commit 才干净。修正为**旧路径 + 新路径成对传入**（delete+add 同 commit 才能表达 rename，实测 HEAD 仅新路径、`git status` 干净、`--follow` 可追到旧 commit）。另实证 pathspec 引用不存在的目录（如未迁移 archived）会导致整条 commit 失败 → 按 `TASKS_MIGRATED`/`ARCH_MIGRATED` 标记条件追加。
- **选项 B（不再吞失败）**：`git commit` 置于 if 条件，失败时输出显式错误「迁移已移动文件，但自动 commit 失败（BDD-8 git 历史未保留），请手工 git commit 完成迁移」+ `exit 1`（不再 `|| true` 吞掉、不再打印"迁移完成"误导用户）。
- **fallback 保护**：外部工作区（fallback 普通 mv，rename 未进暂存区）不再尝试 commit——`GIT_MV_STAGED` 标记只在 git mv 成功时置位；若此时有其他已暂存改动，仅输出 WARNING 不动它们。

**F2.1 — 注释/输出标注**：commit 处补 3 条风险注释（hook 拦截 / 全量 index commit + pathspec 成对说明 / 不吞失败）+ 成功后输出「已自动 commit rename（跳过项目自身 pre-commit hook，git 历史可追溯 BDD-8）」。

**空目标边角（评审 F3 观察）**：`migrate_dir` 目标已存在且为空目录时先 `rmdir` 再 git mv（实测原行为会嵌套 `{dst}/src/...`，rmdir 后平铺正确）。`migrate_dir` 增第 4 参 marker（tasks/archived）供 commit pathspec 判定。

### 1.2 `agate/UPGRADING.md`（F2.2 — 迁移前暂存区提示）

v2.0.0 迁移节 ① 工具前补「迁移前先处理暂存区」提示：工具自动 commit 用 pathspec 只提交迁移目录、不会带上无关已暂存改动，但建议先 `git commit` 或 `git reset`（unstage）掉无关改动，让暂存区只含迁移内容。

### 1.3 `agate/tests/unit/agate-migrate-workspace.bats`（MW.9 回归测试）

新增 MW.9 [BDD-8]：带 pre-commit hook 的 fixture 回归——
- fixture：仓库 docs/tasks 含 TAG0001 任务（.state.yaml 用 v2.0 编号 `^T[A-Z]{2}\d+$`，否则 hook 的 check-state-yaml 先拦）+ 旧版本 P1-dispatch-context-analyst.md（内嵌卡片与当前协议 hash 不一致）+ active-tasks.md；init commit 后按 install-hook 方式软链 pre-commit hook。
- 断言：① 迁移 exit 0 且文件落新路径；② git log 含迁移 commit（旧缺陷下该 commit 缺失 → 红）；③ `git status` 无 docs/tasks 残留（防 partial commit 只提交新路径回归）；④ `--follow` 可追到 init commit；⑤ hook 仍生效（迁移后改 .state.yaml 裸 commit 被卡片校验拦截，防 hook 安装失败导致测试退化失去判别力）。
- TDD 实证：临时还原旧缺陷（裸 commit + `|| true`）→ MW.9 红；恢复修复 → MW.9 绿。

### 1.4 `agate/scripts/pre-commit-gate.sh`（低危顺手项）

L14 注释 `docs/tasks/{Txxx}/` → `{AGATE_WORKSPACE}/tasks/{Txxx}/`（脚本内唯一残留旧路径注释，行为不变）。

## 2. 自查结果（自查≠gate，不声称 P5 已过）

- 全量 bats：unit 530/530（含新 MW.9，基线 529+1）+ regression 17/17 + integration 78/78 + sanity 6/6，全部绿无 `not ok`。
- `shellcheck -S warning agate/scripts/agate-migrate-workspace.sh agate/scripts/pre-commit-gate.sh`：0 告警。
- `python3 agate/scripts/check-protocol-consistency.py`：0 ERROR 全 PASS。
- `bash agate/tests/scripts/count-tests.sh`：625（基线 624 + MW.9 = 预期 +1，无漂移；附录文档无硬编码数字）。

## 3. 偏差与缺口声明

[DESIGN_GAP: P4-review F1 选项 A 原文建议 pathspec 只给新路径（`-- "$AGATE_TASKS_DIR" "${AGATE_WORKSPACE}/archived"`），但实证该写法触发 git partial commit 使 rename 断裂（旧路径残留 HEAD + index 留 staged 删除，BDD-8 需二次 commit 才满足）。实现采用旧路径+新路径成对 pathspec（delete+add 同 commit 表达 rename），并引入 GIT_MV_STAGED 标记避免外部工作区（fallback mv）误触发 commit。选项 A 的意图（跳 hook + 不误提交无关改动）保持不变]

## 4. 低危顺手项评估

| 项（评审第 4 条） | 决定 | 依据 |
|---|---|---|
| pre-commit-gate.sh:14 注释旧路径 | 做（1.4） | 纯注释，零风险 |
| migrate 空目标（已存在空目录）边角 | 做（1.1） | 2 行 rmdir 修复 + 实证平铺 |
| check-pruning 正则转义 | 记录不改 | 评审 F7 已判「不影响正确性底线」；sed 转义脆弱（实证未终止 s 命令），改动风险 > 收益 |
| install-hook 自定义工作区提示 | 记录不改 | 评审 F12 已判「提示性质，不构成行为错误」 |

## 5. 未触碰范围

- 并行组的 6 脚本 / 16 文档 / 8 测试 fixture（core/docs/tests/fix 组产出）；
- `~/.agate`（稳定版 v0.40.2，未动）；
- 除 4 个目标文件与任务文档（本实现记录 + progress 留痕）外的任何文件。

## 6. 环境状态标记

[PROD_NOT_TOUCHED] 本次实现仅改动 worktree `agate/` 下 2 脚本 + 1 文档 + 1 测试文件与任务文档；实证复现与验证均在 `/tmp/opencode/` 临时 fixture 完成；未接触生产环境/生产数据/生产 API；`~/.agate` 稳定版未动。
