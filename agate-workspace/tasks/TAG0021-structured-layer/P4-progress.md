# P4 实现进度（TAG0021-structured-layer，M0 里程碑）

状态标记：[PROD_NOT_TOUCHED]（仅写 worktree；~/.agate 稳定版与主 checkout 未改动）

## 步骤记录

1. [done] 读 implementer 角色文件 + P4-dispatch-context（派发指引、P4 卡片全文）。
2. [done] 读 P2-design.md（C1 方案 §3.1-3.7、M0-1..M0-11、四字段、dispatch_plan serial）。
3. [done] 读 P3-test-cases.md（BDD↔用例映射、假树夹具 seam）+ P2-review.md（5 项非阻塞发现）。
4. [done] 读 P3 测试代码 test_check_yaml_schema.py（8 用例）+ test_check_structure_consistency.py（10 用例）+ _rules_test_utils.py（假树形状）+ conftest.py（run_cli/AGATE_ROOT 契约）。
5. [done] 读 agate_common.py（is_gate_meta_key=line79、resolve_agate_root=line231）、check-platform-assumptions.py（R1-R5 扫描规则）、WORKFLOW.md 阶段总览表（287-299 真实表行）、phase-cards/P2-design.md（S-3 抽检对象）、dispatch-protocol.md（三铁律/五模式/可判定门槛表）、role-system.md、rules/review-mapping.md（C8 映射表）、agate-frontmatter-check.py（SCHEMAS 参照）。
6. [done] 事实核对：真实 WORKFLOW 总览表 P0-P8+P6.5+READY 行；exec_role 列含修饰文本（S-1 需归一化）；CHECK 编号空间 = CHECK 1-12（无 S 前缀）；ruff 未安装（P5_ruff 由主 Agent gate 跑）；CODE-MAP.md 存在（核对表适用）。
7. [done] 写 agate/rules/{phases,dispatch,roles}.yaml（数据面：阶段/门槛/产出/retry_cap/task_fields/三铁律/五模式/gate_commands_syntax/field_readers/C8 映射/角色/脚本注册表）。
8. [done] 写 agate/rules/schema/{phases,dispatch,roles}.schema.json（draft-07 子集：type/required/enum/properties/items/additionalProperties/minItems）。
9. [done] 写 agate/scripts/check-yaml-schema.py（手写子集校验器 + R5 schema 自检）。
10. [done] 写 agate/scripts/check-structure-consistency.py（S-1~S-6 + S-0 编号自校验）。
11. [done] WORKFLOW.md 阶段总览加 S1S2-ANCHOR-START/END 锚点（M0-7）。
12. [now] 跑 M0 两测试文件（test_check_yaml_schema + test_check_structure_consistency），预期 ~1-2min。
13. [done] 首轮全量 pytest：15 failed / 1185 passed——甄别归类：12 项 = M1/M2/M3 预期红灯（reconcile 7 + migration 3 + card_render BDD-13 2）；test_sg_6 = 真实回归（新增 check-*.py 触发锚点表不变式）→ 已修（锚点表纯数据登记 + [SCOPE+]）；test_bdd_7 = 沙箱环境假象（basetemp 在 git 仓库内 → git_ok:true，[CAPABILITY_GAP]）；test_bdd_25 = 全量序偶发（隔离 20 passed 复证）。
14. [done] 锚点表登记后复证：M0 两文件 + test_sg_6 + test_bdd_25 = 20 passed；check-protocol-consistency --strict-errors-only exit 0（CHECK9 WARNING 320→318 消除）；真实树 check-structure-consistency S1-S6+S0 全 OK。
15. [now] 清理 dist/ 后最终全量 pytest（后台 job bash-9，预期仅剩 M1/M2/M3 预期红灯 + CAPABILITY_GAP 环境项）。
16. [done] 最终全量 pytest（job bash-9）：1186 passed / 14 failed / 2 skipped——13 项预期红灯（M1 7 + M2 3 + M3 2）+ 2 项沙箱环境假象（test_bdd_7 git 上下文、test_bdd_25 共享 basetemp 污染 dist/ 一致性扫描，均为 CI 外差异）；test_sg_6 回归已修转绿。零真实回归。
17. [done] 填录 P4-implementation.md 全量回归结果；产出完成。

## M1 轮（implementer，2026-08-22）
- 读了 implementer.md / P4-dispatch-context-implementer.md / P2-design.md / P0-brief.md / P3-test-cases.md / P2-review.md / P4-implementation.md（M0 节）/ test_check_reconcile.py（7 用例契约）
- 下一步：读三脚本 + agate_common + conftest + _rules_test_utils

## M1 轮（重试，2026-08-22）
- [done] 读 implementer.md / P4-dispatch-context-implementer.md / P2-design.md（§3.4 对账 + M1-1..M1-5）/ P3-test-cases.md / P0-brief.md / P2-review.md
- [done] 读 test_check_reconcile.py（7 用例契约，BDD-6/7/8）+ conftest.py（run_cli/CommandResult/output 合并流）+ _rules_test_utils.py
- [done] 读三脚本（agate-read-gate-commands / check-pruning / check-gate P2 分支）+ agate_common.py（is_gate_meta_key/resolve_agate_root）+ agate-md-field-get.py（双读归一化口径）+ M0 YAML（phases/dispatch）
- [done] 读既有测试断言确认回归面：test_check_pruning（substring 断言安全）、test_check_tdd_red（pyx_7 断言 "timeout_seconds" not in output → 对账不 echo 合法 key）、test_dispatch_orchestration（gate_with.output==gate_without.output，两夹具同构 → 对账输出一致）、test_check_gate（substring 断言）
- [done] 环境核对：~/.agate = legacy 软链 → 主 checkout；无 .agate-version；AGATE_ROOT 未设 → 脚本 resolve_rules_root 走脚本路径上溯 = worktree agate/rules/（M0 YAML 可读）
- [done] 复跑 test_check_reconcile.py 确认 7 failed 红灯基线
- [done] 实现 M1-1：agate_common.py 新增对账工具（reconcile_enabled/reconcile_field/reconcile_summary/read_rules_yaml/resolve_rules_root/known_phase_ids/is_legal_gate_key/split_frontmatter/body_field_value/fm_field_value）
- [done] 实现 M1-2：agate-read-gate-commands.py 对账钩子（块键集 vs 声明语法，未声明 key → WARNING + 计数）
- [done] 实现 M1-3：check-pruning.py 对账钩子（P1 risk_level/phases frontmatter↔正文双读）
- [done] 实现 M1-4：check-gate.py P2 分支对账钩子（candidate_count/四字段 + gate_commands 键集）
- [done] 自查 test_check_reconcile.py：7 passed 全绿
- [done] 回归自查：test_check_tdd_red + test_check_pruning + test_dispatch_orchestration = 84 passed；test_check_gate/routing/ci_backstop/dispatch_context_warning/gate_missing_cmds/gate_p5_count/agate_common/gate_key_suffix_audit = 219 passed 1 failed（仅既有 CAPABILITY_GAP 沙箱项 test_bdd_7）
- [done] M0-8 回补：根 AGENTS.md 仓库结构树加 rules/ 一层；根 README.md 文档表加 rules/ 行；agate/AGENTS.md 入口导航加 rules/ 行
- [done] 协议一致性 --strict-errors-only 0 ERROR、结构一致性 S1-S6+S0 全 OK（M0 不受 M1 影响）
- [done] 全量 unit 回归：1062 passed / 7 failed / 2 skipped——7 项全为预期红灯（M2/M3：card_render×2 + structure_migration×3）+ 环境项（routing CAPABILITY_GAP、env_adapt 共享 basetemp），零 M1 真实回归
- [done] 真实任务 check-gate P2 对账：0 mismatches（candidate_count 3==3）、exit 2 原语义、无噪音
- [done] 4 脚本 ast 语法校验 OK；AGATE_RECONCILE=off 降噪验证（无 RECONCILE 输出，exit 0）
- [done] P4-implementation.md M1 节落盘（改动清单 + 7 变绿 + 2 新 DESIGN_GAP + M0 3 条 REVIEWED 标记 + 核对表 N/A）+ README/AGENTS rules/ 回补

## M2 轮（implementer，2026-08-22）
- 读 implementer.md / P4-dispatch-context（M2 范围 1-7）/ P2-design.md（§3.3/§3.4/§3.5 M2-1..M2-7）/ P3-test-cases.md（BDD-9/10/11 契约）/ P2-review.md（非阻塞 1-5）/ P4-implementation.md（M0/M1 节）
- 读 test_structure_migration.py（4 用例：BDD-9 两字面模式零命中 + BDD-10 三处阻断）+ test_check_reconcile.py（7 用例：对账桥接语义须保持）+ _rules_test_utils.py + conftest.py
- 读四脚本现状（agate-read-gate-commands / check-pruning / check-gate P2 分支 / agate-md-field-get）+ agate_common（M1 对账工具）+ check-structure-consistency（M0 常开阻断）
- 读 pre-commit-gate.py（2j 区域）+ protocol-tests.yml（consistency job）+ UPGRADING.md（v0.59.0 当前，新章节 = v0.60.0）+ 真实 rules YAML（phases/dispatch）
- 事实核对：BDD-9 禁令字面量现状 = agate-read-gate-commands:52（块正则）+ check-gate:625（块正则）+ check-gate:710（四字段正则）；agate-gate-missing-cmds.py:17 也有块正则但不在 _MIGRATED_SCRIPTS 扫描清单（本轮不动，最小范围）；test_b3 fake 根无 check-structure-consistency.py（pre-commit 新 step 须对脚本缺失 fail-open）
- [now] M2-0 对账清零确认：实跑 test_check_reconcile（预期 7/7 绿）+ BDD-9 当前红灯基线 + 真实树 check-gate P2 0 mismatches
- [done] M2-0 对账清零确认：test_check_reconcile 7/7 绿 + 真实任务 check-gate P2 `RECONCILE SUMMARY: 0 mismatches across 1 fields`（无残留差异，允许切换）
- [done] BDD-9 红灯基线确认：test_structure_migration 3 failed（bdd_9 + precommit + ci）1 passed（bdd_10_script_drift M0 已阻断）
- [done] M2-1 共享解析抽公共库：agate_common 新增 parse_gate_commands_block + count_p2_declared_fields（块正则 + 四字段正则迁入，BDD-9 消费脚本字面归零）
- [done] M2-1 agate-read-gate-commands.py：块解析改调 parse_gate_commands_block（删内联块正则）；check-gate.py：_gate_commands_block_keys + 四字段计数改调共享助手（删 2 处内联正则 + import fallback 同步）
- [done] BDD-9 扫描验证：4 脚本两字面量命中 0；py_compile 三脚本 OK
- [done] 回归验证：test_check_reconcile + test_check_gate + test_check_tdd_red = 217 passed（read-gate-commands 消费链未破坏）
- [done] M2-2 agate-md-field-get.py：文档头补「两类字段」节（任务数据 vs 协议规则，协议规则不经本工具读取）
- [done] M2-4 pre-commit-gate.py：2j.2 追加结构一致性 step（与 check-gate 并列不短路；脚本缺失 fail-open，test_b3 fake 根兼容）
- [done] M2-5 protocol-tests.yml：consistency job 追加 check-structure-consistency 步骤
- [done] M2-7 UPGRADING.md v0.60.0 章节（①三脚本切 YAML 权威源 ②一致性 gate 提升阻断 ③rules 数据层纯增量 + 通用升级动作）
- [now] M2 自查：test_structure_migration 4/4 + test_check_reconcile 7/7
- [done] M2 自查：test_structure_migration 4/4 + test_check_reconcile 7/7 = 11 passed
- [done] 全量 pytest（后台）：1196 passed / 4 failed / 2 skipped——4 项 = M3 预期红灯（card_render BDD-13 ×2）+ 已登记沙箱环境假象（routing test_bdd_7 CAPABILITY_GAP + env_adapt test_bdd_25 basetemp 污染，清理 dist/ 后隔离通过复证）；M1 14 failed → 4 failed 恰减 10（reconcile 7 + structure 3 转绿），零真实回归
- [done] count-tests = 1202 ≥ 749；consistency --strict-errors-only 0 ERROR；structure S1-S6+S0 OK；schema OK；platform 扫描 exit 0
- [done] 真实树冒烟：check-gate P2 0 mismatches + agate-read-gate-commands JSON 输出正确
- [done] P4-implementation.md M2 节落盘（改动清单 + 11 变绿 + 2 新 DESIGN_GAP + 1 SCOPE+ + 核对表 N/A + 全量回归分类）
- [done] 最终自查复证：UPGRADING v0.60.0 章节在（行 92）；DESIGN_GAP 总数 7（M0 3 + M1 2 + M2 新增 2）；BDD-9 命中 0
- [done] M2 完成：M2-0..M2-7 全部落地，产出 P4-implementation.md M2 节

## M3 实施步骤（implementer，2026-08-22）

- M3-0 读输入：P2-design §3.6/M3-1..5 + P3-test-cases（BDD-12/13/14）+ P2-review 非阻塞 1-5 + P0-brief；读实现对象 agate-inject-card.py / agate-next-card.py / check-structure-consistency.py / rules/phases.yaml + dispatch.yaml。
- M3-0 测试基线确认：test_card_render.py = 2 passed（BDD-12 随 M0 S-3 抽检已绿）+ 2 failed（BDD-13 注入渲染未实现，符合派发声明）。
- M3-0 关键设计判定：BDD-13 注入测试在假树拷贝 agate-next-card.py → 渲染器须内嵌 next-card（自包含，agate_common 缺失回退 env AGATE_ROOT）；真实卡片含 `## ` 节 → 原样输出保字节稳定（test_nc_* sha256 契约），裸模板（无 `## ` 节，如假树 P3-tdd.md）→ 从 rules/phases.yaml 渲染产出/派发/gate/retry 节。
- M3-0 硬约束确认：test_docs_assertions / test_protocol_mechanism_anchors / test_p2p4_boundary_docs 断言真实卡片叙事文本 → 真实卡片不可破坏性重写（"渲染化不改变人类可读叙事"）。
- M3-1 实现：agate-next-card.py 内嵌渲染器（_load_phases / _render_sections / _needs_render：裸模板无 `## ` 节 → 从 rules/phases.yaml 渲染产出/派发/gate/retry 四节追加；正式卡片原样输出保字节稳定）；agate-inject-card.py 文档化 M3 渲染路径。
- M3-2 实现：check-structure-consistency.py S-3 升级（孤儿卡片防护 + 有卡片阶段输出文件整卡级对账；P2 试点锚点保留）。
- M3-3 自查：test_card_render.py 4 passed（BDD-13 两例转绿，BDD-12 两例保持）；test_agate_next_card + test_agate_inject_card + test_agate_card_inject 35 passed（字节稳定/注入 hash 契约未破坏）；test_check_structure_consistency 10 passed。
- M3-4 自查：全量 pytest 1198 passed / 2 failed（均已登记 [CAPABILITY_GAP] 沙箱项：test_bdd_7 git-repo basetemp + test_bdd_25 dist 污染；隔离复跑前者仍红后者绿）/ 2 skipped——零真实回归；consistency 0 ERROR；structure S1-S6+S0 OK（0 漂移）；schema OK；count-tests 1202 ≥ 749；platform-assumptions 0 命中。
- M3-5 状态标记：[PROD_NOT_TOUCHED]（仅 worktree 写；主 checkout 未动）。

## ruff 修复轮（P5 回退，2026-xx）
- [x] 读取 implementer.md + P4-dispatch-context-implementer.md + P0-brief.md
- [x] 确认 ruff 状态：70 errors（UP031 38 / RUF100 13 / E731 11 / PLW0603 2 / I001 2 / W292 2 / F401 1 / SIM102 1），与诊断一致
- [ ] 跑 ruff --fix 自动修复
- [ ] 手修剩余（E731/SIM102/PLW0603 等）
- [ ] 验证：ruff 0 errors + unit 无新增失败 + consistency 0 ERROR + structure S 全 OK + count-tests 1202
- [ ] P4-implementation.md 追加修复轮小节

- [x] 跑 ruff --fix 自动修复（18 处：RUF100 13 / I001 2 / W292 2 / F401 1）
- [x] 手修 52 处：
  - agate_common.py：PLW0603 2（global→_RECONCILE_STATE dict，行为等价）+ UP031 2 + RUF010 2（!s 修复）
  - check-gate.py：E731 8（lambda→def）
  - check-pruning.py：E731 3（lambda→def）
  - pre-commit-gate.py：SIM102 1（嵌套 if→and 合并）
  - check-structure-consistency.py：UP031 20（%→f-string，%r→!r）
  - check-yaml-schema.py：UP031 16（%→f-string，%r→!r）
- [x] ruff check agate/ = 0 errors（exit 0）
- [ ] 验证：unit 无新增失败 + consistency 0 ERROR + structure S 全 OK + count-tests 1202
- [x] 启动验证：unit pytest
- [x] 验证完成：unit 2 failed（=允许的 test_bdd_7/25 环境假象，1067 passed 无新增失败）/ consistency 0 ERROR（清 dist 后 exit 0）/ structure S 全 OK / count-tests 1202
- [x] P4-implementation.md 追加「ruff 修复轮」小节
