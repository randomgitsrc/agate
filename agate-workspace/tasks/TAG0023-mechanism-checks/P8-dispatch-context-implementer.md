# P8-dispatch-context-implementer — TAG0023 发布准备

> 派发对象：implementer（P8 releaser 模式）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> **你不执行 git commit/tag/bump-version**——只产出 P8-release.md + 更新 CHANGELOG.md 正文内容 + 登记技术债，主 Agent 在 gate 验证通过后亲自执行 bump-version/commit/tag。

## 目标

1. 产出 `P8-release.md`（bump_type/debt_check/版本号变更确认/CHANGELOG确认/临时资源清单）
2. 更新 `CHANGELOG.md`：在文件顶部（`## [0.61.0]` 之前）新增 `## [0.62.0] - 2026-08-25` 小节，`### 新增（TAG0023：机制校验补强批，RM-AG0042~RM-AG0045）` 子标题，列出本次 4 个子项的用户可见变更（参照文件里 TAG0022/TAG0021 等既有条目的写法风格，逐条列出：门槛失败事件↔retries对应性校验 / P8 roadmap done反查 / 环境敏感测试根因修复+集中清单+CI重跑 / 声明写时自检+错误提示增强）
3. 登记 3 条技术债（DEBT0019/0020/0021）到 `{AGATE_WORKSPACE}/debt/tech-debt.md`，来源于 P4-review.md 的 3 条 INFORMATIONAL 发现（见下方「技术债登记内容」）

## bump_type 判定

**minor**（新增机制/校验能力，无破坏性变更，向后兼容——新增的 P8 roadmap 校验只在有 roadmap 关联记录时触发，不影响无关联的既有任务；新增的 retries 对应性校验 BDD-1/3 是 WARNING 不阻断，BDD-2 阻断但只影响真实违规场景）。当前版本 `v0.61.0` → 新版本 `v0.62.0`。

## 技术债登记内容（3 条，来源 P4-review.md INFORMATIONAL 三项，标准三分法判据：不修不影响本任务验收，但会让未来变更更贵/更危险）

### DEBT0019（roadmap.md 表格解析脆弱）
- category: technical
- title: `check-gate.py._check_roadmap_done()` 用固定索引 `split("|")` 解析 roadmap.md 表格，无列数完整性校验
- priority: low
- evidence: ref `agate/scripts/check-gate.py`（`_check_roadmap_done()` 约 L1181-1206），note 引用 P4-review.md 原文："已用 awk -F'|' 核实当前 roadmap.md 全文无嵌入 | 的标题行...但标题是自由技术文本，一旦未来某条描述里写进字面 |...列会整体错位"
- impact: 未来若 roadmap.md 某行描述文本包含字面 `|` 字符，该行状态判定可能错位（漏判或误判）
- recommendation: 加一条"实际列数应为 9（含首尾空列）否则跳过/WARNING"的防护，不必用完整 markdown 表格解析器
- closure_criteria: 新增防护逻辑 + 对应回归用例（构造含 `|` 字符的行验证不误判）+ 全量测试通过
- source: review
- created_at: 2026-08-25
- task_id: TAG0023

### DEBT0020（roadmap_path 硬编码相对路径）
- category: technical
- title: `check-gate.py._check_roadmap_done()` 调用点用相对 CWD 的硬编码路径拼接 roadmap.md，与同批次其他新增函数的 repo-root 定位风格不一致
- priority: low
- evidence: ref `agate/scripts/check-gate.py`（约 L1224），note 引用 P4-review.md 原文："若脚本被非仓库根 CWD 调用，_read_text(roadmap_path) 静默返回''...'路径解析失败'和'确实无关联RM'被静默合并成同一结果"
- impact: 环境差异下（非仓库根 CWD 调用）新增的 P8 roadmap-done 检查可能被静默绕过而无任何提示
- recommendation: 对齐同批次其他函数用 `git rev-parse --show-toplevel` 拼 repo-root 路径，或至少在 roadmap.md 确实不存在时输出区分性 stderr 提示
- closure_criteria: 路径定位方式对齐或加区分性提示 + 回归用例 + 全量测试通过
- source: review
- created_at: 2026-08-25
- task_id: TAG0023

### DEBT0021（RM-AG0032 roadmap.md 多行矛盾状态）
- category: management
- title: RM-AG0032 在 roadmap.md 现存 3 行（backlog/scheduled/done），P2 设计"新增一行"策略与 P4 判定算法"任一非done即阻断"存在潜在交互副作用
- priority: low
- evidence: ref `agate-workspace/roadmap/roadmap.md`（RM-AG0032 三行记录），note 引用 P4-review.md 原文："若未来任何人对 task_id=TAG0020 重跑 check-gate.py P8，会被这条已过时的 scheduled 行永久阻断，即便 done 事实已经记录在后面那行"
- impact: 实际触发概率低（TAG0020 是已发布历史任务，通常不会重跑 P8 gate），但属未被察觉的设计-实现交互副作用
- recommendation: 改为原地更新已有行状态列（而非追加新行），或调整算法为"同 RM_id+task_id 分组，组内任一行为done即视为已完成"
- closure_criteria: 主 Agent/后续任务决策采纳其中一种方案并落地 + 回归用例
- source: review
- created_at: 2026-08-25
- task_id: TAG0023

## debt_check 字段

`debt_check: reviewed`（本次新登记 DEBT0019/0020/0021，均为 low priority、非阻断，正文附条目 id 清单）

## 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P2-design.md`（packages 声明）
2. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P4-review.md`（3 条 INFORMATIONAL 原文）
3. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P7-consistency.md`
4. `{agate_root}/assets/templates/tech-debt-template.md`（登记格式）
5. `{project_root}/CHANGELOG.md`（现有条目风格参照，改动位置：文件顶部 `## [0.61.0]` 之前）
6. `{project_root}/README.md`（version badge，**不要在本阶段改**，由主 Agent bump-version 时统一处理）
7. `{agate_root}/phase-cards/P8-release.md`（本阶段卡片）

## 临时资源清单（供你确认后如实填写）

本任务全程未启动任何调试服务器/临时数据库/开发环境安装——4 个 P4 批次实现 + P5/P6 验证 + P7 一致性检查全部是静态代码修改 + pytest 本地运行 + 5 次真实 GitHub Actions CI 触发（远程资源，运行后自动释放，无需本地清理）。若你核实后发现有遗漏的本地临时资源，如实列出。

## 命令超时兜底

`timeout 30s python3 agate/scripts/check-debt.py {AGATE_WORKSPACE}/debt/tech-debt.md` 验证 3 条新登记债务 schema 合法。

## 产出

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P8-release.md`
- `{project_root}/CHANGELOG.md`（新增小节）
- `{AGATE_WORKSPACE}/debt/tech-debt.md`（追加 3 条 DEBT）

## 门槛

- P8-release.md 含 bump_type/debt_check/版本确认/CHANGELOG确认/临时资源清单
- CHANGELOG 新小节格式与既有条目风格一致
- 3 条 DEBT 通过 `check-debt.py` schema 校验
- 不执行任何 git 操作（commit/tag/bump-version 均由主 Agent 执行）

## 返回给我

只返回两行：① 产出文件路径列表；② 一句话摘要（bump_type + 3条DEBT登记，≤30字）。绝不返回文件全文。

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
