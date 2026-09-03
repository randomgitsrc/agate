---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0027
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

**P8 发布准备（releaser，implementer P8 模式）**：产出 `P8-release.md`（发布记录：bump_type、
版本号变更确认、CHANGELOG 更新建议、debt_check、临时资源清单、Lessons Learned）。
**不执行 bump-version / git commit / git tag**（主 Agent 在 gate 验证后亲自执行）。

### 约束

1. **单包**（packages=[agate-protocol]——P2 声明）→ 直接产出 P8-release.md（不走多包合并）。
2. **bump_type 判定**（P2 §4.1 + 版本发布清单）：TAG0027 = 新增 3 CLI（agate next/advance/
   dispatch）+ phases.yaml 加字段（gate_pass_exit 等）+ 编排语义文档化 + CHECK 14/15——加功能
   向后兼容（check-gate/check-state-transition 返回语义不变，BDD-13）→ **minor**（v0.65.0 →
   v0.66.0）。在 P8-release.md 显式声明 bump 理由。
3. **P8-release.md 必含**：
   - `bump_type: minor` + 理由
   - `debt_check: reviewed`（附核对的 DEBT 条目——见 debt/tech-debt.md，重点核对本任务是否
     产生新债如 DEBT0023 相关 + P2 review/exit2fix 是否登记过债）
   - 版本号变更确认（README badge v0.65.0 → v0.66.0 建议）
   - CHANGELOG [Unreleased] → [0.66.0] 的变更条目建议（按 CHANGELOG 格式：新增/变更/修复分节，
     列本任务关键交付）
   - 临时资源清单（本任务启动了哪些临时服务/进程/数据/开发安装——预期：无，pytest 仅本地跑）
   - Lessons Learned（2-3 条关键教训）
   - **UPGRADING.md 需新增 v0.66.0 章节**（无破坏性变更也写"（无破坏性变更）"——版本发布
     清单硬要求）——P8-release.md 里注明该动作
4. **roadmap 回写**：RM-AG0054 在 roadmap.md scheduled → 主 Agent 在 P8 commit 前回写 done
   （RM-AG0043 P8 gate 硬校验）——P8-release.md 注明此动作由主 Agent 执行。
5. **CHANGELOG/版本文件**：releaser 只产出**建议**（改动清单），不实际改 README/CHANGELOG/
   UPGRADING（主 Agent 执行 bump）。
6. **分阶段落盘** P8-progress.md（勿攒）。[PROD_NOT_TOUCHED]。

### 上游关联

- P2-design.md（packages=[agate-protocol] + §4.1 gate_commands）
- P7-consistency.md（approved——P8 前置）
- P6-acceptance.md（26 PASS）+ P6.5-judge-verdict.md（passed）
- 版本基线：最新 tag v0.65.0（2026-08-30）、README badge v0.65.0、CHANGELOG [Unreleased] 空
- CHANGELOG 近期格式参照（TAG0026 条目——新增/变更/修复分节）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0027-orchestration-semantics/P2-design.md`（packages + gate_commands）
2. `agate-workspace/tasks/TAG0027-orchestration-semantics/P7-consistency.md`（一致性结论）
3. `agate-workspace/tasks/TAG0027-orchestration-semantics/P0-brief.md`（范围）
4. `CHANGELOG.md`（格式参照 + Unreleased 现状）
5. `README.md`（version badge 行）
6. `agate/UPGRADING.md`（章节格式——新增 v0.66.0 章节建议）
7. `agate-workspace/debt/tech-debt.md`（debt_check 核对）
8. `agate-workspace/roadmap/roadmap.md`（RM-AG0054 行）
9. `AGENTS.md`（版本发布清单——项目约定）

> ⚠️ 只读 + 产出建议文档。产出写任务目录 P8-release.md。不 commit/不 tag/不改 README/
> CHANGELOG/UPGRADING（那些主 Agent bump 时做）。

### 产出文件字段

- `P8-release.md`（frontmatter：phase/task_id/type/parent/trace_id/status/agent + bump_type/
  debt_check 用 agate-md-field-set 写）。
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
### A. 路径拓扑
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0027`
- 任务目录 = `agate-workspace/tasks/TAG0027-orchestration-semantics/`
- 版本基线：v0.65.0（最新 tag）

### B. 本任务关键交付（CHANGELOG 条目素材）
- 新增：agate next / agate advance / agate dispatch 三 CLI
- 新增：phases.yaml next/retreat/gate_subphase/gate_pass_exit 字段 + schema
- 新增：check-protocol-consistency CHECK 14（md 段落平台名）/ CHECK 15（数据面词边界）
- 变更：check-structure-consistency S-1/S-2 next/retreat 加列比对
- 变更：check-p6-provenance 审计 2 双锚点（CARD-SOURCE）+ check-judge-verdict Fix C
- 变更：check-gate.py 头注释 exit 2 语义说明（返回逻辑不变）
- 文档：协议文档平台名三分类清理（实现注记标记）+ 编排心智统一
- 测试：+48 用例（tag0027 批）

### C. 需在 P8-release.md 注明的动作（主 Agent 执行）
- bump README badge v0.65.0 → v0.66.0 + CHANGELOG [Unreleased] → [0.66.0] + UPGRADING 新增
  v0.66.0 章节 + git tag v0.66.0 + roadmap RM-AG0054 回写 done
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
