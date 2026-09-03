---
phase: P3
task_id: TAG0030
type: test-design
parent: P2-design.md
trace_id: TAG0030-P3-20260904
status: draft
created: '2026-09-04'
agent: test-designer
test_code_dir: agate/tests/unit/
---
# P3-test-cases — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）断言审计测试设计

> 测试策略：grep 断言审计（TAG0027 批量改动 TDD 策略）——读协议文件文本 + 关键词 `in` 判断，
> 锁定 P2-design §2 / §0.1 落点锚词。测试文件路径已由 P2 §5 gate_commands.P3 固化：
> `agate/tests/unit/test_tag0030_assertions.py`（不得另起文件名）。
> 当前协议文件尚未被本任务改动，全部用例当前失败（红灯）——P4 逐条落地后转绿（BDD-6 回归防线）。
> 纯协议文档面改造，不涉及生产环境 `[PROD_NOT_TOUCHED]`。

## 0. 测试代码目录

- `test_code_dir: agate/tests/unit/`（含 `agate/tests/unit/test_tag0030_assertions.py`）
- 模式源：`test_review_role_docs.py`（`_read_repo` 逐条 assert）+ `test_protocol_mechanism_anchors.py`（锚词纪律）
- 路径基座：相对仓库根（`agate_root.parent`）；AGENTS.md 在仓库根（不在 agate/ 内，P2-review G2）

## 1. 假绿核实结论（写每条用例前逐词核实当前命中数）

| 目标文件 | 当前已命中关键词（假绿点） | 处理 |
|---|---|---|
| `agate/phase-cards/P3-tdd.md` | 无（清理钩子/创建即注册/无条件删除/200/204/404 均 0 命中） | 直接断言，真红 |
| `agate/phase-cards/P4-implementation.md` | 无（清理钩子/创建即注册 0 命中） | 直接断言，真红 |
| `agate/phase-cards/P6-acceptance.md` | 无（残留检查/post-test 0 命中） | 直接断言，真红 |
| `agate/phase-cards/P1-requirements.md` | 无（人工体验/seed/页面有内容 0 命中） | 直接断言，真红 |
| `agate/assets/execution-roles/analyst.md` | 无（人工体验/seed 0 命中） | 直接断言，真红 |
| `agate/assets/review-roles/plan-design-review.md` | **布局型（行 19）、渲染正确性/动效时序/形态（行 21）、0-10（行 13）、status（行 32-35）** | BDD-10/11/12/14/15 改 AND 语义，至少一个当前 0 命中新锚词兜底（ui_render_shape/三组/渲染组件型+architect/原文保留/回落） |
| `agate/assets/execution-roles/architect.md` | **对齐（行 111 时间戳对齐、行 221 批次边界对齐，语义不同）** | BDD-16/17 不用「对齐」作唯一锚词，改用视觉契约/可表达子集/不收主观视觉 |
| `agate/assets/execution-roles/verifier.md` | 无（DOM 度量/getBoundingClientRect 0 命中） | 直接断言，真红 |
| `agate/assets/templates/dispatch-context.md` | 无（清理/残留/环境还原/拆小/体量/>5 文件 0 命中） | 直接断言，真红 |
| `agate/tests/README.md` | 无（真实 gate 语义 0 命中） | 直接断言，真红 |
| `AGENTS.md`（仓库根） | 无（全量扫描/新增 CHECK 0 命中） | 直接断言，真红 |

## 2. 用例清单（BDD-1~21 全覆盖 1:1，测试名含 test_bdd_N_）

### Phase 1（BDD-1~6）：测试副作用/环境还原 gate（RM-AG0057-①）

| 用例（测试名） | BDD | 目标文件 | 锚词（逐字复用 P2 §2/§0.1） | 当前状态 → P4 后 |
|---|---|---|---|---|
| test_bdd_1_p3_card_cleanup_hook | BDD-1 | agate/phase-cards/P3-tdd.md | 清理钩子 + 创建即注册 | 红 → 绿（P3 卡 step0 补清理钩子要求段） |
| test_bdd_2_p4_card_cleanup_hook | BDD-2 | agate/phase-cards/P4-implementation.md | 清理钩子 + 创建即注册 | 红 → 绿（P4 卡 step0 镜像同段） |
| test_bdd_3_cleanup_delete_semantics | BDD-3 | agate/phase-cards/P3-tdd.md | 无条件删除 + 200/204/404 | 红 → 绿（afterEach 清理队列模式语义） |
| test_bdd_4_p6_residue_check | BDD-4 | agate/phase-cards/P6-acceptance.md | 残留检查 + post-test | 红 → 绿（P6 卡验收流程补残留检查步骤） |
| test_bdd_5_dispatch_context_cleanup_slot | BDD-5 | agate/assets/templates/dispatch-context.md | 环境还原 + 残留检查 | 红 → 绿（模板约束节补条目位） |
| test_bdd_6_phase1_audit_lock | BDD-6 | P3/P4/P6 卡 + dispatch-context 模板 | 清理钩子 + 残留检查 + 环境还原（汇总 BDD-1/2/4/5 载体） | 红 → 绿（回归防线：条文被删即转红） |

### Phase 2（BDD-7~9）：P1 人工体验路径验收节（RM-AG0057-②）

| 用例（测试名） | BDD | 目标文件 | 锚词（逐字复用 P2 §2/§0.1） | 当前状态 → P4 后 |
|---|---|---|---|---|
| test_bdd_7_p1_card_manual_experience | BDD-7 | agate/phase-cards/P1-requirements.md | 人工体验 + seed | 红 → 绿（P1 卡产出规格补「人工体验路径验收」节） |
| test_bdd_8_analyst_manual_experience | BDD-8 | agate/assets/execution-roles/analyst.md | 人工体验 + seed | 红 → 绿（analyst 输出节补同源句） |
| test_bdd_9_seed_content_bdd_required | BDD-9 | agate/phase-cards/P1-requirements.md | seed 数据 + 页面有内容 | 红 → 绿（「Given seed 数据 → 页面有内容」强制句式） |

### Phase 3（BDD-10~15）：plan-design-review 形态驱动化（RM-AG0057-③）

| 用例（测试名） | BDD | 目标文件 | 锚词（逐字复用 P2 §2/§0.1） | 当前状态 → P4 后 |
|---|---|---|---|---|
| test_bdd_10_shape_dispatch_header | BDD-10 | agate/assets/review-roles/plan-design-review.md | ui_render_shape + 维度组 | 红 → 绿（评分维度节首加形态分派头；「形态」已命中故不用） |
| test_bdd_11_layout_dimension_group | BDD-11 | agate/assets/review-roles/plan-design-review.md | 布局型 + 三组 | 红 → 绿（布局型三组 = 布局/交互/视觉；「布局型」行 19 已命中 → AND「三组」兜底） |
| test_bdd_12_render_component_group | BDD-12 | agate/assets/review-roles/plan-design-review.md | 渲染组件型 + architect | 红 → 绿（渲染组件组 + 交叉引用 architect 渲染 checklist；「渲染正确性/动效时序」行 21 已命中 → 换「渲染组件型+architect」） |
| test_bdd_13_two_candidates_tradeoff | BDD-13 | agate/assets/review-roles/plan-design-review.md | 候选 + 权衡 | 红 → 绿（≥2 候选 + 权衡说明，candidate_count 下沉 UI 布局层） |
| test_bdd_14_score_status_preserved | BDD-14 | agate/assets/review-roles/plan-design-review.md | 0-10 + status + 原文保留 | 红 → 绿（0-10/status 已命中 = 保持性断言；AND「原文保留」P2 §2 逐字锚词，当前 0 命中保整体为假） |
| test_bdd_15_default_layout_fallback | BDD-15 | agate/assets/review-roles/plan-design-review.md | 回落 + 布局型 | 红 → 绿（无形态声明回落布局型默认；「布局型」已命中 → AND「回落」兜底） |

### Phase 4（BDD-16~21）：视觉契约断言收录 + DEBT0024/25/26

| 用例（测试名） | BDD | 目标文件 | 锚词（逐字复用 P2 §2/§0.1） | 当前状态 → P4 后 |
|---|---|---|---|---|
| test_bdd_16_visual_contract_expressible | BDD-16 | agate/assets/execution-roles/architect.md | 视觉契约 + 可表达子集 | 红 → 绿（视觉 checklist 头部单源定义，P2 §3 pin 定 architect.md） |
| test_bdd_17_architect_checklist_dom_metric | BDD-17 | agate/assets/execution-roles/architect.md | DOM 度量 + 不收主观视觉 | 红 → 绿（同文件一次落笔；「对齐」已命中（行 111/221 语义不同）故不作锚词） |
| test_bdd_18_verifier_dom_evidence | BDD-18 | agate/assets/execution-roles/verifier.md | DOM 度量 + getBoundingClientRect | 红 → 绿（证据形式指南补非截图量化证据句，P2 §3 pin 定 verifier.md） |
| test_bdd_19_real_gate_semantics | BDD-19 | agate/tests/README.md | 真实 gate 语义 | 红 → 绿（「何时更新」节补真实 gate 语义句，DEBT0024 closure） |
| test_bdd_20_full_scan_before_check | BDD-20 | AGENTS.md（仓库根） | 全量扫描 + 新增 CHECK | 红 → 绿（「改脚本的工作流」节首补第 0 步，DEBT0025 closure） |
| test_bdd_21_split_by_volume | BDD-21 | agate/assets/templates/dispatch-context.md | 拆小 + 体量 | 红 → 绿（>5 文件/大文档按体量评估拆小默认指导，DEBT0026 closure） |

## 3. 平台无关与运行

- 全部用例：`Path.read_text(encoding="utf-8")` + `in`，无 shell grep、无 /tmp、无裸 python3
- `windows_smoke` 标记：Phase 1~4 首用例已标（BDD-1/7/10/16 代表四条 phase 面）；平台无关断言全平台可跑
- 运行命令（P2 §5 gate_commands.P3 固化）：`python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`
- 验证结果：21 条用例当前全部失败（B 类 assertion 红灯），无 A 类错误（无 SyntaxError / 未装第三方依赖 import）

## 4. P4 落笔注意（供 implementer）

- 锚词逐字复用本文件 §2 表格（不意译）——P4 落地词与 P3 断言词一致，测试才转绿
- plan-design-review.md 落笔禁动：CHECK11 三锚词（视觉设计/交互设计/渲染正确性与时序，consistency 行 910-911）只增不删；0-10 分值行与 status 映射行原文保留（BDD-14 断言「原文保留」四字句）
- role-system.md 行 47 七维描述须同步形态驱动口径（连带同步点，P7 核对）
- commit message 含 `self-gate-review:`（SELF-GATE 触发面：phase-cards + assets + 模板）
- UPGRADING.md 新增 v0.68 版本章节（无破坏性声明 + 新条文摘要）+ CHANGELOG Unreleased 同步
