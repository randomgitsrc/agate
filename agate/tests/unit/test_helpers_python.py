# tests/unit/test_helpers_python.py — python_exe 探测 helper 语义
# （helpers-python.bats 3 用例迁移，TAG0011 批次 1）
# create_python_shim_bin 退役（P2 §3.1 / P3 §4 批次 0）——pytest 直跑解释器，shim 断言
# 改写为 python_exe fixture 语义（conftest，detect_python 等价）+ agate_common.probe_python
# （python3 → python 回退，fail-closed 返回空）。

import os
import shutil

import pytest


def _probe_code():
    return "import agate_common; print(agate_common.probe_python() or 'NONE')"


def _make_python_only_bin(base, python_exe, name="pybin"):
    """构造仅含 python 可执行（无 python3）的 PATH 目录（运行时探测形态，跨平台）。"""
    fakebin = base / name
    fakebin.mkdir()
    dest = fakebin / "python.exe" if os.name == "nt" else fakebin / "python"
    shutil.copyfile(python_exe, dest)
    os.chmod(dest, 0o755)
    return fakebin, dest


@pytest.mark.windows_smoke
def test_bdd_13_python_exe_resolved_and_executable(python_exe, run_cli):
    assert python_exe
    result = run_cli(python_exe, "--version")
    assert result.returncode == 0
    assert "Python" in result.output


@pytest.mark.windows_smoke
def test_bdd_15_python_fallback_when_python3_missing(
    python_exe, run_cli, agate_scripts, tmp_path
):
    fakebin, dest = _make_python_only_bin(tmp_path, python_exe)
    result = run_cli(
        python_exe,
        "-c",
        _probe_code(),
        env={"PATH": str(fakebin), "PYTHONPATH": str(agate_scripts)},
    )
    assert result.returncode == 0
    assert str(dest).lower() in result.output.lower()


def test_bdd_17_probe_python_fail_closed(python_exe, run_cli, agate_scripts, tmp_path):
    scripts_py = str(agate_scripts)

    # ① 正常环境：probe_python 解析到可用 python → 非空
    result = run_cli(python_exe, "-c", _probe_code(), env={"PYTHONPATH": scripts_py})
    assert result.returncode == 0
    assert result.output != ""

    # ② PATH 仅含 python（无 python3）→ probe_python 回退 python
    fakebin, dest = _make_python_only_bin(tmp_path, python_exe, name="pyonly")
    result = run_cli(
        python_exe,
        "-c",
        _probe_code(),
        env={"PATH": str(fakebin), "PYTHONPATH": scripts_py},
    )
    assert result.returncode == 0
    assert str(dest).lower() in result.output.lower()

    # ③ PATH 无任何 python → probe_python 返回空 → 输出 NONE（调用方 fail-closed 阻断）
    emptybin = tmp_path / "emptybin"
    emptybin.mkdir()
    result = run_cli(
        python_exe,
        "-c",
        _probe_code(),
        env={"PATH": str(emptybin), "PYTHONPATH": scripts_py},
    )
    assert result.returncode == 0
    assert "NONE" in result.output
