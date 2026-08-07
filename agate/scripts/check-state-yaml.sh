#!/usr/bin/env bash
# check-state-yaml.sh — .state.yaml 格式校验（P2.15）
# 检查 .state.yaml 是否符合 state-machine.md 协议模板
# exit 0 = 格式正确; exit 1 = 格式错误; exit 2 = 无 .state.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STATE_FILE="${1:?用法: check-state-yaml.sh STATE_FILE}"

[ ! -f "$STATE_FILE" ] && exit 2

# 用环境变量传参，避免 shell 变量注入 Python 代码（M2 修复）
# 2>&1 保留 stderr，让 YAML 解析错误信息可见（M1 修复）
ERRORS=$(STATE_FILE="$STATE_FILE" python3 "$SCRIPT_DIR/agate-state-yaml-check.py" 2>/dev/null || true)

if [ -n "$ERRORS" ]; then
    echo "GATE STATE-YAML: .state.yaml 格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
