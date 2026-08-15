# BDD-5 Windows CI 冒烟 — 本地验证说明（minimal_validation 兜底）

## 结论：待 Windows CI 确认（cannot verify locally）

BDD-5（Windows CI 冒烟通过：`python -m pytest agate/tests/ -m windows_smoke` 在 windows-latest 真机跑通）
**本地 Linux 无法真机验证**——这是 `requires_minimal_validation: true` 的既定边界（P1 frontmatter +
P2-design §4.4 minimal_validation 第 5 条已确认）。

## 本地可验证的等价证据（P2 minimal_validation 兜底）

1. **marker 机制成立**：`python3 -m pytest agate/tests/ --collect-only -q -m windows_smoke`
   → `78/750 tests collected (672 deselected)`（见 `windows-smoke-collect.log`）——Windows 冒烟代表用例
   已逐用例打 `@pytest.mark.windows_smoke` 标，选取逻辑不再依赖 check-windows-smoke.sh 的 @test 名称正则。
2. **marker 已注册**：pyproject.toml `[tool.pytest.ini_options] markers = ["windows_smoke: Windows CI smoke representative"]`——无 PytestUnknownMarkWarning（P2 §4.4 minimal_validation 第 2 条实测）。
3. **CI 配置就位**：`.github/workflows/protocol-tests.yml` pytest job 的 Windows 分支执行
   `python -m pytest agate/tests/ -m windows_smoke`（line 38）——冒烟子集在 windows-latest 真机实跑。
4. **Linux 全量功能正确**：全量 pytest 748 passed / 2 skipped / exit 0（见 `regression.log`），
   平台敏感机制（cp1252 / CRLF / symlink 复制模式 / py_path / PYTHONIOENCODING）在 Linux 全量覆盖，
   功能正确性由 Linux 保证，Windows 只验证代表用例跑通。

## 判定口径

本 BDD 判定为 **PASS（本地证据 + 待 Windows CI 实跑确认）**：
- PASS 依据 = marker 机制（78 用例收集）、marker 注册、CI 配置引用 `-m windows_smoke`、Linux 全量全绿。
- 边界声明 = Windows 真机实跑结果以 push 后 GitHub Actions `windows-latest` job 为准；
  P5 时 `ci-gate-backstop.py` 在本机非 CI 平台 SKIP（设计行为，CI 兜底由 push 后 Actions 承担）。

> 若 Windows CI 实跑出现失败，按协议回退 P4 修复后重走 P5/P6，本说明文件随之更新。
