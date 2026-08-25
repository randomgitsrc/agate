---
phase: P7
task_id: TAG0023-mechanism-checks
type: consistency
parent: P2-design.md
trace_id: TAG0023-P7-20260825
status: draft
created: 2026-08-25
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---

# P7-consistency.md — TAG0023 一致性交叉检查

> [PROD_NOT_TOUCHED] 只读跨文件核对，无生产环境写操作。

## 1. DESIGN_GAP 配对检查

**结论：机械层面无需配对（design_gap_count=0），附一条 WARNING 级观察。**

- 已核实 `P4-implementation.md` 全文不含任何 `[DESIGN_GAP:` 行首标记，`check-gate.py` P7 门槛只扫描 `P4-implementation.md`，因此机械层面不存在"P4 声明但 P7 未转抄"的缺口。
- `[WARNING]` 但 `P4-progress-batchA.md`（L23-27）记录了一处**真实的过程内设计歧义**：`P2-design.md §2.1` 对 BDD-2 条件的字面表述（"暂存版本 `retries[new_phase]` 长度未大于 HEAD 版本长度"）未显式要求 `old_retries_len>0`，implementer 最初据此实现会误拦 `test_st_archive_1/2/3/6` 四个既有回归测试（这些场景 HEAD/暂存 `retries[new_phase]` 均从未记录过，历史上一直由检查4的 stale-outputs 规则单独把关）。该歧义在同一批次（batch A）实现过程内被发现（`[test]` 首次全量跑回归失败）→ 记录为过程内 `[DESIGN_GAP:]`（L23-27）→ 当场修复（新增 `old_retries_len>0` 守卫）→ 复跑验证（`[fix] 加 old_retries_len>0 守卫后重跑：40 passed（30 既有 + 10 新增全绿，无回归）`）。
- **判定：不需要在 `P4-implementation.md` 补记 `[DESIGN_GAP:]` 标记，不阻断。** 理由：①`P4-implementation.md` 按其自身定位描述的是**最终交付状态**（"实现总结"），而不是过程记录——最终交付代码不存在遗留偏差，`P2-design.md §2.1` 的字面表述缺口已在同阶段闭环，不构成"设计与最终实现之间的遗留落差"；②`P4-progress-batchA.md` 已完整记录发现→讨论→修复→复验的全过程，审计痕迹完整，不依赖 `P4-implementation.md` 补记也可追溯；③若强行在 `P4-implementation.md` 补记一条"已解决"的 DESIGN_GAP，反而会与该字段"标记交付时仍存在的设计-实现落差"的语义不符，制造无意义的配对负担。
- 该 WARNING 观察项本身不计入 `design_gap_count`/`design_gap_reviewed_count`（frontmatter 均为 0，按 dispatch-context 约定）。

## 2. SCOPE+ 闭环

**结论：全程无 SCOPE+ 增补，闭环确认，无需 SCOPE_RESOLVED 配对。**

- `P1-requirements.md` §7「待确认清单与提案」声明 `[NO_NEED_CONFIRM]`（无 SCOPE+ 项，仅有 5 条 `[SUGGEST: D1~D5]` 倾向性建议留痕，非 SCOPE+ 增补请求）。
- `P4-implementation.md`「[SCOPE+] 声明」节原文："无。四批实现均严格按 P2-design.md 已批准范围执行，RM-AG0032 时序调整是编排层面的执行时机决策（不改变 BDD 语义/验收标准），不构成范围外改动。"
- 两端一致：P1 起点无 SCOPE+，P4 终点确认无 SCOPE+ 增补，闭环成立。

## 3. 跨文件一致性

### 3.1 P1 BDD-1~13 与 P6 PASS-1~13 逐条内容核对（非仅数量对比）

| BDD | P1-requirements.md §6 内容锚点 | P6-acceptance.md 对应结论 | 核对 |
|-----|------|------|------|
| BDD-1 | §6.1 评审 rejected 类门槛失败事件缺失对应 retries 记录时被拦截（阻断/WARNING 双路径可判） | §6.1 "评审 rejected 类门槛失败事件的对应性校验用例全部通过——`bdd_1` 前缀 6 个用例（含两个负面锚点 `implementer-review-fix`、`consistency-reviewer` 均不误命中）" | 一致：负面锚点即 P2-design.md §2.1 D6 核实的两个真实假阳性样本 |
| BDD-2 | §6.1 P5→P4 回退类门槛失败事件缺失对应 retries 记录时被拦截 | §6.1 "含首次单步回退回归用例 `test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1`" | 一致：对应 P4-progress-batchA.md 记录的 `old_retries_len>0` 守卫场景 |
| BDD-3 | §6.1 子代理空返回重派类门槛失败事件缺失对应 retries 记录时被拦截 | §6.1 "含分批命名回归用例 `test_bdd_3_progress_batch_named_file_detected`" | 一致 |
| BDD-4 | §6.1 正常路径不受影响（回归防呆） | §6.1 "正常路径回归防呆用例通过——无门槛失败事件 + retries 为空 → exit 0 无 WARNING" | 一致，逐字对应 Given/Then |
| BDD-5 | §6.2 P8 完成时关联 roadmap RM 条目未回写 done 被拦截 | §6.2 "P8 gate 关联 roadmap RM 条目未回写 done 时被拦截（exit 1）用例通过" | 一致 |
| BDD-6 | §6.2 无关联 RM 记录时不误拦 | §6.2 "无关联 RM 记录时不误拦（exit 0 继续既有流程）用例通过" | 一致 |
| BDD-7 | §6.2 RM-AG0032 历史数据补记为 done | §6.2 "单测通过，且直接 grep roadmap.md 实测确认 L32 存在 `RM-AG0032 \| ... \| done \| ... \| 2026-08-24 \|` 记录行" | 一致，双证据（测试+真实数据） |
| BDD-8 | §6.3 复现定位计划 + 已知证据基线四要素落盘 | §6.3 "四要素齐全断言用例通过（已知证据基线/判定标准/集中清单位置/CI flaky 重跑触发条件）" | 一致，四要素逐项对应 P1 BDD-8 Then 条款 |
| BDD-9 | §6.3 test_bdd_14 连续 5 次 CI 稳定 | §6.3 "连续 5 次真实 GitHub Actions CI 触发均 conclusion=success（run id 32800038697/32800344966/32800650000/32800954146/32801251214）" | 一致，真实 CI 证据 |
| BDD-10 | §6.3 环境敏感测试集中清单存在（含 test_bdd_7/25/14 三条目） | §6.3 "`ENV-SENSITIVE-TESTS.md` 存在且含 test_bdd_7/test_bdd_25/test_bdd_14 三条目（各含根因分类字段）" | 一致 |
| BDD-11 | §6.4 声明格式错误在写入时即报 | §6.4 "dispatch-prompt.md 含'P1/P2 声明写时自检'小节文本的断言用例通过" | 一致 |
| BDD-12 | §6.4 错误信息含具体行号+修复提示 | §6.4 "含缺失必填字段错误提示、非法枚举值错误提示两类用例" | 一致 |
| BDD-13 | §6.4 commit 时格式折返归零（TAG0019 三类历史用例） | §6.4 "TAG0019 三类历史用例（coupling_checklist 非 list 声明/全角冒号/源码数 6>5）在写时全部被拦截的回归用例全部通过" | 一致，三类逐一对应 |

13 条 BDD 编号在 P1 与 P6 两份文件中所指内容逐一核实一致（非仅数量匹配），无错位映射。P6 frontmatter `pass: 13, fail: 0` 与正文 13 条 PASS 记录数量吻合。

### 3.2 P2-design.md `packages: [agate]` 声明

`P2-design.md` frontmatter（L11）声明 `packages: [agate]`，与 `P1-requirements.md` frontmatter（L14）声明一致，理由（P2-design.md §3）："agate 协议本体单一版本单元，4 子项改动面均在此包内"，声明存在且合理。**P8-release.md 尚未产出，`packages` 与 P8 release bump 范围的一致性核对留待 P8 阶段，本轮不阻断。**

### 3.3 P4-implementation.md 4 批改动文件清单 vs P2-design.md §1.1「改什么」表 / dispatch_plan 5 批声明

`P2-design.md` frontmatter `dispatch_plan.batches` 声明 5 批：`batch-A-RM-AG0042` / `batch-B-RM-AG0043` / `batch-C-RM-AG0044` / `batch-D-RM-AG0045` / `batch-E-RM-AG0032-manual`。`P4-implementation.md`「批次与改动文件」表实际落地 4 批（A/B/C/D），第 5 批（E，RM-AG0032 人工补记）未独立成批，而是**并入批次 B**：

| 批次 | P2-design.md §1.1「改什么」声明文件 | P4-implementation.md 实际改动文件 | 核对 |
|------|------|------|------|
| A（RM-AG0042） | `check-state-transition.py` + `state-transitions.md` + `state-machine.md` + `dispatch-protocol.md`/`WORKFLOW.md` | 同左（P4-progress-batchA.md 末尾 `git status` 确认仅 5 个范围内文件被改动） | 吻合 |
| B（RM-AG0043） | `check-gate.py` `gate_p8()` + `roadmap.md`（原 §2.2 计划 RM-AG0032 补记在 P8/批次E执行） | `check-gate.py` + `roadmap.md`（RM-AG0032 补记提前并入本批） | **有意偏差，已在 P4-implementation.md「编排决策记录」节明确记录并说明理由**：P3 已写的 `test_bdd_7` 断言属标准 pytest 套件，不符合 `known-failures.md` 登记条件，若拖到 P8 会导致 P5-P7 全程红灯卡 gate；主 Agent 判定 BDD-7 验收语义不因提前执行改变，遂提前到 batch B 完成 |
| C（RM-AG0044） | `check-debt.py` + 新建 `ENV-SENSITIVE-TESTS.md` + `protocol-tests.yml` | 同左 | 吻合 |
| D（RM-AG0045） | `dispatch-prompt.md` + `agate-frontmatter-check.py` | 同左 | 吻合 |

**文件集合两两不相交核实**：A={check-state-transition.py, state-transitions.md, state-machine.md, dispatch-protocol.md, WORKFLOW.md}；B={check-gate.py, roadmap.md}；C={check-debt.py, ENV-SENSITIVE-TESTS.md, protocol-tests.yml}；D={dispatch-prompt.md, agate-frontmatter-check.py}——四组两两无交集，与 P2-design.md §0「H3 更新结论」（"RM-AG0042/0043 生产代码文件零重叠……比字面预判的'错开分支'更彻底"）及 §8「批次设计说明」（"D 与 A/B/C 均无文件重叠"）一致；`P4-progress-batchA.md` 末尾 `git status` 独立确认无越界改动。

**结论**：4 批 vs 5 批的差异是有记录、有理由的**编排层面执行时机决策**（RM-AG0032 从批次 E 提前并入批次 B），不改变 BDD-7 的 Given/When/Then 语义，`P4-implementation.md`「[SCOPE+] 声明」节已明确排除其构成范围外改动。判定为一致，非偏差，不标记 DEVIATION。

## 4. 未决项清零（独立复核）

- `P1-requirements.md` 全文检索：无任何行首 `[NEED_CONFIRM]` 标记，§7 明确 `[NO_NEED_CONFIRM]`（仅存在 5 条 `[SUGGEST: D1~D5]`，为倾向性建议留痕，非未决确认项）。
- `P6-acceptance.md` 全文检索：无任何 `[BLOCKER]` / `[DEVIATION-CRITICAL]` 标记，frontmatter `pass: 13, fail: 0`，正文 13 条全部为 `PASS` 前缀，无 `FAIL`/`BLOCKER`/`DEVIATION` 字样。
- 独立复核结论：两份文件均确认未决项清零，与 dispatch-context 初步核实结论一致。

## 5. CODE-MAP 核对

**结论：`[CODE_MAP_EXEMPT: agate/tests/ 目录不在 CODE-MAP.md 追踪的模块范围内]`**

- 已读 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`「模块」节全文，实际列出 6 条模块目录：`phase-cards`（`agate/phase-cards/`）、`execution-roles`（`agate/assets/execution-roles/`）、`review-roles`（`agate/assets/review-roles/`）、`scripts`（`agate/scripts/`）、`templates`（`agate/assets/templates/`）、`rules`（`agate/rules/`）。本任务新增的 `agate/tests/ENV-SENSITIVE-TESTS.md` 与 `agate/tests/unit/test_env_sensitive_tests_registry.py`（均在 `agate/tests/` 目录下）均不落在上述任一模块目录范围内，确认不属于 CODE-MAP.md 追踪范围。dispatch-context 该判断核实无误。
- 附带发现（`[WARNING]`，次要，不影响本结论）：`CODE-MAP.md` 开篇正文写"agate 协议本体划分为**五大模块**"，但「模块」节实际列举了 **6 条**（含 `rules`，TAG0021 新增结构化层），数字用词与实际列举条目数不一致——推测是 `rules` 模块后补时未同步更新"五大"措辞为"六大"，与本任务改动面无关，仅作观察记录，不阻断。
- `[WARNING]` `P4-implementation.md`「新增文件核对表」原文表述："（本仓库未采用骨架/CODE-MAP机制，本节按 P4 卡片说明省略。）"——**该表述不准确**。`CODE-MAP.md` 确实存在（`{AGATE_WORKSPACE}/agents/CODE-MAP.md`）且在实际使用中：`phase-cards/P7-consistency.md` 明确要求 P7 consistency-reviewer 对照该文件做 CODE-MAP 核对，`CODE-MAP.md` 自身「层」节也描述了 scripts 消费 phase-cards/templates 声明字段的机制说明。**不阻断的理由**：本节的实质结论——"本任务新增文件（`ENV-SENSITIVE-TESTS.md`/`test_env_sensitive_tests_registry.py`）不需要新增 CODE-MAP 条目"——依然成立，只是原因表述错了：不是"CODE-MAP 机制未被本仓库采用"，而是"这些新增文件恰好落在 `agate/tests/` 目录、不在 CODE-MAP.md 六大模块追踪范围内"（见上一条 `[CODE_MAP_EXEMPT:]` 判定）。结论正确、理由表述不精确，属文档措辞瑕疵，不影响 gate 判定，标 WARNING 供后续任务参考修正措辞，本轮不要求回改已 commit 的 P4-implementation.md。

## 6. 总体结论

- BLOCKER=0（无阻断项）
- DEVIATION-CRITICAL=0
- DESIGN_GAP 配对：机械层面 design_gap_count=0，无需配对；附 1 条 WARNING 级观察（§1，过程内歧义已同阶段闭环，判定不需补记）
- SCOPE+ 闭环：确认成立（§2）
- 跨文件一致性：BDD 编号内容级核对通过（§3.1）、packages 声明存在合理（§3.2，与 P8 一致性核对留待 P8）、4 批文件清单与 P2 设计吻合（§3.3，含 1 处已记录理由的编排时机偏差，判定非 SCOPE+/非 DEVIATION）
- 未决项清零：独立复核通过（§4）
- CODE-MAP 核对：`[CODE_MAP_EXEMPT: agate/tests/ 目录不在 CODE-MAP.md 追踪的模块范围内]`（§5），附 2 条 WARNING 级观察（CODE-MAP.md 自身"五大模块"措辞与实际 6 条列举不一致；P4-implementation.md"未采用骨架/CODE-MAP机制"表述不准确）

**P7 一致性检查结论：通过，无 BLOCKER，可推进 P8。**

[PROD_NOT_TOUCHED]
