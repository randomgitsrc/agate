---
phase: P1
task_id: T001
type: review
parent: P1-requirements.md
trace_id: T001-P1-review-20260809
status: approved
created: 2026-08-09
agent: requirements-review
---

# T001 — P1 需求基线独立评审（requirements-review）

> 被评审对象：`P1-requirements.md`（analyst 产出）
> 评审依据：P0-brief.md（A+B+C+D 范围 / 9 条硬约束 / 流 D 硬切）、可行性评估 `/tmp/opencode/feasibility.md`（§1 字段清单 / §2.2 半结构化 / §5 风险 / §6 路线）、HANDOFF-V2.0.md、P1-dispatch-context-requirements-review.md（派发指引，优先级最高）
> 结论：**approved**（含 3 条非阻塞 FIND，交由 analyst 酌情修正，不影响推进）

## 0. 客观查证结果（派发指引要求独立核实，不轻信 analyst 自述）

| 待查证事实 | P1 声明 | 独立核实 | 结论 |
|-----------|---------|---------|------|
| count-tests.sh 基线 | 594（sanity 6 另计，F9/BDD-11）| worktree 实跑 `bash agate/tests/scripts/count-tests.sh` = **594** | ✅ 一致 |
| CHECK 9 锚点表条数 | 37 条（F10/BDD-13）| python3 AST 解析 `SCRIPT_ALIGNMENT_ANCHORS` = **37 items**，内容含 risk_level/coupling_checklist/internal_only/PROD_TOUCHED/NEED_CONFIRM/DESIGN_GAP/ui_affected 等旧关键词 | ✅ 一致 |
| gate_commands 读取工具数 | 4 个（F13 上下文/BDD-15）| grep 确认 `agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-read-p5-commands.py` / `agate-gate-p5-count.py` 存在并被 check-gate.sh:161/194、check-tdd-red.sh:57、agate-capture-env-baseline.sh:25 调用 | ✅ 一致 |
| 受影响测试规模 | 355 个 @test / 15 个测试文件（占 594 的 60%，F9）| 汇总可行性附录 = **355 / 15 个文件** | ✅ 一致 |
| 环境能力 | pyyaml / bats 1.10.0 / shellcheck（§8）| pyyaml 6.0.1、bats 1.10.0、shellcheck 0.9.0 均可用 | ✅ 一致 |
| 迁移字段清单与可行性 §1/§2.2 一致 | P1 12 项 + P2 4 项；gate_commands/files_to_read/env_constraints/minimal_validation/implementation_dir/capability_requirements 不迁移（§1）| 与可行性 §1.2（P1 字段表）、§1.4（P2 字段表）、§2.2 逐项比对一致；与 P0-brief 流 A 字段清单逐项一致 | ✅ 一致 |
| 摩擦清单代码引用 | F17 check-changelog.sh:14 `grep -oE 'T[0-9]+'`；F18 agate-state-yaml-check.py:39 `^T\d+$`；F5 check-gate.sh:106 candidate_count；F13 check-gate.sh:259 BLOCKER 计数行 | 逐行核实代码 | ✅ 一致 |

## 1. BDD 评审（28 条逐条判定）

> 覆盖维度标注约定：数据=数据格式/字段/迁移；前端=UI/交互；多端=工具↔脚本↔gate 契约/接口；边界=异常格式/非法值/编码/缺失；兼容=旧版本/旧格式/降级/自举。
> 本任务无 UI（P0-brief §环境自检 ui_affected: false），故前端维度为 N/A，未出现"漏了前端"问题。

- **BDD-1** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓
- **BDD-2** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-3** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-4** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-5** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-6** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-7** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓
- **BDD-8** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓
- **BDD-9** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 兼容✓
- **BDD-10** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 兼容✓
- **BDD-11** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓（测试基线）
- **BDD-12** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-13** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓
- **BDD-14** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓（语义边界声明）
- **BDD-15** [流 A] 可二值判定 ✓ 单一 GWT ✓。维度：多端✓ 兼容✓
- **BDD-16** [流 B] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓
- **BDD-17** [流 B] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓ 边界✓
- **BDD-18** [流 A→B 边界] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 边界✓
- **BDD-19** [流 B] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓
- **BDD-20** [流 B] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 多端✓
- **BDD-21** [流 C] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 兼容✓
- **BDD-22** [流 C] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓
- **BDD-23** [流 C] 可二值判定 ✓ 单一 GWT ✓。维度：兼容✓ 数据✓
- **BDD-24** [流 C] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓
- **BDD-25** [流 D] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 兼容✓
- **BDD-26** [流 D] 可二值判定 ✓ 单一 GWT ✓。维度：数据✓ 兼容✓ 边界✓
- **BDD-27** [流 D] 可二值判定 ✓ 单一 GWT ✓。维度：多端✓ 数据✓
- **BDD-28** [流 D 边界/自举] 可二值判定 ✓ 单一 GWT ✓。维度：兼容✓

**编号格式**：BDD-1..28 全部使用 `#### BDD-NN:` 标准格式、连续不跳号（grep 实测 28 条连续）。✓

**单一 GWT 抽查**：逐条核对均为单一 Given / When / Then，无合并场景，无"⚠️ 调整/部分通过"中间态。✓

**跨条一致性**：BDD-9（旧格式回退）与 BDD-10（frontmatter 优先）的 Given 由隐含需求 #1 的判别契约显式互斥（frontmatter 含迁移字段=新格式 → BDD-6/10 场景；不含=旧格式 → BDD-9 场景），无矛盾。BDD-5 枚举非法值与 BDD-2 全角冒号场景不重叠。✓

## 2. 四流覆盖（派发指引重点 2）

| 流 | 覆盖 BDD | 覆盖面 | 是否只是表面提一句 |
|----|---------|--------|------------------|
| **流 A**（P1/P2 迁移+校验器+双读+硬约束）| BDD-1..15（15 条）| 字段读取 / 全角冒号 / phases 双格式 / 缩进 / 枚举 / 必填 / 错误定位 / pre-commit 同机制 / 双读回退 / frontmatter 优先 / 测试数 / 嵌套深度 / 一致性 / 语义边界 / gate_commands 无回归 | 否，最厚实 |
| **流 B**（P6/P7 结果结构化）| BDD-16..20（5 条）| P6 汇总 frontmatter / P6 行格式从严 / 总结行不计入 / P7 BLOCKER 计数 / P7 DESIGN_GAP 配对 | 否，逐摩擦对应 |
| **流 C**（标记状态收尾）| BDD-21..24（4 条）| 标记已解决状态 / SCOPE_RESOLVED 闭环 / 发现性标记保持散文 / 角色卡模板 | 否 |
| **流 D**（编号硬切）| BDD-25..28（4 条）| TAG0001 接受 / T001 拒绝（硬切）/ check-changelog 完整 task_id / 自举约束 | 否 |

结论：四流全部有实质 BDD 覆盖，无遗漏、无"表面提一句"。✓

## 3. 语义真实性边界（派发指引重点 3）

- 28 条 BDD 全部只断言"解析可靠性 / 格式校验 / 编号规则正确校验"，**无一条声称"gate 变强"或能发现内容造假**。✓
- BDD-14 显式要求 P2-design.md 声明"结构化提高解析可靠性、不改变 gate 对内容真实性的判断"，与硬约束 6 对应。✓
- §9 语义真实性边界清单完整（结构化解决 12 项 / 不解决 3 项 / 保障机制不变 / BDD 不得声称 gate 变强）。✓
- 隐含需求 #7（BDD-14）与 P0-brief known_risks 第 9 条一致。✓

## 4. 隐含需求覆盖（隐含需求 16 条逐条核对）

| # | 隐含需求 | 载体 | 判定 |
|---|---------|------|------|
| 1 | 在途任务双读兼容 | BDD-9/10 + §3 判别契约 | ✅ 覆盖 |
| 2 | frontmatter schema 校验器新交付物 | BDD-6/7/8 | ✅ 覆盖 |
| 3 | CHECK 9 锚点表 37 条重新校准 | BDD-13 | ✅ 覆盖 |
| 4 | 测试 fixture 大规模重写且用例数不漂移 | BDD-11 | ✅ 覆盖 |
| 5 | 角色卡/模板贴可复制模板 | BDD-24 | ✅ 覆盖 |
| 6 | frontmatter 禁止 >3 层嵌套 | BDD-12 | ✅ 覆盖 |
| 7 | 语义真实性边界写入设计文档 | BDD-14 | ✅ 覆盖 |
| 8 | agate-md-field-get.py 核心改造点 | §1 形态描述（实现载体，非行为）| ✅ 已声明载体 |
| 9 | P5_DATA CACHE_KEY 验证 | §3 #9 明确"P4/P5 实现回归检查项，无对应 BDD" | ✅ 显式声明 |
| 10 | P6 折中增强行格式校验器 | BDD-17/18 | ✅ 覆盖 |
| 11 | P6 dispatch-context 预判白名单同步 | §3 #11 描述，属实现回归项 | ✅ 已声明（非阻塞）|
| 12 | 发现性标记保持散文边界 | BDD-22/23 | ✅ 覆盖 |
| 13 | 流 D 自举（T001 用 v0.35）| BDD-28 + §1 自举原则 | ✅ 覆盖 |
| 14 | check-changelog TASK_ID_SHORT 派生连锁 | BDD-27 | ✅ 覆盖 |
| 15 | 版本发布流程（badge/CHANGELOG/tag/--no-ff）| §3 #15 + §6 P8 理由 | ✅ 已声明（P8 载体）|
| 16 | 双工作区隔离 | §3 #16 + P0 env_constraints | ✅ 已声明（环境约束）|

## 5. 与 P0-brief 一致性（派发指引重点 5）

- **范围 A+B+C+D**：§1 范围说明显式"A+B+C+D 四流全做（非仅流 A）"，与 P0-brief 扩展一致。✓
- **9 条硬约束**：每条均有对应 BDD 或显式声明（1→BDD-11，2→BDD-12，3→BDD-24，4→BDD-9/10，5→BDD-13，6→BDD-14，7→BDD-15，8→§6 P3 理由"新格式 fixture + 校验器测试先行"，9→BDD-25/26/27/28）。✓
- **流 D 硬切**：§1"流 D 硬切"段落 + BDD-26 显式"不兼容旧格式（硬切，无双格式过渡）"+ F19，与 P0-brief §扩展硬切决策一致。✓
- **自举原则**（派发指引重点 6）：§1 自举原则、隐含需求 #13、BDD-28 三处一致声明"本 task T001 按 v0.35 产出、新编号规则是产物不是运行时约束"。✓

## 6. 裁剪评审

- **无裁剪**：`phases: [P1..P8]` 全流程，`跳过风险: 本次不裁剪任何阶段`。P2/P3/P4/P5/P6/P7/P8 逐阶段给出不裁剪理由（P2 核心设计 / P3 风险 high 需 TDD / P4-P8 交付底线），理由充分。✓
- **risk_level: high**：与"数据格式变更 + gate 自我改造 + 355 测试换血 + 流 D 硬切"的实际风险匹配。✓
- **capability_requirements 三态**：3 项均 `available`，无 `GAP`、无 `supplementable`，与实测环境（pyyaml/bats/shellcheck 可用）一致。✓

## 7. P1 纯净性

- BDD 不绑定类名/属性名/具体实现；唯一涉及的工具名（BDD-15 的 4 个 gate_commands 工具、BDD-8 的 check-state-yaml.sh 机制）是既有产物的非回归契约，非新增设计。✓
- §1"重构后目标形态"引用可行性 Option A 是范围陈述（P0-brief 已定），非 P1 混入 P2 设计。✓

## 8. FIND 列表（全部非阻塞，不阻碍 P1 推进；建议 analyst 酌情修正）

- **FIND-1（建议）**：§4 编号说明写"连续编号 BDD-1..27"，但实际有 BDD-1..28（§6/§9 均写 28 条）。应为 "BDD-1..28"。属笔误，不影响 gate（gate 只查 `#### BDD-NN:` 锚点存在性）。
- **FIND-2（建议）**：摩擦清单表 F13（P7 BLOCKER）的"对应 BDD"列写 BDD-18，但 BDD-18 实际是"P6 总结行不计入（F11 消除）"；F13 应指向 BDD-19（P7 BLOCKER/DEVIATION 计数结构化）。同理 F11 的"对应 BDD"列为 BDD-16/17，可补 BDD-18（BDD-18 标题已自注"（F11 消除）"）。建议交叉核对摩擦↔BDD 追溯列，避免 P6/P7 验收时按表索引错位。
- **FIND-3（建议）**：`domains: [backend, cli]` 中 `cli` 不在阶段卡片/role-system.md 的机械映射枚举（backend/frontend/mcp/security）内。影响：P2 评审机械映射（C8）只认 backend/frontend/mcp/security，`cli` 不会触发额外评审——但因已含 backend 且 risk_level=high 必派 plan-eng-review，实际评审覆盖不受影响。建议在 §7 注释说明 `cli` 是 backend 域内子语义，或改 `domains: [backend]` 以对齐协议枚举。

## 9. 评审结论

**status: approved**

- 28 条 BDD（BDD-1..BDD-28）全部可二值判定、单一 GWT、格式合规、连续编号。
- A/B/C/D 四流全部实质覆盖，无遗漏流。
- 语义真实性边界全程守住（只断言解析可靠性/格式校验，不断言 gate 变强）。
- 关键数字独立核实一致（594 / 37 锚点 / 4 工具 / 355 测试 / 环境能力 / 迁移字段清单）。
- 隐含需求 16 条全部有载体；与 P0-brief 范围、9 条硬约束、流 D 硬切决策、自举原则一致。
- 3 条 FIND 均非阻塞，不构成 rejected 理由，由主 Agent 酌情回派 analyst 修正后即可推进 P2。

> 提示主 Agent：gate 规则要求 P1-review.md 的 `agent` 非 main（此处 = requirements-review，满足），且 BDD 编号锚点已含于 §1。预跑 `check-gate.sh P1` 预期 exit 2（主 Agent 自判路径）。
