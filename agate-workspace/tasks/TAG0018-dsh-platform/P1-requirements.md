---
phase: P1
task_id: TAG0018
type: problems
parent: P0-brief.md
trace_id: TAG0018-P1-20260821
status: draft
created: 2026-08-21
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # 增量改动（新模板/文档章节/新测试），不触碰既有协议机制运行时行为；实机验证已完成
phases: [P1, P2, P3, P4, P5, P6, P8]   # 裁剪 P7，理由见「裁剪说明」
packages: [agate]           # 协议本体（交付物为 agate 内 4 个路径 + 1 个新目录）
domains: [cli, docs]        # cli=平台接入/身份注册命令面；docs=文档章节与模板；无 backend/frontend/mcp/security
# ── v2.0 可选字段 ──
design_trivial: true        # P0 已锁定接入方案（符号链接 + preset），P2 只需把草稿结构正式化，无争议候选
follows_existing_pattern:
  - assets/templates/            # 模板目录风格（dsh/ 子目录与 .yml 文件为 DSH 平台文件名契约所必需，见同类扫描）
  - SETUP.md 步骤 2 平台章节形态 # Claude Code / OpenCode / Windows 同构
  - platform-notes.md 平台条目结构 # `## <平台>` + 能力表 + 已知注意
  - tests/unit/test_*.py 命名    # 平台前缀（dsh）命名风格
# ── P7 裁剪必备：显式互链清单（逐项已由 BDD 断言兜底）──
coupling_checklist: ["SETUP.md 步骤 2-DSH 命令 ↔ assets/templates/dsh/ 文件名: checked（BDD-8/BDD-9 断言）", "platform-notes.md DSH 条目 ↔ SETUP.md 步骤 2-DSH: checked（BDD-14 断言）", "test_dsh_preset.py ↔ 模板文件/SETUP.md 章节在位: checked（BDD-15/BDD-17 断言）"]
# ── v2.0 已解决/已确认标记（P1 首次产出留空）──
need_confirm_resolved: []
suggest_resolved: []
scope_resolved: []
---

# P1 需求基线 — agate 原生支持 DSH 平台（TAG0018）

> 本文件是 TAG0018 的活基线（需求唯一真相源）。后续阶段发现的隐含需求以 `[SCOPE+ from Pn]` 回写本文件。

## 0. P0-brief 时效性核对（2026-08-21 执行）

逐条对照 P0 卡片「P0-brief 时效性自检（漂移判据）」严重 3 条 + 轻微 2 条：

| P0-brief 字段 | 对照当前仓库状态 | 判定 |
|---|---|---|
| `task`（目标方案）| 主仓库 `agate/` 无任何 DSH/deepseek-harness 引用，`assets/templates/` 无 `dsh/` 子目录，`tests/unit/` 无 test_dsh_preset.py——目标尚未实现，方案（模板 + 符号链接 + 测试）仍成立 | 无漂移 |
| `issues`（3 条）| ① DSH 用 agent-preset 注册（无 .claude/agents 等价物）——平台机制描述与实机验证一致；② DSH 工具面映射需 SKILL.md——成立；③ 回归测试缺失、tool-fs-search 缺陷——主仓库无该测试，缺陷记录与 2026-08-21 实机复现一致 | 无漂移 |
| `known_risks`（3 条）| ① DSH 新兴平台、CI 无 DSH——仍成立（实机验证已完成属缓解，非前提失效）；② sandbox 只读（Errno 30）——仍成立；③ 改动面触发 SELF-GATE——**表述不精确**：commit-msg-self-gate.py 正则仅匹配 `agate/scripts/*.py` 与 `agate/**/*.md`，`tests/unit/test_dsh_preset.py` 不触发；实际触发文件为 SETUP.md / platform-notes.md / SKILL.md | **轻微漂移（记录）** |
| `executor_env` | platform: opencode、has_task_tool: true、has_local_runtime: true、network: full、git: true——当前 DSH 会话 subagent 工具可用、worktree 分支 `feat/TAG0018-dsh-platform` 在位、git 可用 | 无漂移 |
| `env_constraints` | debug_env（Linux、实机验证已完成、CI 无 DSH）、test_cmd、workspace_path——均成立；HANDOFF-TAG0018 记录 worktree 基线 pytest 全绿 + consistency 0 ERROR | 无漂移 |

[P0_STALE: known_risks 第 3 条将 tests/ 列为 self-gate 触发面不准确——commit-msg-self-gate.py 正则 `^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md|README\.md|AGENTS\.md)$` 不匹配 tests/unit/*.py；本次实际触发文件为 agate/SETUP.md、agate/platform-notes.md、agate/assets/templates/dsh/SKILL.md（agate/**/*.md），test_dsh_preset.py 不触发。已更新该字段描述（见「SELF-GATE 触发面声明」节），轻微漂移，不阻塞 P1]

已核对 P0-brief 时效性：无严重漂移，1 处轻微漂移已记录并按「记录」处理，继续 P1。

## 1. 需求复述

**原始需求（RM-AG0030）**：把 DSH（deepseek-harness）变成 agate 官方支持的第三个平台（继 OpenCode、Claude Code 之后）。

**结构化重述**：DSH 用户应能像 OpenCode/Claude Code 用户一样，通过文档化步骤把 orchestrator 注册为平台可调用的 Agent，并以 agate 编排者人格运行完整 P0-P8 流程。交付物为六项：

1. `assets/templates/dsh/agent.cordis.yml` — orchestrator 的 DSH agent-preset（薄身份 persona + 最小工具面 + 必填配置）
2. `assets/templates/dsh/preset.yml` — preset 展示元数据（会话选择器「agate 编排者」）
3. `assets/templates/dsh/SKILL.md` — agate-protocol skill（DSH 工具映射 + 平台注意 + 进阶食谱）
4. `SETUP.md`「步骤 2-DSH」章节 — 符号链接接入步骤（与 Claude Code/OpenCode 步骤 2 同构）
5. `platform-notes.md` DSH 平台条目 — 能力差异对照 + 已知注意
6. `tests/unit/test_dsh_preset.py` — 回归测试（守护 preset 必填配置与文档在位，平台无关）

**问题与方案分离**：P1 只定义"做完什么样算对"（上列六项 + 下述 BDD），不设计 persona 措辞、工具行顺序等实现细节——那些是 P2/P4 的职责。

## 2. 隐含需求识别

用户没说、但技术上必须做或必须遵守的依赖（逐条附"为什么必须"）：

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| I-1 | **DSH 平台文件名契约**：三个模板文件必须原样命名为 `agent.cordis.yml` / `preset.yml` / `SKILL.md`（不按 agate 模板命名风格改名） | DSH 装配器按固定文件名发现 preset 与 skill（`~/.dsh/.agent-presets/agate/`、`~/.dsh/skills/agate-protocol/SKILL.md`），改名即无法挂载；这是外部平台契约，不属于"发明新结构" |
| I-2 | **符号链接跟随性与复制模式退化路径**：文档须说明无符号链接权限环境（Windows/受限容器）的复制模式与升级后重跑 | SETUP.md 既有 Windows 章节先例；DSH 发现机制跟随软链（2026-08-21 实机验证确认），但不给退化路径则部分用户接入失败无指引 |
| I-3 | **身份薄、协议厚**：persona 只写薄身份，行为规范指向 `{agate_root}/orchestrator-template.md`，不得复制模板全文 | 模板随 `~/.agate`（→ 仓库软链）升级自动更新；复制会导致升级不同步（SETUP.md 已记录复制模式代价）；等价官方符号链接性质 |
| I-4 | **tool-fs-search 必填配置**：`config.sampleOverCapGlobResults: false` 必须保留并固化进回归测试 | DSH schemastery 校验该字段为必填且无默认值，缺失 → preset 挂载失败 → DSH fail-closed 拒绝创建会话（2026-08-21 实机复现并修复） |
| I-5 | **测试平台无关**：test_dsh_preset.py 只校验仓库内文件，不依赖真实 DSH 实例、不写 /tmp、不假设符号链接语义 | CI 无 DSH 实例（P0-brief env_constraints 明确）；依赖真实实例的测试必然 CI 红 |
| I-6 | **不发明新结构**：平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py；不引入 `platforms/` 目录、不引入 per-platform installer | agate 既有平台接入原则；install-dsh.py 已废弃（per-platform installer 路线失败过）；发明新结构破坏一致性、增加维护面 |
| I-7 | **文档互链与接入步骤单一真相源**：接入命令只维护在 SETUP.md「步骤 2-DSH」，platform-notes.md 只做能力差异说明并引用它 | 同一命令两处维护必然漂移（命令改一处漏一处） |
| I-8 | **SELF-GATE 触发**：改动 `agate/**/*.md` 的 commit 须携带 `self-gate-review:` / `self-gate-skip:` 标记 | 协议自身变更纪律（SELF-GATE.md + commit-msg-self-gate.py）；同时修正 P0-brief 对 tests/ 的误列（见第 0 节） |
| I-9 | **全量回归底线**：新增文件后 `agate/tests/` 全量 pytest 全绿 + `check-protocol-consistency.py --strict-errors-only` 0 ERROR + count-tests 只增不减 | AGENTS.md 开发命令 + CI（protocol-tests.yml）自动执行；红则 CI 失败，破坏"Linux 现状是基线"（HANDOFF 核心约束 1） |
| I-10 | **与既有平台章节同构**：SETUP.md 步骤 2-DSH 的形态（命令块 + 注意 + 验证指引）与 Claude Code/OpenCode 小节一致；platform-notes 条目结构（`## <平台>` + 能力表 + 已知注意）与既有条目一致 | 读者按既有文档路径与心智模型找到并理解 DSH 接入；同类扫描结论见第 6 节 |
| I-11 | **数据/存量影响**：**无**——交付物全部为新增文件（dsh/ 目录、test_dsh_preset.py）与文档追加章节（SETUP.md / platform-notes.md 追加），无存量数据迁移、无既有文件内容改写 | 显式声明"无"，防止后续误以为需要迁移步骤 |
| I-12 | **边界：无符号链接权限**（Windows 受限环境）→ 复制模式退化 + 升级后重跑指引 | 并入 I-2；agate 官方支持 Windows（platform-notes 已记录），DSH 接入指引不能只覆盖 Linux |

## 3. BDD 验收条件

每条 BDD 可二值判定（PASS/FAIL），是 P6 验收的逐条兑现依据。

### 交付物 1：assets/templates/dsh/agent.cordis.yml（orchestrator agent-preset）

#### BDD-1: agent.cordis.yml 是合法 YAML 行列表，每行含非空 id 与 name
- Given 仓库内存在 `assets/templates/dsh/agent.cordis.yml`
- When 用 YAML 解析该文件（容忍 `!!js` 自定义标签）并检查顶层结构与每行字段
- Then 解析成功、顶层为行列表、每一行含非空 `id` 与 `name`（DSH 装配器按 id/name 解析行，缺字段导致挂载失败）

#### BDD-2: tool-fs-search 行带 config.sampleOverCapGlobResults: false（实机缺陷回归）
- Given agent.cordis.yml 中存在 `id: tool-fs-search` 的行
- When 检查该行的 config
- Then `config.sampleOverCapGlobResults` 为 `false`（DSH schemastery 必填无默认值，缺失 → preset 挂载失败 → fail-closed 拒绝创建会话）

#### BDD-3: persona 是薄身份——指向 orchestrator-template.md 而非内嵌模板正文
- Given agent.cordis.yml 的 persona 行
- When 检查 persona.text 内容
- Then 文本包含 `{agate_root}/orchestrator-template.md` 路径引用，且不包含模板正文的 verbatim 片段（判据：模板首行标题「# Orchestrator（agate 编排 Agent）」不出现在 persona 中）——行为规范指向模板、模板随 ~/.agate 升级自动更新，preset 不复制模板全文

### 交付物 2：assets/templates/dsh/preset.yml

#### BDD-4: preset.yml 是合法 YAML 且含非空 name 与 description
- Given 仓库内存在 `assets/templates/dsh/preset.yml`
- When 用 YAML 解析并检查字段
- Then 解析成功且 `name` 与 `description` 均为非空字符串（DSH GUI 会话选择器据此展示「agate 编排者」）

### 交付物 3：assets/templates/dsh/SKILL.md（agate-protocol skill）

#### BDD-5: SKILL.md frontmatter 含 name: agate-protocol 与 description
- Given 仓库内存在 `assets/templates/dsh/SKILL.md`
- When 解析其 frontmatter 块
- Then `name` 等于 `agate-protocol` 且 `description` 非空（DSH 技能目录按名发现，安装到 `~/.dsh/skills/agate-protocol/SKILL.md` 才能被按名加载）

#### BDD-6: SKILL.md 正文含 DSH 工具映射与平台注意
- Given SKILL.md 正文
- When 检查正文内容
- Then 包含「编排者四项职责 × DSH 工具」映射（读状态 → read/grep/glob、派发 → subagent/subagent_fork、跑 gate → bash 按 `[exit code: N]` 判定、更新状态 → write/edit）与「平台注意」节（sandbox 只读区、/tmp 只读、审批策略、bash 纪律）——任何想在 DSH 上手动跑 agate 任务的 agent 加载本 skill 即获得适配层全部要点

### 交付物 4：SETUP.md 步骤 2-DSH

#### BDD-7: SETUP.md 含「步骤 2-DSH」章节
- Given SETUP.md 已存在（当前含步骤 2 的 Claude Code/OpenCode/Windows 平台小节）
- When 检查章节标题
- Then 存在标题「步骤 2-DSH」，且位于步骤 2 平台章节区（与既有平台小节同构，用户按既有路径可找到）

#### BDD-8: 章节含符号链接安装命令，指向模板文件与 DSH 安装目标
- Given SETUP.md 的「步骤 2-DSH」章节
- When 检查章节内命令块
- Then 含 `mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol` 与三条 `ln -sf`：`agent.cordis.yml`、`preset.yml` → `~/.dsh/.agent-presets/agate/`、`SKILL.md` → `~/.dsh/skills/agate-protocol/SKILL.md`，源路径均指向 `~/.agate/assets/templates/dsh/`——用户照抄命令即可完成注册

#### BDD-9: 不发明新结构——安装仅符号链接 + 唯一 install-hook.py
- Given SETUP.md 的「步骤 2-DSH」章节与仓库 scripts/ 目录
- When 检查安装指引与脚本清单
- Then 章节含 `python3 ~/.agate/scripts/install-hook.py`（唯一安装脚本）调用，且全仓无任何 per-platform installer（如 `install-dsh.py`）文件或引用——平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py

#### BDD-10: 章节含「身份薄、协议厚」说明与升级跟随行为
- Given SETUP.md 的「步骤 2-DSH」章节
- When 检查说明文字
- Then 含「身份薄、协议厚」表述（persona 指向 orchestrator-template.md、不复制模板全文），并说明升级行为：符号链接方式升级后无需操作；无符号链接权限时退复制模式、升级后重跑 `ln` 对应命令

#### BDD-11: 章节含使用与验证指引
- Given SETUP.md 的「步骤 2-DSH」章节
- When 检查使用说明
- Then 含「打开 DSH 会话、在会话选择器选「agate 编排者」」的使用指引（对应 Claude Code 的 `claude --agent orchestrator`），并指引执行 orchestrator-template.md 的「开始」几步验证

### 交付物 5：platform-notes.md DSH 条目

#### BDD-12: platform-notes.md 含 DSH 平台条目
- Given platform-notes.md 已存在（含 OpenCode/Claude Code/Windows 等条目）
- When 检查条目标题
- Then 存在「## DSH（deepseek-harness」平台条目，与既有平台条目同级（结构对齐）

#### BDD-13: DSH 条目含能力差异对照表与已知注意
- Given platform-notes.md 的 DSH 条目
- When 检查条目内容
- Then 含与 OpenCode/Claude Code 的能力差异对照表（身份注册 / 派发 subagent / 批量并行 / 独立复核 / 跨轮续跑 / 实时 gate）与「已知注意」节（sandbox 只读区；DSH 无 `.claude/agents/*.md` 等价物、不要试图把 orchestrator-template.md 软链进 DSH 目录、用 preset）

#### BDD-14: DSH 条目引用 SETUP.md「步骤 2-DSH」为接入步骤单一真相源
- Given platform-notes.md 的 DSH 条目
- When 检查互链引用
- Then 条目包含指向 `SETUP.md`「步骤 2-DSH」的引用（接入步骤只维护一处，platform-notes 只做能力差异说明，避免命令双份漂移）

### 交付物 6：tests/unit/test_dsh_preset.py

#### BDD-15: 测试文件存在且 ≥5 用例，pytest 全绿
- Given 仓库内存在 `tests/unit/test_dsh_preset.py`
- When 运行 `python3 -m pytest tests/unit/test_dsh_preset.py`
- Then pytest 收集 ≥5 个用例且全部通过，覆盖：agent.cordis.yml 行结构（id/name）、tool-fs-search 必填配置、preset.yml name/description、SKILL frontmatter、SETUP.md 章节与命令在位

#### BDD-16: 测试平台无关——无 DSH 实例的 CI 环境可跑
- Given 无真实 DSH 实例、无 `~/.dsh` 目录、/tmp 不可写的 CI 环境
- When 运行 `python3 -m pytest tests/unit/test_dsh_preset.py`
- Then 全部通过（测试只校验仓库内模板文件：不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖用户主目录路径）

#### BDD-17: 回归护栏有效——移除必填配置用例红，恢复用例绿
- Given test_dsh_preset.py 中的 tool-fs-search 回归用例（对应 BDD-2）
- When 分别对「agent.cordis.yml 缺失 `config.sampleOverCapGlobResults`」与「配置在位」两种状态运行该用例
- Then 配置缺失时该用例 FAIL、配置在位时该用例 PASS（红/绿均可复现）——证明测试真实守护 2026-08-21 实机缺陷而非空断言

#### BDD-18: 全量回归——agate/tests/ 全绿 + consistency 0 ERROR + 用例数不漂移
- Given 六项交付物落位后的 worktree（分支 feat/TAG0018-dsh-platform）
- When 运行 `python3 -m pytest agate/tests/`、`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`、`bash agate/tests/scripts/count-tests.sh`
- Then 全量 pytest 全绿、consistency 0 ERROR、测试用例总数 ≥ 改动前基线（只增不减）——"Linux 现状是基线"回归底线不破

### SELF-GATE 触发面（P8 核对用）

#### BDD-19: 触发文件入暂存区的 commit 携带 self-gate 标记
- Given 本次改动触发的 self-gate 文件清单：`agate/SETUP.md`、`agate/platform-notes.md`、`agate/assets/templates/dsh/SKILL.md`（`agate/**/*.md`）
- When 提交含上述任一文件的 commit
- Then commit message 含 `self-gate-review: <路径>` 或 `self-gate-skip: <理由>`（协议既有机制，P8 按本清单核对触发面覆盖；`tests/unit/test_dsh_preset.py` 不触发 self-gate）

## 4. 待确认清单

[NO_NEED_CONFIRM] — 无方向性待确认项：接入方案（符号链接 + preset）、身份薄协议厚、测试平台无关、不发明新结构等方向性选择均已被 P0-brief 锁定并有实机证据，P1 无需人定夺。

倾向项（主 Agent 可直接采纳，不阻塞）：

- [SUGGEST: persona 内联工具映射与 SKILL.md 表格保持双份、以「编排者四项职责 × DSH 工具」为统一口径——persona 内联保证 preset 独立可用（不依赖 skill 加载），SKILL.md 供手动加载与食谱扩展；修改映射时两处同步。理由：实机验证 persona 自带映射可独立启动会话，双份是刻意设计而非重复]
- [SUGGEST: P4 时在 tests/README.md 的脚本→测试映射表补 test_dsh_preset.py 一行——文档卫生，非 gate 强制（count-tests.sh 用 pytest collect-only 计数，不受该表影响）]

## 5. 裁剪说明

**复杂度判定**：小任务（新增模板 + 文档章节 + 独立测试文件，无既有代码路径修改，风险 low）。

**phases: [P1, P2, P3, P4, P5, P6, P8]**（跳过 P7）：

| 阶段 | 处理 | 理由 |
|------|------|------|
| P1 需求基线 | 保留 | 核心阶段不可裁 |
| P2 设计 | 保留 | 核心阶段不可裁；`design_trivial: true`（P0 已锁定接入方案，模板结构由 DSH 平台契约 + standard preset 对齐决定，P2 只需 1 个候选方案） |
| P3 TDD | 保留 | test_dsh_preset.py 先写失败测试确认红、实现后确认绿（BDD-17）是回归护栏有效性的证明；草稿已红/绿验证，P4 在 worktree 重做 |
| P4 实现 | 保留 | 核心阶段不可裁 |
| P5 验证 | 保留 | 核心阶段不可裁；跑测试 + consistency + count-tests |
| P6 验收 | 保留 | 核心阶段不可裁；19 条 BDD 逐条实跑 |
| **P7 一致性** | **跳过** | ① 交付物全部为**新增文件**（dsh/ 目录、test_dsh_preset.py）与**文档追加章节**（SETUP.md / platform-notes.md 追加），无既有代码路径被修改，无隐式耦合（frontmatter `coupling_checklist` 已列显式互链并逐项 checked）；② P7 的跨文件一致性职责已由测试断言直接替代——test_dsh_preset.py 断言 SETUP.md 章节/命令与模板文件在位（BDD-8/BDD-15），platform-notes↔SETUP 互链由 BDD-14 断言；③ risk_level: low，改动为增量非破坏性。跳过风险:测试断言与文档实现不一致（如命令串拼写漂移）——由 BDD-8/BDD-15 在 P5/P6 兜底，P4 实现时以 BDD 为准 |
| P8 发布 | 保留 | 官方第三平台是面向用户的对外功能，需发版：README badge / CHANGELOG `[Unreleased]` 含 TAG0018 / UPGRADING 章节 / release PR 普通 merge（--no-ff，禁止 squash） |

## 6. 同类扫描结论（强制节）

扫描动作：grep/find 全仓（主 checkout + worktree）关键符号与结构，记录命中数与文件清单，逐条判定：

| # | 扫描项 | 扫描结果 | 判定 |
|---|--------|---------|------|
| S-1 | `platforms/` 目录 | 主 checkout 与 worktree 均 **0 命中**（`find -type d -name platforms` 空） | 无先例可复用；确认"不发明新结构"约束的可执行面（无 platforms/ 目录可照抄，也不新建） |
| S-2 | per-platform installer（install-dsh.py 等）| `grep -rn "install-dsh"` 主 checkout 与 worktree 均 **0 命中**；scripts/ 仅 `install-hook.py` / `agate-install.py` / `install-offline.py` | install-dsh.py 已废弃且已从仓库清除；唯一安装脚本 = install-hook.py——本任务不得引入任何新安装脚本（BDD-9 固化） |
| S-3 | 主仓库 DSH/deepseek-harness 引用 | `grep -rln "deepseek-harness\|dsh"` agate/ **0 命中** | 本任务是从零引入 DSH 支持，无既有形态可对齐；文档/模板/测试全部为新增 |
| S-4 | `assets/templates/` 命名风格 | 13 个文件全部 kebab-case `.md`、平铺（无子目录、无 .yml/.yaml 先例）| 既有风格 = kebab-case .md 平铺；`dsh/` 子目录与 `.yml` 文件是**本任务新增形态**，但由 DSH 平台文件名契约强制（agent.cordis.yml / preset.yml 是 DSH 发现机制固定名），属外部约束而非"发明新结构"——BDD-1/BDD-4 固化文件名 |
| S-5 | SETUP.md 步骤 2 平台章节形态 | 步骤 2 下 Claude Code / OpenCode / Windows 三小节，每节 = 符号链接命令块 + 验证命令 + 注意/副作用说明 | DSH 章节与既有小节同构对齐（BDD-7~11 固化命令块 + 说明 + 使用指引三要素） |
| S-6 | platform-notes.md 平台条目结构 | 既有条目（OpenCode/Claude Code/Claude Project/Windows）均为 `## <平台>` + 能力表 + 已知注意/适用范围 | DSH 条目沿用该结构（BDD-12/BDD-13 固化） |
| S-7 | tests/unit/ 测试命名 | 既有 test_*.py（test_agate_*.py / test_check_*.py / test_dispatch_*.py 等），无 DSH 前缀先例 | 新文件 `test_dsh_preset.py` 命名符合 `test_<subject>_*.py` 风格（平台前缀 dsh）；tests/README.md 映射表为文档性（check-protocol-consistency.py 不校验该表），P4 顺手补行（见 [SUGGEST]） |
| S-8 | 平台身份注册先例（custom-role.md）| `assets/templates/custom-role.md` 是 OpenCode 自定义角色模板（--custom-role 路线，platform-notes 已记 OpenCode 该能力不可用，issue #29616）| 与 DSH agent-preset 是**不同机制**，不构成 DSH 接入的可复用先例；DSH 用 preset 是新形态但由平台机制决定，不冲突 |

**回归拦截**：同类问题（平台接入结构）未来新增平台时还会出现——拦截手段 = ① SETUP.md 步骤 2 平台章节形态约定（新平台章节照此形态写）；② platform-notes 条目结构约定；③ 本任务 BDD-9（不发明新结构）作为文档约定由 P6 验收守护。结论已落盘本节，非只写 progress。

## 7. SELF-GATE 触发面声明（P8 参考）

- **触发文件**（本任务改动且命中 commit-msg-self-gate.py 正则）：`agate/SETUP.md`（`agate/[^/]+\.md`）、`agate/platform-notes.md`（同上）、`agate/assets/templates/dsh/SKILL.md`（`agate/.+/.*\.md`）
- **不触发**：`agate/tests/unit/test_dsh_preset.py`（`.py` 但不在 `agate/scripts/` 下，正则不匹配）——已修正 P0-brief known_risks 第 3 条误列
- **处理**：含触发文件的 commit message 须含 `self-gate-review: <路径>` 或 `self-gate-skip: <理由>`；self-gate 流程本身是协议既有机制，本任务不新增，P8 按 BDD-19 核对触发面覆盖

## 8. 能力需求声明

```yaml
capability_requirements:
  - need: yaml-structure-validation
    why: 校验 agent.cordis.yml（含 `!!js process.platform` 自定义标签）与 preset.yml 的结构与必填字段（BDD-1/BDD-2/BDD-4）
    available:
      - "pyyaml（环境已验证：pytest 9.0.3 + pyyaml，worktree 基线全绿）"
      - "草稿 test_dsh_preset.py 已实现自定义 YAML Loader 容忍 !!js 标签（agate-copy，TDD 红/绿验证通过）"
    status: available

  - need: doc-text-assertion
    why: 断言 SETUP.md / platform-notes.md 章节标题、命令串、互链引用在位（BDD-7~14）
    available:
      - "纯文本断言（str in text / 正则），无外部依赖"
    status: available
```

**判断树说明（verification_env vs supplementable）**：本任务验收路径 = **仓库内文件断言**（python3 + pyyaml + pytest，均已就绪），无运行环境依赖，故不声明 `verification_env`。真实 DSH 实例验证**不作为能力 need 声明**——① 2026-08-21 已在 DSH GUI 实机完成（preset 软链安装 → 热发现 → 选择器出现「agate 编排者 · 自定义」→ 设置持久化 → 新会话以 agate 编排者人格启动；并发现/修复 tool-fs-search 缺陷），证据锚定 P0-brief 上游关联；② CI 无 DSH 是既定约束（P0-brief env_constraints），测试平台无关原则（P0-brief 强制要求）明确把真实实例验证排除在交付物之外——将"真实 DSH 验证"列为 need 只会得到 GAP，属机制误用（TAG0009 教训：环境/约束问题不标能力三态）。`domains` 不含 frontend，无视觉能力条目要求。
