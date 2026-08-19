> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0015
role: implementer
retry: 0
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 P8-release.md（发布准备核对，不执行 git commit/tag/版本文件改动——这些由主 Agent 在 gate
验证后统一执行）。组织方式参照
`agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P8-release.md`（同类协议机制任务的
已完成 P8 记录，可直接借鉴结构，但内容必须重新核实，不要照抄）。

### 约束

1. **版本决策**：当前基线 `v0.52.0`（`README.md:5` badge + `git describe --tags --abbrev=0`
   实测一致）。独立核实 bump_type——本任务七类改动（模板正文结构/内容价值标准/归因分层/技术债
   强制说明/资产沉淀标注/frontmatter 三字段/agate 反馈节/挂钩点、check-retrospective.py 新增
   分支（exit code 契约不变）、state-machine.md 新增 L2 checkpoint 小节、AGENTS.md 措辞同步、
   5 份存量文档标注、新增 agate-feedback.py 脚本、agate-md-field-get.py 新增 3 字段注册）均为
   **新增能力，无任何字段语义改变、无既有 gate 脚本行为对老任务产生拦截性变化**（`check-
   retrospective.py` 的 `sys.exit(0)` 恒定契约未变；`agate-md-field-get.py` 新增字段不影响
   既有 P1/P2/P6/P7 消费字段；`check-gate.py` 本身零改动）——按此判定 `bump_type: minor`
   （v0.52.0 → v0.53.0），不要凭空套用其他判定，要给出独立核实依据（引用具体文件/行号）。
2. **CHANGELOG 内容不能照抄 TAG0012 的段落结构**——逐条回查 `P4-implementation.md`「改动文件
   清单」原文重新组织表述，每条 CHANGELOG 条目须能追溯到本任务实际改动的具体文件和 BDD 编号
   （RM-AG0020/RM-AG0021 两条 roadmap 编号）。
3. **packages 声明与实际改动的对照说明**：`P1-requirements.md §9` 声明 6 个逻辑分组
   （`assets/templates`/`scripts`/`state-machine`/`phase-cards`/`docs-reviews-migration`/
   `core-protocol-docs`），P7-consistency.md §3b 已核实实际改动文件与这 6 组的对应关系（含
   1 项观察：`agate-workspace/roadmap/roadmap.md` 未被 packages 描述文字显式归类，但改动本身
   有 P1/P2 出处，不构成问题）——P8 只需引用 P7 该节结论，不需要重新逐文件核对一遍。
4. **debt_check**：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`，核对现存 DEBT 条目的 `task_id`
   是否有任何一条属于本任务（TAG0015-retrospective-feedback）或其归因的 RM-AG0020/AG0021——
   独立核实每条 DEBT 的 evidence/task_id，不要只看条目数就下结论。若无相关 → `debt_check: none`。
5. **临时资源清单**：本任务全程为纯协议文档 + Python 脚本改动（`agate-feedback.py`/
   `agate-md-field-get.py` 字段扩展/`check-retrospective.py` 分支），P4/P5/P6 阶段均未启动
   任何 debug server/临时数据库/端口占用/开发安装——核实这一点后如实声明"无临时资源"，不要
   凭空假设。
6. **发布检查命令清单**：从 P2-design.md §5 `gate_commands` 抄录（P3 三文件 pytest + P5
   链式命令），列出供主 Agent 在 gate 验证阶段重跑，本 releaser 不重跑（P5 已跑过，结果仅供
   参照标注"非本次结果"）。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P1-requirements.md（frontmatter
  packages/domains + BDD 原文）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P2-design.md（§5 gate_commands）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P4-implementation.md（改动文件清单
  + DESIGN_GAP）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P6-acceptance.md（20/20 PASS）
- {AGATE_WORKSPACE}/tasks/TAG0015-retrospective-feedback/P7-consistency.md（跨文件核对结论）
- {AGATE_WORKSPACE}/debt/tech-debt.md（债务清单核对）
- agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P8-release.md（结构参照，内容不可
  照抄）

### 门槛（什么算完成）
P8-release.md 含：`bump_type`（独立核实依据）、`debt_check`（逐条核对结论）、版本号变更确认、
CHANGELOG [Unreleased]→新版本号 内容建议、发布检查命令清单、临时资源清单（如实声明）。
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
- 当前版本：v0.52.0（`README.md:5` badge + `git describe --tags --abbrev=0` 一致）。
- P2-design.md §5 gate_commands 原文：
  `P3: python3 -m pytest agate/tests/unit/test_check_retrospective.py agate/tests/unit/
  test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
  `P5: python3 -m pytest agate/tests/ -q --tb=no && python3 agate/scripts/
  check-protocol-consistency.py --strict`
- P5 阶段实测结果（commit ae7dc57）：932 passed + 2 skipped + 0 failed；0 ERROR / 305 WARNING。
- P6-acceptance.md frontmatter：`pass: 20`, `fail: 0`。
- P7-consistency.md frontmatter：`blocker_count: 0`, `design_gap_count: 1`,
  `design_gap_reviewed_count: 1`。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
