---
phase: P4
task_id: TAG0007
type: implementation
parent: P2-design.md
trace_id: TAG0007-P4-skeleton-docs-20260820
status: draft
created: 2026-08-20
agent: implementer
---
implementation_dir: agate/

## 改动文件清单

| 文件 | 改动 | 关联 BDD |
|------|------|----------|
| `agate/phase-cards/P1-requirements.md`（L81-83 附近，`change_type: refactor` 注释样例后） | 新增可选字段注释样例 `project_phase: bootstrap`（枚举 bootstrap / established，缺省 established，向后兼容），仿照 `change_type` 注释样例风格 | BDD-1/3 |
| `agate/phase-cards/P2-design.md`「产出规格」节（UI 设计节段落之后、候选方案简化之前） | 新增「骨架产出」条件产出规格说明：`project_phase: bootstrap` 时 P2 architect 需额外产出 task 目录下 `P2-skeleton.md`（须含 `## 骨架声明` 标题） | BDD-1/2 |
| `agate/assets/execution-roles/architect.md`「输出」节 P2 部分（UI 设计节 checklist 之后、`gate_commands:` 之前） | 新增「骨架设计职责」段落：0→1 任务时 architect 产出 `P2-skeleton.md`，须用「候选目录集合 + 项目侧声明」参数化形式，不写死具体语言/框架目录名，模板指向 `assets/templates/skeleton-template.md` | BDD-1/2 |
| `agate/assets/templates/skeleton-template.md`（新建） | 骨架模板：五类候选目录（源码/测试/文档/构建/部署）以抽象类别标签表达 + 项目侧技术栈声明填空区；不含黑名单硬编码目录名（`src/components`/`src/include`/`src/hooks`/`src/pages`），含参数化关键词「候选目录」「技术栈」 | BDD-2 |

## 自查测试结果

```bash
timeout 60s python3 -m pytest agate/tests/unit/test_skeleton_template_stack_neutral.py -v
```

```
test_bdd_2_skeleton_template_exists PASSED
test_bdd_2_skeleton_template_no_hardcoded_stack_dirs PASSED
test_bdd_2_skeleton_template_has_parameterization_markers PASSED
3 passed in 0.02s
```

3 个测试由红灯（AssertionError：文件不存在）全部变绿灯（PASSED）。未修改测试文件本身。

## 范围核对

`git status --porcelain` 确认本批次仅改动/新增以下 4 个文件（均在批次约束清单内）：
- `agate/phase-cards/P1-requirements.md`
- `agate/phase-cards/P2-design.md`
- `agate/assets/execution-roles/architect.md`
- `agate/assets/templates/skeleton-template.md`（新建）

工作树中同时存在其他并行批次（code-map-docs / gate-script-both / dogfood-bootstrap）产生的
未暂存改动（`agate/WORKFLOW.md`、`consistency-reviewer.md`、`P4-implementation.md`、
`P7-consistency.md`、`code-map-template.md` 等），均非本批次改动，未触碰。

未发现 DESIGN_GAP：P2-design.md §1.1/§2.2 对本批次四个文件的改动点、插入位置、字段名/枚举值、
模板黑名单/关键词均已给出精确规格，无需自主决策补缺口。
