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
# Q1（TAG0004）：前缀剥离先试直接剥离（Linux 字节不变），失败再归一化双方（统一 /、盘符小写）后剥离。
# 归一化用 tr/bash 参数替换，不用 sed '\L'（GNU 专有，macOS/BSD sed 不可移植）。
# 盘符小写（C:/ → c:/），bash 参数替换 + tr，不依赖 sed '\L'
lower_drive() {
    local p="$1" drive
    if [[ "$p" =~ ^[A-Za-z]: ]]; then
        drive="$(printf '%s' "${p:0:1}" | tr 'A-Z' 'a-z')"
        p="${drive}${p:1}"
    fi
    printf '%s' "$p"
}

rel_card() {
    local root="$1" file="$2" rel
    rel="${file#$root/}"
    if [ "$rel" = "$file" ]; then
        local root_norm file_norm
        root_norm="$(printf '%s' "$root" | tr '\\' '/' )"
        root_norm="$(lower_drive "$root_norm")"
        file_norm="$(printf '%s' "$file" | tr '\\' '/' )"
        file_norm="$(lower_drive "$file_norm")"
        rel="${file_norm#$root_norm/}"
    fi
    printf '%s' "$rel"
}

REL_CARD="$(rel_card "$AGATE_ROOT" "$CARD_FILE")"
printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$REL_CARD"
cat "$CARD_FILE"