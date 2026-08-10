> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: review
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 背景：这是复审，不是初审

上一轮 review（`docs/tasks/T001-v2.0-structured/P4-review.md`，commit `e566303` 之前的版本，可用 `git log -p --follow -- docs/tasks/T001-v2.0-structured/P4-review.md` 查看历史版本）给出 `status: rejected`：1 个 CRITICAL（`agate-frontmatter-check.py` 异常处理不完整导致坏格式静默放行）+ 4 个 INFO。implementer 已在 commit `e566303` 修复 CRITICAL + 2 个低风险 INFO（`agate-md-field-get.py` 死代码清理、`check-gate.sh` 子串改精确匹配），另 2 个 INFO 明确未处理（review 报告里已注明"不属于本次 CRITICAL"）。主 Agent 已独立复现验证 CRITICAL 确实修复（复现步骤从 exit 0 变成 exit 1）。

### 目标

复审 `commit e566303` 里对 CRITICAL 和 2 个 INFO 的修复质量，判定是否可以 `status: approved`。**不是重新从头审查整个 P4 diff**——上一轮已审过的其余代码（除本次改动的 4 个文件外）不需要重新过一遍，除非你怀疑本次改动引入了新问题。

### 约束

1. **审查范围**：`git diff 68e4173..e566303 -- agate/scripts/`（这是本次修复的具体 diff，4 个文件：`agate-frontmatter-check.py`/`check-frontmatter.sh`/`agate-md-field-get.py`/`check-gate.sh`）。
2. **核对 CRITICAL 是否真的修复**：
   - 读修复后的 `agate-frontmatter-check.py`，确认 `try/except Exception` 的包裹范围是否完整覆盖了原来会崩溃的路径（`yaml.safe_load`、`_check()`、`_value_depth()` 递归）
   - 读修复后的 `check-frontmatter.sh`，确认 Fix B（python 非零退出 → fail-closed exit 1）逻辑正确
   - **自己重新跑一遍复现步骤**（不要只信主 Agent 或 implementer 的自述）：构造一个深嵌套 `risk_level` 字段的 P1-requirements.md fixture（参考 `P4-review.md` 历史版本里 Pass 1 CRITICAL 一节给的具体构造代码），确认 `bash agate/scripts/check-frontmatter.sh` 现在返回非 0（拦截），而不是之前的 0（放行）
   - **额外检查**：`try/except Exception` 这种宽泛捕获本身是否可能引入新问题（比如吞掉本应该让 pre-commit 硬失败的严重系统错误、比如捕获了 `KeyboardInterrupt`/`SystemExit` 这类不该被 `except Exception` 捕获但也不该被吞掉的信号——虽然 Python 里 `Exception` 基类本就不包括 `KeyboardInterrupt`/`SystemExit`，这两个是 `BaseException` 的直接子类，正常情况下 `except Exception` 不会误捕，但请确认代码里没有更宽泛地写成 `except:` 裸捕获）
3. **核对 2 个 INFO 修复质量**：
   - `agate-md-field-get.py` 死代码清理：确认纯重构无行为变化（`agate-md-field-get.bats` 应无回归）
   - `check-gate.sh` 子串改精确匹配（`grep -qF` → `grep -qFx`）：确认这个改动没有破坏 NEED_CONFIRM/SUGGEST 的正常判定逻辑，且 implementer 报告"未发现回归、无需 DESIGN_GAP"这个结论是否可信（自己简单验证一下 `check-gate.bats`/`check-retrospective.bats`/`check-gate-p1-review.bats` 相关用例，不需要全量重跑，可以直接看这几个文件是否有 not ok）
4. **不需要重新审查的**：上一轮已经过审、本次未改动的其余代码（P6/P7 结构化、P1 标记结构化、任务编号硬切等），以及 2 个本次明确未处理的 INFO（`check-changelog.sh` 分隔符集合、流 D 上线迁移计划）——这两个不是本次修复范围，不影响本次 approve/reject 判定。
5. **测试基线**：`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats` 应为 600/600；`count-tests.sh` 应为 594；这些主 Agent 已独立验证过，你可以信这个结论，重点放在代码审查本身。
6. **产出规则**：只描述"怎么改"，不直接改代码；本轮如果发现 CRITICAL 确已妥善修复且无新引入的问题 → `status: approved`；如果修复不彻底或引入新 CRITICAL → `status: rejected`（并具体说明还差什么）。
7. **产出文件**：**覆盖写** `docs/tasks/T001-v2.0-structured/P4-review.md`（不是新建文件，是更新同一个文件到最新结论——之前的 rejected 版本已经在 git 历史里保留，不需要额外备份）。Header 含 `agent: review` + `status` 字段。

### 上游关联

- 上一轮 review 报告（git 历史里的 `P4-review.md` 旧版本）是本次复审的对照基线。
- `docs/tasks/T001-v2.0-structured/P4-implementation.md` 的"## Review 修复"小节是 implementer 对本次修复的说明记录。

### 输入文件（自己读）

- `agate/assets/review-roles/review.md`（你的角色定义）
- `git log -p -1 e566303 -- agate/scripts/` 或 `git diff 68e4173..e566303 -- agate/scripts/`（本次修复的具体 diff）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`"## Review 修复"小节
- `git show 68e4173:docs/tasks/T001-v2.0-structured/P4-review.md`（上一轮 review 报告原文，用这个命令读历史版本，因为工作区里的 P4-review.md 已经是待你覆盖的文件）
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
- 环境状态：worktree `feat/v2.0`，HEAD `e566303`（review 修复已 commit）。
- 主 Agent 已独立验证：CRITICAL 复现步骤从 exit 0 变成 exit 1（错误信息可见）；全量 bats 600/600；count-tests.sh = 594；check-protocol-consistency.py 0 ERROR；shellcheck -S warning 两个改动脚本干净；git diff 逐处核对改动范围严格限于 4 个允许文件。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
