> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P8-release.md（发布准备记录）。**你不执行 git commit / git tag / 版本文件改动**——只做核对
与声明，bump 动作由主 Agent 在 gate 验证后统一执行。参照先例：
`{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P8-release.md` 是同类协议机制任务的已
完成 P8 记录，本任务组织方式可直接借鉴（agate 自身无独立多包，`packages:` 是逻辑分组，单版本号）。

### 约束

1. **版本号决策**：当前 `README.md` version badge 为 `v0.51.0`（`git describe --tags --abbrev=0`
   同为 `v0.51.0`）。本任务新增机制（verification_env 失败处理协议/timeout_seconds 字段/
   P0-brief 漂移判据/同类扫描强制节/命令超时兜底）全部是**新增可选内容或新增强制性文档要求**，
   不破坏任何既有字段语义（`timeout_seconds` 缺字段行为等同现状；新增的"推进条件"checklist 项
   是流程要求不对应脚本 exit code 变化，不会拦截老任务）——判定为 **minor**（`v0.51.0 → v0.52.0`）。
   你需要独立核实这个判断（检查是否真的没有破坏性变更），不要直接采信本段结论。
2. **P2 packages 声明与实际改动的对照说明（P7 已记录的观察点）**：P2-design.md frontmatter 声明
   `packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates,
   scripts]`，但 P7-consistency.md 已核实**实际改动的 12 个文件中没有一个在 `agate/scripts/`
   目录下**（唯一新增的"代码"是 `agate/tests/unit/test_protocol_mechanism_anchors.py`，属于
   `agate/tests/`，不属于 `agate/scripts/`）。这是逻辑分组声明与实际改动范围的措辞差异，不是
   一致性问题（P7 已判定不阻塞）——你在 P8-release.md 里如实写清楚这个差异，不要为了凑"packages
   声明"而虚报改了 `scripts/`。
3. **CHANGELOG.md 更新**：在 `[Unreleased]` 或新增 `## [0.52.0] - {日期}` 章节（参照 CHANGELOG.md
   现有 v0.51.0 章节的格式：新增/变更/测试三段式），内容基于 P4-implementation.md 的改动清单 +
   P1-requirements.md 的 5 条 RM 编号（RM-AG0013/RM-AG0014 主体+补充/RM-AG0019/RM-AG0016）。
   **只描述本任务真实做了什么**，不要照抄 TAG0014 的 CHANGELOG 段落。
4. **debt_check 字段**：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在）确认有无本任务相关的
   遗留债务条目；本任务在 SELF-GATE alignment-review 的 A7 项已讨论过"止损轮次不入 .state.yaml"
   这一取舍，但主 Agent 已裁决"暂不追加新 ADR、不登记为债务"（P2-design.md §2.3 已记录为设计
   取舍非债务）——因此本任务预期 `debt_check: none`，但你需要独立核实 tech-debt.md 现状，不要
   凭空假设。
5. **发布检查命令**：从 P2-design.md `gate_commands` 读取（P3/P5/P5_consistency/P5_count/
   P5_shellcheck），在 P8-release.md 里列出，供主 Agent 在 gate 验证阶段重跑。你**不需要**自己
   重跑这些命令（P5/P6/P7 已跑过，P8 gate 验证阶段主 Agent 会亲自重跑一遍确认 bump 后仍全绿）。
6. **临时资源清单**：本任务全程无临时服务/进程/数据库/端口占用/开发安装（纯协议文档 + 测试文件
   改动），如实声明"无"。
7. **版本文件核对**：确认 `README.md` version badge 的准确位置（行号），供主 Agent 后续执行
   bump 时定位；不要自己修改该文件。

### 上游关联

- P7-consistency.md（approved，BLOCKER=0，两条非阻塞观察已在上方约束 2 中处理）
- P4-implementation.md（12 个改动文件清单，CHANGELOG 内容来源）
- P1-requirements.md（5 条 RM 编号来源）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P2-design.md（packages 声明 + gate_commands）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P4-implementation.md（改动清单）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P7-consistency.md（两条观察点原文）
- CHANGELOG.md（现有格式参照，尤其最新 [0.51.0] 章节）
- README.md（version badge 位置）
- {AGATE_WORKSPACE}/debt/tech-debt.md（若存在，债务核对）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P8-release.md（组织方式参照）
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
- 环境状态：worktree HEAD 已含 P7 commit（41cf435）。当前版本 v0.51.0（README badge + git tag
  一致）。CHANGELOG.md 最新章节是 `[0.51.0] - 2026-08-18`（TAG0006）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
