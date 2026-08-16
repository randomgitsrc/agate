---
phase: P5
task_id: TAG0008
type: implementation
parent: FIX-WINDOWS-TAG0008.md
trace_id: TAG0008-P5FIX2-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P5 修复轮：失败 2（test_bdd_1_latest_pointer_after_noarg_install）

## 根因（已实证，dispatch-context 采信）

`test_agate_version_install.py` 的 `_run_install` helper 只设 `env={"HOME": str(home)}`，未设 `USERPROFILE`。
Windows 上 `os.path.expanduser("~")` 优先用 USERPROFILE（ntpath 不认 HOME）→ `_agate_home()`
（agate-install.py:66-68）解析到**真实用户目录**（CI 路径 `C:\Users\runneradmin\.agate`）→
`latest`/`current` 写到真实 `~/.agate` → 测试断言 `home/.agate/latest` 不存在而失败。

对照同批 `test_agate_version_resolve.py:17-19` 的 `_resolve_env` 正确设置了 `HOME`+`USERPROFILE`——install 测试 helper 是遗漏。这是测试缺陷修复（helper 遗漏），非改测试迁就实现。

## 修复内容

`test_agate_version_install.py:22` 的 `_run_install` helper：

```python
# 修复前
env = {"HOME": str(home)}
# 修复后（与 resolve 测试 _resolve_env 一致）
env = {"HOME": str(home), "USERPROFILE": str(home)}
```

该 helper 服务 test_bdd_1~8 全部 install 测试，一处修复覆盖整批。

## 验证结果

- `python3 -m pytest agate/tests/unit/test_agate_version_install.py -q` → **9 passed**（3.02s）
- `python3 -m pytest agate/tests/ -q` → **823 passed, 2 skipped**（82.71s），与基线 823 passed 一致，无回归

## 边界

只改 test_agate_version_install.py 的 `_run_install` helper，未碰其他文件（含实现代码）。

## 环境

[PROD_NOT_TOUCHED] 本任务仅修改 worktree 内测试文件 + 任务目录产出，未接触生产环境。
