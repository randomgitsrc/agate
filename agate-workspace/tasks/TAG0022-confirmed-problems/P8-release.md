---
phase: P8
task_id: TAG0022-confirmed-problems
type: release
parent: P7-consistency.md
trace_id: TAG0022-P8-20260822
status: draft
created: 2026-08-22
agent: implementer
---

# P8 发布准备 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 状态标记：[PROD_NOT_TOUCHED]（只读消费稳定版 `~/.agate` 与主 checkout；写操作全部落在 worktree `agate-workspace/` 内；worktree `agate/` 协议文件为本任务改造对象，属正常改动面）
> 本文件为发布**准备**（建议清单），**不执行** git commit / git tag / version 文件修改 / CHANGELOG 写入——均由主 Agent 在 P8 gate 验证通过后亲自执行。
> 上游：P7-consistency.md（审查通过）/ P2-design.md（packages=[agate] + gate_commands）/ P1-requirements.md（BDD-1..10）
> 现状：README badge v0.60.0 / CHANGELOG [0.60.0] 为顶节（无 [Unreleased]）/ UPGRADING v0.61.0 章节 ① 完整 + ②③ 占位

---

## 1. bump_type

**`bump_type: minor`**

**理由**（逐改动面按 P8 bump 规则判定）：

| 改动面 | 性质 | 兼容性判定 |
|--------|------|-----------|
| RM-AG0037 ruff 合并强制 | CI 门禁配置：workflow `ruff` job 锁 `ruff==0.16.4` + job name 固化 + required check 配置步骤文档（UPGRADING ① / AGENTS.md step 5） | 无脚本行为变化；已部署项目零动作（UPGRADING ①「升级动作：无」）；required 勾选是维护者配置 |
| RM-AG0038 check-gate 权威源切换 | 内部重构：check-gate.py A/B/C/D 组 md/grep 解析迁 `agate_common` 共享读取器 + `agate-md-field-get` 新 op（status/agent/project_phase/code_map_*/created）；S-3 双向收紧（YAML↔卡片 gate 命令一致性） | **读取方式变、判定口径不变，well-formed 等价**；旧格式任务 md 靠双轨回退（frontmatter 优先 + 正文回退）向后兼容——与 v0.60.0 M2（同型「切权威源 + 判定语义逐字节等价」，当时判 **minor**）为直接先例 |
| RM-AG0039 judge 新任务强制 | gate 行为变化：机制后新任务（P1 `created` ≥ `judge_required_since: "2026-08-22"`）P1 gate 缺 `judge.enabled: true` → **exit 1 阻断** | **历史任务跳过**（created < 截止 / 未声明 → fail-open 跳过，对齐 gate_p65 历史兼容语义）；存量进行中任务零影响；只对「机制后新任务」增加启用要求，非存量破坏 |
| RM-AG0041 M15 opt-in 排除钩子 | 新增 env `AGATE_CONSISTENCY_SKIP_DIRS`（iter_md_files 排除，默认关闭） | **默认关闭 → 行为逐字节不变**（R6 缓解）；测试侧根治（test_bdd_7 GIT_CEILING_DIRECTORIES / test_bdd_25 位置感知），无用户行为变化 |
| RM-AG0040 M3 实证计划 | 文档交付（P2 §4.4 四要素 + 触发条件），无代码改动 | 无 |

**结论**：
1. **存量破坏面 ≈ 0**——五项全部向后兼容（历史任务跳过 / 正文回退 / 默认关闭 / 纯配置+文档 / 纯文档）。
2. **RM-AG0038 与 v0.60.0 M2 同型**（都是「规则读取从 md 切 YAML 权威源、判定口径不变、well-formed 等价」），v0.60.0 判 minor 是仓库内直接先例，本任务同判 minor 保持一致。
3. **UPGRADING 章节版本号不冲突**：UPGRADING v0.61.0 章节已按 v0.61.0 预写（含「本版本含破坏性变更」声明）——本仓库对 minor 版本同样维护「破坏性变更」节（v0.60.0 即 minor + 破坏性变更节）：该节作用是**列出升级者需对照的行为变化**（RM-AG0038 权威源切换 / RM-AG0039 新任务强制），不自动触发 major；major 仅当**存量任务/已部署项目**被破坏时才需要（本任务不满足）。
4. **非 minor 情形（供主 Agent 复核）**：若仓库版本策略把「任何脚本行为变化（即使向后兼容）」一律视为 major，则应改判 major——但 v0.60.0 先例与 UPGRADING 预写均不支持该口径，本文件按 minor 建议。

---

## 2. debt_check

**`debt_check: reviewed`**

已读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（682 行，check-debt 可校验格式）并逐条核对：

- **open 条目（10 条，全部核对）**：DEBT0002（compute_sha256 双实现）/ DEBT0003（manifest 未签名）/ DEBT0004（卸载引用扫描限流）/ DEBT0007（test_check_pruning 依赖真实暂存区）/ DEBT0008（ABS_PATH_RE 中文误伤）/ DEBT0014（Windows Store 占位符，closure_criteria 5 待 Windows CI matrix）/ DEBT0015（env_constraints 声明性无 gate 绑定）/ DEBT0016（gate_p4 CODE-MAP 本地路径推导）/ DEBT0017（gate_p4 子串判定假阴性）/ **DEBT0018（本任务 P4-review INFORMATIONAL #2 登记：check-gate.py agate_common import 降级 stub 返回 0/空 → 安装破损边缘 false-PASS）**。
- **与本任务改动面直接相关的 open 债**：DEBT0018——与 RM-AG0038 迁移新增的共享读取器依赖（count_p7_markers/count_p6_pass_fail/count_code_map_lines）同面；P4-review 采纳「登记本债（低优先）」路径（Fix 建议为后续改 fail-closed），**本任务不修**（评审定案，非遗漏）。DEBT0016/DEBT0017 均涉 check-gate.py gate_p4 的 CODE-MAP 判定——RM-AG0038 迁移后该两债仍在（迁移未改 gate_p4 CODE-MAP 路径推导与子串判定），未纳入本任务 BDD（P2 §1.2 N6 延伸面）。
- **closed 条目**：DEBT0013（P8 时序注意）与本任务 P8 直接相关——P8 卡 gate 规则已含「⚠️ 时序注意（DEBT0013）」，本文件 §7 发布检查命令中落实。
- **结论**：无 open 债阻塞发布（P8 卡 BDD-17：债务未关闭不阻断）；debt_check 留痕为 reviewed。

---

## 3. 版本号变更确认（v0.60.0 → v0.61.0）

P2 packages=[agate] 为单一版本单元（P1 §packages / P2 §packages 一致，P7 §3.1 核对）。bump 目标 **v0.61.0**（与 UPGRADING 预写章节一致）。变更点清单（主 Agent 发布时逐项执行）：

| # | 文件 | 变更 |
|---|------|------|
| 1 | `README.md` L5 | version badge `v0.60.0` → `v0.61.0` |
| 2 | `README.zh-CN.md` L5 | version badge `v0.60.0` → `v0.61.0`（中文镜像同步） |
| 3 | `CHANGELOG.md` | 顶部 `[0.60.0]` 节之上**新增 `[0.61.0] - 2026-08-22` 节**（现无 `[Unreleased]`——P8 卡「CHANGELOG [Unreleased] → 新版本号」语义以新增版本节替代；条目建议见 §4） |
| 4 | `agate/UPGRADING.md` | v0.61.0 节已预写（① 完整），发布时**补齐 ②③ 占位小节**（清单见 §5，主 Agent 亲自执行） |
| 5 | version 文件 | **无**（仓库无 `agate/version*` / `VERSION*`，已确认；不涉及） |
| 6 | 稳定版引用 | grep 全树（README/README.zh-CN/docs/agate，排除 UPGRADING/CHANGELOG/agate-workspace 历史数据）：`v0.60.0` 硬编码仅 README badge 两处——无其他「当前版本」写死引用需更新（文档按 AGENTS.md 约定写「稳定版」不写死版本号） |

---

## 4. CHANGELOG 更新确认（[0.61.0] 节条目建议）

> 建议条目按本任务 5 子项（RM-AG0037~0041）+ 计数 + 破坏性变更指针组织；主 Agent 写入时可调整措辞，勿丢内容。

```
## [0.61.0] - 2026-08-22

### 新增（TAG0022：质量门禁与迁移收尾批，RM-AG0037~RM-AG0041）

- **ruff 合并强制（RM-AG0037）**：CI `ruff` job 锁版本 `ruff==0.16.4`（与本地开发环境
  `~/.venvs/agate-dev/bin/ruff` 对齐）+ job name 固化 `ruff`（可被 GitHub 分支保护按 check 名引用）；
  UPGRADING/AGENTS.md 写入「将 ruff 设为 PR required check（维护者在仓库设置勾选）」配置步骤——
  TAG0019/20 曾带 23/12 处违规合并的复发防线（required 勾选为维护者配置，非实现侧动作）。
- **check-gate 权威源切换闭环（RM-AG0038，M2 二期）**：check-gate.py 协议规则类 md/grep 解析清零——
  A 组 frontmatter 字段改走 `agate-md-field-get` 新 op（status/agent/project_phase/code_map_*/created）、
  B/C/D 组标记与产出格式判定迁 `agate_common` 共享读取器单点（判定口径不变、well-formed 等价、旧格式
  正文回退保留）；S-3 双向收紧（S-3a YAML→卡片、S-3b 卡片→YAML 的 gate 命令一致性，md 禁止承载
  可判定规则）——「YAML 权威、md 禁止承载可判定规则」落地（破坏性变更见 UPGRADING v0.61.0 ②）。
- **judge 启用强制化（RM-AG0039）**：check-gate P1 新增 judge 校验——机制后新任务（P1 `created` ≥
  `judge_required_since: "2026-08-22"`）缺 `.state.yaml` 的 `judge.enabled: true` → exit 1 阻断；
  历史任务（created < 截止或未声明）跳过（向后兼容，与 gate_p65 历史语义一致）；state-machine /
  P1 卡模板语义同步（破坏性变更见 UPGRADING v0.61.0 ③）。
- **ceremony: thin 实证收尾（RM-AG0040）**：M3 实证执行计划 + 触发条件落盘（P2 §4.4：评审轮数 /
  真实发现数 / TAG0018 基线 / 不达标回滚 standard / 触发条件 = 下一 low 薄任务），薄任务实战后产出
  对比报告。
- **环境假象测试根治（RM-AG0041）**：test_bdd_7 改 `GIT_CEILING_DIRECTORIES` 注入确定化非 git
  上下文；test_bdd_25 改位置感知 + `check-protocol-consistency.py` `iter_md_files` 新增 opt-in
  排除钩子 `AGATE_CONSISTENCY_SKIP_DIRS`（默认关闭、行为不变）——任意 basetemp 位置全量 0 失败
  （TAG0020/21 反复复现的 2 条 known-failures 根治）。
- 新增 13 测试用例（count-tests 1202 → 1215）；全量 pytest 1213 passed / 2 skipped / 0 failed
  （P5/P6 双位置验证）；consistency 0 ERROR；structure S0-S6 0 漂移；ruff×2 0 违规。

### 破坏性变更

见 `agate/UPGRADING.md` v0.61.0 节：① ruff job 锁版本 + required check 配置步骤（纯 CI 配置 +
文档，无升级动作）② check-gate 规则读取切 YAML 唯一权威源（判定口径不变、旧格式任务靠正文回退，
对账兜底行为见 UPGRADING）③ 机制后新任务 P1 强制 `judge.enabled: true`（历史任务跳过）。
```

> 对照口径：`git log v0.60.0..HEAD --oneline` 共 14 commits——10 个 `wf(TAG0022-*)`（P0..P7，上表全覆盖）+ 4 个 docs-only（b88fb92 TAG0021 READY 收尾 / e30690f PR#185 merge / cc034be roadmap docs / bde3bfd PR#186 merge，均无产品代码，属非用户面文档变更，CHANGELOG 以本任务 5 子项覆盖即可；主 Agent 核对时确认这 4 个提交 diff 无产品代码即可放行）。

---

## 5. UPGRADING ②③ 补齐清单（主 Agent 亲自执行写入——AGENTS.md 版本发布清单 step 3 强制，v0.44.0 教训；protocol-alignment-review HUMAN_CONFIRMED A5 确认项）

> 现状：`agate/UPGRADING.md` v0.61.0 节 ②③ 为占位（本任务 P4 批实现时无法写入——②③ 的「合并发布前补齐」由主 Agent 在 P8 亲自落笔，protocol-alignment-review 将该动作标为 HUMAN_CONFIRMED A5，commit d66c848 记录「6 ALIGNED 1 HUMAN_CONFIRMED（A5 UPGRADING P8 补齐）」）。以下为补齐要点（依据 P2 §4.2/§4.3 与实现 diff 整理，主 Agent 可按 UPGRADING 既有格式扩写，须含影响面 / 升级动作 / 兼容兜底三要素）。

### ② RM-AG0038 权威源切换（替换占位块）

- **影响面**：`check-gate.py`（P1/P2/P6/P7/P6.5 分支的协议规则类 md/grep 解析点清零）+ `agate_common.py`（新增共享读取器：count_markers / extract_bdd_titles / parse_ui_design_section / count_p6_pass_fail / count_p7_markers / count_design_gap / count_code_map_lines / parse_fail_list_block / count_kf_entries / extract_embedded_yaml_blocks 等）+ `agate-md-field-get.py`（新 op：status / agent / project_phase / code_map_new_files_count / code_map_reviewed_count / created）+ `check-structure-consistency.py`（S-3 双向收紧：S-3a YAML→卡片、S-3b 卡片→YAML 的 gate 命令一致性）+ `agate/rules/phases.yaml`（各阶段 gates[].check 增补实际命令串）。`.state.yaml` 读取与 git/CHANGELOG 输出解析（E/F 组）不在迁移面。
- **行为变化**：协议可判定规则声明**只从 `rules/*.yaml` 读取**，协议 md / phase-cards 中新增可判定规则（如 gate 命令行）不再被脚本消费——S-3 双向检查拦截 md 侧新增规则未入 YAML（ERROR）。任务产出文件（P1/P2/P6/P7 格式判定）读取走共享读取器，**判定口径与旧版逐字节等价**。
- **升级动作**：`git pull` + 重跑 `install-hook.py` 即可；**无存量任务迁移动作**——旧格式任务产出（无新字段）靠共享读取器正文回退，语义不变（「不动则无感」原则保持）。
- **对账兜底行为**：迁移保留双轨（frontmatter 优先 + 正文回退），旧正文格式任务可照常跑 gate；无 RECONCILE 差异告警面（不同于 v0.60.0 M1 对账——本版本为判定口径等价迁移，无对账叠加）。

### ③ RM-AG0039 judge 强制化（替换占位块）

- **判据**：`agate/rules/dispatch.yaml` 新增 `judge_required_since: "2026-08-22"`（机制发布日，ISO）；`check-gate.py` gate_p1 读 `.state.yaml` judge 块 + P1 frontmatter `created` + rules 截止日期。
- **判定语义**：机制后新任务（`created` ≥ `2026-08-22`）缺 judge 块或 `judge.enabled` 非 true → **P1 gate exit 1 阻断**（fail-closed，stderr 提示「机制后新任务须在 .state.yaml 写 judge.enabled: true」）；含 `judge.enabled: true` → 原语义放行；历史任务（created < 截止 / created 缺失或非 ISO）无 judge 块 → **跳过不被拦**（fail-open，兼容存量）。
- **升级动作**：进行中任务（created < 2026-08-22）零动作；**新任务 P1 初始化必须写 `judge.enabled: true`**（P1 卡产出规格已加 checklist，state-machine L442-443 模板语义已同步）；机制后存量任务若 P1 缺 judge 块且 created ≥ 截止，需补写 judge 块再推进。
- **不动面**：P6.5 消费链（pre-commit-gate 2i.1 / ci-gate-backstop / gate_p65 早退语义）逐字节不变。

---

## 6. 临时资源清单（releaser → 主 Agent READY 收尾交接）

**结论：无残留**。本任务无临时服务 / 进程 / 端口 / 开发安装启动（P1 §9 声明 + P4/P5/P6 记录一致：无 debug server、无数据库、无 pip 安装——ruff 用既有 `~/.venvs/agate-dev/bin/ruff`，pytest/pyyaml 为环境既有）。曾创建并已清理的临时数据（供主 Agent 逐项核对）：

| # | 路径 | 用途 | 清理确认 |
|---|------|------|---------|
| 1 | `<worktree>/agate-tmp-bt-sim/` | P4 D 批仓库内 basetemp 模拟（ptpollute 注入坏引用验证 M15 排除链） | P4-implementation.md L151/155「测后 rm -rf 已确认不存在」 |
| 2 | `<worktree>/agate/.bt-p5-inrepo/` | P5 全量 pytest 位置 2（仓库内 basetemp） | P5-progress.md L28/L42「rm -rf 确认无残留」 |
| 3 | `<worktree>/agate/.bt-p6-verify/` | P6 BDD-9 全量 pytest 位置 2（仓库内 basetemp） | P6-progress.md「跑完 rm -rf 已清理」；本次 P8 复核 `ls` 不存在 ✓ |
| 4 | `<worktree>/agate/.bt-fix/` | P4 回退修复（f724e48）位置 2 全量验证 basetemp | P4-progress.md L184「BTFIX GONE」 |
| 5 | `/home/kity/oclab/dsh-workspace/ptpollute.py` | P4 D 批 pytest 污染注入插件（验证用，**非交付物**，仓库外 dsh-workspace 临时资源） | 任务文档未记录删除——**主 Agent READY 收尾核对**：存在则可删除（`rm -f /home/kity/oclab/dsh-workspace/ptpollute.py`）或保留（不影响仓库） |
| 6 | `/home/kity/oclab/dsh-workspace/ptmp/` | 权威仓库外 basetemp（N2 实证冻结，全阶段 pytest 输出目录） | pytest 自动管理；仓库外可写位置，保留供后续任务复用（非本任务污染） |

**主 Agent READY 收尾核对命令建议**：`ls <worktree>/agate-tmp-bt-sim <worktree>/agate/.bt-p5-inrepo <worktree>/agate/.bt-p6-verify <worktree>/agate/.bt-fix`（应全部不存在）+ `git status`（应干净，仅 gate-events.jsonl 正常 append 与任务产出未跟踪文件）+ `ps aux | grep -E 'pytest|ptpollute'`（无遗留进程）。

---

## 7. 发布检查命令核对建议

> 主 Agent P8 gate 后逐项亲自执行（不可委托）。命令以 P2 gate_commands（§6）与 AGENTS.md 版本发布清单为准。

1. **P8 gate**：`python3 agate/scripts/check-gate.py P8 $TASK_DIR`（bump_type / debt_check / version 文件变更 / CHANGELOG 变更四要素——version 与 CHANGELOG 变更在 bump 后进暂存区时判定）。
2. **版本变更**：README/README.zh-CN badge v0.61.0 + CHANGELOG 新增 [0.61.0] 节（§3 清单逐项）。
3. **CHANGELOG 无遗漏对照**：`git log v0.60.0..HEAD --oneline`（当前 14 commits：10 个 wf(TAG0022-*) + 4 个 docs-only）逐条对照 [0.61.0] 节（§4 覆盖说明）；对 docs-only 4 条确认 diff 无产品代码。
4. **P5 验证重跑（DEBT0013 时序注意）**：`gate_commands.P5`（全量 pytest `--basetemp=/home/kity/oclab/dsh-workspace/ptmp -p no:cacheprovider`）+ `P5_consistency`（`check-protocol-consistency.py --strict-errors-only`）+ `P5_structure` + `P5_ruff` + `P5_count`——**必须在 `git commit + git tag v0.61.0` 之后重跑**，避免 CHECK 7（badge v0.61.0 ≠ tag v0.60.0）时序性 ERROR；P5 复用条件：先跑 `check-p6-provenance.py --audit7-only $TASK_DIR` 读 `AUDIT7_RESULT` 行（reuse_allowed → 复用 P5-test-results/；否则完整重跑）。
5. **tag 创建 + 远端验证**：`git tag v0.61.0 && git push origin v0.61.0`（**显式推 tag**，`git push` 不推送 tag——v0.51.0 教训）；随后 `git ls-remote --tags origin v0.61.0` 必须显示该 tag。
6. **release PR 合并**：必须普通 merge（`--no-ff`），**禁止 squash merge**（agate-summary.py `git describe --tags --abbrev=0` 依赖 tag 为 HEAD 祖先——v0.31.0 事故）；合并后 G-5 验证：`git fetch origin && git describe --tags origin/main` == v0.61.0 + `git merge-base --is-ancestor v0.61.0 origin/main` rc=0 + 合并后 push 的 CI 全绿（含 consistency job）。
7. **CI ruff job required check 验证（RM-AG0037 本任务主题）**：合并前确认分支保护已勾选 ruff，或在第 5 步后验证 CI ruff job 绿（ruff==0.16.4 锁版本与本地 `~/.venvs/agate-dev/bin/ruff` 对齐）——防 ruff 违规合并复发（TAG0019/20 教训）。
8. **干净 checkout consistency（P8 卡 READY 检查，TAG0001-0003 D4 教训）**：`git clone` 临时目录跑 worktree 的 `check-protocol-consistency.py` 0 ERROR（本地 worktree `.worktrees` 路径过滤会掩盖扫描问题）；若不可 clone，至少确认 CI consistency job 对 release PR 通过。
9. **CI 失败诊断纪律（E-3）**：本地绿 CI 红 → 先拉 job 日志（`gh api repos/{owner}/{repo}/actions/jobs/{id}/logs`）看真实 FAIL 归属，禁止臆测；CHECK 7 FAIL 第一排查项 = `git ls-remote --tags origin v0.61.0`。

---

## 8. Lessons Learned（供主 Agent 汇入 `docs/notes/lessons.md`，类别 / 教训 / 来源任务 / 日期）

1. **流程**：同文件多轮大改（check-gate.py 同时承载 RM-AG0038 迁移 + RM-AG0039 校验）靠「批序错开 + 非重叠改动块」（Wave1 C 先 → Wave2 B 串行叠加）实现零冲突——「同簇互扰任务分批错开同一文件」可复用为 P2 批次设计的标准判据。
2. **测试**：BDD-9 双位置验证额外捕获第 3 个环境假象（test_tag0005_bdd_9 的 rglob 依赖 basetemp，非 test_bdd_7/25 独有）——「任意 basetemp 位置全量 0 失败」作为验收锚的价值 = 暴露所有同类位置依赖，而非仅修已知两条。
3. **流程**：环境假象根治（M15 opt-in 排除钩子 + GIT_CEILING_DIRECTORIES 确定化）使「仓库内 basetemp 全量 0 失败」从「登记 known-failures + 人工复排」升级为「可重复机械验证」——根治优于登记，后续任务无需再为同一类位置依赖消耗排查成本。

---

## 9. 交接摘要（给主 Agent）

- bump_type=minor（存量兼容面≈0；RM-AG0038 与 v0.60.0 M2 同型先例）；debt_check=reviewed（10 open 核对，DEBT0018 为本任务登记、不阻塞）；CHANGELOG [0.61.0] 条目按 5 子项建议（§4）；UPGRADING ②③ 补齐要点清单（§5，主 Agent 亲自写）；临时资源无残留（§6，含 ptpollute.py 核对项）；发布检查命令核对建议（§7）。
- 本任务全部产出 commit 均含 SELF-GATE 触发文件（CI/check-gate/state-machine/P1 卡/测试）——release commit 的 commit message 须含 `self-gate-review: <路径>`（本任务已做 protocol-alignment-review，路径 `docs/reviews/agate-alignment-review-2026-08-23-TAG0022.md`）或 `self-gate-skip: <理由>`。
