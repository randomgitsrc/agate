---
phase: P4
task_id: TAG0029
parent: P4-implementation.md
trace_id: TAG0029-P4-20260904
agent: review
status: approved
---

# P4-review — TAG0029 review 评审意见

> [PROD_NOT_TOUCHED] 本评审只读核查，未改动任何实现代码与 git 状态。
> 评审对象：`P4-implementation.md`（M1–M5）+ 改造后 3 脚本 + `agate/phase-cards/P2-design.md` 新增节。
> 验收锚：`P1-requirements.md` 9 条 BDD；方案锚：任务 `P2-design.md` §2.5 / §3.1–§3.4；派发指引：`P4-dispatch-context-review.md`。
> 结论：**approved** —— CRITICAL 0 个；INFORMATIONAL 3 个（均不阻断）；存量冲突 3 处逐条定论（1 更新 + 2 保留）。

## 1. Pass 1 正确性核对（CRITICAL：0 个）

| # | 核对项 | 结论 |
|---|--------|------|
| C1 | M1 值清洗状态机边界（`agate-read-gate-commands.py` L49–92，调用点 L103 / L112） | 通过。外层先剥一层（L62）+ 截断后复剥（L85）；`\` 转义跳过（L68–72）、引号开闭跟踪（L73–80）、仅引号外且前导空白的 ` #` 截断（L81）——`\#` 保留、引号内保留，与 P2 §3.1 一致。BDD-1（`test_tag0029_bdd_1_inline_comment_stripped_to_pure_command`，`test_tag0029_gate_parser_fix_a.py` L59–77）断言 `cmd == "echo hi"` 可成立；BDD-2（同文件 L83–97）断言 `returncode != 0` + stderr 含解析错误 + 无 `"cmd"` 输出——L86–91 奇计数 fail-closed（stderr 含 key 名 + `sys.exit(2)`，exit 前无 print，无残渣）满足。L103 命令值 / L112 formatter 值两处共用，符合 M1 要求。 |
| C2 | M2 精确键收集（同文件 L106–113） | 通过。`key == "P3"` 精确键（L106），`suffix = ""`（L107），`P3_formatter` 伴随查找不变（L108–112），与 P2 §3.2 字面一致。`grep startswith("P3") agate/scripts/` 零命中，无残留宽匹配。BDD-4（`test_tag0029_bdd_4_p3_aux_keys_not_collected`）/ BDD-5（`test_tag0029_bdd_5_bare_p3_collected_meta_exempt`）锚定。 |
| C3 | M3 judge 分区无交（`check-tdd-red.py` L110–121） | 通过。新分支位于 `exit == 0` 判定（L106–108）之后、既有 A 类分支（L123，要求 `exit_code == 1`）之前；与 `exit >= 120` 分支（L165）输入域分别为 exit 2 / exit 1 / exit ≥ 120，三域不交，无优先级冲突。主判 `exit 2` + 运行器统计全零（locale 无关）+ 辅证正则恰为 B1 关闭版 5 项（`syntax error\|unexpected\|matching\|寻找匹配\|未预期`），推测项（`unmatched` / `找不到匹配` / `unterminated`）未引入，与 P2 §3.3 复审关闭一致。BDD-3 双 locale 用例（`test_tag0029_bdd_3_exit2_chinese_syntax_is_a_class` / `..._english_...`）锚定。 |
| C4 | M4 豁免仅 R2（`check-platform-assumptions.py` L46–65 + L101 / L108–109） | 通过。`_FIXTURE_EXEMPT_DIRS = {"agate/tests/fixtures/"}`（L46）+ 连续路径段包含判定（L62–64，posix 归一化 + 反斜杠兼容），禁用字符串 startswith，符合 P2 §3.4 与 R3 缓解。`_scan_file` 内 `if exempt == "r2" and fixture_exempt: continue`（L108）仅跳过 R2 规则，R1 / R3–R5 照常命中。R2 正则本体（L39）不动。BDD-7（`test_tag0029_bdd_7_fixture_data_exempt_zero_hits`）/ BDD-8（`test_tag0029_bdd_8_bare_call_outside_fixture_still_hit`）锚定。 |
| C5 | M5 卡片只加不改（`agate/phase-cards/P2-design.md` L182–194） | 通过。新增「`P3_xxx` 禁止声明」子节（L182–189，白名单 `_formatter` / `_timeout_seconds` + `_e2e` + 退役 `_js` / `_html`，与任务 P2 §2.5 一致）+ CHECK 上线流程段（L191–194）；既有 L125–180 语义文字未动。BDD-6（`test_tag0029_bdd_6_protocol_card_bans_p3_aux_keys`）/ BDD-9（`test_tag0029_bdd_9_task_p2_declares_scanner_keys`）锚定。 |
| C6 | 公共库 / rules YAML 零触碰（S-4） | 通过。`files_modified` 四文件不含 `agate_common.py` 与 `rules/*.yaml`；`is_gate_meta_key`（L79）/ `is_legal_gate_key`（L679）/ `parse_gate_commands_block`（L784）定义 intact，与 P2 N3 / N7 一致。 |

## 2. Pass 2 代码健康（INFORMATIONAL：3 个，均不阻断）

| # | 意见 | 处置 |
|---|------|------|
| I1 | `agate-read-gate-commands.py` L106 `elif key == "P3" and not is_gate_meta_key(key)` 中后半条件恒真（`is_gate_meta_key("P3")` 恒 False），为冗余条件 | 建议顺手简化为 `elif key == "P3":`（与 P2 §3.2 字面一致）。机械简化，主 Agent 可在 P5 前定向执行，不计重试。 |
| I2 | `_clean_value` L86 奇计数校验未排除转义引号；混合引号（如双引号包裹内含 `'`）可能误判 fail-closed | 接受现状：方向为 fail-closed（stderr 明示 key 名，可诊断，非静默损坏）；gate 命令域罕见混合引号；且与 P2 §3.1 字面（计数为奇）一致。仅记录，不改。 |
| I3 | M3 分支要求 `raw_output` 非空；exit 2 + 空输出回落末尾 red-light exit 0 | 接受现状：`bash -c` 语法错误必有输出，该路径实际不可达；且符合 P2 匹配策略。仅记录，不改。 |

正向：新函数命名（`_clean_value` / `_is_fixture_exempt`）与既有 `_r2_comment_exempt` 风格一致，注释均带 P2 节号追溯；无 AGENTS.md 脚本分层违规（未碰 `git diff` / `grep -c` / `printf` / hook 模式，`GATE_FILE` env 传参延续既有惯例）。

## 3. 存量冲突定论（grep `P3_js|P3_html` 于 `agate/tests/`，6 命中分属 3 处，逐条定论）

| # | 存量测试 | 定论 |
|---|----------|------|
| S1 | `test_pyx_1_read_gate_commands_p3_html_and_project_module`（`test_check_tdd_red.py` L588–611，断言 `P3_html` 被收集） | **更新**。冲突是 P2 §2.5 已显式声明的语义变更（`P3_js` / `P3_html` 历史多栈形态退役），测试同步合法。方式：P5 前由主 Agent 定向更新该断言（期望改为 `P3_html` 不再被收集；`project_module` 断言保留）。不是实现返工，M2 维持。 |
| S2 | `test_tdd_f10_multi_stack_p3_and_p3_js`（同文件 L517–545，声明 `P3_js` 但仅断言 `returncode == 0` + `classic red-light`） | **保留，无需改动**。修后仅裸 P3（exit 1，`1 failed`）被运行，判定结果仍为 exit 0 + classic red-light，断言继续成立（与自报回归「唯一失败即 S1」一致，可作旁证）。 |
| S3 | `test_agate_common.py` L30 / L41 / L52 参数化（含 `P3_html_formatter` / `P3_html_timeout_seconds` / `P3_html` 的 `is_gate_meta_key` 期望） | **保留，无冲突**。测的是公共判据（本任务 N3 零触碰，语义不变），非解析器收集侧；`P3_html → False` 等期望仍成立。 |

## 4. 追溯与自检

- BDD 锚点：BDD-1/2 → C1；BDD-3 → C3；BDD-4/5 → C2；BDD-6/9 → C5；BDD-7/8 → C4。全覆盖。
- Implementer 自报（10 passed；回归唯一失败即 S1；consistency 0 ERROR）与本评审独立核对一致，未发现自报之外的偏差。
- 主 Agent 后续动作：P5 前定向更新 S1 断言（测试同步）；I1 可选顺手简化；P5 全量回归确认 S2 / S3 仍绿。
- 自检：`python3 agate/scripts/check-frontmatter.py agate-workspace/tasks/TAG0029-gate-parser-fix/P4-review.md` 通过（worktree 根执行）。
