---
phase: P3
task_id: TAG0024
type: test-cases
parent: P2-design.md
trace_id: TAG0024-P3-20260825
status: draft
created: 2026-08-25
agent: test-designer
---

> 本文件是 3 个并行批次（P2-design.md dispatch_plan：`md-field-set-tool` / `check-gate-debt-fixes` /
> `phases-yaml-consistency`）测试用例说明的合并汇总，由主 Agent 做轻量拼装（拼接各批次产出，
> 无跨批次交叉修改）。三批次分工与合并语义详见各自 dispatch-context 文件；各批次的完整测试
> 用例清单/断言细节/自跑红灯记录保留在各自的 `P3-test-cases-{batch-id}.md` 中，本文件只做
> 顶层索引 + 统一字段声明。

## test_code_dir

```yaml
test_code_dir: agate/tests/unit/
```

三批次测试代码分布（零文件交叉，P2-review.md 已核验）：
- `agate/tests/unit/test_agate_md_field_set.py`（新建，批次 `md-field-set-tool`）
- `agate/tests/unit/test_check_gate.py`（既有文件追加，批次 `check-gate-debt-fixes`）
- `agate/tests/unit/test_check_structure_consistency.py`（既有文件追加，批次 `phases-yaml-consistency`）

## BDD 覆盖索引（全局 29 条，1:1 映射，无遗漏）

| BDD 范围 | 批次 | 测试文件 | 说明文档 |
|---|---|---|---|
| BDD-1~19（RM-AG0048 一期） | md-field-set-tool | test_agate_md_field_set.py | P3-test-cases-md-field-set-tool.md |
| BDD-20~24（DEBT0019/20） | check-gate-debt-fixes | test_check_gate.py | P3-test-cases-check-gate-debt-fixes.md |
| BDD-25~28（RM-AG0049/50） | phases-yaml-consistency | test_check_structure_consistency.py | P3-test-cases-phases-yaml-consistency.md |
| BDD-29（跨 issue 约束） | phases-yaml-consistency（文档归属） | 无自动化测试——P7 阶段 diff 逐行核对验收 | P3-test-cases-phases-yaml-consistency.md |

## 全量红灯汇总（主 Agent 独立复核，非采信各批次自述）

主 Agent 已对三批次产出逐一独立重跑并核实：

- **批次 md-field-set-tool**：`test_agate_md_field_set.py` 全部 35 个测试项（19 条 BDD，其中
  BDD-8/9/15/18 参数化）**全部 FAILED**，失败原因均为被测脚本文件不存在（subprocess "can't
  open file" 或 importlib `FileNotFoundError`）——B 类真红灯，无 SyntaxError 等 A 类假红灯。
- **批次 check-gate-debt-fixes**：新增 BDD-20/22/23 共 3 个测试项 **FAILED**（AssertionError，
  B 类真红灯）；BDD-21（3 组参数化）+ BDD-24 共 4 个测试项 **PASSED**（回归守卫用例，验证
  既有合法场景判定结果不变，语义上要求恒真，非红灯覆盖对象）；全量重跑
  `test_check_gate.py`（`--basetemp=.pytest-tmp -p no:cacheprovider -q`）→ 182 项中
  3 failed / 179 passed，既有全部用例保持绿色，`git diff --stat` 确认纯追加（156 行新增，
  0 删除）。
- **批次 phases-yaml-consistency**：新增 BDD-25/27 共 2 个测试项 **FAILED**（AssertionError，
  B 类真红灯）；BDD-26/28 共 2 个测试项 **PASSED**（回归守卫用例）；全量重跑
  `test_check_structure_consistency.py` → 17 项中 2 failed / 15 passed，既有全部用例保持绿色，
  `git diff --stat` 确认纯追加（168 行新增，0 删除）。

三批次互不干扰：`git status --short agate/tests/unit/` 确认只涉及上表列出的三个文件，无交叉
修改；`check_agate_md_field_set.py` 为新建（untracked），另两个为既有文件修改（modified）。

## 各批次完整清单

详见：
- `P3-test-cases-md-field-set-tool.md`
- `P3-test-cases-check-gate-debt-fixes.md`
- `P3-test-cases-phases-yaml-consistency.md`
