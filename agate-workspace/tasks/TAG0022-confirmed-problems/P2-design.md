---
phase: P2
task_id: TAG0022-confirmed-problems
type: design
parent: P1-requirements.md
trace_id: TAG0022-P2-20260822
status: draft
created: 2026-08-22
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [agate]
domains: [backend]
ui_affected: false
# ── v2.0 派发编排字段 ──
# 4 执行批（RM-AG0040 为文档交付，计划落于本文件 §5.4，无 P4 代码批）。
# 依赖：B-judge 须在 C-migration 之后串行（0038 需先注册 agate-md-field-get 的 created op、
# 且 judge 块是叠加在 0038 重构后的 gate_p1 之上）；A/D 与 C 文件不重叠，可并行。
dispatch_plan: {mode: static-batch, parallel_limit: 4, batches: [{id: A-ruff, complexity: low}, {id: B-judge, complexity: medium}, {id: C-migration, complexity: high}, {id: D-env-tests, complexity: medium}]}
---

# P2 方案设计 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 状态标记：[PROD_NOT_TOUCHED]（本阶段仅读稳定版/worktree 协议文件与代码，写操作全部落在 worktree `agate-workspace/` 内）
> 上游：P1-requirements.md（BDD-1..10，§4 四组扫描，§5 D1-D4）/ P1-review.md（approved + N1/N2/N3）/ tag0019-21-analysis.md / HANDOFF-TAG0022.md

## 0. 输入读取与最小验证摘要（证据链）

| 项 | 结论 | 证据 |
|----|------|------|
| N1（0039 校验强度） | **fail-closed：机制后新任务缺 `judge.enabled: true` → check-gate P1 exit 1** | 理由见 §4.3；对齐 gate_p65 缺 verdict exit 1 与「缺失必填字段」惯例（P1-review N1） |
| N2（basetemp 写可性） | **`/home/kity/oclab/dsh-workspace/ptmp` 可写，冻结为权威仓库外 basetemp** | 实证：在 ptmp 实建/删除 probe 文件成功（§8 minimal_validation） |
| N3（count-tests 基线） | **冻结 1202**（本 worktree `count-tests.sh` 实测 = 1202） | P6 判据以 1202 为「只增不减」下界，防漂移 |
| 0038 结构化读取路径 | **可打通** | `read_rules_yaml(phases.yaml)` 10 阶段解析 OK；`known_phase_ids`/`is_legal_gate_key` OK；`agate-md-field-get domains` 对 P1 文件返回 `backend`（§8） |
| 0041 git 上下文隔离 | **GIT_CEILING_DIRECTORIES 有效** | 实测：探针目录在 git 仓库内，设 ceiling 后 `git rev-parse --show-toplevel` rc=128（§8） |

---

## 1. 影响面梳理（候选方案之前，强制节）

> 依据：P1 §4 四组扫描（grep 证据）+ P1 §5 范围表 + 本阶段对实现代码的逐文件核对（check-gate.py 全文件 1258 行实读）。

### 1.1 改什么（Modify）——逐文件逐小节

| # | 文件 | 改动点（小节/函数） | 归属子项 | 关联 BDD |
|---|------|---------------------|---------|---------|
| M1 | `.github/workflows/protocol-tests.yml` | `ruff:` job（L106-116）：job name 固化 `ruff`（不改名）；`pip install ruff` → 锁版本 `ruff==0.16.4`（与本地 `~/.venvs/agate-dev/bin/ruff` 对齐，BDD-2 对齐语义实体化） | 0037 | BDD-1/2 |
| M2 | `agate/scripts/check-gate.py` | **0038 迁移面**：①A 组——`_frontmatter_field`（L164-170 定义 + 10 处使用：L500/506/716/722/768/1108/1109 等）整体移除，改走 `_md_field_get`（新注册 op）；17 处 `_md_field_get` 调用保留（已是结构化路径）；②B 组——行首标记正则 `_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE`（L101-110）及其计数逻辑（L523-584）迁至 agate_common 共享读取器；③C 组——任务产出格式判定正则（BDD 标题 L390 / UI 区块 L417-462 / candidate_count L693 / design_trivial L703 / 权衡关键词 L736 / P6 行首 PASS-FAIL L946-954 / P7 BLOCKER-DEVIATION L1015-1023 / DESIGN_GAP L1048-1088 / CODE_MAP L1127-1135 / fail-list 代码块 L875-887 / known-failures 表格 L909 / P4 关键词 L1060）迁至共享读取器；④D 组——内嵌 yaml 块解析（L336-338）迁至共享函数；⑤**0039 校验点**——gate_p1 新增 judge 校验块（读 `.state.yaml` judge 块 + P1 `created` 字段 + rules `judge_required_since`，机制后新任务缺/未启用 → exit 1） | 0038 + 0039 | BDD-3/4/5、BDD-6/7 |
| M3 | `agate/scripts/agate_common.py` | 新增共享 md 解析读取器（B/C/D 组单点）：标记行计数、BDD 标题提取、UI 区块解析、P6/P7 计数、fail-list 块、嵌 yaml 块；沿用「已迁移解析点不在消费脚本字面出现」模式（对齐 parse_gate_commands_block，BDD-9 先例） | 0038 | BDD-3 |
| M4 | `agate/scripts/agate-md-field-get.py` | KNOWN_OPS 注册新 op：`status`/`agent`（review 文件 frontmatter-only → NO_FALLBACK_STRING_FIELDS）、`project_phase`（NO_FALLBACK_STRING_FIELDS）、`code_map_new_files_count`/`code_map_reviewed_count`（NO_FALLBACK_INT_FIELDS，解 L1098-1107 DESIGN_GAP 遗留）、`created`（NO_FALLBACK_STRING_FIELDS，0039 日期判据用） | 0038（+0039 判据依赖） | BDD-3/4、BDD-6/7 |
| M5 | `agate/scripts/check-structure-consistency.py` | S-3 收紧（双向 gate 命令一致性）：phases.yaml `gates[].check` 补命令串（P1-P8 各阶段）+ S-3a（YAML→md：gate 命令须在卡片 `## gate 规则` 出现）+ S-3b（md→YAML：卡片机器可判定 gate 行须在 YAML 声明） | 0038 | BDD-5 |
| M6 | `agate/rules/phases.yaml` | 各阶段 `gates[].check` 增补实际 gate 命令串（与卡片 `## gate 规则` 对应，命令即规则，入 YAML 权威源） | 0038 | BDD-5 |
| M7 | `agate/rules/dispatch.yaml` | 新增 `judge_required_since: "2026-08-22"`（机制后强制日期，YAML 权威判据）；`dispatch.schema.json` 同步 | 0039 | BDD-6/7 |
| M8 | `agate/state-machine.md` | L442-443 judge 模板语义：「P1 初始化时主 Agent 写入；缺失/false = 历史任务」→「机制后新任务（P1 created ≥ judge_required_since）必须含 `judge.enabled: true`（check-gate P1 机械校验）；历史任务（created < 截止或未声明）缺块 → 跳过」；P6.5 硬边界/早退语义不改 | 0039 | BDD-6/7 |
| M9 | `agate/phase-cards/P1-requirements.md` | 产出规格 checklist 新增「judge 启用声明」条：新任务 P1 初始化须在 `.state.yaml` 写 `judge.enabled: true`（check-gate P1 校验，judge_required_since 起强制）；frontmatter 样例注释同步 | 0039 | BDD-6 |
| M10 | `agate/UPGRADING.md` | 新增 TAG0022 版本章节：① ruff required check 配置步骤（RM-AG0037）；② 权威源切换（YAML 为规则唯一来源，md 禁止承载可判定规则）为脚本行为破坏性变更（RM-AG0038）；③ judge 强制化 P1 校验（RM-AG0039） | 0037/0038/0039 | BDD-1/8、P8 清单 |
| M11 | `agate/tests/unit/test_check_gate.py` | 新增 0039 judge P1 校验用例（机制后缺块/未启用 → exit 1；历史跳过 → exit 0/2；含 `judge.enabled: true` → 放行） | 0039 | BDD-6/7 |
| M12 | `agate/tests/unit/test_md_parse_scan.py`（新增） | BDD-3 静态扫描测试：扫描 check-gate.py，A/B/C/D 组模式清单命中数 = 0 | 0038 | BDD-3 |
| M13 | `agate/tests/unit/test_check_routing.py` | `test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`（L148-156）改：run_cli 注入 `GIT_CEILING_DIRECTORIES=<tmp_path>`，非 git 上下文确定化 | 0041 | BDD-9/10 |
| M14 | `agate/tests/unit/test_env_adapt_docs.py` | `test_bdd_25_consistency_zero_error`（L47-60）改：basetemp 在仓库根下时注入排除 env（见 M15），使一致性检查免疫会话污染 | 0041 | BDD-9 |
| M15 | `agate/scripts/check-protocol-consistency.py` | `iter_md_files`（L119-138）新增 opt-in 排除钩子：env `AGATE_CONSISTENCY_SKIP_DIRS`（相对根路径列表）在扫描时跳过（默认关闭、行为不变）——test_bdd_25 的仓库内 basetemp 污染根治使能 **[SCOPE+，见 §1.4]** | 0041 | BDD-9 |

### 1.2 不改什么（Not Modify）——显式边界

| # | 文件/范围 | 不改的理由 |
|---|----------|-----------|
| N1 | P6.5 judge 链：`pre-commit-gate.py` 2i.1（L386-394）/ `ci-gate-backstop.py` / `gate_p65`（check-gate L972-996）消费语义 | 0039 只新增 P1 侧校验点，P6.5 commit-time 硬边界与 skip-历史语义保持（P1 §4.3 扫描 3 判定「本次不处理」）；gate_p65 的「无 judge 块 → 早退 0」逐字节不变 |
| N2 | ceremony 机制本体：`check-routing.py` / `agate-risk-score.py` / pre-commit 2j.1 | RM-AG0040 只要求实证收尾（计划+触发），不改机制（P1 §4.4 扫描 4；P0-brief D4） |
| N3 | `.state.yaml` 读取（E 组，`_load_state_yaml` L230-241 / gate_p65 L982-983）与 git/CHANGELOG 输出解析（F 组，L1162-1230） | D2 判定口径：非 md 规则读取（YAML/工具输出），不计入「零 md 解析」面；迁移不触碰 |
| N4 | `pyproject.toml` ruff 规则集配置（[tool.ruff] L1,6） | 规则集是运行参数非强制点（P1 §4.1 扫描 1 判定「本次不处理」） |
| N5 | `check-gate.py` 退出码语义/CLI 契约（0/1/2 + OLD_PHASE 回退检测）、P0/P3/P4/P5/P8 分支判定逻辑 | H12：P1 gate 既有锚点格式/判定语义不得回归；迁移只换读取方式不换判定口径 |
| N6 | 除 check-gate.py 外其余脚本的 grep 解析残留（分析文档「53 脚本大量 grep 残留」） | D2 验收锚 = check-gate.py 零 md 解析；「等核心脚本」为延伸愿景，不在本任务 BDD 内（roadmap 后续批次承接） |
| N7 | P6 卡 judge 条文（L21/178/209）「P6.5 强制所有任务」宣称 | 条文保持；正是该「宣称无机械兑现」由 0039 的 P1 校验补齐（P1 §4.3 扫描 3 判定「本次不处理」）；如需措辞微调仅限 P2 定案后的语义对齐，不改机制 |
| N8 | `.gitignore` / `.gitattributes` / shellcheck 薄壳（3 个 hook sh） | 本任务无新增 hook 需求；ruff 无 pre-commit 消费（P1 §4.1 关键佐证） |

### 1.3 风险在哪（Risk）——每条配缓解

| # | 风险 | 缓解 |
|----|------|------|
| R1 | **0038/0039 同文件互扰**：都改 check-gate.py（0038 重构 gate_p1 解析层，0039 往 gate_p1 加 judge 块） | 分批纪律 D3：C-migration 先（注册 created op + 重构解析层），B-judge 后（纯叠加 judge 块于重构后基础）；批文件集不交叉（§6） |
| R2 | **工具链自举**：迁移后的 check-gate.py 用未发布的共享读取器判自己，P1/P2 gate 红 | 迁移期每步全量测试先绿再 commit；gate 命令在 P2 固化，P3 红→P4 绿；共享读取器行为与旧内联实现逐字节等价（回归兜底：既有 1202 用例全绿） |
| R3 | **fixture 兼容回归（H10）**：conftest/create_task_dir 构造的 md 夹具在迁移后读不到字段 | 共享读取器保留旧格式正则回退（双轨：frontmatter 优先 + 正文回退），既有夹具语义不变；预计 conftest 零改动，P5 全量验证 |
| R4 | **S-3 收紧误伤既有条文**：卡片 `## gate 规则` 措辞与 phases.yaml gates 命令串非逐字对应 → 基线红线 | P3 先对新 S-3 检查跑基线验证（10 张卡逐一核对），不逐字匹配处按「机器可判定命令行」模式匹配；确实缺漏时补卡片 gate 串（md 侧对齐 YAML，正是收紧语义）；`--strict-errors-only` 沿用 |
| R5 | **0039 判据边界**：created 缺失/格式异常的机制后任务被误判为历史 → 漏拦 | 默认值定 `created` 缺失 → 按历史跳过（fail-open，兼容存量）；P1 卡强制新任务写 created + judge（软层兜底）；judge_required_since 在 rules YAML 可调（若用户要求更严可改判据） |
| R6 | **0041 的 M15 排除钩子改变一致性扫描面** | 默认关闭（无 env 不排除），行为逐字节不变；仅 test_bdd_25 在 basetemp ∈ 仓库根时注入；新增该钩子的单元测试（扫面变化可观测） |
| R7 | **CI 行为验证滞后**：workflow 改动（M1）合并后 CI 行为才暴露 | CI 改动保守（仅锁版本 + job name 固化）；合并后 P8 验证 CI 全绿（版本发布清单第 6 步）；required check 勾选由用户配置（D1 边界） |
| R8 | **count-tests 漂移（H7）**：新增用例叠加致 P6 判据移动 | N3 冻结 1202 为下界，「只增不减」硬约定；每次 commit 前跑 count-tests |

### 1.4 [SCOPE+] 声明

```
[SCOPE+] 发现：test_bdd_25 在「仓库内 basetemp」位置失败的根因是 check-protocol-consistency.py
         iter_md_files 扫描了 basetemp 目录下预存测试生成的坏引用 fixture .md（TAG0020
         known-failures.md 条目 2 实证）。
         必须做的理由：BDD-9 要求「仓库内默认 basetemp」与「仓库外显式 basetemp」两种位置
         全量 0 失败；仅靠测试侧改（clean-copy）会破坏 CHECK 7 的 git 依赖（main() 强制
         root 为仓库根，L1118 校验 root/agate/WORKFLOW.md），因此需给 iter_md_files 加
         最小 opt-in 排除钩子（env AGATE_CONSISTENCY_SKIP_DIRS，默认关闭、行为不变）。
         影响：M15 文件（check-protocol-consistency.py）进入改动面；不新增 BDD（归属
         BDD-9 验收口径内）；若主 Agent 不接受该产品文件改动，备选 = 仅外部 basetemp
         验证（BDD-9 仓库内位置降级为声明性要求），但「任意 basetemp 0 失败」锚将打折。
```

---

## 2. 候选方案（candidate_count=2）

> 场景类型：常规功能 + 迁移重构（follows_existing_pattern = M2 已迁移的 gate_commands 族模式，但适配面大，按「设计模式」方法论探索 2 个真候选）。

### 候选 1：共享库单点化（agate_common import + agate-md-field-get op 扩展）——推荐

**方案**：A/B/C/D 组的 md 解析逻辑全部迁出 check-gate.py——B/C/D 组成为 `agate_common.py` 的共享读取器函数（与 `parse_gate_commands_block` 同款）：`count_markers(text, kind)`（NEED_CONFIRM/SUGGEST/NO_NEED 计数 + 描述提取）、`extract_bdd_titles(text)`、`extract_ui_design_section(text)`、`count_p6_pass_fail(text)`、`count_p7_markers(text)`、`parse_fail_list_block(text)`、`extract_embedded_yaml_blocks(text)`；A 组 `_frontmatter_field` 删除，全部经 `agate-md-field-get.py`（注册 status/agent/project_phase/code_map_*/created op）。旧格式正文回退语义保留在共享函数内（行为逐字节等价）。

**权衡**：
- 优点：① 完全对齐 M2 先例（BDD-9「已迁移解析点在消费脚本零字面出现、落在公共库单点」）；② 行为逐字节等价 → 既有 1202 用例回归风险最小（H10/H12 双满足）；③ 防漂移单点：未来任何脚本要读任务 md 格式，改一处即全局生效；④ 无 subprocess 开销（import 直调）。
- 风险：agate_common 体量增长（新增一批读取器）；迁移是机械但面广（47 处正则行 + 10 处 frontmatter 读），需按组推进；P4 实现者需精读现有解析语义防行为漂移。
- 工作量：中-高（candidate A 内最大块）。

### 候选 2：读取器工具化（独立脚本 agate-task-md-parse.py + subprocess 调用）

**方案**：仿 `agate-md-field-get.py` 工具族，新增独立 CLI 脚本 `agate-task-md-parse.py`（`op TASK_FILE` 输出结构化结果），check-gate.py 经 subprocess 调用（复用 `_md_field_get` 式调用封装，失败回退空值）。

**权衡**：
- 优点：① 进程隔离——check-gate 主进程不加载解析代码本体；② 工具复用面更广（53 个脚本里的 grep 残留脚本未来可直接换用同一工具）；③ CLI 工具风格与既有工具族一致，P4 可独立单测工具本身；④ 不膨胀 agate_common。
- 风险：① 每次 gate 运行增加 N 次 subprocess（现 17 次 `_md_field_get` 已是子进程，再叠加标记/格式计数，一个 phase 分支可能 30+ 子进程——P1/P6/P7 gate 延迟明显）；② 输出契约（字符串/换行/JSON）在 6+ 个消费点间同步成本高；③ 工具与 agate_common 的既有共享读取器并存 → 「两套读取范式」漂移新风险。
- 工作量：高（新工具 + 调用封装 + 双轨测试）。

### 选择理由（候选 1 胜出）

候选 1 在「对齐既有架构」（M2 先例明确指向公共库单点）、「回归风险」（逐字节等价迁移，1202 用例兜底）、「延迟/复杂度」三个维度全面优于候选 2；候选 2 的「进程隔离/多脚本复用」优点在本任务验收锚（仅 check-gate.py 清零，D2）面前价值有限——其他脚本的 grep 残留明确不在本任务 BDD 内（N6）。按 YAGNI，不为「未来 53 脚本迁移」预设候选 2 的工具架构；候选 1 的共享函数同样可被未来批次复用（import 比 subprocess 更轻）。**最终采用候选 1。**

> 0039 判据（日期截止 vs 仅 presence）与 0041 修复（GIT_CEILING_DIRECTORIES vs 分支跳过、排除钩子 vs clean-copy）作为子决策在 §4 内给出权衡与定案，不重复列主候选。

---

## 3. 完成标准（供 P3/P5/P6 使用的可判定口径）

- **RM-AG0037（BDD-1/2）**：① `protocol-tests.yml` 存在 `name: ruff` job（引用名稳定）+ `ruff==0.16.4` 锁版本，diff 可见；② UPGRADING/AGENTS 含「将 ruff job 勾选为 PR required check（维护者配置）」步骤文本；③ P5/P6 `ruff check agate/` 两次均 exit 0。
- **RM-AG0038（BDD-3/4/5）**：① test_md_parse_scan.py 静态扫描 check-gate.py，A/B/C/D 模式清单命中 = 0；② 全量 pytest 0 failed（外部 basetemp）；count-tests ≥ 1202；consistency 0 ERROR；structure 0 ERROR；③ 人为单侧漂移（卡片加 gate 行不入 YAML / 改 YAML gate 不动卡片）→ structure 非 0 报 S-3；双侧一致 → exit 0。
- **RM-AG0039（BDD-6/7）**：① 机制后新任务（P1 `created ≥ judge_required_since`）缺 judge 块或 `judge.enabled` 非 true → `check-gate.py P1 <dir>` exit 1 + stderr 提示；② 含 `judge.enabled: true` → 原语义放行（exit 2）；③ 历史任务（created < 截止 / 未声明）无 judge 块 → exit 0/2 不被拦；④ state-machine L442-443 与 P1 卡条文已更新；⑤ gate_p65/2i.1/ci-backstop 消费语义逐字节不变（既有 judge 三态用例 L2663-2689 保持绿）。
- **RM-AG0040（BDD-8）**：§4.4 实证执行计划含四要素 + 触发条件，各可二值判定（P2 交付，P6 核对）。
- **RM-AG0041（BDD-9/10）**：① 仓库内默认 basetemp 与仓库外 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider` 两种位置全量 pytest 0 failed；② `check-platform-assumptions.py` 全树 0 R1-R5 命中；修改点 diff 无裸 `PATH=`/裸 `python3`/POSIX symlink 硬假设/`/tmp` 字面。

---

## 4. 五子项设计

### 4.1 RM-AG0037 — ruff 合并强制（BDD-1/2）

- **实现侧动作**（D1 边界）：workflow 的 `ruff` job 保持稳定 job name + `pip install ruff==0.16.4`；UPGRADING 新章节 + AGENTS.md 写「required check 配置步骤」（GitHub 分支保护 → 勾选 ruff check）。required 勾选本身由维护者（用户）执行，不写进 BDD-1 When。
- **不改**：pyproject.toml 规则集（N4）；pre-commit 无 ruff 消费（P1 §4.1 佐证）→ 不新增 hook。
- **回归拦截**：BDD-2 双跑 `ruff check agate/` 全绿 + 合并后 CI ruff job 绿（P8 验证）。

### 4.2 RM-AG0038 — M2 迁移闭环（BDD-3/4/5）

#### 4.2.1 逐点映射清单（A/B/C/D 组 → YAML 字段/读取器）

> 判定口径（D2）：E/F 组不计入零 md 解析面；迁移后 check-gate.py 内 A/B/C/D 组字面解析点 = 0。

| P1 §4.2 分组 | check-gate.py 现解析点（实证行号） | 迁移目标（YAML 字段/读取器） | 改用方式 |
|-------------|----------------------------------|---------------------------|---------|
| A | `_frontmatter_field` L164-170，使用 L500(status)/L506(agent)/L716(status)/L722(agent)/L768(project_phase)/L1108-1109(code_map_*) | agate-md-field-get.py 新 op：`status`/`agent`/`project_phase` → NO_FALLBACK_STRING_FIELDS；`code_map_new_files_count`/`code_map_reviewed_count` → NO_FALLBACK_INT_FIELDS（解 L1098-1107 DESIGN_GAP 遗留） | `_md_field_get("status", file)` 等 |
| A | `_md_field_get` 17 处调用（L327/380/381/412/471/533/554/606/929/931/939/940/1005/1006/1030/1031/471-ish） | 已是结构化读取（agate-md-field-get 双轨：frontmatter 优先 + 正文回退） | 保留；无字面正则 |
| B | `_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE` L101-110 + 计数 L523-584 | agate_common 共享读取器 `count_markers(text, kind)`（逐字节同正则）+ 描述提取 | import 调用 |
| C | BDD 标题 L390；UI 区块 L417-462；candidate_count L693-694；design_trivial/follows L703；权衡关键词 L736；P6 行首 L946-954；P7 L1015-1023；DESIGN_GAP L1048-1088；CODE_MAP L1127-1135；fail-list L875-887；known-failures 表 L909；P4 关键词 L1060 | agate_common 共享读取器：`extract_bdd_titles` / `parse_ui_design_section` / `scan_fm_line`（candidate_count/design_trivial）/ `count_p6_pass_fail` / `count_p7_markers` / `count_design_gap` / `count_code_map_lines` / `parse_fail_list_block` / `count_kf_entries` / `has_keyword`；`count_p2_declared_fields` 已共享（L730） | import 调用；新格式（frontmatter 计数）路径保持 `_md_field_get` |
| D | 内嵌 yaml 块 `re.finditer(r"```(?:yaml\|yml)...")` L336-338（_gate_p1_vision_capability 兜底） | agate_common `extract_embedded_yaml_blocks(text)`（同正则单点）；首选 `read_vision_tri_state`（L331-332 已走共享） | import 调用 |

#### 4.2.2 S-1~S-6 收紧（BDD-5）

- **S-3 双向 gate 命令一致性**（check-structure-consistency.py）：
  - 数据面：phases.yaml 各阶段 `gates[].check` 增补实际 gate 命令串（如 P1 → `check-gate.py P1 $TASK_DIR`；P5 → `gate_commands.P5`；P6.5 → `check-judge-verdict.py + check-events.py`）。
  - S-3a（YAML→md）：每阶段 `gates[].check` 中的命令串须出现在对应卡片 `## gate 规则`（或推进条件）节。
  - S-3b（md→YAML）：卡片 `## gate 规则` 节中机器可判定命令行（匹配 `check-gate.py P\d+` / `gate_commands.P\d+` / `check-[\w-]+\.py` 模式）须在该阶段 gates[].check 有声明。
  - BDD-5 单侧漂移构造：卡片加红线行不入 YAML → S-3b ERROR；改 YAML gate 命令不动卡片 → S-3a ERROR。
- **静态扫描兜底（BDD-3）+ S-4 字段登记**：test_md_parse_scan.py 按 §4.2.1 映射清单的模式库存扫 check-gate.py；dispatch.yaml `field_readers` 行保持（S-4 已校验登记字段 ⊆ 已知词表）；新增 op 的登记随 agate-md-field-get KNOWN_OPS 扩展，S-4 的已知词表（_TASK_FRONTMATTER_FIELDS）在 check-structure-consistency.py 同步补 status/agent/project_phase/code_map_*（防 S-4 误报）。

#### 4.2.3 既有测试兼容（H10）

共享读取器保留正文回退 → conftest create_task_dir 的旧格式夹具（无新字段）语义不变；预计 conftest 零改动；P5 全量 1202+ 用例回归验证。fixture 无需「桥接新字段」——迁移保持双轨向后兼容，这是相对「全结构化切换」候选 2 的额外回归收益。

### 4.3 RM-AG0039 — judge 启用强制化（BDD-6/7）

#### 4.3.1 N1 校验强度定案（P2 冻结）——**fail-closed exit 1**

理由：① BDD-6 Then 字面「非 0 退出（阻断）」——fail-closed 直接满足，无需「二值判定以 exit code + stderr 兜底」的语义解释；② 对齐既有惯例：gate_p65 缺 verdict → exit 1（fail-closed）、P1-review 缺/非 approved → exit 1（缺失必填字段）——judge.enabled 对机制后新任务升级为必填字段；③ 「高优 WARNING」路径 exit 0 会与 BDD-6 的「被拦」锚字面冲突（P1-review N1 明示），且靠主 Agent 自觉兑现仍是软强制——正是本 issue 要消灭的形态。

#### 4.3.2 判别机制（区分「机制后新任务」与「历史任务」）

- 判据：rules/dispatch.yaml 新增 `judge_required_since: "2026-08-22"`（机制发布日，ISO 字符串）；P1-requirements.md frontmatter `created`（agate-md-field-get `created` op 读取）。
- 判定（gate_p1 新增块）：
  1. `judge = _load_state_yaml(task_dir).get("judge")`；
  2. `judge` 为 dict 且 `enabled` truthy → 放行（继续原 P1 判定，exit 2 语义不变）；
  3. `judge` 为 dict 且 enabled falsy → **exit 1**（「judge 已声明但未启用」）；
  4. `judge` 缺失 → 读 P1 `created`：`created` 为 ISO 日期且 `>= judge_required_since` → **exit 1**（机制后新任务缺 judge 块）；否则（pre-cutoff / created 缺失或非 ISO）→ 跳过（历史兼容，fail-open 默认，R5 缓解）。
- 二元测试构造（P3）：BDD-6 fixture = P1 frontmatter `created: 2026-08-22` + `.state.yaml` 无 judge 块 → exit 1；BDD-7 fixture = P1 `created: 2026-08-19`（或无 created）→ exit 0。

#### 4.3.3 文档面同步

state-machine.md L442-443 模板语义更新（M8）+ P1 卡产出规格新增 judge 声明 checklist（M9）；P6 卡条文不改（N7），其「强制所有任务」宣称由 P1 机械校验兑现。

### 4.4 RM-AG0040 — M3 实证收尾（BDD-8，文档交付）

#### 4.4.1 实证执行计划（M3 四要素 + 触发条件，本 task 验收锚）

| 要素 | 指标 | 采集/判定口径 |
|------|------|--------------|
| ① 评审轮数 | 薄任务在 P2/P4 派发的 LLM 评审 subagent 轮数（含重试轮） | 从薄任务 .state.yaml `retries[P2]/retries[P4]` + gate-events.jsonl 派发事件计数；每轮 1 次事件记录 |
| ② 真实发现数 | 评审产出中被采纳/阻止真实问题的条数 | 评审文件（P2-review.md/P4-review.md）中标注 BLOCKER/被采纳建议 + 主 Agent 采纳记录；排除非阻塞建议与机械可抓项（明确剔除：count-tests 基线类、gh 轮询类等机械项） |
| ③ TAG0018 基线值 | 4 场 LLM 评审 ≈ 0 净收益（17 非阻塞 + 1 真实且机械可抓） | 基线冻结值（tag0019-21-analysis.md/ TAG0018 复盘）；薄任务结束后对照 |
| ④ 不达标决策规则 | 「LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard」 | 二值判定：真实发现数 = 0 且 BDD-3（静态扫描）/BDD-5（S-*）等机械 gate 覆盖同类 → 主 Agent 批准回滚 thin→standard |
| ⑤ 触发条件 | 下一个 low 风险任务 / 用户指定薄任务真跑 `ceremony: thin` | 触发后该任务按 check-routing thin 流程实战并产出实证对比报告（评审轮数 vs 真实发现数，对照 TAG0018 基线）；报告在触发任务 P6 交付 |

**已知边界（写入计划）**：check-routing.py 只校验 ceremony 声明格式/要素，不校验「thin 档是否真跳过评审」的执行语义（P1 §4.4 扫描 4 实证）——观测手段 = 薄任务的派发事件与评审文件清单核对（gate-events.jsonl + tasks 目录评审文件存在性），不新增 gate 脚本（D4）。

### 4.5 RM-AG0041 — 环境假象测试根治（BDD-9/10）

#### 4.5.1 test_bdd_7（test_check_routing.py L148-156）——git 上下文确定化

- **方案**：run_cli 注入 `env={"GIT_CEILING_DIRECTORIES": str(tmp_path)}`——git 从 `tmp_path/task` 向上发现仓库时在 `tmp_path` 处截止 → `git rev-parse --show-toplevel` 失败 → `git_ok:false` → thin + 算分异常 → exit 1（隔绝不依赖 basetemp 位置的确定断言）。
- **权衡（子决策）**：备选「探测环境分支断言」（tmp 在仓库内则 skip）——语义真实但仓库内位置失去该分支覆盖；备选「默认 basetemp 扫码」——依赖外部目录布局。GIT_CEILING_DIRECTORIES 是 git 核心机制（跨平台 Git 都支持），已实测有效（§8），两种 basetemp 位置下分支均真实覆盖。**定案：GIT_CEILING_DIRECTORIES**。
- 平台无关：无裸 python3/PATH 假设；环境 var 注入经 run_cli env 参数（conftest `_run_cli_impl` 已支持）。

#### 4.5.2 test_bdd_25（test_env_adapt_docs.py L47-60）——一致性检查免疫 basetemp 污染

- **根因**（TAG0020 known-failures.md 条目 2）：全量会话中预存测试在 `agate-workspace/.pytest-tmp/test_*/` 生成坏引用 fixture .md；check-protocol-consistency.py `iter_md_files`（root=仓库根，main() L1118 强制）扫描到 → CHECK 2 误收。
- **方案**：check-protocol-consistency.py `iter_md_files` 新增 opt-in 排除：env `AGATE_CONSISTENCY_SKIP_DIRS=<相对根路径列表>`（默认未设置 → 行为逐字节不变，R6）；test_bdd_25 在 `tmp_path_factory.getbasetemp()` 位于仓库根下时注入排除（basetemp 相对根 rel 路径），否则不注入。
- **权衡（子决策）**：备选「先清后查」/「clean-copy」——copy 需含 .git 供 CHECK 7（badge vs tag），重量且慢，排除法更轻；备选「缩小 --root 到 agate/」——被 main() L1118（root 须为仓库根）与 CHANGELOG/badge 检查否决。**定案：opt-in 排除钩子（M15）+ 单测**。
- 平台无关：rel 路径经 `Path.relative_to` + 正斜杠归一（iter_md_files 既有 rel 处理），无 Unix 假设。

---

## 5. 批次设计（dispatch_plan）

> frontmatter：`{mode: static-batch, parallel_limit: 4, batches: [A-ruff(low), B-judge(medium), C-migration(high), D-env-tests(medium)]}`。

| 批 | 子项 | complexity | 文件集（本批独占，不跨批写入） | 执行时相依 |
|----|------|-----------|-------------------------------|-----------|
| A-ruff | RM-AG0037 | low | `.github/workflows/protocol-tests.yml` + `agate/UPGRADING.md` + `AGENTS.md` | 无（可并行） |
| C-migration | RM-AG0038 | **high** | `agate/scripts/check-gate.py`（解析层重构块）+ `agate/scripts/agate_common.py`（共享读取器）+ `agate/scripts/agate-md-field-get.py`（全部新 op，含 created）+ `agate/scripts/check-structure-consistency.py`（S-3 收紧）+ `agate/rules/phases.yaml`（gates 命令串）+ `agate/tests/unit/test_md_parse_scan.py`（新） | 无（可并行）；**先于 B-judge** |
| B-judge | RM-AG0039 | medium | `agate/scripts/check-gate.py`（gate_p1 新增 judge 块，**叠加于 C 重构后基础**）+ `agate/rules/dispatch.yaml`（judge_required_since）+ `agate/state-machine.md`（L442-443）+ `agate/phase-cards/P1-requirements.md`（产出规格）+ `agate/tests/unit/test_check_gate.py`（judge P1 用例） | **依赖 C**（created op + 重构后 gate_p1）；C 之后串行 |
| D-env-tests | RM-AG0041 | medium | `agate/tests/unit/test_check_routing.py`（test_bdd_7）+ `agate/tests/unit/test_env_adapt_docs.py`（test_bdd_25）+ `agate/scripts/check-protocol-consistency.py`（iter_md_files 排除钩子 [SCOPE+ M15]） | 无（可并行） |

- **D3 错开验证**：0039 与 0038 的 check-gate.py 改动分属 B/C 两批、不同 commit、非重叠改动块（C = 解析层重构；B = gate_p1 末尾纯叠加 judge 块），批文件集互不交叉；C 先行使 agate-md-field-get.py 单批独占（B 的 created 依赖由 C 提供，B 不再写该文件）。
- **共享件处理**：dispatch.yaml 仅 B 写（judge_required_since）；phases.yaml 仅 C 写（gates 命令串）；rules schema（dispatch.schema.json）随 B、phases.schema.json 随 C（同文件同批，不跨批）。
- **并行编排**：Wave1 = {A, C, D} 并行（文件完全不相交）；Wave2 = {B} 于 C 返回后派发（串行依赖）。parallel_limit 4（批数 4 ≤ 4）；实际并发 ≤3。
- **RM-AG0040**：无 P4 代码批（计划已落 §4.4 本文件）；P6 按 BDD-8 核对四要素 + 触发条件。
- **资源密集型批次判定**：各批独立验证以全量 pytest 收口（P5 gate 命令唯一，主 Agent 串行跑），批内无 xdist/E2E/构建——不触发「资源密集型默认串行」之外的额外串行要求；Wave1 并行期间各自只跑目标文件子集测试热身，全量验证留 P5。

---

## 6. gate_commands（P2 固化，后续不得修改）

> 各 key 独立声明，禁 `&&` 拼接（短路反模式）；/tmp 只读 → pytest 一律 `-p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（N2 实证可写）。

```yaml
gate_commands:
  P3: "python3 -m pytest -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp --tb=short"
  P5: "python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp"
  P5_timeout_seconds: 600
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_consistency_timeout_seconds: 120
  P5_structure: "python3 agate/scripts/check-structure-consistency.py"
  P5_structure_timeout_seconds: 120
  P5_ruff: "/home/kity/.venvs/agate-dev/bin/ruff check agate/"
  P5_ruff_timeout_seconds: 120
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_count_timeout_seconds: 120
```

说明：① P5 全量（1202+ 用例）设 600s 档（构建类 600 档下沿，防长跑误杀）；② P5_consistency/structure 120s 档（单元测试档）；③ ruff 用绝对路径（0.16.4 实证）；④ P3/P5 同一 basetemp，`AGATE_TDD_TIMEOUT` 机制照旧管 P3 超时（timeout_seconds 不覆盖 P3）；⑤ P3 formatter 不声明 → check-tdd-red 退化为 exit-code-only（本任务全为 pytest，A/B 类红灯区分不关键，P3 红→P4 绿路径简单）。

---

## 7. files_to_read（P4 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/check-gate.py
    why: 迁移主对象：gate_p1（judge 块注入口 + B 组标记逻辑）/gate_p2/gate_p6/gate_p7/gate_p65 的 A/C/D 组解析点改造；只改读取方式、不改判定口径
  - path: agate/scripts/agate_common.py
    why: 共享读取器落点：M2 共享解析节（L769-805）为样板；新增 B/C/D 组读取器与 parse_gate_commands_block 同款；run_git/read_rules_yaml/resolve_rules_root/reconcile_* 供判据用
  - path: agate/scripts/agate-md-field-get.py
    why: KNOWN_OPS 注册（status/agent/project_phase/code_map_new_files_count/code_map_reviewed_count/created）；双轨读取契约（frontmatter 优先 + 回退），新增 op 归类到 NO_FALLBACK_* 集合
  - path: agate/scripts/check-structure-consistency.py
    why: S-3 双向 gate 命令一致性收紧（S-3a/S-3b）+ S-4 已知字段表补新 op；S-0 编号空间约束（不新增 S-7）
  - path: agate/rules/phases.yaml + agate/rules/dispatch.yaml + agate/rules/schema/*.json
    why: gates 命令串数据增补（phases.yaml）+ judge_required_since（dispatch.yaml）+ schema 同步；S-5 schema 校验对象
  - path: agate/state-machine.md:440-448
    why: 0039 judge 模板语义更新（L442-443）；P6.5 硬边界/早退语义（L153/155）只读参考
  - path: agate/phase-cards/P1-requirements.md
    why: 产出规格 checklist 增补 judge 声明条 + frontmatter 样例注释（L49-97）；ceremony checklist（L111-120）为同型参照
  - path: agate/tests/unit/test_check_gate.py:2626-2689
    why: gate_p65 judge 三态用例（无/true/false）为 judge 语义参照；P1 分支用例（L40-134 区）为新增 judge P1 用例的 fixture 挂靠点
  - path: agate/tests/unit/test_check_routing.py:148-156
    why: test_bdd_7 改造对象（git_ok:false 语义 + _write_p1/run_cli fixture 用法）
  - path: agate/tests/unit/test_env_adapt_docs.py:47-60
    why: test_bdd_25 改造对象（run_cli --root 调用 + 一致性断言）
  - path: agate/tests/conftest.py
    why: create_task_dir/_run_cli_impl/task_dir/tmp_path fixture：确认 env 注入路径（test_bdd_7 用）与夹具兼容（H10 验证，预计零改动）
  - path: agate/scripts/check-protocol-consistency.py:119-138
    why: iter_md_files 排除钩子落点（[SCOPE+] M15）；main() L1104-1120（root 强制仓库根）为排除法依据
  - path: agate/scripts/agate-risk-score.py:202-270
    why: score_task 的 run_git(cwd=task_dir) 调用点——GIT_CEILING_DIRECTORIES 生效机理（git 向上发现仓库）
  - path: .github/workflows/protocol-tests.yml:106-116
    why: ruff job 稳定化（锁 ruff==0.16.4 + job name 固化）
  - path: agate/UPGRADING.md
    why: 新增 TAG0022 章节（required check 步骤 + 权威源切换破坏性变更 + judge 强制化）；沿用「按版本章节」格式
  - path: agate/tests/scripts/count-tests.sh
    why: N3 基线 1202 的验证脚本（P5_count gate）
```

---

## 8. env_constraints / minimal_validation

```yaml
env_constraints:
  debug_env: "Linux；/tmp 只读 → pytest 一律 --basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider（N2 实证可写）；ruff 用 /home/kity/.venvs/agate-dev/bin/ruff（0.16.4 实证，对齐 CI 锁版本）"
  dual_workspace: "改造对象 = worktree agate/（/home/kity/oclab/agate/.worktrees/agate-TAG0022/agate/）；~/.agate 稳定版只读；check-protocol-consistency.py 用 worktree 自己的；主 checkout /home/kity/oclab/agate 禁止改动"
  count_tests_baseline: "1202（N3 冻结，只增不减；P6 判据下界）"
  reconcile_layer: "AGATE_RECONCILE 缺省 on（M1 对账叠加层，不改变退出码语义）；CI/批处理可设 off 降噪"
```

```yaml
minimal_validation:
  - assumption: "dsh-workspace/ptmp 可作为仓库外 basetemp（N2）"
    method: "在 /home/kity/oclab/dsh-workspace/ptmp 实际创建+删除 probe 临时文件"
    result: "confirmed"
    note: "probe 文件创建/删除成功；ptmp 与 dsh-workspace 本身均可写——冻结为权威仓库外 basetemp（BDD-4/9 gate 命令即用此路径）"
  - assumption: "0038 结构化读取路径可打通（read_rules_yaml + agate-md-field-get 读 rules/*.yaml 与任务字段）"
    method: "最小脚本调 agate_common.resolve_rules_root + read_rules_yaml(phases) + known_phase_ids + is_legal_gate_key + agate-md-field-get domains（对 P1-requirements.md）"
    result: "confirmed"
    note: "phases.yaml 10 阶段解析 OK；known_phase_ids 返回 P0-P8+P6.5；is_legal_gate_key('P5_e2e_timeout_seconds')=True；domains op 对 P1 文件返回 backend——共享读取器模式可行，迁移无外部系统依赖"
  - assumption: "GIT_CEILING_DIRECTORIES 能确定性制造非 git 上下文（test_bdd_7 修复依赖 git 核心行为）"
    method: "临时 git 仓库 + 子目录探针：无 ceiling 时 rev-parse 找到仓库，设 ceiling 后 rc=128（not a git repository）"
    result: "confirmed"
    note: "git 核心机制，跨平台支持；test 经 run_cli env 注入，无 Unix 假设"
  - assumption: "test_bdd_25 排除钩子（[SCOPE+] M15）为纯代码逻辑"
    method: "声明纯代码逻辑，无外部系统依赖——依赖内部函数 iter_md_files（check-protocol-consistency.py L119-138）的 rel_parts 排除链 + main() L1117 root 解析；新增 env 读取与排除分支走同一排除链"
    result: "not_needed（纯代码逻辑）"
    note: "依赖的数据转换 = Path.relative_to + os.sep 正斜杠归一（既有 rel() 处理）；默认行为（env 未设置）与改动前逐字节一致"
  - assumption: "0039 judge 校验为纯代码逻辑"
    method: "声明纯代码逻辑，无外部系统依赖——依赖内部函数 _load_state_yaml（check-gate L230-244）+ _md_field_get（created op，agate-md-field-get 双轨）+ read_rules_yaml（judge_required_since，dispatch.yaml）"
    result: "not_needed（纯代码逻辑）"
    note: "数据转换 = .state.yaml yaml.safe_load → judge dict 取值 → ISO 日期字符串比较（created >= judge_required_since 字典序）"
```

---

## 9. self-gate 处理纪律（约束 6，隐含节）

- **触发面**：本任务全部产出 commit 均含触发文件（CI/check-gate.py/state-machine/P1 卡/测试）→ 每个含触发文件的 commit message 必须含 `self-gate-review: <路径>` 或 `self-gate-skip: <理由>`（HANDOFF §5；为后续 commit 批次统一纪律）。
- **一次 protocol-alignment-review 安排**：RM-AG0038 的「协议-脚本对齐」面最大（check-gate.py 判定口径 ↔ rules YAML ↔ state-machine/P1 卡条文），在 **C-migration 批完成后、B-judge 批开始前**（或受托主 Agent 决定）派发一次 protocol-alignment-review（独立 subagent，评审协议条文与脚本行为一致性）——拟安排于 P4 的 C 批产出 commit 后；B 批与 A/D 批如评审结论涉及则顺带核对。主 Agent 落实（P1 §3 H1）。
- **commit 纪律**：批次各自 commit，phase 与产出阶段一致（P3 产出的测试红 commit → phase=P3；P4 实现绿 commit → phase=P4）；count-tests 每 commit 前不漂移（只增不减）。

---

## 10. 门槛自检（对照 dispatch-context）

- candidate_count=2 ✓（附权衡与选择理由）；四字段齐全（packages/domains/ui_affected/gate_commands）✓
- 影响面梳理三部分齐全（§1.1 改什么 / §1.2 不改什么 / §1.3 风险）且写在候选方案（§2）之前 ✓
- dispatch_plan：D3 错开（0038=C 批 / 0039=B 批，check-gate.py 非重叠改动块）+ high（C-migration）已拆批 + 每批 id+complexity ✓
- gate_commands 各 key 独立声明（P3/P5/consistency/structure/ruff/count + 各自 timeout_seconds）✓
- N1（fail-closed exit 1 + 理由 §4.3.1）/ N2（ptmp 写可实证 §8）/ N3（1202 冻结 §0）闭环落盘 ✓
- RM-AG0038 逐点映射清单（§4.2.1 A-D 组 → YAML 字段/读取器）+ RM-AG0040 四要素 + 触发条件（§4.4）落盘 ✓

---

## 11. 下游影响

- **P3**：按 §3 完成标准写失败测试——0038 静态扫描测试（test_md_parse_scan.py）、0039 judge P1 用例（test_check_gate.py）、0041 test_bdd_7/25 改造 + M15 排除钩子用例；TDD 先红后绿，批内自验。
- **P4**：按 §5 批次执行（Wave1 A/C/D 并行 → Wave2 B），C 批实现共享读取器 + op 注册 + S-3 收紧，B 批叠加 judge 块；各批 commit 遵守 §9 self-gate 纪律。
- **P5**：按 §6 gate_commands 验证（全量 pytest 外部 basetemp / consistency / structure / ruff / count）；BDD-2/4/9 双位置验证。
- **P6**：逐条 BDD-1..10；无 UI 证据需求（domains=[backend]）；**P6.5 judge 复核强制**（.state.yaml 已写 judge.enabled: true）。
- **P7**：跨文件交叉核对（CI/check-gate/state-machine/P1 卡/测试五面）；0039/0038 批界一致性（judge 块叠加于重构后基础）。
- **P8**：版本 bump + UPGRADING 章节（required check 步骤 / 权威源切换破坏性变更 / judge 强制化）+ SELF-GATE review；README badge/CHANGELOG 清单。