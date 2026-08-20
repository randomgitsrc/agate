---
phase: P4
task_id: TAG0007
type: implementation
parent: P2-design.md
trace_id: TAG0007-P4-code-map-docs-20260820
status: draft
created: 2026-08-20
agent: implementer
---
implementation_dir: agate/

## 本批次范围

`code-map-docs`（P2-design.md §7 四批并行之一）：CODE-MAP 机制文档层实现，让
`agate/tests/unit/test_code_map_template.py` 的 2 个红灯测试变绿（未改动测试文件本身）。

## 改动文件清单

| 文件 | 改动内容 | 关联 BDD |
|------|---------|---------|
| `agate/phase-cards/P4-implementation.md` | 在「产出规格」节后新增「新增文件核对表」小节：implementer 为每个新增文件填一行——骨架归属列（`within <dir>` / `[SKELETON_DEVIATION: 理由]`）+ CODE-MAP 处理列（`[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT: 理由]`），末尾追加 `change_type: refactor` 同样适用本表的说明。标题逐字为 `## 新增文件核对表` | BDD-4/7/10 |
| `agate/phase-cards/P7-consistency.md` | frontmatter 可直接复制样例新增两个可选字段 `code_map_new_files_count`（对应 `design_gap_count` 语义）/ `code_map_reviewed_count`（对应 `design_gap_reviewed_count` 语义），与既有 DESIGN_GAP 两字段并列展示在同一 YAML 代码块；「执行方式」检查清单新增第 5 条：CODE-MAP 核对（对照 `agents/CODE-MAP.md` 与 P4 新增文件核对表，偏离标 `[CODE_MAP_DRIFT:]` WARNING 不阻断，通过标 `[CODE_MAP_SYNC:]`） | BDD-6/8/9 |
| `agate/assets/execution-roles/consistency-reviewer.md` | 「检查清单」节新增第 5 条职责段落：CODE-MAP 核对——对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 记录与 P4「新增文件核对表」实际新增文件，逐条判定同步（`[CODE_MAP_SYNC:]`）/偏离（`[CODE_MAP_DRIFT:]`），人工判断不做跨语言静态依赖分析（ADR-003 合规） | BDD-8/9 |
| `agate/assets/templates/code-map-template.md`（新建） | CODE-MAP 模板：含五个必填字段标题（模块/层/依赖方向/关键文件/约定），每节含占位声明说明用途，供 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 初始化时参照 | BDD-6 |
| `agate/WORKFLOW.md` | 「工作区目录规范」`agents/` 行追加一句：也承载 `CODE-MAP.md`（项目架构全貌维护物，非任务产出，不新增第 10 个固定子目录） | BDD-6 |

## 自查测试结果

```
$ timeout 60s python3 -m pytest agate/tests/unit/test_code_map_template.py -v
agate/tests/unit/test_code_map_template.py::test_bdd_6_code_map_template_exists PASSED
agate/tests/unit/test_code_map_template.py::test_bdd_6_code_map_template_has_five_required_headings PASSED
2 passed in 0.02s
```

2 个测试由红灯（AssertionError，模板文件不存在）变为绿灯（PASSED），测试文件本身未改动。

## 范围核对

`git status --porcelain` 确认本批次只涉及上表 5 个文件（含 1 个新建）。其余同一 worktree 下出现的
改动（`architect.md`、`P1-requirements.md`、`P2-design.md`、`P2-skeleton.md` 等）属并行的
`skeleton-docs`/`gate-script-both`/`dogfood-bootstrap` 批次，未触碰。未碰
`agate/scripts/check-gate.py`、`{AGATE_WORKSPACE}/agents/CODE-MAP.md`、任何 `tests/unit/test_*.py`。

## DESIGN_GAP 声明

无。P2-design.md §1.1/§2.3/§3 对本批次涉及的字段名、标题文字、判定逻辑归属（本批次只写文档说明，
不实现 gate 判定逻辑）已给出精确规格，实现按规格逐条对应，未需自主决策填补歧义。
