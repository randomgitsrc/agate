---
phase: P1
task_id: TAG0001-tech-debt-closure
type: review
parent: P1-requirements.md
trace_id: TAG0001-P1-20260812
status: approved
created: 2026-08-12
agent: requirements-review
---

# TAG0001 P1 需求基线评审（requirements-review，独立视角）

评审对象：`P1-requirements.md`（20 条 BDD，risk_level=medium，全 8 阶段无裁剪，packages=[agate]，domains=[backend,cli]）。
评审依据：P0-brief.md（known_risks 9 项）、review-20260812-1204.md（Phase 1-3 设计）、角色定义 requirements-review.md，以及对本 worktree 现状的客观查证（见下）。

## 客观查证摘要（评审对象的事实陈述均已在 worktree 核实）

- WORKFLOW.md L79「固定 8 个子目录」、L85 `agents/ # agent 知识（project.md / memory / tech-debt）` — 属实（§1.3 表第 1 行的改动面描述准确）
- mkdir 8 子目录三处：SETUP.md:114 / orchestrator-template.md:102 / state-machine.md:40 — 属实，命令内容一致（无一处已含 debt/）
- TAG0003 BDD-1 验收口径（L84-87：`roadmap/、tasks/、agents/、archived/、reviews/、decisions/、plans/、logs/ 全部子目录`）— 属实，本次需随 8→9 重验（BDD-4 引用成立）
- change_type: refactor 已由 TAG0002 实现 — 属实（`agate/scripts/agate-frontmatter-check.py:37-40` enums 含 `"change_type": ("refactor",)`；TAG0002 P1 BDD-5 等覆盖 P6 分流）；TAG0001 无需重做，需求已声明「不重复做、不回退」
- plan-eng-review.md:19「技术债有没有记录和计划」— 属实，无 DEBT 条目格式要求
- retreat 提交格式 `retreat: {old_p} -> {new_p}（诊断：...）` 由 agate-retreat-to.sh:63 强制 — 属实；全仓库 2 条 retreat（023b28b / 29301ad）已用 `git cat-file -e` + `git log` 核实存在且格式一致
- T001 复盘 T1-T4（docs/reviews/T001-retrospective-2026-08-10.md L119-122，技术原因表）— 属实，各含问题/根因/影响，可作回填 source
- check-gate.sh P8 分支（L413-470：bump_type / version / CHANGELOG / tag 检查）— 属实
- UPGRADING.md v0.41.0 迁移节 — 存在（L92-127）。注：该节未含 mkdir 8 子目录命令本身（见「非阻塞观察」N4）

## BDD 评审

逐条判定（每条均含覆盖维度标注）：

- BDD-1（WORKFLOW 目录规范 tech-debt 归 debt/）：可二值判定，PASS 口径清晰（目录图含 debt/ + agents/ 注释去 tech-debt）。覆盖维度：数据✓ 前端✗ 多端✓ 边界✗ 兼容✗
- BDD-2（初始化 mkdir 9 子目录）：可二值判定；Then 含两子句（9 子目录出现 + 三处 mkdir 同步）但属同一验收场景，可接受。覆盖维度：数据✗ 前端✗ 多端✓ 边界✓ 兼容✓（新项目首次接入）
- BDD-3（SETUP/UPGRADING 路径一致）：可二值判定（grep 过期 `agents/tech-debt` 表述即可）。覆盖维度：数据✗ 前端✗ 多端✓ 边界✗ 兼容✓（旧文档路径迁移）
- BDD-4（TAG0003 验收口径重验）：可二值判定（对照 TAG0003 BDD-1 口径与回归结果）。覆盖维度：数据✗ 前端✗ 多端✗ 边界✗ 兼容✓（不破坏已验收功能）
- BDD-5（合法条目通过 schema 校验）：可二值判定，Given 覆盖 closed 态特殊要求。覆盖维度：数据✓ 前端✗ 多端✗ 边界✗ 兼容✗
- BDD-6（evidence 缺失拦截）：可二值判定。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-7（非法枚举拦截）：可二值判定（category/status/priority 三枚举各举非法值）。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-8（closed 缺 task_id 或证据引用拦截）：可二值判定。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-9（三态状态机 + task_id→in_progress）：可二值判定（schema 三值枚举 + task_id 语义）。覆盖维度：数据✓ 前端✗ 多端✗ 边界✗ 兼容✗
- BDD-10（无 tech-debt.md no-op 不报错）：可二值判定，兼容性核心 BDD。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✓（存量项目行为不变）
- BDD-11（T001 T1-T4 无损回填）：可二值判定（回填成功 + schema 通过 + 根因/影响无丢失 + evidence 引用出处），内嵌止损条件 1 判据。覆盖维度：数据✓ 前端✗ 多端✗ 边界✗ 兼容✗
- BDD-12（协议文档明确「回退落地必须建 DEBT」）：可二值判定（文档 grep）。覆盖维度：数据✗ 前端✗ 多端✓ 边界✗ 兼容✗
- BDD-13（retreat 无对应条目报 WARNING）：可二值判定；WARNING 不阻断已写死。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-14（已建对应条目不报）：可二值判定（与 BDD-13 成对，正反两向闭合）。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-15（真实 retreat fixture 可复现）：可二值判定（023b28b/29301ad 已核实存在）；为 P3 fixture 提供依据。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-16（P8 确认债务清单并留痕，含「无关注项」合法选项）：可二值判定。覆盖维度：数据✓ 前端✗ 多端✓ 边界✓ 兼容✗
- BDD-17（P8 只查留痕不阻断）：可二值判定，防 Goodhart 核心 BDD（未关闭债务不阻断 + 空确认合法）。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✓
- BDD-18（空确认可观测）：可二值判定（通过 P8-release.md 留痕判定连续 N 次空确认）；明示无新增计数脚本也可。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-19（判据文档化含「不登记」合法出口）：可二值判定（三分法 + 出口显式写出）。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓ 兼容✗
- BDD-20（登记 DEBT 不得豁免当前任务）：可二值判定（P7 人工核对验收声明表述），与 §1.2 决策 5、设计 §5.3 硬规则一致。覆盖维度：数据✗ 前端✗ 多端✗ 边界✗ 兼容✓

编号检查：`#### BDD-01:`~`BDD-20` 共 20 条，连续无跳号，格式标准；每条均单 Given-When-Then，无多场景未拆（BDD-2 Then 两子句属同一场景）。全部可二值判定，无「调整/部分通过」中间态。

## 隐含需求覆盖（五维度）

- 数据维度：覆盖。BDD-5~9（schema 字段/枚举/closed 准入）、BDD-11（回填无损）、BDD-13/14（retreat 比对数据源）、BDD-16/18（P8 留痕数据形态）。§2.7 明确复用 category 三分法不另起枚举，§2.4 给出「不登记」出口。
- 前端维度：不适用（无 UI 面，domains 无 frontend，评审对象为非 UI 协议改造）。已在 §2.4 说明依赖 P7 人工核对，无前端遗漏。
- 多端维度：覆盖。BDD-1/2/3/12/16 覆盖 WORKFLOW 目录图、三处 mkdir、SETUP/UPGRADING、回退规则文档、P8 卡片等消费方；§2.2 明确归类修正同步面四项清单，§2.8 明确机制可发现性（review 角色卡 / P8 卡片 / 回退规则文档三处可见）。
- 边界维度：覆盖。BDD-2（新项目首次接入）、BDD-6/7/8（缺失/非法值）、BDD-10（空文件 no-op）、BDD-13/15（稀疏信号与 fixture 复现）、BDD-17/18（空确认合法、不阻断）。§2.6 诚实标注召回极低（样本 1 起），未粉饰。
- 兼容维度：覆盖。BDD-4（TAG0003 已验收行为不回归）、BDD-10（无 tech-debt.md 存量项目零拦截）、BDD-17（P8 不因未关闭债务阻断）。§2.1 是全文最重要兼容约束（登记机制 vs 强制存量迁移的本质区别），§1.2 决策 9 明确 dev/workspace 增量不改已验收功能。

## 本任务特有评审重点（dispatch-context 5 项逐项核对）

1. **debt/ 目录归类修正**：BDD-1（agents/ 只留 project.md/memory + 目录图含 debt/）、BDD-2（mkdir 9 子目录三处同步）、BDD-3（SETUP/UPGRADING 路径一致）、BDD-4（TAG0003 BDD-1 口径 8→9 重验）全部覆盖；§1.2 决策 1 明确设计依据（tech-debt 是流程产出的项目状态记录——有状态机/schema/被脚本读写——vs agents/ 是 agent 输入知识），已在需求中体现。
2. **Phase 1 schema 校验**：BDD-5~9 覆盖必填字段/枚举/evidence 非空/closed 准入（task_id+证据引用）；BDD-11 用 T001 T1-T4 回填作试金石，且把「回填失败=模板设计错」作为可观测判据写进 Then——T001 复盘 T1-T4 回填验证覆盖完整。
3. **Phase 2 回退强制**：BDD-12（文档强制 `source: retreat`）、BDD-13（git log 提取 retreat 与 tech-debt.md 比对，缺失 WARNING，明确不阻断）、BDD-14（已建不报）、BDD-15（真实 fixture 复现）覆盖「回退落地 → 必须建 DEBT 条目」闭环。
4. **Phase 3 P8 锚定**：BDD-16（确认债务清单 + 结果写入 P8-release.md）、BDD-17（只查留痕不查内容达标、不阻断发布）、BDD-18（空确认次数可观测）覆盖「空确认/无关注项是合法选项」——防 Goodhart 边界写死。
5. **TAG0002 change_type 衔接**：§1.2 决策 8 + 客观查证确认 change_type 已由 TAG0002 实现；需求明确「不重复做、不回退、基于最新协议构建」，无重复 BDD、无对既有 change_type schema 的覆盖。

## 裁剪评审

全流程 P1-P8 无裁剪。逐阶段理由评审：

- 不跳过 P2：归类修正同步面清单、schema 字段集合、三态→task_id 映射、回退比对口径、P8 留痕落点均为真实设计决策——理由充分。
- 不跳过 P3：risk_level=medium，新增 `agate-debt-check.py`/`check-debt.sh`/回退比对/留痕检查是真实脚本逻辑，需先红后绿——理由充分（符合 AGENTS.md 工作流）。
- 不跳过 P4/P5/P6/P7/P8：交付底线 + T001 回填/向后兼容验收 + 跨文件一致性 + 版本发布——理由充分。

risk_level=medium 与实际风险匹配：触及 gate 脚本 P8 分支 + 新增 schema 校验器 + 协议文档横切 + 工作区初始化目录变更；但无 tech-debt.md 时全链路 no-op（BDD-10），非破坏性变更，不置 high——判定正确。

capability_requirements 三态全部 available，逐项有环境佐证（bash/python3+pyyaml/bats/shellcheck/git 均已核实），无 GAP、无 supplementable 存疑——判定正确。

## P1 纯净性

- 20 条 BDD 全部描述「用户/系统可观察行为」而非「调用哪个 API」，无实现细节混入。
- §1.3 改动面表格与 §2 隐含需求为「做什么 + 做完什么样算对」的问题定义，未给候选方案。
- 4 条 SUGGEST 属实现倾向建议（wrapper 模式复用、静态 mkdir 清单、WARNING 不挂 gate），已按 P1 规范标记 SUGGEST 待确认，未冒充已决策——边界处理得当，不构成 P1 污染。
- 结论：P1 纯净性通过。

## 非阻塞观察（供 P2/P4 参考，不影响通过判定）

- N1（BDD-4 落地口径）：BDD-4 的「重跑既有断言/测试」需明确落点——本 worktree 无直接断言「8 子目录」的测试（已 grep agate/tests/ 及脚本层），主要落点是更新 TAG0003 已归档 P1 的 BDD-1 验收口径 + 全量回归无红；P2 设计时应写清「重验」的具体动作，避免 BDD-4 验收时争议。
- N2（BDD-7 枚举覆盖广度）：BDD-7 显式覆盖 category/status/priority 三枚举，但 schema 尚有 `source`（retreat|review|retrospective）枚举未在 BDD-7 点名（BDD-5 的「枚举值合法」兜底覆盖）。P2 可确认校验器对 source 一并做枚举校验，或为 BDD-7 补一行注释。
- N3（BDD-18 可观测性依赖格式）：BDD-18 的判定依赖 P8-release.md 留痕格式足以区分「空确认」与「有关注项」——P2 设计 P8-release.md 确认节字段时需保证该可区分性（建议显式字段如 `debt_check:`，而非自由文本）。
- N4（§1.3 表第 9 行表述）：「UPGRADING.md v0.41.0 迁移节（8 子目录）」与实际略有出入——该迁移节并未内嵌 mkdir 8 子目录命令（命令仅存在于 SETUP.md/orchestrator-template.md/state-machine.md 三处）。不影响 BDD-3 语义（UPGRADING 同步 tech-debt 路径表述仍必要），P4 按实际内容同步即可。

## 结论

20 条 BDD 全部可二值判定、编号连续、单 GWT；数据/多端/边界/兼容四维度全覆盖（前端不适用）；跨条一致性无矛盾；裁剪与 risk_level=medium 判定合理；P1 纯净性通过；5 项本任务特有评审重点全部有对应 BDD/章节锚定。4 条非阻塞观察（N1-N4）交由 P2 设计收敛，不构成打回理由。

**Status: approved**
