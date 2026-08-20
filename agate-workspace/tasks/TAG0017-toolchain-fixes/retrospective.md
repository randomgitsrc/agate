---
task_id: TAG0017
mechanism_issues:
  - "check-tdd-red.py 无 formatter 时的原始输出正则兜底（Traceback|SyntaxError|ImportError|ModuleNotFoundError）会被测试自身的字符串字面量测试夹具污染——当含该字面量的测试本身处于红灯时，pytest 默认详细模式回显其源码到外层 raw_output，导致整个 P3 gate 被误判为 A 类假红灯"
  - "check-debt.py 的 source 字段枚举（retreat/review/retrospective）未覆盖 cross_project_feedback，但 DEBT0014/DEBT0015 已用该值登记且从未被任何 P0-P8 gate 捕获（check-debt.py 未接入 gate 流水线），属静默 schema 违规"
execution_issues:
  - "5 批并行 P4 implementer 派发时遗漏要求任一批产出 P4-implementation.md（阶段规定的汇总文档），事后需额外派发第 6 个轻量 subagent 补齐"
feedback_ready: true
---

# TAG0017 复盘 — 协议工具链修复批（DEBT0010/11/12/14/15）

## 一、事实基线

- P0 在本会话开始前已完成（交接单 HANDOFF-TAG0017.md），本会话执行 P1→READY。
- 阶段产出 commit 共 8 个（P1~P7 各一 + READY 一），另加 self-gate 修复未单独计入 phase commit。
- retry 记录：P1 第 1 轮（analyst 同类扫描 3.3/3.4 节计数错误：8→7、12→13）、P2 第 1 轮（plan-eng-review 打回 BLOCKER-1：`agate/SELF-GATE.md` 路径前缀自相矛盾）、P3 第 1 轮（主 Agent 亲自跑全量 gate_commands.P3 后发现 3 处并行批次副作用，非设计缺陷）、P4 第 1 轮（review 打回 1 CRITICAL：`--strict` 未同步为 `--strict-errors-only`，另有 1 轮 self-gate MISALIGNED：`agate/scripts/README.md` 未同步新增 flag 文档）。P5/P6/P7 均首轮通过。
- P4 阶段 review subagent 第一次派发因平台用量限额中途中断（无产出），未计入 retries[P4]（按 dispatch-protocol.md「外部中断恢复」处理），原样重发后正常完成。
- 12 条 BDD、5 批并行 implementer + test-designer（P3/P4 各 5 批）均未出现文件级冲突。
- 版本 v0.54.0 → v0.55.0（minor）。5 条登记 DEBT 中 3 条（DEBT0010/11/12）本次全部 closure_criteria 满足并标记 closed；DEBT0014 保持 open（Windows 真实环境验证依赖 CI matrix，本会话未跑）；DEBT0015 保持 open（closure_criteria 3 要求未来 UI 任务实证，本任务无 UI 场景无法自证）。

## 二、做得好的 + 可复用模式

- **同批共享落点文件的合并策略成立**：P1「按文件→改动归并 BDD」+ P2 dispatch_plan 把 DEBT0010/DEBT0015 的文档半和 DEBT0012 的文档半都并入 `fg1-doc-boundary` 批次（因三者都要改 `phase-cards/P2-design.md` 同一节），5 批 P3 test-designer + 5 批 P4 implementer 并行执行后，`git status`/`git diff --stat` 逐次核实均无同一文件被两批各改一次的情况。去向：**回馈 agate**——这条"批次边界应对齐影响面梳理的文件分组"规则已写在 P2 卡片，本次是一次成功的实测验证，无需改协议，但值得作为该规则有效性的正面证据留痕。
- **自我指涉审查确实抓住了协议自身的滞后**：P4 review 发现 `phase-cards/P2-design.md` 新增的"正确做法"示例（本任务自己写的）仍推荐 `--strict` 而非本任务新增的 `--strict-errors-only`——即修复本身的示范文档没跟上修复本身的代码。这正是 agate review 机制设计要捕获的"协议改自己却留下新陷阱"场景，此次在真实场景下验证有效。去向：**回馈 agate**——不需要改动协议，但值得记录"self-gate + P4 review 对协议自改任务的双重校验在本任务中各自单独抓到了一处真实缺陷（self-gate 抓 README.md，P4 review 抓 P2 卡片示例）"，证明两道审查机制不是冗余而是覆盖了不同的偏差面。

## 三、发现的问题

- 问题：`check-tdd-red.py` 无 formatter 兜底时的原始输出正则（`Traceback|SyntaxError|ImportError|ModuleNotFoundError`）对整个 gate_commands.P3 输出做全文扫描，未区分"真实错误"与"测试夹具里的字符串字面量恰好含这些词、且该测试自身处于红灯导致 pytest 默认详细模式回显源码"两种情况。本次 fg1-parser-scripts 批次新增的 `test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class` 恰好命中此陷阱，导致 check-tdd-red.py 把真红灯误判为 A 类假红灯，主 Agent 需额外一轮排查+修复（重写字符串字面量为拼接形式规避，未修正判定逻辑本身）。
  归因层面: 机制缺口
  说明：这不是本任务测试写得不规范，是 `check-tdd-red.py` 的兜底分类逻辑对"测试源码被 pytest 详细模式回显"这一必然场景没有防护，任何未来测试只要在断言消息/模拟数据里含这几个关键词、且该测试当前处于红灯，都会复现同一问题。当前的规避方式（改写字面量）是绕过而非修复，问题仍潜伏在 `check-tdd-red.py:110` 附近。
- 问题：`check-debt.py` 的 `source` 字段枚举只接受 `retreat`/`review`/`retrospective` 三值，但 DEBT0014/DEBT0015（本任务范围内两条，registered 于 P0 阶段之前）用的是 `cross_project_feedback`，属枚举外非法值，`check-debt.py` 会报错。该问题在本会话开始前已存在（P0-brief 交接时已是这个状态），且因为 `check-debt.py` 未接入任何 P0-P8 phase gate（本会话核实：全仓 grep 未发现该脚本被 check-gate.py 或任何阶段卡片的 gate_commands 引用），此 schema 违规从未被任何自动化流程捕获，处于静默状态。
  归因层面: 机制缺口
  说明：`source` 枚举没有随着"跨项目反馈"这一登记来源类型的实际使用而更新，且 `check-debt.py` 缺少接入点导致新登记条目的 schema 合规性完全靠人工肉眼核对。本次任务范围锁定在 DEBT0010/11/12/14/15 的问题修复本身，未将此 schema/接入缺口纳入范围（避免范围蔓延），原样保留、仅记录发现。
- 问题：P4 阶段按 P2 dispatch_plan 拆成 5 批并行 implementer 时，5 份 dispatch-context 均只要求各批产出代码/文档改动，没有一份要求产出阶段规定的汇总文档 `P4-implementation.md`（`implementation_dir` 声明 + 改动清单），直到 gate 检查前才发现遗漏，临时加派第 6 个轻量 subagent 专门补这份文档。
  归因层面: 执行错误
  说明：`phase-cards/P4-implementation.md` 已明确"产出规格"要求该文件存在，协议本身没有缺失定义；这是主 Agent 在设计 5 批拆分时漏想了"谁来交付阶段级汇总产出"这一环，属于派发规划疏漏，不是协议未覆盖。

## 四、改进措施

- 建议登记新 DEBT：`check-tdd-red.py`（约 L110）无 formatter 兜底分支的原始输出正则扫描，应改为只扫描"当前测试运行的执行摘要区域"而非全文，或在扫描前排除被 pytest 详细模式回显的失败测试源码段——具体方案留给后续修复任务设计，本复盘只标记需要登记，不在此提交注册。
- 建议登记新 DEBT 或 roadmap backlog 条目：`check-debt.py` 的 `source` 枚举补充 `cross_project_feedback`（或明确该来源应归并为 `review`/`retrospective` 之一，统一登记口径），并评估是否需要把 `check-debt.py` FILE 模式接入某个阶段（如 P0/P8）的 gate_commands，避免登记时 schema 违规长期不被发现。
- 落到具体协议位置的建议（非本任务范围内改动，仅记录）：`dispatch-protocol.md`「派发编排机制」的多批并行拆分指引，可补一句"多批并行的阶段级汇总产出物（如 P4-implementation.md/P8-release.md）需在拆批设计时明确由哪一批或独立一批产出，不能默认某批会顺带完成"，减少未来同类遗漏。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | | P1/P2/P3/P4 共 4 轮 retry 均正确记录到 `.state.yaml` |
| PAUSED | 否 | — | | 全程未触发回退/超限 |
| PROD_TOUCHED | 否 | — | | 全程 `[PROD_NOT_TOUCHED]`，纯脚本/文档改动 |
| SCOPE+ | 否 | — | | 全程未发现范围外隐含需求 |
| SCOPE_RESOLVED | 否 | — | | 无 SCOPE+ 触发，无需闭环 |
| DESIGN_GAP | 否 | — | | 5 批 P4 实现均报告"无 DESIGN_GAP" |
| DESIGN_GAP_REVIEWED | 否 | — | | 无 DESIGN_GAP 触发 |
| NEED_CONFIRM | 否 | — | | P1 全程 `[NO_NEED_CONFIRM]` |
| CAPABILITY_GAP | 否 | — | | 无特殊能力需求（`capability_requirements: []`） |
| gate 验证（每阶段） | 是 | ✅ | | P1-P8/READY 每阶段均亲自跑 gate 脚本判定 |
| 阶段产出文件（每阶段） | 是 | ✅ | | 无裁剪，全部阶段产出齐全 |
| .state.yaml phase 同步 | 是 | ✅ | | 每次 commit 前同步更新 |
| 裁剪条件 + override | 否 | — | | 全程无裁剪（`phases:` 声明完整 P1-P8） |
| capability_requirements | 是 | ✅ | | P1 声明 `[]` 并附理由 |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | | 全程无空返回（除 1 次外部用量限额中断，非空返回） |
| phase-产出一致性 | 是 | ✅ | | pre-commit hook WARNING 在预期节点触发（如 P2 修复涉及跨阶段改动时），未误伤 |
| P6 evidence（含截图 + 引用 + vision YAML） | 否 | — | | 非 UI 任务，无截图/vision 要求，改用命令输出日志作证据，符合角色文件条件化要求 |
| P2 候选方案 + 权衡（≥2） | 是 | ✅ | | 4 功能分组各 2 候选，8 个候选方案全部落地 |
| P8 internal_only_reason | 否 | — | | 未裁剪 P8 |
| dispatch-context.md | 是 | ✅ | | 每次派发前均落盘，含增量修复轮 |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅ | | 每次 commit 均触发且按预期判定 |
| CI backstop | 是 | — | | 本会话未推送/未观察 CI 结果，留待 PR 阶段确认 |
| **技术债登记** | 是 | ✅ | | DEBT0010/11/12/14/15（本任务范围内）+ 本复盘新发现 2 项（check-tdd-red.py 假红灯陷阱、check-debt.py schema 枚举缺口）建议登记但未在本复盘内注册，留待后续任务处理 |

## agate 反馈

- **check-tdd-red.py 无 formatter 兜底的原始输出正则误判**：`agate/scripts/check-tdd-red.py` 约 L110 的 `re.search(r"Traceback|SyntaxError|ImportError|ModuleNotFoundError", raw_output)` 对整个 gate_commands.P3 命令的原始输出做全文扫描，未排除"当前处于红灯的测试自身源码被 pytest 默认详细模式回显、且源码里恰好含这些字符串作为测试夹具数据（非真实错误）"这一场景。TAG0017 的 `test_bdd_2_timeout_seconds_declared_real_a_class_failure_stays_a_class` 实测复现：该测试构造了一个含 `"Traceback (most recent call last):\nSyntaxError: invalid syntax"` 字面量的模拟 pytest 输出用于测试 check-tdd-red.py 自身的分类逻辑，这个字面量在该测试自身红灯时被 pytest 回显到外层 `python3 -m pytest agate/tests/` 的整体输出中，导致整条 gate_commands.P3 被误判为 A 类假红灯。建议后续任务修复：原始输出扫描应限定在"当前失败摘要"区域，或改用更精确的错误类型标记而非全文关键词匹配。
- **check-debt.py 的 source 枚举未覆盖已在用的 cross_project_feedback 值，且未接入任何 gate**：`agate/scripts/check-debt.py` 的 `source` 字段合法值只有 `retreat`/`review`/`retrospective`，但 `agate-workspace/debt/tech-debt.md` 中 DEBT0014/DEBT0015（TQC0001 跨项目反馈来源）已用 `source: cross_project_feedback` 登记，属枚举外非法值。此问题预先存在于 TAG0017 P0 立项时的债务登记（非本会话引入），且因为 `check-debt.py` 未被任何 P0-P8 phase 卡片的 `gate_commands` 引用（本会话全仓 grep 核实），这类 schema 违规长期不会被任何自动化检查捕获。建议：① `check-debt.py` 的 `source` 枚举补充 `cross_project_feedback`（或明确要求跨项目反馈类条目改用 `review` 登记，统一口径后修正现有两条）；② 评估是否需要把 `check-debt.py` FILE 模式接入某个阶段的 gate，或至少加入 CI backstop，让登记时的 schema 错误能被及时发现而非无限期静默存在。
