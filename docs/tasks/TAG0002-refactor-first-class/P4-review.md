---
phase: P4
task_id: TAG0002-refactor-first-class
type: review
parent: P4-implementation.md
trace_id: TAG0002-P4-20260812
status: approved
created: 2026-08-12
agent: review
---

# TAG0002 — P4 实现评审（第 3 轮复审：R1/R2 闭环确认）

> 评审角色：偏执 Staff Engineer（review）。评审对象：worktree `agate/` 的 refactor 机制改动（TAG0002-P4，未 commit）。本轮为第 3 轮复审——R1（change_type 正文回退误判）与 R2（两处文档残留）均已由 implementer 修复并同步。
> 评审依据：P2-design.md（方案 A 基线）+ P4-implementation.md（实现记录）+ P1-requirements.md（8 条 BDD）+ P3-test-cases.md（契约）+ 实际代码逐文件查证 + 关键 bats 复跑。
> 结论：**approved** —— R1 BLOCKER 代码层闭环、R2 两处文档残留已同步，无剩余 BLOCKER / CRITICAL。

---

## 1. 结论摘要

**R1 BLOCKER（change_type 正文回退误判缺省任务）代码层闭环，验证通过：**

- `change_type` 在 `NO_FALLBACK_STRING_FIELDS`（agate-md-field-get.py:78），`_get` 对 NO_FALLBACK 系列字段在 frontmatter 无该字段时直接 `return ""`（agate-md-field-get.py:188-190），`_regex_fallback` 无 change_type 分支（agate-md-field-get.py:164-180），`STRING_FIELDS` 注释明确 change_type 不在其中（agate-md-field-get.py:107）——frontmatter-only，正文散文提及不会误判（BDD-2）。
- 消费方单一通道确认：check-gate.sh P6 分流（check-gate.sh:300-310）与 ci-gate-backstop.py P3 分支（ci-gate-backstop.py:141-144，`_read_p1_change_type` 在 :76-98）均复用同一 md-field-get 通道，缺省任务返回空字符串不会误入 refactor 分支。
- 回归用例覆盖该场景（MDF.8/MDF.11/MDF.12 正文提及→空、test_bdd_2b P6 不误拦、backstop P3 不误跳），全部真实且绿。

**R2 文档残留已同步，验证通过：**

- P2-design.md:122：已改为"新增 `change_type` op（NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——change_type 是新增 P1 机器字段，正文旧格式从未有该字段，无向后兼容需求；正文散文提及 change_type 不得误判为 refactor（BDD-2））"。
- P4-implementation.md:24：已改为"新增 `change_type`（NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——P4-review §2.1 BLOCKER 修复）；新增 `regression_pass`（NO_FALLBACK_BOOL_FIELDS，无正文回退，防伪造陷阱 MDF.10）"。
- 两处描述现与落地代码（agate-md-field-get.py:78）一致，实现记录与代码无矛盾，P7 一致性交叉检查不会误报。

**无剩余 BLOCKER / CRITICAL。** 关键 bats 复跑：agate-md-field-get.bats 12/12、check-gate.bats 111/111 全绿。

---

## 2. R1 BLOCKER 闭环验证（第 3 轮再确认）

锚点（全部 grep / read 实证）：

- agate/scripts/agate-md-field-get.py:78 — `NO_FALLBACK_STRING_FIELDS = frozenset({"change_type"})`
- agate/scripts/agate-md-field-get.py:72-77 — 模块注释明确"frontmatter-only，无正文回退"及 BDD-2 理由（正文散文提及不得误判）
- agate/scripts/agate-md-field-get.py:188-190 — `_get` no-fallback 判定并入 NO_FALLBACK_STRING_FIELDS，frontmatter 无该字段直接 `return ""`
- agate/scripts/agate-md-field-get.py:107 — `STRING_FIELDS` 注释"change_type 不在其中——它走 NO_FALLBACK_STRING_FIELDS"
- agate/scripts/agate-md-field-get.py:164-180 — `_regex_fallback` 无 change_type 分支（对比 risk_level :165-166 有回退分支，证明"与 risk_level 同模式"旧描述已彻底清除）
- agate/scripts/check-gate.sh:300-310 — P6 分流：`CHANGE_TYPE` 为空短路直落既有 L312-336 判定（逐字节保留）
- agate/scripts/ci-gate-backstop.py:141-144 — `is_refactor = _read_p1_change_type(task_dir) == "refactor"` → SKIP；缺省返回空 → 不误跳
- agate/scripts/agate-frontmatter-check.py:37/40/51 — P1 schema `change_type` 入 migrated_keys / enums `("refactor",)` / types `str`，不入 required（:39）
- agate/scripts/agate-frontmatter-check.py:68/75 — P6 schema `regression_pass` 入 migrated_keys / types `bool`，不入 required（:69）

回归用例核验（bats 复跑）：

| 用例 | 断言 | 复跑结果 |
|---|---|---|
| MDF.8（改契约） | frontmatter 无 change_type 时正文行不读取 | ok |
| MDF.11 / MDF.12 | 功能任务正文散文/否定式提及 → 输出空（BDD-2） | ok ×2 |
| MDF.9 / MDF.10 | regression_pass frontmatter 读取 true / 无字段输出空（无正文回退） | ok ×2 |
| test_bdd_1 | P1 gate 接受 change_type: refactor 声明（BDD-1） | ok |
| test_bdd_2b | 仅正文散文提及 → P6 仍走功能口径 exit 2，不误拦 | ok |
| test_bdd_3 | refactor + regression_pass + regression.log + 关键路径 PASS → exit 2（BDD-3/7） | ok |
| test_bdd_4 / 4b | regression.log 缺失 / regression_pass 未声明 → exit 1（BDD-4） | ok ×2 |
| backstop P3 refactor | change_type=refactor 跳过 check-tdd-red（SKIP 非 FAIL，mock exit 2 绿灯） | ok |

---

## 3. R2 文档残留同步验证（第 3 轮核心）

**两处残留均已同步为 frontmatter-only 描述，与代码一致：**

- P2-design.md:122 — 原文 `STRING_FIELDS ... 可选正文正则回退 ... 与 risk_level 同模式` 已替换为 `NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退` + BDD-2 理由。与代码、与 P4-implementation.md、与修复记录三方一致。
- P4-implementation.md:24 — 原文 `STRING_FIELDS + 正文正则回退，与 risk_level 同模式` 已替换为 `NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——P4-review §2.1 BLOCKER 修复`；同单元格 regression_pass 亦为 `NO_FALLBACK_BOOL_FIELDS，无正文回退`。实现记录现如实反映落地代码。

其余文档口径一致性抽查（全部与 P2 设计一致，change_type 均表述为 P1 frontmatter 声明、无正文回退）：

- agate/phase-cards/P6-acceptance.md:5,87-112 — refactor 换口径非裁 P6 + 三段式 + regression_pass frontmatter 样例 + 双证硬校验 + 禁止伪造功能 BDD + BDD 编号不豁免 + no_behavior_change 不豁免
- agate/phase-cards/P3-tdd.md:17-25 — refactor 回归测试口径 + 跳过 TDD 红灯 + P3 gate 不变
- agate/phase-cards/P1-requirements.md:68-69 — frontmatter 样例可选 change_type 注释行
- agate/WORKFLOW.md:201 — 换口径 ≠ 裁 P6
- agate/state-machine.md:174 — 裁剪条件 P6 同步补说明
- agate/dispatch-protocol.md:536-538（P3 派发追加）、:595-601（P6 派发追加）
- agate/assets/execution-roles/verifier.md:126-135 — P6 refactor 验收口径
- agate/assets/execution-roles/test-designer.md:45-52 — P3 refactor 回归设计

---

## 4. Pass 1 — 数据安全与正确性复核（不重复第 2 节已验项）

- **refactor 分支双证硬校验不可绕过**（check-gate.sh:304-310）：`REGRESSION_PASS != "true"` 或 `P6-evidence/regression.log` 不存在 → exit 1，独立于关键路径 FAIL 判定；`2>/dev/null || echo ""` 兜底防 md-field-get 异常崩溃导致误放行（异常时 REGRESSION_PASS 为空 ≠ "true" → 拦截，安全侧）。P6_FILE 为固定拼接 `$TASK_DIR/P6-acceptance.md`，无注入面。
- **缺省路径逐字节保留**（check-gate.sh:311-336）：分流为纯增量前置分支，`CHANGE_TYPE=""` 时 if 不进，直落既有判定；对比 git diff 确认既有 L312-336 未动。
- **schema 非必填语义正确**：change_type 不入 P1 required、regression_pass 不入 P6 required；条件性必填由 gate 层强制（文件级 schema 校验器无法表达跨字段条件，设计取舍正确）。
- **backstop refactor 感知健壮性**（ci-gate-backstop.py:81-98）：P1 文件缺失/脚本缺失/subprocess 异常/超时均静默返回空 → 缺省视为功能任务，不误伤非 refactor 任务。

---

## 5. Pass 2 — 代码健康

- check-gate.sh `set -euo pipefail` 既有，改动未破坏；`grep -c || echo 0 | tail -1` 约定保留。
- python 三文件无语法/引用错误（bats 全绿佐证）；`_get` 的 no-fallback 集合并集写法（agate-md-field-get.py:188-189）清晰。
- shellcheck：P4-implementation.md §2 声明 `shellcheck -S warning agate/scripts/check-gate.sh` 0 error（上轮实测一致）。
- 无新观察点。

---

## 6. 缺省行为不变回归（BDD-2）

- 本轮复跑：`bats agate/tests/unit/agate-md-field-get.bats` → **12/12 ok**；`bats agate/tests/unit/check-gate.bats` → **111/111 ok，0 not ok**（含 P6 既有基线 + refactor 新增分流用例 + 回退检测用例）。
- implementer 记录：全量 `sanity + unit + regression + integration` → 650/650（631 基线 + 19 新增）0 not ok；consistency 0 ERROR；count-tests 644（unit/regression/integration，不含 sanity）。
- R1/R2 两轮修复均未触碰缺省路径判定逻辑（分流为前置短路），缺省任务行为与改造前一致。

---

## 7. SCOPE_GAP 审查（保持上轮结论）

- P4-implementation.md §3 声明：`docs/plans/agate-test-plan-2026-07-01.md` 已归档至 `docs/archived/plans/`（check-protocol-consistency.py:108 跳过 archived/），count-tests.sh 仅 informational 非 gate 阻断。声明属实、合理，未改动归档文件。

---

## 8. 检查清单

| 项 | 结果 |
|---|---|
| R1 BLOCKER 闭环（change_type frontmatter-only） | 闭环（代码 + bats 复跑 + 消费方单一通道） |
| R2 文档残留同步（P2-design.md:122 + P4-implementation.md:24） | 已同步（与代码三方一致） |
| Pass 1 分流/CI/schema | 通过 |
| Pass 2 代码健康 | 通过 |
| 缺省行为不变（BDD-2） | 通过（关键 bats 12/12 + 111/111，全量 650/650） |
| 文档一致性 | 通过（卡片/角色/WORKFLOW/state-machine/dispatch 全部一致） |
| SCOPE_GAP | 合理 |

---

## 9. 结论

**Status: approved**

R1 BLOCKER（change_type 正文回退误判）已在代码层闭环并验证：frontmatter-only 读取通道 + 消费方单一通道 + 场景化回归用例（MDF.8/11/12、test_bdd_2b、backstop）全部真实且绿。R2 两处文档残留（P2-design.md:122、P4-implementation.md:24）已同步为 frontmatter-only 描述，与落地代码一致，无剩余矛盾。

无 BLOCKER / CRITICAL，无需再迭代。可推进 P5 验证（gate_commands.P5 全量回归 + consistency + shellcheck 已由 implementer 自查，P5 阶段按 gate 复跑确认）。
