---
phase: P3
task_id: TAG0027
type: test-cases
parent: P2-design.md
trace_id: TAG0027-P3-20260902
status: draft
created: 2026-09-02
agent: test-designer
---

# P3 测试用例映射 — 编排语义统一落地（TAG0027，25 BDD）

> 设计对象 = worktree `agate/` 协议本体；本文件是 BDD→测试文件映射（P1 25 BDD 1:1 全覆盖），
> 测试代码已实际写入 test_code_dir（非仅映射——TAG0020 分工模式之后本任务按
> P3-dispatch-context-test-designer.md 约束 2 直接把测试代码写进 agate/tests/unit/）。
> 用例数：**44 个 pytest 测试函数**（25 BDD 全覆盖；部分 BDD 拆多场景用例 + 回归守卫，BDD 行
> 计不重复）；当前 **30 红（全部 B 类真红灯）/ 14 绿（回归守卫）**——自跑结果与失败原因分类见
> P3-progress.md「自跑红灯记录」节；语义来源 = P2-design.md §5 覆盖映射表 + §3.1-3.8 定案 +
> P1-requirements.md（25 BDD，含 BDD-10 BASELINE_CHANGE 回改后语义）。

## test_code_dir

```yaml
test_code_dir: agate/tests/unit/
```

测试代码分布（新文件，7 个，全部可被 P5 `python3 -m pytest agate/tests/` 收集；命名带
P2-design §8 dispatch_plan 批次前缀 B1/B2/B3a/B3b，P4 分批实现按此对应）：

| 批次 | 测试文件（agate/tests/unit/ 下） | 覆盖 BDD | P4 实现对象 |
|---|---|---|---|
| B1 | `test_tag0027_b1_phases_transfer_fields.py` | BDD-1/2/3/5 | phases.yaml + schema（§3.1）|
| B1 | `test_tag0027_b1_agate_next_cli.py` | BDD-6/7/8/9/11/13 | agate-next.py + check-gate 消费（§3.4/§3.1 A1）|
| B1 | `test_tag0027_b1_agate_advance_cli.py` | BDD-10 | agate-advance.py（§3.4）|
| B1 | `test_tag0027_b1_judge_exit2_review.py` | BDD-12 | check-judge-verdict.py exit2-resolution 复核（§3.3）|
| B2 | `test_tag0027_b2_agate_dispatch.py` | BDD-18/19/25 | agate-dispatch.py + 模板（§3.5/§3.6）|
| B2 | `test_tag0027_b2_audit2_dual_anchor.py` | BDD-20/21 | check-p6-provenance.py 审计 2 双锚点（§3.6）|
| B3a | `test_tag0027_b3a_platform_name_docs.py` | BDD-14/16/17 | 平台名存量清理 + 注记 + 五模式锚点（§3.8/§6③）|
| B3b | `test_tag0027_b3b_structure_s1s2_next_retreat.py` | BDD-4（S-1/S-2 扩展）| check-structure-consistency.py S-1/S-2（§3.2）|
| B3b | `test_tag0027_b3b_protocol_check14_check15.py` | BDD-15/22/24（CHECK 14/15）| check-protocol-consistency.py CHECK 14/15（§3.8）|

> 注：BDD-5 实数据面回归、BDD-13/19/21/23 回归守卫用例（现状绿，验证 P4 不改既有机制）分布
> 在上述文件内；新扩展点行为用例现状红。各 BDD 的"红/绿当前态"见下映射表「当前态」列
> （红 = P3 现状即失败【B 类真红灯，被测未实现】；绿 = 回归守卫【P3 现状即通过，验证不改既有】）。

## BDD → 用例映射（25 条 1:1，44 用例）

> 用例名引用 BDD 编号（`test_bdd_N_*`），全部可二值判定。红灯语义（约束 3）：不 mock 被测对象；
> 新 CLI/脚本未实现 → subprocess rc 2 "can't open file" → 断言失败 = B 类真红灯；既有脚本
> 扩展点（S-1/S-2 加列、审计 2 双锚点、judge exit2 复核、CHECK 14/15）用临时任务目录/假协议树
> 模拟 P4 定案场景断言新行为 → 未实现红、既有行为绿。

### B1 批 — 转移表结构化 + 推进侧 CLI（BDD-1/2/3/5/6/7/8/9/10/11/12/13）

| BDD | 测试文件 | 用例 | 当前态 | 断言要点 |
|---|---|---|---|---|
| BDD-1 | b1_phases_transfer_fields | `test_bdd_1_phases_mainline_next_retreat_keys_present` | 红 | 实 worktree rules/phases.yaml 主线阶段（P0-P8 非 P6.5）每条含 `next` 与 `retreat` 键；P8 的 next/retreat 值域含 null |
| BDD-1 | b1_phases_transfer_fields | `test_bdd_1_phases_schema_declares_next_retreat` | 红 | 实 worktree rules/schema/phases.schema.json items.properties 声明 `next`/`retreat`（P4 须补键否则 additionalProperties:false 拦）|
| BDD-2 | b1_phases_transfer_fields | `test_bdd_2_p65_gate_subphase_not_independent_edge` | 红 | 实 phases.yaml P6.5 条目含 `gate_subphase`（hosted_on=P6/forward_to=P7/needs_revision_to=P6）；断言 P6.5 不出现 `next:`/`retreat:` 键（非独立转移边，state-machine.md:74-78 口径）|
| BDD-3 | b1_phases_transfer_fields | `test_bdd_3_retreat_targets_match_state_machine` | 红 | 实 phases.yaml：P5.retreat==P4 且 P6.retreat==P4（state-machine.md:132/148 锚点）；P6.5 gate_subphase.needs_revision_to==P6；P5.next==P6、P6.next==P7 |
| BDD-5 | b1_phases_transfer_fields | `test_bdd_5_consistency_worktree_still_green_regression` | 绿 | worktree 版 check-protocol-consistency.py --strict-errors-only exit 0（P4 加字段后不得破坏既有 WARNING 口径 = 回归守卫）|
| BDD-13 | b1_agate_next_cli | `test_bdd_13_check_gate_exit_semantics_regression` | 绿 | check-gate.py 头注释三态（exit 0=通过/1=未通过/2=自判）+ P1 缺 review 场景 exit 1——既有返回约定回归守卫 |
| BDD-13 | b1_agate_next_cli | `test_bdd_13_check_state_transition_exit_semantics_regression` | 绿 | check-state-transition.py 头注释 exit 0=合法/1=非法保留（回归守卫）|
| BDD-6 | b1_agate_next_cli | `test_bdd_6_next_exit0_advances_to_next_phase` | 红 | mock 子进程 check-gate 层：临时任务 phase=P5 + gate exit 0 → agate-next 消费 phases.yaml next → .state.yaml phase 变 P6（预期脚本 agate-next.py 未实现 → 红灯）|
| BDD-6 | b1_agate_next_cli | `test_bdd_6_p6_judge_disabled_direct_p7_anchor` | 红 | P6 条件式推进 A1 锚点：临时任务 phase=P6 + judge 块缺失/未启用 + check-gate P6 恒 exit 2 + check-p6-provenance exit 0 → agate-next 按 §3.1 裁决直推 P7（gate_p65 早退语义）|
| BDD-7 | b1_agate_next_cli | `test_bdd_7_next_exit1_delegates_retreat_to_retreat_target` | 红 | mock check-gate exit 1 → agate-next 委托 agate-retreat-to 到 retreat 表目标（P5→P4）+ retries[P4] 记录；不预判 diff（表值存在即委托）|
| BDD-7 | b1_agate_next_cli | `test_bdd_7_p6_exit1_retreats_to_p4_via_retreat_to` | 红 | P6 exit 1（表 retreat:P4，diff=2）→ 委托 retreat-to 逐阶 P6→P5→P4（BDD-7 §3.4：CLI 不预判 diff）|
| BDD-8 | b1_agate_next_cli | `test_bdd_8_non_p6_exit2_writes_exit2_resolution` | 红 | 临时任务 phase=P5 + gate exit 2（mock）→ agate-next 不推进 + 落盘 `P5-exit2-resolution.md` 含 §3.3 模板字段（phase/task_id/type/触发/客观证据/解决人）|
| BDD-8 | b1_agate_next_cli | `test_bdd_8_exit2_resolution_frontmatter_machine_readable` | 红 | 落盘文件 frontmatter（phase/task_id/type=exit2-resolution/parent=`.state.yaml`）可由 agate-md-field-get 读取 = 机器可读（agate-md-field-get 是既有脚本可直接调）|
| BDD-9 | b1_agate_next_cli | `test_bdd_9_p6_exit2_keeps_advancing_no_resolution_file` | 红 | P6 exit 2 + provenance exit 0 + judge 未启用 → 推进 P7 且**不**生成任何 `P6-exit2-resolution.md`（唯一例外不泛化）|
| BDD-9 | b1_agate_next_cli | `test_bdd_9_p6_judge_enabled_gate_p65_pass_advances_p7` | 红 | P6 judge.enabled=true + verdict/evidence/账本合规 → check-gate P6.5 exit 0 → agate-next 推 P7 + gate-events.jsonl 含 state_transition（A1 闭环正向）|
| BDD-9 | b1_agate_next_cli | `test_bdd_9_p6_judge_gate_p65_fail_stays_p6` | 红 | P6 judge.enabled=true + 缺 verdict（check-gate P6.5 exit 1）→ 停留 P6 不推进、不落盘 exit2-resolution（A1 闭环反向）|
| BDD-11 | b1_agate_next_cli | `test_bdd_11_state_transition_event_observable` | 红 | 两次推进后（P5→P6→P7 场景或等效 mock 链）gate-events.jsonl 含 `event: state_transition`（from/to 字段）——档位 C 可观测证据（BDD-11 的 When 记录面）|
| BDD-12 | b1_judge_exit2_review | `test_bdd_12_judge_review_gate_run_exit2_without_resolution_fails` | 红 | 任务 gate-events.jsonl 含 `gate_run exit:2`（phase=P5）但无 `P5-exit2-resolution.md` → check-judge-verdict P6.5 复核 exit 1（挂载点 §3.3：缺失或格式非法 → judge 不通过）|
| BDD-12 | b1_judge_exit2_review | `test_bdd_12_judge_review_exit2_resolution_present_passes` | 红 | 同上但 `P5-exit2-resolution.md` 存在且 frontmatter/必填节完整 → 复核 exit 0 |
| BDD-10 | b1_agate_advance_cli | `test_bdd_10_advance_diff2_manual_jump_prompts_paused` | 红 | agate-advance `--to` 目标与当前 diff≥2（如 P6→P4）→ 提示"须先 PAUSED（check-state-transition 会拦直退）"不自行回退（diff≥2 人工直跳语义，state-machine.md:647-654）|
| BDD-10 | b1_agate_advance_cli | `test_bdd_10_advance_diff1_delegates_retreat_to` | 红 | agate-advance diff=1（如 P6→P5）→ 委托 agate-retreat-to 单步（逐阶 diff=1 独立 commit，不触发 PAUSED 拦截）|

### B2 批 — 渲染层 + 注入自动化 + 审计 2（BDD-18/19/20/21/25）

| BDD | 测试文件 | 用例 | 当前态 | 断言要点 |
|---|---|---|---|---|
| BDD-18 | b2_agate_dispatch | `test_bdd_18_dispatch_render_injects_full_card` | 红 | 临时任务目录跑 agate-dispatch P3 test-designer → 产物含完整卡片块（AGATE_CARD_START/END 内抽取 hash == agate-next-card stdout 归一化 hash）且 frontmatter generated_by 含 agate-dispatch.py（§3.5 Lazy Injection）|
| BDD-18 | b2_agate_dispatch | `test_bdd_18_dispatch_card_source_marker_outside_block` | 红 | 渲染产物 `<!-- CARD-SOURCE: agate-dispatch.py ... -->` 在 `<!-- AGATE_CARD_START -->` **之前**（块外，不进 _extract_card 抽取区间 = A2 机制）|
| BDD-19 | b2_agate_dispatch | `test_bdd_19_manual_inject_card_kept_exit_0` | 绿 | 手工占位符文件 + agate-inject-card.py P3 注入 → exit 0 且卡片块写入占位符块（两路并存兜底现状）|
| BDD-19 | b2_agate_dispatch | `test_bdd_19_manual_path_2p_hash_pass_anchor` | 绿 | 手工注入产物 START..END 内嵌 hash == agate-next-card P3 归一化 hash（2p 现状语义 = A2 定案 2p 天然兼容）|
| BDD-25 | b2_agate_dispatch | `test_bdd_25_two_paths_dispatch_context_hash_equal` | 红 | 两路生成物（手工 inject-card 兜底 + 自动 agate-dispatch，含块外 CARD-SOURCE）的 START..END 内嵌抽取 hash 相等且 == next-card stdout hash（两路并存 gate 行为无差异；CARD-SOURCE 不入抽取区间）——自动路缺 CLI → 红 |
| BDD-25 | b2_agate_dispatch | `test_bdd_25_auto_dispatch_card_hash_matches_next_card` | 绿 | 含块外 CARD-SOURCE + START..END 内嵌 next-card stdout 的产物 → _extract_card 抽取 hash == next-card 期望（A2 机制不变量：CARD-SOURCE 不入抽取区间 → 2p 天然兼容；现状绿，P4 后仍绿防回归）|
| BDD-20 | b2_audit2_dual_anchor | `test_bdd_20_audit2_render_product_with_card_source_exit_0` | 绿 | 渲染产物（CARD-SOURCE 块外 + 卡片含 PASS/FAIL 模板字样）→ check-p6-provenance 审计 2 exit 0（物理块剥离现状已不误报 = 回归守卫；P4 双锚点后仍绿）|
| BDD-20 | b2_audit2_dual_anchor | `test_bdd_20_audit2_pass_before_start_requires_dual_anchor` | 红 | 双锚点剥离起点真锚点：CARD-SOURCE 行与 START 之间放行首 `- PASS` 预判行 → 双锚点（CARD-SOURCE 起整段剥）exit 0；现状单锚点（只剥 START..END）保留该行 → 误报 exit 1（B 类红：双锚点剥离未实现）|
| BDD-21 | b2_audit2_dual_anchor | `test_bdd_21_audit2_manual_physical_block_fallback_exit_0` | 绿 | 手工注入文件（物理 AGATE_CARD_START/END，无 CARD-SOURCE）含 PASS/FAIL 卡片行 → 审计 2 exit 0（既有物理块剥离兜底回归守卫）|

### B3a 批 — 编排心智统一文档化（BDD-14/16/17/23）

| BDD | 测试文件 | 用例 | 当前态 | 断言要点 |
|---|---|---|---|---|
| BDD-14 | b3a_platform_name_docs | `test_bdd_14_dispatch_protocol_five_modes_single_anchor` | 绿 | dispatch-protocol.md 五模式（模式 1-5）语义锚点条文存在；grep 断言协议层无 "workflow 模式"/"ralph 模式"/"goal 模式" 平台命名概念（回归守卫）|
| BDD-16 | b3a_platform_name_docs | `test_bdd_16_workflow_md_known_env_table_has_anchor` | 绿 | WORKFLOW.md「已知适用环境」表存在（平台适配元信息豁免结构现状，回归守卫）|
| BDD-16 | b3a_platform_name_docs | `test_bdd_16_implementation_note_marker_format_present_after_cleanup` | 红 | 「实现注记」统一格式标记 `> 实现注记：` 在 B3a 清理面文档（role-system/UPGRADING/adr/loop-orchestration/dispatch-protocol/WORKFLOW）中出现（Phase 3 后应有；现状 0 处 → 红，B3a 未完成）|
| BDD-17 | b3a_platform_name_docs | `test_bdd_17_assets_dsh_skill_md_is_structure_exempt` | 绿 | A3 定案①：assets/templates/dsh/ 平台食谱目录实存且含 md 资产（结构豁免对象事实；真实豁免判定由 B3b CHECK 14 用例承载）|
| BDD-23 | b3a_platform_name_docs | `test_bdd_23_render_dispatch_prompt_cli_contract_regression` | 绿 | agate-render-dispatch-prompt.py 既有 CLI 契约（P1 analyst TASK_DIR → exit 0 + P1-dispatch-prompt-analyst.md）回归守卫（Not Modify，P2 §1.2）|

### B3b 批 — S-1/S-2 扩展 + 护栏 1 机械化（BDD-4/15/22/24）

| BDD | 测试文件 | 用例 | 当前态 | 断言要点 |
|---|---|---|---|---|
| BDD-4 | b3b_structure_s1s2_next_retreat | `test_bdd_4_s1_yaml_retreat_vs_table_mismatch_exit_1` | 红 | 假协议树（schema 已扩展声明 next/retreat；YAML P2 retreat:P1 ↔ 表 P2 retreat 列写 P3）→ check-structure-consistency S-1 exit 1（S-1 扩展比对 4/5 列 = 扩展点；现状 S-1 不比对 → exit 0 红）|
| BDD-4 | b3b_structure_s1s2_next_retreat | `test_bdd_4_s1_yaml_next_vs_table_mismatch_exit_1` | 红 | 同上前者 next 列不一致（YAML P1 next:P2 ↔ 表 P1 next 列写 P4）→ S-1 exit 1（现状红）|
| BDD-4 | b3b_structure_s1s2_next_retreat | `test_bdd_4_s1_consistent_next_retreat_exit_0` | 绿 | YAML 与表 next/retreat 一致 → S-1/S-2 exit 0（加列后既有前 3 列比对不受影响 = 回归守卫）|
| BDD-15 | b3b_protocol_check14_check15 | `test_bdd_15_check15_data_rules_platform_token_zero` | 红 | CHECK 15 数据面扫描（rules/*.yaml + schema 平台词表命中数 = 0；task_fields/task_id 既有键不误报 = 豁免词典机械生成）。P3 无 check_rules_platform_tokens 函数 → AttributeError 红（B 类）|
| BDD-15 | b3b_protocol_check14_check15 | `test_bdd_15_check15_inserted_bare_task_errors` | 红 | 数据面插入裸平台词（DSH 注释）→ CHECK 15 ERROR（词边界命中）。P3 无函数 → 红 |
| BDD-16 | b3b_protocol_check14_check15 | `test_bdd_16_check14_whole_file_exempt_structure` | 红 | 豁免结构：platform-notes.md / SETUP.md 整文件含平台名 → CHECK 14 不报（整文件豁免 = 结构性判据豁免面）。P3 无 check_md_platform_paragraphs → 红 |
| BDD-22 | b3b_protocol_check14_check15 | `test_bdd_22_check14_md_paragraph_platform_name_no_note_errors` | 红 | 协议 md 语义叙述段含 DSH 且段内无 `> 实现注记：` → CHECK 14 ERROR（段落级判据）。P3 无函数 → 红 |
| BDD-22 | b3b_protocol_check14_check15 | `test_bdd_22_check14_add_note_marker_pass` | 红 | 同段补 `> 实现注记：` 标记行 → CHECK 14 不报（注记豁免 = BDD-22 二值：插 ERROR → 补注记 pass）。P3 无函数 → 红 |
| BDD-24 | b3b_protocol_check14_check15 | `test_bdd_24_new_protocol_md_auto_covered` | 红 | 新增临时协议 md（agate/ 顶层语义叙述面）含平台名无注记 → 自动被 CHECK 14 命中（结构性判据无名单，新增文档自动覆盖 = BDD-24）。P3 无函数 → 红 |

## 红灯状态汇总（自跑确认，详见 P3-progress.md「自跑红灯记录」）

- **44 个 pytest 测试函数：30 红 / 14 绿**（`pytest agate/tests/unit/test_tag0027_b{1,2,3a,3b}_*.py`，
  自跑 2026-09-02）。红灯全部为 **B 类真红灯**：
  - 新增 CLI（agate-next/advance/dispatch）与 phases.yaml/schema 新字段未实现 → B1/B2 批多数红
    （subprocess rc 2 "can't open file" / 数据面字段缺失断言失败）。
  - 既有脚本扩展点未实现 → S-1/S-2 加列比对（B3b）、审计 2 双锚点剥离起点（B2）、judge
    exit2-resolution 复核（B1）、CHECK 14/15 函数缺失（B3b AttributeError）→ 红。
  - B3a「实现注记」标记清理未完成（Phase 3 文档批次 = P4 B3a）→ 红。
- **14 绿 = 回归守卫**：BDD-5/13/14/19/21/23/部分 BDD-4 等——验证既有机制（check-gate 三态 /
  check-state-transition 二态 / 手工 inject-card 2p hash / 审计 2 物理块兜底 / render-dispatch-
  prompt 契约 / 五模式锚点 / 加列兼容）不被 P4 破坏。
- **无 A 类假红灯**：无 SyntaxError / 第三方 import 失败；全部测试文件被 pytest 正常收集
  （语法经 ast.parse 验证）。pytest formatter 下 "assertion failures only" 为经典红灯 → 
  check-tdd-red exit 0（可推进）。

## BDD 覆盖对照

- P1 25 条 BDD → 本表 25 行映射、44 用例，每条 BDD ≥1 用例、无遗漏（含 BDD-10 BASELINE_CHANGE
  回改 P6→P4 语义、BDD-9 A1 三条锚点、BDD-20/25 A2 机制锚点、BDD-17 A3 豁免锚点）。
- 多重承载行（BDD-6/9 拆 2-3 场景、BDD-4/15/16/22 拆红/绿双态）为场景拆分/回归，非重复计数。

[PROD_NOT_TOUCHED]：本文件只写任务目录产出（P3-test-cases.md）；测试代码写入
agate/tests/unit/（P3 阶段允许的测试落点）。协议本体 rules/scripts/md 一律未改。
