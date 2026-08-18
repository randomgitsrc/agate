---
phase: P6
task_id: TAG0012-protocol-mechanism-fixes
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0012-P6-20260818
status: draft
created: 2026-08-18
agent: verifier
# ── v2.0 机器汇总 ──
pass: 23
fail: 0
ui_affected: false
---

[NO_NEED_CONFIRM]
[PROD_NOT_TOUCHED]

# P6 验收报告 — TAG0012 协议机制增强批（RM-AG0013 / RM-AG0014 / RM-AG0019 / RM-AG0016）

## 0. 验收方法与边界

本任务的"用户"是**未来读这些协议文件的主 Agent / subagent**，"行为"是**协议文本能否让读者据以正确行动**。因此本轮验收：

1. **不复用 P5 结论**。P5 的 `test_protocol_mechanism_anchors.py` 28/28 只证明"关键词存在"，不证明"内容语义正确"。本轮对 23 条 BDD 逐条打开 HEAD 下的实际协议文件，读新增段落原文，逐句对照 P1-requirements.md 的 Then 子句判定。
2. **证据形式为文本摘录**（本任务 `ui_affected: false`，无截图 / 无 vision）。`P6-evidence/bdd-NN-*.md` 每个文件含两部分：① Then 子句**逐项**核对（每项写"Then 要求什么 → 实际文本怎么写的 → 是否满足"）；② 从实际文件摘录的原文片段（含文件路径与行号）。证据文件可脱离本报告独立复核。
3. **本轮独立实跑的命令**（输出落 `P6-evidence/shared-p6-command-output.log`，非转抄 P5）：
   - `timeout 120s python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v` → **28 passed, exit 0**
   - `timeout 180s python3 agate/scripts/check-protocol-consistency.py --strict` → **0 ERROR / 279 WARNING**（exit 2 为该脚本 `--strict` 有 WARNING 时的既定语义），CHECK 1/3/4/6/7/8/9/11 全 ✅ PASS
   - `grep -n timeout_seconds` 三文件命名一致性核对
   - BDD-13/BDD-14 双源关键词逐条计数对照
4. **环境**：工作目录 `/home/kity/oclab/agate/.worktrees/agate-TAG0012`，HEAD = `e40adac`（含 P4 commit `27509a2` 的 12 个协议文件改动）。只读验收，未修改任何协议/脚本文件，未碰主 checkout 与 `~/.agate`。P5 全量回归结果（909 passed / 0 failed）作为"未破坏既有行为"的旁证引用，不替代任何一条 BDD 的语义验证。

## 1. 逐条验收结果（23 条）

### 文件分组 A：`agate/phase-cards/P0-orchestrator.md`

- PASS BDD-1: 新增 `## 同类/影响面预判（强制，写在 known_risks 里）` 小节，预判三问覆盖 Then 要求的"历史同类实例"（grep 记命中数 + 文件清单）与"牵动哪些子系统/文件簇"（上下游消费方 + 未来实例拦截手段），并给出 `known_risks` 写法 yaml 示例；关键词可 grep (bdd-01-p0-scan-preview.md)
- PASS BDD-2: 「推进条件」新增 `**P0-brief 时效性自检已执行**` checklist 项，四字段（task / executor_env / known_risks / env_constraints）在漂移判据中全部有落点，严重漂移→回 P0、轻微漂移→更新字段并标 `[P0_STALE]`，"无间隔或无漂移→记录已核对"使首次立项即执行的任务不被额外阻塞（presence 语义） (bdd-02-p0-staleness-checklist.md)

### 文件分组 B：`agate/state-machine.md`

- PASS BDD-3: `P0 --[...四字段自查通过...]--> P1` 转移条件**紧邻下方**新增括号注解，首句即"四字段自查含时效性校验"，显式覆盖搁置重启 / 跨会话恢复 / 从 PAUSED 恢复三种重启场景并声明"同样强制"，判据全文引用 P0 卡「P0-brief 时效性自检（漂移判据）」不重写；引用用节标题非行号，CHECK3 ✅ (bdd-03-state-machine-staleness.md)

### 文件分组 C：`agate/phase-cards/P1-requirements.md`（阶段卡）

- PASS BDD-4: 新增 `## 同类扫描（强制节）`，明确要求对关键符号 grep/rg 扫**全仓**并记命中数 + 文件清单，逐条判"处理/不处理 + 理由"，同类问题会新增时转 BDD 声明拦截手段，结论必须落盘 P1 正文（"只此一处"也要写出），缺失 → requirements-review 打回 (bdd-04-p1card-similar-scan.md)
- PASS BDD-5: 新增 `## verification_env vs supplementable 边界判断树`，ASCII 判断树左枝=能力缺失走三态、右枝=运行环境（服务/端口/数据库/依赖/平台）走 verification_env，口诀 +"把环境问题标 supplementable 属机制误用"确立二者不可互替；同节末含**环境验证轮次预算占位声明位**（`verification_env_budget` yaml 示例，数值权威定义外引 dispatch-protocol.md） (bdd-05-p1card-env-vs-capability.md)
- PASS BDD-6: 新增 `## P0-brief 时效性质疑`，`[P0_STALE: 具体漂移点]` 标记格式强制带出漂移点（禁裸标记），阻塞/记录**二选一**以三行表按严重/轻微/无漂移分流且各档规定落盘内容，明写"不允许既不阻塞也不记录地含糊推进" (bdd-06-p1card-p0stale-rule.md)

### 文件分组 D：`agate/assets/execution-roles/analyst.md`

- PASS BDD-7: 「隐含需求清单」列表首位新增 `- **同类/影响面**：…` 条目，覆盖"仓库里还有别的实例吗"与"被改动符号有哪些消费方"两问，与既有数据/前端/多端/边界/兼容五维度同级同体例并列，落地要求引 P1 卡「同类扫描」 (bdd-07-analyst-scan-dimension.md)
- PASS BDD-8: 「三态判断规则」之后新增 `**判断树：缺的是能力还是环境？**`，能力侧（看不见图/不会用工具/没有技能）→ available/supplementable/GAP，环境侧（服务没起/端口没通/数据库没建/依赖没装/平台不支持）→ verification_env；含可操作自问句与口诀，并显式引 TAG0009 机制误用教训 (bdd-08-analyst-capability-vs-env-tree.md)
- PASS BDD-9: 「输入（自己读取）」节紧邻下方新增"读完 P0-brief 的第一个动作：质疑它的时效性"四步流程——先对照 P0 卡严重 3 条排查（非只确认非空）→ 严重则写 `[P0_STALE: 具体漂移点]` 并停下报告主 Agent → 轻微则标记并注明已更新字段后继续 → 无漂移写"已核对"，再进入需求质疑 (bdd-09-analyst-p0brief-staleness-step.md)

### 文件分组 E：`agate/dispatch-protocol.md`

- PASS BDD-10: 新增 `**verification_env 失败处理协议**` 权威子节，四个必答问题逐条有可执行答案——① 可重试/不可重试**二列判据表**（不可重试类含"机制误用型"且不消耗轮次预算）② 批处理要求（单轮 ≥2 个待验假设须同轮批量验完，附 TAG0009 11.7 小时教训）③ 止损轮次 = 2、与 `retries[Pn]` 独立计数、由**主 Agent** 在 dispatch-context 记录轮次追踪、超限转 **PAUSED** ④ READY 后归属**三条判据**（本任务遗留 / 环境本身问题 / 证据不足默认按第 1 条） (bdd-10-verification-env-failure-protocol.md)
- PASS BDD-11: 同节新增 `**环境准备职责边界**` 权威子节——条款 1"启动/维护/关停默认归主 Agent（或 P0-brief 声明的单一责任方），subagent 只消费不自启"，条款 2"并行 subagent 共享环境由主 Agent 统一启动 + dispatch-context 注入访问方式"，条款 3 与 `.state.yaml` 的 `env_state` 建立引用关系（指向 state-machine.md「主 Agent 的单步执行（一轮）」环境一致性验证步骤，本轮已核实该目标节实际存在），不重复定义字段语法 (bdd-11-env-ownership-boundary.md)
- PASS BDD-12: 「派发编排机制」§4 并行规则以**追加第 4 条**形式（未新建独立小节）新增"资源密集型默认串行"：即使无数据依赖/无共享文件改动也默认串行，四条判据（xdist 多进程 / CDP-Playwright E2E / 构建打包安装 / 独占外部资源）各注明竞争对象，要并行须先按 P4 卡分配隔离参数否则串行；与「全阶段适用表」P5 行**双向**建立引用（P5 行同步改为"资源密集型命令 → 模式 5（串行）"） (bdd-12-parallel-rule-4-resource-serial.md)
- PASS BDD-13: 「派发 prompt 模板」规范正文新增 `## 命令超时兜底（层级 4，所有 bash 命令强制）` 标准段，五点全覆盖——① 倍数规则存在且定为 **×1.5**（已声明 `{key}_timeout_seconds` 则直接取该值）② 超时后固定三动作（停止执行不换命令不深挖 / 写 progress 记卡在哪条命令 / 返回主 Agent）③ 非预期失败走同一套动作 ④ 落盘粒度扩展到"每条 bash 命令执行前" ⑤ 新增 `### 命令超时兜底与既有超时机制的分层关系` 子节，四层对照表显式区分层级 4 与层级 2（脚本内部硬超时 HARD 90s/180s）并规定外层须留够内层余量；条件性子句以 L521 示例块后的"为何本示例不展开「命令超时兜底」"说明闭合（判定 self-gate/alignment-review 多为秒级短命令不适用，但声明纪律仍全局适用并给出触发追加条件） (bdd-13-command-timeout-fallback.md)

### 文件分组 F：`agate/assets/templates/dispatch-prompt.md`

- PASS BDD-14: 三处同步落地（「执行顺序」第 4 步补"跑任何 bash 命令前先设超时"、「分阶段落盘」补"每条 bash 命令执行前"粒度、新增 `## 命令超时兜底（层级 4，所有 bash 命令强制）` 段），与协议侧在倍数（×1.5）、取值来源、失败三动作、触发条件、层级归属上逐条一致，无矛盾表述；唯一措辞差异（模板侧写 `timeout 180s <你的命令>` 而非 `timeout {N}s {命令}`）源于渲染模板禁残留花括号占位符的既有回归约束，语义等价；本轮实跑 `check-protocol-consistency.py --strict` **0 ERROR** (bdd-14-dispatch-prompt-sync.md, shared-p6-command-output.log)

### 文件分组 G：`agate/phase-cards/P2-design.md` + `agate/assets/execution-roles/architect.md`

- PASS BDD-15: P2 卡新增 `## 影响面梳理（强制节）`，明写"**写候选方案之前**先做"并被推进条件 checklist 强制；三部分覆盖 Then 两问——"改什么/不改什么"回答"是否波及 P1 未列出的文件/模块"（不改什么栏要求显式列出"看起来该改但决定不改"），"风险在哪"把"双源同步（权威源 + 副本）"列为高频风险回答"是否与既有类似机制冲突或重复"；另要求梳理有客观证据、`follows_existing_pattern` 不豁免 (bdd-15-p2card-impact-analysis.md)
- PASS BDD-15b: architect.md「批次设计（强制节）」末新增「批次设计前置检查项」，第 1 条"影响面梳理已完成"要求批次边界建立在三部分之上并**引用** P2 卡「影响面梳理（强制节）」、明写"本节不重复展开"；与 analyst.md 侧（维度条目 + 引 P1 卡「同类扫描」）形成"角色文件放 checklist/维度 + 指向阶段卡权威节"的对称结构 (bdd-15b-architect-impact-checkitem.md)
- PASS BDD-16: P2 卡「gate_commands 声明」样例块新增 `P5_timeout_seconds` / `P5_e2e_timeout_seconds` 两行 + 新增 `### {key}_timeout_seconds 字段规则` 子节，四个必答问题逐条给出明确答案——① per-key 声明、**不设整体共享默认**（附理由）② 三档默认基准表（单元 120s / E2E 300s / 构建 600s，每档带依据，并标注"手动声明非自动推断"）③ 缺字段 → 行为等同现状，沿用 `dispatch_plan` 先例，不新增阻断 ④ **排除 P3**（P3 继续走 `AGATE_TDD_TIMEOUT`，"两层不合并"并说明运行时消费 vs 静态声明的区别）；architect.md 侧新增"长命令已声明 `{key}_timeout_seconds`"检查项，逐一点名四点并指向 P2 卡权威定义，不重复展开基准表 (bdd-16-timeout-seconds-field-rule.md)

### 文件分组 H：`agate/phase-cards/P5-verification.md`

- PASS BDD-17: 「按包拆分并行」节新增"**但『无写冲突』不等于可以随便并行**"段，指出 `gate_commands.P5` 常为全量测试套件（含 xdist）或 E2E 浏览器命令属**资源密集型默认串行**、即使包间无依赖也默认串行，按 dispatch-protocol.md 并行规则**第 4 条**处理并与 BDD-12 双向引用编号一致，判据细节不在本卡重复展开 (bdd-17-p5card-resource-serial-ref.md)
- PASS BDD-18: 同节新增"**环境准备职责边界（本阶段落地）**"段，明确 verifier subagent 默认不自行启动环境、debug server/测试数据库/临时端口由主 Agent（或 P0-brief 声明的单一责任方）统一准备并通过 dispatch-context 注入、并行 verifier 共享环境不允许各自启动；失败分类/批处理/止损一律引用协议两节，本卡只做落地引用 (bdd-18-p5card-env-ownership.md)

### 文件分组 I：`agate/phase-cards/P6-acceptance.md` + `agate/assets/execution-roles/verifier.md`

- PASS BDD-19: verifier.md「verification_env 条件化」条目改为**引用式**——权威定义指向 dispatch-protocol.md「verification_env 条件化」「verification_env 失败处理协议」「环境准备职责边界」三节并明写"本文件只引用，不重复展开"；本文件不再含判据表/轮次数值来源/归属判据等规则副本，只保留两条 verifier 侧操作约束（默认不自启环境、失败先分类再动作且可重试类须一次性批量验完），与协议侧结论逐条一致无分叉 (bdd-19-verifier-ref-style.md)
- PASS BDD-20: P6 卡「按包拆分并行」节末新增"**环境准备职责边界（本阶段落地）**"段，覆盖三点——沿用 P5 已由主 Agent 准备的环境（环境状态未变时不重复起）、需要新环境时同样遵循 dispatch-protocol.md「verification_env 条件化」/「环境准备职责边界」统一准备规则、**不由 verifier subagent 自行启动**（附并行时端口占用与资源竞争后果）；失败分类与止损引用协议不展开 (bdd-20-p6card-env-ownership.md)

### 文件分组 J：`agate/assets/templates/task-files.md`

- PASS BDD-21: `gate_commands:` 权威样例块新增 `P5_timeout_seconds: 120` / `P5_e2e_timeout_seconds: 300` / `P6_timeout_seconds: 120` 三行 + 成块注释（用途 / per-key 命名惯例 / 三档建议档位并标注"手动声明非自动推断" / **缺省行为**"不声明即等同现状、无 gate 拦截、老任务无需回填"），与 BDD-16 的四点规则数值与结论一致；本轮 grep 实证三处（task-files.md / P2 卡 / architect.md）命名统一为 `{key}_timeout_seconds`，无异名。联动子句（P3 key）实际未加 P3 示例，前置条件不触发，且反向以"⚠️ 排除 P3 + 关系说明引用 P2 卡字段规则"与 P3 键注释末追加的"P3 的超时不写 `P3_timeout_seconds`"两处提示直接消除"照抄样例忽略既有机制冲突"的风险 (bdd-21-task-files-schema-sample.md, shared-p6-command-output.log)

### 文件分组 K：`agate/scripts/check-gate.py`（+ 配套 pytest 回归）

- PASS BDD-22: 收敛到 P1 允许的第二分支——P2-design.md §3.7 标题与正文**显式声明**"`check-gate.py` 不新增 `timeout_seconds` 校验函数"并给出三条理由（无运行时消费方 / 只能做浅校验收益有限且增加脚本复杂度 / 把回归拦截压力转移到 grep 断言审计测试）；`agate/tests/unit/test_protocol_mechanism_anchors.py` 存在且本轮独立实跑 **28 passed, exit 0**（全部用例可运行）；`git show 27509a2 --stat` 核实 `check-gate.py` 确未被改动，决定与落地一致 (bdd-22-check-gate-branch-decision.md, shared-p6-command-output.log)

**Summary**: PASS 23 / FAIL 0（共 23 条 BDD：BDD-1~22 + BDD-15b）

## 2. 验收过程中的观察（不改变上述判定）

以下两点在逐条核对时被记录，均**不构成 FAIL**，理由一并写明，供 P7 一致性检查与后续任务参考：

1. **BDD-13 第 3 点括注"互相引用不重复定义"的字面形式未落地**。新增「命令超时兜底」段与既有「写脚本与跑脚本分离」节之间**未互加显式跳转链接**。判定不 FAIL 的依据：① 该点的**规范性要求**（非超时报错同样记录后返回主 Agent、不允许 subagent 自行深入诊断）已逐字落地；② 括注的实质约束"不冲突"成立——两节约束主体不同（新增段约束 subagent 跑 bash 命令，既有节约束主 Agent 跑脚本时可做最小修复），无规则冲突；③ "不重复定义"成立——新增段未复制"最小修复 vs 重写界限"判据；④ 对比 BDD-13 第 5 点用"**须**与…建立**显式的**文档内引用区分"的强表述且已落地（四层分层表），第 3 点的括注属兼容性说明而非独立的引用建设要求。
2. **P5 的锚点测试只覆盖存在性，不覆盖语义**。`test_protocol_mechanism_anchors.py` 是 28 条关键词 `in` 断言，无法拦截"关键词在但语义写错"的回归（该取舍已在 SELF-GATE 语义对齐审查 A4 项记为 NEEDS_HUMAN_REVIEW 并附 `[HUMAN_CONFIRMED]` 裁决，属 P2 已论证并经评审通过的范围收窄）。本轮 P6 的逐条语义核对与 `P6-evidence/` 下的 Then 逐项对照记录构成该缺口的一次性人工补位，但**不是持续性回归拦截**——若后续任务改写这些协议节，锚点测试仍只保证关键词不被删。

## 3. 与 P5 结果的关系

P5-test-results/unit.md 记录的 909 passed / 2 skipped / 0 failed、consistency `--strict` 0 ERROR、count-tests 911、shellcheck 0 issue，在本轮作为"本次协议改动未破坏既有行为"的**旁证**引用；其中锚点测试与 consistency 两条已由本轮独立重跑复核（结果一致）。全量 pytest 与 count-tests.sh 未在本轮重跑（P6 验收对象是协议文本语义，不是测试套件），P5 结论按 P6 dispatch-context 约束 6 仅作旁证，不覆盖任何一条 BDD 的语义验证。
