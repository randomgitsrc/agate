---
phase: P6
task_id: TAG0015
type: acceptance
parent: P5-verification.md
trace_id: TAG0015-P6-20260819
status: draft
created: 2026-08-19
agent: verifier
# ── v2.0 机器汇总 ──
pass: 20
fail: 0
ui_affected: false
---

[NO_NEED_CONFIRM]
[PROD_NOT_TOUCHED]

# P6 验收报告 — TAG0015 agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）

## 0. 验收方法与边界

本任务无 UI（`ui_affected: false`）。"用户"是**未来读这些协议文件/脚本的主 Agent 或
subagent**，"行为"是**协议文本/脚本能否让读者据以正确行动**。本轮验收：

1. **不复用 P5 结论**。P5 的 932 passed 只证明"断言存在且通过"，不证明"内容语义正确、真的能
   指导行为"。本轮对 20 条 BDD 逐条打开 HEAD 下的实际协议文档/脚本文件，读实际内容，逐句
   对照 `P1-requirements.md` 的 Given/When/Then 原文判定。
2. **证据形式**：
   - 文档类 BDD（BDD-1~8/12~16，13 条）：`P6-evidence/bdd-NN-*.md`，含①Then 子句逐项核对
     （每项写"Then 要求什么 → 实际文本怎么写的（引用文件路径+行号）→ 是否满足"）②从实际文件
     摘录的原文片段。
   - 脚本行为类 BDD（BDD-9/10/11/17~20，7 条）：`P6-evidence/bdd-NN-*.md`，除文本摘录外，
     均附**本轮独立实跑命令的输出**——不是转抄 P3/P4/P5 的测试断言，而是本轮手动构造场景
     （含 DEBT/roadmap 关联信号的假 task_dir、独立编写的样例 retrospective.md，内容与
     `test_check_retrospective.py`/`test_agate_feedback.py` 的既有 fixture 不同）跑
     `check-retrospective.py`/`agate-feedback.py` 观察实际 stdout/stderr/exit code。
3. **本轮共享命令输出**落 `P6-evidence/shared-p6-command-output.log`（本轮独立实跑，非转抄
   P5）：
   - `timeout 60s python3 -m pytest agate/tests/unit/test_check_retrospective.py
     agate/tests/unit/test_agate_feedback.py agate/tests/unit/test_retrospective_protocol_docs.py -v`
     → **35 passed, EXIT_CODE: 0**
   - `timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict` →
     **0 ERROR / 305 WARNING**（`EXIT_CODE: 2`，`--strict` 模式下有 WARNING 即非零退出属既定
     语义，与 P4 自查记录一致）
   - P5 的全量 932 passed + 2 skipped + 0 failed / consistency --strict 0 ERROR 作为
     "未破坏既有行为"的旁证引用，不替代任何一条 BDD 的语义验证。
4. **环境**：工作目录 `/home/kity/oclab/agate/.worktrees/agate-TAG0015`，HEAD =
   `ae7dc57`（P5 commit）。只读验收，未修改任何协议/脚本文件，未碰主 checkout 与 `~/.agate`。

## 1. 逐条验收结果（20 条）

### 文件分组 A：`agate/assets/templates/retrospective-template.md`（模板迁移，BDD-1~8）

- PASS BDD-1: 模板正文「一、事实基线」「二、做得好的 + 可复用模式」「三、发现的问题」「四、改进措施」四节标题齐全，每节标题下均有 `>` 引导说明 + 一行填写占位提示，模板文件本身定义结构与说明，非产出文档才补充 (bdd-01-four-sections.md)
- PASS BDD-2: 新增「填写前必读：内容价值标准」小节，枚举三条"机制缺口/可复用模式/归因到可行动层面的问题"逐字存在，并附反面案例增强可执行性，放在"填写前必读"位置（非产出文档正文节）符合 BDD-2 检查对象是模板文件本身 (bdd-02-content-value-criteria.md)
- PASS BDD-3: 「发现的问题」节强制"归因层面: 机制缺口 / 执行错误"字段，显式声明"不允许留空，不允许标注'两者都是'"，两值各自定义 + 填写示例齐全 (bdd-03-attribution-layer.md)
- PASS BDD-4: 技术债登记核对清单表格"技术债登记"行的"未触发后果"列含显式强制说明"标记为'是'时，本列必须填写具体 DEBT 编号或 roadmap RM 编号，不允许留空或写'待定'"；本轮独立 grep 核实 `check-retrospective.py` 未对该列文本做任何内容语义解析，未新增阻断逻辑（exit 0 恒成立），符合"只提醒不阻断"既有边界 (bdd-04-debt-registration.md)
- PASS BDD-5: 「做得好的 + 可复用模式」节强制追问句"本次产生的临时命令/脚本/经验，哪些该沉淀为项目固定资产？沉淀到哪？"逐字精确匹配 P1 原文，两类去向（①回馈 agate ②项目资产沉淀+具体位置）标注齐全，去向①指向的「## agate 反馈」节确有效存在 (bdd-05-asset-precipitation.md)
- PASS BDD-6: frontmatter 样例块声明 `mechanism_issues`（list）/`execution_issues`（list）/`feedback_ready`（bool）三字段 + 类型注释 + 填写说明；本轮独立跑 `yaml.safe_load` 解析模板样例块本身，三字段类型确认为 `list`/`list`/`bool`，与 Then 要求完全一致 (bdd-06-frontmatter-fields.md)
- PASS BDD-7: 「## agate 反馈」标题存在，内容边界声明"只列出归因到 agate 机制/执行层面的条目，不涉及项目敏感信息"逐字齐全，且触发条件（`feedback_ready: true`）与 BDD-6 字段挂钩；本轮独立实跑 `agate-feedback.py` 验证该节确实能被脚本正确定位提取（见 BDD-17/18） (bdd-07-agate-feedback-section.md)
- PASS BDD-8: 本轮独立 grep 确认 `agate/phase-cards/P8-release.md:96` 显式引用完整新模板路径字符串 `agate/assets/templates/retrospective-template.md`（挂钩点落在"READY 收尾检查"节，符合 P2-design.md 指定落点），模板不再游离于协议本体外；`roadmap.md` 三处旧路径引用（L313/316/322）均带同步更正脚注指向新路径 (bdd-08-hooked-into-protocol.md)

### 文件分组 B：`agate/scripts/check-retrospective.py`（BDD-9~11）

- PASS BDD-9: 本轮独立构造场景（`.state.yaml` 声明 P1 retry 4 次超限 + `P1-requirements.md` 含行首 `[SCOPE+]`）实跑脚本，stderr 输出含 `tasks/{Txxx}/retrospective.md`、grep 零命中 `docs/releases`，exit 0；源码第 141 行确认提示文案已改写，不再提及 `docs/releases` (bdd-09-path-hint.md)
- PASS BDD-10: 本轮独立构造两级嵌套目录（`.state.yaml` 无异常 + `debt/tech-debt.md`/`roadmap/roadmap.md` 均登记该 task_id）实跑脚本，触发独立于异常模式的第二个消息块 `GATE RETRO: 建议复盘 — 发现机制缺口信号：`（与异常模式标题"检测到异常模式"逐字不同，可区分），exit code 仍为 0（`_scan_debt_roadmap_signal` 检测分支未并入 `warnings` 列表，独立输出） (bdd-10-mechanism-gap-signal.md)
- PASS BDD-11: `test_check_retrospective.py` 新增 3 个非空心测试函数（`test_tag0015_bdd9_stderr_hint_points_to_task_dir` / `test_tag0015_bdd10_debt_signal_...` / `test_tag0015_bdd10_roadmap_signal_...`），断言内容具体（真实构造嵌套目录 + subprocess 实跑 + stdout/stderr 文本断言），超过 Then 要求"至少 2 个"的门槛，覆盖 BDD-9（路径文案）与 BDD-10（debt 信号 + roadmap 信号两个触发面）；本轮独立实跑 pytest 确认三者均 PASSED（见 shared-p6-command-output.log 与本文件引用的 grep 结果） (bdd-11-test-coverage.md, shared-p6-command-output.log)

### 文件分组 C：`agate/state-machine.md`（BDD-12~13）

- PASS BDD-12: 第 481 行三项既有排除"不写思考过程、不写文件内容摘要、不写 subagent 返回原文"逐字保留，新增"只写决策、下一步和触发决策的简要依据（依据示例：gate 输出摘要 / BDD 编号 / 文件路径引用；不等同于展开的思考过程）"；本轮独立 grep 确认旧限制性表述"只写决策和下一步"零命中（已被替换） (bdd-12-orchestrator-log-semantics.md)
- PASS BDD-13: 「L2 会话 checkpoint（两件套）——P{n}-checkpoint.md + task-session-summary.md」小节（第 494 行起）显式回答 P2-design.md 明确的四问——①落盘时机（阶段级：每阶段 gate 通过后；任务级：P8 gate 通过后）②文件路径与命名（`P{n}-checkpoint.md`/`task-session-summary.md`，均为新开文件类型，非扩展 orchestrator-log.md）③与 BDD-12 语义关系（三者互补，L1 逐决策 vs L2 阶段级 vs L2 任务级，不互相替代/包含）④防 compact 落盘策略（写完即完成使命，不回读校验）；验收对象是协议文档定义本身，不要求实际产出 `P{n}-checkpoint.md` 运行时文件，符合 dispatch-context 约束 2 明确的验收范围收窄 (bdd-13-l2-checkpoint.md)

### 文件分组 D：`agate/loop-orchestration.md` + `agate/assets/templates/task-files.md`（BDD-14）

- PASS BDD-14: 本轮独立读取 `loop-orchestration.md:168,173` 与 `task-files.md:45` 原文，均为"防无响应"用途摘要/指针式引用，未逐字复述被 BDD-12 扩展的旧限制性表述"只写决策和下一步"（grep 零命中），语义上是新规则的超集而非替代，不矛盾；`task-files.md`「辅助文件」表新增 `P{n}-checkpoint.md`/`task-session-summary.md` 两行说明（候选方案 A1 必要联动）；`task-files.md:45` 指向的 `state-machine.md`「orchestrator-log.md 防无响应」小节标题（第 475 行）确实存在，指针有效 (bdd-14-cross-file-sync.md)

### 文件分组 E：`agate/AGENTS.md`（BDD-15）

- PASS BDD-15: 第 11 行已改写为区分"历史存量复盘仍在 docs/reviews/（迁移前旧布局，2026-08-19 前）"与"新复盘归 tasks/{Txxx}/retrospective.md（模板见 agate/assets/templates/retrospective-template.md）"，并以"路径不在 docs/ 下"收尾，切断"复盘在 docs/"这一路径断言对新复盘同样成立的过期推论，避免被 P7/CI 一致性检查判定为文档漂移 (bdd-15-agents-md.md)

### 文件分组 F：`docs/reviews/` 存量 5 份复盘文档（BDD-16）

- PASS BDD-16: 本轮逐一 `head -1` 核实 5 份存量文件（tag0008/tag0010-0011 含同名 review/tag0013/tag0014）首行均为统一标注"历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`"；`git status --short docs/reviews/` 为空确认文件原地保留、未物理迁移；`roadmap.md` 对这 5 份文件的路径引用未被本次改动涉及 (bdd-16-legacy-annotation.md)

### 文件分组 G：`agate/scripts/agate-feedback.py`（新增，BDD-17~20）

- PASS BDD-17: 本轮独立编写样例复盘文档（含独立内容的 `mechanism_issues`/`execution_issues`/`feedback_ready`/「## agate 反馈」节，非转抄 test_agate_feedback.py 的既有 fixture），实跑 `AGATE_FEEDBACK=on python3 agate-feedback.py retrospective.md`，`mechanism_issues` 列表内容被正确解析输出（语义完整保留），`task_id`/`execution_issues`/`agate_feedback_section` 均正确解析，无解析错误，exit 0 (bdd-17-extraction.md)
- PASS BDD-18: 本轮独立构造两个场景验证脱敏——场景 A（路径不在项目根内）绝对路径整体替换为 `<PATH>`；场景 B（路径在项目根内）截断为相对路径 `config/secrets.yaml`；两场景项目名（含大小写变体）均被替换为 `<PROJECT>`；最终输出 JSON 均不含原始项目名/绝对路径字符串 (bdd-18-anonymize.md)
- PASS BDD-19: 本轮独立实跑两场景（`env -u AGATE_FEEDBACK` 显式未设置 / `AGATE_FEEDBACK=off` 显式关闭），均观察到 stdout 为空（无 JSON 输出）、stderr 明确"功能未启用（设置 AGATE_FEEDBACK=on 启用）"、exit code 2（非静默失败的 0，也非无提示的 1） (bdd-19-feedback-off-by-default.md)
- PASS BDD-20: 产出物末尾固定"请提交前人工复核以下内容是否包含未预期的项目特定信息"，明确是待人工提交草稿；本轮独立 grep 脚本源码确认零命中 `git push`/`gh ` 调用，唯一 `subprocess` 调用是本地脚本间通信（`agate-md-field-get.py`，ADR-007 复用）；本轮全仓 grep（CI workflow yaml / pre-commit-gate.py / GitHub Actions 目录）确认不存在任何自动触发该脚本的 hook/CI/cron (bdd-20-manual-trigger-no-submit.md)

## 2. 交叉核对：BDD-9/BDD-10/BDD-16 共享路径字符串一致性（P1 §5 依赖关系声明）

P1 §5 要求 `tasks/{Txxx}/retrospective.md` 字符串在 check-retrospective.py stderr 文案 /
`retrospective-template.md` 文档路径引用 / `AGENTS.md:11` 新文案 / 5 份存量标注四处逐字一致。
本轮逐一核实：

- `check-retrospective.py:141`：`tasks/{Txxx}/retrospective.md`
- `retrospective-template.md:3`：`产出路径固定为 \`tasks/{Txxx}/retrospective.md\``
- `AGENTS.md:11`：`新复盘归 \`tasks/{Txxx}/retrospective.md\``
- 5 份存量标注行：`新复盘请见 \`tasks/{Txxx}/retrospective.md\``

四处字符串逐字一致（均为 `tasks/{Txxx}/retrospective.md`，无尾部斜杠差异、无大小写差异），
未发现本任务要修复的"三处不一致"问题重现。

## 3. Summary

**Summary**: 20/20 PASS, 0 FAIL
