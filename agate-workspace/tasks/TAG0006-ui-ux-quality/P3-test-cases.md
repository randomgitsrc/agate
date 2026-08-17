---
phase: P3
task_id: TAG0006-ui-ux-quality
type: test-cases
parent: P2-design.md
trace_id: TAG0006-P3-20260817
status: draft
created: 2026-08-17
agent: test-designer
---
test_code_dir: agate/tests/

# P3 测试用例清单 — agate UI/UX 验收质量机制

> 上游：P2-design.md §2.1-2.16（每 BDD 已定义 gate 逻辑 + 单测规格）+ P1-requirements.md 17 BDD。
> 测试对象 = gate 脚本（check-gate.py / check-p6-evidence.py / check-p6-provenance.py）+ 协议文档（analyst.md / architect.md / verifier.md / plan-design-review.md / role-system.md / P1/P6 卡片 / dispatch-protocol.md / dispatch-prompt.md）。
> P4 实现前全部新增用例为红灯（或部分为既有行为正例/回归守卫，见 §3 说明）；P4 实现后转绿。

## 1. 落点文件

| 落点 | 新增用例数 | 覆盖 BDD |
|------|-----------|----------|
| `agate/tests/unit/test_check_gate.py`（追加） | 20 | BDD-3 / BDD-4 / BDD-16（`_gate_p1_vision_capability` / `_gate_p1_ui_shape` / `_gate_p2_ui_design_section`） |
| `agate/tests/unit/test_check_p6_evidence.py`（追加） | 15 | BDD-9 / BDD-10 / BDD-13 / BDD-14 / BDD-17 |
| `agate/tests/unit/test_check_p6_provenance.py`（追加） | 4 | BDD-9（R1b GAP 放宽 + 回归守卫） |
| `agate/tests/unit/test_review_role_docs.py`（新增） | 14 | BDD-1 / BDD-2 / BDD-5 / BDD-6 / BDD-11 / BDD-12 / BDD-13 / BDD-16 / BDD-17 |

合计 **53** 个新增用例。基线 825 → 878（只增不减）。

## 2. BDD → 测试用例映射（1:1）

### 2.1 BDD-3（P1 gate vision 三态）→ 4 用例（test_check_gate.py）

| 用例名 | 构造 | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_vision_1_frontend_missing_capability_exit_1 | P1 `domains: [frontend]` + 无 capability_requirements → gate P1 | exit 1，输出含 "vision" | 🔴（现 exit 2） |
| test_vision_2_frontend_invalid_status_exit_1 | P1 frontend + capability 块 `status: invalid` → gate P1 | exit 1 | 🔴（现 exit 2） |
| test_vision_3_frontend_valid_gap_exit_2 | P1 frontend + `status: GAP` → gate P1 | exit 2（GAP 合法声明，不阻 P1） | 🟢（兼容正例） |
| test_vision_4_backend_no_vision_no_fail_exit_2 | P1 `domains: [backend]` 无 vision → gate P1 | exit 2（不触发） | 🟢（兼容） |

### 2.2 BDD-16（P1 gate 形态声明合法性 `_gate_p1_ui_shape`）→ 7 用例（test_check_gate.py）

| 用例名 | 构造（均 domains=frontend + valid vision=available 隔离 BDD-3） | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_shape_1_shape_no_dimensions_exit_1 | `ui_render_shape: render_component` + `ui_ux_dimensions: []` | exit 1（声明形态但维度空） | 🔴（现 exit 2） |
| test_shape_2_shape_with_valid_dims_exit_2 | shape + `ui_ux_dimensions: [渲染正确性]`（框架内） | exit 2 | 🟢（正例） |
| test_shape_2b_shape_missing_dims_present_exit_2 | 无 shape + dims `[渲染正确性]` | exit 2（shape 缺失维度存在 → 允许） | 🟢（正例） |
| test_shape_3_no_shape_backend_exit_2 | domains=backend 无形态字段 | exit 2（不触发） | 🟢（兼容） |
| test_shape_4_extension_dim_declared_exit_2 | shape + dims `[自定义导出能力]` + P1 BDD 标题含该扩展维度名 | exit 2（扩展维度已声明运用） | 🟢（正例） |
| test_shape_4b_extension_dim_not_declared_exit_1 | shape + dims `[自定义导出能力]` + P1 无含该名的 BDD 标题 | exit 1（扩展维度未声明运用） | 🔴（现 exit 2） |
| test_shape_5_no_shape_fields_default_exit_2 | frontend 双字段缺失（布局型默认） | exit 2（presence 语义，不红基线） | 🟢（兼容） |

> 注：shape 用例的 P1 统一含 `status: available` 视觉条目 —— 使 BDD-3 检查通过、隔离"仅 shape 检查"的判定（BDD-3 与 BDD-16 同挂 gate_p1，触发域同为 frontend）。

### 2.3 BDD-4（P2 gate UI 设计节检查 `_gate_p2_ui_design_section`，含形态分支 + P1-P2 一致性）→ 9 用例（test_check_gate.py）

| 用例名 | 构造（均 4 字段 + candidate_count=2 + review approved） | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_ui_design_1_ui_true_missing_section_exit_1 | `ui_affected: true` 无 UI 节 | exit 1 | 🔴（现 exit 2） |
| test_ui_design_2_ui_true_full_section_exit_2 | `## UI 设计` + 形态声明 + 布局/交互/视觉关键词 | exit 2 | 🟢（正例） |
| test_ui_design_3_ui_true_missing_keyword_exit_1 | 有节 + 形态声明 + 布局/交互但缺"视觉" | exit 1 | 🔴（现 exit 2） |
| test_ui_design_4_ui_false_no_section_exit_2 | `ui_affected: false` 无节 | exit 2（不触发） | 🟢（兼容） |
| test_ui_design_5_ui_true_render_comp_section_exit_2 | 渲染组件型形态声明（渲染正确性/动效时序 checklist） | exit 2 | 🟢（正例） |
| test_ui_design_6_ui_true_missing_shape_decl_exit_1 | 有节但缺形态声明/维度选择 | exit 1 | 🔴（现 exit 2） |
| test_ui_design_7_ui_true_p1_p2_shape_mismatch_exit_1 | P1 `ui_render_shape: render_component` vs P2 声明 layout | exit 1（跨阶段不一致） | 🔴（现 exit 2） |
| test_ui_design_8_ui_true_p1_p2_shape_canonical_match_exit_2 | P1 render_component + P2 `渲染形态: render_component（渲染组件型）` | exit 2（规范值比对正例） | 🟢（正例） |
| test_ui_design_9_ui_true_p1_p2_shape_synonym_match_exit_2 | P1 render_component + P2 `渲染形态: 渲染组件型`（中文标签经同义映射归一化） | exit 2（防中文标签字面误拦） | 🟢（正例） |

> P1-P2 一致性的规范值/同义映射语义固化于 §2.15.1 词汇表；test_ui_design_8/9 为**词汇表正例、反误拦守卫**（实现为规范化值比对）。
> 构造注：8/9 的 P2 节内同时含渲染正确性/动效时序 checklist，满足形态分支的维度锚点。

### 2.4 BDD-9（P6 双证据分档：GAP 走人工复核 / available 强制 vision YAML / 无声明默认 available） → 5 例 evidence + 4 例 provenance

test_check_p6_evidence.py（check-p6-evidence.py 的 GAP 复核记录存在性检查 + 文档条文）：

| 用例名 | 构造 | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_vision_gap_1_evidence_manual_review_exit_0 | P1 vision=GAP + 截图 >1KB + PASS 引 `(manual-review: review-gap1.md)` 且文件存在 | exit 0（合法 GAP 降级链放行） | 🟢（正例，红转换由 test_vision_gap_2 承担） |
| test_vision_gap_2_evidence_missing_review_exit_1 | P1 vision=GAP + 截图但不引复核记录 | exit 1（复核记录缺失拦截） | 🔴（现 exit 0） |
| test_vision_docs_1_verifier_has_triple_state | 读 verifier.md | 含 available / supplementable / GAP 三态分档条文 | 🔴（现全缺席） |
| test_vision_docs_2_p6_card_real_analysis | 读 P6 卡片 | 含 "真实视觉分析"（BDD-10，available 分支真实分析硬要求） | 🔴（现缺席） |
| test_vision_docs_3_input_state_review | 读 verifier.md + P6 卡片 | 含 "人工复核"+"输入态"（BDD-13 判定标准） | 🔴（现缺席） |

test_check_p6_provenance.py（check-p6-provenance.py R1b 的 GAP 放宽 + 默认 available 语义回归守卫）：

| 用例名 | 构造（P1 含 `#### BDD-1` + 截图 PASS；ui_affected=true） | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_vision_gap_prov_1_gap_manual_review_exit_0 | P1 vision=GAP + 截图 + `(manual-review: review-gap.md)` 文件存在，无 vision 引用 | exit 0（GAP 放宽 vision 强制，改验复核记录） | 🔴（现 R1b 缺 vision exit 1） |
| test_vision_gap_prov_2_gap_missing_review_exit_1 | P1 vision=GAP + 截图 + 无复核记录 | exit 1 + 输出含 "人工复核" | 🔴（现输出 "缺 vision"，断言失败） |
| test_vision_avail_1_ui_available_no_vision_yaml_exit_1 | P1 vision=available + 截图无 vision YAML | exit 1（available 分支既有 R1b 语义保持） | 🟢（回归守卫） |
| test_vision_none_1_no_decl_default_available_exit_1 | P1 无视觉能力声明 + 截图无 vision YAML | exit 1（无声明默认 available，不落入 GAP 放行） | 🟢（回归守卫，守护 BDD-15 基线） |

### 2.5 BDD-14 + BDD-17（avg-hash 雷同降级待复核 + 时序截图 `-tN` 分组豁免） → 4 例 evidence（test_check_p6_evidence.py）

> ⚠️ 前置门禁（P2 §2.13）：PNG 必须 P6-evidence/screenshots/ 下 `>1KB` 且像素方差 ≥50（≤1KB 先被空文检查 exit 1、方差<50 先触发 WARNING exit 2，均遮挡 ahash 判定）。测试内 `_png_ok()` 显式断言两门禁满足。Pillow 缺失 → `pytest.importorskip("PIL.Image")` 整函数 skip（平台无关）。
> 同视觉内容不同字节 = 同 seed 像素 + 不同 compress_level → ahash 相同、md5 不同（P2 §5.2 minimal_validation confirmed）。

| 用例名 | 构造 | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_ahash_1_duplicate_with_review_record_exit_0 | BDD-1/BDD-2 各一张同视觉截图（跨 BDD 组雷同）+ P6-acceptance 含 "雷同截图复核" 记录 | exit 0 + 输出含 "人工复核记录"（放行） | 🔴（现输出仅 WARNING 无该字段） |
| test_ahash_2_duplicate_no_review_record_exit_1 | 同上但无复核记录 | exit 1（从 WARNING 升级为判定） | 🔴（现 exit 0） |
| test_ahash_3_no_duplicate_exit_0 | 两张不同视觉截图 | exit 0（无雷同不受影响） | 🟢（兼容） |
| test_time_seq_1_adjacent_time_shots_exempt_exit_0 | 同 BDD `bdd7-t1.png`/`bdd7-t2.png` 视觉相近（同 bdd 组分组豁免） | exit 0 且输出**不含** "average hash 相同"（组内相邻样本豁免，不触发雷同降级） | 🔴（现 ahash 全量统计 → 输出含 "average hash 相同"，断言失败） |

### 2.6 BDD-17（渲染组件类证据形式按形态识别） → 6 例 evidence（test_check_p6_evidence.py）

| 用例名 | 构造（P1 声明 `ui_render_shape` + ui_affected=true） | 预期 | P4 前状态 |
|--------|------|------|-----------|
| test_render_evid_1_frame_sequence_recognized_exit_0 | shape=render_component + `frames/bdd16-01.png/02.png`（>1KB） | exit 0（帧序列被识别） | 🟢（兼容，红由 test_render_diff_1 承担） |
| test_render_evid_2_render_output_compare_exit_0 | shape=render_component + `renders/` actual + diff.json（含 pixel_diff_ratio） | exit 0（渲染输出对比被识别） | 🟢（兼容） |
| test_render_evid_3_frame_seq_pure_text_exit_1 | shape=render_component + 证据全 .md/.txt | exit 1（非纯文本证据门槛） | 🟢（等位于既有 e_15 检查） |
| test_render_evid_4_shape_decl_layout_no_frames_exit_0 | shape=layout + 无 frames/ | exit 0（布局型不要求渲染组件证据） | 🟢（兼容） |
| test_render_diff_1_missing_diff_json_exit_1 | shape=render_component + renders/ 仅 actual+reference 无 diff.json | exit 1（对比缺 diff 锚点） | 🔴（现 exit 0） |
| test_render_diff_2_diff_json_with_metric_exit_0 | renders/ + actual + reference + diff.json 含量化度量 | exit 0（对比证据合规） | 🟢（正例） |

### 2.7 协议文档条文 → 14 例（test_review_role_docs.py，新增）

> 文档漂移保护：均读 agate_root 下协议文件断言 P4 将新增的锚点；现全缺席 → P4 前全红（B 类断言失败）。BDD-7/8/15 无单测，理由见 §3.2。

| BDD | 用例名 | 断言目标（文件 → 锚点词） |
|-----|--------|--------------------------|
| BDD-1 | test_bdd_1_analyst_classification_framework | analyst.md → "分类框架"+"渲染形态"（UX 分类框架 + 形态适配机制） |
| BDD-1 | test_bdd_1_p1_card_classification_framework | phase-cards/P1-requirements.md → "分类框架" |
| BDD-2 | test_bdd_2_analyst_quantitative_criteria | analyst.md → "渲染正确性"+"动效时序"+"可量化判据"（BDD 反模式自检清单 UX 全维度） |
| BDD-5 | test_bdd_5_architect_ui_design_section | architect.md → "UI 设计"+"兼任"（architect 兼任产出 UI 设计节） |
| BDD-5 | test_bdd_5_role_system_architect_dual_hats | role-system.md → "UI 设计节由 architect 兼任产出"（不新增 designer） |
| BDD-6 | test_bdd_6_plan_design_review_dimensions | plan-design-review.md → "视觉设计"+"交互设计"+"渲染正确性与时序"（七维 + 渲染维度） |
| BDD-11 | test_bdd_11_dispatch_prompt_injection_guidance | dispatch-prompt.md → "视觉能力"+"获取指引"（supplementable 注入位） |
| BDD-11 | test_bdd_11_dispatch_protocol_a3_vision | dispatch-protocol.md → "视觉能力"（A3 视觉语境扩展） |
| BDD-12 | test_bdd_12_dispatch_prompt_self_check | dispatch-prompt.md → "能力自查"+"先自查能否调用视觉能力"（subagent 能力自查强制段） |
| BDD-13 | test_bdd_13_verifier_input_state_review | verifier.md → "人工复核"+"输入态"（输入态判定标准） |
| BDD-13 | test_bdd_13_p6_card_input_state_review | phase-cards/P6-acceptance.md → "人工复核"+"输入态" |
| BDD-16 | test_bdd_16_render_component_dim_requirements | P1 卡片 → "渲染形态"+"渲染正确性"+"动效时序"；analyst.md → "手势交互"+"特效" |
| BDD-17 | test_bdd_17_verifier_evidence_form_by_shape | verifier.md → "帧序列"+"时序截图"+"渲染输出对比"（证据形式按形态选择） |
| BDD-17 | test_bdd_17_p6_card_evidence_form_by_shape | phase-cards/P6-acceptance.md → "帧序列"+"时序截图"+"渲染输出对比" |

## 3. 红绿灯语义与说明

### 3.1 灯色约定

- 🔴 = P4 前该测试失败（断言失败 / 引用未实现检查逻辑），失败原因为**被测功能未实现**（B 类）。
- 🟢 = P4 前已通过 —— 属以下两类：**兼容回归守卫**（既有行为即期望行为：test_vision_3/4、test_shape_2/3/5、test_ui_design_2/4、test_vision_avail_1、test_vision_none_1、test_render_evid_3/4）或**新行为正例**（最终期望行为与既有行为在正分支恰好一致：test_vision_gap_1、test_shape_2b/4、test_ui_design_5/8/9、test_render_evid_1/2、test_render_diff_2、test_ahash_3）。这类正例的**负分支**（无复核记录/不一致）由配对红灯用例承担判定（test_ahash_2、test_vision_gap_2、test_ui_design_1/3/6/7、test_time_seq_1）。check-tdd-red.py 语义：套件存在 assertion 失败（红灯用例足够多）即判定 exit 0（真红灯）——绿灯正例不改变"实现先于测试"的判定。

### 3.2 无单测的 BDD（设计决策记录）

- **BDD-7**（P2-design.md 必含 Windows GUI 自动化评估小节 + 无"已实测"声称）/ **BDD-8**（P2-design.md 必含影响面核对清单）：验收方式为**读本任务自身 P2-design.md**（任务工件，位于 `agate-workspace/tasks/`，非 agate/tests 可移植对象；CI 无该路径）→ 由 P6 verifier 读取核对，**不适合 agate/tests 单测**。P2 §2.6/§2.7 已将二节落实于本任务 P2-design.md（§4 / §6）。P6 验收时直接核对。
- **BDD-15**（基线回归）：P2 §2.14 明确"不新增（回归本身是执行验证）"→ 由 gate_commands.P5/P6 全量 pytest + consistency + count-tests 实跑覆盖。

### 3.3 平台无关落实

- 全部 fixture 用 pytest `task_dir`（tmp_path），无 `/tmp` 硬编码。
- 随机字节证据用 `os.urandom` + `write_bytes`；PNG 用 PIL 生成且用 `pytest.importorskip("PIL.Image")` 包裹（无 Pillow 自动 skip）。
- 运行解释器统一走 `python_exe` fixture（python3→python 探测），测试内不出现裸 `python3`。
- 中文字符串与路径仅作断言锚点/文件名，不构成 Unix 假设。

### 3.4 关联事项（P4 实现时生效，非 P3 责任）

- 新增用例总数 53 → count-tests.sh 计数期望值由 P4/发布流程更新（tests/README.md 计数表同步）。
- test_dispatch_orchestration.py 的 BDD-11 注入用例由 P4 侧评估（P2 §2.10 注明"若无 render 函数则模板 grep 断言"——本清单以 dispatch-prompt/dispatch-protocol 模板断言承担，避免侵入既有编排测试）。

## 4. P3 自检记录

- [x] P3-test-cases.md 存在 + Header 完整 + test_code_dir 声明
- [x] BDD-1~17 映射（1:1，测试名含 BDD 编号；BDD-7/8/15 无单测理由见 §3.2）
- [x] 测试代码已写入 agate/tests/（test_check_gate.py / test_check_p6_evidence.py / test_check_p6_provenance.py 追加 + test_review_role_docs.py 新增）
- [x] 自跑测试（2026-08-17，worktree 环境）：4 个落点文件 **32 failed / 211 passed**，32 例失败全部为 `AssertionError`（B 类红灯，原因=被测 gate 检查逻辑/文档条文未实现），无 SyntaxError/ImportError（A 类 0）→ check-tdd-red 判定 exit 0 真红灯
  - 失败明细：test_check_gate.py 8（vision_1/2 + shape_1/4b + ui_design_1/3/6/7）、test_check_p6_evidence.py 8（vision_gap_2 + vision_docs_1/2/3 + render_diff_1 + ahash_1/2 + time_seq_1）、test_check_p6_provenance.py 2（gap_prov_1/2）、test_review_role_docs.py 14（全文件）
  - 21 例通过 = 兼容回归守卫 + 新行为正例（§3.1 灯色约定）
- [x] 红灯原因核对：非"断言与测试数据矛盾"——test_ahash_1/2 与 test_time_seq_1 曾因 seed 派生 bug 产生假红（数据构造错误），已改为显式同 seed 不同 compress（同视觉内容不同字节→ahash 相同 md5 不同）并复跑确认红灯原因为"降级判定/分组豁免未实现"
- [x] 平台无关原则（tmp_path / importorskip("PIL") / python_exe 探测）