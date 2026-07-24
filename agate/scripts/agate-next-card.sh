#!/usr/bin/env bash
# agate-next-card.sh — 输出当前阶段卡片全文
# 用法：agate-next-card.sh PHASE
#   PHASE 取值 P0-P8
#   输出固定格式（hook 用 sha256 校验嵌入 dispatch-context 的卡片是当前版本）
#
# exit 0：成功（输出卡片全文到 stdout）
# exit 1：参数缺失或过多
# exit 2：phase 不在 P0-P8 范围

set -euo pipefail

# 解析脚本真实路径（软链接兼容）
SCRIPT_REAL="$(readlink -f "${BASH_SOURCE[0]:-$0}" 2>/dev/null || echo "${BASH_SOURCE[0]:-$0}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_REAL")" 2>/dev/null && pwd || true)"

# 协议目录：脚本在 scripts/ 下，上一级就是协议目录
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$SCRIPT_DIR")}"

# 参数校验
if [ "$#" -ne 1 ]; then
    echo "GATE: agate-next-card.sh 需要 1 个参数（PHASE: P0-P8），收到 $# 个" >&2
    exit 1
fi

PHASE="$1"

# phase 必须在 P0-P8 范围
case "$PHASE" in
    P0|P1|P2|P3|P4|P5|P6|P7|P8) ;;
    *)
        echo "GATE: phase '$PHASE' 不在 P0-P8 范围内" >&2
        exit 2
        ;;
esac

CARD_FILE="$AGATE_ROOT/phase-cards/${PHASE}-$(case "$PHASE" in
    P0) echo "orchestrator" ;;
    P1) echo "requirements" ;;
    P2) echo "design" ;;
    P3) echo "tdd" ;;
    P4) echo "implementation" ;;
    P5) echo "verification" ;;
    P6) echo "acceptance" ;;
    P7) echo "consistency" ;;
    P8) echo "release" ;;
esac).md"

if [ ! -f "$CARD_FILE" ]; then
    echo "GATE: 阶段卡片文件不存在: $CARD_FILE" >&2
    exit 2
fi

# 输出格式（固定，便于下游 hook 做 sha256 校验）
# 路径用仓库相对路径——跨 checkout 保持字节稳定
REL_CARD="${CARD_FILE#$AGATE_ROOT/}"
printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$REL_CARD"
cat "$CARD_FILE"