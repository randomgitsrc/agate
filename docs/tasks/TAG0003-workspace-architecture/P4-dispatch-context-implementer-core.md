---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0003
role: implementer-core
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
实现 TAG0003 工作区架构的**核心脚本**：新增 `agate-workspace-resolve.sh`（工作区路径单点解析器）+ `agate-migrate-workspace.sh`（强制迁移工具），改造 `pre-commit-gate.sh` / `ci-gate-backstop.py` / `check-state-transition.sh` / `check-pruning.sh`。让 P3 的红灯测试（agate-workspace-resolve.bats / agate-migrate-workspace.bats / check-state-transition.bats 新增用例）变绿。

### 约束
- 本任务是 **agate 协议自身改造**（dogfooding）：只改 worktree 的 `agate/`，**禁止改动 `~/.agate`**（稳定版 v0.40.2 开发工具）。测试用 worktree 本体（load.bash 反推 AGATE_ROOT）。
- **只改本角色文件集**（核心脚本），不改文档、不改既有测试 fixture（那是另外两个并行 implementer 的活）：
  - 新增：`agate/scripts/agate-workspace-resolve.sh`、`agate/scripts/agate-migrate-workspace.sh`
  - 改造：`agate/scripts/pre-commit-gate.sh`、`agate/scripts/ci-gate-backstop.py`、`agate/scripts/check-state-transition.sh`、`agate/scripts/check-pruning.sh`
- 实现严格按 P2-design.md（方案 A）：
  - **解析器**（§3.1）：解析优先级 `.agate.env` 显式配置（`AGATE_WORKSPACE=`，相对路径相对项目根解析/绝对路径原样/可含空格）> 环境变量 `AGATE_TASKS_DIR`（向后兼容，允许直接指定 tasks 目录）> 默认 `{project_root}/agate-workspace`；输出 `AGATE_WORKSPACE` + `AGATE_TASKS_DIR`（均绝对路径）。脚本可被 bash source 复用 + 被 python subprocess 调用（输出两行 `AGATE_WORKSPACE=...` / `AGATE_TASKS_DIR=...`）。边界：无 .agate.env 不报错走默认（BDD-4）；含空格全程引号 + `realpath -m`（BDD-5）；解析器不创建目录（BDD-3）。
  - **迁移工具**（§3.2）：源检测（docs/tasks 不存在或空 → no-op exit 0，空目录 rmdir 清理，BDD-19）→ 目标冲突检测（工作区 tasks 已存在非空 → exit 1 防覆盖）→ 目录级 `git mv docs/tasks {workspace}/tasks`（git mv 失败 exit 128 → fallback `mv` + WARNING 标注外部工作区限制）→ 归档迁移（`docs/archived/` → `{workspace}/archived/`，BDD-18）→ 幂等（重复运行 no-op，BDD-9）→ 迁移后校验（清单对照 + 摘要）→ 可选写 .agate.env。
  - **pre-commit-gate.sh**（§3.1 消费方）：L27 `AGATE_TASKS_DIR` 默认值改为 source 解析器获取（替换 L27/L83）；保持任务级/根级 TASK_DIR 分支语义；**注意**：解析器输出绝对路径时，L83 不得再拼 `REPO_ROOT/` 前缀（P2-review 非阻塞项 2）。
  - **ci-gate-backstop.py**（§3.1 消费方）：L86 tasks_base 解析点改为 subprocess 调解析脚本，与 bash 侧共用。
  - **check-state-transition.sh**（§3.6 去硬编码）：`get_old_phase()` 的 `grep -qE 'docs/tasks/[^/]+/'` 改为 `dirname($STATE_FILE) != REPO_ROOT` 语义（与 pre-commit-gate.sh L82 同构）。
  - **check-pruning.sh**（SCOPE+ #2）：L66 排除模式 `grep -cvE '^docs/tasks/|\.state\.yaml$|...'` 改为工作区 tasks 相对路径。
- **自查≠gate**：写完代码自跑相关测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。不要声称"P5 已过"。
- 实现中发现 P2 设计歧义/缺口 → 标 `[DESIGN_GAP: 描述]`（单行 tag）；发现 P1/P2 都没覆盖的必须做的事 → 标 `[SCOPE+]`；发现 prompt 漏了 P2 已声明的事 → 标 `[SCOPE_GAP]`。
- 遵守 AGENTS.md 脚本约定：`set -euo pipefail`、`git diff --cached`、`grep -c || echo 0` 后 `| tail -1`、`printf '%b'`、Python 用 os.environ、紧凑输出。
- 禁止行首 `- PASS` / `- FAIL` 格式（provenance 审计拦截）。

### 上游关联
- P3 红灯测试（本次要变绿的）：`agate/tests/unit/agate-workspace-resolve.bats`（9 用例：解析优先级/空格路径/外部路径）、`agate/tests/unit/agate-migrate-workspace.bats`（8 用例：迁移/幂等/空源/归档）、`agate/tests/unit/check-state-transition.bats`（新增 ST_WS.1-4：去硬编码语义）。
- P2 已批准（plan-eng-review approved）：方案 A；gate_commands.P3 = `bats --formatter tap agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/agate-migrate-workspace.bats agate/tests/unit/check-state-transition.bats`。
- 3 项 SCOPE+ 已回补 P1 scope_resolved（check-state-transition.sh / check-pruning.sh 去硬编码 + worktree 自身不迁移）。

### 输入文件
- docs/tasks/TAG0003-workspace-architecture/P2-design.md（方案设计 §3.1/3.2/3.6 + files_to_read——**必读**）
- docs/tasks/TAG0003-workspace-architecture/P3-test-cases.md（测试契约——必读，实现目标）
- agate/tests/unit/agate-workspace-resolve.bats + agate-migrate-workspace.bats + check-state-transition.bats（测试代码——必读，理解预期行为）
- docs/tasks/TAG0003-workspace-architecture/P0-brief.md（环境约束——必读）
- AGENTS.md（脚本约定/测试约定——必读）
- 按 P2-design.md files_to_read 读取现有脚本（pre-commit-gate.sh / ci-gate-backstop.py / check-state-transition.sh / check-pruning.sh / tests/helpers/fixtures.bash）
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
- 环境状态：worktree 是改造对象（分支 dev/workspace，HEAD=80c30d5=P3 commit）；`~/.agate` → 主 checkout 是稳定版 v0.40.2 开发工具（禁止改动）。
- 版本隔离三条铁律：改协议只改 worktree 的 `agate/`；跑 gate/读卡片用 `~/.agate`（原版规则）；跑测试用 worktree 本体（load.bash 反推 AGATE_ROOT 到 worktree）。
- 已核实查证：pre-commit-gate.sh L27 `AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"`、L82-86 根级/任务级 TASK_DIR 分支；ci-gate-backstop.py L86 tasks_base 解析点；check-state-transition.sh L28 `grep -qE 'docs/tasks/[^/]+/'`；check-pruning.sh L66 排除模式。
- P3 测试已确认红灯（check-tdd-red exit 0）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
