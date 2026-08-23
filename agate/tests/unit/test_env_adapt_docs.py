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
from pathlib import Path

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


def test_bdd_25_consistency_zero_error(
    agate_scripts, agate_root, python_exe, run_cli, tmp_path_factory
):
    """bdd-25：修复后协议一致性检查 0 ERROR（worktree 自己的脚本，Q2）。

    等价 bats `run $PYTHON "$(py_path "$AGATE_ROOT/scripts/check-protocol-consistency.py")"`
    （bats 以仓库根为 cwd 默认 `--root .`）；pytest 用 `--root agate_root.parent` 显式指定，
    行为等价（批次 14 test_consistency 同口径）。exit 0 = 无 ERROR。

    TAG0022 RM-AG0041（P2 §4.5.2 + [SCOPE+] M15）：basetemp 位于仓库根下时注入
    `AGATE_CONSISTENCY_SKIP_DIRS=<basetemp 相对根 rel 路径>`，使 iter_md_files 免疫
    basetemp 污染（TAG0020 known-failures 条目 2：预存测试生成的坏引用 fixture .md 被
    CHECK 2 误收）；basetemp 在仓库外时不注入（行为与基线一致，零改动）。
    两种位置断言口径：仓库内=注入后 0 ERROR（P3 现状 M15 未实现 → env 无效果 → 红）；
    仓库外=不注入 0 ERROR（P3 现状即绿）。
    """
    repo_root = agate_root.parent
    basetemp = Path(tmp_path_factory.getbasetemp())
    env = None
    try:
        rel_bt = Path(basetemp).relative_to(repo_root)
        env = {"AGATE_CONSISTENCY_SKIP_DIRS": rel_bt.as_posix()}
    except ValueError:
        env = None  # basetemp 在仓库外 → 不注入（基线行为）

    kwargs = {}
    if env is not None:
        kwargs["env"] = env
    result = run_cli(
        python_exe,
        str(agate_scripts / "check-protocol-consistency.py"),
        "--root",
        str(repo_root),
        **kwargs,
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


# ─────────────────────────────────────────────
# TAG0022 增补：M15 排除钩子单测（RM-AG0041 [SCOPE+] / BDD-9，TG-3；P2 §4.5.2 + §8 minimal_validation）
#   被测：agate/scripts/check-protocol-consistency.py iter_md_files 的 opt-in 排除钩子
#   （env AGATE_CONSISTENCY_SKIP_DIRS=<相对根路径列表>，默认关闭、行为逐字节不变）。
#   P3 现状 M15 未实现 → env 无效果 → 排除断言失败（红，B 类）；默认行为用例现即绿（回归守卫）。
#   平台无关：无裸 python3 / 无 /tmp 字面（用 tmp_path）/ 无软链假设；rel 路径经 Path.relative_to
#   + as_posix 归一（与 iter_md_files 既有 rel 处理一致，Windows 反斜杠归一）。


def _load_protocol_consistency_mod(agate_scripts, suffix):
    """importlib 加载 check-protocol-consistency.py（__name__ ≠ __main__ → main 不跑）。

    每次测试用唯一模块名加载（env 在 exec_module 前由 monkeypatch 设置）——
    对「import-time 读 env」或「call-time 读 env」两种 M15 实现方式均能正确捕获。
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "agate_consistency_" + suffix,
        str(agate_scripts / "check-protocol-consistency.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_root_with_skip(tmp_path):
    """含被排除目录的最小根：a.md + sub/b.md + skip-dir/c.md（c.md 是排除对象）。"""
    root = tmp_path / "fake-root"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.md").write_text("a", encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "b.md").write_text("b", encoding="utf-8")
    (root / "skip-dir").mkdir()
    (root / "skip-dir" / "c.md").write_text("c", encoding="utf-8")
    return root


def test_m15_iter_md_files_skip_dirs_injected_excluded(tmp_path, agate_scripts, monkeypatch):
    """M15（TG-3）：注入 AGATE_CONSISTENCY_SKIP_DIRS 后 iter_md_files 不产出被排除路径。
    TDD：P3 现状 M15 未实现 → env 无效果 → skip-dir/c.md 仍产出 → 断言失败（红，B 类）。"""
    monkeypatch.setenv("AGATE_CONSISTENCY_SKIP_DIRS", "skip-dir")
    mod = _load_protocol_consistency_mod(agate_scripts, "injected")
    root = _fake_root_with_skip(tmp_path)
    got = {str(p.relative_to(root)) for p in mod.iter_md_files(root)}
    assert "skip-dir/c.md" not in got, f"M15 未生效：被排除路径仍产出 {sorted(got)}"
    assert "a.md" in got and "sub/b.md" in got


@pytest.mark.windows_smoke
def test_m15_iter_md_files_default_unchanged(tmp_path, agate_scripts, monkeypatch):
    """M15（TG-3）：默认未设置 AGATE_CONSISTENCY_SKIP_DIRS 时行为不变（扫面变化可观测）——
    iter_md_files 产出全部 .md（无排除）。回归守卫：P3 现状即绿；P4 实现后（默认关闭）仍绿。"""
    monkeypatch.delenv("AGATE_CONSISTENCY_SKIP_DIRS", raising=False)
    mod = _load_protocol_consistency_mod(agate_scripts, "default")
    root = _fake_root_with_skip(tmp_path)
    got = sorted(str(p.relative_to(root)) for p in mod.iter_md_files(root))
    assert got == ["a.md", "skip-dir/c.md", "sub/b.md"]
