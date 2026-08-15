#!/usr/bin/env bash
# pre-push-gate.sh — pre-push hook 薄壳（逻辑在 pre-push-gate.py 单份维护）
# AGATE_ALIGNMENT_REVIEW_THRESHOLD 阈值在 pre-push-gate.py 内维护
set -u
# 1. AGATE_ROOT 自定位（软链→本体；复制模式 .agate-root 恢复）
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")")}"
if [ ! -d "$AGATE_ROOT/scripts" ] \
    && [ -f "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root" ]; then
    AGATE_ROOT=$(tr -d '\r' < "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root")
fi
# 2. python 探测：python3 → python
PY=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
# 3. exec python 主程序
if [ -n "$PY" ] && [ -f "$AGATE_ROOT/scripts/pre-push-gate.py" ]; then
    exec "$PY" "$AGATE_ROOT/scripts/pre-push-gate.py" "$@"
fi
# 4. exec 失败 → fail-closed 阻断（不运行 sh 兜底逻辑）
echo "GATE ERROR: 无法启动 python gate（python3/python 均不可用或脚本缺失）" >&2
echo "  agate/*.md 改动量 alignment-review 提示无法执行，push 中止——请安装 python3 + pyyaml" >&2
exit 1
