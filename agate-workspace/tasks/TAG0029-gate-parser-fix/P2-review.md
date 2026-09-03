---
phase: P2
task_id: TAG0029
parent: P2-design.md
trace_id: TAG0029-P2-20260904
agent: plan-eng-review
status: approved
---

# P2-review — TAG0029 plan-eng-review 评审意见

> [PROD_NOT_TOUCHED] 本评审只读核查 P2-design.md 及关联输入，未改动 P2-design.md 与任何实现代码。
> 评审对象：`agate-workspace/tasks/TAG0029-gate-parser-fix/P2-design.md`（245 行，候选 A/B/C，选定 A）。
> 验收锚：`P1-requirements.md` 9 条 BDD（BDD-1 ~ BDD-9）；范围依据：`P0-brief.md` 三缺口 + out-of-scope；派发指引：`P2-dispatch-context-plan-eng-review.md`。
> 结论：上轮 **rejected**（B1 阻塞级）；复审轮仅复核 B1 三处修复，**改判 approved**（复审 B1 关闭节见文末；D1–D10 锁定决策维持不变）。
> 复审范围：P2-design.md §2.2 judge 段（L80）、§3.3 judge 段（L139）、§8 BDD-3 行（L238）三处增量；其余节沿用上轮结论。

## 架构问题（阻塞级）

- B1 judge 新分支文案匹配表含未经实测项且缺失本机真实串（设计 §2.2 / §3.3，`check-tdd-red.py` `judge_result` L87-157）。本机实测（`zh_CN.UTF-8`，`bash -c 'echo hi" # comment'`）：`exit=2`，stderr 为 `寻找匹配的 `"' 时遇到了未预期的 EOF`；对照组 `LC_ALL=C` 同命令输出 `unexpected EOF while looking for matching`"。结论：匹配表 5 项中 `syntax error` / `unexpected` 有英文实测依据，`unterminated` / `unmatched` / `找不到匹配` 无 bash 实测出处（`找不到匹配` 与本机真实串 `寻找匹配` 相反，疑似推测项）；同时缺失真实串 `寻找匹配` / `未预期` / `matching`。后果：在中文 locale 下 unterminated quote 仍落末尾 red-light exit 0，DEBT0027 假绿灯在本机环境未被修复。要求：以中英文双 locale 实测补每项出处，补齐缺失串或改匹配策略（`exit 2` + 零运行器统计为主、文案为辅），P3 单测覆盖双 locale 典型串。派发指引发现 1 → **打回**。

## 架构问题（非阻塞）

- NB1 `P3_scanner` 常驻手动跑义务表述隐含（设计 §4 + R6 注记）。执行主体已可判定：P3 阶段由主 Agent 手动跑（`exit 0` 判定），非 `check-tdd-red` 自动收集（修后仅裸 `P3` 被收集，`P3_scanner` 永不进 TDD 判定；修前靠 `TEST_RUNNER` 覆盖绕过，`check-tdd-red.py` L164-169 最高优先级为证），非 `gate_p3` 脚本（`check-gate.py` L891-897 仅存在性检查 `return 2`）。但设计仅在 R6 注记与 §8 `跑通` 提及，未写成 P3 阶段显式 checklist 步骤。建议 P3-test-cases 登记 `P3_scanner` 手动跑步骤。不阻本次结论，派发指引发现 3 的显式化部分。
- NB2 fixture `python3` 数量口径与 P1 描述有差（P1 称 cmdstream fixture 17 处裸 `python3`；本轮 worktree 实测 `agate/tests/fixtures/` 下仅 4 处，且均为 `env python3` 形，本就经 `_r2_comment_exempt` 豁免）。不影响豁免路径覆盖结论（见 F2），P4 按 DEBT0025 全量扫描复核实际数量即可。
- NB3 `_clean_value` 边界语义已声明充分（`\#` 转义保留、引号内 ` #` 保留、防 URL / echo 误伤），P3 单测须逐条锁定转义与状态机边界；`formatter` 值清洗（L66）须与命令值（L57）各锁一条，不可只测一处。设计 M1 已声明共用，实现时落实即可。

## 测试缺口

- T1 judge 双 locale 文案单测缺失（B1 衍生，阻塞级）：P3 必须补 `exit 2` + 中文串（`寻找匹配` / `未预期`）→ `exit 1` 与英文串（`unexpected` / `matching` / `syntax error`）→ `exit 1` 双用例，否则 BDD-3 在中文环境无锁定。
- T2 `_clean_value` 转义与引号状态机边界用例（设计 §3.1 已声明算法）：`\#` 不截断、引号内 ` #` 不截断、残留单侧引号 → `exit` 非 0 + `stderr`，P3 覆盖。
- T3 P3 收集三态边界用例（BDD-4 / BDD-5）：`P3_xxx` 不收集、`_e2e` 不收集（归 BDD-4）、裸 `P3` 收集、两元键豁免，设计 §3.2 `三键共存块` 已声明，落实即可，无新增缺口。
- T4 R2 豁免边界用例（BDD-7 / BDD-8）：目录内裸 `python3 -m pytest` 豁免 `exit 0`、目录外同类文本仍命中 `exit 1`、`env` 形正交一条，设计 §3.4 已声明各锁一条，无新增缺口。
- T5 DEBT0025 存量全量扫描（H6 过程义务）：P4 落地常驻面前先全量扫描存量，有命中先登记清单再启；属过程步骤，非设计缺口。

## 锁定决策

- D1 选定方案 A（本地化精确修复，a1 + a2 + a3 + a4）锁定：唯一同时满足 9 条 BDD 全覆盖 + 公共库零触碰 + high 风险最小爆炸半径；B 的统一收益可用 P2 卡禁令替代，C 以牺牲 BDD-2 / BDD-4 为代价排除。稻草人自检成立：B 在全链口径统一维度更好、C 在工作量与历史兼容维度最好，均非纯陪衬（§2.1 / §2.6）。
- D2 公共库零触碰锁定（N3）：不动 `is_gate_meta_key` / `parse_gate_commands_block` / `is_legal_gate_key`，S-4 对账零触碰、5 消费方语义零漂移；`rules/*.yaml` 无需同步（N7），只做回归验证。与 P1-review 非阻塞建议 2 的关系：因未动公共判据，不触发 `[BASELINE_CHANGE]` 回写义务；§2.5 收紧语义变更（`P3_js` / `P3_html` 显式退役）落在解析器本地收集侧，与 P1 BDD-4 / BDD-5 一致，非基线冲突。
- D3 `dispatch_plan: {mode: single}` 锁定：四改动同源耦合（M1 / M2 同文件、M3 消费 M1 输出、M4 / M5 共享 gate 语义），拆批制造同文件跨批冲突，单发串行成立。
- D4 数据流与状态机完整：值清洗（纯命令或解析错误 fail-closed，无第三种残渣输出）→ 收集（精确键）→ judge（`exit 2` 新分支置于 `exit 0` 判定后、L110 之前，与既有 `exit 1` / `exit >= 120` 三域不交）→ R2 豁免（仅 R2 跳过，其余 R1 / R3-R5 照常）；错误边界清晰（解析错误归解析器 `exit` 非 0，命令串语法错误归 judge A 类 `exit 1`，不改 `check-gate` 返回约定含义）。
- D5 R6 bootstrap 充分：`TEST_RUNNER` 最高优先级绕过文件收集有代码依据（`check-tdd-red.py` L164-169），修后文件收集仅裸 `P3` 被收集即安全，§4 注记成立。
- D6 白名单 `_e2e` 与 BDD-5 无冲突：`_e2e` 在 P3 永不收集归 BDD-4（`P3_xxx` 不收集），BDD-5 仅锁裸 `P3` + 两元键；M2 精确键统一实现三态，无矛盾。
- D7 `minimal_validation` 通过：`bash -c` 实测 `confirmed`（本机中文串为证，恰反证 B1）+ 纯代码逻辑声明写明内部函数与数据转换（块→JSON / 输出→formatter JSON→`exit` 码 / 命中行→`exit 1`），符合派发约束。
- D8 `files_to_read` 实现就绪通过：14 条覆盖三脚本落点 + `agate_common` 四函数行号段 + S-4 口径 + `dispatch.yaml` + P2 卡落点 + 扫描器测试契约 + DEBT 条目原文 + TAG0028 范例，大文件均标行号，无上下文爆炸，implementer 可自主实现。
- D9 `gate_commands` 固化通过：逐 key 独立无 `&&` 短路、`consistency` 用 `--strict-errors-only`、`shellcheck` 与 CI 同口径 3 薄壳、`count-tests` 独立、`timeout` 三档（P5 全量 600s，其余 120s，P3 走 `AGATE_TDD_TIMEOUT`），`ui_affected: false` 故无 `P5_e2e` 正确。
- D10 BDD 覆盖锚点：BDD-1 → §3.1 注释剥离 + §8；BDD-2 → §3.1 闭合校验 fail-closed + §8；BDD-3 → §3.3 新分支 + §8（实现被 B1 阻断，设计位置正确）；BDD-4 → §3.2 精确键 + §8；BDD-5 → §3.2 三键共存 + §8；BDD-6 → §3.2 P2 卡禁令子节 + §2.5 白名单；BDD-7 → §3.4 目录豁免 + §8；BDD-8 → §3.4 目录外仍命中 + §8；BDD-9 → §4 三 `scanner` key + §8。9 条全覆盖，`candidate_count: 3` 与正文 A / B / C 一致。
- D11 三条发现逐条结论：发现 1 中文匹配表 → **打回**（B1，阻塞级，理由见上）；发现 2 豁免常量覆盖 `agate/tests/fixtures/` 前缀 → **通过**（`fixtures/cmdstream/*.jsonl` 在前缀下，目录绑定成立；数量差见 NB2 非阻塞）；发现 3 `P3_scanner` 执行主体 → **通过**（主 Agent P3 手动跑 `exit 0` 判定，P4 implementer 按 checklist 跑，P5 由 gate 执行；BDD-9 为存在性语义故非空宣称，显式化见 NB1 非阻塞）。

## 复审 B1 关闭（2026-09-04，增量复核轮）

- 范围：仅 §2.2 judge 段（L80）、§3.3 judge 段（L139）、§8 BDD-3 行（L238）三处修复；D1–D10 锁定维持，NB1/NB2/NB3 与 T1–T5 原样保留（T1 由 B1 衍生，随 B1 关闭自动解除阻塞）。
- 条件 1 通过：推测项已从匹配表删除——`unmatched` / `找不到匹配` / `unterminated` 在 §2.2 / §3.3 仅出现于"已删推测项 …"说明文字，匹配表正文仅含实测五项。
- 条件 2 通过：辅证表每项有实测出处 + 独立验证成立——本轮实测 bash 5.2.21：`LC_ALL=C` 得 `unexpected EOF while looking for matching`（覆盖 `unexpected` / `matching`，`syntax error` 为同类英文辅证项）；`zh_CN.UTF-8` 得 `寻找匹配的 '" 时遇到了未预期的 EOF`（覆盖 `寻找匹配` / `未预期`），与设计所载文案一致。
- 条件 3 通过：匹配策略为 `exit 2` + 零运行器统计主判（locale 无关）+ 文案辅证（§2.2 / §3.3 均已声明）；§8 BDD-3 行已声明双 locale 用例（中文串→exit 1 + 英文串→exit 1）。
- 改判：B1 关闭，status 由 rejected 改为 **approved**。
- [PROD_NOT_TOUCHED] 本复审只读核查 + 原位改 P2-review.md 的 status/结论节，未碰实现代码。
