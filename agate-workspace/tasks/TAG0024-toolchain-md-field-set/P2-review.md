---
phase: P2
task_id: TAG0024
type: review
parent: P2-design.md
trace_id: TAG0024-P2-review-rev2-20260825
status: approved
created: 2026-08-25
agent: plan-eng-review
---

# P2-review.md —— plan-eng-review 独立核验（TAG0024，复评第 2 轮）

本轮是**复评（第 2 轮）**。上一轮（trace_id `TAG0024-P2-review-20260825`，本文件旧版本）判定
`needs-revision`，唯一阻塞点：`dispatch_plan` 声明的三批次（`md-field-set-tool` /
`check-gate-debt-fixes` / `phases-yaml-consistency`）宣称"彼此文件不重叠、可并行派发 P4"，但
§1.1「改什么」表格中 `agate/tests/unit/test_check_gate.py` 追加用例一行同时归属
`check-gate-debt-fixes`（DEBT0019/20 用例）与 `phases-yaml-consistency`（RM-AG0049 用例，
BDD-25/26），实际存在文件级交叉，与"可并行"的声明矛盾。architect 在修复轮（
`P2-dispatch-context-architect-rev2.md`）采用方案①：把 RM-AG0049 相关用例全部改落
`test_check_structure_consistency.py`，`test_check_gate.py` 现只承载 DEBT0019/20（BDD-20~24）。
本轮不重做上一轮已通过的 5 个核验维度（同源铁律/候选真实性/不改什么/minimal_validation
方法/files_to_read 精准度），核验重心放在本次修复点本身。

本轮全部核验均对本 worktree 真实文件做过实测复核（`grep`/脚本化统计/`agate-frontmatter-check.py`
实跑），非纸面推演。

## 1. dispatch_plan 修复点逐条核验

**frontmatter / 开篇范围重述 / §1.1 表格三处是否真的一致**：

- frontmatter（第 16 行）：`dispatch_plan: {mode: static-batch, parallel_limit: 3, batches:
  [{id: md-field-set-tool, complexity: medium}, {id: check-gate-debt-fixes, complexity: low},
  {id: phases-yaml-consistency, complexity: low}]}`——三批次 id 与上一轮一致，未变。
- 开篇范围重述（第 19-23 行）：已改为"三个 dispatch_plan 批次彼此文件零交叉（见下节改
  什么——RM-AG0049 相关用例统一落在 `test_check_structure_consistency.py`，不再分散到
  `test_check_gate.py`），可并行派发 P4"——明确点名本次修复方案，不是笼统断言。
- §1.1 表格（第 40、41 行）：`test_check_gate.py` 追加用例一行改动点已删除"RM-AG0049
  outputs 声明用例"表述，仅保留"DEBT0019 列数精确匹配红/绿用例、DEBT0020 非仓库根 CWD
  用例"，关联 BDD 收窄为 **BDD-20~24**；`test_check_structure_consistency.py` 行新增
  "RM-AG0049 全部用例落地于本文件，不再分散到 `test_check_gate.py`（避免与
  `check-gate-debt-fixes` 批次同文件交叉）"，关联 BDD 标注 **BDD-25~26**。

三处表述逐字一致，无矛盾：frontmatter 声明三批次并行 → 开篇断言零交叉的具体依据 → 表格
逐行给出该依据的落地证据，三层递进一致，非"表格改了、开篇断言没跟着改"的半吊子修复。

**test_check_gate.py 与 test_check_structure_consistency.py 是否真的零交叉**：

逐文件核对 §1.1 表格全部 11 行改动点归属的 dispatch_plan 批次：

| 文件 | 表格改动行 | 归属批次 |
|---|---|---|
| `agate-md-field-set.py`（新增） | 1 行 | md-field-set-tool |
| `agate-md-field-set-gate-commands.py`（新增） | 1 行 | md-field-set-tool |
| `check-gate.py` `_check_roadmap_done()` | 1 行 | check-gate-debt-fixes |
| `check-gate.py` `gate_p8()` roadmap_path | 1 行 | check-gate-debt-fixes |
| `phases.yaml` P4 outputs | 1 行 | phases-yaml-consistency |
| `phases.yaml` P6.5 注释 | 1 行 | phases-yaml-consistency |
| `dispatch-prompt.md` | 1 行 | md-field-set-tool |
| `dispatch-context.md` | 1 行 | md-field-set-tool |
| `test_agate_md_field_set.py`（新增） | 1 行 | md-field-set-tool |
| `test_check_gate.py` 追加用例 | 1 行，仅 BDD-20~24 | check-gate-debt-fixes |
| `test_check_structure_consistency.py` 追加用例 | 1 行，仅 BDD-25~26 | phases-yaml-consistency |

`check-gate.py` 两行改动同属 `check-gate-debt-fixes`（批内不算交叉），`phases.yaml` 两行改动
同属 `phases-yaml-consistency`（批内不算交叉）。`test_check_gate.py` 与
`test_check_structure_consistency.py` 现分属两个不同批次且各自只出现一次——修复前那种
"同一物理文件被两个不同批次同时追加用例"的情况已不存在，三批次两两之间**没有共享文件**，
`dispatch_plan` 的"可并行"声明现在有真实的文件级证据支撑。

**BDD-25/26 覆盖是否完整（迁移后未丢失）**：脚本化统计全文 `BDD-N`/`BDD-N~M` 引用，覆盖
BDD-1 至 BDD-29 全部 29 条，无遗漏。`test_check_structure_consistency.py` 行明确标注
"phases.yaml P4 outputs 声明存在性用例（BDD-25）+ 核对 P4 outputs 追加后 S-1/S-2/S-3 均
0 mismatch（回归用例，非新增检查逻辑，BDD-26）"，§8"实现完成的标志"第 4 条同步印证
"`check-structure-consistency.py` 全量跑 S-1~S-6 均 0 mismatch（BDD-26/28）"——BDD-25/26
迁移到新文件后覆盖完整，未丢失，也未和其余 27 条 BDD 产生重号或遗漏。

**判定：dispatch_plan 阻塞点已对症修复，三处表述一致，两测试文件零交叉，BDD 覆盖完整。**

## 2. 笔误修正复核

- **grep 次数 7→10**：§1.3 风险 5（第 67 行）与 §3.8（第 335 行）均已改为"核实该字符串已
  出现 10 次"——dispatch-context 点名的这两处均已同步，确认到位。
  **新发现（非阻塞）**：全文 grep 同一断言发现第三处引用未被同步——§6 minimal_validation
  method 第 5 项（第 456 行）仍写"grep 确认 "P4-review" 已在 phase-cards/P4-implementation.md
  出现 **7 处**（第 90-153 行）"。这是同一个 grep 事实在文档内的第三处独立复述，dispatch-context
  当时只点名了"两处"（§1.3+§3.8）要求核对，未提及此处，architect 也确实只修了那两处，此处
  遗漏。**不影响任何技术结论**——第 1 节已复核 S-3 逻辑只做字符串存在性判断（`if fname not
  in card_text`），不判断出现次数，无论文中写 7 还是 10 都不改变"S-3 天然通过"这一结论；
  但文档内部同一事实出现"10 次"与"7 处"两种表述并存，属于遗留的文本不一致，建议 architect
  下次顺手统一为 10（不必单独开一轮修订）。
- **timeout 240→250**：`gate_commands.P3_timeout_seconds` 与 `P5_timeout_seconds`（第 468、
  470 行）均实测为 `250`，且第 485-487 行说明文字已同步改为"取 250s……按经验值 ×1.5 =
  248.55s，向上取整为 250s，与「宁高勿低」取值原则对齐，不再向下取整"——数值与说明文字均
  已修正，与自身 165.7×1.5 公式对齐，确认到位。

**判定：两处点名笔误均已修正到位；额外发现 1 处同一断言的第三次引用未同步（非阻塞，不影响
结论方向，见上）。**

## 3. 自检与抽查

- `FILE=agate-workspace/tasks/TAG0024-toolchain-md-field-set/P2-design.md python3
  agate/scripts/agate-frontmatter-check.py` 实跑 **exit 0**，frontmatter 结构合法。
- 抽查未改动内容：候选方案 A/B 全文、§1.3 其余 6 条风险项、§3.1~3.7/3.9/3.10 详细设计、
  §4 files_to_read 全部 17 条目、§5 env_constraints、§6 minimal_validation 其余 4 项、
  §7 gate_commands 其余 5 个 key（`P3`/`P5`/`P5_consistency`/`P5_shellcheck`/`P5_count`/
  `P5_ruff`）、§8 实现完成标志，均与上一轮评审引用/核实过的原文内容逐条比对一致，未发现
  借本轮修复之机夹带的无关改动。文件行数 506 行（上一轮为 503 行），增量与本次声明的修改点
  规模相符，非大幅重写。

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

- §6 minimal_validation method 第 5 项（第 456 行）仍写"7 处"，与同一事实在 §1.3/§3.8 已
  修正的"10 次"不一致，属于遗漏未同步的第三处引用。不影响任何技术结论（S-3 只做存在性判断，
  见上），建议下次顺手统一。

## 测试缺口

未发现新增测试缺口。BDD-1~29 全部在 §1.1/§8 中对应到具体测试文件（
`test_agate_md_field_set.py`/`test_check_gate.py` 追加（BDD-20~24）/
`test_check_structure_consistency.py` 追加（BDD-25~26）），迁移后覆盖仍然完整。

## 锁定决策

- `dispatch_plan` 三批次划分（`md-field-set-tool`/`check-gate-debt-fixes`/
  `phases-yaml-consistency`）经本轮核验确认文件级零交叉，"可并行派发 P4"声明现在有真实依据
  支撑，锁定为 P4 派发编排方案。
- `test_check_gate.py` 仅承载 DEBT0019/20（BDD-20~24），`test_check_structure_consistency.py`
  承载 RM-AG0049（BDD-25~26）——测试文件归属锁定，P4 implementer 按此归属落地用例，不再
  混放。
- 上一轮已锁定的候选方案 A（importlib 动态复用）、`_ROADMAP_EXPECTED_COLS = 9`、DEBT0020
  仓库根锚定方案、gate_commands 六个独立 key 拆分方案继续有效，本轮未改动。

## 返回给主 Agent

status: approved（复评通过，唯一阻塞点已对症修复并逐项验证成立；1 项非阻塞遗留记录：
§6 第 5 项 grep 次数引用"7 处"未同步为"10 次"，不影响结论，可后续顺手修正）
