---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0031
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> **本次 P8 是「发布准备声明」，不执行实际 bump-version / git tag / CHANGELOG 正式提交**——用户已明确决定：TAG0031 是 TAG0029/30/31 三路并行任务之一，三个 worktree 若各自独立 bump 版本号/建 tag 会在合并时冲突，因此版本号/tag/CHANGELOG 正式条目统一延后到三路全部合并进 main 之后，由主 Agent 在主 checkout 一次性处理。你的产出是"声明本次改动的发布准备信息"，不是"执行发布"。

### 目标
产出 P8-release.md：声明本次改动的 `bump_type` 建议、CHANGELOG 草稿条目（不实际写入 CHANGELOG.md 正式文件）、`debt_check` 字段、临时资源清单。**不修改 README.md 版本徽章、不修改 CHANGELOG.md、不创建 git tag、不执行任何 bump-version 相关命令**。

### 约束
- **`bump_type` 判断依据**：本次改动是 7 条低风险脚本健壮性修复（DEBT0002/3/4/7/16/17/18），无破坏性变更（无 API/CLI 参数变化，无协议文档面改动，SELF-GATE protocol-alignment-review 已确认 A1-A7 全 ALIGNED），属于 `patch` 级别（对齐既往同类"工具链批"任务如 TAG0024 的版本号跳变模式——仅需你给出判断依据，不需要你去查具体历史版本号数字，那由主 Agent 处理）。
- **CHANGELOG 草稿内容**：仿照 `CHANGELOG.md` 现有条目格式（`## [x.y.z] - 日期` + `### 新增/变更/修复` 分类），写一段可直接被主 Agent 后续采纳的草稿文本，放在 P8-release.md 正文（不是修改 CHANGELOG.md 本体）。内容应覆盖：7 条 DEBT 关闭（版本管理域 hash 共享+信任边界文档+限流 WARNING / 测试隔离验证 / check-gate.py 三处健壮性修复）+ 2 条新登记 DEBT（DEBT0028/29）。
- **`debt_check` 字段**：读 `agate-workspace/debt/tech-debt.md`，本次任务关闭了 7 条、新增登记 2 条——`debt_check: reviewed`，正文附这 9 条 DEBT id 清单（7 closed + 2 open）。
- **临时资源清单**：核对本任务全程（P1-P8）是否启动过任何调试服务/进程/临时数据库/开发环境安装——本任务是纯脚本+测试改动，预期为空清单，若发现遗漏（如某个测试留下了未清理的临时文件），如实列出。
- **`version_deferred` 声明**（本次特有，供主 Agent 后续合并批处理用）：正文写明"版本号 bump / git tag / CHANGELOG.md 正式提交延后至 TAG0029/30/31 三路合并 main 后统一处理，本 worktree 不执行"，避免后续阅读者误以为遗漏。
- **不执行任何 git tag / bump-version 命令**：你的角色定义（implementer P8 模式）里"不执行 git commit/tag"这条本就适用，本次额外强调"也不建议具体版本号数字给主 Agent 直接套用"——只给 bump_type 级别（patch/minor/major）判断，具体数字由合并时由主 Agent 统一决定（因为要看三路合并后的联合改动范围）。

### 上游关联
- P7-consistency.md 通过（0 BLOCKER，DESIGN_GAP 已配对接受，SCOPE+ 闭环完整）
- P2-design.md packages: [agate-scripts, agate-tests, agate-docs]

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P7-consistency.md
- {AGATE_WORKSPACE}/tasks/TAG0031-debt-cleanup/P2-design.md（packages 声明）
- {AGATE_WORKSPACE}/debt/tech-debt.md（本次 7 closed + 2 open 的 debt_check 依据）
- /home/kity/oclab/agateon/.worktrees/agate-TAG0031/CHANGELOG.md（现有条目格式参照，只读不改）
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
- 环境状态：worktree 分支 feat/TAG0031-debt-cleanup（P7 已 commit），工作目录 /home/kity/oclab/agateon/.worktrees/agate-TAG0031
- 关键标识：当前最新 tag v0.67.0（仅供参考，不代表本次要 bump 到的具体数字——具体数字延后决定）
- 查证结果：用户已明确批准"worktree 内不 bump 版本/不建 tag"的处理方式（三路并行冲突规避）
</objective_info>
