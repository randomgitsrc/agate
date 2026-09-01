---
phase: P7
task_id: TAG0026
type: consistency
parent: P2-design.md
trace_id: TAG0026-P7-20260830
status: draft
created: 2026-08-30
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 1
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
code_map_new_files_count: 3
code_map_reviewed_count: 3
---

# P7-consistency — TAG0026 维护性反模式 gate（RM-AG0046）跨文件一致性审查

> 审查对象：P1-P6 全部产出 + 实现侧第一手锚点核验（只审不写，无 worktree git 写操作）。
> 审查时 .state.yaml phase=P7；worktree HEAD=5d828c9（P6.5 commit）。
> 输入：dispatch-context 清单 13 项全读（P7 输入数量豁免），P6-evidence 抽查 bdd-7/9/12/13
> 四份 + P6.5 verdict 互证；实现侧核验 check-gate.py / check-maintainability.py 落点 /
> 卡片改动 / 测试函数清单均为第一手读取。

[PROD_NOT_TOUCHED]

## 1. DESIGN_GAP 配对（P4§3.1 → 本文件转抄 + REVIEWED）

P4-implementation.md §3.1 声明 1 条 DESIGN_GAP（gate 配对口径按行内标记计数，
gate_p7 走 frontmatter 结构化计数判定：design_gap_count=1 / design_gap_reviewed_count=1）。

P4 §3.1 原文逐字转抄（程序化提取自 P4-implementation.md:45，`### 3.1 ` 标题行内嵌标记，
下述引号区为该行 `[DESIGN_GAP:` 之后至行尾的原样字节）：

[DESIGN_GAP: P2-design.md §2.1/§3.2 的 import 兜底形态未覆盖连字符文件名问题：文件名 check-maintainability.py 含连字符，而 from check_maintainability import 的模块名标识符不能含连字符——该 ImportError 在"检测器已部署"场景下同样必然发生（子进程跑 check-gate.py 时 sys.path 探测无法命中连字符文件），§3.2 的单段 try/except 会把"已部署"静默降级为"未部署"，P4 三重门槛在生产 hook 路径上永不生效。实现保留 try/except 形态（约束 6）并在 except 内加 importlib 按文件路径加载兜底（agate-risk-score.py _load_script 同源机制），仍失败才降级 None；check-gate.py 的降级路径经 test_check_gate.py 182 条回归验证（含此前因该问题暴露的 1 条 WARNING 语义回归，修复后全绿）。]

[DESIGN_GAP_REVIEWED: P2-design.md §2.1/§3.2 的 import 兜底形态未覆盖连字符文件名问题——已逐字转抄并按下述四子项审查通过，判定为与 P2 契约兼容的合理实现偏差（不构成 P2 设计缺陷，无需文档回写）。]

审查结论（dispatch-context 指定的四个审查子项，逐项给锚点）：

- **该偏差是否与 P2-design 契约兼容**：兼容。P2§2.1 要求"实现保留 try/except 形态
  （约束 6）"，P2§3.2 伪代码的 `except ImportError:` 分支语义 = "import 失败时降级为
  None / WARNING 不阻断（R2）"。实现（check-gate.py:162-185 第一手读取）保留外层
  try/except，except 内新增 importlib 按路径加载兜底、仍失败才置 None——对"未部署"
  场景（文件不存在，spec_from_file_location 抛异常）最终仍落 None，与 P2 降级语义
  逐点等价；对"已部署"场景新增了正确加载路径，是契约的**收紧**而非偏离。P2§3.2
  "降级为 WARNING 不阻断"与"未部署 ≠ 判定缺失"的立场均未改变（gate_p4 :965-968
  的 None 分支 WARNING 与 P2 伪代码 :163 一致）。
- **importlib 兜底是否与 agate-risk-score `_load_script` 同源**：是。第一手比对：
  agate-risk-score.py:46-54 `_load_script` = `importlib.util.spec_from_file_location`
  → `module_from_spec` → `exec_module`（docstring 明言"带连字符模块名无法直接
  import"）；check-gate.py:172-183 except 分支 = 同一 importlib.util 四步机制
  （spec_from_file_location("check_maintainability", dirname(__file__)+"/check-maintainability.py")
  → module_from_spec → exec_module → 取属性），差异仅为内联形态与无 `module_name`
  替换参数——连字符文件名本就没有合法模块名，行为等价。与 P4 申报"_load_script 同源
  机制"一致。
- **P2-review 是否已核**：部分预核 + 实现评审闭环。P2-review.md:76-81 实测
  `_load_script` :46-54（importlib spec_from_file_location、连字符转下划线）并将其与
  check-gate.py:32-41 既有 ImportError 兜底先例同型对照（非阻塞建议：P4 实现时注明）；
  但连字符文件名对 `from check_maintainability import` 的必然失效属实现期发现，P2-review
  未预判（P2§3.2 伪代码即按裸 import 写定）。实现期由 P4-review.md 核查项 3.1 完成
  同源性核（P4-review.md:41-46，结论"申报与落地无出入"），核查项 1/2（返回约定与
  挂载注释）同步复核该兜底路径，P4-review status: approved（frontmatter :9）。申报链
  完整：P4 §3.1 申报 → P4-review 核查项 3.1 确认 → 本节 P7 复核三方一致。
- **文档层面是否需回写**：不需要。P2-design.md §3.2 伪代码是设计意图（import 兜底 +
  降级语义），连字符加载细节是 Python 模块系统层面的实现事实，P4 §3.1 已完整申报、
  P4-review 已核、本文件已 REVIEWED 配对——修正记录留存在 P4 产出链，P2 正文无需
  追改（改 P2 反而制造"设计被实现后回写"的 provenance 噪声）。同理不立新 DEBT
  （P4-review「无非阻塞 DEBT 新增」结论维持）。

## 2. SCOPE+ 闭环

- P4§5 范围声明：「无 [SCOPE+]：实现严格限于 P2 §1.1 M1-M8」「无 [SCOPE_GAP]」——
  第一手核验 P4-implementation.md:66-69 属实。
- P1-requirements.md 全文 grep SCOPE+ / SCOPE_RESOLVED / NEED_CONFIRM / 阻断标记 /
  严重偏差标记（含反引号包裹形态）：仅 1 命中 = §3 的行首 [NO_NEED_CONFIRM]（P1:84）
  ——无 SCOPE+ 增补、无 SCOPE_RESOLVED 需求、无残留 NEED_CONFIRM。
- 结论：**无增补即无闭环动作**——SCOPE+ 机制本任务零条目，闭环条件（P1 有
  [SCOPE_RESOLVED]）以"无需存在"方式满足；P4-review 核查项 10（P4-review.md:114-122）
  `git diff --name-only` 全清单比对亦确认无越界文件，交叉印证。

## 3. 跨文件一致性（逐项给锚点）

### 3.1 P1 BDD 数 = P6 PASS 数 = P6.5 judge criteria_total

- 数量三方一致：P1§7 逐条 BDD-1..13（P1:126-219）= P6 §2 PASS 行 13 条
  （P6-acceptance.md:43-55，frontmatter `pass: 13 / fail: 0`，Summary "13/13 PASS,
  0 FAIL"）= P6.5 frontmatter `criteria_total: 13 / criteria_passed: 13` +
  verdict_evidence 13 份（P6.5:3-5）。
- 逐条编号内容对应（非仅数量对齐，按 dispatch-context 指定抽查 BDD-7/9/12/13）：
  - **BDD-7**：P1 判定锚「known-violations.md 不存在 → gate_p4 返回 1」（P1:170-175）
    ↔ P6 PASS 行「violations 3 条 + 登记缺失 + 门槛 a 命中 exit 1」（P6:49）↔ 证据
    bdd-7.log：前置核验 violations=3（fuzzy_boundary_count: 3，base.py:12/17/22）+
    stderr 含"需登记 known-violations.md（模板 agate/assets/templates/known-violations-template.md）"
    + EXIT_CODE:1——场景、阻断消息、退出码与判定锚逐项吻合。
  - **BDD-9**：P1 判定锚「登记对齐但评审未 approve 仍 return 1，不能靠数量对齐单独
    放行」（P1:184-189）↔ P6 PASS 行三变体（P6:51）↔ 证据 bdd-9.log：变体 a
    （P4-review.md 不存在，stderr=既有①的评审缺失消息）→ EXIT_CODE:1；变体 b
    （status=draft，stderr=②非 approved 消息）→ EXIT_CODE:1；变体 c（agent=main，
    stderr=③主 Agent 不可自行批准消息）→ EXIT_CODE:1——三变体各自落在既有 ①②③
    检查的真实阻断消息上，证明新步骤未改变其语义（P2§3.2"顺序敏感面"设计兑现）。
  - **BDD-12**：P1 判定锚「移动代码新增行照判 violation（已知假阳性），且能经三重
    门槛正常处理」（P1:207-212）↔ P6 PASS 行（P6:54）↔ 证据 bdd-12.log：diff 呈
    删除行+新增行（except 块 11-14 行移至末尾），检测器 `fuzzy-boundary: mover.py:18
    (matched pattern: ^\s*except\s*:)` EXIT_CODE:1（新增行号 18 > 原位置 11-14，照判
    未忽略）；同场景登记 1 条 + approve 后 `GATE_EXIT_CODE:0`（三重门槛消化）——
    判定锚两半均满足。
  - **BDD-13**：P1 判定锚「P4 调用时能读到代码 diff 并判定；挂 P6 则读空 diff 不产生
    判定」（P1:214-219）↔ P6 PASS 行（P6:55）↔ 证据 bdd-13.log：同一 tmp 仓库两侧
    对照——侧 A（代码 staged）`fuzzy-boundary: p4feat.py:6` EXIT_CODE_SIDE_A:1；侧 B
    （代码已 commit 暂存区空）`god_file_count: 0 / fuzzy_boundary_count: 0`
    EXIT_CODE_SIDE_B:0——数据源 = `git diff --cached`、挂载在 P4 的对齐成立。
- 数量口径附注：P3§4 汇总行称"合计 26 用例"（M9"10 BDD 用例 + 5 契约用例 = 15"、
  M10"11 用例"），与该文件 §2/§3 映射表逐条函数清单及两测试文件 `^def test_` 实测
  （M9 14 = 9 BDD + 5 契约；M10 13；合计 27）存在算术口径差；P5§3 count-tests 实测
  **27**（14+13）入账且与 P0 基线 1308 精确吻合（1308+27=1335），P4§2/P4-review 均
  按 27 口径——27 为权威实测数，BDD 13/13 覆盖映射逐条在案无缺口。该汇总行算术
  瑕疵计入 deviation_count=1（WARNING 级非阻断，详见 §7 偏差记录）。

### 3.2 P2 packages 与 P4 实现落点、P8 bump 范围一致

- P2§packages（frontmatter）与 P1 frontmatter packages 同为
  `[agate-scripts, agate-tests, agate-phase-cards, agate-templates]`（P1:12 / P2:11）。
- 逐包落点核对（P4§6 改动清单 8 文件 + P4-review 核查项 10 git 清单）：
  agate-scripts → check-maintainability.py（新增）/ check-gate.py /
  check-protocol-consistency.py / agate-summary.py；agate-templates →
  known-violations-template.md（新增）；agate-phase-cards → P4-implementation.md（两处）
  / P6-acceptance.md（一处）；agate-tests → 两个测试文件（主 Agent 授权修复）；
  agate-workspace 数据面 → maintainability.yaml（新增，ADR-009 对齐，非协议 bump 面）。
  四包全部有实际产出，无包外协议改动（P4-review.md:114-122 无越界文件结论）。
- P8 bump 范围一致性：P8 发布对象 = 上述协议本体改动（agate/ 下 7 文件），P2§1.2
  「不改什么」清单（gate_p4 既有四步、check-p6-provenance、gate_p5 判定、ruff 配置、
  WORKFLOW.md、rules/*.yaml 等）与 P4§1「未动」清单逐条一致——无隐性改动面需要
  溢出 bump 范围。P7 时点判定：一致（P8 release bump 按此清单执行即可覆盖）。

### 3.3 P4 实现路径与 P2 §3 方案吻合

- **检测器契约**（P2§3.1 ↔ P4§1 M1 ↔ check-maintainability.py）：返回 dict 四键
  `{git_ok, violations, god_file_count, fuzzy_boundary_count}`（P4-review 核查项 9
  实测 :271-276）；violation 条目形状 god-file=`{type,file,detail}` / fuzzy-boundary=
  `{type,file,line,detail}`；`_load_config` 全兜底（缺失/坏 YAML/单键缺失 → 默认值）；
  `git show HEAD:{path}`/`git show :{path}` 前后行数 + `before < N <= after` 跨越判定；
  fuzzy 取 `git diff --cached -U0` 的 `+` 行、行号取 `@@ -a,b +c,d @@` c 列、按扩展名
  路由正则（.py→python；.ts/.tsx/.js/.jsx→typescript）；`--name-status` 只处理 A/M
  跳过 D——与 P2§3.1 数据流逐点吻合。复用链 `run_git`/`count_kf_entries`（agate_common）
  + `_norm_rel`（_load_script("agate-risk-score")，P2§2.1 四点单源声明兑现）。
- **gate_p4 挂载点**（P2§3.2 ↔ check-gate.py:932-968 第一手读取）：新步骤落在既有
  ④步「暂存区代码检查」return 1（:929-930）之后、骨架/CODE-MAP WARNING（:970-988）
  之前，与 P2§3.2「④步之后、骨架 WARNING 之前」逐字一致；门槛 a（:943-950，
  known-violations.md 不存在 → stderr + return 1）→ 门槛 b（:953-958，
  count_kf_entries < violations → stderr + return 1）→ 门槛 c（:959-960 注释复用既有
  ①②③不重复实现）；只产生 return 1 或继续向下，无新增 return 2（:933-935 注释 +
  P3 G7 用例守护）；git_ok False（:961-964）/ 未部署（:965-968）两 WARNING 分支与
  P2 伪代码 :161-163 一致；挂载处注释 :932 含字面 `check-maintainability.py`（P2§R6
  callers 字面校验对策兑现）。
- **import 兜底区**：check-gate.py:162-185（连字符 importlib 兜底，见 §1 DESIGN_GAP
  审查）落位与 P4§1 M2 ① 声明一致（agate_common 块之后、既有兜底先例同型）。
- **模板格式**（P2§3.3 ↔ P4§1 M5）：P4-review 核查项 5 实测样例行首 `| # |`
  （known-violations-template.md:16，不命中 count_kf_entries 行首数字列正则，R8
  成立）+ 语义边界引用块 +「P4 评审确认」列不参与机械计数——与 P2§3.3 全文一致。
- **配置键**（P2§3.5 ↔ P4§1 M8 ↔ maintainability.yaml）：`god_file_threshold: 1000` +
  fuzzy_patterns python/typescript 正则组 +「默认值仅供参考可配置」注释（R9），
  P4-review 核查项 5 实测逐字一致；路径 `agate-workspace/maintainability.yaml`
  （repo_root 经 rev-parse 解析）符合 P2§3.5 与 ADR-009（隐含需求 5：不用 `.agate/`）。
- **M3/M4 一致性配套**：锚点登记 check-protocol-consistency.py:753
  （script=agate/scripts/check-maintainability.py，keywords=god_file_count/
  fuzzy_boundary_count，callers=[agate/scripts/check-gate.py]——P2§3.6 方案 1 兑现）；
  _DRIFT_SCRIPTS 追加 agate-summary.py:50 第 8 项（P2§3.6 方案 3 兑现）；P5§2 实测
  worktree consistency 0 ERROR / 323 WARNING（与 objective_info E 预检同值）——
  CHECK9-coverage 无新告警，锚点登记生效。

### 3.4 P2 §4 gate_commands 与 P5 实跑命令一致

P2§4 声明 5+P3 命令键 ↔ P5§命令结果总览 5/5 exit 0 逐键对照：

| P2§4 键 | P2§4 声明 | P5 实跑（unit.md 节） | 判定 |
|---|---|---|---|
| P5 | `python3 -m pytest agate/tests/ -q --tb=no`（600s 档） | §1 同命令，exit 0，150.77s，1333 passed + 2 skipped | 一致 |
| P5_consistency | `check-protocol-consistency.py --strict-errors-only`（120s） | §2 同命令（worktree 版），exit 0，0 ERROR / 323 WARNING | 一致 |
| P5_count_tests | `bash agate/tests/scripts/count-tests.sh`（60s） | §3 同命令，exit 0，1335（1308+27 只增不减） | 一致 |
| P5_ruff | `~/.venvs/agate-dev/bin/ruff check agate/scripts/ agate/tests/unit/`（60s） | §4 同命令，exit 0，All checks passed | 一致 |
| P5_shellcheck | `shellcheck -S warning agate/scripts/*.sh`（60s） | §5 同命令，exit 0，零发现 | 一致 |

5 条 P5 键全执行（无子集、无 && 链、单次全量未分片）；P3 运行器 = `python3 -m pytest`
（P3 红灯先行已由 P3/P4 阶段消费，13 failed 真红灯 + 修复后 27 passed，P4§2/P4§3.2）；
P2§4「无 P3_xxx 检测命令键」见 §3.6；`ui_affected: false` ↔ P6 frontmatter 同值，无
P5_e2e 键，两侧自洽。

### 3.5 卡片改动与实际 gate 行为对应

- **P4 卡两处**（P2§3.4 ↔ agate/phase-cards/P4-implementation.md 第一手读取）：
  评审 checklist 条目在 :112（「评审 checklist（RM-AG0046）」：violations 非空时 approve
  前必须读过 known-violations.md 登记理由，判断权在评审角色，登记与数量对齐不单独构成
  放行依据）——承载 P1 隐含需求 11 的流程要求 c；gate 规则节 exit 1 条目在 :150
  （RM-AG0046 三重门槛：violations 非空时 known-violations.md 必须存在且登记 ≥ violation
  数；三跳过场景不阻断）——与 check-gate.py gate_p4 实际行为（门槛 a/b return 1；
  violations 空/未部署/git_ok False 不阻断）逐字对应，两处均含字面 check-maintainability.py。
- **P6 卡一处**（P2§3.4 ↔ agate/phase-cards/P6-acceptance.md:230）：「自查≠gate」节
  非阻断复跑提醒 `python3 agate/scripts/check-maintainability.py {TASK_DIR}`，注明 P6
  暂存区通常无代码 diff、挂载在 P4（BDD-13）——与 bdd-13.log 侧 B 实测行为（P6 语境
  0/0）互证， wording 与实现语义一致。
- 卡片 wording 与代码行为的对应闭环由 P5 consistency 0 ERROR（CHECK 10 引用漂移无告警）
  与 P4-review 核查项 6 双重背书。

### 3.6 DEBT0023 与 P2 gate_commands 契约一致

- DEBT0023（tech-debt.md:814-841）：gate_commands 的 `P3*` 前缀键被
  agate-read-gate-commands.py:60 静默收集为 TDD 测试命令执行，协议层无机械防护——
  status: open / task_id: TAG0026 / source: review，登记要素齐全。
- 契约一致性：P2§4 声明说明第 1 条「无 P3_xxx 检测命令键（R7）」+ P2§1.3 R7 风险项，
  与本节实测 P2§4 键清单（P3 运行器 + P5 五命令 + 各 timeout 后缀键，无任何
  `P3_xxx` 形态键）逐键核对一致；P2§4 引用「P3 为合法阶段 + 合法后缀」的规避路径
  正是 DEBT0023 evidence 第 3 条所述机制。P2 靠约定规避、DEBT0023 登记协议层缺口待
  后续任务收口——两者关系自洽，无契约冲突。P7 时点判定：一致（DEBT0023 保持 open
  正确，本任务不承担其 closure_criteria）。

## 4. 未决项清零

- **P1-requirements.md**：行首残留标记 grep 实测——NEED_CONFIRM 残留 0 处（仅
  [NO_NEED_CONFIRM] 确认标记，P1:84）；阻断标记 0 处；严重偏差标记 0 处；
  SCOPE+ 0 处（§2 已核）。
- **P4-implementation.md §3.2 阻塞上报（测试探测缺陷）已解决**：证据链三方在案——
  ①P4-progress.md:43「主 Agent 定夺到达：授权修两个测试文件的探测机制……断言语义/
  用例逻辑不动」+ :54「P4-implementation.md 已更新：§3.2 末尾补【已解决·主 Agent 定夺】
  行」；②P4-implementation.md:55 终态记录「组合 27 passed（14+13）+ gate 回归
  182 passed + ruff All checks passed」；③P4-review.md 核查项 8 机械验证（git diff
  HEAD=2225634 对照，`assert` 行零改动、无 skip/xfail 增改，改动逐项归类 ∈ 授权三类
  无第四类）+ 核查项 10 追认「后续阶段不再追溯」。**结论：已解决**，无遗留阻塞。
- **P6/P6.5**：P6 frontmatter fail: 0、Summary 13/13 PASS、无 FAIL 项与"修复后 PASS"
  情形（P6:61）；P6.5 status: passed / partial: false，独立重放 13/13 一致——无
  NEED_CONFIRM 残留、无阻断 / 严重偏差标记残留。
- **本文件**：无阻断标记、无严重偏差标记（frontmatter
  blocker_count=0 / deviation_count=1 / deviation_critical_count=0）。

## 5. CODE-MAP 核对（3 新增文件逐条）

对照 agents/CODE-MAP.md（存在，CODE-MAP 机制采用中）与 P4「新增文件核对表」
（P4-implementation.md:57-63，3 个新增文件均附 [CODE_MAP_EXEMPT] 理由）逐条人工判定
（ADR-003：不做跨语言静态依赖分析）：

[CODE_MAP_SYNC:] agate/scripts/check-maintainability.py——P4 申报豁免理由「CODE-MAP
关键文件为导航式清单，同类检测脚本均无专条」与 CODE-MAP.md「关键文件」节实测相符：
该节仅 5 条导航式条目（WORKFLOW.md / dispatch-protocol.md / state-machine.md /
role-system.md / check-gate.py），gate/一致性族同类检测脚本（check-pruning.py 未被
点名、仅由 gate 族「等」隐含；agate-risk-score.py / check-routing.py /
check-judge-verdict.py 仅在 scripts 模块叙述中以家族/机制族形式提及）均无「关键文件」
专条；本脚本属 gate/一致性族新成员，落位 within agate/scripts/ 与模块划分一致，无
依赖方向偏离——同步成立。

[CODE_MAP_SYNC:] agate/assets/templates/known-violations-template.md——P4 申报豁免
理由「CODE-MAP 以目录粒度登记 templates 层，不逐模板列条」与 CODE-MAP.md「templates」
节实测相符（以目录粒度 + 等列举 11 个模板文件名，无逐模板条目；known-failures 类
既有模板同样无专条）；层级归属 within agate/assets/templates/ 无偏离——同步成立。

[CODE_MAP_SYNC:] agate-workspace/maintainability.yaml——P4 申报豁免理由「任务工作区
数据文件（对齐 ADR-009），非代码结构，CODE-MAP 不覆盖」与 CODE-MAP.md 实测相符
（其覆盖范围 = agate/ 协议本体四层，agate-workspace/ 数据面不在描述对象内；CODE-MAP
「关键文件」节与依赖方向节均只涉及协议层文件）——同步成立，无 CODE_MAP_DRIFT 判定。

核对通过 3/3（code_map_new_files_count=3 / code_map_reviewed_count=3，无未配对项）。

## 6. 审查总表

| 检查项 | 结论 | 锚点 |
|---|---|---|
| DESIGN_GAP 配对 | 1/1 REVIEWED（§1） | P4§3.1 ↔ P7§1 ↔ P4-review 核查项 3.1 ↔ check-gate.py:162-185 ↔ agate-risk-score.py:46-54 |
| SCOPE+ 闭环 | 零条目，无需闭环动作（§2） | P4§5 ↔ P1:84 ↔ P4-review 核查项 10 |
| BDD 数量与内容 | 13 = 13 = 13，抽查 4 条逐项吻合（§3.1） | P1§7 ↔ P6§2 ↔ P6.5 frontmatter ↔ bdd-7/9/12/13.log |
| packages 与 bump 范围 | 四包落点齐备，无越界（§3.2） | P1/P2 frontmatter ↔ P4§6 ↔ P4-review 核查项 10 |
| 实现路径 vs 设计 | M1-M8 逐点吻合（§3.3） | P2§3.1/3.2/3.3/3.5 ↔ check-gate.py:162-185/932-968 ↔ consistency.py:753 ↔ summary.py:50 |
| gate_commands vs 实跑 | 5/5 键一致 exit 0（§3.4） | P2§4 ↔ P5§1-5 |
| 卡片改动 vs gate 行为 | 三处 wording 与行为对应（§3.5） | P2§3.4 ↔ P4 卡 :112/:150 ↔ P6 卡 :230 ↔ bdd-13.log |
| DEBT0023 契约 | 无 P3_xxx 键，登记与规避自洽（§3.6） | tech-debt.md:814-841 ↔ P2§1.3 R7 ↔ P2§4 |
| 未决项清零 | 全清零，P4 阻塞已解决（§4） | P1:84 ↔ P4:55 ↔ P4-progress:43/54 ↔ P4-review 核查项 8/10 |
| CODE-MAP | 3/3 SYNC，无 DRIFT（§5） | CODE-MAP.md ↔ P4 核对表三行 |

## 7. 偏差记录（非阻断）

[DEVIATION: P3-test-cases.md §4 汇总行用例计数与该文件自身映射表及 P5 实测不一致——
汇总行称"M9 10 BDD 用例 + 5 契约用例 = 15；M10 11 用例；合计 26 用例"，而该文件
§2/§3 映射表逐条函数清单与两测试文件 `^def test_` 实测为 M9 14（9 BDD + 5 契约）、
M10 13、合计 27；P5§3 count-tests 实测 1335 = P0 基线 1308 + 27、P4§2/§3.2 终态
27 passed（14+13）相互印证，27 为权威数。性质：P3 文档汇总行算术口径瑕疵，BDD
13/13 覆盖映射逐条在案无缺口，红灯 / 绿灯记录均以实测 27 为准，不影响任何 gate
判定与验收结论。级别：WARNING 级非阻断；建议主 Agent 择机订正该汇总行或留痕说明，
P7 只审不写、不代改。]

除上述 1 条外无其他偏差（deviation_count=1 / deviation_critical_count=0）。

## 8. 结论

**P7 一致性审查通过**：阻断与严重偏差均为零（blocker_count=0 /
deviation_critical_count=0），普通偏差 1 条（WARNING 级非阻断，见 §7）；DESIGN_GAP
1/1 全配对 REVIEWED；SCOPE+ 零条目闭环成立；跨文件十项检查全部以源文件节名锚点给出
非裸判定；CODE-MAP 3/3 同步。P1-P6 产出与实现未发现阻断级偏离，可进入 P8（发布前
机械步骤，roadmap 回写 done 为 RM-AG0043 硬校验）。
