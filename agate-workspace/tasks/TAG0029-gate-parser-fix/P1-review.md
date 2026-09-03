---
phase: P1
task_id: TAG0029
parent: P1-requirements.md
trace_id: TAG0029-P1-20260904
agent: requirements-review
status: approved
---

# P1-review — TAG0029 requirements-review 评审意见

> [PROD_NOT_TOUCHED] 本评审只读核查 P1-requirements.md 及关联输入，未改动 P1-requirements.md 与任何实现代码。
> 评审对象：`agate-workspace/tasks/TAG0029-gate-parser-fix/P1-requirements.md`（9 条 BDD，BDD-1~BDD-9）
> 范围依据：`P0-brief.md`（三缺口 scope + out-of-scope 三条）；派发指引：`P1-dispatch-context-requirements-review.md`
> 结论：**approved**（无阻塞项；2 处非阻塞文字建议见末节，不计入重试）

## BDD 评审（二值判定 + 单 Given-When-Then + 编号连续性）

编号连续性：`#### BDD-1:` ~ `#### BDD-9:` 连续无跳号，格式符合 `#### BDD-NN:`；每条均为单 Given-When-Then 单场景；无"部分通过/调整"主观词。

- BDD-1: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-2: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-3: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-4: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-5: 通过 + <覆盖维度：数据n/a 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-6: 通过 + <覆盖维度：数据n/a 前端n/a 多端n/a 边界n/a 兼容✓>
- BDD-7: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-8: 通过 + <覆盖维度：数据✓ 前端n/a 多端n/a 边界✓ 兼容✓>
- BDD-9: 通过 + <覆盖维度：数据n/a 前端n/a 多端n/a 边界✓ 兼容✓>

#### BDD-1: 行内注释值解析出纯命令且可被 bash 执行 — 通过
Given 单一（带 ` #` 注释尾巴的引号包裹命令值）、When 单一（运行解析器）、Then 二值（cmd 恰等于纯命令
+ `bash -c` 退出码不为 2 + stderr 无 unterminated quote）。覆盖 DEBT0027 closure ①。

#### BDD-2: 引号未闭合报解析错误不产出残渣 — 通过
Given/When/Then 单一；Then 三断言同场景合取（非零退出 + stderr 解析错误 + 无残渣输出），二值可判定。
与 BDD-1 按"引号是否闭合"互斥分区，无重叠矛盾。覆盖 H1 后半。

#### BDD-3: 命令串语法错误判 A 类不计入红灯证据 — 通过
Given 显式三元组（bash exit 2 + 含语法错误文案 + 无运行器失败断言统计），真正区分了"命令串本身语法错误"
与"运行器正常退出报告错误"（后者走既有 A 类 Traceback/SyntaxError/exit>=120 分支）；Then 退出码为 1
二值判定。假绿灯根因覆盖到位。覆盖 H2（派发指引易错点②通过）。

#### BDD-4: P3_xxx 辅助键不被收集 — 通过
Then 以 commands 缺席断言，二值；Given 限定"不具测试命令语义"，与 BDD-5 的裸 P3 互斥。

#### BDD-5: 裸 P3 收集而元键豁免 — 通过
单场景双断言（ Transactional 原子判定：含裸 P3 条目 ∧ 不含任一元键条目），二值；与 BDD-4 一致无矛盾。

#### BDD-6: P2 卡 gate_commands 节含 P3_xxx 禁止声明及原因 — 通过
文档存在性断言二值（文本存在 ∧ 原因说明存在）；属协议约束落盘，非实现设计混入。

#### BDD-7: R2 对 fixture 数据面豁免 tests 树 0 命中 — 通过
Given 绑定"fixture 目录内的数据文件"（目录声明绑定，非宽匹配）；Then 无命中 ∧ 退出码 0，二值。
覆盖 H5 前半 + H9。派发指引易错点③前半通过。

#### BDD-8: R2 对代码面裸 python3 仍拦截 — 通过
Given 四重排除（非注释、非 docstring、非探测形态、豁免目录之外），与 BDD-7 按目录内外互斥分区；
Then 报出命中 ∧ 退出码 1，二值。BDD-7/BDD-8 联合可二值判定豁免边界（H5 要求）。易错点③通过。

#### BDD-9: 扫描器纳入 P3/P4 常驻面 — 通过
Then 双块存在性合取断言，二值；覆盖 H6 行为变更的验收面（存量全量扫描为过程义务，见隐含需求节）。

## 隐含需求覆盖（H1~H9 逐条引用）

- 数据维度：覆盖 — H1（BDD-1/BDD-2 值清洗闭合性）、H5 数据面豁免（BDD-7 命令字段真实日志形态）。
- 前端维度：不适用且正确省略 — domains=[backend]，改动面为 `agate/scripts/*` + 卡片文本，无 UI/交互变化；
  无 UX 类别 BDD、无 `ui_render_shape`/`ui_ux_dimensions`、无 vision 条目均正确（与 analyst §8 声明一致）。
- 多端维度：不适用 — 纯本地脚本与协议文本，无 API↔客户端契约面；无遗漏。
- 边界维度：覆盖 — BDD-2（引号未闭合）、BDD-3（exit 2 语法错误 vs 运行器错误）、BDD-4/BDD-5
  （P3 vs P3_xxx vs 元键三态边界）、BDD-7/BDD-8（豁免目录内外边界，H5 单测锁边界要求由 P3 承接）。
- 兼容维度：覆盖 — H3（判据动则同步 rules YAML，S-4，由 P7 承接）、H6（DEBT0025 存量全量扫描过程义务，
  由 phases 含 P7 + BDD-9 承接）、H8（Linux 全量 pytest 底线 + SELF-GATE 提交义务，由 P5/P8 承接）、
  H9（TAG0011 bdd-8 保持绿，由 BDD-7 承接）。

条目映射：H1→BDD-1+BDD-2 ✓；H2→BDD-3 ✓；H3→P7 一致性承接（判据变更同步 YAML，无独立 BDD 合理，属过程 gate）
✓；H4→BDD-4/BDD-5 单测锁定 + 收紧前 grep（P2/P3 承接）✓；H5→BDD-7+BDD-8 ✓；H6→BDD-9 + P7 ✓；
H7→phases 含 P3（TDD 先红后绿过程义务）✓；H8→phases 含 P5/P8 ✓；H9→BDD-7 ✓。无遗漏条目。

## BDD 跨条一致性

- BDD-1 vs BDD-2：按引号闭合性互斥分区，Then（纯命令输出 vs 解析错误）无矛盾。
- BDD-3 独立 judge 侧分区，与 BDD-1/BDD-2 无共享 Given/When，不冲突；与既有 A 类分支按"有无运行器产出"分区，
  H2 已显式声明优先级（运行器正常退出才判红灯）。
- BDD-4 vs BDD-5：P3_xxx 排除 vs 裸 P3 纳入 + 元键排除，三态划分完备一致。
- BDD-7 vs BDD-8：按"豁免目录内外"互斥分区，Then（exit 0 无命中 vs exit 1 有命中）无矛盾。
- BDD-6 vs BDD-9：同断言 P2-design.md 不同节（P3_xxx 禁止声明 vs P3/P4 扫描器条目），无冲突。
- 测试数据环境约束：BDD-1/BDD-3 依赖 `bash -c` 执行语义，标准 Linux 环境可满足，无并发/数据量/资源特殊约束遗漏。

## 裁剪评审

- 本任务主张全阶段（phases 全量 [P1..P8]，零裁剪）：P2（多形态比选）/ P3（单测锁定 closure）/
  P4（四处改动面）/ P5·P6（high 风险底线）/ P7（S-4 对账 + 用例数核对 + 新扫描面上线）/ P8（RM-AG0056→done，
  DEBT0023/0027 关闭登记）理由逐项充分。裁剪合理（无裁剪即合理）。
- 同类扫描"本次不处理"坐实（易错点①通过）：#3 `agate-read-p5-commands.py` L30/L37（P0 scope 锁定三缺口 +
  P5 路径不在假绿灯 `bash -c` 消费链 + 同源不同严重度候选后续，不扩范围）✓；#4 `agate-gate-missing-cmds.py`
  L24（只取首 token 做缺失检测，不经 `bash -c` 执行，不构成 unterminated quote + 回归验证覆盖）✓；
  #6 `is_gate_meta_key` 消费方清单齐全（check-gate 对账 / p5-commands / missing-cmds / read-gate-commands /
  gate-p5-count + S-4 + rules YAML），处理面限定收集侧、动判据同步 YAML（H3）✓；
  R2 全仓唯一 + judge L156-157 exit 2 无分支两项本次处理锚定 BDD-7/BDD-8/BDD-3 ✓。scope 锁定与同源扩散平衡得当。
- P0-brief 时效性质疑：§5 已独立质疑并记录"无漂移"（同日立项 + 四处缺陷模式仍命中 + 状态机一致），符合
  "无间隔/无漂移则记录已核对"规则。待确认清单 `[NO_NEED_CONFIRM]` 合法（范围锁定 + 方向明确，无真阻塞）。
- analyst 偏离派发检查：trace_id 与本 review 同日（TAG0029-P1-20260904，analyst 以执行日为准已更新，
  主 Agent 初检通过）；risk high / phases 全量 / packages 四项 / domains [backend] / 能力三态空表 + 判断树
  说明均与派发一致，无偏离。

## 审声明（风险分级/裁剪声明 vs diff 证据）

- 暂存区证据（`git diff --cached --stat` + `git status --short` 只读查证）：已暂存仅 `.state.yaml`（M）；
  未暂存新建为 P1 派发上下文 ×2 + P1-requirements.md（P1 阶段无 `agate/scripts/*` 实现改动，符合阶段纯净性）。
- `risk_level: high` vs 实际改动面：匹配 — DEBT0027 假绿灯属验收真实性风险（high），改动面跨解析器/judge/
  扫描器/协议卡四处（packages 四项对应），high 不虚高。
- `ceremony` 未声明 → 缺省 standard（fail-closed），无 thin 四要素义务；`ceremony: full → phases 含 P7`
  规则不触发（未声明 full），而实际 phases 全量含 P7，核对通过。
- `phases` 全量 vs 改动规模：匹配 — 新扫描面常驻（行为变更）+ 判据收紧须过 P7，P7 不可裁已含。
- `domains: [backend]` vs 改动域：匹配 — scripts + 卡片文本，无前端面；UX/视觉豁免正确。
- 结论：审声明核对通过；声明与实际一致，不触发 `needs-revision`/`rejected`。

## P1 纯净性

- BDD 均为行为/判定描述（输出什么/判什么），未指定实现机制（如未写"首个未转义 ` #`"算法、正则改法、
  豁免存储结构）；H1~H9 为需求约束与过程义务，非解决方案设计。BDD-6/BDD-9 为文档存在性验收，
  非设计方案。纯净性通过。out-of-scope 三条（DEBT0016/17/18→TAG0031；R2 本体语义不扩；cmdstream 引擎不动；
  TAG0011 bdd-8 不改断言意图）均未被需求越界。

## 非阻塞建议（不阻 approved，analyst 可自行决定是否采纳）

1. BDD-3 Given 中"语法错误文案"可枚举典型串（如 unterminated quote / syntax error）以增强 P6 可重复性，
   但当前三元组已可二值判定，不作打回。
2. H3/H6 无独立 BDD 而由 P7/过程承接是合理的；若 P2 设计动公共判据，须按基线保护回写 `[BASELINE_CHANGE]`。

## 评审结论

- Status: approved
- 锚点完备性：正文含 `#### BDD-1:` ~ `#### BDD-9:` 全部锚点 + 覆盖维度清单（数据/前端/多端/边界/兼容逐项标注）
  + 隐含需求条目 H1~H9 引用 + 审声明 diff 证据（暂存区文件类型/规模/域）+ ceremony:full→P7 核对记录。
