---
phase: P1
task_id: TAG0026
parent: P0-brief.md
trace_id: TAG0026-P1-20260830
status: draft
created: 2026-08-30
agent: analyst
risk_level: high
ceremony: standard
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts, agate-tests, agate-phase-cards, agate-templates]
domains: [backend]
capability_requirements: []
---

# P1-requirements — TAG0026 维护性反模式 gate（RM-AG0046）

## 1. 需求复述

把 P0-brief 的一句话任务展开为可验收的需求基线。本任务在 Agateon 协议层落地维护性反模式
gate（RM-AG0046，G0 优先、diff 驱动），范围严格锁定为：

- **G0 两条检测**：god-file 跨越（`before < N and after >= N`，N 默认 1000 可配置）+
  fuzzy-boundary（diff 新增行匹配 Python/TS 类型逃逸正则），新增
  `agate/scripts/check-maintainability.py`。
- **P4 三重门槛硬挂钩**：`check-gate.py` 的 `gate_p4` 新增一步，放行条件 =
  「known-violations 登记存在 + 登记数量对齐 + P4-review approved（agent≠main）」，
  绝不退回"登记即放行"。
- **登记模板**：新增 `known-violations-template.md`，表格用 `| N |` 行首格式，对齐
  `count_kf_entries` 计数算法。
- **配置**：`agate-workspace/maintainability.yaml`（阈值/正则集，缺失用默认值）。
- **卡片自查**：P4 phase card 评审 checklist 加"approve 前必须读过登记理由"；P6 phase card
  自查节加"可再跑一次检测器"提醒（非阻断）。
- **测试**：`agate/tests/` 新增 pytest 覆盖 13 条 BDD（含移动代码假阳性 BDD-12、挂载阶段
  对齐 BDD-13）。

关键立场：**只挂 P4，不挂 P6**；检测器数据源是 `git diff --cached`，代码在 P4 才 staged。

## 2. 隐含需求识别

以下不是用户明说、但技术上必须满足的隐含依赖，每条注明"为什么必须"：

1. **check-gate.py 返回约定兼容**：`gate_p4` 新增一步必须保持既有返回约定（1=阻断 / 2=WARNING
   不阻断 / 0=通过），与既有调用链（`pre-commit-gate.py:349,362` subprocess 调用、
   `ci-gate-backstop.py:24,26,154` CI 兜底）兼容。为什么必须：check-gate.py 是所有任务
   P0-P8 的总闸，回归面最大，P4 新增一步不得改变已有 gate_p4 检查（P4-review 存在/approved/
   agent≠main、代码 staged 检查）的既有语义。
2. **数据源与挂载阶段对齐**：`git diff --cached` 只在 P4（代码 staged）时含代码 diff；P6
   提交的是验收文档，暂存区已无代码 diff。为什么必须：挂 P6 是永远零命中的死代码（v2 教训，
   BDD-13 专门防复发）。
3. **known-violations 与 known-failures 语义区分**：known-failures 登记"预存失败"，宽容方向
   相反；known-violations 登记"本任务自己引入的反模式"。为什么必须：若只要求"数量对齐"就放行，
   等于给引入反模式发打折券（v3 评审 B3 最深修正）；必须「登记存在 + 数量对齐 + P4 评审
   approve」三重齐全。
4. **模板格式对齐 `count_kf_entries`**：登记表必须用 `| N |` 行首表格格式。为什么必须：
   `count_kf_entries`（agate_common.py:1015-1017）按行首 `^\|\s*[0-9]+\s*\|` 计数；"P4 评审
   确认"列不参与机械计数，防"填了就自动放行"错觉。
5. **配置路径用 `agate-workspace/maintainability.yaml`，不用 `.agate/`**：为什么必须：
   ADR-009 界定 `.agate` 前缀是用户级版本管理命名空间，项目级协议配置统一放 `agate-workspace/`。
6. **阈值 N=1000 无实证依据**：文档/配置必须明确"默认值仅供参考可配置"，不造成"协议断言该
   阈值"的错觉。为什么必须：该值来自 Cursor skill 经验值（P0-brief known_risks 第三条）。
7. **fuzzy-boundary 只覆盖 Python/TS**：协议参考实现覆盖 Python（`# type: ignore`/裸
   `except:`）与 TypeScript（`any`/`as any`）；其它语言（Go `interface{}`、Java
   `@SuppressWarnings`）不在本版范围，项目经 `gate_commands` 自行补充。为什么必须：避免
   "支持所有语言"的超范围承诺（约束 5）。
8. **移动代码假阳性是已知行为，非缺陷**：不引入跨行移动检测。为什么必须：复杂度与 god-file
   判据的"零歧义"原则冲突；靠 known-violations 登记机制吸收（BDD-12）。
9. **平台无关性**：路径判定复用 `_norm_rel` 归一化模式，Windows/POSIX 路径分隔符不影响判定
   结果。为什么必须：平台无关是测试硬约束（AGENTS.md），BDD-11 覆盖。
10. **新增脚本文件名与 consistency 覆盖面的关系**：`check-maintainability.py` 以 `check-`
    开头，会落入 `check-protocol-consistency.py` `check_anchor_coverage` 的
    `agate/scripts/check-*.py` 扫描 glob；`agate-summary.py` 的 `_DRIFT_SCRIPTS` 清单也可能
    需同步。为什么必须：consistency 0 ERROR 是硬门槛，P2 需评估锚点登记或命名，避免新脚本
    被反向覆盖检查误判（P2 细化，P1 记录为影响面）。
11. **P4/P6 phase card 自查承载流程要求**：三重门槛的 c（评审 approve 前必须读过登记理由）是
    流程要求，写进 P4 卡片评审 checklist；P6 卡片自查节只加"可再跑一次检测器"提醒，非阻断。
    为什么必须：c 不是新增独立 approve 字段，靠既有评审闭环 + 卡片 checklist 承载。
12. **pytest 覆盖 13 条 BDD**：新脚本、gate 分支、模板格式、配置兜底、平台无关、挂载阶段对齐
    均需测试，对齐既有覆盖惯例。为什么必须：设计文档配套要求"不是只写 BDD 文档不写测试"。

## 3. 待确认清单

[NO_NEED_CONFIRM]

## 4. P0-brief 时效性核对

已核对 P0-brief 时效性，无漂移

## 5. 裁剪说明

本任务 **risk_level=high + ceremony=standard，全阶段不裁**，逐阶段理由：

- **P1 不可裁**：核心阶段，产出需求基线（本文件）。
- **P2 不可裁**：high 风险 + check-gate.py 是核心 gate，回归风险最高，设计须经独立评审。
- **P3 不可裁**：**risk_level=high 时 P3（测试设计）不可裁**；13 条 BDD 须先写失败测试
  确认红灯再实现（AGENTS.md「改脚本的工作流」第 1 条）。
- **P4 不可裁**：实现 + 独立评审闭环是三重门槛 c 的既有依托。
- **P5 不可裁**：验证阶段，跑全量 pytest / consistency / count-tests 是硬门槛。
- **P6 不可裁**：验收阶段，逐条对照 13 条 BDD（PASS/FAIL 总数 ≥ P1 BDD 总数）。
- **P7 不可裁**：**协议跨文件一致性风险保留**——本次同时改 check-gate.py、phase cards、
  模板、配置、测试多文件，跨文件交叉核对必要（ceremony=standard 下 P7 本就不可裁）。
- **P8 不可裁**：**roadmap 回写强制**——RM-AG0046 关联条目须回写 done（RM-AG0043 硬校验），
  版本发布清单（README/CHANGELOG/UPGRADING/稳定版引用）亦须走 P8。

## 6. 同类扫描

扫描动作：对本次涉及的关键符号做全仓 grep/glob，命中清单 + 逐条处理判定如下。

| 扫描对象 | 命中清单（文件:行，代表性） | 本次处理 | 理由 |
|---|---|---|---|
| `check-gate.py` 消费方（P4 新增一步影响面） | `agate/scripts/pre-commit-gate.py:349,362`；`agate/scripts/ci-gate-backstop.py:24,26,154`；`agate/scripts/agate-summary.py:32,44`；`agate/scripts/check-protocol-consistency.py:480,484,562,572,577,622,627,632,704,733,739`；`agate/scripts/check-structure-consistency.py:303`；`agate/scripts/agate-md-field-set.py:129`；`agate/scripts/agate-md-field-get.py:109,130`；`agate/scripts/agate-feedback.py:51`；`agate/scripts/agate-md-field-set-gate-commands.py:10`；`agate/rules/phases.yaml:31,42,53,65,75,84,86,99,109,118,119`；`agate/rules/roles.yaml:45`；`agate/rules/dispatch.yaml:15,32,34-42`；`agate/rules/schema/dispatch.schema.json:21`；`agate/scripts/check-judge-verdict.py`（经 gate_p6.5 被调用） | 不修改这些文件；P2 设计约束：gate_p4 新增一步保持返回约定 1/2 兼容 | 这些是 check-gate.py 的 subprocess 调用方、CI 兜底、漂移清单、锚点表与注释级引用；改动面收敛在 gate_p4 函数内部，不触碰调用方契约。回归拦截：全量 pytest + consistency 0 ERROR 硬门槛（约束 7） |
| `count_kf_entries` 消费方 | `agate/scripts/check-gate.py:156,978`；`agate/scripts/agate_common.py:1015`；`agate/tests/unit/test_md_parse_scan.py:42`；`agate/UPGRADING.md:186` | 复用不改 P5 语义；known-violations.md 采用相同 `\| N \|` 行首格式 | 约束 8：known-violations 复用同一计数函数，不改函数本体、不改 P5 known-failures 判定；P4 评审确认列不参与机械计数 |
| `known-violations` 相关 | 全仓 grep 命中均在设计文档/HANDOFF/任务文件（`rm-ag0046-maintainability-gate-plan.md`、`review-rm-ag0046-maintainability-plan-2026-08-30.md`、`HANDOFF-TAG0026.md`、本任务 P0/P1 文件）；`agate/` 协议本体内无既有机制文件 | 本次处理：首次引入，新增 `agate/assets/templates/known-violations-template.md` | glob 无 `**/known-violations*` 实体文件 → 确认首次引入，无同类实例可合并 |
| `maintainability.yaml` 相关 | 全仓 grep 命中均在设计文档/任务文件；glob 无 `**/maintainability.yaml` | 本次处理：首次引入，新增配置读取逻辑 | 无既有配置文件，确认首次引入 |
| `check-maintainability.py` 相关 | 全仓 grep 命中均在设计文档/HANDOFF/任务文件；`agate/scripts/` 下无该文件；glob 无 `**/check-maintainability.py` | 本次处理：新增脚本 | 确认不存在，新增文件 |
| ruff E722 与 fuzzy-boundary 关系 | `pyproject.toml:7` `select = ["E4","E7","E9","F","W","I","UP","B","SIM","C4","RUF","PLW"]`（E7 含 E722 裸 except） | 本次处理：不改 ruff 配置、不宣称替代 ruff；在需求/设计文档说明二者关系 | ruff 是静态 lint（全文件、非 diff 驱动、不产出 violation 计数）；check-maintainability 的 fuzzy-boundary 是 diff 新增行驱动、产出 violation 计数供 P4 三重门槛。设计文档 §9 明确 ruff 是"fuzzy-boundary 一类的一个平台实现"，二者互补不冲突 |

回归拦截声明：本次新增检测能力不是一次性修完的存量，未来还会持续新增同类反模式判定；拦截手段
= 新增 pytest 用例（13 条 BDD）+ `check-gate.py` P4 硬挂钩 + 协议文档约定，对应 BDD-1..13。

## 7. BDD 验收条件

### 检测器行为（BDD-1..6）

#### BDD-1: god-file 跨越检测

- Given 一个 900 行的文件（默认阈值 N=1000）在本次 diff 中新增行后变为 1150 行（`before < N and after >= N`）
- When 在 P4 阶段（代码已 staged）运行维护性反模式检测
- Then `check_maintainability()` 返回的 violations 包含该文件的 god-file 违规（god_file_count ≥ 1）
- 判定锚：`check_maintainability()` 返回值含该文件违规 = PASS；不含 = FAIL

#### BDD-2: god-file 不误伤存量

- Given 一个已存在 1200 行的文件（已超过默认阈值），本次 diff 只修改 5 行（before 与 after 均 ≥ N，未跨越阈值线）
- When 运行维护性反模式检测
- Then 返回的 violations 不包含该文件（god_file_count 不增加），P4 gate 不阻断（exit 0）
- 判定锚：violations 不含该文件 = PASS；含 = FAIL

#### BDD-3: fuzzy-boundary Python 检测

- Given 一次 diff 在 Python 文件（`.py`）中新增一行裸 `except:`
- When 运行维护性反模式检测
- Then 返回的 violations 包含该文件及其新增行位置（fuzzy_boundary_count ≥ 1）
- 判定锚：violations 含该文件+行号 = PASS；不含 = FAIL

#### BDD-4: fuzzy-boundary 不误伤存量

- Given 一个 Python 文件已有裸 `except:`，但本次 diff 未新增该行（存量行不在 diff 新增行中）
- When 运行维护性反模式检测
- Then 返回的 violations 不包含该存量行（fuzzy_boundary_count 不增加）
- 判定锚：violations 不含该存量行 = PASS；含 = FAIL

#### BDD-5: 阈值可配置

- Given `agate-workspace/maintainability.yaml` 声明 `god_file_threshold: 500`
- When 一个 480 行文件在本次 diff 中变为 520 行（跨越 500）
- Then 返回的 violations 包含该文件；同一 480→520 行变化在默认阈值（1000）下不触发
- 判定锚：配置 500 时触发违规 = PASS；默认 1000 时触发 = FAIL（配置生效性）

#### BDD-6: 配置缺失兜底

- Given 不存在 `agate-workspace/maintainability.yaml` 配置文件
- When 运行维护性反模式检测
- Then 检测器使用默认阈值 N=1000 正常判定，不报错、不静默跳过（返回有效结果，god_file_count / fuzzy_boundary_count 为客观值）
- 判定锚：无配置时仍返回有效判定结果 = PASS；报错或跳过 = FAIL

### P4 三重门槛（BDD-7..10）

#### BDD-7: 三重门槛-登记缺失阻断

- Given violations 非空（检测到维护性反模式），且 `agate-workspace/tasks/{Txxx}/known-violations.md` 不存在
- When `check-gate.py` 在 P4 阶段运行 gate_p4
- Then gate_p4 返回 1（阻断），与 verifier / implementer 输出的任何文字无关
- 判定锚：check-gate.py P4 exit code == 1 = PASS；否则 FAIL

#### BDD-8: 登记数量硬校验

- Given violations 数量为 3，且 known-violations.md 只登记 2 条（`| N |` 行首表格）
- When P4 gate 运行
- Then 返回 1（登记不完整），不是"有文件就过"
- 判定锚：登记条目数 < violations 数时 exit code == 1 = PASS；exit 0 = FAIL

#### BDD-9: 数量对齐但评审未 approve 仍阻断

- Given violations 数量为 3，known-violations.md 登记 3 条，但 P4-review.md 不存在、或 status 非 approved、或 agent == main
- When P4 gate 运行
- Then 仍返回 1，不能靠"数量对齐"单独放行
- 判定锚：登记数量对齐但评审未 approve 时 exit code == 1 = PASS；exit 0 = FAIL

#### BDD-10: 三重门槛全满足才放行

- Given violations 数量为 3，known-violations.md 登记 3 条，且 P4-review.md status == approved 且 agent != main
- When P4 gate 运行
- Then 放行（不阻断），且 known-violations 登记内容不进入 provenance 审计范围（本次不新增第八道审计）
- 判定锚：三重门槛全满足时 exit code == 0（放行）= PASS；仍 exit 1 = FAIL

### 平台与边界（BDD-11..13）

#### BDD-11: 平台无关性（路径分隔符）

- Given 同一 diff 场景分别使用 Windows 路径分隔符（`\`）与 POSIX 路径分隔符（`/`）表示相同文件
- When 运行维护性反模式检测
- Then 检测结果一致（violations 数量与文件列表一致），不受路径分隔符影响
- 判定锚：两种分隔符下 violations 一致 = PASS；不一致 = FAIL

#### BDD-12: 移动代码假阳性诚实处理

- Given 一段含裸 `except:` 的代码从位置 A 移动到位置 B（diff 表现为删除行 + 新增行）
- When 运行维护性反模式检测
- Then 该新增行被判定为 violation（已知假阳性，非 bug），且该 violation 能经 known-violations 三重门槛正常处理（登记 + 数量对齐 + P4 评审 approve）
- 判定锚：判定为 violation = PASS；被自动识别为移动而忽略 = FAIL

#### BDD-13: 数据源与挂载阶段对齐

- Given 一个任务在 P4 阶段 commit 代码后，P6 阶段只 commit 验收文档（暂存区不含代码 diff）
- When 检测器在 P4 阶段被调用
- Then 能读到代码 diff（`git diff --cached` 含代码），产生客观判定；验证检测器挂载在 P4 而非 P6（若挂 P6 则读到空 diff、不产生判定）
- 判定锚：P4 调用时能读到代码 diff 并判定 = PASS；P4 调用读不到代码 diff = FAIL

## 8. 能力需求声明

本任务为纯后端脚本 / 文档 / 测试工作，无浏览器行为、无外部系统行为、无视觉 / 渲染验收需求：

- 能力需求：无特殊能力依赖（不需要 vision / browser / 外网 / 数据库）
- 三态：全部 `available`（python3 / pytest / pyyaml / git / ruff / shellcheck 均在 executor_env 声明可用）
- 因此 frontmatter 置 `capability_requirements: []`，无 `[CAPABILITY_GAP]` 标记
