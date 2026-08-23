# P8-dispatch-context-implementer — TAG0022 发布准备

> 派发对象：implementer（P8 releaser 模式）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/`

## 目标

产出 `P8-release.md`（发布准备，**不执行 git commit/tag/bump**——那些由主 Agent 在 gate 验证通过后亲自执行）。

## 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-requirements.md`（phases/packages 声明）
2. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P2-design.md`（packages=[agate] + gate_commands）
3. `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P7-consistency.md`（P7 结论）
4. `{AGATE_WORKSPACE}/debt/tech-debt.md`（债务清单，debt_check 用）
5. `{agate_root}/phase-cards/P8-release.md` + `{agate_root}/assets/execution-roles/implementer.md`（角色定义）
6. 现状：`README.md`（version badge v0.60.0）、`CHANGELOG.md`（[0.60.0] 节，无 [Unreleased]）、`agate/UPGRADING.md`（v0.61.0 章节 ① 完整 + ②③ 占位——发布时须补齐，见下）

## 产出规格

`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P8-release.md`，Header：

---
phase: P8
task_id: TAG0022-confirmed-problems
type: release
parent: P7-consistency.md
trace_id: TAG0022-P8-20260822
status: draft
created: 2026-08-22
agent: implementer
---

正文必须包含：
- **`bump_type:`** — 建议档位 + 理由（参考：本任务 = CI 门禁配置 + check-gate.py 内部重构（读取方式变、判定口径不变，well-formed 等价）+ judge 新任务强制（机制后新任务行为变化，历史任务跳过）+ M15 opt-in 排除钩子（默认关闭）——按 P8 bump 判定规则给出 minor 或 major 建议与理由；UPGRADING 章节已按 v0.61.0 预写，版本号若与建议冲突需说明）
- **`debt_check:`** — none / reviewed（读 tech-debt.md；若 reviewed 附已核对条目 id，如 DEBT0018）
- **版本号变更确认**：README badge v0.60.0 → v0.61.0 的变更点清单
- **CHANGELOG 更新确认**：[0.60.0] 节之上新增 [0.61.0] 节的条目建议（本任务 5 子项：RM-AG0037 ruff 合并强制（required check 配置）/ RM-AG0038 check-gate 权威源切换 + S-3 双向收紧 / RM-AG0039 judge P1 强制校验 / RM-AG0040 M3 实证计划 / RM-AG0041 环境测试根治（M15 + test_bdd_7/25））
- **UPGRADING ②③ 补齐清单**：AGENTS.md 版本发布清单 step 3 强制（v0.44.0 教训）+ protocol-alignment-review HUMAN_CONFIRMED（A5）——② RM-AG0038 权威源切换（影响面/升级动作/对账兜底行为）、③ RM-AG0039 judge 强制化（判据/历史兼容语义/升级动作）需在发布时补齐完整条目；给出补齐要点清单（主 Agent 亲自执行写入）
- **临时资源清单**：本任务启动的临时服务/进程/数据/开发安装（如 P4/P5/P6 阶段的临时 basetemp 目录——均已清理，写明"无残留"并列出曾创建的路径供核对）
- **发布检查命令**：`git log v0.60.0..HEAD --oneline` 对照 CHANGELOG 无遗漏的核对建议

## 约束（硬约束）

1. **不执行** git commit / git tag / version 文件修改 / CHANGELOG 写入——只产出 P8-release.md 与建议清单
2. 只读消费（worktree 文件可读；写操作仅限 P8-release.md 与 P8-progress.md）
3. 环境：Linux；/tmp 只读；bash 一律 timeout；双工作区纪律；状态标记 `[PROD_TOUCHED]`/`[PROD_NOT_TOUCHED]`
4. debt_check 必须读 tech-debt.md 后给出（含 DEBT0018 等 open 条目）

## 分阶段落盘

每完成一步，追加写 `{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P8-progress.md`。

## 返回给我

只返回两行：① P8-release.md 路径；② 一句话摘要（bump_type 建议 + debt_check + 要点数）。绝不返回文件全文。
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
