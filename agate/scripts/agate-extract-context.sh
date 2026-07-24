#!/usr/bin/env bash
# agate-extract-context.sh — 从上游产出提取结构化字段，注入 dispatch-context 上游关联节
# 用法：
#   agate-extract-context.sh PHASE TASK_DIR           # 输出到 stdout
#   agate-extract-context.sh PHASE TASK_DIR --write    # 追加到 dispatch-context 文件
#
# PHASE 取值 P1-P8
# TASK_DIR 是任务目录路径（含 P0-brief.md 等）
#
# exit 0：成功
# exit 1：参数错误
# exit 2：phase 不在 P1-P8 范围或任务目录不存在

set -euo pipefail

SCRIPT_REAL="$(readlink -f "${BASH_SOURCE[0]:-$0}" 2>/dev/null || echo "${BASH_SOURCE[0]:-$0}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_REAL")" 2>/dev/null && pwd || true)"
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$SCRIPT_DIR")}"

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "用法: agate-extract-context.sh PHASE TASK_DIR [--write]" >&2
    exit 1
fi

PHASE="$1"
TASK_DIR="$2"
WRITE_MODE="${3:-}"

case "$PHASE" in
    P1|P2|P3|P4|P5|P6|P7|P8) ;;
    *)
        echo "agate-extract-context.sh: phase '$PHASE' 不在 P1-P8 范围内" >&2
        exit 2
        ;;
esac

if [ ! -d "$TASK_DIR" ]; then
    echo "agate-extract-context.sh: 任务目录不存在: $TASK_DIR" >&2
    exit 2
fi

extract() {
    local phase="$1"
    local task_dir="$2"
    local output=""

    case "$phase" in
        P1)
            if [ -f "$task_dir/P0-brief.md" ]; then
                output+="### P0-brief 关键字段"$'\n'
                local task_line
                task_line="$(grep -E '^task:' "$task_dir/P0-brief.md" 2>/dev/null || true)"
                [ -n "$task_line" ] && output+="- ${task_line}"$'\n'
                local risks
                risks="$(grep -E '^known_risks:' "$task_dir/P0-brief.md" 2>/dev/null || true)"
                [ -n "$risks" ] && output+="- ${risks}"$'\n'
                local env
                env="$(grep -A5 '^env_constraints:' "$task_dir/P0-brief.md" 2>/dev/null | head -6 || true)"
                [ -n "$env" ] && output+="- env_constraints:"$'\n'"${env}"$'\n'
            fi
            ;;
        P2)
            if [ -f "$task_dir/P1-requirements.md" ]; then
                output+="### P1-requirements 关键字段"$'\n'
                local domains
                domains="$(grep -E '^domains:' "$task_dir/P1-requirements.md" 2>/dev/null || true)"
                [ -n "$domains" ] && output+="- ${domains}"$'\n'
                local risk
                risk="$(grep -E '^risk_level:' "$task_dir/P1-requirements.md" 2>/dev/null || true)"
                [ -n "$risk" ] && output+="- ${risk}"$'\n'
                local bdd_count
                bdd_count="$(grep -cE '^#### BDD-' "$task_dir/P1-requirements.md" 2>/dev/null || echo 0 | tail -1)"
                output+="- BDD 条件数: ${bdd_count}"$'\n'
            fi
            ;;
        P3)
            if [ -f "$task_dir/P2-design.md" ]; then
                output+="### P2-design 关键字段"$'\n'
                local fields
                fields="$(grep -E '^(packages|domains|ui_affected|gate_commands):' "$task_dir/P2-design.md" 2>/dev/null || true)"
                [ -n "$fields" ] && output+="${fields}"$'\n'
            fi
            ;;
        P4)
            if [ -f "$task_dir/P2-design.md" ]; then
                output+="### P2-design 关键字段"$'\n'
                local fields
                fields="$(grep -E '^(packages|domains|ui_affected|gate_commands|files_to_read):' "$task_dir/P2-design.md" 2>/dev/null || true)"
                [ -n "$fields" ] && output+="${fields}"$'\n'
            fi
            if [ -f "$task_dir/P3-test-cases.md" ]; then
                local bdd_count
                bdd_count="$(grep -cE '^#### BDD-' "$task_dir/P3-test-cases.md" 2>/dev/null || echo 0 | tail -1)"
                output+="- P3 BDD 测试覆盖数: ${bdd_count}"$'\n'
            fi
            ;;
        P5)
            if [ -f "$task_dir/P2-design.md" ]; then
                output+="### P2-design gate_commands"$'\n'
                local gc
                gc="$(grep -A5 '^gate_commands:' "$task_dir/P2-design.md" 2>/dev/null | head -6 || true)"
                [ -n "$gc" ] && output+="${gc}"$'\n'
            fi
            local impl_dirs
            impl_dirs="$(grep -rh '^implementation_dir:' "$task_dir/P4-implementation.md" "$task_dir/P4-implementation/" 2>/dev/null || true)"
            if [ -n "$impl_dirs" ]; then
                output+="### implementation_dir"$'\n'
                while IFS= read -r line; do
                    [ -n "$line" ] && output+="- ${line}"$'\n'
                done <<< "$impl_dirs"
            fi
            ;;
        P6)
            if [ -f "$task_dir/P1-requirements.md" ]; then
                output+="### P1 BDD 编号列表"$'\n'
                local bdd_list
                bdd_list="$(grep -E '^#### (BDD-[^:]+):' "$task_dir/P1-requirements.md" 2>/dev/null | sed 's/^#### //' | sed 's/:.*//' || true)"
                if [ -n "$bdd_list" ]; then
                    while IFS= read -r line; do
                        [ -n "$line" ] && output+="- ${line}"$'\n'
                    done <<< "$bdd_list"
                else
                    output+="- (无 BDD 条件)"$'\n'
                fi
            fi
            if [ -d "$task_dir/P5-test-results" ]; then
                local failed
                failed="$(grep -rh '^\s*failed:' "$task_dir/P5-test-results/" 2>/dev/null | grep -oE '[0-9]+' | paste -sd+ 2>/dev/null | bc 2>/dev/null || echo 0 | tail -1)"
                output+="- P5 failed 参考: ${failed}（仅供参考，gate 以主 Agent 实跑为准）"$'\n'
            fi
            ;;
        P7)
            if [ -f "$task_dir/P2-design.md" ]; then
                output+="### P2-design packages"$'\n'
                local pkgs
                pkgs="$(grep -E '^packages:' "$task_dir/P2-design.md" 2>/dev/null || true)"
                [ -n "$pkgs" ] && output+="- ${pkgs}"$'\n'
            fi
            if [ -f "$task_dir/P6-acceptance.md" ]; then
                local pass_count fail_count
                pass_count="$(grep -cE '^\s*- PASS' "$task_dir/P6-acceptance.md" 2>/dev/null || echo 0 | tail -1)"
                fail_count="$(grep -cE '^\s*- FAIL' "$task_dir/P6-acceptance.md" 2>/dev/null || echo 0 | tail -1)"
                output+="- P6 验收: ${pass_count} PASS, ${fail_count} FAIL"$'\n'
                local gaps
                gaps="$(grep -E '\[DESIGN_GAP:' "$task_dir/P6-acceptance.md" 2>/dev/null || true)"
                [ -n "$gaps" ] && output+="- DESIGN_GAP 列表:"$'\n'"${gaps}"$'\n'
            fi
            ;;
        P8)
            if [ -f "$task_dir/P2-design.md" ]; then
                output+="### P2-design packages"$'\n'
                local pkgs
                pkgs="$(grep -E '^packages:' "$task_dir/P2-design.md" 2>/dev/null || true)"
                [ -n "$pkgs" ] && output+="- ${pkgs}"$'\n'
            fi
            if [ -f "$task_dir/P7-consistency.md" ]; then
                local blockers deviations
                blockers="$(grep -cE '\[BLOCKER\]' "$task_dir/P7-consistency.md" 2>/dev/null || echo 0 | tail -1)"
                deviations="$(grep -E '\[DEVIATION' "$task_dir/P7-consistency.md" 2>/dev/null || true)"
                output+="- P7 BLOCKER 数: ${blockers}"$'\n'
                [ -n "$deviations" ] && output+="- DEVIATION 列表:"$'\n'"${deviations}"$'\n'
            fi
            ;;
    esac

    if [ -f "$task_dir/P${PHASE#P}-gate-diagnosis.md" ]; then
        output+=$'\n'"### gate-diagnosis 引用"$'\n'
        output+="- 参见 P${PHASE#P}-gate-diagnosis.md"$'\n'
    fi

    printf '%s' "$output"
}

result="$(extract "$PHASE" "$TASK_DIR")"

if [ "$WRITE_MODE" = "--write" ]; then
    dc_file="$(find "$TASK_DIR" -maxdepth 1 -name "P${PHASE#P}-dispatch-context-*.md" 2>/dev/null | head -1 || true)"
    if [ -n "$dc_file" ]; then
        printf '\n%s\n' "$result" >> "$dc_file"
        echo "已追加到 $dc_file"
    else
        echo "agate-extract-context.sh: 未找到 P${PHASE#P}-dispatch-context-*.md，输出到 stdout" >&2
        printf '%s\n' "$result"
    fi
else
    printf '%s\n' "$result"
fi
