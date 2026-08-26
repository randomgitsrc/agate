---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0025
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 `P8-release.md`（发布准备记录）。**你不执行 git commit/tag/bump-version 写操作**——你只
做发布检查命令 + 产出记录，实际的文件改动（README/CHANGELOG/UPGRADING 版本号写入）与 git
commit/tag 由主 Agent 在你返回后亲自执行。

### 关键决策（主 Agent 已与用户确认，直接采纳，不需要你重新判断）

1. **本次发布，bump_type: minor，目标版本 v0.64.0**（当前 v0.63.0）。用户已确认："与历史惯例
   一致"——本仓库每个任务完成都 bump minor 版本号。
2. **本仓库是单一版本方案，不是多包 npm 风格**：P2-design.md 声明的
   `packages: [agate-brand-docs, agate-installer-scripts, agate-repo-admin]` 是本任务内部的
   改动范围分类标签，不是三个独立可发布的包——整个仓库只有一套版本号（README badge +
   CHANGELOG 版本头 + git tag），不需要为这三个"package"分别 bump。
3. **roadmap RM-AG0035 回写已由主 Agent 亲自完成**（不需要你处理）：状态维持 `backlog`
   （本任务只完成 ①-⑥ 中的②，交接单明确要求不能整条标 done），已在正文追加部分完成说明。
   check-gate.py P8 的 RM-AG0043 校验不会因此阻断（TAG0025 未被登记进 RM-AG0035 的「关联任务」
   列，该硬校验只对已登记的精确匹配行生效）。

### 你需要产出的检查内容

1. **发布检查命令**：本任务无独立于全量测试套件之外的"per-package 发布检查命令"（不是 npm
   项目，没有 `npm publish --dry-run` 这类命令）。你的检查动作是：确认 P6.5 judge 已 passed
   （已确认，`.state.yaml` `judge.last_verdict: passed`）+ 确认当前 git 工作区状态干净（除本
   P8 阶段外无残留未提交改动）。
2. **CHANGELOG 现状确认**：读 CHANGELOG.md，确认 `## [Unreleased]` 段当前内容（TAG0025 品牌
   改名 Phase 0-1 的三条要点），把这段内容原样摘录到 P8-release.md，供主 Agent 之后执行"
   `[Unreleased]` → `[0.64.0] - 2026-08-26`"改名时核对不遗漏。
3. **版本文件现状确认**：记录 README.md（当前 v0.63.0）与 README.zh-CN.md（当前 v0.62.0——
   **这是一处 TAG0025 之前就存在的历史遗留不一致，不是本任务引入的**，本次统一 bump 到
   v0.64.0 后两者会自然对齐，不需要你额外处理或深究这个历史差异的成因）的 badge 版本号现状。
4. **UPGRADING.md §3 章节确认**：读 `agate/UPGRADING.md` 第 3 节最新一条（`### v0.63.0`）的
   格式，作为参考模板记录到 P8-release.md（主 Agent 会照此格式写 `### v0.64.0` 章节——本次
   任务性质是品牌层变更，预期"无破坏性变更"，你只需确认这个判断是否合理：改动是否涉及任何
   CLI 命令行为变更/字段格式变更/hook 变更——本任务没有，只是 URL 文本替换 + 仓库改名 + 新增
   1 个回归测试文件，判定"无破坏性变更"应该成立，把你的判断写进 P8-release.md）。
5. **debt_check**：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`，确认本任务范围内是否有相关条目
   需要关闭或新增（预期：无相关条目，本任务未发现需要登记的新技术债，也没有可关闭的既有条目）。
   `debt_check: none` 或 `reviewed`，按你实际核查结果判定并说明理由。
6. **临时资源清单**：本任务全程未启动任何临时服务/进程/测试数据库/端口占用（全部验证是文件
   grep/curl/git 命令），如实记录"无临时资源"，不需要编造清单项。
7. **`git log v0.63.0..HEAD --oneline` 对照 CHANGELOG 核实**：跑这条命令，确认本次 CHANGELOG
   `[Unreleased]` 段的 3 条要点覆盖了这段 commit 历史里的主要变更，无明显遗漏（不要求逐字对应
   每个 commit，只需确认量级/主题吻合）。

### 上游关联

- P2-design.md：`packages` 声明（本任务改动范围分类，非多包发布单元）
- CHANGELOG.md：当前 `[Unreleased]` 段内容
- README.md / README.zh-CN.md：当前 badge 版本号
- agate/UPGRADING.md：§3 最新版本章节格式参考
- `{AGATE_WORKSPACE}/debt/tech-debt.md`：技术债清单

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0025-agateon-rename/P2-design.md`（frontmatter packages 字段）
2. `CHANGELOG.md`
3. `README.md` / `README.zh-CN.md`（前 10 行）
4. `agate/UPGRADING.md`（第 3 节最新一条）
5. `agate-workspace/debt/tech-debt.md`
6. `agate-workspace/tasks/TAG0025-agateon-rename/.state.yaml`

### 产出文件字段
`P8-release.md` frontmatter 含 `bump_type: minor`、`debt_check:`。用
`FILE={AGATE_WORKSPACE}/tasks/TAG0025-agateon-rename/P8-release.md agate-md-field-set --list`
查看应填字段。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P8

路径：phase-cards/P8-release.md
---
# P8 — 发布

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P8 + internal_only: true + internal_only_reason 已声明 → 跳过，标记 READY
> ⑨ P8 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 releaser subagent（implementer P8 模式）执行发布准备
   1.1 写 P8-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. releaser subagent 产出 P8-release.md，**不执行 git commit/tag**
3. 主 Agent 执行 gate 验证 → 通过后执行 bump-version + CHANGELOG 更新 → 同一 commit + tag
4. 主 Agent 执行 READY 收尾检查（参考 P8-release.md 临时资源清单）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + P8-release.md，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 READY，不要提前写 DONE——phase = 本 commit 的产出阶段；终态 DONE 收尾随任务终态 commit 一起

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P8 MAX=2）

## 执行方式

releaser subagent（implementer P8 模式）执行以下发布准备步骤：

1. 读取 P2-design.md packages 声明，确定需 bump 的包
2. 为每个 package 执行发布检查命令
3. 更新 CHANGELOG [Unreleased] → 版本号
4. 确认债务清单：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在），在 P8-release.md 写入 `debt_check:` 字段（TAG0001 Phase 3）
5. 产出 P8-release.md（含 bump_type、版本号变更确认、CHANGELOG 更新确认、debt_check 字段、临时资源清单）

> **注意**：releaser subagent 不执行 bump-version / git commit / git tag，这些由主 Agent 在 gate 验证通过后亲自执行。

## 多包发布拆批（模式 2/3，条件触发）

> 仅当 P2 packages > 1 时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry 见 dispatch-protocol「派发编排机制」并行规则。

多包发布时 P8 可拆批并行（模式 2 静态拆批 / 模式 3 并行）：

1. 每个 package 派一个 releaser subagent（implementer P8 模式），各写 `P8-release-{pkg}.md`
2. 各 releaser 只处理自己包的发布准备（版本 bump 建议 + CHANGELOG 更新 + 发布检查命令）
3. 所有 releaser 返回后，主 Agent 派合并 subagent 整合唯一 P8-release.md
4. 合并 subagent 需交叉核对：各包版本号不冲突、bump_type 汇总一致、CHANGELOG 变更合并无遗漏
5. 主 Agent 在 gate 验证通过后统一执行 bump-version / git commit / git tag

**合并机制**：单包时 releaser 直接产出 P8-release.md（不走合并）；多包时各 releaser 产 P8-release-{pkg}.md，合并 subagent 整合唯一 P8-release.md 供 gate 检查。

## releaser→主 Agent 交接

P8-release.md 中的**临时资源清单**是 releaser→主 Agent 的交接文件：
- releaser subagent 负责写入临时资源清单（本任务启动的临时服务/进程/数据/开发安装）
- 主 Agent 使用该清单执行 READY 收尾检查中的清理工作
- P8-release.md 由 releaser subagent 产出，主 Agent 不直接编写

## 前置条件

- [ ] P7-consistency.md 通过（无 BLOCKER / DESIGN_GAP 已配对）
- [ ] P2-design.md packages 声明（决定哪些包需要 bump）

## 产出规格

P8-release.md 必须包含：
- `bump_type: major / minor / patch`
- `debt_check: none / reviewed`——债务清单确认留痕（TAG0001 Phase 3）：`none` = 本次无关注项（合法选项，不视为失败）；`reviewed` = 已核对，建议正文附条目 id 清单。只查留痕存在，不查内容达标、不阻断发布
- 版本号变更确认（version 文件已修改）
- CHANGELOG [Unreleased] → 新版本号
- 临时资源清单：本任务启动的临时服务/进程/数据/开发安装

## gate 规则

```bash
check-gate.py P8 $TASK_DIR
```

- bump_type 字段存在
- `debt_check` 字段存在（缺失 → exit 1；内容任意，含 `none` / 未关闭债务 → 不阻断，BDD-17）
- 暂存区有 version 文件变更
- 暂存区 CHANGELOG 有变更
- 若任务在 `agate-workspace/roadmap/roadmap.md` 有关联 RM 条目（按 `task_id` 反查「关联任务」列），须先回写「状态」列为 `done`，否则阻断（RM-AG0043）

主 Agent **必须亲自执行**以下验证（不可跳过、不可委托 subagent）：
- 从 P2 packages 逐包读取发布检查命令并执行 → 全部 exit 0
- **P5 验证（TAG0016 BDD-14 精简为条件化表述，底线不变——至少一次客观验证动作不可省）**：
  跑 `python3 agate/scripts/check-p6-provenance.py --audit7-only $TASK_DIR`，读 stdout 的
  `AUDIT7_RESULT: <reuse_allowed|reuse_blocked|no_reuse_claim_possible>` 行判定：
  - `AUDIT7_RESULT: reuse_allowed`（exit 0）→ 复用同一份 `P5-test-results/`（不重新执行命令）
  - `AUDIT7_RESULT: reuse_blocked`（exit 1）或 `AUDIT7_RESULT: no_reuse_claim_possible`
    （exit 0 但结果非 reuse_allowed）→ 完整重跑 `gate_commands.P5`（exit 0 + failed==0）
   - **⚠️ 时序注意（DEBT0013）**：若 `gate_commands.P5` 的链路包含
     `check-protocol-consistency.py` 的 CHECK 7（README version badge 与最新 git tag 一致性），
     P5 重跑应安排在 **commit + 创建 git tag 之后** 进行，而非 bump 版本文件后立即重跑——
     bump 已完成、tag 尚未创建的中间状态下，CHECK 7 必然报 `badge vX.Y.A != tag vX.Y.B` ERROR，
     这是设计使然（校验的是"发布完成态"），不是回归。先 tag 后重跑即 0 ERROR。
- `git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 无遗漏
- 从 P2 packages 验证 version 文件路径

## READY 收尾检查（P8 gate 通过后）— 主 Agent 亲自执行（不派发 subagent）

参考 P8-release.md 临时资源清单执行清理。以上检查项无 gate 脚本自动验证（已知缺口），**必须逐项实际执行检查命令**（如 `ps aux | grep debug` 确认服务已停止、`git status` 确认工作区干净），不得仅凭记忆打勾。

**状态与版本**：
- [ ] .state.yaml phase == READY
- [ ] {AGATE_WORKSPACE}/tasks/active-tasks.md 任务行状态已更新
- [ ] git 工作区干净
- [ ] git tag 已创建
- [ ] 若本任务触发复盘（异常模式 / 发现机制缺口 / 高价值任务），复盘产出
  `tasks/{Txxx}/retrospective.md` 基于 `agate/assets/templates/retrospective-template.md`
  模板撰写

**测试环境已清理**：
- [ ] 调试服务/进程已停止
- [ ] 临时数据已删除
- [ ] 测试占用的端口已释放

**开发环境已还原**：
- [ ] 开发安装已卸载
- [ ] 系统环境无污染
- [ ] 项目依赖恢复到发布版本

**协议一致性（改造协议自身的任务必做，TAG0001-0003 批次 D4 教训）**：
- [ ] **在干净 checkout 上跑一次 `check-protocol-consistency.py`**（`git clone` 到临时目录或 CI 兜底确认），0 ERROR
  - 原因：本地 worktree 的 `.worktrees` 路径过滤会掩盖任务产出文件的扫描问题，本地 0 ERROR ≠ CI 0 ERROR
  - 若无法干净 checkout，**至少确认 CI 的 consistency job 对本次 PR 通过**
- [ ] **确认任务产出目录（`docs/tasks/` 或 `{AGATE_WORKSPACE}/tasks/`）不被一致性检查器误扫**（若为 dogfooding 任务，任务产出应已在 `NARRATIVE_DIRS` 白名单）

**生产环境无残留**：
- [ ] 无 PROD_TOUCHED 标记（触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`）
- [ ] 生产数据/API 未被测试写入

## 推进条件（全部满足才写 phase: READY）

- [ ] bump-version 完成 + P5 验证全绿（重跑或复用 `P5-test-results/`，见上方「gate 规则」条件化表述）
- [ ] CHANGELOG 已更新
- [ ] git tag 已创建
- [ ] READY 收尾检查全部通过

## 常见错误

1. **不重跑 P5 gate**：bump-version 后直接 tag，不确认测试仍全绿
2. **CHANGELOG [Unreleased] 留在模板状态**：版本 bump 完但 CHANGELOG 没更新
3. **忘记清理测试环境**：debug server 还在跑、临时数据没删 → READY 不干净
4. **临时资源清单遗漏**：P4/P5 阶段启动的服务/安装的包没记录 → 清理时遗漏
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- READY → DONE：任务完成，代码可合并/发布
- 本任务是 agate 链条的终点——P8 完成后任务状态转为 DONE

> 完成 → 任务 DONE
<!-- AGATE_CARD_END -->

<objective_info>
- 用户已确认：bump minor → v0.64.0（2026-08-26）
- 用户已确认：roadmap RM-AG0035 保持 backlog，正文标注部分完成，不整条标 done（主 Agent 已
  亲自完成这项回写，你不需要处理）
- 当前版本：README.md badge v0.63.0，README.zh-CN.md badge v0.62.0（历史遗留不一致，本次
  统一 bump 后自然对齐）
- CHANGELOG.md 当前 `## [Unreleased]` 段（TAG0025 三条要点）位于 `## [0.63.0] - 2026-08-25`
  段之上
- `.state.yaml`：`judge.last_verdict: passed`（P6.5 第 2 轮通过）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
