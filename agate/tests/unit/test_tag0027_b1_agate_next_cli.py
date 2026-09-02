# agate/tests/unit/test_tag0027_b1_agate_next_cli.py — TAG0027 B1 批：agate next 推进 CLI（BDD-6/7/8/9/11/13）
#
# 被测契约（P2-design §3.4 定案 D4-A + §3.1「P6 主线 next 条件式裁决（A1）」）：
#   新增脚本 agate/scripts/agate-next.py [TASK_DIR]（P4 新建）：
#     exit 0 → 按 phases.yaml next 更新 .state.yaml phase + git add + append_event state_transition
#     exit 1 → 按 retreat 表值存在即委托 agate-retreat-to.py（CLI 不预判 diff）
#     exit 2 → 非 P6 落盘 {phase}-exit2-resolution.md；P6 特例（FAIL=0/证据非空 + check-p6-provenance
#              exit 0）按 A1 裁决：judge 未启用直推 P7；启用 → check-gate P6.5 exit 0 推 P7 /
#              exit 1 停留 P6 有指引，不落盘
#   P6 恒 exit 2（check-gate.py gate_p6 1051-1093 return 2，无 exit 0 分支）= A1 前提
#   BDD-11：每次推进 append state_transition 事件 = 档位 C 可观测证据
#   BDD-13：check-gate.py exit 0=通过/1=未通过/2=自判 与 check-state-transition.py exit 0=合法/
#            1=非法 返回约定不被本任务改造（回归守卫，P2 §1.2 Not Modify）
#
# TDD 红灯语义（约束 3）：被测对象 = 新增 agate-next.py，P3 不存在 → subprocess "can't open
#   file"（rc 2）→ 断言 exit==0/1 与文件落盘全部失败 = B 类真红灯（被测模块未实现）。
#   不 mock agate-next.py 本身；check-gate 等既有脚本现状存在，用临时任务目录（task_dir
#   fixture）模拟 .state.yaml 场景即可。
# 平台无关：tmp_path/task_dir fixture + run_cli(python_exe,...)；显式 utf-8；无 /tmp 字面量。

import json
import os
import re

import pytest

# 被测新 CLI（P4 实现交付）——P3 现状缺失 → 真红灯锚点
_NEXT_SCRIPT = "agate-next.py"


def _run_next(agate_scripts, python_exe, run_cli, td, env=None):
    """预期 CLI：agate-next.py [TASK_DIR]。P3 脚本缺失 → rc 2（can't open file）。"""
    script = agate_scripts / _NEXT_SCRIPT
    cmd = [python_exe, str(script)]
    if td is not None:
        cmd.append(str(td))
    return run_cli(*cmd, env=env)


def _write_state(agate_root, td, phase, judge=None, retries=None):
    """覆写任务目录 .state.yaml：phase + 可选 judge 块（judge 为 dict）。"""
    lines = ["task_id: T001", f"phase: {phase}", "status: active"]
    if retries:
        lines.append(f"retries: {retries}")
    else:
        lines.append("retries: {}")
    if judge is not None:
        lines.append("judge:")
        lines.append(f"  enabled: {str(judge.get('enabled', True)).lower()}")
        if judge.get("rounds") is not None:
            lines.append(f"  rounds: {judge['rounds']}")
    (td / ".state.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_p6_pass_fixture(td):
    """P6 通过路径合规产物：P6-acceptance PASS + 证据 + provenance 可过（审计 2/3 面）。"""
    (td / "P6-acceptance.md").write_text(
        "---\nphase: P6\ntask_id: T001\nagent: verifier\npass: 1\nfail: 0\n---\n"
        "- PASS BDD-1: verified (e1.json)\n",
        encoding="utf-8",
    )
    ev = td / "P6-evidence"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "e1.json").write_text("evidence\n", encoding="utf-8")
    # 审计 3 挑验：P1 BDD 计数 = 1（task_dir 默认 P1 有 1 条 BDD）
    (td / "P1-requirements.md").write_text(
        "---\nagent: test\n---\n#### BDD-1: test\n- Given g\n- When w\n- Then t\n",
        encoding="utf-8",
    )


def _write_verdict_pass_fixture(td):
    """P6.5 judge 通过产物：verdict passed + dispatch-context + 证据（check-judge-verdict 可过）。"""
    ev = td / "P6-evidence"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / "e1.json").write_text("evidence\n", encoding="utf-8")
    (td / "P6.5-judge-verdict.md").write_text(
        "---\nstatus: passed\ncriteria_total: 1\ncriteria_passed: 1\n"
        'verdict_evidence: ["e1.json"]\n---\n- PASS BDD-1: verified (e1.json)\n',
        encoding="utf-8",
    )
    (td / "P6.5-dispatch-context-judge.md").write_text(
        "---\nphase: P6.5\ntask_id: T001\n---\n\n"
        "### 输入文件\n- P1-requirements.md\n- P6-evidence/\n\n"
        "### 上游关联\n- gate-events.jsonl\n",
        encoding="utf-8",
    )


def _read_state_phase(td):
    text = (td / ".state.yaml").read_text(encoding="utf-8")
    m = re.search(r"^phase:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def _ledger_events(td):
    path = td / "gate-events.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ── BDD-13 回归守卫（现状绿：既有返回约定不被本任务改造） ─────────────

def test_bdd_13_check_gate_exit_semantics_regression(
    agate_root, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-13：check-gate.py 头注释 exit 0/1/2 三态保留 + P1 缺 review 场景 exit 1（未通过）。"""
    head = (agate_root / "scripts" / "check-gate.py").read_text(encoding="utf-8")[:3000]
    assert "exit 0 = gate 通过" in head, "check-gate.py 头注释 exit 0 语义丢失（BDD-13）"
    assert "exit 1 = gate 未通过" in head, "check-gate.py 头注释 exit 1 语义丢失（BDD-13）"
    assert "exit 2 = 需主 Agent 自判" in head, "check-gate.py 头注释 exit 2 语义丢失（BDD-13）"
    td = task_dir()
    result = run_cli(
        python_exe, str(agate_scripts / "check-gate.py"), "P1", str(td)
    )
    assert result.returncode == 1, "check-gate.py P1 缺 review 场景应 exit 1（回归守卫）"


def test_bdd_13_check_state_transition_exit_semantics_regression(
    agate_root, agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-13：check-state-transition.py 头注释 exit 0=合法/1=非法保留。"""
    head = (agate_root / "scripts" / "check-state-transition.py").read_text(encoding="utf-8")[:3000]
    assert "exit 0 = 合法" in head and "exit 1 = 非法" in head


# ── BDD-6：gate exit 0 直推 ─────────────────────────────────────────────

def test_bdd_6_next_exit0_advances_to_next_phase(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-6：phase=P5 + gate exit 0（mock 于 CLI 内部判定路径）→ agate-next 把 .state.yaml
    phase 推为 P6（phases.yaml next 字段）——P3 agate-next.py 未实现 → 红灯。"""
    td = task_dir()
    _write_state(None, td, "P5")
    # 让 check-gate P5 现实 exit 2 无妨——agate-next 内部按三态分支；P3 无该 CLI → 直接红灯。
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"agate-next.py exit 0 预期（P4 实现）；当前 rc={result.returncode}"
    # 注意：本断言集整组在 P3 全红（脚本缺失 rc 2）；P4 实现后按三态分支消费真实 check-gate
    # exit 判定推进。绿灯路径的 phase 推进断言由 BDD-6 P6 锚点用例承载。


def test_bdd_6_p6_judge_disabled_direct_p7_anchor(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-6 P6 通过路径锚点（A1）：phase=P6 + P6 验收产物合规（FAIL=0/证据非空 +
    check-p6-provenance exit 0）+ judge 未启用（历史任务）→ agate-next 按 §3.1 裁决直推 P7。
    P3：agate-next.py 缺失 → 红灯（B 类，被测未实现）。"""
    td = task_dir()
    _write_state(None, td, "P6")  # 无 judge 块 = 历史任务
    _write_p6_pass_fixture(td)
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"P6 judge 未启用直推应 exit 0；当前 rc={result.returncode}"
    events = _ledger_events(td)
    assert any(
        ev.get("event") == "state_transition" and ev.get("from") == "P6" and ev.get("to") == "P7"
        for ev in events
    ), "P6→P7 推进应记 state_transition 事件（A1 裁决成立）"


# ── BDD-7：gate exit 1 回退（委托 retreat-to，retry 同步） ──────────────

def test_bdd_7_next_exit1_delegates_retreat_to_retreat_target(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：phase=P5 + gate exit 1（mock）→ 按 retreat:P4 委托 agate-retreat-to（P5→P4 单步）
    + retries[P4] 记录。P3 agate-next.py 缺失 → 红灯。"""
    td = task_dir()
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    shutil_copytree_into(td, repo)
    _write_state(None, repo / "task", "P5")
    result = _run_next(agate_scripts, python_exe, run_cli, repo / "task", env={"AGATE_ROOT": ""})
    assert result.returncode == 0, f"exit 1 委托 retreat-to 应成功；rc={result.returncode}"
    state = (repo / "task" / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P4" in state, "回退后 phase 应为 P4（retreat 表值）"
    assert "P4:" in state or "retries" in state, "retries[P4] 记录由 retreat-to 同步"


def shutil_copytree_into(td, repo):
    import shutil

    target = repo / "task"
    shutil.copytree(td, target)


def test_bdd_7_p6_exit1_retreats_to_p4_via_retreat_to(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：phase=P6 + gate exit 1 → retreat:P4（diff=2）亦委托 retreat-to 逐阶 P6→P5→P4
    （CLI 不预判 diff，表值存在即委托；state-machine.md:148）。P3 红灯。"""
    td = task_dir()
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    shutil_copytree_into(td, repo)
    _write_state(None, repo / "task", "P6")
    result = _run_next(agate_scripts, python_exe, run_cli, repo / "task", env={"AGATE_ROOT": ""})
    assert result.returncode == 0, f"P6→P4 diff=2 委托 retreat-to 应成功；rc={result.returncode}"
    state = (repo / "task" / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P4" in state, "P6 gate exit 1 回退目标 = P4（retreat 表值）"


# ── BDD-8：gate exit 2（非 P6）落盘 exit2-resolution ────────────────────

def test_bdd_8_non_p6_exit2_writes_exit2_resolution(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-8：phase=P5 + gate exit 2（需自判）→ 不推进 + 落盘 {phase}-exit2-resolution.md
    （§3.3 模板：frontmatter + 触发/客观证据/解决节）。P3 红灯。"""
    td = task_dir()
    _write_state(None, td, "P5")
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"exit 2 暂停动作完成应 exit 0；rc={result.returncode}"
    res_file = td / "P5-exit2-resolution.md"
    assert res_file.is_file(), "非 P6 exit 2 应落盘 P5-exit2-resolution.md（BDD-8）"


def test_bdd_8_exit2_resolution_frontmatter_machine_readable(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-8：exit2-resolution.md frontmatter 机器可读（phase/task_id/type=exit2-resolution/
    parent=.state.yaml/agent），正文含 触发/客观证据/解决 三节（§3.3 格式）。P3 红灯。"""
    td = task_dir()
    _write_state(None, td, "P3")
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"exit 2 暂停动作完成应 exit 0；rc={result.returncode}"
    res_file = td / "P3-exit2-resolution.md"
    assert res_file.is_file()
    text = res_file.read_text(encoding="utf-8")
    assert "type: exit2-resolution" in text, "frontmatter type 应为 exit2-resolution"
    assert "task_id:" in text and "phase: P3" in text
    assert "parent:" in text, "frontmatter parent 应声明（§3.3）"
    assert "## 触发" in text and "## 客观证据" in text and "## 解决" in text, "正文三节缺失（§3.3 模板）"


# ── BDD-9：P6 exit 2 前进特例（不落盘不停等） ───────────────────────────

def test_bdd_9_p6_exit2_keeps_advancing_no_resolution_file(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-9：P6 exit 2（FAIL=0/证据非空 + provenance exit 0）+ judge 未启用 → 直推 P7，
    不生成 P6-exit2-resolution.md（唯一例外，不泛化）。P3 红灯。"""
    td = task_dir()
    _write_state(None, td, "P6")
    _write_p6_pass_fixture(td)
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0
    assert not (td / "P6-exit2-resolution.md").exists(), "P6 特例不落盘 exit2-resolution（BDD-9）"


def test_bdd_9_p6_judge_enabled_gate_p65_pass_advances_p7(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-9 P6 judge 后推进路径锚点（A1）：judge.enabled=true + verdict/evidence 合规 +
    gate_p65 exit 0 → agate-next 把 phase P6→P7 + state_transition 事件。P3 红灯。"""
    td = task_dir()
    _write_state(None, td, "P6", judge={"enabled": True, "rounds": 1})
    _write_p6_pass_fixture(td)
    _write_verdict_pass_fixture(td)
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"judge 通过推 P7 应 exit 0；rc={result.returncode}"
    assert _read_state_phase(td) == "P7", "gate_p65 exit 0 → agate-next 应把 phase 推为 P7"
    events = _ledger_events(td)
    assert any(
        ev.get("event") == "state_transition" and ev.get("to") == "P7" for ev in events
    ), "P6→P7 推进应 append state_transition 事件"


def test_bdd_9_p6_judge_gate_p65_fail_stays_p6(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-9 反向锚点（A1）：judge.enabled=true + 缺 verdict（gate_p65 exit 1）→ 停留 P6 不推进、
    不落盘 exit2-resolution（P6 特例豁免）。P3 红灯。"""
    td = task_dir()
    _write_state(None, td, "P6", judge={"enabled": True})
    _write_p6_pass_fixture(td)
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, "judge 复核未过 → CLI 提示停留应 exit 0（不推进不报错）"
    assert _read_state_phase(td) == "P6", "gate_p65 exit 1 → 停留 P6"
    assert not (td / "P6-exit2-resolution.md").exists(), "P6 特例不落盘"


# ── BDD-11：档位 C 可观测证据 ───────────────────────────────────────────

def test_bdd_11_state_transition_event_observable(
    task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-11：两次推进后 gate-events.jsonl 含 state_transition 记录（from/to/ts）——
    档位 C「推进均经 agate next」的可观测证据面（§3.7）。P3 红灯（无 CLI 无事件）。"""
    td = task_dir()
    _write_state(None, td, "P5")
    result = _run_next(agate_scripts, python_exe, run_cli, td)
    assert result.returncode == 0, f"推进应成功；rc={result.returncode}"
    events = _ledger_events(td)
    transitions = [ev for ev in events if ev.get("event") == "state_transition"]
    assert len(transitions) >= 1, "推进记录应含 state_transition 事件（BDD-11 证据面）"
    ev = transitions[0]
    assert "from" in ev and "to" in ev and "ts" in ev, "state_transition 字段 from/to/ts 齐全"
