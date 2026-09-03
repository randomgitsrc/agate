# tests/regression/test_offline_bundle_roundtrip.py — 离线包 pack→install→卸载全流程回归
# （TAG0031 DEBT0002 hash 共享迁移，BDD-2；P2-design.md §1.1 簇 A 新增测试 / §3
# gate_commands.P5_offline_bundle 独立 key）。
#
# 覆盖：agate-pack-offline.py 打包 → install-offline.py 安装 → agate-install.py 卸载三步链路，
# `compute_sha256` 迁移到 `agate_common.py` 共享实现后，三步行为与迁移前逐字节一致——
# 打包产出 manifest.json（sha256 字段值不变）、安装 checksum 校验通过、卸载成功移除版本目录，
# 全程无 checksum 不匹配误报（BDD-2 原文验收条件）。
#
# 迁移锚点（保证本文件当前为真红灯，而非"流程本就跑得通"的假绿）：pack/install 两侧的
# `compute_sha256` 必须是 `agate_common.compute_sha256` 同一函数对象（全仓共享单实现，
# 与 BDD-1「全仓 grep def compute_sha256 只有 1 处定义」同一约束的行为面证据）。当前
# pack/install 两侧仍各自本地定义 → identity 不成立，断言失败（真红灯，非语法错误）；
# 迁移落地后该断言转绿，其后的 pack→install→卸载全流程行为不变性断言才真正开始把关回归。
#
# 网络隔离：全程 mock subprocess.run（git worktree add / pip download / pip install /
# git worktree remove），不联网、不实际 pip download（同 test_agate_pack_offline.py /
# test_install_offline.py 既有网络隔离手法）。HOME 环境变量重定向到 tmp_path（
# agate-install.py 的 `_find_references` 卸载引用扫描用 os.path.expanduser("~")，必须隔离
# 防触碰真实 ~/.agate，同该模块 docstring 既有测试隔离约定）；安装目标 dest_root 同样落在
# tmp_path 下，不写 ~/.agate。

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def _load_script_module(agate_scripts, module_name, filename):
    """从 agate/scripts/ 加载脚本为模块（同 test_agate_pack_offline.py/test_install_offline.py
    既有惯例）；被测模块未实现 → ModuleNotFoundError（B 类红灯）。"""
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


def _fake_pack_artifacts(bundle):
    """mock subprocess.run（pack 阶段）：git worktree add / pip download 均幂等产出假产物，
    跨调用幂等（不耦合具体 argv 解析），同 test_agate_pack_offline.py 既有手法。"""

    def _side_effect(argv, **kwargs):
        agate_dir = bundle / "agate"
        agate_dir.mkdir(parents=True, exist_ok=True)
        (agate_dir / "WORKFLOW.md").write_text("# agate\n", encoding="utf-8")
        wheels = bundle / "wheels"
        wheels.mkdir(parents=True, exist_ok=True)
        (wheels / "pyyaml-6.0.2-py3-none-any.whl").write_bytes(b"fake pyyaml wheel data")
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    return _side_effect


def _expected_component_sha256(path):
    """独立 oracle：现状目录/文件 hash 约定（不依赖 agate_common，避免测试自证）——
    文件=内容哈希；目录=按 f.relative_to(p).as_posix() 字典序排序逐文件 sha256 拼接再整体
    sha256（与 agate-pack-offline.py/install-offline.py 现状实现逐字节一致的独立复算）。"""
    p = Path(path)
    if p.is_dir():
        digests = [
            hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(p.rglob("*"), key=lambda f: f.relative_to(p).as_posix())
            if f.is_file()
        ]
        return hashlib.sha256("".join(digests).encode("utf-8")).hexdigest()
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change(
    tmp_path, agate_scripts, monkeypatch, capsys
):
    """BDD-2：hash 合并后 pack → install → 卸载全流程无行为变化（回归）。

    Given 用改造后的 agate-pack-offline.py 对本地 worktree（无网络依赖）打包一个 bundle
    When 依次执行 agate-pack-offline.py 打包 → install-offline.py 安装 →
         agate-install.py 卸载该版本
    Then 三步均与改造前行为一致：打包产出 manifest.json（sha256 字段值不变）、安装 checksum
         校验通过、卸载成功移除版本目录，全程无 checksum 不匹配误报
    """
    # ── 迁移锚点：pack/install 两侧的 compute_sha256 必须是 agate_common 共享的同一函数对象 ──
    scripts_dir = str(agate_scripts)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    pack_module = _load_script_module(agate_scripts, "agate_pack_offline_rt", "agate-pack-offline.py")
    install_module = _load_script_module(agate_scripts, "agate_install_offline_rt", "install-offline.py")
    agate_install_module = _load_script_module(agate_scripts, "agate_install_rt", "agate-install.py")

    import agate_common

    assert pack_module.compute_sha256 is agate_common.compute_sha256, (
        "agate-pack-offline.py 的 compute_sha256 应迁移为 agate_common 共享实现（当前各自本地定义）"
    )
    assert install_module.compute_sha256 is agate_common.compute_sha256, (
        "install-offline.py 的 compute_sha256 应迁移为 agate_common 共享实现（当前各自本地定义）"
    )

    out_dir = tmp_path / "out"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    dest_root = tmp_path / "dest"
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    version = "v0.48.0"
    platform = "linux-x86_64"
    bundle = out_dir / f"agate-{version}-{platform}"

    # ── ① pack：mock subprocess.run（git worktree add / pip download），本地无网络 ──
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(subprocess, "run", _fake_pack_artifacts(bundle))
        result_bundle = pack_module.pack_offline(version, platform, str(out_dir), str(repo_dir))
    assert Path(result_bundle) == bundle
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    for name, comp in manifest["components"].items():
        comp_path = bundle / comp["path"]
        expected = _expected_component_sha256(comp_path)
        assert comp["sha256"] == expected, (
            f"组件 {name} 的 sha256 应与现状目录/文件 hash 约定逐字节一致（迁移未改变算法）"
        )

    # ── ② install：mock subprocess.run（pip install --no-index），checksum 校验须通过 ──
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            subprocess, "run",
            lambda argv, **kw: subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b""),
        )
        mp.setattr(install_module, "get_current_platform", lambda: platform)
        code = install_module.main([str(bundle), "--dest-root", str(dest_root)])
    err = capsys.readouterr().err
    assert code == 0, f"安装应成功（无 checksum 不匹配误报），stderr: {err}"
    assert "checksum" not in err.lower(), f"安装阶段不应有 checksum 误报: {err}"
    version_dir = dest_root / version
    assert version_dir.is_dir()
    assert (version_dir / ".installed-version").read_text(encoding="utf-8").strip() == version

    # ── ③ 卸载：mock run_git（无需真实 git 仓库），HOME 已隔离到 fake_home，
    #    _find_references 不应因扫到本次安装本身而误判为"仍被引用" ──
    monkeypatch.setattr(agate_install_module, "run_git", lambda *a, **k: (0, ""))
    with pytest.raises(SystemExit) as exc_info:
        agate_install_module._cmd_uninstall(str(dest_root), version)
    assert exc_info.value.code == 0, "卸载应成功退出（exit 0），不应被误判为仍被引用/无引用可安全卸载判定失败"
    assert not version_dir.exists(), "卸载后版本目录应被移除"
