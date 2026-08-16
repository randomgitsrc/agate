# tests/unit/test_agate_pack_offline.py — 离线打包器 agate-pack-offline.py（TAG0008 批次 offline，BDD-22~24）
# 被测：agate/scripts/agate-pack-offline.py（P4 实现；当前未实现 → 加载抛 ModuleNotFoundError = B 类红灯）。
# 契约（详见 P3-test-cases-offline.md）：compute_sha256 / build_manifest / pack_offline /
#   PackOfflineError / main(argv)->int；bundle 目录命名 agate-{version}-{platform}；git worktree add +
#   pip download 走 subprocess.run（测试 mock）；目录组件 sha256 用"排序逐文件 hash 拼接再整体 hash"约定。
# 网络隔离：不实际联网 / 不实际 pip download——假 tag 代码 + 假 wheel 文件（tmp_path），checksum 用真实 hashlib。

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

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


def _bundle_dir(out_dir, version, platform):
    return Path(out_dir) / f"agate-{version}-{platform}"


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _fake_artifacts_side_effect(bundle, include_pillow):
    """mock subprocess.run：无论 git/pip 调用都幂等产出假 tag 代码 + 假 wheel（跨调用幂等，避免 argv 解析耦合）。"""

    def _side_effect(argv, **kwargs):
        agate_dir = bundle / "agate"
        agate_dir.mkdir(parents=True, exist_ok=True)
        (agate_dir / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")
        wheels = bundle / "wheels"
        wheels.mkdir(parents=True, exist_ok=True)
        (wheels / "pyyaml-6.0.2-py3-none-any.whl").write_bytes(b"fake pyyaml wheel data")
        if include_pillow:
            (wheels / "Pillow-10.4.0-py3-none-any.whl").write_bytes(b"fake pillow wheel data")
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    return _side_effect


@pytest.mark.windows_smoke
def test_bdd_22_bundle_manifest(tmp_path, agate_scripts):
    module = _load_script_module(agate_scripts, "agate_pack_offline", "agate-pack-offline.py")
    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    bundle = _bundle_dir(out_dir, "v0.48.0", "linux-x86_64")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _fake_artifacts_side_effect(bundle, include_pillow=False))
        result = module.pack_offline("v0.48.0", "linux-x86_64", str(out_dir), str(repo_dir))

    assert Path(result) == bundle
    assert (bundle / "manifest.json").is_file()
    assert (bundle / "agate" / "WORKFLOW.md").is_file()
    assert list((bundle / "wheels").glob("*.whl"))

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["platform"] == "linux-x86_64"
    assert manifest["version"] == "v0.48.0"
    for comp in manifest["components"].values():
        assert re.fullmatch(r"[0-9a-f]{64}", comp["sha256"])


def test_bdd_23_manifest_fields_checksum(tmp_path, agate_scripts):
    module = _load_script_module(agate_scripts, "agate_pack_offline", "agate-pack-offline.py")
    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    bundle = _bundle_dir(out_dir, "v0.48.0", "linux-x86_64")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _fake_artifacts_side_effect(bundle, include_pillow=False))
        module.pack_offline("v0.48.0", "linux-x86_64", str(out_dir), str(repo_dir))

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["platform"] == "linux-x86_64"

    wheel = next((bundle / "wheels").glob("pyyaml-*.whl"))
    pyyaml_entry = manifest["components"]["pyyaml"]
    assert pyyaml_entry["sha256"] == _sha256_bytes(wheel.read_bytes())
    assert (bundle / pyyaml_entry["path"]).is_file()
    for name, comp in manifest["components"].items():
        assert comp["sha256"], f"component {name} sha256 为空"


def test_bdd_24_fail_tag_missing(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_pack_offline", "agate-pack-offline.py")
    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    bundle = _bundle_dir(out_dir, "v0.99.0", "linux-x86_64")

    def _fail_git(argv, **kwargs):
        if "worktree" in argv and "add" in argv:
            raise subprocess.CalledProcessError(128, argv, output=b"", stderr=b"tag not found")
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _fail_git)
        code = module.main(["v0.99.0", "--platform", "linux-x86_64", "--outdir", str(out_dir)])

    err = capsys.readouterr().err
    assert code != 0
    assert "v0.99.0" in err
    assert not (bundle / "manifest.json").exists()


def test_bdd_24_fail_pip_network(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_pack_offline", "agate-pack-offline.py")
    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    bundle = _bundle_dir(out_dir, "v0.48.0", "linux-x86_64")

    def _fail_pip(argv, **kwargs):
        if "pip" in argv and "download" in argv:
            raise OSError("Network is unreachable")
        agate_dir = bundle / "agate"
        agate_dir.mkdir(parents=True, exist_ok=True)
        (agate_dir / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _fail_pip)
        code = module.main(["v0.48.0", "--platform", "linux-x86_64", "--outdir", str(out_dir)])

    err = capsys.readouterr().err
    assert code != 0
    assert "download" in err
    assert not (bundle / "manifest.json").exists()


def test_bdd_24_fail_wheel_missing(tmp_path, agate_scripts, capsys):
    module = _load_script_module(agate_scripts, "agate_pack_offline", "agate-pack-offline.py")
    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    bundle = _bundle_dir(out_dir, "v0.48.0", "linux-x86_64")

    def _empty_wheels(argv, **kwargs):
        if "pip" in argv and "download" in argv:
            (bundle / "wheels").mkdir(parents=True, exist_ok=True)
            return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")
        agate_dir = bundle / "agate"
        agate_dir.mkdir(parents=True, exist_ok=True)
        (agate_dir / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _empty_wheels)
        code = module.main(["v0.48.0", "--platform", "linux-x86_64", "--outdir", str(out_dir)])

    err = capsys.readouterr().err
    assert code != 0
    assert "wheel" in err
    assert not (bundle / "manifest.json").exists()
