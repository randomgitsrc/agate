---
review_date: 2026-09-01
reviewer: independent-design-review
change_summary: 编排语义统一设计（自动化在协议内，平台只做执行环境）独立评审——docs/design-notes/design-orchestration-semantics.md
files_changed: [docs/design-notes/design-orchestration-semantics.md]
---

# 编排语义统一设计（design-orchestration-semantics）评审

审查对象：`docs/design-notes/design-orchestration-semantics.md`（151 行，设计讨论，待立项候选 RM-AG0049）。
权威规则源：`agate/WORKFLOW.md`、`agate/orchestrator-template.md`、`agate/dispatch-protocol.md`、`agate/state-machine.md`、`agate/loop-orchestration.md`、`agate/platform-notes.md`、`agate/SETUP.md`、`agate/rules/phases.yaml`、`agate/rules/state-transitions.md`、`agate/scripts/check-gate.py`、`agate/scripts/check-state-transition.py`、`agate/scripts/agate-next-card.py`、`agate/scripts/agate-retreat-to.py`、`agate/scripts/agate_common.py`、`docs/design-notes/dsh-integration.md`、`docs/design-notes/design-independent-judge.md`、`docs/design-notes/README.md`。

## 结论汇总

| # | 问题 | 级别 |
|---|------|------|
| B1 | 4.1/5 节"dispatch-protocol 五模式"内容误述——实际五模式是单发/静态拆批/并行/先理解后拆/串行链，非"单发/并行批/流水线/独立复核/跨轮续跑"；作为统一锚点的核心依据失实 | **BLOCKER** |
| B2 | 第 5 节"已具备 60% 零件"资产清单不完整，且低估现状——状态机推进/回退的既有资产（state-machine.md / loop-orchestration.md / check-state-transition.py / agate-retreat-*.py / rules/ 结构化层）全部未列；Phase 1"定义状态转移表 schema"与既有 `rules/phases.yaml` 高度重叠，有重复造轮子风险 | **BLOCKER** |
| W1 | 第 3 节"流程层 100% 可程序化"过度简化——PAUSED / 跨阶段回退 / 裁剪跳变 / SCOPE+ 定向回补 / P6.5 judge 门槛均为既有状态机的非确定性成分，"确定性状态机"只覆盖主线推进与单步回退子集 | WARNING |
| W2 | 第 7 节"gate 失败 → 回当前 phase"与现有回退语义不符——实际是 P5/P6 gate 失败 → 回 P4（retry+1）、跨阶段回退 diff≥2 → 强制 PAUSED（check-state-transition.py 机械拦截）；回退路由已由脚本承接 | WARNING |
| W3 | 4.3 三条护栏可执行性不足且自相矛盾——护栏 2"平台名只出现在如何实现小节"与现有 `platform-notes.md`（整篇按平台组织）冲突，落地成本未评估；护栏 1"不发明以平台工具命名的概念"与 4.1 表自身用 workflow/ralph/goal 命名语义列相矛盾 | WARNING |
| W4 | gate exit code 的"确定性输入"声称忽略 exit 2 语义——check-gate.py 大量返回 exit 2（需主 Agent 自判，含动态 gate_commands），`{phase, gate_exit_code, 输入产物} → 下一 phase` 对 exit 2 无唯一后继 | WARNING |
| N1 | P6.5 是挂载于 P6→P7 转移的强门槛子阶段、非独立 phase 值（state-machine.md:74-78）——设计笔记未提，转移表 schema 若按"每 phase 一行"建模会与之冲突 | NIT |
| N2 | design-notes/README.md 未登记本笔记（索引格式约定，review-rm-ag0046 N1 同类问题） | NIT |
| N3 | 外部链接 issue #20849 真实存在（标题为 "Plugin-based agent orchestration layer"，比"平台层正在往同一方向收敛"更克制）——引用存在但推断略超前 | NIT |
| N4 | `agate-next-card.py` 实际是"输出当前阶段卡片全文"（M3 渲染化），不是"选下一张卡"——5 节用途描述可更精确 | NIT |

## 事实核验（文档声称 vs 仓库现状）

| 声称 | 核验结果 |
|------|---------|
| orchestrator 四项职责"读状态 → 派发 subagent → 跑 gate → 更新状态"（1.1）| ✅ 属实（WORKFLOW.md:15 "读状态、派发、验门槛、更新状态"；orchestrator-template.md:36-39 同构）|
| 三个关键设计：状态显式落盘 / 判定可执行化（BDD-9）/ 角色薄化（1.1）| ✅ 属实（state-machine.md:11-15；WORKFLOW.md:310 "exit code 才是门槛（哲学红线，BDD-9）"；role-system.md 方法 B + SETUP.md:13 "只需要注册 orchestrator 这一个 agent"）|
| 三平台能力差异：DSH 有 workflow/ralph/goal，另两个没有（1.2/4.1）| ✅ 属实（platform-notes.md:181-190 能力差异表；dsh-integration.md:24-28）|
| "统一锚点是 dispatch-protocol 五模式（单发/并行批/流水线/独立复核/跨轮续跑）"（4.1）| ❌ **不符**——dispatch-protocol.md:511-519 实际五模式 = 单发 / 静态拆批 / 并行 / 先理解后拆 / 串行链；"流水线/独立复核/跨轮续跑"在 dispatch-protocol 中不存在（后者疑似来自 dsh-integration.md 的 workflow/ralph/goal 工具映射，张冠李戴）|
| 资产清单：`agate-next-card.py` / `check-gate.py` / `.state.yaml` / `agate_common.py` / `dispatch-protocol.md`（5 节）| ⚠️ 五项均实存（glob 核验），但清单遗漏状态机侧既有资产，且 `agate-next-card.py` 功能描述不精确（见 N4）|
| "`agate-next-card.py` 选下一张阶段卡"（5 节）| ⚠️ 部分属实——实际是"按 PHASE 输出阶段卡片全文 + sha256 校验 + 从 rules/phases.yaml 渲染可判定节"（agate-next-card.py:2-24），不承担"选下一张"逻辑 |
| "`agate_common.py` 公共函数库（resolve_workspace 等）"（5 节）| ✅ 属实（agate_common.py:245 write_gate_result / 290 read_state_phase / 296 read_state_task_id / 551 resolve_workspace）|
| "check-gate.py gate 判定（exit code）已有"（5 节）| ✅ 属实，但 exit 0/1/2 语义未在笔记中展开（见 W4）；且 check-gate.py 已有第 3 参 OLD_PHASE 回退检测（check-gate.py:9-11, 1387-1396）|
| "P0-P8 是固定拓扑（一条主线 + 有限回退边），不需要图引擎"（2 节 B 否决理由）| ⚠️ 基本属实但需限定——主线 P0→…→READY 固定（state-machine.md:72-73），但存在裁剪跳变、SCOPE+ 定向回补、跨阶段回退、PAUSED 汇合等非主线边（见 W1）|
| "缺口：把读状态→查状态转移表→推进/回退→落盘串成确定性 CLI"（5 节）| ⚠️ 推进侧确实无 CLI（无 agate-next/advance），但**回退侧 CLI 已存在**（agate-retreat-to.py / agate-retreat-state.py / agate-archive-stale-outputs.py，rules/state-transitions.md:73-85），笔记未提 |
| 状态转移表"从自然语言卡片压缩为机器可读"（5 节）| ⚠️ 既有的 `rules/phases.yaml`（TAG0021 结构化层，phases.yaml:1-10）已承载 phase/exec_role/outputs/gates/retry_cap 机器可读数据面；笔记未引用，Phase 1 schema 与之重叠 |
| "OpenCode 社区提案（issue #20849）证明平台层正在往同一方向收敛"（4.4）| ⚠️ 链接真实存在（[anomalyco/opencode#20849](https://github.com/anomalyco/opencode/issues/20849)，标题 "Plugin-based agent orchestration layer — parallel execution without upstream changes"）；"正在收敛"是从单一 issue 推出的超前结论 |
| DSH 的 `workflow` 四钩子 agent/pipeline/parallel/phase（4.4）| ✅ 属实（dsh-integration.md:130 "agent/pipeline/parallel/phase + 1000 agent 上限"）|
| 4.1 语义-实现映射表（并行批→workflow / 独立复核→ralph / 跨轮续跑→goal）| ✅ 与 dsh-integration.md:24-28、platform-notes.md:188-189 一致 |

## B1（BLOCKER）：4.1/5 节"dispatch-protocol 五模式"内容误述

设计笔记 4.1 把统一锚点定义为"dispatch-protocol 五模式（单发 / 并行批 / 流水线 / 独立复核 / 跨轮续跑）"，5 节资产表又称 `dispatch-protocol.md`"五模式编排语义……已有，作为统一锚点"。

核验 `agate/dispatch-protocol.md` 511-519 行「2. 五模式编排」：

| 模式 | 实际名称 |
|------|---------|
| 模式 1 | 单发 |
| 模式 2 | 静态拆批 |
| 模式 3 | 并行 |
| 模式 4 | 先理解后拆 |
| 模式 5 | 串行链 |

笔记所列"并行批 / 流水线 / 独立复核 / 跨轮续跑"在 dispatch-protocol 中**不存在**——其中"流水线"疑似对应 DSH `workflow` 的 pipeline 钩子、"独立复核"对应 ralph/judge、"跨轮续跑"对应 goal 工具，全部来自 dsh-integration.md 的工具映射，而非协议侧派发模式。笔记把"平台工具映射"误写成了"协议五模式"。

推演：

```text
4.1 声称：统一锚点 = dispatch-protocol 五模式 = {单发, 并行批, 流水线, 独立复核, 跨轮续跑}
实际：    dispatch-protocol 五模式 = {单发, 静态拆批, 并行, 先理解后拆, 串行链}
差异：    "并行批"≈"并行/静态拆批"但改名；"流水线/独立复核/跨轮续跑"为笔记自造或工具名借用
→ 读者按锚点去读 dispatch-protocol 会找不到对应概念；平台差异表（4.1）挂在错误锚点上
→ 恰违反笔记自己 4.3 护栏 1"协议概念禁止平台特化"——把 workflow/ralph/goal 倒灌进协议层语义
```

可选修正：

1. 4.1 改引 dispatch-protocol 实际五模式（单发/静态拆批/并行/先理解后拆/串行链），平台映射列到"如何实现"小节；
2. 或明确"语义锚点"是笔记新定义的抽象（批/复核/续跑三类语义），并声明"不等同于 dispatch-protocol 五模式"，避免挂靠失实的权威源。

## B2（BLOCKER）：第 5 节资产清单不完整，Phase 1 与既有结构化层重叠

第 5 节"已具备 60% 零件"只列五项（next-card / check-gate / .state.yaml / agate_common / dispatch-protocol），缺口定为"把读状态→查状态转移表→推进/回退→落盘串成 CLI"。核验仓库发现状态机侧的既有资产远不止 60%：

| 既有资产 | 实际功能 | 与笔记的关系 |
|---------|---------|-------------|
| `agate/state-machine.md` | 完整状态机定义：状态集合/转移规则/回退规则/PAUSED 恢复/单步函数（state-machine.md:69-391）| 笔记未引用，却声称"未连成状态机" |
| `agate/loop-orchestration.md` | 三档自动化（手动/半自动/全自动 /loop），档位 C 已是"自动跑 P1-P8、硬中断点必停"（loop-orchestration.md:46-74）| 笔记未引用，其"推进决策自动化"诉求已有近似实现（档位 B/C）|
| `agate/scripts/check-state-transition.py` | 机械校验：P2.3 phase 跳变合法性 / P2.4 重试超限→PAUSED / P2.5 回退 diff≥2→强制 PAUSED / RM-AG0042 retries 对应性（check-state-transition.py:2-16, 48-60）| 笔记未列；这正是"状态转移表 + 机械校验"的现成骨架 |
| `agate/scripts/agate-retreat-to.py` / `agate-retreat-state.py` / `agate-archive-stale-outputs.py` | 自动化多步单向回退（每步独立 gate 校验的 commit）+ 被跨过阶段产出归档（rules/state-transitions.md:69-85）| 笔记称"推进/回退 CLI"为缺口，但**回退侧 CLI 已存在** |
| `agate/rules/phases.yaml` + `rules/state-transitions.md` | TAG0021 结构化层：phase/id/exec_role/outputs/gates/retry_cap 数据面 + S-1/S-2 一致性 gate（phases.yaml:1-10）| Phase 1"定义状态转移表 schema（YAML：phase/gate/输入产物/下一 phase/角色）"与 phases.yaml 字段高度重叠，唯一新增是"下一 phase"边 |

推演：

```text
现状评估偏差："60%"低估——推进判定与转移校验已由 check-state-transition.py 承载，回退 CLI 已有
→ 真实缺口收敛为：① 转移表的"下一 phase/回退边"结构化（phases.yaml 无此字段）
                   ② 推进侧 CLI（agate next/advance）
→ 若按笔记 Phase 1 从零定义 schema：与 phases.yaml 重复造轮子，
  且违反笔记自己 4.4"不该造的是另一个 workflow 引擎"的克制原则
→ 与既有 S-1/S-2 双向一致性 gate（check-structure-consistency.py）的衔接也未讨论
```

可选修正：

1. 5 节资产表补列 state-machine.md / loop-orchestration.md / check-state-transition.py / agate-retreat-*.py / rules/phases.yaml；
2. Phase 1 改为"扩展 phases.yaml（增 next/retreat 字段）+ 扩展现有 check-state-transition.py"，而不是新建 schema；
3. 显式论证与既有 /loop（loop-orchestration.md）的关系：状态机 CLI 是 /loop 档位 C 的机械替身还是并行动物，二者如何取舍。

## W1（WARNING）："流程层 100% 可程序化"过度简化

第 3 节三层拆解表把流程层（阶段推进、gate 判定、回退重做、派发决策）标为"✅ 100%——确定性状态机"。核验 state-machine.md 与 dispatch-protocol.md，流程层含大量非确定性成分：

- **PAUSED 汇合**：任意阶段遇 NEED_CONFIRM/PROD_TOUCHED/GAP/retry 超限 → PAUSED，恢复依赖人工决策（state-machine.md:95-99, 254-263）——不是状态机查表能独立决定的
- **跨阶段回退**：P5/P6 gate 失败 → 回 P4；回退 diff≥2 → 强制 PAUSED + 人工批准（state-machine.md:132-133, 148, 615-658）——回退目标由诊断（模型）决定
- **裁剪跳变**：P1 裁剪声明驱动 P2→P4 / P5→P8 / P7→DONE 等跳边（state-machine.md:218-224）——跳边由 P1 analyst 产出 + 主 Agent 确认
- **SCOPE+ 定向回补**：任意阶段发现新需求 → 增补 P1 → "判断影响范围"依赖主 Agent 临场判断（state-machine.md:233-241，笔记自述"无明确决策规则"）
- **P6.5 judge 门槛**：判定层模型节点（WORKFLOW.md:310），笔记已承认"判定层混合"

推演：笔记第 3 节自己也写了"完全编排程序化 ≠ 完全自动化"（58 行），但"流程层 100% 可程序化"的表述把上述模型/人工依赖点排除在外；若按 100% 承诺立项，落地时会发现状态机只能覆盖"主线推进 + 单步回退"子集，其余仍要 orchestrator/人兜底——承诺与交付不符。

可选修正：把"流程层 100% 可程序化"改为"主线推进与单步回退可程序化（确定性状态机）"，PAUSED/跨阶段回退/裁剪跳变/SCOPE+ 显式列为"状态机暂停点（转模型/人工）"，与 4.2"平台=执行环境"的降级叙事对齐。

## W2（WARNING）：第 7 节"gate 失败 → 回当前 phase"与现有回退语义不符

第 7 节风险对策："转移表只定义'正常推进 + 有限回退'（gate 失败 → 回当前 phase），judge NEEDS-REVISION → 回退路径同样表驱动；不做任意图。"

核验 state-machine.md 的实际回退语义：

```text
P5 --[failed>0 && retry<MAX]--> P4 (retry+1)      # 不是"回当前 phase"
P6 --[任何 BDD 标 FAIL && retry<MAX]--> P4 (retry+1)  # 回实现阶段，不是回 P6
P6.5 --[needs-revision/rejected]--> P6 重验（judge 轮次 ≤2）
回退 diff≥2（如 P6→P4/P7→P4）→ 强制 PAUSED，人工批准（state-machine.md:636-658）
```

推演：若按"gate 失败 → 回当前 phase"实现转移表，会把 P5/P6 失败错误地路由为同阶段重试，绕过"回实现阶段 P4"的既有语义；且"有限回退"的边界（diff≥2 必须 PAUSED）已在 check-state-transition.py:10 机械拦截，转移表若不与之一致会造成双套判定（表说回、脚本拦）。

可选修正：转移表明确"gate 失败的目标回退阶段"（P5/P6→P4、P6.5→P6），并把"跨阶段回退 → PAUSED"写进转移表状态集合；引用 rules/state-transitions.md 既有回退规则（69-85 行）作为实现基础。

## W3（WARNING）：4.3 三条护栏可执行性不足且自相矛盾

三条护栏是本文档的核心防分叉机制，但：

1. **护栏 2 与现有文档结构冲突**："协议文档里平台名只出现在'如何实现'小节"——现有 `platform-notes.md` 整篇按平台组织（OpenCode/Claude Code/Codex/DSH 各一章），是"平台适配权威源"（platform-notes.md:3）；WORKFLOW.md「已知适用环境」表也含平台名（WORKFLOW.md:143-148）。按护栏 2 严格执行，platform-notes.md 要么被整体归入"如何实现"，要么需要大规模迁移——笔记未评估该落地成本。
2. **护栏 1 与笔记自身矛盾**：护栏 1 要求"协议层只认'并行批'，不发明'workflow 模式'/'ralph 模式'"——而 4.1 语义表恰以"DSH 实现"列名（workflow/ralph/goal）标注语义，且 B1 已指出五模式误述把工具名倒灌进协议层。护栏的"语义小节"边界本身未定义（哪节算语义、哪节算实现，无判据）。
3. **无机械兜底**：三护栏均为文档写作纪律，靠"评审时检查"（7 节），与笔记自己推崇的"exit code 才是门槛"哲学存在张力——护栏本身没有 exit code。

推演：护栏无判据 = 无分歧仲裁标准。两平台开发者对"并行批该渲染成 workflow 还是 N 路 Task"有分歧时，护栏 3"通用食谱先于平台食谱"无法机械判定谁对；需在 4.3 补"语义小节"的可操作定义（如：以 `rules/*.yaml` 数据面为语义，md 正文含平台名的段落必须指向数据面）。

可选修正：① 护栏 2 明确 platform-notes.md/SETUP.md 的归属（建议：整文件视为"如何实现"，语义侧只在数据面/阶段卡片）；② 语义锚点改挂机器可读面（rules/phases.yaml + dispatch.yaml），平台渲染归"实现注记"；③ 护栏增加可判定化方向（如 check-protocol-consistency.py 增加"语义锚点文件禁含平台名"检查），对齐"exit code 才是门槛"。

## W4（WARNING）：gate exit code 作为"确定性状态机输入"忽略 exit 2 语义

第 2 节方案 C 与 4.2 均把 gate 判定建模为 `{phase, gate_exit_code, 输入产物} → 下一 phase`。核验 check-gate.py 的 exit code 契约（check-gate.py:6-7）：`exit 0 = 通过; exit 1 = 未通过; exit 2 = 需主 Agent 自判（含动态 gate_commands 或语义判断）`。

实际返回 exit 2 的分支（grep 核验）：

```text
P0 gate → return 2（check-gate.py:577 附近：P0-brief 自查提示）
P3 gate → return 2（文件存在，红灯由主 Agent 手动跑 check-tdd-red.py，state-machine.md:112）
P5 gate → return 2（gate_commands.P5 动态读取，需主 Agent 执行）
P6 gate → return 2（脚本化部分通过，仍需主 Agent 判定 provenance/UI 等）
P8 gate → return 2（脚本化部分通过，仍需主 Agent 逐包跑发布检查，state-machine.md:368）
```

推演：exit 2 的语义是"脚本化检查通过，但下一动作由主 Agent 决定"——状态机查表到 exit 2 时无唯一后继，仍需模型介入"跑 gate_commands / 判断语义"。这与 4.2"推进决策 → 状态机查表"的声称冲突：exit 2 恰恰是"推进决策仍是模型"的残留点（笔记 1.2 自己承认的张力）。

可选修正：转移表把 exit code 建模为三态（0=直推、1=回退、2=暂停转主 Agent），并为 exit 2 定义"下一动作"字段（如 P5 exit 2 → 主 Agent 跑 gate_commands.P5）；或承认"推进决策在 exit 2 分支仍需模型"，把 4.2"推进决策全查表"改为"推进决策查表 + exit 2 分支人机混合"。

## N1（NIT）：P6.5 非独立 phase 值未提

P6.5 是挂载于 P6→P7 转移的**强门槛子阶段，非独立 phase 值**（state-machine.md:74-78 "避免扩展 valid_phases / 重试表 / 卡片枚举的连锁改动面"；rules/phases.yaml:89-91 同口径）。笔记第 3 节把 judge 作为"判定层模型节点"、第 7 节说"judge NEEDS-REVISION → 回退路径表驱动"——机制理解正确，但未提 P6.5 不是独立 phase 的实现约束；Phase 1 schema 若按"每 phase 一行"建模会把 P6.5 误列为独立状态。修正：schema 明确支持"子阶段门槛（挂载于转移上）"表达，或引用 state-machine.md 的 P6.5 口径。

## N2（NIT）：design-notes/README.md 未登记本笔记

`docs/design-notes/README.md` 索引无 `design-orchestration-semantics.md` / RM-AG0049 条目（grep 零命中）。按 README 登记格式约定（"新增决策记录时，按这个格式写"，README.md:27）应补登记；与 review-rm-ag0046 的 N1 为同类问题。

## N3（NIT）：外部链接 issue #20849 引用存在但推断超前

4.4 引用的 [opencode issue #20849](https://github.com/anomalyco/opencode/issues/20849) 经 web 核验真实存在，标题为 "[FEATURE]: Plugin-based agent orchestration layer — parallel execution without upstream changes"。"平台层正在往同一方向收敛"是从单个 feature request 推出的结论（issue 未合并、非官方路线图），表述宜降级为"平台层有向该方向演进的社区提案"。

## N4（NIT）：`agate-next-card.py` 功能描述可更精确

5 节把 `agate-next-card.py` 用途写为"选下一张阶段卡"，实际功能是"按 PHASE 参数输出当前阶段卡片全文（含 sha256 校验契约、M3 从 rules/phases.yaml 渲染可判定节）"（agate-next-card.py:2-24, 151-190）——"选下一张"的逻辑不在脚本里，而在 orchestrator 的 phase 推进。建议改述为"输出指定阶段卡片"，避免读者以为该脚本已承担推进选择。

## 建议

1. 修复 B1：4.1/5 节改引 dispatch-protocol 实际五模式，或明确定义新抽象并声明与既有五模式无挂靠关系。
2. 修复 B2：资产表补列状态机侧既有资产；Phase 1 改为扩展 phases.yaml + 复用 check-state-transition.py；论证与 /loop 的关系。
3. 修复 W1/W2：修正"100% 可程序化"与"gate 失败→回当前 phase"表述，对齐 state-machine.md 实际转移/回退语义。
4. 修复 W3：为护栏补"语义小节"可操作定义 + platform-notes.md 归属 + 可判定化方向。
5. 修复 W4：转移表建模 exit 0/1/2 三态，exit 2 显式转主 Agent。
6. 补 N1-N4：P6.5 非独立 phase 口径、README 登记、issue 措辞、next-card 描述。

## 是否通过

**FAIL（需迭代）**。存在 2 个 BLOCKER：统一锚点（dispatch-protocol 五模式）内容误述（B1）、现状资产盘点低估且 Phase 1 与既有结构化层重叠（B2）——两者都直接动摇文档的核心论证（4.1 锚点叙事、5 节落地评估），且 4 个 WARNING（W1 100% 声称、W2 回退语义、W3 护栏可执行性、W4 exit 2 语义）涉及状态机方案与既有 gate/状态机机制的自洽性。方向上方案 C（领域专用状态机 + 平台渲染层收敛）与仓库现状（check-state-transition.py / rules/ 结构化层 / /loop 三档）高度吻合，值得立项，但需按上述 1-6 修正后复审。
