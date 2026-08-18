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

**G-4（更正）：P8 `tag v0.51.0` 未 push 到 origin 致 CI CHECK 7 失败**（PR 合并阶段，真实根因）
- 现象：PR 156 的 CI `pytest` 3 个 consistency 测试失败（`test_con_6_check_7_version_badge_sync` 断言 `PASS CHECK 7`）。本地/干净 checkout 均 0 ERROR、CHECK 7 PASS，但 CI 失败。
- **真实根因**：本地打了 tag `v0.51.0`，但 push 分支时**用了 `git push` 未加 `--tags`，tag 从未推送到 origin**。CI 在 `pull_request` merge ref 环境 `git describe --tags --abbrev=0` 只能找到 origin 上的 `v0.50.0`，而 README badge 已是 `v0.51.0` → CHECK 7 报 `badge v0.51.0 != tag v0.50.0` → FAIL。
- 早期诊断偏差：本复盘初稿把此现象写成"release PR merge-ref 必红"（误判）；随后 `FIX-YAML-PR156.md` 又误判为"YAML 块 Python 3.10 解析 bug"（实际 CHECK 1 一直 PASS）。**真根因是 tag 未 push**，补 `git push origin v0.51.0` + rerun PR 后 CHECK 7 转绿。
- 归因：**机制缺口**——发布流程（AGENTS.md 版本发布清单）写了"tag + push"，但没有显式强调"`git push --tags` 或逐个 `git push origin vN.N.N` 必须执行 + 验证 `git ls-remote --tags origin` 确认 tag 到达远端"。`git push` 默认不推 tag，是杯静默失败点（本地 tag 存在、远端缺失，本地验证全绿但 CI 红）。
- 措施：`git push origin v0.51.0`（已做）+ rerun PR（已做）。**建议**：P8 发布清单补"push tag 并 `git ls-remote --tags origin <tag>` 验证远端存在"显式步骤 + CHECK 7 失败解读指南（本地绿 CI 红 → 先查 tag 是否推送，勿臆测 YAML）。

**G-5：发布后缺少"合并产物最终验证"的显式步骤**
- 现象：合并 PR、`git describe origin/main` = v0.51.0、tag 为 main 祖先均需手动逐条查证；若未验证就易静默引入"tag 未推送"这类问题。
- 归因：**机制缺口**——release 合并后的 verify 步骤（describe + tag 祖先 + 合并后 push CI 全绿）在 AGENTS.md/交接单里是推荐项非强制 checklist。
- 措施：已手动逐条验证（见 §4）。**建议**把"合并后 main describe = 目标版本 + tag 为 main 祖先 + 合并后 push CI 全绿"固化为 max release PR 合并后的强制清单。

### 3.2 执行层（主 Agent/subagent 未遵守规则，→ 修纪律）

**E-1：`.state.yaml` 多次 YAML 冒号语法错误**（P1/P4）
- reason/adjustment 字段含半角冒号（`design:`/`backend:`）触发 YAML mapping 错误，pre-commit 拦截。
- 归因：**执行错误**（写 YAML 值未加引号）。
- 措施：YAML 值含半角冒号/特殊字符时加引号（已做）。**建议 protocol 审查替代/主 Agent 提醒。**

**E-2：plan-design-review SCOPE 复审空返回**（P2）
- subagent 完成复审但产出文件未落盘（空返回），progress 显示已判定需 recovery 恢复会话落盘。
- 归因：**执行层**（subagent 未写文件即返回，符合空返回恢复流程，已正确走 resume 路径）。
- 措施：通过 task resume 恢复落盘（已做）。

**E-3：CI 失败未拉日志即臆测根因，产出错误诊断文档**（PR 合并阶段）
- PR 156 的 consistency pytest 失败时，先被误判为"release PR merge-ref 必红"（交接单），又被 `FIX-YAML-PR156.md` 误判为"YAML 块 Python 3.10 解析 bug"——**两个都错**。实际拉出 CI 完整日志后，明确看到 `❌ FAIL CHECK 7 version badge 与 git tag`（非 YAML，CHECK 1 一直 PASS），再核对 `git ls-remote --tags origin` 发现 `v0.51.0` tag 未推送。
- 归因：**执行错误**——未第一时间拉 CI job 完整日志看真实 FAIL 的 CHECK 归属，靠猜测（本 repo 历史"release PR CHECK 7 红"记忆 + YAML 版本差异假设）而非证据。
- 措施：拉全日志（`gh api .../actions/jobs/{id}/logs`）+ 核对远端 tag 后定位真根因（已做）。**教训**：CI 一致性失败必须先看 `CHECK N` 归属与远端 tag 状态，**禁止在未看日志前臆测**（理性应遵循 systematic-debugging：先看证据再下结论，不靠历史先例或表面版本差异猜测）。`FIX-YAML-PR156.md` 的错误诊断应作废或更正为实际根因。

---

## 4. 改进措施（落到文件/字段/gate）

| 措施 | 落点 | 状态 |
|------|------|------|
| gate_commands.P3 语义文档化（check-tdd-red 需执行输出）| P3 卡片注释已改（本任务内）| ✅ 已做 |
| P8 tag push 显式验证（`git push origin vN` + `git ls-remote --tags origin` 确认）| AGENTS.md 版本发布清单 / P8 卡片 | ⏳ 建议（本次已手动补 push tag）|
| P8 版本 bump 顺序（badge+tag 同批，P5 重跑在 tag 后）| P8 卡片/AGENTS.md 版本发布清单 | ⏳ 建议 |
| 合并后 main 验证清单（describe + tag 祖先 + 合并后 push CI 全绿）| max release PR 合并后强制清单 | ⏳ 建议 |
| CI consistency 失败先看 `CHECK N` 归属 + 远端 tag，勿臆测 | 团队纪律（systematic-debugging 原则）| ⏳ 建议文档化 |
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
