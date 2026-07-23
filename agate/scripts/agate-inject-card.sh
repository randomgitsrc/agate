#!/usr/bin/env bash
# agate-inject-card.sh — 自动注入 AGATE_CARD 到 dispatch-context 文件
# 用法: agate-inject-card.sh P{N} TASK_DIR

set -euo pipefail

PHASE="${1:?用法: agate-inject-card.sh PHASE TASK_DIR}"
TASK_DIR="${2:?用法: agate-inject-card.sh PHASE TASK_DIR}"

AGATE_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "$0")")")}"
AGATE_NEXT_CARD="$AGATE_ROOT/scripts/agate-next-card.sh"

if [ ! -x "$AGATE_NEXT_CARD" ]; then
    echo "GATE: agate-next-card.sh 不可用" >&2
    exit 1
fi

CARD_CONTENT=$(bash "$AGATE_NEXT_CARD" "$PHASE" 2>/dev/null) || true
if [ -z "$CARD_CONTENT" ]; then
    echo "GATE: agate-next-card.sh $PHASE 输出为空" >&2
    exit 1
fi

shopt -s nullglob
DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)
shopt -u nullglob

if [ ${#DC_FILES[@]} -eq 0 ]; then
    # fallback: 过渡期兼容旧格式
    DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context.md")
fi

if [ ! -f "${DC_FILES[0]}" ]; then
    echo "GATE: ${PHASE}-dispatch-context-{role}.md 不存在" >&2
    exit 1
fi

# 用 python3 替换 AGATE_CARD 块（sed 多行替换不可靠）
for DC_FILE in "${DC_FILES[@]}"; do
    CARD_FILE=$(mktemp)
    printf '%s' "$CARD_CONTENT" > "$CARD_FILE"
    DC_FILE="$DC_FILE" CARD_FILE="$CARD_FILE" python3 -c "
import os, re, sys
dc = os.environ['DC_FILE']
with open(dc) as f:
    text = f.read()
with open(os.environ['CARD_FILE']) as f:
    card = f.read()
pattern = r'(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)'
if not re.search(pattern, text, flags=re.DOTALL):
    print(f'AGATE_CARD 注入失败: {os.path.basename(dc)} 中未找到 AGATE_CARD_START/END 占位符', file=sys.stderr)
    sys.exit(1)
replacement = lambda m: m.group(1) + card.rstrip('\n') + '\n' + m.group(3)
new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
with open(dc, 'w') as f:
    f.write(new_text)
"
    rm -f "$CARD_FILE"
    echo "AGATE_CARD 已注入: $(basename "$DC_FILE")"
done
