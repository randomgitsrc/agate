---
phase: P3
task_id: TAG0008
type: test-cases
parent: P2-design.md
trace_id: TAG0008-P3O-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

# P3 测试用例清单 — 批次 offline（BDD-22~29）

- test_code_dir: agate/tests/unit/
- 测试文件：
  - `agate/tests/unit/test_agate_pack_offline.py`（打包器：manifest / checksum / 失败路径）
  - `agate/tests/unit/test_install_offline.py`（安装器：平台核对 / checksum 校验 / wheels 安装 / 勾选跳过）
- 映射：每条 `#### BDD-NN` → 1 个测试用例，测试名引用 BDD 编号（`test_bdd_22_*` 等）。BDD-24 三失败场景为 1 条 BDD 拆 3 个场景断言（共用同一失败契约）。
- 网络隔离：不实际联网 / 不实际 pip download / 不实际 git worktree add——pack 用假 tag 目录 + 假 wheel（tmp_path），install 的 pip 步骤 mock；checksum 用真实 hashlib 算小文件；平台核对与 checksum 校验是纯逻辑直接测。
- 平台无关：每文件第 1 个用例标 `@pytest.mark.windows_smoke`；hook 指向断言按平台分支（Linux 软链 os.readlink / Windows is_file + .agate-root）；复制模式用 `AGATE_HOOK_COPY_MODE=1` 模拟；无裸 python3（用 conftest `python_exe` 探测）无裸 /tmp（用 `tmp_path`）。

## 被测模块接口契约（P4 implementer 必须提供，测试据此 import）

> 两脚本均为 `agate/scripts/` 下可独立运行的 CLI 脚本，测试用 `importlib` 以模块方式加载（文件名带连字符，不能直接 `import`）。`main(argv) -> int` 供 CLI 行为断言（返回值 = 进程退出码），错误信息写 stderr（`capsys` 断言）。

### `agate/scripts/agate-pack-offline.py`（模块名 agate_pack_offline）

| 成员 | 签名 | 语义 |
|------|------|------|
| `compute_sha256` | `compute_sha256(path) -> str` | hashlib sha256 64 位 hex（标准库） |
| `build_manifest` | `build_manifest(version, platform, components) -> dict` | components: `{name: Path}`（文件或目录）；manifest 含 `version` / `platform` / `components`（每组件 `{path, sha256}` 非空）；sha256 值来自 compute_sha256；目录组件 hash 用"排序逐文件 hash 拼接再整体 hash"约定（见下） |
| `pack_offline` | `pack_offline(version, platform, out_dir, repo_dir, include_python=False, include_pillow=False) -> Path` | 打包主流程：检出 tag 代码 → 按平台拉 wheels（pyyaml 必装 / Pillow 可选）→（可选）嵌入式 Python → 写 manifest.json；**返回 bundle 目录 Path（命名 `out_dir/agate-{version}-{platform}`）**；失败抛 `PackOfflineError`（消息指明失败原因） |
| `PackOfflineError` | `class PackOfflineError(RuntimeError)` | 失败信号（tag 不存在 / pip download 失败 / wheel 缺失） |
| `main` | `main(argv=None) -> int` | CLI 入口；argv 形如 `["v0.48.0", "--platform", "linux-x86_64", "--outdir", "<dir>"]`；成功 0；捕获 PackOfflineError → stderr 写明原因 + 返回非 0；**失败路径不产 manifest.json** |

**pack_offline 内部契约（测试 mock 依据）**：git worktree 检出与 pip download 均经 `subprocess.run` 调用——`git worktree add <bundle>/agate <tag>` 与 `pip download --platform <platform> --python-version 311 --only-binary=:all: --no-deps -d <bundle>/wheels pyyaml [Pillow]`。任一步失败（CalledProcessError / OSError / 非 0 返回码）→ 抛 `PackOfflineError`；pip download 后须校验 `wheels/` 含所需 wheel，缺失 → `PackOfflineError`（消息含 "wheel"）。

**目录组件 sha256 约定（build_manifest 与 install 侧 verify_checksums 必须一致）**：对目录内全部文件按相对路径字典序排序，逐一 `sha256(file_bytes)` 得 hex，拼为一条长串后整体 `sha256`。pack 与 install 应共享 agate_common 工具函数（依赖 resolve-chain 批）。

### `agate/scripts/install-offline.py`（模块名 install_offline）

| 成员 | 签名 | 语义 |
|------|------|------|
| `load_manifest` | `load_manifest(manifest_path) -> dict` | 读 manifest.json |
| `get_current_platform` | `get_current_platform() -> str` | 返回当前机器平台标签（`linux-x86_64` / `windows-x86_64`）；main 经它核对平台（测试可 mock.patch.object 替换） |
| `check_platform` | `check_platform(manifest_platform, current_platform) -> bool` | 平台核对纯逻辑；True=匹配 |
| `verify_checksums` | `verify_checksums(manifest, bundle_dir) -> list` | 逐组件按 manifest path 定位、重算 sha256 比对；返回不匹配组件名列表（空 = 全过）；目录组件用共享目录 hash 约定 |
| `install_wheels` | `install_wheels(bundle_dir, skip=()) -> None` | `pip install --no-index --find-links <bundle>/wheels pyyaml [Pillow]` 经 subprocess.run；skip 含 "pillow" 时不装 Pillow |
| `install_bundle` | `install_bundle(manifest_path, bundle_dir, dest_root, skip=()) -> None` | 复制 bundle 内容到 `dest_root/v{version}/` → 写 `dest_root/v{version}/.installed-version`（内容=版本号）→ 建 `dest_root/current` 指针（Linux 软链 → v{version} 目录 / Windows 或 `AGATE_HOOK_COPY_MODE=1`：复制指针文件 + `dest_root/.agate-root` 标记文件含目标目录绝对路径） |
| `main` | `main(argv=None) -> int` | CLI 入口；argv 形如 `["<bundle_dir>", "--dest-root", "<dir>", "--skip-python", "--skip-pillow"]`；流程：读 manifest → `check_platform(manifest.platform, get_current_platform())` 不匹配 → stderr 警告（**须含 manifest 平台值与当前机器平台**）+ 返回非 0 + 不安装 → `verify_checksums` 不匹配 → stderr 列出被篡改组件 + 返回非 0 + 不安装 → 装 wheels（skip 生效）→ `install_bundle` → 返回 0 |

## 测试用例

| 编号 | BDD 归属 | 测试名 | 场景（Given / When / Then 要点） | 关键 mock / 数据 |
|------|----------|--------|----------------------------------|------------------|
| O-1 | BDD-22 | `test_bdd_22_bundle_manifest` | Given 外网 + repo 有 tag；When `pack_offline("v0.48.0","linux-x86_64",out,repo)`；Then bundle 目录含 agate 代码 + wheels/ + manifest.json；manifest 含 `platform: linux-x86_64` 与各组件 sha256 | git checkout / pip download 均 mock（假 tag 目录 + 假 wheel 文件），checksum 真实 hashlib |
| O-2 | BDD-23 | `test_bdd_23_manifest_fields_checksum` | Given O-1 已打包；When 读 manifest.json；Then platform 字段 == 打包时 `--platform` 值；每组件 sha256 非空且 == 文件真实 hashlib 值（64 hex） | 真实 hashlib 比对 wheel 文件 |
| O-3 | BDD-24① | `test_bdd_24_fail_tag_missing` | Given tag 不存在；When `main(["v0.99.0","--platform","linux-x86_64"])`；Then 退出非 0 + stderr 指明版本/tag 原因 + 不产 manifest | mock `_checkout_tag` 抛 `PackOfflineError`；capsys 断言 stderr |
| O-4 | BDD-24② | `test_bdd_24_fail_pip_network` | Given pip download 网络失败；When 同上；Then 退出非 0 + stderr 指明网络/下载原因 + 不产可用 bundle | mock subprocess.run（pip）抛网络错误 → PackOfflineError |
| O-5 | BDD-24③ | `test_bdd_24_fail_wheel_missing` | Given 目标平台 wheel 缺失；When 同上；Then 退出非 0 + stderr 指明 wheel 缺失 + 不产 manifest | mock pip download 产出空 wheels/ 或无目标 wheel |
| O-6 | BDD-25 | `test_bdd_25_platform_mismatch_reject` | Given manifest platform=`linux-x86_64`、本机 windows-x86_64；When `main`；Then stderr 含 `linux-x86_64` 与当前机器平台 + 退出非 0 | `check_platform` 传参对照；capsys 断言警告内容；不实际装 |
| O-7 | BDD-26 | `test_bdd_26_checksum_mismatch_reject` | Given bundle 内某组件文件被篡改；When `main`；Then 退出非 0 + stderr 指明被篡改组件名 + 拒绝安装 | 篡改 wheel 文件一个字节 → verify_checksums 返回该组件名 |
| O-8 | BDD-27 | `test_bdd_27_wheels_offline_install` | Given 内网无互联网、bundle 含 wheels/；When `install_wheels`；Then subprocess 收到 `pip install --no-index --find-links wheels/` 且包含 pyyaml（含 Pillow 时含 pillow） | mock subprocess.run 捕获 argv 断言标志位 |
| O-9 | BDD-28 | `test_bdd_28_version_dir_hook_verify` | Given 各步骤通过；When `install_bundle(..., dest_root)`；Then `dest_root/v0.48.0/` 存在 + agate 代码已复制 + `.installed-version` == v0.48.0 + `current` 指针就位（Linux 软链 os.readlink / Windows 复制 + `.agate-root`） | 假 bundle（含 agate 代码 + manifest）；平台分支断言 |
| O-9b | BDD-28（平台变体） | `test_bdd_28b_copy_mode_hook` | `AGATE_HOOK_COPY_MODE=1` 模拟 Windows 复制模式：current 为文件 + `.agate-root` 标记含目标目录 | monkeypatch.setenv("AGATE_HOOK_COPY_MODE","1")（复用 test_install_hook.py 先例） |
| O-10 | BDD-29 | `test_bdd_29_skip_flags` | Given bundle 含 Pillow；When `main([...,"--skip-python","--skip-pillow"])`；Then 跳过对应安装步骤（pip argv 无 Pillow）、不报错（stderr 空）、退出 0 | mock subprocess.run 断言安装 argv；get_current_platform mock 匹配 |

> 用例数：**11 个测试用例**（8 条 BDD；BDD-24 三失败场景拆 3 用例 O-3/O-4/O-5 同编号映射；BDD-28 平台变体 O-9b 为补充用例）。

## 红灯自检记录

- 自跑命令：`python3 -m pytest agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py -q --tb=no`
- 预期：全部红灯，失败原因 = 被测模块未实现（helper 抛 ModuleNotFoundError"被测模块未实现: agate-pack-offline.py / install-offline.py"）→ B 类
- 结果：见 P3-progress.md（self-run 段）

## 平台无关核对

- [x] 无裸 `python3`（仅测试运行自跑用；测试内部用 conftest `python_exe` fixture，`python3|python` 探测语义）
- [x] 无裸 `/tmp`（全部 `tmp_path`）
- [x] symlink 断言平台分支（Linux os.readlink / Windows is_file）
- [x] 每文件第 1 用例 `@pytest.mark.windows_smoke`
- [x] 复制模式用 `AGATE_HOOK_COPY_MODE=1` 模拟（复用 test_install_hook.py 先例）
