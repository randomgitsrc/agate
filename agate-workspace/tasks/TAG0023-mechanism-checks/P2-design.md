---
phase: P2
task_id: TAG0023-mechanism-checks
type: design
parent: P1-requirements.md
trace_id: TAG0023-P2-20260824
status: draft
created: 2026-08-24
agent: architect
candidate_count: 8
packages: [agate]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 5, batches: [{id: batch-A-RM-AG0042, complexity: medium}, {id: batch-B-RM-AG0043, complexity: medium}, {id: batch-C-RM-AG0044, complexity: high}, {id: batch-D-RM-AG0045, complexity: medium}, {id: batch-E-RM-AG0032-manual, complexity: low}]}
---

> [PROD_NOT_TOUCHED] 本阶段仅读取 P1/P0/复盘/HANDOFF/角色卡片/worktree 脚本源码 + 用 `gh api` 只读拉取
> 公开 GitHub Actions 日志（PR #188）+ 本地临时 git 仓库/浅克隆做最小验证实验（均在 `/tmp/claude-*`
> scratchpad 与本 worktree 内，未落盘到项目仓库外任何生产路径），无任何写操作落在 worktree 之外。

# P2 方案设计 — TAG0023 机制校验补强批

## 0. 结论速览（供 P3/P4 快速定位）

| 子项 | 落点（不新建脚本） | 校验强度 | 关键结论 |
|------|------|------|------|
| RM-AG0042（BDD-1~4）| `check-state-transition.py` 新增函数 | BDD-2 阻断；BDD-1/BDD-3 高优 WARNING（分层，见 D1。**P2 重试 #2 修正**：BDD-1 因枚举正则仍有结构性残余假阳性风险，由阻断下调为与 BDD-3 同级 WARNING） | 事件源三类均已给出机器判定规则（§2.1）；**BDD-1 P2 重试 #2**：正则由"文件名含 review 子串的宽松通配"收紧为"C8 已知评审角色 token 精确枚举"（D6），并显式承认无法排除的残余边界 |
| RM-AG0043（BDD-5~7）| `check-gate.py` `gate_p8()` 新增分支 | 阻断（exit 1）| 匹配算法=`task_id` 精确匹配「关联任务」列（§2.2，D2）|
| RM-AG0044（BDD-8~10）| `check-debt.py._retreat_coverage()` L75 | WARNING（现状不变）| **根因已确认**（非候选）：CI runner git 2.55.0 vs 本地 2.43.0 的 auto-abbrev 长度差异（§2.3，已用真实 CI 失败日志实证，见 `minimal_validation`）|
| RM-AG0045（BDD-11~13）| `assets/templates/dispatch-prompt.md`「返回前自检」节新增子项 + `agate-frontmatter-check.py` 错误消息增强 | subagent 自检非 0 退出即需自行修正后再返回 | D5：挂载既有"返回前自检"模式**可行**，不新造写入拦截机制（§2.4）|
| RM-AG0032 历史补记 | `roadmap.md` 人工补一行 | — | P8 阶段主 Agent 直接编辑，非脚本改动（§2.2 末）|

**H3 更新结论**：dispatch-context 预判"0042/0043 同触碰 `check-gate.py` 不同分支"——本设计下**不成立**。RM-AG0042 落点最终定在 `check-state-transition.py`（复用已有 `retries_over` 所在文件，理由见 §2.1），RM-AG0043 落点在 `check-gate.py`，两批**生产代码文件零重叠**，比字面预判的"错开分支"更彻底（连文件都不共享）。批次仍按 dispatch-context 建议拆分（保持关注点分离、便于独立 review/独立 commit），但技术上 A/B 两批可并行执行，不存在互斥依赖。

---

## 1. 影响面梳理（先于候选方案）

### 1.1 改什么（Modify）

| 文件/小节 | 改动点 | 关联 BDD |
|-----------|--------|----------|
| `agate/scripts/check-state-transition.py` | 新增函数（暂命名 `check_retries_correspondence()`），在 `main()` 现有检查 1/2/4 之后新增检查 3；复用 `get_old_phase()` 的 git-show-HEAD 模式新增对称的 `get_old_retries_len()` | BDD-1/2/3/4 |
| `agate/rules/state-transitions.md` §「回退规则」/「重试上限」 | 补充措辞："单步回退（Pn→Pn-1）必须同步在 retries[目标阶段] 追加一条记录，否则被 gate 拦截"（把现有 prose 规程升级为"有机械校验兜底"的表述）| BDD-1/2（文档同步） |
| `agate/state-machine.md` L587-624「重试记录也要落盘」/ L668-714「⑩L1 阶段内再评审循环」| 同上，补充"该步骤现由 check-state-transition.py 机械校验"一句 | BDD-1/2/3（文档同步） |
| `agate/dispatch-protocol.md` / `agate/WORKFLOW.md` 相关小节 | 补充"评审 rejected 后必须写 retries"提示（H3 隐含需求）+ **P2 重试 #1 新增**：在「评审打回后的意见回流」节新增强制措辞——"重新派发评审角色时必须写新编号的 `P{n}-dispatch-context-{role}-retryN.md`/`-revN.md`，不得覆盖旧文件"，把 BDD-1 新事件源依赖的命名惯例从历史实践固化为协议明文（见 §2.1 D6） | BDD-1 |
| `agate/scripts/check-gate.py` `gate_p8()`（L1181-1257）| 新增分支（暂命名 `_check_roadmap_done(task_id, roadmap_path)`），在 P8-release.md 字段检查之后、version/CHANGELOG 检查之前插入；无匹配 RM 不提前 return，检测到非 done 提前 `return 1` | BDD-5/6 |
| `agate-workspace/roadmap/roadmap.md` | ①主 Agent 在 P8 阶段人工把 RM-AG0032 对应行状态改为 `done`（新增一行，参照既有 done 行格式，「关联任务」沿用 `TAG0020`）②任务本身完成后 RM-AG0042~0044 三行回写 `done`（P8 常规动作，不在 P2 设计范围内特别处理）| BDD-7 |
| `agate/scripts/check-debt.py` `_retreat_coverage()`（L48-81，聚焦 L75）| `short = full[:7]` → 改为调用 `git rev-parse --short {full}`（新增 `_short_hash()` helper，复用 `run_git`）得到运行环境下的真实 short 长度，同时保留原有 `full` 全量兜底比对 | BDD-8/9 |
| 新建：`agate/tests/ENV-SENSITIVE-TESTS.md`（集中清单，路径见 §2.3）| 新文件，登记 test_bdd_7/test_bdd_25/test_bdd_14 三条目 + 根因分类字段 | BDD-10 |
| `.github/workflows/protocol-tests.yml` pytest job（Linux 步骤）| 新增 `pytest-rerunfailures` 依赖 + `--reruns 1` 参数（见 §2.3 权衡）| BDD-9（辅助，非直接判据）|
| `agate/scripts/agate-frontmatter-check.py` `_check()`（L143-194）| 每个 `errors.append(...)` 调用追加一句修复提示文本（如"缺必填字段 X → 在 frontmatter 补 `X: <值>`"）| BDD-12 |
| `agate/assets/templates/dispatch-prompt.md`「返回前自检」节（L92-96）/「返回前自检（强制）」节（L288-292）| 新增子项："若本次产出含 P1-requirements.md/P2-design.md，返回前先跑 `check-frontmatter.py {文件}`；若 P1 声明 `ceremony: thin`，额外 `git add` 本阶段产出后跑 `check-routing.py {task_dir}`，非 0 退出先修正再返回" | BDD-11/12/13 |
| 各批次对应 `agate/tests/unit/test_*.py` | 新增用例覆盖上述改动（见 §4 完成标准逐条）| 全部 BDD |

### 1.2 不改什么（Not Modify）

| 文件/范围 | 理由 |
|-----------|------|
| `agate/scripts/agate-state-yaml-check.py`（retries 字段格式校验）| P1 §4.1 判定：只校验格式合法性，与本次"对应性校验"职责不重叠，继续保留 |
| `agate/scripts/check-retrospective.py`（含 `_scan_debt_roadmap_signal`）| P1 §4.1/§4.2 判定：复盘阶段的信号扫描，与 retries 对应性 / P8 roadmap done 校验是不同判定维度，不构成同类实现面 |
| `agate/scripts/check-protocol-consistency.py` | 只做协议文档间字段一致性核对，不涉及 retries/roadmap 值本身的对应性判定 |
| `agate/LIMITATIONS.md` 既有 P5 机械化回归判定机制本体（`pre-task-baseline.md` + `known-failures.md`）| P1 §4.3 判定：这是"新增失败回归判定"机制，与本次"环境敏感测试专门分类清单"是不同维度，机制本体不改，只新增独立清单文件 |
| `agate/scripts/check-yaml-schema.py` + `agate/rules/schema/*.json`（RM-0022 结构化层）| dispatch-context 明示：本次只在写路径接入既有 schema 校验能力，不重做 YAML schema 基建 |
| `agate-retreat-state.py` / `agate-retreat-to.py` 本体逻辑 | **关键发现**（§2.1）：`write_retreat` 操作已经会追加 retries 记录，问题不在这两个脚本内部逻辑缺失，而在于"是否被实际调用"未被检测——本次不改这两个脚本，只在 `check-state-transition.py` 新增"回退发生但 retries 未同步增长"的旁路检测 |
| `check-routing.py` `_staged_source_count()` 本体逻辑 | 该函数的 git-staged-diff 计算逻辑本身正确（RM-AG0027 已修复过 `_timeout_seconds` 后缀等问题），RM-AG0045 只是把"调用时机"提前到 subagent 返回前，不改函数内部实现 |
| `check-yaml-schema.py` 与 `agate-frontmatter-check.py` 的双源关系 | 保持现状并行（YAML 侧 schema 是 RM-0022/0038 已完成基建，本次不合并两套校验器）|

### 1.3 风险在哪（Risk）

| 风险 | 缓解措施 |
|------|----------|
| 0042/0043 表面同簇实际不同文件，但 4 份协议文档（state-transitions.md/state-machine.md/dispatch-protocol.md/WORKFLOW.md）均可能被 0042 批次触碰——若批次 D（0045）也需要改 dispatch-prompt.md，属不同文件，无冲突；但若后续发现 0043 也要动 state-machine.md（本设计判定不需要），需在 P4 前二次确认 | 批次边界已按「改什么」表逐文件锁定，P4 implementer 严格按 `files_to_read` 范围操作，不得"顺手"改本设计未列出的文件 |
| RM-AG0044 根因验证不充分导致修复无效 | 已用真实 CI 失败日志（PR #188 run 32645685798 job 97209482443）forensic 分析确认根因（CI git 2.55.0 vs 本地 2.43.0 auto-abbrev 长度差异），非停留在"候选机制"猜测；修复方案（动态 `git rev-parse --short`）直接对症；剩余风险仅是"是否还有其他潜在环境敏感点未发现"，用 BDD-9 连续 5 次 CI 稳定作为最终验收兜底 |
| RM-AG0045 写时校验若挂载方式不当，可能只是"换个位置的 commit-time 检查"| 已在 §2.4 明确区分：`agate-frontmatter-check.py` 部分（coupling_checklist 类型/FIND-5 全角冒号）是**真正的写时提前**（不依赖 git 状态，Write 工具调用后立即可跑）；`check-routing.py` 的"源码数"检查因其实现依赖 `git diff --cached`，**技术上仍需 git add**，但因为整个自检发生在 subagent 自己的回合内（早于"主 Agent 收到返回→决定是否打回重写"这一次完整折返），仍然消灭了 BDD-13 定义的"commit 折返"（折返的成本单位是"subagent 与主 Agent 之间的一次往返"，不是"是否发生过 git add"）——本设计对此边界诚实标注，不含糊带过 |
| CI 新增 `pytest-rerunfailures --reruns 1` 可能掩盖真实新增回归（不只是环境敏感测试）| 权衡见 §2.3 候选方案 B 讨论；缓解＝reruns 值保守（只重试 1 次，不无限重试）+ 集中清单机制持续观察，若发现非环境敏感测试被意外掩盖，后续可用 `--only-rerun` 参数收紧到清单内测试 id（本次不预先实现该收紧，YAGNI，问题未出现前不预防）|
| 跨模块引用：`get_old_phase()` 模式需要在新函数里对称复用（读取 retries 而非 phase）| 复用同一 git-show-HEAD 子进程调用范式，不重新发明；单测覆盖 HEAD 版本读取失败（如 `.state.yaml` 首次创建，无 HEAD 版本）时的降级行为（视为 old_retries_len=0，不误报） |
| 双源同步：state-transitions.md / state-machine.md 两份文档均提及 retries 语义，本次改动需同步措辞，避免再次出现"文档提了但脚本没做"或反过来的漂移 | P7 一致性检查阶段专门核对这两份文档与 `check-state-transition.py` 新函数的措辞是否对齐（P2 完成标准已列判据） |

---

## 2. 候选方案（8 个，按 4 子项分组，每组 2 候选 + 权衡 + 选择理由）

### 2.1 RM-AG0042：门槛失败事件强制记录 retries

**关键发现**（读代码得出，非猜测）：`agate-retreat-state.py` 的 `write_retreat` 操作**已经会**在回退时 `attempts.append({"attempt": ..., "reason": ...})` 并写回 `retries[NEW_PHASE]`；`agate-retreat-to.py` 也已调用它。复盘中"四任务 retries 全为 `{}`"说明实际执行时**未走这条标准工具路径**，而是绕过它直接手改 `.state.yaml` 的 `phase` 字段。同时 `check-state-transition.py` 现有检查 1（回退跳变判定）只在 `diff(old_num - new_num) >= 2` 时触发，`diff==1`（如复盘实证的 P5→P4 单步回退）完全未被覆盖——这正是 BDD-2 的真正机制缺口。

**候选 A（选定）**：在 `check-state-transition.py` 内新增函数，不新建脚本。

- 事件源判定规则（三类，机器可判定）：
  - **BDD-1（评审 rejected，P2 重试 #2 修正，见下方「BDD-1 事件源重新设计（D6）」专节）**：扫描 `task_dir` 下文件名精确匹配 `^P(\d+)-dispatch-context-(requirements-review|plan-eng-review|plan-design-review|plan-ceo-review|cso|review|design-review|review-eng|review-cso)-(retry|rev)\d+\.md$`（C8 已知评审角色 token 枚举，非文件名含 review 子串的宽松通配）的**评审角色重试/复评 dispatch-context 文件**；命中即提取阶段号 Pn，若 `.state.yaml` 的 `retries[Pn]` 为空/缺失 → **高优 WARNING（非阻断，P2 重试 #2 下调，理由见 D1）**。信号源是"评审角色被二次派发"这一从写入起就不会被覆盖的文件系统事实，不再依赖已提交/暂存 review.md 的 `status:` 字段——原方案在现行"驳回→修订→再评审→approved 全流程发生在同一次 commit 之前"的协议下结构性不可能触发，证据与重新设计过程见下方专节
  - **BDD-2（P5→P4 回退）**：复用 `get_old_phase()` 的 git-show-HEAD 范式，新增对称函数读取 HEAD 版本与暂存版本的 `retries[new_phase]` 长度；`old_num > new_num`（含 diff==1）且暂存版本长度未大于 HEAD 版本长度（即本次 commit 没有新增 retries 条目）→ 拦截
  - **BDD-3（子代理空返回重派）**：扫描 `P{n}-progress.md` 或该阶段 dispatch-context 文件是否含"空返回"/"重派"关键词信号；命中且 `retries[Pn]` 为空 → **高优 WARNING**（非阻断，理由见下方 D1）
- 校验强度（D1，**P2 重试 #2 重新定案**）：**分层，BDD-1 由阻断下调为高优 WARNING**——
  - **BDD-2 保持阻断（exit 1）**：信号是 phase 数值倒退（`old_num>new_num` 且暂存 retries 长度未增长），纯结构化数值比较，无自由裁量空间，误报率低，维持原判断
  - **BDD-1 改为高优 WARNING（不阻断，本轮下调，推翻 P2 重试 #1 的阻断定案）**：P2 重试 #1 把 BDD-1 定阻断的理由是"信号来源客观、已用 36 个真实历史文件验证零假阳性/假阴性"——这个理由已被 P2-review.md 复评第 2 轮推翻：独立复核发现真实历史文件总数是 34（非 36）、原始宽松正则匹配 15/19（非声称的 13/17），且 15 个匹配中有 2 个确认假阳性（详见下方 D6 专节的完整核实过程）。本轮把正则收紧为 C8 角色 token 精确枚举后，重新核验：34 个历史文件中枚举正则匹配 13/21，两个已知假阳性均被排除（详见 D6）。但即便如此，枚举法本质是"文件名 token 是否恰好等于已知评审角色字符串"的字符串匹配，无法从逻辑上排除两类结构性残余风险：①未来新增的非评审角色如果恰好用了与枚举 token 完全相同的名字（历史已发生一次：`P7-dispatch-context-consistency-reviewer-retry1.md` 文件名 token 精确等于一个"像评审角色"的字符串，但真实执行角色是 architect）；②`retries[Pn]` 字段本身当前处于"复盘中四任务全为 `{}`"的已知不可靠状态（RM-AG0042 本身要修的问题），在过渡期内该字段的准确性尚未被验证，把一个尚未被验证可靠的字段和一个尚未被验证能 100% 排除假阳性的正则组合起来做阻断级判定，双重不确定性叠加，误判后果是直接拦截 commit（自锁风险）——不符合"阻断级信号来源必须结构性确定"的门槛。故降级为与 BDD-3 同级的高优 WARNING：提示但不阻断，待 dispatch-protocol.md 完成命名惯例明文固化（见 D6 缓解，P4 交付物）且线上运行一段时间验证枚举 token 无新假阳性后，可作为后续任务的升级候选（本轮不预先做这个升级判断，避免重蹈"自报验证充分"的覆辙）
  - BDD-3 维持高优 WARNING（不阻断），信号来源是自由文本关键词扫描，主观性高，误报成本可能导致任务自锁——与 P2 重试 #1 判断一致，本轮未变
  - 本设计给出的仍是"按信号置信度分层"的结论，而非笼统单一强度；分层依据从"BDD-1/2 客观 vs BDD-3 主观"两档，细化为"BDD-2 结构化数值比较（阻断）> BDD-1 字符串枚举匹配+待验证字段（WARNING）> BDD-3 自由文本关键词（WARNING）"三档置信度序列

**BDD-1 事件源重新设计（D6，P2 重试 #1 新增，替换原方案）**：

原判定规则——"扫描已提交/暂存 review.md 的 `status: rejected` 字段"——经独立评审（`P2-review.md`）用 3 个真实 `git log` 案例（本任务自身 `P1-review.md`、`TAG0019-risk-routing/P1-review.md`、`TAG0016-protocol-hygiene/P4-review.md`）证实结构性不可行：agate 现行协议下评审驳回→修订→再评审→approved 的完整迭代循环全部发生在同一次 commit 之前（`phase-cards/P2-design.md` 步骤 3→5→6），被驳回的中间版本从未单独进入 git 历史，`check-state-transition.py`（pre-commit hook）能读到的 review.md 版本按协议必然已是"approved 之后才发生的那次 commit"版本，`status: rejected` 永远不可观测。

**候选 1（选定）——评审角色重试 dispatch-context 文件存在性**：核实本仓库 `agate-workspace/tasks/*/` 下 7 个历史任务（TAG0008/16/17/19/20/23）的 `*-dispatch-context-*.md` 实际命名，发现一条稳定惯例：主 Agent 每次重新派发某角色时，若该角色已有过前序派发，一律写一个**新编号**的 `P{n}-dispatch-context-{role}-retryN.md` 或 `-revN.md` 文件，**从不覆盖旧文件**（如本任务 `P1-dispatch-context-requirements-review-retry1.md`、TAG0019 的 `P2-dispatch-context-plan-eng-review-rev2.md`、TAG0019 的 `P4-dispatch-context-review-cso-rev2.md`）。按 phase-cards 派发纪律（同一角色首次派发不带数字后缀），"某评审角色的 retryN/revN 派发文件存在"本身就是"该阶段评审发生过驳回"的直接证据，且该文件早于 commit 落盘、写入后永不被覆盖或删除——正是原方案缺失的持久性属性。

**正则修正（P2 重试 #2，逐文件重新核实，不采信任何一方历史自述数字）**：本轮独立重新跑了一遍全仓统计，过程与结果如下（可复现）：
1. `find . -iname "*dispatch-context*.md" | grep -v node_modules` → 440 个文件；过滤出文件名以 `-(retry|rev)\d+\.md$` 结尾的 → **34 个历史文件**（不含本任务本轮自身新产生的 `P2-dispatch-context-architect-retry2.md`）——与 P2-review.md 复评第 2 轮独立核实的数字一致，**不是** P2 重试 #1 声称的 36，也不是 dispatch-context 复评轮转述的 30
2. 用 P2 重试 #1 的原始宽松正则 `^P(\d+)-dispatch-context-.*review.*-(retry|rev)\d+\.md$`（文件名含 "review" 子串即命中）对这 34 个文件逐一匹配 → **15 匹配 / 19 不匹配**，不是声称的 13/17。逐一读取 15 个匹配文件的 frontmatter/正文核实真实角色，确认 **2 个假阳性**：
   - `agate-workspace/archived/tasks/T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md`——frontmatter `role: implementer`，正文明确是"主 Agent 账号触发月度 API 花费上限、在做任何代码改动之前就失败终止"的干净重启，与评审驳回无关，文件名恰好含 "review-fix"（响应上一轮 review 意见修复的角色名后缀，不是评审角色本身）
   - `agate-workspace/tasks/TAG0016-protocol-hygiene/P7-dispatch-context-consistency-reviewer-retry1.md`——frontmatter `role: architect`，正文同样是配额中断重启；且核实 `phase-cards/P7-consistency.md` 模板本身固定要求"1.1 写 `P7-dispatch-context-consistency-reviewer.md`"——这是**协议规定的标准文件名**，意味着每个任务的 P7 重试都会产生这个 token，不是偶发命名，是结构性命中源
3. 核实 `agate/rules/review-mapping.md`（C8 映射表）与 `agate/assets/review-roles/` 目录下全部 11 个角色文件（`cso.md`/`design-review.md`/`investigate.md`/`judge.md`/`plan-ceo-review.md`/`plan-design-review.md`/`plan-eng-review.md`/`protocol-alignment-review.md`/`qa.md`/`review.md`/`requirements-review.md`）的 `role_id` 字段，确认 `consistency-reviewer` **不在**注册角色清单中——它只是 P7 阶段"architect 兼任一致性检查"这一执行角色的历史文件命名别名，不是 C8 表内任何一条评审委员会角色，语义上也不属于 BDD-1 要捕捉的"P1-P4 评审委员会 rejected → retry"事件（P7 自身的重试由 P7 gate 的 `[BLOCKER]`/`[DEVIATION-CRITICAL]` 机制把关，不产出 `status: rejected` 的委员会评审文件）。基于这条已核实的依据，新枚举**排除** `consistency-reviewer`（而非像 P2-review.md 建议正则那样保留它、再靠兜底信号排除）——这不是"回避问题"，而是纠正了把一个非评审角色的历史命名误当作评审信号源收进枚举的设计错误。同理排除 `protocol-alignment-review`（该角色 `agent:` 字段实际是 `review`，34 个真实文件中从未以 `protocol-alignment-review` 作为文件名 token 出现过，真出现时会被 `review` token 命中）、`qa`/`judge`/`investigate`（均未在 34 个真实文件中观测到，且 `judge` 属 P6.5 独立机制，已有专属 `judge_verdict` 事件账本，非本 BDD 覆盖范围）
4. **最终枚举正则**：
   ```
   ^P(\d+)-dispatch-context-(requirements-review|plan-eng-review|plan-design-review|plan-ceo-review|cso|review|design-review|review-eng|review-cso)-(retry|rev)\d+\.md$
   ```
   `review-eng`/`review-cso` 是从 34 个真实文件里逐一核实到的复合 token（TAG0019 的 `P4-dispatch-context-review-eng-rev2.md` 真实角色 `role: review`、`P4-dispatch-context-review-cso-rev2.md` 真实角色 `role: cso`——C8 表按 domain 派 P4 后评审时，历史命名习惯把 domain 后缀拼在 "review-" 后面），不是凭空推测的通配。用此正则重新匹配全部 34 个文件 → **13 匹配 / 21 不匹配**，两个已确认假阳性均被正确排除，13 个匹配逐一核对（含本任务自身 2 个无 frontmatter 的新格式文件，靠读正文内容而非 `role:` 字段确认角色属实）全部为真实评审委员会重试事件，无遗漏、无误判。

**残余边界（显式承认，不假装枚举能解决一切）**：本轮的枚举法解决了当前已知的 2 个假阳性，但不构成"逻辑上排除一切假阳性"的证明——枚举本质是字符串匹配，只要未来出现新角色的名字恰好完全等于枚举中某个 token（`consistency-reviewer` 案例已经证明这种命名碰撞在本仓库真实发生过一次），该正则仍会误判。且这类误判**无法**用"读 frontmatter `role:` 字段核实"来兜底排除——本任务自身的 `P1-dispatch-context-requirements-review-retry1.md`/`P2-dispatch-context-plan-eng-review-retry1.md` 就是纯 Markdown 新格式，完全没有 `---` frontmatter 块（已现地核实两文件全文，无 `role:` 字段可读），"检查 frontmatter 角色字段"这条路不总是可行，机制设计不能假设它总能生效。因此本设计**不**依赖 frontmatter 兜底，而是从校验强度层面处理这个残余风险（见 D1：BDD-1 由阻断下调为高优 WARNING，直到 dispatch-protocol.md 完成命名惯例明文固化 + 线上运行验证无新假阳性）。

- 优点：零新增写入义务——完全复用主 Agent 已有的派发行为（该文件本就会因重新派发而产生），不要求任何角色/脚本新学一个"记账"动作；枚举法比原宽松通配显著收窄误判面（15→13 匹配，两个已知假阳性均排除）
- 缺点：①命名惯例目前只是历史实践，未见 dispatch-protocol.md 有明文规定"必须用递增数字后缀、不得覆盖旧文件"——理论上未来派发实践可能漂移；②枚举法对"未来新角色恰好撞上已知 token"这类命名碰撞无免疫力（残余边界，上文已展开）
- 缓解：**P4 交付物**——需在 `agate/dispatch-protocol.md`「评审打回后的意见回流」节新增强制措辞（见 §1.1 改动表第 4 行），把"重新派发评审角色时必须写新编号的 `P{n}-dispatch-context-{role}-retryN.md`/`-revN.md`，不得覆盖旧文件"从"历史上恰好如此"升级为"协议明文要求"，并**新增一条禁止性措辞**："非评审角色的 dispatch-context 文件命名不得使用与 C8 评审角色 token 相同或包含其作为独立词段的名字"（直接预防 `consistency-reviewer` 类碰撞再次发生）。此为 P4 阶段落地项，P2 阶段本身不修改协议文档（已用 `git diff HEAD --stat` 确认 `dispatch-protocol.md` 当前无任何改动，符合"P2 只设计不实现"边界）

**候选 2（备选，未选）——扩展 `gate-events.jsonl` 事件账本**：本仓库已有 append-only 事件账本（`check-events.py` 审计哈希链+ts单调，未知 event 类型不拦截，扩展新类型技术上安全），在评审 verdict 产出时追加一条 `review_verdict` 事件。

- 优点：复用既有账本基建（哈希链完整性 + 审计脚本已存在），不新建文件类型
- 缺点：核实 `pre-commit-gate.py` L356-380 后发现，账本现有两类事件（`gate_run`/`state_transition`）**全部只在 `git commit` 触发的 pre-commit hook 内 append**（`_run_script_capture` 调用点在 `main()` 内，随 commit 一次性写入）——与原 BDD-1 的 review.md 完全同源的"仅 commit 时可观测"局限。要让 `review_verdict` 事件在驳回发生的当下（而非最终 approved commit 时）就被写入，必须新增一个**不依赖 commit 触发**的写入点（如要求主 Agent 或评审 subagent 在产出 `status: rejected` 的 P{n}-review.md 后额外调用 `append_event()`）——这是一条全新的协议写入义务，且本仓库目前唯一"非 commit 触发、由校验脚本主动写账本"的先例是 `check-judge-verdict.py` 专属 P6.5 阶段的 `judge_verdict` 事件（见 `agate/scripts/check-judge-verdict.py` 第 9 步），从未有覆盖"P1/P2/...任意评审阶段通用 rejected 事件"的先例，等于要新建一整套通用写入协议，与 dispatch-context「不发明新写入拦截机制」的既有教训（RM-AG0045 §2.4 同批已验证过的原则）相悖
- 未选理由：候选 1 用零新增写入义务达成同等效果（甚至更强的历史数据验证），候选 2 的"复用账本"优点被"仍需新造写入义务"的实际成本抵消，不是更优选择

**选择**：候选 1。理由：①零新增写入义务，纯观测既有派发行为②已用本仓库 34 个真实历史文件逐一核实（非估算/转述），枚举正则排除了已发现的全部 2 个假阳性，13/21 分类全部逐文件验证③持久性来源可解释（从不覆盖旧文件的现有惯例）④已知缺点有明确缓解路径（P4 固化命名惯例为协议明文），未知的命名碰撞类残余风险已通过校验强度下调（D1：WARNING 而非阻断）做兜底，不依赖"正则 100% 准确"这一无法证明的强假设。
- 工作量：改 1 个现有文件（新增 1 个函数 + `main()` 内新增 1 处调用）+ 4 处文档措辞同步 + 3-4 个新单测

**候选 B（备选，未选）**：新建独立脚本 `check-retries-correspondence.py`，由 pre-commit hook 单独增加一个调用点。

- 优点：与"回退跳变/重试上限"两个既有检查关注点分离，未来独立维护/测试更清晰
- 缺点：① 需要复用或重复实现 `get_old_phase()`/`_run_state_get()` 等基础设施（要么拆成公共库增加改动面，要么重复代码违反 DRY）② 需要新增 hook 配置调用点（`pre-commit-gate.sh` 需改），比"在现有脚本加函数"改动面更大 ③ 从数据源看，仍然强依赖同一份 `.state.yaml` / `git diff --cached` 机制，与 `check-state-transition.py` 本质同属"状态转移合法性"判断范畴，拆开是不必要的关注点过度切分
- 未选理由：改动面更大且无实质收益（不新增可测试性、不降低耦合，只是物理挪了个文件位置）

**选择**：候选 A。理由：改动面最小、直接复用已验证的 `get_old_phase()` 模式、`check-state-transition.py` 本身职责定位（"状态转移合法性检查"）与"retries 对应性"属同一职责范畴，不新增 hook 调用点。

### 2.2 RM-AG0043：P8 roadmap 回写 done 校验

**现状确认**：`gate_p8()`（L1181-1257）全函数内无任何 `roadmap.md` 读取；`roadmap.md` 表结构核实：列为 `id|标题|状态|来源|关联任务|创建|更新`，`task_id` 落在「关联任务」列，纯文本精确值（如 `TAG0023`）。**实地取证**：RM-AG0042/43/44/45 四行「关联任务」均 = `TAG0023`（一个 task 关联多条 RM 的真实实例，D2 场景已现地取证，非假设）；RM-AG0032 两行分别为「关联任务=—」（无 task）与「关联任务=TAG0020」（历史 task，非当前 TAG0023）。

**候选 A（选定）**：在 `check-gate.py` `gate_p8()` 内新增分支 `_check_roadmap_done(task_id, roadmap_path)`。

- 匹配算法（D2，本设计定案）：
  1. 读取 `.state.yaml` 的 `task_id`（复用 `agate-state-get.py task_id` 现有操作）
  2. 逐行解析 `roadmap.md` 表格（按 `|` 分列），取「关联任务」列
  3. 收集「关联任务」列值**精确等于**当前 `task_id` 的所有行（支持一个 task 关联多条 RM，天然覆盖已取证的 4 行场景）
  4. 全部匹配行的「状态」列必须为 `done`；任一非 `done` → `return 1`，报出该 RM 编号与当前状态
  5. 无匹配行（含"关联任务列值是别的历史 task_id，如 TAG0020"这种情况）→ 不触发拦截，函数直接返回、`gate_p8()` 继续走后续既有检查（BDD-6：这天然覆盖了"历史 RM 无当前 task 关联"不误拦的场景，因为它们的「关联任务」值本来就不等于当前 task_id）
  6. 暂不支持「关联任务」列多值分隔符（如逗号分隔多个 task_id）——现存数据全部是单值，YAGNI，若未来出现多值场景再扩展
- 工作量：改 1 个现有文件（新增 1 个函数 + `gate_p8()` 内新增 1 处调用）+ 2-3 个新单测

**候选 B（备选，未选）**：新建独立脚本 `check-roadmap-done.py`，与 `gate_p8()` 解耦，由 P8 阶段单独调用。

- 优点：若担心"同触碰 check-gate.py"风险，物理拆开更彻底
- 缺点：① P8 gate 现有职责本来就是"P8 阶段完成检查"，roadmap done 回写逻辑上属于其子项，人为拆分成两个脚本增加调用点维护成本（P8 阶段需要主 Agent 记住"跑两个脚本"而非一个）② 复盘证据本就明确指向 `gate_p8()` 函数体内部缺失这个分支，拆成独立脚本偏离了问题的自然落点 ③ 本设计已确认 RM-AG0042 落点在 `check-state-transition.py`（§2.1），与 `check-gate.py` 完全不重叠，H3 风险已自然解除，候选 B 试图规避的风险前提本身不成立
- 未选理由：H3 风险已通过 RM-AG0042 落点选择解除，候选 B 的"物理隔离"收益不再存在，反而增加不必要的脚本数量

**选择**：候选 A。理由：改动面最小、逻辑上归属 P8 gate 既有职责、H3 担忧的风险前提已不存在。

**RM-AG0032 历史补记（BDD-7）**：**主 Agent 人工操作，不新增脚本**。谁做——主 Agent；怎么做——P8 阶段直接编辑 `roadmap.md`，在 RM-AG0032 现有 `scheduled` 行（L31，「关联任务」=`TAG0020`）基础上新增一行 `done` 状态记录（参照其他 done 行格式，「关联任务」沿用 `TAG0020`，「更新」列改为本次操作日期）；何时做——P8 阶段，与本任务自身的 RM-AG0042~0044 roadmap 回写同批操作，无需等待新脚本存在。验证方式：`grep "RM-AG0032" roadmap.md | grep "done"` 非空。

### 2.3 RM-AG0044：环境敏感测试集中治理

**根因（已确认，非候选）**：见 §0「已确认」+ `minimal_validation` 字段完整证据链。核心结论——`check-debt.py._retreat_coverage()` L75 `short = full[:7]` 固定 7 位前缀切片，在 CI runner（git 2.55.0）与本地开发环境（git 2.43.0）下，`git rev-parse --short HEAD` 的 auto-abbrev 算法计算出的实际长度可能不一致（本地两个版本均恒定输出 7 位，无法本地复现；但 PR #188 真实失败 CI 日志证实该环境下确实触发了 mismatch）。

**候选 A（选定）**：`short = full[:7]` 改为调用 `git rev-parse --short {full}`（新增 `_short_hash(full, cwd)` helper，复用已有 `run_git`），得到运行环境下的真实 short 长度再比对 `covered` 集合；同时保留原有 `full` 全量兜底比对不变。

- 优点：与测试 fixture（`git rev-parse --short HEAD`）使用同一套计算逻辑，从根本上消除版本差异导致的不一致；改动量极小（约 3-5 行）
- 缺点：每次比对多一次 `git` 子进程调用（性能影响可忽略，`_retreat_coverage()` 只在 pre-commit/CI 时跑一次，retreat 提交数量通常个位数）
- 工作量：改 1 个现有文件（`check-debt.py` 新增 1 个 helper + 改 1 行调用）+ 1-2 个新单测（覆盖"不同长度 short 仍能正确匹配"场景）

**候选 B（备选，未选）**：不额外调用 git，改为宽松匹配——`covered` 集合中任一 token 是 `full` 的前缀（长度 ≥4 即可，不限定 7）即视为已覆盖。

- 优点：不新增 git 子进程调用
- 缺点：① 理论上存在极小概率的"另一个不相关 commit 的短前缀恰好也是当前 full 的前缀"误判风险（hex 空间碰撞概率虽极低但非零，比"重新计算真实 short"更不严谨）② 语义上"宽松匹配任意前缀长度"偏离了"short hash 应该是该环境实际生成的唯一标识"这一本质，只是规避症状不还原语义
- 未选理由：候选 A 直接消除不一致的根源（用真实环境计算值比对），候选 B 只是放宽容忍度掩盖问题，且引入非零的碰撞风险

**选择**：候选 A。理由：直接对症根因、改动最小、不引入新的匹配歧义。

**环境敏感测试判定标准**（BDD-8 四要素之二）：测试断言/前置条件依赖"外部环境计算结果的长度/内容会因平台或工具版本产生非代码逻辑相关的差异"（如 git 版本差异导致 short hash 长度不同、文件系统路径分隔符差异、临时目录挂载点差异），且该差异不代表被测代码本身存在缺陷 → 归类为"环境敏感测试"。

**集中清单文件位置与格式**（BDD-8 四要素之三，BDD-10 判据）：`agate/tests/ENV-SENSITIVE-TESTS.md`，登记字段：`test_id` / 根因分类（`basetemp位置依赖` / `git版本差异` / 其他）/ 状态（`已根治` / `观察中`）/ 关联 commit 或 RM 编号。初始至少含 3 条目：`test_bdd_7`（RM-0041，basetemp 位置依赖，已根治）、`test_bdd_25`（同上）、`test_bdd_14`（RM-AG0044，git 版本差异，本次修复）。

**CI flaky 自动重跑机制**（BDD-8 四要素之四）：`protocol-tests.yml` pytest job（Linux 步骤）新增 `pytest-rerunfailures` 依赖，追加 `--reruns 1`（保守，只重试 1 次，不无限重试）。**权衡（写入风险节）**：该参数是 pytest 全局重跑所有失败用例，无法只对"已登记在环境敏感清单"的用例生效，理论上可能掩盖非环境敏感的真实新增回归；缓解方式是保守取值（1 次）+ 后续若发现被意外掩盖，可用 `--only-rerun` 收紧到清单内 test id（本次不预先实现该收紧，问题未出现前不预防，YAGNI）。

### 2.4 RM-AG0045：声明写时校验

**关键约束发现**（读代码得出）：TAG0019 三类历史错误中，`coupling_checklist` 流式声明错误 + 半角冒号错误（FIND-5）由 `agate-frontmatter-check.py` 覆盖，可在 Write 工具调用后立即校验，不依赖 git 状态；但"源码数 6>5"由 `check-routing.py` 的 `_staged_source_count()` 计算，该函数读取 `git diff --cached --name-only`，**本质是 commit-time 计算**，纯"写文件"时刻（未 `git add`）无法得到真实源码数。

**候选 A（选定）**：挂载到 `assets/templates/dispatch-prompt.md`「返回前自检」标准节，新增"P1/P2 声明写时自检"子项。

- 具体机制：subagent 在返回前，若本次产出含 `P1-requirements.md`/`P2-design.md`：
  1. 跑 `python3 agate/scripts/check-frontmatter.py {写的文件路径}`（覆盖 coupling_checklist 类型错误 + FIND-5 全角冒号，纯文件内容校验，不依赖 git 状态——这是真正的"写时提前"）
  2. 若 P1 声明 `ceremony: thin`，额外先 `git add {写的文件}`（只 add，不 commit）再跑 `python3 agate/scripts/check-routing.py {task_dir}`（覆盖"源码数 6>5"类检查——**技术上仍依赖 git add**，但整个动作发生在 subagent 自己的回合内，早于"主 Agent 收到返回 → 决定是否打回重写"这一次完整往返，因此仍然消灭了 BDD-13 定义的"commit 折返"）
  3. 非 0 退出 → subagent 必须在本回合内修正后再返回，不允许把错误留给 commit-time 的 pre-commit hook
- 配套：`agate-frontmatter-check.py` 的 `_check()` 每个 `errors.append(...)` 追加一句修复提示文本（如"缺必填字段 X → 在 frontmatter 补 `X: <值>`"；"非法值 → 合法值见 {列表}，请改用其一"）
- **D5 结论（dispatch-context 明确要求给出）**：`dispatch-prompt.md` 自检步骤挂载**可行**，采用。理由——agate 当前架构下 subagent 的 Write 工具调用本身不可被 orchestrator 侧拦截（dispatch-context 已明示），真正可行的路径只能是"subagent 自己在返回前主动跑检查"（self-check-before-return），而这正是 `dispatch-prompt.md` 已有的既定模式（现有「返回前自检」节已要求 grep 确认落盘等），本次只是新增检查目标，不发明新写入拦截机制，不违反"不发明新架构"的既有教训（复盘 A2/LIMITATIONS 局限 3）
- 工作量：改 2 个现有文件（`dispatch-prompt.md` 新增子节 + `agate-frontmatter-check.py` 增强错误消息）+ 2-3 个新单测

**候选 B（备选，未选）**：新建独立 formatter CLI（如 `agate-declaration-format-check.py`），把三类检查（frontmatter schema + FIND-5 + 源码数）合并成一个统一入口，供 subagent 主动调用。

- 优点：subagent 只需记一条命令，调用面更简洁
- 缺点：① 新增一个"胶水脚本"重复封装已有三个独立脚本（`agate-frontmatter-check.py`/`check-routing.py`）的调用逻辑，违反"不发明新架构"的既有教训（LIMITATIONS/复盘 A2 类）② 需要额外维护一份"哪些文件触发哪些检查"的映射规则，与 `SCHEMAS` 表存在重复维护风险 ③ 改动面/维护面比候选 A 大，而效果目标完全相同（都是"写完立即跑校验"）
- 未选理由：候选 A 用既有模式（返回前自检）零架构新增即可达成同等效果

**选择**：候选 A。理由：复用既有"返回前自检"模式、不新增脚本、改动面最小、诚实标注"源码数"类检查的 git-add 依赖边界（不含糊宣称"完全独立于 git 状态"）。

---

## 3. 四字段（frontmatter 已声明，正文补充说明）

- `packages: [agate]`（frontmatter）：agate 协议本体单一版本单元，4 子项改动面均在此包内
- `domains: [backend]`（frontmatter）：纯协议/脚本/CI/测试改造，无 frontend、无 security 域，按 C8 映射表只需派 plan-eng-review（backend 域必派 + risk_level: high 硬规则叠加，去重后仍是 1 个 plan-eng-review）
- `ui_affected: false`（frontmatter）：无 UI/交互变化，不含「UI 设计」节
- `gate_commands`（P2 固化，后续阶段不可改，沿用 dispatch-context §「gate_commands 声明」原值，不新增 key——现有 pytest/ruff/consistency/count-tests 命令已能覆盖 4 子项新增的测试/脚本改动，无需专门新增 key）：

```yaml
gate_commands:
  P3: "pytest -v"
  P5: "python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_ruff: "~/.venvs/agate-dev/bin/ruff check agate/"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_timeout_seconds: 300
```

---

## 4. 完成标准（供 P3/P5 使用，逐条 BDD 转具体可观测判据）

| BDD | 完成判据（文件/函数/命令级） |
|-----|------|
| BDD-1 | `check-state-transition.py` 新增函数扫描 `task_dir` 下文件名精确匹配 `^P(\d+)-dispatch-context-(requirements-review\|plan-eng-review\|plan-design-review\|plan-ceo-review\|cso\|review\|design-review\|review-eng\|review-cso)-(retry\|rev)\d+\.md$`（C8 评审角色 token 枚举，P2 重试 #2 收紧，见 D6）的评审角色重试/复评 dispatch-context 文件，命中阶段 Pn + 对应 `retries[Pn]` 为空 → **stderr 输出高优 WARNING 但 exit 0（P2 重试 #2 由阻断下调，见 D1）**；单测覆盖：①存在该类文件+`retries[Pn]`为空（WARNING）②存在该类文件+`retries[Pn]`非空（无 WARNING）③无该类文件（无 WARNING）三分支全部断言通过；另需以下真实历史样本固化为回归用例（回应 P2-review.md 测试缺口①，仅靠合成 fixture 无法暴露"信号源在真实协议下不可观测"或"正则对真实数据误命中"这两类问题，必须锚定真实历史文件名）：正样本命中 TAG0016/17/19 三个历史任务的 `requirements-review`/`plan-eng-review`/`review`/`review-cso`/`review-eng` 真实文件名（`retry`/`rev` 两种后缀各至少 1 例）；**负样本（P2 重试 #2 新增，固定使用真实历史假阳性文件）**：`agate-workspace/archived/tasks/T001-v2.0-structured/P4-dispatch-context-implementer-review-fix-retry1.md`（角色 token 为 `implementer-review-fix`，整体不精确等于枚举中任一 token，必须不命中）+ `agate-workspace/tasks/TAG0016-protocol-hygiene/P7-dispatch-context-consistency-reviewer-retry1.md`（角色 token 为 `consistency-reviewer`，本轮枚举未收录该 token，必须不命中）两条均须断言"不得误命中"|
| BDD-2 | 同函数内子逻辑：`old_num>new_num` 且暂存版本 `retries[new_phase]` 长度未大于 HEAD 版本长度 → exit 1；单测覆盖 P5→P4 有/无新增 retries 记录两分支 |
| BDD-3 | 同函数内子逻辑：progress/dispatch-context 文件命中"空返回"/"重派"关键词 + `retries[Pn]` 为空 → stderr 输出高优 WARNING 但 exit 0（不阻断）；单测覆盖命中关键词+空retries（有WARNING）/命中关键词+有retries（无WARNING）两分支 |
| BDD-4 | 上述三处逻辑共用同一单测 fixture：无 rejected + 无回退 + 无关键词命中 + retries 为空/缺失 → exit 0 且 stderr 无 WARNING 文本 |
| BDD-5 | `check-gate.py` 新增 `_check_roadmap_done()`：构造 `.state.yaml task_id` 在 roadmap.md 有匹配行且状态非 done → `gate_p8()` return 1，stderr 含该 RM 编号；单测覆盖单条/多条关联 RM 部分非 done 场景 |
| BDD-6 | 同函数：`task_id` 在 roadmap.md 无匹配行 → 不提前 return，`gate_p8()` 继续既有流程最终 return 2；单测覆盖 |
| BDD-7 | `grep "RM-AG0032" agate-workspace/roadmap/roadmap.md | grep "done"` 非空（主 Agent P8 阶段人工操作后即满足，无需新脚本） |
| BDD-8 | 本 `P2-design.md` 文件本身即判据：①已知证据基线（§2.3 + `minimal_validation`，已确认根因）②环境敏感测试判定标准（§2.3）③集中清单文件位置与格式（§2.3，`agate/tests/ENV-SENSITIVE-TESTS.md`）④CI flaky 自动重跑机制触发条件（§2.3，`--reruns 1`）——四要素均已落盘，缺一即 FAIL；本文件四要素齐全，P4 只需落地代码/文件，无需重新设计 |
| BDD-9 | P6 阶段：连续触发 5 次 `protocol-tests.yml`（同一 commit 或等价改动内容，可用空 commit push 5 次或 workflow_dispatch）均 success；任一失败 → FAIL |
| BDD-10 | `agate/tests/ENV-SENSITIVE-TESTS.md` 文件存在且含 `test_bdd_7`/`test_bdd_25`/`test_bdd_14` 三条目（各含根因分类字段）；可加 1 条轻量单测断言文件存在 + 关键字覆盖，防止后续被误删 |
| BDD-11 | `dispatch-prompt.md` 含新增"P1/P2 声明写时自检"小节文本；轻量单测（或扩展 `check-protocol-consistency.py` 一条锚点）断言该文本存在 |
| BDD-12 | `agate-frontmatter-check.py` 每类 `errors.append` 消息含修复提示关键词（如"补"/"改用"/"应为"等具体指引）；单测覆盖每类错误消息断言含修复提示文本，不再是纯"格式错误"四字 |
| BDD-13 | 单测复现 TAG0019 三类历史用例（构造对应 `.md` 内容片段）：① `check-frontmatter.py` 对 coupling_checklist 流式声明/半角冒号两类均非 0 退出 ② `git add` 后 `check-routing.py` 对源码数 6>5 场景非 0 退出；三类全部覆盖，且验证既有 pre-commit hook 行为不变（回归防呆，同批用例过 commit 阶段不再产生"格式类"新拦截，因为内容已在写时被拦截未曾落盘）|

**SELF-GATE 处理纪律**（dispatch-context 第 8 条要求，非留白）：本任务改动面（`check-gate.py`/`check-state-transition.py`/`check-debt.py`/`state-transitions.md`/`state-machine.md`/`dispatch-protocol.md`/`WORKFLOW.md`/`phase-cards`/CI/测试）全部触发 SELF-GATE。批次 A/B/C/D/E **各自独立 commit** 时，每次 commit message 必须逐次显式含 `self-gate-review: <path>` 或 `self-gate-skip: <理由>`，按该次 commit 实际暂存的触发文件逐一声明，不得用"本任务已完成 self-gate"一次性笼统带过多个 commit。

---

## 5. files_to_read（P4 implementer 上下文地图，按批次分组）

```yaml
files_to_read:
  # batch A — RM-AG0042
  - path: agate/scripts/check-state-transition.py
    why: 新函数落点；复用 get_old_phase() 的 git-show-HEAD 范式
  - path: agate/scripts/agate-state-get.py
    why: retries_over 操作实现参照，理解现有 retries 读取方式
  - path: agate/scripts/agate-retreat-state.py
    why: 理解 write_retreat 已有的 retries 写入行为（回退标准路径）
  - path: agate/rules/state-transitions.md:56-107
    why: 回退规则/重试上限权威表述，本批需同步措辞
  - path: agate/state-machine.md:420-495
    why: retries 字段结构定义
  - path: agate/state-machine.md:587-624
    why: 「重试记录也要落盘」prose 规程，需补充"现有机械校验兜底"表述
  - path: agate/state-machine.md:668-714
    why: ⑩L1 阶段内再评审循环，evaluation rejected 场景的协议来源
  - path: agate/tests/unit/test_check_state_transition.py
    why: 现有测试模式，新增用例参照风格
  - path: agate/dispatch-protocol.md:1139-1156
    why: "P2 重试 #1 新增（BDD-1 事件源重新设计，D6）：「评审打回后的意见回流」节，新增强制措辞——重新派发评审角色时必须写新编号的 P{n}-dispatch-context-{role}-retryN.md/-revN.md，不得覆盖旧文件，把 BDD-1 依赖的命名惯例固化为协议明文"

  # batch B — RM-AG0043
  - path: agate/scripts/check-gate.py:1181-1257
    why: gate_p8() 新分支插入点
  - path: agate-workspace/roadmap/roadmap.md
    why: 表格格式/「关联任务」列取值规律，匹配算法依据
  - path: agate/scripts/agate-state-get.py
    why: task_id 读取操作复用

  # batch C — RM-AG0044
  - path: agate/scripts/check-debt.py:1-95
    why: _retreat_coverage() 全函数，L75 修复落点
  - path: agate/tests/unit/test_agate_debt_check.py:450-486
    why: test_bdd_14 现有实现，理解 fixture 构造方式
  - path: agate/LIMITATIONS.md:39-48
    why: 既有 P5 回归判定机制描述，理解与本次集中清单的边界差异
  - path: .github/workflows/protocol-tests.yml
    why: CI pytest job 配置，新增 pytest-rerunfailures 落点

  # batch D — RM-AG0045
  - path: agate/scripts/agate-frontmatter-check.py
    why: SCHEMAS 定义 + _check() 错误消息增强落点
  - path: agate/scripts/check-frontmatter.py
    why: 调用入口，理解错误输出格式如何透传
  - path: agate/scripts/check-routing.py:84-102
    why: _staged_source_count() 的 git-staged-diff 依赖边界
  - path: agate/assets/templates/dispatch-prompt.md:85-134
    why: 「返回前自检」节现状与新增子项插入点
  - path: agate/assets/templates/dispatch-prompt.md:280-296
    why: 「返回前自检（强制）」节现状，风格参照
```

---

## 6. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "Linux；/tmp 只读（pytest 需 --basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider）；ruff 0.16.4（~/.venvs/agate-dev/bin/ruff，对齐 CI）"
  isolation_check: "双工作区纪律——本任务只改 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0023），禁止改动主 checkout 与 ~/.agate；跑 gate 用 ~/.agate 稳定版；check-protocol-consistency.py 用 worktree 自己的脚本"
  ci_forensics: "RM-AG0044 根因验证已用 gh api（只读）拉取 PR #188 实际失败 CI job 日志，网络访问权限=full（P0-brief executor_env 已声明），无需额外权限申请"
  git_version_note: "本地开发环境 git 2.43.0，CI runner（ubuntu-latest, GitHub Actions）实测 git 2.55.0——RM-AG0044 修复后的单测无法在本地 100% 复现 CI 环境下的具体 short 长度差异（本地固定输出 7 位），但修复逻辑（动态调用 git rev-parse --short）本身与运行环境无关，正确性不依赖能否本地复现具体数值"
```

---

## 7. minimal_validation

```yaml
minimal_validation:
  # RM-AG0042/0043/0045：纯代码逻辑
  RM-AG0042_0043_0045:
    assumption: "纯代码逻辑，无外部系统依赖"
    method: "依赖内部函数：get_old_phase()/_run_state_get()（.state.yaml 读取范式）、
      retries_over 现有操作、roadmap.md 表格文本解析（纯字符串/正则处理）、
      dispatch-prompt.md 模板机制（既有'返回前自检'节的扩展，非新架构）。
      均为已读过源码验证过实现细节的确定性数据转换，不涉及浏览器/外部服务行为。"
    result: not_needed
    note: "唯一涉及外部工具调用的是 git subprocess（run_git 现有封装），行为已通过读代码 + 本地实跑验证确定"

  # RM-AG0044：已做真实最小验证，非声明豁免
  RM-AG0044:
    assumption: "check-debt.py._retreat_coverage() 的 full[:7] 固定 7 位前缀切片，与不同 git 版本下
      git rev-parse --short HEAD 的实际输出长度可能不一致，是 test_bdd_14 CI flaky 的根因"
    method: |
      1. 本地 git 2.43.0 三种场景实测（timeout 60s 内完成）：
         - 全新 init 仓库（1 commit）：`git rev-parse --short HEAD` → 7 位
         - 完整仓库（1250 commits）：→ 7 位
         - file:// 协议浅克隆（--depth 1，1 commit）：→ 7 位（`git rev-parse --is-shallow-repository` 确认为 true）
         结论：本地 git 2.43.0 环境下 auto-abbrev 存在 floor=7 的下限行为，三种规模场景均无法复现 mismatch，
         与 P1 §4.3「本地无法复现」的预判一致。
      2. 用 `gh api repos/randomgitsrc/agate/actions/runs/32645685798/attempts/1/jobs` 定位到
         PR #188 实际失败的 pytest(ubuntu-latest) job（id 97209482443，run_attempt 1，
         事件 pull_request，该 run 的最终 conclusion 因后续 rerun 而变为 success，
         但 attempt 1 的真实失败记录仍可查）。
      3. 用 `gh api .../jobs/97209482443/logs` 拉取完整日志，确认：
         - CI runner 实际 git 版本为 **2.55.0**（本地为 2.43.0，日志行 `git version 2.55.0`）
         - workflow 用 `actions/checkout@v4` + `fetch-depth: 0, fetch-tags: true`（全量克隆，
           排除"CI 用浅克隆导致 short 变短"这一假设分支）
         - 真实失败断言：`AssertionError: assert 'GATE DEBT WARNING' not in ...`，具体输出
           `GATE DEBT WARNING: retreat 提交 0674061（...）未登记为 source: retreat DEBT 条目`——
           `0674061` 即 check-debt.py 固定输出的 `full[:7]`（7 位），该值未命中 `covered` 集合
           （covered 集合内容由测试 fixture 用同一 CI 环境下 git 2.55.0 的
           `git rev-parse --short HEAD` 实际计算得出，与固定 7 位不一致）
      4. 尝试用 docker 容器复现 git 2.55.0 环境下的具体 short 长度数值（`docker run alpine:3.20`
         安装 git），因网络/执行环境限制在 90s 超时内未完成，未获得精确数值，但不影响根因结论——
         CI 真实失败日志已构成决定性证据链（runner 真实 git 版本差异 + workflow 全量克隆排除
         浅克隆假设 + 固定 7 位输出精确对应代码行为 + WARNING 确实触发）
    result: confirmed
    note: "根因已从 P1 阶段的'候选机制'升级为本阶段'已确认根因'（基于真实 CI 失败日志的 forensic
      证据，非本地猜测复现）。修复方向（§2.3 候选 A：改用动态 git rev-parse --short 调用）直接
      对症此根因。剩余不确定性仅是'CI 环境下具体的 short 长度数值是多少'（未获得，因 docker 复现
      超时），但该数值对修复方案的正确性无影响——动态调用天然适配任何长度。"
```

---

## 8. 批次设计说明（补充 dispatch_plan frontmatter）

5 批：A（RM-AG0042）/ B（RM-AG0043）/ C（RM-AG0044）/ D（RM-AG0045）/ E（RM-AG0032 历史补记，P8 阶段人工操作）。

- **A/B 可并行**：本设计已确认两批生产代码文件零重叠（`check-state-transition.py` vs `check-gate.py`），文档改动也不重叠（A 改 state-transitions.md/state-machine.md/dispatch-protocol.md/WORKFLOW.md，B 只改 roadmap.md 相关表述在 P1/P2 卡片层面，无需改上述 4 份协议文档）
- **C 建议尽早启动**：因 BDD-9「连续 5 次 CI 稳定」需要多次触发 GitHub Actions（wall-clock 耗时最高的验收锚），且与 A/B/D 文件零重叠，可与其他批次同时进行，不阻塞其他批次的 P4/P5
- **D 与 A/B/C 均无文件重叠**（`dispatch-prompt.md`/`agate-frontmatter-check.py` 独占）
- **E 是 P8 阶段动作，非 P4 代码实现批次**，可与任一批次并行准备（工作量近零），但实际落盘时机在 P8
- `parallel_limit: 5` 覆盖全部 5 批同时派发的场景（本设计判定批数 ≤ parallel_limit 合法）；主 Agent 可按实际并发能力选择部分并行/全部并行，不强制一次性拉满

**批次粒度自查**（派发编排机制任务粒度基准）：各批次产出文件数（代码改动 1-2 个 + 测试 1 个 + 文档 0-4 个）与输入文件数（`files_to_read` 各批 3-8 项）均在合理范围，未见单批过度膨胀。
