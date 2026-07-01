#!/usr/bin/env bash
# check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
# 四道客观审计 + agent 字段协作规范
# exit 0 = 通过; exit 1 = 审计不通过; exit 2 = WARNING（不阻塞）

set -euo pipefail

TASK_DIR="${1:?用法: check-p6-provenance.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"
P6_FILE="$TASK_DIR/P6-acceptance.md"
EVIDENCE_DIR="$TASK_DIR/P6-evidence"

# --- 辅助函数 ---

get_agent() {
    local file="$1"
    [ ! -f "$file" ] && echo "" && return
    sed -n '/^---$/,/^---$/p' "$file" | { grep -E '^agent:' || true; } | sed 's/^agent:\s*//' | head -1
}

get_risk_level() {
    [ ! -f "$P1_FILE" ] && echo "" && return
    P1_F="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_F']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo ""
}

# --- 审计 1：证据-结论对应 ---
# 1a. PASS 行的证据引用路径必须存在
# 1b. PASS 条目数 ≤ 证据文件数（空证据拦截）
# 1c. 证据文件必须被至少一条 PASS 行引用（空 png 充数拦截）
# 只在 P6-acceptance.md 存在时运行（C1 修复：不阻塞非 P6 阶段的 commit）

if [ -f "$P6_FILE" ]; then
    PASS_COUNT=$(grep -cE '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || echo 0)
    PASS_COUNT=$(echo "$PASS_COUNT" | tail -1)

    # 1a: PASS 行里的证据引用路径必须存在
    # I3 修复：取行末最后一个括号组（证据引用在行末），避免前置括号干扰
    # R1b 兼容：先剥离 (vision: ...) 引用，避免把它当证据文件路径
    MISSING_REFS=0
    while IFS= read -r line; do
        # 剥离 (vision: ...) 后再取行末括号组（去尾随空格避免行尾不是 )
        LINE_CLEAN=$(echo "$line" | sed 's/(vision:[^)]*)//g' | sed 's/[[:space:]]*$//')
        REF=$(echo "$LINE_CLEAN" | grep -oE '\([^)]+\)$' | sed 's/[()]//g' | head -1)
        if [ -n "$REF" ]; then
            # I4 修复：去除 P6-evidence/ / p6-evidence/ / evidences/ 前缀
            REF_CLEAN=$(echo "$REF" | sed 's|^P6-evidence/||' | sed 's|^p6-evidence/||' | sed 's|^evidences/||')
            REF_PATH="$EVIDENCE_DIR/$REF_CLEAN"
            if [ ! -f "$REF_PATH" ]; then
                MISSING_REFS=$((MISSING_REFS + 1))
            fi
        fi
    done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

    if [ "$MISSING_REFS" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 有 ${MISSING_REFS} 条 PASS 引用的证据文件不存在" >&2
        exit 1
    fi

    # 1b: PASS 数 ≤ 证据文件数（空证据拦截）
    # I5 修复：排除隐藏文件（.gitkeep, .DS_Store 等）
    if [ -d "$EVIDENCE_DIR" ]; then
        EVIDENCE_COUNT=$(find "$EVIDENCE_DIR" -type f -not -name '.*' 2>/dev/null | wc -l)
    else
        EVIDENCE_COUNT=0
    fi

    if [ "$PASS_COUNT" -gt 0 ] && [ "$EVIDENCE_COUNT" -eq 0 ]; then
        echo "GATE PROVENANCE: 有 ${PASS_COUNT} 条 PASS 但 P6-evidence/ 为空或不存在" >&2
        exit 1
    fi

    if [ "$PASS_COUNT" -gt "$EVIDENCE_COUNT" ]; then
        echo "GATE PROVENANCE: PASS 条目数(${PASS_COUNT}) > 证据文件数(${EVIDENCE_COUNT})" >&2
        exit 1
    fi

    # 1c: 证据文件必须被至少一条 PASS 行引用（空 png 充数拦截）
    # C2 修复：用括号上下文精确匹配，防止子字符串假阴性
    # C3 修复：只在 PASS 行里搜索，不在整个文件里搜索
    if [ "$EVIDENCE_COUNT" -gt 0 ] && [ -d "$EVIDENCE_DIR" ]; then
        UNREFERENCED=0
        while IFS= read -r ev_file; do
            ev_basename=$(basename "$ev_file")
            # I4 修复：匹配时考虑子目录路径（evidences/ screenshots/ 等）
            if ! grep -E '^\s*- PASS\b' "$P6_FILE" | grep -qE "\([^)]*${ev_basename}\)"; then
                UNREFERENCED=$((UNREFERENCED + 1))
            fi
        done < <(find "$EVIDENCE_DIR" -type f -not -name '.*' 2>/dev/null)
        if [ "$UNREFERENCED" -gt 0 ]; then
            echo "GATE PROVENANCE: ${UNREFERENCED} 个证据文件未被 P6-acceptance.md PASS 行引用（可能为充数文件）" >&2
            exit 1
        fi
    fi
fi

# --- 审计 2：dispatch-context 内容约束 ---
# P6 阶段的 dispatch-context 不能含验收结论预判

DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"
if [ -f "$DISPATCH_CTX" ]; then
    PREJUDICE=$(grep -cE '^\s*- (PASS|FAIL)\b' "$DISPATCH_CTX" 2>/dev/null || echo 0)
    PREJUDICE=$(echo "$PREJUDICE" | tail -1)
    if [ "$PREJUDICE" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-dispatch-context.md 含 ${PREJUDICE} 处验收结论预判" >&2
        exit 1
    fi
fi

# --- 审计 3：BDD 总数自动化对照 ---
# P6 的 PASS+FAIL 数 ≥ P1 的 Given 行数（挑验拦截）

if [ -f "$P6_FILE" ] && [ -f "$P1_FILE" ]; then
    P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)
    P1_BDD=$(echo "$P1_BDD" | tail -1)

    P6_TOTAL=$(grep -cE '^\s*- (PASS|FAIL)\b' "$P6_FILE" 2>/dev/null || echo 0)
    P6_TOTAL=$(echo "$P6_TOTAL" | tail -1)

    if [ "$P1_BDD" -gt 0 ]; then
        if [ "$P6_TOTAL" -lt "$P1_BDD" ]; then
            echo "GATE PROVENANCE: P6 结果数(${P6_TOTAL}) < P1 BDD 条目数(${P1_BDD})，挑验不通过" >&2
            exit 1
        fi
    else
        echo "GATE PROVENANCE: P1 BDD 格式非标准（无 Given 行），BDD 总数对照需主 Agent 手动核实" >&2
        exit 2
    fi
fi

# --- 审计 4：UI vision YAML 引用（R1b：T045 评审 v5）---
# 将 dispatch-protocol.md:575 已有规则 hook 化
# ui_affected: true 时，含截图引用的 PASS 行必须同时含 (vision: ...) 引用
# 兼容"查询类 BDD 可不截图"规则——只检查含 (screenshots/ 引用的 PASS 行
# YAML 文件存在 + summary.blocker_count == 0
if [ -f "$P6_FILE" ] && [ -f "$P1_FILE" ]; then
    P2_FILE="$TASK_DIR/P2-design.md"
    UI_AFFECTED=""
    if [ -f "$P2_FILE" ]; then
        UI_AFFECTED=$(P2_FILE="$P2_FILE" python3 -c "
import re, os
with open(os.environ['P2_FILE']) as f:
    text = f.read()
m = re.search(r'ui_affected:\s*(true|false)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
    fi

    if [ "$UI_AFFECTED" = "true" ]; then
        # 只检查含截图引用的 PASS 行——这些行必须同时有 vision 引用
        VISION_MISSING=0
        while IFS= read -r line; do
            if echo "$line" | grep -qE '\(screenshots/'; then
                if ! echo "$line" | grep -qE '\(vision:\s*[^)]+\)'; then
                    VISION_MISSING=$((VISION_MISSING + 1))
                fi
            fi
        done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

        if [ "$VISION_MISSING" -gt 0 ]; then
            echo "GATE PROVENANCE: ui_affected=true 但有 ${VISION_MISSING} 条含截图的 PASS 缺 vision YAML 引用" >&2
            exit 1
        fi

        # 检查每个 vision YAML 文件存在 + blocker_count == 0
        while IFS= read -r ref; do
            YAML_FILE=$(echo "$ref" | sed 's/^.*vision:\s*//' | tr -d ' )')
            YAML_PATH="$TASK_DIR/$YAML_FILE"
            if [ ! -f "$YAML_PATH" ]; then
                echo "GATE PROVENANCE: vision YAML 引用的文件不存在: $YAML_FILE" >&2
                exit 1
            fi
            BLOCKER_COUNT=$(YAML_PATH="$YAML_PATH" python3 -c "
import yaml, os
try:
    with open(os.environ['YAML_PATH']) as f:
        data = yaml.safe_load(f)
    va = data.get('vision_analysis', {}) if data else {}
    summary = va.get('summary', {})
    print(summary.get('blocker_count', -1))
except Exception:
    print(-1)
" 2>/dev/null || echo -1)
            if [ "$BLOCKER_COUNT" != "0" ]; then
                echo "GATE PROVENANCE: vision YAML $YAML_FILE 的 blocker_count=$BLOCKER_COUNT（须为 0）" >&2
                exit 1
            fi
        done < <(grep -oE '\(vision:\s*[^)]+\)' "$P6_FILE" 2>/dev/null | sort -u || true)
    fi
fi

# --- 协作规范：agent 字段 ---
# 不做硬拦截（自报数据不可信），缺字段降级为 WARNING
# 安全审计（1/2/3）用 ERROR，协作规范用 WARNING——符合「不把自报字段当安全边界」原则

if [ -f "$P6_FILE" ]; then
    AGENT=$(get_agent "$P6_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 缺 agent 字段（协作规范，不阻塞）" >&2
        exit 2
    fi
fi

# P2 评审：缺字段 WARNING；risk=high + agent=main WARNING
P2_REVIEW_FILE="$TASK_DIR/P2-review.md"
if [ -f "$P2_REVIEW_FILE" ]; then
    RISK=$(get_risk_level)
    AGENT=$(get_agent "$P2_REVIEW_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P2-review.md 缺 agent 字段（协作规范，不阻塞）" >&2
        exit 2
    fi
    if [ "$RISK" = "high" ] && [ "$AGENT" = "main" ]; then
        echo "GATE PROVENANCE: risk_level=high 且 P2-review.md agent=main（自审），建议派发独立 reviewer" >&2
        exit 2
    fi
fi

# 所有阶段产出文件 agent 字段存在性（格式校验）
# 向后兼容：v2 之前创建的文件无 agent 字段，降级为 WARNING 不阻塞
if [ -f "$P6_FILE" ]; then
for f in "$TASK_DIR"/P[0-8]-*.md; do
    [ -f "$f" ] || continue
    localname=$(basename "$f")
    [ "$localname" = "P0-brief.md" ] && continue
    case "$localname" in
        *-dispatch-context.md|*-progress.md|*-paused-resolution.md) continue ;;
    esac
    AGENT=$(get_agent "$f")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: $localname 缺 agent 字段（协作规范，不阻塞）" >&2
        exit 2
    fi
done
fi

exit 0
