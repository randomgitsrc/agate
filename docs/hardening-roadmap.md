# agate 硬工具化路线图

> 日期：2026-06-29（v2：2026-06-30 修订；v3：2026-06-30 评审反馈修订；v4：2026-07-02 状态更新）
> 状态：Phase 1 + 2A + 2B 已落地；Phase 3 待平台支持
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

硬工具化是**加法，不是替换**。协议仍然告诉主 Agent "必须跑 gate"——现在多了一层：即使主 Agent 忘了跑，hook 也会跑。即使主 Agent 伪造结果，CI 会重跑验证。

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
| P2.8 | 裁剪条件 hook 检查 | `scripts/check-pruning.sh` | ✅ 已实现（P2 不可裁例外口 + P3 high 不可裁 + P6 no_behavior_change + P7 源码文件数 + P8 internal_only + 跳过风险 nudge） |
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

### Phase 3：平台接口规范（待平台支持）

| 编号 | 名称 | 做什么 | 解决什么 | 状态 |
|------|------|--------|---------|------|
| P3.1 | 平台接口规范文档 | 定义 agate 需要的平台能力 | 明确"需要什么"才能争取"平台给什么" | 待写 |
| P3.2 | subagent 可观测性 | 平台暴露 subagent 活动信号 | 局限 4：subagent 卡死 vs 在干活不可区分 | 待平台支持 |
| P3.3 | gate 结果独立存储 | 平台提供主 Agent 不可写的存储位置 | .gate-result.json 防篡改的根治方案 | 待平台支持 |
| P3.4 | gate 执行平台化 | 平台在 subagent 返回后自动触发 gate | 覆盖非 git 事件的 gate 执行 | 待平台支持 |

**P2.1 P6 验收独立化的根治**：当前降级方案靠 provenance 审计（证据-结论对应 + BDD 总数对照 + vision YAML），但主 Agent 仍可伪造证据。根治需要平台支持独立 git author（P3.1 平台能力调查）。

---

## 4. 与 LIMITATIONS.md 的对应关系

| 局限 | 描述 | Phase 1 缓解 | Phase 2 缓解 | Phase 3 根治 |
|------|------|-------------|-------------|-------------|
| 局限 1 | 测试质量上限 | — | — | —（方法论边界） |
| 局限 2 | 同源模型盲区 | — | — | —（方法论边界） |
| 局限 3 | 主 Agent 判断力单点 | ✅ gate 执行不被跳过 | ✅ P6 审计 + 状态强制 + 流程选择硬约束 | 待：结果防篡改 |
| 局限 4 | subagent 不可观测 | — | — | 待：平台可观测性 |
| 局限 5 | 协议文档一致性 | — | ✅ self-gate + CHECK 9 | — |

---

## 5. 待论证的改进

| 改进 | 内容 | 状态 |
|------|------|------|
| evidence 类型检查 | `ui_affected: true` 时 evidence 不能全是 .md/.txt（防源码分析充数） | 待论证（`docs/plans/agate-evidence-diagnosis-v2-2026-07-02.md`） |
| 能力使用检查提醒 | P5/P6 派发 prompt 加能力对账（防忘了派 vision-analyst） | 待论证 |
| 诊断优先提醒 | `retries >= 2` 时 hook 提醒"跑诊断命令" | 待论证 |
| verifier 工具困难处理 | 角色文件补"遇到工具困难标 NEED_CONFIRM，不回退源码" | 待论证 |
| Issue #002 | self-gate 递归触发缺乏终止机制 | 待设计 |
