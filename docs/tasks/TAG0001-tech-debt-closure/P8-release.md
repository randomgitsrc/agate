---
phase: P8
task_id: TAG0001-tech-debt-closure
type: release
parent: P7-consistency.md
trace_id: TAG0001-P8-20260812
status: draft
created: 2026-08-12
agent: implementer
debt_check: reviewed
---

# TAG0001 — P8 发布准备记录（v0.42.0 → v0.43.0）

> 角色：releaser（implementer P8 模式）。本文件为发布准备记录，**只产出文件不执行 git commit / git tag / bump-version**——bump-version + CHANGELOG 更新 + git tag 由主 Agent 在 P8 gate 验证通过后亲自执行。

环境标记：`[PROD_NOT_TOUCHED]`——本次仅只读读取协议文件 + 只读 git 查询（tag/log/grep），未改动 `~/.agate`、未对 worktree 做任何写操作。

## 1. bump 范围与 bump_type

### 1.1 packages 声明（P2-design.md frontmatter）

- `packages: [agate]`（协议本体单一包），`ui_affected: false`
- bump 范围 = worktree `agate/` 协议本体——P7 §3.3 已核对 16/16 改动面全部落在 worktree `agate/` 与任务记录内，无跨包改动

### 1.2 bump_type

```
bump_type: minor
```

### 1.3 版本号变更确认

- **旧版本：v0.42.0**（README.md L6 badge + 本地 tag v0.42.0；`git describe` = v0.42.0-9-g328cbd3，HEAD=328cbd3 TAG0001-P7 commit）
- **建议新版本：v0.43.0**
- 变更动作（主 Agent 执行）：README.md L6 badge `v0.42.0` → `v0.43.0`；P5 重跑全绿后 `git tag v0.43.0`

### 1.4 理由（里程碑策略）

- 主 Agent 决策（dispatch-context）：TAG0003=v0.41.0、TAG0002=v0.42.0（均已打本地 tag），TAG0001=v0.43.0，最终一起 push/merge。
- 本次变更性质：**规则新增/调整**（技术债登记闭环 + debt/ 目录归类修正），**非破坏性**——无 tech-debt.md 时校验器/回退比对/P8 留痕全部 no-op（UPGRADING.md v0.43.0 节 ①），存量项目行为不变。
- 定级 minor：含新机制（DEBT 模板/校验器/回退比对）、新脚本（agate-debt-check.py / check-debt.sh）、新必填字段（P8 debt_check）、工作区子目录 8→9——规则面实质新增，非 patch 级纯修复；又非破坏性（可选启用），不触发 major。

## 2. CHANGELOG 更新确认

### 2.1 现状

- CHANGELOG.md 最新节 `[0.42.0]`（TAG0002），Keep a Changelog 格式，分类为「新增 / 变更 / 修复 / 文档」。
- 本次 bump 后 `[0.42.0]` 保持原样，在 `[0.42.0]` 段前插入 `[0.43.0]` 新节。

### 2.2 [0.43.0] 新节内容建议（主 Agent bump 时写入，格式对齐既有节）

```markdown
## [0.43.0] - 2026-08-12

### 新增（TAG0001 技术债登记闭环，Phase 1-3）
- **DEBT 条目模板 `assets/templates/tech-debt-template.md`**：标准技术债登记格式——用法/判据三分法（技术/管理/协议）+「都不影响→不登记」出口 + 三态（open/in_progress/closed）+ 字段表 + 可解析示例条目；落点 `{AGATE_WORKSPACE}/debt/tech-debt.md`（单文件多条目，每条 ` ```yaml ` fenced 机器块 + 可选正文）
- **`agate-debt-check.py` + `check-debt.sh`**：技术债 schema 校验器（fail-closed 薄壳 + 独立 .py）——必填字段 / 枚举（category/status/priority/source）/ 类型 / closed 准入（须 task_id + evidence 引用 P5/P6 证据）/ 同文件 id 唯一性；无任何 yaml 块 → no-op（向后兼容）
- **`check-debt.sh --retreat-coverage` 回退覆盖比对**：`git log --all --grep='^retreat:'` 提取回退提交，与 `source: retreat` DEBT 条目 evidence 引用比对，未登记 → WARNING（恒 exit 0，只读提醒不挂 gate）
- **P8 `debt_check` 必填字段**：P8-release.md 产出规格新增（`none` = 本次无关注项 / `reviewed` = 已核对并附条目清单）；check-gate.sh P8 分支缺失即 exit 1 硬拦截、内容任意放行不阻断发布；`debt_check: none` 可跨发布 grep 计数（防无脑打勾可观测）

### 变更（TAG0001 debt/ 归类修正 + 回退强制）
- **工作区子目录集 8→9**：新增 `debt/` 技术债登记目录（WORKFLOW.md 目录图 + orchestrator-template/SETUP/state-machine 三处 mkdir 同步同一 9 集字面量）；tech-debt 不再归入 `agents/`（该目录只放 agent 输入知识 project.md/memory）
- **回退落地后必须建 DEBT 条目**：`rules/state-transitions.md` 回退规则 + P6/P4 卡片 + `agate-retreat-to.sh` 回退完成提醒 四处同步「`source: retreat` 条目，evidence 引用回退提交哈希」强制
- **review 可发现性**：`plan-eng-review.md` 追加「提债须用标准 DEBT 条目格式」

### 文档
- **UPGRADING.md v0.43.0 节**：子目录 8→9（可选启用）/ tech-debt 路径 / P8 debt_check / 回退强制四项升级指引
- **TAG0003 BDD-1 口径修订注**（P1/P6 各一行）：8 子目录 → 9 子目录口径更新
```

### 2.3 变更节对照（git log v0.42.0..HEAD）

- HEAD 提交序列实测（git log v0.42.0..HEAD）：TAG0001-P1..P7 共 7 个 commit（04c7465 → 328cbd3），全部为技术债登记闭环 + debt/ 归类修正内容，无遗漏项。
- bump + CHANGELOG [0.43.0] 新节 + README badge + tag 将由主 Agent 在 P8 验证通过后同一 commit 完成。

## 3. 发布检查命令（P2 gate_commands + AGENTS.md 标准流程）

> 发布检查命令由主 Agent 亲自执行（P8 卡片硬约束，不可委托），本文件仅列清单供参照，不代跑。

| 检查 | 命令 | 基线（P5/P6 实测） |
|---|---|---|
| 全量 bats | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | 676/0 |
| consistency | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR |
| shellcheck | `shellcheck -S warning agate/scripts/*.sh` | 0 |
| 用例数 | `bash agate/tests/scripts/count-tests.sh` | 基线含新增用例（无漂移） |
| 版本号 | README.md L6 badge → v0.43.0 + tag v0.43.0 | CHECK 7 自动通过 |

## 4. 临时资源清单（releaser → 主 Agent 交接）

> 主 Agent 在 P8 gate 通过后执行 READY 收尾检查时，按此清单清理。

- **临时数据（bats 测试创建的持久 /tmp 产物，非 BATS_TEST_TMPDIR 自动清理范围）**：
  - `/tmp/opencode/bdd13-mIgwyo/`、`/tmp/opencode/bdd14-PJ2a13/`、`/tmp/opencode/bdd15-xShJ1b/` —— P6 验收 BDD-13/14/15 的 fixture git 仓库（含 retreat 提交 + tech-debt.md），P6-evidence/bdd-13.log 有路径引用
  - `/tmp/opencode/debttest/`（missing-evidence.md / valid.md）—— P5 schema 校验手测临时文件
- **临时服务/进程**：无（本任务为纯协议仓库变更 + bats fixture 验证，未启动任何 debug server / daemon）
- **开发安装**：无（复用既有 python3 + pyyaml + bats，无新增安装）
- **生产环境**：`[PROD_NOT_TOUCHED]`——未写生产数据/API、未触 `~/.agate`（v0.42.0 稳定版工具未改动）
- **可复用保留（发布内容，勿误删）**：`agate/tests/unit/agate-debt-check.bats`（新增用例）、`assets/templates/tech-debt-template.md`、`scripts/agate-debt-check.py` / `check-debt.sh`

## 5. debt_check（本任务债务清单确认留痕）

```
debt_check: reviewed
```

- 核对内容：
  - 本任务（TAG0001）P1-P7 全程**无回退事件**（提交序列 04c7465→328cbd3 全为正向推进），无新增 `retreat:` 提交需登记。
  - 协议仓库历史存在 2 条**机制建立前**的回退提交：`023b28b`（retreat: P5→P4）/ `29301ad`（retreat: P6→P5），2026-08-10 check-p6-format --fix 修复。本任务已将其作为 `source: retreat` 判据的 fixture 正反两向验证（BDD-13/14/15，见 agate-debt-check.bats）；但协议仓库自身工作区**未启用 debt/ 目录**（opt-in，UPGRADING v0.43.0 ①）——无 tech-debt.md → 回退比对 no-op，无 WARNING。
  - 未决后续项（治理动作，非本任务范围）：若协议仓库后续启用债务登记，应将 023b28b / 29301ad 以 `source: retreat` 条目补登记。
- 本发布无「未关闭债务阻断发布」情形——`debt_check` 字段存在即通过，不因内容拦截（BDD-17）。

## 6. Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|---|---|---|---|
| 架构 | 「登记簿类」项目级状态文件（tech-debt 多条目）与任务级单 frontmatter 是两种数据形态——独立校验器（agate-debt-check.py + check-debt.sh 薄壳）复用「fail-closed + stdout 错误行」模式而非复用实现，可把对既有 frontmatter 校验的回归风险降到零（654 用例零红） | TAG0001 | 2026-08-12 |
| 架构 | 目录归类不是小事——tech-debt 有状态机/schema/被脚本读写，属「流程产出的项目状态记录」，归独立 `debt/` 比塞进「agent 输入知识」目录更符合内容边界判据；归类修正会牵动 mkdir 字面量、目录图、升级文档、TAG0003 验收口径等多端面，须 grep 全量同步 + BDD 重验 | TAG0001 | 2026-08-12 |
| 测试 | bats fixture 里 `mkdir -p "$dir/{a,b,c}"` 大括号被引号包裹不展开、只建 1 目录（而非 9）——shell 大括号展开不做引号内求值，fixture 断言与真实行为必须显式参数化（P4 已修，DESIGN_GAP 1/1 REVIEWED） | TAG0001 | 2026-08-12 |

## 7. READMEY 收尾提示（主 Agent 执行）

1. P8 gate 验证通过后：bump README badge v0.42.0→v0.43.0 + 写入 §2.2 CHANGELOG `[0.43.0]` 新节 → **同一 commit + tag v0.43.0**（AGENTS.md 版本发布流程 + P8 卡片）。
2. **重跑 P5 gate**：bump 后必须 P5 全量回归全绿再 tag（P8 卡片推进条件）。
3. `git log v0.42.0..HEAD --oneline` 对照 CHANGELOG 无遗漏（§2.3 已列 7 commit）。
4. 按 §4 临时资源清单清理 `/tmp/opencode` 下 P6 fixture 与 debttest。
5. 环境标记 `[PROD_NOT_TOUCHED]`：无生产残留。
6. release PR 必须普通 merge（`--no-ff`），禁止 squash merge（AGENTS.md：tag 需为 HEAD 祖先，squash 会致 describe 回退）。
