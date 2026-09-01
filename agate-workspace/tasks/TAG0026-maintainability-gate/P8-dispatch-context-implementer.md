---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0026
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

发布准备（releaser，implementer P8 模式）：产出 `P8-release.md`——bump 判定、debt_check、
CHANGELOG 草案、临时资源清单。**你不执行 git commit/tag、不改 README/pyproject——
bump 与版本文件改动由主 Agent 在 gate 验证后亲自执行。**

### 约束

1. **bump 判定**：本任务 = 新增协议功能（新 gate 脚本 + check-gate.py P4 挂载 + 模板 +
   卡片机制条目），无破坏性变更（不改既有协议语义/数据格式；唯一行为扩展是 gate_p4 新增
   一步且 violations 为空时行为不变，P4-review 已核）→ 建议 **minor**（v0.64.0 → v0.65.0）。
   在 P8-release.md 显式声明 bump_type + 理由。
2. **debt_check**：读 `agate-workspace/debt/tech-debt.md`，确认 DEBT0023（本任务 P2 登记，
   status: open，priority: low，不阻断发布）→ `debt_check: reviewed`，正文列条目 id
   （DEBT0023 + 其它 open 条目如 DEBT0014 若仍 open 一并列出）。
3. **CHANGELOG 草案**：给出本任务条目文本（放 [Unreleased] 下，主 Agent 决定版本段标题），
   对齐现有条目风格（加粗开头 + 一句话机制描述）。注意 [Unreleased] 现有 TAG0025 内容
   （品牌文案等）——你只追加本任务条目，不动既有内容；版本段切分建议（Unreleased 整体
   变 v0.65.0 或仅本任务入新段）给出建议但标注"主 Agent 定夺"。
4. **UPGRADING 提醒**：新版本须新增章节（无破坏性变更也写"（无破坏性变更）"，v0.62.0
   教训）——在 P8-release.md 写明该 checklist 项（内容由主 Agent 亲自执行，你给要点草案：
   TAG0026 新增 check-maintainability.py 与 P4 三重门槛对已有任务的兼容性说明——既有任务
   无 known-violations.md 时三重门槛仅在 violations 非空时触发，空场景零行为变化）。
5. **roadmap 回写提醒**：RM-AG0046（roadmap.md :51，scheduled → done）回写是 P8 gate
   硬校验（RM-AG0043），由主 Agent 执行——你在 P8-release.md 列为 checklist 项。
6. **版本引用文件清单**（Agateon 仓库特有，全列入 checklist）：README.md version badge
   / CHANGELOG / UPGRADING 章节 /（无其它硬编码版本——README 优先写"稳定版"）。
7. **临时资源清单**：本任务无启动服务/无安装/无临时端口——写 none（P6 验收用的 tmp 场景
   脚本在 /tmp，属系统临时区自动清理，列出说明）。
8. **发布检查命令**：读 P2-design.md §4 gate_commands，P8 阶段主 Agent 将按 AUDIT7 判定
   决定复用 P5 证据或重跑——你在 P8-release.md 写明该验证计划（AUDIT7_ONLY 命令 +
   两分支动作）。
9. **不 commit**：全程不改 git 状态；禁 worktree git 写操作（只读 log/diff 可）。
10. **PROD 隔离**：返回报 [PROD_NOT_TOUCHED]；所有 bash timeout。

### 输入文件

1. `agate-workspace/tasks/TAG0026-maintainability-gate/P2-design.md`（§4 gate_commands / §1 packages）
2. `agate-workspace/tasks/TAG0026-maintainability-gate/P7-consistency.md`（一致性结论）
3. `agate-workspace/debt/tech-debt.md`（open 条目）
4. `CHANGELOG.md`（[Unreleased] 现状与条目风格）
5. `agate/UPGRADING.md`（章节结构）
6. `agate-workspace/roadmap/roadmap.md`（RM-AG0046 行 :51）
7. `AGENTS.md`（版本发布清单节）
8. `timeout 30 git log v0.64.0..HEAD --oneline`（本版本周期 commit 概览，对照 CHANGELOG 无遗漏）

### 产出（路径硬约束）

/home/kity/oclab/agateon/.worktrees/agate-TAG0026/agate-workspace/tasks/TAG0026-maintainability-gate/P8-release.md
frontmatter（agate-md-field-set，先 --list）：phase: P8 / task_id: TAG0026 / type: release /
parent: P7-consistency.md / trace_id: TAG0026-P8-20260830 / status: draft / created: 2026-08-30 /
agent: implementer。正文含：bump_type + 理由 / debt_check: reviewed + 条目 id 清单 /
CHANGELOG 条目草案 / UPGRADING 要点草案 / roadmap 回写 checklist / 版本引用文件 checklist /
AUDIT7 验证计划 / 临时资源清单。
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
### A. 版本现状（主 Agent 已核，2026-08-30 实测）
- 最新 tag：v0.64.0（2026-08-26）；README.md badge：v0.64.0（:12）；pyproject.toml 无 version 字段（单包文档型项目，版本以 README badge + CHANGELOG 为准）
- CHANGELOG：[Unreleased] 段已有 8 条（TAG0025 收尾内容：品牌文案/DSH preset 显示名/测试并行化文档/agate-summary DSH 校验/TAG0025 复盘措施/DEBT0022 关闭/删假想版本锚点/HANDOFF 归档）——注意核对 `git log v0.64.0..HEAD` 确认这些改动在 0.64.0 tag 之后（是→Unreleased 归属正确）
- UPGRADING：最新章节 v0.64.0（:92），新版本须新增章节（无破坏性变更也要写）
- roadmap RM-AG0046（:51）：状态 scheduled，关联任务 TAG0026 → P8 gate 硬校验须回写 done
- 主流程 git 链：f7e7b9f（P4）→ acf0cb2（P5）→ 7af1e72（P6）→ 5d828c9（P6.5）→ 1053472（P7）
- 本任务改动文件面（P8 bump 范围参考）：agate/scripts/ 4 脚本 + agate/assets/templates/ + agate/phase-cards/ 2 卡 + agate/tests/unit/ 2 测试文件 + agate-workspace/{maintainability.yaml,debt/tech-debt.md,tasks/}
- DEBT0023：open / low / 不阻断发布（TAG0026 P2 登记）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
