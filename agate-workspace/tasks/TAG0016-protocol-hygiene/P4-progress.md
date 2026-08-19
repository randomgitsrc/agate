
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
