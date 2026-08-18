---
phase: P1
task_id: TAG0012-protocol-mechanism-fixes
type: review
parent: P1-requirements.md
trace_id: TAG0012-P1review-20260818-retry1
status: approved
created: 2026-08-18
agent: requirements-review
---

# P1 需求基线评审 — TAG0012 协议机制增强批（重试 #1 复核）

独立视角评审，未修改 P1-requirements.md。domains: [process]，本任务无 frontend，评审跳过 UI/UX 类别 BDD、`ui_render_shape`、vision 能力声明相关检查项（按 dispatch-context 约束 1）。

## 结论先行

**status: approved**。本轮为针对性复核（非重新展开全部 23 条），聚焦上一轮 needs-revision 的 3 处发现（BDD-13 规范/示例混淆、BDD-16/21 缺 AGATE_TDD_TIMEOUT 关系问题、architect.md/analyst.md 覆盖不对称）。三处均已妥善解决，逐点核实见下；其余 19 条已判 PASS 的 BDD 复核未发现被修订过程破坏的迹象，沿用上一轮判定。

## 复核 3 处改动点

### 1. BDD-13（L161-170）：规范正文 vs 示例块拆分 + 层级 2 显式区分

行号交叉核实（`grep -n` 实测 dispatch-protocol.md）：
- L429 `## 派发 prompt 模板`、L462 `## 分阶段落盘（留痕文件，防空返回）`（属于 L429 起内联模板的一部分，是"全阶段通用"规范正文）
- L503 `### 非阶段产出的路径规范`、L521 `## 分阶段落盘（留痕文件）`（此 L521 确认位于 L514 起"示例（self-gate 审查派发）："之后的 ``` 代码块内，是场景示例，非独立规范节）
- L790 `## Playwright/长时操作 subagent 派发策略`（层级 2 硬超时机制：`HARD=90_000/180_000` + `lastStep` + exit code 0/1/2 语义，确认存在于 L790-879 区间）

修订后 BDD-13 的 Then 已正确拆成两支：
- 「规范正文，必改」5 点，其中第 5 点新增："新增内容须与 L790-879...既有硬超时机制（层级 2...）建立显式的文档内引用区分，明确标注本次新增的是'层级 4：bash 命令级超时兜底'，不是层级 2 的替代或重复" —— 客观可判（grep 关键词"层级 4"/引用关系是否落盘）。
- 「L521 示例块，条件性」：改为引用 L462 新增段落而非重复展开（与 BDD-17/BDD-19 引用模式一致），且要求"若判定不适用需留一句理由说明，不允许留空"——避免了留白应付。

判定：**已解决**。规范正文/示例块编辑方式的区分清晰，层级 4 vs 层级 2 的显式区分要求已落入 Then 判据（不再只停留在第 0 节 analyst 内部认知）。

### 2. BDD-16（L191-198）+ BDD-21（L226-230）：新字段与 AGATE_TDD_TIMEOUT 关系

核实 `agate/scripts/agate_common.py:408`：`timeout_secs = int(os.environ.get("AGATE_TDD_TIMEOUT", "120"))`，行号与 BDD-16 引用一致。

BDD-16 第 4 点新增问题："新字段是否适用于 `gate_commands.P3` key；若适用，与既有 `AGATE_TDD_TIMEOUT` env var 机制...是互斥（`timeout_seconds` 存在时优先覆盖）、叠加、还是字段本身排除 P3...——具体决定仍由 P2 architect 拍板，本 BDD 只验证'该层级关系问题被文档显式回答'，不预设/写死答案"。核实：只提出问题选项（互斥/叠加/排除三选一框架），未指定最终选哪个，符合 P1 不越权拍板的定位。

BDD-21 新增"联动 BDD-16 第 4 点"的 Then 子句：若样例块 P3 key 下标注 `timeout_seconds` 示例，注释须引用 BDD-16 第 4 点说明，不在样例块重复展开关系细节——是联动引用而非重复展开，落点正确。

判定：**已解决**。层级 1（P3 专用 AGATE_TDD_TIMEOUT）vs 新字段的关系已作为"必须被文档显式回答的问题"写入 Then 判据，且未替 P2 拍板具体答案。

### 3. BDD-15b（新增，L186-189）：architect.md/analyst.md 覆盖不对称

核实：`grep -n "影响面\|同类" agate/assets/execution-roles/architect.md` 零命中，`agate/assets/execution-roles/architect.md` L191 确认存在「批次设计」节（TAG0014 强制节）——与 BDD-15b 的 Given 描述一致。

BDD-15b 要求 architect.md「批次设计」节新增检查项，"引用/执行 P2-design.md（BDD-15）定义的'影响面梳理'要求，不在角色文件内重复展开梳理方法细节（与既有'权威定义 + 角色文件引用'惯例一致，可参照 BDD-19 verifier.md 对 dispatch-protocol.md 的引用模式）"。

判定：**已解决**。analyst 选择了方案①（补 BDD-15b），落点方式（角色文件引用卡片权威定义，不重复展开）与既有 BDD-19 引用模式一致、与 BDD-3/BDD-17/BDD-18 等"权威定义+引用"组织惯例一致，选择站得住；同时使 analyst.md（BDD-4 卡片 + BDD-7 角色文件）与 architect.md（BDD-15 卡片 + BDD-15b 角色文件）两侧覆盖方式对称。全局编号声明（L82："BDD-1…BDD-22，另有对称补充项 BDD-15b，共 23 条"；L252："23 条 BDD（BDD-1~22 + BDD-15b）"）前后一致。

## 沿用上一轮判定的 19 条 BDD（未发现被本次修订破坏）

BDD-1、BDD-2、BDD-3、BDD-4、BDD-5、BDD-6、BDD-7、BDD-8、BDD-9、BDD-10、BDD-11、BDD-12、BDD-14、BDD-15、BDD-17、BDD-18、BDD-19、BDD-20、BDD-22 —— 均判定 PASS，覆盖维度（数据/多端/边界/兼容，前端 N/A）见上一轮 P1-review.md 逐条记录，本轮复核未发现修订过程中语义被意外改动。

## 覆盖维度小结（角色文件「实质锚点要求」）— 全 23 条 BDD 清单

- approved（19 条，沿用上一轮）：BDD-1、BDD-2、BDD-3、BDD-4、BDD-5、BDD-6、BDD-7、BDD-8、BDD-9、BDD-10、BDD-11、BDD-12、BDD-14、BDD-15、BDD-17、BDD-18、BDD-19、BDD-20、BDD-22
- approved（本轮修订确认，3 条）：BDD-13（规范正文/示例块拆分 + 层级 4 vs 层级 2 显式区分，覆盖：边界✓ 多端✓）、BDD-16（P3 key 与 AGATE_TDD_TIMEOUT 关系问题化，覆盖：兼容✓）、BDD-21（联动引用 BDD-16 第 4 点，覆盖：多端✓ 兼容✓）
- approved（本轮新增，1 条）：BDD-15b（architect.md 影响面梳理检查项，与 analyst.md BDD-7 对称，覆盖：多端✓ 数据✓）

合计 23 条 BDD 全部 approved，无遗留 needs-revision 项。

## 裁剪评审

沿用上一轮判定：不裁剪任何阶段（`phases` 全量）理由充分，`risk_level: high` 定级合理（详见上一轮 P1-review.md 裁剪评审节，本轮未发现该部分被修订触及）。

## 返回主 Agent

File: /home/kity/oclab/agate/.worktrees/agate-TAG0012/agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P1-review.md
Status: approved
