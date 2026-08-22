---
phase: P3
task_id: TAG0021-structured-layer
type: test-cases
parent: P2-design.md
trace_id: TAG0021-P3-20260822
status: draft
created: 2026-08-22
agent: test-designer
---

# P3 测试用例 — TAG0021 协议结构化层（RM-AG0022）

> 状态标记：[PROD_NOT_TOUCHED]（仅读稳定版与主 checkout 协议文件；全部写操作落在 worktree `agate-workspace/` 与 worktree `agate/tests/` 内）

## 1. 测试代码位置声明

```yaml
test_code_dir: agate/tests/unit/
```

| 测试文件 | 功能域 | 对应 BDD | 用例数 |
|---------|--------|---------|:---:|
| `agate/tests/unit/test_check_yaml_schema.py` | schema 校验（BDD-1） | BDD-1 | 8 |
| `agate/tests/unit/test_check_structure_consistency.py` | S-1~S-6 双向一致性（BDD-2/3/5） | BDD-2/3/5 | 10 |
| `agate/tests/unit/test_check_reconcile.py` | M1/M2 对账模式（BDD-6/7/8） | BDD-6/7/8 | 7 |
| `agate/tests/unit/test_structure_migration.py` | M2 切权威源 + gate 提升阻断（BDD-9/10） | BDD-9/10 | 4 |
| `agate/tests/unit/test_card_render.py` | M3 卡片渲染化（BDD-12/13） | BDD-12/13 | 4 |
| `agate/tests/unit/test_cross_milestone.py` | 跨里程碑平台无关（BDD-16） | BDD-16 | 1 |
| `agate/tests/unit/_rules_test_utils.py` | 共享夹具（非测试模块，不计数） | — | — |

**合计：34 条新测试用例**（pytest collect-only 计数：1168 → **1202**，只增不减，BDD-15 满足）。

## 2. BDD ↔ 测试用例 1:1 映射表

| BDD | 里程碑 | 测试文件 | 用例（测试名） | 预期红灯类型 |
|-----|-------|---------|---------------|-------------|
| BDD-1 | M0 | test_check_yaml_schema.py | `test_bdd_1_valid_rules_exit_0` / `test_bdd_1_invalid_enum_exit_nonzero` / `test_bdd_1_invalid_type_exit_nonzero` / `test_bdd_1_invalid_field_exit_nonzero` / `test_bdd_1_missing_required_exit_nonzero` / `test_bdd_1_dispatch_mode_enum_aligned` / `test_bdd_1_schema_self_check_exit_nonzero` / `test_bdd_1_dispatch_schema_roundtrip` | B（`check-yaml-schema.py` 未实现 → 存在性断言失败）|
| BDD-2 | M0 | test_check_structure_consistency.py | `test_bdd_2_s1_s2_consistent_exit_0`（含 READY 行排除）/ `test_bdd_2_s1_yaml_extra_phase_exit_1` / `test_bdd_2_s2_md_extra_phase_exit_1` / `test_bdd_2_s1_name_mismatch_exit_1` | B（`check-structure-consistency.py` 未实现）|
| BDD-3 | M0 | test_check_structure_consistency.py | `test_bdd_3_s6_missing_reference_exit_1` / `test_bdd_3_s5_schema_enum_violation_exit_1` | B |
| BDD-4 | M0 | **声明（无新测试）** | 存量行为不变由 P5 全量回归覆盖（gate_commands.P5 / P5_consistency / P5_count）；M0 纯增量不碰既有脚本 | — |
| BDD-5 | M0 | test_check_structure_consistency.py | `test_bdd_5_s3_card_output_mismatch_exit_1` / `test_bdd_5_s4_field_readers_unknown_field_exit_1` / `test_bdd_5_s4_gate_commands_syntax_mismatch_exit_1` / `test_bdd_5_initial_consistency_exit_0` | B |
| BDD-6 | M1 | test_check_reconcile.py | `test_bdd_6_pruning_warning_and_exit_preserved` / `test_bdd_6_read_gate_commands_unknown_key_warning` / `test_bdd_6_check_gate_p2_reconcile_warning` | B（M1 对账钩子未实现 → 断言 `RECONCILE` 输出缺失；退出码保持断言在 P3 已成立）|
| BDD-7 | M1 | test_check_reconcile.py | `test_bdd_7_coverage_three_scripts_three_parse_points` / `test_bdd_7_project_module_not_warned` | B |
| BDD-8 | M2 | test_check_reconcile.py | `test_bdd_8_zero_diff_blocks_switch` / `test_bdd_8_normalization_list_inline_block_equal` | B |
| BDD-9 | M2 | test_structure_migration.py | `test_bdd_9_migrated_patterns_zero_hits` | B（P3 当下已迁移解析模式仍命中 2 处——实测 `agate-read-gate-commands.py` 与 `check-gate.py`；M2 删除 md 正则后归零）|
| BDD-10 | M2 | test_structure_migration.py | `test_bdd_10_script_drift_blocked` / `test_bdd_10_precommit_includes_structure_step` / `test_bdd_10_ci_includes_structure_step` | B（脚本缺失 / pre-commit 未调用 / CI 未追加）|
| BDD-11 | M2 | **声明（无新测试）** | 迁移后回归全绿由 P5 全量回归 + `P5_consistency` + `P5_count` 覆盖（M2-6 fixture 增补 YAML 构造的回归面） | — |
| BDD-12 | M3 | test_card_render.py | `test_bdd_12_rendered_card_matches_yaml_exit_0` / `test_bdd_12_tampered_yaml_detected` | B |
| BDD-13 | M3 | test_card_render.py | `test_bdd_13_inject_renders_from_yaml` / `test_bdd_13_stable_isolation_not_polluted` | B（P3 注入静态卡片无 YAML marker；隔离测试双工具两次注入）|
| BDD-14 | M3 | **声明（无新测试）** | 渲染化回归全绿由 P5 全量回归 + `P5_structure`/`P5_schema`/`P5_count` 覆盖 | — |
| BDD-15 | M0-M3 全程 | **声明（无新测试）** | 由既有 `agate/tests/scripts/count-tests.sh` + `gate_commands.P5_count`（每里程碑血糖）履行：本任务新增测试文件被 pytest collect-only 自动纳入计数（1168→1202），单调不减天然成立，无需重实现计数断言 | — |
| BDD-16 | M0-M3 全程 | test_cross_milestone.py | `test_bdd_16_new_scripts_exist_and_platform_clean`（新脚本存在 + 过 `check-platform-assumptions.py` R1-R5 扫描） | B（脚本未实现 → 存在性断言失败）|

## 3. 红灯确认记录（自跑）

```bash
# 命令（/tmp 只读约束：-p no:cacheprovider --basetemp=worktree dist/）
python3 -m pytest agate/tests/unit/test_check_yaml_schema.py \
  agate/tests/unit/test_check_structure_consistency.py \
  agate/tests/unit/test_check_reconcile.py \
  agate/tests/unit/test_structure_migration.py \
  agate/tests/unit/test_card_render.py \
  agate/tests/unit/test_cross_milestone.py \
  -q --tb=line -p no:cacheprovider --basetemp=/home/kity/oclab/agate/.worktrees/agate-TAG0021/dist/
```

**结果：34 failed in ~1s（全部 B 类真红灯；0 passed；0 A 类）。**

逐文件失败原因（均为「被测模块/机制未实现」，非测试代码自身 bug）：

| 测试文件 | 失败原因（B 类） |
|---------|----------------|
| test_check_yaml_schema.py（8） | `check-yaml-schema.py` 不存在 → `assert script.is_file()` 失败（P4 M0 交付）|
| test_check_structure_consistency.py（10） | `check-structure-consistency.py` 不存在 → 存在性断言失败（P4 M0 交付）|
| test_check_reconcile.py（7） | 三脚本对账钩子/M1 机制未实现 → `RECONCILE` / `RECONCILE SUMMARY` 输出断言失败（退出码保持断言全部先通过）|
| test_structure_migration.py（4） | BDD-9：已迁移解析模式仍命中 2 处（read-gate-commands 块正则 + check-gate 四字段正则）；BDD-10：脚本缺失 / pre-commit 未调用 / CI 未追加 |
| test_card_render.py（4） | 脚本缺失（S-3 两用例）；注入产物无 YAML 渲染 marker（静态卡片）（BDD-13 两用例）|
| test_cross_milestone.py（1） | 新脚本不存在 → 存在性断言失败 |

**无 A 类假红灯**：无 SyntaxError、无第三方 import 失败（全部仅用 stdlib + pyyaml/pytest 依赖内模块）。**无假绿灯**：最终自跑 34 failed 0 passed。

其它验证：
- 平台无关自检（BDD-16）：`check-platform-assumptions.py` 对新 7 文件扫描 **0 命中（exit 0）**。
- ruff：新 7 文件 `ruff check` 全过（P5_ruff gate 对齐）。
- count-tests：**1202** ≥ 立项基线 749（且 > 既有 1168），只增不减（BDD-15）。

## 4. P2-review 非阻塞发现的测试固化

| 发现 | 固化位置 | 断言内容 |
|------|---------|---------|
| #1 S-2 READY 行排除 | test_check_structure_consistency.py `test_bdd_2_s1_s2_consistent_exit_0`（默认假表含 READY 行 → exit 0）+ `test_bdd_2_s2_md_extra_phase_exit_1`（P4 行必需报错而 READY 行仍排除）| S-2 只匹配 `P` 数字/`P6.5` 前缀行，READY/表外行显式排除 |
| #2 五模式词表对齐 | test_check_yaml_schema.py `test_bdd_1_dispatch_mode_enum_aligned` + `_rules_test_utils.default_dispatch_schema` | dispatch.yaml `modes` 枚举 = {single, static-batch, parallel, recon-then-split, serial}；混入旧词（hybrid）→ 退出码非 0 |
| #3 gate_commands 合法 key | test_check_reconcile.py `test_bdd_7_project_module_not_warned` + test_check_structure_consistency.py `test_bdd_5_s4_gate_commands_syntax_mismatch_exit_1` | 合法 key = `is_gate_meta_key`（`_formatter`/`_timeout_seconds` 后缀）**OR** `project_module` 特判（参照 agate-gate-missing-cmds.py）；project_module 不得告警，语法声明缺特判 → S-4 非 0 |
| #4 825 基线出处 | 本文件 §1/§2 用「既有 fixture 集合」表述 + count-tests 实数值（1202）；M2-6 fixture 增补语义不依赖具体数字 | 不引入 825 字面量 |
| #5 53/57 口径 | 未在测试中硬编码脚本总数；BDD-9 只扫已迁移脚本清单（D3 首批三脚本 + md-field-get），与 P1 §4.1 口径一致 | 不写死 53/57 |

对账归一化规则表（R10 / P2-review「测试缺口」）固化为 `test_bdd_8_normalization_list_inline_block_equal`（frontmatter 空格连接 list vs 正文内联 `[a, b]` / 块式 `- a` 语义等价 → 0 差异）与 `test_bdd_8_zero_diff_blocks_switch`（值真不同 → 非 0 计数兜底）。

## 5. 测试会话约定（夹具 seam，P4 实现契约）

1. **AGATE_ROOT 环境变量**：`check-yaml-schema.py` / `check-structure-consistency.py` / `agate-inject-card.py` 均按 `agate_common.resolve_agate_root` 四层链解析（env → 项目声明 → current/latest → 脚本路径上溯，P2-design §3.6）；测试构造 tmp_path 下的**最小假协议树**（`_rules_test_utils.make_fake_root`：rules/*.yaml + schema/*.json + WORKFLOW.md 总览表 + phase-cards/P2-design.md + scripts/ + assets/ 占位），以 `AGATE_ROOT=<假树>` 驱动被测脚本，**不触碰真实 worktree 协议文件**（P3 时 rules YAML 尚不存在）。
2. **假树默认内容互证**：S-1~S-6 全过 + schema 全过；测试传覆写参数制造漂移。YAML 形状沿用 P2-design §3.1/§3.2 已定字段（`schema_version`/`phases`（id/name/exec_role/outputs/gates/retry_cap）/`modes`/`templates`/`gate_commands_syntax`/`field_readers`/`execution_roles`/`review_roles`/`scripts`）。
3. **对账开关**：`AGATE_RECONCILE` 缺省 on（P2-design §3.4）；测试不设该环境变量即走缺省路径。
4. **BDD-13 注入测试**：`make_fake_root(..., agate_scripts=...)` 会把真实 `agate-next-card.py` 拷贝进假树 scripts/（该脚本 agate_common 缺失时回退 env AGATE_ROOT）——使测试在 P3（静态卡片 → 红）与 M3（渲染器版本 → 绿）两阶段都可运行。
5. **平台无关**：全部临时内容经 pytest `tmp_path` / `--basetemp=worktree dist/`；无裸解释器字面量、无 `PATH=`、无 `-L` 软链假设、无临时目录字面量（本文件与测试源码均经 `check-platform-assumptions.py` 0 命中验证）。

## 6. 下游说明（P4 implementer）

- P4 按本映射表实现：M0 两新脚本（`check-yaml-schema.py` / `check-structure-consistency.py`，S-1~S-6 六条 rep 编号检查，S-5 串联 schema 校验、S-6 校验 `file:`/`template:`/`script:` 引用存在性）；M1 `agate_common.reconcile_field` + 三消费点（agate-read-gate-commands / check-pruning / check-gate）对账钩子 + `RECONCILE WARNING`/`RECONCILE SUMMARY` 出口（退出码 0/2 不变）；M2 删除已迁移 md 正则（BDD-9 归零）+ pre-commit-gate.py / protocol-tests.yml 追加 structure 步骤（BDD-10）；M3 `agate-inject-card.py` 内嵌 `render_card()` 读 AGATE_ROOT 解析 YAML 渲染（含 project_module 特判词表）。
- 每条测试的「空实现锚点断言」（存在性 / RECONCILE 出现 / marker 出现 / 模式归零）即 P4 验收锚点：实现哪条 BDD 就应让对应断言转绿。

## 7. 关联文件

- 夹具共享模块：`agate/tests/unit/_rules_test_utils.py`
- 分阶段落盘：`agate-workspace/tasks/TAG0021-structured-layer/P3-progress.md`
