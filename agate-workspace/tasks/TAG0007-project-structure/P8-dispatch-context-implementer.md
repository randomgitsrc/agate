---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。你是 releaser（implementer P8 模式）——只产出
P8-release.md（+ 直接编辑 CHANGELOG.md 正文，见约束 4），**不执行 git commit/tag/bump-version**，
这些由主 Agent 在 gate 验证通过后亲自执行。

### 目标
产出 P8-release.md：版本 bump 建议 + 债务清单确认 + 发布检查命令结果 + 临时资源清单。

### 约束

1. **包声明核对（单包发布）**：P2-design.md frontmatter 声明
   `packages: [phase-cards, execution-roles, templates, scripts]`。核实：agate 是单一协议仓库，
   无独立子包发布结构（无 per-package 版本文件），P2 的 `packages` 字段是**改动范围分类**，
   不是多包发布场景清单——不需要拆批发布、不需要各自独立 bump。**单包发布，无 SCOPE_GAP**（同类
   先例：TAG0017 的 P8-release.md「包声明核对」节）。

2. **bump_type 判定**：
   - 当前版本（README.md / README.zh-CN.md badge）：`v0.55.0`
   - 本任务新增了两个全新协议机制（RM-AG0008 骨架脚手架 + RM-AG0009 CODE-MAP 架构演进纪律），
     均为**向后兼容的新能力**（`project_phase`/`code_map_new_files_count`/
     `code_map_reviewed_count` 均为可选字段，缺失时行为与改动前逐字节一致，12 个新增测试用例
     已验证回归安全）——加功能，不改变现有 API/CLI 行为 → **minor**
   - 无破坏性变更（未删除/修改任何既有字段语义，`gate_p2`/`gate_p4`/`gate_p7` 新增分支均为
     纯增量判定）→ 排除 major
   - 请按上述依据自行核实并给出判定，预期结论：`bump_type: minor`，`v0.55.0 → v0.56.0`
     （同类先例：TAG0017 v0.54→v0.55 minor、TAG0012 v0.51→v0.52 minor）

3. **CHANGELOG 更新**：直接编辑
   `/home/kity/oclab/agate/.worktrees/agate-TAG0007/CHANGELOG.md`，在 `## [0.55.0]` 节**之上**
   新增 `## [0.56.0] - 2026-08-20` 节。格式参照现有 `[0.55.0]` 节结构（三级标题「新增」+ 分组
   小标题）。内容至少覆盖：
   - RM-AG0008（0→1 骨架脚手架）：`project_phase: bootstrap` 字段、`P2-skeleton.md` 产出、
     骨架模板参数化、`gate_p2` 新增判定
   - RM-AG0009（CODE-MAP 架构演进纪律）：`agents/CODE-MAP.md` 维护物、「新增文件核对表」机制、
     `gate_p4`/`gate_p7` 新增判定（两层 pairing 校验）、consistency-reviewer CODE-MAP 核对职责
   - 关联 BDD 覆盖（11 条全覆盖，可提及 BDD 组划分）
   - 提及新登记的 DEBT0016（CODE-MAP 路径解析简化推导）+ DEBT0017（gate_p4 子串判定假阴性 +
     自我应用缺口），均为 `open` 状态未关闭
   **不要修改 README.md / README.zh-CN.md 的 version badge**（留给主 Agent 执行）。

4. **debt_check 字段**：`debt_check: reviewed`。核对
   `{AGATE_WORKSPACE}/debt/tech-debt.md`，本任务本轮新登记的 2 条债务
   （DEBT0016、DEBT0017，均 `status: open`，`task_id: TAG0007`）**不要求本次关闭**——两条的
   `closure_criteria` 都是"留待后续任务处理"性质（DEBT0016：改用 `resolve_workspace` 权威函数；
   DEBT0017：`gate_p4` 改整行匹配 + 后续自我应用补齐），不是本任务范围内必须完成的收尾项。
   在 P8-release.md 正文列出这 2 条债务 id + 状态 + 一句话说明"本轮登记，留待后续任务关闭"，
   不建议本次改为 closed（与 TAG0017 场景不同——TAG0017 的 5 条债务是继承自更早任务且本轮已
   满足 closure_criteria，TAG0007 的 2 条是本轮才发现且明确设计为留待未来处理）。

5. **发布检查命令与结果**：沿用 P0-brief.md `env_constraints.test_cmd` 声明的命令（不用
   `--strict`），汇总本任务全程已验证的结果（可直接引用 P5-test-results/unit.md + P6-evidence/
   test-output.log，不需要重新跑一遍——除非你想独立复核）：
   - `python3 -m pytest agate/tests/ -q --tb=no` → 1028 passed, 2 skipped, 0 failed
   - `python3 agate/scripts/check-protocol-consistency.py`（默认模式）→ 0 ERROR
   - `bash agate/tests/scripts/count-tests.sh` → 1030 个测试用例
   - `shellcheck -S warning agate/scripts/*.sh` → 0 issue
   是否可直接判定为本次 P8 gate 的"发布检查命令全部 exit 0"证据，取决于主 Agent 执行
   `check-p6-provenance.py --audit7-only` 后的 `AUDIT7_RESULT` 判定——你不越权代主 Agent 做该
   判定，仅如实转述已有证据。

6. **Lessons Learned**（2-3 条）：建议覆盖——① P2 review 首轮打回的 pairing 字段对应关系错误
   （复用既有机制模板时，字段对应关系是最容易写反的地方，即使有源码可参照）；② self-gate 事后
   补做暴露的教训（commit 前应先做 self-gate 审查，而非事后补救——虽然本次补救成功且发现了 5 处
   真实文档传播缺口）；③ dogfooding/自指场景下 gate 判定逻辑的字符串匹配脆弱性（DEBT0017：
   子串包含判定容易被"描述机制本身的文字"误伤，未来新增类似 gate 检查时应优先用整行/结构化
   匹配而非子串包含）。

7. **临时资源清单**：本任务全程未启动任何临时服务/进程/数据库/端口，无开发安装（纯脚本+协议
   文档改动，静态验证：pytest 单元测试 + check-protocol-consistency.py 静态扫描 + shellcheck
   静态检查）。

### 上游关联
P7-consistency.md（approved，BLOCKER=0）→ 本阶段。P2-design.md packages 声明供包核对；
P4/P5/P6 的既有证据供发布检查命令结果汇总。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P0-brief.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（packages 声明）
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P5-test-results/unit.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P6-acceptance.md
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P7-consistency.md
- {AGATE_WORKSPACE}/debt/tech-debt.md（DEBT0016/DEBT0017 条目）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/CHANGELOG.md（`[0.55.0]` 节格式参照）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/README.md（版本 badge 当前值）
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P8-release.md（同类协议任务 P8 产出格式参照，
  只借鉴结构，不照抄内容）
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
- 当前版本：v0.55.0（README.md/README.zh-CN.md badge）
- P2-design.md packages：[phase-cards, execution-roles, templates, scripts]（单一协议仓库改动
  范围分类，非多包发布场景）
- P5/P6 已确认全部命令 exit 0：pytest 1028 passed/2 skipped/0 failed；consistency 0 ERROR；
  count-tests 1030 用例；shellcheck 0 issue
- 本任务新登记 DEBT0016（P4 阶段）+ DEBT0017（P7 阶段），均 open，均非本轮关闭范围
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
