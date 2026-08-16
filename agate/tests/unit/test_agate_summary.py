# tests/unit/test_agate_summary.py — agate-summary.py 版本显示语义迁移（resolve-chain 批次）
# 被测：agate/scripts/agate-summary.py（TAG0008 语义迁移：从"仓库自身 git describe"→"项目解析到的版本 + 原因"）。
# P3 阶段该迁移未实现 → 红灯（断言失败：输出为旧 git-describe 语义，不包含项目解析版本）。
# BDD 映射：BDD-20（.agate-version 锁定 + 原因）、BDD-21（全局 current 回退 + 原因）。
# 平台无关：假 HOME 经 HOME+USERPROFILE env 指向 tmp_path；current/latest 用文本指针（Windows-safe）。

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
