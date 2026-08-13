---
phase: P6
task_id: TAG0005-mechanism-fixes
type: acceptance
parent: P5-verification.md
trace_id: TAG0005-mechanism-fixes-P6-20260813
status: draft
created: 2026-08-13
agent: verifier
# ── v2.0 机器汇总 ──
pass: 16
fail: 0
ui_affected: false
---

# P6 验收报告 — agate 机制修复批（TAG0005）

> 验收口径：功能任务标准口径。16 条 BDD（BDD-1..16）逐条实际验证（跑命令 / grep 断言），每条 PASS 引用 P6-evidence/ 下证据文件。本任务为协议/脚本/文档修复，无 UI（`ui_affected: false` 与 P2 声明一致）。

## 验收方法与证据策略

- 脚本行为类 BDD（BDD-3/4/5/6/10/11/16 + BDD-15 守卫）：实跑被测脚本/测试，输出落盘。
- 文档断言类 BDD（BDD-1/2/7/8/9/12/13/14）：grep/sed/rg 断言输出落盘。
- 全部证据文件含实际命令输出，末行 `EXIT_CODE: <n>`。
- 环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`，bats 1.10 / python3 3.12，`[PROD_NOT_TOUCHED]`（全程仅 worktree 测试环境）。

## BDD 逐条验收结果

- PASS BDD-1: backend 域 P2 有机械触发的评审角色——三处 C8 表 backend 行均含 plan-eng-review（P2 方案评审）且保留 review（P4 后），三表均附去重说明(bdd-1-c8-tables.log, bdd-1-c8-rows.log)
- PASS BDD-2: check-gate.sh P2 的 P2-review.md 无条件要求保持原样——L157 仍 `[ ! -f "$P2_REVIEW" ]` exit 1 + L164 status 非 approved exit 1，gate 未放宽(bdd-2-gate-p2.log)
- PASS BDD-3: P5 计数区分主命令与辅助命令——agate-gate-p5-count.py 对 P5+P5_unit+P5_e2e+P5_formatter 输出 `1 2`（formatter 不计 aux）、仅 P5 输出 `1 0`、无块输出 `0 0`，不再合并计 3(bdd-3-p5-count.log, bdd-script-asserts.bats.log)
- PASS BDD-4: check-gate P5 多命令 WARNING 文案区分主/辅——输出「GATE P5 WARNING: P2 声明了 1 个主命令 + 1 个辅助命令（共 2 条 gate_commands.P5 命令）」，不再笼统称「N 个命令」(bdd-4-p5-warning.log, bdd-script-asserts.bats.log)
- PASS BDD-5: 仅主命令（无 P5_*）时不输出多命令 WARNING——仅 P5 fixture 无「辅助命令」WARNING，行为与现状一致(bdd-5-p5-only.log, bdd-script-asserts.bats.log)
- PASS BDD-6: read-p5-commands 执行枚举行为不变——该文件未被本任务修改（git log 无 TAG0005 提交），P5+P5_e2e 仍全枚举 2 条、formatter 仅配对不执行；P5C.1-4 回归守卫全绿(bdd-6-read-p5.log, bdd-script-asserts.bats.log)
- PASS BDD-7: 执行角色派发 prompt 不含「Review 角色特别指令」——render P2 architect 输出 87 行正常渲染，0 命中该节(bdd-7-exec-no-review.log)
- PASS BDD-8: 评审角色派发 prompt 含「Review 角色特别指令」完整语义——render P2 design-review 输出含该节 + status draft/approved/rejected/needs-revision 全部出现(bdd-8-review-instruction.log)
- PASS BDD-9: 同类扫描守卫——`grep -rl 'Review 角色特别指令' agate/` 仅命中 assets/templates/dispatch-prompt.md 单文件（节标题+代码块同文件 2 行，不违反「模板一处」）；render 脚本仅 sed 范围机制引用(bdd-9-review-single.log, bdd-doc-asserts.bats.log)
- PASS BDD-10: 角色文件不存在 → exit 2 + stderr 报错——render P2 nonexistent-role 返回 exit=2 + stderr「角色文件不存在: nonexistent-role」(bdd-10-exit2.log)
- PASS BDD-11: 该行为有 bats 回归测试锁定——RP.17 用例存在（L130 断言 exit 2 + stderr）且实跑 ok；RP.18/19 同套件全绿(bdd-11-rp17.log)
- PASS BDD-12: 空返回恢复策略含「自动重试一次」——dispatch-protocol.md L112「自动重试一次：相同 prompt 原样重发（不占用 retries[Pn] 槽位）」+ L114「自动重试仍空返回 → 进入步骤 b」进入既有 retries[Pn] 流程(bdd-12-13-14-retry.log, bdd-doc-asserts.bats.log)
- PASS BDD-13: 短会话（<1min）空返回触发异常告警——L113「复用下方派发耗时弱信号：若本次会话时长 <1min → 输出『会话时长异常短』告警」(bdd-12-13-14-retry.log, bdd-doc-asserts.bats.log)
- PASS BDD-14: 自动重试不改变现有 retry 上限/PAUSED 规则——P4 提交 diff 未触碰 MAX_RETRY / PAUSED 行；现状 L123「len(retries[Pn]) > MAX_RETRY → PAUSED 报告人工」原样保留(bdd-14-retry-unchanged.log, bdd-doc-asserts.bats.log)
- PASS BDD-15: 全仓 scripts 的「stderr 报错后 exit 0」仅剩显式跳过语义——`rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 仅 3 处命中，消息均含「跳过」语义（agate-capture-env-baseline.sh L23/26/28 跳过基线捕获/非 git 仓库跳过）(bdd-15-scan.log, bdd-doc-asserts.bats.log)
- PASS BDD-16: check-debt.sh --retreat-coverage 依赖加载失败不再静默 exit 0——隔离目录缺 agate-workspace-resolve.sh 时返回 exit=2 + stderr「缺少 agate-workspace-resolve.sh，无法解析工作区，回退覆盖比对无法执行」(bdd-16-check-debt.log, bdd-script-asserts.bats.log)

## 证据与测试套件交叉确认

- 文档断言 bats（BDD-1/2/9/12/13/14/15 文本断言）：check-gate.bats ok 83-89 全绿(bdd-doc-asserts.bats.log)。
- 脚本断言 bats：agate-gate-p5-count.bats GPC.1-3（BDD-3）、agate-read-p5-commands.bats P5C.1-4（BDD-6）、check-gate.bats G5_CMD.1-5（BDD-4/5）、agate-debt-check.bats test_bdd_16（BDD-16）+ test_bdd_13/14/15 有意跳过守卫全绿(bdd-script-asserts.bats.log)。
- P5 全量回归红线（上游证据，本报告引用不重复实跑）：bats 726 ok / consistency 0 ERROR / shellcheck 0 error（P5-test-results/）。

## 结论

16 条 BDD 全部实际验证通过，0 FAIL。四处机制/契约修复（RM-AG0010 C8 补 backend P2 评审、RM-AG0011 P5 主/辅计数、RM-AG0012 自定义角色两瑕疵、RM-AG0003 空返回自动重试）行为符合 P1 验收条件。

**Summary**: 16/16 PASS, 0 FAIL

## 环境隔离

`[PROD_NOT_TOUCHED]`——验收全程仅在 worktree 内运行被测脚本/bats/grep 断言，未接触生产环境。
