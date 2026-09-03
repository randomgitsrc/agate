# P3-progress.md — TAG0027 测试设计分阶段落盘

> 本文件为 P3 test-designer 分阶段落盘记录。每读完一个输入文件、每完成一个关键步骤追加一条。

## 开工（2026-09-02）

- 角色：test-designer（P3 TDD）
- 读取 dispatch-context（P3-dispatch-context-test-designer.md）：目标 = P3-test-cases.md + agate/tests/unit/ 下新测试文件（当前全部红灯），25 BDD 1:1 映射；约束 9 条 + 平台无关硬约束；产出声明 test_code_dir。
- 测试基线：pytest 1311（unit 1191 + regression 28 + integration 92）；python 3.12.3 / pyyaml 6.0.1 / pytest 9.0.3
- 目标文件确认：`agate/tests/unit/` 下既有测试列表已看（test_agate_*.py / test_check_*.py / conftest.py 在同级 agate/tests/）
- 状态：P1-requirements.md 25 BDD 全读完成（P3-progress 首条记录）

## 输入文件读取记录

- [x] P3-dispatch-context-test-designer.md（派发指引 + 目标 + 约束 + 上游关联）
- [x] execution-roles/test-designer.md（角色定义：1:1 映射、Examples 表参数化、分阶段落盘）
- [x] P1-requirements.md（25 BDD 全读，含 BDD-10 BASELINE_CHANGE 回改后语义）
- [ ] P2-design.md（§5 映射表 + §3.x 定案 + §4.1 gate_commands）

## 输入文件读取记录（续）

- [x] P2-design.md（§5 BDD 覆盖映射表全读 + §3.1-3.8 定案全读 + §4.1 gate_commands + §8 dispatch_plan 4 批 B1/B2/B3a/B3b）
  - 关键定案：B1 core-rules-cli（phases.yaml/schema + agate-next/advance + check-judge-verdict + loop-orchestration）；B2 render-audit（agate-dispatch + 模板 + check-p6-provenance 审计 2）；B3a docs-clean（9 md 平台名清理/注记）；B3b guardrail-scripts（check-structure-consistency S-1/S-2 + check-protocol-consistency CHECK 14/15）
  - P3 测试按 B1/B2/B3a/B3b 分组命名，P4 分批实现对应
- [ ] P2-review.md（approved 定案 A1/A2/A3）
- [ ] 既有测试风格参照（1-2 文件）
- [ ] agate/tests/conftest.py
- [ ] phases.yaml / phases.schema.json
- [ ] 被测扩展点脚本（按需）

## 输入文件读取记录（续 2）

- [x] P2-review.md（approved 终局判定：A1/A2/A3/B1/B2/B3 闭合 + 锁定决策 8 面 + 测试缺口 3 条补锚点确认）
- [x] agate/tests/conftest.py（fixture 体系：agate_root/agate_scripts/agate_assets/bash/python_exe/run_cli/task_dir/git_repo/load_fixture/py_path；create_task_dir 构造任务目录）
- [x] agate/tests/unit/_rules_test_utils.py（make_fake_root 假协议树：fake-root/rules/{phases,dispatch,roles}.yaml + schema + WORKFLOW.md + phase-cards/ + scripts/ + assets/；DEFAULT_PHASES_YAML/WORKFLOW_TABLE 等）
- [x] agate/tests/unit/test_check_structure_consistency.py（风格参照：_run_structure 辅助 + make_fake_root(tmp_path) + run_cli(python_exe, script, env={"AGATE_ROOT": str(root)}) + assert result.returncode）
- [x] agate/rules/phases.yaml（现状：9 主线 + P6.5 条目，无 next/retreat/gate_subphase 字段）
- [ ] agate/rules/schema/phases.schema.json
- [ ] 被测扩展点脚本相关区（check-structure-consistency/check-p6-provenance/check-judge-verdict/pre-commit-gate/check-gate/agate-next-card/agate_common）
- [ ] 1-2 个 CLI 风格既有测试（如 test_check_gate.py / test_agate_next_card.py）

## 输入文件读取记录（续 3 — 被测扩展点脚本/既有测试风格/数据面全读完）

- [x] phases.schema.json（additionalProperties:false 现状：items.properties 无 next/retreat/gate_subphase；枚举 phaseId 含 P6.5）
- [x] check-yaml-schema.py（S-5 链路：手写 draft-07 子集校验器，支持 type/enum/required/properties/items/additionalProperties/minItems；**不支持 if/then/oneOf/$ref**——P4 实现 schema 反例拦截须扩展该子集或换判据；P3 测试按"行为"断言不绑实现形态）
- [x] check-structure-consistency.py（S-1/S-2 扩展点实证：_TABLE_ROW_RE 不锚行尾只消费前 3 列；_parse_workflow_rows 返回 3 元组；_check_s1 比对 id/name/exec_role；S-5 串联独立进程 exit code；S-0 编号自校验）
- [x] check-p6-provenance.py 审计 2（318-355 行：物理 AGATE_CARD_START→END 剥离 + frontmatter 剥离 + 行首 - PASS|FAIL 计数）——双锚点改动点实证
- [x] check-judge-verdict.py _strip_card（98-111 行）+ _strip_frontmatter + main 链——双锚点同步面 + exit2-resolution 复核挂载点实证
- [x] pre-commit-gate.py（_extract_card 171-189 只抽 START..END；2p hash 425-448 期望 = agate-next-card stdout 归一化 sha256；gate_run/state_transition 事件 2h.1b/2h.1c；judge verdict 文件存在时 2i.1 双脚本）——CARD-SOURCE 块外兼容实证
- [x] check-gate.py（gate_p5 exit 2/exit 1 语义；gate_p6 恒 exit 1/2 无 exit 0（1051-1093 return 2）；gate_p65（1096-1120）judge 三态；main 1410-1414 未知阶段 exit 2）——A1 裁决前提实证
- [x] agate_common.py append_event（309+：GENESIS_HASH 哈希链/ts 单调/失败仅 WARNING）——state_transition 事件写入面
- [x] agate-next-card.py CLI（测试参照）+ agate/tests/unit/test_agate_next_card.py（4 行头剥离 body sha256 == 卡片文件 sha256）
- [x] dispatch-context.md 模板（frontmatter phase/generated_by/task_id/role + AGATE_CARD_START 占位）+ rules/dispatch.yaml + phases.yaml task_fields
- [x] WORKFLOW.md S1S2-ANCHOR 总览表（287-304 行实证：现在 5 列=阶段/名称/执行角色/评审角色/门槛；加 next/retreat 4/5 列后评审角色顺延——S-1/S-2 比对用前 3 列不受影响）
- [x] state-machine.md（74-78 P6.5 非独立口径 / 132 P5→P4 / 139 P6→P6.5 / 148 P6→P4 diff=2 / 151-157 P6.5 needs-revision→P6 / 647-654 diff≥2 PAUSED）
- [x] 稳定版 P3-test-cases.md 格式参照（TAG0020/TAG0024：frontmatter + test_code_dir + BDD 映射表 + 红灯说明）
- [x] test_check_gate.py（gate 测试 fixture 用法：task_dir/git_repo/覆写 .state.yaml/verdict fixture/_write_state_judge）
- [x] test_check_p6_provenance.py / test_check_judge_verdict.py / test_check_events.py / test_check_tdd_red.py / test_agate_retreat_to.py / test_agate_render_dispatch_prompt.py 等风格参照

关键判定（供设计定稿）：
1. P3 gate_commands.P3 = `python3 -m pytest agate/tests/`（全量收集）→ 新测试文件放 agate/tests/unit/ 即可被收集；check-tdd-red 会把新用例的 subprocess "can't open file"(rc 2)+assertion 失败判为 B 类（无 project_module 时 heuristic import→B）。
2. 新增 CLI（agate-next/advance/dispatch）P4 新建 → P3 全部 subprocess 测它必 rc 2（can't open file）→ 断言 exit==0/1 全失败 = B 类红灯 ✓
3. schema next/retreat/gate_subphase 与 phases.yaml 字段均未实现 → 实数据面（worktree agate/rules/）断言全红 ✓；S-1/S-2 扩展点、CHECK 14/15、审计 2 双锚点、judge exit2 复核、2p hash 均未实现 → 对既有脚本现状断言部分红（A2 类新增功能点红、既有行为绿 = 正确区分）。
4. 回归注意：P5_schema = `check-yaml-schema.py agate/rules/phases.yaml`（worktree 版）在 P3 现状（无 next/retreat）下 exit 0（全绿，既有 schema 通过）——但 P4 B1 加字段后必须同步 schema 否则 S-5 红；本测试设计在 P3 断言实数据面字段存在（红），P5 后该断言变绿即验证 B1 完成。

## 测试用例设计（25 BDD 全覆盖，36 用例草案）→ 映射结构定稿

按 P2 §8 四批（B1 core-rules-cli / B2 render-audit / B3a docs-clean / B3b guardrail-scripts）分文件：

**B1 批**（agate-next.py / agate-advance.py / phases.yaml / schema / check-judge-verdict / loop-orchestration 文档层）：
- test_tag0027_b1_phases_transfer_fields.py（BDD-1/2/3/5 数据面）
- test_tag0027_b1_agate_next_cli.py（BDD-6/7/8/9/11/13）
- test_tag0027_b1_agate_advance_cli.py（BDD-10）
- test_tag0027_b1_judge_exit2_review.py（BDD-12）
- （BDD-13 另含 check-gate/check-state-transition 头注释断言）

**B2 批**（agate-dispatch.py / check-p6-provenance 审计 2 / dispatch 产物 / 2p hash）：
- test_tag0027_b2_agate_dispatch.py（BDD-18/19/25）
- test_tag0027_b2_audit2_dual_anchor.py（BDD-20/21）

**B3a 批**（平台名存量清理 + WORKFLOW 总览表加列 + 注记标记）：
- test_tag0027_b3a_platform_name_docs.py（BDD-16/17 文档断言 + 注记格式）

**B3b 批**（check-structure-consistency S-1/S-2 扩展 + check-protocol-consistency CHECK 14/15）：
- test_tag0027_b3b_structure_s1s2_next_retreat.py（BDD-4 + S-1/S-2 扩展假协议树）
- test_tag0027_b3b_protocol_check14_check15.py（BDD-15/16/22/24 + 回归）

**跨批/文档断言**（BDD-14 五模式锚点 = 纯文档断言不新增概念）：
- BDD-14 → 归 B3a（grep 断言五模式锚点 + 无 workflow/ralph/goal 模式概念）

用例数草案：BDD-1(2) BDD-2(1) BDD-3(1) BDD-4(2) BDD-5(2) BDD-6(2) BDD-7(2) BDD-8(2) BDD-9(3)
BDD-10(2) BDD-11(1) BDD-12(2) BDD-13(2) BDD-14(1) BDD-15(2) BDD-16(2) BDD-17(1) BDD-18(2)
BDD-19(2) BDD-20(2) BDD-21(1) BDD-22(2) BDD-23(1) BDD-24(1) BDD-25(2) = 43 用例草案 → 细化裁剪至 ~36-40

## 用例清单定稿（36 用例，25 BDD 全覆盖）——进入 P3-test-cases.md 编写

设计决策：
- **新文件承载全部新用例**（不 append 既有大文件）——TAG0027 改 4 域 12+ 文件，P4 四批实现需对应独立测试文件；文件名带 batch 前缀便于 P4 分批对应。
- **实数据面 + 假协议树双轨**：B1 转移表用例断言 worktree 实 phases.yaml/schema（P4 改真文件转绿）；S-1/S-2 扩展 + CHECK 14/15 用假协议树（make_fake_root 风格）避免污染真实协议文件。
- 新增 CLI（agate-next/advance/dispatch）全部 subprocess 测：P3 现状 rc 2（can't open file）→ exit 断言失败 = B 类真红灯；P4 建脚本后转绿。不 mock 被测对象（约束 3）。
- 既有脚本扩展点（check-structure S-1/S-2 加列、check-p6-provenance 审计 2 双锚点、check-judge-verdict exit2 复核、check-protocol CHECK 14/15）：新扩展点行为红（未实现）既有行为绿（回归守卫）——区分 A2 语义。
- BDD-14（五模式锚点）纯文档断言归 B3a；BDD-23 render-dispatch-prompt 既有契约 = 回归断言（现状绿，验证 P4 不改契约）。
- 平台无关：tmp_path/task_dir/git_repo fixture；run_cli(python_exe,...)；显式 utf-8；无裸解释器无 /tmp。
- 红色灯记录与 check-tdd-red 兼容：断言失败 + subprocess 缺脚本 = B 类。

## P3-test-cases.md 已落盘（test_code_dir 声明 + 36 用例 25 BDD 映射表 + 红灯汇总）
- 路径：agate-workspace/tasks/TAG0027-orchestration-semantics/P3-test-cases.md
- 7 个测试文件已定名（B1×4 + B2×2 + B3a×1 + B3b×2），下一步写测试代码

## 测试代码已落盘（9 文件，44 用例）+ 自跑红灯记录

落盘文件（agate/tests/unit/，全部新建）：
- test_tag0027_b1_phases_transfer_fields.py（5 用例：BDD-1×2/2/3 红 + BDD-5 绿）
- test_tag0027_b1_agate_next_cli.py（12 用例：BDD-6×2/7×2/8×2/9×3/11 红 + BDD-13×2 绿）
- test_tag0027_b1_agate_advance_cli.py（2 用例：BDD-10×2 红）
- test_tag0027_b1_judge_exit2_review.py（2 用例：BDD-12 反向红 + 正向绿）
- test_tag0027_b2_agate_dispatch.py（6 用例：BDD-18×2/25 两路红 + BDD-19×2/25 A2 绿）
- test_tag0027_b2_audit2_dual_anchor.py（3 用例：BDD-20 双锚点红 + BDD-20 渲染/21 兜底绿）
- test_tag0027_b3a_platform_name_docs.py（5 用例：BDD-16 注记红 + BDD-14/16 豁免/17 dsh/23 绿）
- test_tag0027_b3b_structure_s1s2_next_retreat.py（3 用例：BDD-4 不一致×2 红 + 一致绿）
- test_tag0027_b3b_protocol_check14_check15.py（6 用例：BDD-22×2/24/15×2/16 豁免 红）

### 自跑红灯记录（worktree 根，`pytest agate/tests/unit/test_tag0027_b{1,2,3a,3b}_*.py -q`）
结果：**30 failed / 14 passed**（2.9s）

失败原因逐类（全部 B 类真红灯，无 A 类假红灯）：
1. subprocess rc 2 "can't open file"（agate-next.py/agate-advance.py/agate-dispatch.py 未实现）
   → BDD-6/7/8/9/10/11/18/25(两路) 全红
2. 数据面字段断言失败（phases.yaml/schema 无 next/retreat/gate_subphase 键）→ BDD-1×2/2/3 红
3. 扩展点行为未实现（check-judge-verdict 无 exit2-resolution 复核项 → 无 resolution 场景 exit 0
   未拦截 → 断言 exit 1 失败）；S-1/S-2 未扩展比对 4/5 列 → 不一致场景 exit 0 → 断言 exit 1 失败；
   审计 2 单锚点剥离 → CARD-SOURCE 与 START 间 PASS 行误报 exit 1 → 断言 exit 0 失败
   → BDD-12/4/20(双锚点) 红
4. 函数缺失（check-protocol-consistency 无 check_md_platform_paragraphs / check_rules_platform_
   tokens → AttributeError）→ BDD-22×2/24/15×2/16(豁免) 红
5. 文档清理未完成（协议文档 0 处 `> 实现注记：`）→ BDD-16(注记) 红

通过（14 = 回归守卫，现状即绿）：
- BDD-5（worktree consistency 0 ERROR）；BDD-13×2（check-gate/check-state-transition 头注释）
- BDD-19×2（手工 inject-card exit 0 + 2p hash）；BDD-25(A2 抽取口径)；BDD-20(渲染 exit 0)
- BDD-21（物理块兜底）；BDD-14（五模式锚点）；BDD-16(豁免表)/17(dsh)/23(render-dispatch-prompt)
- BDD-4 一致场景（加列兼容回归守卫）；BDD-12 正向（resolution 合规 exit 0）

修复记录：test_bdd_13_check_gate_exit_semantics_regression 首跑失败（正则与真实头注释不符，
断言数据矛盾 = 测试代码 bug）→ 改为断言真实头注释文本（exit 0 = gate 通过 / exit 1 = gate
未通过 / exit 2 = 需主 Agent 自判）后绿。无其它断言与数据矛盾。

## P3 收尾自检（全部通过）
- P3-test-cases.md 存在 + 声明 test_code_dir: agate/tests/unit/（grep 3 处确认）
- 9 个测试文件非空（44 用例：30 红 / 14 绿），pytest 正常收集、无 A 类假红灯
- check-tdd-red（TEST_RUNNER 指向新测试 9 文件）exit 0 = B 类真红灯确认
- check-frontmatter P3-test-cases.md exit 0
- BDD 覆盖对照：25 BDD 全覆盖（映射表 25 行）
- 环境隔离：写 agate/tests/unit/（P3 允许落点）+ 任务目录产出，未改协议本体
  [PROD_NOT_TOUCHED]
