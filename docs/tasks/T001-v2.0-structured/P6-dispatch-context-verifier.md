> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P6
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: verifier
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

对 T001 的 P1-requirements.md 全部 28 条 `#### BDD-NN` 逐条做验收判定（PASS/FAIL），产出 `docs/tasks/T001-v2.0-structured/P6-acceptance.md` + `docs/tasks/T001-v2.0-structured/P6-evidence/`。**这是用户视角/BDD 视角的验收，不是重新跑一遍 P5 的技术测试**——P5 已确认代码能跑通过，P6 要确认"每条 BDD 描述的行为，现在真的成立"，要点出具体证据，不是"测试绿了所以 PASS"这种同义反复。

### 核心原则（阶段卡片已强调，这里重申）

**功能验证和 gate 格式都必须满足，缺一不可**：不能只满足"行首 `- PASS BDD-N:` 格式"而不实际核实该 BDD 描述的行为是否真的发生；也不能验证了行为却不按格式写。**验收报告记录的是你验收时观察到的事实**——如果验收时发现某条 BDD 实际不成立，写 FAIL，不要因为"应该是对的"就写 PASS。

### 约束

1. **非 UI 任务**：P2 声明 `ui_affected: false`，不需要 vision-analyst，不需要截图证据，用断言输出/命令结果作证据。
2. **本任务是协议工程任务，不是典型 Web 应用**——"证据"的形式不是截图，而是：
   - 对于有直接 bats 测试覆盖的 BDD：引用 `docs/tasks/T001-v2.0-structured/P5-test-results/unit.md` 里对应测试用例的 `ok N {测试名}` 行（这是已经跑过、独立留痕的真实证据，不需要重新跑），并在 `P6-evidence/` 下写一个小文件摘录该证据（不是 1 行文本糊弄，要包含测试名+断言了什么+为什么这构成该 BDD 的证据）
   - 对于无直接可执行断言的 BDD（`P3-test-cases.md` 里已标注"无 P3 阶段 @test"的几条，如 BDD-11/13/14/23~28 里的部分）：**自己动手验证**——跑对应命令（如 `count-tests.sh` 验 BDD-11、`check-protocol-consistency.py` 验 BDD-13、读 `P2-design.md` §10 原文验 BDD-14、读 `task-files.md`/角色卡验 BDD-24 的可复制样例是否存在且能 `yaml.safe_load`、查 git log 验 BDD-28 本任务自身全程用 v0.35 gate），把验证过程和结果写进 `P6-evidence/`
   - **不要空手声称"已验证"**——每条 PASS 都要有可复核的具体产出物（命令输出片段/文件路径/测试名），哪怕只是几行
3. **BDD 与设计落点/测试用例的映射**（避免你重新推导，直接用已有权威映射）：
   - `docs/tasks/T001-v2.0-structured/P2-design.md` §9"BDD 覆盖映射（P1 基线 28 条 → 设计落点）"——每条 BDD 对应哪个设计章节
   - `docs/tasks/T001-v2.0-structured/P3-test-cases.md` §2-§5（按流 A/B/C/D 分组的 BDD→测试用例映射表，含每条测试当时的红/绿状态说明）——这是你验收时定位"这条 BDD 该看哪个测试"的主要工具
   - `docs/tasks/T001-v2.0-structured/P4-implementation.md`（实现记录，含 4 条 `[DESIGN_GAP:]`——验收这几条对应的 BDD 时要特别注意，DESIGN_GAP 意味着实现与设计有已声明的偏离，你需要判断这个偏离是否导致对应 BDD 事实上不成立，如果不确定就如实记录，不要自己下结论说"偏离不影响"）
4. **frontmatter 汇总字段**（BDD-16 要求，本任务自己也要用新格式写，dogfooding）：
   ```yaml
   ---
   phase: P6
   task_id: T001
   type: acceptance
   parent: P5-verification.md
   trace_id: T001-P6-20260810
   status: draft
   created: 2026-08-10
   agent: verifier
   pass: {int}
   fail: {int}
   ui_affected: false
   ---
   ```
   `pass`/`fail` 必须是你逐条判定后的真实计数，不要先写个数字占位再"凑"正文条数去匹配。
5. **正文格式**：每条 `- PASS BDD-NN: {描述} ({证据路径})` 或 `- FAIL BDD-NN: {描述} ({说明})`，行首精确匹配，不用表格/emoji。总结行（如有）不要用 `- PASS`/`- FAIL` 开头。
6. **P6-evidence/ 目录要求**：每个证据文件有实质内容（不是 1 行文本充数）。可以是 `.md`/`.txt`/`.log` 文件，内容是"这条 BDD 的具体验证过程 + 结果摘录"。
7. **DESIGN_GAP 交叉核对**：`P4-implementation.md` 有 4 条 `[DESIGN_GAP:]`，本次验收时，对每条 DESIGN_GAP 涉及的 BDD 做特别标注（在对应 BDD 的证据文件里提一句"该 BDD 的实现存在已声明的 DESIGN_GAP，详见 P4-implementation.md 第 X 行"），这是为 P7 一致性检查做铺垫，不是让你现在就裁决对错。
8. **不要修改任何代码/测试/设计文档**——你是纯验收角色，发现问题如实记录 FAIL，不要自己去修。
9. **28 条 BDD 清单**（从 P1-requirements.md 摘录，逐条验收，不能漏）：BDD-1 到 BDD-28，分组信息见 P3-test-cases.md：流A（BDD-1~15）、流B（BDD-16~20）、流C（BDD-21~24）、流D（BDD-25~28）。
10. **自查用命令**（自查不是 gate，我会自己跑 check-gate.sh/check-p6-evidence.sh/check-p6-provenance.sh）：
    ```
    cd /home/kity/oclab/agate/.worktrees/v2.0
    bash ~/.agate/scripts/check-p6-format.sh --fix docs/tasks/T001-v2.0-structured/P6-acceptance.md
    ```
    产出后自己跑一遍这条做格式归一化（大小写/全角冒号等），这是阶段卡片要求的①自动格式化步骤。

### 上游关联

- P1-requirements.md 的 28 条 BDD 是验收对象本身。
- P2-design.md §9（BDD 覆盖映射表）+ §10（语义真实性边界声明，BDD-14 的验收依据）。
- P3-test-cases.md（BDD→测试用例映射，含红绿状态历史）。
- P4-implementation.md（实现记录 + 4 条 DESIGN_GAP）。
- P5-test-results/unit.md（P5 全量测试的完整 TAP 原始输出，600/600，可直接引用其中的 `ok N {测试名}` 行作证据，不需要重新跑）。

### 输入文件（自己读）

- `agate/assets/execution-roles/verifier.md`（你的角色定义，先读这个，注意 P6 模式的产出规格）
- `docs/tasks/T001-v2.0-structured/P1-requirements.md`（28 条 BDD 全文）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §9、§10
- `docs/tasks/T001-v2.0-structured/P3-test-cases.md`（全文，BDD→测试映射）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（全文，含 4 条 DESIGN_GAP）
- `docs/tasks/T001-v2.0-structured/P5-test-results/unit.md`（P5 完整测试输出，证据来源）
- `agate/assets/templates/task-files.md`（BDD-24 验收用，检查可复制样例是否存在）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P6

路径：phase-cards/P6-acceptance.md
---
# P6 — 验收

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P6 不可裁剪。no_behavior_change 可简化（快速验收），不可省略。

## 如果是首次进入本阶段

1. 派发 verifier subagent → 产出 P6-acceptance.md + P6-evidence/
   1.1 写 P6-dispatch-context-verifier.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. UI 任务：派 vision-analyst → 产出 vision-reports/
3. 主 Agent 逐条核实 BDD 对照结果
4. **功能验证和 gate 格式都必须满足**（T046 教训：先做功能验证，不要只凑格式）
5. **运行 `bash $AGATE_ROOT/scripts/check-p6-format.sh --fix "$TASK_DIR/P6-acceptance.md"`** 归一化 PASS/FAIL 大小写和行首空白（verifier 产出后、gate 前，① 自动格式化）
6. 预跑 check-gate.sh P6 + check-p6-evidence.sh + check-p6-provenance.sh
7. 更新 .state.yaml phase=P6 → P7
8. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
9. git commit -m "wf({Txxx}-P6): {摘要}"

## 如果是重试

确认上一轮失败原因（BDD 不覆盖 / 证据不足 / gate 格式拦截）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P6 MAX=2）

## 核心原则 ⚠️

**功能验证和 gate 格式都必须满足。** T046 教训：花 2 小时凑 PASS 格式，没花 5 分钟检查 API 响应头。不接受只满足格式不验证功能，也不接受只验证功能不满足格式。gate 是必要条件（格式不对 → commit 不了），不是充分条件（格式对了 ≠ 功能正确）。

**验收报告记录的是验收时的事实，不是修复后的状态。** P6-acceptance.md 的 PASS/FAIL 声明必须基于 evidence 文件的实际输出。如果验收时 BDD 为 FAIL，写 FAIL——修复后重新验收时再改 PASS。不能在同一个 P6 acceptance 里写"修复后 PASS"。

## 前置条件

- [ ] P1-requirements.md BDD 验收条件完整（含 SCOPE+ 增补）
- [ ] P1 声明的 capability_requirements 中 ability 为 available

## 派发

- **角色**：verifier（`{agate_root}/assets/execution-roles/verifier.md`）
- **UI 任务追加**：vision-analyst（`{agate_root}/assets/execution-roles/vision-analyst.md`）
- **输入**：P1-requirements.md + P5-test-results/
- **输出**：P6-acceptance.md + P6-evidence/

## 产出规格

### P6-acceptance.md

- BDD 逐条对照，每条只允许 PASS 或 FAIL（不允许"调整/跳过/覆盖"）
- 所有 PASS 必须有文件引用：`- PASS Bxx: 描述 (p6-bxx.png)` 或响应日志/断言文件
- UI 任务：操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图但须有断言记录文件
- UI 任务：每条 UI 类 PASS 含 vision 引用：`(vision: vision-reports/bxx.yaml)`

**PASS 行最小格式规范**：

```
- PASS BDD-NN: {描述} ({证据路径})
```

证据路径格式：
- 截图：`(screenshots/{filename}.png)`
- vision：`(vision: vision-reports/{filename}.yaml)`
- 其他：`(result.json)` / `(assert.log)` / `(P6-evidence/{filename})` / ...
- 多文件引用（逗号分隔）：`(file1.json, file2.log)` / `(screenshots/a.png, screenshots/b.png)`

描述文本可自由添加，不影响解析（provenance 脚本用精确正则提取路径）。

**总结行格式**：行首 `- PASS`/`- FAIL` 只用于 BDD 条目，不得用于总结行。总结行用其他格式（如 `**Summary**: 34/34 PASS, 0 FAIL`）。check-p6-format.sh `--fix` 会自动修正违规总结行。

### P6-evidence/

- 必须非空，每个文件含实质内容（截图 >1KB，断言文件含实际输出）
- 不接受 1 行文本文件充数（T046 教训：15 个 1 行 txt 文件凑 provenance 数量）
- 元素级截图建议使用父级元素 + padding，避免过小截图（≤1KB 虽不阻断但会触发 WARNING）
- 操作类 BDD 截图必须互不相同（md5 完全重复会被 hook 硬阻断，无例外）。
  若某个行为差异类 BDD 天然会产出视觉相同的页面（如两个不同查询都命中同一个空状态），
  优先改用非截图证据（断言日志 / response.json）而非截图，或截图时带上能体现差异的元素
  （如带时间戳的调试面板、高亮差异区域），确保截图本身逐字节不同。
  查询类 BDD 本来就可以不截图，这类场景应优先归为查询类而非勉强用截图。

### vision-helper 结论绑定 ⚠️

- `ui_affected: true` 时至少一条 PASS 基于 vision-helper 报告
- vision-helper 报 `blocker_count > 0`：不能仅用程序化指标（naturalWidth>0, complete=true, HTTP 200）反驳
- 必须追查根因（curl -I 检查响应头 / DevTools Network / API 日志），追查结果写入 P6-acceptance.md

## gate 规则

```bash
check-p6-format.sh --fix $TASK_DIR/P6-acceptance.md  # ① 自动格式化（verifier 产出后、gate 前）
check-gate.sh P6 $TASK_DIR      # FAIL=0 / 总数>0
check-p6-evidence.sh $TASK_DIR  # 证据目录非空 / UI截图>1KB / md5去重
check-p6-provenance.sh $TASK_DIR # 证据-结论对应 / dispatch-context审计 / BDD对照
```

- FAIL > 0 → gate exit 1 → 回 P4

格式问题 → 运行 check-p6-format.sh --fix 归一化 → 再验 gate → … → 通过（⑩迭代循环，格式迭代和 gate 重试共享 retry 预算）

**⚠️ FAIL > 0 时，主 Agent 不能直接改项目源码让它变绿**：P6 是 self-authored gate（判定对象是 verifier 自己写的 P6-acceptance.md），验收阶段本身不应该有代码变更——`pre-commit-gate.sh` 会硬拦截 phase=P6 时暂存的非证据文件（不在 `P6-evidence/` 下的文件）。正确流程：诊断问题出在哪个上游阶段 → 退回该阶段（`agate/rules/state-transitions.md` 回退规则，退回前须先跑 `agate-archive-stale-outputs.sh` 归档当前 P6 产出，或用 `agate-retreat-to.sh` 自动化多步回退）→ 重新派发对应角色 subagent 修复 → 重新走到 P6 时，旧的 P6-acceptance.md/P6-evidence/ 已被归档清空，verifier 必须重新产出真实证据，不存在"挑几条改改、其余沿用旧结论"的空间。

## 按包拆分并行（条件触发，受限模式）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

P6 采用**证据并行、验收文件不并行**模式：

1. 各包 verifier 并行跑 BDD 验证，证据写入 P6-evidence/{pkg}/，同时写 P6-evidence/{pkg}/results.md（PASS/FAIL 行 + 证据引用，不进 gate）
2. 所有 verifier 返回后，派一个汇总 verifier 逐包读取 results.md，转抄整合进唯一的 P6-acceptance.md
3. 汇总 verifier 确认各包 BDD 编号合集 = P1 全部 BDD 编号，无重复/遗漏，**必须在 P6-acceptance.md 中记录交叉核对结果**

基础设施隔离同 P5（端口/数据库/截图目录独立）。

## 推进条件（全部满足才写 phase: P7）

- [ ] 所有 BDD PASS（FAIL=0）
- [ ] P6-evidence/ 目录非空 + 证据文件被引用
- [ ] UI 任务：vision-helper blocker_count=0；blocker>0 时须在 P6-acceptance.md 写明追查命令 + 输出 + 根因结论（仅写"已追查"不合规）
- [ ] provenance 审计通过

## 常见错误（T046 实证）

1. **用 DOM 属性替代视觉验证**：img.src 被重写 = 图片显示正常。不对——还有 Content-Type、CORS、CSP 等 100 种原因导致图片不渲染。**vision-helper 说破了就是破了**
2. **凑 PASS 数量**：deferred BDD 标 PASS、用 1 行文本文件充证据 → provenance 审计能通过但功能不对
3. **只验证中间指标不验证用户结果**：naturalWidth>0, complete=true, API 返回 200 → 结论"功能正常"。用户看到的：破图。**问自己：用户看到了什么**
4. **收到视觉否定先反驳**：vision-helper 报异常 → 先 curl -I 查响应头 → 再决定是 vision 误报还是真问题。T046：三次视觉否定被三次程序化指标反驳，15 分钟浪费
5. **验收失败自己动手改代码**：这和上面几条本质是同一类问题（判定证据和判定对象由同一人在同一时间点生产），只是这次改的是真代码而非假 markdown，反而更难被察觉。正确动作是退回重新派发，见上方 FAIL > 0 的处理说明

gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P7 一致性检查依赖 P6 的 BDD 对照结果
- 验收结果是判定任务成败的最终依据——P8 发布只是机械步骤

## 自查≠gate
写完验证脚本后应自跑确认脚本可执行（自查），但自查通过 ≠ P6 gate 通过。
P6 gate 由主 Agent 亲自跑 gate 脚本（check-gate.sh P6 + check-p6-evidence.sh + check-p6-provenance.sh），验证的是 verifier subagent 的产出。结果以主 Agent 跑的 gate 脚本为准。
不要在返回中声称"验收已通过"或"全部 BDD PASS"——只返回路径 + 摘要。

> 完成 → 读 phase-cards/P7-consistency.md
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P5 status=active（P6 验收产出后，主 Agent 会在同一个 commit 里把 phase 推进到 P6——不要自己改 .state.yaml，那是主 Agent 的工作）。
- P5 已通过：600/600 测试、594 基线、0 一致性错误、0 shellcheck 警告，commit f4bd942。
- P4 实现全部完成：9 个 commit（3754e9d/ebda17e/901f61d/2b56579/68e4173/e566303/3064734/17f11e5/f476834），含 1 个已修复的 CRITICAL、4 条已核实的 DESIGN_GAP、4 条已修复的 self-gate MISALIGNED、1 条新增 ADR-007。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
