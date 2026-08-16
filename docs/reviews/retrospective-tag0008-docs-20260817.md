# TAG0008 复盘 — agate 版本管理机制（v0.50.0）

> 任务：agate 版本管理机制 v1（多版本共存 + 项目锁定 + 程序化安装/升级 + 内网离线部署包）
> 分支：feat/TAG0008-version-management → PR #148（普通 merge）→ v0.50.0
> 执行窗口：2026-08-16 10:46 ~ 08-17 02:00（跨 session，含 Windows 冒烟修复）
> 事实依据：git log（13 commit）+ .state.yaml retries + **OpenCode session 提取**（主会话 ses_ff789c4c + 27 subagent 子会话，指南 docs/reviews/opencode-session-extraction-guide.md）

---

## 0. 事实基线

| 项 | 数据 |
|----|------|
| P1 BDD | 29 条 → 31 条（SCOPE+ 增补 2）|
| P6 验收 | 31/31 BDD PASS（真实 CLI 实跑）|
| P7 一致性 | BLOCKER=0，DESIGN_GAP 8/8 REVIEWED |
| pytest | 823 passed（基线 780 + 新增 43）|
| consistency | 0 ERROR |
| 版本 | v0.49.0 → v0.50.0（bump minor）|
| retry | P1×1（quality）、P2×1（empty_return）、P4×1（quality）、P5×1（empty_return）|
| Windows 冒烟修复 | 2 失败（resolve-entry os.execv 根因 + latest 指针）→ 修复后 89 passed |
| subagent 空返回 | 2 次（P2 architect、P5fix implementer）|

## 1. 做得好的

1. **dispatch_plan 被 dogfooding 验证**：P2 输出 `dispatch_plan: static-batch 3 批`（resolve-chain / install / offline），P3 按批并行派发、P4 按批实现——**TAG0014 刚建的派发编排机制在本任务真实生效**。P4 还应用了共享文件约束（resolve-chain 先改共享 agate_common.py，install/offline 只读）。
2. **空返回处理完全符合协议**：P2 architect 连续 2 次空返回——主 Agent 按协议：第 1 次原样重试（不占槽位）→ 仍空返回 → 计入 retries + 根因分析（认知过载："从零写大报告"推理失败）→ 调整策略（新会话 + dispatch-context 内联已验证设计输入）→ 成功。**没有违规降级，没有静默绕过**。
3. **Windows 冒烟修复的系统性调试**（session 提取证实）：失败 1（test_csg_1）**前两轮修复被 CI 证伪 → 第三轮做 CI 实证诊断（DIAG-j/k 对比探针）→ 决定性证据（os.execv 丢 stderr）→ 外科手术式修复**。这是 systematic-debugging 的教科书级应用，且"被 CI 证伪后不猜、先取证"的做法值得固化。
4. **P4 C8 评审真实有效**：review 专家发现 3 条真实 CRITICAL（指针解析 isdir 短路破坏 BDD-5 / install-offline 无 Pillow bundle 默认流断裂 / manifest 路径穿越）→ rejected → 迭代修复 → 复核 approved。评审角色独立性有实际产出。
5. **gate 逐阶段执行 + CI 兜底**：每阶段主 Agent 预跑 gate + commit hook 复核 + CI 双矩阵——823 passed 全绿后 merge。
6. **R4 平台扫描误报处理**：注释里 `/tmp` 字面量触发 R4（平台假设扫描器）——识别为纯注释误报，改措辞（"系统临时目录"）而非改扫描器或加豁免，正确处理。

## 2. 发现的问题

### 2.1 P2 architect 空返回：复杂产出认知过载（机制缺口/执行交互）
- **现象**：architect 做了大量调研（含最小验证）但 P2-design.md 未落盘，连续 2 次空返回。
- **归因层面**：**agate 机制层**（认知过载是 dispatch-protocol 已知的"从零写大报告"问题，T016 教训）——但本次处理**完全正确**（内联输入 + 换会话），说明机制已能兜住。遗留点：**P2 是单 subagent 大产出**，没有像 P3-P8 那样的 dispatch_plan 拆分路径（P2 本身设计时还没有 plan）。
- **改进措施**：RM-AG0016（派发编排）已覆盖"模式 4 先理解后拆"——但 P2 自身作为"设计后续批次的阶段"无法拆。建议：复杂 P2 可先派"侦察 architect"产出结构化设计要点，再派"主 architect"写 P2-design.md（**记入 RM-AG0022 协议结构化层或作为派发编排的模式 4 应用示例**）。

### 2.2 Windows os.execv 丢 stderr：跨平台进程语义差异（机制缺口，本任务暴露）
- **现象**：`resolve-entry.py:54` 用 `os.execv` exec gate py——Windows 上（`_wexecv` → CRT spawn）不继承重定向 std handles，gate 的 stderr WARNING 输出丢失 → commit-msg hook 静默（TAG0013 的 README 触发面在 Windows 失效）。
- **归因层面**：**agate 机制层 + 平台差异**——resolve-entry 是 TAG0008 新写的，但 `os.execv` 的跨平台语义（POSIX 真 exec vs Windows spawn）没在设计中考虑。
- **改进措施**：resolve-entry Windows 分支改 `subprocess.run` 透传（已修复）。**教训**：hook 链上的 exec 类调用必须考虑 Windows 的 std handle 继承差异。**同类扫描**：grep 全仓 `os.execv`/`os.spawn` 是否有其他 Windows 平台风险点。

### 2.3 P4 评审 3 CRITICAL：评审发现真实缺陷（正面，但暴露设计迭代成本）
- **现象**：P4 review 专家发现 3 条 CRITICAL（指针 isdir 短路 / install-offline 默认流 / manifest 路径穿越），rejected → 回派修复。
- **归因层面**：**执行层正常**（P4 实现含缺陷 → 评审拦截 → 修复，这是机制在正确工作）。不是问题，是"评审真实有效"的证明（已列入做得好的）。
- **改进措施**：无（机制工作正常）。但可记录：manifest 路径穿越暴露"路径处理需要安全审计"——可复用 cso 角色关注点。

### 2.4 P5fix implementer 空返回：诊断过深导致认知过载（执行层）
- **现象**：P5 修复轮 implementer 深度诊断 git-for-windows 机制后修复未落盘，空返回。
- **归因层面**：**执行层 + 机制交互**——单个 subagent 承担"深度诊断 + 修复"双重任务过重；主 Agent 处理正确（拆两失败为独立小任务并行派发）。
- **改进措施**：RM-AG0016 的模式 4（先理解后拆）+ 任务粒度指引已覆盖"诊断与修复分离"。**确认**：本任务处理符合协议（拆分 + 并行），无机制缺口。

### 2.5 P1 影响面表 4 处联动点缺口被 requirements-review 抓住（机制正效应）
- **现象**：P1 影响面表（~/.agate 消费点）被 requirements-review 发现 4 处联动点缺口 → needs-revision → rev2 修复。
- **归因层面**：**机制正效应**——同类扫描强制 + requirements-review 独立审查共同兜住。不是问题。
- **改进措施**：无。

## 3. 问题清单 + 改进措施（汇总）

| # | 问题 | 归因 | 措施落点 |
|---|------|------|---------|
| 2.1 | P2 复杂产出空返回 | 机制交互（已正确兜住）| RM-0016 模式 4 应用示例：复杂 P2 先侦察再主写 |
| 2.2 | os.execv Windows 丢 stderr | **机制缺口 + 平台差异** | resolve-entry 已修（subprocess 透传）；grep 全仓 os.execv 同类风险 |
| 2.3 | P4 评审 3 CRITICAL | 机制正效应（评审有效）| 无 |
| 2.4 | P5fix 空返回 | 执行层（已正确拆分）| 无 |
| 2.5 | P1 影响面缺口被评审抓 | 机制正效应 | 无 |

**真正需要行动的**：2.2（os.execv 同类扫描）。

## 4. 亮点 + 可复用模式

1. **dispatch_plan 全流程 dogfooding**（可固化）：P2 输出 dispatch_plan → P3 按批并行 → P4 按批实现 + 共享文件约束——TAG0014 机制的第一次实战验证，**建议在后续任务推广**（RM-AG0016 已定）。
2. **Windows 修复的 CI 实证诊断法**（可固化）：前两轮修复被 CI 证伪 → 第三轮 DIAG-j/k 对比探针 → 决定性证据 → 外科修复。**"被证伪后不猜、先取证"**——可写入 systematic-debugging 相关角色文件。
3. **retries 落盘质量高**（已固化）：.state.yaml 的 failure_mode/prompt_changed/adjustment 全填——复盘能精确还原每次 retry 的因果。

## 5. 复盘机制触发核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（4 次）| ✅ P1/P2/P4/P5 各 1 次，adjustment 详实 | | |
| 空返回恢复 | 是（2 次）| ✅ P2 architect / P5fix 按协议（重试→根因→调整）| | |
| SCOPE+ | 是（P4 增补 2 BDD）| ✅ 处理 + P7 闭环 | | |
| SCOPE_RESOLVED | 是 | ✅ | | |
| DESIGN_GAP | 是（8 条）| ✅ 8/8 REVIEWED | | |
| P4 评审 | 是（backend+security+high）| ✅ review+cso 并行 + 组长汇总 | | |
| P4 评审迭代 | 是（3 CRITICAL）| ✅ rejected→修复→复核 approved | | |
| dispatch_plan | 是（TAG0014 机制）| ✅ static-batch 3 批全流程应用 | | |
| gate 验证 | 是 | ✅ 每阶段预跑 + hook + CI | | |
| 平台扫描 R4 | 是（注释误报）| ✅ 识别误报改措辞 | | |
| Windows 冒烟 | 是（2 失败）| ✅ 修复后全绿 | | |
| 技术债登记 | 待评估 | 2.2 os.execv 同类扫描是否登记 | | |

## 6. 版本发布清单核对

- [x] pytest 823 passed + 0 consistency ERROR + ruff
- [x] README badge + CHANGELOG [0.50.0] + UPGRADING 章节
- [x] `git tag v0.50.0 && git push`（CHECK 7 通过）
- [x] release PR 普通 merge（--no-ff），tag 为 main 祖先
- [x] Windows 冒烟修复后 CI 双矩阵全绿

---

> **事实依据说明（RM-AG0020 原则应用）**：本复盘基于 L1 仓库落盘（git log/.state.yaml retries/产出文件）+ **L2 session 提取**（主会话决策链 + subagent 行为，用 docs/reviews/opencode-session-extraction-guide.md 方法从 opencode.db 提取）。session 提取揭示了 progress 文件没覆盖的细节：P2 空返回的"调研完成但未落盘"、Windows 修复的"前两轮证伪 → 第三轮取证"、P4 评审的"专家发现 3 CRITICAL 的决策链"。**L3 平台导出在此次复盘是主力事实源**——验证了 RM-AG0020 的 L3 层设计价值。
