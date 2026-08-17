---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0006
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
修复 P4 双评审（design-review + review）发现的 gate 脚本缺陷，使实现通过复审。

### 约束
1. **BLOCKER/CRITICAL 级必修（2 项，双评审一致确认）**：
   - **B1（check-p6-provenance.py:322）**：GAP 分支 `sys.exit(0)` 在审计 4 后立即整脚本退出，跳过了审计 5（日志 EXIT_CODE 一致性）、审计 6（evidence JSON 一致性）与协作规范 agent 字段检查——这些是 exit 1 硬检查，被静默跳过。修复：GAP 分支**不要整体 sys.exit(0)**，只跳过"vision YAML 强制 + blocker_count"子块（作为 is_gap 开关），随后继续执行审计 5/6 与协作规范检查，镜像 available 分支结构。
   - **B2（check-p6-evidence.py:340-343 + agate-image-check.py:50-52）**：avg-hash `zip(sorted(glob), ahash_lines)` 对齐缺陷——agate-image-check 对非图片/损坏图 `contextlib.suppress` 吞错不打印行，导致 ahash_lines 行数 < 文件数 → 哈希错位。修复：统一过滤口径——check-p6-evidence 只对图片文件（`_is_image`）收集 `ordered` 与 ahash_lines 对齐；或让 agate-image-check 对非图片也输出占位行；确保行数与文件名一一对应。**补一条含 >1KB 非图片文件的回归测试**（混入 .log 后真重复对仍正确分组）。
2. **MEDIUM/INFO 级落实（评审建议）**：
   - **M1（check-p6-provenance.py）**：同上 B1，GAP 分支修复后确认非 vision 审计不再被跳过。
   - **I1（check-gate.py _gate_p2_ui_design_section，backend INFO-1）**：布局/交互/视觉三锚点豁免当前"任一维度声明不适用 → 全部豁免"过宽。改为按维度粒度豁免（分别匹配"布局不适用/交互不适用/视觉不适用"），与 P2 §2.3"维度不适用显式声明即可豁免该维度"语义一致。
   - **I2（check-gate.py _gate_p2_ui_design_section，backend INFO-2）**：节标题正则 `^#{2,3}\s+UI 设计\s*$` 要求精确结尾，放宽为前缀匹配（`^#{2,3}\s+UI 设计`）防漂移误拦。
3. **不修改测试断言语义**：只修实现（脚本），不改 P3 测试（测试是契约）。新增回归测试除外（B2 需要补新的含非图片文件测试）。
4. **TDD 纪律**：先确认现有测试仍红/绿状态，改完自跑全量相关测试确认绿灯，不引入回归。
5. **平台无关原则**：修复不引入 Unix 假设。
6. **只修 P4 已做文件的缺陷**：聚焦 check-p6-provenance.py / check-p6-evidence.py / check-gate.py；不扩散到其他已通过审查的改动。
7. **DEBT0006 已登记**：B2 的修复即建立该重构（ahash 计算收敛），可同时闭合。

### 上游关联
- design-review（P4-review-design.md）needs-revision：4.1 BLOCKER（GAP 短路审计 5/6）+ 4.2 MEDIUM（avg-hash zip 错位）。
- review（P4-review-backend.md）rejected：CRITICAL-1（avg-hash zip 对齐）+ MEDIUM-1（GAP 早退短路）+ INFO-1/2。
- 双评审其余项全通过（P1/P2 gate 逻辑、GAP 降级、证据按形态、形态一致性、公共 helper、schema、consistency CHECK 11、测试健康）。
- 全量基线：876 passed + 2 skipped；consistency 0 ERROR；count-tests 878。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P4-review-backend.md（CRITICAL-1/MEDIUM-1/INFO-1/2 详情）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P4-review-design.md（BLOCKER/MEDIUM 详情）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P4-implementation.md（实现记录）
- {AGATE_WORKSPACE}/tasks/TAG0006-ui-ux-quality/P2-design.md（设计方案：§2.13 BDD-14 雷同判定 / §2.8-2.9 BDD-9 GAP 分档 / §2.3 gate 逻辑）
- {project_root}/agate/scripts/check-p6-provenance.py（修复对象）
- {project_root}/agate/scripts/check-p6-evidence.py（修复对象）
- {project_root}/agate/scripts/check-gate.py（修复对象）
- {project_root}/agate/scripts/agate-image-check.py、agate_common.py（参考/可能修改）
- {project_root}/agate/tests/unit/test_check_p6_evidence.py、test_check_p6_provenance.py、test_check_gate.py（补回归测试）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.py 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.py P4（确认暂存区有代码文件）
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
- [ ] check-tdd-red.py 确认红灯（测试先于实现）
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
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.py 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

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

## gate 规则（check-gate.py 会跑）

```bash
check-gate.py P4 $TASK_DIR
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
- 修复对象：check-p6-provenance.py（GAP 分支 sys.exit(0) 短路）、check-p6-evidence.py（avg-hash zip 错位）、check-gate.py（layout 豁免过宽 + 节标题正则）。
- 双评审确认：B1（GAP 短路审计 5/6，exit 1 硬检查被跳过）+ B2（zip 对齐错位，非图片 suppress）。
- 全量基线：876 passed + 2 skipped；consistency 0 ERROR；count-tests 878。
- DEBT0006 已登记（ahash zip 脆性重构）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。