---
phase: P4
task_id: TAG0029
type: implementation
parent: P2-design.md
trace_id: TAG0029-P4-20260904
status: draft
created: 2026-09-04
agent: implementer
implementation_dir: agate/scripts
---

# P4 实现记录 — TAG0029 gate 命令解析器修复批

> 方案：P2-design.md §3.1–3.4（方案 A 本地化精确修复，dispatch_plan single 串行）。
> 自查≠P5 gate：以下均为 implementer 自跑，不声称"P5 已过"。
> [PROD_NOT_TOUCHED]

## 改动清单（四处，M1–M5；M6 测试已由 P3 覆盖）

| # | 文件 | 改动 | 追溯 |
|---|------|------|------|
| M1 | `agate/scripts/agate-read-gate-commands.py`（L56 前 + L57/L66） | 新增 `_clean_value(raw, key)`：外层首尾匹配引号先剥一层 → 状态机截断首个引号外未转义 ` #`（`\#` 保留、引号内保留）→ 截断后剥一层 → 残留未闭合引号则 stderr 解析错误（含 key 名）+ exit 2；L57 命令值与 L66 formatter 值两处共用 | BDD-1 `test_tag0029_bdd_1_inline_comment_stripped_to_pure_command` / BDD-2 `test_tag0029_bdd_2_unclosed_quote_fails_closed` |
| M2 | 同文件收集侧 | `key.startswith("P3")` → `key == "P3"` 精确键；`suffix = ""`；`fmt_key = "P3_formatter"` 伴随查找不变 | BDD-4 `test_tag0029_bdd_4_p3_aux_keys_not_collected` / BDD-5 `test_tag0029_bdd_5_bare_p3_collected_meta_exempt` |
| M3 | `agate/scripts/check-tdd-red.py` `judge_result`（exit 0 判定后、既有 A 类分支前） | 新分支：`exit_code == 2` + 运行器统计全零（failed/errors/syntax/import/name 全 0）为主判 + 输出含辅证文案（英文 `syntax error`/`unexpected`/`matching`；中文 `寻找匹配`/`未预期`）→ 打印 A 类说明 → return 1；推测项（`unmatched`/`找不到匹配`/`unterminated`）未引入 | BDD-3 `test_tag0029_bdd_3_exit2_chinese_syntax_is_a_class` / `test_tag0029_bdd_3_exit2_english_syntax_is_a_class` |
| M4 | `agate/scripts/check-platform-assumptions.py` | 新增 `_FIXTURE_EXEMPT_DIRS = {"agate/tests/fixtures/"}` 声明式路径前缀集合 + `_is_fixture_exempt(path)`（连续路径段包含判定，posix 归一化，禁 startswith）+ `_scan_file` 入口判定，豁免前缀内 R2 跳过（R1/R3–R5 照常）；R2 正则本体不动 | BDD-7 `test_tag0029_bdd_7_fixture_data_exempt_zero_hits` / BDD-8 `test_tag0029_bdd_8_bare_call_outside_fixture_still_hit` |
| M5 | `agate/phase-cards/P2-design.md` gate_commands 节 | 新增"P3_xxx 禁止声明"子节（§2.5 白名单清单：`_formatter`/`_timeout_seconds` 元键 + `_e2e` E2E 形态 + 历史 `_js`/`_html` 已退役 + 原因）+ 新增 CHECK/扫描面上线流程段落（DEBT0025：先全量扫描存量）；只加节，既有语义文字不动 | BDD-6 `test_tag0029_bdd_6_protocol_card_bans_p3_aux_keys` / BDD-9 `test_tag0029_bdd_9_task_p2_declares_scanner_keys` |

## 自跑结果（自查签名）

- A 批：4/4 绿（BDD-1/2 M1 后绿；BDD-3 双 locale M3 后绿）
- B 批：6/6 绿（BDD-4/5 M2 后绿；BDD-7/8 M4 后绿；BDD-6 M5 后绿；BDD-9 锁定绿）
- 全量 10 用例：`10 passed`
- 回归抽查：全量 pytest `1 failed, 1443 passed, 2 skipped`——唯一失败为存量 `test_pyx_1_read_gate_commands_p3_html_and_project_module`（断言 `P3_html` 被收集），与 P2 §2.5/M2 取舍一致（`P3_js`/`P3_html` 历史多栈形态显式退役），属设计内预期冲突，P4 不改测试，上报主 Agent 由 P5/P7 裁决；consistency `--strict-errors-only` 0 ERROR（329 WARNING）；count-tests 1446；全树扫描器 exit 0。

## files_modified

- `agate/scripts/agate-read-gate-commands.py`
- `agate/scripts/check-tdd-red.py`
- `agate/scripts/check-platform-assumptions.py`
- `agate/phase-cards/P2-design.md`

## 备注

- P2 歧义自主决策：无（dispatch-context 已强制到函数签名与正则字面级别，无需自主决策）。
- 最小实现原则：五处改动均只做 P2 §3 明确事项；公共库（`parse_gate_commands_block`/`is_gate_meta_key`）与 `rules/*.yaml` 未动。
- [修复轮 fix1] S1 落地：`test_pyx_1_read_gate_commands_p3_html_and_project_module` 同步退役语义（P3_html 不再被收集）；I1 落地：`agate-read-gate-commands.py` L106 简化为 `elif key == "P3":`。
