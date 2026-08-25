---
task_id: TAG0024
mechanism_issues:
  - "P4 gate 无独立重跑 implementer 自报测试结果（自报 0 failed vs 实测 3 failed 的偏差本次由 SELF-GATE 审查捕获；P5 verifier + P6.5 judge 为既有兜底且本次生效）"
  - "模板示例无可运行性校验机制（dispatch-context.md 的 FILE 语法示例与工具 env var 契约不符，SELF-GATE 审查捕获）"
execution_issues:
  - "P4 报告对 CODE-MAP.md 的断言未实证（称'本仓库未采用 CODE-MAP'，实际存在）；P7 交叉核对捕获并纠正"
feedback_ready: true
---

# TAG0024 复盘 — 工具链批：agate-md-field-set + 前置修复

> 模板：`agate/assets/templates/retrospective-template.md`。撰写日期 2026-08-25（合并后主 checkout，
> 按 HANDOFF-TAG0024 §8 约定）。PR #205（merge ea0dca9），v0.62.0 → v0.63.0。

## 一、事实基线

- **流程**：P0→P8→READY 全阶段（standard 档，无裁剪），2026-08-24 ～ 2026-08-25
- **规模**：v0.62.0..v0.63.0 区间 first-parent 18 commits；PR #205 共 118 文件 +12262/-38（含任务卡文档）
- **交付**：
  - RM-AG0048 一期：`agate-md-field-set.py`（16K）+ `agate-md-field-set-gate-commands.py`（5.7K），importlib 动态复用同源校验逻辑
  - DEBT0019/20 closed：`check-gate.py._check_roadmap_done()` 列数精确匹配（`!= 9`）+ `git rev-parse --show-toplevel` 仓库根锚定
  - RM-AG0049/50 done：phases.yaml P4 outputs 补 P4-review.md 声明、P6.5 统一为"强门槛子阶段"口径
  - BDD-30（SCOPE+，用户确认）：`check-pruning.py` 测试隔离修复（两轮）
  - ADR-011（用户确认新增）：引导型 CLI 工具权限原则入 `agate/adr.md`
- **质量事件**：
  - P1/P2 各 1 轮 needs-revision 打回（retries 已记录：failure_mode=quality / adjustment=add_navigation）
  - P4 SELF-GATE 对齐审查：3 项发现（A1/A2 MISALIGNED、A4 NEEDS_HUMAN_REVIEW），全部修复 + HUMAN_CONFIRMED
  - P6.5 judge：1 轮 passed（账本 3 条 judge_verdict 均 passed，含 P7 修正后复验）
  - P7：BLOCKER=0；纠正 P4 关于 CODE-MAP.md 的 1 处不准确表述
- **测试**：pytest 1285 passed / 2 skipped / 0 failed（含 `--basetemp=.pytest-tmp` 真实暂存场景复核）；BDD 29→30 全 PASS；CI 全绿（pytest×2/shellcheck×2/ruff/consistency/gate-backstop/platform-scan×2）

## 二、做得好的 + 可复用模式

**填写引导语回答**：本次产生的可沉淀物——GIT_CEILING_DIRECTORIES 环境兼容测试技术（已进测试代码）、同源复用模式（已进 design note + ADR）、影响面预排查做法（进本复盘）。

1. **retry 记录机制（RM-AG0042）首次实战生效**：P1/P2 两轮评审打回均如实记入 `.state.yaml retries` + 账本，无静默重试。→ 去向：回馈 agate——机制有效性实证样本（本复盘归档）。
2. **两轮根因修复模式（BDD-30）**：第 1 轮修根因（`run_git` 加 `cwd=task_dir`）→ 发现本仓库 `--basetemp=.pytest-tmp` 使 task_dir 物理嵌套真仓库、根因修复不够 → 第 2 轮复用本仓既有 `GIT_CEILING_DIRECTORIES` 先例（`test_bdd_23_*` 同技术）补齐，不发明新机制。→ 去向：项目资产沉淀，位置：`agate/tests/`（`test_p2_6f_*` 回归用例）。
3. **修复前影响面预排查**：P1-dispatch-context 预先全仓 grep `split("|")` 消费点，确认 DEBT0019 修复范围仅 `check-gate.py` 一处（`check-retrospective.py` 用不同解析方式），SELF-GATE 审查确认范围无需扩大。→ 去向：可复用模式（修复类任务 P1 阶段先枚举消费点再定范围）。
4. **同源铁律落地**：set 工具经 importlib 动态复用 gate 同源校验（phases.yaml task_fields + 值域 + resolve-entry 版本链），避免"set 说通过、gate 说不通过"的新漂移源。→ 去向：已沉淀 `docs/design-notes/design-md-field-set.md`；配套原则升格 ADR-011。
5. **ADR-011 决策升格**：审查建议"权限是引导不是安全边界"原则从 design note 升格进 `adr.md`（用户确认后落地），未来引导型 CLI 工具不必重新论证。→ 去向：回馈 agate，位置：`agate/adr.md` ADR-011。

## 三、发现的问题

- **问题 1**：implementer 自报"0 failed"与实测 3 failed 偏差（A4）——check-pruning.py 测试隔离缺陷在本仓库 `--basetemp` 强制配置下暴露，实现者环境未复现。
  归因层面: 机制缺口
  说明：P4 gate 信任实现者自报的测试结果，无独立重跑要求；本次偏差由 SELF-GATE 审查独立重跑捕获，P5 verifier + P6.5 judge 两级兜底亦覆盖。缺口存在但既有兜底有效（见改进措施 1）。
- **问题 2**：dispatch-context.md 模板示例语法与工具契约不符（A1/A2）——示例写 FILE 位置语法，工具实际契约是 `FILE=<路径>` env var。
  归因层面: 机制缺口
  说明：模板示例无可运行性校验机制/要求，示例写错无拦截；本次由 SELF-GATE 审查发现并修复 + 实测验证（HUMAN_CONFIRMED）。
- **问题 3**：P4 报告称"本仓库未采用骨架或 CODE-MAP"，实际 `agate-workspace/agents/CODE-MAP.md` 存在（94 行）。
  归因层面: 执行错误
  说明：对仓库结构的断言未先实证；P7 交叉核对捕获并纠正（P7-consistency.md §3 留痕）。实质结论不受影响：字段读写 CLI 在 CODE-MAP 现有粒度下本就是系统性未点名的一类，非本任务遗漏。

## 四、改进措施

1. **对问题 1（自报偏差）**：不新增 gate——本次实证既有两级兜底（SELF-GATE 审查独立重跑 + P5/P6.5 judge）已覆盖该风险，新增机制属过度设防。落点：本复盘作为实证样本归档；.state.yaml/账本已留痕全过程。若未来同类偏差绕过两级兜底，再评估在 verifier.md 加"必须独立重跑实现者自报命令"硬条文。
2. **对问题 2（模板示例漂移）**：本次已修复 `dispatch-context.md:31-32`（env var 语法）并实测 `FILE=<路径> ... --list` 执行成功（HUMAN_CONFIRMED）。纪律沉淀：模板示例改动视同代码改动，须实际跑一次再提交——落点：本复盘记录该纪律；不加新 gate（避免 gate 膨胀）。
3. **对问题 3（未实证断言）**：无需行动——P7 交叉核对机制实际捕获，机制有效；落点：P7-consistency.md §3 纠正记录留痕。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是（P1/P2 评审打回）| ✅ | | |
| PAUSED | — | — | | |
| PROD_TOUCHED | — | — | | |
| SCOPE+ | 是（BDD-30 check-pruning 测试隔离，P1 未覆盖）| ✅ | | |
| SCOPE_RESOLVED | 是（BDD-30 两轮修复完成）| ✅ | | |
| DESIGN_GAP | — | — | | |
| DESIGN_GAP_REVIEWED | — | — | | |
| NEED_CONFIRM | — | — | （偏差经 SELF-GATE 审查通道发现，非 verifier NEED_CONFIRM 通道）| |
| CAPABILITY_GAP | — | — | | |
| gate 验证（每阶段） | 是 | ✅（账本 P1-P7 gate_run 全记录）| | |
| 阶段产出文件（每阶段） | 是 | ✅（P1-P8 产出齐，P8 gate 校验）| | |
| .state.yaml phase 同步 | 是 | ✅（READY）| | |
| 裁剪条件 + override | —（未裁剪）| — | | |
| capability_requirements | —（无特殊能力需求）| — | | |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅（dispatch-context/progress 文件齐，无空返回）| | |
| phase-产出一致性 | 是 | ✅（pre-commit 无拦截记录）| | |
| P6 evidence（含截图 + 引用 + vision YAML） | 是（CLI 任务，证据=测试日志）| ✅ | | |
| P2 候选方案 + 权衡（≥2） | 是 | ✅（P2 经 needs-revision 1 轮后通过）| | |
| P8 internal_only_reason | —（未裁剪）| — | | |
| dispatch-context.md | 是 | ✅（各阶段 dispatch-context 齐）| | |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅（全程经 hook）| | |
| CI backstop | 是 | ✅（PR #205 CI 全绿）| | |
| **技术债登记** | 是 | ✅ | | DEBT0019/20 closed（本任务交付）；BDD-30 缺陷修复随任务落地（测试代码+回归用例）|

## agate 反馈

1. **实证样本（机制有效）**：retry 记录机制（RM-AG0042）首次实战——两轮评审打回均如实入 `.state.yaml retries` + 账本，"重试上限防绕过"在真实打回场景成立。
2. **实证样本（兜底有效，勿加新 gate）**：实现者自报测试结果与实测的偏差（0 failed vs 3 failed），被 SELF-GATE 审查独立重跑捕获，P5 verifier + P6.5 judge 两级兜底亦覆盖——此类风险的现有防线足够，新增机制属过度设防。
3. **原则沉淀**：ADR-011——引导型 CLI 工具的权限语义 = 引导与早纠错，不是安全边界；真正的安全边界在 gate 链（agent 字段 + 账本 + 独立 judge）。已入 `adr.md`，供未来引导型工具设计直接引用。
