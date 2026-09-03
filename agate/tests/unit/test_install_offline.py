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


def test_bdd_29b_no_pillow_bundle_installs_pyyaml_only(tmp_path, agate_scripts, capsys):
    """rev2 CRITICAL-2：无 Pillow bundle + 无 --skip-pillow → 只装 pyyaml，默认流成功。

    回归用例：`install_wheels` 旧实现恒把 Pillow 塞进 pip 命令（仅由 skip 控制），
    对无 Pillow wheel 的最小 bundle `--no-index` 下必失败。修复后安装清单从 manifest
    `components` 推导——"pillow" 组件不存在则不装 Pillow（BDD-29 语义：skip 只过滤已包含项）。
    """
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, with_pillow=False)
    dest = tmp_path / "dest"
    pip_argv = []

    def fake_run(argv, **kwargs):
        if any(str(a) == "install" for a in argv):
            pip_argv.append([str(a) for a in argv])
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    with mock.patch("subprocess.run", side_effect=fake_run), mock.patch.object(
        module, "get_current_platform", return_value="linux-x86_64"
    ):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code == 0
    assert err.strip() == ""
    assert pip_argv
    last = pip_argv[-1]
    assert "--no-index" in last
    assert "--find-links" in last
    assert any("pyyaml" in a for a in last)
    assert not any("Pillow" in a for a in last)
    assert (dest / "v0.48.0").is_dir()
    assert (dest / "v0.48.0" / ".installed-version").read_text(encoding="utf-8").strip() == "v0.48.0"


def test_manifest_version_traversal_rejected(tmp_path, agate_scripts, capsys):
    """rev2 CRITICAL-3：恶意 manifest `version` 穿越（../../..）→ 拒绝安装，不写出 dest_root。

    回归用例：旧实现 `version = manifest["version"]` 直接作 `dest / version` 目录名，
    篡改后可把 bundle 复制到 dest_root 之外。修复后 version 套 vX.Y.Z 正则
    （同 agate-install `_VERSION_RE`），非法即 fail-closed。
    """
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path, version="v0.48.0")
    mpath = bundle / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["version"] = "../../../../pwned"
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    dest = tmp_path / "dest"

    with mock.patch.object(module, "get_current_platform", return_value="linux-x86_64"):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code != 0
    assert "version" in err
    assert not (tmp_path / "pwned").exists()
    assert not dest.exists()


def test_manifest_component_path_traversal_rejected(tmp_path, agate_scripts, capsys):
    """rev2 CRITICAL-3：恶意 manifest 组件 `path` 用 `..` 越界 → 拒绝安装（防越界读）。

    回归用例：旧实现 `verify_checksums` 直接 `bundle / comp["path"]`，`..` 可越过 bundle
    读取 bundle 外文件（哈希比对作可探测 oracle）。修复后组件 path 必须是 bundle 内相对路径
    （拒绝绝对路径与 `..`，commonpath 断言），非法即 fail-closed。
    """
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path)
    mpath = bundle / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    secret = tmp_path / "secret.txt"
    secret.write_text("sensitive", encoding="utf-8")
    manifest["components"]["evil"] = {
        "path": "../secret.txt",
        "sha256": "0" * 64,
    }
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    dest = tmp_path / "dest"

    with mock.patch.object(module, "get_current_platform", return_value="linux-x86_64"):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code != 0
    assert "path" in err
    assert not dest.exists()


# ─────────────────────────────────────────────
# TAG0031 簇 A（DEBT0002 hash 共享，BDD-1）+ R1（P2-design.md §1.3 pyyaml 引导缓解设计，
# 列入 BDD-2 范围）：compute_sha256 迁移到 agate_common + install-offline.py 的
# _ensure_agate_common(bundle_dir, manifest) 引导函数。
#
# 迁移前 install-offline.py 顶部零外部依赖（不 import agate_common/yaml），刻意设计为可在
# 未装 pyyaml 的机器上跑。迁移后 verify_checksums 需要 agate_common.compute_sha256，但
# agate_common 顶部硬依赖 pyyaml（缺失即 sys.exit(1)）——若直接 `import agate_common` 会在
# 真正没装 pyyaml 的机器上于"给它装 pyyaml"（install_wheels）之前就崩溃。缓解设计：
# _ensure_agate_common 先探测 yaml 可用性；不可用时先内联 hashlib 校验 pyyaml wheel 的
# manifest checksum（校验通过才 pip install --no-index --find-links，不匹配则报错且不装），
# 再 import agate_common 返回模块引用。
#
# 当前 install-offline.py 尚无 verify_checksums 接入 agate_common、也无 _ensure_agate_common
# → AttributeError（真实的项目内运行时失败 = B 类红灯语义），非测试代码自身语法错误。


def test_bdd_1_verify_checksums_uses_agate_common_compute_sha256(tmp_path, agate_scripts):
    """BDD-1：install-offline.py 的 checksum 校验改用 agate_common.compute_sha256 后，
    用 agate_common.compute_sha256 算出的 checksum 应通过 verify_checksums 校验（两侧共享
    同一 hash 实现的行为证据；不假设 verify_checksums 内部变量命名，兼容 R1 引导设计）。

    当前状态：agate_common 尚无 compute_sha256（迁移前）→ AttributeError（真红灯）。
    """
    module = _load_script_module(agate_scripts, "agate_install_offline_bdd1", "install-offline.py")
    import agate_common

    bundle = tmp_path / "bundle"
    agate_dir = bundle / "agate"
    agate_dir.mkdir(parents=True)
    (agate_dir / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")

    checksum = agate_common.compute_sha256(agate_dir)
    manifest = {
        "version": "v0.48.0",
        "platform": "linux-x86_64",
        "components": {"agate": {"path": "agate", "sha256": checksum}},
    }

    mismatched = module.verify_checksums(manifest, str(bundle))
    assert mismatched == []


def test_r1_ensure_agate_common_bootstraps_when_yaml_unavailable(tmp_path, agate_scripts, monkeypatch):
    """R1（P2-design.md §1.3「回归覆盖」①，列入 BDD-2 范围）：yaml 不可导入时，
    install-offline.py 的 _ensure_agate_common(bundle_dir, manifest) 应能引导安装 pyyaml
    （mock subprocess.run 的 pip install --no-index --find-links <bundle>/wheels pyyaml）后
    返回可用的 agate_common 模块引用（具备 compute_sha256）。

    先确保 agate_common 已在本进程缓存（避免 yaml 不可用模拟期间，其自身模块级 `import yaml`
    真的被重新触发从而 sys.exit(1)，导致进程级副作用而非测试目标本身的红灯）。

    当前状态：install-offline.py 尚无 _ensure_agate_common → AttributeError（真红灯）。
    """
    module = _load_script_module(
        agate_scripts, "agate_install_offline_r1a", "install-offline.py"
    )
    import agate_common as _agate_common  # noqa: F401  # 确保已缓存，规避测试顺序依赖

    bundle = tmp_path / "bundle"
    wheels = bundle / "wheels"
    wheels.mkdir(parents=True)
    pyyaml_whl = wheels / "pyyaml-6.0.2-py3-none-any.whl"
    pyyaml_whl.write_bytes(b"fake pyyaml wheel data")
    manifest = {
        "version": "v0.48.0",
        "platform": "linux-x86_64",
        "components": {
            "pyyaml": {
                "path": "wheels/pyyaml-6.0.2-py3-none-any.whl",
                "sha256": _sha256_bytes(pyyaml_whl.read_bytes()),
            }
        },
    }

    pip_calls = []

    def fake_run(argv, **kwargs):
        pip_calls.append([str(a) for a in argv])
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    monkeypatch.setitem(sys.modules, "yaml", None)
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = module._ensure_agate_common(str(bundle), manifest)

    assert result is not None
    assert hasattr(result, "compute_sha256")
    assert pip_calls, "yaml 不可用时应触发 pip install 引导安装 pyyaml"
    assert any("pyyaml" in a for a in pip_calls[-1])
    assert "--no-index" in pip_calls[-1]


def test_r1_ensure_agate_common_rejects_pyyaml_checksum_mismatch_before_pip_install(
    tmp_path, agate_scripts, monkeypatch, capsys
):
    """R1（P2-design.md §1.3「回归覆盖」②，列入 BDD-2 范围）：pyyaml wheel checksum 与
    manifest 不匹配时，_ensure_agate_common 必须在执行 pip install 之前就拒绝（stderr 报错 +
    非成功返回），且全程 mock 的 subprocess.run 未被调用——用"未被调用"断言校验"校验先于安装"
    这一顺序本身，而不只是校验最终结果（BDD-26 字面不变量"checksum 不匹配则不落地"对 pyyaml
    组件同样成立）。

    当前状态：install-offline.py 尚无 _ensure_agate_common → AttributeError（真红灯）。
    """
    module = _load_script_module(
        agate_scripts, "agate_install_offline_r1b", "install-offline.py"
    )
    import agate_common as _agate_common  # noqa: F401  # 确保已缓存，规避测试顺序依赖

    bundle = tmp_path / "bundle"
    wheels = bundle / "wheels"
    wheels.mkdir(parents=True)
    pyyaml_whl = wheels / "pyyaml-6.0.2-py3-none-any.whl"
    pyyaml_whl.write_bytes(b"fake pyyaml wheel data")
    manifest = {
        "version": "v0.48.0",
        "platform": "linux-x86_64",
        "components": {
            "pyyaml": {
                "path": "wheels/pyyaml-6.0.2-py3-none-any.whl",
                # 篡改：与真实 wheel 内容不匹配的 sha256（模拟被篡改/损坏的 pyyaml 组件）
                "sha256": "0" * 64,
            }
        },
    }

    subprocess_run_calls = []

    def fake_run(argv, **kwargs):
        subprocess_run_calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    monkeypatch.setitem(sys.modules, "yaml", None)
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = module._ensure_agate_common(str(bundle), manifest)

    err = capsys.readouterr().err
    assert result is None
    assert "pyyaml" in err
    assert not subprocess_run_calls, "checksum 不匹配时 pip install 不应被执行（校验先于安装）"


def test_manifest_absolute_path_rejected(tmp_path, agate_scripts, capsys):
    """rev2 CRITICAL-3：恶意 manifest 组件 `path` 为绝对路径 → 拒绝安装。"""
    module = _load_script_module(agate_scripts, "agate_install_offline", "install-offline.py")
    bundle = _make_bundle(tmp_path)
    mpath = bundle / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    manifest["components"]["evil"] = {
        "path": "/etc/hostname",
        "sha256": "0" * 64,
    }
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    dest = tmp_path / "dest"

    with mock.patch.object(module, "get_current_platform", return_value="linux-x86_64"):
        code = module.main([str(bundle), "--dest-root", str(dest)])

    err = capsys.readouterr().err
    assert code != 0
    assert "path" in err
    assert not dest.exists()
