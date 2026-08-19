---
task_id: TAG0015
mechanism_issues:
  - "test_check_pruning.py 三个用例依赖真实 git 暂存区（非隔离 fixture），协议自身改造任务大体量暂存时误报（DEBT0007）"
  - "P2 设计阶段缺少'新增涉及 frontmatter 读取的脚本需核对 ADR-007 单一双读工具适用性'的前置检查项，导致合规缺口留到 SELF-GATE 才发现"
  - "P1/P2 转译 roadmap.md 已有具体设计方案（如 L2 checkpoint 两件套）时，协议没有强制要求逐项对照原始方案，容易在转译过程中不知不觉丢内容"
  - "agate-feedback.py 的 ABS_PATH_RE 匿名化正则误伤中文散文里的斜杠分隔词，本复盘端到端 dogfooding 时当场发现（DEBT0008）"
execution_issues:
  - "P2 首版方案 A1 把 roadmap.md 原始'两件套'checkpoint 设计简化为单一文件，且用未经验证的等价性断言（'已被 progress.md+orchestrator-log 覆盖'）掩盖了这个收窄，属于影响面梳理没有做到'有客观证据支撑'这条已有要求"
feedback_ready: true
---

[PROD_NOT_TOUCHED]

# TAG0015 复盘 — agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）

> 本复盘基于本任务自己交付的新模板撰写（自举）。撰写者：orchestrator（编排 Agent），合并后在主
> checkout 撰写，路径遵循新约定 `tasks/{Txxx}/retrospective.md`（不再是 docs/reviews/）。

## 一、事实基线

- 任务周期：2026-08-16 立项（P0）→ 2026-08-19 完成合并（PR #162 merge commit `70e21ad`）
- 阶段：P0-P8 全部走完，无裁剪
- 版本：v0.52.0 → v0.53.0（minor）
- BDD：20 条，20/20 PASS，0 FAIL
- 重试记录（.state.yaml）：P1 1 次（requirements-review needs-revision，路径引用裸名订正）、
  P2 1 次（plan-eng-review 阻塞项 AP-1，L2 checkpoint 设计收窄）、P4 1 次（SELF-GATE 语义
  对齐审查发现 3 MISALIGNED + 1 NEEDS_HUMAN_REVIEW）；P3/P5/P6/P7/P8 均首轮通过
- 另有 3 次 requirements-review 子任务因平台 API 过载（529）在启动阶段失败，未产出任何文件，
  按 TAG0012 先例（同一角色原样重派非"调整重派"）不计入正式重试计数
- DESIGN_GAP：1 条（roadmap.md 路径字符串因 check-protocol-consistency.py CHECK 2 误判死链，
  拆分处理），P7 已配对 REVIEWED
- SCOPE+：0 条
- 改动文件：新增 1 个协议模板（retrospective-template.md）+ 1 个脚本
  （agate-feedback.py）+ 3 个测试文件；修改 6 个协议/脚本文件（check-retrospective.py /
  state-machine.md / AGENTS.md / task-files.md / P8-release.md / agate-md-field-get.py）+
  5 份存量复盘文档标注 + roadmap.md/README.md×2/CHANGELOG.md
- 全量测试：909 passed（改动前基线）→ 932 passed + 2 skipped（净增 23，0 回归）
- CI（PR #162）：18/18 全绿（pytest/shellcheck/consistency/gate-backstop/ruff/platform-scan，
  ubuntu + windows 双平台）

## 二、做得好的 + 可复用模式

- **P6 verifier"不复用 P5 结论、独立构造场景实跑取证"**——沿用 TAG0012 先例，本次对脚本类 BDD
  （check-retrospective.py/agate-feedback.py）都手工搭建独立 fixture 实跑验证，而非转抄
  pytest 断言。去向：**回馈 agate**（已是既有协议模式，本次是成功复用的再验证，不需要新动作，
  记录在案供后续任务参照）
- **P2 评审对"候选方案是否真的分析了取舍"做了深挖式核查**（plan-eng-review 发现 A1 方案用
  未经验证的等价性断言掩盖了对 roadmap 原始设计的收窄）——这是评审角色真正发挥"偏执 Staff
  Engineer"作用的例子，不是走过场。去向：**回馈 agate**（已是既有角色定义要求，记录为正面
  案例，不需要新动作）
- **SELF-GATE 语义对齐审查在合并前真的拦住了一个实质缺口**（ADR-007 合规）——如果没有这道检查，
  `agate-feedback.py` 会带着"绕开单一双读工具"的架构违规进入 main。去向：**回馈 agate**（证明
  SELF-GATE 机制本身值得继续强制执行，不需要新动作）
- **对 test_check_pruning.py 三次间歇性失败做了完整根因排查而非绕过**（isolated run / 组合
  子集 run / git stash A-B 对比 / 无并发进程下干净单跑，最终定位到
  `_staged_source_count` 读真实暂存区），没有因为"看起来像 flaky"就跳过或强行改动测试文件让它
  变绿。去向：**回馈 agate**（已登记 DEBT0007，见「四、改进措施」）

**本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？**——本任务未产生项目特定
的临时命令/脚本（agate 自身即协议项目，本任务的"项目资产"与"agate 机制"是同一件事，不存在
"项目侧 vs agate 侧"的区分），故不适用「项目资产沉淀」这一去向，两条可复用项均归入「回馈
agate」。

## 三、发现的问题

- **问题 1**：P2 首版方案 A1 把 roadmap.md RM-AG0020 详情节明确并列的"两件套"L2 checkpoint
  设计（`P{n}-checkpoint.md` 每阶段 + `task-session-summary.md` 任务级）简化为"只在 P8 落盘
  一次"，且用"已被 P{n}-progress.md + orchestrator-log.md 覆盖"这个未经逐项内容比对的断言
  为收窄辩护。
  归因层面: 执行错误
  说明：P2 卡片「影响面梳理（强制节）」已明确要求"梳理动作要有客观证据……不是凭印象列"，
  architect 在写这条等价性断言时没有真的逐项核对 progress.md/orchestrator-log.md 的内容颗粒度
  是否真的覆盖了 checkpoint 想保留的信息——属于"该核对但没核对"，不是协议没要求核对。评审
  （plan-eng-review）事后发现并要求修订，未流入 main。

- **问题 2**：`agate-feedback.py` 首版实现本地重新实现了 frontmatter 字段读取逻辑，未复用
  ADR-007 规定的"单一双读工具" `agate-md-field-get.py`，直到 P4 阶段的 SELF-GATE 语义对齐
  审查才发现（A7 项）。
  归因层面: 机制缺口
  说明：P2-design.md 卡片当前没有"新增涉及 frontmatter/机器字段读取的脚本时，须核对 ADR-007
  适用性"这一检查项——architect 在设计 `agate-feedback.py` 时没有主动想到要对照 ADR
  清单，这不是"没有认真做"的执行问题，而是协议本身在 P2 阶段缺少这个提醒点（P8 releaser 的
  Lessons Learned 也独立得出同样结论："ADR-007 合规性检查应前移到 P2/P4 阶段，而非留给 P7/P8
  补救"）。

- **问题 3**：`test_check_pruning.py` 三个用例在本任务 P4/P5/P6/P8 阶段多次跑全量 pytest 时
  间歇性失败（929 passed + 3 failed vs 932 passed + 0 failed 交替出现），一度被误判为可能的
  真实回归或资源竞争假阳性，排查耗费了数轮独立验证。
  归因层面: 机制缺口
  说明：这三个用例的判定逻辑（`check-pruning.py:56 _staged_source_count`）依赖运行 pytest
  时**外层真实仓库**的 `git diff --cached` 状态，而非隔离在测试自己的 tmp_path fixture 内——
  测试设计本身没有做环境隔离，不是本任务的执行问题，是该测试用例的既有设计缺口（已登记
  DEBT0007）。

- **问题 4**（技术债登记核对，见下方核对清单"技术债登记"行）：问题 3 的机制缺口在 P4/P5 阶段
  被发现并在 orchestrator-log/commit message 里详细记录了根因，但**当时没有立即登记进
  tech-debt.md**，只是判断"非本任务范围"就搁置了。
  归因层面: 执行错误
  说明：复盘模板本身（本任务的产出）明确要求"技术债登记"行标"是"时必须填写具体 DEBT 编号，
  不允许留空或写"待定"——本复盘撰写时已补登记为 DEBT0007，闭环该项，但过程中确实有一段时间
  "发现了但没登记"的执行空档，值得下次任务发现类似机制缺口时，当场登记而不是留到复盘时才补。

- **问题 5**（撰写本复盘时端到端 dogfooding 发现，非原任务范围内已知问题）：本复盘定稿后实跑
  `AGATE_FEEDBACK=on python3 agate/scripts/agate-feedback.py .../retrospective.md` 做机制
  闭环验证，发现 `ABS_PATH_RE` 会把中文散文里"机制/执行层面"这类用 `/` 分隔的正常文本误判为
  绝对路径并替换为 `<PATH>`，产出内容出现语义破损。
  归因层面: 机制缺口
  说明：`test_agate_feedback.py` 的 BDD-18 用例只覆盖了"真实绝对路径应被处理"的正向场景，没有
  覆盖"中文散文含 `/` 但不是路径"这类负向场景——是测试覆盖盲区，不是脚本作者的执行疏漏（P2
  候选方案 B1 的设计文本本身没有讨论这种边界情况）。已登记 DEBT0008，priority: low（不影响
  BDD-18 核心诉求，只是产出内容有可读性瑕疵）。

## 四、改进措施

1. **P2-design.md 卡片新增 ADR 合规检查提示**（对应问题 2）：在「产出规格」或「影响面梳理」节
   补一句——"新增/大改涉及 frontmatter/机器字段读取的脚本时，须核对 `agate/adr.md` 是否有
   适用的既有 ADR（如 ADR-007 单一双读工具），不符合需在候选方案权衡中说明理由"。落点：
   `agate/phase-cards/P2-design.md`。**本条不在本任务范围内实施**（本任务已完成 P0-brief 锁定
   的范围，新增协议改动需走独立任务流程），记录为后续任务的输入，登记进 roadmap backlog。
2. **`test_check_pruning.py` 隔离缺口修复**（对应问题 3）：已登记 DEBT0007（`priority: medium`，
   `status: open`），建议方向是把三个用例改为在隔离临时 git 仓库内运行或 monkeypatch
   `run_git`/`_staged_source_count`。落点：`agate/tests/unit/test_check_pruning.py` +
   `agate/scripts/check-pruning.py`（若需要为可测性重构）。
3. **发现机制缺口时当场登记，不留到复盘补登**（对应问题 4，纪律提醒非协议改动）：本条不对应
   具体文件改动，是给未来任务的执行提醒——写入本复盘作为"经验教训"留痕，不重复登记为独立 DEBT
   （问题本身已通过"本复盘完成登记"的动作闭环）。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | | |
| PAUSED | 否 | — | | |
| PROD_TOUCHED | 否 | — | | |
| SCOPE+ | 否 | — | | |
| SCOPE_RESOLVED | — | — | | |
| DESIGN_GAP | 是 | ✅ | | |
| DESIGN_GAP_REVIEWED | 是 | ✅ | | |
| NEED_CONFIRM | 否 | — | | |
| CAPABILITY_GAP | 否 | — | | |
| gate 验证（每阶段） | 是 | ✅ | | |
| 阶段产出文件（每阶段） | 是 | ✅ | | |
| .state.yaml phase 同步 | 是 | ✅ | | |
| 裁剪条件 + override | 否（全阶段未裁剪） | — | | |
| capability_requirements | 是 | ✅（声明 available） | | |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | | |
| phase-产出一致性 | 是 | ✅（P3 出现一次预期内 WARNING，测试代码本就是 P3 产出，非问题） | | |
| P6 evidence（含截图 + 引用 + vision YAML） | 是（无 UI，用文本证据代替截图） | ✅（21 个证据文件） | | |
| P2 候选方案 + 权衡（≥2） | 是 | ✅（2 个候选方案） | | |
| P8 internal_only_reason | 否 | — | | |
| dispatch-context.md | 是 | ✅ | | |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅ | | |
| CI backstop | 是 | ✅（PR #162 18/18 全绿） | | |
| **技术债登记** | 是 | ✅（本复盘补登记 DEBT0007） | 发现问题 3 到正式登记之间有约 1 天执行空档（P4 发现→P8 收尾未登记→复盘时补登） | 执行错误（问题 4） |

## agate 反馈

> `feedback_ready: true`，以下条目归因到 agate 机制/执行层面，供 `agate-feedback.py` 提取。

- **[机制缺口]** P2-design.md 卡片缺少"新增涉及 frontmatter 读取的脚本需核对 ADR-007 单一
  双读工具适用性"的前置检查项，导致合规缺口留到 P4 SELF-GATE 才被发现，造成一轮返工。建议：
  P2 卡片补充该检查项。
- **[机制缺口]** `test_check_pruning.py` 的 `_staged_source_count` 相关三个用例依赖运行
  pytest 时外层真实仓库的 git 暂存区状态，不是隔离测试，在协议自身改造类任务（大体量暂存）下
  会间歇性误报。已本地登记 DEBT0007，供 agate 项目组参考决定是否收进协议本体维护清单。
- **[机制缺口]** P1/P2 转译 P0-brief/roadmap.md 已有的具体设计方案时，协议没有强制要求逐项
  对照原始方案内容，本次曾因此在 P2 首版设计中意外收窄了 roadmap 原始的"两件套"checkpoint
  设计（后被 plan-eng-review 发现并纠正，未流入 main）。建议：评估是否需要在 P1/P2 卡片补充
  "若 P0-brief/roadmap 已有具体方案，需逐项核对转译完整性"的检查项，或判断现有"同类扫描/
  影响面梳理"机制已经足够、本次只是执行疏漏（两种结论都需要人工裁决，不由本条单方面定论）。
- **[机制缺口]** `agate-feedback.py`（本任务自身产出）的匿名化正则 `ABS_PATH_RE` 会误伤中文
  散文里的斜杠分隔词（如"机制/执行层面"→"机制`<PATH>`执行层面"），本条反馈本身就是用
  该脚本提取时当场发现的实例——已登记 DEBT0008（priority: low）。有趣的元观察：这条反馈内容
  经过脚本处理后，"P1/P2"这类引用也会被误伤，说明 BDD-18 的测试覆盖需要补负向场景。
