# P4 修复轮进度记录（retry round 1）

## 修复的 4 处

1. `agate/phase-cards/P2-design.md`「gate_commands 声明」节"正确做法"示例（L165-172）：
   `P5_consistency` 由 `"check-protocol-consistency.py --strict"` 改为 `"check-protocol-consistency.py --strict-errors-only"`，并在示例代码块下方新增一句说明：
   "`--strict-errors-only`（仅 ERROR 判失败）适合日常任务默认使用；`--strict`（WARNING-only 也判失败）保留给专门做 WARNING 债务清理的任务主动选用。"

2. `agate-workspace/tasks/TAG0017-toolchain-fixes/P2-design.md` §5 gate_commands（L164-171）：
   `P5_consistency` 由 `"python3 agate/scripts/check-protocol-consistency.py --strict"` 改为
   `"python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"`。
   紧邻上方新增一行 **YAML `#` 注释**（非 HTML 注释——首次用 `<!-- -->` 实测会被
   `check-protocol-consistency.py` CHECK 1「YAML 代码块可解析」判定为无法解析，
   WARNING 数从基线 314 增至 315；改用 `#` 注释后验证仍为 314，问题已规避）：
   `# P4 review 修正：原 --strict 在当前 WARNING 基线下阻塞本任务自身 P5，改用 --strict-errors-only`

3. `agate/scripts/agate-gate-p5-count.py` docstring 第 6 行：
   "排除 `_formatter` 键" → "排除 `_formatter` / `_timeout_seconds` 元信息键"。
   （核实 `agate_common.py:is_gate_meta_key` 已实现精确匹配两个后缀，本次仅同步文档，无行为变更）

4. `SELF-GATE.md` 第 62 行示例文案：
   `agate-alignment-2026-07-01-01.progress.md`、`-02.progress.md`（旧格式，缺 `{task_id}`）
   → `agate-alignment-2026-07-01-TAG0017-01.progress.md`、`-02.progress.md`（新格式）

## 验证结果

- `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only --root .`
  （独立一行验证，未走管道）→ `EXIT=0`，输出「仅有 314 个 WARNING，无 ERROR」，与既有基线一致，未新增/减少 WARNING。
- `python3 -m pytest agate/tests/ -q --tb=no` → `1011 passed, 2 skipped in 88.67s`，与基线一致，无回归。
- 两个 P2-design.md 中不再有把裸 `--strict`（不带 `-errors-only`）当作 gate_commands「默认推荐用法」的表述；
  其余出现的 `--strict`（如反例展示、`--strict` 反模式说明、TAG0017 自身验收标准里对 --strict 0 ERROR 的引用）均为
  说明性/非"gate_commands 默认推荐"上下文，按约束保留未改动。

## 结论

4 处修复全部完成并验证通过，无回归。
