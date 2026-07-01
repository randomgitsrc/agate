#!/usr/bin/env bash
# check-state-transition.sh — 状态转移合法性检查（Phase 2A: P2.3-P2.5）
# P2.3 phase 跳变合法性
# P2.4 重试超限 -> phase 必须是 PAUSED（按阶段差异化 MAX）
# P2.5 回退跳变 >= 2 -> 强制 PAUSED（恢复 exit 1，T019 教训）
#
# exit 0 = 合法; exit 1 = 非法

set -euo pipefail

STATE_FILE="${1:-.state.yaml}"
# 按阶段差异化 MAX_RETRY（P3/P5/P6/P7/P8=2, 其他=3）
# 与 check-retrospective.sh 的 MAX_RETRY_MAP 字面值保持同步
MAX_RETRY=3
MAX_RETRY_MAP="${MAX_RETRY_MAP:-P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2}"
export MAX_RETRY_MAP

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
    [ -f "$STATE_FILE" ] || return
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
# .gate-history.jsonl 的 PAUSED 验证功能已被 HEAD/staged diff 机制隐式覆盖
# （PAUSED 单独 commit 时 HEAD=PAUSED → L51-53 早退 exit 0）
# 保留 old_num > 0 守卫：PAUSED→Pn 恢复（old_num=0）不被误拦
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]; then
    diff=$((old_num - new_num))
    if [ "$diff" -ge 2 ]; then
        echo "GATE STATE: 回退跳变 P${old_num}→P${new_num}（差 ${diff}），强制 PAUSED" >&2
        exit 1
    fi
fi

# 检查 2：重试超限（P2.4，按阶段差异化 MAX）
# .state.yaml 的 retries[Pn] 是列表（每次重试一个对象），不是整数
# 按 retries dict 的 key 逐阶段查 MAX_RETRY，不是按 new_phase
if [ -f "$STATE_FILE" ]; then
    retries_json=$(STATE_FILE="$STATE_FILE" MAX_RETRY="$MAX_RETRY" MAX_RETRY_MAP="$MAX_RETRY_MAP" python3 -c "
import yaml, os
with open(os.environ['STATE_FILE']) as f:
    data = yaml.safe_load(f)
retries = data.get('retries', {})
max_retry = int(os.environ['MAX_RETRY'])
max_map_str = os.environ['MAX_RETRY_MAP']
max_map = dict(p.split(':') for p in max_map_str.split(','))
if isinstance(retries, dict):
    for phase, attempts in retries.items():
        phase_max = int(max_map.get(phase, 3))
        if isinstance(attempts, list) and len(attempts) >= phase_max:
            print(f'{phase}={len(attempts)} (MAX={phase_max})')
            break
" 2>/dev/null || echo "")

    if [ -n "$retries_json" ] && [ "$new_phase" != "PAUSED" ]; then
        echo "GATE STATE: ${retries_json}，phase 应为 PAUSED" >&2
        exit 1
    fi
fi

exit 0
