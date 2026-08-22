---
phase: P8
task_id: TAG0020-independent-judge
type: release
parent: P2-design.md
trace_id: TAG0020-P8-20260822
status: draft
created: 2026-08-22
agent: implementer
packages: [agate]
bump_type: minor
debt_check: reviewed
---

# P8 发布准备 — 独立 Judge 机制（RM-AG0032）：v0.58.0 → v0.59.0

> releaser（implementer P8 模式）产出。**不执行 git commit / tag / bump-version**——三项由主 Agent 在 gate 验证通过后亲自执行。
> [PROD_NOT_TOUCHED]：本文件只写任务目录产出，未触碰主 checkout / 生产环境。

## 1. 版本信息

- **当前版本**：v0.58.0（README.md badge L5 / CHANGELOG [0.58.0] 小节 / git tag v0.58.0，TAG0019 发布）
- **目标版本**：**v0.59.0**
- `bump_type: minor`
- **理由**：新增 P6.5 独立 Judge 机制功能（P1 10 条 BDD 全过，P7 BLOCKER=0），**向后兼容**——历史任务（.state.yaml 无 `judge.enabled: true`）对 P6.5 全链跳过（BDD-2），无破坏性变更、无迁移动作。

## 2. debt_check: reviewed

已读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（DEBT0001 ~ DEBT0017 共 17 条）核对：

- **无 TAG0020 相关既有债务条目**（DEBT0001-0017 均为历史任务 TAG0013/0008/0006/0015/0016/0017/0007 登记）。
- **本任务产生或留存的候选关注项**（三分法评估：均未达"不修验收声明变假 / 不修未来变更更贵"登记标准 → 不新增债务条目，列为正文记录供未来评估）：
  1. **P4 评审 I-3 budget_exhausted 粘性**（P4-progress「修复轮」次要项 ③）：一轮预算超限后，后续轮次 verdict 永远无法 passed——实现忠实于 P2-design §3.3 步 8 原文（设计语义副作用，非实现偏差）；如需改为"轮次区分配对"（事件带 round / 最近一轮比对）属 P2 设计变更。**三分法判定：不影响本任务验收声明，未来变更成本不明确 → 不登记**。
  2. **P4 评审 I-4 同 BDD 重复结论行不拦截**（可选增强）：编号集相等 + 条目数==criteria_total 下冗余行不被检出——BDD-3 最小合规满足。**三分法判定：不影响验收 → 不登记**。
  3. **P4 评审 I-5 append_event 非原子写 + fail-open**：P2 R7 已声明缓解（单任务单进程顺序写入）+ P2 明确"账本=辅助防线"取舍；CRITICAL-1 修复后逃生门动机消失。**三分法判定：已有设计声明覆盖 → 不登记**。
  4. **P7 [CODE_MAP_DRIFT]**（CODE-MAP.md 未登记 3 新文件）：已由补登记任务闭环（CODE-MAP.md 已登记 judge 机制族 + review-roles 11 个），**非债务**。
- `debt_check: reviewed`（留痕确认，见上）。

## 3. 版本号变更确认清单（主 Agent bump 时逐项执行）

| # | 引用文件 | 现状 | 变更动作 |
|---|---------|------|---------|
| 1 | `README.md` L5 version badge | `version-v0.58.0` | → `version-v0.59.0`（CHECK 7 校验对象，**必改**）|
| 2 | `README.zh-CN.md` L5 version badge | `version-v0.57.0`（**存量偏离**——TAG0019 发布 v0.58.0 时未同步 zh badge）| 建议本次一并 → `version-v0.59.0`（CHECK 7 目前只查 README.md；zh 同步与否由主 Agent 定，不同步则登记为存量偏移）|
| 3 | `CHANGELOG.md` | 头部为 `[0.58.0]`（无 [Unreleased] 块）| 头部新增 `[0.59.0]` 小节（草稿见 §6；如仓库约定含 [Unreleased] 则先改 [Unreleased] → [0.59.0]）|
| 4 | `agate/UPGRADING.md` | 最新章节 `### v0.58.0` | **新增 `### v0.59.0 — 独立 Judge 机制（无破坏性变更）` 章节**（草案见 §7）|
| 5 | git tag | `v0.58.0` | 新建 `v0.59.0` + `git push origin v0.59.0`（推送后 `git ls-remote --tags origin v0.59.0` 确认远端到达）|

> 版本 最终验证（G-5）：`git fetch origin && git describe --tags origin/main` == v0.59.0；`git merge-base --is-ancestor v0.59.0 origin/main` 返回 0。

## 4. 临时资源清单（供主 Agent READY 收尾检查清理）

| # | 资源 | 状态 | 清理动作/确认项 |
|---|------|------|----------------|
| 1 | 临时服务/进程 | **未启动任何临时服务/daemon/debug server** | 无需清理；确认 `ps aux | grep -E 'agate|pytest'` 无遗留进程 |
| 2 | pytest 临时 basetemp | `/home/kity/oclab/agate/.ptmp-scratch`（P3/P4/P5/P4 修复轮多次使用）| **已清理**（每轮验证后 rm -rf）；确认目录不存在 |
| 3 | 评审/复现 scratch | `/home/kity/oclab/agate/.ptmp-scratch/repro-*`（P4-review 复现、CRITICAL 复现实验）| 已随 basetemp 清理；无残留 |
| 4 | 测试端口 | 全程用 pytest `tmp_path` fixture，未绑定任何端口 | 无端口占用 |
| 5 | 开发安装 | **未执行任何 pip 安装**（pyyaml/pytest 为环境既有）| 无需卸载 |
| 6 | git 分支 | worktree `feat/TAG0020-independent-judge`（合并进 main 前常规状态）| 主 Agent 合并时处理；无独立残留分支动作 |

> 异常/回归修复期间运行的进程均已退出（单步串行 bash + timeout 90s 纪律，无后台长驻）。

## 5. 发布检查命令表（主 Agent 亲自执行，不委托 subagent）

> 源自 P2-design §5 gate_commands + P8 卡「gate 规则 / 主 Agent 必须亲自执行」。全部命令在 worktree 根（`/home/kity/oclab/agate/.worktrees/agate-TAG0020`）执行；bash 一律外层 timeout。

| # | 命令 | 预期 | 说明 |
|---|------|------|------|
| 1 | `/usr/bin/python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=agate-workspace/.pytest-tmp agate/tests/` | exit 0，failed==0 | P2 `gate_commands.P5`（全量）。**⚠️ DEBT0013 时序**：若链路含 consistency CHECK 7（badge vs tag），重跑安排在 bump + tag 创建**之后**，"bump 完成、tag 未建"中间态 CHECK 7 必 ERROR 是设计使然非回归 |
| 2 | `/usr/bin/python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | 0 ERROR | P2 `gate_commands.P5_consistency`；用 worktree 自身脚本（读 worktree 协议文件）；WARNING 不阻断 |
| 3 | `bash agate/tests/scripts/count-tests.sh` | 用例数 ≥ 749（基线）| P2 `gate_commands.P5_count_tests`；当前 1168，新增 5 回归用例后无漂移 |
| 4 | `/usr/bin/python3 agate/scripts/check-p6-provenance.py --audit7-only $TASK_DIR` | 读 `AUDIT7_RESULT:` 行判定 | P8 条件化 P5 复用：`reuse_allowed` → 复用 `P5-test-results/`；`reuse_blocked` / `no_reuse_claim_possible` → 完整重跑 #1（TAG0016 BDD-14 底线）|
| 5 | `git log v0.58.0..HEAD --oneline` | 对照 CHANGELOG [0.59.0] 小节无遗漏 | 逐条核对：judge 机制 + 账本 + 三档预算 + 历史兼容条目 |
| 6 | `git tag v0.59.0 && git push origin v0.59.0` | tag 创建 + 推送成功 | **主 Agent 亲自执行**；随后 `git ls-remote --tags origin v0.59.0` 确认远端到达 |
| 7 | 干净 checkout 跑 consistency | 0 ERROR | READY 收尾 D4：`git clone` 临时目录重跑（或确认 CI consistency job 对本次 PR 通过）——本地 worktree 的 `.worktrees` 路径过滤可能掩盖扫描问题 |

> P5 重跑确认（T027 纪律）：bump/tag 后 #1 全量重跑一次，确认 bump 未引入回归。

## 6. CHANGELOG [0.59.0] 小节草稿

```markdown
## [0.59.0] - 2026-08-22

### 新增（TAG0020：P6.5 独立 Judge 机制，RM-AG0032）

- **新评审角色 judge**（`assets/review-roles/judge.md`，所有任务强制）：P6 验收后、P7 之前以 fresh
  context 逐条重验**所有** BDD（含已 PASS 项，零挑验），只信 `P6-evidence/` 证据与 git log，不读
  verifier/implementer 自述——补 self-authored gate（P6/P7）的作者与裁判同信任链弱点（LIMITATIONS.md
  局限 3 缓解链）。
- **三层防造假**：① 信息隔离白名单（judge 的 dispatch-context 仅允许白名单输入，`check-judge-
  verdict.py` 机械校验黑名单路径引用集）② 证据交叉核对（BDD 计数对照「criteria_total == P1 标题数
  + 编号集零挑验」/ 证据存在非空 / md5 去重 / 引用对称）③ append-only 事件账本
  `gate-events.jsonl`（`agate_common.append_event` 单点写入，行间哈希链 + 时间戳单调，
  `check-events.py` 审计）。
- **新脚本**：`check-judge-verdict.py`（verdict 门槛判定九步链，通过后自记 `judge_verdict` 事件含
  `verdict_hash` 内容寻址——同一 verdict 被多处 gate 执行重跑不增轮次）、`check-events.py`（账本
  审计：哈希链完整 / ts 单调 / judge 复核轮次 ≤2 按 verdict_hash 去重）。
- **P6.5 状态机挂载**（候选 A）：P6 → P6.5（judge 复核）→ P7；`.state.yaml` phase 保持 P6 直至 P7
  （P6.5 非独立 phase 值，valid_phases/重试表零扩展）；`check-gate.py` 新增 `P6.5` 分支（judge
  未启用 → 早退跳过，历史兼容）；pre-commit-gate 2i.1 + ci-gate-backstop judge/events 兜底
  （commit-time 硬边界 + --no-verify 补跑）。
- **三档预算与诚实降级**：轮次 ≤2 / token 100k（`judge_token_budget` 可覆盖）/ 时间 30min；预算耗尽
  → `partial: true` + `status: needs-revision`（账本 `reason: budget_exhausted` 交叉校验），不静默
  放行。哲学红线保持：judge verdict 是行为描述输入，**机械核对（双脚本 exit 0）才是门槛**。
- 文档：state-machine / WORKFLOW / dispatch-protocol（Judge 信息隔离节）/ P6 卡片（P6.5 门槛）/
  dispatch-prompt（Judge 派发追加节）/ role-system（judge 登记，不进 C8）/ LIMITATIONS（局限 3
  缓解链）/ AGENTS（角色清单）/ CODE-MAP（judge 机制族）；CHECK 9 锚点 + `_DRIFT_SCRIPTS` 登记。
```

## 7. UPGRADING.md v0.59.0 章节草案（主 Agent 按此新增 `### v0.59.0` 节到「已知破坏性变更」表头下）

```markdown
### v0.59.0 — 独立 Judge 机制（无破坏性变更）

**本版本无破坏性变更，无需迁移动作。**

- 新增 P6.5 独立 Judge 复核（P6 验收后、P7 之前，所有任务强制）：新角色 `assets/review-roles/judge.md`
  以 fresh context 逐条重验所有 BDD（含已 PASS 项），只信 `P6-evidence/` 证据与 git log。
- 新增检查脚本 `check-judge-verdict.py` + `check-events.py`；`check-gate.py` 增加 `P6.5` 分支——
  **只对启用了 judge 机制的任务生效**（`.state.yaml` 含 `judge.enabled: true`）；历史任务/存量任务
  无该字段 → P6.5 全链自动跳过（含 gate、pre-commit 注入、CI backstop 三处守卫一致）。
- 新增 append-only 事件账本 `{AGATE_WORKSPACE}/tasks/{Txxx}/gate-events.jsonl`（`append_event`
  单点写入，随任务目录落库）——仅新增文件，不改变既有 `.state.yaml` / 产出文件语义。
- 记录：`judge:` 字段块（.state.yaml 可选，enabled/rounds/last_verdict/partial/
  judge_token_budget/double_judge）不入任何既有校验（agate-state-yaml-check 忽略未知顶层键）。
- 已有项目升级：`git pull` + 重跑 `python3 ~/.agate/scripts/install-hook.py`（Linux/macOS 符号链接
  模式自动跟随，不放心可重跑确认；Windows 复制模式必须重跑）。
```

## 8. releaser 边界声明

- 本文件未执行：bump-version（README/README.zh-CN badge 未改）、CHANGELOG 未写、UPGRADING 未写、
  git commit/tag 未创建——全部由主 Agent 在 P8 gate 验证通过后亲自执行（§3 清单 + §5 命令表）。
- 进度与发布明细已追加 `P8-progress.md`（同目录）。