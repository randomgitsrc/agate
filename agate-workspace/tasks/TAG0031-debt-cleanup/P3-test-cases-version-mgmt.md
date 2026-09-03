---
phase: P3
task_id: TAG0031
parent: P2-design.md
trace_id: TAG0031-P3-version-mgmt-20260904
agent: test-designer
created: '2026-09-04'
test_code_dir: agate/tests/unit/,agate/tests/regression/test_offline_bundle_roundtrip.py
---

# P3-test-cases-version-mgmt.md — 版本管理域（DEBT0002/3/4）测试用例清单

> 并行拆批之一（batch id: `version-mgmt`），只覆盖版本管理域（BDD-1~5），不覆盖测试隔离/
> check-gate.py 健壮性两簇。上游：P2-design.md §1.1 簇 A + §1.3 R1（pyyaml 引导缓解设计）。

## 红灯确认（真实实测记录）

命令：

```
timeout 120s /usr/bin/python3 -m pytest agate/tests/unit/test_agate_common.py \
  agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py \
  agate/tests/unit/test_agate_install_uninstall.py \
  agate/tests/regression/test_offline_bundle_roundtrip.py -v
```

结果：**12 failed, 32 passed, 0 errors**（无 collection error / 语法错误，pre-existing 32 项不受影响）。

逐项红灯类型（均为 B 类：assertion 失败 / 项目内 ImportError·AttributeError·ValueError，非测试代码
自身语法错误）：

| 测试函数 | 文件 | 红灯类型 | 原因 |
|---|---|---|---|
| `test_bdd_1_compute_sha256_file_hash_matches_hashlib` | test_agate_common.py | B（子进程 `from agate_common import compute_sha256` ImportError → returncode=1） | `agate_common.py` 尚无 `compute_sha256` |
| `test_bdd_1_compute_sha256_dir_hash_sorted_relpath_concat` | test_agate_common.py | B（同上） | 同上 |
| `test_bdd_1_compute_sha256_single_definition_in_repo` | test_agate_common.py | B（AssertionError） | 当前命中 2 处（pack/install 各自定义），非 agate_common.py 1 处 |
| `test_bdd_3_upgrading_doc_states_checksum_trust_boundary` | test_agate_common.py | B（AssertionError） | UPGRADING.md 未见"防损坏/不防/信任"字样 |
| `test_bdd_3_scripts_readme_states_checksum_trust_boundary` | test_agate_common.py | B（AssertionError） | scripts/README.md 未见"防损坏/不防/信任"字样 |
| `test_bdd_1_pack_offline_imports_compute_sha256_from_agate_common` | test_agate_pack_offline.py | B（AttributeError: `agate_common` 无 `compute_sha256`） | pack 侧尚未 import 共享实现 |
| `test_bdd_1_verify_checksums_uses_agate_common_compute_sha256` | test_install_offline.py | B（AttributeError，同上） | install 侧尚未接入共享实现 |
| `test_r1_ensure_agate_common_bootstraps_when_yaml_unavailable` | test_install_offline.py | B（AttributeError: module 无 `_ensure_agate_common`） | R1 引导函数未实现 |
| `test_r1_ensure_agate_common_rejects_pyyaml_checksum_mismatch_before_pip_install` | test_install_offline.py | B（AttributeError，同上） | 同上 |
| `test_bdd_4_find_references_and_uninstall_warn_when_scan_limit_hit` | test_agate_install_uninstall.py | B（ValueError: `_find_references` 仍返回 plain list，解包 `(refs, hit_limit)` 二元组失败） | 限流信号尚未落地 |
| `test_bdd_5_find_references_no_warning_within_scan_bounds` | test_agate_install_uninstall.py | B（ValueError，同上） | 同上 |
| `test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change` | test_offline_bundle_roundtrip.py | B（AttributeError: `agate_common` 无 `compute_sha256`） | 迁移锚点断言先行失败，全流程回归尚未接入共享实现 |

## test_code_dir

`agate/tests/unit/`（`test_agate_common.py` / `test_agate_pack_offline.py` /
`test_install_offline.py` / `test_agate_install_uninstall.py`）+
`agate/tests/regression/test_offline_bundle_roundtrip.py`

## 用例清单（1:1 映射 BDD）

### BDD-1：compute_sha256 迁移到 agate_common 后两侧结果一致（DEBT0002）

- `test_bdd_1_compute_sha256_file_hash_matches_hashlib`（`agate/tests/unit/test_agate_common.py`）
  文件 hash = `hashlib.sha256(内容)`，子进程调用（`PYTHONPATH` 指向 `agate/scripts`），不在
  pytest 自身进程内 import agate_common（同文件既有惯例，避免跨用例 sys.path 污染）。
- `test_bdd_1_compute_sha256_dir_hash_sorted_relpath_concat`（同文件）
  目录 hash 遵循现状约定：按 `f.relative_to(p).as_posix()` 字典序排序逐文件 sha256 拼接再整体
  sha256——迁移到 `agate_common` 时排序键必须原样保留（P1 隐含需求表：跨平台路径排序一致性）。
- `test_bdd_1_compute_sha256_single_definition_in_repo`（同文件）
  全仓 grep `^def compute_sha256\(`（`re.MULTILINE`）应只命中 `agate_common.py` 1 处
  （`agate-pack-offline.py`/`install-offline.py` 内不再各自重复定义）。
- `test_bdd_1_pack_offline_imports_compute_sha256_from_agate_common`
  （`agate/tests/unit/test_agate_pack_offline.py`）
  `agate-pack-offline.py` 迁移后 `module.compute_sha256` 应与 `agate_common.compute_sha256` 是
  同一函数对象（identity 检查，而非仅结果相等——强制"共享单实现"而非"逐字节相同的两份实现"）。
- `test_bdd_1_verify_checksums_uses_agate_common_compute_sha256`
  （`agate/tests/unit/test_install_offline.py`）
  用 `agate_common.compute_sha256` 算出的 checksum 应能通过 `install-offline.py` 的
  `verify_checksums` 校验（behavior-level 证据，兼容 R1 引导设计，不假设内部变量命名/挂载方式）。

### BDD-2：hash 合并后 pack → install → 卸载全流程无行为变化（回归，DEBT0002 + R1 机制细化）

- `test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change`
  （`agate/tests/regression/test_offline_bundle_roundtrip.py`，新文件）
  全流程：`pack_offline`（mock `subprocess.run` 的 git worktree add / pip download）→
  `install_module.main`（mock `subprocess.run` 的 pip install，`get_current_platform` mock 匹配
  平台）→ `agate_install_module._cmd_uninstall`（mock `run_git`）。断言：①迁移锚点——pack/install
  两侧 `compute_sha256` 与 `agate_common.compute_sha256` 同一对象；②manifest 各组件 sha256 与
  独立 oracle（现状目录/文件 hash 算法的独立复算，不依赖 agate_common，避免自证）逐字节一致；
  ③安装 exit 0 且 stderr 无 "checksum" 字样误报；④卸载 exit 0 且版本目录被移除。
  网络隔离：全程 mock `subprocess.run`；`HOME` 重定向到 `tmp_path/fakehome`（`_find_references`
  用 `os.path.expanduser("~")`，必须隔离防触碰真实 `~/.agate`）；`dest_root` 落在 `tmp_path` 下。
- R1 两条测试（P2-design.md §1.3「回归覆盖」①②，列入 BDD-2 范围，不新增 BDD 编号）：
  - `test_r1_ensure_agate_common_bootstraps_when_yaml_unavailable`
    （`agate/tests/unit/test_install_offline.py`）
    `monkeypatch.setitem(sys.modules, "yaml", None)` 模拟 yaml 不可导入，mock `subprocess.run`，
    调用 `module._ensure_agate_common(bundle_dir, manifest)`，断言：返回非 `None` 且具备
    `compute_sha256` 属性；`pip install --no-index --find-links .../wheels pyyaml` 确实被调用
    （引导路径可用）。先 `import agate_common` 确保已缓存，规避"yaml 不可用期间 agate_common
    自身模块级 import yaml 触发 sys.exit(1)"的测试顺序副作用。
  - `test_r1_ensure_agate_common_rejects_pyyaml_checksum_mismatch_before_pip_install`
    （同文件）
    构造 manifest 中 pyyaml 组件 `sha256` 字段与真实 wheel 内容不匹配（篡改），mock
    `subprocess.run`，断言：`_ensure_agate_common` 返回 `None` + stderr 含 "pyyaml"；且全程
    mock 的 `subprocess.run` **未被调用**（用"未被调用"断言校验"校验先于安装"这一顺序本身，
    而不只是校验最终结果——BDD-26 字面不变量对 pyyaml 组件同样成立）。

### BDD-3：离线安装文档明示信任边界（DEBT0003）

- `test_bdd_3_upgrading_doc_states_checksum_trust_boundary`（`agate/tests/unit/test_agate_common.py`）
  `agate/UPGRADING.md` 须含"防损坏"+"不防"+"信任"字样（信任边界说明）。
- `test_bdd_3_scripts_readme_states_checksum_trust_boundary`（同文件）
  `agate/scripts/README.md` 须含同样的信任边界说明字样，口径与 UPGRADING.md 一致。

### BDD-4：限流边界命中时输出 WARNING（DEBT0004）

- `test_bdd_4_find_references_and_uninstall_warn_when_scan_limit_hit`
  （`agate/tests/unit/test_agate_install_uninstall.py`，新文件）
  构造深度 5（`a/b/c/d/e`，超出 `_SCAN_MAX_DEPTH=4`）的 `.agate-version` 声明目标版本。
  机制层：`refs, hit_limit = module._find_references(home, version)` 应为 `(refs, hit_limit)`
  二元组，`hit_limit is True`，`refs == []`（漏扫本身即 BDD-4 描述的风险）。行为层：
  `module._cmd_uninstall(agate_home, version)`（mock `run_git`，`HOME` 隔离到 `tmp_path`）stderr
  须含 "WARNING"。

### BDD-5：未命中限流边界时不产生 WARNING 噪音（DEBT0004，边界流）

- `test_bdd_5_find_references_no_warning_within_scan_bounds`（同文件）
  构造深度 1（`home/proj`，远在边界内）的 `.agate-version`。机制层：`hit_limit is False`，
  `refs == [str(proj)]`（真实引用应被正常发现）。行为层：`_cmd_uninstall` 因真实引用拒绝卸载
  （与 WARNING 无关的独立判定），但 stderr **不**含 "WARNING"（限流噪音与"拒绝卸载"提示是两件
  独立的事，只断言前者不出现）。

## 网络隔离 / 环境隔离自检

- 所有 pack/install/uninstall 相关测试均 `mock subprocess.run`（git worktree add/remove、pip
  download、pip install），无真实网络请求、无真实 git/pip 调用。
- `HOME` 环境变量在涉及 `agate-install.py`（`_find_references`/`_cmd_uninstall`）与全流程回归的
  测试中均通过 `monkeypatch.setenv("HOME", str(tmp_path/...))` 重定向，未触碰真实 `~/.agate`。
- `agate-pack-offline.py`/`install-offline.py` 的 `repo_dir`/`dest_root`/`out_dir` 均落在
  `tmp_path` 下，无写入项目外目录。
- 本次未触发任何真实 pack/install/uninstall 写入 `~/.agate`：`[PROD_NOT_TOUCHED]`。

## 已知设计约束（供 P4 implementer 参考，非本文件门槛）

- `install-offline.py` 的 `compute_sha256` 迁移**不能**是简单的模块顶部 `from agate_common
  import compute_sha256`（会破坏离线 bootstrap 前提，见 P2-design.md §1.3 R1）——必须经
  `_ensure_agate_common(bundle_dir, manifest)` 引导，`verify_checksums` 拿到模块引用后再调用
  `agate_common_mod.compute_sha256(p)`。`test_bdd_1_verify_checksums_uses_agate_common_compute_sha256`
  刻意只做行为级验证（不断言 `install_module.compute_sha256` 顶层属性 identity），以兼容这一
  设计约束。
- `agate-pack-offline.py` 无此限制（打包环境不受"未装 pyyaml"约束），可以是直接
  `from agate_common import compute_sha256`，`test_bdd_1_pack_offline_imports_compute_sha256_from_agate_common`
  按此假设做严格 identity 检查。
