# agate 协议评审 — 基于 PeekView T044/T045 实战复盘 + 行为审计

> 评审日期：2026-07-01
> 评审类型：实战复盘 + 行为审计驱动
> 来源：
> - `~/oclab/peekview/docs/reviews/t044-t045-retrospective-20260701.md`（复盘）
> - `~/oclab/peekview/docs/reviews/t044-t045-behavioral-audit-20260701.md`（行为审计）
> 评审对象：agate v0.5.0 协议本体（commit `b160c99`）
> 修订：v5（吸收专家二次评审——R1 措辞澄清"已有规则 hook 化"、总结明确两类防线分野、补充实现顺序建议、加协议文档与脚本实现漂移风险观察）

---

## 评审背景

T045 的核心故障链（行为审计第 6 节「缺陷逃逸链」）：

```
P2 方案假设错误（CSS overflow:auto 下 display:block 不铺满）
  → P3 裁剪（无 TDD 设计验证）
    → P4 忠实实现错误方案
      → P5 发现页面空白未深究（确认偏差）
        → P6 subagent 写脚本但不跑（"写跑分离"模式缺陷）
          → P6 subagent progress 已标 NEED_CONFIRM 但 acceptance 写 PASS
            → P6 主 Agent 信任自评（C7 违规）
              → bug 流入"完成"状态 → 3h 后手动发现，5 轮修复
```

**7 个环节，0 个拦截成功**——系统性的防线失效。

### 故因分层

| 层次 | 问题 | 防线 |
|------|------|------|
| **执行层** | 主 Agent 违反 C7（接受自评）、P5 发现异常未深究（确认偏差） | 已有规则被违反 |
| **模板层** | P6 subagent 有 NEED_CONFIRM 但 acceptance 写 PASS | 模板结构 + 现有二值规则 |
| **gate 层** | gate 检查"产出物存在"不检查"产出物可信" | gate 设计哲学 |
| **裁剪层** | 裁剪理由是"省力偏好"而非"风险判断" | 裁剪决策过程 |

### 关键原则：backstop 必须用客观证据，不依赖自报文本

T045 的核心教训：**任何基于 subagent 自报文本的防线都可被同一 subagent 绕过**。subagent 在 progress.md 写了 `NEED_CONFIRM`，但在 acceptance.md 写了 `PASS 9/9`——acceptance.md 里根本没有 NEED_CONFIRM，hook 只读 acceptance.md 就不会触发。

因此，真正的 backstop 必须检查**客观证据**（文件大小、vision YAML 的 blocker_count、截图存在性），而不是检查 subagent 写的文本（PENDING 状态、NEED_CONFIRM 标记）。

---

## 评审发现

### R1: P6 证据从"形式合规"升级到"实质合规"——客观证据检查（Important）

**来源**：行为审计第 3 节「问题 1」+ 第 2 节「决策点 4」

**现状**：`check-p6-provenance.sh` 三道审计检查 P6-acceptance.md 的内容一致性——证据引用存在性、PASS 数 ≤ 证据数、BDD 总数对照。`check-p6-evidence.sh` 只检查"P6-evidence/ 非空 + BDD 行数 ≥ 1"。

**盲区**：T045 P6 subagent 没跑 Playwright、没截图、没 vision 验证，但写了 "9/9 BDD PASS" + 引用了证据路径 + 证据文件存在（空 png 或无关截图）。三道审计全过——**形式上合规，实质上 subagent 没跑浏览器**。

**为什么不用 PENDING 状态**：v3 曾提议 P6 acceptance 模板增加 PENDING_VERIFICATION 状态。但：
1. **与现有二值规则冲突**：`task-files.md:35` 明确"P1 每条 BDD 有实跑结果（**只允许 PASS 或 FAIL，不允许中间态**）"；`verifier.md:119` 重申此规则；`state-machine.md:118`："⚠️ 调整等中间态不合法"——T019 教训正是中间态导致逃逸
2. **可被 subagent 绕过**：subagent 在 acceptance.md 不写 NEED_CONFIRM 就行——T045 就是这么干的。hook 只读 acceptance.md，不读 progress.md
3. **自报文本防线不可靠**：任何基于 subagent 自报文本的防线都可被同一 subagent 绕过

**建议**：

a) **check-p6-evidence.sh 增加 UI 截图实质检查**（第一道防线，P1.7 在 P2.1 前触发）：
   - `ui_affected: true` 时，P6-evidence/screenshots/ 必须非空 + 每个截图文件大小 > 1KB（防空 png）
   - 客观证据检查——subagent 无法绕过（文件大小是文件系统级属性）

b) **check-p6-provenance.sh 将门槛表已有 UI vision 规则 hook 化**：
   - `dispatch-protocol.md:575` 门槛表**已明文写**"UI 条件须截图 + vision-analyst YAML 引用 + `summary.blocker_count → =0`"——规则一直存在，但只靠主 Agent 自觉执行，没 hook 强制
   - T045 的 vision YAML 规则在协议里躺了很久，主 Agent 跳过它零成本
   - hook 化：`ui_affected: true` 时，每条 UI 类 PASS 必须含 `(vision: vision-reports/*.yaml)` 引用 + YAML 文件存在 + `summary.blocker_count == 0`
   - 这不是"新增审计"，是"把规则从靠 Agent 自觉变成机器强制"——这正是 hardening 项目存在的全部理由

c) ~~PENDING_VERIFICATION 状态~~ → **否决**：与二值规则冲突（T019 教训）+ 可被 subagent 绕过

d) ~~截图 md5 去重~~ → **Phase 2**：vision YAML 审计已要求每条 UI PASS 有独立 vision 分析，边际收益有限

**优先级**：Important——T045 是 live 事故。首要防线是 C7（主 Agent 亲自跑），provenance 审计是 **C7 被违反时的 backstop**——必须用客观证据，不依赖自报文本

---

### R2: P5 冒烟检查 + P2 E2E 声明——互补而非互斥（Important）

**来源**：行为审计第 2 节「决策点 3」+ 第 5.2 节 + 第 7 节 P0#3

**现状**：P5 gate 只检查"测试通过 + 无 PROD_TOUCHED"。T045 P5 阶段主 Agent 用 Playwright 发现**页面空白**，但以"后端问题"为由绕过。P5 gate 全过。

**v3 的否决错误**：v3 引用审计 5.2 否决 P5 冒烟检查——"冒烟只能发现页面空白不能发现 zebra 不铺满"。但审计 5.2 原文同时说"如果页面完全空白（P5 观察到的情况），这个检查会发现"。**审计自己将 P5 冒烟列为 P0 优先级**。v3 否决了审计的最高优先级建议，否决理由不成立。

**正确做法**：P5 冒烟检查 + P2 E2E 声明**两者都做**，互补而非互斥。

**建议**：

a) **P2 gate 强制 UI 任务声明 E2E 命令**（拦在 P2）：
   - `ui_affected: true` 时，P2-design.md 的 `gate_commands.P5` 必须含至少一条 E2E/冒烟命令（hook 检查非空且含 `playwright`/`curl`/`e2e` 字样）
   - 防"P2 没规划 E2E"

b) **P5 冒烟检查保留但降级为 WARNING**（exit 2，不阻塞 commit）：
   - `check-gate.sh P5` 增加：`ui_affected: true` 时，检查 P5-test-results/e2e.md 存在 + 含 `status: passed`
   - `task-files.md:34` 已要求"UI 任务必须：Playwright 实跑结果 + 截图路径"——补 hook 检查
   - **降级为 WARNING 的理由**：冒烟检查是 self-authored（主 Agent 填 status），形式合规。但制造了"我考虑过冒烟"的摩擦力。与 R3 裁剪风险评估同理——nudge 不是 barrier
   - 防"P5 发现异常未深究"——虽然冒烟不能发现 zebra 不铺满，但能发现页面空白（审计 5.2 确认）

c) ~~gate 输出 WARNING 降级~~ → **否决**：过度工程，误杀风险高

**优先级**：Important——P5 是技术验证关，P2→P5 传递性盲区 + P5 冒烟缺失让 UI 回归逃逸

---

### R3: 裁剪是"省力偏好"而非"风险判断"（Important）

**来源**：行为审计第 3 节「问题 2」+ 复盘第 9 节

**现状**：T045 的裁剪理由每条都在说"为什么不需要"，没有一条说"跳过的风险是什么"。

**建议**：

a) **裁剪理由必须包含"跳过风险"评估**：
   - P1-requirements.md 裁剪说明格式改为：`裁剪 P{n}: {为什么不需要} | 跳过风险: {风险评估}`
   - `check-pruning.sh` 检查裁剪声明含"跳过风险:"字样
   - **局限性承认**：这是 form check（和 risk_level 同级），"跳过风险: 低"可以无脑填。但强制写一行风险评估制造了"我考虑过风险"的形式义务——nudge 不是 barrier。审计第 3 节的本质是认知偏差不是缺少表格字段，R3(a) 只提高"不思考就裁剪"的摩擦力，不改变"思考后仍选择省力"的行为

b) **P7 语义澄清**：
   - WORKFLOW.md / state-machine.md P7 描述加："P7 是'实现是否偏离 P2 设计'，不是'是否跨端'。跨端一致性是 P7 的子集，不是 P7 的全部。"

**优先级**：Important——裁剪决策过程缺陷是 P7/P8 被系统性裁剪的深层根因

---

### R4: P7 裁剪条件——文件数 > 5 不合理 + 条件未实现（Important）

**来源**：用户质疑 + 复盘第 8 节 + 行为审计第 3 节

**现状**：`state-machine.md:167` 文档了"裁剪 P7：需改动文件数 ≤ 5"。但 `check-pruning.sh` **从未实现** P7 的文件数检查。

**文件数 > 5 作为 P7 不可跳条件为什么不合理**：

1. **文件数衡量"散布度"不衡量"耦合度"**：T045 是 8 文件 3 组件共享 `.line` 样式——隐式耦合远超文件数反映的散布度。T044 是 14 文件但源码仅 2 个——文件数虚高（含 task docs + static）。1 个文件 3 处耦合改动比 6 个文件各改 1 行风险更高

2. **阈值 5 是武断的**：没有经验数据支撑

3. **文件数计算口径不明确**：git diff 总文件数？源码文件数？T044 的 14 文件含 task docs + static，只算源码是 2 个——差距 7 倍

**建议**：

a) **补实现已文档化的文件数条件**（bug fix，作为最低限指标保留）：
   - `check-pruning.sh` 增加 P7 检查：源码文件数 > 5 → 不可跳
   - 源码文件 = git diff 文件排除 `docs/tasks/`、`.state.yaml`、`*.md`（P{n}-*.md 等阶段产出文件）
   - 这是必要不充分条件——超过 5 文件时 P7 不可跳，但 ≤ 5 文件不代表可以跳

b) **加 shared_styles 维度**（self-declaration，与 risk_level 同级）：
   - P1 声明 `shared_styles: [...]` 或 `shared_interfaces: [...]` 时 → P7 不可跳
   - hook 检查声明字段存在性
   - **局限性承认**：hook 只能检查字段存在性，不能检查声明准确性。T045 的 analyst 完全可以不声明 shared_styles——此维度只能提高声明摩擦，T045 场景下不提供拦截。文件数 > 5 是客观的，shared_styles 是主观的——但两个维度叠加比单一文件数阈值更好

c) **P7 不可跳条件改为"源码文件数 > 5 OR 有 shared_styles 声明"**（a + b 合并）

d) ~~裁剪策略翻转默认~~ → **否决**：行为审计 5.1 反事实推演——P3 不保证能拦截（jsdom 不支持真实 CSS 布局）。翻转默认给小任务加开销但不保证收益

**优先级**：Important——文件数条件不合理 + 未实现是双重问题

---

### R5: P8 被系统性裁剪——裁剪无硬规则（Important）

**现状**：`check-pruning.sh` 没有 P8 的裁剪条件——P8 可以被任意裁剪。8/10 任务跳过。

**建议**：

a) **P8 裁剪需显式声明 `internal_only: true`**：
   - P1 需声明 `internal_only: true` + 理由才能裁剪 P8
   - hook 检查声明存在性
   - ~~git diff 路径硬编码~~ → **否决**：项目特定路径不可泛化

b) **P8 裁剪理由也必须含"跳过风险"评估**（与 R3a 统一）

c) ~~P8 两级制~~ → **否决**：当前 P8 gate 已足够轻量

**优先级**：Important——`internal_only: true` 声明机制 + 风险评估是可行改进

---

### R6: P2 已有 `minimal_validation` 机制未被执行（Minor / 项目侧）

**来源**：行为审计第 3 节「问题 4」+ 第 7 节 P1#6

**现状**：`architect.md:65` 已有 `minimal_validation` 字段——"若方案依赖浏览器行为/安全模型/外部系统行为，P2 必须做最小验证"（T019 教训）。`analyst.md:39` 有 `requires_minimal_validation` 字段与之配套。

**T045 的 P2 没有执行这个已有机制**——CSS `overflow:auto + display:block` 的交互正是"依赖浏览器行为"的场景，P2 应该做 `minimal_validation` 但没做。

**建议**：

a) **项目侧改进**：PeekView 的 orchestrator.md 或 architect 角色配置中，强调 `requires_minimal_validation: true` 时 P2 必须填 `minimal_validation` 块且 `result: confirmed`——这是已有机制的项目侧执行问题，不是 agate 协议缺口

b) **P2 设计增加"交互分析"节**（行为审计第 3 节问题 4）：列出各子方案之间的属性交互——这也是项目侧 architect 角色改进，非协议本体

**优先级**：Minor——已有机制未被执行，是项目侧执行改进

---

## 评审总结

| # | 发现 | 优先级 | 根因类型 | 建议（评审后保留） |
|---|------|--------|---------|-------------------|
| R1 | P6 证据"形式合规"≠"实质合规" | Important | gate 层 | (a) check-p6-evidence UI 截图 > 1KB + (b) provenance 审计 4 vision YAML |
| R2 | P5 冒烟 + P2 E2E 声明 | Important | gate 层 | (a) P2 gate 强制 UI 声明 E2E + (b) P5 冒烟降级 WARNING |
| R3 | 裁剪"省力偏好"而非"风险判断" | Important | 裁剪层 | (a) 裁剪理由含"跳过风险" + (b) P7 语义澄清 |
| R4 | P7 文件数 > 5 不合理 + 未实现 | Important | 裁剪层 + bug | (a) 补实现文件数检查 + (b) 加 shared_styles[标注局限] + (c) 条件合并 |
| R5 | P8 被系统性裁剪 | Important | 裁剪层 | (a) `internal_only: true` 声明 + (b) 风险评估 |
| R6 | P2 已有 minimal_validation 未执行 | Minor | 项目侧 | 项目侧执行改进，非协议本体 |

### 关键原则

**backstop 必须用客观证据，不依赖自报文本**。T045 的核心教训：subagent 在 progress.md 写了 NEED_CONFIRM，但在 acceptance.md 写了 PASS——任何基于 subagent 自报文本的防线（PENDING 状态、NEED_CONFIRM 标记）都可被同一 subagent 绕过。真正的 backstop 是 R1 的客观证据检查（文件大小、vision YAML blocker_count）。

### 两类防线的分野

T045 评审揭示了一个需要明说的结构性结论：**不同层的防护强度不同**。

| 防线类型 | 适用层 | 机制 | 强度 | 对应建议 |
|----------|--------|------|------|---------|
| **客观证据 barrier** | P6 验收 | 文件系统级属性（文件大小、YAML 值）、文件数 | 不可绕过——subagent 写完就固定 | R1(a)(b)、R4(a) |
| **自报 nudge** | 裁剪决策 | 声明字段存在性（跳过风险、shared_styles、internal_only） | 可绕过——subagent/analyst 控制文本 | R3(a)、R4(b)、R5(a) |

P6 验收层可以用客观证据做 barrier（文件大小、blocker_count），裁剪层只能用自报做 nudge（因为"风险"无客观度量）。**承认这个分野，比假装 R3/R5 提供了和 R1 同等强度的保护更诚实**。自报 nudge 的价值是"制造思考的形式义务"——强制写一行风险评估制造了"我考虑过风险"的摩擦力，但不改变"思考后仍选择省力"的行为。裁剪决策的根问题（认知偏差）在 hook 层无解。

### 实现顺序建议

R1/R2 实现前需先在 `task-files.md` 补格式约定：
- `P6-evidence/screenshots/` 目录约定（R1a 依赖）
- `P5-test-results/e2e.md` 格式（R2b 依赖，需含 `status: passed` 字段）

**先定协议格式、再写检查脚本**——这是 agate 已踩过的坑（check-p6-evidence 早期假设 `## BDD-NN` 格式但协议没定义，最后退化处理）。

**优先级排序**：
1. R4(a) 补实现文件数检查——纯 bug fix，修复一年未生效的规则
2. R1(a) 截图 > 1KB——最低成本堵住 T045 核心逃逸点
3. R1(b) vision YAML hook 化——需先确认 vision-analyst YAML 格式
4. R2 / R3 / R5——需先定模板格式

### 否决的建议

| 建议 | 否决理由 |
|------|---------|
| PENDING_VERIFICATION 状态 | 与二值规则冲突（T019 教训）+ 可被 subagent 绕过 |
| P7 裁剪默认翻转 | P3/P7 保留不保证能发现问题（jsdom 不支持真实 CSS 布局）|
| P8 两级制 | 当前 P8 gate 已足够轻量 |
| git diff 路径硬编码 | 项目特定路径不可泛化 |
| gate 输出 WARNING 降级 | 过度工程，误杀风险高 |
| md5 去重 | Phase 2，vision YAML 审计边际收益更高 |

### 附：协议文档与脚本实现的漂移风险

R4 揭示了一个信号：`state-machine.md:167` 文档了"裁剪 P7 需文件数 ≤ 5"，但 `check-pruning.sh` 从未实现——**一条规则在文档里躺了一年但从未生效**。P3-1 一致性脚本（check-protocol-consistency.py）检查文件引用和字段集，**检查不到"文档描述的逻辑是否在脚本里实现"**。

值得考虑给一致性检查加一个维度：扫描 `state-machine.md` 里所有"裁剪 P{n} 需……"的条件，核对 `check-pruning.sh` 是否都实现了。否则会有更多"躺在文档里但从未生效"的规则。
