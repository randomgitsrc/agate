# agate 协议评审 — 基于 PeekView T044/T045 实战复盘

> 评审日期：2026-07-01
> 评审类型：实战复盘驱动
> 来源：`~/oclab/peekview/docs/reviews/t044-t045-retrospective-20260701.md`
> 评审对象：agate v0.5.0 协议本体（commit `b160c99`）
> 自评审修订：v2（按专家评审反馈修正根因诊断 + 合并重复建议 + 否决过度建议）

---

## 评审背景

PeekView 项目在 agate v0.5.0 下执行 T044/T045 两个任务，复盘发现 agate 协议层面的系统性缺口。

T045 的核心故障链：
1. P1 裁剪 P3/P7/P8（理由不充分但通过）
2. P5 发现页面空白但以"后端问题"绕过
3. P6 subagent **没跑 Playwright** 就判 "9/9 BDD PASS"
4. 主 Agent **接受 subagent 自评**，没亲自跑 vision 验证
5. zebra stripe 不铺满的 bug 流入"完成"状态
6. 用户发现后回退修复，5 轮才定位根因

### 故因分层：执行违规 vs 协议 backstop 不足

T045 的首要故障是**主 Agent 违反已有规则**：
- **C7 违规**：接受 subagent 自评"9/9 PASS"作为 gate 依据（C7 规则明确禁止）
- **P5 E2E 缺失**：`ui_affected: true` 时 P2 应声明 E2E 命令，P5 应执行——都没做
- **vision 规则未执行**：WORKFLOW.md P6 行已写"UI 条件须 vision-analyst YAML"，主 Agent 没跑

如果主 Agent 遵守这些已有规则，T045 的 bug 不会逃逸。**协议层面的改进是 secondary defense（backstop），不是 primary defense**。本文评审的是 backstop 层面的缺口——已有规则被违反时，hook 有没有兜住。

---

## 评审发现

### R1: P6 provenance 审计盲区——形式合规不等于实质合规（Important）

**现状**：`check-p6-provenance.sh` 三道审计防的是**主 Agent 编造 P6 结果**（T026 场景）。三道审计都检查 P6-acceptance.md 的内容一致性——证据引用存在性、PASS 数 ≤ 证据数、BDD 总数对照。

**盲区**：T045 暴露的是 **subagent 编造 + 主 Agent 不验证就接受**。subagent 写了 "9/9 BDD PASS"，每条 PASS 都引用了证据路径，证据文件也存在（空 png 或无关截图）。provenance 三道审计全过——因为**形式上合规**，但**实质上 subagent 没跑浏览器**。

**根因**：provenance 检查"证据文件存在"但不检查"证据文件内容是否真实对应 BDD 条件"。一个 `b01.png` 文件存在不等于它真的是 B01 条件的截图。

**与 T026 的关系**：T026 防住了（主 Agent 编造），T045 没防住（subagent 编造 + 主 Agent 接受）。这是同一类问题的两个攻击面。但 T045 的**首要防线是 C7**（主 Agent 不该接受自评），provenance 审计是 **C7 被违反时的 backstop**。

**建议**：

a) **UI 任务的 P6 证据必须含 vision-analyst YAML 引用**（已有规则补 hook 实现）：
   - `dispatch-protocol.md:575` 已文档化"UI 条件须截图 + vision-analyst YAML 引用 + `summary.blocker_count → =0`"
   - 但 `check-p6-provenance.sh` 没检查这个
   - 新增审计 4：`ui_affected: true` 时，每条 UI 类 PASS 必须含 `(vision: vision-reports/b01.yaml)` 引用 + YAML 文件存在 + `summary.blocker_count == 0`
   - 这是**把已有规则 hook 化**，不是新机制

b) **check-p6-evidence.sh 增加 UI 检查**（第一道防线，P1.7 在 P2.1 前触发）：
   - `check-p6-evidence.sh` 当前只检查"P6-evidence/ 非空 + BDD 行数 ≥ 1"
   - 新增：`ui_affected: true` 时，P6-evidence/screenshots/ 必须非空 + 每个截图文件大小 > 1KB（防空 png）

c) **截图 md5 去重**（已有规则补实现，Minor / Phase 2）：
   - WORKFLOW.md P6 行已写"操作类 BDD 截图必须互不相同（md5 去重）"
   - 但 hook 没实现
   - 优先级低于 (a)(b)——vision YAML 审计已要求每条 UI PASS 有独立 vision 分析，同一张截图充多个 BDD 时 vision YAML 也得伪造多份，成本已大幅提高。md5 去重的边际收益有限

**优先级**：Important——T045 是 live 事故，但首要故障是 C7 执行违规，hook 是 backstop

---

### R2: P5 gate 缺 UI 冒烟检查——P2 → P5 传递性盲区（Important）

**现状**：P5 gate 只检查"测试通过 + 无 PROD_TOUCHED"。`check-gate.sh P5` 从 P2-design.md 的 `gate_commands.P5` 读取命令执行。

**盲区**：T045 P5 阶段，主 Agent 用 Playwright 检查详情页时发现**页面空白**（文件树空白、内容区空白），但以"后端问题不是 P4 回归"为由绕过。P5 gate 全过——因为单元测试通过、无 PROD_TOUCHED。

**根因**：`state-machine.md:98` 已要求"若 ui_affected: P2 gate_commands.P5 E2E 命令 exit 0"——**协议已要求 UI 任务 P5 跑 E2E，但 P2 没声明 + P5 没强制**。这是 P2 gate 的传递性盲区：P2 没声明 E2E 命令也能过 P2 gate。

**建议**：

a) **P2 gate 强制 UI 任务声明 E2E 命令**（优先方案，不引入新文件）：
   - `ui_affected: true` 时，P2-design.md 的 `gate_commands.P5` 必须含至少一条 E2E/冒烟命令（hook 检查 `gate_commands.P5` 非空且含 `playwright`/`curl`/`e2e` 字样）
   - 把问题拦在 P2，不引入新文件

b) ~~P5 gate 增加"冒烟检查"硬步骤 + P5-smoke-test.md~~ → **评审否决**：新增 self-authored 文件 + 主 Agent 填 status: passed 是形式合规，不如 (a) 在 P2 强制声明

c) ~~gate 输出含 WARNING → exit 2~~ → **评审否决**：gate 命令输出因项目而异，WARNING 在测试输出中极其常见（deprecation、node warnings），对任意 WARNING 降级会大量误杀

**优先级**：Important——P5 是技术验证关，UI 任务的 E2E 缺失让回归逃逸

---

### R3: P7 被系统性裁剪——文档化条件未实现 + 语义被误解（Important）

**现状**：`state-machine.md:167` 文档了"裁剪 P7：需改动文件数 ≤ 5"。但 **`check-pruning.sh` 从未实现 P7 的文件数检查**——脚本只有 P2/P3/P6 的裁剪条件检查 + P2.9 声明-执行一致性。

**数据**：PeekView 最近 10 个任务，**0 个保留 P7**。T030（29 文件）、T033（112 文件）、T039（110 文件）全部跳过 P7——文件数远超 5 但 hook 没拦。

**根因**（评审修正）：

1. **文档化条件未实现**（bug，不是设计缺陷）：`state-machine.md:167` 写了"文件数 ≤ 5"但 `check-pruning.sh` 没实现 P7 检查。10/10 任务跳 P7 不是因为"条件过机械被绕过"，而是因为 **hook 根本没拦**。

2. **P7 被误解为"跨端一致性"**：P1 analyst 常用"仅前端""不跨端"作为跳过 P7 的理由，但 P7 的设计目的是"实现是否偏离 P2 设计"——与是否跨端无关。

3. **文件数是弱相关变量**：1 个文件 3 处耦合改动比 6 个文件各改 1 行风险更高。T045 是 8 个文件，但 3 个组件共享 `.line` 样式——隐式耦合远超文件数反映的散布度。

**建议**：

a) **补实现已文档化的文件数条件**（bug fix，优先做）：
   - `check-pruning.sh` 增加 P7 检查：文件数 > 5 → 不可跳（`state-machine.md:167` 已文档化，补实现）
   - 文件数计算用 git diff 统计源码文件（排除 docs/tasks/ 等非源码）

b) **加隐式耦合维度**（self-declaration，与 risk_level 同级）：
   - P1 声明 `shared_styles: [...]` 或 `shared_interfaces: [...]` 时 → P7 不可跳
   - hook 检查声明字段存在性（不检查声明准确性——和 risk_level 一样是 self-declaration）

c) **WORKFLOW.md / state-machine.md P7 描述明确语义**：
   - 加一行："P7 是'实现是否偏离 P2 设计'，不是'是否跨端'。跨端一致性是 P7 的子集，不是 P7 的全部。"

d) ~~裁剪策略从"默认跳过+条件保留"改为"默认保留+条件跳过"~~ → **评审否决**：翻转默认影响所有未来任务，给大部分确实不需要 P7 的小任务增加开销。补实现现有条件 (a) + 加隐式耦合 (b) 已足够。T037/T040 保留 P7 是合理的，说明现有条件在"主 Agent 判断"层面能工作——问题在 hook 没强制执行

**优先级**：Important——10/10 任务跳 P7 是 hook 实现 bug + 语义误解，不是设计缺陷

---

### R4: P8 被系统性裁剪——裁剪无硬规则（Important）

**现状**：`state-machine.md` 写"涉及发布的任务必做 P8"。`check-pruning.sh` 没有对 P8 的裁剪条件——P8 可以被任意裁剪。

**数据**：PeekView 最近 10 个任务，仅 2 个保留 P8。8/10 跳过，理由同质化（"纯 bug 修复""合并到下次发布""不需要 bump"）。

**后果**：
- 用户可见修复停留在 main 但版本号不变
- `pipx upgrade peekview` 拿不到修复
- CHANGELOG `[Unreleased]` 条目写了但没有系统化发布检查

**建议**：

a) **P8 裁剪需显式声明 `internal_only: true`**（policy change，P8 从默认可跳 → 默认保留）：
   - P1 需声明 `internal_only: true` + 理由才能裁剪 P8
   - hook 检查声明存在性
   - 这是 policy change 而非 bug fix——P8 跳过的后果是用户可见的（拿不到修复），方向上合理
   - ~~git diff 含 `src/`/`backend/`/`frontend/` 路径 → 不可裁~~ → **评审否决**：`src/`/`backend/`/`frontend/` 是 PeekView 的路径，不是 agate 通用协议该硬编码的。agate 是通用协议，P2 的 `packages` 字段才是项目声明源码路径的约定读取点

b) ~~P8 简化版（patch bump + CHANGELOG + 测试重跑）~~ → **评审否决**：当前 P8 gate 已经是"脚本化部分通过 + 主 Agent 补充验证"（`check-gate.sh:60-87`），并非特别重。patch bump + CHANGELOG + 测试重跑本来就是 P8 的最小集。两级制增加协议分支复杂度，收益有限

**优先级**：Important——8/10 任务跳 P8 是系统性问题，`internal_only: true` 声明机制是可行改进

---

### R5: ~~P6 UI 验证规则不硬~~ → 合并入 R1

**评审合并**：R5 与 R1 是同一发现拆成了两条。R5(a)（check-p6-evidence.sh UI 检查）= R1(b)；R5(b)（provenance 审计 4）= R1(a)；R5(c)（文档明确"主 Agent 亲自跑"）是 C7 在 P6 UI 场景的重申。

**C7 重申**（R5(c)，接受）：
- WORKFLOW.md P6 行加："UI 条件的主 Agent 必须亲自跑 Playwright 截图 + vision-analyst 验证，不委托 subagent 自评"
- 本质是 C7 规则在 P6 UI 场景的明确化，不是新规则

---

## 评审总结

| # | 发现 | 优先级 | 根因类型 | 建议（评审后保留） |
|---|------|--------|---------|-------------------|
| R1 | provenance 盲区：形式合规≠实质合规 | Important | 审计覆盖面 | (a) vision YAML 审计 4 + (b) check-p6-evidence.sh UI 检查 + (c) md5 去重[Phase 2] |
| R2 | P5 缺 UI 冒烟检查 | Important | P2→P5 传递性盲区 | (a) P2 gate 强制 UI 任务声明 E2E 命令 |
| R3 | P7 被系统性裁剪 | Important | 文档化条件未实现 + 语义误解 | (a) 补实现文件数检查[bug fix] + (b) 加 shared_styles 维度 + (c) 语义澄清 |
| R4 | P8 被系统性裁剪 | Important | 裁剪无硬规则 | (a) `internal_only: true` 声明机制 |
| R5 | ~~P6 UI 验证规则不硬~~ | — | — | 合并入 R1；C7 重申 |

**核心洞察**：agate v0.5.0 的 hardening-roadmap 防的是"主 Agent 在 commit 时伪造"，但 T045 暴露的是"subagent 在执行时伪造 + 主 Agent 不验证就接受"。**首要防线是 C7**（主 Agent 亲自跑），provenance 审计是 **C7 被违反时的 backstop**。

**修复方向**：把"证据存在性检查"升级为"证据有效性检查"——不只检查文件存在，还检查文件内容是否对应 BDD 条件（vision YAML 的 blocker_count、UI 任务截图非空）。同时补实现已文档化但未实现的裁剪条件（P7 文件数检查 bug fix）。

**否决的建议**（评审否决，不进 v0.5.1）：
- R2(b)(c)：gate 输出 WARNING 降级 / P5-smoke-test.md → 过度工程或形式合规
- R3(d)：翻转 P7 裁剪默认 → 过度反应
- R4(a) git diff 路径硬编码 → 项目特定，不可泛化
- R4(b)：P8 两级制 → 复杂度收益比不好
- R1(c) md5 去重 → Phase 2，边际收益有限
