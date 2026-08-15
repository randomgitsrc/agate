#!/usr/bin/env bash
# tests/scripts/count-tests.sh — 用 pytest --collect-only 统计全树测试用例
# 用法：bash tests/scripts/count-tests.sh
# 输出：总计：N 个测试用例（pytest collect-only 收集口径）
# TAG0011 改写：统计对象从 .bats 的 @test（grep -c '^@test'）改为 pytest 收集数（P2 §1.4 D1 决策）
# 守护职责延续："用例数不漂移"（handoff/AGENTS.md/UPGRADING/tests-README 引用路径不变）

set -euo pipefail

TESTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"   # agate/tests/ 绝对路径（显式传参，不依赖 cwd）
PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
if [ -z "$PY" ]; then
    echo "count-tests: 找不到 python3/python（pytest 未安装则无法计数）" >&2
    exit 1
fi
# 收集数（unit/regression/integration/sanity/scripts 全树，pytest --collect-only 末行 "N tests collected"）
count=$("$PY" -m pytest --collect-only -q "$TESTS_DIR" 2>/dev/null | grep -oE '[0-9]+ tests? collected' | tail -1 | grep -oE '[0-9]+' || true)
echo "=== pytest 用例覆盖度自检 ==="
echo "总计：${count:-0} 个测试用例（pytest collect-only 口径）"
echo ""
echo "目标：≥ 749（TAG0011 迁移基线，BDD-1）；迁移期数值单调逼近 749。"
echo "如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 的口径不一致"
echo "→ 文档漂移，需要更新（附录 A 已归档，口径以 BDD-1 749 为准）。"
