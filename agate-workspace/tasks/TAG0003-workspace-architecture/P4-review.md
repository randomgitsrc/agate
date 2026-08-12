---
phase: P4
task_id: TAG0003-workspace-architecture
type: review
parent: P4-implementation.md
trace_id: TAG0003-P4-20260812
status: approved
created: 2026-08-12
agent: review
---

# TAG0003 — 工作区架构：P4 复审（修复轮后）

> 角色：review（偏执 Staff Engineer，`~/.agate/assets/review-roles/review.md`）。
> 范围：复审轮——针对上一轮 P4-review.md（status: needs-revision）的 F1/F2 修复 + MW.9 回归 + 顺手项，逐一验证闭环；并对修复轮引入的变更做回归抽查。
> 方法：代码逐行核对 + **实证复现**（/tmp/opencode/revcheck2 fixture：带 hook 的仓库 + 迁移前无关暂存改动）+ 全量客观查证（bats / consistency / shellcheck / count-tests）。
> 环境标记：[PROD_NOT_TOUCHED] 评审仅读代码 + 在 `/tmp/opencode/` 构造 fixture 复现，未接触生产环境；`~/.agate` 稳定版未动。

## 结论（一句话）

上一轮 F1/F2/MW.9 全部闭环（实证复现 + 全量测试绿），顺手项处理合理，**status: approved**。

## 一、F1（主要）迁移自动 commit 静默失败 — 已闭环

**修复落点**：`agate/scripts/agate-migrate-workspace.sh:134-153`（commit 段重写）。

- **hook 跳过（选项 A）**：`:142` `git -c core.hooksPath=/dev/null commit -qm "chore(workspace): migrate legacy docs/tasks layout to workspace" -- "${COMMIT_PATHS[@]}"`——`core.hooksPath=/dev/null` 是 git 官方临时禁用 hook 的方式，精确满足上一轮"跳过自身 hook"要求。
- **pathspec 成对修正（对上一轮建议的实证改进）**：`COMMIT_PATHS` 按 `TASKS_MIGRATED`/`ARCH_MIGRATED` 标记条件追加「旧路径 + 新路径」成对（`:135-140`），而非上一轮建议的只给新路径。实现记录 `P4-implementation-review-fix.md:24` 实证了只给新路径会触发 git partial commit（旧路径残留在 HEAD + index 留 staged 删除，需二次 commit）。**我独立复现验证成对写法正确**（见下）。
- **不再吞失败（选项 B）**：`:141-149` `git commit` 置于 if 条件，失败时输出显式错误「迁移已移动文件，但自动 commit 失败（BDD-8 git 历史未保留），请手工 git commit 完成迁移」+ `exit 1`，不再 `|| true` 吞掉、不再打印"迁移完成"。:150-153 fallback（外部工作区，rename 未进暂存区）不尝试 commit，有其他已暂存改动时仅 WARNING 不动。

**实证复现（本轮独立，fixture `/tmp/opencode/revcheck2/repo`）**：
- 场景：docs/tasks（含 .state.yaml + 任务 + active-tasks）+ docs/archived + 按 install-hook 方式软链 pre-commit hook + **迁移前塞入无关暂存改动 unrelated.txt**。
- 结果：迁移 exit 0；git log 顶部为「chore(workspace): migrate legacy docs/tasks layout to workspace」，无迁移前无关内容；`git cat-file -e HEAD:unrelated.txt` → **NO（无关改动未进迁移 commit，pathspec 限定生效）**；`git log --follow -- agate-workspace/tasks/.../P1-requirements.md` 同时追到「init」与「migrate」两条 commit（BDD-8 成立）。
- 即 F1 的两个核心断言（跳过 hook 不被拦截 + pathspec 不误提交无关改动）均经实证成立。

## 二、F2（主要）缓解措施缺失 — 已闭环

- **工具注释/输出标注**：`agate-migrate-workspace.sh:123-133` 补 3 条风险注释（hook 拦截 / 全量 index commit + pathspec 成对说明 / 不吞失败）；`:144` 成功后输出「已自动 commit rename（跳过项目自身 pre-commit hook，git 历史可追溯 BDD-8）」。上一轮"工具全文无任何标注"的事实已消除。
- **UPGRADING.md 迁移前提示**：`agate/UPGRADING.md:102` v2.0.0 迁移节 ① 工具前补「迁移前先处理暂存区」——明确 pathspec 限定不会带无关改动、但仍建议先 `git commit` 或 `git reset` 让暂存区只含迁移内容。上一轮"文档侧提示不存在"的事实已消除。

## 三、MW.9 回归测试 — 真实且带回归守卫（非空壳）

`agate/tests/unit/agate-migrate-workspace.bats:132-182`：

- **fixture 真实还原缺陷场景**：.state.yaml 用 v2.0 编号格式（`:137-142`，否则 check-state-yaml 先拦）；旧版本 dispatch-context（内嵌卡片与当前协议 hash 不一致，`:146-154`）——正是上一轮实证命中 pre-commit-gate.sh 卡片校验的输入形态；软链安装 pre-commit hook（`:156-159`）。
- **5 项断言**：① exit 0 + 文件落新路径（`:162-163`）；② git log 含迁移 commit（`:166-167`，旧缺陷下缺失→红）；③ `git status` 无 docs/tasks 残留（`:169`，防 partial commit 只提交新路径回归）；④ `--follow` 追到 init commit（`:172-174`）；⑤ **hook-liveness 回归守卫**（`:175-181`）——迁移后改 .state.yaml 的裸 commit 必须仍被卡片校验拦截（`status -ne 0`），防 hook 安装失败导致测试退化失去判别力。
- **实测**：MW.9 独立运行绿（9/9）；实现记录 `:41` 声明 TDD 实证（还原旧缺陷红→修复绿），与测试断言结构自洽。
- 该测试为 P4 评审缺陷的真实捕获测试，非形式化空壳。

## 四、顺手项（上一轮返回建议第 4 条）

| 项 | 决定 | 依据 |
|---|---|---|
| pre-commit-gate.sh:14 注释旧路径 | 已做 | `:14` 现为「扫描所有暂存的 .state.yaml（根 + {AGATE_WORKSPACE}/tasks/{Txxx}/）」，行为不变 |
| migrate 空目标（已存在空目录）边角 | 已做 | `agate-migrate-workspace.sh:61-64` 目标为空目录先 rmdir 再 git mv，规避 `{dst}/src/` 嵌套；实现记录 `:30` 实证平铺 |
| check-pruning 正则转义 | 记录不改 | 上一轮 F7 已判不影响正确性底线；sed 转义脆弱（实证风险 > 收益），决定合理 |
| install-hook 自定义工作区提示 | 记录不改 | 上一轮 F12 已判提示性质不构成行为错误，决定合理 |

## 五、回归抽查（修复轮未引入新问题）

- 全量 bats：**unit 530/530**（`^not ok` 计数 0；含新增 MW.9）+ **regression 0 not ok** + **integration 78/78** + **sanity 0 not ok**。
- `count-tests.sh`：**625**（基线 624 + MW.9 = 预期 +1，无漂移）。
- `check-protocol-consistency.py`：**0 ERROR** 全 PASS。
- `shellcheck -S warning`（migrate / pre-commit / check-state-transition / check-pruning / render-dispatch-prompt / install-hook）：**0 告警**。
- 修复轮只改 4 个目标文件（2 脚本 + 1 文档 + 1 测试），与 `P4-implementation-review-fix.md:15` 声明一致，未越界触碰并行组文件集与 `~/.agate`。

## 六、残留观察（非阻塞，记录即可）

- `agate-migrate-workspace.sh:162` 提示分支 `AGATE_WORKSPACE != "$PROJECT_ROOT/agate-workspace"` 用字符串比较未 `realpath -m` 归一——同一路径的不同写法（如 `agate-workspace/` 带尾斜杠）可能触发提示。纯提示性质，无行为错误，与上一轮 F4 的 realpath 观察同源。
- MW.9 的 hook-liveness 守卫依赖 pre-commit-gate.sh 卡片校验——该守卫与协议版本耦合，若未来协议修改卡片校验逻辑，MW.9 可能需要同步更新。非当前缺陷。

## 七、检查清单

| 项 | 结论 | 依据 |
|---|---|---|
| F1 commit 静默失败 | **已闭环** | hooksPath 跳过 + pathspec 成对 + 失败 exit 1；实证 exit 0 / 无关改动未提交 / --follow 可追溯 |
| F2 缓解措施缺失 | **已闭环** | 工具注释标注 L123-133 + UPGRADING:102 迁移前提示 |
| MW.9 回归测试 | **已闭环（真实）** | 带 hook fixture + 5 断言 + hook-liveness 守卫，实测绿 |
| 顺手项 | 处理合理 | 2 项已做、2 项记录不改（均有实证依据） |
| 回归 | 通过 | unit 530 / regression / integration / sanity 全绿，count-tests 625 无漂移 |

## 八、返回建议

**Status: approved**。F1/F2/MW.9 三处上一轮主要缺陷全部实证闭环，可推进 P5 验证。
