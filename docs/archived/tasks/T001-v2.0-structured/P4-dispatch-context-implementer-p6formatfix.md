> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P4
generated_by: agate-inject-card.sh + 主 Agent
task_id: T001
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 背景（这是一次从 P6 回退的定向修复，不是重做 P4）

P6 验收发现真实 bug：`check-p6-format.sh --fix` 会破坏 `P6-acceptance.md` frontmatter 里 BDD-16 要求的 `pass:`/`fail:` 字段（变成非法 YAML），且没有下游校验拦截。用户已批准从 P6 回退到 P4 定向修复。完整诊断见 `docs/tasks/T001-v2.0-structured/P6-gate-diagnosis.md`（已归档的 P6 证据在 `docs/tasks/T001-v2.0-structured/.archived/20260810-085926-P6/`，其中 `P6-evidence/bdd-17.md` 是最详细的复现分析，值得一读）。

### 目标

修复 `agate/scripts/check-p6-format.sh` 的 `--fix` 模式：让它的归一化逻辑只作用于正文，不触碰 frontmatter 块。补充回归测试覆盖这个此前完全没被测过的场景。

### 约束

1. **只改这 2 类文件**：
   - `agate/scripts/check-p6-format.sh`（核心修复）
   - `agate/tests/unit/check-p6-format.bats`（新增回归用例）
2. **修复方式（先读 `P6-gate-diagnosis.md` 里的"修复方向建议"一节，这是已经想清楚的方案，照做）**：
   `--fix` 分支目前对整个文件内容跑 5 条 `sed` 归一化。改为：先判断文件是否以 `---\n` 开头（有 frontmatter 块），若有，用类似 `agate-frontmatter-check.py`/`agate-md-field-get.py` 里已有的 `_extract_frontmatter_block` 同款逻辑（找到文件头 `---` 到下一个 `\n---` 之间的区间）把文件切成"frontmatter 部分"（含首尾 `---` 分隔符，原样保留不动）+ "正文部分"，5 条归一化 sed **只应用到正文部分**，最后把 frontmatter 部分 + 处理后的正文部分拼回一个文件。无 frontmatter 块的旧格式文件（BDD-9 兼容场景）行为不变（相当于"frontmatter 部分"为空，全文本都是"正文"）。
3. **不要重新发明 frontmatter 提取逻辑**——`agate/scripts/agate-frontmatter-check.py` 里已经有 `_extract_frontmatter_block(text)` 函数（Python），但 `check-p6-format.sh` 是纯 bash 脚本，不方便直接调用 Python 函数返回复杂结构。你可以选择：① 在 bash 里用等价的 `sed`/`awk` 逻辑做同样的"找到第二个 `---` 分隔符位置"的切分（注意 `agate-frontmatter-check.py` 的判定是"文件以 `---\n` 开头，从第 4 个字符开始找下一个 `\n---`"，bash 版要保持同样的语义）；② 或者写一个极简的辅助 python 单行脚本内嵌调用（参考 `check-frontmatter.sh` 用 `python3 -c` 或独立 `.py` 文件的既有模式）。两种方式都可以，选你觉得更简洁可靠的，但**必须和 `agate-frontmatter-check.py` 的 frontmatter 边界判定语义一致**（不能出现"两个工具对同一个文件判断 frontmatter 边界不一样"这种新的不一致）。
4. **验证正确性的核心测试场景**（务必覆盖，这是本次 bug 的直接复现场景）：
   ```
   P6-acceptance.md 内容：
   ---
   phase: P6
   task_id: T001
   pass: 28
   fail: 0
   ui_affected: false
   ---

   - PASS BDD-1: xxx (x.log)
   - pass BDD-2: yyy (y.log)      ← 正文里的小写，应该被 --fix 归一化

   跑 --fix 后期望：
   - frontmatter 的 pass: 28 / fail: 0 原样不变，整个 frontmatter 块依然是合法 YAML（用 python3 -c "import yaml; yaml.safe_load(...)" 验证）
   - 正文的 "- pass BDD-2" 被归一化为 "- PASS BDD-2"（--fix 该做的事没有因为这次修复而失效）
   ```
5. **回归测试要覆盖**：
   - 新场景（本次修复的核心）：含 frontmatter `pass:`/`fail:` 字段的文件跑 `--fix`，frontmatter 保持合法 YAML 不变
   - 已有场景（不能因为这次改动而回归）：无 frontmatter 的旧格式文件、正文散文里的 pass/fail 归一化、总结行归一化——这些既有行为必须保持不变，跑 `agate/tests/unit/check-p6-format.bats` 全部既有用例确认无回归
6. **验收标准**：
   ```
   cd /home/kity/oclab/agate/.worktrees/v2.0
   bats agate/tests/unit/check-p6-format.bats
   bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats
   shellcheck -S warning agate/scripts/check-p6-format.sh
   ```
   全量应仍是 600/N（N = 594 + 新增回归用例数，不是恰好 600 了——这次是真的新增用例，不受 BDD-11 的"594 不漂移"硬约束限制，因为那条约束是 T001 v2.0 改造本身的范围内测试基线，本次是发现的新 bug 修复，理应新增测试覆盖这个此前的盲区）。shellcheck 应无输出。
7. **自查**：改完后用约束 4 给的具体场景手动验证一遍（构造真实 fixture，`--fix` 后 `yaml.safe_load` 确认 frontmatter 合法），再跑约束 6 的自动化测试。这不是最终 gate，我会独立重跑验证。
8. **生产环境隔离**：不适用。
9. **产出/追加记录**：本次是从 P6 退回的定向修复，不是走一个新的"流"，不需要在 `P4-implementation.md` 追加"## 流 X"格式的小节（那些是 A/B/C/D 四个既定流的命名空间）。改为追加一个"## P6 回退修复：check-p6-format.sh frontmatter 破坏 bug"小节，简述问题+修复方式+新增测试。

### 上游关联

- `docs/tasks/T001-v2.0-structured/P6-gate-diagnosis.md`（完整诊断，含复现步骤 + 根因分析 + 修复方向建议——这是本次派发的直接依据，先读这个）
- `docs/tasks/T001-v2.0-structured/.archived/20260810-085926-P6/P6-evidence/bdd-17.md`（P6 verifier 的原始发现记录，更详细的分析过程）
- `agate/scripts/agate-frontmatter-check.py`（`_extract_frontmatter_block` 函数，frontmatter 边界判定的既有实现，语义要对齐）

### 输入文件（自己读）

- `agate/assets/execution-roles/implementer.md`（角色定义）
- `docs/tasks/T001-v2.0-structured/P6-gate-diagnosis.md`（完整读）
- `agate/scripts/check-p6-format.sh`（当前状态，待修复文件）
- `agate/scripts/agate-frontmatter-check.py`（`_extract_frontmatter_block` 实现参考）
- `agate/tests/unit/check-p6-format.bats`（既有用例，了解测试风格）
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
- 环境状态：worktree `feat/v2.0`，`.state.yaml` phase=P4 status=active，retries: P5(1)/P4(1)（本次是从 P6 回退后的重新进入 P4，非首次）。HEAD 023b28b（P5→P4 回退 commit）。
- 主 Agent 已独立复现 bug：构造含 `pass: 28`/`fail: 0` frontmatter 的真实 `P6-acceptance.md`，跑 `--fix` 后 frontmatter 变为非法 YAML（`**Summary**: PASS: 28` 替换了 `pass: 28`），已用 `python3 -c "import yaml; yaml.safe_load(...)"` 验证解析失败。
- 已用 `diff` 确认这段有问题的 sed 逻辑是 v0.35 时代的既有代码，本次 v2.0 改造此前从未触碰过——这是一个此前从未被测试覆盖到的组合场景（frontmatter pass/fail 字段是本任务新引入的，恰好和这段老代码冲突）。
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
