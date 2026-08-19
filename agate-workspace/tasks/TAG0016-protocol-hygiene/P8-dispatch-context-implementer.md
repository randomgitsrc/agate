---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0016
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P8-release.md（发布准备记录）。**你不执行 bump-version / git commit / git tag**——这些由
主 Agent 在 gate 验证通过后亲自执行。你的任务是判定 bump_type、核对债务清单、列出临时资源清单。

### 约束

1. **本任务是 agate 协议自身的单一版本发布**，不是多包各自独立版本的项目。虽然 P2-design.md
   frontmatter 声明了 8 个 `packages`（workflow/dispatch-protocol/state-machine/platform-notes/
   state-transitions/phase-cards/dispatch-prompt-template/gate-scripts），这些是 P7 一致性检查
   用的"受影响范围分类"，不是 8 个独立可发布单元——agate 整体只有**一个版本号**（README.md
   `version-v{X.Y.Z}-blue` 徽章）。不要按"多包拆批发布"流程处理，产出单一 P8-release.md。
2. **bump_type 判定**：本任务新增 CHECK 12（防复发检测）、审计 7 + `--audit7-only` CLI 模式
   （跨阶段证据引用机制）、ADR-010，均为向后兼容的新增能力（不改变任何既有 gate 脚本对老任务的
   判定行为——CHECK 1-11、审计 1-6 逻辑未改，新增的是并列的第 12/7 项）；协议文档去重是内容
   重组（指针替代重复段落），语义不变，不影响任何消费方的可判定行为。按 implementer.md「版本
   bump 判定」规则："加功能/内部重构改 API（向后兼容）→ minor"，判定 **bump_type: minor**。
   当前版本 v0.53.0（TAG0015），bump 后为 **v0.54.0**。
3. **debt_check 字段**：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`，逐条核对当前全部 DEBT 条目
   （含本任务本身新增/扩充的 DEBT0009/DEBT0010（扩充）/DEBT0011/DEBT0012）的 `task_id` 是否与
   本任务相关——本任务自己新增的 DEBT 条目均为 `status: open`（不要求本次关闭，登记本身就是
   目的：可见可追踪），其余历史 DEBT（DEBT0001-0008）与本任务无关。写
   `debt_check: reviewed`（已核对，非 none——本任务确实新增/修改了 debt 条目，不是"无关注项"），
   正文附本任务相关的 DEBT id 清单（DEBT0009/DEBT0010/DEBT0011/DEBT0012）+ 各自 status。
4. **临时资源清单**：本任务全程未启动任何临时服务/进程/数据库（纯文档改动 + Python 脚本改动 +
   pytest 验证，无 debug server、无临时数据），如实写"无临时资源"。
5. **不要在本次派发里执行任何 git commit/tag/bump-version 操作**——只产出 P8-release.md 记录你
   的判定和核实过程，主 Agent 会亲自执行实际的 bump 和验证。

### 上游关联

P7 一致性检查已通过（BLOCKER=0，DESIGN_GAP 1/1 已配对，1 个非核心 DEVIATION 已分类不阻塞）。
P1-P7 全部完成。当前版本 v0.53.0，本任务的改动清单见 P2-design.md §1.1（M1-M23）+ P7-consistency.md
汇总。

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P2-design.md（packages 声明）
- {AGATE_WORKSPACE}/tasks/TAG0016-protocol-hygiene/P7-consistency.md（一致性结论，含 DEVIATION）
- {AGATE_WORKSPACE}/debt/tech-debt.md（债务清单核对）
- CHANGELOG.md（当前 [0.53.0] 节格式，供你判断新版本节应该写成什么结构，不要求你直接编辑
  CHANGELOG.md——CHANGELOG 更新由主 Agent 在 bump-version 时亲自执行）
- README.md（当前版本徽章位置，供你确认，不要求你直接编辑）

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

主 Agent **必须亲自执行**以下验证（不可跳过、不可委托 subagent）：
- 从 P2 packages 逐包读取发布检查命令并执行 → 全部 exit 0
- 重跑 P5 gate（gate_commands.P5 exit 0 + failed==0）
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

- [ ] bump-version 完成 + P5 重跑全绿
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
- worktree HEAD：51ecb31（P7 已 commit），工作区干净。
- 当前版本：v0.53.0（README.md badge + CHANGELOG.md 最新节标题）。
- tech-debt.md 当前 12 条 DEBT，其中 4 条（DEBT0009/0010/0011/0012）为本任务新增/扩充，均
  status: open，task_id: TAG0016。
</objective_info>
