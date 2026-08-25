---
phase: P3
task_id: TAG0025
type: test-cases
parent: P2-design.md
trace_id: TAG0025-P3-20260826
status: draft
agent: test-designer
created: '2026-08-26'
test_code_dir: agate/tests/regression/
---

# P3 测试用例清单 — TAG0025 Agateon 品牌改名执行 Phase 0-1

> 本文件把 P1-requirements.md 的 16 条 BDD 逐条转成明确的验证手段（1:1 映射）。dispatch-context
> 已明确：本任务大部分"实现"是文本文件字符串替换 + 一次不可逆外部操作（GitHub 仓库改名），
> 因此 16 条 BDD 分两类处理——A 类（BDD-1~10，10 条）写成真实可运行的 pytest 测试代码，落在
> `agate/tests/regression/test_repo_url_no_stale_rename.py`；B 类（BDD-11~16，6 条）登记为
> 程序化验证用例，引用 P2-design.md 已固化的 `gate_commands` key，不塞进 pytest。

## test_code_dir

`agate/tests/regression/`

## A 类：可 TDD 红灯（BDD-1~10，pytest，共 11 个测试函数）

测试文件：`agate/tests/regression/test_repo_url_no_stale_rename.py`

沿用 P2-design.md 候选方案已确定的单文件命名，未拆分为多文件——7 处 URL 更新点集中在 5 个
文件、彼此断言逻辑高度共享（`_assert_old_cleared_new_present` 复用），CHANGELOG/品牌声明/
批次原子性/全仓残留扫描各自独立但同属"改名前后状态判定"这一单一主题，拆分不会带来隔离收益，
反而会打散 P2 已固化的 `gate_commands.P3 = "python3 -m pytest agate/tests/regression/ -v"`
与该文件路径的一一对应关系。

**兜底职责（呼应 P2-review.md「测试缺口」节，约束 2）**：`gate_commands.P5_bdd4to8_new_url_present`
只验证"新 URL 存在"，不验证"旧 URL 已清除"，单靠它拦不住"README.md 两处 URL 只改一处"这类
部分修复（BDD-7/8 明确禁止）。本测试文件的 BDD-4~8 用例对每个文件都同时断言两个方向：
① 不含字面 `randomgitsrc/agate\b`（旧 URL 已清除，word-boundary 排除 `agateon` 误判）
② 含字面 `randomgitsrc/agateon`（新 URL 已存在）。已在测试文件顶部注释里写明这层兜底关系。

`test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` 还额外兜底了
`gate_commands.P5_bdd10_residual_scan` 自身的一个已知盲区：该 gate key 的排除正则里 P2
architect 自行追加排除了 5 个核心文件本身（`install.sh:`/`README.md:`/`README.zh-CN.md:`/
`agate-install.py:`/`agate-changes.py:`），这 5 条排除项不属于 P1 BDD-10 声明的 5 类豁免
（P2-review.md 核查项 3 已指出这是 gate_commands 自行追加、未在"5 类豁免"叙述里说明理由的
排除项）。若全仓残留扫描沿用该排除正则，改名前这 7 处核心文件的旧 URL 命中会被悄悄吞掉，扫描
"看起来"是 0 残留，实为假阴性。本测试只应用 P1-requirements.md BDD-10 原文声明的 5 类豁免
（不含 gate_commands 额外追加的核心文件排除），因此改名前会真实命中这 7 处（已实测确认），
改名落地、其余位置未新增旧 URL 后才会转绿。

| BDD | 测试函数 | 断言方向 | 当前红灯原因（已实测） |
|-----|---------|---------|----------------------|
| BDD-1 | `test_bdd_1_readme_en_brand_statement_first_screen` | README.md 前 15 行含 "Agateon (formerly agate)" | 品牌声明句尚未插入 |
| BDD-2 | `test_bdd_2_readme_zh_brand_statement_first_screen` | README.zh-CN.md 前 15 行同时含 "Agateon" 与 "agate" | "Agateon" 尚未插入（"agate" 已存在但不满足"两词缺一不可"） |
| BDD-3 | `test_bdd_3_changelog_unreleased_section_above_0_63_0` | CHANGELOG.md 含 `## [Unreleased]` 段且位于 `## [0.63.0]` 段之上 | 当前 CHANGELOG 无 `[Unreleased]` 段（已实测核实，最新已发布段是 `[0.63.0]`） |
| BDD-3 | `test_bdd_3_changelog_tag0025_entry_under_unreleased` | `[Unreleased]` 段下含 TAG0025 条目 | `[Unreleased]` 段本身不存在，条目自然不存在 |
| BDD-4 | `test_bdd_4_install_sh_new_url_and_old_url_cleared` | install.sh 不含旧 URL 且含新 URL | 第 24 行当前仍是 `randomgitsrc/agate.git` |
| BDD-5 | `test_bdd_5_agate_install_py_new_url_and_old_url_cleared` | agate-install.py 同上 | 第 55 行 `DEFAULT_REPO_URL` 当前仍指向旧仓 |
| BDD-6 | `test_bdd_6_agate_changes_py_new_url_and_old_url_cleared` | agate-changes.py 同上 | 第 116 行文案内嵌 URL 当前仍指向旧仓 |
| BDD-7 | `test_bdd_7_readme_en_badge_and_install_entry_new_url_and_old_cleared` | README.md 第 5 行（badge）+ 第 29 行（安装入口）均指向新仓，且全文不含旧 URL | 两行当前均为旧仓 |
| BDD-8 | `test_bdd_8_readme_zh_badge_and_install_entry_new_url_and_old_cleared` | README.zh-CN.md 同上 | 两行当前均为旧仓 |
| BDD-9 | `test_bdd_9_seven_urls_same_commit_batch_atomicity` | 6 个文件（core 5 + CHANGELOG.md）`git log -1 --format=%H -- <file>` 的 SHA 全部相同 | 已实测：当前 5 个不同 SHA（README.md 与 CHANGELOG.md 恰好共享历史提交，其余互异），批次 commit 尚未发生 |
| BDD-10 | `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` | 全仓扫描（P1 BDD-10 原文 5 类豁免后）命中数为 0 | 已实测：命中数=7，精确对应 Phase1 核心 7 处更新点 |

### BDD-9 处理说明（呼应 dispatch-context 约束 4，"由你判断并说明理由"）

判定为 **A 类**（写成 pytest，而非归入 B 类）。理由：BDD-9 的判定逻辑是"检查 6 个文件最近一次
改动的 commit SHA 是否全部相同"——这个判定逻辑本身**当前就可执行**（`git log -1 --format=%H --
<file>` 对任意时刻的 git 历史都有确定输出），不属于"依赖尚未发生的不可逆外部操作、当前根本不
适用"的 B 类特征（B 类特征是"GitHub 改名前，旧仓库返回 200，不是应该失败但当前失败的红灯，
而是当前根本不适用的状态"——BDD-9 不符合这个描述，它随时可判定，只是**当前判定结果为 FAIL**，
这正是真红灯的定义）。已实测确认：当前 6 个文件的最近一次改动分散在 5 个不同 commit（`install.sh`
→ `dc5090b`、`agate-install.py` → `f752c73`、`agate-changes.py` → `fbf865b`、`README.md` →
`a0a2d14`、`README.zh-CN.md` → `7dc7417`、`CHANGELOG.md` → `a0a2d14`，其中 README.md 与
CHANGELOG.md 恰好共享历史提交但其余 4 个互异），断言"全部相同"当前为假 → pytest 断言失败 →
真红灯（AssertionError，非 SyntaxError/import 错误）。此断言逻辑与
`gate_commands.P5_bdd9_atomic_commit` 的 shell 实现（SHA 比对）同源复刻，不是脱离真正判定逻辑
的假断言。已在测试函数上方注释里注明"时序说明"：本用例在 P3/P4 阶段就能给出真实、有意义的
红/绿结果（不像 BDD-11~16 那样要等不可逆操作发生后才适用判定），但最终以 P5/P6 阶段
`gate_commands.P5_bdd9_atomic_commit` 的独立复跑结果为准（可独立于 pytest 环境重跑，是这条
BDD 的权威判定源，pytest 版本是提前捕获批次原子性风险的辅助手段）。

## B 类：不可 TDD 红灯（BDD-11~16，程序化验证用例，共 6 条）

这 6 条 BDD 依赖一次尚未发生、且要等主 Agent 获得用户在场确认后才会执行的不可逆外部操作
（GitHub 仓库改名）。改名发生之前，旧仓库 `randomgitsrc/agate` 正常返回 200——不是"应该失败
但当前失败"的红灯语义，而是"当前根本不适用"的状态（`git ls-remote` 对 `randomgitsrc/agateon`
现在会报仓库不存在，`in:name agateon` 搜索现在不会命中目标仓库，这些都不是"待修复的 bug"，
是"前提条件尚未成立"）。因此不写成 pytest 单元测试假装当前可判定，而是登记为**程序化验证用例**
——验证手段是明确的、可复跑的 shell 命令（P2-design.md 已固化为 `gate_commands` key），只是
执行时机本质上晚于 P3/P4，要等改名真正发生之后才能跑出有意义的结果。1:1 映射的目标是"每条 BDD
都有明确对应的验证手段"，不是"每条 BDD 都必须是 pytest 函数"。

| BDD | 验证手段 | 引用的 gate_commands key | 为何不适用红灯语义 | 何时可执行 |
|-----|---------|--------------------------|---------------------|-----------|
| BDD-11 | 会话时序人工确认（非文件/系统状态判定） | 无对应 key（P2-design.md 已明确说明：BDD-11 不落 gate_commands，强制力落在候选方案 §1 选定的执行分工本身——改名调用不下放给 implementer subagent，由主 Agent 在获得用户当次会话内明确放行确认后亲自执行） | 判定对象是"当次会话内是否发生了明确的人工放行确认"，这是一个会话时序事件，不是可以脱离会话上下文、事后用一条 shell 命令重放判定的文件/系统状态；写成 pytest 断言无从断言起（断言对象不存在于任何可读的持久化状态里） | 每次准备执行改名调用之前，由主 Agent 在当前会话内向用户发起确认，确认发生的那个时刻 |
| BDD-12 | curl 检查 301 状态码 + Location 头指向新仓 | `P5_bdd12_301_status`、`P5_bdd12_301_location` | 依赖 GitHub 真实的重定向行为，只有改名真正发生后才可观察——改名前旧仓库正常 200 响应，不存在"应该 301 但现在不是 301"的中间态可供断言，是"当前根本不适用" | 改名调用成功执行之后 |
| BDD-13 | `git ls-remote` 对新仓名执行，检查返回码与 SHA 输出 | `P5_bdd13_ls_remote` | 改名前 `randomgitsrc/agateon.git` 不存在，`git ls-remote` 会返回"仓库不存在"错误——这不是"实现有 bug 导致的失败"，是"验证对象尚未存在" | 改名调用成功执行之后 |
| BDD-14 | GitHub 搜索 API 检查 `in:name agateon` 是否命中目标仓库 | `P5_bdd14_search` | 依赖改名后 GitHub 搜索索引更新（BDD-14 Given 子句本身已用"且 GitHub 搜索索引已更新"限定前提），索引更新时序不可控，改名前该仓库压根不叫 agateon，搜索无从命中 | 改名调用成功执行、且搜索索引已更新之后（失败时按索引延迟复跑，非直接判定实现有误） |
| BDD-15 | 主 checkout 与 worktree 的 `git remote -v` 均检查是否已指向新仓 | `P5_bdd15_remote_main`、`P5_bdd15_remote_worktree` | 依赖 `git remote set-url` 已在主 checkout 执行——该操作属于候选方案 P4 批次 2（改名确认成功后才派发），当前尚未发生，remote 现在必然仍指向旧仓，断言"已指向新仓"当前恒假但并非"待修复的实现缺陷"，是"前置操作尚未执行" | remote 迁移（`git remote set-url`）在主 checkout 执行之后 |
| BDD-16 | 主 checkout 与 worktree 各执行一次 `git fetch`，检查返回码为 0 | `P5_bdd16_fetch_main`、`P5_bdd16_fetch_worktree` | 验证性抽查的对象是"迁移后 fetch 是否成功"，在迁移发生前执行这条命令测的是"迁移前对旧仓 fetch 是否成功"，与 BDD-16 要验证的语义（迁移后仍能正常 fetch）完全不同，提前跑没有意义 | remote 迁移完成之后 |

### 环境隔离声明

本文件的编写过程未执行任何 `git remote set-url` / `gh api -X PATCH` / `git push` 等写操作，
未接触主 checkout（`/home/kity/oclab/agate`）与 `~/.agate`，不涉及生产环境。`[PROD_NOT_TOUCHED]`。

## 红灯确认（客观事实陈述）

`python3 -m pytest agate/tests/regression/test_repo_url_no_stale_rename.py -v` 已实跑：
11 个测试函数全部 FAILED，失败类型均为 `AssertionError`（真红灯，非 SyntaxError/项目外
import 错误），失败内容与上表「当前红灯原因」逐条对应。同批跑 `agate/tests/regression/`
全目录（`python3 -m pytest agate/tests/regression/ -v`）：新增的 11 个红灯之外，既有 17 个
回归测试全部通过（本次新增未破坏既有回归套件）。
