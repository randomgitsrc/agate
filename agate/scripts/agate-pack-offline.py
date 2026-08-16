#!/usr/bin/env python3
"""agate-pack-offline.py — 外网离线打包器（TAG0008 批次 offline，BDD-22~24）

在**外网**机器上把指定版本 tag 的 agate 代码 + 目标平台的依赖 wheels 打包成
离线部署 bundle，供内网机器经 install-offline.py 安装。

用法:
  python3 agate-pack-offline.py v0.48.0 [--platform linux-x86_64|windows-x86_64]
      [--outdir DIR] [--repo DIR] [--include-python] [--include-pillow]

- 默认平台 linux-x86_64，默认 repo ~/.agate/repo，默认 outdir 当前目录。
- 产物：`<outdir>/agate-<version>-<platform>/`，内含：
    agate/          # 版本 tag 检出代码（git worktree add）
    wheels/         # pip download --platform 拉到的 pyyaml [Pillow] wheel
    manifest.json   # platform + version + 各组件 {path, sha256}
- 失败路径（BDD-24）：tag 不存在 / pip download 网络失败 / wheel 缺失
  → 抛 PackOfflineError（main 捕获 → stderr + 非 0 退出），不产 manifest.json。

目录组件 sha256 约定（与 install-offline.py 一致）：对目录内全部文件按相对路径
字典序排序，逐一 sha256(file_bytes) 得 hex，拼为一条长串后整体 sha256。
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# 平台标签 → pip --platform 值（P2 §7 minimal_validation 已实测可用）
_PIP_PLATFORMS = {
    "linux-x86_64": "manylinux_2_17_x86_64",
    "windows-x86_64": "win_amd64",
}

_DEFAULT_REPO = os.path.join(os.path.expanduser("~/.agate"), "repo")


class PackOfflineError(RuntimeError):
    """打包失败信号（tag 不存在 / pip download 失败 / wheel 缺失）。"""


def _run(cmd, cwd=None):
    """subprocess.run 封装：非 0 退出抛 CalledProcessError（调用方转为 PackOfflineError）。"""
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=True,
    )


def compute_sha256(path):
    """sha256 hex：文件=内容哈希；目录=排序逐文件 hash 拼接再整体 hash（与 install 侧一致）。"""
    p = Path(path)
    if p.is_dir():
        digests = []
        for f in sorted(p.rglob("*"), key=lambda f: f.relative_to(p).as_posix()):
            if f.is_file():
                digests.append(hashlib.sha256(f.read_bytes()).hexdigest())
        return hashlib.sha256("".join(digests).encode("utf-8")).hexdigest()
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_manifest(version, platform, components):
    """构造 manifest dict：components {name: Path} → {name: {path, sha256}}。

    path 为相对 bundle 根（公共祖先）的相对路径；目录组件用 compute_sha256 目录约定。
    """
    comps = {}
    base = os.getcwd()
    if components:
        base = os.path.commonpath([os.path.abspath(str(p)) for p in components.values()])
    for name, comp_path in components.items():
        cp = Path(comp_path)
        rel = os.path.relpath(os.path.abspath(str(cp)), base)
        comps[name] = {"path": rel, "sha256": compute_sha256(cp)}
    return {"version": version, "platform": platform, "components": comps}


def _fetch_embedded_python(platform, bundle):
    """（可选）下载嵌入式 Python 到 bundle/python/。失败 → PackOfflineError。"""
    import urllib.request

    py_dir = bundle / "python"
    py_dir.mkdir(parents=True, exist_ok=True)
    if platform == "windows-x86_64":
        url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    else:
        url = "https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz"
    dest = py_dir / Path(url).name
    try:
        urllib.request.urlretrieve(url, str(dest))
    except Exception as exc:
        raise PackOfflineError(f"嵌入式 Python 下载失败: {exc}") from exc
    return dest


def pack_offline(version, platform, out_dir, repo_dir, include_python=False, include_pillow=False):
    """打包主流程，返回 bundle 目录 Path（out_dir/agate-{version}-{platform}）。"""
    out = Path(out_dir)
    bundle = out / f"agate-{version}-{platform}"
    bundle.mkdir(parents=True, exist_ok=True)
    agate_dir = bundle / "agate"
    wheels_dir = bundle / "wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)

    try:
        _run(["git", "worktree", "add", str(agate_dir), version], cwd=repo_dir)
    except (subprocess.CalledProcessError, OSError) as exc:
        raise PackOfflineError(f"版本 tag {version} 检出失败: {exc}") from exc

    pip_platform = _PIP_PLATFORMS.get(platform)
    if not pip_platform:
        raise PackOfflineError(f"不支持的平台标签: {platform}（应为 linux-x86_64 / windows-x86_64）")

    cmd = [
        "pip", "download", "--platform", pip_platform, "--python-version", "311",
        "--only-binary=:all:", "--no-deps", "-d", str(wheels_dir), "pyyaml",
    ]
    if include_pillow:
        cmd.append("Pillow")
    try:
        _run(cmd)
    except (subprocess.CalledProcessError, OSError) as exc:
        raise PackOfflineError(f"pip download 失败（网络或平台 wheel 不可得）: {exc}") from exc

    pyyaml_wheels = list(wheels_dir.glob("pyyaml-*.whl"))
    if not pyyaml_wheels:
        raise PackOfflineError(f"pyyaml wheel 缺失（--platform {pip_platform} 未拉到 wheel）")
    components = {"agate": agate_dir, "wheels": wheels_dir, "pyyaml": pyyaml_wheels[0]}
    if include_pillow:
        pillow_wheels = list(wheels_dir.glob("Pillow-*.whl"))
        if not pillow_wheels:
            raise PackOfflineError("Pillow wheel 缺失")
        components["pillow"] = pillow_wheels[0]
    if include_python:
        components["python"] = _fetch_embedded_python(platform, bundle)

    manifest = build_manifest(version, platform, components)
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return bundle


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    version = None
    platform = "linux-x86_64"
    out_dir = os.getcwd()
    repo_dir = _DEFAULT_REPO
    include_python = False
    include_pillow = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--platform":
            i += 1
            if i >= len(args):
                sys.stderr.write("agate-pack-offline: --platform 缺少取值\n")
                return 2
            platform = args[i]
        elif a == "--outdir":
            i += 1
            if i >= len(args):
                sys.stderr.write("agate-pack-offline: --outdir 缺少取值\n")
                return 2
            out_dir = args[i]
        elif a == "--repo":
            i += 1
            if i >= len(args):
                sys.stderr.write("agate-pack-offline: --repo 缺少取值\n")
                return 2
            repo_dir = args[i]
        elif a == "--include-python":
            include_python = True
        elif a == "--include-pillow":
            include_pillow = True
        elif a.startswith("--"):
            sys.stderr.write(f"agate-pack-offline: 未知选项 {a}\n")
            return 2
        else:
            version = a
        i += 1

    if not version:
        sys.stderr.write("agate-pack-offline: 缺少版本参数（如 v0.48.0）\n")
        return 2

    try:
        bundle = pack_offline(
            version, platform, out_dir, repo_dir,
            include_python=include_python, include_pillow=include_pillow,
        )
    except PackOfflineError as exc:
        sys.stderr.write(f"agate-pack-offline: {exc}\n")
        return 1
    print(f"打包完成: {bundle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
