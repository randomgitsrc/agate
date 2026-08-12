---
phase: P2
task_id: TAG0001-tech-debt-closure
type: review
parent: P2-design.md
trace_id: TAG0001-P2-20260812
status: approved
created: 2026-08-12
agent: plan-eng-review
---

# TAG0001 P2 方案评审（plan-eng-review，工程维度独立评审）

评审对象：`P2-design.md`（4 决策点 D1-D4 × 2 候选，candidate_count=4，2 项 SCOPE+，20/20 BDD 映射）。
评审依据：P0-brief.md（known_risks 9 项）、P1-requirements.md（20 BDD）、P1-review.md（N1-N4）、review-20260812-1204.md（背景设计），以及对 worktree 现状的逐项客观查证。

## 客观查证摘要（方案的关键事实假设均已在 worktree 核实，非纸面推理）

- **P8 分支与插入点**：check-gate.sh P8 分支（L413-471）bump_type 检查在 L420-424、version 检查紧随其后——§2.5 拟插入的 `debt_check:` 缺失即 exit 1 检查在 bump_type 之后、version 之前，位置可行且不会误伤 G8.1（缺 bump_type，提前 exit 1）。
- **[SCOPE+] #1 成立**：G8.2/3/4/6/7/8 的 P8-release.md 均仅含 `bump_type: minor`，加 debt_check 硬检查后将从 exit 2 变 exit 1，6 处 fixture 必须同步更新；G8.1（缺 bump_type）与 G8.5（无 P8 文件）不受影响。fixture 面判定与设计一致。
- **[SCOPE+] #2 成立**：check-protocol-consistency.py 的 SCRIPT_ALIGNMENT_ANCHORS（L451）与 check_anchor_coverage（L694-724，WARNING L723）确实对无锚点的 check-*.sh 报 coverage WARNING——新增 check-debt.sh 必须加锚点，且 scripts/README.md 需补录脚本清单。
- **fenced yaml 提取可复用**：check-protocol-consistency.py L133-140 `extract_code_blocks` 正则 `r"```yaml\n(.*?)\n```"`（非贪婪，可提取多条）确为既有机制（L188 已用于 CHECK 1）；agate-debt-check.py 复用之是"复用既有模式"，非新造轮子。
- **mkdir 8→9 无脚本依赖**：8 子目录逗号字面量仅存在于 orchestrator-template.md:102 / SETUP.md:114 / state-machine.md:40-41 三处文档，agate/scripts 与 agate/tests 无任何脚本/测试对该集合做计数断言——改 9 集是纯增量，无兜底分支被破坏（§7 minimal_validation #2 结论属实，其"4 处文档"表述含 WORKFLOW.md:79 的"固定 8 个子目录"文字，非逗号字面量，属措辞小误，不影响结论）。
- **回退信号可观测**：`git log --format='%H%x09%s' --all --grep='^retreat:'` 实测返回 023b28b/29301ad 两条，格式与 agate-retreat-to.sh L63 一致——BDD-13/14/15 的 fixture 依据成立。
- **654 基线一致**：count-tests.sh 实测 648 + sanity.bats 6 = 654，与设计引用的"既有 654 用例"吻合。
- **薄壳范式**：check-frontmatter.sh（`[ ! -f "$FILE" ] && exit 0` + mktemp stderr + python exit≠0→exit 1 + ERRORS 非空→exit 1）与 §2.3 check-debt.sh 的设计逐条一致。

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

- **N-A：P3 gate_commands 的 TDD 覆盖面窄于改动面**。`P3: bats agate/tests/unit/agate-debt-check.bats` 只跑新增校验器的用例；而 check-gate.sh P8 debt_check 改动 + [SCOPE+] #1 的 check-gate.bats 新用例（缺失→exit 1 / 内容任意→exit 2）不在 P3 命令内。后果：check-gate.sh 的改动没有"P3 先红、P4 转绿"的可观测 TDD 证据，只由 P5 全量回归兜底。建议：把 check-gate.bats 追加进 P3 命令（或 P3 明确声明该改动以 P5 回归为验收载体，G8 fixture 同步属既有用例维护非新 TDD）。
- **N-B：tests/fixtures/*.md 被 CHECK 1 扫描**。check-protocol-consistency.py 的 iter_md_files 扫描根下全部 *.md（含 agate/tests/fixtures/），CHECK 1 对 yaml 块解析失败会 ERROR。§2.8 计划的 `tech-debt-backfill.md`（T1-T4 回填，均为合法条目）不会触发，但**任何后续负向 fixture 若放 .md 且故意含不可解析 YAML，会误伤 consistency 0 ERROR**。建议：负向用例一律走 .bats heredoc（不在 CHECK 1 扫描面），并在实现完成标志中明示此约束。
- **N-C：schema 校验器无自动化调用点**。check-debt.sh FILE 模式不接入 pre-commit（§10 已文档化），正常任务流中无 gate 自动运行它，BDD-5..10 只靠 P6 对 fixture 实跑验证。这是与"只留痕不阻断 / 防 Goodhart"哲学一致的有意选择，非缺陷；但实现完成标志第 8 条应明确"BDD-5..10 的验收载体 = P6 对 tech-debt-backfill.md + bats 负向用例实跑 check-debt.sh"。
- **N-D：`debt_check` 取值集合未约束**（§10 已自声明开放项）。缺失即拦、值任意放行符合 BDD-17"只查存在性"，`none`/`reviewed` 为建议值——可接受，P3/P6 按"只查存在性"验收即可，勿在 P4 私自加硬枚举。

## 测试缺口

- BDD-13/14/15（回退覆盖比对）与 BDD-16/17/18（P8 留痕）的 bats 用例集中在 `agate-debt-check.bats` + check-gate.bats 的 2 组新用例，覆盖已充分；唯一缺口即 N-A 所述的"check-gate.sh P8 改动缺少 P3 红-绿 TDD 证据"（P5 回归兜底不构成设计缺口，但应在 P3/P4 执行时显式确认）。

## 锁定决策

- **D1 选 1A（fenced yaml 块）**：与 CHECK 1 共用 extract_code_blocks（已验证非贪婪多块提取），块边界无歧义，模板示例被 CHECK 1 强制可解析白送自校验。1B 的 frontmatter 多块解析与 `---` 横线歧义是新实现成本，弃选合理。
- **D2 选 2A（独立 agate-debt-check.py + check-debt.sh）**：tech-debt 多条目块解析与 frontmatter 单块校验是两种数据形态，"复用薄壳模式而非实现"，回归风险隔离到零。与 P1 SUGGEST #3 一致。
- **D3 选 3A（--retreat-coverage 子命令）**：schema 校验与回退比对同属"检查 debt 状态"职责，单入口少一个 CHECK 9 锚点；恒 exit 0 + WARNING 落地 P1 SUGGEST #4（回退比对不挂 gate）。与 BDD-13"不阻断 commit/发布"一致。
- **D4 选 4A（debt_check 缺失即 exit 1）**：与 review doc §5.4"P8 必须看过清单并留痕"的强制语义一致，与 bump_type 缺失即 exit 1 保持一致性；内容全放行满足 BDD-17。既有 6 处 G8 fixture 更新是 BDD-16/17 的直接代价（[SCOPE+] #1 已如实声明）。
- **三态状态机 + task_id 承载立项**（BDD-9）：validator 只做枚举校验，`open + task_id` 合法不拦截，语义写进模板与判据文档——符合 review doc §5.2（无 gate 强制不引入中间态）。
- **schema 校验器独立于 agate-frontmatter-check.py**，既有 frontmatter 四类校验零触碰（BDD-10 兼容面收敛）。
- **回退强制 = 唯一新增硬强制**（retreat-to.sh 提醒 + state-transitions/P6/P4 卡片文档锚点 + --retreat-coverage 事后兜底只读提醒），与 review doc §4.1"不依赖价值判断的强制点"一致。

## 评审检查清单（dispatch-context 7 项）

1. **方案可行性**：fenced yaml + 独立校验器 + 回退比对子命令 + P8 debt_check 硬留痕四者自洽且均已对照现状代码验证；与 agate-frontmatter-check.py 兼容（0.2 明确不触碰）；`{...}` 占位符被 _sanitize_placeholders 处理、模板示例可解析（§0.3 风险行 3 已预警）。
2. **候选方案质量**：candidate_count=4，D1-D4 各 2 候选均为真实替代（1B 多块解析、2B 扩展既有校验器、3B 独立脚本、4B WARNING 软化），权衡表逐维度诚实，选择理由自洽，无稻草人。
3. **影响域完整性**：改什么（16 项清单）覆盖模板/校验器/回退比对/P8 卡片/check-gate.sh/mkdir 8→9/consistency 锚点/scripts README/两处 P8 fixture 面；不改什么明确（~/.agate、frontmatter 校验器、retreat 格式、TAG0003 主体、change_type、654 用例语义）；P0-brief known_risks 9 项全部有落点（回填止损 1、空确认止损 4、debt/ 归类修正同步面、dev/workspace 增量、change_type 衔接）；P1 §2.2 四项同步面（WORKFLOW 目录图、mkdir 三处、SETUP/UPGRADING、TAG0003 口径）+ P1-review N1-N4 全部收敛（N1→§2.6 BDD-4 判定口径、N2→source 枚举、N3→debt_check 显式字段、N4→v0.41.0 节不改）。
4. **BDD 可验收性**：§3 映射表 20/20 全部给出可执行验收路径（grep/实跑 mkdir/fixture 校验/修订注存在），二值可判定；BDD-10（no-op）与 BDD-13（retreat 缺失 WARNING）语义边界清晰不冲突。
5. **gate_commands**：P3/P5 命令紧凑可执行；ui_affected=false 正确（无 UI 面）；consistency/shellcheck/count-tests 走 AGENTS.md 标准流程。N-A 为唯一保留意见。
6. **SCOPE+ 审查**：#1（G8 fixture 同步）实测必需（不更新则 6 处既有用例全红，654 基线破坏）；#2（consistency 锚点 + scripts README 补录）实测必需（无锚点则 CHECK9-coverage WARNING，--strict 阻断）。两者均不新增 BDD、P1 scope_resolved 已登记，不扩大 P1 基线。
7. **止损条件**：止损 1（T001 回填失败=模板错）在 §2.8 无损判据 + §10 落地；止损 4（P8 空确认连续 3 次=移除强制）在 §2.5 `debt_check: none` 计数口径 + §10 落地；止损 2（自愿通道死）由 `source` 枚举（retreat|review|retrospective）提供数据可观测性，§10 给出后续强化方向。三者均有可观测数据形态，非空话。

## 结论

方案在工程维度上可行、自洽、可验收：关键事实假设全部经 worktree 实查证，候选决策点均有真实权衡，影响域覆盖 P0-brief 全部风险与 P1 全部同步面，20/20 BDD 二值可判定，2 项 SCOPE+ 均实测必需，止损条件有数据形态。无阻塞项；4 项非阻塞观察（N-A P3 TDD 覆盖面、N-B fixture 与 CHECK 1 交互、N-C schema 校验器调用点、N-D debt_check 取值开放项）供 P3/P4 执行时收敛。

**Status: approved**
