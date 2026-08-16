---
phase: P1
task_id: TAG0014-dispatch-orchestration
type: review
parent: P1-requirements.md
trace_id: TAG0014-P1-20260816
status: approved
created: 2026-08-16
agent: requirements-review
---

# P1 需求基线复评 — TAG0014-dispatch-orchestration（复评轮）

> 评审对象：修订后 `P1-requirements.md`（22 条 BDD，[NO_NEED_CONFIRM]）。
> 参照：P0-brief.md、approved plan（agate-dispatch-orchestration-20260815.md）、上轮 P1-review.md（needs-revision，F1-F5）、P1-dispatch-context-analyst.md（修复轮指引）、WORKFLOW.md、requirements-review.md 角色清单。
> 只审不写：未修改 P1-requirements.md。环境声明：`[PROD_NOT_TOUCHED]`。

## 评审结论

**status: approved**

上轮 BLOCKER F1 与 F2-F5 全部解决：F1 → 新增 BDD-22（§4.6）+ I1 交叉引用「验收落点：BDD-22（§4.6）」；F2 → BDD-6 Given 补全每批 complexity 且显式声明避开 BDD-5 路径；F3 → BDD-15 Given 显式 `agate/phase-cards/P1-requirements.md` 并同名消歧；F4 → BDD-5 保留合并但注明 P6 须分别构造两子场景各验一次；F5 → BDD-20 改为动态实测基线表述。修订未引入回归：BDD 1-22 连续无跳号、全部可二值、无 [NEED_CONFIRM]、frontmatter 未动、P1 纯净性保持。

## F1-F5 复核（逐项）

- **[F1 / BLOCKER] 已解决**：§4.6 新增 BDD-22（L249-252，Given 完成协议/脚本改动并提交 → When git log 检查 commit message 与派发记录 → Then 均含 `self-gate-review:` 路径且存在 protocol-alignment-review 派发记录），与 plan 验收标准 6 口径一致（走推荐方案 a）。I1（L70）已补交叉引用「验收落点：BDD-22（§4.6）」。Then 子句可 grep（`git log` + 派发记录存在性）二值判定。
- **[F2] 已解决**：BDD-6 Given 改为 4 批全字段（每批 `{id, complexity: low}` ×4）并附注「各批字段完整，不会先命中 BDD-5 缺字段错误路径」，批数超限校验路径独立可达，结构与 plan `test_dispatch_plan_batch_granularity` 一致。
- **[F3] 已解决**：BDD-15 Given 显式 `agate/phase-cards/P1-requirements.md`（即阶段卡片目录下的 P1-requirements.md，非任务自身同名需求基线文件），同名歧义消除。
- **[F4] 已解决**：BDD-5 保留合并，但新增注（L157）明确两子场景——① batch 缺 complexity（对应 plan 负向用例 `test_dispatch_plan_batch_missing_complexity`）② complexity 非法值（对应 plan 正向粒度用例枚举校验）——且强制「P6 验收须分别构造两子场景的 Given 各验一次，两子场景均须 PASS」。满足「保留合并但注明 P6 覆盖两子场景」分支。
- **[F5] 已解决**：BDD-20 Then 改为「用例总数 ≥ 改造前实测基线 + 8 条新增（基线 = P4 实现前 `bash agate/tests/scripts/count-tests.sh` 的实际输出值；不硬编码 plan 估算值 751+ 或 tests/README.md 的 TAG0011 基线 749）」，动态实测口径消除常数漂移风险。

## BDD 评审（逐条，复评）

> 覆盖维度标注：数据/前端/多端/边界/兼容。domains=[docs,scripts,tests] 无前端域，前端统一 N/A；"多端"指 op↔gate 子进程契约、文档双源同步。

- **BDD-1**: PASS（可二值）。数据✓ 多端✓。JSON 合法 + mode 五值枚举成员判定客观。
- **BDD-2**: PASS（可二值）。兼容✓。缺字段逐行一致 + 同 exit code，P6 对照改造前快照。
- **BDD-3**: PASS（可二值）。边界✓。stderr「GATE P2 ERROR」+ exit 1 可 grep/exit code 判定。
- **BDD-4**: PASS（可二值）。边界✓。parallel_limit<1 拦截同 BDD-3。
- **BDD-5**: PASS（可二值）。数据✓ 边界✓。缺字段/非法值两子场景合并但已注明 P6 分场景验（F4 解决）。**注：子场景若分别验，各自 Given 均已明确（缺 complexity vs complexity 非法值），可二值。**
- **BDD-6**: PASS（可二值）。边界✓。4 批全字段 > 上限 3，路径独立（F2 解决）。
- **BDD-7**: PASS（可二值）。边界✓ 兼容✓。解析失败按缺字段处理不误拦。
- **BDD-8**: PASS（可二值）。数据✓。五维评级 + low/medium/high 输出可 grep。
- **BDD-9**: PASS（可二值）。数据✓。5 模式 + 每模式"何时用/流程"两部分可 grep。
- **BDD-10**: PASS（可二值）。多端✓ 兼容✓。三步流程 + 文档样例可 grep。
- **BDD-11**: PASS（可二值）。边界✓ 兼容✓。三要素（上限 3 / retry 对齐 retries[Pn] / 共享文件 P6 例外）落到 I6/I7。
- **BDD-12**: PASS（可二值）。数据✓。P1-P8 每阶段 + P2/P7/P8 特例可 grep。
- **BDD-13**: PASS（可二值）。数据✓ 多端✓。逐卡片引用 + 阶段特定约束关键词清单。
- **BDD-14**: PASS（可二值）。兼容✓。新表述 + 原有理由保留双断言。
- **BDD-15**: PASS（可二值）。多端✓。显式 `agate/phase-cards/P1-requirements.md` 消歧（F3 解决）。
- **BDD-16**: PASS（可二值）。多端✓。拆批 + 合并机制（P8-release-{pkg}.md → 合并 subagent 整合唯一文件）。
- **BDD-17**: PASS（可二值）。数据✓。强制节三要素 + high 必须拆分。
- **BDD-18**: PASS（可二值）。多端✓ 兼容✓。双处同步 + 权威源声明，落到 I5。
- **BDD-19**: PASS（可二值）。边界✓ 兼容✓。8 条 = 5 正向 + 3 负向，与 plan Task 1/2 一致。
- **BDD-20**: PASS（可二值）。兼容✓。动态实测基线 + 8 条新增，pytest exit code 判定（F5 解决）。
- **BDD-21**: PASS（可二值）。兼容✓。0 ERROR + CHECK 3 行号引用不误报，落到 I8。
- **BDD-22**: PASS（可二值）。兼容✓。`git log` grep `self-gate-review:` + 派发记录存在性（F1 解决，新增）。落到 I1 / plan 验收标准 6。

## 隐含需求覆盖

- **数据维度**：BDD-1/5/8/12（字段契约序列化、complexity 枚举、五维评级表）。✓
- **前端维度**：N/A（domains 无前端，§7 已说明无外部域）。✓
- **多端维度**：BDD-1（op↔gate JSON 契约）、BDD-10/15/16/18（双源同步、合并机制）。✓
- **边界维度**：BDD-3/4/5/6/7（非法 mode、parallel_limit<1、batch 缺字段、批数超限、malformed YAML）、I6（retry 对齐）、I7（P6 例外）。✓
- **兼容维度**：BDD-2/7（缺字段向后兼容）、BDD-20/21（全量回归 + consistency）、I1/BDD-22（self-gate）、I2（不入 frontmatter-check schema）、I4（JSON 序列化）、I5（双源同步）、I8（CHECK 3）、I9（保留既有粒度规则）。✓

**对照 dispatch-context 覆盖清单**（工作量评估/五模式/并行规则/模式 4/全阶段适用表/dispatch_plan 契约/self-gate/consistency）：
- 工作量评估→BDD-8✓；五模式→BDD-9✓；并行规则→BDD-11✓；模式 4→BDD-10✓；全阶段适用表→BDD-12✓；dispatch_plan 契约→BDD-1~7+19✓；consistency 回归→BDD-21✓；**self-gate 触发→BDD-22✓（F1 修复后补全）**。

I1-I10 全部在 §2 声明；I2/I3/I4 契约细节与 plan（B3/N9）逐字一致，需求层未重新发明。无 [NEED_CONFIRM] 残留；S1-S3 均为非阻塞 SUGGEST。

## BDD 跨条一致性

- 返回码分组互斥且内部一致：BDD-2/7（缺字段/解析失败→等同现状）vs BDD-3/4/5/6（非法值→ERROR exit 1）。
- BDD-19 负向三例与 BDD-4/5/7 一一对应，无冲突。
- BDD-5 与 BDD-6 路径已隔离（F2 修复后互不干扰）。
- BDD-12（P7=单发+豁免）与 BDD-14（P7 卡片表述）一致；BDD-10 合并步与 BDD-15 侦察产出互补不矛盾。
- BDD-22 与 I1 及 plan 验收标准 6 口径一致，无新增矛盾。

## 裁剪评审

- 无裁剪（phases 全 P0-P8），理由引用 P0-brief known_risks「有 approved plan ≠ 裁剪阶段」+ SELF-GATE 需 P7/P8。✓
- risk_level: high 与改动面匹配（协议 4 类 + 2 脚本 + 3 测试 + README/CHANGELOG/UPGRADING），触发 P2 plan-eng-review / P4 评审 / P7 双向一致性，合理。✓
- capability_requirements 四能力全部 available、无 GAP/supplementable，判定正确。✓
- 阶段职责 ↔ plan 6 Task 映射完整（§6）。✓

## P1 纯净性

- 22 条 BDD 均为行为/产出断言，无"如何实现校验器"的方案设计；"哪些卡片改"属影响面（§3 扫描表）。✓
- BDD-5 注中引用 plan 测试用例名（`test_dispatch_plan_batch_missing_complexity` 等）仅为 P6 场景构造的锚点引用，非实现方案。✓
- dispatch_plan 契约细节（flow YAML / op 读取 / KNOWN_OPS 注册 / JSON 输出 / 不入 schema）属已定死契约引用，非 P1 新发明。✓
- 无 NEED_CONFIRM 残留：§5 [NO_NEED_CONFIRM]；S1-S3 非阻塞 SUGGEST。✓

## 回归复核（修订引入检查）

- **BDD 编号**：`#### BDD-1:` ~ `#### BDD-22:` 连续无跳号（grep 确认 22 条）。✓
- **二值判定**：全部 22 条 Then 可 grep / exit code / 文件存在性判定，无中间态。✓
- **[NEED_CONFIRM]**：全文仅 L256 [NO_NEED_CONFIRM]。✓
- **frontmatter**：phase/task_id/type/parent/trace_id/status/created/agent + risk_level: high / phases 全 P0-P8 / packages 3 / domains 3 / capability_requirements 4 条，完整未动。✓
- **影响面表**：§3 扫描表（3.1/3.2/3.3）未因修订残缺。✓

## 结论

上轮 5 项发现全部解决，修订无回归。22 条 BDD 全部可二值、契约对齐 plan、覆盖清单 8 项全命中（含 self-gate）、无 NEED_CONFIRM、P1 纯净。判定 **approved**。可进入 P2。
