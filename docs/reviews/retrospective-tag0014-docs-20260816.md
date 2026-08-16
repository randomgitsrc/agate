# TAG0014 复盘 — agate 派发编排机制（v0.49.0）

> 任务：RM-AG0016（subagent 派发编排机制：工作量评估 + 五模式编排 + 并行规则统一，全阶段）
> 分支：feat/TAG0014-dispatch-orchestration → PR #144（普通 merge）→ v0.49.0
> 执行窗口：2026-08-16
> 参考 plan：agate-workspace/plans/agate-dispatch-orchestration-20260815.md（plan-eng-review 三轮评审 approved）

---

## 0. 事实基线

| 项 | 数据 |
|----|------|
| P1 BDD | 22 条（I1-I10 隐含需求 + BDD-1~22）|
| P6 验收 | 22/22 BDD PASS（每条有证据文件）|
| P7 一致性 | BLOCKER=0、DESIGN_GAP 2/2 REVIEWED、SCOPE+ 空集 |
| pytest | 780 passed（基线 768 + 新增 12）|
| consistency | 0 ERROR |
| 版本 | v0.48.0 → v0.49.0（bump minor）|
| P2 候选方案 | 6 个（3 处改动各 2）|

## 1. 做得好的

1. **approved plan 作为参考输入而非替代**：plan（三轮评审）提供了字段契约 + 6 Task 结构，但任务仍走完整 P0-P8——P1 独立产出 22 条 BDD、P2 独立设计（含候选方案 6 个），gate 全过。**验证了"有 plan ≠ 裁剪阶段"原则在 dogfooding 中成立**。
2. **字段契约一次落地**：`dispatch_plan:` frontmatter flow YAML + op 子进程读取 + JSON 输出 + 不入 schema（plan B3 结论）——P2 严格遵循 plan 契约，未返工。plan 评审的价值在此显现：B1/B2/B3 三轮发现的坑（TDD 不闭合/字段契约/schema 类型矛盾）在 P2 前就锁定。
3. **DESIGN_GAP 闭环真实有效**：P2 的 2 条 DESIGN_GAP（files_to_read YAML 引号、README badge 提前 bump）在 P4 声明 → P7 配对 REVIEWED → check-gate 通过。两条都是"主 Agent 在 P4 修复轮处理"——归因清晰，P7 转抄配对无遗漏。
4. **全阶段卡统一引用**：8 张阶段卡的"按包拆分并行"统一指向权威节，阶段特定约束（P5 端口/P6 证据并行）保留在卡片——没有在统一过程中误删约束。

## 2. 发现的问题

### 2.1 P2 DESIGN_GAP-1：files_to_read `why:` 值含冒号未加引号 → YAML 解析 ERROR（机制缺口）
- **现象**：P2-design.md files_to_read 块 `why:` 值含冒号标量未加引号 → consistency CHECK 1 YAML 解析 ERROR。
- **归因层面**：**agate 机制层**（非执行错误）——P2 卡片/architect 角色没有强制"YAML 标量含冒号须加引号"的写入规则，任何 architect 都可能踩。
- **改进措施**：P2 产出规格加一句"YAML 标量值含冒号（`: `）时须加引号"（落点：phase-cards/P2-design.md 产出规格节 + architect.md）。可复用：所有 frontmatter/flow YAML 写入处。

### 2.2 P4 README badge 提前 bump → CHECK 7 ERROR（执行错误，时机问题）
- **现象**：P4 修复轮把 README badge 改 v0.49.0（提前 bump），触发 CHECK 7（badge vs git tag）ERROR。
- **归因层面**：**执行错误**（非机制缺口）——协议 P8-release 已明确"bump 归 P8 与 tag 同 commit"，P4 不应提前改 badge。
- **改进措施**：非机制缺口，无需改协议。教训：P4/P5 阶段不碰 README badge（版本 bump 只在 P8）。可记入 P8-release 卡"常见错误"节。

### 2.3 orchestrator-log.md 缺失（机制缺口，本次复盘直接暴露）
- **现象**：TAG0014 任务目录**无 orchestrator-log.md**——主 Agent 的过程决策（派发依据/gate 判定理由）未落盘，只有 subagent 的 progress.md。
- **归因层面**：**agate 机制层**——orchestrator-log 在 state-machine.md L459-473 有定义（"必须记录的事件"），但**无强制力**（无 gate/无提醒），执行者可完全跳过。且定义里"不写思考过程"导致即使写了也缺决策依据。
- **改进措施**：RM-AG0020 的核心动因之一——orchestrator-log 扩展"决策 + 依据" + 阶段 checkpoint 落盘（L2 会话事实源）。本次复盘的事实依据因此不完整（无法重建主 Agent 各阶段判断的因果链），只能靠产出文件 + progress 推断。

### 2.4 复盘事实依据依赖平台 session（机制缺口，本次复盘暴露）
- **现象**：本复盘基于产出文件 + git log + progress 撰写——主 Agent/subagent 的 session 判断过程未落盘，若 session 被 compact，机理分析的事实源断。
- **归因层面**：**agate 机制层**——无"会话 checkpoint 落盘"机制（RM-AG0020 建议修复方向 5）。
- **改进措施**：时机前置——P8 完成时落盘 task-session-summary.md（趁 session 完整），复盘基于它写，不依赖平台导出。

## 3. 问题清单 + 改进措施（汇总）

| # | 问题 | 归因 | 措施落点 |
|---|------|------|---------|
| 2.1 | files_to_read `why:` 冒号未引号 → YAML ERROR | 机制缺口 | P2-design.md 产出规格 + architect.md 加"冒号须引号" |
| 2.2 | README badge 提前 bump → CHECK 7 ERROR | 执行错误 | P8-release.md 常见错误节记"P4/P5 不碰 badge" |
| 2.3 | orchestrator-log 缺失（无强制力）| 机制缺口 | RM-AG0020：扩展决策+依据 + 强制落盘 |
| 2.4 | 复盘事实依据依赖 session（无 checkpoint）| 机制缺口 | RM-AG0020：L2 会话 checkpoint + 时机前置 |

## 4. 亮点 + 可复用模式

1. **approved plan 的正确用法**（可固化）：plan 给"做什么/字段契约/实施顺序"，任务仍走 P0-P8 独立产出——"有 plan ≠ 裁剪"原则的 dogfooding 验证。
2. **DESIGN_GAP 配对流程**（已固化，保持）：P4 声明 → P7 转抄 + REVIEWED → gate 校验 count 配对——本次 2/2 无遗漏。
3. **YAML 标量引号纪律**（可固化进 P2 卡）：见问题 2.1。

## 5. 复盘机制触发核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 否（无 retry 超限）| — | | |
| PAUSED | 否 | — | | |
| PROD_TOUCHED | 否（纯文件系统+git 操作）| ✅ [PROD_NOT_TOUCHED] | | |
| SCOPE+ | 否（无新增隐含需求）| — | | |
| DESIGN_GAP | 是（P2 2 条）| ✅ P4 声明 + P7 REVIEWED 配对 | | |
| NEED_CONFIRM | 否 | — | | |
| gate 验证（每阶段）| 是 | ✅ P1-P8 每阶段 + commit hook 复核 | | |
| 阶段产出文件 | 是 | ✅ 全产出齐全 | | |
| .state.yaml phase 同步 | 是 | ✅ | | |
| 分阶段落盘 | 是 | ✅ 各阶段 progress 存在 | | |
| P6 evidence | 是（无 UI 无截图）| ✅ 22 BDD 各 1 证据 + 引用 | | |
| P2 候选方案 + 权衡 | 是 | ✅ 6 候选 + 权衡 | | |
| dispatch-context | 是 | ✅ 各阶段 + inject-card | | |
| pre-commit hook | 是 | ✅ 各 commit 触发 | | |
| CI backstop | 是 | ✅ 双矩阵全绿 | | |
| 技术债登记 | 是（复盘发现缺口）| ⚠️ 本复盘 2.1/2.3/2.4 为机制缺口，待登记 | 未登记=机制缺口 | RM-AG0020 已立（2026-08-16）|

## 6. 版本发布清单核对

- [x] pytest 780 passed + 0 consistency ERROR + ruff 通过
- [x] README badge + CHANGELOG [0.49.0]
- [x] UPGRADING v0.49.0 章节
- [x] `git tag v0.49.0 && git push`（CHECK 7 通过）
- [x] release PR 普通 merge（--no-ff），tag 为 main 祖先

---

> **事实依据说明（RM-AG0020 原则应用）**：本复盘基于 L1 仓库落盘（git log/产出文件/progress/consistency 输出）+ 任务产出推断。**L2 会话 checkpoint 缺失**（orchestrator-log 无强制力）——主 Agent 各阶段判断的因果链无法完整重建，是本复盘最大的事实依据局限，已登记为问题 2.3/2.4。L3 平台 session 导出未使用（补充层）。
