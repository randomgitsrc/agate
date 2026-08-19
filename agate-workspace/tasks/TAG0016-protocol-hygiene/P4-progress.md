
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

## P4 SELF-GATE 修复轮（trace_id: TAG0016-P4-selfgate-fix-20260819）

- 已读 dispatch-context P4-dispatch-context-implementer-selfgate-fix.md
- 已读 docs/reviews/agate-alignment-review-2026-08-19.md A1-c/A3/A5/A7 四节完整原文
- 已读 agate/scripts/check-p6-provenance.py 现有实现（main() 结构、audit7_p5_evidence_reuse 函数）
- 已读 agate/phase-cards/P8-release.md L82-85、agate/dispatch-protocol.md「全量重跑点审计」表 L453-462
- 已读 agate/assets/execution-roles/verifier.md「refactor 任务验收口径」节 L171-180
- 已读 agate/assets/templates/dispatch-prompt.md「P5/P6 派发追加」节 L158-197
- 已读 agate/adr.md ADR-002/ADR-004/ADR-009 格式参照
- 开始实现修复目标 1：--audit7-only CLI 模式
- 修复目标 1 script 改动完成：check-p6-provenance.py 新增 --audit7-only 模式（_load_state_yaml
  提取复用 + _run_audit7_only）。手工验证三态：reuse_allowed exit0 / reuse_blocked exit1 /
  no_reuse_claim_possible exit0，输出行 `AUDIT7_RESULT: <state>`，均符合规格。
- 修复目标 1 文档同步完成：P8-release.md L82-86（改为可执行命令 + AUDIT7_RESULT 三态判定步骤）、
  dispatch-protocol.md「全量重跑点审计」表 P8 行（同样改为具体命令 + AUDIT7_RESULT 判定）。
- 开始实现修复目标 2：verifier.md + dispatch-prompt.md 补充新机制说明
- 修复目标 2 完成：verifier.md「refactor 任务验收口径」节后新增「引用 P5 证据、不重跑（P6 模式，
  TAG0016 BDD-12/13）」小节（判定权归主 Agent，指向 P6-acceptance.md 权威节，不复制完整规则）；
  dispatch-prompt.md「P5/P6 派发追加」节加一句指针，指向 verifier.md 新增小节。
- 开始实现修复目标 3：ADR-010
- 修复目标 3 完成：adr.md 末尾新增 ADR-010（受控例外——满足客观可判定条件时允许复用既有验证
  证据），格式参照 ADR-002/ADR-004（状态/语境/决策/理由/后果五节）。
- 三个修复目标代码/文档改动均已落盘，准备新增 --audit7-only CLI 测试用例并跑全量 pytest。
- 新增 4 条 --audit7-only CLI 测试用例（test_check_p6_provenance.py，未改动已有测试断言逻辑）：
  reuse_allowed exit0/stdout、reuse_blocked exit1/stdout、no_reuse_claim_possible exit0/stdout、
  缺 TASK_DIR 参数 exit1。全部通过。
- 全量 pytest 跑完：963 passed, 2 skipped, 0 failed（基线 959 passed + 新增 4 条，无回归）。
- 返回前自检：grep 确认各文件改动落盘 + 手工 CLI 验证三态输出格式，均通过。准备写
  P4-implementation-selfgate-fix.md。
- P4-implementation-selfgate-fix.md 已用 Write 工具写入指定路径，含正确 header 与 3 个修复
  目标摘要。本轮任务完成，准备返回。

## P4-review（review 子 Agent，2026-08-19）
- 审查对象：check-protocol-consistency.py CHECK12（行 914-1019）、check-p6-provenance.py 审计7+--audit7-only（行 61-222）、7 份协议文档去重抽查
- 发现 2 个 CRITICAL：
  1. audit7_p5_evidence_reuse（check-p6-provenance.py:179）忽略 git diff 返回码，git 命令失败时静默判为 reuse_allowed（已用最小复现验证：伪造不存在的 commit hash 得到 RESULT: reuse_allowed，应拦截）
  2. redeclares_table（check-protocol-consistency.py:944-956）对指针文件做无范围全文扫描，未采用姊妹函数 extract_md_table_int_column 已用的小节限定策略，与本任务修复过一次的"误吞同形态表格行"同根因，存在潜在误报
- 4 个 INFORMATIONAL：must_not_redeclare_table 死配置key / exists+read_text 无 try-except（全文件既有模式）/ pyyaml 缺失被 except Exception 静默吞掉无诊断信号 / MAX= 正则无上下文锚定
- 协议文档去重抽查（dispatch-protocol.md 派发 prompt 模板骨架 + state-machine.md/state-transitions.md/WORKFLOW.md/platform-notes.md 指针句）未发现新问题
- 产出：P4-review.md，status: rejected

## P4-review 修复轮进度（trace_id: TAG0016-P4-reviewfix-20260819）

- [已读] dispatch-context P4-dispatch-context-implementer-review-fix.md
- [已读] implementer.md 角色定义
- [已读] P4-review.md 全文：CRITICAL-1（audit7 git 返回码未检查，check-p6-provenance.py:179）+
  CRITICAL-2（redeclares_table 无小节限定，check-protocol-consistency.py:944-956）
- [已读] check-p6-provenance.py 全文（audit7_p5_evidence_reuse 行 164-188）
- [已读] check-protocol-consistency.py CHECK12 段（行 914-1020）
- [核实] agate/rules/state-transitions.md 确实有「## 重试上限」小节（行 56-60），
  只含指针句无表格 → 小节限定方案对真实文件可行

- [已改] agate/scripts/check-p6-provenance.py：audit7_p5_evidence_reuse 检查 `_run_git`
  返回码，rc != 0 时 fail-closed 返回 reuse_blocked，stderr 诊断信息与"检测到改动"分支
  分开（不同性质失败不合并消息）
- [已改] agate/scripts/check-protocol-consistency.py：
  - 新增 extract_section(text, heading) 通用小节裁剪辅助函数（原 extract_md_table_int_column
    内联逻辑抽取为共用函数）
  - extract_md_table_int_column 改为调用 extract_section
  - check_authoritative_values 调用 redeclares_table 前先用 extract_section(text,
    RETRY_LIMIT_HEADING) 裁剪出「## 重试上限」小节文本，找不到该标题则回退全文扫描（保持
    既有行为不变，不引入新漏报）
  - 顺手修复 INFO-1：must_not_redeclare_table key 现被实际读取（默认 True）

- [已加测试] test_check_p6_provenance.py: test_p4_review_critical1_git_diff_command_fails_fail_closed_reuse_blocked
  + test_audit7_only_p4_review_critical1_fake_commit_git_fails_exit1（单元 + CLI 两层覆盖）
- [已加测试] test_check_protocol_consistency.py: test_p4_review_critical2_unrelated_table_outside_section_no_false_positive
- [已跑] 全量 pytest：966 passed, 2 skipped, 0 failed（基线 963 + 新增 3 条）
- [已写] P4-implementation-reviewfix.md
- [完成] P4-review 修复轮结束

## P4-review 复审第 2 轮（2026-08-19，agent: review）

- 核对 CRITICAL-1 修复代码（check-p6-provenance.py:164-206 `audit7_p5_evidence_reuse`）：
  `rc != 0` 时 fail-closed 为 `reuse_blocked`，stderr 文案与"确实检测到改动"分支不混淆。
  自跑 `pytest -k critical1`：2 passed。
- 核对 CRITICAL-2 修复代码（check-protocol-consistency.py `extract_section` + 调用处小节裁剪）：
  `check_authoritative_values` 已先用 `extract_section(text, RETRY_LIMIT_HEADING)` 裁剪再传给
  `redeclares_table`，未找到标题时回退全文（不引入新漏报）。自跑 `pytest -k critical2`：1 passed。
- 自跑全量：`timeout 180 python3 -m pytest agate/tests/ -q --tb=short` → 966 passed, 2 skipped,
  0 failed，与预期基线一致。
- 结论：2 个 CRITICAL 均验证修复到位，无新问题。P4-review.md 已覆盖重写，status: approved。

[orchestrator] commit 880269d 触发 SELF-GATE WARNING（commit message 未含 self-gate-review/skip 标记，
系疏漏）。判断：本次改动（CRITICAL-1/2 fail-closed 修复）不改变 check-protocol-consistency.py
CHECK 12 / check-p6-provenance.py 审计7 的协议层三态语义（reuse_allowed/reuse_blocked/
no_reuse_claim_possible 含义不变，只是修正了两处判定逻辑的正确性缺陷），不涉及任何 agate/*.md
协议文档改动，且改动的两处函数已被 P4-review（偏执 Staff Engineer 视角）两轮深度代码级评审
（第 1 轮发现问题+复现，第 2 轮验证修复），protocol-alignment-review 的 A1-A7 协议-脚本语义对齐
问题不适用于这类纯 bug 修复。补记 self-gate-skip 理由：CRITICAL 修复不改变协议语义，已被 P4-review
两轮代码级评审覆盖，不重复派发 protocol-alignment-review。commit message 未能及时写入此标记是
本次操作的疏漏，此处补记存档，不重新 commit（遵循"不 amend"纪律）。
