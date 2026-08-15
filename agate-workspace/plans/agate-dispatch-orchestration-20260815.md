# subagent 派发编排机制（全阶段）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **⚠️ 阶段完整性声明**：本计划是 RM-AG0016 的**参考输入**，不替代 agate 任务流程。执行本条目时仍须走完整 P0-P8（P1 需求基线 + BDD → P2 设计 → …），P1/P2 须产出当前任务自己的需求基线与设计（可引用本计划内容，不可跳过阶段）。本计划只提供"做什么、怎么落地"的既有分析，不豁免任务质量 gate。

**Goal:** 建立统一的 subagent 派发编排机制，覆盖全阶段（P1-P8），解决"工作量高时单 subagent 过载卡死"问题。核心：工作量评估 → 五模式编排（单发/静态拆批/并行/先理解后拆/串行链）→ 并行规则统一。消灭 P1/P2 的编排空白，统一 P3-P6 分散的"按包并行"，为 P8 多包发布提供拆批路径。

**关联 roadmap**：RM-AG0016（backlog，用户确认合并"批次粒度传导" + "派发编排" + "全阶段"为一）。

**Architecture:** 在 dispatch-protocol.md 现有「任务粒度指引」（L639）基础上升级为「派发编排机制」权威节；P2-design.md 新增 `dispatch_plan:` 机器字段（gate 可校验）；各阶段卡片统一引用权威节（删除各自分散的"按包拆分并行"定义，保留阶段特定约束如 P5 端口隔离、P6 证据并行模式）；dispatch-prompt.md 内联粒度兜底约束。

**Tech Stack:** Python 3.8+（脚本/测试）+ pytest。

**背景（已核实）**：
- 协议现状：`任务粒度指引` 只存于 dispatch-protocol.md L639-663，只覆盖"产出/输入数量上限"，无任何其他文件引用（P2-design.md / architect.md / 派发模板均无）
- P3/P4/P5/P6 各自有"按包拆分并行"节（独立定义，无统一机制）；P7 明确不拆分（L99）；**P1/P2 无任何编排机制**
- TAG0010 批次 0 卡死（用户中止）：P2 设计阶段 architect 单发扛"理解+设计+批次规划"全部工作，无编排机制
- TAG0011 拆 19 批后零卡死：证明"拆批 + 主 Agent 批验证"是有效模式，但无协议机制固化
- 并行规则缺口：无并行上限（平台并发 + 主 Agent 上下文）、无并行失败处理（失败批单独 retry vs 全批重跑）、无共享文件统一约束（仅 P4 有）

**范围决策**：
- 模式 4（先理解后拆）为新增编排形态，不改变既有"按包并行"的能力，只统一其规则
- 各阶段卡片的"按包拆分并行"节保留阶段特定约束（P5 端口隔离 / P6 证据并行 / P7 不拆分），统一部分（并行上限/失败处理/共享文件）迁移到权威节
- 不改状态机（P3/P4/P5/P6 gate 仍是该阶段门槛命令，拆分不改变 phase 语义，dispatch-protocol L654 已有此规则）

---

## File Structure

- **Modify** `agate/dispatch-protocol.md:639` — 「任务粒度指引」升级为「派发编排机制」权威节（工作量评估 + 五模式 + 并行规则 + 模式 4 流程）
- **Modify** `agate/phase-cards/P2-design.md` — 新增 `dispatch_plan:` 机器字段说明（frontmatter + 正文样例）
- **Modify** `agate/phase-cards/P1-requirements.md` — 加"编排模式"引用（复杂需求可先理解后拆）
- **Modify** `agate/phase-cards/P3-tdd.md` / `P4-implementation.md` / `P5-verification.md` / `P6-acceptance.md` — "按包拆分并行"节改为引用权威节 + 保留阶段特定约束
- **Modify** `agate/phase-cards/P8-release.md` — 加"多包发布可拆批"提示
- **Modify** `agate/assets/templates/dispatch-prompt.md` — 内联粒度兜底约束（产出>3 或输入>5 必须分批或说明）
- **Modify** `agate/assets/execution-roles/architect.md` — 批次设计强制节（P2 含多子任务时输出 `dispatch_plan:`）
- **Modify** `agate/scripts/check-gate.py` — P2 gate 校验 `dispatch_plan:` 字段存在性/一致性（可选，与 candidate_count 同级）
- **Test** `agate/tests/unit/test_check_gate.py` — P2 `dispatch_plan:` 字段校验测试
- **Test** `agate/tests/unit/test_dispatch_orchestration.py`（新建）— 工作量评估/模式决策/并行规则逻辑测试
- **Modify** `agate/tests/README.md` — 用例数
- **Modify** `README.md`, `CHANGELOG.md`, `agate/UPGRADING.md` — 协议变更记录

---

### Task 1: TDD — 写失败测试（先红）

**Files:** `agate/tests/unit/test_dispatch_orchestration.py`（新建）

**背景**：`dispatch_plan:` 字段是新协议契约，先写测试定义预期行为（TDD 红灯）。

**`dispatch_plan:` 字段契约（先定义，B2 修复）**：
- **序列化格式**：P2-design.md **frontmatter 单行 flow YAML**，与 candidate_count 同级：
  ```yaml
  dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: B1, complexity: medium}, {id: B2, complexity: low}]}
  ```
  无批次时 `dispatch_plan: {mode: single}`（模式 1/5 可省略 batches）
- **mode 枚举**：`single` / `static-batch` / `parallel` / `recon-then-split` / `serial`
- **读取机制**：新增 `agate-md-field-get.py` op `dispatch_plan`（该工具已支持 yaml 解析，L56/L124，返回 JSON 字符串）；check-gate.py P2 分支通过 subprocess 调 `agate-md-field-get.py dispatch_plan` 读取（**与 pass/blocker_count 同路径**，即 `_md_field_get` 子进程模式，N8 修复——candidate_count 是正则逐行读取，非子进程，不引用它）。`_frontmatter_field` 是单行 sed 提取，对嵌套 YAML 不可用——**不复用**。
- **frontmatter schema**：`dispatch_plan` **完全不入 `agate-frontmatter-check.py` 的 P2 schema**（B3 方案 c）——类型校验由 check-gate 经 op 返回 JSON 后做。理由：flow YAML dict 会被 frontmatter-check 的 `types: str` 校验误拦（isinstance str 对 dict 失败，pre-commit-gate.py L313-316 拦截 commit），不入 schema 才能保证"缺字段等同现状"向后兼容。全部校验走 check-gate + op，与现有 P1/P6/P7 子进程读取模式一致。
- **op 注册与输出**（N9 修复）：`dispatch_plan` 须注册入 `KNOWN_OPS`（否则 `_md_field_get` 视为缺失 exit 2 → gate 跳过 → `test_mode_valid` 静默不报 ERROR 而红）；新增 dict → `json.dumps` 输出路径（当前 `_format_value` 对 dict 走 `str()` Python repr 单引号，非 JSON，须加 JSON 序列化分支）
- **向后兼容**：`dispatch_plan:` 可选——无此字段时 P2 gate 行为完全等同现状（不拦截、不 WARNING）

**Steps:**
- [ ] 新建 `agate/tests/unit/test_dispatch_orchestration.py`
- [ ] 测试用例（Task 2 实现范围 = **全部五条**，B1 闭合）：
  - `test_dispatch_plan_required_fields`：含 `dispatch_plan:` 时，op 返回 JSON 含 mode 且 mode ∈ 枚举；parallel_limit 存在时 ≥ 1
  - `test_dispatch_plan_mode_valid`：mode 非法值（如 `xyz`）→ P2 gate 报 ERROR exit 1
  - `test_dispatch_plan_batch_granularity`：static-batch/parallel 模式，batches 存在时各 batch 含 id + complexity 且 complexity ∈ {low, medium, high}；模式 1/5 可无 batches
  - `test_dispatch_plan_parallel_limit`：static-batch/parallel 模式 batch 数 ≤ parallel_limit（默认 3，N10 术语统一）
  - `test_dispatch_plan_optional`：无 `dispatch_plan:` 时 P2 gate 行为等同现状（exit 2 通过，无额外输出）——含"等同现状"断言（比较有无该字段时的输出）
- [ ] **负向用例**（B1 扩展）：
  - `test_dispatch_plan_malformed_yaml`：frontmatter 含 `dispatch_plan:` 但 YAML 解析失败 → 不误拦（op 返回空 → 按缺字段处理），且不崩溃
  - `test_dispatch_plan_parallel_limit_zero`：parallel_limit=0 → 报 ERROR（非法，至少 1）
  - `test_dispatch_plan_batch_missing_complexity`：batch 缺 complexity → 报 ERROR
- [ ] 确认测试红（字段契约未实现，`agate-md-field-get.py` 无 dispatch_plan op，check-gate P2 不读此字段）

---

### Task 2: 实现 `dispatch_plan:` 读取 + P2 gate 校验（改绿）

**Files:** `agate/scripts/agate-md-field-get.py`, `agate/scripts/check-gate.py`（**不改** `agate-frontmatter-check.py`——B3 方案 c：`dispatch_plan` 不入 frontmatter-check schema）

**Steps:**
- [ ] `agate-md-field-get.py`：新增 op `dispatch_plan` 并注册入 `KNOWN_OPS`——从 frontmatter 读 `dispatch_plan` 键，yaml 解析后 `json.dumps` 输出（复用 L124 yaml 解析路径；`_format_value` 增 dict→json.dumps 分支；格式错/无此键 → 输出空 + exit 0）
- [ ] `check-gate.py` P2 分支（L323 附近）：调 `agate-md-field-get.py dispatch_plan` 读取（subprocess，env FILE=P2-design.md，与 pass/blocker_count 的 `_md_field_get` 子进程模式同路径）→ 解析 JSON 校验：
  - mode ∈ 枚举，非法 → stderr ERROR + return 1
  - parallel_limit 存在且 < 1 → ERROR + return 1
  - static-batch/parallel 模式：batches 各 batch 含 id + complexity ∈ 三值，缺 → ERROR + return 1；batch 数 > parallel_limit（默认 3）→ ERROR + return 1
  - 模式 1/5：batches 可选，不校验
  - op 返回空（无字段/解析失败）→ 完全跳过，行为等同现状
- [ ] 跑 `python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py` 确认绿（八条全过，B1 闭合）

---

### Task 3: dispatch-protocol.md 「派发编排机制」权威节

**Files:** `agate/dispatch-protocol.md:639`

**Steps:**
- [ ] 把「任务粒度指引」节改写为「派发编排机制」节，结构：
  1. **工作量评估**：五维评级表（产出规模/输入规模/改动性质/耦合度/认知负荷）→ low/medium/high
  2. **五模式编排**：模式 1 单发 / 模式 2 静态拆批 / 模式 3 并行 / 模式 4 先理解后拆 / 模式 5 串行链，每个模式给"何时用 + 流程"
  3. **模式 4 流程**（重点新增）：侦察 subagent（读全貌产出拆分方案）→ 执行（按方案并行/串行）→ 合并（轻量拼装主 Agent/单 subagent；重量整合派整合 subagent）
  4. **并行规则**：上限默认 3 / 失败批单独 retry（**与 state-machine retries[Pn] 对齐：并行批 retry 事件按"每批独立计入"或"整组计 1 次"二选一，默认整组计 1 次，N3 修复**）/ 共享文件统一后处理（原 P4 约束推广，**P6 例外：走自身汇总 verifier，N4 修复**）
  5. **全阶段适用表**：P1-P8 各阶段的编排模式参考（P1/P2 表述修正——P2 = 单发 + dispatch_plan 产出，非 P2 自身拆分，N1 修复；P7 = 模式 1 单发 + 输入豁免特例，非串行链，N2 修复；P8 多包拆批需含合并机制，N5 修复）
- [ ] 保留原任务粒度指引的既有有效规则（输入/产出数量上限、拆批判据、T016/T026 教训）
- [ ] **同步内联派发 prompt 节**（N6 修复）：dispatch-prompt.md 的内联兜底约束须同时写入 dispatch-protocol.md 的「派发 prompt 模板」节（权威源），防止双源漂移
- [ ] 确认 CHECK 3（硬编码行号引用）不误报——更新节后跑 `python3 agate/scripts/check-protocol-consistency.py`

---

### Task 4: 各阶段卡片统一引用

**Files:** `agate/phase-cards/P1-requirements.md`, `P2-design.md`, `P3-tdd.md`, `P4-implementation.md`, `P5-verification.md`, `P6-acceptance.md`, `P7-consistency.md`, `P8-release.md`

**Steps:**
- [ ] P2-design.md：新增 `dispatch_plan:` 机器字段说明（frontmatter 单行 flow 样例，与 candidate_count 同级，字段契约见 Task 1）
- [ ] P1-requirements.md：加"编排模式"引用——复杂需求（多来源/多模块）可先派侦察 subagent 再拆，**合并语义（BDD 全局编号、包归属去重）在 P1 侦察产出中定义**（N1 修复）
- [ ] P3/P4/P5/P6 卡片：把各自"按包拆分并行"节改为"→ 见 dispatch-protocol「派发编排机制」并行规则"，**完整保留阶段特定约束**（N7 修复——逐卡片核对：P4 基础设施隔离全组 L111-117 + "无法确定共享改动→串行安全默认值" L109 + 共享文件后处理；P5 端口/数据库/环境变量/临时文件隔离 L121-127；P6 证据并行 + 汇总 verifier 整合唯一 P6-acceptance.md）
- [ ] P7 卡片：确认"不拆分"理由保留，改为"模式 1 单发 + 输入数量豁免特例"（N2 修复）
- [ ] P8-release.md：加"多包发布可拆批（模式 2/3）"，**并定义合并机制**：多 releaser 并行各写 P8-release-{pkg}.md → 主 Agent 派合并 subagent 整合唯一 P8-release.md（N5 修复）
- [ ] 跑 consistency 确认 0 ERROR

---

### Task 5: architect.md 批次设计强制节 + 派发模板兜底（含权威源同步）

**Files:** `agate/assets/execution-roles/architect.md`, `agate/assets/templates/dispatch-prompt.md`, `agate/dispatch-protocol.md`

**Steps:**
- [ ] architect.md：新增"批次设计"强制节——P2 方案含多个独立子任务时，P2-design.md 必须输出 `dispatch_plan:`（模式 + 批次表 + 并行上限）；强调"批次粒度受工作量评估约束，high 复杂度必须拆"
- [ ] dispatch-prompt.md：内联粒度兜底——"产出文件 >3 或输入 >5 个时，必须分批派发或明确说明为何不分批"
- [ ] **同步权威源（N6 修复）**：dispatch-prompt.md 头部声明"与 dispatch-protocol.md「派发 prompt 模板」节保持同步"——内联兜底须**同时写入** dispatch-protocol.md 的「派发 prompt 模板」内联节，防双源漂移
- [ ] 跑 `python3 -m pytest agate/tests/` 确认无回归

---

### Task 6: 全量验证

**Steps:**
- [ ] `python3 -m pytest agate/tests/ -q` → 全绿（新增 test_dispatch_orchestration + 既有 751+ 用例）
- [ ] `python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR
- [ ] `bash agate/tests/scripts/count-tests.sh` → 用例数 ≥ 751 不漂移
- [ ] 更新 `agate/tests/README.md` 用例计数表
- [ ] `README.md` badge / `CHANGELOG.md` / `agate/UPGRADING.md` 记录协议变更
- [ ] ruff check（新增 py 文件）
- [ ] 模式 4 验证：dispatch-protocol「模式 4 流程」节含可运行的文档样例（侦察产出拆分方案 → 执行 → 合并），由 consistency CHECK 2 校验样例引用路径存在（模式 4 是编排行为，非脚本逻辑，以文档样例 + 引用检查兜底）

---

## 验收标准（gate）

1. `dispatch_plan:` 字段契约定义完整（序列化格式 + mode 枚举 + 读取 op + KNOWN_OPS 注册 + JSON 输出路径 + 不入 frontmatter-check schema，见 Task 1/2），P2 gate 校验存在时正确拦截非法值（mode 非法/parallel_limit<1/batch 缺 complexity/batch 数超限），缺字段向后兼容（行为等同现状）
2. dispatch-protocol「派发编排机制」节含：工作量评估五维表 + 五模式定义 + 模式 4 流程（含合并语义）+ 并行规则（含 retry 预算对齐 N3 / P6 例外 N4）+ 全阶段适用表（P1/P2 表述 N1 / P7 归类 N2 / P8 合并 N5）
3. 各阶段卡片不再有重复的"按包拆分并行"定义（统一引用权威节，阶段特定约束完整保留 N7——逐卡片核对 P4 隔离全组/P5 基础设施/P6 证据+汇总 verifier）
4. architect.md 有批次设计强制节；dispatch-prompt.md 与 dispatch-protocol.md 内联节同步有粒度兜底（N6）
5. pytest 全绿（含 8 条 dispatch_plan 用例：5 正向 + 3 负向）+ consistency 0 ERROR + 用例数不漂移
6. self-gate：本任务改 `agate/*.md` + `agate/scripts/*.py` + phase-cards → commit message 需含 `self-gate-review:` 路径，派发 protocol-alignment-review

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 协议文档改动大，consistency 误报 | 每改一节跑一次 consistency，增量修复 |
| P2 gate 新字段校验引入误拦 | `dispatch_plan:` 可选字段（缺失不拦截），向后兼容；负向用例锁定非法值拦截行为 |
| 各阶段卡片删除分散定义后丢阶段约束 | 迁移时逐卡片核对（N7 清单），阶段特定约束（端口/证据/共享文件/隔离全组）显式保留在卡片 |
| `agate-md-field-get.py` 新 op 与既有 op 冲突 | op 命名唯一（dispatch_plan），复用既有 yaml 解析路径，不触碰其他 op 行为 |
| 改动触发 self-gate（改 agate/*.md + scripts/*.py）| 按 SELF-GATE.md 流程：派发 protocol-alignment-review + commit message 带 `self-gate-review:` |
