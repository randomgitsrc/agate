---
task_id: TAG0025
mechanism_issues:
  - "BDD-10 豁免清单的授权链缺口：P3/P4 阶段在测试代码里实现了一条豁免逻辑（`_is_exempt()` 的
    文件自我豁免），P4/P5/P6 一直沿用这条逻辑作为'已知盲区'判定依据，但从未走回 P1-requirements.md
    正式补授权——直到 P6.5 judge fresh-context 独立复核才发现这个链路断裂"
  - "永久回归测试的瞬时状态耦合反模式：P3 test-designer 为 P1 的 BDD-3（CHANGELOG Unreleased 段
    新建）与 BDD-9（批次原子性）设计的测试断言，用的是'当前状态'（是否存在 [Unreleased] 段/
    文件最近一次改动是哪个 commit）而不是'不可变历史事实'（该版本段是否曾经存在过/某历史 commit
    是否覆盖这些文件），导致这两条测试在 P8 发布动作发生后必然假性变红——这不是回归，是测试
    编写时的判据选择错误，但协议对'如何设计 TDD 验收测试才能安全过渡为永久回归测试'没有给出
    显式指引"
execution_issues: []
feedback_ready: true
---

# TAG0025 复盘 — Agateon 品牌改名执行 Phase 0-1

## 一、事实基线

- **任务周期**：单会话内完成 P0-P8 全流程（2026-08-26），15 个 `wf(TAG0025-*)` commit
- **P1**：16 条 BDD，requirements-review 一次通过（无重试）
- **P2**：2 候选方案（A/B），plan-eng-review 一次通过（无重试），P2 阶段发现并修复 P1 BDD-10
  第一处豁免授权缺口（[SCOPE+] → [BASELINE_CHANGE]）
- **P3**：11 个 pytest 测试函数（A 类 10 条对应 BDD-1~10，B 类 6 条登记为程序化验证用例）
- **P4**：2 个常规批次（文件层改动 + remote 迁移）+ 1 次重试（`retries.P4[0]`，ruff RUF005
  违规，failure_mode: quality，1 行语法修复）；GitHub 仓库改名不可逆操作由主 Agent 亲自执行
  （用户当次会话放行确认，未下放 subagent）
- **P5**：首轮 24 个 gate_commands.P5_* key，1 个真失败（ruff）+ 1 个已知盲区（BDD-10 shell 版
  测试文件自指）；修复后全量重跑 0 failed；P8 阶段再全量重跑 1 次（发现并修复 BDD-9 的同类
  瞬时状态耦合问题）
- **P6**：2 轮（第 1 轮 15/16 PASS + 1 FAIL 由 judge 发现，第 2 轮 16/16 PASS）
- **P6.5 judge**：2 轮（第 1 轮 `needs-revision`，发现 BDD-10 豁免授权缺口；第 2 轮
  `passed`，16/16），`judge.rounds: 2`，未超预算（≤2 轮上限内收敛）
- **P7**：一致性检查一次通过，`blocker_count: 0`
- **P8**：版本 v0.63.0 → v0.64.0（minor bump，用户确认），git tag 创建后又移动一次（发布验证
  期间发现并修复 BDD-9 测试脆弱性）
- **回归底线**：迁移前 1293 用例，本任务净增 11 个测试函数 → 1304，全绿

## 二、做得好的 + 可复用模式

- **不可逆外部操作的执行权归属设计（候选 B）**：P2 阶段候选方案权衡时，明确识别"派发平台是否
  支持暂停/恢复运行中 subagent"这一能力空白是真实风险（而非稻草人陪衬候选），选择把 GitHub
  仓库改名操作的执行责任收归主 Agent 本人、与用户确认发生在同一会话轮次——去向：①**回馈
  agate**，这个决策模式（不可逆操作执行主体归属 = 与放行确认发生在同一 Agent/同一轮次，不依赖
  未经验证的平台能力）值得沉淀进 dispatch-protocol.md 或 role-system.md 作为通用指引，供未来
  任务遇到类似"不可逆外部操作该由谁执行"的决策时参考。
- **P6.5 judge 机制的真实价值验证**：本任务是 judge 机制（RM-AG0032）投入使用以来，第一次
  实证"judge 独立复核确实抓到了主链路（P1→P2→P4→P5→P6 全部经过校验的）遗漏的真实缺口"——
  BDD-10 的豁免授权链断裂在 P2/P4/P5/P6 四个阶段都被"合理化"为已知盲区处理，唯独 fresh-context
  的 judge 因为不读 P4-P6 任何 dispatch-context/自述文件、只信 P1 原文授权范围，发现了这个
  授权文本与实际执行口径的落差——去向：①**回馈 agate**，这是 TAG0018（LLM 评审≈0 净收益）的
  反例实证，建议记入 judge 机制的价值评估证据库（对照 TAG0018 的成本账，为"judge 机制值得
  保留"提供一个真实数据点）。

## 三、发现的问题

- 问题：BDD-10 的豁免清单存在"测试代码里先实现豁免逻辑、P1 授权文本后补"的时间倒挂——
  `_is_exempt()` 的文件自我豁免逻辑在 P3 就写好了，P4/P5/P6 三个阶段的 dispatch-context 都
  引用它作为"已知盲区"判定依据，但没有一个阶段触发"这需要走 P1 BASELINE_CHANGE 流程"这个
  检查，直到 P6.5 judge fresh-context 独立复核才发现。
  归因层面: 机制缺口
  说明：agate 现有的 `[BASELINE_CHANGE]` 机制要求"变更 P1 需主 Agent 显式批准"，但没有一个
  机制在"P3/P4 阶段的实现细节隐含了对 P1 验收标准的事实性扩展"时主动触发提醒——本例中
  test-designer 在 P3 写豁免逻辑时，其实已经在"定义验收标准的一部分"（哪些文件豁免残留扫描），
  这本质上是需求层面的决策，但发生在测试实现阶段，没有被识别为"需要走 BASELINE_CHANGE"的
  时刻。P1 卡片"基线保护"节的措辞是"P4 发现 BDD 矛盾需标 DESIGN_GAP"，没有覆盖"P3 测试实现
  阶段隐式扩展了验收标准细节（而非产生矛盾）"这种情形。

- 问题：P3 test-designer 为"验证一次性 TDD 事实"（CHANGELOG 新建 Unreleased 段/7 处 URL 落在
  同一 commit）设计的测试，断言逻辑用了会被后续合法操作打破的"当前状态"/"最近一次改动"，而非
  "不可变历史事实"，导致这两条测试在 P8 发布动作后必然假性变红（先后在 P8 阶段被发现并修复
  两次：CHANGELOG 段转正后修 BDD-3，README badge bump 后修 BDD-9）。
  归因层面: 机制缺口
  说明：test-designer.md 角色定义里有"TDD：先写测试，测试先失败，再让实现使其通过"的通用
  指引，但没有区分"这条测试验证的是一次性交付事实（应该设计成对未来改动免疫的历史事实断言）"
  还是"这条测试验证的是需要长期保持的不变量（用当前状态判断是对的）"——本任务的 BDD-1/2/4~8/10
  是后者（品牌声明/URL 正确性应该永远成立），BDD-3/9 实际是前者（CHANGELOG 段新建/批次原子性
  是这次交付的历史事实，不是长期不变量），但两类测试用了相同的编写模式（断言当前/最近状态），
  没有协议层面的指引提示这个区分。

## 四、改进措施

- **落点 1**：`agate/assets/execution-roles/test-designer.md`「认知模式」节补一条区分指引——
  写永久回归测试（`agate/tests/regression/` 或等价目录）时，先问"这条 BDD 验证的是长期不变量
  还是一次性交付事实"：长期不变量（如"品牌声明应始终存在""URL 应始终正确"）可以断言当前状态；
  一次性交付事实（如"某个版本段的建立""某次批次提交的原子性"）必须断言不可变历史证据（如
  git 具体 commit SHA 的 diff-tree，而非"最近一次改动"；如版本号一旦转正后的具体历史值，而非
  "是否存在 Unreleased 包装"），否则该测试会在后续任何正常操作（如下一次发布）后假性变红。
- **落点 2**：`agate/phase-cards/P1-requirements.md`「P1 基线保护」节或
  `agate/dispatch-protocol.md` 补一条触发点——P3/P4 阶段若实现细节隐含了对 P1 验收标准范围的
  事实性扩展（如新增豁免条件、放宽/收紧某条 BDD 的判定边界），即使当下没有产生"矛盾"（不触发
  DESIGN_GAP 的典型定义），也应视为需要 `[BASELINE_CHANGE]` 授权的情形，不能只在下游阶段的
  dispatch-context 里口头引用而不回写 P1 正文。
- **落点 3**（低优先级，非本次任务范围，供未来评估）：`gate_commands` 在 P2 固化后不可改这条
  纪律，遇到"下游阶段新增文件导致固化命令产生盲区"（本任务出现 3 次：P1 BDD-10 第 5/6 类豁免、
  P8 的 BDD-3/BDD-9 shell 版本）时，目前的处理方式是"pytest 权威版本 + 文档记录盲区"，功能上
  没问题但每次都要重新论证一遍。是否需要在 P2 卡片补一条"gate_commands 固化后如发现盲区，
  标准处理路径是什么"的简要指引（而不是每个任务各自发明说法），由用户评估是否值得，不在本次
  任务内处理。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | — | P4 retries[0] 已记录（ruff 修复，failure_mode: quality） |
| PAUSED | 否 | — | — | 无 retry 超限/跨阶段回退/未获批不可逆操作 |
| PROD_TOUCHED | 否 | — | — | 全程 `[PROD_NOT_TOUCHED]`，未接触生产环境 |
| SCOPE+ | 是 | ✅ | — | P2「[SCOPE+] 发现」小节已记录并走 BASELINE_CHANGE 收敛 |
| SCOPE_RESOLVED | — | — | — | 本任务的 SCOPE+ 走的是 BASELINE_CHANGE 而非常规 SCOPE_RESOLVED 机制，P7 已核实此判定 |
| DESIGN_GAP | 否 | — | — | P4-implementation.md 三节均确认无 DESIGN_GAP，P7 已核实 |
| DESIGN_GAP_REVIEWED | — | — | — | 无 DESIGN_GAP，不适用 |
| NEED_CONFIRM | 否 | — | — | P1 [NO_NEED_CONFIRM]，全程无残留 |
| CAPABILITY_GAP | 否 | — | — | 无能力缺口，P1 capability_requirements 全部 available |
| gate 验证（每阶段） | 是 | ✅ | — | P0-P8 每阶段均预跑 gate 脚本 |
| 阶段产出文件（每阶段） | 是 | ✅ | — | P0-P8 全部产出齐全 |
| .state.yaml phase 同步 | 是 | ✅ | — | 每次 commit 均同步更新 |
| 裁剪条件 + override | 否 | — | — | 本任务 phases 全流程不裁剪（P1 §6 已论证） |
| capability_requirements | 是 | ✅ | — | P1 §8 已声明三态，均 available |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | — | 全部 subagent 均产出 progress.md |
| phase-产出一致性 | 是 | ✅ | — | 无 phase-产出不匹配的 commit |
| P6 evidence | 是 | ✅ | — | 16 个证据文件，均含实质命令输出 |
| P2 候选方案 + 权衡（≥2） | 是 | ✅ | — | 候选 A/B，权衡充分（P2-review 已核实非稻草人） |
| P8 internal_only_reason | 否 | — | — | 本任务对外可见（品牌+仓库改名），不适用 internal_only |
| dispatch-context.md | 是 | ✅ | — | 每次派发前均先写 dispatch-context |
| pre-commit hook（gate/状态转移/裁剪） | 是 | ✅ | — | 全程 hook 正常拦截/放行 |
| CI backstop | — | — | — | 本任务未 push，CI backstop 尚未触发（待 PR 阶段） |
| **技术债登记** | 否 | — | — | 本任务未产生需登记的新技术债（P8 debt_check: none，已核对 tech-debt.md） |
