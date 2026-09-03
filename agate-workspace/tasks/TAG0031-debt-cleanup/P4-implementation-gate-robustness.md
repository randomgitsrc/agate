---
phase: P4
task_id: TAG0031
parent: P3-test-cases-gate-robustness.md
trace_id: TAG0031-P4-gate-robustness-20260904
agent: implementer
created: '2026-09-04'
---

implementation_dir: agate/scripts/

## 范围声明

本文件是 TAG0031「DEBT 存量修复批」P4 阶段三簇并行拆批之一——**gate-robustness**（check-gate.py
健壮性，DEBT0016/17/18）。只改动 `agate/scripts/check-gate.py`，未触碰其他两簇文件
（`agate-install.py`/`agate-pack-offline.py`/`install-offline.py`/`check-pruning.py`/
`agate_common.py` 本体），也未触碰 `agate-workspace/debt/tech-debt.md`（六条 DEBT 登记闭合由
主 Agent 三簇返回后统一处理）。

## 改动清单

代码文件：`agate/scripts/check-gate.py`（唯一改动文件，无新增文件）

### DEBT0016：gate_p4 CODE-MAP.md 路径改用 resolve_workspace 权威解析

- 顶部 import 块（原 L42-46）追加 `resolve_workspace`：
  `from agate_common import read_vision_tri_state, resolve_workspace, run_git`；ImportError
  分支追加 `resolve_workspace = None`。
- gate_p4（原 L985-987）：project_root 优先取
  `run_git(["rev-parse", "--show-toplevel"], cwd=task_dir)` 的 git 顶层；`run_git` 不可用/失败
  时退化为本地 `dirname(dirname(task_dir))` 算术值，仅作 `resolve_workspace` 的入参兜底
  （`resolve_workspace` 内部按 `project_root/.agate.env` 覆盖解析，找不到该文件时走默认
  `{project_root}/agate-workspace` 规则，不因入参不够精确而报错）。`resolve_workspace` 本身
  不可用（`agate_common` 整体不可导入，与 `run_git` 同一 import 块，生产环境下二者必然同生共死）
  时才整体回退旧算术。本分支保持 WARNING-only（不 `return 1`）——不是 DEBT0018 evidence 点名的
  4 个"关键读取器"之一，fail-open 语义与既有 WARNING 一致（P2-design.md §1.3 R3）。

### DEBT0017：gate_p4「新增文件核对表」判定改为整行/标题级正则

- gate_p4 判定语句由 `"## 新增文件核对表" not in _read_text(p4_impl_check)` 改为
  `not re.search(r"^##\s+新增文件核对表", _read_text(p4_impl_check), re.MULTILINE)`（参照
  `agate_common.py` `extract_bdd_titles`/`parse_ui_design_section` 的 `re.MULTILINE` 行首匹配
  写法风格）。消除自指/dogfooding 场景下散文提及标题字面量被子串判定误判为"标题已存在"的假阳性；
  标题行尾允许附加说明文字（只要求行首匹配，不要求标题后无内容）。

### DEBT0018：4 个"关键读取器"消费点 fail-closed

- 新增辅助函数 `_reader_missing(fn)`（`_read_text` 函数前）：判定当前绑定的 `fn.__module__`
  是否等于 `"agate_common"`——是则视为可信的真实实现，否则（ImportError 降级 stub / 任何非
  agate_common 来源的替换）视为不可信，触发 fail-closed。选择"调用时刻的 `__module__` 身份判定"
  而非"一次性 import 期布尔标记"，是因为白盒测试通过 `mod.count_p7_markers = lambda ...` 等
  方式在模块 `exec_module` 完成后重新绑定函数名对象——一次性标记在模块 exec 那一刻就已固定，
  无法感知之后的重新绑定；且实测发现同一 pytest 会话内因跨测试文件/测试执行顺序导致 `sys.path`
  被污染（其他测试用 `sys.path.insert` 使 `agate/scripts` 变为可导入），会让"是否发生过
  ImportError"这一次性判定在同一进程内变得不确定。身份判定在每次调用时刻重新核验，不受这些
  副作用影响，对生产环境（真实 agate_common 导入成功/失败二选一，不会中途变化）和测试环境
  （monkeypatch 替换）均给出正确结果。
- 4 个消费点各自在使用返回值前先判 `_reader_missing(fn)`：
  - `gate_p1`（原 L687，read_rules_yaml，无条件调用点）：`_reader_missing(read_rules_yaml)` →
    `sys.stderr.write("GATE P1: 安装破损：agate_common 不可导入，无法读取 rules/dispatch.yaml
    判定 judge_required_since 门槛\n"); return 1`。
  - `gate_p6`（原 L1084，count_p6_pass_fail，仅旧格式回退分支触达）：
    `_reader_missing(count_p6_pass_fail)` →
    `sys.stderr.write("GATE P6: 安装破损：agate_common 不可导入，无法读取 PASS/FAIL 计数\n");
    return 1`。
  - `gate_p7`（原 L1144，count_p7_markers，仅旧格式回退分支触达）：
    `_reader_missing(count_p7_markers)` →
    `sys.stderr.write("GATE P7: 安装破损：agate_common 不可导入，无法读取
    BLOCKER/DEVIATION-CRITICAL 计数\n"); return 1`。
  - `gate_p7`（原 L1238，count_code_map_lines，注意与前三者相反——只在
    `code_map_new_files_count`/`code_map_reviewed_count` 字段均已声明时才触达，不是旧格式回退）：
    `_reader_missing(count_code_map_lines)` →
    `sys.stderr.write("GATE P7: 安装破损：agate_common 不可导入，无法读取 CODE-MAP 转抄标记
    计数\n"); return 1`。
- 其余 20+ 个降级 stub（`count_design_gap`/`reconcile_*`/`parse_gate_commands_block` 等）不改动，
  维持既有 fail-open 语义（不在 DEBT0018 evidence 点名范围内，P2-design.md §1.3）。

## 新增文件核对表

本簇改动仅修改既有文件 `agate/scripts/check-gate.py`，**未新增任何文件**（与 P2-design.md
预期一致）。本节按规范声明为空。

## 自查结果（自查 ≠ P5 gate）

```
timeout 120 python3 -m pytest agate/tests/unit/test_check_gate.py -v
```

结果：**191 passed, 1 failed**。

- 8 个真红灯测试全部转绿：`test_tag0031_bdd_8_gate_p4_code_map_uses_resolve_workspace` /
  `test_tag0031_bdd_9_gate_p4_non_standard_nesting_resolves_via_agate_env` /
  `test_tag0031_bdd_10_gate_p4_self_referential_prose_not_matched` /
  `test_tag0031_bdd_12_gate_p1_read_rules_yaml_missing_fail_closed` /
  `test_tag0031_bdd_12_gate_p6_count_pass_fail_missing_fail_closed` /
  `test_tag0031_bdd_12_gate_p7_count_markers_missing_fail_closed` /
  `test_tag0031_bdd_12_gate_p7_count_code_map_lines_missing_fail_closed`（此列 7 个 + BDD-8 共 8 个）。
- 2 个回归守卫测试保持绿：`test_tag0031_bdd_11_gate_p4_real_heading_trailing_text_satisfied`、
  `test_tag0031_bdd_13_gate_p6_p7_new_format_unaffected_regression`。
- 唯一 1 个失败：`test_tag0031_bdd_15_six_debts_registry_closed`（预期红——检查
  `debt/tech-debt.md` 六条 DEBT status 字段，本簇 dispatch-context 明确指派"实现阶段不需要你去
  改 tech-debt.md"，由主 Agent 三簇返回后统一登记闭合，不在本簇自查范围内）。
- 184 个既有测试全部保持绿，无回归。

补充跑了一次仓库全量测试（`agate/tests/`，非本簇 gate 要求，仅供参考）：1454 passed, 2 skipped,
3 failed。3 个失败分别是本簇预期的 `test_tag0031_bdd_15_six_debts_registry_closed`、其他簇同样
指向 `debt/tech-debt.md` 待主 Agent 统一登记的 `test_bdd_7_debt0007_status_closed_with_closure_fields`
（DEBT0007，test-isolation 簇范围）、以及 version-mgmt 簇 `install-offline.py`（非本簇改动文件）
触发的 ruff 格式检查失败——均不在本簇改动范围/职责内，未做任何处理。

## 自检

- 代码改动确实产生 diff：`git diff --stat agate/scripts/check-gate.py` → 85 行改动
  （+80/-5 左右，含新增 `_reader_missing` 辅助函数 + 4 处消费点改造 + gate_p4 两处 DEBT0016/17）。
- 测试确实跑了且转绿，记录见上「自查结果」节。
- 全量 `test_check_gate.py` 无回归（184 个既有测试保持绿）。
