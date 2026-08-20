---
phase: P2
task_id: TAG0017-toolchain-fixes
type: design
parent: P1-requirements.md
trace_id: TAG0017-P2-20260820
status: draft
created: 2026-08-20
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 8
packages: [gate-scripts, hooks-shell, phase-cards, self-gate-template, platform-notes, agent-roles]
domains: [protocol-docs, gate-scripts]
ui_affected: false
# ── v2.0 派发编排字段 ──
dispatch_plan: {mode: static-batch, parallel_limit: 5, batches: [{id: fg1-parser-scripts, complexity: medium}, {id: fg1-doc-boundary, complexity: low}, {id: fg2-self-gate-naming, complexity: low}, {id: fg3-strict-mode-code, complexity: medium}, {id: fg4-windows-python-probe, complexity: medium}]}
---

## 0. 总览

本方案覆盖 P1-requirements.md 的 12 条 BDD、4 个功能分组（DEBT0010+RM-AG0028/DEBT0015 整合、DEBT0011、DEBT0012、DEBT0014）。P1 已判定 4 组"无域重叠"，但 P2 设计阶段发现一处例外（见 §2 风险 R1）：DEBT0010 的 `env_constraints` 边界说明（BDD-5）与 DEBT0012 的 `--strict` 反模式指引（BDD-9）都要写进 `phase-cards/P2-design.md`「gate_commands 声明」同一节——为避免同一文件被两个批次各改一次，`dispatch_plan` 把这两处文档增补合并进同一批 `fg1-doc-boundary`，不严格 1:1 对齐 4 个功能分组（详见 §2 与 §6）。

## 1. 影响面梳理（强制节，写在候选方案之前）

### 1.1 改什么（Modify）

| 文件 | 改动点 | 关联 BDD |
|------|--------|----------|
| `agate/scripts/agate_common.py` | 新增共享判据函数 `is_gate_meta_key(key)`（`key.endswith(("_formatter","_timeout_seconds"))`），供 4 个解析脚本复用 | BDD-1/2/3/4 |
| `agate/scripts/agate-read-gate-commands.py`（L31 附近） | `elif key.startswith("P3") and not key.endswith("_formatter"):` 改为 `elif key.startswith("P3") and not is_gate_meta_key(key):` | BDD-2/4 |
| `agate/scripts/agate-gate-missing-cmds.py`（L20 附近） | `if k.endswith("_formatter") or k == "project_module": continue` 改为 `if is_gate_meta_key(k) or k == "project_module": continue` | BDD-1/4 |
| `agate/scripts/agate-gate-p5-count.py`（L23 附近） | `aux = [k for k in ... if not k.endswith("_formatter")]` 改为 `if not is_gate_meta_key(k)` | BDD-3/4 |
| `agate/scripts/agate-read-p5-commands.py`（L29 附近） | `if key.endswith("_formatter"): continue` 改为 `if is_gate_meta_key(key): continue` | BDD-1/3/4 |
| 新增审计测试（如 `agate/tests/unit/test_gate_key_suffix_audit.py`） | 结构性 grep 断言：`agate/scripts/agate-*.py` 中含 `"_formatter"` 排除逻辑的文件必须同时含 `"_timeout_seconds"` 或引用 `is_gate_meta_key` | BDD-4 |
| `agate/tests/unit/test_check_tdd_red.py`（`test_pyx_*` 系列附近，约 L588 起） | 新增 `P3_timeout_seconds` 声明场景用例（BDD-1/2） | BDD-1/2 |
| `agate/tests/unit/test_agate_gate_missing_cmds.py` / `test_agate_gate_p5_count.py` / `test_agate_read_p5_commands.py` | 各自新增 `_timeout_seconds` 排除场景用例 | BDD-1/3 |
| `agate/phase-cards/P2-design.md`「gate_commands 声明」节（L117-146） | 新增两段：① `env_constraints` 声明性 vs `gate_commands` 执行性边界说明（BDD-5）② `--strict` 不放 `&&` 链路中间的指引 + 反例（BDD-9） | BDD-5/9 |
| `agate/assets/execution-roles/architect.md`「输出」节 `gate_commands:` 相关段落 | 同步 BDD-5 边界说明 | BDD-5 |
| `agate/phase-cards/P4-implementation.md`「自查≠gate」节（L50-54） | 新增"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"提醒条目 | BDD-6 |
| `SELF-GATE.md` L53/54（文件类型表）、L133/143、L183/193（两处派发模板） | 命名模板补任务标识：留痕 `docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md`；成果 `docs/reviews/agate-alignment-review-{date}-{task_id}.md` | BDD-7 |
| `agate/assets/review-roles/protocol-alignment-review.md` L118（验收清单项）+ 新增"写入前检查目标路径"段落 | 同步新命名 + Write 前先 `test -f` 判断同任务复核轮（可覆盖）还是他任务遗留（不可覆盖） | BDD-7/8 |
| `agate/scripts/check-protocol-consistency.py`（main() 尾部，约 L1076-1134） | 新增 `--strict-errors-only` 互斥模式：仅 ERROR 非零（exit 1），WARNING-only 打印提示 exit 0；`--strict` 现有语义不变 | BDD-9 |
| `agate/tests/unit/test_check_protocol_consistency.py` | 新增 `--strict-errors-only` 场景用例（0E0W→0 / 0E+NW→0+提示 / NE→1，与既有 `--strict` 矩阵并列不冲突） | BDD-9 |
| `agate/scripts/pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`（探测循环，约 L15-16，3 文件结构完全一致） | ① `AGATE_PYTHON` 环境变量显式指定时直接使用，跳过探测循环 ② 探测循环内候选加可执行性小测试（`"$CAND" -c "" >/dev/null 2>&1`，非零则跳过继续下一候选） | BDD-10/11 |
| `agate/tests/integration/test_pre_commit_hook.py`（及 pre-push/commit-msg 对应集成测试，参照同结构） | 新增：PATH 中放置"不可执行 python3 stub + 可用 python stub"验证探测继续（BDD-10）；新增 `AGATE_PYTHON` 显式指定跳过探测循环用例（BDD-11） | BDD-10/11 |
| `agate/platform-notes.md`「已知限制（Windows 原生）」表（L152 附近）+「Windows 原生」章节 | 新增一行限制条目 + 一段 Store 占位符现象 + `AGATE_PYTHON` 机制说明（不含"已实测通过"断言） | BDD-12 |
| `AGENTS.md`「Gate 脚本分层」节（L42） | 追加一句：探测循环支持 `AGATE_PYTHON` 显式覆盖 + 候选可执行性小测试 | BDD-12 |

### 1.2 不改什么（Not Modify）

| 范围 | 理由 |
|------|------|
| `agate-capture-env-baseline.py` / `check-tdd-red.py` 里对 `agate-read-gate-commands.py` 的 subprocess 调用方式 | P1 同类扫描 3.1 已确认二者不做独立 key 后缀解析，只消费其 JSON 输出，本次修复在被调用方生效即可传导，不需要改调用方代码 |
| 历史 8 个任务（TAG0004/9/12/14/15/16 的 `&&` 链路 + TAG0005/10/11 的独立 key 声明）已产出的 `P2-design.md` | 已完成任务的既定产出不可回改；风险已转化为协议文档层新增指引（BDD-9），不追溯改历史文件 |
| `docs/reviews/` 目录下 TAG0015/TAG0016 已生成的历史审查文件 | P1 已核对当前无遗留冲突（TAG0016 已手工加后缀规避过一次），命名规则变化只影响未来新生成文件，不回改历史文件名 |
| `check-tdd-red.py` docstring 提及的 `pytest` 探测（`shutil.which`） | P1 同类扫描 3.5 已确认其探测目标是 `pytest` 而非 python 解释器本身，且走 Python 标准库而非 shell `command -v`，不构成 DEBT0014 同一风险路径 |
| `check-protocol-consistency.py` 现有 `--strict` 语义（WARNING-only 也 exit 2） | 新增 `--strict-errors-only` 是并列新模式，不修改 `--strict` 现有行为——用户仍可主动选用 `--strict` 做"WARNING 也要清零"的严格检查，只是不推荐把它放进 `&&` 链路默认组成 |
| `env_constraints` 字段本身的语法/位置（P0-brief.md / P2-design.md frontmatter 声明方式不变） | DEBT0015 修复的是"边界认知文档化"，不是给 `env_constraints` 新增执行机制——若真的新增了自动执行绑定，反而混淆了"声明性 vs 执行性"这条本次要澄清的边界，属于 P1 已明确排除的方案（见 §3.1 候选 B 讨论） |
| `agate/scripts/ci-gate-backstop.py` / `protocol-tests.yml` | DEBT0012 修复对象是任务级 `gate_commands.P5` 声明；CI workflow 自己的 pytest/consistency/shellcheck 是三个独立 job 步骤，本来就不是 `&&` 链路，不受影响，无需改动 |
| `CHANGELOG.md` / `README.md` version badge / `UPGRADING.md` | 版本发布是 P8 阶段既有流程（AGENTS.md「版本发布」节），P2/P4 不预先处理，避免与 P8 实际发布时的版本号/条目重复或冲突 |

### 1.3 风险在哪（Risk）

| 风险 | 缓解措施 |
|------|----------|
| **R1（协议文档层跨批共享文件冲突）**：`phase-cards/P2-design.md`「gate_commands 声明」节被 DEBT0010/DEBT0015（BDD-5）与 DEBT0012（BDD-9）两个"P1 判定无域重叠"的功能分组同时需要增补 | `dispatch_plan` 把这两处文档增补合并进同一批 `fg1-doc-boundary`（见 §6），由一个 P4 批次一次性完成两段增补，避免两个并行批次各自 Write 同一文件互相覆盖 |
| R2（共享判据函数误伤）：`is_gate_meta_key` 若判据写错（如漏了某后缀），4 处调用方会同时受影响，波及面比各自独立内联判据更大 | 先写 `is_gate_meta_key` 单测（覆盖 `_formatter`/`_timeout_seconds`/普通 key 三态）再改 4 处调用方（TDD 红→绿），4 处调用方修改后各自的既有测试 + 新增测试须全绿才算完成 |
| R3（BDD-2 回归判定被放宽）：DEBT0010 修复容易做成"P3 阶段所有非常规 key 都忽略"，从而连真正的红灯误判也一并放宽 | `is_gate_meta_key` 只排除两个**已知固定后缀**（`_formatter`/`_timeout_seconds`），不做通配/正则宽松匹配；BDD-2 用例显式验证"真实失败（非超时）测试命令仍被判 A 类"，防止修复本身引入更危险的回归（P1 隐含需求已点名） |
| R4（`--strict-errors-only` 新增模式误用）：主 Agent/未来任务可能混淆 `--strict` 与 `--strict-errors-only`，把后者当成"更严格"而非"更宽松" | argparse 用互斥组（`add_mutually_exclusive_group`），`--help` 文案明确写清两者语义差异；本任务自己的 `gate_commands` 声明以身作则用独立 key + `--strict`（不用新 flag，见 §5），新 flag 是给**未来选择继续用 `&&` 链路**的任务的兜底，不是本任务默认用法 |
| R5（3 个 hook 薄壳改动一致性）：3 处探测循环结构完全一致，改动必须逐字同步，漏改一处会导致行为分叉 | 3 文件改动内容逐字相同（同一段代码片段），P4 实现后跑 `diff` 三份探测循环片段确认一致；集成测试对 3 个 hook 各跑一遍探测跳过 + `AGATE_PYTHON` 用例（不只测 pre-commit 一个代表） |
| R6（Windows 行为验证过度声称）：本环境 Linux，无法真实复现 Store 占位符 exit 49 | 严格执行 P1 verification_env 声明：验收证据只能是"静态修复 + 模拟 stub 回归 + CI matrix 冒烟"，不写"已在 Windows 实测通过"；P6 acceptance 措辞需同样受此约束（P7 一致性检查时核对） |
| R7（`is_gate_meta_key` 与 `project_module` 精确匹配语义混淆）：`agate-gate-missing-cmds.py` 现有判据是 `k.endswith("_formatter") or k == "project_module"`（两种不同性质的排除条件） | `is_gate_meta_key` 只处理后缀类判据，不吞并 `project_module` 精确匹配——调用方保留 `is_gate_meta_key(k) or k == "project_module"` 的组合写法，不把语义不同的两个判据强行合并成一个函数（避免过度抽象） |

## 2. 候选方案

> 本任务涉及 4 个功能分组、5 处系统缺陷，每组按方案空间独立探索 ≥2 候选（design_trivial 不适用）。§1 影响面梳理已完成，以下候选方案的取舍均建立在该梳理之上。

### 2.1 功能分组 1（DEBT0010 + RM-AG0028/DEBT0015）候选方案

**候选 A（推荐）：共享判据函数 + 文档边界说明（纯声明，不新增执行绑定）**
- DEBT0010：`agate_common.py` 新增 `is_gate_meta_key(key)`，4 处解析脚本改为调用它，替换各自的内联 `.endswith("_formatter")` 判据。
- DEBT0015：仅在 `phase-cards/P2-design.md`「gate_commands 声明」节 + `architect.md` + `P4-implementation.md`「自查≠gate」节新增文字说明"`env_constraints` 是声明性字段，执行性约束须落 `gate_commands` 或 P4/P8 checklist"，不新增任何 gate 脚本对 `env_constraints` 做校验。
- 优点：单点判据消除未来"改一处忘改一处"的重复失误来源；DEBT0015 修复保持声明性字段的语义纯粹（不制造"部分执行、部分不执行"的更混乱状态）；改动面小，回归风险低。
- 风险：共享函数一旦判据本身写错会同时影响 4 处（已在 §1.3 R2 给缓解措施）。
- 工作量：中（5 个代码文件 + 3 个文档文件 + 若干测试）。

**候选 B（不采纳）：4 处各自内联修复 + 新增 `env_constraints.deploy` 专用 gate 脚本**
- DEBT0010：4 个脚本各自独立加 `and not key.endswith("_timeout_seconds")`，不抽共享函数（P1 known_risks 已允许此路径）。
- DEBT0015：新增一个 `check-env-constraints-deploy.py`，在声明了 `env_constraints.deploy` 时校验 P4/P8 产出目录下存在对应 dist 产物，接入 gate。
- 优点：DEBT0010 部分改动面更小（不引入新的跨文件依赖）；DEBT0015 部分能自动兜底，不依赖人工遵循 checklist。
- 缺点（判定不采纳的理由）：① DEBT0010 部分虽然改动面小，但不解决"未来第 5 处遗漏"的根本问题——没有共享判据函数，BDD-4 要求的"审计断言或共享判据函数"里能兜底的只剩纯审计测试一条腿，防线更薄；② DEBT0015 部分**恰恰是本次要澄清的反面**：新增一个自动校验 `env_constraints.deploy` 的 gate 脚本，实质上是把声明性字段变成了半执行性字段，混淆了"`gate_commands` 是执行机制、`env_constraints` 是声明性字段"这条 P1 已明确要求整体表述的边界（dispatch-context 约束 3），且 P1 BDD-5/6 只要求"文档化边界 + P4 checklist 提醒"，未要求新增自动化校验（该子选项在 P0-brief 原文本就标"可选"）——做了反而超出 P1 范围，属于不必要的 scope 扩张。
- 工作量：中高。

**选择理由**：候选 A。DEBT0010 用共享函数既满足 BDD-4 又与候选 B 打平（工作量相近，但防线更强）；DEBT0015 部分候选 A 严格遵守 P1 BDD-5/6 的字面要求（文档边界 + checklist 提醒），候选 B 的自动校验方案实质上违反了本次修复要澄清的核心边界，风险和收益不成比例，故排除。

### 2.2 功能分组 2（DEBT0011）候选方案

**候选 A（推荐）：命名模板补 `{task_id}` + Write 前存在性检查**
- 留痕文件：`docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md`；成果文件：`docs/reviews/agate-alignment-review-{date}-{task_id}.md`。
- `protocol-alignment-review.md` 新增段落：Write 前先 `test -f` 判断目标路径是否已存在；已存在时读取该文件内容判断是否为同一任务同日复核轮（文件名里的 `{task_id}` 与当前任务一致 → 可覆盖）还是别的任务遗留（`{task_id}` 不同或无法确认 → 不可覆盖，改用新文件名或人工确认）。
- 优点：`task_id` 是每次派发时已知的上下文（dispatch-context 本身就含 task_id），零新增状态；文件名自解释，读者一眼看出归属任务；与现有"留痕文件 vs 成果文件"两类命名模式统一处理，改动一致。
- 工作量：低（2 个文件，纯文本模板替换 + 一段新逻辑说明）。

**候选 B（不采纳）：全局递增序号替代日期命名**
- 改用 `docs/reviews/agate-alignment-review-{seq}.md`（`{seq}` 从一个共享计数器文件读取递增），不依赖日期或 task_id。
- 优点：文件名更短。
- 缺点（判定不采纳的理由）：① 需要新增一个跨任务共享的可变计数器文件，而"跨任务共享可变状态"正是本次要解决的"同日多任务互相覆盖"问题的同类风险（计数器文件本身在并发场景下也可能被两个任务同时读到旧值、写出同一个 `{seq}`，重蹈覆辙）；② 文件名脱离日期和任务语义，不看内容无法判断归属，可读性劣于候选 A；③ 引入新状态文件意味着新的生命周期管理问题（计数器何时重置、如何回收），维护成本高于纯字符串模板替换。
- 工作量：中（需要新增并维护计数器文件及其读写逻辑）。

**选择理由**：候选 A。`task_id` 是零成本的既有上下文，直接嵌入命名即解决碰撞问题，不引入新状态；候选 B 用新状态解决旧状态问题，属于反模式。

### 2.3 功能分组 3（DEBT0012）候选方案

**候选 A（推荐，P0-brief"两者都做"）：协议文档指引 + 新增 `--strict-errors-only` 模式**
- (a) `phase-cards/P2-design.md`「gate_commands 声明」节新增指引："不要把 `--strict` 放进 `&&` 链路中间；`gate_commands.P5` 的多个校验步骤各自声明独立 key（如 `P5`/`P5_consistency`/`P5_count_tests`），由执行方分别跑分别判断" + 一个反例（引用 TAG0004/TAG0016 式 `&&` 链路作为反面示例，不点名批评已完成任务，只展示模式）。
- (b) `check-protocol-consistency.py` 新增 `--strict-errors-only` 互斥模式：仅 ERROR 非零（exit 1），WARNING-only 打印提示信息但 exit 0；保留现有 `--strict`（WARNING-only 也非零）供人工主动选用。
- 优点：(a) 从源头阻止未来任务把 `--strict` 写进链路中间；(b) 给仍然想用单条链式命令的场景提供一个不会被 WARNING 卡住的选项，双重防线。P1 同类扫描 3.3 已确认"独立 key 声明"（TAG0005/10/11 模式）也可能被下游二次拼接成 `&&` 链路（结论"无法排除等价短路风险"），只做纯文档指引（不改代码）覆盖不了这条残余风险，(b) 补上代码层防线。
- 工作量：中（1 个脚本改动 + 多个协议文档段落 + 测试矩阵扩展）。

**候选 B（不采纳）：仅做协议文档指引，不改脚本**
- 只做候选 A 的 (a) 部分，不新增 `--strict-errors-only`。
- 优点：零代码改动风险，diff 最小。
- 缺点（判定不采纳的理由）：无法覆盖 P1 同类扫描 3.3 明确指出的"独立 key 被下游重新拼接成 `&&` 链路"残余风险——文档指引只能约束"P2 阶段怎么声明"，管不到"P5 阶段主 Agent/subagent 实际怎么执行多个 `P5_*` key"；BDD-9 要求的是"链路后续步骤确实被执行到"这一行为结果，纯文档方案在"声明层已合规但执行层仍拼接"的场景下无法保证结果达标，风险敞口未闭合。
- 工作量：低。

**选择理由**：候选 A。BDD-9 关心的是行为结果不被短路，候选 B 只管住了声明层，管不住执行层的残余风险；(b) 的新增模式改动成本可控（互斥 flag + 尾部分支），选 A。**以身作则**：本 P2-design.md 自己的 `gate_commands` 声明（见 §5）严格使用独立 key，`--strict` 不放入 `&&` 链路。

### 2.4 功能分组 4（DEBT0014）候选方案

**候选 A（推荐）：`AGATE_PYTHON` 显式覆盖 + 探测循环候选可执行性小测试（通用 exit code 判据）**
- 3 个 hook 薄壳探测逻辑改为：`AGATE_PYTHON` 环境变量非空时直接使用（跳过探测循环，BDD-11）；否则遍历 `python3 python` 候选，每个候选先做 `"$CAND" -c "" >/dev/null 2>&1` 可执行性小测试，非零结果跳过继续下一候选（BDD-10）。
- 判据选型：用**通用 exit code 判据**（候选执行任意最小命令失败即跳过），不用"exit code 精确等于 49"或 stderr 字符串特征匹配。理由：exit 49 是当前已知的 Store 占位符行为，但通用判据同时覆盖"候选返回其他非 49 错误码"或"未来 Windows 版本 Store 占位符改变错误码"等场景，且不依赖 locale 相关的 stderr 文案（stderr 字符串匹配在非英文 Windows 环境可能失效）。已用模拟 stub 验证该判据逻辑正确（见 minimal_validation）。
- 优点：默认路径（不设置 `AGATE_PYTHON`）即可自动跳过不可用候选，不要求 Windows 用户先知道有这个环境变量才能绕过问题；判据通用、鲁棒性强。
- 工作量：中（3 个几乎逐字相同的文件改动 + 集成测试）。

**候选 B（不采纳）：仅新增 `AGATE_PYTHON`，不改探测循环本身**
- 只加显式覆盖变量，`command -v` 探测循环维持原样不做可执行性校验。
- 优点：探测循环零行为变更，回归风险最低。
- 缺点（判定不采纳的理由）：BDD-10 要求"探测循环命中不可执行的候选时能继续探测下一候选"——这是默认路径（无需用户配置）必须具备的行为；候选 B 把问题完全转嫁给用户手动设置 `AGATE_PYTHON`，不知道这个变量存在的 Windows 用户仍然会在默认路径下被 Store 占位符阻断，只满足 BDD-11 不满足 BDD-10，是本次要修的核心症状未修。
- 工作量：低。

**选择理由**：候选 A。BDD-10 明确要求默认探测路径本身具备跳过能力，候选 B 不满足；候选 A 的判据选型已用最小验证确认可行（见 minimal_validation）。

## 3. 实现完成的标志

- 4 个 DEBT0010 解析脚本统一调用 `agate_common.is_gate_meta_key`，`_timeout_seconds` 声明不再被误判为待核实命令/误算入 P5 计数/误当 P3 命令执行；`is_gate_meta_key` 单测 + 4 处调用方回归测试 + 1 个结构性审计测试全绿。
- `phase-cards/P2-design.md`「gate_commands 声明」节可查到"`env_constraints` 声明性 vs `gate_commands` 执行性"边界说明与"`--strict` 不放 `&&` 链路中间"指引；`architect.md`/`P4-implementation.md` 同步内容存在。
- `check-protocol-consistency.py --strict-errors-only` 在 0 ERROR+N WARNING 场景 exit 0（打印提示），在 N ERROR 场景 exit 1；既有 `--strict` 行为不变；测试矩阵覆盖三种模式 × 两种 WARNING 状态。
- `SELF-GATE.md`/`protocol-alignment-review.md` 命名模板含 `{task_id}`；同日两个不同任务各自触发审查生成的文件名不同；`protocol-alignment-review` 角色文件含"Write 前检查目标路径存在性"逻辑说明。
- 3 个 hook 薄壳探测循环支持 `AGATE_PYTHON` 显式覆盖 + 候选可执行性小测试；集成测试用模拟 stub（exit 非零候选 + 正常候选）验证跳过与显式覆盖两条路径；`platform-notes.md`/`AGENTS.md` 含对应文档条目且不含"已在 Windows 实测通过"断言。
- `python3 -m pytest agate/tests/` 全绿（含新增用例）；`python3 agate/scripts/check-protocol-consistency.py --strict` 0 ERROR；`bash agate/tests/scripts/count-tests.sh` 计数 ≥ 现有基线且口径一致；`shellcheck -S warning agate/scripts/*.sh` 0 error。

## 4. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本地 Linux（继承 P0-brief）：python3 -m pytest agate/tests/ + python3 agate/scripts/check-protocol-consistency.py --strict + bash agate/tests/scripts/count-tests.sh + shellcheck -S warning agate/scripts/*.sh，均在 worktree 自己的脚本上跑（dogfooding 纪律：check-protocol-consistency.py 必须用 worktree 自己的，不能用 ~/.agate 稳定版）"
  isolation_check: "本任务不涉及生产环境/生产数据库/生产 API；改动对象是 agate 协议脚本与文档本体，验证环境即开发环境（worktree），无需额外隔离检查。改动仅涉及协议脚本/文档：[PROD_NOT_TOUCHED]（预期，P6 acceptance 复核实际执行情况）"
  windows_note: "DEBT0014 相关行为（Store 占位符 exit 49）本地 Linux 无法真实复现，验证方式见下方 minimal_validation 与 §1.3 R6；Windows 侧最终由 GitHub Actions Windows CI matrix（pytest -m windows_smoke，protocol-tests.yml 已有）冒烟兜底"
```

## 5. gate_commands（P2 固化，P3/P5/P6 按此执行，不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  # P4 review 修正：原 --strict 在当前 WARNING 基线下阻塞本任务自身 P5，改用 --strict-errors-only
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
```

说明：
- `P3`/`P5` 命令固定为 `python3 -m pytest agate/tests/`（dispatch-context 约束 9 指定），`P5` 额外加 `-q --tb=no` 走 architect.md 要求的紧凑输出模式；`P3` 保留详细输出供 `check-tdd-red.py` 自动读取，不加 `-q`。
- `P5_consistency`/`P5_count_tests`/`P5_shellcheck` 均为**独立 key**，不与 `P5` 用 `&&` 拼接——这正是本任务 DEBT0012 要修复的反模式，本设计文档以身作则不复现（见 §2.3 选择理由）。
- 不声明 `P3_timeout_seconds`/`P5_timeout_seconds`：本任务验证命令均为常规单元测试规模（950+ 用例，历史实测数分钟量级），走既有 `AGATE_TDD_TIMEOUT` 默认机制即可，dispatch-context 约束 9 已明确不声明。
- `project_module` 未声明：本任务改动对象是 agate 自身（dogfooding），非典型"项目代码 + import 错误检测"场景；参照 TAG0013/TAG0016 同类 dogfooding 任务的 P2-design.md 先例，均未声明该字段。

## 6. dispatch_plan 说明（批次设计，TAG0014 强制节）

工作量五维评估：改动跨越 4 个 Python 解析脚本 + 1 个新增共享函数 + 1 个 check-protocol-consistency.py 代码改动 + 3 个 shell 薄壳 + 至少 6 处协议 Markdown 文档 + 约 10 个测试文件的新增/修改，产出文件数远超「派发编排机制」单批基准（≤3），判定 **high 复杂度**，按硬规则必须拆批。

批次边界设计（对齐 §1 影响面梳理的文件分组，5 批）：

| 批次 id | 覆盖范围 | 涉及文件 | complexity |
|---------|---------|---------|------------|
| `fg1-parser-scripts` | DEBT0010 核心：共享判据函数 + 4 处解析脚本 + 对应回归测试 + 审计测试 | `agate_common.py`、4 个 `agate-*.py` 解析脚本、`test_check_tdd_red.py`（新增用例）、`test_agate_gate_missing_cmds.py`、`test_agate_gate_p5_count.py`、`test_agate_read_p5_commands.py`、新增 `test_gate_key_suffix_audit.py` | medium |
| `fg1-doc-boundary` | DEBT0015 边界文档化（BDD-5/6）+ DEBT0012 的 `&&` 反模式协议指引（BDD-9 文档半）—— **两个功能分组共享同一落点文件，合并为一批**（§1.3 R1） | `phase-cards/P2-design.md`（gate_commands 声明节）、`assets/execution-roles/architect.md`、`phase-cards/P4-implementation.md` | low |
| `fg2-self-gate-naming` | DEBT0011：命名模板 + 写入前检查 | `SELF-GATE.md`、`assets/review-roles/protocol-alignment-review.md` | low |
| `fg3-strict-mode-code` | DEBT0012 代码半：`--strict-errors-only` 新增模式 + 测试矩阵 | `check-protocol-consistency.py`、`test_check_protocol_consistency.py` | medium |
| `fg4-windows-python-probe` | DEBT0014：3 个 hook 薄壳探测循环改动 + 文档 + 集成测试 | `pre-commit-gate.sh`、`commit-msg-self-gate.sh`、`pre-push-gate.sh`、`platform-notes.md`、`AGENTS.md`、`test_pre_commit_hook.py`（及 pre-push/commit-msg 对应集成测试） | medium |

- `mode: static-batch`，`parallel_limit: 5`（5 批全部文件互不重叠，可一轮全部并行；无资源密集型全量测试/E2E/构建类批次，不强制串行——各批 P4 自查跑各自相关的目标测试子集，全量 `python3 -m pytest agate/tests/` 作为 P5 gate 在所有批次合并后统一跑一次）。
- 跨批共享文件核查：5 批覆盖的文件集合两两不相交（`fg1-doc-boundary` 已吸收原本会与 `fg1-parser-scripts`/`fg3-strict-mode-code` 重叠的文档改动，见 §1.3 R1），满足"同一文件不跨批次被改两轮"。
- 批次间无顺序依赖（各批改动的代码/文档相互独立，不存在"批 B 依赖批 A 先落地的接口"关系），可全部并行派发；仅需在所有批次返回后，主 Agent 统一跑一次全量 `python3 -m pytest agate/tests/` 确认无跨批次意外交互（如共享测试 fixture 冲突）。

## 7. files_to_read（P4 implementer 上下文导航）

按批次归类，P4 implementer 按所属批次读取对应子集，不必全读：

**fg1-parser-scripts**：
- `agate/scripts/agate-read-gate-commands.py`（全文，约 44 行）— DEBT0010 修复点 1，L28-33 排除逻辑
- `agate/scripts/agate-gate-missing-cmds.py`（全文）— 修复点 2
- `agate/scripts/agate-gate-p5-count.py`（全文）— 修复点 3
- `agate/scripts/agate-read-p5-commands.py`（全文）— 修复点 4
- `agate/scripts/agate_common.py:60-76`（`probe_python()` 附近）— 参照现有函数注释风格，`is_gate_meta_key` 插入点
- `agate/tests/unit/test_check_tdd_red.py:588-660`（`test_pyx_*` 系列）— BDD-1/2 回归测试参照与新增落点
- `agate/tests/unit/test_agate_gate_missing_cmds.py`、`agate/tests/unit/test_agate_gate_p5_count.py`、`agate/tests/unit/test_agate_read_p5_commands.py` — 各自新增 `_timeout_seconds` 用例的参照结构

**fg1-doc-boundary**：
- `agate/phase-cards/P2-design.md:110-146`（影响面梳理节尾 + gate_commands 声明节）— BDD-5/9 两段增补落点
- `agate/assets/execution-roles/architect.md`（`env_constraints:` 相关段落，grep `env_constraints` 定位）— BDD-5 同步
- `agate/phase-cards/P4-implementation.md:46-54`（「自查≠gate」节）— BDD-6 增补落点

**fg2-self-gate-naming**：
- `SELF-GATE.md:48-60,125-145,175-195`（文件类型表 + 两处派发模板）— BDD-7 命名模板改动落点
- `agate/assets/review-roles/protocol-alignment-review.md:100-119`（闭环规则 + 人工验收清单）— BDD-7/8 消费引导 + 写入前检查落点

**fg3-strict-mode-code**：
- `agate/scripts/check-protocol-consistency.py:1076-1134`（`main()` 全部）— BDD-9 `--strict-errors-only` 实现落点
- `agate/tests/unit/test_check_protocol_consistency.py:1-50`（现有用例结构风格，`test_bdd_N_*` 命名惯例）— BDD-9 新增测试参照（新用例避免与文件内已有 `test_bdd_9_*` 撞名，改用如 `test_strict_errors_only_*` 前缀）

**fg4-windows-python-probe**：
- `agate/scripts/pre-commit-gate.sh`（全文，约 25 行）— 3 文件结构完全一致，改动模板
- `agate/scripts/commit-msg-self-gate.sh`、`agate/scripts/pre-push-gate.sh`（全文）— 同结构同步改动
- `agate/tests/integration/test_pre_commit_hook.py`（PATH/探测相关用例风格，grep `PATH` 定位）— BDD-10/11 回归测试参照模式
- `agate/platform-notes.md:140-170`（已知限制表 + Windows 原生章节）— BDD-12 文档落点
- `AGENTS.md:40-43`（Gate 脚本分层节）— BDD-12 文档落点

## 8. minimal_validation

```yaml
minimal_validation:
  - assumption: "DEBT0012：check-protocol-consistency.py --strict 在 WARNING-only 场景 exit 2，与该值置于 && 链路中间时会短路链路后续命令"
    method: "3 行 python subprocess 最小复现：subprocess.run('true && (exit 2) && echo STEP3_RAN', shell=True)，用 exit 2 模拟 --strict 的真实返回值"
    result: "confirmed"
    note: "chain exit code=2，STEP3_RAN 未打印（STEP3 ran: False）——确认 && 链路在中间步骤非零退出时确实短路后续步骤，与 P1 BDD-9 描述现象一致，且与 check-protocol-consistency.py 实际代码（main() 尾部 if rep.warnings and args.strict: return 2）读代码确认的返回值语义一致"
  - assumption: "DEBT0014：探测循环加候选可执行性小测试（\"$CAND\" -c \"\" 非零则跳过）能正确跳过不可执行候选并继续探测下一候选；AGATE_PYTHON 显式指定能跳过整个探测循环"
    method: "构造模拟 stub：fake-bin/python3（脚本体 exit 49，模拟 Store 占位符非交互 exec 直接 49）+ fake-bin2/python（脚本体 exit 0，模拟真实可用候选）。在 PATH=fake-bin:fake-bin2:$PATH 下跑候选设计的探测循环片段（CAND=$(command -v \"$c\") || continue; \"$CAND\" -c \"\" >/dev/null 2>&1 || continue; PY=\"$CAND\"; break）；另测 AGATE_PYTHON=/usr/bin/python3 场景验证循环体被跳过"
    result: "confirmed"
    note: "场景 1：resolved PY=.../fake-bin2/python——探测正确跳过不可执行的 python3 stub，继续探测并解析到 python。场景 2：resolved PY=/usr/bin/python3——AGATE_PYTHON 显式指定时探测循环体未执行，直接采用显式路径。**诚实声明**：本验证在 Linux 用模拟 stub 完成（构造 exit 49 的假可执行文件），不代表真实 Windows Store 占位符已实测；真实 Windows 场景由 CI matrix（pytest -m windows_smoke）冒烟兜底，P6 acceptance 措辞不得声称'已在 Windows 实测通过'（P1 verification_env 约束、P0-brief 约束 3 均已明确要求）"
  - assumption: "DEBT0010：4 处解析脚本的排除逻辑是纯代码字符串/正则处理，无外部系统依赖"
    method: "纯代码逻辑，无外部系统依赖。依赖的内部函数/数据转换：re.findall 正则提取 gate_commands 块内的 key/value 对（4 个脚本各自的正则模式不同但同属字符串解析）、str.endswith 后缀判断（新增 is_gate_meta_key 集中此判断）、json.dumps 序列化输出。已读 4 个脚本源码逐行核实当前逻辑（见 P2-progress.md），不存在浏览器/网络/文件系统之外的外部依赖"
    result: "not_needed"
    note: "声明性验证，非「待验证假设→实测确认」类型；已通过读代码 + 单测设计覆盖代替最小验证"
  - assumption: "DEBT0011：SELF-GATE.md 命名模板改动 + 写入前检查逻辑是纯文档/文本改动，无外部系统依赖"
    method: "纯代码逻辑，无外部系统依赖。依赖的内部函数/数据转换：字符串模板替换（{date}/{task_id}/{NN} 占位符拼接），Write 前检查逻辑依赖 Bash test -f（文件系统存在性判断，非浏览器/网络行为）"
    result: "not_needed"
    note: "文档模板改动，无需最小验证；BDD-7/8 的可判定性通过'两个不同 task_id 生成不同文件名'这一字符串拼接结果直接验证，P3 测试设计阶段可用简单字符串断言覆盖"
```
