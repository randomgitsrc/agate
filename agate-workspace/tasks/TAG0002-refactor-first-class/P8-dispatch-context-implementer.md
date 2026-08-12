---
phase: P8
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0002
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 docs/tasks/TAG0002-refactor-first-class/P8-release.md——TAG0002（重构一等任务 Phase A）的发布准备记录：bump_type + 版本号变更确认 + CHANGELOG 更新确认 + 临时资源清单。**你只产出文件，不执行 git commit / git tag / bump-version**（主 Agent 在 gate 验证后亲自执行）。

### 约束
- **只产出 P8-release.md**：不执行 `git commit` / `git tag` / bump-version——这些是主 Agent 的专属职责。
- 本任务是 **agate 协议自身改造**（dogfooding）：发布对象是 worktree `agate/`（已含 TAG0003 工作区架构 + TAG0002 refactor 机制）；`~/.agate` 是稳定版 v0.40.2 开发工具（禁止改动）。
- **版本 bump 判定**（主 Agent 已决策，遵循里程碑策略）：TAG0003 已 bump v0.41.0（minor，破坏性变更按用户指示走小版本）。TAG0002 为**规则新增/调整**（change_type 字段 + P6 分流 + CI 感知，非破坏性，缺省行为不变）→ **minor bump → v0.42.0**。
- **版本号变更确认**：当前版本 v0.41.0（README.md L6 badge + 本地 tag v0.41.0）。P8-release.md 中给出：旧版本号 → 建议新版本号（v0.42.0）、bump_type（minor）、理由。
- **CHANGELOG 更新确认**：给出 CHANGELOG.md 的 [0.41.0] → [0.42.0] 新节内容建议（Keep a Changelog 格式：新增/变更/修复分类；本任务 = refactor 一等任务机制：change_type 字段、P6 回归口径、P3 refactor 感知）。
- **临时资源清单**：列出本任务执行期间启动的临时服务/进程/数据/开发安装（本任务为协议改动 + fixture 验证，注意 /tmp/opencode/ 下的 P6 fixture 等）。
- **Lessons Learned**：P8-release.md 增加「Lessons Learned」节（2-3 条关键教训），主 Agent 汇入 docs/notes/lessons.md。
- **READMEY 收尾提示**：P8-release.md 列出需主 Agent 清理的临时资源。
- 读取 P2-design.md packages 声明（[agate] 单包）——bump 范围 = agate 协议本体。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P7 已通过（gate exit 0）：DESIGN_GAP 0 项，SCOPE+ 闭环，BLOCKER=0。
- P1..P6 全部通过：8 BDD（P6 8/8 PASS）、P5 验证绿（bats 654/0 + consistency 0 ERROR + shellcheck 0 + count 648）。
- P2 packages=[agate]，ui_affected=false。
- 里程碑策略（主 Agent 决策）：TAG0003=v0.41.0（已打本地 tag），TAG0002=v0.42.0，TAG0001=v0.43.0（预计），最终一起 push/merge。

### 输入文件
- docs/tasks/TAG0002-refactor-first-class/P2-design.md（packages 声明 + gate_commands——必读）
- docs/tasks/TAG0002-refactor-first-class/P0-brief.md（环境约束——必读）
- AGENTS.md（版本发布流程——必读：确认 bats 全过 + 0 consistency ERROR + 0 shellcheck error；更新 README version badge；git tag vN.N.0；release PR 普通 merge 禁止 squash）
- CHANGELOG.md（当前版本段格式——必读）
- README.md（version badge L6——必读）
- docs/tasks/TAG0002-refactor-first-class/P7-consistency.md（一致性结论——选读）
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
5. 更新 .state.yaml phase=READY → DONE

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P8 MAX=2）

## 执行方式

releaser subagent（implementer P8 模式）执行以下发布准备步骤：

1. 读取 P2-design.md packages 声明，确定需 bump 的包
2. 为每个 package 执行发布检查命令
3. 更新 CHANGELOG [Unreleased] → 版本号
4. 产出 P8-release.md（含 bump_type、版本号变更确认、CHANGELOG 更新确认、临时资源清单）

> **注意**：releaser subagent 不执行 bump-version / git commit / git tag，这些由主 Agent 在 gate 验证通过后亲自执行。

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
- 版本号变更确认（version 文件已修改）
- CHANGELOG [Unreleased] → 新版本号
- 临时资源清单：本任务启动的临时服务/进程/数据/开发安装

## gate 规则

```bash
check-gate.sh P8 $TASK_DIR
```

- bump_type 字段存在
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
- [ ] active-tasks.md 任务行状态已更新
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=2998e64=TAG0002-P7 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 当前版本：v0.41.0（README.md L6 badge + 本地 tag v0.41.0，未 push）；git describe --tags = v0.41.0。
- 测试基线：全量 bats 654 用例（count 648 + sanity 6）；consistency 0 ERROR；shellcheck 0。
- 任务进度：TAG0002 P1 8 BDD → P2 方案 A → P3 19 回归测试 → P4 实现（review 三审 approved）→ P5 验证绿 → P6 验收 8/8 PASS → P7 一致性通过。
- 里程碑：TAG0003（工作区架构）已完成并打本地 tag v0.41.0；TAG0002（重构一等任务）本次发布 v0.42.0；TAG0001（技术债闭环）后续 v0.43.0。
- 版本发布流程（AGENTS.md）：1. 确认 bats 全过 + 0 consistency ERROR + 0 shellcheck error；2. 更新 README version badge；3. git tag vN.N.0 && push；4. CHECK 7 自动通过。release PR 必须普通 merge（--no-ff），禁止 squash merge。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
