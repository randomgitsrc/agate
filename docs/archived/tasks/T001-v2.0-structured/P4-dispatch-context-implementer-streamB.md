> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

P4 实现阶段的**第 2 个子派发**（共 4 个，按流 A→B→C→D 串行，流 A 已完成并 commit）。本次只做**流 B**：P6/P7 结果结构化（汇总入 frontmatter + 逐条行格式从严 + P7 状态计数结构化）。流 C/D 后续单独派发，本次不做。

### 约束

1. **范围锁定为流 B，严禁越界改动**。允许改动的文件（且仅这些）：
   - `agate/scripts/agate-md-field-get.py`（在流 A 已有基础上继续追加新 op，不要动流 A 已实现的部分）
   - `agate/scripts/check-gate.sh`（**只改 P6 分支约 236-254 行区域 + P7 分支约 255-298 行区域**——P1/P2 分支流 A 已处理完，不要动）
   - `agate/scripts/check-p6-format.sh`
   - `agate/scripts/check-p6-provenance.sh`（只改审计 3 计数逻辑 + 审计 2 的 dispatch-context 扫描排除范围，其余审计不动）
   - **不改**：`agate/scripts/check-scope-resolved.sh`、`agate/scripts/check-changelog.sh`、`agate/scripts/agate-state-yaml-check.py`（流 C/D 的事）
   - **不改**：`agate/scripts/agate-frontmatter-check.py` / `check-frontmatter.sh`（流 A 已完成，P6/P7 schema 规则已经在里面了，你不需要动这两个文件——除非发现流 A 遗留的 bug，那样标 `[DESIGN_GAP]` 报告，不要直接改）
   - **不改**：`agate/scripts/pre-commit-gate.sh`（流 A 的 2g.2 挂载点已经覆盖 P6-acceptance.md / P7-consistency.md 的 frontmatter 校验扫描，本次不需要新增挂载点）
   - **不改**：模板/角色卡文件（BDD-24 归入流 C，本次不做）
   - **不改**：`agate/tests/**`（测试已由 P3 test-designer 写好并 commit；发现测试有 bug 标 `[SCOPE+]`，不要私自改）
2. **实现依据是 P2-design.md §3.2（3.2.1-3.2.3）**，伪代码/frontmatter 样例/判定逻辑已经定死，照做。
3. **新增 op 的"无正文回退"语义要理解清楚**：`pass`/`fail`/`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/`design_gap_reviewed_count` 这些字段在 v0.35 正文里**从来不是单行声明**（旧格式靠 grep 计数 PASS/FAIL 行数、BLOCKER 关键词数，不是读一个字段）。所以这些新 op 在 frontmatter 无该字段时应输出**空字符串**，不需要、也不应该在 `agate-md-field-get.py` 内部试图"正则回退"出一个计数——"回退到旧格式计数逻辑"是调用方（`check-gate.sh`/`check-p6-provenance.sh`）的责任：op 返回非空 → 用 frontmatter 声明值；op 返回空 → 调用方执行原有的正文 grep 计数逻辑。不要把两种机制混在一个函数里。
4. **check-p6-format.sh 从"归一化 sed"升级为"行格式校验"**：新增 `--check` 模式（校验 `^\s*-\s+(PASS|FAIL)\s+BDD-\d+`，总结行/小写/全角一律报错要求用 `--fix`），保留 `--fix` 模式（v0.35 现有归一化 sed 原样保留，小写→大写/全角→半角/总结行→`**Summary**:`）。pre-commit 在 gate 前自动 `--fix` 的现有挂载点（`pre-commit-gate.sh` 2h 步骤）**不需要改**，只需保证 `--fix` 行为不回归。
5. **check-p6-provenance.sh 审计 3（PASS/FAIL BDD 数 vs P1 BDD 数）计数口径改严**：`grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`（带 BDD 编号才计入，总结行不再误计，BDD-17/18）；或读 frontmatter `pass+fail` 为总数（新格式），无 frontmatter 汇总 → 回退从严 grep。
6. **FIND-6 交叉校验 WARNING（新增，不是硬拦截）**：新格式下，若 frontmatter `pass+fail` 总数与正文从严行数（上条的 grep）不一致 → 输出 WARNING（`exit` 仍是 0，不阻断），提示"frontmatter 汇总与正文逐条不符，请复核"。这是防呆 nudge，不提升 gate 强度——不要把它写成 exit 1 硬拦截。
7. **P7 BLOCKER/DEVIATION 判定**：读 frontmatter `blocker_count`/`deviation_critical_count` → 皆 0 通过（BDD-19），不再用旧的 `grep -cvE '\[BLOCKER\][:：]?[0-9]+条?$'` 排除总结行的方式；frontmatter 无这些字段（旧格式）→ 回退现有正文 grep 逻辑。
8. **P7 DESIGN_GAP 配对判定**：读 frontmatter `design_gap_count`/`design_gap_reviewed_count` → `reviewed_count >= count` 通过，否则拦截（BDD-20），不再用"数量相减是否为 0"的歧义判定方式（F14 消除）；旧格式回退现有逻辑。**P4 侧的 `[DESIGN_GAP:]` 转抄核对（R2.3 既有机制）不变**——P4-implementation.md 里的 `[DESIGN_GAP:]` 仍从正文 grep（这是 P4 产出物自身的标记，属于流 C 的"发现性标记保持散文"范畴，不是本次要改的东西）。
9. **审计 2（dispatch-context 预判扫描）范围扩展**：`check-p6-provenance.sh` 现有对 dispatch-context 文件"无 `- PASS/FAIL` 预判"的扫描要新增排除 `---` frontmatter 块（不只排除 AGATE_CARD 块）——避免未来 dispatch-context 模板里出现 frontmatter 样例时被误判为预判违规。这是 P2-design.md §3.2.3 明确要求的，不是可选项。
10. **验收目标**：`docs/tasks/T001-v2.0-structured/P3-test-cases.md` §3"流 B"表里标"**红**"的用例必须转绿：`G_BDD16.1`（check-gate.bats）、`F_BDD18.1`（check-p6-format.bats）、`PV_BDD19.1`、`PV_BDD20.1`（check-p6-provenance.bats）。标"绿"的用例（`F_BDD17.1`、`v060-design-gap.bats` 4 条：R2.1/R2.2/R2.3/R2.3b）必须保持绿——回归安全网。**流 A 已转绿的用例（`CF.*`/`MDF.*`）也必须继续保持绿**，不要因为改 `agate-md-field-get.py` 引入回归。
11. **不要求流 C/D 的红灯变绿**：`RT_BDD21.1`/`SC_BDD22.1`（流C）、`SY.1`/`CL.6`/`CL.7`/`CL.8`（流D）本次不管，但不能因为你的改动让它们从"预期红"变成"意外崩溃"。
12. **自查用命令**（不是 gate，P5 才是；我会在你返回后独立重跑全量验证）：
    ```
    cd /home/kity/oclab/agate/.worktrees/v2.0
    bats agate/tests/unit/check-gate.bats agate/tests/unit/check-p6-format.bats agate/tests/unit/check-p6-provenance.bats agate/tests/regression/v060-design-gap.bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/agate-md-field-get.bats
    ```
13. **生产环境隔离**：不适用（本任务不涉及生产环境）。
14. **追加产出 `docs/tasks/T001-v2.0-structured/P4-implementation.md` 的"## 流 B"小节**（该文件已存在，含"## 流 A"小节，`implementation_dir: agate/scripts/` 已声明）——**用追加方式写，不要覆盖或删除已有的"## 流 A"小节**。结构同流 A 那节：目标 / 改动文件清单 / 未改动文件说明（如有）/ 594 配平说明（本流不涉及新增测试，可省略此项或注明"无变化"）/ 自查结果。若发现设计之外必须做的改动，标 `[SCOPE+] 描述`；若发现你判断"设计要求的做法在当前场景不必要/有问题"，标 `[DESIGN_GAP: 描述 + 你的判断依据]`，**不要自己决定跳过**——流 A 已有一次这样的教训（implementer 单方面跳过 check-gate.sh 迁移，被主 Agent 退回补标记），这次直接按标准格式声明，不需要我再退回一次。

### 上游关联

- P2-design.md §3.2 全节（3.2.1 P6 汇总+行格式从严、3.2.2 P7 状态入 frontmatter、3.2.3 审计 2 白名单同步）是本次唯一设计依据。
- P3-test-cases.md §3"流 B"表是本次唯一验收清单。
- 流 A 已交付：`agate-md-field-get.py` 已有 `_read_frontmatter`/`_get`/`_format_value` 基础设施（字段级 presence 检测 + bool 归一化），`agate-frontmatter-check.py` 已含 P6/P7 schema 校验规则（必填字段/类型/嵌套深度），本次**复用**这些基础设施，不要重新发明。
- P2-review.md FIND-6（P7-provenance 交叉校验 WARNING，决定"加"）是本次唯一需要新增的机制（其余都是既有逻辑的读取源切换）。

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义）
- `docs/tasks/T001-v2.0-structured/P2-design.md` §3.2 全节、§13 FIND-6
- `docs/tasks/T001-v2.0-structured/P3-test-cases.md` §3（流 B 验收清单）
- `docs/tasks/T001-v2.0-structured/P4-implementation.md`（流 A 已交付内容，了解 `agate-md-field-get.py` 现有基础设施长什么样，本次在其上追加）
- `agate/scripts/agate-md-field-get.py`（当前状态，流 A 已改造）
- `agate/scripts/agate-frontmatter-check.py`（流 A 已交付的 P6/P7 schema 规则，确认字段名/必填/类型和你要读取的字段一致）
- `agate/scripts/check-gate.sh`（约 236-298 行，P6/P7 分支）
- `agate/scripts/check-p6-format.sh`（现有归一化 sed 逻辑，要升级为 --check/--fix 双模式）
- `agate/scripts/check-p6-provenance.sh`（审计 2 约 115-141 行、审计 3 约 148-186 行）
- `agate/tests/unit/check-gate.bats`（`G_BDD16.1` 用例，确认 P6 分支的确切接口期望）
- `agate/tests/unit/check-p6-format.bats`（`F_BDD17.1`/`F_BDD18.1` 用例，确认 --check/--fix 的确切行为期望）
- `agate/tests/unit/check-p6-provenance.bats`（`PV_BDD19.1`/`PV_BDD20.1` 用例，确认 P7 分支的确切期望）
- `agate/tests/regression/v060-design-gap.bats`（4 条 characterization 用例，确认不能破坏的既有行为）
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active（流 A 已 commit，commit 3754e9d 附近，`git log --oneline -5` 可查）。流 A 独立验证：594 用例、10 个预期流B/C/D红灯、0 意外回归、CHECK9 0 ERROR。
- 流 A 交付的可复用基础设施：`_read_frontmatter(text)`（解析 `---` 块）、`_get(text, op)`（字段级 presence + 正则回退分发）、`_format_value(value, field)`（bool→小写字符串/list→空格连接/int→str）、`BOOL_FIELDS`/`LIST_FIELDS`/`INT_FIELDS`/`STRING_FIELDS` 常量集合、`KNOWN_OPS` 汇总集合（新增 op 时记得加入对应集合，否则 `main()` 的 `if op not in KNOWN_OPS` 会拒绝新 op）。
- 流 A 有一条已记录的 DESIGN_GAP（check-gate.sh/check-pruning.sh 未迁移双读工具）——这是流 A 遗留问题，不是你本次要处理的（除非它恰好和你要改的 P6/P7 分支有交集，若有交集需一并说明）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
