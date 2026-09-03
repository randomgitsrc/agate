# agate/tests/unit/test_tag0027_b1_judge_exit2_review.py — TAG0027 B1 批：exit2-resolution 纳入
# P6.5 judge 复核（BDD-12，exit2fix Fix C 语义）
#
# 被测契约（P2-design §3.3 定案 D3-A + §3.3 Fix C（CRITICAL-2 修正））：
#   exit2-resolution 只在**真暂停**分支（gate exit ∉ gate_pass_exit 且 ≠ 1）落盘（任务目录，
#   frontmatter + 正文留痕，不塞 .state.yaml、不加 events 类型）；复核挂载 =
#   check-judge-verdict.py P6.5 校验新增一项（Fix C：**只校验已存在的 resolution 文件**）：
#     任务目录存在 {phase}-exit2-resolution.md（= 经真暂停分支落过盘）→ 校验 frontmatter/必填节
#     完整（触发时间/客观证据/解决人/结论）；格式非法或不完整 → judge verdict 不通过
#     文件不存在（任务从未真暂停；账本 P0-P3/P5/P8 的 exit:2 全是正常通过码）→ 不要求文件，
#     judge 复核通过（不误拦健康任务——CRITICAL-2）
#   P6 自身 exit 2 条件式推进不落盘（BDD-9），其 gate_run 不带 resolution 要求
#
# TDD 红灯语义：现实现 _check_exit2_resolution 按"凡账本 exit:2 事件强制要求 resolution 文件"
#   → 健康任务反向用例（账本含正常 exit:2 事件 + 无 resolution 文件）当前 exit 1 → 断言 exit 0
#   失败 = B 类真红灯（Fix C 未实现）；已存在 resolution 文件校验场景现状即绿 = 回归守卫。
# 平台无关：task_dir fixture + run_cli(python_exe,...)；显式 utf-8。

import hashlib
import json


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


def test_bdd_12_healthy_ledger_no_resolution_file_passes(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-12 健康任务反向（CRITICAL-2 盲区补测，Fix C）：账本含 P0/P1/P2/P3/P5 正常通过
    exit:2 gate_run 事件（pre-commit 每次成功 commit 都记）+ 无任何 resolution 文件
    （任务从未真暂停）→ check-judge-verdict P6.5 复核 exit 0（不误拦）。
    现实现（凡 exit:2 强制要求文件）→ exit 1 = 红灯。"""
    td = task_dir()
    _write_verdict_pass(td)
    _write_dispatch_context(td)
    _write_ledger(
        td,
        [
            _gate_run_event("P0", 2),
            _gate_run_event("P1", 2),
            _gate_run_event("P2", 2),
            _gate_run_event("P3", 2),
            _gate_run_event("P5", 2),
        ],
    )
    result = _run_judge(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, (
        "健康任务账本（正常通过 exit:2，无 resolution 文件）→ judge 复核应 exit 0（Fix C 不误拦）；"
        f"rc={result.returncode} {result.output[:400]}"
    )


def test_bdd_12_existing_resolution_format_invalid_fails(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-12（Fix C 正向维持）：任务目录**存在** resolution 文件但格式非法（frontmatter
    type 缺失/缺必填节）→ judge 复核 exit 1（已存在的 resolution 文件须格式/完整性合法）。"""
    td = task_dir()
    _write_verdict_pass(td)
    _write_dispatch_context(td)
    # 账本无需 exit:2 事件——Fix C 由"文件存在性"驱动（存在即校验格式）
    (td / "P4-exit2-resolution.md").write_text(
        "---\nphase: P4\n---\n# P4 exit2-resolution\n（缺 type/必填字段/三节）\n",
        encoding="utf-8",
    )
    result = _run_judge(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 1, (
        "已存在的 resolution 文件格式非法 → judge 复核应 exit 1（Fix C 格式校验）；"
        f"rc={result.returncode}"
    )
    assert "exit2-resolution" in result.output or "resolution" in result.output


def test_bdd_12_judge_review_exit2_resolution_present_passes(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-12 正向：任务目录存在合规 resolution 文件（frontmatter/必填节完整）→ judge 复核
    exit 0（可核查"真暂停何时/证据/由谁解决"）。"""
    td = task_dir()
    _write_verdict_pass(td)
    _write_dispatch_context(td)
    (td / "P4-exit2-resolution.md").write_text(
        "---\nphase: P4\ntask_id: T001\ntype: exit2-resolution\nparent: .state.yaml\n"
        "created: 2026-09-02T12:00:00Z\nagent: main-agent\n---\n"
        "# P4 exit2-resolution\n\n"
        "## 触发\n- 时间: 2026-09-02T12:00:00Z\n- 触发命令: check-gate.py P4（exit 2）\n\n"
        "## 客观证据\n- check-gate 输出摘要非空\n\n"
        "## 解决\n- 解决人: main-agent\n- 结论: 继续\n- 依据: gate 输出\n",
        encoding="utf-8",
    )
    result = _run_judge(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"resolution 合规 → judge 复核应 exit 0；{result.output[:800]}"
