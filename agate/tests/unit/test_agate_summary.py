# tests/unit/test_agate_summary.py — agate-summary.py 版本显示语义迁移（resolve-chain 批次）
# 被测：agate/scripts/agate-summary.py（TAG0008 语义迁移：从"仓库自身 git describe"→"项目解析到的版本 + 原因"）。
# P3 阶段该迁移未实现 → 红灯（断言失败：输出为旧 git-describe 语义，不包含项目解析版本）。
# BDD 映射：BDD-20（.agate-version 锁定 + 原因）、BDD-21（全局 current 回退 + 原因）。
# 平台无关：假 HOME 经 HOME+USERPROFILE env 指向 tmp_path；current/latest 用文本指针（Windows-safe）。

import os

import pytest


def _resolve_env(home):
    return {"AGATE_ROOT": "", "HOME": str(home), "USERPROFILE": str(home)}


def _make_home(tmp_path, versions=("v0.43.0", "v0.44.0"), current="latest", latest="v0.44.0"):
    home = tmp_path / "home"
    for v in versions:
        (home / ".agate" / v).mkdir(parents=True, exist_ok=True)
    (home / ".agate" / "latest").write_text(latest + "\n", encoding="utf-8")
    (home / ".agate" / "current").write_text(current + "\n", encoding="utf-8")
    return home


@pytest.mark.windows_smoke
def test_bdd_20_summary_resolved_version_and_reason(run_cli, python_exe, agate_scripts, tmp_path):
    home = _make_home(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / ".agate-version").write_text("agate: v0.43.0\n", encoding="utf-8")

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-summary.py"),
        cwd=str(project),
        env=_resolve_env(home),
    )
    expected_root = str((home / ".agate" / "v0.43.0").resolve())
    assert result.returncode == 0
    assert expected_root in result.output
    assert "v0.43.0" in result.output
    assert ".agate-version" in result.output  # 原因说明引用 .agate-version


def test_bdd_21b_symlink_pointer_shows_actual_version(run_cli, python_exe, agate_scripts, tmp_path):
    """rev2 CRITICAL-1：软链指针布局下 summary 显示实际版本号（BDD-21 current 回退语义）。

    回归用例：软链布局下 `_resolve_pointer_chain` isdir 短路会把 version 显示成
    "current"/"latest" 而非实际版本号（agate-summary 误导）。
    """
    home = tmp_path / "home"
    for v in ("v0.43.0", "v0.44.0"):
        (home / ".agate" / v).mkdir(parents=True, exist_ok=True)
    try:
        os.symlink("v0.44.0", str(home / ".agate" / "latest"))
        os.symlink("latest", str(home / ".agate" / "current"))
    except (OSError, NotImplementedError):
        pytest.skip("当前平台无法创建软链，软链指针布局无法构建")

    project = tmp_path / "project"
    project.mkdir()
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-summary.py"),
        cwd=str(project),
        env=_resolve_env(home),
    )
    expected_root = str((home / ".agate" / "v0.44.0").resolve())
    assert result.returncode == 0
    assert expected_root in result.output
    assert "v0.44.0" in result.output
    assert "版本：v0.44.0" in result.output, "软链布局下显示版本应为实际版本号，而非 current/latest"


def test_bdd_21_summary_global_current_reason(run_cli, python_exe, agate_scripts, tmp_path):
    home = _make_home(tmp_path)  # current→latest→v0.44.0
    project = tmp_path / "project"
    project.mkdir()

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-summary.py"),
        cwd=str(project),
        env=_resolve_env(home),
    )
    expected_root = str((home / ".agate" / "v0.44.0").resolve())
    assert result.returncode == 0
    assert expected_root in result.output
    assert "v0.44.0" in result.output
    assert "current" in result.output  # 原因说明：全局 current 回退


# --- DSH 安装产物链接校验（防软链指向非权威副本的静默漂移复发）---
# 背景（2026-08-26）：~/.dsh/skills/agate-protocol/SKILL.md 曾被安装成指向
# dsh-workspace/agate-copy（测试用临时副本）而非 ~/.agate 权威链，静默存活 5 天
# 穿过 v0.64.0 发布。机制缺口：安装后无任何校验。本组测试覆盖修复。

_DSH_ARTIFACTS = (
    (".agent-presets/agate/preset.yml", "preset.yml"),
    (".agent-presets/agate/agent.cordis.yml", "agent.cordis.yml"),
    ("skills/agate-protocol/SKILL.md", "SKILL.md"),
)


def _symlink_or_skip(target, link_path):
    try:
        os.symlink(str(target), str(link_path))
    except (OSError, NotImplementedError):
        pytest.skip("当前平台无法创建软链，无法构建 DSH 链接布局")


def test_dsh_links_no_dsh_dir_no_warning(run_cli, python_exe, agate_scripts, tmp_path):
    """无 ~/.dsh（未装 DSH）→ 校验整体跳过，无 DSH 相关警告。"""
    home = _make_home(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    result = run_cli(
        python_exe, str(agate_scripts / "agate-summary.py"),
        cwd=str(project), env=_resolve_env(home),
    )
    assert result.returncode == 0
    assert "DSH 安装产物" not in result.output


@pytest.mark.windows_smoke
def test_dsh_links_canonical_chain_no_warning(run_cli, python_exe, agate_scripts, agate_assets, tmp_path):
    """三个产物软链均指向权威模板（{agate_root}/assets/templates/dsh/）→ 无警告。"""
    if os.name == "nt":
        pytest.skip("DSH 链接校验在 Windows 跳过（复制模式，无 DSH 部署）")
    home = _make_home(tmp_path)
    tpl_dir = agate_assets / "templates" / "dsh"
    for rel, name in _DSH_ARTIFACTS:
        link = home / ".dsh" / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        _symlink_or_skip(tpl_dir / name, link)
    project = tmp_path / "project"
    project.mkdir()
    result = run_cli(
        python_exe, str(agate_scripts / "agate-summary.py"),
        cwd=str(project), env=_resolve_env(home),
    )
    assert result.returncode == 0
    assert "DSH 安装产物" not in result.output


def test_dsh_links_stale_target_warns_with_fix(run_cli, python_exe, agate_scripts, tmp_path):
    """软链指向非权威副本（真实 bug 复现）→ WARNING 指明产物 + 给出 ln -sf 修复命令。"""
    if os.name == "nt":
        pytest.skip("DSH 链接校验在 Windows 跳过（复制模式，无 DSH 部署）")
    home = _make_home(tmp_path)
    stale_dir = tmp_path / "stale-copy"
    stale_dir.mkdir()
    for rel, name in _DSH_ARTIFACTS:
        stale_file = stale_dir / name
        stale_file.write_text("stale\n", encoding="utf-8")
        link = home / ".dsh" / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        _symlink_or_skip(stale_file, link)
    project = tmp_path / "project"
    project.mkdir()
    result = run_cli(
        python_exe, str(agate_scripts / "agate-summary.py"),
        cwd=str(project), env=_resolve_env(home),
    )
    assert result.returncode == 0
    assert "DSH 安装产物" in result.output
    assert "SKILL.md" in result.output
    assert "ln -sf" in result.output  # 附带一条命令即可修复


def test_dsh_links_missing_artifact_warns_not_installed(run_cli, python_exe, agate_scripts, agate_assets, tmp_path):
    """~/.dsh 存在但部分产物缺失 → 提示未安装（含 SETUP.md 指引），不误报为漂移。"""
    if os.name == "nt":
        pytest.skip("DSH 链接校验在 Windows 跳过（复制模式，无 DSH 部署）")
    home = _make_home(tmp_path)
    tpl_dir = agate_assets / "templates" / "dsh"
    rel, name = _DSH_ARTIFACTS[0]
    link = home / ".dsh" / rel
    link.parent.mkdir(parents=True, exist_ok=True)
    _symlink_or_skip(tpl_dir / name, link)  # 只装 1 个，其余 2 个缺失
    project = tmp_path / "project"
    project.mkdir()
    result = run_cli(
        python_exe, str(agate_scripts / "agate-summary.py"),
        cwd=str(project), env=_resolve_env(home),
    )
    assert result.returncode == 0
    assert "未安装" in result.output
    assert "SETUP.md" in result.output
