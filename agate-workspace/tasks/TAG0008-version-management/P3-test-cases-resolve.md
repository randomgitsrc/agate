---
phase: P3
task_id: TAG0008
type: test-cases
parent: P2-design.md
trace_id: TAG0008-P3R-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

# P3 测试用例 — 批次 resolve-chain（BDD-9~21/30/31）

> 批次范围（dispatch-context 约束）：agate-resolve / agate_common 解析集成 / resolve-entry /
> 3 hook 薄壳 / install-hook / agate-summary / 3 内联脚本归口的测试设计。**只写本批测试**，
> 不碰 install（BDD-1~8）与 offline（BDD-22~29）批次的测试文件。

test_code_dir: agate/tests/unit/

## 1. BDD 映射（1:1，测试名引用 BDD 编号）

| BDD | 测试（文件名: 函数名） | 断言要点 | 预期（P3） |
|-----|------------------------|----------|-----------|
| BDD-9 | test_agate_version_resolve.py: test_bdd_9_project_lock | `.agate-version` 声明 v0.43.0 → AGATE_ROOT=v0.43.0 目录 + 版本号 | 红灯（模块缺失） |
| BDD-10 | test_agate_version_resolve.py: test_bdd_10_walk_up_from_cwd | cwd 为子目录时向上查找命中 | 红灯 |
| BDD-11 | test_agate_version_resolve.py: test_bdd_11_no_decl_fallback_current | 无声明 → current→latest→v0.44.0 + 原因"current" | 红灯 |
| BDD-12 | test_agate_version_resolve.py: test_bdd_12_env_override | AGATE_ROOT env 覆盖项目声明，优先级最高 | 红灯 |
| BDD-13 | test_agate_version_resolve.py: test_bdd_13_declared_not_installed_fallback | 声明未安装 → 警告（含版本号+未安装）+ 回退 current，exit 0 | 红灯 |
| BDD-14 | test_agate_version_resolve.py: test_bdd_14_invalid_format_fallback（parametrize ×3） | 非法格式 / 未知前缀 / 空文件 → 格式警告 + 回退 current | 红灯 |
| BDD-15 | test_hook_resolve_entry.py: test_bdd_15_install_fixed_resolve_entry | hook 执行链经 resolve-entry，不直接 exec 具体版本 gate py（负向断言） | 红灯（薄壳未改） |
| BDD-16 | test_hook_resolve_entry.py: test_bdd_16_ab_isolated_versions | 项目 A 锁 v0.43.0 / 项目 B 走 current(v0.44.0)，各自 gate 互不干扰 | 红灯 |
| BDD-17 | test_hook_resolve_entry.py: test_bdd_17_resolve_failure_fallback_not_silent | 声明未装 → 警告 + 回退 current 跑 gate（不静默跳过） | 红灯 |
| BDD-18 | test_hook_resolve_entry.py: test_bdd_18_switch_version_no_reinstall | 改 .agate-version 不重跑 install-hook 即切版本生效 | 红灯 |
| BDD-19 | test_hook_resolve_entry.py: test_bdd_19_copy_mode_resolve_entry | 复制模式经 .agate-root 恢复后仍按项目版本解析跑 gate | 红灯（resolve-entry 缺失） |
| BDD-20 | test_agate_summary.py: test_bdd_20_summary_resolved_version_and_reason | summary 显示解析版本 v0.43.0 + 原因引用 .agate-version | 红灯（旧 git-describe 语义） |
| BDD-21 | test_agate_summary.py: test_bdd_21_summary_global_current_reason | summary 显示 current 回退 v0.44.0 + 原因"current" | 红灯 |
| BDD-30 | test_agate_version_resolve.py: test_bdd_30_legacy_symlink_direct_root | 无指针 legacy 软链布局 → 软链目标本身 = AGATE_ROOT | 红灯 |
| P2-review 缺口 1 | test_agate_version_resolve.py: test_resolve_terminal_failure_fail_closed | 无 current/latest/legacy + 声明未装 → exit 非 0 且警告不静默 | 红灯 |

**BDD-31（gate 判定逻辑本身未被修改）**：非 pytest 验证项——P2-review 测试缺口 5 已裁定
"gate 判定逻辑未改靠 P7 一致性 + git log diff 判定，非 pytest"。本批次在 P3-test-cases 中
登记该验证程序（P7 时执行）：`git log` 对照 gate 判定脚本（check-gate.py / pre-commit-gate.py /
commit-msg-self-gate.py / pre-push-gate.py）改动仅限解析层；`check-protocol-consistency.py` 0 ERROR。
不为此写新 pytest 用例（写了即绿，违反 TDD 红灯要求）。

## 2. 测试代码布局

| 文件 | 覆盖 | 用例数 |
|------|------|--------|
| `agate/tests/unit/test_agate_version_resolve.py` | BDD-9~14, 30 + 终态 fail-closed | 8（BDD-14 为 3 参数化变体） |
| `agate/tests/unit/test_agate_summary.py` | BDD-20, 21 | 2 |
| `agate/tests/unit/test_hook_resolve_entry.py` | BDD-15~19 | 5 |

合计 **15 个测试函数**（17 个执行用例含参数化）。每个文件第 1 个用例 + 平台敏感用例标记
`@pytest.mark.windows_smoke`（BDD-30 软链 / BDD-19 复制模式）。

## 3. Given 环境契约（测试数据即 P4 实现输入约束）

1. **假 HOME**：经 `HOME`+`USERPROFILE` env 指向 `tmp_path/home`，`~/.agate` = `home/.agate`
   （不碰真实 `~/.agate`、不假设 `/tmp`）。resolve 基址 = `os.path.expanduser("~/.agate")`。
2. **版本目录**：`~/.agate/<vX.Y.Z>/` 目录存在即视为"已安装"。
3. **current/latest 指针**：文本文件，内容 = 目标名（Windows 复制模式指针形态，不假设 POSIX symlink）：
   - `latest` → `v0.44.0`（版本目录名）
   - `current` → `latest`（指针链）
   - 解析沿链：current → latest → 版本目录。
4. **resolve-entry 调用契约**：`resolve-entry.py <gate-name> [args...]`；gate-name 映射
   `pre-commit`→`pre-commit-gate.py` / `commit-msg`→`commit-msg-self-gate.py` /
   `pre-push`→`pre-push-gate.py`（P2-review 决策点 2：薄壳保留、exec 目标变 resolve-entry）。
5. **BDD-16/17/18/19 的 gate 验证**：版本目录内放 stub `scripts/pre-commit-gate.py`，写
   `GATE-V043`/`GATE-V044` 标记到 stdout，断言 hook 执行链实际跑到的版本。
6. **平台分支**：
   - BDD-30 legacy 软链：`os.symlink` 失败（Windows 无权限）→ `pytest.skip` 声明跳过；
     Linux 断言软链目标 = AGATE_ROOT。
   - BDD-19 复制模式：`AGATE_HOOK_COPY_MODE=1` 模拟（test_install_hook.py 既有模式）；
     `.agate-root` 标记断言 + hook 经 bash 调用。
   - 每文件首个用例 + 平台敏感用例带 `@pytest.mark.windows_smoke`。

## 4. 红灯确认

- **被测模块未实现（B 类）**：`agate-resolve.py` / `resolve-entry.py` 不存在 → run_cli 报
  "No such file"，returncode 非 0 → 断言失败。P3 当前全红。
- **BDD-15**：现有薄壳 exec `pre-commit-gate.py`、不含 `resolve-entry.py` → 断言失败（P4 改薄壳后绿）。
- **BDD-20/21**：现有 summary 显示 git describe（旧语义），不含项目解析版本 → 断言失败（P4 语义迁移后绿）。
- **无 A 类错误**（SyntaxError / fixture 缺失）；BDD-14 参数化含空文件变体（I-1 三要素全验收）。

## 5. 自检记录

- 3 个测试文件存在且非空 ✓
- 自跑命令：`python3 -m pytest agate/tests/unit/test_agate_version_resolve.py
  agate/tests/unit/test_agate_summary.py agate/tests/unit/test_hook_resolve_entry.py -q --tb=no`
- 结果：15 个测试函数全部红灯，失败原因为被测模块未实现（B 类）。摘要记入 P3-progress.md。
