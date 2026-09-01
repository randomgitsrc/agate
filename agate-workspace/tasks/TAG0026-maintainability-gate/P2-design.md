---
phase: P2
task_id: TAG0026
type: design
parent: P1-requirements.md
trace_id: TAG0026-P2-20260830
status: draft
created: 2026-08-30
agent: architect
candidate_count: 3
packages: [agate-scripts, agate-tests, agate-phase-cards, agate-templates]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: serial}
---

# P2-design — TAG0026 维护性反模式 gate（RM-AG0046）方案设计

> parent: P1-requirements.md（13 条 BDD 验收对照物）｜落地计划：`docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（v3 定稿）｜设计地基：`docs/design-notes/design-maintainability-gate.md`（决策 1/2/3）
> 范围锁定 P1 基线：G0 两条 + P4 三重门槛 + 模板 + P4/P6 卡片自查 + 配置 + 测试。G1/G2/G3、RM-AG0022 结构化层联动、第八道 provenance 审计、门户、跨行移动检测一律不设计（P1 out-of-scope）。

## 1. 影响面梳理

> 证据基线：本节所有行号均来自 worktree 实际读取（2026-08-30），非凭印象罗列。

### 1.1 改什么（Modify）

| # | 文件 | 改动落点 | 关联 BDD | 证据 |
|---|------|---------|---------|------|
| M1 | `agate/scripts/check-maintainability.py` | **新增**。模块级函数 `check_maintainability(task_dir) -> dict`；内部 `_load_config(repo_root)` / `_god_file_check(...)` / `_fuzzy_boundary_check(...)` / CLI 薄壳 `main()`（exit code 唯一判定） | BDD-1/2/3/4/5/6/11/12/13 | P1 同类扫描已确认全仓无同名文件；形态参照 `agate-risk-score.py:202-279` 的 `score_task()` dict 返回形状 |
| M2 | `agate/scripts/check-gate.py` | `gate_p4()`（:870-927）**新增一步**：落在既有第④步「暂存区代码检查」（:893-905）之后、骨架/CODE-MAP WARNING（:907-925）之前；另在模块头 import 兜底区（:32-41 模式）加 `try: from check_maintainability import check_maintainability / except ImportError: None` | BDD-7/8/9/10 | gate_p4 现有结构实测：①review 存在→1 ②status 非 approved→1 ③agent 缺→2/main→1 ④staged 代码检查→1 ⑤骨架 WARNING 不阻断 ⑥return 0 |
| M3 | `agate/scripts/check-protocol-consistency.py` | `SCRIPT_ALIGNMENT_ANCHORS` 列表尾（:745-751 之后）**登记一条锚点**：`script="agate/scripts/check-maintainability.py"` + keywords + `callers=["agate/scripts/check-gate.py"]` | 隐含需求 10 | `check_anchor_coverage`（:797-830）遍历 `agate/scripts/check-*.py`，未登记且不在 `GATE_SCRIPT_EXEMPT`（:791-794）→ CHECK9-coverage WARNING |
| M4 | `agate/scripts/agate-summary.py` | `_DRIFT_SCRIPTS` 清单（:42-50）**追加一行** `"check-maintainability.py"` | 隐含需求 10 | 清单现有 7 项（check-tdd-red/check-gate/check-pruning/agate-risk-score/check-routing/check-judge-verdict/check-events） |
| M5 | `agate/assets/templates/known-violations-template.md` | **新增**。格式对齐 `known-failures-template.md`（:1-14，frontmatter + 语义边界引用块 + `\| N \|` 行首表格）但语义反转；样例行首用 `\| # \|`（不命中 `count_kf_entries` 的 `^\|\s*[0-9]+\s*\|` 计数，防照抄模板未改样例导致计数虚高） | BDD-7/8 隐含（计数对齐） | `count_kf_entries`（agate_common.py:1015-1017）只数行首数字列 |
| M6 | `agate/phase-cards/P4-implementation.md` | 「## 评审派发（C8 机械映射）」节末尾（:110「单评审角色时」段之后）**加一条评审 checklist 要求**；「## gate 规则（check-gate.py 会跑）」节（:140-148）**补一行 exit 1 条件** | 隐含需求 11、约束 14 | 实测该卡无既有 checklist 小节，评审节 :84-112 为改动落点 |
| M7 | `agate/phase-cards/P6-acceptance.md` | 「## 自查≠gate」节正文（:226-229）**加一句非阻断复跑提醒** | 隐含需求 11、约束 2 | 该节是卡片文末独立小节，实测 :226-229 |
| M8 | `agate-workspace/maintainability.yaml` | **新增**示例配置（默认阈值 + Python/TS 正则集 + "仅供参考可配置"注释） | BDD-5/6 | P1 同类扫描确认首次引入；路径对齐 ADR-009（不用 `.agate/`，隐含需求 5） |
| M9 | `agate/tests/unit/test_check_maintainability.py` | **新增**检测器单测（§5 分组） | BDD-1..6/11/12/13 | tests/README 按脚本分文件 `test_*.py` 惯例 |
| M10 | `agate/tests/unit/test_check_gate_p4_maintainability.py` | **新增** P4 挂载 gate 测试（§5 分组） | BDD-7/8/9/10 + 回归面 | 先例 `test_check_gate_p5_diff.py`（P5 diff 判定挂载测试） |

### 1.2 不改什么（Not Modify）

| 不改对象 | 理由（客观证据） |
|---------|----------------|
| `gate_p4` 既有四步的语义与顺序（:870-905） | 派发约束 4 + 隐含需求 1：`pre-commit-gate.py:349,362`、`ci-gate-backstop.py:24,26,154` 等消费方按返回约定 0/1/2 调用；新步骤只做**追加**（violations 为空时行为与现状逐字节等价） |
| `check-p6-provenance.py` 七道审计 | 计划 v3 §0 修正 B2：登记内容不进 provenance 审计，不新增第八道 |
| `gate_p5` known-failures 判定（:945-985） | 只复用 `count_kf_entries` 计数函数本体，不碰 P5 判定逻辑（P1 同类扫描第 2 行处理声明） |
| `check-gate.py` 的任何调用方（pre-commit-gate / ci-gate-backstop / check-judge-verdict / agate-summary 等，P1 同类扫描第 1 行全清单） | 改动收敛在 gate_p4 函数体内，调用契约（CLI 参数 + exit code）不变 |
| `check-pruning.py` / `_STAGED_EXCLUDE_RE`（check-gate.py:174） | 检测器自行取 staged 文件（按扩展名路由 .py/.ts/.tsx/.js/.jsx），md/state 文件天然不参与行数与正则判据，无需复用该排除模式 |
| ruff 配置（pyproject.toml:7，E7 含 E722 裸 except） | ruff 是静态 lint（全文件、非 diff 驱动），与 fuzzy-boundary（diff 新增行驱动、产出 violation 计数）互补不冲突（P1 同类扫描第 6 行），不宣称替代 |
| `known-failures-template.md` 本体 | known-violations 语义相反（自引入 vs 预存），不共享文件、不改既有模板 |
| 协议本体 WORKFLOW.md / rules/*.yaml | G0 机制条文承载在 P4/P6 卡片（M6/M7）+ 本设计文档链，不动协议主流程文件（避免范围蔓延与额外一致性面） |

### 1.3 风险在哪（Risk）

| # | 风险 | 缓解 |
|---|------|------|
| R1 | check-gate.py 是所有任务 P0-P8 总闸，P4 新增一步回归风险最高（P0-brief known_risks 第 1 条） | 新步骤以「violations 非空」为前置门；空场景行为与现状等价；回归拦截 = 全量 pytest + consistency 0 ERROR 硬门槛 + M10 专项测试含「无 violations 时既有返回值不变」用例 |
| R2 | import 失败面（agate_common / check_maintainability 不可导入） | 沿用 check-gate.py:32-41 既有 ImportError 降级先例：降级为 WARNING 不阻断（检测未部署 ≠ 判定缺失——gate_p4 ④步已阻断无 git 通道场景） |
| R3 | staged 文件状态边界（新增/修改/删除/重命名） | 用 `git diff --cached --name-status` 过滤：只处理 A/M，跳过 D；`git show :path` 失败（新增文件）→ before=0；HEAD 不存在（首次提交）→ before=0 |
| R4 | Windows 路径分隔符影响判定 | 复用 `_norm_rel`（agate-risk-score.py:86-88，反斜杠归一）单点，不第二实现（BDD-11、隐含需求 9） |
| R5 | fuzzy 正则误报（注释/字符串含 `any` 等词） | v1 诚实接受已知假阳性，靠 known-violations 登记吸收（BDD-12 同机制），不做 AST 级消歧（P0 out-of-scope） |
| R6 | consistency CHECK9-coverage WARNING（新 check-*.py 未登记锚点） | M3 锚点登记 + `callers` 字面核对对策：`check_script_alignment`（:771-785）按**字面 basename** 在 caller 文件找 `check-maintainability.py`——import 语句是裸模块名不含 `.py`，故 gate_p4 挂载处注释必须含字面 `check-maintainability.py`（如「加载 agate/scripts/check-maintainability.py」） |
| R7 | check-tdd-red 把 `P3*` 非元键当测试命令执行 | 实测 `agate-read-gate-commands.py:60`：`key.startswith("P3") and not is_gate_meta_key(key)` 的键**全部**被收集为测试命令——gate_commands **禁止声明任何 `P3_xxx` 检测命令键**（本设计只声明 `P3:` 运行器 + 非 P3 前缀的辅助键） |
| R8 | 模板样例行 `\| 1 \|` 被照抄后计入 `count_kf_entries` → 数量对齐虚高 | M5：样例行首用 `\| # \|`（不命中 `^\|\s*[0-9]+\s*\|`），登记人填真实行时自然替换为数字 |
| R9 | 阈值 N=1000 被误解为协议断言 | M8 配置注释 + 模板/文档明确「默认值仅供参考可配置」（P0-brief known_risks 第 3 条） |
| R10 | P5/P6 卡片 wording 引用 `check-maintainability.py` 时脚本尚未实现 → CHECK 10 引用漂移 | 卡片改动（M6/M7）与脚本实现（M1/M2）同属 P4 产出，P5 时脚本已存在；P5 跑 worktree 自己的 `check-protocol-consistency.py --strict-errors-only` 实测验证（§3.6） |

## 2. 候选方案

### 2.1 候选 A（选定）：importlib 单源复用 + gate_p4 内联三重门槛

`check-maintainability.py` 为独立检测脚本（对齐 agate-risk-score.py / check-pruning.py 的"每个检测关注点一个独立脚本"分层先例）：

- 复用链：`from agate_common import run_git, count_kf_entries`（ImportError 降级兜底，先例 check-gate.py:32-41）；`_load_script("agate-risk-score")`（importlib 模式，agate-risk-score.py:46-54 同源）加载后复用 `_norm_rel`——**不第二实现**路径归一化与 git 调用。
- `check-gate.py` 在模块头按既有模式 `try: from check_maintainability import check_maintainability / except ImportError: check_maintainability = None`，gate_p4 函数体内新增三重门槛步骤（伪代码见 §3.2），③（评审 approve）复用本函数既有 ①②③ 检查，不重复实现。
- 返回 dict 对齐 `score_task()` 形状：`{"git_ok": bool, "violations": [...], "god_file_count": N, "fuzzy_boundary_count": M}`。

优点：函数级返回值直读（无文本解析面）；单测可直接 import 断言；复用面最大（run_git/_load_script/_norm_rel/count_kf_entries 四点单源）；与协议「exit code 唯一判定 + dict 结构化返回」既有哲学同构。
风险：import 耦合（R2，有降级先例兜底）；gate_p4 函数体增长（可控，约 +25 行）。
工作量：低（复用为主，新逻辑集中在两个 check 函数 + 门槛步骤）。

### 2.2 候选 B（否决）：subprocess CLI 互调

`gate_p4` 用 `subprocess` 跑 `python3 check-maintainability.py TASK_DIR`，解析 stdout JSON 拿 violations。

优点：进程隔离，检测器崩溃不影响 check-gate；check-maintainability 可独立替换为项目自有工具。
缺点：引入文本解析面（JSON 解析错误处理分支多）；双解释器启动开销；Windows 解释器探测面（DEBT0014 同源问题）；单测必须走 subprocess（慢且脆）。**派发约束 5 明确禁止**（"不走 subprocess 解析文本"）。
否决理由：与约束直接冲突，且优势（隔离/可替换）对单一协议内置检测器无实际收益。

### 2.3 候选 C（否决）：检测逻辑下沉 agate_common.py

把 `check_maintainability` 逻辑直接写进 `agate_common.py` 共享库。

优点：单文件单点，import 最简单。
缺点：agate_common 是公共原语库（`import` 不执行，承载 write_gate_result/resolve_workspace 等机制函数），混入业务检测策略会把「检测什么反模式」耦合进库版本——策略一改就要动公共库，放大回归面；破坏既有分层先例（检测逻辑独立脚本：agate-risk-score.py / check-pruning.py / check-tdd-red.py 均独立，agate_common 只收共享原语）。
否决理由：分层先例与回归面权衡均不利；`count_kf_entries` 等原语已在 agate_common 单点，候选 A 已获得"原语单点"收益。

### 2.4 权衡与选择

| 维度 | A（选定） | B | C |
|------|-----------|---|---|
| 派发约束 5（禁 subprocess 文本解析） | ✓ | ✗ 冲突 | ✓ |
| 单测可达性 | 直接 import 断言 | 需 subprocess | 直接 import 断言 |
| 复用单源（run_git/_load_script/_norm_rel/count_kf_entries） | 四点全单源 | 检测器侧单源、gate 侧文本解析 | 同 A，但公共库被业务污染 |
| 回归面 | gate_p4 追加一步 | 双进程 + 解析面 | agate_common 全消费方 |
| 分层先例一致性 | ✓（检测独立脚本） | ✓ | ✗（打破先例） |

**选择候选 A**：唯一同时满足派发约束 5、协议 exit-code 判定哲学、分层先例与最小回归面的方案。B 在约束层面直接不可行；C 的分层代价无对等收益。

## 3. 选定方案设计细节

### 3.1 检测器 `check-maintainability.py`

模块 docstring 对齐计划 v3 §2.1。核心数据流：

```text
task_dir → run_git(rev-parse --show-toplevel, cwd=task_dir) → repo_root
        → run_git(diff --cached --name-status, cwd=task_dir) → 过滤 A/M、按扩展名路由
        → 配置 _load_config(repo_root)（agate-workspace/maintainability.yaml；缺失/坏键 → 默认值）
        → _god_file_check（before = git show HEAD:{path} 行数，新增文件/HEAD 缺失 = 0；
                           after = git show :{path} 行数【staged 版本，与"判定本次 commit"自洽】；
                           before < N and after >= N → violation）
        → _fuzzy_boundary_check（git diff --cached -U0 -- {path}；只取 '+' 前缀且非 '+++' 行；
                           行号取 @@ -a,b +c,d @@ 的 c 列；按扩展名路由正则组逐行匹配 → violation）
        → {"git_ok": True, "violations": [...], "god_file_count": N, "fuzzy_boundary_count": M}
```

- violation 条目形状：god-file → `{"type": "god-file", "file": <norm_rel>, "detail": "before=900 after=1150 threshold=1000"}`；fuzzy-boundary → `{"type": "fuzzy-boundary", "file": <norm_rel>, "line": <diff 新侧行号>, "detail": "matched pattern: 裸 except:"}`。
- `git_ok` 语义对齐 `score_task()`：run_git 不可用 / rev-parse 失败 → `{"git_ok": False, ...}`（fail-closed，不静默降级）。gate_p4 消费侧对 `git_ok: False` 只写 WARNING 不阻断（此时 ④ 步已因 git 通道问题返回 1，防御性降级不构成判定缺口）。
- 默认正则集（协议参考实现，配置可覆盖）：Python（`.py`）→ `^\s*except\s*:`（裸 except）、`#\s*type:\s*ignore`；TypeScript（`.ts/.tsx/.js/.jsx`）→ `:\s*any\b`、`\bas\s+any\b`。其它扩展名只做 god-file 行数判定，不做 fuzzy（P0-brief：其它语言不在本版范围）。
- 移动代码假阳性（BDD-12）：纯文本 diff 层面"删除行 + 新增行"中的新增行**照判**为 violation——已知行为非 bug，靠三重门槛登记吸收，不引入跨行移动检测。
- CLI 薄壳：`main()` 打印 violations 摘要（供 P6 复跑自查可读），exit code：0 = 无 violation 或 git 通道不可用（WARNING 语义）；1 = 有 violation。判定唯一依据 exit code。

### 3.2 gate_p4 三重门槛挂载与返回约定

挂载点：`gate_p4()` 第④步（:905）之后、骨架 WARNING（:907）之前。伪代码：

```python
# ── RM-AG0046：维护性反模式三重门槛（加载 agate/scripts/check-maintainability.py）──
if check_maintainability is not None:            # ImportError 降级 = WARNING（R2）
    result = check_maintainability(task_dir)
    if result.get("git_ok"):
        violations = result.get("violations", [])
        if violations:
            # 门槛 a：known-violations.md 存在（BDD-7）
            kv_path = os.path.join(task_dir, "known-violations.md")
            if not os.path.isfile(kv_path):
                sys.stderr.write(f"GATE P4: 检测到 {len(violations)} 个维护性反模式 violation，"
                                 "需登记 known-violations.md（模板 agate/assets/templates/known-violations-template.md）\n")
                return 1
            # 门槛 b：count_kf_entries 登记 ≥ violation 数（BDD-8，算法同构 gate_p5 :978-984）
            entries = count_kf_entries(_read_text(kv_path))
            if entries < len(violations):
                sys.stderr.write(f"GATE P4: known-violations.md 登记条目数({entries}) < "
                                 f"violation 数({len(violations)})，登记不完整\n")
                return 1
            # 门槛 c：P4-review approved 且 agent≠main —— 复用本函数既有 ①②③ 检查
            # （能执行到这里即 ①②③ 已通过，不重复实现；BDD-9/10 由顺序天然保证）
    else:
        sys.stderr.write("GATE P4 WARNING: check-maintainability git 通道不可用，本轮跳过维护性检测\n")
else:
    sys.stderr.write("GATE P4 WARNING: check-maintainability 未部署（ImportError），跳过维护性检测\n")
# 追加步骤结束，继续既有骨架 WARNING 与 return 0
```

返回约定兼容（约束 4）：

- 新步骤只产生 `return 1`（门槛 a/b 失败）或继续向下（通过/跳过），**不新增 return 2**——既有 WARNING 语义面不变。
- 顺序敏感面：①②③（评审检查）先于新步骤——BDD-9（登记对齐但评审未 approve → 1）由 ①②③ 的既有 return 1 天然满足，新步骤无需也不应重复评审判定。
- violations 为空 / 检测未部署 / git_ok False：三种跳过场景下 gate_p4 行为与改动前完全一致（R1 的等价性保证）。

### 3.3 `known-violations-template.md`（对齐计划 v3 §4.1）

模板内容如下（写入 `agate/assets/templates/known-violations-template.md`）：

    ---
    task_id: {Txxx}
    generated_by: {agent}
    ---
    # 维护性反模式登记

    > **语义边界**：本文件登记**本次任务 diff 引入的**维护性反模式（god-file 跨越 / fuzzy-boundary
    > 新增行），与 known-failures.md（登记预存失败）语义相反——这里登记的是"本任务自己造成的"问题。
    > 登记 + 数量对齐 + P4 评审 approve 三者齐全才放行，登记本身不构成放行依据。

    ## 本次引入的反模式

    | # | 文件 | 反模式类型 | 违规详情 | 理由 | P4 评审确认 |
    |---|------|-----------|---------|------|------------|
    | # | | god-file 跨越 / fuzzy-boundary | | | 是/否 |

- 「P4 评审确认」列不参与 `count_kf_entries` 机械计数（该函数只数行首数字列），是评审角色人工填写字段——防"填了就自动放行"错觉（计划 v3 §4.1）。
- 样例行首用 `| # |` 而非 `| 1 |`：不命中 `count_kf_entries` 正则（R8），照抄未改不虚增计数。
- 「违规详情」列登记 before/after 行数或 diff 行号，对应检测器 violation 条目的 `detail` 字段，便于评审核对。

### 3.4 P4/P6 卡片改动（落到具体小节标题）

- `agate/phase-cards/P4-implementation.md`：
  - 「## 评审派发（C8 机械映射）」节，:110「**单评审角色时**」段之后追加：评审角色 approve 前必须读过 `known-violations.md` 的登记理由（`check-maintainability.py` 检出 violations 非空时；RM-AG0046）——"是否接受该反模式"的判断权在评审角色，登记与数量对齐不单独构成放行依据。
  - 「## gate 规则（check-gate.py 会跑）」节追加 exit 1 条目：维护性反模式三重门槛——检测 violations 非空时，`known-violations.md` 必须存在且登记条目数 ≥ violation 数（评审检查复用上方既有 exit 1 条件）。
- `agate/phase-cards/P6-acceptance.md`：「## 自查≠gate」节正文追加：自查可（非阻断）复跑 `python3 agate/scripts/check-maintainability.py {TASK_DIR}` 确认 P4 后无新增反模式——P6 阶段暂存区通常已不含代码 diff，此为自查提醒而非 gate 判定点（检测器挂载在 P4，BDD-13）。

### 3.5 配置 `agate-workspace/maintainability.yaml`

```yaml
# RM-AG0046 维护性反模式检测配置——默认值仅供参考可配置（N=1000 来自 Cursor skill 经验值，无实证依据）
god_file_threshold: 1000
fuzzy_patterns:
  python:
    - '^\s*except\s*:'
    - '#\s*type:\s*ignore'
  typescript:
    - ':\s*any\b'
    - '\bas\s+any\b'
```

- 读取逻辑：repo_root 经 `run_git(["rev-parse", "--show-toplevel"], cwd=task_dir)` 解析，配置路径 = `{repo_root}/agate-workspace/maintainability.yaml`（隐含需求 5：不用 `.agate/`）。
- 兜底（BDD-6）：文件不存在 → 全默认值；yaml 库不可导入 → 全默认值 + stderr 提示；单键缺失/类型坏 → 该键默认值。任何配置问题不报错、不静默跳过，返回有效判定。

### 3.6 consistency 扫描面方案（隐含需求 10，P7 前实测验证）

新脚本落入 `check-protocol-consistency.py` 对 `agate/scripts/check-*.py` 的锚点覆盖扫描（:807-811 glob）。方案：**登记而非豁免**（脚本是真 gate 脚本，豁免表 `GATE_SCRIPT_EXEMPT` 只收非判定脚本）：

1. M3 在 `SCRIPT_ALIGNMENT_ANCHORS` 登记锚点（keywords 至少含 `god_file_count` / `fuzzy_boundary_count`——对应检测器返回 dict 的真实键；`callers: ["agate/scripts/check-gate.py"]`）。
2. R6 对策：gate_p4 挂载处注释含字面 `check-maintainability.py`（callers 校验 :771-785 按字面 basename 匹配，裸模块 import 行不含 `.py`）。
3. M4 同步 `_DRIFT_SCRIPTS` 一行。
4. M6/M7 卡片 wording 在脚本实现后引用，CHECK 10（脚本名引用漂移，:841-846）无漂移。

**P7 前实测验证**（写入 P5 执行契约）：`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（**必须用 worktree 自己的脚本**，AGENTS.md dogfooding 约定）0 ERROR = 通过；另跑一次 `--strict` 人工确认新增 WARNING 为零（锚点登记后 CHECK9-coverage 不应再报）。

## 4. gate_commands 声明（P2 固化，P4-P6 不可改）

```yaml
gate_commands:
  P3: "python3 -m pytest"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_timeout_seconds: 600
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_consistency_timeout_seconds: 120
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_count_tests_timeout_seconds: 60
  P5_ruff: "~/.venvs/agate-dev/bin/ruff check agate/scripts/ agate/tests/unit/"
  P5_ruff_timeout_seconds: 60
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
  P5_shellcheck_timeout_seconds: 60
```

声明说明：

- **无 `P3_xxx` 检测命令键**（R7）：实测 `agate-read-gate-commands.py:60` 会把所有 `P3*` 非元键收集为测试命令执行，检测器红灯由 pytest 统一承载（模块函数与 CLI exit code 均可测），不需要独立 count 命令。
- **不分片声明 P5_unit/P5_regression/P5_integration**：分片执行（`-n auto`、大 timeout）是 AGENTS.md 工具纪律层的**执行技术**，不是验证契约——`gate_commands` 声明"什么必须绿"，全量 `P5` 命令为权威口径，避免主命令 + 分片双跑的运行时翻倍。P5 执行时按工具纪律分片跑、汇总口径以全量命令为准。
- timeout 档位（三档基准表）：全量 pytest 属资源密集型，取构建档 600s（宁可档高勿误判，TPV0093 教训）；consistency 属单测类 120s；count_tests / ruff / shellcheck 均秒级命令，60s。P3 不声明 timeout（走 `AGATE_TDD_TIMEOUT` 既有机制，P2 卡字段规则第 1 条）。
- P5_ruff 用 `~/.venvs/agate-dev/bin/ruff`（与 CI 锁定 `ruff==0.16.4` 对齐，objective_info E 建议）；P5_shellcheck 本次无新 .sh，纯防回归。
- 每 key 独立声明、无 `&&` 链（禁短路反模式）；`ui_affected: false` → 无 `P5_e2e`。

## 5. 测试设计落点（给 P3 test-designer：落点 + 分组，不写用例代码）

先例：`test_check_gate.py`（gate 判定主套件）、`test_check_gate_p5_diff.py`（gate 挂载 + diff 判定）、`test_agate_risk_score.py`（返回结构）、`test_md_parse_scan.py`（count_kf_entries）。fixture 复用 conftest：`git_repo`（:264-302，git init/stage/commit 封装）、`task_dir`（:374-394）、`agate_root`（:305-312，`AGATE_ROOT` env 覆盖）、`python_exe`（:358-365，python3|python 探测）。

### 5.1 `agate/tests/unit/test_check_maintainability.py`（检测器，M9）

| 分组 | 覆盖 | 要点 |
|------|------|------|
| G1 god-file 跨越 | BDD-1 | git_repo 造 900 行文件 stage 后扩到 1150 行再 stage；断言 violations 含该文件 |
| G2 存量不误伤 | BDD-2 | 1200 行文件已 commit，diff 改 5 行 stage；断言 god_file_count 不增 |
| G3 fuzzy Python | BDD-3 | .py 新增裸 `except:` 行 staged；断言 violation 含文件+行号 |
| G4 存量行不误伤 | BDD-4 | 既有裸 `except:` 不在本次 diff 新增行；断言 fuzzy_boundary_count 不增 |
| G5 阈值可配置 | BDD-5 | tmp_path 下写 maintainability.yaml `god_file_threshold: 500`；480→520 触发，默认 1000 不触发 |
| G6 配置缺失兜底 | BDD-6 | 无配置文件 / 坏 YAML / 单键缺失三态；断言返回有效判定不抛错 |
| G7 路径平台无关 | BDD-11 | 同一 diff 场景分别以 `/` 与 `\` 形态的相对路径输入（Windows 场景在 Linux 用模拟路径断言 `_norm_rel` 归一等价，按平台分支） |
| G8 移动假阳性诚实行为 | BDD-12 | 含裸 `except:` 的代码块 A→B 移动（删除行+新增行）；断言新增行判 violation |
| G9 P4 数据源对齐 | BDD-13 | 代码 staged 状态下调 `check_maintainability(task_dir)`，断言能读到 diff 并判定（对比：无 staged 代码时 git_ok/violations 形态） |
| G10 模块契约 | 实现导航 | `check_maintainability` 可 import、dict 形状（git_ok/violations/god_file_count/fuzzy_boundary_count）、git 通道失败 fail-closed、CLI exit code 0/1 |

### 5.2 `agate/tests/unit/test_check_gate_p4_maintainability.py`（P4 挂载，M10）

| 分组 | 覆盖 | 要点 |
|------|------|------|
| G1 登记缺失阻断 | BDD-7 | violations 非空 + known-violations.md 不存在 → `check-gate.py P4` exit 1 |
| G2 数量不对齐阻断 | BDD-8 | violations=3（构造 staged diff）+ 登记 2 条 → exit 1 |
| G3 评审未 approve 仍阻断 | BDD-9 | 登记 3 条 + P4-review 缺失/非 approved/agent=main 三态 → 各自 exit 1 或 2（既有 ①②③ 语义不被新步骤改变） |
| G4 三重满足放行 | BDD-10 | violations=3 + 登记 3 条 + review approved（agent≠main）→ exit 0 |
| G5 无 violations 回归面 | R1 | 合规任务无 violations → gate_p4 返回值与改动前逐项等价（含 ①②③④ 既有失败路径） |
| G6 ImportError 降级 | R2 | 模拟 check_maintainability 不可导入 → WARNING 不阻断 |
| G7 返回约定 | 约束 4 | 新步骤不产生 return 2；门槛 a/b 失败仅 return 1 |

平台无关硬约束落实：全部用 `tmp_path`（不用 /tmp）；git 操作经 `git_repo` fixture（不裸 PATH）；解释器经 `python_exe` 探测；`AGATE_ROOT` 经 `agate_root` fixture 支持 env 覆盖（CI 无 ~/.agate）；Windows 差异场景按平台分支断言或模拟路径（G7），不假设 POSIX symlink 语义。

## 6. files_to_read

```yaml
files_to_read:
  - path: agate/scripts/check-gate.py:870-927
    why: gate_p4 函数体——新步骤挂载点（④步之后、骨架 WARNING 之前），既有检查 ①②③④ 的返回语义
  - path: agate/scripts/check-gate.py:25-58
    why: import 兜底区模式（try from agate_common / except ImportError）——check_maintainability import 同型
  - path: agate/scripts/check-gate.py:930-985
    why: gate_p5 known-failures 数量对齐算法参照（:978-984）
  - path: agate/scripts/agate-risk-score.py:41-59
    why: _load_script importlib 模式（复用加载 agate-risk-score 取 _norm_rel）
  - path: agate/scripts/agate-risk-score.py:86-88
    why: _norm_rel 路径归一化单源（BDD-11）
  - path: agate/scripts/agate-risk-score.py:202-229
    why: score_task 返回 dict 形状参照 + run_git(cwd=task_dir) 用法
  - path: agate/scripts/agate_common.py:1015-1017
    why: count_kf_entries 行首数字列计数（门槛 b 复用）
  - path: agate/scripts/check-protocol-consistency.py:697-830
    why: SCRIPT_ALIGNMENT_ANCHORS 表尾登记位 + check_script_alignment 的 callers 字面校验机制
  - path: agate/scripts/agate-summary.py:42-50
    why: _DRIFT_SCRIPTS 清单同步位
  - path: agate/assets/templates/known-failures-template.md
    why: known-violations-template.md 的格式参照（语义反转）
  - path: agate/phase-cards/P4-implementation.md:84-148
    why: 评审派发节（checklist 追加位）+ gate 规则节（exit 1 条目追加位）
  - path: agate/phase-cards/P6-acceptance.md:226-229
    why: 自查≠gate 节（复跑提醒追加位）
  - path: agate/tests/conftest.py:264-312
    why: GitRepo fixture（git init/stage/commit/staged_diff）+ agate_root（AGATE_ROOT env 覆盖）
  - path: agate/tests/unit/test_check_gate_p5_diff.py
    why: gate 挂载测试的结构先例（M10 测试文件照此组织）
  - path: agate-workspace/tasks/TAG0026-maintainability-gate/P1-requirements.md
    why: 13 条 BDD 验收对照（实现完成判定）
  - path: docs/design-notes/rm-ag0046-maintainability-gate-plan.md
    why: 落地计划 v3 §2/§4.1（实现蓝图与模板定义）
```

## 7. env_constraints

```yaml
env_constraints:
  debug_env: "python3 -m pytest agate/tests/ -n auto（unit/regression/integration 分片，执行技术）+
    python3 agate/scripts/check-protocol-consistency.py --strict-errors-only（必须用 worktree 自己的脚本）+
    bash agate/tests/scripts/count-tests.sh；gate/hook 用 ~/.agate 稳定版；ruff 用 ~/.venvs/agate-dev/bin/ruff（锁 0.16.4 与 CI 对齐）"
  isolation_check: "P5 实测 worktree check-protocol-consistency.py --strict-errors-only 0 ERROR +
    count-tests.sh 数字以实测为准（不写死）；P2 阶段声明 [PROD_NOT_TOUCHED]"
  workspace_note: "本任务为 worktree（agate-TAG0026）dogfooding：改代码/测试在 worktree；
    consistency 必须跑 worktree 版（否则扫到主 checkout 协议文件，TAG0016 同源教训）"
```

- 从 P0-brief 继承并细化，无弱化。P0 阶段未接触生产环境，`[PROD_NOT_TOUCHED]`。
- 本任务纯代码逻辑（git diff 解析 + 行数计算 + 正则匹配），无生产环境依赖；`env_constraints` 为声明性字段，强制执行面已全部落在 `gate_commands`（§4）与 P4/P6 卡片 checklist（§3.4）。

## 8. minimal_validation

```yaml
minimal_validation:
  assumption: "纯代码逻辑，无外部系统依赖——不涉及浏览器行为/安全模型/外部系统交互"
  method: "依赖的内部函数/数据转换均已实测核实（本 P2 逐文件读取验证）：
    ① git diff --cached -U0 输出解析（新增行 '+' 前缀过滤 + @@ -a,b +c,d @@ 新侧行号提取）
    ② git show HEAD:{path} / git show :{path} 前后行数计算（新增文件/首次提交 before=0 兜底）
    ③ agate_common.count_kf_entries（:1015-1017，行首 ^\\|\\s*[0-9]+\\s*\\| 计数）
    ④ agate-risk-score._norm_rel（:86-88，反斜杠归一）经 _load_script 单源复用
    ⑤ check-gate._md_field_get（P4-review frontmatter 读取，既有函数直接复用）"
  result: "not_needed"
  note: "git/python3/pytest/pyyaml 均为本地工具链（P0-brief 环境自检已声明可用），
    无网络/浏览器/外部系统前提需要最小验证。P1 无删除/移动路由类改动（T086 B1 教训不触发）。
    唯一'代码逻辑正确性假设'——gate_p4 挂载点顺序（新步骤在评审检查之后可复用其结论）——
    已通过读取 gate_p4 :870-927 全函数体核实，非凭想象。"
```

## 9. dispatch_plan 说明

单脚本 + 测试任务，无多包/多模块拆批需求；P5 全量 pytest 资源密集型 → 编排默认**串行**（派发约束 9）。frontmatter 声明 `dispatch_plan: {mode: serial}`；无 batches（serial 模式无批次表）。

## 10. 实现完成的标志（可判定，供 P3/P5/P6 消费）

1. `check_maintainability(task_dir)` 可被 check-gate.py import，返回 §3.1 形状的 dict（G10 断言通过）。
2. 13 条 BDD 对应测试全部落于 §5 两个文件，红灯先行（P3）→ 实现后全绿（P5）。
3. `check-gate.py P4 $TASK_DIR` 在 violations 非空 + 未登记场景 exit 1（BDD-7 实测），三重满足场景 exit 0（BDD-10 实测）；violations 为空场景行为与改动前一致（G5 回归面）。
4. `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`（worktree 版）0 ERROR，且 `--strict` 无新增 WARNING（§3.6 实测）。
5. `bash agate/tests/scripts/count-tests.sh` 数字只增不减（新增用例计入），无既有用例漂移。
6. P4/P6 卡片 wording 含 §3.4 声明的 checklist 条目与复跑提醒；模板文件存在于 `agate/assets/templates/known-violations-template.md` 且样例行首为 `| # |`。
