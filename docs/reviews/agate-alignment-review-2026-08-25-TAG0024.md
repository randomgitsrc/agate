---
date: 2026-08-25
task_id: TAG0024
reviewer: protocol-alignment-review
change_summary: "工具链批：新增 agate-md-field-set(-gate-commands).py 结构化字段写入工具（RM-AG0048 一期）+ check-gate.py roadmap-done 健壮性修复（DEBT0019/20）+ phases.yaml P4/P6.5 文档自洽（RM-AG0049/50）+ dispatch-prompt/dispatch-context 模板改为引导 set 工具"
files_changed:
  - agate/scripts/check-gate.py
  - agate/rules/phases.yaml
  - agate/assets/templates/dispatch-prompt.md
  - agate/assets/templates/dispatch-context.md
  - agate/scripts/agate-md-field-set.py (新建)
  - agate/scripts/agate-md-field-set-gate-commands.py (新建)
  - agate/tests/unit/test_agate_md_field_set.py
---

# 协议-脚本对齐审查（TAG0024 P4 SELF-GATE）

## 意图分析

1. RM-AG0048 一期：新增 `agate-md-field-set.py` + `agate-md-field-set-gate-commands.py`，给 subagent 提供"写入即校验"的字段写工具，value 校验通过 importlib 动态复用 `agate-frontmatter-check.py`/`agate-md-field-get.py`/`check-judge-verdict.py`（三者零改动，P2 既定设计）；同步把 `dispatch-prompt.md`/`dispatch-context.md` 的"直接复制 frontmatter 代码围栏"指引改为"用 set 工具填写"。
2. DEBT0019：`_check_roadmap_done()` 列数判据从 `len(cols) < 8` 改为 `!= 9`（`_ROADMAP_EXPECTED_COLS`），修复描述含字面 `|` 时的错位风险。
3. DEBT0020：`gate_p8()` 的 `roadmap_path` 改用 `git rev-parse --show-toplevel` 仓库根锚定，修复非仓库根 CWD 下静默跳过。
4. RM-AG0049：`phases.yaml` P4 outputs 补 `P4-review.md` 声明，对齐既有 `gate_p4()` 的实际要求。
5. RM-AG0050：`phases.yaml` P6.5 前追加注释，对齐 `state-machine.md` 已有表述。

## 反向传播文件清单（实际核实结果）

| 候选文件 | 是否需要同步 | 核实结论 |
|---|---|---|
| `agate/assets/execution-roles/implementer.md` | 检查是否提及 roadmap 检查内容 | grep 命中为空，无需同步 |
| `agate/state-machine.md` | P6.5 表述权威源 | 已有表述与 phases.yaml 新注释语义一致，无需改 |
| `agate/dispatch-protocol.md` | P4 产出文件表 | 第 396 行已列 `P4-review.md`，早已一致 |
| `agate/assets/templates/task-files.md` | status 枚举 | `draft/approved/rejected/done` 与工具 `DEFAULT_STATUS_ENUM` 一致 |
| 其他 roadmap.md 消费点（如 `check-retrospective.py`）| 是否也有 `split("|")` 列错位风险 | grep 全仓确认仅 `check-gate.py` 一处含 `split("|")` 模式，无需传播（P1-analyst 已排查，非本次遗漏）|
| `CHANGELOG.md` | 是否需要预留条目 | 本仓库惯例是任务到 P8/release 才追加（TAG0023→0.62.0），TAG0024 当前 P4，不需要 |
| `agate/scripts/README.md` / CHECK 9 锚点表 | 新脚本是否需要登记 | 两个新脚本文件名不匹配 `check-*.py` glob，反向覆盖检查不要求登记 |

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED（1 处，见下） |
| A2 | 脚本→文档对齐 | MISALIGNED（同上，dispatch-context.md 一处）|
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | NEEDS_HUMAN_REVIEW |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | NEEDS_HUMAN_REVIEW（建议项，不阻塞）|

## 逐项审查

### A1/A2: dispatch-context.md 的 `agate-md-field-set FILE ...` 语法与脚本实际调用惯例矛盾

**文档声明**（`agate/assets/templates/dispatch-context.md:31`，本次 diff 新增）：
> 用 `agate-md-field-set FILE --list` 查看本阶段应填字段；`agate-md-field-set FILE <key> <value>` 逐个写入

**脚本实现**（`agate/scripts/agate-md-field-set.py:388-397`）：
```python
def main():
    file_path = os.environ.get("FILE")
    args = sys.argv[1:]
    ...
    if not file_path:
        sys.stderr.write("agate-md-field-set: 需要 FILE 环境变量\n")
        return 1
```
FILE 路径只能经**环境变量**传入，脚本从不解析位置参数里的文件名（同惯例的 `agate-md-field-get.py`、脚本自身 docstring 第 4-6 行、`test_agate_md_field_set.py:35-36` 注释、`docs/design-notes/design-md-field-set.md` §5.1/§6.1「FILE 路径经环境变量传入（同 md-field-get / state-get 惯例）」均确认这一点）。

**实测复现**：
```
$ python3 agate/scripts/agate-md-field-set.py /tmp/test-p4-review.md --list
agate-md-field-set: 需要 FILE 环境变量
（退出码 1）

$ FILE=/tmp/test-p4-review.md python3 agate/scripts/agate-md-field-set.py --list
（正确执行，退出码 0）
```
若 subagent 照 dispatch-context.md 字面语法执行（把 FILE 替换成真实路径作为第一个位置参数），必定报错退出，与文档承诺的"先 `--list` 看"完全不符。

另外，该模板文件全篇占位符统一用 `{}` 包裹（`{P1-P8}`、`{Txxx}`、`{project_conventions_file}` 等，见同文件第 4/6/26/27 行），本次新增的裸词 `FILE` 打破了自身的占位符约定，进一步印证这不是"占位符写法"而是把 `agate-md-field-set-gate-commands.py`（该工具才是 FILE 位置参数，见其 docstring 第 4 行 `CLI：agate-md-field-set-gate-commands.py FILE <yaml块或@文件路径>`）的调用惯例误移植到了 `agate-md-field-set.py` 身上。

**结论**：MISALIGNED
**差异**：`dispatch-context.md` 新增的产出文件字段填写指引描述了一种 `agate-md-field-set.py` 不支持的调用语法。
**建议修复**：把 `dispatch-context.md:31` 改为 env var 语法，例如：
```
用 FILE=<文件路径> agate-md-field-set --list 查看本阶段应填字段；
FILE=<文件路径> agate-md-field-set <key> <value> 逐个写入
```
或按角色实际调用方式（bash 工具通常一次性设 env）调整措辞，但必须消除"FILE 作为第一个 CLI 参数"的误导。

**测试覆盖缺口说明**：`test_bdd_19_dispatch_templates_reference_set_tool_no_copyable_fence`（`test_agate_md_field_set.py:531-539`）只断言 "agate-md-field-set" 子串存在 + 旧代码围栏文案已移除，未对具体调用语法做正确性校验，因此这处错误未被 P3/P4 现有测试捕获。

### A1: check-gate.py DEBT0019/20 实现 vs P0-brief/analyst 缺陷描述

**文档声明**（`P0-brief.md:12-13`）：DEBT0019 要求"列数校验（非法列数跳过/WARNING）"；DEBT0020 要求"对齐 repo-root 定位（git rev-parse --show-toplevel）或加区分性 stderr 提示"。

**脚本实现**（`check-gate.py:1181-1206`、`1229-1245`）：`_ROADMAP_EXPECTED_COLS = 9` + `if len(cols) != _ROADMAP_EXPECTED_COLS: continue`；`gate_p8()` 用 `_git(["rev-parse", "--show-toplevel"])` 锚定 `roadmap_path`，失败时 `sys.stderr.write(...WARNING...)` 且跳过检查（非静默）。

**验证**：用真实 `agate-workspace/roadmap/roadmap.md` 数据行（含字面 `|` 的 RM-AG0048 描述行）手工复算 `line.split("|")` 长度确实为 9，与常量一致；`_git` 是 check-gate.py 已有的 helper（`check-gate.py:177`），非新引入。DEBT0020 的仓库根锚定模式与 `check-pruning.py`/`agate-risk-score.py`/`check-state-transition.py`/`install-hook.py`/`pre-commit-gate.py` 等既有脚本一致，非独创写法。

**结论**：ALIGNED

### A1: phases.yaml P4/P6.5 变更 vs 权威源

**P4 outputs**（`phases.yaml:62`）新增 `{file: P4-review.md, required: true, status_field: status}`，与 `gate_p4()`（`check-gate.py:871-877`，本次未改动、早已强制要求 `P4-review.md` 存在）语义完全对称，且结构与 P1/P2 的既有 `{file: PN-review.md, required: true, status_field: status}` 声明一致。

**P6.5 注释**（`phases.yaml:75-78`）与 `state-machine.md:74-78/152` 已有的"P6.5 是挂载于 P6→P7 转移的强门槛子阶段，非独立 phase 值"表述逐字对应。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

- `implementer.md` 未提及 roadmap 检查相关内容，无需同步（配套文件提示项已核实为"本来就不需要改"）。
- `task-files.md` 通用 Header 的 status 枚举、以及仅 P1/P2/P4 三个文件在 `phases.yaml` 声明 `status_field`，与 `agate-md-field-set.py` 的 `STATUS_ENUM_BY_BASENAME`（仅覆盖这三个 basename）精确对应，无遗漏也无多余。
- roadmap.md 表格解析的其他潜在消费点：全仓 grep `split("|")` 模式仅命中 `check-gate.py` 一处，`check-retrospective.py` 用的是不同解析方式，DEBT0019 的修复范围无需扩大（P1-dispatch-context-analyst.md 已预先排查此项，非本次审查新发现）。
- `dispatch-protocol.md:396` 早已列出 `P4-review.md` 为既有产出文件，无需因本次 phases.yaml 改动再同步。

**结论**：ALIGNED

### A4: 测试覆盖（独立实跑，非采信自报）

**独立执行**：
```
timeout 300s python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q
→ 3 failed, 1281 passed, 2 skipped in 137.75s
```
失败用例：`test_check_pruning.py::test_p2_6e_prune_p7_coupling_checklist_exit_0`、`test_p2_52_yaml_list_phases_exit_0`、`test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0`，均报 `裁剪 P7 需源码文件数 ≤ 5，实际=8`。

这与 `agate-workspace/tasks/TAG0024-toolchain-md-field-set/P4-implementation.md:49` 自报的 **"1284 passed, 2 skipped, 0 failed"** 不符。

**根因定位**：`check-pruning.py._staged_source_count()`（本次 diff **未改动**此函数）用 `git diff --cached --name-only` 读取**真实仓库**的暂存区（而非测试 fixture 的隔离 tmp_path），且 `tasks_base_rel` 是相对真实 `repo_root` 计算的，永远匹配不到 fixture 用的 tmp_path 路径，导致"排除任务产出文件"的机制对测试 fixture 完全失效。当前 worktree 因 TAG0024 自身处于待提交状态，暂存区里有 8 个不匹配排除正则的文件（`dispatch-context.md`/`dispatch-prompt.md`/`phases.yaml`/`agate-md-field-set.py`/`agate-md-field-set-gate-commands.py`/`check-gate.py`/`test_agate_md_field_set.py`/`gate-events.jsonl`），手工按脚本排除正则复算得 count=8，与实测完全吻合。

**判断**：这是 `check-pruning.py` 既有的测试隔离缺陷（依赖外层真实 git 暂存区状态而非隔离仓库），只在"自我修改协议脚本本身、且暂存文件数较多"的 SELF-GATE 场景下才会触发，**不是 TAG0024 本次代码改动引入的回归**——本次 diff 完全未触碰 `check-pruning.py`。但这也意味着 P4-implementation.md 的"0 failed"自报无法在当前暂存状态下复现（大概率是实现者分批 commit、暂存文件数较少时跑的），**不能直接采信为可复现证据**。`agate/tests/ENV-SENSITIVE-TESTS.md` 目前未登记这类"依赖外层 git 暂存区状态"的测试类别。

**结论**：NEEDS_HUMAN_REVIEW
**建议**：
1. 人工确认这 3 个失败确实是环境耦合而非回归（本报告已给出根因证据链，建议按"清空/减少暂存文件数后重跑"或"临时 unstage 后跑 pytest 再重新 stage"验证一次）。
2. 建议登记进 `ENV-SENSITIVE-TESTS.md`，避免下次 SELF-GATE 场景重复排查同一个假阳性。
3. `check-pruning.py._staged_source_count()` 的 fixture 隔离缺陷本身可考虑登记为新 DEBT（不在本任务范围内，不阻塞本次 commit）。

`[HUMAN_CONFIRMED: 待人工确认]`（本项尚未获得人工确认标记，按闭环规则等同 MISALIGNED，不应在未确认前 commit；若人工判断确系环境噪音，请补充 `[HUMAN_CONFIRMED: 日期 确认：理由]` 后放行）。

### A5: 下游影响 + 文档传播

- `check-gate.py` 的两处修复只收紧/修正既有判据，对合法 `roadmap.md` 现有数据的判定结果不变（BDD-21/24 回归用例覆盖，P4-implementation.md 报告独立重跑 `test_check_gate.py`: 182 passed）——不构成破坏性变更。
- `phases.yaml` 改动为纯追加（新增一行 outputs 声明 + 注释块），未修改任何既有字段结构。
- CHANGELOG.md：按本仓库既定惯例（`## [0.62.0] - 2026-08-25` 对应已完成的 TAG0023，任务到 P8/release 节点才追加条目），TAG0024 当前处于 P4，尚不需要 CHANGELOG 条目，非遗漏。
- 需要传播的文档（dispatch-prompt.md/dispatch-context.md）本身就是本次 diff 的一部分，已同步；唯一遗留问题已计入 A1/A2 的 MISALIGNED。

**结论**：ALIGNED

### A6: 锚点表覆盖

`agate/scripts/check-protocol-consistency.py` 的 CHECK9 反向覆盖检查（`check_anchor_coverage`）只扫描 `agate/scripts/check-*.py` glob + `pre-commit-gate.{sh,py}` + `ci-gate-backstop.py`。新增的 `agate-md-field-set.py` / `agate-md-field-set-gate-commands.py` 文件名不匹配该 glob（前缀是 `agate-` 不是 `check-`），且两者定位也确实不是 gate 判定脚本（design note §5.8 明确"set 不是 gate 替代品"），因此不要求登记进 `SCRIPT_ALIGNMENT_ANCHORS`。`check-gate.py` 本身的改动是既有函数内部逻辑修正，非新增脚本，锚点表无需新增条目。

**结论**：ALIGNED

### A7: 设计原则一致性（ADR）

- DEBT0020 的 `git rev-parse --show-toplevel` 仓库根锚定模式，与仓库内 `check-pruning.py`/`agate-risk-score.py`/`check-state-transition.py`/`install-hook.py`/`pre-commit-gate.py` 等既有脚本的一致做法吻合，未引入新架构决策。
- `agate-md-field-set.py` 的 importlib 动态加载模式复用 `check-routing.py._load_script` 既有先例（非新发明），其"单工具 + frontmatter 统一读写"的整体定位是 ADR-007（机器字段并入 frontmatter，单工具双读）在写侧的对称延伸，未违反 ADR-007 的核心论点（LLM 产出者场景下单文件优于独立事实文件），符合 YAGNI（未过度设计成多工具拆分）。
- design-md-field-set.md §7.1/§7.4 明确记录了一条有复用价值的架构原则——"set 端权限是引导与早纠错，不是安全边界；真正的安全边界在 gate 链（agent 字段 + 账本 + 独立 judge）"，这条原则目前只停留在 design note，尚未沉淀进 `agate/adr.md`。考虑到 `adr.md` 现有 ADR-001（隔离性）、ADR-002（可判定性）等都在讨论"谁能改什么、怎么保证不被绕过"这类安全边界问题，这条原则与既有 ADR 群体主题高度相关，建议后续（不必在本任务内）补充一条 ADR 记录，供未来任何"引导型 CLI 工具"设计参考，避免同类工具重新论证一遍"权限是引导不是安全边界"。

**结论**：NEEDS_HUMAN_REVIEW（仅 A7 的补充 ADR 建议项，属指导性建议，不阻塞 commit；ADR-007/YAGNI/既有模式一致性部分本身是 ALIGNED）
`[HUMAN_CONFIRMED: 待人工确认是否需要在本任务或后续任务内补充 ADR-011]`

## 闭环状态（2026-08-25 复核更新，全部关闭）

| 结论 | 处理状态 |
|------|----------|
| A1/A2 MISALIGNED（dispatch-context.md FILE 语法）| **已修复**：`dispatch-context.md:31-32` 改为 `FILE=<文件路径> agate-md-field-set ...` env var 语法，`git diff` 确认只改这两行；实测 `FILE=<路径> python3 agate/scripts/agate-md-field-set.py --list` 执行成功。`[HUMAN_CONFIRMED: 2026-08-25 用户确认：修复方案正确，放行]` |
| A4 NEEDS_HUMAN_REVIEW（pytest 3 failed vs 自报 0 failed）| **已修复（两轮）**：第 1 轮给 `check-pruning.py._staged_source_count()` 两处 `run_git` 调用加 `cwd=task_dir`（根因修复，新增回归测试 `test_p2_6f_*` 验证），第 2 轮发现本仓库强制的 `--basetemp=.pytest-tmp` 使 `task_dir` 物理嵌套在真仓库内、第 1 轮修复不足以让原 3 个用例转绿，复用本仓库已有的 `GIT_CEILING_DIRECTORIES` 先例（`test_bdd_23_p8_repo_root_unavailable_distinct_warning` 同技术）补齐。独立复核：`python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q` → **1285 passed, 2 skipped, 0 failed**（当前大量暂存文件的真实场景下）。`[HUMAN_CONFIRMED: 2026-08-25 用户确认：两轮修复方案正确，放行]` |
| A7 NEEDS_HUMAN_REVIEW（补充 ADR 建议）| **已处理**：用户确认"现在就补一条 ADR-011"，已在 `agate/adr.md` 新增 ADR-011「引导型 CLI 工具的权限是早纠错，不是安全边界」，`check-protocol-consistency.py --strict-errors-only` 复核 exit 0（无新增 ERROR）。`[HUMAN_CONFIRMED: 2026-08-25 用户确认：现在补充 ADR-011]` |

全部三项结论均已关闭（ALIGNED 或已确认修复），无遗留 MISALIGNED，SELF-GATE 审查通过，可推进 commit。
