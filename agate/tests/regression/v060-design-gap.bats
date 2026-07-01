#!/usr/bin/env bats
# tests/regression/v060-design-gap.bats — 回归测试：DESIGN_GAP 配对
# 触发：cf6cd80 "feat(v0.6): DESIGN_GAP" 提交新机制
# R2.3 已修复：P4/P7 DESIGN_GAP 数量交叉核对

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

@test "R2.3 P4 有 DESIGN_GAP 但 P7 未转抄 → exit 1（交叉核对）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-implementation.md" <<'EOF'
---
agent: test
---
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    cat > "$dir/P7-consistency.md" <<'EOF'
---
agent: test
---
一致性检查完成。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4"*"DESIGN_GAP"*"P7"* ]]
}

@test "R2.3b P4/P7 DESIGN_GAP 数量一致 + REVIEWED → exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P4-implementation.md" <<'EOF'
---
agent: test
---
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    cat > "$dir/P7-consistency.md" <<'EOF'
---
agent: test
---
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}
