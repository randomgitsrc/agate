# agate/tests/unit/test_tag0027_b1_agate_advance_cli.py — TAG0027 B1 批：agate advance 回退引导（BDD-10）
#
# 被测契约（P2-design §3.4 定案 D4-A + P1 BDD-10 [BASELINE_CHANGE: P6→P4]）：
#   新增脚本 agate/scripts/agate-advance.py [TASK_DIR] [--to {phase}] [--reason {text}]（P4 新建）：
#     * --to 目标与当前 diff ≥ 2（如 P6→P4）→ 提示「diff≥2 须先 PAUSED（check-state-transition
#       会拦截直退）」引导归档 + 置 PAUSED，不自行回退（state-machine.md:647-654 人工直跳路径）
#     * diff = 1（如 P6→P5）→ 等价委托 agate-retreat-to.py 单步（逐阶 diff=1 独立 commit，retry
#       记录同步；retreat-to 自动化与人工直跳不同轨，不触发 PAUSED 拦截）
#     * 不传 --to → 打印当前 phase 的 next/retreat 转移表建议
#     * advance 不内联回退实现（边界：只做目标解析 + 合法性提示 + 委托，I-7 复用而非重造）
#
# TDD 红灯语义：被测对象 = 新增 agate-advance.py，P3 不存在 → subprocess rc 2（can't open
#   file）→ 断言全失败 = B 类真红灯（被测模块未实现）。
# 平台无关：tmp_path/git_repo fixture + run_cli(python_exe,...)；无 /tmp 字面量。

import pytest

_ADVANCE_SCRIPT = "agate-advance.py"


def _run_advance(agate_scripts, python_exe, run_cli, td, *args, cwd=None):
    script = agate_scripts / _ADVANCE_SCRIPT
    cmd = [python_exe, str(script)]
    if td is not None:
        cmd.append(str(td))
    cmd.extend(args)
    return run_cli(*cmd, cwd=cwd)


def _write_state(td, phase, retries_yaml="retries: {}"):
    (td / ".state.yaml").write_text(
        f"task_id: T001\nphase: {phase}\nstatus: active\n{retries_yaml}\n",
        encoding="utf-8",
    )


def _init_task_repo(git_repo, phase):
    """git repo + docs/tasks/T001 布局任务（agate-retreat-to 期望的任务目录形态）。"""
    repo = git_repo.path
    task = repo / "docs" / "tasks" / "T001"
    task.mkdir(parents=True)
    (task / "P6-evidence").mkdir(parents=True)
    _write_state(task, phase)
    (task / "P6-acceptance.md").write_text("p6\n", encoding="utf-8")
    (task / "P6-evidence" / "x.png").write_bytes(b"x" * 100)
    git_repo.commit("init")
    return repo, task


def test_bdd_10_advance_diff2_manual_jump_prompts_paused(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-10：P6 --to P4（diff=2 人工直跳）→ 提示须先 PAUSED，不自行改 phase（拦截语义）。
    P3 agate-advance.py 缺失 → 红灯。"""
    repo, task = _init_task_repo(git_repo, "P6")
    result = _run_advance(
        agate_scripts, python_exe, run_cli, "docs/tasks/T001",
        "--to", "P4", "--reason", "诊断", cwd=str(repo),
    )
    assert result.returncode == 0, f"引导完成应 exit 0；rc={result.returncode}"
    assert "PAUSED" in result.output, "diff≥2 人工直跳应提示先 PAUSED（state-machine.md:647-654）"
    state = (task / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P6" in state, "diff≥2 直跳不自行回退（拦截为 PAUSED 引导，非表内直退）"


def test_bdd_10_advance_diff1_delegates_retreat_to(
    git_repo, agate_scripts, python_exe, run_cli
):
    """BDD-10：P6 --to P5（diff=1）→ 委托 agate-retreat-to 单步（逐阶 diff=1 独立 commit，
    retry 同步，不触发 PAUSED 拦截）。P3 agate-advance.py 缺失 → 红灯。"""
    repo, task = _init_task_repo(git_repo, "P6")
    result = _run_advance(
        agate_scripts, python_exe, run_cli, "docs/tasks/T001",
        "--to", "P5", "--reason", "诊断", cwd=str(repo),
    )
    assert result.returncode == 0, f"diff=1 委托 retreat-to 应成功；rc={result.returncode}"
    state = (task / ".state.yaml").read_text(encoding="utf-8")
    assert "phase: P5" in state, "diff=1 委托 retreat-to 单步后 phase 应为 P5"
    log = git_repo.git("log", "--oneline").stdout
    assert "retreat" in log.lower() or "P6 -> P5" in log, "retreat-to 单步应独立 commit（可观测）"
