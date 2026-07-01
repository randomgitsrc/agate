#!/usr/bin/env bash
# tests/scripts/count-tests.sh — 从 .bats 文件自动统计测试用例
# 用法：bash tests/scripts/count-tests.sh
# 输出：每个 .bats 文件的 @test 数量 + 总计
# 这是测试计划附录 B 的实现——让"测试用例数"和"实际写的 .bats 文件"保持一致

set -euo pipefail

cd "$(dirname "$0")/.."

total=0
echo "=== 测试用例覆盖度自检 ==="
for f in unit/*.bats regression/*.bats integration/*.bats; do
    [ -f "$f" ] || continue
    count=$(grep -c '^@test' "$f" || true)
    total=$((total + count))
    printf "  %-50s %3d 个 @test\n" "$f" "$count"
done
echo "==="
echo "总计：$total 个测试用例"
echo ""
echo "如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 不一致"
echo "→ 文档漂移，需要更新。"
echo "如果文档改了但 .bats 文件没动 → 测试计划空头支票。"
