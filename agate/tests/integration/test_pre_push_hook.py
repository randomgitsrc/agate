# tests/integration/test_pre_push_hook.py — pre-push hook 集成测试
# （integration/pre-push-hook.bats 4 用例迁移，TAG0011 批次 12）
# 被测：agate/scripts/pre-push-gate.sh（bash 薄壳 exec pre-push-gate.py）+ install-hook.py 真安装。
# git hook 真环境：install-hook.py 把 hook 装进 .git/hooks/（Linux 软链 / Windows 复制模式）。
# 平台分支（P3 §5.2）：Linux 断言软链语义（os.readlink），Windows 断言文件已安装（复制模式覆盖）。
# stdin 管道（等价 bats `echo '...' | bash pre-push-gate.sh`）：run_cli input= 传入推送行。

import os
import shutil
import sys

import pytest


def _install(run_cli, python_exe, agate_scripts, repo, root):
    """等价 `( cd "$repo" && "$PYTHON" "$AGATE_ROOT/scripts/install-hook.py" "$AGATE_ROOT" )`。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "install-hook.py"),
        str(root),
        cwd=str(repo),
    )


def _assert_pre_push_installed(repo, agate_scripts):
    """等价 bats 平台分支：Linux 断言软链指向 pre-push-gate.sh，Windows 断言文件存在。"""
    hook = repo / ".git" / "hooks" / "pre-push"
    if sys.platform == "win32":
        assert hook.is_file()
    else:
        assert os.readlink(str(hook)) == str(agate_scripts / "pre-push-gate.sh")


def _run_gate(run_cli, agate_scripts, agate_root, repo, line, env=None):
    """等价 `echo 'LINE' | bash pre-push-gate.sh 2>&1 || true`（2>&1 合并流由 run_cli 承接）。"""
    gate_env = {"AGATE_ROOT": str(agate_root)}
    if env:
        gate_env.update(env)
    return run_cli(
        "bash",
        str(agate_scripts / "pre-push-gate.sh"),
        input=line,
        cwd=str(repo),
        env=gate_env,
    )


@pytest.mark.windows_smoke
def test_pre_push_1_new_branch_skips_check(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    _install(run_cli, python_exe, agate_scripts, repo, agate_root)
    _assert_pre_push_installed(repo, agate_scripts)

    (repo / "file.txt").write_text("test\n", encoding="utf-8")
    git_repo.stage("file.txt")
    git_repo.git("commit", "-m", "init", "--no-gpg-sign", "--no-verify")
    sha = git_repo.git("rev-parse", "HEAD").stdout.strip()
    line = f"refs/heads/main {sha} refs/heads/main {'0' * 40}"

    result = _run_gate(run_cli, agate_scripts, agate_root, repo, line)
    assert "新分支" in result.output


@pytest.mark.windows_smoke
def test_pre_push_2_copy_mode_install_hint(
    git_repo, agate_scripts, agate_root, python_exe, run_cli, tmp_path
):
    repo = git_repo.path
    fake = tmp_path / "agate-fake"
    (fake / "scripts").mkdir(parents=True)
    for name in ("pre-commit-gate.sh", "commit-msg-self-gate.sh", "pre-push-gate.sh"):
        shutil.copy2(str(agate_scripts / name), str(fake / "scripts" / name))

    result = run_cli(
        python_exe,
        str(agate_scripts / "install-hook.py"),
        str(fake),
        cwd=str(repo),
        env={"AGATE_HOOK_COPY_MODE": "1", "AGATE_ROOT": str(agate_root)},
    )
    assert "复制" in result.output or "需重跑" in result.output
    assert (repo / ".git" / "hooks" / "pre-push").is_file()


def test_pre_push_3_big_change_triggers_hint(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    _install(run_cli, python_exe, agate_scripts, repo, agate_root)

    (repo / "agate").mkdir(parents=True)
    (repo / "agate" / "test.md").write_text(
        "line1\nline2\nline3\nline4\n", encoding="utf-8"
    )
    git_repo.stage("agate/test.md")
    git_repo.git("commit", "-m", "add agate file", "--no-gpg-sign", "--no-verify")
    prev_sha = git_repo.git("rev-parse", "HEAD").stdout.strip()

    (repo / "agate" / "test.md").write_text(
        "line1-new\nline2-new\nline3-new\nline4-new\nline5-new\n", encoding="utf-8"
    )
    git_repo.stage("agate/test.md")
    git_repo.git("commit", "-m", "big change", "--no-gpg-sign", "--no-verify")
    current_sha = git_repo.git("rev-parse", "HEAD").stdout.strip()

    line = f"refs/heads/main {current_sha} refs/heads/main {prev_sha}"
    result = _run_gate(
        run_cli,
        agate_scripts,
        agate_root,
        repo,
        line,
        env={"AGATE_ALIGNMENT_REVIEW_THRESHOLD": "2"},
    )
    assert "改动" in result.output


def test_pre_push_4_zero_match_no_integer_error(
    git_repo, agate_scripts, agate_root, python_exe, run_cli
):
    repo = git_repo.path
    _install(run_cli, python_exe, agate_scripts, repo, agate_root)

    (repo / "file.txt").write_text("test\n", encoding="utf-8")
    git_repo.stage("file.txt")
    git_repo.git("commit", "-m", "init", "--no-gpg-sign", "--no-verify")
    prev_sha = git_repo.git("rev-parse", "HEAD").stdout.strip()

    (repo / "file.txt").write_text("test2\n", encoding="utf-8")
    git_repo.stage("file.txt")
    git_repo.git("commit", "-m", "change", "--no-gpg-sign", "--no-verify")
    current_sha = git_repo.git("rev-parse", "HEAD").stdout.strip()

    line = f"refs/heads/main {current_sha} refs/heads/main {prev_sha}"
    result = _run_gate(run_cli, agate_scripts, agate_root, repo, line)
    assert "整数表达式" not in result.output
    assert "integer expression" not in result.output
    assert result.returncode == 0
