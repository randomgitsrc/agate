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

> 上游：P1-requirements.md（15 条 BDD 已 approved）+ P1-review.md（复审记录闭合）
> 本方案设计的是**协议机制增强**：改造对象是 worktree 里 `agate/` 的协议文档 + gate 脚本 + 单测，不是业务 UI 应用。

---

## 0. 影响域分析

### 0.1 改什么（机制增强落点，按 BDD 分组）

| BDD | 改动域 | 涉及文件 |
|-----|--------|---------|
| BDD-1/2/3 | P1 UX 需求基线 + vision 能力三态声明 | analyst.md、P1 卡片、requirements-review.md、check-gate.py（gate_p1）、test_check_gate.py |
| BDD-4/5 | P2 UI 设计节（ui_affected: true 任务必含） + architect 兼任声明 | architect.md、P2 卡片、check-gate.py（gate_p2）、test_check_gate.py、agate-frontmatter-check.py、task-files.md |
| BDD-6 | plan-design-review 增视觉/交互维度 | plan-design-review.md、test（文档读取测试） |
| BDD-7 | Windows GUI 评估 | P2-design.md 本文件（本节） |
| BDD-8 | 影响面核对清单 | P2-design.md 本文件（本节） |
| BDD-9/10/13 | P6 双证据 + 视觉质量 checklist + 输入态人工复核 | verifier.md、P6 卡片、check-p6-evidence.py、test_check_p6_evidence.py |
| BDD-11/12 | 派发注入 + subagent 自查 | dispatch-protocol.md（A3）、dispatch-prompt.md、test_dispatch_orchestration.py |
| BDD-14 | 雷同截图降级待复核 | check-p6-evidence.py、test_check_p6_evidence.py |
| BDD-15 | 兼容回归 | 全量 pytest + consistency + count-tests 实跑 |

### 0.2 不改什么（明确边界，降低风险）

- **不新增 designer 角色**：UI 设计节由 architect 兼任产出（BDD-5），role-system.md 角色清单不变
- **不回溯改既有 task 数据**：新检查只对"新声明"生效——P1 vision 三态声明检查只在 `domains` 含 `frontend` 时触发；P2 UI 设计节检查只在 `ui_affected: true` 时触发；既有 825 基线用例不因新增检查而变红（见 §10 兼容策略）。静态 fixtures 中 `ui-affected`/`vision-blocked` 两个 P2-design 均 `ui_affected: true` 且无 UI 设计节，但均不用于 P2 gate 测试（test_check_gate 自建 fixture，不引用静态夹具），且 P6 专用，故新 P2 检查不会命中它们（见 §2.3 兼容段）
- **不改 md5 硬阻断语义**：截图逐字节去重仍然 exit 1 硬阻断（BDD-14 只改 avg-hash 级别）
- **不改既有 P6 vision-helper/blocker_count/R1b 审计语义**：available 分支的既有流程原样保留，新机制是叠加分档
- **不改 P5 E2E 实跑门槛**：state-machine.md:101 的 ui_affected→P5 E2E 实跑不变，只补 P6 侧视觉证据

### 0.3 风险在哪

1. **BDD-3 P1 检查误伤既有任务**：若既有任务 P1 的 `domains` 含 frontend 但无 capability_requirements → 新增检查会 exit 1（这正好是需求要拦截的场景，但需确认基线任务无此形态——基线 fixtures 的 P1 均无 domains:frontend，见 §5 兼容验证）
2. **BDD-4 P2 检查误伤既有 P2 fixture**：既有 fixture `ui-affected/P2-design.md` 与 `vision-blocked/P2-design.md` 均声明 `ui_affected: true` 但无 UI 设计节 → 若被 P2 gate 测试消费会变红。对策：触发条件**仅为 P2 自身 `ui_affected: true`**（不读取 P1 capabilities，与 §2.3 一致）——经核实无 P2 gate 测试引用 fixtures/ui-affected 或 fixtures/vision-blocked（test_check_gate 自建 fixture），故这些 fixture 不会被 P2 检查命中，兼容成立；新增专门 fixture 覆盖 BDD-4
3. **BDD-14 降级判定强度**：avg-hash 重复从 WARNING 升级为"降级待复核"判定后，若无人工复核记录则阻断——需保证有合法复核路径（P6-acceptance.md 记"人工复核记录"字段），否则误伤合法行为差异类 BDD 截图视觉相同的场景
4. **文档联动 45 文件**：一处改动须同步全部联动点（见 §6 影响面核对清单），P7 一致性检查按清单核

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

**BDD-1 落点**：
- `assets/execution-roles/analyst.md` 产出规格节：新增"domains 含 frontend 的 P1 必须含至少一条 UX 类别 BDD（键盘可用性 / 显示内容正确性 / 样式呈现中至少一类用户可观测行为），类别写入 BDD 标题后缀（如 `BDD-3: 键盘可用性：...`），缺失时 requirements-review 打回"
- `phase-cards/P1-requirements.md` 产出规格节 + 常见错误节：对应条文
- `assets/review-roles/requirements-review.md` 检查清单：新增评审要点"frontend 任务 P1 是否含 UX 类别 BDD（键盘/显示/样式）"

**BDD-2 落点**：
- `assets/execution-roles/analyst.md` BDD 反模式自检清单（196 行附近）扩展：新增两条——"□ 若为 UX 类别 BDD，Then 子句是否可被用户可观测行为二值判定（PASS/FAIL）？"、"□ UX 类别 BDD 是否不绑定具体 CSS 类名/组件名/工具名？"

**gate/单测**：BDD-1/2 验收方式为"读文档确认"，不新增 gate 逻辑。单测以文档内容检查为主——新增 `test_docs_ux_bdd_requirements.py`（或在既有 test_check_protocol_consistency.py 补一致性规则）：grep analyst.md + P1 卡片含"UX 类别 BDD"/"键盘"等锚点词，断言存在（文档漂移保护）。一致性规则在 check-protocol-consistency.py 补：analyst.md 必须含 UX 类别 BDD 要求条文。

### 2.3 BDD-4：P2 UI 设计节 gate 检查

**协议条文落点**：
- `assets/execution-roles/architect.md`：
  - §输出（39 行 ui_affected 字段说明处）补：`ui_affected: true` 时 P2-design.md 必须含「UI 设计」节（`## UI 设计`），节内至少覆盖布局 / 交互 / 视觉三类 checklist，由 architect 兼任产出
  - 补 UI 设计节结构规格（见 §2.4）
- `phase-cards/P2-design.md`：产出规格 + gate 规则补"ui_affected: true → UI 设计节检查"
- `assets/templates/task-files.md` P2 模板（227-311 行）补 UI 设计节样例
- `agate-frontmatter-check.py`:56-74 P2 schema 可加**可选字段**（如 `ui_design_section: true`，bool，可选，presence 语义）——供 P2 gate 读取，不破坏旧 fixture（旧 P2-design 无该字段 = 未声明 UI 节 → 检查仅在 frontmatter `ui_affected: true` 且（无该字段或缺节）时触发）

**gate 逻辑（check-gate.py gate_p2）**：
- 新增 helper `_gate_p2_ui_design_section(p2_file)`：
  1. `_md_field_get("ui_affected", p2_file)`；非 `true` → 通过
  2. 解析 P2-design.md：要求含 `## UI 设计`（或 `### UI 设计`）节标题
  3. 节内须出现三组 checklist 锚点关键词：布局（layout/布局）、交互（interaction/交互）、视觉（visual/视觉）各至少一次
  4. 缺标题或缺任一组关键词 → `sys.stderr.write("GATE P2: ui_affected: true 但缺 UI 设计节（须含布局/交互/视觉三类 checklist）")` → return 1
- **兼容**：既有 fixture 中 full-task/high-risk/paused-task 的 P2-design 均 `ui_affected: false` → 不触发；`ui-affected/P2-design.md` 与 `vision-blocked/P2-design.md` 两个均为 `ui_affected: true` 但无 UI 设计节 → 若被 P2 gate 测试消费会命中（触发条件仅为 P2 自身 `ui_affected: true`，与 §0.3 风险 2 对齐）。但**二者均不用于 P2 gate 测试**：test_check_gate 用自建 fixture、不引用静态夹具目录；二者均 P6 专用（ui-affected 测 P6 双证据路径、vision-blocked 测 P6 GAP/blocker 降级演示）→ 新 P2 检查不会命中，兼容成立。已核实 test_check_gate 无静态夹具引用

**单测（test_check_gate.py）**：
- `test_ui_design_1_ui_true_missing_section_exit_1`：构造 ui_affected:true 无 UI 设计节 P2 → exit 1
- `test_ui_design_2_ui_true_full_section_exit_2`：含 ## UI 设计 + 布局/交互/视觉关键词 → exit 2
- `test_ui_design_3_ui_true_missing_keyword_exit_1`：含节标题但缺"视觉"关键词 → exit 1
- `test_ui_design_4_ui_false_no_section_exit_2`：ui_affected:false 无节 → 不触发 exit 2（兼容）

### 2.4 BDD-5：UI 设计节规格（architect 兼任产出）

**architect.md 补充的 UI 设计节结构规格（协议条文内容）**：

```markdown
## UI 设计（ui_affected: true 时 P2-design.md 必含）

### 布局 checklist
- [ ] 页面/组件层级结构（Header/Content/Footer 或等效分区）已描述
- [ ] 关键区域占位关系（主区/侧栏/弹层）已描述
- [ ] 桌面与移动两档 viewport 布局均说明（对应 P3 的 desktop_1280x800 / mobile_390x844 截图）

### 交互 checklist
- [ ] 键盘可达性（Tab 顺序 / 焦点可见 / 回车激活）已覆盖
- [ ] 输入态变化（输入 → 界面状态变化）已定义或声明"无输入态用例"
- [ ] 反馈（loading/error/empty/disable 态）已覆盖
- [ ] 输入态变化类用例若存在：宣称需人工复核（对应 P6 BDD-13）

### 视觉 checklist
- [ ] 颜色/对比度（主色/背景色/WCAG AA 对比）已说明
- [ ] 字体层级（字号/字重）与间距节奏已说明
- [ ] 组件一致性（圆角/阴影/图标风格）已说明
```

**role-system.md**：确认不新增 designer 角色——在角色清单表后补一行注明"UI 设计节由 architect 兼任产出（P2），不新增角色"。

### 2.5 BDD-6：plan-design-review 增视觉/交互维度

**plan-design-review.md 维度表（13-21 行）扩容**，五维 → 七维：

| 维度（现有） | 维度（新增后） |
|------|------|
| 交互状态覆盖率 | **交互状态覆盖率**（保留，措辞微调：交互设计维度） |
| AI Slop 风险 | AI Slop 风险（保留） |
| 移动端考虑 | 移动端考虑（保留） |
| 可访问性 | **可访问性 / 键盘可达**（升级，含键盘导航 + 输入态反馈） |
| 组件完整性 | 组件完整性（保留） |
| — | **视觉设计**（新增：布局一致性／颜色对比度／字体层级／组件一致性等，0-10 可判定评分） |
| — | **交互设计细节**（新增：输入态反馈／禁用态／过渡动画等，0-10 可判定评分） |

每新增维度配 0-10 评分项："""视觉设计：布局一致性（0-2）／颜色与对比度（0-3）／字体与间距（0-3）／组件一致性（0-2）"""（合计 0-10）；"""交互设计细节：输入态反馈（0-4）／键盘可达与焦点（0-3）／过渡与禁用态（0-3）"""。

- 适用口径：**frontend 任务评审时启用**（受评对象是 P2-design.md 的 UI 设计节）。UI 设计节缺失时该维度直接 0 分（联动 BDD-4）
- **七维边界注（写入 plan-design-review.md 维度表，防 double count）**：**"交互状态覆盖率"= 状态存在性**（审「loading/error/empty/edge 等状态是否被 spec 覆盖」），**"交互设计细节"= 状态内实现质量**（审「输入态反馈/过渡/禁用态等具体实现细节质量」）——前者回答"各状态有没有被覆盖"，后者回答"覆盖到的状态实现得够不够好"，同一问题不允许跨两维重复打分
- 同时 `role-system.md` 中 role 表 plan-design-review 行（45 行）职责描述同步（"spec 交互完整性 + 视觉设计"）

**单测**：新增 `tests/unit/test_review_role_docs.py`（读 plan-design-review.md 断言含"视觉设计"与"交互设计"维度名），并入一致性检查（check-protocol-consistency.py 增加该文件关键词锚点规则）。

### 2.6 BDD-7：Windows GUI 自动化框架评估

见 §4（本文件独立小节，调研结论"保持现状"）。

### 2.7 BDD-8：影响面核对清单

见 §6（与 P1 影响面清单对齐核对）。

### 2.8 BDD-9：P6 双证据 + 视觉质量 checklist（vision 三态分档）

**verifier.md 改动**：
- §UI 任务追加约束（104-108 行）改写：`ui_affected: true` 时每条 UI 类 PASS 必须同时含——运行时证据（截图/行为日志）+ 视觉证据；视觉证据形式按 P1 声明的 vision 能力状态分档：
  - `available`/`supplementable` → vision YAML 引用 `(vision: vision-reports/bxx.yaml)`（含既有 UI 追加约束：blocker_count=0、≤1KB 处理）
  - `GAP` → 降级为"像素检测 + 人工复核记录"：PASS 行引 `(screenshots/bxx.png)` + `(manual-review: review-bxx.md)`，**不要求 vision YAML 引用**
  - 读取三态声明来源：P1-requirements.md capability_requirements（视觉条目 status）
- **无视觉能力声明的默认语义（兼容回归锚点）**：P1 的 capability_requirements 无 `need` 含 visual/vision 条目（无视觉能力声明）时 → 视为 **available 语义**——保留既有 R1b 强制（截图 PASS 必须引 vision YAML）与 blocker_count=0 流程；**GAP 分支仅在 P1 显式声明 status: GAP 的任务触发**，不因"无声明"落入 GAP 放行。该默认保证既有无声明任务（如 test_pv_11/12/13、integration T086 等 create_task_dir 默认 P1）的 P6 行为与基线完全一致（BDD-15 不红），并有兼容回归用例固化（test_vision_none_1）
- §P6 处理流程（175-182 行）补第 0.5 步：先读 P1 声明 vision 三态 → 决定证据路径
- §UI 条件的处理流程 补"视觉质量 checklist 核对"：逐条对照 P1 UX 类别 BDD + P2 UI 设计节（布局/交互/视觉 checklist），在验收报告中记录 checklist 核对结果（每项 checked/unchecked + 依据），不只写"渲染成功"

**P6 卡片改动**：
- 产出规格补双证据分档条文 + vision 能力三态读取来源
- gate 规则段补：GAP 分支的视觉证据为"像素检测 + 人工复核记录"，check-p6-evidence.py 校验

**check-p6-evidence.py 改动**：`ui_affected == "true"` 时读取 P1 的 vision 三态声明，GAP 分支豁免"含截图 PASS 必须引 vision YAML"这一层（该层现由 check-p6-provenance R1b 执行，需同步：GAP 分支改为校验"人工复核记录文件存在"）。⚠️ 注意：本脚本本身不校验 vision YAML 引用存在性（那是 provenance），本任务只新增 GAP 分支"人工复核记录文件"存在性检查（截图 PASS + 复核记录引用 → 放行）。

**check-p6-provenance.py 改动（核对 + GAP 分支）**：R1b 审计在 P1 声明 vision=GAP 且该任务已验证降级路径时，不强制 vision YAML（改为要求"人工复核记录"被 PASS 引用）。改动点：读取 P1 capability 视觉条目 status，GAP → R1b 对该任务的截图 PASS 放宽 vision 强制。

**单测（test_check_p6_evidence.py + test_check_p6_provenance.py）**：
- `test_vision_gap_1_evidence_manual_review_exit_0`：P1 vision=GAP + 截图 + `manual-review` 文件被引用 → exit 0
- `test_vision_gap_2_evidence_missing_review_exit_1`：P1 vision=GAP + 截图但不引复核文件 → exit 1
- `test_vision_avail_1_evidence_no_vision_yaml_exit_1`：P1 vision=available + 截图 PASS 无 vision YAML → exit 1（既有 R1b 语义保持，新增回归保护）
- `test_vision_none_1_no_decl_evidence_no_vision_yaml_exit_1`：**P1 无视觉能力声明（capability_requirements 无 need 含 visual/vision）+ ui_affected:true + 截图 PASS 无 vision YAML → exit 1**（无声明默认 available 语义——不落入 GAP 放行；兼容回归，守护 BDD-15 基线，对应 test_pv_11 现有断言）
- `test_vision_docs_1_verifier_has_triple_state`：读 verifier.md 断言含 available/supplementable/GAP 分档条文（文档漂移保护）

### 2.9 BDD-10：vision available 时 P6 必须真实视觉分析

**落点**：
- P6 卡片「vision-helper 结论绑定」（126-130 行）已有"可用 blocker_count > 0 时不能仅用程序化指标反驳"。补充条文："P1 声明 visual 能力 status=available 时，P6 必须执行真实视觉分析（截图 → 结构化描述 → 判定），不得仅以 naturalWidth>0 / complete=true / HTTP 200 断言视觉 PASS"
- verifier.md §行为验证证据优先级（78-80 行）标注 vision-analyst 视觉分析为 available 分支的硬性证据

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

### 2.12 BDD-13：输入态变化类用例人工复核

**"输入态变化"判定标准（写入 verifier.md + P6 卡片）**：
```
输入态变化类用例 = 用户输入（键盘/鼠标/粘贴/手势）导致界面状态发生变化的用例。
判据：BDD 的 When 子句含输入动作（输入/点击/按键/滚动）且 Then 子句断言的界面状态（显示内容/样式/组件状态）与该输入相关。
```
- 非输入态类（静态渲染、查询结果展示）→ 不触发人工复核
- 输入态类（表单输入、键盘导航、焦点转移）→ P6 结论必须附人工复核记录

**落点**：
- verifier.md §UI 追加约束补：输入态变化类 BDD 的 PASS/FAIL 结论必须附人工复核记录（复核人 / 复核时间 / 复核结论），不能仅由自动断言通过；判定标准见本节
- P6 卡片补对应条文 + PASS 行样例：`- PASS BDD-N: ... (screenshots/x.png) (vision: ...) 人工复核: 张三 2026-08-17 确认输入态正常`
- `assets/templates/task-files.md` P6 模板补人工复核记录样例

**单测**：`test_vision_docs_3_input_state_review`（读 verifier.md + P6 卡片含输入态判定标准条文）；check-p6-evidence/check-gate P6 不新增 gate（人工复核记录是 verifier 自述性质，靠文档条文约束 + P7 一致性检查兜底，符合 self-authored gate 缓解层次）。

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

**单测（test_check_p6_evidence.py）**：
- ⚠️ **构造前置门禁（test_ahash_* 共用）**：测试 PNG 必须同时满足 check-p6-evidence 执行序的前置——文件 **>1KB**（≤1KB 会先被"evidence 非文本"检查 exit 1）且**像素方差 ≥50**（方差<50 会先触发方差 WARNING→exit 2，遮挡 ahash 判定）；故测试 PNG 须为**非纯色图**（PIL 生成含内容/噪声/渐变图，不能纯色填充），并显式断言生成文件尺寸与方差满足门禁再进入 ahash 断言
- `test_ahash_1_duplicate_with_review_record_exit_0`：构造两张同 visual content 不同文件名截图（用 PIL 生成同像素不同编码的非纯色 PNG，或 base64 写两版，均满足 >1KB + 方差≥50）+ P6-acceptance 含"雷同截图复核"记录 → exit 0（最小验证已实测：同视觉内容不同字节 → ahash 相同、md5 不同）
- `test_ahash_2_duplicate_no_review_record_exit_1`：同上但不含复核记录 → exit 1（行为从 WARNING 改为判定）
- `test_ahash_3_no_duplicate_exit_0`：不同 visual 内容 → 不受影响
- ⚠️ Pillow 缺失时 ahash 直接 SKIP（现有行为）→ 测试用 `pytest.importorskip("PIL")` 包裹，无 Pillow 环境自动 skip（平台无关原则，不硬编码 /tmp 等路径，用 tmp_path）

### 2.14 BDD-15：兼容回归

**单测**：不新增（回归本身是执行验证，见 gate_commands）。实施后跑：全量 pytest（基线 825 + 新增用例全绿）+ `check-protocol-consistency.py` 0 ERROR + `count-tests.sh` 计数无漂移（≥749 且单调不减）。

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
```

## 6. 影响面核对清单（BDD-8，对齐 P1 影响面清单）

> 与 P1 §8 的 45 文件 / 64 处口径逐项核对。P1 清单含 45 文件（协议文档 + 脚本 + 测试夹具）；P2 全量再扫描 `agate/` 树 `rg -l 'ui_affected|vision-analyst|plan-design-review|vision-helper'` = 45 文件，**与 P1 一致**。以下按 P1 分类逐项列同步动作，缺失项即 P7 一致性检查核对点。

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

### 6.2 Gate 脚本（agate-scripts-py）

| 脚本 | 联动点 | 本方案改动 |
|------|--------|-----------|
| `check-gate.py` | P1/P2 gate | ① gate_p1 新增 vision 三态检查（BDD-3）；② gate_p2 新增 UI 设计节检查（BDD-4） |
| `check-p6-evidence.py` | 156-181 行 ui_affected 证据、261 行 avg-hash | ① GAP 分支改"人工复核记录文件"证据检查（BDD-9）；② avg-hash 从 WARNING 改降级待复核判定（BDD-14） |
| `check-p6-provenance.py` | 277-313 行 R1b vision YAML 审计 | GAP 分支放宽 vision 强制（要求复核记录替代），available 分支语义不变（BDD-9） |
| `agate-md-field-get.py` | 175-176 行 ui_affected op | 核对即可（ui_affected op 已有）；不新增 op（UI 设计节用 body 节标题检测，非 frontmatter 字段） |
| `agate-frontmatter-check.py` | 56-74 行 P2 schema | P2 schema 增加可选字段 `ui_design_section`（bool，可选，presence 语义），不破坏旧 fixture |
| `agate-vision-blocker.py` | blocker_count | 核对，兼容保留 |
| `agate-extract-context.py` | 126-133 行 P2 字段 | 核对；不新增字段（UI 设计节用 body 检测） |
| `check-protocol-consistency.py` | 355 行 P5_e2e 模板、542 行 ui_affected 关键词 | 新增一致性规则：① analyst.md/P1 卡片须含 UX 类别 BDD 要求（BDD-1）；② plan-design-review.md 须含"视觉设计"维度（BDD-6）；③ verifier.md/P6 卡片须含三态分档/输入态复核条文（BDD-9/13） |
| `ci-gate-backstop.py` | 无直接命中 | 核对，兼容（新检查在 push 后 CI 重跑 gate 时自动覆盖） |

### 6.3 测试与夹具（agate-tests）

| 文件 | 联动点 | 本方案改动 |
|------|--------|-----------|
| `tests/unit/test_check_gate.py` | P1/P2 gate 用例 | 新增 BDD-3/4 用例（vision 三态缺失/非法/兼容 + UI 设计节缺失/完整/兼容） |
| `tests/unit/test_check_p6_evidence.py` | avg-hash WARNING 用例 | 改/增降级判定用例（同 content 不同名 → 有/无复核记录） |
| `tests/unit/test_check_p6_provenance.py` | 240 行 vision blocker | 增 GAP 分支用例（vision=GAP 时 R1b 放宽） |
| `tests/unit/test_agate_md_field_get.py` | ui_affected op | 核对，无新增 op |
| `tests/unit/test_check_frontmatter.py` | P2/P6 schema | 增 P2 可选字段 `ui_design_section` 用例 |
| `tests/unit/test_agate_vision_blocker.py` | 2 用例 | 核对，兼容 |
| `tests/unit/test_agate_extract_context.py` | P2 字段 | 核对，无新字段 |
| `tests/unit/test_agate_capture_env_baseline.py` | 环境基线 | 核对，无关不动 |
| `tests/integration/test_pre_commit_hook.py` | hook 集成 | 核对；若 pre-commit P1/P2 gate 行为变则补用例（新增检查均在 check-gate.py 内，hook 行为通过脚本化自动覆盖，预计无需改） |
| `tests/unit/test_dispatch_orchestration.py` | 派发/A3 | 补 supplementable 视觉语境注入用例（BDD-11） |
| `tests/fixtures/{...}/P2-design.md` | 既有夹具 | 核对：full-task/high-risk/paused-task 三个 `ui_affected:false` → 不触发新 P2 检查；**`ui-affected` 与 `vision-blocked` 两个均 `ui_affected:true` 且无 UI 设计节——但均不用于 P2 gate 测试（test_check_gate 自建 fixture，不引用静态夹具目录），P6 专用**（ui-affected 测 P6 证据路径、vision-blocked 测 P6 GAP 降级，见 §2.3 兼容段免责说明）→ 新 P2 检查不命中；新增可选字段不破坏旧 fixture |
| `tests/README.md`（58 行计数表）+ `tests/scripts/count-tests.sh` | 用例计数 | 用例数变化后更新计数期望值（≥749 且单调不减） |

### 6.4 外部联动（非协议文件，P8 处理）

- `docs/roadmap*`：RM-AG0004/0006/0007 回写 done（P8）
- `CHANGELOG.md` / `README.md` badge / `agate/UPGRADING.md`：版本发布三件套（P8）；UPGRADING 需新增"P1 frontend 任务必须声明 vision 三态 + P2 ui_affected 必须含 UI 设计节 + P6 avg-hash 降级"破坏性变更条目

## 7. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/check-gate.py:100-419
    why: gate_p1/gate_p2 结构 + _frontmatter_field/_md_field_get 模式，新增 vision 三态 + UI 设计节检查挂载点
  - path: agate/scripts/check-p6-evidence.py:148-264
    why: ui_affected 判定 + avg-hash WARNING 改降级待复核；GAP 分支证据检查
  - path: agate/scripts/check-p6-provenance.py:270-320
    why: R1b vision YAML 审计的 GAP 放宽点
  - path: agate/scripts/agate_common.py:233-310
    why: write_gate_result/read_state 等公共函数（脚本改动时复用）
  - path: agate/scripts/agate-frontmatter-check.py:56-80
    why: P2 schema 增加可选 ui_design_section 字段
  - path: agate/scripts/check-protocol-consistency.py:340-560
    why: 新增文档一致性锚点规则（UX BDD/视觉维度/三态条文）
  - path: agate/assets/execution-roles/analyst.md:75-120
    why: 能力三态机制现有条文，补 UX/vision 声明要求
  - path: agate/assets/execution-roles/architect.md:34-110
    why: 输出规格补 UI 设计节 + UI 设计节结构规格
  - path: agate/assets/execution-roles/verifier.md:104-230
    why: UI 追加约束改三态分档 + 输入态复核 + 视觉质量 checklist
  - path: agate/assets/execution-roles/vision-analyst.md:244-297
    why: 补能力自查要求 + 确认不写死工具
  - path: agate/assets/review-roles/plan-design-review.md:9-33
    why: 维度表扩容为七维
  - path: agate/assets/review-roles/requirements-review.md:14-43
    why: 补 UX/vision 评审要点
  - path: agate/phase-cards/P2-design.md:43-110
    why: 产出规格+gate 规则补 UI 设计节
  - path: agate/phase-cards/P6-acceptance.md:44-140
    why: 双证据分档/输入态复核/雷同降级条文落点
  - path: agate/dispatch-protocol.md:900-960,1160-1205
    why: gate 表 + A3 节扩展
  - path: agate/assets/templates/dispatch-prompt.md:55-160
    why: 能力自查节 + supplementable 注入位
  - path: agate/tests/conftest.py:76-262
    why: create_task_dir/add_frontmatter_field 等 fixture helpers，新测试复用
  - path: agate/tests/unit/test_check_gate.py:200-270
    why: P2 gate 测试模式（_write_p2_design/add_p2_review），新增用例沿用
  - path: agate/tests/unit/test_check_p6_evidence.py:250-345
    why: 截图证据测试模式，新增 ahash 降级用例沿用
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
- gate 脚本：check-gate.py 含 `_gate_p1_vision_capability` + `_gate_p2_ui_design_section`；check-p6-evidence.py avg-hash 降级判定；check-p6-provenance.py GAP 放宽；agate-frontmatter-check.py 可选字段；check-protocol-consistency.py 新增锚点规则
- 单测：BDD-3/4/6/9/11/12/13/14 各有对应用例（新增用例全绿 + 基线 825 全绿）
- 验收对照：P6 逐条对照 15 条 BDD，全部 PASS（BDD-15 回归靠 gate_commands 实跑）

## 10. 兼容策略确认（P1 §9 落实）

- **增量增强**：新检查只对"新声明"生效（domains=frontend / ui_affected=true）——既有 fixture P1 均无 frontend domains；既有 P2-design 中 full-task/high-risk/paused-task 三个 ui_affected:false，`ui-affected` 与 `vision-blocked` 两个均 ui_affected:true 但不用于 P2 gate 测试（P6 专用，见 §2.3）→ 基线不受影响
- **P6 双证据**：available/supplementable 分支语义与既有 R1b/blocker_count 完全一致，GAP 分支新增"人工复核记录"证据路径（P6 卡片 122-124 行既有"改用非截图证据"指引的强化版）
- **雷同截图**：md5 硬阻断不变，avg-hash 从 WARNING 升级为"降级待复核"（有复核记录放行，无则阻断）
- **回归底线**：825 基线全绿 + 新增用例全绿 + count-tests 单调不减 + consistency 0 ERROR

## 11. 断言与风险缓解

- BDD-3 P1 检查：若 future 项目既有 frontend 任务 P1 无 vision 声明 → 下次过 P1 gate 会 exit 1——这正是需求目标（强制声明），但属行为变更，需在 UPGRADING.md 写破坏性变更条（已在 §6.4 收录）
- **无声明默认语义断言**：P1 无视觉能力声明（capability_requirements 无 need 含 visual/vision）→ 视为 available 语义（证据路径保留 R1b 强制 + blocker_count，与现状完全一致），GAP 分支仅在 P1 显式声明 status=GAP 时触发——该默认由 test_vision_none_1 兼容回归用例固化（§2.8），BDD-15 基线 825 不受影响。
- avg-hash 降级判定误伤风险：行为差异类 BDD 截图视觉相同（非重复）场景——缓解：P6 卡片 122-124 行指引优先改用非截图证据；若用截图则走复核记录（复核人确认"确为不同操作但视觉相近"即可放行）
- 输入态人工复核是自述性质（verifier 自己写复核记录）——缓解：文档条文约束 + P7 一致性检查按条核对，符合 self-authored gate 缓解层次，不新增伪硬校验