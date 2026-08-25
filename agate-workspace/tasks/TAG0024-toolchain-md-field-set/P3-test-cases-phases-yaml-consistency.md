---
phase: P3
task_id: TAG0024
type: test-cases
parent: P2-design.md
trace_id: TAG0024-P3-phases-yaml-consistency-20260825
status: draft
created: 2026-08-25
agent: test-designer
---

## 步骤 3 判断结果（先行声明）

`agate/tests/unit/test_check_structure_consistency.py` **已存在**（覆盖 S-1~S-6 双向一致性，
含 TAG0021 M0 基线用例与 TAG0022 增补的 S-3a/S-3b 用例）。本批次判断：**追加到该文件**，
不新建文件。理由：

1. P2-design.md §1.1 改动落点表第 41 行已明确指定"`test_check_structure_consistency.py`
   （若存在，否则于既有 S-3 测试文件追加）"，且已确认该文件真实存在。
2. dispatch-context 的约束节同样明确指向本文件，且已声明"RM-AG0049 相关用例全部落地于
   本文件，不再分散到 test_check_gate.py"。
3. 本文件已有 S-1/S-2/S-3(a/b) 的完整测试基础设施（`make_fake_root` 假协议树 + `run_cli` +
   `agate_scripts`/`python_exe` 等共享 fixture），BDD-25/26 直接复用同一被测脚本
   `check-structure-consistency.py`，追加到同文件符合测试组织惯例（同被测对象同文件）。

**追加位置的特殊说明**：BDD-25~28 断言的对象是**真实仓库文件**
（`agate/rules/phases.yaml` + `agate/state-machine.md` 的当前/补丁后内容），而非既有用例使用的
`make_fake_root` 最小假协议树——因为本次要验证的是"真实文件当前是否已补全 / 补丁后是否引入
新不一致"，不是脚本抽象行为。因此新增用例改用 `conftest.py` 会话级 `agate_root` fixture
（解析到本仓库 `agate/` 目录）直接驱动，与既有假协议树用例风格不同但共存于同一文件、
互不影响（已用回归跑确认既有 13 条用例全部保持 PASSED）。

## 测试用例清单

测试代码文件：`agate/tests/unit/test_check_structure_consistency.py`（追加，第 227-395 行区域，
本批次新增 4 个测试函数 + 4 个共享 helper）。

| BDD | 测试函数 | 断言什么 |
|---|---|---|
| BDD-25 | `test_bdd_25_p4_outputs_includes_review_md` | 真实 `agate/rules/phases.yaml` 用 `yaml.safe_load` 解析后，`id: P4` 的 `outputs` 列表中包含 `{file: P4-review.md, required: true, status_field: status}`；当前真实文件未补全该条目，断言真实失败（红灯） |
| BDD-26 | `test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix` | 把 RM-AG0049（P4 outputs 补全）+ RM-AG0050（P6.5 注释）两处修复打到真实协议树的临时副本（`rules`/`WORKFLOW.md`/`phase-cards`/`scripts`/`assets` 全部拷贝真实内容，仅 `phases.yaml` 换成补丁版），跑真实 `check-structure-consistency.py` 二进制，断言 exit code == 0（S-1~S-6 全量 0 mismatch）；回归守卫性质，当前即为绿（P2-design §1.3 风险 5 已用静态 grep 论证过，本用例改用真实脚本调用坐实证据） |
| BDD-27 | `test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording` | 真实 `phases.yaml` 中 `- id: P6.5` 条目前紧邻的注释块须同时含"强门槛子阶段"与"非独立/不是……独立"与"phase"字样，口径与 `state-machine.md` 第 74-78/152-155 行既有表述对齐；当前真实文件该条目前无任何注释，断言真实失败（红灯）。同时对 `state-machine.md` 侧做控制组断言（应已为真，确认对照锚点未漂移） |
| BDD-28 | `test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior` | 两层断言：① 补丁前后 `yaml.safe_load` 解析出的 `P6.5` 条目字段值逐一相等（证明纯注释改动对 YAML 解析器不可见）；② 用 `task_dir` fixture 构造 judge 未启用的历史任务，分别以 `AGATE_ROOT=真实仓库根` / `AGATE_ROOT=补丁后协议树副本` 两种环境跑 `check-gate.py P6.5 $TASK_DIR`，断言两次 exit code 均为 0 且 stderr 逐字节相同（既有判定行为不变，回归守卫性质，当前即为绿——`gate_p65()` 本就不读取 `phases.yaml`/`AGATE_ROOT`，只读 `task_dir/.state.yaml`） |
| BDD-29 | 无自动化测试函数（见下） | RM-AG0048 不改变 `check-gate.py`/`check-events.py` 判定逻辑——判定方式为**审查全部改动的 diff**，跨越本任务全部代码改动面（不局限于本批次涉及的 phases.yaml/state-machine.md），非某个具体函数的行为断言，写成单测会退化为"重新断言 diff 里没有出现某些字符串"这类脆弱字符串匹配，价值有限且容易漏判真实的逻辑变更。按 dispatch-context 建议，**本条以 P7 一致性检查阶段对 `check-gate.py`/`check-events.py` 的 diff 逐行核对方式验收**，不算测试缺口。 |

## 自跑结果（红灯确认）

命令：`python3 -m pytest agate/tests/unit/test_check_structure_consistency.py -v --basetemp=.pytest-tmp -p no:cacheprovider`

- `test_bdd_25_p4_outputs_includes_review_md` → **FAILED**（AssertionError，真红灯 B 类：真实
  `phases.yaml` P4 outputs 目前只有 `P4-implementation.md`，非测试代码 bug）
- `test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording` → **FAILED**（AssertionError，
  真红灯 B 类：真实 `phases.yaml` P6.5 条目前当前无任何注释，`comment_block` 为空字符串）
- `test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix` → PASSED（回归守卫，符合预期）
- `test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior` → PASSED（回归守卫，符合预期）
- 既有 13 条用例（`test_bdd_2_*`/`test_bdd_3_*`/`test_bdd_5_*` 系列）全部保持 **PASSED**，
  未受本次追加影响（同一文件跑一次全量确认：17 items，15 passed / 2 failed，失败即上述两条真红灯）

## 已知边界

- BDD-26/28 的"回归守卫"性质已在 dispatch-context 中预先声明（非新增检查逻辑），故它们当前
  即为绿属预期行为，不违反"新增用例应在当前 phases.yaml 未修复情况下断言失败"的通则——该通则
  对 BDD-25/27 这两条真正引入新断言目标的用例适用，已确认为真红灯；BDD-26/28 是"验证修复不
  引入回归"的性质，语义上要求本就应该恒真。
- 未跑全仓 `agate/tests/` 全量回归的其余批次红灯（`test_agate_md_field_set.py` 全部失败、
  `test_check_gate.py` 的 BDD-20/22/23 失败）：确认为**另外两个并行批次**（`md-field-set-tool`
  / `check-gate-debt-fixes`）各自的红灯产出，与本批次无关，已用 `git diff --stat` 核实本次改动
  只涉及 `agate/tests/unit/test_check_structure_consistency.py` 一个文件。
