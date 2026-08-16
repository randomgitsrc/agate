---
phase: P4
task_id: TAG0008
type: implementation
parent: P2-design.md
trace_id: TAG0008-P4I-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P4 实现 — agate-install.py（安装 / 卸载 / 环境探测）

> 批次：install（P2 dispatch_plan 批次 2/3）。承接 BDD-1~8，验收测试 test_agate_version_install.py（8 用例）。
> implementation_dir: agate/scripts/

## 产出

- **新增** `agate/scripts/agate-install.py`（本批唯一代码改动；resolve-chain 批文件只读复用，未修改）。

## 实现摘要（对照 P2 §4.5 与 BDD-1~8）

| BDD | 实现位置 | 关键行为 |
|-----|----------|----------|
| BDD-1 | `_cmd_install(version=None)` → `_latest_tag` + `_write_pointer` | 无参 = 最新发布 tag（`git tag --sort=-version:refname` 过滤 `vX.Y.Z`）worktree + `latest`→版本 + `current`→`latest` |
| BDD-2 | `_worktree_add` | `git -C repo worktree add --detach <dir> <tag>`，检出 tag 快照 |
| BDD-3 | `_install_version` | 幂等预判：`os.path.lexists(version_dir)` 已存在即跳过（不依赖 git 报错，MV exit 128 已核实） |
| BDD-4 | `_write_pointer(current, "latest")` | `current` 默认 → `latest`（指针链） |
| BDD-5 | `_cmd_uninstall` + `_repair_pointers` | worktree remove（失败 `--force` 兜底）→ rmtree → prune → 指针清理/重指（卸载前捕获指针解析目标，防悬空） |
| BDD-6 | `_find_references` | 引用保护：扫描 `$HOME` 下 `.agate-version` 声明该版本 → 拒绝卸载（exit 1 + 列出引用项目） |
| BDD-7 | `_cmd_check` | 探测 python3（probe_python）/ pyyaml（probe 到的 python 子进程 `import yaml`）/ git / bash，全齐 exit 0 |
| BDD-8 | `_cmd_check` + `_fix_guidance` | 缺项非 0 + 分平台修复指引（Linux `pip install pyyaml`；Windows Python/PATH/PYTHONUTF8/Git for Windows） |

## 关键设计点

1. **指针形态**：POSIX `os.symlink` 软链（`latest`→版本名、`current`→`latest` 相对软链）；Windows（`os.name == "nt"`）复制模式文本指针（内容 = 目标名）。测试侧 `_resolve_pointer` 兼容两种形态。
2. **repo 单克隆**：`~/.agate/repo` 已有 `.git` 直接复用；`git clone <AGATE_REPO_URL|默认上游>` 首次克隆，失败 fail-closed exit 1。
3. **卸载引用扫描限流**：深度 ≤ 4 + 跳过隐藏/.agate/.git/node_modules 等目录 + mtime 窗口 365 天（详见 DESIGN_GAP 2）。
4. **指针清理防悬空**：在 worktree remove 前用 `_pointer_targets` 捕获 latest/current 解析落点；卸载后按「latest 先、current 后」重指最新有效版本或清除。
5. **agate_common 复用**：`from agate_common import probe_python, run_git`（只读）；pyyaml 缺失时 `(ImportError, SystemExit)` 降级本地实现（install-hook.py 同款先例），保证 `--check` 在无 pyyaml 环境仍能输出修复指引。
6. **git 探测**：`--check` 的 python 探测走 `probe_python()`（shutil.which 用子进程 PATH）而非 `sys.executable`——BDD-8 用 venv 前置 PATH 使 `import yaml` 失败，正确命中 pyyaml 缺失。

## 红线核对

- [x] 重复安装幂等（BDD-3）：先判版本目录存在，不依赖 git 报错。
- [x] 卸载引用保护（BDD-6）：项目仍引用 → 拒绝卸载 + 警告（stderr + exit 1）。
- [x] 卸载清理指针（BDD-5）：latest/current 曾指向被删版本 → 重指有效版本或清除（卸载前捕获，防悬空）。
- [x] --check 缺项 exit 非 0 + 分平台修复指引。
- [x] 只新建 agate-install.py；resolve-chain 批文件（agate_common / resolve-entry / hook / install-hook / summary / 3 内联脚本）零修改。

## 自查结果

- 命令：`python3 -m pytest agate/tests/unit/test_agate_version_install.py -q`
- 结果：**8 passed**（test_bdd_1~8 全绿；自查通过 ≠ P5 gate）。
- `ruff check agate/scripts/agate-install.py`：通过（0 违规）。
- `python3 -m py_compile`：通过。

## DESIGN_GAP（实现中自主决策，供主 Agent 审查）

[DESIGN_GAP: P2 §4.5 未指明 repo URL 来源（P3 §5 备注确认），AGATE_REPO_URL 未设置时默认采用仓库 canonical URL https://github.com/randomgitsrc/agate]
[DESIGN_GAP: P2 §4.5 "mtime 合理限流" 未给具体参数，实现采用深度 ≤4 + 跳过隐藏/.agate/.git 等目录 + mtime 窗口 365 天]
[DESIGN_GAP: P2 §4.5 未给 worktree remove 失败策略，实现采用 remove 失败后 --force 兜底 + rmtree + git worktree prune]
[DESIGN_GAP: P2 §4.5 "最新发布 tag" 未给确定方法，实现采用 git tag --sort=-version:refname 过滤 vX.Y.Z 取首项]

## SCOPE 标注

- [SCOPE_GAP]：无——本批 prompt 覆盖 P2 声明范围（仅 agate-install.py）。
- SCOPE+ 声明：本批无新隐含需求（无行首 [SCOPE+] 标记）。
- 测试断言与 BDD 矛盾：无。

## 环境隔离

[PROD_NOT_TOUCHED] — 测试全程 HOME 重定向到 pytest tmp_path；未触碰真实 ~/.agate / 主 checkout / 生产环境。

## 追加：rev2 修复记录（评审 rejected 后）

> P4-review.md 阻断项 1（CRITICAL-1）同时覆盖 agate-install.py 的 `_resolve_pointer`（与
> agate_common `_resolve_pointer_chain` 同源缺陷），本批补相应修复与测试。

### 修复内容

- `agate-install.py::_resolve_pointer`：解析顺序改为**先判 `os.path.islink` 再判 `os.path.isdir`**。
  POSIX 软链指针（latest→v0.48.0、current→latest）指向版本目录时 `os.path.isdir(p)` 恒为 True，
  旧实现直接返回软链路径自身 → `_pointer_targets` 的 basename 变成 "latest"/"current" →
  `_repair_pointers` 的 `before.get(name) != removed_version` 恒匹配不上 → 卸载后 latest/current
  悬空（BDD-5 红线失效，静默破坏项目版本隔离 BDD-16）。新实现 islink 分支 readlink 目标名继续追，
  最终落点 = 实际版本目录名。

### 补测试

- `test_agate_version_install.py::test_bdd_5b_uninstall_pointed_version_repoints_symlink`
  （`os.name == "nt"` 时 skip）：软链布局安装 v0.48.0（latest）+ v0.43.0 → 卸载 v0.48.0 →
  断言 latest/current 均重指到 v0.43.0 且不悬空、worktree 已 prune。

### 自查

- `test_agate_version_install.py`：9 passed（8 原有用例 + 1 新增）。
- 全量 pytest：823 passed 无回归；ruff 0 违规。

[PROD_NOT_TOUCHED]
