> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P8
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

T001（agate v0.40.0 结构化数据改造）P0-P7 已全部通过（P7 一致性检查 approved，BLOCKER=0）。本次是 P8 发布准备——**只做准备，不执行 git commit/tag**（那是主 Agent 的工作）。

### 命名澄清（重要，避免你自己搞混）

"v2.0" 只是本次改造的世代代号（worktree 目录名 `.worktrees/v2.0`、分支名 `feat/v2.0`），**不是实际 semver**。agate 走 v0.x 版本线，本次要 bump 到的**真实版本号是 v0.40.0**（当前 README badge 是 v0.35.0）。到处都不要写"v2.0.0"，写"v0.40.0"。

### 约束

1. **不执行 git commit / git tag / bump-version**——这些由主 Agent 在你产出后亲自验证+执行。你只准备内容。
2. **产出 `docs/tasks/T001-v2.0-structured/P8-release.md`**，必须包含：
   - `bump_type: minor`（0.35.0 → 0.40.0，符合 `agate/WORKFLOW.md` 版本说明"规则新增/调整升minor"——本次是大量新增机器可读格式规则，非破坏性大改架构，不是 major；也不是纯 bug fix 的 patch）
   - 版本号变更确认：说明 `README.md` 第 6 行 version badge 需要从 `v0.35.0` 改为 `v0.40.0`（**你不改，只在报告里写清楚要改哪个文件哪一行改成什么**，主 Agent 会亲自执行这一步）
   - CHANGELOG 更新确认（见下方约束 3，你需要实际写入 CHANGELOG.md 的 `[Unreleased]` 区域内容，这一步你要做，因为 gate 检查在 bump 前需要看到 `[Unreleased]` 里含 T001）
   - 临时资源清单：本任务全程未启动任何调试服务/进程/临时数据库（纯 bash/python 脚本 + bats 测试，无需起服务），如实写"无临时资源"
3. **CHANGELOG.md 更新（你要实际执行这一步，写入 `[Unreleased]` 区域）**：
   - `CHANGELOG.md` 当前没有 `[Unreleased]` 区域（在 `# 变更日志` 说明段和 `## [0.35.0]` 之间插入一个新的 `## [Unreleased]` 区块）
   - 内容需要总结 T001 v0.40.0 的全部变更（写作角度参考现有 `## [0.35.0]` 条目的详略程度和分类风格：修复/新增/变更 这类分组），核心内容至少覆盖：
     - 机器字段从"正文内嵌 YAML/正则提取"迁移为"frontmatter + pyyaml + schema 校验"（流A：新增 `agate-frontmatter-check.py`/`check-frontmatter.sh`，`agate-md-field-get.py` 双读改造）
     - P6/P7 结果结构化（流B：frontmatter pass/fail/blocker_count 等汇总字段）
     - P1 标记状态结构化 + 角色卡/模板可复制 frontmatter 样例（流C）
     - 任务编号规则硬切为 `T[A-Z]{2}\d+`（流D，如 `TAG0001`），不兼容旧格式
     - CHECK 9 锚点表 37→38
   - **必须含 "T001" 字样**（`check-changelog.sh` 的 gate 校验靠这个关键词匹配，不含会被拦截）
   - 参考来源：`docs/tasks/T001-v2.0-structured/P4-implementation.md`（六个小节的完整变更记录）、`docs/tasks/T001-v2.0-structured/P7-consistency.md`（已核实的最终状态）
4. **自查用命令**（自查不是 gate，主 Agent 会亲自跑最终验证）：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   CHECK_CHANGELOG_MODE=normal bash ~/.agate/scripts/check-changelog.sh T001
   ```
   应该 exit 0（[Unreleased] 区域含 T001）。
5. **不要修改任何脚本/测试文件**——本阶段只写 P8-release.md + CHANGELOG.md 的 `[Unreleased]` 部分，不碰 `agate/scripts/**`、`agate/tests/**`、其他协议文档。
6. **不要修改 README.md**——版本 badge 的实际修改由主 Agent 执行（约束 2 已说明，你只在报告里指出要改什么）。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（完整实现记录，CHANGELOG 内容的主要来源）
- `docs/tasks/T001-v2.0-structured/P7-consistency.md`（一致性检查结论，approved，可作为"确认无遗留问题"的引用）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §4（`packages: [agate]`，本次 bump 对象）

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义，P8 模式）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（全文，CHANGELOG 素材）
- `docs/tasks/T001-v2.0-structured/P7-consistency.md`
- `CHANGELOG.md`（现有格式风格参考，尤其 `## [0.35.0]` 条目）
- `agate/WORKFLOW.md`（版本号 major/minor/patch 判断依据，开头几行有说明）
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
- 环境状态：worktree `feat/v2.0`，HEAD `a1edf02`（P7 一致性检查通过后）。`.state.yaml` phase=P7 status=active。
- 当前 README.md 版本 badge：`v0.35.0`（第 6 行）。目标：`v0.40.0`。
- CHANGELOG.md 当前无 `[Unreleased]` 区域，最新条目是 `## [0.35.0] - 2026-08-09`。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
