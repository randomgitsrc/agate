---
phase: P8
task_id: TAG0005-mechanism-fixes
type: release
parent: P7-consistency.md
trace_id: TAG0005-mechanism-fixes-P8-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P8 发布准备记录 — agate 机制修复批（TAG0005）

> 合并发布模式（HANDOFF §8b）：TAG0005 与 TAG0009 同 worktree，合并为一次发布。
> 本文件是**发布计划文档**——声明 bump 计划 / debt_check / 临时资源清单 / 本任务 CHANGELOG 条目草稿。
> **不执行版本 bump、不 git commit/tag**（releaser 不执行；bump + tag + PR 由主 Agent 在 TAG0009 完成后统一执行）。

## bump_type

- **bump_type: minor**（v0.44.0 → **v0.45.0**）
- 判定依据（AGENTS.md 版本发布节 + dispatch-context 约束）：
  - TAG0005 为机制/契约缺陷修复 + 新增 C8 触发角色（backend 域 P2 评审 plan-eng-review）+ 新 gate 行为（P5 主/辅计数、check-debt exit 2）——含**行为变化**（新增评审触发），判 minor。
  - 若 TAG0009 也是 minor，合并后仍 v0.45.0；若 TAG0009 需 major，由主 Agent 统一裁决（本文件按 v0.45.0 计划）。

## 受影响包（P2-design.md frontmatter `packages`）

| 包 | 涉及改动 | P4 提交 | 验证 |
|----|---------|--------|------|
| agate-scripts-sh | check-gate.sh（P5 WARNING 主/辅文案）、agate-render-dispatch-prompt.sh（Review 指令条件注入）、check-debt.sh（依赖失败 exit 2）| 9aacf81 | P5 全量 bats + shellcheck 0 error |
| agate-scripts-py | agate-gate-p5-count.py（主/辅双值输出）| 9aacf81 | P5 全量 bats |
| agate-docs | role-system.md / rules/review-mapping.md / phase-cards/P2-design.md（三处 C8 表）、dispatch-protocol.md（空返回策略）、assets/templates/dispatch-prompt.md（Review 指令独立块）、scripts/README.md | 9aacf81 | consistency 0 ERROR --strict |
| agate-tests | check-gate.bats / agate-gate-p5-count.bats / agate-render-dispatch-prompt.bats（RP.17-19）/ agate-debt-check.bats（BDD-16）/ tests/README.md 计数表 | b0c2475 + 9aacf81 + 89331a1 | P5 全量 bats 726 ok |

> 合并发布时四包随同一个版本 bump（agate 协议本体单版本号，非逐包独立版本）。

## 版本号变更确认（计划，非已执行）

- 当前版本：**v0.44.0**（README badge L6 + git tag v0.44.0，已核实）
- 计划新版本：**v0.45.0**（合并发布时执行）
- 需更新的版本引用（合并发布时由主 Agent 执行，参考 AGENTS.md 版本发布节 + 版本引用文件清单）：
  - README.md version badge（L6 v0.44.0 → v0.45.0；另 L32 有一处残留 v0.43.0 badge，建议一并核对是否残留）
  - CHANGELOG.md `[Unreleased]` → `[0.45.0]`
  - UPGRADING.md 新增 v0.45.0 升级章节（含 backend 域 P2 评审触发行为变化——影响所有已部署项目）
- 本任务不执行，全部留待合并发布。

## debt_check

- **debt_check: none**
- 核对过程：读取 `agate-workspace/debt/tech-debt.md`——worktree 中该文件**不存在**（`agate-workspace/` 仅 archived/roadmap/tasks 三个子目录，无 `debt/`）。本任务为机制/契约修复，P1-P7 均无 `source: retreat` 回退提交、无 [SCOPE+] 增补、无技术债登记条目（P4-implementation.md §DESIGN_GAP/SCOPE+ 声明为空）。无关注项，合法选项 `none`。

## 本任务变更摘要（CHANGELOG 草稿，供合并发布写入 CHANGELOG.md）

> 合并发布时主 Agent 将本节内容合并进 CHANGELOG.md 的 `[0.45.0]` 版本条目（与 TAG0009 条目并列）。

### 修复（TAG0005 agate 机制修复批：4 个已核实机制/契约缺陷）

- **RM-AG0010 C8 表补 backend 域 P2 评审**：role-system.md / rules/review-mapping.md / phase-cards/P2-design.md 三处 C8 映射表 backend 行新增 `plan-eng-review（P2 方案评审）`（保留既有 `review（P4 后）`），并附去重说明（同任务命中同一评审角色只派发一次）——消除「P2 gate 强制要 P2-review.md 但 C8 无触发角色 → 主 Agent 被迫自造评审」契约矛盾；check-gate.sh P2 分支未改（无条件要求保留）
- **RM-AG0011 P5 gate_commands 主/辅命令计数语义**：`agate-gate-p5-count.py` 输出改单行双值 `{main} {aux}`（main 精确匹配 `P5:`、aux 为 `P5_*` 且排除 `_formatter`，与 read-p5-commands.py 执行枚举对齐）；check-gate.sh P5 WARNING 文案改为「X 个主命令 + Y 个辅助命令（共 Z 条 gate_commands.P5 命令）」；仅 P5 无辅助命令时不 WARNING（行为不变）
- **RM-AG0012① Review 角色特别指令按角色类型条件注入**：`assets/templates/dispatch-prompt.md` 将「Review 角色特别指令」从主代码块拆为「## 阶段特定提示」下独立子块；`agate-render-dispatch-prompt.sh` 按 `ROLE_DIR=review-roles` 追加该节（组装顺序 main_block → review_appendix → 阶段 appendix）——执行角色派发 prompt 不再含 status draft→approved 评审语义，评审角色含完整语义
- **RM-AG0012② render 角色文件不存在 exit 2 回归锁定**：行为 v0.23.0 已修复（exit 2 + stderr 报错），本任务新增 RP.17 bats 测试锁定
- **RM-AG0003 空返回自动重试（增量增强）**：dispatch-protocol.md 空返回恢复策略「第 1 次空返回」新增步骤 a——相同 prompt 原样自动重试一次（不占用 retries[Pn] 槽位），会话时长 <1min 输出「会话时长异常短」告警；自动重试仍空返回才进入既有 retries[Pn] 流程；「相同 prompt 直接重试」禁令的唯一豁免（仅限首次/单次/原样重发）；retry 上限/PAUSED 规则未改
- **同类扫描守卫 / check-debt.sh 依赖加载失败 exit 2**：`check-debt.sh --retreat-coverage` 依赖 agate-workspace-resolve.sh 加载失败（source 失败或文件缺失）从「stderr 报错但 exit 0」改为 **exit 2**（需主 Agent 自判，与 check-gate.sh 约定一致）；「无 retreat 提交」有意跳过分支保持 exit 0；`rg '>&2;\s*exit 0' agate/scripts/*.sh` 仅剩 3 处「跳过」语义（agate-capture-env-baseline.sh）

### 测试（TAG0005 配套）

- 新增/同步 bats 用例：RP.17/18/19（render 条件注入 + exit 2 回归）、GPC.1-3（主/辅计数）、G5_CMD.1-5（WARNING 文案）、test_bdd_16（check-debt 依赖缺失）+ 文档断言（BDD-1/2/9/12-15）；全量 726 ok（714 基线 + 12 新增）
- agate/tests/README.md 计数表同步（render 16→20；check-gate 100→124；agate-gate-p5-count 2→3）

### 文档

- 三处 C8 表去重说明 / dispatch-prompt.md 模板结构调整 / dispatch-protocol.md 空返回策略与内联模板评审语义备注 / scripts/README.md check-debt 描述同步

## 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务为纯文档 + 脚本/gate 修改，P4/P5 阶段未启动任何临时服务/进程，未创建临时数据，未做开发安装。逐项核对：

- **临时服务/进程**：无（P4/P5 自查均为 bats / shellcheck / consistency 本地命令，无 debug server / daemon 启动）
- **临时数据**：无（无测试数据库、无临时文件目录；P6-evidence/ 与 P5-test-results/ 为阶段产出物，属任务目录内正常产物，随任务归档，不需单独清理）
- **开发安装**：无（未做 editable install / 全局包安装；bats 1.10 / python3 3.12+pyyaml / shellcheck 均为既有环境）
- **端口占用**：无（无网络监听服务）
- **工作区残留**：worktree `agate-TAG0005-0009` 本身为隔离开发环境，合并发布完成后由主 Agent 按常规流程处理（merge + 清理）

## 合并发布注意事项（主 Agent）

- bump 版本引用三处：README badge / CHANGELOG / UPGRADING.md 新章节（AGENTS.md 版本发布节固化清单）
- release PR 用普通 merge（`--no-ff`），禁 squash merge（`agate-summary.sh` 依赖 `git describe --tags`）
- 合并发布时重跑 P5 gate（bats 726 全绿 / consistency 0 ERROR / shellcheck 0 error）确认 bump 后仍绿
- CHANGELOG 对照 `git log v0.44.0..HEAD --oneline` 无遗漏（TAG0005 13 提交 + TAG0009 提交）
- `debt_check: none` 为合法选项，不阻断发布

## 环境隔离

`[PROD_NOT_TOUCHED]`——本阶段仅读取 worktree 内产出文件与 git log/status 核验，未接触生产环境。
