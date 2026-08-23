---
phase: P1
task_id: TAG0022-confirmed-problems
type: review
parent: P1-requirements.md
trace_id: TAG0022-P1-20260822
status: approved
created: 2026-08-22
agent: requirements-review
---

# P1 需求基线独立评审 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 评审对象：`P1-requirements.md`（290 行，BDD-1..10 连续，5 子项分组）
> 上游核对：`P0-brief.md`（5 issue 验收锚原文）/ `tag0019-21-analysis.md`（main 实测证据基准）/ `HANDOFF-TAG0022.md`（范围/纪律）
> 工作区核验：`git status --short` 仅 task 目录改动（.state.yaml + P1-dispatch-context-* ×2 + P1-requirements.md + P1-progress.md + gate-events.jsonl），**无协议文件越界写入**，analyst 状态标记 `[PROD_NOT_TOUCHED]` 属实

## BDD 评审

> 覆盖维度标注：本任务为纯协议/脚本/CI/测试改造（domains=[backend]），无前端/数据/多端常规面——按角色表逐项标注，前端=✗（不适用），边界/兼容/数据按实际标注；另附协议面团维度。

### 6.1 RM-AG0037 ruff 合并强制

- **BDD-1**（CI ruff job 可被 required check 引用 + 配置步骤文档化）：**可二值判定 PASS**。覆盖维度——实现/配置边界✓（When=核对 workflow diff + grep 文档配置步骤文本，Then 明示「required 勾选本身由维护者配置，不设为本 BDD 的 When 动作」；**未把「设 required check」当实现侧动作**）；多端✗ 前端✗ 数据✗。
- **BDD-2**（新任务合并时 ruff 零违规，验收锚）：**可二值判定 PASS**。覆盖维度——数据✓（两次 `ruff check agate/` 均 exit 0 为 PASS，任一违规 FAIL）；回归拦截✓（防第 4 次复发，与 §4.1 回归拦截声明闭环）；前端✗ 多端✗。

### 6.2 RM-AG0038 M2 迁移闭环

- **BDD-3**（check-gate.py 协议规则类 md 解析清零，验收锚前半）：**可二值判定 PASS**。覆盖维度——边界✓（**A/B/C/D 组 vs E/F 组判定口径显式界定**（D2）：A/B/C/D 清零、任务产出校验走结构化读取、E（.state.yaml）/F（git/CHANGELOG 输出）不计入；判定模式清单由 P2 按 §4.2 细化、P3 固化为静态扫描测试、P5 执行——分阶段可执行，无中间态）；数据✓（命中数=0）；前端✗ 多端✗。
- **BDD-4**（迁移后全量测试绿，验收锚后半）：**可二值判定 PASS**。覆盖维度——数据✓（pytest 0 failed / count-tests 只增不减 / consistency 0 ERROR / structure 0 漂移 四条件，任一不满足 FAIL）；兼容✓（H10 既有 fixture 对账桥接）；前端✗ 多端✗。
- **BDD-5**（S-1~S-6 收紧「YAML 权威、md 禁止承载可判定规则」）：**可二值判定 PASS**。覆盖维度——边界✓（人为单侧漂移动作明确：md 新增可判定规则不入 YAML / 改 YAML 不动 md → 非 0 报 S-*；双侧一致 exit 0）；兼容✓（与 TAG0021 既有 S-1~S-6 语义一致，收紧不推翻）；前端✗ 多端✗。

### 6.3 RM-AG0039 judge 启用强制化

- **BDD-6**（机制后新任务 P1 不写 judge 即被拦，验收锚）：**可二值判定 PASS**。覆盖维度——边界✓（缺 judge/非 true → 非 0 阻断 + stderr 提示；含 `judge.enabled: true` → 放行；**双向判据齐全**）；校验强度（阻断 vs 高优 WARNING）由 P2 定案的悬置点已在 BDD 内显式声明「任一路径均满足『被拦』锚，二值判定以最终 exit code + stderr 语义为准」——非盲区，见非阻塞观察 N1；前端✗ 多端✗ 数据✗。
- **BDD-7**（历史任务跳过，存量不挂）：**可二值判定 PASS**。覆盖维度——兼容✓（exit 0 不被拦；显式对齐 gate_p65 既有 BDD-2 历史兼容语义；「机制后新任务被拦 + 历史任务跳过」双向覆盖完整）；前端✗ 多端✗ 数据✗。

### 6.4 RM-AG0040 M3 实证收尾

- **BDD-8**（实证执行计划 + 触发条件落盘，本 task 验收锚）：**可二值判定 PASS**。覆盖维度——数据✓（**M3 四要素全含**：①评审轮数指标（P2/P4 LLM 评审 subagent 轮数含重试）②真实发现数指标（被采纳/阻止真实问题条数，排除非阻塞建议与机械可抓项）③TAG0018 基线值（4 场 ≈0 净收益：17 非阻塞+1 真实且机械可抓）④不达标决策规则（≈0 且机械覆盖 → 回滚 standard）+ ⑤触发条件（下一 low 风险任务/用户指定薄任务实战））；边界✓（每项声明采集/判定口径，缺任一 FAIL；实证对比报告外置到触发后薄任务，与本 task 交付边界清晰——与 P0-brief known_risks「本 task 内无法自证，需产出实证执行计划+触发条件」一致）；前端✗ 多端✗。

### 6.5 RM-AG0041 环境假象测试根治

- **BDD-9**（任意 basetemp 位置下全量 pytest 0 失败，验收锚）：**可二值判定 PASS**。覆盖维度——边界✓（「仓库内默认 basetemp」+「仓库外显式 `--basetemp=dsh-workspace/ptmp -p no:cacheprovider`」两种位置显式列举，两位置均 0 failed 为 PASS）；兼容✓/平台无关✓（H5：不引入 Unix 假设，探测 git 上下文/按平台分支断言）；前端✗ 多端✗（路径写可性见非阻塞观察 N2）。
- **BDD-10**（平台无关原则不破坏，回归拦截）：**可二值判定 PASS**。覆盖维度——边界✓（`check-platform-assumptions.py` 全树扫描 0 R1-R5 命中 + 人工核对修改点 diff，任一违规 FAIL）；兼容✓（裸 `PATH=`/裸 `python3`/POSIX symlink 硬假设/`/tmp` 路径禁令与 AGENTS.md 测试平台无关原则对齐）；「任意 basetemp 0 失败 + 平台无关不破坏」双向覆盖完整；前端✗ 多端✗。

**BDD 编号**：`#### BDD-1:` ~ `#### BDD-10:` 连续不跳号，每条单一 Given/When/Then（多场景已拆独立编号），无「部分通过/建议调整」中间态——全部可二值判定。**BDD 未自行增删验收标准**：五子项验收锚与 P0-brief issues 逐条对齐（BDD-2↔0037 锚、BDD-3/4↔0038 锚、BDD-6↔0039 锚、BDD-8↔0040 锚（计划+触发条件形态）、BDD-9↔0041 锚；BDD-1/5/7/10 为锚的实现边界/收紧/历史兼容/平台保护衍生，均能在 P0-brief 原文找到出处，非新增验收标准）。

## 隐含需求覆盖

- 数据维度：**覆盖**——BDD-2/4/9 以退出码/计数为客观判据，无格式/迁移/缺失性数据面；本任务无数据迁移需求（协议面）。
- 前端维度：**N/A（不适用）**——domains=[backend]，无 UI/视觉/UX 面；P1 frontmatter 正确未声明 ui_render_shape/ui_ux_dimensions、无 vision 能力条目（P1 卡视觉硬要求不触发），`capability_requirements` 三态齐全且合法。
- 多端维度：**N/A**——无 API↔客户端契约。
- 边界维度：**覆盖**——D2 的 A/B/C/D vs E/F 判定口径（BDD-3）、双 basetemp 位置（BDD-9）、单侧漂移构造（BDD-5）、judge 双路径（BDD-6）、/tmp 只读约束（H8）。
- 兼容维度：**覆盖**——历史任务跳过（H11/BDD-7）、P1 gate 既有锚点格式不回归（H12）、既有 fixture 对账桥接（H10）、测试平台无关不破坏（H5/BDD-10）、count-tests 只增不减（H7）。
- 协议面隐含依赖（本任务重点，规格要求逐项核对）：**H1 SELF-GATE 触发面 ✓ / H2 实现 vs 配置边界 ✓ / H3 0038/0039 同簇互扰分批 ✓（D3） / H4 0040 外部薄任务依赖 ✓（D4/BDD-8） / H5 平台无关原则 ✓ / H6 本任务 P6.5 judge 生效 ✓（.state.yaml 已写 judge.enabled: true，实证核对） / H7 count-tests 冻结 ✓ / H8 pytest 环境约束 ✓ / H9 UPGRADING 章节 ✓ / H10 既有测试兼容 ✓ / H11 judge 校验与历史跳过并存 ✓ / H12 P1 gate 锚点格式不变 ✓** —— 12 条全覆盖，无遗漏。

## 裁剪评审

- **阶段裁剪**：`phases: [P1..P8]` 全保留无跳过，逐阶段理由充分（P2 因 risk_level=high 需 plan-eng-review（C8 强制）+ 迁移映射清单；P3 三子项（0038 静态扫描测试 / 0039 judge 校验用例 / 0041 环境测试改造）均可写失败测试 TDD 先红后绿；P4 五子项分批 commit（0038/0039 错开文件）；P5 四网验证（pytest/consistency/ruff/count-tests）；P6 验收 + **P6.5 judge 复核**（judge.enabled: true 已写入，H6）；P7 跨文件交叉核对（CI/check-gate/state-machine/P6 卡/P1 卡/测试）；P8 版本发布 + UPGRADING 破change性变更 + SELF-GATE review）。改动面大（CI/check 脚本/gate 逻辑/测试卫生四域）+ 同簇互扰 + 工具链自举风险——不裁合理。
- **risk_level: high**：与实际匹配——改动面 = CI 配置 + check-gate.py（主 Agent 每阶段总闸）+ state-machine + P6 卡 + P1 卡 + 测试，五子项同簇互扰（0038/0039 同触 check-gate.py），且触发 SELF-GATE 自举风险；与 P0-brief known_risks / HANDOFF §7 一致。
- **ceremony: standard**：fail-closed 缺省档，正确——本任务为 high/全阶段任务，非 thin 候选（thin 档实证对象是另立的 low 薄任务，符合 RM-AG0040 触发条件设计）；非 full 档故「full→phases 含 P7」不适用，但 phases 仍含 P7，声明一致。
- **capability_requirements 三态**：3 项全部 available（text-analysis-scanning / python-testing-and-lint / protocol-editing），无 supplementable、无 GAP——判断正确（纯协议/脚本/CI 任务无视觉/环境补充能力需求）；verification_env 恰当不声明（无外部服务依赖）。

## 同类扫描完整性

四组扫描齐备且逐条判定、结论落盘正文（§4.1-4.4）：
- **扫描 1 ruff 消费点**（5 条命中逐条判定：本次处理=CI ruff job / 本次不处理=pyproject 规则集、本地 test_bdd_34、文档引用、注释历史 + 理由）+ 关键佐证（*.sh/pre-commit 无 ruff 消费）+ 回归拦截声明（防护 required check + BDD-2）✓
- **扫描 2 check-gate.py md 解析点**（84 处 regex 命中分 6 组 A-F 逐条判定：A/B/C/D 本次处理、E/F 本次不处理 + 理由）+ 关键佐证（0 处 rules/*.yaml 读取）+ 回归拦截声明（转 BDD-3）✓
- **扫描 3 judge.enabled 消费点**（53 命中分 8 类逐条判定：仅新增 P1 校验点处理、pre-commit/ci-backstop/P6 卡保持）+ 消费链三方一致佐证 + 互扰说明（与 0038 批次）+ 回归拦截声明（转 BDD-6/7）✓
- **扫描 4 ceremony 消费点**（110 命中分 6 类逐条判定：仅实证边界标注、机制保持）+ 关键佐证（`ceremony: thin` 48 处命中全为 fixture/条文引用、无实战）+ 回归拦截声明（无新增回归点）✓

## 审声明（风险分级/裁剪声明 vs diff 证据）

- **git 状态核验（TAG0019 要求）**：`git status --short`（worktree `feat/TAG0022-confirmed-problems`）实际改动面 = `agate-workspace/tasks/TAG0022-confirmed-problems/` 内 `.state.yaml`（修改）+ `P1-dispatch-context-analyst.md`/`P1-dispatch-context-requirements-review.md`/`P1-progress.md`/`P1-requirements.md`/`gate-events.jsonl`（新增）——**仅任务目录产出 + 派发上下文，analyst 无越界写协议文件**；`[PROD_NOT_TOUCHED]` 与 git 证据一致。
- **需求声明的五子项改动面（§5 范围表）vs P0-brief/分析文档证据**：一致。——（1）RM-AG0037：`protocol-tests.yml:106-116` 实测存在 `ruff:` job（name: ruff、`pip install ruff && ruff check agate/`）且非 required check，改动面=workflow 稳定化+文档；（2）RM-AG0038：check-gate.py 实测 `_md_field_get`（L95/L173-174，MD_FIELD_GET 调 agate-md-field-get）~16 处调用（L327/380/381/412/471/533/554/606/929/931/939/940/1005/1006/1030/1031）+ `_NC_RE`/`_SUGGEST_RE`（L101-102，L523-558 使用）+ yaml 块解析（L336-338）+ P6/P7 格式判定正则，**0 处 rules/*.yaml 读取**（grep 仅 L657 注释）——「22 处 md 解析 / 0 处 YAML」与 §4.2 六组分类一致；（3）RM-AG0039：check-gate.py gate_p65（L977-995）实测「judge 未启用 → 早退 0」，state-machine.md:442-443 实测含「P1 初始化时主 Agent 写入；缺失/false = 历史任务」自写开关——「软强制」成立；（4）RM-AG0040：check-routing.py 实测（L79-138）只校验 ceremony 声明/三值/thin 四要素/算分对拍，**不校验「thin 是否真跳过评审」执行语义**——M3 未闭环机械证据成立；（5）RM-AG0041：`test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`（basetemp 在 git 仓库内 → git_ok:false 语义被破坏，TAG0019 P4/P5/P6 累计 3 轮复现 + TAG0021 P4/P5 多次复现登记）与 `test_env_adapt_docs.py::test_bdd_25_consistency_zero_error`（共享 basetemp 污染，TAG0021 复现 2 次隔离转绿）——环境假象基线成立（TAG0020 known-failures.md + roadmap RM-AG0041 同文登记）。
- **ceremony: standard、phases 含 P7**：非 full 档（full→P7 不可裁核对不适用）；phases 声明含 P7 且理由充分——声明与实际改动形态匹配。
- **结论**：声明与实际一致，无「声明≠实际」情形，不触发 needs-revision/rejected 条件。

## P1 纯净性

- **无解决方案设计掺入**：§5 关键决策（D1-D4）均为范围/边界决策（实现 vs 配置边界、判定口径、分批纪律、交付形态），正文明示「不涉及具体实现方案（候选方案与机制设计留 P2 architect）」；BDD 的 When 全部为「运行命令后观察退出码/输出/文件」行为判据，未绑定实现符号。
- **无「设 required check 当实现」越界**：BDD-1 的 Then 明示 required 勾选由维护者配置、不设为本 BDD 的 When 动作（审核重点 2 ✓）。
- **实现细节未前移**：BDD-6 校验强度（阻断 vs 高优 WARNING）待 P2 定案属 P1 行为锚的正常下放，非混入实现；BDD-3 判定模式清单下放 P2 细化映射、P3 固化扫描测试——分阶段职责清晰。

## 评审重点提示（TAG0022 特殊性）逐项应答

1. **五子项验收锚 ↔ P0-brief issues 逐条对齐**：✓ 全部命中（见 BDD 评审逐条标注），BDD 未自行增删验收标准；
2. **BDD-1 未把「设 required check」当实现侧动作**：✓（When=核对 workflow diff + 文档 grep，Then 外置说明）；
3. **BDD-3 判定口径（A/B/C/D vs E/F）可二值判定**：✓（D2 显式界定 + 命中数=0 判据 + 分阶段固化路径）；
4. **BDD-6/7 覆盖「机制后新任务被拦 + 历史任务跳过」双向**：✓；
5. **BDD-8 含 M3 四要素 + 触发条件**：✓（5 项全齐，各有采集/判定口径）；
6. **BDD-9/10 含「任意 basetemp 0 失败 + 平台无关不破坏」双向**：✓。

## 非阻塞观察（不构成 needs-revision，建议 P2 闭环）

- **N1（BDD-6 校验强度悬置）**：BDD-6 双路径（阻断 vs 高优 WARNING）中若 P2 选「高优 WARNING」且最终 exit code=0，将与 Then 的「非 0 退出（阻断）」字面冲突——BDD 已声明「二值判定以最终 exit code + stderr 语义为准」兜底，**建议 P2 尽早冻结该语义（推荐 fail-closed exit≥1，对齐 gate_p65/缺失必填字段惯例）**，P3 据此固化用例。
- **N2（BDD-4/9 basetemp 路径写可性）**：`[P0_STALE]` 已声明 ptmp 只读，但 H8/BDD-4/BDD-9 仍以 `dsh-workspace/ptmp` 为仓库外验证 basetemp；本沙箱 workspace-write 写面可能仅 worktree（git 仓库内，与 test_bdd_7 的 git 上下文语义相关）——沿 **TAG0021 SCOPE+3 先例**，建议 P2/P3 对 basetemp 写可性实证并冻结权威路径（仓库外写可位置若不可得，P5 需按「探测 git 上下文」修复方向实跑，这正是 RM-AG0041 的验收核心，P2 影响面应显式覆盖）。
- **N3（BDD-4「≥ 立项基线」数值未冻结）**：count-tests 基线建议 P2/P3 冻结具体数字（现 1202，分析文档），避免 P6 判据漂移。

## 评审结论

**status: approved。**

- BDD-1..10 全部可二值判定、编号连续、单一 GWT、无中间态；五子项验收锚与 P0-brief issues 逐条对齐，未增删验收标准（锚点：BDD-2/3+4/6/8/9 ↔ RM-AG0037/38/39/40/41）；
- 隐含需求 H1-H12 全覆盖（协议面团 12 条逐项核对通过）；
- 同类扫描四组齐备（§4.1-4.4，逐条判定 + 关键佐证 + 回归拦截声明落盘正文）；
- 裁剪合理（phases 全保留理由充分；risk_level=high 匹配；ceremony standard fail-closed 正确）；
- 审声明核对通过（git status 证据：改动面仅 task 目录、无越界写协议文件；五子项改动面声明与 P0-brief/分析文档实测一致）；
- P1 纯净性通过（无方案设计混入、无「设 required check 当实现」越界、BDD 行为级判据）。

3 项非阻塞观察（N1/N2/N3）建议 P2 闭环，不阻塞推进。