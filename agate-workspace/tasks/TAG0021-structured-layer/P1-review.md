---
phase: P1
task_id: TAG0021-structured-layer
type: review
parent: P1-requirements.md
trace_id: TAG0021-P1-20260822
status: approved
created: 2026-08-22
agent: requirements-review
---

# P1 需求基线评审 — TAG0021 协议结构化层（RM-AG0022）

## 评审范围与方法

- **评审对象**：`P1-requirements.md`（279 行，16 条 BDD，按 M0/M1/M2/M3 分组 + 跨里程碑 2 条）
- **输入文件**：P1-requirements.md（主对象）/ P0-brief.md / HANDOFF-TAG0021.md / design-structured-layer.md / phase-cards/P1-requirements.md（随 dispatch-context 注入）
- **独立评审声明**：本评审只依据客观标准与评审对象文件内容作判断；不采信任何"实现者自述"。`[PROD_NOT_TOUCHED]`：全程只读协议文件，唯一写操作是本文件与 progress 文件，均在 worktree `agate-workspace/` 内。
- **证据核验方式**：BDD 锚点用 grep 实扫（16 处 `#### BDD-`）；NEED_CONFIRM/GAP/P0_STALE 标记用 grep 实扫；git 证据用 `git status` + `git diff --cached` 实查（见「审声明」节）。

## BDD 评审

**总体判定：16 条全部通过。** 编号 `BDD-1`..`BDD-16` 连续无跳号、无重复（grep 实扫 16 处锚点）；格式全部为 `#### BDD-NN:`；每条仅一条 Given/When/Then 三元组，无中间态（无"部分通过/调整"类措辞），判据全部为"运行命令后观察退出码/输出/文件"的客观二值判定。按 M0/M1/M2/M3 分组（§6.1-6.4 + 标题后缀 `(M0)`-`(M3)`），跨里程碑 2 条列 §6.5。逐条：

- **BDD-1**: 通过 — 数据✓（rules/ 目录 schema 合法性，数据格式可机器校验）边界✓（非法字段/错误枚举/错误类型 → 非 0）前端 N/A 多端 N/A 兼容✗
- **BDD-2**: 通过 — 数据✓（S-1/S-2 双向一致，YAML↔md 数据面对账）兼容✓（与既有 WORKFLOW 总览表共存校验）边界✗
- **BDD-3**: 通过 — 边界✓（S-6 引用完整性缺失引用、S-5 枚举违规）兼容✓（引用既有角色/模板/脚本路径须真实存在）
- **BDD-4**: 通过 — 兼容✓（存量行为不变：pytest 全绿 / count-tests ≥ 立项基线 / consistency 0 ERROR，M0 纯增量不破坏）
- **BDD-5**: 通过 — 数据✓（phases.yaml ↔ phase-cards/P2-design.md ↔ check-gate.py P2 判定三方一致）兼容✓（与既有卡片文本与既有脚本判定并存）
- **BDD-6**: 通过 — 边界✓（对账模式差异 → stderr WARNING + 计数，退出码保持原判定 0/2 不变）兼容✓（M1 告警不阻断语义，与 BDD-8/BDD-10 的 M2 阻断升级是分阶段设计，无矛盾）
- **BDD-7**: 通过 — 数据✓（脚本数 ≥ 3 且覆盖 gate_commands 块 / P1 裁剪字段 / P2 四字段三类解析点，可计数判定）
- **BDD-8**: 通过 — 迁移✓（对账清零为切换门槛；残留差异 → 禁止切换回退 M1，二值判定）
- **BDD-9**: 通过 — 数据✓（静态扫描已迁移解析点命中数为 0）边界✓（零命中判定无模糊）
- **BDD-10**: 通过 — 兼容✓（一致性 gate 提升为阻断并纳入 pre-commit + CI，三处均非 0 阻断）
- **BDD-11**: 通过 — 兼容✓（切换后全量回归：pytest 全绿 / count-tests 只增不减 / consistency 0 ERROR）
- **BDD-12**: 通过 — 数据✓（渲染产物 vs phases.yaml 声明一致；人为篡改 YAML → 非 0，S-3 强制）
- **BDD-13**: 通过 — 兼容✓（注入结果与渲染一致 + `~/.agate` 稳定版不被 worktree 未发布 YAML 污染，双工作区自举纪律可二值判定）
- **BDD-14**: 通过 — 兼容✓（渲染化后全量回归 + 结构一致性 0 漂移）
- **BDD-15**: 通过 — 兼容✓（count-tests 只增不减，回归拦截转 BDD，判据明确"≥ 立项基线且单调不减"）
- **BDD-16**: 通过 — 多端✓（测试平台无关：禁裸 python3 / 硬编码 PATH / `-L` 软链假设 / /tmp 路径；平台差异按分支断言或模拟覆盖；`check-platform-assumptions.py` 或人工审查双通道）

**跨条一致性**：无 Then 矛盾。M1 对账"告警不阻断"（BDD-6）与 M2"提升阻断"（BDD-10）由 BDD-8（对账清零后才切换）显式串接，阶段边界清晰。

## 隐含需求覆盖

§3 共 H1-H12，每条附"为什么必须"且多数转 BDD。按评审角色清单逐维度核：

- 数据维度：H1（YAML 必须配 JSON Schema + check-yaml-schema.py，转 BDD-1）覆盖 ✓
- 前端维度：任务 domains=[backend]，无 UI/视觉需求面；H10 显式声明"不适用" ✓（N/A 有声明，非遗漏）
- 多端/平台维度：H9（测试平台无关，转 BDD-16）覆盖 ✓
- 边界维度：H1 schema 枚举/类型、H7 fixture 兼容桥接（转 BDD-11）、H12 对账差异可观测出口（转 BDD-6/7）覆盖 ✓
- 兼容维度：H4/H5（README/AGENTS 目录图 + consistency 扫描面纳入新 YAML，防误报）、H3（UPGRADING 章节，M2 破坏性变更逐条列）、H2（新目录/新脚本进入 SELF-GATE 触发面，HANDOFF §5 硬约束）覆盖 ✓
- 迁移维度：H7（既有 pytest fixture 825 基线兼容）、H11（frontmatter 字段读取链随 M2 迁移）覆盖 ✓
- 隐含需求与 BDD 映射完整（H1→BDD-1、H6→BDD-13、H7→BDD-11、H8→BDD-15、H9→BDD-16、H12→BDD-6/7），无"隐含需求列了但不落 BDD"的悬空项。

## 同类扫描核验（评审要点 2）

三组扫描全部落盘在 §4 正文（非仅 progress），命中数量 + 文件清单 + 逐条判定 + 回归拦截声明齐备：

1. **扫描 1（4.1）grep 脚本对 markdown 的解析点**：统计 57 个 `.py`、29 个含正则解析、约 25 个对 md 内容做 grep 式解析（约 44%）；按解析对象分 A-F 六组，每组列脚本清单 + 「本次处理」（标 M0/M1/M2 归属）或「本次不处理 + 理由」（F 组：解析的是任务/状态数据而非协议规则，非摩擦源）。回归拦截声明：M2 起 S-4 + 静态扫描零命中（BDD-9）兜底，新脚本读协议规则必须先入 YAML ✓
2. **扫描 2（4.2）phase-cards 门槛/产出/派发字段**：统计 9 张卡 + 结构一致性说明；字段清单抽取出前置条件/派发角色/产出文件/gate 规则/retry 上限/卡片特有机器字段并标命中卡；逐条判定 5 类「本次处理」进数据面、叙事层「本次不处理」留 md（理由：YAML 只承载可判定规则，design §2 关键决策）。回归拦截：S-3 + S-2 双向强制（BDD-12）✓
3. **扫描 3（4.3）CHECK 编号空间**：统计活动编号 CHECK 1/2/3/4/6/7/8/9/10/11/12（11 个）、CHECK 5 已退役；逐条判定 S-1~S-6 独立前缀「本次处理」（决策 D1 不并入 CHECKS）、CHECK 5 退役位「本次不处理：不复活也不占用 + 理由（S 前缀已规避冲突，M0 只加不改）」。回归拦截：S 编号由 check-structure-consistency.py 内 CHECKS 列表自校验 ✓

三组扫描结论均写进 P1-requirements.md 正文（满足"结论落盘"要求）；"本次不处理"项均有显式理由，非空白跳过。**核验通过。**

## P0-brief 时效性核验（评审要点 3）

§2 已做时效性质疑：逐条对照 P0 卡三判据 —— task 目标方案成立（design §2/§4/§5 与 P0-brief 一致，worktree 已合并 TAG0019/TAG0020 与设计 §6 表述不冲突）/ executor_env 平台前提成立 / known_risks「已解决前提」无变化。

发现 1 处漂移并落盘 `[P0_STALE: ...]`（行 44）：P0-brief env_constraints.debug_env 声明"权限为 danger-full-access"，实际为 workspace-write 沙箱且 /tmp、ptmp 只读（dispatch-context 客观查证：pytest 须 `-p no:cacheprovider --basetemp=<可写目录>`）。Grep 实扫确认：标记含**具体漂移点**（非裸词），按**轻微漂移 → 记录不阻塞**处理，且已将测试命令权威声明移交 HANDOFF §4 + dispatch-context 客观查证（P0-brief 原文未就地改正，但 P1 基线内已显式覆盖其权威性，符合「记录」路径，不命中严重判据 1-3）。**核验通过。**

## frontmatter 机器字段核验（评审要点 4）

行 10-15 grep/read 实查：

- `risk_level: high` ✓（注释给出理由：改动面极大 + 工具链自举风险；与 P0-brief「改动面极大」一致）
- `ceremony: standard` ✓（显式声明缺省档位，fail-closed；未声明 thin → 无需 coupling_checklist/跳过风险四要素；standard 不触发 P7 绑定）
- `phases: [P1, P2, P3, P4, P5, P6, P7, P8]` ✓（全保留，理由见 §8）
- `packages: [agate]` ✓（协议本体单一版本单元，四改动面在 §5 展开）
- `domains: [backend]` ✓（纯协议/脚本/数据层，无 frontend/security）
- 身份字段 phase/task_id/type/parent/trace_id/status/created/agent 齐全 ✓

**核验通过。**

## NEED_CONFIRM 核验（评审要点 5）

Grep 实扫：

- 无任何未决 `[NEED_CONFIRM]`（行 78 的 `[NEED_CONFIRM]` 出现在扫描 1 D 组的解析对象清单中，是对被扫描标记协议的枚举描述，非本文件未决项）✓
- §7 显式声明 `[NO_NEED_CONFIRM]` ✓
- `[SUGGEST:]` 三项（决策 D1/D2/D3）均附理由与采纳条件（"主 Agent 无异议即采纳"），不阻塞推进 ✓
- 无 GAP 状态声明（§7 行 235 显式写出，三态明细见 §9）✓

**核验通过。**

## 裁剪说明核验（评审要点 6）

§8：`phases` 全保留 P1-P8，逐阶段给出保留理由（P2 不可裁 + risk_level=high → plan-eng-review 经 C8 强制；P3 可写失败测试 TDD 硬约束；P4 分批 commit；P5 每里程碑血糖；P6 逐条实跑 BDD-1..16 且无 UI 证据需求；P7 跨文件交叉核对必要；P8 版本 bump + UPGRADING + tag），另附不裁总述（改动面极大 + 工具链自举风险 → 每阶段 gate 是自举兜底闸）。无违规裁剪、无跳过阶段。**核验通过。**

## 能力自查核验（评审要点 7）

§9：`capability_requirements` 两条（text-analysis-scanning / protocol-editing），`status: available` 均给出 available 依据；显式写明"无 supplementable、无 GAP"。`domains=[backend]` 不含 frontend → 按 P1 卡视觉硬要求仅当含 frontend 时触发，本任务无需 vision 能力条目、无 `[CAPABILITY_GAP]`，判定正确。`verification_env` 不声明（无 debug server/数据库/外部服务，测试命令为主 Agent 标准操作可准备，仅需遵守 /tmp 只读 + 双工作区纪律）——环境约束处理正确，未误用 supplementable（判别口诀：环境问题不走三态）。**核验通过。**

## 审声明（risk_level / ceremony / phases vs 证据，TAG0019）

- 当前 git 证据（实查）：`git diff --cached --stat` 为空暂存；P1-requirements.md 等为 untracked，尚无 P1 commit——符合 P1 卡流程（review 通过后才 commit，评审时点无暂存 diff 属预期）。
- 以 P0-brief/HANDOFF 交付物清单 + 评审对象自身扫描统计为证据面：改动面 = 协议文档 + 57 个 `agate/scripts/*.py` + 9 张 phase-cards + 新增 `agate/rules/` 目录（M0-M3 分批）→ `risk_level: high` 与实际规模匹配 ✓；`ceremony: standard` 未声明 thin，无薄化诉求，与声明一致 ✓；`phases` 全保留与"工具链自举风险需每阶段 gate 兜底"自洽 ✓。声明与实际改动面无矛盾证据。
- `ceremony` 非 full → 不触发"full 档 P7 不可裁"核对条件（P7 本就在全保留之列）。

**核验通过。**

## P1 纯净性

BDD 全部以"运行命令 → 观察退出码/输出/文件"为用户可观测行为表述，无"调用哪个 API/哪个函数签名"类实现细节；D1/D2/D3 为编号空间与范围决策（非实现设计），且依据客观机械约束（gate 正则只认数字 BDD 编号，扫描 3 佐证）+ 设计文档（dispatch-context 指定输入）定案，不构成"P1 掺入解决方案设计"。`verification_env`/vision 等环境能力边界声明与 P1 卡判断树一致。**核验通过。**

## 推进条件对照（P1 卡逐项）

| P1 卡推进条件 | 核验结果 |
|---|---|
| P1-requirements.md 含 BDD ≥ 1 条 | ✅ 16 条（BDD-1..BDD-16） |
| 含「同类扫描」结论（命中清单 + 逐条处理判定） | ✅ 三组扫描（4.1/4.2/4.3）全部落盘 |
| P0-brief 时效性已质疑（无漂移记已核对 / 有漂移含 P0_STALE 且已处理） | ✅ 判据逐条质疑 + `[P0_STALE: debug_env 权限声明]` 轻微漂移按记录处理 |
| domains / packages / risk_level / phases 已声明 | ✅ frontmatter 全部就位 |
| 无 [NEED_CONFIRM] 标记 | ✅ `[NO_NEED_CONFIRM]` 已声明 |
| 无 status: GAP | ✅ 无 GAP，capability_requirements 全部 available |
| P1-review.md status: approved | ✅ 本文件 |

## 结论

**status: approved（与 Header 一致）。** P1-requirements.md 满足 P1 卡全部推进条件：16 条 BDD 编号连续、Given/When/Then 二值可判定且按 M0/M1/M2/M3 分组；三组同类扫描齐备并含回归拦截；P0-brief 时效性已质疑且 1 处轻微漂移按记录处理；frontmatter 机器字段齐全（risk_level=high / ceremony=standard / phases 全保留 / packages=[agate] / domains=[backend]）；无未决 NEED_CONFIRM、无 GAP；能力自查正确（无视觉硬要求）。

**非阻塞备注（不构成 needs-revision）**：行 255 正文拼写笔误 `domans = [backend]`（应为 `domains`）。语义无歧义、不影响机器字段，建议主 Agent 采纳时顺带修正；如需修理由 analyst 下一迭代处理，不阻塞本次通过。