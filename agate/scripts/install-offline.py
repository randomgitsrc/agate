#!/usr/bin/env python3
"""install-offline.py — 内网离线安装器（TAG0008 批次 offline，BDD-25~29）

在**内网**机器上安装 agate-pack-offline.py 打好的离线 bundle：
  1. 读 manifest.json
  2. 平台核对（不匹配 → stderr 警告 + 拒绝安装，exit 非 0，BDD-25）
  3. checksum 校验（不匹配 → 拒绝安装 + 指明组件，exit 非 0，BDD-26）
  4. `pip install --no-index --find-links wheels/`（BDD-27）
  5. 建 ~/.agate/vX.Y.Z/（bundle 复制目录，非 worktree）
  6. current 指针：Linux 软链 / Windows（或 AGATE_HOOK_COPY_MODE=1）复制 + .agate-root 标记
  7. 验证：.installed-version 内容 = 版本号（BDD-28）
  8. 勾选：--skip-python / --skip-pillow 覆盖包含项（BDD-29）

用法:
  python3 install-offline.py <bundle_dir> [--dest-root DIR] [--skip-python] [--skip-pillow]

目录组件 sha256 约定（与 agate-pack-offline.py 一致）：对目录内全部文件按相对路径
字典序排序，逐一 sha256(file_bytes) 得 hex，拼为一条长串后整体 sha256。
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_DEFAULT_DEST = os.path.expanduser("~/.agate")
_VERSION_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def load_manifest(manifest_path):
    """读 manifest.json 为 dict。"""
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def _validate_manifest(manifest, bundle_dir):
    """manifest 字段校验（CRITICAL-3，防路径穿越，fail-closed）。

    version 必须匹配 vX.Y.Z（与 agate-install `_VERSION_RE` 同款正则）；
    每个组件 path 必须是 bundle 内相对路径（拒绝绝对路径与 '..'，断言
    os.path.commonpath([bundle, p]) == bundle）。非法 → 抛 ValueError。
    """
    version = manifest.get("version", "")
    if not isinstance(version, str) or not _VERSION_RE.match(version):
        raise ValueError(f"manifest version 非法: {version!r}（应为 vX.Y.Z）")
    bundle = Path(bundle_dir).resolve()
    for name, comp in manifest.get("components", {}).items():
        raw = comp.get("path", "")
        if not isinstance(raw, str) or not raw:
            raise ValueError(f"manifest 组件 {name!r} 缺 path 字段")
        p = Path(raw)
        if p.is_absolute():
            raise ValueError(f"manifest 组件 {name!r} path 为绝对路径: {raw!r}")
        if ".." in p.parts:
            raise ValueError(f"manifest 组件 {name!r} path 含 '..': {raw!r}")
        resolved = (bundle / p).resolve()
        try:
            if os.path.commonpath([str(bundle), str(resolved)]) != str(bundle):
                raise ValueError(f"manifest 组件 {name!r} path 越出 bundle: {raw!r}")
        except ValueError as exc:
            raise ValueError(f"manifest 组件 {name!r} path 越出 bundle: {raw!r}") from exc


def get_current_platform():
    """返回当前机器平台标签（linux-x86_64 / windows-x86_64）；main 经它核对平台。"""
    import platform as _platform

    machine = _platform.machine().lower()
    if sys.platform == "win32":
        return "windows-x86_64"
    if machine in ("x86_64", "amd64"):
        return "linux-x86_64"
    return f"linux-{machine}"


def check_platform(manifest_platform, current_platform):
    """平台核对纯逻辑；True = 匹配。"""
    return manifest_platform == current_platform


def compute_sha256(path):
    """sha256 hex：文件=内容哈希；目录=排序逐文件 hash 拼接再整体 hash（与 pack 侧一致）。"""
    p = Path(path)
    if p.is_dir():
        digests = []
        for f in sorted(p.rglob("*"), key=lambda f: f.relative_to(p).as_posix()):
            if f.is_file():
                digests.append(hashlib.sha256(f.read_bytes()).hexdigest())
        return hashlib.sha256("".join(digests).encode("utf-8")).hexdigest()
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_checksums(manifest, bundle_dir):
    """逐组件按 manifest path 定位、重算 sha256 比对；返回不匹配组件名列表（空 = 全过）。

    先 `_validate_manifest` 校验字段（version 正则 + 组件 path 限 bundle 内，CRITICAL-3）——
    拒绝篡改 manifest 用 `..`/绝对路径越界读 bundle 外文件（哈希比对作为可探测 oracle）。
    """
    _validate_manifest(manifest, bundle_dir)
    bundle = Path(bundle_dir)
    mismatched = []
    for name, comp in manifest.get("components", {}).items():
        p = bundle / comp["path"]
        if not p.exists():
            mismatched.append(name)
            continue
        if compute_sha256(p) != comp["sha256"]:
            mismatched.append(name)
    return mismatched


def install_wheels(bundle_dir, skip=()):
    """pip install --no-index --find-links <bundle>/wheels——安装清单从 manifest components 推导。

    有 "pillow" 组件才装 Pillow（无 Pillow bundle 默认流不再失败，CRITICAL-2）；
    "pyyaml" 组件必有 → 默认装 pyyaml。skip 只过滤已包含项（BDD-29）。
    """
    wheels_dir = Path(bundle_dir) / "wheels"
    manifest = load_manifest(Path(bundle_dir) / "manifest.json")
    components = manifest.get("components", {})
    cmd = ["pip", "install", "--no-index", "--find-links", str(wheels_dir)]
    for comp, pkg in (("pyyaml", "pyyaml"), ("pillow", "Pillow")):
        if comp in components and comp not in skip:
            cmd.append(pkg)
    try:
        subprocess.run(
            cmd, capture_output=True,
            text=True, encoding="utf-8", errors="replace", check=True,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        raise RuntimeError(f"pip install 失败: {exc}") from exc


def _copy_tree(src, dst, exclude_names=()):
    """copytree 封装：顶层目录复制（可排除 skip 的组件顶层名，如 python）。"""
    def _ignore(dirpath, names):
        if os.path.normpath(dirpath) == os.path.normpath(str(src)):
            return [n for n in names if n in exclude_names]
        return []

    shutil.copytree(str(src), str(dst), dirs_exist_ok=True, ignore=_ignore)


def install_bundle(manifest_path, bundle_dir, dest_root, skip=()):
    """复制 bundle 到 dest_root/v{version}/ → 写 .installed-version → 建 current 指针。

    Linux 软链 → v{version} 目录；Windows / AGATE_HOOK_COPY_MODE=1：复制指针文件 +
    dest_root/.agate-root 标记文件（含目标目录绝对路径）。
    """
    manifest = load_manifest(manifest_path)
    _validate_manifest(manifest, bundle_dir)
    version = manifest["version"]
    bundle = Path(bundle_dir)
    dest = Path(dest_root)
    version_dir = dest / version

    exclude = set()
    if "python" in skip and "python" in manifest.get("components", {}):
        py_path = Path(manifest["components"]["python"]["path"])
        exclude.add(py_path.parts[0])
    _copy_tree(bundle, version_dir, exclude_names=exclude)

    (version_dir / ".installed-version").write_text(version + "\n", encoding="utf-8")

    copy_mode = os.environ.get("AGATE_HOOK_COPY_MODE") == "1" or sys.platform == "win32"
    current = dest / "current"
    if copy_mode:
        current.write_text(version + "\n", encoding="utf-8")
        marker = dest / ".agate-root"
        marker.write_text(str(version_dir) + "\n", encoding="utf-8")
    else:
        if current.is_symlink() or current.exists():
            current.unlink()
        os.symlink(str(version_dir), str(current))
    return version_dir


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    bundle_dir = None
    dest_root = _DEFAULT_DEST
    skip = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--dest-root":
            i += 1
            if i >= len(args):
                sys.stderr.write("install-offline: --dest-root 缺少取值\n")
                return 2
            dest_root = args[i]
        elif a == "--skip-python":
            skip.append("python")
        elif a == "--skip-pillow":
            skip.append("pillow")
        elif a.startswith("--"):
            sys.stderr.write(f"install-offline: 未知选项 {a}\n")
            return 2
        else:
            bundle_dir = a
        i += 1

    if not bundle_dir:
        sys.stderr.write("install-offline: 缺少 bundle 目录参数\n")
        return 2

    manifest_path = Path(bundle_dir) / "manifest.json"
    try:
        manifest = load_manifest(manifest_path)
        _validate_manifest(manifest, bundle_dir)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"install-offline: 读取/校验 manifest 失败: {exc}\n")
        return 1

    manifest_platform = manifest.get("platform", "")
    current_platform = get_current_platform()
    if not check_platform(manifest_platform, current_platform):
        sys.stderr.write(
            f"install-offline: 平台不匹配——bundle 平台 {manifest_platform} "
            f"与本机平台 {current_platform} 不一致，拒绝安装\n"
        )
        return 1

    mismatched = verify_checksums(manifest, bundle_dir)
    if mismatched:
        sys.stderr.write(
            "install-offline: checksum 校验失败，以下组件被篡改或损坏: "
            + ", ".join(mismatched) + "\n"
        )
        return 1

    try:
        install_wheels(bundle_dir, skip=tuple(skip))
        install_bundle(manifest_path, bundle_dir, dest_root, skip=tuple(skip))
    except (RuntimeError, OSError, ValueError) as exc:
        sys.stderr.write(f"install-offline: 安装失败: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
