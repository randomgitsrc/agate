---
phase: P2
task_id: TAG0025
type: design
parent: P1-requirements.md
trace_id: TAG0025-P2-20260826
created: '2026-08-26'
status: draft
agent: architect
candidate_count: 2
packages:
- agate-brand-docs
- agate-installer-scripts
- agate-repo-admin
domains:
- docs
- cli
- ops
ui_affected: false
---

# P2 方案设计 — TAG0025 Agateon 品牌改名执行 Phase 0-1

> [PROD_NOT_TOUCHED] 本阶段仅读取 P0/P1/设计文档/交接单 + 在本 worktree 内对全仓文件做只读 grep
> 审计（含验证豁免清单是否真能让 BDD-10 残留扫描归零）；未修改任何文件、未执行任何
> `git`/`gh` 写操作、未接触主 checkout（`/home/kity/oclab/agate`）与 `~/.agate`，不涉及生产环境。

## 0. 影响面梳理（先于候选方案）

### 0.1 改什么（Modify）

逐文件列出改动点 + 关联 BDD，改动落点精确到行：

| 文件 | 具体改动 | 关联 BDD |
|------|---------|---------|
| `README.md` | 第 1 行标题下方新增一行品牌声明（含 "Agateon (formerly agate)"字样，首屏可见，不需滚动）；第 5 行 badge img src 的 `randomgitsrc/agate` → `randomgitsrc/agateon`；第 29 行 curl 安装入口同上 | BDD-1, BDD-7 |
| `README.zh-CN.md` | 同上结构，中文品牌声明句（含 "Agateon" 与 "agate" 两词）；第 5/29 行同上替换 | BDD-2, BDD-8 |
| `CHANGELOG.md` | 在 `## [0.63.0]` 段之上新增 `## [Unreleased]` 段，段下新增一条描述 TAG0025 品牌改名 Phase 0-1 的条目 | BDD-3 |
| `install.sh` | 第 24 行 `git clone https://github.com/randomgitsrc/agate.git` → `.../agateon.git` | BDD-4 |
| `agate/scripts/agate-install.py` | 第 55 行 `DEFAULT_REPO_URL = "https://github.com/randomgitsrc/agate"` → `.../agateon` | BDD-5 |
| `agate/scripts/agate-changes.py` | 第 116 行 `"https://github.com/randomgitsrc/agate.git"` → `.../agateon.git` | BDD-6 |
| GitHub 仓库本体（`randomgitsrc/agate` → `randomgitsrc/agateon`，`gh api -X PATCH`） | 仓库改名，不可逆外部操作 | BDD-11, BDD-12, BDD-13, BDD-14 |
| 本机 git remote（主 checkout `/home/kity/oclab/agate`，worktree 自动跟随） | `git remote set-url origin <新 URL>` | BDD-15, BDD-16 |
| `agate/tests/regression/`（新增 1 个测试文件，采纳 P1 §3.4 SUGGEST，见 §2.3） | 断言 5 个 Phase1 核心文件不含字面 `randomgitsrc/agate`（word-boundary，排除 `agateon`） | 呼应 BDD-4~8，防未来回归 |

**批次原子性执行落点（呼应 BDD-9，约束 4）**：上表前 6 行（README×2 品牌声明 + badge/安装入口、
CHANGELOG、install.sh、agate-install.py、agate-changes.py）**在同一次工作树编辑动作内一次性改完
→ 一次 `git add <这 5 个文件>` → 一次 `git commit`**，不允许边改边分批提交。README.md /
README.zh-CN.md 本身同时承载 Phase 0（品牌声明）与 Phase 1（badge/安装入口）两类编辑点——把它们
拆成两次提交意味着对同一文件做两轮编辑，既不必要也不被 BDD-9 要求（BDD-9 只要求 7 处 URL 落在
同一 commit，不禁止连带 Phase 0 品牌声明与 CHANGELOG 条目一起提交），故本设计把 Phase 0 + Phase 1
核心 7 处 URL + CHANGELOG 条目合并为**同一个 commit**。GitHub 仓库改名、remote 迁移、新增回归
测试是各自独立的后续步骤，不与这次文件提交混在一起（各自的执行顺序见候选方案 §2）。

### 0.2 不改什么（Not Modify）

| 范围 | 理由 |
|------|------|
| `agate/` 目录名、`agate-workspace/` 目录名、`~/.agate` 软链、`AGATE_*` 环境变量、`agate-*.py` 文件名、`agate_common` 内容 | P0-brief/P1 §1 三层解耦原则：内部命名空间永久保留，本任务不触碰（dispatch-context 约束 3 硬性禁动） |
| `check-protocol-consistency.py` 及其余 19 个 `check-*.py` gate 脚本 | 设计 §6 已事实核实：现有一致性 gate 不校验品牌词，改名不触发其判定逻辑变化，无需改动 |
| `.github/workflows/*.yml`（CI workflow） | 本次全仓 grep（`--include=*.yml --include=*.yaml`）命中数为 0——CI workflow 未硬编码 `randomgitsrc/agate` 仓库路径，无需改动（与设计 §4"CI workflow 2 个｜job 名/注释换，路径不动"一致，且本次实测连 job 名/注释都未命中，无需动） |
| Phase 2 范围：`agateon-*` CLI 别名、`agate/` 协议正文品牌 prose 统一、一次性 brand-check 工具、CHECK 10 脚本名白名单扩展 | P0-brief/P1 §6 已显式裁剪，设计 §5.2/§5.3 明确划入 Phase 2（v1.0 窗口），本任务范围锁定 Phase 0-1 |
| Phase 3：`agateon-portal` 门户新仓 | 设计 §5.5 明确独立立项时机，当前无立项计划 |
| `docs/design-notes/design-rename-execution.md`、`docs/design-notes/agateon-trademark-research.md`、`docs/superpowers/specs/2026-08-15-docs-suite-review.md`、`HANDOFF-TAG0025.md` 中的历史性 `randomgitsrc/agate` 引用 | 均为决策记录/审计快照/任务专属交接单的历史真实性载体，改写会扭曲记录的时间语境；处理方式是**扩大 BDD-10 残留扫描的豁免清单**而非编辑这些文件——详见 §1「[SCOPE+] 发现」 |
| `archived/**`、`agate-workspace/tasks/**`、`agate-workspace/archived/**` 下全部 `randomgitsrc/agate` 引用 | 设计 §5.3 归档豁免层，P1 已固化为 BDD-10 排除清单，本阶段不重判 |
| 用户侧协同项（商标申请、PyPI/npm/crates.io 占位、org 迁移） | P0-brief known_risks 已列为用户侧人工协同，不计本任务交付 |

### 0.3 风险在哪（Risk）

| 风险 | 缓解措施 |
|------|---------|
| 批次原子性被破坏（README 改一半就提交，中间态部分入口指向新仓部分指向旧仓） | §0.1 已固化"同一次编辑动作→一次 add→一次 commit"的执行顺序；gate_commands 声明 `P5_bdd9_atomic_commit`，用 `git log -1 --format=%H -- <file>` 逐文件比对 SHA 是否一致，可复跑验证 |
| 不可逆改名操作在未获得用户在场放行确认的情况下被 subagent 误执行 | 本 P2 的核心决策点——见候选方案 §2，选定方案把执行责任收归主 Agent 本人，不依赖"subagent 停下等待恢复"这一未经平台能力验证的假设 |
| BDD-10 残留扫描的豁免清单不完整，导致验收锚"全仓无残留"永远无法为 PASS（本阶段实测发现的真实缺口） | 见下方「[SCOPE+] 发现」——已用实测 grep 验证补齐第 5 类豁免后残留数=0，方案已把修正后的 5 类豁免固化进 `gate_commands.P5_bdd10_residual_scan` |
| remote 迁移的"主 checkout 一次 set-url，worktree 自动跟随"是基于 `.git/config` 共享机制的推断，若未来该 worktree 被 `git worktree repair` 或路径迁移，共享关系可能失效 | env-rename-handoff.md 已实测确认当前共享关系成立；gate_commands 声明 `P5_bdd15_remote_worktree` + `P5_bdd16_fetch_worktree` 做**验证性抽查**而非仅信任机制（呼应 P1 隐含需求 5），失败则说明假设不成立，需要现场诊断而非静默跳过 |
| CI 徽章/actions 断链（README badge img src 若遗漏未同批改） | badge 与安装入口已在同一改动批次内处理（§0.1），`P5_bdd4to8_new_url_present` 覆盖 badge 行 |
| GitHub 搜索索引更新有延迟，`P5_bdd14_search` gate 命令执行时索引可能尚未同步，出现假阴性 | BDD-14 Given 本身已限定"且 GitHub 搜索索引已更新"，非本任务可控的外部时序——gate 命令失败时先按"索引延迟"复跑而非直接判方案/实现有误，minimal_validation 节已如实声明这一点不可预先验证 |
| 新增回归测试（regression 目录 +1）导致 `count-tests.sh` 基线数字从 1293 漂移到 1294 | 已在 gate_commands 说明中显式声明新基线预期为 1294（而非误判为"用例数漂移=坏事"），P5/P8 阶段核对时按新基线判断 |

### [SCOPE+] 发现：BDD-10 豁免清单遗漏第 5 类边界文档

**发现**：本阶段用 dispatch-context 给出的全仓 grep 命令重新实测（而非采信 P1-review 的"已验证残留
数=0"结论），发现 `docs/design-notes/design-rename-execution.md:35`（本任务的执行地基设计文档自身）
含一处字面 `randomgitsrc/agate` 引用：

```
- **主仓**：`randomgitsrc/agate` → `randomgitsrc/agateon`。原 URL 301 自动跳转；...
```

这是该文档 §3.1 描述改名决策本身的"前 → 后"记号，性质与 P1 已排除的 3 类边界案例（商标调研决策
记录 / 历史评审快照 / 本任务交接单）完全同源——都是"记录决策/事实发生时刻的历史性引用"，不是
需要被替换的活跃品牌层引用。但 P1 BDD-10 的 4 类豁免清单未覆盖它，若 gate_commands 按 P1 原始
4 类豁免清单实现，`P5_bdd10_residual_scan` 会**永远命中 1 处残留、无法归零**，与 BDD-10"排除后
剩余命中数为 0"的验收目标矛盾。

**必须做的理由**：不把这处遗漏补齐豁免清单，BDD-10 在 P6 阶段将永久性 FAIL，且不是实现错误，
是需求裁决遗漏——不应该等到 P6 才发现。

**处理方式**：在 §0.1/gate_commands 中把 `docs/design-notes/design-rename-execution.md` 追加为
第 5 类豁免（"设计地基文档描述改名决策本身的历史性记号"），**不编辑该文档**（它已三轮评审通过
入 main，属冻结的决策记录，编辑它反而会造成"当时设计时到底叫不叫 agateon"的时间语境混乱，与
排除商标调研文档的理由完全一致）。已用实测验证：5 类豁免（P1 原 4 类 + 本项）应用后，全仓残留
命中数 = 0（见「minimal_validation」）。

**影响**：无需新增 BDD 编号（这不是新的验收要求，是让既有 BDD-10 的判定条件可达成的必要修正），
`packages`/`domains` 不变。建议主 Agent 视情况在 P1-requirements.md BDD-10 的 Given 排除清单里
补第 5 类（非阻塞，gate_commands 已经按修正后的清单实现，不依赖 P1 文本先改）。

## 1. 候选方案（不可逆改名操作的执行位置与放行确认机制）

**关键决策点**（dispatch-context 约束 1）：GitHub 仓库改名（`gh api -X PATCH repos/randomgitsrc/agate
-f name=agateon`）放在哪个阶段/哪一步执行，以什么具体机制获得"用户在场放行确认"（BDD-11）。

### 候选 A：改名作为 P4 implementer 内部的一步，subagent 停下汇报后由主 Agent 恢复其执行

**流程**：
1. P4 implementer 一个批次内完成 §0.1 前 6 行的文件改动 → 单次 commit（满足 BDD-9）。
2. implementer 准备发起 `gh api -X PATCH ...` 前，停下向主 Agent 报告
   `[NEED_USER_CONFIRM: 即将执行不可逆改名 randomgitsrc/agate → randomgitsrc/agateon，请确认放行]`，
   implementer 子任务本身**暂停**、不退出。
3. 主 Agent 把确认请求转达给会话中的人类用户，获得明确放行后，把确认结果传回给**同一个**
   implementer 子任务实例（恢复其执行，而非重新派发一个新 subagent）。
4. implementer 收到确认后执行改名调用，随即在同一子任务内跑 BDD-12~14 验收锚 + remote 迁移
   （BDD-15/16）。

**优点**：全流程收敛在一个 P4 批次内，implementer 上下文连续，不需要额外拆出一次独立的主 Agent
直接操作步骤，编排结构最简单。

**风险（本方案的致命问题）**：这个流程要求"派发平台支持暂停一个已运行的 subagent、等待外部输入后
再恢复其原会话继续执行"这一能力。本任务 `executor_env.platform` 是 `dsh`（DeepSeek Harness Web
GUI），P0-brief/HANDOFF 均未给出"DSH 的 task 工具是否支持暂停并恢复同一 subagent 实例"的实测证据
——`has_task_tool: true` 只说明能派发子任务，不等于能中途暂停恢复。如果该能力实际不支持，"停下
汇报"在这类平台上唯一可能的真实行为是 subagent 直接把改名调用当成任务的一部分继续执行下去（因为
它没有真正意义上的"暂停点"可用），"停下等待"只是 prompt 层面的指令，没有任何机制强制阻止 subagent
在没收到确认前就调用 `gh api`。这正是 dispatch-context 警告的"选错了要么在 P4 卡住要么造成事故"
中的"造成事故"分支——把一次不可逆的外部操作的执行时机，托付给一个无法被验证具备"暂停能力"的
执行环境。

### 候选 B：改名从 P4 常规批次中抽离，由主 Agent 本人在确认后直接执行（推荐）

**流程**：
1. **P4 批次 1**（派发给 implementer subagent）：只做 §0.1 前 6 行的纯文件层改动（README 品牌
   声明+badge/安装入口、README.zh-CN.md 同上、CHANGELOG [Unreleased] 段、install.sh、
   agate-install.py、agate-changes.py）→ 单次 commit（BDD-9）。implementer **不触碰**
   `gh api`/`git remote set-url`，批次内跑常规回归（`gate_commands.P5` 系列）确认全绿后返回。
2. **确认与执行环节**（不派发 subagent，由主 Agent 在当前会话内亲自执行，属"P4 常规实现批次
   之外的单独确认步骤"）：主 Agent 在会话中向用户发起明确的放行请求（内容包含仓库名、改名方向、
   不可逆性提示），拿到用户明确同意后，**由主 Agent 本人**运行
   `gh api -X PATCH repos/randomgitsrc/agate -f name=agateon`，随即立刻自查 BDD-12/13
   （curl 301 + git ls-remote）。
3. **P4 批次 2**（改名确认成功后再派发给 implementer subagent）：`git remote set-url` 主 checkout
   迁移 + worktree 验证性 fetch（BDD-15/16）+ 补跑 BDD-14（GitHub 搜索）+ 把结果记入
   env-rename-handoff.md §六版本记录。

**优点**：
- 把"用户在场"和"执行改名调用"锁定在**同一个主体、同一个会话轮次**——主 Agent 本身就是与用户
  直接对话的那个 Agent，获得确认和执行调用之间不存在"转达 → 恢复另一个 Agent 执行"的中间环节，
  没有平台能力假设，在任何 `has_task_tool: true` 的平台上都成立（不依赖"暂停 subagent 并恢复"
  这一未经验证的能力）。
- implementer subagent 全程不接触不可逆操作，"subagent 能不能被信任执行不可逆操作"这个问题
  被直接消解——不是靠信任 subagent 会乖乖停下，而是压根不把这个权限交给它。
- 与 P0-brief known_risks"① 权限核实 ② 用户在场确认放行……二者是并列的两个不可逆操作前置
  条件，缺一不可"的表述精确对应：①已由 P1 dispatch-context 客观查证信息 A 核实（`gh` admin
  权限），②由本方案在执行改名调用的**同一时刻**由主 Agent 亲自确认，不存在"确认"与"执行"
  分离到不同 Agent 实例的时间差。

**代价**：
- P4 拆成 2 个批次 + 1 个非 subagent 的人工确认环节，编排步骤比候选 A 多；批次 2 必须等批次 1
  commit 完成、且改名已成功执行后才能开始（有先后依赖，不能并行）。
- 主 Agent 亲自跑一条 `gh api` 命令，形式上是"主 Agent 亲自动手"，但这是一次幂等性极低、
  影响面清晰的单条运维命令（不是写代码/改协议逻辑），不违反"单个编排 Agent 从不亲自写代码"
  的精神（那条原则针对的是代码实现，不是不可逆外部运维操作的执行主体归属判断）。

**其余分歧点权衡（不构成独立候选，作为 B 的子决策一并说明）**：

- **7 处 URL 更新：脚本化批量替换 vs 逐文件手改**——选**脚本化**（一个一次性 Python/sed 脚本，
  按 §0.1 表格逐文件逐行做精确字符串替换，不做正则宽泛匹配），理由：7 处分布在 5 个文件、
  替换目标字符串完全一致（`randomgitsrc/agate` → `randomgitsrc/agateon`），脚本化能保证"一次
  运行改完全部 7 处"与批次原子性的执行顺序天然吻合，且比逐文件手改更不容易漏改一处（BDD-9 的
  风险点）；脚本本身不必保留（用完即弃的一次性工具，不同于设计 §6 否决的"brand-check 常驻
  gate"）。
- **是否采纳 P1 §3.4 SUGGEST 的轻量回归测试**——**采纳**，落地为新增 1 个 pytest 测试文件
  `agate/tests/regression/test_repo_url_no_stale_rename.py`（文件名由 P3/P4 最终确定），断言
  §0.1 表中 5 个 Phase1 核心文件（install.sh / agate-install.py / agate-changes.py / README.md
  / README.zh-CN.md）不含字面 `randomgitsrc/agate\b`（word-boundary，天然排除 `agateon`）。
  理由：范围窄（只测这 5 个文件，不做全仓品牌词扫描，不与设计 §6"不新增硬性品牌 gate"决策冲突）、
  成本低（~15 行）、收益是永久性的（防止未来贡献者从旧 issue/旧文档复制粘贴安装说明时把旧 URL
  带回来，一次性 check 脚本做不到"长期常驻"这一点）。**副作用**：`count-tests.sh` 基线从 1293
  变为 1294（+1），已在 gate_commands 说明中显式声明，避免被误判为"用例数漂移"。

### 选择理由：采用候选 B

核心理由是 dispatch-context 反复强调的那句话——"选错了要么在 P4 卡住要么造成事故"。候选 A 的
"卡住"或"事故"二选一恰好取决于一个本任务当前**没有实测证据**的平台能力（DSH 是否支持暂停/恢复
subagent）；候选 B 不依赖这个假设，用"不可逆操作的执行主体固定为主 Agent 本人、与用户确认发生
在同一会话轮次"这一更弱、更普适的机制达成同样的放行保障，代价只是多一次批次拆分的编排开销，
这个代价相对于"平台能力假设不成立时不可逆操作被误执行"的后果是不对等的，故选候选 B。

## 2. 实现完成的标志

- 16 条 BDD 全部可判定为 PASS（含改名后验收锚 4 条与 remote 迁移 2 条）
- §0.1 前 6 行文件改动落在同一个 commit（`git log -1 --format=%H` 逐文件比对一致）
- 仓库已改名为 `randomgitsrc/agateon`，本机主 checkout 与 worktree 的 `git remote -v` 均已更新
  并各自 `git fetch` 验证成功
- 全仓残留扫描（5 类豁免后）命中数为 0
- 新增回归测试落地且通过；`count-tests.sh` 报告数为 1294
- 回归底线维持：pytest 全绿（unit 1160+2 skipped + 其余 132）+ consistency 0 ERROR
  （`--strict-errors-only`）+ shellcheck 0 error
- env-rename-handoff.md §六版本记录已补填改名完成时间戳

## 3. files_to_read（P4 implementer 实现导航）

```yaml
files_to_read:
  - path: install.sh:20-30
    why: BDD-4 落点，第 24 行硬编码仓库 URL，克隆入口
  - path: agate/scripts/agate-install.py:50-58
    why: BDD-5 落点，第 55 行 DEFAULT_REPO_URL 常量定义
  - path: agate/scripts/agate-changes.py:110-120
    why: BDD-6 落点，第 116 行更新提示文案内嵌 URL
  - path: README.md:1-35
    why: BDD-1/BDD-7 落点，首屏品牌声明插入位置 + 第 5 行 badge + 第 29 行安装入口
  - path: README.zh-CN.md:1-35
    why: BDD-2/BDD-8 落点，中文镜像同结构
  - path: CHANGELOG.md:1-20
    why: BDD-3 落点，[Unreleased] 段建立位置（[0.63.0] 段之上）
  - path: agate-workspace/tasks/TAG0025-agateon-rename/env-rename-handoff.md
    why: BDD-11/15/16 的执行程序权威源——改名执行窗口纪律（§四）、remote 迁移与验证性抽查的
         具体命令、§六版本记录待补填位置；候选 B 的 P4 批次 2 直接照此文件的 §四清单执行
```

## 4. env_constraints

```yaml
env_constraints:
  debug_env: "继承 P0-brief：python3 -m pytest agate/tests/{unit,regression,integration}/ +
              test_sanity.py + scripts/ 分片跑（每片外层 timeout）；
              python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；
              gate/hook 用 ~/.agate 稳定版；consistency 必须用 worktree 自己的"
  isolation_check: "本 worktree 与主 checkout 共享同一 .git/config（env-rename-handoff.md 已
                    实测确认）——remote 迁移只在主 checkout 执行一次，P5 用
                    P5_bdd15_remote_worktree / P5_bdd16_fetch_worktree 做验证性抽查而非仅信任
                    机制成立"
  irreversible_op_confirmation: "候选 B 已选定：GitHub 仓库改名调用（gh api -X PATCH）不派发给
                    subagent，由主 Agent 在获得用户当次会话内明确放行确认后亲自执行；此约束
                    无法落成 gate_commands（不是可复跑的文件/系统状态判定，是会话时序内的
                    人工确认动作）——强制力落在 P4 阶段的执行分工本身（P4 批次 1/2 之间插入
                    非 subagent 的人工确认环节，见候选方案 §1）+ P4 阶段卡片/dispatch-context
                    须显式声明'改名调用不下放给 implementer subagent'这条编排指令，不能只写
                    进本字段就当作已生效"
  new_baseline_after_regression_test: "采纳 P1 §3.4 SUGGEST 后 count-tests.sh 基线从 1293 变为
                    1294（+1 新增 agate/tests/regression/test_repo_url_no_stale_rename.py），
                    P5/P8 核对用例数时按 1294 判断，不是漂移"
```

## 5. minimal_validation

本任务不是纯代码逻辑——依赖 GitHub 的 301 重定向真实行为、`gh api` 改名调用的真实效果、
GitHub 搜索索引的真实更新时序，这三类都是外部系统行为。逐项如实声明：

```yaml
minimal_validation:
  - assumption: "P1-review 声明的 BDD-10 残留扫描'4 类豁免应用后命中数=0'完全成立，可直接照抄
                 进 gate_commands"
    method: "本阶段重新实跑 dispatch-context 给出的全仓 grep 命令（不采信 P1-review 的自述结论），
             逐条比对 4 类豁免"
    result: "refuted"
    note: "发现 docs/design-notes/design-rename-execution.md:35 未被覆盖，残留数=1（非 0）。
           补第 5 类豁免（该文件）后重跑同一命令，残留数=0，已 confirmed。详见正文
           「[SCOPE+] 发现」，gate_commands.P5_bdd10_residual_scan 已按修正后的 5 类豁免实现。
           这是本阶段实际执行的最小验证，且验证结果与最初假设不符——不是走过场。"
  - assumption: "GitHub 仓库改名后旧 URL 返回 301 且 Location 指向新仓"
    method: "无法预先验证——重定向行为只有在改名真正发生之后才能被观察到（改名前旧仓库正常
             200 响应，不存在可供验证的中间状态），不像'某 API 返回什么 MIME 类型'那样可以
             现在就 curl 一下核实。"
    result: "not_needed（不是不需要验证，是当前阶段不具备可验证的前提条件）"
    note: "替代的风险缓解方式：改名后立即跑 gate_commands.P5_bdd12_301 系列验收锚；若 301 未
           按预期出现，属 P0-brief known_risks 已声明的已知风险（'301 兜底存在但不可依赖'），
           不阻断任务推进，但需要主 Agent 现场停下诊断（是否改名未生效/GitHub 侧异常），不是
           静默跳过。GitHub 官方文档承诺仓库改名后旧路径 301 到新路径，这是本方案敢于把验收
           锚建立在此行为上的依据，但'官方承诺'不等于'本次已实测'，二者不能混同。"
  - assumption: "GitHub in:name 搜索能在改名后被本任务的验收窗口内观察到 agateon 首屏命中"
    method: "同上，无法预先验证（索引更新本身有 GitHub 侧不可控延迟）；BDD-14 的 Given 子句已
             显式用'且 GitHub 搜索索引已更新'限定前提，不是本任务验收锚必须在改名后立刻通过
             的硬性时限"
    result: "not_needed"
    note: "gate_commands.P5_bdd14_search 失败时的正确动作是按'索引延迟'复跑观察，不是判定
           实现有误"
  - assumption: "本 worktree 与主 checkout 共享同一 .git/config，主 checkout 执行一次
                 set-url 后 worktree 无需重复操作"
    method: "读代码/读交接单验证——非本阶段新验证，env-rename-handoff.md 已实测确认（worktree
             的 git config --show-origin 指向主仓文件），P1 dispatch-context 客观查证信息 B
             同源确认，本阶段直接引用不重复实测（dispatch-context objective_info 已声明
             '本阶段无需重新核实'）"
    result: "confirmed"
    note: "沿用既有验证，非本阶段新增动作"
```

## gate_commands

> 每条 key 独立、不用 `&&` 拼接。BDD-11（用户在场放行确认）不出现在下表——它是会话时序内的
> 人工确认动作，不是可复跑的文件/系统状态判定，强制力落在候选方案 §1 选定的执行分工本身
> （见 env_constraints.irreversible_op_confirmation），不是 gate_commands 能表达的东西。
> 下方 `gate_commands:` 块由 `agate-md-field-set-gate-commands.py` 写入（未手写），写入后紧
> 跟在本段之后。

**说明**（不重复写进上面每条 key，集中在此）：
- `P5_bdd12_*`/`P5_bdd13_*`/`P5_bdd14_*`/`P5_bdd15_*`/`P5_bdd16_*` 只能在候选 B 的"确认与执行
  环节"（改名已真实执行）之后运行，运行时机晚于 `P5_bdd4to8`/`P5_bdd9`/`P5_bdd10`（这几条只要
  文件层改动完成即可运行，不依赖改名已发生）。
- `P5_count_tests` 期望输出数为 1294（1293 基线 + 1 条新增回归测试，见 env_constraints）。
- `P5_bdd14_search` 若因索引延迟失败，按 minimal_validation declared 的方式复跑，不直接判定
  失败。
gate_commands:
  P3: "python3 -m pytest agate/tests/regression/ -v"
  P3_formatter: "pytest.sh"
  P5_unit: "python3 -m pytest agate/tests/unit/ -q --tb=no"
  P5_unit_formatter: "pytest.sh"
  P5_unit_timeout_seconds: 180
  P5_other: "python3 -m pytest agate/tests/ --ignore=agate/tests/unit -q --tb=no"
  P5_other_formatter: "pytest.sh"
  P5_other_timeout_seconds: 120
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh install.sh"
  P5_count_tests: "bash agate/tests/scripts/count-tests.sh"
  P5_bdd1_readme_en: "head -15 README.md | grep -F 'Agateon (formerly agate)'"
  P5_bdd2_readme_zh: "head -15 README.zh-CN.md | grep -E 'Agateon.*agate|agate.*Agateon'"
  P5_bdd3_unreleased_section: "grep -n '^## \\[Unreleased\\]' CHANGELOG.md"
  P5_bdd3_tag0025_entry: "grep -n TAG0025 CHANGELOG.md"
  P5_bdd4to8_new_url_present: "for f in install.sh agate/scripts/agate-install.py agate/scripts/agate-changes.py README.md README.zh-CN.md; do grep -q randomgitsrc/agateon \"$f\" || { echo \"MISSING:$f\"; exit 1; }; done; echo OK"
  P5_bdd9_atomic_commit: "sha0=$(git log -1 --format=%H -- install.sh); ok=1; for f in agate/scripts/agate-install.py agate/scripts/agate-changes.py README.md README.zh-CN.md CHANGELOG.md; do s=$(git log -1 --format=%H -- \"$f\"); [ \"$s\" = \"$sha0\" ] || ok=0; done; [ \"$ok\" = 1 ] && echo \"OK:$sha0\" || { echo \"FAIL: 批次未落在同一commit\"; exit 1; }"
  P5_bdd10_residual_scan: "out=$(grep -rn 'randomgitsrc/agate\\b' --include=*.md --include=*.py --include=*.sh --include=*.yml --include=*.yaml . --exclude-dir=.git --exclude-dir=.worktrees | grep -vE '^(\\./)?(archived/|agate-workspace/(tasks|archived)/|install\\.sh:|README\\.md:|README\\.zh-CN\\.md:|agate/scripts/agate-install\\.py:|agate/scripts/agate-changes\\.py:|docs/design-notes/agateon-trademark-research\\.md:|docs/superpowers/specs/2026-08-15-docs-suite-review\\.md:|HANDOFF-TAG0025\\.md:|docs/design-notes/design-rename-execution\\.md:)'); [ -z \"$out\" ] && echo 'OK:0残留' || { echo \"$out\"; exit 1; }"
  P5_bdd12_301_status: "curl -sI https://github.com/randomgitsrc/agate | grep -Eq '^HTTP/[0-9.]+ 301'"
  P5_bdd12_301_location: "curl -sI https://github.com/randomgitsrc/agate | grep -qi '^location:.*randomgitsrc/agateon'"
  P5_bdd13_ls_remote: "timeout 30 git ls-remote https://github.com/randomgitsrc/agateon.git HEAD | grep -qE '^[0-9a-f]{40}[[:space:]]+HEAD'"
  P5_bdd14_search: "gh api -X GET search/repositories -f q='agateon in:name' --jq '.items[].full_name' | grep -qx randomgitsrc/agateon"
  P5_bdd15_remote_main: "git -C /home/kity/oclab/agate remote -v | grep -q randomgitsrc/agateon"
  P5_bdd15_remote_worktree: "git -C /home/kity/oclab/agate/.worktrees/agate-TAG0025 remote -v | grep -q randomgitsrc/agateon"
  P5_bdd16_fetch_main: "git -C /home/kity/oclab/agate fetch"
  P5_bdd16_fetch_worktree: "git -C /home/kity/oclab/agate/.worktrees/agate-TAG0025 fetch"
