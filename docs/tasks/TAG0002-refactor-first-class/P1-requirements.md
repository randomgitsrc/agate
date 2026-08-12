---
phase: P1
task_id: TAG0002-refactor-first-class
type: problems
parent: P0-brief.md
trace_id: TAG0002-P1-20260812
status: draft
created: 2026-08-12
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium             # 触及 gate 脚本行为 + 协议文档横切 + 向后兼容性要求 + 需回填验证；非破坏性（缺省行为不变）故不置 high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]   # 全流程，无裁剪（理由见 §5 裁剪说明）
packages: [agate]              # 协议本体单一包（改的是 worktree 的 agate/）
domains: [backend, cli]        # backend=check-gate.sh P6 分支/一致性检查/bats 测试；cli=orchestrator 读取层（P1 卡片样例、P6 卡片口径、verifier 派发）。无 frontend、无 security
---

# TAG0002 — 重构一等任务（Phase A）：P1 需求基线

> 输入：P0-brief.md（任务简报/风险/约束）+ P1-dispatch-context-analyst.md（派发指引）+ AGENTS.md（项目约定）+ docs/reviews/review-design-20260812-1428.md（方案己 Phase A §3/§5——任务内容来源）。
> 角色：analyst（需求质疑，见 `~/.agate/assets/execution-roles/analyst.md`）。
> 范围说明：本任务改造对象是 **worktree 的 `agate/`（协议本体）**，不是 `~/.agate`（稳定版开发工具，禁止改动）。本基线定义"做什么 + 做完什么样算对"，不写实现方案（P2 的活）。本任务为**功能型任务**（为协议新增"重构一等任务"机制），自身不声明 `change_type: refactor`。

## 1. 需求复述

### 1.1 一句话需求

把"重构"升级为 agate 的一等任务类型：任务在 P1 需求基线上声明 `change_type: refactor`，P6 验收改走"**行为不变 + 全量回归全绿 + 关键路径验收**"口径（禁止伪造功能 BDD），`check-gate.sh` P6 分支按 `change_type` 分流。机制是把 agate 已发生 20 次（19 次不挂任务编号）的既有重构实践纳入轨道，**不是引入新行为**。

### 1.2 已确认决策（来自 review-design 方案己 Phase A §5.3，作为需求输入，不得推翻）

1. **P1 加字段**：`P1-requirements.md` frontmatter 新增 `change_type: refactor` 字段，重构类任务在需求基线上声明类型。
2. **P6 口径分支**：`phase-cards/P6-acceptance.md` 增加 refactor 口径分支——验收证据 = 行为不变 + 全量回归全绿 + 关键路径验收，**禁止伪造功能 BDD**。
3. **gate 分流**：`check-gate.sh` P6 分支按 `change_type` 分流，refactor 任务走回归口径而非功能 BDD 口径。
4. **回填验收**：用 agate 已有的一次真实重构（如 `refactor: orchestrator-template 相关`）回填走一遍完整流程，确认 P6 口径可用。
5. **止损**：若回填发现 refactor 口径与既有 P6 gate 冲突难以调和 → 停，重新设计而非硬塞（P0 known_risks[0]，本节作为边界条件，不在 BDD 中强行验收）。

### 1.3 改动面（主 Agent 已核实，本基线确认覆盖完整范围）

| 改动面 | 现状（已查证） | 本任务需要什么 |
|---|---|---|
| P1-requirements.md frontmatter | 无 `change_type` 字段（P1 卡片样例只有 risk_level/phases/packages/domains） | 可声明 `change_type: refactor`，且缺省行为不变 |
| P6-acceptance.md | 第 4 行仅有 `no_behavior_change 可简化（快速验收）`，**无 refactor 独立分支** | 增加 refactor 口径分支（行为不变 + 全量回归全绿 + 关键路径验收，禁止伪造功能 BDD） |
| check-gate.sh P6 分支 | L292-322：frontmatter pass/fail 汇总 + 证据目录非空，**无 change_type 分流** | 按 change_type 分流：refactor 任务走回归口径，缺省走功能口径 |
| P3 测试设计 | P3 卡片要求测试用例与 BDD 1:1 映射 | refactor 任务无新功能 BDD，测试设计需为**回归测试**口径（不新增行为断言） |
| 协议一致性 | check-protocol-consistency.py 含 P6/no_behavior_change 锚点（L463 等） | 新增 refactor 口径后 0 ERROR，不产生 MISALIGNED |
| bats 测试 | `agate/tests/unit/check-gate.bats` 等 | 新增 check-gate.sh P6 分流用例（P0-brief 声明的 test_cmd） |

## 2. 隐含需求识别

### 2.1 refactor 口径 ≠ no_behavior_change（等价性确认结论）——known_risks[2] 的直接回应

**结论：不等价，需独立分支。**

- `no_behavior_change` 是**影响声明**（"预期无行为变更"）→ 当前语义仅是"P6 可简化（快速验收）"。它是历史遗留泄压阀，无结构化验收口径，`check-gate.sh` P6 分支根本不读取该字段，只存在于文档措辞与 check-pruning 错误文案中。
- `change_type: refactor` 是**任务类型声明** → 决定 P6 验收口径（行为不变 + 全量回归全绿 + 关键路径验收）与 gate 分流，是 gate 驱动的结构化字段。
- **语义方向相反**：重构恰恰因为存在行为回归风险，**需要**全量回归验证，不能声明 no_behavior_change 走"快速验收"；而能放心声明 no_behavior_change 的微调（如改配置）不是重构。
- 关系：互补不替代。`no_behavior_change` 保留给非 refactor 的小改动；两者不得混用（见 BDD-6）。

### 2.2 向后兼容（缺省 = 功能口径）——兼容维度

既有任务目录、协议模板、bats fixture 均无 `change_type` 字段。新增字段后，**未声明 change_type 的任务必须走改造前的功能 BDD 口径**，否则会破坏全部存量任务与既有测试（631 用例全绿基线）。

### 2.3 P3 回归测试设计——known_risks[3] 的直接回应

refactor 任务**无新功能 BDD**，P3 测试用例若强制 1:1 映射"新行为断言"会卡死。需求：refactor 任务的 P3 测试设计口径 = **回归测试**（复用/保留既有测试用例，不新增行为断言，验证重构后行为不变），P3 卡片/派发指引需同步说明以免 test-designer 按功能口径设计而卡死。**该需求由 BDD-8 锚定**（见 §3.4），P6 验收逐条对照时可据此判定回归口径是否落地。

### 2.4 BDD 编号机制兼容——边界维度

check-p6-provenance.sh 审计 3 要求 P1 含 `#### BDD-NN`（≥1）且 P6 PASS+FAIL ≥ P1 BDD 数。refactor 任务**仍须满足该机制，不豁免**——只是 BDD 性质从"新增功能断言"变为"关键路径行为不变断言"。若为 refactor 豁免 BDD 编号，会击穿 provenance 审计的统一基线，属范围蔓延，不做。

### 2.5 协议一致性检查同步——多端维度

P6 卡片新增 refactor 口径分支后，check-protocol-consistency.py 的 P6 相关锚点/关键词（含 no_behavior_change 表述处）必须同步校准，否则 CI consistency 检查 0 ERROR 目标失败。WORKFLOW.md / state-machine.md 中 P6 不可裁剪的表述与 refactor 口径不得冲突（refactor 口径是"换口径"不是"裁 P6"）。

### 2.6 机制可发现性——多端维度

新字段与口径必须对**消费方可见**：P1 卡片 frontmatter 样例注明 `change_type` 字段及取值；verifier 角色/P6 派发指引注明 refactor 口径（否则 analyst 不知道可声明、verifier 不知道按什么口径验收，机制形同虚设）。这是"机制被真正使用"的前提，不是额外负担。

### 2.7 流程负担最小化（重构流程不比直接改更麻烦）——known_risks[1] 的直接回应

止损 §6.1.1：若重构走协议比直接 commit 更麻烦，机制失败。需求：refactor 任务**不新增任何文书负担**——不强制审计、不要求伪造功能 BDD、不新增阶段。成本与普通任务一致，只是 P6 口径换成回归口径。

### 2.8 禁止伪造功能 BDD 的可观测锚点——诚实标注判定边界

"伪造功能 BDD"在语义层面无法完全机器判定（LIMITATIONS 局限 3）。需求不假装能封死，而是把验收锚点放到**客观证据**上：全量回归运行结果 + 关键路径验收 PASS 必须作为 refactor 验收证据存在，从而压缩"靠编功能 BDD 蒙混"的空间。判定边界诚实标注，不为此新增检测军备竞赛（§6.1.4 原则）。

## 3. BDD 验收条件

### 3.1 功能组 A：change_type 声明（P1 层）

#### BDD-1: P1 需求基线可声明 change_type: refactor 且被协议认可
- Given 一份 P1-requirements.md，其 frontmatter 声明 `change_type: refactor`
- When 对该任务目录执行 P1 验收 gate
- Then gate 通过且不因该字段报错，任务可正常推进到 P2

#### BDD-2: 未声明 change_type 的任务验收行为与改造前完全一致（向后兼容）
- Given 一份 P1-requirements.md 未声明 change_type（缺省）
- When 该任务按既有流程走完 P1-P6 验收
- Then 其 P6 验收判定口径与改造前一致（功能 BDD 计数 + 证据目录检查），不受新增字段影响

### 3.2 功能组 B：P6 refactor 验收口径

#### BDD-3: refactor 任务按回归口径验收，无需伪造功能 BDD 即可通过
- Given 一个 change_type: refactor 的任务，其 P6 验收报告含全量回归全绿结果与关键路径验收 PASS，且全程未新增任何功能性质 BDD
- When 对该任务执行 P6 验收 gate
- Then gate 通过，不因"无功能 BDD"而拦截

#### BDD-4: 全量回归未全绿 → refactor 验收不通过（回归是硬性组成）
- Given 一个 change_type: refactor 的任务，其关键路径验收 PASS 但其回归运行结果存在失败项
- When 对该任务执行 P6 验收 gate
- Then gate 不通过，关键路径 PASS 不能豁免回归失败

#### BDD-5: refactor 口径文档明确禁止伪造功能 BDD
- Given 一个 change_type: refactor 的任务进入 P6 验收
- When verifier 依据 P6 验收口径文档执行验收
- Then 文档明确约束验收证据为行为不变 + 全量回归全绿 + 关键路径验收，并明确禁止为凑验收数量新增功能性质 BDD

#### BDD-6: refactor 口径独立于 no_behavior_change，不混用不降级
- Given 一个 change_type: refactor 的任务（无论其是否声明 no_behavior_change）
- When 对该任务执行 P6 验收 gate
- Then 验收口径始终为 refactor 口径（行为不变 + 全量回归全绿 + 关键路径验收），no_behavior_change 既不豁免回归证据、也不改变 refactor 判定

### 3.3 功能组 C：机制可用性（回填验证）

#### BDD-7: 真实历史重构按 refactor 类型回填走完 P1-P6，全程 gate 通过且未被强制伪造
- Given agate 一次真实历史重构（如 orchestrator-template 相关重构）被回填声明为 change_type: refactor 的完整任务
- When 该任务按 P1-P6 流程完整走一遍
- Then 各阶段 gate 均可正常通过，且全程未被强制新增功能 BDD 或额外功能测试（重构流程不比直接改更麻烦）

### 3.4 功能组 D：P3 回归测试设计（known_risks[3] 锚点）

#### BDD-8: refactor 任务的 P3 测试设计为回归测试口径，P3 卡片/派发指引含回归口径说明且可被 P6 验收
- Given 一个 change_type: refactor 的任务进入 P3 测试设计，其需求基线无新功能 BDD（无需伪造）
- When test-designer 依据 P3 测试设计指引为该任务设计测试用例
- Then 测试设计为回归测试口径（复用/保留既有用例、不新增功能行为断言），且 P3 卡片/派发指引已明确写入该回归口径说明，可被 P6 验收逐条对照（不是 test-designer 即兴改编的产物）

## 4. 待确认清单

[NO_NEED_CONFIRM]

- [SUGGEST: refactor 口径采用独立分支，不等价于 no_behavior_change。理由：no_behavior_change 是"影响声明"（触发简化验收、无 gate 分流），change_type 是"任务类型声明"（触发结构化回归口径、gate 分流）；重构恰因存在行为回归风险而需要回归验证而非简化验收。no_behavior_change 保留给非 refactor 微调；长期可评估将其 deprecate 归并入 change_type（超出 Phase A 范围，本任务不做）]
- [SUGGEST: refactor 任务不豁免 BDD 编号机制（P1 仍须 ≥1 条 BDD + P6 逐条对照），BDD 性质限定为"关键路径行为不变断言"。理由：豁免会击穿 check-p6-provenance 审计 3 的统一基线，属范围蔓延]
- [SUGGEST: P3 卡片/派发指引需同步回归测试口径说明（2.3）。理由：否则 test-designer 按功能 BDD 1:1 口径设计会因 refactor 无新行为断言而卡死；这是口径落地的必要条件，不是新阶段]

## 5. 裁剪说明

**全流程 P1-P8，无裁剪。** 理由：

- **P2 不可裁**：`change_type` 字段取值设计、P6 口径分支措辞、gate 分流点的判定细节是真实设计决策，需要候选方案与独立评审。
- **P3 不可裁**：risk_level=medium；check-gate.sh P6 分流是真实脚本逻辑变更，须先写失败 bats 测试（AGENTS.md 工作流：先加失败测试确认红）。
- **P4/P5 不可裁**：交付底线——gate 脚本 + 协议卡片 + 测试是本任务可发布产物。
- **P6 不可裁**：验收含回填验证（BDD-7），是本任务质量最后防线。
- **P7 不可裁**：改动横切 P1 卡片/P6 卡片/check-gate.sh/tests/consistency 检查，需一致性交叉核对。
- **P8 不可裁**：本任务产出是 agate 新协议版本的一部分，需版本发布流程。
- **跳过风险评估**：无裁剪，不适用。缺省行为由 BDD-2 保证，非破坏性变更。

## 6. 能力需求声明

```yaml
capability_requirements:
  - need: bash 脚本能力（check-gate.sh P6 分流逻辑 + bats fixture）
    why: gate 分流是本任务核心交付物，协议既有脚本全为 bash 实现
    available:
      - "worktree 环境 bash（既有 check-gate.sh / check-pruning.sh 同语言）"
    status: available

  - need: python3 + pyyaml（协议一致性检查）
    why: P5 需对 P6 卡片/check-gate.sh 变更跑 check-protocol-consistency.py 确认 0 ERROR
    available:
      - "Python 3.12 + pyyaml（agate-state-yaml-check.py 在用，已核实）"
    status: available

  - need: bats 测试框架
    why: P3/P5/P6 验证 check-gate.sh P6 分流新增用例与既有 631 用例回归
    available:
      - "bats ≥1.2.0（worktree 环境已核实，P0-brief test_cmd 基线）"
    status: available

  - need: shellcheck
    why: P5 对改动的 .sh 脚本做静态检查
    available:
      - "shellcheck（worktree 环境已核实）"
    status: available
```

本任务无能力缺口（capability_requirements 全部 available）。非 UI 任务，不需要浏览器/视觉能力，无 `requires_minimal_validation`。

## 参考

- 任务简报：P0-brief.md（重构一等任务 Phase A、known_risks 四项、env_constraints）
- 派发指引：P1-dispatch-context-analyst.md（目标/约束/上游关联/输入文件）
- 背景设计：docs/reviews/review-design-20260812-1428.md（方案己 Phase A §3/§5，止损 §6.1.1/§6.1.4）
- 现状代码：`agate/scripts/check-gate.sh`（P6 分支 L292-322）、`agate/scripts/check-p6-provenance.sh`（审计 3 BDD 对照）、`agate/scripts/check-pruning.sh`（no_behavior_change 历史语义）、`agate/phase-cards/P6-acceptance.md`、`agate/phase-cards/P3-tdd.md`、`agate/phase-cards/P1-requirements.md`、`agate/scripts/check-protocol-consistency.py`
