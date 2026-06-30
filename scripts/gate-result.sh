#!/usr/bin/env bash
# gate-result.sh — .gate-result.json 生成 + .gate-history.jsonl 追加
# 被 pre-commit-gate.sh 调用，不直接执行。

set -euo pipefail

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
  "output": $(printf '%s' "$output" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'),
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
    python3 -c "
import yaml
with open('$state_file') as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
}

read_state_task_id() {
    local state_file="$1"
    [ ! -f "$state_file" ] && { echo ""; return; }
    python3 -c "
import yaml
with open('$state_file') as f:
    data = yaml.safe_load(f)
print(data.get('task_id', '') if data else '')
" 2>/dev/null || echo ""
}

has_staged_phase_change() {
    local state_file="$1"
    local basename
    basename=$(basename "$state_file")
    git diff --cached --name-only 2>/dev/null | grep -qF "$basename" || return 1
    git diff --cached -- "$basename" 2>/dev/null | grep -qE '^\+.*phase:' || return 1
    return 0
}

has_staged_phase_output() {
    git diff --cached --name-only 2>/dev/null | grep -qE 'P[0-9]+-.*\.(md|yaml)$' || return 1
    return 0
}
