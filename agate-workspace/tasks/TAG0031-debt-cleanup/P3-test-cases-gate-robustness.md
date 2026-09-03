---
phase: P3
task_id: TAG0031
parent: P2-design.md
trace_id: TAG0031-P3-gate-robustness-20260904
agent: test-designer
created: '2026-09-04'
---

test_code_dir: agate/tests/unit/test_check_gate.py

## 范围声明

本文件是 TAG0031「DEBT 存量修复批」P3 阶段三簇并行拆批之一——**gate-robustness**（check-gate.py
健壮性，DEBT0016/17/18），覆盖 BDD-8~15。只负责本簇范围；版本管理域（DEBT0002/3/4）与测试隔离
（DEBT0007）由另外两个 test-designer subagent 并行产出各自的 P3-test-cases-*.md，不在本文件重复。

测试代码全部追加在既有文件 `agate/tests/unit/test_check_gate.py`（新增 "8k: TAG0031 P3
gate-robustness 簇" 章节，位于 gate_p1 judge 三态测试段之后），未新建测试文件——BDD-15
的六条 DEBT 聚合检查虽是"收尾"性质，仍按约束写入同一文件（约束节明确"测试代码：
agate/tests/unit/test_check_gate.py（既有文件），新增用例插入位置参照其组织方式"）。

## 测试技术选型说明

- **BDD-8 / BDD-12（4 个子用例）**：白盒直连手法。用 `importlib.util.spec_from_file_location`
  把 `check-gate.py` 直接加载为独立模块对象（`_load_check_gate_direct`，每次调用返回全新模块，
  测试间互不污染），再 monkeypatch 模块级函数名（`resolve_workspace` / `read_rules_yaml` /
  `count_p6_pass_fail` / `count_p7_markers` / `count_code_map_lines`），直接调用
  `gate_p1`/`gate_p4`/`gate_p6`/`gate_p7`。
  - BDD-8 选择这条路径的原因：要验证的是"gate_p4 是否真的调用并使用了 resolve_workspace 的
    返回值"这一实现机制本身——标准两级嵌套场景下新旧路径算术结果恰好相同，纯黑盒行为无法区分
    两者，必须靠依赖注入（redirect `resolve_workspace` 到一个可观测的不同位置）才能证明。
  - BDD-12 选择这条路径的原因：要模拟"agate_common 整体不可导入"，但 `check-gate.py` 与同目录
    的 `agate-md-field-get.py` 等辅助脚本是 subprocess 协作关系，把脚本复制到隔离目录会连带
    破坏这些协作点，不是该场景的正确模拟手段——直接把四个消费函数替换为 ImportError 降级 stub
    的返回值（`None`/`(0,0)`/`0`），等价于"agate_common 不可导入时这些名字在 check-gate.py
    命名空间里的实际取值"，是更直接、更不脆弱的模拟。
- **BDD-9/10/11/13/15**：黑盒 CLI 子进程手法（`_run_gate`，同本文件既有风格），因为这些场景测
  的是端到端可观察行为（非标准嵌套下真实 `.agate.env` 解析结果 / 标题判定的最终文案 / 六条
  debt 登记条目 status 字段），黑盒验证更贴近用户可观察契约、也更稳健。

## BDD → 测试用例映射

| BDD | DEBT | 类型 | 测试函数 | 技术手法 | P3 现状 |
|---|---|---|---|---|---|
| BDD-8 | DEBT0016 | 正常流 | `test_tag0031_bdd_8_gate_p4_code_map_uses_resolve_workspace` | 白盒直连 + monkeypatch `resolve_workspace` | 红（AssertionError） |
| BDD-9 | DEBT0016 | 边界流 | `test_tag0031_bdd_9_gate_p4_non_standard_nesting_resolves_via_agate_env` | 黑盒 CLI，真实 `.agate.env` | 红（AssertionError） |
| BDD-10 | DEBT0017 | 异常流（原假阴性） | `test_tag0031_bdd_10_gate_p4_self_referential_prose_not_matched` | 黑盒 CLI | 红（AssertionError） |
| BDD-11 | DEBT0017 | 正常流（防假阳性回归） | `test_tag0031_bdd_11_gate_p4_real_heading_trailing_text_satisfied` | 黑盒 CLI | 绿（回归守卫，设计如此） |
| BDD-12 | DEBT0018 | 异常流 | `test_tag0031_bdd_12_gate_p1_read_rules_yaml_missing_fail_closed` | 白盒直连 + monkeypatch `read_rules_yaml` | 红（AssertionError） |
| BDD-12 | DEBT0018 | 异常流 | `test_tag0031_bdd_12_gate_p6_count_pass_fail_missing_fail_closed` | 白盒直连 + monkeypatch `count_p6_pass_fail` | 红（AssertionError，消息断言） |
| BDD-12 | DEBT0018 | 异常流 | `test_tag0031_bdd_12_gate_p7_count_markers_missing_fail_closed` | 白盒直连 + monkeypatch `count_p7_markers` | 红（AssertionError） |
| BDD-12 | DEBT0018 | 异常流 | `test_tag0031_bdd_12_gate_p7_count_code_map_lines_missing_fail_closed` | 白盒直连 + monkeypatch `count_code_map_lines` | 红（AssertionError） |
| BDD-13 | DEBT0018 | 回归 | `test_tag0031_bdd_13_gate_p6_p7_new_format_unaffected_regression` | 黑盒 CLI，新格式 frontmatter | 绿（回归守卫，设计如此） |
| BDD-14 | 同类扫描 | 登记动作 | 无自动化测试 | 见下方「BDD-14 说明」 | 不适用 |
| BDD-15 | 六条 DEBT 聚合 | 登记闭合 | `test_tag0031_bdd_15_six_debts_registry_closed` | 黑盒，读 `debt/tech-debt.md` | 红（AssertionError，六条均 open） |

共 10 个测试函数（BDD-8/9/10/11/12×4/13/15），8 红 2 绿，2 个私有辅助函数
（`_load_check_gate_direct` / `_tag0031_debt_block`）。

## 逐条用例详情

### BDD-8：gate_p4 CODE-MAP 路径改用 resolve_workspace（正常流）

- Given：task_dir 处于标准两级嵌套（`{repo}/agate-workspace/tasks/T001`）——本地
  `dirname(dirname(task_dir))` 算术与 `resolve_workspace` 默认解析结果本会重合，纯黑盒无法
  区分"用了权威函数"还是"巧合算对了"。
- 手法：monkeypatch 模块级 `resolve_workspace` 返回一个"重定向" workspace（与本地算术推导路径
  不同），只在重定向位置放 `CODE-MAP.md`，本地算术位置刻意留空。
- Then：期望 gate_p4 真调用 `resolve_workspace` 并使用其返回值 → 在重定向位置找到文件 → 触发
  「新增文件核对表」WARNING（exit 0，非阻断）。
- 现状：gate_p4 未 import/调用 `resolve_workspace`，两处都找不到文件 → 无 WARNING → 红。

### BDD-9：非标准两级嵌套场景下路径解析仍正确（边界流）

- Given：`{repo}/.agate.env` 声明 `AGATE_WORKSPACE=custom-ws`，task_dir 只在 `{repo}/task`
  一级（不满足 `{workspace}/tasks/{task_id}` 两级嵌套约定）。本地算术会推导到 repo 的父目录
  （repo 外部）；权威 `resolve_workspace` 能正确识别 `.agate.env` 覆盖。
- Then：期望在 `{repo}/custom-ws/agents/CODE-MAP.md` 找到文件并触发 WARNING。
- 现状：本地算术推导到 repo 外部，找不到文件 → 无 WARNING → 红。
- **R3 边界遵循**：只覆盖"非标准嵌套 + agate_common 可用"，未覆盖"agate_common 不可用"的组合
  场景（P2-design.md §1.3 R3 明确此组合超出本次范围）。

### BDD-10：自指场景下说明性文字不再被误判为已满足（异常流，原假阴性）

- Given：P4-implementation.md 用叙述文本提及"新增了一个标题叫『## 新增文件核对表』的小节"，
  该字符串以散文形式出现，非独立成行的标题。
- Then：期望判定为未满足，触发 WARNING。
- 现状：子串 `in` 判定命中散文里的字面子串 → 判定为已满足 → 无 WARNING → 红。

### BDD-11：标题真实存在时判定通过（正常流，防假阳性回归）

- Given：P4-implementation.md 含独立成行的「## 新增文件核对表」标题，行尾附加额外说明文字
  （验证 `re.MULTILINE` 行首匹配 `^##\s+新增文件核对表` 不要求标题后必须无内容）。
- Then：判定为已满足，不触发 WARNING。
- 现状：子串判定本就能命中 → 现状即绿（回归守卫，P4 改为整行/标题级正则后须继续保持绿）。

### BDD-12：agate_common 不可导入时关键读取器显式失败（异常流，4 个子用例）

DEBT0018 evidence 点名的 4 个"关键读取器"消费点，每个消费点一个测试：

1. **`read_rules_yaml`（gate_p1）**：无条件调用点（不像另外三个只在旧格式回退分支触达，见
   P2-design.md §1.3 R2），作为主力用例。stub 返回 `None` → 现状 `isinstance(cutoff, str)` 为
   False → 整段 judge 强制校验被跳过 → gate_p1 继续走到 exit 2（PASS）→ 与期望的 exit 1 不符 → 红。
2. **`count_p6_pass_fail`（gate_p6）**：**必须构造旧格式** P6-acceptance.md（frontmatter 无
   `pass`/`fail` 字段）才能命中降级哨兵分支（R2 风险，新格式下该函数根本不会被调用，见 BDD-13）。
   stub 返回 `(0, 0)` → 现状 `total == 0` 恰好也会 `return 1`（exit code 巧合撞对），但输出消息
   是通用的「GATE P6: FAIL=0, TOTAL=0」，不含「安装破损」字样——测试断言消息内容而非仅断言
   exit code，正确暴露"exit code 巧合正确但语义缺失"的红灯。
3. **`count_p7_markers`（gate_p7，BLOCKER/DEVIATION 计数）**：**旧格式** P7-consistency.md
   （无 `blocker_count`/`deviation_critical_count` 字段）。stub 返回 `(0, 0)` → 现状不触发该处
   return，继续走到函数末尾 `return 0`（真正的静默 false-PASS）→ 红。
4. **`count_code_map_lines`（gate_p7，CODE-MAP 转抄核对）**：**注意与另外两个消费点相反**——
   代码实际读取显示该调用点只在 `code_map_new_files_count`/`code_map_reviewed_count`
   frontmatter 字段**均已声明**（"机制已采用"）时才会被调用（check-gate.py:1212-1245），不是
   "旧格式回退"。构造 `cm_reviewed(2) >= cm_count(2)` 使内部一致性层先行通过、不提前 return，
   再命中转抄核对层。stub 返回 `0` → `0 > 2` 为 False → 落到函数末尾 `return 0`（false-PASS）→ 红。

### BDD-13：agate_common 正常可导入时行为逐字节不变（回归）

- Given：真实 CLI 子进程（不 monkeypatch），P6/P7 均用新格式 frontmatter 声明计数字段。
- Then：判定结果与改造前逐字节一致（P6 exit 2 PASS，P7 exit 0 PASS）。
- 现状：新格式快速路径本就不经过四个降级消费点，本用例即绿（regression baseline）。P4 完成
  fail-closed 改造后须继续保持绿——这是本 BDD 的核心诉求（防止改造误伤新格式路径），故本用例
  设计为"现状绿、改造后仍须绿"的回归安全网，不是传统 TDD 红灯用例。

### BDD-14：同类未处理实例登记为新 DEBT（登记动作，非代码断言）

按 dispatch-context 指引，本 BDD 是 P8 阶段的登记动作（在 `debt/tech-debt.md` 新增 ≥2 条 open
DEBT 条目：① `task_dir` 类路径推导非本体 2 处——`check-retrospective.py:74` /
`agate-render-dispatch-prompt.py:191`；② 标题字符串子串判定同款、风险更高的
`check-gate.py:881` gate_p2 bootstrap 骨架声明校验），不是代码行为，P3 不写自动化测试。验证方式：
P6 阶段核对 `debt/tech-debt.md` 是否新增了这 2 条 open 条目（人工/P6-acceptance.md 记录）；P8
阶段完成登记动作本身。

### BDD-15：六条 DEBT 登记条目闭合（跨簇聚合收尾检查）

- 归属本簇（gate-robustness）——三簇（version-mgmt / test-isolation / gate-robustness）中本簇
  最后完成，是收尾聚合检查的天然位置（P3-dispatch-context-test-designer-gate-robustness.md
  §约束 明确指派）。
- 检查 `debt/tech-debt.md` 中 DEBT0002/0003/0004/0016/0017/0018 六个 ID 的 `status:` 字段。
  DEBT0007 单独由 `test_debt_registry_closure.py` 的
  `test_bdd_7_debt0007_status_closed_with_closure_fields` 覆盖，不在本用例范围内（避免重复
  断言同一条目）。
- 现状：六条均为 `open` → 本用例预期全部 FAIL（真红灯）。收尾登记完成后六条均改为 `closed`，
  本用例转绿。
- 等价 grep 命令模板（人工核对用）：
  ```bash
  grep -A3 '^## DEBT0002$\|^## DEBT0003$\|^## DEBT0004$\|^## DEBT0016$\|^## DEBT0017$\|^## DEBT0018$' \
    agate-workspace/debt/tech-debt.md | grep 'status:'
  ```

## 实测红灯确认

```
python3 -m pytest agate/tests/unit/test_check_gate.py -q
```

结果：**8 failed, 184 passed**（2026-09-04 本 worktree 实测）。

- 8 个失败：`test_tag0031_bdd_8_*` / `test_tag0031_bdd_9_*` / `test_tag0031_bdd_10_*` /
  `test_tag0031_bdd_12_*`（4 个）/ `test_tag0031_bdd_15_*`，全部为 **AssertionError**（B 类：
  断言不符预期，非 SyntaxError/ImportError），逐条核对失败信息均指向"当前实现未做 fail-closed /
  未调用 resolve_workspace / 判定仍为子串匹配"，不是测试代码自身的错误。
- 2 个预期绿（设计如此，非遗漏）：`test_tag0031_bdd_11_*`（标题真实存在场景，子串判定本就能
  命中，属回归守卫）、`test_tag0031_bdd_13_*`（新格式 frontmatter 路径不经过四个降级消费点，
  本就不受影响，属回归守卫）。
- 184 个既有测试全部保持绿，无回归；`--collect-only` 确认全部 192 个测试可正常收集（无语法
  错误）。

## 与 P2-design.md 风险声明的对照

- **R2（旧格式回退分支限制）**：BDD-12 的 `count_p6_pass_fail`/`count_p7_markers` 两个用例
  均显式构造旧格式 fixture（frontmatter 无对应计数字段）命中降级哨兵分支；`count_code_map_lines`
  经代码实读确认实际是"字段已声明才调用"（与另外两个相反），已在用例详情节标注差异并按代码
  实况构造 fixture，未machinery 照搬文档字面表述导致假绿。`read_rules_yaml` 无条件调用，构造
  最直接，作为主力用例。
- **R3（resolve_workspace 双依赖降级路径）**：BDD-9 只覆盖"非标准嵌套 + agate_common 可用"，
  未扩大到"agate_common 不可用"的组合场景（超出本次范围，写了也不算错但非必须，本次未写）。
