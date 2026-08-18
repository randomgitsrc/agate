---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 P8-release.md：为 agate UI/UX 验收质量机制（TAG0006）做发布准备——确定 bump_type、债务清单确认、版本引用文件清单、CHANGELOG 更新建议、临时资源清单。**不执行 git commit/tag/bump-version**（主 Agent 专属职责）。

### 约束
1. **本任务是 agate 协议本体改造**（dogfooding 双工作区）：改动在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0006/），不碰主 checkout / ~/.agate。
2. **bump_type 判定**（AGENTS.md + dispatch-prompt P8 节）：
   - 公共 API 行为变化 / 破坏性变更 → major
   - 加功能 / 内部重构改 API（向后兼容）→ minor
   - 修 bug / 不改 API 行为 → patch
   - 本任务是**机制增强**（新增 capability_requirements 三态硬校验、UI 设计节检查、avg-hash 降级、形态适配）——**新增功能 + 向后兼容**（既有 task 无新字段走默认，825 基线不红），应判 **minor**。但需核查是否有破坏性变更（如 avg-hash 降级从 WARNING 改硬拦是行为变化——需权衡，见下）。
3. **破坏性变更评估**：avg-hash 雷同从 WARNING 升级为"降级待复核"（无复核记录 exit 1）是**行为变化**——对既有任务可能有影响。若判为破坏性变更 → UPGRADING.md 需写对应章节。请评估并在 P8-release.md 说明 bump_type 理由。
4. **版本引用文件清单**（AGENTS.md 特有，通用 P8 卡不覆盖）：README badge / CHANGELOG / UPGRADING 章节 / 稳定版引用（文档优先写"稳定版"不写死版本号）。列出需更新的文件。
5. **debt_check 字段**：读 {AGATE_WORKSPACE}/debt/tech-debt.md，写 `debt_check: none / reviewed` + 建议正文附条目 id 清单。本任务新增 DEBT0005/DEBT0006（已登记）。
6. **CHANGELOG 更新建议**：CHANGELOG.md 当前最新 [0.50.0] 无 [Unreleased]——releaser 建议新版本节内容（TAG0006 变更条目），但实际写入由主 Agent 执行。
7. **临时资源清单**：列出本任务执行期间启动的临时服务/进程/数据/开发安装。
8. **主 Agent 亲自执行项**（releaser 只产出 P8-release.md，不执行）：bump-version、CHANGELOG 写入、git commit/tag、重跑 P5、README 收尾。

### 上游关联
- 当前版本：v0.50.0（最新 tag）。CHANGELOG 最新 [0.50.0] 无 [Unreleased]。
- P2 packages: [agate-docs, agate-scripts-py, agate-tests]（同仓库 agate 协议本体）。
- P7 已通过：BLOCKER=0，DESIGN_GAP 配对，SCOPE+ 闭环。
- 全链路：P1 17 BDD → P2 → P3 53 用例 → P4 28 文件 → P5 881 过 → P6 17/17 PASS → P7 一致性通过。
- DEBT0005（三态解析重复，已抽 read_vision_tri_state 解决）/ DEBT0006（ahash zip 脆性，已修复）已登记。
- 无临时服务/进程（纯脚本 + 文档改造，无 server 启动）；无开发安装。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-design.md（packages 声明 + gate_commands）
- {AGATE_WORKSPACE}/debt/tech-debt.md（债务清单）
- {project_root}/README.md（版本 badge）
- {project_root}/CHANGELOG.md（版本日志）
- {project_root}/agate/UPGRADING.md（升级指引）
- {project_root}/AGENTS.md（版本发布清单：README badge/CHANGELOG/UPGRADING/稳定版引用）
- {project_root}/agate/assets/execution-roles/implementer.md（角色定义，P8 模式）
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
- 当前版本：v0.50.0（最新 tag，CHANGELOG 无 [Unreleased]）。
- TAG0006 变更：机制增强（悲视觉三态硬校验、UI 设计节、avg-hash 降级、形态适配）——向后兼容，倾向 minor。
- 潜在破坏性变更：avg-hash 雷同从 WARNING 升硬拦。
- 版本文件：README badge（v0.50.0）/ CHANGELOG / UPGRADING（需新增本版本章节）/ 无独立 version 文件。
- 无临时资源。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。