---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0017-toolchain-fixes
role: review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。单评审角色（domains=[protocol-docs, gate-scripts] 视同 backend 性质，按 C8 映射机械触发 `review`），直接产出 P4-review.md，无需组长汇总。

### 目标
对 P4 实现（5 个并行批次，14 个改动文件）做上线前最后一道评审：找一切可能在生产/后续任务中出问题的东西。

### 约束
1. **本任务性质特殊**：改动对象是 agate 协议自身（gate 判定脚本 + git hook 薄壳 + 协议 Markdown 文档），不是常规业务后端代码——传统"SQL 注入/竞态条件"类 CRITICAL 检查项大部分不适用，请把 Pass 1/Pass 2 的检查精神迁移到本任务语境：
   - **Read-Check-Write 竞态** → 关注 3 个 hook 薄壳的探测逻辑是否有类似的检查-使用不一致（如 `command -v` 命中后到实际 exec 之间环境是否可能变化）
   - **Enum/状态值新增后消费方是否都处理** → 关注 `is_gate_meta_key` 新增后是否所有原本判断 `_formatter` 后缀的地方都已切换、有无遗漏
   - **TOCTOU** → 关注新增的可执行性小测试（`"$c" -c "" >/dev/null 2>&1`）与随后的 `exec "$PY"` 之间是否存在竞态窗口
   - **资源泄漏/错误被吞掉** → 关注 `check-protocol-consistency.py` 新增 `--strict-errors-only` 分支是否正确处理所有 Report 状态组合，没有吞掉 ERROR 场景
2. **重点核查同类扫描/影响面梳理声明的完整性**：P1/P2 反复强调"5 条 issue 域重叠、按文件→改动归并、避免同一文件被两批各改一次"——请核实最终实现是否真的做到了这一点（可用 `git diff --stat` 核对改动文件清单是否与 P2 §6 dispatch_plan 声明的 5 批文件边界一致，无遗漏无越界）。
3. **核查 DEBT0010 修复没有放宽 TDD 红灯判定语义**（P1 R3 风险，BDD-2 核心要求）：`is_gate_meta_key` 是否严格只匹配 `_formatter`/`_timeout_seconds` 两个后缀，有没有可能被写成更宽泛的匹配从而误伤真实红灯判定。
4. **核查 Windows 相关改动的诚实性边界**：`platform-notes.md`/`AGENTS.md` 新增文字是否真的没有"已在 Windows 实测通过"类断言（P0-brief 约束 3 硬性要求）。
5. **核查 3 个 hook 薄壳改动是否逐字一致**：这是 P2 §1.3 R5 明确要求的一致性约束（3 文件必须同步，不能只改 1-2 个）。

### 上游关联
5 个并行 P4 implementer 批次全部完成，无任何 `[DESIGN_GAP]`/`[SCOPE+]`/`[CLARIFY]` 标记。主 Agent 已独立验证：全量 `python3 -m pytest agate/tests/` → 1011 passed, 2 skipped, 0 failed；`ruff check agate/` 全绿；`shellcheck -S warning` 3 个 hook 全绿；3 个 hook 薄壳探测循环片段逐字比对（`awk` 精确锚点提取）确认完全一致。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P2-design.md（方案设计全文，尤其 §1 影响面梳理 + §2 候选方案选择理由 + §6 dispatch_plan 批次边界）
- {AGATE_WORKSPACE}/tasks/TAG0017-toolchain-fixes/P1-requirements.md（BDD-1~12 验收条件原文）
- 改动文件（`git diff HEAD` 可看到全部改动，或按下方清单逐个读取）：
  - agate/scripts/agate_common.py（新增 `is_gate_meta_key`）
  - agate/scripts/agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py / agate-read-p5-commands.py（改用共享判据）
  - agate/scripts/check-protocol-consistency.py（新增 `--strict-errors-only`）
  - agate/scripts/pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh（探测循环增强）
  - agate/phase-cards/P2-design.md / agate/assets/execution-roles/architect.md / agate/phase-cards/P4-implementation.md（env_constraints 边界 + --strict 反模式指引 + dist 提醒文档）
  - SELF-GATE.md / agate/assets/review-roles/protocol-alignment-review.md（命名模板 + 写入前检查）
  - agate/platform-notes.md / AGENTS.md（Windows 已知限制文档）
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
- 独立核验（主 Agent 已做）：全量 pytest 1011 passed / 0 failed；ruff 全绿；shellcheck 全绿；3 hook 探测循环片段逐字一致；`check-platform-assumptions.py agate/` 的若干命中经核实均为改动范围之外的历史遗留代码（未被本任务改动的行），非本次引入的回归
</objective_info>
