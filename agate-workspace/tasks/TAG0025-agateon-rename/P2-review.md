---
phase: P2
task_id: TAG0025
type: review
parent: P2-design.md
trace_id: TAG0025-P2-review-20260826
status: approved
created: '2026-08-26'
agent: plan-eng-review
---

# P2 评审 — plan-eng-review — TAG0025 Agateon 品牌改名执行 Phase 0-1

> 角色：plan-eng-review（工程经理，架构和执行锁定）。评审对象：P2-design.md（architect 产出，
> 2 候选方案 + 影响面梳理 + 26 条 gate_commands）。独立视角复核，不预设 architect 结论正确，
> 关键论证与实测发现均已本阶段独立重跑核实（见下）。

## 0. 四个重点核查项结论摘要

### 核查项 1 — 候选 A"致命问题"论证是否站得住：**成立，非借口**

核实路径：读 P0-brief.md `executor_env`（`platform: "dsh"` / `has_task_tool: true`，未声明
暂停/恢复能力）+ 通读 `agate/dispatch-protocol.md` 全部关于 subagent 生命周期的条款。结论：

- `agate/dispatch-protocol.md` L143-160「subagent 外部中断恢复（额度/超时/崩溃）」是协议里
  唯一一处描述"subagent 中途终止后如何处理"的机制，但其语境明确是**外部原因**（额度/超时/崩溃）
  导致的非自愿中断，恢复方式是"评估已落盘产出 → 复用/补做/重派"，**不是**"同一个运行中的
  subagent 实例暂停、等待外部输入、原地恢复执行"。
- L200 起的「标准派发流程」描述的是 fire-and-forget：主 Agent 派发 → subagent 独立运行至
  返回 → 主 Agent 校验。协议全文没有任何"暂停一个仍在运行的 subagent、注入确认后从原状态
  继续"的原语。
- 因此 P2-design.md L129-137 的论证——"`has_task_tool: true` 只说明能派发子任务，不等于能
  中途暂停恢复"——**是真实的能力空白，不是为了选 B 硬凑的借口**。architect 的措辞也克制
  （"没有实测证据"，未夸大为"确定不支持"），如实呈现了不确定性而非把假设包装成结论。

### 核查项 2 — `[SCOPE+]` 发现是否真实、处理是否得当：**发现属实；处理方式不完全够，需追加一条锁定要求**

- **独立重跑验证（本阶段实测，非采信 P2 自述）**：用 dispatch-context 给出的全仓命令 + P1 原始
  4 类豁免正则重跑，命中残留 **1 处**，精确复现 `docs/design-notes/design-rename-execution.md:35`
  ——与 P2-design.md 描述完全一致。再用 P2 `gate_commands.P5_bdd10_residual_scan` 声明的完整
  5 类豁免正则重跑，残留 **0 处**。逐类核对（archived/ 7 处、agate-workspace/tasks/ 60 处、
  agate-workspace/archived/ 8 处、边界文档 3 类共 7 处、design-rename-execution.md 1 处，
  总计 90 处 = 全部有归属，无遗漏无多算）。**SCOPE+ 发现是真实的，不是编造的。**
- **处理方式的缺口**：`agate/phase-cards/P1-requirements.md` L233-238「P1 基线保护」明确写
  "如需变更，**必须**标注 `[BASELINE_CHANGE: 理由]`"（非"建议"）。BDD-10 的 Given 排除清单
  当前只列 4 类，按字面判定会**永久**产生 1 处残留、与"排除后剩余命中数为 0"矛盾——这不是
  单纯"没改 P1 文本"的克制，而是 P1 文本本身描述的验收条件已经**不可达成**（除非隐式依赖
  P2/gate_commands 里一份 P1 文本没有的第 5 类）。P2 §0.1 末尾把这件事降级为"建议主 Agent
  视情况补"（非阻塞），这与"必须标注"的协议原文有落差。
- **判定**：不要求 architect 现在回头改 P2 设计（gate_commands 已经是正确、可复跑、已验证的
  版本，功能层面没问题），但**锁定为一条必须执行的后续动作**（见下「锁定决策」）：主 Agent
  在 P4 派发前，须在 P1-requirements.md BDD-10 的 Given 排除清单补第 5 类并标注
  `[BASELINE_CHANGE: P2 阶段实测发现 4 类豁免遗漏 design-rename-execution.md:35，导致 BDD-10
  验收条件永久不可达成，补第 5 类豁免]`，不能停留在"视情况"的软建议。这是流程合规缺口，
  非阻塞本次 P2 通过，但阻塞 P4 派发前的收尾。

### 核查项 3 — gate_commands 的 shell 命令语法/逻辑是否正确：**语法全部可执行；发现 1 处逻辑缺口（非阻塞，已有兜底但未显式声明）**

本阶段在 worktree 内只读实跑（未改动任何文件，未执行 `gh api`/`git remote set-url`/`git push`，
未接触主 checkout）以下不依赖改名已发生的 key：

| key | 实跑结果 | 语法/逻辑判定 |
|-----|---------|--------------|
| `P5_bdd1_readme_en` | exit 1（当前未含品牌声明，符合改名前红态）| 正确，`head -15 \| grep -F` 定位首屏 |
| `P5_bdd2_readme_zh` | exit 1（同上）| 正确；已核实 "Agateon" 不会因大小写误自匹配出 "agate" 子串（`A` 与 `a` 大小写不同，`grep -E` 默认区分大小写，无假阳性风险）|
| `P5_bdd3_unreleased_section` | exit 1（当前无 `[Unreleased]` 段）| 正确 |
| `P5_bdd3_tag0025_entry` | exit 1（当前 CHANGELOG 无 TAG0025 字样）| 语法正确；**逻辑弱点（非阻塞）**：只判定"文件内任意位置含 TAG0025"，未限定"必须在 `[Unreleased]` 段下"；本次实测当前 CHANGELOG.md 全文无 TAG0025 残留，暂无假阳性风险，但若未来该字符串因其他原因出现在别处（如误粘贴/引用其它任务），该 key 会误判 PASS。建议 P4/P5 执行时人工确认位置，不必现在改设计。|
| `P5_bdd4to8_new_url_present` | exit 1，`MISSING:install.sh`（当前未改名前红态）| 语法正确；**逻辑缺口（非阻塞，见下）**|
| `P5_bdd9_atomic_commit` | `FAIL: 批次未落在同一commit`（6 个核心文件各自最近一次改动的 commit SHA 互不相同——当前无 batch commit，属预期红态）| 正确，SHA 比对逻辑可靠 |
| `P5_bdd10_residual_scan` | `OK:0残留`（见核查项 2 的独立复现）| 正确，已验证 |
| CI workflow 声明核对 | `grep --include=*.yml --include=*.yaml` 命中 0，`.github/workflows/` 实测 2 个文件（docs-check.yml / protocol-tests.yml）| 与设计 §4/§0.2 描述完全一致 |

**逻辑缺口细节**：`P5_bdd4to8_new_url_present` 用 `grep -q randomgitsrc/agateon "$f"` 只验证
"新 URL 在文件内至少出现一次"，**不验证"旧 URL 在文件内已被完全清除"**。同时
`P5_bdd10_residual_scan` 的排除正则里显式包含了这 5 个核心文件本身（`install\.sh:` /
`README\.md:` / `README\.zh-CN\.md:` / `agate/scripts/agate-install\.py:` /
`agate/scripts/agate-changes\.py:`——这 5 条排除项不属于 P1 BDD-10 声明的 4 类豁免，也不属于
本阶段 SCOPE+ 新增的第 5 类，是 P2 自行追加、且未在"5 类豁免"的叙述文字里说明理由的排除项）。
两者叠加的后果：**没有任何一条 BDD 编号对应的 gate key，单独就能拦住"README.md 两处 URL 只改
一处"这种部分修复**（这正是 BDD-7/BDD-8 显式禁止的"不允许只改其中一行"）。已核实这个缺口
目前有兜底——P1 §3.4 SUGGEST 被 P2 采纳落地的回归测试
`agate/tests/regression/test_repo_url_no_stale_rename.py`（断言 5 个核心文件不含字面旧 URL）
会在 `gate_commands.P3` 与 `gate_commands.P5_other`（该 key 跑 `agate/tests/` 排除
`unit/`，天然覆盖 `regression/` 目录）两处被执行到，可以补上这个缺口。**但这一兜底关系目前
只存在于我这次独立推导中，P2-design.md 正文与 gate_commands 的"说明"注释块都没有显式写明
"BDD-7/8 的完整性验证依赖回归测试而非 bdd4to8 key 本身"**——建议在 gate_commands 的"说明"
块补一句，否则未来任何人（含 P4/P5/P6 执行者）读 gate_commands 时会误以为
`P5_bdd4to8_new_url_present` 已经是 BDD-7/8 的完整验证。判定为**测试缺口 + 非阻塞架构问题**，
不影响本次 approved（功能层面确有兜底，只是未显式声明）。

`P5_bdd12_301_status` / `P5_bdd12_301_location` / `P5_bdd13_ls_remote` / `P5_bdd14_search` /
`P5_bdd15_*` / `P5_bdd16_*` 依赖改名已实际发生，按角色隔离约束未执行（`P5_bdd14_search` 需要
`gh api`，`P5_bdd16_*` 会对主 checkout 执行 `git fetch`，均在本阶段"严禁执行"范围内），仅做
语法静态审查：curl/grep/git ls-remote/git remote -v 的选项与管道结构均无语法错误，与其对应的
BDD-12~16 语义匹配（301 状态码+Location 头、SHA 格式校验、仓库名精确匹配、remote -v 输出比对）。

### 核查项 4 — `minimal_validation` 是否如实：**基本如实；记录数与 dispatch-context 描述不一致（4 条非 5 条），已如实核对**

P2-design.md 实际的 `minimal_validation` 块含 **4 条**（非 dispatch-context 声称的 5 条——
dispatch-context 计数有误，非 P2-design.md 本身缺项；已按实际内容逐条核实，不影响本次判定）：

1. BDD-10 豁免验证：`refuted → confirmed`。**已在核查项 2 独立复现，与本阶段实测过程完全对应**，
   不是编造结论。
2. GitHub 301 重定向：`not_needed`，理由"改名前无可观察的中间态"——**真实技术限制**：旧仓库
   当前返回 200（未改名），重定向行为客观上无法在改名前被观察到，不是可以现在验证却偷懒不做。
3. GitHub `in:name` 搜索索引：`not_needed`，同理，索引更新本身依赖改名后的外部时序，当前
   无可验证前提。
4. worktree/主 checkout 共享 `.git/config`：`confirmed`，声明"非本阶段新验证，沿用
   env-rename-handoff.md 既有实测"。**本阶段独立重新只读验证**（`git config --show-origin
   --get remote.origin.url`，未做任何写操作）：worktree 内该命令返回
   `file:/home/kity/oclab/agate/.git/config https://github.com/randomgitsrc/agate.git`，
   证实 worktree 确实读取主 checkout 的 config 文件，佐证该结论成立、非凭空断言。

## 1. 候选方案权衡核实（对应 P2-design.md §1）

- 候选 A（改名放 P4 内部，subagent 暂停等待恢复）被否决的理由已在核查项 1 独立核实为真实风险，
  非稻草人。
- 候选 B（改名抽离，主 Agent 亲自执行）：核实其与 BDD-11（"执行方（主 Agent 或受派发的
  subagent）...必须先在当前会话内获得用户明确的在场放行确认"）的措辞完全兼容——BDD-11 本身
  就把"主 Agent"列为可能的执行方之一，候选 B 选择主 Agent 而非 subagent 执行，不违反 BDD-11
  语义，反而是对"确认"与"执行"避免跨 Agent 实例分离的更保守实现。
- "其余分歧点"（脚本化批量替换 vs 逐文件手改；是否采纳 P1 §3.4 SUGGEST）权衡理由自洽，脚本化
  选择与 BDD-9 批次原子性要求逻辑一致，采纳回归测试选择成本收益描述合理（且已在核查项 3 证实
  该测试实际承担了 gate_commands 结构性缺口的兜底作用，比 P2 正文里描述的"防未来回归"的
  单一动机更重要）。

## 2. 影响面梳理核实（对应 P2-design.md §0）

- **改什么**：逐行核对 §0.1 表格 7 处 URL 落点（install.sh:24、agate-install.py:55、
  agate-changes.py:116、README.md:5,29、README.zh-CN.md:5,29）与 P1 BDD-4~8 一一对应，
  行号与 P1-requirements.md 描述一致，未发现漏项/错位。
- **不改什么**：核实 `.github/workflows/*.yml` 0 命中的实测声明（本阶段独立复测，见核查项 3
  表格）；核实 Phase 2/3 裁剪范围与 P0-brief/P1 §6 裁剪说明一致，无越界声明。
- **风险在哪**：7 条风险各配缓解措施且均指向具体 gate_commands key 或 minimal_validation 条目，
  可复跑验证（非空泛陈述）；唯一需要补强的是"BDD-10 豁免清单遗漏"这条风险的缓解措施描述为
  "已用实测验证...gate_commands 已固化"，本阶段核实这个缓解措施本身成立，但未覆盖到"P1 基线
  文本本身也应同步更新"这层——已在核查项 2/锁定决策补齐。

## 3. gate_commands 覆盖的 BDD 编号核对

- BDD-1 ← `P5_bdd1_readme_en`；BDD-2 ← `P5_bdd2_readme_zh`；BDD-3 ← `P5_bdd3_unreleased_section`
  + `P5_bdd3_tag0025_entry`；BDD-4~8 ← `P5_bdd4to8_new_url_present`（+ 隐式依赖回归测试兜底
  完整性，见核查项 3）；BDD-9 ← `P5_bdd9_atomic_commit`；BDD-10 ← `P5_bdd10_residual_scan`；
  BDD-11 ← 不落 gate_commands（会话时序人工确认，设计已如实声明理由，符合"env_constraints 与
  gate_commands 边界不等价"的协议规则）；BDD-12 ← `P5_bdd12_301_status` +
  `P5_bdd12_301_location`；BDD-13 ← `P5_bdd13_ls_remote`；BDD-14 ← `P5_bdd14_search`；
  BDD-15 ← `P5_bdd15_remote_main` + `P5_bdd15_remote_worktree`；BDD-16 ←
  `P5_bdd16_fetch_main` + `P5_bdd16_fetch_worktree`。16 条 BDD 全部有对应 key 或明确豁免理由，
  无遗漏编号。

---

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

1. **P1 基线保护条款执行不到位**：`agate/phase-cards/P1-requirements.md` L233-238 对"需变更
   P1"的场景要求"必须标注 `[BASELINE_CHANGE: 理由]`"，P2-design.md 把 BDD-10 豁免清单遗漏
   降级为"建议主 Agent 视情况补"（非阻塞、软性）。SCOPE+ 发现的本质是 P1 BDD-10 的 Given 排除
   清单存在遗漏，导致该 BDD 按原文永久不可达成——这属于协议里"P4 发现 BDD 矛盾"的同类场景，
   理应走 `[BASELINE_CHANGE]` 硬性标注流程，而不是留一条可以被忽略的软建议。**要求**：主 Agent
   在派发 P4 之前，在 P1-requirements.md BDD-10 Given 排除清单补第 5 类并加
   `[BASELINE_CHANGE: 理由]` 标注（见「锁定决策」）。不影响本次 gate_commands 的正确性
   （已验证功能层面无误），不阻塞本次 approved。
2. **`P5_bdd4to8_new_url_present` 与 `P5_bdd10_residual_scan` 的排除正则叠加后产生的"BDD-7/8
   完整性验证"缺口未被显式记录**：见核查项 3 细节。当前有回归测试兜底（功能上不缺），但
   gate_commands 的"说明"注释块应补一句显式声明这层依赖关系，避免 P4/P5/P6 执行者误读
   `P5_bdd4to8_new_url_present` 为 BDD-7/8 的独立完整验证。建议 P4 implementer 落地回归测试时
   在测试文件顶部注释里说明"本测试同时承担 gate_commands.P5_bdd4to8 未覆盖的旧 URL 完全清除
   校验"，或由主 Agent 在派发 P4 时的 dispatch-context 里补充这条说明。不要求现在改
   gate_commands（已固化，且改了反而违反"P2 固化后 P4-P6 不能改"的协议纪律）。

## 测试缺口

1. `P5_bdd4to8_new_url_present` 只验证"新 URL 存在"，不验证"旧 URL 已清除"——单靠这一个 key
   无法拦截"README.md 两处 URL 只改一处"这类部分修复（BDD-7/BDD-8 显式禁止）。当前由 P1 §3.4
   SUGGEST 采纳落地的回归测试 `test_repo_url_no_stale_rename.py` 兜底（P3 与 P5_other 两处都会
   跑到），但这层依赖关系未被显式记录（见「架构问题（非阻塞）」第 2 条）。
2. `P5_bdd3_tag0025_entry` 只判定"文件内任意位置含 TAG0025 字符串"，未限定必须落在
   `## [Unreleased]` 段下。当前 CHANGELOG.md 全文实测无 TAG0025 残留，无现实风险，但严格来说
   该 key 不能排除"TAG0025 字样出现在错误位置也判 PASS"的边界情况。建议 P5 执行时人工抽查
   条目实际所在段落，不要求现在改 gate_commands。

## 锁定决策

1. **候选 B（改名从 P4 抽离，由主 Agent 本人在获得用户放行确认后直接执行）锁定为本任务
   不可逆改名操作的唯一执行路径**。implementer subagent 全程不接触 `gh api -X PATCH` /
   `git remote set-url`。理由已在核查项 1 独立核实：DSH 平台无实测证据支持"暂停一个运行中
   subagent 并原地恢复"，候选 A 的风险真实存在。
2. **P4 派发前必须完成的收尾动作**：主 Agent 在 P1-requirements.md BDD-10 的 Given 排除清单
   补第 5 类（`docs/design-notes/design-rename-execution.md`）并标注
   `[BASELINE_CHANGE: 理由]`——这是本次评审对 P1 基线保护协议条款的强制补正要求，不是可选项。
3. **gate_commands 26 条 key 按 P2-design.md 原文固化，不因本评审的非阻塞发现而改动**——发现
   的两处测试缺口均有既有兜底（回归测试）或现实风险极低（CHANGELOG 位置校验），处理方式是
   补充说明/人工抽查，不重开 P2 设计。
4. **P4 implementer 的 dispatch-context 须显式声明"改名调用不下放给 implementer subagent"**
   （P2 env_constraints.irreversible_op_confirmation 已提出此要求，本次评审确认该要求成立且
   必须落实，不能只停留在 P2 文本声明层面）。
