---
phase: P2
task_id: TAG0006-ui-ux-quality
type: review
parent: P2-design.md
trace_id: TAG0006-P2-20260817
status: approved
created: 2026-08-17
agent: plan-design-review
---

# P2 设计评审 — 前端/UI 设计维度（plan-design-review）

> 评审对象：P2-design.md（547 行，candidate_count=4，方案 A 选定）。
> 评审范围：本任务方案定义的是"业务任务 ui_affected: true 时的协议机制"（前端维度 = UI/UX 验收机制的协议设计），**不是本任务自身 UI**（本任务 ui_affected: false，无 UI 产物）。
> 评审方式：逐条对照 15 条 BDD 的协议条文落点 + gate 逻辑 + 单测三件套是否完整可判定，并对方案提出修改意见。

## 一、结论摘要

方案 A（三态能力声明的"硬声明 + 降级链"双层机制）方向正确、机制设计完整、覆盖全部 15 条 BDD，BDD-7/8/15 处理扎实，兼容策略经核对（fixtures P1 均无 domains:frontend、test_check_gate 自建 fixture 不引用静态夹具）基本成立。**但存在一处设计文档内部矛盾（§0.3 风险2 的触发条件描述与 §2.3 gate 逻辑冲突），必须在 P4 前修正，否则 implementer 与 P6 验收对"BDD-4 检查触发条件"产生歧义，可能实现出弱化/错配行为**。故判定 **needs-revision**（非 rejected——机制本体不推翻，修正矛盾 + 补两处边界说明即可推进）。

## 二、维度评分（0-10）

| 维度 | 评分 | 说明 |
|------|------|------|
| 交互状态覆盖率 | 9 | ui_affected 任务 P2 必含交互 checklist（输入态/键盘/反馈），§2.4 模板覆盖 loading/error/empty/disable/输入态变化 |
| AI Slop 风险 | 8 | 布局/交互/视觉三类 checklist 强制模板化 + BDD-2 禁绑 CSS 类名/工具名收窄了"随便搞"空间；但缺 objective 反模式扫描（结构性局限 3，非本方案能根治） |
| 移动端考虑 | 9 | §2.4 明确要求桌面/移动两档 viewport 布局并对应 P3 截图（desktop_1280x800 / mobile_390x844） |
| **可访问性/键盘可达** | 8 | 升级为"键盘导航 + 输入态反馈"（§2.5），键盘可达性入交互 checklist（§2.4）+ P6 输入态人工复核（§2.12）；核心链路成立 |
| 组件完整性 | 8 | UI 设计节要求结构层级/占位关系/组件一致性描述，绑定 P6 视觉质量 checklist 逐项核对（§2.8）；与 BDD-4 联动（缺节→P2 拦截）自洽 |
| **视觉设计（新增维度）** | 8 | 布局一致性0-2/颜色对比度0-3/字体间距0-3/组件一致性0-2=10 分，子项均为可客观打分的落地项；**建议**补充——明确与"交互状态覆盖率/交互设计细节"的边界（防止 double count） |
| **交互设计细节（新增维度）** | 7 | 输入态反馈0-4/键盘可达焦点0-3/过渡禁用态0-3=10 分，可判定；与"交互状态覆盖率"（审"各状态是否被覆盖"vs"交互实现细节质量"）边界需在文档中显式标注 |

扩容意见（约束 5）：七维扩容方向正确，未遗漏关键 UX 维度（响应式断点行为、加载性能感知属非 spec 阶段范围，移动端维度已覆盖视口档位，可接受）。

## 三、逐 BDD 核对（引用 §2.x + 三件套）

### P1 组

- **BDD-1（UX 类别 BDD 基线）** — §2.2 落点在 analyst.md 产出规格 + P1 卡片 + requirements-review.md 评审点，验收方式为"读文档"符合 P1 §3 约定。✅ 完整
- **BDD-2（UX BDD 可二值判定/不绑实现）** — §2.2 扩展 analyst BDD 反模式清单两条（用户可观测行为二值判定 + 不绑 CSS 类名/组件名/工具名）。✅ 完整
- **BDD-3（vision 能力三态声明 P1 gate）** — §2.1 `_gate_p1_vision_capability` + 4 条单测（缺失/非法态/GAP 合法/backend 兼容）。经核实：fixtures P1 均无 domains:frontend → 不误伤基线。✅ 完整
  - ⚠️ 注意：`_md_field_get` 无 `capability_requirements` op（agate-md-field-get.py op 列表无此项），§2.1 采用 check-gate 内嵌 yaml.safe_load 解析正文块；minimal_validation 第 3 项确认"块边界用 '## ' 章节分隔定位"——实际 P1 中 capability 是 ```yaml 代码围栏块，建议 P4 用"围栏提取"而非"## 章节分隔"（minimal_validation 描述写的是章节定位，与代码围栏实际结构不符，P4 实现时须按围栏提取，不影响机制可行性，归档为实现级澄清）。

### P2 组

- **BDD-4（ui_affected 任务 P2 必含 UI 设计节）** — §2.3 `_gate_p2_ui_design_section` 检测 `##/### UI 设计` 标题 + 布局/交互/视觉三类关键词 + 4 条单测；模板 §2.4 与检测关键词自洽。**❌ 触发条件存在文档矛盾（见问题 1）**，修正后完整。
- **BDD-5（architect 兼任，不新增 designer）** — §2.4 role-system.md 补注 + architect.md 声明；经核实 architect.md:39 已含 ui_affected 字段说明可承接。✅ 完整，边界清晰（架构=architect，UI 设计节产出=architect 兼任并经 plan-design-review 审）
- **BDD-6（plan-design-review 增视觉/交互维度）** — §2.5 五维→七维 + 双 0-10 分项；经核实现有 plan-design-review.md:13-21 确为五维，扩容方向正确。✅ 完整（边界说明见建议 2）
- **BDD-7（Windows GUI 评估）** — §4 保持现状 + 理由 3 条 + 明确"不写已实测 Windows"。调研非实测诚实边界。✅ 完整
- **BDD-8（影响面核对清单）** — §6 逐文件列同步动作（docs/gate/tests 三表 + 外部联动），P2 全量 rg 45 文件与 P1 一致。✅ 完整

### P6 组

- **BDD-9（P6 双证据 + 视觉质量 checklist + 三态分档）** — §2.8 verifier.md/P6 卡片/check-p6-evidence/check-p6-provenance 四处联改：available/supplementable→vision YAML，GAP→像素检测+人工复核记录。经核对 check-p6-evidence.py 现 156-264 行 R1a 与 check-p6-provenance.py 277-313 行 R1b 结构、GAP 分支与设计描述一致。✅ 完整
- **BDD-10（available 时 P6 真实视觉分析）** — §2.9 P6 卡片 + verifier.md 条文"禁止仅以 naturalWidth/HTTP 200 断言"。✅ 完整（证据必需性由 BDD-9 兜底）
- **BDD-11（supplementable 派发注入）** — §2.10 A3 扩展视觉语境绑定；经核实 dispatch-protocol.md A3 现有规则（1184-1204）为"读 P1 提取 supplementable→注入对应阶段 prompt"，扩展点明确。✅ 完整
- **BDD-12（subagent 能力自查）** — §2.11 dispatch-prompt.md 新增强制"能力自查"节 + A3 注明。✅ 完整
- **BDD-13（输入态变化类人工复核）** — §2.12 判定标准（When 含输入动作 + Then 断言与此输入相关的界面状态）可二值判定，非输入态不触发；P6 结论须附复核记录。✅ 完整
- **BDD-14（雷同截图降级待复核）** — §2.13 ahash WARNING→降级判定（有复核记录放行/无则 exit 1），md5 硬阻断不变；测试用 PIL 生成同视觉不同字节 PNG（minimal_validation 已实测 ahash 同/md5 异），Pillow 缺失 skip 符合平台无关原则。✅ 完整

### 兼容/回归组

- **BDD-15（基线回归）** — §10 兼容策略四条 + count-tests ≥749 单调不减；实测当前 pytest 收集为 **825 用例**（P1 基线文字写 823，P8 发布时统一口径为 825 即可）；既有 P6 vision-helper/blocker_count/R1b 语义不动（§0.2 明确边界）。✅ 完整

## 四、评审结论

**判定：needs-revision**（非 rejected——机制本体成立，pending 修正项为文档内部矛盾，不足以推翻方案 A）。

### 必须修正（BLOCKER，回派 architect 改 P2-design.md）

**问题 1：BDD-4 检查的触发条件在 §0.3 与 §2.3 相互矛盾**
- §0.3 风险2 对策表述为："新增检查按'既有 task 数据免检'策略处理——**只在 P1 capabilities 声明 vision 且 P2 ui_affected: true 时才触发**（fixture 无 capabilities → 不触发）"
- §2.3 gate 逻辑为："`_md_field_get("ui_affected", p2_file)`；**非 true → 通过**"——即仅以 P2 `ui_affected: true` 触发，**不读取 P1 capabilities**；且 §2.3 兼容段明说 "ui-affected/P2-design.md … 设计为 P2 检查**仍触发**"
- 同一设计稿对同一检查给出两个相反的触发条件（§0.3 声称该 fixture 不触发，§2.3 声称仍触发）。BDD-4 的 Given 是"P2-design.md 声明 ui_affected: true"，不含 P1 条件，故**应以 §2.3 为准（ui_affected 单独触发）**，§0.3 描述须改为"经核实无 P2 gate 测试引用 fixtures/ui-affected（test_check_gate 自建 fixture），故该 fixture 不会被 P2 检查命中，兼容成立"，删除"需要 P1 vision 才触发"的表述。
- 风险：若不修正，P4 implementer 可能按 §0.3 实现成"需 P1 vision 声明才触发"，导致 BDD-4 验收用例（§2.3 test_ui_design_1 仅构造 ui_affected:true 缺节 P2 断言 exit 1）若不配 P1 cap 就会失败或触发条件不被满足，产生弱化检查。
- 锚点：P2-design.md §0.3 风险2 / §2.3 兼容段 ↔ BDD-4（P1 §3 BDD-4 验收方式"构造缺节 fixture 断言 exit 1"）。

### 建议改进（MAJOR，不阻断 P2 通过，P4 前落实）

**建议 2：明确七维边界，防 double count（BDD-6 扩容落实）**
- "交互状态覆盖率"审"各状态（loading/error/empty/edge）是否被 spec 覆盖"，"交互设计细节"审"具体交互实现细节质量（输入态反馈/过渡/禁用态）"——建议在 plan-design-review.md 维度表加一句边界注（如"交互状态覆盖率=状态存在性，交互设计细节=状态内实现质量"），避免评审时同一问题在两维重复打分。
- 锚点：P2-design.md §2.5 ↔ BDD-6（P1 §3 BDD-6"每维度有 0-10 可判定评分项"）。

**建议 3：方案 A 已隐含、建议文档明示——GAP 分支的退出码语义**
- §2.13 公式里"含复核记录 → 放行 exit 0/2"、"不含 → exit 1"；补充明确与既有"方差 WARNING→exit 2"的叠加顺序（同一截图集既重方差警告又雷同时，以哪个为准），避免 P6 实测时 gate 传播歧义。
- 锚点：P2-design.md §2.8 / §2.13 ↔ BDD-9/14。

**建议 4：minimal_validation 第 3 项的块定位描述修正**
- 将"块边界用 '## ' 章节分隔定位"改为"提取 ```yaml 代码围栏块内 YAML"（与 P1 capability_requirements 实际承载格式一致），该说明将指导 P4 实现 P1 视觉条目解析。
- 锚点：P2-design.md §5.2 第 3 项 ↔ BDD-3。

## 五、对照检查（评审约束核验）

- **不写死视觉工具**：机制全程用三态声明 + 运行时探测（available/supplementable/GAP），未绑定 vision-engine/任何具体工具名。✅ 符合约束 4
- **架构兼任 UI 设计**：§2.4 architect 产出 + role-system 不新增 designer，边界清晰。✅ 符合 BDD-5
- **GAP 降级链不死锁**：像素检测 + 人工复核记录有合法出口（人工复核记录 = 复核人/时间/结论）。✅ 符合 BDD-9
- **影响面不透支**：§6 逐文件核实同步动作，P2 rg 结果与 P1 的 45 文件一致。✅ 符合 BDD-8

## 六、返回给主 Agent

- **File**: agate-workspace/tasks/TAG0006-ui-ux-quality/P2-review-design.md
- **Status**: needs-revision
- 需回派 architect 修正：**问题 1（§0.3 触发条件矛盾，BLOCKER）**；落实建议 2/3/4（边界注 + GAP 退出码 + 块定位描述）。
- 本评审无 BLOCKER 级的设计方向异议，修正后即可 approved 推进 P3。

---

## 复审记录（2026-08-17，第二轮 review，plan-design-review）

> 复审对象：architect 已按上轮意见修改后的 P2-design.md（555 行，候选方案/架构/章节结构未变）。
> 复审范围：逐项核对 B1（BLOCKER）/ M1（建议2）/ M2（建议3）/ B4（建议4）四处的修复落实，并独立复核"已 approved 部分未被意外改动"与"兼容性声明成立"。

### 1. B1（上轮 BLOCKER：§0.3 vs §2.3 BDD-4 触发条件矛盾）— 已修复 ✅

- 修复后 §0.3 风险2（P2-design.md:53）表述改为：**"触发条件**仅为 P2 自身 `ui_affected: true`**（不读取 P1 capabilities，与 §2.3 一致）"**——并删除"需要 P1 vision 才触发"的旧表述，改为"经核实无 P2 gate 测试引用 fixtures/ui-affected 或 fixtures/vision-blocked（test_check_gate 自建 fixture），故这些 fixture 不会被 P2 检查命中，兼容成立；新增专门 fixture 覆盖 BDD-4"。
- 修复后 §2.3 兼容段（P2-design.md:163）明确"触发条件仅为 P2 自身 `ui_affected: true`，与 §0.3 风险 2 对齐"，并给出免责核验（test_check_gate 用自建 fixture、不引用静态夹具目录；ui-affected/vision-blocked 均为 P6 专用）。触发条件全稿统一为"P2 自身 ui_affected: true 单独触发，不读 P1 capabilities"，与 BDD-4 的 Given（P2-design.md 声明 ui_affected: true）一致。**矛盾消除。**
- **独立复核（本审）**：`grep` 全 tests 树确认无任何 `fixtures/ui-affected` / `fixtures/vision-blocked` 的 Python 引用；`test_check_gate.py` 全部 P2 用例经 `_write_p2_design` 自建 fixture（task_dir factory），不引用静态夹具目录；静态夹具 `ui-affected`/`vision-blocked` 的 P2-design.md 确为 `ui_affected: true` 且无 `## UI 设计` 节，但当前无 P2 gate 测试消费它们 → 兼容声明成立，新检查不会误伤。

### 2. M1（上轮建议2：七维边界注）— 已解决 ✅

- §2.5（P2-design.md:214）新增**七维边界注**（写入 plan-design-review.md 维度表）：「**"交互状态覆盖率"= 状态存在性**（审 loading/error/empty/edge 等状态是否被 spec 覆盖）」「**"交互设计细节"= 状态内实现质量**（审输入态反馈/过渡/禁用态等实现细节质量）」——前者回答"各状态有没有被覆盖"、后者回答"覆盖到的状态实现得够不够好"，并明确"同一问题不允许跨两维重复打分"。double count 风险已按建议消除，与 BDD-6 的"每维度有 0-10 可判定评分项"自洽。

### 3. M2（上轮建议3：GAP 分支退出码叠加顺序）— 已解决 ✅

- §2.13（P2-design.md:318）新增**退出码叠加顺序**完整声明：① 雷同且无复核记录 → exit 1（覆盖方差 WARNING，最终 exit 1）；② 雷同有复核记录 + 存在方差 WARNING → 以聚合公式中的 2 为准（exit 2，不放宽为 0）；③ 雷同有复核记录且全程无方差 WARNING → exit 0；④ 无雷同仅方差 WARNING → exit 2（现状不变）。并给出实现落地顺序（"先累加 variance_warning 计数 → 再判断雷同阻断/放行 → 最后统一汇总结论 exit 码"）。P6 实测时 gate 传播歧义已消除，BDD-9/14 判据完备。

### 4. B4（上轮建议4：minimal_validation 块定位描述）— 已解决 ✅

- §5.2 第 3 项（P2-design.md:402）已改为"**提取 ```yaml 代码围栏块内 YAML**（与 P1 capability_requirements 实际承载格式一致，见 P1 §7 代码围栏样例），**不用 '## ' 章节分隔定位**"；同时 §2.1（P2-design.md:123）gate 逻辑描述同步为"提取 P1-requirements.md `capability_requirements:` 代码围栏块（```yaml ... ```）内 YAML，`yaml.safe_load` 解析"。两处口径一致，P4 实现有明确指引，BDD-3 定位方式准确。

### 5. 已 approved 部分复核（未被意外改动）

- **方案 A 机制方向未被推翻**：§1.1 仍为候选方案 A（三态能力声明的"硬声明 + 降级链"双层机制），candidate_count=4（frontmatter 第 11 行）、B/C/D 三对照与选择理由、dispatch_plan: single（§8）均保持。
- **PDD 落点/结构未变**：§2.1-2.14 逐 BDD 三件套（落点 + gate + 单测）、§3 gate_commands、§4 Windows 评估（保持现状 + 不写实测）、§5 env_constraints/minimal_validation、§6 影响面核对清单（45 文件）、§7 files_to_read、§9 完成标志、§10 兼容策略四条、§11 断言——全部保留，上轮已 approved 的结论不因本次修正而改变。
- **兼容性关键声明复核通过**：§0.2/§2.3/§6.3/§10 四处关于"ui-affected/vision-blocked 静态夹具不用于 P2 gate 测试"的表述互相一致，且经本审独立 grep 核实为真（见第 1 节）。
- **825 vs 823 口径**：本稿一致采用 825（上轮实测收集值），并保留"P8 发布统一口径"的提示，无新增不一致引入。

### 6. 复审结论

- B1（BLOCKER）/ M1 / M2 / B4 四项**全部解决**，无新增 BLOCKER，无新增 MAJOR 建议；既有 pending 项清空。
- 上轮 all-BDD 核对结论（15 条 BDD 三件套完整、兼容策略成立、机制不推翻）在修复后全部维持。
- **最终判定：approved**（依据：P2-design.md §0.3/§2.3 触发条件统一 → BDD-4；§2.5 七维边界注 → BDD-6；§2.13 退出码叠加 → BDD-9/14；§5.2 第 3 项围栏提取 → BDD-3；§1.1/§8/§10 方案与兼容结构未动 → 方案 A 不推翻）。

---

## SCOPE+ 复审记录（2026-08-17，第三轮 review，plan-design-review）

> 复审对象：architect 按 2026-08-17 用户范围扩展（UI/UX 覆盖任意渲染形态）完成的 P2-design.md SCOPE+ 增补（741 行，新增 §2.15 形态声明载体与跨阶段一致、§2.16 P6 证据形式按形态选择，对 §2.3/§2.4/§2.5/§2.8/§2.9/§2.12/§2.13/§0/§5/§6/§7/§9-§11 标注 33 处 [BASELINE_CHANGE]，gate_commands §3 与 dispatch_plan §8 不变）。
> 复审范围：聚焦增补部分（形态声明载体设计、跨阶段一致 I14、判据可量化表、渲染组件 checklist、plan-design-review 渲染维度 0-10 可判定、不写死技术栈、gate 组合收口），并对原 approved 部分做一致性抽查。

### 1. 结论摘要
SCOPE+ 增补方向正确、机制架构成立：载体 A（P1 frontmatter 可选字段 + P2 UI 设计节声明）落地路径清晰，I14 跨阶段一致机制（P1→P2→P6→P7 四层）闭环成立，判据可量化表（§2.15.3）有效防住主观词，渲染组件 checklist（§2.4）要素完整，plan-design-review 渲染正确性与时序维度 0-10 可判定，技术栈中立（仅举例不绑定）。**但存在 2 处设计未闭合（P1-P2 形态词汇表未定义、时序截图 -tN 系列的雷同豁免未显式扩展），会在 P3/P4 阶段造成 implementer 歧义或 P6 误伤**，需回派 architect 修正。判定 **needs-revision**（非 rejected——增补本体不推翻，修 2 处 + 落实 3 条建议即可推进）。

### 2. 增补部分逐项评审

| # | 评审项 | 结论 | 说明（锚点） |
|---|--------|------|-------------|
| 1 | 形态声明载体设计（§2.15.1） | ✅ 合理可落地 | 载体 A（P1 frontmatter 可选字段 `ui_render_shape`/`ui_ux_dimensions` + P2 UI 设计节 `### 渲染形态声明` 行）+ B 对比；frontmatter 机器可读、presence 语义（缺失=布局型默认）保基线不红；agate-frontmatter-check P1 schema migrated_keys+types 增可选键不破坏旧 fixture（核验：migrated_keys 为判别集合、required 为硬校验集，新增可选键不动 required → 兼容成立）；agate-md-field-get 新 op 参照 ui_affected 模式（frontmatter 优先 + 正则回退）可行。 |
| 2 | 跨阶段一致 I14（§2.15.1 + §2.3:174） | ⚠️ 机制成立，匹配语义未定义 | P1 frontmatter→P2 gate 交叉校验（§2.3:174 关键词匹配）→P6 读 P1 frontmatter →P7 一致性规则（I14 三处一致）。四层闭环成立；但「关键词匹配，不要求逐字相等」未定义 P1 值与 P2 声明的对应词汇表（见 BLOCKER-1）。 |
| 3 | 维度选择合法性（§2.15.2） | ✅ | `_gate_p1_ui_shape`：ui_render_shape 缺失但维度存在→允许；shape 存在维度空→拦截；缺失双字段→通过；扩展维度须在 P1 UX BDD 标题出现。test_shape_1~5 全覆盖。 |
| 4 | 判据可量化表（§2.15.3） | ✅ 有效防主观词 | 渲染正确性/时序/动效/手势交互 4 档每档给量化判据锚点 + 明确禁用主观词（可读/美观/流畅/平滑/跟手…），与 BDD-2/16 的「Then 不主观」对齐；requirements-review 打回收口。 |
| 5 | 渲染组件 checklist（§2.4） | ✅ 较完整 | 渲染正确性（渲染管线/绘制配置、判定锚点、图层/加载、特效触发结束）+ 动效时序（帧采样、关键帧、结束判定）+ 手势（交互 checklist 可选）覆盖 BDD-16 四维；「维度不适用显式声明可豁免」与 §2.3 step4 分支自洽。 |
| 6 | plan-design-review 渲染维度 0-10（§2.5） | ✅ 可判定 | 渲染结果正确性 0-4/帧时序 0-3/动效质量 0-3=10，各子项量化锚点已给；启用规则（渲染组件/时序类形态才启用）避免常规布局型噪音；七维边界注防 double count。 |
| 7 | gate 组合收口（§2.15.4） | ✅ | P1 `_gate_p1_ui_shape` / P2 形态分支+交叉校验 / P6 证据形式按形态 / P7 consistency 新规则四档收口，触发条件与终点行为齐表；三件套（条文+gate+单测）完整。 |
| 8 | P6 证据形式按形态（§2.16） | ⚠️ 命名/豁免边界待闭合 | forms 表（常规布局型/帧序列/渲染输出对比/时序截图）+ 目录命名约定 + check-p6-evidence 5 点适配 + 平台无关（os.walk+正则，不依赖 Pillow）整体成立；但时序截图 -tN 与 frames/ 的雷同分组豁免衔接未显式闭合（见 BLOCKER-2）。 |
| 9 | 不写死技术栈（约束 4） | ✅ | 分类框架为示例性开放集合，WebGL/Canvas/OpenGL 仅举例；§2.3 step4 的「画布/图表/模型/特效/地图/数字地球」属启发式关键词并带命中替代分支，非绑定（观察 2 建议补一句明示）。 |
| 10 | 原 approved 部分一致性抽查 | ✅ 未被破坏 | §0/§1（方案 A、candidate_count=4）、§3 gate_commands、§4 Windows 保持现状、§8 dispatch_plan: single、§10 兼容策略、§9 完成标志、825 口径全部保留；33 处 [BASELINE_CHANGE] 与 P2 宣称一致（核验 grep 计数 = 33）；BDD-16/17 与 P1 SCOPE+ 扩展组逐条对齐。 |

### 3. 必须修正（BLOCKER，回派 architect 改 P2-design.md）

**BLOCKER-1：P1-P2 形态值词汇表与匹配语义未定义（I14，BDD-4①/BDD-16）**
- 现状矛盾：P2-design.md §2.15.1 载体 A 规定 P1 frontmatter 字段值示例为 **ASCII 值**（`layout` / `render_component` / `temporal_effects`，§2.15.1 表 + §5.2 minimal_validation 第 5 项），而 §2.3 gate step4 的形态分支关键词与 §2.4 UI 设计节模板声明用的是**中文标签**（实时序如「渲染组件/视觉渲染/布局（layout/布局）」、P2 声明行「渲染形态: <……示例：布局型/渲染组件型/时序特效型>」）。§2.3:174 跨阶段一致仅说「关键词匹配，不要求逐字相等」，**未定义 `ui_render_shape: render_component` 与 P2 声明「渲染组件型」之间的对应关系**（同义映射表？规范化别名？还是 P1 值也必须用中文词？）。
- 风险：P4 implementer 与 P3 单测（test_ui_design_7「P1 声明 ui_render_shape 与 P2 形态声明行不一致→exit 1」）对「什么算一致」产生歧义——若按字面匹配，ASCII token 与中文标签永不相等，合法任务被误拦；若按宽松关键词，语义形同虚设。跨阶段一致（I14）是本增量核心承诺，词汇表不闭合则「机械比对」落空。
- 建议修正（二选一）：① 定义规范形态值词汇表（如 `layout`/`render_component`/`temporal_effects` 为规范值，P2 声明行必须复用该规范值并附中文注释）；② 或规定 P1 字段值用中文标签（「布局型/渲染组件型/时序特效型」），gate 与 P2 模板统一中文口径。轻改：在 §2.15.1 增加「P1 值 ↔ P2 声明标签」同义映射表并各录一条单测固化匹配行为。
- 锚点：P2-design.md §2.15.1（383-397）/§2.3:174/§2.4:194-195 ↔ BDD-4①、BDD-16、I14（P1 §2 I14）。

**BLOCKER-2：时序截图 -tN 系列的雷同分组豁免未显式扩展（BDD-17/I15）**
- 现状：§2.16 时序特效型证据形式为「时序截图 `screenshots/{bdd-id}-t1.png/-t2.png`（时刻后缀）或帧序列」，放在 `screenshots/` 目录；而 §2.13/§2.16 的雷同分组豁免只写「按『同 BDD 帧序列组』分组——组内相邻帧豁免」（§2.13:360、§2.16:456,462），措辞均以 **frames/ 帧序列** 为对象。
- 风险：同一 bdd 的 `-t1/-t2/-t3` 时序截图像素内容必然高度近似（同一场景不同时刻），放在 screenshots/ 目录后会被现有「整目录 md5/ahash 去重」逻辑扫到 → 触发雷同降级待复核（要求人工复核记录），合法时序证据被误判为「疑似充数」。若「同 BDD 组」分组不覆盖 `-tN` 系列（其不在 frames/ 目录），时序特效型任务每纠一条时序 BDD 都要额外走人工复核——BDD-17 的核心场景（动效/时序按形态选证据）被自己新加的 gate 误伤。
- 建议修正：在 §2.16 显式声明「**同 BDD 的 `-tN` 时序截图系列与 frames/ 帧序列同权获取分组豁免**」（分组键 = bdd-id 前缀，`{bdd-id}-t1..tN` 与 `{bdd-id}-NN` 统一按同 bdd 组豁免相邻样本），并补单测（同 bdd 的 t1/t2 视觉相近 → 不触发雷同降级 exit 0）。
- 锚点：P2-design.md §2.16:445-462 + §2.13:360 ↔ BDD-17、BDD-14、I15（P1 §2 I15）。

### 4. 建议改进（MAJOR，不阻断 P2 修正轮通过，P3/P4 前落实）

**建议 1：渲染正确性 checklist 补「颜色/光照/材质 归入参考对比锚点」明示**（BDD-16）
- §2.4 渲染正确性 checklist 有「判定锚点：渲染结果对比（参考图/diff 阈值）或输出数据断言」，但对渲染组件的颜色/光照/材质保真未单列——建议补一句「颜色/光照/材质等视觉保真项以渲染结果对比参考图覆盖」，避免 implementer 误以为渲染组件无需视觉保真项。

**建议 2：§2.3 step4 关键词列表补「启发非绑定」注**（约束 4 加固）
- 「画布/图表/模型/特效/地图/数字地球 …」为产品域启发词而非技术栈绑定，建议明示「这些词仅作识别提示，不构成技术栈要求；形态判定以 ui_render_shape/维度选择为准」。

**建议 3：BLOCKER-1 修正后补词汇表匹配单测**（BDD-4① 加固）
- 除 test_ui_design_7（不一致 exit 1）外，补一条「P1 值与 P2 声明为规范值 → 一致 → exit 2」的正例，固化词汇表映射行为，防实现漂移。

### 5. 复审结论
- 前三轮已 approved 的结论（方案 A 机制、15 条 BDD 三件套、兼容策略、825 口径）在 SCOPE+ 增补后全部维持，增补未破坏原语义（抽查 §0/§1/§3/§4/§8/§10 均保留）。
- 增补核心（载体 A + I14 机制 + 判据可量化表 + 渲染 checklist + 渲染维度可判定）方向正确、整体可实施。
- BLOCKER-1（P1-P2 词汇表未定义，I14 匹配语义落空）与 BLOCKER-2（-tN 时序截图雷同豁免未显式扩展）需回派 architect 修正后推进 P3；建议 1/2/3 随修正同步落实。
- **最终判定：needs-revision**（依据：P2-design.md §2.15.1/§2.3:174 ↔ BDD-4①/BDD-16/I14；§2.16:445-462 + §2.13:360 ↔ BDD-17/BDD-14/I15；§2.4 → BDD-16；§2.15.3 → BDD-2；§2.5 → BDD-6；方案主体 §1.1/§3/§8/§10 未动 → 非 rejected）。

---

## 修复复审记录（2026-08-17，第四轮 review，plan-design-review）

> 复审对象：architect 按第三轮 SCOPE+ 评审意见（BLOCKER-1/BLOCKER-2 + 建议 1/2/3）完成修复后的 P2-design.md（759 行，§0-§16 章节结构未变，candidate_count=4 / dispatch_plan: single / gate_commands / 825 口径全部保持）。
> 复审范围：逐项核对 B1（BLOCKER-1 词汇表）／B2（BLOCKER-2 -tN 分组豁免）／M1（建议1）／M2（建议2）／M3（建议3）五处修复的彻底性，并独立复核"已 approved 部分未被意外改动"。

### 1. B1（BLOCKER-1：P1-P2 形态值词汇表与匹配语义未定义）— 已彻底解决 ✅

- **规范形态值词汇表已定义**（§2.15.1:391-404）：新旧值表（layout/render_component/temporal_effects × 布局型/渲染组件型/时序特效型 × 形态描述）齐全；同义映射表（§2.15.1:399）显式列出 `layout↔布局型`、`render_component↔渲染组件型`、`temporal_effects↔时序特效型` 三对映射，**ASCII↔中文双向闭合，无缺对**。
- **取值规则闭合（§2.15.1:401-402）**：P1 frontmatter 字段值**必须用规范值**；P2 声明行**复用规范值并附中文注释**；gate 侧对"仅含中文标签"的声明行经同义映射表归一化。
- **匹配语义已统一为规范化值比对（§2.3:174 + §2.15.1:403）**：P2 声明行解析规范 token（含规范值直接取用 / 仅中文标签经映射归一化）→ 与 P1 `ui_render_shape` 字段值比对，**相同规范值即一致**；并显式写明"杜绝 ASCII 规范值与中文标签字面永不匹配的误拦"。与第三轮唯一残留的旧表述（"关键词匹配，不要求逐字相等"）已全稿清除（grep 无残留）。
- **单测固化（§2.3:185-186）**：`test_ui_design_8`（规范值一致 exit 2）+ `test_ui_design_9`（中文标签经映射归一化 exit 2）——正反两向匹配行为均被机器固化，P3/P4 实现不可能产生歧义。
- **本审独立验证**：grep P2-design.md 确认 §2.3:174 与 §2.15.1:399/403 三处口径逐字一致，无"逐字相等"旧表述残留；词汇表三对映射与 §2.3:174 归一化路径引用一致。I14 跨阶段一致的核心承诺（机械比对）就此落地。

### 2. B2（BLOCKER-2：时序截图 -tN 系列雷同分组豁免未显式扩展）— 已彻底解决 ✅

- **分组豁免已双层显式化**：
  - §2.13:363（判定域分组豁免）：**分组键 = bdd-id 前缀**——同一 BDD 的帧序列 `{bdd-id}-NN` 与 时序截图 `{bdd-id}-t1..tN` **统一归入同一组、同权豁免**；组内相邻帧/相邻时刻豁免降级，组间/跨 BDD 雷同仍触发降级待复核。实现时"ahash 按 BDD 分组后再统计 dupes"。
  - §2.16:473-474（目录/命名 + md5/avg-hash 适用域）：时序截图 `-tN` 系列与 `frames/` 帧序列**同权豁免**——`screenshots/{bdd-id}-t1/-t2` 与 `frames/{bdd-id}-01/-02` 统一按「同 BDD 证据组（bdd-id 前缀）」分组，组内相邻样本不触发雷同降级；跨 BDD md5 逐字节重复仍硬阻断（充数防伪）、avg-hash 跨组重复仍降级待复核。
  - §2.16:480（check-p6-evidence 适配第 4 条）：雷同判定按同 BDD 证据组分组（`-tN` 与帧序列统一归组）。
- **防误伤与防作恶双向闭合**：豁免范围严格限定"同 bdd-id 前缀的组内相邻样本"，跨组（含同 BDD 不同形态、跨 BDD）雷同仍按 §2.13 降级判定——时序特效型合法证据不误伤，充数作恶不被放行。**组内相邻样本豁免 + 组间判定**的边界清晰，防误伤设计成立。
- **单测固化（§2.16:485）**：`test_time_seq_1_adjacent_time_shots_no_ahash_trigger_exit_0`（同 bdd 时序截图 t1/t2 视觉相近 → 按同 bdd 组豁免 → exit 0）+ 既有 test_frame_seq_1（帧序列相邻帧同豁免）。BDD-17/I15 核心场景（时序证据按形态选用不被新 gate 误伤）已有机器固化。

### 3. M1（建议1：渲染正确性 checklist 补颜色/光照/材质）— 已解决 ✅

§2.4:219 在渲染正确性 checklist 新增明示条目：**"颜色/光照/材质等视觉保真项归入参考对比锚点"**——以渲染结果对比参考图覆盖（diff 阈值量化），不得仅以"绘制成功/渲染出图"断言保真。implementer 不会再误以为渲染组件无需视觉保真项，BDD-16 视觉保真维度闭环。

### 4. M2（建议2：§2.3 step4 关键词列表补"启发非绑定"注）— 已解决 ✅

§2.3:171 渲染组件型分支末尾新增 ⚠️ **启发非绑定注**：画布/图表/模型/特效/地图/数字地球等为**产品域启发词**（仅用于识别可能的渲染组件形态、触发本分支），**不构成技术栈要求**——形态判定以 P1 `ui_render_shape` 规范值 / §2.15.2 维度选择为准。与约束 4（不写死技术栈）对齐，启发词与规范值判定优先级明确。

### 5. M3（建议3：词汇表匹配正例单测）— 已解决 ✅

test_ui_design_8/9 已补入 §2.3 单测清单（见第 1 节），并在 §9:742 完成标志中同步登记（"test_ui_design_5~9（BDD-4 形态分支 + P1-P2 规范值/同义映射一致）"）——词汇表匹配行为既有设计条文又有机器固化，防实现漂移。

### 6. 已 approved 部分复核（未被意外改动）

- **方案主体未动**：frontmatter（candidate_count=4 / packages / domains / ui_affected）逐字段一致；§1.1 方案 A、§3 gate_commands、§4 Windows 保持现状、§8 dispatch_plan: {mode: single}、§9 完成标志、§10 兼容策略、§11 断言——全部保留。
- **825 口径一致**：全稿 825 无回退，minimal_validation 与 §2.14/§10 引用一致。
- **SCOPE+ 增补结构未破坏**：§2.15.1-2.15.4 与 §2.16 章节完整，修复仅新增词汇表/分组豁免内容，未改写既有增补条文；[BASELINE_CHANGE] 标记总数由第三轮 33 处增至 37 处（净增 4 处 = 修复轮新增标记），方向与修复范围一致。
- **兼容声明成立**：presence 语义（字段缺失 = 布局型默认）、既有 fixture 不触发新检查、跨组雷同仍降级——三点均未因修复而松动。

### 7. 修复复审结论

- B1（词汇表闭合 + 规范化值比对）／B2（-tN 与帧序列同权分组豁免）／M1／M2／M3 五项**全部彻底解决**，无新增 BLOCKER，无新增 MAJOR 建议；第三轮 pending 项清空。
- **唯一残留备注（非阻断，P4 既可）**：§6.3 与 §7 影响面/文件清单两处仍写"test_ui_design_5~7"（§6.3:653、§7:716），而 §2.3/§9 已扩至 test_ui_design_5~9——属清单描述滞后，完善 P4 落地时把这两处同步为 5~9 即可，不影响 gate 逻辑与实现歧义（权威枚举在 §2.3 与 §9）。
- 第三、四轮 all-BDD 核对结论（涵盖原 15 条 + SCOPE+ BDD-16/17 及扩展）在修复后全部维持；机制本体自第二轮以来持续未推翻。
- **最终判定：approved**（依据：P2-design.md §2.15.1:391-404 + §2.3:174+185-186 ↔ BDD-4①/BDD-16/I14；§2.13:363 + §2.16:473-480+485 ↔ BDD-17/BDD-14/I15；§2.4:219 → BDD-16；§2.3:171 → 约束 4；方案主体 §1.1/§3/§8/§10 + 825 口径未动 → 非 rejected）。修复轮 BLOCKER 清零，可推进 P3。