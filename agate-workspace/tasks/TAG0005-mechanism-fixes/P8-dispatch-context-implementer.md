> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P8
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0005
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P8-release.md`（发布准备记录），为 TAG0005 机制修复批的合并发布做准备。

### 约束

- **合并发布模式（用户已确认，HANDOFF §8b）**：本 worktree 承载 TAG0005 + TAG0009 两个任务，**合并为一次发布**（bump 一次版本 v0.45.0，一个 tag，一个 PR）。TAG0005 先到 READY（不 bump 不 tag），TAG0009 完成后由主 Agent 统一执行 bump + CHANGELOG + tag + PR。
  - 因此本次 P8-release.md 是**发布计划文档**：声明 bump_type / 计划版本号 / debt_check / 临时资源清单 / 本任务变更摘要（供合并发布时写入 CHANGELOG）。
  - **不执行版本 bump、不 git commit/tag**（releaser 本来就不执行，由主 Agent 在合并发布时统一执行）。
- **bump_type 判定**（AGENTS.md 版本发布节）：TAG0005 为机制/契约缺陷修复 + 新增 C8 触发角色（backend P2 评审）+ 新 gate 行为（P5 主/辅计数、check-debt exit 2）——含行为变化（新增评审触发），判 **minor**（v0.44.0 → v0.45.0，若 TAG0009 也是 minor 则合并后仍 v0.45.0；若 TAG0009 需 major 再议，主 Agent 统一裁决）。
- **debt_check**：读 `agate-workspace/debt/tech-debt.md`，确认本任务是否产生/关闭债务，写 `debt_check: none` 或 `reviewed` + 条目 id。
- **CHANGELOG 草稿**：P8-release.md 里写本任务变更条目草稿（release note 文本，供合并发布时合并进 CHANGELOG.md），不实际改 CHANGELOG.md。
- **临时资源清单**：列出本任务执行期间启动的临时服务/进程/临时数据/开发安装（供主 Agent READY 收尾清理）。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（provenance 预检检测）。

### 上游关联

- `P2-design.md`（packages 声明、bump 范围）
- `P7-consistency.md`（一致性通过）
- `P6-acceptance.md`（验收 16/16 PASS）

### 输入文件

- `agate-workspace/tasks/TAG0005-mechanism-fixes/P2-design.md`（packages: agate-scripts-sh/agate-scripts-py/agate-docs/agate-tests）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P6-acceptance.md`（验收结果，CHANGELOG 条目素材）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P7-consistency.md`（一致性结论）
- `agate-workspace/debt/tech-debt.md`（债务清单，debt_check）
- 参考：`CHANGELOG.md`（现有格式）、`README.md`（version badge 位置）、`agate/UPGRADING.md`（升级章节）
- `{agate_root}/assets/execution-roles/implementer.md`（P8 模式角色定义）
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
check-gate.sh P8 $TASK_DIR
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；当前版本 v0.44.0（README badge + git tag）
- 合并发布模式：TAG0005 先 READY，TAG0009 后完成，主 Agent 统一 bump v0.45.0 + tag + PR
- 本任务 P8 仅产出发布计划文档，实际 bump 在合并发布时
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
