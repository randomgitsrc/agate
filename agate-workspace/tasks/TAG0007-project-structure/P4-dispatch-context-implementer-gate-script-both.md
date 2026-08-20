---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0007
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。本批次是 P2-design.md `dispatch_plan` 声明的
`gate-script-both` 批次（4 批并行之一），是**唯一**改动 `check-gate.py` 的批次（P2-design.md
§1.3 R1：三处判定合并进单一批次，避免同文件跨批冲突，不要与其他批次并行改这个文件）。

### 目标
在 `agate/scripts/check-gate.py` 的 `gate_p2`/`gate_p4`/`gate_p7` 三个函数内新增判定分支，让
P3 已产出的 12 个测试函数（`agate/tests/unit/test_check_gate.py`，函数名前缀 `test_bdd_1_bootstrap`/
`test_bdd_3_`/`test_bdd_4_7_`/`test_bdd_8_9_`/`test_bdd_10_`）从红灯变绿灯。**这些测试已经写好
且不可修改**——你的实现必须让测试断言的确切行为成立，不是反过来设计新逻辑再让测试适配。

### 三处判定的精确规格（已在 P3 测试中锁定，逐条对照实现）

#### 1. `gate_p2`（BDD-1/3，函数约 L552-641，新增分支放在 candidate_count/review 检查通过之后、
最终 `return 2` 之前）
- 读取 P1-requirements.md 的 `project_phase` frontmatter 字段（用现有 `_frontmatter_field(p1_file,
  "project_phase")`，签名已在既有代码 `_frontmatter_field(p2_review, "status")` 处确认）。
- `project_phase == "bootstrap"`：检查 task_dir 下 `P2-skeleton.md` 是否存在且含 `## 骨架声明`
  标题。缺失或缺标题 → `sys.stderr.write(...)` 含 `"P2-skeleton.md"` 字样，`return 1`。存在且含
  标题 → 不额外拦截，继续走到原有 `return 2`。
- `project_phase` 缺失或非 `"bootstrap"`（含显式 `"established"`）：**完全不检查**，行为必须与
  改动前逐字节一致（这是 BDD-3 的回归验收点，测试断言 `"P2-skeleton.md" not in result.output`）。

**对应测试断言（逐字核对）**：
```python
def test_bdd_1_bootstrap_missing_skeleton_exit_1(...):
    # project_phase: bootstrap 声明 + 无 P2-skeleton.md
    assert result.returncode == 1
    assert "P2-skeleton.md" in result.output

def test_bdd_1_bootstrap_with_skeleton_title_exit_2(...):
    # project_phase: bootstrap 声明 + P2-skeleton.md 含 "## 骨架声明" 标题
    assert result.returncode == 2

def test_bdd_3_field_missing_no_regression_exit_2(...):
    # project_phase 完全不声明
    assert result.returncode == 2
    assert "P2-skeleton.md" not in result.output

def test_bdd_3_established_explicit_no_regression_exit_2(...):
    # project_phase: established 显式声明
    assert result.returncode == 2
    assert "P2-skeleton.md" not in result.output
```

#### 2. `gate_p4`（BDD-4/7/10，函数约 L650-680）
在现有"暂存区含代码文件 → return 0"逻辑基础上新增 WARNING 分支（**不改变 exit code 行为，仍是
WARNING 不阻断**）：暂存区含代码文件（现有判定已算出）**且**（task_dir 下 `P2-skeleton.md` 存在
**或** `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在——骨架/CODE-MAP 机制已采用的 OR 条件）**且**
`P4-implementation.md` 缺少 `## 新增文件核对表` 标题 → `sys.stderr.write(...)` 含 `"WARNING"` 与
`"新增文件核对表"` 字样，但仍 `return 0`（不阻断）。**判定逻辑不读取/不分支 `change_type` 字段**
（BDD-10 要求：`change_type: refactor` 声明的任务同样触发这条 WARNING，不豁免）。

**`{AGATE_WORKSPACE}` 路径解析（P2-design.md 未给出精确到函数级的解析细节，你需要自行判断合理
实现方式）**：`task_dir` 通常形如 `{AGATE_WORKSPACE}/tasks/{Txxx}`，`agents/` 是 `tasks/` 的
同级目录。建议实现：`os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(task_dir))),
"agents", "CODE-MAP.md")`（即从 task_dir 向上两级到 workspace 根，再进 agents/）。**这一具体
路径推导方式若与项目实际工作区解析机制（`agate_common.py` 的 `_resolve_workspace` 或
`.agate.env`）有出入，请在 P4-implementation.md 标注 `[DESIGN_GAP: {具体说明}]`**——P3 测试
只覆盖了 `P2-skeleton.md` 分支（task-dir 相对路径，判据明确无歧义），未覆盖
`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 分支的路径解析细节，这是你需要自主决策的实现空间，不是
测试遗漏。

**对应测试断言（逐字核对，均只用 `P2-skeleton.md` 分支验证，符合上述测试覆盖范围说明）**：
```python
def test_bdd_4_7_gate_p4_warning_when_table_missing(...):
    # task_dir 含 P2-skeleton.md；P4-implementation.md 由 create_task_dir 生成的空文件
    # （补 frontmatter 后无 "## 新增文件核对表" 标题）
    assert result.returncode == 0  # WARNING 不阻断
    assert "WARNING" in result.output
    assert "新增文件核对表" in result.output

def test_bdd_4_7_gate_p4_no_warning_when_table_present(...):
    # 同上前提，但 P4-implementation.md 含 "## 新增文件核对表" 标题 + 一行内容
    assert result.returncode == 0
    assert "WARNING" not in result.output

def test_bdd_10_gate_p4_refactor_not_exempt_warning(...):
    # 同 test_bdd_4_7_gate_p4_warning_when_table_missing，额外声明 change_type: refactor
    assert result.returncode == 0
    assert "WARNING" in result.output
    assert "新增文件核对表" in result.output
```

#### 3. `gate_p7`（BDD-8/9/10，函数约 L807-903，两层 pairing 硬校验，与现有 DESIGN_GAP pairing
逻辑结构完全对齐——直接参照现有 `design_gap_count`/`design_gap_reviewed_count` 那两段代码
（L836-893 一带）复制模板改字段名，**不要重新设计判定算法**）：
- 读取 P7-consistency.md frontmatter 的 `code_map_new_files_count` / `code_map_reviewed_count`
  （用 `_md_field_get`，与既有 `design_gap_count`/`design_gap_reviewed_count` 读取方式一致）。
  两字段均缺失 → 机制未采用，**两层校验全部跳过**，不触发任何 CODE_MAP 相关输出（回归对照）。
- **两字段均存在时**，跑两层校验（**字段对应关系必须严格如下，这是 P2 review 第一轮打回过的
  错误点，请仔细核对不要写反**）：
  - **内部一致性层**：`code_map_reviewed_count < code_map_new_files_count` → `return 1`，
    stderr 含 `"CODE_MAP"` 字样（仿照 `dg_reviewed < dg_count` 分支）。
  - **转抄核对层**：从 `P4-implementation.md` 正文用 regex 数 `[CODE_MAP_UPDATED]` +
    `[CODE_MAP_EXEMPT` 两种标记的**实际出现次数**（仿照现有 `p4_design_gap_count` 的 regex 数法，
    正则示例：`r"^\s*-?\s*\[CODE_MAP_UPDATED\]"` 和 `r"^\s*-?\s*\[CODE_MAP_EXEMPT"`），若该实际
    计数 **>** `code_map_new_files_count`（**注意不是** `code_map_reviewed_count`）→ `return 1`，
    stderr 含 `"CODE_MAP"` 字样。
  - 两层均通过（或字段缺失机制未采用）→ 不拦截，继续原有流程（不要提前 `return 0`，插入位置在
    现有 DESIGN_GAP 检查段之后、函数末尾 `return 0` 之前，作为并行独立的检查段，不与 DESIGN_GAP
    逻辑共享变量或互相干扰）。
- `change_type` 字段**完全不读取、不分支**（BDD-10 要求两层校验对 refactor 任务同样生效）。

**对应测试断言（逐字核对，字段对应关系是本部分最容易写错的地方，务必对照）**：
```python
def test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1(...):
    # P7 frontmatter: code_map_new_files_count=2, code_map_reviewed_count=1（1 < 2）
    assert result.returncode == 1
    assert "CODE_MAP" in result.output

def test_bdd_8_9_gate_p7_transcription_mismatch_exit_1(...):
    # P4 正文 3 条 [CODE_MAP_UPDATED]/[CODE_MAP_EXEMPT] 标记；P7 声明
    # code_map_new_files_count=2, code_map_reviewed_count=2（内部一致性层本身通过，
    # 只让转抄核对层单独触发：3 > 2）
    assert result.returncode == 1
    assert "CODE_MAP" in result.output

def test_bdd_8_9_gate_p7_paired_matches_exit_0(...):
    # P4 正文 2 条标记；P7 声明 code_map_new_files_count=2, code_map_reviewed_count=2
    assert result.returncode == 0

def test_bdd_8_9_gate_p7_mechanism_not_adopted_no_check(...):
    # P7 完全不声明 code_map_new_files_count/code_map_reviewed_count
    assert result.returncode == 0
    assert "CODE_MAP" not in result.output

def test_bdd_10_gate_p7_refactor_not_exempt_pairing_check(...):
    # 同 test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1，额外声明
    # change_type: refactor
    assert result.returncode == 1
    assert "CODE_MAP" in result.output
```

### 验证（写完后自跑，不是 P5 gate，是自查）
```bash
timeout 120s python3 -m pytest agate/tests/unit/test_check_gate.py -v 2>&1 | tail -80
```
预期新增的 12 个测试函数全部由红灯变绿灯，**且既有 test_check_gate.py 中所有既有测试用例（数百
个）保持全绿，不产生任何回归**——改的是新增分支，不是修改既有判定逻辑。全跑一遍确认无回归：
```bash
timeout 60s python3 -m pytest agate/tests/unit/test_check_gate.py -q --tb=short 2>&1 | tail -20
```

### 不要做
- 不要碰任何 `.md` 文档文件（`skeleton-docs`/`code-map-docs` 批次的范围，字段名/标题名已由那两
  批次按本设计声明的精确字符串产出，本批次只消费字段名，不重复定义）
- 不要碰 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（`dogfood-bootstrap` 批次）
- 不要修改任何测试文件（`agate/tests/unit/test_check_gate.py` 或其他）——测试已锁定，实现必须
  匹配测试，不是反过来改测试匹配实现
- 不要改动 `gate_p2`/`gate_p4`/`gate_p7` 以外的函数

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0007-project-structure/P2-design.md（§1.1/§2.3/§5/§8 「files_to_read」
  gate-script-both 部分，本批次的权威规格来源，minimal_validation 已核实字段对应关系）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py:552-641
  （`gate_p2` 全函数）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py:642-680
  （`gate_p4` 全函数）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/scripts/check-gate.py:807-903
  （`gate_p7` 全函数，DESIGN_GAP pairing 判定逻辑是直接参照模板）
- /home/kity/oclab/agate/.worktrees/agate-TAG0007/agate/tests/unit/test_check_gate.py:2400-2624
  （本批次要满足的全部 12 个新增测试函数，本 dispatch-context 已摘录关键断言，但建议直接读
  这段源码确认 fixture/helper 用法如 `add_p1_field`/`_write_p2_design`/`add_p2_candidate_count`/
  `add_p2_review`/`_run_gate`/`git_repo`/`_init_repo_with_task`/`_write_p4_review`/`_write_p7`）
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
UI/前端等需构建任务：单元测试全绿不代表可用，implementer 在 P4 完成后应构建并确认 dist 等构建产物存在，不能只跑单元测试就认为完成。

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
- P2-design.md frontmatter：packages=[phase-cards, execution-roles, templates, scripts],
  domains=[backend], ui_affected=false
- 批次范围（P2-design.md §7）：`gate-script-both`，涉及文件 2 个：`agate/scripts/check-gate.py`、
  `agate/tests/unit/test_check_gate.py`（P3 已产出新增测试函数，本批次不改测试文件，只改
  check-gate.py 让测试变绿）
- 现有 `test_check_gate.py` 文件约 2624 行，含数百个既有测试用例，本批次新增改动必须保证既有
  用例 0 回归
- 4 批并行范围两两不相交（P2-design.md §7 已核实），本批次可独立完成，无需等待其他批次
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
