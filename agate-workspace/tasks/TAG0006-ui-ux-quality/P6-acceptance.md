---
phase: P6
task_id: TAG0006-ui-ux-quality
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0006-P6-20260817
status: draft
created: 2026-08-17
agent: verifier
# ── v2.0 机器汇总 ──
pass: 17
fail: 0
ui_affected: false
---

# P6 — 验收报告（agate UI/UX 验收质量机制）

> 本任务为 **agate 协议本体增强**（dogfooding），ui_affected: false（协议机制增强，无真实 UI 产物）。
> 验收方式（P1 §3）：客观证据 = ① 对应协议文档/角色文件含该行为要求（grep 于 `bdd-doc-anchor-grep.log` + 各测试附带的文档断言）；② 对应 gate 脚本单测（pytest）覆盖并断言该行为。二者兼备才允许 PASS。
> 环境标记：`[PROD_NOT_TOUCHED]` 全部验证在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0006/）内执行，未触碰主 checkout 与 ~/.agate。

## 执行摘要

- 目标测试模块：`test_check_gate.py`、`test_check_p6_evidence.py`、`test_check_p6_provenance.py`、`test_review_role_docs.py`、`test_dispatch_orchestration.py`（258 passed，见 test-output.log）
- 全量回归（BDD-15）：881 passed, 2 skipped, 0 failed（P6-evidence/bdd15-full-regression.log）
- consistency：0 ERROR（P6-evidence/bdd15-consistency.log）
- count-tests：883 收集 ≥ 749 目标，无漂移（P6-evidence/bdd15-count-tests.log）
- 17 条 BDD 全部 PASS，0 FAIL。

**Summary**: PASS: 17, FAIL: 0 (17/17), redacted AC.

## P1 组 — UX 需求基线 / 能力识别（BDD-1/2/3）

- PASS BDD-1: frontend 任务 P1 必须含 UX 类别 BDD（从分类框架按形态选适用维度）——analyst.md 明文含「UX 类别 BDD 与分类框架」（渲染形态声明 + 维度选择 + 至少一条可二值判定 UX BDD，缺失时 requirements-review 打回），P1 卡片含分类框架条文；单测 test_bdd_1_analyst_classification_framework / test_bdd_1_p1_card_classification_framework 断言文档含分类框架与形态适配要求 (P6-evidence/bdd-doc-review-role-docs.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-2: UX 类别 BDD 可二值判定且不绑定具体实现/技术栈——analyst.md BDD 反模式自检清单含「可二值判定/无主观形容词/不绑定 CSS/工具/技术栈」「渲染正确性/时序/动效/手势判据可量化」条文（渲染结果对比/帧时序/动画关键帧/手势坐标量化）；单测 test_bdd_2_analyst_quantitative_criteria 断言 (P6-evidence/bdd-doc-review-role-docs.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-3: ui_affected 任务 P1 必须声明 vision 能力三态——check-gate.py 新增 `_gate_p1_vision_capability`（domains 含 frontend → capability_requirements 视觉条目缺失/非法 status → exit 1）；analyst.md:105-109 + P1 卡片:123-124 明文；单测 test_vision_1_frontend_missing_capability_exit_1 / test_vision_2_frontend_invalid_status_exit_1 / test_vision_3_frontend_valid_gap_exit_2 / test_vision_4_backend_no_vision_no_fail_exit_2 断言 exit 行为 (P6-evidence/bdd3-p1-vision-tri-state.log, P6-evidence/bdd-doc-anchor-grep.log)

## P2 组 — UI 设计节 / 评审维度 / GUI 评估 / 影响面（BDD-4/5/6/7/8）

- PASS BDD-4: ui_affected 任务 P2-design.md 必须含「UI 设计」节（按渲染形态适配）——check-gate.py 新增 `_gate_p2_ui_design_section`（ui_affected:true 缺节/缺形态声明 → exit 1；含布局/交互/视觉三类；形态一致性按规范值比对）；单测 test_ui_design_1~12 覆盖缺节/缺形态/三类 checklist/规范值与同义映射匹配/形态不一致拦截 (P6-evidence/bdd4-p2-ui-design-section.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-5: UI 设计节由 architect 兼任产出（不新增 designer 角色）——architect.md 明文「UI 设计节由 architect 兼任产出，不新增 designer 角色」+ 结构规格；role-system.md 声明兼任且不新增角色；单测 test_bdd_5_architect_ui_design_section / test_bdd_5_role_system_architect_dual_hats 断言 (P6-evidence/bdd-doc-review-role-docs.log)
- PASS BDD-6: plan-design-review 评审维度含视觉/交互/渲染形态适配维度——plan-design-review.md 维度表含「视觉设计」「交互设计细节」「渲染正确性与时序」各 0-10 可判定评分项；单测 test_bdd_6_plan_design_review_dimensions 断言 (P6-evidence/bdd-doc-review-role-docs.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-7: P2 必须执行 Windows GUI 自动化框架评估——P2-design.md §4 独立小节列出 WinAppDriver/AutoIt 评估表 + 结论「保持现状（调研非实测）」，明确不写「已实测 Windows」（grep 确认无实测声称）；文档验证 (P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-8: P2-design.md 必须含影响面核对清单——P2-design.md §6 含「影响面核对清单」逐项列出 45 文件/64 处联动点与同步动作，对齐 P1 影响面清单；grep 命中 (P6-evidence/bdd-doc-anchor-grep.log)

## P6 组 — 双证据 / 视觉质量 / 能力消费 / 降级链（BDD-9/10/13/14）

- PASS BDD-9: P6 UI 任务强制双证据 + 视觉质量 checklist（三态分档 + 证据形式按形态可选）——verifier.md 明文「双证据 + 视觉能力三态分档」（available/supplementable → vision YAML；GAP → 像素检测 + 人工复核记录不要求 vision YAML）+ 视觉质量 checklist 核对 + 证据形式按形态清单（帧序列/时序截图/渲染输出对比）；单测 test_vision_gap_1/2、test_vision_docs_1_verifier_has_triple_state、test_vision_gap_prov_1/2、test_vision_avail_1、test_vision_none_1 断言分档语义 (P6-evidence/bdd-p6-evidence-provenance.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-10: vision 能力 available 时 P6 必须真实视觉分析——verifier.md + P6 卡片明文「p1 显式声明 status=available 时必须执行真实视觉分析（截图/帧序列/渲染输出 → 结构化描述 → 判定），不得仅以 naturalWidth>0/complete/HTTP 200/像素方差断言」；单测 test_vision_docs_2_p6_card_real_analysis 断言 (P6-evidence/bdd-p6-evidence-provenance.log, P6-evidence/bdd-doc-anchor-grep.log)
- PASS BDD-11: vision 能力 supplementable 时派发 prompt 注入获取指引——dispatch-prompt.md 能力补充说明节明文「视觉能力 supplementable 时获取指引必须注入本任务语境（ui_affected:true 任务 P6 派发注入 vision-analyst/skill 调用指引）」；dispatch-protocol.md A3 扩展；单测 test_bdd_11_dispatch_prompt_injection_guidance / test_bdd_11_dispatch_protocol_a3_vision 断言 (P6-evidence/bdd-doc-review-role-docs.log)
- PASS BDD-12: 派发 prompt 强制 subagent 能力自查——dispatch-prompt.md「能力自查（强制，BDD-12）」节明文「先自查能否调用视觉能力，不能则报告 [CAPABILITY_GAP] 走降级路径，不静默假设」；单测 test_bdd_12_dispatch_prompt_self_check 断言 (P6-evidence/bdd-doc-review-role-docs.log)
- PASS BDD-13: 输入态/交互形态变化类用例人工复核——verifier.md + P6 卡片明文判定标准（输入态类/交互形态类 BDD 结论必须附人工复核记录，不能仅由自动断言通过）+ PASS 行样例；单测 test_vision_docs_3_input_state_review、test_bdd_13_verifier_input_state_review、test_bdd_13_p6_card_input_state_review 断言 (P6-evidence/bdd-p6-evidence-provenance.log, P6-evidence/bdd-doc-review-role-docs.log)
- PASS BDD-14: 雷同截图降级待复核——check-p6-evidence.py avg-hash 重复改为「降级待复核」判定（含人工复核记录 → exit 0/放行；无记录 → exit 1 阻断，非纯 WARNING）；md5 硬阻断不变；帧序列/时序截图按 BDD 组豁免；单测 test_ahash_1_duplicate_with_review_record_exit_0 / test_ahash_2_duplicate_no_review_record_exit_1 / test_ahash_3_no_duplicate_exit_0 / test_time_seq_1 / test_ahash_4 断言行为改变 (P6-evidence/bdd14-ahash-degradation.log, P6-evidence/bdd-doc-anchor-grep.log)

## 兼容/回归组（BDD-15）

- PASS BDD-15: 基线回归不破坏既有 gate 语义——全量 pytest 881 passed, 2 skipped, 0 failed（既有 823 基线 + 新增用例全绿）；consistency 0 ERROR；count-tests 883 ≥ 749 单调不减无漂移；既有 P6 vision-helper/blocker_count/R1b/二值 PASS/FAIL 语义保持不变（test_vision_avail_1 守护基线 R1b 语义） (P6-evidence/bdd15-full-regression.log, P6-evidence/bdd15-consistency.log, P6-evidence/bdd15-count-tests.log, P6-evidence/test-output.log)

## SCOPE+ 扩展组（BDD-16/17）

- PASS BDD-16: 渲染组件类与 UX 交互形态维度进入 BDD 可测项——analyst.md + P1 卡片明文要求渲染组件型形态（渲染正确性/时序/动效/手势交互）与 UX 交互形态（动作/特效/时序）产出可二值判定 BDD，判据可量化、不绑定技术栈；单测 test_bdd_16_render_component_dim_requirements + test_ui_design_5_ui_true_render_comp_section_exit_2 等断言 (P6-evidence/bdd-doc-review-role-docs.log, P6-evidence/bdd4-p2-ui-design-section.log)
- PASS BDD-17: 渲染组件类验收的证据形式可按项目形态选择——verifier.md + P6 卡片明文证据形式按形态可选（渲染组件型：帧序列/时序截图/渲染输出对比；常规布局型：截图/行为日志），不绑定具体工具；单测 test_bdd_17_verifier_evidence_form_by_shape、test_bdd_17_p6_card_evidence_form_by_shape、test_render_evid_1/2/3/4、test_render_diff_1/2 断言证据类型识别与形态适配 (P6-evidence/bdd-doc-review-role-docs.log, P6-evidence/bdd-p6-evidence-provenance.log)

## 自查（非 gate）

以上为 verifier 自查结果，P6 gate（check-gate.py P6 + check-p6-evidence.py + check-p6-provenance.py）由主 Agent 亲自运行判定。
