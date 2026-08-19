
## P4 batchA (doc-dedup) progress log

- [read] dispatch-context, implementer.md role, P2-design.md, P0-brief.md, P1-requirements.md 3.1-3.8, test_protocol_dedup_audit.py — 已读完，确认改动清单 M1-M12（M13 不动）
- [done] WORKFLOW.md: M3(职责边界声明行) + M2(阶段总览分工声明) + M1(平台适配收窄为指针) 已落盘
- [done] dispatch-prompt.md: M8(文件头矛盾声明修正) + 补充 refactor 任务追加节（发现 dispatch-protocol.md 独有内容未见于 dispatch-prompt.md，先迁移避免内容丢失，见后续 DESIGN_GAP 标注）
- [done] dispatch-protocol.md: M7(职责边界声明行) + M5(可判定门槛规范分工声明) + M4(平台适配收窄，保留 OpenCode issue #29616 调用坑位) + M6(派发 prompt 模板收窄为骨架+指针，431-682 行收窄为 20 行)
- [done] state-machine.md: M10(职责边界声明行) + M9(重试上限权威源声明)
- [done] rules/state-transitions.md: M11(重试上限表改为指针句)
- [done] platform-notes.md: M12(职责边界声明行)
- [next] 跑 test_protocol_dedup_audit.py 自查
- [self-check] test_protocol_dedup_audit.py: BDD-1/2/3/4/5/7 (+回归 BDD-16/18) 变绿；BDD-11/14/15 保持红（预期，batch3 范围）
- [regression found+fixed] 全量 pytest 自查发现 M6 收窄误伤两处既有绿灯：
  (1) test_check_gate.py::test_tag0005_bdd_9_review_role_instruction_single_file（"Review 角色特别指令"字面串在骨架列表里意外重复出现）
  (2) test_protocol_mechanism_anchors.py 三条 BDD-13 用例（"命令超时兜底"/"层级 4"/"×1.5" 关键词随整段收窄被删除）
  已修复：骨架列表改用"评审角色专属指令"措辞避免重复；骨架新增一行保留"命令超时兜底（层级 4...×1.5）"关键词+指针。
- [confirmed pre-existing, out of scope] test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff 失败 — ruff 报的是 test_protocol_dedup_audit.py 自身的 lint 问题（import 排序 + E741 变量名 l），属测试代码，dispatch-context 明确禁止改测试代码，未处理。
- [self-check] 全量 python3 -m pytest agate/tests/ -q：944 passed, 15 failed（全部落在 check12/provenance/dedup 后两批 scope 内，或上述 ruff 预存问题），2 skipped
- [self-check] check-protocol-consistency.py（非 strict）：0 ERROR，仅既有 308 WARNING，与改动前基线一致
- [done] P4-implementation.md 写入完成，DESIGN_GAP 计数=1，返回前自检完成

## [batchB] check12-anti-recurrence 实现进度

- 读取 dispatch-context + P2-design.md §2（CHECK 12 完整设计伪代码）+ 现有 CHECK 4/9/11 实现风格 + 7 条相关测试断言。
- 读取批次1迁移后真实文档：agate/state-machine.md「## 重试上限」表（表头列名实为 MAX_RETRY，非 MAX，故 extract 用列位置而非列名解析）；agate/rules/state-transitions.md 已是纯指针句「详见 `state-machine.md`《重试上限》——权威唯一来源」；8 张 phase-cards 的 MAX= 内联行确认存在且与权威表一致（P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2）。
- 已实现：extract_md_table_int_column()（限定扫描「## 重试上限」小节，避免误吞 state-machine.md L30 任务追踪表里同形态的 "| P4 | 0 | ... |" 行）+ redeclares_table()（阈值3组匹配判定重复表格）+ AUTHORITATIVE_VALUE_ANCHORS（retry-max 锚点）+ check_authoritative_values() + 注册进 CHECKS 列表 + docstring 编号表追加 CHECK 12 一行。
- 下一步：跑 test_check_protocol_consistency.py 7 条 CHECK 12 用例自查 + 跑 check-protocol-consistency.py --strict 全仓确认 0 ERROR。

## [batchB] check12-anti-recurrence 完成

- 代码改动确认已落盘（grep 确认 AUTHORITATIVE_VALUE_ANCHORS / check_authoritative_values / CHECKS 注册均存在）。
- test_check_protocol_consistency.py: 23 passed（7 条 CHECK 12 用例全绿，既有 16 条未破坏）。
- check-protocol-consistency.py --strict: CHECK 12 PASS，全仓 0 ERROR（exit=2 仅因既有 308 条 WARNING，与本批次无关）。
- 全量 pytest: 8 failed / 951 passed / 2 skipped（失败数从 15 降到 8，均为批次3范围/ruff lint，非本批次范围）。
- 已写 P4-implementation-batchB.md。

## [batchC] test-evidence-provenance 实现进度

- 读取 dispatch-context + 角色定义 + P2-design.md §1.1(M16-M23)/§3(BDD-12/13 完整设计+§3.2 R9)/§10 + check-p6-provenance.py 现有六道审计风格 + test_check_p6_provenance.py 4 条 audit7 测试断言 + conftest GitRepo fixture + test_protocol_dedup_audit.py BDD-11/14/15 三条测试断言。
- 确认落点：dispatch-protocol.md L453 前插入 M16 新小节；state-machine.md L404-456「每任务独立状态文件」插入 p5_pass_commit；P5-verification.md L13-15 步骤4-5间插入写入步骤+R9操作纪律；P6-acceptance.md 新增引用P5证据分支（约L130后）+gate规则行更新；P8-release.md L82 精简为条件化表述；.github/workflows/protocol-tests.yml pytest job 新增 continue-on-error xdist 观测步骤。
- 下一步：逐条实现 M16-M23。

## [batchC] test-evidence-provenance 完成

- 代码/文档改动确认已落盘（grep 确认 M16-M23 七处落点均存在：dispatch-protocol.md「## 全量重跑点审计」、check-p6-provenance.py 的 EXCLUDE_PRODUCE_PREFIX/audit7_p5_evidence_reuse/p6_declares_reuse、state-machine.md/P5-verification.md 的 p5_pass_commit、P6-acceptance.md 引用P5证据分支、P8-release.md 复用表述、protocol-tests.yml xdist观测步骤）。
- test_check_p6_provenance.py: 45 passed（4 条审计7用例全绿，既有41条未破坏）。
- test_protocol_dedup_audit.py: 16 passed（BDD-11/14/15 全绿，既有 BDD-1/2/3/4/5/7/16/18 回归防护未破坏）。
- 全量 pytest: 958 passed / 1 failed / 2 skipped——唯一失败是既有 ruff lint 问题（test_protocol_dedup_audit.py 测试代码自身 I001/E741，批次1遗留，不可改测试代码，dispatch-context 明确排除范围）。本批次新代码自查 ruff check 已过（修复了自己引入的 RUF005 list 拼接警告）。
- check-protocol-consistency.py（非 strict）：0 ERROR，308 WARNING，与批次2基线一致。
- 未改动批次1/2已完成部分；DEBT0010 与本批次无交集未修复。无 DESIGN_GAP/SCOPE+/CLARIFY。
- 已写 P4-implementation-batchC.md。三批次全部完成，等待主 Agent 全批次汇总。
