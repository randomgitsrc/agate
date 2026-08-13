> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P8
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0004
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P8-release.md`——TAG0004 发布准备。确定版本 bump 类型、版本号变更确认、CHANGELOG 更新内容、debt_check 字段、临时资源清单。**不执行 git commit/tag**（主 Agent 在 gate 验证后亲自执行）。

### 约束

- **只做发布准备，不执行 git 操作**：不 commit、不 tag、不改 .state.yaml。
- **版本判断**：当前 v0.43.0。本任务是 bug 修复 + 环境适配（不改公共 API 行为、不破坏性变更）→ **bump_type: patch**（v0.44.0）。若你认为应 minor（如 Windows 兼容算新能力），在 P8-release.md 显式声明理由，主 Agent 判断。
- **P2 packages 声明**（7 项）：agate-scripts-sh / agate-scripts-py / agate-phase-cards / agate-docs / agate-gitconfig / agate-ci / agate-tests——实际改动覆盖这 7 项，全部纳入 CHANGELOG。
- **CHANGELOG 位置**：仓库根 `/home/kity/oclab/agate/.worktrees/agate-TAG0004/CHANGELOG.md`（Keep a Changelog 格式）。新增 `## [0.44.0] - 2026-08-13` 段，内容按「新增 / 变更 / 文档」组织，覆盖：
  - S1 pre-commit-gate.sh 空格路径 fail-open 修复（数组化）
  - S3 13 py encoding + grep 断言审计
  - S2 check-p6-evidence 中文证据文件名
  - M4/M5 全角冒号 POSIX locale（check-gate.sh / check-p6-format.sh alternation）
  - M6 frontmatter 提取 CRLF 容错
  - M9 路径正则元字符（grep -F 前缀）
  - Q1 agate-next-card.sh 路径归一化
  - Q2 7 张 phase-cards 补注规则 2 语义
  - Q5 SETUP.md Windows 章节 + .gitignore 预设
  - RM-AG0001 check-gate P1 反引号盲区
  - RM-AG0002 + TPV0090-M4 check-tdd-red A/B 判定增强（无 formatter 关键词判定 + NameError B 类）
  - 其他：.agate.env CR / 复制模式 AGATE_ROOT / sed 转义
  - CI windows-latest matrix
  - 版本 badge：README.md `v0.43.0` → `v0.44.0`
- **version 文件**：仓库无独立 version.txt（README badge 即版本标识）。P8-release.md 记录"version 文件 = README.md badge"，主 Agent 执行 bump 时改 README。
- **debt_check 字段**：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在）确认；本任务无回退（retreat）历史，写 `debt_check: none` 或 `reviewed`（若 debt 文件有相关条目）。
- **临时资源清单**：本任务执行期间启动的临时服务/进程/数据/开发安装——P4-P7 只在 worktree 跑 bats/gate，未启动服务、未装包，写入"无临时服务/进程；无开发安装；/tmp/opencode 下有临时验证日志（可清理）"。
- **Lessons Learned**：P8-release.md 增加 2-3 条关键教训（TDD 空返回拆分、LC_ALL=C 实测、跨平台正则）。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`。改用"通过/失败"或加引号。

### 上游关联

- P7-consistency.md approved：BLOCKER=0、DESIGN_GAP 1 条 REVIEWED、SCOPE+ 闭环。
- P6-acceptance.md：37/37 PASS、0 FAIL。
- P2-design.md packages：7 项。
- 当前版本 v0.43.0（git tag + README badge + CHANGELOG [0.43.0]）。

### 输入文件

- `agate-workspace/tasks/TAG0004-env-adaptation/P2-design.md`（packages 声明）
- `agate-workspace/tasks/TAG0004-env-adaptation/P7-consistency.md`（一致性结论）
- `agate-workspace/tasks/TAG0004-env-adaptation/P0-brief.md`（任务简报）
- `CHANGELOG.md`（仓库根，Keep a Changelog 格式参考）
- `README.md`（版本 badge）
- `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在，debt_check 依据）
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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`；协议 v0.43.0；P7 已 commit（f9f6957）
- 关键路径：产出 `agate-workspace/tasks/TAG0004-env-adaptation/P8-release.md`
- 查证结果：当前 tag v0.43.0；README badge v0.43.0；CHANGELOG 顶部 [0.43.0]
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
