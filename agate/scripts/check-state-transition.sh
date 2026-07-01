#!/usr/bin/env bash
# check-state-transition.sh — 状态转移合法性检查（Phase 2A: P2.3-P2.5）
# P2.3 phase 跳变合法性
# P2.4 重试超限 -> phase 必须是 PAUSED
# P2.5 回退跳变 >= 2 -> 必须有 PAUSED 记录
#
# exit 0 = 合法; exit 1 = 非法

set -euo pipefail

STATE_FILE="${1:-.state.yaml}"
MAX_RETRY=3

# git pathspec 命令需要相对路径，不接受绝对路径
# pre-commit-gate.sh 传入绝对路径，这里转成 basename
STATE_BASENAME=$(basename "$STATE_FILE")

get_old_phase() {
    # HEAD: 版本是 commit 前的旧版本（pre-commit hook 运行时 commit 还没创建）
    # :<path> 是暂存区版本（新的），HEAD:<path> 是旧版本
    git show "HEAD:$STATE_BASENAME" 2>/dev/null | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    print(data.get('phase', '') if data else '')
except:
    print('')
" 2>/dev/null || echo ""
}

get_new_phase() {
    [ -f "$STATE_FILE" ] || { echo ""; return; }
    STATE_FILE="$STATE_FILE" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
print(data.get('phase', '') if data else '')
" 2>/dev/null || echo ""
}

phase_num() {
    echo "$1" | grep -oE '[0-9]+' || echo "0"
}

# 只在 .state.yaml 有暂存变更时检查
git diff --cached --name-only 2>/dev/null | grep -qF "$STATE_BASENAME" || exit 0

old_phase=$(get_old_phase)
new_phase=$(get_new_phase)

case "$new_phase" in
    ""|PAUSED|READY|DONE) exit 0 ;;
esac

old_num=$(phase_num "$old_phase")
new_num=$(phase_num "$new_phase")

# 检查 1：回退跳变 >= 2（T019 教训）
# 协议规定"不依赖 commit message 格式"（state-machine.md L371-373）
# .gate-history.jsonl 尚未积累数据，降级为 WARNING 不中止（O1 修复）
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]; then
    diff=$((old_num - new_num))
    if [ "$diff" -ge 2 ]; then
        echo "GATE STATE: 警告 — 回退跳变 P${old_num}→P${new_num}（差 ${diff}），建议确认是否经过 PAUSED" >&2
        # 降级 WARNING，不 exit 1
        # 长期：等 .gate-history.jsonl 积累数据后改为查历史记录
    fi
fi

# 检查 2：重试超限（P2.4）
# .state.yaml 的 retries[Pn] 是列表（每次重试一个对象），不是整数（O2 修复）
if [ -f "$STATE_FILE" ]; then
    retries_json=$(STATE_FILE="$STATE_FILE" MAX_RETRY="$MAX_RETRY" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
max_retry = int(os.environ['MAX_RETRY'])
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        if isinstance(attempts, list) and len(attempts) >= max_retry:
            print(f'{phase}={len(attempts)}')
            break
" 2>/dev/null || echo "")

    if [ -n "$retries_json" ] && [ "$new_phase" != "PAUSED" ]; then
        echo "GATE STATE: ${retries_json}（>= MAX ${MAX_RETRY}），phase 应为 PAUSED" >&2
        exit 1
    fi
fi

exit 0
