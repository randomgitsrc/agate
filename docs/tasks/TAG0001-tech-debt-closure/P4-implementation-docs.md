---
phase: P4
task_id: TAG0001-tech-debt-closure
type: implementation
parent: P2-design.md
trace_id: TAG0001-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0001 — 技术债登记闭环：P4 实现记录（implementer-docs 文档/卡片/规则同步面）

> 角色：implementer-docs（P4 并行 implementer 之一，只改文档/卡片/规则/同步面）。
> 输入：P4-dispatch-context-implementer-docs.md（派发指引）+ P2-design.md（§0.1 改动面表 + §2.5/2.6/2.7）+ P1-requirements.md（BDD-1/2/3/4/12/16/17/18/19/20）+ P0-brief.md + AGENTS.md。
> 环境标记：`[PROD_NOT_TOUCHED]` 本次只改 worktree `agate/` 文档与 docs/tasks/ 记录，未接触生产环境、未改 `~/.agate`（稳定版 v0.40.2 开发工具未动）。

## 改动清单（10 个文件集，均按 P2-design.md 方案实现）

### 1. `agate/phase-cards/P8-release.md`（BDD-16/17/18）
- 执行方式新增第 4 步「确认债务清单：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在），在 P8-release.md 写入 `debt_check:` 字段（TAG0001 Phase 3）」；原第 4 步变第 5 步并纳入 debt_check 产出。
- 产出规格新增 `debt_check: none / reviewed` 字段说明：`none` 是合法选项（本次无关注项），gate 只查字段存在（缺失 → exit 1）、不查内容达标、不因存在未关闭债务阻断发布。
- gate 规则节新增 `debt_check` 字段存在性条目（缺失 → exit 1；内容任意含 none/未关闭债务 → 不阻断，BDD-17）。

### 2. `agate/rules/state-transitions.md`（BDD-12/19）
- 回退规则节（agate-retreat-to.sh 段落之后）新增「**回退落地后必须建 DEBT 条目（TAG0001 强制）**」：任何正式回退（`retreat:` 提交）完成后必须建立 `source: retreat` 的 DEBT 条目，`evidence` 引用 retreat 提交哈希；模板见 `assets/templates/tech-debt-template.md`，登记于 `{AGATE_WORKSPACE}/debt/tech-debt.md`；事后 `check-debt.sh --retreat-coverage` 只读比对 WARNING（不阻断 commit/发布）。

### 3. `agate/phase-cards/P6-acceptance.md` L144（BDD-12）
- FAIL > 0 回退流程段末尾补「**回退落地后必须建 DEBT 条目**」（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 + state-transitions 引用）。

### 4. `agate/phase-cards/P4-implementation.md` L27（BDD-12）
- 从更后阶段退回的重派段落末尾补同一 DEBT 强制语（模板 + state-transitions 引用）。

### 5. `agate/assets/review-roles/plan-eng-review.md` L19（BDD-19/20 可发现性）
- 追加「**若提出'后续应重构 / 存在架构债'，须用标准 DEBT 条目格式**」：模板 `assets/templates/tech-debt-template.md`，`evidence` 必填，登记于 `{AGATE_WORKSPACE}/debt/tech-debt.md`——强制格式、不强制产出。

### 6. `agate/WORKFLOW.md`（BDD-1）
- L79「固定 8 个子目录」→「固定 9 个子目录」。
- 目录图（L81-91）加 `├── debt/  # 技术债登记（tech-debt.md，模板见 assets/templates/tech-debt-template.md）`，位于 agents/ 之后。
- `agents/` 注释 `# agent 知识（project.md / memory / tech-debt）` → `# agent 输入知识（project.md / memory）`（归类修正，去 tech-debt）。

### 7. 三处 mkdir 8→9 子目录（BDD-2，同一字面量集 `{roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt}`）
- `agate/orchestrator-template.md` L102：mkdir 加 `,debt`，文字「创建工作区 8 个子目录」→「9 个子目录（roadmap/tasks/agents/archived/reviews/decisions/plans/logs/debt，debt/ 为技术债登记目录）」。
- `agate/SETUP.md` L114：mkdir 加 `,debt`。
- `agate/state-machine.md` L40-41：mkdir 加 `,debt`，注释「创建 8 个子目录」→「9 个子目录」。

### 8. `agate/UPGRADING.md`（BDD-3）
- §3 新增 `### v0.43.0 — 技术债登记闭环 + 工作区子目录 8→9` 变更节：① 子目录集 8→9（存量项目 `mkdir -p {AGATE_WORKSPACE}/debt` 可选启用，不建行为不变）；② tech-debt.md 路径 `{AGATE_WORKSPACE}/debt/tech-debt.md`（不再指向 agents/）；③ P8-release.md 新增 `debt_check` 必填字段；④ 回退落地须建 DEBT 条目。

### 9. `agate/scripts/check-protocol-consistency.py` + `agate/scripts/README.md`（[SCOPE+] #2）
- SCRIPT_ALIGNMENT_ANCHORS 新增 `check-debt.sh` 锚点（desc「tech-debt schema 校验 + 回退覆盖比对（DEBT 条目）」、keywords `["debt", "retreat"]`）。
- scripts/README.md「Gate 检查」表补录 `check-debt.sh` 行；「检查逻辑工具」.py 表补录 `agate-debt-check.py` 行。

### 10. TAG0003 口径重验修订注（BDD-4）
- `docs/tasks/TAG0003-workspace-architecture/P1-requirements.md` BDD-1 + `P6-acceptance.md` BDD-1 各追加 2026-08-12 修订注：口径由 TAG0001 更新为 **9 子目录**（含 `debt/`）——WORKFLOW.md 目录规范已改，本记录保留原 8 子目录证据；BDD-4 重验判据 = 修订注存在 + 三处 mkdir 与目录图一致为 9。

## 自查结果（≠P5 gate）

- [x] grep 确认关键同步落盘：WORKFLOW.md 含 `debt/` 且无 `agents/.*tech-debt`；三处 mkdir 同一 9 集字面量；UPGRADING v0.43.0 节含 `debt/tech-debt.md`；P8-release.md 含 `debt_check` 字段与确认步骤；state-transitions/P6/P4 卡片含 DEBT 强制；TAG0003 P1+P6 BDD-1 含「9 子目录」修订注。
- [x] consistency 实跑：worktree 内唯一 ERROR 为 `check-debt.sh` 脚本不存在（core 并行 implementer 的交付物，非 docs 组范围）；用 /tmp 全量拷贝 + core 桩文件验证：docs 组改动不引入新 ERROR（剩余 ERROR 全为 TAG0002/TAG0003 对已归档/迁移文件的既有引用）。CHECK 3 无硬编码行号 ERROR。
- [x] 未改动 core 组文件集（tech-debt-template.md / agate-debt-check.py / check-debt.sh / check-gate.sh P8 分支 / agate-retreat-to.sh）——与并行 core implementer 无文件重叠。

## 声明

- [PROD_NOT_TOUCHED] 未触发生产写入；本次全部改动在 worktree `agate/` 与 docs/tasks/ 记录内。
- 无 [DESIGN_GAP] / [SCOPE+] / [SCOPE_GAP]：P2 方案对 docs 组的改动面足够明确，未发现歧义或遗漏；check-protocol-consistency.py 归 docs 组处理（P2 §0.1 #13）已执行。

## 边界说明

- `agate/UPGRADING.md` §3 最新节实际为 v0.41.0（dispatch-context 客观查证注记为 v0.42.0 的 TAG0002 变更未在 UPGRADING 落破坏性迁移节，以文件实际为准）——v0.43.0 节已按最新版本链插入。
- check-debt.sh 锚点 keywords 用 `["debt", "retreat"]`：core 交付的 check-debt.sh 含 `--retreat-coverage` 回退比对 + tech-debt 条目校验，两关键词均覆盖；若 core 实现措辞差异导致 CHECK9-align WARNING，由 P5/P7 按 WARNING 处理（不阻断非 --strict）。
