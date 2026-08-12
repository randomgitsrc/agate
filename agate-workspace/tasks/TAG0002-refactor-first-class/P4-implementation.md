---
phase: P4
task_id: TAG0002-refactor-first-class
type: implementation
parent: P2-design.md
trace_id: TAG0002-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0002 — 重构一等任务（Phase A）：P4 实现记录

> 本任务是 agate 协议自身改造（dogfooding）。只改 worktree `agate/`，未触碰 `~/.agate`（稳定版 v0.40.2 开发工具）。
> 实现严格按 P2-design.md 方案 A（change_type 入 P1 frontmatter + P6 gate 分流回归口径 + P3 refactor 跳过 TDD 红灯）。
> implementation_dir: agate/（协议文件原位写入 worktree agate/ 下）

## 1. 改动清单（P2 §1.1 逐项落实）

### 1.1 脚本层（4 处核心）

| 文件 | 改动 | 落点 |
|---|---|---|
| `agate/scripts/agate-md-field-get.py` | 新增 `change_type`（NO_FALLBACK_STRING_FIELDS，frontmatter-only，无正文回退——P4-review §2.1 BLOCKER 修复）；新增 `regression_pass`（NO_FALLBACK_BOOL_FIELDS，无正文回退，防伪造陷阱 MDF.10） | 字段集 + _regex_fallback + _get 无回退判定 + KNOWN_OPS |
| `agate/scripts/agate-frontmatter-check.py` | P1 schema：migrated_keys/types 增 `change_type`（str）、enums 增 `("refactor",)`（不 required）；P6 schema：migrated_keys/types 增 `regression_pass`（bool，不 required） | SCHEMAS["P1-requirements.md"] / SCHEMAS["P6-acceptance.md"] |
| `agate/scripts/check-gate.sh` | P6 分支（L292 之后、既有判定之前）新增 change_type 分流前置分支：refactor → 硬校验 regression_pass==true + P6-evidence/regression.log 存在，任一缺失 exit 1；缺省短路直落既有判定 | L297-310（纯增量前置分支，既有 L312-336 判定逐字节保留） |
| `agate/scripts/ci-gate-backstop.py` | P3 分支 refactor 感知（[SCOPE+]）：change_type=refactor 时跳过 check-tdd-red 并输出 SKIP（避免 exit 2 绿灯被误判 FAIL）；新增 `_read_p1_change_type()` helper 复用 agate-md-field-get.py 通道 | main() P3 分支开头 + helper 函数 |

### 1.2 卡片层（3 张）

| 文件 | 改动 |
|---|---|
| `agate/phase-cards/P1-requirements.md` | frontmatter 完整样例（L49-72）新增可选 `change_type: refactor` 注释行（取值 + 缺省=功能任务说明） |
| `agate/phase-cards/P3-tdd.md` | 新增「refactor 任务：回归测试口径」节（回归口径 + 跳过 check-tdd-red 红灯 + P3 gate 不变） |
| `agate/phase-cards/P6-acceptance.md` | 顶部裁剪说明补 refactor 换口径非裁 P6；产出规格新增「P6-acceptance.md（refactor 任务：回归验收口径）」节（三段式 + regression_pass frontmatter 样例 + 回归双证硬校验 + 禁止伪造功能 BDD + BDD 编号不豁免 + no_behavior_change 不豁免） |

### 1.3 协议文档层（5 处可发现性同步，P2 §3.5）

| 文件 | 改动 |
|---|---|
| `agate/WORKFLOW.md` | P6 不可裁剪表述处补「change_type: refactor 换用回归口径（换口径 ≠ 裁 P6）」 |
| `agate/state-machine.md` | 裁剪条件 P6 条目同步补 refactor 换口径说明 |
| `agate/dispatch-protocol.md` | P3 派发追加节补 refactor 回归测试口径；P5/P6 派发追加节补 refactor 三段式回归验收口径 |
| `agate/assets/execution-roles/verifier.md` | 新增「refactor 任务验收口径（P6 模式）」节（三段式 + regression.log + EXIT_CODE: 0 + 双证硬校验 + 禁止伪造功能 BDD + no_behavior_change 不豁免） |
| `agate/assets/execution-roles/test-designer.md` | 新增「refactor 任务：回归测试设计（P3 模式）」节（回归口径 + 不跑 TDD 红灯 + BDD 为关键路径行为不变断言） |

## 2. 自查结果（P4 自查 ≠ P5 gate）

| 检查 | 命令 | 结果 |
|---|---|---|
| P3 目标测试 4 文件 | `bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-md-field-get.bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/ci-gate-backstop.bats` | 143/143 通过（110+10+14+9），0 not ok |
| 全量回归（缺省行为不变验证） | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | 650/650 通过（631 基线 + 19 新增），0 not ok |
| shellcheck | `shellcheck -S warning agate/scripts/check-gate.sh` | 0 error |
| 协议一致性 | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR（全部检查 PASS） |
| 用例计数漂移 | `bash agate/tests/scripts/count-tests.sh` | 总计 644（unit/regression/integration，不含 sanity 6） |

## 3. DESIGN_GAP / SCOPE+ / SCOPE_GAP 声明

```
[SCOPE_GAP] P2-design.md §1.1 声明"docs/plans/agate-test-plan-2026-07-01.md 附录 A 测试用例数漂移同步"，
            但该文件已归档至 docs/archived/plans/（脱离一致性检查扫描范围，check-protocol-consistency.py
            L108 跳过 archived/ 路径）。count-tests.sh 仅输出 informational 提示（非 gate 阻断），
            新增 19 用例后计数 644（unit/regression/integration 不含 sanity 6）与既有漂移机制一致，
            未改动归档文件。
```

无 DESIGN_GAP（P2 方案在实现中未发现歧义/缺口，实现严格按 §3.1-§3.5 落地）。

## 4. 关键实现说明

- **缺省行为不变（BDD-2）**：check-gate.sh P6 分流为纯增量前置分支，`CHANGE_TYPE=""` 时短路跳过，直落既有 L312-336 判定逻辑（逐字节保留）。全量 650 用例回归验证缺省路径不受影响。
- **BDD-4 双证硬校验**：refactor 分支 `REGRESSION_PASS != "true"` 或 regression.log 缺失 → exit 1，独立于关键路径 FAIL 判定。
- **ci-gate-backstop refactor 感知（SCOPE+）**：P3 分支先读 P1 change_type，refactor → 打印 `SKIP: refactor 任务，TDD 红灯不适用（回归口径由 P5/P6 全量回归兜底）` 并 return 0（不跑 check-tdd-red）。
- **check-p6-*.sh 六道审计未改动**：regression.log 复用既有 EXIT_CODE: 0 约定（审计 5）与被 PASS 行引用要求（审计 1c），refactor 证据与功能任务同构，无需改审计脚本（P2 §1.2 边界）。
