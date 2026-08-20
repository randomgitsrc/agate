---
phase: P1
task_id: TAG0017-toolchain-fixes
type: review
parent: P1-requirements.md
trace_id: TAG0017-P1review-20260820-retry1
status: approved
created: 2026-08-20
agent: requirements-review
---

## 结论

**approved**——本轮为复评轮（retry round 1），仅复核上轮「待订正清单」列出的两项（3.3 节 / 3.4 节）是否已解决，未重新逐项审查已通过内容（BDD-1~12 结构、隐含需求覆盖、裁剪合理性、P1 纯净性、P0_STALE 处理，均沿用上轮核实结论，见下方复用节）。独立核实后，两处订正均已解决，未发现新引入的算术/逻辑不一致，未发现其他未授权改动。

## 本轮复核结果（核心）

### 3.3 节（`--strict`，DEBT0012）—— 已解决

1. **结论句数字与实际枚举一致**：正文表格「历史任务 `&&` 链路模式」行列出 TAG0004/TAG0009/TAG0012/TAG0014/TAG0015/TAG0016 共 6 个命中 + TAG0013 1 个主动规避 = 7；结论句现写"确认 7 个历史任务已踩过或规避过这个反模式（6 个 `&&` 链路命中 + 1 个主动规避 TAG0013）"，6+1=7，与"7"一致，算术自洽（原"8"与实际不符的错误已修正）。
2. **TAG0005/TAG0010/TAG0011 三处独立 key 声明已有显式分类判定**：正文新增表格行「独立 key 拆分声明（非同串 `&&` 链路）」，列出三个文件对应行号（TAG0005 L250 / TAG0010 L273 / TAG0011 L382），并给出明确判定——"本次不处理，但判定为同一反模式的变体、需一并纳入 P2 卡片新增指引覆盖范围"，附理由（P5-verification.md 未明确规定多 `P5_*` key 是否会被拼接执行，按保守口径纳入）。满足"不能不提"要求。
   - 独立核验：`sed` 抽取 TAG0005/P2-design.md L250、TAG0010/P2-design.md L273、TAG0011/P2-design.md L382 上下文，三处均确认为独立 `P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict ..."` key，与正文描述完全一致，无失实。

### 3.4 节（`env_constraints`，DEBT0015）—— 已解决

1. **结论句数字与实际枚举一致**：正文"命中 13 处协议语义引用"后枚举的文件清单逐项计数为 13（dispatch-protocol.md / state-machine.md / WORKFLOW.md / phase-cards/P0-orchestrator.md / phase-cards/P1-requirements.md / phase-cards/P2-design.md / phase-cards/P4-implementation.md / assets/execution-roles/analyst.md / assets/execution-roles/architect.md / assets/templates/dispatch-context.md / assets/templates/dispatch-prompt.md / assets/templates/task-files.md / agate-extract-context.py），"13"与枚举数一致（原"12"与实际 13 项不符的错误已修正）；后续"本次处理 3 处 + 本次不处理 10 处"=13，内部算术也自洽。
2. **测试基础设施类命中已补归类说明**：正文新增独立段落「测试基础设施类命中」，覆盖 `agate/rules/state-transitions.md`、`agate/tests/conftest.py`、5 个 fixture（`agate/tests/fixtures/{full-task,high-risk,paused-task,ui-affected,vision-blocked}/P0-brief.md`）、`agate/tests/unit/test_check_retrospective.py`，明确"不计入协议语义引用点，本次不处理"并给出理由（勾选项字段名 / 测试固件字面量，非协议语义消费）。满足"不能不提"要求。
   - 独立核验：`grep -n "env_constraints" agate/rules/state-transitions.md agate/tests/conftest.py agate/tests/unit/test_check_retrospective.py` 三处均命中（分别为 L15 四字段自查清单 / L107 测试固件字符串 / L278 注释提及），`grep -rl "env_constraints" agate/tests/fixtures/*/P0-brief.md` 精确命中列出的 5 个 fixture 且无遗漏，与正文描述完全一致，无失实。

**新引入问题排查**：未发现新的算术/逻辑不一致；两节修订未影响其余章节表述（本次复评未见对 3.1/3.2/3.5/3.6 或第 0/1/2/4/5 节的改动痕迹）。

## 复用节（沿用上轮核实结论，未重新逐条验证）

### BDD 评审
BDD-1~12 编号连续（`#### BDD-NN:` 格式，12 条无跳号无重复），每条单一 Given-When-Then，均可二值判定，覆盖维度标注详见上轮 P1-review.md 历史记录（数据✓/边界✓/兼容✓ 为主，前端 N/A、多端 N/A 均有显式声明理由）。本轮未发现任何改动触及 BDD 正文。

### 隐含需求覆盖
数据维度（BDD-1/3/7）、边界维度（BDD-2/4/9/10）、兼容维度（全部 12 条含兼容性判据）均覆盖；前端/多端维度经正文显式声明 N/A（domains 不含 frontend；改动对象是协议本体，无多端契约面），判断合理。

### 裁剪评审
无裁剪——`phases: [P1, P2, P3, P4, P5, P6, P7, P8]` 全阶段声明，risk_level=medium 与改动域匹配，未见裁剪不当。

### P1 纯净性
未见掺入解决方案设计，具体修复路径选择（DEBT0012 P2 卡片指引 vs 新 CLI 模式、DEBT0014 Store 占位符识别阈值）已留待 P2 architect，符合"P1 只定义问题"要求。

### P0_STALE 处理
已核对，正文第 0 节 `[P0_STALE: ...]` 标记（task 字段"4 个"vs 实际 5 条 issue）判定为轻微计数漂移、按"记录"处理，合理不构成阻塞。

## 待订正清单

无——上轮列出的 2 项均已订正解决，本轮无新增待订正项。
