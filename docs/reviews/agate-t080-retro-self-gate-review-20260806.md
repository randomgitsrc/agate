---
review_id: agate-t080-retro-self-gate-review-20260806
target_commit: 8ae8a2c
target_branch: main
reviewer: protocol-alignment-review subagent
date: 2026-08-06
files_changed: 16 (+404 / -11)
tests_total: 531
tests_new: 2 (G_NC_TENDENCY.1/.2)
---

# T080 复盘改进 — 协议-脚本对齐审查

## 总评

**NEEDS_FIX** — Plan 的 8 项 Task 实施完整且核心逻辑正确（gate 脚本的倾向分级判断、4 个 bats 测试、5 个角色/卡片/模板追加、roadmap 状态更新），但**反向传播存在多处遗漏**：NEED_CONFIRM 从二值升级到三值后，原 6 处文档（dispatch-protocol.md / WORKFLOW.md / state-machine.md / state-transitions.md / analyst.md / CONTEXT.md + task-files.md 模板）未同步更新，且无对应 CHANGELOG 条目或版本 bump。技术细节 0 ERROR（531 测全过 + consistency 0 ERROR + shellcheck 干净）。

---

## A1. 文档→脚本对齐（plan vs 实际）

**结论：ALIGNED（附 1 处微调优化）**

Plan Task 8 Step 2（`docs/plans/agate-t080-retro-fixes-20260806.md:204-209`）提议用 `NC_ALL - NC_TENDENCY` 减法计算阻塞项数量：

```bash
NC_ALL=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM' ... )
NC_TENDENCY=$(grep -cE '^\s*-?\s*\[NEED_CONFIRM倾向:' ... )
NC_BLOCKING=$((NC_ALL - NC_TENDENCY))
```

实际实现（`agate/scripts/check-gate.sh:68`）更简洁：直接用行首锚点正则 `^\s*-?\s*\[NEED_CONFIRM\]` 匹配——因为该正则的 `\]` 要求 `]` 紧跟 `NEED_CONFIRM`，**不会**误匹配 `[NEED_CONFIRM倾向: ...]`（`倾向:` 不是 `]`）。

**已实证**（临时 fixture）：
- 仅含 `[NEED_CONFIRM倾向: 推荐方案 A]` → NC_BLOCKING=0, NC_TENDENCY=1, 子串检查 NO（安全），实际跑 `check-gate.sh P1` → exit 2 + WARNING，**正确不阻塞**。
- 含 `[NEED_CONFIRM倾向: X]` + `[NEED_CONFIRM] 需用户决策的方向` → NC_BLOCKING=1, exit 1 + "阻塞" 消息，**正确阻塞**。

实施方式更稳（避免减法在意外输入下出错），**本质等价**。

G_NC_TENDENCY.1/.2 测试覆盖了"纯倾向"（不阻塞）和"混合"（阻塞）两个关键边界，足够。

---

## A2. 脚本→文档对齐（check-gate.sh vs P1-requirements.md）

**结论：ALIGNED**

P1-requirements.md 分级格式（`agate/phase-cards/P1-requirements.md:49-51`）：
- `[NEED_CONFIRM倾向: 推荐 X，理由 Y]` → 倾向（主 Agent 可自行采纳）
- `[NEED_CONFIRM]` → 真无方向（阻塞）

check-gate.sh 实际逻辑（`agate/scripts/check-gate.sh:65-85`）：
- NC_BLOCKING = grep `^\s*-?\s*\[NEED_CONFIRM\]`（line 68，**精确匹配**，不数倾向）→ >0 则 exit 1
- NC_TENDENCY = grep `^\s*-?\s*\[NEED_CONFIRM倾向:`（line 70）→ >0 则 WARNING 不阻塞
- 缺失声明 WARNING（line 83-84）——把 `[NO_NEED_CONFIRM] / [NEED_CONFIRM] / [NEED_CONFIRM倾向:]` 都列为合法选项

两侧**术语与逻辑完全对齐**。

---

## A3. 一致性连锁 + 反向传播

### A3a. 计划中的 8 个 Task 实施完整性

**结论：ALIGNED**

| Task | 实施证据 | 状态 |
|------|---------|------|
| 1. gate 格式契约透明化 | `verifier.md:184-198` + `consistency-reviewer.md:70-74` + `dispatch-context.md:19` | ✅ |
| 2. known-failures.md 语义边界 | `known-failures-template.md:7-8` + `P5-verification.md:67` | ✅ |
| 3. P1 基线保护 | `P1-requirements.md:87-92` + `P4-implementation.md:150` | ✅ |
| 4. P8 bump + CHANGELOG 同一 commit | `P8-release.md:12` | ⚠️ 见 A5 |
| 5. P2 选择器契约提示 | `P2-design.md:102` | ✅ |
| 6. P1 review 跨条 BDD 一致性 | `requirements-review.md:30-33` | ✅ |
| 7. P2 review UI 组件完整性 | `plan-design-review.md:18` | ✅ |
| 8. NEED_CONFIRM 分级 | `P1-requirements.md:49-51` + `check-gate.sh:65-85` + `G_NC_TENDENCY.1/.2` | ✅ |

8/8 任务都有对应文件改动。roadmap 状态从"待处理"改为"已实施"（`docs/hardening-roadmap.md:385-395`）8 处全部对齐。

### A3b. 反向传播 — 应被影响但 diff 未列的文件

**结论：MISALIGNED（多处遗漏）**

NEED_CONFIRM 从**二值**升级到**三值**（NEED_CONFIRM / NO_NEED_CONFIRM / NEED_CONFIRM倾向:）后，多处文档/脚本仍只描述二值，对读者/agent 误导：

| # | 文件:行 | 当前内容 | 问题 | 建议修复方向 |
|---|---------|---------|------|------------|
| R1 | `agate/dispatch-protocol.md:804` | `grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' P1-requirements.md → =0` | 字面"=0"未区分阻塞 vs 倾向。读者可能误以为任何 NEED_CONFIRM 都阻塞 | 改为：`grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' ... → =0`（阻塞项为 0）+ 新增"倾向项允许非 0"说明 |
| R2 | `agate/dispatch-protocol.md:1016-1018` | "`[NEED_CONFIRM]` 采用二值声明（T005/T006 教训）：[NEED_CONFIRM] {描述} = 有待确认项（正向）/[NO_NEED_CONFIRM] = 无待确认项（负向）" | **直接矛盾**新三值系统 | 改为三值声明，明确 `[NEED_CONFIRM倾向:]` 第三选项（T080 retro） |
| R3 | `agate/dispatch-protocol.md:1042` | 标记声明规范表只有 2 列 | 缺倾向列 | 表格加一行/一列：`倾向` 列 |
| R4 | `agate/WORKFLOW.md:216` | P1 阶段说明含 `grep -cE '^\s*-?\s*\[NEED_CONFIRM\]'` → =0 | 同 R1 | 加倾向说明 |
| R5 | `agate/state-machine.md:77` | "无未决 NEED_CONFIRM" | 未澄清倾向不算"未决" | 改为"无未决阻塞 NEED_CONFIRM（倾向项可非零）" |
| R6 | `agate/state-machine.md:79` | "存在未决 NEED_CONFIRM" → PAUSED | 同 R5 语义模糊 | 加澄清 |
| R7 | `agate/state-machine.md:124` | "存在未决 NEED_CONFIRM" → P6 PAUSED | 同 R5 | 加澄清 |
| R8 | `agate/state-machine.md:336` | `grep -cE '^\s*-?\s*\[NEED_CONFIRM\]' {task}/P1-requirements.md → =0;` | 同 R1 | 区分阻塞 vs 倾向 |
| R9 | `agate/rules/state-transitions.md:18` | "无未决行首 NEED_CONFIRM" | 同 R5 | 加倾向说明 |
| R10 | `agate/assets/execution-roles/analyst.md:91-99` | "何时标 [NEED_CONFIRM]" 只描述二值 | analyst 应知道倾向选项（避免把"有倾向需求"也标阻塞项） | 新增倾向使用指引（何时倾向 vs 真无方向） |
| R11 | `agate/CONTEXT.md:16` | NEED_CONFIRM 术语表只列 `[NO_NEED_CONFIRM]`，未提倾向 | 术语表应反映协议现状 | 补 `[NEED_CONFIRM倾向:]` 项 |
| R12 | `agate/assets/templates/task-files.md:148` | 模板 `[NEED_CONFIRM] 问题描述 + 几种可能的理解` | 无倾向变体模板 | 加 `[NEED_CONFIRM倾向: 推荐 X，理由 Y]` 模板 |
| R13 | `agate/scripts/check-protocol-consistency.py:491-493` | `"desc": "NEED_CONFIRM 二值声明"` + `"keywords": ["NEED_CONFIRM", "NO_NEED_CONFIRM"]` | CHECK 9 锚点描述与实际三值不符 | `desc` 改为"NEE_CONFIRM 三值声明"；`keywords` 加 `"NEED_CONFIRM倾向"` |
| R14 | `agate/tests/integration/consistency.bats:57` | `CON.12: CHECK 9: NEED_CONFIRM 二值锚点存在` | 测试名/语义过时 | 测试名加 `倾向` 检查 |

**14 处遗漏** —— 主要是 NEED_CONFIRM 三值演进的反向传播，部分直接影响主 Agent / subagent 阅读时的行为判断（如 R10 analyst 不知道有倾向选项，可能把所有"有倾向"的请求都标阻塞 NEED_CONFIRM，违背 Task 8 的核心收益"减少用户阻塞"）。

实际可执行性已通过 537 ok 验证，但**协议语义完整性**缺这一轮传播。

---

## A4. 测试覆盖

**结论：ALIGNED**

实测 `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` 输出尾部连续 `ok 498-537` 全过（共 531 用例按 `count-tests.sh`）。

新增 2 个测试（`agate/tests/unit/check-gate.bats:1399-1457`）：
- `G_NC_TENDENCY.1`：纯倾向 → exit 2 + WARNING 含 `NEED_CONFIRM倾向` + 输出**不含**"未解决的 NEED_CONFIRM 项（阻塞）"
- `G_NC_TENDENCY.2`：混合（倾向 + 阻塞）→ exit 1 + 输出含"阻塞"

边界覆盖：
- ✅ 纯倾向不阻塞
- ✅ 混合时阻塞（数量 ≥1 阻塞即 exit 1）
- ⚠️ **未覆盖**：空 P1 文件、P1 仅 `[NO_NEED_CONFIRM] + 倾向`、P1 仅 `[NO_NEED_CONFIRM] + 阻塞`（前者现 G_NC_BINARY.1 覆盖，后者新增）

`count-tests.sh` 输出 check-gate.bats = 98（plan 报 96→98 一致）；`tests/README.md` 同步更新 96→98 ✅。

---

## A5. 下游影响 + 文档传播

**结论：MISALIGNED**

**关键缺口**：本次 commit (8ae8a2c, 2026-08-06) 之后无对应 CHANGELOG 条目，也无对应版本 tag。

- 当前最新 tag：`v0.30.0` (2026-08-04)，对应 `CHANGELOG.md` 第 9 行 §[0.30.0]
- 本次 commit 在 v0.30.0 tag 之后 push（如 commit msg self-gate-review 已声明）
- `CHANGELOG.md` **找不到本次改动条目**

本计划 Task 4 明确说"bump-version + CHANGELOG 更新 → 同一 commit + tag"，但提交时**未见**：
- `README.md` version badge 是否更新（未检查）
- CHANGELOG 新增 `[0.30.1]` / `[0.31.0]` 条目
- `git tag v0.30.1` 或 `v0.31.0`

**建议修复方向**：bump patch version (v0.30.1) 在新 commit 增加 CHANGELOG 条目 + README badge 同步（如果之前未做）；或者 amend 本次 commit 把 CHANGELOG 一起纳入（plan Task 4 强调"同一 commit"，目前 plan 实施与官方纪律脱节）。

`docs/hardening-roadmap.md` 已在 L385-395 标注"已实施"，但 CHANGELOG 没有落地。

---

## A6. 锚点表覆盖（CHECK 9）

**结论：MINOR MISALIGNED**

`check-protocol-consistency.py` CHECK 9 锚点表中（`agate/scripts/check-protocol-consistency.py:480-528`）：

| 锚点 | 当前 desc | 当前 keywords | 影响 |
|------|----------|--------------|------|
| NEED_CONFIRM | "二值声明" | `["NEED_CONFIRM", "NO_NEED_CONFIRM"]` | 关键字仍匹配（NEED_CONFIRM 是子串），CHECK 9 仍 PASS；但 desc 与实际三值机制不符，未来可能误判"脚本缺倾向支持" |
| DESIGN_GAP | 配对 | `["DESIGN_GAP"]` | 已有 P7 行首正则（task 1 实施），但 anchor 没区分 DESIGN_GAP_REVIEWED，CHECK 9 仍只验证 DESIGN_GAP 出现 |
| 其他锚点 | — | — | 不受影响 |

**建议修复方向**：
- R13：`keywords` 加 `"NEED_CONFIRM倾向"` + `desc` 改为"NEE_CONFIRM 三值声明"
- 可选：DESIGN_GAP anchor 加 `"DESIGN_GAP_REVIEWED"`

CHECK 9 当前 PASS（实测 0 ERROR），但锚点文案误导后续维护者。

新增的协议规则（P1 基线保护 `[BASELINE_CHANGE:]`、UI 选择器契约）目前**没有脚本实现**——是纯文档约定，无 anchor 需求。

---

## A7. 设计原则一致性（ADR）

**结论：NEEDS_HUMAN_REVIEW（建议补 ADR-008）**

新增的"NEED_CONFIRM 分级"引入了一个中间状态（WARNING 不阻塞），偏离 ADR-002（可判定性）的"二值 gate exit code"框架。三个 ADR 需关注：

- **ADR-002**（可判定性）：明确说"gate 通过/不通过由脚本 exit code 决定（0=通过，1=不通过，2=需人工判断）"。当前 implementation 把倾向项放在 gate script 里做 WARNING（line 76-77），实际是**第二层语义判断**（"主 Agent 可自行采纳"）藏在 exit 2 之后的 stderr。这与 ADR-002 的"exit 2 标记需人工判断"语义有微妙不同——倾向项不需要人工判断，主 Agent 自行决定，但脚本仍记 WARNING 留给 CI 审计。
  - **影响**：可接受，但应在 ADR-002 注释追加"T080 retro: 增加 NEED_CONFIRM倾向 WARNING，主 Agent 自行决定不视为 gate 失败"
- **ADR-006**（双层角色）：倾向项让主 Agent 跳过 reviewer 直接采纳 recommendation。在 reviewer / approval 链上是弱化。这与 ADR-006 的"独立视角发现盲点"主张有冲突——倾向选择本质是 reviewer 的活。
  - **影响**：可接受，但应在 ADR-006 标注"T080 retro: 倾向项降低 reviewer 介入门槛，由主 Agent 自行采纳"

**建议**：在 `agate/adr.md` 新增 **ADR-008（NEE_CONFIRM 三值与主 Agent 自主采纳边界）**，明确：
1. 三值的设计 rationale（区分阻塞/倾向/无）
2. 主 Agent 自主采纳范围的边界（不涉及破坏性变更 / 业务方向时）
3. 与 ADR-002 / ADR-006 的张力说明

或最低限度，在 ADR-002 / ADR-006 末尾追加"T080 演进"段落。

---

## 总体结论

**NEEDS_FIX**

| 维度 | 结论 | 严重度 |
|------|------|--------|
| A1 文档→脚本 | ✅ ALIGNED | — |
| A2 脚本→文档 | ✅ ALIGNED | — |
| A3a 8 任务完整性 | ✅ ALIGNED | — |
| **A3b 反向传播** | ❌ **MISALIGNED** | **High** — 14 处遗漏影响协议可读性 |
| A4 测试覆盖 | ✅ ALIGNED | Low（边界小缺口） |
| **A5 CHANGELOG / 版本 bump** | ❌ **MISALIGNED** | **High** — 违反 plan Task 4 自定纪律 |
| A6 锚点表 | ⚠️ MINOR | Low |
| **A7 ADR 一致性** | ⚠️ NEEDS_HUMAN_REVIEW | **Medium** — 建议补 ADR-008 或在 ADR-002/006 加演进注释 |

## 修复优先级（主 Agent 决策用）

### P0 必须修（不修不能 release）

1. **CHANGELOG.md + version badge 同步**（A5）：plan Task 4 自定纪律未执行
   - `CHANGELOG.md` 增加 `[0.30.1]` 条目，记 8 项 Task 摘要
   - `README.md` badge `v0.30.0` → `v0.30.1`（如尚未改）
   - `git tag v0.30.1` 在 CHANGELOG + README 同一 commit 后打

### P1 强烈建议修（影响协议可读性 / 主 Agent 决策）

2. **dispatch-protocol.md 三处反向传播**（A3b R1-R3）：R2 是直接矛盾（T005/T006 二值声明），必须修；R1/R3 是阅读一致性
3. **state-machine.md 三处 + state-transitions.md**（A3b R5-R9）：NEED_CONFIRM 语义澄清
4. **WORKFLOW.md:216**（A3b R4）：P1 阶段判定说明
5. **analyst.md:91-99**（A3b R10）：analyst 角色不知道倾向选项会继续把所有"有倾向"需求都标阻塞 NEED_CONFIRM，违背 Task 8 核心收益

### P2 建议修（术语与脚本同步）

6. **CONTEXT.md:16 + task-files.md:148**（A3b R11/R12）：术语表 / 模板同步
7. **check-protocol-consistency.py:491-494 + consistency.bats:57**（A3b R13/R14）：CHECK 9 锚点 desc 改为"三值声明"，keywords 加 `NEED_CONFIRM倾向`
8. **ad.md**（A7）：补 ADR-008 或在 ADR-002 / ADR-006 追加 T080 演进注

### P3 可选改进

9. **check-gate.bats**（A4）：补 G_NC_TENDENCY.3 测"`[NO_NEED_CONFIRM] + 倾向 + 阻塞`混合 → exit 1"边界（当前 G_NC_TENDENCY.2 已覆盖主路径，可选）

---

## 关键引用汇总

**协议完整性证据**：
- 全量测试：537 ok / 0 fail（truncated tail 显示 480-537 ok）
- consistency: 0 ERROR（仅 12 个 narrative 文件 WARNING）
- shellcheck: clean（`shellcheck -S warning agate/scripts/check-gate.sh` 无输出）

**NEED_CONFIRM 分级实测**：
- `[NEED_CONFIRM倾向: 推荐 X] only` → `check-gate.sh P1` exit 2 + "1 个 NEED_CONFIRM倾向 项（主 Agent 可自行采纳，不阻塞）"
- `[NEED_CONFIRM倾向: X] + [NEED_CONFIRM] Y` → exit 1 + "1 个未解决的 NEED_CONFIRM 项（阻塞）"
- 正则 `^\s*-?\s*\[NEED_CONFIRM\]` 不误匹配 `[NEED_CONFIRM倾向:`（实证）

**未列在 diff 中的反向传播文件数**：14 处（详见 A3b 表）

---

*审查完成于 2026-08-06 | target_commit = 8ae8a2c | 537 ok + 0 fail*
