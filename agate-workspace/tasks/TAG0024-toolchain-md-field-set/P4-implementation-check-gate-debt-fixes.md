---
phase: P4
task_id: TAG0024
type: implementation
parent: P2-design.md
trace_id: TAG0024-P4-check-gate-debt-fixes-20260825
status: draft
created: 2026-08-25
agent: implementer
---

```yaml
implementation_dir: agate/scripts/
```

## 改动摘要

修复 `agate/scripts/check-gate.py` 两处缺陷（批次 `check-gate-debt-fixes`）：

1. **DEBT0019**（`_check_roadmap_done()`，原第 1181-1199 行）：新增模块级常量
   `_ROADMAP_EXPECTED_COLS = 9`，把原宽松判据 `len(cols) < 8` 替换为精确匹配
   `len(cols) != _ROADMAP_EXPECTED_COLS`，单元格内含字面 `|` 时整行跳过，不再错位取值。
2. **DEBT0020**（`gate_p8()` 内 `roadmap_path` 构造，原第 1223-1224 行）：改用
   `_git(["rev-parse", "--show-toplevel"])` 做仓库根锚定后拼接
   `agate-workspace/roadmap/roadmap.md`，替换原 CWD 相对拼接；`_git()` 返回非零
   （仓库根不可得，非 git 环境）时在 stderr 输出含"仓库根不可得"字样的区分性提示，
   并跳过检查（`roadmap_path = None`），不再静默跳过。

未新增独立的 `_repo_root()` 辅助函数——直接在 `gate_p8()` 内联调用 `_git()`，
以满足"只改 `_check_roadmap_done()` 和 `gate_p8()` 内 `roadmap_path` 相关行"的
派发约束（P2-design.md §3.7 伪代码示例中的 `_repo_root()` 是示意写法，未强制要求
拆出新函数；本实现选择不新增顶层函数以最小化改动面）。

## 自跑测试结果

命令：
```
timeout 150s python3 -m pytest agate/tests/unit/test_check_gate.py --basetemp=.pytest-tmp -p no:cacheprovider -q
```

结果：
```
182 passed in 26.25s
```

0 failed，182 项全绿（新增 BDD-20/21(x3)/22/23/24 共 7 项用例全部通过 + 既有 175 项无回归）。

## `git diff --stat check-gate.py`

```
 agate/scripts/check-gate.py | 27 ++++++++++++++++++++++++---
 1 file changed, 24 insertions(+), 3 deletions(-)
```

`git diff` 逐行核对：改动仅落在 `_check_roadmap_done()` 函数体（新增常量定义 + docstring
补充说明 + 判据替换一行）与 `gate_p8()` 内 `roadmap_path` 构造相关的代码块（新增仓库根
锚定逻辑 + stderr 提示），未触及其余判定逻辑或其他函数。
