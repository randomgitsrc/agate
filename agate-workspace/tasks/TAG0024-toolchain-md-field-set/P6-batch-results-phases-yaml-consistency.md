---
phase: P6-evidence
task_id: TAG0024
batch: phases-yaml-consistency
type: evidence-results
created: 2026-08-25
agent: verifier
---

# P6 证据批次结果：phases-yaml-consistency（BDD-25~29）

本文件为证据并行批次产出，**非最终 P6-acceptance.md**。供汇总 verifier 转抄整合。

## 逐条结果

- PASS BDD-25: `agate/rules/phases.yaml` 中 `id: P4` 条目的 `outputs` 列表现已包含
  `{file: P4-review.md, required: true, status_field: status}`，`test_bdd_25_p4_outputs_includes_review_md`
  单独执行 PASSED（P3 阶段记录的红灯已由 P4 实现修复转绿）(bdd-25-pytest.log)
- PASS BDD-26: 补全后的 `phases.yaml` 跑真实 `check-structure-consistency.py` 二进制，
  S-1~S-6 双向一致性检查 exit code 0，未因 P4-review.md 声明产生新的不一致报错，
  `test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix` 单独执行 PASSED (bdd-26-pytest.log)
- PASS BDD-27: `agate/rules/phases.yaml` 中 `- id: P6.5` 条目前的注释块与 `agate/state-machine.md`
  对 P6.5 性质的文字定位口径一致（均表达"P6.5 是挂载于 P6→P7 转移的强门槛子阶段，非独立
  `.state.yaml` phase 值"），`test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording`
  单独执行 PASSED（P3 阶段记录的红灯已由 P4 实现修复转绿）(bdd-27-pytest.log)
- PASS BDD-28: 口径统一后（纯注释改动）① `phases.yaml` 中 `P6.5` 条目 `yaml.safe_load` 解析结果
  字段值与补丁前逐一相等（注释对 YAML 解析器不可见）；② `check-gate.py P6.5 $TASK_DIR` 与
  `check-judge-verdict.py` 在真实仓库根 / 补丁后协议树副本两种环境下 exit code 均为 0 且
  stderr 逐字节相同，既有判定行为（`.state.yaml phase` 字段语义、事件账本记录、judge 复核轮次
  预算计数方式）不变，`test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior`
  单独执行 PASSED (bdd-28-pytest.log)
- PASS BDD-29: 对本任务 P4 commit `e2357fc` 的 diff 逐行核对，`agate/scripts/check-gate.py`
  的改动范围仅限于：新增常量 `_ROADMAP_EXPECTED_COLS = 9`（DEBT0019 列数精确匹配）、
  `_check_roadmap_done()` 内 `len(cols) < 8` 改为 `len(cols) != _ROADMAP_EXPECTED_COLS`
  （DEBT0019 精确匹配修复）、`gate_p8()` 内 `roadmap_path` 从 CWD 相对拼接改为
  `git rev-parse --show-toplevel` 仓库根锚定并对非 git 仓库环境增加 stderr 提示
  （DEBT0020 修复）——三处改动均落在 dispatch-context 圈定的
  `_check_roadmap_done()`/`gate_p8()` 中 `roadmap_path` 定位相关行范围内，未触及其他判定逻辑；
  `agate/scripts/check-events.py` 在整条任务分支（`main..HEAD`）上 `git diff` 输出为空，
  零改动。核对命令与完整 diff 输出见证据文件 (bdd-29-diff.log)

## 交叉核对（本批次内部）

- P1-requirements.md BDD-25~29 共 5 条，本批次结果覆盖 BDD-25/26/27/28/29 共 5 条，PASS 5 / FAIL 0，
  编号无重复无遗漏。
- BDD-25/26/27/28 证据来源：`agate/tests/unit/test_check_structure_consistency.py` 对应测试函数单独执行
  （非仅引用 P3 阶段自跑记录，本次为 P6 重新独立实跑）。
- BDD-29 证据来源：`git show e2357fc -- agate/scripts/check-gate.py` + `git diff main..HEAD -- agate/scripts/check-gate.py`
  + `git diff main..HEAD -- agate/scripts/check-events.py`（跨全部任务提交范围核对，未局限于本批次改动）实际命令输出。

## 证据文件清单

| 文件 | 对应 BDD | 内容 |
|---|---|---|
| bdd-25-pytest.log | BDD-25 | `test_bdd_25_p4_outputs_includes_review_md` 单测执行输出 + EXIT_CODE |
| bdd-26-pytest.log | BDD-26 | `test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix` 单测执行输出 + EXIT_CODE |
| bdd-27-pytest.log | BDD-27 | `test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording` 单测执行输出 + EXIT_CODE |
| bdd-28-pytest.log | BDD-28 | `test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior` 单测执行输出 + EXIT_CODE |
| bdd-29-diff.log | BDD-29 | `git show e2357fc`（check-gate.py 完整 diff）+ 全任务分支 `check-gate.py`/`check-events.py` diff 核对输出 |

**Summary**: PASS 5 / FAIL 0（BDD-25~29 全覆盖）
