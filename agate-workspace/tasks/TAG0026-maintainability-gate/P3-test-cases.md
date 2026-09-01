---
test_code_dir: agate/tests/unit/
phase: P3
task_id: TAG0026
parent: P2-design.md
trace_id: TAG0026-P3-20260830
status: draft
created: '2026-08-30'
agent: test-designer
---
# P3-test-cases — TAG0026 维护性反模式 gate

> `agent: test-designer` 由 agate-md-field-set 无该键（合法 key 清单不含 agent），按产出规格手写；
> 其余字段全部经 `agate-md-field-set` 写入。test_code_dir 以 frontmatter 为准，正文 §4 重复声明供人读。

## 1. 产出说明

- **test_code_dir: `agate/tests/unit/`**（frontmatter 已声明；P2-design.md §5 落点）
- 测试文件：
  - `agate/tests/unit/test_check_maintainability.py`（M9 检测器，G1-G10）
  - `agate/tests/unit/test_check_gate_p4_maintainability.py`（M10 P4 挂载，G1-G7）
- 红灯形态（check-tdd-red 判定口径适配，2026-08-31 实测 EXIT=0 真红灯）：
  - M9 文件：`check_maintainability` 模块未实现 → 收集期探测 ImportError → `pytestmark.skipif` 整组跳过（14 skipped）。**不产生 collect-error**——check-tdd-red 无 formatter 分支（judge_result）对 raw_output 的 ModuleNotFoundError 文本一律判 A 类（假红灯 exit 1），collect-error 会毒化整批红灯语义。
  - M10 文件：模块级 sentinel `_IMPLEMENTED`（正则探测 check-gate.py 已 import 且 gate_p4 体消费 `check_maintainability(`）→ 未实现时每条用例首行 `assert _IMPLEMENTED, RED_REASON` 失败（13 failed，全为 assertion failure → classic red-light exit 0 真红灯）。
  - P4 实现落地后：M9 自动解除 skip 参与真实断言；M10 哨言自动转绿、后续行为断言接管。
- P2-review 测试缺口/建议采纳：
  - 缺口 1：BDD-8 补"登记文件存在但 0 条 `| N |` 行 → exit 1"反向分支（test_g2_zero_entries_with_file_exit_1）。
  - 缺口 2：G5 补"violations 非空 + 三重满足 → 穿过新步骤落 return 0"断言（test_g5_violations_registered_passes_to_return_0_with_skeleton_warning）。
  - 建议 1：G5b 既有 ①②③④ 失败路径逐项等价断言（test_g5_legacy_failure_paths_unchanged，含 agent 缺失 → 2 的既有 WARNING 语义面）。
  - 建议 2：G6 ImportError 降级用 monkeypatch（in-process 导入 check-gate 模块后 patch `check_maintainability` 属性为 None / git_ok=False 假实现）。

## 2. P2 §5 分组 → 用例映射（M9 检测器）

| 分组 | BDD | 用例（函数名） | 要点 |
|------|-----|---------------|------|
| G1 god-file 跨越 | BDD-1 | `test_bdd_1_god_file_crossing` | 900→1150 行 staged；violations 含 src/big.py（god_file_count ≥ 1） |
| G2 存量不误伤 | BDD-2 | `test_bdd_2_existing_god_file_not_flagged` | 1200 行已 commit，改 5 行 staged；god_file_count == 0 |
| G3 fuzzy Python | BDD-3 | `test_bdd_3_fuzzy_python_bare_except` | 新增裸 `except:` 行 staged；violation 含文件+新增行号（line 13） |
| G4 存量行不误伤 | BDD-4 | `test_bdd_4_existing_bare_except_not_flagged` | 存量裸 except 不在 diff 新增行；fuzzy_boundary_count == 0 |
| G5 阈值可配置 | BDD-5 | `test_bdd_5_threshold_configurable` | maintainability.yaml `god_file_threshold: 500` → 480→520 触发；默认 1000 同场景不触发 |
| G6 配置缺失兜底 | BDD-6 | `test_bdd_6_config_missing_invalid_fallback` | 无配置 / 坏 YAML / 单键缺失三态 → 不抛错返回有效判定（默认 N=1000） |
| G7 路径平台无关 | BDD-11 | `test_bdd_11_path_separator_normalized` | violations 的 file 一律 `/` 归一形态；`_norm_rel` 两分隔符等价（模拟，Windows 真行为由 windows_smoke + CI 覆盖） |
| G8 移动假阳性诚实行为 | BDD-12 | `test_bdd_12_moved_code_new_lines_judged` | 裸 except 块 A→B 移动（删+增）；新增行照判 violation（行号 > 原位置） |
| G9 P4 数据源对齐 | BDD-13 | `test_bdd_13_p4_staged_diff_readable` | staged 代码 → 读到 diff 判定（P4）；`git reset` 清暂存区（P6 形态对照）→ 无 violation |
| G10 模块契约 | 实现导航 | `test_g10_module_importable` / `test_g10_dict_shape` / `test_g10_violation_entry_shapes` / `test_g10_git_channel_fail_closed` / `test_g10_cli_exit_codes` | import 可达；dict 四键形状；god-file/fuzzy-boundary 条目形状；git 通道失败 git_ok=False（fail-closed）；CLI exit 1（有 violation）/ 0（无 violation） |

## 3. P2 §5 分组 → 用例映射（M10 P4 挂载）

| 分组 | BDD | 用例（函数名） | 要点 |
|------|-----|---------------|------|
| G1 登记缺失阻断 | BDD-7 | `test_g1_missing_known_violations_exit_1` | violations 非空 + known-violations.md 不存在 → exit 1 |
| G2 数量不对齐阻断 | BDD-8 | `test_g2_registration_insufficient_exit_1` + `test_g2_zero_entries_with_file_exit_1` | 登记 2 条 < violations 3 → exit 1；文件存在但 0 条（`| # |` 样例行不计数）→ exit 1 |
| G3 评审未 approve 仍阻断 | BDD-9 | `test_bdd_9_review_missing_exit_1` / `test_bdd_9_review_not_approved_exit_1` / `test_bdd_9_review_agent_main_exit_1` | 登记 1=1 对齐但 review 缺失 / status=pending / agent=main 三态 → 各自 exit 1（顺序保证，新步骤不改 ①②③ 语义） |
| G4 三重满足放行 | BDD-10 | `test_bdd_10_all_three_satisfied_exit_0` | violations=3 + 登记 3 条（真写文件，count_kf_entries 口径）+ approved(agent≠main) → exit 0 |
| G5 无 violations 回归面 | R1 | `test_g5_no_violations_baseline_equivalence` / `test_g5_legacy_failure_paths_unchanged` / `test_g5_violations_registered_passes_to_return_0_with_skeleton_warning` | 合规任务 exit 0 且无新消息；既有 ①②③④ 逐项等价（含 agent 缺失 → 2）；非空+三重满足落 return 0（新步骤不得中途 return） |
| G6 ImportError 降级 | R2 | `test_g6_import_error_degrades_to_warning` / `test_g6_git_unavailable_degrades_to_warning` | monkeypatch `check_maintainability`=None → gate_p4 返回 0；git_ok=False 假实现 → 返回 0 |
| G7 返回约定 | 约束 4 | `test_g7_no_new_return_2_from_new_step` | 门槛 a/b 失败仅 return 1；既有 return 2（agent 缺失）语义不被动 |

## 4. BDD-1..13 覆盖对照（1:1，无挑验）

| BDD | 用例文件 | 用例 |
|-----|---------|------|
| BDD-1 | test_check_maintainability.py | test_bdd_1_god_file_crossing |
| BDD-2 | test_check_maintainability.py | test_bdd_2_existing_god_file_not_flagged |
| BDD-3 | test_check_maintainability.py | test_bdd_3_fuzzy_python_bare_except |
| BDD-4 | test_check_maintainability.py | test_bdd_4_existing_bare_except_not_flagged |
| BDD-5 | test_check_maintainability.py | test_bdd_5_threshold_configurable |
| BDD-6 | test_check_maintainability.py | test_bdd_6_config_missing_invalid_fallback |
| BDD-7 | test_check_gate_p4_maintainability.py | test_g1_missing_known_violations_exit_1 |
| BDD-8 | test_check_gate_p4_maintainability.py | test_g2_registration_insufficient_exit_1 + test_g2_zero_entries_with_file_exit_1 |
| BDD-9 | test_check_gate_p4_maintainability.py | test_bdd_9_review_missing_exit_1 + test_bdd_9_review_not_approved_exit_1 + test_bdd_9_review_agent_main_exit_1 |
| BDD-10 | test_check_gate_p4_maintainability.py | test_bdd_10_all_three_satisfied_exit_0 |
| BDD-11 | test_check_maintainability.py | test_bdd_11_path_separator_normalized |
| BDD-12 | test_check_maintainability.py | test_bdd_12_moved_code_new_lines_judged |
| BDD-13 | test_check_maintainability.py | test_bdd_13_p4_staged_diff_readable |

13/13 全覆盖：BDD-1..6/11/12/13 → M9（10 BDD 用例 + 5 契约用例 = 15）；BDD-7/8/9/10 → M10（11 用例）。合计 26 用例 + 2 文件级 skip/sentinel 机制。

## 5. 测试环境与平台无关声明

- git 操作全部经 conftest `git_repo` fixture（tmp_path 下 `GitRepo`），仓库内不做任何对 worktree 本体的 git 写操作。
- 全部临时目录走 pytest `tmp_path`；无 `/tmp` 字面、无裸 `python3`（`python_exe` 探测）、无硬编码 `/home/...` 绝对路径。
- `agate_scripts`（AGATE_ROOT 解析）由 conftest `agate_root` fixture 提供，CI 无 `~/.agate` 时走 env 覆盖/上溯反推。
- Windows 差异：BDD-11 路径分隔符在 Linux 用模拟路径断言归一等价；`test_g1_...` 标 `@pytest.mark.windows_smoke`（每文件第 1 个用例约定）。未假设 POSIX symlink 语义。
- fixture 需求记录：conftest 现有 fixture（git_repo/task_dir/agate_root/python_exe/run_cli）已满足全部场景，**无需改动 conftest**。

