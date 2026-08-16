---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0014
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

发布准备（implementer P8 模式）：产出 P8-release.md，确定 bump 类型、核对版本文件与 CHANGELOG、记录债务检查与临时资源清单。**不执行 git commit / git tag**——由主 Agent 在 gate 验证后统一执行。

### 约束

- **版本决策**：TAG0014 是 agate 协议本体改造（加功能 + 内部机制升级，向后兼容——dispatch_plan 为可选字段，缺字段行为等同现状）→ **bump_type: minor**（v0.48.0 → v0.49.0）。P2-design §2.1 已明确 README badge v0.48.0 → v0.49.0。
- **版本文件核对（AGENTS.md 版本发布清单 + P8 卡）**：
  - README.md L5 version badge：当前 v0.48.0（P4 修复轮已还原），P8 应 bump 到 v0.49.0——但 **bump 动作由主 Agent 在 gate 验证后亲自执行**，releaser 只核对并在 P8-release.md 声明
  - CHANGELOG.md：P4 已写 [0.49.0] 章节（L13-30），核对内容完整（权威节升级 + dispatch_plan 可选字段 + 8 卡统一 + 无破坏性变更声明）→ 声明已就绪
  - agate/UPGRADING.md：P4 已写 v0.49.0 章节（L181-187）→ 声明已就绪
- **debt_check 字段（TAG0001 Phase 3）**：读 {AGATE_WORKSPACE}/debt/tech-debt.md（若存在），写 `debt_check: none / reviewed`（留痕存在即可，内容任意）
- **临时资源清单**：列出本任务执行期间启动的临时服务/进程/数据/开发安装（本任务为协议文档+脚本改造，应无服务/进程；若有临时测试文件列出）
- **不执行 git 操作**：P8 模式禁止 git commit / git tag——由主 Agent 在 gate 验证后统一执行
- **产出规格**：P8-release.md 必须含 bump_type / debt_check / 版本号变更确认 / CHANGELOG 更新确认 / 临时资源清单
- **输出路径硬约束**：P8-release.md → {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P8-release.md

### 上游关联

- P7-consistency.md：通过（BLOCKER=0）
- P2-design.md：packages: [agate-protocol, agate-scripts, agate-tests]（逻辑分组，本任务单版本 v0.49.0）
- self-gate 审查报告：docs/reviews/agate-alignment-review-TAG0014.md（A1-A7 闭环）
- P5-test-results/unit.md：pytest 780 passed / consistency 0 ERROR / count 782

### 输入文件

- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P2-design.md（packages 声明）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P5-test-results/unit.md（验证结果）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P7-consistency.md（一致性结论）
- {project_root}/README.md（版本 badge 核对）
- {project_root}/CHANGELOG.md（[0.49.0] 章节核对）
- {project_root}/agate/UPGRADING.md（v0.49.0 章节核对）
- {AGATE_WORKSPACE}/debt/tech-debt.md（若存在，debt_check）
- {project_root}/AGENTS.md（版本发布清单）
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
- 当前版本：v0.48.0（README badge + git tag 均为 v0.48.0）
- 目标版本：v0.49.0（bump minor）
- P4 已写：CHANGELOG [0.49.0] 章节 + UPGRADING v0.49.0 章节（待 P8 确认完整）
- 验证基线：pytest 780 passed / consistency 0 ERROR / count 782
- 本任务无 UI、无服务、无数据库——临时资源清单应为空/极简
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
