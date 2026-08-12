---
phase: P1
task_id: TAG0002-refactor-first-class
type: review
parent: P1-requirements.md
trace_id: TAG0002-P1-20260812
status: approved
created: 2026-08-12
agent: requirements-review
---

# P1 需求基线评审（复审轮）：TAG0002 重构一等任务（Phase A）

> 评审对象：`docs/tasks/TAG0002-refactor-first-class/P1-requirements.md`（193 行，8 条 BDD，3 条 SUGGEST）
> 评审基准：requirements-review.md 检查清单 + dispatch-context 本任务特有评审重点 5 项 + P0-brief known_risks
> 本轮重点：上一轮 needs-revision 阻塞项（**P3 回归测试设计缺直接 BDD 锚点**）是否已解决
> 独立查证：check-gate.sh P6 分支（L292-322，无 change_type 分流）、P6-acceptance.md L4（仅 no_behavior_change 简化表述）、P3-tdd.md L37（测试用例与 BDD 1:1 映射）、check-p6-provenance.sh 审计 3（P1_BDD vs P6 PASS+FAIL 总数对照）、check-protocol-consistency.py L463（P6 no_behavior_change 锚点）、`agate/` 全树 `change_type` 字段（零命中）、review-design §5.3/§6.1.1/§6.1.4 止损条款

## 上一轮阻塞项解决情况（本复审主判）

**P3 回归测试设计缺直接 BDD 锚点 → 已解决。**

- 新增 **BDD-8**（§3.4 功能组 D，标题即锚定"P3 测试设计为回归测试口径 + P3 卡片/派发指引含回归口径说明 + 可被 P6 验收"），Given/When/Then 完整：
  - Given：`change_type: refactor` 任务进入 P3，需求基线无新功能 BDD
  - When：test-designer 依据 P3 测试设计指引设计用例
  - Then：测试设计为回归口径（复用/保留既有用例、不新增功能行为断言）+ P3 卡片/派发指引已明确写入回归口径说明 + 可被 P6 验收逐条对照
- **可二值判定**：判定对象 = P3 测试设计产物性质 + P3 卡片/派发指引文档是否含回归口径说明，两者均可 PASS/FAIL 判定，无中间态。
- **修复来源可追溯**：§3.4 显式标注"known_risks[3] 锚点"，§2.3 散文需求与 BDD-8 一一对应，SUGGEST #3 保持待采纳状态（主 Agent 可自决）。上一轮指出的"若 test-designer 即兴改编，P3 卡片同步需求可静默流失"的风险已由 BDD-8 的 Then 条款（"不是 test-designer 即兴改编的产物"）显式封堵。

## BDD 评审

格式合规：编号 `#### BDD-NN:` 连续（BDD-1…BDD-8），无跳号、无重复；每条仅一条 Given/When/Then（8 条 × 3 = 24 行 G/W/T，已核对）；全部可二值判定（PASS/FAIL 无中间态）。

- BDD-1（P1 可声明 change_type: refactor）：判定=符合，可二值判定（gate 通过且不报错）。覆盖维度：数据✗ 前端✗ 多端✗ 边界✗ 兼容✓（新增字段不破坏既有任务缺省路径）
- BDD-2（缺省向后兼容）：判定=符合，可二值判定（口径与改造前一致）。覆盖维度：数据✗ 前端✗ 多端✗ 边界✓（缺省=旧口径的边界情形） 兼容✓（存量任务/631 用例基线不受影响）
- BDD-3（refactor 走回归口径，无需伪造功能 BDD）：判定=符合，可二值判定（gate 是否因无功能 BDD 拦截）。覆盖维度：数据✗ 前端✗ 多端✓（gate↔口径契约） 边界✗ 兼容✗
- BDD-4（回归未全绿→验收不通过）：判定=符合，可二值判定（关键路径 PASS 不能豁免回归失败）。覆盖维度：数据✓（回归运行结果为客观证据） 前端✗ 多端✗ 边界✓（失败路径判定） 兼容✗
- BDD-5（口径文档禁止伪造功能 BDD）：判定=符合，可二值判定（文档是否含明确约束）。覆盖维度：数据✗ 前端✗ 多端✓（verifier 消费方可见） 边界✗ 兼容✗
- BDD-6（refactor 口径独立于 no_behavior_change）：判定=符合，可二值判定（no_behavior_change 是否豁免/改变 refactor 判定）。覆盖维度：数据✗ 前端✗ 多端✗ 边界✓（混用/降级边界） 兼容✓（与既有 no_behavior_change 语义并存不替代）
- BDD-7（真实重构回填走 P1-P6）：判定=符合，可二值判定（各阶段 gate 是否通过 + 是否被强制伪造）。覆盖维度：数据✓（真实重构作验收样本） 前端✗ 多端✓（P1-P6 全链路跨阶段契约） 边界✓（全流程边界） 兼容✓（回填验证不破坏既有协议）
- BDD-8（P3 回归测试设计口径）：判定=符合，可二值判定（P3 测试设计产物 + P3 卡片/派发指引文档状态）。覆盖维度：数据✓（回归口径即"复用既有用例"的数据基础） 前端✗ 多端✓（P3 卡片↔派发指引↔test-designer↔P6 验收多方契约） 边界✓（refactor 无新行为断言的边界） 兼容✓（与既有 P3 功能口径并存，仅 refactor 任务切换）

## 隐含需求覆盖

- 数据维度：**覆盖**。回归运行结果（BDD-4）、真实重构回填（BDD-7）、既有用例复用（BDD-8）作为客观证据锚点，§2.8 诚实标注"伪造功能 BDD 无法完全机器判定"的边界。
- 前端维度：**不适用**。无 UI，domains 已声明无 frontend。
- 多端维度：**覆盖**。§2.5（check-protocol-consistency.py 锚点同步）、§2.6（P1 卡片样例/verifier 角色/P6 派发指引的可发现性）、§2.4（check-p6-provenance 审计 3 不豁免）、BDD-8（P3 卡片/派发指引多方契约）。
- 边界维度：**覆盖**。§2.2（缺省=功能口径）、§2.4（BDD 编号机制兼容）、BDD-6（混用边界）、BDD-4（回归失败边界）、BDD-8（无新行为断言边界）。
- 兼容维度：**覆盖**。§2.2 向后兼容 + BDD-2 + BDD-6（no_behavior_change 并存不替代）+ BDD-8（P3 功能口径并存）。

## BDD 跨条一致性

- 无矛盾：BDD-2（缺省走功能口径）与 BDD-3/6（refactor 走回归口径）以 `change_type` 声明与否区分场景，不冲突。
- BDD-8 与既有条一致：BDD-3（P6 回归口径）、BDD-7（回填不被强制伪造）在"refactor 不新增功能断言"上同向；BDD-8 补足 P3 层，形成 P3→P6 闭环，无反向约束。
- 保护优先级显式：BDD-6 明确 refactor 口径支配 no_behavior_change（不豁免不降级），无重叠歧义。
- 测试数据考虑环境约束：BDD-7 回填依托 P0-brief 已声明的真实重构样本 + 既有 631 用例基线，可执行。

## 裁剪评审

- 全流程 P1-P8 无裁剪，§5 逐阶段理由充分（P2 需独立评审设计决策、P3 需先写失败 bats 测试、P6 含回填验收、P7 横切多文件需一致性核对）。合理。
- risk_level=medium：触及 gate 脚本行为 + 协议文档横切 + 向后兼容 + 需回填验证，但缺省行为不变故非破坏性——medium 与风险匹配。
- capability_requirements：四项（bash/py3+pyyaml/bats/shellcheck）全部 available，均已在 worktree 环境核实（P0-brief test_cmd + env），无 GAP、无 supplementable。判定正确。

## P1 纯净性

- 未掺入解决方案设计：§1.3 改动面表格为"现状 vs 需要什么"范围界定（非"怎么做"），BDD 全部描述可观测的 gate/文档行为，无具体实现细节（如改动哪一行脚本）。基本纯净。
- 备注（非阻塞）：§2.6 提及"P1 卡片 frontmatter 样例注明 change_type 字段"——属可发现性需求而非实现方案，可接受。

## 本任务特有评审重点（5 项）

1. **refactor 口径 vs no_behavior_change 等价性**：§2.1 论证充分——两者语义方向相反（影响声明 vs 任务类型声明）、互补不替代，独立分支理由成立。独立查证一致：check-gate.sh P6 分支（L292-322）确为 BDD 计数 + 证据目录检查、不读取 no_behavior_change；P6-acceptance.md L4 仅有"可简化"表述。BDD-6 锚定。
2. **P6 gate 分流**：BDD-2（缺省旧口径）+ BDD-3（refactor 走回归口径）+ BDD-4（回归失败拦截）+ BDD-6（不降级）行为级覆盖 check-gate.sh P6 分流，可验收。
3. **P3 回归测试设计**：**已解决（本轮阻塞项）**。BDD-8 直接锚定回归口径 + P3 卡片/派发指引说明 + 可被 P6 验收，§2.3 散文需求已升级为 BDD 硬锚，known_risks[3] 回应闭环。
4. **流程不比直接改麻烦**：§2.7 明确不新增文书负担（不强制审计/不伪造 BDD/不新增阶段），BDD-7 Then 锚定"重构流程不比直接改更麻烦"，review-design §6.1.1 止损条款（连续 3 次仍协议外→重设计）已被 P1 §1.2 决策 5 引用为边界条件。
5. **回填验证**：BDD-7 覆盖真实历史重构回填 P1-P6 全流程 + 各阶段 gate 通过 + 未被强制伪造，与 review-design §5.3 Phase A 验收一致。

## 评审结论

**上一轮阻塞项（P3 回归测试设计缺 BDD 锚点）已解决**：BDD-8 格式合规、可二值判定、与 §2.3/known_risks[3] 及 P3-tdd.md L37 现状（1:1 映射会卡死 refactor）对应成立，P3→P6 回归口径闭环完整。

**整体质量高**：等价性论证严谨（§2.1）、缺省向后兼容有 BDD 硬锚（BDD-2）、诚实标注（§2.8）到位、裁剪与能力声明合理、P1 纯净性合格、§1.3 改动面六行全部经独立查证属实。

**本复审无打回项**。上一轮已通过的项（BDD-1…BDD-7 格式/可判定性/一致性、五维度覆盖、裁剪、risk_level、capability、P1 纯净性）复审后维持通过；新增 BDD-8 评审通过。

status: approved
