---
phase: P4
task_id: TAG0021-structured-layer
type: review
parent: P4-implementation.md
trace_id: TAG0021-P4-20260822
status: approved
created: 2026-08-22
agent: review
---

# P4 实现评审 — TAG0021 协议结构化层（RM-AG0022）· M0-M3 四里程碑

> 评审范围：P4-implementation.md 声明的 M0-M3 全部改动（agate/rules/ 三 YAML + schema、check-yaml-schema.py、check-structure-consistency.py、对账模式、切权威源、阻断提升、卡片渲染化、UPGRADING v0.60.0 节）
> 评审方式：独立只读评审（不修改任何实现文件）；对照 P2-design.md C1 方案 + P1 BDD 基线 + 真实树实测（gate/测试/一致性）
> 状态标记：[PROD_NOT_TOUCHED]

## 1. 评审要点 1 — 实现与 P2 C1 方案一致性

**结论：一致（逐落点核对，无越界扩大；[SCOPE+] 处置合规）**

对照 P2-design.md §1.1 M0-M3 落点表（39 个落点）逐项核对 P4-implementation.md 四节改动清单（引用：P2 §1.1；P4-implementation.md M0/M1/M2/M3 各节「改动文件清单」）：

| P2 落点 | 实现落点 | 核对结果 |
|---------|---------|---------|
| M0-1/2/3（三 YAML）| `agate/rules/{phases,dispatch,roles}.yaml` | ✅ 字段集/枚举与 P2 §3.1-3.2 一致（phases.yaml 10 阶段与 WORKFLOW 总览表逐字一致、D3 首批三脚本=对账三脚本、五模式词表含 P2-review 发现 #2/#3 修正） |
| M0-4（三 schema）| `agate/rules/schema/*.schema.json` | ✅ draft-07 子集（type/required/enum/...）与 §3.2 一致；check-yaml-schema 实跑全 OK（progress：SCHEMA 全 OK exit 0） |
| M0-5 / M0-6 | `check-yaml-schema.py`（仿 agate-frontmatter-check SCHEMAS）+ `check-structure-consistency.py`（S-1~S-6 + S-0 自校验，S 空间 ⊆ {S1..S6} 且与 CHECK 1-12 隔离） | ✅ 与 §3.3 S-1~S-6 判定口径一致（S-5 独立进程调 check-yaml-schema；S-6 引用完整性断言协议根）；真实树 S1-S6+S0 全 OK exit 0 |
| M0-7（WORKFLOW 锚点）| `agate/WORKFLOW.md` 表前后加 S1S2-ANCHOR 注释，表行未动 | ✅ 与 §3.3 S-1/S-2 md 侧锚点声明一致；真实树 S-1/S-2 对账 0 漂移 |
| M0-8（README/AGENTS rules/ 层）| M1 回补：仓库根 README.md + AGENTS.md + agate/AGENTS.md 各补 rules/ 一行 | ✅ [CLARIFY] 处置：延迟到 M1 批补做，完成且合规 |
| M0-9（UPGRADING 章节）| M2-7 以「v0.60.0」章节落地（原 P2 写 v0.57 章节，版本纠正合理） | ✅ 见要点 5 |
| M0-10（SELF-GATE 自生效）| 无文件改动，机制自生效声明 | ✅ 合规 |
| M0-11（两测试文件）| P3 已交付测试零触碰 | ✅ git diff 确认 agate/tests/ 无任何改动 |
| M1-1..M1-5（对账工具/三脚本/测试）| agate_common 对账函数 + read-gate-commands/pruning/check-gate 接入 + 测试零触碰 | ✅ 与 §3.4 一致：RECONCILE WARNING/SUMMARY 出口、AGATE_RECONCILE 开关、三类解析点覆盖（BDD-7） |
| M2-1..M2-7（切权威源/阻断提升/UPGRADING）| 共享助手单点化（parse_gate_commands_block/count_p2_declared_fields）+ md-field-get 文档化 + pre-commit 2j.2 + CI 步骤 + UPGRADING v0.60.0 | ✅ 与 §3.5 一致；md-field-get 落点为「文档化边界」非行为迁移，有 DESIGN_GAP-6 声明兜底（见要点 2） |
| M3-1..M3-5（渲染化）| 渲染器内嵌 next-card（非 P2 字面 inject-card，DESIGN_GAP-8 声明采纳 dispatch-context「或新渲染器」分支）+ S-3 全卡对账升级 + 测试零触碰 | ✅ 落点偏离有声明且与 BDD-13 注入测试实际路径一致（见要点 2/6） |

- **范围边界符合「只实现方案里的东西」**：git diff 实测 18 修改 + 8 新增，全部落在 P2 §1.1 声明的落点内；N-1~N-9（不改什么）逐条未越界（check-protocol-consistency.py 仅锚点**数据登记**，见 [SCOPE+]；phase-cards 叙事节未动；rules/*.md 未迁移未删；hook 薄壳未动）。
- **[SCOPE+] 处置合规**：M0 锚点登记 SCOPE+ → P1-requirements.md L231 已标 `[SCOPE_RESOLVED: ...无检查逻辑改动...]`（主 Agent 已确认）；M2 的「3 处非扫描清单内联正则留后续批」SCOPE+ 为建议性（未扩大范围），见 §8 观察项 2。

## 2. 评审要点 2 — [DESIGN_GAP] 处置

**结论：3 条声明（S-4 字段词表 / P0 main-agent / S-3 整卡级）合理、实现与声明一致、均已 [DESIGN_GAP_REVIEWED]**

评审要点 2 覆盖的 3 条（引用：P4-implementation.md M0 节「[DESIGN_GAP] 声明」）逐条判定：

1. **S-4 字段词表（DESIGN_GAP-1）**：P2 §3.3 未指定字段集裁决来源，实现取「内置任务字段词表（源自 agate-frontmatter-check.py SCHEMAS migrated_keys + P2/P4 卡片机器字段）∪ phases.yaml task_fields 声明」为判定面。**合理**——判定面可判定（词表为脚本内置常量 + 数据扩展面），与 S-4 实现（implementation M0 判定口径说明）一致；`[DESIGN_GAP_REVIEWED: 主 Agent 已确认采纳]` 已标。
2. **P0 main-agent（DESIGN_GAP-2）**：P2 exec_role 枚举未覆盖 P0，实现取 `exec_role: main-agent` 并扩展 schema 枚举（**既有枚举值不变**，与测试夹具 schema 兼容）。**合理**——与真实 WORKFLOW 总览表 P0 列「**主 Agent 亲自写**」对齐，向后兼容；`[DESIGN_GAP_REVIEWED]` 已标。
3. **S-3 整卡级（DESIGN_GAP-3）**：P2 未指定产出文件名比对作用域，真实 P2 卡「产出规格」节未含 P2-review.md（评审产出散落于 gate 规则/推进条件节），节级比对会误报；实现采用整卡文本包含判定。**合理**——P3 篡改测试在节级/整卡级两种口径下均变红（语义等价）；`[DESIGN_GAP_REVIEWED]` 已标。

M1/M2/M3 后续声明的 6 条（比较语义 / gate_commands 合法 key 判定面 / 结构化读取形态 / pre-commit fail-open / 渲染器落点 next-card / 前置条件节不渲染）：**逐条评估均合理、实现与声明一致**（见 §1 对应行与 §6 渲染化核验）；其中「pre-commit fail-open」与 UPGRADING ② 的「自定义 AGATE_ROOT 缺 rules/ → FATAL 阻断」互补不矛盾（脚本缺失 → 跳过；脚本存在但 rules/ 缺失 → 阻断）。此 6 条尚未标 `[DESIGN_GAP_REVIEWED]`，记入 §8 观察项 1（流程项，不阻断）。

## 3. 评审要点 3 — 测试变绿真实性

**结论：真实（P3 34 红线全部转绿，零真实回归，测试文件零触碰）**

- **34 条里程碑测试 = P3 红线基线逐条转绿**（引用：P3-test-cases.md；P4-implementation.md 各节「变绿测试」）：`test_check_yaml_schema` 8/8（M0，BDD-1/2/3/5）→ `test_check_structure_consistency` 10/10（M0，S-1~S-6+S-0）→ `test_check_reconcile` 7/7（M1，BDD-6/7/8 对账部分）→ `test_structure_migration` 4/4（M2，BDD-9/10）→ `test_card_render` 4/4（M3，BDD-12/13）→ `test_cross_milestone` 1（跨里程碑联动）。**本机实测复跑：全部绿，0 failed**（progress 记录）。
- **全量 pytest 真实基线**：basetemp 置于仓库外 /tmp（规避沙箱约束）复跑 **1200 passed / 0 failed / 2 skipped**；2 个 skip 为既有。M3 声称的「2 failed 沙箱假象」（test_bdd_7 git 上下文 + test_bdd_25 dist 污染）在仓库外 basetemp 下均**通过**——[CAPABILITY_GAP] 归因正确（implementation M3 全量回归表），非实现缺陷；沙箱内复跑 4 failed 与 M2 声称一致（同族假象，隔离复跑全绿）。
- **只增逻辑核对**：count-tests **1202 ≥ 749 基线**（P3 预期，只增不减）；**agate/tests/ 零触碰**（git diff --name-only 无任何 tests/ 路径——「不改测试迁就实现」纪律成立）。
- **BDD-14 字节稳定回归**：next-card/inject-card/card-inject 35 passed（sha256/注入 hash 契约保持，见要点 6）。
- **零真实回归链路**：M1 全量 14 failed（12 预期红灯 + 2 沙箱）→ M2 4 failed（2 预期红灯 + 2 沙箱）→ M3 2 failed（2 沙箱）→ 沙箱外 0 failed；唯一真实回归 test_sg_6 经锚点登记修复转绿。

## 4. 评审要点 4 — 代码质量

**结论：合格（py38/utf-8/os.environ 约定、平台无关 BDD-16、最小实现）**

- **Python 3.8+ 兼容**：两新脚本与全部改动脚本语法检查通过（无 walrus/`X | Y`/match 等 3.9+ 特性），utf-8 显式（文件头/读写编码），环境读取用 os.environ（无 shell 注入面），import 齐备（agate_common 新函数使用 re/yaml/sys，文件头 import 已存在，diff 无缺失）。
- **平台无关（BDD-16）**：无裸 `python3`/`PATH`/`/tmp`/POSIX symlink 假设（progress 逐脚本确认）；`check-platform-assumptions.py` 对改动脚本扫描 **0 命中 exit 0**（唯一既有命中为 pre-commit-gate.py:62 字符串，非本轮引入）。
- **最小实现、无越界改**：git diff 全部为纯追加（对账钩子/共享助手/渲染函数/文档化）+ 1 处纯数据登记（锚点表）；三消费脚本既有判定逻辑语义未动（M2 共享助手与原内联正则逐字节等价：块只认列 0 标题 + 二空格缩进，四字段 = 全文列 0 声明行数）；无死代码残留（回退边界各自声明）。
- **自查记录如实**：实施记录明示 ruff 本环境未安装（P5_ruff 由主 Agent gate 执行），未虚报自查通过。

## 5. 评审要点 5 — 破坏性变更与向后兼容

**结论：合规（UPGRADING v0.60.0 节逐条列 M2 行为变化，对账桥接兼容存量）**

逐条核对 UPGRADING.md v0.60.0 节（L92-133）与 M2 实际行为（引用：UPGRADING L92-133；P4-implementation.md M2 节）：

1. **① 三脚本切权威源（UPGRADING L97-111「行为变化表」）**：`agate-read-gate-commands.py` / `check-pruning.py` / `check-gate.py`（P2 分支）的升级前后对照与实现一致——块解析/四字段计数迁 agate_common 共享助手、合法 key 判定读 rules/*.yaml（dispatch.yaml gate_commands_syntax + phases.yaml 阶段集）；**声明「退出码 0/1/2 语义、P2 四字段门槛、P3 JSON 输出结构与 v0.59.x 一致」经实测定立**（progress：check-gate P2 真实任务 0 mismatches exit 2 原语义；read-gate-commands JSON 正确）。逐条列全（行为表 3 行 + 语义不变声明 + 对账兜底 + 升级动作），无遗漏破坏性变更。
2. **② 一致性 gate 提升阻断（UPGRADING L113-121）**：pre-commit 独立 step（2j.2，不与 gate_exit 短路）+ CI consistency job 追加步骤，漂移即 exit 1 阻断——与实现 M2-4/M2-5 一致；「自定义 AGATE_ROOT 缺 rules/ → FATAL 阻断」与 pre-commit fail-open（脚本缺失跳过）互补，语义自洽。
3. **③ rules/ 数据层纯增量（UPGRADING L123-129）**：新增文件不改变既有协议文件语义、既有 rules/*.md 保留——与 N-2 范围边界一致。
4. **通用升级动作**（L131-133）：git pull + 重跑 install-hook.py（Windows 复制模式必须重跑）——与 AGENTS.md 发布清单一致。
5. **向后兼容实测**：对账桥接（正文 grep 保留为兜底侧）使既有 md 文本夹具与 825 基线 fixture 回归全绿（BDD-11 语义保持）；AGATE_RECONCILE 可关供 CI/批处理降噪；旧格式 md 任务（frontmatter 无机器字段）不迁移仍可跑（仅 RECONCILE 告警）。

## 6. 评审要点 6 — 渲染化正确性

**结论：正确（S-3 全卡对账 exit 0，字节稳定契约保持，稳定版隔离成立）**

- **S-3 渲染一致升级**（引用：P4-implementation.md M3 节「判定口径实现说明」）：①孤儿卡片防护（phase-cards/ 下 P 前缀卡片无 phases.yaml 定义 → ERROR）+ ②有卡片阶段输出文件**整卡级**逐字段对账（M0 仅抽检 P2 → M3 全卡）+ P2 试点锚点强制。**真实树实测 S1-S6 + S0 全 OK exit 0**（progress；含 S-3 全卡对账——9 张真实卡片与 phases.yaml 对账无漂移）。
- **渲染产物与 phases.yaml 对账**：S-3 比对面 = 输出文件（`outputs.file` 整卡文本包含）+ exec_role（「## 派发」节出现）；validated 于真实树全部卡片；无卡片阶段（P6.5）正确跳过。人为篡改 YAML → S-3 exit 1（test_bdd_12 两例覆盖，绿）。
- **字节稳定契约（BDD-14/R6）**：正式卡片（含 `## ` 节，git 管理渲染产物）由 next-card **原样输出**——test_nc_* body-sha256 + test_icb_1 注入 hash 契约保持（35 passed）；渲染仅对裸模板（无 `## ` 节）生效，渲染路径确定（无时间戳/路径注入）。
- **稳定版隔离（BDD-13）**：渲染只读 `resolve_agate_root` 解析到的 rules/phases.yaml（env AGATE_ROOT → 项目声明 → current → 脚本上溯）；两例隔离测试（注入渲染 + 不被 worktree 未发布 YAML 污染）绿——worktree 改 rules/*.yaml 不影响 ~/.agate 稳定版注入（TAG0016 教训防线）。
- **真实卡片叙事未动**：git status 无 phase-cards/ 修改 + test_docs_assertions/test_protocol_mechanism_anchors/test_p2p4_boundary_docs 断言真实卡片叙事文本——「渲染化不改变人类可读叙事」硬约束成立（M3 CLARIFY 落点正确，见 §8 观察项 3）。

## 7. 评审要点 7 — 新增文件核对表

**结论：齐全（M0 逐行表 + M1/M2/M3 无新增说明 + CODE-MAP.md 已实际更新）**

- **M0 新增文件核对表**（引用：P4-implementation.md M0 节「新增文件核对表」）：8 个新增文件（三 YAML + 三 schema + 两脚本）全部 `within agate/` + `[CODE_MAP_UPDATED]`，2 个修改文件（WORKFLOW.md / check-protocol-consistency.py）`[CODE_MAP_EXEMPT: 既有文件修改，无新增路径需登记]`——骨架归属列与 CODE-MAP 处理列均填写合规。
- **M1/M2/M3 无新增文件说明**：三节均声明「全部改动为修改既有文件，无新增路径需登记，不重复 M0 表」——合理（git diff 实测确认 M1-M3 无新增文件，仅修改既有登记模块内脚本）。
- **CODE-MAP.md 实际更新确认**（引用：`agate-workspace/agents/CODE-MAP.md`）：L37-41 新增 `rules` 模块条目（数据面：phases/dispatch/roles.yaml + schema/），L67-71 新增「scripts 消费 rules/*.yaml 声明做判定」依赖方向 + 「禁止 scripts 反向定义 rules 数据语义」约束——「新增文件已同步更新 CODE-MAP」成立，非纸面声明。

## 8. 非阻塞观察项（建议，不构成 rejected）

以下为流程/建议级观察项（**均不构成 CRITICAL/BLOCKER**，不阻断推进；建议主 Agent 在推进过程中处置）：

1. **M1/M2/M3 的 6 条 [DESIGN_GAP] 未标 [DESIGN_GAP_REVIEWED]**（M0 的 3 条已标）：与派发指引「3 条声明」评审范围外的后续声明；内容均合理且实现一致（见 §2），建议主 Agent 按 M0 同格式补确认标记。
2. **M2 [SCOPE+]（3 处非扫描清单内联块正则留后续批）在 P1-requirements.md 无对应 [SCOPE_RESOLVED]**：P1-requirements.md 现仅 1 条 SCOPE_RESOLVED（L231，对应 M0 锚点登记）；建议主 Agent 对该 SCOPE+ 显式处置（登记后续批或标 RESOLVED），防"建议性声明"在 P7 被误读为未关闭项。
3. **M0 [CLARIFY]（M0-8/9）与 M3 [CLARIFY]（真实卡片渲染化）仍 open**：M0-8 已回补、M0-9 经 M2-7 以 v0.60.0 章节落地（版本纠正合理）、M3 渲染机制就位 + S-3 全卡对账已覆盖可判定面——均为合理落点，待主 Agent 关闭声明即可。
4. **S-4 未实现 roles.yaml c8_mapping ↔ review-mapping.md 一致性对**（P2 §3.1 承诺、当前数据一致）：两处 C8 表人工核对一致，无 BDD 覆盖，属设计承诺的未落地项（非实现缺陷）；建议主 Agent 确认是否后续批补或显式降级为数据一致性声明。
5. **ruff 未在本环境实测**：P4-implementation 三处自查记录如实声明；P5_ruff 为 gate_commands.P5 项，由 P5 verifier + 主 Agent gate 执行兜底，非 P4 评审可判定的缺失。

## 9. 总结论

**PASS — status: approved（7 项评审要点全覆盖，无 CRITICAL/BLOCKER）**

- 7 项评审要点逐项核验：①实现与 P2 C1 方案 39 落点一致、无越界、[SCOPE+] 处置合规；②3 条 [DESIGN_GAP] 声明合理且已 REVIEWED；③P3 34 红线全部真实转绿、零真实回归、agate/tests/ 零触碰、全量沙箱外 0 failed；④代码质量合格（py38/utf-8/os.environ、BDD-16 平台无关、最小实现）；⑤UPGRADING v0.60.0 节逐条列全破坏性变更、对账桥接兼容存量；⑥S-3 全卡对账 exit 0、字节稳定契约保持、BDD-13 稳定版隔离成立；⑦新增文件核对表齐全、CODE-MAP.md 实际更新。
- 无 CRITICAL（review.md Pass 1 数据安全/正确性面）、无 BLOCKER；§8 的 5 项为流程/建议级观察项，主 Agent 推进中处置即可。
- 证据基：真实树 gate 实测（check-yaml-schema / check-structure-consistency / check-protocol-consistency / check-platform-assumptions 全 exit 0）+ 全量 pytest（仓库外 basetemp 1200 passed/0 failed）+ 34 里程碑测试全绿 + count-tests 1202 + git diff 全量审查（本机实测记录见 P4-review-progress.md）。