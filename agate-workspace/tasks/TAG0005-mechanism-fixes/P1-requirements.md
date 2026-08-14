---
phase: P1
task_id: TAG0005-mechanism-fixes
type: problems
parent: P0-brief.md
trace_id: TAG0005-mechanism-fixes-P1-20260813
status: draft
created: 2026-08-13
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts-sh, agate-scripts-py, agate-docs, agate-tests]
domains: [backend, cli]
---

[NO_NEED_CONFIRM]

# P1 需求基线 — agate 机制修复批（TAG0005）

## 1. 需求复述

修复 4 个已核实的机制/契约缺陷，全部为「现有东西错了/不完整」的修复，无新机制。Linux 全量 bats（714）为回归红线，每处修复保持全绿 + 新增对应测试。

| 缺陷 | 现象（代码证据） | 修复方向（已拍板） |
|------|------------------|--------------------|
| RM-AG0010 P2 gate vs C8 契约矛盾 | check-gate.sh P2 无条件要求 P2-review.md（L157-161 exit 1 拦截）；C8 表 backend 域 P2 无触发评审角色（role-system.md L54-61 / review-mapping.md L15-23 / phase-cards/P2-design.md L93-97）→ backend 域任务 P2 按 C8 不派评审被 gate 拦截，主 Agent 被迫自造评审（TPV0090） | **C8 补 backend P2 评审**（用户 2026-08-13 拍板），三处 C8 表同步；check-gate.sh 本身不改 |
| RM-AG0011 P5 gate_commands 计数语义 | agate-gate-p5-count.py L19 `^  (P5\w*):` 合并计数（P5/P5_unit/P5_e2e 各计 1 → 3）；check-gate.sh L253-257 WARNING 输出「N 个 gate_commands.P5 命令」→ 实际是「1 主 + N-1 辅助」，误导主 Agent | 区分主/辅命令（P5 是主，P5_* 是辅），WARNING 文案区分主/辅 |
| RM-AG0012① 自定义角色无条件注入评审指令 | dispatch-prompt.md L9-13「Review 角色特别指令」（status draft→approved）被 render 脚本（L78 main_block）无条件注入，执行角色也被注入，语义混乱 | 按角色 type（execution vs review）条件注入——render 脚本已能区分 ROLE_DIR |
| RM-AG0012② render 脚本角色不存在 exit 0 | 主 Agent 已核实：缺陷已修复——agate-render-dispatch-prompt.sh L66-68 自 v0.23.0 起 exit 2，实测 EXIT=2；但 agate/tests/unit/agate-render-dispatch-prompt.bats 无回归测试覆盖（RP.1-RP.16 只测合法角色） | 补回归测试锁定该行为（角色文件不存在 → exit 2 + stderr 报错） |
| RM-AG0003 短命会话无制度化重试 | dispatch-protocol.md L105-129 空返回恢复策略全手动；TQC0001 实测 P2 49 秒 / P3 3 分钟各一次空返回靠主 Agent 经验性重发 | 增量增强：恢复策略加「自动重试一次」+「会话时长 <1min 判定异常告警」；**不改变现有重试语义**（retry 上限/PAUSED 规则不动） |

**范围锁定**：5 处修复互不耦合；若 P1 分析发现需改动超出上述锁定范围，先停下跟主 Agent / 用户确认（P0-brief known_risks 要求）。

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| I1 | RM-AG0010 三处 C8 表必须同步（role-system.md / review-mapping.md / phase-cards/P2-design.md） | 只改一处会留下同类矛盾（agate 历史多次栽在「修一处漏同类」）；consistency 检查按 packages 声明做跨文件交叉核对 |
| I2 | RM-AG0010 具体评审角色名**不在 P1 定**，留 P2 选型 | 派发指引明确：P2 阶段再定具体评审角色；P1 绑定角色名会提前锁定 P2 设计空间 |
| I3 | check-gate.sh P2 分支不改（反向是 gate 豁免，已被用户否决） | 防止 P2/P4 误选「gate 豁免」方案破坏既有 P2 评审硬约束 |
| I4 | RM-AG0011 WARNING 文案改动须同步既有 bats 断言（G5_CMD.1「2 个 gate_commands.P5」、G5_CMD.5） | 现网测试断言旧文案，只改脚本不改测试 → 全量 bats 变红（回归红线） |
| I5 | RM-AG0011 read-p5-commands.py 不需要区分主/辅（执行枚举，主+辅都要跑）——已核验，需回归守卫防误伤 | 该脚本被 agate-capture-env-baseline.sh 消费做基线捕获，计数语义修复若波及会破坏 P5 基线机制 |
| I6 | agate-gate-p5-count.py 输出格式变化须同步消费方 check-gate.sh L253 | 当前输出纯数字被 `-gt 1` 消费；若改「主/辅分列」输出需同步 WARNING 判定逻辑（P2 定具体格式） |
| I7 | RM-AG0012① 条件注入改动涉及 render 脚本 + 模板，须保证 dispatch-prompt.md（assets）与 dispatch-protocol.md 内联模板的「Review 指令」语义不进一步分叉 | 内联模板（dispatch-protocol.md L427-494）本身无该节；改动后 assets 模板按角色条件注入，两处语义需一致（协议文件为权威来源） |
| I8 | RM-AG0012② 新增 bats 用例 → 测试计数漂移 → 须同步更新 **agate/tests/README.md 逐脚本计数表**（agate-render-dispatch-prompt.sh 行） | 库内实时逐脚本计数表在 agate/tests/README.md（agate-test-plan-2026-07-01.md 已归档至 agate-workspace/archived/plans/，非库内实时路径）；计数漂移 = 文档漂移（AGENTS.md 开发命令）。注：count-tests.sh L22 提示仍指向已归档的 docs/plans 路径——pre-existing 陈旧引用（fb5b754 归档时未同步），**非本任务引入，不纳入本任务修复范围**（避免范围蔓延）。README 计数表现在已存在 1 漂移（render 记 16 vs bats 实际 17 @test），新增用例后按实际数同步 |
| I9 | RM-AG0003 「自动重试一次」与「手动调整后重派」的关系须在策略文档中定义清晰 | 现状首次空返回是「分析→调整→重派」；增量后需明确自动重试与既有 retries[Pn] 计数/MAX_RETRY/PAUSED 的衔接，不改变上限语义 |
| I10 | RM-AG0003 会话时长 <1min 判定须复用已有「主 Agent 记录派发耗时」弱信号（dispatch-protocol.md L128） | 现状已有耗时记录作为弱信号；增量告警应基于该机制扩展，不另起炉灶 |
| I11 | 所有脚本改动走 TDD（先红后绿） | AGENTS.md「改脚本的工作流」硬性约定；本任务改脚本（check-gate.sh / agate-gate-p5-count.py / render 脚本）+ 补测试 |
| I12 | 改 agate/*.md + agate/scripts/* 触发 SELF-GATE | commit message 需含 `self-gate-review:` 或 `self-gate-skip:`，否则 commit-msg hook WARNING |
| I13 | consistency 检查必须用 worktree 自己的脚本 | 检查对象是 worktree 里的协议文件；误用 `~/.agate` 会扫主 checkout（HANDOFF §2 双工作区纪律） |
| I14 | 全量 714 bats 回归底线 + 每个修改脚本的单脚本测试先行 | Linux 现状是基线（HANDOFF 核心约束 1） |

**同类扫描结果**（P0 known_risks 强制要求，全仓 grep，三组）：
- **「静默 exit 0」类**：`agate/scripts/*.sh` 中「echo 错误到 stderr 但 exit 0」字面模式 `>&2;\s*exit 0`，全仓实测 **4 处**（`rg -n '>&2;\s*exit 0' agate/scripts/`，无跨行变体）：
  - `check-debt.sh:26`：`--retreat-coverage` 模式依赖加载失败（`source agate-workspace-resolve.sh` 失败）→ stderr 报「无法加载」→ `exit 0`。与 RM-AG0012② 原始缺陷**结构同构**（依赖缺失→stderr 报错→exit 0 成功码）。裁定：**同同类，纳入修复**（该模式文档声明「只读 WARNING 恒 exit 0（不阻断）」针对的是有意跳过分支，依赖加载失败是硬失败而非有意跳过，静默 exit 0 会让回退覆盖比对被无声跳过）→ 并入 BDD-16。
  - `agate-capture-env-baseline.sh:23/26/28`：三处均为**显式跳过语义**（消息含「跳过基线捕获」「非 git 仓库，跳过」）。裁定：**非同类的有意跳过**——脚本头注释声明「本脚本任何情况下都不应导致调用方 P3/P4 流程失败」「不影响 P3/P4 推进」，捕获失败不写文件 exit 0 由 P5 graceful degradation 兜底（best-effort 设计），**不需修复**。
  - render 脚本为唯一**已修同类**实例（v0.23.0 起角色不存在 exit 2，BDD-10/11 锁定）。
- **「无条件注入评审指令」类**：全仓 `Review 角色特别指令` 仅 dispatch-prompt.md L9-13 一处（docs/reviews、docs/plans、archived 目录为历史快照/存档，非协议本体）。**仅 1 处**。
- **「P5 前缀计数」类**：`^  (P5\w*):` 正则 2 处——agate-gate-p5-count.py L19（计数，待修）+ agate-read-p5-commands.py L26（执行枚举，核验无需改，加回归守卫）。

## 3. BDD 验收条件

> 组织原则：按 5 处修复分组编号，每条可二值判定（PASS/FAIL），BDD 描述「用户能看到什么/系统该做什么」，不绑定实现细节。

### RM-AG0010 — C8 映射表补 backend P2 评审

#### BDD-1: backend 域 P2 有机械触发的评审角色（三处 C8 表同步）
- Given 一个 backend 域、risk_level 非 high 的 agate 任务
- When 读取 role-system.md / rules/review-mapping.md / phase-cards/P2-design.md 三处 C8 映射表
- Then 三处表的 backend 行均含 P2 插入阶段的评审触发条目（不再只是「P4 后 review」），机械映射可直接派到 P2 评审

#### BDD-2: check-gate.sh P2 的 P2-review.md 无条件要求保持原样（gate 不改）
- Given RM-AG0010 修复完成
- When 检查 check-gate.sh 的 P2 分支（L157-161）
- Then 仍无条件要求 P2-review.md 存在且 status=approved（修复方向是 C8 补评审，不是 gate 豁免/放宽）

### RM-AG0011 — P5 gate_commands 主/辅计数语义

#### BDD-3: P5 计数区分主命令与辅助命令
- Given P2-design.md gate_commands 声明 P5 + P5_unit + P5_e2e（1 主 2 辅）
- When 运行 agate-gate-p5-count.py
- Then 输出能区分主命令（P5）与辅助命令（P5_*）的数量（而非合并计为 3）

#### BDD-4: check-gate P5 多命令 WARNING 文案区分主/辅
- Given P2-design.md 声明了辅助 P5 命令（P5_*），check-gate.sh P5 触发多命令 WARNING
- When 读取 GATE P5 WARNING 输出
- Then 文案区分主/辅（如「1 个主命令 + N 个辅助命令」），不再笼统称「N 个 gate_commands.P5 命令」

#### BDD-5: 仅主命令（无 P5_*）时不输出多命令 WARNING（现状保持）
- Given P2-design.md 只声明 P5（无任何 P5_* 键）
- When 运行 check-gate.sh P5
- Then 不输出 gate_commands.P5 多命令 WARNING（行为与现状一致）

#### BDD-6: read-p5-commands 执行枚举行为不变（主+辅全枚举）
- Given P2-design.md 声明 P5 + P5_e2e（含各自 formatter）
- When 运行 agate-read-p5-commands.py
- Then 仍输出全部 P5 命令（主命令与辅助命令）及其 formatter 配对，供 P5 执行与基线捕获使用（计数语义修复不改变执行枚举）

### RM-AG0012① — Review 角色特别指令按角色类型条件注入

#### BDD-7: 执行角色派发 prompt 不含「Review 角色特别指令」
- Given 派发 execution-roles 角色（如 architect / implementer / verifier）
- When 运行 agate-render-dispatch-prompt.sh 渲染派发 prompt
- Then 渲染输出不含「Review 角色特别指令」节（执行角色不被注入 status draft→approved 语义）

#### BDD-8: 评审角色派发 prompt 含「Review 角色特别指令」
- Given 派发 review-roles 角色（如 requirements-review / design-review / review）
- When 运行 agate-render-dispatch-prompt.sh 渲染派发 prompt
- Then 渲染输出含「Review 角色特别指令」节，且含 status 初始 draft 后改 approved/rejected/needs-revision 的完整语义

#### BDD-9: 同类扫描守卫——协议内该指令仅存在于模板一处（经 render 条件注入分发）
- Given RM-AG0012① 修复完成
- When 全仓 grep「Review 角色特别指令」
- Then 协议文件（agate/**）中仅 dispatch-prompt.md 模板一处存在（无第二份无条件注入副本；docs/plans、archived 等历史快照不计）

### RM-AG0012② — render 脚本角色不存在 exit 2 回归测试

#### BDD-10: 角色文件不存在 → exit 2 + stderr 报错
- Given 派发一个不存在的角色名（如 nonexistent-role）
- When 运行 agate-render-dispatch-prompt.sh
- Then 返回 exit code 2 且 stderr 含「角色文件不存在」报错（不退回为 v0.23.0 修复前的 exit 0）

#### BDD-11: 该行为有 bats 回归测试锁定
- Given agate/tests/unit/agate-render-dispatch-prompt.bats 测试套件
- When 运行该套件
- Then 含覆盖「角色文件不存在 → exit 2 + stderr 报错」的回归测试用例（RP 系列新增编号，断言 exit 2 + stderr 报错）

### RM-AG0003 — 短命会话自动重试（增量增强，不改既有重试语义）

#### BDD-12: 空返回恢复策略含「自动重试一次」
- Given subagent 首次空返回（约定产出文件不存在）
- When 主 Agent 执行 dispatch-protocol.md 空返回恢复策略
- Then 策略文档明确「自动重试一次」动作（自动重发一次，不要求主 Agent 手工分析后重发）；自动重试后仍空返回才进入既有 retries[Pn] 流程

#### BDD-13: 短会话（<1min）空返回触发异常告警
- Given subagent 空返回且派发会话时长 <1min
- When 主 Agent 评估该空返回的失败模式
- Then 策略文档声明输出「会话时长异常短」告警（复用已有派发耗时记录弱信号，明确 <1min 为异常判定阈值）

#### BDD-14: 自动重试不改变现有 retry 上限/PAUSED 规则
- Given RM-AG0003 增量增强完成
- When 对比 dispatch-protocol.md 空返回恢复策略与改造前
- Then retry 上限（MAX_RETRY）与 PAUSED 判定规则与改造前一致（「自动重试一次」不改变既有重试语义）

### 同类扫描守卫（静默 exit 0）

#### BDD-15: 全仓 scripts 的「stderr 报错后 exit 0」仅剩显式跳过语义（同类扫描守卫）
- Given RM-AG0012 修复完成且 check-debt.sh:26 已修复
- When 执行判定命令 `rg -n '>&2;\s*exit 0' agate/scripts/*.sh`（全仓字面扫描，排除 docs/archived 历史快照）
- Then 所有命中行的 stderr 消息文本均含「跳过」语义（显式跳过/不影响推进声明，如 agate-capture-env-baseline.sh 的「跳过基线捕获」「非 git 仓库，跳过」）；若任一命中行含「无法加载/缺失/失败」类错误语义则 FAIL（check-debt.sh 依赖加载失败已改 exit 非零，不应再命中）

#### BDD-16: check-debt.sh --retreat-coverage 依赖加载失败不再静默 exit 0
- Given 运行 check-debt.sh --retreat-coverage 时 agate-workspace-resolve.sh 缺失或 source 加载失败
- When 执行 check-debt.sh --retreat-coverage
- Then 返回非零 exit code 且 stderr 报错（依赖加载失败属硬失败，不静默当作成功跳过；「有意跳过」分支如无 retreat 提交仍 exit 0）。修法由 P2 定，建议 exit 2 WARNING（与 check-gate.sh 失败约定一致）

## 4. 待确认清单

[NO_NEED_CONFIRM]

无未决待确认项。方向性决策均已拍板：
- RM-AG0010 方向由用户拍板（C8 补 backend P2 评审，非 gate 豁免）
- RM-AG0012② 缺陷已确认修复，仅补测试
- RM-AG0011/RM-AG0003 增量范围由 P0-brief 锁定
- 具体实现选型（C8 表补哪个评审角色、p5-count 输出格式、条件注入实现位置）属 P2 设计决策，不阻塞 P1

## 5. 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` — 无裁剪。

| 阶段 | 保留理由 |
|------|---------|
| P1 | 需求基线，不可裁剪（核心阶段） |
| P2 | 5 处修复各有设计选型（C8 表评审角色、p5-count 输出格式、条件注入位置、自动重试语义、告警阈值），需多方案权衡 |
| P3 | 脚本改动走 TDD（先红后绿），需 test-designer 写红灯测试（含 RP 新增回归用例） |
| P4 | 改脚本 + 文档，需实现 |
| P5 | 全量 bats（714）回归 + 单脚本测试验证，验证 gate_commands.P5 |
| P6 | 逐条 BDD 验收，证据留档 |
| P7 | 跨文件一致性（三处 C8 表 + render 脚本 + 模板 + dispatch-protocol），consistency-reviewer 交叉核对 |
| P8 | 版本发布（TAG0005+TAG0009 合并一次发布） |

## 6. 范围声明

见 frontmatter：`packages: [agate-scripts-sh, agate-scripts-py, agate-docs, agate-tests]`，`domains: [backend, cli]`。

- **agate-scripts-sh**：check-gate.sh（P5 WARNING 文案，P2 分支不改）、agate-render-dispatch-prompt.sh（条件注入）
- **agate-scripts-py**：agate-gate-p5-count.py（主/辅计数）；agate-read-p5-commands.py（不改，仅回归守卫）
- **agate-docs**：role-system.md、rules/review-mapping.md、phase-cards/P2-design.md（三处 C8 表）、dispatch-protocol.md（空返回恢复策略）、assets/templates/dispatch-prompt.md（Review 指令条件注入）
- **agate-tests**：agate-render-dispatch-prompt.bats（新增回归）、agate-gate-p5-count.bats、check-gate.bats（WARNING 文案断言同步）、agate/tests/README.md 逐脚本计数表（测试计数同步，非已归档的 docs/plans 测试计划）

## 7. 能力需求声明

```yaml
capability_requirements:
  - need: bats-1.10
    why: 运行/新增 agate 测试套件（回归红线 + TDD 红绿）
    available:
      - "本机 bats 1.10（HANDOFF §2 已确认）"
    status: available
  - need: python3-pyyaml
    why: 跑 check-protocol-consistency.py（P7 一致性检查，必须用 worktree 自己的脚本）
    available:
      - "本机 python3 3.12 + pyyaml（HANDOFF §2 已确认）"
    status: available
  - need: shellcheck
    why: agate 脚本 shellcheck 检查（改 scripts/*.sh 后验证）
    available:
      - "本机 shellcheck（HANDOFF §2 已确认）"
    status: available
```

本任务为 agate 协议本体自身修复（self-gate 任务），能力齐备，无 GAP、无 supplementable。`[PROD_NOT_TOUCHED]`——全程仅接触 worktree 测试环境，未接触生产环境。
