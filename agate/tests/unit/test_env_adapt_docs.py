# tests/unit/test_env_adapt_docs.py — 文档/CI/全局层 BDD 断言
# （unit/env-adapt-docs.bats 9 用例迁移，TAG0011 批次 15）
# Q2（BDD-23/24/25）、Q5（BDD-26/27）、CI（BDD-33）、shellcheck（BDD-34）、M6 .gitattributes（BDD-16）。
# 断言目标随 pytest 化更新（P2 §5 批次 15 / P3 §5 批次 15，非新增断言，目标迁移）：
#   * bdd-32「bats 可解析」→「pytest 可收集（--collect-only 全绿）」
#   * bdd-34 ruff 目标 `agate/scripts/` → `agate/`（含 tests，BDD-3）
#   * bdd-33 windows-latest matrix 保留；bdd-16/23/24/25/26/27 不变
# 读文件断言按 P2 §3.2「run grep -q ...」映射（read_text + substring/正则）。
# windows_smoke：bdd-23（文件首 @test，P3 §5.2 每文件第 1 用例）+ bdd-16（CRLF 平台关键词）+
#   bdd-26（Windows）+ bdd-33（Windows）——共 4 处（P3 §5.2 表「3 处平台关键词」+ 首用例规则）。

import re
import shutil

import pytest

_PHASE_CARDS = [
    "P1-requirements",
    "P2-design",
    "P3-tdd",
    "P4-implementation",
    "P6-acceptance",
    "P7-consistency",
    "P8-release",
]


@pytest.mark.windows_smoke
def test_bdd_23_phase_cards_no_mode_b_write(agate_root):
    """bdd-23：7 张阶段卡片与 git-integration.md 规则 2 对齐（无 mode B 旧写法，Q2）。

    等价 bats：`grep -q '更新 .state.yaml phase='` 对每张卡片应无命中。
    """
    for card in _PHASE_CARDS:
        text = (agate_root / "phase-cards" / f"{card}.md").read_text(encoding="utf-8")
        assert "更新 .state.yaml phase=" not in text, (
            f"FAIL: {card}.md 残留 mode B 旧写法（先更新 phase=N→N+1 再 commit）"
        )


def test_bdd_24_git_integration_rule2_semantics(agate_root):
    """bdd-24：git-integration.md 规则 2 语义不变（commit 顺序/gate 判定逻辑无改动，Q2）。"""
    text = (agate_root / "git-integration.md").read_text(encoding="utf-8")
    assert "不得提前写下一阶段" in text


def test_bdd_25_consistency_zero_error(agate_scripts, agate_root, python_exe, run_cli):
    """bdd-25：修复后协议一致性检查 0 ERROR（worktree 自己的脚本，Q2）。

    等价 bats `run $PYTHON "$(py_path "$AGATE_ROOT/scripts/check-protocol-consistency.py")"`
    （bats 以仓库根为 cwd 默认 `--root .`）；pytest 用 `--root agate_root.parent` 显式指定，
    行为等价（批次 14 test_consistency 同口径）。exit 0 = 无 ERROR。
    """
    result = run_cli(
        python_exe,
        str(agate_scripts / "check-protocol-consistency.py"),
        "--root",
        str(agate_root.parent),
    )
    assert result.returncode == 0, result.output


def test_bdd_16_gitattributes_no_md_eol_rule(agate_root):
    """bdd-16：.gitattributes 不含强制 *.md eol 规则（历史 CRLF review 文件不被改写，M6）。"""
    ga = agate_root.parent / ".gitattributes"
    assert ga.is_file()
    matched = [
        line
        for line in ga.read_text(encoding="utf-8").splitlines()
        if re.search(r"^\s*[*]*\.md\s", line)
    ]
    assert not matched, f"FAIL: .gitattributes 含强制 *.md eol 规则: {matched}"


@pytest.mark.windows_smoke
def test_bdd_26_setup_has_windows_pythonutf8(agate_root):
    """bdd-26：SETUP.md 含 Windows 章节覆盖 PYTHONUTF8（Q5）。"""
    text = (agate_root / "SETUP.md").read_text(encoding="utf-8")
    assert "PYTHONUTF8" in text


def test_bdd_27_gitignore_version_txt_dist(agate_root):
    """bdd-27：仓库 .gitignore 模板预设 version.txt/dist 白名单（Q5）。"""
    gitignore = agate_root.parent / ".gitignore"
    assert gitignore.is_file()
    text = gitignore.read_text(encoding="utf-8")
    assert re.search(r"version\.txt|dist/", text) is not None


@pytest.mark.windows_smoke
def test_bdd_33_ci_windows_latest_matrix(agate_root):
    """bdd-33：protocol-tests.yml 含 windows-latest matrix（Windows 唯一兜底验证，保留）。"""
    wf = agate_root.parent / ".github" / "workflows" / "protocol-tests.yml"
    assert wf.is_file()
    text = wf.read_text(encoding="utf-8")
    assert "windows-latest" in text


def test_bdd_34_shellcheck_three_hook_shells_and_ruff(agate_root, agate_scripts, run_cli):
    """bdd-34：shellcheck 3 hook 薄壳 0 error + ruff check agate/ 0 error（含 tests，BDD-3）。

    断言目标随 pytest 化更新：ruff 从 `agate/scripts/` 扩展到 `agate/`（P2 §5 批次 15）。
    等价 bats：shellcheck 与 ruff 均未安装时 skip（由独立 CI lint job 覆盖）。
    """
    shellcheck = shutil.which("shellcheck") or shutil.which("shellcheck.exe")
    ruff = shutil.which("ruff")
    if not shellcheck and not ruff:
        pytest.skip("shellcheck 与 ruff 均未安装（由独立 CI lint job 覆盖）")

    if shellcheck:
        result = run_cli(
            shellcheck,
            "-S",
            "warning",
            "pre-commit-gate.sh",
            "commit-msg-self-gate.sh",
            "pre-push-gate.sh",
            cwd=str(agate_scripts),
        )
        assert result.returncode == 0, result.output

    if ruff:
        result = run_cli(ruff, "check", str(agate_root), cwd=str(agate_root.parent))
        assert result.returncode == 0, result.output


def test_bdd_32_pytest_collectible(agate_root, python_exe, run_cli):
    """bdd-32：全量 pytest 测试文件可被收集（--collect-only 全绿，P5 全量回归前提）。

    断言目标从 bats「可解析」迁移为 pytest「可收集」：`pytest --collect-only` 对
    agate/tests/ 全树 exit 0 = 所有 test_*.py 收集无错误（P3 §5 批次 15）。
    """
    result = run_cli(
        python_exe,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        str(agate_root / "tests"),
    )
    assert result.returncode == 0, result.output
