---
phase: P3
task_id: TAG0008
type: test-cases
parent: P2-design.md
trace_id: TAG0008-P3-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

# P3 测试用例汇总 — agate 版本管理机制（v1）

> 本任务按 P2 dispatch_plan 拆 3 批（static-batch: resolve-chain / install / offline），
> 每批一个 test-designer 并行产出测试设计，各批用例详见分批文件：
> - **resolve-chain 批**：P3-test-cases-resolve.md（BDD-9~21/30/31，15 个测试函数 / 17 用例）
> - **install 批**：P3-test-cases-install.md（BDD-1~8，8 用例）
> - **offline 批**：P3-test-cases-offline.md（BDD-22~29，11 用例）
>
> test_code_dir: agate/tests/unit/

## 1. 测试文件清单

| 测试文件（agate/tests/unit/） | 批次 | 覆盖 BDD | 用例数 | 状态（P3） |
|-------------------------------|------|----------|--------|-----------|
| test_agate_version_resolve.py | resolve-chain | BDD-9~14 | 6 函数 / 8 用例（BDD-14 parametrize ×3） | 红灯（模块未实现） |
| test_hook_resolve_entry.py | resolve-chain | BDD-15~19 | 5 函数 / 5 用例 | 红灯（薄壳未改） |
| test_agate_summary.py | resolve-chain | BDD-20/21 | 2 函数 / 2 用例 | 红灯（模块未实现） |
| test_agate_version_install.py | install | BDD-1~8 | 8 用例 | 红灯（模块未实现） |
| test_agate_pack_offline.py | offline | BDD-22~24 | 3 用例 | 红灯（模块未实现） |
| test_install_offline.py | offline | BDD-25~29 | 7 用例（含 BDD-28 复制模式变体） | 红灯（模块未实现） |

> BDD-30/31（向后兼容红线）由 resolve-chain 批的 test_hook_resolve_entry.py 覆盖（legacy 兜底 / gate 判定不变）。

## 2. 红灯确认（check-tdd-red.py）

命令（主 Agent 执行）：
```bash
TEST_RUNNER="python3 -m pytest agate/tests/unit/test_agate_version_resolve.py agate/tests/unit/test_agate_summary.py agate/tests/unit/test_hook_resolve_entry.py agate/tests/unit/test_agate_version_install.py agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py -q --tb=no" python3 ~/.agate/scripts/check-tdd-red.py <TASK_DIR>
```
实测结果：exit 0（真红灯，全部为 B 类——被测模块/函数不存在，测试正确但因实现未写而失败）。

## 3. BDD 覆盖率

- BDD-1 ~ BDD-31 全覆盖（1:1 映射，测试名引用 BDD 编号）。
- 无 UI 交互（ui_affected=false），无需 Playwright/E2E。
- 平台无关：每文件第 1 个用例标 `@pytest.mark.windows_smoke`；复制模式用 `AGATE_HOOK_COPY_MODE=1` 模拟；禁止裸 python3 / 裸 /tmp / POSIX symlink 假设。

## 4. P4 实现导航

- P4 implementer 按 P2-design.md files_to_read + 本文件各分批用例的"接口契约"节（P3-test-cases-install.md §0 等）实现，测试名即预期行为。
- 共享文件 agate_common.py 由 resolve-chain 批修改，install/offline 批只读使用（dispatch_plan 共享文件后处理）。
