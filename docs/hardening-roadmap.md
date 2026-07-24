# agate 硬工具化路线图

> 日期：2026-06-29（v2：2026-06-30 修订；v3：2026-06-30 评审反馈修订；v4：2026-07-02 状态更新；v5：2026-07-24 版本计划补充）
> 状态：Phase 1 + 2A + 2B + 2C 已落地；Phase 3 已取消（依赖平台，非 agate 可独立实现）
> 关联：LIMITATIONS.md 局限 3（主 Agent 判断力是单点故障）、局限 4（subagent 不可观测）

---

## 1. 背景

### 1.1 问题

agate 经过多次复盘 + 实战评审，反复验证同一个根因：

**主 Agent 既是运动员又是裁判，且默认倾向于少走路。**

Agent 的"走捷径"不是"遇到困难时的行为退化"，是**出厂设置**——一切时候都倾向于少走步骤。所有依赖 Agent 自觉的环节都是脆弱的。

### 1.2 核心原则

> **有确定逻辑要处理的事情，用 hook、脚本等硬工具执行，不靠 Agent 自觉。**

### 1.3 与现有协议的关系

硬工具化是**加法，不是替换**。协议仍然告诉主 Agent "必须跑 gate"——现在多了一层：即使主 Agent 忘了跑，hook 也会跑。即使主 Agent 造假结果，CI 会重跑验证。

---

## 2. 已落地内容

### Phase 1：可脚本化检测（已全部落地）

| 编号 | 名称 | 脚本 | 状态 |
|------|------|------|------|
| P1.1 | pre-commit hook | `scripts/pre-commit-gate.sh` | ✅ 已实现（含多任务适配） |
| P1.2 | PROD_TOUCHED 检测 | `scripts/pre-commit-gate.sh` 内 | ✅ 已实现 |
| P1.3 | CI gate backstop | `.github/workflows/` + `scripts/ci-gate-backstop.py` | ✅ 已实现 |
| P1.4 | gate 结果存储 | `scripts/gate-result.sh` | ✅ 已实现（.gate-result.json + .gate-history.jsonl） |
| P1.5 | READY 检查 | `scripts/check-gate.sh` P8 case | ✅ 已实现（部分） |
| P1.6 | CHANGELOG 检查 | `scripts/check-changelog.sh` | ✅ 已实现 |
| P1.7 | P6 证据格式检查 | `scripts/check-p6-evidence.sh` | ✅ 已实现（含 R1a 截图 >1KB + md5 去重） |

### Phase 2A：状态一致性强制（已全部落地）

| 编号 | 名称 | 脚本 | 状态 |
|------|------|------|------|
| P2.3 | 状态转移强制 | `scripts/check-state-transition.sh` | ✅ 已实现（含 per-phase MAX_RETRY + 回退跳变 exit 1） |
| P2.4 | 重试计数强制 | `scripts/check-state-transition.sh` | ✅ 已实现（按阶段差异化） |
| P2.5 | 回退跳变检测 | `scripts/check-state-transition.sh` | ✅ 已实现（恢复 exit 1，只查回退方向，保留 PAUSED 守卫） |
| P2.15 | .state.yaml 格式校验 | `scripts/check-state-yaml.sh` | ✅ 已实现 |
| — | 多任务 .state.yaml 扫描 | `scripts/pre-commit-gate.sh` | ✅ 已实现（Phase-产出一致性 WARNING） |
| — | P2.6 修复后全量重跑验证 | — | ❌ 移除（hook 无法验证 full run vs partial run） |

### Phase 2B：产出独立化与流程选择硬约束（已全部落地）

| 编号 | 名称 | 脚本/机制 | 状态 |
|------|------|----------|------|
| P2.1 | P6 验收独立化 | `scripts/check-p6-provenance.sh` | ✅ 降级方案 v2（客观行为审计：证据-结论对应 + dispatch-context 审计 + BDD 总数对照 + R1b vision YAML 审计） |
| P2.2 | BDD 格式 + 总数对照 | `scripts/check-p6-provenance.sh` | ✅ 已实现（provenance 审计覆盖） |
| P2.7 | 风险等级字段 | `scripts/check-pruning.sh` | ✅ 已实现（low/medium/high） |
| P2.8 | 裁剪条件 hook 检查 | `scripts/check-pruning.sh` | ✅ 已实现（P2/P4/P5/P6 不可裁 + P3 仅 low 可裁 + P7 源码文件数 + P8 internal_only + 跳过风险 nudge） |
| P2.9 | 裁剪声明回写 | `scripts/check-pruning.sh` | ✅ 已实现（override 字段） |
| P2.10 | P2 评审派发强制 | `scripts/check-p6-provenance.sh` | ✅ 降级方案 v2（agent 字段软提醒 + dispatch-context 审计） |
| P2.11 | SCOPE+ 处理追踪 | `scripts/check-scope-resolved.sh` | ✅ 已实现 |
| P2.12 | 复盘异常触发 | `scripts/check-retrospective.sh` | ✅ 已实现（按阶段差异化重试提醒） |
| P2.13 | 非 agate 任务风险矩阵 | `WORKFLOW.md` | ✅ 已实现 |
| P2.14 | "直接做"最低要求 | `WORKFLOW.md` | ✅ 已实现 |
| — | P2 form check（权衡/选择理由） | `scripts/check-gate.sh` | ✅ 已实现 |
| — | P2 status:approved + 四字段检查 | `scripts/check-gate.sh` | ✅ 已实现 |
| — | P8 internal_only_reason | `scripts/check-pruning.sh` | ✅ 已实现 |
| — | md5 截图去重 | `scripts/check-p6-evidence.sh` | ✅ 已实现 |
| — | self-gate 机制 | `SELF-GATE.md` + `scripts/check-protocol-consistency.py` CHECK 9 | ✅ 已实现（含反向传播） |

### 架构：两层防护（已落地）

```
Layer 1: pre-commit hook（本地，防"不知不觉绕过"）
  - 扫描所有暂存 .state.yaml（根 + 任务级）
  - 跑 gate + 写 .gate-result.json
  - PROD_TOUCHED 检测
  - 状态转移 + 重试上限 + 回退跳变
  - 裁剪条件 + SCOPE+ 追踪
  - P6 证据格式 + md5 去重
  - phase-产出一致性 WARNING

Layer 2: CI backstop（远程，防"故意绕过"）
  - 重跑 gate + 对照 .gate-result.json
  - 一致性检查（CHECK 1-9）
  - 捕获 --no-verify 绕过
```

---

## 3. 待落地内容

### Phase 2C：ADR + 术语表（v0.14.0 已落地）

| ID | 内容 | 脚本/文件 | 状态 |
|----|------|----------|------|
| P2.16 | 架构决策记录 | `adr.md`（6 条核心 ADR） | ✅ 已实现 |
| P2.17 | 术语表 + 上下文 | `CONTEXT.md`（20 个术语） | ✅ 已实现 |
| P2.18 | A7 审查锚定到 ADR | `protocol-alignment-review.md` | ✅ 已实现 |

### Phase 2D：BDD 标准化 + bug 修复（v0.20.0 已落地）

| ID | 内容 | 脚本/文件 | 状态 |
|----|------|----------|------|
| P2.19 | BDD 编号格式标准化 | `#### BDD-NN:` + `###` 功能分组 | ✅ 已实现 |
| P2.20 | T3: P1 BDD 计数硬阻 | `check-p6-provenance.sh` grep -cE | ✅ 已实现 |
| P2.21 | T6: AGATE_CARD 块剥离 | `pre-commit-gate.sh` sed | ✅ 已实现 |
| P2.22 | M5: gate_commands YAML 解析 | `check-gate.sh` python3 regex | ✅ 已实现 |
| P2.23 | B01→BDD 批量替换 | 8 个 bats 文件 + 5 fixture | ✅ 已实现 |

### Phase 3：平台接口规范（已取消 — 依赖平台能力，非 agate 可独立实现）

| 编号 | 名称 | 原计划 | 取消理由 |
|------|------|--------|---------|
| P3.1 | 平台接口规范文档 | 定义 agate 需要的平台能力 | 平台不会为 agate 实现专属接口 |
| P3.2 | subagent 可观测性 | 平台暴露 subagent 活动信号 | 依赖平台支持，无法自行实现 |
| P3.3 | gate 结果独立存储 | 平台提供主 Agent 不可写的存储位置 | 依赖平台支持，无法自行实现 |
| P3.4 | gate 执行平台化 | 平台在 subagent 返回后自动触发 gate | 依赖平台支持，无法自行实现 |

**P2.1 P6 验收独立化的根治**：当前降级方案靠 provenance 审计（证据-结论对应 + BDD 总数对照 + vision YAML），但主 Agent 仍可造假证据。根治需平台支持独立 git author，Phase 3 已取消——接受此为结构性局限。

---

## 4. 与 LIMITATIONS.md 的对应关系

| 局限 | 描述 | Phase 1 缓解 | Phase 2 缓解 | Phase 3 根治 |
|------|------|-------------|-------------|-------------|
| 局限 1 | 测试质量上限 | — | — | —（方法论边界） |
| 局限 2 | 同源模型盲区 | — | — | —（方法论边界） |
| 局限 3 | 主 Agent 判断力单点 | ✅ gate 执行不被跳过 | ✅ P6 审计 + 状态强制 + 流程选择硬约束 | 取消（结构性局限，接受） |
| 局限 4 | subagent 不可观测 | — | — | 取消（结构性局限，接受） |
| 局限 5 | 协议文档一致性 | — | ✅ self-gate + CHECK 9 | — |
| 局限 6 | 运行时依赖 | — | ✅ 文档化（LIMITATIONS.md + AGENTS.md） | — |
| 局限 7 | vision/UI 基础设施 | — | ✅ 文档化（LIMITATIONS.md） | — |
| 局限 8 | CI backstop 仅 GHA | — | ✅ 文档化（LIMITATIONS.md + AGATE_TASKS_DIR） | — |

---

## 5. 版本计划

### v0.21.0 — 协议自维护基础设施补丁（P2+P3 合并）

| ID | 内容 | 涉及文件 | 状态 |
|----|------|----------|------|
| P2.29 | LIMITATIONS.md 交叉引用 ADR | `LIMITATIONS.md` | ✅ 已实现 |
| P2.30 | 反向传播表补 BDD 传播路径 | `protocol-alignment-review.md` | ✅ 已实现 |
| P2.31 | check-retrospective.sh 排除 dispatch-context + AGATE_CARD | `check-retrospective.sh` | ✅ 已实现 |
| P2.32 | gate 错误消息列具体文件名 | `check-p6-evidence.sh` | ✅ 已实现 |

**合理性审查 DROP 项**：P2.25（change_nature 是 pre-protocol 决策非 P0-brief 字段）、P2.26（P0 入口点措辞差异是有意设计）、P2.28（一行默认值无需测试）

**DOWNGRADE 项**：P2.24（ADR-007 事后记录低优先级）、P2.27（python3 环境变量零真实报告）

### v0.22.0 — Superpowers 吸收 + 上下文编排 + 并行执行

| ID | 内容 | 涉及文件 | 状态 |
|----|------|----------|------|
| P2.37 | architect.md 方案探索方法论（按场景类型） | architect.md | ✅ 已实现 |
| P2.38 | investigate.md 结构化诊断强化（≥3 原因/排除留痕/禁止先改试试） | investigate.md | ✅ 已实现 |
| P2.39 | dispatch-prompt.md P4 回退诊断模板自动注入 | dispatch-prompt.md | ✅ 已实现 |
| P2.40 | verifier.md 验证纪律（先验证后结论） | verifier.md | ✅ 已实现 |
| P2.41 | implementer.md 最小实现原则 + 测试不通过决策树 | implementer.md | ✅ 已实现 |
| P2.42 | dispatch-context 上游关联自动提取脚本（--write 模式） | agate-extract-context.sh + bats | ✅ 已实现 |
| P2.43 | 阶段卡片并行执行操作指引（评审+按包拆分+基础设施隔离） | 5 phase cards + dispatch-protocol.md | ✅ 已实现 |
| P2.44 | loop-orchestration.md 并行执行状态更新 | loop-orchestration.md | ✅ 已实现 |

### v0.23.0+ — 设计讨论（P4，按需启动）

| ID | 内容 | 依赖 | Issue |
|----|------|------|-------|
| P2.33 | C8 机械化 + 领域触发评审硬要求 | 独立设计讨论 | #59 |
| P2.34 | 审计/可观测性重设计 | 独立设计讨论 | #60 |
| P2.35 | 重试预算模型（功能/格式分离） | 独立设计讨论 | #61 |
| P2.36 | Monorepo 多目录 AGATE_TASKS_DIR | 独立设计讨论 | #62 |

### 不修清单（设计选择/低价值/arms race）

| ID | 内容 | 理由 | Issue |
|----|------|------|-------|
| — | G3: P6 无单命令入口 | pre-commit-gate 已自动调用 | #63 |
| — | G5: SCOPE+ 回补后无强制重审 | 评审员训练问题 | — |
| — | G8: 频繁修改同一文件检测 | 低价值，事后审查足够 | — |
| — | M3: 模板示例偏向 JS/Python | 已记录，非阻断 | — |
| — | M4→P2.27 | 已提升为可修项 | #53 |
| — | P6-format 裸路径不加括号 | 语义判断，provenance 审计处理 | — |
| — | N14-N16: 流程/训练问题 | 非协议层面 | — |
| — | M6: P6 发现已知局限无后续跟踪 | workflow 问题 | — |
| — | T4: P3 测试覆盖边界条件 | test-designer 职责 | — |
| — | T5: agate-next-card.sh 路径解析 | ✅ 已修复（v0.21.1：用 AGATE_ROOT 替代 AGATE_REPO，ci-gate-backstop.py 用 __file__ 相对路径） | — |
| — | M2: 证据扩展名白名单 | 实测已无白名单（by design, ADR-003），关闭 | — |
| — | 目录改名 agate/ → agate-core/ | 高成本中收益（~205 引用 / ~33 文件 / 下游 breaking），留待 v2.0 窗口重新派生 | PR #46 已关 |

### 结构性限制（需平台支持，记录不修）

| 局限 | 描述 | 根治条件 |
|------|------|---------|
| 局限 3 | 主 Agent 判断力单点故障 | 平台支持独立 git author |
| 局限 4 | subagent 不可观测 | 平台暴露 subagent 活动信号 |
| — | P6 证据真实性无法机器验证 | CI 独立重新生成证据 |
| — | dispatch-context provenance 链 | 平台支持 subagent 工具调用日志 |

### 代码 TODO

| 位置 | 内容 | 触发条件 |
|------|------|---------|
| `check-p6-provenance.sh:245` | 移除旧格式兼容 | v2.0 |

---

## 6. 待论证的改进

| 改进 | 内容 | 状态 |
|------|------|------|
| evidence 类型检查 | `ui_affected: true` 时 evidence 不能全是 .md/.txt（防源码分析充数） | 待论证（`docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`） |
| 能力使用检查提醒 | P5/P6 派发 prompt 加能力对账（防忘了派 vision-analyst） | 待论证 |
| 诊断优先提醒 | `retries >= 2` 时 hook 提醒"跑诊断命令" | 待论证 |
| verifier 工具困难处理 | 角色文件补"遇到工具困难标 NEED_CONFIRM，不回退源码" | 待论证 |
| Issue #002 | self-gate 递归触发缺乏终止机制 | 待设计 |
