---
phase: P4
task_id: TAG0018
type: review
parent: P4-implementation.md
trace_id: TAG0018-P4R-20260821
status: approved
agent: review
criteria:
  blockers: 0
  criticals: 0
  suggestions: 4
---

# P4 实现评审 — agate 原生支持 DSH 平台（TAG0018）

> 评审角色：review（偏执 Staff Engineer，独立评审，非实现者）。评审对象：六项交付物 + 1 顺手项。
> 对照基线：P1-requirements.md（BDD-1~19，权威）+ P2-design.md（D-1~D-5 决策，权威）+ P3-test-cases.md（8 用例断言基准）+ P4-implementation.md/P4-progress.md（实现自述）。
> 查证手段：逐文件精读 + 实跑测试 + 对照 DSH 源码（deepseek-harness checkout，路径约定/版本/standard preset）+ worktree git 状态核实。

## 总体结论

**status: approved**（0 BLOCKER / 0 CRITICAL）。六项交付物与 BDD/设计逐条核对全部满足，核心约束（不发明新结构 / 身份薄协议厚 / 测试平台无关 / tool-fs-search 必填配置）落实无误，执行决策 D-2 合理且有证据锚定。发现 4 条非阻塞建议（均为过程文档精度与可忽略级措辞），不构成打回理由。

---

## 逐文件评审

### 1. `agate/assets/templates/dsh/agent.cordis.yml` — 通过（无 BLOCKER/CRITICAL）

- **BDD-1**（行列表 + 非空 id/name）：顶层 13 行列表，每行含非空 `id`/`name`；`!!js process.platform` 自定义标签保留（测试 `_js_loader` 容忍）。已核实：DSH 装配器形状检查要求"顶层为 plugin 行列表、group 递归自己的列表"（`packages/preset/agent-presets/src/discovery.ts`），本文件结构合规。
- **BDD-2**（tool-fs-search 必填配置）：L78 `config.sampleOverCapGlobResults: false` 在位，与 DSH standard preset 同字段值一致。schemastery 必填无默认值 → 缺失即挂载失败（fail-closed），此为实机复现缺陷的回归护栏对象，保留正确。
- **BDD-3**（persona 薄身份）：正判据——L35 含 `{agate_root}/orchestrator-template.md` 引用；负判据——persona 文本不含模板 H1 标题「# Orchestrator（agate 编排 Agent）」（该标题在 `orchestrator-template.md` L12，已核实为 verbatim 判据锚点）。persona 只写你是谁 + 会话开始 5 步 + DSH 工具映射 + 平台注意，未复制模板正文。
- **group/isolate 语法对齐**（派发指引核对项 ①）：delegation 组（`cordis:group` + `group: true` + `isolate: {workflowEngine: true}` + 嵌套 7 行）与 standard preset（`apps/cli/config/agent-presets/standard/agent.cordis.yml` L174-234）逐行一致；`!!js process.platform === 'win32'` 平台分支、tool-fs-search config、tool-subagent spawn/fork + `backgroundMode: continuable`、workflow-worker-thread、tool-ralph（`subagentProvider: spawn` + `maxRounds: 64`）全部同构。相对 standard 仅裁剪 disabled 的 codex/claude-code 可选 provider——符合"最小工具面"设计，非结构性偏差。
- **工具面最小集**：persona / agent-instructions / bash+pwsh / fs+fs-search / jobs / skills / goal / delegation / ask-user / todo，无多余行；文件头注释（L13-16）声明"已实机验证（2026-08-21，DSH v0.1.0-rc.8）"，已核实 deepseek-harness `package.json` version = `0.1.0-rc.8`，版本声明与事实一致。

**建议 1**（文档精度，非交付物缺陷）：`P4-implementation.md` §1 声称"顶层行列表（15 行）"——实际为 **13 行**（`grep -c "^- id:"` = 13；含嵌套共 20 处 id）。建议改为 13 或删去具体行数，避免与文件不符。

### 2. `agate/assets/templates/dsh/preset.yml` — 通过

- **BDD-4**：合法 YAML，`name: agate 编排者` / `description`（非空，P0-P8 职责一句话）/ `order: 1`。决策 D-4 最小元数据集落实，未过度设计（name/description 是产品级要求非 schema 强制，P2-design R-6 边界正确）。
- 与 DSH 元数据文件约定一致（`METADATA_FILE = 'preset.yml'`，已核实）。

### 3. `agate/assets/templates/dsh/SKILL.md` — 通过

- **BDD-5**：frontmatter `name: agate-protocol` + 非空 description。已核实 DSH skill 发现约定：`{dshHome}/skills/<目录>/SKILL.md` 目录 bundle（`packages/skill/skill-filesystem/src/index.ts` L253/L725）——安装目标 `~/.dsh/skills/agate-protocol/SKILL.md` 的目录名 = frontmatter name，按名发现成立。
- **BDD-6**：「编排者四项职责 × DSH 工具」映射表（读状态 → read/grep/glob；派发 → subagent/subagent_fork；跑 gate → bash 按 `[exit code: N]` 判定；更新状态 → write/edit）与 persona 内联映射同口径（决策 D-5 双份同步，逐项比对无冲突）；「平台注意」节四要素齐全（sandbox 只读区 Errno 30 / /tmp 只读 --basetemp / 审批策略 / bash 纪律）。
- 食谱 4 引用的 `packages/hooks/hooks-claude-code` 路径真实存在（已核实目录清单），非虚构引用。

**建议 2**（可忽略）：食谱 4「session hooks」的实现方式措辞"强类型 agent 扩展点，见 DSH 代码"指向偏模糊——作为探索性食谱的指引性说明可接受，但若读者按此找扩展点会多花时间。可补充一个具体文件路径或示例配置，非必须。

### 4. `agate/SETUP.md`「步骤 2-DSH」章节 — 通过（位置与命令串全部实测核对）

- **BDD-7**（位置判据）：`### 步骤 2-DSH：deepseek-harness（DSH）接入` 位于 L144——在 `## 步骤 2：`（L72）与 `## 步骤 3`（L173）之间，为步骤 2 区内最后一个 h3（Windows 环境适配要点 h3 之后），与 Claude Code/OpenCode/Windows 小节同构。决策 D-1 落位精确。
- **BDD-8**（精确命令串）：L152-155 为 `mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol` + **三条独立** `ln -sf ~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml,SKILL.md}` → 目标路径，与 BDD-8 字面及 P3 用例 6 断言完全一致（无花括号简写，P2-review 建议 5 落实）。
- **BDD-9**（不发明新结构）：L158 `python3 ~/.agate/scripts/install-hook.py` 在 DSH 章节切片内（唯一安装脚本）；worktree 全仓 `grep install-dsh` 0 命中、`find` 无 install-dsh.py（实跑复证），scripts/ 仅 install-hook.py 等。无 platforms/ 目录（find 空）。
- **BDD-10**（身份薄协议厚 + 升级行为）：L161-163 含「身份薄、协议厚」表述 + 符号链接升级免操作 / 无符号链接权限退复制模式、升级后重跑 `ln` 对应 `cp`。
- **BDD-11**（使用与验证指引）：L165-166 含「打开 DSH 会话 → 会话选择器选「agate 编排者」（对应 `claude --agent orchestrator`）→ 执行 orchestrator-template.md 的「开始」几步验证」。
- **外部事实核对**（偏执项）：命令目标路径与 DSH 源码约定逐项吻合——`~/.dsh/.agent-presets/`（`USER_PRESET_DIR = '.agent-presets'`，`dshHomePath` 拼接，preset 发现 user root）、`~/.dsh/skills/`（skill-filesystem user-dsh root）、`agent.cordis.yml`/`preset.yml` 文件名（`COMPOSITION_FILE`/`METADATA_FILE`）、`~/.dsh` 为 DSH config root（`resolveDshHome`，`$DSH_HOME` 或 `~/.dsh`）。`ln -sf` 源路径 `~/.agate/assets/templates/dsh/` 与既有 Claude Code 小节 `~/.agate/orchestrator-template.md` 的 `~/.agate` 锚点一致（单软链 / 版本管理目录两种形态均解析）。

**建议 3**（可忽略）：L163 复制模式退化指引（"升级后重跑上述 `ln` 命令对应的 `cp`"）相对 Claude Code 小节（L121-126 的复制代价详细说明）偏简。DSH 章节命令块含 mkdir/ln 全串，Windows 用户可对照改写 cp，指引够用；如需对齐可补一句"复制模式代价：升级后不自动同步"。

### 5. `agate/platform-notes.md`「## DSH（deepseek-harness）」条目 — 通过

- **BDD-12**：L174 `## DSH（deepseek-harness）` h2 条目，与既有 OpenCode/Claude Code 条目同级；闭合括号写法（决策 D-3）消除子串断言歧义。
- **BDD-13**：六行能力差异表（orchestrator 身份注册 / 派发 subagent / 批量并行派发 / 独立复核 / 跨轮续跑 / 实时 gate，OpenCode/Claude Code vs DSH）+「已知注意」两条（sandbox 只读区 Errno 30；DSH 无 `.claude/agents/*.md` 等价物、不要软链 orchestrator-template.md、用 preset）。
- **BDD-14**（互链单一真相源）：L176「接入步骤见 `SETUP.md`「步骤 2-DSH」（接入命令单一真相源，本条目只做能力差异说明）」。接入命令在 SETUP.md 单处维护，无命令双份漂移。

### 6. `agate/tests/unit/test_dsh_preset.py` — 通过（实跑复证）

- **BDD-15**：**本人实跑 `python3 -m pytest agate/tests/unit/test_dsh_preset.py` = 8 passed（0.04s）**，8 用例 ≥5 下限；覆盖 agent.cordis.yml 行结构 / tool-fs-search 必填配置 / persona 薄身份 / preset.yml 元数据 / SKILL frontmatter / SETUP.md 章节与命令串 / 位置判据 / install-hook 调用。
- **BDD-16**（平台无关）：四条禁止项落实——不写 /tmp（无临时文件）、不调用 `islink`/不创建链接（`ln -sf` 仅作文本断言）、不 spawn DSH（`~/.dsh` 仅为断言字面量）、不依赖主目录（`agate_root` fixture，conftest 上溯反推 + AGATE_ROOT 覆盖，fail-closed）。无 DSH 实例的 CI 环境可跑，成立。
- **BDD-17**（回归护栏）：用例 2 用 `config.get("sampleOverCapGlobResults") is False` 精确断言，缺配置 FAIL / 在位 PASS 双态可复现；P4-implementation 记录实跑变异复证，断言代码本身支持红/绿判定，非空断言。
- 章节切片断言（`_dsh_section`）刻意设计：只切「步骤 2-DSH」→「步骤 3」，防 SETUP.md 其他章节既有 install-hook.py 引用（步骤 4 / Windows 适配）误命中——BDD-9 前半守护真实有效。
- BDD-1 断言仅覆盖顶层行（嵌套 delegation 行不在断言面）——与 P2-design §3 交付物 1「顶层行列表」定义一致；嵌套行实际均有 id/name（已核实），无漏网风险。

### 7. `agate/tests/README.md`（M-7 顺手项）— 通过

- L78 已补「DSH 平台模板结构（TAG0018）| unit/test_dsh_preset.py | 8」，count-tests.sh 用 collect-only 计数不受该表影响（P1 [SUGGEST] 2 落实）。

### 8. 过程文档（P4-implementation.md / P4-progress.md）

- 新增文件核对表 CODE-MAP EXEMPT 理由充分（templates 模块内新增子目录、tests 不枚举），无骨架机制（无 P2-skeleton.md）标注正确。
- 完成标准自检与 P2-design §11 六条对照：除 self-gate 标记（P8 commit 时落实，本阶段不 commit）外全部勾选，勾选内容与文件实况一致。

**建议 4**（文档精度）：P4-implementation.md 测试结果表「全量 unit」行混入"用例数 1030 → 1038 只增不减"——1038 是 count-tests.sh（全量收集）口径，不是该行 `pytest agate/tests/unit/` 的运行输出（unit 收集 906 passed + 2 skipped = 908）。建议标注计数来源（count-tests.sh），避免证据链口径混淆。该数字本身与 P3-test-cases.md「1030 → 1038」一致，无事实错误。

---

## 执行决策核对（派发指引特别项：D-2 优先）

**结论：决策合理，确认通过。** 理由：

1. **权威优先级正确**：派发指引文本与 P2-design D-2（approved）在「待实机验证标注」措辞上冲突，但派发指引自身声明"设计权威优先"；P2-design §2.3 D-2 是经 P2 评审批准的设计决策，implementer 按 D-2 执行是正确选择。
2. **「已实机验证」表述有客观证据锚定**：2026-08-21 实机验证记录于 P0-brief 上游关联与 P2 §6 env_constraints（preset 软链安装 → 热发现 → 选择器「agate 编排者 · 自定义」→ 新会话以 orchestrator 人格启动；tool-fs-search 缺陷复现并修复）；本次复核独立核实 DSH 版本 `0.1.0-rc.8` 与声明一致、`~/.dsh/.agent-presets/` 与 `~/.dsh/skills/` 发现路径与命令目标吻合。
3. **措辞选择合理**：实机验证已完成，保留「待实机验证」会误导读者（陈旧标记）；新兴平台风险改由「版本敏感提示 + 机制可能随版本变化 + 重跑命令块」承载，与 P0-brief known_risk 1 的缓解方向一致。
4. **透明记录**：implementer 在执行决策说明 #1 中明确记录冲突与选择（未静默处理），若主 Agent 意图保留待验证项清单可回补——处理方式符合纪律。

---

## 核心约束核对（派发指引核对项 ⑥）

| 约束 | 核实结果 |
|------|---------|
| 不发明新结构 | 无 platforms/ 目录（find 空）、无 install-dsh.py（grep 0 命中 + find 空）；安装 = SETUP.md 文档化符号链接 + 唯一 install-hook.py；`dsh/` 子目录与 `.yml` 文件名是 DSH 平台文件名契约（I-1），非发明 |
| 身份薄、协议厚 | persona 指向 orchestrator-template.md、不复制模板正文（BDD-3 双判据实测通过）；模板随 ~/.agate 升级自动更新（BDD-10 文档落实） |
| 测试平台无关 | 四条禁止项在测试实现中逐条落实，实跑通过（BDD-16） |
| tool-fs-search 必填配置 | 配置在位 + 回归用例精确断言（BDD-2/17） |

## 其余 BDD 覆盖路径核对

- BDD-6/10/11/13/14 为正文文本类判据，由 P6 实跑文本核对（P3-test-cases.md §3 已声明路径）；本次评审逐条人工核对文本在位，与 BDD 判据一致。
- BDD-18 全量回归（全量 pytest + consistency 0 ERROR + count ≥1030）属 P5 gate 职责；P4 自查记录 0 ERROR / 317 WARNING（`--strict-errors-only` exit 0，`dsh/` 新形态未引入新 ERROR），无降级迹象。
- BDD-19 self-gate 标记由 P8 在 commit message 落实（P4 不 commit），触发面清单与 P1 §7 一致。

## 建议汇总（4 条，均非阻塞）

1. `P4-implementation.md` §1「顶层行列表（15 行）」→ 实际 13 行，建议修正数字。
2. `P4-implementation.md` 测试结果表「全量 unit」行标注 1038 计数来源为 count-tests.sh，避免口径混淆。
3. SETUP.md L163 复制模式退化指引可补"复制模式代价"一句与 Claude Code 小节对齐（可忽略）。
4. SKILL.md 食谱 4 的 session hooks 实现方式可补具体文件路径（可忽略）。

## 结论

六项交付物 + 1 顺手项全部落位且与 P1 BDD-1~19、P2-design D-1~D-5 逐条吻合；实跑验证 8/8 绿；DSH 侧路径约定、版本、standard preset 语法全部独立核实一致；执行决策 D-2 合理。**0 BLOCKER / 0 CRITICAL → status: approved。**
