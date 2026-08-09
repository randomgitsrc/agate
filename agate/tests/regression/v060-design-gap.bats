#!/usr/bin/env bats
# tests/regression/v060-design-gap.bats — 回归测试：DESIGN_GAP 配对
# 触发：cf6cd80 "feat(v0.6): DESIGN_GAP" 提交新机制；R2.3 已修复：P4/P7 DESIGN_GAP 数量交叉核对
# T001 v2.0 流 B（BDD-20）改写：配对判定改读 P7 frontmatter 的
# design_gap_count / design_gap_reviewed_count（结构化计数），不再用正文数量相减的
# 0-vs-0 歧义判定（F14 消除）。[DESIGN_GAP]/[DESIGN_GAP_REVIEWED] 散文标记保留为人类痕迹。
# @test 数保持 4 不变。

load ../helpers/load.bash

@test "R2.1 BDD-20: frontmatter design_gap_count == design_gap_reviewed_count（已全部配对）→ exit 0" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
---
phase: P7
task_id: T001
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}

@test "R2.2 BDD-20: frontmatter design_gap_reviewed_count(0) < design_gap_count(1) → exit 1（未配对）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P7-consistency.md" <<'EOF'
---
phase: P7
task_id: T001
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 0
---
- [DESIGN_GAP: P2 未指定错误处理]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
}

@test "R2.3 P4 有 DESIGN_GAP 但 P7 frontmatter design_gap_count 为 0（未转抄）→ exit 1（交叉核对，回归 R2.3）" {
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
phase: P7
task_id: T001
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 0
design_gap_reviewed_count: 0
---
一致性检查完成。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P4"*"DESIGN_GAP"*"P7"* ]]
}

@test "R2.3b BDD-20: P4 DESIGN_GAP 数量 ≤ P7 frontmatter design_gap_count 且已 REVIEWED → exit 0" {
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
phase: P7
task_id: T001
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
---
- [DESIGN_GAP: P2 未指定错误处理]
- [DESIGN_GAP_REVIEWED: 已确认]
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"
    [ "$status" -eq 0 ]
}
