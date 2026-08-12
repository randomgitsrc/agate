---
phase: P1
task_id: TAG0003-workspace-architecture
type: review
parent: P1-requirements.md
trace_id: TAG0003-P1-20260812
status: approved
created: 2026-08-12
agent: requirements-review
---

# TAG0003 — P1 需求基线评审（requirements-review，复审轮）

> 评审对象：docs/tasks/TAG0003-workspace-architecture/P1-requirements.md（修订版，260 行，20 条 BDD，risk_level=high，phases 全 8 阶段）
> 对照输入：P0-brief.md、上一轮 P1-review.md（needs-revision：阻塞项 A + 建议 B）、P1-dispatch-context-analyst-revision.md（修订派发指引）、requirements-review.md 角色清单
> 客观核验：BDD-1..20 编号连续无跳号、格式 `#### BDD-NN:` 合规、无 `- PASS`/`- FAIL` 行首、无 [NEED_CONFIRM]（仅 `[NO_NEED_CONFIRM]`）、无 status: GAP、frontmatter 四字段（risk_level/phases/packages/domains）齐全、.state.yaml phase=P1。

**结论：approved。** 上一轮阻塞项 A（归档历史迁移无 BDD）与建议 B 两条（空源迁移、一致性白名单/用例数基线）已全部解决：新增 BDD-18/19/20 并追加在末尾，既有 BDD 语义未改动（仅 BDD-6/17 补观察项注释，符合基线保护"只补充不破坏"）。未发现 BDD 矛盾、裁剪不合理或 P1 纯净性破坏。2 项非阻塞观察（口径澄清类）留给 P2。

---

## BDD 评审（逐条判定 + 覆盖维度）

维度缩写：数据 D / 前端 F / 多端 M / 边界 B / 兼容 C

- BDD-1（新项目初始化完整目录）：可二值判定（8 子目录存在性可检）。覆盖：D✓ F✓ B✓。
- BDD-2（默认工作区位置 agate-workspace/）：可二值判定（默认路径生效）。覆盖：D✓ B✓。
- BDD-3（项目外路径）：可二值判定（外部路径生效 + 项目根不新建默认目录，双断言均可检）。覆盖：D✓ M✓ B✓。
- BDD-4（无 .agate.env 不报错）：可二值判定（正常启动 + 默认位置 + 无配置错误）。覆盖：B✓。
- BDD-5（路径含空格）：可二值判定（读写正常、无路径解析错误）。覆盖：B✓。
- BDD-6（迁移 docs/tasks 入工作区）：可二值判定（文件落位可检）。覆盖：D✓ C✓。修订已补注释（line 111），明确"不再承担编排职责"为推论性表述、P2 需落到可检状态——观察项 2 已记录。
- BDD-7（不丢失状态与阶段产出）：可二值判定（迁移前后文件清单对比）。覆盖：D✓。显式点名 `.state.yaml` 与 P0-P8 产出，命中隐含需求 #1/#2。
- BDD-8（保留 git 历史）：可二值判定（git log 新路径可追溯）。覆盖：D✓ C✓。不绑定实现（git mv 仅作 SUGGEST 倾向）。
- BDD-9（迁移幂等）：可二值判定（重复运行无新增动作/无重复/无丢失）。覆盖：D✓ B✓ C✓。
- BDD-10（旧布局获得迁移指引）：可二值判定（检测 + 指引 + 不静默继续/不静默失败）。覆盖：C✓ M✓。
- BDD-11（orchestrator 从工作区读 project.md）：可二值判定（读取路径切换可检）。覆盖：M✓ C✓。
- BDD-12（orchestrator 从工作区读任务看板）：可二值判定（读取路径切换可检）。覆盖：F✓ M✓。
- BDD-13（状态机与 gate 以工作区为任务根、行为不变）：可二值判定（扫描范围 + 行为回归对比）。覆盖：M✓ B✓ C✓。Given 含"指向项目外"，覆盖本地 hook 与 CI 一致性（隐含需求 #4）。
- BDD-14（需求/讨论进入 roadmap）：可二值判定（roadmap/ 下出现条目 + 含状态标识）。覆盖：F✓ D✓。
- BDD-15（roadmap 条目拆分进待开始看板）：可二值判定（任务落位 + 关联）。覆盖：F✓ D✓。
- BDD-16（任务完成回写 roadmap）：可二值判定（条目状态更新 + 可追溯）。覆盖：D✓。闭环完成。
- BDD-17（内容边界二值判据）：可二值判定（两类文件结论相反，判据自洽性可检）。覆盖：D✓ B✓。修订已补注释（line 174）说明单条双场景为对偶测试、拆分会丢失对偶断言——观察项 1 已记录，合理。
- BDD-18（存量归档迁入工作区 archived/ 且幂等）：可二值判定（归档整体落位 + 相对目录结构对应 + 无丢失 + 重复运行无重复归档/动作）。覆盖：D✓ C✓ B✓。**阻塞项 A 已解决**——单独覆盖 docs/archived/（BDD-7 只覆盖 docs/tasks/），与 BDD-9 幂等语义一致，不冲突。
- BDD-19（无 docs/tasks/ 时迁移工具正常运行）：可二值判定（不报错 + 无错误动作 + tasks/ 可正常初始化）。覆盖：B✓。**建议 B #1 已解决**——显式覆盖"无迁移源合法"边界。
- BDD-20（迁移后一致性检查白名单与用例数基线全绿）：可二值判定（一致性检查无 ERROR + 用例总数不漂移）。覆盖：C✓ M✓。**建议 B #2 已解决**——命中隐含需求 #9（check-protocol-consistency 白名单重校准 + count-tests 基线）。

**编号与结构**：BDD-1..20 连续无跳号，格式标准，各条单套 Given-When-Then（BDD-17 双场景有设计意图注释，不视为违规）。无跨条 Then 矛盾：迁移族（BDD-6/7/8/9/10/18/19）断言互不冲突（BDD-7 限 docs/tasks/、BDD-18 限 docs/archived/，互补）；路径断言（BDD-11/12/13）一致；roadmap 闭环（BDD-14/15/16）无回环矛盾；BDD-20 与 BDD-13 无冲突。

---

## 隐含需求覆盖（对照 §2 的 12 条逐项）

- 数据维度：覆盖 —— 迁移完整性（#1→BDD-6/7）、.state.yaml 不漏（#2→BDD-7）、幂等（BDD-9）、**归档历史（#10→BDD-18，上轮遗漏项已闭合）**。
- 前端/展示维度：覆盖 —— 看板与 roadmap 入口/格式变化（#5→BDD-1/12/14/15）。无真实 UI（domains 无 frontend），以路径与产物存在性覆盖展示层，合理。
- 多端维度：覆盖 —— 协议本体与下游接入项目双面（#3→BDD-1/6/11）、本地 hook 与 CI 一致性（#4→BDD-13）。
- 边界维度：覆盖 —— 空工作区初始化（#6 新项目侧→BDD-1）、**空源迁移（#6 迁移工具侧→BDD-19，上轮建议已闭合）**、无 .agate.env/空格/项目外路径（#7→BDD-3/4/5）。
- 兼容维度：覆盖 —— 旧项目迁移路径与升级指引（#8→BDD-6/10）、git 历史（BDD-8）、幂等降级（BDD-9）、**一致性检查器白名单与用例数基线（#9→BDD-20，上轮建议已闭合）**。

12 条隐含需求全部有 BDD 锚点，无遗漏。

---

## 上轮阻塞项与建议的解决情况（逐项判定）

- **阻塞项 A（归档历史迁移无 BDD）——已解决**：新增 BDD-18（归档迁入工作区 archived/ + 相对结构对应 + 无丢失 + 幂等），§2 #10 已同步引用。BDD-6/7 Given 限 docs/tasks/ 的缺口由 BDD-18（限 docs/archived/）补齐，两域互补无重叠。
- **建议 B #1（空源迁移）——已解决**：新增 BDD-19（项目从无 docs/tasks/ 时迁移工具正常），§2 #6 已同步引用。
- **建议 B #2（一致性白名单/用例数基线）——已解决**：新增 BDD-20（一致性检查无 ERROR + 用例数不漂移），§2 #9 已同步引用。
- **观察项 1（BDD-17 单条双场景）——已记录**：line 174 注释明确对偶测试意图。
- **观察项 2（BDD-6 Then 推论）——已记录**：line 111 注释明确 P2 需落到可检状态。

---

## 观察项（非阻塞，记录不阻断，P2 需澄清口径）

1. **BDD-20"用例总数不漂移"口径**：迁移工具是新增交付物（P3 会新增其用例），"用例总数与迁移前基线一致"字面上与新增用例增长冲突。语义应为"既有用例换血后数量不漂移（count-tests 基线）、新增迁移工具用例允许增长"。P2 设计需在 BDD-20 验收口径中显式区分"既有基线不变"与"新增允许"，否则 P6 判定时会遇到口径歧义。
2. **BDD-19 与 BDD-1 场景重叠度**：BDD-1（无既有工作区目录的初始化）与 BDD-19（从无 docs/tasks/ 的空源迁移）场景相近但对象不同（初始化 vs 迁移工具运行），P6 判定时需确认两者判定路径分离，避免一条 PASS 误判另一条。

---

## 裁剪评审

- risk_level=high 判定准确：破坏性迁移 + orchestrator 路径影响所有接入项目 + 43 文件/516 处引用（含 377 处测试）+ 新增 roadmap 机制与迁移工具交付物，与 P0-brief known_risks 匹配。
- phases=[P1..P8] 全保留、逐阶段给出理由（P2 设计、P3 迁移工具测试先行、P7 跨文件一致性 + self-gate、P8 发布），与 high 风险匹配。无跳过阶段，无 override 需求。裁剪声明合理。
- capability_requirements 三态正确：bash/python3+pyyaml/bats/shellcheck 均 available，均给实证，无 GAP、无 supplementable 含糊项。合理。

---

## P1 纯净性

- BDD Then 未绑定具体脚本名/实现路径，引用 agate-workspace/、docs/tasks/、docs/archived/、.agate.env、project.md、active-tasks 均为 P0-brief 已确认的需求对象，不构成方案设计。
- 新增 BDD-18/19/20 均为行为/结果描述（归档落位、空源不报错、检查全绿），无实现细节。
- BDD-20 提及"目录排除白名单重校准"是引用既有一致性检查器机制（check-protocol-consistency.py 白名单）作为验收状态描述，同 BDD-13 引用 pre-commit/CI 一致，不算混入方案设计。
- SUGGEST 项含实现倾向但非绑定（git mv、配置优先级链），已标注为非约束倾向项。主体基线纯净。

---

## 结论

**status: approved** —— 修订版需求基线达到通过门槛。上轮阻塞项 A 与建议 B 全部闭合（BDD-18/19/20），隐含需求 12 条全部有 BDD 锚点，无 BDD 矛盾、无裁剪不合理、无纯净性破坏。2 项非阻塞观察（BDD-20 用例数口径、BDD-19/BDD-1 判定分离）记录在案，交 P2 设计时澄清，不阻断 P1 推进。本评审未触碰生产环境，未触发 `[PROD_TOUCHED]`。

[PROD_NOT_TOUCHED]
