# tests/unit/test_agate_version_install.py — agate-install（安装/卸载/环境探测）TDD 测试
# （TAG0008 批次 install，BDD-1~8 1:1 映射）
# 被测：agate/scripts/agate-install.py（P3 阶段尚未实现 → 当前全部红灯，B 类：模块不存在）
# 接口契约（P3-test-cases-install.md §0）：
#   * agate-install [<version> | --uninstall <version> | --check]
#   * AGATE_REPO_URL env = 版本源仓库（测试指向本地临时 repo，含 v0.43.0 / v0.48.0 tag）
#   * HOME env 重定向 ~ 到 tmp_path，~/.agate = <home>/.agate（防触碰真实 ~/.agate）
# 平台分支（AGENTS.md 平台无关原则）：
#   * 指针断言 POSIX 软链 / Windows 文本指针分支；worktree 路径经 os.path.normcase 匹配
#   * python 一律用 conftest python_exe fixture，不写死 python3

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _run_install(run_cli, python_exe, agate_scripts, home, *args, repo_url=None, extra_env=None):
    env = {"HOME": str(home), "USERPROFILE": str(home)}
    if repo_url is not None:
        env["AGATE_REPO_URL"] = str(repo_url)
    if extra_env:
        env.update(extra_env)
    return run_cli(python_exe, str(agate_scripts / "agate-install.py"), *args, env=env)


def _tag_upstream(git_repo):
    """建版本源 repo：两次 commit + v0.43.0 / v0.48.0 tag（v0.48.0 最新）。"""
    scripts = git_repo.path / "agate" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "README.md").write_text("# agate upstream v0.43.0\n", encoding="utf-8")
    git_repo.commit("base v0.43.0")
    git_repo.git("tag", "v0.43.0")
    (scripts / "README.md").write_text("# agate upstream v0.48.0\n", encoding="utf-8")
    git_repo.commit("bump v0.48.0")
    git_repo.git("tag", "v0.48.0")


def _resolve_pointer(agate_home, name):
    """解析 ~/.agate/{name} 指针链 → 最终路径（兼容软链 / 文本指针 / current→latest）。"""
    node = agate_home / name
    for _ in range(5):
        if node.is_symlink():
            target = Path(os.readlink(str(node)))
            node = target if target.is_absolute() else node.parent / target
            continue
        if node.is_file() and not node.is_dir():
            content = node.read_text(encoding="utf-8").strip()
            if content:
                p = Path(content)
                node = p if p.is_absolute() else agate_home / p
                continue
        break
    return node


def _git(git_exe, *args, cwd=None):
    return subprocess.run(
        [git_exe] + [str(a) for a in args],
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _worktree_porcelain(git_exe, repo_clone):
    return _git(git_exe, "-C", str(repo_clone), "worktree", "list", "--porcelain").stdout


def _head_of(git_exe, worktree_dir):
    return _git(git_exe, "-C", str(worktree_dir), "rev-parse", "HEAD").stdout.strip()


def _tag_commit_of(git_exe, repo_clone, tag):
    return _git(git_exe, "-C", str(repo_clone), "rev-parse", tag).stdout.strip()


@pytest.mark.windows_smoke
def test_bdd_1_latest_pointer_after_noarg_install(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"

    result = _run_install(run_cli, python_exe, agate_scripts, home, repo_url=py_path(git_repo.path))
    assert result.returncode == 0

    agate_home = home / ".agate"
    latest = agate_home / "latest"
    assert latest.exists()
    if sys.platform == "win32":
        assert not latest.is_dir()
    else:
        assert latest.is_symlink()
    target = _resolve_pointer(agate_home, "latest")
    assert target.is_dir()
    assert target.name == "v0.48.0"


def test_bdd_2_version_dir_worktree_of_tag(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"

    result = _run_install(run_cli, python_exe, agate_scripts, home, "v0.48.0", repo_url=py_path(git_repo.path))
    assert result.returncode == 0

    version_dir = home / ".agate" / "v0.48.0"
    assert version_dir.is_dir()

    git_exe = shutil.which("git")
    assert git_exe
    repo_clone = home / ".agate" / "repo"
    wt = _worktree_porcelain(git_exe, repo_clone)
    assert os.path.normcase(str(version_dir)) in os.path.normcase(wt)
    assert _head_of(git_exe, version_dir) == _tag_commit_of(git_exe, repo_clone, "v0.48.0")


def test_bdd_3_reinstall_idempotent(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"
    url = py_path(git_repo.path)

    first = _run_install(run_cli, python_exe, agate_scripts, home, "v0.48.0", repo_url=url)
    assert first.returncode == 0

    result = _run_install(run_cli, python_exe, agate_scripts, home, "v0.48.0", repo_url=url)
    assert result.returncode == 0

    version_dir = home / ".agate" / "v0.48.0"
    assert version_dir.is_dir()
    git_exe = shutil.which("git")
    assert git_exe
    wt = _worktree_porcelain(git_exe, home / ".agate" / "repo")
    assert os.path.normcase(wt).count(os.path.normcase(str(version_dir))) == 1


def test_bdd_4_current_defaults_to_latest(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"

    result = _run_install(run_cli, python_exe, agate_scripts, home, repo_url=py_path(git_repo.path))
    assert result.returncode == 0

    agate_home = home / ".agate"
    assert (agate_home / "current").exists()
    current = _resolve_pointer(agate_home, "current")
    latest = _resolve_pointer(agate_home, "latest")
    assert current == latest
    assert current.name == "v0.48.0"
    assert current.is_dir()


@pytest.mark.windows_smoke
def test_bdd_5_uninstall_removes_dir_and_clean_pointer(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"
    url = py_path(git_repo.path)

    latest_install = _run_install(run_cli, python_exe, agate_scripts, home, repo_url=url)
    assert latest_install.returncode == 0
    older = _run_install(run_cli, python_exe, agate_scripts, home, "v0.43.0", repo_url=url)
    assert older.returncode == 0

    result = _run_install(run_cli, python_exe, agate_scripts, home, "--uninstall", "v0.43.0")
    assert result.returncode == 0
    assert not (home / ".agate" / "v0.43.0").exists()

    git_exe = shutil.which("git")
    assert git_exe
    wt = _worktree_porcelain(git_exe, home / ".agate" / "repo")
    assert os.path.normcase(str(home / ".agate" / "v0.43.0")) not in os.path.normcase(wt)

    agate_home = home / ".agate"
    for name in ("latest", "current"):
        if (agate_home / name).exists():
            target = _resolve_pointer(agate_home, name)
            assert target.is_dir(), f"指针 {name} 悬挂指向不存在的目录"


def test_bdd_5b_uninstall_pointed_version_repoints_symlink(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    """rev2 CRITICAL-1：软链布局下卸载被 latest/current 指向的版本必须触发指针修复（BDD-5 红线）。

    回归用例：`_resolve_pointer` 先判 isdir 会对"软链→版本目录"短路，返回软链路径自身
    （basename="latest"/"current"），使 `_repair_pointers` 的 `before != removed_version`
    恒不匹配 → 卸载后指针悬空。本用例断言卸载后指针解析到剩余有效版本目录。
    """
    if os.name == "nt":
        pytest.skip("POSIX 软链指针布局仅在非 Windows 平台成立")
    _tag_upstream(git_repo)
    home = tmp_path / "home"
    url = py_path(git_repo.path)

    latest_install = _run_install(run_cli, python_exe, agate_scripts, home, repo_url=url)
    assert latest_install.returncode == 0
    older = _run_install(run_cli, python_exe, agate_scripts, home, "v0.43.0", repo_url=url)
    assert older.returncode == 0

    agate_home = home / ".agate"
    assert (agate_home / "latest").is_symlink()
    assert (agate_home / "current").is_symlink()

    result = _run_install(run_cli, python_exe, agate_scripts, home, "--uninstall", "v0.48.0")
    assert result.returncode == 0
    assert not (agate_home / "v0.48.0").exists()

    git_exe = shutil.which("git")
    assert git_exe
    wt = _worktree_porcelain(git_exe, home / ".agate" / "repo")
    assert os.path.normcase(str(home / ".agate" / "v0.48.0")) not in os.path.normcase(wt)

    for name in ("latest", "current"):
        target = _resolve_pointer(agate_home, name)
        assert target.is_dir(), f"指针 {name} 悬挂指向不存在的目录"
        assert target.name == "v0.43.0", f"指针 {name} 应重指到 v0.43.0，实际解析到 {target.name}"


def test_bdd_6_uninstall_rejected_when_referenced(
    git_repo, python_exe, run_cli, agate_scripts, tmp_path, py_path
):
    _tag_upstream(git_repo)
    home = tmp_path / "home"
    install = _run_install(run_cli, python_exe, agate_scripts, home, "v0.43.0", repo_url=py_path(git_repo.path))
    assert install.returncode == 0

    project = home / "myproject"
    project.mkdir(parents=True)
    (project / ".agate-version").write_text("agate: v0.43.0\n", encoding="utf-8")

    result = _run_install(run_cli, python_exe, agate_scripts, home, "--uninstall", "v0.43.0")
    assert result.returncode != 0
    assert "v0.43.0" in result.output
    assert ("myproject" in result.output) or (".agate-version" in result.output)
    assert (home / ".agate" / "v0.43.0").is_dir()

    git_exe = shutil.which("git")
    assert git_exe
    wt = _worktree_porcelain(git_exe, home / ".agate" / "repo")
    assert os.path.normcase(str(home / ".agate" / "v0.43.0")) in os.path.normcase(wt)


@pytest.mark.windows_smoke
def test_bdd_7_env_check_all_present_exit_0(python_exe, run_cli, agate_scripts, tmp_path):
    home = tmp_path / "home"
    result = _run_install(run_cli, python_exe, agate_scripts, home, "--check")
    assert result.returncode == 0
    assert "git" in result.output
    assert "bash" in result.output
    assert "yaml" in result.output
    assert ("python3" in result.output) or ("python" in result.output)


@pytest.mark.windows_smoke
def test_bdd_8_env_check_missing_pyyaml_guidance(python_exe, run_cli, agate_scripts, tmp_path):
    venv = tmp_path / "noyaml"
    created = subprocess.run(
        [python_exe, "-m", "venv", str(venv)], capture_output=True, text=True, encoding="utf-8"
    )
    assert created.returncode == 0
    venv_bin = venv / ("Scripts" if os.name == "nt" else "bin")
    assert venv_bin.is_dir()

    home = tmp_path / "home"
    path = str(venv_bin) + os.pathsep + os.environ.get("PATH", "")
    result = _run_install(run_cli, python_exe, agate_scripts, home, "--check", extra_env={"PATH": path})
    assert result.returncode != 0
    assert "yaml" in result.output
    if sys.platform == "win32":
        assert ("PYTHONUTF8" in result.output) or ("Git for Windows" in result.output)
    else:
        assert "pip install" in result.output
