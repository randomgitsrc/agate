# tests/unit/test_agate_migrate_workspace.py — 工作区迁移工具单元测试
# （agate-migrate-workspace.bats 9 用例迁移，TAG0011 批次 4）
# 被测：agate/scripts/agate-migrate-workspace.py（在项目根运行；可选 --to <workspace> 覆盖目标）
# 接口契约（P2-design.md §3.2）：
#   docs/tasks → {workspace}/tasks、docs/archived → {workspace}/archived（git mv 目录级）
#   空源 no-op exit 0；迁移幂等；仓库外目标 fallback 普通 mv + WARNING
# 依赖 git_repo fixture（git-helper.bash git_init 等价）；run_cli(..., cwd=repo) 等价 bats `cd $repo`
# 流语义：MW.5 输出非空断言基于合并流 .output（bats $output = stdout + stderr，P2 BLOCKER-1）

import os
import shutil

import pytest


def _run_migrate(agate_scripts, python_exe, run_cli, repo, *args):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-migrate-workspace.py"),
        *args,
        cwd=str(repo),
    )


def _sorted_files(root):
    """find "$root" -type f | sort 等价：root 下相对路径文件列表。"""
    if not root.exists():
        return []
    return sorted(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    )


def _install_pre_commit_hook(repo, agate_scripts):
    """ln -sf pre-commit-gate.sh 装 hook（Windows 复制模式，平台无关）。"""
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    src = str(agate_scripts / "pre-commit-gate.sh")
    try:
        os.symlink(src, str(hook))
    except OSError:
        shutil.copyfile(src, str(hook))
    os.chmod(src, 0o755)


@pytest.mark.windows_smoke
def test_mw_1_bdd_6_docs_tasks_migrate_to_workspace(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "active-tasks.md").write_text("## 看板\n", encoding="utf-8")
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "# P1\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert (repo / "agate-workspace" / "tasks" / "active-tasks.md").is_file()
    assert (repo / "agate-workspace" / "tasks" / "T001" / "P1-requirements.md").is_file()
    assert not (repo / "docs" / "tasks").exists()


def test_mw_2_bdd_7_state_yaml_and_outputs_migrate_including_gitignored(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / ".gitignore").write_text("*.state.yaml\n", encoding="utf-8")
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "T001" / ".state.yaml").write_text(
        "task_id: T001\nphase: P1\nstatus: active\nretries: {}\n", encoding="utf-8"
    )
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "# P1\n", encoding="utf-8"
    )
    (repo / "docs" / "tasks" / "T001" / "P2-design.md").write_text(
        "# P2\n", encoding="utf-8"
    )
    (repo / "docs" / "tasks" / "T001" / "P7-consistency.md").write_text(
        "# P7\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    migrated = repo / "agate-workspace" / "tasks" / "T001"
    assert (migrated / ".state.yaml").is_file()
    assert (migrated / "P1-requirements.md").is_file()
    assert (migrated / "P2-design.md").is_file()
    assert (migrated / "P7-consistency.md").is_file()
    assert len(_sorted_files(migrated)) == 4


def test_mw_3_bdd_8_migration_preserves_git_history(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "unique-content-for-history\n", encoding="utf-8"
    )
    git_repo.commit("orig task file")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    log = git_repo.git(
        "log", "--follow", "--oneline", "--",
        "agate-workspace/tasks/T001/P1-requirements.md",
    ).stdout
    assert "orig task file" in log


def test_mw_4_bdd_9_migration_idempotent(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "# P1\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    before = _sorted_files(repo / "agate-workspace" / "tasks")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert _sorted_files(repo / "agate-workspace" / "tasks") == before
    assert not (repo / "docs" / "tasks").exists()


def test_mw_5_bdd_10_migration_output_explicit_guidance(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "# P1\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert result.output != ""
    assert "迁移" in result.output


def test_mw_6_bdd_18_archived_migration_preserves_structure_idempotent(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    (repo / "docs" / "archived" / "tasks" / "T009-archive").mkdir(parents=True)
    (repo / "docs" / "archived" / "tasks" / "T009-archive" / "P7-consistency.md").write_text(
        "# P7\n", encoding="utf-8"
    )
    (repo / "docs" / "archived" / "tasks" / "T009-archive" / "P8-release.md").write_text(
        "# P8\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    arch = repo / "agate-workspace" / "archived" / "tasks" / "T009-archive"
    assert (arch / "P7-consistency.md").is_file()
    assert (arch / "P8-release.md").is_file()
    assert not (repo / "docs" / "archived").exists()

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert len(_sorted_files(repo / "agate-workspace" / "archived")) == 2


def test_mw_7_bdd_19_no_docs_tasks_noop(git_repo, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    (repo / "README.md").write_text("readme\n", encoding="utf-8")
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert not (repo / "docs" / "tasks").exists()
    assert not (repo / "agate-workspace" / "tasks").is_dir()


def test_mw_8_bdd_8_external_workspace_fallback_plain_mv_warning(
    git_repo, agate_scripts, python_exe, run_cli, tmp_path
):
    repo = git_repo.path
    ext_ws = tmp_path.parent / (tmp_path.name + "-ext-ws")
    (repo / "docs" / "tasks" / "T001").mkdir(parents=True)
    (repo / "docs" / "tasks" / "T001" / "P1-requirements.md").write_text(
        "# P1\n", encoding="utf-8"
    )
    git_repo.commit("init")

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo, "--to", str(ext_ws))
    assert result.returncode == 0
    assert (ext_ws / "tasks" / "T001" / "P1-requirements.md").is_file()
    assert "WARNING" in result.output


def test_mw_9_bdd_8_auto_commit_not_blocked_by_pre_commit_hook(
    git_repo, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    task = repo / "docs" / "tasks" / "TAG0001-demo"
    task.mkdir(parents=True)
    # .state.yaml 用 v2.0 编号格式（^T[A-Z]{2}\d+$），否则 hook 的 check-state-yaml 会先拦截
    (task / ".state.yaml").write_text(
        "task_id: TAG0001\nphase: P1\nstatus: active\nretries: {}\n", encoding="utf-8"
    )
    (repo / "docs" / "tasks" / "active-tasks.md").write_text("## 看板\n", encoding="utf-8")
    (task / "P1-requirements.md").write_text("# P1\n", encoding="utf-8")
    # 旧版本 dispatch-context：内嵌卡片与当前协议不一致 → hook 卡片 hash 校验会拦截裸 commit
    (task / "P1-dispatch-context-analyst.md").write_text(
        "---\nphase: P1\n---\n"
        "<!-- AGATE_CARD_START -->\n"
        "## 旧版本 P1 卡片（非当前协议）\n"
        "该卡片内容与 agate-next-card.sh 当前输出不一致，hash 校验应失败。\n"
        "<!-- AGATE_CARD_END -->\n",
        encoding="utf-8",
    )
    git_repo.commit("init task")
    _install_pre_commit_hook(repo, agate_scripts)

    result = _run_migrate(agate_scripts, python_exe, run_cli, repo)
    assert result.returncode == 0
    assert (repo / "agate-workspace" / "tasks" / "TAG0001-demo" / "P1-requirements.md").is_file()

    log = git_repo.git("log", "--oneline").stdout
    assert "migrate legacy docs/tasks layout" in log

    status = git_repo.git("status", "--short").stdout
    assert "docs/tasks" not in status

    history = git_repo.git(
        "log", "--follow", "--oneline", "--",
        "agate-workspace/tasks/TAG0001-demo/P1-requirements.md",
    ).stdout
    assert "init task" in history
    assert "migrate legacy" in history

    # 回归守卫：hook 仍然生效——迁移后改 .state.yaml 的裸 commit 应被卡片校验拦截
    state = repo / "agate-workspace" / "tasks" / "TAG0001-demo" / ".state.yaml"
    with open(state, "a", encoding="utf-8") as fh:
        fh.write("\n# hook-liveness probe\n")
    git_repo.git("add", "-f", "agate-workspace/tasks/TAG0001-demo/.state.yaml")
    probe = git_repo.git("commit", "-qm", "hook-liveness probe")
    assert probe.returncode != 0
    git_repo.git("reset", "-q")
