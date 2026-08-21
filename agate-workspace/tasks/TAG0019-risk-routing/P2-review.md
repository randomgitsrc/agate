---
phase: P2
task_id: TAG0019-risk-routing
type: review
parent: P2-design.md
trace_id: TAG0019-P2-20260821
status: approved
created: 2026-08-21
agent: plan-eng-review
---

# P2 方案评审（rev2 复审）— TAG0019 风险分路由（计划工程维度）

> 复审对象：P2-design.md（rev2，341 行）
> 依据：rev2 dispatch-context（增量轮）+ plan-eng-review 角色定义 + P1-requirements.md（15 BDD）
> 结论：**approved** —— 上轮 rejected 的 BLK-1 + NB-1~4 + 测试缺口全部修订到位并经独立复核/实测确认，全量复评无新不一致。残留 1 个非阻塞修订建议（NB-1a）+ 2 个微观察。
> 本轮独立实测：① worktree 5 个 P5_platform target 路径检查（3 既有文件存在、4 新文件 P4 产出属预期）；② 扫描器单文件 target 语义实测（现存文件 RC=0 / 不存在 RC=2）。

## 阻塞级问题复核结论

- **[BLK-1] P5_platform 收窄为变更文件集 — 已闭环（approved 条件满足）**
  - P2-design §4 `P5_platform`（:283）：target = `agate-risk-score.py` + `check-routing.py`（worktree scripts）+ 5 个测试文件（test_agate_risk_score / test_check_routing / test_check_frontmatter / test_agate_md_field_get / test_pre_commit_hook）——已不含 scripts 全树，且不再传递任何目录 target。
  - 三处措辞一致：§0.3 R5（:103"本任务变更文件集…扫描 **0 命中**（…既有 scripts 树存量命中不阻塞，记入评审备查 BLK-1）"）；§4 说明（:288 逐条列出既有命中证据：agate-install.py:326,330,396 R2 / check-platform-assumptions.py:22,38 R3/R1 自伤 / 3 个 sh hook R2 / pre-commit-gate.py:61 / install-hook.py:128 R2，并声明"均落在 §0.2 Not Modify 文件上…记入评审备查"）；§5（:340"platform 变更文件集 0 命中（存量 scripts 树命中不阻塞，评审备查 BLK-1）"）。
  - **独立实测（本轮）**：① 5 个测试文件路径中 3 个既有文件（test_check_frontmatter.py / test_agate_md_field_get.py / test_pre_commit_hook.py）真实存在，4 个新文件（2 新脚本 + 2 新测试）属 P3/P4 交付物（P5 时存在，预期）；② 扫描器单文件 target：现存文件 → RC=0（0 命中，命令形态可用）、不存在 target → RC=2（"目标不存在"）→ P5 时任一变更文件未产出即红灯（fail-closed，验收强制成立）。**基线不再有 scripts 树存量命中进入扫描面**，P5_platform 可绿。

## 非阻塞修订项复核结论

- **[NB-1] full→P7 声明层+评审层保证 — 闭环（含 1 个残留分支建议 NB-1a）**
  - D2（:208）：P1 卡 ceremony 说明补「声明 ceremony: full 的任务 phases 必须含 P7」（与 thin 的 P5/P6 保留要素同构）；D4（:242）③ 评审清单补「声明 ceremony: full → phases 含 P7」核对项，不一致 → needs-revision/rejected；§2.6（:254-257）删"通常伴随"推断，改为显式三重保证（声明层 + 评审层 + C8 评审映射），并正确论证"check-pruning 检查 7 三类条件（源码数>5 / implicit_coupling / coupling_checklist）不覆盖 full 语义，故不可依赖既有 gate 联动"。
  - **[NB-1a 残留，非阻塞，建议本轮一行修订]**：D4 ③（:242）核对条件只覆盖「声明 ceremony: full」分支；BDD-14 Given 的「算分 tier=full」分支（无 full 声明的任务）的 P7 不可裁无核对触发——该场景下（敏感路径/影响面单信号 high 且源码数≤5、无 implicit_coupling、coupling_checklist 齐全）既有 gate 不拦 P7 裁剪，声明层/评审层均不触发。建议 :242 核对条件扩为「算分 tier=full **或** 声明 ceremony: full → phases 须含 P7」，§3:271 的 grep 断言同步扩两分支；不修订亦可接受（P6 验收 BDD-14 按声明层 + 评审派发两分支口径执行，算分分支由 check-pruning 源码数>5 部分兜底），但低成本封死更稳。
- **[NB-2] 错误边界 exit 语义 — 闭环（含 1 个微观察）**
  - :231-233 补两条：① P1-requirements.md 缺失 → exit 2（对齐同链 check-pruning，与"不声明=standard"的 exit 0 明确区分，防破损目录静默通过）；② 算分异常分支：score_task 输出 `git_ok: false` 标记（不静默降级）+ `ceremony: thin` 且 `git_ok: false` → exit 1（fail-closed，防"算分偏薄误放行"的 fail-open 边缘）；standard/full 声明下 git_ok:false 不拦截（更保守合法）。语义可判定、fail-closed 方向正确。
  - 微观察：§2.1 输出描述（:189）列了 risk_score/tier/证据行/domain-markers，未显式列 `git_ok` 键（:233 引入）——建议在 D1 输出契约补一行，保持 score_task 返回结构文档完整（P4 契约锚点）。
- **[NB-3] 影响面判据二值可判 — 闭环**
  - :179 精确化：扫描对象=暂存区每个改动文件 F（排除 tests/ 与配置类）、模块标识=basename 去扩展名、搜索面=repo_root 排除 task_dir 与 agate/tests/ 树、命中判据=存在 ≥1 行引用且所在文件非 F 自身 → high，无 → low；R9（:107）同步"按模块标识正则定位引用行"。判据满足 BDD-5 二值可判。
- **[NB-4] files_to_read 补格式先例 + P1-P2 清单不一致消除 — 闭环**
  - files_to_read 补 requirements-review.md:48-52（:310，D4 改写对象格式先例）与 role-system.md:54-70（:313，full 档映射行样式先例）。
  - §0.2 补齐三处交代（:90-92）：WORKFLOW:290 不处理（论证：评审角色映射权威源=role-system C8 表，总览表仅汇总引用，改副本=双源同步风险——与 review-mapping.md:9"权威源：agate/role-system.md"一致，论证成立）；P3/P7 卡:4 不细化（thin 仪式薄化与 phases 去留正交）；_GUARD_SCRIPTS 不追加（展示清单非 BDD-15 漂移清单）。
- **测试缺口 — 闭环**：§3 :266-271 补 check-routing 分支测试清单（正向/拦截/边界/对拍 + importlib 上下文 agate_common 可导入性断言）与 full-P7 文档条文 grep 断言（:271，NB-1a 修订时同步扩分支）。

## 全量复评（防修订引入新不一致）

- **candidate_count=3**（frontmatter :11）与正文三候选（§1.1 A / §1.2 B / §1.3 C）+ 权衡表（§1.4）+ 选择理由一致，未破坏。
- **四字段齐全**：packages [agate-protocol, agate-scripts, agate-tests] / domains [backend, security] / ui_affected: false / gate_commands（§4）——frontmatter-check schema 所需字段全。
- **gate_commands 其余 key 无回归**：P3（:280）/ P5（:281）pytest 带 `-p no:cacheprovider --basetemp=...`；P5_consistency（:282）用 worktree 自己的脚本 + `--strict-errors-only`（无 && 链、无短路，符合 P2 卡反模式规则）；P5_count_tests（:284）；P5_timeout_seconds: 90（:285）。无 key 声明 `&&` 拼接。
- **minimal_validation**（:324-328）未破坏：纯代码逻辑声明 + confirmed + 内部依赖列举（run_git:49 / _md_field / _read_p1 / _staged_source_count:30-81 / coupling_checklist & 跳过风险判据:141-157）——上轮独立复跑（importlib 三函数 callable / 非 git 目录 staged_count=0 / 带连字符模块可加载）结论仍成立。
- **影响面三部分**（§0 改什么/不改什么/风险在哪）在候选方案（§1）之前，齐全。
- **消费点同步主体**（BDD-15）：6 脚本注册点 + 10 文档 + tests/README 与 P1 清单一致（rev2 修订未删改）；worktree 涉改脚本与稳定版 cmp SAME（上轮核实仍有效）。

## 锁定决策（approved 确认）

1. 方案 B（独立 check-routing.py + importlib 同源复用）成立；BDD-10 复用真实（_md_field/:30-44、_read_p1/:47-53、_staged_source_count/:55-81 稳定版存在，import 非表面重写）。
2. 2j.1 挂载（pre-commit-gate.py:339 后，gate_exit != 1 条件）与 2j/2k 并列成立；ceremony 三节点注册链（frontmatter-check allowed/enums/types → md-field-get STRING_FIELDS → check-routing 语义校验）锚点全部核实。
3. fail-closed 三 BDD（7/8/9）流程闭环 + 错误边界（exit 2 / git_ok:false）补齐；P5/P6 双闸（check-routing 四要素 + check-pruning 检查 3/5）关系清楚。
4. P5_platform 变更文件集口径（BLK-1 修复）实测可执行（文件 target RC=0、缺失 RC=2）。
5. 多方案探索充分（candidate_count=3 真实权衡）；实现就绪度：files_to_read 覆盖脚本侧全上下文 + 文档侧格式先例，行号落点精确。

## 修订要求（非阻塞，architect 可选）

- **NB-1a（建议本轮补，一行）**：D4 :242 核对条件扩为「算分 tier=full 或声明 ceremony: full → phases 须含 P7」，§3:271 断言同步。
- 微观察 2 条（不强求）：§2.1 :189 输出契约补 `git_ok` 键；§4 :283 注释"按实际变更文件集调整"建议改为"若 P4 实际变更文件超集，主 Agent 在 P5 前对超集文件补跑同一扫描命令"（避免放松 gate_commands P2 固化契约的口径歧义）。