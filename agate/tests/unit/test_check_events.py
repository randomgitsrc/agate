# tests/unit/test_check_events.py — 事件账本审计（check-events.py）
# （TAG0020 新增：BDD-7/8；映射见 P3-test-cases.md §2）
# 被测：agate/scripts/check-events.py [TASK_DIR]（exit 0 = 通过 / exit 1 = 审计不通过）。
# 审计链（P2-design §3.4）：缺失/空账本合法 → 逐行 JSON 可解析 → 首行 prev_hash==GENESIS_HASH
#   → 逐行 prev_hash==sha256(上一行原始行) 链完整 → ts 单调不减 → 仅行尾追加 → judge_verdict
#   事件计数 ≤ 2（BDD-8 轮次预算机械兜底）；未知 event 类型不拦截。
# 哈希链约定（与 test_check_judge_verdict._write_ledger 同源，P2 §3.2）：
#   prev_hash = sha256(上一行 JSON 文本 UTF-8，不含行尾换行符)；GENESIS_HASH = sha256(b"")。
# TDD 红灯语义：脚本未实现 → subprocess 运行触发 "can't open file"（返回码 2），
#   全部 exit 0/1 断言失败 = 真实 B 类红灯。
# 平台无关：tmp_path/task_dir fixture；平台临时目录字面量与软链接语义零假设，解释器走 python_exe fixture。

import hashlib
import json

import pytest


def _run_events(agate_scripts, python_exe, run_cli, td):
    """check-events.py [TASK_DIR] 等价（合并流 result.output 断言）。"""
    return run_cli(python_exe, str(agate_scripts / "check-events.py"), str(td))


def _genesis():
    return hashlib.sha256(b"").hexdigest()


def _line(ts, event, prev_hash, **extra):
    return json.dumps({"ts": ts, "event": event, **extra, "prev_hash": prev_hash}, sort_keys=True)


def _write_ledger(td, events):
    """构造 gate-events.jsonl：逐行哈希链，首行 prev_hash = GENESIS_HASH。
    events: list[dict]，每元素须含 ts/event；raw line = JSON 文本（不含行尾换行符）。"""
    prev_hash = _genesis()
    lines = []
    for ev in events:
        line = _line(ev["ts"], ev["event"], prev_hash,
                     **{k: v for k, v in ev.items() if k not in ("ts", "event")})
        lines.append(line)
        prev_hash = hashlib.sha256(line.encode("utf-8")).hexdigest()
    (td / "gate-events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_line(td, ev):
    """按文件尾行现状真实追加一行（ev 已含 ts/event 与其余字段），自动补 prev_hash。"""
    path = td / "gate-events.jsonl"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    prev_hash = _genesis() if not lines else hashlib.sha256(
        lines[-1].encode("utf-8")
    ).hexdigest()
    row = dict(ev)
    row["prev_hash"] = prev_hash
    new_line = json.dumps(row, sort_keys=True)
    path.write_text(text.rstrip("\n") + "\n" + new_line + "\n", encoding="utf-8")


@pytest.mark.windows_smoke
def test_bdd_7_missing_ledger_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：账本缺失 → 合法态 exit 0（历史任务/首次运行不误报）。"""
    td = task_dir()

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_7_empty_ledger_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：空文件账本 → 合法态 exit 0。"""
    td = task_dir()
    (td / "gate-events.jsonl").write_text("", encoding="utf-8")

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_7_valid_chain_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7 正向：三事件合法链 + ts 单调不减 → exit 0。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run",
             "phase": "P6", "cmd": "check-gate.py P6", "exit": 2, "runner": "pre-commit"},
            {"ts": "2026-08-22T10:00:02.000001Z", "event": "state_transition",
             "phase": "P6.5", "from": "P6", "to": "P7"},
            {"ts": "2026-08-22T10:00:03.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "needs-revision", "criteria_total": 1,
             "criteria_passed": 0, "partial": True, "reason": "budget_exhausted"},
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_7_append_after_tail_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：真实行尾追加（新行 prev_hash 链自文件尾行）→ exit 0。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run", "phase": "P6",
             "cmd": "check-gate.py P6", "exit": 2, "runner": "pre-commit"},
        ],
    )
    _append_line(td, {"ts": "2026-08-22T10:00:02.000001Z", "event": "state_transition",
                      "phase": "P6.5", "from": "P6", "to": "P7"})

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_7_tampered_middle_line_chain_break_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：改写历史中间行 → 后续行 prev_hash 断裂 → exit 1（防改写检测）。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run", "phase": "P6",
             "cmd": "check-gate.py P6", "exit": 2, "runner": "pre-commit"},
            {"ts": "2026-08-22T10:00:02.000001Z", "event": "state_transition",
             "phase": "P6.5", "from": "P6", "to": "P7"},
            {"ts": "2026-08-22T10:00:03.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "needs-revision", "criteria_total": 1,
             "criteria_passed": 0, "partial": True, "reason": "budget_exhausted"},
        ],
    )
    path = td / "gate-events.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    # 改写第二行内容（exit 2 → 99），保持其余行不动
    tampered = json.loads(lines[1])
    tampered["exit"] = 99
    lines[1] = json.dumps(tampered, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_bdd_7_ts_out_of_order_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：ts 单调不减违反（第二行 ts < 首行）→ exit 1。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:05.000000Z", "event": "gate_run", "phase": "P6",
             "cmd": "check-gate.py P6", "exit": 2, "runner": "pre-commit"},
            {"ts": "2026-08-22T10:00:01.000000Z", "event": "state_transition",
             "phase": "P6.5", "from": "P6", "to": "P7"},
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_bdd_7_bad_json_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：某行非 JSON → exit 1（坏行检测）。"""
    td = task_dir()
    (td / "gate-events.jsonl").write_text(
        '{"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run", "prev_hash": "'
        + _genesis()
        + '"}\nnot-json-line\n',
        encoding="utf-8",
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_bdd_7_first_line_prev_hash_not_genesis_exit_1(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：首行 prev_hash != GENESIS_HASH → exit 1。"""
    td = task_dir()
    path = td / "gate-events.jsonl"
    path.write_text(
        '{"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run", "prev_hash": "'
        + "0" * 64
        + '"}\n',
        encoding="utf-8",
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_bdd_7_genesis_hash_constant_equals_sha256_empty(
    python_exe, run_cli, agate_scripts
):
    """BDD-7：agate_common.GENESIS_HASH 常量 == sha256(b"") 的 hex（模块级常量同源定义）。"""
    code = "from agate_common import GENESIS_HASH; print(GENESIS_HASH)"
    result = run_cli(python_exe, "-c", code, env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == hashlib.sha256(b"").hexdigest()


def test_bdd_7_unknown_event_type_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-7：未知 event 类型（向后兼容）不拦截 → exit 0。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:01.000001Z", "event": "gate_run", "phase": "P6",
             "cmd": "check-gate.py P6", "exit": 2, "runner": "pre-commit"},
            {"ts": "2026-08-22T10:00:02.000001Z", "event": "future_event_type",
             "phase": "P9", "note": "unknown but valid"},
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_8_judge_verdict_count_three_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-8：judge_verdict 事件 3 条 > 2 → exit 1（轮次预算机械兜底）。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": f"2026-08-22T10:00:0{i}.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "needs-revision", "criteria_total": 10,
             "criteria_passed": 9, "partial": True, "reason": "budget_exhausted"}
            for i in range(1, 4)
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1


def test_bdd_8_judge_verdict_count_two_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """BDD-8 边界：judge_verdict 事件恰 2 条（≤2 合规）→ exit 0。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": f"2026-08-22T10:00:0{i}.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "needs-revision", "criteria_total": 10,
             "criteria_passed": 9, "partial": True, "reason": "budget_exhausted"}
            for i in range(1, 3)
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_8_judge_verdict_same_hash_dedupe_exit_0(task_dir, agate_scripts, python_exe, run_cli):
    """CRITICAL-1 回归：3 条 judge_verdict 事件仅 2 个不同 verdict_hash（同一 verdict 被
    多处 gate 执行重跑）→ 去重后轮次=2 → exit 0（P6.5→P7 正常流程不再自锁）。"""
    td = task_dir()
    same_hash = "a" * 64
    _write_ledger(
        td,
        [
            {"ts": "2026-08-22T10:00:01.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "passed", "criteria_total": 10,
             "criteria_passed": 10, "partial": False, "verdict_hash": same_hash},
            {"ts": "2026-08-22T10:00:02.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "passed", "criteria_total": 10,
             "criteria_passed": 10, "partial": False, "verdict_hash": same_hash},
            {"ts": "2026-08-22T10:00:03.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "passed", "criteria_total": 10,
             "criteria_passed": 10, "partial": False, "verdict_hash": "b" * 64},
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0


def test_bdd_8_judge_verdict_three_distinct_hashes_exit_1(task_dir, agate_scripts, python_exe, run_cli):
    """CRITICAL-1 边界：3 条 judge_verdict 事件 3 个不同 verdict_hash（3 次真实复核）→ exit 1。"""
    td = task_dir()
    _write_ledger(
        td,
        [
            {"ts": f"2026-08-22T10:00:0{i}.000001Z", "event": "judge_verdict",
             "phase": "P6.5", "verdict": "needs-revision", "criteria_total": 10,
             "criteria_passed": 9, "partial": True, "verdict_hash": chr(96 + i) * 64}
            for i in range(1, 4)
        ],
    )

    result = _run_events(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1
