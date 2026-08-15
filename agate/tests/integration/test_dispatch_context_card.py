# tests/integration/test_dispatch_context_card.py — dispatch-context 卡片 hash 校验
# （integration/dispatch-context-card.bats 8 用例迁移，TAG0011 批次 13c）
# 被测：pre-commit-gate.sh 薄壳 + pre-commit-gate.py 的 2p 节（AGATE_CARD 嵌入块
# sha256 hash 校验 + 派发阶段产出 commit 强制要求 dispatch-context 文件）。
# 任务目录在 repo 根下 `task/`（等价 bats `$REPO/task`），.state.yaml 任务级。
# 合并流：run_cli .output = stdout + stderr（等价 bats $output，P2 §3.2 BLOCKER-1）。

import os
import sys

import pytest


def _install_pre_commit_hook(repo, agate_scripts):
    """等价 bats setup()：`ln -sf pre-commit-gate.sh .git/hooks/pre-commit` + chmod +x。"""
    hook = repo / ".git" / "hooks" / "pre-commit"
    src = str(agate_scripts / "pre-commit-gate.sh")
    if sys.platform == "win32":
        import shutil

        shutil.copy2(src, str(hook))
    else:
        os.symlink(src, str(hook))
    hook.chmod(0o755)


def _git_commit(run_cli, agate_root, repo, *args):
    """等价 bats `git -C "$REPO" commit <args>`；AGATE_ROOT 经 env= 显式传入。"""
    return run_cli(
        "git",
        "-C",
        str(repo),
        "commit",
        *args,
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )


def _setup_task_with_state(repo, phase):
    """等价 bats _setup_task_with_state：task/ 下 test.py + .state.yaml（TXX0999）。"""
    task_dir = repo / "task"
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "test.py").write_text("test\n", encoding="utf-8")
    (task_dir / ".state.yaml").write_text(
        f"task_id: TXX0999\nphase: {phase}\nstatus: in_progress\nretries: {{}}\n",
        encoding="utf-8",
    )
    return task_dir


def _next_card(run_cli, python_exe, agate_scripts, agate_root, phase, out_file):
    """等价 bats `"$PYTHON" "$AGATE_SCRIPTS/agate-next-card.py" "$phase" >> "$out_file"`。"""
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-next-card.py"),
        phase,
        cwd=str(out_file.parent),
        env={"AGATE_ROOT": str(agate_root)},
    )


def _create_dispatch_context(
    run_cli, python_exe, agate_scripts, agate_root, phase, role, out_file
):
    """等价 bats _create_dispatch_context：写模板 + 嵌入真实卡片 + 占位符替换。"""
    body = (
        "---\n"
        f"phase: {phase}\n"
        "generated_by: agate-next-card.sh + 主 Agent\n"
        "task_id: TXX0999\n"
        f"role: {role}\n"
        "---\n"
        "\n"
        "<dispatch_guide>\n"
        "> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）\n"
        "\n"
        "### 目标\n"
        "测试目标描述\n"
        "\n"
        "### 约束\n"
        "测试约束\n"
        "\n"
        "### 上游关联\n"
        "上游摘要信息\n"
        "\n"
        "### 输入文件\n"
        "- agate-workspace/tasks/TXX0999/P0-brief.md\n"
        "- agate-workspace/tasks/TXX0999/前阶段产出.md\n"
        "</dispatch_guide>\n"
        "\n"
        "<!-- AGATE_CARD_START -->\n"
    )
    card = _next_card(run_cli, python_exe, agate_scripts, agate_root, phase, out_file)
    body += card.stdout.rstrip("\n") + "\n"
    body += (
        "<!-- AGATE_CARD_END -->\n"
        "\n"
        "<objective_info>\n"
        "- 环境状态：正常\n"
        "- 关键标识：无\n"
        "</objective_info>\n"
    )
    out_file.write_text(body, encoding="utf-8")


@pytest.mark.windows_smoke
def test_dc_1_valid_card_hash_not_blocked(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    """DC.1：dispatch-context 含正确卡片 hash → 不因 hash mismatch 被拦。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P3")
    dc = task_dir / "P3-dispatch-context-test-designer.md"
    _create_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, "P3", "test-designer", dc
    )
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: valid card hash")
    assert "hash mismatch" not in result.output


def test_dc_2_tampered_card_hash_mismatch(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    """DC.2：卡片被篡改 → hash mismatch 拦截。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P3")
    dc = task_dir / "P3-dispatch-context-test-designer.md"
    _create_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, "P3", "test-designer", dc
    )
    text = dc.read_text(encoding="utf-8")
    dc.write_text(
        text.replace(
            "<!-- AGATE_CARD_END -->", "_TAMPERED_\n<!-- AGATE_CARD_END -->"
        ),
        encoding="utf-8",
    )
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: tampered card")
    assert result.returncode != 0
    assert "hash mismatch" in result.output


def test_dc_3_empty_card_block_hash_mismatch(
    git_repo, agate_root, agate_scripts, run_cli
):
    """DC.3：空卡片块 → hash mismatch 拦截。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P3")
    (task_dir / "P3-dispatch-context-test-designer.md").write_text(
        "---\nphase: P3\ngenerated_by: agate-next-card.sh + 主 Agent\n"
        "task_id: TXX0999\nrole: test-designer\n---\n\n"
        "<dispatch_guide>\n### 目标\n测试\n\n### 约束\n无\n\n### 上游关联\n无\n\n"
        "### 输入文件\n- agate-workspace/tasks/TXX0999/P0-brief.md\n</dispatch_guide>\n\n"
        "<!-- AGATE_CARD_START -->\n<!-- AGATE_CARD_END -->\n\n"
        "<objective_info>\n- 环境状态：正常\n</objective_info>\n",
        encoding="utf-8",
    )
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: empty card block")
    assert result.returncode != 0
    assert "hash mismatch" in result.output


def test_dc_4_p2_missing_dispatch_context_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    """DC.4：派发阶段 P2 产出 commit 缺 dispatch-context → exit 1。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P2")
    (task_dir / "P2-design.md").write_text("# P2 design\n", encoding="utf-8")
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: missing dispatch-context in P2")
    assert result.returncode != 0
    assert "dispatch-context" in result.output


def test_dc_5_p5_missing_dispatch_context_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    """DC.5：P5 产出 commit 缺 dispatch-context → 拦截。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P5")
    results = task_dir / "P5-test-results"
    results.mkdir(parents=True, exist_ok=True)
    (results / "unit.md").write_text("results\n", encoding="utf-8")
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: no dispatch-context in P5")
    assert result.returncode != 0
    assert "dispatch-context" in result.output


def test_dc_6_p7_missing_dispatch_context_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    """DC.6：P7 产出 commit 缺 dispatch-context → 拦截。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P7")
    (task_dir / "P7-consistency.md").write_text("# P7 consistency\n", encoding="utf-8")
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: no dispatch-context in P7")
    assert result.returncode != 0
    assert "dispatch-context" in result.output


def test_dc_7_p8_missing_dispatch_context_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    """DC.7：P8 产出 commit 缺 dispatch-context → 拦截。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P8")
    (task_dir / "P8-release.md").write_text("# P8 release\n", encoding="utf-8")
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: no dispatch-context in P8")
    assert result.returncode != 0
    assert "dispatch-context" in result.output


def test_dc_multi_multiple_dispatch_context_files(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    """DC.multi：同一阶段多个 dispatch-context 文件 → 逐个校验 hash。"""
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    task_dir = _setup_task_with_state(repo, "P1")
    _create_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, "P1", "analyst",
        task_dir / "P1-dispatch-context-analyst.md",
    )
    _create_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, "P1", "requirements-review",
        task_dir / "P1-dispatch-context-requirements-review.md",
    )
    git_repo.stage("task/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "test: multiple dispatch-context files")
    assert "hash mismatch" not in result.output
