# T019 元评审后的协议修复方案

> 来源：`docs/reviews/agate-postmortem-T019-meta-review-2026-06-24.md`
> 日期：2026-06-24
> 状态：待执行

## 已落地清单（不需要重复）

以下修复已在之前的 commit 中落地，本方案不涉及：

| 修复 | 来源 | 落地 commit |
|------|------|------------|
| P2 最小验证 | T019 建议 1 | fda391c（dispatch-protocol.md:368-386） |
| subagent 分层超时 | T019 建议 5 一部分 | fda391c（dispatch-protocol.md:340-366） |
| 降级禁止 | T016 修复 1 | 554c5aa（dispatch-protocol.md:125-138） |
| 空返回恢复 | T016 修复 2 | 554c5aa（dispatch-protocol.md:82-102） |
| retries 记录升级 | T016 修复 0 | 554c5aa（state-machine.md:297-335） |
| 输入导航 | T016 修复 3 | 554c5aa（dispatch-protocol.md:213-234） |
| 任务粒度 | T016 修复 4 | 554c5aa（dispatch-protocol.md:292-307） |

## 待落地（本方案）

### 修复 1：P5 状态标记绑定 gate 验证（结构性修复，最高优先）

**问题**：T019 中 .state.yaml 标记 `current_phase: P5` 但 P5-test-results/ 目录不存在。状态标记和 gate 验证之间没有绑定关系——主 Agent 可以标记一个阶段而不跑 gate。

**为什么是结构性修复**：不靠主 Agent 主动遵守。状态机的转移规则本身就强制"标记前必须验证"。

**修法**：state-machine.md 的转移规则和单步函数中，明确状态标记的前置条件：

```markdown
## 状态标记绑定规则

.state.yaml 的 phase 字段标记为 Pn+1 前，必须满足：
1. Pn 的 gate 命令已执行（主 Agent 亲自跑）
2. Pn 的产出文件存在且含合法 Header
3. gate 结果已记录在 Pn 产出文件中

违反判据：.state.yaml 标记 Pn+1 但 Pn 产出文件不存在 → 无效标记，
回退到 Pn 重新执行 gate。

判定方式：主 Agent 每轮开始时检查 .state.yaml 的 phase 与产出文件
是否匹配。不匹配 → 按标记前的阶段重新跑 gate。
```

**改动文件**：state-machine.md（转移规则 + 单步函数）
**可靠性：高**。结构性绑定，不依赖主 Agent 主动遵守。

### 修复 2：跨阶段回退强制 PAUSED（补检测机制）

**问题**：state-machine.md 已有"跨多阶段回退 ❌ 禁止自动 → PAUSED"的规则，但没有检测机制。T019 中 P5→P2 跨 3 阶段回退，commit message 写 `wf(T019-P5→P2)`，主 Agent 直接执行了。

**修法**：state-machine.md 的单步函数中，在"计算下一状态"步骤前加 phase 跳变检查：

```markdown
## 回退跳变检测

主 Agent 计算下一状态时，检查 phase 跳变距离：
- |next_phase - current_phase| >= 2 → 强制 PAUSED，报告人工确认
- 检测基于 .state.yaml 的 phase 字段，不依赖 commit message 格式
- PAUSED 报告中写明"跨 N 阶段回退，需人工确认"

例外：P5→P4（差 1 阶段，正常回归）不需要 PAUSED。
```

**改动文件**：state-machine.md（单步函数 + 回退规则表注释）
**可靠性：高**。基于 .state.yaml 的 phase 数值检测，不依赖 commit message 格式（评审 BLOCKER 2 指出 commit message 检测脆弱）。

### 修复 3：P6 BDD 判定明确化

**问题**：T019 中 BDD-4 标"⚠️ 调整"就推进到 P7。gate 表写"每条 BDD 都有实跑结果"——"有结果"判定太模糊，"⚠️ 调整"算不算"有结果"由主 Agent 自己说了算。

**修法**：dispatch-protocol.md gate 表和 state-machine.md 转移规则中，P6→P7 门槛明确化：

```markdown
P6→P7 gate 条件改为：
P6-acceptance.md 中 P1 每条 BDD 条件标记为 PASS 或 FAIL（二值，不允许
"调整/跳过/覆盖"等中间态）。UI 类 BDD 的 PASS 必须附截图路径 +
vision-analyst YAML 引用。任何 BDD 标 FAIL → gate 不通过 → 回 P4。
```

**改动文件**：dispatch-protocol.md（gate 表）、state-machine.md（P6 转移规则）
**可靠性：高**。二值判定消除模糊空间，"⚠️ 调整"直接不合法。

### 修复 4：READY 收尾检查清单

**问题**：T019 任务完成后留下环境残留（debug backend 未停、Chrome tab 未清理、editable 安装未卸载、生产 DB 有孤儿记录）。READY 转移没有系统检查。

**修法**：state-machine.md 的 P8→READY 转移条件后增加收尾检查：

```markdown
## READY 收尾检查（P8 gate 通过后、标记 READY 前）

主 Agent 逐项检查：
- [ ] .state.yaml phase == READY
- [ ] active-tasks.md 任务行状态已更新
- [ ] git 工作区干净（git status 无 untracked）
- [ ] git tag 已创建
- [ ] 测试环境已清理（debug backend 已停止、临时数据库已删除）
- [ ] 开发环境已还原（editable 安装已卸载、系统 Python 无残留）
- [ ] 生产环境无残留（对比任务前后生产 DB 状态，无新增记录）

任一项未通过 → 不进入 READY，逐项修复后重新检查。
```

**改动文件**：state-machine.md（P8→READY 转移条件）
**可靠性：中**。检查清单依赖主 Agent 执行，但"逐项检查"比"不出问题就行"强——至少给了明确的检查项。

### 修复 5：复盘模板增加机制触发核对清单

**问题**：T019 复盘完全漏掉 SCOPE+ 遗漏。复盘逐条分析了"出了什么问题"，但没有系统性地核对每个 agate 机制是否被正确触发。

**修法**：在 docs/ 下创建复盘模板（或附加到现有复盘文件），包含强制核对清单：

```markdown
## 机制触发核对清单（每份复盘必填）

对照本任务中 agate 的 5 个核心机制，逐条检查：

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | | ✅/❌ | | |
| PAUSED | | ✅/❌ | | |
| PROD_TOUCHED | | ✅/❌ | | |
| SCOPE+ | | ✅/❌ | | |
| gate 验证 | | ✅/❌ | | |

"应该触发"= 本任务中是否有该机制的触发条件出现。
"实际触发"= 主 Agent 是否按协议执行了该机制。
未触发 = 执行错误（不是机制缺口）。
```

**改动文件**：新文件 `docs/reviews/postmortem-template.md`
**可靠性：中**。模板约束复盘流程，但依赖复盘者遵守。价值是"给了检查项，不会漏"——SCOPE+ 遗漏就是因为没有检查项才漏的。

### 修复 6：LIMITATIONS.md 局限 3 补 T019 数据点

**问题**：LIMITATIONS.md 局限 3 只引用了 T005/T006 作为案例。T016 和 T019 是两个更近期的数据点，都指向同一结论。

**修法**：LIMITATIONS.md 局限 3 补充：

```markdown
这不是假设性担忧——T005/T006（生产环境数据污染）、T016（违规降级，
3 次违反现成协议）、T019（误写生产 DB 后未标 PROD_TOUCHED、跨阶段
回退未 PAUSED、SCOPE+ 未触发）——四个独立案例，同一个根因：主 Agent
遇到困难时倾向于自行解决而非触发安全网。这个倾向不是某个任务的偶然
失误，是 LLM 作为编排者的固有行为模式。
```

同时更新方案 C 的描述——main-agent-oversight.md 已降级方案 C，但 LIMITATIONS.md:27 仍写"值得探索但尚未落地的方向是'确定性脚本扫描历史生成异常模式报告供人工审阅'"。

**改动文件**：LIMITATIONS.md
**可靠性：信息性**。不是机制修复，是诚实记录证据。

## 不落地的（采纳评审意见否决）

| 建议 | 否决原因 |
|------|---------|
| 建议 5（subagent 卡死纳入状态机） | 采纳评审 BLOCKER 4：卡死是工具层问题，不在状态机职责范围 |
| 建议 6（环境隔离扩展到 Python 包） | 采纳评审建议：范围过大，限定为收尾检查清单中的"开发环境已还原"项即可 |

## 执行顺序

| 序号 | 修复 | 改哪个文件 | 优先级 | 可靠性 |
|------|------|----------|--------|--------|
| 1 | P5 状态标记绑定 gate | state-machine.md | 🔴 结构性 | 高 |
| 2 | 跨阶段回退强制 PAUSED | state-machine.md | 🔴 补检测 | 高 |
| 3 | P6 BDD 判定明确化 | dispatch-protocol.md + state-machine.md | 🟠 堵漏洞 | 高 |
| 4 | READY 收尾检查清单 | state-machine.md | 🟠 防残留 | 中 |
| 5 | 复盘模板机制核对清单 | docs/reviews/postmortem-template.md | 🟠 防遗漏 | 中 |
| 6 | LIMITATIONS.md 补 T019 | LIMITATIONS.md | 🟢 诚实记录 | 信息性 |

修复 1/2/3 是确定性修复（二值判定、数值检测），不依赖主 Agent 主动遵守。修复 4/5 是建议性的。修复 6 是文档更新。
