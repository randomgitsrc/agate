---
phase: P7
task_id: TAG0003-workspace-architecture
type: consistency
parent: P2-design.md
trace_id: TAG0003-P7-20260812
status: draft
created: 2026-08-12
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 3
design_gap_reviewed_count: 3
---

# TAG0003 — 工作区架构：P7 一致性审查

> 角色：consistency-reviewer（独立一致性交叉检查，`~/.agate/assets/execution-roles/consistency-reviewer.md`）。
> 审查对象：P1-P6 全部产出（P1-requirements / P2-design / P4-{core,docs,tests,fix,review-fix} / P4-review / P5-test-results/unit / P6-acceptance）+ git log 实际改动核对。
> 方法：逐条对照源文件（非"看起来对"的跳过），结论引用具体锚点。
> 环境标记：`[PROD_NOT_TOUCHED]` 本次审查只读 P1-P6 产出 + git 只读查询，未修改任何 agate/ 文件，未接触生产环境；`~/.agate` 稳定版未动。

## 结论（一句话）

P1-P6 产出跨文件一致：DESIGN_GAP 3 条全部 REVIEWED 配对、SCOPE+ 3 项闭环、BDD 20/20 与验收逐条对应、实现路径与 P2 方案吻合，无 BLOCKER / DEVIATION-CRITICAL，**可推进 P8**。

## 一、DESIGN_GAP 配对（P4 声明 → P7 转抄 + REVIEWED）

> 上游 dispatch 只识别了 core 的 1 条；独立审查发现 P4 拆分文件（core/docs/review-fix）共声明 **3 条** DESIGN_GAP，P7 全部转抄并逐一 REVIEWED。数量按实际审查结果从预填 1 调整为 3（`design_gap_count: 3` / `design_gap_reviewed_count: 3`），gate 判定 reviewed ≥ count 仍通过。

[DESIGN_GAP: P2 §3.2 未指定迁移后是否 commit。P3 MW.3 断言 git log --follow 在新路径可追溯旧 commit，但实测 git mv 只暂存 rename（index），未 commit 时 git log --follow 在新路径查不到任何 commit（历史为空）——故实现采用迁移完成后若有暂存变更则自动 `git commit -qm "chore(workspace): migrate legacy docs/tasks layout to workspace"`。此 commit 是全量 index commit，若用户迁移前有其他已暂存改动会被一并提交（风险已在工具输出注释标注，文档侧 UPGRADING.md 应提示迁移前保持暂存区干净）]
[DESIGN_GAP_REVIEWED: 已确认——P4-implementation-core.md L58 声明 + L59 主 Agent 已标 REVIEWED；P4-review.md §一实证闭环（revcheck2 fixture：hook 跳过 + pathspec 限定 + --follow 可追溯 + 无关改动未入 commit）；MW.9 回归测试（agate-migrate-workspace.bats:132-182）5 断言含 hook-liveness 守卫实测绿。自动 commit 是满足 P1 BDD-8（git 历史可追溯）的必要行为，风险已缓解，接受该实现决策。]

[DESIGN_GAP: P2 §3.3 只列了 orchestrator-template 的 4 处路径切换点，未覆盖 phase-cards/P0-orchestrator.md 与 P8-release.md 的裸 `active-tasks.md` 引用；实现中将其一并改为工作区路径以保持一致。]
[DESIGN_GAP_REVIEWED: 已确认——P4-implementation-docs.md L74 声明。实现将 P0-orchestrator / P8-release 两张卡片的裸 `active-tasks.md` 引用一并改为 `{AGATE_WORKSPACE}/tasks/active-tasks.md`（git diff 实测两文件均 M），与 BDD-6「docs/tasks 迁入工作区」及 BDD-10「旧布局获得迁移指引」一致；P5 consistency 0 ERROR 佐证无残留。范围外顺手补齐属合理实现决策，无行为风险。]

[DESIGN_GAP: P4-review F1 选项 A 原文建议 pathspec 只给新路径（`-- "$AGATE_TASKS_DIR" "${AGATE_WORKSPACE}/archived"`），但实证该写法触发 git partial commit 使 rename 断裂（旧路径残留 HEAD + index 留 staged 删除，BDD-8 需二次 commit 才满足）。实现采用旧路径+新路径成对 pathspec（delete+add 同 commit 表达 rename），并引入 GIT_MV_STAGED 标记避免外部工作区（fallback mv）误触发 commit。选项 A 的意图（跳 hook + 不误提交无关改动）保持不变]
[DESIGN_GAP_REVIEWED: 已确认——P4-implementation-review-fix.md L56 声明。P4-review.md §一独立复现验证成对 pathspec 正确（`/tmp/opencode/revcheck2/repo`：迁移 commit 不含无关 staged 改动 + `--follow` 追到 init/migrate 双 commit）；MW.9 断言③`git status` 无 docs/tasks 残留防 partial commit 回归。偏离评审原建议但有实证依据且更正确，接受。]

DESIGN_GAP 配对汇总：P4 声明 3 条 → P7 转抄 3 条 → REVIEWED 3 条，零遗漏（对应 gate 断言 BLOCKER=0 的配对锚点）。

## 二、SCOPE+ 闭环（P1 scope_resolved 3 项确认）

P1-requirements.md frontmatter `scope_resolved` 共 3 项（P2 回补，2026-08-12），逐项核对已纳入 P2 方案与 P4 实现：

1. **[SCOPE_RESOLVED] check-state-transition.sh 任务级 .state.yaml 检测硬编码**（P1 scope_resolved #1）→ P2-design.md §1.1/§3.6 + §8 minimal_validation#4（改 dirname!=REPO_ROOT 语义）→ P4-implementation-core.md §1.5 已实现（P4-core L28-34 实测：`realpath -m dirname` + `git rev-parse --show-toplevel` + `realpath --relative-to`，覆盖 docs/tasks/agate-workspace/自定义三布局）；ST.1-20 + ST_WS.1-4 测试绿（P4-core §2 自查 47/47，P5 全量绿）。BDD-13 覆盖。
2. **[SCOPE_RESOLVED] check-pruning.sh P7 源码文件数过滤硬编码**（P1 scope_resolved #2）→ P2-design.md §1.1 + §10 → P4-implementation-core.md §1.6 已实现（P4-core L65-73 实测：`TASKS_BASE_REL` 从运行时 TASK_DIR 反推 + 排除正则 `^docs/tasks/|^${TASKS_BASE_REL}/`，保留旧布局兼容）。BDD-6/13 覆盖。
3. **[SCOPE_RESOLVED] worktree 自身 live docs/tasks 不物理迁移**（P1 scope_resolved #3）→ P2-design.md §1.2/§1.3/§10 → 迁移工具验证全走 fixture（BATS_TEST_TMPDIR），P6-acceptance BDD-6 用 fixture 判定（bdd-06.log，docs/tasks 物理消失发生在 fixture 仓库）；worktree 自身 docs/tasks/TAG0003 仍存活（本审查实测存在）。BDD-6 覆盖。

SCOPE+ 闭环成立：P1 3 项 scope_resolved → P2 §10 3 项 [SCOPE+] 一一对应 → P4 实现全部落地。另 P4-docs §1.3 声明 4 个清单外文档（custom-role / protocol-alignment-review / P0-card / P8-card）一并换血——check-scope-resolved.sh 对非空 scope_resolved 即放行（实测 P1 非空），且该批改动与迁移方向一致、P5 consistency 0 ERROR，属合理增补非遗漏。

## 三、跨文件一致性

### 3.1 P2§packages 与变更范围

- P2-design.md frontmatter `packages: [agate]`（协议本体单一包）。git log 实测 P1..P6 六 commit（4dd7fec/a2e85b3/80c30d5/9aaab53/2bf9221/6bf3110），`git diff 4dd7fec..HEAD` 全部 100 个变更文件均落在 `agate/` 包内（+ 任务目录 docs/tasks/TAG0003-… + active-tasks.md），无包外文件（grep 排除后 exit 1 无残留）。与 P2§packages 一致；P8 release bump 范围应沿用此边界（agate 单包，P8 阶段确认）。

### 3.2 P1 BDD 数量/内容 ↔ P6 验收

- P1-requirements.md 共 **20 条 BDD**（`#### BDD-` 计数 = 20，BDD-1..20 编号连续）；P6-acceptance.md **20 条 PASS**（`- PASS BDD-` 计数 = 20），frontmatter `pass: 20 / fail: 0`。数量匹配。
- 逐条内容对应（抽查语义关键项，非只对编号）：
  - BDD-1（初始化建 8 子目录）↔ PASS BDD-1（orchestrator-template.md:102 + SETUP.md:114 同一 mkdir 命令，fixture 实测建齐 roadmap/tasks/agents/archived/reviews/decisions/plans/logs）✓
  - BDD-8（git 历史保留）↔ PASS BDD-8（git mv 记 R rename + `git log --follow` 追到 init+migrate）✓
  - BDD-10（旧布局迁移指引）↔ PASS BDD-10（orchestrator-template.md:71/73-75/77 检测+指引+不静默）✓
  - BDD-13（状态机行为不变）↔ PASS BDD-13（pre-commit 走解析器 + state-transition dirname 语义 + pruning 跟随；全量 bats 631/0，resolve/migrate/state-transition 48/0）✓
  - BDD-17（内容边界判据）↔ PASS BDD-17（WORKFLOW.md:93-104 判据 + 双场景对偶结论相反）✓
  - BDD-20（白名单 + 用例数基线）↔ PASS BDD-20（consistency 0 ERROR + count-tests 625 与 P5 一致）✓
  - 其余 BDD-2/3/4/5/6/7/9/11/12/14/15/16/18/19 逐条核对编号与内容均对应（P6 §附注对 BDD-6 推论、BDD-8 外部工作区限制的判定说明合理）。
- 结论：20/20 数量与内容双重匹配，无"数量对内容错"的映射错误。

### 3.3 P2§impl-path ↔ P4 实现路径

P2-design.md §1.1 声明 vs `git diff 4dd7fec..HEAD` 实际：

| P2 §1.1 声明 | git 实测 | 吻合 |
|---|---|---|
| 6 既有脚本 + 2 新增（resolve/migrate） | 7 修改（pre-commit-gate / ci-gate-backstop / check-state-transition / check-pruning / check-protocol-consistency / install-hook / agate-render-dispatch-prompt）+ 2 新增 | ✓（render-dispatch-prompt 为 P4-fix §1.3 RP.13 修复，属 fix 轮合理增补；gate-result.sh 未改——P2 声明"或由新增解析脚本承载"，选择解析脚本方案） |
| 16 文档 + roadmap-template 新增 | 16 个逻辑条目全部命中（含 assets/execution-roles 7 + phase-cards 9 + templates/loop/rules 等）+ roadmap-template.md 新增；另 SCOPE+ 扩展 4 文档（§二 已声明） | ✓ |
| 8 个 .bats 换血 + 2 新增测试文件 | 7 修改 + 2 新增（P4-tests 表：check-pruning.bats 无 docs/tasks 硬编码 0 处改动，符合声明） | ✓ |

### 3.4 P4-implementation 各文件声明 ↔ git 实际改动

- **core**：声明 6 脚本（2 新增 + 4 改造）→ git 实测 4 M（pre-commit-gate / ci-gate-backstop / check-state-transition / check-pruning）+ 2 A（resolve / migrate）✓；其 [SCOPE_GAP]（check-protocol-consistency + install-hook 未入并行文件集）由 P4-fix §1.1/§1.2 补做 ✓。
- **docs**：声明 16 文档 + roadmap + 4 SCOPE+ 扩展 → git 实测全部命中 ✓。
- **tests**：声明 8 文件集（7 改 1 零改动）+ 2 新增 → git 实测 7 M + 2 A，fixtures.bash 未改（符合"mktemp 不改"）✓。
- **fix**：声明 3 脚本（consistency/install-hook/render-dispatch-prompt）→ git 实测 3 M ✓。
- **review-fix**：声明 4 文件（migrate / pre-commit-gate / UPGRADING / agate-migrate-workspace.bats）→ git 实测全命中 ✓。
- 各文件声明与 git 无出入，无越界改动（diff 范围限定 agate/ + 任务目录）。

### 3.5 用例数基线

- P2-review 确认基线 603；P4-tests：624（603+21 P3 新增）；P4-fix：624；P4-review-fix：625（+MW.9）；P5-count：625；P6 BDD-20：625。逐阶段单调且预期一致，无漂移。✓

## 四、未决项清零

- P1-requirements.md §4 为 `[NO_NEED_CONFIRM]`，实测无残留行首 `[NEED_CONFIRM]`（grep 仅命中 dispatch-context 的格式说明文字，非产出文件标记）。✓
- 全任务目录产出文件（P1/P2/P4/P5/P6）grep 无行首 `[BLOCKER]` / `[DEVIATION-CRITICAL]`（命中项均为 P6-evidence 测试日志的测试名文本，非产出标记）。✓
- P4-review（approved）无未决阻塞项；P4-review §六 2 条残留观察（migrate 提示分支字符串比较 / MW.9 hook 守卫耦合）均标注非阻塞，本次审查确认为提示性质不构成行为错误。✓

## 五、结论与推进建议

- **BLOCKER=0**：无 [BLOCKER] / [DEVIATION-CRITICAL]；DESIGN_GAP 3/3 配对 REVIEWED（锚点：§一逐条）。
- **CRITICAL=0**：跨文件检查全部一致（锚点：P2§packages / P1 BDD-1..20 ↔ P6 PASS BDD-1..20 / P2§impl-path ↔ P4 各文件 / count-tests 625）。
- **SCOPE+ 闭环**：P1 scope_resolved 3 项 ↔ P2 §10 ↔ P4 实现全部落地（锚点：§二逐条 + [SCOPE_RESOLVED]）。
- 残留观察（非阻塞）：agate-retreat-to.bats 仍含 `docs/tasks/T001` fixture 路径（P4-tests §协调事项 2 已声明，retreat-to 以 TASK_DIR 为参数、测试任意路径均可运行，且不属 P2 §1.1 8 文件集；一致性检查只扫 .md 不扫 .bats，BDD-20 不受影响）——记录留痕，不做处理。
- **推进 P8**：P7 通过，进入机械发布步骤。
