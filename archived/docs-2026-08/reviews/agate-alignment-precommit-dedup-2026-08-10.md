---
review_date: 2026-08-10
reviewer: protocol-alignment-review
change_summary: 将 WORKFLOW.md「Pre-commit 检查总览」定为唯一权威表格，删除 dispatch-protocol.md 与 state-machine.md 中各自维护的重复表格，改为指向 WORKFLOW.md 的一句话；反向传播表新增一行记录该收敛规则
files_changed: [agate/WORKFLOW.md, agate/dispatch-protocol.md, agate/state-machine.md, agate/assets/review-roles/protocol-alignment-review.md]
---

# 协议-脚本对齐审查：pre-commit 检查清单去重

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**总体结论：未发现 MISALIGNED。发现 2 处轻微信息精度损失（非实质性信息丢失，详见"核心问题"节），建议顺手修复但不阻塞本次改动。**

---

## 核心问题：有没有信息丢失？（逐条比对过程）

比对方法：`git diff -- agate/dispatch-protocol.md agate/state-machine.md agate/WORKFLOW.md`（109 行，全文读取），把两份被删表格 + 表格前后说明段落拆成信息点清单，逐条在 WORKFLOW.md 新版「Pre-commit 检查总览」（`agate/WORKFLOW.md:234-265`）中找对应表述。

### dispatch-protocol.md 被删表格（原 823-850 行区间，10 行 + 6 段说明）逐条核对

| 被删信息点 | WORKFLOW.md 对应位置 | 结论 |
|---|---|---|
| check-state-yaml.sh / 格式合法性 | WORKFLOW.md:240（行 0） | 覆盖 |
| `[PROD_TOUCHED]` 三步检测 | WORKFLOW.md:242（行 1.2，本次新增） | 覆盖 |
| check-state-transition.sh / 状态转移+重试上限 | WORKFLOW.md:246（行 2.3） | 覆盖 |
| check-gate.sh / 各阶段门控 | WORKFLOW.md:241（行 1） | 覆盖 |
| check-p6-provenance.sh / 六道审计（含 P2.57 evidence JSON） | WORKFLOW.md:245（行 2.1，逐项枚举更细） | 覆盖，超集 |
| check-pruning.sh / 裁剪+override 校验 | WORKFLOW.md:247（行 2.7） | 覆盖但**行内枚举细节（design_trivial/follows_existing_pattern/no_behavior_change）未随行携带**——见下方说明 |
| check-scope-resolved.sh / [SCOPE+]追踪 | WORKFLOW.md:248（行 2.11） | 覆盖 |
| check-retrospective.sh / 异常模式提醒 | WORKFLOW.md:249（行 2.12） | 覆盖 |
| check-changelog.sh / [Unreleased]含task_id | WORKFLOW.md:243（行 1.6） | 覆盖 |
| check-p6-evidence.sh / 证据目录+BDD行数 | WORKFLOW.md:244（行 1.7，含 md5/方差细节，超集） | 覆盖 |
| 多任务适配段落 | WORKFLOW.md:258 | 逐字覆盖 |
| phase-产出一致性 WARNING | WORKFLOW.md:261 | 逐字覆盖（且补充了「状态标记绑定规则」的指向） |
| dispatch-context 缺失 WARNING | WORKFLOW.md:262 | 逐字覆盖 |
| 非实现阶段代码暂存 WARNING | WORKFLOW.md:263 | 逐字覆盖 |
| Pre-push hook 阈值提示段落 | WORKFLOW.md:265 | 逐字覆盖 |
| CI backstop（P1.3）段落，含 `check-p6-provenance.sh` + `P6-acceptance.md 单 author WARNING` | WORKFLOW.md:255（此段落**未被本次 diff 触碰**，是既有内容） | 覆盖大部分；**"P6-acceptance.md" 这一具体文件名未出现在 WORKFLOW.md 该段落**——见下方说明 |

**关于 check-pruning.sh 行的裁剪细节**：dispatch-protocol.md 旧表该行写「裁剪条件 + override 校验（P2/P6 不可裁；design_trivial / follows_existing_pattern / no_behavior_change 可简化但不可省略）」，WORKFLOW.md 新表 2.7 行只写「裁剪条件与实际执行一致性 + override 校验（P2.7-P2.9）」，未把括号里的枚举带过来。核实这不是本次改动造成的净损失：
- WORKFLOW.md 自身第 147-148、157 行（裁剪规则一节）已独立、更详细地记录了 `design_trivial`/`follows_existing_pattern`/`no_behavior_change` 三个例外条件的适用范围；
- state-machine.md 第 169、173 行也各自独立记录了同样内容；
- 且该表格行在 WORKFLOW.md 中的这一措辞（「裁剪条件与实际执行一致性」）**在本次 diff 之前就已经是这个样子**（该行不在本次 diff 的改动范围内），即 WORKFLOW.md 表格本来就比 dispatch-protocol.md 旧表简略，这是本次改动之前已存在的表述差异，不属于这次去重引入的新丢失。
判定：不算 MISALIGNED。

**关于 CI backstop 段落的 "P6-acceptance.md" 具名缺失**：dispatch-protocol.md 被删段落明确写「provenance 审计重跑 + `P6-acceptance.md` 单 author WARNING 作为兜底审计」，点名了 git blame 检测的目标文件是 `P6-acceptance.md`。WORKFLOW.md 现存的对应段落（`agate/WORKFLOW.md:255`，本次 diff 未触碰、属于既有内容）只写「provenance 审计重跑（check-p6-provenance.sh）+ git blame 单 author WARNING 作为兜底审计」，未点名具体文件。经查 `agate/scripts/ci-gate-backstop.py:166-182`，该 git blame 检测的目标确实硬编码为 `P6-acceptance.md`（`p6_file = Path(task_dir) / "P6-acceptance.md"`），并非任意文件。
- 在去重之前，读者若看 dispatch-protocol.md 能看到这个具体文件名；去重之后，三份文档里唯一保留、且被 state-machine.md/dispatch-protocol.md 共同指向的 WORKFLOW.md 版本恰好是三者中最不精确的那版（只有泛化的"git blame"，没具体文件名）。这是**去重合并时选错了"信息量最大版本"作为权威版**导致的精度损失，虽然轻微（可从脚本源码查到），但违背了本次改动"确保 WORKFLOW.md 是真正的信息超集"的目标。
判定：不构成需要回退的 MISALIGNED（不阻断 commit），但记为**建议修复项**：建议给 WORKFLOW.md:255 该句补上"（`P6-acceptance.md`）"。

### state-machine.md 被删表格（原 214-238 行区间，9 行 + 2 段说明）逐条核对

| 被删信息点 | WORKFLOW.md 对应位置 | 结论 |
|---|---|---|
| P1.1 gate / exit 1 拦截 | WORKFLOW.md:241 | 覆盖 |
| P1.6 CHANGELOG / P8 phase 警告不拦截 | WORKFLOW.md:243 | 覆盖 |
| P1.7 P6证据 / 拦截+md5+方差WARNING | WORKFLOW.md:244 | 覆盖，超集 |
| P2.1/P2.10 provenance / 六道审计 exit1/exit2 | WORKFLOW.md:245 | 覆盖，超集 |
| P2.3-P2.5 状态转移 / exit1拦截 | WORKFLOW.md:246 | 覆盖 |
| P2.7-P2.9 裁剪 / exit1拦截 | WORKFLOW.md:247 | 覆盖（同上，枚举细节见前述说明，非本次引入损失） |
| P2.11 SCOPE_RESOLVED / exit1拦截 | WORKFLOW.md:248 | 覆盖 |
| P2.12 复盘提醒 / exit0不拦截 | WORKFLOW.md:249 | 覆盖，超集（补充了"重试超限/SCOPE+/override"触发条件） |
| P2.15 格式校验 / exit1拦截 | WORKFLOW.md:240（行 0） | 覆盖 |
| 多任务 hook 扫描段落，含具名脚本 `pre-commit-gate.sh` | WORKFLOW.md:258 | 覆盖核心逻辑；**"pre-commit-gate.sh" 这一具体脚本名未随句带过去**——见下方说明 |
| CI 兜底（P1.3）段落 | WORKFLOW.md:255 | 覆盖 |

**关于 "pre-commit-gate.sh" 脚本名缺失**：state-machine.md 旧段落明确写「**pre-commit-gate.sh** 扫描暂存区中所有变更的 `.state.yaml`」，WORKFLOW.md 合并后的段落（`agate/WORKFLOW.md:258`）只写「hook 扫描暂存区中所有变更的 `.state.yaml`」，未点名脚本文件名。经查 `agate/scripts/README.md:3,13` 仍明确记录 `pre-commit-gate.sh` 是 hook 入口、按顺序调度 9 项检查，因此该脚本名信息在整个 agate/ 文档体系里并未真正消失，只是没有在这一句里重复。
判定：不构成信息丢失，属于去重的合理精简（scripts/README.md 已经是记录脚本清单的权威位置）。

### 悬空引用检查

`grep -rn "dispatch-protocol.md#\|state-machine.md#\|Pre-commit 检查全景" agate/ --include="*.md"` 未发现任何文件（角色文件/phase-cards/模板）以锚点链接或原文摘引方式引用被删表格的具体行内容。dispatch-protocol.md 和 state-machine.md 现在的一句话（分别在 `dispatch-protocol.md:823` 和 `state-machine.md:216`）都正确指向 `WORKFLOW.md`「Pre-commit 检查总览」，措辞与该小节标题（`WORKFLOW.md:234`）完全一致，无悬空。

---

## 逐项审查

### A1: 文档→脚本对齐

WORKFLOW.md 表格里列出的 10 个检查点（`check-state-yaml.sh` / PROD_TOUCHED / `check-gate.sh` / `check-changelog.sh` / `check-p6-evidence.sh` / `check-p6-provenance.sh` / `check-state-transition.sh` / `check-pruning.sh` / `check-scope-resolved.sh` / `check-retrospective.sh`）与 `agate/scripts/pre-commit-gate.sh`（hook 入口，见 `agate/scripts/README.md:13`「按顺序调度 9 项检查」）实际调度的脚本集合一致，本次改动未修改任何 `.sh` 文件（`shellcheck -S warning agate/scripts/*.sh` 0 输出确认无变更被漏检），纯文档合并，不涉及脚本行为变化。

**结论**：ALIGNED

### A2: 脚本→文档对齐

同上，本次未改任何脚本，脚本行为无变化，文档只是把三份表格收敛为一份，不存在"脚本改了文档没跟上"的情形。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

**A3a 连锁**：删除 dispatch-protocol.md/state-machine.md 表格 → 补充 WORKFLOW.md 表格（已完成，见核心问题节）→ 更新 protocol-alignment-review.md 反向传播表（已完成，`agate/assets/review-roles/protocol-alignment-review.md:40` 新增一行记录该收敛规则）。三步闭环，无遗漏环节。

**A3b 反向传播**：核对了以下应受影响但未出现在本次 diff 里的文件，确认均无需改动——
- `agate/orchestrator-template.md`：未见对 pre-commit 表格的直接摘引，不受影响。
- `agate/role-system.md`：未见对 pre-commit 表格的直接摘引，不受影响。
- 各执行角色文件（`assets/execution-roles/*.md`）：未见摘引具体表格行。
- `agate/phase-cards/*.md`：`P6-acceptance.md` 提到 `pre-commit-gate.sh` 会硬拦截 P6 阶段非证据文件，这是独立于被删表格的另一处正确引用（未受影响，仍准确）。
- `agate/scripts/README.md`：仍独立维护脚本清单（9 项检查的调度顺序），与本次去重的"检查项语义说明表"是不同维度的内容，无需同步。

**结论**：ALIGNED

### A4: 测试覆盖

本次改动是纯文档合并，不涉及脚本逻辑变化，理论上不需要新增 bats 测试。核对现有测试基线保持不变即可证明未引入回归：

- `bash agate/tests/scripts/count-tests.sh` 实跑输出：**总计 597 个测试用例**（符合任务要求的基线，未漂移）。
- `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` 实跑输出：**1..603，603 ok，0 not ok**（sanity 6 个 + 其余 597 个）。本次实跑中 `ok 10 ARCH.4 同一任务对 P6 归档两次，两份历史证据都保留` 一次性直接通过，未出现已知的秒级时间戳碰撞 flaky，无需重跑确认。

**结论**：ALIGNED（有实跑输出佐证，非无实跑的空绿灯）

### A5: 下游影响 + 文档传播

本次改动不改变任何 gate 的判定逻辑或退出码语义，纯粹是"同一份事实的表述位置收敛"，对已有项目消费该协议的行为无影响，无需 CHANGELOG 特别标注（本次任务范围内也未见 CHANGELOG 改动要求）。文档传播方面，`orchestrator-template.md`、`role-system.md`、`LIMITATIONS.md` 均未直接摘引被删表格内容，核对后确认无需同步（见 A3b）。

**结论**：ALIGNED

### A6: 锚点表覆盖

读取 `agate/scripts/check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS`（第 446-596 行，约 30 条锚点）全量。逐条确认：
- 所有以 `.md` 文件为 `"script"` 字段的锚点（如 "dispatch-context 派发指引节" → `agate/dispatch-protocol.md`，keywords `["dispatch-context", "dispatch_guide"]`；"PAUSED 语义翻转（dispatch-protocol）" → keywords `["正确路由", "非认输"]`）检测的都是特定关键词在该文件中**是否存在**，与"pre-commit 检查表格是否以表格形式出现在该文件"无任何关联。
- 没有任何一条锚点的 `keywords` 依赖于被删表格的具体行文字（如 "P2.1/P2.10"、"六道客观审计" 等表格措辞）。
- `check_script_alignment()` 函数（第 638 行起）逻辑上只做"脚本文件是否存在" + "关键词是否出现"两类判定，不解析表格结构。
- 实跑 `python3 agate/scripts/check-protocol-consistency.py`：CHECK 1-9 全部 PASS，0 ERROR，其中 CHECK 9（协议-脚本结构对齐）也 PASS，`bats` 中对应的 `CON.8`/`SG.6` 用例（分别校验 CHECK 9 含新增锚点、CHECK 9 锚点表覆盖全部 11 个 gate 脚本）均通过。

**结论**：ALIGNED（无任何锚点依赖被删表格的存在）

### A7: 设计原则一致性

本次改动是"单一事实来源（Single Source of Truth）"原则的体现——消除三份文档各自维护同一份事实的重复表格，改为一处权威 + 两处引用，属于典型的文档去重最佳实践，未见与 `agate/adr.md` 中任何已记录架构决策相冲突。协议自身的自省能力（protocol-alignment-review.md 反向传播表）也同步更新，记录了这条新收敛规则，符合"协议改自己也要走 self-gate"的既有原则。

**结论**：ALIGNED

---

## 建议修复项（非阻塞，供后续顺手清理）

1. `agate/WORKFLOW.md:255` CI backstop 段落的「git blame 单 author WARNING」建议补充具名为「`P6-acceptance.md` 的 git blame 单 author WARNING」，与 `agate/scripts/ci-gate-backstop.py:168` 的实际检测目标保持精确对应（去重前 dispatch-protocol.md 旧表原本有这个具名信息，去重后应保留在唯一权威版本里）。
2. 可选：`agate/WORKFLOW.md:258` 多任务适配段落可补上脚本名「`pre-commit-gate.sh` 扫描暂存区…」，与 state-machine.md 旧段落的具名精度对齐（优先级低于第 1 条，因为 `scripts/README.md` 已有该脚本名的权威记录）。

以上两项均为文字精度层面的建议，不影响协议语义正确性，不构成需要回退或重审的 MISALIGNED。
