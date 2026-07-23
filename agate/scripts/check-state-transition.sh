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
    local git_path="$STATE_BASENAME"
    # 任务级 .state.yaml：保留完整路径（如 docs/tasks/T001/.state.yaml）
    if echo "$STATE_FILE" | grep -qE 'docs/tasks/[^/]+/'; then
        git_path="$STATE_FILE"
    fi
    git show "HEAD:$git_path" 2>/dev/null | python3 -c "
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

# 检查 3：pre-phase-change commit gate（逐阶段 commit 强制）
# 从 P{n} 推进到 P{n+1} 时，P{n} 产出必须已 commit
# 仅适用于任务级 .state.yaml（docs/tasks/Txxx/.state.yaml），根 .state.yaml 跳过
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ] && [ "$new_num" -gt "$old_num" ] \
   && [ "$old_phase" != "PAUSED" ]; then
    TASK_DIR=$(dirname "$STATE_FILE")
    # 仅任务级 .state.yaml 需要 commit gate（根 .state.yaml 无法映射 task 路径）
    if echo "$STATE_FILE" | grep -qE 'docs/tasks/[^/]+/'; then
        REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
        TASK_REL=$(realpath --relative-to="$REPO_ROOT" "$TASK_DIR" 2>/dev/null || echo "$TASK_DIR")

    _phase_output_for() {
        case "$1" in
            P0) echo "P0-brief.md" ;;
            P1) echo "P1-requirements.md" ;;
            P2) echo "P2-design.md" ;;
            P3) echo "P3-test-cases.md" ;;
            P4) ;;  # scope out — 代码在项目任意路径，无法 task-scoped 关联
            P5) ;;  # 用文件存在性检查，不走路径
            P6) echo "P6-acceptance.md" ;;
            P7) echo "P7-consistency.md" ;;
            P8) echo "P8-release.md" ;;
        esac
    }

    OLD_OUTPUT=$(_phase_output_for "$old_phase")

    if [ -n "$OLD_OUTPUT" ]; then
        # 产出在暂存区但未 commit → 拦截（产出和推进不能同一个 commit）
        if git diff --cached --name-only | grep -q "^${TASK_REL}/${OLD_OUTPUT}"; then
            echo "GATE STATE: 在推进到 ${new_phase} 前，${old_phase} 产出必须已 commit" >&2
            echo "      提示：先 git commit ${old_phase} 产出再改 phase" >&2
            exit 1
        fi
        # 产出从未被 commit（不在暂存区也不在 HEAD）
        # 注：git ls-files 退出码恒 0，用输出判空而非退出码
        if [ -z "$(git ls-files "$TASK_REL/$OLD_OUTPUT")" ]; then
            echo "GATE STATE: ${old_phase} 产出 ${OLD_OUTPUT} 尚未 commit" >&2
            echo "      提示：先 commit ${old_phase} 产出再推进 phase" >&2
            exit 1
        fi
    fi

    # P5 特殊处理：目录级检查
    if [ "$old_phase" = "P5" ] && [ ! -d "$TASK_DIR/P5-test-results" ]; then
        echo "GATE STATE: ${old_phase} 产出 P5-test-results/ 目录不存在" >&2
        exit 1
    fi
    fi  # 任务级 .state.yaml guard
fi  # 检查 3 外层：向前推进 + 非 PAUSED

# 检查 4：回退时若被跨过阶段是 self-authored 产出阶段（P1/P2/P6/P7），
# 且该阶段的产出文件仍在原位（未归档）-> 拦截，要求先跑 agate-archive-stale-outputs.sh
# （self-authored gate 产出不能跨重试静默复用，见 LIMITATIONS.md self-authored 分类）
# 文件列表须与 agate-archive-stale-outputs.sh 的 _outputs_for() 保持一致
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ] && [ "$diff" -eq 1 ]; then
    case "$old_phase" in
        P1|P2|P6|P7)
            TASK_DIR=$(dirname "$STATE_FILE")
            STALE_FOUND=""
            case "$old_phase" in
                P1)
                    for f in P1-requirements.md P1-review.md; do
                        [ -f "$TASK_DIR/$f" ] && STALE_FOUND="$f" && break
                    done
                    ;;
                P2)
                    for f in P2-design.md P2-review.md; do
                        [ -f "$TASK_DIR/$f" ] && STALE_FOUND="$f" && break
                    done
                    ;;
                P6) [ -f "$TASK_DIR/P6-acceptance.md" ] && STALE_FOUND="P6-acceptance.md" ;;
                P7) [ -f "$TASK_DIR/P7-consistency.md" ] && STALE_FOUND="P7-consistency.md" ;;
            esac
            if [ -n "$STALE_FOUND" ]; then
                echo "GATE STATE: 回退 P${old_num}->P${new_num}，但 ${old_phase} 的自撰产出（${STALE_FOUND}）仍在原位" >&2
                echo "  退回前须先跑：bash agate/scripts/agate-archive-stale-outputs.sh ${old_phase} ${TASK_DIR}" >&2
                echo "  （self-authored gate 产出不能跨重试静默复用，见 LIMITATIONS.md self-authored 分类）" >&2
                exit 1
            fi
            ;;
    esac
fi

exit 0
