---
phase: P3
task_id: TAG0023-mechanism-checks
type: test-cases
parent: P2-design.md
trace_id: TAG0023-P3-20260824
status: draft
created: 2026-08-24
agent: test-designer
---

> [PROD_NOT_TOUCHED] 本阶段仅读取 P1/P2/P2-review/角色定义/现状生产脚本源码 + 在 worktree
> 内写测试代码与本文件，未对生产脚本做任何修改，未触碰 worktree 之外任何路径。

# P3 测试用例 — TAG0023 机制校验补强批（RM-AG0042~0045）

`test_code_dir: agate/tests/unit/`

本任务测试**追加到既有测试文件**（而非新建独立目录），理由：dispatch-context 明确按 P2
`dispatch_plan` 5 批分组织，每批对应文件已在被测生产脚本所属的现有测试文件中（
`test_check_state_transition.py` / `test_check_gate.py` / `test_agate_debt_check.py` /
`test_check_frontmatter.py` / `test_check_routing.py` / `test_agate_render_dispatch_prompt.py`），
延续既有测试组织与断言风格（`_write_state`/`_run_state`/`_run_gate`/`_run_frontmatter`/
`_run_routing` 等 helper 复用）比新建平行目录更符合本仓库既有测试卫生惯例；仅 BDD-10 因
dispatch-context 明确要求新建独立清单文件存在性测试而新建
`test_env_sensitive_tests_registry.py`。

## 1. BDD → 测试函数 → 文件 映射表（13 条，1:1，BDD-9 除外见 §3）

| BDD | 子项 | 测试函数 | 所在文件 |
|-----|------|---------|---------|
| BDD-1 | RM-AG0042 | `test_bdd_1_review_rejected_retry_file_empty_retries_warning`（分支①：命中+空 retries→WARNING）<br>`test_bdd_1_review_rejected_retry_file_with_retries_no_warning`（分支②：命中+有 retries→无 WARNING）<br>`test_bdd_1_no_retry_dispatch_context_file_no_warning`（分支③：无命中→无 WARNING）<br>`test_bdd_1_negative_anchor_implementer_review_fix_not_matched`（负面锚点①，真实历史假阳性样本）<br>`test_bdd_1_negative_anchor_consistency_reviewer_not_matched`（负面锚点②，真实历史假阳性样本） | `agate/tests/unit/test_check_state_transition.py` |
| BDD-2 | RM-AG0042 | `test_bdd_2_retreat_p5_to_p4_no_retries_growth_exit_1`（阻断）<br>`test_bdd_2_retreat_p5_to_p4_retries_growth_exit_0`（回归防呆） | `agate/tests/unit/test_check_state_transition.py` |
| BDD-3 | RM-AG0042 | `test_bdd_3_empty_return_redispatch_keyword_empty_retries_warning`<br>`test_bdd_3_empty_return_redispatch_keyword_with_retries_no_warning` | `agate/tests/unit/test_check_state_transition.py` |
| BDD-4 | RM-AG0042 | `test_bdd_4_no_event_empty_retries_exit_0_no_warning` | `agate/tests/unit/test_check_state_transition.py` |
| BDD-5 | RM-AG0043 | `test_bdd_5_p8_roadmap_rm_not_done_blocked_exit_1` | `agate/tests/unit/test_check_gate.py` |
| BDD-6 | RM-AG0043 | `test_bdd_6_p8_roadmap_no_matching_rm_not_blocked_exit_2` | `agate/tests/unit/test_check_gate.py` |
| BDD-7 | RM-AG0043（历史补记）| `test_bdd_7_roadmap_rm_ag0032_backfilled_done` | `agate/tests/unit/test_check_gate.py` |
| BDD-8 | RM-AG0044 | `test_bdd_8_recon_plan_and_known_baseline_four_elements` | `agate/tests/unit/test_agate_debt_check.py` |
| BDD-9 | RM-AG0044 | 无测试函数（占位声明，见 §3） | — |
| BDD-10 | RM-AG0044 | `test_bdd_10_env_sensitive_tests_registry_exists_with_required_entries` | `agate/tests/unit/test_env_sensitive_tests_registry.py`（新建） |
| BDD-11 | RM-AG0045 | `test_bdd_11_dispatch_prompt_declares_write_time_selfcheck_section` | `agate/tests/unit/test_agate_render_dispatch_prompt.py` |
| BDD-12 | RM-AG0045 | `test_bdd_12_missing_required_field_error_includes_fix_hint`<br>`test_bdd_12_invalid_enum_error_includes_fix_hint` | `agate/tests/unit/test_check_frontmatter.py` |
| BDD-13 | RM-AG0045（历史回归）| `test_bdd_13_historical_coupling_checklist_non_list_write_time_caught`<br>`test_bdd_13_historical_fullwidth_colon_write_time_caught` | `agate/tests/unit/test_check_frontmatter.py` |
| BDD-13（续，第③类）| RM-AG0045 | `test_bdd_13_historical_source_count_6_over_5_write_time_caught` | `agate/tests/unit/test_check_routing.py` |

共 **22 个测试函数**（BDD-1 贡献 5 个、BDD-2/3 各 2 个、BDD-4/5/6/7/8/10/11 各 1 个、
BDD-12 贡献 2 个、BDD-13 贡献 3 个），覆盖 13 条 BDD 中的 12 条（BDD-9 占位声明不产出
pytest 用例）。

## 2. 实测 pytest 结果（真红灯证据）

### 2.1 仅新增/改动的 7 个测试文件（隔离 basetemp，排除环境噪音）

```
$ timeout 180s python3 -m pytest agate/tests/unit/test_check_state_transition.py \
    agate/tests/unit/test_check_gate.py agate/tests/unit/test_agate_debt_check.py \
    agate/tests/unit/test_env_sensitive_tests_registry.py \
    agate/tests/unit/test_check_frontmatter.py agate/tests/unit/test_check_routing.py \
    agate/tests/unit/test_agate_render_dispatch_prompt.py \
    -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_clean2

10 failed, 285 passed in 30.11s
```

10 个失败全部为本轮新增的 TAG0023 用例，逐一核对失败原因均为**断言失败**（B 类红灯，非
语法错误/项目外 import 失败）：

| 失败测试函数 | 失败原因（真红灯来源） |
|---|---|
| `test_bdd_1_review_rejected_retry_file_empty_retries_warning` | `check-state-transition.py` 尚无新函数扫描评审重试 dispatch-context 文件，stderr 恒为空，`assert "WARNING" in result.output` 失败 |
| `test_bdd_2_retreat_p5_to_p4_no_retries_growth_exit_1` | 现有检查 1 只判 `diff>=2`，P5→P4（diff==1）不触发任何拦截，`assert returncode == 1` 失败（实际 0） |
| `test_bdd_3_empty_return_redispatch_keyword_empty_retries_warning` | 同 BDD-1，无关键词扫描机制，`assert "WARNING" in result.output` 失败 |
| `test_bdd_5_p8_roadmap_rm_not_done_blocked_exit_1` | `gate_p8()` 无 roadmap.md 读取，全量合规场景下恒 return 2，`assert returncode == 1` 失败（实际 2） |
| `test_bdd_7_roadmap_rm_ag0032_backfilled_done` | `roadmap.md` 中 RM-AG0032 当前两行（backlog/scheduled）确无 done 行，`assert done_lines` 失败 |
| `test_bdd_8_recon_plan_and_known_baseline_four_elements` | `agate/tests/ENV-SENSITIVE-TESTS.md` 尚未创建，`assert env_sensitive_doc.is_file()` 失败 |
| `test_bdd_10_env_sensitive_tests_registry_exists_with_required_entries` | 同上，清单文件不存在 |
| `test_bdd_12_missing_required_field_error_includes_fix_hint` | `agate-frontmatter-check.py` 现状消息为"缺必填字段 X"，无"补"字样，`assert "补" in result.output` 失败 |
| `test_bdd_12_invalid_enum_error_includes_fix_hint` | 现状消息为"非法值 X（合法值: ...)"，无"改用"字样，`assert "改用" in result.output` 失败 |
| `test_bdd_11_dispatch_prompt_declares_write_time_selfcheck_section` | `dispatch-prompt.md` 尚无"P1/P2 声明写时自检"小节文本，`assert` 失败 |

其余 285 个测试通过，含本批新增的 12 个"回归防呆"分支用例（`test_bdd_1_*_with_retries_no_warning`
`_no_retry_dispatch_context_file_no_warning` 两个负面锚点、`test_bdd_2_*_growth_exit_0`、
`test_bdd_3_*_with_retries_no_warning`、`test_bdd_4_*`、`test_bdd_6_*`、
`test_bdd_13_*` 三个历史回归锚点）——这些用例当前**本就应为绿灯**（见 §3 说明），
不是假红灯遗漏。

首次运行曾额外触发 1 个 `ERROR`（`test_st_1_no_state_yaml_staged_exit_0` 的 fixture
teardown 阶段报 `rm_rf` 失败），复核为 `--basetemp` 目录残留自并发历史运行的非空垃圾
目录，与本批新增测试代码无关；换一个干净 basetemp 目录复跑后该 ERROR 消失，10 failed /
285 passed 结果不变，确认非本批引入的问题。

### 2.2 全量 `agate/tests/` 回归确认（未破坏既有测试）

```
$ timeout 300s python3 -m pytest agate/tests/ -q -p no:cacheprovider \
    --basetemp=/home/kity/oclab/dsh-workspace/ptmp_full3

10 failed, 1224 passed, 2 skipped in 121.86s
```

全量结果的 10 个失败与 §2.1 完全一致（同一组 TAG0023 新用例），既有测试全部保持原
通过状态，未引入新的意外失败。（过程中发现并修复一处自伤：BDD-11 测试初版把
`.read_text(\n    encoding="utf-8"\n)` 跨行书写，触发既有
`test_agate_scripts_encoding.py::test_bdd_5_all_test_py_text_io_explicit_encoding` 的
逐行正则误判"缺 encoding"——该既有测试逐行扫描，`encoding=` 参数换行后不在
`.read_text(` 同一行即被误报；已改为单行写法 `tmpl_path.read_text(encoding="utf-8")`
修复，修复后复跑该既有测试转回绿灯，全量结果由「11 failed, 1223 passed」回到
「10 failed, 1224 passed, 2 skipped」。）

## 3. 特殊 BDD 说明（如实报告，不做数字游戏）

### BDD-9：占位声明，本阶段不提供单元测试

`test_bdd_14_retreat_entry_present_no_warning` 连续 5 次 CI 稳定是环境级验收锚，需要
连续触发 5 次 `protocol-tests.yml` 真实 CI run 才能判定，P3 单元测试无法在本地模拟/
断言这类跨多次真实 CI 触发的稳定性结果。**此 BDD 由 P6 阶段的 CI 触发验证覆盖，P3 不
提供单元测试**，未为了凑数造假测试（对应 dispatch-context 约束 5、P2-design.md §4
完成标准表 BDD-9 行）。

### BDD-6：判据取自 P2-design.md §4 完成标准表而非 P1 原文

P1 原文写"exit 0"，但 P2-design.md §4 完成标准表逐条判据行明确写"继续既有流程最终
`return 2`"——因为 `gate_p8()` 现状代码在任何全量合规场景下都以
`"GATE P8: 脚本化检查通过...仍需主 Agent..."` + `return 2` 收尾，从不返回纯 0。本测试
按 P2-design.md 具体判据断言 `exit 2`（而非重复 P1 抽象原文的 exit 0），符合
dispatch-context 约束 1"断言到函数/命令级、不是重复 BDD 原文"的要求。该分支当前
**已是绿灯**（现状代码对无匹配 roadmap 场景的行为与新增判据要求的行为一致，因为
"无匹配不拦截"本就是现状默认行为），如实标注，不强行拗成红灯。

### BDD-13 第③类（源码数 6>5）现状说明：三类历史回归锚点均可能已是绿灯

BDD-13 的判据是"TAG0019 三类历史错误用例在写时即被拦截"。逐一核实现状代码：

1. **coupling_checklist 非列表声明**：`agate-frontmatter-check.py` 现状 `_check()` 已对
   `coupling_checklist` 做 `types["coupling_checklist"] = list` 类型校验，非列表值已被
   拦截——**非本任务新增能力**。
2. **半角冒号误写全角冒号（FIND-5）**：现状 `_extract_frontmatter_block`/`yaml.safe_load`
   已把此类单行标量判为非 dict 并报错——**非本任务新增能力**。
3. **源码数 6>5**：`check-routing.py` 现状已复用 `check-pruning._staged_source_count()`
   + `agate-risk-score.py.score_task()` 做"声明 thin 但算分 tier 非 thin"判定（与
   BDD-9〔check-routing 自身历史 BDD 编号，非本任务〕同族既有判据）——**非本任务新增
   能力**。

三条底层检测机制均已在现状代码中实现，本任务 RM-AG0045 的真正新增交付是
**dispatch-prompt.md 的"写时自检"挂载动作**（把"跑这些既有脚本"的时机从"等
pre-commit hook 触发"提前到"subagent 返回前主动跑"），而不是重新实现这三类检测逻辑
本身（P2-design.md §2.4 候选 A 的选择理由）。因此 §2.1 实测中，这 3 个 BDD-13 测试
函数当前均落在"285 passed"里，是**如实的绿灯**，不是遗漏或造假；本文件如实报告，
不隐瞒也不强行改造断言使其表现为假红灯。BDD-13 的红灯性质完全由 BDD-11（写时自检
小节文本尚未挂载）承载并已确认真红灯。

### BDD-4 / BDD-1 分支②③ / BDD-2 回归分支 / BDD-3 回归分支：当前即为绿灯的规则性说明

这些是"无事件/事件已妥善记录 retries"的回归防呆分支。在当前"新校验函数尚未实现"的
状态下，主脚本对这些输入的行为本来就是 exit 0 且无 WARNING/无拦截（没有新代码去误
触发），因此这些分支测试从写下的第一天起就是绿灯——这是回归防呆用例应有的性质（防止
未来实现引入误报），不代表遗漏了红灯设计。真正验证"新功能已实现"的红灯断言集中在
BDD-1 分支①、BDD-2 阻断分支、BDD-3 命中分支、BDD-5、BDD-7、BDD-8、BDD-10、BDD-11、
BDD-12 共 9 个测试函数（对应 §2.1 表格的 10 个失败用例，BDD-12 贡献 2 个）。

## 4. 自检结论

- [x] 13 条 BDD 全部有对应处理（12 条产出 pytest 测试用例，BDD-9 为占位声明说明由 P6 覆盖）
- [x] 真红灯已确认：10 个失败均为断言失败（B 类），非语法错误/项目外 import 失败（A 类）；
      未见任何 `SyntaxError`/`ModuleNotFoundError`/`ImportError` 堆栈
- [x] `test_code_dir: agate/tests/unit/` 已声明，13 条 BDD → 测试函数 → 所在文件映射表见 §1
- [x] 全量回归确认未破坏既有测试（1224 passed，较改动前 +1，因修复了测试自身的 encoding
      书写问题使既有 encoding 检查测试保持绿灯；除新增的 10 个红灯外无其他失败）
- [x] 非本任务应交付的检测能力（BDD-13 三类历史机制）已如实标注现状为绿灯，未虚构红灯
