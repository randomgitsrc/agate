# tests/integration/test_commit_msg_self_gate_integration.py — commit-msg hook 真环境
# （integration/commit-msg-self-gate.bats 6 用例迁移，TAG0011 批次 12）
# git hook 真环境：把 commit-msg-self-gate.sh 复制到 .git/hooks/commit-msg（等价 bats cp + chmod +x），
# git commit 时 hook 被 git 自动调用（subprocess 调 bash 薄壳，BDD-11）。
# 关键：hook 是复制非软链，AGATE_ROOT 靠环境变量传递（bats load.bash export 等价）——
#   复制模式下 wrapper 的 readlink -f 定位到 .git/hooks 目录，须 env AGATE_ROOT 指向真实 agate 根。
# 流语义（P2 BLOCKER-1）：hook WARNING 写 stderr，git 转发出现在合并流——断言用 result.output。

import os
import shlex
import shutil
import sys

import pytest


def _setup_hook(git_repo, agate_scripts):
    """等价 bats setup：init commit + 复制 hook 到 .git/hooks/commit-msg + 建 repo/agate 目录。"""
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.stage("README.md")
    git_repo.commit("init")

    hook = repo / ".git" / "hooks" / "commit-msg"
    shutil.copy2(str(agate_scripts / "commit-msg-self-gate.sh"), str(hook))
    hook.chmod(0o755)

    (repo / "agate" / "scripts").mkdir(parents=True)
    (repo / "agate" / "assets").mkdir(parents=True)
    shutil.copy2(
        str(agate_scripts / "commit-msg-self-gate.sh"),
        str(repo / "agate" / "scripts" / "commit-msg-self-gate.sh"),
    )
    return repo


def _commit(run_cli, bash, repo, agate_root, *args):
    """bash 包装 git（对照 test_bdd_19：Windows 直接 spawn git 时 hook 被静默跳过）。
    env 传 AGATE_ROOT（hook 复制模式依赖），经 bash 继承给 git/hook。"""
    msg = " ".join(shlex.quote(a) for a in args)
    return run_cli(
        bash,
        "-c",
        f"cd {shlex.quote(str(repo))} && git commit {msg}",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )


@pytest.mark.windows_smoke
def test_csg_1_readme_triggers_warning(git_repo, agate_scripts, agate_root, run_cli, bash, tmp_path):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "README.md").write_text("change\n", encoding="utf-8")
    git_repo.stage("README.md")

    # === TEMP DIAGNOSTIC rev3（CI 实证，确认根因后清理） ===
    print(f"[DIAG-a] sys.platform={sys.platform!r}")
    print(f"[DIAG-a] bash={bash!r}")
    print(f"[DIAG-a] shutil.which('bash')={shutil.which('bash')!r}")
    print(f"[DIAG-a] os.environ.get('PATH')={os.environ.get('PATH')!r}")
    hook = repo / ".git" / "hooks" / "commit-msg"
    print(f"[DIAG-b] hook.exists()={hook.exists()}")
    print(f"[DIAG-b] os.access(hook, os.X_OK)={os.access(hook, os.X_OK)}")
    print(f"[DIAG-b] mode={oct(hook.stat().st_mode) if hook.exists() else 'n/a'}")
    gv = run_cli("git", "version")
    print(f"[DIAG-c] git version rc={gv.returncode} out={gv.output!r}")
    hp = run_cli("git", "-C", str(repo), "config", "core.hooksPath")
    print(f"[DIAG-c] core.hooksPath rc={hp.returncode} out={hp.output!r}")
    msg_file = tmp_path / "commit-msg"
    msg_file.write_text("update readme\n", encoding="utf-8")
    man = run_cli(
        bash,
        str(hook),
        str(msg_file),
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    print(f"[DIAG-d] manual hook rc={man.returncode}")
    print(f"[DIAG-d] manual hook stdout={man.stdout!r}")
    print(f"[DIAG-d] manual hook stderr={man.stderr!r}")
    man_noenv = run_cli(bash, str(hook), str(msg_file), cwd=str(repo))
    print(f"[DIAG-d] manual hook(noenv) rc={man_noenv.returncode}")
    print(f"[DIAG-d] manual hook(noenv) stdout={man_noenv.stdout!r}")
    print(f"[DIAG-d] manual hook(noenv) stderr={man_noenv.stderr!r}")
    # === END TEMP DIAGNOSTIC ===

    result = _commit(run_cli, bash, repo, agate_root, "-m", "update readme")
    print(f"[DIAG-e] commit rc={result.returncode}")
    print(f"[DIAG-e] commit stdout={result.stdout!r}")
    print(f"[DIAG-e] commit stderr={result.stderr!r}")

    # === TEMP DIAG-f/g/h rev3-r2: 区分 find_hook/执行失败 vs 输出被吞（CI 实证后清理） ===
    # DIAG-h: git 视角的 hooks 路径
    hp2 = run_cli("git", "-C", str(repo), "rev-parse", "--git-path", "hooks")
    print(f"[DIAG-h] git rev-parse --git-path hooks rc={hp2.returncode} out={hp2.output!r}")
    hpf = run_cli("git", "-C", str(repo), "config", "--show-origin", "--get", "core.hooksPath")
    print(f"[DIAG-h] config --show-origin core.hooksPath rc={hpf.returncode} out={hpf.output!r}")

    # DIAG-f: GIT_TRACE 看 git 是否 attempt 跑 commit-msg hook
    trace = run_cli(
        bash,
        "-c",
        f"cd {shlex.quote(str(repo))} && git commit --allow-empty -m 'trace test'",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root), "GIT_TRACE": "1"},
    )
    print(f"[DIAG-f] GIT_TRACE commit rc={trace.returncode}")
    for line in trace.stderr.splitlines():
        if any(k in line.lower() for k in ("run_command", "hook", "prefix","exec")):
            print(f"[DIAG-f] {line[:300]!r}")

    # DIAG-g: 换成 trivial marker hook，验证 git 是否执行任何 #!/bin/bash hook
    marker_name = "hook-executed.marker"
    trivial = (
        "#!/bin/bash\n"
        "echo TRIVIAL_HOOK_RAN >&2\n"
        f"touch '{marker_name}'\n"
        "exit 0\n"
    )
    (repo / ".git" / "hooks" / "commit-msg").write_text(trivial, encoding="utf-8")
    (repo / ".git" / "hooks" / "commit-msg").chmod(0o755)
    tres = run_cli(
        bash,
        "-c",
        f"cd {shlex.quote(str(repo))} && git commit --allow-empty -m 'trivial hook test'",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    print(f"[DIAG-g] trivial hook commit rc={tres.returncode}")
    print(f"[DIAG-g] trivial hook commit stdout={tres.stdout!r}")
    print(f"[DIAG-g] trivial hook commit stderr={tres.stderr!r}")
    print(f"[DIAG-g] marker exists={(repo / marker_name).exists()}")

    # DIAG-i: probe hook = 真实薄壳链逐段 marker，定位 git 调用下断在哪段
    probe_name = "probe-hook.marker"
    probe = (
        "#!/bin/bash\n"
        "echo PROBE0-ENTER >> 'probe-hook.marker'\n"
        "echo PROBE0-ENTER >&2\n"
        "set -u\n"
        "echo PROBE1-BASH_SOURCE=${BASH_SOURCE[0]:-$0} >> 'probe-hook.marker'\n"
        "echo PROBE1-PWD=$(pwd) >> 'probe-hook.marker'\n"
        "echo PROBE1-AGATE_ROOT=$AGATE_ROOT >> 'probe-hook.marker'\n"
        "ENTRY_ROOT=\"${AGATE_ROOT:-$(dirname \"$(dirname \"$(readlink -f \"${BASH_SOURCE[0]:-$0}\")\")\")}\"\n"
        "echo PROBE2-ENTRY_ROOT=$ENTRY_ROOT >> 'probe-hook.marker'\n"
        "if [ ! -d \"$ENTRY_ROOT/scripts\" ] "
        "&& [ -f \"$(dirname \"$(readlink -f \"${BASH_SOURCE[0]:-$0}\")\")/.agate-root\" ]; then\n"
        "  echo PROBE3-AGATEROOT-MARKER-FOUND >> 'probe-hook.marker'\n"
        "  ENTRY_ROOT=$(tr -d '\\r' < \"$(dirname \"$(readlink -f \"${BASH_SOURCE[0]:-$0}\")\")/.agate-root\")\n"
        "  echo PROBE3-ENTRY_ROOT=$ENTRY_ROOT >> 'probe-hook.marker'\n"
        "fi\n"
        "PY=\"\"\n"
        "for c in python3 python; do command -v \"$c\" >/dev/null 2>&1 && { PY=\"$c\"; break; }; done\n"
        "echo PROBE4-PY=$PY >> 'probe-hook.marker'\n"
        "echo PROBE4-LS-SCRIPTS=$(ls \"$ENTRY_ROOT/scripts\" 2>&1 | head -3) >> 'probe-hook.marker'\n"
        "if [ -n \"$PY\" ] && [ -f \"$ENTRY_ROOT/scripts/resolve-entry.py\" ]; then\n"
        "  echo PROBE5-STAGE=$(git diff --cached --name-only 2>&1 | tr '\\n' '|') >> 'probe-hook.marker'\n"
        "  echo PROBE5-EXEC >> 'probe-hook.marker'\n"
        "  \"$PY\" \"$ENTRY_ROOT/scripts/resolve-entry.py\" commit-msg \"$@\" 2>>'probe-hook.marker'\n"
        "  echo PROBE6-DONE-RC=$? >> 'probe-hook.marker'\n"
        "  exit 0\n"
        "fi\n"
        "echo PROBE7-FAILCLOSED >> 'probe-hook.marker'\n"
        "echo GATE ERROR PROBE-FAILED >&2\n"
        "exit 1\n"
    )
    (repo / ".git" / "hooks" / "commit-msg").write_text(probe, encoding="utf-8")
    (repo / ".git" / "hooks" / "commit-msg").chmod(0o755)
    (repo / probe_name).write_text("", encoding="utf-8")
    ires = run_cli(
        bash,
        "-c",
        f"cd {shlex.quote(str(repo))} && git commit --allow-empty -m 'probe hook test'",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    print(f"[DIAG-i] probe hook commit rc={ires.returncode}")
    print(f"[DIAG-i] probe hook commit stdout={ires.stdout!r}")
    print(f"[DIAG-i] probe hook commit stderr={ires.stderr!r}")
    probe_content = (repo / probe_name).read_text(encoding="utf-8") if (repo / probe_name).exists() else "<no probe>"
    print(f"[DIAG-i] probe marker content={probe_content!r}")
    # === END TEMP DIAG-f/g/h ===

    assert result.returncode == 0
    assert "self-gate-review" in result.output


def test_csg_2_trigger_no_review_warning(git_repo, agate_scripts, agate_root, run_cli, bash):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "SELF-GATE.md").write_text("# change\n", encoding="utf-8")
    git_repo.stage("SELF-GATE.md")

    result = _commit(run_cli, bash, repo, agate_root, "-m", "update self-gate")
    assert result.returncode == 0
    assert "self-gate-review" in result.output


def test_csg_3_trigger_with_review_no_warning(git_repo, agate_scripts, agate_root, run_cli, bash):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "SELF-GATE.md").write_text("# change\n", encoding="utf-8")
    git_repo.stage("SELF-GATE.md")

    result = _commit(
        run_cli,
        bash,
        repo,
        agate_root,
        "-m",
        "update self-gate",
        "-m",
        "self-gate-review: docs/reviews/agate-alignment-review-2026-07-02.md",
    )
    assert result.returncode == 0
    assert "self-gate-review" not in result.output


def test_csg_4_trigger_with_skip_no_warning(git_repo, agate_scripts, agate_root, run_cli, bash):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "SELF-GATE.md").write_text("# change\n", encoding="utf-8")
    git_repo.stage("SELF-GATE.md")

    result = _commit(run_cli, bash, repo, agate_root, "-m", "fix typo", "-m", "self-gate-skip: typo")
    assert result.returncode == 0
    assert "self-gate-review" not in result.output


def test_csg_5_scripts_sh_triggers(git_repo, agate_scripts, agate_root, run_cli, bash):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "agate" / "scripts" / "pre-commit-gate.sh").write_text("# change\n", encoding="utf-8")
    git_repo.stage("agate/scripts/pre-commit-gate.sh")

    result = _commit(run_cli, bash, repo, agate_root, "-m", "update gate script")
    assert result.returncode == 0
    assert "self-gate-review" in result.output


def test_csg_6_agate_md_triggers(git_repo, agate_scripts, agate_root, run_cli, bash):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "agate" / "WORKFLOW.md").write_text("# change\n", encoding="utf-8")
    git_repo.stage("agate/WORKFLOW.md")

    result = _commit(run_cli, bash, repo, agate_root, "-m", "update workflow")
    assert result.returncode == 0
    assert "self-gate-review" in result.output
