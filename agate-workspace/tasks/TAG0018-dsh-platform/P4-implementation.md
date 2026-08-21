---
phase: P4
task_id: TAG0018
type: implementation
parent: P2-design.md
trace_id: TAG0018-P4-20260821
status: done
agent: implementer
implementation_dir: agate/assets/templates/dsh/ + agate/SETUP.md + agate/platform-notes.md + agate/tests/README.md（worktree 根相对路径）
---

# P4 实现摘要 — agate 原生支持 DSH 平台（TAG0018）

> 依据：P1 BDD-1~19（验收权威）+ P2-design.md（设计权威，D-1~D-5 决策）+ P3-test-cases.md（8 用例断言基准）+ P2-review.md（7 条非阻塞建议，P3 已吸收 3 条为用例、P4 吸收其余 4 条）。参考实现（agate-copy，非权威）作为蓝本，凡与 BDD/设计冲突处以 BDD/设计为准。

## 交付物落位（6 + 1）

### 1. `agate/assets/templates/dsh/agent.cordis.yml`（新建，→ BDD-1/2/3）

- 顶层行列表（13 行，每行非空 `id`/`name`；`grep -c "^- id:"` = 13，含 delegation 组嵌套共 20 处 id），`!!js process.platform` 自定义标签保留（BDD-1 测试用 `_js_loader` 容忍）。
- **tool-fs-search 行含 `config.sampleOverCapGlobResults: false`**（BDD-2/BDD-17 回归护栏断言对象；实机缺陷修复，schemastery 必填无默认值，缺失 → preset 挂载失败 → fail-closed 拒绝创建会话）。
- persona 行 = 薄身份：你是谁 + 会话开始 5 步（解析 agate_root / project_root / AGATE_WORKSPACE / 读 `{agate_root}/orchestrator-template.md` / 读 active-tasks.md）+ DSH 工具映射 + 平台注意；含 `{agate_root}/orchestrator-template.md` 引用，**不含**模板首行标题「# Orchestrator（agate 编排 Agent）」（BDD-3 双判据，模板全文零复制）。
- 工具面 = 最小集：persona / agent-instructions / bash+pwsh（`!!js` 平台分支）/ fs+fs-search / jobs / skills（skill-filesystem + tool-skill）/ goal / delegation 组（subagent + subagent_fork + workflow + ralph，`cordis:group` + `isolate.workflowEngine` 语法对齐 DSH standard preset）/ ask-user / todo。
- 文件头注释：移除参考草稿的「草稿，待实机验证」字样，改为「已实机验证（2026-08-21，DSH v0.1.0-rc.8）」+ 缺陷修复说明（决策 D-2）。

### 2. `agate/assets/templates/dsh/preset.yml`（新建，→ BDD-4）

- `name: agate 编排者` / `description`（非空，P0-P8 编排职责一句话）/ `order: 1`——最小元数据集（决策 D-4；name/description 非空是产品级要求，非 DSH schema 强制，不做挂载失败类过度设计）。

### 3. `agate/assets/templates/dsh/SKILL.md`（新建，→ BDD-5/6）

- frontmatter：`name: agate-protocol` + 非空 description（BDD-5；DSH 技能目录按名发现）。
- 正文：①「编排者四项职责 × DSH 工具」映射表（读状态 → read/grep/glob；派发 → subagent/subagent_fork；跑 gate → bash 按 `[exit code: N]` 判定；更新状态 → write/edit）——与 persona 内联映射同口径（决策 D-5）；② 4 个 DSH 原生食谱（workflow 并行派发 / ralph 独立 judge / goal 跨轮续跑 / session hooks 实时 gate）；③「平台注意」四要素（sandbox 只读区 Errno 30 / /tmp 只读 --basetemp / 审批策略 / bash 纪律 timeout + 工具读文件）；④ 接入后验证清单。

### 4. `agate/SETUP.md`「步骤 2-DSH」章节（追加，→ BDD-7~11）

- 落位：步骤 2 平台章节区内最后一个 h3——`### 步骤 2-DSH：deepseek-harness（DSH）接入`（现 L144，Windows 环境适配要点 h3 L130-143 之后、`## 步骤 3` L173 之前；决策 D-1）。
- 命令块（与 P3 用例 6/8 断言完全一致）：
  - `mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol`
  - **三条独立** `ln -sf ~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml}` → `~/.dsh/.agent-presets/agate/`、`SKILL.md` → `~/.dsh/skills/agate-protocol/SKILL.md`（P2-review 建议 5：花括号简写改显式三条 ln 行，与 BDD-8 字面及测试断言一致）
  - `python3 ~/.agate/scripts/install-hook.py`（唯一安装脚本调用，BDD-9 前半）
- 说明段：「身份薄、协议厚」表述 + 升级行为（符号链接升级免操作 / 无符号链接权限退复制模式、升级后重跑 `ln` 对应 `cp`）（BDD-10）。
- 使用段：打开 DSH 会话 → 会话选择器选「agate 编排者」（对应 `claude --agent orchestrator`）→ 执行 orchestrator-template.md「开始」几步验证（BDD-11）。
- 版本敏感提示：已实机验证（2026-08-21，DSH v0.1.0-rc.8）+ 机制可能随版本变化（决策 D-2）。

### 5. `agate/platform-notes.md`「## DSH（deepseek-harness）」条目（追加，→ BDD-12/13/14）

- 落位：文件末尾 h2 条目（现 L174，与既有 OpenCode/Claude Code 等条目同级；决策 D-3 闭合括号标题，消除 BDD-12 子串断言歧义）。
- 能力差异对照表：**六行**（orchestrator 身份注册 / 派发 subagent / 批量并行派发 / 独立复核 judge / 跨轮续跑 / 实时 gate），OpenCode/Claude Code vs DSH（BDD-13；按设计 §3 交付物 5 的六项，未扩参考草稿的第 7 行「外部 agent 执行」——最小实现）。
- 已知注意两条：sandbox 只读区（Errno 30）；DSH 无 `.claude/agents/*.md` 等价物——不要试图把 orchestrator-template.md 软链进 DSH 目录，用 preset（BDD-13）。
- 互链：条目开头注明「接入步骤见 `SETUP.md`「步骤 2-DSH」（接入命令单一真相源）」（BDD-14）。

### 6. `agate/tests/unit/test_dsh_preset.py`（P3 已落位，P4 未修改）

- 8/8 全红 → 实现落位后 **8/8 全绿**；BDD-17 变异复证见「测试结果」。

### 顺手项（M-7，P1 [SUGGEST] 2，非 gate 强制）

- `agate/tests/README.md` 脚本→测试映射表补一行：`| DSH 平台模板结构（TAG0018）| unit/test_dsh_preset.py | 8 |`（count-tests.sh 用 collect-only 计数，不受该表影响）。

## 测试结果

| 验证项 | 命令（worktree 根 cwd） | 结果 |
|--------|------------------------|------|
| P3 单文件 | `python3 -m pytest agate/tests/unit/test_dsh_preset.py -q -p no:cacheprovider --basetemp=...` | **8/8 passed**（0.04s）|
| 全量 unit | `python3 -m pytest agate/tests/unit/ -q -p no:cacheprovider --basetemp=...` | **906 passed, 2 skipped**（62.85s，exit 0，无新失败）；用例总数 1030 → 1038 只增不减（1038 为 `bash agate/tests/scripts/count-tests.sh` 全量收集口径，非本行 unit 运行输出）|
| BDD-17 变异 | 移除 `config.sampleOverCapGlobResults: false` → 用例 2 FAIL（AssertionError）；恢复 → 8/8 PASS | 红/绿双态可复现，回归护栏真实 |
| consistency（R-4 自查） | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | **0 ERROR** / 317 WARNING（exit 0；`dsh/` 子目录与 `.yml` 新形态未引入新 ERROR；基线 335 为 P2-review 实测口径，量级一致）|

## P2-review 建议吸收（P4 侧 4 条，P3 已吸收 3 条）

| 建议 | P4 吸收方式 |
|------|------------|
| 3（M-4 行号精度）| 以实际行号为准：Windows 区 = h3① L111-129 + h3② L130-143；DSH h3 插于 L143 后（现 L144）；步骤 3 原 L144 → 现 L173。设计写「L111-139」的 4 行差已不再引用 |
| 4（pytest 双 cwd 口径）| 本 P4 全部测试命令以 worktree 根为 cwd（`agate/tests/...` 前缀），与 P2-design §5 gate_commands 口径一致 |
| 5（花括号简写歧义）| SETUP.md 命令块用**三条独立 `ln -sf` 行**（无 `{a,b}` 花括号简写），与 BDD-8 字面及 P3 用例 6 断言一致 |
| 6（基线 WARNING 数）| 记录 consistency 基线 0 ERROR / 335 WARNING（P2-review 实测）；P4 自查 0 ERROR / 317 WARNING，无新 ERROR（见测试结果表）|

## 新增文件核对表（CODE-MAP 机制已采用；骨架未采用）

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| agate/assets/templates/dsh/agent.cordis.yml | N/A（无 P2-skeleton.md）| `[CODE_MAP_EXEMPT: CODE-MAP 为模块级架构图，templates 模块描述用「等」非枚举式；dsh/ 子目录属既有 templates 模块内新增，无新模块/新层，无需更新 CODE-MAP]` |
| agate/assets/templates/dsh/preset.yml | 同上 | 同上 |
| agate/assets/templates/dsh/SKILL.md | 同上 | 同上 |
| agate/tests/unit/test_dsh_preset.py | 同上（P3 已提交，非 P4 新增）| `[CODE_MAP_EXEMPT: tests 为既有测试模块内新增文件，CODE-MAP 不枚举测试文件]` |

## 执行决策说明（透明记录，非 DESIGN_GAP）

1. **「待实机验证标注」措辞**：派发指引目标 4 写「待实机验证标注」，而 P2-design 决策 D-2（approved）明确要求**移除**「待实机验证」陈旧字样、改为「已实机验证（2026-08-21）」+ DSH v0.1.0-rc.8 版本敏感提示。实机验证确已完成（P2 §6 env_constraints 记录：preset 软链安装 → 热发现 → 选择器出现「agate 编排者 · 自定义」→ 新会话以 agate 编排者人格启动）。本实现按**设计权威（D-2）**执行：SETUP.md/platform-notes.md 均标注实机验证状态与版本敏感提示，未保留「草稿/待实机验证」字样。若主 Agent 意图是保留待验证项清单，请指示回补。
2. **platform-notes 能力表行数**：参考草稿含 7 行（多「外部 agent 执行」），本实现按设计 §3 交付物 5 的六项能力落位（最小实现，不扩范围）；BDD-13 判据（六项 + 两条注意）完全覆盖。
3. **无 [SCOPE_GAP]**：P2 声明改动（M-1~M-7）全部落实，prompt 无遗漏项。
4. **无 [SCOPE+]**：实现未发现 P1/P2 未覆盖的必须动作。
5. **self-gate 触发面**：本次改动含 `agate/SETUP.md`、`agate/platform-notes.md`、`agate/assets/templates/dsh/SKILL.md`（`agate/**/*.md`）——P8 commit message 必须携带 `self-gate-review:` / `self-gate-skip:` 标记（BDD-19）；`test_dsh_preset.py` 不触发。

## 完成标准自检（P2-design §11）

- [x] 文件在位：dsh/ 三模板 + SETUP.md 步骤 2 区内「步骤 2-DSH」+ platform-notes.md DSH 条目 + tests/README.md 补行
- [x] 单文件测试：8 用例全绿（≥5）
- [x] 回归护栏：变异缺配置 → FAIL / 在位 → PASS（BDD-17 实跑复证）
- [x] 全量回归：unit 全量 906 passed + 2 skipped 无新失败；consistency 0 ERROR（自查；P5 全量 gate 由主 Agent 跑）
- [x] 不发明新结构复证：worktree 全仓 grep `install-dsh` 0 命中、find 无 install-dsh.py；scripts/ 仅 install-hook.py 等
- [ ] self-gate 标记：P8 commit 时携带（本阶段不 commit，标记由主 Agent 在 commit message 中落实）

## P4-review 建议吸收（4 条非阻塞，status: approved，0 BLOCKER/0 CRITICAL）

| 建议 | 吸收落点 |
|------|---------|
| 1（§1 顶层行数「15 行」→ 13 行）| 本文件 §1 已改为「13 行（grep -c "^- id:" = 13，含嵌套共 20 处 id）」 |
| 2（1038 计数来源标注）| 本文件测试结果表「全量 unit」行已标注：1038 为 `bash agate/tests/scripts/count-tests.sh` 全量收集口径，非 unit 运行输出 |
| 3（复制模式退化指引）| `agate/SETUP.md` 步骤 2-DSH 已补：「Windows 无符号链接权限时退复制模式，升级后需重跑上述 `ln` 命令对应的 `cp`（复制模式代价：模板升级后不会自动同步）」 |
| 4（session hooks 实现方式措辞）| `agate/assets/templates/dsh/SKILL.md` 食谱 4 已改为：「PostToolUse 类 session hooks 经 DSH `hooks-claude-code` 配置或强类型 agent 扩展点实现（见 DSH 代码 `packages/hooks/`）」 |
