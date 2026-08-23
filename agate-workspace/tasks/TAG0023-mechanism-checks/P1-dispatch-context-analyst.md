# P1-dispatch-context-analyst — TAG0023 机制校验补强批

> 派发对象：analyst（P1 需求基线）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`（完整目录名：TAG0023-mechanism-checks）

## 目标

产出 `P1-requirements.md`（需求基线），把 P0-brief 的 4 个 issue（RM-AG0042/RM-AG0043/RM-AG0044/RM-AG0045）转成可二值判定的 BDD 验收条件，并完成：
- P0-brief 时效性质疑（不默认立项前提仍成立；立项日 2026-08-23，今日 2026-08-24）
- 强制同类扫描（3 组 grep，见下，来自 HANDOFF-TAG0023.md §5「强制要求」）
- 需求复述 / 隐含需求识别 / 裁剪说明 / 能力需求声明（按 P1 卡片 + analyst 角色文件规格）
- frontmatter 机器字段（risk_level / ceremony / phases / packages / domains）
- `.state.yaml` 已由主 Agent 写入 `judge.enabled: true`（本任务 P1 created ≥ judge_required_since 2026-08-22，机制强制），P1 需求无需重复声明该字段本身，可在隐含需求中提及 P6 走 P6.5 judge 复核

## 约束（硬约束，违反即打回）

1. **BDD 按子项分组**（P0-brief 4 个 issue 各自验收锚）：
   - RM-AG0042（retries 强制记录）：门槛失败事件（评审 rejected / P5→P4 回退 / 子代理空返回重派）与 `.state.yaml` 的 `retries` 字段必须对应——gate 校验"失败事件存在而 retries 为空"→ 阻断或高优 WARNING；P1/P2 卡须明确"评审被拒必须写 retries"。**先定义可机器判定的事件源**（P0-brief known_risks 已列：评审 status=rejected / P5→P4 回退证据 / subagent 空返回记录），本阶段只需把事件源判定规则转成 BDD 的 Given 前提，具体判定实现留 P2。验收锚=新任务评审 rejected 后 retries 必有对应条目（对应性校验拦截空记录）。
   - RM-AG0043（roadmap 回写 done 校验）：P8 gate 增加校验——按 task_id 反查 roadmap 关联 RM 条目，状态必须为 done；同时补记 RM-AG0032（独立 Judge，v0.59.0 已发布、PR #184 已合并）→ done（历史数据修正，独立 BDD）。验收锚=新任务 P8 后 roadmap RM 自动 done；RM-AG0032 手工补记验证。
   - RM-AG0044（环境敏感测试集中治理）：先复现定位 test_bdd_14（check-debt.py --retreat-coverage）CI flaky 根因（git short SHA / runner 环境敏感点），再定 BDD（P1 卡片明确"P1 需先复现定位根因再定 BDD，不盲改"）；建立环境敏感测试判定标准 + 集中清单 + CI flaky 自动重跑机制。验收锚=test_bdd_14 连续 5 次 CI 稳定 + 集中清单落盘。**若本阶段无法在 P1 内完成"复现定位"（需要多次 CI 触发观测），可交付"复现定位计划 + 已知证据基线"作为 BDD 前置锚，具体根因结论留到 P2/P4**，不得跳过复现直接假设根因。
   - RM-AG0045（声明写时校验）：P1/P2 声明（ceremony / coupling_checklist / 跳过风险 / phases 等）写文件时即由 schema 校验，消灭 commit 时格式折返（TAG0019 实证：coupling_checklist 流式/半角冒号/源码数 6>5 均在 commit 才暴露）。修复面=声明 schema 校验接入写路径（生成器/编辑器/formatter 层）+ 错误信息给具体行+修复提示。验收锚=声明格式错误写入即报、commit 折返归零；关联 RM-0022（schema 基建）/RM-0038（check-gate YAML 迁移，TAG0021/22 已完成的 M0-M3）。
2. **强制同类扫描**（HANDOFF-TAG0023.md §5「强制要求」，扫描结论必须写进 P1 正文）：
   - grep retries 全部消费点（check-state-transition.py / state-machine.md / check-gate.py / agate-state-get.py / agate-retreat-state.py / agate-state-yaml-check.py 等）——本阶段已初步 grep 命中 9 个文件（见下「客观查证信息」），analyst 需核实清单完整性并逐条判定
   - grep roadmap 回写消费点（check-gate.py P8 分支 / state-machine.md / check-retrospective.py）——初步核实 check-gate.py 当前**无**任何 roadmap 校验（仅 1 处不相关注释命中"roadmap 补 gap"字样），需 analyst 确认此结论
   - grep 环境敏感测试已知清单（test_bdd_7 / test_bdd_25 / test_bdd_14 + LIMITATIONS.md 的 known-failures 登记机制，见客观查证信息）
   每条命中标"本次处理 / 本次不处理 + 理由"；结论"已确认只此一处"也要显式写出。
3. **环境（客观查证）**：Linux；`/tmp` 只读——pytest 必须 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`；ruff 在 `~/.venvs/agate-dev/bin/ruff`（0.16.4 对齐 CI）；测试平台无关原则不得破坏。
4. **双工作区纪律**：本任务改造对象 = worktree `agate/`（`/home/kity/oclab/agate/.worktrees/agate-TAG0023/agate/`）；主 checkout `/home/kity/oclab/agate` 与稳定版 `~/.agate` **禁止改动**（只读消费角色/卡片文件可）。本阶段（P1）只产出需求文件，不改任何协议文件。
5. **SELF-GATE**：本任务改动面（check-gate.py / check-state-transition.py / P1/P2/P8 卡 / check-debt.py / CI 配置 / 测试）触发 self-gate——后续 commit message 须含 `self-gate-review:` 或 `self-gate-skip:` 理由（P1 需求里可把 self-gate review 列为隐含需求/阶段要求）。
6. **三子项同簇互扰**：RM-0042/RM-0043 都可能触碰 check-gate.py 的不同分支（P1/P2 判定 vs P8 判定）——P1 需求需在「同类扫描/隐含需求」中标注两者改动面是否重叠、是否需要分批 commit（HANDOFF §7 已提示此风险）。
7. 需求基线保护：P1 之后不改 BDD 语义；本任务验收锚以 P0-brief issues 逐条为准，不要自行增删验收标准。

## 上游关联

- `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P0-brief.md`（本阶段主要输入：task/issues/known_risks/env_constraints）
- `{project_root}/HANDOFF-TAG0023.md`（交接单：范围/纪律/验收锚/验证命令/风险止损）
- `/home/kity/oclab/dsw-workspace/agate-research/retrospective-tag0019-21.md`（**必读**：TAG0019-21 复盘独立评审，2026-08-23 approved，本任务 4 个机制缺口的证据来源）
- 参照：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-requirements.md`（同仓库同类"机制修复批"任务的需求格式范本，含 judge/ceremony/同类扫描写法）

## 输入文件（逐一读，每读完一个追加 progress）

1. `{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P0-brief.md`
2. `{project_root}/HANDOFF-TAG0023.md`
3. `/home/kity/oclab/dsw-workspace/agate-research/retrospective-tag0019-21.md`
4. `{agate_root}/phase-cards/P1-requirements.md`（本阶段卡片，含 gate 规则）
5. `{agate_root}/assets/execution-roles/analyst.md`（角色定义）
6. 按需：`{AGATE_WORKSPACE}/tasks/TAG0022-confirmed-problems/P1-requirements.md`（格式参照）
7. 按需：`agate/scripts/check-state-transition.py`（retries_over 机制现状，L146-154）、`agate/scripts/check-gate.py`（P8 分支现状、judge 校验写法范例 L647-662）

## 客观查证信息（可复算的事实基线，供 BDD 锚定，主 Agent 已初步核实）

- retries 消费点初步 grep 命中 9 个文件：`agate-retreat-state.py` / `check-retrospective.py` / `agate-state-get.py`（`retries_over` 操作）/ `agate-state-yaml-check.py`（格式校验，非对应性校验）/ `check-state-transition.py`（L146-154，MAX_RETRY→PAUSED 判定，但无"失败事件↔retries 记录"对应性检查）/ `WORKFLOW.md` / `check-protocol-consistency.py`
- roadmap 回写：`check-gate.py` 全文 grep "roadmap" 仅 1 处命中且与 P8 无关（P4 review 门禁注释），确认 P8 gate 当前无任何 roadmap done 校验
- RM-AG0032 现状：roadmap.md 第 31 行仍为 `scheduled`（非 done），与 P0-brief 描述一致（v0.59.0 已发布但记录未回写）
- 环境敏感测试已知清单：`test_bdd_7` / `test_bdd_25`（RM-AG0041，TAG0022 已处理，basetemp 类根因）、`test_bdd_14`（RM-AG0044 本次新例，check-debt.py --retreat-coverage，PR #188 同 commit 双 CI run 一过一挂）；`LIMITATIONS.md` L45 提到 `known-failures.md` 登记机制作为既有基础设施，但未见"环境敏感测试"专门分类清单
- judge：`.state.yaml` 已由主 Agent 写入 `judge.enabled: true`（`rules/dispatch.yaml` `judge_required_since: 2026-08-22`，本任务 created 2026-08-24 ≥ cutoff，强制适用）

## 验证命令（P1 阶段不需要跑测试，但 BDD 验收锚须与这些命令可判定对齐）

```bash
python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only   # 用 worktree 自己的
~/.venvs/agate-dev/bin/ruff check agate/                                    # All checks passed
bash agate/tests/scripts/count-tests.sh                                     # 用例数只增不减
```

## 产出

`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/P1-requirements.md`

要求：
- BDD ≥1 条，`#### BDD-NN:` 连续编号，Given/When/Then 可二值判定；按 4 子项分组（含 RM-AG0032 历史补记独立 BDD）
- frontmatter 机器字段齐全（risk_level / ceremony / phases / packages / domains）
- 含「同类扫描结论」节（3 组 grep 命中数 + 文件清单 + 逐条判定）
- 含 P0-brief 时效性质疑结论（无漂移写"已核对无漂移"，有漂移写 `[P0_STALE: 具体漂移点]`）
- 无未决 `[NEED_CONFIRM]`（无则写 `[NO_NEED_CONFIRM]`）；有方向但求确认用 `[SUGGEST: ...]`
- 不含解决方案设计（P2 才做）

## 门槛（什么算完成）

- P1-requirements.md 存在且非空
- BDD ≥1 条且编号连续、可二值判定、按子项分组覆盖 4 个 issue 验收锚
- 同类扫描 3 组结论落盘（空白不算做过）
- frontmatter 字段齐全、无 NEED_CONFIRM

## 返回给我

只返回两行：① 产出文件路径；② 一句话摘要（≤30 字）。绝不返回文件全文。

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.py P1（exit 2，主 Agent 自判）
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 复杂需求编排（模式 4，条件触发）

需求复杂（多来源 / 多模块 / 无法预先拆清范围）时，P1 可先派**侦察 subagent**（模式 4 先理解后拆，见 dispatch-protocol「派发编排机制」）读全貌后再拆需求：

1. 侦察 subagent 读 P0-brief + 相关上下文，产出拆分方案（拆成哪些子需求、各子需求的输入/产出/依赖）
2. 按方案派 analyst（并行或串行）分别产出需求基线
3. 合并时定义**合并语义**（在侦察产出中声明，P7 一致性检查依赖）：
   - **BDD 全局编号**：各子需求承接的 BDD 编号全局唯一（`#### BDD-NN:`），不允许各子需求各自从 1 编号
   - **包归属去重**：每个 BDD 明确归属唯一包，跨包的共享件单独列出，不允许两个子需求各写一份

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `ceremony:` 声明（thin / standard / full）→ 仪式深度档位（可选，缺省 standard，fail-closed：不声明或声明要素不满足一律按 standard 处理，不做薄化）
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `judge:` 启用声明（RM-AG0039 强制）：机制后新任务（P1 `created` ≥ `judge_required_since`，见 `agate/rules/dispatch.yaml`）P1 初始化须在 `.state.yaml` 写 `judge.enabled: true`——check-gate P1 机械校验（缺失/未启用 → exit 1）；历史任务（created < 截止或未声明）缺块 → 跳过
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
ceremony: standard          # thin / standard / full，可选；缺省 standard（fail-closed）
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── RM-AG0039 judge 启用声明（写在 .state.yaml，非 P1 frontmatter）──
# 机制后新任务（P1 created ≥ judge_required_since，rules/dispatch.yaml "2026-08-22"）必须
# 在 .state.yaml 写 judge.enabled: true——check-gate P1 机械校验，缺失/未启用 → exit 1
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── TAG0007 项目阶段声明（可选，缺省 = established，向后兼容）──
# project_phase: bootstrap   # bootstrap（0→1 新项目）/ established（既有项目，缺省值）；
#                             # bootstrap 时 P2 architect 需额外产出 P2-skeleton.md（骨架声明）
# ── TAG0006 UI/UX 渲染形态声明（可选，presence 语义：缺失 = 常规布局型默认，不红基线）──
# ui_render_shape: render_component   # str，规范形态值：layout（布局型）/ render_component
#                                     # （渲染组件型，仅举例 OpenGL/WebGL/Canvas/图表/模型/特效/
#                                     #  地图/数字地球）/ temporal_effects（时序特效型）；开放集合可扩
# ui_ux_dimensions: [渲染正确性, 动效时序]  # list，从 UX 分类框架选适用维度；渲染组件/时序特效
#                                     # 类形态必填，常规布局型可省略
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

**UX 类别 BDD 与分类框架（domains 含 frontend 时必做）**：frontend 任务的 P1 必须含至少一条
UX 类别 BDD，并按实际 UI/渲染形态声明 `ui_render_shape` + 从 **UX 分类框架**（布局结构/
渲染正确性/交互行为/动效时序/视觉呈现等示例性开放集合）选 `ui_ux_dimensions` 维度，类别写入
BDD 标题后缀（如 `#### BDD-3: 渲染正确性：...`）。判据必须可量化（渲染正确性 → 渲染结果对比 +
diff 阈值或输出断言；时序 → 帧/时间戳对齐；动效 → 过渡/动画关键帧与结束状态断言；手势交互 →
动作输入的坐标/参数量化），禁主观词。缺失形态声明/维度选择/UX BDD → requirements-review 打回，
P1 gate 在"声明了形态但维度为空"或"维度不在分类框架且未在 BDD 标题声明"时 exit 1。

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## ceremony fail-closed 声明 checklist（TAG0019，BDD-7/8/9）

`ceremony:` 声明仪式深度档位（thin / standard / full），缺省 standard（fail-closed——不声明或声明要素不满足一律按 standard 处理）。声明 **thin**（薄仪式）时，P1 必须连同以下四要素一起声明，缺一 → check-routing exit 1，档位回退 standard：

1. **申请**：`ceremony: thin` 显式声明
2. **逐信号 checklist**：`coupling_checklist: [...]` 流式声明（判据 `^coupling_checklist:\s*\[`，复用 check-pruning）
3. **跳过风险评估**：`跳过风险:` 声明（复用 check-pruning 判据）
4. **P5/P6 保留**：`phases` 含 P5 与 P6（薄化仪式不薄化验证，P5/P6 由 check-routing / check-pruning 双闸兜底）

不声明（存量/新任务缺 ceremony 字段）→ standard，不拦截。`ceremony: full` 的任务 `phases` 必须含 P7（P7 不可裁，缺失由 requirements-review 审声明拦截，BDD-14）。

### M3 验收锚度量协议（BDD-12，机制文档供提取）

thin 档跳过 LLM 评审的 M3 验收锚四要素：

1. **评审轮数**指标：任务在 P2/P4 阶段派发的 LLM 评审 subagent 轮数（含重试轮）
2. **真实发现数**指标：评审产出中被采纳或阻止了真实问题的条数（排除非阻塞建议、排除机械检查可抓项）
3. **TAG0018 基线值**：4 场 LLM 评审 ≈0 净收益（17 条非阻塞 + 1 条真实发现且机械检查可抓）
4. **不达标决策规则**：「LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard」

## 同类扫描（强制节）

需求基线必须含一次**同类扫描**结论——被报告的那一处几乎从来不是唯一的一处。P0 卡片的「同类/影响面预判」给出粗粒度量级，P1 在此基础上把清单做实：

1. **扫描动作**：对问题涉及的关键符号（函数名、字段名、配置键、协议节标题、错误文案）用 grep/rg 扫全仓，记录**命中数量 + 文件清单**
2. **逐条判定**：每个命中标"本次处理 / 本次不处理 + 理由"。本次不处理的同类实例要么进 roadmap，要么写清为何不构成同一问题
3. **回归拦截**：若同类问题未来还会新增（不是一次性修完的存量），需求里要声明拦截手段（新增测试 / gate 脚本 / 文档约定），并转成对应 BDD
4. **结论落盘**：扫描结论写进 P1-requirements.md 正文（不是只写在 progress 里）；即使结论是"已确认只此一处"也要显式写出，空白不算做过

同类扫描缺失 → requirements-review 打回（"只修被报告的那一处"是 agate 反复复发的反模式）。P2 的「影响面梳理」在本节结论上继续做候选方案级的影响域分析，三处（P0 预判 / P1 同类扫描 / P2 影响面梳理）同源、逐级细化，不重复劳动。

## verification_env vs supplementable 边界判断树

`capability_requirements` 三态（available / supplementable / GAP）和 `verification_env`（运行环境声明）经常被混用——TAG0009 的 11.7 小时就是把一个环境问题错标成 `supplementable` 导致的。P1 声明时按下面的判断树走：

```
先问：缺的是能力还是环境？
├─ 缺的是「agent 侧的能力」（看不见图 / 不会用某工具 / 没有某技能）
│   └─ 走 capability_requirements 三态：
│      ├─ 当前就有 ................................. available
│      ├─ 当前没有，但能通过派发子角色 / 注入 skill / 换工具补上 ... supplementable
│      │   （必须在需求里写清补充方式，否则等同 GAP）
│      └─ 当前没有且补不上 ......................... GAP（阻塞，PAUSED 交人工）
└─ 缺的是「运行环境」（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）
    └─ 走 verification_env 声明（不是 supplementable）：
       ├─ 环境可由主 Agent 用标准操作准备好 → P1 声明 verification_env，
       │   由主 Agent 按 dispatch-protocol.md「环境准备职责边界」统一准备
       └─ 环境本质不可得（权限/凭据/平台原生不支持）→ 这是不可重试类，
           按 dispatch-protocol.md「verification_env 失败处理协议」立即升级人工
```

**判别口诀**：换个更强的模型/角色就能做 → 能力问题（supplementable）；换谁来做都得先把服务起起来 → 环境问题（verification_env）。**把环境问题标成 `supplementable` 属于机制误用**，不算"环境故障"，不消耗验证轮次预算，应立即改正声明方式。

**环境验证轮次预算占位声明位**：声明了 `verification_env` 的任务，P1 需求里留一行轮次预算占位（默认止损轮次 = 2 轮，与阶段 `retries[Pn]` 独立计数），供 P5/P6 派发时由主 Agent 在 dispatch-context 中接续记录"当前第几轮 + 历次已排除假设"。数值与完整规则的权威定义在 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重写：

```yaml
verification_env: "debug server http://127.0.0.1:3001 + tests/fixtures/test.db"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录"
```

## P0-brief 时效性质疑

analyst 拿到 P0-brief 后不默认它仍然成立——立项与实际启动之间可能已经漂移（跨会话恢复、任务搁置后重启、从 PAUSED 恢复）。P1 阶段必须做一次时效性质疑，判据（严重 3 条 / 轻微 2 条）的权威定义见 P0 卡片「P0-brief 时效性自检（漂移判据）」，本节只定标记规则与处理方式：

**标记格式**（行首声明，一个漂移点一行，必须写出**具体漂移点**，不允许只写标记裸词）：

```
[P0_STALE: executor_env 声明的 CI 镜像已下线，当前实际跑在 ubuntu-24.04]
[P0_STALE: task 描述的 .sh 路线已全量 Python 化，目标方案本身不再成立]
```

**阻塞 / 记录二选一**（按漂移严重程度分流，不允许"既不阻塞也不记录"地含糊推进）：

| 漂移程度 | 处理 | 落盘 |
|---------|------|------|
| **严重**（命中 P0 卡判据 1-3 任一条） | **阻塞**：停止 P1，回 P0 重新立项 / 重做可行性分析 | P1-requirements.md 写 `[P0_STALE: 具体漂移点]` + 说明为何判定严重；主 Agent 按 PAUSED 或回 P0 流程处理 |
| **轻微**（不命中判据 1-3） | **记录**：更新 P0-brief 对应字段后继续 P1，不阻塞 | P1-requirements.md 写 `[P0_STALE: 具体漂移点]` + 已更新哪个字段 |
| 无间隔 / 已核对无漂移 | 继续 | 写一行"已核对 P0-brief 时效性，无漂移"，空白不算做过 |

## gate 规则

check-gate.py P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] 含「同类扫描」结论（命中清单 + 逐条处理判定，"只此一处"也要写出）
- [ ] P0-brief 时效性已质疑：无漂移则记录已核对；有漂移则含 `[P0_STALE: 具体漂移点]` 且已按阻塞/记录二选一处理
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工。**frontend 任务
   漏声明 vision 视觉能力条目（need 含 visual/vision）→ P1 gate exit 1 硬拦**（check-gate.py
   `_gate_p1_vision_capability`）；声明形态但漏选维度 / 形态声明与 UI/渲染形态不符 →
   同样 exit 1
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
<!-- AGATE_CARD_END -->
