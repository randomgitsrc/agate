---
phase: P8
task_id: TAG0002-refactor-first-class
type: release
parent: P7-consistency.md
trace_id: TAG0002-P8-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0002 — P8 发布准备记录（releaser，implementer P8 模式）

> 角色声明：本文件仅做**发布准备记录**。releaser 不执行 `git commit` / `git tag` / bump-version——这些由主 Agent 在 P8 gate 验证通过后亲自执行。
> 客观查证（非自报）：`git describe --tags` = v0.41.0，v0.41.0 是 HEAD 祖先；README.md L6 badge = v0.41.0；HEAD = 2998e64（TAG0002-P7 commit）。
> 环境隔离：`[PROD_NOT_TOUCHED]` 本任务为 agate 协议自身改造（dogfooding），全程只在 worktree `agate/` + 任务目录 + `/tmp/opencode/` 验证，未触碰 `~/.agate`（稳定版 v0.40.2）与主 checkout，无生产环境接触，未触发 `[PROD_TOUCHED]`。

## 1. bump 范围（P2 packages 声明）

- **包**：`[agate]`（单包）——bump 范围 = worktree `agate/` 协议本体。
- **ui_affected**: false（P2 声明，无 P5_e2e）。
- **改动面实证**（`git diff --stat v0.41.0..HEAD -- agate/`）：16 文件 +573/-13——check-gate.sh（P6 分流）/ agate-md-field-get.py（change_type + regression_pass op）/ agate-frontmatter-check.py（P1/P6 schema）/ ci-gate-backstop.py（P3 refactor 感知）/ 4 张卡片（P1/P3/P6 + WORKFLOW/state-machine/dispatch-protocol）/ 2 角色（verifier/test-designer）+ 4 个 bats 测试文件。与 P2 §1.1 清单 + P7 §3.3 逐项核对一致，无越权改动。

## 2. bump_type 与版本号变更确认

- `bump_type: minor`
- **旧版本 → 新版本**：`v0.41.0` → `v0.42.0`
- **理由**（主 Agent 决策，遵循里程碑策略）：
  - TAG0002 为**规则新增/调整**（`change_type: refactor` 字段 + P6 回归口径分流 + P3/CI refactor 感知），非破坏性——缺省路径（未声明 change_type）行为与改造前逐字节一致，由 P6 基线用例反证（BDD-2）+ P5 全量 654 用例回归兜底。
  - 破坏性变更走小版本（TAG0003 已按此策略 bump v0.41.0）；规则新增/调整同理按**语义化版本 minor** 处理，不是 patch（功能面扩展）。
  - 里程碑衔接：TAG0003=v0.41.0（已打本地 tag，未 push），TAG0002=v0.42.0，TAG0001=v0.43.0（预计），最终一起 push/merge。
- **版本号来源**：README.md L6 version badge（v0.41.0-blue）+ 本地 tag v0.41.0。**bump-version 时需同步改 README.md L6 badge**（AGENTS.md CHECK 7：version badge vs git tag）。
- **发布检查命令**（主 Agent P8 gate 亲自执行，releaser 不跑）：
  - P5 gate 重跑：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`（期望 654 ok / 0 not ok）
  - `python3 agate/scripts/check-protocol-consistency.py`（期望 0 ERROR）
  - `shellcheck -S warning agate/scripts/*.sh`（期望 0 error）
  - `bash agate/tests/scripts/count-tests.sh`（期望 648，与 P5 一致）
  - `git log v0.41.0..HEAD --oneline` 对照 CHANGELOG 无遗漏

## 3. CHANGELOG 更新建议

CHANGELOG.md 当前顶段为 `[0.41.0] - 2026-08-12`（无 [Unreleased] 段）。建议在文件顶部（`---` 之后、`[0.41.0]` 段之前）插入新节：

```markdown
## [0.42.0] - 2026-08-12

### 新增（TAG0002 重构一等任务机制，Phase A）
- **`change_type: refactor` 任务类型声明**（P1 frontmatter 可选机器字段，枚举 `{refactor}`，缺省 = 功能任务）：重构任务可在 P1 声明类型，gate/CI 按类型分流——`agate-md-field-get.py` 新增 `change_type`/`regression_pass` 读取 op；`agate-frontmatter-check.py` P1 schema 增枚举校验
- **P6 重构验收口径（回归口径，非功能 BDD 口径）**：change_type=refactor 的任务，P6 验收改为三段式——行为不变声明 + 全量回归全绿（frontmatter `regression_pass: true` + `P6-evidence/regression.log` 尾行 `EXIT_CODE: 0` 双证）+ 关键路径行为不变 BDD 逐条 PASS/FAIL；`check-gate.sh` P6 分支按 change_type 分流硬校验（缺回归双证 → gate 不通过）
- **P3 重构回归测试口径**：refactor 任务 P3 走回归测试设计（既有用例覆盖映射，不新增功能行为断言），跳过 TDD 红灯步骤（红灯语义不适用）；`ci-gate-backstop.py` P3 分支对 change_type=refactor 任务跳过 check-tdd-red 兜底（避免全量即绿被误判 FAIL）

### 变更（TAG0002 重构一等任务机制，Phase A）
- **重构验收口径对 no_behavior_change 独立**：refactor 判定只看 change_type，不读 no_behavior_change——即使重构任务声明 no_behavior_change，回归双证仍强制（换口径 ≠ 裁 P6，P6 仍不可裁剪）；WORKFLOW.md/state-machine.md/dispatch-protocol.md 同步"P6 不可裁剪"表述
- **可发现性**：P1/P6/P3 卡片 + verifier/test-designer 角色 + P5/P6/P3 派发指引补充 refactor 口径说明；明文禁止"为凑验收数量新增功能性质 BDD"

### 文档（TAG0002 重构一等任务机制，Phase A）
- P6-acceptance.md / P1-requirements.md / P3-tdd.md 卡片 refactor 分支说明；verifier.md / test-designer.md 角色口径
```

> 说明：本任务**无既有 bug 修复**（[v0.40.2..v0.41.0] 内的修复已随 v0.41.0 发布），故 CHANGELOG 新节不含"修复"分类；Keep a Changelog 格式允许按实际类别取舍。

## 4. 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务执行期间启动/创建的临时资源，主 Agent P8 gate 通过后执行 READY 收尾检查时清理：

| # | 临时资源 | 类型 | 位置 | 清理动作 |
|---|---|---|---|---|
| 1 | TAG0002 P6 fixture 目录 ×3（bdd1..bdd7 子目录） | 临时数据 | `/tmp/opencode/tag0002-p6-fixture.l2UwTS`、`/tmp/opencode/tag0002-p6-fixture.rpSpRf`、`/tmp/opencode/tag0002-p6-fixture.thayEh` | `rm -rf` |
| 2 | P6 手工验证脚本 | 临时数据 | `/tmp/opencode/tag0002-p6-verify.sh` | `rm -f` |
| 3 | P6 手工验证日志（bdd1/6/7/8/9 各 log + grep/live-selector log） | 临时数据 | `/tmp/opencode/p6-*.log`（p6-bdd1-e2e.log / p6-bdd6-stale.log / p6-bdd7-fresh.log / p6-bdd8-quick.log / p6-bdd9-safety.log / p6-grep.log / p6-live-selector.log） | `rm -f` |
| 4 | P6 验证辅助目录（backstop-p6 / mdget-p6 / p6fix） | 临时数据 | `/tmp/opencode/backstop-p6`、`/tmp/opencode/mdget-p6`、`/tmp/opencode/p6fix` | `rm -rf` |

- **无临时服务/进程**：本任务无 debug server / daemon（`ps` 查证无任务启动的常驻进程，仅环境既有的 MCP server）。
- **无开发安装**：本任务不安装/卸载任何包，无 editable install，无全局安装。
- **无端口占用**：ui_affected=false，无服务端口。
- **任务目录内 P6-evidence/（15 个 bdd log）不是临时资源**——是 P6 验收证据，随任务提交归档，保留。
- **其他 /tmp/opencode/ 下文件**（demo-repo/migtest/migtest2/migtest3/mw* 等）为**其他任务**（TAG0003 工作区迁移验证等）的临时产物，不属于本任务清理范围，主 Agent 如需一并清理另行判断。

## 5. READMEY 收尾提示（主 Agent）

1. 按 §4 临时资源清单清理 `/tmp/opencode/` 下 TAG0002 专属 fixture/脚本/日志。
2. `git status` 确认工作区干净（bump-version + CHANGELOG + README badge 变更 commit 后）。
3. `.state.yaml` phase 置 READY；active-tasks.md 任务行更新。
4. `git tag v0.42.0` 创建 + 后续 push。
5. **release PR 必须普通 merge（--no-ff），禁止 squash merge**（AGENTS.md：agate-summary.sh 用 `git describe` 探测版本，要求 tag 是 HEAD 祖先；squash 会生成新 SHA 导致 describe 回退）。若已 squash，合并后 `git tag -f v0.42.0 <main-commit>` + force push。

## 6. Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|---|---|---|---|
| 流程 | 版本 bump 必须同步核对 README badge + 本地 tag + `git describe` 三处来源，且发布前确认 tag 是 HEAD 祖先（release PR 普通 merge 前提）；CHANGELOG 新节按 Keep a Changelog 分类取舍（无修复就写无修复，不为凑格式硬塞空分类） | TAG0002 | 2026-08-12 |
| 架构 | 新增 gate 分流机制（如 P6 change_type 分支）必须是"前置增量分支 + 空值短路"，缺省路径逐字节保留并由基线用例反证——向后兼容靠"分支短路"而非"复制粘贴旧逻辑"，否则缺省路径漂移难以检测 | TAG0002 | 2026-08-12 |
| 测试 | refactor 类任务的验证不适用 TDD 红灯语义（无新行为断言，全量即绿），需在 P3 口径 + CI backstop 双点声明跳过 check-tdd-red，否则合法重构任务会被 CI 误杀；回归质量由 P5 全量 + P6 regression.log（EXIT_CODE: 0 尾行）双证兜底 | TAG0002 | 2026-08-12 |
| 安全 | 协议自身改造（dogfooding）全程只触碰 worktree 产物 + /tmp 验证目录，`~/.agate` 稳定版与主 checkout 隔离，避免"改协议把自己工具改坏" | TAG0002 | 2026-08-12 |

## 7. 主 Agent 发布动作清单（releaser 不执行，仅列出）

1. 执行 §2 发布检查命令（P5 gate 重跑 / consistency / shellcheck / count-tests / git log 对照 CHANGELOG）→ 全部通过。
2. bump-version：README.md L6 badge `v0.41.0` → `v0.42.0`。
3. 按 §3 建议更新 CHANGELOG.md（插入 `[0.42.0]` 新节）。
4. 同一 commit 提交版本变更 + CHANGELOG；`git tag v0.42.0`。
5. 执行 §5 READY 收尾检查（含 §4 临时资源清理）。
6. `.state.yaml` phase=READY → DONE。

## 8. SCOPE_GAP / DESIGN_GAP 检查

- [SCOPE_GAP] 检查：P2 packages=[agate]，本 P8 处理 agate 单包 bump——无遗漏包。P2 §1.1 声明的 12 必改 + 2 条件文件全部在 v0.41.0..HEAD 改动集内（P7 §3.3 核对），无 prompt 遗漏项。
- [DESIGN_GAP] 检查：本发布准备未自主决策偏离 P2 设计——bump_type/版本号/CHANGELOG 建议均遵循派发指引与主 Agent 决策，无歧义需要上报。
- 本文件不含行首 `- PASS` / `- FAIL` 格式（provenance 审计要求）。
