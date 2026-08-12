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

C8 门槛评审（`docs/tasks/T001-v2.0-structured/P4-review.md`）对 P4 全部实现返回 `status: rejected`，发现 1 个 CRITICAL + 4 个 INFO。主 Agent 已独立复现 CRITICAL（不是评审角色误报）。本次派发修复 CRITICAL + 2 个低风险 INFO，其余 2 个 INFO 明确不在本次范围。

### 目标

修复 `docs/tasks/T001-v2.0-structured/P4-review.md` 里的 CRITICAL 发现（`agate-frontmatter-check.py` 对非 `yaml.YAMLError` 异常无兜底，导致校验器崩溃时被 `check-frontmatter.sh` 的 `2>/dev/null || true` 静默吞掉，端到端表现为"应报错的坏格式被放行"），以及 2 个低风险 INFO。修完后需要重新过 review。

### 约束

1. **必须修的 CRITICAL**（P4-review.md Pass 1 完整描述 + 复现步骤，先读那一节）：
   - `agate/scripts/agate-frontmatter-check.py`：给 `yaml.safe_load(block)` 增加 `RecursionError` 捕获（`RecursionError` 不是 `yaml.YAMLError` 子类，独立 except 分支）；`_check()` 调用及其内部 `_value_depth()` 的无保护递归也要纳入同一层防护；`open(file_path, encoding="utf-8")` 遇到非 UTF-8 内容抛的 `UnicodeDecodeError` 也一并兜住。**建议做法**：把 `main()` 里"读文件之后"的全部逻辑包一层 `try: ... except Exception as e: print(...); return`，任何未预见异常都转成一行错误输出打到 stdout，而不是让异常穿透。错误信息格式参考现有 `print(str(e))` 风格，前缀带文件名（如 `"{}: frontmatter 处理异常（{}）".format(basename, e)`）。
   - `agate/scripts/check-frontmatter.sh`：**同时做纵深防御（Fix B，review 建议"A+B 都做"）**——不要用 `python3 ... 2>/dev/null || true` 把 stderr 和非零 exit code 一起吞掉。改为区分"python 正常退出（exit 0）但 stdout 为空"（真的没错误，应 exit 0）与"python 非零退出"（脚本自己崩了，fail-closed，应 exit 1，且把 stderr 内容打印出来方便排查，不要吞掉）两种情况。
   - **验证要求**：修完后必须重跑 review 报告里给的复现步骤（P4-review.md 第 44-63 行的 3 段 bash），确认深嵌套场景现在 exit 1（而不是 0）。
2. **一并修的 2 个低风险 INFO**：
   - `agate/scripts/agate-md-field-get.py`（约第 123-124 行）：`_format_value` 的 bool 分支死代码——`if isinstance(value, bool) else` 两个分支返回值相同，简化为 `return str(value).lower()`。纯重构，不改变行为，改完跑一遍 `agate-md-field-get.bats` 确认仍全绿。
   - `agate/scripts/check-gate.sh`（约第 23、47 行）：NEED_CONFIRM/SUGGEST 已解决匹配从 `grep -qF`（子串匹配）改 `grep -qFx`（整行精确匹配）。**这处改动有回归风险，必须验证**：改完后跑 `bats agate/tests/unit/check-gate.bats agate/tests/unit/check-retrospective.bats agate/tests/unit/check-gate-p1-review.bats` 确认全绿；如果发现现有某条测试的 fixture 确实依赖"子串匹配"语义（比如已解决描述是未解决描述的父串这种测试场景），说明这个 INFO 的 fix 建议和现有测试设计有冲突，**不要为了让测试通过而改测试**，标 `[DESIGN_GAP]` 报告，保留原有子串匹配行为，不要强行应用这条 INFO 修复。
3. **本次明确不做的 2 个 INFO**（review 报告里也明确说了"不属于本次 CRITICAL"/"不是本次 diff 的代码缺陷"）：
   - `check-changelog.sh` 分隔符集合扩展（review 明确标注"不属于本次 CRITICAL，可与其他 INFO 一起排期"）——不在本次范围，不要碰这个文件。
   - 流 D 硬切上线迁移计划（review 明确标注"不是本角色评审范围"，是给主 Agent 的提醒，不是代码修复项）——这是主 Agent 在 P7/P8 阶段要考虑的事，不是你本次要做的。
4. **范围锁定**：本次只允许改 `agate/scripts/agate-frontmatter-check.py`、`agate/scripts/check-frontmatter.sh`、`agate/scripts/agate-md-field-get.py`、`agate/scripts/check-gate.sh` 这 4 个文件。不碰其他任何文件（含 `agate/tests/**`——测试不动，只用来验证）。
5. **验收标准**：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats
   ```
   修复后应仍是 **600/600 全绿**（本次修复不改变任何测试预期行为，纯粹是补异常处理 + 死代码清理 + 收紧一处匹配逻辑）；`count-tests.sh` 仍是 594；另外手动验证 CRITICAL 复现步骤（约束 1 末尾）确认从 exit 0 变成 exit 1。
6. **自查用命令**：约束 5 的完整命令 + 手动跑一次 CRITICAL 复现（P4-review.md 第 46-63 行）。这不是最终 gate，我会独立重跑验证。
7. **生产环境隔离**：不适用。
8. **更新 `docs/tasks/T001-v2.0-structured/P4-implementation.md`**：在文件末尾追加一个"## Review 修复"小节（追加，不改动已有的流 A/B/C/D 小节），简述本次修了什么、对应 review 报告哪几条。如果 INFO #2（check-gate.sh 子串匹配收紧）因为约束 2 提到的冲突而未应用，在这里说明并附 `[DESIGN_GAP:]` 标记。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P4-review.md` 是本次修复的直接依据，Pass 1 CRITICAL 一节有完整问题描述+实测复现+建议 fix（A+B）。
- 修复完成后，主 Agent 会重新派发 review 角色复审，`status: approved` 后才能推进到 P5。

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义）
- `docs/tasks/T001-v2.0-structured/P4-review.md`（本次修复依据，完整读一遍，尤其 Pass 1 和 Pass 2 前两条 INFO）
- `agate/scripts/agate-frontmatter-check.py`（当前状态）
- `agate/scripts/check-frontmatter.sh`（当前状态）
- `agate/scripts/agate-md-field-get.py`（当前状态，约 120-130 行附近）
- `agate/scripts/check-gate.sh`（当前状态，约 20-50 行附近，NEED_CONFIRM/SUGGEST 分支）
- `agate/tests/unit/check-gate.bats`、`agate/tests/unit/check-retrospective.bats`、`agate/tests/unit/check-gate-p1-review.bats`（验证 INFO #2 改动无回归用）
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
- 环境状态：worktree `feat/v2.0`，HEAD 68e4173（P4 fixture修复完成后）。`P4-review.md` 已产出，status: rejected，agent: review。
- 主 Agent 已独立复现 CRITICAL：`python3 -c "depth=2000; yaml.safe_load('['*depth+'1'+']'*depth)"` 抛 `RecursionError`（非 `yaml.YAMLError` 子类）；端到端构造深嵌套 `risk_level` 的 P1-requirements.md fixture，`bash agate/scripts/check-frontmatter.sh` 返回 exit 0（应为非 0）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
