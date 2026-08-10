> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 背景

`docs/reviews/agate-alignment-review-2026-08-10.md`（self-gate 语义审查）给出 4 个 `MISALIGNED`（均为文档滞后，不影响任何已验证的 gate 行为，纯文档修复）。按 SELF-GATE.md 闭环规则"MISALIGNED → 必须修复"，本次定向修复这 4 处。

### 目标

修复 self-gate 报告里的 4 个 MISALIGNED 文档项，均为纯文本编辑，不涉及任何脚本逻辑改动。

### 约束

1. **只改这 4 处**（每处的精确位置和期望内容见 self-gate 报告"待闭环事项清单"表，先读那张表）：
   - `agate/scripts/README.md:68`：`agate-md-field-get.py` 的工具清单行需反映双读语义 + 完整 op 清单（当前只写"P1/P2 提取 risk_level/ui_affected/phases"，需更新为反映流A/B/C 新增的全部 op：candidate_count/packages/domains/override/internal_only/internal_only_reason/跳过风险/design_trivial/follows_existing_pattern/pass/fail/blocker_count/deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count/need_confirm_resolved/suggest_resolved/scope_resolved，共 17 个新增 op + 原有 3 个）。不需要逐字列全部 op 名（会很长），可以概括描述"frontmatter 双读 + N 个字段 op（详见脚本内 docstring）"这种写法，只要不再是过时的"仅 risk_level/ui_affected/phases"描述即可。
   - `agate/WORKFLOW.md:78-79`：任务目录命名示例 `docs/tasks/T001-mcp-namespace-map/` / `docs/tasks/T002-fix-db-migration/` 改为符合流 D 新编号规则的示例（如 `docs/tasks/TAG0001-mcp-namespace-map/` / `docs/tasks/TAG0002-fix-db-migration/`）。
   - `agate/dispatch-protocol.md:537-553`："P5/P6 派发时追加"的派发 prompt 模板块，在提到"每条 BDD 验收结果必须用行首 `- PASS`/`- FAIL` 格式"附近，补一句关于 frontmatter `pass:`/`fail:`/`ui_affected:` 汇总字段的要求（P6-acceptance.md 需要在 frontmatter 声明这三个字段，具体格式参考 `agate/assets/execution-roles/verifier.md` 里已有的样例）。
   - `agate/tests/README.md:28-64`：覆盖度表补一行 `| check-frontmatter.sh | unit/check-frontmatter.bats | 11 |`（放在表格里合适的位置，参考现有行的格式）。
2. **不要碰这 2 处"建议非阻断"项**（self-gate 报告明确标注"不构成 MISALIGNED"）：`agate/CONTEXT.md`、`agate/LIMITATIONS.md`——这两个是可选的完整性建议，不在本次范围。
3. **不要碰任何脚本文件**（`agate/scripts/*.sh`、`agate/scripts/*.py`）——本次只是文档纠偏，不涉及任何逻辑变更。
4. **不要碰 `agate/tests/**`**——只是读 `agate/tests/README.md` 这一个文档文件，不碰实际测试代码。
5. **验收标准**：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   python3 agate/scripts/check-protocol-consistency.py
   ```
   修复后应仍是 0 ERROR（CHECK 1 会重新校验所有 YAML 代码块可解析，若你在文档里加了 YAML 示例要确保语法正确；CHECK 2 会校验文件引用存在，若你加了新的文件路径引用要确保真实存在）。
6. **自查**：改完后跑约束 5 的命令确认 0 ERROR。这不是最终 gate，我会自己独立重跑验证。
7. **生产环境隔离**：不适用。
8. **追加产出 `docs/tasks/T001-v2.0-structured/P4-implementation.md` 的"## Self-gate 文档修复"小节**（追加，不改动已有小节），简述修了这 4 处的哪些内容。

### 上游关联

- `docs/reviews/agate-alignment-review-2026-08-10.md`"待闭环事项清单"表是本次修复的直接依据（4 条 MISALIGNED 行）。

### 输入文件（自己读）

- `docs/reviews/agate-alignment-review-2026-08-10.md`（重点读 A2、A3b、A5 三节的具体差异描述 + 文末"待闭环事项清单"表）
- `agate/scripts/README.md`（约第 68 行）
- `agate/WORKFLOW.md`（约第 78-79 行）
- `agate/dispatch-protocol.md`（约第 537-553 行）
- `agate/tests/README.md`（约第 28-64 行的覆盖度表）
- `agate/assets/execution-roles/verifier.md`（P6 frontmatter 样例参考，用于 dispatch-protocol.md 那处补充内容）
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
5. 更新 .state.yaml phase=P4 → P5
6. git add docs/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
7. git commit -m "wf({Txxx}-P4): {摘要}"

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`docs/tasks/Txxx/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `docs/tasks/Txxx/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。

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
| risk=high | —（plan-eng-review 在 P2 已派）| — |

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
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（无触发评审角色时此项自动满足）
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
- 环境状态：worktree `feat/v2.0`，HEAD `3064734`（P4 review 复审通过后）。
- self-gate 报告：`docs/reviews/agate-alignment-review-2026-08-10.md`，A1/A4/A6 ALIGNED，A2/A3/A5 MISALIGNED（本次要修的 4 项都在这三节里），A7 NEEDS_HUMAN_REVIEW（不在本次范围，另行处理）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
