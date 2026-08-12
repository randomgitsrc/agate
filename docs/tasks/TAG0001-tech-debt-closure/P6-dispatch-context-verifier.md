---
phase: P6
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0001
role: verifier
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
对 TAG0001 P4 实现做 P6 验收：逐条对照 P1 的 20 条 BDD 验收条件，在 worktree 实测验证，产出 P6-acceptance.md（每条 BDD 二值 PASS/FAIL + 证据引用）+ P6-evidence/（执行日志/断言文件）。

### 约束
- **只验证不修改**：不修改 agate/ 任何文件。验收记录的是验收时的事实（PASS 必须基于证据文件实际输出）。
- 本任务是 **agate 协议自身改造**（dogfooding）：验收对象是 worktree `agate/`（已含 TAG0003 工作区架构 + TAG0002 refactor 机制 + TAG0001 技术债闭环）；**禁止触碰 `~/.agate`**（稳定版 v0.40.2 开发工具）。跑测试/验证用 worktree 本体。
- **ui_affected: false**（P2 声明）→ 无 UI/截图需求。
- **BDD 二值规则**：每条 BDD 只允许 PASS 或 FAIL，不允许"调整/跳过/覆盖"。任何 FAIL → 如实记录（gate 会拦）。
- **PASS 行格式**：`- PASS BDD-NN: {描述} ({证据路径})`——行首 `- PASS` 大写、括号内引用证据文件路径（相对 P6-evidence/ 目录）。FAIL 同理。
- **证据要求**：每条 PASS 必须有对应证据文件（验证脚本执行日志/断言记录），存 P6-evidence/。证据文件须有实质内容，日志末行含 `EXIT_CODE: <n>` 格式。P6-evidence/ 必须非空。
- **frontmatter 汇总**：P6-acceptance.md 文件头 frontmatter 必须声明 `pass:`/`fail:`/`ui_affected:` 三个机器字段。
- **BDD 覆盖完整性**：P1 有 20 条 BDD → P6 必须有 ≥20 条验收结果，不能挑验。
- **验收路径提示**（来自 P2-design.md §3 BDD 覆盖映射，逐条对照）：
  - BDD-1/2/4（debt/ 目录归类修正）：WORKFLOW.md 目录图含 debt/、agents/ 注释无 tech-debt、三处 mkdir 9 子目录、TAG0003 修订注存在
  - BDD-3（UPGRADING v0.43.0 变更节）：grep UPGRADING.md 含 debt/tech-debt.md
  - BDD-5..10（schema 校验）：fixture tech-debt.md 合法/非法条目实测 agate-debt-check.py / check-debt.sh（必填/枚举/evidence 非空/closed 准入/id 唯一）
  - BDD-11（T001 回填）：用 T001 复盘 T1-T4 回填成 DEBT 条目，校验器通过
  - BDD-12/19（回退强制）：fixture 建 retreat 提交，check-debt.sh --retreat-coverage 比对；retreat 存在但无 DEBT 条目 → WARNING
  - BDD-13..15（回退比对边界）：文件不存在/空/正常三种情况
  - BDD-16/17/18（P8 debt_check）：P8-release.md 缺 debt_check → exit 1；含 debt_check: none → exit 2；check-gate.sh P8 分支实测
  - BDD-20（债 vs 缺陷判据文档锚点）：tech-debt-template.md 含判据说明
- **自查≠gate**：你产出验收记录，最终 gate 由主 Agent 亲自跑。不要声称"验收已通过"。

### 上游关联
- P1：20 条 BDD（BDD-1..20），risk_level=medium。
- P2：D1-D4 定案（fenced yaml 块 + 独立校验器 + 回退比对 + P8 debt_check 硬留痕）。
- P4：实现完成（core 5 文件 + docs 12 文件 + debt/ 归类修正），review approved；P5 修复 serialize_evidence YAML int 边界。
- P5：全量验证绿（bats 676/0 + consistency 0 ERROR + shellcheck 0）。
- 2 项 SCOPE+ 已回补 P1 scope_resolved（G8 fixture 同步 + consistency 锚点）。

### 输入文件
- docs/tasks/TAG0001-tech-debt-closure/P1-requirements.md（20 条 BDD——**必读**，验收对象）
- docs/tasks/TAG0001-tech-debt-closure/P2-design.md（§3 BDD 覆盖映射 + 验收路径——**必读**）
- docs/tasks/TAG0001-tech-debt-closure/P5-test-results/unit.md（回归证据——必读）
- docs/tasks/TAG0001-tech-debt-closure/P4-review.md（评审记录——必读）
- docs/tasks/TAG0001-tech-debt-closure/P0-brief.md（环境约束——必读）
- AGENTS.md（项目约定——必读）
- agate/scripts/agate-debt-check.py / check-debt.sh / check-gate.sh（验证对象——必读）
- agate/assets/templates/tech-debt-template.md（模板——必读）
- agate/WORKFLOW.md / UPGRADING.md / orchestrator-template.md / SETUP.md（文档 BDD 验证对象——必读）
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

`pass:`/`fail:`/`ui_affected:` 汇总写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P6
task_id: TAG0001           # 替换为实际任务编号
type: acceptance
parent: P5-verification.md
trace_id: T001-P6-20260101 # {task_id}-P6-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: verifier
# ── v2.0 机器汇总 ──
pass: 28                          # int ≥0
fail: 0                           # int ≥0
ui_affected: false                # bool（与 P2 声明一致）
---
```

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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=TAG0001-P5 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 版本隔离三条铁律：跑 gate/读卡片用 `~/.agate`（原版规则）；跑测试/验证用 worktree 本体。
- 测试基线：全量 bats 676 用例（count 670 + sanity 6）；consistency 0 ERROR；shellcheck 0。
- 已核实查证：check-debt.sh / agate-debt-check.py / tech-debt-template.md 已实现；check-gate.sh P8 debt_check 缺失 exit 1；WORKFLOW.md 目录图含 debt/；三处 mkdir 9 子目录；UPGRADING v0.43.0 节含 debt/tech-debt.md。
- 验证临时目录：可用 /tmp/opencode/ 下建 fixture 仓库，产出证据落 P6-evidence/。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
