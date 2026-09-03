---
agent: implementer
phase: P8
task_id: TAG0030
type: release
parent: P7-consistency.md
trace_id: TAG0030-P8-20260904
status: draft
created: '2026-09-04'
bump_type: minor
---
# P8-release — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）发布准备

> parent: P7-consistency.md（approved：blocker_count=0 / deviation_count=0 /
> design_gap_count=0 / CODE-MAP_SYNC / BDD 21↔P6 21 逐条对应 / 未决项清零）
> 本文件由 releaser subagent（implementer P8 模式）产出，只做发布准备——已按派发指引更新
> README badge 与 CHANGELOG 版本号行，**不执行 git commit / git tag / bump-version 脚本**
> （这些由主 Agent 在 gate 验证后亲自执行）。
> 环境隔离：[PROD_NOT_TOUCHED]（全程只读分析 + 产出 P8-release.md / P8-progress.md +
> 更新三个版本引用文件，未触碰生产面/未启动任何服务进程）。

## 1. bump_type 建议与理由

**bump_type: minor**（最新 tag v0.67.2 → 目标 v0.68.0）

理由（逐条，对齐 dispatch-context 判定规则与 P8 卡「版本 bump 判定」）：

1. **协议机制新增（semver minor 主判据）**：本任务为**协议机制补强批**，纯协议文档面改造——
   ① P3/P4 卡新增创建型测试清理钩子条文（afterEach 清理队列模式）；② P1 卡/analyst 角色新增
   人工体验验收节（seed 数据 → 页面有内容 BDD）；③ plan-design-review 形态驱动化（先读
   `ui_render_shape` 再加载维度组评分细则 + 布局方案 ≥2 候选必审）；④ 视觉契约可表达子集
   （五类 DOM 度量）收录 architect/verifier 指南；⑤ DEBT0024/25/26 三连约定（真实 gate 语义 /
   新增 CHECK 先全量扫描 / 拆小默认指导）——属 "new backwards-compatible functionality" → minor。
2. **向后兼容性已客观验证（非 major）**：未改 `.state.yaml` schema / 未改 gate 返回约定 /
   未改 3 个 hook 薄壳（UPGRADING v0.68.0 节行 94-96 声明 + P7 改动面核对无 `.sh`）；plan-design-review
   的 0-10 评分与 status 门槛映射原文保留，无形态声明回落布局型默认 → 非 major。
3. **非 bugfix 批次 / 非 hotfix**：本任务不是 patch 级修复，是机制新增批 → 非 patch。
4. **版本载体**：单仓单版本，无独立包 version 文件（README badge / CHANGELOG / UPGRADING 三处
   一致为准）；P2 frontmatter `packages: [agate-phase-cards, agate-assets-roles,
   agate-assets-templates]` 三包面共享同一协议仓库版本号，无多版本文件 → P8 卡「多包发布拆批」
   不触发，无需合并 subagent。

## 2. debt_check

**debt_check: reviewed**

已读 `agate-workspace/debt/tech-debt.md`（DEBT0024/0025/0026，TAG0027 复盘登记，2026-09-04 实读），
三条 closure_criteria 均实证满足（grep 锚词，非凭记忆）：

| id | closure_criteria（tech-debt.md 原文） | 实证锚词（worktree 实测） | 满足 |
|---|---|---|---|
| DEBT0024 | 协议测试设计约定写明「gate 消费方测试夹具须走真实 gate 语义」 | `agate/tests/README.md:117`：「写 gate 消费方测试夹具 → **必须走真实 gate 语义**（真实执行 gate 脚本并按真实 exit code 断言），不得 stub/mock 假 exit（DEBT0024）」 | ✓ |
| DEBT0025 | 协议开发约定写明「新增 CHECK 上线前先全量扫描存量」 | `AGENTS.md:19`：「新增 CHECK 上线前先全量扫描存量：新增 CHECK/规则前，先对既有协议文档与数据面做全量扫描，确认新规则不误伤存量条文（DEBT0025）」 | ✓ |
| DEBT0026 | 派发模板补「>5 文件/大文档类任务按体量评估拆小」默认指导 | `agate/assets/templates/dispatch-context.md:33`：「拆小默认指导条目位：单 agent 派发改动体量 >5 文件或大文档时，主 Agent 应先评估是否拆小（外部拆小兜底，与 subagent 内部自主拆互补）」 | ✓ |

- 结论：`debt_check: reviewed`——关联 DEBT0024/0025/0026 closure_criteria 均已满足（对应
  P1§BDD-19/20/21，P6 PASS 21/21 + P6.5 judge 独立复核 passed）；三条目在 tech-debt.md 的
  status 字段由主 Agent 按惯例关闭（releaser 不写 tech-debt.md）。其余 open 债务与本任务
  改动面无交集，均不阻断发布。

## 3. 版本号变更确认（三处一致）

| 项 | 现状（实测 2026-09-04） | 目标 | 状态 |
|---|---|---|---|
| 最新 git tag | v0.67.2（`git describe --tags --abbrev=0` 实测） | v0.68.0（主 Agent 创建并推送） | 待主 Agent |
| README.md version badge（:12） | v0.67.0 | v0.68.0 | **本文件已更新** |
| README.zh-CN.md version badge（:12） | v0.67.0 | v0.68.0 | **本文件已更新**（中文镜像同批，TAG0028 先例） |
| CHANGELOG.md | [Unreleased] 节（P4 e39c897 已写四 phase 条目） | [0.68.0] - 2026-09-04 | **本文件已更新** |
| agate/UPGRADING.md | v0.68.0 节存在（行 92-112：无破坏性变更声明 + 四 phase 摘要，P4 落笔） | 确认存在 | ✓ 已确认，无需改动 |

- 版本号变更确认：README badge 已 v0.67.0 → v0.68.0（README.md + README.zh-CN.md 两处）；
  CHANGELOG 已 [Unreleased] → [0.68.0] - 2026-09-04；UPGRADING v0.68.0 章节确认存在（P4 落笔，
  无破坏性变更、零迁移动作）。
- 三处一致核对：README badge v0.68.0 = CHANGELOG [0.68.0] = UPGRADING v0.68.0 节标题 ✓。

## 4. CHANGELOG 更新确认

- P4 commit e39c897 已写 CHANGELOG [Unreleased] 节（TAG0030 四 phase 条目：新增 6 条 + 变更 1 条，
  覆盖 RM-AG0057-①清理钩子/②人工体验节/③形态驱动化/④视觉契约 + 断言审计单测 + DEBT0024/25/26
  三连）——已复核内容完整、格式对齐既有章节（「新增（TAG0030：…）」+「变更」子节，Keep a
  Changelog 格式）。
- releaser 本次仅执行版本号行替换：[Unreleased] → `[0.68.0] - 2026-09-04`（日期用当前日期
  2026-09-04，不编造历史日期；v0.67.0 先例 [Unreleased] 直接改名、不留空头）。
- `git log v0.67.2..HEAD --oneline` 对照：13 个 commit 全为 TAG0030 链（交接单 ×3 + P1→P7），
  无任务外条目遗漏；CHANGELOG [0.68.0] 节覆盖本任务全部机制变更 ✓。

## 5. 发布检查命令建议清单（主 Agent 亲自执行，releaser 只列建议）

按 P2-design §5 gate_commands.P5 全量验证（worktree 根执行；P8 gate 后主 Agent 按 AUDIT7
分支决定复用或重跑——DEBT0013 时序：若需重跑 consistency，先 commit + 创建 tag v0.68.0
再跑，避开 CHECK 7 中间态误报）：

```yaml
P5_unit:        "python3 -m pytest agate/tests/unit/ -q --tb=no -n auto"        # 300s
P5_regression:  "python3 -m pytest agate/tests/regression/ -q --tb=no -n auto"  # 300s
P5_integration: "python3 -m pytest agate/tests/integration/ -q --tb=no -n auto" # 600s
P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"  # 120s，worktree 版
P5_shellcheck:  "shellcheck agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh"  # 60s
P5_count_tests: "bash agate/tests/scripts/count-tests.sh"  # 120s
P5_audit7:      "python3 agate/scripts/check-p6-provenance.py --audit7-only agate-workspace/tasks/TAG0030-acceptance-blindspot"
```

## 6. roadmap 回写 checklist（RM-AG0043 硬校验，主 Agent 执行）

- [ ] `agate-workspace/roadmap/roadmap.md` **RM-AG0057** 行：「状态」列 `scheduled` → `done`
  （P8 gate 硬校验 RM-AG0043：关联任务 TAG0030 的 RM 条目未回写 done 即阻断；回写与 P8 阶段
  commit 同批，同步「更新」列日期为回写当日，参照 RM-AG0054/55 done 行口径）。
- [ ] 回写由主 Agent 亲自执行，releaser 不写 roadmap。

## 7. 主 Agent 动作清单（P8 gate 通过后按序执行）

| # | 动作 | 依据 |
|---|------|------|
| 1 | `check-gate.py P8 $TASK_DIR` 跑 gate（bump_type / debt_check 字段 + 暂存区 version 文件 + CHANGELOG 变更 + roadmap done 检查面） | P8 卡 gate 规则 |
| 2 | AUDIT7 判定（§5）：reuse_allowed → 复用 P5-test-results/；否则重跑 gate_commands 全键（DEBT0013：先 tag 后重跑 consistency） | P8 卡 gate 规则 |
| 3 | `git tag v0.68.0 && git push origin v0.68.0` + `git ls-remote --tags origin v0.68.0` 验证远端到达（git push 默认不推 tag） | AGENTS.md 版本发布清单 |
| 4 | P8 commit message 须含 `self-gate-review:`（触发面：P1/P3/P4/P6 卡 + analyst/architect/verifier 角色 + plan-design-review.md + dispatch-context 模板，P0 env_constraints） | P0-brief env_constraints |
| 5 | release PR **普通 merge（--no-ff）禁止 squash**（CHECK 7 / G-5 describe 依赖 tag 与 main 同轨） | AGENTS.md（v0.31.0 事故） |
| 6 | G-5 最终验证：`git fetch origin && git describe --tags origin/main` == v0.68.0；`git merge-base --is-ancestor v0.68.0 origin/main` exit 0；合并后 CI 全绿 | AGENTS.md |
| 7 | READY 收尾检查（§8 临时资源清单清理 + 干净 checkout 跑 consistency 0 ERROR + 无 PROD_TOUCHED + 复盘判断） | P8 卡 READY 清单 |

## 8. 临时资源清单（releaser → 主 Agent READY 收尾交接）

| 类别 | 内容 |
|------|------|
| 临时服务/进程 | **无**——未启动服务/进程/daemon/调试进程 |
| 临时端口 | **无** |
| 开发安装 | **无**——未做 editable install / 全局包安装 |
| 临时数据 | **无**——未创建临时数据/测试数据库；临时文件仅 bash 探测用 `/tmp/agate-md-test*.md`（已删除，非任务产出） |
| 残留进程核查 | READY 收尾按 P8 卡逐项实际执行检查命令（`ps aux` / `git status`），不得仅凭本清单打勾 |

## 9. Lessons Learned（主 Agent 汇入 docs/notes/lessons.md）

1. **流程 / 纯文档面任务 bump 判定看机制兼容性而非改动行数**：协议条文新增 + 未改
   `.state.yaml` schema / gate 返回约定 / hook 薄壳 → 向后兼容的机制新增 = minor；判定依据是
   机制面兼容性（UPGRADING 无破坏性声明 + P7 改动面核对无 `.sh`），与改动文件数/行数无关。
   （来源任务 TAG0030，2026-09-04）
2. **流程 / 版本引用三处一致的职责分工**：P4 落 UPGRADING 章节 + CHANGELOG 条目，P8 releaser
   只做版本号行替换（README badge + CHANGELOG [Unreleased]→版本号）——分工明确避免重复劳动；
   中文镜像 README.zh-CN.md badge 易漏，须与 README.md 同批更新（TAG0028 先例，v0.65.0/66.0
   均两 README 同批）。 （来源任务 TAG0030，2026-09-04）
3. **流程 / DEBT closure 核对以 grep 锚词实证为准**：closure_criteria 满足与否逐条 grep 锚词
   实证（tests/README「真实 gate 语义」/ AGENTS.md「新增 CHECK 先全量扫描」/ dispatch-context
   模板「拆小默认指导」），不凭记忆断言；releaser 只核对留痕，tech-debt.md status 关闭与
   roadmap 回写留给主 Agent。 （来源任务 TAG0030，2026-09-04）

## 10. SELF-GATE 注记（触发面声明）

本任务触发 SELF-GATE（P0-brief env_constraints）：改动面含 `agate/phase-cards/*.md`
（P1/P3/P4/P6 四卡）+ `agate/assets/execution-roles/*.md` + `agate/assets/review-roles/
plan-design-review.md` + `agate/assets/templates/dispatch-context.md`。P4 commit e39c897 已含
`self-gate-review:` 声明（P7 核对一致）；P8 commit（主 Agent 执行）同触发面，message 必须含
`self-gate-review:`。协议文档改动已由 P5_consistency（--strict-errors-only）0 ERROR 验证
（P5 commit 196aca8 / P6 b650508 记录）。
