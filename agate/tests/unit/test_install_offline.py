# tests/unit/test_install_offline.py — 内网安装器 install-offline.py（TAG0008 批次 offline，BDD-25~29）
# 被测：agate/scripts/install-offline.py（P4 实现；当前未实现 → 加载抛 ModuleNotFoundError = B 类红灯）。
# 契约（详见 P3-test-cases-offline.md）：load_manifest / check_platform / get_current_platform /
#   verify_checksums / install_wheels / install_bundle / main(argv)->int。
# 网络隔离：pip install mock subprocess.run；平台核对 / checksum 校验纯逻辑直接测；
#   假 bundle 的 manifest 含真实 hashlib checksum（文件组件）；hook 指向平台分支断言。

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from unittest import mock

import pytest


def _load_script_module(agate_scripts, module_name, filename):
    """从 agate/scripts/ 加载脚本为模块；被测模块未实现 → ModuleNotFoundError（B 类红灯，No module named 供 formatter 提取）。"""
    path = agate_scripts / filename
    if not path.is_file():
        raise ModuleNotFoundError(f"No module named '{module_name}' (被测模块未实现: {filename})")
    scripts_dir = str(agate_scripts)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _make_bundle(tmp_path, version="v0.48.0", platform="linux-x86_64", with_pillow=False):
    """构造假离线 bundle：agate 代码 + wheels/（pyyaml 必装 / Pillow 可选）+ manifest.json（真实 sha256）。"""
    bundle = tmp_path / "bundle"
    agate = bundle / "agate"
    agate.mkdir(parents=True)
    (agate / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")
    wheels = bundle / "wheels"
    wheels.mkdir(parents=True)
    pyyaml_whl = wheels / "pyyaml-6.0.2-py3-none-any.whl"
    pyyaml_whl.write_bytes(b"fake pyyaml wheel data")

    components = {
        "pyyaml": {
            "path": "wheels/pyyaml-6.0.2-py3-none-any.whl",
            "sha256": _sha256_bytes(pyyaml_whl.read_bytes()),
        }
    }
    if with_pillow:
        pillow_whl = wheels / "Pillow-10.4.0-py3-none-any.whl"
        pillow_whl.write_bytes(b"fake pillow wheel data")
        components["pillow"] = {
            "path": "wheels/Pillow-10.4.0-py3-none-any.whl",
            "sha256": _sha256_bytes(pillow_whl.read_bytes()),
        }

    manifest = {"version": version, "platform": platform, "components": components}
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return bundle


@pytest.mark.windows_smoke
def test_bdd_25_platform_mismatch_reject(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, platform="linux-x86_64")
    dest = tmp_path / "dest"

    with mock.patch.object(module, "get_current_platform", return_value="windows-x86_64"):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code != 0
    assert "linux-x86_64" in err
    assert "windows-x86_64" in err
    assert not dest.exists()


def test_bdd_26_checksum_mismatch_reject(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, platform="linux-x86_64")
    wheel = next((bundle / "wheels").glob("pyyaml-*.whl"))
    tampered = bytearray(wheel.read_bytes())
    tampered[0] ^= 0xFF
    wheel.write_bytes(bytes(tampered))
    dest = tmp_path / "dest"

    with mock.patch.object(module, "get_current_platform", return_value="linux-x86_64"):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code != 0
    assert "pyyaml" in err
    assert not dest.exists()


def test_bdd_27_wheels_offline_install(tmp_path, agate_scripts):
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, with_pillow=True)
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = [str(a) for a in argv]
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with mock.patch("subprocess.run", side_effect=fake_run):
        module.install_wheels(str(bundle), skip=())

    argv = captured["argv"]
    assert "install" in argv
    assert "--no-index" in argv
    assert "--find-links" in argv
    assert any(str(bundle / "wheels") in a for a in argv)
    assert any("pyyaml" in a for a in argv)
    assert any("Pillow" in a for a in argv)


def test_bdd_28_version_dir_hook_verify(tmp_path, agate_scripts):
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, version="v0.48.0")
    dest = tmp_path / "agate-root"

    with mock.patch(
        "subprocess.run", return_value=subprocess.CompletedProcess(["verify"], 0, stdout=b"", stderr=b"")
    ):
        module.install_bundle(str(bundle / "manifest.json"), str(bundle), str(dest))

    version_dir = dest / "v0.48.0"
    assert version_dir.is_dir()
    assert (version_dir / "agate" / "WORKFLOW.md").is_file()
    assert (version_dir / ".installed-version").read_text(encoding="utf-8").strip() == "v0.48.0"

    current = dest / "current"
    if os.environ.get("AGATE_HOOK_COPY_MODE") == "1" or sys.platform == "win32":
        assert current.is_file()
        marker = dest / ".agate-root"
        assert marker.is_file()
        assert marker.read_text(encoding="utf-8").strip() == str(version_dir)
    else:
        assert current.is_symlink()
        assert os.readlink(str(current)) == str(version_dir)


def test_bdd_28b_copy_mode_hook(agate_scripts, tmp_path, monkeypatch):
    monkeypatch.setenv("AGATE_HOOK_COPY_MODE", "1")
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, version="v0.48.0")
    dest = tmp_path / "agate-root-copy"

    with mock.patch(
        "subprocess.run", return_value=subprocess.CompletedProcess(["verify"], 0, stdout=b"", stderr=b"")
    ):
        module.install_bundle(str(bundle / "manifest.json"), str(bundle), str(dest))

    version_dir = dest / "v0.48.0"
    assert version_dir.is_dir()
    current = dest / "current"
    assert current.is_file()
    marker = dest / ".agate-root"
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8").strip() == str(version_dir)


def test_bdd_29_skip_flags(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, with_pillow=True)
    dest = tmp_path / "dest"
    pip_argv = []

    def fake_run(argv, **kwargs):
        if any(str(a) == "install" for a in argv):
            pip_argv.append([str(a) for a in argv])
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with mock.patch("subprocess.run", side_effect=fake_run), mock.patch.object(
        module, "get_current_platform", return_value="linux-x86_64"
    ):
        code = module.main([str(bundle), "--dest-root", str(dest), "--skip-python", "--skip-pillow"])

    err = capsys.readouterr().err
    assert code == 0
    assert err.strip() == ""
    assert pip_argv
    last = pip_argv[-1]
    assert "--no-index" in last
    assert "--find-links" in last
    assert any("pyyaml" in a for a in last)
    assert not any("Pillow" in a for a in last)
