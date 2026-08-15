# tests/unit/test_agate_next_card.py — agate-next-card.py CLI 防漂移 byte-stability 硬保证
# （agate-next-card.bats 22 用例迁移，TAG0011 批次 3）
# 被测：agate/scripts/agate-next-card.py（CLI 输出去掉固定 4 行头后 sha256 必须等于
#       phase-cards/{PHASE}-*.md 的 sha256——step 3 hook 嵌入 dispatch-context 卡片的前提）
# 精确等值注意（P2 §3.2）：$(...) 剥尾部换行 vs subprocess 保留——输出按行保留字节后
#       再 sha256（splitlines(keepends=True) 逐字节保留，等价 tail -n +5 | sha256sum）
# 平台分支：Windows 上 ln -sf 退化为复制（AGENTS.md 测试约定），symlink 用例按平台构造

import hashlib
import os
import shutil

import pytest

_PHASE_CARD_FILES = {
    "P0": "P0-orchestrator.md",
    "P1": "P1-requirements.md",
    "P2": "P2-design.md",
    "P3": "P3-tdd.md",
    "P4": "P4-implementation.md",
    "P5": "P5-verification.md",
    "P6": "P6-acceptance.md",
    "P7": "P7-consistency.md",
    "P8": "P8-release.md",
}


def _run_card(agate_scripts, python_exe, run_cli, phase, cwd=None, env=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-next-card.py"),
        phase,
        cwd=cwd,
        env=env,
    )


def _file_sha256(path):
    """阶段卡文件 sha256：Windows checkout 可能 CRLF（git autocrlf），归一化 \r\n → \n
    与 CLI 输出（Python print 到管道 universal newlines 为 \n）对齐。"""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _body_sha256(cli_output, skip_lines=4):
    """tail -n +5 后 sha256：按行保留字节（splitlines(keepends=True) 不丢尾部换行）。"""
    lines = cli_output.splitlines(keepends=True)
    body = "".join(lines[skip_lines:])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _full_sha256(cli_output):
    return hashlib.sha256(cli_output.encode("utf-8")).hexdigest()


def _make_link(script, link_path):
    """平台分支：Linux 真软链；Windows（Git Bash ln -sf 退化为复制）用 copyfile。"""
    if os.name == "nt":
        shutil.copyfile(str(script), str(link_path))
    else:
        os.symlink(str(script), str(link_path))


def _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, phase):
    expected = _file_sha256(agate_root / "phase-cards" / _PHASE_CARD_FILES[phase])
    result = _run_card(agate_scripts, python_exe, run_cli, phase)
    assert result.returncode == 0
    assert _body_sha256(result.output) == expected


@pytest.mark.windows_smoke
def test_nc_p0_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P0")


def test_nc_p1_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P1")


def test_nc_p2_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P2")


def test_nc_p3_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P3")


def test_nc_p4_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P4")


def test_nc_p5_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P5")


def test_nc_p6_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P6")


def test_nc_p7_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P7")


def test_nc_p8_cli_body_sha256_matches_card(agate_root, agate_scripts, python_exe, run_cli):
    _assert_body_matches(agate_root, agate_scripts, python_exe, run_cli, "P8")


def test_nc_header_three_lines_fixed(agate_scripts, python_exe, run_cli):
    result = _run_card(agate_scripts, python_exe, run_cli, "P3")
    assert result.returncode == 0
    first_four = "\n".join(result.output.splitlines()[:4])
    assert first_four.startswith("## 当前阶段卡片：P3\n\n路径：")
    assert "---" in result.output


def test_nc_byte_stability_two_calls_sha256_equal(agate_scripts, python_exe, run_cli):
    hash1 = _full_sha256(_run_card(agate_scripts, python_exe, run_cli, "P3").output)
    hash2 = _full_sha256(_run_card(agate_scripts, python_exe, run_cli, "P3").output)
    assert hash1 == hash2


def test_nc_cwd_in_project_dir_still_resolves(agate_scripts, python_exe, run_cli, tmp_path):
    result = _run_card(agate_scripts, python_exe, run_cli, "P3", cwd=str(tmp_path))
    assert result.returncode == 0
    assert _full_sha256(result.output) != ""


@pytest.mark.windows_smoke
def test_nc_symlink_script_readlink_resolves(
    agate_scripts, python_exe, run_cli, agate_root, tmp_path
):
    link_dir = tmp_path / "symlink_test"
    link_dir.mkdir()
    link = link_dir / "card"
    script = agate_scripts / "agate-next-card.py"
    _make_link(script, link)
    # Windows 复制模式下脚本路径解析不到真实 agate_root → 显式 AGATE_ROOT 兜底
    link_env = {"AGATE_ROOT": str(agate_root)} if os.name == "nt" else None
    hash_link = _full_sha256(
        run_cli(python_exe, str(link), "P3", env=link_env).output
    )
    hash_direct = _full_sha256(run_cli(python_exe, str(script), "P3").output)
    assert hash_link == hash_direct


def test_nc_cross_checkout_paths_hash_consistent(
    agate_scripts, python_exe, run_cli, agate_root, tmp_path
):
    link_a = tmp_path / "checkout_a" / "card"
    link_b = tmp_path / "checkout_b" / "card"
    link_a.parent.mkdir()
    link_b.parent.mkdir()
    script = agate_scripts / "agate-next-card.py"
    _make_link(script, link_a)
    _make_link(script, link_b)
    link_env = {"AGATE_ROOT": str(agate_root)} if os.name == "nt" else None
    for phase in _PHASE_CARD_FILES:
        hash_a = _full_sha256(run_cli(python_exe, str(link_a), phase, env=link_env).output)
        hash_b = _full_sha256(run_cli(python_exe, str(link_b), phase, env=link_env).output)
        assert hash_a == hash_b, f"phase {phase} hash mismatch"


def test_nc_no_args_exit_1(agate_scripts, python_exe, run_cli):
    result = run_cli(python_exe, str(agate_scripts / "agate-next-card.py"))
    assert result.returncode == 1
    assert "需要 1 个参数" in result.output


def test_nc_two_args_exit_1(agate_scripts, python_exe, run_cli):
    result = run_cli(python_exe, str(agate_scripts / "agate-next-card.py"), "P3", "extra")
    assert result.returncode == 1
    assert "需要 1 个参数" in result.output


def test_nc_phase_p9_exit_2(agate_scripts, python_exe, run_cli):
    result = run_cli(python_exe, str(agate_scripts / "agate-next-card.py"), "P9")
    assert result.returncode == 2
    assert "不在 P0-P8 范围内" in result.output


def test_nc_lowercase_p3_exit_2_case_sensitive(agate_scripts, python_exe, run_cli):
    result = run_cli(python_exe, str(agate_scripts / "agate-next-card.py"), "p3")
    assert result.returncode == 2


def test_nc_root_1_agate_root_env_override(agate_scripts, python_exe, run_cli, agate_root):
    hash_default = _full_sha256(_run_card(agate_scripts, python_exe, run_cli, "P3").output)
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-next-card.py"),
        "P3",
        env={"AGATE_ROOT": str(agate_root)},
    )
    assert _full_sha256(result.output) == hash_default


def test_nc_root_2_outside_git_repo(agate_scripts, python_exe, run_cli, agate_root, tmp_path):
    tmp_root = tmp_path / "no_git"
    (tmp_root / "phase-cards").mkdir(parents=True)
    (tmp_root / "scripts").mkdir()
    shutil.copyfile(
        str(agate_root / "phase-cards" / "P3-tdd.md"),
        str(tmp_root / "phase-cards" / "P3-tdd.md"),
    )
    shutil.copyfile(
        str(agate_scripts / "agate-next-card.py"),
        str(tmp_root / "scripts" / "agate-next-card.py"),
    )
    result_main = _run_card(agate_scripts, python_exe, run_cli, "P3")
    result_tmp = run_cli(
        python_exe,
        str(tmp_root / "scripts" / "agate-next-card.py"),
        "P3",
        env={"AGATE_ROOT": str(tmp_root)},
    )
    assert _body_sha256(result_main.output) == _body_sha256(result_tmp.output)


@pytest.mark.windows_smoke
def test_bdd_21_windows_drive_backslash_agate_root_strip(
    agate_scripts, python_exe, run_cli, agate_root, tmp_path
):
    if os.name == "nt":
        pytest.skip("盘符/反斜杠前缀剥离在 Windows 上无法用字面目录模拟（Linux 字面反斜杠目录已覆盖）")
    root_agate = "C:\\proj\\agate"
    dir_path = tmp_path / "q1-win"
    (dir_path / root_agate / "phase-cards").mkdir(parents=True)
    shutil.copyfile(
        str(agate_root / "phase-cards" / "P3-tdd.md"),
        str(dir_path / root_agate / "phase-cards" / "P3-tdd.md"),
    )
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-next-card.py"),
        "P3",
        cwd=str(dir_path),
        env={"AGATE_ROOT": root_agate},
    )
    assert result.returncode == 0
    assert "路径：phase-cards/P3-tdd.md" in result.output


def test_bdd_22_linux_regular_path_prefix_strip(
    agate_scripts, python_exe, run_cli
):
    result = run_cli(python_exe, str(agate_scripts / "agate-next-card.py"), "P3")
    assert result.returncode == 0
    assert "路径：phase-cards/P3-tdd.md" in result.output
