#!/usr/bin/env bash
# gate-result.sh — .gate-result.json 生成 + .gate-history.jsonl 追加
# 被 pre-commit-gate.sh 调用，不直接执行。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# write_gate_result PHASE TASK_ID EXIT_CODE OUTPUT
write_gate_result() {
    local phase="$1"
    local task_id="$2"
    local exit_code="$3"
    local output="$4"
    local ts prev_commit_sha

    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    # pre-commit hook 在 commit 创建之前运行，HEAD 是上一个 commit
    # 字段名 prev_commit_sha 明确语义，避免误读为"本次 commit SHA"（O3 修复）
    prev_commit_sha=$(git rev-parse HEAD 2>/dev/null || echo "pre-commit")

    cat > .gate-result.json <<EOF
{
  "phase": "${phase}",
  "task_id": "${task_id}",
  "exit_code": ${exit_code},
  "timestamp": "${ts}",
  "output": $(printf '%s' "$output" | python3 "$SCRIPT_DIR/agate-json-get.py" escape),
  "runner": "pre-commit-hook",
  "prev_commit_sha": "${prev_commit_sha}"
}
EOF

    printf '{"phase":"%s","task_id":"%s","exit_code":%d,"timestamp":"%s","prev_commit_sha":"%s"}\n' \
        "$phase" "$task_id" "$exit_code" "$ts" "$prev_commit_sha" >> .gate-history.jsonl
}

read_state_phase() {
    local state_file="$1"
    [ ! -f "$state_file" ] && { echo ""; return; }
    STATE_FILE="$state_file" python3 "$SCRIPT_DIR/agate-state-get.py" phase 2>/dev/null || echo ""
}

read_state_task_id() {
    local state_file="$1"
    [ ! -f "$state_file" ] && { echo ""; return; }
    STATE_FILE="$state_file" python3 "$SCRIPT_DIR/agate-state-get.py" task_id 2>/dev/null || echo ""
}

has_staged_phase_change() {
    local state_file="$1"
    local basename
    basename=$(basename "$state_file")
    # tr -d '\r'：Git for Windows diff 输出 CRLF 行尾，grep 精确匹配会失败（TAG0009）
    git diff --cached --name-only 2>/dev/null | tr -d '\r' | grep -qF "$basename" || return 1
    git diff --cached -- "$basename" 2>/dev/null | grep -qE '^\+.*phase:' || return 1
    return 0
}

has_staged_phase_output() {
    git diff --cached --name-only 2>/dev/null | tr -d '\r' | grep -qE 'P[0-9]+-.*\.(md|yaml)$' || return 1
    return 0
}

resolve_formatter() {
    local fmt="$1"
    local task_dir="${2:-}"
    local agate_root="${AGATE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
    [ "${fmt:0:1}" = "/" ] && { [ -f "$fmt" ] && { echo "$fmt"; return 0; } || return 1; }
    if [ -n "$task_dir" ] && [ -f "$task_dir/.agate/formatters/$fmt" ]; then
        echo "$task_dir/.agate/formatters/$fmt"
    elif [ -f "$agate_root/assets/formatters/$fmt" ]; then
        echo "$agate_root/assets/formatters/$fmt"
    else
        return 1
    fi
}

run_test_with_formatter() {
    local cmd="$1"
    local fmt_path="$2"
    local exit_code output raw_json
    local timeout_secs="${AGATE_TDD_TIMEOUT:-120}"
    if command -v timeout &>/dev/null; then
        output=$(timeout "$timeout_secs" bash -c "$cmd" 2>&1) && exit_code=0 || exit_code=$?
    else
        output=$(eval "$cmd" 2>&1) && exit_code=0 || exit_code=$?
    fi
    if [ "$exit_code" -eq 124 ]; then
        echo "TDD_CHECK: 测试命令超时（${timeout_secs}s），请手动运行确认：$cmd" >&2
        echo "{\"exit_code\":124,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[]}"
        return 0
    fi
    if [ -z "$fmt_path" ]; then
        raw_json=$(printf '%s' "$output" | python3 "$SCRIPT_DIR/agate-json-get.py" escape)
        echo "{\"exit_code\":$exit_code,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[],\"name_errors\":[],\"raw_output\":$raw_json}"
    else
        local json_result
        json_result=$(echo "$output" | bash "$fmt_path" "$exit_code" 2>/dev/null) || {
            raw_json=$(printf '%s' "$output" | python3 "$SCRIPT_DIR/agate-json-get.py" escape)
            echo "{\"exit_code\":$exit_code,\"total\":0,\"passed\":0,\"failed\":0,\"errors\":0,\"failed_tests\":[],\"import_errors\":[],\"syntax_errors\":[],\"name_errors\":[],\"raw_output\":$raw_json}"
        }
        echo "$json_result"
    fi
}
