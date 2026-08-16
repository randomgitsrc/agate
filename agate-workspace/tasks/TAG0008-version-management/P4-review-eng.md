---
phase: P4
task_id: TAG0008
type: review
parent: P2-design.md
trace_id: TAG0008-P4RE2-20260816
status: approved
created: 2026-08-16
agent: review
---

# P4 实现复核（review 专家，rev2）

> 复核轮：逐条核实上一轮 3 CRITICAL 是否真实修复 + 复核 8 条 INFORMATIONAL 是否仍成立。
> 评审只读，未修改任何代码 `[PROD_NOT_TOUCHED]`。

## 结论摘要

Status: **approved**（3 CRITICAL 全部真实修复并有回归测试；无新增 CRITICAL；8 条
INFORMATIONAL 仍成立但非阻断）。

## 复核证据

实测命令（本 worktree，读代码 + 跑测试）：
- `pytest unit/`（全量）→ **699 passed, 2 skipped**（skip 为平台无关声明场景）
- `pytest test_agate_pack_offline + integration/test_pre_commit_hook + test_dispatch_context_warning` → **54 passed**
- `ruff check` 6 个脚本 → **All checks passed**
- `shellcheck -S warning agate/scripts/*.sh` → **无输出（干净）**
- `check-protocol-consistency.py` → **0 ERROR**（279 WARNING 为既有叙事文件引用，非本次引入）

## CRITICAL 逐条判定

### CRITICAL-1（指针解析 isdir 短路 → 软链布局卸载指针悬空 + 版本号显示错误）— **已修复**

- `agate_common.py:113-151` `_resolve_pointer_chain`：解析顺序改为**先 `os.path.islink`
  再 `os.path.isdir`**（127-139），软链 readlink 目标名继续追（相对目标递归 / 绝对目标
  normpath 后递归），最终落点 = 实际版本目录名；seen 防环保留。已用 /tmp 真实 symlink 布局
  复现：`current→latest→v0.48.0` 解析到 `v0.48.0`（修复前返回 "current"）。
- `agate-install.py:98-126` `_resolve_pointer`：同样 islink 先判（109-112）。`_pointer_targets`
  现能捕获真实版本名，`_repair_pointers` 的 `before != removed_version`（211-227）在卸载被
  指向版本时**匹配触发**（复现：before={'latest':'v0.48.0','current':'v0.48.0'} → REPAIR FIRES）。
- 回归测试（全绿）：
  - `test_bdd_5b_uninstall_pointed_version_repoints_symlink`（install）：软链布局卸载被
    latest/current 指向的 v0.48.0 → 断言 latest/current 重指 v0.43.0 且不悬空、worktree 已移除。
  - `test_bdd_11b_symlink_pointer_shows_actual_version`（resolve）：`AGATE_VERSION=v0.44.0`
    而非 current/latest。
  - `test_bdd_21b_symlink_pointer_shows_actual_version`（summary）：显示"版本：v0.44.0"。
- 平台处理：软链用例 `os.name=="nt"` skip / `pytest.skip` 声明（符合 AGENTS.md 平台无关原则）。

### CRITICAL-2（install-offline 安装清单忽略 manifest → 无 Pillow bundle 默认流失败）— **已修复**

- `install-offline.py:116-135` `install_wheels`：读 manifest `components` 推导安装清单——
  含 "pillow" 组件才装 Pillow；"pyyaml" 必有 → 默认装 pyyaml；skip 只过滤已包含项（BDD-29
  语义对齐）。已实测 pip：空 wheels 目录 + 未装 Pillow 时旧命令必失败（复现过），修复后不再
  尝试 Pillow。
- 回归测试：`test_bdd_29b_no_pillow_bundle_installs_pyyaml_only`（全绿）——无 Pillow bundle
  + 无 skip → 走 install_wheels 真实路径，pip argv 只含 pyyaml、无 Pillow，安装成功。

### CRITICAL-3（manifest 字段未校验 → version 路径穿越写 / component path 越界读）— **已修复**

- `install-offline.py:40-66` 新增 `_validate_manifest`：version 套 `^v[0-9]+\.[0-9]+\.[0-9]+$`
  正则（同 agate-install `_VERSION_RE`）；组件 `comp["path"]` 拒绝绝对路径与 `..`，并用
  `os.path.commonpath([bundle, resolved]) == bundle` 断言（含 symlink 越界兜底）。
- 接线完整（fail-closed）：`main` 读 manifest 后立即校验（214，先于 checksum/pip）、
  `verify_checksums`（103）与 `install_bundle`（155）内部各自校验（防御纵深）；`main` 错误
  捕获补 `ValueError`（239）。
- 回归测试（全绿）：`test_manifest_version_traversal_rejected`（version=`../../../../pwned`
  拒绝、不写出 dest_root）、`test_manifest_component_path_traversal_rejected`（`../secret.txt`
  拒绝）、`test_manifest_absolute_path_rejected`（`/etc/hostname` 拒绝）。

## INFORMATIONAL 复核（8 条仍成立，非阻断，未因修复引入新问题）

1. `resolve_agate_root` 归口后 worktree 开发场景解析到 `~/.agate/current` —— 仍成立（P2 §4.4
   决策，文档待确认）。
2. `_find_references` 跳过 dot 目录 + mtime 365 天窗口 → 引用保护假阴性 —— 仍成立（接受取舍）。
3. 版本化布局 `~/.agate/scripts/` 入口根无显式 provision —— 仍成立（建议后续 ensure-scripts）。
4. `agate-pack-offline` 失败路径 worktree/bundle 残留 —— 仍成立。
5. 指针文件内容未做版本名校验 —— 仍成立（用户可控，低风险）。
6. install-offline 复制模式 `.agate-root` 标记无消费方 —— 仍成立。
7. `agate-summary` guards 来源与解析 root 不一致 —— 仍成立（轻微）。
8. pack 固定 `--python-version 311` 无 install 端核对 + compute_sha256 双实现漂移 —— 仍成立。

> 修复未引入新问题：islink 先判对文本指针/legacy 软链布局无行为回归（current 缺失 → None →
> 正常回退链路）；`_validate_manifest` 对合法 bundle 的 path 均放行（pack 侧 path 全为 bundle
> 内相对路径）；`install_wheels` 空组件清单属畸形 manifest，被 main 的 validate + pip 报错
> fail-closed 覆盖，非合法输入路径。

## 门槛判定

- 3 CRITICAL 全部修复 + 回归测试覆盖 + 全量测试/静态检查/一致性全绿 → **approved**。
- 8 条 INFORMATIONAL 不阻断，留待后续（建议作为 backlog 记录，不入本任务阻塞）。
