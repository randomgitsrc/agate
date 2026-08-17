---
phase: DONE
task_id: TAG0006-ui-ux-quality
type: retrospective
parent: P8-release.md
trace_id: TAG0006-RETRO-20260818
status: draft
created: 2026-08-18
agent: orchestrator
---

# TAG0006 复盘 — agate UI/UX 验收质量机制

> 本复盘基于任务 P0-P8 全程 + 中间多次 gate 失败/review 打回的过程记录。按 RM-AG0020 复盘机制组织（事实基线 / 做得好的 / 发现的问题（分层归因）/ 改进措施 / 机制核对清单）。

---

## 1. 事实基线（客观数据）

| 维度 | 值 |
|------|-----|
| 任务 | TAG0006 agate UI/UX 验收质量机制（RM-AG0004/0006/0007 + SCOPE+ UI/UX 覆盖任意渲染形态） |
| 产出版本 | v0.51.0（minor，2026-08-18） |
| BDD 数 | 15 条（P1 首轮）→ 17 条（SCOPE+ 增补 BDD-16/17）→ P6 全部 PASS |
| 新增测试 | 53 用例（P3）+ 5 回归（P4 修复轮）= 58 新增，全量 881 passed + 2 skipped |
| 改动文件 | P4 28 文件（7 gate 脚本 + 18 协议文档 + 3 测试）|
| 子 Agent 派发 | P1 analyst×2（修复轮+SCOPE）/P2 architect×2（修复+SCOPE）/P3 test-designer×1/P4 implementer×2（+修复轮）/P5 verifier×1/P6 verifier×1/P7 consistency-reviewer×1/P8 releaser×1 + 评审 subagent 若干 |
| retry | P1×1、P2×1、P3×1、P4×1（详见 §3）|
| 范围扩展 | 1 次用户 SCOPE+（2026-08-17，工作流中途中止 P3 提出）|

---

## 2. 做得好的 + 可复用模式

**可复用模式 1：SCOPE+ 中途回退增补的成功路径**（用户在工作流中途提出范围扩展）
- 用户中止 P3 → 回退 P1 增补 BDD（标注 [BASELINE_CHANGE]）→ 回退 P2 增补设计（§2.15/§2.16）→ 双评审复审 → 再进 P3。全程未丢失已 approved 的语义，靠"叠加适配层 + 明确标注"而非推翻。
- **可固化**：SCOPE+ 增补时保留原 approved 内容 + 新增标注 [BASELINE_CHANGE]，比"重写"安全。
- **建议**：agate 协议可考虑支持"SCOPE+ 增补轮"的明确流程标注（当前靠主 Agent 自律）。

**可复用模式 2：双评审互相印证缺陷**（P4 design-review + review 独立发现同一 avg-hash/GAP 缺陷）
- 两个不同视角评审独立定位到 check-p6-evidence 的 zip 对齐 + check-p6-provenance 的 GAP 短路——交叉验证提高缺陷捕获率。这正是 C8 双域评审的价值实证。

**可复用模式 3：gate 发现问题后修根因而非绕过**（P3 collect-only 误判）
- check-tdd-red 报绿 → 排查发现 P2 gate_commands.P3 固化为 `--collect-only`（只收集不执行）→ 改回 `--tb=no`。没有绕过 check-tdd-red，而是修了命令配置根因。

---

## 3. 发现的问题（分层归因）

### 3.1 机制缺口（协议/工具层面，→ 立 RM/DEBT）

**G-1：`gate_commands.P3` 用 `--collect-only` 致 check-tdd-red 误判绿**（P3）
- P2 architect 把 P3 命令设为 collect-only（误以为 check-tdd-red 只读测试集），实际 check-tdd-red 需要看断言失败行判红灯 → 误判 exit 2 绿。
- 归因：**协议文档误导**——P3 卡片注释"P3 用 collect-only 供 check-tdd-red 读测试集"本身就是错误理解（check-tdd-red 读的是失败行不是测试集），architect 照搬。
- 措施：改 gate_commands.P3 为 `--tb=no` + 修正 P3 卡片注释（已做）。**建议协议文档明确 check-tdd-red 需要执行测试输出而非 collect-only。**
- 流向：**DEBT**（gate_commands 语义文档化）。

**G-2：P6 `check-p6-provenance.py` GAP 分支 `sys.exit(0)` 短路后续硬审计**（P4 双评审发现）
- GAP 分支在校验人工复核记录后整脚本退出，跳过审计 5（日志 EXIT_CODE）/审计 6（evidence JSON）两个 exit 1 硬检查 → GAP 任务比 available 任务 gate 更弱。
- 归因：**机制缺口**（implementer 实现偏差 desc 与 P2 设计"只放松 vision YAML"不符）。
- 措施：修 GAP 分支为 is_gap 开关只跳过 vision 子块（已做）。

**G-3：`check-p6-evidence.py` avg-hash zip 对齐脆性**（P4 双评审发现，已登记 DEBT0006）
- `zip(sorted(glob), ahash_lines)` 依赖文件名与哈希行一一对应，但非图片文件被 agate-image-check suppress 跳过 → 行数不匹配错位。
- 归因：**机制缺口**（脚本间隐式耦合）。
- 措施：统一 `_is_image` 过滤口径（已做），DEBT0006 登记重构建议。

**G-4：P8 README badge bump 后未打 tag 导致 CHECK 7 测试红**（P8）
- bump README badge 到 v0.51.0 但 tag v0.51.0 未打 → `test_con_6_check_7_version_badge_sync` 失败（CHECK 7 = version badge vs git tag 同步）。
- 归因：**机制缺口**（P8 顺序：先 commit 版本文件 + 再 tag + 再重跑 P5；AGENTS.md 版本发布清单写了"tag+push"但未强调"重跑 P5 依赖 tag 已打"）。
- 措施：先打 tag 再重跑 P5（已做）。**建议 P8 卡片/AGENTS.md 明确"README badge 更新与 git tag 必须同批，P5 重跑须在 tag 之后"。**

### 3.2 执行层（主 Agent/subagent 未遵守规则，→ 修纪律）

**E-1：`.state.yaml` 多次 YAML 冒号语法错误**（P1/P4）
- reason/adjustment 字段含半角冒号（`design:`/`backend:`）触发 YAML mapping 错误，pre-commit 拦截。
- 归因：**执行错误**（写 YAML 值未加引号）。
- 措施：YAML 值含半角冒号/特殊字符时加引号（已做）。**建议 protocol 审查替代/主 Agent 提醒。**

**E-2：plan-design-review SCOPE 复审空返回**（P2）
- subagent 完成复审但产出文件未落盘（空返回），progress 显示已判定需 recovery 恢复会话落盘。
- 归因：**执行层**（subagent 未写文件即返回，符合空返回恢复流程，已正确走 resume 路径）。
- 措施：通过 task resume 恢复落盘（已做）。

---

## 4. 改进措施（落到文件/字段/gate）

| 措施 | 落点 | 状态 |
|------|------|------|
| gate_commands.P3 语义文档化（check-tdd-red 需执行输出）| P3 卡片注释已改（本任务内）| ✅ 已做 |
| P8 版本 bump 顺序（badge+tag 同批，P5 重跑在 tag 后）| P8 卡片/AGENTS.md 版本发布清单 | ⏳ 建议 |
| DEBT0006 ahash zip 重构（内联或成对输出）| 已登记 DEBT0006（本任务已临时修复 + 登记重构方向）| ✅ 登记 |
| YAML 冒号告警 | 文档提醒/模板提示 | ⏳ 建议 |

---

## 5. 机制核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅（P1/P2/P3/P4 各记录）| — | — |
| PAUSED | 否（无 retry 超限/跨段回退）| — | — | 无触发条件 |
| PROD_TOUCHED | 否（全程 worktree）| — | — | 无触达 |
| SCOPE+ | 是（用户 2026-08-17 扩展）| ✅ | 无 | 已增补 BDD-16/17 + BASELINE_CHANGE |
| SCOPE_RESOLVED | 是 | ✅（P4 无新增 SCOPE+，P1 已含 BASELINE_CHANGE 处理）| 无 | — |
| DESIGN_GAP | 否（P4 声明"无"）| ✅（P7 转抄"无"并 REVIEWED）| 无 | — |
| DESIGN_GAP_REVIEWED | 是（P4 声明存在性）| ✅ | 无 | — |
| NEED_CONFIRM | 否 | — | 无 | 需求方向已锁定 |
| CAPABILITY_GAP | 否 | — | 无 | visual supplementable 非 GAP |
| gate 验证 | 是（每阶段）| ✅（P1-P8 均实跑）| 无 | — |
| 阶段产出文件 | 是 | ✅（P1-P8 全产出）| 无 | — |
| .state.yaml phase 同步 | 是 | ✅ | 无 | — |
| 裁剪条件 + override | 否（零裁剪）| — | 无 | — |
| capability_requirements | 是 | ✅（P1 三态声明 + P2 消费）| 无 | — |
| 分阶段落盘 | 是 | ✅ | 无 | 防空返回生效（plan-design-review 空返回靠 progress 恢复）|
| phase-产出一致性 | 是 | ✅ | 无 | — |
| P6 evidence | 是 | ✅（17 BDD 证据齐全）| 无 | — |
| P2 候选方案 | 是 | ✅（candidate_count=4）| 无 | — |
| P8 internal_only_reason | 否（P8 未裁）| — | 无 | — |
| dispatch-context.md | 是 | ✅（每阶段派发前写+注入卡片）| 无 | — |
| pre-commit hook | 是 | ✅（多轮拦截 state YAML/P1 gate/SCOPE 扫描）| 无 | hook 有效 |
| CI backstop | 否（未 push）| — | — | push 后由 PR CI 兜底 |
| 技术债登记 | 是 | ✅（DEBT0005/0006 登记并 closed）| 无 | — |

---

## 6. 事实依据

- **L1 仓库落盘**：git log（P1-P8 + READY 共 15 commits）、各阶段产出文件、.state.yaml（含 retries/scope_expand/p3_fix/READY 记录）、progress.md（各阶段 subagent 落盘）。
- **L2 会话 checkpoint**：本会话过程中持续落盘（P{n}-dispatch-context 冻结 + P{n}-review.md 复审记录 + .state.yaml 增量）。
- **L3 平台 session**：无导出（OpenCode 会话），以 L1/L2 为准。

---

[PROD_NOT_TOUCHED] — 全程在 worktree（.worktrees/agate-TAG0006/）开发，未触碰主 checkout 或 ~/.agate 生产环境。
