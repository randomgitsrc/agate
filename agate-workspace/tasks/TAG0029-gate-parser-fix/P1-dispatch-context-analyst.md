---
phase: P1
generated_by: 主 Agent
task_id: TAG0029
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 `agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`——把 P0-brief 的"gate 命令解析器修复批（DEBT0027 + DEBT0023 + RM-AG0056）"转化为需求基线：需求复述 + 隐含需求识别 + BDD 验收条件（Given/When/Then，每条可二值判定）+ 同类扫描结论 + P0-brief 时效性质疑结论 + 待确认清单 + 裁剪说明 + 能力需求声明。

### 约束
- 本任务是 **Agateon 协议自身改造**（dogfooding）：改造对象是 worktree 的 `agate/`（gate 解析器 + check-tdd-red judge 分支 + 平台假设扫描器 + P2 卡 gate_commands 节），`~/.agate` 是稳定版开发工具（禁止改动）。P1 产出属于需求层，不写实现方案。
- **三个缺口（P0-brief 已锁定，范围不可自行扩大；若分析发现需超出范围，先停下报告主 Agent）**：
  1. **DEBT0027（high，假绿灯——验收真实性风险）**：`agate-read-gate-commands.py` 值清洗 `strip(chr(34)).strip(chr(39))` 不剥离值内 `# 注释` 与残留引号（值不以引号结尾时只剥开头引号）；消费方 `bash -c` 执行 unterminated quote 语法错误（exit 2）；`check-tdd-red.py` 的 `judge_result` 对"命令串本身语法错误致 exit 2"无显式分支，落到末尾 red-light exit 0（L156-157）——测试根本没跑却被当红灯证据放行。要求：解析器输出纯命令或报解析错误；judge 仅在测试运行器正常退出时才判定红灯可推进。
  2. **DEBT0023（low，P3* 键静默收集）**：收集侧 `key.startswith("P3")`（L60）把所有 P3* 非元键收集为 TDD 测试命令执行；`is_gate_meta_key`（`agate_common.py` L79-87）仅精确匹配 `_formatter`/`_timeout_seconds` 后缀，P3_xxx 不被豁免。TAG0026 靠"禁用 P3_xxx 键"约定规避，协议层无机械防护。要求：P3 精确键 + 白名单后缀收紧或扩展元键约定 + P2 卡 gate_commands 节禁止声明 + 单测锁定收集行为。
  3. **RM-AG0056（平台假设扫描器 fixture 数据面误伤 + 未进常驻面）**：R2 规则（`check-platform-assumptions.py` L39）静态扫描无法区分"测试代码里的命令调用"（应禁裸 python3）与"fixture 模拟平台日志的数据面内容"（command 字段模拟真实日志本应含 `python3 -m pytest`）；TAG0028 周期 cmdstream fixture 17 处裸 python3 破坏 TAG0011 bdd-8「tests 树 0 命中」，P5 全量红灯回 P4 fix3 才闭环；且扫描器不在 P3/P4 gate_commands 常驻面，回归到 P5 全量才暴露。要求：fixture 目录/文件声明豁免（禁止"含 fixture 字样就跳过"的宽匹配，须绑定目录声明）+ 纳入 P3/P4 gate_commands 常驻面 + fixture 恢复真实日志形态。
- **BDD 至少覆盖**：解析器对带行内注释的 gate_commands 值输出纯命令且 `bash -c` 无 unterminated quote（DEBT0027 closure ①）；check-tdd-red 对语法错误类 exit 判 exit 1 不再误判红灯（closure ②）；read-gate-commands P3* 键收集行为锁定（DEBT0023 closure）；R2 扫描器对 fixture 数据面豁免且代码面仍拦截（RM-AG0056 closure）。每条 BDD 可二值判定，不绑定实现细节。
- **同类扫描（P1 卡强制节，结论必须写进 P1 正文）**：对关键符号 `strip(chr(34))` / `is_gate_meta_key` / `startswith("P3")` / R2 正则扫全仓，命中清单逐条判定"本次处理 / 本次不处理 + 理由"。主 Agent 已初扫（见客观查证信息），你须独立复核并做实最终清单。
- **frontmatter 机器字段**：`task_id: TAG0029` / `trace_id: TAG0029-P1-20260903`（日期以你执行日为准）/ `agent: analyst` / `parent: P0-brief.md` / `status: draft`；`risk_level`（建议 high——DEBT0027 是验收真实性风险，你按实际自判）；`phases` 全量 `[P1, P2, P3, P4, P5, P6, P7, P8]`（新 CHECK/扫描面上线须过 P7 一致性，P7 不可裁；如主张裁剪某阶段须写理由）；`packages` 按实际改动文件对应声明（如 gate-parser / tdd-judge / platform-scanner / protocol-docs，你核实后定）；`domains: [backend]`（纯脚本/协议层，预期无 frontend——你核实后声明，若含 frontend 则须补视觉能力条目与 UX BDD）；`judge:` 启用声明写在 `.state.yaml`（由主 Agent 落盘，你在需求正文提醒即可，不要直接改 `.state.yaml`）。
- **P0-brief 时效性质疑**：主 Agent 已核对（P0-brief 与交接单同日立项；三处缺陷模式在 worktree 现状中仍全部命中，无漂移）。你按 analyst.md 要求独立质疑一次，并在 P1-requirements.md 写"已核对 P0-brief 时效性，无漂移"（或按实际标记 `[P0_STALE: 具体漂移点]`）。
- 无待确认项时写 `[NO_NEED_CONFIRM]`（行首声明）。拿不准方向用 `[NEED_CONFIRM]`（阻塞）或 `[SUGGEST: 推荐 X，理由 Y]`（非阻塞倾向）。
- capability_requirements 三态判断：本任务能力预期均可用（bash/python3/pyyaml/pytest 环境齐全），你按判断树核实；环境问题走 `verification_env` 声明，不标 `supplementable`。
- 返回前先跑 `python3 agate/scripts/check-frontmatter.py` 自检你写的文件（worktree 路径执行），非 0 先修正再返回。
</dispatch_guide>

### 上游关联
- P0-brief 已完成（四字段齐全，主 Agent 已做时效性核验：无漂移），`.state.yaml` phase=P0，P1 首次派发。
- 无上一阶段 subagent 摘要（P0 由主 Agent 亲自写）。

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
4. **隐含扩展同样要授权**（TAG0025 教训）：P3/P4 的实现细节若事实上扩展了 P1 验收标准的范围（新增豁免条件、放宽/收紧某条 BDD 的判定边界等），即使当下未产生"矛盾"，也视为需要`[BASELINE_CHANGE]` 授权的情形——授权内容必须回写 P1-requirements.md 正文，不得只存在于下游阶段的 dispatch-context 口头引用中
<!-- AGATE_CARD_END -->

### 输入文件
- `agate-workspace/tasks/TAG0029-gate-parser-fix/P0-brief.md`（任务简报与风险声明——**P1 主要输入**）
- `HANDOFF-TAG0029.md`（worktree 根：双工作区纪律 + 范围/约束/风险——必读 §2/§3/§5/§7）
- `AGENTS.md`（项目约定：双工作区纪律、改脚本工作流、工具纪律——必读）
- `agate/scripts/agate-read-gate-commands.py`（改造对象 ①，70 行——精读 L56-67）
- `agate/scripts/check-tdd-red.py`（改造对象 ②，`judge_result` L87-157——精读）
- `agate/scripts/check-platform-assumptions.py`（改造对象 ③，R2 规则 L39 周边——按需读）
- `agate/scripts/agate_common.py`（`is_gate_meta_key` L79-87 共享判据——按需读）
- `agate-workspace/debt/` 下 DEBT0023 / DEBT0027 条目（closure_criteria 来源——必读）
- `agate-workspace/roadmap/` 中 RM-AG0056 关联行（scheduled，2026-09-03 立项——按需读）

<objective_info>
- worktree 状态：分支 `feat/TAG0029-gate-parser-fix`；hook 指向 `~/.agate` 稳定版；consistency 基线 0 ERROR（--strict-errors-only，已验）；工作目录即 worktree 根。
- 已核实查证（主 Agent 实测，你须独立复核）：
  - 值清洗同模式 5 处：`agate-read-gate-commands.py` L57/L66、`agate-read-p5-commands.py` L30/L37、`agate-gate-missing-cmds.py` L24——同类扫描时逐条判定本次处理/不处理。
  - P3 收集 `startswith("P3")`：仅 `agate-read-gate-commands.py` L60 一处。
  - `is_gate_meta_key` 消费方：`check-gate.py`（对账语义）/ `agate-read-p5-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-gate-commands.py` / `agate-gate-p5-count.py` + `check-structure-consistency.py` S-4 校验（`rules/` YAML 声明 vs 脚本判据一致；改判据须同步 YAML，否则 consistency 红）。
  - R2 正则：`check-platform-assumptions.py` L39 全仓唯一。
  - `judge_result` 现状：exit 2 无显式分支 → 落末尾 exit 0（L156-157）；A 类 exit 1 分支覆盖 Traceback/SyntaxError/exit>=120（L110-116, L152-154）——那是"测试运行器正常退出且报告错误"的路径，与"命令串本身语法错误致 bash exit 2"不同，需求须区分两者。
  - `.state.yaml` 现状：仅 task_id/phase/status 三行，无 judge 块——主 Agent 将在你返回后补 `judge.enabled: true`（TAG0028 惯例格式）。
  - 环境：python3.12 / pyyaml / pytest 9 / ruff（`~/.venvs/agate-dev/bin/ruff`）/ shellcheck 0.9 齐全；pytest 分片 `unit/regression/integration` + `-n auto`；consistency 必须用 worktree 自己的 `agate/scripts/check-protocol-consistency.py`；编排/派发类工具用 `~/.agate/scripts/` 稳定版。
- 任务编号 TAG0029；任务目录 `agate-workspace/tasks/TAG0029-gate-parser-fix/`；并行提示：TAG0030/TAG0031 三路并行，文件域不重叠——roadmap/active-tasks/debt 共享面只改自己关联行，不整表重排。
- 注：该文件禁止包含 verdict 预判（provenance 审计要求）。
</objective_info>
