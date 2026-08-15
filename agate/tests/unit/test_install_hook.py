# tests/unit/test_install_hook.py — install-hook.py .gitignore 检测 + ln 软链/复制模式
# （unit/install-hook.bats 6 用例迁移，TAG0011 批次 12）
# 被测：agate/scripts/install-hook.py（git 仓库检测 / hook 软链安装 / .gitignore WARNING）。
# 平台分支（P3 §5.2）：Linux 断言软链语义（os.readlink），Windows 断言文件已安装
#   （复制模式由 AGATE_HOOK_COPY_MODE=1 + fake agate_root 用例覆盖，等价 bats mock ln → cp）。
# 流语义（P2 BLOCKER-1）：install-hook.py 提示写 stdout、错误写 stderr——断言用合并流 .output。

import os
import shutil
import sys

import pytest


def _run_install(run_cli, python_exe, agate_scripts, repo, root, copy_mode=False):
    env = {"AGATE_ROOT": str(root)}
    if copy_mode:
        env["AGATE_HOOK_COPY_MODE"] = "1"
    return run_cli(
        python_exe,
        str(agate_scripts / "install-hook.py"),
        str(root),
        cwd=str(repo),
        env=env,
    )


def _make_fake_root(tmp_path, agate_scripts):
    """等价 bats fake agate_root：cp 三个 hook 薄壳到 fake/scripts/。"""
    fake = tmp_path / "agate-fake"
    (fake / "scripts").mkdir(parents=True)
    for name in ("pre-commit-gate.sh", "commit-msg-self-gate.sh", "pre-push-gate.sh"):
        shutil.copy2(str(agate_scripts / name), str(fake / "scripts" / name))
    return fake


@pytest.mark.windows_smoke
def test_install_1_gitignore_state_yaml_warning(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    (repo / ".gitignore").write_text(".state.yaml\n", encoding="utf-8")

    result = _run_install(run_cli, python_exe, agate_scripts, repo, agate_root)
    assert ".state.yaml" in result.output
    assert "忽略" in result.output


def test_install_2_no_gitignore_no_warning(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path

    result = _run_install(run_cli, python_exe, agate_scripts, repo, agate_root)
    assert not (".state.yaml" in result.output and "忽略" in result.output)


def test_install_3_pre_push_is_symlink(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    _run_install(run_cli, python_exe, agate_scripts, repo, agate_root)

    hook = repo / ".git" / "hooks" / "pre-push"
    if sys.platform == "win32":
        assert hook.is_file()
    else:
        assert os.readlink(str(hook)) == str(agate_scripts / "pre-push-gate.sh")


def test_install_4_existing_pre_push_backed_up_and_replaced(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    hook = repo / ".git" / "hooks" / "pre-push"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    result = _run_install(run_cli, python_exe, agate_scripts, repo, agate_root)
    assert "已备份现有 pre-push hook" in result.output
    if sys.platform == "win32":
        assert hook.is_file()
    else:
        assert os.readlink(str(hook)) == str(agate_scripts / "pre-push-gate.sh")
    assert list(hook.parent.glob("pre-push.bak.*"))


@pytest.mark.windows_smoke
def test_install_5_ln_copy_mode_upgrade_hint(
    git_repo, agate_scripts, python_exe, run_cli, tmp_path
):
    repo = git_repo.path
    fake = _make_fake_root(tmp_path, agate_scripts)

    result = _run_install(run_cli, python_exe, agate_scripts, repo, fake, copy_mode=True)
    assert result.returncode == 0
    assert "复制" in result.output or "需重跑" in result.output
    marker = repo / ".git" / "hooks" / ".agate-root"
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8").strip() == str(fake)


@pytest.mark.windows_smoke
def test_install_6_ln_copy_mode_pre_push_installed(
    git_repo, agate_scripts, python_exe, run_cli, tmp_path
):
    repo = git_repo.path
    fake = _make_fake_root(tmp_path, agate_scripts)

    result = _run_install(run_cli, python_exe, agate_scripts, repo, fake, copy_mode=True)
    assert result.returncode == 0
    assert "复制" in result.output or "需重跑" in result.output
    assert (repo / ".git" / "hooks" / "pre-push").is_file()
