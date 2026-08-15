# 复盘总结：agate 三任务批次（TAG0001-TAG0003，v0.40.2 → v0.43.0）

> **复盘范围**：HANDOFF-TAG-TASKS.md 交接的三个 agate 协议自身改造任务——TAG0003（工作区架构）、TAG0002（重构一等任务）、TAG0001（技术债登记闭环），在 worktree `dev/workspace` 分支上 P1-P8 全流程执行，最终 PR #121 普通 merge 回 main，`~/.agate` 升级到 v0.43.0。
>
> **证据来源（两条独立轨道，交叉印证）**：
> 1. git 记录（commit/tag/P0-brief 历史）+ 三任务 P1-P8 全部产出文件（含 review 记录、retry 记录、gate 结果、P6 验收证据、P8-release.md）。
> 2. 本次 opencode 主会话（`ses_00a830d5affeqmWCsrwS6i6SYW`，534 条 message / 2254 个 part，2026-08-12 18:20 → 2026-08-13 05:57）原始 session 记录：14 条用户原始指令、50 次 subagent 派发（含各阶段时间戳）、338 次 bash 调用、全部工具事件。复盘结论均标注来源。
>
> **复盘方法**：按 T001 复盘惯例，从技术 / 管理 / agate 协议自身三个维度归因，每条结论标注证据来源。不粉饰、不把成功归因于"流程好"——流程好的部分说清好在哪里，出错的部分找出结构性原因。

---

## 一、总体结果

| 任务 | 版本 | wf commit 数 | review 轮次（派发次数） | 发现的真实缺陷 |
|------|------|-------------|------------------------|----------------|
| TAG0003 工作区架构 | v0.41.0 | 10 | P1 复审 1 + P4 review 2（评审→修复→复审） | 迁移工具自动 commit 被自身 hook 静默拦截（F1） |
| TAG0002 重构一等任务 | v0.42.0 | 10 | P1 复审 1 + P4 review 5（评审→修复→复审→docfix→三审+重派） | change_type 正文回退误判缺省任务（BLOCKER） |
| TAG0001 技术债闭环 | v0.43.0 | 10（+1 fix commit） | P1 复审 1 + P4 review 1 + P5 修复 1 | serialize_evidence YAML int 边界（P5）+ CI 一致性漏检（P8 后） |

三个任务全部 P1-P8 走完、全 gate 通过、验收全 PASS，最终以普通 merge（--no-ff）合入 main。**从结果看是成功的**——但复盘的意义不在确认成功，而在找出"哪些问题被 gate 拦住了、哪些问题靠 gate 之外才暴露"。

---

## 二、时间线（session 原始记录校准）

> 本节时间均来自本次 opencode 会话原始记录（part 时间戳）+ git commit 时间，非转述。

| 时间 | 事件 | 证据 |
|------|------|------|
| 08-12 14:00-17:55 | **P0 立项**（TAG0001 14:00、TAG0002 14:35、TAG0003 17:55 merge）——发生在本次执行 session 之前 | git commit 583dac6/6795950/b0e3b91 |
| 08-12 18:20 | 本次会话开始；用户指令"先掌握信息、查看 HANDOFF-TAG-TASKS.md" | session 首条 user 消息 |
| 08-12 18:23 | 用户指令"依据 agate v0.40.2 实施 TAG0003"；TAG0003 P1 启动 | user 消息 + 首派 18:24 |
| 18:24-20:26 | TAG0003 P1-P7（analyst→review→修订→复审→architect→plan-eng-review→test-designer→3 并行 implementer→fix→review→review-fix→复审→verifier→verifier→consistency） | 50 次派发记录 |
| 20:26 | TAG0003 P8 releaser 产出，**建议 major v2.0.0**（WORKFLOW 版本策略 + UPGRADING 已写 v2.0.0 节） | P8-release.md + 派发记录 |
| **20:30** | **用户决策"不用2.0 你bump小版本号就行"** → TAG0003 改 minor v0.41.0 | user 消息 |
| 20:40 | TAG0003 READY + 本地 tag v0.41.0 | bash tag 事件 |
| **20:55** | **用户质疑"任务还没做完是不是不适合现在pr？"** → 确认不 PR、先 tag 再继续 | user 消息 |
| **20:56** | **用户"先tag 再继续推进？"** → 确认本地 tag 后推进 TAG0002 | user 消息 |
| 20:57-22:51 | TAG0002 P1-P8（P1 复审 1 + P4 review 5 轮：评审 21:46→review-fix 21:59→复审 22:08→docfix 22:16→三审 22:17→三审重派 22:25） | 派发记录 |
| 22:51 | TAG0002 READY + 本地 tag v0.42.0 | bash tag 事件 |
| **22:56** | **用户"继续。这个 brief 建立的比较早，且已经完成了 tag0003、tag0002，如果 tag0001 任务 p0 写的有偏差，应该修改到最新"** | user 消息 |
| 22:57 | TAG0001 P1 analyst 首派（**随后被用户打断**——tech-debt 归属讨论） | 派发记录 ses_00985b2 |
| **23:00-23:13** | **tech-debt.md 归属讨论**（4 轮用户对话：23:00"放 agents 目录合理吗"→23:02"继续？"→23:07"谁产出、什么内容、目录如何设计"→23:10"接受单独 debt/ 目录，但就这一个文件？"→23:13"确认，这是新问题"） | 4 条 user 消息 |
| 23:13 | 用户确认"接受单独 debt/ 目录" + "如果 tag0003 的设计与本次不符合，本次应该解决，但这算新问题" → P0-brief 更新 + **P1 analyst 重派**（ses_009765a4） | user 消息 + 派发记录 |
| 23:21-01:16 | TAG0001 P1-P8（含 P5 verifier 发现 serialize_evidence bug → implementer-fix 00:53） | 派发记录 |
| 01:16 | TAG0001 READY + 本地 tag v0.43.0 | bash tag 事件 |
| 04:13 | 用户"可以" → 发起 merge：push tags → git-to-pr 建 PR #121 | user 消息 |
| 04:15 | **CI 复现本地漏检**：一致性检查器扫描任务产出 10 ERROR（本地因 .worktrees 过滤 0 ERROR） | CI 日志 |
| 04:22 | 修复 commit ca90a30（NARRATIVE_DIRS 加 docs/tasks/ + YAML 引号） | git commit |
| 04:25 | PR #121 普通 merge（--no-ff），三 tag 均成 main 祖先 | gh pr view + git log |
| 05:53 | 用户要求写复盘 + 交接报告 | user 消息 |
| 05:56 | 用户要求提取 session 原始记录修正总结 | user 消息 |

---

## 三、技术原因

### 3.1 真实缺陷（被 gate 拦住的，都修对了）

**D1. 迁移工具自动 commit 被自身 hook 静默拦截（TAG0003，P4 review 发现）**

- **现象**：`agate-migrate-workspace.sh` 迁移完成后用裸 `git commit` 自动提交 rename，被项目自身 pre-commit hook（dispatch-context 卡片 hash 校验）拦截，`|| true` 吞掉 exit 1，工具照常打印"迁移完成"并 exit 0——**BDD-8（git 历史可追溯）静默不满足，用户被误导**。
- **根因**：迁移工具用裸 `git commit`（不跳过 hook、不限 pathspec、失败不检测），与"dogfooding 项目自身装有 agate hook"这一必然现实冲突。既有测试（MW.3）的 fixture 未安装 hook，无法捕获该路径。
- **修复**：`git -c core.hooksPath=/dev/null` + pathspec 限定 + 失败不再吞（显式报错 + exit 1）+ MW.9 带 hook fixture 回归测试。
- **证据**：P4-review.md F1 实证复现（fixture /tmp/opencode/migtest3/repo）。

**D2. change_type 正文回退误判缺省任务（TAG0002，P4 review 五轮迭代发现）**

- **现象**：`agate-md-field-get.py` 的 `change_type` 正文正则回退 `change_type:\s*(\S+)` 全文扫描，功能任务（frontmatter 无 change_type）只要 P1 正文出现 `change_type: refactor` 字样（散文提及/文档说明）就被误判为 refactor → P6 gate 误拦 + CI 误跳 check-tdd-red。**违反 BDD-2（未声明 change_type 的任务验收行为与改造前完全一致）**。
- **根因**：`_regex_fallback` 全文扫描不限于 frontmatter，`\S+` 对任意值匹配；而 change_type 是**新增**字段（正文旧格式从未有），与 risk_level（有旧正文格式需回退）不同——无向后兼容需求却套用了回退模式。
- **修复**：change_type 改 frontmatter-only（NO_FALLBACK_STRING_FIELDS）+ 4 条回归用例（正文提及不误判）。
- **证据**：P4-review.md §2.1 BLOCKER 实测 4 场景 + 五轮迭代记录（评审→修复→复审→docfix→三审）。

**D3. serialize_evidence YAML int 边界（TAG0001，P5 verifier 发现）**

- **现象**：`agate-debt-check.py::serialize_evidence` 对全数字值（如 commit 哈希 `023b28b`）YAML 解析为 int，round-trip 后与原始 fixture 不一致 → `test_bdd_15` 偶发红（1/4 全量运行）。
- **根因**：全数字标量被 YAML safe_load 解析为 int，序列化时未保持字符串语义。
- **修复**：serialize_evidence 对 int 归一 str（isinstance 检查 + str()）。
- **证据**：P5-test-results/unit.md §2 完整诊断 + 修复后 5 轮验证。

**D4. 一致性检查器 CI 漏检任务产出（P8 后，CI 复现）**

- **现象**：本地 `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR，CI 里 10 ERROR（YAML 解析错误 + 9 个引用不存在文件）。
- **根因**：TAG0003 工作区迁移后 `PATH_IGNORE_SUBSTRINGS` 不再忽略 `docs/tasks/`，但任务产出文件（P0-P8 阶段文档）含示例引用/归档路径/已修复缺陷的叙事引用；本地因 worktree 路径含 `.worktrees` 被 `iter_md_files` 过滤而漏检，CI 干净 checkout 不包含该路径 → 误扫任务产出。
- **修复**：`NARRATIVE_DIRS` 加 `docs/tasks/`（任务产出 = 编排状态，同 docs/plans|reviews 宽松待遇）+ 修 P1-requirements YAML 引号 bug。
- **证据**：干净 checkout 复现（/tmp/opencode/agate-conscheck）+ 修复后 0 ERROR 仅 48 WARNING。

### 3.2 技术教训

1. **"本地全绿 ≠ CI 全绿"**：本地 worktree 的 `.worktrees` 路径过滤会掩盖真实问题。D4 是结构性的——本地与 CI 的扫描范围不同。**教训：协议自身改造任务，P8 前必须在干净 checkout 上跑一次全量验证**（或 CI 兜底后检查 consistency job）。
2. **dogfooding 场景的"自身 hook 冲突"是必然现实**：D1 中迁移工具自动 commit 触发项目自身 hook——凡"协议工具要操作 git"的设计，必须显式考虑 `core.hooksPath`/`--no-verify`/pathspec。这不是偶发，是 dogfooding 的结构性约束。
3. **新增字段 ≠ 套用既有回退模式**：D2 中 change_type 是新增字段，却套用了 risk_level 的正文回退模式——`_regex_fallback` 的全文扫描对"正文会提及该字段名"的协议文档天然误判。**教训：新增机器字段若无历史正文格式，一律 frontmatter-only**。
4. **YAML 边界在"全数字 + 引号混用"两个方向**：D3（int 哈希）+ D4 附属（`retreat: 提交` 未引号）——协议文档的 YAML 块极易踩"冒号+空格""全数字 int""引号未闭合"三类坑。**教训：产出 YAML 块时对含冒号/数字的值一律加引号，schema 校验器对 int/str 边界显式处理**。

---

## 四、管理原因

### 4.1 做得好的

1. **版本里程碑策略清晰**：用户决策 minor bump（不走 major 2.0）+ 每任务一个版本（v0.41/0.42/0.43）→ CHANGELOG 天然分段、tag 可追溯、最终一次 merge。避免了"三个任务挤一个版本"的 CHANGELOG 合并痛苦。**关键转折点：TAG0003 P8 releaser 建议 major v2.0.0（有 WORKFLOW 版本策略 + UPGRADING 已写 v2.0.0 节支撑），但用户拍板走小版本**——版本语义与用户意志冲突时，用户是最终决策者，releaser 的建议如实呈现但被覆盖。
2. **"先 tag 再继续"的节奏控制**：TAG0003 完成后用户主动质疑"任务还没做完不适合 PR"，确认三任务是一个整体交付、逐任务打本地 tag、最后一次性 merge——避免了对 main 的中间态发布。**用户对"什么时候 merge"的判断比协议默认的"每任务发布"更贴合实际**。
3. **范围外问题及时升级决策**：tech-debt.md 归属（agents/ vs debt/）在 P1 前发现并升级用户决策（23:00-23:13 四轮对话），而不是 P4 实现时才发现改。用户拍板"独立 debt/ 目录"，同时认识到这是 TAG0003 已验收规范的修正（新发现问题）。
4. **三任务顺序合理**：TAG0003（容器）→ TAG0002（出口）→ TAG0001（记录）——下游任务天然基于上游成果，无返工。

### 4.2 做得不好的 / 可改进的

1. **TAG0001 的 P0-brief 建立在较早状态**：P0-brief 在 14:00（TAG0003/TAG0002 完成前）写好，其中 tech-debt.md 路径（`docs/agents/`）在 TAG0003 落地后已过时。**22:56 用户主动提示"P0 写的有偏差应该修改到最新"才被发现**。**教训：跨任务批次启动前，P0-brief 必须与最新协议状态核对**——本次靠用户提示而非流程强制。
2. **TAG0003 的 agents/ 归类是粗略决策**：把 tech-debt 塞进 agents/（agent 知识目录）是当时"凑 8 子目录"的归类，与 tech-debt 的"项目状态记录"本质不符。**教训：目录/命名空间的归类决策应在 P1 就做语义审查，而不是等下游任务发现再修正**（虽然本次修正代价可控）。
3. **CI 一致性漏检未被 P8 前置发现**：D4 在 PR 后 CI 才暴露——如果 P8 前在干净 checkout 跑一次 consistency，可在 merge 前发现。**教训：发布前置检查清单应含"干净 checkout 全量验证"**。
4. **TAG0001 P1 analyst 首派浪费**：22:57 首派 analyst 后，用户 23:00 开始 tech-debt 归属讨论（23:00-23:13），首派产出被取消/重派。**如果 P0-brief 先与用户对齐目录归属再启动 P1，可避免一次派发**——但当时的顺序是"用户先提示 P0 有偏差→我重审→派 analyst→用户深入讨论归属"，属于用户驱动的自然迭代，代价小（1 次派发）可接受。

---

## 五、agate 协议自身原因（agate 的机制哪些有效、哪些有缺口）

### 5.1 有效的机制（被验证）

1. **独立评审发现真实缺陷**：三任务的 P1 requirements-review 各发现 1 个阻塞项（TAG0003 归档 BDD 缺失、TAG0002 P3 回归 BDD 缺失、TAG0001 需求覆盖）；P4 review 发现 D1/D2 两个真实 bug。**独立 subagent + 实质锚点要求（非裸 approved）确实拦截了"假完成"**。
2. **do→review 迭代循环 + retry 预算**：TAG0002 P4 review 五轮（BLOCKER→文档残留→approved，含一次空返回重派）走完整迭代，无降级、无绕过。retry 记录（quality/empty_return）真实反映过程。
3. **external-output-gate 有效**：P5 verifier 发现 D3（YAML int 边界）——**测试执行是外部输出，主 Agent 验 gate 时能发现真实缺陷**，不是自写文件的自我确认。
4. **P6 provenance 审计**：三任务验收全 PASS 且审计 0——证据-结论对应机制工作正常。
5. **P8 版本决策流程**：releaser 只产出建议（含理由与锚点），主 Agent + 用户决策，subagent 不执行 commit/tag——版本决策与执行分离有效（本次 v2.0.0 建议被用户否决走 v0.41.0，流程无冲突）。

### 5.2 机制缺口（协议本身的问题）

1. **一致性检查器对"任务产出"的扫描范围缺口（最严重）**：D4 的根因是 `check-protocol-consistency.py` 的 `iter_md_files` 用 `root.rglob("*.md")` 扫描全部 .md（含任务产出），`NARRATIVE_DIRS` 只豁免 docs/plans|reviews 等，未含任务目录。**本地 `.worktrees` 过滤与 CI 行为不一致**——这是 LIMITATIONS 局限 3（自写文件 gate 弱保证）的具体形态：本地能过、CI 不能过。**修复已落地，但值得反思：为什么 TAG0003 工作区迁移时没同步适配一致性检查器的扫描范围？**——因为当时本地跑 0 ERROR（被 .worktrees 过滤掩盖），没有在干净 checkout 验证。
2. **发布前置检查无"干净 checkout 验证"步骤**：P8 卡片列了 P5 重跑/consistency/shellcheck/git log 对照，但都在 worktree 内跑——对 dogfooding 任务（改造协议自身）来说，本地过滤可能掩盖问题。**建议 P8 增加"干净 checkout 或 CI 兜底确认 consistency"步骤**。
3. **`change_type` 字段设计本可更早避免 D2**：如果 P1/P2 对"新增机器字段的读取通道"做语义审查（是否有历史正文格式？），会发现 change_type 无需回退——但协议没有强制这一审查，靠 review 五轮兜底。**属于 review 兜底成功、设计预防缺位的组合**。
4. **worktree 开发模式的本地/CI 环境差异**：worktree 的 `.worktrees` 路径过滤、`~/.agate` 软链指向主 checkout、CI 里软链不存在（load.bash 反推）——这些差异在协议里部分文档化（AGENTS.md），但**没有形成"dogfooding 任务发布前必须在 CI 等价环境验证"的强制步骤**。

---

## 六、对协议的建议（后续任务可落地）

| # | 建议 | 来源 | 优先级 |
|---|------|------|--------|
| 1 | 一致性检查器 `NARRATIVE_DIRS` 已加 `docs/tasks/`（本次已修） | D4 | 已落地 |
| 2 | P8 卡片增加"干净 checkout 或 CI 兜底确认 consistency"步骤（dogfooding 任务） | D4 | 高 |
| 3 | 新增机器字段的读取通道语义审查：无历史正文格式 → frontmatter-only（可写入 architect 角色） | D2 | 中 |
| 4 | 协议工具操作 git 时显式考虑 hooksPath/pathspec（可写入 implementer 角色提示） | D1 | 中 |
| 5 | 跨任务批次启动前，P0-brief 与最新协议状态核对（**本次靠用户提示，流程未强制**） | M2 | 中 |
| 6 | 目录归类决策在 P1 做语义审查（agents/ vs 独立目录） | M3 | 低 |

---

## 七、一句话总结

三任务批次成功交付（v0.40.2 → v0.43.0，PR #121 普通 merge，`~/.agate` 已升级），**四个真实缺陷（D1-D4）全部被 gate/review/CI 拦下并修复**；三个关键管理转折（版本走小版本、先 tag 再继续、debt/ 独立目录）都来自**用户的主动决策**而非协议默认——协议流程负责"拦缺陷"，用户负责"定方向"，二者配合良好。最重要的教训是 D4——**本地 worktree 的路径过滤会掩盖一致性检查的真实问题，dogfooding 任务发布前必须在 CI 等价环境验证**——这与 T001 复盘的"本地全绿 ≠ 机制有效"一脉相承，是 LIMITATIONS 局限 3 在协议自身改造场景下的又一次实证。
