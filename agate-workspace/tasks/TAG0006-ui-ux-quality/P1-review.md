---
phase: P1
task_id: TAG0006-ui-ux-quality
type: review
parent: P1-requirements.md
trace_id: TAG0006-P1-20260817
status: approved
created: 2026-08-17
agent: requirements-review
---

# P1 Review — agate UI/UX 验收质量机制

> 评审对象：P1-requirements.md（masterial 15 条 BDD，P1/P2/P6 组 + 兼容/回归组）
> 评审方式：独立 re-read + 对照 P0-brief / analyst 派发约束 / HANDOFF 双重核对 / 协议文件实地核验（state-machine、analyst 角色、dispatch-protocol A3、P6 卡片、plan-design-review 维度表、check-gate.py P1 结构）

## 评审范围与依据

- 依据 1：P0-brief 三 RM（RM-AG0007 三层修复 / RM-AG0004 五项修复 / RM-AG0006 评估）+ 强制要求（同类扫描 64 处联动面）
- 依据 2：analyst 派发约束（不写死视觉工具 / 不宣称实测 Windows / 范围锁定 / 决策已定不推翻 / 不掺解决方案）
- 依据 3：协议现状实地核验（`state-machine.md:89` ui_affected 现仅要求 E2E 交互点；`analyst.md:78-104` 三态机制已存在；`dispatch-protocol.md:1184-1202` A3 传递规则已存在；`P6-acceptance.md:35` available 前置检查已存在；`plan-design-review.md` 维度表当前为五维、确无视觉/交互维度；`check-gate.py` gate_p1 已读 P1-requirements 含 BDD 锚点 + NEED_CONFIRM 结构，新增 vision 三态检查与之兼容）

## BDD 逐条评审（格式/二值判定/覆盖维度）

### 格式合规性（全局）
- 编号格式 `#### BDD-NN:` 全部合规；BDD-1~BDD-15 连续不跳号 ✓
- 每条 BDD 单 Given-WHEN-Then、单场景 ✓；无"⚠️ 调整 / 部分通过"中间态 ✓
- 无 vision-engine 等视觉工具名绑定（BDD 正文零引用；第 39 行"需求不写死工具名"显式声明）✓
- 无 Windows 实测宣称（BDD-7 Then 显式禁止"已实测 Windows"字样）✓

### 逐条判定

- **BDD-1**（P1 须含 UX 类别 BDD）：二值可判（读 analyst.md + P1 卡片）；覆盖维度：前端✓ 边界✓（缺失时 requirements-review 打回）——与 RM-AG0007① 对应 ✓
- **BDD-2**（UX BDD 可二值判定、不绑定实现）：二值可判（读 analyst.md 反模式清单覆盖 UX 维度）；覆盖维度：前端✓ 兼容✓（延续既有 BDD 约束）——对应 RM-AG0007① ✓
- **BDD-3**（ui_affected P1 声明 vision 三态）：二值可判（check-gate.py P1 新增检查 + 构造缺失/非法态 fixture 断言 exit 1）；覆盖维度：数据✓（非法 status 值）边界✓（缺失声明）——对应 RM-AG0004① ✓
- **BDD-4**（ui_affected P2 必须含"UI 设计"节）：二值可判（check-gate.py P2 检查 + 缺节 fixture）；覆盖维度：前端✓ 数据✓（frontmatter 字段）——对应决策"UI 设计节并入 P2-design.md" ✓
- **BDD-5**（architect 兼任产出 UI 设计节，不新增 designer）：二值可判（读 architect.md + role-system.md 角色清单）；覆盖维度：前端✓ 兼容✓（不认 designer 角色）——对应决策"architect 兼任" ✓
- **BDD-6**（plan-design-review 增视觉/交互维度）：二值可判（读维度表扩容 + grep 命中）；覆盖维度：前端✓——对应 RM-AG0007②（现状核验：维度表当前五维确无视觉/交互，需求正确）✓
- **BDD-7**（P2 执行 Windows GUI 自动化框架评估）：二值可判（P2-design.md 含该节 + grep 无实测声称）；覆盖维度：多端✓（Windows 平台）兼容✓（调研非实测）——对应 RM-AG0006 ✓
- **BDD-8**（P2-design.md 含影响面核对清单）：二值可判（含影响面节 + 与 P1 影响面清单对齐）；覆盖维度：多端✓（64 处联动跨文件）——对应 P0-brief 强制要求 ✓
- **BDD-9**（P6 强制双证据 + 视觉质量 checklist）：二值可判（读 verifier.md + P6 卡片）；覆盖维度：前端✓ 兼容✓——对应 RM-AG0007③；**发现缺口：GAP 场景未限定（见下"发现 1"）** ⚠️
- **BDD-10**（available 时真实视觉分析）：二值可判（读 P6 卡片 + verifier.md）；覆盖维度：前端✓ 边界✓（不得仅用程序化指标）——对应 RM-AG0004② ✓
- **BDD-11**（supplementable 时派发 prompt 注入）：二值可判（读 dispatch-protocol A3 扩展 + dispatch-prompt 模板）；覆盖维度：多端✓（跨阶段传递）——对应 RM-AG0004①supplementable 分支 + I3 ✓
- **BDD-12**（派发 prompt 强制 subagent 能力自查）：二值可判（读 dispatch-prompt.md 模板含自查要求）；覆盖维度：多端✓ 边界✓（不能调则报告降级）——对应 RM-AG0004③ ✓
- **BDD-13**（输入态变化类用例人工复核）：二值可判（读 verifier.md + P6 卡片 + P6 产出含复核记录）；覆盖维度：前端✓ 边界✓——对应 RM-AG0004④ + I6 ✓
- **BDD-14**（雷同截图降级待复核）：二值可判（check-p6-evidence.py avg-hash 判定改造 + 构造同 content 不同名 fixture 断言行为改变）；覆盖维度：数据✓ 边界✓ 兼容✓（md5 硬阻断语义不变，见 §9）——对应 RM-AG0004⑤ + I5 ✓
- **BDD-15**（基线回归不破坏既有语义）：二值可判（pytest + consistency + count-tests 实跑）；覆盖维度：数据✓ 兼容✓——对应 I10 + I12 ✓

## 隐含需求覆盖（五维逐项）

- **数据维度**：覆盖 ✓（I5 fixture 构造、BDD-14 同 content 不同名截图、frontmatter schema 新字段不破坏旧 fixture，见 §8.3/§9）
- **前端维度**：覆盖 ✓（BDD-1/2/4/6/9/10/13/14 覆盖键盘/显示/样式/布局/交互/视觉质量）
- **多端维度**：覆盖 ✓（BDD-7 Windows 评估、BDD-11 supplementable 跨阶段传递、BDD-12 派发注入、I3 扩展 A3）
- **边界维度**：覆盖 ✓（BDD-3 缺失/非法 status、BDD-4 缺节、BDD-13 输入态变化、BDD-14 雷同截图）——**但 GAP 降级链边界缺 BDD** ⚠️
- **兼容维度**：覆盖 ✓（BDD-6 兼容既有五维度表、BDD-14 md5 硬阻断不变、BDD-15 823 回归底线、§9 增量增强策略）

隐含需求 I1-I12 逐条核对：I1→BDD-4、I2→BDD-3、I3→BDD-11、I4→BDD-12、I5→BDD-14、I6→BDD-13、I7→BDD-8、I8→（并入 BDD-3/4/14 单测的测试约定，I8 本身是测试平台无关原则，由 AGENTS.md + TAG0009 gate 兜底，非需求层 BDD 强制项，合理）I9→SELF-GATE hook 机制（非 BDD 可判项，属开发纪律，合理）、I10→BDD-15、I11→BDD-7、I12→BDD-15。全部覆盖或合理归因 ✓

## 裁剪评审（零裁剪）

`phases: [P1,P2,P3,P4,P5,P6,P7,P8]` 全保留，每阶段理由逐项充分：
- P3 保留：risk_level=medium 非 low，TDD 不可裁，且 gate 脚本改动必须走先红后绿——正确 ✓
- P6 保留：15 条 BDD 需逐条验收——正确 ✓
- P7 保留：`implicit_coupling: true`（64 处联动）仅 P7 能查联动遗漏——正确 ✓
- P8 保留：协议本体版本发布（badge/CHANGELOG/UPGRADING/tag）——正确 ✓

## 能力三态评审（available/supplementable/GAP 语义）

- **pytest-test-runner**: `available` ✓（本机 python3 + pytest 已确认，P0-brief env_constraints）
- **pyyaml**: `available` ✓（gate 脚本读取 frontmatter 所需，本机具备）
- **visual-analysis**: `supplementable` ✓（本任务无 UI 产物，P6 以脚本单测+文档内容为核心证据；available 来源列 agate 内置 vision-analyst 角色 + 视觉分析 skill，不硬编码工具名；标 supplementable 而非 GAP 合理——有已知可用来源）
- **gui-e2e-framework-win**: `supplementable` ✓（P2 评估靠文档/网络调研可完成，network=full；`gap_note` 诚实声明无真实 Windows GUI、结论不得宣称实测；不阻塞合理）

无 `status: GAP` 条目 → 不触发 [CAPABILITY_GAP] 暂停 ✓；无未决 [NEED_CONFIRM]（[NO_NEED_CONFIRM] ×2 + 1 个格式合法 [SUGGEST:] 非阻塞）✓

## 影响面清单评审（同类扫描 + 联动面）

- §8 清单覆盖 45 个协议/脚本/测试文件，每项列明联动点行号 + 改动要求，粒度充分 ✓
- 45 vs P0-brief"64 处"差异已明确解释（45 = worktree `agate/` 全树 rg 结果含 15 个测试/夹具文件；64 = P0-brief 口径含 docs/roadmap 等非协议文件），且 BDD-8 要求 P2 再次全量核对——处理方式合理 ✓
- 协议文档 8.1 / 脚本 8.2 / 测试 8.3 / 外部联动 8.4 四分结构清晰，覆盖 state-machine/角色文件/阶段卡片/模板/脚本/测试夹具 ✓

## 发现（需修改项）

### 发现 1（需修改，非拒稿但必须修）— GAP 降级链未 BDD 化，且与 BDD-9 存在语义冲突

**位置**：BDD-9（P6-acceptance 组）。

**问题**：BDD-9 Then 明文"每条 UI 类 PASS 必须同时含运行时证据（截图/行为日志）与视觉证据（vision YAML 引用）"，未限定 capability 状态。而 RM-AG0004① 三态声明中 **GAP（无视觉能力）→ 降级为"双证据截图+行为日志 + 像素检测 + 人工复核"**——GAP 任务无法产出"vision YAML 引用"（P6-acceptance.md:35 前置检查已声明 available 才走真实视觉分析）。当前 15 条 BDD 中无一条定义 GAP 场景的 P6 验收路径（BDD-10 限 available、BDD-14 限雷同截图、BDD-13 限输入态，均非 GAP 一票到底降级链）。

**影响**：未来某任务声明 vision=GAP 时，BDD-9 的"每条 PASS 必含 vision YAML"将不可满足（像素检测 + 人工复核无 vision YAML 可引）——协议对 GAP 任务的 P6 验收标准处于真空。本任务自身声明 visual-analysis 为 supplementable 不暴露此坑，但需求基线描述的是机制对任意任务的行为，GAP 分支必须有定义。

**建议修复**（任选其一即可，P2 前由 analyst 完成）：
1. **修改 BDD-9**：限定"视觉证据"为"vision YAML 引用（vision 能力 available/supplementable 时）或像素检测 + 人工复核记录（vision 能力 GAP 时）"，使 GAP 降级链成为 BDD-9 的显式分支；或
2. **新增 BDD-16**：定义"vision=GAP 的 ui_affected 任务，P6 以像素检测 + 人工复核记录作为视觉证据、不要求 vision YAML"，并按 P6 组编号插入（编号连续性保持 1-16）。

### 发现 2（minor，非阻塞）— BDD-15 误用"823"表述

BDD-15 Then "既有 823 用例（含新增用例）全绿"——823 为既有基线数，新增用例后总数会 >823，括号"含新增用例"与"823"并存易被误读为"总数必须仍是 823"。建议改为"既有 823 基线用例全绿 + 新增用例全绿"。不影响可判定性（实际验证以 pytest 全绿 + count-tests 无漂移为准），不阻塞，仅表述精确性建议。

## 结论

- **判定**：`needs-revision`
- **总评**：需求基线整体高质量——15 条 BDD 全部二值可判、编号连续、单场景、无工具名绑定；RM-AG0007 三层修复 + RM-AG0004 五项修复 + RM-AG0006 评估要求全覆盖；影响面清单 45 文件详实；零裁剪理由逐项充分；能力三态判断正确、无 GAP 阻断；P1 纯净性良好（BDD 验收对象为协议文档/gate 脚本/单测的产出行为，符合本任务特殊性，未掺 P2 方案细节）。
- **阻塞修订点**：仅 1 项——BDD-9 与 GAP 降级链的语义冲突（发现 1）；建议按发现 1 的修复方案（改 BDD-9 或新增 BDD-16）修订后复审，其余 14 条 BDD 与全部声明判定通过。

---

## 复审记录（2026-08-17，第二轮）

> 上轮结论 `needs-revision`，阻塞点 1 项（发现 1）+ 可选项 1 项（发现 2）。analyst 已按 fix 派发约束修复，本轮复审如下。

### 复核发现 1（BDD-9 与 GAP 降级链语义冲突）— 已解决 ✓

- BDD-9 已制入 GAP 降级分支：Then 子句现明文规定「视觉证据的形式按该任务 P1 声明的 vision 能力状态分档——available/supplementable 时须为 vision YAML 引用，GAP 时降级为『像素检测 + 人工复核记录』且不要求 vision YAML 引用」——GAP 任务的 P6 视觉证据路径已定义，与 RM-AG0004① 三态降级语义一致，不再存在「GAP 任务无法满足『必含 vision YAML』」的真空。
- 验收方式已同步补 GAP 条文：验收方式明写「读 verifier.md + P6 卡片含该要求（含 vision 能力 GAP 分支的降级路径条文）」——GAP 分支的可判定锚点实体化（文档是否含该分支条文，二值可判）。✓
- 二值可判性复核：BDD-9 整体 Given/When/Then 仍为可明确判定 PASS/FAIL 的单一场景；无中间态；不绑定工具名（「像素检测」「人工复核记录」为机制描述非工具名）。✓
- 交叉一致性：BDD-9（三态分档）与 BDD-10（限 available 真实视觉分析）、BDD-11（限 supplementable 派发注入）、BDD-13（输入态复核）、BDD-14（雷同截图降级）无冲突——BDD-10/11/13/14 各自限定能力状态或场景，BDD-9 为总纲性双证据条款，逻辑自洽。✓

### 复核发现 2（BDD-15 表述精确化）— 已处理 ✓

- BDD-15 Then 已改为「既有 823 基线用例全绿 + 新增用例全绿、consistency 0 ERROR、count-tests 计数无漂移」——去除「（含新增用例）」与「823」并存造成的总体数误读；语义与编号（BDD-15）均未变。✓

### 复核 BDD 编号连续性与未授权改动 — 通过 ✓

- `#### BDD-NN:` 编号 BDD-1~15 连续不跳号（grep 复核 15 条）；采纳"修改 BDD-9"方案（非新增 BDD-16），编号维持 15 条与原 fix 约束一致。✓
- 已 approved 的 14 条 BDD（BDD-1~8、BDD-10~14）语义与上轮逐条判定一致，无重写、无改号、无工具名引入——抽查 BDD-1/3/6/10/12/14 原文与上轮判定描述吻合。✓
- frontmatter 未动（status: draft / agent: analyst / trace_id / risk_level / phases / packages / domains 与上轮一致）；无 [NEED_CONFIRM]（[NO_NEED_CONFIRM] ×2 + 非阻塞 [SUGGEST:] 保留）。✓

### 本轮最终判定

- **判定**：`approved`
- **覆盖维度清单**：每条 BDD 均二值可判，覆盖维度逐条复核——
  - 前端：BDD-1/2/3/4/5/6/9/10/13/14 ✓
  - 数据：BDD-3（缺失/非法 status 值）/BDD-14（同 content 不同名截图 fixture）✓
  - 多端：BDD-7（Windows 评估）/BDD-8（64 处联动跨文件）/BDD-11（supplementable 跨阶段传递）/BDD-12（派发注入）✓
  - 边界：BDD-3（缺失/非法）/BDD-4（缺节）/BDD-13（输入态变化）/BDD-14（雷同截图）+ **BDD-9 新增 GAP 降级边界（上轮缺口）** ✓
  - 兼容：BDD-2/5/6/9/10/14/15（既有 gate 语义、md5 硬阻断、823 回归底线）✓
- 3 个 RM（RM-AG0007 三层 / RM-AG0004 五项 / RM-AG0006）覆盖完整；零裁剪理由逐项充分；能力三态判断正确、无 GAP 阻断；P1 纯净性保持（验收对象为协议文档/gate/单测产出行为，未掺 P2 实现方案）。
- 上轮全部判定（其余 14 条 BDD + 影响面清单 + 裁剪 + 三态）维持不变，修订点与本轮复核均已闭合。

> 结论：修复彻底、无新问题引入，同意推进 P1 → gate 通过 → 进入 P2。