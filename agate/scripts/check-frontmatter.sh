#!/usr/bin/env bash
# check-frontmatter.sh FILE — frontmatter schema 校验（P1/P2/P6/P7，v2.0 T001 流 A）
# 检查 FILE 的 frontmatter 块是否符合 P2-design.md §3.1.3 定义的 schema
# exit 0 = 格式正确（含非目标文件 / 旧格式无 frontmatter）; exit 1 = 格式错误

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FILE="${1:?用法: check-frontmatter.sh FILE}"

[ ! -f "$FILE" ] && exit 0

# 用环境变量传参，避免 shell 变量注入 Python 代码（同 check-state-yaml.sh 惯例）
# 2>/dev/null：解析错误信息由 agate-frontmatter-check.py 输出到 stdout（ERRORS 捕获）
ERRORS=$(FILE="$FILE" python3 "$SCRIPT_DIR/agate-frontmatter-check.py" 2>/dev/null || true)

if [ -n "$ERRORS" ]; then
    echo "GATE FRONTMATTER: $FILE frontmatter 格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
