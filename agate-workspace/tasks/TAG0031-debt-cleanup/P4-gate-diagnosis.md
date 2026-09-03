---
phase: P4
date: 2026-09-04
trigger: unintended_regression
---
# P4 Gate 诊断（三簇实现全量跑后）

- 全量测试结果：3 failed, 1432 passed, 2 skipped（`pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=short`）
- 2 项失败是预期的 debt 登记闭合动作尚未执行（`test_tag0031_bdd_15_six_debts_registry_closed` / `test_bdd_7_debt0007_status_closed_with_closure_fields`）——按 P2 design 由主 Agent 在三簇返回后统一处理，非缺陷
- **1 项意外失败**：`agate/tests/unit/test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff`（既有 ruff lint 守卫测试）

## 诊断

version-mgmt 簇在 `install-offline.py` 新增的 yaml/agate_common 探测导入块（L38-39）触发 ruff
`I001`（import block un-sorted）：

```python
try:
    import yaml as _yaml_probe  # noqa: F401
    import agate_common as _agate_common_probe
except ImportError:
    _agate_common_probe = None
```

`ruff check agate/scripts/install-offline.py` 实测输出：`import yaml as _yaml_probe` 与
`import agate_common as _agate_common_probe` 被 ruff isort 判定为两个不同分组（第三方 `yaml` vs
本地/一级模块 `agate_common`），需要空行分隔才算"已排序"。`ruff --fix` 建议方案是在两行之间插入
一个空行。

## 修复方向

在 `import yaml as _yaml_probe  # noqa: F401` 与 `import agate_common as _agate_common_probe`
之间插入一个空行（纯格式修正，不改变导入语义/运行行为）。修复后跑
`~/.venvs/agate-dev/bin/ruff check agate/scripts/install-offline.py` 确认 0 error，并重跑
`test_bdd_34_shellcheck_three_hook_shells_and_ruff` 确认转绿。

## 路由

退回 version-mgmt 簇的 implementer，仅修正这一处空行格式，不动其余任何已确认转绿的实现内容。
