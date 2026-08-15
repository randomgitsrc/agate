# tests/integration/test_pre_commit_hook.py — pre-commit hook 集成测试
# （integration/pre-commit-hook.bats 迁移，TAG0011 批次 13a 子批）
# 本子批覆盖前 12 个 @test：IT_PT_BINARY.1-7 / IT_PT_MENTION.1 / IT_PT_T6.1-4；
# 后续子批 13b（IT_PHASE_SPAN / IT_RETREAT / IT.9 / IT_CHANGELOG / IT_P6_CODE）、
# 13c（其余）在此文件追加。
# 被测：pre-commit-gate.sh 薄壳 + pre-commit-gate.py 真 hook 行为（BDD-11）——
# git commit 经 .git/hooks/pre-commit 软链触发（等价 bats setup `ln -sf`）。
# 合并流：run_cli .output = stdout + stderr（等价 bats $output，P2 §3.2 BLOCKER-1）。

import os
import shutil
import sys


def _install_pre_commit_hook(repo, agate_scripts):
    """等价 bats setup()：`ln -sf pre-commit-gate.sh .git/hooks/pre-commit` + chmod +x。

    Linux 用 POSIX 软链（bats ln 语义）；Windows（Git Bash ln 退化为复制）复制薄壳，
    AGATE_ROOT 由 _git_commit env= 显式传入（P3 §5.2 平台分支纪律）。13a 用例不打
    windows_smoke 标（无平台关键词用例且非文件首 @test），软链语义由 Linux 全量覆盖。
    """
    hook = repo / ".git" / "hooks" / "pre-commit"
    src = str(agate_scripts / "pre-commit-gate.sh")
    if sys.platform == "win32":
        shutil.copy2(src, str(hook))
    else:
        os.symlink(src, str(hook))
    hook.chmod(0o755)


def _git_commit(run_cli, agate_root, repo, *args):
    """等价 bats `git -C "$REPO" commit <args>`；AGATE_ROOT 经 env= 显式传入
    （bats 由 load.bash export 继承给 git → hook，pytest 用 run_cli env= 承接）。"""
    return run_cli(
        "git",
        "-C",
        str(repo),
        "commit",
        *args,
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )


def _init_commit(run_cli, agate_root, git_repo, repo):
    """等价 bats `echo init > README.md; git add README.md; git commit -qm "init"`。"""
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.stage("README.md")
    return _git_commit(run_cli, agate_root, repo, "-q", "-m", "init")


def _write_state_yaml(task_dir, task_id, phase):
    """等价 bats `cat > task_dir/.state.yaml` heredoc（retries 空表）。"""
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / ".state.yaml").write_text(
        f"task_id: {task_id}\nphase: {phase}\nstatus: active\nretries: {{}}\n",
        encoding="utf-8",
    )


def _write_min_valid_dispatch_context(
    run_cli, python_exe, agate_scripts, agate_root, task_dir, phase, role
):
    """等价 bats _write_min_valid_dispatch_context：写 dispatch-context + 注入 AGATE_CARD。

    卡片内容 = agate-next-card.py phase 输出（hook 用 sha256 校验嵌入块是当前版本），
    注入于 AGATE_CARD_START/END 之间（T6.1 验证卡片说明文本不触发 PROD_TOUCHED 误报）。
    """
    card = run_cli(
        python_exe,
        str(agate_scripts / "agate-next-card.py"),
        phase,
        cwd=str(task_dir),
        env={"AGATE_ROOT": str(agate_root)},
    )
    body = (
        "---\n"
        f"phase: {phase}\n"
        "generated_by: agate-next-card.sh + 主 Agent\n"
        "task_id: T001\n"
        f"role: {role}\n"
        "---\n"
        "\n"
        "<dispatch_guide>\n"
        "### 目标\n"
        "测试\n"
        "\n"
        "### 约束\n"
        "无\n"
        "\n"
        "### 上游关联\n"
        "无\n"
        "\n"
        "### 输入文件\n"
        "- agate-workspace/tasks/T001/P0-brief.md\n"
        "</dispatch_guide>\n"
        "\n"
        "<!-- AGATE_CARD_START -->\n"
        + card.stdout.rstrip("\n")
        + "\n"
        "<!-- AGATE_CARD_END -->\n"
        "\n"
        "<objective_info>\n"
        "- 环境状态：正常\n"
        "</objective_info>\n"
    )
    target = task_dir / f"{phase}-dispatch-context-{role}.md"
    target.write_text(body, encoding="utf-8")


def test_pt_binary_1_line_start_prod_touched_blocks(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "[PROD_TOUCHED] 接触了生产环境：修改了线上配置\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should fail")
    assert result.returncode != 0
    assert "PROD_TOUCHED" in result.output


def test_pt_binary_2_prod_not_touched_passes(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text("[PROD_NOT_TOUCHED]\n", encoding="utf-8")
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should pass")
    assert result.returncode == 0


def test_pt_binary_3_deleted_line_not_scanned(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "[PROD_TOUCHED] 旧内容\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "T001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    _git_commit(
        run_cli,
        agate_root,
        repo,
        "--no-verify",
        "-q",
        "-m",
        "setup with PROD_TOUCHED",
    )

    (task_dir / "P5-verification.md").write_text("clean content\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "remove PROD_TOUCHED")
    assert result.returncode == 0


def test_pt_binary_4_inline_mention_passes(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "无 [PROD_TOUCHED] 需要报告\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should pass")
    assert result.returncode == 0


def test_pt_binary_5_inline_mention_passes_variant(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "检查了 [PROD_TOUCHED] 标记\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should pass")
    assert result.returncode == 0


def test_pt_binary_6_no_marker_no_warning(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "normal content without any marker\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should pass")
    assert result.returncode == 0
    assert "WARNING" not in result.output


def test_pt_binary_7_prod_not_touched_with_desc_passes(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "[PROD_NOT_TOUCHED] 确认未接触\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should pass")
    assert result.returncode == 0


def test_pt_mention_1_body_mention_not_declaration(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "P5-verification.md").write_text(
        "说明：本任务无生产接触，不需要写 [PROD_TOUCHED] 声明\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/P5-verification.md")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")

    result = _git_commit(run_cli, agate_root, repo, "-m", "mention not declaration")
    assert result.returncode == 0


def test_t6_1_p8_card_injection_no_false_flag(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P8", "releaser"
    )
    _write_state_yaml(task_dir, "T001", "P8")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _git_commit(run_cli, agate_root, repo, "-m", "p8 dispatch-context with AGATE_CARD")
    assert "不合规的 PROD_TOUCHED" not in result.output
    assert "检测到生产环境接触" not in result.output


def test_t6_2_note_inline_mention_passes(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "note.md").write_text(
        "记录：曾经不小心碰到了 [PROD_TOUCHED] 生产环境\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _git_commit(run_cli, agate_root, repo, "-m", "mention not declaration")
    assert result.returncode == 0


def test_t6_3_note_line_start_declaration_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "note.md").write_text(
        "[PROD_TOUCHED] 意外接触生产环境\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "TXX0001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _git_commit(run_cli, agate_root, repo, "-m", "should be blocked")
    assert result.returncode != 0
    assert "检测到生产环境接触" in result.output


def test_t6_4_note_prod_not_touched_passes(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    (task_dir / "note.md").write_text(
        "[PROD_NOT_TOUCHED] 未接触生产环境\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "T001", "P5")
    git_repo.stage("agate-workspace/tasks/T001/")

    result = _git_commit(
        run_cli, agate_root, repo, "-m", "should not be blocked by PROD_TOUCHED check"
    )
    assert "不合规的 PROD_TOUCHED" not in result.output
    assert "检测到生产环境接触" not in result.output
