---
phase: P4
task_id: TAG0021-structured-layer
type: review
parent: P4-implementation.md
trace_id: TAG0021-P4-20260822
status: approved
created: 2026-08-22
agent: protocol-alignment-review
---

# SELF-GATE 审查报告 — TAG0021 P4（协议-脚本对齐）

> 审查角色：protocol-alignment-review（独立上下文，只读审查对象，唯一写操作：本报告 + P4-review-progress.md）
> 审查对象：TAG0021 P4 实现改动面（TAG0021-structured-layer M0-M3）
> 状态标记：`[PROD_NOT_TOUCHED]`（主 checkout `~/.agate` 稳定版零改动；worktree 仅审查不修改实现文件）
> 核验方式：上一轮实测（真实树 gate 实跑 + 全量 pytest + git diff 逐文件对照）+ 本轮引用核验

## 审查结论汇总

| # | 审查要点（dispatch-context） | 结论 |
|---|------------------------------|------|
| 1 | 新脚本与既有协议约定对齐（编号空间/输出格式/退出码/--strict-errors-only/agate_common 接口） | ALIGNED |
| 2 | gate 脚本行为一致性（check-gate P1-P8 分支，P2 分支未破坏） | ALIGNED |
| 3 | 协议文档与脚本一致（WORKFLOW↔phases.yaml / UPGRADING v0.60.0 / AGENTS.md 目录图） | ALIGNED |
| 4 | 渲染化后卡片与协议一致（S-3，无叙事丢失） | ALIGNED |
| 5 | hook 链完好（pre-commit-gate 2j.2 未破坏既有 gate 挂载） | ALIGNED |
| 6 | 平台无关（无裸 python3/PATH//tmp/POSIX 假设，BDD-16） | ALIGNED |
| 7 | 测试套件（既有测试未因改动破坏，全量 pytest） | ALIGNED |

**总体结论**：全部 7 项 ALIGNED，无 MISALIGNED / NEEDS_HUMAN_REVIEW 项 → **status: approved**（见"审查结论与 Header status 一致性"节）。

## 逐项审查

### 要点 1：新脚本与既有协议约定对齐

**判定对象**：`agate/scripts/check-structure-consistency.py`（443 行）+ `agate/scripts/check-yaml-schema.py`（175 行）

**编号空间（S-1~S-6 vs CHECK 1-12）**：
- `check-structure-consistency.py:2` 声明 S-1~S-6 结构一致性双向 gate（TAG0021 M0）；`:367-381` S-0 编号自校验：本脚本 S 编号 ⊆ 保留空间 {S1..S6}（无 S7+ 蔓延），且反查 `check-protocol-consistency.py` 未使用 S 编号（与 CHECK 1-12 不冲突）。
- `check-structure-consistency.py:370-376`：`errs.append("本脚本使用 S 编号 %s 超出保留空间 %s（S-0 编号自校验）")` / `:381` `"check-protocol-consistency.py 使用 S 编号 S%s（与 S-1~S-6 空间冲突，S-0 编号自校验）"` —— 双向防冲突。
- `check-protocol-consistency.py:18` 标题声明 CHECK 9；`:704-710` 锚点表新增两条：`check-yaml-schema.py`、`check-structure-consistency.py`（keywords `["S-1", "check-yaml-schema.py"]`）——S 编号空间与 CHECK 空间互不侵占，锚点登记同步（见要点 3/6）。
- **实测**：S-0 自校验随真实树 S1-S6+S0 全 OK（exit 0）通过。

**输出格式（rep 风格）**：
- `check-yaml-schema.py:20`：`输出：SCHEMA-<file>: OK / SCHEMA-<file>: ERROR <path> <msg>（仿 rep 编号风格）`；`:168-171` 实现 `sys.stdout.write("SCHEMA-%s: ERROR %s%s\n" ...)` / `"SCHEMA-%s: OK\n"`，`sys.exit(1 if any_error else 0)`。
- `check-structure-consistency.py` 同族：每条 `errs.append(...)` 带 `（S-N ...）` 定位后缀，`:391/:395/:439` `sys.exit(1 if any_error else 0)` —— 与既有 check-*.py rep 输出（`rep.error("CHECKn-xxx", ...)`）风格同构。

**退出码语义**：
- 两新脚本统一 `exit 0` = 全绿 / `exit 1` = 至少一条 ERROR（`check-yaml-schema.py:171`、`check-structure-consistency.py:439`），与既有 gate 约定（0 过 / 非 0 阻断）一致；ERROR 即阻断语义与 P2-design §3.3 规格一致。

**--strict-errors-only 兼容**：
- `check-structure-consistency.py` 无 argparse、不解析 argv（进度核验：忽略 argv 恒常开阻断）——被 `check-protocol-consistency.py --strict-errors-only` 调用/并列运行均无参数冲突；兼容成立。

**agate_common 公共库接口**：
- 两新脚本复用 `agate_common.read_rules_yaml`（`:641`）/ `resolve_rules_root`（`:653`）/ `reconcile_*`（`:599-631`）公共函数，未自造 YAML 读取与规则根解析；`check-structure-consistency.py:21` S-5 用 `sys.executable` 调用同目录 `check-yaml-schema.py`（AGATE_ROOT 透传）——无硬编码 python3。
- 真实树实测：`check-yaml-schema.py` SCHEMA-phases/dispatch/roles 全 OK（exit 0）；`check-structure-consistency.py` S1-S6+S0 全 OK（exit 0）。

**结论**：ALIGNED

### 要点 2：gate 脚本行为一致性

**判定对象**：`agate/scripts/check-gate.py`（P2 分支迁移）

**P2 分支判定未破**：
- 四字段计数迁移：`check-gate.py:715` `field_count = count_p2_declared_fields(p2_text)`（公共库 `agate_common.py:802`），旧实现为内联逐行正则——语义等价核验（进度 P4-review：全文列 0 匹配行数，frontmatter+正文都算，`count_p2_declared_fields` 覆盖 `packages/domains/ui_affected/gate_commands` 四字段）；BDD-9 迁移不改变判定口径。
- gate_commands 块解析：`:626` `_gate_commands_block_keys(p2_text)` 用公共库 `parse_gate_commands_block`（`agate_common.py:788`），合法 key 判定读 `rules/dispatch.yaml` `gate_commands_syntax`——P2 卡片「gate 规则」的字段集合语义不变。
- **对账 fail-open 不改变退出码**：`:636-643` `_reconcile_p2_fields` 差异 → stderr `RECONCILE WARNING` + 汇总计数（可重定向进日志），对账不改变 `gate_p2` 判定——M1 双跑阶段的既约语义，升级为"对账兜底"彻底兼容旧格式任务。
- P2 其余判定未动（进度核验）：权衡 / 候选 / UI 节 / dispatch_plan / missing_cmds 分支零触碰。
- **真实任务实测**：本任务（TAG0021-structured-layer）真实 P2-design.md 跑 `check-gate.py P2` → RECONCILE SUMMARY 0 mismatches，`exit 2` 原语义保留（RECONCILE 差异不阻断既有判定）。

**P1-P8 其余阶段分支**：diff 面仅 P2 分支（+78 行），P1/P3-P8 分支未列入改动（git diff 逐文件对照确认）；P3 分支 refactor 感知等既有机制未触碰。

**结论**：ALIGNED

### 要点 3：协议文档与脚本一致

**3a. WORKFLOW 阶段总览 ↔ phases.yaml（S-1/S-2 锚点）**：
- `agate/WORKFLOW.md:283-304`：P1-P8 阶段总览表 + `S1S2-ANCHOR-START/END` 锚点注释（`:287` `<!-- S1S2-ANCHOR-START：本表是 check-structure-consistency.py S-1（YAML→md）/S-2（md→YAML）双向一致性检查的 md 侧锚点（数据面 = rules/phases.yaml） -->`；`:288` 表行三段式 `| P{N} | 名称 | 执行角色 | …`，S-2 只匹配 `P` 数字/P6.5 前缀行）。
- `agate/rules/phases.yaml`（105 行）10 阶段 P0-P8+P6.5，exec_role 逐项：P0=main-agent, P1=analyst, P2=architect, P3=test-designer, P4=implementer, P5=verifier, P6=verifier, P6.5=judge, P7=consistency-reviewer, P8=implementer——与 WORKFLOW 总览表 10 行 id/name/exec_role 逐项一致（进度核验 S-1/S-2 手工比对 + 真实树 exit 0）。
- 锚点表登记（`check-protocol-consistency.py:704-710`）同时覆盖两新脚本，CHECK 9 实测 0 ERROR（含反向覆盖检查）。

**3b. UPGRADING v0.60.0 破坏性变更 vs 实际脚本行为**（`agate/UPGRADING.md:92-133`）：
- ① `:97-111` 三脚本（read-gate-commands / check-pruning / check-gate P2）从 grep 解析切为读 YAML 权威源 + 对账兜底；`:105` 明确"迁移后判定语义不变：退出码 0/1/2 语义、P2 四字段门槛、P3 命令输出 JSON 结构均与 v0.59.x 一致"——与要点 2 实测（RECONCILE 0 mismatches / exit 2 保留）一致。
- ② `:113-121` 一致性 gate 提升阻断：`check-structure-consistency.py` 从"仅 P5 gate + 手动"提升为 pre-commit 独立 step + CI consistency job 追加步骤；漂移即阻断（exit 1）——与 `pre-commit-gate.py:407-415` 2j.2 实现及 CI `protocol-tests.yml:131-132`（`Run structure consistency check (TAG0021 M2, Linux)`）完全对应。
- ③ `:123-129` 新增 `rules/*.yaml` + schema + 两新脚本，纯增量、既有 md 保留不动——实际 diff 面确认（rules/ 三 YAML + schema/ 三 JSON 是新增目录）。
- 版本号修正：UPGRADING v0.57→v0.60.0 纠正合理（进度核验）。

**3c. AGENTS.md 目录图 ↔ 实际目录**：
- worktree 根 `AGENTS.md` 仓库结构节已加入 `rules/`（"可判定规则权威源（TAG0021 结构化层）：phases.yaml / dispatch.yaml / roles.yaml + schema/*.json … S-1~S-6 双向一致性 gate 防 md↔YAML 漂移"）——实际 `agate/rules/`（三 YAML + schema/）与 `agate/scripts/` 两新脚本均存在，目录图与实际一致。
- `agate/AGENTS.md`（协议本体层）入口导航表同步新增 `rules/` 行（跨阶段规则权威源）——文档传播到位。

**结论**：ALIGNED

### 要点 4：渲染化后卡片与协议一致

**判定对象**：M3 卡片渲染化（`agate-next-card.py` / `agate-inject-card.py` diff）+ S-3 一致性 gate

**S-3 双向 gate 实现**（`check-structure-consistency.py:180-239`）：
- `:186-191` S-3 YAML→cards：产出/派发 vs phases.yaml 声明逐卡片比对，"人为篡改 YAML 删阶段 / 增卡片均被 S-3 双向捕获"；`:206/:226/:233` 三类 ERROR（无 phases.yaml 定义 / P2-design.md 缺失 / 产出或 exec_role 未出现在卡片）。P2 试点锚点强制（`:237-239` phases.yaml 必须定义 P2）。

**渲染化后卡片与协议一致（无叙事丢失）**：
- **真实卡片零触碰**：进度核验 `git status` 无 `phase-cards/` 修改——S-3 判定对象（P2-design.md 渲染卡片）在本次改动面上未被动过，叙事层保留完整；`test_docs_assertions` 等叙事断言全绿。
- **渲染链路契约**：next-card/inject-card/card-inject 相关测试 35 passed（字节稳定契约保持——next-card 正式卡片原样输出路径改为 utf-8 round-trip，契约由测试锁定）；本 dispatch-context 经 `agate-inject-card.py` 注入的 P4 卡片全文含 `##` 节（派发指引 + 卡片全文结构完整）——渲染链路实测通。
- **S-3 真实树 exit 0**（S1-S6+S0 全 OK）确认当前渲染产物与 phases.yaml 声明一致、无漂移。

**结论**：ALIGNED

### 要点 5：hook 链完好

**判定对象**：`agate/scripts/pre-commit-gate.py`（+13 行：2j.2 structure step）+ `check-gate.py` P3 分支

**2j.2 结构一致性 step**（`pre-commit-gate.py:398-415`）：
- 位置：2j.1 ceremony 路由校验（`:402`）之后、2k SCOPE+ 之前，`2j.2` 独立 step、与 check-gate 并列不短路（进度核验：`gate_exit!=1` 短路条件不含 2j.2）——BDD-10 语义成立：结构漂移阻断 commit 不受其他 step 结果影响。
- 双fail 语义：脚本缺失 → fail-open（`:412` `os.path.isfile(...)` 守卫，缺失跳过不阻断——与 M2-4 描述一致）；脚本存在且 `exit 1`（S-1~S-6 漂移 ERROR）→ `:415` `GATE: 结构一致性漂移（check-structure-consistency.py exit 1）` 阻断。判定逻辑 = 退出码（客观），无对自写文件的文本信任。

**既有 gate 挂载未破坏**：
- 2j（裁剪条件检查）/2j.1（ceremony）/2k（SCOPE+）既有代码零触碰（diff +13 行仅插入 2j.2 块 + 注释）；`check-gate.py` P3 分支 refactor 感知等既有机制未纳入改动面（要点 2 已述）。
- 稳定版 hook 软链指向不变：`commit-msg-self-gate.sh` 的 self-gate-review 路径要求由本报告路径满足（commit message 须含 `self-gate-review:` 路径）。

**结论**：ALIGNED

### 要点 6：平台无关

**判定对象**：两新脚本 + 改动面 7 脚本的平台假设扫描（BDD-16）

- **静态核验**：`check-structure-consistency.py` / `check-yaml-schema.py` 均无裸 `python3`（S-5 子进程用 `sys.executable` 调用同目录脚本，`check-structure-consistency.py:21`）、无硬编码 PATH、无 `/tmp` 等 Unix-only 路径、无 POSIX symlink 假设；utf-8 显式（`encoding="utf-8"`）、Python 3.8+ 语法。
- **check-yaml-schema.py** 无平台分支依赖：纯 YAML↔JSON schema 校验逻辑，draft-07 子集手写实现（`:10-13` type/required/enum/properties/items/additionalProperties 等）。
- **自动化扫描**：`check-platform-assumptions.py` 对改动面 7 脚本（agate_common/read-gate-commands/check-pruning/check-gate/md-field-get/pre-commit-gate + 两新脚本）0 命中（exit 0，仅既有 pre-commit-gate:62 R2 命中属基线项）。
- 新测试文件同规：`test_check_structure_consistency.py` / 新 schema 测试用 pytest `tmp_path` fixture，无平台硬编码（全量绿见要点 7）。

**结论**：ALIGNED

### 要点 7：测试套件

**要求**：既有测试未因改动破坏，**附最近一次 pytest 全量实跑输出（含 passed/failed 计数）**——无实跑输出的 ✓ 视为无效（role-def 原则，T026/G2.5 教训）。

**实跑记录（P4-review-progress.md 尾部，本轮实测）**：
- **34 条里程碑测试全绿**（P3-test-cases 8+10+7+4+4+1 = 34，0 failed）——M0-M3 各迁移阶段行为红线全过。
- **全量 pytest 干净跑**（basetemp=/tmp 仓库外，worktree 代码）：**1200 passed / 0 failed / 2 skipped**。首跑 1196 passed/4 failed/2 skipped 的 4 个 failed 经隔离复跑全部定位为环境假象：`test_bdd_7`（沙箱 git 上下文）、`test_bdd_25` + `test_con_1/2`（共享 basetemp 残留 dist 被一致性扫描，清 dist / basetemp 移仓库外后全绿）——**零真实回归**；实现声称的 1198/2/2 为保守口径（从 worktree 内 basetemp 观测），沙箱外真实 0 failed。
- **count-tests** = 1202 ≥ 749 基线 ✓（文档用例数未漂移）。
- **next-card/inject-card/card-inject 契约**：35 passed（字节稳定契约保持，要件 4）。
- **新测试覆盖**：`test_check_structure_consistency.py` 10 用例覆盖 S1（YAML→md 一致/漂移）、S2（md→YAML）、S3（卡片产出）、S4（字段登记与语法）、S5（schema 枚举串联）、S6（引用缺失）、S0（编号自校验）—— tamper 双向语义有覆盖；`check-yaml-schema` 用例覆盖 draft-07 子集 + R5 schema 自身健全性。
- consistency `--strict-errors-only`：0 ERROR（318 WARNING 基线）；`check-platform-assumptions`：exit 0（要件 6）。

**结论**：ALIGNED

## 非阻塞观察项（不计入修复项，交付 P7 跟进）

以下各项**不影响本次 ALIGNED 判定**（不构成文档-脚本不一致或破坏性行为），但需 P7 consistency-reviewer / 主 Agent 后续收敛：

1. **S-4 未覆盖 roles.yaml c8_mapping ↔ review-mapping.md 一致性对**：P2-design §3.1 承诺的比对在 `check-structure-consistency.py` 中未实现（当前 roles.yaml c8_mapping 与 review-mapping.md 数据一致，但无 BDD 覆盖——S-4 仅覆盖 dispatch.yaml field_readers/gate_commands_syntax）。当前数据一致、无漂移风险暴露 → 观察项，非阻断。
2. **M1/M2/M3 共 6 条 DESIGN_GAP 未标 REVIEWED**：P4-implementation.md 记录 8 条 DESIGN_GAP（task P4 尚在进行，P7 未执行）；按 role-def 原则 6，任务尚无 P7 REVIEWED-ACCEPTED 记录时不构成"已知偏离豁免"，本次审查逐项核验后未发现由这些 DESIGN_GAP 引发的实际协议-脚本不一致 → 仍判 ALIGNED，交付 P7 consistency-reviewer 独立核实并标注。
3. **M0-8 / M0-9 CLARIFY 待主 Agent 关闭**：P4-implementation.md 中 2 条 CLARIFY 属实现决策确认项，不影响协议对齐判定，由主 Agent 关闭。
4. **UPGRADING 版本号纠正**：v0.57→v0.60.0 章节定位合理（与 CHANGELOG 版本序列一致），无遗留 v0.59.x 表述冲突。

## 审查结论与 Header status 一致性

- Header `status: approved`，正文 7 项审查要点结论全部 **ALIGNED**、无 MISALIGNED / NEEDS_HUMAN_REVIEW 项、无未确认的 HUMAN_CONFIRMED 依赖 → **终值与正文结论一致**。
- 闭环规则（role-def）：ALIGNED → 通过，可 commit。commit message 须含 `self-gate-review: agate-workspace/tasks/TAG0021-structured-layer/self-gate-review-TAG0021-P4.md`。
- 审查只读性：未修改任何实现文件；唯一写操作 = 本报告 + P4-review-progress.md（留痕）。`[PROD_NOT_TOUCHED]`。