---
task_id: TAG0027
mechanism_issues:
- "exit 2 双义语义无权威源核对：P2 设计/BDD/P3 测试把 check-gate exit 2 当'需自判暂停'，实为多数 phase 正常通过码——直至 P4 review 实证才发现，返工 P1-P4 四层"
- "P3 TDD 测试契约复制了设计对 exit 2 的错误前提，红灯未暴露协议级语义冲突（测试契约与真实语义脱节盲区）"
- "B3a/B1 文档清理边界漏网：CHECK 14/15 上线首跑 3 ERROR（dispatch.yaml law-1 / loop 前提 / dispatch-protocol 字段语境），跨批独占文件清单不覆盖全部命中面"
execution_issues:
- "P4 多批 implementer 单 agent 大任务上下文耗尽（B3a 两次卡住），改按文件拆分小 agent 后解决"
- "P8 bump 新增 UPGRADING 章节漏挂实现注记，自引入 CHECK 14 ERROR（本任务护栏 1 即时捕获）"
- "P3 测试注释含 /tmp 字面量触发 check-platform-assumptions R4（3 文件）"
feedback_ready: true
---

# TAG0027 复盘 — 编排语义统一落地（RM-AG0054）

## 一、事实基线

- 任务跨度：2026-09-02 立项 → 2026-09-03 P8（跨 2 天，集中执行）
- P0-P8 全流程：P1（25→26 BDD）/ P2（候选 A + 8 决策面 + exit2fix 修正轮）/ P3（44 用例）/
  P4（4 批 + exit2fix，2 轮 review rejected 后 approved）/ P5（7/7 gate 命令）/ P6（26/26 PASS）/
  P6.5（judge 26/26）/ P7（BLOCKER=0）/ P8（v0.66.0）
- subagent 派发：~30 次；其中 3 次上下文耗尽/卡住中断重派（B3a×2、B3b 初始轮）
- gate/review 失败：P2 review rejected 1 次（6 问题）+ P4 review rejected 1 次（2 CRITICAL +
  2 DEVIATION）+ needs-revision 1 次（REV-1）
- 涉及文件：92 files +14443（12 commit）
- 测试：全量 1381 passed + 2 skipped（P5 基线 → P8 后一致）
- **关键事件：P4 review 实证发现 check-gate exit 2 双义语义错误前提 → P1/P2/P3/P4 四层返工**
  （用户批准"回 P2 修正再重做"）

## 二、做得好的 + 可复用模式

- **P4 review 角色实测 gate exit 语义**（非 mock 构造任务实测 check-gate return）→ 发现设计层
  错误前提 → 去向：① 回馈 agate——review 角色应把"消费方实现 vs gate 真实语义核对"列为 Pass 1
  必查项（本任务 P4 review 做到了，但机制未固化）
- **exit2fix 修复先补测试后改实现**（健康任务 exit:2 直推 + judge Fix C 反向场景先红后绿）→
  去向：① 回馈 agate——语义修正类修复必须先补"真实场景测试"而非只改实现
- **多批并行 + 文件拆分**（B1/B2 并行、B3a 按 7 文件拆 7 个小 agent 分批）→ 去向：① 回馈
  agate——单 agent 大任务（>5 文件/大文档清理）易上下文耗尽，拆小粒度派发是有效缓解
- **P1 [BASELINE_CHANGE] 授权机制**（R1-R8 逐条标注 + 主 Agent 显式批准 + scope_resolved）→
  去向：① 回馈 agate——基线保护在语义修正场景下运作良好，值得保持
- **review 产出 Fix 方向 A/B/C 选项化**（P4 review 对每个 CRITICAL 给多选项而非单一路径）→
  去向：② 项目资产沉淀——评审给选项让主 Agent/architect 决策，比强制单方案高效

## 三、发现的问题

- 问题：P2 设计/BDD/P3 测试对 check-gate exit 2 语义的错误前提（当"需自判暂停"，实为多数
  phase 正常通过码）→ P4 review 实证才发现，四层返工
  归因层面: 机制缺口
  说明：exit 2 双义（P0-P3/P5/P8 正常通过 = exit 2 vs 真暂停）在 check-gate.py 头注释有
  "exit 2 = 需主 Agent 自判"，但其信号语义（通过 + 主 Agent 判下一步）与暂停语义（等解决）
  未区分——协议无"gate exit code 语义权威源"（如 phases.yaml gate_pass_exit 类字段）供
  消费方设计前核对。修复 = 本任务引入 gate_pass_exit 逐 phase 声明。教训：**消费方（CLI/
  BDD/测试）设计前必须先核对被消费脚本的真实返回语义，不能只读头注释的表面措辞**。

- 问题：P3 TDD 测试契约复制了设计的错误 exit 2 前提，红灯未暴露语义冲突（测试用 mock 造
  exit 0/1/2 场景，与真实 check-gate 语义脱节）
  归因层面: 机制缺口
  说明：P3 测试夹具构造"假 gate exit"（mock/前置产物），未用真实 check-gate 实测——若夹具
  用真实 gate 判定（如 B1 夹具修复那样补 P5 baseline + fail-list），CRITICAL-1/2 会在 P3
  红在测试设计期而非 P4 review 期暴露。教训：**测试 gate 消费方时夹具应尽量走真实 gate
  语义**（B1 修复后的 3 例夹具就是正确方向）。

- 问题：B3a/B1 跨批独占文件清单不覆盖全部平台名命中面（CHECK 14/15 上线首跑 3 ERROR：
  dispatch.yaml law-1 属 B3b 数据面但 B3a 清的是 md、loop-orchestration 归 B1 但其 OpenCode
  前提行 B1 没清、dispatch-protocol 字段语境 B3a 漏）
  归因层面: 机制缺口
  说明：文档清理批按"文件归属"划分边界，但平台名命中是"内容面"——同文件可能含多个清理点
  且跨批。教训：**清理类任务的批边界应按命中面而非文件归属划分，且上线新检查前必须先全量
  扫描确认零存量命中**（B3b 补漏才做这步，应在 B3a 完成时做）。

- 问题：P4 三个实现批 subagent 上下文耗尽/卡住（B3a 两次、B3b 初始轮），浪费多轮
  归因层面: 执行错误
  说明：B3a 派单个 agent 处理 7 文件文档清理（上下文重），卡在开工后。implementer.md 有
  分阶段落盘要求但单 agent 大任务仍易耗尽。改按文件拆 7 个小 agent 并行后解决。教训：
  **大任务（多文件/大文档）派发前先评估单 agent 上下文体量，超限拆小**。

- 问题：P8 bump 新增 UPGRADING v0.66.0 章节漏挂 `> 实现注记：`（含平台名词表）→ 自引入
  CHECK 14 ERROR，3 个一致性测试红
  归因层面: 执行错误
  说明：本任务自己落地的护栏 1（CHECK 14）即时捕获——UPGRADING 章节平台名词表须挂注记。
  修复 = 补注记。教训：**新增协议 md 段落若含平台名须同步挂注记**（本任务 UPGRADING 章节
  2 正是讲这个规则，自己却漏了——规则生效的即时验证）。

- 问题：P3 测试注释含 "/tmp 字面量" 字样触发 check-platform-assumptions R4（3 文件）
  归因层面: 执行错误
  说明：注释写"无 /tmp 字面量"自证平台无关，但注释本身含 /tmp 触发扫描。修复 = 措辞改为
  "临时目录字面量"。教训：**注释自证时避免出现被扫描的关键词本身**。

## 四、改进措施

- **gate_pass_exit 字段已落地**（本任务 phases.yaml + schema + agate-next pass_set 判定）——
  exit code 语义权威源，后续消费方设计核对用（落点：phases.yaml / P2-design §3.1）。
- **check-gate.py 头注释补 exit 2 语义说明**（"多数 phase 正常通过码，pass 判定以
  gate_pass_exit 为准"）——防止后续任务重蹈错误前提（落点：check-gate.py 头注释）。
- **P3 测试 gate 消费方夹具走真实 gate 语义**——review-mapping/test-designer 文档补充建议
  （落点：dispatch-protocol / test-designer 角色，待后续任务固化）。
- **清理/新检查任务先全量扫描确认零存量**（落点：B3 补漏教训——新 CHECK 上线前扫描面全量
  核对，可由 CI 先行验证）。
- **UPGRADING/新 md 段落含平台名须挂注记**——CHECK 14 已机械拦截（本任务自证生效）。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（P4 review 2 轮 rejected）| ✅ | — | — |
| PAUSED | 否（无 retry 超限/跨阶回退）| — | — | — |
| PROD_TOUCHED | 否 | ✅（全任务 [PROD_NOT_TOUCHED]）| — | — |
| SCOPE+ | 是（B3b 3 ERROR 补清）| ✅（P4-implementation + P1 scope_resolved）| — | — |
| SCOPE_RESOLVED | 是 | ✅ | — | — |
| DESIGN_GAP | 是（B1 夹具 + /tmp 注释）| ✅（P4-implementation 2 条）| — | — |
| DESIGN_GAP_REVIEWED | 是 | ✅（P7 2/2 配对）| — | — |
| NEED_CONFIRM | 否 | — | — | — |
| CAPABILITY_GAP | 否 | — | — | — |
| gate 验证（每阶段）| 是 | ✅ | — | — |
| 阶段产出文件（每阶段）| 是 | ✅ | — | — |
| .state.yaml phase 同步 | 是 | ✅ | — | — |
| 裁剪条件 + override | 否（全量 P1-P8）| — | — | — |
| capability_requirements | 否（[]）| — | — | — |
| 分阶段落盘（防 subagent 空返回）| 是 | ✅（但 B3a 单 agent 仍耗尽）| 3 次中断重派 | 执行错误（大任务未拆小）|
| phase-产出一致性 | 是 | ✅ | — | — |
| P6 evidence（含截图 + 引用 + vision YAML）| 是 | ✅（9 证据文件）| — | — |
| P2 候选方案 + 权衡（≥2）| 是 | ✅（候选 A/B）| — | — |
| P8 internal_only_reason | 否（走完整 P8）| — | — | — |
| dispatch-context.md | 是 | ✅ | — | — |
| pre-commit hook（gate / 状态转移 / 裁剪）| 是 | ✅（多次拦截：phase 不符/hash mismatch/SCOPE 标记）| — | — |
| CI backstop | 是 | ✅（ruff job 捕获 F401/C416/RUF005）| — | — |
| **技术债登记** | 否（无新增债）| — | 无 | DEBT0023 无涉；P8 debt_check=reviewed | |

## agate 反馈

1. **exit code 语义权威源缺失**：gate 脚本（check-gate exit 0/1/2）的真实语义（多数 phase
   正常通过码 = exit 2）与头注释表面措辞（"exit 2 = 需主 Agent 自判"）易误导消费方设计。
   建议：协议侧为每阶段声明"通过出口码"（如 gate_pass_exit），消费方（CLI/BDD/测试）设计
   前核对，而非凭注释推断——本任务 gate_pass_exit 字段是首个实例。
2. **P3 测试 gate 消费方的夹具应走真实 gate 语义**：用 mock 假 exit 码会让测试契约复制设计的
   错误前提、红灯不暴露语义冲突。建议测试设计文档强调：夹具构造真实前置产物（P5
   baseline/fail-list 等）让真实 check-gate 产 exit，而非 stub。
3. **清理/新检查上线前先全量扫描**：新增 CHECK 前须确认存量零命中（本任务 CHECK 14/15 首跑
   3 ERROR 是 B3a 批边界漏网）。建议：新检查上线先跑一次全量扫描作为前置 gate。
4. **单 agent 大任务上下文管理**：>5 文件/大文档清理类任务单 agent 易耗尽，建议派发前按
   文件数/体量评估拆小（本任务 B3a 拆 7 个小 agent 后稳定）。
