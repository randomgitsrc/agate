---
phase: P2
task_id: TAG0018
type: design
parent: P1-requirements.md
trace_id: TAG0018-P2-20260821
status: draft
created: 2026-08-21
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 1          # design_trivial: true（P1 已声明，理由见 §2），P2 gate 允许 1 个候选
packages: [agate]           # 协议本体——六项交付物全部落在 agate/ 内（templates/dsh/ + SETUP.md + platform-notes.md + tests/unit/）
domains: [cli, docs]        # cli=平台接入/身份注册命令面（SETUP.md 步骤 2-DSH 符号链接命令）；docs=文档章节与模板；无 backend/frontend/mcp/security
ui_affected: false          # 纯仓库文件新增/追加，无显示或交互变化，无 E2E 需求
# ── v2.0 派发编排字段（可选；单包低复杂度，single 模式）──
dispatch_plan: {mode: single, parallel_limit: 1}
---

# P2 方案设计 — agate 原生支持 DSH 平台（TAG0018）

> 一句话摘要：把 P0-brief 已锁定的接入方案（**SETUP.md 文档化符号链接 + 唯一 install-hook.py**，身份注册用 DSH agent-preset）正式化为六项交付物设计——三个 `assets/templates/dsh/` 模板文件、SETUP.md「步骤 2-DSH」小节、platform-notes.md DSH 条目、`tests/unit/test_dsh_preset.py` 回归测试，全部为新增文件/追加章节，不触碰既有协议机制运行时行为；以 P1 的 BDD-1~19 为逐条验收基线，吸收 P1-review 全部非阻塞建议。

## 0. 设计定位与输入

- **性质**：`design_trivial: true`（P1 已声明）。P0-brief 已锁定接入路线（符号链接 + agent-preset，实机验证 2026-08-21 完成），P2 职责 = 把已实机/TDD 验证的草稿结构**正式化**并逐条映射 BDD，不做新方案探索。
- **输入**：P1-requirements.md（19 条 BDD，权威验收基线）、P1-review.md（approved + 5 条非阻塞建议 S-1~S-5 + 2 条 [SUGGEST]）、P0-brief.md、参考实现（agate-copy，非权威，已实机/TDD 验证）。
- **权威性声明**：设计以 BDD 为准；参考草稿的结构/命令串仅作内容基线，凡与 BDD 冲突处以 BDD 为准（差异决策见 §2.3）。

## 1. 影响面梳理（强制节）

> 证据来源：worktree（分支 `feat/TAG0018-dsh-platform`，`.state.yaml` phase=P1）实际文件状态；grep/read 命中见 P2-progress.md。

### 1.1 改什么（Modify）

| # | 改动落点（文件 + 位置） | 改动内容 | 关联 BDD |
|---|------------------------|---------|---------|
| M-1 | `agate/assets/templates/dsh/`（**新目录**，新建 `agent.cordis.yml`） | 新增 orchestrator agent-preset：行列表结构、persona 薄身份（指向 `{agate_root}/orchestrator-template.md`）、tool-fs-search 带 `config.sampleOverCapGlobResults: false` | BDD-1/2/3 |
| M-2 | `agate/assets/templates/dsh/preset.yml`（新文件） | 新增展示元数据：`name: agate 编排者` / `description`（非空） | BDD-4 |
| M-3 | `agate/assets/templates/dsh/SKILL.md`（新文件） | 新增 agate-protocol skill：frontmatter（name/description）+ 四项职责×DSH 工具映射 + 平台注意 | BDD-5/6 |
| M-4 | `agate/SETUP.md`「步骤 2」区（现有 h3 小节末尾，Windows 小节 L111-139 之后、步骤 3 L144 之前） | 追加「步骤 2-DSH」h3 小节：符号链接命令块（mkdir -p + 三条 ln -sf + install-hook.py 调用）+「身份薄、协议厚」说明 + 使用与验证指引 | BDD-7~11 |
| M-5 | `agate/platform-notes.md` 文件末尾（现有 h2 条目之后） | 追加 `## DSH（deepseek-harness）` 条目：能力差异对照表（六项能力）+ 已知注意（两条）+ 指向 SETUP.md「步骤 2-DSH」的互链 | BDD-12/13/14 |
| M-6 | `agate/tests/unit/test_dsh_preset.py`（新文件） | 新增 5 用例回归测试：agent.cordis.yml 行结构 / tool-fs-search 必填配置 / preset.yml 元数据 / SKILL frontmatter / SETUP.md 章节命令在位；平台无关（只读仓库内文件） | BDD-15/16/17 |
| M-7 | `agate/tests/README.md`（脚本→测试映射表） | 补 `test_dsh_preset.py` 一行（P1 [SUGGEST] 第 2 条，文档卫生，非 gate 强制） | —（P1 [SUGGEST]） |

### 1.2 不改什么（Not Modify）

| # | 范围 | 不改的理由 |
|---|------|-----------|
| N-1 | `agate/scripts/install-hook.py` 及 scripts/ 其他脚本 | 唯一安装脚本已存在（worktree 核实），BDD-9 只要求 SETUP.md 章节**引用**它，不改其行为；不新增任何 per-platform installer |
| N-2 | `agate/orchestrator-template.md` | 身份薄协议厚的锚点——persona 指向它而非复制它；模板本身不在本任务改动面 |
| N-3 | `agate/SETUP.md` 既有小节（步骤 2 的 Claude Code/OpenCode/Windows、步骤 3/4/5、.agate.env、.gitignore） | BDD-7 要求 DSH 小节与既有小节同构，既有内容一字不动（追加而非改写） |
| N-4 | `agate/platform-notes.md` 既有条目（OpenCode/Claude Code/Claude Project/Codex/Hardening/验证记录/Windows 原生） | 只追加 DSH 条目，不触碰既有条目结构与内容 |
| N-5 | `agate/assets/templates/` 既有 13 个模板文件 | dsh/ 是新子目录；既有模板保持 kebab-case .md 平铺风格不变 |
| N-6 | `P0-brief.md` | 锁定文件；self-gate 触发面修正只记录于 P1 §0/§7 + BDD-19，不物理改动 P0-brief（吸收 S-2） |
| N-7 | `.state.yaml`、active-tasks.md、HANDOFF 等任务状态文件 | 由主 Agent 维护，非交付物 |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解措施 |
|---|------|---------|
| R-1 | 测试断言与文档实现漂移（SETUP.md 命令串拼写与 BDD-8 精确断言不一致） | test_dsh_preset.py 以 BDD-8 的精确命令串为断言基准；P5 单文件 pytest + P6 BDD-15 逐条兜底 |
| R-2 | 双源同步：persona 内联工具映射 与 SKILL.md 表格 双份 | 以「编排者四项职责 × DSH 工具」为统一口径（P1 [SUGGEST] 第 1 条）；修改映射时两处同步，P4 实现时先定口径再写两处 |
| R-3 | SELF-GATE：SKILL.md（`agate/**/*.md`）、SETUP.md、platform-notes.md 触发 commit-msg-self-gate.py | commit message 携带 `self-gate-review:`/`self-gate-skip:` 标记（BDD-19，P8 核对触发面覆盖）；test_dsh_preset.py 不触发（正则不匹配 tests/unit/*.py，P1 已核实） |
| R-4 | `dsh/` 子目录与 `.yml` 是模板目录新形态，check-protocol-consistency.py 扫描行为未知 | P5_consistency gate（`--strict-errors-only` 0 ERROR）兜底；既有 templates/ 下 13 个 .md 已被一致性检查容忍，SKILL.md 同属模板内容目录，预期无 ERROR；若出现 ERROR 由 P4 按 checker 文件分类处理，不降级 |
| R-5 | 平台无关性回归（测试误引入 Unix 假设：裸 /tmp、符号链接语义、真实 DSH 调用） | 设计约束写死四条禁止项（不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖主目录路径）；P5 全量 pytest（CI 无 DSH 环境）兜底 |
| R-6 | preset.yml 语义误读：实现者以为缺 name/description 会挂载失败而过度设计 | 吸收 S-3：name/description 是**产品级要求**（会话选择器展示「agate 编排者」），非 DSH schema 强制（metadata.ts 证实缺失仍挂载）；preset.yml 保持最小元数据 |

## 2. 候选方案与选择（design_trivial: 1 个候选）

### 2.1 候选方案（唯一）：符号链接 + agent-preset 接入，草稿结构正式化

方案要点（即交付物设计，详见 §3）：

1. `assets/templates/dsh/` 三个模板文件——`agent.cordis.yml`（agent-preset：persona 薄身份 + 最小工具面 + tool-fs-search 必填配置）、`preset.yml`（展示元数据）、`SKILL.md`（agate-protocol 适配层 skill）；
2. `SETUP.md` 步骤 2 内追加「步骤 2-DSH」小节：`mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol` + 三条 `ln -sf`（模板源 → DSH 安装目标）+ `python3 ~/.agate/scripts/install-hook.py`（唯一安装脚本）；
3. `platform-notes.md` 追加 DSH 条目（能力差异表 + 已知注意 + 互链 SETUP.md）；
4. `tests/unit/test_dsh_preset.py` 回归测试（5 用例，平台无关）。

### 2.2 选择理由（design_trivial 的"选择"+ 理由）

- **为什么只需 1 个候选**：P0-brief 已锁定接入路线，且路线每一步都有客观证据——DSH 身份注册机制是 agent-preset（无 `.claude/agents/*.md` 等价物，issue 1）、符号链接安装形态已在 2026-08-21 实机验证（preset 热发现 → 挂载 → 会话选择器出现「agate 编排者 · 自定义」→ 新会话以 orchestrator 人格启动）、tool-fs-search 缺陷已实机复现并修复、草稿测试已 TDD 红/绿验证。不存在"还有别的做法吗"的开放问题：`platforms/` 目录 / per-platform installer 路线已被同类扫描 S-1/S-2 证实无先例且被 P0-brief 明令禁止（install-dsh.py 已废弃）。
- **该方案的不可替代性**：DSH 装配器按固定文件名发现 preset/skill（`agent.cordis.yml` / `preset.yml` / `SKILL.md`），符号链接让模板随 `~/.agate`（→ 仓库软链）升级自动更新——与官方平台接入（Claude Code `.claude/agents/` 软链）同构，是唯一满足"身份薄协议厚 + 不发明新结构"两条核心约束的接入方式。

### 2.3 与参考草稿的差异决策（取舍锚点）

| # | 取舍点 | 草稿做法 | 本设计决策 | 理由 |
|---|--------|---------|-----------|------|
| D-1 | SETUP.md「步骤 2-DSH」位置与标题级别 | 文件末尾 h2（`## 步骤 2-DSH`，在 .gitignore 之后） | 步骤 2 区内最后一个 **h3 小节**（`### 步骤 2-DSH：deepseek-harness（DSH）接入`，Windows 小节后、步骤 3 前） | BDD-7 要求「位于步骤 2 平台章节区（与既有平台小节同构）」——h3 与 Claude Code/OpenCode/Windows 小节同级、位置在步骤 2 区内，标题串「步骤 2-DSH」仍在（BDD-7/BDD-15 断言不依赖标题级别）；草稿的 h2 末尾放置不满足"步骤 2 平台章节区"的字面要求 |
| D-2 | 草稿「待实机验证」标记（SETUP.md ①②③ / platform-notes 草稿状态） | 保留「草稿，待实机验证」字样 | 全部移除，改为「已实机验证（2026-08-21）」+ DSH v0.1.0-rc.8 版本敏感提示（机制可能随版本变化） | 吸收 S-5：实机验证已完成，陈旧标记误导读者；新兴平台风险改由版本敏感提示承载（P0-brief known_risk 1） |
| D-3 | platform-notes DSH 条目标题 | `## DSH（deepseek-harness，草稿）` | `## DSH（deepseek-harness）`（全角括号闭合） | 吸收 S-1：BDD-12 断言串 `## DSH（deepseek-harness` 是子串断言，闭合写法同时满足断言与文档规范性，消除 P6 断言歧义 |
| D-4 | preset.yml 元数据 | name/description/order | 保持 name/description/order 最小集，不新增字段 | 吸收 S-3：name/description 非空是产品级要求非 schema 强制，最小集避免过度设计 |
| D-5 | persona 工具映射与 SKILL.md 表格 | 双份 | 保留双份，统一口径 | P1 [SUGGEST] 第 1 条：persona 内联保证 preset 独立可用（不依赖 skill 加载），SKILL.md 供手动加载；以「编排者四项职责 × DSH 工具」为唯一口径，修改同步 |

## 3. 六项交付物设计

### 交付物 1：`assets/templates/dsh/agent.cordis.yml`（→ BDD-1/2/3）

- **结构**：顶层为行列表（`- id: xxx / name: @deepseek-ai/xxx`），每行非空 `id` 与 `name`（BDD-1）——DSH 装配器按 id/name 解析行。
- **tool-fs-search 行**：必须含 `config.sampleOverCapGlobResults: false`（BDD-2）——DSH schemastery 必填无默认值，缺失 → preset 挂载失败 → fail-closed 拒绝创建会话（2026-08-21 实机缺陷回归）。
- **persona 行（薄身份）**：`config.text` 只写①你是谁（orchestrator，四项职责）②会话开始时按序执行的解析步骤（agate_root / project_root / AGATE_WORKSPACE / 读 orchestrator-template.md / 读 active-tasks.md）③DSH 工具映射（subagent/subagent_fork/read/grep/glob/bash/workflow/ralph/goal）；**必须包含 `{agate_root}/orchestrator-template.md` 路径引用，且不得包含模板首行标题「# Orchestrator（agate 编排 Agent）」**（BDD-3 verbatim 判据）。
- **工具面**：最小集——bash/pwsh（gate 运行面，`!!js process.platform` 平台分支）、fs/fs-search（状态读取）、jobs（长 gate 后台）、skills/tool-skill + skill-filesystem、goal、delegation 组（subagent/subagent_fork/workflow/ralph，`provider: spawn/fork`、`backgroundMode: continuable`）、ask-user、todo。与 standard preset 结构对齐。
- **`!!js` 自定义标签**：保留 `!!js process.platform === 'win32'`（DSH 平台机制），测试用自定义 Loader 容忍（BDD-1 解析容忍）。

### 交付物 2：`assets/templates/dsh/preset.yml`（→ BDD-4）

- `name: agate 编排者`（会话选择器展示项，对应 Claude Code 的 orchestrator 身份）、`description`（非空，一句话说明 P0-P8 编排职责）、`order: 1`。
- 语义边界（吸收 S-3）：name/description 非空是**产品级要求**，不是 DSH schema 强制——缺失仍可挂载（metadata.ts 回退 preset id），测试按产品要求断言非空即可，不做挂载失败类过度设计。

### 交付物 3：`assets/templates/dsh/SKILL.md`（→ BDD-5/6）

- **frontmatter**：`name: agate-protocol` + 非空 `description`（BDD-5）——DSH 技能目录按名发现，安装到 `~/.dsh/skills/agate-protocol/SKILL.md` 才能被按名加载。
- **正文**（BDD-6）：
  - 「编排者四项职责 × DSH 工具」映射表：读状态 → read/grep/glob；派发 subagent → subagent（spawn）/subagent_fork（fork）；跑 gate → bash 按 `[exit code: N]` 判定（不信输出文本）；更新状态 → write/edit。
  - 「平台注意」节四要素：sandbox 只读区（写仓库内文件 Errno 30，任务工作区放可写位置）；/tmp 只读（pytest 用 --basetemp/TMPDIR）；审批策略（禁用时沙箱拒绝即终局，gate 命令不触发需审批操作）；bash 纪律（长命令外层 timeout、读文件用工具不走 bash）。
  - DSH 原生进阶食谱（workflow 批量并行 / ralph 独立 judge / goal 跨轮续跑 / session hooks 实时 gate）——供手动跑 agate 任务的 agent 使用。

### 交付物 4：`SETUP.md`「步骤 2-DSH」小节（→ BDD-7~11）

追加为步骤 2 区最后一个 h3 小节（决策 D-1），内容四要素（与 Claude Code/OpenCode/Windows 小节同构）：

1. **命令块**（BDD-8/9）：`mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol`；三条 `ln -sf ~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml} → ~/.dsh/.agent-presets/agate/`、`SKILL.md → ~/.dsh/skills/agate-protocol/SKILL.md`；`python3 ~/.agate/scripts/install-hook.py`（唯一安装脚本调用）。全仓无 per-platform installer（worktree 已核实无 install-dsh.py，P4 以 grep 复证）。
2. **「身份薄、协议厚」说明**（BDD-10）：persona 只写薄身份、行为规范指向 `{agate_root}/orchestrator-template.md`、不复制模板全文；升级行为——符号链接方式升级后无需操作；Windows/无符号链接权限时退复制模式、升级后重跑 `ln` 对应命令。
3. **使用指引**（BDD-11）：打开 DSH 会话 → 会话选择器选「agate 编排者」（对应 `claude --agent orchestrator`）→ 执行 orchestrator-template.md 的「开始」几步验证。
4. **版本敏感提示**（决策 D-2）：已实机验证（2026-08-21）+ DSH v0.1.0-rc.8 机制可能随版本变化。

### 交付物 5：`platform-notes.md` DSH 条目（→ BDD-12/13/14）

追加 `## DSH（deepseek-harness）` 条目（h2，与既有平台条目同级；决策 D-3）：

1. **能力差异对照表**（BDD-13）：六项能力——orchestrator 身份注册（`.agents/orchestrator.md` 软链 vs agent-preset）、派发 subagent（task vs subagent/subagent_fork）、批量并行派发（手工多路 vs workflow 脚本）、独立复核（手工 fresh context vs ralph）、跨轮续跑（手动重开会话 vs goal）、实时 gate（仅 git hook vs 可挂 session hooks）。
2. **已知注意**（BDD-13）：sandbox 只读区（写仓库内文件 Errno 30）；DSH 无 `.claude/agents/*.md` 等价物——不要试图把 orchestrator-template.md 软链进 DSH 目录，用 preset。
3. **互链引用**（BDD-14）：条目内注明「接入步骤见 `SETUP.md`「步骤 2-DSH」」——接入命令单一真相源，本条目只做能力差异说明（避免命令双份漂移）。

### 交付物 6：`tests/unit/test_dsh_preset.py`（→ BDD-15/16/17）

- **5 个用例**（BDD-15）：① agent.cordis.yml 行结构（每行非空 id/name，容忍 `!!js` 的自定义 YAML Loader）；② tool-fs-search 必填配置回归（`config.sampleOverCapGlobResults is False`）；③ preset.yml name/description 非空；④ SKILL.md frontmatter（name == agate-protocol + description 非空）；⑤ SETUP.md「步骤 2-DSH」章节 + 符号链接命令串在位。
- **平台无关**（BDD-16）：只校验仓库内文件（`agate_root` fixture + pyyaml 解析 + 文本断言）；不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖 `~/.dsh` / 主目录路径——无 DSH 实例的 CI 环境可跑。
- **回归护栏真实性**（BDD-17）：用例 ② 是缺陷回归——agent.cordis.yml 缺失 `config.sampleOverCapGlobResults` 时 FAIL、在位时 PASS（红/绿均可复现，P3 在 worktree 重做 TDD 证明，草稿已红/绿验证）。
- **helper 依赖**：`conftest.py` 的 `agate_root` fixture（L306，从 tests/ 上溯反推 AGATE_ROOT）——与既有 test_*.py 一致。

## 4. BDD-1~19 逐条对照（设计如何满足）

| BDD | 验收判据要点 | 设计满足方式（§3 落点） |
|-----|-------------|------------------------|
| BDD-1 | agent.cordis.yml 合法 YAML 行列表，每行非空 id/name | §3 交付物 1 结构：顶层行列表 + 非空 id/name；测试用例①以 `_js_loader` 容忍 `!!js` 标签解析断言 |
| BDD-2 | tool-fs-search 行 config.sampleOverCapGlobResults: false | §3 交付物 1：必填配置固化；测试用例②精确断言（BDD-17 变异验证同一断言） |
| BDD-3 | persona 薄身份：含 `{agate_root}/orchestrator-template.md` 引用、不含模板首行标题 verbatim | §3 交付物 1 persona 行：指向模板 + 不含「# Orchestrator（agate 编排 Agent）」；测试按子串 + 排除判据可机器断言 |
| BDD-4 | preset.yml 合法 YAML、name/description 非空 | §3 交付物 2：最小元数据集；测试用例③ |
| BDD-5 | SKILL.md frontmatter name: agate-protocol + description 非空 | §3 交付物 3：frontmatter 固化；测试用例④ |
| BDD-6 | 正文含四项职责×DSH 工具映射 + 平台注意四要素 | §3 交付物 3：映射表 + 平台注意节（sandbox 只读 /tmp 只读 / 审批策略 / bash 纪律） |
| BDD-7 | SETUP.md 含「步骤 2-DSH」标题且位于步骤 2 平台章节区 | §3 交付物 4 + 决策 D-1：h3 小节追加在步骤 2 区内（Windows 小节后、步骤 3 前）；测试用例⑤断言标题串 |
| BDD-8 | 章节含 mkdir -p + 三条 ln -sf 命令，源指向 ~/.agate/assets/templates/dsh/ | §3 交付物 4 命令块：精确命令串（mkdir 一行 + 三条 ln -sf + 源路径）；测试用例⑤断言 |
| BDD-9 | 不发明新结构：仅符号链接 + 唯一 install-hook.py；全仓无 per-platform installer | §3 交付物 4 + 影响面 N-1：章节含 `python3 ~/.agate/scripts/install-hook.py` 调用；worktree 已核实 scripts/ 无 install-dsh.py（P4 grep 复证） |
| BDD-10 | 「身份薄、协议厚」表述 + 升级跟随行为（符号链接免操作 / 复制模式重跑） | §3 交付物 4 说明段：含表述 + 两种模式升级行为 |
| BDD-11 | 会话选择器使用指引 + orchestrator-template.md「开始」几步验证 | §3 交付物 4 使用段：「打开 DSH 会话 → 选『agate 编排者』」+「执行 orchestrator-template.md 的『开始』几步验证」 |
| BDD-12 | platform-notes.md 含 DSH 平台条目，与既有条目同级 | §3 交付物 5 + 决策 D-3：`## DSH（deepseek-harness）` h2 条目追加 |
| BDD-13 | 能力差异对照表（六项）+ 已知注意（两条） | §3 交付物 5：六行能力表 + 两条已知注意 |
| BDD-14 | 条目引用 SETUP.md「步骤 2-DSH」为接入单一真相源 | §3 交付物 5 互链段：条目内含 `SETUP.md`「步骤 2-DSH」引用 |
| BDD-15 | test_dsh_preset.py 存在 ≥5 用例且 pytest 全绿 | §3 交付物 6：5 用例覆盖五类断言对象；P3/P5 gate 跑单文件/全量 |
| BDD-16 | 测试平台无关（无 DSH 实例 / 无 ~/.dsh / /tmp 不可写可跑） | §3 交付物 6：只读仓库内文件，四条禁止项写死；P5 在无 DSH 环境全量通过即证明 |
| BDD-17 | 回归护栏有效：缺配置红、在位绿 | §3 交付物 6 用例②：红/绿双态变异可复现；P3 在 worktree 重做 TDD 红→绿（草稿已验证） |
| BDD-18 | 全量回归：pytest 全绿 + consistency 0 ERROR + 用例数不漂移 | §5 gate_commands P5 / P5_consistency / P5_count：基线 1030 钉死（S-4），只增不减 |
| BDD-19 | 触发文件（SETUP.md/platform-notes.md/SKILL.md）commit 携带 self-gate 标记 | 影响面 R-3：commit message 含 `self-gate-review:`/`self-gate-skip:`；P8 按触发面清单核对；test_dsh_preset.py 不触发 |

## 5. gate_commands（P2 固化，P4-P6 不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/test_dsh_preset.py"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 120           # 全量 pytest 分片预期 ~120s（dispatch 指引档位）
  P5_consistency_timeout_seconds: 60
  P5_count_timeout_seconds: 30
```

- **执行工作目录**：worktree 根（`/home/kity/oclab/agate/.worktrees/agate-TAG0018/`，agate/ 为协议本体子目录）。
- **P5 设计要点**（TAG0017 DEBT0012 教训）：三个校验拆成**独立 key**（P5 / P5_consistency / P5_count），各自独立跑、独立记录 pass/fail——**无 `&&` 短路链**；`--strict-errors-only` 只用于 P5_consistency 独立 key，不放任何命令串中间（仅 ERROR 判失败，适合日常任务默认）。
- **P3 不设 `_timeout_seconds`**：P3 走既有 `AGATE_TDD_TIMEOUT` 机制（默认 120s，check-tdd-red.py 消费），timeout_seconds 只服务 P5/其他 key（P2 卡片规则 1）。
- **P5_count 判据**：用例总数 ≥ **1030**（改动前基线，2026-08-21 count-tests.sh 实测钉死，P1-review S-4；TAG0011 迁移下限 749 不受影响）。
- 未声明 formatter：pytest 退化为 exit-code-only（红灯可推进，精度可接受，不阻断）。

## 6. env_constraints（确认 P0-brief，不弱化）

```yaml
env_constraints:
  debug_env: "Linux；DSH 实机验证已完成（2026-08-21：preset 软链安装 → 热发现 → 选择器出现「agate 编排者 · 自定义」→ 设置持久化 → 新会话以 agate 编排者人格启动；tool-fs-search 缺 sampleOverCapGlobResults 缺陷已复现并修复）；CI 无 DSH 实例；worktree 分支 feat/TAG0018-dsh-platform，基线 1028 passed / 0 ERROR（HANDOFF 记录）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh（基线 1030）"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0018-dsh-platform/"
  isolation_check: "测试平台无关性验证：P5 在无 DSH 实例、无 ~/.dsh、/tmp 不可写的 CI 类环境跑全量 pytest 全绿（test_dsh_preset.py 只读仓库内文件，四条禁止项由设计约束 + 测试本身保证）——本字段为声明性信息，强制执行靠 §5 gate_commands（P5 单文件 + 全量）"
```

## 7. files_to_read（P4 实现时的上下文地图）

```yaml
files_to_read:
  - path: agate/SETUP.md:72-144
    why: 步骤 2 平台章节区现状（Claude Code/OpenCode/Windows 小节形态），DSH 小节追加位置与同构参照（BDD-7~11 落点）
  - path: agate/platform-notes.md
    why: 既有平台条目结构（## <平台> + 能力表 + 已知注意），DSH 条目追加参照与互链锚点（BDD-12~14 落点）
  - path: agate/tests/conftest.py:306
    why: agate_root fixture 定义，test_dsh_preset.py 依赖（与既有 test_*.py 一致的路径解析）
  - path: agate/tests/README.md
    why: 脚本→测试映射表补 test_dsh_preset.py 一行（P1 [SUGGEST]，非 gate 强制）
  - path: agate/scripts/install-hook.py
    why: 确认唯一安装脚本存在（BDD-9 断言前置；不改其内容）
  - path: /home/kity/oclab/dsh-workspace/agate-copy/agate/assets/templates/dsh/agent.cordis.yml
    why: 参考实现（非权威）——内容基线（persona 措辞/工具行/必填配置），以 BDD 为准修正（决策 D-2/D-5）
  - path: /home/kity/oclab/dsh-workspace/agate-copy/agate/tests/unit/test_dsh_preset.py
    why: 参考实现（非权威）——测试结构基线（_js_loader/agate_root/5 用例），P3 据此在 worktree 重做红绿
```

## 8. minimal_validation

```yaml
minimal_validation:
  assumption: "方案为纯代码逻辑（仓库内文件结构断言），无外部系统行为依赖——仅依赖 pyyaml（环境已验证 available）解析模板 YAML、pytest/conftest 的 agate_root fixture（tests/conftest.py:306）解析仓库路径、文本子串断言 SETUP.md/platform-notes.md 章节；不调用 DSH、不写 /tmp、不假设符号链接语义、不依赖主目录路径"
  method: "外部平台假设（DSH preset 挂载 / skill 按名发现 / schemastery 必填校验 / 符号链接跟随）已在 2026-08-21 实机验证确认（P0-brief 上游关联证据锚定）；BDD-17 红/绿变异已在 agate-copy 草稿 TDD 验证（缺失 sampleOverCapGlobResults → 测试 FAIL，在位 → PASS）"
  result: "confirmed"
  note: "P3 在 worktree 重做 BDD-17 红/绿（P3 保留理由）；P5 全量 pytest + consistency + count-tests 兜底（BDD-18）；无需新的外部系统最小验证"
```

## 9. 核心约束落实核对

| 核心约束 | 落实 |
|---------|------|
| **不发明新结构** | 平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py（M-4/N-1/R 影响面）；无 platforms/ 目录、无 per-platform installer（worktree 核实 scripts/ 仅 install-hook.py 等，无 install-dsh.py）；`dsh/` 子目录与 `.yml` 文件名是 DSH 平台文件名契约强制（I-1），非发明（P1 §6 S-4 论证） |
| **身份薄、协议厚** | persona 只写薄身份（你是谁 + 会话开始步骤 + DSH 工具映射），行为规范指向 `{agate_root}/orchestrator-template.md`，不复制模板正文（BDD-3 verbatim 判据）；模板随 ~/.agate 升级自动更新（BDD-10 文档说明） |
| **测试平台无关** | test_dsh_preset.py 只校验仓库内文件（agate_root + pyyaml + 文本断言），四条禁止项写死（不写 /tmp / 不假设符号链接语义 / 不调用 DSH / 不依赖主目录路径）→ BDD-16 可兑现 |
| **tool-fs-search 必填配置回归** | BDD-2（配置在位断言）+ BDD-17（红/绿变异验证）双保险；P3 TDD 重做红绿证明护栏真实性 |

## 10. P1-review 建议吸收汇总

| 建议 | 吸收方式 |
|------|---------|
| S-1（BDD-12 标题断言串缺右括号） | 决策 D-3：条目标题用闭合写法 `## DSH（deepseek-harness）`，子串断言通过且无歧义 |
| S-2（P0_STALE 措辞澄清） | 影响面 N-6：P0-brief 保持锁定不物理改动，修正记录于 P1 §0/§7 + BDD-19（本设计不再触碰） |
| S-3（preset.yml 可选元数据语义） | 决策 D-4 + 影响面 R-6：preset.yml 最小元数据集，name/description 按产品级要求断言非空，不做挂载失败类过度设计 |
| S-4（BDD-18 基线数值钉死） | 基线 **1030** 已实测钉死（§5 P5_count 判据 + §6 env_constraints + P2-progress 记录），P6 比对有据 |
| S-5（待实机验证标注处理） | 决策 D-2：移除「待实机验证」陈旧字样，改为已实机验证 + DSH v0.1.0-rc.8 版本敏感提示 |
| [SUGGEST] 1（persona/SKILL 双份映射统一口径） | 决策 D-5：保留双份，以「编排者四项职责 × DSH 工具」为统一口径 |
| [SUGGEST] 2（tests/README.md 补行） | M-7：P4 顺手补 test_dsh_preset.py 一行（文档卫生，非 gate 强制） |

## 11. 完成标准（P4/P5/P6 判定锚点）

做到以下全部才算实现完成：

1. **文件在位**：`assets/templates/dsh/{agent.cordis.yml,preset.yml,SKILL.md}` 三文件存在且合法（BDD-1~6）；`SETUP.md` 步骤 2 区内含「步骤 2-DSH」小节（BDD-7~11）；`platform-notes.md` 含 `## DSH（deepseek-harness）` 条目（BDD-12~14）；`tests/unit/test_dsh_preset.py` 存在（BDD-15）；`tests/README.md` 映射表补行（M-7）。
2. **单文件测试**：`python3 -m pytest agate/tests/unit/test_dsh_preset.py` 收集 ≥5 用例且全绿（BDD-15）。
3. **回归护栏**：变异 agent.cordis.yml 移除 `config.sampleOverCapGlobResults` → 用例② FAIL；恢复 → PASS（BDD-17，P3 红绿证明）。
4. **全量回归**：`python3 -m pytest agate/tests/ -q --tb=no` 全绿 + `check-protocol-consistency.py --strict-errors-only` 0 ERROR + `count-tests.sh` 用例数 ≥1030（BDD-18）。
5. **不发明新结构复证**：worktree 全仓 grep 无 per-platform installer（如 install-dsh.py）（BDD-9）。
6. **self-gate 标记**：含 SETUP.md/platform-notes.md/SKILL.md 的 commit message 带 `self-gate-review:`/`self-gate-skip:`（BDD-19，P8 核对）。

## 12. 风险与缓解汇总

见 §1.3（R-1~R-6，每条配缓解）；核心风险为 R-1（文档-测试漂移，P5/P6 兜底）、R-4（consistency 对新形态扫描，P5_consistency gate 兜底）、R-3（self-gate，commit 标记兜底）。无 blocker 级风险。

## 13. 裁剪说明

沿用 P1 裁剪结论：`phases: [P1, P2, P3, P4, P5, P6, P8]`（跳过 P7）。理由（P1 §5）：交付物全部为新增文件/追加章节，无既有代码路径被修改；P7 跨文件一致性职责已由 test_dsh_preset.py 断言直接替代（BDD-8/15 兜底 SETUP↔模板、BDD-14 兜底 platform-notes↔SETUP）；risk_level: low。本设计不改变该裁剪，且 §4 BDD 对照表本身即 P7 职责的替代性证据面。
