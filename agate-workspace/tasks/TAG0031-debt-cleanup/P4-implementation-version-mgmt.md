---
phase: P4
task_id: TAG0031
parent: P3-test-cases-version-mgmt.md
trace_id: TAG0031-P4-version-mgmt-20260904
agent: implementer
created: '2026-09-04'
implementation_dir: agate/scripts/
---

# P4-implementation-version-mgmt.md — 版本管理域（DEBT0002/3/4）实现记录

> 实现目录见 frontmatter `implementation_dir`（脚本改动落在 `agate/scripts/`，文档改动另涉 `agate/UPGRADING.md`）。

## 改动清单

| 文件 | 改动 |
|---|---|
| `agate/scripts/agate_common.py` | 紧邻 `resolve_workspace` 定义之后新增 `compute_sha256(path)`：文件=内容哈希，目录=按 `f.relative_to(p).as_posix()` 字典序排序逐文件 sha256 拼接再整体 sha256，逐字节保留原两侧实现的排序键约定。 |
| `agate/scripts/agate-pack-offline.py` | 删除本地 `def compute_sha256`；改为 `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` + `from agate_common import compute_sha256`（与 `check-events.py`/`check-judge-verdict.py` 既有引导惯例一致）；`build_manifest` 调用点不变。 |
| `agate/scripts/install-offline.py` | 删除本地 `def compute_sha256`；新增模块级探测块——先探测 `import yaml` 是否可用，可用才顺带 `import agate_common` 并暴露同一个 `compute_sha256` 引用（供已装好环境下的直接调用/identity 检查，如全流程回归测试），不可用时保持 `None`；新增 `_ensure_agate_common(bundle_dir, manifest)` 引导函数（每次调用独立重新探测 `import yaml`，不复用模块级探测结果，以支持运行时 yaml 从不可用变可用的场景）：yaml 可用直接 `import agate_common` 返回；不可用时内联 `hashlib.sha256` 校验 manifest 中 pyyaml 组件 checksum，不匹配 → stderr 报错（含 "pyyaml"）+ 返回 `None`，**不执行 pip install**；校验通过才 `pip install --no-index --find-links <bundle>/wheels pyyaml`，成功后 `import agate_common` 返回模块引用。`verify_checksums` 改为先调 `_ensure_agate_common` 拿模块引用，再逐组件调用 `agate_common_mod.compute_sha256(p)`；引导失败时抛 `RuntimeError`，`main()` 捕获并 stderr 输出 + `return 1`。 |
| `agate/scripts/agate-install.py` | `_find_references(home, version)` 返回值由 plain list 改为 `(refs, hit_limit)` 二元组：深度剪枝（`dirs[:] = []` 触发点）或 mtime 超窗跳过均置 `hit_limit=True`。`_cmd_uninstall` 解包后，`hit_limit` 为真时立即 stderr 输出 WARNING（不论 `refs` 是否为空），置于原有"拒绝卸载"判定之前。 |
| `agate/UPGRADING.md` | ④ 新工具小节追加信任边界说明：checksum 校验"防损坏"（传输/存储过程意外错误）、"不防"恶意整包替换，bundle 提供者需"信任"。 |
| `agate/scripts/README.md` | 版本管理表格后追加同口径信任边界说明段落（"防损坏"+"不防"+"信任"三关键词）。 |

## 关键设计决策说明

- **R1 pyyaml 引导时序**：`install-offline.py` 保持零外部依赖启动（不无条件 `from agate_common import compute_sha256`），避免在未装 pyyaml 的机器上于 `verify_checksums`（早于 `install_wheels`）阶段因 `agate_common.py` 模块级 `import yaml` 失败（`sys.exit(1)`）而崩溃。`_ensure_agate_common` 的 checksum-then-pip-install 顺序对 pyyaml 组件同样保证"校验先于安装"。
- **模块级 `compute_sha256` 探测块**：全流程回归测试（`test_offline_bundle_roundtrip.py`）要求 `install_module.compute_sha256 is agate_common.compute_sha256` identity 成立。为兼容此要求同时不破坏 R1 的零依赖启动约束，采用"先探测 `import yaml`，可用才顺带导入 agate_common 暴露引用，不可用保持 None"的模块级探测块；`_ensure_agate_common` 内部逻辑不复用该模块级探测结果，每次独立重新探测（`monkeypatch.setitem(sys.modules, "yaml", None)` 可正确模拟运行时 yaml 从可用变不可用）。此设计点未见于 P2 §1.3 原文字面描述，但与其"先校验后安装"的核心不变量、以及"不能简单 `from agate_common import compute_sha256`"的约束完全一致，属于在既定设计边界内的实现细化。

[DESIGN_GAP: P2-design.md §1.3 R1 未明确说明如何在满足"install-offline.py 不能顶层无条件 import agate_common"约束的同时，让 `test_offline_bundle_roundtrip.py` 的 `install_module.compute_sha256 is agate_common.compute_sha256` identity 断言成立——实现中采用"先探测 yaml 可用性，可用才顺带模块级导入并暴露 compute_sha256 引用，不可用保持 None"的折中方案，`_ensure_agate_common` 独立重新探测不复用该结果，两条路径互不干扰，12 个测试函数（含该 identity 断言）全部转绿验证方案自洽。]

## 测试结果

```
timeout 120 python3 -m pytest agate/tests/unit/test_agate_common.py \
  agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py \
  agate/tests/unit/test_agate_install_uninstall.py \
  agate/tests/regression/test_offline_bundle_roundtrip.py -v
```

结果：**44 passed**（本簇目标 12 个测试函数全部转绿 + 既有 32 项无回归，0 failed，0 errors）。

补充回归确认（关联既有测试文件，无本簇直接改动但依赖同一批脚本）：
`agate/tests/unit/test_agate_version_install.py` + `agate/tests/unit/test_install_hook.py`：**15 passed**，无回归。

## 网络隔离 / 环境隔离自检

- 全程未执行真实 `pip install` / `git worktree` / 网络请求（测试内均 mock `subprocess.run`）。
- 未写入 `~/.agate` 或项目外目录：`[PROD_NOT_TOUCHED]`。

## 新增文件核对表

无新增文件（本簇仅修改既有文件：`agate_common.py`/`agate-pack-offline.py`/`install-offline.py`/`agate-install.py`/`UPGRADING.md`/`scripts/README.md`）。

## 自检

- 代码改动产生真实 diff：`agate/UPGRADING.md`(+2/-1)、`agate/scripts/README.md`(+2)、`agate/scripts/agate-install.py`(+17/-3)、`agate/scripts/agate-pack-offline.py`(+16/-11)、`agate/scripts/agate_common.py`(+14)、`agate/scripts/install-offline.py`(+86/-11)。
- 测试确实运行且全绿（见上方测试结果，非猜测/非未跑先声称）。
- 未改动 `check-pruning.py`/`check-gate.py`（另两簇范围）与 `agate-workspace/debt/tech-debt.md`。
