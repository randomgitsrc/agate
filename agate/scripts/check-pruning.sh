#!/usr/bin/env bash
# check-pruning.sh — 裁剪条件检查（P2.7-P2.9）
# 检查 P1-requirements.md 的 risk_level + phases 声明是否符合裁剪条件
# exit 0 = 通过; exit 1 = 裁剪条件不满足; exit 2 = 无 P1 文件

set -euo pipefail

TASK_DIR="${1:?用法: check-pruning.sh TASK_DIR}"
P1_FILE="$TASK_DIR/P1-requirements.md"

[ ! -f "$P1_FILE" ] && exit 2

# R1 修复：所有 Python 调用用环境变量传参，避免 shell 变量注入
RISK_LEVEL=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'risk_level:\s*(low|medium|high)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")

PHASES_DECLARED=$(P1_FILE="$P1_FILE" python3 -c "
import re, os
with open(os.environ['P1_FILE']) as f:
    text = f.read()
m = re.search(r'phases:\s*\[([^\]]+)\]', text)
if m:
    phases = [p.strip() for p in m.group(1).split(',')]
    print(' '.join(phases))
" 2>/dev/null || echo "")

# P2.9：裁剪声明与执行一致性检查
# 逻辑：P1 声明裁剪的阶段，如果文件系统里实际有该阶段的产出文件
# → 声明与执行不符 → 必须有 override: 字段记录原因
HAS_OVERRIDE=$(grep -c '^override:' "$P1_FILE" 2>/dev/null || true)
HAS_OVERRIDE=${HAS_OVERRIDE:-0}
HAS_OVERRIDE=$(echo "$HAS_OVERRIDE" | tail -1)

ERRORS=""

# 检查 1：risk_level 必须存在
if [ -z "$RISK_LEVEL" ]; then
    ERRORS="${ERRORS}P1-requirements.md 缺 risk_level 字段\n"
fi

# 检查 2：P2 不可裁剪（除非 design_trivial / follows_existing_pattern / legacy_p2_pruned）
if ! echo "$PHASES_DECLARED" | grep -qw 'P2'; then
    # 过渡期：legacy_p2_pruned 字段放行（一次性迁移标记）
    if grep -qE '^legacy_p2_pruned:\s*true' "$P1_FILE" 2>/dev/null; then
        : # 放行，不报错
    # 例外口 1：design_trivial（typo / 文案 / 配置值修改）
    elif grep -qE '^design_trivial:\s*true' "$P1_FILE" 2>/dev/null; then
        : # 放行
    # 例外口 2：follows_existing_pattern（须含参照文件路径 [xxx]）
    elif grep -qE '^follows_existing_pattern:\s*\[[^]]+\]' "$P1_FILE" 2>/dev/null; then
        : # 放行
    else
        ERRORS="${ERRORS}P2 不可裁剪（例外口：design_trivial: true / follows_existing_pattern: [参照文件] / legacy_p2_pruned: true）\n"
    fi
fi

# 检查 3：裁剪 P6 的条件（不可裁，除非 no_behavior_change）
if ! echo "$PHASES_DECLARED" | grep -qw 'P6'; then
    if ! grep -q 'no_behavior_change:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}P6 不可裁剪（除非 no_behavior_change: true）\n"
    fi
fi

# 检查 4：裁剪 P3 的条件
if ! echo "$PHASES_DECLARED" | grep -qw 'P3'; then
    if [ "$RISK_LEVEL" = "high" ]; then
        ERRORS="${ERRORS}高风险任务不可裁剪 P3\n"
    fi
fi

# 检查 5：裁剪 P7 的条件（R4：bug fix + implicit_coupling 维度）
if ! echo "$PHASES_DECLARED" | grep -qw 'P7'; then
    # R4(a) bug fix：补实现已文档化的文件数条件
    # ⚠️ 用 --cached（暂存区），不用 HEAD~1（pre-commit 时本次变更还没进 HEAD）
    SOURCE_FILE_COUNT=$(git diff --cached --name-only 2>/dev/null \
        | grep -cvE '^docs/tasks/|\.state\.yaml$|/P[0-8]-.*\.md$|^\.|CHANGELOG' || echo 0)
    SOURCE_FILE_COUNT=$(echo "$SOURCE_FILE_COUNT" | tail -1)

    if [ "$SOURCE_FILE_COUNT" -gt 5 ]; then
        ERRORS="${ERRORS}裁剪 P7 需源码文件数 ≤ 5，实际=${SOURCE_FILE_COUNT}\n"
    fi

    # R4(b)：implicit_coupling 维度（self-declaration nudge）
    # 通用字段：analyst 声明改动涉及隐式耦合（共享 CSS class / API schema / 数据模型 / 配置项等）
    # 局限性：hook 只能检查字段存在性，不能检查声明准确性
    if grep -qE '^implicit_coupling:' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P7 不可行：P1 声明了 implicit_coupling（隐式耦合维度）\n"
    fi
fi

# 检查 6：裁剪 P8 的条件（R5：internal_only 声明）
if ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    if ! grep -qE '^internal_only:\s*true' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪 P8 需声明 internal_only: true + 理由\n"
    fi
fi

# 检查 7：裁剪理由必须含"跳过风险"评估（R3a：self-declaration nudge）
if ! echo "$PHASES_DECLARED" | grep -qw 'P2' || ! echo "$PHASES_DECLARED" | grep -qw 'P3' || ! echo "$PHASES_DECLARED" | grep -qw 'P7' || ! echo "$PHASES_DECLARED" | grep -qw 'P8'; then
    if ! grep -qE '跳过风险:' "$P1_FILE" 2>/dev/null; then
        ERRORS="${ERRORS}裁剪声明缺'跳过风险:'评估（nudge：强制思考裁剪风险）\n"
    fi
fi

# P2.9 实际实现：对比 P1 phases 声明与文件系统中的产出文件
# 对每个被声明裁剪的阶段（P1/P3/P4/P5/P6/P7/P8），检查 task 目录下是否有该阶段的产出文件
# 如果声明裁剪了 Pn 但 Pn-*.md 存在 → 声明与执行不符 → 必须有 override
PRUNED_WITH_OUTPUT=""
for phase in P1 P2 P3 P4 P5 P6 P7 P8; do
    # P1 必填不裁剪，跳过
    [ "$phase" = "P1" ] && continue
    # P4/P5 不可裁剪（协议硬约束），但有 override 可保留
    # 这里只检查"被声明裁剪但实际有产出"的矛盾
    if echo "$PHASES_DECLARED" | grep -qw "$phase"; then
        continue  # 阶段未被裁剪，跳过
    fi
    # 阶段被声明裁剪，检查是否有该阶段的产出文件
    # shellcheck disable=SC2231
    for f in "$TASK_DIR"/${phase}-*.md; do
        [ -f "$f" ] || continue
        # P2-implementation.md 实际上是 P4-implementation 的别名？不，严格按 P{n}- 开头
        PRUNED_WITH_OUTPUT="${PRUNED_WITH_OUTPUT}${phase}:$(basename "$f") "
    done
done

if [ -n "$PRUNED_WITH_OUTPUT" ]; then
    if [ "$HAS_OVERRIDE" -eq 0 ]; then
        ERRORS="${ERRORS}裁剪声明与执行不一致（${PRUNED_WITH_OUTPUT}），但 P1 无 override: 字段\n"
    fi
fi

if [ -n "$ERRORS" ]; then
    echo "GATE PRUNING: 裁剪条件不满足：" >&2
    printf '%b' "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0