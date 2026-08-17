---
phase: P2
task_id: TAG0006-ui-ux-quality
type: design
parent: P1-requirements.md
trace_id: TAG0006-P2-20260817
status: draft
created: 2026-08-17
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 4
packages: [agate-docs, agate-scripts-py, agate-tests]
domains: [frontend, backend]
ui_affected: false
---

> 注意：ui_affected: false 是本任务自身声明（本任务无 UI 产物）；方案内部定义的"业务任务 ui_affected: true 时的机制"是设计内容，不影响本任务自身 frontmatter。

# P2 方案设计 — agate UI/UX 验收质量机制

> 上游：P1-requirements.md（17 条 BDD 已 approved：原 15 条 + SCOPE+ 增补 BDD-16/17 与 BDD-1/2/4/6/9/10/13 扩展）+ P1-review.md（含 SCOPE+ 复审记录闭合）
> 本方案设计的是**协议机制增强**：改造对象是 worktree 里 `agate/` 的协议文档 + gate 脚本 + 单测，不是业务 UI 应用。
> **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 本轮为 SCOPE+ 增补轮**：在原已 approved 设计（§0-§14 全部保留）之上叠加"渲染形态分类框架 + 形态适配"层——新增 §2.15（形态声明载体/跨阶段一致/判据可量化/gate 组合）与 §2.16（P6 证据形式按形态选择），并对 §0/§2.1-§2.5/§2.8-§2.12/§5/§6/§7/§9-§11 增补标注；gate_commands（§3）与 dispatch_plan（§8，single）**不变**。

---

## 0. 影响域分析

### 0.1 改什么（机制增强落点，按 BDD 分组）

| BDD | 改动域 | 涉及文件 |
|-----|--------|---------|
| BDD-1/2/3 | P1 UX 需求基线 + vision 能力三态声明（[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] BDD-1/2 泛化为分类框架+形态适配） | analyst.md、P1 卡片、requirements-review.md、check-gate.py（gate_p1）、test_check_gate.py |
| BDD-4/5 | P2 UI 设计节（ui_affected: true 任务必含，[BASELINE_CHANGE] 泛化为形态声明+维度选择+按形态 checklist） + architect 兼任声明 | architect.md、P2 卡片、check-gate.py（gate_p2）、test_check_gate.py、agate-frontmatter-check.py、task-files.md |
| BDD-6 | plan-design-review 增视觉/交互维度 + 渲染正确性与时序维度 | plan-design-review.md、test（文档读取测试） |
| BDD-7 | Windows GUI 评估 | P2-design.md 本文件（本节） |
| BDD-8 | 影响面核对清单 | P2-design.md 本文件（本节） |
| BDD-9/10/13 | P6 双证据 + 视觉质量 checklist + 输入态人工复核（[BASELINE_CHANGE] BDD-9/10/13 扩展：证据形式按形态可选 + 渲染输出/帧序列真实视觉分析 + 动作/特效/时序类交互形态） | verifier.md、P6 卡片、check-p6-evidence.py、check-p6-provenance.py、test_check_p6_evidence.py |
| BDD-11/12 | 派发注入 + subagent 自查 | dispatch-protocol.md（A3）、dispatch-prompt.md、test_dispatch_orchestration.py |
| BDD-14 | 雷同截图降级待复核 | check-p6-evidence.py、test_check_p6_evidence.py |
| BDD-15 | 兼容回归 | 全量 pytest + consistency + count-tests 实跑 |
| BDD-16/17 [BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] | 渲染组件类/UX 交互形态维度进入 BDD 可测项 + 渲染组件类证据形式可按形态选择 | analyst.md、P1 卡片、P2 卡片、architect.md、verifier.md、vision-analyst.md、plan-design-review.md、test-designer.md、check-gate.py（gate_p1/p2）、check-p6-evidence.py、check-protocol-consistency.py、agate-frontmatter-check.py、test_check_gate.py、test_check_p6_evidence.py、test_dispatch_orchestration.py、test_review_role_docs.py、task-files.md |

### 0.2 不改什么（明确边界，降低风险）

- **不新增 designer 角色**：UI 设计节由 architect 兼任产出（BDD-5），role-system.md 角色清单不变
- **不回溯改既有 task 数据**：新检查只对"新声明"生效——P1 vision 三态声明检查只在 `domains` 含 `frontend` 时触发；P2 UI 设计节检查只在 `ui_affected: true` 时触发；既有 825 基线用例不因新增检查而变红（见 §10 兼容策略）。静态 fixtures 中 `ui-affected`/`vision-blocked` 两个 P2-design 均 `ui_affected: true` 且无 UI 设计节，但均不用于 P2 gate 测试（test_check_gate 自建 fixture，不引用静态夹具），且 P6 专用，故新 P2 检查不会命中它们（见 §2.3 兼容段）
- **不改 md5 硬阻断语义**：截图逐字节去重仍然 exit 1 硬阻断（BDD-14 只改 avg-hash 级别）
- **不改既有 P6 vision-helper/blocker_count/R1b 审计语义**：available 分支的既有流程原样保留，新机制是叠加分档
- **不改 P5 E2E 实跑门槛**：state-machine.md:101 的 ui_affected→P5 E2E 实跑不变，只补 P6 侧视觉证据
- **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 不绑定技术栈/不推翻原分类**：UX 分类框架（布局结构/渲染正确性/交互行为/动效时序/视觉呈现等）是**示例性开放集合**，WebGL/Canvas/OpenGL 等仅作举例不作绑定；原"键盘可用性/显示内容正确性/样式呈现"三类不删除——折叠为常规布局型 UI 的典型维度示例（分别对应交互行为/渲染正确性/视觉呈现维度）；原方案 A、原有 15 条 BDD 语义与既有 vision 三态/UI 设计节检查全部保留，扩展仅叠加"按形态选维度/选证据形式"的适配层
- **[BASELINE_CHANGE]** 既有任务无形态/维度声明走默认布局型行为：`ui_render_shape` 缺失 = 视为常规布局型 → 既有全部判定路径与基线一致（presence 语义，见 §2.15.1）

### 0.3 风险在哪

1. **BDD-3 P1 检查误伤既有任务**：若既有任务 P1 的 `domains` 含 frontend 但无 capability_requirements → 新增检查会 exit 1（这正好是需求要拦截的场景，但需确认基线任务无此形态——基线 fixtures 的 P1 均无 domains:frontend，见 §5 兼容验证）
2. **BDD-4 P2 检查误伤既有 P2 fixture**：既有 fixture `ui-affected/P2-design.md` 与 `vision-blocked/P2-design.md` 均声明 `ui_affected: true` 但无 UI 设计节 → 若被 P2 gate 测试消费会变红。对策：触发条件**仅为 P2 自身 `ui_affected: true`**（不读取 P1 capabilities，与 §2.3 一致）——经核实无 P2 gate 测试引用 fixtures/ui-affected 或 fixtures/vision-blocked（test_check_gate 自建 fixture），故这些 fixture 不会被 P2 检查命中，兼容成立；新增专门 fixture 覆盖 BDD-4
3. **BDD-14 降级判定强度**：avg-hash 重复从 WARNING 升级为"降级待复核"判定后，若无人工复核记录则阻断——需保证有合法复核路径（P6-acceptance.md 记"人工复核记录"字段），否则误伤合法行为差异类 BDD 截图视觉相同的场景
4. **文档联动 45 文件**：一处改动须同步全部联动点（见 §6 影响面核对清单），P7 一致性检查按清单核
5. **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 渲染形态声明缺失导致的歧义**：新机制要求 P1 声明形态/维度、P2 UI 设计节复用、P6 按形态选证据——任一环节漏声明会造成适配层失效。缓解：形态声明为 presence 语义可空字段（缺失 = 布局型默认，不红基线）；P1/P2 各加一次 gate 校验（缺形态声明/维度选择 → exit 1，BDD-4/16）；跨阶段一致性由 P7 一致性检查按 I14 核对（P2 形态声明必须与 P1 一致）
6. **[BASELINE_CHANGE]** 渲染组件类证据形式（帧序列/时序截图/渲染输出对比）无法被既有 check-p6-evidence.py 类型识别 → 误拦或漏检。缓解：R1a 证据类型检查扩展为新的形式清单（帧序列目录结构/时序截图后缀/渲染输出 diff 锚点），见 §2.16；P3 单测构造帧序列 fixture 断言识别
7. **[BASELINE_CHANGE]** 判据不可量化风险：渲染正确性/时序/动效类 BDD 若用主观词，P6 二值判定失效。缓解：verifier.md/P6 卡片写入"渲染正确性以渲染结果对比、时序以帧时序对齐、动效以过渡/动画行为断言为判据"的可量化条文（BDD-2/16），requirements-review 打回带主观词的 UX BDD

---

## 1. 候选方案

### 1.1 候选方案 A（选定）：三态能力声明的"硬声明 + 降级链"双层机制

**核心思路**：P1 必须显式声明 vision 能力三态（available/supplementable/GAP），gate 校验声明合法性；P6 按声明档位消费证据，GAP 走降级链。

```
P1: capability_requirements 含视觉条目 + status ∈ {available, supplementable, GAP}
     ↓  check-gate.py P1 校验（缺失/非法 → exit 1）
P2: ui_affected: true → P2-design.md 必含 UI 设计节（布局/交互/视觉 checklist）
     ↓  check-gate.py P2 校验（缺节 → exit 1）
P6: 按 P1 声明的三态分档消费视觉证据
     available/supplementable → vision YAML 引用 + blocker_count=0
     GAP → 像素检测 + 人工复核记录（不要求 vision YAML）
     ↓  check-p6-evidence.py 校验（avg-hash 重复 → 降级待复核须含人工复核记录）
```

- **优点**：需求与实施完全对齐 15 条 BDD 的分组逻辑；能力边界诚实（不写死视觉工具）；GAP 有明确出口（人工复核记录）不会死锁
- **风险**：改动面大（P1/P2/P6 三阶段 + 4 脚本 + 测试）；降级链依赖文档条文约束 verifier 行为（self-authored gate 固有局限）
- **工作量**：中（文档条文 + 4 处 gate 逻辑 + 单测）

### 1.2 候选方案 B：仅文档层面增强，不新增 gate 检查

**核心思路**：只在 analyst.md/verifier.md/P6 卡片等文档写"应当声明/应当分档"，不新增 check-gate.py 逻辑。

- **优点**：改动小，只动文档
- **缺点**：无 gate 校验的协议要求是软约束——analyst 漏写 vision 声明、architect 漏写 UI 设计节、verifier 漏做 GAP 降级都不会被拦截（P1 I1/I2 明确要求"缺检查则 architect 可漏写"）；与 BDD-3/4 验收方式（"check-gate.py P1/P2 新增该检查 + 构造 fixture 断言 exit 1"）直接冲突
- **风险**：BDD-3/4 验收必不通过——方案 B 不可接受

### 1.3 候选方案 C：过渡灰度（gate 检查只 WARNING 不阻断）

**核心思路**：新增检查先输 WARNING（exit 2）不阻断，观察一个版本周期后再升级为硬校验。

- **优点**：对既有 pipeline 冲击最小
- **缺点**：与 BDD-3/4 验收方式冲突（需求要求"构造缺失/非法 fixture 断言 exit 1"）；灰度期协议"必须声明"实际不强制，P6 验收该 BDD 时无客观证据锚点
- **风险**：需求不满足，且 WARNING 语义在自写文件 gate 上容易被忽略（P1 已明确 BDD-3/4 要 exit 1）

### 1.4 候选方案 D：UI 设计节门禁分级（仅作对照，非独立候选）

BDD-4 要求"ui_affected: true 时缺节 → P2 gate 拦截"。对照方案：把 UI 设计节检查做成"Windows 平台分支差异检查"（跳过 Windows）——不成立，P1 明确 check-gate.py P2 新增该节检查且单测构造缺节 fixture 断言 exit 1，与平台无关。此方案不采，作为论证 BDD-4 检查必须平台无关的对照记录。

### 1.5 选择理由

**选 A（三态声明 + 双层门禁）**：三个候选对比后，A 是唯一同时满足以下条件的方案——
- 满足 BDD-3/4 验收方式（check-gate.py 新增检查 + fixture 断言 exit 1，A 天然符合，B/C 不符合）
- 满足能力边界诚实（A 的三态分档正是 RM-AG0004 的核心诉求，vision 能力不写死工具）
- 满足 GAP 不死锁（A 的"GAP → 像素检测 + 人工复核记录"在 BDD-9 已制入，A 落实该分支）
- 多方案 nudge 的价值主要是"强制走一遍'还有别的做法吗'的思考"——B（纯文档）和 C（灰度）都被需求验收方式判死，D 是平台无关性对照，故 A 是唯一真方案；此处如实标注：这是一次 nudge 驱动下的排除式选择，非稻草人陪衬

---

## 2. 设计细节（按 BDD 逐条落实）

> 每条 BDD 对应"协议条文落点 + gate 逻辑 + 单测"三件套（P1 §3 验收方式：文档含要求 + 单测覆盖）。

### 2.1 BDD-3：vision 能力三态声明的 P1 gate 检查

**协议条文落点**：
- `assets/execution-roles/analyst.md`:78-104 能力三态机制已有——补一句"`ui_affected` 任务（domains 含 frontend 或 P2 会标 ui_affected）必须在 capability_requirements 中声明视觉能力条目（`need` 命名含 visual/vision）。缺失声明即视为需求不完整，requirements-review 打回"
- `phase-cards/P1-requirements.md`:常见错误节（109 行附近）把"capability_requirements 漏声明"升级为"frontend 任务漏声明 vision 条目 → hook exit 1"

**gate 逻辑（check-gate.py gate_p1）**：
- 新增 helper `_gate_p1_vision_capability(p1_file)`：
  1. `_md_field_get("domains", p1_file)` 取 domains；若不含 `frontend` → 通过（返回 True）
  2. 提取 P1-requirements.md `capability_requirements:` 代码围栏块（```yaml ... ```）内 YAML，`yaml.safe_load` 解析，找 `need`/`name` 含 `visual|vision` 的条目（定位方式见 §5.2 minimal_validation 第 3 项）
  3. 条目缺失 → `sys.stderr.write("GATE P1: frontend 任务必须声明 vision 能力条目（capability_requirements 含 visual/vision need）")` → return 1
  4. 条目存在但 `status` 不在 {available, supplementable, GAP} → return 1
- 挂在 gate_p1 末尾（现有 return 2 之前）：失败先于 `return 2` 返回 1，通过则继续
- **兼容**：既有 fixture P1 均无 `domains: frontend`（create_task_dir 默认 P1 无 domains frontmatter，full-task/ui-affected/vision-blocked fixtures 的 P1 均无 frontend domains）→ 检查不触发，基线 825 用例不误伤

**单测（test_check_gate.py）**：
- `test_vision_1_frontend_missing_capability_exit_1`：构造 P1 fixture——`add_frontmatter_field(td/P1, "domains", "[frontend]")`、无 capability_requirements → 断言 exit 1
- `test_vision_2_frontend_invalid_status_exit_1`：domains=frontend + capability 块 status=invalid → exit 1
- `test_vision_3_frontend_valid_gap_exit_2`：domains=frontend + status: GAP → exit 2（GAP 合法声明，不阻 P1；GAP 触发的是 P6 降级链，不是 P1 拦截）
- `test_vision_4_backend_no_vision_no_fail_exit_2`：domains=backend 无 vision → 不触发（兼容基线）

### 2.2 BDD-1/2：UX 类别 BDD 基线要求

**BDD-1 落点** `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`：
- `assets/execution-roles/analyst.md` 产出规格节：新增"domains 含 frontend 的 P1 必须含至少一条 UX 类别 BDD"，并要求：①声明实际 UI/渲染形态（见 §2.15.1 载体）；②从协议 UX 分类框架（布局结构/渲染正确性/交互行为/动效时序/视觉呈现等，示例性开放集合）按形态选适用维度；③针对选中维度写至少一条可二值判定的 UX 类别 BDD（常规布局型典型维度示例：键盘可用性→交互行为、显示内容正确性→渲染正确性、样式呈现→视觉呈现）；类别写入 BDD 标题后缀（如 `BDD-3: 渲染正确性：...`），缺失形态声明/维度选择/UX BDD 时 requirements-review 打回
- `phase-cards/P1-requirements.md` 产出规格节 + 常见错误节：对应条文（含分类框架 + 形态声明要求）
- `assets/review-roles/requirements-review.md` 检查清单：新增评审要点"frontend 任务 P1 是否含形态声明 + 维度选择 + 按维度编辑的 UX 类别 BDD（分类框架口径）"

**BDD-2 落点** `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`：
- `assets/execution-roles/analyst.md` BDD 反模式自检清单（196 行附近）扩展：新增两条——"□ 若为 UX 类别 BDD，Then 子句是否可被用户可观测行为二值判定（PASS/FAIL）？"、"□ UX 类别 BDD 是否不绑定具体 CSS 类名/组件名/工具名/技术栈名（WebGL/Canvas/OpenGL 等仅举例）？"；渲染正确性/时序/动效类 BDD 另要求可量化判据（渲染结果对比/帧时序/像素或输出差异），条文写入清单（BDD-16 配套）

**gate/单测**：BDD-1/2 验收方式为"读文档确认"，不新增 gate 逻辑。单测以文档内容检查为主——新增 `test_docs_ux_bdd_requirements.py`（或在既有 test_check_protocol_consistency.py 补一致性规则）：grep analyst.md + P1 卡片含"UX 分类框架"/"渲染正确性"/"时序"等锚点词，断言存在（文档漂移保护）。一致性规则在 check-protocol-consistency.py 补：analyst.md 必须含 UX 分类框架 + 形态适配要求条文。

### 2.3 BDD-4：P2 UI 设计节 gate 检查 `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**协议条文落点**：
- `assets/execution-roles/architect.md`：
  - §输出（39 行 ui_affected 字段说明处）补：`ui_affected: true` 时 P2-design.md 必须含「UI 设计」节（`## UI 设计`），节内含渲染形态声明 + 维度选择 + 按形态适配的 checklist（布局/交互/视觉 或 渲染正确性/动效时序 等适用维度，完整结构见 §2.4），由 architect 兼任产出
  - 补 UI 设计节结构规格（见 §2.4）
- `phase-cards/P2-design.md`：产出规格 + gate 规则补"ui_affected: true → UI 设计节检查（含形态声明 + 维度选择）"
- `assets/templates/task-files.md` P2 模板（227-311 行）补 UI 设计节样例（含形态声明行 + 布局/渲染组件/时序三类 checklist 样例）
- `agate-frontmatter-check.py`:56-74 P2 schema 可加**可选字段**（如 `ui_design_section: true`，bool，可选，presence 语义）——供 P2 gate 读取，不破坏旧 fixture（旧 P2-design 无该字段 = 未声明 UI 节 → 检查仅在 frontmatter `ui_affected: true` 且（无该字段或缺节）时触发）

**gate 逻辑（check-gate.py gate_p2）**：
- 新增 helper `_gate_p2_ui_design_section(p2_file)`：
  1. `_md_field_get("ui_affected", p2_file)`；非 `true` → 通过
  2. 解析 P2-design.md：要求含 `## UI 设计`（或 `### UI 设计`）节标题
  3. 节内须出现**渲染形态声明**关键词（`渲染形态` 或 `适用维度`）至少一次（BDD-4 ①，缺失 → 拦截）
  4. 按形态分支校验 checklist 存在性：
     - 常规布局型（形态声明缺失或声明 layout/布局）：三组锚点关键词 布局/组合（layout/布局）、交互（interaction/交互）、视觉（visual/视觉）各至少一次
     - 渲染组件型（形态声明含 渲染组件/视觉渲染/画布/图表/模型/特效/地图/数字地球 等关键词或选中渲染正确性/动效时序维度）：出现渲染正确性（渲染|渲染正确性|capture）或动效时序（时序|动效|animation|frame）维度锚点。⚠️ **启发非绑定注**：「画布/图表/模型/特效/地图/数字地球」等为**产品域启发词**（仅用于识别可能的渲染组件形态、触发本分支），**不构成技术栈要求**——形态判定以 P1 `ui_render_shape` 规范值 / §2.15.2 维度选择为准，命中启发词 ≠ 绑定任何技术栈/框架（符合「不写死技术栈」约束 4）
     - 维度适用性判定口径见 §2.15.2（"维度不适用"显式声明即可豁免该维度 checklist 关键词）
  5. 缺节标题或形态声明或按形态判定的维度锚点全部缺失 → `sys.stderr.write("GATE P2: ui_affected: true 但缺 UI 设计节（须含渲染形态声明 + 维度选择 + 按形态 checklist）")` → return 1
- **形态一致性交叉校验**（BDD-4① 与 P1 形态一致）：P1-requirements.md frontmatter 声明 `ui_render_shape` / `ui_ux_dimensions` 时，P2 UI 设计节的形态声明行必须与 P1 一致——匹配语义为**规范化值比对**：P2 声明行解析出规范 token（声明行含规范值 layout/render_component/temporal_effects 直接取用；仅含中文标签「布局型/渲染组件型/时序特效型」时经 §2.15.1 同义映射表归一化为规范值）→ 与 P1 `ui_render_shape` 字段值比对，**相同规范值即一致**（词汇表与同义映射表见 §2.15.1，杜绝 ASCII 规范值与中文标签字面永不匹配的误拦）——不一致或 P1 有声明而 P2 缺形态声明行 → return 1
- **兼容**：既有 fixture 中 full-task/high-risk/paused-task 的 P2-design 均 `ui_affected: false` → 不触发；`ui-affected/P2-design.md` 与 `vision-blocked/P2-design.md` 两个均为 `ui_affected: true` 且无 UI 设计节 → 若被 P2 gate 测试消费会命中（触发条件仅为 P2 自身 `ui_affected: true`，与 §0.3 风险 2 对齐）。但**二者均不用于 P2 gate 测试**：test_check_gate 用自建 fixture、不引用静态夹具目录；二者均 P6 专用（ui-affected 测 P6 双证据路径、vision-blocked 测 P6 GAP/blocker 降级演示）→ 新 P2 检查不会命中，兼容成立。已核实 test_check_gate 无静态夹具引用

**单测（test_check_gate.py）**：
- `test_ui_design_1_ui_true_missing_section_exit_1`：构造 ui_affected:true 无 UI 设计节 P2 → exit 1
- `test_ui_design_2_ui_true_full_section_exit_2`：含 ## UI 设计 + 渲染形态声明 + 布局/交互/视觉关键词 → exit 2
- `test_ui_design_3_ui_true_missing_keyword_exit_1`：含节标题但缺"视觉"关键词 → exit 1
- `test_ui_design_4_ui_false_no_section_exit_2`：ui_affected:false 无节 → 不触发 exit 2（兼容）
- `test_ui_design_5_ui_true_render_comp_section_exit_2` `[BASELINE_CHANGE]`：渲染组件型形态声明（渲染正确性/动效时序维度 checklist）→ exit 2
- `test_ui_design_6_ui_true_missing_shape_decl_exit_1` `[BASELINE_CHANGE]`：含节标题但缺渲染形态声明/维度选择 → exit 1
- `test_ui_design_7_ui_true_p1_p2_shape_mismatch_exit_1` `[BASELINE_CHANGE]`：P1 frontmatter 声明 ui_render_shape 与 P2 形态声明行不一致 → exit 1
- `test_ui_design_8_ui_true_p1_p2_shape_canonical_match_exit_2` `[BASELINE_CHANGE]`：P1 `ui_render_shape: render_component` + P2 声明行 `渲染形态: render_component（渲染组件型）` → 规范值一致 → exit 2（**词汇表匹配正例**，固化 §2.15.1 规范化值比对语义）
- `test_ui_design_9_ui_true_p1_p2_shape_synonym_match_exit_2` `[BASELINE_CHANGE]`：P1 `ui_render_shape: render_component` + P2 声明行仅用中文标签 `渲染形态: 渲染组件型` → 经同义映射表归一化为 render_component → 一致 → exit 2（**同义映射正例**，防中文标签被字面匹配误拦）

### 2.4 BDD-5：UI 设计节规格（architect 兼任产出） `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**architect.md 补充的 UI 设计节结构规格（协议条文内容）**：

```markdown
## UI 设计（ui_affected: true 时 P2-design.md 必含）

### 渲染形态声明（必填，与 P1 形态声明一致，BDD-4 ①）
- 渲染形态: <规范形态值词汇表（§2.15.1）中的规范值 + 中文注释；示例：layout（布局型） / render_component（渲染组件型，仅举例 OpenGL/WebGL/Canvas/图表/模型/特效/地图/数字地球） / temporal_effects（时序特效型），开放声明不绑定技术栈>
- 适用维度: <按形态选用的 UX 维度清单；常规布局型为 布局结构/交互行为/视觉呈现，渲染组件型可为 渲染正确性/动效时序/交互行为 等>

### 布局 checklist（布局结构维度——常规布局型必选）
- [ ] 页面/组件层级结构（Header/Content/Footer 或等效分区）已描述
- [ ] 关键区域占位关系（主区/侧栏/弹层）已描述
- [ ] 桌面与移动两档 viewport 布局均说明（对应 P3 的 desktop_1280x800 / mobile_390x844 截图）

### 交互 checklist（交互行为维度——常规布局型必选；渲染组件型按适用维度增补手势/动作交互）
- [ ] 键盘可达性（Tab 顺序 / 焦点可见 / 回车激活）已覆盖或声明"不适用"
- [ ] 输入态变化（输入 → 界面状态变化）已定义或声明"无输入态用例"
- [ ] 反馈（loading/error/empty/disable 态）已覆盖
- [ ] 输入态变化类用例若存在：宣称需人工复核（对应 P6 BDD-13）
- [ ] [渲染组件型可选] 手势/动作交互（旋转/缩放/拖拽/平移）已定义触发方式与响应断言

### 视觉 checklist（视觉呈现维度——常规布局型必选）
- [ ] 颜色/对比度（主色/背景色/WCAG AA 对比）已说明
- [ ] 字体层级（字号/字重）与间距节奏已说明
- [ ] 组件一致性（圆角/阴影/图标风格）已说明

### 渲染正确性 checklist（渲染组件型形态适用维度，对应 BDD-16）
- [ ] 渲染管线/绘制配置（画布尺寸与分辨率、投影与坐标系）已说明
- [ ] 判定锚点已定义：渲染结果对比（参考图/diff 阈值）或输出数据断言
- [ ] **颜色/光照/材质等视觉保真项归入参考对比锚点**：以渲染结果对比参考图覆盖（diff 阈值量化），不得仅以"绘制成功/渲染出图"断言保真——防 implementer 误以为渲染组件无需视觉保真项
- [ ] 图层顺序/加载状态（场景加载完成/异步资源就绪）已说明
- [ ] 特效/动效的触发与结束状态（起始帧/结束帧/还原）已定义

### 动效时序 checklist（时序特效型形态适用维度，对应 BDD-16）
- [ ] 帧/时序采样点（帧捕获位置或时间戳断言）已定义
- [ ] 动画关键帧与过渡时序（起止状态 + 时长或帧数）已说明
- [ ] 动效结束判定（回到静止态/目标态）已定义且可量化
```

- 节内渲染形态声明**必须与 P1 形态声明一致**（跨阶段一致 I14）——P2 gate 校验两者匹配（见 §2.15.1）
- checklist 结构按形态适配：常规布局型必含布局/交互/视觉三类；渲染组件型/时序特效型按适用维度启用渲染正确性/动效时序 checklist——**不要求渲染组件型任务写布局/视觉三类**（维度适用即写，不适用的维度声明"维度不适用"即可，BDD-4 ③ 的"适配机制存在"是硬要求，具体维度组合由任务形态决定）

**role-system.md**：确认不新增 designer 角色——在角色清单表后补一行注明"UI 设计节由 architect 兼任产出（P2），不新增角色"。

### 2.5 BDD-6：plan-design-review 增视觉/交互维度 + 渲染正确性与时序维度 `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**plan-design-review.md 维度表（13-21 行）扩容**，五维 → 七维（常规布局型）+ 渲染正确性与时序维度（渲染组件型按形态启用，变相第八维）：

| 维度（现有） | 维度（新增后） |
|------|------|
| 交互状态覆盖率 | **交互状态覆盖率**（保留，措辞微调：交互设计维度） |
| AI Slop 风险 | AI Slop 风险（保留） |
| 移动端考虑 | 移动端考虑（保留） |
| 可访问性 | **可访问性 / 键盘可达**（升级，含键盘导航 + 输入态反馈） |
| 组件完整性 | 组件完整性（保留） |
| — | **视觉设计**（新增：布局一致性／颜色对比度／字体层级／组件一致性等，0-10 可判定评分） |
| — | **交互设计细节**（新增：输入态反馈／禁用态／过渡动画等，0-10 可判定评分） |
| — | **渲染正确性与时序**（新增，渲染组件类形态启用：渲染结果正确性／帧时序／动效质量，0-10 可判定评分，见下） |

每新增维度配 0-10 评分项："""视觉设计：布局一致性（0-2）／颜色与对比度（0-3）／字体与间距（0-3）／组件一致性（0-2）"""（合计 0-10）；"""交互设计细节：输入态反馈（0-4）／键盘可达与焦点（0-3）／过渡与禁用态（0-3）"""；"""渲染正确性与时序：渲染结果正确性（0-4：渲染输出与预期一致/参考对比，锚点=渲染结果对比或输出断言，0-4 按 BDD 判据是否定义量化锚点评分）／帧时序（0-3：帧/时间戳采样点定义、动画或加载时序断言）／动效质量（0-3：过渡/动画关键帧与结束状态定义，0-3 按动效 BDD 判据可判定性评分）"""。

- 适用口径：**frontend 任务评审时启用**（受评对象是 P2-design.md 的 UI 设计节）。UI 设计节缺失时该维度直接 0 分（联动 BDD-4）
- **渲染正确性与时序维度启用规则**：受评任务 P1/P2 声明渲染组件/时序特效类形态（或维度选择含渲染正确性/动效时序）时启用；常规布局型任务不启用该维（避免维度不适用的打分噪音）
- **七维边界注（写入 plan-design-review.md 维度表，防 double count）**：**"交互状态覆盖率"= 状态存在性**（审「loading/error/empty/edge 等状态是否被 spec 覆盖」），**"交互设计细节"= 状态内实现质量**（审「输入态反馈/过渡/禁用态等具体实现细节质量」）——前者回答"各状态有没有被覆盖"，后者回答"覆盖到的状态实现得够不够好"，同一问题不允许跨两维重复打分
- 同时 `role-system.md` 中 role 表 plan-design-review 行（45 行）职责描述同步（"spec 交互完整性 + 视觉设计 + 渲染形态适配"）

**单测**：新增 `tests/unit/test_review_role_docs.py`（读 plan-design-review.md 断言含"视觉设计"与"交互设计"与"渲染正确性与时序"维度名），并入一致性检查（check-protocol-consistency.py 增加该文件关键词锚点规则）。

### 2.6 BDD-7：Windows GUI 自动化框架评估

见 §4（本文件独立小节，调研结论"保持现状"）。

### 2.7 BDD-8：影响面核对清单

见 §6（与 P1 影响面清单对齐核对）。

### 2.8 BDD-9：P6 双证据 + 视觉质量 checklist（vision 三态分档 + 证据形式按形态可选） `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**verifier.md 改动**：
- §UI 任务追加约束（104-108 行）改写：`ui_affected: true` 时每条 UI 类 PASS 必须同时含——运行时证据（截图/行为日志/帧序列/渲染输出） + 视觉证据；视觉证据形式按任务**渲染形态**选择（常规布局型：截图/行为日志；渲染组件型可选用帧序列、时序截图、渲染输出对比——形式清单见 §2.16）且按 P1 声明的 vision 能力状态分档：
  - `available`/`supplementable` → vision YAML 引用 `(vision: vision-reports/bxx.yaml)`（含既有 UI 追加约束：blocker_count=0、≤1KB 处理）
  - `GAP` → 降级为"像素检测 + 人工复核记录"：PASS 行引 `(screenshots/bxx.png)` + `(manual-review: review-bxx.md)`，**不要求 vision YAML 引用**（渲染组件型 GAP 任务：帧序列/渲染输出差异检测替代人工截图，仍须人工复核记录）
  - 读取三态声明来源：P1-requirements.md capability_requirements（视觉条目 status）
- **无视觉能力声明的默认语义（兼容回归锚点）**：P1 的 capability_requirements 无 `need` 含 visual/vision 条目（无视觉能力声明）时 → 视为 **available 语义**——保留既有 R1b 强制（截图 PASS 必须引 vision YAML）与 blocker_count=0 流程；**GAP 分支仅在 P1 显式声明 status: GAP 的任务触发**，不因"无声明"落入 GAP 放行。该默认保证既有无声明任务（如 test_pv_11/12/13、integration T086 等 create_task_dir 默认 P1）的 P6 行为与基线完全一致（BDD-15 不红），并有兼容回归用例固化（test_vision_none_1）
- §P6 处理流程（175-182 行）补第 0.5 步：先读 P1 声明的渲染形态 + vision 三态 → 决定证据路径（截图/帧序列/时序截图/渲染输出对比）与 vision 分档
- §UI 条件的处理流程 补"视觉质量 checklist 核对"：逐条对照 P1 UX 类别 BDD + P2 UI 设计节（渲染形态声明 + 维度选择的 checklist），核对渲染正确性/时序/动效判据是否有量化锚点，在验收报告中记录 checklist 核对结果（每项 checked/unchecked + 依据），不只写"渲染成功"

**P6 卡片改动**：
- 产出规格补双证据分档条文 + vision 能力三态读取来源 + 证据形式按形态可选清单（`帧序列/时序截图/渲染输出对比` 见 §2.16）
- gate 规则段补：GAP 分支的视觉证据为"像素检测 + 人工复核记录"，check-p6-evidence.py 校验；帧序列/渲染输出对比证据的目录与锚点校验（见 §2.16）

**check-p6-evidence.py 改动**：`ui_affected == "true"` 时读取 P1 的 vision 三态声明 + 渲染形态，GAP 分支豁免"含截图 PASS 必须引 vision YAML"这一层（该层现由 check-p6-provenance R1b 执行，需同步：GAP 分支改为校验"人工复核记录文件存在"）；渲染组件型证据类型识别（`frames/` 帧序列目录、`renders/` 渲染输出目录、时序截图后缀 `_t1/_t2` 等）纳入非纯文本证据判定（§2.16）。⚠️ 注意：本脚本本身不校验 vision YAML 引用存在性（那是 provenance），本任务只新增 GAP 分支"人工复核记录文件"存在性检查（截图 PASS + 复核记录引用 → 放行）。

**check-p6-provenance.py 改动（核对 + GAP 分支）**：R1b 审计在 P1 声明 vision=GAP 且该任务已验证降级路径时，不强制 vision YAML（改为要求"人工复核记录"被 PASS 引用）。改动点：读取 P1 capability 视觉条目 status，GAP → R1b 对该任务的截图 PASS 放宽 vision 强制。

**单测（test_check_p6_evidence.py + test_check_p6_provenance.py）**：
- `test_vision_gap_1_evidence_manual_review_exit_0`：P1 vision=GAP + 截图 + `manual-review` 文件被引用 → exit 0
- `test_vision_gap_2_evidence_missing_review_exit_1`：P1 vision=GAP + 截图但不引复核文件 → exit 1
- `test_vision_avail_1_evidence_no_vision_yaml_exit_1`：P1 vision=available + 截图 PASS 无 vision YAML → exit 1（既有 R1b 语义保持，新增回归保护）
- `test_vision_none_1_no_decl_evidence_no_vision_yaml_exit_1`：**P1 无视觉能力声明（capability_requirements 无 need 含 visual/vision）+ ui_affected:true + 截图 PASS 无 vision YAML → exit 1**（无声明默认 available 语义——不落入 GAP 放行；兼容回归，守护 BDD-15 基线，对应 test_pv_11 现有断言）
- `test_vision_docs_1_verifier_has_triple_state`：读 verifier.md 断言含 available/supplementable/GAP 分档条文（文档漂移保护）
- `test_render_evid_1_frame_sequence_recognized_exit_0` `[BASELINE_CHANGE]`：渲染组件型（P1 形态声明=渲染组件）+ `P6-evidence/frames/` 帧序列目录 + 帧文件非空 → exit 0（证据类型识别扩展）
- `test_render_evid_2_render_output_compare_exit_0` `[BASELINE_CHANGE]`：`P6-evidence/renders/` 渲染输出对比（输出 PNG + diff 锚点文件）→ exit 0
- `test_render_evid_3_frame_seq_pure_text_exit_1` `[BASELINE_CHANGE]`：声明渲染组件型但证据全为纯文本 .md/.txt → exit 1（非纯文本证据门槛按形态适配）

### 2.9 BDD-10：vision available 时 P6 必须真实视觉分析（形式可含渲染输出对比/帧序列） `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**落点**：
- P6 卡片「vision-helper 结论绑定」（126-130 行）已有"可用 blocker_count > 0 时不能仅用程序化指标反驳"。补充条文："P1 声明 visual 能力 status=available 时，P6 必须执行真实视觉分析（截图/帧序列/渲染输出按所选证据形式 → 结构化描述 → 判定），不得仅以 naturalWidth>0 / complete=true / HTTP 200 / 像素方差断言视觉 PASS"；渲染组件型任务按所选证据形式执行：帧序列逐帧描述 → 时序/动效判定、渲染输出对比 → 结果差异描述 → 判定（anchor 为 BDD 量化判据）
- verifier.md §行为验证证据优先级（78-80 行）标注 vision-analyst 视觉分析为 available 分支的硬性证据；视觉分析对象扩展至渲染输出/帧序列（不写死工具；像素/场景差异结构化描述，vision-analyst.md 同步）

**单测**：`test_vision_docs_2_p6_card_real_analysis`（读 P6 卡片含"真实视觉分析"条文）；不新增 gate 逻辑（真实视觉分析由 verifier 行为执行，gate 以 evidence 存在性兜底，BDD-9 已覆盖证据必需性）。

> 注：无声明任务按 §2.8 默认 available 语义**仅在证据路径**（check-p6-* R1b 强制 + blocker_count）生效；BDD-10 的"真实视觉分析"条文面向 **P1 显式声明 status=available** 的任务，不回溯强加于既有无声明任务（避免基线行为变更，与 BDD-15 兼容）。

### 2.10 BDD-11：supplementable 时派发 prompt 注入获取指引

**落点**：
- `dispatch-protocol.md` A3 节（1184-1204 行）扩展：补充"当 P1 capability_requirements 中视觉条目 status=supplementable 且该任务的 P2 `ui_affected: true` 时，P6 派发 prompt 必须注入视觉能力获取指引（如 '可调用 vision-analyst 角色 / 视觉分析 skill，先自查能否调用，再向主 Agent 报告'）"。A3 现有规则是"读 P1 提取 supplementable → 注入对应阶段 prompt"，本扩展绑定 UI 视觉语境（把 A3 的通用规则显式应用到 P6 verifier/vision-analyst 派发）
- `assets/templates/dispatch-prompt.md`：能力补充说明节（67-69 行）注明"vision supplementable 时该节必含获取方式 + 自查要求"

**单测**：`tests/unit/test_dispatch_orchestration.py` 补用例——构造 P1 vision=supplementable + P2 ui_affected:true，断言派发 prompt 合成（如 render 函数或模板断言）含获取指引段；若无 render 函数则改为模板 grep 断言（读 dispatch-prompt.md 含"先自查能否调用视觉能力"锚点）。

### 2.11 BDD-12：派发 prompt 强制 subagent 能力自查

**落点**：`assets/templates/dispatch-prompt.md` 新增"能力自查"段（放在能力补充说明节之后）：
```
## 能力自查（强制）
若本任务可能涉及视觉能力（如 P6 验收 UI 截图 / vision-analyst 派发）：
- 先自查当前环境能否调用视觉能力（视觉模型 / skill / 图像读取工具）
- 能 → 正常执行；不能 → 明确报告[CAPABILITY_GAP]并走降级路径（文档条文/像素检测/人工复核），不静默假设
```
同时在 dispatch-protocol.md A3 节点出"派发 prompt 必须含能力自查要求"（对应 BDD-12 验收：读模板含自查要求）。

**单测**：`test_dispatch_orchestration.py` 或新增 `test_dispatch_prompt_self_check.py`——读 dispatch-prompt.md 模板断言含"先自查能否调用视觉能力"锚点。

### 2.12 BDD-13：输入态/交互形态变化类用例人工复核 `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

**"输入态/交互形态变化"判定标准（写入 verifier.md + P6 卡片）**：
```
输入态/交互形态变化类用例 = 用户输入（键盘/鼠标/粘贴/手势/拖拽）或动作/特效/时序交互导致界面状态或渲染表现变化，或有时序动效联动的用例。
判据：BDD 的 When 子句含输入动作（输入/点击/按键/滚动/手势/拖拽）或动作/特效/时序触发，且 Then 子句断言的界面状态（显示内容/样式/组件状态/渲染表现/时序状态）与该输入或触发相关。
```
- 非输入态类（静态渲染、查询结果展示）→ 不触发人工复核
- 输入态类（表单输入、键盘导航、焦点转移）→ P6 结论必须附人工复核记录
- 交互形态类（动作/特效/时序：旋转/缩放/拖拽/过渡动画/帧时序变化）→ 亦触发人工复核（BDD-16 扩展），按时序类证据（帧序列/时序截图）附复核记录

**落点**：
- verifier.md §UI 追加约束补：输入态/交互形态变化类 BDD 的 PASS/FAIL 结论必须附人工复核记录（复核人 / 复核时间 / 复核结论），不能仅由自动断言通过；判定标准见本节
- P6 卡片补对应条文 + PASS 行样例：`- PASS BDD-N: ... (screenshots/x.png) (vision: ...) 人工复核: 张三 2026-08-17 确认输入态正常`
- `assets/templates/task-files.md` P6 模板补人工复核记录样例

**单测**：`test_vision_docs_3_input_state_review`（读 verifier.md + P6 卡片含输入态判定标准条文，扩展断言含"动作/特效/时序"交互形态词）；check-p6-evidence/check-gate P6 不新增 gate（人工复核记录是 verifier 自述性质，靠文档条文约束 + P7 一致性检查兜底，符合 self-authored gate 缓解层次）。

### 2.13 BDD-14：雷同截图降级待复核

**check-p6-evidence.py avg-hash 逻辑改造（251-262 行）**：

现状：ahash 重复 → 仅 WARNING（exit 2 语义，不阻断）。
改造后：ahash 重复 → 升级为"降级待复核"判定：

```
if ahash_total > ahash_unique:
    dupes = ahash_total - ahash_unique
    检查 P6-acceptance.md 是否含"雷同截图复核记录"（锚点：`雷同截图复核` 或 `manual-review` PASS 引用）
    含 → 输出 "GATE P6-EVIDENCE: 有 N 组雷同截图，已降级待复核且含人工复核记录，放行"  → exit 0/2
    不含 → 输出 "GATE P6-EVIDENCE: 有 N 组视觉高度相似截图，未含人工复核记录 → 降级待复核失败" → exit 1
```

- **md5 硬阻断语义不变**（235-248 行保持 exit 1）
- 降级判定强度：非纯 WARNING（有复核记录才放行，无记录阻断）——满足 BDD-14"不能仅以 WARNING 放行"
- **退出码叠加顺序（GAP 降级分支 exit 0/2 与既有方差 WARNING exit 2）**：同一截图集两种判定同时命中时的优先级——① **阻断级最高**：雷同且无复核记录 → exit 1（覆盖方差 WARNING，最终 exit 1）；② 雷同有复核记录 + 该集/其他截图集存在方差 WARNING（variance_warning>0）→ **以 exit 0/2 公式中的 2 为准**（任一 WARNING 存在即汇总 exit 2，不放宽为 0）；③ 雷同有复核记录且全程无方差 WARNING → exit 0；④ 无雷同仅方差 WARNING → exit 2（现状不变，§2.14/a-hash 前置门禁不变）。实现时按"先累加 variance_warning 计数，再判断雷同阻断/放行，最后统一汇总结论 exit 码"的顺序落地，避免先返回某单一判定导致遮蔽另一判定
- ⚠️ 触发后要求 verifier 在 P6-acceptance.md 记录复核结论（复核人/时间/结论），符合 P6 卡片 122-124 行"行为差异类 BDD 视觉相同场景优先改用非截图证据"的既有指引，新增的是"若仍用截图则必须复核"的硬约束
- **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 判定域分组豁免**：雷同判定按"同 BDD 证据组"分组（§2.16）——**分组键 = bdd-id 前缀**：同一 BDD 的 帧序列 `{bdd-id}-NN` 与 时序截图 `{bdd-id}-t1..tN` **统一归入同一组、同权豁免**；组内相邻帧/相邻时刻视觉相近是动画时序正常特性，豁免降级；组间/跨 BDD 雷同仍触发降级待复核。实现时 ahash 列表按「所属 BDD（帧序列/时序截图共用 bdd-id 前缀分组）」分组后再统计 dupes，避免时序特效任务被误伤阻断（详见 §2.16）

**单测（test_check_p6_evidence.py）**：
- ⚠️ **构造前置门禁（test_ahash_* 共用）**：测试 PNG 必须同时满足 check-p6-evidence 执行序的前置——文件 **>1KB**（≤1KB 会先被"evidence 非文本"检查 exit 1）且**像素方差 ≥50**（方差<50 会先触发方差 WARNING→exit 2，遮挡 ahash 判定）；故测试 PNG 须为**非纯色图**（PIL 生成含内容/噪声/渐变图，不能纯色填充），并显式断言生成文件尺寸与方差满足门禁再进入 ahash 断言
- `test_ahash_1_duplicate_with_review_record_exit_0`：构造两张同 visual content 不同文件名截图（用 PIL 生成同像素不同编码的非纯色 PNG，或 base64 写两版，均满足 >1KB + 方差≥50）+ P6-acceptance 含"雷同截图复核"记录 → exit 0（最小验证已实测：同视觉内容不同字节 → ahash 相同、md5 不同）
- `test_ahash_2_duplicate_no_review_record_exit_1`：同上但不含复核记录 → exit 1（行为从 WARNING 改为判定）
- `test_ahash_3_no_duplicate_exit_0`：不同 visual 内容 → 不受影响
- ⚠️ Pillow 缺失时 ahash 直接 SKIP（现有行为）→ 测试用 `pytest.importorskip("PIL")` 包裹，无 Pillow 环境自动 skip（平台无关原则，不硬编码 /tmp 等路径，用 tmp_path）

### 2.14 BDD-15：兼容回归

**单测**：不新增（回归本身是执行验证，见 gate_commands）。实施后跑：全量 pytest（基线 825 + 新增用例全绿）+ `check-protocol-consistency.py` 0 ERROR + `count-tests.sh` 计数无漂移（≥749 且单调不减）。

### 2.15 SCOPE+ 形态声明载体与跨阶段一致性（BDD-1/4/16/17） `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`

> 本节目的是把 2026-08-17 范围扩展（A1 分类框架+适配 / B1 本任务内增补）落为可实施设计——定义"任务如何声明渲染形态与维度选择、跨阶段如何保持一致、gate 如何校验"，全部为**叠加层**，不推翻原方案 A 与 BDD-3/4 门禁。

#### 2.15.1 形态声明载体（放哪 + presence 语义 + 跨阶段一致 I14）

**载体设计**（二选一对比）：

| 候选 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **A（选定）：P1 frontmatter 可选字段 + P2 UI 设计节内声明** | P1-requirements.md frontmatter 新增两个**可选字段**：`ui_render_shape: <形态声明>`（字符串，**用规范形态值**（见下方词汇表，如 `layout` / `render_component` / `temporal_effects`），开放集合不写死枚举）与 `ui_ux_dimensions: [维度1, 维度2]`（列表，从分类框架选，缺失=未声明；presence 语义）。P2 UI 设计节 `### 渲染形态声明` 行复用同一**规范值**并附中文注释（BDD-4 ①），P6 从 P1 frontmatter 读取形态决定证据形式 | 机器可读（frontmatter 结构固定，gate 直接字段读取）+ 跨阶段一致天然可校验（P2 声明须与 P1 匹配）+ presence 语义简单（字段缺失 = 布局型默认） | P1 frontmatter 需在 agate-frontmatter-check.py P1 schema 增加可选键（不破坏旧 fixtures） |
| B：capability_requirements 内嵌形态键 | 在既有 capability_requirements YAML 块加 `ui_render_shape` / `ui_ux_dimensions` 键 | 复用既有 YAML 解析路径 | 语义混杂（能力 vs 形态混合在一个三维结构里）；P1 gate 已独立解析 capability，形态读取会耦合该解析；跨阶段读取 P6/P2 都要从 YAML 提取，比 frontmatter 复杂；presence 语义不直观 |

**选择 A 的理由**：机器可读性优先——形态声明是"机制的输入物"，gate（P1/P2/P6）与 P7 一致性检查都要消费它，frontmatter 固定结构 + `agate-md-field-get.py` 现成 op 模式（新增两个 op）成本最低；presence 语义天然成立（字段缺失 = 未声明 = 布局型默认，基线不红）；跨阶段一致（I14）变成"P2 形态声明行 vs P1 frontmatter 字段"的机械比对，P7 可自动化核对。B 方案 YAML 嵌套提取成本高且模糊能力/形态边界。

**规范形态值词汇表（协议内部规范化值，[BASELINE_CHANGE] 修复轮闭合）**：

| 规范值（P1 `ui_render_shape` 字段值 = P2 gate 比对基准） | P2 声明中文标签（同义） | 形态描述 |
|------|------------------------|---------|
| `layout` | 布局型 | 常规布局结构 UI（页面/组件/弹层/视图分区），维度典型为布局结构/交互行为/视觉呈现 |
| `render_component` | 渲染组件型 | 渲染输出为主的形态（仅举例：OpenGL/WebGL/Canvas 画布/图表/模型/特效/地图/数字地球），维度典型为渲染正确性/动效时序/交互行为 |
| `temporal_effects` | 时序特效型 | 动画/动效/时序状态为主的交互形态，维度典型为动效时序/时序状态断言 |

**P1 值 ↔ P2 声明标签同义映射**：`layout`↔布局型、`render_component`↔渲染组件型、`temporal_effects`↔时序特效型。

- **取值规则（P1）**：P1 frontmatter `ui_render_shape` 字段值**必须使用规范值**（`layout`/`render_component`/`temporal_effects`；开放集合，新形态可新增规范值）。
- **取值规则（P2）**：P2 UI 设计节「渲染形态」声明行**复用规范值并附中文注释**（如 `渲染形态: render_component（渲染组件型）`）；禁止声明行仅用中文标签作为唯一表达（无规范值时可经同义映射表归一化，见下）。
- **gate 匹配语义（规范化值比对）**：P2 gate 解析 P2 声明行 → 提取规范 token（声明行含规范值直接取用；仅含中文标签「布局型/渲染组件型/时序特效型」时经同义映射表归一化为对应规范值）→ 与 P1 `ui_render_shape` 字段值比对，**相同规范值即视为一致**——杜绝 ASCII 规范值（`render_component`）与中文标签（渲染组件型）字面永不匹配的误拦问题（§2.3 形态一致性交叉校验按此语义执行）。
- **扩展规范值**：任务声明开放集合中的新形态时，P1 新增规范值 + P2 声明行复用该规范值并附中文注释；gate 比对以 P1 字段值为基准、P2 声明行提取规范值后做相等比对（同义映射表仅覆盖上表三组）。词汇表是协议内部规范化值，与「不绑定 WebGL/Canvas 等技术栈」不冲突——技术栈中立不变（约束 5）。

**架构落点**：
- `agate-frontmatter-check.py` P1 schema（31-54 行）`migrated_keys` + `types` 增两个**可选键**：`ui_render_shape: str`、`ui_ux_dimensions: list`（保留 `required` 不变——可选键不影响既有 schema 校验）
- `agate-md-field-get.py` 新增 op `ui_render_shape` / `ui_ux_dimensions`（参照 ui_affected op 的 frontmatter 优先 + 正文回退模式，175-176 行附近）
- P1 卡片/analyst.md 产出规格：frontmatter 样例补两行（注释标注"可选，渲染组件/时序特效类形态必填，常规布局型可省略"）

**跨阶段一致机制（I14，BDD-4 ① + BDD-16 验收前提）**：
- P1：`ui_render_shape` + `ui_ux_dimensions` 声明 → 决定该任务 VP 的 UX 类别 BDD 维度（BDD-1/16）
- P2：UI 设计节 `### 渲染形态声明` 行必须复用 P1 的形态与维度（gate_p2 形态一致性交叉校验按 **规范化值比对**执行，§2.3 兼容段前一项 + §2.15.1 词汇表）
- P6：verifier 从 P1 frontmatter 读形态 → 选证据形式（§2.16）；P7 一致性检查核对 P1/P2/P6 三处形态声明一致（I14，check-protocol-consistency.py 新增规则）
- **一致性缺失语义**：P2 形态声明与 P1 不一致 → P2 gate exit 1（形态一致性交叉校验）；P6 证据形式与 P1 形态不匹配（如声明渲染组件型但只用纯文本证据）→ check-p6-evidence 证据类型检查拦截（§2.16）

#### 2.15.2 维度选择合法性 + 分类框架适用口径

**维度选择合法性（gate 校验）**：P1 `ui_ux_dimensions` 的值必须是协议 UX 分类框架中的维度名（布局结构/渲染正确性/交互行为/动效时序/视觉呈现，或任务自行声明的扩展维度——扩展维度须在 P1 正文 UX 类别 BDD 标题中出现以证明其运用）。`ui_render_shape` 缺失但 `ui_ux_dimensions` 存在 → 允许（维度选择本身合法）；反之 `ui_render_shape` 存在但维度为空 → P1 gate 拦截（声明了形态却不选维度，适配层无法生效）。**校验在 check-gate.py gate_p1 新增 helper `_gate_p1_ui_shape`**：domains 含 frontend 时校验该字段对（存在性 + 维度非空 + 维度 ∈ 框架或已声明），缺失（两个都无）→ 通过（布局型默认）。

**分类框架适用口径（写 analyst.md / P1 卡片）**：
- 常规布局型（默认，`ui_render_shape` 缺失）：维度 = 布局结构/交互行为/视觉呈现（对应键盘可用性→交互行为、显示内容正确性→交互行为或渲染正确性、样式呈现→视觉呈现的典型示例）
- 渲染组件型（声明渲染正确性/动效时序/交互行为等维度）：checklist 覆盖渲染管线配置/画布尺寸与分辨率/投影与坐标系/图层顺序/场景加载状态/帧时序/动画关键帧/特效触发与结束状态/手势交互（见 §2.4）
- 时序特效型（声明动效时序维度）：checklist 覆盖帧时序/动画关键帧/特效/时序状态断言
- **技术栈中立**：维度与 checklist 全部用"形态机制"描述（渲染正确性=渲染结果是否正确呈现，时序=帧/时间戳对齐，动效=过渡/动画行为），不出现 WebGL/Canvas/OpenGL 等绑定（协议条文里仅可作"仅举例"出现）

#### 2.15.3 判据可量化条文（BDD-2 扩展 + BDD-16 验收锚点）

**verifier.md + P6 卡片写入可量化判据条文**，绑定渲染组件类维度：

| 维度 | 可量化判据（P6 判定锚点） | 禁用的主观词 |
|------|--------------------------|-------------|
| 渲染正确性 | 渲染输出与参考/预期对比（渲染输出对比图 + diff 度量、输出数据断言、坐标/尺寸断言） | 可读、美观、画面自然、位置正确 |
| 时序 | 帧/时间戳对齐（帧号/采样点断言、加载/动画时长不超阈值） | 流畅、及时、连贯 |
| 动效 | 过渡/动画行为断言（关键帧状态、结束态落点、动效时长） | 平滑、自然 |
| 手势交互/动作 | 动作输入 → 界面/渲染响应的坐标/参数断言（旋转角/缩放比/拖拽位移量化） | 响应灵敏、跟手 |

- analyst.md BDD 反模式自检清单沿用上表档位（BDD-2）：UX 全维度"Then 必须可用可量化判据二值判定 + 禁用主观词"（§2.2 已挂靠）
- requirements-review：渲染组件类形态任务的 UX BDD 若是主观词表述 → 打回（表 3 档非量化判据 → 需补量化锚点）

#### 2.15.4 gate 组合收口（SCOPE+ 新增检查汇总）

| 阶段 | 新增检查 | 触发条件 | 终点行为 |
|------|---------|---------|---------|
| P1 | `_gate_p1_ui_shape`（形态/维度声明合法性） | domains 含 frontend | 非法（声明了形态但维度空/维度非框架且未声明使用）→ exit 1；缺失两个字段 → 通过 |
| P2 | `_gate_p2_ui_design_section` 形态分支（§2.3 检查 4）+ P1-P2 形态一致性交叉校验 | ui_affected: true | 缺形态声明/维度选择/按形态 checklist → exit 1；声明不一致 → exit 1 |
| P6 | check-p6-evidence.py 证据形式按形态识别（§2.16） | ui_affected: true + P1 形态声明 | 形态与证据形式不匹配 → exit 1 |
| P7 多阶段 | check-protocol-consistency.py 新增规则（I14 三处形态一致） | — | 不一致 → consistency ERROR |

**单测（test_check_gate.py）**：
- `test_shape_1_shape_no_dimensions_exit_1`：domains=frontend + `ui_render_shape: render_component` 但 `ui_ux_dimensions: []` → exit 1
- `test_shape_2_shape_with_valid_dims_exit_2`：domains=frontend + shape + dimensions=[渲染正确性]（框架内） → exit 2
- `test_shape_3_no_shape_backend_exit_2`：domains=backend 无形态字段 → 不触发 exit 2（兼容）
- `test_shape_4_extension_dim_declared_exit_2`：维度=自定义扩展名 + 该维在 P1 UX BDD 标题出现 → exit 2（扩展维度合法）
- `test_shape_5_frontmatter_optional_presence_exit_2`：既有 P1 schema 无形态字段的 fixture → frontmatter-check 通过（可选键不破坏）→ exit 2

### 2.16 P6 证据形式按形态选择（BDD-9/17：形式清单 + check-p6-evidence 适配）

> I15 要求"渲染组件类证据形式可在 verifier/P6 侧选用"，本节目的是把 P2 设计的**形式清单**细化到可实施（verifier.md / P6 卡片 / check-p6-evidence.py 共用同一契约）。

**形式清单（按形态档）**：

| 形态档 | 运行时证据 | 视觉证据 | 判定锚点 |
|--------|-----------|---------|---------|
| 常规布局型（默认） | `screenshots/` 截图 + `.log/.json` 行为日志 | vision YAML（available/supplementable）、像素检测+人工复核（GAP） | 既有 R1a/R1b/blocker_count 体系 |
| 渲染组件型 | **帧序列** `frames/{bdd-id}-{NN}.png`（NN=帧号 01..，目录结构 `P6-evidence/frames/`）+ 行为日志 | 帧序列逐帧 vision YAML（描述帧间差异/时序） | 帧号连续性 + 帧差异可描述 + 时序断言（帧间变化与 BDD 时序判据对齐） |
| 渲染组件型（对比类） | **渲染输出对比** `renders/{bdd-id}-{variant}-actual.png` + `renders/{bdd-id}-{variant}-reference.png` + `renders/{bdd-id}-{variant}-diff.{json,png}` | 对比描述 vision YAML + diff 度量（像素差异率/结构相似度，量化为锚点） | diff 度量文件存在 + 差异数值与 BDD 阈值（P1/P2 定义）对照 |
| 时序特效型 | **时序截图** `screenshots/{bdd-id}-t1.png / -t2.png ...`（时刻后缀）或帧序列 | 逐时刻 vision YAML | 时刻序列完整 + 各时刻状态与 BDD 时序断言对齐 |

**目录/命名约定（写入 verifier.md 输出节 + P6 卡片）**：
- `frames/`：帧序列统一放 `P6-evidence/frames/`，命名 `{bdd-id}-{NN}.png`（NN 两位起，如 `bdd16-01.png`），帧号=时序顺序；PASS 行引用目录或首末帧（`(frames/bdd16-01.png, frames/bdd16-02.png)`）
- `renders/`：渲染输出对比统一 `P6-evidence/renders/`，命名 `{bdd-id}-{variant}-actual.png` / `-reference.png` / `-diff.json`（variant 可区分多个对比场景）；diff.json 含量化度量字段（如 `pixel_diff_ratio` / `average_hash_distance`，与 BDD 定义档一致）；PASS 行引 actual + diff
- 时序截图：沿用 `screenshots/` 目录 + 时刻后缀 `-t{N}.png`（`-t1`/`-t2`/`-t3`），多时刻共属一 BDD 时按后缀有序；**`-tN` 系列与 `frames/` 帧序列同权获取分组豁免**（分组键 = bdd-id 前缀：`{bdd-id}-t1..tN` 与 `{bdd-id}-NN` 统一按同 bdd 组豁免相邻样本，见下雷同判定）
- **md5/avg-hash 雷同判定适用域扩展**：帧序列内相邻帧"视觉相近"是**正常时序特性**（动画连续帧），**时序截图 `-tN` 系列同理**（同场景不同时刻、同一 bdd 的相邻时刻截图必然高度近似）——二者**同权豁免**：`screenshots/{bdd-id}-t1.png`/`-t2.png` 与 `frames/{bdd-id}-01.png`/`-02.png` 统一按「同 BDD 证据组（bdd-id 前缀）」分组——组内相邻样本不触发雷同降级待复核；跨 BDD 的帧/对比图/时序截图若 md5 逐字节重复 → 仍硬阻断（充数防伪）；avg-hash 重复且非同一 bdd 组 → 降级待复核（沿用 §2.13 产出，判定域从"同目录截图"扩展到"跨 scenes 的帧/对比图/时序截图"）。防误伤设计：check-p6-evidence 按「同 BDD 证据组（bdd-id 前缀匹配，同时覆盖 `-tN` 时序截图与帧序列 `-NN`）」计算雷同——组内相邻样本豁免、组间雷同触发判定

**check-p6-evidence.py 适配**：
1. 证据类型识别：`ui_affected == "true"` 且 P1 `ui_render_shape` 声明渲染组件/时序特效类 → 非纯文本证据判定扩展识别 `frames/`、`renders/`、`-t{N}` 后缀（当前仅判 .md/.txt 排除，image/结构化文件天然计入非文本，扩展主要是目录规范化判定：渲染组件型必须含 `frames/` 或 `renders/` 或带时刻后缀截图，否则"证据形式与形态不匹配" exit 1）
2. 帧序列完整性：`frames/` 目录引用存在 + 帧文件非空（>1KB）+ 帧号连续（命名解析序号，缺口 → WARNING；P6 卡片不阻断，verifier 复核）
3. 渲染输出对比：`diff.json` 必须存在（缺 → exit 1）且含量化度量字段；PASS 行须引 actual + diff
4. 雷同判定按"同 BDD 证据组"分组（分组键 = bdd-id 前缀，`-tN` 时序截图系列与 `frames/` 帧序列统一归组、同权豁免相邻样本，防相邻帧/相邻时刻误伤，见上）
5. **平台无关**：帧/renders 检查用 `os.walk` + 命名正则，不依赖特定图片编码工具；Pillow 缺失时 diff 数值不做像素级验证（仅结构性检查），vision YAML 描述由 vision-analyst 产出

**单测（test_check_p6_evidence.py）**：§2.8 已列 3 例（test_render_evid_1 帧序列识别 / test_render_evid_2 渲染输出对比 / test_render_evid_3 纯文本拦截），补充：
- `test_frame_seq_1_adjacent_frames_no_ahash_trigger_exit_0`：同 BDD 帧序列相邻帧视觉相近 → 不触发雷同降级（分组豁免）→ exit 0
- `test_time_seq_1_adjacent_time_shots_no_ahash_trigger_exit_0` `[BASELINE_CHANGE]`：同 bdd 的时序截图 `screenshots/{bdd-id}-t1.png` / `{bdd-id}-t2.png` 视觉相近 → 按同 bdd 组（bdd-id 前缀）豁免 → 不触发雷同降级待复核 → exit 0（`-tN` 系列与 frames/ 帧序列同权豁免）
- `test_render_diff_1_missing_diff_json_exit_1`：渲染输出对比缺 diff.json → exit 1
- `test_render_diff_2_diff_json_with_metric_exit_0`：diff.json 含 pixel_diff_ratio → exit 0
- `test_render_evid_4_shape_decl_layout_no_frames_exit_0`：P1 形态=常规布局型 + 无 frames/ → 不要求渲染组件证据（兼容布局型）→ exit 0

---

## 3. gate_commands（P2 固化，P3/P5/P6 照此执行）

```yaml
gate_commands:
  P3: "python3 -m pytest -q --collect-only agate/tests/"
  P3_formatter: "python3 agate/assets/formatters/pytest.sh"   # 可选：测试输出标准化
  P5: "python3 -m pytest -q --tb=no agate/tests/"
  P5_formatter: "python3 agate/assets/formatters/pytest.sh"
  P6: "python3 -m pytest -q --tb=no agate/tests/"
  project_module: "scripts"
```

说明：
- 本任务无 UI 产物（ui_affected: false），**不声明 P3_e2e/P5_e2e**（P2 卡片 gate_commands.P5_e2e 仅在 ui_affected: true 时必填）
- 测试根目录 `agate/tests/`（AGENTS.md 约定全量 pytest），P3 用 collect-only 供 check-tdd-red 读测试集，P5/P6 用 `--tb=no` 紧凑输出
- formatter 路径用绝对/仓库相对路径（`agate/assets/formatters/pytest.sh`）——check-gate.py P2.61 会做命令可执行性 WARNING 检查，`python3` 存在即可（脚本本身做 shutil.which(token)，首 token 是 python3，通过）

## 4. Windows GUI 自动化评估小节（BDD-7，RM-AG0006）

### 4.1 评估对象

- Windows 环境 agate UI 任务的 E2E 现状：QTest offscreen 信号级模拟 + 截图（TQC0001 Q9）
- 候选框架：WinAppDriver（微软官方，Selenium/Appium 系，支持 UIA 树）、AutoIt（脚本化 GUI 自动化，非标准协议）

### 4.2 评估结论：保持现状（调研非实测）

| 维度 | WinAppDriver | AutoIt | 结论 |
|------|--------------|--------|------|
| 协议/生态 | Selenium 系，API 成熟，Appium 兼容 | 专有脚本语言，社区小众 | WinAppDriver 占优 |
| 适用对象 | Windows 原生桌面 app（UIA 暴露） | 任意 Windows GUI（坐标/控件级） | WinAppDriver 更贴合 Qt 应用（Qt 有 UIA bridge） |
| 接入成本 | 需装 WinAppDriver 服务 + 测试框架适配 | 需装 AutoIt 解释器 + 脚本化 | 两者均需新增运行时依赖 |
| 与现有 QTest 路径关系 | 真实 GUI 交互（真实输入事件），与 offscreen 信号级模拟互补 | 同左 | 均为"真实 GUI 路径"补充 |
| 本环境限制 | **本环境为 Linux，无真实 Windows GUI**——无法实测，仅调研 | 同左 | 调研非实测（P0-brief env_constraints 明确） |

**结论**：**保持现状**，理由：
1. 本任务改动对象是 agate 协议本体（文档 + gate 脚本），不直接受益 GUI 框架；当前 UI 任务走 QTest offscreen + 截图 + 双证据机制已覆盖功能与视觉验收路径
2. Windows GUI 自动化框架评估属**运行时基础设施选型**，应由"未来真实 Windows UI 改造任务"在其 P2 阶段决策（本任务无真实 Windows 环境，硬上框架无法验证）
3. 引入 WinAppDriver/AutoIt 需要 Windows 测试机 + 服务编排，超出协议增强任务范围；协议层面已通过 vision 能力三态（available/supplementable/GAP）+ 降级链保证"无 GUI 框架时 P6 不脆断"

**不写"已实测 Windows"**——本评估基于框架能力文档调研与 P0-brief 环境约束推断，无真实 Windows GUI 实测。若未来项目在 Windows 上落地，建议在该任务 P2 复用本评估表 + 实跑验证。

## 5. env_constraints 与 minimal_validation

### 5.1 env_constraints（确认 P0-brief）

```yaml
env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale），无真实 Windows GUI；视觉分析能力可用（P1 能力识别确认）——用于跑 worktree 全部 pytest + consistency"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  isolation_check: "本任务无外部服务/端口/数据库，无需隔离动作；P5/P6 全在 worktree 本地跑 gate 脚本单测"
  # 双工作区：gate 工具用 ~/.agate（稳定版），check-protocol-consistency 用 worktree 自己的（检查 worktree 协议文件）
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/"
```

### 5.2 minimal_validation

```yaml
minimal_validation:
  - assumption: "BDD-3 P1 检查不误伤基线——既有 fixtures 的 P1 domains 均不含 frontend"
    method: "grep fixtures P1-requirements.md 的 domains 字段 + create_task_dir 默认 P1 无 domains frontmatter"
    result: "confirmed"        # 已核实：fixtures（full-task/ui-affected/vision-blocked/high-risk/paused-task）P1 均无 domains:frontend
    note: "基线 825 cases 不因新增 P1 检查变红——新检查仅 frontend 触发"
  - assumption: "BDD-14 avg-hash 判定可构造可测——同视觉内容不同字节 PNG → ahash 相同、md5 不同"
    method: "PIL 生成同 visual 内容不同编码 PNG + 跑 agate-image-check.py ahash 实测"
    result: "confirmed"        # 实测：两 PNG md5 不同（55e8... vs 500b...），ahash 均为 64 位 '1' 串
    note: "Pillow 缺失时 ahash 测试 skip（平台无关，不硬编码 Unix 路径）"
  - assumption: "P1 的 capability_requirements yaml 块可被 gate 脚本解析"
    method: "读 check-gate.py 现有 _md_field_get 模式 + 用 yaml.safe_load 提取 capability_requirements 代码围栏块"
    result: "confirmed"        # pyyaml 是强制依赖（LIMITATIONS.md）；提取 ```yaml 代码围栏块内 YAML 解析（与 P1 capability_requirements 实际承载格式一致，见 P1 §7 代码围栏样例），不用 '## ' 章节分隔定位
    note: "纯代码逻辑，依赖内部函数 agate-md-field-get.py（_md_field_get）+ pyyaml"
  - assumption: "UI 设计节节标题用 `## UI 设计` 可被 P2 gate grep 定位"
    method: "参照现有 P2-design.md 节标题风格（## 5. 裁剪说明 等）"
    result: "confirmed"        # 协议文档节标题统一 `## ` 层级；兼容 `### ` 子级
    note: "纯代码逻辑"
  - assumption: "[BASELINE_CHANGE] P1 frontmatter 可选字段 ui_render_shape/ui_ux_dimensions 可被 gate 读取且不破坏既有 schema"
    method: "读 agate-frontmatter-check.py P1 schema（migrated_keys 为增补清单，required 不变）+ agate-md-field-get.py frontmatter 优先正则回退模式"
    result: "confirmed"        # schema 的 migrated_keys 是可变集合、required 是硬校验集——新增可选键仅进 migrated_keys+types，required 不动则不破坏既有 fixture；md-field-get 的 op 模式（175-176 行 ui_affected）可直接仿照
    note: "纯代码逻辑，依赖内部函数 _frontmatter_field / _regex_scalar（agate-md-field-get.py）+ pyyaml"
  - assumption: "[BASELINE_CHANGE] 渲染组件型证据目录（frames/renders/-tN 后缀）可被 check-p6-evidence 现有非文本证据判定逻辑扩展识别"
    method: "读 check-p6-evidence.py 156-170 行证据类型判定（_find_files + 扩展名排除），确认走 os.walk 目录遍历、扩展名判定，frame/renders 为 image 文件天然计入非文本"
    result: "confirmed"        # .png 不在排除列表（仅 .md/.txt 排除），帧/对比图文件自动计入非文本证据；新增的是"形态匹配"目录规范化检查（渲染组件型须含 frames/ 或 renders/ 或 -tN 截图），为纯逻辑新增
    note: "纯代码逻辑，依赖 os.walk + 命名正则，不依赖 Pillow（结构性检查）"
  - assumption: "[BASELINE_CHANGE] 帧序列/时序截图雷同判定按'同 BDD 组（bdd-id 前缀）'豁免相邻样本不误伤动画时序证据（frames 相邻帧与 -tN 相邻时刻同权豁免）"
    method: "设计判定域：check-p6-evidence avg-hash 逻辑（250-262 行 ahash）。改造为组内豁免（同 BDD 证据组——帧序列 {bdd-id}-NN 与 时序截图 {bdd-id}-tN 共用 bdd-id 前缀分组），组间雷同触发降级判定"
    result: "confirmed"        # 动画连续帧/时序相邻截图天然视觉相近——按 bdd 组豁免避免时序证据被误判为'充数雷同'；跨 bdd 组雷同仍是降级待复核判据（充数防伪不放松）
    note: "纯代码逻辑；Pillow 缺失时 ahash 整体 SKIP（沿用现有行为）"
```

## 6. 影响面核对清单（BDD-8，对齐 P1 影响面清单）

> 与 P1 §8 的 45 文件 / 64 处口径逐项核对。P1 清单含 45 文件（协议文档 + 脚本 + 测试夹具）；P2 全量再扫描 `agate/` 树 `rg -l 'ui_affected|vision-analyst|plan-design-review|vision-helper'` = 45 文件，**与 P1 一致**。以下按 P1 分类逐项列同步动作，缺失项即 P7 一致性检查核对点。
>
> **【2026-08-17 扩展** `[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态]`**：渲染组件类/UX 交互形态适配（BDD-16/17 + BDD-1/2/4/6/9/10/13 扩展）新增联动点以【2026-08-17 扩展】标注并入下表，与 P1 清单合并后的全量核对由本清单负责（BDD-8）。

### 6.1 协议文档（agate-docs）

| 文件 | 联动点（P1 记录） | 本方案同步动作 |
|------|------------------|---------------|
| `state-machine.md` | 89-94 行 P2 ui_affected、101 行 P5 E2E、323/326/330/333 gate 摘要 | ① P2 转移条件补"ui_affected:true 须含 UI 设计节"（对应 BDD-4 gate 检查）；② P1→P2 转移补 vision 三态声明约束（对应 BDD-3）；③ P6 转移 119 行补措辞"双证据按三态分档" |
| `rules/state-transitions.md` | 21 行 P2 四字段、25/32 行 UI 任务段 | 同步 P2 四字段→"四字段+ui_affected 时 UI 设计节"；UI 任务段补三态分档 |
| `WORKFLOW.md` | 286 行 P2 评审映射、290 行 P6 验收 | ① frontend→plan-design-review 行补"审视觉/交互维度"；② P6 行补双证据三态分档描述 |
| `role-system.md` | 31/44/45/57 行角色映射 | ① 确认不新增 designer（补一行注明）；② plan-design-review 行职责描述同步视觉/交互维度 |
| `assets/execution-roles/analyst.md` | 78-104 三态机制、168 行 frontend→ui_affected | ① capability 节补"frontend 任务必须声明视觉能力条目"（BDD-3）；② 产出规格补 UX 类别 BDD 要求（BDD-1/2）；③ BDD 反模式清单补 UX 维度自查（BDD-2） |
| `assets/execution-roles/architect.md` | 39 行 ui_affected 字段、116 行三字段、191 行复杂交互 | ① §输出补"ui_affected:true 必含 UI 设计节"（BDD-4/5）；② 补 UI 设计节结构规格（§2.4） |
| `assets/execution-roles/verifier.md` | 104-108 行 UI 追加约束、175-182 行 UI 流程 | ① UI 追加约束改写为三态分档双证据（BDD-9）；② 流程补第 0.5 步读三态；③ 补视觉质量 checklist 核对（BDD-9）；④ 补输入态人工复核判定标准（BDD-13） |
| `assets/execution-roles/test-designer.md` | 18/29/33/40 行 UI 用例、30-33 viewport | 核对，无实质改动（现有 E2E/viewport 要求已够）——仅确认联动 |
| `assets/execution-roles/vision-analyst.md` | 角色定位/B3/yaml 结构 | ① 角色文件补"能力自查"要求（自己先自查能否调视觉能力，不能则报告）——对应 BDD-12 的 subagent 侧；② 确认不写死视觉工具名（保持运行时探测） |
| `assets/review-roles/plan-design-review.md` | 13-21 行五维度 | 扩容为七维：增"视觉设计""交互设计细节"维度（BDD-6） |
| `assets/review-roles/design-review.md` | P4 后 UI 问题评审 | 核对，复用 P2 的视觉质量 checklist 口径（联动不新增） |
| `assets/review-roles/requirements-review.md` | 38 行 capability 三态判断 | ① 补"frontend 任务 P1 是否含 UX 类别 BDD（键盘/显示/样式）"评审要点（BDD-1）；② 补"vision 能力条目是否已声明"评审要点（BDD-3） |
| `phase-cards/P1-requirements.md` | 52-57 行 capability 声明、109 行漏声明错误 | ① 产出规格补 UX 类别 BDD + vision 声明条款（BDD-1/3）；② 常见错误补"frontend 漏 vision 条目 → exit 1" |
| `phase-cards/P2-design.md` | 48/53/70/103/113/129/155/163/177 行 | ① 产出规格补 UI 设计节字段说明（BDD-4/5）；② gate 规则补 ui_affected→UI 设计节检查（BDD-4） |
| `phase-cards/P3-tdd.md` | 49 行 UI E2E 用例 | 核对，现有已含（联动确认） |
| `phase-cards/P5-verification.md` | 40 行 E2E 命令、55/66/89/95 行 | 核对，现有已含 E2E 实跑要求（联动确认） |
| `phase-cards/P6-acceptance.md` | 11-12/35/40/50-51/126-130/164/169-172 行 | ① 13 行 UI 派发流程补 vision-analyst 可选择性（GAP 降级时改人工复核）；② 50-51 行证据要求改三态分档（BDD-9）；③ 补视觉质量 checklist 核对条文（BDD-9）；④ vision-helper 绑定节补 available 真实视觉分析（BDD-10）；⑤ 补输入态人工复核条文（BDD-13）；⑥ 168-172 补雷同截图降级待复核说明（BDD-14） |
| `phase-cards/README.md` | 15 行 P6 卡片索引 | 核对，无实质改动 |
| `dispatch-protocol.md` | 294/381/571/910/913/914/950-957/1163-1204 行 | ① A3 节（1184-1204）补视觉补充能力注入绑定（BDD-11）；② 派发 prompt 模板同步（见 dispatch-prompt）；③ P6 证据段（571 行附近）补"avg-hash 降级待复核"措辞（BDD-14）；④ P5/P6 派发追加段（560-570 附近）补能力自查要求（BDD-12） |
| `assets/templates/dispatch-prompt.md` | 69 行能力注入、92 行评审角色、106 行 P3_e2e | ① 新增"能力自查"强制节（BDD-12）；② 能力补充说明节注明视觉 supplementable 注入指引（BDD-11） |
| `assets/templates/task-files.md` | 27/244/267/271/329/354-356 行 | ① P2 模板补 UI 设计节样例（BDD-4/5）；② P6 UI 证据约定改三态分档 + 人工复核样例（BDD-9/13） |
| `LIMITATIONS.md` | 97-106 行局限 7 | 更新：视觉能力三态识别 + 降级链（像素检测+人工复核）缓解局限 7 的程度描述；补 avg-hash 降级待复核说明 |
| `loop-orchestration.md` | 84 行示例 | 核对，无实质改动 |
| `scripts/README.md` | 114/122 行脚本索引、199-203 WARNING 说明 | ① 新增脚本/行为说明（check-p6-evidence avg-hash 降级）② P1/P2 gate 新检查说明 |
| `state-machine.md` | 【2026-08-17 扩展】P1/P2/P6 转移条件的渲染形态声明约束 | P2 转移条件补"ui_affected:true UI 设计节含形态声明"（BDD-4 ①，§2.3） |
| `assets/execution-roles/analyst.md` | 【2026-08-17 扩展】UX 分类框架 + 形态声明/维度选择步骤 | ① 产出规格补"frontend 任务 P1 必须声明 ui_render_shape/ui_ux_dimensions"（BDD-1/16，§2.15.1）；② 分类框架维度清单条文（布局结构/渲染正确性/交互行为/动效时序/视觉呈现等开放集合）；③ BDD 反模式清单补渲染正确性/时序/动效/手势维度可量化判据挡（BDD-2，§2.15.3） |
| `assets/execution-roles/architect.md` | 【2026-08-17 扩展】UI 设计节补形态声明 + 维度选择 + 渲染组件/时序 checklist | UI 设计节结构规格随分类框架适配（BDD-4，§2.4） |
| `assets/execution-roles/verifier.md` | 【2026-08-17 扩展】证据形式按形态可选（帧序列/时序截图/渲染输出对比）+ 渲染输出/帧序列真实视觉分析 | ① 双证据形式分档增加渲染形态维度（BDD-9，§2.8）；② 证据输出节补 frames/renders/-tN 目录命名约定（BDD-17，§2.16）；③ 可量化判据条文（渲染正确性/时序/动效/手势，BDD-2/16，§2.15.3） |
| `assets/execution-roles/vision-analyst.md` | 【2026-08-17 扩展】视觉分析对象扩展至渲染输出/帧序列 | 不写死工具；像素/帧间/场景差异结构化描述（BDD-10/17，§2.9/§2.16） |
| `assets/execution-roles/test-designer.md` | 【2026-08-17 扩展】渲染组件类用例覆盖帧采样点/帧捕获 | UI 用例规格适配渲染组件形态（时序采样点/帧捕获与 viewport 并列，BDD-16）——§2.16 的 frames 命名约定须在 P3 测试设计中体现 |
| `assets/review-roles/plan-design-review.md` | 【2026-08-17 扩展】新增"渲染正确性与时序"维度 | 渲染组件类形态启用，0-10 可判定评分项（渲染结果正确性0-4/帧时序0-3/动效质量0-3）（BDD-6，§2.5） |
| `assets/review-roles/requirements-review.md` | 【2026-08-17 扩展】评审要点补"形态声明/维度选择是否随任务适配 + 渲染组件类维度 BDD 是否齐备" | UX 类别 BDD 评审按分类框架执行（BDD-1/16，§2.15.3 主观词打回） |
| `phase-cards/P1-requirements.md` | 【2026-08-17 扩展】分类框架 + 形态声明 + 维度选择产出要求 | frontmatter 样例补 ui_render_shape/ui_ux_dimensions 可选键（BDD-1/16，§2.15.1）+ 判据可量化条文 |
| `phase-cards/P2-design.md` | 【2026-08-17 扩展】UI 设计节规格补形态声明 + 渲染组件类 checklist 要求 | UI 设计节 gate 检查按形态适配（BDD-4，§2.3） |
| `phase-cards/P6-acceptance.md` | 【2026-08-17 扩展】证据类型补"帧序列/时序截图/渲染输出对比"按形态可选 + 渲染输出分析条文 | 双证据/视觉质量核对按形态分档（BDD-9/17，§2.16） |
| `dispatch-protocol.md` | 【2026-08-17 扩展】md5/avg-hash 雷同判定适用域扩展至帧序列/时序证据；A3 注入语境含渲染组件证据形式 | 证据规则与能力注入覆盖渲染形态（BDD-9/17，§2.16 分组豁免设计） |
| `assets/templates/task-files.md` | 【2026-08-17 扩展】P2 模板补渲染形态声明样例、P6 模板补帧序列/时序截图证据样例 | 模板随分类框架适配（BDD-4/17，§2.15.1/§2.16） |
| `LIMITATIONS.md` | 【2026-08-17 扩展】局限 7 缓解描述更新（帧序列/输出对比证据 + 分类框架适配） | 局限缓解描述同步范围扩展 |

### 6.2 Gate 脚本（agate-scripts-py）

| 脚本 | 联动点 | 本方案改动 |
|------|--------|-----------|
| `check-gate.py` | P1/P2 gate | ① gate_p1 新增 vision 三态检查（BDD-3）；② gate_p2 新增 UI 设计节检查（BDD-4） |
| `check-p6-evidence.py` | 156-181 行 ui_affected 证据、261 行 avg-hash | ① GAP 分支改"人工复核记录文件"证据检查（BDD-9）；② avg-hash 从 WARNING 改降级待复核判定（BDD-14） |
| `check-p6-provenance.py` | 277-313 行 R1b vision YAML 审计 | GAP 分支放宽 vision 强制（要求复核记录替代），available 分支语义不变（BDD-9） |
| `agate-md-field-get.py` | 175-176 行 ui_affected op | 新增 op `ui_render_shape`/`ui_ux_dimensions`（P1 frontmatter 形态字段读取，SCOPE+ 见【2026-08-17 扩展】行）——UI 设计节 body 检测另行（节标题 + 形态声明行） |
| `agate-frontmatter-check.py` | 56-74 行 P2 schema | P2 schema 增加可选字段 `ui_design_section`（bool，可选，presence 语义），不破坏旧 fixture |
| `agate-vision-blocker.py` | blocker_count | 核对，兼容保留 |
| `agate-extract-context.py` | 126-133 行 P2 字段 | 核对；不新增字段（UI 设计节用 body 检测） |
| `check-protocol-consistency.py` | 355 行 P5_e2e 模板、542 行 ui_affected 关键词 | 新增一致性规则：① analyst.md/P1 卡片须含 UX 类别 BDD 要求（BDD-1）；② plan-design-review.md 须含"视觉设计"维度（BDD-6）；③ verifier.md/P6 卡片须含三态分档/输入态复核条文（BDD-9/13） |
| `ci-gate-backstop.py` | 无直接命中 | 核对，兼容（新检查在 push 后 CI 重跑 gate 时自动覆盖） |
| `check-gate.py` | 【2026-08-17 扩展】gate_p1 新增 `_gate_p1_ui_shape`（形态/维度合法性，BDD-1/16）；gate_p2 形态分支 + P1-P2 一致性（BDD-4 ①） | P1/P2 gate 随分类框架适配（§2.15.4） |
| `check-p6-evidence.py` | 【2026-08-17 扩展】证据形式按形态识别（frames/renders/-tN）+ 帧序列分组雷同豁免 | 证据形式按形态分档（BDD-9/17，§2.16） |
| `check-p6-provenance.py` | 【2026-08-17 扩展】GAP 分支的渲染组件类证据（帧序列/输出对比）复核记录；R1b 语义保持 | 双证据覆盖渲染形态（BDD-9，§2.8） |
| `agate-md-field-get.py` | 【2026-08-17 扩展】新增 op `ui_render_shape`/`ui_ux_dimensions`（P1 frontmatter 读取） | 新增 op（BDD-1/16，§2.15.1） |
| `agate-frontmatter-check.py` | 【2026-08-17 扩展】P1 schema 增加可选键 `ui_render_shape`/`ui_ux_dimensions` | 可选键进 migrated_keys+types，required 不动，不破坏既有 fixtures（BDD-1/16，§2.15.1） |
| `check-protocol-consistency.py` | 【2026-08-17 扩展】新增分类框架/形态适配条文跨文档一致 + I14 三处形态声明一致 | 文档族一致性覆盖新增条文（BDD-1/16，§2.15.1/§2.15.4） |

### 6.3 测试与夹具（agate-tests）

| 文件 | 联动点 | 本方案改动 |
|------|--------|-----------|
| `tests/unit/test_check_gate.py` | P1/P2 gate 用例 | 新增 BDD-3/4 用例（vision 三态缺失/非法/兼容 + UI 设计节缺失/完整/兼容）+ 【2026-08-17 扩展】BDD-1/16 形态声明/维度合法性用例（test_shape_1~5，§2.15.4）+ BDD-4 形态分支用例（test_ui_design_5~7，§2.3） |
| `tests/unit/test_check_p6_evidence.py` | avg-hash WARNING 用例 | 改/增降级判定用例（同 content 不同名 → 有/无复核记录）+ 【2026-08-17 扩展】帧序列/渲染输出对比证据用例（test_render_evid_*/test_frame_seq_*/test_render_diff_*，§2.8/§2.16） |
| `tests/unit/test_check_p6_provenance.py` | 240 行 vision blocker | 增 GAP 分支用例（vision=GAP 时 R1b 放宽）；【2026-08-17 扩展】渲染组件类 GAP 复核记录用例（§2.8） |
| `tests/unit/test_agate_md_field_get.py` | ui_affected op | 【2026-08-17 扩展】新增 ui_render_shape/ui_ux_dimensions op 用例（§2.15.1） |
| `tests/unit/test_check_frontmatter.py` | P1/P2/P6 schema | 增 P2 可选字段 `ui_design_section` 用例 + 【2026-08-17 扩展】P1 可选键 ui_render_shape/ui_ux_dimensions 用例（不破坏既有 fixture，§2.15.1） |
| `tests/unit/test_agate_vision_blocker.py` | 2 用例 | 核对，兼容 |
| `tests/unit/test_agate_extract_context.py` | P2 字段 | 核对，无新字段 |
| `tests/unit/test_agate_capture_env_baseline.py` | 环境基线 | 核对，无关不动 |
| `tests/integration/test_pre_commit_hook.py` | hook 集成 | 核对；若 pre-commit P1/P2 gate 行为变则补用例（新增检查均在 check-gate.py 内，hook 行为通过脚本化自动覆盖，预计无需改） |
| `tests/unit/test_dispatch_orchestration.py` | 派发/A3 | 补 supplementable 视觉语境注入用例（BDD-11）+ 【2026-08-17 扩展】渲染组件形态证据形式注入用例（BDD-17，§2.16） |
| `tests/unit/test_review_role_docs.py` | plan-design-review 文档读取 | 新增（BDD-6，§2.5）：断言含"视觉设计"/"交互设计"/"渲染正确性与时序"维度名 + 0-10 评分项条文 |
| `tests/fixtures/{...}/P2-design.md` | 既有夹具 | 核对：full-task/high-risk/paused-task 三个 `ui_affected:false` → 不触发新 P2 检查；**`ui-affected` 与 `vision-blocked` 两个均 `ui_affected:true` 且无 UI 设计节——但均不用于 P2 gate 测试（test_check_gate 自建 fixture，不引用静态夹具目录），P6 专用**（ui-affected 测 P6 证据路径、vision-blocked 测 P6 GAP 降级，见 §2.3 兼容段免责说明）→ 新 P2 检查不命中；新增可选字段不破坏旧 fixture |
| `tests/fixtures/{...}/P1-requirements.md` | 【2026-08-17 扩展】既有 P1 fixtures 均无 ui_render_shape 字段 | 核对：新字段为可选 → 缺失 = 布局型默认，不触发新 P1 检查，兼容基线（§2.15.1 presence 语义） |
| `tests/README.md`（58 行计数表）+ `tests/scripts/count-tests.sh` | 用例计数 | 用例数变化后更新计数期望值（≥749 且单调不减） |

### 6.4 外部联动（非协议文件，P8 处理）

- `docs/roadmap*`：RM-AG0004/0006/0007 回写 done（P8）
- `CHANGELOG.md` / `README.md` badge / `agate/UPGRADING.md`：版本发布三件套（P8）；UPGRADING 需新增"P1 frontend 任务必须声明 vision 三态 + P2 ui_affected 必须含 UI 设计节 + P6 avg-hash 降级"破坏性变更条目，【2026-08-17 扩展】补"前端任务可选声明渲染形态/维度（缺失走布局型默认，不破坏性）"说明

## 7. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/check-gate.py:100-419
    why: gate_p1/gate_p2 结构 + _frontmatter_field/_md_field_get 模式，新增 vision 三态 + UI 设计节检查挂载点；【2026-08-17 扩展】新增 _gate_p1_ui_shape 挂载（§2.15.4）
  - path: agate/scripts/check-p6-evidence.py:148-264
    why: ui_affected 判定 + avg-hash WARNING 改降级待复核；GAP 分支证据检查；【2026-08-17 扩展】证据形式按形态识别（frames/renders/-tN）+ 帧序列分组雷同豁免（§2.16）
  - path: agate/scripts/check-p6-provenance.py:270-320
    why: R1b vision YAML 审计的 GAP 放宽点；【2026-08-17 扩展】渲染组件类 GAP 复核记录（§2.8）
  - path: agate/scripts/agate_common.py:233-310
    why: write_gate_result/read_state 等公共函数（脚本改动时复用）
  - path: agate/scripts/agate-frontmatter-check.py:30-104
    why: P2 schema 增加可选 ui_design_section 字段；【2026-08-17 扩展】P1 schema 增加可选键 ui_render_shape/ui_ux_dimensions（§2.15.1）
  - path: agate/scripts/agate-md-field-get.py:175-180
    why: 【2026-08-17 扩展】新增 op ui_render_shape/ui_ux_dimensions 参照 ui_affected op（§2.15.1）
  - path: agate/scripts/check-protocol-consistency.py:340-560
    why: 新增文档一致性锚点规则（UX BDD/视觉维度/三态条文）；【2026-08-17 扩展】分类框架/形态适配跨文档一致 + I14 三处形态一致（§2.15.1/§2.15.4）
  - path: agate/assets/execution-roles/analyst.md:75-130
    why: 能力三态机制现有条文，补 UX/vision 声明要求；【2026-08-17 扩展】分类框架 + 形态声明/维度选择步骤 + 可量化判据挡（§2.15.1/§2.15.3）
  - path: agate/assets/execution-roles/architect.md:34-110
    why: 输出规格补 UI 设计节 + UI 设计节结构规格；【2026-08-17 扩展】UI 设计节形态声明行 + 渲染组件/时序 checklist（§2.4）
  - path: agate/assets/execution-roles/verifier.md:104-230
    why: UI 追加约束改三态分档 + 输入态复核 + 视觉质量 checklist；【2026-08-17 扩展】证据输出节补 frames/renders/-tN 命名约定 + 可量化判据条文（§2.15.3/§2.16）
  - path: agate/assets/execution-roles/vision-analyst.md:244-297
    why: 补能力自查要求 + 确认不写死工具；【2026-08-17 扩展】视觉分析对象扩展至渲染输出/帧序列（§2.9）
  - path: agate/assets/review-roles/plan-design-review.md:9-33
    why: 维度表扩容为七维；【2026-08-17 扩展】渲染正确性与时序维度（§2.5）
  - path: agate/assets/review-roles/requirements-review.md:14-43
    why: 补 UX/vision 评审要点；【2026-08-17 扩展】形态声明/维度选择评审 + 渲染组件类维度 BDD 齐备性（§2.15.3）
  - path: agate/phase-cards/P1-requirements.md:43-120
    why: 【2026-08-17 扩展】frontmatter 样例补形态字段 + 分类框架条文（§2.15.1）
  - path: agate/phase-cards/P2-design.md:43-110
    why: 产出规格+gate 规则补 UI 设计节；【2026-08-17 扩展】UI 设计节形态分支检查（§2.3）
  - path: agate/phase-cards/P6-acceptance.md:44-140
    why: 双证据分档/输入态复核/雷同降级条文落点；【2026-08-17 扩展】证据类型补帧序列/时序截图/渲染输出对比 + 可量化判据（§2.15.3/§2.16）
  - path: agate/dispatch-protocol.md:900-960,1160-1205
    why: gate 表 + A3 节扩展
  - path: agate/assets/templates/dispatch-prompt.md:55-160
    why: 能力自查节 + supplementable 注入位
  - path: agate/tests/conftest.py:76-262
    why: create_task_dir/add_frontmatter_field 等 fixture helpers，新测试复用；【2026-08-17 扩展】测试可能需新增 P1 形态字段注入 helper
  - path: agate/tests/unit/test_check_gate.py:200-270
    why: P2 gate 测试模式（_write_p2_design/add_p2_review），新增用例沿用；【2026-08-17 扩展】test_shape_1~5 + test_ui_design_5~7
  - path: agate/tests/unit/test_check_p6_evidence.py:250-345
    why: 截图证据测试模式，新增 ahash 降级用例沿用；【2026-08-17 扩展】帧序列/渲染输出对比用例沿用
  - path: agate/tests/unit/test_check_frontmatter.py
    why: 【2026-08-17 扩展】P1 可选键 schema 用例模式（§2.15.1）
  - path: agate/tests/unit/test_agate_md_field_get.py
    why: 【2026-08-17 扩展】新 op 用例模式（§2.15.1）
```

## 8. dispatch_plan（机器字段）

本方案含三个包（agate-docs / agate-scripts-py / agate-tests）的改动，但各包改动**强耦合**（BDD 验收要求"文档条文 + gate 脚本逻辑 + 单测"三件套同批落地，拆批会导致"文档改了脚本没改"或反之的半套状态；且实现者是同一协议本体）。批间无独立可验收子目标——不符合 static-batch 拆批条件（每批须独立可验收）。故模式 = single（单发），不做静态拆批：

```yaml
dispatch_plan: {mode: single}
```

理由：
- 三包改动是同一机制（UI/UX 验收机制）的不同侧面，单批完成才可验收（BDD 三件套配对）
- 复杂度评估为 medium（改动面大但机械、无算法难度），未达 high 拆批硬线
- 知识负载：机制上下文（三态/分档/降级链）在一个 subagent 内完整承载，拆批会丢失跨包语义

## 9. 实现完成的标志（P3/P5 判定锚点）

- 协议文档：analyst.md / architect.md / verifier.md / plan-design-review.md / requirements-review.md / P1/P2/P6 卡片 / dispatch-protocol.md / dispatch-prompt.md / task-files.md / role-system.md / LIMITATIONS.md 均含对应 BDD 要求的条文（grep 锚点可查）
- gate 脚本：check-gate.py 含 `_gate_p1_vision_capability` + `_gate_p2_ui_design_section`；【2026-08-17 扩展】`_gate_p1_ui_shape` 形态/维度合法性 + gate_p2 形态分支 + P1-P2 一致性（§2.15.4，规范化值比对）；check-p6-evidence.py avg-hash 降级判定 + 证据形式按形态识别（frames/renders/-tN）+ 帧序列/时序截图分组豁免（bdd-id 前缀）；check-p6-provenance.py GAP 放宽；agate-frontmatter-check.py 可选字段（P2 ui_design_section + P1 ui_render_shape/ui_ux_dimensions）；agate-md-field-get.py 新 op ui_render_shape/ui_ux_dimensions；check-protocol-consistency.py 新增锚点规则（含分类框架/形态一致）
- 单测：BDD-3/4/6/9/11/12/13/14 各有对应用例；【2026-08-17 扩展】test_shape_1~5（BDD-1/16）+ test_ui_design_5~9（BDD-4 形态分支 + P1-P2 规范值/同义映射一致）+ test_render_evid_*（BDD-9/17）+ test_frame_seq_* + test_time_seq_* + test_render_diff_* + test_render_evid_4（兼容布局型）+ test_review_role_docs（BDD-6 渲染维度）——新增用例全绿 + 基线 825 全绿
- 验收对照：P6 逐条对照 17 条 BDD，全部 PASS（BDD-15 回归靠 gate_commands 实跑）

## 10. 兼容策略确认（P1 §9 落实）

- **增量增强**：新检查只对"新声明"生效（domains=frontend / ui_affected=true / ui_render_shape 声明）——既有 fixture P1 均无 frontend domains 且无形态字段；既有 P2-design 中 full-task/high-risk/paused-task 三个 ui_affected:false，`ui-affected` 与 `vision-blocked` 两个均 ui_affected:true 但不用于 P2 gate 测试（P6 专用，见 §2.3）→ 基线不受影响
- **P6 双证据**：available/supplementable 分支语义与既有 R1b/blocker_count 完全一致，GAP 分支新增"人工复核记录"证据路径（P6 卡片 122-124 行既有"改用非截图证据"指引的强化版）
- **雷同截图**：md5 硬阻断不变，avg-hash 从 WARNING 升级为"降级待复核"（有复核记录放行，无则阻断）；【2026-08-17 扩展】帧序列与时序截图 `-tN` 系列按同 BDD 组（bdd-id 前缀）豁免相邻样本雷同（动画时序证据不误伤），跨组雷同仍降级判定
- **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 形态声明为可空字段（presence 语义）**：`ui_render_shape`/`ui_ux_dimensions` 为 P1 frontmatter **可选字段**，缺失 = 常规布局型 + 走既有全部判定路径（P2 仅需布局/交互/视觉三类、P6 走既有截图/行为日志证据、无帧序列要求）——既有 825 基线任务与 fixtures 全部无形态字段 → 不触发新增检查，基线不红（§2.15.1）
- **回归底线**：825 基线全绿 + 新增用例全绿 + count-tests 单调不减 + consistency 0 ERROR

## 11. 断言与风险缓解

- BDD-3 P1 检查：若 future 项目既有 frontend 任务 P1 无 vision 声明 → 下次过 P1 gate 会 exit 1——这正是需求目标（强制声明），但属行为变更，需在 UPGRADING.md 写破坏性变更条（已在 §6.4 收录）
- **无声明默认语义断言**：P1 无视觉能力声明（capability_requirements 无 need 含 visual/vision）→ 视为 available 语义（证据路径保留 R1b 强制 + blocker_count，与现状完全一致），GAP 分支仅在 P1 显式声明 status=GAP 时触发——该默认由 test_vision_none_1 兼容回归用例固化（§2.8），BDD-15 基线 825 不受影响。
- avg-hash 降级判定误伤风险：行为差异类 BDD 截图视觉相同（非重复）场景——缓解：P6 卡片 122-124 行指引优先改用非截图证据；若用截图则走复核记录（复核人确认"确为不同操作但视觉相近"即可放行）
- 输入态人工复核是自述性质（verifier 自己写复核记录）——缓解：文档条文约束 + P7 一致性检查按条核对，符合 self-authored gate 缓解层次，不新增伪硬校验
- **[BASELINE_CHANGE: 2026-08-17 用户范围扩展：UI/UX 覆盖任意渲染形态] 形态声明一致性断言**：P1 声明形态但 P2 UI 设计节复用不一致 / P6 证据形式与形态不匹配 → 会被 gate（P2 exit 1 / P6 证据类型 exit 1）与 P7 一致性检查（I14 三处一致）拦截；同一任务三处形态声明由 check-protocol-consistency.py 新增规则覆盖。存在"形态声明本身撒谎"的残余风险（自写文件 gate 固有局限）——缓解：形态声明与 UX BDD / UI 设计节 / 证据形式三处互相印证（任一伪造需同时伪造三处，成本抬高），且渲染组件类关键形态由 P3 test-designer 帧采样用例 + P5/P6 实跑兜底。
- **[BASELINE_CHANGE]** 帧序列/时序截图证据被误判"充数"风险：纯色/1KB 内帧 → 触发既有方差/大小 WARNING（复用），动画帧非纯色但相邻帧雷同、时序截图 `-tN` 相邻时刻相近 → 同 bdd 组（bdd-id 前缀）豁免；若动画整体为低方差（如大面积渐变场景）→ 方差 WARNING 不阻断（exit 2）且允许 vision YAML 描述兜底，P6 卡片指引"低对比度场景优选用渲染输出对比 diff 度量"，避免时序特效任务因证据特性卡死。