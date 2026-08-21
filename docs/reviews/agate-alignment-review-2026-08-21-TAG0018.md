---
review_date: 2026-08-21
reviewer: protocol-alignment-review
task_id: TAG0018
change_summary: agate 原生支持 DSH（deepseek-harness）平台：新增 assets/templates/dsh/ 三模板（agent.cordis.yml / preset.yml / SKILL.md）+ SETUP.md「步骤 2-DSH」章节 + platform-notes.md DSH 条目 + tests/README.md 映射行 + tests/unit/test_dsh_preset.py（8 用例）；版本 bump v0.56.0 → v0.57.0（README badge ×2 / CHANGELOG [0.57.0] / UPGRADING v0.57.0 章节）
files_changed: [agate/SETUP.md, agate/assets/templates/dsh/SKILL.md, agate/assets/templates/dsh/agent.cordis.yml, agate/assets/templates/dsh/preset.yml, agate/platform-notes.md, agate/tests/README.md, agate/tests/unit/test_dsh_preset.py, CHANGELOG.md, README.md, README.zh-CN.md, agate/UPGRADING.md]
---

# 协议-脚本对齐审查

> 审查对象：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0018`（分支 feat/TAG0018-dsh-platform，HEAD 0ccbfd7，main=1272b0c v0.56.0）
> 审查范围：`git diff main...HEAD`（7 个 agate/ 文件，P0~P6 提交）+ 工作区未提交的 bump 4 文件（README/README.zh-CN/CHANGELOG/agate-UPGRADING，P8 releaser 已编辑，commit 待主 Agent）
> 实跑环境：Linux，Python 3.12.3，pytest 9.0.3；/tmp 只读 → pytest 以 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp-*` 适配

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED（1 项：README 平台表缺 DSH 行） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | MISALIGNED（同 A3 缺口：README「Supported platforms」表未同步） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**总评**：needs-fix（1 个 MISALIGNED 问题，修复成本低——README 平台表补一行；其余六项 ALIGNED）。

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（SETUP.md:144-171「步骤 2-DSH」）：
> DSH 的接入方式与 OpenCode/Claude Code 完全同构——注册 orchestrator 身份就是符号链接；协议模板文件在 `{agate_root}/assets/templates/dsh/`；命令块 = `mkdir -p` + 三条 `ln -sf`（指向 `~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml,SKILL.md}`）+ `python3 ~/.agate/scripts/install-hook.py`

**脚本/检查器实现**：
- `check-protocol-consistency.py`：`PROTOCOL_DIRS` 含 `agate/assets/`（L68）→ 新增模板目录天然纳入协议文件扫描面；`NARRATIVE_DIRS` 白名单（L77）不含 `agate/assets/` → 模板不会被宽松豁免。实跑：除 CHECK 7 时序 ERROR 外 0 ERROR。
- 模板结构（YAML 行结构 / tool-fs-search 必填配置 / frontmatter）**不由** check-protocol-consistency.py 校验——该检查器只解析 `.md` 内的 ```yaml 代码块（CHECK 1）与引用路径（CHECK 2），不扫描独立 `.yml` 模板文件。模板结构守护由 `test_dsh_preset.py`（8 用例）承担——这是检查器设计边界（结构检查只管 `.md` 协议文件）与测试层（模板结构）的合理分工，非文档-脚本矛盾。`agent.cordis.yml` 内的 `!!js process.platform === 'win32'` 自定义标签由测试 `_js_loader()` 容忍解析（test_dsh_preset.py:43-52），与 DSH schemastery 语义一致。
- `SETUP.md` 引用的 `~/.agate/assets/templates/dsh/...` 与 `{agate_root}/assets/templates/dsh/` 路径：`~` 前缀 / `{` 占位符均被 CHECK 2 的 `PATH_IGNORE_SUBSTRINGS`（L80-93）豁免 → 无误报；`platform-notes.md` 的 `assets/templates/dsh/` 无扩展名结尾不匹配 REF_RE（L241）→ 无误报。实跑证实 0 新增死链 ERROR。

**结论**：ALIGNED
**差异**：无。新增模板/文档与一致性检查器无矛盾；模板结构校验职责归属测试层（设计使然，已在 P2-design §3 交付物 6 声明）。

### A2: 脚本→文档对齐

**脚本逻辑**：本任务无任何 `agate/scripts/*.py` / `*.sh` 逻辑改动（diff 中 7 个文件全部为模板/文档/测试；bump 4 文件为文档）。无脚本行为变化 → 无"脚本已改、文档未跟"的反向问题。

**对应文档**：平台接入步骤单一真相源 = SETUP.md「步骤 2-DSH」（platform-notes.md:173-175 显式互链指向）；唯一安装脚本 `install-hook.py` 在 scripts/ 实存（P6 BDD-9 已 grep/find 复证：无 install-dsh.py、无 per-platform installer）。

**结论**：ALIGNED
**差异**：无。

### A3: 一致性连锁 + 反向传播

**A3a 连锁（已知衍生改动，逐项验证）**：

| 应连锁文件 | 是否落实 | 验证 |
|-----------|---------|------|
| `agate/tests/README.md`（脚本→测试映射表补行）| ✅ | diff 中 +1 行 `unit/test_dsh_preset.py \| 8`（M-7，P1 [SUGGEST] 第 2 条）|
| `agate/platform-notes.md`（DSH 条目，与 SETUP 互链）| ✅ | diff +22 行：`## DSH（deepseek-harness）` h2 + 六项能力表 + 已知注意 + 指向 SETUP.md「步骤 2-DSH」单一真相源 |
| `agate/UPGRADING.md`（v0.57.0 章节）| ✅ | 工作区 +14 行：`### v0.57.0 — DSH 平台支持（无破坏性变更）`，位于「3. 已知破坏性变更」节（L92），与既有 v0.52.0「无破坏性变更」同构 |
| `CHANGELOG.md`（[0.57.0] 节）| ✅ | 工作区 +43 行：`## [0.57.0] - 2026-08-21` 于 [0.56.0] 之上，含新增/关键机制/说明三小节 |
| `README.md` / `README.zh-CN.md` badge | ✅ | 工作区各 +1 行：`version-v0.57.0-blue` |

**A3b 反向传播（应被影响但 diff 未列出的文件，主动推断）**：

| 候选文件 | 应受影响理由 | 实际状态 | 判定 |
|---------|-------------|---------|------|
| `README.md` L58-64「Supported platforms」表 | CHANGELOG [0.57.0] 声明"DSH 成为 agate 官方支持的第三个平台（继 OpenCode、Claude Code 之后）"——README 平台表是用户可见的官方平台支持清单，新增官方平台应同步补行 | **表仍只有 OpenCode / Claude Code / Claude Project sessions 三行，无 DSH** | **MISALIGNED** |
| `README.zh-CN.md` L58-64 同表 | 同上（中文版对等） | 同英文版，无 DSH 行 | **MISALIGNED**（同一缺口两文件） |
| `agate/WORKFLOW.md` L5「适用：OpenCode / Claude Code / Codex 等支持 subagent 的 Agent 平台」| 平台适用声明 | 用「等」字开放列举，语义上不排除 DSH；且 L467 声明 platform-notes.md 是权威唯一来源、本文件不重复维护 | 不构成硬矛盾（轻微，见 A5 提示）|
| `agate/AGENTS.md` L29「不同平台适配（OpenCode/Claude Code/Windows）」| 导航性平台列举 | 指向 platform-notes.md（已更新）；「适配」语义含 Windows 非平台形态，属导航举例 | 不构成硬矛盾（轻微）|
| `README.md` L37 / L75 平台步骤列举 | 同上 | 「Platform-specific steps — OpenCode, Claude Code, and Windows」导航举例，指向 SETUP.md/platform-notes.md（均已更新）| 不构成硬矛盾（轻微）|

**结论**：MISALIGNED（1 项）
**差异**：README.md / README.zh-CN.md「Supported platforms」表未补 DSH 行——与 CHANGELOG [0.57.0]「官方第三平台」声明形成文档间字面矛盾（声明了支持、清单未列入）。P2-design M-1~M-7 改动声明未含 README 平台表（设计层遗漏），且无 P7-consistency.md（P1 已裁剪 P7，coupling_checklist 显式互链 checked），无 `[DESIGN_GAP: ... REVIEWED-ACCEPTED]` 记录可豁免 → 按正常 MISALIGNED 处理。
**建议**：README.md 与 README.zh-CN.md 的平台表各补一行 `| DSH | ✅ | Full P0-P8 |`（Task tool 列对应 subagent/subagent_fork，与 OpenCode/Claude Code 行同构），并同步平台表下方指向 platform-notes.md 的注记（可选加 DSH 字样）。

### A4: 测试覆盖

**本任务测试**：`agate/tests/unit/test_dsh_preset.py` 8 用例（BDD-1/2/3/4/5/7/8/9/15/16/17 覆盖）。

**实跑输出（本次审查亲自执行）**：

```
$ python3 -m pytest agate/tests/unit/test_dsh_preset.py -v -p no:cacheprovider --basetemp=.../ptmp-review
collected 8 items
test_dsh_agent_cordis_rows_have_id_and_name PASSED
test_dsh_tool_fs_search_has_required_config PASSED
test_dsh_persona_is_thin_identity PASSED
test_dsh_preset_yml_has_name_and_description PASSED
test_dsh_skill_frontmatter_valid PASSED
test_dsh_setup_section_and_symlink_commands_present PASSED
test_dsh_setup_dsh_section_within_step_2 PASSED
test_dsh_setup_section_has_install_hook_call PASSED
============================== 8 passed in 0.04s ===============================
```

**全量 pytest（本次审查亲自执行，bump 状态）**：

```
$ python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=.../ptmp-full
3 failed, 1033 passed, 2 skipped in 93.85s
FAILED test_consistency.py::test_con_1_check_1_yaml_parseable
FAILED test_consistency.py::test_con_6_check_7_version_badge_sync
FAILED test_consistency.py::test_bdd_25_consistency_zero_error
```

**3 个失败归因验证（非回归，非本任务引入）**：三例均为 consistency 断言（CHECK 7 version badge 与最新 git tag 一致性）。bump 已完成（badge=v0.57.0）但 tag v0.57.0 尚未创建（`git describe --tags --abbrev=0` = v0.56.0）——这是 P8 卡「gate 规则」DEBT0013 明示的时序中间态，tag 创建后消失。本人执行 `git stash`（临时移除 4 个 bump 文件）后重跑同三例 → **3 passed**；随后 `git stash pop` 完整还原工作区（git status 确认 bump 4 文件恢复原状）。bump 前基线 0 ERROR（P8-release §5 记录 + 本次 stash 实跑互证），bump 未引入任何新 WARNING（319 基线不变，本次实跑 321 = 319 + 2 条本报告路径占位引用，落盘后消失）。

**边界守护有效性**：
- tool-fs-search 必填配置：`test_dsh_tool_fs_search_has_required_config`（用例 2）断言 `config.sampleOverCapGlobResults is False`——P6 BDD-17 已做红/绿双态实跑（移除配置 → 1 failed；恢复 → 8 passed；md5 校验还原 + git 无 diff），护栏真实有效而非空断言。
- 章节切片断言（`_dsh_section`，test_dsh_preset.py:74-86）刻意防止"DSH 章节漏写 install-hook.py 调用"被 SETUP.md 其他章节的既有引用掩盖——BDD-9 守护到位。
- 平台无关（BDD-16）：静态核查四条禁止项 0 命中 + 空 HOME 环境 8 passed（P6 证据），无 DSH 实例的 CI 可跑。

**结论**：ALIGNED
**差异**：无。8 用例实测全绿，全量 3 失败全部归因 CHECK 7 时序态并经 stash 对照验证非回归。

### A5: 下游影响 + 文档传播

**下游影响**：无破坏性变更（交付物全部为新增文件 + 文档追加章节，未改动任何既有协议机制运行时行为——UPGRADING v0.57.0 章节与 CHANGELOG [0.57.0]「说明」小节均明确声明）；既有项目升级 = `git pull` + 重跑 `install-hook.py`，与既有平台一致。不触发任何既有项目的 gate 行为变化（无 check-*.py 改动）。

**CHANGELOG 标注**：✅ [0.57.0] 节完整覆盖（新增/关键机制/说明），单条目对应 9 commits 无遗漏（P8-release §1 对照）。

**文档传播**：
- 应同步且已同步：SETUP.md / platform-notes.md / tests/README.md / UPGRADING.md / CHANGELOG.md / README badge（见 A3a 表）✅
- 应同步但未同步：**README「Supported platforms」表（中英两文件）** ❌（同 A3b，本项重复计数同一缺口）
- 轻微提示（不判 MISALIGNED）：`WORKFLOW.md:5` / `AGENTS.md:29` / `README.md:37,75` 的开放列举（「等」/ 导航举例）未含 DSH——语义上不构成矛盾（权威源 platform-notes.md / SETUP.md 均已更新），但作为可选卫生项可在后续顺手补「DSH」。

**结论**：MISALIGNED（1 项，同 A3 缺口：README 平台表文档传播不完整）
**差异**：官方第三平台的用户可见声明（README 平台表）未与 CHANGELOG/UPGRADING 的发布声明同步。
**建议**：同 A3b 建议（补两处 README 平台表 DSH 行）。

### A6: 锚点表覆盖

**CHECK 9 锚点表**（`SCRIPT_ALIGNMENT_ANCHORS`，check-protocol-consistency.py:473+）：白名单式"文档声明规则 → 脚本关键词"，覆盖对象是 gate 脚本（check-*.py / pre-commit-gate / ci-gate-backstop）。本任务**未新增/修改任何 gate 脚本**（test_dsh_preset.py 是测试文件，非 gate 脚本；模板文件非脚本）→ 锚点表无新增条目需求。

**反向覆盖**（`check_anchor_coverage`，L730-762）：遍历 gate 脚本目录确认每脚本在锚点表有锚点——本任务无新 gate 脚本，不触发"脚本未纳入锚点表"警告。实跑确认 0 新增 ERROR/WARNING。

**结论**：ALIGNED
**差异**：无。锚点表无需更新（无新 gate 脚本）；新增模板/测试文件不属于锚点表管辖对象（锚点表校验的是"脚本存在且被正确挂载调用"，模板结构由 A4 测试层守护）。

### A7: 设计原则一致性

逐条核对相关 ADR（agate/adr.md）：

| ADR | 内容 | 本任务符合性 |
|-----|------|------------|
| ADR-003 最小约定——不绑定技术栈 | 不发明新结构 | ✅ 平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py；无 platforms/ 目录（模板在既有 `assets/templates/dsh/` 子目录）、无 install-dsh.py（P6 BDD-9 实跑复证）|
| ADR-008 orchestrator 符号链接接入 | 文件级符号链接 + 模板单一来源 + 升级自动跟随 | ✅ DSH 接入用 agent-preset 符号链接（三条 `ln -sf` 指向 `~/.agate/assets/templates/dsh/`），persona 薄身份指向 orchestrator-template.md（不复制模板），「身份薄、协议厚」与 ADR-008 的"模板随 ~/.agate 升级自动更新"精神一致；Windows 复制模式退化与既有小节同构 |
| ADR-005 改动性质决定流程 | 声明性/行为逻辑/机制交叉分流程 | ✅ 纯声明性交付（新增模板+文档），P1 裁剪 P7 合理（P1 §5 论证：无既有代码路径修改，测试断言替代 P7 一致性职责）|
| ADR-009 ~/.agate 版本管理根 | resolve-entry 固定解析入口 | ✅ 未改动版本管理机制；bump 仅文档 4 处 |

未发现违反 ADR 的架构决策；未发现需补充新 ADR 的未记录决策（DSH preset 接入形态由 DSH 平台机制强制，SETUP.md/platform-notes.md 已文档化，P2-design S-8 已判定与 custom-role.md 是不同机制、不冲突）。

**结论**：ALIGNED

## 问题清单

1. **[MISALIGNED] README「Supported platforms」表缺 DSH 行**（A3b/A5）
   - 位置：`README.md:58-64` 与 `README.zh-CN.md:58-64`（工作区文件，bump 已改 badge 但未补平台表）
   - 证据：CHANGELOG [0.57.0]「新增」首条 = "DSH（deepseek-harness）成为 agate 官方支持的第三个平台"；README 平台表仅 OpenCode / Claude Code / Claude Project sessions 三行
   - 影响：官方平台支持的用户可见清单与发布声明不一致；读者从 README 无法得知 DSH 支持
   - 修复方向：两文件平台表各补 `| DSH | ✅ | Full P0-P8 |` 行（Task tool 列对应 subagent/subagent_fork）；可选同步表下注记
   - 备注：无 `[DESIGN_GAP: ... REVIEWED-ACCEPTED]` 记录可豁免（P7 已裁剪，P4 执行决策 4 条均不涉 README 表）

## 闭环规则

| 结论 | 主 Agent 动作 |
|------|--------------|
| ALIGNED（A1/A2/A4/A6/A7）| 通过 |
| MISALIGNED（A3/A5，问题清单 1 项）| **必须修复**——README 两文件平台表补 DSH 行，修完重审（或由主 Agent 确认 README 平台表不在本任务传播面后标注 NEEDS_HUMAN_REVIEW + `[HUMAN_CONFIRMED: ...]`）|

## 附注（审查过程关键事实）

- 本报告写入前已确认目标路径不存在（`ls docs/reviews/agate-alignment-review-2026-08-21-TAG0018.md` → 无此文件），DEBT0011 写入前检查通过，无跨任务覆盖风险。
- 留痕文件：`docs/reviews/agate-alignment-2026-08-21-TAG0018-01.progress.md`（11 行原始痕迹）。
- 审查期间 consistency 输出含 2 条本报告路径占位 WARNING（`agate-workspace/.../P8-dispatch-context-protocol-alignment-review.md:13,22` 引用本报告路径）——本报告落盘后自动消失，WARNING 数回落至 319 基线。
- 审查仅读/跑/写报告，未修改任何交付物文件；`git stash` 对照实验已完整还原（git status 与审查前一致）。
