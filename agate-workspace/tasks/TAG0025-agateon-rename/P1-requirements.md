---
agent: analyst
phase: P1
task_id: TAG0025
type: problems
parent: P0-brief.md
trace_id: TAG0025-P1-20260826
status: draft
created: '2026-08-26'
risk_level: medium
phases:
- P1
- P2
- P3
- P4
- P5
- P6
- P7
- P8
packages:
- agate-brand-docs
- agate-installer-scripts
- agate-repo-admin
domains:
- docs
- cli
- ops
---

# P1 — 需求基线：TAG0025 Agateon 品牌改名执行 Phase 0-1（RM-AG0035 剩余工作②）

## 0. P0-brief 时效性质疑

已核对 P0-brief 时效性，无漂移。核对依据：立项与本次 P1 执行同一天（2026-08-26）；P0-brief 引用的
三项前置——`design-rename-execution.md`（2026-08-25 三轮评审通过入 main）、商标调研
`agateon-trademark-research.md`（2026-08-23 决策 / 2026-08-25 调研完成）、`agateon` org 占名
与 `agateon.com` 域名注册（均 2026-08-25）——本次读取时内容未见改动，逐字核对与 P0-brief 转述
一致。dispatch-context 客观查证信息 A-D（`gh` admin 权限、worktree 拓扑、CHANGELOG 现状、全仓
硬编码 URL 扫描）均为 2026-08-26 当场实测，与 P1 分析同一会话内产生，不存在"已解决前提实际未
解决"的漂移。P0 卡片三条严重漂移判据（目标方案不再成立 / executor_env 平台前提不再成立 /
known_risks 已解决前提实际未解决）均不命中。`[NO_P0_STALE]`（无需 `[P0_STALE]` 标记）。

## 1. 需求复述

TAG0025 是 RM-AG0035「Agateon 品牌改名」的剩余执行工作②，范围限定在设计文档
`design-rename-execution.md` 的 **Phase 0（品牌声明）** 与 **Phase 1（仓库改名执行）**：

1. **Phase 0（品牌声明）**：在 README.md 与 README.zh-CN.md 首屏、CHANGELOG.md 新条目中标注
   "Agateon (formerly agate)"，让访问者立即看到新旧品牌的沿革关系。
2. **Phase 1（仓库改名执行）**：
   - 把 GitHub 主仓 `randomgitsrc/agate` 改名为 `randomgitsrc/agateon`（不可逆的一次性外部操作，
     执行前需再次确认用户在场放行——`gh` 权限已实测具备，但权限核实不等于放行确认）；
   - 同批更新设计 §4 实测的 7 处硬编码仓库 URL（install.sh / agate-install.py /
     agate-changes.py / README.md badge+安装入口 / README.zh-CN.md badge+安装入口）；
   - 本机所有 git remote（主 checkout + 现存 worktree，经实测二者共享同一 `.git/config`）
     完成 `git remote set-url` 迁移；
   - 达成设计 §7 给出的 4 条验收锚：旧 URL 301、`git ls-remote` 新仓名正常、全仓无旧 URL 残留、
     GitHub `in:name agateon` 搜索首屏命中。

**明确排除**（Phase 2/3，不在本次 BDD 展开范围，理由见第 5 节裁剪说明）：`agateon-*` CLI 别名、
品牌 prose 全文统一、brand-check 一次性工具、CHECK 10 脚本名白名单扩展（均为 Phase 2）；
`agateon-portal` 门户新仓（Phase 3）；商标正式申请、PyPI/npm/crates.io 占位、org 迁移（用户侧
协同项，不计本任务交付）。

**三层解耦原则（本任务最大反模式警戒线）**：外部品牌层（仓库名 `agateon`、README/CHANGELOG 品牌
prose）改；内部命名空间（`agate/` 目录、`agate-workspace/`、`~/.agate`、`AGATE_*`、
`agate-*.py` 文件名、`agate_common`）**一律不动**，backtick 代码 token 一律保留。下方任何一条
BDD 都不得写成"全局 find-replace agate→agateon"式的措辞，必须点名具体文件+行。

## 2. 隐含需求识别

1. **中文文档必须同步改**：README.zh-CN.md 与 README.md 是双语镜像；原始任务描述聚焦"品牌声明"，
   未显式强调中文版，但设计 §4 已把 README.zh-CN.md 的 badge（:5）与安装入口（:29）两处一并
   纳入盘点——若只改英文版，中文读者会继续看到旧品牌/旧安装命令，视为必须同步的隐含依赖。
2. **CHANGELOG 段结构必须先建后填**：原始任务只说"CHANGELOG 标 Agateon"，未点破当前 CHANGELOG
   无 `[Unreleased]` 段这一现状障碍（客观查证信息 C 已实测确认，最新已发布段是 `[0.63.0]`）——
   必须先建 `## [Unreleased]` 段才能记 TAG0025 条目，这是 P1.6 check-changelog 机制的隐含前提，
   不建段直接写条目会落错位置。
3. **验收锚的豁免清单必须显式化，否则验收会永远 FAIL**：设计 §7 给出"全仓无旧 URL 残留"验收锚，
   但对 `randomgitsrc/agate\b` 做字面 grep 会命中 3 处边界案例文档（商标调研记录 / 历史评审快照 /
   本任务交接单，见第 6 节同类扫描）。若不把这 3 处显式排除写进 BDD-10 的 Given/When 条件，
   P6 验收时这条锚点永远无法达成 PASS——这是本次 analyst 必须补齐的隐含需求，原始设计文档只给
   "archived/" 一层豁免，未覆盖这 3 处非 archived 目录下的历史快照类文档。
4. **7 处更新必须落在同一 commit（批次原子性）**：known_risks 已提"须同批全改"，但只是定性描述，
   未给出可验证边界。若分批提交，会出现"部分入口指向新仓、部分仍指向旧仓"的中间态，对新用户
   造成困惑（例如 README 已改但 install.sh 未改，用户按 README 点进新仓，却用旧版 install.sh
   装出对旧仓的依赖）——转成 BDD-9 的可验证批次边界。
5. **remote 迁移"理论生效"与"已验证生效"不是一回事**：env-rename-handoff.md 已实测确认 worktree
   与主 checkout 共享同一 `.git/config`，理论上只需主 checkout 执行一次 `set-url`。但"机制上
   应该自动生效"不能替代"逐 worktree 验证性抽查"——隐含需求是迁移后仍需对每个 worktree 跑一次
   `git fetch` 确认实际生效，不能因为机制成立就跳过验证步骤。
6. **权限核实与放行确认是两件事，必须拆开各自成为前置条件**：dispatch-context 客观查证信息 A
   已确认 `gh` 对目标仓具备 admin 权限，容易被误当作"已经可以执行改名"。但 known_risks 明确
   "① `gh` 权限 ② 用户在场确认放行"是并列的两个不可逆操作前置条件，权限核实只解决①，
   ②必须在每次实际执行改名操作前单独发生——不能因为①已完成就默认②也完成。
7. **README badge 是 URL 硬编码点的一种，不是独立范畴**：known_risks 提到"CI 耦合"风险
   （badge img src 硬编码旧仓名断链），但这实际上就是设计 §4 盘点里 README.md:5 / 
   README.zh-CN.md:5 两个"badge"点位——需要在需求文字里显式点破"badge 也是 URL 硬编码点"，
   防止实现阶段把"安装入口链接"和"CI 徽章"当成两类不同工作、只改一类漏改另一类。

## 3. 同类扫描（强制节）

**扫描动作**：dispatch-context 客观查证信息 D 已给出全仓命令
`grep -rn "randomgitsrc/agate\b" --include=*.md --include=*.py --include=*.sh --include=*.yml
--include=*.yaml . --exclude-dir=.git --exclude-dir=.worktrees`（已排除 `randomgitsrc/agateon`
自身命中）的完整命中分类，analyst 本节逐条做处理判定，不重新跑扫描。

### 3.1 Phase 1 核心范围（7 处，本次处理）

| 文件:行 | 判定 | 理由 |
|---------|------|------|
| `install.sh:24` | **本次处理** | 设计 §4 实测核心 7 处之一，安装入口硬编码 |
| `agate/scripts/agate-changes.py:116` | **本次处理** | 同上 |
| `agate/scripts/agate-install.py:55` | **本次处理** | 同上 |
| `README.md:5`（badge） | **本次处理** | 同上，CI 徽章 img src |
| `README.md:29`（安装入口） | **本次处理** | 同上 |
| `README.zh-CN.md:5`（badge） | **本次处理** | 同上，中文版镜像必须同步（隐含需求 1） |
| `README.zh-CN.md:29`（安装入口） | **本次处理** | 同上 |

### 3.2 边界案例（补全扫描新发现，本次逐条判定为"不处理"）

| 文件:行 | 判定 | 理由 |
|---------|------|------|
| `docs/design-notes/agateon-trademark-research.md:3` | **本次不处理** | 商标调研决策记录，行内引用是撰写该报告当下（2026-08-23）项目仓库的真实状态，用于交代"拟更名"的决策背景；性质上是历史决策快照，与 CHANGELOG 历史条目"保持历史真实"同理——改写会扭曲决策记录的时间语境（让读者误以为调研当时仓库已叫 agateon）。旧 URL 经 301 仍可正常访问，不产生断链。 |
| `docs/superpowers/specs/2026-08-15-docs-suite-review.md:89` | **本次不处理** | 2026-08-15 的历史评审快照表格，记录当时 `git remote -v` 实测结果为 `randomgitsrc/agate`；这是"审计事实"记录，改写会使历史审计记录失真（造成"当时验证的其实是新仓名"的错误印象）。 |
| `HANDOFF-TAG0025.md`（多处） | **本次不处理** | 本任务自身的交接单/验证脚本载体，其中的旧 URL 引用是验证命令本体（`curl`/`git ls-remote`/`grep` 的搜索目标字符串）与执行说明性描述，服务于"改名前后对比验证"；若把 grep 搜索模式本身替换成新仓名，命令会失去"检测旧仓名残留"的功能，语义自相矛盾。该文件是任务专属产物，生命周期与任务绑定，不是面向最终用户的产品文档，与 `agate-workspace/tasks/**` 归档豁免层同理但物理位置不同（仓库根而非 `agate-workspace/`），本次显式扩展豁免范围覆盖它。 |

上述 3 处"不处理"的判定已固化为 BDD-10 的显式排除清单（见第 4 节），使"全仓无旧 URL 残留"
验收锚可判定，不会因为这 3 处历史/任务性质文档而永远 FAIL。

### 3.3 已有归属，无需重判（设计 §5.3 归档豁免层）

`agate-workspace/tasks/**`、`agate-workspace/archived/**`、`archived/**` 下的全部命中——均为
任务记录/证据日志/历史文档，设计 §5.3 迁移范围边界表已明确豁免（"保持历史真实"），不再重复判定。

### 3.4 回归拦截手段

设计 §6 已决策"不新增硬性品牌 gate"（避免改名时 check 爆炸），本节尊重该决策，**不建议新增
全仓品牌词 CI gate**。但"硬编码旧仓库 URL 意外重新出现在 Phase 1 核心 7 处文件"与"品牌 prose
统一"是不同范畴的问题（前者是 URL 正确性，后者是措辞风格），风险敞口更窄、可维护性更高：

`[SUGGEST: 推荐在 P3/P4 为 Phase 1 核心 7 处文件新增一条轻量回归测试/脚本断言（仅断言这 7 个
文件不含字面 randomgitsrc/agate 字符串，不做全仓品牌词扫描），防止未来贡献者从旧文档/旧
issue 复制粘贴安装说明时把旧 URL 带回来；范围窄、不与设计 §6"不新增硬性品牌 gate"决策冲突
（那条决策针对的是全仓品牌 prose 统一检查，不是这里的窄范围 URL 回归防护）。若采纳，由 P2/P3
决定具体落地形式（regression 测试 or 一次性 check 脚本）。]`

## 4. BDD 验收条件

### 品牌声明（Phase 0）

#### BDD-1: README.md 首屏可见品牌声明
- Given 打开仓库 README.md
- When 阅读文件顶部（首屏可见区域，不需要滚动到文末）
- Then 包含形如 "Agateon (formerly agate)" 的文字，新旧品牌名同时出现，说明品牌沿革

#### BDD-2: README.zh-CN.md 首屏可见品牌声明（多语言同步）
- Given 打开仓库 README.zh-CN.md
- When 阅读文件顶部首屏可见区域
- Then 包含同时出现 "Agateon" 与 "agate" 两个品牌词的中文表述，说明品牌沿革关系（不要求逐字
  照搬英文版句式，但两个品牌词缺一不可）

#### BDD-3: CHANGELOG.md 建立 [Unreleased] 段并含 TAG0025 条目
- Given 当前 CHANGELOG.md 无 `[Unreleased]` 段（已实测核实，最新已发布段是 `[0.63.0]`）
- When 本任务提交首个 commit 批次
- Then CHANGELOG.md 顶部（`[0.63.0]` 段之上）新增 `## [Unreleased]` 段，且该段下含至少一条
  描述本任务（TAG0025 品牌改名 Phase 0-1）的条目

### 硬编码 URL 同批更新（Phase 1 核心 7 处）

#### BDD-4: install.sh 安装入口指向新仓名
- Given install.sh 第 24 行当前硬编码 `randomgitsrc/agate`
- When 读取该行内容
- Then 该行硬编码的仓库 URL 指向 `randomgitsrc/agateon`，不再出现 `randomgitsrc/agate`（非
  `agateon` 子串意义上的旧仓名残留）

#### BDD-5: agate-install.py 安装脚本指向新仓名
- Given agate/scripts/agate-install.py 第 55 行当前硬编码 `randomgitsrc/agate`
- When 读取该行内容
- Then 该行硬编码的仓库 URL 指向 `randomgitsrc/agateon`

#### BDD-6: agate-changes.py 指向新仓名
- Given agate/scripts/agate-changes.py 第 116 行当前硬编码 `randomgitsrc/agate`
- When 读取该行内容
- Then 该行硬编码的仓库 URL 指向 `randomgitsrc/agateon`

#### BDD-7: README.md badge 与安装入口同批指向新仓名
- Given README.md 第 5 行（badge img src）与第 29 行（安装入口）当前均硬编码 `randomgitsrc/agate`
- When 读取这两行内容
- Then 两行都指向 `randomgitsrc/agateon`（不允许只改其中一行，badge 是 URL 硬编码点的一种，
  不是独立于安装入口的另一类工作）

#### BDD-8: README.zh-CN.md badge 与安装入口同批指向新仓名
- Given README.zh-CN.md 第 5 行（badge）与第 29 行（安装入口）当前均硬编码 `randomgitsrc/agate`
- When 读取这两行内容
- Then 两行都指向 `randomgitsrc/agateon`

#### BDD-9: Phase 1 核心 7 处更新落在同一 commit（批次原子性）
- Given Phase 1 核心 7 处硬编码 URL 更新点（install.sh、agate-install.py、agate-changes.py、
  README.md ×2、README.zh-CN.md ×2）
- When 检查交付这些改动的 commit(s)
- Then 全部 7 处更新点出现在同一个 commit 的 diff 中，不允许跨多个 commit 分批交付（避免中间态
  部分入口指向新仓、部分仍指向旧仓）

#### BDD-10: 全仓无旧仓库 URL 残留（含显式豁免清单）
- Given 对全仓（排除 `.git/` 与 `.worktrees/`）执行 `randomgitsrc/agate\b` 字面扫描
- When 从命中结果中排除以下豁免范围：① `archived/`、`agate-workspace/tasks/**`、
  `agate-workspace/archived/**`（设计 §5.3 归档豁免层，保持历史真实）② 
  `docs/design-notes/agateon-trademark-research.md`（商标调研决策记录，历史决策快照）③ 
  `docs/superpowers/specs/2026-08-15-docs-suite-review.md`（历史评审快照表格）④ 
  `HANDOFF-TAG0025.md`（本任务专属交接单，旧 URL 是验证命令本体与执行说明，非产品文档）
- Then 排除后剩余命中数为 0

### 不可逆操作前置条件

#### BDD-11: GitHub 仓库改名执行前必须获得用户在场放行确认
- Given `gh` 已实测对 `randomgitsrc/agate` 具备 admin 权限（dispatch-context 客观查证信息 A，
  权限核实已完成，不需要在本 BDD 里重复设计"申请权限"步骤）
- When 执行方（主 Agent 或受派发的 subagent）准备发起改名调用（如 
  `gh api -X PATCH repos/randomgitsrc/agate` 更名操作）之前
- Then 必须先在当前会话内获得用户明确的在场放行确认（确认发生在本次改名操作执行窗口内）；若未
  获得该确认，不得执行改名调用——权限核实（技术上能不能做）不能替代放行确认（现在要不要做），
  二者是并列的两个前置条件，缺一不可

### 仓库改名验收锚（Phase 1）

#### BDD-12: 旧仓库 URL 301 跳转到新仓
- Given 仓库已完成改名 `randomgitsrc/agate` → `randomgitsrc/agateon`
- When 对旧 URL `https://github.com/randomgitsrc/agate` 发起 HTTP 请求（如 `curl -sI`）
- Then 响应状态码为 301，且 Location 头指向新仓 URL

#### BDD-13: `git ls-remote` 对新仓名返回正常结果
- Given 仓库已完成改名
- When 执行 `git ls-remote https://github.com/randomgitsrc/agateon.git HEAD`
- Then 命令返回码为 0，且输出包含有效的 commit SHA（无错误信息、无空输出）

#### BDD-14: GitHub `in:name agateon` 搜索首屏命中新仓
- Given 仓库已完成改名且 GitHub 搜索索引已更新
- When 在 GitHub 搜索执行 `in:name agateon`
- Then 目标仓库出现在搜索结果首屏（不需要翻页即可见）

### remote 迁移影响面

#### BDD-15: 主 checkout 执行一次 remote 迁移，worktree 自动跟随
- Given 本机只有主 checkout（`/home/kity/oclab/agate`）与 1 个 worktree
  （`.worktrees/agate-TAG0025`），二者共享同一 `.git/config`（env-rename-handoff.md 已实测确认）
- When 仅在主 checkout 执行一次 `git remote set-url origin <新仓 URL>`
- Then 该 worktree 内 `git remote -v` 无需任何额外操作即显示新仓 URL（不需要在 worktree 内
  重复执行 `set-url`）

#### BDD-16: 迁移后各 worktree 验证性抽查成功
- Given remote 已在主 checkout 完成迁移
- When 在主 checkout 与该 worktree 内各执行一次 `git fetch`
- Then 两次 fetch 均成功完成，返回码为 0，无网络/权限报错（不能因为机制"理论上应该自动生效"
  就跳过这一步验证）

## 5. 待确认清单

`[NO_NEED_CONFIRM]`：本阶段未识别出需要人定夺方向的真无方向项。3 处边界案例文档的处理判定
（第 3.2 节）已由 analyst 依据设计 §5.3"保持历史真实"原则类比给出明确结论，不涉及业务方向
判断，不阻塞推进。1 条回归拦截手段建议（第 3.4 节）已用 `[SUGGEST: ...]` 标注，主 Agent 可
自行采纳或跳过，不必问用户。

## 6. 裁剪说明

- **Phase 2（设计文档意义上的阶段，非 agate P1-P8 阶段）不展开 BDD**：`agateon-*` CLI 别名、
  品牌 prose 全文统一、brand-check 一次性验收工具、CHECK 10 脚本名白名单扩展——理由：设计文档
  `design-rename-execution.md` §5.1/§5.2/§7 已明确把这些划入 v1.0 窗口的 Phase 2，且依赖
  Phase 1 先完成（别名机制依赖仓库已改名的既成事实），本任务范围锁定在 Phase 0-1，P0-brief
  scope 字段已显式切出。
- **Phase 3（门户）不展开 BDD**：`agateon-portal` 新仓建设——理由：设计 §5.5 明确门户是独立
  立项时机（依赖单向，协议仓 → 门户仓，发布节奏不同），当前无立项计划，P0-brief 已排除。
- **商标申请 / PyPI-npm-crates.io 占位 / org 迁移不展开 BDD**：均为用户侧人工协同项
  （P0-brief known_risks 已列），已写入 env-rename-handoff.md 跟踪，不计入本任务交付。

**agate P1-P8 阶段裁剪（frontmatter `phases:` 字段依据）**：`phases: [P1, P2, P3, P4, P5, P6,
P7, P8]`，全流程不裁剪。理由：
- **P1/P2/P4/P5/P6 协议硬性不可裁**，不再单独论证。
- **P3（测试设计）不裁剪**：`risk_level: medium`（见下），按规则仅 `low` 档可裁 P3，本任务
  不满足裁剪条件；且第 3.4 节 SUGGEST 的回归测试若被采纳，需要 P3 先设计测试用例。
- **P7（一致性检查）保留**：本任务是"同批改 7 处文件 + 双语镜像同步"的横切改动，known_risks
  明确"须同批全改"是本任务最大的执行期风险（BDD-9 已固化批次原子性要求）——P7 的跨文件一致性
  核对机制正对应这类"改了 A 忘了配对的 B"风险，保留。设计 §6 已确认
  `check-protocol-consistency.py` 本身不受品牌改名影响（无需新增/修改该 gate 脚本），但这
  与"P7 阶段是否跑一次跨文件核对"是两件事，不构成裁剪 P7 的理由。
- **P8（发布准备）保留**：本任务对应 roadmap 条目 RM-AG0035 剩余工作②，roadmap 回写 `done` 是
  P8 gate 硬校验（RM-AG0043，AGENTS.md 已确认）；是否需要连带版本号 bump 由 P8 阶段按
  `bump_type` 实际判断（本任务不改协议功能，预期 `bump_type` 判定为无需 bump 或仅记
  CHANGELOG，不在 P1 预判）。

**ceremony**：不声明（frontmatter 不写 `ceremony` 字段——`agate-md-field-set.py` 当前稳定版
key 白名单未收录该字段，遵循"写入失败照错误提示修正，不绕开 set"，不手写）。按 fail-closed
规则，不声明 = 默认 `standard`。理由与默认结论一致：本任务含一条不可逆外部操作（BDD-11），
不满足"薄仪式"适用场景，未申请 thin 四要素，standard 档位符合实际。

**risk_level：medium**。理由：不评 `low`——含一条不可逆的外部操作（GitHub 仓库改名）与
CI 徽章断链风险（known_risks 已列），且涉及 7 处文件跨批一致性要求；不评 `high`——不触碰
`agate/` 协议正文、不改任何 `check-*.py` gate 脚本逻辑、无数据迁移、无破坏性行为变更
（改名有 GitHub 301 兜底、目录/remote 迁移经 env-rename-handoff.md 验证是纯配置操作可逆），
设计文档已三轮评审通过降低了方案层面的不确定性。

## 7. 范围声明

`packages:` 与 `domains:` 已写入文件头 frontmatter，正文不重复列举。简述：

- **packages**：`agate-brand-docs`（README.md / README.zh-CN.md / CHANGELOG.md，品牌声明与
  CHANGELOG 纪律）、`agate-installer-scripts`（install.sh / agate-install.py /
  agate-changes.py，安装入口硬编码 URL）、`agate-repo-admin`（GitHub 仓库改名操作 + 本机
  git remote 配置迁移，无源码 diff 的运维类改动）。
- **domains**：`docs`（README/CHANGELOG 品牌声明与 URL 文本）、`cli`（安装脚本内嵌 URL，
  面向命令行安装场景）、`ops`（GitHub 仓库管理操作与本地 git 配置迁移，不涉及 frontend/mcp/
  security）。无 `frontend` 域，不触发 UX 类别 BDD 与 `ui_render_shape`/`ui_ux_dimensions`
  声明要求。

## 8. 能力需求声明

判断树核验（先问缺的是能力还是环境）：本任务不缺"agent 侧能力"（不涉及看图/视觉/生疏工具），
也不缺"运行环境"（网络/`gh`/`git` 已在 P0-brief `executor_env` 声明且实测齐备：
`network: "full"`、`has_local_runtime: true`；dispatch-context 客观查证信息 A/B 已当场实测
`gh` 权限与 worktree 拓扑）。因此**不声明 `verification_env`**，也不产生
`supplementable`/`GAP` 缺口。

```yaml
capability_requirements:
  - need: github-repo-admin-api
    why: Phase 1 需要通过 gh api 执行不可逆的仓库改名操作（BDD-11/12/13/14）
    available:
      - "gh CLI（本机已认证 randomgitsrc 账号，对 randomgitsrc/agate 具备 admin 权限，见
         P1-dispatch-context-analyst.md 客观查证信息 A，2026-08-26 当场实测）"
    status: available
  - need: local-git-multi-worktree-remote-config
    why: remote 迁移需要确认主 checkout 与 worktree 共享 .git/config 的机制成立并做验证性抽查
         （BDD-15/16）
    available:
      - "git（本机已实测 2 个工作树共享同一 .git/config，见 env-rename-handoff.md 与
         P1-dispatch-context-analyst.md 客观查证信息 B）"
    status: available
  - need: outbound-network-github
    why: 验收锚 BDD-12（curl 301）/BDD-13（git ls-remote）/BDD-14（GitHub 搜索）均需访问
         github.com
    available:
      - "P0-brief executor_env 已声明 network: \"full\""
    status: available
```

无 `frontend` 域，不适用 vision 能力声明硬要求。
