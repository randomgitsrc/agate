---
task_id: TAG0016
mechanism_issues:
  - "4 个 gate_commands 键解析脚本（agate-read-gate-commands.py/agate-gate-missing-cmds.py/agate-gate-p5-count.py/agate-read-p5-commands.py）均只排除 _formatter 后缀、未排除 _timeout_seconds 后缀，把正常声明的超时字段误判为待执行命令/待核实项（DEBT0010，本次实测在 P2/P3/P5 三个阶段各复现一次）"
  - "SELF-GATE.md 的 protocol-alignment-review 成果文件/留痕文件按纯日期命名（不含任务标识），跨任务同日复用会静默覆盖已提交的历史审查记录——本次实测复现，TAG0016 的审查一度覆盖了 TAG0015 已合并入 main 的历史记录，靠主 Agent 手工 git diff 核对才发现并恢复（DEBT0011）"
  - "check-protocol-consistency.py --strict 在'仅 WARNING 无 ERROR'时返回 exit 2，与 gate_commands.P5 的 && 串联组合会因本仓库长期存量 WARNING 债务（300+ 条历史叙事文件死链引用）永久短路中断，且这个组合缺陷此前从未被发现——根因是历史验证流程习惯性用 `command | tail -N; echo $?` 管道模式核对 exit code，管道会让 $? 变成 tail 的退出码而非目标命令的真实退出码，本任务自己也在 P4 阶段踩过同一验证方法陷阱，改用不经管道的直接核对方式才发现（DEBT0012）"
  - "check-protocol-consistency.py 的 CHECK 7（README version badge 与最新 git tag 一致）与 gate_commands.P5 的调用时机存在结构性冲突：P8 阶段版本文件必须先于 commit+tag 被修改，但 CHECK 7 要求 badge == 最新 tag，导致'bump 后、tag 前'这个必经的中间状态下重跑 gate_commands.P5 必然触发该 ERROR——本次通过调整重跑顺序（commit → tag → 再重跑）规避，但协议文档（P8-release.md「主 Agent 必须亲自执行」节）未明确说明这一时序依赖，容易被后续任务误判为真实回归"
execution_issues:
  - "P1-P4 阶段多次使用 worktree 自己的 `agate/scripts/agate-inject-card.py`（相对路径）注入 AGATE_CARD，而非 HANDOFF-TAG0016.md 明确要求的 `~/.agate/scripts/agate-inject-card.py`（稳定版工具）——该脚本自身的 AGATE_ROOT 解析逻辑会向上溯源到脚本所在目录，导致从 worktree 内运行时读取的是 worktree 正在被修改的协议卡片副本，而非稳定基线。P5 阶段发现 P5-verification.md 卡片（被本任务 M20 修改过）被注入了尚未发布的新机制内容后才定位到问题并改正，此前 P1-P4 阶段未产生实际损害是因为那几张卡片当时还未被本任务修改，纯属侥幸"
  - "P1 阶段一处 gate-diagnosis.md 撰写时，引用 dispatch-protocol.md 禁止格式的示例文本被 Markdown 自动换行切断，导致某一物理行行首恰好出现 `[PROD_TOUCHED]` 字面串，触发 pre-commit hook 的误判拦截——是自己在诊断文档里引用禁用格式示例时没有意识到换行会产生行首碰撞，修改措辞后规避，未造成实质影响"
feedback_ready: true
---

[PROD_NOT_TOUCHED]

# TAG0016 复盘 — agate 协议卫生与测试效率（RM-AG0025 + RM-AG0026）

> 撰写者：orchestrator（编排 Agent），合并后在主 checkout 撰写，路径遵循 `tasks/{Txxx}/retrospective.md` 约定（沿用 TAG0015 落地的新机制）。

## 一、事实基线

- 任务周期：2026-08-17 立项（P0）→ 2026-08-19 完成合并（PR #164 merge commit `7f27ce0`）
- 阶段：P0-P8 全部走完，无裁剪（`phases: [P0...P8]`，risk_level: high）
- 版本：v0.53.0 → v0.54.0（minor，无破坏性变更）
- BDD：19 条，19/19 PASS，0 FAIL
- 重试记录（`.state.yaml`）：P1 2 次（第 1 轮 requirements-review needs-revision，BDD-12 provenance
  存储表述"既成事实语气"问题；第 2 轮纯格式修复，正文误引用 `[NEED_CONFIRM]` 字面标记文本触发
  gate 拦截）、P2 1 次（plan-eng-review 阻塞：审计 7 的 git diff 失败路径静默判定"无改动"，用真实
  历史 commit `5bdcd90` 复现）、P4 1 次（P4-review 发现 2 个 CRITICAL：审计 7 未检查 git 命令
  返回码 + CHECK 12 的 `redeclares_table` 无范围扫描误报风险，均已用真实场景复现并修复验证）；
  另有 2 次 subagent 因主 Agent 账号月度 API 花费上限中断（P3、P7 各一次），均在"尚未产生任何
  实质产出"阶段中断，按既有先例（同一角色原样重派非"调整重派"）不计入正式重试计数
- DESIGN_GAP：1 条（P2 假设 `dispatch-prompt.md` 已是 `dispatch-protocol.md` 内联模板的完整
  超集，实现时发现反向缺口——refactor 任务两段内容缺失），P7 已用 `git show` 逐字核对确认为
  纯内容迁移后配对 `[DESIGN_GAP_REVIEWED: 已确认]`
- SCOPE+：0 条（全仓核实，P1§8 声明"无"与实际一致）
- 非核心 DEVIATION：1 条（`verifier.md`/`adr.md` 两处改动超出 P2 声明的 8 个 `packages` 范围，
  溯源为 SELF-GATE Layer 1 语义审查产物，P7 判定不阻塞并附 SUGGEST）
- 改动文件：新增 1 个测试文件（`test_protocol_dedup_audit.py`）+ 1 个 ADR（ADR-010）；修改
  2 个 gate 脚本（`check-protocol-consistency.py` 新增 CHECK 12、`check-p6-provenance.py`
  新增审计 7 + `--audit7-only` CLI）+ 8 份协议文档去重（WORKFLOW.md/dispatch-protocol.md/
  state-machine.md/platform-notes.md/rules/state-transitions.md/dispatch-prompt.md/
  verifier.md + 3 张 phase-cards）+ 2 个既有测试文件扩充 + 1 处 CI 配置
- 全量测试：916（P0-brief 声明基线，改动前）→ 966 passed + 2 skipped（净增 50，0 回归）；
  `count-tests.sh` 968 用例（≥ 749 迁移基线）
- CI（PR #164）：18/18 全绿（pytest/shellcheck/consistency/gate-backstop/ruff/platform-scan，
  ubuntu + windows 双平台，两次 workflow run 均全绿）
- 技术债登记：4 条（DEBT0009/0010/0011/0012），另在复盘撰写阶段发现 1 条协议文档未明确说明的
  时序依赖（CHECK 7 vs P8 重跑顺序，见下方问题 5），一并登记

## 二、做得好的 + 可复用模式

- **主 Agent 对每个 subagent 的自我报告都独立复核，而非直接采信**——本任务多次抓到 subagent
  自我总结与实际产出的细微出入（如 P3 test-designer 汇报"4 条新增测试"实际是 3 条、P4 批次 B
  汇报 `--strict` exit code 与独立核实结果不一致），均在合并前订正。去向：**回馈 agate**
  （这是 C7 规则"subagent 自我报告不可信"的一次完整实践，证明该规则在长链路多轮派发场景下
  依然必要，不需要新动作）。
- **P4-review（偏执 Staff Engineer 视角）两个 CRITICAL 均带真实复现，不是猜测式挑刺**——审计 7
  的 fail-closed 缺陷用伪造不存在的 40 位哈希实际跑出了"应拦截却放行"的结果；CHECK 12 的误报
  风险用真实构造的"小节外无关表格"场景验证。去向：**回馈 agate**（review 角色"先复现再下
  结论"的工作方式值得作为同类评审的范式，记录为正面案例）。
- **发现协议工具自身的系统性缺陷时，没有止步于修复触发场景，而是主动同类扫描**——DEBT0010
  从"P3 阶段一处 `_timeout_seconds` 解析 bug"经过 grep 全仓 `_formatter` 排除模式，扩展为登记
  4 个脚本的同一缺陷；DEBT0011 的文件命名冲突被发现后立即溯源检查是否已经覆盖了其他任务的
  历史记录（而不是简单地"改个文件名绕过"）。去向：**回馈 agate**（这正是本任务 RM-AG0025 本身
  倡导的"系统排查而非只修报告的那一处"方法论，用在协议工具链自己身上是一次有效的自举验证）。
- **serial 三批次拆分（doc-dedup → check12-anti-recurrence → test-evidence-provenance）** 让
  risk_level=high 的大改动面（8 份文档 + 2 个脚本 + CI 配置）始终保持小步可回退——每批独立
  commit、独立验证，P4-review 发现的 2 个 CRITICAL 都能精确定位到具体批次的具体函数，未出现
  "一大坨改动混在一起难以归因"的情况。去向：**回馈 agate**（dispatch_plan 的 serial 模式在
  高风险协议自身改造任务上的一次成功实践，可作为未来同类任务的参照案例）。

**本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？**——本任务未产生项目特定
的临时命令/脚本（agate 自身即协议项目，"项目侧"与"agate 侧"是同一件事），故不适用「项目资产
沉淀」这一去向，全部可复用项归入「回馈 agate」。

## 三、发现的问题

- **问题 1**：`gate_commands` 键解析脚本系统性未排除 `_timeout_seconds` 后缀（4 处，DEBT0010）。
  归因层面: 机制缺口
  说明：P2 卡片「`{key}_timeout_seconds` 字段规则」是 TAG0012 引入的正式协议字段，但当时未
  同步排查全部消费该字段格式的解析脚本，导致字段声明与脚本解析之间产生了系统性的盲区——协议
  规则本身没有问题，是配套脚本没有跟上协议扩展。

- **问题 2**：SELF-GATE 审查文件命名冲突，本任务一度静默覆盖 TAG0015 已合并的历史审查记录
  （DEBT0011）。
  归因层面: 机制缺口
  说明：`SELF-GATE.md` 的派发模板明确规定了 `docs/reviews/agate-alignment-review-{date}.md`
  这个只含日期的命名格式，本次派发的 subagent 严格按协议执行、没有做错任何事——是协议模板本身
  没有考虑"同一天两个不同任务各自触发一次审查"这一在活跃仓库中并不罕见的场景。

- **问题 3**：`check-protocol-consistency.py --strict` 与 `gate_commands.P5` 的 `&&` 串联组合
  因本仓库长期存量 WARNING 债务而永久短路（DEBT0012），且此前从未被发现。
  归因层面: 机制缺口
  说明：脚本自身的 `--strict` 语义（WARNING-only 也返回非 0）是有意设计，问题出在这个语义与
  `&&` 链路组合后产生的复合效应从未被验证过——历史上多个任务的"验证方法"本身有共同盲区（管道
  `| tail` 掩盖真实 exit code），使得这个组合缺陷长期存在但无人发现，是协议对"gate 命令链路
  设计"缺少显式的组合语义校验。

- **问题 4**：CHECK 7（README badge vs 最新 git tag）与 P8 阶段"先改版本文件、后 tag"的必经
  时序之间存在结构性冲突，协议文档未明确说明。
  归因层面: 机制缺口
  说明：P8-release.md 列出"重跑 P5 gate"为主 Agent 必须亲自执行的验证项，但没有说明这一步在
  "版本文件已改、tag 未打"的中间状态下重跑必然会撞上 CHECK 7 的设计性 ERROR——协议对 P8 阶段
  gate 重跑与 tag 创建的先后顺序没有显式约定，容易让后续任务的执行者误判这是真实回归而困惑
  排查。

- **问题 5**（主 Agent 自身执行问题）：P1-P4 阶段多次用 worktree 相对路径调用
  `agate-inject-card.py`，实际读取的是 worktree 正在改动的协议卡片副本而非稳定基线。
  归因层面: 执行错误
  说明：HANDOFF-TAG0016.md 已经明确写出"gate 工具 ≠ 检查对象"这条纪律、且专门举了
  `check-protocol-consistency.py` 和 `agate-summary.py` 两个例子提醒容易搞混，但没有把
  `agate-inject-card.py` 也列进这个警示范围——主 Agent 在读到这条纪律时，没有主动推广到"所有
  编排/派发类工具脚本"这个更完整的心智模型，只套用在了 HANDOFF 举例过的那两个脚本上，属于对
  已有纪律的适用范围理解不完整，不是协议或 HANDOFF 本身缺失了这条规则。

## 四、改进措施

1. **修复 `_timeout_seconds` 解析缺口**（对应问题 1，DEBT0010）：`agate-read-gate-commands.py`
   / `agate-gate-missing-cmds.py` / `agate-gate-p5-count.py` / `agate-read-p5-commands.py`
   四处判据统一补充排除 `key.endswith("_timeout_seconds")`。**本任务未实施**（发现于 P2/P3/P5
   验证过程，非本任务 P0-brief 锁定范围），已登记 DEBT0010（priority: medium），供后续任务
   处理。
2. **SELF-GATE 审查文件命名补充任务标识**（对应问题 2，DEBT0011）：`SELF-GATE.md` 派发模板的
   成果文件/留痕文件路径补充 `{task_id}` 占位符（如
   `agate-alignment-review-{date}-{task_id}.md`）。**本任务未实施**（协议模板改动需走独立流程），
   已登记 DEBT0011（priority: medium）。
3. **`--strict` 与 `&&` 链路组合语义修复**（对应问题 3，DEBT0012）：二选一——gate_commands.P5
   declaration 改用分号分隔的独立命令而非 `&&` 串联；或 `check-protocol-consistency.py` 新增
   仅在存在 ERROR 时非 0 的更细粒度模式。**本任务未实施**，已登记 DEBT0012（priority: medium）。
4. **P8-release.md 补充 CHECK 7 时序说明**（对应问题 4，本次复盘新发现，非原任务范围）：在
   「主 Agent 必须亲自执行」节"重跑 P5 gate"一条附注"若 gate_commands.P5 含
   consistency 的 CHECK 7（badge vs tag）校验，应在 commit + tag 创建之后再重跑，而非 bump
   文件后立即重跑"。落点：`agate/phase-cards/P8-release.md`。**本任务未实施**（发现于本次
   复盘撰写，需走独立协议改动流程），已登记 **DEBT0013**（priority: low）。
5. **HANDOFF/AGENTS 类文档的"工具 vs 对象"纪律示例清单化**（对应问题 5，纪律提醒非协议改动）：
   本条不对应具体文件改动，是给未来 worktree 类协议自身改造任务的执行提醒——"gate 工具 ≠ 检查
   对象"这条纪律举例时若只列 1-2 个具体脚本名，容易被误解为"只有这几个脚本要注意"，而不是
   "凡是编排/派发/卡片注入类工具都要用稳定版"这个更完整的心智模型。建议未来 HANDOFF 模板在
   给出示例后补一句"以上仅为示例，判断标准是'脚本是否读取/操作协议文档内容'——是则用稳定版，
   检查对象是 worktree 自身内容的脚本才用 worktree 版"。不重复登记为独立 DEBT（本条通过复盘
   撰写本身已完成经验沉淀）。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | | |
| PAUSED | 否 | — | | |
| PROD_TOUCHED | 否（全程 `[PROD_NOT_TOUCHED]`） | — | | |
| SCOPE+ | 否 | — | | |
| SCOPE_RESOLVED | — | — | | |
| DESIGN_GAP | 是 | ✅ | | |
| DESIGN_GAP_REVIEWED | 是 | ✅ | | |
| NEED_CONFIRM | 否（P1 `[NO_NEED_CONFIRM]`） | — | | |
| CAPABILITY_GAP | 否 | — | | |
| gate 验证（每阶段） | 是 | ✅ | | |
| 阶段产出文件（每阶段） | 是 | ✅ | | |
| .state.yaml phase 同步 | 是 | ✅（P4 曾一度提前写 P4 阶段但产出未就绪，gate 拦截后回退重来） | | |
| 裁剪条件 + override | 否（全阶段未裁剪） | — | | |
| capability_requirements | 是 | ✅（声明 available，纯代码逻辑无外部依赖） | | |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | | |
| phase-产出一致性 | 是 | ✅（多次出现预期内 WARNING，产出阶段与暂存内容一致） | | |
| P6 evidence（含截图 + 引用 + vision YAML） | 是（无 UI，用文本证据代替截图） | ✅（18 个证据文件） | | |
| P2 候选方案 + 权衡（≥2） | 是 | ✅（整体路线 2 个候选，CHECK 12/审计 7 两个子决策各自 3 个候选） | | |
| P8 internal_only_reason | 否 | — | | |
| dispatch-context.md | 是 | ✅（每次派发/重试均独立撰写，累计 30+ 份） | | |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅ | | |
| CI backstop | 是 | ✅（PR #164 18/18 全绿） | | |
| **技术债登记** | 是 | ✅（DEBT0009/0010/0011/0012 均在发现的当次会话内当场登记；DEBT0013 在复盘撰写时新发现并当场登记，均未拖延补登） | | |

## agate 反馈

> `feedback_ready: true`，以下条目归因到 agate 机制/执行层面，供 `agate-feedback.py` 提取。

- **[机制缺口]** 4 个 gate_commands 键解析脚本均只排除 `_formatter` 后缀、未排除
  `_timeout_seconds` 后缀，是 TAG0012 引入 `timeout_seconds` 字段时未同步排查全部消费脚本
  导致的系统性盲区。已登记 DEBT0010（priority: medium），建议 agate 项目组统一修复四处判据。
- **[机制缺口]** SELF-GATE.md 的 protocol-alignment-review 派发模板给出的成果文件/留痕文件
  命名只含日期不含任务标识，在活跃仓库中同日多任务各自触发审查会静默覆盖彼此的历史记录（本次
  实测复现，TAG0015 的记录一度被覆盖）。已登记 DEBT0011（priority: medium）。
- **[机制缺口]** `check-protocol-consistency.py --strict` 的"WARNING-only 也非 0"语义与
  `gate_commands.P5` 的 `&&` 串联组合，在存量 WARNING 债务未清零的仓库里会永久短路——这个
  组合缺陷长期潜伏未被发现，根因是历史验证习惯用管道 `| tail` 核对 exit code（掩盖真实退出码）。
  已登记 DEBT0012（priority: medium）。
- **[机制缺口]** P8-release.md 未说明 CHECK 7（README badge vs 最新 tag）与"重跑 P5 gate"
  之间的时序依赖——bump 版本文件后、tag 创建前的中间状态重跑 consistency 检查必然触发该 ERROR，
  容易被误判为真实回归。已登记 DEBT0013（priority: low），建议在 P8 卡片补充时序说明。
- **[执行错误]** 主 Agent 在 P1-P4 阶段多次用 worktree 相对路径调用 `agate-inject-card.py`，
  实际读取了 worktree 正在被本任务修改的协议卡片副本而非稳定基线（HANDOFF 已提醒"工具 ≠
  对象"但示例未覆盖此脚本，主 Agent 未能主动推广适用范围）。P5 阶段发现并改正，此前未产生
  实质损害纯属侥幸（那几张卡片当时尚未被本任务改动）。建议 HANDOFF 类文档给出该纪律示例时
  补充"判断标准是脚本是否读取协议文档内容，不是仅举例的那几个脚本"这一更完整表述。
