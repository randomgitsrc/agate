---
phase: P4
task_id: TAG0007
type: implementation
parent: P2-design.md
trace_id: TAG0007-P4-20260820
status: draft
created: 2026-08-20
agent: implementer
---
implementation_dir: agate/

## 总览

本文件汇总 4 个并行批次（`skeleton-docs` / `code-map-docs` / `gate-script-both` /
`dogfood-bootstrap`）已完成的实现，覆盖 P1-requirements.md 的全部 11 条 BDD（RM-AG0008 骨架
BDD-1~5 + RM-AG0009 CODE-MAP BDD-6~11）。4 批文件集合两两不相交（`git status --porcelain`
已确认无跨批文件重叠、无非预期改动），可全部并行派发并合并。本文件本身按批次分节，逐字转抄
`gate-script-both` 批次的 2 条 `[DESIGN_GAP:]` 标记（见该节）。

## 批次一：skeleton-docs（骨架机制文档层）

### 改动文件清单

| 文件 | 改动 | 关联 BDD |
|------|------|----------|
| `agate/phase-cards/P1-requirements.md`（L81-83 附近，`change_type: refactor` 注释样例后） | 新增可选字段注释样例 `project_phase: bootstrap`（枚举 bootstrap / established，缺省 established，向后兼容），仿照 `change_type` 注释样例风格 | BDD-1/3 |
| `agate/phase-cards/P2-design.md`「产出规格」节（UI 设计节段落之后、候选方案简化之前） | 新增「骨架产出」条件产出规格说明：`project_phase: bootstrap` 时 P2 architect 需额外产出 task 目录下 `P2-skeleton.md`（须含 `## 骨架声明` 标题） | BDD-1/2 |
| `agate/assets/execution-roles/architect.md`「输出」节 P2 部分（UI 设计节 checklist 之后、`gate_commands:` 之前） | 新增「骨架设计职责」段落：0→1 任务时 architect 产出 `P2-skeleton.md`，须用「候选目录集合 + 项目侧声明」参数化形式，不写死具体语言/框架目录名，模板指向 `assets/templates/skeleton-template.md` | BDD-1/2 |
| `agate/assets/templates/skeleton-template.md`（新建） | 骨架模板：五类候选目录（源码/测试/文档/构建/部署）以抽象类别标签表达 + 项目侧技术栈声明填空区；不含黑名单硬编码目录名（`src/components`/`src/include`/`src/hooks`/`src/pages`），含参数化关键词「候选目录」「技术栈」 | BDD-2 |

### 自查测试结果

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

### 范围核对

`git status --porcelain` 确认本批次仅改动/新增以下 4 个文件（均在批次约束清单内）：
- `agate/phase-cards/P1-requirements.md`
- `agate/phase-cards/P2-design.md`
- `agate/assets/execution-roles/architect.md`
- `agate/assets/templates/skeleton-template.md`（新建）

### DESIGN_GAP / SCOPE+ / CLARIFY

无。P2-design.md §1.1/§2.2 对本批次四个文件的改动点、插入位置、字段名/枚举值、模板黑名单/关键词
均已给出精确规格，无需自主决策补缺口。

## 批次二：code-map-docs（CODE-MAP 机制文档层）

### 本批次范围

CODE-MAP 机制文档层实现，让 `agate/tests/unit/test_code_map_template.py` 的 2 个红灯测试变绿
（未改动测试文件本身）。

### 改动文件清单

| 文件 | 改动内容 | 关联 BDD |
|------|---------|---------|
| `agate/phase-cards/P4-implementation.md` | 在「产出规格」节后新增「新增文件核对表」小节：implementer 为每个新增文件填一行——骨架归属列（`within <dir>` / `[SKELETON_DEVIATION: 理由]`）+ CODE-MAP 处理列（`[CODE_MAP_UPDATED]` / `[CODE_MAP_EXEMPT: 理由]`），末尾追加 `change_type: refactor` 同样适用本表的说明。标题逐字为 `## 新增文件核对表` | BDD-4/7/10 |
| `agate/phase-cards/P7-consistency.md` | frontmatter 可直接复制样例新增两个可选字段 `code_map_new_files_count`（对应 `design_gap_count` 语义）/ `code_map_reviewed_count`（对应 `design_gap_reviewed_count` 语义），与既有 DESIGN_GAP 两字段并列展示在同一 YAML 代码块；「执行方式」检查清单新增第 5 条：CODE-MAP 核对（对照 `agents/CODE-MAP.md` 与 P4 新增文件核对表，偏离标 `[CODE_MAP_DRIFT:]` WARNING 不阻断，通过标 `[CODE_MAP_SYNC:]`） | BDD-6/8/9 |
| `agate/assets/execution-roles/consistency-reviewer.md` | 「检查清单」节新增第 5 条职责段落：CODE-MAP 核对——对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 记录与 P4「新增文件核对表」实际新增文件，逐条判定同步（`[CODE_MAP_SYNC:]`）/偏离（`[CODE_MAP_DRIFT:]`），人工判断不做跨语言静态依赖分析（ADR-003 合规） | BDD-8/9 |
| `agate/assets/templates/code-map-template.md`（新建） | CODE-MAP 模板：含五个必填字段标题（模块/层/依赖方向/关键文件/约定），每节含占位声明说明用途，供 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 初始化时参照 | BDD-6 |
| `agate/WORKFLOW.md` | 「工作区目录规范」`agents/` 行追加一句：也承载 `CODE-MAP.md`（项目架构全貌维护物，非任务产出，不新增第 10 个固定子目录） | BDD-6 |

### 自查测试结果

```
$ timeout 60s python3 -m pytest agate/tests/unit/test_code_map_template.py -v
agate/tests/unit/test_code_map_template.py::test_bdd_6_code_map_template_exists PASSED
agate/tests/unit/test_code_map_template.py::test_bdd_6_code_map_template_has_five_required_headings PASSED
2 passed in 0.02s
```

2 个测试由红灯（AssertionError，模板文件不存在）变为绿灯（PASSED），测试文件本身未改动。

### 范围核对

`git status --porcelain` 确认本批次只涉及上表 5 个文件（含 1 个新建）。其余同一 worktree 下出现的
改动（`architect.md`、`P1-requirements.md`、`P2-design.md`、`P2-skeleton.md` 等）属并行的
`skeleton-docs`/`gate-script-both`/`dogfood-bootstrap` 批次，未触碰。未碰
`agate/scripts/check-gate.py`、`{AGATE_WORKSPACE}/agents/CODE-MAP.md`、任何 `tests/unit/test_*.py`。

### DESIGN_GAP / SCOPE+ / CLARIFY

无。P2-design.md §1.1/§2.3/§3 对本批次涉及的字段名、标题文字、判定逻辑归属（本批次只写文档说明，
不实现 gate 判定逻辑）已给出精确规格，实现按规格逐条对应，未需自主决策填补歧义。

## 批次三：gate-script-both（两机制共享的 check-gate.py 判定实现）

### 改动范围

只改动 `agate/scripts/check-gate.py`，在 `gate_p2`/`gate_p4`/`gate_p7` 三个函数内新增判定分支。
未改动测试文件、未改动其他函数、未改动任何 `.md` 文档/`CODE-MAP.md`。

### 1. gate_p2（BDD-1/3）

插入位置：`_gate_p2_ui_design_section` 检查通过之后、最终 `sys.stderr.write(...) + return 2` 之前
（`gate_p2` 函数末尾）。

逻辑：
- 用既有 `_frontmatter_field(p1_file, "project_phase")` 读取 P1-requirements.md 的
  `project_phase` 字段。
- `project_phase == "bootstrap"`：检查 `task_dir/P2-skeleton.md` 是否存在且文本含
  `"## 骨架声明"`。缺失或缺标题 → `sys.stderr.write(...)` 含 `"P2-skeleton.md"` 字样，
  `return 1`。存在且含标题 → 不拦截，继续走到原有 `return 2`。
- `project_phase` 缺失或非 `"bootstrap"`（含显式 `"established"`）：完全跳过该分支，不产生任何
  `"P2-skeleton.md"` 相关输出（回归对照）。

关联 BDD：BDD-1（bootstrap 骨架声明校验）、BDD-3（字段缺失/established 回归无变化）。

### 2. gate_p4（BDD-4/7/10）

在现有"暂存区含代码文件 → return 0 / 否则 return 1"逻辑基础上重构为：先扫描暂存区判定
`has_code_file`（无代码文件仍 `return 1`，行为不变），有代码文件时不再立即 `return 0`，而是先做
WARNING 检查，再统一 `return 0`（exit code 行为不变，WARNING 不阻断）。

WARNING 触发条件（AND）：
1. 暂存区含代码文件（已判定）
2. `task_dir/P2-skeleton.md` 存在 **或** `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在（OR 条件，
   骨架/CODE-MAP 机制已采用）
3. `task_dir/P4-implementation.md` 正文不含 `"## 新增文件核对表"` 标题

满足则 `sys.stderr.write(...)` 含 `"WARNING"` 与 `"新增文件核对表"` 字样，`return 0`（不阻断）。
判定逻辑完全不读取/不分支 `change_type` 字段（BDD-10：`change_type: refactor` 任务同样触发，不
豁免）。

`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 路径解析见下方 DESIGN_GAP。

关联 BDD：BDD-4/7（WARNING 机制）、BDD-10（refactor 不豁免）。

### 3. gate_p7（BDD-8/9/10）

插入位置：现有 DESIGN_GAP pairing 检查段（含 N3 review 实质锚点 WARNING）之后、函数末尾
`return 0` 之前，作为并行独立检查段，不与 DESIGN_GAP 逻辑共享变量。

读取 P7-consistency.md frontmatter 的 `code_map_new_files_count` / `code_map_reviewed_count`
（读取方式见下方 DESIGN_GAP，非字面照搬 `_md_field_get`）。

- 两字段均缺失 → 机制未采用，两层校验全部跳过，不触发任何 `"CODE_MAP"` 相关输出（回归对照）。
- 两字段均存在时，跑两层校验：
  - **内部一致性层**：`code_map_reviewed_count < code_map_new_files_count` →
    `sys.stderr.write(...)` 含 `"CODE_MAP"`，`return 1`（仿照 `dg_reviewed < dg_count` 分支）。
  - **转抄核对层**：正则数 `P4-implementation.md` 正文中 `[CODE_MAP_UPDATED]` /
    `[CODE_MAP_EXEMPT` 两种标记的实际出现次数（`r"^\s*-?\s*\[CODE_MAP_UPDATED\]"` /
    `r"^\s*-?\s*\[CODE_MAP_EXEMPT"`），若该计数 **>** `code_map_new_files_count`（不是
    `code_map_reviewed_count`）→ `sys.stderr.write(...)` 含 `"CODE_MAP"`，`return 1`。
  - 两层均通过 → 不拦截，继续原有流程直到函数末尾 `return 0`。
- `change_type` 字段完全不读取、不分支（BDD-10：两层校验对 refactor 任务同样生效）。

关联 BDD：BDD-8/9（两层 pairing 硬校验）、BDD-10（refactor 不豁免）。

### DESIGN_GAP 声明

[DESIGN_GAP: dispatch-context 建议 gate_p7 用 `_md_field_get` 读取 `code_map_new_files_count`/`code_map_reviewed_count`（与既有 `design_gap_count` 读取方式一致），但 `agate-md-field-get.py` 的 `KNOWN_OPS` 允许列表尚未注册这两个新字段名，且该文件不在本批次允许改动范围内（只能改 `check-gate.py`）——若照字面调用 `_md_field_get`，子进程会因 unknown op `sys.exit(2)`，`_md_field_get` 恒回退为空字符串，导致两层校验永远被判定为"机制未采用"而跳过，会使 3 个 gate_p7 新增测试失败。改为使用本文件已有的纯本地函数 `_frontmatter_field(path, field)`（同文件内定义，无子进程/无 allowlist 限制）直接从 P7-consistency.md frontmatter 块取值，行为等价（frontmatter-only、无正文回退语义，因为 `_frontmatter_field` 本身只扫描 `---` 块内的行，不会误读正文散文）。若后续有其他改动把这两个字段注册进 `agate-md-field-get.py` 的 `NO_FALLBACK_INT_FIELDS`，可切回 `_md_field_get` 以保持代码风格统一，非阻塞项。]

[DESIGN_GAP: `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 的路径解析方式 P2-design.md 未给出函数级精确规格（dispatch-context 已明确指出这是本批次需自主决策的空间，P3 测试只覆盖 `P2-skeleton.md` 分支）。本实现采用 dispatch-context 建议的推导方式：`task_dir` 通常形如 `{AGATE_WORKSPACE}/tasks/{Txxx}`，从 `task_dir` 向上两级到 workspace 根，再拼接 `agents/CODE-MAP.md`——即 `os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(task_dir))), "agents", "CODE-MAP.md")`。此推导依赖"task_dir 是 `{AGATE_WORKSPACE}/tasks/{Txxx}` 的两级嵌套"这一约定，若与项目实际工作区解析机制（`agate_common.py` 的 `_resolve_workspace` 或 `.agate.env`）不一致（例如 workspace 根不由目录层级推导，而是显式配置/环境变量），需要后续对齐为读取同一权威解析源，而不是本地重新推导路径。测试套件未覆盖此分支（仅覆盖 `P2-skeleton.md` OR 条件的另一侧），因此该风险在当前测试下不可见，需人工/主 Agent 确认是否与实际部署布局相符。]

### 自查测试结果

- 12 个新增测试全部 PASSED：
  - `test_bdd_1_bootstrap_missing_skeleton_exit_1`
  - `test_bdd_1_bootstrap_with_skeleton_title_exit_2`
  - `test_bdd_3_field_missing_no_regression_exit_2`
  - `test_bdd_3_established_explicit_no_regression_exit_2`
  - `test_bdd_4_7_gate_p4_warning_when_table_missing`
  - `test_bdd_4_7_gate_p4_no_warning_when_table_present`
  - `test_bdd_8_9_gate_p7_internal_consistency_mismatch_exit_1`
  - `test_bdd_8_9_gate_p7_transcription_mismatch_exit_1`
  - `test_bdd_8_9_gate_p7_paired_matches_exit_0`
  - `test_bdd_8_9_gate_p7_mechanism_not_adopted_no_check`
  - `test_bdd_10_gate_p4_refactor_not_exempt_warning`
  - `test_bdd_10_gate_p7_refactor_not_exempt_pairing_check`
- 既有测试无回归：`agate/tests/unit/test_check_gate.py` 全量 159 passed（0 failed）；
  `agate/tests/unit` 全量 gate 相关用例（`-k "check_gate or check-gate or gate"`）898 passed,
  2 skipped（既有 skip，与本次改动无关）。
- `git status --porcelain agate/scripts/` 确认只改动 `check-gate.py` 一个文件。

（本文件为自查记录，不代表 P5 gate 已通过。）

## 批次四：dogfood-bootstrap（agate 自身 CODE-MAP.md 初始化，超出 implementation_dir 范围）

> 说明：本批次产出文件 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（即本 worktree 的
> `agate-workspace/agents/CODE-MAP.md`）不在 `implementation_dir: agate/` 范围内，单独在此列出，
> 不影响 `implementation_dir` 字段本身的声明（参照 TAG0017 同类协议任务先例）。

### 产出摘要

新建 `{AGATE_WORKSPACE}/agents/CODE-MAP.md`（本 worktree 的 `agate-workspace/agents/CODE-MAP.md`，
`agents/` 目录此前不存在，已创建），为 agate 协议本体自身初始化 CODE-MAP dogfooding 实例——BDD-6
「CODE-MAP 存在性」的验收对象。

内容按 P2-design.md §1.1 表格最后一行 + dispatch-context 约束 2 的字段清单，五类必填字段
（模块 / 层 / 依赖方向 / 关键文件 / 约定）均填真实内容，描述 agate 协议本体的实际架构：

- **模块**：phase-cards（9 张阶段卡片）/ execution-roles（7 个执行角色）/ review-roles（10 个
  评审角色）/ scripts（gate/一致性/状态三大脚本家族 + 编排辅助脚本）/ templates（模板文件，
  含协作批次新增的 `code-map-template.md`）。
- **层**：协议流程层（phase-cards）→ 角色层（execution-roles + review-roles）→ 工具层
  （scripts）→ 模板层（templates），逐层说明各层职责与消费关系。
- **依赖方向**：phase-cards 松耦合不依赖角色/脚本实现细节；scripts 消费 phase-cards/templates
  声明的字段名做判定（举例 `check-gate.py` 的 `gate_p7` 读 `code_map_new_files_count` 等字段）；
  execution-roles/review-roles 消费 phase-cards 声明的职责边界，不反向定义流程；明确禁止反向
  依赖。
- **关键文件**：WORKFLOW.md / dispatch-protocol.md / state-machine.md / role-system.md /
  check-gate.py，各自一句话职责说明。
- **约定**：新增机制需经 P0-P8 完整流程不可裁剪、改协议脚本走 TDD、改协议文档/脚本/卡片触发
  SELF-GATE 自审。

标题层级采用 `##`（模块/层/依赖方向/关键文件/约定），与 `code-map-template.md` 的标题结构一致
（dispatch-context 允许不强制完全一致，本批次选择对齐以便对照阅读）。

内容中模块/角色/脚本/模板的数目（7 个执行角色、10 个评审角色、9 张阶段卡片）已实地 `ls` 核对，
非猜测填写；`code-map-template.md` 已存在（另一并行批次 `code-map-docs` 的产出物），本批次只读取
参照其标题结构，未做任何修改。

### 关联 BDD

- BDD-6：`{AGATE_WORKSPACE}/agents/CODE-MAP.md` 存在，含模块/层/依赖方向/关键文件/约定五类
  字段——本文件即该验收对象，供 P6 acceptance 人工核对存在性。

### 自查记录

```
$ test -f agate-workspace/agents/CODE-MAP.md && echo EXISTS_OK
EXISTS_OK
$ grep -c "模块\|层\|依赖方向\|关键文件\|约定" agate-workspace/agents/CODE-MAP.md
15
```
五字段名（模块/层/依赖方向/关键文件/约定）均出现在文件中（含正文引用，不止标题行）。

### 范围确认

本批次只产出 `agate-workspace/agents/CODE-MAP.md` 一个文件，未触碰其他三个并行批次
（skeleton-docs / code-map-docs / gate-script-both）范围内的任何文件。

### DESIGN_GAP / SCOPE+ / CLARIFY

无。

## BDD 覆盖核对（对照 P2-design.md §1.1 + P1-requirements.md 11 条 BDD）

| BDD | 内容摘要 | 覆盖批次 |
|-----|---------|---------|
| BDD-1 | 0→1 项目产出骨架的存在性 | skeleton-docs（字段+产出规格+模板）、gate-script-both（gate_p2 校验） |
| BDD-2 | 骨架模板技术栈参数化，不硬编码 | skeleton-docs（skeleton-template.md + 回归测试） |
| BDD-3 | 骨架机制不对已有结构项目重复触发 | skeleton-docs（缺省 established）、gate-script-both（gate_p2 字段缺失/established 回归） |
| BDD-4 | 后续产出物落在骨架声明目录内，偏离可追溯 | code-map-docs（P4 新增文件核对表）、gate-script-both（gate_p4 WARNING） |
| BDD-5 | 骨架机制实现改动不破坏现有回归基线 | gate-script-both（`test_check_gate.py` 159 passed 无回归）+ 全量回归（见文末） |
| BDD-6 | CODE-MAP 维护物的存在与初始化 | code-map-docs（模板+WORKFLOW.md 说明）、dogfood-bootstrap（实例文件） |
| BDD-7 | P4 新增文件触发 CODE-MAP 更新义务 | code-map-docs（核对表 CODE-MAP 处理列）、gate-script-both（gate_p4 WARNING） |
| BDD-8 | P7 一致性检查核对 CODE-MAP 与实际文件同步偏离 | code-map-docs（P7 frontmatter 字段+consistency-reviewer.md）、gate-script-both（gate_p7 内部一致性层） |
| BDD-9 | 依赖方向偏离检测产生可见信号，不允许静默通过 | code-map-docs（`[CODE_MAP_SYNC:]`/`[CODE_MAP_DRIFT:]` 标记）、gate-script-both（gate_p7 转抄核对层） |
| BDD-10 | change_type: refactor 任务不豁免 CODE-MAP 更新义务 | code-map-docs（核对表末尾豁免声明）、gate-script-both（gate_p4/gate_p7 均不读 change_type） |
| BDD-11 | CODE-MAP 机制实现改动不破坏现有回归基线 | gate-script-both（`test_check_gate.py`/gate 相关用例无回归）+ 全量回归（见文末） |

11 条 BDD 均在 4 批改动中找到对应；BDD-5/BDD-11（回归拦截类 BDD）未在 P2-design.md §1.1 中单列
专属文件行（P1-requirements.md 已声明其"属新增测试拦截范畴"，通过全量回归测试是否通过来体现，
非某一个文件的改动点），已在上表以"全量回归"方式覆盖，与 P1/P2 对这两条 BDD 的定性一致。

## 全量回归结果（主 Agent 已跑，未重新执行）

`python3 -m pytest agate/tests/ -q --tb=line` → 1028 passed, 2 skipped, 0 failed（1011 基线 + 17
新增 = 1028，与 P3 阶段确认的用例总数吻合）；`python3 agate/scripts/check-protocol-consistency.py`
→ 0 ERROR（316 WARNING）；`shellcheck -S warning agate/scripts/*.sh` → 0 error；
`bash agate/tests/scripts/count-tests.sh` → 1030 个测试用例（含 2 skipped）；4 批全部完成后
`git status --porcelain` 确认无跨批文件重叠、无非预期改动。
