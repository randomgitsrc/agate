---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）
> 本文件是**批次 0** 派发（P2 表 E 批次 0 — 公共库）。后续批次（1-4）由主 Agent 在批次 0 验证通过后另行派发。**本次只做批次 0，不做其他批次。**

### 目标
实现批次 0：新建 `agate/scripts/agate_common.py`（替代 gate-result.sh + agate-workspace-resolve.sh 的函数库）+ 同步改 `agate/scripts/ci-gate-backstop.py`（resolve_tasks_dir 改调 agate_common.resolve_workspace）+ 对应 bats 测试调用方式改造。同时更新 P4-implementation.md（声明 implementation_dir + 本批次改动）。

### 约束（从 P2-design.md 提取，必须遵守）
- **批次 0 范围（P2 §3.2 批次 0，评审 BLOCKER-2 修订后）**：
  - `agate_common.py`：按 P2 §3.1 模块设计实现——数据流函数（write_gate_result / read_state_phase / read_state_task_id / has_staged_phase_change / has_staged_phase_output / resolve_formatter / run_test_with_formatter）+ 工作区解析函数（resolve_workspace + 执行模式 main 两行输出）+ hook 公共工具（resolve_agate_root / probe_python / run_git）
  - `ci-gate-backstop.py`：只改 `resolve_tasks_dir` 改调 `agate_common.resolve_workspace`（消除对 agate-workspace-resolve.sh 的 bash subprocess）；**`_bash_cmd`/`_find_bash` 保留不动**（批次 2 随各被调脚本 py 化才删）；`run_gate` 的 check-gate.sh → check-gate.py 切换**不做**（批次 2）
  - 对应 bats 改造：`unit/agate-workspace-resolve.bats`（10 处调用改 py）、`unit/helpers-python.bats`（3，重构为 py 探测/失败回退语义）、`unit/ci-gate-backstop.bats`（workspace 解析相关断言改后绿）
- **编码规范**：所有 py 显式 `encoding="utf-8"`；Python 3.8+（禁 match/str.removeprefix）；pyyaml 缺失 fail-closed（同 agate-state-get.py L18-21 模式）
- **CLI 契约不变**：`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出（bats 直调契约）；`GATE ...:` 前缀；exit 0/1/2 语义
- **bats 调用约定**：`bash "$AGATE_SCRIPTS/x.sh"` → `"$PYTHON" "$AGATE_SCRIPTS/x.py"`（复用 fixtures.bash 的 $PYTHON detect_python）
- **count-tests 口径**：用例数不减少（727 基线）
- **agate_common.py 只收 ≥2 处使用的函数**；单点工具函数留各自脚本内（P2 §1 方案 A 边界）
- 最小实现原则：只做批次 0，不加额外功能、不重构无关代码
- 自查≠gate：写完后自跑 bats 确认基本功能，但不要声称"P5 已过"
- 不写行首 `- PASS`/`- FAIL` 格式

### 上游关联
- P2-design.md 已 approved：§3.1 agate_common.py 模块设计（函数签名/语义）、§3.2 批次 0、§3.6 bats 断言改动（helpers-python / agate-workspace-resolve / ci-gate-backstop）
- P3-test-cases.md：批次 0 验证 = agate-workspace-resolve.bats(10) + helpers-python.bats(3) + ci-gate-backstop.bats(11) + 全量 bats

### 输入文件（按 P2 files_to_read + 本批需要）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-design.md（§3.1 agate_common.py 设计——本批核心依据）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P3-test-cases.md（批次 0 验证口径）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（env_constraints）
- {project_root}/agate/scripts/gate-result.sh（数据流函数迁移源——全读）
- {project_root}/agate/scripts/agate-workspace-resolve.sh（工作区解析函数迁移源——全读）
- {project_root}/agate/scripts/ci-gate-backstop.py（resolve_tasks_dir 改造点——读相关片段）
- {project_root}/agate/scripts/agate-state-get.py（read_state_phase 语义——pyyaml 模式参考）
- {project_root}/agate/tests/helpers/fixtures.bash（$PYTHON detect_python 约定）
- {project_root}/agate/tests/unit/agate-workspace-resolve.bats（10 用例改造点）
- {project_root}/agate/tests/unit/helpers-python.bats（3 用例重构点）
- {project_root}/agate/tests/unit/ci-gate-backstop.bats（11 用例改造点）
- {project_root}/AGENTS.md（脚本约定：编码/超时/测试约定）

### 产出要求
- 新建 `agate/scripts/agate_common.py`（批次 0 核心产出）
- 修改 `agate/scripts/ci-gate-backstop.py`（resolve_tasks_dir 改调）
- 修改 3 个 bats 文件（调用方式 + 断言改造）
- 更新 `{AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P4-implementation.md`（声明 implementation_dir: agate/scripts/ + 本批次改动清单；若文件不存在则创建，Header: phase: P4 / task_id: TAG0010-python-migration / type: implementation / parent: P3-test-cases.md / trace_id: TAG0010-P4-20260814 / status: draft / agent: implementer）
- 若实现中发现 P2 设计歧义/缺口 → 标 `[DESIGN_GAP: 描述]`（独立成行）；发现新隐含需求 → 标 `[SCOPE+]`
- 自查：跑 `bats agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/helpers-python.bats agate/tests/unit/ci-gate-backstop.bats` 确认基本功能

### 门槛（什么算完成）
- agate_common.py 存在且非空（含 write_gate_result / resolve_workspace / probe_python 等核心函数）
- ci-gate-backstop.py resolve_tasks_dir 已改调 agate_common.resolve_workspace
- 3 个 bats 文件调用方式已改 py
- P4-implementation.md 存在且含 implementation_dir 声明
- 自跑 3 个 bats 文件基本通过（自查）
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
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3（~/.venvs/agate-dev/bin/python）；bats 1.10.0；ruff 0.16.3
- 测试基线：733 bats 全绿（58 文件/727 @test）+ consistency 0 ERROR（--strict）
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动！gate/hook 用 ~/.agate）
- bash 命令一律加 timeout、单步串行（AGENTS.md 工具纪律）
- 测试命令：`timeout 120 bats agate/tests/unit/agate-workspace-resolve.bats ...`（或全量 `timeout 300 bats agate/tests/unit/`）
</objective_info>
