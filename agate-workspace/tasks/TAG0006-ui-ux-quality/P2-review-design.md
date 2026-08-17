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