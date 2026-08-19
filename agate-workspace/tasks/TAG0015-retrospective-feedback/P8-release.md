---
phase: P8
task_id: TAG0015-retrospective-feedback
type: release
parent: P7-consistency.md
trace_id: TAG0015-P8-20260819
status: draft
created: 2026-08-19
agent: implementer
---

[PROD_NOT_TOUCHED]

# P8 发布记录 — agate 复盘与反馈机制统一（TAG0015，RM-AG0020 + RM-AG0021）

> releaser（implementer P8 模式）产出。本文件只核对与声明，**不执行 git commit / git tag / 版本
> 文件改动**——bump 动作由主 Agent 在 gate 验证后统一执行。组织方式参照
> `agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P8-release.md`（同类协议机制任务已完成
> 的 P8 记录），内容逐条重新核实，不照抄其段落结构。

## 版本决策

- `bump_type: minor`
- `debt_check: none`
- 版本号变更：**v0.52.0 → v0.53.0**——`README.md:5` badge 实测
  `[![version](https://img.shields.io/badge/version-v0.52.0-blue)]`，`git describe --tags
  --abbrev=0` 实测 `v0.52.0`，二者一致，当前基线确认为 v0.52.0。

### 独立核实依据（不直接采信 dispatch-context 结论原文，逐条自行复核）

1. **`check-gate.py` 零改动，独立验证**：`git diff --stat 70a16af..HEAD -- agate/scripts/
   check-gate.py`（`70a16af` 是本任务 P0 交接单提交点，早于 P1 任何改动）输出为空——本任务
   P1~P7 全部提交中，`check-gate.py` 一行未动，dispatch-context 声称的"check-gate.py 本身零
   改动"在本次核实中成立，不是转抄。
2. **`check-retrospective.py` exit code 契约独立验证**：`grep -n "sys.exit"
   agate/scripts/check-retrospective.py` 只命中两处——第 115 行（`if not args:` 无参数用法
   错误，本任务改动前既有分支，未触碰）与第 152 行（`main()` 末尾恒 `sys.exit(0)`）。
   `sed -n '85,145p'` 通读 BDD-10 新增的 `_scan_debt_roadmap_signal` 分支与 `main()` 内新增的
   独立第二段 stderr 输出逻辑，两处均未引入任何新的 `sys.exit` 调用——BDD-10 只新增输出文本，
   不改变控制流出口，`sys.exit(0)` 恒定契约在本次代码通读中确认未变。同时确认第 141 行提示文案
   已改为 `tasks/{Txxx}/retrospective.md`（不再含 `docs/releases`），是新增能力而非既有语义
   变更。
3. **`agate-md-field-get.py` 新增字段不影响既有消费字段，独立验证**：`git diff 70a16af..HEAD --
   agate/scripts/agate-md-field-get.py` 显示改动只有两处 `frozenset` 追加元素——
   `NO_FALLBACK_BOOL_FIELDS` 由 `{"regression_pass"}` 追加为 `{"regression_pass",
   "feedback_ready"}`；`NO_FALLBACK_LIST_FIELDS` 由 `{"need_confirm_resolved",
   "suggest_resolved", "scope_resolved"}` 追加为再含 `"mechanism_issues",
   "execution_issues"`。既有 4 个字段（`regression_pass`/`need_confirm_resolved`/
   `suggest_resolved`/`scope_resolved`，分别是 P1/P2/P6/P7 阶段消费的既有字段）逐字原样保留，
   diff 中无一行删除或修改既有条目——纯新增，不影响任何既有 P1/P2/P6/P7 消费方的读取行为。
4. **本任务七类改动均为新增能力，无字段语义改变**：对照 `P4-implementation.md`「改动清单」
   1~7 条逐类核对——模板迁移（新文件+新字段+新协议挂钩点）、`check-retrospective.py` 新分支
   （见上第 2 点，控制流出口不变）、`state-machine.md` 新增小节（`orchestrator-log` 第 481 行
   原有三项排除逐字保留，只追加"和简要依据"分句，未删改既有约束语义）、跨文件同步（`P4` 记录
   为"核实不矛盾，未改正文"，非语义变更）、`AGENTS.md`（区分历史/新复盘措辞，不推翻既有段落
   其余内容）、5 份存量文档标注（首行插入，不改原文一字）、`agate-feedback.py` 新脚本（全新
   文件，不存在"改变既有行为"的问题）——均为加性变更，无一条删除或反转既有 gate 判定逻辑。

**判定：minor（v0.52.0 → v0.53.0）**。不是 patch（本任务新增 1 个协议模板、1 个新脚本、
2 个脚本内新检测分支、1 个协议文档新章节，非纯 bug 修复量级）；不是 major（第 1~4 点独立核实
均未发现任何字段语义改变或既有 gate 脚本行为对老任务产生拦截性变化）。

## packages 声明与实际改动对照（引用 P7-consistency.md §3b 结论，不重新逐文件核对）

`P1-requirements.md §9` 声明 `packages: [assets/templates, scripts, state-machine,
phase-cards, docs-reviews-migration, core-protocol-docs]` 六个逻辑分组。`P7-consistency.md
§3b` 已逐文件核实实际改动（含 SELF-GATE 重试 #1 额外触碰的 4 个文件）与这六组的对应关系，
结论：**全部实际改动文件均能归入 6 组之一或同类推定归入**（`agate/tests/README.md` 归入
scripts 同类；`agate/WORKFLOW.md` 归入 core-protocol-docs 同类）。唯一观察项：
`agate-workspace/roadmap/roadmap.md`（BDD-8 关联脚注更正）未被 §9 描述文字显式挂靠某个包名，
但 P7 已核实该改动在 P1 §4.1 BDD-8 与 P2 §1.1 类 4.1 均有明文出处，不构成未声明的范围外改动，
不升级为阻断项。**本节直接引用该结论，未重新逐文件核对一遍。**

## 版本文件核对结论

| 文件 | 当前状态 | 核对结论 |
|------|---------|---------|
| `README.md` **L5** version badge | `v0.52.0` | 待主 Agent 在 P8 gate 后 bump 至 `v0.53.0`，与 tag 同 commit |
| `CHANGELOG.md` | 最新章节 `## [0.52.0] - 2026-08-18`（TAG0012） | 待主 Agent 新增 `## [0.53.0] - 2026-08-19` 章节（内容见下节，本 releaser 只声明不写入） |
| git tag | `v0.52.0`（`git describe --tags --abbrev=0` 实测） | 发布时创建 `v0.53.0`（主 Agent 执行，与 badge bump 同一 commit） |
| `agate/UPGRADING.md` | 未检查是否需要新增本版本章节 | 本任务无破坏性变更（见上节独立核实），主 Agent 可判断是否需要新增章节说明"新增可选字段/新增模板/新增脚本，无需迁移动作" |

## CHANGELOG [0.53.0] 内容建议（供主 Agent 写入，本 releaser 不直接编辑 CHANGELOG.md）

逐条回查 `P4-implementation.md`「改动清单」1~7 条原文重新组织表述（不套用 TAG0012
P8-release.md 的段落结构），每条追溯到本任务实际改动文件与 BDD 编号：

```markdown
## [0.53.0] - 2026-08-19

### 新增（TAG0015：agate 复盘与反馈机制统一，RM-AG0020 + RM-AG0021）

- **复盘模板迁入协议本体（RM-AG0020，BDD-1~8）**：`docs/reviews/postmortem-template.md`
  git mv 为 `agate/assets/templates/retrospective-template.md`，补齐正文四节结构（事实基线 /
  做得好的 + 可复用模式 / 发现的问题 / 改进措施，BDD-1）、内容价值标准小节（机制缺口 / 可复用
  模式 / 归因到可行动层面的问题，BDD-2）、「发现的问题」节强制"归因层面：机制缺口 / 执行错误"
  二值字段（BDD-3）、技术债登记核对行强制说明（标记"是"必须填 DEBT/roadmap 编号，BDD-4）、
  「做得好的」节两类去向标注 + 强制追问句（BDD-5）、frontmatter 三机器字段
  `mechanism_issues`/`execution_issues`/`feedback_ready`（BDD-6）、「## agate 反馈」结构化节
  （BDD-7）；挂钩点落在 `agate/phase-cards/P8-release.md`「READY 收尾检查」节，模板不再游离
  于协议本体外（BDD-8）；`agate-workspace/roadmap/roadmap.md` 三处旧路径引用同步脚注更正
- **`check-retrospective.py` 路径与触发标的扩展（RM-AG0020，BDD-9~11）**：stderr 提示文案改为
  指向 `tasks/{Txxx}/retrospective.md`，不再提及 `docs/releases/`（BDD-9）；新增
  `_scan_debt_roadmap_signal` 检测分支，任务关联 DEBT/roadmap 条目时输出独立于异常模式的第二段
  "建议复盘"提醒（消息文案可区分，BDD-10），`exit code` 恒为 0 的既有契约未变；
  `agate/tests/unit/test_check_retrospective.py` 新增 3 个测试函数覆盖路径文案与两类信号
  （BDD-11）
- **`orchestrator-log` 语义扩展为"决策 + 依据"（RM-AG0020，BDD-12~14）**：`agate/state-machine.md`
  第 481 行规则文本追加"和触发决策的简要依据"分句（三项既有排除原样保留）；新增「L2 会话
  checkpoint（两件套）——`P{n}-checkpoint.md` + `task-session-summary.md`」小节，回答落盘
  时机/文件路径/与 orchestrator-log 关系/防 compact 策略四问（BDD-13）；核实
  `loop-orchestration.md`/`agate/assets/templates/task-files.md` 既有引用不与新语义矛盾，
  `task-files.md`「辅助文件」表新增两行说明两个 L2 文件（BDD-14）
- **`agate/AGENTS.md` 复盘位置措辞同步（RM-AG0020，BDD-15）**：第 11 行区分"历史存量复盘仍在
  `docs/reviews/`（迁移前旧布局）"与"新复盘归 `tasks/{Txxx}/retrospective.md`"，消除过期声明
  对新复盘同样成立的推论
- **存量 5 份复盘文档标注（RM-AG0020，BDD-16）**：`docs/reviews/retrospective-tag0008-*.md` /
  `retrospective-tag0010-0011-*.md`（含同名 review）/ `retrospective-tag0013-*.md` /
  `retrospective-tag0014-*.md` 首行统一插入历史标注，指向新路径约定，文件原地保留不物理迁移
- **`agate-feedback.py` 新增（RM-AG0021，BDD-17~20）**：新脚本 `agate/scripts/agate-feedback.py`
  从复盘文档提取 `mechanism_issues`/`execution_issues`/「## agate 反馈」节结构化数据（BDD-17，
  ADR-007 合规复用 `agate-md-field-get.py` 单一双读工具，SELF-GATE 重试 #1 修复）；输出脱敏
  （项目名 → `<PROJECT>`，绝对路径按项目根截断/替换 `<PATH>`，BDD-18）；`AGATE_FEEDBACK`
  开关默认 `off`，未启用时不产生任何提取输出，exit code 明确提示功能未启用（BDD-19）；产出物
  为待人工提交的 JSON + Markdown 片段，脚本本身不调用 `git push`/`gh` 等网络提交命令，且不存在
  任何自动触发钩子（BDD-20）
- **`agate-md-field-get.py` 字段注册（ADR-007 合规，SELF-GATE 重试 #1）**：`NO_FALLBACK_BOOL_FIELDS`
  新增 `feedback_ready`，`NO_FALLBACK_LIST_FIELDS` 新增 `mechanism_issues`/`execution_issues`，
  三字段均为 `retrospective.md` 专用，纯新增不影响既有 4 个字段行为

### 测试

- 新增/扩展 `agate/tests/unit/test_check_retrospective.py`（+3 用例，BDD-9/10/11）+ 全新
  `agate/tests/unit/test_agate_feedback.py`（BDD-17~20）+ 全新
  `agate/tests/unit/test_retrospective_protocol_docs.py`（纯文档类 BDD-1/2/3/4/5/6/7/8/12/13/
  14/15/16），三文件合计 35 passed
- 全量 `pytest agate/tests/ -q --tb=no` → 932 passed + 2 skipped + 0 failed（基线 909 passed，
  净增 23，无回归）；`check-protocol-consistency.py --strict` → 0 ERROR（305 WARNING）
- **本版本无破坏性变更**：`check-gate.py` 零改动（独立 diff 验证）；`check-retrospective.py`
  `exit code` 契约不变（独立代码通读验证）；`agate-md-field-get.py` 新字段纯新增不影响既有
  4 个消费字段（独立 diff 验证）；均为面向新场景的加性变更
```

## 发布检查命令清单（从 P2-design.md §5 `gate_commands` 原文抄录，供主 Agent 在 gate 验证阶段
重跑，本 releaser 不重跑）

| key | 命令 | P5 阶段已跑结果（P4-implementation.md 自查记录，仅供参照，非本次结果） |
|---|---|---|
| P3 | `python3 -m pytest agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v` | 35 passed |
| P5 | `python3 -m pytest agate/tests/ -q --tb=no && python3 agate/scripts/check-protocol-consistency.py --strict` | 932 passed, 2 skipped（commit ae7dc57）；0 ERROR / 305 WARNING |

主 Agent 需在 bump 后重跑上表全部命令确认仍全绿，并额外执行：`git log v0.52.0..HEAD --oneline`
对照 CHANGELOG 无遗漏；从 P2 packages 验证 version 文件路径（`README.md` L5）。

## debt_check

- `debt_check: none`
- 已读 `{AGATE_WORKSPACE}/debt/tech-debt.md`：现存 6 条 DEBT。**逐条核对 `task_id`**（非只看
  条目数）：
  - `DEBT0001`：`task_id: TAG0013-script-consistency`，`status: closed`
  - `DEBT0002`：`task_id: TAG0008-version-management`，`status: open`
  - `DEBT0003`：`task_id: TAG0008-version-management`，`status: open`
  - `DEBT0004`：`task_id: TAG0008-version-management`，`status: open`
  - `DEBT0005`：`task_id: TAG0006-ui-ux-quality`，`status: closed`
  - `DEBT0006`：`task_id: TAG0006-ui-ux-quality`，`status: closed`
- 6 条 `task_id` 分别为 `TAG0013-script-consistency`（1 条）、`TAG0008-version-management`
  （3 条）、`TAG0006-ui-ux-quality`（2 条），**无一条为 `TAG0015-retrospective-feedback`，
  evidence 内容亦均与版本管理/离线安装/脚本引用漂移/P6 双证据解析相关，未见任何一条
  evidence 提及 RM-AG0020 或 RM-AG0021**。
- **结论：无本任务相关开放债务项，不阻塞发布。**

## 临时资源清单

本任务全程为纯协议文档 + Python 脚本改动（`agate-feedback.py` 新增 / `agate-md-field-get.py`
字段扩展 / `check-retrospective.py` 新检测分支）。核实 P4/P5/P6 阶段记录（`P4-implementation.md`
自查结果、`P6-acceptance.md` 验收方法节）——均为 `pytest subprocess` 调用协议脚本本身、
`grep`/`git status`/`head -1` 等只读命令，未见任何 debug server 启动记录、临时数据库创建、
端口占用、或 editable/全局包安装动作：

- 无 debug server / 临时 daemon 启动
- 无临时数据库 / 测试数据目录创建
- 无端口占用
- 无 editable install / 全局包安装
- 任务目录内产出（`P0-brief.md` ~ `P7-consistency.md` + `P6-evidence/`21 个证据文件 +
  `P8-progress.md`/`P8-release.md` 本文件）均随 git 管理，非临时资源，无需清理

**如实声明：无临时资源。**

> 主 Agent READY 收尾检查：仅需确认 `git status` 工作区干净后创建 tag `v0.53.0`，无额外环境
> 清理动作。

## Lessons Learned

1. **"新增能力 vs 语义改变"的 bump_type 判定需要逐文件独立读代码验证，不能仅凭"新增分支"字面
   描述下结论**：本任务 `check-retrospective.py`/`agate-md-field-get.py` 均属"新增检测分支/新增
   字段"表述，但 P8 仍独立跑了 `git diff`（确认既有 frozenset 元素未删改）与 `grep sys.exit`
   （确认控制流出口数量未变）两项具体验证，而非直接采信 dispatch-context 给出的判定文字——这是
   P8 角色卡"不要凭空套用其他判定，要给出独立核实依据"的具体落实方式，值得在同类协议机制任务里
   延续。
2. **ADR-007 单一双读工具的合规性检查应前移到 P2/P4 阶段，而非留给 P7/P8 补救**：本任务
   `agate-feedback.py` 首版实现绕开了 `agate-md-field-get.py` 直接 `yaml.safe_load`，是 SELF-GATE
   重试 #1 才发现并修复的合规缺口；P2 设计阶段若显式核对 ADR-007 适用范围（涉及 frontmatter
   字段读取的新脚本一律复用该工具），可以在 P4 首轮实现前就避免这次返工。
3. **debt_check 的"逐条核对而非数条目"纪律在小规模债务清单下同样重要**：本次 tech-debt.md 只有
   6 条且与本任务明显无关，但仍逐条列出 task_id 而非简单写"6 条均不相关"——避免"债务清单增长后
   审查者习惯性跳过逐条核对"的路径依赖提前形成。

## 交接给主 Agent

- [ ] 重跑发布检查命令清单全部命令（exit 0 + failed==0 + 0 ERROR）确认 bump 后仍全绿
- [ ] `git log v0.52.0..HEAD --oneline` 对照 CHANGELOG 无遗漏
- [ ] `README.md` L5 badge `v0.52.0 → v0.53.0` + `CHANGELOG.md` 新增 `## [0.53.0]` 章节（内容
  参照上方建议） → 同一 commit
- [ ] 创建 tag `v0.53.0`（与 bump commit 同点）
- [ ] 按临时资源清单执行 READY 收尾检查（本任务清单为空，仅确认工作区干净）
- [ ] 干净 checkout（或 CI 兜底）跑 `check-protocol-consistency.py` 确认 0 ERROR（P8 卡 READY
  收尾「协议一致性」要求，本地 worktree 结果不能替代）
- [ ] 确认 `agate-workspace/tasks/` 任务产出目录不被一致性检查器误扫（dogfooding 任务，应已在
  `NARRATIVE_DIRS` 白名单，主 Agent 核实一次）
