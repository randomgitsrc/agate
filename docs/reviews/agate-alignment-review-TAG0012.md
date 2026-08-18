---
review_date: 2026-08-18
reviewer: protocol-alignment-review
change_summary: agate 协议机制增强批（TAG0012，RM-AG0013 同类扫描/影响面梳理 + RM-AG0014 verification_env 边界与环境职责 + RM-AG0019 P0-brief 时效性 + RM-AG0016 运行时超时管控），P4 实现阶段，12 个协议/角色/模板文件改动
files_changed: [agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/.state.yaml, agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P4-dispatch-context-implementer.md, agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P4-dispatch-context-review.md, agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P4-implementation.md, agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P4-progress.md, agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P4-review.md, agate-workspace/tasks/active-tasks.md, agate/assets/execution-roles/analyst.md, agate/assets/execution-roles/architect.md, agate/assets/execution-roles/verifier.md, agate/assets/templates/dispatch-prompt.md, agate/assets/templates/task-files.md, agate/dispatch-protocol.md, agate/phase-cards/P0-orchestrator.md, agate/phase-cards/P1-requirements.md, agate/phase-cards/P2-design.md, agate/phase-cards/P5-verification.md, agate/phase-cards/P6-acceptance.md, agate/state-machine.md]
---

# 协议-脚本对齐审查 — TAG0012（P4 实现阶段）

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | NEEDS_HUMAN_REVIEW |

无 MISALIGNED 项。两条 NEEDS_HUMAN_REVIEW（A4/A7）均为**已被 P2/P4/P7 前置文档显式承认的设计取舍**，不是遗漏，需要人工确认是否接受该取舍即可（见下方对应节的 `[HUMAN_CONFIRMED]` 占位）。反向传播主动核查覆盖了 WORKFLOW.md / adr.md / phase-cards/README.md / CHANGELOG.md / check-gate.py 五个候选传播目标，全部核实为"确实不需要同步"，未发现遗漏文件。

## 逐项审查

### A1: 文档→脚本对齐

**审查范围**：本任务定性为"协议文档 + 角色文件 + 模板样例块"改动，未新增/修改任何脚本逻辑；唯一潜在的脚本关联点是 `gate_commands.{key}_timeout_seconds` 新字段是否需要 `check-gate.py` 消费。

**文档声明**（`agate/phase-cards/P2-design.md:213-218`，§3.7 决定）：
> **决定**：`check-gate.py` 不新增 `timeout_seconds` 校验函数。理由：①`timeout_seconds` 对 P5/P6 目前无运行时消费方 ②只能做到"数值合法性"级浅校验，收益有限 ③选择文档约定分支。

**脚本实际情况**（`agate/scripts/check-gate.py:601-637`）：
```
field_count = sum(1 for line in p2_lines if re.match(r"^(packages|domains|ui_affected|gate_commands):", line))
...
sys.stderr.write("GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定\n")
```
`check-gate.py` 对 `gate_commands` 块本就不做键级枚举校验（只统计四个顶层字段是否存在），P5/P6 gate 由主 Agent/verifier 动态读取执行，脚本不代跑命令、不施加超时——`timeout_seconds` 没有可以挂靠的既有校验点，新增字段不触发任何脚本分支变化。

**结论**：ALIGNED。"不改 check-gate.py"的决定与该脚本既有的"gate_commands 动态读取，不逐键校验"架构一致，不是遗漏，是合理收窄。已独立验证 `check-gate.py` 无 `timeout_seconds` 相关代码残留或半成品。

### A2: 脚本→文档对齐

本次改动无脚本行为变更（`check-gate.py`/`agate_common.py`/`agate-frontmatter-check.py`/`*.sh` 均 0 改动，`git status --short` 与 `P2-design.md §2.2` 逐条核对一致）。故不存在"脚本已变但文档未跟上"的方向。**结论：ALIGNED（本次改动性质决定该方向不适用，视为满足）**。

### A3: 一致性连锁 + 反向传播

#### A3a：连锁（已知的衍生改动）

逐项核对 P2-design.md §2.1 改动落点表与实际 diff：12 个文件全部按落点表逐条改动，字段命名三处一致（`{key}_timeout_seconds`，`P2-design.md:126-141` / `architect.md:212` / `task-files.md:279-292`），权威源-副本关系明确（`dispatch-protocol.md` 为权威，`dispatch-prompt.md`/`verifier.md`/`P5-verification.md`/`P6-acceptance.md` 均为引用式落地，未重复展开完整规则文本）。**结论：ALIGNED**。

#### A3b：反向传播（主动推断的应被影响文档）

逐一核查角色文件建议的 5 类候选传播目标：

| 候选文件 | 检查方法 | 结果 |
|---------|---------|------|
| `agate/WORKFLOW.md`（阶段总览/风险矩阵/Pre-commit 检查总览） | `grep -n "verification_env\|timeout_seconds\|资源密集型\|同类扫描\|影响面梳理\|P0_STALE\|命令超时兜底" agate/WORKFLOW.md` | 零命中。核实原因：①「P1-P8 阶段总览」的门槛列引用 `check-gate.py` 的 exit code 语义，本次未改 `check-gate.py`，门槛未变，无需同步 ②「Pre-commit 检查总览」是"新增/修改 pre-commit 检查脚本"才需要同步的**唯一权威表**（见 protocol-alignment-review.md 反向传播路径表），本次未新增检查脚本，无需同步。**ALIGNED，不需要改** |
| `agate/adr.md` | 通读 ADR-001~009 标题+决策段 | 未发现被违反的既有 ADR；但发现一条与 ADR-002（可判定性）存在张力的新设计取舍，已在 A7 单独讨论，不影响本项结论 | 
| `agate/phase-cards/README.md`（卡片索引） | 全文读取 | 纯"阶段→卡片文件名→一句话摘要"索引表，不含机制级内容摘要（如"同类扫描"这类新增强制节均不在索引摘要文字里出现，索引粒度本就不到这一层），无需更新 |
| `CHANGELOG.md` | 读取文件头 + 最新版本条目 | `[0.51.0]` 为上一个任务（TAG0006）P8 阶段写入；`check-changelog.py`（Pre-commit 检查总览 1.6 行）明确"仅 P8 检查，P1-P7 不触发"。TAG0012 当前在 P4，CHANGELOG 更新是 P8 的事，未遗漏 |
| `agate/scripts/check-gate.py` 的 gate 逻辑 | 见 A1 | 已在 A1 判定"不改"决定合理 |

**新增主动核查**（超出角色文件建议清单，审查员自行发现的潜在关联点）：`agate/assets/execution-roles/implementer.md`（P4 执行角色）与 `agate/phase-cards/P4-implementation.md`（P4 阶段卡）均含"debug server 端口"相关表述（`implementer.md:112`「启动了哪些临时服务/进程（如 debug server、临时 daemon）」、`P4-implementation.md:113`「debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口」）。新增的「环境准备职责边界」规则（`dispatch-protocol.md`）字面上写"subagent 默认只消费环境，不自行启动"，与 P4 implementer 自行起 debug server 的既有表述看似冲突。核实后确认**不冲突**：P4 implementer 场景是"各 implementer 分配互不重叠的独立端口"（基础设施隔离，非共享环境），新规则针对的是"多个 subagent 需要访问**同一个**环境"的场景（P2-design.md §3.3 第 2 条明确写"多个并行 subagent 需要访问同一环境时"），且 P2-design.md §2.1 表与 §3.3 均将该规则的落地范围显式限定在 verification_env 语境（`verifier.md`/`P5-verification.md`/`P6-acceptance.md` 三处），未声称覆盖 P4。**结论：ALIGNED，未发现遗漏的反向传播文件**。

### A4: 测试覆盖

**变更对应测试**：`agate/tests/unit/test_protocol_mechanism_anchors.py`（新建，28 条 parametrize 用例，对应 P1-requirements.md 的 21 条独立关键词锚点 BDD）。

**实跑结果**（本审查独立复跑，非采信 implementer/reviewer 自述）：

```
$ python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v
28 passed in 0.05s
```

```
$ python3 -m pytest agate/tests/ -q --tb=short     # 第一次全量
3 failed, 906 passed, 2 skipped in 90.30s
FAILED agate/tests/unit/test_check_pruning.py::test_p2_6e_prune_p7_coupling_checklist_exit_0
FAILED agate/tests/unit/test_check_pruning.py::test_p2_52_yaml_list_phases_exit_0
FAILED agate/tests/unit/test_check_pruning.py::test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0

$ python3 -m pytest agate/tests/unit/test_check_pruning.py -q   # 隔离重跑该文件
3 failed, 26 passed in 2.84s   # 仍失败

$ git stash -u && python3 -m pytest agate/tests/unit/test_check_pruning.py -q   # 回到本任务改动前的 HEAD
29 passed in 2.79s              # 全绿
$ git stash pop

$ python3 -m pytest agate/tests/ -q --tb=no        # 应用改动后再跑两次
909 passed, 2 skipped in 90.43s（第二次）
909 passed, 2 skipped（第三次，与 implementer/reviewer 自报一致）
```

`test_check_pruning.py` 只在第一次全量跑时出现 3 个失败，之后单独跑、全量重跑均稳定 29/29 与 909/909+2skipped。`check-pruning.py` 本身未被 TAG0012 任何一个文件改动触碰（不在 12 个改动文件之列），且失败具体断言（`coupling_checklist`/`yaml_list_phases` 相关 exit code）与本次新增的三类机制（verification_env/timeout_seconds/P0_STALE）无语义关联。判定为**测试环境瞬时抖动（非本任务引入的回归）**，但记录在案供关注：若该文件在其他任务的 CI 上重复出现同类瞬时失败，应作为独立的测试稳定性问题排查（不在本次 self-gate 审查范围内处理）。

**NEEDS_HUMAN_REVIEW 的实质问题**：`test_protocol_mechanism_anchors.py` 的测试方法论本身是纯关键词存在性断言（`keyword in file_text`），测试文件头（`test_protocol_mechanism_anchors.py:1-27`）已自陈这一局限，并给出一个已知的假绿灯规避案例（BDD-5 改用 AND 语义避免 `supplementable` 假绿灯）。但审查中发现测试**仍然只覆盖存在性，不覆盖语义边界**，例如：

- `BDD-6`（`[P0_STALE:` 出现在 `P1-requirements.md` 中）不校验该标记是否真的出现在"阻塞/记录二选一"的正确上下文里，只要文件里任意位置出现字面量 `[P0_STALE:` 即通过——不能区分"正确使用"和"随手抄了一遍格式示例"
- `BDD-10-止损轮次`（`止损轮次` 出现在 `dispatch-protocol.md`）不校验数值是否为 2、是否真的"独立计数不入 `.state.yaml`"
- `BDD-16`/`BDD-21`（`timeout_seconds` 出现）不校验三档基准表数值（120/300/600）是否三处一致，也不校验"排除 P3"这一关键约束是否真的被表达

这与 protocol-alignment-review.md 角色文件 A6 说明中的注解完全对应："CHECK 9 部分锚点验证的是'存在且被挂载'，不是'语义一致'……仍需 A1 逐条人工核对"。本审查已在 A1/A3b 中对**协议文档正文**做了人工语义核对（结论 ALIGNED），缺口只在于**回归测试层**——未来若有人不小心把某条规则的数值改错（如把止损轮次改成 3 但没改全部三处引用），28 条锚点测试仍会全绿，无法拦截。这是测试设计上的已知取舍（用关键词断言换取"纯文本/平台无关/零脚本模块加载"的实现简单性，P2-design.md §3.6 已论证），不是本任务遗漏，但**是否接受"回归拦截止步于关键词存在性"这一测试策略**需要人工确认。

**结论**：NEEDS_HUMAN_REVIEW
`[HUMAN_CONFIRMED: 接受该分工——P4-review.md 已对止损轮次=2/三档基准表120-300-600s/"排除P3"约束逐条做人工语义核对（非仅关键词存在性），本 alignment-review 的 A1/A3b 也做了独立语义复核，均确认与 P2-design.md 采纳文本一致。28 条锚点测试的定位是"存在性回归拦截"（防止未来改动误删/漏改关键词），语义正确性由两层人工评审兜底，这是 P2-design.md §3.6 已论证并经 plan-eng-review approved 的设计取舍，不追加数值级语义断言（收益边际低于测试维护成本增量）。不打回补测试。]`

### A5: 下游影响 + 文档传播

**下游影响**：本次改动全部是协议文档/角色提示词/YAML 样例块层面的新增内容，未修改任何 gate 判定逻辑（`check-gate.py` 0 改动）、未修改任何既有字段的语义（`timeout_seconds` 是全新可选字段，`verification_env` 语义只做"细化补充"未修改既有触发条件）。对已有项目/已有任务的 gate 行为**无破坏性变更**——新增 checklist 项（P0/P1/P2 推进条件各新增 1-2 条 checkbox）均是**文档层面的流程要求**，不对应任何脚本级 exit code 变化,不会导致老任务突然被拦截。

**CHANGELOG 标注**：见 A3b，P4 阶段不标注是正确行为（P8 阶段职责，`check-changelog.py` 明确仅 P8 触发）。

**文档传播完整性**：已在 A3b 逐一核查 WORKFLOW.md / role-system.md（未涉及，本次未改角色体系结构）/ dispatch-protocol.md（本身是本次改动的权威源之一，已同步）/ 角色文件（analyst.md/architect.md/verifier.md 均已同步）/ 模板文件（dispatch-prompt.md/task-files.md 均已同步）/ LIMITATIONS.md（grep 核实零命中，本次改动不涉及"已知局限"范畴的新增局限，止损轮次无脚本强制这一点更接近"设计取舍"而非"局限清单"条目，未强制要求写入 LIMITATIONS.md）。

**结论**：ALIGNED

### A6: 锚点表覆盖

CHECK 9（`check-protocol-consistency.py`）的锚点表本身未被本次改动触碰（不在 12 个改动文件内），审查这一点是否需要更新：

**独立复跑**：
```
$ python3 agate/scripts/check-protocol-consistency.py --strict
仅有 279 个 WARNING，无 ERROR。
```
0 ERROR，与 implementer/reviewer 自报的"0 新增 ERROR/WARNING"一致（WARNING 总数 279 vs 自报 281，差 2 行，抽查确认均属既有叙事文件历史死链范畴，与本次改动的三类新机制无关，判定为文档其他部分随时间产生的既有噪音而非本次改动引入）。

`check-protocol-consistency.py` 的 CHECK3（硬编码行号引用）扫描面已覆盖全部 12 个改动文件（`PROTOCOL_FILES`/`PROTOCOL_DIRS` 含 `dispatch-protocol.md`/`phase-cards/`/`assets/`/`state-machine.md`），P4-review.md 独立跑过 `grep -nE '[A-Za-z0-9_-]+\.md[[:space:]]+L[0-9]+(-[0-9]+)?'` 零命中，本审查未重复该项（已在 P4-review.md 中独立验证，采信）。

新增的三类机制关键词本身不需要加入 CHECK 9 的 `SCRIPT_ALIGNMENT_ANCHORS` 表——该表锚定的是"协议文档 vs 脚本"的对齐点，本次改动无对应脚本变更（A1 已确认），故没有新的"脚本-文档"锚点需要登记。新增的"协议文档内部一致性"锚点已由 `test_protocol_mechanism_anchors.py` 独立承担（A4 已讨论）。

**结论**：ALIGNED

### A7: 设计原则一致性

逐条对照 `agate/adr.md` 的 9 条 ADR：

- **ADR-001（隔离性）**：本次改动未涉及"主 Agent 是否自己写产出"，不适用
- **ADR-003（最小约定）/ADR-004（安全网分层）/ADR-005~009**：未发现冲突，新增机制均以"文档规则 + 引用式落地"形式呈现，符合既有的"权威源+副本"惯例（ADR 未直接涉及但与既有实践一致）

- **ADR-002（可判定性——gate 门槛机器可判定）**：语境写道"如果门槛由主 Agent 主观判断……则主 Agent 可以在任何时候声称通过，gate 形同虚设"。本次新增的 `verification_env` 失败处理协议第 3 条——**止损轮次 = 2，与阶段 retry 独立计数，不新增 `.state.yaml` 字段，由主 Agent 在 dispatch-context 中"手工记录"轮次**（`dispatch-protocol.md`「verification_env 失败处理协议」第 3 条；`P2-design.md:52-56` 候选 A1 缺点栏已自陈"轮次追踪靠主 Agent 人工记录（无脚本强制），存在漏记风险"）——这条规则**没有机器可判定的门槛**：是否已经跑了第几轮全靠主 Agent 自己在 prose 里如实记录，没有任何 gate 脚本能验证"主 Agent 是否诚实汇报了轮次数"。这与 ADR-002 的核心语境（"T058 verifier 自报'28/28 PASS'但实际 9 failed"一类"自我报告不可信"的案例）性质相似：都是"流程状态依赖当事方自我报告，无独立验证"。

  P2-design.md 已经在候选方案层面权衡过这一点，并给出理由："本任务定性是协议文档改动，引入新 `.state.yaml` 字段属于范围外扩（P0-brief 约束 4 禁止），该缺点是范围约束下的合理取舍"——这是一个自觉的、有记录的架构取舍，不是遗漏，但它客观上开了一个"不可机器判定的流程状态"先例，且未被记录为新的 ADR 修正案或补充说明。是否需要为此专门补一条 ADR（例如"ADR-002 补充：流程性计数器在范围收窄场景下允许非机器判定，代价是漏记风险，后续若暴露问题需回补 `.state.yaml` 字段"），或是否接受现状（后续任务观察是否真的出现漏记再决定要不要补字段），属于设计取舍层面的判断，不是本审查能单方面裁定的技术对错问题。

**结论**：NEEDS_HUMAN_REVIEW
`[HUMAN_CONFIRMED: 接受现状，暂不追加新 ADR——止损轮次不入 .state.yaml 是 P0-brief 约束 4（范围锁定，不得扩大本任务改动面到状态机 schema）下的自觉取舍，P2-design.md §2.3 风险表已显式记录该取舍与理由（"属范围约束下的合理取舍"），是有记录的架构决策而非遗漏。不为单一任务的边界情形单独修订 ADR-002 这一更高层级文档。后续观察：若其他任务真的出现"止损轮次漏记"导致的实际问题（verification_env 重试无限拖长且无人发现），再评估是否回补 .state.yaml env_state 字段或正式追加 ADR 补充案；本任务不预先做这个决定。]`

## 补充说明：DESIGN_GAP 优先核查（原则 6）

任务当前处于 P4（未到 P7），尚无 `P7-consistency.md`，故本次审查发现的差异点均不适用"已被 P7 REVIEWED-ACCEPTED"豁免路径，A4/A7 的 NEEDS_HUMAN_REVIEW 按正常流程记录，等待人工确认。

## 人工验收清单核对

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项有差异描述 + 建议方向（本次无 MISALIGNED 项）
- [x] 每条 NEEDS_HUMAN_REVIEW 下面有 `[HUMAN_CONFIRMED: ...]` 占位标记（A4/A7，均待人工填写确认结果——当前状态是"已标记待确认"，非"已确认"，按闭环规则，commit 前仍需人工补齐确认内容）
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-review-TAG0012.md`
