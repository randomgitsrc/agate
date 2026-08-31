---
phase: P4
task_id: TAG0026
parent: P2-design.md
trace_id: TAG0026-P4-20260830
status: draft
created: '2026-08-30'
agent: implementer
implementation_dir: agate/scripts/
---

# P4-implementation — TAG0026 维护性反模式 gate 实现说明

implementation_dir: agate/scripts/

[PROD_NOT_TOUCHED]

> parent: P2-design.md（§1.1 M1-M8 改动清单 + §3 设计细节）｜TDD 目标：P3 两个测试文件 27 条用例转绿。
> 本文件由 implementer subagent 产出；frontmatter 经 agate-md-field-set 写入（agent 键若不在合法清单，按 P3-test-cards 先例手写补行）。

## 1. 实现清单（M1-M8 逐项）

| # | 文件 | 实现 |
|---|------|------|
| M1 | `agate/scripts/check-maintainability.py`（新增） | 检测器：`check_maintainability(task_dir) -> {"git_ok", "violations", "god_file_count", "fuzzy_boundary_count"}` 四键严格；violation 条目 god-file=`{type,file,detail}` / fuzzy-boundary=`{type,file,line,detail}`；`_load_config` 全兜底（缺失/坏 YAML/单键缺失/类型坏 → 该键默认值，stderr 提示，不抛错）；god-file 用 `git show HEAD:{path}`（before，新增文件/HEAD 缺失=0）+ `git show :{path}`（after，staged 版本），`before < N <= after` 跨越判定；fuzzy 用 `git diff --cached -U0`，只取 `+` 前缀非 `+++` 行，行号取 `@@ -a,b +c,d @@` 的 c 列，按扩展名路由正则组（.py→python；.ts/.tsx/.js/.jsx→typescript；其它只做 god-file）；`git diff --cached --name-status` 只处理 A/M 跳过 D；复用链 `from agate_common import run_git, count_kf_entries`（ImportError 降级）+ `_load_script("agate-risk-score")._norm_rel`（importlib 同源，加载失败降级本地同实现）；CLI 薄壳 `main()` 打印摘要、exit 0（无 violation 或 git 不可用 WARNING）/ 1（有 violation） |
| M2 | `agate/scripts/check-gate.py`（修改） | ①import 兜底区（agate_common 块之后）`try: from check_maintainability import check_maintainability / except ImportError` 降级——**except 内含 importlib 按文件路径加载兜底**（连字符文件名见 §3 DESIGN_GAP），仍失败才 None；②gate_p4 在④步（staged 代码检查）之后、骨架 WARNING 之前插入三重门槛步骤：violations 非空时 门槛 a（known-violations.md 不存在 → stderr 含 "known-violations" + return 1）→ 门槛 b（`count_kf_entries` 登记 < violation 数 → stderr 含 "登记" + return 1）→ 门槛 c 复用既有①②③不重复实现；git_ok False / 未部署各写 WARNING 继续；只产生 return 1 或继续向下，不新增 return 2；挂载处注释含字面 `check-maintainability.py`（R6） |
| M3 | `agate/scripts/check-protocol-consistency.py`（修改） | `SCRIPT_ALIGNMENT_ANCHORS` 表尾登记：script=`agate/scripts/check-maintainability.py`，keywords=`["god_file_count", "fuzzy_boundary_count"]`，callers=`["agate/scripts/check-gate.py"]`（R6 callers 字面校验由 M2 注释满足） |
| M4 | `agate/scripts/agate-summary.py`（修改） | `_DRIFT_SCRIPTS` 追加一行 `"check-maintainability.py"` |
| M5 | `agate/assets/templates/known-violations-template.md`（新增） | P2 §3.3 全文：frontmatter（task_id/generated_by）+ 语义边界引用块（与 known-failures 语义相反 + 三者齐全才放行）+ 表格；样例行首 `| # |`（不命中 `count_kf_entries` 的行首数字列正则，R8）；另附填写说明（真实行用 `| 1 |` 行首数字、详情抄检测器输出） |
| M6 | `agate/phase-cards/P4-implementation.md`（修改） | 两处：①「评审派发（C8 机械映射）」节末尾加评审 checklist 条目（violations 非空时评审 approve 前必须读过 known-violations.md 登记理由，判断权在评审角色）；②「gate 规则」节补一行 exit 1 条目（RM-AG0046 三重门槛：violations 非空时 known-violations.md 必须存在且登记 ≥ violation 数；三跳过场景不阻断）。两处均含字面 `check-maintainability.py` |
| M7 | `agate/phase-cards/P6-acceptance.md`（修改） | 「自查≠gate」节追加一句非阻断复跑提醒：`python3 agate/scripts/check-maintainability.py {TASK_DIR}`，注明 P6 暂存区通常无代码 diff、挂载在 P4（BDD-13），自查提醒而非 gate 判定点 |
| M8 | `agate-workspace/maintainability.yaml`（新增） | P2 §3.5 示例配置：`god_file_threshold: 1000` + python/typescript 正则组；注释明确"默认值仅供参考可配置"（R9） |

未动（P2 §1.2 逐条遵守）：gate_p4 既有四步语义与顺序、check-p6-provenance.py、gate_p5 判定、check-gate.py 调用方、ruff 配置、known-failures-template.md、WORKFLOW.md、rules/*.yaml、P3 测试文件、conftest.py。

## 2. 自查结果（自查 ≠ P5 gate）

- `python3 -m pytest agate/tests/unit/test_check_gate.py`：**182 passed**（既有 gate 主套件，含 gate_p4 既有失败路径回归面——新步骤对 violations 为空/未部署场景零行为变化）。
- `~/.venvs/agate-dev/bin/ruff check agate/scripts/`：**All checks passed**（0 error；自查中修掉了本实现引入的 14 项：%-格式化→f-string、无效 noqa）。
- P3 目标测试（`test_check_maintainability.py` + `test_check_gate_p4_maintainability.py`）：**27 passed 全绿（14 + 13）**——初轮 13 failed + 14 skipped 的测试侧探测路径缺陷（§3.2，非实现断言失败）已按主 Agent 定夺修复；实现侧已按探测规则匹配形态（import 语句 + gate_p4 体消费 + 模块可加载 + `_norm_rel` 存在）。
- 一致性预检：gate_p4 挂载处注释含字面 `check-maintainability.py`（grep 2 处）；模板样例行首 `| # |`（grep 确认）；consistency 锚点登记（grep 1 处）。

## 3. 申报与阻塞

### 3.1 [DESIGN_GAP: P2-design.md §2.1/§3.2 的 import 兜底形态未覆盖连字符文件名问题：文件名 check-maintainability.py 含连字符，而 from check_maintainability import 的模块名标识符不能含连字符——该 ImportError 在"检测器已部署"场景下同样必然发生（子进程跑 check-gate.py 时 sys.path 探测无法命中连字符文件），§3.2 的单段 try/except 会把"已部署"静默降级为"未部署"，P4 三重门槛在生产 hook 路径上永不生效。实现保留 try/except 形态（约束 6）并在 except 内加 importlib 按文件路径加载兜底（agate-risk-score.py _load_script 同源机制），仍失败才降级 None；check-gate.py 的降级路径经 test_check_gate.py 182 条回归验证（含此前因该问题暴露的 1 条 WARNING 语义回归，修复后全绿）。]

### 3.2 ⛔ 主 Agent 必读：P3 测试探测路径缺陷（未改测试，报告定夺）

两个 P3 测试文件的"实现探测"都少算了一级 parent（`unit → tests → agate` 少了最后一跳），解析到不存在的路径：

- `test_check_gate_p4_maintainability.py` `_gate_p4_source()`：`Path(__file__).resolve().parent.parent / "scripts" / "check-gate.py"` = `agate/tests/scripts/check-gate.py`（**实际目标应为 `agate/scripts/check-gate.py`**）。`agate/tests/scripts/` 是真实存在的目录（含 count-tests.sh 等），但 check-gate.py 不在其中；`git log --all -- agate/tests/scripts/check-gate.py` 为空（全仓历史从未存在）。后果：`_IMPLEMENTED` 恒 False → 13 条用例全部卡在 `_require_implemented()` 的 sentinel 断言（failed 均为 sentinel，非行为断言）。
- `test_check_maintainability.py` 收集期探测与 `_load_mod()`：`sys.path.insert(Path(__file__).resolve().parent.parent)` = 插入 `agate/tests`（**实际应插入 `agate/scripts`**）→ `import check_maintainability` 永久 ImportError → 14 条 skipif 永久 skip。且模块名 `check_maintainability`（下划线）与文件名 `check-maintainability.py`（连字符）在纯 sys.path 机制下本就无法互相命中，`_load_mod` 需要类似 importlib 按路径加载的形态。
- 互证证据（实现侧与探测规则已对齐）：①对 `agate/scripts/check-gate.py` 重放 `_maintainability_gate_implemented()` 正则 → imported=True / consumed=True；②`check-maintainability.py` 按文件路径 importlib 加载成功且 `check_maintainability` / `_norm_rel` 均在；③既有 182 条 gate 回归全绿。
- 按派发约束 1/13 与 implementer 角色决策树：未修改任何测试文件，停在此处报告。P3-test-cases.md §1 描述的红灯机制（"sentinel 自动转绿/skipif 自动解除"）在当前路径缺陷下无法兑现，需主 Agent 决定：修测试探测路径（一行级）后重跑，或另定验证路径。
- 【已解决·主 Agent 定夺 2026-08-30】授权修测试探测机制（断言语义与用例逻辑不动）。修复落地：①探测路径补算 unit→tests→agate 三级 parent（两文件）+ `_load_mod` 改 importlib 按路径加载（连字符文件名机制）；②修复轮场景构造：`_repo_with_staged` 返回值改名 `_td`（repo 内 task 目录）后 6 处裸 `td` 引用修正（G2/_bdd9_case/BDD-10/G5c/G7），纯 NameError 机械修；③ruff hygiene 清零（未用解包 `_` 前缀 + 删未用导入；HEAD 基线本带 20 项，非本轮引入）。终态：组合 **27 passed**（14+13）+ gate 回归 **182 passed** + ruff All checks passed。以上原缺陷描述保留作历史留档。

## 新增文件核对表（CODE-MAP 机制采用中：agents/CODE-MAP.md 存在）

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| agate/scripts/check-maintainability.py | within agate/scripts/（P2-skeleton.md 不存在，骨架机制未采用） | [CODE_MAP_EXEMPT: CODE-MAP「关键文件」为导航式清单，同类检测脚本（check-pruning.py / agate-risk-score.py / check-routing.py 等）均无专条，本文件与其同层不单列] |
| agate/assets/templates/known-violations-template.md | within agate/assets/templates/ | [CODE_MAP_EXEMPT: 同上——CODE-MAP 以目录粒度登记 templates 层，不逐模板列条] |
| agate-workspace/maintainability.yaml | within agate-workspace/ | [CODE_MAP_EXEMPT: 任务工作区数据文件（对齐 ADR-009），非代码结构，CODE-MAP 不覆盖] |

## 5. 范围声明

- 无 [SCOPE+]：实现严格限于 P2 §1.1 M1-M8。
- 无 [SCOPE_GAP]：dispatch prompt 与 P2 改动清单逐项对照无遗漏。
- git 纪律：未对 worktree 仓库执行任何 git 写操作（无 add/commit/checkout）；仅有的 git 调用为只读查证（git log --all / git status）。

## 6. 改动文件清单

1. `agate/scripts/check-maintainability.py`（新增）
2. `agate/scripts/check-gate.py`（import 兜底区 + gate_p4 新步骤）
3. `agate/scripts/check-protocol-consistency.py`（锚点登记）
4. `agate/scripts/agate-summary.py`（_DRIFT_SCRIPTS）
5. `agate/assets/templates/known-violations-template.md`（新增）
6. `agate/phase-cards/P4-implementation.md`（两处）
7. `agate/phase-cards/P6-acceptance.md`（一处）
8. `agate-workspace/maintainability.yaml`（新增）
