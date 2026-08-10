#!/usr/bin/env bash
# check-scope-resolved.sh — SCOPE+ 处理追踪（P2.11）
# 检查产出含 [SCOPE+] 时，P1-requirements.md 有对应 [SCOPE_RESOLVED] 标记
# exit 0 = 通过; exit 1 = SCOPE+ 未处理; exit 2 = 无 task 目录

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TASK_DIR="${1:?用法: check-scope-resolved.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"

[ ! -d "$TASK_DIR" ] && exit 2

# M2 修复：扫描所有 .md 文件（SCOPE+ 可能出现在非 P 前缀文件里，如 dispatch-context-{role}.md）
# 排除 AGATE_CARD 嵌入块（卡片模板文本含字面 SCOPE+ 会触发误报）
SCOPE_FOUND=""
for f in "$TASK_DIR"/*.md; do
    [ -f "$f" ] || continue
    # 跳过 dispatch-context 文件（编排指令，非阶段产出，不含实际 SCOPE+ 指令）
    basename "$f" | grep -qE 'dispatch-context|dispatch-prompt|progress' && continue
    if sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -qE '^\s*-?\s*\[SCOPE\+\]'; then
        SCOPE_FOUND="${SCOPE_FOUND}$(basename "$f") "
    fi
done

# 无 SCOPE+ → 不检查
[ -z "$SCOPE_FOUND" ] && exit 0

# 有 SCOPE+：检查 P1 是否有 [SCOPE_RESOLVED]
if [ ! -f "$P1_FILE" ]; then
    echo "GATE SCOPE: 产出含 [SCOPE+]（${SCOPE_FOUND}），但无 P1-requirements.md" >&2
    exit 1
fi

# v2.0 T001 流 C（BDD-22）：优先读 P1 frontmatter 结构化 scope_resolved 列表——
# 发现性标记本体（[SCOPE+]）保持散文不迁移（BDD-23），但"已解决"状态改为结构化，
# 闭环判定不再扫描正文 [SCOPE_RESOLVED] 散文标记。非空列表即已解决 → 直接通过。
# 字段不存在 / 存在但为空列表 → 落到下方旧格式正文 grep 回退判定（与"无该字段"
# 同等对待——本工具的 scope_resolved op 无正文回退语义，presence 与"非空"在此处
# 合并为同一判定信号，不单独区分"声明了空列表"与"完全未声明"两种情况）。
SCOPE_RESOLVED_FM=$(FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" scope_resolved 2>/dev/null || echo "")
if [ -n "$SCOPE_RESOLVED_FM" ]; then
    SCOPE_RESOLVED_FM_COUNT=$(printf '%s\n' "$SCOPE_RESOLVED_FM" | grep -cv '^\s*$' || true)
    echo "GATE SCOPE: ${SCOPE_FOUND}有 [SCOPE+]，P1 frontmatter scope_resolved 非空（${SCOPE_RESOLVED_FM_COUNT} 项已解决）" >&2
    exit 0
fi

# grep -c 找到 0 匹配时 exit 1，与 set -e 冲突，用 || true 抑制
# 匹配 [SCOPE_RESOLVED: xxx] 格式（协议定义格式）
# 也匹配 [SCOPE_RESOLVED] 独立出现或后接非小写字符
RESOLVED_COUNT=$(grep -cE '^\s*-?\s*\[SCOPE_RESOLVED($|[^a-z])' "$P1_FILE" 2>/dev/null || true)
RESOLVED_COUNT=${RESOLVED_COUNT:-0}
# 确保是数字（grep -c 可能输出 "0\n0" 在 || true 触发时）
RESOLVED_COUNT=$(echo "$RESOLVED_COUNT" | tail -1)

if [ "$RESOLVED_COUNT" -eq 0 ]; then
    echo "GATE SCOPE: 产出含 [SCOPE+]（${SCOPE_FOUND}），但 P1 无 [SCOPE_RESOLVED] 标记" >&2
    exit 1
fi

echo "GATE SCOPE: ${SCOPE_FOUND}有 [SCOPE+]，P1 有 ${RESOLVED_COUNT} 个 [SCOPE_RESOLVED]" >&2
exit 0
