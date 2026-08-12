---
phase: P2
task_id: TAG0003-workspace-architecture
type: review
parent: P2-design.md
trace_id: TAG0003-P2-20260812
status: approved
created: 2026-08-12
agent: plan-eng-review
---

# P2 评审：TAG0003 工作区架构方案设计

> 角色：plan-eng-review（工程经理，独立评审）。评审对象：P2-design.md（候选方案 A/B/C、§3.6 去硬编码、SCOPE+ 3 项、minimal_validation 5 项）。
> 方法：先读代码再评审。已实测核验设计引用的全部关键锚点（行号、grep 语义、bats TAP 输出、formatter 正则、用例数基线、SCOPE gate 触发条件）。

## 架构问题（阻塞级）

无。方案 A（候选方案 A：单点解析器 + git mv 目录级迁移 + 全量同步）核心假设全部经独立实测证实可行：

- **解析器落地性**：`pre-commit-gate.sh` L27 `AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"` 与 L82-86 根级/任务级 `TASK_DIR` 分支语义均已核实，改为 source 解析器后任务级/根级分支仍可保持（files_to_read 已提醒保持分支语义）。
- **git mv 目录级迁移**：minimal_validation#1/#2 的空源 exit 128 / 非空目标 exit 1 / 仓库外 exit 128 三组边界行为与 git mv 实际语义一致，迁移工具第 2/3/4 步的守卫设计（no-op / 冲突检测 / fallback）与边界行为一一对应，无悬空假设。
- **check-state-transition.sh 去硬编码（SCOPE+ #1）**：L28 `grep -qE 'docs/tasks/[^/]+/'` 实测存在，且是任务级 .state.yaml 检测的唯一入口；改 `dirname($STATE_FILE) != REPO_ROOT` 与 pre-commit-gate.sh L82 `[ "$STATE_DIR" = "$REPO_ROOT" ]` 完全同构，三种布局（docs/tasks / agate-workspace / 外部）均正确路由，方案成立。
- **bats TAP 与 formatter 兼容（minimal_validation#5）**：实测 `bats --formatter tap` 输出 `1..N` + `ok N`/`not ok N`，与 `assets/formatters/generic-tap.sh` 的 `^ok\b`/`^not ok\b` 正则匹配，P3/P5 gate 命令可用。
- **"不改"边界**：grep 实测 check-gate.sh / check-p6-provenance.sh / check-p6-evidence.sh / check-scope-resolved.sh / check-retrospective.sh / check-changelog.sh / agate-state-get.py / agate-md-field-get.py / agate-gate-p5-count.py 均 0 处 `docs/tasks`，§1.2 边界声明属实。

## 架构问题（非阻塞）

1. **[SCOPE+ 基线回补遗漏，需主 Agent 在 P2 commit 前动作]** P2-design.md §10 的 3 项 `[SCOPE+]`（L321/325/329）会触发 pre-commit 的 check-scope-resolved.sh（pre-commit-gate.sh L184-191 对所有非 exit 1 的 GATE_EXIT 都跑）。实测 P1-requirements.md **无 `scope_resolved` frontmatter**，而 check-scope-resolved.sh L42-47 要求非空 `scope_resolved` 列表才放行 → **P2 commit 会被 SCOPE gate 拦截（exit 1）**。评审结论：3 项 SCOPE+ 本身真实必要（2 项为隐藏硬编码，1 项为边界声明），"不需新增 BDD"（BDD-13/BDD-6 覆盖）成立；但方案未声明 P1 需回补 `scope_resolved`。建议：主 Agent 在 P2 commit 前给 P1-requirements.md frontmatter 补 `scope_resolved`（3 项均已纳入本方案，标注实施计划），否则 commit 阻塞。

2. **[实现期路径拼接注意]** 解析器输出 `AGATE_TASKS_DIR` 为**绝对路径**（§3.1 边界语义），但 pre-commit-gate.sh L83 现为 `TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"`——绝对路径时重复拼接 `REPO_ROOT` 前缀会产出错误路径。§3.1 已声明"替换 L27/L83"且 files_to_read 首条即指向该文件，方向正确，但未明确 L83 新公式（绝对路径时不再拼前缀）。P4 实现时须处理，建议直接在设计中写明。

3. **[BDD-20 口径偏差需 P6 留痕]** BDD-20 Then 字面为"测试用例总数与迁移前基线一致（不漂移）"，设计采用 P1-review 观察项 1 口径——"既有 603 条换血不改数 = 不漂移，新增迁移/解析器用例允许增长"（§1.3 风险表 + §3.7）。实测 count-tests.sh 基线确为 603，设计引用属实；但字面与口径存在语义差，P6 验收 BDD-20 时须按此口径判定并显式留痕，避免二值判定争议（建议 P6 验收记录中引用本评审锚点）。

4. **[roadmap 验收依赖模拟而非真实闭环]** BDD-14/15/16 的验收路径（§3.4 + 实现完成标志 #7）依赖模板与 WORKFLOW.md 规范支撑，roadmap 循环无脚本 gate。P6 判定须按文档规范**模拟执行**闭环（创建条目→拆任务→写待开始→回写 done/cancelled），不能依赖真实跑完一个完整 P0-P8 任务。属 self-authored gate 固有局限（LIMITATIONS 局限 3），可接受，但 P6 验收路径应明确"模拟闭环"。

## 测试缺口

- **SCOPE gate 回补测试**：check-scope-resolved.bats 现无覆盖"P2 设计含 [SCOPE+] 而 P1 无 scope_resolved → exit 1"的场景（P1 需回补后该场景自然消失，属流程性缺口，非本方案代码缺口）。建议 P1 回补时顺带在 check-scope-resolved.bats 增加一条 fixture 用例。
- **解析器绝对路径拼接**：P3 新增 `agate-workspace-resolve.bats` 应覆盖"解析器输出绝对 tasks_base + pre-commit-gate.sh L83 拼接"的联合场景（外部工作区 + 根级 .state.yaml），防止实现期路径拼接回归。
- **BDD-6 "不再从 docs/tasks 读取"的可检落点**：P1 注（L111）明确要求把推论落到可检状态。设计通过 BDD-11/12/13 落点 + 实现标志 #6（orchestrator-template.md 四处切换完成）覆盖，但建议 P6 额外断言"orchestrator-template.md 不再含 `docs/tasks/active-tasks.md` / `docs/agents/project.md` 读取路径"（grep 可判），使 BDD-6 判定不依赖推论。

## 候选方案质量（candidate_count=3）

- 方案 B（环境变量直连，无 .agate.env）：明确标注"违背 P1 已确认决策 4，只能作为对照而非候选"——诚实自评，未伪装成可选替代。评审接受该定位：P1 决策是硬约束输入（不得推翻），B 作为对照用于说明不引入 .agate.env 的代价，具备对照价值而非稻草人（其权衡列出的 BDD-3/4/5 无法满足是真实结构性结论）。
- 方案 C（.agate.env + 文件级 git mv）：真实替代（粒度可控 vs 复杂度），否决理由"目录级 git mv 已验证覆盖 gitignore/未追踪文件，文件级无额外收益"有 minimal_validation#1 实证支撑，逻辑自洽。
- 权衡与选择理由：选择理由三因素（BDD-13 结构性保证 / 目录级物理移动经验证 / B 违背决策 4）均锚定具体 BDD 与验证结果，自洽、非空泛。

## 影响域完整性

- known_risks 5 项全覆盖：破坏性迁移（迁移工具 §3.2 + UPGRADING.md）、6 脚本 + 16 文档 + 75+ 引用（§1.1 按 43 文件/516 处预算，采用 P1 analyst 修正口径）、orchestrator 路径影响所有接入项目（§1.3 + SETUP/UPGRADING 双路径）、roadmap 新增机制（§3.4）、内容边界（§3.5）。
- 隐藏硬编码两处（check-state-transition.sh L28、check-pruning.sh L65-66）被 SCOPE+ 识别并纳入 §1.1 改造清单——这是本方案超出 P1 基线的重要正确性补全（T086 B1 教训同构），评审认可。
- 明确"不改"边界（check-gate.sh 等 9 脚本零硬编码）+ worktree 自身 live docs/tasks 不物理迁移（SCOPE+ #3），边界清晰无越界。

## 锁定决策

- 候选方案 A（单点解析器 + git mv 目录级迁移）为锁定方向；解析优先级 `.agate.env` > `AGATE_TASKS_DIR` env > 默认 `agate-workspace/`（§3.1，与 P1 SUGGEST #2 一致）。
- check-state-transition.sh 任务级检测改 `dirname != REPO_ROOT` 语义（§3.6，去硬编码）。
- gate_commands 固化：P3 = 三个目标 .bats 文件（TAP 输出 + generic-tap.sh formatter）；P5 = 全量 bats + P5_consistency/P5_shellcheck/P5_count 补充命令；ui_affected=false（无前端，无 P5_e2e），合理。P5 多命令 WARNING 属预期（agate-gate-p5-count.py 实测会数出 4 个 P5* 命令）。
- BDD-20 口径锁定为 P1-review 观察项 1（603 换血不漂移 + 新增允许增长）。

## 结论

**approved**。方案 A 的可行性、候选质量、影响域、BDD 可验收性、gate_commands、风险止损均通过独立核验；无阻塞级问题。需主 Agent 关注的非阻塞项：P2 commit 前补 P1 `scope_resolved` frontmatter（否则 SCOPE gate 拦截）；实现期处理 AGATE_TASKS_DIR 绝对路径与 pre-commit-gate.sh L83 的拼接。

参考锚点：候选方案 A（§2）/ B（§2）/ C（§2）；SCOPE+ #1（§10 L321 + §3.6）/ #2（§10 L325）/ #3（§10 L329）；minimal_validation #1/#2/#4/#5（§8）；gate_commands（§5）；BDD-6/13/14/15/16/20（§4）；风险表（§1.3）。
