---
review_date: 2026-07-01
reviewer: protocol-alignment-review
review_target_commit: 133c7b4
change_summary: self-gate 加反向传播机制（SELF-GATE.md 派发模板改写 + A3/A5 加反向传播 + A3 拆 A3a/A3b + 反向传播常见路径表 + orchestrator 措辞按阶段差异化 + RT.5/RT.6 新增）
files_changed:
  - SELF-GATE.md
  - agate/assets/review-roles/protocol-alignment-review.md
  - agate/orchestrator-template.md
  - agate/tests/unit/check-retrospective.bats
  - docs/reviews/agate-alignment-review-2026-07-01.md
---

# 协议-脚本对齐审查（133c7b4 补充审查）

> 主审查是 2026-07-01 上半天的 `agate-alignment-review-2026-07-01.md`，本报告是本次 commit 后用反向传播方法做的"遗漏扫描"——按 SELF-GATE.md 新机制（意图分析 + 反向传播）走一遍。

## 意图分析

**为什么改**：self-gate 之前只审"diff 对不对"，漏掉了"该影响但没影响的文件"。本次升级为"diff + 反向传播"，把"改了什么 + 应影响什么 + 影响到了没"作为审查基础能力固化进 SELF-GATE.md 派发模板和协议对齐审查角色。

**改了什么方向**：
1. SELF-GATE.md 派发模板加意图分析 + 反向传播两步（变更触发 + 全量触发）
2. protocol-alignment-review 角色 A3 拆 A3a（连锁）+ A3b（反向传播），A5 加文档传播；新增"反向传播常见路径"推理起点表
3. orchestrator-template.md:82 描述复盘提醒的"重试 ≥3 次"按阶段差异化（P3/P5/P6/P7/P8=2, P1/P2/P4=3）
4. check-retrospective.bats 新增 RT.5（retries[P3]=2 触发）/RT.6（retries[P3]=1 不触发），覆盖 P3 MAX=2 的边界
5. 主审查文件加"补充审查"段记录遗漏扫描

## 反向传播检查

本次 commit 触及**两类语义变更**：
- **(a) self-gate/reverse-prop 文档级**（SELF-GATE.md、protocol-alignment-review.md）
- **(b) 重试措辞按阶段差异化**（orchestrator-template.md:82、check-retrospective.bats）

反向传播候选清单（按"应被影响"优先级）：

| # | 候选文件 | 是否应被影响 | 验证结论 |
|---|---------|------------|---------|
| 1 | `agate/git-integration.md` | **是**（重试措辞 | (b) | **❌ MISALIGNED**——仍写"重试 ≥3"（line 168），与 orchestrator-template.md:82 新描述矛盾 |
| 2 | `agate/tests/README.md` | **是**（RT.5/RT.6 加了 | (b) | **❌ MISALIGNED**——line 38 写 check-retrospective.bats=4，实际 @test=6 |
| 3 | `agate/assets/review-roles/protocol-alignment-review.md` 自身 | **是**（A3/A5 改了 | (a) | **❌ MISALIGNED**——line 68-75 输出模板汇总表里 A3/A5 仍是旧标签"一致性连锁"/"下游影响"，与 line 22-24 审查清单不一致 |
| 4 | `agate/orchestrator-template.md:82` | 已改 | (b) | ✅ ALIGNED |
| 5 | `agate/tests/unit/check-retrospective.bats` | 已改（RT.5/RT.6 | (b) | ✅ ALIGNED，6 用例全过 |
| 6 | `agate/WORKFLOW.md` | 否（line 274 用"按阶段 2-3 次"泛指，已引向 state-machine.md 表 | (b) | ✅ ALIGNED，泛指表述对按表权威源 |
| 7 | `agate/dispatch-protocol.md` | 否（用 `MAX_RETRY(Pn)` 引用 | (b) | ✅ ALIGNED |
| 8 | `agate/loop-orchestration.md` | 否（line 134 同样泛指 | (b) | ✅ ALIGNED |
| 9 | `agate/role-system.md` | 否（不涉及 retry 措辞 | (b) | ✅ ALIGNED |
| 10 | `agate/LIMITATIONS.md` 局限 5 | 否（提到 protocol-alignment-review + CHECK 9 + A1-A6，反向传播是 A3 子能力，描述仍准确 | (a) | ✅ ALIGNED |
| 11 | `agate/platform-notes.md` | 否（不涉及 | (b) | ✅ ALIGNED |
| 12 | `agate/AGENTS.md` | 否（不涉及 | (a) | ✅ ALIGNED |
| 13 | `agate/scripts/check-state-transition.sh` / `check-retrospective.sh` | 否（ff05aa5 已同步 MAX_RETRY_MAP 字面值 | (b) | ✅ ALIGNED |
| 14 | `agate/scripts/check-protocol-consistency.py` CHECK 9 锚点表 | 否（无新增 A3/A5 锚点需求 | (a) | ✅ ALIGNED |
| 15 | `agate/scripts/README.md` | 否（不涉及 | (a) | ✅ ALIGNED |
| 16 | `agate/assets/templates/dispatch-prompt.md` | 否（项目侧派发模板，不是 self-gate 派发 | (a) | ✅ ALIGNED |
| 17 | `.github/workflows/protocol-tests.yml` | 否（仅跑 bats/shellcheck/consistency | (a) | ✅ ALIGNED |
| 18 | `agate/tests/integration/protocol-alignment-review.bats` SG.1-SG.6 | 否（grep A1-A6 + SELF-GATE.md 字符串命中仍通过）——但**有更深层担忧**：现有测试只验证字符串存在，不验证反向传播机制 subagent 是否真的执行（属 A4 局限，不属 A3 漏改） | (a) | ✅ ALIGNED（结构层）；⚠️ 留 NEEDS_HUMAN_REVIEW（语义层） |
| 19 | `README.md` | 否（不涉及版本 bump | (a) | ✅ ALIGNED |
| 20 | `CHANGELOG.md` | **是**（A5 文档传播：协议语义变更应标 [Unreleased]） | (a) | **❌ MISALIGNED**——本次 commit 没在 `[Unreleased]` 加 self-gate 反向传播条目 |

**反向传播结论**：发现 4 个 MISALIGNED（#1, #2, #3, #20）。

## A1-A6 审查结论汇总

| # | 审查项 | 结论 | 备注 |
|---|--------|------|------|
| A1 | 文档→脚本对齐 | **ALIGNED** | SELF-GATE.md / protocol-alignment-review.md / orchestrator-template.md / state-machine.md 重试表 / check-retrospective.sh MAX_RETRY_MAP 字面值 / check-state-transition.sh MAX_RETRY_MAP 字面值——三者一致 |
| A2 | 脚本→文档对齐 | **ALIGNED** | check-retrospective.bats 新增的 RT.5/RT.6 边界测试覆盖了 P3 MAX=2 的语义；orchestrator 描述与脚本行为对齐 |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED** | 反向传播命中 4 处遗漏：git-integration.md:168、tests/README.md:38、protocol-alignment-review.md:68-75、CHANGELOG.md |
| A3a | 连锁（已知的衍生改动） | **ALIGNED** | RT.5/RT.6 ↔ orchestrator 措辞 ↔ state-machine 表 ↔ MAX_RETRY_MAP 字面值——所有衍生同步 |
| A3b | 反向传播（主动推断的应被影响文档） | **MISALIGNED** | 同 A3 |
| A4 | 测试覆盖 | **ALIGNED** | RT.5/RT.6 新增覆盖 P3 MAX=2 边界；SG.1-SG.6 仍过；bats 172/172 全绿 |
| A5 | 下游影响 + 文档传播 | **MISALIGNED** | CHANGELOG.md `[Unreleased]` 未加本次 self-gate 反向传播条目；orchestrator 改了但 git-integration.md 措辞没同步 |
| A6 | 锚点表覆盖 | **ALIGNED** | CHECK 9 锚点表无新增需求（A3/A5 是 subagent 审查项，不在 check-protocol-consistency.py 的锚点覆盖范围）|

## 逐项审查详情

### A1：文档→脚本对齐

- **state-machine.md:427-438 重试上限表**：P1/P2/P4=3, P3/P5/P6/P7/P8=2
- **check-state-transition.sh:15**：`MAX_RETRY_MAP="${MAX_RETRY_MAP:-P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2}"`——完全一致
- **check-retrospective.sh:21**：同样字面值 `P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2`——完全一致
- **orchestrator-template.md:82**："P3/P5/P6/P7/P8 ≥2 次、P1/P2/P4 ≥3 次"——与表一致
- **SELF-GATE.md** / **protocol-alignment-review.md** 自身：定义审查机制，不涉及 retry 字面值
- **结论**：ALIGNED

### A2：脚本→文档对齐

- **check-retrospective.sh 行为**：按 `max_map.get(phase, 3)` 查每阶段 MAX，命中即警告"重试超限"
- **check-retrospective.bats:55-86** 新增 RT.5（P3=2 触发）/RT.6（P3=1 不触发），验证 P3 边界
- 跑测试：`bats agate/tests/unit/check-retrospective.bats` → 6/6 ok
- **结论**：ALIGNED

### A3：一致性连锁 + 反向传播

#### A3a：连锁

本次 diff 列出的 5 个文件全部互相一致，无连锁遗漏（见 A1）。

#### A3b：反向传播（关键）

逐项验证见上文"反向传播检查"表，4 处 MISALIGNED：

**#1 `agate/git-integration.md:168`**
- 现状：`检测到 gate 重试 ≥3 / SCOPE+ / override → 提醒写复盘`
- 应改：按阶段差异化（P3/P5/P6/P7/P8 ≥2）
- 来源：orchestrator-template.md:82 已按阶段写，git-integration.md 漏
- 建议修复：`检测到 gate 重试超限（P3/P5/P6/P7/P8 ≥2 次、P1/P2/P4 ≥3 次）/ SCOPE+ / override`
- **严重度**：Minor（同一 commit 涉及但漏改；commit message ff05aa5 当时也漏了）

**#2 `agate/tests/README.md:38`**
- 现状：`check-retrospective.sh | unit/check-retrospective.bats | 4`
- 应改：`6`（RT.5/RT.6 是本次 commit 新加的）
- 验证：`grep -c "^@test" agate/tests/unit/check-retrospective.bats` → 6
- **严重度**：Minor（测试数对不上，但 count-tests.sh 输出以脚本实际为准）

**#3 `agate/assets/review-roles/protocol-alignment-review.md:68-75` 自身**
- 现状（line 72）：`| A3 | 一致性连锁 | ... |`（旧标签）
- 现状（line 73）：`| A5 | 下游影响 | ... |`（旧标签）
- line 22-24 审查清单已改为：`A3 = 一致性连锁 + 反向传播`、`A5 = 下游影响 + 文档传播`
- 同一文件内不一致——subagent 报告输出格式（line 56-90 的模板）若用 line 68-75 的标签，会和实际审查项命名错位
- 建议修复：把 line 72-73 改为 `A3 | 一致性连锁 + 反向传播` 和 `A5 | 下游影响 + 文档传播`
- **严重度**：Minor（同一文件内部标签不一致）

**#20 `CHANGELOG.md [Unreleased]`**
- 现状：只有 ff05aa5（MAX_RETRY per-phase + 回退跳变恢复 exit 1）条目，没加 133c7b4（self-gate 反向传播）
- A5 文档传播要求：协议语义变更必须标 `[Unreleased]`
- 建议修复：在 `[Unreleased]` 加新条目记录 SELF-GATE.md 派发模板加意图分析+反向传播、A3 拆 A3a+A3b、A5 加文档传播
- **严重度**：Minor（用户级 release 时会漏标本次变更，破坏 changelog 完整性）

### A4：测试覆盖

- **RT.5/RT.6**：本次新增，覆盖 P3 MAX=2 边界 + 未达边界
- **SG.1-SG.6**：未改（grep 字符串命中仍通过）——**NEEDS_HUMAN_REVIEW**：
  - 现有测试只验证"SELF-GATE.md 含派发模板字符串" / "角色文件含 A1-A6 grep 命中"，不验证 subagent 实际执行反向传播
  - 这是 A4 的结构性局限——A3b 反向传播是**行为契约**，靠字符串存在性检查不到
  - 缓解：本次新增 subagent 派发模板明示步骤（`## 第二步：反向传播——列出应被影响的文件`），主 Agent 审留痕文件即可验证
  - 决策：接受现有覆盖（结构兜底 + 人工审查），不强行添加新 bats 用例（成本 > 收益）

**结论**：ALIGNED（bats 172/172 全绿，附带 NEEDS_HUMAN_REVIEW 一条）

### A5：下游影响 + 文档传播

- **CHANGELOG.md 未同步**（#20）——MISALIGNED
- **git-integration.md 措辞未同步**（#1）——MISALIGNED
- **orchestrator-template.md:82 已同步**（本次 commit 改）——ALIGNED
- **role-system.md / platform-notes.md / WORKFLOW.md / dispatch-protocol.md / loop-orchestration.md**：经反向传播验证，不需要改（用泛指或 MAX_RETRY(Pn) 引用）

### A6：锚点表覆盖

- **check-protocol-consistency.py:486-572 SCRIPT_ALIGNMENT_ANCHORS**：无新增需求
- **A3/A5 是 subagent 行为契约**，不在结构锚点检查范围（CHECK 9 只看脚本关键词）
- **SG.6 测试**：`bats agate/tests/integration/protocol-alignment-review.bats` → 6/6 ok，11 个 gate 脚本都在锚点表中
- **结论**：ALIGNED

## 验证记录

| 检查 | 命令 | 结果 |
|------|------|------|
| bats 全量 | `bats agate/tests/{sanity.bats,unit/,regression/,integration/}` | **172/172 ok** |
| check-protocol-consistency.py | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR（5 预存 WARNING 与本次无关）|
| shellcheck | `shellcheck agate/scripts/*.sh` | 0 ERROR（3 预存 info 与本次无关）|
| count-tests.sh | `bash agate/tests/scripts/count-tests.sh` | 166 用例（不含 sanity.bats 的 6，加 172 全数对）|

## 最终结论

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（4 处反向传播遗漏：#1 git-integration.md:168、#2 tests/README.md:38、#3 protocol-alignment-review.md:68-75、#20 CHANGELOG.md [Unreleased]）|
| A4 | 测试覆盖 | ALIGNED（附 NEEDS_HUMAN_REVIEW：反向传播行为契约无法被字符串 grep 覆盖）|
| A5 | 下游影响 + 文档传播 | **MISALIGNED**（与 A3 #1/#20 重叠）|
| A6 | 锚点表覆盖 | ALIGNED |

**修复建议**（合并 #1/#2/#3/#20 的统一修复方案）：
1. `agate/git-integration.md:168`：把"重试 ≥3"改为"重试超限（P3/P5/P6/P7/P8 ≥2 次、P1/P2/P4 ≥3 次）"
2. `agate/tests/README.md:38`：把 `check-retrospective.sh | 4` 改为 `6`
3. `agate/assets/review-roles/protocol-alignment-review.md:72-73`：把汇总表里 A3/A5 标签与 line 22-24 审查清单对齐
4. `CHANGELOG.md [Unreleased]`：加新条目记录 133c7b4 的 self-gate 反向传播机制

修复后重跑本审查 4 个 A 项，确认全部 ALIGNED 方可 commit。