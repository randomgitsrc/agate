#!/usr/bin/env bash
# pre-commit-gate.sh — pre-commit hook 入口
# 安装到 .git/hooks/pre-commit，每次 git commit 自动触发。
#
# Phase 1: P1.1 跑 gate 写 .gate-result.json
#          P1.2 PROD_TOUCHED 检测
#          P1.6 CHANGELOG 检查
#          P1.7 P6 证据格式检查
# Phase 2A: P2.3-P2.5 状态转移检查
#           P2.15 .state.yaml 格式校验
#
# 触发条件：.state.yaml phase 变更 OR 阶段产出文件变更
#
# 多任务架构：扫描所有暂存的 .state.yaml（根 + docs/tasks/{Txxx}/）
# 单任务架构：向后兼容根 .state.yaml

set -euo pipefail

# REPO_ROOT = 当前 git 仓库根（项目仓库或 agate 仓库本身）
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# AGATE_ROOT = 协议本体路径（默认 ~/.agate 软链接 → 你克隆的 agate 仓库的 agate/ 子目录）
AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"
AGATE_TASKS_DIR="${AGATE_TASKS_DIR:-docs/tasks}"

# R1 修复：source 后验证函数已加载，防止静默放行
source "$AGATE_ROOT/scripts/gate-result.sh" \
    || { echo "GATE ERROR: 无法加载 gate-result.sh" >&2; exit 1; }
type write_gate_result >/dev/null 2>&1 \
    || { echo "GATE ERROR: gate-result.sh 加载不完整（write_gate_result 未定义）" >&2; exit 1; }

# 1. 收集所有暂存的 .state.yaml 文件（根 + 任务级）
STAGED_STATE_FILES=""
if git diff --cached --name-only 2>/dev/null | grep -qF ".state.yaml"; then
    while IFS= read -r f; do
        case "$f" in
            *.state.yaml)
                STAGED_STATE_FILES="${STAGED_STATE_FILES}${REPO_ROOT}/${f} "
                ;;
        esac
    done < <(git diff --cached --name-only 2>/dev/null | grep -F '.state.yaml' || true)
fi

# 2. 对每个暂存的 .state.yaml：格式校验 + 状态转移 + gate
for STATE_FILE in $STAGED_STATE_FILES; do
    [ -f "$STATE_FILE" ] || continue

    # 2a. 格式校验（任何变更都触发）
    bash "$AGATE_ROOT/scripts/check-state-yaml.sh" "$STATE_FILE" || exit 1

    # 2b. 检测 phase 是否变更
    STATE_REL=$(realpath --relative-to="$REPO_ROOT" "$STATE_FILE" 2>/dev/null || echo "$STATE_FILE")
    PHASE_CHANGED=false
    if git diff --cached -- "$STATE_REL" 2>/dev/null | grep -qE '^\+.*phase:'; then
        PHASE_CHANGED=true
    fi

    # 2c. 状态转移检查（phase 变更时）
    if [ "$PHASE_CHANGED" = true ]; then
        bash "$AGATE_ROOT/scripts/check-state-transition.sh" "$STATE_FILE" || exit 1
    fi

    # 2d. 读取状态
    PHASE=$(read_state_phase "$STATE_FILE")
    TASK_ID=$(read_state_task_id "$STATE_FILE")

    [ -z "$PHASE" ] && continue
    [ -z "$TASK_ID" ] && continue

    # 2e. 反推 TASK_DIR
    STATE_DIR=$(dirname "$STATE_FILE")
    # 如果 .state.yaml 在任务目录下，TASK_DIR = dirname
    # 如果 .state.yaml 在根目录，TASK_DIR = REPO_ROOT/AGATE_TASKS_DIR/TASK_ID
    if [ "$STATE_DIR" = "$REPO_ROOT" ]; then
        TASK_DIR="$REPO_ROOT/$AGATE_TASKS_DIR/$TASK_ID"
    else
        TASK_DIR="$STATE_DIR"
    fi

    # 2f. phase-产出一致性检查（WARNING，不拦截）
    # 只检查"暂存了 P{n}-*.md 产出但 phase 不匹配"的情况
    TASK_REL=$(realpath --relative-to="$REPO_ROOT" "$TASK_DIR" 2>/dev/null || echo "$TASK_DIR")
    STAGED_OUTPUTS=$(git diff --cached --name-only 2>/dev/null \
        | grep -E "^${TASK_REL}/P[0-8]-.*\.md$" || true)
    if [ -n "$STAGED_OUTPUTS" ]; then
        while IFS= read -r out_file; do
            [ -z "$out_file" ] && continue
            # 从文件名提取阶段号 Pn
            out_phase=$(echo "$out_file" | grep -oE 'P[0-8]' | head -1)
            if [ -n "$out_phase" ] && [ "$out_phase" != "$PHASE" ]; then
                echo "GATE WARNING: 暂存了 ${out_phase} 产出但 phase=${PHASE}（${TASK_ID}）——请确认是否需要更新 phase" >&2
            fi
        done <<< "$STAGED_OUTPUTS"
    fi

    # 2g. 跳过非 gate 阶段
    case "$PHASE" in
        PAUSED|READY|DONE) continue ;;
    esac

    [ ! -d "$TASK_DIR" ] && continue

    # 2g.1 PROD_TOUCHED 检测（P1.2）——仅扫任务目录下的暂存 diff
    # R3 修复：只扫任务产出文件，不扫协议/模板/项目文档（后者引用标记是说明性文本，非真正标记）
    # v0.17：三步检测（正向→中止 / 不合规→中止 / 缺失→静默通过）+ 只扫新增行
    TASK_REL=$(realpath --relative-to="$REPO_ROOT" "$TASK_DIR" 2>/dev/null || echo "$TASK_DIR")
    if git diff --cached --name-only 2>/dev/null | grep -qE "^${TASK_REL}/"; then
        DIFF_ADDED=$(git diff --cached -- "$TASK_REL" | grep '^+[^+]' | sed 's/^+//' || true)
        if echo "$DIFF_ADDED" | grep -qE '^\s*-?\s*\[PROD_TOUCHED\]'; then
            echo "GATE: [PROD_TOUCHED] 检测到生产环境接触（${TASK_ID}），commit 中止" >&2
            exit 1
        fi
        if echo "$DIFF_ADDED" | grep -q '\[PROD_TOUCHED\]'; then
            echo "GATE: 不合规的 PROD_TOUCHED 标记格式（${TASK_ID}），须用行首 [PROD_TOUCHED] 或 [PROD_NOT_TOUCHED] 声明" >&2
            exit 1
        fi
    fi

    # 2h. P6 格式自动归一化（①）——verifier 产出后、gate 前
    if [ "$PHASE" = "P6" ] && [ -f "$TASK_DIR/P6-acceptance.md" ]; then
        bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md" || true
        git add "$TASK_DIR/P6-acceptance.md" 2>/dev/null || true
    fi

    # 2h.1 运行 gate（P1.1）
    GATE_OUTPUT=""
    GATE_EXIT=2
    GATE_OUTPUT=$(bash "$AGATE_ROOT/scripts/check-gate.sh" "$PHASE" "$TASK_DIR" 2>&1) && GATE_EXIT=0 || GATE_EXIT=$?

    # 2h.1 写 gate 结果（供 CI backstop 检测 --no-verify 绕过）
    write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"

    # 2i. P6 客观行为审计（P2.1/P2.10）
    if [ "$GATE_EXIT" != "1" ]; then
        PROV_EXIT=0
        bash "$AGATE_ROOT/scripts/check-p6-provenance.sh" "$TASK_DIR" || PROV_EXIT=$?
        if [ "$PROV_EXIT" -eq 1 ]; then
            exit 1
        fi
    fi

    # 2j. 裁剪条件检查（P2.7-P2.9）
    if [ "$GATE_EXIT" != "1" ]; then
        PRUNE_EXIT=0
        bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || PRUNE_EXIT=$?
        if [ "$PRUNE_EXIT" -eq 1 ]; then
            exit 1
        fi
    fi

    # 2k. SCOPE+ 追踪检查（P2.11）
    if [ "$GATE_EXIT" != "1" ]; then
        SCOPE_EXIT=0
        bash "$AGATE_ROOT/scripts/check-scope-resolved.sh" "$TASK_DIR" || SCOPE_EXIT=$?
        if [ "$SCOPE_EXIT" -eq 1 ]; then
            exit 1
        fi
    fi

    # 2p. dispatch-context 卡片 hash 校验（防漂移：嵌入卡片是当前版本）
    # 所有 P1-P8 阶段统一强制 dispatch-context 存在
    if [ -x "$AGATE_ROOT/scripts/agate-next-card.sh" ]; then
        shopt -s nullglob
        DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)
        shopt -u nullglob
        if [ ${#DC_FILES[@]} -gt 0 ]; then
            EXPECTED=$(bash "$AGATE_ROOT/scripts/agate-next-card.sh" "$PHASE" 2>/dev/null) || true
            if [ -n "$EXPECTED" ]; then
                EXPECTED_HASH=$(printf '%s' "$EXPECTED" | sha256sum | awk '{print $1}')
                for DC_FILE in "${DC_FILES[@]}"; do
                    EMBEDDED=$(sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p' "$DC_FILE" \
                               | sed '1d;$d')
                    EMBEDDED_HASH=$(printf '%s' "$EMBEDDED" | sha256sum | awk '{print $1}')
                    if [ "$EMBEDDED_HASH" != "$EXPECTED_HASH" ]; then
                        echo "GATE: $(basename "$DC_FILE") 卡片内容与 CLI 输出不一致（hash mismatch）" >&2
                        echo "      期望 sha256: $EXPECTED_HASH" >&2
                        echo "      实际 sha256: $EMBEDDED_HASH" >&2
                        echo "      提示：重新调 agate-next-card.sh ${PHASE} 复制到 dispatch-context 文件" >&2
                        exit 1
                    fi
                done
            fi
        else
            # 仅当暂存了该阶段的产出文件时才强制要求 dispatch-context
            # 中间 commit / legacy 任务 / 裁剪跳阶 → 不强制
            STAGED_IN_TASK=$(git diff --cached --name-only 2>/dev/null | grep "^${TASK_REL}/" || true)
            PHASE_OUTPUT=""
            PHASE_OUTPUT_DIR=""
            case "$PHASE" in
                P1) PHASE_OUTPUT="P1-requirements\.md" ;;
                P2) PHASE_OUTPUT="P2-design\.md" ;;
                P3) PHASE_OUTPUT="P3-test-cases\.md" ;;
                P5) PHASE_OUTPUT_DIR="P5-test-results" ;;
                P6) PHASE_OUTPUT="P6-acceptance\.md" ;;
                P7) PHASE_OUTPUT="P7-consistency\.md" ;;
                P8) PHASE_OUTPUT="P8-release\.md" ;;
            esac
            HAS_OUTPUT=""
            if [ -n "$PHASE_OUTPUT" ] && echo "$STAGED_IN_TASK" | grep -q "$PHASE_OUTPUT"; then
                HAS_OUTPUT="yes"
            fi
            if [ -n "$PHASE_OUTPUT_DIR" ] && [ -d "$TASK_DIR/$PHASE_OUTPUT_DIR" ]; then
                HAS_OUTPUT="yes"
            fi
            if [ "$HAS_OUTPUT" = "yes" ]; then
                echo "GATE: subagent 派发阶段产出 commit 需提供 ${PHASE}-dispatch-context-{role}.md（至少一个，当前阶段卡片嵌入）" >&2
                echo "      提示：调 agate-next-card.sh ${PHASE} 嵌入 dispatch-context 模板" >&2
                exit 1
            fi
            # P4: 用代码文件判断（见 pre-commit-gate.sh 原有逻辑，不变）
            if [ "$PHASE" = "P4" ] && echo "$STAGED_IN_TASK" | grep -qvE '\.(md|yaml)$|^\.state'; then
                echo "GATE: subagent 派发阶段产出 commit 需提供 ${PHASE}-dispatch-context-{role}.md（至少一个，当前阶段卡片嵌入）" >&2
                echo "      提示：调 agate-next-card.sh ${PHASE} 嵌入 dispatch-context 模板" >&2
                exit 1
            fi
        fi
    fi

    # 2l. 复盘异常触发（P2.12）——只提醒不中止
    bash "$AGATE_ROOT/scripts/check-retrospective.sh" "$TASK_DIR" "$STATE_FILE" 2>/dev/null || true

    # 2m. CHANGELOG 检查（P1.6）——警告不中止
    bash "$AGATE_ROOT/scripts/check-changelog.sh" "$TASK_ID" 2>/dev/null || \
        echo "GATE CHANGELOG: 警告 — [Unreleased] 未记录 ${TASK_ID}" >&2

    # 2n. P6 证据格式检查（P1.7）
    if [ "$PHASE" = "P6" ] || [ "$PHASE" = "P7" ]; then
        bash "$AGATE_ROOT/scripts/check-p6-evidence.sh" "$TASK_DIR" || exit 1
    fi

    # 2n.1 dispatch-context missing WARNING (B3)
    # Only warn when 2p hash check is not active (agate-next-card.sh not available)
    if [ ! -x "$AGATE_ROOT/scripts/agate-next-card.sh" ]; then
        STAGED_OUTPUT_IN_TASK=$(git diff --cached --name-only 2>/dev/null \
            | grep -E "^${TASK_REL}/P[0-8]-.*\.md$" || true)
        if [ -n "$STAGED_OUTPUT_IN_TASK" ]; then
            shopt -s nullglob
            DC_GLOB=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)
            shopt -u nullglob
            if [ ${#DC_GLOB[@]} -eq 0 ]; then
                # Check if old format exists in HEAD (transitional)
                HAS_DC_IN_HEAD=$(git ls-tree HEAD "${TASK_REL}/" 2>/dev/null | grep -qE "${PHASE}-dispatch-context-.*\.md$" && echo yes || echo no)
                if [ "$HAS_DC_IN_HEAD" = "no" ]; then
                    echo "GATE WARNING: ${PHASE} 产出已暂存但 ${PHASE}-dispatch-context-*.md 不存在——是否忘记先写 dispatch-context？" >&2
                fi
            fi
        fi
    fi

    # 2n.2 non-phase code staging WARNING (E3)
    CODE_FILES=$(git diff --cached --name-only 2>/dev/null | grep -vE '\.(md|yaml)$|^\.state' || true)
    if [ -n "$CODE_FILES" ]; then
        case "$PHASE" in
            P4|P5|P6) ;;
            *)
                echo "GATE WARNING: phase=$PHASE 但暂存了代码文件——主 Agent 是否在非实现阶段直接改代码？" >&2
                ;;
        esac
    fi

    # 2o. gate 结果处理
    case "$GATE_EXIT" in
        0) echo "GATE $PHASE ($TASK_ID): 通过" >&2 ;;
        1) echo "GATE $PHASE ($TASK_ID): 未通过" >&2; echo "$GATE_OUTPUT" >&2; exit 1 ;;
        2) echo "GATE $PHASE ($TASK_ID): 需主 Agent 手动判断" >&2; echo "$GATE_OUTPUT" >&2 ;;
    esac
done

# 3. 扫描暂存的 P{n}-*.md 产出文件（无 .state.yaml 变更的任务也检查一致性）
# 只做 WARNING，不拦截——覆盖"产出了但忘改 phase"的场景
PROCESSED_DIRS=""
for STATE_FILE in $STAGED_STATE_FILES; do
    [ -f "$STATE_FILE" ] || continue
    STATE_DIR=$(dirname "$STATE_FILE")
    [ "$STATE_DIR" = "$REPO_ROOT" ] && continue
    PROCESSED_DIRS="${PROCESSED_DIRS}${STATE_DIR} "
done

while IFS= read -r staged_file; do
    [ -z "$staged_file" ] && continue
    # 从路径提取任务目录：docs/tasks/{Txxx}/P{n}-*.md
    task_dir_rel=$(echo "$staged_file" | sed -E 's|^(.*/P[0-8]-[^/]+\.md)$|\1|; s|/P[0-8]-[^/]+$||')
    [ -z "$task_dir_rel" ] && continue
    # 跳过已被 .state.yaml 扫描处理的任务
    case " $PROCESSED_DIRS " in
        *" $REPO_ROOT/$task_dir_rel "*) continue ;;
    esac
    # 读该任务的 .state.yaml（如果存在）
    task_state="$REPO_ROOT/$task_dir_rel/.state.yaml"
    [ -f "$task_state" ] || continue
    task_phase=$(read_state_phase "$task_state")
    [ -z "$task_phase" ] && continue
    # 从文件名提取阶段号
    out_phase=$(echo "$staged_file" | grep -oE 'P[0-8]' | head -1)
    [ -n "$out_phase" ] || continue
    if [ "$out_phase" != "$task_phase" ]; then
        echo "GATE WARNING: 暂存了 ${out_phase} 产出但 phase=${task_phase}（${task_dir_rel##*/}）——请确认是否需要更新 phase" >&2
    fi
done < <(git diff --cached --name-only 2>/dev/null | grep -E 'P[0-8]-.*\.md$' || true)

exit 0
