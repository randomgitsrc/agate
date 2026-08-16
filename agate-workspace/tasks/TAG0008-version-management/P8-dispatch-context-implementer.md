> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P8
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
P8 发布准备（implementer P8 模式，releaser）：产出 P8-release.md（含 bump_type / debt_check / 版本变更确认 / CHANGELOG 确认 / 临时资源清单）+ 完成本任务**文档层联动改动**（P1 影响面表 2.2 声明、P7 标注归 P8 处理）+ 版本 bump + CHANGELOG 更新。**不执行 git commit/tag**（主 Agent 在 gate 后统一执行）。

### 约束
1. **版本 bump 判定**（P2 packages=[agate] 单包）：
   - 新功能（版本管理 6 组件 + 离线包）→ **minor**（v0.49.0 → v0.50.0）。理由：加功能、向后兼容（~/.agate 软链保留 + 回退 current）、不改既有 gate 判定 API。
2. **版本引用文件清单（agate 仓库特有，必须同步）**：
   - README.md version badge（GitHub 风格 shield）
   - CHANGELOG.md：新版本号章节（从 [Unreleased] 迁移 + 本任务变更条目）
   - version 文件（如有：查 agate/ 下或根目录 version/version.txt）
   - UPGRADING.md：**新增本版本章节**（破坏性变更逐条列——~/.agate 目录化 / .agate-version 语法 / hook 解析入口迁移 / agate-install 新工具）
   - 文档中写死版本号处（agate-summary.py 输出示例、SETUP 安装示例等）
3. **文档层联动改动（P1 影响面表 2.2 全部落地，P7 已标注归 P8）**：
   - README.md / README.zh-CN.md：新增"版本管理"接入方式（agate-install 流程）
   - agate/SETUP.md：新增「环境准备（agent 执行）」节（探测命令 exit code 可判 → 分平台修复 → 验证闭环）+ 路径叙述随版本目录调整
   - agate/UPGRADING.md：新版本章节（见上）
   - agate/platform-notes.md：latest/current 指针在无符号链接权限时的复制/配置文件模式说明
   - agate/AGENTS.md：升级/卸载叙述适配版本目录
   - agate/WORKFLOW.md：安装位置叙述（目录 + 解析）
   - agate/orchestrator-template.md / handoff-template.md / templates/project.md / adr.md：复核（`{agate_root}` 语义 / ADR-008 论据 / 默认安装位置）
   - agate/scripts/README.md：新增 4 脚本入清单（agate-install / agate-resolve / agate-pack-offline / install-offline）+ resolve-entry + 解析入口说明
   - install.sh：兼容保留（作为 agate-install 底层或替换，单软链场景仍可用）
4. **CHANGELOG 更新**：将 [Unreleased] 已有条目迁移到 v0.50.0 章节 + 追加本任务条目（版本管理机制 6 组件 + 离线部署包 + 环境探测）。
5. **debt_check 字段**：读 {AGATE_WORKSPACE}/debt/tech-debt.md（若存在），P8-release.md 写 `debt_check: reviewed` + 关联条目 id（评审 INFORMATIONAL/MEDIUM 建议项如 sha256 共享、manifest 签名、扫描限流 WARNING 等可登记为 DEBT 条目）。
6. **临时资源清单**：列出本任务执行的开发安装/临时数据（如 /tmp/opencode/tag0008-mv.sh 最小验证脚本、测试假 HOME 目录等）。
7. **P8 模式禁止 git commit/tag**——只改文件，不提交。
8. **双工作区纪律**：worktree 内改文件；`~/.agate` / 主 checkout 禁止改动。
9. **一致性**：改完协议文档后跑 `python3 agate/scripts/check-protocol-consistency.py --strict` 确认 0 ERROR（必须 worktree 自己的脚本）。

### 上游关联
- P7 一致性通过（BLOCKER=0，8/8 DESIGN_GAP 配对）
- P1 影响面表 2.2 文档层全部联动点
- P2 packages=[agate] 单包发布
- 当前版本 v0.49.0（主 checkout stable，本 worktree 基于 main）

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-requirements.md（影响面表 2.2 文档层清单）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P7-consistency.md（一致性结论 + 文档联动归 P8 标注）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/README.md / README.zh-CN.md / CHANGELOG.md / agate/SETUP.md / agate/UPGRADING.md / agate/platform-notes.md / agate/AGENTS.md / agate/WORKFLOW.md / agate/orchestrator-template.md / agate/scripts/README.md / install.sh（修改对象）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace/debt/tech-debt.md（若存在，debt_check）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（版本发布流程：README badge + CHANGELOG + UPGRADING 章节 + tag）
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；P7 已过；当前 stable v0.49.0
- 关键路径：worktree=/home/kity/oclab/agate/.worktrees/agate-TAG0008
- 查证结果：P2 packages=[agate] 单包；影响面表 2.2 文档层 13+ 文件；P7 标注文档联动归 P8
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
