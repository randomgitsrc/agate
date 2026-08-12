---
phase: P7
task_id: TAG0001-tech-debt-closure
type: consistency
parent: P2-design.md
trace_id: TAG0001-P7-20260812
status: draft
created: 2026-08-12
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---

# TAG0001 — P7 一致性检查（跨文件交叉核对：DESIGN_GAP 配对 / SCOPE+ 闭环 / 跨文件一致性 / 未决项清零）

> 角色：consistency-reviewer（独立视角）。审查对象：TAG0001 P1-P6 全部产出 + worktree `agate/` 实际改动（HEAD=a6fa468，分支 dev/workspace）。
> 方法：逐文件读取 P1/P2/P4-core/P4-docs/P4-fix/P4-review/P5-unit/P6-acceptance/P0-brief，再与 git log 实际提交（006c3e6 P4 / 5bdcd90 P5 / a6fa468 P6）对照核验。只审不写，未修改任何产出文件。
> 环境标记：`[PROD_NOT_TOUCHED]`——本次仅只读文件 + 只读 git 查询，未改 `~/.agate`、未修改 worktree 任何文件。

---

## 1. DESIGN_GAP 配对（P4 声明 → 本文件转抄 + REVIEWED）

[DESIGN_GAP: P3 测试 fixture test_bdd_2 的 mkdir -p 大括号被引号包裹不展开，仅建 1 目录（应为 9）——测试代码缺陷不在本角色文件集，已如实标注，交由主 Agent/docs 组处理（改测试 fixture 或评估断言），本次未改动测试文件]（转抄自 P4-implementation-core.md §DESIGN_GAP）

[DESIGN_GAP_REVIEWED: 已确认并核实修复落地——git 006c3e6 中 `agate/tests/unit/agate-debt-check.bats` 的 test_bdd_2 已改为显式参数 `mkdir -p "$dir/roadmap" "$dir/tasks" ... "$dir/debt"`（大括号不再被引号包裹）；test_bdd_3 SETUP 断言由 `grep 'debt/'` 改为 `grep 'debt'`（SETUP.md:114 只含 `{...,debt}` 字面量）；R5.1-3（v060-p8-cached.bats）补 `debt_check: none` 三处。与 P4-core.md:58-59 声明、P4-review.md §DESIGN_GAP 复核一致。]

> P4-implementation-fix.md §DESIGN_GAP 声明为"无自主设计决策——修复方向完全遵循 verifier 诊断"（serialize_evidence int 归一），**未声明独立 DESIGN_GAP**，无新增转抄项。P4-implementation-docs.md 声明"无 [DESIGN_GAP]"（P2 方案对 docs 组改动面足够明确）。故全任务 DESIGN_GAP 总数 = 1，REVIEWED = 1，配对齐全。

## 2. SCOPE+ 闭环（P1 frontmatter scope_resolved 2 项）

[SCOPE_RESOLVED: P1-requirements.md frontmatter scope_resolved 第 1 项——"P8 gate 加 debt_check 缺失即 exit 1 需同步更新 check-gate.bats 既有 6 处 G8 fixture"。已闭环：P2 §9 [SCOPE+] #1 落方案（G8.2/3/4/6/7/8 补 debt_check）+ P3 新增 G8.9/G8.10 两用例；git 006c3e6 实测 check-gate.bats:1165/1186/1205/1231/1250/1543 六处 `debt_check: none` + G8.9（缺字段 exit 1）+ G8.10（内容任意 exit 2）在案。]

[SCOPE_RESOLVED: P1-requirements.md frontmatter scope_resolved 第 2 项——"check-protocol-consistency.py SCRIPT_ALIGNMENT_ANCHORS 需为 check-debt.sh 加锚点 + scripts/README.md 脚本清单补录"。已闭环：P2 §9 [SCOPE+] #2 落方案；git 006c3e6 实测 check-protocol-consistency.py:646-648 新增 `check-debt.sh` 锚点（desc「tech-debt schema 校验 + 回退覆盖比对」、keywords `["debt","retreat"]`）+ scripts/README.md:23（Gate 检查表补 check-debt.sh）+ :82（.py 表补 agate-debt-check.py）。]

> 两项 SCOPE+ 均由 P2 方案承接、P4 实现在 git 落地，P1 frontmatter scope_resolved 声明一致，闭环成立。

## 3. 跨文件一致性检查

### 3.1 P2 packages=[agate] 与 P8 release bump 范围（P2§packages 锚点）

P2-design.md frontmatter `packages: [agate]`（协议本体单一包），与 P1-requirements.md `packages: [agate]` 一致。本次改动面（git 006c3e6 共 28 文件）全部落在 worktree `agate/` 与 `docs/tasks/TAG0001*` 记录内，无跨包改动。P8 尚未执行（P7 在 P8 之前），bump 范围终值待 P8-release.md 产出后由主 Agent 按 `git diff` 范围最终确认；本阶段结论：无跨包面，P8 bump 范围与 packages=[agate] 无矛盾面。

### 3.2 P1 20 条 BDD 与 P6 验收结果数量 + 内容对应（P1§3 BDD / P6-acceptance 锚点）

P1-requirements.md §3 定义 BDD-1..20（20 条，功能组 A-F）。P6-acceptance.md Summary=20/20 PASS，0 FAIL，功能组 A-F 逐条列示：
- BDD-1/2/3/4（功能组 A debt/ 归类修正）→ P6 四条 PASS，引用 WORKFLOW.md:85-86 / SETUP.md:114 / orchestrator-template.md:102 / state-machine.md:40 / UPGRADING.md:97-99 / TAG0003 修订注——内容与本审查 §3.4 grep 结果一致。
- BDD-5..10（schema 校验）→ P6 六条 PASS，与 P2 §2.2 校验规则（必填/枚举/closed 准入/no-op）逐条对应。
- BDD-11（T001 回填）→ P6 PASS（5 条 source: retrospective 条目，grep -c=5）。
- BDD-12..15（回退强制）→ P6 四条 PASS；BDD-15 含 P5 修复的 int 边界回归验证（bdd-15-int-regression.log）。
- BDD-16/17/18（P8 留痕）→ P6 三条 PASS，对应 P8-release.md:27/48/60 与 check-gate.sh:426-428。
- BDD-19/20（判据）→ P6 两条 PASS，对应 tech-debt-template.md:9-15 与 plan-eng-review.md:20。

数量 20=20，逐条内容与 P1 §3 验收条件对应，无"数量对但内容错位"。

### 3.3 P4 实现与 P2 §0.1 改动面表吻合（P2§0.1 改动面表 / P4§impl-path 锚点）

P2-design.md §0.1 改动面表 16 项，逐一与 git 006c3e6 diff 核对：

| # | P2 声明文件 | git 006c3e6 实际改动 | 吻合 |
|---|---|---|---|
| 1 | tech-debt-template.md（新增） | +101 行 | ✓ |
| 2 | agate-debt-check.py（新增） | +189 行 | ✓ |
| 3 | check-debt.sh（新增） | +80 行 | ✓ |
| 4 | check-gate.sh P8 分支 | +6 行（:426-428 debt_check） | ✓ |
| 5 | P8-release.md | +5 行（:27/:48/:60） | ✓ |
| 6 | state-transitions.md | +2 行（:84 回退强制） | ✓ |
| 7 | P6-acceptance.md + P4-implementation.md | 各 +2 行（:144/:27 DEBT 强制） | ✓ |
| 8 | agate-retreat-to.sh | +3 行（:72-73 提醒） | ✓ |
| 9 | plan-eng-review.md | +1 行（:20） | ✓ |
| 10 | WORKFLOW.md | +5 行（:79 9 子目录 / :85 注释 / :86 debt/） | ✓ |
| 11 | orchestrator-template.md / SETUP.md / state-machine.md | 各 +2/-2 行（三处同一 9 集字面量） | ✓ |
| 12 | UPGRADING.md | +13 行（v0.43.0 节 :94-103） | ✓ |
| 13 | check-protocol-consistency.py + scripts/README.md | +5 / +2 行（CHECK9 锚点 + 清单补录） | ✓ |
| 14 | TAG0003 P1+P6 BDD-1 修订注 | 各 +1 行 | ✓ |
| 15 | check-gate.bats G8 fixture | 6 处 debt_check + G8.9/G8.10 | ✓ |
| 16 | agate-debt-check.bats（新增） | +4 行（含 DESIGN_GAP 修复） | ✓ |

16/16 全部落地，无"方案声明但未实现"项。

### 3.4 debt/ 归类修正同步面完整性（WORKFLOW.md 目录图 / agents/ 注释 / 三处 mkdir / UPGRADING / TAG0003 修订注锚点）

- WORKFLOW.md:79「固定 9 个子目录」、:85 `agents/ # agent 输入知识（project.md / memory）`、:86 `├── debt/ # 技术债登记`——目录图 + agents/ 注释同步 ✓
- 三处 mkdir 同一 9 集字面量：orchestrator-template.md:102 / SETUP.md:114 / state-machine.md:40 均为 `{roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt}` ✓
- grep 全 worktree `agate/` 无「8 个子目录」残留（P4-review 注记的 TAG0003 P6-evidence/bdd-01-init.log 属已验收证据存档，不在改动范围）✓
- UPGRADING.md v0.43.0 节（:94-103）含 ① 子目录 8→9 ② tech-debt 路径 debt/tech-debt.md ③ debt_check 必填 ④ 回退强制 ✓
- TAG0003 P1-requirements.md 与 P6-acceptance.md 各含「2026-08-12 修订注 9 子目录」一行（git 006c3e6 实测）✓
- `agents/.*tech-debt` grep 命中仅为 UPGRADING.md:97 的否定式说明（"tech-debt 不再归入 agents/"）与 agate-debt-check.bats:22/49 的**断言否定检查**，非过期路径残留 ✓

### 3.5 P4 三份实现记录声明与 git 实际改动一致（P4-implementation-core / -docs / -fix 锚点）

- core.md 声明 5 文件改动清单 → git 006c3e6 中 core 组 5 文件（模板/校验器/薄壳/check-gate.sh/retreat-to.sh）全部在案，改动内容与描述一一对应 ✓
- docs.md 声明 10 文件集 → git 006c3e6 中 docs 组文件（P8 卡/state-transitions/P6/P4 卡/plan-eng-review/WORKFLOW/mkdir 三处/UPGRADING/consistency+README/TAG0003 修订注）全部在案 ✓；docs.md 边界声明"未改动 core 组文件集"与 git 中两角色文件无重叠一致 ✓
- fix.md 声明仅改 agate-debt-check.py serialize_evidence（+10 行）→ git 5bdcd90 diff 实测仅该函数改动，int/bool 归一分支在案 ✓

## 4. 未决项清零

- P1-requirements.md:209 为 `[NO_NEED_CONFIRM]`（已解决标记），全任务目录无残留行首 `[NEED_CONFIRM]`。
- 全任务目录 grep `^\s*\[(BLOCKER|DEVIATION-CRITICAL)` 无匹配；P4-review.md status: approved（0 BLOCKER / 0 CRITICAL）。
- P5-test-results/unit.md 唯一失败 test_bdd_15（flaky）根因已由 P5 判定为交付代码缺陷并回 P4 修复（serialize_evidence int 边界），修复后 20/20 绿 + 全量 676/0，P6 验收 20/20 PASS——无未处理的失败项。
- 遗留观察（非阻断，不构成本阶段未决项）：P4-review.md O1（check-debt.sh $2 与 git log 的 repo 一致性，建议 `git -C` 加固）/ O2（--covered-hashes hex 启发式误判可能），均为 P2 §10 已诚实标注的召回局限与已知建议，已 approved 归档。

## 5. 结论

**BLOCKER=0 / DEVIATION-CRITICAL=0 / DEVIATION=0**，DESIGN_GAP 1 条已 REVIEWED 配对（§1），SCOPE+ 2 项已闭环（§2），跨文件一致性 5 项全部通过（§3），未决项清零（§4）。TAG0001 P1-P6 产出与 worktree 实际改动无一致性缺口，P7 通过。

**环境标记：`[PROD_NOT_TOUCHED]`**——本次仅只读文件 + 只读 git 查询（log/show/diff），未修改任何产出文件、未改动 worktree `agate/`、未触碰 `~/.agate`。
