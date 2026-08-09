#!/usr/bin/env bash
# check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
# 六道客观审计 + agent 字段协作规范
# exit 0 = 通过; exit 1 = 审计不通过; exit 2 = WARNING（不阻塞）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
    FILE="$P1_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" risk_level 2>/dev/null || echo ""
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
    # R1c 修复：优先精确提取 screenshots/ 路径，避免嵌套括号（如 nth(1)）截断
    MISSING_REFS=0
    MISSING_DETAILS=""
    while IFS= read -r line; do
        LINE_CLEAN=$(echo "$line" | sed 's/(vision:[^)]*)//g' | sed 's/[[:space:]]*$//')

        mapfile -t REFS < <(echo "$LINE_CLEAN" | grep -oE 'screenshots/[^ ),]+' || true)

        if [ ${#REFS[@]} -eq 0 ]; then
            REF_GROUP=$(echo "$LINE_CLEAN" | grep -oE '\([^)]+\)$' | sed 's/[()]//g' | head -1 || true)
            IFS=',' read -ra REFS <<< "$REF_GROUP"
        fi

        for REF in "${REFS[@]}"; do
            REF=$(echo "$REF" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            [ -z "$REF" ] && continue
            REF_CLEAN=$(echo "$REF" | sed 's|^P6-evidence/||' | sed 's|^p6-evidence/||' | sed 's|^evidences/||')
            REF_PATH="$EVIDENCE_DIR/$REF_CLEAN"
            if [ ! -f "$REF_PATH" ]; then
                MISSING_REFS=$((MISSING_REFS + 1))
                MISSING_DETAILS="${MISSING_DETAILS}  PASS行: ${line}\n  缺失路径: ${REF_PATH}\n"
            fi
        done
    done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

    if [ "$MISSING_REFS" -gt 0 ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 有 ${MISSING_REFS} 条 PASS 引用的证据文件不存在" >&2
        if [ -n "$MISSING_DETAILS" ]; then
            printf '%b' "$MISSING_DETAILS" >&2
        fi
        exit 1
    fi

    # 1b: 证据目录非空检查（多条 PASS 可共享同一证据文件）
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

    # 1c: 证据文件必须被至少一条 PASS 行引用（空 png 充数拦截）
    # C2 修复：用括号上下文精确匹配，防止子字符串假阴性
    # C3 修复：只在 PASS 行里搜索，不在整个文件里搜索
    if [ "$EVIDENCE_COUNT" -gt 0 ] && [ -d "$EVIDENCE_DIR" ]; then
        UNREFERENCED=0
        while IFS= read -r ev_file; do
            ev_basename=$(basename "$ev_file")
            # I4 修复：匹配时考虑子目录路径（evidences/ screenshots/ 等）
            # 用 grep -F 做固定字符串匹配（ev_basename 可能含正则元字符如 + ）
            if ! grep -E '^\s*- PASS\b' "$P6_FILE" | grep -qF "$ev_basename"; then
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

shopt -s nullglob
DISPATCH_CTXS=("$TASK_DIR/P6-dispatch-context-"*.md)
shopt -u nullglob
for DISPATCH_CTX in "${DISPATCH_CTXS[@]}"; do
    # Exclude AGATE_CARD embedded block (card template text like "- FAIL > 0" is not a prejudice)
    # T001 v2.0 流 B（P2-design.md §3.2.3，P1 隐含需求 #11）：P6 结果入 frontmatter 后，
    # dispatch-context 顶部的 "---" frontmatter 样例块也须排除，避免其中的字段示例
    # （如未来模板贴出 `pass: N` 附近若含 "- PASS ..." 说明文字）被误判为验收结论预判。
    # 排除范围：先删 AGATE_CARD 块，再删文件顶部第一对 "---" 定界的 frontmatter 块。
    PREJUDICE=$(sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$DISPATCH_CTX" | sed '/^---$/,/^---$/d' | grep -cE '^\s*- (PASS|FAIL)\b' 2>/dev/null || echo 0)
    PREJUDICE=$(echo "$PREJUDICE" | tail -1)
    if [ "$PREJUDICE" -gt 0 ]; then
        echo "GATE PROVENANCE: $(basename "$DISPATCH_CTX") 含 ${PREJUDICE} 处验收结论预判" >&2
        exit 1
    fi
done

# --- 审计 3：BDD 总数自动化对照 ---
# P6 的 PASS+FAIL 数 ≥ P1 的 BDD 标题数（挑验拦截）
# T001 v2.0 流 B（BDD-17/18，P2-design.md §3.2.1）：计数口径改从严格式
# `grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]'`（总结行如 "- PASS: 16" 不带 BDD 编号不再
# 误计入，F11 消除）；新格式（frontmatter 声明 pass+fail）优先用该结构化汇总为总数，
# 无 frontmatter 汇总（旧格式）→ 回退从严正文 grep。
# FIND-6（P2-design.md §3.2.1/§13，决定"加"）：新格式下增加交叉校验 WARNING——
# frontmatter pass+fail 总数与正文从严行数不一致（如声明 pass:28 但正文仅 20 条
# PASS 行）→ 输出 WARNING 提示复核；exit 仍 0，非阻断，属防呆 nudge，不提升 gate
# 强度（语义真实性边界不变，§10：机器只提示"计数对不上"，不判定"内容造假"）。

if [ -f "$P6_FILE" ] && [ -f "$P1_FILE" ]; then
    P1_BDD=$(grep -cE '^#### BDD-[0-9]' "$P1_FILE" 2>/dev/null || echo 0)
    P1_BDD=$(echo "$P1_BDD" | tail -1)

    P6_BODY_STRICT=$(grep -cE '^\s*- (PASS|FAIL) BDD-[0-9]' "$P6_FILE" 2>/dev/null || echo 0)
    P6_BODY_STRICT=$(echo "$P6_BODY_STRICT" | tail -1)

    PASS_FM=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" pass 2>/dev/null || echo "")
    FAIL_FM=$(FILE="$P6_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" fail 2>/dev/null || echo "")
    if [ -n "$PASS_FM" ] && [ -n "$FAIL_FM" ]; then
        P6_TOTAL=$((PASS_FM + FAIL_FM))
        if [ "$P6_TOTAL" -ne "$P6_BODY_STRICT" ]; then
            echo "GATE PROVENANCE WARNING: P6-acceptance.md frontmatter 声明 pass+fail=${P6_TOTAL}，正文逐条 '- PASS|FAIL BDD-N' 行数=${P6_BODY_STRICT}，两者不一致，请复核" >&2
        fi
    else
        P6_TOTAL=$P6_BODY_STRICT
    fi

    if [ "$P1_BDD" -eq 0 ]; then
        echo "GATE PROVENANCE: P1-requirements.md 未使用标准 #### BDD-NN: 格式（或没有 BDD），标准化后必须使用该格式" >&2
        exit 1
    fi
    if [ "$P6_TOTAL" -lt "$P1_BDD" ]; then
        echo "GATE PROVENANCE: P6 结果数(${P6_TOTAL}) < P1 BDD 条目数(${P1_BDD})，挑验不通过" >&2
        exit 1
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
        UI_AFFECTED=$(FILE="$P2_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" ui_affected 2>/dev/null || echo "")
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
            BLOCKER_COUNT=$(YAML_PATH="$YAML_PATH" python3 "$SCRIPT_DIR/agate-vision-blocker.py" 2>/dev/null || echo -1)
            if [ "$BLOCKER_COUNT" != "0" ]; then
                echo "GATE PROVENANCE: vision YAML $YAML_FILE 的 blocker_count=$BLOCKER_COUNT（须为 0）" >&2
                exit 1
            fi
        done < <(grep -oE '\(vision:\s*[^)]+\)' "$P6_FILE" 2>/dev/null | sort -u || true)
    fi
fi

# --- 审计 5：日志 EXIT_CODE 与 PASS/FAIL 声明一致性（依赖 M1.3a 约定）---
if [ -f "$P6_FILE" ]; then
    while IFS= read -r log_file; do
        LAST_LINE=$(tail -1 "$log_file" 2>/dev/null || echo "")
        if echo "$LAST_LINE" | grep -qE '^EXIT_CODE: [0-9]+$'; then
            LOG_EXIT=$(echo "$LAST_LINE" | grep -oE '[0-9]+$')
            LOG_BASENAME=$(basename "$log_file")
            if grep -qF "$LOG_BASENAME" "$P6_FILE" 2>/dev/null && [ "$LOG_EXIT" != "0" ]; then
                echo "GATE PROVENANCE: ${LOG_BASENAME} 声明 PASS 但日志 EXIT_CODE=${LOG_EXIT}（矛盾）" >&2
                exit 1
            fi
        else
            echo "GATE PROVENANCE: $(basename "$log_file") 缺少标准 EXIT_CODE 尾行，跳过一致性核验（不阻塞）" >&2
        fi
    done < <(find "$TASK_DIR/P6-evidence" -name "*.log" 2>/dev/null)
fi

# --- 协作规范：agent 字段 ---
# 不做硬拦截（自报数据不可信），缺字段降级为 WARNING
# 安全审计（1/2/3）用 ERROR，协作规范用 WARNING——符合「不把自报字段当安全边界」原则
# WARNING 不立即 exit——记变量继续往下跑审计 6，最后统一判断 exit code

WARNING_FOUND=0

if [ -f "$P6_FILE" ]; then
    AGENT=$(get_agent "$P6_FILE")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: P6-acceptance.md 缺 agent 字段（协作规范，不阻塞）" >&2
        WARNING_FOUND=1
    fi
fi

# 所有阶段产出文件 agent 字段存在性（格式校验）
if [ -f "$P6_FILE" ]; then
for f in "$TASK_DIR"/P[0-8]-*.md; do
    [ -f "$f" ] || continue
    localname=$(basename "$f")
    [ "$localname" = "P0-brief.md" ] && continue
    case "$localname" in
        *-dispatch-context.md|*-dispatch-context-*.md|*-dispatch-prompt-*.md|*-progress.md|*-paused-resolution.md) continue ;;
    esac
    AGENT=$(get_agent "$f")
    if [ -z "$AGENT" ]; then
        echo "GATE PROVENANCE: $localname 缺 agent 字段（协作规范，不阻塞）" >&2
        WARNING_FOUND=1
    fi
    done
fi

# 审计 6: evidence JSON 与 P6 PASS/FAIL 声明一致性（P2.57）
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
if [ -d "$EVIDENCE_DIR" ]; then
    INCONSISTENCY=$(EVIDENCE_DIR="$EVIDENCE_DIR" P6_FILE="$TASK_DIR/P6-acceptance.md" python3 "$SCRIPT_DIR/agate-evidence-consistency.py" 2>/dev/null || echo "")
    if [ -n "$INCONSISTENCY" ]; then
        echo "GATE PROVENANCE: evidence JSON 与 P6-acceptance.md 声明不一致：" >&2
        echo "$INCONSISTENCY" | sed 's/^/  - /' >&2
        exit 1
    fi
fi

if [ "$WARNING_FOUND" -eq 1 ]; then
    exit 2
fi
exit 0
