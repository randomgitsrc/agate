---
phase: P3
task_id: TAG0001-tech-debt-closure
type: test-cases
parent: P2-design.md
trace_id: TAG0001-P3-20260812
status: draft
created: 2026-08-12
agent: test-designer
---

# TAG0001 — P3 测试用例清单（TDD：测试先行，当前全部红灯）

> 角色：test-designer。输入：P2-design.md（方案 + gate_commands + SCOPE+）+ P1-requirements.md（20 条 BDD）+ P0-brief.md + AGENTS.md + 既有 tests/ 结构。
> 方式：BDD→测试 1:1（20 条 BDD = 20 个 `test_bdd_N_*` 用例，N 即 BDD 编号）；另在 check-gate.bats 新增 G8.9/G8.10 两组 P8 行为用例（BDD-16/17 的 gate 行为面）。
> 现状：被测模块（check-debt.sh / agate-debt-check.py / check-gate.sh P8 debt_check 分支 / 协议文档锚点）尚未实现/未改 → 当前全部红灯（红因合规，见 §5）。

## test_code_dir

```yaml
test_code_dir: agate/tests/
gate_commands_P3: "bats agate/tests/unit/agate-debt-check.bats"
```

## 测试文件清单

| 文件 | 动作 | 内容 |
|---|---|---|
| `agate/tests/unit/agate-debt-check.bats` | **新增** | 20 条 `test_bdd_N_*`（BDD-1..20，1:1）；覆盖 schema 校验（BDD-5..10）、T001 回填（BDD-11）、回退覆盖比对（BDD-13..15）、P8 留痕锚点（BDD-16..18）、判据锚点（BDD-19..20）、工作区归类（BDD-1..4）、回退强制文档（BDD-12） |
| `agate/tests/unit/check-gate.bats` | **修改** | ① [SCOPE+] #1：6 处 G8 fixture（G8.2/3/4/6/7/8）P8-release.md 补 `debt_check: none` 行；② 新增 G8.9（缺 debt_check → exit 1）/ G8.10（debt_check 内容任意 → exit 2） |

## BDD → 测试 1:1 映射（20/20）

| BDD | 测试用例（`agate/tests/unit/agate-debt-check.bats`） | 断言要点（P2 §3 可验收路径） | 当前灯 |
|---|---|---|---|
| BDD-1 | `test_bdd_1_workflow_directory_diagram_has_debt_dir` | WORKFLOW.md 目录图含 `debt/` 且 `agents/` 注释不含 tech-debt | 红（文档未改） |
| BDD-2 | `test_bdd_2_mkdir_nine_subdirs_synced_across_three_files` | 三处 mkdir（SETUP/orchestrator-template/state-machine）同一 9 集字面量 + 实跑 mkdir 建出 9 目录 | 红（文档未改） |
| BDD-3 | `test_bdd_3_setup_upgrading_debt_path_consistent` | UPGRADING 含 `debt/tech-debt.md`；SETUP 含 `debt/`；无 `agents/tech-debt` 过期路径 | 红（文档未改） |
| BDD-4 | `test_bdd_4_tag0003_scope_rechecked_to_nine` | TAG0003 P1/P6 BDD-1 修订注含"9 子目录" | 红（文档未改） |
| BDD-5 | `test_bdd_5_valid_entry_passes_schema` | 合法条目（open 无 task_id + closed 含 task_id 与 P5/P6 证据引用）过校验 exit 0 无输出 | 红（脚本不存在） |
| BDD-6 | `test_bdd_6_evidence_missing_intercepted` | evidence 缺失 → exit 1 + 报 evidence | 红（脚本不存在） |
| BDD-7 | `test_bdd_7_invalid_enum_values_intercepted` | category 枚举外值 → exit 1 + 报 category | 红（脚本不存在） |
| BDD-8 | `test_bdd_8_closed_missing_task_id_or_p5p6_intercepted` | closed 缺 task_id → exit 1 + 报 task_id；closed 有 task_id 但 evidence 无 P5/P6 → exit 1 | 红（脚本不存在） |
| BDD-9 | `test_bdd_9_three_state_and_open_with_task_id_legal` | open+task_id 合法 exit 0；`accepted` 第四态 → exit 1 + 报 status | 红（脚本不存在） |
| BDD-10 | `test_bdd_10_no_file_or_no_yaml_block_is_noop` | 无文件/空文件/纯正文无 yaml 块 → exit 0 无输出 | 红（脚本不存在） |
| BDD-11 | `test_bdd_11_t001_backfill_entries_pass_schema` | T1-T4(+A5 protocol) 回填 fixture 过校验 exit 0 无输出（止损条件 1 判据） | 红（脚本不存在） |
| BDD-12 | `test_bdd_12_retreat_requires_debt_entry_documented` | state-transitions + P6/P4 卡片 + agate-retreat-to.sh 均含 DEBT 强制语 | 红（文档未改） |
| BDD-13 | `test_bdd_13_retreat_commit_without_entry_warns` | fixture 仓库有 retreat 提交无条目 → GATE DEBT WARNING + exit 0 | 红（脚本不存在） |
| BDD-14 | `test_bdd_14_retreat_entry_present_no_warning` | source: retreat 条目 evidence 引用提交 hash → 无 WARNING | 红（脚本不存在） |
| BDD-15 | `test_bdd_15_real_retreat_records_fixture_reproducible` | 真实消息格式（023b28b/29301ad 同款 subject）fixture 两方向可复现 | 红（脚本不存在） |
| BDD-16 | `test_bdd_16_p8_card_requires_debt_confirm_and_field` | P8 卡片含"确认债务清单"步骤 + `debt_check` 产出规格 | 红（文档未改） |
| BDD-17 | `test_bdd_17_p8_gate_checks_debt_check_existence_only` | check-gate.sh 含 `debt_check:` 检查；行为面另见 G8.9/G8.10 | 红（脚本未改） |
| BDD-18 | `test_bdd_18_empty_confirmation_observable` | P8 卡片明示 `debt_check: none` 合法选项（可 grep 计数） | 红（文档未改） |
| BDD-19 | `test_bdd_19_criteria_documented_with_no_registration_outlet` | tech-debt-template.md 存在且含"验收声明"判据 + "不登记"出口 | 红（模板不存在） |
| BDD-20 | `test_bdd_20_registration_does_not_exempt_current_task` | 模板含"豁免"硬规则 + plan-eng-review.md 含"DEBT 条目格式" | 红（模板不存在） |

**check-gate.bats 新增 2 组 P8 行为用例（BDD-16/17 的行为面，非 1:1 主映射之外的新 BDD）：**

| 用例 | 断言 | 当前灯 |
|---|---|---|
| `G8.9 check-gate.sh P8 P8-release.md 缺 debt_check 字段 期望 exit 1` | P8-release.md 有 bump_type 无 debt_check → exit 1 + 报 debt_check（P2 §2.5 检查落点） | 红（check-gate.sh P8 分支未实现 debt_check 检查；当前走完返回 exit 2） |
| `G8.10 check-gate.sh P8 debt_check 内容任意（debt_check: none）期望 exit 2 不阻断` | 有 `debt_check: none` → exit 2（只查存在不查内容，BDD-17 不因内容拦截） | 绿（回归守卫测试：现状忽略 debt_check 即通过；P4 实现后须保持不拦截） |

> G8.10 当前绿是**预期**：它测的是"内容任意不阻断"这一正向路径，现状（无 debt_check 检查）与 P4 后（检查通过静默放行）行为一致，属守卫测试，防止 P4 实现把该正向路径改坏。红灯驱动 = `agate-debt-check.bats` 全 20 条 + check-gate.bats G8.9。

## 红灯确认（TDD 自检，2026-08-12）

| 命令 | 结果 | 红因判定 |
|---|---|---|
| `bats --formatter tap agate/tests/unit/agate-debt-check.bats` | `1..20`，20/20 `not ok` | 合规——schema/回退用例红因 `check-debt.sh` 不存在（exit 127，Command not found，B 类红灯）；文档锚点用例红因"协议文档未改"（WORKFLOW/SETUP/UPGRADING/P8 卡片/state-transitions/模板/review 卡 现状不符） |
| `bats --formatter tap agate/tests/unit/check-gate.bats`（-f G8 全组 + 全文件） | 全文件 112 ok / 1 not ok | 合规——唯一 not ok 为新增 G8.9（红因 check-gate.sh P8 分支无 debt_check 检查）；既有 G8.1-8.8 全绿（6 处 fixture 补字段后行为保持 = SCOPE+ #1） |
| `check-tdd-red.sh docs/tasks/TAG0001-tech-debt-closure` | exit 0（真红灯） | P3 gate 判定真红灯（gate_commands.P3 无 formatter → 退化为 exit-code-only，非零退出即红灯） |
| `bats --formatter tap` 可解析性 | 含 TAP plan `1..20` + `not ok` 行 | 合规——generic-tap 可解析 |

无"断言与测试数据矛盾"类红因（所有断言与 P2 §2.1-2.5 / §3 可验收路径一致）。

## [SCOPE+] #1：G8 fixture 同步（6 处）

`check-gate.bats` 中 G8.2 / G8.3 / G8.4 / G8.6 / G8.7 / G8.8 的 P8-release.md 由

```
bump_type: minor
```

补为

```
bump_type: minor
debt_check: none
```

（P8 gate 加 debt_check 缺失即 exit 1 后，若 fixture 不补字段，既有用例将从 exit 2 变 exit 1 全红。）G8.1（缺 bump_type，在 debt_check 检查之前拦截）与 G8.5（无 P8 文件）无需改动。同步后实测 G8 全组（除新增 G8.9 外）仍全绿。

## 门槛自检

- [x] P3-test-cases.md 存在且含 `test_code_dir: agate/tests/` + 合法 Header
- [x] 20 条 BDD 均有对应测试用例（1:1），测试名引用 BDD 编号（`test_bdd_N_*`）
- [x] 测试代码存在且能运行，当前红灯（红因 = 被测模块未实现/未改，无测试代码 bug）
- [x] G8 fixture 同步完成（SCOPE+ #1），相关用例行为保持（仍绿）
- [x] 未改动其他无关测试/实现文件（仅新增 1 个 .bats + 修改 check-gate.bats）
- [x] 测试输出可被 `bats --formatter tap` 解析（含 TAP plan）

## 下游交接（P4/P5 注意）

- P4 按 P2 §2 实现后，本套测试应由红转绿：agate-debt-check.bats 全绿 + check-gate.bats G8.9 转绿 + G8.10 保持绿。
- 若 P4 实现在某条 BDD 上无法转绿，须先核对"断言是否与 P2 §3 可验收路径一致"，再定是改断言还是改实现——测试是 P2 方案的契约执行，不是实现的可调整项。
- 本任务改动触达 `tests/` 与协议文档，commit 需遵循 AGENTS.md self-gate 约定（触发文件含协议 md 时 commit message 须含 `self-gate-review:` 或 `self-gate-skip:`）。
