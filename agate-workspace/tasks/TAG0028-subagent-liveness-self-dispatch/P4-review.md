---
phase: P4
task_id: TAG0028
trace_id: TAG0028-P4-20260903
agent: review
status: approved
---

# P4 复审（fix2 定点复核）— TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P4（代码实现复审·fix2 增量）· 角色：review（偏执 Staff Engineer）· 日期：2026-09-03
> 评审对象：P4-implementation.md「### fix2：CRITICAL-4 残留修复」（302-361 行）——两处 isinstance
> 守卫 + test_bdd_2_claude_malformed_lines_no_crash 扩展 4 类畸形输入。
> 复审方法：定点复核 fix1 复审（P4-review.md rejected）CRITICAL-4 节残留 2 条崩溃链（修法原文
> 对照），其余 6 项 CRITICAL 已在上轮确认修复、本轮不重审；独立运行时实证（cmdstream 全套件 +
> 4 类畸形输入崩溃实验）。
> 实证记录（本审独立运行，非转述 implementer 自报）：
> - `timeout 300s python3 -m pytest agate/tests/unit/test_agate_cmdstream_{ir,adapters,detect,heartbeat,dispatch}.py -q`
>   → **53 passed**
> - 4 类畸形输入崩溃实验（只读 /tmp 临时文件，用后即删）：tool_use `timestamp:1788400860000`(int) /
>   `timestamp:null` / tool_result `timestamp` 为 int / `toolUseResult:"not-a-dict"` → 全部不崩溃；
>   int/null use 配对跳过（stderr「跳过 2 条 timestamp 缺失/非法的配对」计数告警）、tool_result
>   ts int 记录保留 ts_end=None、toolUseResult 非 dict 记录保留 truncated=False、合法配对保留。
> - `verify_cmdstream_detection.py` → 9 场景全 PASS（结论「全部断言通过」）；`check-protocol-consistency.py
>   --strict-errors-only` → 0 ERROR（329 WARNING 既有基线）；ruff 两文件 → All checks passed。
> - `check-maintainability.py` → god_file_count 0 / fuzzy_boundary_count 0（无 violations，
>   RM-AG0046 known-violations.md 登记门槛不触发）。

## 复审结论

**status: approved**（CRITICAL-4 残留 2 条崩溃链已按 fix1 评审修法原文彻底修复，测试缺口补齐，
无回归；未发现其他残留问题）

fix1 复审 rejected 的唯一依据是 CRITICAL-4 残留 2 条崩溃链（非字符串 timestamp 抛 AttributeError、
非 dict toolUseResult 抛 AttributeError，异常类型不在 except 捕获面内）。fix2 修复轮已按
P4-review.md CRITICAL-4 节（76-100 行）修法原文落地两处类型守卫，并扩展
test_bdd_2_claude_malformed_lines_no_crash 覆盖 4 类畸形输入（先红后绿记录在案）。本审以
代码锚点对照 + 独立运行时实验双重确认修复彻底性，未发现其他残留问题。

## 重审目标逐条核对（fix2 dispatch-context）

### 1. 残留链 1（非字符串 timestamp）— 已修复

- 代码锚点：`_iso8601_to_epoch_ms` 入口 `if not isinstance(ts, str): raise TypeError(...)`
  （agate-cmdstream-adapters.py:82-83，含类型名入错误信息）；docstring 明确「非字符串输入
  （int/None 等畸形外部数据）抛 TypeError——落入调用方既有 except (ValueError, TypeError)
  分支，不让 AttributeError 传播崩溃 read_commands」（adapters.py:76-78）。
- 调用方捕获面核验：
  - `_build_record` ts_start（adapters.py:217-220）：`try: ts_start = _iso8601_to_epoch_ms(
    u.get("timestamp", ""))` / `except (ValueError, TypeError): return None`——TypeError 落入
    except → 返回 None → read_commands 配对循环 `dropped += 1` + stderr 告警（adapters.py:178-185），
    不崩溃、不产出坏记录。
  - `_build_record` ts_end（adapters.py:240-243）：`except (ValueError, TypeError): ts_end = None`
    ——TypeError 落入 → 记录保留、结束时间未知（不崩溃）。
- 运行时实证：tool_use `timestamp` int/null → 配对跳过（dropped 计数告警）；tool_result
  `timestamp` int → 记录保留 ts_end=None。修复前复现为 AttributeError: 'int'/'NoneType'
  object has no attribute 'endswith'（fix1 复审实验 + implementer fix2 先红记录，P4-progress.md）。

### 2. 残留链 2（非 dict toolUseResult）— 已修复

- 代码锚点：`_build_record`（agate-cmdstream-adapters.py:271-274）——
  `tr = r.get("toolUseResult")` 先取引用，`truncated = bool(r.get("truncated", False)) or
  (isinstance(tr, dict) and bool(tr.get("isImage", False)))`——isinstance 守卫短路，非 dict
  不触发 `.get`，与 fix1 评审修法原文逐字一致（P4-review.md 96-97 行）。
- 运行时实证：toolUseResult 为字符串（非空非 dict）→ 记录保留、truncated=False、不崩溃。
  修复前复现为 AttributeError: 'str' object has no attribute 'get'。

### 3. 测试缺口补齐 — 已补齐

- 锚点：test_bdd_2_claude_malformed_lines_no_crash（test_agate_cmdstream_adapters.py:451-520）
  扩展覆盖 4 类畸形输入，断言逐类核验：
  - tool_use `timestamp` int（471-475 行，toolu_intts_1）→ 断言 `int_ts_cmd` 不在记录
    （510 行）；
  - tool_use `timestamp` null（476-480 行，toolu_nullts_1）→ 断言 `null_ts_cmd` 不在记录
    （511 行）；
  - tool_result `timestamp` int（481-486 行，toolu_intend_1）→ 断言记录保留且 ts_end is None
    （513-515 行）；
  - toolUseResult 非 dict 字符串（487-493 行，toolu_strtr_1）→ 断言记录保留且 truncated is
    False（517-519 行）。
- 合法配对保留断言（506 行 `python3 -m pytest -q tests/unit` 在记录中）+ 既有畸形覆盖
  （非 JSON 行 460 行 / 非 dict 行 462 行 / timestamp 缺失 464-465 行 / timestamp 非法字符串
  467-470 行）不削弱。
- 先红后绿证据：P4-progress.md 155-156 行（「测试已扩展…跑单个用例确认红」「两处修复落地…
  重跑扩展用例确认绿」）+ P4-implementation.md fix2 节 322-323 / 334-335 行（修复前红：
  AttributeError 复现，修复后绿）。用例数不变（扩展既有函数，未新增函数），cmdstream 套件
  保持 53 passed。

### 4. 无回归 — 确认

- 本审独立复核（非转述）：cmdstream 全套件 53 passed（0.87s）；verify 9 场景全 PASS；
  consistency --strict-errors-only 0 ERROR；ruff 两文件 All checks passed。
- 主 Agent 复核记录（P4-progress.md 162 行）：全量 unit 1292 passed / 2 skipped 无回归
  （基线 1292/2 保持）。
- 阈值数值锚未动（300/900/60/300/10/5 + expected×2 下限 30s + REPEAT_UNIQUE_MIN=3）：
  fix2 只改 adapters.py 两处守卫 + 扩展一个测试函数，未触 detect.py / maintainability.yaml /
  verify 脚本（P4-implementation.md 302-308 行「本轮只修这两处 + 补回归测试，不动已通过评审
  的 6 项修复、不动阈值数值锚、不动 verify 脚本、不改 P1 基线」+ git 面本审实读确认）。

## Pass 2 — INFORMATIONAL（非阻塞，记录保持）

fix2 为定点增量复审，仅复核 CRITICAL-4 残留修复。fix1 复审 Pass 2 记录的 4 项非阻塞
INFORMATIONAL（DSH 侧畸形行不计数 / node zstd 探测无缓存 / _looks_like_polling "sleep"
关键词过宽 / cleanup_heartbeats 吞 OSError 等）本轮未处理也不在本轮范围，维持「非阻塞、
记录保持」结论不变；不构成本轮放行障碍。

## 特有约束核对（fix2 增量面）

- 「只审不写」遵守：本审未修改任何代码/测试文件；所有复核均为读 + 只读运行时实验（pytest、
  /tmp 崩溃复现文件用后即删），修复仅以「已修复」结论记录于本文件。
- 评审正文遵守 provenance 审计约束：全文无行首 `- PASS` / `- FAIL` 预判格式。
- RM-AG0046 评审 checklist：check-maintainability.py 检出 violations 为空（god_file_count 0 /
  fuzzy_boundary_count 0），known-violations.md 登记门槛不触发，无需读登记理由。

## 复审门槛对照

- 定点复审 CRITICAL-4 三项（残留链 1 守卫 / 残留链 2 守卫 / 4 类畸形输入测试缺口）逐条确认
  修复：代码锚点（adapters.py:82-83 / 271-274 + 调用方 except 捕获面）+ 独立运行时实验双
  重确认，先红后绿记录在案。
- 无回归：cmdstream 53 passed / verify 9 PASS / consistency 0 ERROR / ruff 全过 / 全量 unit
  1292 passed（基线保持）。
- 未发现其他残留问题。
- 结论：**approved**——CRITICAL-4 残留修复彻底，测试缺口补齐，满足「全部通过」门槛。

## 环境隔离声明

[PROD_NOT_TOUCHED] 本复审仅读取 worktree 代码/文档/测试 + 运行只读实验（pytest 套件与
/tmp 临时崩溃复现文件，用后即删）；未修改任何代码文件，未触碰生产环境、未读取其他用户
DSH 会话。
