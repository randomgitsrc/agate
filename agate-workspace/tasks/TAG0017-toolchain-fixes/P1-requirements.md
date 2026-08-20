---
phase: P1
task_id: TAG0017-toolchain-fixes
type: problems
parent: P0-brief.md
trace_id: TAG0017-P1-20260820
status: draft
created: 2026-08-20
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [gate-scripts, hooks-shell, phase-cards, self-gate-template, platform-notes, agent-roles]
domains: [protocol-docs, gate-scripts]
# 跳过风险: 本任务未裁剪任何阶段——risk_level=medium 强制 P1/P2/P4/P5/P6；P3 仅 low 可裁，本任务改
#   4 处解析脚本逻辑需先红后绿（TDD），不可裁；P7 是协议自身改动的一致性交叉检查核心手段，不可裁；
#   P8 是发布必经步骤（本任务终态要提 PR 合并 main），不可裁。故 phases 为完整 P1-P8，无阶段被跳过。
capability_requirements: []
verification_env: "本地 Linux（P0-brief env_constraints.debug_env）：python3 -m pytest agate/tests/ + python3 agate/scripts/check-protocol-consistency.py --strict（worktree 自己的脚本）+ bash agate/tests/scripts/count-tests.sh + shellcheck -S warning agate/scripts/*.sh。Windows 侧（DEBT0014 相关）走 GitHub Actions Windows CI matrix（pytest -m windows_smoke，protocol-tests.yml 已有），本地无法复现真实 Store 占位符 exit 49 行为，只能构造模拟 stub 做单测/回归覆盖"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录"
---

[NO_NEED_CONFIRM]

## 0. P0-brief 时效性质疑

已核对 P0-brief.md 时效性，判定：**局部计数漂移（轻微），非目标方案漂移**。

`[P0_STALE: P0-brief.md 顶部 task 字段文案写"修复 4 个真实、未修复、影响后续任务的系统缺陷"，但下方 issues 列表实际含 5 条（DEBT0010/DEBT0011/DEBT0012/DEBT0014/RM-AG0028-DEBT0015）——DEBT0014 是 2026-08-19 用户跨项目反馈汇入后追加进 issues/known_risks 的，task 字段的"4 个"文案未同步更新为"5 个"]`

严重性判定（对照 P0 卡片漂移判据 1-3）：
- `task` 目标方案是否不再成立？否——issues 列表本身完整包含全部 5 条，方案未变，只是概述句的数字未跟上。
- `executor_env` 平台前提是否不再成立？无相反证据（本次会话为 subagent 执行环境，未观察到 bash/网络/文件系统能力与声明不符）。
- `known_risks` 的"已解决前提"是否已失效或被他任务解决？已逐条核对（含 DEBT0011 的"TAG0016 已手工恢复一次，确认无其他遗留"——本次 P1 重新核对 `docs/reviews/` 现存文件清单，确认无新的同名覆盖残留，该前提仍成立）。

三条严重判据均不命中 → 不阻塞，按"记录"处理。本 P1-requirements.md 已按 issues 列表的完整 5 条展开需求（不受 task 字段计数误差影响）。**受影响字段**：P0-brief.md 顶部 `task` 字段的"4 个"文案。本文件锁定 P1-requirements.md 单一产出路径，不直接改写 P0-brief.md；建议主 Agent 后续同步把该文案改为"5 个"（非阻塞，不影响本次 P1-P8 推进）。

## 1. 需求复述

TAG0017 要修复 agate 协议工具链的 5 个已核实、未修复、影响**每一个后续任务**的系统缺陷（RM-AG0027 + RM-AG0028，源自 TAG0016 复盘 + TQC0001 跨项目反馈）：

1. **DEBT0010**：4 个 gate_commands 解析脚本（`agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-gate-p5-count.py` / `agate-read-p5-commands.py`）只排除 `_formatter` 后缀键，未排除 `_timeout_seconds` 后缀键，导致 P2/P3/P5 三阶段 gate 判定被误导（假 WARNING / 误判红灯类别 / 假命令计数）。
2. **DEBT0011**：SELF-GATE.md 的审查文件命名模板只含日期不含任务标识，同日多任务各自触发审查会同名覆盖彼此的历史记录。
3. **DEBT0012**：`check-protocol-consistency.py --strict` 模式下 WARNING-only 也 `exit 2`，与 `gate_commands.P5` 常见的 `&&` 链路组合时，存量 WARNING 未清零会导致链路后续步骤永久执行不到（短路）。
4. **DEBT0014**：3 个 git hook 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`）的 python 探测循环在 Windows 上可能命中 Microsoft Store 的 `python3.exe` 占位符（`command -v` 能找到，但 exec 非交互模式返回 exit 49），导致 hook fail-closed 阻断 commit。
5. **DEBT0015/RM-AG0028**：`env_constraints` 是纯声明性字段（协议所有引用只做"确认/细化 + 注入 subagent 上下文"），没有任何 gate/脚本对其中的执行性约束（如 deploy 类）做强制校验，导致声明了却从未被主动执行的情况（TQC0001 实证）。

明确排除范围：DEBT0013（已在 PR #166 修复）、DEBT0009（已单独关闭）不在本任务范围内。若 P2 设计阶段发现需改动超出以上 5 条锁定范围，须先停下与用户确认，不擅自扩大。

## 2. 隐含需求识别

- **回归测试覆盖，不仅是"改对"**：DEBT0010 的修复必须同时证明"P3 声明 timeout_seconds 时真红灯仍被正确判定为 A 类失败"——否则修复本身可能变成"放宽判定"这一更危险的回归（详见 BDD-2）。用户/P0-brief 均未明说这条，但技术上是必须的护栏。
- **同类遗漏拦截机制**：DEBT0010 是 4 处同类缺陷同时存在，说明这类"新增脚本忘记排除某后缀键"的错误会复发。需要一个可自动捕获"第 5 处遗漏"的机制（共享判据函数或审计测试），而不是只改这 4 处就算完（详见 BDD-4，同类扫描已确认当前无第 5 处，但需要防止未来新增）。
- **文档增量声明 vs 实测断言的区分**：DEBT0014 涉及 Windows 行为，但本环境（Linux）无法真实复现 Store 占位符的 exit 49 场景。隐含要求是：验收证据必须诚实区分"静态修复 + Linux 模拟回归 + CI matrix 验证"与"已在真实 Windows 环境实测通过"，不能把前者包装成后者（P0-brief 约束 3 已明说，但需要落到具体 BDD 的验证方式描述里，不能只在自然语言约束里存在）。
- **P2/P4 设计整合点，不是两次独立设计**：DEBT0010 与 DEBT0015 都触及"`gate_commands` 是真正被执行的机制、`env_constraints` 是声明性字段"这条边界。若 P2 分两次设计（各自只顾自己那条 issue），容易出现"DEBT0010 的修复暗示 gate_commands 就该无所不包"与"DEBT0015 的修复暗示 env_constraints 该有独立执行通道"两种口径打架。需求层面必须把这条边界作为一个整体表述（本文件已按此归并为「功能分组 1」）。
- **历史任务产出不可回改，但要防复发**：同类扫描发现 8 个历史任务的 P2-design.md 已经用了"--strict 放进 && 链路中间"这个反模式（TAG0004/9/12/14/15/16）。这些是已完成任务的既定产出，不能回改，但隐含要求是：P2 卡片的 `gate_commands` 声明指引必须新增"不要这样做"的提示，否则未来任务还会重蹈覆辙（详见 BDD-9 关联的同类扫描结论）。
- **无用户界面/前端受影响**：5 条缺陷全部是脚本逻辑、shell 探测逻辑、协议 Markdown 文档的改动，没有任何用户可见的 UI/交互面。因此本任务不适用 UX 类别 BDD 与 `ui_render_shape`/`ui_ux_dimensions` 声明（domains 不含 frontend）。
- **多端同步**：本任务改动对象是 agate 协议本体（Python gate 脚本 + bash 薄壳 + Markdown 协议文档），不存在 MCP/CLI/API 多端分叉的问题——所有"端"就是这一套脚本 + 文档，本身已经是"单一实现"，不需要额外同步动作。
- **边界情况**：DEBT0010 需要覆盖"值为纯数字字符串"（`timeout_seconds` 声明本身就是整数值）这一边界；DEBT0012 需要覆盖"WARNING 数量非零但 ERROR 为零"这一当前长期存在的真实基线状态（314 条历史 WARNING），不是构造出来的边界情形。
- **兼容性**：所有修复必须保持现有 950 pytest 全绿 + `check-protocol-consistency.py --strict` 0 ERROR（P0-brief 约束 2，回归基线不可破）。

## 3. 同类扫描结论（强制节，6 类扫描全部已执行）

> 完整 grep 命令与原始输出见 `P1-progress.md`。以下为分类归纳后的结论。

### 3.1 `_timeout_seconds` 全仓扫描（找 DEBT0010 之外第五处遗漏消费点）

命中约 44 个文件。分类处理判定：

| 分类 | 代表文件 | 处理判定 |
|---|---|---|
| 目标解析脚本（4 处，DEBT0010 核心） | `agate-read-gate-commands.py`（L31）/ `agate-gate-missing-cmds.py`（L20）/ `agate-gate-p5-count.py`（L23）/ `agate-read-p5-commands.py`（L29） | **本次处理**——均只判 `key.endswith("_formatter")`，从未引用 `_timeout_seconds`，这正是缺陷本身 |
| 间接消费方（3 处） | `agate-capture-env-baseline.py` / `agate_common.py` / `check-tdd-red.py` | **本次不处理**——均通过 `subprocess` 调用 `agate-read-gate-commands.py` 取数据（`check-tdd-red.py` 的 `_read_gate_commands()` 实测确认走 subprocess），不做独立 key 后缀解析，不构成第 5 处 |
| 协议文档声明侧（正确用法） | `architect.md` / `phase-cards/P2-design.md`（`{key}_timeout_seconds` 字段规则节） / `dispatch-prompt.md` / `task-files.md` / `UPGRADING.md` / `CHANGELOG.md` | **本次不处理**——这些是"如何声明该字段"的正确文档说明，不是解析逻辑 |
| `agate-workspace/` 任务历史产出 | `TAG0012`/`TAG0015`/`TAG0016`/`TAG0017` 各阶段文件、`roadmap.md`、`tech-debt.md` | **本次不处理**——历史记录/既有 debt 登记，不可回改 |

**结论**：确认仅 4 处解析缺陷点（DEBT0010 已知范围），无第 5 处遗漏消费点。回归拦截需求见 BDD-4。

### 3.2 `agate-alignment-review-{date}` 及同类纯日期命名模式扫描（DEBT0011 同类命名引用）

命中约 85 个文件。分类处理判定：

| 分类 | 代表文件 | 处理判定 |
|---|---|---|
| 活跃协议源（模板定义 + 消费引导） | `SELF-GATE.md`（根目录，L53/54/133/143/183/193）/ `agate/assets/review-roles/protocol-alignment-review.md`（L118） | **本次处理**——DEBT0011 核心，命名模板缺任务标识 |
| 提示文案（非强制格式） | `agate/scripts/commit-msg-self-gate.py`（L80，示例字符串 `self-gate-review: docs/reviews/agate-alignment-review-{date}.md`） | **本次不处理，可选同步**——理由：该字符串只是 commit message 里 `self-gate-review:` 后缀的示例文案，脚本只校验前缀存在性不校验具体文件名格式，命名规则变化不影响功能，不阻塞验收 |
| 历史生成产物 | `docs/reviews/*.md`、`archived/docs-2026-08/reviews/*.md`、各任务 `agate-workspace/tasks/*/P*.md` 里对既有审查文件路径的引用 | **本次不处理**——历史记录/历史任务对自己当时生成文件路径的引用，语义正确，不受命名规则变更影响 |
| 测试 fixture | `agate/tests/integration/test_commit_msg_self_gate_integration.py`（L82） | **本次不处理**——测试只断言 `self-gate-review:` 前缀存在性，不校验具体文件名模式 |

**结论**：真正需要修改的活跃协议源文件 2 处，已确认无第 3 处需要处理的活跃协议逻辑源。另确认 `docs/reviews/` 当前文件列表（`agate-alignment-review-2026-08-19.md` 与 `agate-alignment-review-2026-08-19-tag0016.md` 并存）证实 TAG0016 已用手工加后缀方式规避过一次同名覆盖，当前无其他遗留冲突。

### 3.3 `--strict` 在 gate_commands 声明/协议文档中的所有使用点（DEBT0012 影响面）

| 分类 | 代表文件 | 处理判定 |
|---|---|---|
| 脚本本身 | `check-protocol-consistency.py`（L27 docstring、L1079 `--strict` flag 定义、main() 尾部 `if rep.warnings and args.strict: return 2`） | **本次处理**——DEBT0012 核心 |
| 独立命令示例（非链路短路模式） | `agate/assets/templates/handoff-template.md`（L35/63/65/108，均为单条命令示例，不在 `&&` 链路中间） | **本次不处理**——不构成 DEBT0012 描述的短路模式，属良好示例 |
| 历史任务 P2-design.md 的 `&&` 链路模式 | `TAG0004`（L337）/ `TAG0009`（L289）/ `TAG0012`（L299）/ `TAG0014`（L220）/ `TAG0015`（L438）/ `TAG0016`（L307/312）均把 `--strict` 放进 `pytest && consistency --strict && ...` 链路中间；`TAG0013`（L223 明确写"P5_consistency 不用 --strict"）已主动规避 | **本次不处理个别历史文件**——理由：已完成任务的既定产出，不可回改；**但需转化为回归拦截**：P2 卡片 `gate_commands` 声明规则需新增指引避免未来任务复现同一反模式（对应 BDD-9） |
| 独立 key 拆分声明（非同串 `&&` 链路） | `TAG0005`（L250）/ `TAG0010`（L273）/ `TAG0011`（L382）三处 `P2-design.md` 均把 `--strict` 写在独立的 `P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict ..."` key 里，不是 TAG0004 式同一字符串内 `pytest && consistency --strict && ...` 链式拼接 | **本次不处理，但判定为同一反模式的变体、需一并纳入 P2 卡片新增指引覆盖范围**——理由：`P5-verification.md` 未明确规定 P5 阶段执行多个 `P5_*` key 时是否会把它们再拼接成一条 `&&` 链（若拼接，短路风险与 TAG0004 式完全等价；若不拼接，`--strict` 单独执行时若前序 WARNING 未暴露则仍可能被静默跳过判读）。由于无法排除等价短路风险，按更保守的口径纳入同一反模式处理，BDD-9 对应的指引新增范围需同时覆盖"链式拼接"与"独立 key 声明"两种形态，不只针对 TAG0004 式写法 |

**结论**：确认 7 个历史任务已踩过或规避过这个反模式（6 个 `&&` 链路命中 + 1 个主动规避 `TAG0013`），另有 3 个历史任务（TAG0005/TAG0010/TAG0011）以独立 key 形态声明了同一命令、按保守口径一并计入需覆盖范围，证明这不是孤立一次性问题，需要在协议文档层面新增拦截指引，不能只改脚本本身。

### 3.4 `env_constraints` 全协议引用点 + 各引用点对应 gate_commands 消费情况（DEBT0015 影响面）

命中 13 处协议语义引用：`dispatch-protocol.md` / `state-machine.md` / `WORKFLOW.md` / `phase-cards/P0-orchestrator.md` / `phase-cards/P1-requirements.md` / `phase-cards/P2-design.md` / `phase-cards/P4-implementation.md` / `assets/execution-roles/analyst.md` / `assets/execution-roles/architect.md` / `assets/templates/dispatch-context.md` / `assets/templates/dispatch-prompt.md` / `assets/templates/task-files.md` / `agate-extract-context.py`。

逐条核实消费方式：全部 13 处均为"确认/细化 + 注入 subagent 上下文"的声明性语义（`agate-extract-context.py` L107-109 的 P1 分支实测确认只做字符串抽取拼接注入，无执行判断逻辑）。`check-gate.py` 对 `deploy` / `env_constraints` 关键词 grep 结果均为 0 命中，确认当前无任何 gate 脚本对 `env_constraints` 做执行性校验。

处理判定：
- **本次处理**：`phase-cards/P2-design.md`（gate_commands 声明节新增边界说明）+ `assets/execution-roles/architect.md`（同步说明）+ `phase-cards/P4-implementation.md`「自查≠gate」节（新增 deploy 类约束提醒）——对应 BDD-5/BDD-6
- **本次不处理**：其余 10 处声明性引用点——理由：均为"注入/确认细化"语义的既有正确用法，不需要改变其声明性质，只需要新增一处清晰的边界说明文档（已在处理点覆盖，不需要逐个改写）

**测试基础设施类命中（独立 grep 全仓另发现，未计入上述 13 处协议语义引用）**：`agate/rules/state-transitions.md`（P0-brief 四字段自查清单提及 `env_constraints` 作为勾选项名称）、`agate/tests/conftest.py`、`agate/tests/fixtures/{full-task,high-risk,paused-task,ui-affected,vision-blocked}/P0-brief.md`（5 个 fixture）、`agate/tests/unit/test_check_retrospective.py`。**归类判定：不计入协议语义引用点，本次不处理**——理由：`state-transitions.md` 的命中是自查清单里的字段名勾选项，不是对该字段做语义解释或消费；`conftest.py`/`test_check_retrospective.py`/5 个 fixture 的 `P0-brief.md` 命中均是测试固件里的字面量（构造测试数据/断言字段存在），不驱动任何执行判断，也不是"协议文档对 `env_constraints` 语义的声明或消费"，与本节标题限定的"协议引用点"不属同一范畴，故不与上述 13 处协议语义引用合并计数，也不新增处理项。

**结论**：确认 `env_constraints` 目前是纯声明性字段，零执行绑定，与 P0-brief 描述完全一致。

### 3.5 `command -v` / 薄壳探测循环相关扫描（防同类平台探测陷阱，不限于已知 3 薄壳）

| 分类 | 代表文件 | 处理判定 |
|---|---|---|
| 同结构探测循环（3 处） | `pre-commit-gate.sh`（L15）/ `commit-msg-self-gate.sh`（L16）/ `pre-push-gate.sh`（L16），逐字对比确认循环体完全一致：`for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done` | **本次处理**——DEBT0014 核心，"三薄壳同批改" |
| 静态扫描器豁免匹配代码 | `check-platform-assumptions.py`（L51，`if "command -v python3" in text ...`） | **本次不处理**——这是识别"探测惯用法"作为 R2 豁免形态的扫描器代码本身，不是探测循环 |
| pytest 探测（不同实现路径） | `check-tdd-red.py`（docstring L44 提及 `command -v pytest → shutil.which`，实际实现用 Python `shutil.which`） | **本次不处理**——探测目标是 `pytest` 而非 `python3` 解释器本身，且用 Python 标准库 `shutil.which` 而非 shell `command -v`，不构成同一类 Store 占位符 exec 风险路径；若未来需要覆盖此路径需单独确认，超出本次 P0-brief 锁定范围 |

**结论**：确认 3 处同结构探测循环（P0-brief 已知范围），无第 4 处。

### 3.6 `python3` / `WindowsApps` / `Store` 关键词扫描（防同类跨平台兼容性陷阱）

对 `WindowsApps` / `Microsoft Store` / `Store 占位符` / `AppExecAlias` 关键词做全仓扫描（含 `agate/platform-notes.md`、根 `AGENTS.md`、根 `CLAUDE.md`）：**0 命中**。

**结论**：确认协议层此前从未记录 Store 占位符问题（与 P0-brief"AGENTS.md/CLAUDE.md 已知但 protocol 层未处理"的描述一致——本次核对发现连 AGENTS.md/CLAUDE.md 本身也未记录，这是全新增补，不是"已有描述但协议层没跟上"）。`platform-notes.md` L152「已知限制（Windows 原生）」表当前只列 3 条（`ln -sf` 退化为复制 / pytest 需安装 / 3 hook 需 sh），是明确的插入点。对应 BDD-12。

## 4. BDD 验收条件

### 功能分组 1：gate_commands 是执行机制、env_constraints 是声明性字段（DEBT0010 + RM-AG0028/DEBT0015 整合归并）

> 涉及文件：`agate-read-gate-commands.py` / `agate-gate-missing-cmds.py` / `agate-gate-p5-count.py` / `agate-read-p5-commands.py`（可选抽共享判据函数到 `agate_common.py`）；`phase-cards/P2-design.md`「gate_commands 声明」节；`assets/execution-roles/architect.md`；`phase-cards/P4-implementation.md`「自查≠gate」节。
> 这两条 issue 必须整体设计的边界：**`gate_commands` 是真正被执行的机制，`env_constraints` 是声明性字段（仅信息注入）**——任何需要被强制执行的约束必须落到 `gate_commands` 或 P4/P8 显式 checklist，二者不能混淆。

#### BDD-1: P2 阶段声明 `{key}_timeout_seconds` 不再被误判为待核实命令
- Given P2-design.md 的 `gate_commands` 块声明了 `P5_timeout_seconds: 120`（纯整数字符串值，无路径无 `=`）
- When 主 Agent / check-gate.py 读取 `gate_commands` 生成"待核实命令清单"
- Then 清单中不出现以 `_timeout_seconds` 结尾的 key 对应的假"命令不存在"判定

#### BDD-2: P3 阶段声明 timeout_seconds 时真红灯仍正确判定为 A 类失败
- Given P2-design.md 同时声明了 `P3_timeout_seconds` 与真实会失败（非超时）的 P3 测试命令
- When `check-tdd-red.py` 判定该次测试运行结果的失败类别
- Then 判定结果仍为 A 类真实失败（对应 exit 1 分支），不因新增的 `_timeout_seconds` 排除逻辑而被误判为其他类别或被放宽为通过

#### BDD-3: P5 阶段命令计数不含 timeout_seconds 声明键
- Given P2-design.md 的 `gate_commands` 块含一条 `P5:` 主命令 + 一条 `P5_timeout_seconds: 120` 超时声明
- When `agate-gate-p5-count.py` 统计主命令数与辅助命令数
- Then 统计结果为"1 主命令 + 0 辅助命令"，`P5_timeout_seconds` 不被计入辅助命令

#### BDD-4: 同类遗漏拦截——防止未来新增第 5 处未排除 `_timeout_seconds` 的解析点
- Given 仓库新增或修改任意一个解析 `gate_commands` 块 key 后缀的脚本
- When 该脚本对 `_formatter` 后缀做了排除但未同时排除 `_timeout_seconds` 后缀
- Then 回归测试套件中存在能捕获该遗漏的用例（审计断言或共享判据函数的单测），使 pytest 整体运行失败

#### BDD-5: env_constraints 声明性字段与 gate_commands 执行机制的语义边界已文档化
- Given 读者查阅 `phase-cards/P2-design.md`「gate_commands 声明」节或 `architect.md` 角色文件
- When 读者查找"`env_constraints` 里声明的约束是否会被自动执行"这一问题
- Then 文档明确给出结论：`env_constraints` 是声明性字段（仅用于信息确认/注入），任何需要被强制执行的约束必须落到 `gate_commands` 或 P4/P8 明确 checklist，二者不等价

#### BDD-6: UI 类任务的部署类执行性约束在 P4 后有显式检查提醒
- Given 某任务 P2-design.md 的 `env_constraints` 声明了 deploy 类约束（如构建 dist / 打包产物）
- When implementer 完成 P4 实现后对照 `phase-cards/P4-implementation.md`「自查≠gate」节自查
- Then 该节包含"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"的显式提醒条目

### 功能分组 2：SELF-GATE 审查文件命名去重（DEBT0011，与分组 1/3/4 无域重叠，独立成组）

> 涉及文件：`SELF-GATE.md`（根目录，命名模板定义）；`assets/review-roles/protocol-alignment-review.md`（消费引导）。

#### BDD-7: 同日不同任务的 SELF-GATE 审查文件不再同名覆盖
- Given 两个不同任务（如 TAG0015 与 TAG0016）在同一日期各自触发 protocol-alignment-review
- When 两次审查各自按 `SELF-GATE.md` 模板生成留痕文件与成果文件
- Then 两次生成的文件名不同（命名模板含任务标识），两次产出互不覆盖

#### BDD-8: subagent 写入前检查目标路径存在性，避免误覆盖历史记录
- Given protocol-alignment-review subagent 即将用 Write 工具写入审查产出路径
- When 目标路径已存在同名文件
- Then subagent 先判断该文件是否属于同一任务的复核轮（可覆盖）还是别的任务遗留（不可覆盖，需改用带任务标识的新文件名），不无条件覆盖

### 功能分组 3：check-protocol-consistency --strict 与 && 链路短路修复（DEBT0012，与分组 1/2/4 无域重叠，独立成组）

> 涉及文件：`check-protocol-consistency.py`；`phase-cards/P2-design.md`「gate_commands 声明」节（新增指引，防止历史反模式复现，见同类扫描 3.3）。

#### BDD-9: WARNING-only 场景下 gate_commands.P5 链路后续步骤仍会被执行到
- Given 协议一致性检查结果为 0 ERROR、若干条 WARNING（当前基线 314 条历史叙事死链，短期内不会清零）
- When 主 Agent 按某任务 `gate_commands.P5` 声明的链路顺序执行验证（pytest → 一致性检查 → 测试计数等多步）
- Then 链路中一致性检查之后的步骤确实被执行到并产出各自的结果，不因一致性检查步骤命中"WARNING-only 也判非 0"而导致后续步骤被短路跳过

### 功能分组 4：Windows Store python3 占位符命中 hook 探测循环（DEBT0014，三薄壳同批改，与分组 1/2/3 无域重叠，独立成组）

> 涉及文件：`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`（同结构探测循环，三者一并修改）；`platform-notes.md`「已知限制（Windows 原生）」表 + 「Windows 原生」章节；`AGENTS.md`「升级 agate」段。
> 验证方式声明（P0-brief 约束 3，不得夸大）：本环境为 Linux，无法真实复现 Windows Store 占位符的 exit 49 行为，验收证据只能是"静态修复 + 构造模拟 stub 的 Linux 回归测试 + CI matrix（`pytest -m windows_smoke`）冒烟验证"，不得声称"已在真实 Windows 环境实测通过"。

#### BDD-10: 探测循环命中不可执行的候选时能继续探测下一候选
- Given `python3` 候选在可执行性小测试中判定为不可用（如返回特定 exit code，或输出内容包含判定为不可用的特征字符串）
- When 3 个 hook 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`）执行 python 探测循环
- Then 该候选被跳过，探测继续尝试下一候选（`python`），最终解析到可正常执行的 Python 解释器；此行为在 Linux 上通过构造模拟不可执行候选的回归测试验证，Windows 真实场景由 CI matrix 冒烟兜底

#### BDD-11: 显式指定的 Python 路径可跳过探测循环
- Given 用户通过环境变量显式指定了 Python 解释器路径
- When hook 薄壳启动
- Then 薄壳直接使用该显式路径，不执行 `command -v` 探测循环

#### BDD-12: Windows 已知问题已在协议文档中说明
- Given 读者查阅 `platform-notes.md`「已知限制（Windows 原生）」表、「Windows 原生」章节，或 `AGENTS.md`「升级 agate」段
- When 读者检索 Windows 环境下 python3 探测相关的已知问题
- Then 能找到 Store 占位符现象的说明条目 + 显式指定 Python 路径机制的文档条目，且条目文案不包含"已在 Windows 实测通过"一类断言

## 5. 待确认清单

`[NO_NEED_CONFIRM]`

本次未发现需要人工拍板业务方向的开放问题。以下两处技术实现选择留给 P2 architect 按方案空间自行设计，不构成 P1 层面的方向性分歧：
- DEBT0012 的具体修复路径（P0-brief 原文"二选一或都做"：仅调整 P2 卡片指引 / 新增 `check-protocol-consistency.py` 的独立 CLI 模式），BDD-9 只约束行为结果（链路不短路），不预设实现方案。
- DEBT0014 的 Store 占位符识别阈值（exit code / stderr 内容特征 / 路径特征），BDD-10 只约束行为结果（可跳过不可用候选），不预设具体判据实现。

## 6. 能力需求声明

```yaml
capability_requirements: []
```

本任务不需要浏览器/视觉/外部网络等特殊 agent 侧能力——5 条缺陷全部是脚本逻辑改动（Python/bash）+ Markdown 协议文档改动，验收手段是 pytest + `check-protocol-consistency.py` + `count-tests.sh` + `shellcheck`（均为本地命令行工具，非交互式 UI）。

真正的环境限制是"运行环境"类而非"能力"类（见判断树：换更强的模型/角色做不到，只能换有真实 Windows 的机器），已按 `verification_env` 声明处理（见文件头 frontmatter），不走 `capability_requirements` 三态：

```yaml
verification_env: "本地 Linux（P0-brief env_constraints.debug_env）：python3 -m pytest agate/tests/ + python3 agate/scripts/check-protocol-consistency.py --strict + bash agate/tests/scripts/count-tests.sh + shellcheck -S warning agate/scripts/*.sh。Windows 侧（DEBT0014）走 GitHub Actions Windows CI matrix（pytest -m windows_smoke），本地无法复现真实 Store 占位符 exit 49 行为"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录"
```

## 7. 范围声明

已在文件头 frontmatter 声明（`packages:` / `domains:`），不在正文重复。
