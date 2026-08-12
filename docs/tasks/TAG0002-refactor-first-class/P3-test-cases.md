---
phase: P3
task_id: TAG0002-refactor-first-class
type: test-cases
parent: P2-design.md
trace_id: TAG0002-P3-20260812
status: draft
created: 2026-08-12
agent: test-designer
---

# TAG0002 — 重构一等任务（Phase A）：P3 测试用例清单（回归测试口径）

> 本任务 P3 为 **refactor 机制** 的测试设计：验证"重构一等任务"新机制（change_type 字段 + P6 回归口径分流）**存在且行为正确**。不新增 agate 功能行为断言（回归口径约束）。refactor 语义下不要求 TDD 红灯——新机制未实现时新用例失败属预期（见 §4 自跑结果），P4 实现后转绿。
>
> 角色：test-designer（本任务是**功能型任务**自身，但 P3 测试设计按派发指引走回归测试口径——测试验证对象是新机制本身，不是新增业务行为）。

## 1. 基本信息

- **test_code_dir**: `agate/tests/`
- **gate_commands.P3 落点**：`bats agate/tests/unit/check-gate.bats`（P2 gate_commands 固化）+ 相关新增测试文件（agate-md-field-get.bats / check-frontmatter.bats / ci-gate-backstop.bats）
- **上游**：P2-design.md §3.1（change_type 字段）/ §3.2（P6 回归口径三段式）/ §3.3（check-gate.sh P6 分流）/ §3.4（P3 回归口径 + ci-gate-backstop refactor 感知）
- **参考现有测试结构**：G6.* P6 用例模式（check-gate.bats:706-778）、CF.* schema 用例（check-frontmatter.bats）、MDF.* field-get 用例（agate-md-field-get.bats）、backstop P3 用例（ci-gate-backstop.bats）

## 2. BDD → 测试 1:1 映射

| BDD | 验收条件摘要 | 测试用例（test_code_dir 内） | 文件 |
|---|---|---|---|
| BDD-1 | P1 可声明 change_type: refactor 且被协议认可 | `test_bdd_1_p1_gate_accepts_change_type_refactor`（P1 gate exit 2 不因字段报错）+ `MDF.7`（change_type frontmatter 读取）+ `MDF.8`（change_type 正文回退）+ `CF.11`（change_type 枚举合法）+ `CF.12`（枚举非法值拦截并提示 refactor） | check-gate.bats / agate-md-field-get.bats / check-frontmatter.bats |
| BDD-2 | 未声明 change_type 验收行为与改造前一致 | `test_bdd_2_p6_gate_default_no_change_type_unchanged`（缺省 P6 走既有功能口径 exit 2） | check-gate.bats |
| BDD-3 | refactor 按回归口径验收，无需伪造功能 BDD 即通过 | `test_bdd_3_p6_gate_refactor_with_regression_evidence`（refactor + regression_pass:true + regression.log + 关键路径 PASS → exit 2） | check-gate.bats |
| BDD-4 | 回归未全绿 → 验收不通过（硬性组成） | `test_bdd_4_p6_gate_refactor_missing_regression_log`（缺 regression.log → exit 1）+ `test_bdd_4b_p6_gate_refactor_missing_regression_pass`（缺 regression_pass:true → exit 1）+ `MDF.9`（regression_pass 读取）+ `MDF.10`（regression_pass 无正文回退）+ `CF.13`（regression_pass bool 类型校验）+ `CF.14`（bool 合法） | check-gate.bats / agate-md-field-get.bats / check-frontmatter.bats |
| BDD-5 | 口径文档明确禁止伪造功能 BDD | `test_bdd_5_p6_card_docs_forbid_fake_functional_bdd`（P6-acceptance.md 卡片含"禁止…伪造…"表述，文档锚点） | check-gate.bats |
| BDD-6 | refactor 独立于 no_behavior_change | `test_bdd_6_p6_gate_refactor_no_behavior_change_not_waived`（声明 no_behavior_change 仍缺回归双证 → exit 1）+ `test_bdd_6b_p6_gate_refactor_no_behavior_change_with_evidence`（no_behavior_change + 双证齐备 → exit 2） | check-gate.bats |
| BDD-7 | 真实重构回填走 P1-P6 全程 gate 通过 | `test_bdd_7_refactor_backfill_walk_p1_p3_p6`（fixture 建模 c182dc3：P1→P3→P6 三处 gate 全 exit 2，无功能 BDD） | check-gate.bats |
| BDD-8 | P3 测试设计为回归测试口径，卡片/派发含说明 | `test_bdd_8_p3_card_docs_regression_test_port`（P3-tdd.md 卡片含"回归测试口径"表述，文档锚点）+ `backstop P3: change_type=refactor 任务跳过 check-tdd-red`（[SCOPE+] ci-gate-backstop refactor 感知，避免绿灯误杀） | check-gate.bats / ci-gate-backstop.bats |

**映射口径说明（回归测试）**：每条 BDD 至少一个测试，测试名引用 BDD 编号（`test_bdd_N_...`）。测试断言的是"新机制存在且行为正确"（分流/字段/文档锚点），**不新增任何 agate 功能行为断言**——refactor 任务无新行为可断言（P1 §2.3 / P2 §3.4）。

## 3. 测试用例明细（19 条新增，4 文件）

### 3.1 `agate/tests/unit/check-gate.bats`（+10）

check-gate.sh P6 分支 change_type 分流（P2 §3.3）——缺省短路走既有判定（BDD-2），refactor 硬校验回归双证（BDD-3/4/6），回填 walk（BDD-7），文档锚点（BDD-5/8）：

| 用例 | 断言 | 当前（P4 前）状态 |
|---|---|---|
| `test_bdd_1_p1_gate_accepts_change_type_refactor` | P1 gate exit 2 且输出不含 change_type | 绿（锁定） |
| `test_bdd_2_p6_gate_default_no_change_type_unchanged` | 缺省 P6 exit 2（既有口径） | 绿（锁定） |
| `test_bdd_3_p6_gate_refactor_with_regression_evidence` | refactor 双证齐备 exit 2 | 绿（锁定） |
| `test_bdd_4_p6_gate_refactor_missing_regression_log` | 缺 regression.log → exit 1 | **红**（分流未实现，实为 exit 2） |
| `test_bdd_4b_p6_gate_refactor_missing_regression_pass` | 缺 regression_pass → exit 1 | **红**（同上） |
| `test_bdd_6_p6_gate_refactor_no_behavior_change_not_waived` | no_behavior_change 不豁免回归 → exit 1 | **红**（同上） |
| `test_bdd_6b_p6_gate_refactor_no_behavior_change_with_evidence` | no_behavior_change + 双证 exit 2 | 绿（锁定） |
| `test_bdd_7_refactor_backfill_walk_p1_p3_p6` | P1/P3/P6 三 gate 全 exit 2 | 绿（锁定） |
| `test_bdd_5_p6_card_docs_forbid_fake_functional_bdd` | P6 卡片含"禁止…伪造…" | **红**（卡片未更新） |
| `test_bdd_8_p3_card_docs_regression_test_port` | P3 卡片含"回归测试口径" | **红**（卡片未更新） |

### 3.2 `agate/tests/unit/agate-md-field-get.bats`（+4）

新 op 读取（P2 §3.1.3 机器通道）：`change_type` 入 STRING_FIELDS（正文正则回退，与 risk_level 同模式）；`regression_pass` 为 bool 无正文回退（防止正文伪造陷阱）：

| 用例 | 断言 | 当前状态 |
|---|---|---|
| `MDF.7` change_type frontmatter 读取 | 输出 `refactor` | **红**（unknown op，exit 2） |
| `MDF.8` change_type 正文正则回退 | 输出 `refactor` | **红**（同上） |
| `MDF.9` regression_pass frontmatter 读取 | 输出 `true` | **红**（同上） |
| `MDF.10` regression_pass 无正文回退 | 输出空（正文 `regression_pass: false` 陷阱行不被读到） | **红**（同上） |

### 3.3 `agate/tests/unit/check-frontmatter.bats`（+4）

frontmatter schema 同步（P2 §3.1.1/§3.2.2）：P1 `change_type` 枚举 `{refactor}`；P6 `regression_pass` bool：

| 用例 | 断言 | 当前状态 |
|---|---|---|
| `CF.11` change_type: refactor（合法枚举） | 校验通过（exit 0、输出空） | 绿（锁定） |
| `CF.12` change_type: feature（枚举外） | 校验失败且输出含 change_type + refactor | **红**（schema 未加枚举） |
| `CF.13` regression_pass: "yes"（非 bool） | 校验失败且输出含 regression_pass | **红**（schema 未加类型） |
| `CF.14` regression_pass: true（合法 bool） | 校验通过（exit 0、输出空） | 绿（锁定） |

### 3.4 `agate/tests/unit/ci-gate-backstop.bats`（+1，[SCOPE+]）

P3 分支 refactor 感知（P2 §3.4）：change_type=refactor 任务跳过 check-tdd-red，避免绿灯误杀（BDD-7/8 机制完整性）：

| 用例 | 断言 | 当前状态 |
|---|---|---|
| `backstop P3: change_type=refactor 任务跳过 check-tdd-red` | mock tdd-red exit 2 仍输出 SKIP + refactor 且不含 FAIL | **红**（backstop 未 refactor 感知） |

## 4. 自跑结果（refactor 语义，2026-08-12）

- 命令：`bats agate/tests/unit/check-gate.bats`（110 用例，5 红）、`bats agate/tests/unit/agate-md-field-get.bats`（10 用例，4 红）、`bats agate/tests/unit/check-frontmatter.bats`（14 用例，2 红）、`bats agate/tests/unit/ci-gate-backstop.bats`（9 用例，1 红）
- **合计 143 用例，12 红，全部失败原因 = "被测逻辑未实现"**（合规，refactor 任务不要求 TDD 红灯）：
  - check-gate.sh P6 change_type 分流未实现 → BDD-4/4b/6 期望 exit 1 实际 exit 2（缺省路径）
  - agate-md-field-get.py 无 change_type / regression_pass op → `unknown op` exit 2
  - agate-frontmatter-check.py schema 未加 change_type 枚举 / regression_pass bool → 输出空
  - P6/P3 卡片未写 refactor 口径 → doc-grep 无匹配
  - ci-gate-backstop.py P3 分支未 refactor 感知 → 无 SKIP
- **无失败是"断言与测试数据矛盾"**（非测试代码 bug）。
- 既有用例全部保持绿（check-gate.bats 105/105、md-field-get 6/6、frontmatter 12/12、backstop 8/8）——新增用例不破坏基线。
- 输出可被 `bats --formatter tap` 解析（已验证）。

## 5. 交付口径与 P4 注意

- **P4 实现后这些红用例应全转绿**（check-gate.sh P6 分流 / agate-md-field-get 新 op / agate-frontmatter-check schema / P6+P3 卡片口径 / ci-gate-backstop refactor 感知）。
- **regression.log 尾行 EXIT_CODE: 0 约定**：P6 refactor 验收记录的 regression.log 由 check-p6-provenance.sh 审计 5 核对（既有机制，本任务不改审计脚本）；fixture 中 regression.log 已带 `EXIT_CODE: 0` 尾行。
- **count-tests 漂移**：新增 19 用例后 `bash agate/tests/scripts/count-tests.sh` 计数上升（4 文件 110/10/14/9）；`docs/plans/agate-test-plan-2026-07-01.md` 附录 A 同步留待 P4/P5（P2 §6.6 实现完成标志要求）。
- **self-gate**：本次仅新增 .bats 测试文件（不触发 agate/scripts/*.sh 或协议文档的 self-gate 清单），P4 改动协议文档/脚本时按 SELF-GATE.md 处理。
