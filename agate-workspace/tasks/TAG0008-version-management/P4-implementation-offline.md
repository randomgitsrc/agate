---
phase: P4
task_id: TAG0008
type: implementation
parent: P2-design.md
trace_id: TAG0008-P4O-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P4 实现记录 — 批次 offline（agate-pack-offline.py + install-offline.py）

## implementation_dir

`implementation_dir: agate/scripts/`

## 本次改动

批次 offline（P2 dispatch_plan 批次 3/3），新建 2 个脚本（resolve-chain 批文件未修改）：

1. `agate/scripts/agate-pack-offline.py`（外网打包器，BDD-22~24）
   - `compute_sha256(path) -> str`：文件=内容 sha256（64 hex）；目录=相对路径字典序排序逐文件 hash 拼接再整体 hash（与 install 侧同约定）
   - `build_manifest(version, platform, components) -> dict`：components `{name: Path}` → `{path, sha256}`，path 相对 bundle 根（公共祖先）
   - `pack_offline(version, platform, out_dir, repo_dir, include_python=False, include_pillow=False) -> Path`：
     - `git worktree add <bundle>/agate <tag>` → `pip download --platform <pip平台> --python-version 311 --only-binary=:all: --no-deps -d <bundle>/wheels pyyaml [Pillow]` → 校验 wheel 存在 → 可选嵌入式 Python → 写 manifest.json
     - 平台标签映射：`linux-x86_64 → manylinux_2_17_x86_64`、`windows-x86_64 → win_amd64`（P2 §7 MV 实测值）
     - 失败路径（BDD-24）：tag 不存在 / pip download 网络失败 / wheel 缺失 → 抛 `PackOfflineError`，不产 manifest.json
   - `PackOfflineError(RuntimeError)`；`main(argv=None) -> int` 成功 0，失败 1 + stderr 写明原因
   - 缺版本参数 → 2；未知选项 → 2

2. `agate/scripts/install-offline.py`（内网安装器，BDD-25~29）
   - `load_manifest` / `get_current_platform`（win32→windows-x86_64，x86_64/amd64→linux-x86_64）/ `check_platform`
   - `verify_checksums(manifest, bundle_dir) -> list`：不匹配组件名列表（目录组件用同约定）
   - `install_wheels(bundle_dir, skip=())`：`pip install --no-index --find-links <bundle>/wheels pyyaml [Pillow]`；`"pillow" in skip` 时不装 Pillow（BDD-29）
   - `install_bundle(manifest_path, bundle_dir, dest_root, skip=())`：复制 bundle → `dest_root/v{version}/` → 写 `.installed-version` → current 指针（Linux 软链 / Windows 或 `AGATE_HOOK_COPY_MODE=1` 复制指针文件 + `.agate-root` 标记含绝对路径）；skip 含 "python" 时排除 python 组件顶层目录
   - `main(argv=None) -> int`：读 manifest → 平台核对（不匹配警告含两平台值 + 拒绝 exit 1，BDD-25）→ checksum 校验（不匹配列出组件 + 拒绝 exit 1，BDD-26）→ 装 wheels（skip 生效）→ install_bundle → 0

## 自查结果

- 命令：`python3 -m pytest agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py -q --tb=no`
- 结果：**11 passed**（BDD-22~29 全部绿灯；BDD-24 三失败场景 O-3/O-4/O-5、BDD-28 平台变体 O-9b 在内）
- ruff：`~/.venvs/agate-dev/bin/ruff check` 两脚本全部通过（修过 PLW2901 循环变量覆盖 + RUF100 无用 noqa）
- 未实际访问网络 / 未实际 git worktree add / 未实际 pip（测试已 mock）

## 未解决的 [DESIGN_GAP]

[DESIGN_GAP: P3-test-cases-offline.md 声明"pack 与 install 应共享 agate_common 工具函数（依赖 resolve-chain 批）"，但 resolve-chain 批交付的 agate_common.py（438 行）未含 sha256/目录 hash 工具；本批约束"只新建 2 个脚本、不得修改 agate_common.py"，故在 pack/install 两侧各自实现了**相同约定**的 compute_sha256（目录=排序逐文件 hash 拼接再整体 hash），未通过 agate_common 共享。若后续期望共享，需在 agate_common.py 补一个 hash 工具并让两侧 import]

## 记录

- 未发现 [SCOPE_GAP] / [SCOPE+]
- 未触发生产环境；双工作区纪律遵守（只动 worktree agate/scripts/ 下 2 个新文件）`[PROD_NOT_TOUCHED]`

## 追加：rev2 修复记录（评审 rejected 后）

> P4-review.md 阻断项 2/3（CRITICAL-2 安装清单忽略 manifest / CRITICAL-3 manifest 字段未校验→路径穿越）
> 均归属本批 install-offline.py。

### CRITICAL-2：install_wheels 从 manifest components 推导安装清单

- 旧实现：Pillow 仅由 `--skip-pillow` 控制，与 manifest `components` 是否含 pillow 无关。
  `agate-pack-offline.py` 默认（不含 `--include-pillow`）的最小 bundle 在无 Pillow 机器上
  `--no-index` 安装 Pillow 必失败（pip: No matching distribution found）→ 默认流断裂。
- 新实现：`install_wheels` 读 manifest，`components` 含 "pillow" 才装 Pillow；"pyyaml" 组件必有
  → 默认装 pyyaml。`--skip-pillow` 只过滤已包含项（BDD-29 语义：skip 覆盖包含项，未包含项不装）。

### CRITICAL-3：manifest 字段校验（防路径穿越）

- 新增 `_validate_manifest(manifest, bundle_dir)`：
  - `version` 套 `^v[0-9]+\.[0-9]+\.[0-9]+$` 正则（同 agate-install `_VERSION_RE`）——旧实现
    `manifest["version"]` 直接作 `dest / version` 目录名，篡改为 `"../../.."` 可把 copytree +
    `.installed-version` 写到 dest_root 之外（写任意用户可写路径）。
  - 组件 `comp["path"]` 拒绝绝对路径与 `..`，用 `os.path.commonpath([bundle, p]) == bundle` 断言
    ——旧实现 `verify_checksums` 直接 `bundle / comp["path"]`，`..` 可越界读 bundle 外文件
    （哈希比对作可探测 oracle）。
- 接线：`main` 读 manifest 后立即校验（fail-closed，先于 checksum/pip）；`verify_checksums` 与
  `install_bundle` 内部也各自校验（防御纵深）；`main` 错误捕获补 `ValueError`。

### 补测试（test_install_offline.py）

| 测试 | 覆盖 |
|------|------|
| `test_bdd_29b_no_pillow_bundle_installs_pyyaml_only` | 无 Pillow bundle + 无 skip → 走 install_wheels 真实路径，pip argv 只含 pyyaml、无 Pillow，安装成功（CRITICAL-2） |
| `test_manifest_version_traversal_rejected` | version=`../../../../pwned` → main 非 0、stderr 含 version、不写出 dest_root（CRITICAL-3 写路径） |
| `test_manifest_component_path_traversal_rejected` | 组件 path=`../secret.txt` → main 非 0、stderr 含 path、不安装（CRITICAL-3 越界读） |
| `test_manifest_absolute_path_rejected` | 组件 path=`/etc/hostname` → 拒绝（绝对路径） |

### 自查

- `test_install_offline.py`：12 passed（8 原有用例 + 4 新增）。
- 全量 pytest：823 passed 无回归；ruff 0 违规；consistency 0 ERROR。

[PROD_NOT_TOUCHED]
