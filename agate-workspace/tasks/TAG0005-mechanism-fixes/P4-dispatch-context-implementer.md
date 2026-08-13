> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0005
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

实现 TAG0005 机制修复批的 6 处修复（P2-design.md §2.1-2.6），让 P3 的红灯测试变绿。**不改测试迁就实现**——测试是 P3 锁定的契约。

### 约束

- **实现范围（P2-design.md 锁定，六处）**：
  1. **RM-AG0010（§2.1，BDD-1/2）**：三处 C8 表 backend 行补 plan-eng-review（P2）触发：
     - `agate/role-system.md` L56：`| backend | 任意 | plan-eng-review（P2 方案评审）+ review（P4 后）|`
     - `agate/rules/review-mapping.md` L17：拆两行 `| backend | 任意 | plan-eng-review | P2 |` + 保留 `| backend | 任意 | review | P4 后 |`
     - `agate/phase-cards/P2-design.md` C8 表（L93-97）：新增 `| backend | 任意 | plan-eng-review（P2 方案评审）|`
     - 三处各补**去重说明**（backend+high 均命中 plan-eng-review → 去重只派 1 次）。check-gate.sh P2 分支**不动**（BDD-2）
  2. **RM-AG0011（§2.2，BDD-3/4/5）**：
     - `agate/scripts/agate-gate-p5-count.py`：输出 `"{main} {aux}"`（如 `1 2`）——`main = len(re.findall(r"^  P5:", block))`（精确 P5:，不匹配 P5_*）；`aux` 计数 `^  (P5_\w+):` 且**排除 `_formatter` 键**；无 gate_commands 块输出 `0 0`
     - `agate/scripts/check-gate.sh` L249-258：读双值 → `P5_MAIN`/`P5_AUX`/`P5_TOTAL`，`P5_TOTAL>1` 时 WARNING 文案 `GATE P5 WARNING: P2 声明了 ${P5_MAIN} 个主命令 + ${P5_AUX} 个辅助命令（共 ${P5_TOTAL} 条 gate_commands.P5 命令），请确认已全部执行（非子集）。` + 保留 T060 第二行
  3. **RM-AG0012①（§2.3，BDD-7/8/9）**：
     - `agate/assets/templates/dispatch-prompt.md`：主代码块（L9-13）**移除**「## Review 角色特别指令」节；在 `## 阶段特定提示（按需追加到 prompt 末尾）` 下新增首个子节 `### Review 角色特别指令`（代码块含完整指令文本，原样保留 status draft→approved/rejected/needs-revision 语义）
     - `agate/scripts/agate-render-dispatch-prompt.sh`：新增 review_appendix 逻辑——`ROLE_DIR=review-roles` 时用 `sed -n '/^### Review 角色特别指令$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block` 提取；组装顺序 main_block → review_appendix → 阶段 appendix
     - `agate/dispatch-protocol.md` 内联模板（L427-494）：在「## 你的角色定义」后加备注「若派发评审角色（review-roles），须追加 assets/templates/dispatch-prompt.md 中评审角色专用节的 status 字段语义说明」。**避免出现「Review 角色特别指令」字面量**（BDD-9）
  4. **RM-AG0012②（§2.4，BDD-10/11）**：缺陷已修，仅测试已加（RP.17），无需脚本改动
  5. **RM-AG0003（§2.5，BDD-12/13/14）**：`agate/dispatch-protocol.md` L111-118「第 1 次空返回」改写为含「自动重试一次」（不占 retries[Pn] 槽位）+ 会话时长 <1min 告警（「会话时长异常短」，复用 L128 派发耗时弱信号）；「禁止」段（L124）后补「自动重试一次」是「相同 prompt 直接重试」禁令的唯一豁免说明；**retry 上限/PAUSED 段不改**（BDD-14）
  6. **同类扫描守卫 / check-debt.sh（§2.6，BDD-15/16）**：`agate/scripts/check-debt.sh` L26/L28 依赖加载失败 exit 0→2（消息保留「缺少 agate-workspace-resolve.sh」措辞）；头部注释 L5/L13 同步；「有意跳过」分支（无 retreat 提交 exit 0）保持
- **同步更新**（P1 I4/I8 + P2-review NB-1）：
  - `agate/tests/README.md` L33：render 计数表 16→20（含既有 1 漂移修正）
  - `agate/scripts/README.md` L23：check-debt.sh `--retreat-coverage` 描述从「恒 exit 0」改为「依赖加载失败 exit 2，无 retreat 提交等有意跳过 exit 0」
  - `agate/scripts/state-transitions.md` L84 / `agate/UPGRADING.md` L120 若含 check-debt「恒 exit 0」表述 → 同步（P2-review NB-1 建议覆盖）
  - count-tests.sh L22 陈旧引用**不改**（P1 I8 排除）
- **最小实现**：只改上述清单，不加功能、不重构、不顺手改进。若发现 P2 设计有歧义 → `[DESIGN_GAP: ...]` 标注；发现新需求 → `[SCOPE+]`；prompt 漏了 P2 已声明的事 → `[SCOPE_GAP]`
- **测试纪律**：P3 测试是契约，改实现不改测试。RP.17（exit 2 已实现）本应已绿——确认它保持绿即可
- **格式约束**：P4-implementation.md 约束节避免行首 `- PASS`/`- FAIL`（provenance 预检检测）
- **自查≠gate**：写完自跑相关测试（`bats agate/tests/unit/agate-gate-p5-count.bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-render-dispatch-prompt.bats agate/tests/unit/agate-debt-check.bats`）确认基本变绿，但自查≠P5 gate，不要声称"P5 已过"

### 上游关联

- `P2-design.md`（§2.1-2.6 实现方案 + §4 files_to_read + §7 完成标准）
- `P3-test-cases.md`（测试契约，红灯要变绿）
- `P2-review.md`（approved + NB-1 scripts/README 同步建议）

### 输入文件

- `agate-workspace/tasks/TAG0005-mechanism-fixes/P2-design.md`（实现方案）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P3-test-cases.md`（测试契约）
- `agate-workspace/tasks/TAG0005-mechanism-fixes/P2-review.md`（NB 建议）
- 协议文件（按 P2 §4 files_to_read 清单读取，标了行号范围的只读片段）：
  - `agate/scripts/agate-gate-p5-count.py:14-20`
  - `agate/scripts/check-gate.sh:249-259`
  - `agate/scripts/agate-read-p5-commands.py:21-37`（参照 _formatter 排除语义，不改）
  - `agate/assets/templates/dispatch-prompt.md:6-101`
  - `agate/scripts/agate-render-dispatch-prompt.sh:63-106`
  - `agate/dispatch-protocol.md:105-135`、`agate/dispatch-protocol.md:427-494`
  - `agate/scripts/check-debt.sh:19-50`
  - `agate/role-system.md:50-68`、`agate/rules/review-mapping.md:15-30`、`agate/phase-cards/P2-design.md:89-101`
  - `agate/tests/README.md:28-59`、`agate/scripts/README.md`（L23）
  - `agate/scripts/state-transitions.md` L84、`agate/UPGRADING.md` L120
- `{agate_root}/assets/execution-roles/implementer.md`（角色定义）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.sh 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.sh $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.sh P4（确认暂存区有代码文件）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P4，不要提前写 P5——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P4): {摘要}"（phase=P4，P4 产出含 P4-implementation.md + 代码文件）
7. P4 commit 完成后进入 P5：**phase 推进 P5 随 P5 产出 commit 一起**（P5-test-results/ 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`{AGATE_WORKSPACE}/tasks/{Txxx}/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `{AGATE_WORKSPACE}/tasks/{Txxx}/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。**回退落地后必须建 DEBT 条目**（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 `assets/templates/tech-debt-template.md`——TAG0001 强制，见 `agate/rules/state-transitions.md` 回退规则节）。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.sh 确认红灯（测试先于实现）
- [ ] 未跳过 P4（如有裁剪理由，见上方裁剪跳阶）

## 派发

- **角色**：implementer（`{agate_root}/assets/execution-roles/implementer.md`）
- **输入**：P2-design.md（files_to_read 导航 + gate_commands）+ P3-test-cases.md + P0-brief.md（env_constraints）
- **输出**：代码文件（在 P4-implementation.md 声明的 implementation_dir 下）
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md` + 以下阶段特定追加：

```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。

## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |

多个评审角色 `专家组并行` → 所有返回后派组长汇总 → 统一 P4-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.sh 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**——跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 → 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 → 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。

## gate 规则（check-gate.sh 会跑）

```bash
check-gate.sh P4 $TASK_DIR
```

- **exit 0**：暂存区含非 md/yaml 代码文件（git diff --cached --name-only）
- **exit 1**：暂存区仅 .md/.yaml 文件（无实际代码变更）→ 不能推进

## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成

## 常见错误

1. **不读 files_to_read，在项目里乱翻**：implementer 拿到 P2 的 files_to_read 清单后应按清单阅读，不要在项目里全文搜索或整目录全读——上下文会爆炸
2. **自行加范围外改动**：发现需要做但不在 P1 范围内的改动 → 标 [SCOPE+]（行首声明格式）而非直接做
3. **只跑单元测试不验证集成**：单元测试全绿 ≠ 功能可用。P5 会跑 gate_commands 做技术验证，但要确保实现时路径依赖的端点行为已验证
4. **先更新 .state.yaml 再 commit**：state 和产出在同一 commit 里——不要先 commit 产出再单独 commit state
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P5 验证依赖：P5 跑 gate_commands.P5 的命令（在 P2 声明），确保你的实现能通过
- P6 验收依赖：实现路径的端点行为必须可验证（确认 API 返回正确的 Content-Type、状态码等）
- 代码改动文件路径：P8 发布时确认版本文件变更需要知道你改动了哪些 package

> 完成 → 读 phase-cards/P5-verification.md

6. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0005-0009`；协议 v0.44.0 基线；714 bats 全绿（P3 前）；P1/P2/P3 已 commit
- 测试命令：`bats agate/tests/unit/agate-gate-p5-count.bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-render-dispatch-prompt.bats agate/tests/unit/agate-debt-check.bats`（P2 gate_commands.P3）
- 变更文件清单（P4 后 commit 范围）：agate/scripts/*.py/.sh、agate/*.md、agate/rules/*、agate/phase-cards/*、agate/assets/templates/*、agate/tests/README.md、agate/scripts/README.md → 触发 SELF-GATE（commit message 需 self-gate-review 标记）
- RM-AG0012② 已修复（exit 2），RP.17 应天然绿
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
