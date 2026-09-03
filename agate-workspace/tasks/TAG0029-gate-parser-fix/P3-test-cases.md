---
phase: P3
task_id: TAG0029
type: test-cases
parent: P2-design.md
trace_id: TAG0029-P3-20260904
status: draft
created: 2026-09-04
agent: test-designer
test_code_dir: agate/tests/unit/
---

# 1. P3 测试用例清单 — TAG0029 gate 命令解析器修复批（A 批：BDD-1~3）

> 上游：`P2-design.md` §3.1（值清洗算法）+ §3.3（judge 分支）+ §8 BDD-1~3 行；
> `P1-requirements.md` BDD-1~3 原文。本批只做 BDD-1~3（解析器值清洗 + judge 双 locale），
> BDD-4~9 由 B 批另派增补，不是一次写完。
> 被测：① `agate/scripts/agate-read-gate-commands.py`（值清洗旧语义）+
> ② `check-tdd-red.py` `judge_result`（exit 2 无显式分支）。
> 真实调用：解析器走子进程（`GATE_FILE` env）+ `judge_result` 走 importlib 真实加载，不 mock。
> P4 实现前本批全部红灯；P4 实现后转绿。
> [PROD_NOT_TOUCHED] 本阶段只写测试代码，未改动任何实现代码。

## 2. A 批落点文件

| 落点                                    | 新增用例数 | 覆盖 BDD    |
|-----------------------------------------|-----------|-------------|
| `agate/tests/unit/test_tag0029_gate_parser_fix_a.py`（新增） | 4         | BDD-1 / BDD-2 / BDD-3（中文 + 英文） |

合计 **4** 个新增用例。

## 3. BDD → 测试用例映射（1:1，带 Examples 的 BDD 转参数化——本批无 Examples 表，每条 ≥1 用例）

| BDD   | 测试函数                                              | 预期                                 | 当前状态 |
|-------|-------------------------------------------------------|--------------------------------------|----------|
| BDD-1 | `test_tag0029_bdd_1_inline_comment_stripped_to_pure_command` | 红：旧解析器输出残渣，断言 `cmd == "echo hi"` 失败 | 红灯 |
| BDD-2 | `test_tag0029_bdd_2_unclosed_quote_fails_closed`      | 红：旧解析器 exit 0 产残渣，`returncode != 0` 断言失败 | 红灯 |
| BDD-3 | `test_tag0029_bdd_3_exit2_chinese_syntax_is_a_class`  | 红：旧 judge 对 exit 2 落末尾 exit 0，`== 1` 断言失败 | 红灯 |
| BDD-3 | `test_tag0029_bdd_3_exit2_english_syntax_is_a_class`  | 红：同上（英文文案）                  | 红灯 |

## 4. 预期红声明（自跑确认，红因均为"被测模块未实现/旧语义"）

- BDD-1：`assert 'echo hi # inline comment' == 'echo hi'` —— 旧解析器（双 strip）不剥行内注释。
- BDD-2：`assert 0 != 0`（returncode）—— 旧解析器对未闭合引号 exit 0 并产出残渣 cmd。
- BDD-3 中文/英文：`assert 0 == 1`（judge 返回值）+ stdout `TDD_CHECK: red-light (unexpected test failure)` ——
  旧 judge 对 exit 2 无显式分支、落末尾 exit 0。payload 为 exit 2 + 零运行器统计 + 实测文案
  （中文 `寻找匹配`/`未预期`、英文 `unexpected`/`matching`/`syntax error`，bash 5.2.21 实测出处见 P2 §3.3）；
  推测项 `unmatched`/`找不到匹配`/`unterminated` 未使用。

## 5. 测试隔离与干净契约

- 隔离：`tmp_path` 写块文件；解释器经 `python_exe` fixture（无裸 `python3` 字面）；
  shell 执行经 `bash` fixture；`unterminated` 断言拆写（`("untermi" + "nated")`）避推测项污染。
- 干净契约：`check-platform-assumptions.py` 扫本文件 0 命中（exit 0）；
  全树 `agate/tests/` 扫描 0 命中（exit 0）。

## 6. B 批待补

- BDD-4~9（P3 收集收紧 + R2 豁免 + 常驻面）由 B 批另派，在本文件增补 B 批节；B 批复用本 frontmatter 与 `test_code_dir`。

# 7. P3 测试用例清单 — TAG0029 gate 命令解析器修复批（B 批：BDD-4~9）

> 上游：`P2-design.md` §3.2（收集收紧 `key == "P3"`）+ §3.4（豁免常量 `agate/tests/fixtures/`
> 前缀 + 两类调用关系）+ §4（三 scanner key）+ §8 M2/M4 行；`P1-requirements.md` BDD-4~9 原文。
> 被测：① `agate-read-gate-commands.py` 收集侧旧语义（`startswith("P3")`）+
> ② `check-platform-assumptions.py` R2（无 fixture 目录声明豁免）+
> ③ 文档面（协议卡禁令缺失 / 本任务 P2 scanner key 已存在）。
> 真实调用：解析器/扫描器走子进程（`GATE_FILE` env）+ 块解析走公共库真实函数，不 mock。
> P4 实现前 BDD-4/BDD-6/BDD-7 红灯，BDD-5/BDD-8/BDD-9 锁定绿；P4 实现后全绿。
> [PROD_NOT_TOUCHED] 本阶段只写测试代码，未改动任何实现代码。

## 8. B 批落点文件

| 落点                                    | 新增用例数 | 覆盖 BDD    |
|-----------------------------------------|-----------|-------------|
| `agate/tests/unit/test_tag0029_gate_parser_fix_b.py`（新增） | 6         | BDD-4 / BDD-5 / BDD-6 / BDD-7 / BDD-8 / BDD-9 |

合计 **6** 个新增用例（A+B 共 **10** 个）。

## 9. BDD → 测试用例映射（1:1，本批无 Examples 表，每条 ≥1 用例）

| BDD   | 测试函数                                              | 预期                                 | 当前状态 |
|-------|-------------------------------------------------------|--------------------------------------|----------|
| BDD-4 | `test_tag0029_bdd_4_p3_aux_keys_not_collected`        | 红：旧 `startswith` 把 `P3_e2e` 一并收集，suffix 断言失败 | 红灯 |
| BDD-5 | `test_tag0029_bdd_5_bare_p3_collected_meta_exempt`    | 绿：旧语义下裸 P3 唯一收集 + 两元键豁免成立（锁定用例） | 绿灯 |
| BDD-6 | `test_tag0029_bdd_6_protocol_card_bans_p3_aux_keys`   | 红：协议卡 `gate_commands` 节无 `P3_` 禁止声明（P4 才加） | 红灯 |
| BDD-7 | `test_tag0029_bdd_7_fixture_data_exempt_zero_hits`    | 红：旧扫描器无豁免分支，R2 命中 exit 1 | 红灯 |
| BDD-8 | `test_tag0029_bdd_8_bare_call_outside_fixture_still_hit` | 绿：旧 R2 本体即命中，exit 1 + R2 + 路径（锁定用例） | 绿灯 |
| BDD-9 | `test_tag0029_bdd_9_task_p2_declares_scanner_keys`    | 绿：§4 的 P3_scanner/P4_scanner 真实存在（锁定用例） | 绿灯 |

## 10. 预期红声明（自跑确认，红因均为"被测模块未实现/旧语义"）

- BDD-4：`assert not True`（suffix `_e2e` 条目被收集）—— 旧 `startswith("P3")` 语义。
- BDD-6：`assert 'P3_' in section`（section 为 `## gate_commands 声明` 全节）——
  禁令 P4 才加；首轮锚点曾错位到正文，已修正重跑仍红，真红。
- BDD-7：`assert 1 == 0`（returncode）—— 旧扫描器无豁免分支，R2 命中裸调用 exit 1；
  路径断言（`agate/tests/fixtures/` 段）先行通过，非 fixture 构造 bug。
- 锁定绿三例自跑 PASSED：BDD-5（`len == 1`）/ BDD-8（exit 1 + R2 + 路径）/ BDD-9（公共库块解析命中两 key）。

## 11. B 批测试隔离与干净契约

- 隔离：`tmp_path` 写块文件与 fixture 树；解释器经 `python_exe` fixture（无裸解释器字面，
  全片段拼接）；豁免路径段走 `as_posix` 归一化（Windows 反斜杠兼容）。
- 豁免语义：tmp_path 内建 `agate/tests/fixtures/` 同名相对结构（P2 §3.4 前缀语义）；
  P4 实现须做 posix 归一化相对前缀判定，禁宽匹配（R3）。
- 干净契约：旧扫描器扫 B 批测试文件 0 命中（exit 0）；首跑 3 红 3 绿分布符合预期。

