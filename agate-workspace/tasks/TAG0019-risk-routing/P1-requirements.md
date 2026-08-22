---
phase: P1
task_id: TAG0019-risk-routing
type: problems
parent: P0-brief.md
trace_id: TAG0019-P1-20260821
status: draft
created: 2026-08-21
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-protocol, agate-scripts, agate-tests]
domains: [backend, security]
implicit_coupling: true
# ── 标记"已解决/已确认"状态（本阶段无 ──
# need_confirm_resolved: []
# suggest_resolved: []
# scope_resolved: []
---

# TAG0019 风险分路由（ceremony routing，RM-AG0031）— P1 需求基线

> 状态标记：`[PROD_NOT_TOUCHED]`（本任务仅改动 agate 协议本体文件与测试，不涉及任何生产环境，无 [PROD_TOUCHED] 场景）

## 0. P0-brief 时效性质疑记录

已按 P0 卡片判据（严重 3 条 / 轻微 2 条）逐条核对：

- **严重判据 1（task 目标方案不再成立）**：不命中。设计文档 design-risk-routing.md 为 2026-08-21 当日产出，三原则 / 三档表 / M1-M4 节奏与 P0-brief task 字段一致，无推翻性变更。
- **严重判据 2（executor_env 平台前提不再成立）**：不命中。executor_env 声明的 git/本地运行时/网络前提全部成立；platform-notes.md 已登记 DSH 为一等受支持平台（2026-08-21 实机验证），本任务消费的是 git 协议级 gate，与具体编排平台能力正交。
- **严重判据 3（known_risks 的已解决前提被推翻）**：不命中，四类 known_risks 无一被其他任务预先解决。
- **轻微漂移 1 条（记录，不阻塞）**：
  `[P0_STALE: executor_env.platform 声明 opencode，实际编排/验证环境为 DSH（deepseek-harness）。平台-notes.md 已登记支持，gate 脚本为 git 协议级、平台无关，本任务无 opencode 特有能力依赖；建议主 Agent 在 P0-brief executor_env 追加 DSH 兼容备注（platform: opencode + dsh-compatible）]`

**结论**：按"阻塞 / 记录二选一"分流，上条属**轻微漂移 → 记录**，不阻塞 P1，继续推进。

## 1. 需求复述

原始需求（P0-brief task + 设计文档）结构化重写如下：

把任务的"仪式深度（ceremony）"决策从 **agent 自报复杂度**（self-authorization 陷阱：同一个概率模型提出行动又评判它能否进行）改为 **客观信号脚本算分**——由可计算的 git diff 客观事实决定风险分级，压 agate 成本曲线而不降质量地板（薄化的是"仪式"：评审/折叠，不是"验证"：测试/验收）。

**本任务范围（M1-M2 主体 + M3 验收锚，五交付物）**：

| # | 交付物 | 内容 | M 归属 |
|---|--------|------|--------|
| D1 | `agate/scripts/agate-risk-score.py`（新） | 客观信号算分：文件类型 / 敏感路径 / 改动规模（对齐 pruning 源码数≤5 先例）/ 域映射 / 影响面 → risk_score + tier（thin/standard/full）+ 每条信号证据行 | M1 |
| D2 | P1 卡加 `ceremony` 字段（thin/standard/full）+ fail-closed 声明 checklist | 对齐 coupling_checklist 流式格式 + 跳过风险评估 | M1 |
| D3 | check-pruning.py 扩展为 check-routing（或新增 CHECK） | 校验 ceremony 声明 vs risk_score 与 checklist | M2 |
| D4 | requirements-review 角色增"审声明"职责 | 审风险分级/裁剪声明 vs diff 证据（P1 后最便宜独立复核点） | M1 |
| D5 | M3（thin 档跳过 LLM 评审）实证验收锚 | 以 TAG0018"LLM 评审≈0 净收益"为基线，定义前后对比指标（评审轮数 vs 真实发现数），不达标回滚 | M1（锚协议） |

**范围边界（显式声明）**：
- M3 的"thin 档实际跳过 LLM 评审"机制实施**不在本任务**——本任务只交付验收锚度量协议（BDD-12），供后续 M3 任务执行对比；
- M4（dogfood：下一个 low 风险任务走 thin 档）不在本任务；
- "折返优化"配套（subagent 返回前自检 gate、写时 schema 校验联动 RM-AG0022）不在本任务（设计文档 §3.4 标注为配套非主体）；
- P1 requirements-review 是协议硬约束**不可裁**，thin 档的"无 LLM 评审"仅指 P2/P4 的 C8 域触发 LLM 评审（M3 生效后），不涉及 P1 review——两者不冲突。
- P5/P6 不可薄化：thin 档不得裁剪/弱化 P5 验证与 P6 验收——"薄化仪式不薄化验证"由 BDD-7 固化为 thin 档 checklist 要素（P5/P6 保留为四要素之一，缺则回退 standard），并与 check-pruning 既有检查 3（P6 不可裁）+ 检查 5（P5 不可裁）双闸拦截。

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|----------|-----------|
| I1 | `ceremony` 字段必须注册进 frontmatter 机器字段体系 | 不注册则 agate-frontmatter-check.py P1 schema 拦非法值、agate-md-field-get.py 读不出字段、check-routing 无法读取声明——字段"写不进/读不出/校验不了"，机制空转 |
| I2 | check-routing 的挂载点必须落在既有 gate 链 | pre-commit-gate.py 链（2g.2 frontmatter → 2h.1 check-gate → 2j check-pruning → 2k scope）是唯一保证"声明被校验"的执行点；M2 生效必须接进该链或 check-gate 内嵌 |
| I3 | 消费点文档同步防漂移 | agate-summary.py `_DRIFT_SCRIPTS`、scripts/README.md 工具清单、tests/README.md 用例映射、check-protocol-consistency.py 检查项注册、WORKFLOW.md gate 表均引用 check-pruning.py 契约——扩展/改名不同步即一致性 ERROR |
| I4 | thin 档与 phases 裁剪声明正交且 fail-closed 交互 | ceremony 管"仪式深度"、phases 管"阶段去留"，两字段独立；thin 的"≤5 BDD / 无 LLM 评审 / P2 单候选 / P6 快速验收"内的每一项都必须是**逐信号的客观 checklist 确认**，任何一项缺 → 回退 standard |
| I5 | 改动规模信号必须与 pruning 源码数≤5 **同一口径** | 同一"源码文件数"两套定义会导致 P7 裁剪与算分打架（一处 ≤5 可裁、一处 >5 升级），是同类扫描 1 的直接结论 |
| I6 | SELF-GATE 触发面声明（供 P8） | 本任务改动 `agate/**/*.md` 与 `agate/scripts/*.py` 均触发 self-gate；P1 需求列出触发文件清单，P8 才可一轮过 self-gate review。触发文件清单：`agate/scripts/agate-risk-score.py`（新）/`check-pruning.py`/`agate-frontmatter-check.py`/`agate-md-field-get.py`/`pre-commit-gate.py`/`agate-summary.py`/`check-protocol-consistency.py`/`scripts/README.md` + `agate/phase-cards/P1-requirements.md`/`P2-design.md` + `agate/assets/review-roles/requirements-review.md`/`assets/execution-roles/analyst.md`/`assets/templates/task-files.md` + `agate/state-machine.md`/`dispatch-protocol.md`/`role-system.md`/`rules/review-mapping.md`/`WORKFLOW.md`/`CONTEXT.md`/`tests/README.md` + 新增/修改 `agate/tests/*` |
| I7 | 新脚本平台无关（R1-R5 零命中） | agate 测试平台无关原则是核心约束；新脚本做 git diff 路径/行数统计，最容易引入硬编码路径假设。既有拦截 = check-platform-assumptions.py 全树扫描（CI 必跑） |
| I8 | 无存量数据迁移 / 向后兼容 | ceremony 是**新字段存在即生效**：存量 P1 文件无 ceremony 字段 → 默认 standard（fail-closed 兼容），不破坏任何在途任务；无存量数据需迁移 |
| I9 | 文档同步面（多端消费） | ceremony/算分机制说明须同步：P1 卡（声明格式）、analyst.md 角色卡（样例块）、task-files.md 模板（可复制 frontmatter 块）、dispatch-protocol.md（P1 gate 门槛）、requirements-review.md（审声明 checklist）——五处任缺一处即文档漂移 |

## 3. 同类扫描结论（强制节）

> 扫描对象 = **worktree**（`agate-TAG0019/agate/`，改造目标）；稳定版 `~/.agate` 副本与 worktree 基线一致（`git status` 确认协议文件未改）。三组扫描命中数量 + 文件清单 + 逐条判定如下。

### 3.1 扫描 1：check-pruning.py 既有判定逻辑的可复用性（复用不重造）

**命中总数：40 处**（`check-pruning` 字面全仓 grep）。按用途分三类：

**A 类——check-pruning.py 内部可复用函数/判定（直接复用，本次处理）**：

| 符号 | 位置 | 用途 | 判定 |
|------|------|------|------|
| `_md_field(op, p1_file)` | check-pruning.py:30-44 | 经 agate-md-field-get.py 读任何 frontmatter 字段（含 ceremony） | **本次处理**：check-routing 直接复用，不新写读取通道 |
| `_read_p1(p1_file)` | check-pruning.py:47-53 | 读 P1 全文 | **本次处理**：复用 |
| `_staged_source_count(task_dir)` | check-pruning.py:55-81 | git diff --cached 排除任务产出后的源码文件数（改动规模信号 + P7 裁剪共用口径） | **本次处理**：直接复用为算分脚本的"改动规模"信号与 check-routing 校验源，**保证 I5 同一口径** |
| 检查 7 源码数 >5 → 拦截 | check-pruning.py:134-136 | P7 裁剪条件 | **本次处理**：预置"对齐 pruning 源码数≤5 先例"的语义锚（>5 自动高风险级，联动 P7 不可裁） |
| 检查 7 R4(c) coupling_checklist 流式 | check-pruning.py:141-146 | `^coupling_checklist:\s*\[` 流式格式先例 | **本次处理**：thin 档逐信号 checklist 沿用同一流式格式与判据 |
| 检查 9 "跳过风险:" nudge | check-pruning.py:154-157 | 裁剪声明必须含跳过风险评估 | **本次处理**：thin 档申请三要素之一，直接复用该判据 |
| `run_git`（agate_common.py:49） | 全脚本共用 | 平台无关 git 封装 | **本次处理**：算分脚本的 git diff 一律经此通道 |

**B 类——消费 check-pruning 契约的外部点（同步更新，本次处理）**：

| 消费点 | 位置 | 判定 |
|--------|------|------|
| pre-commit-gate.py 链 2j 步 | pre-commit-gate.py:337-339 | **本次处理**：check-routing 挂载点（2j 或 2j 旁），扩展即改此处 |
| WORKFLOW.md gate 表（P8 行 + 2.7 行） | WORKFLOW.md:296,320 | **本次处理**：gate 表补 check-routing 条目 |
| agate-summary.py `_DRIFT_SCRIPTS` | agate-summary.py:37,42 | **本次处理**：脚本改名/新增须同步清单，否则 drift 检测漏 |
| check-protocol-consistency.py 检查项注册 | check-protocol-consistency.py:452-508 | **本次处理**：注册表补"ceremony 校验/风险算分"关键词与 mapping，否则一致性检查不覆盖新机制 |
| scripts/README.md 工具清单 | scripts/README.md:36 | **本次处理**：补 agate-risk-score.py / check-routing 行 |
| tests/README.md 用例映射表 | tests/README.md:31 | **本次处理**：补新测试文件 ↔ 用例数 |
| P7/P3/P4 卡裁剪跳阶引用 | phase-cards/P7:4, P3:4, P4:4 | **本次处理**：thin 档语义变化时对口径（P2 阶段细化） |
| UPGRADING.md 历史记录 | UPGRADING.md:145,179 | **本次不处理**：历史迁移记录，不改写 |

**C 类——测试资产（跟随变更，本次处理）**：`tests/unit/test_check_pruning.py`（29 用例）、`tests/regression/test_v060_r4_cached.py`、`test_v060_p8_internal_only.py`、`tests/integration/test_pre_commit_hook.py`（hook 链用例）、`tests/conftest.py`（fixture/helper，add 字段 helper 需支持 ceremony）。

### 3.2 扫描 2：全仓 risk_level / ceremony / 裁剪 / check-gate 消费点

**ceremony：命中 0 处**（`ceremony` 字面 grep = 0，含 .py 与 .md）→ **确认全新概念，无存量冲突，无需"处理存量同类"**；需从零注册消费链（frontmatter schema → 字段读取 → gate 校验 → 评审）。

**risk_level / C8 消费点（.md 与 .py 分口径，可复现 grep 命令）**——扫描范围 = `agate/**/*.md` 与 `agate/**/*.py`（worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0019/agate`），按匹配行计数：
- `risk_level`（pattern `risk_level`）→ .md **36 处** / .py **70 处**——36 与 .py 70 均与独立实测（评审复核）一致，以下逐域判定以 36 处为口径；
- `C8`（pattern `\bC8\b`）→ .md **20 处**（评审映射机制消费点，与 risk_level 计数分开列）；
- 上版"55 处（.md）"口径更正：为 `risk_level|C8` 两 pattern 合并逐行去重的并集（36 + 20 − 1 = 55，重叠行 P4-implementation.md:86 同含 `risk_level` 与 `C8`）；本版按语义拆分，纯 `risk_level` 口径 = 36，与实测一致。

| 消费点 | 位置 | 判定 |
|--------|------|------|
| agate-frontmatter-check.py P1 schema（required/enums/types） | scripts/agate-frontmatter-check.py:31-50 | **本次处理**：`ceremony` 注册进 allowed + enums（thin/standard/full） |
| agate-md-field-get.py 字段 op 清单 | scripts/agate-md-field-get.py:91,122,187-188 | **本次处理**：`ceremony` 注册为 presence 语义字符串字段 |
| check-pruning.py risk_level 消费（检查 1/6） | check-pruning.py:93,102,128 | **本次处理**：P3 裁剪条件与 ceremony 档位的关系在 P2 定（thin 不豁免 P3 既有条件） |
| check-gate.py P1 gate 函数族 + dispatch-protocol P1 门槛 | check-gate.py:229-311；dispatch-protocol.md:740 | **本次处理**：P1 gate 门槛扩展 ceremony 校验（或由 check-routing 独立承担，P2 定挂载方式） |
| role-system.md C8 映射表 + rules/review-mapping.md + P2 卡评审派发 + P4 卡评审派发 | role-system.md:52-70；rules/review-mapping.md:13-15；P2:182-186；P4:84-86 | **本次处理（M2-M3）**：full 档补强制 plan-eng-review + cso + P7 不可裁；thin 档在 M3 生效后跳过 P2/P4 LLM 评审 |
| WORKFLOW.md 裁剪矩阵 / 评审/门槛表 | WORKFLOW.md:237-263,290 | **本次处理**：裁剪矩阵加档位维度说明，评审表补 full/ceremony 列 |
| dispatch-protocol.md 评审检查项 | dispatch-protocol.md:931 | **本次处理**：评审检查项已有"risk_level 是否与实际风险匹配"——requirements-review 增责的落点即此 |
| requirements-review.md 裁剪合理性清单 | assets/review-roles/requirements-review.md:48-51 | **本次处理**：第 50 行"risk_level 是否与实际风险匹配"升级为"声明 vs diff 证据"逐信号核对（D4） |
| CONTEXT.md 词条 / phase-cards/P1 卡 | CONTEXT.md:19,29；P1 卡:55,178,195 | **本次处理**：词条与卡片补 ceremony 定义；P1 卡 frontmatter 样例块加 ceremony（D2） |
| 测试与 fixture 消费：test_check_frontmatter.py、test_check_pruning.py、test_check_gate.py:1872、conftest.py:79,380、fixtures/full-task、high-risk、paused-task 等 | tests/** | **本次处理**：新字段补 schema/读取/gate 三层测试 + fixture 支持 |

### 3.3 扫描 3：平台差异对 gate 语义的影响（agate-risk-score.py 是否受平台影响）

**结论：agate-risk-score.py 受平台影响，且已有完整拦截链**——判定为"本次处理 + 既有拦截手段已存在，转 BDD-13"：

| 证据 | 位置 | 判定 |
|------|------|------|
| gate 机制为 git 协议级，v0.4 起所有平台统一（pre-commit hook 全平台全功能） | platform-notes.md:49-61 | **本次处理**：算分脚本消费 git diff --cached，属 git 协议级，平台无关前提成立 |
| Windows 原生：gate 脚本全 Python 化（TAG0010），仅 hook 薄壳需 sh；CI windows_smoke 冒烟 | platform-notes.md:85-96,159 | **本次处理**：新脚本须纯 Python、无 bash 依赖 |
| DSH 平台：已登记一等支持（2026-08-21 实机验证），agent-preset 接入，gate 语义不随平台变 | platform-notes.md:174-194 | **本次处理**：无 gate 语义差异 |
| **既有拦截**：check-platform-assumptions.py R1-R5 全树扫描（硬编码 PATH / 裸解释器 / `[[ -L ]]` / 临时目录字面 / 裸外部工具），tests/ 全树 0 命中为 CI 必跑 | tests/scripts/test_check_platform_assumptions.py:6-16,106-114 | **本次处理（回归拦截）**：新脚本自动入扫描面，零命中是硬门槛 → 转 BDD-13 |
| 路径归一化先例：`os.path.relpath(...).replace("\\","/")` | check-pruning.py:66 | **本次处理**：算分脚本路径信号复用此归一化 |
| CRLF 归一化先例：diff 逐行 `.rstrip("\r")` + dispatch-context hash 前 `replace("\r","")` | check-pruning.py:79；pre-commit-gate.py:354-357 | **本次处理**：行数统计信号须 CRLF 鲁棒（Windows autocrlf checkout） |
| 平台无关 git 封装  | agate_common.py:49 `run_git(args, cwd=None)` | **本次处理**：所有 git 调用经此通道，不裸 subprocess |

### 3.4 回归拦截手段汇总（同类问题未来新增的兜底）

| 拦截手段 | 覆盖的同类问题 | 对应 BDD |
|----------|----------------|----------|
| check-platform-assumptions.py 全树扫描（CI）+ windows_smoke | 新脚本引入平台假设 | BDD-13 |
| check-protocol-consistency.py（--strict-errors-only） | 消费点文档漂移（README/卡片/角色/模板不同步） | BDD-15 |
| count-tests.sh 只增不减 | 测试用例数回退 | BDD-15（伴随校验） |
| TDD 红灯先行（P3） | check-routing 判定逻辑回归 | 协议既有机制，随 BDD-7/9 测试 |
| SELF-GATE commit hook（self-gate-review 路径要求） | 协议本体改动未过协议-脚本对齐审查 | I6 触发面清单 |

## 4. BDD 验收条件

> 全部 BDD 为"做完后应表现成什么样"的用户/系统行为（P6 依据），不写实现方案；唯一例外是 D1/D3 的 CLI 契约名（agate-risk-score.py / check-routing）——它们是交付物本身的名称，属契约而非实现细节。

### 客观信号算分（D1）

#### BDD-1: 算分脚本输出三要素
- Given 一个任务目录存在且其暂存区含非空改动（git diff --cached）
- When 运行风险算分脚本对该任务算分
- Then 输出同时包含 risk_score（数值）、tier（thin/standard/full 之一）、每条判据信号及其证据行，且 tier 与各信号证据均与暂存区 diff 内容一致（任一缺失或不一致 = FAIL）

#### BDD-2: 文件类型信号分级
- Given 两类暂存区改动：A 类含 `agate/**/*.md` 或 `agate/scripts/*.py`（协议本体/gate 逻辑），B 类仅含纯 tests/配置类文件
- When 分别运行风险算分脚本
- Then A 类在"文件类型"信号位判为高风险级，B 类判为低风险级，且 A 类信号位评分严格高于 B 类（分级不可区分 = FAIL）

#### BDD-3: 敏感路径信号与 security 域映射
- Given 暂存区改动路径含 security/data/permission/auth/网络请求相关关键词（如 `auth/`、`permission`、`data-model`、外部网络调用文件）
- When 运行风险算分脚本
- Then 输出"敏感路径"信号判为高风险级并给出 security 域映射标记；不含上述关键词的改动无该标记（误报/漏报 = FAIL）

#### BDD-4: 改动规模信号与 pruning 口径一致
- Given 暂存区源码文件数（经任务产出排除后计数，与 check-pruning 的 `_staged_source_count` 同口径）> 5
- When 运行风险算分脚本
- Then "改动规模"信号判为高风险级；对同一暂存区，check-routing 的规模判定与 check-pruning 的 P7 裁剪条件（>5 拦截）不产生矛盾结果（两处口径不一致 = FAIL）

#### BDD-5: 域映射与影响面信号
- Given 改动文件被其他模块经 grep 可见的反向引用，或任务 scope 声明 backend/frontend/mcp/security 任一域
- When 运行风险算分脚本
- Then 输出含域映射标注；存在跨模块反向引用时"影响面"信号升级为高风险级（无反向引用则不升级，升级/不升级两态二值可判）

### ceremony 声明与 fail-closed（D2/D3）

#### BDD-6: ceremony 字段合法值声明
- Given P1-requirements.md frontmatter 含 `ceremony: thin`（或 `standard`/`full`）
- When 该文件过 frontmatter schema 校验与字段读取
- Then 校验通过且字段可被读出；`ceremony: 任意非三值字面`（如 `light`/`THIN`）被判非法并拦截（返回码非 0 = 拦截生效）

#### BDD-7: fail-closed——thin 申请缺任一要素或薄化验证回退 standard
- Given P1 声明 `ceremony: thin`，但满足以下任一情形：缺少"逐信号 checklist"（coupling_checklist 流式格式）、缺少"跳过风险评估"（跳过风险: 声明）、或 phases 声明裁剪 P5/P6 之一（薄化验证/验收）
- When check-routing 校验该声明（P5/P6 情形同时由既有 check-pruning 检查 3（P6 不可裁）+ 检查 5（P5 不可裁）兜底）
- Then 校验不通过（任一校验 exit 1），档位判定回退 standard；仅当"申请（ceremony: thin）+ 逐信号 checklist + 跳过风险评估 + P5/P6 保留（薄化仪式不薄化验证）"四要素齐全时 thin 才成立（任一缺 = FAIL）

#### BDD-8: fail-closed——不声明 = standard 默认
- Given P1-requirements.md frontmatter 无 ceremony 字段（存量或新任务）
- When check-routing 校验
- Then 按 standard 处理且不拦截（exit 0，向后兼容）；任何工具/评审/文档不得把"无声明"解释为 thin 或 full（解释偏差 = FAIL）

#### BDD-9: check-routing 声明 vs 算分一致性（单向 fail-closed）
- Given 同一任务暂存区：agate-risk-score.py 算出 tier=standard 或 full，而 P1 frontmatter 声明 `ceremony: thin`
- When check-routing 校验
- Then 拦截（exit 1，声明档位薄于算分档位）；反向场景（算分 thin 而声明 standard/full，即更保守声明）不拦截（拦截方向与 fail-closed 语义相反 = FAIL）

#### BDD-10: 复用不重造——check-routing 与 check-pruning 同源判定
- Given check-routing 需要"源码文件数 / coupling_checklist 流式 / 跳过风险"三类判定
- When 检查其实现与对同一 P1 输入的对拍结果
- Then 实现直接复用 check-pruning.py 对应逻辑（import 或同函数调用，无重复实现），且对同一输入两者输出判定一致（存在独立重写或结果分叉 = FAIL）

### requirements-review 增责（D4）

#### BDD-11: requirements-review 审声明职责显式化
- Given requirements-review 评审某 P1-requirements.md
- When 检查其检查清单与评审产出
- Then 清单含"风险分级/裁剪声明（risk_level/ceremony/phases）vs 暂存区 diff 证据（文件类型/规模/域）"核对项；声明与 diff 证据不一致时结论为 needs-revision 或 rejected（职责缺失或不一致仍 approved = FAIL）

### M3 实证验收锚（D5）

#### BDD-12: M3 验收锚度量协议定义
- Given 本任务产出的 thin 档机制文档（D2 的 ceremony 字段说明 + D3 的 check-routing）
- When 从机制文档提取 M3 验收锚的度量协议
- Then 协议含全部四要素：①"评审轮数"指标定义；②"真实发现数"指标定义；③TAG0018 基线值（4 场 LLM 评审 ≈0 净收益：17 条非阻塞 + 1 条真实发现且机械检查可抓）；④"不达标（LLM 评审真实发现≈0 且机械 gate 已覆盖）→ 回滚 standard"决策规则（任一要素缺失 = FAIL）

### 平台无关（扫描 3 转 BDD）

#### BDD-13: 新脚本平台假设零命中
- Given 本任务新增/修改的 `agate/scripts/*.py`
- When 运行 check-platform-assumptions.py 对 agate 全树扫描
- Then 扫描 0 命中（R1-R5 无一触发），且新脚本的 git 调用经平台无关通道、路径处理对 Windows 分隔符与 CRLF 行尾鲁棒（任何 R1-R5 命中或裸路径/裸解释器 = FAIL）

### full 档强制项与消费点防漂移（扫描 2 转 BDD）

#### BDD-14: full 档强制评审与 P7 不可裁
- Given 某任务算分 tier=full 或声明 `ceremony: full`
- When P2/P4 评审派发与裁剪检查执行
- Then 该任务 P2 强制独立 plan-eng-review + cso（security 域）评审、P7 不可裁（与 risk_level=high 强制项对齐；任一强制项缺失 = FAIL）

#### BDD-15: 消费点文档同步防漂移
- Given 本任务新增 agate-risk-score.py / 扩展 check-routing（check-pruning.py 契约变化）
- When 运行 check-protocol-consistency.py --strict-errors-only 及检查相关文档
- Then 0 ERROR，且 scripts/README.md 工具清单、tests/README.md 用例映射、agate-summary.py 漂移脚本清单、WORKFLOW.md gate 表均同步反映新机制（任何一处未同步且一致性检查未拦截 = FAIL）

## 5. 裁剪说明与风险分级

- **risk_level: medium**——理由：行为逻辑改动（新增算分脚本 + 扩展 gate 判定）且影响面跨模块（协议卡片/角色/脚本/测试/README 五类消费点联动，I3/I9），但无直接 security/data 风险操作面（敏感路径检测是"读 diff 打标记"而非触达权限/数据变更），不升 high；改动是纯增量新机制（I8 向后兼容），不降 low。按 C8 映射，backend 域 + medium → P2 强制独立 plan-eng-review（role-system.md backend 行）。
- **phases: [P1, P2, P3, P4, P5, P6, P7, P8]（全阶段，无裁剪）**——逐条理由：
  - P1（本阶段）：需求基线，不可裁；
  - P2：方案设计必经（check-routing 挂载方式/算分权重/档位交互需先设计），不可裁；
  - P3：TDD 红灯先行是 HANDOFF 硬约束且 M2 明确要求（"check-routing 拦截 thin 未过 checklist；TDD 红灯先行"），不可裁；
  - P4：实现交付，不可裁；
  - P5：验证，不可裁（thin 档亦不得薄化——P5/P6 保留已由 BDD-7 固化为 thin 档 checklist 要素，缺则回退 standard）；
  - P6：验收（逐条对照本基线 15 条 BDD），不可裁（同上，BDD-7 固化"薄化仪式不薄化验证"）；
  - P7：**不可裁**——本任务声明 `implicit_coupling: true`（frontmatter schema↔字段读取↔gate 校验↔评审清单↔README 五处隐式契约耦合，P7 卡判定此维度必保留），且改动协议本体多文件；
  - P8：agate 自身发布（README badge/CHANGELOG/UPGRADING/版本 tag 清单），不可裁。
- **无裁剪 → 无"跳过风险:"评估条目**（check-pruning 检查 9 仅对存在裁剪时生效）。
- **domains: backend + security**——backend：gate 脚本/算分逻辑；security：敏感路径信号与 cso 评审映射域（扫描 2 中 role-system C8 security 行消费）。

## 6. 能力需求声明

```yaml
capability_requirements: []
```

- 无特殊能力缺口：算分脚本为纯 Python + git 协议级操作（run_git 通道），运行环境具备；测试用 pytest ≥7 + pyyaml + 平台假设扫描器均在现有 CI/本地环境；
- 无 verification_env 声明（无服务/端口/外部系统依赖）；
- domains 不含 frontend → 无视觉能力条目要求（P1 gate `_gate_p1_vision_capability` 不触发）；
- 非环境问题也非能力缺口，不适用 supplementable/GAP 三态。

## 7. 待确认清单

[NO_NEED_CONFIRM]

- 无未决待确认项（负向声明见行首 [NO_NEED_CONFIRM]）：五个交付物边界、fail-closed 语义、范围边界（M3 主体/M4 不在本任务）、risk_level=medium + 全阶段裁剪均由 P0-brief / design 文档 / HANDOFF 明确锁定，无真无方向的人定夺项；
- 既有倾向项（不阻塞，供主 Agent 知悉）：
  - `[SUGGEST: check-routing 实现形态建议扩展现有 check-pruning.py 而非独立新脚本，理由：复用 _md_field/_read_p1/_staged_source_count 同源判定，避免双实现（BDD-10）与消费点双份注册]`——倾向项，P2 architect 定夺；
  - `[SUGGEST: M1 与 M2 合并为同一实现任务（同 commit 批次），理由：D2 的 ceremony 字段若无 D3 校验即无约束力，分开交付会产生"字段已声明但无 gate 保障"的中间态；但 P1-P2 评审与 TDD 红灯仍按阶段执行]`——倾向项，主 Agent 决定任务内节奏。

## 8. 门槛自检

- [x] BDD ≥ 1（15 条，编号连续 BDD-1..BDD-15，格式 `#### BDD-NN:`）
- [x] frontmatter 含 risk_level / phases / packages / domains（机器字段块）
- [x] 含同类扫描结论（三组扫描：命中数 + 文件清单 + 逐条判定 + 回归拦截手段，见 §3）
- [x] P0-brief 时效性质疑记录（§0，1 条轻微漂移已记录，无严重漂移）
- [x] 无行首未决确认标记；capability_requirements 为空列表，无任何阻塞性 GAP 项
- [x] 无掺入方案设计（唯一例外为交付物自身的 CLI 契约名，属边界内）
- [x] 隐含需求 9 条逐条带"为什么必须"（§2）
- [x] 状态标记 `[PROD_NOT_TOUCHED]`（§0 首行）