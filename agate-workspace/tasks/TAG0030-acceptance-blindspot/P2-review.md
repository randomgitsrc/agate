---
phase: P2
task_id: TAG0030
type: review
parent: P2-design.md
trace_id: TAG0030-P2-20260904
status: approved
created: 2026-09-04
agent: plan-eng-review
---

# P2-review — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）

> 评审角色：plan-eng-review（工程经理）。评审对象 `P2-design.md`（241 行）。纯协议文档面评审，
> 不涉及生产环境 `[PROD_NOT_TOUCHED]`。只审不写——本文件不回改 P2-design.md，意见由主 Agent
> 决定是否回派 architect。

## 结论

**status: approved**（阻塞级架构问题 0 项；非阻塞落笔注意 7 项 + 测试缺口观察 2 项，均不构成
打回条件，可在 P3/P4 落地时吸收）。候选方案 ≥2 + 权衡充分（v0.6 nudge 满足），实现就绪度
达标（files_to_read 覆盖面完整、dispatch_plan 三批合理），最小验证真实（§8 动作与结论一致）。

## 架构问题（阻塞级）

无。范围锁定、门槛契约、CHECK11 三锚词、影响面完整性、gate_commands 固化五项逐一核对
无阻塞项（逐项证据见「评审对照」）。

## 架构问题（非阻塞）

以下均为 P3/P4 落笔注意级观察，不属「后续应重构 / 架构债」，不产 DEBT 条目（dispatch 约束 6）：

- **N1（实现导航小缺口）**：P2-design §6 files_to_read（行 183-211）未列入 grep 断言审计测试的
  既有参照模式——`agate/tests/unit/test_review_role_docs.py`（TAG0006 产物，其
  `test_bdd_6_plan_design_review_dimensions` 已锁定 plan-design-review.md「视觉设计/交互设计/
  渲染正确性与时序」三锚词）与 `agate/tests/unit/test_protocol_mechanism_anchors.py`
  （TAG0012 锚词审计模式，`read_text + assert "x" in text` 平台无关写法 + windows_smoke 标注）。
  这是新建 `test_tag0030_assertions.py`（§0.1 #14 行 41）的现成模式源与协同锚（详见「锁定决策」D4）。
  建议 P4 templates-tests-meta 批实现导航补入（行为不阻塞：implementer 可自行发现）。
- **N2（P5 主命令语义 + 既有单测双锚）**：gate_commands（§5 行 158-175）无裸 `P5:` 主 key，
  仅 P5_unit/regression/integration/consistency/shellcheck/count 六个 `P5_*` 辅助 key——
  `agate-gate-p5-count.py` 统计得出 0 主 + 6 辅，`check-gate.py` gate_p5（行 1005-1010）会打印
  「GATE P5 WARNING: 0 个主命令 + 6 个辅助命令」提醒型 WARNING（非阻断，exit 语义由
  pre-task-baseline 机械 diff 决定）。功能上 P5 六命令可完整枚举执行，无真实缺口；仅提示
  可考虑加 `P5: "python3 -m pytest agate/tests/unit/ -q --tb=no"` 作主命令使计数语义自然。
- **N3（files_to_read 未列 CHANGELOG.md）**：§0.1 #13（行 40）与 §9.5（行 240）要求
  「CHANGELOG Unreleased 同步」，但 §6 #13（行 209-210）只列 UPGRADING.md，未列 CHANGELOG.md
  与 `agate-changelog-unreleased.py` 工具。当前 CHANGELOG.md 无 `## [Unreleased]` 节（最新
  `[0.67.0] - 2026-09-03`），P4 需新建该节——建议 files_to_read 补 CHANGELOG.md 一行。
- **N4（双「>5」阈值措辞易混）**：BDD-21 锚词「>5 文件」（§2 Phase4 行 134、§0.1 #9 行 36）与
  dispatch-prompt.md 行 49 既有「输入文件 >5 个分批」硬规则（§0.2 #9 行 60 已声明不重复）阈值
  同为「>5」，语义却不同（任务体量 vs 输入数）。P4 落笔建议写「改动体量 >5 文件」以显式区分，
  避免读者混淆拆小（派发前兜底）与分批（产出/输入数规则）。
- **N5（文件名 pin 定与 architect 约束 5 的偏差未标注）**：§5（行 177-178）将 P3 审计测试文件名
  固定为 `test_tag0030_assertions.py` 并称「不得另起文件名（gate 已固化）」；architect 派发约束
  5（P2-dispatch-context-architect.md 行 32-33）却要求「不限定文件名，由 P3 test-designer 定」。
  从 gate_commands.P3 需要指向真实路径看，pin 名是更稳的选择；但设计未对这条指令偏差做一句
  交代。建议 §5 补一句「对照 architect 约束 5 的偏差理由」；不补亦可（gate 契约优先）。
- **N6（跨包文件 P7 核对列示不完整）**：role-system.md（§0.1 #12 行 39）、tests/README.md、
  AGENTS.md、UPGRADING/CHANGELOG 均不在 P1 三包面
  （phase-cards/assets-roles/assets-templates）内；§9.6（行 241）只显式列出 role-system 行 47
  为 P7 交叉核对项。建议 P7 派发指引把其余跨包文件一并列入核对清单（§9.1 锚词 grep + §9.5
  UPGRADING 已有兜底，属提示性补强）。
- **N7（P3_timeout_seconds 表述）**：§5（行 179）声明 `P3_timeout_seconds: 120` 并注明「仅作
  执行方 shell 超时参考」。P2 卡 `{key}_timeout_seconds` 规则 1 明言「排除 P3：只服务 P5/P6/其他
  非 P3 key」。设计已显式标注参考语义、不覆盖 AGATE_TDD_TIMEOUT，含义无歧义；仅提示未来读者
  勿把该值当作 P3 运行时真实超时。

## 测试缺口

- **G1（锚词机制语义局限，既有通性非本设计引入）**：BDD-10/12「先读受评任务 `ui_render_shape`
  再加载维度组」的**机制正确性**（分派逻辑、维度组映射）grep 只能锁「词存在」，锁不住「逻辑
  正确」——§2 Phase3（行 120-126）声称的形态分派行为最终靠评审 + P7 人工核对兜底，P3 审计单测
  只能防条文被删。与 CHECK11「词存在白名单」同为协议既定模式的已知边界，建议 P7 显式核对该
  语义点（§9.6 可补一句）。
- **G2（断言 AGENTS.md 仓库根路径）**：BDD-20 载体锚词在 worktree 根 AGENTS.md（§0.1 #11 行 38），
  新审计单测断言它时需经 `agate_root.parent` 上溯——conftest `_resolve_agate_root` 上溯解析可
  行，CI 仓库 checkout 下可达；P3 test-designer 写用例时注意路径基座，勿假设 agate_root 即
  仓库根。

## 锁定决策

- **D1（候选方案 A 确认）**：§1（行 76-101）方案 A「单源提及式」vs 方案 B「分散定义式」取舍
  自洽——本任务是「门槛契约冻结 + 白名单锚点强耦合」场景（CHECK11 三锚词、0-10/status 门槛），
  最小改写是风险主导最优解；稻草人自检（行 100-101）说明方案 B 非陪衬，其自包含性真实更优但
  总账为负。candidate_count=2 与正文（§1 两方案）一致。
- **D2（落点 pin 定确认）**：§3（行 136-144）BDD-16 定义落 `architect.md` 视觉 checklist 头部
  （实测行 88-91，BDD-17 同文件一次落笔天然单源）、BDD-18 落 `verifier.md` 证据形式指南
  （实测「行为验证证据优先级」节行 76-92，files_to_read 标 `:70-95` 覆盖）。落实 P1「或」表述
  的 P2 pin 定（P2-dispatch-context-architect.md 约束 8）。
- **D3（连带同步判 Modify 确认）**：§4（行 146-154）role-system.md 行 47 判 Modify——实测行 47
  「七维：…」扁平罗列与形态分组表述不兼容，保留维度名改形态分组口径理由成立；
  CHECK11 三锚词「只增不删」——实测 consistency 行 910-911 白名单
  `("agate/assets/review-roles/plan-design-review.md", ("视觉设计", "交互设计", "渲染正确性与时序"))`
  与 plan-design-review.md 行 19-21 三词俱在，保持方案可行。
- **D4（既有双保险协同确认）**：既有 `test_review_role_docs.py::test_bdd_6_plan_design_review_dimensions`
  与 CHECK11 对同一三锚词构成「单测 + 白名单」双保险——§2 Phase3「评分行原文保留」策略下
  两条防线均不破，形态分派头只增不改的写法成立（§0.3 风险 1/3 缓解有效）。
- **D5（门槛契约冻结确认）**：§2 Phase3（行 126）「0-10 分值行与 status 映射行原文保留」+
  §0.2 #7（行 58）「0-10 权重语义 + status 映射冻结」——实测 plan-design-review.md 行 13-21
  评分维度 + 行 31-38 门槛产出（status 映射 approved/rejected/needs-revision）均为将保留原文，
  无形态声明回落布局型默认（行 26-21 既有启用规则兼容）。check-gate P2「读 status 判门槛」语义
  不被触碰。
- **D6（范围锁定确认）**：§0.2 十项 Not Modify（行 48-61）覆盖 check-gate 判据（含
  `_gate_p1_ui_shape`）、consistency 不新增 CHECK、rules/ 全树、review-mapping/WORKFLOW 映射
  机制、vision-analyst 概念定位、P6 证据形态机制、dispatch-prompt 行 49 硬规则、具体项目 spec、
  state-transitions 行 54（实测 "READY 收尾检查：测试环境清理/开发环境还原"，P8 后语义，与
  测试运行期残留检查非同问题）——TAG0029/TAG0031 out-of-scope 保持（§0.3 风险 5）。

## 实现就绪度核对

- **files_to_read 13 项**（§6 行 183-211）：全部带行号/范围 + why + 批次归属；逐一实测——
  P3 卡 step0 行 8、P4 卡 step0 行 8、tests/README「何时更新」行 114-120（标注 114-121）、
  AGENTS.md「改脚本的工作流」行 17-23（标注 17-24）、dispatch-context.md 61 行（标注全读）、
  architect.md 渲染 checklist 行 93-99（标注只读不动）均与实测吻合。唯一补强项 = N1/N3 两处
  参照文件缺口（非阻断）。
- **dispatch_plan**（frontmatter 行 14）：mode=static-batch、parallel_limit=3、三批
  phase-cards(medium)/assets-roles(medium)/templates-tests-meta(low)——批 id 与 packages 三包
  一致，批数 ≤ 并行上限，complexity 取值合法；三个批次与 §6 files_to_read 批次标注、§0.1
  Modify 表 14 行归属完全对齐（role-system 归 assets-roles 批、AGENTS/UPGRADING 归
  templates-tests-meta 批）。

## gate_commands 固化核对

- §5（行 158-175）15 项 key 全部独立命令、零 `&&` 短路（DEBT0012 反模式规避）：P3 单 pytest、
  P5_unit/regression/integration 分片 `-n auto` 并行、P5_consistency `--strict-errors-only`
  （默认档位正确）、P5_shellcheck 三 hook 薄壳、P5_count 用例数核对。per-key timeout 与 P2 卡
  三档基准同量级或更宽松（unit 300s ≥ 120s 参考档、integration 600s、consistency 120s、
  shellcheck 60s、count 120s），取值方向正确（宁可高不误判，TPV0093 教训）。
- P3 走 `AGATE_TDD_TIMEOUT` 机制、timeout_seconds 仅服务非 P3 key——与 P2 卡规则 1 一致
  （N7 提示性项除外）。
- `P3_formatter: pytest.sh` 实测存在于 `agate/assets/formatters/` ✓。

## 最小验证核对（dispatch 约束 5）

- §8（行 224-232）含 assumption/method/result/note 四要素，声明「纯文档 + pytest/grep 改造，
  无浏览器/外部系统依赖」与 architect 派发约束 10 口径逐字一致（P2 卡 minimal_validation 字段
  要求的声明 + 理由满足；本任务无外部系统行为假设，属「纯代码逻辑」类，无外验必要——与 P1 §4
  能力需求声明一致）。
- 验证动作真实可复核：21 锚词 × CHECK14/15 平台词零冲突——实测 CHECK14 扫描面 = `agate/*.md`
  顶层（`check-protocol-consistency.py` 行 1233-1237），本任务改动面（phase-cards/assets/
  templates/tests-README/AGENTS/UPGRADING）均在扫描面外；CHECK15 数据面仅 rules/*.yaml +
  schema/*.json（行 1266-1279），P2 不碰 rules/ 故无触达；21 锚词无一命中平台词表
  （OpenCode/Claude Code/DSH/workflow/ralph/goal/task）。
- CHECK11 保持方案可行：三锚词 + 0-10 + status 五词实测俱在 plan-design-review.md
  （行 13-21/31-38）。

## 测试策略核对

- P3 断言审计单测（BDD-6 载体，§0.1 #14 行 41）锁定 #1~13 全部落点锚词——比 P1 BDD-6 载体
  （仅 P3/P6 卡 + dispatch-context 模板）更强的全量锁，条文删/改即转红；既有
  test_review_role_docs.py + CHECK11 双保险继续常驻（D4）。
- P5 回归三片（unit/regression/integration）+ consistency + shellcheck + count 构成完整防线，
  与 P1 §7 回归拦截声明（① 审计单测常驻 ② P7 三包面交叉核对）配套。

## 评审对照（TAG0030 核心约束逐项）

- 范围锁定（dispatch 约束 1）：保持——不改 check-gate 判据（§0.2 #1）、不实现清理运行器
  （§0.2 #8）、TAG0029/TAG0031 out-of-scope（§0.3 风险 5）、不重构形态声明机制（§0.2 #7）。
- 门槛契约（约束 2）：保持——0-10 + status 原文保留（D5），gate 读 status 语义不变。
- 视觉契约可表达子集（约束 3）：保持——仅五类 DOM 度量（§0.1 #7 行 34），不收主观视觉。
- DEBT0026 边界（约束 4）：保持——只补 dispatch-context 模板拆小默认指导（§0.1 #9 行 36、
  §2 Phase4 行 134），不重复 TAG0028 §4（§0.2 #9 行 60）。
- BDD-16 落点 pin 定（约束 8）：落实（D2）。
- role-system 行 47 同步（约束 7）：判 Modify + 理由（D3）。
- CHECK11 三锚词禁动（约束 7）：只增不删 + P5_consistency 常驻 + 审计单测同锁（D3/D4）。
- 实现就绪度（约束 3）：达标（见上，N1/N3 补强）。
- gate_commands 固化（约束 4）：达标（见上）。
- 最小验证（约束 5）：达标（见上）。
- 技术债（约束 6）：本评审未提出「后续应重构 / 架构债」结论（N1-N7 均为任务内可吸收的落笔
  注意/导航补强，G1 为既有机制通性局限），故不产 DEBT 条目、不登记 tech-debt.md。

## 审声明

- 评审依据：P2-design.md 全文 241 行 + 派发上下文 10 项输入文件逐一实测核对（P1-requirements、
  P0-brief、plan-eng-review 角色、plan-design-review.md 38 行、check-protocol-consistency.py
  CHECK11/14/15 口径、role-system.md 行 47、architect.md 视觉/渲染 checklist、P3/P4/P6/P1 卡
  step0 与产出规格、dispatch-context 模板 61 行、tests/README 114-120、AGENTS.md 17-23、
  UPGRADING/CHANGELOG 头部、SELF-GATE.md 触发面、conftest fixture、既有锚词审计测试两文件）。
- 无未读输入、无悬置决策、无需 HUMAN_CONFIRM 项；阻塞 0、非阻塞 7、测试缺口观察 2。
- 结论：**approved**——方案可进入 P3/P4；N1/N3/N5 三项建议主 Agent 酌情回派 architect 补
  files_to_read 与 §5 一句说明，不构成打回条件。