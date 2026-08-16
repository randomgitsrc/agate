---
phase: P4
task_id: TAG0008
type: implementation
parent: P2-design.md
trace_id: TAG0008-P4R-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P4 实现记录 — 批次 resolve-chain（P2 dispatch_plan 批次 1/3）

> 实现范围：agate-resolve.py / agate_common.py 解析集成 / resolve-entry.py / 3 hook 薄壳 /
> install-hook.py / agate-summary.py / 3 内联脚本归口。验收 = P3 三个测试文件全绿。

implementation_dir: agate/scripts/

## 1. 改动清单

| 文件 | 改动 | 关联 |
|------|------|------|
| `agate/scripts/agate-resolve.py`（新） | 版本解析 CLI：env 最高 → 项目声明 → current → legacy；输出 AGATE_ROOT/AGATE_VERSION/AGATE_REASON；终态失败 exit 1 | BDD-9~14/30 + fail-closed |
| `agate/scripts/resolve-entry.py`（新） | hook 固定解析入口：gate-name→gate py 映射；env 覆盖最高；解析失败警告 + 回退 current；gate 缺失 fail-closed | BDD-12~18 |
| `agate/scripts/agate_common.py` | 新增 `_find_project_declaration` / `_resolve_pointer_chain` / `_resolve_version_info` / `resolve_version_root` / `resolve_hook_root`；`resolve_agate_root` 改经 `resolve_hook_root`（env → 项目/current → 脚本路径上溯 + `.agate-root` 标记，既有语义加法） | I-5, §4.1 |
| `agate/scripts/pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh` | AGATE_ROOT 自定位改经 resolve-entry exec 对应版本 py；入口根用 `ENTRY_ROOT`（见 §4 设计修正） | BDD-15~19 |
| `agate/scripts/install-hook.py` | 装固定解析入口链：校验 `resolve-entry.py` 存在（缺失仅 WARNING 不阻断）；复制模式 `.agate-root` 标记保留；文案更新 | BDD-15/19 |
| `agate/scripts/agate-summary.py` | 语义迁移：显示项目解析版本 + 原因 + AGATE_ROOT（复用 resolve_version_root）；移除 git-describe 依赖（worktree `.git` 是文件非目录时旧逻辑失效） | BDD-20/21, §4.6 |
| `agate/scripts/agate-next-card.py` / `agate-inject-card.py` / `agate-render-dispatch-prompt.py` | 内联 `_agate_root()/_resolve_agate_root()` 归口 `agate_common.resolve_agate_root` | §4.4 |

## 2. 测试修正（P3 测试文件 bug 修正，非迁就实现）

> P3 验收测试中发现 3 处测试代码缺陷——其自身断言/设计文档自洽，但 fixture 构造与之矛盾，任何正确实现都无法使其变绿。修正均不削弱断言，仅对齐 P3 设计文档声明的行为。

1. `agate/tests/unit/test_hook_resolve_entry.py::_make_home`：stub marker 计算 `"GATE-V" + v.replace(".", "")` 对 `v="v0.43.0"` 得 `GATE-Vv0430`，与测试自身断言 `GATE-V043`/`GATE-V044` 及 P3-test-cases-resolve.md 声明的标记矛盾 → 改为 `"GATE-V" + v[1:].rsplit(".", 1)[0].replace(".", "")`（`v0.43.0 → GATE-V043`）。不改断言。
2. `agate/tests/integration/test_pre_commit_hook.py::test_agate_root_self_locate_worktree`：fake 安装根只复制了薄壳 + gate py，缺新架构 hook 链必须的 resolve-entry.py + agate_common.py → 补齐（hook 薄壳经 resolve-entry 解析后 exec gate，是 P2 设计 §4.3 的既定架构变更，非实现权宜）。
3. `agate/tests/unit/test_dispatch_context_warning.py::_FAKE_SCRIPTS`：同上补 `resolve-entry.py`（该测试直接跑薄壳，fake 根须含解析入口）。

## 3. [DESIGN_GAP] 声明（自主决策，供主 Agent/architect 审查）

[DESIGN_GAP: P2 §4.1 层 4「legacy 软链兜底」仅用于 agate-resolve/summary；resolve-entry（hook 链）与 resolve_agate_root 的终态兜底用「脚本路径上溯 + .agate-root 标记」而非 ~/.agate legacy 解析——否则 copy 模式集成测试（.agate-root 指向 worktree）会被真实 ~/.agate 稳定版软链劫持，且真实 legacy 安装下脚本路径上溯与 legacy 目标等价。]

[DESIGN_GAP: P2 §4.4「3 内联脚本统一归口 agate_common.resolve_agate_root」保留了 agate_common 不可用（脚本被独立复制、agate_common 不在同目录）时的内联兜底（env → 脚本路径上溯）——既有 test_agate_next_card.py 的 standalone-copy 场景（test_nc_root_2 等）只复制脚本本身，无 agate_common 可 import；兜底仅在 import 失败时生效，不改变归口主路径。]

[DESIGN_GAP: 3 hook 薄壳改用 `ENTRY_ROOT`（非 `AGATE_ROOT`）承载自定位结果——bash 从环境继承的 AGATE_ROOT 具 exported 属性，薄壳内 `AGATE_ROOT=${AGATE_ROOT:-...}` 赋值会保留该属性并泄漏给 resolve-entry，使其 env 覆盖恒触发而绕过项目版本解析；换名后用户显式 AGATE_ROOT env 仍原样透传（BDD-12 语义保留）。]

## 4. 自查结果

- 本批 3 个测试文件：`test_agate_version_resolve.py` / `test_agate_summary.py` / `test_hook_resolve_entry.py` —— **17 passed**（含参数化）。
- 相关回归（agate_common/薄壳/归口改动影响面）：unit 全量 679 passed（仅 install/offline 批 19 个预期红——`agate-install.py`/`agate-pack-offline.py`/`install-offline.py` 属后续批次未实现）；integration 85 passed；regression 17 passed。
- 质量门：shellcheck 3 薄壳 0 error；ruff 改动 py 0 error；count-tests 818 ≥ 749。

## 5. 未解决问题

- 无未解决的 [DESIGN_GAP]（以上 3 条已声明，待主 Agent 审查追加 [DESIGN_GAP_REVIEWED]）。
- install/offline 批次测试红属预期（依赖其对应脚本实现，不在本批范围）。

## 6. rev2 修复记录（评审 rejected 后，CRITICAL-1 归属本批）

> P4-review.md 阻断项 1（CRITICAL-1 指针解析 isdir 短路）在 resolve-chain 批 `agate_common.py`。

### 修复内容

- `agate_common.py::_resolve_pointer_chain`：解析顺序改为**先判 `os.path.islink` 再判 `os.path.isdir`**。软链指向版本目录时 `isdir` 恒为 True，旧实现把软链路径自身当终态（返回 `~/.agate/current`/`latest`），version=basename 变 "current"/"latest" 而非实际版本号。新实现：islink → readlink 目标名继续追（相对目标递归 / 绝对目标 normpath 后递归），最终落点 = 实际版本目录名。
- 关联（agate-install 批同源）：`agate-install.py::_resolve_pointer` 同样先判 islink——`_pointer_targets` 才能捕获到真实版本名，`_repair_pointers` 的 `before != removed_version` 匹配才会触发（BDD-5 红线修复）。

### 补测试（平台无关：软链用例 skip 声明）

| 测试 | 文件 | 断言 |
|------|------|------|
| `test_bdd_5b_uninstall_pointed_version_repoints_symlink` | test_agate_version_install.py | 软链布局卸载被 latest/current 指向的版本 → 指针重指 v0.43.0（不悬空），worktree 已移除（Linux skip） |
| `test_bdd_11b_symlink_pointer_shows_actual_version` | test_agate_version_resolve.py | 软链布局 current→latest→v0.44.0 → AGATE_VERSION=v0.44.0（非 current/latest） |
| `test_bdd_21b_symlink_pointer_shows_actual_version` | test_agate_summary.py | 软链布局 summary 显示"版本：v0.44.0" |

### 自查

- 相关测试文件：`test_agate_version_install.py` / `test_agate_version_resolve.py` / `test_agate_summary.py` 全绿。
- 全量 pytest：823 passed（含新增软链用例），0 ERROR（check-protocol-consistency），count-tests 825 ≥ 749。

[PROD_NOT_TOUCHED]
