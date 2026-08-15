# tests/integration/test_pre_commit_hook.py — pre-commit hook 集成测试
# （integration/pre-commit-hook.bats 迁移，TAG0011 批次 13a / 13b 子批）
# 13a 覆盖 IT_PT_BINARY.1-7 / IT_PT_MENTION.1 / IT_PT_T6.1-4（12 个）；
# 13b 追加 IT_PHASE_SPAN.1-5 / IT_P6_CODE.1-5 / IT_RETREAT.1-2 /
#      IT_CHANGELOG_P54/P54b / IT.9 / IT.9b（17 个）；
# 后续子批 13c（其余）在此文件追加。
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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
    task_dir.mkdir(parents=True, exist_ok=True)
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


# ============================================================
# TAG0011 批次 13b：IT_PHASE_SPAN / IT_P6_CODE / IT_RETREAT /
# IT_CHANGELOG / IT.9 系列（中段 @test，pre-commit-hook.bats 迁移）
# ============================================================


def _in_order(text, *parts):
    """bats `[[ "$output" == *"A"*"B"* ]]` 复合 glob 等价：parts 按顺序出现。"""
    pos = 0
    for part in parts:
        idx = text.find(part, pos)
        if idx == -1:
            return False
        pos = idx + len(part)
    return True


_P1_REQ = (
    "---\nagent: test\n---\n"
    "risk_level: medium\n"
    "phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]\n"
    "- Given test precondition\n"
)


def _write_p1_requirements(task_dir):
    (task_dir / "P1-requirements.md").write_text(_P1_REQ, encoding="utf-8")


def test_phase_span_1_late_p1_p2_outputs_no_warning(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "T001", "P3")
    (task_dir / "P3-test-cases.md").write_text("## P3 test cases\n", encoding="utf-8")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P3", "test-designer"
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T001 P3 setup")

    _write_p1_requirements(task_dir)
    (task_dir / "P2-design.md").write_text(
        "---\nagent: test\nphase: P2\ntask_id: T001\ntype: design\n"
        "parent: P1-requirements.md\ntrace_id: T001-P2-20260708\n"
        "status: approved\ncreated: 2026-07-08\n---\n"
        "### 候选方案 A：方案一\n",
        encoding="utf-8",
    )
    git_repo.stage("agate-workspace/tasks/T001/P1-requirements.md")
    git_repo.stage("agate-workspace/tasks/T001/P2-design.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 late commit P1/P2 outputs")
    assert result.returncode == 0
    assert not _in_order(result.output, "WARNING", "P1")
    assert not _in_order(result.output, "WARNING", "P2")


def test_phase_span_2_existing_p1_restaged_warns(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "T001", "P1")
    _write_p1_requirements(task_dir)
    git_repo.stage("agate-workspace/tasks/T001/")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T001 P1 setup")

    _write_state_yaml(task_dir, "T001", "P3")
    (task_dir / "P3-test-cases.md").write_text("## P3 test cases\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    git_repo.stage("agate-workspace/tasks/T001/P3-test-cases.md")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T001 P3 setup")

    with open(task_dir / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write("updated requirements\n")
    git_repo.stage("agate-workspace/tasks/T001/P1-requirements.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 modify P1 while phase=P3")
    assert result.returncode == 0
    assert _in_order(result.output, "WARNING", "P1")


def test_phase_span_3_new_p4_output_early_warns(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "T001", "P3")
    _write_p1_requirements(task_dir)
    git_repo.stage("agate-workspace/tasks/T001/")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T001 P3 setup")

    (task_dir / "P4-implementation.md").write_text("implementation\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T001/P4-implementation.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 P4 output while phase=P3")
    assert result.returncode == 0
    assert _in_order(result.output, "WARNING", "P4")


def test_phase_span_4_multi_task_warn_selective(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    # T001: phase=P3, 历史产出晚提交（P1/P2/P3/P1-review 全新增）→ 不 WARNING
    t1 = repo / "agate-workspace" / "tasks" / "T001"
    t1.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(t1, "T001", "P3")
    _write_p1_requirements(t1)
    (t1 / "P2-design.md").write_text(
        "---\nagent: test\nphase: P2\ntask_id: T001\ntype: design\n"
        "parent: P1-requirements.md\ntrace_id: T001-P2-20260708\n"
        "status: approved\ncreated: 2026-07-08\n---\n"
        "### 候选方案 A：方案一\n",
        encoding="utf-8",
    )
    (t1 / "P3-test-cases.md").write_text(
        "---\nagent: test\n---\ntest cases\n", encoding="utf-8"
    )
    (t1 / "P1-review.md").write_text(
        "---\nphase: P1\ntask_id: T001\nstatus: approved\nagent: requirements-review\n---\n"
        "## BDD 评审\n- BDD-1: PASS + 覆盖维度：数据✓\n",
        encoding="utf-8",
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, t1, "P3", "test-designer"
    )
    git_repo.stage("agate-workspace/tasks/T001/P3-dispatch-context-test-designer.md")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T001 P3 setup")

    # T002: phase=P3, 已存在 P1 产出被修改 → WARNING
    t2 = repo / "agate-workspace" / "tasks" / "T002"
    t2.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(t2, "T002", "P1")
    _write_p1_requirements(t2)
    git_repo.stage("agate-workspace/tasks/T002/")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T002 P1 setup")
    _write_state_yaml(t2, "T002", "P3")
    (t2 / "P3-test-cases.md").write_text("## P3 test cases\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T002/.state.yaml")
    git_repo.stage("agate-workspace/tasks/T002/P3-test-cases.md")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T002 P3 setup")
    with open(t2 / "P1-requirements.md", "a", encoding="utf-8") as fh:
        fh.write("updated\n")

    # T003: phase=P3, 新增 P4 产出（提前产出）→ WARNING
    t3 = repo / "agate-workspace" / "tasks" / "T003"
    t3.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(t3, "T003", "P3")
    _write_p1_requirements(t3)
    (t3 / "P3-test-cases.md").write_text("## P3 test cases\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T003/")
    _git_commit(run_cli, agate_root, repo, "--no-verify", "-q", "-m", "T003 P3 setup")
    (t3 / "P4-implementation.md").write_text("implementation\n", encoding="utf-8")

    git_repo.stage("agate-workspace/tasks/T002/P1-requirements.md")
    git_repo.stage("agate-workspace/tasks/T003/P4-implementation.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "multi-task phase-span")
    assert result.returncode == 0
    assert not _in_order(result.output, "WARNING", "T001", "P1")
    assert _in_order(result.output, "WARNING", "P1")
    assert _in_order(result.output, "WARNING", "P4")


def test_phase_span_5_paused_phase_no_crash(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "TXX0001", "PAUSED")
    _write_p1_requirements(task_dir)
    git_repo.stage("agate-workspace/tasks/T001/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 PAUSED with P1 output")
    assert result.returncode == 0
    assert "integer expression expected" not in result.output


def test_p6_code_1_p6_evidence_dir_allowed(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    screenshots = task_dir / "P6-evidence" / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    (screenshots / "a.png").touch()
    (task_dir / "P6-acceptance.md").write_text(
        "- PASS BDD-1: ok (screenshots/a.png)\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "T001", "P6")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P6", "verifier"
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "p6 evidence only")
    assert "暂存了项目源码" not in result.output
    assert "不应直接改代码" not in result.output


def test_p6_code_1b_evidences_dir_allowed(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    evidences = task_dir / "evidences"
    evidences.mkdir(parents=True, exist_ok=True)
    (evidences / "desktop.png").touch()
    (task_dir / "P6-acceptance.md").write_text(
        "- PASS BDD-1: ok (screenshots/a.png)\n", encoding="utf-8"
    )
    _write_state_yaml(task_dir, "T001", "P6")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P6", "verifier"
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "evidences dir only")
    assert "暂存了项目源码" not in result.output
    assert "不应直接改代码" not in result.output


def test_p6_code_2_p6_source_blocked(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    screenshots = task_dir / "P6-evidence" / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    (screenshots / "a.png").touch()
    (task_dir / "P6-acceptance.md").write_text(
        "- PASS BDD-1: ok (screenshots/a.png)\n", encoding="utf-8"
    )
    src = repo / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print('fix')\n", encoding="utf-8")
    _write_state_yaml(task_dir, "TXX0001", "P6")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P6", "verifier"
    )
    git_repo.stage("src/app.py")
    git_repo.stage("agate-workspace/tasks/T001/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "should be blocked")
    assert result.returncode != 0
    assert "不应直接改代码" in result.output


def test_p6_code_3_p4_source_allowed(git_repo, agate_root, agate_scripts, run_cli):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    src = repo / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print('impl')\n", encoding="utf-8")
    _write_state_yaml(task_dir, "T001", "P4")
    git_repo.stage("src/app.py")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    result = _git_commit(run_cli, agate_root, repo, "-m", "p4 impl")
    assert "不应直接改代码" not in result.output


def test_p6_code_4_p5_source_allowed(git_repo, agate_root, agate_scripts, run_cli):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    src = repo / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print('fix')\n", encoding="utf-8")
    _write_state_yaml(task_dir, "T001", "P5")
    git_repo.stage("src/app.py")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    result = _git_commit(run_cli, agate_root, repo, "-m", "p5 fix")
    assert "不应直接改代码" not in result.output


def test_p6_code_5_p2_source_warns_not_blocked(
    git_repo, agate_root, agate_scripts, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    src = repo / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print('early')\n", encoding="utf-8")
    _write_state_yaml(task_dir, "TXX0001", "P2")
    git_repo.stage("src/app.py")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    result = _git_commit(run_cli, agate_root, repo, "-m", "p2 early code")
    assert "是否在非实现阶段直接改代码" in result.output
    assert "不应直接改代码" not in result.output


def _retreat_setup(git_repo, agate_root, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    screenshots = task_dir / "P6-evidence" / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    (task_dir / "P6-acceptance.md").write_text(
        "- PASS BDD-1: ok (screenshots/x.png)\n", encoding="utf-8"
    )
    (screenshots / "x.png").touch()
    _write_state_yaml(task_dir, "TXX0001", "P6")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P6", "verifier"
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    _git_commit(run_cli, agate_root, repo, "-q", "-m", "setup P6 state")
    return repo, task_dir


def test_retreat_1_real_hook_each_step(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo, _task_dir = _retreat_setup(
        git_repo, agate_root, agate_scripts, python_exe, run_cli
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-retreat-to.py"),
        "agate-workspace/tasks/T001",
        "P4",
        "集成测试诊断",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    assert result.returncode == 0
    assert "共 2 步" in result.output
    log = git_repo.git("log", "--oneline").stdout
    assert "retreat: P6 -> P5" in log
    assert "retreat: P5 -> P4" in log


def test_retreat_2_midway_hook_rejected(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo, task_dir = _retreat_setup(
        git_repo, agate_root, agate_scripts, python_exe, run_cli
    )
    (task_dir / "note.md").write_text(
        "[PROD_TOUCHED] 意外接触了生产环境\n", encoding="utf-8"
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-retreat-to.py"),
        "agate-workspace/tasks/T001",
        "P4",
        "集成测试：中途拒绝",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    assert result.returncode == 1
    assert "未通过 pre-commit hook 校验" in result.output
    assert "已停在 P6" in result.output
    log = git_repo.git("log", "--oneline").stdout
    assert "retreat:" not in log


def test_changelog_1_p4_no_changelog_warning(git_repo, agate_root, agate_scripts, run_cli):
    repo = git_repo.path
    git_repo.git("commit", "-q", "--allow-empty", "-m", "init")
    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "T001", "P4")
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Fixed\n- T999: other task\n",
        encoding="utf-8",
    )
    (task_dir / "P0-brief.md").write_text("task: test\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    git_repo.stage("agate-workspace/tasks/T001/P0-brief.md")
    result = run_cli(
        "bash",
        str(agate_scripts / "pre-commit-gate.sh"),
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    assert "CHANGELOG" not in result.output


def test_changelog_2_p8_changelog_warning(git_repo, agate_root, agate_scripts, run_cli):
    repo = git_repo.path
    git_repo.git("commit", "-q", "--allow-empty", "-m", "init")
    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "TXX0001", "P8")
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Fixed\n- T999: other task\n",
        encoding="utf-8",
    )
    (task_dir / "P0-brief.md").write_text("task: test\n", encoding="utf-8")
    git_repo.stage("agate-workspace/tasks/T001/.state.yaml")
    git_repo.stage("agate-workspace/tasks/T001/P0-brief.md")
    result = run_cli(
        "bash",
        str(agate_scripts / "pre-commit-gate.sh"),
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
    assert "CHANGELOG" in result.output


def test_it9_pruning_skip_low_passes(git_repo, agate_root, agate_scripts, python_exe, run_cli):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "TXX0001", "P2")
    (task_dir / "P1-requirements.md").write_text(
        "---\nagent: test\n---\nrisk_level: low\n"
        "phases: [P0, P1, P2, P4, P5, P6, P7, P8]\n跳过风险: 低\n",
        encoding="utf-8",
    )
    (task_dir / "P2-design.md").write_text(
        "---\nagent: test\nphase: P2\ntask_id: TXX0001\ntype: design\n"
        "parent: P1-requirements.md\ntrace_id: T001-P2-20260708\n"
        "status: approved\ncreated: 2026-07-08\n---\n"
        "### 候选方案 A：方案一\n### 候选方案 B：方案二\n## 权衡\nA 简单 B 稳健\n"
        "candidate_count: 2\npackages: [pkg-a]\ndomains: [backend]\n"
        "ui_affected: false\ngate_commands: {}\n",
        encoding="utf-8",
    )
    (task_dir / "P2-review.md").write_text(
        "---\nstatus: approved\nagent: reviewer-subagent\n---\nP2 review approved.\n",
        encoding="utf-8",
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P2", "architect"
    )
    git_repo.stage("agate-workspace/tasks/T001/P2-dispatch-context-architect.md")
    _git_commit(run_cli, agate_root, repo, "-q", "-m", "T001 P2")

    _write_state_yaml(task_dir, "TXX0001", "P5")
    (task_dir / "P5-verification.md").write_text(
        "---\nagent: test\n---\n", encoding="utf-8"
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 skip to P5")
    assert result.returncode == 0


def test_it9b_pruning_skip_medium_blocked(
    git_repo, agate_root, agate_scripts, python_exe, run_cli
):
    repo = git_repo.path
    _install_pre_commit_hook(repo, agate_scripts)
    _init_commit(run_cli, agate_root, git_repo, repo)

    task_dir = repo / "agate-workspace" / "tasks" / "T001"
    task_dir.mkdir(parents=True, exist_ok=True)
    _write_state_yaml(task_dir, "TXX0001", "P2")
    (task_dir / "P1-requirements.md").write_text(
        "---\nagent: test\n---\nrisk_level: medium\n"
        "phases: [P0, P1, P2, P4, P5, P6, P7, P8]\n跳过风险: 低\n",
        encoding="utf-8",
    )
    (task_dir / "P2-design.md").write_text(
        "---\nagent: test\nphase: P2\ntask_id: TXX0001\ntype: design\n"
        "parent: P1-requirements.md\ntrace_id: T001-P2-20260708\n"
        "status: approved\ncreated: 2026-07-08\n---\n"
        "### 候选方案 A：方案一\n### 候选方案 B：方案二\n## 权衡\nA 简单 B 稳健\n"
        "candidate_count: 2\npackages: [pkg-a]\ndomains: [backend]\n"
        "ui_affected: false\ngate_commands: {}\n",
        encoding="utf-8",
    )
    (task_dir / "P2-review.md").write_text(
        "---\nstatus: approved\nagent: reviewer-subagent\n---\nP2 review approved.\n",
        encoding="utf-8",
    )
    git_repo.stage("agate-workspace/tasks/T001/")
    _write_min_valid_dispatch_context(
        run_cli, python_exe, agate_scripts, agate_root, task_dir, "P2", "architect"
    )
    git_repo.stage("agate-workspace/tasks/T001/P2-dispatch-context-architect.md")
    result = _git_commit(run_cli, agate_root, repo, "-m", "T001 P2 medium skip P3")
    assert result.returncode != 0
    assert _in_order(result.output, "P3 不可裁剪", "仅 low")
