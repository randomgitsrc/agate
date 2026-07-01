#!/usr/bin/env bats
# tests/regression/v060-design-gap.bats — 回归测试：DESIGN_GAP 配对
# 触发：cf6cd80 "feat(v0.6): DESIGN_GAP" 提交新机制
# ⚠️ 注意：当前是"待关闭的已知风险"，不是设计如此
#         如果这个测试通过 = 漏洞仍在

load ../helpers/load.bash

@test "R2.1 DESIGN_GAP + REVIEWED 配对可解除（基本功能）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "R2.2 DESIGN_GAP 未配对 → exit 1" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
}

# ⚠️ R2.3 是"已知风险"测试——通过 = 漏洞仍在，不要"修复"这个测试
@test "R2.3 ⚠️ 已知风险：DESIGN_GAP 在 P4 但 architect 忘记转抄 P7 → 静默放过" {
    # 这个测试是锁定当前行为：implementer 在 P4 标了 DESIGN_GAP，
    # 但 architect 忘记把它复制到 P7-consistency.md，
    # 结果 gate 看不到这个 GAP，直接 exit 0。
    #
    # 通过 = 漏洞仍在。
    # 修这个测试 = 实施 R2 待办（cross-check P4 vs P7 数量），
    #              必须先开新 issue/PR，不要"顺手"修。
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-implementation.md" <<'EOF'
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    # P7-consistency.md 没有这条 GAP
    cat > "$dir/P7-consistency.md" <<'EOF'
一致性检查完成。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}
