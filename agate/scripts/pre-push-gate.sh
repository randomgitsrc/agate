#!/usr/bin/env bash
# pre-push-gate.sh — pre-push hook 薄壳（经 resolve-entry 解析版本后 exec 对应版本 py）
# AGATE_ALIGNMENT_REVIEW_THRESHOLD 阈值在 pre-push-gate.py 内维护
set -u
# 1. 入口根自定位（软链→本体；复制模式 .agate-root 恢复）——resolve-entry 所在安装根。
#    不用 AGATE_ROOT 变量（避免经环境泄漏给 resolve-entry 而绕过项目版本解析，TAG0008）
ENTRY_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")")}"
if [ ! -d "$ENTRY_ROOT/scripts" ] \
    && [ -f "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root" ]; then
    ENTRY_ROOT=$(tr -d '\r' < "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root")
fi
# 2. python 探测：python3 → python
PY=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
# 3. exec 固定解析入口 resolve-entry（读项目 .agate-version → 对应版本 gate py，不随版本变）
if [ -n "$PY" ] && [ -f "$ENTRY_ROOT/scripts/resolve-entry.py" ]; then
    exec "$PY" "$ENTRY_ROOT/scripts/resolve-entry.py" pre-push "$@"
fi
# 4. exec 失败 → fail-closed 阻断（不运行 sh 兜底逻辑）
echo "GATE ERROR: 无法启动 resolve-entry（python3/python 均不可用或脚本缺失）" >&2
echo "  agate/*.md 改动量 alignment-review 提示无法执行，push 中止——请安装 python3 + pyyaml" >&2
exit 1
