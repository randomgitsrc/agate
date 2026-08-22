---
phase: P2
task_id: TAG0019-risk-routing
type: design
parent: P1-requirements.md
trace_id: TAG0019-P2-20260821
status: draft
created: 2026-08-21
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 3
packages: [agate-protocol, agate-scripts, agate-tests]
domains: [backend, security]
ui_affected: false
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: static-batch, parallel_limit: 2, batches: [{id: core, complexity: high}, {id: docs-sync, complexity: medium}]}
---

# TAG0019 风险分路由（ceremony routing，RM-AG0031）— P2 方案设计

> 状态标记：`[PROD_NOT_TOUCHED]`（本任务仅改动 agate 协议本体文件与测试，不涉及任何生产环境）。
> 基线：P1-requirements.md 15 条 BDD（BDD-1..BDD-15）approved；本设计覆盖五个交付物 D1-D5（M1-M2 主体 + M3 验收锚，范围边界同 P1 §1）。

## 0. 影响面梳理（强制节）

> 本节省客观证据（grep 命中 / 消费方代码行号 / gate 校验口径），写在候选方案之前。

### 0.1 改什么（Modify）

改动落点分四类：**A 新脚本**（D1/D3 核心）、**B 既有脚本注册点**（ceremony 消费链）、**C 协议文档**（D2/D4/D5 + I3/I9 同步）、**D 测试资产**（C 类跟随）。逐文件 + 关联 BDD 编号如下。

**A. 新脚本（2 个）**

| 文件 | 改动内容 | BDD |
|------|---------|-----|
| `agate/scripts/agate-risk-score.py`（新） | 客观信号算分：四信号分级（文件类型 / 敏感路径 / 改动规模 / 影响面）+ 域映射标注 + risk_score 数值 + tier（thin/standard/full）+ 逐信号证据行。提供可 import 的 `score_task(task_dir) -> dict` + CLI 薄壳 | BDD-1/2/3/4/5 |
| `agate/scripts/check-routing.py`（新，见 §1 候选 B） | ceremony 校验：声明 vs 算分一致性（单向 fail-closed）+ thin 四要素 checklist + 不声明回退 standard。经 pre-commit-gate.py 2j.1 挂载 | BDD-6/7/8/9/10 |

**B. 既有脚本注册点（ceremony 字段消费链，6 处）**

| 文件:位置 | 改动内容 | BDD |
|-----------|---------|-----|
| `agate/scripts/agate-frontmatter-check.py:33,41,43`（P1 schema） | `allowed` 字段表加 `ceremony`；`enums` 增 `ceremony: (thin, standard, full)`；types 增 `ceremony: str`。非法值（`light`/`THIN`）→ exit 1 | BDD-6 |
| `agate/scripts/agate-md-field-get.py:89-127` | `ceremony` 注册为 STRING_FIELDS（presence 语义字符串字段，frontmatter 优先 + 正则回退），check-routing 经 `_md_field("ceremony", p1)` 读取 | BDD-6 |
| `agate/scripts/pre-commit-gate.py:337-339`（2j 步旁） | 新增 2j.1 挂载 `_run_script_rc("check-routing.py", [task_dir])`（gate_exit != 1 时执行），与 2j check-pruning 并列 | BDD-7/9（I2 挂载点） |
| `agate/scripts/agate-summary.py:37,42`（_DRIFT_SCRIPTS） | 清单追加 `agate-risk-score.py`、`check-routing.py`，否则漂移检测漏新脚本 | BDD-15 |
| `agate/scripts/check-protocol-consistency.py:452-508`（关键词注册表） | 追加 `ceremony` / `agate-risk-score.py` / `check-routing.py` 关键词与 script mapping（对齐 check-pruning 既有条目样式） | BDD-15 |
| `agate/scripts/scripts/README.md:36`（工具清单） | 追加 `agate-risk-score.py`、`check-routing.py` 两行（含 CLI 契约与退出码） | BDD-15 |

**C. 协议文档（10 处，D2/D4/D5 + I3/I9 同步）**

| 文件:位置 | 改动内容 | BDD |
|-----------|---------|-----|
| `agate/phase-cards/P1-requirements.md:49-60,62-74`（产出规格 + frontmatter 样例块） | ① 产出规格节增 `ceremony:` 字段条目（thin/standard/full + fail-closed 语义一句）；② frontmatter 样例块加 `ceremony: standard` 行；③ 新增「ceremony fail-closed 声明 checklist」小节（thin 四要素：ceremony 声明 + coupling_checklist 流式 + 跳过风险: + P5/P6 保留缺一回退 standard）+ ④ M3 验收锚度量协议小节（BDD-12 四要素，作为机制文档供提取） | BDD-7/8/12（D2/D5） |
| `agate/assets/review-roles/requirements-review.md:48-52`（裁剪合理性节） | `risk_level 是否与实际风险匹配` 升级为「风险分级/裁剪声明（risk_level/ceremony/phases）vs 暂存区 diff 证据」逐信号核对项：评审时对照 agate-risk-score.py 输出与 diff 文件类型/规模/域，不一致 → needs-revision / rejected | BDD-11（D4） |
| `agate/dispatch-protocol.md:931`（评审检查项） | 同句升级为「风险分级/裁剪声明 vs diff 证据 核对（跑 agate-risk-score.py 对拍）」 | BDD-11 |
| `agate/assets/execution-roles/analyst.md:63-66`（frontmatter 样例块） | 样例块加 `ceremony: standard` 行 + 一句说明（缺省 standard，thin 需申请 + 逐信号 checklist） | BDD-8（I9） |
| `agate/assets/templates/task-files.md:127-160`（P1 frontmatter 块） | 可复制 frontmatter 块加 `ceremony` 行 + 必填/可选说明（可选字段，缺省 standard） | BDD-8（I9） |
| `agate/role-system.md:54-70`（C8 映射表）+ `agate/rules/review-mapping.md:13-15` + `agate/phase-cards/P2-design.md:182-186` + `agate/phase-cards/P4-implementation.md:84-86` | 评审映射补 full 档维度：算分 tier=full 或声明 `ceremony: full` → P2 强制独立 plan-eng-review + cso（security 域）+ P7 不可裁（对齐 risk_level=high 强制项，去重规则同现有 C8 表） | BDD-14 |
| `agate/WORKFLOW.md:237-263`（裁剪矩阵） | 裁剪风险维度节补档位维度说明（ceremony 管仪式深度、phases 管阶段去留，两字段正交；thin 的 P5/P6 保留由 check-routing/check-pruning 双闸兜底） | BDD-7/14 |
| `agate/WORKFLOW.md:296,320`（gate 表） | P8 行与 2.7 行旁补 check-routing 条目（或 2.7.1 行：ceremony 路由校验） | BDD-15 |
| `agate/CONTEXT.md:11,28,29`（词条区） | 新增 ceremony 词条（thin/standard/full + fail-closed 一句），与风险等级词条并列 | BDD-15（I9） |
| `agate/tests/README.md:29-31`（用例映射表） | 追加 `agate-risk-score.py` / `check-routing.py` ↔ 新测试文件↔用例数行 | BDD-15 |

**变更落点说明（ceremony 注册链三节点）**：frontmatter-check（写合法值校验）→ md-field-get（读）→ check-routing（校验语义），三节点必须同步注册，任缺一节点机制空转（P1 I1）。check-gate.py **不内嵌** ceremony 校验（见 §0.2），其 P1/P2 函数族不动。

**D. 测试资产（跟随变更）**

| 文件 | 改动内容 | 关联 |
|------|---------|------|
| `agate/tests/unit/test_agate_risk_score.py`（新） | 算分四信号分级 / tier 合成 / 证据行 / 平台无关（R1-R5）用例（BDD-1/2/3/4/5/13） | D1 |
| `agate/tests/unit/test_check_routing.py`（新） | thin 四要素 fail-closed、不声明=standard、声明薄于算分拦截、与 check-pruning 对拍（BDD-6/7/8/9/10） | D3 |
| `agate/tests/unit/test_check_frontmatter.py` | ceremony enums 非法值拦截补充（BDD-6） | B |
| `agate/tests/unit/test_agate_md_field_get.py` | ceremony 字段读取补充（frontmatter + 正文回退） | B |
| `agate/tests/integration/test_pre_commit_hook.py` | 2j.1 check-routing 挂载链用例 | B |
| `agate/tests/conftest.py:79,380`（fixture helper） | add 字段 helper 支持 ceremony（写 fixture P1 时注入合法 ceremony） | B |
| `agate/tests/regression/test_v060_r4_cached.py`、`test_v060_p8_internal_only.py` | 保持 check-pruning 既有回归断言（方案 B 下不改，仅确认不破） | 回归 |

### 0.2 不改什么（Not Modify）

| 文件/范围 | 不改的理由（客观依据） |
|-----------|----------------------|
| `agate/scripts/check-gate.py` | P1 扫描 2 提出「P1 gate 门槛扩展 ceremony 校验（或由 check-routing 独立承担，P2 定挂载方式）」——本设计**选择由 check-routing 独立承担**：ceremony 语义校验（声明 vs 算分 / checklist）与 P1 gate 的 frontmatter 结构校验是不同职责层，check-routing 挂 pre-commit 链（2j.1）即可在 commit 时全阶段兜底，无需改 check-gate 的 P1/P2 函数族（其既有 4 个 gate 函数与 ceremony 正交）。**不声明 ceremony 的存量任务在 2j.1 下 exit 0，check-gate 路径完全不变，向后兼容面最小** |
| `agate/scripts/check-pruning.py` 既有 8 个检查与契约 | 候选 B（§1）下 check-pruning.py **零改动**：BDD-10 通过 import 同源函数满足，既有消费点（summary/consistency/README/WORKFLOW/tests）全部不动，避免"次生回归面" |
| `agate/state-machine.md` | 档位（ceremony）不改变阶段转移规则：thin 仅薄化仪式（评审/折叠），P5/P6 保留由 check-routing 四要素 + check-pruning 检查 3/5 双闸兜底（BDD-7），无新增状态 / 转移 / PAUSED 语义 → 无需改动 |
| `agate/UPGRADING.md:145,179` 历史迁移记录 | 历史记录不改写（P1 扫描 B 类判定）；仅**新增**当前版本章节记录 ceremony 机制（见 §0.1 C 表注释——UPGRADING 新机制说明归 P8 发布章节，本设计不修改既有历史行） |
| M3 主体（thin 档实际跳过 LLM 评审） | 范围边界（P1 §1）：本任务只交付 D5 验收锚度量协议（BDD-12），thin 跳过评审的机制实现不在本任务 |
| M4（dogfood：low 风险任务走 thin 档） | 范围边界（P1 §1）：不在本任务 |
| 折返优化配套（RM-AG0022 写时 schema 校验 / subagent 返回前自检） | 设计文档 §3.4 标注为配套非主体（P1 §1 范围声明），不在本任务 |
| `agate/WORKFLOW.md:290`（P1-P8 阶段总览表 P2 行评审角色列） | 不处理——评审角色映射的**权威源是 role-system.md C8 表**（:54-70），总览表仅汇总引用；full 档维度只改权威源（role-system / review-mapping / P2 卡 / P4 卡四处），总览表自动反映。P1 §3.2 判定"补 full/ceremony 列"在 P2 审定为**非必要**（改总览表会造成"权威源 + 副本"双源同步风险，NB-4② 交代） |
| `agate/phase-cards/P3-tdd.md:4`、`agate/phase-cards/P7-consistency.md:4`（裁剪跳阶引用行） | 不细化——thin 档"仪式薄化"与阶段"去留"（phases 裁剪）**正交**：thin 的仪式（≤5 BDD / 无 LLM 评审 / P2 单候选 / P6 快速验收）不改变 P3/P7 的阶段存在性语义，两卡既有的跳阶引用不因 ceremony 新机制改写（P1 §3.1 判定"P2 阶段细化"审定**不适用**，NB-4② 交代） |
| `agate/scripts/agate-summary.py:30-40`（_GUARD_SCRIPTS 展示清单） | 不追加新脚本——BDD-15 只要求 `_DRIFT_SCRIPTS`（漂移清单）同步，_GUARD_SCRIPTS 属展示清单可选增强，非阻塞（评审 NB-4③ 微观察） |
| 生产环境 | `[PROD_NOT_TOUCHED]`：无任何部署 / 运行态服务消费 |

### 0.3 风险在哪（Risk）

| # | 风险 | 缓解 |
|---|------|------|
| R1 | **双源判定分叉**：check-routing 与 check-pruning 对同一 P1 输入的规模/流式/跳过风险判定不一致（BDD-10 反例） | 候选 B 下 check-routing **import 同源函数**（`_staged_source_count` / coupling_checklist 流式 / 跳过风险判据），无第二份实现；P3 测试加「对拍用例」：同一 fixture 输入跑两脚本断言判定一致（BDD-10 验收口径） |
| R2 | **ceremony 三节点注册不同步**（frontmatter-check ↔ md-field-get ↔ check-routing），字段"写不进 / 读不出 / 校验不了"（P1 I1） | 每节点注册配独立测试（test_check_frontmatter / test_agate_md_field_get / test_check_routing 各自覆盖）；改一个节点立即跑对应单测，不攒批 |
| R3 | **挂载点遗漏**：check-routing 未进 pre-commit 链，声明校验只在 CI 生效或永不生效（P1 I2） | 2j.1 显式挂载（pre-commit-gate.py:339 后）+ integration 用例断言 hook 链含 check-routing；gate 表（WORKFLOW 2.7 行旁）同步记录 |
| R4 | **算分规则被 exploit**（agent 凑低分声明 thin）：信号是"声明"非客观事实 | 信号全部来自 git diff --cached 客观事实（run_git 通道）+ 单向 fail-closed（声明薄于算分拦截，BDD-9）+ requirements-review 独立审声明（D4）+ thin 四要素 checklist 缺一拦截（BDD-7） |
| R5 | **平台假设漏网**（BDD-13）：新脚本 git diff / 路径统计引入硬编码 PATH / 裸解释器 / 字面 /tmp / Windows 分隔符 / CRLF 行尾 | 全部 git 经 `agate_common.run_git`（:49）；路径 `os.path.relpath(...).replace("\\","/")`（check-pruning:66 先例）；行数统计逐行 `.rstrip("\r")`（check-pruning:79 先例）；P5_platform 命令跑 check-platform-assumptions R1-R5 对**本任务变更文件集**（agate-risk-score.py / check-routing.py + 新增/修改测试文件）扫描 **0 命中**（BDD-13 验收口径；既有 scripts 树存量命中不阻塞，记入评审备查 BLK-1） |
| R6 | **文档漂移**（I3/I9）：五端消费（卡片/角色/模板/评审/README）不同步，一致性检查漏检 | check-protocol-consistency.py 注册表补 ceremony 关键词（§0.1 B 表），P5 跑 `--strict-errors-only` 0 ERROR 硬门槛（BDD-15） |
| R7 | **向后兼容破坏**：存量无 ceremony 任务被新机制拦死 | ceremony **非 required**（frontmatter-check：仅 allowed+enums，不加 required）；check-routing 缺 ceremony → exit 0（BDD-8）；受此保护的任务 = 全部存量在途任务 |
| R8 | **full 档消费遗漏**：算分 tier=full 但 C8 评审映射未触发强制项（BDD-14 反例） | role-system.md / review-mapping.md / P2 卡 / P4 卡四处评审映射同步补 full 档维度；requirements-review 审声明时对拍 tier=full 任务的派发记录 |
| R9 | **影响面信号性能**：跨模块反向引用搜索慢 / 误报 | 扫描对象限定为**暂存区改动文件集**（非全仓文件逐一判）；搜索面限定 repo_root 排除 task_dir/tests 树（§2.1 NB-3 判据），按模块标识正则定位引用行，实现时控制 I/O 范围（P4 细节） |

## 1. 候选方案（candidate_count: 3）

> 分歧点 = **check-routing 的实现形态**（P1 SUGGEST-1 交由 architect 定夺：扩展现有 check-pruning.py 抑或独立新脚本）。三个候选为真实替代方案，非稻草人：分别在某些维度（职责内聚 / 消费点扰动 / 契约语义）上占优。

### 1.1 方案 A：扩展 check-pruning.py 内部加 ceremony 校验（不改名）

- **做法**：在 check-pruning.py 的检查 1-9 后追加「检查 10：ceremony 声明校验」（thin 四要素 + 算分对拍），pre-commit-gate.py 2j 步保持调用 check-pruning.py 不变（或加模式参数）。算分调用 agate-risk-score.py（importlib 或 subprocess）。
- **优点**：
  - 消费点零新增：pre-commit-gate 2j / summary _DRIFT_SCRIPTS / consistency 注册表 / README 工具清单全部保持 check-pruning 单条目，改动面最小；
  - 同源判定天然成立：ceremony 校验与裁剪检查在同一文件内共享全部函数（BDD-10 无 import 依赖负担）；
  - 挂载点不动：2j 行原样，无需新增 2j.1。
- **缺点**：
  - 职责混装：check-pruning 从「裁剪条件检查」膨胀为「裁剪 + 路由」双职责，脚本名（pruning）不再覆盖其语义（routing），长期维护语义漂移；
  - 回归面放大：文件名虽不改，但内部共享 import 图（agate_common / md-field-get）被 ceremony 逻辑触碰，既有 8 个检查的测试回归面变大；
  - 渐进披露矛盾：ceremony 校验是 M2 新机制，混入 v0.60 既有脚本会让"新机制是否生效"难以独立验证（跑一次 2j 分不清是裁剪还是路由在拦）。

### 1.2 方案 B：新增独立 check-routing.py，import check-pruning 同源函数（选择）

- **做法**：新脚本 `check-routing.py` 放在 `agate/scripts/`，经 importlib 加载 `check-pruning.py` 复用 `_md_field` / `_read_p1` / `_staged_source_count` 及 coupling_checklist / 跳过风险判据（见 §2.3），并 importlib 加载 `agate-risk-score.py` 的 `score_task()` 做算分对拍；pre-commit-gate.py 2j 步旁**新增 2j.1** 挂载 `check-routing.py`。
- **优点**：
  - 职责单一：check-pruning（裁剪条件检查）与 check-routing（ceremony 路由校验）是**正交**的两类检查（后者校验"仪式深度声明 vs 客观算分"，前者校验"阶段去留 vs 裁剪条件"），独立脚本各自内聚；
  - 既有契约零扰动：check-pruning.py 文件与 8 个检查**一字不改**，全部既有消费点（summary/consistency/README/WORKFLOW/tests 回归）不动——向后兼容面最小，次生回归风险最低；
  - BDD-10 用 import 满足（BDD-10 明示"import 或同函数调用，无重复实现"），对拍测试保证判定一致；
  - 渐进可验证：无 ceremony 声明的存量任务在 2j.1 下 exit 0（等于没挂），新机制生效与否可由 2j.1 的 exit 独立判定；
  - P2 最小验证已确认技术可行（见 §4 minimal_validation）：importlib 加载 check-pruning 无副作用、函数可调用、空暂存区返回 0。
- **缺点**：
  - 消费点「多一份注册」：summary _DRIFT_SCRIPTS / consistency 注册表 / README 工具清单需追加 check-routing 条目（新增行，非改动既有行，成本低）；
  - 挂载点新增一行（2j.1）：pre-commit-gate.py 多一个 _run_script_rc 调用（与 2j/2k 同模式，无新技术风险）；
  - 两脚本对同一 P1 输入各自跑一次 git diff（开销级，非正确性风险）。

### 1.3 方案 C：check-pruning.py 改名合并为 check-routing.py

- **做法**：将 check-pruning.py 重命名为 check-routing.py（或创建 check-routing.py 且删除 check-pruning.py），裁剪检查 + ceremony 校验合并在一个新命名的脚本中，全部消费点（pre-commit-gate 2j / summary / consistency / README / WORKFLOW / tests）同步改名。
- **优点**：
  - 语义最自洽：脚本名（routing）覆盖全部职责（裁剪是薄化档位的路由子集），check-routing 可视为 check-pruning 的机制泛化（设计文档 §4 原话）；
  - 单一脚本入口：commit 链只跑一个"路由/裁剪"脚本。
- **缺点**：
  - 消费点改名爆炸：`_DRIFT_SCRIPTS`（:37,42）、consistency 注册表（:452-508 约 8 处）、README（:36）、WORKFLOW（:296,320）、pre-commit-gate（:338）、tests（test_check_pruning.py 29 用例 + 回归 2 文件 + integration）全部联动改名，`git log` 历史契约引用（v0.60 文档 "check-pruning.py"）全断——改动面与收益不成比例；
  - 与 P1 I8（向后兼容 / 无存量迁移）冲突：改名是存量消费者可见的破坏性变更，P1 明确要求无存量数据迁移。

### 1.4 权衡与选择理由

| 维度 | 方案 A（扩展不改名） | 方案 B（独立脚本 import） | 方案 C（改名合并） |
|------|----------------------|---------------------------|-------------------|
| 职责内聚 | ✗ 双职责混装 | ✓ 单一职责 | △ 语义自洽但职责大 |
| 既有消费点扰动 | ✗ 内部共享图被触碰 | ✓ 零扰动（仅追加新条目） | ✗ 全量改名 |
| 向后兼容（I8） | ✓ | ✓ | ✗ 破坏性改名 |
| BDD-10 同源 | ✓ 自然 | ✓ import 满足 | ✓ 自然 |
| 可独立验证新机制 | ✗ 混在 2j 内 | ✓ 2j.1 独立 exit | △ 改名后统一 |

**选择：方案 B**。理由：
1. **正交性**（架构判断）：ceremony 路由校验与裁剪条件检查是独立职责层（前者校验"仪式深度声明"，后者校验"阶段去留"），P1 BDD-7/8/9 全部落在"声明 vs 算分/checklist"的**校验语义**上，独立脚本最贴合 BDD 面向；
2. **改动面控制**：方案 B 对既有 8 个检查的消费点**零改动**（这是比方案 A/C 都低的次生回归风险），新增注册均为"追加行"，consistency 0 ERROR 门槛可兜底；
3. **BDD-10 明示允许 import**：同源判定不需物理合并，import + 对拍测试即满足验收口径；
4. **P1 SUGGEST-1 的核心诉求是"复用不重造"而非"物理合并"**：方案 B 完整复用 _md_field/_read_p1/_staged_source_count，满足 SUGGEST-1 意图且避开方案 C 的改名破坏（SUGGEST-2 的"M1/M2 合并节奏"由主 Agent 决策，与脚本形态正交，不影响本选择）；
5. 方案 C 违背 P1 I8（无存量迁移）；方案 A 的"挂载点不动"优点被"职责混装 + 回归面放大"抵消——ceremony 校验是 M2 新机制，若混入既有脚本，2j 的一次失败无法区分是裁剪条件还是路由声明问题，故障诊断语义变差。

## 2. 选定方案详细设计

### 2.1 D1：agate-risk-score.py 信号模型（BDD-1/2/3/4/5）

**输入**：`task_dir`（argv[1]）。读取暂存区 `git diff --cached --name-only`（经 `agate_common.run_git`）+ P1 frontmatter（经 `_md_field`）。

**五信号判定**（每个信号输出：级别 high/medium/low + 证据行；域映射为纯标注不参与 tier）：

| 信号 | 级别判定（客观判据） | 证据行示例 | BDD |
|------|---------------------|-----------|-----|
| 文件类型 | diff 路径命中 `agate/**/*.md` 或 `agate/scripts/*.py` → high；纯 `agate/tests/**` / 配置类 → low；其余 → medium | `file-type: high (agate/scripts/check-pruning.py 属 gate 逻辑)` | BDD-2 |
| 敏感路径 | diff 路径命中关键词 `security|auth|permission|data[-_]?(model|schema)|secret|credential|token|network|socket|api`（实现时按 P1 BDD-3 例子集扩充，含 `auth/`、`permission`、`data-model`）→ high + 输出 security 域标注；无命中 → low | `sensitive-path: high (auth/ 命中) -> domain: security` | BDD-3 |
| 改动规模 | `_staged_source_count(task_dir)`（check-pruning 同口径，排除任务产出）> 5 → high；≤ 5 → low | `change-size: high (source files=7 > 5)` | BDD-4 |
| 影响面 | **反向引用扫描（NB-3 判据精确化）**：对暂存区每个改动文件 F（排除 `agate/tests/` 与配置类），取其模块标识（basename 去扩展名，如 `check-pruning`），在 repo_root 下（**排除 task_dir 与 `agate/tests/` 树**）搜索该标识的引用行（import / from / 调用 / 路径引用形态）；**命中判据 = 存在 ≥1 行引用且该行所在文件非 F 自身** → high；无 → low（二值可判） | `impact: high (module X referenced by 2 other modules)` | BDD-5 |
| 域映射（标注） | P1 frontmatter domains 或敏感路径命中 → 输出 `domain-markers: [backend, security]`（不升级 tier） | `domain-markers: [security]` | BDD-5 |

**tier 合成规则**（二值可判，BDD-2/9 判定口径）：
- 四信号**任一 high → full**；
- 四信号**全 low → thin**（仅候选：还须过 check-routing 四要素 checklist，BDD-7）；
- 其余（存在 medium 或混合）→ **standard**。

**risk_score 数值**（展示用，供 P2/P4 档位报告的数值锚点）：加权和，信号值 high=3 / medium=2 / low=1 × 权重（文件类型 2、敏感路径 2、改动规模 1、影响面 1），范围 4-12。**tier 由 max 分级规则决定，不依赖数值阈值**（避免阈值漂移导致 BDD-9 二值判定模糊）。

**输出**：`risk_score: N` + `tier: thin|standard|full` + 每条信号一行 `key: level (evidence)` + `domain-markers: [...]`（机器可读 + 人可读双形态，BDD-1 三要素齐备）。

**平台无关**（BDD-13）：git 全经 `run_git`；路径 `relpath().replace("\\","/")`；行数统计 `.rstrip("\r")`；无硬编码 PATH / 裸解释器 / 字面 /tmp / 裸外部工具（R1-R5 零命中）。**模块形态**：核心逻辑为可 import 的函数 `score_task(task_dir) -> dict`（供 check-routing 复用），CLI 为薄壳（`if __name__ == "__main__":` 打印 dict）。

### 2.2 D2：ceremony 字段与 fail-closed 声明 checklist（BDD-7/8/12）

P1 卡「产出规格」节 + frontmatter 样例块新增：

```yaml
ceremony: standard        # thin / standard / full，可选；缺省 standard（fail-closed）
```

- **thin 四要素 checklist**（P1 卡"ceremony fail-closed 声明 checklist"小节，逐信号客观确认，对齐 coupling_checklist 流式格式）：
  1. 申请：`ceremony: thin` 显式声明；
  2. 逐信号 checklist：`coupling_checklist: [已检查的耦合点]` 流式声明（`^coupling_checklist:\s*\[` 判据，复用 check-pruning:142）；
  3. 跳过风险评估：`跳过风险:` 声明（复用 check-pruning:156 判据）；
  4. P5/P6 保留：`phases` 含 P5 与 P6（薄化仪式不薄化验证）。
  任一项缺失 → check-routing exit 1，档位回退 standard（BDD-7）；P5/P6 情形同时由既有 check-pruning 检查 3（P6）+ 检查 5（P5）双闸兜底。
- **不声明**（存量/新任务缺 ceremony 字段）→ standard，不拦截（BDD-8）。
- **full 档 P7 声明（BDD-14 声明层保证，NB-1）**：P1 卡 ceremony 说明补「声明 `ceremony: full` 的任务 `phases` 必须含 P7」——与 thin 的 P5/P6 保留要素同构（full 的仪式深度要求阶段完整性，P7 不可裁）；缺 P7 时由 D4 requirements-review 核对项拦截（见 §2.4③）。
- **M3 验收锚度量协议**（BDD-12 四要素，写入 P1 卡同小节作为机制文档供提取）：
  1. 「评审轮数」指标定义：任务在 P2/P4 阶段派发的 LLM 评审 subagent 轮数（含重试轮）；
  2. 「真实发现数」指标定义：评审产出中被采纳或阻止了真实问题的条数（排除非阻塞建议、排除机械检查可抓项）；
  3. TAG0018 基线值：4 场 LLM 评审 ≈0 净收益（17 条非阻塞 + 1 条真实发现且机械检查可抓）；
  4. 不达标决策规则：「LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard」。

### 2.3 D3：check-routing.py 判定流程（BDD-6/7/9/10）

```
读 ceremony = _md_field("ceremony", p1_file)（复用 check-pruning._md_field）
├─ 空 → exit 0（不声明 = standard，BDD-8）
├─ 非法值（非 thin/standard/full）→ exit 1（兜底；frontmatter-check enums 已先拦，BDD-6）
├─ thin →
│   ├─ 四要素全过（coupling_checklist 流式 + 跳过风险 + P5/P6 保留）？否 → exit 1 回退 standard（BDD-7）
│   ├─ 算分对拍：score_task(task_dir).tier ∈ {standard, full} → exit 1（声明薄于算分，单向 fail-closed，BDD-9）
│   └─ 全过 → exit 0
└─ standard / full → exit 0（更保守声明合法，BDD-9 反向不拦；full 强制项由 C8 评审映射消费，BDD-14）
```

- **同源复用（BDD-10）**：importlib 加载 `check-pruning.py` 复用 `_md_field` / `_read_p1` / `_staged_source_count` 与 coupling_checklist 流式判据（`^coupling_checklist:\s*\[`）/ 跳过风险判据（`"跳过风险:" in text`）——**无第二份实现**；P3 对拍用例在同一 fixture 输入上断言 check-routing 与 check-pruning 判定一致。
- **算分调用（与 agate-risk-score.py 的耦合）**：importlib 加载 `agate-risk-score.py`（`spec_from_file_location`，P2 最小验证确认可行）调用 `score_task(task_dir)`——**不 subprocess**（避免输出解析脆弱 + 平台无关性）。
- **挂载**：pre-commit-gate.py 2j.1（:339 后）`_run_script_rc("check-routing.py", [task_dir])`；执行条件与 2j 一致（`gate_exit != 1`）。
- **错误边界分支语义（NB-2）**：
  - ① **P1 缺失分支**：`P1-requirements.md` 不存在（入口 `os.path.isfile` 判定）→ **exit 2**，对齐同链 check-pruning 的 exit 2 语义（无 P1 文件 = 任务目录破损，交人工判断；与"不声明 = standard"的 exit 0 明确区分，避免破损目录静默通过）；
  - ② **算分异常分支（fail-closed，NB-2②）**：`score_task` 内部 run_git 通道失败或 agate_common 不可导入时（`_staged_source_count` 既有静默返回 0 语义），score_task 输出 **`git_ok: false` 标记**（不静默降级）；check-routing 遇 `ceremony: thin` 且 `git_ok: false` → **exit 1**（thin 申请在算分客观信号不可用时**不通过**，回退 standard——防"算分偏薄误放行"的 fail-open 边缘）；`standard` / `full` 声明下 `git_ok: false` 不拦截（更保守声明合法）。

### 2.4 D4：requirements-review 审声明职责（BDD-11）

requirements-review.md「裁剪合理性」节（:48-52）升级为：

- **「风险分级/裁剪声明 vs diff 证据」核对项**（新增，替代原 :50 单句）：
  - 评审流程：读 P1 frontmatter（risk_level / ceremony / phases）+ 对同一暂存区跑 `agate-risk-score.py`，逐信号核对：文件类型（协议本体/gate 逻辑 vs 声明档位）、改动规模（_staged_source_count vs 声明）、域映射（声明 domains vs diff 路径归属）；
  - 结论规则：声明与 diff 证据不一致（如声明 thin 但算分 tier=standard/full、声明 low 但触碰 gate 逻辑/security 路径）→ **needs-revision 或 rejected**；一致 → 可 approved；
  - ③ **full→P7 逐信号核对（NB-1）**：评审清单补「声明 `ceremony: full` → `phases` 含 P7」核对项，`ceremony: full` 而 phases 缺 P7 → 不一致 → needs-revision / rejected（BDD-14 评审层保证）；
  - 产出锚点：评审结论必须引用核对结果行（"ceremony: thin vs tier: standard → 不一致"），延续实质锚点要求。
- dispatch-protocol.md:931 评审检查项同步升级同句。

### 2.5 D5：M3 验收锚度量协议（BDD-12）

见 §2.2「M3 验收锚度量协议」四要素（写入 P1 卡机制文档）。本任务只交付锚协议，不实施 M3 主体（范围边界）。

### 2.6 full 档强制项消费（BDD-14）

算分 tier=full 或声明 `ceremony: full` 的任务：P2 强制独立 plan-eng-review + cso（security 域）+ P7 不可裁。消费点 = role-system.md C8 映射表（:54-61）补 full 维度行 + rules/review-mapping.md（:13-15）+ P2 卡评审派发（:182-186）+ P4 卡评审派发（:84-86）同步声明（与 risk_level=high 强制项同一去重规则）。

**P7 不可裁落地为「声明层 + 评审层」保证（NB-1，删除"通常伴随"推断）**——tier=full 可仅因敏感路径 / 影响面单信号 high 而源码数 ≤ 5（check-pruning 检查 7 按源码数 >5 / implicit_coupling / coupling_checklist 三类条件拦 P7 裁剪，**不覆盖** full 档新增的"P7 不可裁"语义），故不可依赖既有 gate 联动：
- **声明层**：P1 卡 ceremony 说明要求「声明 `ceremony: full` 的任务 `phases` 必须含 P7」（§2.2 D2 补入，与 thin 的 P5/P6 保留要素同构）；
- **评审层**：requirements-review 核对项补「声明 `ceremony: full` → `phases` 含 P7」逐信号核对（§2.4③），不一致 → needs-revision / rejected；
- **check-routing 对 full 声明不新增 gate 拦截**：更保守声明合法（BDD-9 反向不拦）；full 强制项由「声明层 + 评审层 + C8 评审映射」三重保证。

### 2.7 消费点同步（BDD-15）

§0.1 B/C 表所列 6 处脚本注册点 + 10 处文档 + tests/README 用例映射，全部同步本机制；check-protocol-consistency.py 注册表补 ceremony / 新脚本关键词后，`--strict-errors-only` 0 ERROR 即验证同步完整性（任一 END 端未同步 → ERROR 拦截）。

## 3. 测试策略（P3 导航）

- **新测试文件**：`tests/unit/test_agate_risk_score.py`（算分四信号分级 + tier 合成 + 证据行 + BDD-1/2/3/4/5）、`tests/unit/test_check_routing.py`（BDD-6/7/8/9/10 逐条 + 对拍用例 + 分支清单）。
- **check-routing 分支测试清单**（评审测试缺口 2，逐分支列名到 `test_check_routing.py`）：
  - 正向：thin 四要素全过 → exit 0（BDD-7/9 正向）；不声明 → exit 0（BDD-8）；
  - 拦截：缺任一要素 → exit 1（BDD-7）；声明薄于算分（tier=standard/full）→ exit 1（BDD-9）；**算分异常（run_git 失败 / agate_common 不可导入 → `git_ok: false`）+ thin 声明 → exit 1（fail-closed，NB-2②）**；
  - 边界：**P1 缺失 → exit 2（NB-2①）**；非法 ceremony 值 → exit 1（BDD-6 兜底）；
  - 对拍：同 fixture 下 check-routing vs check-pruning 判定一致（BDD-10）+ **importlib 上下文 agate_common 可导入性断言**（评审测试缺口 1——防双层模块 sys.path 依赖静默退化）。
- **full 档声明形态测试**（评审测试缺口 3）：声明 `ceremony: full` 但 phases 缺 P7 → requirements-review 核对项文档条文可 grep 断言（BDD-11/14 联动，NB-1 评审层保证的静态验证）。
- **既有测试扩展**：test_check_frontmatter（ceremony enums）、test_agate_md_field_get（ceremony 读取）、test_pre_commit_hook（2j.1 挂载链）、conftest fixture helper（ceremony 字段注入）。
- **平台无关**（BDD-13）：新测试不得硬编码 /tmp / 裸 python3 / POSIX symlink（遵守 agate 测试平台无关原则，/tmp 只读 → `-p no:cacheprovider --basetemp=...`）。
- **回归**：test_check_pruning.py（29 用例）与 regression 2 文件在方案 B 下不改——P3 确认其仍全绿即回归干净。

## 4. gate_commands / files_to_read / env_constraints / minimal_validation

```yaml
gate_commands:
  P3: "python3 -m pytest -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp"
  P5: "python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp"
  P5_consistency: "python3 /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_platform: "python3 /home/kity/oclab/agate/agate/scripts/check-platform-assumptions.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/scripts/agate-risk-score.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/scripts/check-routing.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/unit/test_agate_risk_score.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/unit/test_check_routing.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/unit/test_check_frontmatter.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/unit/test_agate_md_field_get.py /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/integration/test_pre_commit_hook.py"  # 变更文件集（BLK-1）；清单 = 本任务新增/修改文件，P3 产出后按实际变更文件集调整
  P5_count_tests: "bash /home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 90
```

> 说明：`/tmp` 只读为 DSH 环境硬约束（P0-brief env_constraints）→ pytest 全命令带 `-p no:cacheprovider --basetemp=...`；consistency 用 **worktree 自己的**脚本（检查 worktree 协议文件，dogfooding 约定）；platform 扫描器**只扫本任务变更文件集**（BLK-1 修复）——BDD-13 Given 明示"本任务新增/修改的 `agate/scripts/*.py`"，全树扫描超出验收口径；验收 = 变更文件集 R1-R5 0 命中（exit 0）；**既有 scripts 树存量命中不阻塞**（评审实测证据：agate-install.py:326,330,396 R2 / check-platform-assumptions.py:22,38 自伤 R3/R1 / 3 个 sh hook R2 / pre-commit-gate.py:61 / install-hook.py:128 R2，均落在 §0.2 Not Modify 文件上，无法靠本任务清零，记入评审备查）。

```yaml
files_to_read:
  - path: agate/scripts/check-pruning.py:30-81,134-157
    why: 复用源——_md_field/_read_p1/_staged_source_count + 源码数>5 + coupling_checklist 流式 + 跳过风险判据（importlib 复用）
  - path: agate/scripts/agate_common.py:49-63
    why: run_git 平台无关 git 封装，算分脚本全部 git 调用经此通道
  - path: agate/scripts/agate-frontmatter-check.py:31-50
    why: P1 schema allowed/enums/types——ceremony 注册点
  - path: agate/scripts/agate-md-field-get.py:89-127,187-188
    why: 字段分类表——ceremony 注册为 STRING_FIELDS；现有 risk_level op 先例
  - path: agate/scripts/pre-commit-gate.py:315-343
    why: 挂载点上下文——2j.1 插在 2j（check-pruning）与 2k（scope）之间，执行条件 gate_exit != 1
  - path: agate/scripts/agate-summary.py:37-76
    why: _DRIFT_SCRIPTS 清单——追加新脚本防漂移
  - path: agate/scripts/check-protocol-consistency.py:452-508
    why: 关键词注册表——追加 ceremony/新脚本 mapping
  - path: agate/scripts/scripts/README.md:36 + agate/tests/README.md:29-64
    why: 工具清单/用例映射表格式先例（同步行样式）
  - path: tasks/TAG0019-risk-routing/P1-requirements.md
    why: BDD 基线 15 条权威（BDD-1..15 逐条实现对照）
  - path: agate/assets/review-roles/requirements-review.md:48-52
    why: D4 改写对象——裁剪合理性节格式先例（:50 单句升级为"声明 vs diff 证据"核对项，NB-4①）
  - path: agate/role-system.md:54-70
    why: full 档映射格式先例——C8 映射表行样式（补 full 维度行的参照，NB-4①）
```

```yaml
env_constraints:
  debug_env: "Linux；解释器 /usr/bin/python3；/tmp 只读 → pytest 必须 -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp"
  test_cmd: "（继承 P0-brief）python3 -m pytest agate/tests/（带 basetemp）；check-protocol-consistency.py --strict-errors-only（worktree 自己的）；bash agate/tests/scripts/count-tests.sh"
  isolation_check: "gate 工具/卡片/角色用 ~/.agate 稳定版（=/home/kity/oclab/agate/agate）；改代码/跑测试在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0019）；bash 外层 timeout 30-90s；[PROD_NOT_TOUCHED]"
```

```yaml
minimal_validation:
  assumption: "check-routing 能以 importlib 方式复用 check-pruning 同源函数（_md_field/_read_p1/_staged_source_count），且带连字符模块（agate-risk-score.py）可被 importlib 加载"
  method: "5 行 python 最小脚本：importlib 加载 check-pruning.py 断言三函数 callable + 模块级无副作用；构造空任务目录断言 _staged_source_count=0（fail-closed 兼容路径）；importlib 加载 agate-md-field-get.py 验证带连字符命名加载模式"
  result: "confirmed"
  note: "纯代码逻辑，无外部系统依赖——算分/路由校验全部消费 git diff --cached（run_git 通道）与 P1 frontmatter 文本（agate-md-field-get 读取链），无浏览器/网络/外部服务行为依赖；依赖的内部函数：agate_common.run_git(:49)、check-pruning._md_field/_read_p1/_staged_source_count(:30-81)、check-pruning coupling_checklist/跳过风险判据(:141-157)。最小验证实测：check_pruning_import_ok=True（三函数 callable）、staged_count_empty=0、hyphen_module_import_ok=True → MINVAL_OK"
```

## 5. 实现完成的标志（供 P3/P5 判定）

- [x] `agate-risk-score.py` 存在且对任一任务目录输出 risk_score + tier + 逐信号证据行 + domain-markers（BDD-1）；
- [x] `check-routing.py` 存在，经 pre-commit-gate 2j.1 挂载；thin 缺任一要素 exit 1；不声明 exit 0；声明薄于算分 exit 1（BDD-6/7/8/9）；
- [x] check-routing 对同一 P1 输入与 check-pruning 判定一致（对拍测试绿，BDD-10）；
- [x] frontmatter-check enums 拦 ceremony 非法值；md-field-get 可读出 ceremony（BDD-6 三节点全通）；
- [x] requirements-review 清单含「声明 vs diff 证据」核对项（BDD-11 文档条文可 grep）；
- [x] P1 卡含 ceremony 字段 + fail-closed checklist + M3 验收锚四要素（BDD-7/8/12 机制文档可提取）；
- [x] full 档强制项消费四处同步（role-system / review-mapping / P2 卡 / P4 卡，BDD-14）；
- [x] 全部 gate 命令通过（P3 红灯先行 → P5 pytest 全绿 + consistency 0 ERROR + **platform 变更文件集 0 命中（存量 scripts 树命中不阻塞，评审备查 BLK-1）** + count-tests 只增不减，BDD-13/15）；
- [x] `[PROD_NOT_TOUCHED]`，无生产环境改动。