---
phase: P6
task_id: TAG0014-dispatch-orchestration
type: acceptance
parent: P5-verification.md
trace_id: TAG0014-P6-20260816
status: draft
created: 2026-08-16
agent: verifier
# ── v2.0 机器汇总 ──
pass: 22
fail: 0
ui_affected: false
---

[PROD_NOT_TOUCHED]

# P6 验收报告 — agate 派发编排机制（TAG0014-dispatch-orchestration）

> 验收口径：对照 P1-requirements.md §4 全部 22 条 BDD 逐条实跑（脚本类跑命令、文档类 grep 锚点），二值判定 PASS/FAIL。非 UI 任务，ui_affected: false。所有 PASS 均基于 P6-evidence/ 实际输出，无"应该能过"推断。

**Summary**: 22/22 PASS, 0 FAIL

## BDD 逐条验收结果

- PASS BDD-1: dispatch_plan 支持单行 flow YAML 且 mode 为五值枚举 (bdd-1.log) — `agate-md-field-get.py dispatch_plan` 对含 flow YAML 文件输出合法 JSON（json.loads round-trip 成功），mode ∈ {single, static-batch, parallel, recon-then-split, serial} 五枚举逐一验证通过
- PASS BDD-2: 无 dispatch_plan 字段时行为完全等同现状 (bdd-2.log) — check-gate P2 对含合法 dispatch_plan 与无字段的 task_dir 输出逐行一致（diff 为空）、exit code 同为 2，无新增 ERROR/WARNING
- PASS BDD-3: P2 gate 拦截非法 mode 值 (bdd-3-4.log) — `mode: xyz` → stderr `GATE P2 ERROR: dispatch_plan.mode 非法` + exit 1
- PASS BDD-4: P2 gate 拦截 parallel_limit < 1 (bdd-3-4.log) — `parallel_limit: 0` → `GATE P2 ERROR: dispatch_plan.parallel_limit 非法` + exit 1
- PASS BDD-5: P2 gate 校验 batch 必填字段与 complexity 枚举 (bdd-5-6.log) — 双子场景均验：① batch 缺 complexity → `ERROR batch 'B1' 的 complexity 非法（None）` + exit 1；② complexity 非法值（invalid）→ `ERROR ... complexity 非法（'invalid'）` + exit 1
- PASS BDD-6: P2 gate 拦截 batch 数超过 parallel_limit (bdd-5-6.log) — 4 批 > 上限 3 → `ERROR 批次数（4）超过 parallel_limit（3）` + exit 1
- PASS BDD-7: dispatch_plan YAML 解析失败时不误拦、不崩溃 (bdd-7.log, bdd-7-gate.log) — 坏 YAML（`{mode: [unclosed`）op 输出空 + exit 0；gate 输出与无字段基线 diff 为空、exit 2，无新增 ERROR
- PASS BDD-8: 权威节含工作量评估方法 (bdd-8-12.log) — dispatch-protocol L647「1. 工作量评估（五维评级）」含产出规模/输入规模/改动性质/耦合度/认知负荷五维表 + low/medium/high 分级与综合定级规则
- PASS BDD-9: 权威节含五模式编排定义 (bdd-8-12.log) — L661「2. 五模式编排」含模式 1-5（单发/静态拆批/并行/先理解后拆/串行链），每模式含"何时用 + 流程"两列
- PASS BDD-10: 模式 4（先理解后拆）流程完整 (bdd-8-12.log) — L671「3. 模式 4 流程」含① 侦察 subagent 读全貌产出拆分方案（含 BDD 全局编号/包归属去重合并语义）→ ② 执行 → ③ 合并，且含可运行文档样例（recon-then-split YAML）
- PASS BDD-11: 并行规则含三要素 (bdd-8-12.log) — L691「4. 并行规则」含① 并行上限默认 3（parallel_limit 可覆盖）② 失败批 retry 与 retries[Pn] 对齐（默认整组计 1 次）③ 共享文件统一后处理（P6 例外走自身汇总 verifier）
- PASS BDD-12: 全阶段适用表覆盖 P1-P8 (bdd-8-12.log) — L697「5. 全阶段适用表」P1-P8 每阶段有编排模式参考；P2 = 单发 + dispatch_plan 产出（非 P2 自身拆分）、P7 = 模式 1 单发 + 输入豁免特例（非串行链）、P8 = 多包可拆批 + 合并机制
- PASS BDD-13: P3/P4/P5/P6 卡片「按包拆分并行」引用权威节且保留阶段特定约束 (bdd-13.log) — 四卡均含"见 dispatch-protocol「派发编排机制」并行规则"引用；P3 保留拆分判据、P4 保留共享文件后处理/基础设施隔离/串行安全默认值、P5 保留端口/数据库/临时输出隔离、P6 保留证据并行 + 汇总 verifier 整合唯一 P6-acceptance.md
- PASS BDD-14: P7 不拆分例外表述更新 (bdd-14-16.log) — P7 卡片「P7 输入文件数量」含"模式 1 单发 + 输入数量豁免特例，见 dispatch-protocol「派发编排机制」全阶段适用表"表述，原有跨文件一致性理由保留
- PASS BDD-15: P1 卡片含编排模式引用 (bdd-14-16.log) — P1 卡片 L39「复杂需求编排（模式 4）」含"先派侦察 subagent 再拆"引用，合并语义（BDD 全局编号、包归属去重）在侦察产出中定义
- PASS BDD-16: P8 卡片含多包拆批与合并机制 (bdd-14-16.log) — P8 卡片 L33「多包发布拆批（模式 2/3）」含各 releaser 写 P8-release-{pkg}.md → 合并 subagent 整合唯一 P8-release.md 机制
- PASS BDD-17: architect.md 含批次设计强制节 (bdd-17-18.log) — architect.md L139「批次设计（强制节，TAG0014）」：P2 方案含多个独立子任务时必须输出 `dispatch_plan:`（模式+批次表+并行上限）；high 复杂度必须拆分
- PASS BDD-18: dispatch-prompt.md 粒度兜底与协议权威源同步 (bdd-17-18.log) — dispatch-prompt.md L40 与 dispatch-protocol「派发 prompt 模板」内联节 L472 均含"产出文件 >3 或输入文件 >5 时必须分批派发或明确说明为何不分批"；dispatch-prompt.md L4 保留"与协议文件保持同步、协议为权威来源"声明
- PASS BDD-19: 新增 dispatch_plan 契约测试全部通过 (bdd-19.log) — `test_dispatch_orchestration.py` 10 条全 PASS（5 正向 + 5 负向，含修复轮补强），10 passed in 1.02s；`test_agate_md_field_get.py` 16 passed（含 2 条新 op 用例）
- PASS BDD-20: 全量 pytest 全绿且用例数不漂移 (bdd-20-21.log, test-output.log) — 全量 `780 passed, 2 skipped` exit 0；count-tests.sh 统计 782 个用例 ≥ 基线 770 + 10 新增
- PASS BDD-21: consistency 检查 0 ERROR (bdd-20-21.log, test-output.log) — `check-protocol-consistency.py` 输出"仅有 280 个 WARNING，无 ERROR"，exit 0；CHECK 3 硬编码行号/锚点引用未因「任务粒度指引」改名误报
- PASS BDD-22: 协议/脚本改动 commit 均走 self-gate-review 流程 (bdd-22.log) — 唯一命中 self-gate 触发文件（agate/*.md + scripts/*.py + phase-cards，15 个文件）的 commit 772bbc2（P4）message 含 `self-gate-review: docs/reviews/agate-alignment-review-TAG0014.md`；全量扫描无改动 agate 协议/脚本但缺标记的 commit；protocol-alignment-review 派发记录由 P7 产出审查报告承接

## 证据清单

- P6-evidence/test-output.log — 验收命令综合执行日志（op 契约 + gate 负向 + 全量 pytest + count-tests + consistency，尾行 EXIT_CODE: 0）
- P6-evidence/bdd-{1,2,3-4,5-6,7,7-gate}.log — BDD-1~7 脚本类验收输出（op 输出 / gate exit code / stderr 内容 / diff 对比）
- P6-evidence/bdd-{8-12,13,14-16,17-18}.log — BDD-8~18 文档类 grep 锚点证据（含行号）
- P6-evidence/bdd-19.log — test_dispatch_orchestration.py 10 条 PASSED + test_agate_md_field_get.py 16 passed
- P6-evidence/bdd-20-21.log — 全量 pytest / count-tests / consistency 输出
- P6-evidence/bdd-22.log — git log self-gate-review 标记扫描

## 验收说明

- 本任务非 UI，ui_affected: false，P2 声明一致，无需 vision-analyst
- consistency 验收用"0 ERROR"判定（dispatch-context 客观查证信息）：280 WARNING 均为既有叙事文件引用（引述旧路径/脚本名），非本任务引入；默认模式（非 --strict）exit 0
- BDD-22 中 P1/P2/P3/P5 commit（aaf817d/c70772f/52fd115/eb48440/792096b/5ad94da）不改动 agate 协议/脚本/卡片，不在 self-gate 触发面内，无需 self-gate-review 标记；唯一触发面 commit 772bbc2 已含标记
