# tests/unit/test_check_routing.py — ceremony 路由校验（TAG0019 D3，BDD-6..10）
# 被测：agate/scripts/check-routing.py（TASK_DIR）
# exit 语义（P2-design.md §2.3）：
#   0 = 通过（不声明=standard / thin 四要素全过 + 算分非薄 / 更保守声明合法）
#   1 = 校验不满足（fail-closed：thin 缺要素 / 声明薄于算分 / 非法值 / 算分异常 git_ok:false）
#   2 = 无 P1 文件（对齐 check-pruning exit 2 语义）
# 同源复用（BDD-10）：importlib 加载 check-pruning 复用 _md_field/_read_p1/_staged_source_count 及
#   coupling_checklist 流式 / 跳过风险 判据——无第二份实现。
# TDD 红灯：模块 P4 前未实现 → CLI "can't open file" exit 2；被迫期望返码的用例断言失败 = 真红灯。
#
# 平台无关：无裸 python3 / 无 /tmp / 无 POSIX symlink 字面；git 经 run_git（被测脚本）。

import importlib.util
import shutil
import sys

import pytest


def _run_routing(agate_scripts, python_exe, run_cli, task_arg, cwd=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "check-routing.py"),
        task_arg,
        cwd=cwd,
    )


def _assert_exit(result, expected):
    """断言退出码；模块未实现（python "can't open file"）时同时失败 → 防假红灯。"""
    assert "can't open file" not in result.output, f"被测模块未实现（假红灯）: {result.output!r}"
    assert result.returncode == expected


_DEFAULT_PHASES = "P0, P1, P2, P3, P4, P5, P6, P7, P8"


def _write_p1(task_dir, *, ceremony=None, coupling=True, skip_risk=True, phases=None):
    """写 P1：frontmatter（risk_level/phases/可选 ceremony）+ coupling_checklist + 跳过风险。"""
    ph = ", ".join(phases) if phases else _DEFAULT_PHASES
    lines = ["---", "agent: test", "risk_level: low", f"phases: [{ph}]"]
    if ceremony is not None:
        lines.append(f"ceremony: {ceremony}")
    lines.append("---")
    text = "\n".join(lines) + "\n"
    if coupling:
        text += "coupling_checklist: [api-schema: checked]\n"
    if skip_risk:
        text += "\n跳过风险: 低\n"
    text += "### 主流程\n#### BDD-1: test\n"
    (task_dir / "P1-requirements.md").write_text(text, encoding="utf-8")


def _git_repo_init(git_repo):
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    return repo


def _thin_repo(git_repo, task_dir, **p1_kwargs):
    """git repo + 暂存单个 tests 类文件（file-type low / 规模≤5 / 无敏感 / 无反向引用 → 算分 thin）。"""
    repo = _git_repo_init(git_repo)
    td = task_dir()
    _write_p1(td, **p1_kwargs)
    p = repo / "agate" / "tests" / "unit" / "test_foo.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def test_x():\n    pass\n", encoding="utf-8")
    git_repo.stage("agate/tests/unit/test_foo.py")
    shutil.copytree(td, repo / "task")
    return repo


def _standard_repo(git_repo, task_dir, **p1_kwargs):
    """git repo + 暂存 src/app.py（file-type medium → 算分 standard）。"""
    repo = _git_repo_init(git_repo)
    td = task_dir()
    _write_p1(td, **p1_kwargs)
    p = repo / "src" / "app.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def main():\n    pass\n", encoding="utf-8")
    git_repo.stage("src/app.py")
    shutil.copytree(td, repo / "task")
    return repo


# ===== BDD-6：ceremony 合法值声明 =====

@pytest.mark.windows_smoke
@pytest.mark.parametrize("ceremony", ["thin", "standard", "full"])
def test_bdd_6_ceremony_valid_value_passes(
    ceremony, git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-6：ceremony: thin/standard/full 均为合法声明（thin 需四要素齐全才过）。"""
    repo = _thin_repo(git_repo, task_dir, ceremony=ceremony)
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 0)


def test_bdd_6_ceremony_invalid_value_blocked(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-6：ceremony: 非三值（light）→ check-routing 非法值兜底 exit 1。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="light")
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 1)


# ===== BDD-7：thin 四要素 fail-closed =====

def test_bdd_7_thin_all_four_elements_exit_0(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：ceremony: thin + coupling_checklist + 跳过风险 + P5/P6 保留 四要素齐全 → exit 0。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="thin")
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 0)


def test_bdd_7_thin_missing_coupling_checklist_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：thin 缺"逐信号 checklist"（coupling_checklist 流式）→ exit 1 回退 standard。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="thin", coupling=False)
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 1)


def test_bdd_7_thin_missing_skip_risk_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：thin 缺"跳过风险:" 声明 → exit 1 回退 standard。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="thin", skip_risk=False)
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 1)


def test_bdd_7_thin_missing_p5_p6_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-7：thin 且 phases 裁剪 P5/P6（薄化验证/验收）→ exit 1 回退 standard。"""
    phases = ["P0", "P1", "P2", "P3", "P4", "P7", "P8"]
    repo = _thin_repo(git_repo, task_dir, ceremony="thin", phases=phases)
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 1)


def test_bdd_7_thin_score_anomaly_git_ok_false_exit_1(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-7 分支清单（算分异常 fail-closed）：非 git 上下文→run_git 失败→git_ok:false + thin → exit 1。"""
    d = tmp_path / "task"
    d.mkdir()
    _write_p1(d, ceremony="thin")
    result = _run_routing(agate_scripts, python_exe, run_cli, str(d))
    _assert_exit(result, 1)


# ===== BDD-8：不声明 = standard =====

def test_bdd_8_no_ceremony_defaults_standard_exit_0(
    tmp_path, agate_scripts, python_exe, run_cli
):
    """BDD-8：frontmatter 无 ceremony 字段（存量/新任务）→ 按 standard 处理不拦截（exit 0）。"""
    d = tmp_path / "task"
    d.mkdir()
    _write_p1(d, ceremony=None)
    result = _run_routing(agate_scripts, python_exe, run_cli, str(d))
    _assert_exit(result, 0)


# ===== BDD-9：声明 vs 算分一致性（单向 fail-closed） =====

def test_bdd_9_declare_thin_scored_standard_exit_1(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-9：算分 tier=standard/full 而声明 thin → exit 1（声明薄于算分，单向 fail-closed）。"""
    repo = _standard_repo(git_repo, task_dir, ceremony="thin")
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 1)


def test_bdd_9_reverse_conservative_not_blocked(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-9：反向（算分 thin 而声明 standard/full，更保守）→ 不拦截（exit 0）。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="standard")
    result = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    _assert_exit(result, 0)


# ===== BDD-10：同源判定（对拍 + importlib 上下文，无独立重写） =====

def test_bdd_10_same_fixture_consistent_with_check_pruning(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-10：同一合法 thin 档 fixture，check-routing 与 check-pruning 判定一致（均 exit 0）。"""
    repo = _thin_repo(git_repo, task_dir, ceremony="thin")
    r_routing = _run_routing(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    r_pruning = run_cli(
        python_exe, str(agate_scripts / "check-pruning.py"), "task", cwd=str(repo)
    )
    _assert_exit(r_routing, 0)
    assert r_pruning.returncode == 0
    assert r_routing.returncode == r_pruning.returncode


def test_bdd_10_no_p1_both_exit_2(tmp_path, agate_scripts, python_exe, run_cli):
    """BDD-10 分支清单（P1 缺失 exit 2）：无 P1 文件 → 两脚本同源对齐 exit 2。"""
    d = tmp_path / "task"
    d.mkdir()
    r_routing = _run_routing(agate_scripts, python_exe, run_cli, str(d))
    r_pruning = run_cli(python_exe, str(agate_scripts / "check-pruning.py"), str(d))
    _assert_exit(r_routing, 2)
    assert r_pruning.returncode == 2
    assert r_routing.returncode == r_pruning.returncode


def test_bdd_10_importlib_context_agate_common_importable_reuse(agate_scripts, tmp_path):
    """BDD-10 + 评审缺口：importlib 上下文 agate_common 可导入 + check-routing 复用 check-pruning 同源函数（无独立重写/分叉）。"""
    sys.path.insert(0, str(agate_scripts))
    try:
        import agate_common  # 双层模块 sys.path 依赖不可静默退化

        def _load(name):
            spec = importlib.util.spec_from_file_location(
                "agate_test_" + name.replace(".py", ""), str(agate_scripts / name)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        cp_mod = _load("check-pruning.py")
        cr_mod = _load("check-routing.py")
    finally:
        sys.path.pop(0)
    # 同源复用：check-routing 暴露 check-pruning._staged_source_count（非独立重写）
    assert callable(getattr(cr_mod, "_staged_source_count", None))
    assert callable(agate_common.run_git)
    assert callable(getattr(cp_mod, "_staged_source_count", None))
