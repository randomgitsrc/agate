---
phase: P8
task_id: TAG0012-protocol-mechanism-fixes
type: release
parent: P7-consistency.md
trace_id: TAG0012-P8-20260818
status: draft
created: 2026-08-18
agent: implementer
---

[PROD_NOT_TOUCHED]

# P8 发布记录 — agate 协议机制增强批（TAG0012-protocol-mechanism-fixes）

> releaser（implementer P8 模式）产出。本文件只核对与声明，**不执行 git commit / git tag / 版本文件改动**——bump 动作由主 Agent 在 gate 验证后统一执行。组织方式参照 `agate-workspace/tasks/TAG0014-dispatch-orchestration/P8-release.md`（同类协议机制任务的已完成 P8 记录）。

## 版本决策

- `bump_type: minor`
- `debt_check: none`
- 版本号变更：**v0.48.0 → v0.49.0 已是历史**——本任务当前基线是 **v0.51.0 → v0.52.0**（`README.md` L5 version badge 实测 `v0.51.0`，`git describe --tags --abbrev=0` 同为 `v0.51.0`，二者一致，无待还原的中间态漂移）

### 独立核实结论（未直接采信 dispatch-context §约束1 结论，逐条复核）

对照 P4-implementation.md「决策标注」第 3 节（`[DESIGN_GAP]`/`[SCOPE+]`/`[SCOPE_GAP]`/`[CLARIFY]` 均 0 条）与 P2-design.md §2.2「不改什么」表逐条复核，本任务本质是新增机制/字段：

1. **`timeout_seconds` 字段**：P2-design.md §1 候选 B「向后兼容」条款——缺字段行为等同现状（沿用 `dispatch_plan` 先例）；`check-gate.py` 明确不改（P2 §3.7 决定），P5/P6 无脚本消费方施加真实拦截，纯声明性字段。**不破坏任何既有任务**。
2. **verification_env 失败处理协议 / 环境准备职责边界**：新增协议文档小节（可/不可重试清单、止损轮次=2、READY 后归属判据），不修改 `.state.yaml` schema（P2 §2.2 明确不新增字段），止损轮次由主 Agent 人工记录，无脚本强制拦截逻辑变化。
3. **P0-brief 漂移判据（RM-AG0019）**：新增文档判断树 + `[P0_STALE:]` 标记规则，`check-gate.py` 当前无 `_gate_p0` 函数（P1 §0 第 6 点已核实），本任务未新增脚本硬校验，仍是人工 checklist 增补一项。
4. **同类扫描/影响面梳理（RM-AG0013）**：P0/P1/P2 三张卡新增强制节，是**流程要求**（"缺失 → requirements-review 打回"这类人工评审判据），不对应 `check-gate.py` 任何 exit code 变化。
5. **命令超时兜底/资源密集型默认串行（RM-AG0016）**：`dispatch-protocol.md`/`dispatch-prompt.md` 新增运行时纪律段落，属 subagent 执行纪律的文字规则，非脚本强制。

`git show 27509a2 --stat` 确认全部 12 个改动文件均在 `agate/` 协议文档/角色文件/模板目录下，`check-gate.py`/`agate_common.py`/`agate-frontmatter-check.py`/`.state.yaml` schema 零改动（P2 §2.2 明确列出且核实一致）——**无任何破坏性变更**，新增内容均为可选字段或纯流程性文档要求。

**判定：minor（v0.51.0 → v0.52.0）**。不是 patch（本任务新增了三类实质性协议机制，非纯 bug 修复）；不是 major（无任何现有字段语义被改变、无 gate 脚本行为变化会拦截老任务）。

## packages 声明与实际改动的对照说明（如实核对，回应 P7 观察点②）

P2-design.md frontmatter 声明 `packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]`（agate 自身无独立多包，这是逻辑分组，单版本号发布）。

**独立核实**（`git show 27509a2 --stat --name-only | grep 'agate/scripts/'` → 零命中）：实际改动的 12 个文件中**没有一个在 `agate/scripts/` 目录下**：

| packages 逻辑分组 | 实际改动文件 |
|---|---|
| phase-cards | P0-orchestrator.md / P1-requirements.md / P2-design.md / P5-verification.md / P6-acceptance.md |
| dispatch-protocol | dispatch-protocol.md |
| state-machine | state-machine.md |
| execution-roles | analyst.md / architect.md / verifier.md |
| templates | dispatch-prompt.md / task-files.md |
| **scripts** | **无对应文件改动** |

唯一新增的"代码"文件是 `agate/tests/unit/test_protocol_mechanism_anchors.py`，路径属 `agate/tests/`，不属于 `agate/scripts/`，且 packages 声明中未列出 `tests` 这一类别。

**结论**：这是 P2 frontmatter 逻辑分组措辞与实际改动范围的差异，**不是一致性问题**（P7-consistency.md §3.2 已判定不阻塞，仅标注"待 P8 核对"）。CHANGELOG 措辞据此调整为直接按"文件类型"描述实际改动（协议文档 + 阶段卡片 + 角色文件 + 模板 + 新增 1 个测试文件），不虚报"改了 `agate/scripts/`"。

## 版本文件核对结论

| 文件 | 当前状态 | 核对结论 |
|------|---------|---------|
| `README.md` **L5** version badge | `[![version](https://img.shields.io/badge/version-v0.51.0-blue)](https://github.com/randomgitsrc/agate)` | 待主 Agent 在 P8 gate 后 bump 至 `v0.52.0`，与 tag 同 commit |
| `CHANGELOG.md` | 最新章节 `## [0.51.0] - 2026-08-18`（L11，TAG0006），三段式格式（新增/变更/测试） | 待主 Agent 新增 `## [0.52.0] - 2026-08-18` 章节（内容见下节，本 releaser 只声明不写入） |
| git tag | `v0.51.0`（`git describe --tags --abbrev=0` 实测） | 发布时创建 `v0.52.0`（主 Agent 执行，与 badge bump 同一 commit） |
| `agate/UPGRADING.md` | 未检查是否需要新增本版本章节 | 本任务**无破坏性变更**（见上节独立核实），主 Agent 可判断是否需要新增章节说明"新增可选字段/新增流程要求，无需迁移动作" |

## CHANGELOG [0.52.0] 内容建议（供主 Agent 写入，本 releaser 不直接编辑 CHANGELOG.md）

基于 P4-implementation.md 改动清单 + P1-requirements.md 5 条 RM 编号（RM-AG0013 / RM-AG0014 主体 / RM-AG0014 补充 / RM-AG0019 / RM-AG0016），只描述本任务真实做了什么：

```markdown
## [0.52.0] - 2026-08-18

### 新增（TAG0012：agate 协议机制增强批）

- **verification_env 失败处理协议（RM-AG0014 主体，`dispatch-protocol.md`）**：新增可重试/不可重试判据表（含"机制误用型问题应立即改正声明方式"）、批处理要求（单轮 ≥2 待验假设须一次性列出批量验完）、止损轮次=2（与阶段 `retries[Pn]` 独立计数，不新增 `.state.yaml` 字段，超限转 PAUSED）、READY 后问题归属三判据（本任务遗留/环境本身问题/证据不足默认按前者）
- **环境准备职责边界（RM-AG0014 补充，`dispatch-protocol.md` + `P5-verification.md` + `P6-acceptance.md` + `verifier.md`）**：环境启动/维护/关停默认归主 Agent，subagent 默认只消费不自启；多个并行 subagent 共享环境由主 Agent 统一注入访问方式；`P5-verification.md`/`P6-acceptance.md`/`verifier.md` 改为引用式落地，不重复展开
- **`{key}_timeout_seconds` 字段（RM-AG0016，`P2-design.md` 卡 + `architect.md` + `task-files.md`）**：per-key 声明式超时基准字段（三档建议默认：单元测试 120s / E2E 300s / 构建类 600s，手动声明非自动推断），明确排除 P3（P3 继续走既有 `AGATE_TDD_TIMEOUT` env var 机制），缺字段行为等同现状（向后兼容，`check-gate.py` 不新增校验）
- **命令超时兜底 + 资源密集型默认串行（RM-AG0016，`dispatch-protocol.md` + `dispatch-prompt.md` 双源同步）**：subagent 执行任意 bash 命令前须设 shell 层超时（预期耗时 ×1.5，有 `_timeout_seconds` 声明则直接取值），超时/非预期失败固定三动作（停止执行/写 progress 记卡点/返回主 Agent，不自行换命令）；「派发编排机制」并行规则新增第 4 条"资源密集型默认串行"（全量 xdist 测试/CDP-Playwright E2E/构建打包默认不并行）
- **P0-brief 漂移判据（RM-AG0019，`P0-orchestrator.md` + `P1-requirements.md` 卡 + `state-machine.md`）**：严重漂移 3 条判据（任务目标方案不成立/`executor_env` 平台前提不成立/`known_risks` 已解决前提失效或已被他任务解决）+ 轻微漂移 2 条判据（局部细节变化/`env_constraints` 值刷新），命中严重 → 回 P0 重新立项；命中轻微 → 更新字段 + 标 `[P0_STALE: 漂移点]` 后继续
- **同类扫描/影响面梳理（RM-AG0013，`P0-orchestrator.md` + `P1-requirements.md` 卡 + `P2-design.md` 卡 + `analyst.md` + `architect.md`）**：P0"同类/影响面预判"节、P1"同类扫描（强制节）"、P2"影响面梳理（强制节）"三级递进；`analyst.md` 隐含需求清单新增"同类/影响面"维度 + "缺的是能力还是环境？"判断树；`architect.md` 批次设计前置检查项引用 P2 强制节

### 测试

- 新增 `agate/tests/unit/test_protocol_mechanism_anchors.py`：28 条 parametrize 用例，逐条 grep 断言审计上述新增机制的关键词锚点已落盘（覆盖 BDD-1~22 + BDD-15b，共 23 条 BDD）
- 全量 `pytest agate/tests/ -q --tb=no` → 909 passed + 2 skipped，无回归；`count-tests.sh` → 911（≥749 单调不减）；`check-protocol-consistency.py --strict` → 0 ERROR（与改动前基线逐行 diff 比对，WARNING 集合完全一致，未新增）；`shellcheck -S warning agate/scripts/*.sh` → 0 issue
- **本版本无破坏性变更**：`timeout_seconds` 为纯声明性可选字段（`check-gate.py` 未新增校验，无运行时消费方）；新增文档强制节/checklist 项为人工评审流程要求，不对应任何 gate 脚本 exit code 变化；`.state.yaml` schema 无新增字段；`agate/scripts/` 目录零改动（仅新增 1 个测试文件于 `agate/tests/`）
```

## 发布检查命令清单（P2-design.md `gate_commands`，供主 Agent 在 gate 验证阶段重跑，本 releaser 不重跑）

| key | 命令 | P5 阶段已跑结果（P4/P7 记录，仅供参照，非本次结果） |
|---|---|---|
| P3 | `python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v` | 28 passed |
| P5 | `python3 -m pytest agate/tests/ -q --tb=no` | 909 passed, 2 skipped |
| P5_consistency | `python3 agate/scripts/check-protocol-consistency.py --strict` | 0 ERROR |
| P5_count | `bash agate/tests/scripts/count-tests.sh` | 911（≥749 达标） |
| P5_shellcheck | `shellcheck -S warning agate/scripts/*.sh` | 0 issue（RM-AG0016 判断不改 .sh，仅回归确认） |

主 Agent 需在 bump 后重跑上表全部命令确认仍全绿，并额外执行：`git log v0.51.0..HEAD --oneline` 对照 CHANGELOG 无遗漏；从 P2 packages 验证 version 文件路径（`README.md` L5）。

## debt_check

- `debt_check: none`
- 已读 `agate-workspace/debt/tech-debt.md`：现存 6 条 DEBT（DEBT0001/DEBT0005/DEBT0006 `status: closed`；DEBT0002/DEBT0003/DEBT0004 `status: open`）。
- **独立核实**：6 条 DEBT 的 `task_id` 全部为 `TAG0008-version-management`（DEBT0002/0003/0004）、`TAG0013-script-consistency`（DEBT0001）、`TAG0006-ui-ux-quality`（DEBT0005/0006），逐条 evidence 内容核对均与版本管理/离线安装/P6 双证据解析相关，**无一条与本任务（TAG0012 协议机制增强批：verification_env/timeout_seconds/P0-brief 漂移判据/同类扫描）相关**。
- SELF-GATE alignment-review A7 项讨论过的"止损轮次不入 `.state.yaml`"取舍：主 Agent 已裁决"暂不追加新 ADR、不登记为债务"（P2-design.md §2.3 风险表已记录为设计取舍非债务，`docs/reviews/agate-alignment-review-TAG0012.md` A7 `[HUMAN_CONFIRMED]`，P7-consistency.md §6 已核实口径一致）——因此该项未在 tech-debt.md 登记，与预期一致，**不构成本次遗漏**。
- **结论：无本任务相关开放债务项，不阻塞发布。**

## 临时资源清单

本任务全程为纯协议文档 + 测试文件改动（P0-brief 定性为"协议文档 + 少量脚本 schema 字段"批次），**无临时服务/进程/数据库/端口占用/开发安装**：

- 无 debug server / 临时 daemon 启动
- 无临时数据库 / 测试数据目录创建
- 无端口占用
- 无 editable install / 全局包安装
- 任务目录内产出（`P0-brief.md` ~ `P7-consistency.md` + `P6-evidence/`24 个证据文件 + `P8-progress.md`/`P8-release.md` 本文件）均随 git 管理，非临时资源，无需清理

> 主 Agent READY 收尾检查：仅需确认 `git status` 工作区干净后创建 tag `v0.52.0`，无额外环境清理动作。

## Lessons Learned

1. **P2 packages 逻辑分组措辞需与实际改动范围留出核对空间（P7→P8 交接模式）**：agate 自身单版本号发布场景下，`packages:` frontmatter 是设计阶段的逻辑分组声明，不是精确的文件路径清单；本任务 `scripts` 类别声明后实际零改动（唯一新代码落在 `agate/tests/` 而非 `agate/scripts/`），P7 未强判 BLOCKER 而是留待 P8 核对，P8 应对差异做"如实说明"而非"凑数虚报"——这一"设计阶段可以用粗粒度分组、发布阶段做精细核对"的分工值得在同类协议机制任务里延续。
2. **纯声明性字段（无运行时消费方）的版本判定不应默认从紧**：`timeout_seconds` 字段本身不触发任何 `check-gate.py` exit code 变化（P2 §3.7 已论证"文档约定优先"分支），但它仍然是"新增机制"而非"零变更"——本次判定 minor（而非 patch）是因为语义上新增了三类实质性协议机制（失败处理协议/漂移判据/超时字段+运行时纪律），即便落地形式是纯文档也不代表可以按 patch 处理；bump_type 判定应看"新增了什么面向使用者的能力"而非仅看"是否触发脚本行为变化"。
3. **CHANGELOG 内容不能照抄同类历史任务模板**：dispatch-context 明确警告"不要照抄 TAG0014 的 CHANGELOG 段落"，本次撰写建议内容时逐条回查 P4-implementation.md §1 改动清单原文重新组织表述（而非套用 TAG0014 P8-release.md 的段落结构直接改几个名词），确保每条 CHANGELOG 条目都能追溯到本任务实际改动的具体文件和 BDD 编号。

## 交接给主 Agent

- [ ] 重跑 P5 gate 全部 5 条命令（exit 0 + failed==0 + 0 ERROR + 0 issue）确认 bump 后仍全绿
- [ ] `git log v0.51.0..HEAD --oneline` 对照 CHANGELOG 无遗漏
- [ ] `README.md` L5 badge `v0.51.0 → v0.52.0` + `CHANGELOG.md` 新增 `## [0.52.0]` 章节（内容参照上方建议） → 同一 commit
- [ ] 创建 tag `v0.52.0`（与 bump commit 同点）
- [ ] 按临时资源清单执行 READY 收尾检查（本任务清单为空，仅确认工作区干净）
- [ ] 干净 checkout（或 CI 兜底）跑 `check-protocol-consistency.py` 确认 0 ERROR（P8 卡 READY 收尾「协议一致性」要求，本地 worktree 结果不能替代）
- [ ] 确认 `agate-workspace/tasks/` 任务产出目录不被一致性检查器误扫（dogfooding 任务，应已在 `NARRATIVE_DIRS` 白名单，主 Agent 核实一次）
