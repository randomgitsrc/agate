# agate/tests/unit/test_tag0027_b1_judge_exit2_review.py — TAG0027 B1 批：exit2-resolution 纳入
# P6.5 judge 复核（BDD-12）
#
# 被测契约（P2-design §3.3 定案 D3-A）：
#   exit 2 分支落盘 {phase}-exit2-resolution.md（任务目录，frontmatter + 正文留痕，不塞
#   .state.yaml、不加 events 类型）；复核挂载 = check-judge-verdict.py P6.5 校验新增一项：
#   若 gate-events.jsonl 含 event:gate_run exit:2（phase==某历史 Pn）→ 任务目录须存在对应
#   {Pn}-exit2-resolution.md 且 frontmatter/必填节完整（触发时间/客观证据/解决人/结论）；
#   缺失或格式非法 → judge verdict 不通过（BDD-12）。P6 自身 exit 2 前进特例豁免（BDD-9）。
#
# TDD 红灯语义：P3 现状 check-judge-verdict.py 已有（既有脚本）但**无 exit2-resolution 复核项**
#   → 用例对"含 exit:2 gate_run 无 resolution 文件"的复核场景当前 exit 0（未拦截）→ 断言 exit 1
#   失败 = B 类真红灯（扩展点行为未实现）；合规场景现状即绿 = 回归守卫。
# 平台无关：task_dir fixture + run_cli(python_exe,...)；显式 utf-8。

import hashlib
import json

import pytest


def _run_judge(agate_scripts, python_exe, run_cli, td):
    return run_cli(python_exe, str(agate_scripts / "check-judge-verdict.py"), str(td))


def _write_ledger(td, events):
    """gate-events.jsonl 哈希链账本（同 test_check_judge_verdict 约定）。events: list[dict]。"""
    prev_hash = hashlib.sha256(b"").hexdigest()
    lines = []
    for ev in events:
        line = json.dumps({**ev, "prev_hash": prev_hash}, sort_keys=True)
        lines.append(line)
        prev_hash = hashlib.sha256(line.encode("utf-8")).hexdigest()
    (td / "gate-events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_verdict_pass(td, criteria_total=1):
    """P6.5-judge-verdict.md 合规（passed 1/1）。"""
    (td / "P6.5-judge-verdict.md").write_text(
        "---\nstatus: passed\ncriteria_total: 1\ncriteria_passed: 1\n"
        'verdict_evidence: ["e1.json"]\n---\n- PASS BDD-1: verified (e1.json)\n',
        encoding="utf-8",
    )
    ev = td / "P6-evidence"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "e1.json").write_text("evidence\n", encoding="utf-8")


def _write_dispatch_context(td):
    (td / "P6.5-dispatch-context-judge.md").write_text(
        "---\nphase: P6.5\ntask_id: T001\n---\n\n"
        "### 输入文件\n- P1-requirements.md\n- P6-evidence/\n\n"
        "### 上游关联\n- gate-events.jsonl\n- P6.5-judge-verdict.md\n",
        encoding="utf-8",
    )


def _gate_run_event(phase, exit_code, ts="2026-08-22T10:00:00.000001Z"):
    return {"ts": ts, "event": "gate_run", "phase": phase, "cmd": f"check-gate.py {phase}", "exit": exit_code}


def test_bdd_12_judge_review_gate_run_exit2_without_resolution_fails(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-12 反向：账本有 gate_run exit:2（phase=P5）但无 P5-exit2-resolution.md →
    check-judge-verdict P6.5 复核 exit 1（产物缺失 → judge 不通过）。P3 现状无该复核项 → 红灯。"""
    td = task_dir()
    _write_verdict_pass(td)
    _write_dispatch_context(td)
    _write_ledger(td, [_gate_run_event("P5", 2)])
    result = _run_judge(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1, (
        "gate_run exit:2 无 resolution 文件 → judge 复核应 exit 1（BDD-12 未实现 → 红灯）"
    )
    assert "exit2-resolution" in result.output or "resolution" in result.output


def test_bdd_12_judge_review_exit2_resolution_present_passes(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-12 正向：账本 gate_run exit:2（phase=P5）+ P5-exit2-resolution.md 存在且
    frontmatter/必填节完整 → judge 复核 exit 0（可核查"何时/证据/由谁解决"）。"""
    td = task_dir()
    _write_verdict_pass(td)
    _write_dispatch_context(td)
    _write_ledger(td, [_gate_run_event("P5", 2)])
    (td / "P5-exit2-resolution.md").write_text(
        "---\nphase: P5\ntask_id: T001\ntype: exit2-resolution\nparent: .state.yaml\n"
        "created: 2026-09-02T12:00:00Z\nagent: main-agent\n---\n"
        "# P5 exit2-resolution\n\n"
        "## 触发\n- 时间: 2026-09-02T12:00:00Z\n- 触发命令: check-gate.py P5（exit 2）\n\n"
        "## 客观证据\n- check-gate 输出摘要非空\n\n"
        "## 解决\n- 解决人: main-agent\n- 结论: 继续\n- 依据: gate 输出\n",
        encoding="utf-8",
    )
    result = _run_judge(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"resolution 合规 → judge 复核应 exit 0；{result.output[:800]}"
