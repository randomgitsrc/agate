> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0004
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

实现 TAG0004 全部修复（S1/S2/S3/M4/M5/M6/M9 + Q1/Q2/Q5 + RM-AG0001/RM-AG0002 + TPV0090-M4 + 其他项 + CI），让 P3 的 21 条红灯测试变绿（不修改测试本身），保持 16 条回归守卫绿。产出 `P4-implementation.md` 声明 implementation_dir + 实际代码改动。

### 约束

- **修复对象 = worktree 的 `agate/` 目录**（`/home/kity/oclab/agate/.worktrees/agate-TAG0004/agate/`）。**禁止改主 checkout `/home/kity/oclab/agate` 和 `~/.agate`**（稳定版 v0.43.0）。
- **按 P2-design.md 方案实现**（候选 1A-16A 选定方案），不擅自扩大范围。发现 P2 设计歧义 → 标 `[DESIGN_GAP: ...]` 或 `[CLARIFY: ...]`；发现 prompt 漏了 P2 已声明改动 → 标 `[SCOPE_GAP]`。
- **让 P3 红灯变绿，不改测试**：P3-test-cases.md 是行为契约。测试断言与 BDD 矛盾 → 标 `[DESIGN_GAP]` 不改测试。
- **实现分组**（按 P2-design §1 选定方案）：
  - **S1**（BDD-1..4）：`pre-commit-gate.sh` STAGED_STATE_FILES/PROCESSED_DIRS 数组化（L50/57/339/343/350）；`set -u` 下 `+=()` 处理；§3 验证场景清单 9+1 项（含 P2-review 观察项 1：任务级 .state.yaml 变更但无 P 产出）
  - **S3**（BDD-5..8）：13 个 py 全部文本 open() 加 `encoding="utf-8"`（P1 §6 清单；`Image.open` 二进制除外）——**先写 grep 断言审计测试已在 P3 完成**，实现按清单逐一补
  - **S2**（BDD-9/10）：`check-p6-evidence.sh:37` 正则改负类加宽 `\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`（维持"文件名+扩展名"结构，防过宽）
  - **M4/M5**（BDD-11..13）：`check-gate.sh:356/357` + `check-p6-format.sh:69` bracket 改 alternation `(:|：)`（统一 v0.40.3 L84 修法）
  - **M6**（BDD-14..16）：frontmatter 提取入口统一 CRLF 归一（py 侧读取后 `.replace('\r\n', '\n')`；shell 侧 `tr -d '\r'` 或 `sed 's/\r$//'`）——入口：`agate-md-field-get.py`、`agate-frontmatter-check.py`、`check-gate.sh` P1/P2 review status 提取、`check-frontmatter.sh` 链路。**不改 .gitattributes**
  - **M9**（BDD-17）：`pre-commit-gate.sh:102/133/228` 改 `grep -F` 前缀 + `awk 'index($0,p)==1'` 行首锚定
  - **Q1**（BDD-21/22）：`agate-next-card.sh:56` 前缀剥离改"先试直接剥离，失败再归一化剥离"（Linux 字节不变优先）；归一化统一 `/`、盘符大小写用 `tr` 或 bash 参数替换（P2-review 观察项 3：避免 `\L`）
  - **Q2**（BDD-23..25）：7 张 phase-cards 补注规则 2 语义（参照 P5 卡）；纯文档，不改 gate 逻辑
  - **Q5**（BDD-26/27）：SETUP.md Windows 章节 + .gitignore 预设 `!version.txt` + `dist/`
  - **RM-AG0001**（BDD-28/29）：`check-gate.sh` P1 标记正则加反引号容错（L69/71/89/109/125/129）
  - **RM-AG0002 + TPV0090-M4**（BDD-30/31/35/36/37）：`check-tdd-red.sh` + `gate-result.sh`——无 formatter 路径 exit 1 + 关键词（`Traceback|SyntaxError|ImportError|ModuleNotFoundError`，**不用裸 `error:`**）→ A 类；formatter 路径 pytest.sh 加 `name_errors` 字段解析（项目模块内 NameError → B 类）；保持 globals().get() 兼容
  - **其他-a/b/c**（BDD-18/19/20）：`agate-workspace-resolve.sh:33` tr -d '\r'；`install-hook.sh` 复制模式写 `.agate-root` 标记 + `pre-commit-gate.sh:26` 读标记兜底；`agate-render-dispatch-prompt.sh:112-126` sed 转义（awk 替代或转义预处理）
  - **CI**（BDD-33）：`.github/workflows/protocol-tests.yml` 加 windows-latest matrix（bats/shellcheck/consistency/gate-backstop）
- **P2-review 4 项观察项全部落实**（见 P3-test-cases.md §P2-review 观察项落实，测试已按此写）。
- **SELF-GATE 触发**：改 `agate/scripts/*.sh/.py`、`agate/phase-cards/*`、`agate/*.md` 触发——commit message 需 `self-gate-review:`；协议文档变更需跑 `check-protocol-consistency.py` 确认 0 ERROR。
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`（被 provenance 预判检测匹配）。改用"通过/失败"或加引号。

### 上游关联

- P2-design.md approved：候选 1A-16A、§2 BDD 映射表 37/37、§3 S1 验证场景清单、§4 files_to_read/gate_commands。
- P3-test-cases.md：37 条测试用例（21 红 / 16 绿），测试名引用 BDD 编号，分布在 agate/tests/ 下。
- P1-requirements.md：37 BDD + 审计范围（§6 代码位置清单）。
- P2-review 4 项非阻塞观察项（已由 test-designer 落实进测试）。

### 输入文件

- `agate-workspace/tasks/TAG0004-env-adaptation/P2-design.md`（方案 + files_to_read 导航 + gate_commands）
- `agate-workspace/tasks/TAG0004-env-adaptation/P3-test-cases.md`（测试用例契约 + 红灯分布）
- `agate-workspace/tasks/TAG0004-env-adaptation/P1-requirements.md`（37 BDD + 审计范围）
- `agate-workspace/tasks/TAG0004-env-adaptation/P0-brief.md`（任务简报）
- `HANDOFF-TAG0004.md`（worktree 根：交接单，双工作区纪律、TDD 纪律）
- `AGENTS.md`（项目约定：脚本关键约定、SELF-GATE 触发清单）
- 按 P2-design §4 files_to_read 读取代码（pre-commit-gate.sh / check-gate.sh / check-p6-format.sh / check-p6-evidence.sh / check-tdd-red.sh / gate-result.sh / agate-next-card.sh / agate-workspace-resolve.sh / install-hook.sh / agate-render-dispatch-prompt.sh / 13 py / formatter pytest.sh / phase-cards / SETUP.md / .gitignore / protocol-tests.yml）
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
5. 更新 .state.yaml phase=P4 → P5
6. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
7. git commit -m "wf({Txxx}-P4): {摘要}"

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
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`；协议 v0.43.0；基线 676 bats 全绿；P3 已写 37 条测试（21 红 / 16 绿）
- 关键路径：产出 `agate-workspace/tasks/TAG0004-env-adaptation/P4-implementation.md`；代码改动在 `agate/` 下
- 自查命令：`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`（P3 自跑已有 21 红基线）；`python3 agate/scripts/check-protocol-consistency.py --strict`；`shellcheck -S warning agate/scripts/*.sh`
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
