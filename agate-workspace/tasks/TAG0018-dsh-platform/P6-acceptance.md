---
phase: P6
task_id: TAG0018
type: acceptance
parent: P5-verification.md
trace_id: TAG0018-P6-20260821
status: draft
created: 2026-08-21
agent: verifier
# ── v2.0 机器汇总 ──
pass: 19
fail: 0
ui_affected: false
---

# TAG0018 P6 验收报告 — agate 原生支持 DSH 平台

> **BDD 总数声明：19 条**（P1-requirements.md `#### BDD-N:` 标题实测 19 条：BDD-1~BDD-19，与派发上下文声明一致）
>
> 验收口径：P1 是"约定"，P6 是"兑现验证"——逐条把 BDD 条件实际跑一遍（结构/文本断言用 python 解析 + grep + 命令输出实证；涉及测试的 BDD 实跑 pytest），结果翻译成人能看懂的行为描述。ui_affected: false（P2 声明）→ 无 UI 截图要求，证据形式 = 命令输出 / 文件检查 / 解析结果。
>
> 执行环境：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0018/`（分支 feat/TAG0018-dsh-platform，HEAD `40a9046`）；Linux；/tmp 只读（pytest 以 `--basetemp=/home/kity/oclab/dsh-workspace/ptmp-p6 -p no:cacheprovider` 适配）；长命令外层 timeout。

**Summary**: 19/19 PASS，0 FAIL，0 NC。全部 BDD 实测通过；19 个证据文件全部非空、全部被 PASS 行引用、md5 互不相同。

## 逐条 BDD 验收明细

### 交付物 1：assets/templates/dsh/agent.cordis.yml（orchestrator agent-preset）

- PASS BDD-1: agent.cordis.yml 是合法 YAML 行列表，13 行每行 id/name 非空 (bdd-1-agent-cordis-rows.log)

行为描述（人话）：DSH 装配器靠 preset 里的"身份行"组装 Agent，每一行都必须有 `id` 和 `name`，缺字段会导致挂载失败。用容忍 `!!js` 自定义标签的 YAML Loader 实跑解析：文件顶层是行列表，共 13 行（persona、agent-instructions、tool-bash、tool-pwsh、tool-fs、tool-fs-search、tool-jobs、skill-filesystem、tool-skill、tool-goal、delegation、tool-ask-user、tool-todo），逐行检查 id/name 均非空——装配器能正常解析这份 preset。

- PASS BDD-2: tool-fs-search 行带 config.sampleOverCapGlobResults: false（实机缺陷回归） (bdd-2-tool-fs-search-config.log)

行为描述（人话）：2026-08-21 实机发现的缺陷：该字段是 DSH schemastery 校验的必填项、无默认值，缺失会导致 preset 挂载失败、DSH fail-closed 拒绝创建会话。实跑解析确认 `id: tool-fs-search` 行带 `config.sampleOverCapGlobResults: false`，缺陷已修复并固化。

- PASS BDD-3: persona 薄身份——含 {agate_root}/orchestrator-template.md 引用，不含模板正文 verbatim (bdd-3-persona-thin.log)

行为描述（人话）：persona 只写"你是谁 + 会话开始步骤 + DSH 工具映射"薄身份，行为规范指向模板文件（模板随 ~/.agate 升级自动更新），不复制模板全文。实跑断言：persona.text 含 `{agate_root}/orchestrator-template.md` 路径引用；且不含模板首行标题「# Orchestrator（agate 编排 Agent）」（verbatim 判据），证明没有把模板正文抄进 preset。

### 交付物 2：assets/templates/dsh/preset.yml

- PASS BDD-4: preset.yml 是合法 YAML 且 name/description 均为非空字符串 (bdd-4.log)

行为描述（人话）：preset.yml 是会话选择器展示用的元数据。实跑 yaml.safe_load：`name: agate 编排者`、`description: agate 编排 Agent（P0-P8 全流程管理，派发 subagent 执行，gate 硬边界验证）。`，两者均非空——DSH GUI 会话选择器据此展示「agate 编排者」。

### 交付物 3：assets/templates/dsh/SKILL.md（agate-protocol skill）

- PASS BDD-5: SKILL.md frontmatter name=agate-protocol 且 description 非空 (bdd-5.log)

行为描述（人话）：DSH 技能目录按名字发现 skill，安装到 `~/.dsh/skills/agate-protocol/SKILL.md` 才能被按名加载。实跑解析 frontmatter：`name: agate-protocol`、description 为一段非空的中文说明（"agate 协议的 DSH 适配层——工具映射、平台注意、并行派发与独立 judge 的 DSH 原生食谱…"）。

- PASS BDD-6: SKILL.md 正文含「编排者四项职责 × DSH 工具」映射与「平台注意」节四要素 (bdd-6.log)

行为描述（人话）：任何想在 DSH 上手动跑 agate 任务的 agent，加载本 skill 即获得适配层全部要点。实跑 10 项检查全 OK：映射表（读状态→read/grep/glob、派发→subagent/subagent_fork、跑 gate→bash 按 `[exit code: N]` 判定、更新状态→write/edit）+ 平台注意四要素（sandbox 只读区、/tmp 只读、审批策略、bash 纪律）。

### 交付物 4：SETUP.md「步骤 2-DSH」

- PASS BDD-7: SETUP.md 含「### 步骤 2-DSH」标题，位于步骤 2 平台章节区内（与既有平台小节同构） (bdd-7.log)

行为描述（人话）：SETUP.md 步骤 2 原本有 Claude Code/OpenCode/Windows 三个平台小节，DSH 小节加在 Windows 小节之后、步骤 3 之前（标题行号 144，位于步骤 2 区 L72 与步骤 3 L173 之间）——用户按既有路径可找到。

- PASS BDD-8: 章节含 mkdir -p + 三条 ln -sf 命令串，源路径均指向 ~/.agate/assets/templates/dsh/ (bdd-8.log)

行为描述（人话）：用户照抄命令即可完成注册。实跑 4 项断言全 OK：`mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol`；三条独立 `ln -sf ~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml} → ~/.dsh/.agent-presets/agate/`、`SKILL.md → ~/.dsh/skills/agate-protocol/SKILL.md`。

- PASS BDD-9: 章节含 python3 ~/.agate/scripts/install-hook.py（唯一安装脚本），交付物树无 per-platform installer（agate/ grep 0 命中、find 无 install-dsh.py） (bdd-9.log)

行为描述（人话）：平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py，不发明新结构。实跑三连：① 章节含 `python3 ~/.agate/scripts/install-hook.py` 调用；② 交付物树 `agate/` 内 grep `install-dsh` 0 命中；③ 全仓 find 无 install-dsh.py 文件，scripts/ 安装脚本仅 agate-install.py / install-hook.py / install-offline.py。（注：任务工作区 agate-workspace/ 的 P0-P8 编排文档中出现的"install-dsh.py 已废弃"为约束说明文字，非 installer 引用，不计入交付物验收范围——BDD-9 的 Given 范围是 SETUP.md 章节与仓库 scripts/。）

- PASS BDD-10: 章节含「身份薄、协议厚」说明与升级跟随行为（符号链接免操作 / 复制模式重跑） (bdd-10.log)

行为描述（人话）：实跑 7 项语义断言全 OK：「身份薄、协议厚」表述、persona 只写薄身份、行为规范指向 orchestrator-template.md、模板随 ~/.agate 升级自动更新、符号链接方式升级后什么都不用做、Windows 无符号链接权限时退复制模式、升级后需重跑对应命令。

- PASS BDD-11: 章节含使用与验证指引（打开 DSH 会话→选「agate 编排者」→执行「开始」几步验证） (bdd-11.log)

行为描述（人话）：实跑 4 项断言全 OK：「打开 DSH 会话，在会话选择器选「agate 编排者」（对应 `claude --agent orchestrator`），然后执行 orchestrator-template.md 的「开始」几步验证」——用户知道装完怎么用、怎么验。

### 交付物 5：platform-notes.md DSH 条目

- PASS BDD-12: platform-notes.md 含「## DSH（deepseek-harness）」条目，与既有平台条目同级（h2） (bdd-12.log)

行为描述（人话）：实跑确认 DSH 条目是 h2（`## DSH（deepseek-harness）`），与 OpenCode / Claude Code / Claude Project / Codex / Hardening / 验证记录 / Windows 原生等既有 h2 条目同级，结构对齐——读者按既有"平台条目"心智模型可找到。

- PASS BDD-13: DSH 条目含六项能力差异对照表与「已知注意」节（sandbox 只读 + 无 .claude/agents 等价物） (bdd-13.log)

行为描述（人话）：实跑 6+2 项断言全 OK：能力表覆盖 orchestrator 身份注册（.agents/orchestrator.md 软链 vs agent-preset）、派发 subagent（task vs subagent/subagent_fork）、批量并行（手工多路 vs workflow）、独立复核（手工 fresh context vs ralph）、跨轮续跑（手动重开 vs goal）、实时 gate（git hook vs session hooks）；已知注意两条：sandbox 只读区（写仓库内文件 Errno 30）、DSH 无 `.claude/agents/*.md` 等价物（不要软链 orchestrator-template.md 进 DSH 目录，用 preset）。

- PASS BDD-14: DSH 条目引用 SETUP.md「步骤 2-DSH」为接入步骤单一真相源 (bdd-14.log)

行为描述（人话）：条目开头写明"接入步骤见 `SETUP.md`「步骤 2-DSH」（接入命令单一真相源，本条目只做能力差异说明）"——安装命令只维护在 SETUP.md 一处，platform-notes 只做能力差异说明，避免命令双份漂移。

### 交付物 6：tests/unit/test_dsh_preset.py

- PASS BDD-15: test_dsh_preset.py 存在且 8 用例 pytest 全绿（实测 8 passed，≥5） (bdd-15-pytest-single.log)

行为描述（人话）：实跑 `python3 -m pytest agate/tests/unit/test_dsh_preset.py`：8 个用例全部通过（≥5），覆盖 agent.cordis.yml 行结构（id/name）、tool-fs-search 必填配置、preset.yml name/description、SKILL frontmatter、SETUP.md 章节与命令在位——与 P5 单文件 8/8 结论一致。

- PASS BDD-16: 测试平台无关——静态核查四条禁止项 0 命中 + 隔离 HOME（无 ~/.dsh）环境 8 passed (bdd-16-platform-independence.log)

行为描述（人话）：模拟无 DSH 实例 / 无 ~/.dsh / 主目录隔离的 CI 类环境实跑：① grep 静态核查四条禁止项（不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖主目录路径）0 命中（`~/.dsh` 与 `ln -sf` 仅作为 SETUP.md 文本断言的字符串字面量，非真实调用）；② 空 HOME（无 ~/.dsh 目录）下 `pytest agate/tests/unit/test_dsh_preset.py` 8 passed——测试只校验仓库内文件。

- PASS BDD-17: 回归护栏有效——移除必填配置用例红（FAIL）、恢复用例绿（PASS），文件已还原且 git 无 diff (bdd-17-red-green.log)

行为描述（人话）：证明测试真实守护 2026-08-21 实机缺陷而非空断言。实跑变异验证（临时改交付物文件、跑完立即还原）：① 红态——移除 `config.sampleOverCapGlobResults` 后跑 tool-fs-search 回归用例 → `1 failed`（断言"tool-fs-search 缺 config.sampleOverCapGlobResults: false"）；② 恢复（md5 与原始一致 3aea0262…）→ 同用例 `1 passed`、全文件 `8 passed`；③ git status 确认 agent.cordis.yml 无 diff，交付物未污染。

- PASS BDD-18: 全量回归——pytest agate/tests/ 全绿 + consistency 0 ERROR + 用例数不漂移（1038 ≥ 1030） (bdd-18-regression.log)

行为描述（人话）：三条 gate 命令独立实跑（无 && 短路链）：① `pytest agate/tests/ -q --tb=no` → `1036 passed, 2 skipped`（0 failed，与 P5 1036 passed 一致）；② `check-protocol-consistency.py --strict-errors-only` → `仅有 317 个 WARNING，无 ERROR`；③ `count-tests.sh` → `总计 1038 个测试用例` ≥ 1030 基线（只增不减）——"Linux 现状是基线"回归底线不破。

### SELF-GATE 触发面（P8 核对用）

- PASS BDD-19: 含触发文件的 commit 携带 self-gate-skip 标记；test_dsh_preset.py 经正则核对不触发 self-gate (bdd-19-selfgate.log)

行为描述（人话）：实跑核对：① 含三个触发文件（SETUP.md / platform-notes.md / SKILL.md）的 P4 commit `bf69754` message 带 `self-gate-skip: P4 实现提交，完整 self-gate review（protocol-alignment-review）于 P8 统一派发`；补行 commit `153c0a2`（tests/README.md，亦命中 `agate/.+/.*\.md`）带 `self-gate-skip: 纯文档行追加，无协议机制改动`；② 用 commit-msg-self-gate.py 的 `_SELF_GATE_RE` 正则逐路径核对：SETUP.md / platform-notes.md / SKILL.md 均触发、`agate/tests/unit/test_dsh_preset.py` 不触发（.py 不在 agate/scripts/ 下）；③ 引入/修改 test_dsh_preset.py 的 commit（15a6874 / 40a9046）确实无 self-gate 标记——符合"该文件不触发"声明。

## 自查结果（产出后执行，供主 Agent gate 前复核）

- `python3 ~/.agate/scripts/check-p6-format.py --check P6-acceptance.md` → exit 0（行格式合规）
- `python3 ~/.agate/scripts/check-p6-evidence.py <task_dir>` → exit 0（19 条 BDD、证据目录非空、每条 PASS 带证据引用）
- `python3 ~/.agate/scripts/check-p6-provenance.py <task_dir>` → exit 0（证据-结论对应 / dispatch-context 无预判 / BDD 总数 19 对照 / EXIT_CODE 一致性 / evidence JSON 一致性 / P5 证据复用判定均通过）
- 注：本报告由 verifier 自查产出；P6 gate 最终判定以主 Agent 亲自复跑 check-gate.py P6 为准，verifier 不自称"验收已通过"。

## 附注

- 无 PROD_TOUCHED 事件（纯本地仓库文件断言与测试执行，未触碰生产环境）→ `[PROD_NOT_TOUCHED]`
- 无不可逆操作待确认（BDD-17 变异测试已备份并还原交付物文件，git 工作区干净）→ `[NO_NEED_CONFIRM]`
- 测试环境隔离：pytest 仅使用 worktree 内仓库文件与可写 basetemp（/home/kity/oclab/dsh-workspace/ptmp-p6），未触碰生产环境。
