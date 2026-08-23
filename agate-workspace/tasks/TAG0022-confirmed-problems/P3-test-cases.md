---
phase: P3
task_id: TAG0022-confirmed-problems
type: test-cases
parent: P2-design.md
trace_id: TAG0022-P3-20260822
status: draft
created: 2026-08-22
agent: test-designer
---

# P3 测试用例清单 — TAG0022 三连任务确认问题修复批（P3 可写测试面：0038 / 0039 / 0041）

> 状态标记：`[PROD_NOT_TOUCHED]`（只写 worktree `agate/tests/unit/` 与 `agate-workspace/tasks/`；`~/.agate` 稳定版与主 checkout 只读）。
> TDD 口径：以下用例**先于实现**交付（P4 才转绿）；本文件为 P4 implementer 的行为契约。
> 上游：P1-requirements.md（BDD-1..10）/ P2-design.md（§3 完成标准 / §4.2.1 逐点映射 / §4.3 judge 判据 / §4.5 0041 / §7 files_to_read）/ P2-review.md（NB-1~6 + TG-1~3，P3 必须落实）。

## 1. 声明

```yaml
test_code_dir: agate/tests/unit/
```

- **测试代码落盘位置**：worktree `agate/tests/unit/` 下 5 个文件（1 新增 + 4 增量/修改），清单见 §2。
- **本次 P3 测试面**：BDD-3/5（0038 静态扫描 + S-3 收紧）/ BDD-6/7（0039 judge P1 校验）/ BDD-9/10（0041 环境测试根治）。
- **无 P3 测试面的 BDD**：BDD-1/2（0037 CI 配置/文档 + ruff 验收，P5/P6 验证）、BDD-4/8（全量绿/实证计划验收，P5/P6 验证）——不映射测试（dispatch-context 明示）。
- **P3 自检结论**：全部红灯用例失败原因均为「被测模块未实现/行为未变更」（B 类），无断言与数据矛盾（无 T075 型手写魔数矛盾）；自跑记录见 `P3-progress.md`。

## 2. 测试文件清单

| # | 文件（worktree `agate/tests/unit/`） | 改动 | 覆盖 BDD | 用例数 |
|---|-------------------------------------|------|---------|--------|
| 1 | `test_md_parse_scan.py`（新增） | 新建 | BDD-3 | 1 |
| 2 | `test_check_gate.py`（增量） | 追加 gate_p1 judge 用例区 | BDD-6/7 | 7 |
| 3 | `test_check_structure_consistency.py`（增量） | 追加 S-3a/S-3b 双向漂移用例区 | BDD-5 | 3 |
| 4 | `test_check_routing.py`（修改） | `_run_routing` 增 env 透传（NB-5）+ test_bdd_7 注入 `GIT_CEILING_DIRECTORIES` | BDD-9/10 | 1（改造） |
| 5 | `test_env_adapt_docs.py`（修改） | test_bdd_25 位置感知 + M15 排除钩子单测（TG-3） | BDD-9/10 | 3（1 改造 + 2 新增） |

## 3. BDD ↔ 测试映射表（1:1）

> 预期红灯类型：B 类 = assertion 失败（被测模块未实现 / 行为未变更）；绿 = 回归守卫（P3 现状即绿，P4 后仍绿）。

| BDD | 子项 | 测试用例（文件::函数） | 用例描述 | 现状 | 预期红灯类型 |
|-----|------|------------------------|---------|------|-------------|
| BDD-3 | 0038 | `test_md_parse_scan.py::test_bdd_3_check_gate_no_protocol_md_parse_points` | 静态扫描 check-gate.py（非注释代码行），A/B/C/D 组 24 条模式（P2 §4.2.1 固化清单）命中数 = 0；E/F 组不计入（D2 口径）；NB-6 补全 L799/805 | **红**（命中 43 处） | B 类（迁移未实施） |
| BDD-5 | 0038 | `test_check_structure_consistency.py::test_bdd_5_s3a_yaml_gate_cmd_not_in_card_exit_1` | S-3a YAML→md：phases.yaml gates 增补命令串但卡片 `## gate 规则` 未出现 → 非 0 | **红**（exit 0 未报） | B 类（S-3a 未实现） |
| BDD-5 | 0038 | `test_check_structure_consistency.py::test_bdd_5_s3b_card_gate_cmd_not_in_yaml_exit_1` | S-3b md→YAML：卡片含机器可判定命令行但 YAML gates 未声明 → 非 0 | **红**（exit 0 未报） | B 类（S-3b 未实现） |
| BDD-5 | 0038 | `test_check_structure_consistency.py::test_bdd_5_s3a_s3b_both_sides_consistent_exit_0` | 双侧一致（YAML 命令串 ↔ 卡片命令行俱在）→ exit 0 | 绿 | ——（守卫） |
| BDD-6 | 0039 | `test_check_gate.py::test_bdd_6_gate_p1_new_task_missing_judge_exit_1` | 机制后新任务（P1 created 2026-08-22 ≥ judge_required_since）且 .state.yaml 无 judge 块 → check-gate P1 exit 1 | **红**（现 exit 2） | B 类（judge P1 校验未实现） |
| BDD-6 | 0039 | `test_check_gate.py::test_bdd_6_gate_p1_new_task_judge_enabled_true_exit_2` | 机制后新任务含 `judge.enabled: true` → 放行（exit 2 语义不变） | 绿 | ——（守卫） |
| BDD-6 | 0039 | `test_check_gate.py::test_bdd_6_gate_p1_judge_disabled_after_cutoff_exit_1` | `judge.enabled: false` + created ≥ cutoff → exit 1（NB-4：falsy 同走 created 判据） | **红**（现 exit 2） | B 类（judge P1 校验未实现） |
| BDD-7 | 0039 | `test_check_gate.py::test_bdd_7_gate_p1_historical_pre_cutoff_no_judge_exit_2` | 历史任务（created 2026-08-19 < cutoff）无 judge 块 → 不拦（exit 2） | 绿 | ——（守卫） |
| BDD-7 | 0039 | `test_check_gate.py::test_bdd_7_gate_p1_historical_no_created_fail_open_exit_2` | created 缺失 → fail-open 不拦（exit 2，R5 兼容存量） | 绿 | ——（守卫） |
| BDD-7 | 0039 | `test_check_gate.py::test_bdd_7_gate_p1_judge_disabled_pre_cutoff_exit_2` | falsy + pre-cutoff → 跳过不拦（NB-4 推荐口径） | 绿 | ——（守卫） |
| BDD-7 | 0039 | `test_check_gate.py::test_bdd_7_gate_p1_judge_non_dict_malformed_fail_open_exit_2` | judge 非 dict（`judge: true` bool）+ created 缺失 → 按缺失处理 fail-open 不拦（TG-2） | 绿 | ——（守卫） |
| BDD-9 | 0041 | `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`（改造） | 注入 `GIT_CEILING_DIRECTORIES=<tmp_path>` 确定性 git_ok:false + thin + 算分异常 → exit 1；语义不依赖 basetemp 位置（P2 §4.5.1，实测 rc=128） | 绿（改造转绿属预期，约束 3） | ——（守卫，P4 后仍绿） |
| BDD-9 | 0041 | `test_env_adapt_docs.py::test_bdd_25_consistency_zero_error`（改造） | basetemp ∈ 仓库根 → 注入 `AGATE_CONSISTENCY_SKIP_DIRS=<rel>` 免疫污染（M15）；仓库外不注入；两位置均断言 0 ERROR | 仓库外绿；**仓库内红**（M15 未实现 → env 无效果，CLI 级机制验证 ERROR=1） | B 类（M15 未实现，仅仓库内位置） |
| BDD-9 | 0041 | `test_env_adapt_docs.py::test_m15_iter_md_files_skip_dirs_injected_excluded` | M15 钩子：注入 SKIP_DIRS 后 iter_md_files 不产出被排除路径（TG-3） | **红**（skip-dir/c.md 仍产出） | B 类（M15 未实现） |
| BDD-9 | 0041 | `test_env_adapt_docs.py::test_m15_iter_md_files_default_unchanged` | M15 默认未设置时行为不变（扫面变化可观测：产出全部 .md） | 绿 | ——（守卫） |
| BDD-10 | 0041 | `test_check_routing.py` + `test_env_adapt_docs.py` 修改点 | 平台无关回归拦截：无裸 `PATH=`/裸 `python3`/POSIX symlink 硬假设/`/tmp` 字面；git 上下文经 env 注入、rel 路径经 `Path.relative_to` + `as_posix` 归一 | 绿 | ——（守卫，P5 由 `check-platform-assumptions.py` 全树兜底） |

## 4. 红/绿汇总与红灯原因（自跑实测）

- **红集（6 个测试函数；第 7 条为位置条件，非独立用例）**：
  1. BDD-3 静态扫描：check-gate.py 命中 43 处 A/B/C/D 组解析点（`_frontmatter_field` 10 + B 组 16 + C 组 16 + D 组 1）——RM-AG0038 迁移未实施。
  2. BDD-6 缺失 judge：P1 现状无 judge 校验 → exit 2，断言 exit 1 失败——judge P1 校验未实现。
  3. BDD-6 falsy after cutoff：同上（judge P1 校验未实现）。
  4. BDD-5 S-3a：单侧漂移（YAML 加命令串、卡片缺）不报 → exit 0，断言非 0 失败——S-3a 未实现。
  5. BDD-5 S-3b：单侧漂移（卡片加命令行、YAML 缺）不报 → exit 0，断言非 0 失败——S-3b 未实现。
  6. BDD-9 M15 注入：`AGATE_CONSISTENCY_SKIP_DIRS` 无效果 → 被排除路径仍产出——M15 未实现。
  7. BDD-9 test_bdd_25 仓库内位置：注入 env 后仍 ERROR=1（CLI 级机制验证）——M15 未实现（本机权威 basetemp=ptmp 在仓库外，本地自跑走绿分支，红态按位置条件存在）。
- **绿集（227）**：其余全部通过（含既有 gate_p65 judge 五用例、既有 S-* 用例、既有路由/环境文档用例、新守卫用例）——既有用例零意外破坏（NB-1 保持）。
- **不引入平台假设**：无裸 `PATH=`/裸 `python3`；`GIT_CEILING_DIRECTORIES` 为 git 核心机制（跨平台）；rel 路径 `relative_to` + `as_posix` 归一；无 `/tmp` 字面、无 symlink 硬假设。

## 5. 契约注解（P4 implementer 必读）

1. **0039 judge 判据（P2-review 锁定决策 2 + NB-4 推荐口径）**：judge 缺失 → 读 P1 frontmatter `created`（agate-md-field-get `created` op，ISO 字典序比较）≥ `judge_required_since`（rules/dispatch.yaml `"2026-08-22"`）→ exit 1；created 缺失/非 ISO → fail-open（exit 2）；`judge.enabled` falsy 与缺失同走 created 判据（falsy + created ≥ cutoff → exit 1；falsy + pre-cutoff → 跳过）；judge 非 dict（如 `judge: true`）→ 按缺失处理（fail-open，本用例断言口径 = created 缺失时不拦）。
2. **S-3a/S-3b（P2 §4.2.2 + TG-1 + NB-1）**：S-3a/S-3b 是**叠加**在既有 S-3 outputs/orphan/exec_role 检查下的新增子检查，不得重定义 S-3；P6.5 无卡片阶段沿用既有「无卡片跳过」模式（NB-2）。S-3a 口径：gates[].check 命令串须在卡片 `## gate 规则`（或推进条件）节出现；双侧一致用例（§3 BDD-5 第 3 行）要求卡片节内同时含全部 P2 gate 串（对「命令串专属」/「全部串」两种实现语义均稳健）。
3. **M15 排除钩子（[SCOPE+] + TG-3）**：`iter_md_files` 新增 opt-in env `AGATE_CONSISTENCY_SKIP_DIRS=<相对根路径列表>`（正斜杠归一），默认未设置 → 行为逐字节不变；排除分支与既有 rel_parts 排除链同层。测试对 import-time / call-time 读 env 两种实现均稳健（monkeypatch 在 import 前注入 + 唯一模块名）。
4. **test_bdd_7（NB-5）**：`_run_routing` 已增 `env` 参数透传（conftest `_run_cli_impl` env 支持）；改造后转绿属预期（git 核心机制即时生效），不构成「实现先于测试」。
5. **test_bdd_25 位置感知**：basetemp ∈ 仓库根时注入（`tmp_path_factory.getbasetemp()` `relative_to` + `as_posix`），仓库外不注入；断言两位置均 0 ERROR。

## 6. 门槛自检

- P3-test-cases.md 存在且非空 ✓；声明 `test_code_dir: agate/tests/unit/` ✓
- BDD 映射表 1:1 覆盖本次可写测试面（BDD-3/5/6/7/9/10）✓
- 测试代码已写入 worktree `agate/tests/unit/` 对应文件 ✓；自跑确认红 6（全 B 类，原因=被测模块未实现/行为未变更）+ 绿 227，既有用例零意外破坏 ✓
- 平台无关原则未破坏（无裸 PATH/裸 python3/symlink 硬假设//tmp 字面）✓